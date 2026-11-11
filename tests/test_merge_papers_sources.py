"""Where `merge_papers` looks for papers and extractions (#111 Part A).

Split from test_merge_papers.py, which covers the merge logic. These three are
all resolution, and resolution is where this tool was unusable on the 2023-26
corpus: every one of the 110 validated papers is keyed by paperoni id under
`cache/fulltext/`, and none has an arXiv `.txt`.
"""

from __future__ import annotations

import pytest

from paperext import CFG
from paperext.merge_papers import (
    DEFAULT_BUCKETS,
    _buckets,
    _paper_pdf,
    _paper_text,
)


def test_paper_text_reads_either_cache_layout(tmp_path, monkeypatch):
    monkeypatch.setitem(CFG.dir._config, "cache", tmp_path)

    (tmp_path / "arxiv").mkdir()
    (tmp_path / "arxiv" / "2304.14082.txt").write_text("ARXIV\nLAYOUT")
    assert _paper_text("2304.14082") == "arxiv layout"

    # The 2023-26 layout: keyed by paperoni id, text inside a per-paper dir.
    pid = "69a5fde548887d403d0a5e91"
    (tmp_path / "fulltext" / pid).mkdir(parents=True)
    (tmp_path / "fulltext" / pid / "fulltext.txt").write_text("FULLTEXT\nLAYOUT")
    assert _paper_text(pid) == "fulltext layout"

    # The per-paper dir also carries a copy named after the id.
    other = "69a5fe1b48887d403d0a64cb"
    (tmp_path / "fulltext" / other).mkdir(parents=True)
    (tmp_path / "fulltext" / other / f"{other}.txt").write_text("BY ID")
    assert _paper_text(other) == "by id"


def test_paper_text_names_every_place_it_looked(tmp_path, monkeypatch):
    """A miss used to be an unhandled FileNotFoundError on one hardcoded path.

    Saying where it looked is the difference between "this corpus is not
    annotatable" and "the cache is pointed somewhere else".
    """
    monkeypatch.setitem(CFG.dir._config, "cache", tmp_path)
    with pytest.raises(FileNotFoundError) as excinfo:
        _paper_text("nope")
    message = str(excinfo.value)
    assert "arxiv/nope.txt" in message
    assert "fulltext/nope/fulltext.txt" in message


def test_paper_pdf_prefers_a_real_file_and_falls_back_to_arxiv(tmp_path, monkeypatch):
    """The fallback is deliberate: the caller downloads from arXiv on a miss."""
    monkeypatch.setitem(CFG.dir._config, "cache", tmp_path)
    pid = "69a5fde548887d403d0a5e91"
    (tmp_path / "fulltext" / pid).mkdir(parents=True)
    (tmp_path / "fulltext" / pid / "fulltext.pdf").write_bytes(b"%PDF-")
    assert _paper_pdf(pid).name == "fulltext.pdf"

    missing = _paper_pdf("absent")
    assert missing.parts[-2:] == ("arxiv", "absent.pdf")
    assert not missing.is_file()


def test_buckets_takes_several_arms_and_rejects_a_bare_provider():
    resolved = _buckets(["anthropic/claude-opus-5", "openai/gpt-5.6-sol"])
    assert [p.parts[-2:] for p in resolved] == [
        ("anthropic", "claude-opus-5"),
        ("openai", "gpt-5.6-sol"),
    ]
    assert len(_buckets(list(DEFAULT_BUCKETS))) == 1

    with pytest.raises(ValueError, match="provider/model"):
        _buckets(["anthropic"])
