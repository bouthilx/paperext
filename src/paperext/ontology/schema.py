"""On-disk schema for the layered ontology (WS-D D1a, #36).

Two artifacts per versioned snapshot, under ``data/ontology/<dim>/v<N>/``:

- ``ontology.json`` — :class:`OntologyDoc`: id-keyed :class:`Node` map (adjacency
  via ``children``) plus an ordered ``roots`` list and ``meta``. A node id listed
  under more than one parent is a DAG edge — the format allows it; single-primary
  is the convention until DAG counting is activated.
- ``normalization.jsonl`` — one :class:`NormRow` per line: a surface form and the
  single canonical node id it resolves to. Strictly surface -> one canonical;
  ambiguous bare surfaces are left out (never guessed).

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
    """

    name: str
    description: str = ""
    examples: list[str] = Field(default_factory=list)
    children: list[str] = Field(default_factory=list)


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
