import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

from paperext import CFG
from paperext.log import logger
from paperext.paperoni.utils import parse_curl_headers

# Paperoni migrated from the (now dev-gated) `/report` endpoint to a paginated
# `/api/v1/search` API. See src/paperext/paperoni/README notes / issue #6.
SEARCH_ENDPOINT = "/api/v1/search"
# The server caps `limit` at 200 regardless of the value requested.
PAGE_SIZE = 200
# `flags=valid` is the new equivalent of the old `validation=validated` filter.
VALID_FLAG = "valid"
# Venue types that do NOT count as peer-reviewed. A paper is counted for a year
# when at least one of its releases *in that year* is in any other venue type.
# This reproduces the old `peer-reviewed=True` server-side filter, which the new
# API no longer exposes as a parameter.
#
# The check is window-specific on purpose: the same paper may be published
# several times across years (workshop, then conference, then journal), and each
# is a separate publication that should be counted in its own year. So a paper is
# kept for a [start, end] window only if it has a peer-reviewed release *dated in
# that window*, and it is counted at most once per window (de-dup by id).
NON_PEER_REVIEWED_VENUES = {"preprint", "unknown"}


def date_type(string: str):
    return datetime.strptime(string, "%Y-%m-%d")


def _get_json(url: str):
    """GET `url` reusing the browser auth from `curl_tokens`, return parsed JSON."""
    request = urllib.request.Request(url, headers=parse_curl_headers())
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
        except (TypeError, ValueError):
            continue
    return None


def is_peer_reviewed(paper: dict, start=None, end=None) -> bool:
    """Whether `paper` has a peer-reviewed release dated within [start, end].

    `start`/`end` are `date` objects (or None for an open bound). A release
    counts when its venue type is peer-reviewed (not preprint/unknown) and its
    date falls inside the window.
    """
    for release in paper.get("releases") or []:
        venue = release.get("venue") or {}
        venue_type = venue.get("type")
        if venue_type is None or venue_type in NON_PEER_REVIEWED_VENUES:
            continue
        released = _venue_date(venue)
        if released is None:
            continue
        if (start is None or released >= start) and (end is None or released <= end):
            return True
    return False


def normalize(paper: dict) -> dict:
    # Downstream consumers (utils.Paper, download_convert, query) key on
    # `paper_id`. The new API exposes the canonical id as `id`; map it across so
    # the rest of the pipeline keeps working unchanged.
    return {**paper, "paper_id": paper["id"]}


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

    if not options.all_valid:
        start_date = options.start.date() if options.start else None
        end_date = options.end.date() if options.end else None
        papers = [
            paper
            for paper in papers
            if is_peer_reviewed(paper, start_date, end_date)
        ]
        logger.info(f"Kept {len(papers)} peer-reviewed papers")

    papers = [normalize(paper) for paper in papers]
    output.write_text(json.dumps(papers, indent=2))

    # Check that the output is a valid JSON
    try:
        json.loads(output.read_text())
    except json.decoder.JSONDecodeError as e:
        logger.error(f"Paperoni report is not a valid JSON: {e}", exc_info=True)


if __name__ == "__main__":
    main()
