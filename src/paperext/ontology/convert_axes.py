"""Convert the derived axis tables into loadable snapshots (D1h, #100).

The three dimensions were each derived as TSV node tables under
``data/ontology/design/axes*/``. They are the authored source and stay that way:
a TSV is what a person reviews in a diff. This module reads them and writes the
format the loader speaks — one :class:`~paperext.ontology.schema.OntologyDoc` per
axis plus a ``dimension.json`` manifest, under ``data/ontology/<dim>/<version>/``.

**One converter, three dimensions.** The tables do not share a column spelling,
and the differences are real rather than accidental, so each dimension declares
them in a :class:`TableSpec` and the reading code is written once. Writing it per
dimension is what would let the three drift.

Spellings that differ, and must not be guessed at:

====================  ==================  =========================
                      parent column       separator
====================  ==================  =========================
domains (5 axes)      ``parent_id``       single parent
models facet axes     ``parent_id``       single parent
models lineage        ``parents``         ``|``
algorithms (all)      ``parents``         ``;`` or ``,``
====================  ==================  =========================

Getting one of those wrong fails loudly rather than silently: a parent id that
does not resolve is a dangling edge, which the audit reports.

Run it with::

    uv run python -m paperext.ontology.convert_axes --write
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

from paperext.ontology.ontology import Ontology
from paperext.ontology.schema import (
    AxisSpec,
    DimensionDoc,
    Meta,
    Node,
    NormRow,
    OntologyDoc,
)

#: Where the authored tables live, relative to the repository root.
DESIGN_ROOT = Path("data/ontology/design")
#: Where snapshots are written.
SNAPSHOT_ROOT = Path("data/ontology")
#: The version these conversions produce. ``v0`` is the faithful import of the
#: *legacy* trees and is the sealed eval reference (#95); it is never overwritten.
VERSION = "v1"

#: Columns that are structure, not description, and therefore never land in
#: ``Node.props``.
_STRUCTURAL = frozenset(
    {"node_id", "name", "parent_id", "parents", "value_parent", "kind", "expands_to"}
)

_SPLIT_SEMI_COMMA = re.compile(r"[;,]")


def split_top(s: str, sep: str = ";") -> "list[str]":
    """Split on *sep*, but only outside parentheses.

    A ``(sources, forms)`` pair contains the comma that would otherwise be a
    separator, so the pair structure has to be respected while splitting.
    """
    out: "list[str]" = []
    depth = 0
    cur = ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]


@dataclass(frozen=True)
class TableSpec:
    """How one dimension's tables are spelled."""

    #: Directory under :data:`DESIGN_ROOT` holding ``<axis>/nodes.tsv``.
    design_dir: str
    #: Axes, in the order they should appear in the manifest.
    axes: "tuple[AxisSpec, ...]"
    #: Which axis carries the pins; empty for a dimension that is only axes.
    backbone: str = ""
    #: Parent column name and the separator inside it, per axis. The backbone and
    #: the facet axes of one dimension genuinely differ, so this is keyed by axis
    #: with a default.
    parent_column: str = "parent_id"
    parent_sep: str = ""
    backbone_parent_column: str = "parents"
    backbone_parent_sep: str = "|"
    #: ``<axis>/SPELLINGS.tsv``, when the axis has one: the surface column name.
    #: Ancestor traversal order for the backbone; see ``DimensionDoc``.
    chain_order: str = "breadth-first"
    #: Separator between pins *inside* one backbone cell. Models writes ``a|b``,
    #: algorithms ``a; b`` or ``a, b``. A pair axis is always split on ``;``
    #: outside parentheses, whatever this says, so the pair survives as one item.
    pin_sep: str = "|"
    #: ``<axis>/SPELLINGS.tsv``, when the axis has one: the surface column name.
    spellings_surface: "dict[str, str]" = field(default_factory=dict)


