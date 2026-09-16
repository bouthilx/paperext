from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

import paperext.download_convert as dc
from paperext.config import Config

NEW_API_LINKS = [
    {"type": "doi", "link": "https://doi.org/10.48550/arXiv.2605.14117"},
    {"type": "doi", "link": "https://doi.org/10.18653/v1/2026.findings-acl.1326"},
    {"type": "openreview", "link": "https://openreview.net/forum?id=ZMmDwqjQN9"},
    {"type": "openreview", "link": "https://openreview.net/pdf?id=ZMmDwqjQN9"},
    {"type": "arxiv", "link": "https://arxiv.org/abs/2605.14117"},
    {"type": "arxiv", "link": "https://arxiv.org/pdf/2605.14117"},
    {"type": "semantic_scholar", "link": "https://www.semanticscholar.org/paper/abc"},
    {"type": "dblp", "link": "https://dblp.org/rec/conf/acl/x"},
]

OLD_REPORT_LINKS = [
    {"type": "doi.abstract", "link": "10.1016/j.neunet.2024.106793"},
    {"type": "corpusid", "link": "259316664"},
    {"type": "arxiv.abstract", "link": "2307.00134"},
    {"type": "arxiv.pdf", "link": "2307.00134"},
    {"type": "pdf", "link": "http://export.arxiv.org/pdf/2307.00134"},
    {
        "type": "pdf.official",
        "link": "https://jmlr.org/papers/volume25/23-0154/23-0154.pdf",
    },
    {"type": "html", "link": "https://aclanthology.org/2024.findings-emnlp.564"},
    {"type": "mlr.abstract", "link": "253/mlodozeniec24a"},
    {"type": "openreview.pdf", "link": "6FfwQvbZ7l"},
]


def test_refs_for_new_api_links():
    # URL-valued links are mapped to type:id, de-duplicated, abstract-only
    # sources dropped, and ordered cheapest-first.
    assert dc.refs_for(NEW_API_LINKS) == [
        "arxiv:2605.14117",
        "openreview:ZMmDwqjQN9",
        "doi:10.48550/arXiv.2605.14117",
        "doi:10.18653/v1/2026.findings-acl.1326",
    ]


def test_refs_for_old_report_links():
    # Bare ids keep their base type; a pdf URL no extractor knows is passed
    # through as a direct pdf ref; html is not locatable.
    assert dc.refs_for(OLD_REPORT_LINKS) == [
        "arxiv:2307.00134",
        "openreview:6FfwQvbZ7l",
        "mlr:253/mlodozeniec24a",
        "pdf:https://jmlr.org/papers/volume25/23-0154/23-0154.pdf",
        "doi:10.1016/j.neunet.2024.106793",
    ]


def test_refs_for_nothing_locatable():
    assert dc.refs_for([{"type": "pubmed.abstract", "link": "39426036"}]) == []


def test_describe_exception_group():
    group = ExceptionGroup(
        "No fulltext found", [ValueError("bad"), RuntimeError("worse")]
    )
    assert dc._describe(group) == "ValueError: bad; RuntimeError: worse"
    assert dc._describe(KeyError("x")) == "KeyError: 'x'"


@dataclass
class _URL:
    url: str
    info: str


@dataclass
class _PDF:
    source: _URL
    pdf_path: Path


@pytest.fixture
def fake_resolver(monkeypatch, tmp_path: Path):
    """Stand in for paperoni.fulltext.pdf.get_pdf and pdftotext."""
    import paperoni.fulltext.pdf

    store = tmp_path / "paperoni-store"
    calls: list[list[str]] = []

    async def get_pdf(refs, cache_policy=None):
        calls.append(list(refs))
        for ref in refs:
            if ref.startswith("doi:10.1109/"):
                # IEEE: nothing found for any reference
                continue
            info = ref.split(":", 1)[0]
            pdf = store / ref.replace("/", "_") / "fulltext.pdf"
            pdf.parent.mkdir(parents=True, exist_ok=True)
            pdf.write_bytes(b"%PDF-1.4 fake " + ref.encode())
            return _PDF(source=_URL(url=f"https://x/{ref}", info=info), pdf_path=pdf)
        raise ExceptionGroup("No fulltext found", [RuntimeError("403 for " + refs[0])])

    def pdf_to_text(pdf: Path, text: Path):
        if b"unconvertible" in pdf.read_bytes():
            return None
        text.write_text(pdf.read_bytes().decode())
        return text

    monkeypatch.setattr(paperoni.fulltext.pdf, "get_pdf", get_pdf)
    monkeypatch.setattr(dc, "pdf_to_text", pdf_to_text)
    return calls


