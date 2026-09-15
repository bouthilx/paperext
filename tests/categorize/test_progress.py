"""Progress reporting (WS-D D1b)."""

from paperext.categorize import progress


def test_track_is_a_no_op_off_a_terminal():
    calls = 0
    with progress.track(3, enabled=False) as advance:
        advance()
        calls += 1
    assert calls == 1


def test_track_counts_to_total_when_enabled(capsys):
    with progress.track(2, "x", enabled=True) as advance:
        advance()
        advance()
    # rich writes the bar to stdout by default; the run must not raise
    assert "2/2" in capsys.readouterr().out


def test_pace_reports_position_and_an_eta_after_the_first_item():
    pace = progress.Pace(10)
    first = pace.line(0)
    assert first.startswith("[1/10]") and "ETA" not in first
    later = pace.line(4)
    assert later.startswith("[5/10]") and "ETA ~" in later


def test_duration_formatting():
    assert progress._fmt(5) == "5s"
    assert progress._fmt(65) == "1m05s"
    assert progress._fmt(3725) == "1h02m"
