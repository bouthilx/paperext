"""Stamp abstracts and OpenAlex research topics on a paperoni-report list.

About a third of the corpus has no fulltext (#13), and the misses concentrate
in paywalled clinical / biomedical journals. So that every paper still has
(a) an abstract and (b) a research-domain label independent of our extraction,
this script looks each record up on OpenAlex and writes, in place:

- ``abstract`` when the record has none, rebuilt from OpenAlex's
  ``abstract_inverted_index``, else fetched from Semantic Scholar, else from
  the arXiv API; ``abstract_source`` says where it came from (``paperoni`` for
  abstracts the record already had).
- ``openalex``: ``{id, domain, field, subfield, topic, is_oa, keywords,
  concepts}`` from the work's ``primary_topic`` (OpenAlex's hierarchy, e.g.
  *Health Sciences > Medicine > Oncology > <topic>*), ``open_access`` and
  keyword / concept lists -- the ``metadata`` tier input of C5 (#74).

Every HTTP response is cached under ``<cache-dir>/enrich/<service>/`` (200s and
404s), so a rerun on the same list is offline and a run interrupted midway
resumes where it was. Calls are paced per service (OpenAlex polite pool,
Semantic Scholar and arXiv ask for ~1 and 3 s between requests).
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from paperext import CFG
from paperext.dashboard import Dashboard
from paperext.download_convert import venue_of
from paperext.log import logger

# Config's attribute access is typed as `Config | Path`; the sections used here
# are known, so read them through an untyped alias rather than casting each use.
_CFG: Any = CFG

PROG = "paperoni-enrich"

DESCRIPTION = """
Stamp abstracts and OpenAlex research topics on the papers of a paperoni-report
JSON, in place (or to --output).

For each paper: `abstract` (+ `abstract_source`) when missing -- OpenAlex, then
Semantic Scholar, then arXiv -- and `openalex` {id, domain, field, subfield,
topic, is_oa, keywords, concepts} from the OpenAlex work's primary topic.
Papers are looked up by DOI, OpenAlex id or arXiv id, in that order.

Responses are cached under <cache-dir>/enrich, so reruns are offline and an
interrupted run resumes. The run ends with a coverage summary (abstracts
before/after, topics).
"""

EPILOG = f"""
Example:
  $ PAPEREXT_LOGGING_LEVEL=INFO {PROG} data/paperoni-2026-01-01-2026-02-01-PR_2026-09-16.json \\
      --mailto you@mila.quebec --report logs/enrich-2026.json
    ...
    Abstracts: 30/45 before, 43/45 after (openalex:10 semantic_scholar:2 arxiv:1)
    OpenAlex topics: 44/45
