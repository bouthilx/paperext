"""Edge-case coverage for the ontology mutation API (WS-D D1a-2, #42).

Grouped by operation. Built TDD-style on top of the happy-path tests in
``test_mutation.py``; the ``tiny`` fixture lives in ``conftest.py``.
"""

import pytest

from paperext.ontology import Ontology
from paperext.ontology.ontology import CycleError, InvariantError, OntologyError
from paperext.ontology.schema import Meta, Node, NormRow, OntologyDoc

# =========================================================================== #
# create_node
# =========================================================================== #


def test_create_node_blank_id_rejected(tiny):
    # an empty or whitespace-only id is a degenerate key; reject it
    for bad in ("", "   "):
        before = tiny.doc.model_dump()
        with pytest.raises(InvariantError):
            tiny.create_node(bad, "X", parent="rl")
        assert tiny.doc.model_dump() == before


def test_create_node_examples_not_aliased(tiny):
    # the caller's list must be copied, not stored by reference
    caller = ["1234.5678"]
    tiny.create_node("dqn", "DQN", parent="rl", examples=caller)
    caller.append("leaked")
    assert tiny.examples("dqn") == ["1234.5678"]


def test_create_node_appends_at_end(tiny):
    # DFS order matters for roll-up; a new child lands last among siblings
    tiny.create_node("dqn", "DQN", parent="rl")
    assert tiny.children("rl") == ["ppo", "sac", "dqn"]
    tiny.create_node("newroot", "New Root")
    assert list(tiny.roots)[-1] == "newroot"


def test_create_node_reuses_deleted_id(tiny):
    tiny.remove_node("resnet")
    tiny.create_node("resnet", "ResNet (fresh)", parent="cnn")
    assert tiny.name("resnet") == "ResNet (fresh)"
    tiny.check_invariants()


def test_create_node_id_may_equal_a_surface_string(tiny):
    # ids and normalization surfaces are separate namespaces
    assert tiny.resolve("cnn") == "cnn"
    tiny.create_node("softactorcritic", "SAC group", parent="rl")  # a surface string
    assert "softactorcritic" in tiny
    assert tiny.resolve("Soft Actor-Critic") == "sac"  # surface still resolves
    tiny.check_invariants()


# =========================================================================== #
# rename
# =========================================================================== #


def test_rename_blank_name_rejected(tiny):
    before = tiny.doc.model_dump()
    with pytest.raises(InvariantError):
        tiny.rename("ppo", "   ")
    assert tiny.doc.model_dump() == before


def test_rename_leaves_surfaces_untouched(tiny):
    # documented contract: rename changes the display name only. The old name's
    # seed surface keeps resolving; the new name does NOT resolve until added.
    assert tiny.resolve("CNN") == "cnn"
    tiny.rename("cnn", "Convolutional Neural Network")
    assert tiny.resolve("CNN") == "cnn"  # old surface intact
    assert (
        tiny.resolve("Convolutional Neural Network") is None
    )  # new name not a surface
    # and the caller can opt in explicitly
    tiny.add_surface("Convolutional Neural Network", "cnn")
    assert tiny.resolve("Convolutional Neural Network") == "cnn"


def test_rename_changes_rollup_label_and_key(tiny):
    from paperext.ontology import to_category_map

    # at depth 2, resnet rolls up to its parent's *name*
    assert to_category_map(tiny, 2)["resnet"] == "CNN"
    tiny.rename("cnn", "ConvNet")
    m = to_category_map(tiny, 2)
    assert m["resnet"] == "ConvNet"  # label follows the rename
    # the node's own roll-up key is its normalized name, which also moved
    assert "convnet" in m and "cnn" not in m


def test_rename_to_same_name_is_noop(tiny):
    tiny.rename("ppo", "PPO")
    assert tiny.name("ppo") == "PPO"
    tiny.check_invariants()


def test_rename_into_name_collision_dedups_in_rollup(tiny):
    from paperext.ontology import to_category_map

    # sac now normalizes to the same key as ppo; roll-up must not crash
    tiny.rename("sac", "ppo")
    tiny.check_invariants()  # names aren't invariant-constrained
    m = to_category_map(tiny, 1)
    assert m["ppo"] == "algorithms"  # single deduped key, both under algorithms


def test_rename_root_to_drop_name_drops_its_subtree(tiny):
    from paperext.ontology import to_category_map

    assert "resnet" in to_category_map(tiny, 1)
    tiny.rename("nn", "ignore")  # top-level name now a drop root
    m = to_category_map(tiny, 1)
    assert "resnet" not in m and "cnn" not in m
