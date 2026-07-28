"""Layered ontology model for category mapping (WS-D D1a, #36).

This package separates the two jobs the legacy ``data/categorized_*.json`` trees
conflated: folding surface variants (**normalization**) and organizing concepts
into a hierarchy (**ontology**). See ``d1-ontology-plan.md`` / issue #36.

Layers::

    raw name -> [normalization] -> canonical id -> [ontology] -> node
             -> [roll-up to cut] -> category

D1a (this package) ships the data model, the read/index/accessor object, the
roll-up converter that reproduces :func:`paperext.analysis.rollup.build_category_map`
exactly, and the faithful ``v0`` migration of the three legacy trees. The LLM
categorization agent (D1b) and the mutation API (D1a-2) build on top of this.
"""

from paperext.ontology.ontology import Ontology
from paperext.ontology.rollup import to_category_map
from paperext.ontology.schema import Meta, Node, NormRow, OntologyDoc

__all__ = [
    "Ontology",
    "OntologyDoc",
    "Node",
    "Meta",
    "NormRow",
    "to_category_map",
]
