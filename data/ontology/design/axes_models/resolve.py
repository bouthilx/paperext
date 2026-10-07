#!/usr/bin/env python3
"""Resolve the effective axis values of a models-lineage node.

Encodes the inheritance semantics of the faceted models dimension. They are not
obvious, and three separate defects were found by placing real corpus names
against them -- see the rules below, each of which exists because the naive
version produced a wrong answer on a real model.

A lineage node pins only what DIFFERS from its parent, so a node's effective
values are never read off its own row.

**connectivity** -- multi-valued, union up the ancestor chain. A parent's coarse
value and a child's refinement may both appear (Convolution + Standard
convolution): the child refines, it does not replace.

**topology** -- single-valued, nearest ancestor that pins it wins. When a node
has several parents that disagree, it MUST pin its own value: picking by
`parents` column order made Flamingo a bidirectional encoder because `vit`
happened to be listed before `transformer`. `audit()` reports any node in that
state instead of silently resolving it.

**attributes** -- multi-valued across families. WITHIN a family, cardinality is
declared per family in attributes/nodes.tsv:
  one  -- nearest pin wins (substrate, latent treatment, invertibility...).
          Without this VQ-VAE resolved to Deterministic AND Stochastic.
  many -- union (symmetry, shortcut connections). EGNN really is permutation-
          AND Euclidean-equivariant; V-Net really has concatenative skips AND
          additive residuals. A per-family single-value rule silently dropped
          one of each.

**negative pins** -- a value written `!node-id` in a lineage row BLOCKS that
value for the node and its descendants. Needed because union inheritance alone
gives a child no way to deny its parent: MLP-Mixer resolved to Self-attention
although the paper's claim is "without attention", and FFJORD resolved to
Standard convolution because Neural ODE descends from ResNet.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
AXES = ("connectivity", "topology", "attributes")


def _load(rel: str) -> list[dict[str, str]]:
    with open(BASE / rel, encoding="utf-8") as fh:
        return list(
            csv.DictReader((l for l in fh if not l.startswith("#")), delimiter="\t")
        )


def load_axes() -> tuple[dict, dict, dict]:
    """Returns (lineage rows by id, axis-value names by id, family id by value id)."""
    lineage = {r["node_id"]: r for r in _load("lineage/nodes.tsv")}
    names: dict[str, str] = {}
    family: dict[str, str] = {}
    for axis in AXES:
        for r in _load(f"{axis}/nodes.tsv"):
            names[r["node_id"]] = r["name"]
            if axis == "attributes":
                family[r["node_id"]] = r["parent_id"] or r["node_id"]
    return lineage, names, family


def family_cardinality() -> dict[str, str]:
    return {
        r["node_id"]: (r.get("cardinality") or "one").strip() or "one"
        for r in _load("attributes/nodes.tsv")
        if not r["parent_id"].strip()
    }


def _parents(lineage: dict, node: str) -> list[str]:
    return [p for p in (lineage[node]["parents"] or "").split("|") if p.strip()]


def _chain(lineage: dict, node: str, seen: set[str] | None = None) -> list[str]:
    """The node, then its ancestors nearest-first."""
    seen = seen if seen is not None else set()
    if node in seen:
        return []
    seen.add(node)
    out = [node]
    for p in _parents(lineage, node):
        out.extend(_chain(lineage, p, seen))
    return out


def _pins(lineage: dict, node: str, axis: str) -> list[str]:
    return [v.strip() for v in (lineage[node].get(axis) or "").split("|") if v.strip()]


def effective(
    lineage: dict,
    family: dict,
    node: str,
    axis: str,
    cardinality: dict[str, str] | None = None,
) -> list[str]:
    chain = _chain(lineage, node)
    blocked = {
        v[1:] for n in chain for v in _pins(lineage, n, axis) if v.startswith("!")
    }

    if axis == "topology":
        for n in chain:
            vals = [
                v
                for v in _pins(lineage, n, axis)
                if not v.startswith("!") and v not in blocked
            ]
            if vals:
                return vals[:1]
        return []

    if axis == "connectivity":
        acc: list[str] = []
        for n in chain:
            for v in _pins(lineage, n, axis):
                if not v.startswith("!") and v not in blocked and v not in acc:
                    acc.append(v)
        return acc

    card = cardinality if cardinality is not None else family_cardinality()
    chosen: list[str] = []
    closed: set[str] = set()
    for n in chain:
        for v in _pins(lineage, n, axis):
            if v.startswith("!") or v in blocked or v in chosen:
                continue
            fam = family.get(v, v)
            if card.get(fam, "one") == "one":
                if fam in closed:
                    continue
                closed.add(fam)
            chosen.append(v)
    return chosen


def audit() -> list[str]:
    """Nodes whose parents disagree on topology and which do not pin their own."""
    lineage, _, family = load_axes()
    card = family_cardinality()
    problems = []
    for nid, row in lineage.items():
        ps = _parents(lineage, nid)
        if len(ps) < 2 or _pins(lineage, nid, "topology"):
            continue
        vals = {t for p in ps for t in effective(lineage, family, p, "topology", card)}
        if len(vals) > 1:
            problems.append(
                f"{nid}: parents disagree on topology {sorted(vals)}; "
                f"resolved by column order -- pin one explicitly"
            )
    for nid in lineage:
        if _parents(lineage, nid) and not effective(
            lineage, family, nid, "topology", card
        ):
            problems.append(f"{nid}: resolves to NO topology")
    return problems


def describe(node: str) -> dict[str, list[str]]:
    lineage, names, family = load_axes()
    card = family_cardinality()
    return {
        a: [names.get(v, v) for v in effective(lineage, family, node, a, card)]
        for a in AXES
    }


if __name__ == "__main__":
    if sys.argv[1:2] == ["--audit"]:
        for p in audit():
            print("  " + p)
        sys.exit(0)
    lineage, names, family = load_axes()
    card = family_cardinality()
    for node in sys.argv[1:]:
        if node not in lineage:
            print(f"  {node}: not a lineage node")
            continue
        v = {
            a: ", ".join(
                names.get(x, x) for x in effective(lineage, family, node, a, card)
            )
            or "—"
            for a in AXES
        }
        print(
            f"  {lineage[node]['name']:<26} conn={v['connectivity']:<40} "
            f"topo={v['topology']:<28} attr={v['attributes']}"
        )
