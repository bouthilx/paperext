from __future__ import annotations

from datetime import date

from paperext.paperoni import report

PAPER = {
    "id": "abc",
    "title": "T",
    "releases": [
        {"venue": {"type": "preprint", "name": "ArXiv", "date": "2025-11-02"}},
        {"venue": {"type": "conference", "name": "ICLR", "date": "2026-01-15"}},
        {"venue": {"type": "journal", "name": "TMLR", "date": "2026"}},
    ],
}


def test_peer_reviewed_venue_is_the_release_inside_the_window():
    jan = (date(2026, 1, 1), date(2026, 2, 1))
    assert report.peer_reviewed_venue(PAPER, *jan)["name"] == "ICLR"
    # year-precision dates resolve to Jan 1st, so a later window misses them
    assert (
        report.peer_reviewed_venue(PAPER, date(2026, 3, 1), date(2026, 12, 31)) is None
    )
    # preprints never qualify
    assert (
        report.peer_reviewed_venue(PAPER, date(2025, 11, 1), date(2025, 12, 1)) is None
    )
    assert report.is_peer_reviewed(PAPER, *jan)


def test_normalize_stamps_paper_id_and_venue():
    venue = report.peer_reviewed_venue(PAPER, date(2026, 1, 1), date(2026, 2, 1))
    record = report.normalize(PAPER, venue)
    assert record["paper_id"] == "abc"
    assert record["venue"] == "ICLR"
    assert "venue" not in report.normalize(PAPER)
    assert report.venue_name({"short_name": "NN"}) == "NN"
    assert report.venue_name({"name": "Physics in Medicine &amp; Biology"}) == (
        "Physics in Medicine & Biology"
    )
    assert report.venue_name(None) == "unknown"
