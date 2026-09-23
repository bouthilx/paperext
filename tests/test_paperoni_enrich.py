from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from paperext.config import Config
from paperext.paperoni import enrich

FIXTURES = Path(__file__).parent / "data" / "enrich"

DOI = "10.1145/3770855.3817476"
ARXIV = "2509.23340"
W_PREPRINT = "W4414813482"
W_PUBLISHED = "W7196932608"
S2 = "d04dfb31220b5d7dae7bf4afa258064047fab683"

#: Recorded responses, keyed by a regex on the URL (the first match wins).
RECORDED: list[tuple[str, int, str]] = [
    (
        rf"openalex\.org/works/doi:{re.escape(DOI)}\?",
        200,
        "openalex-doi-W7196932608.json",
    ),
    (rf"openalex\.org/works/{W_PREPRINT}\?", 200, "openalex-W4414813482.json"),
    (rf"openalex\.org/works/doi:10\.48550/arxiv\.{re.escape(ARXIV)}\?", 404, ""),
    (
        rf"openalex\.org/works\?.*landing_page_url.*{re.escape(ARXIV)}",
        200,
        "openalex-filter-arxiv-2509.23340.json",
    ),
    (r"openalex\.org/", 404, ""),
    (
        rf"semanticscholar\.org/graph/v1/paper/DOI:{re.escape(DOI)}\?",
        200,
        "semanticscholar-DOI-10.1145-3770855.3817476.json",
    ),
    (r"semanticscholar\.org/", 404, ""),
    (
        rf"export\.arxiv\.org/api/query\?id_list={re.escape(ARXIV)}$",
        200,
        "arxiv-2509.23340.atom",
    ),
    (r"export\.arxiv\.org/", 200, "<feed xmlns='http://www.w3.org/2005/Atom'></feed>"),
]


class Recorder:
    """A `fetch` serving the recorded responses and logging every call."""

    def __init__(self, overrides: dict[str, tuple[int, str]] | None = None) -> None:
        self.calls: list[str] = []
        self.overrides = overrides or {}

    def __call__(self, url: str, headers: dict[str, str]) -> tuple[int, str]:
        self.calls.append(url)
        assert headers["User-Agent"].startswith("paperext/")
        for pattern, (status, body) in self.overrides.items():
            if re.search(pattern, url):
                return status, body
        for pattern, status, body in RECORDED:
            if re.search(pattern, url):
                if body and not body.startswith("<feed"):
                    body = (FIXTURES / body).read_text()
                return status, body
        raise AssertionError(f"unexpected request {url}")


@pytest.fixture
def recorder() -> Recorder:
    return Recorder()


@pytest.fixture
def client(recorder: Recorder, tmp_path: Path) -> enrich.Client:
    return enrich.Client(
        tmp_path / "enrich",
        "someone@example.org",
        fetch=recorder,
        sleep=lambda _: None,
    )


def _paper(**links: str) -> dict[str, Any]:
    return {
        "paper_id": "abc",
        "title": "CrediBench",
        "venue": "KDD",
        "links": [{"type": kind, "link": link} for kind, link in links.items()],
    }


# -- lookup keys ----------------------------------------------------------


def test_lookup_keys_from_api_links():
    paper = {
        "links": [
            {"type": "doi.abstract", "link": f"https://doi.org/10.48550/arXiv.{ARXIV}"},
            {"type": "doi.abstract", "link": f"https://doi.org/10.48550/arxiv.{ARXIV}"},
            {"type": "doi.abstract", "link": f"https://doi.org/{DOI}"},
            {"type": "doi.abstract", "link": f"https://doi.org/{DOI.upper()}"},
            {
                "type": "openreview.pdf",
                "link": "https://openreview.net/pdf?id=0Dh0eZ7w9O",
            },
            {"type": "arxiv.abstract", "link": f"https://arxiv.org/abs/{ARXIV}"},
            {"type": "arxiv.pdf", "link": f"https://arxiv.org/pdf/{ARXIV}v2"},
            {
                "type": "semantic_scholar.abstract",
                "link": f"https://www.semanticscholar.org/paper/{S2}",
            },
            {"type": "openalex.abstract", "link": f"https://openalex.org/{W_PREPRINT}"},
        ],
        "info": {
            "discovered_by": {"openalex": W_PUBLISHED, "openreview": "0Dh0eZ7w9O"}
        },
    }
    # publisher DOI first, then OpenAlex ids (links before discovered_by),
    # then the arXiv id (arXiv DOIs and versions folded into it), then the
    # Semantic Scholar sha; DOIs de-duplicated case-insensitively.
    assert enrich.lookup_keys(paper) == [
        ("doi", DOI),
        ("openalex", W_PREPRINT),
        ("openalex", W_PUBLISHED),
        ("arxiv", ARXIV),
        ("s2", S2),
    ]


