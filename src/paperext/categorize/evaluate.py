"""The held-out eval harness and the decision gate (WS-D D1b-3, #53).

Answers one question: **does the agent earn the right to run across D1c-D1e?**

The protocol is **leave-one-out and non-accumulating**. Each item is decided
against its own single-item-ablated copy of the tree, so the items are i.i.d. and
the confidence intervals are honest. Ablating all 300 at once would gut the
sibling context every placement depends on and correlate the errors, which would
make the interval a decoration. The price is that the shared prompt prefix
changes per item, so a gate run does not benefit from prompt caching the way an
accumulating D1c run will.

The gate reads six clauses (:func:`evaluate_gate`), and the primary one is a
blind pairwise win rate whose ceiling is 0.5 **analytically** -- see
:mod:`paperext.categorize.adjudicate`. Everything reference-based is reported
next to a majority-class baseline and a **Levenshtein nearest-neighbour** placer,
because Levenshtein-plus-an-LLM is precisely the pipeline that produced the
reference (``ontology_mapping/build_models_tree.py``): a pinned frontier model
that cannot beat it by a wide margin is not earning its cost band.

Two things measured here that the issue could not know in advance, both reported
per stratum rather than folded away:

- **Not every held-out name has corpus evidence.** The pool was drawn from the
  *tree*, so 28 of 200 dev and 45 of 300 gate names never appear in the 2024
  query records. For those the agent decides from the name alone, while the
  human who built the reference had paper excerpts. W is reported with and
  without them.
- **Ablation leaves residue.** ``v0`` deliberately keeps duplicate concepts, so a
  held-out name can survive inside a *different* node's name (``resnet-20`` in
  ``residual networks (resnet-20)``). 22 of 200 dev and 24 of 300 gate items are
  affected. Scrubbing them would destroy the legitimate neighbourhood cases
  (``gan`` inside ``dp-gan``), so they are reported, not removed.

Nothing here needs the network: :func:`replay_decider` runs the whole harness
against a recorded ``decisions.jsonl``, which is how the acceptance tests get an
end-to-end report with zero API calls.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable, Sequence, Union

from pydantic import BaseModel, Field
from rapidfuzz import fuzz

from paperext.analysis.rollup import Cut, str_normalize
from paperext.categorize import metrics, probes
from paperext.categorize.ablate import ablate, residual_names
from paperext.categorize.actions import Decision, Outcome, Provenance
from paperext.categorize.adjudicate import (
    Pair,
    Verdict,
    VerdictCache,
    adjudicate,
    make_pair,
    render_placement,
    score_pair,
    swap,
)
from paperext.categorize.apply import (
    DecisionLog,
    DecisionRecord,
    apply_decision,
    content_hash,
    read_decisions,
)
from paperext.categorize.candidates import DEFAULT_LIMIT, normalized_keys
from paperext.categorize.items import Item, build_items, read_items
from paperext.categorize.metrics import HierScore
from paperext.categorize.placement import Placement, load_dimension_cut, to_placement
from paperext.categorize.prompt import (
    DEFAULT_SKELETON_DEPTH,
    Context,
    build_context,
    build_payload,
    render_evidence,
)
from paperext.categorize.sampling import SplitItem, Splits
from paperext.ontology.ontology import Ontology

logger = logging.getLogger(__name__)

PROG = "categorize-eval"

#: Files a run writes under ``--out``.
DECISIONS_FILE = "decisions.jsonl"
SCORES_FILE = "scores.jsonl"
REPORT_JSON = "report.json"
REPORT_MD = "report.md"
VERDICTS_FILE = "verdicts.jsonl"

DEFAULT_COVERAGE = 0.85


# --------------------------------------------------------------------------- #
# Eval items
# --------------------------------------------------------------------------- #


class EvalItem(BaseModel):
    """A held-out name, its reference placement, and the evidence the agent gets."""

    split_item: SplitItem
    item: Item
    reference: Placement
    has_evidence: bool
    residue: "list[str]" = Field(
        default_factory=list,
        description="Surviving node names that still spell out the held-out name",
    )

    @property
    def surface(self) -> str:
        return self.split_item.surface


def bare_item(split_item: SplitItem, dimension: str) -> Item:
    """An :class:`Item` for a name the 2024 corpus never mentions.

    Roughly one held-out name in seven: the pool comes from the tree, not the
    corpus. Rather than dropping them -- which would quietly restrict the eval to
    the names the current corpus happens to use -- they are asked with no
    evidence, and scored as their own stratum.
    """
    return Item(
        dimension=dimension,
        surface=split_item.surface,
        name=split_item.name,
        aliases=[],
        spellings=[split_item.name],
        n_mentions=0,
        n_papers=0,
        mentions=[],
    )


def build_eval_items(
    onto: Ontology,
    split_items: "Sequence[SplitItem]",
    corpus_items: "Sequence[Item]",
    *,
    dimension: str,
    cut: Cut,
    with_residue: bool = True,
) -> "list[EvalItem]":
    """Join split items to their corpus evidence and their reference placement."""
    by_surface: "dict[str, Item]" = {item.surface: item for item in corpus_items}
    built: "list[EvalItem]" = []
    for split_item in split_items:
        item = by_surface.get(split_item.surface)
        residue: "list[str]" = []
        if with_residue:
            scratch = ablate(onto, split_item.surface)
            residue = residual_names(scratch, split_item.surface, split_item.name)
        built.append(
            EvalItem(
                split_item=split_item,
                item=item or bare_item(split_item, dimension),
                reference=to_placement(onto, split_item.node_id, cut),
                has_evidence=item is not None,
                residue=residue,
            )
        )
    return built


# --------------------------------------------------------------------------- #
# Deciders
# --------------------------------------------------------------------------- #

#: What the harness needs from "the agent": a decision for one item, taken against
#: the tree it is handed. Injectable so the acceptance tests replay a recording.
Decider = Callable[[Ontology, Context, Item, Provenance], "Awaitable[DecisionRecord]"]


def agent_decider(
    client: Any,
    *,
    cut: Cut,
    limit: int = DEFAULT_LIMIT,
    max_repairs: int = 2,
    rate_limit_errors: "tuple[type[BaseException], ...]" = (),
) -> Decider:
    """The live decider: one :func:`~paperext.categorize.agent.decide_item` call.

    ``apply=False`` throughout -- a leave-one-out pass must not mutate the scratch
    tree, or item ``n+1`` would be decided against item ``n``'s edits.
    """
    from paperext.categorize.agent import decide_item

    async def decide(
        onto: Ontology, ctx: Context, item: Item, provenance: Provenance
    ) -> DecisionRecord:
        return await decide_item(
            client,
            onto,
            ctx,
            item,
            cut=cut,
            provenance=provenance,
            limit=limit,
            keys=normalized_keys(onto),
            apply=False,
            max_repairs=max_repairs,
            rate_limit_errors=rate_limit_errors,
        )

    return decide


def replay_decider(
    source: "Union[str, Path, Iterable[DecisionRecord]]", *, cut: Cut
) -> Decider:
    """A stub decider replaying recorded decisions, keyed by surface.

    The recorded :class:`Decision` is re-applied (dry run) against the tree the
    harness hands over, so placements, apply failures and invariants are all
    recomputed rather than trusted from the recording. That is what lets the
    acceptance test exercise the entire harness -- scoring, probes, adjudication,
    report -- with no network at all.
    """
    if isinstance(source, (str, Path)):
        records = list(read_decisions(source))
    else:
        records = list(source)
    by_surface: "dict[str, Decision]" = {
        str_normalize(record.decision.surface): record.decision for record in records
    }

    async def decide(
        onto: Ontology, ctx: Context, item: Item, provenance: Provenance
    ) -> DecisionRecord:
        decision = by_surface.get(str_normalize(item.surface))
        if decision is None:
            decision = Decision(
                surface=item.surface,
                outcome=Outcome.FAILED,
                confidence=0.0,
                review_notes=["no recorded decision for this surface"],
            )
        payload = build_payload(onto, item, cut=cut)
        from paperext.categorize.prompt import payload_hash

        result = apply_decision(onto, decision, cut=cut, dry_run=True)
        return DecisionRecord(
            decision=decision,
            result=result,
            provenance=provenance.model_copy(
                update={"payload_hash": payload_hash(ctx, payload)}
            ),
        )

    return decide


# --------------------------------------------------------------------------- #
# Leave-one-out pass
# --------------------------------------------------------------------------- #


async def leave_one_out(
    onto: Ontology,
    eval_items: "Sequence[EvalItem]",
    decider: Decider,
    *,
    dimension: str,
    cut: Cut,
    run_id: "str | None" = None,
    model: "str | None" = None,
    concurrency: int = 4,
    skeleton_depth: int = DEFAULT_SKELETON_DEPTH,
    ablated: bool = True,
    log: "DecisionLog | None" = None,
) -> "list[DecisionRecord]":
    """Decide every item against its own ablated copy. *onto* is never mutated.

    With ``ablated=False`` the items are decided against the tree as it stands --
    that is the no-op control, where the correct answer is to change nothing.
    """
    cases = [
        ((ablate(onto, item.surface) if ablated else onto), item.item)
        for item in eval_items
    ]
    return await decide_all(
        cases,
        decider,
        dimension=dimension,
        run_id=run_id,
        model=model,
        concurrency=concurrency,
        skeleton_depth=skeleton_depth,
        ablated=ablated,
        log=log,
    )


async def decide_all(
    cases: "Sequence[tuple[Ontology, Item]]",
    decider: Decider,
    *,
    dimension: str,
    run_id: "str | None" = None,
    model: "str | None" = None,
    concurrency: int = 4,
    skeleton_depth: int = DEFAULT_SKELETON_DEPTH,
    ablated: bool = True,
    log: "DecisionLog | None" = None,
) -> "list[DecisionRecord]":
    """Decide a list of ``(tree, item)`` pairs -- the shared engine of every probe.

    Each pair carries its own tree, which is what lets leave-one-out, the no-op
    control (un-ablated), the policy cases and the injected homonyms all run
    through one code path instead of four near-copies.
    """
    run_id = run_id or uuid.uuid4().hex[:12]
    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def one(seq: int, scratch: Ontology, item: Item) -> DecisionRecord:
        ctx = build_context(
            scratch,
            dimension,
            skeleton_depth=skeleton_depth,
            base_content_hash=content_hash(scratch),
        )
        provenance = Provenance(
            run_id=run_id,
            seq=seq,
            dimension=dimension,
            base_version=ctx.base_version,
            base_content_hash=ctx.base_content_hash,
            model=model,
            ablated=ablated,
            params={"skeleton_depth": skeleton_depth, "eval": True},
        )
        async with semaphore:
            return await decider(scratch, ctx, item, provenance)

    records = list(
        await asyncio.gather(
            *(one(seq, scratch, item) for seq, (scratch, item) in enumerate(cases))
        )
    )
    if log is not None:
        for record in records:
            log.write(record)
    return records


# --------------------------------------------------------------------------- #
# Per-item scoring
# --------------------------------------------------------------------------- #


class ItemScore(BaseModel):
    """Everything the report needs about one held-out name."""

    surface: str
    name: str
    node_id: str
    anchoring: str
    has_evidence: bool
    has_residue: bool
    outcome: str
    confidence: float
    applied: bool
    error: "str | None" = None
    reference_category: "str | None" = None
    agent_category: "str | None" = None
    reference_path: str = ""
    agent_path: str = ""
    hier: "HierScore | None" = None
    win: "float | None" = None


def score_items(
    eval_items: "Sequence[EvalItem]", records: "Sequence[DecisionRecord]"
) -> "list[ItemScore]":
    """Pair each item with its decision. Placements come from the applier.

    :func:`~paperext.categorize.apply.apply_decision` resolves the placement
    against the **pre-decision** tree, which is the only moment at which a bare
    ``create_node(parent=X)`` is resolvable at all.
    """
    scores: "list[ItemScore]" = []
    for eval_item, record in zip(eval_items, records):
        placement = record.result.placement
        hier = None
        if placement is not None:
            hier = metrics.hierarchical_prf(
                metrics.lineage(placement), metrics.lineage(eval_item.reference)
            )
        scores.append(
            ItemScore(
                surface=eval_item.surface,
                name=eval_item.split_item.name,
                node_id=eval_item.split_item.node_id,
                anchoring=eval_item.split_item.anchoring,
                has_evidence=eval_item.has_evidence,
                has_residue=bool(eval_item.residue),
                outcome=record.decision.outcome.value,
                confidence=record.decision.confidence,
                applied=record.result.ok,
                error=record.result.error,
                reference_category=eval_item.reference.cut_category,
                agent_category=placement.cut_category if placement else None,
                reference_path=render_placement(
                    eval_item.reference, leaf=eval_item.split_item.name
                ),
                agent_path=(
                    render_placement(placement, leaf=eval_item.split_item.name)
                    if placement
                    else ""
                ),
                hier=hier,
            )
        )
    return scores


def decided(scores: "Sequence[ItemScore]") -> "list[ItemScore]":
    """Items the agent actually placed -- abstentions and failures excluded."""
    return [score for score in scores if score.agent_path]


# --------------------------------------------------------------------------- #
# Baselines
# --------------------------------------------------------------------------- #


def majority_baseline(reference: "Sequence[str | None]") -> "list[str | None]":
    """Always answer the commonest reference category (~45% ``Other`` at the cut)."""
    counts: "dict[str, int]" = {}
    for category in reference:
        counts[metrics.label(category)] = counts.get(metrics.label(category), 0) + 1
    if not counts:
        return []
    top = max(sorted(counts), key=lambda key: counts[key])
    return [top] * len(reference)


def levenshtein_baseline(
    onto: Ontology, eval_items: "Sequence[EvalItem]", *, cut: Cut
) -> "list[str | None]":
    """Nearest node name by edit distance, scored at the cut.

    This is not an arbitrary baseline: it is the retrieval half of the pipeline
    that *generated* the reference. It is also nearly free, so it belongs beside
    every agreement number the report prints.
    """
    predictions: "list[str | None]" = []
    for eval_item in eval_items:
        scratch = ablate(onto, eval_item.surface)
        query = eval_item.surface
        best_id, best_score = None, -1.0
        for node_id in scratch.nodes:
            score = fuzz.ratio(query, str_normalize(scratch.name(node_id)))
            if score > best_score:
                best_id, best_score = node_id, score
        if best_id is None:
            predictions.append(None)
            continue
        # placed *under* the nearest node, mirroring what the agent is asked to do
        from paperext.categorize.placement import placement_for_new

        predictions.append(
            placement_for_new(
                scratch, best_id, eval_item.split_item.name, cut
            ).cut_category
        )
    return predictions


# --------------------------------------------------------------------------- #
# Sequential replay diagnostic
# --------------------------------------------------------------------------- #


def sequential_replay(
    onto: Ontology,
    records: "Sequence[DecisionRecord]",
    *,
    cut: Cut,
    surfaces: "Sequence[str]" = (),
) -> "dict[str, Any]":
    """Apply the leave-one-out decisions to **one** accumulating tree, in order.

    Reported, never gated. It is the only number that says anything about what a
    real D1c run does to a tree: whether decisions collide, whether the invariants
    survive 300 edits, how far the node count drifts, how many duplicate concepts
    appear.

    One honest limitation: these decisions were taken against per-item ablated
    trees, so this measures the **applier** under accumulation, not the agent
    adapting to its own earlier edits. A true accumulating pass is the D1c dry
    run, not something this harness can fake.
    """
    from paperext.categorize.ablate import copy_ontology

    scratch = copy_ontology(onto)
    for surface in surfaces:
        # every held-out name is hidden *first*, so the pass re-maps them all
        # against one tree. Without this the decisions collide with the very
        # surfaces they are re-creating and the diagnostic measures nothing.
        if scratch.resolve(surface) is not None:
            scratch = ablate(scratch, surface)
    before_nodes = len(scratch.nodes)
    created: "set[str]" = set()
    applied = chained = failed = 0
    failures: "list[str]" = []

    for record in records:
        referenced = {
            getattr(action, "node_id", None) or getattr(action, "parent", None)
            for action in record.decision.actions
        }
        result = apply_decision(scratch, record.decision, cut=cut)
        if result.ok:
            applied += 1
            if referenced & created:
                chained += 1
            created.update(result.diff.created)
        else:
            failed += 1
            failures.append(f"{record.decision.surface}: {result.error}")

    invariants_ok = True
    invariant_error = ""
    try:
        scratch.check_invariants()
    except Exception as exc:  # noqa: BLE001 - reported, not handled
        invariants_ok, invariant_error = False, str(exc)

    names: "dict[str, int]" = {}
    for node_id in scratch.nodes:
        key = str_normalize(scratch.name(node_id))
        names[key] = names.get(key, 0) + 1
    duplicates_after = sum(1 for count in names.values() if count > 1)

    base_names: "dict[str, int]" = {}
    for node_id in onto.nodes:
        key = str_normalize(onto.name(node_id))
        base_names[key] = base_names.get(key, 0) + 1
    duplicates_before = sum(1 for count in base_names.values() if count > 1)

    return {
        "n": len(records),
        "applied": applied,
        "failed": failed,
        "apply_rate": applied / len(records) if records else float("nan"),
        "chaining_rate": chained / applied if applied else float("nan"),
        "nodes_before": before_nodes,
        "nodes_after": len(scratch.nodes),
        "node_drift": len(scratch.nodes) - before_nodes,
        "duplicate_names_before": duplicates_before,
        "duplicate_names_after": duplicates_after,
        "invariants_ok": invariants_ok,
        "invariant_error": invariant_error,
        "failures": failures[:20],
    }


# --------------------------------------------------------------------------- #
# Adjudication
# --------------------------------------------------------------------------- #


def build_pairs(
    eval_items: "Sequence[EvalItem]",
    scores: "Sequence[ItemScore]",
    *,
    onto: Ontology,
    cut: Cut,
    seed: int = 42,
) -> "tuple[list[Pair], dict[str, int]]":
    """Blind pairs for the disagreements, plus the index of each pair's item.

    Agreements never reach the judge: identical placements are a tie by
    definition, which is what keeps adjudication cost proportional to
    disagreements rather than to the sample.
    """
    import random as _random

    rng = _random.Random(seed)
    pairs: "list[Pair]" = []
    index: "dict[str, int]" = {}
    for position, (eval_item, score) in enumerate(zip(eval_items, scores)):
        if not score.agent_path:
            continue
        scratch = ablate(onto, eval_item.surface)
        payload = build_payload(scratch, eval_item.item, cut=cut)
        evidence = "\n".join(render_evidence(payload, annotate=False))
        pair = make_pair(
            score.node_id,
            score.name,
            evidence,
            score.reference_path,
            score.agent_path,
            rng=rng,
        )
        if pair is None:
            continue
        pairs.append(pair)
        index[pair.key] = position
    return pairs, index


def apply_verdicts(
    scores: "list[ItemScore]",
    pairs: "Sequence[Pair]",
    verdicts: "Sequence[Verdict]",
    index: "dict[str, int]",
) -> None:
    """Write win scores back onto the item scores, in place.

    Every decided item that produced no pair agreed with the reference, so it
    scores the definitional 0.5.
    """
    for score in scores:
        if score.agent_path:
            score.win = 0.5
    for pair, verdict in zip(pairs, verdicts):
        position = index.get(pair.key)
        if position is not None:
            scores[position].win = score_pair(pair, verdict)


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #


class GateClause(BaseModel):
    """One pre-registered pass/fail check."""

    name: str
    value: float
    threshold: float
    comparison: str = ">="
    passed: bool
    note: str = ""


class Report(BaseModel):
    """Everything the gate reads, in one serializable object."""

    dimension: str
    split: str
    base_version: str
    base_content_hash: str
    run_id: str = ""
    model: str = ""
    n_items: int = 0
    n_decided: int = 0
    n_abstained: int = 0
    n_failed: int = 0
    n_no_evidence: int = 0
    n_residue: int = 0
    coverage: float = float("nan")
    win: "metrics.WinRate | None" = None
    win_excluding_residue: "metrics.WinRate | None" = None
    win_by_stratum: "dict[str, float]" = Field(default_factory=dict)
    w_at_coverage: float = float("nan")
    coverage_curve: "list[metrics.CoveragePoint]" = Field(default_factory=list)
    hierarchical: "dict[str, Any]" = Field(default_factory=dict)
    distribution: "dict[str, Any]" = Field(default_factory=dict)
    agreement: "dict[str, Any]" = Field(default_factory=dict)
    harmlessness: "dict[str, Any]" = Field(default_factory=dict)
    consistency: "dict[str, Any]" = Field(default_factory=dict)
    probe_results: "dict[str, Any]" = Field(default_factory=dict)
    replay: "dict[str, Any]" = Field(default_factory=dict)
    canary: "dict[str, Any]" = Field(default_factory=dict)
    gate: "list[GateClause]" = Field(default_factory=list)

    @property
    def gate_passed(self) -> bool:
        return bool(self.gate) and all(clause.passed for clause in self.gate)


def _mean(values: "Sequence[float]") -> float:
    return sum(values) / len(values) if values else float("nan")


def build_report(
    onto: Ontology,
    eval_items: "Sequence[EvalItem]",
    scores: "Sequence[ItemScore]",
    *,
    dimension: str,
    split: str,
    cut: Cut,
    seed: int = 42,
    coverage_target: float = DEFAULT_COVERAGE,
    run_id: str = "",
    model: str = "",
) -> Report:
    """Aggregate per-item scores into the reported numbers. No API calls."""
    answered = decided(scores)
    report = Report(
        dimension=dimension,
        split=split,
        base_version=str(onto.doc.meta.version),
        base_content_hash=content_hash(onto),
        run_id=run_id,
        model=model,
        n_items=len(scores),
        n_decided=len(answered),
        n_abstained=sum(1 for s in scores if s.outcome == Outcome.ABSTAINED.value),
        n_failed=sum(1 for s in scores if not s.applied),
        n_no_evidence=sum(1 for s in scores if not s.has_evidence),
        n_residue=sum(1 for s in scores if s.has_residue),
        coverage=len(answered) / len(scores) if scores else float("nan"),
    )

    wins = [s.win for s in answered if s.win is not None]
    if wins:
        report.win = metrics.win_rate(wins, seed=seed)
        clean = [s.win for s in answered if s.win is not None and not s.has_residue]
        if clean and len(clean) != len(wins):
            report.win_excluding_residue = metrics.win_rate(clean, seed=seed)
        report.win_by_stratum = _win_by_stratum(answered)
        curve = metrics.risk_coverage(
            [(s.win, s.confidence) for s in answered if s.win is not None],
            n_total=len(scores),
        )
        report.coverage_curve = curve
        report.w_at_coverage = metrics.w_at_coverage(curve, coverage_target)

    hiers = [s.hier for s in answered if s.hier is not None]
    if hiers:
        depths: "dict[str, int]" = {}
        for hier in hiers:
            if not hier.same_lineage:
                key = str(hier.lca_depth)
                depths[key] = depths.get(key, 0) + 1
        report.hierarchical = {
            "n": len(hiers),
            "precision": _mean([h.precision for h in hiers]),
            "recall": _mean([h.recall for h in hiers]),
            "f1": _mean([h.f1 for h in hiers]),
            "same_lineage_rate": _mean([float(h.same_lineage) for h in hiers]),
            "off_lineage_lca_depth": dict(sorted(depths.items())),
        }

    agent_cats = [s.agent_category for s in answered]
    ref_cats = [s.reference_category for s in answered]
    agent_shares = metrics.shares(agent_cats)
    ref_shares = metrics.shares(ref_cats)
    report.distribution = {
        "agent_shares": agent_shares,
        "reference_shares": ref_shares,
        "spearman": metrics.spearman(agent_shares, ref_shares),
        "top5_overlap": metrics.top_k_overlap(agent_shares, ref_shares, 5),
        "total_variation": metrics.total_variation(agent_shares, ref_shares),
    }

    majority = majority_baseline(ref_cats)
    report.agreement = {
        "n": len(answered),
        "rate": metrics.agreement(agent_cats, ref_cats),
        "cohen_kappa": metrics.cohen_kappa(agent_cats, ref_cats),
        "macro_recall": metrics.macro_recall(agent_cats, ref_cats),
        "majority_baseline": {
            "rate": metrics.agreement(majority, ref_cats),
            "macro_recall": metrics.macro_recall(majority, ref_cats),
        },
    }

    report.harmlessness = {
        "schema_valid": _mean(
            [float(s.outcome != Outcome.FAILED.value) for s in scores]
        ),
        "apply_success": _mean([float(s.applied) for s in scores]),
        "errors": [s.error for s in scores if s.error][:20],
    }
    return report


def _win_by_stratum(answered: "Sequence[ItemScore]") -> "dict[str, float]":
    """W split by the axes that predict difficulty, so a headline cannot hide one."""
    groups: "dict[str, list[float]]" = {}
    for score in answered:
        if score.win is None:
            continue
        groups.setdefault(f"anchoring={score.anchoring}", []).append(score.win)
        groups.setdefault(
            f"evidence={'yes' if score.has_evidence else 'no'}", []
        ).append(score.win)
        groups.setdefault(f"residue={'yes' if score.has_residue else 'no'}", []).append(
            score.win
        )
    return {key: _mean(values) for key, values in sorted(groups.items())}


def add_levenshtein_baseline(
    report: Report,
    onto: Ontology,
    eval_items: "Sequence[EvalItem]",
    scores: "Sequence[ItemScore]",
    *,
    cut: Cut,
) -> None:
    """Score the Levenshtein placer on the same answered items and file it."""
    answered = [
        (eval_item, score)
        for eval_item, score in zip(eval_items, scores)
        if score.agent_path
    ]
    if not answered:
        return
    predictions = levenshtein_baseline(
        onto, [eval_item for eval_item, _ in answered], cut=cut
    )
    reference = [score.reference_category for _, score in answered]
    report.agreement["levenshtein_baseline"] = {
        "rate": metrics.agreement(predictions, reference),
        "macro_recall": metrics.macro_recall(predictions, reference),
    }


def add_consistency(report: Report, repeats: "Sequence[Sequence[ItemScore]]") -> None:
    """Fleiss' kappa and triple agreement over *k* leave-one-out repeats.

    This **upper-bounds** achievable agreement with any reference, and doubles as
    a leak check: agreement with the legacy tree above the agent's agreement with
    *itself* means memorization or a leak, and nothing else in the report should
    be believed until that is explained.
    """
    if len(repeats) < 2:
        return
    ratings = [
        [run[index].agent_category for run in repeats]
        for index in range(len(repeats[0]))
    ]
    hashes_stable = True
    report.consistency = {
        "k": len(repeats),
        "fleiss_kappa": metrics.fleiss_kappa(ratings),
        "triple_agreement": metrics.triple_agreement(ratings),
        "payload_hash_stable": hashes_stable,
        "exceeds_legacy_agreement": (
            metrics.triple_agreement(ratings) > report.agreement.get("rate", 0.0)
        ),
    }


def payload_hashes_stable(repeats: "Sequence[Sequence[DecisionRecord]]") -> bool:
    """Whether every repeat asked each item the byte-identical question.

    Self-consistency only measures the model if the prompt was fixed; a drifting
    payload would report model variance that is really harness variance.
    """
    if len(repeats) < 2:
        return True
    first = [record.provenance.payload_hash for record in repeats[0]]
    return all(
        [record.provenance.payload_hash for record in run] == first
        for run in repeats[1:]
    )


# --------------------------------------------------------------------------- #
# The gate
# --------------------------------------------------------------------------- #


def evaluate_gate(
    report: Report, *, coverage_target: float = DEFAULT_COVERAGE
) -> "list[GateClause]":
    """The six pre-registered clauses. All must pass.

    Thresholds are the ones written into #53 **before** the gate run; they are
    read from the issue, not chosen from the numbers. Clause 2 is void if the
    memorization canary fired, because every raw-agreement number it reads would
    then be measuring recall of a public file rather than judgment.
    """
    clauses: "list[GateClause]" = []

    def add(
        name: str,
        value: float,
        threshold: float,
        *,
        comparison: str = ">=",
        note: str = "",
    ) -> None:
        if value != value:  # nan -- not measured, or undefined
            passed = False
            note = (note + " (not measured)").strip()
        elif comparison == ">=":
            passed = value >= threshold
        else:
            passed = value <= threshold
        clauses.append(
            GateClause(
                name=name,
                value=value,
                threshold=threshold,
                comparison=comparison,
                passed=passed,
                note=note,
            )
        )

    win = report.win
    add(
        "1. LB95(W)",
        win.lower_bound if win else float("nan"),
        0.45,
        note=f"W={win.w:.3f} (l={win.lost}, t={win.tied}, g={win.won})" if win else "",
    )
    add(
        f"1b. W@coverage={coverage_target}",
        report.w_at_coverage,
        0.45,
        note=(
            "the agent never reaches that coverage"
            if report.w_at_coverage != report.w_at_coverage
            else ""
        ),
    )

    canary = bool(report.canary.get("fired"))
    levenshtein = report.agreement.get("levenshtein_baseline", {})
    baseline = levenshtein.get("rate", float("nan"))
    baseline_macro = levenshtein.get("macro_recall", float("nan"))
    floor = max(0.70, baseline + 0.10) if baseline == baseline else 0.70
    if canary:
        clauses.append(
            GateClause(
                name="2. report-facing floor",
                value=float("nan"),
                threshold=floor,
                passed=True,
                note="VOID: the memorization canary fired; only W and the "
                "reference-free probes count",
            )
        )
    else:
        add(
            "2a. cut agreement",
            report.agreement.get("rate", float("nan")),
            floor,
            note=(
                f"floor = max(0.70, levenshtein {baseline:.3f} + 0.10)"
                if baseline == baseline
                else "no levenshtein baseline computed"
            ),
        )
        add("2b. Cohen kappa", report.agreement.get("cohen_kappa", float("nan")), 0.55)
        add(
            "2c. macro-recall (non-Other)",
            report.agreement.get("macro_recall", float("nan")),
            0.60,
            # The 0.60 threshold is the pre-registered one, kept as written. It is
            # printed next to the Levenshtein baseline because on dev that free
            # baseline already scores 0.653: a clause a string matcher passes is
            # not discriminating, and this is what makes that visible instead of
            # quietly reassuring.
            note=(
                f"levenshtein baseline scores {baseline_macro:.3f} here"
                if baseline_macro == baseline_macro
                else ""
            ),
        )
        add("2d. Spearman rho", report.distribution.get("spearman", float("nan")), 0.90)
        add(
            "2e. top-5 unchanged",
            report.distribution.get("top5_overlap", float("nan")),
            1.0,
        )

    add("3a. schema valid", report.harmlessness.get("schema_valid", float("nan")), 1.0)
    add(
        "3b. apply success",
        report.harmlessness.get("apply_success", float("nan")),
        0.99,
    )
    noop = report.probe_results.get("noop", {})
    add("3c. no-op control", noop.get("noop_rate", float("nan")), 0.95)
    add(
        "3d. destructive ops outside candidates",
        float(noop.get("destructive", 0)),
        0.0,
        comparison="<=",
    )

    add(
        "4a. triple agreement",
        report.consistency.get("triple_agreement", float("nan")),
        0.75,
    )
    add(
        "4b. self-consistency > legacy agreement",
        float(
            report.consistency.get("exceeds_legacy_agreement", float("nan"))
            if report.consistency
            else float("nan")
        ),
        1.0,
    )

    ambiguity = report.probe_results.get("ambiguity", {})
    add("5a. Youden J", ambiguity.get("youden_j", float("nan")), 0.70)
    add("5b. coverage", report.coverage, coverage_target)
    add(
        "5c. policy conformance",
        report.probe_results.get("policy", {}).get("conformance", float("nan")),
        0.90,
    )

    ignore = report.probe_results.get("ignore", {})
    add("6a. mark_ignore precision", ignore.get("precision", float("nan")), 0.80)
    add("6b. mark_ignore recall", ignore.get("recall", float("nan")), 0.60)

    return clauses


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return "n/a" if value != value else f"{value:.3f}"
    return str(value)


def render_report(report: Report) -> str:
    """The committed report: the numbers, then the verdict."""
    lines = [
        f"# Categorization eval -- {report.dimension} / {report.split}",
        "",
        f"- base: `{report.base_version}` (`{report.base_content_hash[:12]}`)",
        f"- model: `{report.model or 'n/a'}`  run: `{report.run_id or 'n/a'}`",
        f"- items: {report.n_items} "
        f"({report.n_decided} decided, {report.n_abstained} abstained, "
        f"{report.n_failed} failed to apply)",
        f"- {report.n_no_evidence} items have no corpus evidence; "
        f"{report.n_residue} leave ablation residue",
        "",
        "## Primary -- blind pairwise win rate",
        "",
    ]
    if report.win is None:
        lines.append("_not adjudicated_")
    else:
        win = report.win
        lines += [
            f"- **W = {_fmt(win.w)}**  (95% CI {_fmt(win.lower_bound)}"
            f"-{_fmt(win.upper_bound)}, n={win.n})",
            f"- lost {win.lost} / tied {win.tied} / won {win.won}"
            "  -- 0.5 is the analytic ceiling",
            f"- W@coverage={DEFAULT_COVERAGE}: {_fmt(report.w_at_coverage)}",
        ]
        if report.win_excluding_residue is not None:
            excl = report.win_excluding_residue
            lines.append(
                f"- excluding the {report.n_residue} residue items: "
                f"W = {_fmt(excl.w)} (n={excl.n})"
            )
        if report.win_by_stratum:
            lines += ["", "| stratum | W |", "|---|---|"]
            lines += [
                f"| {key} | {_fmt(value)} |"
                for key, value in report.win_by_stratum.items()
            ]

    for title, block in (
        ("Hierarchy-aware agreement", report.hierarchical),
        ("Agreement with the legacy tree", report.agreement),
        ("Distributional shape", report.distribution),
        ("Harmlessness", report.harmlessness),
        ("Self-consistency", report.consistency),
        ("Reference-free probes", report.probe_results),
        ("Sequential-replay diagnostic", report.replay),
        ("Memorization canary", report.canary),
    ):
        if not block:
            continue
        lines += ["", f"## {title}", ""]
        lines += _render_block(block)

    lines += ["", "## Gate", ""]
    if not report.gate:
        lines.append("_not evaluated_")
    else:
        lines += ["| clause | value | | threshold | verdict |", "|---|---|---|---|---|"]
        for clause in report.gate:
            lines.append(
                f"| {clause.name} | {_fmt(clause.value)} | {clause.comparison} | "
                f"{_fmt(clause.threshold)} | {'PASS' if clause.passed else 'FAIL'}"
                f"{(' -- ' + clause.note) if clause.note else ''} |"
            )
        lines += [
            "",
            f"**Verdict: {'PASS' if report.gate_passed else 'FAIL'}** "
            f"({sum(c.passed for c in report.gate)}/{len(report.gate)} clauses)",
        ]
    return "\n".join(lines) + "\n"


def _render_block(block: "dict[str, Any]", indent: str = "") -> "list[str]":
    lines: "list[str]" = []
    for key, value in block.items():
        if isinstance(value, dict):
            if not value:
                continue
            lines.append(f"{indent}- **{key}**:")
            lines += _render_block(value, indent + "  ")
        elif isinstance(value, list):
            if not value:
                continue
            shown = ", ".join(_fmt(entry) for entry in value[:8])
            more = f" (+{len(value) - 8} more)" if len(value) > 8 else ""
            lines.append(f"{indent}- {key}: {shown}{more}")
        else:
            lines.append(f"{indent}- {key}: {_fmt(value)}")
    return lines


# --------------------------------------------------------------------------- #
# Running the reference-free probes
# --------------------------------------------------------------------------- #


def _item_for(
    surface: str, name: str, corpus: "dict[str, Item]", dimension: str
) -> Item:
    """The corpus item for *surface*, or an evidence-free stand-in."""
    found = corpus.get(str_normalize(surface))
    if found is not None:
        return found
    return Item(
        dimension=dimension,
        surface=str_normalize(surface),
        name=name or surface,
        spellings=[name or surface],
    )


def _hide(onto: Ontology, surface: str) -> Ontology:
    """*onto* with *surface* ablated, or *onto* itself when it cannot be hidden.

    A probe surface is not drawn from the sealed pool, so it may not be in the
    tree at all, or may name a node with children that ablation would orphan.
    Either way the case is still worth asking -- it just is not a held-out one.
    """
    from paperext.categorize.ablate import ablatable

    return ablate(onto, surface) if ablatable(onto, surface) else onto


def _candidate_ids(onto: Ontology, item: Item, *, cut: Cut) -> "set[str]":
    """The node ids the agent was actually shown for *item*."""
    return {view.id for view in build_payload(onto, item, cut=cut).candidates}


async def run_noop_probe(
    onto: Ontology,
    surfaces: "Sequence[str]",
    corpus: "dict[str, Item]",
    decider: Decider,
    *,
    dimension: str,
    cut: Cut,
    n: int = 100,
    seed: int = 42,
    concurrency: int = 4,
) -> "dict[str, Any]":
    """Already-mapped names against the **un-ablated** tree: correct = change nothing.

    Zero subjectivity, and it is the probe that catches an agent which churns the
    tree because it was asked a question and felt obliged to answer.
    """
    cases = probes.noop_cases(surfaces, n=n, seed=seed)
    if not cases:
        return {}
    items = [_item_for(case.surface, case.surface, corpus, dimension) for case in cases]
    records = await decide_all(
        [(onto, item) for item in items],
        decider,
        dimension=dimension,
        concurrency=concurrency,
        ablated=False,
    )
    noops = [probes.is_noop(record) for record in records]
    outside: "list[str]" = []
    for item, record in zip(items, records):
        outside += probes.destructive_ops(
            record, allowed=_candidate_ids(onto, item, cut=cut)
        )
    return {
        "n": len(cases),
        "noop_rate": sum(noops) / len(noops),
        "destructive": len(outside),
        "destructive_examples": outside[:10],
    }


async def run_policy_probe(
    onto: Ontology,
    corpus_items: "Sequence[Item]",
    decider: Decider,
    *,
    dimension: str,
    cut: Cut,
    limit: "int | None" = 60,
    seed: int = 42,
    concurrency: int = 4,
) -> "dict[str, Any]":
    """Alias pairs whose answer the locked granularity policy already fixes."""
    cases = probes.policy_cases(onto, corpus_items, limit=limit, seed=seed)
    if not cases:
        return {}
    corpus = {item.surface: item for item in corpus_items}
    trees_items: "list[tuple[Ontology, Item]]" = []
    for case in cases:
        trees_items.append(
            (
                _hide(onto, case.surface),
                _item_for(case.surface, case.surface, corpus, dimension),
            )
        )
    records = await decide_all(
        trees_items, decider, dimension=dimension, concurrency=concurrency
    )
    return probes.score_policy(cases, records)


async def run_ambiguity_probe(
    onto: Ontology,
    corpus_items: "Sequence[Item]",
    decider: Decider,
    *,
    dimension: str,
    n_acronym: int = 40,
    seed: int = 42,
    concurrency: int = 4,
) -> "dict[str, Any]":
    """The abstention 2x2, on matched items.

    The ambiguity is **injected**, not found: a copy of the item's name is added
    under its own branch *and* under a foreign one, so two exact-name candidates
    exist and nothing but the paper evidence separates them. Strip the evidence
    and abstention is correct by construction.

    The grounded arm is not optional. Without it "always abstain" scores a
    perfect abstention recall, and the probe would reward exactly the behaviour
    that makes the agent useless.
    """
    import random as _random

    picked = probes.acronym_items(onto, corpus_items, n=n_acronym, seed=seed)
    if not picked:
        return {}

    rng = _random.Random(seed)
    branches = sorted(
        node_id
        for root in onto.doc.roots
        for node_id in onto.children(root)
        if onto.children(node_id)
    )
    if len(branches) < 2:
        return {}

    homonym_cases: "list[tuple[Ontology, Item]]" = []
    plain_cases: "list[tuple[Ontology, Item]]" = []
    for item in picked:
        node_id = onto.resolve(item.surface)
        base = _hide(onto, item.surface)
        plain_cases.append((base, item))
        home = probes.branch_of(onto, node_id) if node_id else None
        foreign = rng.choice([b for b in branches if b != home]) if branches else None
        parents = [p for p in (home, foreign) if p is not None]
        if len(parents) < 2:
            continue
        scratch = probes.inject_homonym(
            base,
            item.name,
            parents,
            node_ids=[f"__homonym_{index}_{item.surface}" for index in range(2)],
        )
        homonym_cases.append((scratch, probes.strip_grounding(item)))

    stripped_cases = [
        (tree, probes.strip_grounding(item)) for tree, item in plain_cases
    ]

    should_abstain, should_resolve, stripped_only = await asyncio.gather(
        decide_all(
            homonym_cases, decider, dimension=dimension, concurrency=concurrency
        ),
        decide_all(plain_cases, decider, dimension=dimension, concurrency=concurrency),
        decide_all(
            stripped_cases, decider, dimension=dimension, concurrency=concurrency
        ),
    )
    return probes.score_ambiguity(should_abstain, should_resolve, stripped_only)


def ignore_pool(onto: Ontology, *, root: str = "ignore") -> "list[tuple[str, str]]":
    """``(surface, name)`` for every ablatable leaf under the dropped root.

    The legacy tree already decided these are not entities worth counting, and
    that judgment is far less arguable than a placement -- which is why
    ``mark_ignore`` gets its own gate clause: a false ignore silently removes a
    real entity from every downstream count.
    """
    from paperext.categorize.ablate import ablatable as _ablatable

    if root not in onto:
        return []
    pool: "list[tuple[str, str]]" = []
    stack = list(onto.children(root))
    while stack:
        node_id = stack.pop()
        children = onto.children(node_id)
        stack.extend(children)
        if children:
            continue
        surfaces = onto.surfaces(node_id)
        name = onto.name(node_id)
        if not surfaces or not name.strip():
            continue
        if _ablatable(onto, surfaces[0]):
            pool.append((surfaces[0], name))
    return sorted(pool)


def marked_ignore(record: DecisionRecord, *, root: str = "ignore") -> bool:
    """Whether the decision put the name out of the counted tree."""
    if any(action.op == "mark_ignore" for action in record.decision.actions):
        return True
    placement = record.result.placement
    return placement is not None and str_normalize(placement.branch or "") == root


async def run_ignore_probe(
    onto: Ontology,
    negatives: "Sequence[str]",
    corpus: "dict[str, Item]",
    decider: Decider,
    *,
    dimension: str,
    n: int = 60,
    seed: int = 42,
    concurrency: int = 4,
) -> "dict[str, Any]":
    """Precision and recall of ``mark_ignore`` against the legacy ignore root."""
    import random as _random

    rng = _random.Random(seed)
    pool = ignore_pool(onto)
    if not pool:
        return {}
    positives = pool if len(pool) <= n else sorted(rng.sample(pool, n))
    negative_pool = sorted(set(negatives))
    chosen_negatives = (
        negative_pool
        if len(negative_pool) <= n
        else sorted(rng.sample(negative_pool, n))
    )

    cases = [
        (_hide(onto, surface), _item_for(surface, name, corpus, dimension))
        for surface, name in positives
    ] + [
        (_hide(onto, surface), _item_for(surface, surface, corpus, dimension))
        for surface in chosen_negatives
    ]
    records = await decide_all(
        cases, decider, dimension=dimension, concurrency=concurrency
    )
    flags = [marked_ignore(record) for record in records]
    true_positive = sum(flags[: len(positives)])
    false_positive = sum(flags[len(positives) :])
    predicted = true_positive + false_positive
    return {
        "n_positive": len(positives),
        "n_negative": len(chosen_negatives),
        "precision": true_positive / predicted if predicted else float("nan"),
        "recall": true_positive / len(positives) if positives else float("nan"),
    }


# --------------------------------------------------------------------------- #
# Memorization canary
# --------------------------------------------------------------------------- #


async def run_canary(
    client: Any,
    *,
    path: "Union[str, Path]" = "data/categorized_models.json",
    threshold: float = 0.5,
) -> "dict[str, Any]":
    """Ask the pinned model to recall the published reference file's structure.

    Run this **first**. It costs five minutes and it decides whether the
    report-facing agreement floor means anything at all.
    """
    questions = probes.canary_probes(path)
    scores: "list[float]" = []
    answers: "list[dict[str, Any]]" = []
    for probe in questions:
        payload: Any = [{"role": "user", "content": probe.question}]
        answer, _ = await client.chat.completions.create_with_completion(
            response_model=probes.CanaryAnswer, messages=payload, max_retries=2
        )
        score = probes.score_canary(probe, answer.keys)
        scores.append(score)
        answers.append(
            {
                "question": probe.question.splitlines()[-1],
                "remembered": answer.remembered,
                "recall": score,
                "n_expected": len(probe.expected),
            }
        )
    return {
        "fired": probes.canary_fired(scores, threshold=threshold),
        "max_recall": max(scores) if scores else float("nan"),
        "threshold": threshold,
        "answers": answers,
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Held-out categorization eval and decision gate (#53).",
    )
    parser.add_argument("--dim", default="models", help="dimension to evaluate")
    parser.add_argument("--base", default="v0", help="ontology version to eval against")
    parser.add_argument("--root", default=None, help="ontology root dir override")
    parser.add_argument(
        "--splits", default=None, help="splits manifest (default: the sealed one)"
    )
    parser.add_argument(
        "--split",
        default="dev",
        choices=("dev", "gate", "reserve"),
        help="which split to score -- 'gate' is sealed, open it deliberately",
    )
    parser.add_argument("--items", default=None, help="corpus items jsonl")
    parser.add_argument("--limit-items", type=int, default=None)
    parser.add_argument(
        "--replay",
        default=None,
        help="score a recorded decisions.jsonl instead of calling the model",
    )
    parser.add_argument("--out", default=None, help="directory for the report")
    parser.add_argument("--verdicts", default=None, help="verdict cache jsonl")
    parser.add_argument(
        "--adjudicate",
        action="store_true",
        help="run the blind judge over the disagreements",
    )
    parser.add_argument("--k", type=int, default=1, help="self-consistency repeats")
    parser.add_argument("--probes", action="store_true", help="run the control sets")
    parser.add_argument("--canary", action="store_true", help="run the canary only")
    parser.add_argument("--replay-diagnostic", action="store_true")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--coverage", type=float, default=DEFAULT_COVERAGE)
    parser.add_argument("--platform", default=None)
    parser.add_argument("--model", default=None)
    return parser


def _load_splits(args: argparse.Namespace) -> Splits:
    from paperext.categorize.apply import ontology_root

    path = (
        Path(args.splits)
        if args.splits
        else Path(ontology_root()) / "eval" / args.dim / "splits.json"
    )
    return Splits.model_validate_json(path.read_text(encoding="utf-8"))


def _load_corpus(args: argparse.Namespace) -> "list[Item]":
    if args.items:
        return read_items(args.items)
    return build_items(args.dim)


async def _run(args: argparse.Namespace) -> Report:
    from paperext.categorize.apply import ontology_root

    root = Path(args.root) if args.root else Path(ontology_root())
    onto = Ontology.load(root / args.dim / args.base)
    cut = load_dimension_cut(args.dim)
    splits = _load_splits(args)
    split_items: "list[SplitItem]" = list(getattr(splits, args.split))
    if args.limit_items:
        split_items = split_items[: args.limit_items]

    corpus_items = _load_corpus(args)
    corpus = {item.surface: item for item in corpus_items}
    eval_items = build_eval_items(
        onto, split_items, corpus_items, dimension=args.dim, cut=cut
    )

    if args.replay:
        decider = replay_decider(args.replay, cut=cut)
        model = "replay"
        client: Any = None
    else:
        from paperext.categorize.agent import categorize_settings, make_client

        platform, model = args.platform or "", args.model or ""
        if not platform or not model:
            default_platform, default_model = categorize_settings()
            platform = platform or default_platform
            model = model or default_model
        client = make_client(platform, model)
        decider = agent_decider(client, cut=cut)

    if args.canary:
        if client is None:
            raise SystemExit("--canary needs a live client (drop --replay)")
        report = Report(
            dimension=args.dim,
            split=args.split,
            base_version=args.base,
            base_content_hash=content_hash(onto),
            model=model,
        )
        report.canary = await run_canary(client)
        return report

    run_id = uuid.uuid4().hex[:12]
    log = DecisionLog(Path(args.out) / DECISIONS_FILE) if args.out else None
    try:
        repeats_records = [
            await leave_one_out(
                onto,
                eval_items,
                decider,
                dimension=args.dim,
                cut=cut,
                run_id=f"{run_id}-{index}",
                model=model,
                concurrency=args.concurrency,
                log=log if index == 0 else None,
            )
            for index in range(max(1, args.k))
        ]
    finally:
        if log is not None:
            log.close()

    repeats_scores = [score_items(eval_items, run) for run in repeats_records]
    scores = repeats_scores[0]

    report = build_report(
        onto,
        eval_items,
        scores,
        dimension=args.dim,
        split=args.split,
        cut=cut,
        seed=args.seed,
        coverage_target=args.coverage,
        run_id=run_id,
        model=model,
    )
    add_levenshtein_baseline(report, onto, eval_items, scores, cut=cut)
    add_consistency(report, repeats_scores)
    if report.consistency:
        report.consistency["payload_hash_stable"] = payload_hashes_stable(
            repeats_records
        )

    if args.adjudicate:
        pairs, index = build_pairs(
            eval_items, scores, onto=onto, cut=cut, seed=args.seed
        )
        cache = VerdictCache(
            args.verdicts or (Path(args.out) / VERDICTS_FILE if args.out else None)
        )
        verdicts = await _judge(pairs, cache, args)
        apply_verdicts(scores, pairs, verdicts, index)
        report = build_report(
            onto,
            eval_items,
            scores,
            dimension=args.dim,
            split=args.split,
            cut=cut,
            seed=args.seed,
            coverage_target=args.coverage,
            run_id=run_id,
            model=model,
        )
        add_levenshtein_baseline(report, onto, eval_items, scores, cut=cut)
        add_consistency(report, repeats_scores)

    if args.probes:
        reserve = [item.surface for item in splits.reserve]
        report.probe_results = {
            "noop": await run_noop_probe(
                onto,
                reserve,
                corpus,
                decider,
                dimension=args.dim,
                cut=cut,
                seed=args.seed,
                concurrency=args.concurrency,
            ),
            "policy": await run_policy_probe(
                onto,
                corpus_items,
                decider,
                dimension=args.dim,
                cut=cut,
                seed=args.seed,
                concurrency=args.concurrency,
            ),
            "ambiguity": await run_ambiguity_probe(
                onto,
                corpus_items,
                decider,
                dimension=args.dim,
                seed=args.seed,
                concurrency=args.concurrency,
            ),
            "ignore": await run_ignore_probe(
                onto,
                reserve,
                corpus,
                decider,
                dimension=args.dim,
                seed=args.seed,
                concurrency=args.concurrency,
            ),
        }

    if args.replay_diagnostic:
        report.replay = sequential_replay(
            onto,
            repeats_records[0],
            cut=cut,
            surfaces=[item.surface for item in eval_items],
        )

    report.gate = evaluate_gate(report, coverage_target=args.coverage)

    if args.out:
        _write(Path(args.out), report, scores)
    return report


async def _judge(
    pairs: "Sequence[Pair]", cache: VerdictCache, args: argparse.Namespace
) -> "list[Verdict]":
    """Adjudicate with a different-vendor judge, checking the order-swap guardrail."""
    from paperext.categorize.adjudicate import (
        judge_settings,
        llm_judge,
        order_swap_consistency,
    )
    from paperext.categorize.agent import make_client

    platform, model = judge_settings()
    judge = llm_judge(make_client(platform, model))
    verdicts = await adjudicate(
        pairs, judge, cache=cache, concurrency=args.concurrency, judge_name=model
    )

    import random as _random

    rng = _random.Random(args.seed)
    sample = (
        pairs
        if len(pairs) <= 20
        else [pairs[i] for i in sorted(rng.sample(range(len(pairs)), 20))]
    )
    if sample:
        mirrored = await adjudicate(
            [swap(pair) for pair in sample], judge, concurrency=args.concurrency
        )
        first = [next(v for v in verdicts if v.key == p.key) for p in sample]
        consistency = order_swap_consistency(sample, first, mirrored)
        logger.info(
            "judge order-swap consistency: %.2f (n=%d)", consistency, len(sample)
        )
    return verdicts


def _write(out: Path, report: Report, scores: "Sequence[ItemScore]") -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / REPORT_JSON).write_text(report.model_dump_json(indent=2), encoding="utf-8")
    (out / REPORT_MD).write_text(render_report(report), encoding="utf-8")
    with (out / SCORES_FILE).open("w", encoding="utf-8") as handle:
        for score in scores:
            handle.write(score.model_dump_json() + "\n")


def main(argv: "Sequence[str] | None" = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    report = asyncio.run(_run(args))
    sys.stdout.write(render_report(report))
    if not report.gate:
        return 0
    return 0 if report.gate_passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
