"""Tests for the layered ontology model (WS-D D1a, #36).

Two layers of testing:

- **Unit** — a tiny hand-built ontology exercises the accessors, DFS order,
  multi-hit search, and the roll-up converter's semantics (depth + node cut,
  ignore-drop, Other fallback, first-non-Other collision dedup).
- **Migration / reproduction** — ``build_v0`` on the three legacy trees must
  reproduce :func:`paperext.analysis.rollup.build_category_map` exactly at depths
  1/2/3 and the milabench cut, and the on-disk ``v0`` snapshot must round-trip.
"""

import json

import pytest

from paperext.analysis.rollup import build_category_map, load_cut
from paperext.ontology import Ontology, to_category_map
from paperext.ontology.migrate import LEGACY_TREES, build_v0, write_snapshot
from paperext.ontology.schema import Meta, Node, NormRow, OntologyDoc

# --------------------------------------------------------------------------- #
# A tiny hand-built ontology mirroring the shape of the legacy trees.
# --------------------------------------------------------------------------- #


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
    return Ontology(doc, norm)


def test_accessors():
    o = _tiny()
    assert o.name("ppo") == "PPO"
    assert o.children("rl") == ["ppo", "sac"]
    assert o.parents("ppo") == ["rl"]
    assert o.ancestry("resnet") == ["nn", "cnn", "resnet"]
    assert o.root_of("resnet") == "nn"
    assert o.examples("cnn") == ["1512.03385"]
    assert sorted(o.surfaces("ppo")) == ["ppo", "proximalpolicyoptimization"]
    assert o.root_map() == {
        "algorithms": "algorithms",
        "nn": "neural networks",
        "ignore": "ignore",
    }


def test_resolve_normalizes_surface():
    o = _tiny()
    assert o.resolve("PPO") == "ppo"
    assert o.resolve("Proximal Policy Optimization") == "ppo"  # normalized surface
    assert o.resolve("Soft Actor-Critic") == "sac"
    assert o.resolve("unknown thing") is None


def test_iter_nodes_is_preorder_dfs():
    o = _tiny()
    order = [nid for nid, _, _ in o.iter_nodes()]
    assert order == [
        "algorithms",
        "rl",
        "ppo",
        "sac",
        "nn",
        "cnn",
        "resnet",
        "ignore",
        "junk",
    ]
    # paths are (norm, raw) tuples from the root down
    _, norm_path, raw_path = next(t for t in o.iter_nodes() if t[0] == "resnet")
    assert raw_path == ("neural networks", "CNN", "ResNet")
    assert norm_path == ("neuralnetworks", "cnn", "resnet")


def test_search_is_global_multihit():
    o = _tiny()
    # substring over names + surfaces; deterministic DFS order
    assert o.search("resnet") == ["resnet"]
    assert set(o.search("a")) >= {"rl", "sac"}  # 'reinforcement' & 'actor'
    assert o.search("nonexistent-token") == []


def test_search_multihit_on_real_v0():
    # 'bit' sits under two branches in the models tree; search returns both.
    o = Ontology.load("data/ontology/models/v0")
    hits = set(o.search("bit"))
    assert {"bigtransferbit", "bit"} <= hits
    # the two are under different roots' subtrees (CNN vs vision transformer)
    assert o.root_of("bigtransferbit") == o.root_of("bit") == "neuralnetworks"
    assert o.ancestry("bigtransferbit") != o.ancestry("bit")


# --------------------------------------------------------------------------- #
# Converter semantics on the tiny ontology.
# --------------------------------------------------------------------------- #


def test_converter_depth_cut_and_ignore_drop():
    o = _tiny()
    m = to_category_map(o, 1)
    # every non-ignore node rolls up to its top-level branch name
    assert m["ppo"] == "algorithms"
    assert m["softactorcritic"] == "algorithms"
    assert m["resnet"] == "neural networks"
    assert m["cnn"] == "neural networks"
    # the ignore branch is dropped entirely
    assert "junk" not in m


def test_converter_depth_two():
    o = _tiny()
    m = to_category_map(o, 2)
    assert m["ppo"] == "reinforcement learning"
    assert m["resnet"] == "CNN"
    # shallower-than-cut nodes roll up to themselves
    assert m["algorithms"] == "algorithms"


