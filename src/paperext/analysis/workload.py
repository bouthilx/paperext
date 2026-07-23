"""Workload-characterization view (WS-E E1c, #25).

The view most relevant to picking real GPU workloads: the same per-paper
frequency as E1b (:mod:`paperext.analysis.frequency`), but each dimension is
*split* by an execution attribute —

- **models** by ``is_executed`` (executed in-paper vs merely referenced) and by
  ``execution_mode`` (train / finetune / inference / unknown);
- **datasets / libraries** by ``role`` (contributed / used / referenced).

Counting is non-exclusive per ``(category, split-value)`` cell, exactly as in
E1b: a paper is counted once toward every distinct cell it has an item in. Each
item carries a single split value, so summing a category's cells can exceed that
category's paper count (a paper with two same-category items of different split
values lands in two cells). The **union** over split values reconciles cell-by-cell
with the E1b headline: ``category_counts`` here equals E1b's ``category_counts``.

Roll-up cut, ``Other``-policy and the ``ignore`` drop are inherited from E1b; the
``Other``-policy adjusts only the ``Other`` rows of the category matrix (name-level
counts are never policy-adjusted), matching E1b.
"""

import argparse
import csv
import enum
import logging
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Optional

from paperext.analysis.frequency import (
    Dimension,
    _entity_names,
    _parse_cut,
    _resolve,
    build_maps,
    group_files_by_paper,
    iter_paper_files,
    load_extractions,
)
from paperext.analysis.rollup import OTHER, load_cut

logger = logging.getLogger(__name__)


def _enum_str(x) -> str:
    """String label for an enum member or a plain value."""
    if isinstance(x, enum.Enum):
        return str(x.value)
    return str(x)


# --------------------------------------------------------------------------- #
# Split specifications
# --------------------------------------------------------------------------- #


@dataclass
class Split:
    """How to split a dimension: a label, an extractor, and the column order."""

    name: str
    fn: Callable[[object], str]
    values: "tuple[str, ...]"


def _split_is_executed(entry) -> str:
    return "executed" if entry.is_executed.value else "referenced"


def _split_execution_mode(entry) -> str:
    return _enum_str(entry.execution_mode.value)


def _split_role(entry) -> str:
    return _enum_str(entry.role)


IS_EXECUTED = Split("is_executed", _split_is_executed, ("executed", "referenced"))
EXECUTION_MODE = Split(
    "execution_mode",
    _split_execution_mode,
    ("train", "finetune", "inference", "unknown"),
)
ROLE = Split("role", _split_role, ("contributed", "used", "referenced"))


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


@dataclass
class SplitResult:
    key: str
    split_name: str
    split_values: "tuple[str, ...]"
    n_papers: int
    n_papers_with_dim: int
    #: (category, split_value) -> paper count
    category_split_counts: "dict[tuple, int]"
    #: category -> paper count (union over splits; reconciles with E1b)
    category_counts: "dict[str, int]"
    #: (name_key, split_value) -> paper count
    name_split_counts: "dict[tuple, int]"
    name_counts: "dict[str, int]"
    name_display: "dict[str, str]"
    name_category: "dict[str, str]"
    unmapped_names: set = field(default_factory=set)

    def _columns(self) -> "list[str]":
        """Split values in declared order, plus any extras actually seen."""
        seen = {sv for _, sv in self.category_split_counts}
        extras = sorted(seen - set(self.split_values))
        return [*self.split_values, *extras]

    def category_matrix(self) -> "tuple[list[str], list[tuple]]":
        cols = self._columns()
        header = ["category", *cols, "total"]
        rows = []
        for cat, total in self.category_counts.items():
            cells = [self.category_split_counts.get((cat, sv), 0) for sv in cols]
            rows.append((cat, *cells, total))
        rows.sort(key=lambda r: (-r[-1], r[0]))
        return header, rows

    def name_matrix(self) -> "tuple[list[str], list[tuple]]":
        cols = self._columns()
        header = ["name", "category_at_cut", *cols, "total", "mapped"]
        rows = []
        for nk, total in self.name_counts.items():
            cells = [self.name_split_counts.get((nk, sv), 0) for sv in cols]
            rows.append(
                (
                    self.name_display.get(nk, nk),
                    self.name_category.get(nk, OTHER),
                    *cells,
                    total,
                    nk not in self.unmapped_names,
                )
            )
        rows.sort(key=lambda r: (-r[-2], r[0]))
        return header, rows


