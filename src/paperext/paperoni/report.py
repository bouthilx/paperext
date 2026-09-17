import argparse
import html
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

from paperext import CFG
from paperext.log import logger
from paperext.paperoni.utils import auth_headers

# Paperoni migrated from the (now dev-gated) `/report` endpoint to a paginated
# `/api/v1/search` API. See src/paperext/paperoni/README notes / issue #6.
SEARCH_ENDPOINT = "/api/v1/search"
# The server caps `limit` at 200 regardless of the value requested.
PAGE_SIZE = 200
# `flags=valid` is the new equivalent of the old `validation=validated` filter.
VALID_FLAG = "valid"
# A release counts as a publication when paperoni's own review classification
# says so: `peer_review_status` is "peer-reviewed" or "workshop" (workshops are
# peer-reviewed venues in this field, and a workshop version is a publication
# in its own right -- the conference version that may follow is a different
# paper-year), and the release was not withdrawn. This replaces the earlier
# venue-type rule, which let preprint servers typed as journals (arXiv.org,
# bioRxiv, medRxiv) and withdrawn submissions through.
#
# The check is window-specific on purpose: the same paper may be published
# several times across years (workshop, then conference, then journal), and each
# is a separate publication that should be counted in its own year. So a paper is
# kept for a [start, end] window only if it has such a release *dated in that
# window*, and it is counted at most once per window (de-dup by id).
PUBLICATION_REVIEW_STATUSES = {"peer-reviewed", "workshop"}
WITHDRAWN = "withdrawn"
# Venue types paperoni uses for preprint servers; kept for consumers that only
# have the venue (download-convert's fallback venue choice for old reports).
NON_PEER_REVIEWED_VENUES = {"preprint", "unknown"}


def date_type(string: str):
    return datetime.strptime(string, "%Y-%m-%d")


def _get_json(url: str):
    """GET `url` with the Paperoni API token, return parsed JSON."""
    request = urllib.request.Request(url, headers=auth_headers())
    try:
        with urllib.request.urlopen(request) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as e:
        # The response body (e.g. {"detail": "..."}) is safe to surface; the
        # request carrying the auth header is not exposed by HTTPError.
        detail = e.read().decode(errors="replace")[:200]
        raise RuntimeError(
            f"Paperoni request failed (HTTP {e.code}) for {url}: {detail}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Paperoni request failed for {url}: {e.reason}") from e
    except json.decoder.JSONDecodeError as e:
        raise RuntimeError(f"Paperoni returned a non-JSON response for {url}") from e

    # A 200 with an unexpected shape (should not happen, but guard the contract).
    if isinstance(payload, dict) and "results" not in payload:
        raise RuntimeError(f"Unexpected paperoni response for {url}: {payload}")

    return payload


def fetch_valid_papers(start: str, end: str):
    """Page through `/api/v1/search`, returning all `flags=valid` papers.

    Papers are de-duplicated by their `id` (a paper with releases in several
    years matches multiple date windows and can be returned more than once).
    """
    query = {
        "flags": VALID_FLAG,
        "expand_links": "true",
        "limit": PAGE_SIZE,
    }
    if start:
        query["start_date"] = start
    if end:
        query["end_date"] = end

    papers: dict = {}
    offset = 0
    while True:
        params = urllib.parse.urlencode({**query, "offset": offset})
        page = _get_json(f"{CFG.paperoni.url}{SEARCH_ENDPOINT}?{params}")

        results = page["results"]
        for paper in results:
            papers[paper["id"]] = paper

        total = page.get("total", len(papers))
        offset += len(results)
        logger.info(f"Fetched {len(papers)}/{total} validated papers")

        if not results or offset >= total:
            break

    return list(papers.values())


def _venue_date(venue: dict):
    """Parse a (possibly partial) venue date string to a `date`, or None."""
    raw = venue.get("date")
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except TypeError, ValueError:
            continue
    return None


def is_publication(release: dict) -> bool:
    """Whether a paperoni release is a (peer-reviewed or workshop) publication."""
    return (
        release.get("peer_review_status") in PUBLICATION_REVIEW_STATUSES
        and release.get("status") != WITHDRAWN
    )


def peer_reviewed_venue(paper: dict, start=None, end=None) -> dict | None:
    """The venue of `paper`'s first publication release dated within
    [start, end], or None.

    `start`/`end` are `date` objects (or None for an open bound). A release
    counts when :func:`is_publication` holds and its venue date falls inside
    the window.
    """
    for release in paper.get("releases") or []:
        if not is_publication(release):
            continue
        venue = release.get("venue") or {}
        released = _venue_date(venue)
        if released is None:
            continue
        if (start is None or released >= start) and (end is None or released <= end):
            return venue
    return None


def is_peer_reviewed(paper: dict, start=None, end=None) -> bool:
    """Whether `paper` has a peer-reviewed release dated within [start, end]."""
    return peer_reviewed_venue(paper, start, end) is not None


def venue_name(venue: dict | None) -> str:
    if not venue:
        return "unknown"
    # Names arrive HTML-escaped ("Physics in Medicine &amp; Biology").
    return html.unescape(venue.get("name") or venue.get("short_name") or "unknown")


def normalize(paper: dict, venue: dict | None = None) -> dict:
    # Downstream consumers (utils.Paper, download_convert, query) key on
    # `paper_id`. The new API exposes the canonical id as `id`; map it across so
    # the rest of the pipeline keeps working unchanged. `venue` is the release
    # that put the paper in this window's corpus -- the per-venue statistics
    # downstream (download-convert's dashboard) key on it.
    record = {**paper, "paper_id": paper["id"]}
    if venue is not None:
        record["venue"] = venue_name(venue)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        type=Path,
    )
    parser.add_argument(
        "--start",
        metavar="YYYY-MM-DD",
        default=None,
        type=date_type,
    )
    parser.add_argument(
        "--end",
        metavar="YYYY-MM-DD",
        default=None,
        type=date_type,
    )
    parser.add_argument(
        "--all-valid",
        action="store_true",
        help="Keep every validated paper, skipping the peer-reviewed venue filter",
    )
    options = parser.parse_args(argv)
    start = options.start.strftime("%Y-%m-%d") if options.start else ""
    end = options.end.strftime("%Y-%m-%d") if options.end else ""
    output = (
        options.output
        or CFG.dir.data
        / f"paperoni-{start}-{end}-PR_{date.today().strftime('%Y-%m-%d')}.json"
    )

    papers = fetch_valid_papers(start, end)
    logger.info(f"Fetched {len(papers)} validated papers")

    start_date = options.start.date() if options.start else None
    end_date = options.end.date() if options.end else None
    venues = {
        paper["id"]: peer_reviewed_venue(paper, start_date, end_date)
        for paper in papers
    }
    if not options.all_valid:
        papers = [paper for paper in papers if venues[paper["id"]] is not None]
        logger.info(f"Kept {len(papers)} peer-reviewed papers")

    papers = [normalize(paper, venues[paper["id"]]) for paper in papers]
    output.write_text(json.dumps(papers, indent=2))

    # Check that the output is a valid JSON
    try:
        json.loads(output.read_text())
    except json.decoder.JSONDecodeError as e:
        logger.error(f"Paperoni report is not a valid JSON: {e}", exc_info=True)


if __name__ == "__main__":
    main()
