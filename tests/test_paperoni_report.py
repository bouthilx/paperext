from __future__ import annotations

from datetime import date

from paperext.paperoni import report


def _release(name, date, type="conference", review="peer-reviewed", status="published"):
    return {
        "venue": {"type": type, "name": name, "date": date},
        "peer_review_status": review,
        "status": status,
    }


PAPER = {
    "id": "abc",
    "title": "T",
    "releases": [
        _release(
            "ArXiv", "2025-11-02", type="preprint", review="preprint", status="preprint"
        ),
        _release("ICLR", "2026-01-15"),
        _release("TMLR", "2026", type="journal"),
    ],
}


def test_is_publication_follows_paperoni_flags():
    assert report.is_publication(_release("ICLR", "2026"))
    assert report.is_publication(
        _release(
            "W @ NeurIPS", "2026", type="workshop", review="workshop", status="poster"
        )
    )
    # preprint servers typed as journals by the source, withdrawn submissions,
    # and "other" statuses are not publications
    assert not report.is_publication(
        _release(
            "arXiv.org", "2026", type="journal", review="preprint", status="preprint"
        )
    )
    assert not report.is_publication(
        _release(
            "ICLR.cc/2026/Conference/Withdrawn_Submission",
            "2026",
            review="other",
            status="withdrawn",
        )
    )
    assert not report.is_publication(
        _release("X", "2026", review="peer-reviewed", status="withdrawn")
    )
    assert not report.is_publication({"venue": {"type": "conference"}})


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
