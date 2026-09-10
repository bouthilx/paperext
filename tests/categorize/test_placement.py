"""Placement: the one shared definition of "where did this name end up" (#51)."""

import pytest

from paperext.categorize.actions import (
    AddSurface,
    CreateNode,
    Decision,
    InsertAbove,
    Move,
    Outcome,
)
from paperext.categorize.placement import (
    placement_for_new,
    resolve_placement,
    to_placement,
)
from paperext.ontology.ontology import UnknownNodeError


def test_existing_node(tiny, tiny_cut):
    placement = to_placement(tiny, "resnet50", tiny_cut)
    assert placement.node_id == "resnet50"
    assert placement.parent_id == "resnet"
    assert placement.ancestor_path == ["nn", "cnn", "resnet", "resnet50"]
    assert placement.ancestor_names == ["neural networks", "CNN", "ResNet", "ResNet-50"]
    assert placement.branch == "neural networks"
    assert placement.cut_category == "CNN"
    assert placement.depth == 4


def test_root_is_its_own_branch(tiny, tiny_cut):
    placement = to_placement(tiny, "nn", tiny_cut)
    assert placement.parent_id is None
    assert placement.branch == "neural networks"
    assert placement.cut_category == "Other"  # above every cut point


def test_nodes_under_a_dropped_root_have_no_category(tiny, tiny_cut):
    """Distinct from rolling up to ``Other``: an ignored node counts nowhere."""
    assert to_placement(tiny, "junk", tiny_cut).cut_category is None


def test_new_node_is_not_placed_like_its_parent_under_a_depth_cut(tiny):
    """Why :func:`placement_for_new` exists at all.

    Under a depth cut a new child sits one level deeper than its parent, so
    reusing the parent's placement would record the wrong category.
    """
    parent = to_placement(tiny, "nn", 2)
    child = placement_for_new(tiny, "nn", "BiT-S-101", 2)
    assert parent.cut_category == "neural networks"
    assert child.cut_category == "BiT-S-101"
    assert child.node_id is None
    assert child.parent_id == "nn"
    assert child.depth == parent.depth + 1


def test_new_root(tiny):
    placement = placement_for_new(tiny, None, "world models", 2)
    assert placement.parent_id is None
    assert placement.branch == "world models"
    assert placement.ancestor_path == []


def test_unknown_ids_raise_the_ontology_error(tiny, tiny_cut):
    with pytest.raises(UnknownNodeError):
        to_placement(tiny, "nope", tiny_cut)
    with pytest.raises(UnknownNodeError):
        placement_for_new(tiny, "nope", "X", tiny_cut)


# --------------------------------------------------------------------------- #
# resolve_placement — read off the decision, against the pre-decision tree
# --------------------------------------------------------------------------- #


def _mapping(surface, canonical):
    return AddSurface(
        justification="j", confidence=1.0, surface=surface, canonical=canonical
    )


def test_mapping_onto_an_existing_node(tiny, tiny_cut):
    decision = Decision(
        surface="vision transformer",
        outcome=Outcome.MAPPED,
        confidence=0.9,
        actions=[_mapping("vision transformer", "vit")],
    )
    placement = resolve_placement(tiny, decision, tiny_cut)
    assert placement.node_id == "vit"
    assert placement.cut_category == "transformer"


def test_creating_the_node_the_same_decision_maps_to(tiny, tiny_cut):
    """The created node does not exist yet, so the placement comes from the op."""
    decision = Decision(
        surface="BiT-S-101",
        outcome=Outcome.CREATED,
        confidence=0.8,
        actions=[
            CreateNode(
                justification="ResNetv2-101 backbone",
                confidence=0.8,
                node_id="bits101",
                name="BiT-S-101",
                parent="cnn",
            ),
            _mapping("BiT-S-101", "bits101"),
        ],
    )
    placement = resolve_placement(tiny, decision, tiny_cut)
    assert placement.node_id is None
    assert placement.parent_id == "cnn"
    assert placement.cut_category == "CNN"


def test_insert_above_creates_the_target_too(tiny, tiny_cut):
    decision = Decision(
        surface="big transfer",
        outcome=Outcome.CREATED,
        confidence=0.7,
        actions=[
            InsertAbove(
                justification="ResNet is one of several residual nets",
                confidence=0.7,
                node_id="resnet",
                new_id="residual",
                name="residual networks",
            ),
            _mapping("big transfer", "residual"),
        ],
    )
    placement = resolve_placement(tiny, decision, tiny_cut)
    assert placement.parent_id == "cnn"
    assert placement.cut_category == "CNN"


def test_no_placement_when_nothing_is_mapped(tiny, tiny_cut):
    """Abstentions, no-ops and pure in-flight fixes all place nothing."""
    for decision in (
        Decision(surface="sam", outcome=Outcome.ABSTAINED, confidence=0.2),
        Decision(surface="ppo", outcome=Outcome.NO_OP, confidence=0.9),
        Decision(
            surface="ppo",
            outcome=Outcome.NO_OP,
            confidence=0.9,
            actions=[
                Move(
                    justification="misplaced",
                    confidence=0.6,
                    node_id="sam",
                    new_parent="nn",
                )
            ],
        ),
    ):
        assert resolve_placement(tiny, decision, tiny_cut) is None


def test_a_surface_for_another_name_does_not_count_as_the_placement(tiny, tiny_cut):
    """Only the ``add_surface`` naming *this* decision's surface fixes the target."""
    decision = Decision(
        surface="BiT-S-101",
        outcome=Outcome.MAPPED,
        confidence=0.6,
        actions=[_mapping("some other alias", "vit")],
    )
    assert resolve_placement(tiny, decision, tiny_cut) is None
