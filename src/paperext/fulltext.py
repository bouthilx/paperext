"""Local adjustments to paperoni's fulltext locator.

Paperoni resolves an ``openreview:<note id>`` ref to ``api2.openreview.net/pdf``
(then the v1 API, then the website). That endpoint is rate-limited to **26
requests per hour per account**; the same PDF is served by
``api2.openreview.net/attachment?id=<note id>&name=pdf`` from a separate
**140 per hour** bucket. This module registers a higher-priority overload of
paperoni's ``find_download_links`` for OpenReview refs that yields the
attachment URL first and then falls through to paperoni's own candidates.

Kept here rather than upstream for now; ``install()`` is idempotent and is
called by ``download-convert`` before any download.
"""

from __future__ import annotations

from typing import Literal

_installed = False

OPENREVIEW_ATTACHMENT = "https://api2.openreview.net/attachment?id={link}&name=pdf"


def install() -> None:
    """Register the OpenReview attachment URL as the first candidate."""
    global _installed
    if _installed:
        return

    from ovld import call_next
    from paperoni.discovery.openreview import auth_headers
    from paperoni.fulltext import locate

    @locate.find_download_links.register(priority=10)
    async def find_download_links(typ: Literal["openreview"], link: str):
        """OpenReview attachment endpoint (140/h) before paperoni's /pdf (26/h)."""
        yield locate.URL(
            url=OPENREVIEW_ATTACHMENT.format(link=link),
            info="openreview",
            headers=auth_headers(2),
        )
        async for url in call_next(typ, link):
            yield url

    _installed = True
