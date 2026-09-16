from __future__ import annotations

import argparse
import asyncio
import collections
import hashlib
import json
import os
import shutil
import subprocess
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from paperext import CFG
from paperext.dashboard import Dashboard
from paperext.log import logger
from paperext.utils import Paper

# Config's attribute access is typed as `Config | Path`; the sections used here
# are known, so read them through an untyped alias rather than casting each use.
_CFG: Any = CFG

PROG = f"{Path(__file__).stem.replace('_', '-')}"

DESCRIPTION = """
Utility to download and convert a list of papers' pdfs -> txts.

PDFs are located and downloaded by paperoni's fulltext resolver (arxiv,
openreview, mlr, direct pdf links, and DOIs through CrossRef / OpenAlex /
publisher APIs), configured by the yaml file at $PAPERONI_CONFIG. Converted
texts land in <cache-dir>/fulltext/<paper_id>/fulltext.txt.

stdout will contain the list of files successfully converted separated by '\\n'.
A per-paper JSON report (refs tried, source, error) is written next to the
logs so download drop-out can be quantified.
"""

EPILOG = f"""
Example:
  $ PAPEREXT_LOGGING_LEVEL=INFO {PROG} --paperoni data/paperoni-2026-01-01-2026-12-31-PR_2026-09-16.json
    [DEBUG]
    data/cache/fulltext/69a5fd5448887d403d0a4e4b/fulltext.txt
    ...
    Successfully downloaded and converted 23 out of 45 papers
    arxiv:20/20
    doi.crossref:1/1
    doi.openalex:2/2
    no-fulltext:0/22
  $ {PROG} --paperoni papers.json > data/query_set.txt
"""

#: Ref types paperoni's fulltext locator resolves, in the order they are tried
#: for a paper: cheapest and most reliable first. `get_pdf` stops at the first
#: ref that yields a PDF.
REF_TYPES = ("arxiv", "openreview", "mlr", "pdf", "doi")


@dataclass
class Outcome:
    """What happened to one paper."""

    paper_id: str
    title: str
    refs: list[str] = field(default_factory=list)
    text: Path | None = None
    #: "existing" (already converted) or the resolver that produced the PDF's
    #: URL (arxiv, openreview, doi.crossref, doi.openalex, ...)
    source: str | None = None
    error: str | None = None

    @property
    def link_type(self) -> str:
        # Bucket for the per-resolver tally logged at the end.
        return self.source or ("no-refs" if not self.refs else "no-fulltext")

    @property
    def bucket(self) -> str:
        """Dashboard row: the best link type the paper had *before* downloading
        (so hits + misses per row is meaningful), or "existing"."""
        if self.source == "existing":
            return "existing"
        return self.refs[0].split(":", 1)[0] if self.refs else "no-refs"


def refs_for(links: Iterable[dict[str, Any]]) -> list[str]:
    """Turn paperoni `links` into fulltext refs (`type:id`), ordered by REF_TYPES.

    Handles both link shapes seen in the wild: bare ids (`arxiv.pdf` +
    `2307.00134`, old reports) and full URLs (`arxiv` +
    `https://arxiv.org/abs/2307.00134`, the current API with `expand_links`).
    Abstract-only types (dblp, semantic_scholar, pubmed, ...) are dropped: the
    locator cannot turn them into a PDF.
    """
    from paperoni.utils import url_to_id

    refs: dict[str, None] = {}
    for link in links:
        base = link["type"].split(".")[0]
        target = link["link"]
        if target.startswith("http"):
            typed = url_to_id(target)
            if typed is None and base == "pdf":
                # A direct PDF URL that no extractor recognises (jmlr, ...).
                typed = ("pdf", target)
        else:
            typed = (base, target)
        if typed and typed[0] in REF_TYPES:
            refs[f"{typed[0]}:{typed[1]}"] = None

    return sorted(refs, key=lambda ref: REF_TYPES.index(ref.split(":", 1)[0]))


def pdf_to_text(pdf: Path, text: Path) -> Path | None:
    """Convert `pdf` to `text` with pdftotext; None (and no partial file) on failure."""
    if text.exists():
        return text

    # pdftotext comes from https://poppler.freedesktop.org/
    cmd = ["pdftotext", str(pdf), str(text)]
    # Redirect stderr to stdout to then redirect the combined stdout and
    # stderr to stderr
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    logger.info(p.stdout)

    if p.returncode:
        logger.error(
            f"Failed to convert {pdf} to {text}: {cmd} returned {p.returncode}"
        )
        text.unlink(missing_ok=True)
        return None

    return text


