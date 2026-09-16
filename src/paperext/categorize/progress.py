"""Progress reporting for the long-running loops (WS-D D1b).

One shape for both callers: :func:`track` yields an ``advance()`` callable and
draws a bar with a count, elapsed time and an ETA on stderr. It is a no-op
display when stderr is not a terminal, so logs piped to a file stay clean.

The interactive reviewer cannot share the terminal with a live bar -- it is
waiting on ``input()`` most of the time -- so it gets :class:`Pace` instead: the
same numbers, printed as one line in each item's header. Its ETA deliberately
includes the human's own review time, because that is the session's real pace.
"""

from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from typing import Callable, Iterator

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


@contextmanager
def track(
    total: int, description: str = "deciding", *, enabled: "bool | None" = None
) -> "Iterator[Callable[[], None]]":
    """``with track(n) as advance:`` -- call ``advance()`` once per finished item."""
    if enabled is None:
        enabled = sys.stderr.isatty()
    if not enabled or total <= 0:
        yield lambda: None
        return
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TextColumn("ETA"),
        TimeRemainingColumn(),
        transient=False,
        # stderr, as documented: callers such as download-convert use stdout
        # for their actual output.
        console=Console(stderr=True),
    )
    task = progress.add_task(description, total=total)
    with progress:
        yield lambda: progress.advance(task)


class Pace:
    """Elapsed / ETA for a sequential loop, as text for a header line."""

    def __init__(self, total: int) -> None:
        self.total = total
        self.started = time.monotonic()

    def line(self, done: int) -> str:
        """*done* is how many items are finished before the one being shown."""
        elapsed = time.monotonic() - self.started
        text = f"[{done + 1}/{self.total}]  elapsed {_fmt(elapsed)}"
        if done:
            remaining = elapsed / done * (self.total - done)
            text += f"  ETA ~{_fmt(remaining)}"
        return text


def _fmt(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m{seconds:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h{minutes:02d}m"
