"""Shared fixtures for the categorize tests (WS-D D1b-1, #51)."""

import pytest

from paperext.ontology import Ontology
from paperext.ontology.schema import Meta, Node, NormRow, OntologyDoc


@pytest.fixture
def tiny_cut() -> "list[str]":
    """A per-branch cut over :func:`tiny`, in the milabench dot-path spelling."""
    return ["neural networks.CNN", "neural networks.transformer"]


@pytest.fixture
def tiny() -> Ontology:
    """A small, valid ontology with the shapes the applier has to survive.

    Deliberately includes: two branches under one root (so a cut has something to
    separate), a cross-branch homonym (``sam``, as in the legacy trees), a node
    with a description and examples (so the ablation scrub has something to bite
    on), and an ``ignore`` root.
    """
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["algorithms", "nn", "ignore"],
        nodes={
            "algorithms": Node(name="algorithms", children=["rl", "sam"]),
            "rl": Node(name="reinforcement learning", children=["ppo"]),
            "ppo": Node(name="PPO"),
            "sam": Node(name="SAM"),
            "nn": Node(name="neural networks", children=["cnn", "transformer"]),
            "cnn": Node(
                name="CNN",
                children=["resnet"],
                description="Convolutional nets, e.g. ResNet-50 and VGG.",
                examples=["1512.03385", "ResNet-50 backbone"],
            ),
            "resnet": Node(name="ResNet", children=["resnet50"]),
            "resnet50": Node(name="ResNet-50"),
            "transformer": Node(name="transformer", children=["vit"]),
            "vit": Node(name="ViT"),
            "ignore": Node(name="ignore", children=["junk"]),
            "junk": Node(name="junk"),
        },
    )
    norm = [
        NormRow(surface="ppo", canonical="ppo"),
        NormRow(surface="proximalpolicyoptimization", canonical="ppo"),
        NormRow(surface="sam", canonical="sam"),
        NormRow(surface="cnn", canonical="cnn"),
        NormRow(surface="resnet", canonical="resnet"),
        NormRow(surface="resnet50", canonical="resnet50"),
        NormRow(surface="vit", canonical="vit"),
    ]
    o = Ontology(doc, norm)
    o.check_invariants()  # the fixture starts clean
    return o