def _describe(exc: BaseException) -> str:
    """One-line description of a (possibly grouped) download failure."""
    if isinstance(exc, BaseExceptionGroup):
        return "; ".join(_describe(e) for e in exc.exceptions) or str(exc)
    return f"{type(exc).__name__}: {exc}"[:300]


async def fetch_pdf(refs: list[str], pdf_file: Path) -> tuple[Path, str]:
    """Locate + download the first available PDF for `refs` into `pdf_file`.

    Returns the file and where it came from. Raises when no ref yields a PDF.
    """
    from paperoni.fulltext.pdf import CachePolicies, get_pdf

    # The resolver keeps its own cache (data_path/pdf/<url hash>/); a repeat run
    # is served from it without touching the network.
    pdf = await get_pdf(refs, cache_policy=CachePolicies.USE)
    source = pdf.source.info

    pdf_file.parent.mkdir(parents=True, exist_ok=True)
    if not pdf_file.exists():
        try:
            pdf_file.hardlink_to(pdf.pdf_path)
        except OSError:
            shutil.copyfile(pdf.pdf_path, pdf_file)

    return pdf_file, source


async def download_paper(
    paper_data: dict[str, Any], cache_dir: Path, semaphore: asyncio.Semaphore
) -> Outcome:
    outcome = Outcome(paper_id=paper_data["paper_id"], title=paper_data["title"])
    paper = Paper(paper_data)

    if paper.pdfs:
        outcome.text = paper.get_link_id_pdf()
        outcome.source = "existing"
        return outcome

    outcome.refs = refs_for(paper_data["links"])
    if not outcome.refs:
        outcome.error = "no locatable links"
        logger.warning(f"{outcome.paper_id}:{outcome.title}: {outcome.error}")
        return outcome

    # Paperoni records land in fulltext/<paper_id>/ (utils.Paper's
    # PAPER_ID_FULLTEXT_TEMPLATE); the --arxiv convenience keeps the historical
    # arxiv/<id>.txt layout that `query --arxiv` reads.
    pdf_file = cache_dir / paper_data.get(
        "_pdf", f"fulltext/{outcome.paper_id}/fulltext.pdf"
    )

    async with semaphore:
        try:
            pdf_file, outcome.source = await fetch_pdf(outcome.refs, pdf_file)
        except Exception as e:
            outcome.error = _describe(e)
            logger.error(
                f"Failed to download {outcome.paper_id}:{outcome.title} "
                f"from {outcome.refs}: {outcome.error}"
            )
            return outcome

    # pdftotext is CPU-bound and blocking; keep it off the event loop.
    outcome.text = await asyncio.to_thread(
        pdf_to_text, pdf_file, pdf_file.with_suffix(".txt")
    )
    if outcome.text is None:
        outcome.error = "pdftotext failed"

    return outcome


async def download_all(
    papers: list[dict[str, Any]],
    cache_dir: Path,
    concurrency: int,
    advance: Callable[[Outcome], None] = lambda outcome: None,
) -> list[Outcome]:
    """Download `papers` with at most `concurrency` in flight; `advance` is
    called with each outcome as it finishes (dashboard hook)."""
    semaphore = asyncio.Semaphore(concurrency)

    async def one(paper: dict[str, Any]) -> Outcome:
        outcome = await download_paper(paper, cache_dir, semaphore)
        advance(outcome)
        return outcome

    return list(await asyncio.gather(*(one(paper) for paper in papers)))


def paperoni_config_file() -> Path:
    """The paperoni yaml config, from $PAPERONI_CONFIG (set by [env]) or the
    conventional location under the paperoni directory."""
    raw = os.environ.get("PAPERONI_CONFIG") or _CFG.env.paperoni_config
    path = Path(raw) if raw else _CFG.dir.paperoni / "config.yaml"
    if not path.is_absolute():
        path = _CFG.dir.root / path
    return path.resolve()


