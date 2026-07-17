import json
from pathlib import Path

import pytest

from paperext.analysis.rollup import (
    OTHER,
    build_category_map,
    load_cut,
    roll_up,
    str_normalize,
)

# A tiny hand-built tree exercising depth, nested aliases, and the ignore branch.
TREE = {
    "algorithms": {
        "reinforcement learning": {
            "q-learning": {"deep q-learning": {"bcq": {}}},
            "ppo": {},
        },
        "optimizer": {"adam": {}},
    },
    "neural networks": {
        # ResNet is the canonical, resnet-50 a nested alias.
        "convolutional neural network": {"ResNet": {"resnet-50": {}}},
    },
    "ignore": {"pytorch": {}, "": {}},
}


# --- depth cut ------------------------------------------------------------


def test_depth_cut_rolls_to_ancestor_at_depth():
    m = roll_up(TREE, 2)
    assert m["bcq"] == "reinforcement learning"
    assert m["deepqlearning"] == "reinforcement learning"
    assert m["ppo"] == "reinforcement learning"
    assert m["adam"] == "optimizer"
    assert m["resnet50"] == "convolutional neural network"


def test_depth_cut_top_level():
    m = roll_up(TREE, 1)
    assert m["bcq"] == "algorithms"
    assert m["adam"] == "algorithms"
    assert m["resnet50"] == "neural networks"


def test_depth_cut_uses_self_when_shallower():
    # "algorithms" lives at depth 1; a depth-3 cut can't go deeper than the node.
    m = roll_up(TREE, 3)
    assert m["algorithms"] == "algorithms"
    # "optimizer" is at depth 2, shallower than 3 -> itself.
    assert m["optimizer"] == "optimizer"


# --- node cut -------------------------------------------------------------


def test_node_cut_rolls_to_nearest_named_ancestor():
    cut = [
        "algorithms.reinforcement learning",
        "neural networks.convolutional neural network",
    ]
    m = roll_up(TREE, cut)
    assert m["bcq"] == "reinforcement learning"
    assert m["resnet50"] == "convolutional neural network"


def test_node_cut_unmatched_goes_to_other_not_dropped():
    cut = ["algorithms.reinforcement learning"]
    m = roll_up(TREE, cut)
    # optimizer/adam has no selected ancestor -> Other, but still present.
    assert m["adam"] == OTHER
    assert m["optimizer"] == OTHER
    assert "adam" in m


def test_node_cut_deeper_node():
    cut = ["algorithms.reinforcement learning.q-learning"]
    m = roll_up(TREE, cut)
    assert m["bcq"] == "q-learning"
    # ppo is under RL but not under q-learning -> Other.
    assert m["ppo"] == OTHER


def test_node_cut_prefers_nearest_when_nested_cuts():
    cut = [
        "algorithms.reinforcement learning",
        "algorithms.reinforcement learning.q-learning",
    ]
    m = roll_up(TREE, cut)
    # bcq's nearest cut ancestor is q-learning, not reinforcement learning.
    assert m["bcq"] == "q-learning"
    assert m["ppo"] == "reinforcement learning"


# --- ignore / empty -------------------------------------------------------


def test_ignore_branch_dropped():
    m = roll_up(TREE, 1)
    assert "pytorch" not in m
    # nothing from the ignore branch leaks in.
    assert "ignore" not in set(m.values())


def test_empty_name_skipped():
    m = roll_up(TREE, 1)
    assert "" not in m


def test_custom_drop_roots():
    m = roll_up(TREE, 1, drop_roots=("ignore", "algorithms"))
    assert "bcq" not in m
    assert "resnet50" in m


# --- alias resolution -----------------------------------------------------


def test_alias_and_canonical_resolve_to_same_category():
    m = roll_up(TREE, 2)
    # both "ResNet" and its nested alias "resnet-50" map to the same category.
    assert m[str_normalize("ResNet")] == "convolutional neural network"
    assert m[str_normalize("resnet-50")] == "convolutional neural network"


# --- names containing '.' -------------------------------------------------

# str_normalize strips '.', so a tree name with '.' collapses to one segment.
# The risk is the node-cut path parser, which splits raw cut entries on '.'.
DOT_TREE = {"transformer": {"gpt-3.5": {"variant": {}}}}


def test_dot_name_normalizes_and_keys_by_stripped_name():
    m = roll_up(DOT_TREE, 3)
    assert "gpt35" in m  # '.' stripped, not two segments
    assert "gpt3" not in m and "5" not in m
    assert m["gpt35"] == "gpt-3.5"  # label keeps the raw name


def test_dot_name_depth_cut():
    m = roll_up(DOT_TREE, 1)
    assert m["gpt35"] == "transformer"
    assert m["variant"] == "transformer"


def test_dot_name_node_cut_at_clean_ancestor_works():
    # Cutting at a clean ancestor is unaffected by a '.' lower in the path.
    m = roll_up(DOT_TREE, ["transformer"])
    assert m["gpt35"] == "transformer"
    assert m["variant"] == "transformer"