def test_lookup_keys_from_bare_ids():
    paper = {
        "links": [
            {"type": "doi.abstract", "link": "10.1016/j.neunet.2024.106793"},
            {"type": "arxiv.pdf", "link": "2307.00134v3"},
            {"type": "arxiv.abstract", "link": "hep-th/9901001"},
            {"type": "semantic_scholar.abstract", "link": S2.upper()},
            {"type": "corpusid", "link": "259316664"},
            {"type": "pubmed.abstract", "link": "39426036"},
        ]
    }
    assert enrich.lookup_keys(paper) == [
        ("doi", "10.1016/j.neunet.2024.106793"),
        ("arxiv", "2307.00134"),
        ("arxiv", "hep-th/9901001"),
        ("s2", S2),
    ]
    assert enrich.lookup_keys({"title": "no links"}) == []


# -- OpenAlex helpers -----------------------------------------------------


def test_rebuild_abstract():
    inverted = {"world": [1, 3], "hello": [0], "big": [2]}
    assert enrich.rebuild_abstract(inverted) == "hello world big world"
    assert enrich.rebuild_abstract(None) is None
    assert enrich.rebuild_abstract({}) is None


def test_summarize_work_flattens_the_topic_and_filters_concepts():
    work = json.loads((FIXTURES / "openalex-W4414813482.json").read_text())
    summary = enrich.summarize_work(work)
    assert summary == {
        "id": W_PREPRINT,
        "domain": "Physical Sciences",
        "field": "Computer Science",
        "subfield": "Computer Networks and Communications",
        "topic": "Network Security and Intrusion Detection",
        "is_oa": True,
        "keywords": ["Misinformation", "Hyperlink", "Credibility"],
        # "Crawling" (score 0.26) is below CONCEPT_MIN_SCORE
        "concepts": ["Misinformation", "Computer science", "Hyperlink", "Credibility"],
    }
    # a work OpenAlex has not classified yet
    bare = enrich.summarize_work({"id": f"https://openalex.org/{W_PUBLISHED}"})
    assert bare["id"] == W_PUBLISHED
    assert bare["topic"] is None and bare["domain"] is None
    assert bare["keywords"] == [] and bare["is_oa"] is None


def test_openalex_urls():
    assert enrich.openalex_urls("doi", DOI, "me@x.org") == [
        f"https://api.openalex.org/works/doi:{DOI}"
        f"?select={enrich.OPENALEX_SELECT.replace(',', '%2C')}&mailto=me%40x.org"
    ]
    doi_route, filter_route = enrich.openalex_urls("arxiv", ARXIV, None)
    assert doi_route.startswith(
        f"https://api.openalex.org/works/doi:10.48550/arxiv.{ARXIV}?"
    )
    assert "mailto" not in doi_route
    assert (
        "filter=locations.landing_page_url%3Ahttps%3A%2F%2Farxiv.org%2Fabs%2F2509.23340"
        in filter_route
    )
    assert enrich.openalex_urls("s2", S2, None) == []


# -- Client: cache, pacing, retries ------------------------------------------


