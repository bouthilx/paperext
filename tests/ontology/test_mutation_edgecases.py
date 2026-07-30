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


# =========================================================================== #
# update_description
# =========================================================================== #


def test_update_description_unknown_node_rejected(tiny):
    with pytest.raises(OntologyError):
        tiny.update_description("ghost", "x")


def test_update_description_can_clear(tiny):
    tiny.update_description("ppo", "on-policy")
    tiny.update_description("ppo", "")  # clearing back to empty is allowed
    assert tiny.node("ppo").description == ""


def test_update_description_unicode_multiline_round_trip(tiny, tmp_path):
    desc = "Rés—net: skip connections.\nSecond line η≈0.1"
    tiny.update_description("resnet", desc)
    tiny.save(tmp_path)
    reloaded = Ontology.load(tmp_path)
    assert reloaded.node("resnet").description == desc
    reloaded.check_invariants()


# =========================================================================== #
# add_surface
# =========================================================================== #


def test_add_surface_empty_normalization_rejected(tiny):
    before = len(tiny.norm)
    for bad in ("()", "  ", "--"):
        with pytest.raises(InvariantError):
            tiny.add_surface(bad, "ppo")
    assert len(tiny.norm) == before


def test_add_surface_idempotent_no_duplicate_row(tiny):
    tiny.add_surface("PPO Clip", "ppo")
    n = len(tiny.norm)
    tiny.add_surface("ppo clip", "ppo")  # same normalized surface + canonical
    assert len(tiny.norm) == n  # no duplicate appended
    assert tiny.resolve("PPO Clip") == "ppo"


def test_add_surface_collapses_spelling_variants(tiny):
    tiny.add_surface("ResNet-50", "resnet")
    tiny.add_surface("resnet 50", "resnet")  # collapses to the same key
    assert tiny.resolve("RESNET50") == "resnet"
    assert len([r for r in tiny.norm if r.surface == "resnet50"]) == 1


def test_add_surface_flag_persists_and_is_omitted_when_unset(tiny, tmp_path):
    tiny.add_surface("AdamW", "ppo", via="levenshtein", flag="review")
    tiny.save(tmp_path)
    reloaded = Ontology.load(tmp_path)
    flagged = next(r for r in reloaded.norm if r.surface == "adamw")
    assert flagged.flag == "review" and flagged.via == "levenshtein"
    # an unset flag is dropped from the on-disk row (exclude_none)
    line = (tmp_path / "normalization.jsonl").read_text().splitlines()
    assert all(("flag" in ln) == (ln.count("adamw") > 0) for ln in line if ln.strip())


def test_add_surface_ownership_boundary(tiny):
    # a name owned by no surface row (here 'junk') can be assigned to another node
    assert tiny.resolve("junk") is None
    tiny.add_surface("junk", "ppo")
    assert tiny.resolve("junk") == "ppo"
    # but an owned surface cannot be stolen (1:1)
    with pytest.raises(InvariantError):
        tiny.add_surface("junk", "sac")


# =========================================================================== #
# remove_surface
# =========================================================================== #


def test_remove_surface_normalizes_input(tiny):
    tiny.add_surface("ResNet-50", "resnet")
    tiny.remove_surface("resnet 50")  # different spelling, same normalized key
    assert tiny.resolve("ResNet-50") is None


def test_remove_seed_surface_keeps_node(tiny):
    tiny.remove_surface("resnet")  # its own seed surface
    assert "resnet" in tiny  # node still present
    assert tiny.resolve("resnet") is None  # but no longer resolvable by that name
    tiny.check_invariants()


def test_remove_surface_clears_duplicate_rows():
    # a hand-edited file could carry duplicate identical rows; remove drops all
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["a"],
        nodes={"a": Node(name="A")},
    )
    o = Ontology(
        doc,
        [NormRow(surface="dup", canonical="a"), NormRow(surface="dup", canonical="a")],
    )
    o.remove_surface("dup")
    assert o.resolve("dup") is None
    assert [r for r in o.norm if r.surface == "dup"] == []


# =========================================================================== #
# move
# =========================================================================== #


def test_move_to_current_parent_preserves_order(tiny):
    # ppo is the first of rl's children; moving it to rl again must NOT reorder
    # it to the end (roll-up DFS order is significant).
    assert tiny.children("rl") == ["ppo", "sac"]
    tiny.move("ppo", "rl")
    assert tiny.children("rl") == ["ppo", "sac"]
    tiny.check_invariants()


def test_move_collapses_a_multiparent_node():
    # DAG-ready format: a node may sit under two parents. move re-parents it to a
    # single location (single-primary convention), dropping the other edge.
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["a", "b", "c"],
        nodes={
            "a": Node(name="A", children=["shared"]),
            "b": Node(name="B", children=["shared"]),
            "c": Node(name="C"),
            "shared": Node(name="Shared"),
        },
    )
    o = Ontology(doc, [])
    assert sorted(o.parents("shared")) == ["a", "b"]
    o.move("shared", "c")
    assert o.parents("shared") == ["c"]
    assert "shared" not in o.children("a") and "shared" not in o.children("b")
    o.check_invariants()


def test_move_changes_depth_cut_rollup(tiny):
    from paperext.ontology import to_category_map

    assert to_category_map(tiny, 2)["resnet"] == "CNN"  # nn > cnn > resnet
    tiny.move("resnet", "rl")  # algorithms > rl > resnet
    assert to_category_map(tiny, 2)["resnet"] == "reinforcement learning"