def test_converter_node_cut_and_other_fallback():
    o = _tiny()
    # cut at reinforcement learning only; nn subtree has no cut -> Other
    m = to_category_map(o, ["algorithms.reinforcement learning"])
    assert m["ppo"] == "reinforcement learning"
    assert m["softactorcritic"] == "reinforcement learning"
    assert m["resnet"] == "Other"


def test_converter_rejects_bad_cut():
    o = _tiny()
    with pytest.raises(TypeError):
        to_category_map(o, True)
    with pytest.raises(ValueError):
        to_category_map(o, 0)


# --------------------------------------------------------------------------- #
# Migration: self-nest pruning + cross-branch collisions.
# --------------------------------------------------------------------------- #


def test_self_nest_pruned_and_neutral(tmp_path):
    # a pure self-nest chain: name repeated as its own descendant
    tree = {
        "abstract": {
            "few-shot learning": {
                "few shot learning": {},
                "few-shot learning": {"few-shot learning": {}},
            }
        }
    }
    p = tmp_path / "tree.json"
    p.write_text(json.dumps(tree))
    doc, norm, report = build_v0(p, "test")
    o = Ontology(doc, norm)
    # the redundant same-name descendants are pruned; one node survives
    fsl = [nid for nid in doc.nodes if o.name(nid).lower().startswith("few")]
    assert len(fsl) == 1
    assert report["pruned_self_nests"]
    # and the roll-up is unchanged vs the legacy tree at every tested depth
    for cut in (1, 2, 3):
        assert to_category_map(o, cut) == build_category_map(p, cut)


def test_cross_branch_collision_kept_distinct(tmp_path):
    # same normalized name under two different branches = two entities
    tree = {
        "algorithms": {"optimizer": {"SAM": {}}},
        "neural networks": {"graph neural network": {"sam": {}}},
    }
    p = tmp_path / "tree.json"
    p.write_text(json.dumps(tree))
    doc, norm, report = build_v0(p, "test")
    o = Ontology(doc, norm)
    sam_nodes = o.search("sam")
    assert len(sam_nodes) == 2  # both kept, not merged
    # exactly one owns the ambiguous bare surface; the other is surface-less
    owners = [nid for nid in sam_nodes if o.surfaces(nid)]
    assert len(owners) == 1
    assert report["surfaceless_collision_nodes"]
    # DFS-first (algorithms) owns it, matching legacy first-non-Other
    assert o.root_of(owners[0]) == "algorithms"


# --------------------------------------------------------------------------- #
# Reproduction gate: v0 == legacy build_category_map, in-memory and on-disk.
# --------------------------------------------------------------------------- #

_CUTS = {
    "models": "data/mdl/evaluation/model_categories/milabenchv1",
    "domains": "data/mdl/evaluation/domain_categories/milabenchv1",
}


def _cuts_for(dim):
    cuts = [1, 2, 3]
    if dim in _CUTS:
        cuts.append(load_cut(_CUTS[dim]))
    return cuts


@pytest.mark.parametrize("dim", list(LEGACY_TREES))
def test_v0_reproduces_legacy_in_memory(dim):
    tree_path = LEGACY_TREES[dim]
    doc, norm, _ = build_v0(tree_path, dim)
    o = Ontology(doc, norm)
    for cut in _cuts_for(dim):
        assert to_category_map(o, cut) == build_category_map(tree_path, cut)


@pytest.mark.parametrize("dim", list(LEGACY_TREES))
def test_committed_v0_snapshot_reproduces_legacy(dim):
    tree_path = LEGACY_TREES[dim]
    o = Ontology.load(f"data/ontology/{dim}/v0")
    for cut in _cuts_for(dim):
        assert to_category_map(o, cut) == build_category_map(tree_path, cut)


@pytest.mark.parametrize("dim", list(LEGACY_TREES))
def test_snapshot_write_read_round_trip(dim, tmp_path):
    tree_path = LEGACY_TREES[dim]
    doc, norm, _ = build_v0(tree_path, dim)
    write_snapshot(doc, norm, tmp_path)
    reloaded = Ontology.load(tmp_path)
    for cut in _cuts_for(dim):
        assert to_category_map(reloaded, cut) == build_category_map(tree_path, cut)