def test_client_caches_answers_and_paces(tmp_path: Path):
    calls: list[tuple[str, str]] = []
    statuses = iter([200, 404, 500, 500, 500, 200, 200])
    slept: list[float] = []
    now = [100.0]

    def fetch(url: str, headers: dict[str, str]) -> tuple[int, str]:
        calls.append((url, headers["User-Agent"]))
        return next(statuses), '{"ok": true}'

    def sleep(seconds: float) -> None:
        slept.append(seconds)
        now[0] += seconds

    client = enrich.Client(
        tmp_path, "me@x.org", fetch=fetch, sleep=sleep, clock=lambda: now[0]
    )
    assert client.get("svc", "http://a") == (200, '{"ok": true}')
    assert client.get("svc", "http://b") == (404, '{"ok": true}')
    # a 500 is retried and not cached
    assert client.get("svc", "http://c")[0] == 500
    assert len(calls) == 5 and all(
        ua == "paperext/paperoni-enrich (mailto:me@x.org)" for _, ua in calls
    )
    assert slept == [enrich.BACKOFF, 2 * enrich.BACKOFF, 3 * enrich.BACKOFF]
    # cached: no new call
    assert client.get("svc", "http://a") == (200, '{"ok": true}')
    assert client.get("svc", "http://b") == (404, '{"ok": true}')
    assert len(calls) == 5
    assert client.get("svc", "http://c") == (200, '{"ok": true}')
    assert len(calls) == 6
    assert client.requests == 6 and client.cache_hits == 2
    assert sorted(p.name for p in (tmp_path / "svc").iterdir()) == sorted(
        enrich.Client._cache_file(client, "svc", u).name
        for u in ("http://a", "http://b", "http://c")
    )
    # refresh bypasses the cache
    client.refresh = True
    client.get("svc", "http://a")
    assert client.requests == 7


def test_client_pacing_and_cooldown(tmp_path: Path):
    slept: list[float] = []
    now = [0.0]
    statuses = iter([200, 200, 429, 429, 429])

    def fetch(url: str, headers: dict[str, str]) -> tuple[int, str]:
        return next(statuses), ""

    def sleep(seconds: float) -> None:
        slept.append(round(seconds, 3))
        now[0] += seconds

    client = enrich.Client(
        tmp_path,
        fetch=fetch,
        pacing={"svc": 2.0},
        sleep=sleep,
        clock=lambda: now[0],
    )
    client.get("svc", "http://a")
    now[0] += 0.5
    client.get("svc", "http://b")  # 1.5 s early: paced
    assert slept == [1.5]
    # three 429s in a row -> the service is skipped for COOLDOWN seconds
    assert client.get("svc", "http://c") == (429, "")
    assert client.get("svc", "http://d") == (429, "")
    assert client.requests == 5
    now[0] += enrich.COOLDOWN + 1
    with pytest.raises(StopIteration):  # tries the network again
        client.get("svc", "http://d")


def test_get_json(client: enrich.Client, recorder: Recorder):
    client.fetch = Recorder(
        {
            "http://json": (200, '{"a": 1}'),
            "http://bad": (200, "nope"),
            "http://list": (200, "[1]"),
            "http://err": (503, ""),
        }
    )
    client.sleep = lambda _: None
    assert client.get_json("svc", "http://json") == {"a": 1}
    assert client.get_json("svc", "http://bad") is None
    assert client.get_json("svc", "http://list") is None
    assert client.get_json("svc", "http://err") is None


# -- abstract fallbacks ------------------------------------------------------


def test_semantic_scholar_abstract(client: enrich.Client, recorder: Recorder):
    assert enrich.semantic_scholar_abstract(client, "doi", DOI) == (
        "Automatically assessing the credibility of online sources presents an "
        "invaluable tool."
    )
    assert enrich.semantic_scholar_abstract(client, "arxiv", "0000.00000") is None
    assert enrich.semantic_scholar_abstract(client, "openalex", W_PREPRINT) is None
    assert recorder.calls == [
        f"https://api.semanticscholar.org/graph/v1/paper/DOI:{DOI}?fields=abstract",
        "https://api.semanticscholar.org/graph/v1/paper/arXiv:0000.00000?fields=abstract",
    ]


