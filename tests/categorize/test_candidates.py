"""Retrieval: the stages, the ranking, and the numbers that justify them (#52)."""

import json
from pathlib import Path

import pytest

from paperext.categorize.ablate import ablate
from paperext.categorize.candidates import (
    DEFAULT_LIMIT,
    MIN_ANCHOR_LEN,
    Candidate,
    anchor_ids,
    generate,
    initials,
    is_acronym_shaped,
    normalized_keys,
    skeleton_ids,
)
from paperext.categorize.sampling import Splits, anchoring
from paperext.ontology import Ontology

V0 = Path(__file__).parents[2] / "data" / "ontology" / "models" / "v0"
SPLITS = (
    Path(__file__).parents[2] / "data" / "ontology" / "eval" / "models" / "splits.json"
)


@pytest.fixture(scope="module")
def v0() -> Ontology:
    return Ontology.load(V0)


@pytest.fixture(scope="module")
def dev() -> list:
    return Splits.model_validate_json(SPLITS.read_text()).dev


def ids(candidates: "list[Candidate]") -> "list[str]":
    return [c.node_id for c in candidates]


# -- the stages -------------------------------------------------------------- #


def test_exact_name_outranks_everything(tiny):
    assert ids(generate(tiny, "ResNet"))[0] == "resnet"


def test_reverse_containment_finds_the_anchor_forward_search_misses(tiny):
    """The 96.4%-zero-hit problem, in one assertion."""
    assert tiny.search("resnet50v2") == []
    assert "resnet" in ids(generate(tiny, "ResNet-50-v2"))


def test_forward_containment_still_works(tiny):
    assert "resnet50" in ids(generate(tiny, "resnet"))


def test_acronym_matches_initials(tiny):
    """``rl`` is nowhere in "reinforcement learning" as a substring."""
    assert "rl" not in tiny.search("rl")
    hits = generate(tiny, "RL")
    assert "rl" in ids(hits)
    assert next(c for c in hits if c.node_id == "rl").stage == "acronym"


def test_fuzzy_catches_a_misspelling(tiny):
    assert "transformer" in ids(generate(tiny, "transfomer"))


def test_a_short_key_never_anchors_a_long_query(tiny):
    """A 3-char key may anchor a longer query; a 2-char key is pure noise."""
    assert MIN_ANCHOR_LEN == 3
    tiny.create_node("t5", "T5", parent="nn")
    tiny.create_node("ml", "ML", parent="nn")
    hits = anchor_ids(tiny, "T5-XXL-MODEL")
    assert "t5" not in hits and "ml" not in hits
    assert "sam" in anchor_ids(tiny, "SAM-HQ")


def test_aliases_retrieve_when_the_primary_name_does_not(tiny):
    assert "ppo" not in ids(generate(tiny, "clipped surrogate objective"))
    assert "ppo" in ids(generate(tiny, "clipped surrogate objective", aliases=["PPO"]))


def test_every_candidate_carries_its_retrieval_evidence(tiny):
    for cand in generate(tiny, "ResNet-101"):
        assert cand.stage in {"exact", "forward", "reverse", "acronym", "fuzzy"}
        assert cand.key
        assert 0.0 <= cand.score <= 1.0


def test_initials_ignores_single_word_names():
    assert initials("vision transformer") == "vt"
    assert initials("big-transfer (bit)") == "btb"
    assert initials("resnet") == ""


def test_acronym_shape_follows_the_legacy_rule():
    assert is_acronym_shaped("BiT")
    assert is_acronym_shaped("GPT-4")
    assert not is_acronym_shaped("ResNet-50")
    assert not is_acronym_shaped("a b")


# -- ranking and bounds ------------------------------------------------------ #


def test_ranking_is_deterministic_and_score_ordered(tiny):
    first = generate(tiny, "ResNet-50-v2")
    assert first == generate(tiny, "ResNet-50-v2")
    scores = [c.score for c in first]
    assert scores == sorted(scores, reverse=True)


