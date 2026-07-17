"""Per-paper frequency analysis (WS-E E1b, #24).

Turns the stored extraction corpus into per-paper frequency tables for each
dimension (models / datasets / libraries / research fields), on top of the
category roll-up engine from E1a (:mod:`paperext.analysis.rollup`).

The counting is **non-exclusive per bucket**: a paper is counted once toward
*every* distinct category it has at least one item in, so the per-column counts
overlap and their sum can exceed the number of papers. This is the right shape
for "what fraction of papers use a Transformer / a CNN / ...".

Two reporting levels per dimension (locked in #16):

- **category-at-cut** — the coarse bucket picked by the roll-up cut; aliases and
  fine-grained names fold together here.
- **name** — the extracted name (normalized), with its raw display form recovered
  from the tree. Deliberately *not* alias-folded: the residual name spread is the
  fragmentation signal that feeds D1 (#15). Full alias→canonical folding needs the
  tree to mark entity boundaries, which is D1 content work.

**Other-policy** (``--other``):

- ``inclusive`` (default) — a paper is counted in ``Other`` if it has *any* item
  that matches no selected bucket, *even if* it also matches a selected one. Best
  for ranking ("how many papers touch anything outside the taxonomy").
- ``residual`` — a paper is counted in ``Other`` *only* if none of its items fall
  in a selected bucket, making ``Other`` a true partition complement. Best for
  coverage/partition views. Non-``Other`` counts are identical under both policies.

The explicit ``ignore`` branch of a tree (genuine misextractions) is dropped
outright — such items are counted nowhere, exactly as in the existing pipeline.

Loader notes: the corpus is read straight from ``queries/<platform>/`` with a
**recursive** glob, so it works with today's flat layout *and* the model-scoped
layout from A7 (#27) with no change. Legacy v1–v3 extractions are up-converted to
v4 in memory via the A6 converter chain; the committed files are never rewritten.
Papers with several query files (retries) are unioned into one per-paper item set.
"""

import argparse
import csv
import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional, Union

from paperext.analysis.rollup import (
    OTHER,
    build_category_map,
    load_cut,
    str_normalize,
)

logger = logging.getLogger(__name__)

#: Depth large enough that a depth cut resolves every node to itself, giving an
#: identity ``normalized_name -> raw_name`` map (used to recover display names).
_LEAF_DEPTH = 10_000

#: Dimensions and the extraction attributes they read.
_MODEL_DIMS = ("models", "datasets", "libraries")


# --------------------------------------------------------------------------- #
# Dimension configuration
# --------------------------------------------------------------------------- #


@dataclass
class Dimension:
    """One reporting dimension.

    ``tree_path``/``cut`` are optional: a dimension with no tree is reported by
    normalized name (each name is its own category), matching the "by name until
    D1" plan for datasets/libraries.
    """

    key: str
    tree_path: Optional[Path] = None
    cut: Union[int, "set[str]", None] = None
    drop_roots: tuple = ("ignore",)

    # Populated by build_maps().
    category_map: Optional[dict] = field(default=None, repr=False)
    display_map: dict = field(default_factory=dict, repr=False)
    ignore_names: "set[str]" = field(default_factory=set, repr=False)

    @property
    def has_tree(self) -> bool:
        return self.category_map is not None


def _iter_tree_names(tree: dict, prefix: tuple = ()):
    """Yield ``(top_level_norm, leaf_norm)`` for every node of a category tree."""
    for raw_name, sub in tree.items():
        norm = str_normalize(raw_name)
        path = prefix + (norm,)
        yield path[0], norm
        if sub:
            yield from _iter_tree_names(sub, path)


def build_maps(dim: Dimension) -> Dimension:
    """Populate ``category_map`` / ``display_map`` / ``ignore_names`` for *dim*."""
    if dim.tree_path is None:
        dim.category_map = None
        dim.display_map = {}
        dim.ignore_names = set()
        return dim

    cut = dim.cut if dim.cut is not None else 1
    dim.category_map = build_category_map(dim.tree_path, cut, drop_roots=dim.drop_roots)
    # A leaf-depth roll-up maps every normalized name back to its raw display name.
    dim.display_map = build_category_map(
        dim.tree_path, _LEAF_DEPTH, drop_roots=dim.drop_roots
    )

    drop = {str_normalize(r) for r in dim.drop_roots}
    tree = json.loads(Path(dim.tree_path).read_text())
    dim.ignore_names = {
        leaf for top, leaf in _iter_tree_names(tree) if top in drop and leaf
    }
    return dim