def test_dot_name_as_cut_target_warns_and_no_ops(caplog):
    # The '.' in the cut entry is read as a separator, so it matches no node.
    import logging

    with caplog.at_level(logging.WARNING, logger="paperext.analysis.rollup"):
        m = roll_up(DOT_TREE, ["transformer.gpt-3.5"])
    # children fall through to Other rather than the intended bucket ...
    assert m["variant"] == OTHER
    # ... but the failure is loud, not silent.
    assert any("matches no node" in r.message for r in caplog.records)


def test_unknown_cut_entry_warns(caplog):
    import logging

    with caplog.at_level(logging.WARNING, logger="paperext.analysis.rollup"):
        roll_up(TREE, ["algorithms.does not exist"])
    assert any("matches no node" in r.message for r in caplog.records)


# --- conflict handling ----------------------------------------------------


def test_duplicate_name_across_branches_keeps_first_deterministically():
    tree = {"a": {"dup": {}}, "b": {"dup": {}}}
    m = roll_up(tree, 1)
    assert m["a"] == "a"
    assert m["b"] == "b"
    assert m["dup"] == "a"  # first-seen wins


def test_conflict_prefers_non_other_regardless_of_order():
    # Other seen first, real category second -> real category wins.
    tree_a = {"b": {"dup": {}}, "a": {"dup": {}}}
    assert roll_up(tree_a, ["a"])["dup"] == "a"
    # Real category first, Other second -> real category kept.
    tree_b = {"a": {"dup": {}}, "b": {"dup": {}}}
    assert roll_up(tree_b, ["a"])["dup"] == "a"


# --- cut passed as a bare string ------------------------------------------


def test_string_cut_is_single_entry_not_char_iterable():
    # A bare string must be one cut node, not iterated character-by-character.
    m = roll_up(TREE, "algorithms.reinforcement learning")
    assert m["bcq"] == "reinforcement learning"
    assert m["adam"] == OTHER


# --- reserved fallback label ----------------------------------------------


def test_node_named_like_fallback_warns(caplog):
    import logging

    tree = {"algorithms": {"Other": {"child": {}}}}
    with caplog.at_level(logging.WARNING, logger="paperext.analysis.rollup"):
        roll_up(tree, 2)
    assert any("reserved fallback label" in r.message for r in caplog.records)


# --- empty cut ------------------------------------------------------------


def test_empty_cut_warns_and_maps_all_to_other(caplog):
    import logging

    with caplog.at_level(logging.WARNING, logger="paperext.analysis.rollup"):
        m = roll_up(TREE, [])
    assert set(m.values()) == {OTHER}
    assert any("cut is empty" in r.message for r in caplog.records)


# --- normalizer parity (guards silent drift) ------------------------------


def test_str_normalize_matches_canonical():
    # The whole pipeline's canonicalization depends on this staying identical to
    # structured_output.utils.str_normalize; guard against drift.
    utils = pytest.importorskip("paperext.structured_output.utils")
    for s in [
        "ResNet-50",
        "GPT-3.5",
        "ν3 decay",
        "(CNN)",
        "multi layer perceptron",
        "soft actor-critic (SAC)",
        "a_b/c",
        "x²",
        "",
    ]:
        assert str_normalize(s) == utils.str_normalize(s)


# --- input validation -----------------------------------------------------


def test_depth_zero_raises():
    with pytest.raises(ValueError):
        roll_up(TREE, 0)


def test_bool_cut_rejected():
    with pytest.raises(TypeError):
        roll_up(TREE, True)


# --- cut file loading -----------------------------------------------------


def test_load_cut_parses_and_normalizes(tmp_path: Path):
    f = tmp_path / "cut"
    f.write_text(
        "# a comment\n"
        "\n"
        "algorithms.reinforcement learning\n"
        "  neural networks.convolutional neural network  \n"
        "ignore\n"
    )
    cut = load_cut(f)
    assert cut == {
        "algorithms.reinforcementlearning",
        "neuralnetworks.convolutionalneuralnetwork",
        "ignore",
    }


def test_build_category_map_from_file(tmp_path: Path):
    f = tmp_path / "tree.json"
    f.write_text(json.dumps(TREE))
    m = build_category_map(f, 2)
    assert m["bcq"] == "reinforcement learning"


# --- integration on real category trees (light smoke) ---------------------

REAL_TREES = [
    Path("data/categorized_models.json"),
    Path("data/categorized_datasets.json"),
    Path("data/categorized_domains.json"),
]


@pytest.mark.parametrize("tree_path", REAL_TREES, ids=lambda p: p.name)
@pytest.mark.parametrize("cut", [1, 2, 3], ids=lambda c: f"depth{c}")
def test_real_trees_depth_cut_runs(tree_path: Path, cut: int):
    if not tree_path.exists():
        pytest.skip(f"{tree_path} not available")
    m = build_category_map(tree_path, cut)
    assert m
    assert all(v for v in m.values())


def test_real_models_node_cut_from_milabenchv1():
    tree_path = Path("data/categorized_models.json")
    cut_path = Path("data/mdl/evaluation/model_categories/milabenchv1")
    if not (tree_path.exists() and cut_path.exists()):
        pytest.skip("real model tree / cut file not available")
    m = build_category_map(tree_path, load_cut(cut_path))
    assert m
    # milabench selects the ignore branch, which is dropped -> never a label.
    assert "pytorch" not in m
