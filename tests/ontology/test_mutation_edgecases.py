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