def run(
    papers: list[dict[str, Any]], cache_dir: Path, concurrency: int
) -> list[Outcome]:
    """Download + convert `papers` under the paperoni config; synchronous entry."""
    try:
        import gifnoc
    except ImportError as e:  # pragma: no cover - environment problem
        raise SystemExit(
            f"{PROG} needs paperoni: install the `fulltext` extra "
            "(uv sync --extra fulltext)"
        ) from e

    config_file = paperoni_config_file()
    if not config_file.exists():
        raise SystemExit(
            f"paperoni config not found at {config_file}; copy "
            f"{_CFG.dir.paperoni / 'config.example.yaml'} there and fill it in"
        )

    # The dashboard (logs / stats / progress) draws on stderr when it is a
    # terminal, and in every case moves paperoni's stdout progress prints off
    # stdout so `download-convert ... > query_set.txt` stays a file list.
    with (
        gifnoc.use(str(config_file)),
        Dashboard(len(papers), "download-convert") as dashboard,
    ):
        return asyncio.run(
            download_all(
                papers,
                cache_dir,
                concurrency,
                lambda outcome: dashboard.advance(
                    outcome.bucket, outcome.text is not None
                ),
            )
        )


def synthetic_papers(
    arxiv_ids: Iterable[str], urls: Iterable[str]
) -> list[dict[str, Any]]:
    """Paper records for the --arxiv / --url conveniences."""
    papers = [
        {
            "paper_id": arxiv_id,
            "title": f"arxiv:{arxiv_id}",
            "links": [{"type": "arxiv.pdf", "link": arxiv_id}],
            "_pdf": f"arxiv/{arxiv_id}.pdf",
        }
        for arxiv_id in arxiv_ids
    ]
    for url in urls:
        papers.append(
            {
                "paper_id": hashlib.sha256(url.encode()).hexdigest(),
                "title": url,
                "links": [{"type": "pdf", "link": url}],
            }
        )
    return papers


def write_report(outcomes: list[Outcome], report: Path) -> None:
    report.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for o in outcomes:
        record = asdict(o)
        record["text"] = str(o.text) if o.text else None
        records.append(record)
    report.write_text(json.dumps(records, indent=2))


def log_summary(
    outcomes: list[Outcome], write: Callable[[str], None] = logger.info
) -> None:
    completed = [o for o in outcomes if o.text]
    write(
        f"Successfully downloaded and converted {len(completed)} out of "
        f"{len(outcomes)} papers"
    )
    by_type: dict[str, list[bool]] = collections.defaultdict(list)
    for o in outcomes:
        by_type[o.link_type].append(o.text is not None)
    for t in sorted(by_type):
        write(f"{t}:{sum(by_type[t])}/{len(by_type[t])}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--paperoni",
        metavar="JSON",
        type=Path,
        help="Paperoni json output of papers to download and convert pdfs -> txts",
    )
    parser.add_argument(
        "--arxiv",
        metavar="STR",
        nargs="+",
        default=tuple(),
        help="List of arXiv ids use to download and convert pdfs -> txts",
    )
    parser.add_argument(
        "--url",
        metavar="STR",
        nargs="+",
        default=tuple(),
        help="List of pdf urls to download and convert pdfs -> txts",
    )
    parser.add_argument(
        "--cache-dir",
        metavar="DIR",
        type=Path,
        default=_CFG.dir.cache,
        help="Directory to store downloaded and converted pdfs -> txts",
    )
    parser.add_argument(
        "--concurrency",
        metavar="N",
        type=int,
        default=8,
        help="Papers downloaded in parallel (default 8; requests to one host are "
        "further capped by the paperoni config's fetch.simultaneous)",
    )
    parser.add_argument(
        "--report",
        metavar="JSON",
        type=Path,
        default=None,
        help="Per-paper outcome report (default: <log dir>/download-convert_<timestamp>.json)",
    )
    options = parser.parse_args(argv)

    options.cache_dir.mkdir(parents=True, exist_ok=True)

    papers = json.loads(options.paperoni.read_text()) if options.paperoni else []
    papers += synthetic_papers(options.arxiv, options.url)

    outcomes = run(papers, options.cache_dir, options.concurrency)

    report = options.report or (
        _CFG.dir.log / f"download-convert_{datetime.now():%Y%m%d_%H%M%S}.json"
    )
    write_report(outcomes, report)

    print(*sorted(str(o.text) for o in outcomes if o.text), sep="\n")
    log_summary(outcomes)
    logger.info(f"Report: {report}")


if __name__ == "__main__":
    main()