"""

OPENALEX_API = "https://api.openalex.org"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
ARXIV_API = "https://export.arxiv.org/api/query"

#: The fields fetched from an OpenAlex work; anything else is dead weight.
OPENALEX_SELECT = (
    "id,doi,abstract_inverted_index,primary_topic,keywords,concepts,open_access,ids"
)

#: Seconds between two requests to the same service. OpenAlex's polite pool
#: allows 10/s; Semantic Scholar's anonymous pool is shared and throttles
#: below 1/s; arXiv asks for 3 s.
PACING = {"openalex": 0.1, "semantic_scholar": 3.0, "arxiv": 3.0}

#: Attempts on a 429 / 5xx before giving up on the request (not cached),
#: `BACKOFF` * attempt seconds apart. A service still throttling after that
#: (Semantic Scholar's anonymous pool is shared and bursty) is left alone for
#: `COOLDOWN` seconds instead of stalling every paper.
RETRIES = 3
BACKOFF = 10.0
COOLDOWN = 60.0

#: OpenAlex concepts (the legacy tagging) below this score are noise.
CONCEPT_MIN_SCORE = 0.3

_DOI_RE = re.compile(r"(10\.\d{4,9}/\S+)", re.I)
_ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/([^\s?#]+?)(?:v\d+)?(?:\.pdf)?$", re.I)
_ARXIV_ID_RE = re.compile(
    r"^(?:\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?$"
)
_OPENALEX_RE = re.compile(r"(W\d+)$")
_S2_RE = re.compile(r"semanticscholar\.org/paper/([0-9a-f]{40})", re.I)
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$", re.I)
_ARXIV_DOI_RE = re.compile(r"^10\.48550/arxiv\.(.+)$", re.I)


# -- lookup keys ----------------------------------------------------------


def lookup_keys(paper: dict[str, Any]) -> list[tuple[str, str]]:
    """The ``(kind, id)`` handles a paper can be looked up by, best first.

    Kinds are ``doi``, ``openalex`` (``W...``), ``arxiv`` and ``s2`` (Semantic
    Scholar sha). Publisher DOIs come first: they name the published version.
    arXiv DOIs (``10.48550/arXiv.<id>``) are folded into the arXiv id. Links
    carry either URLs (the current API with ``expand_links``) or bare ids (old
    reports); both are handled. Semantic Scholar shas only serve its own
    abstract fallback.
    """
    dois: dict[str, None] = {}
    openalex: dict[str, None] = {}
    arxiv: dict[str, None] = {}
    s2: dict[str, None] = {}

    for link in paper.get("links") or []:
        base = str(link.get("type", "")).split(".")[0]
        target = str(link.get("link", "")).strip()
        if not target:
            continue
        if base == "doi":
            m = _DOI_RE.search(target)
            if m:
                doi = m.group(1).rstrip("/")
                arxiv_doi = _ARXIV_DOI_RE.match(doi)
                if arxiv_doi:
                    arxiv.setdefault(re.sub(r"v\d+$", "", arxiv_doi.group(1)), None)
                else:
                    dois.setdefault(doi, None)
        elif base == "arxiv":
            m = _ARXIV_RE.search(target)
            arxiv_id = m.group(1) if m else target
            arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
            if _ARXIV_ID_RE.match(arxiv_id):
                arxiv.setdefault(arxiv_id, None)
        elif base == "openalex":
            m = _OPENALEX_RE.search(target)
            if m:
                openalex.setdefault(m.group(1), None)
        elif base == "semantic_scholar":
            m = _S2_RE.search(target)
            sha = m.group(1) if m else target
            if _SHA1_RE.match(sha):
                s2.setdefault(sha.lower(), None)

    discovered = ((paper.get("info") or {}).get("discovered_by") or {}).get("openalex")
    m = _OPENALEX_RE.search(discovered) if isinstance(discovered, str) else None
    if m:
        openalex.setdefault(m.group(1), None)

    # DOIs differ only by case between sources; OpenAlex is case-insensitive.
    def unique(ids: Iterable[str]) -> list[str]:
        seen: dict[str, str] = {}
        for i in ids:
            seen.setdefault(i.lower(), i)
        return list(seen.values())

    keys: list[tuple[str, str]] = []
    keys += [("doi", d) for d in unique(dois)]
    keys += [("openalex", w) for w in openalex]
    keys += [("arxiv", a) for a in arxiv]
    keys += [("s2", s) for s in s2]
    return keys


# -- HTTP with cache and pacing ---------------------------------------------

#: ``fetch(url, headers) -> (status, body)``; swapped for recorded responses
#: in tests.
Fetch = Callable[[str, dict[str, str]], tuple[int, str]]


def urllib_fetch(url: str, headers: dict[str, str]) -> tuple[int, str]:
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


class Client:
    """GETs with a per-URL JSON cache on disk and per-service pacing.

    Only 200s and 404s are cached: they are the answers; a 429 or a 5xx is
    retried a few times and then reported as a miss for this run only.
    """

    def __init__(
        self,
        cache_dir: Path,
        mailto: str | None = None,
        *,
        fetch: Fetch | None = None,
        pacing: dict[str, float] | None = None,
        refresh: bool = False,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.cache_dir = cache_dir
        self.mailto = mailto
        self.fetch: Fetch = fetch or urllib_fetch
        self.pacing = PACING if pacing is None else pacing
        self.refresh = refresh
        self.sleep = sleep
        self.clock = clock
        self._last: dict[str, float] = {}
        #: Service -> clock time until which it is skipped (kept answering
        #: 429 through the retries).
        self.throttled: dict[str, float] = {}
        self.requests = 0
        self.cache_hits = 0

    @property
    def headers(self) -> dict[str, str]:
        agent = f"paperext/{PROG}"
        if self.mailto:
            agent += f" (mailto:{self.mailto})"
        return {"User-Agent": agent, "Accept": "application/json, */*"}

    def _cache_file(self, service: str, url: str) -> Path:
        digest = hashlib.sha256(url.encode()).hexdigest()
        return self.cache_dir / service / f"{digest}.json"

    def get(self, service: str, url: str) -> tuple[int, str]:
        """``(status, body)`` for `url`, from the cache when it has it."""
        cache_file = self._cache_file(service, url)
        if not self.refresh and cache_file.exists():
            cached = json.loads(cache_file.read_text())
            self.cache_hits += 1
            return int(cached["status"]), str(cached["body"])

        if self.clock() < self.throttled.get(service, -1e9):
            return 429, ""

        status, body = 0, ""
        for attempt in range(RETRIES):
            wait = self._last.get(service, -1e9) + self.pacing.get(service, 0.0)
            now = self.clock()
            if wait > now:
                self.sleep(wait - now)
            self.requests += 1
            self._last[service] = self.clock()
            status, body = self.fetch(url, self.headers)
            if status != 429 and status < 500:
                break
            logger.warning(f"{service}: HTTP {status} for {url}, retrying")
            self.sleep(BACKOFF * (attempt + 1))
        if status == 429:
            logger.warning(
                f"{service}: still rate-limited; skipped for {COOLDOWN:.0f} s"
            )
            self.throttled[service] = self.clock() + COOLDOWN

        if status in (200, 404):
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(
                json.dumps({"url": url, "status": status, "body": body})
            )
        return status, body

    def get_json(self, service: str, url: str) -> dict[str, Any] | None:
        """The parsed body of a 200, None for a 404 or anything unusable."""
        status, body = self.get(service, url)
        if status != 200:
            if status != 404:
                logger.warning(f"{service}: HTTP {status} for {url}")
            return None
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            logger.warning(f"{service}: not JSON for {url}")
            return None
        return payload if isinstance(payload, dict) else None


# -- OpenAlex ---------------------------------------------------------------


def openalex_urls(kind: str, ident: str, mailto: str | None) -> list[str]:
    """The OpenAlex requests that may resolve `ident`, in order.

    ``works/https://arxiv.org/abs/<id>`` is not a route (404). An arXiv id is
    tried as its DataCite DOI (``10.48550/arXiv.<id>``), then through a
    landing-page filter: each finds preprints the other misses.
    """
    params: dict[str, str] = {"select": OPENALEX_SELECT}
    if mailto:
        params["mailto"] = mailto

    def url(path: str, **extra: str) -> str:
        return f"{OPENALEX_API}{path}?{urllib.parse.urlencode({**params, **extra})}"

    if kind == "doi":
        return [url(f"/works/doi:{urllib.parse.quote(ident, safe='/:()')}")]
    if kind == "openalex":
        return [url(f"/works/{ident}")]
    if kind == "arxiv":
        return [
            url(f"/works/doi:10.48550/arxiv.{ident}"),
            url(
                "/works",
                filter=f"locations.landing_page_url:https://arxiv.org/abs/{ident}",
            ),
        ]
    return []


def openalex_work(client: Client, kind: str, ident: str) -> dict[str, Any] | None:
    """The OpenAlex work for one lookup key, or None."""
    for url in openalex_urls(kind, ident, client.mailto):
        payload = client.get_json("openalex", url)
        if payload is None:
            continue
        if "results" in payload:  # a filter query
            results = payload.get("results") or []
            if results:
                return results[0]
            continue
        return payload
    return None


def rebuild_abstract(inverted: dict[str, list[int]] | None) -> str | None:
    """OpenAlex stores abstracts as word -> positions; put the words back."""
    if not inverted:
        return None
    words = sorted(
        ((pos, word) for word, positions in inverted.items() for pos in positions)
    )
    text = " ".join(word for _, word in words).strip()
    return text or None


def _name(node: dict[str, Any] | None) -> str | None:
    return (node or {}).get("display_name") or None


def summarize_work(work: dict[str, Any]) -> dict[str, Any]:
    """The ``openalex`` field stamped on a record."""
    topic = work.get("primary_topic") or {}
    return {
        "id": str(work.get("id", "")).rsplit("/", 1)[-1] or None,
        "domain": _name(topic.get("domain")),
        "field": _name(topic.get("field")),
        "subfield": _name(topic.get("subfield")),
        "topic": _name(topic),
        "is_oa": (work.get("open_access") or {}).get("is_oa"),
        "keywords": [k["display_name"] for k in work.get("keywords") or [] if _name(k)],
        "concepts": [
            c["display_name"]
            for c in work.get("concepts") or []
            if _name(c) and (c.get("score") or 0.0) >= CONCEPT_MIN_SCORE
        ],
    }


# -- abstract fallbacks -----------------------------------------------------


def semantic_scholar_abstract(client: Client, kind: str, ident: str) -> str | None:
    if kind == "doi":
        ref = f"DOI:{ident}"
    elif kind == "arxiv":
        ref = f"arXiv:{ident}"
    elif kind == "s2":
        ref = ident
    else:
        return None
    url = f"{SEMANTIC_SCHOLAR_API}/paper/{urllib.parse.quote(ref, safe=':/')}?fields=abstract"
    payload = client.get_json("semantic_scholar", url)
    abstract = (payload or {}).get("abstract")
    return abstract.strip() if isinstance(abstract, str) and abstract.strip() else None


def arxiv_abstract(client: Client, arxiv_id: str) -> str | None:
    url = f"{ARXIV_API}?{urllib.parse.urlencode({'id_list': arxiv_id})}"
    status, body = client.get("arxiv", url)
    if status != 200:
        return None
    try:
        feed = ET.fromstring(body)
    except ET.ParseError:
        logger.warning(f"arxiv: unparsable feed for {arxiv_id}")
        return None
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    summary = feed.findtext("atom:entry/atom:summary", namespaces=ns)
    text = " ".join(summary.split()) if summary else ""
    return text or None


# -- per paper ----------------------------------------------------------------


@dataclass
class Enrichment:
    """What the run did to one paper (also the per-paper report record)."""

    paper_id: str
    title: str
    venue: str = "unknown"
    keys: list[str] = field(default_factory=list)
    openalex_id: str | None = None
    topic: str | None = None
    #: Where the abstract comes from: paperoni (already there), openalex,
    #: semantic_scholar, arxiv; None when no abstract could be found.
    abstract_source: str | None = None


def is_enriched(paper: dict[str, Any]) -> bool:
    """Nothing left to look up: abstract and topic are both there."""
    return bool(paper.get("abstract")) and bool(
        (paper.get("openalex") or {}).get("topic")
    )


def enrich_paper(paper: dict[str, Any], client: Client) -> Enrichment:
    """Stamp `abstract` / `abstract_source` / `openalex` on `paper`, in place."""
    keys = lookup_keys(paper)
    result = Enrichment(
        paper_id=str(paper.get("paper_id") or paper.get("id") or ""),
        title=str(paper.get("title", "")),
        venue=venue_of(paper),
        keys=[f"{kind}:{ident}" for kind, ident in keys],
    )
    if paper.get("abstract"):
        paper.setdefault("abstract_source", "paperoni")
        result.abstract_source = str(paper["abstract_source"])

    if is_enriched(paper):
        result.openalex_id = paper["openalex"].get("id")
        result.topic = paper["openalex"].get("topic")
        return result

    # One OpenAlex work usually settles it. When the first one lacks a topic
    # or an abstract (a freshly indexed publisher version, say), the other
    # handles of the paper -- typically its preprint -- are tried too, and
    # the missing pieces come from them.
    summary: dict[str, Any] | None = None
    abstract: str | None = None
    for kind, ident in keys:
        work = openalex_work(client, kind, ident)
        if work is None:
            continue
        candidate = summarize_work(work)
        if summary is None or (not summary["topic"] and candidate["topic"]):
            summary = candidate
        abstract = abstract or rebuild_abstract(work.get("abstract_inverted_index"))
        if summary["topic"] and (abstract or paper.get("abstract")):
            break

    if summary is not None:
        paper["openalex"] = summary
        result.openalex_id = summary["id"]
        result.topic = summary["topic"]

    if not paper.get("abstract"):
        source: str | None = "openalex" if abstract else None
        if not abstract:
            for kind, ident in keys:
                abstract = semantic_scholar_abstract(client, kind, ident)
                if abstract:
                    source = "semantic_scholar"
                    break
        if not abstract:
            for kind, ident in keys:
                if kind == "arxiv":
                    abstract = arxiv_abstract(client, ident)
                    if abstract:
                        source = "arxiv"
                        break
        if abstract:
            paper["abstract"] = abstract
            paper["abstract_source"] = source
            result.abstract_source = source
    return result


def enrich_all(
    papers: list[dict[str, Any]],
    client: Client,
    advance: Callable[[Enrichment], None] = lambda _: None,
) -> list[Enrichment]:
    results: list[Enrichment] = []
    for paper in papers:
        try:
            result = enrich_paper(paper, client)
        except Exception as e:  # keep going: one paper must not sink the list
            logger.error(f"Failed to enrich {paper.get('paper_id')}: {e!r}")
            result = Enrichment(
                paper_id=str(paper.get("paper_id") or ""),
                title=str(paper.get("title", "")),
                venue=venue_of(paper),
                abstract_source=paper.get("abstract_source"),
            )
        logger.debug(
            f"{result.paper_id}: abstract={result.abstract_source} "
            f"topic={result.topic!r} ({result.openalex_id})"
        )
        results.append(result)
        advance(result)
    return results


# -- reporting ----------------------------------------------------------------


def write_report(results: list[Enrichment], report: Path) -> None:
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps([asdict(r) for r in results], indent=2))


def log_summary(
    results: list[Enrichment],
    abstracts_before: int,
    write: Callable[[str], None] = logger.info,
) -> None:
    total = len(results)
    sources = collections.Counter(
        r.abstract_source for r in results if r.abstract_source
    )
    found = " ".join(
        f"{source}:{count}"
        for source, count in sources.most_common()
        if source != "paperoni"
    )
    write(
        f"Abstracts: {abstracts_before}/{total} before, "
        f"{sum(sources.values())}/{total} after" + (f" ({found})" if found else "")
    )
    write(f"OpenAlex topics: {sum(1 for r in results if r.topic)}/{total}")


def default_mailto() -> str | None:
    """The `mailto` of the paperoni config, when there is one: the same
    contact paperoni's own OpenAlex requests carry."""
    from paperext.download_convert import paperoni_config_file

    config_file = paperoni_config_file()
    if not config_file.exists():
        return None
    try:
        import yaml

        config = yaml.safe_load(config_file.read_text()) or {}
    except Exception:  # a broken config is paperoni's problem, not ours
        return None
    mailto = (config.get("paperoni") or {}).get("mailto")
    return str(mailto) if mailto and "@" in str(mailto) else None


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "papers", metavar="JSON", type=Path, help="paperoni-report output to enrich"
    )
    parser.add_argument(
        "--output",
        metavar="JSON",
        type=Path,
        default=None,
        help="Where to write the enriched list (default: in place)",
    )
    parser.add_argument(
        "--cache-dir",
        metavar="DIR",
        type=Path,
        default=_CFG.dir.cache,
        help="Responses are cached under DIR/enrich (default: the config's cache)",
    )
    parser.add_argument(
        "--mailto",
        metavar="EMAIL",
        default=None,
        help="Contact for OpenAlex's polite pool (default: the paperoni config's "
        "mailto)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Ignore cached responses and query the services again",
    )
    parser.add_argument(
        "--report",
        metavar="JSON",
        type=Path,
        default=None,
        help="Per-paper report (keys tried, OpenAlex id, topic, abstract source)",
    )
    options = parser.parse_args(argv)

    papers: list[dict[str, Any]] = json.loads(options.papers.read_text())
    abstracts_before = sum(1 for p in papers if p.get("abstract"))
    mailto = options.mailto or default_mailto()
    if not mailto:
        logger.warning("No --mailto: OpenAlex requests go to the slower common pool")
    client = Client(Path(options.cache_dir) / "enrich", mailto, refresh=options.refresh)

    with Dashboard(len(papers), PROG, key="venue") as dashboard:
        results = enrich_all(
            papers,
            client,
            lambda result: dashboard.advance(
                result.venue, result.abstract_source is not None
            ),
        )

    output = options.output or options.papers
    output.write_text(json.dumps(papers, indent=2))
    if options.report:
        write_report(results, options.report)
    log_summary(results, abstracts_before)
    logger.info(
        f"{client.requests} requests, {client.cache_hits} cached responses; "
        f"wrote {output}"
    )


if __name__ == "__main__":
    main()