def test_limit_is_honoured_and_none_means_everything(v0):
    assert len(generate(v0, "net", limit=5)) == 5
    assert len(generate(v0, "net", limit=None)) > 5


def test_the_worst_case_query_truncates_deterministically(v0):
    worst = max((len(v0.search(q)) for q in ("net", "gan", "transformer")), default=0)
    assert worst > 100  # the pathological shape is real
    hits = generate(v0, "net", limit=DEFAULT_LIMIT)
    assert len(hits) == DEFAULT_LIMIT
    assert hits == generate(v0, "net", limit=DEFAULT_LIMIT)


def test_branch_collapse_drops_siblings_already_shown_as_children(tiny):
    """``resnet`` is retrieved with its whole subtree; the subtree adds nothing."""
    uncollapsed = ids(generate(tiny, "ResNet", max_per_branch=None))
    collapsed = ids(generate(tiny, "ResNet", max_per_branch=0))
    assert "resnet50" in uncollapsed
    assert "resnet50" not in collapsed
    assert "resnet" in collapsed


def test_min_score_drops_the_noise(tiny):
    assert generate(tiny, "zzzzzzzzzz", min_score=0.99) == []


# -- the shared contract with the sealed splits ------------------------------ #


def test_anchor_ids_is_what_the_frozen_probe_uses(v0, dev):
    """`sampling.anchoring` delegates here; the committed splits pin the rule."""
    keys = normalized_keys(v0)
    for item in dev[:40]:
        assert anchoring(v0, item.node_id, item.surface, keys=keys) == item.anchoring


def test_anchor_ids_excludes_ranking(tiny):
    """Unranked on purpose: the strata must not move when ranking improves."""
    assert isinstance(anchor_ids(tiny, "ResNet-50-v2"), set)
    assert anchor_ids(tiny, "") == set()


# -- the skeleton ------------------------------------------------------------ #


def test_skeleton_holds_every_branch_and_every_shallow_node(tiny):
    skel = skeleton_ids(tiny, max_depth=2)
    assert {"algorithms", "nn", "ignore", "rl", "cnn", "transformer"} <= skel
    assert "resnet" in skel  # deeper than 2, but it has children
    assert "resnet50" not in skel  # deep leaf
    assert "vit" not in skel


def test_skeleton_depth_is_validated(tiny):
    with pytest.raises(ValueError):
        skeleton_ids(tiny, max_depth=-1)


def test_skeleton_shrinks_when_a_node_is_ablated(tiny):
    """It is derived from the injected tree, never cached -- the #53 leak rule."""
    assert "vit" in tiny.nodes
    scratch = ablate(tiny, "ViT")
    assert "vit" not in skeleton_ids(scratch, max_depth=3)


# -- the pre-gate recall number --------------------------------------------- #


@pytest.mark.parametrize("k", [10])
def test_candidate_recall_on_dev_clears_the_pre_gate_bar(v0, dev, k):
    """#52: measure recall@10 on dev before paying for a gate run.

    Ranked candidates alone find the held-out node's true parent for only ~37% of
    items -- and that is not a ranking bug. Of the misses, three quarters have
    their true parent at depth 2 (``optimizer``, ``reinforcement learning``): those
    are *semantic* placements that no string matcher can reach. The taxonomy
    skeleton, which is in every payload, carries them, and the union clears the
    ~0.6 bar comfortably. Both numbers are asserted so a regression in either half
    is visible.
    """
    keys = normalized_keys(v0)
    ranked_hits = union_hits = 0
    for item in dev:
        parent = v0.parents(item.node_id)[0]
        scratch = ablate(v0, item.surface)
        top = set(ids(generate(scratch, item.name, limit=k)))
        ranked_hits += parent in top
        union_hits += parent in (top | skeleton_ids(scratch))

    n = len(dev)
    assert ranked_hits / n > 0.30, f"ranked recall@{k} regressed: {ranked_hits}/{n}"
    assert union_hits / n > 0.90, f"payload recall@{k} regressed: {union_hits}/{n}"
