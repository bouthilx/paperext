"""The agent loop: name in, :class:`Decision` out (WS-D D1b-2, #52).

Everything model-facing lives here, and nothing else in
:mod:`paperext.categorize` imports ``instructor`` -- so retrieval, the payload and
the applier stay testable with no network at all.

Three things this file is deliberate about:

**The categorization model is pinned separately from the extraction model.**
``[categorize] platform`` / ``model``, never ``CFG.platform.select``. If the agent
read the extraction selection, swapping the extraction backend would silently
change what the #53 gate number was measured on, and the number would stop being
attributable to a model. ``Backend.make_client`` closes over ``CFG.<platform>.model``
(the extraction model), so :func:`make_client` overrides that key for the duration
of the build; the client that comes back is permanently pinned to the
categorization model, and the global config is untouched afterwards.

**Concurrency is chunked, not free-running.** In an accumulating run each decision
mutates the tree the next one is asked against, which is the point -- a node created
for ``ResNet-50`` should be there when ``ResNet-101`` comes up. So a chunk of
``concurrency`` items is decided in parallel against the tree as it stands, then
applied **in item order**. The result depends on the chunk size but not on which
request finished first, which is what makes a run reproducible. ``concurrency=1``
is exactly sequential; ``--no-apply`` (the #53 leave-one-out mode) has no ordering
constraint at all.

**A malformed response is repaired, not dropped.** ``instructor`` already retries
schema violations inside one call; what it cannot fix is an action the *applier*
rejects (a node id that does not exist, an edit that breaks an invariant). Those
come back as one more turn quoting the error, up to :data:`DEFAULT_MAX_REPAIRS`,
and every attempt is recorded.

The rate-limit path deliberately does not copy ``query.py:83``, where the
``asyncio.sleep(60)`` is missing its ``await`` and so does nothing at all.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Sequence

import instructor

from paperext.categorize.actions import Decision, Provenance
from paperext.categorize.apply import (
    DECISIONS_FILE,
    ApplyResult,
    DecisionLog,
    DecisionRecord,
    apply_decision,
    content_hash,
    next_version,
    ontology_root,
    write_snapshot,
)
from paperext.categorize.candidates import (
    DEFAULT_LIMIT,
    DEFAULT_SKELETON_DEPTH,
    normalized_keys,
)
from paperext.categorize.items import (
    DEFAULT_MAX_MENTIONS,
    Item,
    build_items,
    read_items,
)
from paperext.categorize.placement import load_dimension_cut
from paperext.categorize.prompt import (
    Context,
    build_context,
    build_messages,
    build_payload,
    payload_hash,
)
from paperext.log import logger
from paperext.ontology.ontology import Ontology

PROG = "categorize"

#: How many items are decided in parallel against one tree state.
DEFAULT_CONCURRENCY = 4

#: Extra turns granted to fix a decision the applier rejected.
DEFAULT_MAX_REPAIRS = 2

#: Seconds to back off on a provider rate-limit error.
RATE_LIMIT_BACKOFF = 60.0

_REPAIR_TEMPLATE = """\
Your previous decision could not be applied. The applier rejected action \
{index} (`{op}`):

    {error}

