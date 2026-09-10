"""Transactional applier + versioned writer + audit log (WS-D D1b-1, #51).

Applies a :class:`~paperext.categorize.actions.Decision` to an **injected**
:class:`~paperext.ontology.Ontology` — never a config path, because #53 applies
decisions to ablated scratch copies.

Why the snapshot/rollback is not optional:

- there is no transaction API on :class:`~paperext.ontology.Ontology`, and a
  decision is several ops; a failure halfway leaves a half-edited tree;
- ``mark_ignore`` (``ontology.py:399-418``) is itself **composite and not atomic**
  — it can create the ``ignore`` root and then fail inside ``move``, leaving the
  orphan root behind;
- the mutators guard only *local* preconditions and ``check_invariants()`` is
  never called automatically, so a decision can be locally legal and globally
  wrong.

So: snapshot ``doc.model_dump()`` + the norm rows, apply the whole decision, run
``check_invariants()``, and on **any** :class:`OntologyError` restore the snapshot
byte-identically.

``decisions.jsonl`` is **append-only, one object per line**. A JSON array written
at end-of-run loses a crashed 300-item run entirely and makes run-to-run diffing
awkward.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from types import TracebackType
from typing import Any, Iterator, Union

from pydantic import BaseModel, Field

from paperext.analysis.rollup import Cut
from paperext.categorize.actions import (
    OPS,
    Action,
    ActionStatus,
    AppliedAction,
    Decision,
    Provenance,
)
from paperext.categorize.placement import (
    Placement,
    load_dimension_cut,
    resolve_placement,
)
from paperext.ontology.ontology import (
    DuplicateNodeError,
    Ontology,
    OntologyError,
    UnknownNodeError,
)
from paperext.ontology.schema import NormRow, OntologyDoc

#: ``v<N>`` snapshot directory names.
VERSION_RE = re.compile(r"^v(\d+)$")

DECISIONS_FILE = "decisions.jsonl"


# --------------------------------------------------------------------------- #
# Snapshots, hashing, diffing
# --------------------------------------------------------------------------- #


def _snapshot(onto: Ontology) -> "tuple[dict[str, Any], list[dict[str, Any]]]":
    return onto.doc.model_dump(), [row.model_dump() for row in onto.norm]


def _restore(
    onto: Ontology, snapshot: "tuple[dict[str, Any], list[dict[str, Any]]]"
) -> None:
    doc, norm = snapshot
    onto.doc = OntologyDoc.model_validate(doc)
    onto.norm = [NormRow.model_validate(row) for row in norm]
    onto._reindex()


def content_hash(onto: Ontology) -> str:
    """Stable sha256 over the tree + normalization DB.

    Pins the exact base a decision was taken against — ``base_version`` alone is
    not enough once a ``v<N>`` directory is rewritten.
    """
    doc, norm = _snapshot(onto)
    payload = json.dumps(
        {"doc": doc, "norm": norm}, sort_keys=True, ensure_ascii=False
    ).encode()
    return hashlib.sha256(payload).hexdigest()


class DecisionDiff(BaseModel):
    """What one decision changed, as it would show up in the two files."""

    created: list[str] = Field(default_factory=list)
    modified: list[str] = Field(default_factory=list)
    deleted: list[str] = Field(default_factory=list)
    roots_added: list[str] = Field(default_factory=list)
    roots_removed: list[str] = Field(default_factory=list)
    surfaces_added: "list[tuple[str, str]]" = Field(default_factory=list)
    surfaces_removed: "list[tuple[str, str]]" = Field(default_factory=list)

    def is_empty(self) -> bool:
        return not any(
            (
                self.created,
                self.modified,
                self.deleted,
                self.roots_added,
                self.roots_removed,
                self.surfaces_added,
                self.surfaces_removed,
            )
        )


def diff_snapshots(
    before: "tuple[dict[str, Any], list[dict[str, Any]]]",
    after: "tuple[dict[str, Any], list[dict[str, Any]]]",
) -> DecisionDiff:
    """Node/root/normalization diff between two :func:`_snapshot` results.

    Shared with ``scripts/mutate_ontology.py``'s ``print_changes`` so the audit
    record and the dev harness report the same thing.
    """
    before_doc, before_norm = before
    after_doc, after_norm = after
    before_nodes: "dict[str, Any]" = before_doc["nodes"]
    after_nodes: "dict[str, Any]" = after_doc["nodes"]

    before_pairs = Counter((r["surface"], r["canonical"]) for r in before_norm)
    after_pairs = Counter((r["surface"], r["canonical"]) for r in after_norm)

    return DecisionDiff(
        created=[nid for nid in after_nodes if nid not in before_nodes],
        modified=[
            nid
            for nid, node in after_nodes.items()
            if nid in before_nodes and node != before_nodes[nid]
        ],
        deleted=[nid for nid in before_nodes if nid not in after_nodes],
        roots_added=[r for r in after_doc["roots"] if r not in before_doc["roots"]],
        roots_removed=[r for r in before_doc["roots"] if r not in after_doc["roots"]],
        surfaces_added=sorted((after_pairs - before_pairs).elements()),
        surfaces_removed=sorted((before_pairs - after_pairs).elements()),
    )


# --------------------------------------------------------------------------- #
# Applying
# --------------------------------------------------------------------------- #


class ApplyResult(BaseModel):
    """Outcome of applying one decision."""

    ok: bool
    dry_run: bool = False
    error: str | None = None
    error_type: str | None = None
    failed_index: int | None = None
    actions: list[AppliedAction] = Field(default_factory=list)
    placement: Placement | None = None
    diff: DecisionDiff = Field(default_factory=DecisionDiff)


class DecisionRecord(BaseModel):
    """One line of ``decisions.jsonl``: what was asked, and what happened."""

    provenance: Provenance
    decision: Decision
    result: ApplyResult


def _check_refs(onto: Ontology, action: Action) -> None:
    """Uniform reference errors, driven by the :data:`OPS` table.

    The mutators already guard most of this; doing it here first means an unknown
    id always surfaces as :class:`UnknownNodeError` naming the *argument*, whatever
    op it came from.
    """
    spec = OPS[action.op]
    for name in spec.noderefs:
        value = getattr(action, name, None)
        if value is None:  # e.g. create_node(parent=None) -> a new root
            continue
        if value not in onto:
            raise UnknownNodeError(f"{action.op}.{name}: unknown node {value!r}")
    for name in spec.creates:
        value = getattr(action, name, None)
        if value is not None and value in onto:
            raise DuplicateNodeError(
                f"{action.op}.{name}: node {value!r} already exists (must be new)"
            )


def _invoke(onto: Ontology, action: Action) -> None:
    """Call the mutator for *action*, with arguments taken from :data:`OPS`."""
    spec = OPS[action.op]
    args = [getattr(action, name) for name in spec.positional]
    kwargs = {name: getattr(action, name) for name in spec.optional}
    method = getattr(onto, spec.method)
    try:
        method(*args, **kwargs)
    except KeyError as exc:  # read accessors raise bare KeyError on unknown ids
        raise UnknownNodeError(f"{action.op}: unknown node {exc.args[0]!r}") from exc


def apply_decision(
    onto: Ontology,
    decision: Decision,
    *,
    cut: Cut,
    dry_run: bool = False,
) -> ApplyResult:
    """Apply *decision* to *onto* atomically.

    On any :class:`~paperext.ontology.OntologyError` — from an action or from the
    post-decision ``check_invariants()`` — *onto* is restored byte-identically and
    ``ok`` is ``False``. With ``dry_run`` the tree is restored either way, so the
    result reports what *would* have happened.

    *cut* is required rather than defaulted: the recorded placement is only
    comparable across a run if every decision rolled up the same way. Use
    :func:`~paperext.categorize.placement.load_dimension_cut`.
    """
    before = _snapshot(onto)
    try:
        placement = resolve_placement(onto, decision, cut)
    except OntologyError:
        # the decision names a node that does not exist; the action loop below
        # rejects it properly. A decision that cannot be placed has no placement,
        # and one malformed decision must not abort a 300-item run.
        placement = None

    statuses: "list[AppliedAction]" = [
        AppliedAction(index=i, op=a.op, status=ActionStatus.SKIPPED)
        for i, a in enumerate(decision.actions)
    ]

    def rollback(index: int | None, exc: Exception) -> ApplyResult:
        _restore(onto, before)
        for entry in statuses:
            if entry.status is ActionStatus.APPLIED:
                entry.status = ActionStatus.ROLLED_BACK
        return ApplyResult(
            ok=False,
            dry_run=dry_run,
            error=str(exc),
            error_type=type(exc).__name__,
            failed_index=index,
            actions=statuses,
            placement=placement,
            diff=DecisionDiff(),
        )

    for i, action in enumerate(decision.actions):
        try:
            _check_refs(onto, action)
            _invoke(onto, action)
        except OntologyError as exc:
            statuses[i].status = ActionStatus.REJECTED
            statuses[i].error = str(exc)
            return rollback(i, exc)
        statuses[i].status = ActionStatus.APPLIED

    try:
        onto.check_invariants()
    except OntologyError as exc:
        return rollback(None, exc)

    diff = diff_snapshots(before, _snapshot(onto))

    if dry_run:
        _restore(onto, before)
        for entry in statuses:
            entry.status = ActionStatus.DRY_RUN

    return ApplyResult(
        ok=True,
        dry_run=dry_run,
        actions=statuses,
        placement=placement,
        diff=diff,
    )


def suggest_node_id(onto: Ontology, name: str) -> str:
    """A ``v0``-conforming id for a new node named *name*.

    Same slug + ``__2`` uniquifier the ``v0`` migration uses, so agent-created ids
    are indistinguishable from migrated ones.
    """
    from paperext.ontology.migrate import make_node_id

    return make_node_id(name, onto.nodes)


# --------------------------------------------------------------------------- #
# Audit log
# --------------------------------------------------------------------------- #


class DecisionLog:
    """Append-only ``decisions.jsonl`` writer.

    One JSON object per line, flushed per record, so a crashed run keeps every
    decision it had already taken.
    """

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("a", encoding="utf-8")

    def write(self, record: DecisionRecord) -> None:
        self._fh.write(
            json.dumps(record.model_dump(mode="json"), ensure_ascii=False) + "\n"
        )
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()

    def __enter__(self) -> "DecisionLog":
        return self

    def __exit__(
        self,
        exc_type: "type[BaseException] | None",
        exc: "BaseException | None",
        tb: "TracebackType | None",
    ) -> None:
        self.close()


def read_decisions(path: Union[str, Path]) -> Iterator[DecisionRecord]:
    """Stream ``decisions.jsonl`` back in, one record per line."""
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield DecisionRecord.model_validate_json(line)


# --------------------------------------------------------------------------- #
# Versioned snapshots
# --------------------------------------------------------------------------- #


def ontology_root() -> Path:
    """``<data>/ontology`` from the config."""
    from paperext.config import CFG

    cfg: Any = CFG  # the config proxy resolves attributes dynamically
    return Path(cfg.dir.data) / "ontology"


def versions(dimension: str, *, root: Union[str, Path, None] = None) -> "list[str]":
    """Existing ``v<N>`` snapshot names for *dimension*, in numeric order."""
    base = Path(root) if root is not None else ontology_root()
    dim_dir = base / dimension
    if not dim_dir.is_dir():
        return []
    found = [
        (int(m.group(1)), m.group(0))
        for p in dim_dir.iterdir()
        if (m := VERSION_RE.match(p.name)) and p.is_dir()
    ]
    return [name for _, name in sorted(found)]


def next_version(dimension: str, *, root: Union[str, Path, None] = None) -> str:
    """The next unused ``v<N>`` name for *dimension*."""
    existing = versions(dimension, root=root)
    highest = max((int(VERSION_RE.match(v).group(1)) for v in existing), default=-1)  # type: ignore[union-attr]
    return f"v{highest + 1}"


def write_snapshot(
    onto: Ontology,
    dimension: str,
    version: str | None = None,
    *,
    root: Union[str, Path, None] = None,
) -> Path:
    """Write *onto* as ``<root>/<dimension>/<version>/``.

    :meth:`Ontology.save` does not bump ``meta.version`` and silently overwrites,
    so this sets the version and **refuses to clobber an existing directory** —
    the committed ``v0`` must not be destroyable by a stray ``--out v0``.
    """
    base = Path(root) if root is not None else ontology_root()
    version = version or next_version(dimension, root=base)
    if not VERSION_RE.match(version):
        raise ValueError(f"version must look like 'v<N>', got {version!r}")
    out_dir = base / dimension / version
    if out_dir.exists():
        raise FileExistsError(f"{out_dir} already exists; refusing to overwrite")
    onto.doc.meta.version = version
    onto.doc.meta.dimension = dimension
    onto.save(out_dir)
    return out_dir


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _load_decisions(path: Path) -> "list[Decision]":
    """Read a decisions file: either raw :class:`Decision` s or full records."""
    decisions: "list[Decision]" = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if "decision" in payload:  # a DecisionRecord (replay)
            payload = payload["decision"]
        decisions.append(Decision.model_validate(payload))
    return decisions


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply a decisions.jsonl to an ontology snapshot.",
    )
    parser.add_argument("--dim", required=True, help="e.g. models")
    parser.add_argument("--base", default="v0", help="base snapshot (default: v0)")
    parser.add_argument("--in", dest="infile", required=True, help="decisions.jsonl")
    parser.add_argument("--out", default=None, help="new snapshot (default: next v<N>)")
    parser.add_argument(
        "--root", default=None, help="ontology root (default: <data>/ontology)"
    )
    parser.add_argument("--run-id", default="apply", help="run id in the audit records")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would change; write nothing",
    )
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root else ontology_root()
    base_dir = root / args.dim / args.base
    onto = Ontology.load(base_dir)
    cut = load_dimension_cut(args.dim)
    base_hash = content_hash(onto)

    decisions = _load_decisions(Path(args.infile))
    out_dir = (
        None
        if args.dry_run
        else root / args.dim / (args.out or next_version(args.dim, root=root))
    )

    records: "list[DecisionRecord]" = []
    failures = 0
    for seq, decision in enumerate(decisions):
        result = apply_decision(onto, decision, cut=cut, dry_run=args.dry_run)
        failures += not result.ok
        records.append(
            DecisionRecord(
                provenance=Provenance(
                    run_id=args.run_id,
                    seq=seq,
                    dimension=args.dim,
                    base_version=args.base,
                    base_content_hash=base_hash,
                ),
                decision=decision,
                result=result,
            )
        )
        status = "ok " if result.ok else "FAIL"
        detail = "" if result.ok else f" ({result.error_type}: {result.error})"
        print(
            f"[{seq:>4}] {status} {decision.surface!r} {decision.outcome.value}{detail}"
        )

    print(
        f"# {len(decisions) - failures}/{len(decisions)} applied, "
        f"{failures} rejected, {len(onto.nodes)} nodes, {len(onto.norm)} surfaces"
    )

    if args.dry_run:
        return 1 if failures else 0

    assert out_dir is not None
    write_snapshot(onto, args.dim, out_dir.name, root=root)
    with DecisionLog(out_dir / DECISIONS_FILE) as log:
        for record in records:
            log.write(record)
    print(f"# wrote {out_dir}")
    return 1 if failures else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
