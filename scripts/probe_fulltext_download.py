"""Probe Paperoni's server-side fulltext cache for a corpus window.

For every valid + peer-reviewed paper in [--start, --end] (same selection as
``paperoni-report``), ask ``GET /api/v1/fulltext/download`` for the paper's
locatable refs (``type:link`` for the link types the server's locator handles).
The endpoint is cache-only (``cache_policy=no_download``): it streams the PDF
when the server already holds it and errors otherwise, so the hit rate tells us
how much of C1 (#13) can be served from the server instead of re-downloaded
from publishers.

Token: ``PAPEREXT_PAPERONI_TOKEN`` in the environment, or the first line of
``paperoni/curl_tokens`` (gitignored), with or without the ``Bearer `` prefix.

Example:
  $ .venv/bin/python scripts/probe_fulltext_download.py \\
        --start 2026-01-01 --end 2026-12-31 --save-dir data/cache/server-pdf
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOKEN_FILE = REPO / "paperoni" / "curl_tokens"


def load_token() -> str:
    token = os.environ.get("PAPEREXT_PAPERONI_TOKEN", "").strip()
    if not token and TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text().strip().splitlines()[0].strip()
    token = token.removeprefix("Bearer ").strip()
    if not token:
        sys.exit(
            "No Paperoni token: export PAPEREXT_PAPERONI_TOKEN or put the bearer "
            f"token in {TOKEN_FILE}"
        )
    # report.py reads CFG.paperoni.token, which the env var overrides.
    os.environ["PAPEREXT_PAPERONI_TOKEN"] = token
    return token


# Link types the server's fulltext locator knows how to turn into a PDF URL
# (paperoni/fulltext/locate.py). Others (doi.abstract, corpusid, dblp, ...)
# are abstract pages and never yield a PDF.
LOCATABLE = ("arxiv", "openreview", "mlr", "pdf", "pdf.official", "doi")


def refs_for(paper: dict) -> list[str]:
    refs: list[str] = []
    for link in paper.get("links") or []:
        typ = link["type"]
        base = typ.split(".")[0]
        if typ in LOCATABLE or base in ("arxiv", "openreview", "mlr", "pdf", "doi"):
            # The locator dispatches on the base type (arxiv.pdf -> arxiv);
            # keep pdf.official verbatim since it is its own case.
            ref_type = typ if typ == "pdf.official" else base
            ref = f"{ref_type}:{link['link']}"
            if ref not in refs:
                refs.append(ref)
    return refs


def download(
    base_url: str, token: str, refs: list[str], timeout: float, via: str
) -> tuple[int | str, str, bytes]:
    """One request; return (status, content-type, payload). Status is 'ERR' on
    a transport failure.

    `via="body"` is what the OpenAPI spec declares (GET + JSON body), but the
    Google Frontend in front of paperoni.mila.quebec rejects any GET carrying a
    body with an HTML 400 before it reaches the app. `via="query"` sends the
    refs as repeated `?ref=` query params instead (the transport `/search`
    uses); the app only honors it if the endpoint parses query params.
    """
    url = f"{base_url}/api/v1/fulltext/download"
    headers = {"Authorization": f"Bearer {token}"}
    data = None
    if via == "body":
        data = json.dumps({"ref": refs, "cache_policy": "no_download"}).encode()
        headers["Content-Type"] = "application/json"
    else:
        query = [("ref", r) for r in refs] + [("cache_policy", "no_download")]
        url += "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(url, data=data, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
            ctype = response.headers.get("Content-Type", "")
            return response.status, ctype, payload
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read()[:500]
    except (urllib.error.URLError, TimeoutError) as e:
        return "ERR", "", str(e).encode()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--start", default="2026-01-01", metavar="YYYY-MM-DD")
    parser.add_argument("--end", default="2026-12-31", metavar="YYYY-MM-DD")
    parser.add_argument("--limit", type=int, default=0, help="probe only N papers")
    parser.add_argument(
        "--paperoni",
        type=Path,
        help="reuse a paperoni-report JSON instead of fetching",
    )
    parser.add_argument(
        "--save-dir", type=Path, help="write fetched PDFs here as <paper_id>.pdf"
    )
    parser.add_argument(
        "--report", type=Path, help="write per-paper results as JSON here"
    )
    parser.add_argument(
        "--via",
        choices=("body", "query", "auto"),
        default="auto",
        help="request transport; auto = body, then query if the proxy 400s",
    )
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--sleep", type=float, default=0.2, help="between requests")
    options = parser.parse_args(argv)

    token = load_token()

    sys.path.insert(0, str(REPO / "src"))
    from paperext import CFG  # noqa: E402  (after token export)
    from paperext.paperoni.report import (  # noqa: E402
        date_type,
        fetch_valid_papers,
        is_peer_reviewed,
        normalize,
    )

    if options.paperoni:
        papers = json.loads(options.paperoni.read_text())
    else:
        papers = fetch_valid_papers(options.start, options.end)
        start, end = date_type(options.start).date(), date_type(options.end).date()
        papers = [normalize(p) for p in papers if is_peer_reviewed(p, start, end)]
    if options.limit:
        papers = papers[: options.limit]
    print(f"{len(papers)} papers in window {options.start}..{options.end}")

    base_url = CFG.paperoni.url.rstrip("/")
    results = []
    by_status: collections.Counter = collections.Counter()
    hit_types: collections.Counter = collections.Counter()
    miss_types: collections.Counter = collections.Counter()
    no_refs = 0

    for i, paper in enumerate(papers, 1):
        refs = refs_for(paper)
        record = {
            "paper_id": paper["paper_id"],
            "title": paper["title"],
            "refs": refs,
            "link_types": sorted({l["type"] for l in paper.get("links") or []}),
        }
        if not refs:
            no_refs += 1
            record["status"] = "NO_REFS"
            results.append(record)
            print(f"[{i}/{len(papers)}] NO_REFS  {paper['title'][:70]}")
            continue

        t0 = time.time()
        via = "body" if options.via == "auto" else options.via
        status, ctype, payload = download(base_url, token, refs, options.timeout, via)
        if options.via == "auto" and status == 400 and b"<html" in payload[:100]:
            via = "query"
            status, ctype, payload = download(
                base_url, token, refs, options.timeout, via
            )
        elapsed = time.time() - t0
        is_pdf = status == 200 and payload[:5] == b"%PDF-"
        record.update(
            via=via,
            status=status,
            content_type=ctype,
            bytes=len(payload) if status == 200 else 0,
            is_pdf=is_pdf,
            seconds=round(elapsed, 2),
        )
        if status == 200 and not is_pdf:
            record["detail"] = payload[:200].decode(errors="replace")
        elif status != 200:
            record["detail"] = payload[:300].decode(errors="replace")
        results.append(record)

        key = "HIT" if is_pdf else str(status)
        by_status[key] += 1
        for r in refs:
            (hit_types if is_pdf else miss_types)[r.split(":", 1)[0]] += 1
        print(
            f"[{i}/{len(papers)}] {key:<4} {via:<5} {elapsed:5.1f}s "
            f"{len(payload) if is_pdf else 0:>9}B  {paper['title'][:60]}"
            + ("" if is_pdf else f"  -- {record.get('detail', '')[:120]!r}")
        )

        if is_pdf and options.save_dir:
            options.save_dir.mkdir(parents=True, exist_ok=True)
            (options.save_dir / f"{paper['paper_id']}.pdf").write_bytes(payload)

        time.sleep(options.sleep)

    total = len(papers)
    hits = by_status["HIT"]
    print("\n=== summary ===")
    print(f"papers: {total}   hits: {hits} ({100 * hits / max(total, 1):.1f}%)")
    print(f"no locatable refs: {no_refs}")
    print("by status:", dict(by_status))
    print("ref types on hits:  ", dict(hit_types))
    print("ref types on misses:", dict(miss_types))

    if options.report:
        options.report.parent.mkdir(parents=True, exist_ok=True)
        options.report.write_text(json.dumps(results, indent=2))
        print(f"per-paper report: {options.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