def _paper_items_split(extractions, dim: Dimension, split: Split):
    """Resolved items for one paper with their split value attached.

    ``(name_key, display, category, mapped, split_value)``; ``ignore`` items dropped.
    """
    entries = getattr(extractions, dim.key)
    items = []
    for entry in entries:
        primary, aliases, raw = _entity_names(entry)
        if not primary:
            continue
        resolved = _resolve(primary, aliases, raw, dim)
        if resolved is None:
            continue
        name_key, display, category, mapped = resolved
        items.append((name_key, display, category, mapped, split.fn(entry)))
    return items


def aggregate_split(
    papers: Iterable[object],
    dim: Dimension,
    split: Split,
    other_policy: str = "inclusive",
) -> SplitResult:
    """Per-paper frequency for one dimension, split by *split*.

    Non-exclusive per ``(category, split_value)`` cell. ``category_counts`` is the
    union over splits and equals the E1b headline for the same dim/cut/policy.
    """
    if other_policy not in ("inclusive", "residual"):
        raise ValueError(
            f"other_policy must be inclusive|residual, got {other_policy!r}"
        )

    n_papers = 0
    n_papers_with_dim = 0
    cat_split: "Counter[tuple]" = Counter()
    cat_counts: "Counter[str]" = Counter()
    name_split: "Counter[tuple]" = Counter()
    name_counts: "Counter[str]" = Counter()
    name_display: "dict[str, str]" = {}
    name_category: "dict[str, str]" = {}
    unmapped: set = set()

    for extractions in papers:
        n_papers += 1
        items = _paper_items_split(extractions, dim, split)
        if items:
            n_papers_with_dim += 1

        paper_cat_split: set = set()
        paper_name_split: set = set()
        paper_cats: set = set()
        paper_names: set = set()
        for name_key, display, category, mapped, sval in items:
            paper_cat_split.add((category, sval))
            paper_name_split.add((name_key, sval))
            paper_cats.add(category)
            paper_names.add(name_key)
            name_display.setdefault(name_key, display)
            name_category[name_key] = category
            if not mapped:
                unmapped.add(name_key)

        # Other-policy: under residual, a paper contributes to Other only if it has
        # no selected (non-Other) bucket. Applies to category cells + totals only.
        has_selected = bool(paper_cats - {OTHER})
        drop_other = other_policy == "residual" and has_selected

        for cat, sval in paper_cat_split:
            if cat == OTHER and drop_other:
                continue
            cat_split[(cat, sval)] += 1
        for cat in paper_cats:
            if cat == OTHER and drop_other:
                continue
            cat_counts[cat] += 1
        for ns in paper_name_split:
            name_split[ns] += 1
        for nk in paper_names:
            name_counts[nk] += 1

    return SplitResult(
        key=dim.key,
        split_name=split.name,
        split_values=split.values,
        n_papers=n_papers,
        n_papers_with_dim=n_papers_with_dim,
        category_split_counts=dict(cat_split),
        category_counts=dict(cat_counts),
        name_split_counts=dict(name_split),
        name_counts=dict(name_counts),
        name_display=name_display,
        name_category=name_category,
        unmapped_names=unmapped,
    )


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #


def _write_csv(path: Path, header: "list[str]", rows: "list[tuple]") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in rows:
            w.writerow(row)


