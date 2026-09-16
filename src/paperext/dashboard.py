"""Live terminal dashboard for long download runs: logs | stats | progress.

Three stacked panels on the alternate screen, redrawn a few times a second:

- **logs** -- the tail of everything written while the run is going: our own
  logger, paperoni's ``print`` progress (stdout) and its root-logger messages.
  It takes whatever height the other two panels leave.
- **stats** -- one row per bucket (see :meth:`Dashboard.advance`) with hits,
  misses and total, plus a total row; sized to its rows.
- **progress** -- count, elapsed and ETA.

When stderr is not a terminal (piped, ``nohup``) nothing is drawn: logs go to
stderr as usual and only the tallies are kept. Either way stdout is redirected
to stderr for the duration, so the caller keeps stdout for its real output.
"""

from __future__ import annotations

import collections
import contextlib
import io
import logging
import sys
from types import TracebackType
from typing import Any

from rich.console import Console, ConsoleOptions, RenderResult
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text


class _LineBuffer(io.TextIOBase):
    """A write-only text stream keeping the last ``maxlen`` lines."""

    def __init__(self, maxlen: int) -> None:
        super().__init__()
        self.lines: collections.deque[str] = collections.deque(maxlen=maxlen)
        self._partial = ""

    def write(self, s: str) -> int:
        self._partial += s
        *done, self._partial = self._partial.split("\n")
        self.lines.extend(line.rstrip() for line in done)
        return len(s)

    def flush(self) -> None:
        pass

    def writable(self) -> bool:
        return True


class _LogTail:
    """Renders as many of the newest lines as the panel has room for."""

    def __init__(self, buffer: _LineBuffer) -> None:
        self.buffer = buffer

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        height = options.height or options.max_height
        lines = list(self.buffer.lines)[-height:] if height else []
        for line in lines:
            yield Text(line, overflow="ellipsis", no_wrap=True)


class Stats:
    """Hits / misses per bucket, in first-seen order."""

    def __init__(self) -> None:
        self.counts: dict[str, list[int]] = {}

    def add(self, bucket: str, hit: bool) -> None:
        self.counts.setdefault(bucket, [0, 0])[0 if hit else 1] += 1

    @property
    def hits(self) -> int:
        return sum(h for h, _ in self.counts.values())

    @property
    def misses(self) -> int:
        return sum(m for _, m in self.counts.values())

    def table(self, title: str | None = None) -> Table:
        table = Table(title=title, expand=True, pad_edge=False)
        table.add_column("value", ratio=1)
        table.add_column("hits", justify="right", style="green")
        table.add_column("misses", justify="right", style="red")
        table.add_column("total", justify="right")
        for bucket, (hits, misses) in self.counts.items():
            table.add_row(bucket, str(hits), str(misses), str(hits + misses))
        table.add_section()
        table.add_row(
            "total",
            str(self.hits),
            str(self.misses),
            str(self.hits + self.misses),
            style="bold",
        )
        return table

    @property
    def rows(self) -> int:
        return len(self.counts) + 1


class Dashboard:
    """``with Dashboard(n, "title") as dash:`` then ``dash.advance(bucket, hit)``."""

    REFRESH_PER_SECOND = 4

    def __init__(
        self,
        total: int,
        description: str,
        *,
        enabled: bool | None = None,
        console: Console | None = None,
        log_lines: int = 500,
    ) -> None:
        if enabled is None:
            enabled = sys.stderr.isatty()
        self.enabled = enabled and total > 0
        self.total = total
        self.description = description
        self.stats = Stats()
        # Bound to the real stderr now, before it is redirected into the buffer.
        self.console = console or Console(file=sys.stderr)
        self._buffer = _LineBuffer(log_lines)
        self._stack = contextlib.ExitStack()
        self._live: Live | None = None
        self._progress: Progress | None = None
        self._task: Any = None
        self._layout: Layout | None = None

    # -- lifecycle ---------------------------------------------------------

    def __enter__(self) -> Dashboard:
        if not self.enabled:
            # Keep stdout for the caller's output even without a display.
            self._stack.enter_context(contextlib.redirect_stdout(sys.stderr))
            return self

        self._progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TextColumn("ETA"),
            TimeRemainingColumn(),
            console=self.console,
        )
        self._task = self._progress.add_task(self.description, total=self.total)

        self._layout = Layout()
        self._layout.split_column(
            Layout(Panel(_LogTail(self._buffer), title="logs"), name="logs", ratio=1),
            Layout(name="stats"),
            Layout(Panel(self._progress, title="progress"), name="progress", size=3),
        )
        self._refresh_stats()

        # Everything written during the run lands in the logs panel: prints
        # (stdout/stderr) and the logging handlers that stream to the console
        # (logging.basicConfig's, and by extension paperoni's root messages).
        console_streams = {sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__}
        for handler in logging.getLogger().handlers:
            if (
                isinstance(handler, logging.StreamHandler)
                and handler.stream in console_streams
            ):
                previous = handler.setStream(self._buffer)
                self._stack.callback(handler.setStream, previous)
        self._stack.enter_context(contextlib.redirect_stdout(self._buffer))
        self._stack.enter_context(contextlib.redirect_stderr(self._buffer))

        self._live = Live(
            self._layout,
            console=self.console,
            screen=True,
            refresh_per_second=self.REFRESH_PER_SECOND,
            redirect_stdout=False,
            redirect_stderr=False,
        )
        self._live.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._live is not None:
            self._live.__exit__(exc_type, exc, tb)
            self._live = None
        self._stack.close()
        if self.enabled:
            # The alternate screen is gone; leave the final numbers behind.
            self.console.print(self.stats.table(title=self.description))

    # -- updates -----------------------------------------------------------

    def advance(self, bucket: str, hit: bool) -> None:
        """Record one finished item under `bucket` and move the bar."""
        self.stats.add(bucket, hit)
        if self._progress is not None:
            self._progress.advance(self._task)
            self._refresh_stats()
        if self._live is not None:
            # Logs redraw on the timer; a finished item is worth a frame now.
            self._live.refresh()

    def _refresh_stats(self) -> None:
        if self._layout is None:
            return
        stats = self._layout["stats"]
        stats.update(Panel(self.stats.table(), title="stats"))
        # panel borders (2) + table box top/bottom (2) + header (1)
        # + header rule (1) + rows + section rule (1)
        stats.size = self.stats.rows + 7

    @property
    def log_lines(self) -> list[str]:
        return list(self._buffer.lines)
