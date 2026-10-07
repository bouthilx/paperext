"""Layered ontology model for category mapping (WS-D D1a, #36).

This package separates the two jobs the legacy ``data/categorized_*.json`` trees
conflated: folding surface variants (**normalization**) and organizing concepts
into a hierarchy (**ontology**). See ``d1-ontology-plan.md`` / issue #36.

Layers::

    raw name -> [normalization] -> canonical id -> [ontology] -> node
             -> [roll-up to cut] -> category

D1a (this package) ships the data model, the read/index/accessor object, its
mutation API + invariants (D1a-2), the roll-up converter that reproduces
:func:`paperext.analysis.rollup.build_category_map` exactly, and the faithful
``v0`` migration of the three legacy trees. The LLM categorization agent (D1b)
builds on top of this.

D1h (#100) makes the *derived* dimensions loadable through the same model:
:class:`~paperext.ontology.axes.Dimension` is one manifest plus one
:class:`Ontology` per axis, with the inheritance semantics declared per axis
rather than hard-coded, and
:func:`~paperext.ontology.rollup.to_category_sets` is the multi-parent
counterpart of :func:`~paperext.ontology.rollup.to_category_map` -- added
alongside it, because the flat map reproduces the legacy one and ``models/v0``
is still the sealed eval reference.
"""

from paperext.ontology.axes import Dimension
from paperext.ontology.ontology import (
    CycleError,
    DuplicateNodeError,
    InvariantError,
    Ontology,
    OntologyError,
    UnknownNodeError,
)
from paperext.ontology.rollup import (
    NodeCut,
    UnresolvedCutError,
    resolve_cut,
    to_category_map,
    to_category_sets,
)
from paperext.ontology.schema import (
    AxisSpec,
    DimensionDoc,
    Meta,
    Node,
    NormRow,
    OntologyDoc,
)

__all__ = [
    "Ontology",
    "Dimension",
    "DimensionDoc",
    "AxisSpec",
    "to_category_sets",
    "OntologyDoc",
    "Node",
    "Meta",
    "NormRow",
    "to_category_map",
    "NodeCut",
    "resolve_cut",
    "UnresolvedCutError",
    "OntologyError",
    "DuplicateNodeError",
    "UnknownNodeError",
    "CycleError",
    "InvariantError",
]