Nothing was changed. Re-read the CANDIDATES and TAXONOMY above and emit a \
corrected decision. Every node id you reference must appear there, or be created \
by an earlier action in the same decision. If you cannot place this name safely, \
abstain.\
"""


def categorize_settings() -> "tuple[str, str]":
    """``(platform, model)`` for the *categorization* agent, from ``[categorize]``."""
    from paperext.config import CFG

    cfg: Any = CFG  # the config proxy resolves attributes dynamically
    return str(cfg.categorize.platform), str(cfg.categorize.model)


def make_client(platform: str, model: str) -> instructor.AsyncInstructor:
    """An async instructor client pinned to *model* on *platform*.

    See the module docstring: the override is scoped to the ``make_client`` call,
    and the returned client keeps *model* because the backend closes over it.
    """
    from paperext.backends import get_backend
    from paperext.config import Config

    with Config.push() as cfg:
        setattr(getattr(cfg, platform), "model", model)
        return get_backend(platform).make_client()


async def decide(
    client: instructor.AsyncInstructor,
    messages: "list[dict[str, str]]",
    *,
    rate_limit_errors: "tuple[type[BaseException], ...]" = (),
) -> "tuple[Decision, dict[str, Any]]":
    """One model call: messages in, validated :class:`Decision` out.

    ``instructor`` handles schema-violation retries internally; this adds only the
    provider rate-limit back-off, which is genuinely ``await``ed.
    """
    retries = 1
    # The provider message TypedDicts are structurally what `build_messages`
    # produces; the annotation is a union of per-role TypedDicts a plain
    # dict[str, str] cannot satisfy nominally.
    payload: Any = messages
    while True:
        try:
            decision, usage = await client.chat.completions.create_with_completion(
                response_model=Decision,
                messages=payload,
                max_retries=2,
            )
            return decision, dict(usage or {})
        except rate_limit_errors:
            if not retries:
                raise
            retries -= 1
            logger.warning("rate limited; backing off %ss", RATE_LIMIT_BACKOFF)
            await asyncio.sleep(RATE_LIMIT_BACKOFF)


def _accumulate(total: "dict[str, Any]", usage: "dict[str, Any]") -> None:
    for key, value in usage.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            total[key] = total.get(key, 0) + value


def _repair_turn(decision: Decision, result: ApplyResult) -> "list[dict[str, str]]":
    index = result.failed_index
    op = (
        decision.actions[index].op
        if index is not None and 0 <= index < len(decision.actions)
        else "?"
    )
    return [
        {"role": "assistant", "content": decision.model_dump_json()},
        {
            "role": "user",
            "content": _REPAIR_TEMPLATE.format(
                index=index, op=op, error=result.error or "unknown error"
            ),
        },
    ]


async def decide_item(
    client: instructor.AsyncInstructor,
    onto: Ontology,
    ctx: Context,
    item: Item,
    *,
    cut: Any,
    provenance: Provenance,
    limit: int = DEFAULT_LIMIT,
    keys: "dict[str, list[str]] | None" = None,
    apply: bool = True,
    max_repairs: int = DEFAULT_MAX_REPAIRS,
    rate_limit_errors: "tuple[type[BaseException], ...]" = (),
) -> DecisionRecord:
    """Decide *item*, repairing up to *max_repairs* times if the applier rejects it.

    With ``apply=False`` every attempt is a dry run, so a #53 leave-one-out pass
    gets the same rejection feedback without mutating the scratch tree. The
    returned record carries the **last** attempt -- what the run actually did --
    with the whole call's token usage in ``provenance.params['usage']``.
    """
    payload = build_payload(onto, item, cut=cut, limit=limit, keys=keys)
    provenance = provenance.model_copy(
        update={"payload_hash": payload_hash(ctx, payload)}
    )
    messages = build_messages(ctx, payload)
    usage_total: "dict[str, Any]" = {}

    for attempt in range(max_repairs + 1):
        decision, usage = await decide(
            client, messages, rate_limit_errors=rate_limit_errors
        )
        _accumulate(usage_total, usage)
        result = apply_decision(onto, decision, cut=cut, dry_run=not apply)

        if result.ok or attempt == max_repairs:
            params = dict(provenance.params)
            if usage_total:
                params["usage"] = usage_total
            params["repairs"] = attempt
            return DecisionRecord(
                decision=decision,
                result=result,
                provenance=provenance.model_copy(update={"params": params}),
            )

        logger.info(
            "repair %d/%d for %r: %s",
            attempt + 1,
            max_repairs,
            item.name,
            result.error,
        )
        messages = messages + _repair_turn(decision, result)

    raise AssertionError("unreachable")  # pragma: no cover


async def run(
    client: instructor.AsyncInstructor,
    onto: Ontology,
    items: "Sequence[Item]",
    *,
    dimension: str,
    cut: Any,
    run_id: "str | None" = None,
    model: "str | None" = None,
    apply: bool = True,
    concurrency: int = DEFAULT_CONCURRENCY,
    limit: int = DEFAULT_LIMIT,
    skeleton_depth: int = DEFAULT_SKELETON_DEPTH,
    max_repairs: int = DEFAULT_MAX_REPAIRS,
    rate_limit_errors: "tuple[type[BaseException], ...]" = (),
    log: "DecisionLog | None" = None,
) -> "list[DecisionRecord]":
    """Decide every item in *items*, mutating *onto* in place when *apply*.

    Chunked concurrency: ``concurrency`` items are decided against one tree state,
    then applied in item order. The shared prompt prefix is identical within a
    chunk -- and across chunks until a decision changes the tree -- which is what
    makes provider prompt caching pay here.
    """
    run_id = run_id or uuid.uuid4().hex[:12]
    records: "list[DecisionRecord]" = []
    semaphore = asyncio.Semaphore(max(1, concurrency))
    chunk_size = max(1, concurrency) if apply else len(items) or 1

    for start in range(0, len(items), chunk_size):
        chunk = items[start : start + chunk_size]
        ctx = build_context(
            onto,
            dimension,
            skeleton_depth=skeleton_depth,
            base_content_hash=content_hash(onto),
        )
        keys = normalized_keys(onto)
        base = Provenance(
            run_id=run_id,
            seq=0,
            dimension=dimension,
            base_version=ctx.base_version,
            base_content_hash=ctx.base_content_hash,
            model=model,
            params={"candidate_limit": limit, "skeleton_depth": skeleton_depth},
        )

        async def one(offset: int, item: Item) -> DecisionRecord:
            async with semaphore:
                # Decisions inside a chunk are taken against the chunk's tree and
                # applied afterwards, so `apply` is off for the in-flight call and
                # the chunk is applied in order below.
                return await decide_item(
                    client,
                    onto,
                    ctx,
                    item,
                    cut=cut,
                    provenance=base.model_copy(
                        update={"seq": start + offset, "ablated": not apply}
                    ),
                    limit=limit,
                    keys=keys,
                    apply=False,
                    max_repairs=max_repairs,
                    rate_limit_errors=rate_limit_errors,
                )

        chunk_records = await asyncio.gather(
            *(one(i, item) for i, item in enumerate(chunk))
        )

        for record in chunk_records:
            if apply:
                result = apply_decision(onto, record.decision, cut=cut)
                record = record.model_copy(update={"result": result})
            records.append(record)
            if log is not None:
                log.write(record)

    return records


def _summarize(records: "Sequence[DecisionRecord]") -> str:
    counts: "dict[str, int]" = {}
    for record in records:
        key = record.decision.outcome.value
        counts[key] = counts.get(key, 0) + 1
    applied = sum(1 for r in records if r.result.ok)
    parts = [f"{name}={counts[name]}" for name in sorted(counts)]
    return f"{len(records)} decisions ({applied} applied) " + " ".join(parts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Run the categorization agent over one dimension's names.",
    )
    parser.add_argument("--dim", default="models", help="ontology dimension")
    parser.add_argument("--base", default="v0", help="version dir to decide against")
    parser.add_argument("--root", default=None, help="ontology root (default: config)")
    parser.add_argument(
        "--items", default=None, metavar="JSONL", help="items file (default: rebuild)"
    )
    parser.add_argument("--limit-items", type=int, default=None, metavar="N")
    parser.add_argument(
        "--surfaces",
        nargs="*",
        default=None,
        help="decide only these names (normalized surfaces)",
    )
    parser.add_argument("--unmapped-only", action="store_true")
    parser.add_argument("--platform", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--candidates", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--skeleton-depth", type=int, default=DEFAULT_SKELETON_DEPTH)
    parser.add_argument("--max-mentions", type=int, default=DEFAULT_MAX_MENTIONS)
    parser.add_argument("--max-repairs", type=int, default=DEFAULT_MAX_REPAIRS)
    parser.add_argument("--run-id", default=None)
    parser.add_argument(
        "--decisions",
        default=None,
        metavar="JSONL",
        help=f"default: <out>/{DECISIONS_FILE}",
    )
    parser.add_argument(
        "--out", default=None, metavar="VERSION", help="snapshot to write"
    )
    parser.add_argument(
        "--no-apply",
        action="store_true",
        help="decide without mutating the tree (dry run per decision)",
    )
    parser.add_argument(
        "--dump-payload",
        action="store_true",
        help="print the payload for each item and exit without calling a model",
    )
    return parser


def _select(
    items: "Sequence[Item]", onto: Ontology, args: argparse.Namespace
) -> "list[Item]":
    selected = list(items)
    if args.surfaces:
        wanted = set(args.surfaces)
        selected = [i for i in selected if i.surface in wanted]
    if args.unmapped_only:
        selected = [i for i in selected if onto.resolve(i.surface) is None]
    if args.limit_items is not None:
        selected = selected[: args.limit_items]
    return selected


def main(argv: "Sequence[str] | None" = None) -> int:
    args = build_parser().parse_args(argv)

    root = Path(args.root) if args.root else ontology_root()
    onto = Ontology.load(root / args.dim / args.base)
    cut = load_dimension_cut(args.dim)

    items = (
        read_items(args.items)
        if args.items
        else build_items(args.dim, max_mentions=args.max_mentions)
    )
    selected = _select(items, onto, args)
    if not selected:
        print("no items selected", file=sys.stderr)
        return 1

    if args.dump_payload:
        ctx = build_context(onto, args.dim, skeleton_depth=args.skeleton_depth)
        keys = normalized_keys(onto)
        for item in selected:
            payload = build_payload(
                onto, item, cut=cut, limit=args.candidates, keys=keys
            )
            print(
                json.dumps(build_messages(ctx, payload), indent=2, ensure_ascii=False)
            )
        return 0

    platform, model = categorize_settings()
    platform = args.platform or platform
    model = args.model or model
    client = make_client(platform, model)

    from paperext.backends import get_backend

    out_dir = root / args.dim / (args.out or next_version(args.dim, root=root))
    decisions_path = (
        Path(args.decisions) if args.decisions else out_dir / DECISIONS_FILE
    )

    with DecisionLog(decisions_path) as log:
        records = asyncio.run(
            run(
                client,
                onto,
                selected,
                dimension=args.dim,
                cut=cut,
                run_id=args.run_id,
                model=model,
                apply=not args.no_apply,
                concurrency=args.concurrency,
                limit=args.candidates,
                skeleton_depth=args.skeleton_depth,
                max_repairs=args.max_repairs,
                rate_limit_errors=get_backend(platform).rate_limit_errors,
                log=log,
            )
        )

    print(f"# {_summarize(records)}")
    print(f"# decisions -> {decisions_path}")
    if not args.no_apply:
        onto.check_invariants()
        print(
            f"# snapshot -> {write_snapshot(onto, args.dim, out_dir.name, root=root)}"
        )
    return 0 if all(r.result.ok or not r.decision.actions for r in records) else 1


if __name__ == "__main__":
    sys.exit(main())
