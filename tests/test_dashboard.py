from __future__ import annotations

import io
import logging
import sys

from rich.console import Console

from paperext import dashboard
from paperext.dashboard import Dashboard, Stats, _LineBuffer


def test_line_buffer_keeps_whole_lines_and_a_tail():
    buffer = _LineBuffer(maxlen=3)
    buffer.write("a\nb")
    buffer.write("2\nc\n")
    assert list(buffer.lines) == ["a", "b2", "c"]
    buffer.write("d\n")
    assert list(buffer.lines) == ["b2", "c", "d"]  # bounded


def _rows(table) -> list[list[str]]:
    out = io.StringIO()
    Console(file=out, width=60, force_terminal=False).print(table)
    return [
        [cell.strip() for cell in line.strip("│").split("│")]
        for line in out.getvalue().splitlines()
        if line.startswith("│")
    ]


def test_stats_table_sorted_with_totals():
    stats = Stats("venue")
    stats.add("TMLR", False)
    stats.add("ICLR", True)
    stats.add("ICLR", True)
    stats.add("JPS", False)
    stats.add("JPS", True)
    assert stats.hits == 3 and stats.misses == 2 and stats.rows() == 4
    # most papers first, ties by name
    assert _rows(stats.table()) == [
        ["ICLR", "2", "0", "2"],
        ["JPS", "1", "1", "2"],
        ["TMLR", "0", "1", "1"],
        ["total", "3", "2", "5"],
    ]


def test_stats_table_folds_rows_past_the_limit():
    stats = Stats("venue")
    for venue, hit in [
        ("A", True),
        ("A", True),
        ("B", True),
        ("C", False),
        ("D", False),
    ]:
        stats.add(venue, hit)
    assert stats.rows(limit=2) == 4  # 2 shown + "... more" + total
    assert _rows(stats.table(limit=2)) == [
        ["A", "2", "0", "2"],
        ["B", "1", "0", "1"],
        ["... 2 more", "0", "2", "2"],
        ["total", "3", "2", "5"],
    ]
    assert stats.rows(limit=10) == 5  # no folding when everything fits


def test_disabled_dashboard_only_moves_stdout(capsys):
    with Dashboard(3, "x", enabled=False) as dash:
        print("progress from a library")
        dash.advance("arxiv", True)
        dash.advance("doi", False)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "progress from a library" in captured.err
    assert dash.stats.counts == {"arxiv": [1, 0], "doi": [0, 1]}


def test_enabled_dashboard_captures_logs_and_draws(monkeypatch):
    # A fake terminal for rich; the root logger carries the console handler
    # logging.basicConfig() installed when paperext.log was imported.
    screen = io.StringIO()
    console = Console(file=screen, force_terminal=True, width=80, height=24)
    (handler,) = [
        h
        for h in logging.getLogger().handlers
        if isinstance(h, logging.StreamHandler) and h.stream is sys.stderr
    ]
    with Dashboard(2, "dl", enabled=True, console=console) as dash:
        print("Downloading https://example/pdf")  # paperoni-style stdout
        logging.getLogger("paperext").warning("careful")
        dash.advance("arxiv", True)
        dash.advance("doi", False)
        assert dash.log_lines == [
            "Downloading https://example/pdf",
            "WARNING:paperext:careful",
        ]
        assert dash._layout is not None
        # 2 keys + total row, plus the panel chrome
        assert dash._layout["stats"].size == 3 + Dashboard.STATS_CHROME

    drawn = screen.getvalue()
    for expected in (
        "logs",
        "stats",
        "progress",
        "Downloading",
        "careful",
        "arxiv",
        "2/2",
    ):
        assert expected in drawn
    # after exit the console handler writes to the console again
    assert handler.stream is sys.stderr


def test_dashboard_caps_the_stats_panel_to_the_terminal(monkeypatch):
    screen = io.StringIO()
    console = Console(file=screen, force_terminal=True, width=80, height=24)
    with Dashboard(30, "dl", key="venue", enabled=True, console=console) as dash:
        for i in range(30):
            dash.advance(f"venue {i:02d}", i % 3 == 0)
        assert dash._layout is not None
        size = dash._layout["stats"].size
        assert size is not None
        # logs keep their minimum, the table folds the rest
        assert size + Dashboard.PROGRESS_HEIGHT + Dashboard.MIN_LOG_LINES + 2 <= 24
        assert "more" in screen.getvalue()
    # the complete table is printed after the live screen
    final = screen.getvalue().split("\x1b[?1049l")[-1]
    assert "venue 29" in final and "more" not in final


def test_enabled_dashboard_prints_final_table(monkeypatch):
    screen = io.StringIO()
    console = Console(file=screen, force_terminal=True, width=80, height=24)
    with Dashboard(1, "dl", enabled=True, console=console) as dash:
        dash.advance("openreview", False)
    tail = screen.getvalue().rsplit("openreview", 1)[-1]
    assert "1" in tail  # final table printed after the live screen closes
