#!/usr/bin/env python3
"""Resolve the effective axis values of a models-lineage node.

Encodes the inheritance semantics of the faceted models dimension, which are
not obvious and are easy to get wrong:

- A lineage node pins only what DIFFERS from its parent; everything else is
  inherited. So the effective value of a node is never read off its own row.
- `topology` is single-valued: the nearest ancestor that pins it wins.
- `connectivity` is multi-valued: union up the ancestor chain. A parent's
  coarse value and a child's refinement may both appear (Convolution +
  Standard convolution), which is correct -- the child refines, it does not
  replace.
- `attributes` is multi-valued ACROSS families but SINGLE-valued WITHIN one.
  Union across families, nearest-pin-wins within a family. Without this rule
  VQ-VAE resolves to Deterministic AND Stochastic AND Quantized, because it
  inherits one latent value from VAE and another from the family default.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


def _load(rel: str) -> list[dict[str, str]]:
    with open(BASE / rel, encoding="utf-8") as fh:
        return list(csv.DictReader((l for l in fh if not l.startswith("#")), delimiter="\t"))


def load_axes() -> tuple[dict, dict, dict]:
    lineage = {r["node_id"]: r for r in _load("lineage/nodes.tsv")}
    names: dict[str, str] = {}
    family: dict[str, str] = {}
    for axis in ("connectivity", "topology", "attributes"):
        for r in _load(f"{axis}/nodes.tsv"):
            names[r["node_id"]] = r["name"]
            if axis == "attributes":
                family[r["node_id"]] = r["parent_id"] or r["node_id"]
    return lineage, names, family


def _parents(lineage: dict, node: str) -> list[str]:
    return [p for p in (lineage[node]["parents"] or "").split("|") if p.strip()]


def _chain(lineage: dict, node: str, seen: set[str] | None = None) -> list[str]:
    """Node first, then ancestors breadth-first: nearest pin wins."""
    seen = seen if seen is not None else set()
    if node in seen:
        return []
    seen.add(node)
    out = [node]
    for p in _parents(lineage, node):
        out.extend(_chain(lineage, p, seen))
    return out


def effective(lineage: dict, family: dict, node: str, axis: str) -> list[str]:
    chain = _chain(lineage, node)
    if axis == "topology":
        for n in chain:
            vals = [v for v in (lineage[n].get(axis) or "").split("|") if v.strip()]
            if vals:
                return vals[:1]
        return []
    if axis == "connectivity":
        acc: list[str] = []
        for n in chain:
            for v in (lineage[n].get(axis) or "").split("|"):
                if v.strip() and v.strip() not in acc:
                    acc.append(v.strip())
        return acc
    # attributes: nearest pin wins WITHIN a family, union ACROSS families
    chosen: dict[str, str] = {}
    for n in chain:
        for v in (lineage[n].get(axis) or "").split("|"):
            v = v.strip()
            if v and family.get(v, v) not in chosen:
                chosen[family.get(v, v)] = v
    return list(chosen.values())


def describe(node: str) -> dict[str, list[str]]:
    lineage, names, family = load_axes()
    return {
        axis: [names.get(v, v) for v in effective(lineage, family, node, axis)]
        for axis in ("connectivity", "topology", "attributes")
    }


if __name__ == "__main__":
    lineage, names, family = load_axes()
    for node in sys.argv[1:]:
        if node not in lineage:
            print(f"  {node}: not a lineage node")
            continue
        vals = {a: ", ".join(names.get(v, v) for v in effective(lineage, family, node, a)) or "—"
                for a in ("connectivity", "topology", "attributes")}
        print(f"  {lineage[node]['name']:<26} conn={vals['connectivity']:<38} "
              f"topo={vals['topology']:<28} attr={vals['attributes']}")