SPECS: "dict[str, TableSpec]" = {
    # Five independent axes and no backbone: a paper maps to a set of values on
    # each, so there is nothing for the axes to be pinned on.
    "domains": TableSpec(
        design_dir="axes",
        backbone="",
        axes=(
            AxisSpec(name="discipline", inherit="none"),
            AxisSpec(name="method", inherit="none"),
            AxisSpec(name="modality", inherit="none"),
            AxisSpec(name="sector", inherit="none"),
            AxisSpec(name="properties", inherit="none"),
        ),
    ),
    "models": TableSpec(
        design_dir="axes_models",
        backbone="lineage",
        chain_order="depth-first",
        axes=(
            AxisSpec(name="lineage", inherit="none"),
            # `deny="chain"` and `subsume=False` are the semantics this
            # dimension was built and audited under (#95). The algorithms work
            # later settled on nearest-statement-wins and on subsumption;
            # adopting them here would silently change resolved values, so the
            # difference is declared and measured rather than assumed away.
            AxisSpec(name="connectivity", inherit="union", deny="chain", subsume=False),
            AxisSpec(name="topology", inherit="nearest", deny="chain", subsume=False),
            AxisSpec(
                name="attributes",
                inherit="nearest-in-family",
                deny="chain",
                subsume=False,
                many_inherit="chain",
            ),
        ),
        backbone_parent_sep="|",
        pin_sep="|",
        spellings_surface={"lineage": "spelling"},
    ),
    "algorithms": TableSpec(
        design_dir="axes_algorithms",
        backbone="lineage",
        axes=(
            AxisSpec(name="lineage", inherit="none"),
            AxisSpec(
                name="signal",
                inherit="union",
                pairs=True,
                pair_prefixes=["S.src", "S.form"],
            ),
            AxisSpec(name="role", inherit="union"),
            # `many_inherit="chain"` matches `signal` and `role`, which also
            # union up the chain, and matches what `cardinality = many`
            # declares. It used to resolve as `nearest` because the design
            # script's branch for `many` had collapsed into its own fallback;
            # fixing it recovered 17 inherited values and exposed four ancestor
            # pins that claimed more than they should (#100).
            AxisSpec(
                name="attributes",
                inherit="nearest-in-family",
                require_scope=True,
                many_inherit="chain",
            ),
        ),
        # Every algorithms table, backbone and facet alike, uses `parents`.
        parent_column="parents",
        parent_sep=";,",
        backbone_parent_column="parents",
        backbone_parent_sep=";,",
        pin_sep=";,",
        spellings_surface={"lineage": "surface"},
    ),
    # Two independent axes and no backbone, the domains shape -- but for a
    # different reason. Domains has nothing to pin on because a paper maps to a
    # set of values on each axis. Here there *are* entities, and they were
    # deliberately given no lineage tree (#102 Part D): `access` is a property
    # of the mention and is carried by `runs[].data_sources[].access` in schema
    # v5, while `provenance` and `referent` are assigned to the entity post-hoc.
    # None of the three is inherited from anything, so all are flat value sets
    # -- `provenance` has one parent edge (`elicited` under `human-authored`)
    # and it is structural, not a pin.
    "data_sources": TableSpec(
        design_dir="axes_data_sources",
        backbone="",
        axes=(
            AxisSpec(name="access", inherit="none"),
            AxisSpec(name="provenance", inherit="none"),
            AxisSpec(name="referent", inherit="none"),
        ),
        parent_column="parents",
        parent_sep="|",
    ),
}


def read_table(path: Path) -> "list[dict[str, str]]":
    """Rows of a ``nodes.tsv``, with ``#`` comment lines stripped.

    Several tables open with a comment block stating the axis's dividing
    principle. It is documentation for a reader of the diff, so it is skipped
    here rather than parsed.
    """
    with path.open(encoding="utf-8", newline="") as fh:
        rows = csv.DictReader(
            (line for line in fh if not line.startswith("#")), delimiter="\t"
        )
        return [{k: (v or "") for k, v in row.items() if k} for row in rows]


def _parents_of(row: "dict[str, str]", column: str, sep: str) -> "list[str]":
    raw = (row.get(column) or "").strip()
    if not raw:
        return []
    if not sep:
        return [raw]
    if sep == ";,":
        return [p.strip() for p in _SPLIT_SEMI_COMMA.split(raw) if p.strip()]
    return [p.strip() for p in raw.split(sep) if p.strip()]


def split_pins(cell: str, sep: str, *, pairs: bool) -> "list[str]":
    """One entry per top-level pin in a backbone cell.

    A pair axis splits on ``;`` outside parentheses only, so
    ``(S.src.self, S.form.likelihood); !S.form.score`` stays two items and the
    comma inside the pair is not mistaken for a separator.
    """
    cell = (cell or "").strip()
    if not cell:
        return []
    if pairs:
        return split_top(cell)
    if sep == ";,":
        return [v.strip() for v in _SPLIT_SEMI_COMMA.split(cell) if v.strip()]
    return [v.strip() for v in cell.split(sep) if v.strip()]