def _md_table(header, rows, limit=None) -> str:
    shown = rows[:limit] if limit else rows
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in shown:
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    if limit and len(rows) > limit:
        lines.append(f"| _… {len(rows) - limit} more_ |" + " |" * (len(header) - 1))
    return "\n".join(lines)


def write_reports(
    results: "list[SplitResult]",
    out_dir: Path,
    other_policy: str,
    top_n: int = 30,
) -> "list[Path]":
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: "list[Path]" = []
    md = [f"# Workload characterization ({other_policy} Other-policy)\n"]

    for res in results:
        tag = f"{res.key}_{res.split_name}"
        cat_header, cat_rows = res.category_matrix()
        name_header, name_rows = res.name_matrix()

        cat_csv = out_dir / f"{tag}_categories.csv"
        name_csv = out_dir / f"{tag}_names.csv"
        _write_csv(cat_csv, cat_header, cat_rows)
        _write_csv(name_csv, name_header, name_rows)
        written += [cat_csv, name_csv]

        md.append(f"## {res.key} × {res.split_name}")
        md.append(
            f"{res.n_papers} papers ({res.n_papers_with_dim} with ≥1 {res.key}); "
            f"{len(cat_rows)} categories.\n"
        )
        md.append("### Categories\n" + _md_table(cat_header, cat_rows, top_n) + "\n")
        md.append("### Names\n" + _md_table(name_header, name_rows, top_n) + "\n")

    summary = out_dir / "workload_summary.md"
    summary.write_text("\n".join(md))
    written.append(summary)
    return written


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _workload_dimensions(models_cut):
    """models (tree + cut) + datasets/libraries (by name), with their splits."""
    from paperext.config import CFG

    data = CFG.dir.data
    if models_cut is None:
        milabench = CFG.dir.evaluation_mod_cat / CFG.evaluation.mod_cat
        models_cut = load_cut(milabench) if milabench.exists() else 2

    models = build_maps(
        Dimension("models", data / "categorized_models.json", models_cut)
    )
    datasets = build_maps(Dimension("datasets"))
    libraries = build_maps(Dimension("libraries"))
    return [
        (models, IS_EXECUTED),
        (models, EXECUTION_MODE),
        (datasets, ROLE),
        (libraries, ROLE),
    ]


def main(argv: Optional["list[str]"] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Workload-characterization view over stored extractions."
    )
    parser.add_argument("--platform", default=None, help="openai | vertexai")
    parser.add_argument("--model", default=None, help="restrict to one model subdir")
    parser.add_argument(
        "--cut",
        type=_parse_cut,
        default=None,
        help="models cut: 'depth=N' or 'nodes=<file>' (default: milabench nodes)",
    )
    parser.add_argument(
        "--other", choices=("inclusive", "residual"), default="inclusive"
    )
    parser.add_argument("--out", default=None, help="output directory")
    parser.add_argument("--top-n", type=int, default=30)
    args = parser.parse_args(argv)

    from paperext.config import CFG

    platform = args.platform or CFG.platform.select
    out_dir = (
        Path(args.out)
        if args.out
        else CFG.dir.queries.parent / "analysis" / platform / "workload"
    )

    dims = _workload_dimensions(args.cut)

    files = iter_paper_files(platform, model=args.model)
    groups = group_files_by_paper(files)
    logger.info(
        "Loading %d papers (%d files) for %s", len(groups), len(files), platform
    )

    papers = []
    for _pid, paper_files in groups.items():
        merged = None
        for f in paper_files:
            ext = load_extractions(f)
            if merged is None:
                merged = ext
            else:
                merged.models.extend(ext.models)
                merged.datasets.extend(ext.datasets)
                merged.libraries.extend(ext.libraries)
        papers.append(merged)

    results = [
        aggregate_split(papers, dim, split, other_policy=args.other)
        for dim, split in dims
    ]
    written = write_reports(results, out_dir, args.other, top_n=args.top_n)
    for p in written:
        logger.info("wrote %s", p)
    print(f"Wrote {len(written)} files to {out_dir}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
