"""Sealed eval splits for the held-out re-mapping eval (WS-D D1b-1, #51).

**Hoisted here from #53 on purpose.** It is the one genuine ordering inversion in
D1b: if the splits were drawn in #53, the prompt iteration in #52 would already
have been done while looking at names that later land in the gate set, burning it.
This is ~200 API-free lines; it does not belong at the end.

The pool is the already-mapped **leaf** names of a dimension. Non-leaf targets are
excluded — ablating them orphans a subtree — as are names carried by a node with
children anywhere in the tree (see :func:`~paperext.categorize.ablate.ablatable`).

Stratified on the two axes that actually predict difficulty:

- **anchoring** — whether cheap containment retrieval finds anything to place the
  name near: ``parent`` (a candidate is an ancestor of the true node), ``some``
  (candidates, but none on the lineage), ``cold`` (nothing at all). On the 1208
  *unmapped* model names, forward substring alone returns nothing 96.4% of the
  time, so this axis dominates.
- **cut class** — the milabench-cut category of the true node, so the thin buckets
  (MLP, RNN, diffusion) get support instead of being swamped by ``Other``.

The anchoring probe here is **deliberately the baseline generator**, frozen: the
strata must not shift when #52 improves retrieval, or a sealed manifest would stop
matching the splits it names. #52 builds its ranked generator on top; it does not
feed this.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Union

from pydantic import BaseModel, Field

from paperext.analysis.rollup import DEFAULT_DROP_ROOTS, Cut, str_normalize
from paperext.categorize.ablate import ablatable, name_matches
from paperext.categorize.apply import content_hash, ontology_root
from paperext.categorize.placement import load_dimension_cut, to_placement
from paperext.ontology.ontology import Ontology

#: Shortest node name allowed to anchor a longer query by reverse containment.
#: Below this it is noise ("ml" matches almost everything).
MIN_ANCHOR_LEN = 3

#: Default split sizes, sized in #53: at N=300 the gate has ~97% power to detect
#: W=0.50 against H0: W <= 0.45; at N=100 it is ~64%, which is not worth running.
DEFAULT_SIZES = {"dev": 200, "gate": 300}

DEFAULT_SEED = 42


class SplitItem(BaseModel):
    """One held-out name."""

    node_id: str
    surface: str
    name: str
    anchoring: str
    cut_category: str | None = None


class Splits(BaseModel):
    """The sealed manifest. Committed; regenerating it must reproduce it exactly."""

    seed: int
    dimension: str
    base_version: str
    base_content_hash: str
    pool_size: int
    strata: "dict[str, dict[str, int]]" = Field(default_factory=dict)
    dev: list[SplitItem] = Field(default_factory=list)
    gate: list[SplitItem] = Field(default_factory=list)
    reserve: list[SplitItem] = Field(default_factory=list)
    gate_ids_sha256: str = ""


# --------------------------------------------------------------------------- #
# The anchoring probe (frozen baseline retrieval)
# --------------------------------------------------------------------------- #


def _normalized_keys(onto: Ontology) -> "dict[str, list[str]]":
    """node id -> its normalized name plus its (already normalized) surfaces."""
    keys: "dict[str, list[str]]" = {}
    for node_id, node in onto.nodes.items():
        keys[node_id] = [str_normalize(node.name), *onto.surfaces(node_id)]
    return keys


def anchoring(
    onto: Ontology,
    node_id: str,
    surface: str,
    *,
    keys: "dict[str, list[str]] | None" = None,
) -> str:
    """``parent`` / ``some`` / ``cold`` for *surface* held out of *onto*.

    Computed against the **full** tree with the ablated ids excluded from the hit
    list, which is exactly equivalent to running the probe on the ablated copy:
    removing nodes can only remove hits, and the description scrub does not touch
    the names and surfaces containment matches on. That equivalence is what keeps
    this O(1) copies instead of one deep copy per pool item.
    """
    keys = keys if keys is not None else _normalized_keys(onto)
    query = str_normalize(surface)
    hidden = set(name_matches(onto, surface)) | {node_id}
    resolved = onto.resolve(surface)
    if resolved is not None:
        hidden.add(resolved)

    candidates = {nid for nid in onto.search(surface) if nid not in hidden}
    for nid, node_keys in keys.items():
        if nid in hidden or nid in candidates:
            continue
        if any(
            len(k) >= MIN_ANCHOR_LEN and k != query and k in query for k in node_keys
        ):
            candidates.add(nid)

    if not candidates:
        return "cold"
    lineage = set(onto.ancestry(node_id)[:-1])
    return "parent" if candidates & lineage else "some"


# --------------------------------------------------------------------------- #
# Pool
# --------------------------------------------------------------------------- #


def build_pool(
    onto: Ontology,
    cut: Cut,
    *,
    drop_roots: "tuple[str, ...]" = DEFAULT_DROP_ROOTS,
) -> "list[SplitItem]":
    """Every already-mapped leaf name that can be held out cleanly.

    Sorted by node id, so the pool order is fixed before any shuffling and the
    manifest reproduces bit-for-bit.
    """
    drop = {str_normalize(root) for root in drop_roots}
    keys = _normalized_keys(onto)

    items: "list[SplitItem]" = []
    for node_id in sorted(onto.nodes):
        if onto.children(node_id):
            continue
        surfaces = onto.surfaces(node_id)
        if not surfaces:
            continue
        if str_normalize(onto.name(onto.root_of(node_id))) in drop:
            continue
        # the node's own name if it owns it, else its first surface (stable order)
        own = str_normalize(onto.name(node_id))
        surface = own if own in surfaces else surfaces[0]
        if not ablatable(onto, surface):
            continue
        placement = to_placement(onto, node_id, cut, drop_roots=drop_roots)
        items.append(
            SplitItem(
                node_id=node_id,
                surface=surface,
                name=onto.name(node_id),
                anchoring=anchoring(onto, node_id, surface, keys=keys),
                cut_category=placement.cut_category,
            )
        )
    return items


def stratum_of(item: SplitItem) -> str:
    return f"{item.anchoring}|{item.cut_category or '-'}"


# --------------------------------------------------------------------------- #
# Allocation
# --------------------------------------------------------------------------- #


def _largest_remainder(
    weights: "dict[str, int]", total: int, caps: "dict[str, int]"
) -> "dict[str, int]":
    """Split *total* across strata proportionally to *weights*, capped by *caps*.

    Largest-remainder so the allocation sums to *total* exactly; strata that hit
    their cap give their surplus back to the rest, iterating until stable.
    """
    keys = sorted(weights)
    alloc = {k: 0 for k in keys}
    remaining = min(total, sum(caps.values()))
    active = [k for k in keys if caps[k] > 0]

    while remaining > 0 and active:
        total_weight = sum(weights[k] for k in active)
        if total_weight:
            exact = {k: remaining * weights[k] / total_weight for k in active}
        else:
            exact = {k: remaining / len(active) for k in active}
        floors = {k: int(exact[k]) for k in active}
        short = remaining - sum(floors.values())
        # ties broken by stratum name, so the manifest is reproducible
        order = sorted(active, key=lambda k: (-(exact[k] - floors[k]), k))
        for k in order[:short]:
            floors[k] += 1

        progressed = False
        for k in active:
            take = min(floors[k], caps[k] - alloc[k])
            if take:
                alloc[k] += take
                remaining -= take
                progressed = True
        active = [k for k in active if caps[k] - alloc[k] > 0]
        if not progressed:  # every active stratum is full
            break
    return alloc


def draw_splits(
    onto: Ontology,
    dimension: str,
    cut: Cut,
    *,
    base_version: str = "v0",
    seed: int = DEFAULT_SEED,
    sizes: "dict[str, int] | None" = None,
) -> Splits:
    """Draw dev / gate / reserve from the pool, stratified and reproducible."""
    sizes = dict(sizes or DEFAULT_SIZES)
    pool = build_pool(onto, cut)

    groups: "dict[str, list[SplitItem]]" = {}
    for item in pool:
        groups.setdefault(stratum_of(item), []).append(item)

    rng = random.Random(seed)
    for key in sorted(groups):
        rng.shuffle(groups[key])

    weights = {k: len(v) for k, v in groups.items()}
    cursors = {k: 0 for k in groups}
    drawn: "dict[str, list[SplitItem]]" = {}
    strata: "dict[str, dict[str, int]]" = {
        k: {"pool": weights[k]} for k in sorted(groups)
    }

    for split in ("dev", "gate"):
        caps = {k: weights[k] - cursors[k] for k in groups}
        alloc = _largest_remainder(weights, sizes[split], caps)
        taken: "list[SplitItem]" = []
        for key in sorted(groups):
            n = alloc[key]
            taken.extend(groups[key][cursors[key] : cursors[key] + n])
            cursors[key] += n
            strata[key][split] = n
        drawn[split] = taken

    reserve: "list[SplitItem]" = []
    for key in sorted(groups):
        rest = groups[key][cursors[key] :]
        reserve.extend(rest)
        strata[key]["reserve"] = len(rest)
    drawn["reserve"] = reserve

    gate_ids = "\n".join(sorted(item.node_id for item in drawn["gate"]))
    return Splits(
        seed=seed,
        dimension=dimension,
        base_version=base_version,
        base_content_hash=content_hash(onto),
        pool_size=len(pool),
        strata=strata,
        dev=drawn["dev"],
        gate=drawn["gate"],
        reserve=drawn["reserve"],
        gate_ids_sha256=hashlib.sha256(gate_ids.encode()).hexdigest(),
    )


def write_splits(splits: Splits, path: Union[str, Path]) -> Path:
    """Write the manifest, refusing to silently reseal a different draw."""
    path = Path(path)
    if path.exists():
        existing = Splits.model_validate_json(path.read_text(encoding="utf-8"))
        if existing.gate_ids_sha256 != splits.gate_ids_sha256:
            raise FileExistsError(
                f"{path} holds a different sealed gate set "
                f"({existing.gate_ids_sha256[:12]} != {splits.gate_ids_sha256[:12]}); "
                "delete it explicitly if the splits are really being redrawn"
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(splits.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dim", default="models")
    parser.add_argument("--base", default="v0")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--dev", type=int, default=DEFAULT_SIZES["dev"])
    parser.add_argument("--gate", type=int, default=DEFAULT_SIZES["gate"])
    parser.add_argument("--root", default=None, help="ontology root")
    parser.add_argument("--out", default=None, help="manifest path")
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root else ontology_root()
    onto = Ontology.load(root / args.dim / args.base)
    splits = draw_splits(
        onto,
        args.dim,
        load_dimension_cut(args.dim),
        base_version=args.base,
        seed=args.seed,
        sizes={"dev": args.dev, "gate": args.gate},
    )
    out = Path(args.out) if args.out else root / "eval" / args.dim / "splits.json"
    write_splits(splits, out)

    print(
        f"# pool {splits.pool_size} -> dev {len(splits.dev)} / gate {len(splits.gate)} / reserve {len(splits.reserve)}"
    )
    for key in sorted(splits.strata):
        counts = splits.strata[key]
        print(
            f"  {key:<28} pool {counts['pool']:>4}  dev {counts['dev']:>3}  "
            f"gate {counts['gate']:>3}  reserve {counts['reserve']:>4}"
        )
    print(f"# gate sha256 {splits.gate_ids_sha256}")
    print(f"# wrote {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