def build_axis(
    rows: "Iterable[dict[str, str]]",
    *,
    dimension: str,
    axis: str,
    parent_column: str,
    parent_sep: str,
    pinned_axes: "Iterable[AxisSpec]" = (),
    pin_sep: str = "|",
    version: str = VERSION,
) -> OntologyDoc:
    """One axis's table -> an :class:`OntologyDoc`.

    Parent edges are written as the parent's ``children`` entry, which is how the
    document stores adjacency; a node with two parents appears under both, which
    the format already allows. Row order is preserved so the walk stays
    deterministic.
    """
    rows = list(rows)
    pinned = list(pinned_axes)
    pin_names = [spec.name for spec in pinned]
    nodes: "dict[str, Node]" = {}
    parents: "dict[str, list[str]]" = {}

    for row in rows:
        nid = row["node_id"].strip()
        if not nid:
            continue
        if nid in nodes:
            raise ValueError(f"{dimension}/{axis}: duplicate node_id {nid!r}")
        props = {
            k: v.strip()
            for k, v in row.items()
            if k not in _STRUCTURAL and k not in pin_names and v.strip()
        }
        pins = {
            spec.name: split_pins(row[spec.name], pin_sep, pairs=spec.pairs)
            for spec in pinned
            if (row.get(spec.name) or "").strip()
        }
        nodes[nid] = Node(
            name=row["name"].strip(),
            parent_ids=_parents_of(row, parent_column, parent_sep),
            axes={a: v for a, v in pins.items() if v},
            value_parent=(row.get("value_parent") or "").strip(),
            kind=(row.get("kind") or "").strip(),
            expands_to=_parents_of(row, "expands_to", ";,"),
            props=props,
        )
        parents[nid] = nodes[nid].parent_ids

    roots: "list[str]" = []
    for nid in nodes:
        if not parents[nid]:
            roots.append(nid)
            continue
        for pid in parents[nid]:
            if pid not in nodes:
                raise ValueError(
                    f"{dimension}/{axis}: {nid} names unknown parent {pid!r}"
                )
            nodes[pid].children.append(nid)

    return OntologyDoc(
        meta=Meta(version=version, dimension=f"{dimension}/{axis}"),
        roots=roots,
        nodes=nodes,
    )


def read_spellings(path: Path, surface_column: str) -> "list[NormRow]":
    """``SPELLINGS.tsv`` -> normalization rows.

    A spelling is a surface that is deliberately *not* its own node. ``via`` keeps
    the table's own reason for the fold, because the reason is the only thing that
    makes the fold reviewable later.
    """
    out: "list[NormRow]" = []
    for row in read_table(path):
        surface = (row.get(surface_column) or "").strip()
        canonical = (row.get("node_id") or "").strip()
        if not surface or not canonical:
            continue
        out.append(
            NormRow(
                surface=surface,
                canonical=canonical,
                via=(row.get("kind") or "spelling").strip() or "spelling",
            )
        )
    return out


def convert(
    dimension: str,
    *,
    design_root: Path = DESIGN_ROOT,
    version: str = VERSION,
) -> "tuple[DimensionDoc, dict[str, tuple[OntologyDoc, list[NormRow]]]]":
    """Read one dimension's tables and return its manifest plus per-axis docs."""
    spec = SPECS[dimension]
    root = design_root / spec.design_dir
    manifest = DimensionDoc(
        meta=Meta(version=version, dimension=dimension),
        backbone=spec.backbone,
        axes=list(spec.axes),
        chain_order=spec.chain_order,
    )
    pinned = [a for a in spec.axes if a.name != spec.backbone]

    built: "dict[str, tuple[OntologyDoc, list[NormRow]]]" = {}
    for axis_spec in spec.axes:
        axis = axis_spec.name
        is_backbone = axis == spec.backbone
        doc = build_axis(
            read_table(root / axis / "nodes.tsv"),
            dimension=dimension,
            axis=axis,
            parent_column=(
                spec.backbone_parent_column if is_backbone else spec.parent_column
            ),
            parent_sep=spec.backbone_parent_sep if is_backbone else spec.parent_sep,
            pinned_axes=pinned if is_backbone else (),
            pin_sep=spec.pin_sep,
            version=version,
        )
        norm: "list[NormRow]" = []
        surface_column = spec.spellings_surface.get(axis)
        spellings = root / axis / "SPELLINGS.tsv"
        if surface_column and spellings.exists():
            norm = read_spellings(spellings, surface_column)
        built[axis] = (doc, norm)

    return manifest, built


def write_snapshot(
    dimension: str,
    manifest: DimensionDoc,
    built: "dict[str, tuple[OntologyDoc, list[NormRow]]]",
    *,
    snapshot_root: Path = SNAPSHOT_ROOT,
    version: str = VERSION,
) -> Path:
    """Write ``dimension.json`` and one snapshot directory per axis."""
    out = snapshot_root / dimension / version
    out.mkdir(parents=True, exist_ok=True)
    (out / "dimension.json").write_text(manifest.model_dump_json(indent=2) + "\n")
    for axis, (doc, norm) in built.items():
        Ontology(doc, norm).save(out / axis)
    return out


def iter_dimensions() -> Iterator[str]:
    return iter(SPECS)


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "dimensions",
        nargs="*",
        choices=sorted(SPECS),
        help="dimensions to convert; default all",
    )
    ap.add_argument(
        "--write", action="store_true", help="write snapshots, not just report"
    )
    ap.add_argument("--version", default=VERSION)
    args = ap.parse_args(argv)

    for dimension in args.dimensions or sorted(SPECS):
        manifest, built = convert(dimension, version=args.version)
        counts = ", ".join(f"{a} {len(d.nodes)}" for a, (d, _) in built.items())
        spellings = sum(len(n) for _, n in built.values())
        print(
            f"{dimension:11} backbone={manifest.backbone or '--':10} {counts}"
            + (f", {spellings} spellings" if spellings else "")
        )
        if args.write:
            print(
                f"  -> {write_snapshot(dimension, manifest, built, version=args.version)}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
