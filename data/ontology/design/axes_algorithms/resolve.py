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
    """Split a pin cell into values.

    The `signal` column holds `(SOURCES, FORMS)` pairs whose commas must not be
    split on, so parenthesised groups are flattened to their member values here
    and the pair structure is read with `signal_pairs`.
    """
    if "(" in s:
        return [v for a, b in signal_pairs(s) for v in sorted(a | b)] + [
            x.strip() for x in s.split(";") if x.strip().startswith("!")
        ]
    return [x.strip() for x in SPLIT.split(s) if x.strip()]


def split_top(s: str, sep: str = ";") -> list[str]:
    """Split on `sep` only outside parentheses."""
    out, depth, cur = [], 0, ""
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


def signal_pairs(s: str) -> list[tuple[frozenset[str], frozenset[str]]]:
    """Parse `(SRC + SRC, FORM + FORM); (SRC, FORM)` into one entry per term.

    A pair is one objective term: the sources its target is drawn from, and the
    form(s) its criterion takes. Both sides are multi-valued, for different
    reasons. Multiple *sources* are needed on 46% of converted nodes -- a
    self-prediction target is the model's own output *of* the next element, and
    a design-based estimator draws its value from a measured outcome and its
    comparability from a design. Multiple *forms* co-describe one criterion:
    f-GAIL's adversarial objective *is* a learned f-divergence, and dropping one
    of the two made its pin identical to plain GAIL's.
    """
    out: list[tuple[frozenset[str], frozenset[str]]] = []
    for item in split_top(s):
        if not item.startswith("("):
            continue
        inner = item.strip()[1:-1]
        parts = split_top(inner, ",")
        if len(parts) != 2:
            continue
        src = frozenset(x.strip() for x in parts[0].split("+") if x.strip())
        form = frozenset(x.strip() for x in parts[1].split("+") if x.strip())
        out.append((src, form))
    return out


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

    def value_parents(self, nid: str) -> list[str]:
        """Parents that axis values flow along.

        A multi-parent node often sits under one family it genuinely descends
        from and another it merely relates to, and inheriting from both
        manufactures contradictions the node then has to deny. `value_parent`
        names the one values come from; the others still carry membership for
        roll-up. It is declared, never inferred from the order of `parents` --
        deciding by column order is a recorded defect of the models dimension.
        """
        row = self.lineage[nid]
        vp = row.get("value_parent", "").strip()
        return [vp] if vp else cells(row["parents"])

    def chain(self, nid: str) -> list[str]:
        """The node and its value-bearing ancestors, nearest first."""
        out: list[str] = []
        queue = [nid]
        while queue:
            cur = queue.pop(0)
            if cur in out:
                continue
            out.append(cur)
            queue.extend(self.value_parents(cur))
        return out

    def conflicting_parents(self, nid: str) -> list[str]:
        """Where a multi-parent node's parents disagree, so a choice is required.

        Two parents conflict when one asserts a value another denies, or when
        they land two values in the same single-valued attribute family. When
        they agree, the union is unambiguous and no declaration is needed --
        explicitness is required exactly where ambiguity exists, not everywhere.
        """
        ps = cells(self.lineage[nid]["parents"])
        if len(ps) < 2 or self.lineage[nid].get("value_parent", "").strip():
            return []
        found: list[str] = []
        for axis in AXES:
            sets, denied = {}, {}
            for p in ps:
                vals = {v for n in self.chain(p) for v in cells(self.lineage[n][axis])}
                sets[p] = {v for v in vals if not v.startswith("!")}
                denied[p] = {v[1:] for v in vals if v.startswith("!")}
            for a in ps:
                for b in ps:
                    if a < b and (sets[a] & denied[b] or sets[b] & denied[a]):
                        found.append(f"{axis}: {a} asserts what {b} denies")
            if axis == "attributes":
                ax = self.axes[axis]
                for fam in {ax.family(v) for p in ps for v in sets[p] if v in ax.nodes}:
                    if ax.nodes[fam].get("cardinality", "").strip() == "many":
                        continue
                    seen = {
                        frozenset(
                            v for v in sets[p] if v in ax.nodes and ax.family(v) == fam
                        )
                        for p in ps
                    }
                    seen = {s for s in seen if s}
                    if len(seen) > 1:
                        found.append(
                            f"attributes: parents disagree in single-valued family {fam}"
                        )
        return found

    def signal_terms(self, nid: str) -> list[tuple[frozenset[str], frozenset[str]]]:
        """The objective terms a node resolves to.

        Pairs inherit as pairs: a descendant that states none of its own takes
        its nearest ancestor's. They are not unioned down the chain, because a
        descendant that restates its terms is replacing them, not adding to
        them -- the DDPM/DDIM lesson applied to the pair representation.
        """
        for n in self.chain(nid):
            pairs = signal_pairs(self.lineage[n]["signal"])
            if pairs:
                denied = {
                    v[1:]
                    for m in self.chain(nid)
                    for v in split_top(self.lineage[m]["signal"])
                    if v.startswith("!")
                }
                out = []
                for src, form in pairs:
                    s, f = src - denied, form - denied
                    if s and f:
                        out.append((frozenset(s), frozenset(f)))
                return out
        return []

    def _subsume(self, axis: str, vals: set[str]) -> set[str]:
        """Drop any value a more specific resolved value already implies.

        A family that legitimately pins the interior `S.src.ext` ("external,
        unspecified") would otherwise push it back onto a leaf that has since
        been given `S.src.ext.obs`, and the leaf would resolve to both. The
        specific value supersedes: it is the same claim, said better. This is
        what lets an interior pin stay correct on a family that really does span
        its children, instead of having to be removed from 19 of them by hand.
        """
        ax = self.axes[axis].nodes
        keep = set(vals)
        for v in vals:
            cur = v
            while True:
                ps = cells(ax[cur].get("parents", "")) if cur in ax else []
                if not ps:
                    break
                cur = ps[0]
                keep.discard(cur)
        return keep

    def effective(self, nid: str, axis: str) -> tuple[set[str], list[str]]:
        """Resolved values for `nid` on `axis`, plus any conflicts found."""
        chain = self.chain(nid)
        notes: list[str] = []
        ax = self.axes[axis]

        # Nearest statement wins between asserting and denying a value. A
        # denial means "this does not apply here", so it governs what it
        # inherits -- not what a more specific descendant goes on to assert
        # about itself. Without this, a `!R.fit.est` on L.causal.struct silently
        # cancelled M.lingam's own R.fit.est pin and left it with no role.
        asserted: dict[str, int] = {}
        denied_at: dict[str, int] = {}
        for depth, n in enumerate(chain):
            for v in cells(self.lineage[n][axis]):
                if v.startswith("!"):
                    denied_at.setdefault(v[1:], depth)
                else:
                    asserted.setdefault(v, depth)
        for v, d in asserted.items():
            if v in denied_at and denied_at[v] == d:
                notes.append(f"{nid}: {v} is both asserted and denied at the same node")
        live = {
            v for v, d in asserted.items() if v not in denied_at or d < denied_at[v]
        }
        denied = {v for v in denied_at if v not in live}

        if axis != "attributes":
            return self._subsume(axis, live), notes

        # attributes: union across families, nearest-ancestor-wins within one
        per_family: dict[str, list[tuple[int, str]]] = {}
        for v in live:
            if v in ax.nodes:
                per_family.setdefault(ax.family(v), []).append((asserted[v], v))

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
            resolved.update(
                at_front if card == "many" or len(at_front) == 1 else at_front
            )
        return self._subsume(axis, resolved - denied), notes


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
                out.append(
                    f"CYCLE     {' -> '.join(stack[stack.index(p):] + [n, p]) if p in stack else f'{n} -> {p}'}"
                )
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
                    out.append(
                        f"UNKNOWN   {nid}.{axis} pins {v!r}, which is not a node on that axis"
                    )
                    continue
                if v.startswith("!"):
                    inherited = {
                        x
                        for a in dim.chain(nid)[1:]
                        for x in cells(dim.lineage[a][axis])
                        if not x.startswith("!")
                    }
                    # A family default is implicitly asserted everywhere in
                    # scope, so denying it is how a node says the default does
                    # not hold -- the whole point of having defaults. Without
                    # this, stripping redundant pins makes every such denial
                    # look dead.
                    is_default = (
                        axis == "attributes"
                        and dim.axes[axis]
                        .nodes[dim.axes[axis].family(bare)]
                        .get("default", "")
                        .strip()
                        == bare
                    )
                    if bare not in inherited and not is_default:
                        out.append(
                            f"DEAD PIN  {nid}.{axis} denies {bare}, which no ancestor asserts"
                        )
                elif axis == "attributes" and not dim.axes[axis].scope(v):
                    out.append(
                        f"NO SCOPE  {nid} pins {v}, whose family declares no scope predicate"
                    )

    for nid, row in dim.lineage.items():
        raw = row["signal"]
        if "(" in raw:
            for item in split_top(raw):
                if item.startswith("!"):
                    continue
                if (
                    not (item.startswith("(") and item.endswith(")"))
                    or len(split_top(item[1:-1], ",")) != 2
                ):
                    out.append(
                        f"BAD PAIR  {nid}: {item!r} is not a (sources, forms) pair"
                    )
            for src, form in signal_pairs(raw):
                if not src or not form:
                    out.append(
                        f"EMPTY SIDE  {nid}: a pair has no {'source' if not src else 'form'}"
                    )
                for v in src:
                    if not v.startswith("S.src"):
                        out.append(
                            f"PAIR SIDE  {nid}: {v} is not an S.src value but sits in the source slot"
                        )
                for v in form:
                    if not v.startswith("S.form"):
                        out.append(
                            f"PAIR SIDE  {nid}: {v} is not an S.form value but sits in the form slot"
                        )

    # A node whose flat values span both sub-facets but which has no pairs
    # anywhere in its chain is back in the cross-product the pairs exist to kill.
    for nid in dim.lineage:
        vals, _ = dim.effective(nid, "signal")
        srcs = {v for v in vals if v.startswith("S.src")}
        forms = {v for v in vals if v.startswith("S.form")}
        if len(srcs) > 1 and len(forms) > 1 and not dim.signal_terms(nid):
            out.append(
                f"UNPAIRED  {nid}: {len(srcs)} sources x {len(forms)} forms resolve with no pair to say which go together"
            )

    for nid in dim.lineage:
        for why in dim.conflicting_parents(nid):
            out.append(f"NEEDS VALUE_PARENT  {nid}: {why}")
        vp = dim.lineage[nid].get("value_parent", "").strip()
        if vp and vp not in cells(dim.lineage[nid]["parents"]):
            out.append(f"BAD VALUE_PARENT  {nid}: {vp} is not among its parents")

    # resolution
    for nid, row in dim.lineage.items():
        for axis in AXES:
            vals, notes = dim.effective(nid, axis)
            out.extend(f"AMBIGUOUS {n}" for n in notes)
            counts[f"{axis}:resolved" if vals else f"{axis}:HOMELESS"] += 1
    # expands_to must name nodes, not describe them: an expansion in prose
    # cannot be rolled up, and rolling up is the only reason it exists. It may
    # be empty when a composite's parts are not independently nameable --
    # nobody cites "column subsampling" on its own -- but it may never be prose.
    for nid, row in dim.lineage.items():
        exp = row["expands_to"].strip()
        if not exp:
            continue
        for part in cells(exp):
            if part not in dim.lineage:
                out.append(
                    f"PROSE EXPANSION  {nid}: expands_to names {part!r}, which is not a node_id"
                )
        if row["kind"] not in ("bundle", "pipeline"):
            out.append(
                f"EXPANSION ON METHOD  {nid} has an expansion but kind={row['kind']!r}"
            )

    for line in sorted(set(out)):
        print(line)
    print(f"\n{len(set(out))} problems across {len(dim.lineage)} lineage nodes")
    for k in sorted(counts):
        print(f"  {k:24} {counts[k]}")
    return 1 if out else 0