# --------------------------------------------------------------------------- #
# Loading extractions
# --------------------------------------------------------------------------- #


def iter_paper_files(
    platform: str,
    model: Optional[str] = None,
    queries_dir: Optional[Path] = None,
) -> "list[Path]":
    """All extraction JSON files for a platform, recursively.

    Works with the flat ``queries/<platform>/*.json`` layout and the model-scoped
    ``queries/<platform>/<model>/*.json`` layout (A7); pass *model* to restrict to
    one model subdirectory.
    """
    if queries_dir is None:
        from paperext.config import CFG

        queries_dir = CFG.dir.queries
    base = Path(queries_dir) / platform
    if model:
        base = base / model
    return sorted(base.glob("**/*.json"))


def load_extractions(path: Union[str, Path]):
    """Load a stored extraction file and return v4 ``PaperExtractions``.

    Detects the schema version and up-converts legacy v1–v3 through the A6 chain.
    """
    from paperext.structured_output.mdl import model as dest_model
    from paperext.structured_output.mdl.convert import (
        CONVERT_CHAIN,
        CONVERT_MODEL,
        _detect_version,
    )

    data = json.loads(Path(path).read_text())
    module, _response, extractions = _detect_version(data)
    if module is None:
        raise ValueError(f"Could not validate {path} against any model version")

    if module is not dest_model:
        for src_model in CONVERT_CHAIN[CONVERT_CHAIN.index(module) :]:
            extractions = CONVERT_MODEL[src_model](extractions)
    return extractions


def _paper_id(path: Path) -> str:
    """Paper id shared by a paper's query files (strip the ``_NN`` query index)."""
    stem = path.stem
    head, sep, tail = stem.rpartition("_")
    if sep and tail.isdigit():
        return head
    return stem


def group_files_by_paper(files: Iterable[Path]) -> "dict[str, list[Path]]":
    """Group query files by paper id, preserving order."""
    groups: "dict[str, list[Path]]" = {}
    for f in files:
        groups.setdefault(_paper_id(f), []).append(f)
    return groups


# --------------------------------------------------------------------------- #
# Per-paper item resolution
# --------------------------------------------------------------------------- #


def _entity_names(entry) -> "tuple[str, list[str], str]":
    """Return ``(primary_norm, alias_norms, raw_display)`` for a reference/field."""
    raw = entry.name.value
    aliases = [str_normalize(a) for a in getattr(entry, "aliases", []) if a]
    return str_normalize(raw), aliases, raw


def _resolve(primary: str, aliases: "list[str]", raw: str, dim: Dimension):
    """Resolve one extracted item to ``(name_key, display, category, mapped)``.

    Returns ``None`` when the item is in the tree's ``ignore`` branch (dropped).
    """
    if not dim.has_tree:
        # No taxonomy: each name is its own category (reported by name).
        return primary, raw, raw, True

    for candidate in (primary, *aliases):
        if candidate in dim.category_map:
            return (
                candidate,
                dim.display_map.get(candidate, raw),
                dim.category_map[candidate],
                True,
            )
    # No candidate matched a kept node. If any is a known misextraction, drop it.
    if primary in dim.ignore_names or any(a in dim.ignore_names for a in aliases):
        return None
    # Genuinely unknown name: keep it, bucket it as Other, flag as unmapped.
    return primary, raw, OTHER, False


def _paper_items(extractions, dim: Dimension):
    """Every resolved item in one paper for *dim* (before within-paper dedup)."""
    key = dim.key
    if key == "research_fields":
        fields = [extractions.primary_research_field, *extractions.sub_research_fields]
        entries = fields
    else:
        entries = getattr(extractions, key)

    items = []
    for entry in entries:
        primary, aliases, raw = _entity_names(entry)
        if not primary:
            continue
        resolved = _resolve(primary, aliases, raw, dim)
        if resolved is not None:
            items.append(resolved)
    return items


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


