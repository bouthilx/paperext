"""On-disk schema for the layered ontology (WS-D D1a #36, extended by D1h #100).

Two artifacts per versioned snapshot, under ``data/ontology/<dim>/v<N>/``:

- ``ontology.json`` — :class:`OntologyDoc`: id-keyed :class:`Node` map (adjacency
  via ``children``) plus an ordered ``roots`` list and ``meta``. A node id listed
  under more than one parent is a DAG edge — the format allows it; single-primary
  is the convention until DAG counting is activated.
- ``normalization.jsonl`` — one :class:`NormRow` per line: a surface form and the
  single canonical node id it resolves to. Strictly surface -> one canonical;
  ambiguous bare surfaces are left out (never guessed).

A **faceted** dimension (#100) adds one more, and one snapshot per axis:

- ``dimension.json`` — :class:`DimensionDoc`: which axis is the backbone, and for
  each axis how its values inherit. Each axis then has its own
  ``<axis>/ontology.json`` (+ optional ``<axis>/normalization.jsonl``), because a
  facet axis *is* a hierarchy and that is exactly what :class:`OntologyDoc`
  already models — so cuts, roll-up, the mutation API and the invariants all work
  per axis unchanged. A dimension with no backbone (domains: five independent
  axes) is the same shape with ``backbone`` left empty, not a special case.

Every field #100 adds to :class:`Node` is defaulted, so the committed ``v0``
documents of the three legacy trees validate against this schema untouched.

The models are deliberately permissive containers (no cross-object validation
here); structural invariants are enforced by the mutation API (D1a-2), and the
loader builds its indexes from these objects.
"""

from typing import Optional

from pydantic import BaseModel, Field


class Node(BaseModel):
    """A single ontology concept.

    ``children`` is an ordered list of node ids (adjacency). ``examples`` holds
    grounding evidence (e.g. paper ids). ``description`` is empty in ``v0`` and is
    bootstrapped during D1b.

    The remaining fields are for faceted dimensions (#100) and default to empty,
    so a legacy ``v0`` document is unaffected by their existence.
    """

    name: str
    description: str = ""
    examples: list[str] = Field(default_factory=list)
    children: list[str] = Field(default_factory=list)

    #: Axis pins carried by a *backbone* node: ``{axis_name: [item, ...]}``.
    #: Items are stored as the source table wrote them — one entry per
    #: top-level item, so a ``(sources, forms)`` pair survives as one item
    #: rather than being flattened into its members. A ``!``-prefixed item is a
    #: negative pin, which blocks a value the node would otherwise inherit.
    #: Read these through the dimension's resolver, not directly.
    axes: "dict[str, list[str]]" = Field(default_factory=dict)

    #: The node's parents **in the order the source table wrote them**.
    #:
    #: ``children`` adjacency stays the structural truth, but it is order-lossy:
    #: a node's parents are recovered by scanning every other node, so they come
    #: back in node order, not in the order the author wrote them. Several
    #: semantics follow the *first* parent — which family an axis value belongs
    #: to, which root a node sits under, where values come from when no
    #: ``value_parent`` is declared — so that order has to survive the trip to
    #: disk. The redundancy with ``children`` is deliberate and checked: the
    #: audit reports any disagreement rather than leaving it latent.
    #:
    #: Empty on a legacy ``v0`` document, where the single-primary convention
    #: makes the derived order unambiguous.
    parent_ids: "list[str]" = Field(default_factory=list)

    #: Which single parent axis values flow along, when a node has several.
    #: Declared, never inferred from the order of the parent list: deciding by
    #: column order made Flamingo a bidirectional encoder, and is a recorded
    #: defect. Empty means "all parents", which is correct whenever they agree.
    value_parent: str = ""

    #: ``method`` / ``bundle`` / ``pipeline`` for a backbone node. A ``pipeline``
    #: is what tells a consumer how many runs to expect.
    kind: str = ""

    #: Node ids a composite decomposes into, so that one paper naming the
    #: composite and another naming its parts roll up identically. Node ids, never
    #: prose — an expansion that cannot be rolled up has no reason to exist.
    expands_to: "list[str]" = Field(default_factory=list)

    #: Everything else the source table carried, verbatim and unparsed:
    #: ``characteristic``, ``positive_test``, ``negative_test``, ``notes``,
    #: ``relation``, ``depth``, ``oecd_code``, and — on an axis-value node —
    #: ``cardinality``, ``default`` and ``scope``.
    #:
    #: The table's own ``examples`` column lands here too, under ``examples``,
    #: rather than in :attr:`examples`: that field means grounding paper ids in
    #: ``v0`` and the column is illustrative prose. Merging them would conflate
    #: two different things under one name.
    props: "dict[str, str]" = Field(default_factory=dict)


class Meta(BaseModel):
    """Snapshot metadata."""

    version: str
    dimension: str


class OntologyDoc(BaseModel):
    """The full ``ontology.json`` document.

    ``roots`` is ordered and ``nodes`` preserves insertion order; together they
    fix a deterministic depth-first traversal used by the roll-up converter to
    reproduce the legacy map (order-sensitive dedup).
    """

    meta: Meta
    roots: list[str] = Field(default_factory=list)
    nodes: dict[str, Node] = Field(default_factory=dict)