def test_arxiv_abstract(client: enrich.Client):
    assert enrich.arxiv_abstract(client, ARXIV) == (
        "Automatically assessing the credibility of online sources presents an "
        "invaluable [...]"
    )
    assert enrich.arxiv_abstract(client, "0000.00000") is None
    client.fetch = Recorder({".": (200, "<not xml")})
    assert enrich.arxiv_abstract(client, "1111.11111") is None


# -- enrich_paper ------------------------------------------------------------


def test_enrich_paper_merges_publisher_and_preprint_works(
    client: enrich.Client, recorder: Recorder
):
    # The published version's work has the abstract but no topic yet; the
    # preprint's work (via the W-id) supplies the topic.
    paper = _paper(
        **{
            "doi": f"https://doi.org/{DOI}",
            "openalex": f"https://openalex.org/{W_PREPRINT}",
        }
    )
    result = enrich.enrich_paper(paper, client)
    assert (
        paper["abstract"]
        == "Automatically assessing the credibility of online sources presents"
    )
    assert paper["abstract_source"] == "openalex"
    assert paper["openalex"]["id"] == W_PREPRINT
    assert paper["openalex"]["topic"] == "Network Security and Intrusion Detection"
    assert result.keys == [f"doi:{DOI}", f"openalex:{W_PREPRINT}"]
    assert (result.openalex_id, result.topic, result.abstract_source, result.venue) == (
        W_PREPRINT,
        "Network Security and Intrusion Detection",
        "openalex",
        "KDD",
    )
    assert len(recorder.calls) == 2

    # A second pass is a no-op: nothing left to look up.
    assert enrich.is_enriched(paper)
    again = enrich.enrich_paper(paper, client)
    assert again == result
    assert len(recorder.calls) == 2


def test_enrich_paper_keeps_the_record_abstract(
    client: enrich.Client, recorder: Recorder
):
    paper = _paper(openalex=W_PREPRINT)
    paper["abstract"] = "The record's own abstract."
    result = enrich.enrich_paper(paper, client)
    assert paper["abstract"] == "The record's own abstract."
    assert paper["abstract_source"] == result.abstract_source == "paperoni"
    assert paper["openalex"]["domain"] == "Physical Sciences"
    assert len(recorder.calls) == 1


def test_enrich_paper_arxiv_routes(client: enrich.Client, recorder: Recorder):
    # The arXiv DOI is unknown to OpenAlex (404); the landing-page filter hits.
    paper = _paper(arxiv=f"https://arxiv.org/abs/{ARXIV}")
    enrich.enrich_paper(paper, client)
    assert paper["openalex"]["id"] == W_PREPRINT
    assert paper["abstract_source"] == "openalex"
    assert [u.split("?")[0] for u in recorder.calls] == [
        f"https://api.openalex.org/works/doi:10.48550/arxiv.{ARXIV}",
        "https://api.openalex.org/works",
    ]


def test_enrich_paper_abstract_fallbacks(client: enrich.Client, recorder: Recorder):
    # Nothing on OpenAlex: Semantic Scholar answers for the DOI.
    paper = _paper(doi="https://doi.org/10.1000/unknown", semantic_scholar=S2)
    client.fetch = Recorder(
        {
            r"semanticscholar\.org/.*/paper/"
            + S2: (200, json.dumps({"abstract": "From S2 by sha."}))
        }
    )
    result = enrich.enrich_paper(paper, client)
    assert paper["abstract"] == "From S2 by sha."
    assert paper["abstract_source"] == result.abstract_source == "semantic_scholar"
    assert "openalex" not in paper and result.topic is None

    # Semantic Scholar has nothing either: the arXiv API is last.
    paper = _paper(arxiv="0000.00000")
    client.fetch = Recorder(
        {
            r"export\.arxiv\.org/api/query\?id_list=0000.00000$": (
                200,
                (FIXTURES / "arxiv-2509.23340.atom").read_text(),
            )
        }
    )
    result = enrich.enrich_paper(paper, client)
    assert paper["abstract"].startswith("Automatically assessing")
    assert paper["abstract_source"] == result.abstract_source == "arxiv"

    # Nothing anywhere: the record is left alone.
    paper = _paper(doi="https://doi.org/10.1000/unknown")
    client.fetch = Recorder()
    result = enrich.enrich_paper(paper, client)
    assert "abstract" not in paper and "abstract_source" not in paper
    assert result.abstract_source is None and result.topic is None
    assert result.venue == "KDD"