@dataclass
class DimensionResult:
    key: str
    n_papers: int
    n_papers_with_dim: int
    category_counts: "dict[str, int]"
    name_counts: "dict[str, int]"
    name_display: "dict[str, str]"
    name_category: "dict[str, str]"
    unmapped_names: "set[str]"

    def category_rows(self) -> "list[tuple]":
        rows = [
            (cat, cnt, cnt / self.n_papers if self.n_papers else 0.0)
            for cat, cnt in self.category_counts.items()
        ]
        rows.sort(key=lambda r: (-r[1], r[0]))
        return rows

    def name_rows(self) -> "list[tuple]":
        rows = [
            (
                self.name_display.get(nk, nk),
                nk,
                self.name_category.get(nk, OTHER),
                cnt,
                cnt / self.n_papers if self.n_papers else 0.0,
                nk not in self.unmapped_names,
            )
            for nk, cnt in self.name_counts.items()
        ]
        rows.sort(key=lambda r: (-r[3], r[0]))
        return rows


def aggregate(
    papers: "Iterable[object]",
    dim: Dimension,
    other_policy: str = "inclusive",
) -> DimensionResult:
    """Count per-paper frequencies for one dimension.

    *papers* is an iterable of v4 ``PaperExtractions``. Counting is non-exclusive:
    a paper contributes once to each distinct category / name it contains.
    """
    if other_policy not in ("inclusive", "residual"):
        raise ValueError(
            f"other_policy must be inclusive|residual, got {other_policy!r}"
        )

    n_papers = 0
    n_papers_with_dim = 0
    cat_counts: "Counter[str]" = Counter()
    name_counts: "Counter[str]" = Counter()
    residual_other = 0
    name_display: "dict[str, str]" = {}
    name_category: "dict[str, str]" = {}
    unmapped: "set[str]" = set()

    for extractions in papers:
        n_papers += 1
        items = _paper_items(extractions, dim)
        if items:
            n_papers_with_dim += 1

        paper_names: "set[str]" = set()
        paper_cats: "set[str]" = set()
        for name_key, display, category, mapped in items:
            paper_names.add(name_key)
            paper_cats.add(category)
            name_display.setdefault(name_key, display)
            name_category[name_key] = category
            if not mapped:
                unmapped.add(name_key)

        for nk in paper_names:
            name_counts[nk] += 1
        for c in paper_cats:
            cat_counts[c] += 1  # inclusive counts (Other included)

        # A paper is residual-Other iff it has items but none in a selected bucket.
        if paper_cats and not (paper_cats - {OTHER}):
            residual_other += 1

    category_counts = dict(cat_counts)
    if other_policy == "residual" and OTHER in category_counts:
        if residual_other:
            category_counts[OTHER] = residual_other
        else:
            del category_counts[OTHER]

    return DimensionResult(
        key=dim.key,
        n_papers=n_papers,
        n_papers_with_dim=n_papers_with_dim,
        category_counts=category_counts,
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


def _md_table(
    header: "list[str]", rows: "list[tuple]", limit: Optional[int] = None
) -> str:
    shown = rows[:limit] if limit else rows

    def fmt(v):
        if isinstance(v, float):
            return f"{v:.3f}"
        return str(v)

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in shown:
        lines.append("| " + " | ".join(fmt(v) for v in row) + " |")
    if limit and len(rows) > limit:
        lines.append(f"| _… {len(rows) - limit} more_ |" + " |" * (len(header) - 1))
    return "\n".join(lines)


def write_reports(
    results: "list[DimensionResult]",
    out_dir: Path,
    other_policy: str,
    top_n: int = 30,
) -> "list[Path]":
    """Write per-dimension CSVs + a combined markdown summary. Returns paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: "list[Path]" = []

    cat_header = ["category", "count", "global_prop"]
    name_header = [
        "name",
        "name_norm",
        "category_at_cut",
        "count",
        "global_prop",
        "mapped",
    ]

    md = [f"# Per-paper frequency ({other_policy} Other-policy)\n"]

    for res in results:
        cat_rows = res.category_rows()
        name_rows = res.name_rows()

        cat_csv = out_dir / f"{res.key}_categories.csv"
        name_csv = out_dir / f"{res.key}_names.csv"
        _write_csv(cat_csv, cat_header, cat_rows)
        _write_csv(name_csv, name_header, name_rows)
        written += [cat_csv, name_csv]

        md.append(f"## {res.key}")
        md.append(
            f"{res.n_papers} papers ({res.n_papers_with_dim} with ≥1 {res.key}); "
            f"{len(cat_rows)} categories, {len(name_rows)} distinct names, "
            f"{len(res.unmapped_names)} unmapped.\n"
        )
        md.append(
            "### Categories\n" + _md_table(cat_header, cat_rows, limit=top_n) + "\n"
        )
        md.append("### Names\n" + _md_table(name_header, name_rows, limit=top_n) + "\n")

        # Fragmentation: unmapped names + high-diversity categories → feeds D1.
        unmapped_rows = [r for r in name_rows if not r[5]]
        if unmapped_rows:
            md.append(
                "### Fragmentation — unmapped names (→ D1)\n"
                + _md_table(name_header, unmapped_rows, limit=top_n)
                + "\n"
            )
        diversity = Counter(r[2] for r in name_rows)
        div_rows = sorted(diversity.items(), key=lambda kv: (-kv[1], kv[0]))
        md.append(
            "### Fragmentation — distinct names per category\n"
            + _md_table(["category", "n_distinct_names"], div_rows, limit=top_n)
            + "\n"
        )

    summary = out_dir / "frequency_summary.md"
    summary.write_text("\n".join(md))
    written.append(summary)
    return written


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _parse_cut(spec: Optional[str]):
    """Parse a ``--cut`` value: ``depth=N`` -> int, ``nodes=<file>`` -> cut set."""
    if spec is None:
        return None
    kind, sep, val = spec.partition("=")
    if not sep:
        raise argparse.ArgumentTypeError("cut must be 'depth=N' or 'nodes=<file>'")
    if kind == "depth":
        return int(val)
    if kind == "nodes":
        return load_cut(val)
    raise argparse.ArgumentTypeError(f"unknown cut kind {kind!r}")


def _default_dimensions(models_cut, domains_cut) -> "list[Dimension]":
    """Dimensions with sensible defaults from the config data directory."""
    from paperext.config import CFG

    data = CFG.dir.data
    eval_mod = CFG.dir.evaluation_mod_cat
    eval_dom = CFG.dir.evaluation_dom_cat

    if models_cut is None:
        milabench = eval_mod / CFG.evaluation.mod_cat
        models_cut = load_cut(milabench) if milabench.exists() else 2
    if domains_cut is None:
        milabench_dom = eval_dom / CFG.evaluation.dom_cat
        domains_cut = load_cut(milabench_dom) if milabench_dom.exists() else 2

    dims = [
        Dimension("models", data / "categorized_models.json", models_cut),
        Dimension("research_fields", data / "categorized_domains.json", domains_cut),
        # Datasets/libraries: reported by name until D1 wires their taxonomy.
        Dimension("datasets"),
        Dimension("libraries"),
    ]
    return [build_maps(d) for d in dims]


def main(argv: Optional["list[str]"] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Per-paper frequency analysis over stored extractions."
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
        "--domains-cut",
        type=_parse_cut,
        default=None,
        help="research-fields cut (default: milabench nodes)",
    )
    parser.add_argument(
        "--other",
        choices=("inclusive", "residual"),
        default="inclusive",
    )
    parser.add_argument("--out", default=None, help="output directory")
    parser.add_argument("--top-n", type=int, default=30)
    args = parser.parse_args(argv)

    from paperext.config import CFG

    platform = args.platform or CFG.platform.select
    out_dir = (
        Path(args.out) if args.out else CFG.dir.queries.parent / "analysis" / platform
    )

    dims = _default_dimensions(args.cut, args.domains_cut)

    files = iter_paper_files(platform, model=args.model)
    groups = group_files_by_paper(files)
    logger.info(
        "Loading %d papers (%d files) for %s", len(groups), len(files), platform
    )

    # One merged v4 extraction list per paper (queries unioned at item level below;
    # here we just pass every query file's extractions and dedup within paper via
    # the paper grouping — retries add items, within-paper set dedup handles overlap).
    papers = []
    for pid, paper_files in groups.items():
        merged = None
        for f in paper_files:
            ext = load_extractions(f)
            if merged is None:
                merged = ext
            else:
                merged.models.extend(ext.models)
                merged.datasets.extend(ext.datasets)
                merged.libraries.extend(ext.libraries)
                merged.sub_research_fields.extend(ext.sub_research_fields)
        papers.append(merged)

    results = [aggregate(papers, dim, other_policy=args.other) for dim in dims]
    written = write_reports(results, out_dir, args.other, top_n=args.top_n)
    for p in written:
        logger.info("wrote %s", p)
    print(f"Wrote {len(written)} files to {out_dir}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
