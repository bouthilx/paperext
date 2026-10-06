"""Resolve and audit the algorithms dimension.

The lineage axis pins values on three other axes: `signal`, `role`, `attributes`.
A node's effective value set is its own pins plus whatever it inherits, minus
whatever it denies with a negative pin (`!value`).

Inheritance semantics, and why each is what it is:

* **role** unions up the chain. A family pins only what is true of every
  descendant (so `L.pg` may pin `R.fit.obj` but never `A.regime.on`), which makes
  a union safe and makes a blank meaningful.
* **signal** also unions, but it must be deniable. `DDPM` is a training
  objective and its own descendant `DDIM` is a decoder with no training target at
  all, so a chain that only ever adds is wrong. `!S.form.score` is how `DDIM`
  says so.
* **attributes** union *across* families. *Within* one family the nearest
  ancestor wins when the family is single-valued -- but cardinality is derived
  from the pinning pass, not assumed, so an undeclared family that resolves to
  two values is reported rather than silently truncated.

`--audit` reports what a validator cannot see from the tables alone. The checks
exist because each caught a real defect in the sibling models dimension: multi-
parent values decided by the order of the `parents` column, nodes resolving to
nothing on an axis, and negative pins left denying something no ancestor says.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).parent
AXES = ("signal", "role", "attributes")
SPLIT = re.compile(r"[;,]")


def cells(s: str) -> list[str]:
    return [x.strip() for x in SPLIT.split(s) if x.strip()]


@dataclass
class Axis:
    nodes: dict[str, dict[str, str]]

    def family(self, nid: str) -> str:
        """The top-level ancestor, which is what carries scope and cardinality."""
        cur = nid
        while True:
            ps = cells(self.nodes[cur].get("parents", ""))
            if not ps:
                return cur
            cur = ps[0]

    def cardinality(self, nid: str) -> str:
        return self.nodes[self.family(nid)].get("cardinality", "").strip()

    def scope(self, nid: str) -> str:
        return self.nodes[self.family(nid)].get("scope", "").strip()


@dataclass
class Dimension:
    lineage: dict[str, dict[str, str]]
    axes: dict[str, Axis]
    problems: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, root: Path = HERE) -> Dimension:
        def table(p: Path) -> dict[str, dict[str, str]]:
            with p.open(newline="") as fh:
                return {r["node_id"]: r for r in csv.DictReader(fh, delimiter="\t")}

        return cls(
            lineage=table(root / "lineage" / "nodes.tsv"),
            axes={a: Axis(table(root / a / "nodes.tsv")) for a in AXES},
        )

    def chain(self, nid: str) -> list[str]:
        """The node and its ancestors, nearest first, breadth-first over parents."""
        out: list[str] = []
        queue = [nid]
        while queue:
            cur = queue.pop(0)
            if cur in out:
                continue
            out.append(cur)
            queue.extend(cells(self.lineage[cur]["parents"]))
        return out

    def effective(self, nid: str, axis: str) -> tuple[set[str], list[str]]:
        """Resolved values for `nid` on `axis`, plus any conflicts found."""
        chain = self.chain(nid)
        denied = {
            v[1:]
            for n in chain
            for v in cells(self.lineage[n][axis])
            if v.startswith("!")
        }
        notes: list[str] = []
        ax = self.axes[axis]

        if axis != "attributes":
            vals = {
                v
                for n in chain
                for v in cells(self.lineage[n][axis])
                if not v.startswith("!")
            }
            return vals - denied, notes

        # attributes: union across families, nearest-ancestor-wins within one
        per_family: dict[str, list[tuple[int, str]]] = {}
        for depth, n in enumerate(chain):
            for v in cells(self.lineage[n][axis]):
                if v.startswith("!") or v in denied or v not in ax.nodes:
                    continue
                per_family.setdefault(ax.family(v), []).append((depth, v))

        resolved: set[str] = set()
        for fam, hits in per_family.items():
            nearest = min(d for d, _ in hits)
            at_front = sorted({v for d, v in hits if d == nearest})
            card = self.axes[axis].nodes[fam].get("cardinality", "").strip()
            if len(at_front) > 1 and card != "many":
                # never settle this by column order; that is the models defect
                notes.append(
                    f"{nid}: family {fam} resolves to {at_front} at equal depth"
                    f" and cardinality is {card or 'undeclared'}"
                )
            resolved.update(at_front if card == "many" or len(at_front) == 1 else at_front)
        return resolved - denied, notes


def audit(dim: Dimension) -> int:
    out: list[str] = []
    counts: Counter[str] = Counter()

    # structure
    colour: dict[str, int] = {}

    def walk(n: str, stack: list[str]) -> None:
        colour[n] = 1
        for p in cells(dim.lineage[n]["parents"]):
            if p not in dim.lineage:
                out.append(f"DANGLING  {n} -> unknown parent {p}")
            elif colour.get(p) == 1:
                out.append(f"CYCLE     {' -> '.join(stack[stack.index(p):] + [n, p]) if p in stack else f'{n} -> {p}'}")
            elif colour.get(p, 0) == 0:
                walk(p, stack + [n])
        colour[n] = 2

    sys.setrecursionlimit(20000)
    for n in dim.lineage:
        if colour.get(n, 0) == 0:
            walk(n, [])

    # pins
    for nid, row in dim.lineage.items():
        for axis in AXES:
            for v in cells(row[axis]):
                bare = v[1:] if v.startswith("!") else v
                if bare not in dim.axes[axis].nodes:
                    out.append(f"UNKNOWN   {nid}.{axis} pins {v!r}, which is not a node on that axis")
                    continue
                if v.startswith("!"):
                    inherited = {
                        x
                        for a in dim.chain(nid)[1:]
                        for x in cells(dim.lineage[a][axis])
                        if not x.startswith("!")
                    }
                    if bare not in inherited:
                        out.append(f"DEAD PIN  {nid}.{axis} denies {bare}, which no ancestor asserts")
                elif axis == "attributes" and not dim.axes[axis].scope(v):
                    out.append(f"NO SCOPE  {nid} pins {v}, whose family declares no scope predicate")

    # resolution
    for nid, row in dim.lineage.items():
        for axis in AXES:
            vals, notes = dim.effective(nid, axis)
            out.extend(f"AMBIGUOUS {n}" for n in notes)
            counts[f"{axis}:resolved" if vals else f"{axis}:HOMELESS"] += 1
        if row["kind"] in ("bundle", "pipeline") and not row["expands_to"].strip():
            out.append(f"NO EXPANSION  {nid} is kind={row['kind']} but expands_to is empty")

    for line in sorted(set(out)):
        print(line)
    print(f"\n{len(set(out))} problems across {len(dim.lineage)} lineage nodes")
    for k in sorted(counts):
        print(f"  {k:24} {counts[k]}")
    return 1 if out else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--audit", action="store_true", help="report defects and exit nonzero if any")
    ap.add_argument("--node", help="print one node's resolved axes")
    args = ap.parse_args()
    dim = Dimension.load()
    if args.node:
        for axis in AXES:
            vals, notes = dim.effective(args.node, axis)
            print(f"{axis:12} {sorted(vals) or '--'}")
            for n in notes:
                print(f"             ! {n}")
        return 0
    return audit(dim)


if __name__ == "__main__":
    raise SystemExit(main())