def test_enrich_all_survives_a_broken_record(client: enrich.Client, monkeypatch):
    papers = [
        _paper(openalex=W_PREPRINT),
        {"paper_id": "bad", "title": "x", "links": None},
    ]

    def boom(paper: dict[str, Any], client: enrich.Client) -> enrich.Enrichment:
        if paper["paper_id"] == "bad":
            raise RuntimeError("boom")
        return original(paper, client)

    original = enrich.enrich_paper
    monkeypatch.setattr(enrich, "enrich_paper", boom)
    seen: list[str] = []
    results = enrich.enrich_all(papers, client, lambda r: seen.append(r.paper_id))
    assert seen == ["abc", "bad"]
    assert results[0].topic and results[1].topic is None
    assert results[1].venue == "unknown"


# -- CLI ---------------------------------------------------------------------


def test_main_enriches_in_place_and_reports(
    cfg: Config, tmp_path: Path, monkeypatch, caplog
):
    recorder = Recorder()
    monkeypatch.setattr(enrich, "urllib_fetch", recorder)
    monkeypatch.setattr(enrich, "default_mailto", lambda: "me@x.org")
    monkeypatch.setattr(enrich.time, "sleep", lambda _: None)
    papers = [
        _paper(doi=f"https://doi.org/{DOI}", openalex=W_PREPRINT),
        {**_paper(arxiv="0000.00000"), "paper_id": "def", "abstract": "Own abstract."},
        {**_paper(), "paper_id": "ghi"},
    ]
    source = tmp_path / "papers.json"
    source.write_text(json.dumps(papers))
    report = tmp_path / "report.json"

    with caplog.at_level("INFO", logger="paperext"):
        enrich.main(
            [
                str(source),
                "--cache-dir",
                str(tmp_path / "cache"),
                "--report",
                str(report),
            ]
        )

    enriched = json.loads(source.read_text())
    assert [p.get("abstract_source") for p in enriched] == [
        "openalex",
        "paperoni",
        None,
    ]
    assert enriched[0]["openalex"]["field"] == "Computer Science"
    assert "openalex" not in enriched[2]
    records = json.loads(report.read_text())
    assert [r["paper_id"] for r in records] == ["abc", "def", "ghi"]
    assert records[0]["openalex_id"] == W_PREPRINT and records[2]["keys"] == []
    assert "Abstracts: 1/3 before, 2/3 after (openalex:1)" in caplog.text
    assert "OpenAlex topics: 1/3" in caplog.text
    assert (tmp_path / "cache" / "enrich" / "openalex").is_dir()
    assert all("mailto=me%40x.org" in u for u in recorder.calls if "openalex" in u)

    # --output leaves the source alone; the rerun is served from the cache
    calls = len(recorder.calls)
    out = tmp_path / "out.json"
    enrich.main(
        [str(source), "--cache-dir", str(tmp_path / "cache"), "--output", str(out)]
    )
    assert json.loads(out.read_text()) == enriched
    assert len(recorder.calls) == calls


def test_default_mailto(cfg: Config, tmp_path: Path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    monkeypatch.setenv("PAPERONI_CONFIG", str(config_file))
    assert enrich.default_mailto() is None
    config_file.write_text("paperoni:\n  mailto: someone@mila.quebec\n")
    assert enrich.default_mailto() == "someone@mila.quebec"
    config_file.write_text("paperoni:\n  mailto: _@mila.quebec\n")
    assert enrich.default_mailto() == "_@mila.quebec"
    config_file.write_text("paperoni: [\n")
    assert enrich.default_mailto() is None
