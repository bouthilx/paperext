"""The corpus fold: mentions -> one decidable item per name (WS-D D1b-2, #52)."""

from pathlib import Path

import pytest

from paperext.categorize.items import (
    DIMENSION_FIELDS,
    Item,
    Mention,
    _as_bool,
    _rank_mentions,
    build_items,
    read_items,
    write_items,
)

QUERIES = Path(__file__).parents[2] / "data" / "mdl" / "queries" / "openai"
#: The #52 worked example: a genuinely ambiguous name with a resolving quote.
BIT_PAPER = QUERIES / "legacy-2024" / "2306.03522_00.json"


@pytest.fixture(scope="module")
def bit_items() -> "list[Item]":
    return build_items("models", files=[BIT_PAPER])


@pytest.fixture(scope="module")
def bit(bit_items) -> Item:
    return next(i for i in bit_items if i.surface == "bits101")


def test_the_worked_example_folds_with_its_grounding(bit):
    assert bit.name == "BiT-S-101"
    assert bit.aliases == ["BiT ResNet"]
    assert bit.n_papers == 1
    mention = bit.mentions[0]
    assert mention.paper == "2306.03522"
    assert "ResNetv2-101 architecture" in mention.quote
    assert mention.is_executed is True
    assert mention.is_contributed is False


def test_int_valued_booleans_are_coerced(bit):
    """``is_*.value`` is ``bool`` in 3305 records and ``int`` 0/1 in 296."""
    assert _as_bool(1) is True and _as_bool(0) is False
    assert _as_bool(True) is True
    assert _as_bool(None) is None
    assert isinstance(bit.mentions[0].is_compared, bool)


def test_pre_v4_execution_mode_is_dropped_not_rendered_as_unknown(bit):
    """Up-conversion fills ``"unknown"`` with an empty quote -- an absence of
    evidence, which must not reach the prompt looking like evidence."""
    assert bit.mentions[0].execution_mode is None


def test_co_occurrence_lists_the_other_entities_of_the_paper(bit):
    names = bit.mentions[0].co_occurring
    assert "ResNet-50" in names and "DenseNet-121" in names
    assert bit.name not in names


def test_an_item_is_never_its_own_neighbour(bit_items):
    """A paper spelling one model two ways must not hand it back to itself."""
    for item in bit_items:
        for mention in item.mentions:
            assert item.name not in mention.co_occurring


def test_research_field_is_carried_as_grounding(bit):
    assert bit.mentions[0].research_field == "Out-of-Distribution Detection"


def test_items_are_ordered_most_mentioned_first(bit_items):
    keys = [(-i.n_mentions, i.surface) for i in bit_items]
    assert keys == sorted(keys)


def test_mention_ranking_prefers_grounded_executed_and_is_tie_broken_by_paper():
    quiet = Mention(paper="b", spelling="x")
    short = Mention(paper="c", spelling="x", quote="short", is_executed=True)
    long_ = Mention(
        paper="a", spelling="x", quote="a much longer quote", is_executed=True
    )
    ranked = _rank_mentions([quiet, short, long_], 3)
    assert [m.paper for m in ranked] == ["a", "c", "b"]
    assert _rank_mentions([quiet, short, long_], 1) == [long_]


def test_max_mentions_bounds_the_payload():
    items = build_items("models", files=[BIT_PAPER], max_mentions=1)
    assert all(len(i.mentions) <= 1 for i in items)


@pytest.mark.parametrize("dimension", sorted(DIMENSION_FIELDS))
def test_every_dimension_folds(dimension):
    items = build_items(dimension, files=[BIT_PAPER])
    assert items and all(i.dimension == dimension for i in items)
    assert all(i.surface and i.name for i in items)


def test_domains_spans_primary_and_sub_fields():
    items = build_items("domains", files=[BIT_PAPER])
    assert any(i.name == "Out-of-Distribution Detection" for i in items)


def test_unknown_dimension_is_rejected():
    with pytest.raises(ValueError, match="unknown dimension"):
        build_items("frameworks", files=[BIT_PAPER])


def test_items_round_trip_through_jsonl(tmp_path, bit_items):
    path = write_items(bit_items, tmp_path / "items.jsonl")
    assert read_items(path) == bit_items