def root_of(dim: Dimension, nid: str) -> str:
    """The lineage family a node ultimately sits under, following first parents."""
    cur, seen = nid, {nid}
    while True:
        ps = cells(dim.lineage[cur]["parents"])
        if not ps or ps[0] in seen:
            return cur
        seen.add(ps[0])
        cur = ps[0]


def homeless(dim: Dimension) -> int:
    """Group nodes that resolve to nothing, by family. This is the design finding:
    a region with no value on an axis is a gap in the axis, not in the node."""
    for axis in AXES:
        groups: dict[str, list[str]] = {}
        for nid in dim.lineage:
            vals, _ = dim.effective(nid, axis)
            if not vals:
                groups.setdefault(root_of(dim, nid), []).append(nid)
        total = sum(len(v) for v in groups.values())
        label = (
            "nodes with no non-default pin (a blank means the family default)"
            if axis == "attributes"
            else "homeless nodes"
        )
        print(f"\n{axis} — {total} {label}, in {len(groups)} families")
        for fam, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            print(f"  {len(members):4}  {fam:20} {dim.lineage[fam]['name'][:46]}")
    return 0


def redundant(dim: Dimension) -> int:
    """Attribute pins that only restate their family default.

    A blank means the default, so such a pin carries no information. One region
    measured 650 of 1024 attribute pins this way -- real information buried under
    its own boilerplate. Stripping them is lossless *because* the default is
    written down.
    """
    ax = dim.axes["attributes"]
    hits: dict[str, list[str]] = {}
    for nid, row in dim.lineage.items():
        for v in cells(row["attributes"]):
            if v.startswith("!") or v not in ax.nodes:
                continue
            fam = ax.family(v)
            if ax.nodes[fam].get("default", "").strip() == v:
                hits.setdefault(fam, []).append(nid)
    total = sum(len(v) for v in hits.values())
    pins = sum(
        len([v for v in cells(r["attributes"]) if not v.startswith("!")])
        for r in dim.lineage.values()
    )
    print(
        f"{total} of {pins} attribute pins restate a family default ({100 * total // max(pins, 1)}%)"
    )
    for fam, ns in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(ns):5}  {fam:18} -> {ax.nodes[fam]['default']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--audit", action="store_true", help="report defects and exit nonzero if any"
    )
    ap.add_argument(
        "--homeless",
        action="store_true",
        help="group nodes resolving to no value, by family",
    )
    ap.add_argument(
        "--redundant",
        action="store_true",
        help="count attribute pins that merely restate their family default",
    )
    ap.add_argument("--node", help="print one node's resolved axes")
    args = ap.parse_args()
    dim = Dimension.load()
    if args.homeless:
        return homeless(dim)
    if args.redundant:
        return redundant(dim)
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
