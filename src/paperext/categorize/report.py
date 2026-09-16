"""``categorize-report``: what a run did, read back from its ``decisions.jsonl``.

For looking at decisions on *new* names after a run -- not for scoring against a
reference tree, which is :mod:`paperext.categorize.evaluate`'s job.

The file is replayed onto a copy of the base version it was taken against, so
the report shows the tree **before** and **after** rather than trusting the
recorded diffs, and any decision that no longer applies says so. Records the
reviewer skipped (``provenance.params.review != "apply"``) and records the
applier rejected are not replayed, because they were never applied.

Four sections, in the order a reader needs them:

1. **decisions** -- one line each: outcome glyph, name, where it landed at the
   cut, confidence, and a marker when the decision also edited the tree beyond
   its own name.
2. **structural fixes** -- every rename / move / demote / insert / remove, listed
   on its own. Six renames in twenty decisions is a lot of "fix what you see",
   and each one touched something *another* name depends on; a plain outcome
   count hides exactly these.
3. **tree diff** -- the touched part of the tree after the run, with ``+`` for
   created, ``~`` for modified (old name shown for renames), ``-`` for deleted,
   and the untouched ancestors for orientation.
4. **at the cut** -- where this run's names landed per category, and the node
   count per category before and after.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence, Union

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from paperext.analysis.rollup import Cut
from paperext.categorize.ablate import copy_ontology
from paperext.categorize.actions import Outcome
from paperext.categorize.apply import (
    DecisionDiff,
    DecisionRecord,
    _snapshot,
    apply_decision,
    diff_snapshots,
    ontology_root,
    read_decisions,
)
from paperext.categorize.placement import load_dimension_cut, to_placement
from paperext.categorize.review import Review, read_reviews
from paperext.ontology.ontology import Ontology

PROG = "categorize-report"

GLYPH = {
    Outcome.MAPPED: "->",
    Outcome.CREATED: "+ ",
    Outcome.ABSTAINED: "? ",
    Outcome.NO_OP: "= ",
    Outcome.FAILED: "! ",
}

#: Ops that change something other than the decision's own name.
STRUCTURAL = frozenset(
    {
        "rename",
        "move",
        "insert_above",
        "demote_to_variant",
        "remove_node",
        "mark_ignore",
    }
)


class Replay:
    """The base tree, the tree after replaying the file, and everything between."""

    def __init__(
        self,
        base: Ontology,
        records: "Sequence[DecisionRecord]",
        *,
        cut: Cut,
        reviews: "Sequence[Review]" = (),
    ) -> None:
        self.base = base
        self.records = list(records)
        self.cut = cut
        self.reviews = {(r.run_id, r.seq): r for r in reviews}
        self.after = copy_ontology(base)
        self.replayed: "list[bool]" = []
        self.failures: "dict[int, str]" = {}
        before = _snapshot(self.after)
        for index, record in enumerate(self.records):
            if not self._was_applied(record):
                self.replayed.append(False)
                continue
            result = apply_decision(self.after, record.decision, cut=cut)
            self.replayed.append(result.ok)
            if not result.ok:
                self.failures[index] = result.error or "rejected"
        self.diff: DecisionDiff = diff_snapshots(before, _snapshot(self.after))
        self.before_names = {nid: base.name(nid) for nid in base.nodes}

    @staticmethod
    def _was_applied(record: DecisionRecord) -> bool:
        if not record.result.ok:
            return False
        review = record.provenance.params.get("review")
        return review in (None, "apply")

    def review_for(self, record: DecisionRecord) -> "Review | None":
        return self.reviews.get((record.provenance.run_id, record.provenance.seq))


# --------------------------------------------------------------------------- #
# Sections
# --------------------------------------------------------------------------- #


def _structural(record: DecisionRecord) -> "list[str]":
    out = []
    for action in record.decision.actions:
        if action.op not in STRUCTURAL:
            continue
        args = {
            key: value
            for key, value in action.model_dump().items()
            if key
            not in {"op", "justification", "confidence", "description", "examples"}
        }
        out.append(f"{action.op}({', '.join(f'{k}={v!r}' for k, v in args.items())})")
    return out


def header(replay: Replay) -> "list[str]":
    records = replay.records
    first = records[0].provenance if records else None
    counts: "dict[str, int]" = {}
    for record in records:
        key = record.decision.outcome.value
        counts[key] = counts.get(key, 0) + 1
    usage_in = sum(
        (r.provenance.params.get("usage") or {}).get("input_tokens", 0) for r in records
    )
    usage_out = sum(
        (r.provenance.params.get("usage") or {}).get("output_tokens", 0)
        for r in records
    )
    lines = [
        f"run {first.run_id if first else '?'}  model {first.model if first else '?'}"
        f"  base {first.base_version if first else '?'}"
        f"  ({first.dimension if first else '?'})",
        f"{len(records)} decision(s): "
        + ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
        + f"; {sum(replay.replayed)} applied",
    ]
    if replay.failures:
        lines.append(f"{len(replay.failures)} no longer apply on replay (see below)")
    if usage_in or usage_out:
        lines.append(f"tokens: {usage_in:,} in / {usage_out:,} out")
    if replay.reviews:
        verdicts: "dict[str, int]" = {}
        for review in replay.reviews.values():
            verdicts[review.verdict] = verdicts.get(review.verdict, 0) + 1
        lines.append(
            "reviewer: " + ", ".join(f"{v} {k}" for k, v in sorted(verdicts.items()))
        )
    return lines


def decisions_table(replay: Replay) -> Table:
    table = Table(title="decisions", title_justify="left", expand=True, pad_edge=False)
    table.add_column("#", width=3, no_wrap=True)
    table.add_column("", width=2, no_wrap=True)
    table.add_column("name", ratio=2, overflow="ellipsis", no_wrap=True)
    table.add_column("landed", ratio=4, overflow="ellipsis", no_wrap=True)
    table.add_column("cut", width=14, overflow="ellipsis", no_wrap=True)
    table.add_column("conf", width=4, no_wrap=True, justify="right")
    table.add_column("fixes", width=5, no_wrap=True)
    if replay.reviews:
        table.add_column("review", ratio=3)  # the human's words: wrap, never clip

    for index, record in enumerate(replay.records, start=1):
        decision, placement = record.decision, record.result.placement
        landed = " > ".join(placement.ancestor_names) if placement else ""
        if decision.outcome is Outcome.ABSTAINED:
            landed = "abstained: " + "; ".join(decision.review_notes) or "abstained"
        elif index - 1 in replay.failures:
            landed = f"NOT APPLIED on replay: {replay.failures[index - 1]}"
        elif not replay.replayed[index - 1] and record.result.ok:
            landed = f"(skipped by reviewer) {landed}"
        cut = placement.cut_category if placement else ""
        if placement is not None and placement.cut_category is None:
            cut = "(ignore)"
        fixes = _structural(record)
        row = [
            str(index),
            GLYPH.get(decision.outcome, "  "),
            decision.surface if not placement else placement.name,
            landed,
            cut or "",
            f"{decision.confidence:.2f}",
            f"*{len(fixes)}" if fixes else "",
        ]
        if replay.reviews:
            review = replay.review_for(record)
            row.append(f"{review.verdict}  {review.note}".strip() if review else "")
        style = "dim" if not replay.replayed[index - 1] else None
        table.add_row(*row, style=style)
    return table


def fixes_lines(replay: Replay) -> "list[str]":
    lines: "list[str]" = []
    for index, record in enumerate(replay.records, start=1):
        fixes = _structural(record)
        if not fixes:
            continue
        name = (
            record.result.placement.name
            if record.result.placement
            else record.decision.surface
        )
        for fix in fixes:
            action = next(a for a in record.decision.actions if fix.startswith(a.op))
            lines.append(f"#{index} {name}: {fix}")
            lines.append(
                f"      because: {action.justification}  [{action.confidence:.2f}]"
            )
    return lines or ["(none)"]


def tree_diff(replay: Replay) -> Tree:
    """The touched part of the after-tree, with untouched ancestors for context."""
    after, base, diff = replay.after, replay.base, replay.diff
    created, modified = set(diff.created), set(diff.modified)
    touched = created | modified
    keep: "set[str]" = set()
    for node_id in touched:
        keep.update(after.ancestry(node_id))

    root = Tree(
        f"[bold]{after.doc.meta.dimension}[/] after replay  (+{len(created)} ~{len(modified)} -{len(diff.deleted)})"
    )

    def label(node_id: str) -> str:
        name = after.name(node_id)
        if node_id in created:
            return f"[green]+ {name}[/]  [dim]{node_id}[/]"
        if node_id in modified:
            old = replay.before_names.get(node_id, "")
            renamed = f"  [dim](was: {old})[/]" if old and old != name else ""
            return f"[yellow]~ {name}[/]{renamed}  [dim]{node_id}[/]"
        return f"[dim]{name}[/]"

    def walk(node_id: str, branch: Tree) -> None:
        for child in after.children(node_id):
            if child in keep:
                walk(child, branch.add(label(child)))

    for root_id in after.doc.roots:
        if root_id in keep:
            walk(root_id, root.add(label(root_id)))
    for node_id in diff.deleted:
        parent = base.parents(node_id)
        where = f" (was under {base.name(parent[0])})" if parent else ""
        root.add(f"[red]- {base.name(node_id)}[/]  [dim]{node_id}{where}[/]")
    if not touched and not diff.deleted:
        root.add("[dim](no structural change)[/]")
    return root


def cut_table(replay: Replay) -> Table:
    """Where this run's names landed at the cut, and node counts before/after."""

    def count_nodes(onto: Ontology) -> "dict[str, int]":
        counts: "dict[str, int]" = {}
        for node_id in onto.nodes:
            key = to_placement(onto, node_id, replay.cut).cut_category or "(ignore)"
            counts[key] = counts.get(key, 0) + 1
        return counts

    before, after = count_nodes(replay.base), count_nodes(replay.after)
    landed: "dict[str, int]" = {}
    for record in replay.records:
        placement = record.result.placement
        if placement is None:
            continue
        key = placement.cut_category or "(ignore)"
        landed[key] = landed.get(key, 0) + 1

    table = Table(title="at the cut", title_justify="left", pad_edge=False)
    table.add_column("category")
    table.add_column("this run", justify="right")
    table.add_column("nodes before", justify="right")
    table.add_column("nodes after", justify="right")
    table.add_column("delta", justify="right")
    keys = sorted(
        set(before) | set(after) | set(landed), key=lambda k: (-landed.get(k, 0), k)
    )
    for key in keys:
        delta = after.get(key, 0) - before.get(key, 0)
        table.add_row(
            key,
            str(landed.get(key, 0)) if landed.get(key) else "",
            str(before.get(key, 0)),
            str(after.get(key, 0)),
            f"{delta:+d}" if delta else "",
        )
    return table


