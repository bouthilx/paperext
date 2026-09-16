"""Blind adjudication: order-blindness, cache keys, scoring (WS-D D1b-3, #53)."""

import asyncio
import random

import pytest

from paperext.categorize import adjudicate
from paperext.categorize.placement import Placement


def make(**kwargs):
    rng = random.Random(kwargs.pop("seed", 0))
    return adjudicate.make_pair(
        kwargs.pop("item_id", "vit"),
        kwargs.pop("name", "ViT"),
        kwargs.pop("evidence", "## ITEM\n\nname: ViT"),
        kwargs.pop("reference", "neural networks > transformer > ViT"),
        kwargs.pop("agent", "neural networks > ViT"),
        rng=rng,
    )


# --------------------------------------------------------------------------- #
# Order blindness
# --------------------------------------------------------------------------- #


def test_agreements_never_reach_the_judge():
    """Identical placements are a tie by definition; adjudication cost is disagreements."""
    assert make(reference="a > b", agent="a > b") is None


def test_swapping_mirrors_the_render_exactly():
    """The property W depends on: the judge cannot see which side is legacy."""
    pair = make()
    mirrored = adjudicate.render_pair(adjudicate.swap(pair))
    expected = adjudicate.render_pair(
        pair.model_copy(update={"option_a": pair.option_b, "option_b": pair.option_a})
    )
    assert mirrored == expected


def test_the_render_never_names_the_sides():
    pair = make()
    text = adjudicate.render_pair(pair).lower()
    for leak in ("reference", "legacy", "agent", "v0", "proposed"):
        assert leak not in text


def test_swap_flips_the_bookkeeping_and_keeps_the_key():
    pair = make()
    mirrored = adjudicate.swap(pair)
    assert mirrored.agent_option != pair.agent_option
    assert mirrored.key == pair.key


def test_scoring_follows_the_agent_side_not_the_letter():
    pair = make()
    for choice, other in (("A", "B"), ("B", "A")):
        verdict = adjudicate.Verdict(key=pair.key, choice=choice)
        expected = 1.0 if choice == pair.agent_option else 0.0
        assert adjudicate.score_pair(pair, verdict) == expected
        assert (
            adjudicate.score_pair(
                adjudicate.swap(pair), adjudicate.Verdict(key=pair.key, choice=other)
            )
            == expected
        )


def test_a_tie_is_half_a_win():
    pair = make()
    assert (
        adjudicate.score_pair(pair, adjudicate.Verdict(key=pair.key, choice="tie"))
        == 0.5
    )


def test_shuffling_actually_shuffles():
    sides = {make(seed=seed).agent_option for seed in range(20)}
    assert sides == {"A", "B"}


# --------------------------------------------------------------------------- #
# Cache keys
# --------------------------------------------------------------------------- #


def test_key_is_stable_across_the_ab_draw():
    """A different shuffle seed must reuse every cached verdict."""
    keys = {make(seed=seed).key for seed in range(20)}
    assert len(keys) == 1


def test_key_separates_the_two_orders_of_the_same_two_paths():
    """(ref=X, agent=Y) is not the same comparison as (ref=Y, agent=X)."""
    assert adjudicate.pair_key("i", "X", "Y") != adjudicate.pair_key("i", "Y", "X")


def test_key_is_not_confusable_by_concatenation():
    assert adjudicate.pair_key("a", "bc", "d") != adjudicate.pair_key("ab", "c", "d")


def test_cache_round_trips_through_a_file(tmp_path):
    path = tmp_path / "verdicts.jsonl"
    cache = adjudicate.VerdictCache(path)
    cache.put(adjudicate.Verdict(key="k", choice="tie", reason="why"))
    reloaded = adjudicate.VerdictCache(path)
    assert len(reloaded) == 1
    assert reloaded.get("k").reason == "why"
    assert "k" in reloaded


def test_adjudicate_only_calls_the_judge_for_uncached_pairs(tmp_path):
    pairs = [make(item_id=f"i{index}") for index in range(3)]
    cache = adjudicate.VerdictCache(tmp_path / "v.jsonl")
    cache.put(adjudicate.Verdict(key=pairs[0].key, choice="tie"))
    calls = []

    async def judge(pair):
        calls.append(pair.key)
        return adjudicate.JudgeChoice(reason="r", choice="A")

    verdicts = asyncio.run(adjudicate.adjudicate(pairs, judge, cache=cache))
    assert len(verdicts) == 3
    assert calls == [pairs[1].key, pairs[2].key]
    assert len(adjudicate.VerdictCache(tmp_path / "v.jsonl")) == 3


# --------------------------------------------------------------------------- #
# Guardrails
# --------------------------------------------------------------------------- #


def test_order_swap_consistency_is_one_for_a_content_reading_judge():
    """A judge that always prefers the agent decides the same way both ways round."""
    pairs = [make(item_id=f"i{index}", seed=index) for index in range(6)]
    first = [adjudicate.Verdict(key=p.key, choice=p.agent_option) for p in pairs]
    second = [
        adjudicate.Verdict(key=p.key, choice=adjudicate.swap(p).agent_option)
        for p in pairs
    ]
    assert adjudicate.order_swap_consistency(pairs, first, second) == 1.0


def test_order_swap_consistency_is_zero_for_a_position_reading_judge():
    """A judge that always says 'A' flips its meaning when the options swap."""
    pairs = [make(item_id=f"i{index}", seed=index) for index in range(6)]
    always_a = [adjudicate.Verdict(key=p.key, choice="A") for p in pairs]
    assert adjudicate.order_swap_consistency(pairs, always_a, always_a) == 0.0


def test_pro_agent_rate_ignores_which_letter_won():
    pairs = [make(item_id=f"i{index}", seed=index) for index in range(4)]
    verdicts = [adjudicate.Verdict(key=p.key, choice=p.agent_option) for p in pairs]
    assert adjudicate.pro_agent_rate(pairs, verdicts) == 1.0


# --------------------------------------------------------------------------- #
# Placement rendering
# --------------------------------------------------------------------------- #


def test_a_created_node_renders_the_items_own_name():
    """So a better-worded proposal cannot stand in for a better placement."""
    created = Placement(
        node_id=None,
        name="BiT-S-101 (Big Transfer, ResNet-101)",
        ancestor_path=["nn", "cnn"],
        ancestor_names=[
            "neural networks",
            "CNN",
            "BiT-S-101 (Big Transfer, ResNet-101)",
        ],
        depth=3,
    )
    assert adjudicate.render_placement(created, leaf="bit-s-101") == (
        "neural networks > CNN > bit-s-101"
    )


def test_an_existing_node_keeps_its_own_name():
    existing = Placement(
        node_id="bigtransferbit",
        name="big-transfer (bit)",
        ancestor_path=["nn", "cnn", "bigtransferbit"],
        ancestor_names=["neural networks", "CNN", "big-transfer (bit)"],
        depth=3,
    )
    assert adjudicate.render_placement(existing, leaf="bit-s-101") == (
        "neural networks > CNN > big-transfer (bit)"
    )