class NormRow(BaseModel):
    """One surface -> canonical mapping in ``normalization.jsonl``.

    ``via`` records provenance (``seed`` = the surface is a node's own name in the
    faithful import; other values e.g. ``levenshtein`` come from later curation).
    ``flag`` optionally marks a row for review (e.g. an ambiguous surface).
    """

    surface: str
    canonical: str
    via: str = "seed"
    flag: Optional[str] = None


#: How an axis's values inherit down the backbone. Each mode exists because the
#: naive alternative produced a wrong answer on a real node:
#:
#: - ``union`` — a parent's coarse value and a child's refinement may both hold
#:   (``Convolution`` + ``Standard convolution``): the child refines rather than
#:   replaces. Safe because a family pins only what is true of every descendant.
#: - ``nearest`` — single-valued for the whole axis; the nearest ancestor that
#:   pins it wins. Picking by parent order made Flamingo a bidirectional encoder.
#: - ``nearest-in-family`` — union *across* families, nearest-ancestor-wins
#:   *within* one, governed by that family's declared ``cardinality``. Without it
#:   VQ-VAE resolved to Deterministic **and** Stochastic; with a blanket
#:   single-value rule, EGNN lost one of its two real equivariances.
#: - ``none`` — the axis carries no pins (every axis of a backbone-less
#:   dimension).
INHERIT_MODES = ("union", "nearest", "nearest-in-family", "none")


class AxisSpec(BaseModel):
    """One axis of a faceted dimension, and how its values resolve."""

    name: str
    inherit: str = "union"

    #: The cell carries ``(sources, forms)`` pairs rather than a flat value list.
    #: One pair is one objective term. Flattening them reintroduces the
    #: cross-product the pairs were built to kill — it licensed 390 combinations
    #: of which 147 were true.
    pairs: bool = False

    #: Id prefix per pair slot, in slot order, e.g. ``["S.src", "S.form"]``. What
    #: makes a misplaced value detectable: a form sitting in the source slot.
    pair_prefixes: "list[str]" = Field(default_factory=list)

    #: Values whose family declares no scope predicate are reported rather than
    #: given a default, because a scope predicate is prose and therefore not
    #: machine-checkable — the loader must not silently synthesise a default
    #: outside its family's scope.
    require_scope: bool = False

    #: How far a negative pin reaches.
    #:
    #: - ``nearest`` — the nearest statement about a value wins, assertion or
    #:   denial. A denial means "this does not apply here", so it governs what it
    #:   inherits, not what a more specific descendant goes on to assert about
    #:   itself. Without this a ``!R.fit.est`` on ``L.causal.struct`` silently
    #:   cancelled ``M.lingam``'s own pin and left it with no role at all.
    #: - ``chain`` — a denial anywhere in the chain blocks the value outright.
    #:   The original models semantics, kept declarable so that dimension's
    #:   resolved values are not changed by a loader rewrite.
    deny: str = "nearest"

    #: For a ``many``-cardinality family, how far the union reaches.
    #:
    #: - ``chain`` — every value the family collects anywhere up the chain. What
    #:   makes EGNN permutation- **and** Euclidean-equivariant when one is pinned
    #:   on the node and the other inherited, and V-Net concatenative-skip **and**
    #:   additive-residual.
    #: - ``nearest`` — only the values pinned at the nearest depth that supplies
    #:   the family, exactly as for a single-valued one. Declared because the
    #:   algorithms dimension resolves this way and its values must not change
    #:   under a loader rewrite.
    #:
    #: Only consulted when ``inherit`` is ``nearest-in-family``.
    many_inherit: str = "nearest"

    #: Whether a specific resolved value supersedes a resolved ancestor of
    #: itself. A family legitimately pinning the interior ``S.src.ext``
    #: ("external, unspecified") would otherwise push it back onto a leaf since
    #: given ``S.src.ext.obs``, and the leaf would resolve to both — the same
    #: claim, said twice, once worse. Off for models, which was built without it.
    subsume: bool = True


class DimensionDoc(BaseModel):
    """``dimension.json`` — the manifest of a faceted dimension.

    ``backbone`` names the axis whose nodes carry the pins (``lineage`` for models
    and algorithms). It is empty for a dimension that is only axes, with nothing
    to pin them on: domains is five independent axes, and a paper maps to a set of
    values on each.
    """

    meta: Meta
    backbone: str = ""
    axes: "list[AxisSpec]" = Field(default_factory=list)

    #: How the backbone's ancestors are visited when collecting pins.
    #:
    #: ``breadth-first`` takes all parents, then all grandparents; the recursive
    #: ``depth-first`` exhausts the first parent's ancestry before looking at the
    #: second. On a single-parent node the two agree; on a multi-parent one they
    #: order the chain differently, which changes which value is "nearest".
    #: Declared rather than chosen, because the two dimensions were built under
    #: different traversals and a loader must not silently re-resolve either.
    chain_order: str = "breadth-first"

    def spec(self, axis: str) -> AxisSpec:
        for spec in self.axes:
            if spec.name == axis:
                return spec
        raise KeyError(f"{axis!r} is not an axis of {self.meta.dimension}")

    @property
    def axis_names(self) -> "list[str]":
        return [spec.name for spec in self.axes]

    @property
    def pinned_axes(self) -> "list[str]":
        """Axes the backbone pins, i.e. every axis but the backbone itself."""
        return [spec.name for spec in self.axes if spec.name != self.backbone]
