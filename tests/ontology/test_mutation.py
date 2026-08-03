"""Tests for the ontology mutation API + invariants (WS-D D1a-2, #42).

Three layers:

- **Ops** — each mutator does the right structural edit and re-indexes.
- **Rejection** — invariant violations raise and (for guarded ops) leave the
  object byte-unchanged; ``check_invariants`` catches a hand-corrupted tree.
- **Round-trip** — a mutated tree ``save``s and re-``load``s to an identical view.
"""

import pytest

from paperext.ontology import Ontology, to_category_map
from paperext.ontology.ontology import (
    CycleError,
    DuplicateNodeError,
    InvariantError,
    OntologyError,
    UnknownNodeError,
)
from paperext.ontology.schema import Meta, Node, NormRow, OntologyDoc


def _tiny() -> Ontology:
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
    o.check_invariants()  # fixture starts clean
    return o


# --------------------------------------------------------------------------- #
# Ops
# --------------------------------------------------------------------------- #


def test_create_node_child_and_root():
    o = _tiny()
    o.create_node("dqn", "DQN", parent="rl")
    assert o.children("rl") == ["ppo", "sac", "dqn"]
    assert o.parents("dqn") == ["rl"]
    o.create_node("meta", "meta-learning")
    assert "meta" in o.root_map()
    o.check_invariants()


def test_rename_and_update_description():
    o = _tiny()
    o.rename("ppo", "Proximal Policy Optimization")
    assert o.name("ppo") == "Proximal Policy Optimization"
    # renaming does not disturb existing surfaces
    assert o.resolve("ppo") == "ppo"
    o.update_description("ppo", "on-policy policy-gradient RL")
    assert o.node("ppo").description == "on-policy policy-gradient RL"


def test_add_and_remove_surface():
    o = _tiny()
    o.add_surface("PPO Clip", "ppo")
    assert o.resolve("PPO Clip") == "ppo"
    o.add_surface("ppo", "ppo")  # idempotent, no raise
    o.remove_surface("ppoclip")
    assert o.resolve("PPO Clip") is None
    o.check_invariants()


def test_move_reparents():
    o = _tiny()
    o.move("resnet", "rl")
    assert o.parents("resnet") == ["rl"]
    assert "resnet" not in o.children("cnn")
    assert o.ancestry("resnet") == ["algorithms", "rl", "resnet"]
    o.check_invariants()


def test_move_a_root_under_a_node():
    o = _tiny()
    o.move("nn", "algorithms")
    assert "nn" not in o.root_map()
    assert o.parents("nn") == ["algorithms"]
    o.check_invariants()


def test_insert_above_preserves_position():
    o = _tiny()
    # insert a "value-based" grouping above ppo's sibling sac
    o.create_node("v", "value-based", parent="rl")  # rl: ppo, sac, v
    o.insert_above("sac", "actor_critic", "actor-critic")
    # sac's slot in rl.children is now the new node, order preserved
    assert o.children("rl") == ["ppo", "actor_critic", "v"]
    assert o.children("actor_critic") == ["sac"]
    o.check_invariants()


def test_insert_above_root():
    o = _tiny()
    o.insert_above("nn", "models", "models")
    assert "models" in o.root_map() and "nn" not in o.root_map()
    assert o.children("models") == ["nn"]
    o.check_invariants()


def test_demote_to_variant_folds_surfaces():
    o = _tiny()
    # resnet is really a variant of cnn
    o.demote_to_variant("resnet", "cnn")
    assert "resnet" not in o
    # its own name + surfaces now resolve to cnn
    assert o.resolve("resnet") == "cnn"
    assert o.children("cnn") == []
    o.check_invariants()


def test_remove_node_cascades_surfaces():
    o = _tiny()
    o.remove_node("resnet")
    assert "resnet" not in o
    assert o.resolve("resnet") is None  # surface row cascaded away
    assert o.children("cnn") == []
    o.check_invariants()


def test_mark_ignore_moves_under_ignore_root_and_drops():
    o = _tiny()
    o.mark_ignore("cnn")  # cnn has child resnet -> both drop from roll-up
    assert o.root_of("cnn") == "ignore"
    m = to_category_map(o, 1)
    assert "cnn" not in m and "resnet" not in m
    o.check_invariants()


def test_mark_ignore_creates_ignore_root_when_absent():
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["nn"],
        nodes={
            "nn": Node(name="neural networks", children=["cnn"]),
            "cnn": Node(name="CNN"),
        },
    )
    o = Ontology(doc, [])
    o.mark_ignore("cnn")
    assert o.root_of("cnn") == "ignore"
    assert o.name("ignore") == "ignore"
    o.check_invariants()