def _paper(paper_id: str, links: list[dict], title: str = "T") -> dict:
    return {"paper_id": paper_id, "title": title, "links": links}


def test_download_all(cfg: Config, fake_resolver, tmp_path: Path):
    cache_dir = tmp_path / "cache"
    papers = [
        _paper("new1", NEW_API_LINKS),
        _paper("ieee", [{"type": "doi", "link": "https://doi.org/10.1109/tpwrd.1"}]),
        _paper("none", [{"type": "pubmed.abstract", "link": "1"}]),
        _paper("old1", OLD_REPORT_LINKS),
    ]
    outcomes = asyncio.run(dc.download_all(papers, cache_dir, concurrency=2))
    by_id = {o.paper_id: o for o in outcomes}

    ok = by_id["new1"]
    assert ok.text == cache_dir / "fulltext/new1/fulltext.txt"
    assert ok.text.read_text().endswith("arxiv:2605.14117")
    assert ok.source == "arxiv" and ok.error is None
    # The PDF is linked into the paperext layout next to the text
    assert (cache_dir / "fulltext/new1/fulltext.pdf").exists()

    assert by_id["old1"].text == cache_dir / "fulltext/old1/fulltext.txt"

    failed = by_id["ieee"]
    assert failed.text is None and failed.source is None
    assert failed.error is not None
    assert failed.error.startswith("RuntimeError: 403 for doi:10.1109/tpwrd.1")
    assert failed.link_type == "no-fulltext"

    assert by_id["none"].error == "no locatable links"
    assert by_id["none"].link_type == "no-refs"
    # The resolver is not consulted for papers without refs
    assert sorted(c[0] for c in fake_resolver) == [
        "arxiv:2307.00134",
        "arxiv:2605.14117",
        "doi:10.1109/tpwrd.1",
    ]


def test_download_existing_is_not_refetched(cfg: Config, fake_resolver, tmp_path):
    # tests/data/cache/arxiv/2304.07193.txt exists: utils.Paper finds it and no
    # download happens.
    paper = _paper("whatever", [{"type": "arxiv.pdf", "link": "2304.07193"}])
    (outcome,) = asyncio.run(dc.download_all([paper], tmp_path, concurrency=1))
    assert outcome.source == "existing"
    dirs: Any = cfg.dir
    assert outcome.text == dirs.cache / "arxiv/2304.07193.txt"
    assert fake_resolver == []


def test_download_pdftotext_failure(cfg: Config, fake_resolver, tmp_path, monkeypatch):
    monkeypatch.setattr(dc, "pdf_to_text", lambda pdf, text: None)
    paper = _paper("p", [{"type": "arxiv.pdf", "link": "1234.00001"}])
    (outcome,) = asyncio.run(dc.download_all([paper], tmp_path, concurrency=1))
    assert outcome.text is None
    assert outcome.source == "arxiv"
    assert outcome.error == "pdftotext failed"


def test_synthetic_papers_keep_arxiv_layout(cfg: Config, fake_resolver, tmp_path):
    papers = dc.synthetic_papers(["1234.00001"], ["https://jmlr.org/x.pdf"])
    outcomes = asyncio.run(dc.download_all(papers, tmp_path, concurrency=1))
    # `query --arxiv` reads <cache>/arxiv/<id>.txt
    assert outcomes[0].text == tmp_path / "arxiv/1234.00001.txt"
    assert outcomes[1].source == "pdf"
    assert outcomes[1].text is not None
    assert outcomes[1].text.name == "fulltext.txt"


def test_write_report_and_summary(tmp_path: Path):
    outcomes = [
        dc.Outcome("a", "A", refs=["arxiv:1"], text=Path("x.txt"), source="arxiv"),
        dc.Outcome("b", "B", refs=["doi:1"], error="boom"),
        dc.Outcome("c", "C", refs=[], error="no locatable links"),
    ]
    report = tmp_path / "r" / "report.json"
    dc.write_report(outcomes, report)
    assert '"text": "x.txt"' in report.read_text()

    lines: list[str] = []
    dc.log_summary(outcomes, lines.append)
    assert lines == [
        "Successfully downloaded and converted 1 out of 3 papers",
        "arxiv:1/1",
        "no-fulltext:0/1",
        "no-refs:0/1",
    ]


def test_paperoni_config_file(cfg: Config, monkeypatch):
    dirs: Any = cfg.dir
    monkeypatch.setenv("PAPERONI_CONFIG", "paperoni/custom.yaml")
    assert dc.paperoni_config_file() == (dirs.root / "paperoni/custom.yaml").resolve()
    monkeypatch.setenv("PAPERONI_CONFIG", "/abs/config.yaml")
    assert dc.paperoni_config_file() == Path("/abs/config.yaml")
