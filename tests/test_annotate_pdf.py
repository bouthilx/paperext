"""Quote location for the annotated PDF (#111).

The matching rules here were each forced by a real failure on the first paper,
and each one is cheap to regress, so they are pinned.
"""

from __future__ import annotations

import pytest

from paperext.annotate_pdf import (
    MIN_MATCH,
    Claim,
    _locate,
    _norm,
    _walk,
    collect_claims,
)


class FakePage:
    """A page whose text layer has no spaces, like this corpus's PDFs."""

    def __init__(self, lines):
        self.chars = []
        for row, line in enumerate(lines):
            for col, ch in enumerate(line):
                self.chars.append(
                    {
                        "text": ch,
                        "x0": float(col),
                        "x1": float(col + 1),
                        "top": float(row * 10),
                        "bottom": float(row * 10 + 8),
                    }
                )


def test_a_quote_is_found_although_the_text_layer_has_no_spaces():
    """Word matching placed 77 of 142; characters have no boundaries to lose."""
    page = FakePage(["trainedforjointmotionforecasting,usingtheirreported"])
    rects = _locate(page, "trained for joint motion forecasting")
    assert len(rects) == 1
    x0, top, x1, bottom = rects[0]
    # One char box per normalised character, so the span is exactly as long as
    # the normalised quote -- 32 for this one.
    assert x0 == 0.0 and top == 0.0
    assert x1 == pytest.approx(
        float(len(_norm("trained for joint motion forecasting")))
    )


def test_a_quote_starting_mid_line_is_found():
    """The failing case: the quote does not begin where a 'word' does."""
    page = FakePage(["usingtheirreportedhyperparameters.Ego-onlyandScenemotion"])
    assert _locate(page, "Ego-only and Scene motion")


def test_a_quote_spanning_two_lines_gets_one_rect_per_line():
    page = FakePage(["Ego-onlyandScenemotion", "forecastingperformance"])
    rects = _locate(page, "Ego-only and Scene motion forecasting performance")
    assert len(rects) == 2
    assert {round(r[1]) for r in rects} == {0, 10}


def test_a_short_quote_must_match_in_full_rather_than_be_dropped():
    """`'We train DJINN on two A100 GPUs'` is 25 normalised chars.

    Requiring a 30-character prefix of it discarded every short quote, and the
    sentence is plainly in the paper.
    """
    short = "We train DJINN on two A100 GPUs"
    assert len(_norm(short)) < MIN_MATCH
    page = FakePage(["WetrainDJINNontwoA100GPUsfor150epochs."])
    assert _locate(page, short)
    # ...and a short quote that is NOT present must not match loosely.
    assert not _locate(page, "We train DJINN on four H100 GPUs")


def test_a_truncated_quote_still_places_its_prefix():
    """Extractions carry quotes cut mid-word; a prefix still points correctly."""
    page = FakePage(["wecompareDJINNagainstareproductionofSceneTransformer"])
    assert _locate(page, "We compare DJINN against a reproduction of Scene Transf")


def test_walk_finds_quotes_at_any_depth_and_labels_them():
    data = {
        "models": [
            {
                "name": {
                    "value": "DJINN",
                    "quote": "we introduce DJINN",
                    "justification": "j",
                }
            }
        ],
        "runs": [
            {"execution_mode": {"value": "train", "quote": "we train for 150 epochs"}}
        ],
    }
    found = dict(_walk(data))
    assert found["models[0].name = DJINN"] == "we introduce DJINN"
    assert found["runs[0].execution_mode = train"] == "we train for 150 epochs"


def test_a_claim_made_by_both_arms_is_green():
    both = Claim(quote="q", sources={"A", "B"})
    assert both.colour == (0.72, 0.93, 0.72)
    assert Claim(quote="q", sources={"A"}).colour != both.colour
    assert Claim(quote="q", sources={"B"}).colour != both.colour


def test_session_notes_read_from_tsv_and_json(tmp_path):
    """The session's own highlights, so a question arrives with its evidence."""
    from paperext.annotate_pdf import read_notes

    tsv = tmp_path / "notes.tsv"
    tsv.write_text(
        "# a comment, skipped\n"
        "\n"
        "Ego-only and Scene motion forecasting\tis Table 2 a separate run?\n"
        "no label here\n"
    )
    claims = read_notes(tsv)
    assert [c.quote for c in claims] == [
        "Ego-only and Scene motion forecasting",
        "no label here",
    ]
    assert claims[0].labels == ["SESSION: is Table 2 a separate run?"]
    assert claims[1].labels == ["SESSION"]

    js = tmp_path / "notes.json"
    js.write_text('[{"quote": "a", "label": "why"}, "b"]')
    claims = read_notes(js)
    assert [(c.quote, c.labels[0]) for c in claims] == [
        ("a", "SESSION: why"),
        ("b", "SESSION"),
    ]


def test_a_session_highlight_is_its_own_colour():
    """Pink, because a session mark is a QUESTION, not either arm's claim."""
    from paperext.annotate_pdf import COLOURS

    session = Claim(quote="q", sources={"S"})
    assert session.colour == COLOURS["S"]
    assert session.colour not in (COLOURS["A"], COLOURS["B"], COLOURS["both"])
