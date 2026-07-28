"""Faithful ``v0`` migration of the legacy ``categorized_*.json`` trees (D1a, #36).

``v0`` is a structural, count-neutral import — intentionally "over-noded". It:

- turns every legacy node into an ontology node with a unique id (order preserved,
  so the roll-up converter reproduces the legacy DFS-ordered dedup);
- prunes **pure-duplicate subtrees** only — a node whose normalized name equals its
  parent's and whose whole subtree shares that name (the self-nests like
  ``few-shot learning`` nested under itself). This is provably roll-up-neutral: the
  surviving ancestor already carries that name-key and rolls up identically, and no
  distinct-named node changes depth. Cross-branch / sibling duplicates (``sam``,
  ``hubert``, ``vicuna``, ``classification`` …) are *kept as distinct nodes* — they
  are genuinely different entities, and splitting/identifying them is D1b's job;
- builds the normalization DB ``surface -> canonical`` 1:1, first-wins in DFS order.
  Where two distinct nodes share a normalized name, the DFS-first (legacy-winner)
  node owns the surface; the "loser" node is left surface-less (reported) for D1b to
  re-surface with a disambiguated form.

All concept-vs-variant judgment (is ``resnet-50`` its own model or a spelling of
``resnet``?) is deferred to D1b. ``v0`` changes no counts.
"""

import argparse
import json
from pathlib import Path
from typing import Union

from paperext.analysis.rollup import str_normalize
from paperext.ontology.ontology import (
    NORMALIZATION_FILE,
    ONTOLOGY_FILE,
    Ontology,
)
from paperext.ontology.schema import Meta, Node, NormRow, OntologyDoc

#: dimension -> legacy tree path (relative to repo root / data dir).
LEGACY_TREES = {
    "models": "data/categorized_models.json",
    "datasets": "data/categorized_datasets.json",
    "domains": "data/categorized_domains.json",
}


def build_v0(
    tree_path: Union[str, Path], dimension: str
) -> "tuple[OntologyDoc, list[NormRow], dict]":
    """Build the ``v0`` :class:`OntologyDoc` + normalization for a legacy tree.

    Returns ``(doc, norm_rows, report)`` where *report* records the pruned self-nest
    nodes and the surface-less duplicate nodes for the migration log.
    """
    tree = json.loads(Path(tree_path).read_text())

    nodes: "dict[str, Node]" = {}
    roots: "list[str]" = []
    used_ids: "set[str]" = set()

    def new_id(name: str) -> str:
        base = str_normalize(name) or "node"
        cand, n = base, 2
        while cand in used_ids:
            cand = f"{base}__{n}"
            n += 1
        used_ids.add(cand)
        return cand

    def build(subtree: dict, parent_id: "str | None") -> None:
        for raw_name, kids in subtree.items():
            nid = new_id(raw_name)
            nodes[nid] = Node(name=raw_name)
            if parent_id is None:
                roots.append(nid)
            else:
                nodes[parent_id].children.append(nid)
            build(kids, nid)

    build(tree, None)

    norm_name = {nid: str_normalize(node.name) for nid, node in nodes.items()}

    # -- prune pure-duplicate subtrees (bottom-up) ---------------------------
    pruned: "list[str]" = []

    def prune(nid: str) -> None:
        kept = []
        for cid in list(nodes[nid].children):
            prune(cid)
            # a same-name child that is now childless is a redundant self-nest node
            if norm_name[cid] == norm_name[nid] and not nodes[cid].children:
                pruned.append(cid)
            else:
                kept.append(cid)
        nodes[nid].children = kept

    for rid in roots:
        prune(rid)
    for nid in pruned:
        del nodes[nid]

    # -- normalization DB (1:1, DFS-first wins) ------------------------------
    def dfs(nid: str):
        yield nid
        for cid in nodes[nid].children:
            yield from dfs(cid)

    surface_to_canonical: "dict[str, str]" = {}
    norm_rows: "list[NormRow]" = []
    surfaceless: "list[str]" = []
    for rid in roots:
        for nid in dfs(rid):
            surf = str_normalize(nodes[nid].name)
            if not surf:
                continue
            if surf in surface_to_canonical:
                surfaceless.append(nid)  # loser of a cross-branch/sibling collision
                continue
            surface_to_canonical[surf] = nid
            norm_rows.append(NormRow(surface=surf, canonical=nid, via="seed"))

    doc = OntologyDoc(
        meta=Meta(version="v0", dimension=dimension),
        roots=roots,
        nodes=nodes,
    )
    report = {
        "dimension": dimension,
        "n_nodes": len(nodes),
        "n_surfaces": len(norm_rows),
        "pruned_self_nests": pruned,
        "surfaceless_collision_nodes": surfaceless,
    }
    return doc, norm_rows, report


def write_snapshot(
    doc: OntologyDoc, norm_rows: "list[NormRow]", out_dir: Union[str, Path]
) -> None:
    """Write ``ontology.json`` + ``normalization.jsonl`` into *out_dir*."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / ONTOLOGY_FILE).write_text(
        json.dumps(doc.model_dump(), indent=2, ensure_ascii=False) + "\n"
    )
    lines = [
        json.dumps(row.model_dump(exclude_none=True), ensure_ascii=False)
        for row in norm_rows
    ]
    (out_dir / NORMALIZATION_FILE).write_text("\n".join(lines) + "\n")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Build the v0 ontology snapshots.")
    parser.add_argument(
        "--dimensions",
        nargs="*",
        default=list(LEGACY_TREES),
        choices=list(LEGACY_TREES),
        help="Which dimensions to migrate (default: all).",
    )
    parser.add_argument(
        "--out-root",
        default="data/ontology",
        help="Root under which <dim>/v0/ snapshots are written.",
    )
    args = parser.parse_args(argv)

    for dim in args.dimensions:
        doc, norm_rows, report = build_v0(LEGACY_TREES[dim], dim)
        out_dir = Path(args.out_root) / dim / "v0"
        write_snapshot(doc, norm_rows, out_dir)
        # round-trip sanity: the written snapshot loads and re-indexes
        Ontology.load(out_dir)
        print(
            f"{dim}: {report['n_nodes']} nodes, {report['n_surfaces']} surfaces, "
            f"{len(report['pruned_self_nests'])} self-nests pruned, "
            f"{len(report['surfaceless_collision_nodes'])} surface-less collision "
            f"nodes -> {out_dir}"
        )


if __name__ == "__main__":
    main()
