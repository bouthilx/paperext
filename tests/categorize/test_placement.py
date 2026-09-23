"""Placement: the one shared definition of "where did this name end up" (#51)."""

import pytest
from pydantic import ValidationError

from paperext.categorize.actions import (
    AddSurface,
    CreateNode,
    Decision,
    DemoteToVariant,
    InsertAbove,
    Move,
    Outcome,
    Rename,
)
from paperext.categorize.placement import (
    load_dimension_cut,
    placement_for_new,
    resolve_placement,
    to_placement,
)
from paperext.ontology.ontology import UnknownNodeError
from paperext.ontology.rollup import (
    NodeCut,
    UnresolvedCutError,
    resolve_cut,
    to_category_map,
)


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
    """Abstentions, no-ops and pure fixes on an *unmapped* name place nothing."""
    for decision in (
        Decision(surface="sam2", outcome=Outcome.ABSTAINED, confidence=0.2),
        Decision(surface="BiT", outcome=Outcome.NO_OP, confidence=0.9),
        Decision(
            surface="BiT",
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


def test_an_already_mapped_name_is_placed_where_it_sits(tiny, tiny_cut):
    """A ``no_op`` on a name the tree already has is a placement, not a blank (#67).

    The 9-of-10 case from the first run over already-mapped items: the model adds
    no duplicate surface, and the report still has to say where the name lives.
    """
    for decision in (
        Decision(surface="ppo", outcome=Outcome.NO_OP, confidence=0.9),
        Decision(
            surface="ppo",
            outcome=Outcome.NO_OP,
            confidence=0.9,
            actions=[
                Rename(
                    node_id="ppo", new_name="PPO!", justification="j", confidence=0.9
                )
            ],
        ),
    ):
        placement = resolve_placement(tiny, decision, tiny_cut)
        assert placement is not None and placement.node_id == "ppo"
        assert placement.cut_category == "Other"
    # ablated in the eval: the surface no longer resolves, so nothing is placed
    tiny.remove_surface("ppo")
    assert (
        resolve_placement(
            tiny,
            Decision(surface="ppo", outcome=Outcome.NO_OP, confidence=0.9),
            tiny_cut,
        )
        is None
    )


def test_a_surface_for_another_name_does_not_count_as_the_placement(tiny, tiny_cut):
    """Only the ``add_surface`` naming *this* decision's surface fixes the target."""
    decision = Decision(
        surface="BiT-S-101",
        outcome=Outcome.NO_OP,
        confidence=0.6,
        actions=[_mapping("some other alias", "vit")],
    )
    assert resolve_placement(tiny, decision, tiny_cut) is None


def test_outcome_must_match_the_actions(tiny):
    """#67: the outcome is a claim about the actions, and the model gets told which."""
    with pytest.raises(ValidationError, match="the outcome is 'no_op'"):
        Decision(surface="ppo", outcome=Outcome.MAPPED, confidence=0.9)
    with pytest.raises(ValidationError, match="make it 'created'"):
        Decision(
            surface="bit",
            outcome=Outcome.MAPPED,
            confidence=0.9,
            actions=[
                CreateNode(
                    node_id="bit",
                    name="BiT",
                    parent="cnn",
                    justification="j",
                    confidence=0.9,
                ),
                _mapping("bit", "bit"),
            ],
        )
    with pytest.raises(ValidationError, match="that is 'mapped'"):
        Decision(
            surface="bit",
            outcome=Outcome.NO_OP,
            confidence=0.9,
            actions=[_mapping("bit", "vit")],
        )
    # folding a duplicate away is an in-flight fix, not a mapping: the surface
    # already resolved, so the honest outcome is no_op. (The MHR case that
    # deadlocked a live run: the model would not say 'mapped', and was right.)
    fold = [
        DemoteToVariant(
            node_id="resnet50",
            target_id="resnet",
            justification="j",
            confidence=0.9,
        )
    ]
    Decision(surface="resnet50", outcome=Outcome.NO_OP, confidence=0.9, actions=fold)
    with pytest.raises(ValidationError, match="the outcome is 'no_op'"):
        Decision(
            surface="resnet50", outcome=Outcome.MAPPED, confidence=0.9, actions=fold
        )
    # the runner's own label is not second-guessed
    Decision(surface="x", outcome=Outcome.FAILED, confidence=0.0)


# --------------------------------------------------------------------------- #
# id-keyed cuts (#62): renaming a cut node relabels its category, never empties it
# --------------------------------------------------------------------------- #


def test_cut_survives_renaming_a_cut_node(tiny, tiny_cut):
    cut = resolve_cut(tiny, tiny_cut)
    assert isinstance(cut, NodeCut) and cut.ids == {"cnn", "transformer"}

    tiny.rename("cnn", "Convolutional Neural Network (CNN)")
    placement = to_placement(tiny, "resnet50", cut)
    assert placement.cut_category == "Convolutional Neural Network (CNN)"
    assert to_placement(tiny, "vit", cut).cut_category == "transformer"
    # the label follows the name, so the map is the same partition, relabelled
    m = to_category_map(tiny, cut)
    assert m["resnet"] == m["resnet50"] == "Convolutional Neural Network (CNN)"
    assert m["ppo"] == "Other"


def test_name_cut_against_a_renamed_tree_fails_loudly(tiny, tiny_cut):
    """The old failure mode: a stale name path silently sent a branch to Other."""
    tiny.rename("cnn", "Convolutional Neural Network (CNN)")
    with pytest.raises(UnresolvedCutError, match="neuralnetworks.cnn"):
        to_placement(tiny, "resnet50", tiny_cut)


def test_new_node_rolls_up_to_its_nearest_cut_ancestor(tiny, tiny_cut):
    """A node that does not exist yet has no id, so it cannot be a cut node."""
    assert placement_for_new(tiny, "cnn", "BiT", tiny_cut).cut_category == "CNN"
    assert placement_for_new(tiny, "nn", "BiT", tiny_cut).cut_category == "Other"
    # ... even when it is named exactly like a cut entry
    assert placement_for_new(tiny, "nn", "CNN", tiny_cut).cut_category == "Other"


def test_resolve_cut_passes_depths_and_resolved_cuts_through(tiny, tiny_cut):
    assert resolve_cut(tiny, 2) == 2
    cut = resolve_cut(tiny, tiny_cut)
    assert resolve_cut(tiny, cut) is cut
    with pytest.raises(TypeError):
        resolve_cut(tiny, True)
    with pytest.raises(ValueError):
        resolve_cut(tiny, 0)


def test_dimension_cut_is_resolved_against_the_frozen_base():
    """The milabench file is spelled in ``v0`` names; ids are what a run keeps."""
    cut = load_dimension_cut("models")
    assert isinstance(cut, NodeCut)
    assert "convolutionalneuralnetwork" in cut.ids and "transformer" in cut.ids
    assert load_dimension_cut("test") == 2
