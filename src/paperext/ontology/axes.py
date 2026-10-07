"""Resolve a faceted dimension's axis values (D1h, #100).

A backbone node pins values on the other axes, and pins only what *differs* from
its parents, so a node's effective values are never read off its own row. This
module is the one place those inheritance semantics live.

Each semantic is declared per axis in ``dimension.json`` rather than hard-coded,
because the two dimensions that have a backbone do not agree on all of them — and
the disagreement is a finding about the dimensions, not a wrinkle to flatten:

* **inherit** — ``union`` (a child refines rather than replaces), ``nearest``
  (single-valued for the whole axis), ``nearest-in-family`` (union across
  families, nearest wins within one, governed by that family's ``cardinality``).
* **deny** — how far a negative pin reaches. ``nearest`` lets a descendant's own
  assertion beat an ancestor's denial; ``chain`` makes a denial anywhere final.
* **subsume** — whether a specific value supersedes a resolved ancestor of
  itself.

Resolution reports its own ambiguity rather than settling it. Where two values
land at equal depth in a single-valued family, that is returned as a note and
both values are kept: picking one by column order is the recorded defect this
whole design exists to avoid.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from paperext.ontology.ontology import Ontology
from paperext.ontology.schema import AxisSpec, DimensionDoc, Node

DIMENSION_FILE = "dimension.json"

_SPLIT_SEMI_COMMA = re.compile(r"[;,]")

#: One objective term: the sources its target is drawn from, and the form(s) its
#: criterion takes. Both sides are multi-valued, for different reasons -- a
#: self-prediction target is the model's own output *of* the next element, while
#: f-GAIL's adversarial objective *is* a learned f-divergence and dropping either
#: form made its pin identical to plain GAIL's.
Term = "tuple[frozenset[str], frozenset[str]]"


def split_top(s: str, sep: str = ";") -> "list[str]":
    """Split on *sep* only outside parentheses."""
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


def parse_term(item: str) -> "tuple[frozenset[str], frozenset[str]] | None":
    """``(SRC + SRC, FORM + FORM)`` -> one term, or ``None`` if not a pair."""
    item = item.strip()
    if not (item.startswith("(") and item.endswith(")")):
        return None
    parts = split_top(item[1:-1], ",")
    if len(parts) != 2:
        return None
    src = frozenset(x.strip() for x in parts[0].split("+") if x.strip())
    form = frozenset(x.strip() for x in parts[1].split("+") if x.strip())
    return src, form


#: The four states a family can be in on a node. The distinction is the reason
#: family defaults are written down at all: without it, "this procedure is
#: on-policy by default" and "nobody has said whether it is on-policy" are the
#: same blank cell.
FAMILY_STATES = ("stated", "absent", "default", "unknown")


@dataclass(frozen=True)
class FamilyValue:
    """What a node says about one axis family, and how firmly.

    ``state`` is:

    - ``stated`` — the node resolves to ``values`` in this family.
    - ``absent`` — it resolves to nothing **and** the chain denies the family
      default. An asserted absence: somebody looked and said no.
    - ``default`` — it resolves to nothing and the family has a default, which
      **would** apply wherever the family's ``scope`` predicate holds.
    - ``unknown`` — nothing resolved and no default to fall back on.

    ``default`` is deliberately *not* merged into ``values``. A family default
    applies only where its scope predicate holds, that predicate is prose, and
    no code can evaluate it — so synthesising the default here would turn an
    unchecked claim into data. `A.regime` defaults to on-policy, which is
    meaningless for a tokenizer. The caller gets the default and the prose and
    decides.
    """

    family: str
    values: "frozenset[str]"
    state: str
    default: str = ""
    scope: str = ""

    @property
    def effective_values(self) -> "frozenset[str]":
        """``values``, or the default when that is the family's state.

        Only correct where the family's scope predicate holds. Read
        :class:`FamilyValue`'s docstring before using it.
        """
        if self.state == "default" and self.default:
            return frozenset({self.default})
        return self.values


@dataclass
class Dimension:
    """A faceted dimension: a manifest plus one :class:`Ontology` per axis."""

    doc: DimensionDoc
    axes: "dict[str, Ontology]"

    # -- construction ---------------------------------------------------------

    @classmethod
    def load(cls, version_dir: "str | Path") -> "Dimension":
        version_dir = Path(version_dir)
        doc = DimensionDoc.model_validate_json(
            (version_dir / DIMENSION_FILE).read_text()
        )
        return cls(
            doc=doc,
            axes={
                spec.name: Ontology.load(version_dir / spec.name) for spec in doc.axes
            },
        )

    # -- basic accessors ------------------------------------------------------

    @property
    def name(self) -> str:
        return self.doc.meta.dimension

    @property
    def backbone(self) -> "Ontology | None":
        """The axis carrying the pins, or ``None`` for a dimension of pure axes."""
        return self.axes.get(self.doc.backbone) if self.doc.backbone else None

    def spec(self, axis: str) -> AxisSpec:
        return self.doc.spec(axis)

    def axis(self, axis: str) -> Ontology:
        return self.axes[axis]

    def _node(self, node_id: str) -> Node:
        bb = self.backbone
        if bb is None:
            raise ValueError(f"{self.name} has no backbone axis to resolve against")
        return bb.node(node_id)

    def parent_ids(self, node_id: str) -> "list[str]":
        """Parents in authored order, falling back to derived adjacency."""
        bb = self.backbone
        assert bb is not None
        node = bb.node(node_id)
        return list(node.parent_ids) if node.parent_ids else bb.parents(node_id)

    # -- the chain values travel along ---------------------------------------

    def value_parents(self, node_id: str) -> "list[str]":
        """Parents that axis values flow along.

        A multi-parent node often sits under one family it genuinely descends
        from and another it merely relates to, and inheriting from both
        manufactures contradictions the node then has to deny. ``value_parent``
        names the one values come from; the others still carry membership for
        roll-up. It is declared, never inferred from parent order.
        """
        node = self._node(node_id)
        if node.value_parent:
            return [node.value_parent]
        return self.parent_ids(node_id)

    def chain(self, node_id: str) -> "list[str]":
        """The node and its value-bearing ancestors, nearest first.

        The traversal is declared per dimension (``chain_order``): on a
        multi-parent node, breadth-first and depth-first order the chain
        differently and therefore disagree about which value is "nearest".
        """
        if self.doc.chain_order == "depth-first":
            ordered: "list[str]" = []
            seen: "set[str]" = set()

            def walk(cur: str) -> None:
                if cur in seen:
                    return
                seen.add(cur)
                ordered.append(cur)
                for parent in self.value_parents(cur):
                    walk(parent)

            walk(node_id)
            return ordered

        out: "list[str]" = []
        queue = [node_id]
        while queue:
            cur = queue.pop(0)
            if cur in out:
                continue
            out.append(cur)
            queue.extend(self.value_parents(cur))
        return out

    # -- pins -----------------------------------------------------------------

    def pin_items(self, node_id: str, axis: str) -> "list[str]":
        """A node's own pins on *axis*, as the source table wrote them."""
        return list(self._node(node_id).axes.get(axis, []))

    def pins(self, node_id: str, axis: str) -> "list[str]":
        """A node's own pins flattened to values, ``!`` prefixes kept.

        On a pair axis, a cell holding any pair contributes its members and its
        denials and **nothing else**: a bare value written alongside a pair says
        nothing about which term it belongs to, so it is not a value — it is an
        unpaired leftover, which the audit reports.
        """
        items = self.pin_items(node_id, axis)
        if not self.spec(axis).pairs or not any("(" in it for it in items):
            return items
        out: "list[str]" = []
        for item in items:
            term = parse_term(item)
            if term is not None:
                out.extend(sorted(term[0] | term[1]))
        out.extend(it for it in items if it.startswith("!"))
        return out

    # -- axis-value helpers ---------------------------------------------------

    def family(self, axis: str, value_id: str) -> str:
        """The top-level ancestor of an axis value: what carries its metadata."""
        onto = self.axes[axis]
        cur = value_id
        seen = {cur}
        while cur in onto:
            node = onto.node(cur)
            parents = node.parent_ids or onto.parents(cur)
            if not parents or parents[0] in seen:
                return cur
            cur = parents[0]
            seen.add(cur)
        return cur

    def _family_prop(self, axis: str, value_id: str, key: str) -> str:
        onto = self.axes[axis]
        fam = self.family(axis, value_id)
        if fam not in onto:
            return ""
        return onto.node(fam).props.get(key, "").strip()

    def cardinality(self, axis: str, value_id: str) -> str:
        return self._family_prop(axis, value_id, "cardinality")

    def default(self, axis: str, value_id: str) -> str:
        return self._family_prop(axis, value_id, "default")

    def scope(self, axis: str, value_id: str) -> str:
        return self._family_prop(axis, value_id, "scope")

    def _subsume(self, axis: str, values: "set[str]") -> "set[str]":
        """Drop any value a more specific resolved value already implies."""
        keep = set(values)
        for value in values:
            cur = value
            seen = {cur}
            while True:
                fam_step = self.family(axis, cur)
                onto = self.axes[axis]
                if cur not in onto:
                    break
                node = onto.node(cur)
                parents = node.parent_ids or onto.parents(cur)
                if not parents or parents[0] in seen:
                    break
                cur = parents[0]
                seen.add(cur)
                keep.discard(cur)
                del fam_step
        return keep

    # -- resolution -----------------------------------------------------------

    def effective(self, node_id: str, axis: str) -> "tuple[set[str], list[str]]":
        """Resolved values for *node_id* on *axis*, plus any ambiguity found."""
        values, notes = self._effective_ordered(node_id, axis)
        return set(values), notes

    def _effective_ordered(
        self, node_id: str, axis: str
    ) -> "tuple[list[str], list[str]]":
        """Resolved values in nearest-first order, for the ``nearest`` mode."""
        spec = self.spec(axis)
        chain = self.chain(node_id)
        notes: "list[str]" = []

        if spec.deny == "chain":
            blocked = {
                v[1:] for n in chain for v in self.pins(n, axis) if v.startswith("!")
            }
            asserted: "dict[str, int]" = {}
            ordered: "list[str]" = []
            for depth, n in enumerate(chain):
                for v in self.pins(n, axis):
                    if v.startswith("!") or v in blocked or v in asserted:
                        continue
                    asserted[v] = depth
                    ordered.append(v)
            denied: "set[str]" = set()
        else:
            # Nearest statement wins between asserting and denying a value. A
            # denial means "this does not apply here", so it governs what it
            # inherits -- not what a more specific descendant goes on to assert
            # about itself.
            asserted = {}
            denied_at: "dict[str, int]" = {}
            ordered = []
            for depth, n in enumerate(chain):
                for v in self.pins(n, axis):
                    if v.startswith("!"):
                        denied_at.setdefault(v[1:], depth)
                    elif v not in asserted:
                        asserted[v] = depth
                        ordered.append(v)
            for v, d in asserted.items():
                if denied_at.get(v) == d:
                    notes.append(
                        f"{node_id}: {v} is both asserted and denied at the same node"
                    )
            live = {
                v for v, d in asserted.items() if v not in denied_at or d < denied_at[v]
            }
            ordered = [v for v in ordered if v in live]
            asserted = {v: d for v, d in asserted.items() if v in live}
            denied = {v for v in denied_at if v not in live}

        if spec.inherit == "nearest":
            # Single-valued for the whole axis: the nearest ancestor that pins it
            # wins, and only its first value. Reproduces the models semantics.
            if not ordered:
                return [], notes
            nearest = min(asserted[v] for v in ordered)
            first = [v for v in ordered if asserted[v] == nearest][:1]
            return first, notes

        if spec.inherit != "nearest-in-family":
            flat = set(ordered)
            if spec.subsume:
                flat = self._subsume(axis, flat)
            return [v for v in ordered if v in flat], notes

        # nearest-in-family: union across families, nearest wins within one.
        onto = self.axes[axis]
        per_family: "dict[str, list[tuple[int, str]]]" = {}
        for v in ordered:
            if v in onto:
                per_family.setdefault(self.family(axis, v), []).append((asserted[v], v))

        resolved: "set[str]" = set()
        for fam, hits in per_family.items():
            card = (
                onto.node(fam).props.get("cardinality", "").strip()
                if fam in onto
                else ""
            )
            if card == "many" and spec.many_inherit == "chain":
                # The family is explicitly multi-valued, so a value inherited
                # from further up is not competing with one pinned here -- both
                # hold. Restricting to the nearest depth is what dropped one of
                # EGNN's two real equivariances.
                resolved.update(v for _, v in hits)
                continue
            nearest = min(d for d, _ in hits)
            at_front = sorted({v for d, v in hits if d == nearest})
            if len(at_front) > 1 and card != "many":
                # never settle this by column order; that is the models defect
                notes.append(
                    f"{node_id}: family {fam} resolves to {at_front} at equal depth"
                    f" and cardinality is {card or 'undeclared'}"
                )
            resolved.update(at_front)

        resolved -= denied
        if spec.subsume:
            resolved = self._subsume(axis, resolved)
        return [v for v in ordered if v in resolved], notes

    def families(self, node_id: str, axis: str) -> "dict[str, FamilyValue]":
        """Every family of *axis*, and what *node_id* says about it.

        Covers families the node resolves to **and** families it does not, since
        the whole point of the distinction is what a blank means. Keyed by
        family id.
        """
        onto = self.axes[axis]
        values, _ = self.effective(node_id, axis)
        by_family: "dict[str, set[str]]" = {}
        for value in values:
            if value in onto:
                by_family.setdefault(self.family(axis, value), set()).add(value)

        denied = {
            v[1:]
            for n in self.chain(node_id)
            for v in self.pins(n, axis)
            if v.startswith("!")
        }

        out: "dict[str, FamilyValue]" = {}
        for family in onto.roots:
            props = onto.node(family).props
            default = props.get("default", "").strip()
            scope = props.get("scope", "").strip()
            found = by_family.get(family, set())
            if found:
                state = "stated"
            elif default and default in denied:
                state = "absent"
            elif default:
                state = "default"
            else:
                state = "unknown"
            out[family] = FamilyValue(
                family=family,
                values=frozenset(found),
                state=state,
                default=default,
                scope=scope,
            )
        return out

    def resolved_order(self, node_id: str, axis: str) -> "list[str]":
        """Resolved values, nearest-first, as the design scripts returned them."""
        return self._effective_ordered(node_id, axis)[0]

    def terms(
        self, node_id: str, axis: str
    ) -> "list[tuple[frozenset[str], frozenset[str]]]":
        """The objective terms a node resolves to, on a pair axis.

        Terms inherit *as terms*: a descendant that states none of its own takes
        its nearest ancestor's. They are not unioned down the chain, because a
        descendant that restates its terms is replacing them, not adding to them.
        """
        if not self.spec(axis).pairs:
            return []
        chain = self.chain(node_id)
        denied = {
            v[1:] for n in chain for v in self.pin_items(n, axis) if v.startswith("!")
        }
        for n in chain:
            found = [t for t in map(parse_term, self.pin_items(n, axis)) if t]
            if not found:
                continue
            out: "list[tuple[frozenset[str], frozenset[str]]]" = []
            for src, form in found:
                s, f = src - denied, form - denied
                if s and f:
                    out.append((frozenset(s), frozenset(f)))
            return out
        return []

    def conflicting_parents(self, node_id: str) -> "list[str]":
        """Where a multi-parent node's parents disagree, so a choice is required.

        Two parents conflict when one asserts a value another denies, or when
        they land two values in the same single-valued family. When they agree
        the union is unambiguous and no declaration is needed -- explicitness is
        required exactly where ambiguity exists, not everywhere.
        """
        parents = self.parent_ids(node_id)
        if len(parents) < 2 or self._node(node_id).value_parent:
            return []
        found: "list[str]" = []
        for axis in self.doc.pinned_axes:
            onto = self.axes[axis]
            sets: "dict[str, set[str]]" = {}
            denied: "dict[str, set[str]]" = {}
            for p in parents:
                vals = {v for n in self.chain(p) for v in self.pins(n, axis)}
                sets[p] = {v for v in vals if not v.startswith("!")}
                denied[p] = {v[1:] for v in vals if v.startswith("!")}
            for a in parents:
                for b in parents:
                    if a < b and (sets[a] & denied[b] or sets[b] & denied[a]):
                        found.append(f"{axis}: {a} asserts what {b} denies")
            if self.spec(axis).inherit != "nearest-in-family":
                continue
            families = {
                self.family(axis, v) for p in parents for v in sets[p] if v in onto
            }
            for fam in families:
                if (
                    fam in onto
                    and onto.node(fam).props.get("cardinality", "").strip() == "many"
                ):
                    continue
                seen = {
                    frozenset(
                        v for v in sets[p] if v in onto and self.family(axis, v) == fam
                    )
                    for p in parents
                }
                if len({s for s in seen if s}) > 1:
                    found.append(
                        f"{axis}: parents disagree in single-valued family {fam}"
                    )
        return found

    # -- composites -----------------------------------------------------------

    def expand(self, node_id: str) -> "set[str]":
        """Every node a composite decomposes into, transitively.

        What makes ``RLHF`` and ``SFT + reward model + PPO`` roll up identically.
        Returns the empty set for a node that is not a composite, and never
        includes the node itself.
        """
        out: "set[str]" = set()
        queue = list(self._node(node_id).expands_to)
        while queue:
            cur = queue.pop()
            if cur in out or cur == node_id:
                continue
            out.add(cur)
            bb = self.backbone
            assert bb is not None
            if cur in bb:
                queue.extend(bb.node(cur).expands_to)
        return out

    # -- integrity ------------------------------------------------------------

    def check_integrity(self) -> "list[str]":
        """Problems the *conversion* could introduce, reported not raised.

        Deliberately narrow. The semantic audits that found the real design
        defects live with the authored tables
        (``axes_algorithms/resolve.py --audit``) and still run against them; what
        cannot be checked there is whether the trip through this format preserved
        what they checked. So this covers exactly that: the redundancy between
        authored parent order and derived adjacency, pins naming values that
        exist, a declared ``value_parent`` that is really a parent, and
        expansions naming nodes rather than prose.
        """
        problems: "list[str]" = []
        for axis, onto in self.axes.items():
            for nid, node in onto.nodes.items():
                if node.parent_ids and sorted(node.parent_ids) != sorted(
                    onto.parents(nid)
                ):
                    problems.append(
                        f"PARENTS  {axis}/{nid}: authored {node.parent_ids} "
                        f"disagrees with adjacency {onto.parents(nid)}"
                    )
                for pid in node.parent_ids:
                    if pid not in onto:
                        problems.append(f"DANGLING {axis}/{nid} -> {pid}")

        bb = self.backbone
        if bb is None:
            return problems

        for nid, node in bb.nodes.items():
            if node.value_parent and node.value_parent not in self.parent_ids(nid):
                problems.append(
                    f"BAD VALUE_PARENT  {nid}: {node.value_parent} is not among "
                    f"its parents"
                )
            for axis in self.doc.pinned_axes:
                onto = self.axes[axis]
                for value in self.pins(nid, axis):
                    bare = value[1:] if value.startswith("!") else value
                    if bare not in onto:
                        problems.append(
                            f"UNKNOWN  {nid}.{axis} pins {value!r}, which is not "
                            f"a node on that axis"
                        )
            for part in node.expands_to:
                if part not in bb:
                    problems.append(
                        f"PROSE EXPANSION  {nid}: expands_to names {part!r}, "
                        f"which is not a node_id"
                    )
        return problems

    def backbone_nodes(self) -> "Iterator[str]":
        bb = self.backbone
        if bb is None:
            return iter(())
        return iter(bb.nodes)