# --------------------------------------------------------------------------- #
# Rejection: guarded ops raise and leave state unchanged
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "op",
    [
        lambda o: o.create_node("ppo", "dup"),  # duplicate id
        lambda o: o.create_node("x", "", parent="rl"),  # empty name
        lambda o: o.create_node("x", "X", parent="ghost"),  # unknown parent
        lambda o: o.add_surface("ppo", "sac"),  # 1:1 conflict (ppo owned by ppo)
        lambda o: o.add_surface("new", "ghost"),  # unknown canonical
        lambda o: o.remove_surface("nope"),  # unknown surface
        lambda o: o.rename("ghost", "X"),  # unknown node
        lambda o: o.move("rl", "ppo"),  # cycle: under own descendant
        lambda o: o.move("rl", "rl"),  # cycle: under self
        lambda o: o.move("ghost", "rl"),  # unknown node
        lambda o: o.insert_above("ppo", "rl", "dup"),  # duplicate new id
        lambda o: o.demote_to_variant("cnn", "algorithms"),  # cnn has a child
        lambda o: o.demote_to_variant("ppo", "ppo"),  # into itself
        lambda o: o.remove_node("cnn"),  # has a child
        lambda o: o.remove_node("ghost"),  # unknown node
    ],
)
def test_rejected_op_leaves_state_unchanged(op):
    o = _tiny()
    before_doc = o.doc.model_dump()
    before_norm = [r.model_dump() for r in o.norm]
    with pytest.raises(OntologyError):
        op(o)
    assert o.doc.model_dump() == before_doc
    assert [r.model_dump() for r in o.norm] == before_norm


def test_specific_exception_types():
    o = _tiny()
    with pytest.raises(DuplicateNodeError):
        o.create_node("ppo", "dup")
    with pytest.raises(UnknownNodeError):
        o.rename("ghost", "X")
    with pytest.raises(CycleError):
        o.move("rl", "ppo")


def test_demote_does_not_hijack_ambiguous_surface():
    # two "sam" nodes; the bare surface is owned by the algorithms one.
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["algorithms", "nn"],
        nodes={
            "algorithms": Node(name="algorithms", children=["sam"]),
            "sam": Node(name="SAM"),
            "nn": Node(name="neural networks", children=["sam2"]),
            "sam2": Node(name="SAM"),  # collision loser, surface-less
        },
    )
    o = Ontology(doc, [NormRow(surface="sam", canonical="sam")])
    o.demote_to_variant("sam2", "nn")  # fold the loser into nn
    # the bare 'sam' surface must still point at the original owner, not nn
    assert o.resolve("sam") == "sam"
    o.check_invariants()


# --------------------------------------------------------------------------- #
# Rejection: check_invariants catches a hand-corrupted tree
# --------------------------------------------------------------------------- #


def _bare(nodes, roots, norm=None):
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"), roots=roots, nodes=nodes
    )
    return Ontology(doc, norm or [])


def test_check_invariants_dangling_child():
    o = _bare({"a": Node(name="A", children=["ghost"])}, ["a"])
    with pytest.raises(InvariantError, match="unknown child"):
        o.check_invariants()


def test_check_invariants_dangling_canonical():
    o = _bare({"a": Node(name="A")}, ["a"], [NormRow(surface="s", canonical="ghost")])
    with pytest.raises(InvariantError, match="unknown node"):
        o.check_invariants()


def test_check_invariants_cycle():
    o = _bare(
        {"a": Node(name="A", children=["b"]), "b": Node(name="B", children=["a"])},
        ["a"],
    )
    with pytest.raises(CycleError):
        o.check_invariants()


def test_check_invariants_orphan():
    o = _bare(
        {"a": Node(name="A"), "orphan": Node(name="Orphan")},
        ["a"],  # orphan reachable from no root
    )
    with pytest.raises(InvariantError, match="orphan"):
        o.check_invariants()


def test_check_invariants_root_not_a_node():
    o = _bare({"a": Node(name="A")}, ["a", "ghost"])
    with pytest.raises(InvariantError, match="not a node"):
        o.check_invariants()


# --------------------------------------------------------------------------- #
# Round-trip: mutated tree save -> load is identical and clean
# --------------------------------------------------------------------------- #


def test_mutation_round_trip(tmp_path):
    o = _tiny()
    o.create_node("dqn", "DQN", parent="rl")
    o.add_surface("deep q-network", "dqn")
    o.move("resnet", "rl")
    o.demote_to_variant("junk", "ignore")
    o.remove_node("sac")

    before = to_category_map(o, 2)
    o.save(tmp_path)
    reloaded = Ontology.load(tmp_path)
    reloaded.check_invariants()
    assert to_category_map(reloaded, 2) == before
    assert reloaded.resolve("deep q-network") == "dqn"
    assert reloaded.doc.model_dump() == o.doc.model_dump()
