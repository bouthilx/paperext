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


def test_stats_table_rows_and_totals():
    stats = Stats()
    stats.add("arxiv", True)
    stats.add("arxiv", True)
    stats.add("doi", False)
    stats.add("doi", True)
    assert stats.hits == 3 and stats.misses == 1 and stats.rows == 3

    console = Console(file=io.StringIO(), width=60, force_terminal=False)
    console.print(stats.table())
    out = console.file.getvalue()
    rows = [
        [cell.strip() for cell in line.strip("│").split("│")]
        for line in out.splitlines()
        if line.startswith("│")
    ]
    assert rows == [
        ["arxiv", "2", "0", "2"],
        ["doi", "1", "1", "2"],
        ["total", "3", "1", "4"],
    ]


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
        # 2 buckets + total row, plus panel borders, table box, header,
        # header rule and section rule
        assert dash._layout["stats"].size == 3 + 7

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


def test_enabled_dashboard_prints_final_table(monkeypatch):
    screen = io.StringIO()
    console = Console(file=screen, force_terminal=True, width=80, height=24)
    with Dashboard(1, "dl", enabled=True, console=console) as dash:
        dash.advance("openreview", False)
    tail = screen.getvalue().rsplit("openreview", 1)[-1]
    assert "1" in tail  # final table printed after the live screen closes
