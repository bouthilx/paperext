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


# =========================================================================== #
# insert_above
# =========================================================================== #


def test_insert_above_blank_name_rejected(tiny):
    before = tiny.doc.model_dump()
    with pytest.raises(InvariantError):
        tiny.insert_above("resnet", "block", "  ")
    assert tiny.doc.model_dump() == before
    assert "block" not in tiny


def test_insert_above_shifts_depth_cut(tiny):
    from paperext.ontology import to_category_map

    assert to_category_map(tiny, 3)["resnet"] == "ResNet"  # nn>cnn>resnet
    tiny.insert_above("resnet", "block", "Block")  # nn>cnn>block>resnet
    assert to_category_map(tiny, 3)["resnet"] == "Block"


def test_insert_above_multiparent_inherits_all_parents():
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["a", "b"],
        nodes={
            "a": Node(name="A", children=["shared"]),
            "b": Node(name="B", children=["shared"]),
            "shared": Node(name="Shared"),
        },
    )
    o = Ontology(doc, [])
    o.insert_above("shared", "grp", "Group")
    # the new grouping node takes shared's slot under *both* parents
    assert o.children("a") == ["grp"] and o.children("b") == ["grp"]
    assert sorted(o.parents("grp")) == ["a", "b"]
    assert o.parents("shared") == ["grp"]
    o.check_invariants()


# =========================================================================== #
# demote_to_variant
# =========================================================================== #


def test_demote_root_is_removed_from_roots(tiny):
    tiny.create_node("solo", "Solo")  # a childless root
    assert "solo" in tiny.root_map()
    tiny.demote_to_variant("solo", "ppo")
    assert "solo" not in tiny and "solo" not in tiny.roots
    assert tiny.resolve("Solo") == "ppo"  # its name folded in as a surface
    tiny.check_invariants()


def test_demote_records_via_demote(tiny):
    tiny.demote_to_variant("resnet", "cnn")
    row = next(r for r in tiny.norm if r.surface == "resnet")
    assert row.canonical == "cnn" and row.via == "demote"


def test_demote_surfaceless_loser_is_plain_delete():
    # a collision loser (surface-less) folds into nothing: no rows added
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["algorithms", "nn"],
        nodes={
            "algorithms": Node(name="algorithms", children=["sam"]),
            "sam": Node(name="SAM"),
            "nn": Node(name="neural networks", children=["sam2"]),
            "sam2": Node(name="SAM"),  # loser, surface-less
        },
    )
    o = Ontology(doc, [NormRow(surface="sam", canonical="sam")])
    n_before = len(o.norm)
    o.demote_to_variant("sam2", "nn")
    assert "sam2" not in o
    assert len(o.norm) == n_before  # nothing added; 'sam' still owned by winner
    assert o.resolve("sam") == "sam"
    o.check_invariants()


def test_demote_name_owned_by_target_makes_no_duplicate():
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["t", "x"],
        nodes={"t": Node(name="Target"), "x": Node(name="Foo")},
    )
    o = Ontology(doc, [NormRow(surface="foo", canonical="t")])  # target owns 'foo'
    o.demote_to_variant("x", "t")  # x is named Foo -> normalizes to owned 'foo'
    assert [r for r in o.norm if r.surface == "foo"] == [
        NormRow(surface="foo", canonical="t")
    ]
    o.check_invariants()


def test_demote_multiparent_leaf_drops_all_parents():
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["a", "b", "t"],
        nodes={
            "a": Node(name="A", children=["shared"]),
            "b": Node(name="B", children=["shared"]),
            "t": Node(name="T"),
            "shared": Node(name="Shared"),
        },
    )
    o = Ontology(doc, [])
    o.demote_to_variant("shared", "t")
    assert "shared" not in o
    assert "shared" not in o.children("a") and "shared" not in o.children("b")
    assert o.resolve("Shared") == "t"
    o.check_invariants()


def test_demote_empty_normalizing_name_not_added():
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["t", "weird"],
        nodes={"t": Node(name="T"), "weird": Node(name="()")},
    )
    o = Ontology(doc, [])
    o.demote_to_variant("weird", "t")
    assert o.norm == []  # empty-normalizing name is not registered as a surface
    o.check_invariants()


# =========================================================================== #
# remove_node
# =========================================================================== #


def test_remove_childless_root_leaves_rest_reachable(tiny):
    tiny.create_node("solo", "Solo")  # childless root
    tiny.remove_node("solo")
    assert "solo" not in tiny and "solo" not in tiny.roots
    # childless precondition means removal can never orphan a subtree
    tiny.check_invariants()


def test_remove_node_cascades_all_surfaces(tiny):
    # ppo carries two surfaces; both rows must cascade away
    assert sorted(tiny.surfaces("ppo")) == ["ppo", "proximalpolicyoptimization"]
    tiny.remove_node("ppo")
    assert tiny.resolve("PPO") is None
    assert tiny.resolve("Proximal Policy Optimization") is None
    assert [r for r in tiny.norm if r.canonical == "ppo"] == []
    tiny.check_invariants()


def test_remove_multiparent_node_drops_all_parents():
    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"),
        roots=["a", "b"],
        nodes={
            "a": Node(name="A", children=["shared"]),
            "b": Node(name="B", children=["shared"]),
            "shared": Node(name="Shared"),
        },
    )
    o = Ontology(doc, [])
    o.remove_node("shared")
    assert "shared" not in o
    assert o.children("a") == [] and o.children("b") == []
    o.check_invariants()
