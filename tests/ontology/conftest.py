"""Shared fixtures for the ontology tests."""

import pytest

from paperext.ontology import Ontology
from paperext.ontology.schema import Meta, Node, NormRow, OntologyDoc


@pytest.fixture
def tiny() -> Ontology:
    """A small, valid ontology mirroring the shape of the legacy trees."""
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["algorithms", "nn", "ignore"],
        nodes={
            "algorithms": Node(name="algorithms", children=["rl"]),
            "rl": Node(name="reinforcement learning", children=["ppo", "sac"]),
            "ppo": Node(name="PPO"),
            "sac": Node(name="Soft Actor-Critic"),
            "nn": Node(name="neural networks", children=["cnn"]),
            "cnn": Node(name="CNN", children=["resnet"], examples=["1512.03385"]),
            "resnet": Node(name="ResNet"),
            "ignore": Node(name="ignore", children=["junk"]),
            "junk": Node(name="junk"),
        },
    )
    norm = [
        NormRow(surface="ppo", canonical="ppo"),
        NormRow(surface="proximalpolicyoptimization", canonical="ppo"),
        NormRow(surface="softactorcritic", canonical="sac"),
        NormRow(surface="cnn", canonical="cnn"),
        NormRow(surface="resnet", canonical="resnet"),
    ]
    o = Ontology(doc, norm)
    o.check_invariants()
    return o