def render(replay: Replay, *, width: "int | None" = None) -> str:
    console = Console(
        file=io.StringIO(), width=width, force_terminal=False, highlight=False
    )
    for line in header(replay):
        console.print(line)
    console.print()
    console.print(decisions_table(replay))
    console.print()
    console.print("[bold]structural fixes[/]  (edits beyond the decision's own name)")
    for line in fixes_lines(replay):
        console.print("  " + line, highlight=False)
    console.print()
    console.print(tree_diff(replay))
    console.print()
    console.print(cut_table(replay))
    if replay.diff.surfaces_added:
        console.print()
        console.print(
            f"[bold]surfaces[/]  +{len(replay.diff.surfaces_added)} "
            f"-{len(replay.diff.surfaces_removed)}"
        )
    return console.file.getvalue()  # type: ignore[attr-defined]


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Show what a categorize run did, from its decisions.jsonl.",
    )
    parser.add_argument("decisions", help="decisions.jsonl from a categorize run")
    parser.add_argument(
        "--review", default=None, help="review.jsonl from --interactive"
    )
    parser.add_argument("--dim", default=None, help="default: from the records")
    parser.add_argument(
        "--base",
        default=None,
        help="the version the decisions were taken AGAINST -- the tree before the "
        "run, which the records already name. Not the version the run wrote: "
        "replaying onto that fails with 'already exists' / 'unknown node'.",
    )
    parser.add_argument("--root", default=None, help="ontology root (default: config)")
    parser.add_argument("--width", type=int, default=None)
    return parser


def main(argv: "Sequence[str] | None" = None) -> int:
    args = build_parser().parse_args(argv)
    records = list(read_decisions(args.decisions))
    if not records:
        print("no decisions", file=sys.stderr)
        return 1
    first = records[0].provenance
    dimension = args.dim or first.dimension
    base_version = args.base or first.base_version
    if args.base and args.base != first.base_version:
        print(
            f"warning: --base {args.base} but the records were taken against "
            f"{first.base_version}; expect 'already exists' / 'unknown node' on "
            "replay",
            file=sys.stderr,
        )
    root = Path(args.root) if args.root else ontology_root()
    base = Ontology.load(root / dimension / base_version)
    cut = load_dimension_cut(dimension)
    reviews: "list[Review]" = []
    review_path = (
        Path(args.review)
        if args.review
        else Path(args.decisions).with_name("review.jsonl")
    )
    if review_path.exists():
        reviews = read_reviews(review_path)
    replay = Replay(base, records, cut=cut, reviews=reviews)
    Console(width=args.width, highlight=False).print(
        render(replay, width=args.width), end="", markup=False
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
