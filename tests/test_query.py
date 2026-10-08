import asyncio
import json
from unittest.mock import MagicMock

import openai
import pytest

import paperext.backends.vertexai
import paperext.query
from paperext.query import (
    extraction_path,
    get_extraction_response,
    get_first_message,
    get_paper_extractions,
    get_system_message,
    main,
    partition_pending,
)
from paperext.structured_output import STRUCT_MODULES
from paperext.structured_output.mdl.model import PaperExtractions


@pytest.fixture(autouse=True)
def set_cfg(cfg, monkeypatch):
    monkeypatch.setattr(paperext.query, "CFG", cfg)
    # backends check their credential before building a client (#80)
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")


@pytest.fixture(scope="function", autouse=True)
def clean_up(cfg):
    yield

    for query_file in cfg.dir.queries.glob(f"**/new_*.json"):
        query_file.unlink(missing_ok=True)


@pytest.mark.parametrize("model_struct", ["ai4hcat", "mdl"])
def test_model_struct_from_cfg(cfg, model_struct):
    cfg.platform.struct = model_struct

    assert get_first_message() is STRUCT_MODULES[model_struct].FIRST_MESSAGE
    assert get_system_message() is STRUCT_MODULES[model_struct].SYSTEM_MESSAGE
    assert get_extraction_response() is STRUCT_MODULES[model_struct].ExtractionResponse
    assert get_paper_extractions() is STRUCT_MODULES[model_struct].PaperExtractions


@pytest.mark.parametrize("platform", ["openai", "gemini"])
def test_query(
    platform, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    """Test that the query function:
    * works correctly for different platforms
    * does not retry a request if the query result file exists
    * creates a query result file on success
    """
    # The gemini backend builds its client via instructor.from_vertexai (Vertex
    # is the platform, Gemini the model), so map the platform id to its factory.
    instructor_factory = {"openai": "from_openai", "gemini": "from_vertexai"}[platform]

    if platform == "openai":
        monkeypatch.setattr(openai, "AsyncOpenAI", MagicMock)

    elif platform == "gemini":
        monkeypatch.setattr(paperext.backends.vertexai, "GenerativeModel", MagicMock)

    monkeypatch.setattr(paperext.query.instructor, instructor_factory, MagicMock())

    monkeypatch.setattr(openai, "AsyncOpenAI", MagicMock)
    monkeypatch.setattr(paperext.query.instructor, "from_openai", MagicMock())

    main(["--platform", platform, "--papers", "2401.14487"])

    # Both backends now build AsyncInstructor clients, so the mocked
    # create_with_completion is awaitable for every platform.
    async def create_with_completion(*_a, **_kwa):
        magicmock = MagicMock(spec=PaperExtractions)
        magicmock.models = []
        magicmock.datasets = []
        magicmock.libraries = []
        return magicmock, MagicMock()

    def AsyncOpenAI(*_a, **_kwa):
        magicmock = MagicMock()
        magicmock.chat.completions.create_with_completion.side_effect = (
            create_with_completion
        )
        return magicmock

    monkeypatch.setattr(paperext.query.instructor, instructor_factory, AsyncOpenAI)

    main(["--platform", platform, "--papers", "new_1234.12345"])
    assert (
        len(
            list(
                paperext.query.CFG.dir.queries.glob(
                    f"{platform}/*/new_1234.12345_*.json"
                )
            )
        )
        == 1
    )

    for record in filter(lambda r: r.levelname == "ERROR", caplog.records):
        assert "Failed to extract paper information" not in record.message


def test_query_error_logged(monkeypatch: pytest.MonkeyPatch):
    """Test that the query function:
    * logs an error when a query fails and continues with the next paper
    """

    async def create_with_completion(*_a, **_kwa):
        raise Exception("Expected exception")

    def AsyncOpenAI(*_a, **_kwa):
        magicmock = MagicMock()
        magicmock.chat.completions.create_with_completion.side_effect = (
            create_with_completion
        )
        return magicmock

    monkeypatch.setattr(openai, "AsyncOpenAI", MagicMock)
    monkeypatch.setattr(paperext.query.instructor, f"from_openai", AsyncOpenAI)

    papers = ["new_1234.12345", "new_1234.23456"]
    logging_error_mock = MagicMock()
    with monkeypatch.context() as m:
        m.setattr(paperext.query.logging, "basicConfig", MagicMock)
        m.setattr(paperext.query.logging, "error", logging_error_mock)
        main(["--platform", "openai", "--papers", *papers])

    error_msg_cnt = 0
    for call_arg in map(lambda c: str(c[0][0]), logging_error_mock.call_args_list):
        if (
            sum(
                text in call_arg
                for text in [
                    "Failed to extract paper information",
                    *papers,
                    "Expected exception",
                ]
            )
            == 3
        ):
            error_msg_cnt += 1

    assert error_msg_cnt == len(papers)


def test_an_input_resolving_to_no_papers_fails_loudly(tmp_path, capsys):
    """An empty paper list used to run to completion having queried nothing.

    `all([])` is True, so both of `main`'s guards passed vacuously and
    `asyncio.run` looped over nothing -- a silent no-op on a pipeline whose next
    step is thousands of paid calls. The common cause is a cache pointed
    somewhere else, so the error has to name the directory it looked in.
    """
    paperoni = tmp_path / "sample.json"
    paperoni.write_text(
        json.dumps(
            [
                {
                    "paper_id": "deadbeef",
                    "title": "A paper whose converted text is not cached",
                    "links": [],
                    "releases": [],
                    "authors": [],
                }
            ]
        )
    )

    with pytest.raises(SystemExit):
        main(["--platform", "openai", "--paperoni", str(paperoni)])

    err = capsys.readouterr().err
    assert "no papers to query" in err
    assert "PAPEREXT_DIR_CACHE" in err


def test_a_named_paper_with_no_file_fails_loudly(capsys):
    """The non-empty case: say which files are missing, not just that some are."""
    with pytest.raises(SystemExit):
        main(["--platform", "openai", "--papers", "definitely-not-a-paper"])

    err = capsys.readouterr().err
    assert "no file on disk" in err
    assert "definitely-not-a-paper" in err


def _valid_extractions():
    """A minimal extraction that round-trips, which `model_construct` does not."""

    def expl(value):
        return {"quote": "q", "justification": "j", "value": value}

    return PaperExtractions.model_validate(
        {
            "title": expl("t"),
            "description": "d",
            "type": expl("empirical"),
            "research_fields": [{"name": expl("x"), "aliases": [], "role": "unknown"}],
            "models": [],
            "data_sources": [],
            "libraries": [],
            "algorithms": [],
            "runs": [],
        }
    )


def test_partition_pending_separates_what_still_needs_a_call(tmp_path):
    """The resume check, which is what makes the ETA honest.

    A bar that counted already-extracted papers as progress would quote minutes
    for an eight-hour job, because a reused paper returns instantly.
    """
    papers = [tmp_path / f"{name}.txt" for name in ("done", "missing", "corrupt")]
    for paper in papers:
        paper.write_text("body")
    destination = tmp_path / "out"
    destination.mkdir()

    response = get_extraction_response()(
        paper="done.txt",
        words=1,
        extractions=_valid_extractions(),
        usage=None,
    )
    extraction_path(papers[0], destination).write_text(response.model_dump_json())
    extraction_path(papers[2], destination).write_text("{not json")

    pending, reused = partition_pending(papers, destination)

    assert [p.name for p in reused] == ["done.txt"]
    assert [p.name for p in pending] == ["missing.txt", "corrupt.txt"]


def test_a_fully_extracted_input_makes_no_call_and_says_so(
    tmp_path, monkeypatch, capsys
):
    """Re-running a finished command must not re-query, and must not look idle."""
    paper = tmp_path / "done.txt"
    paper.write_text("body")
    destination = tmp_path / "out"
    destination.mkdir()
    response = get_extraction_response()(
        paper="done.txt",
        words=1,
        extractions=_valid_extractions(),
        usage=None,
    )
    extraction_path(paper, destination).write_text(response.model_dump_json())

    monkeypatch.setattr(paperext.query, "platform_bucket", lambda _base: destination)
    made_client = MagicMock()
    monkeypatch.setattr(paperext.query, "get_backend", made_client)

    with monkeypatch.context() as m:
        m.setattr(paperext.query.logging, "basicConfig", MagicMock)
        main(["--platform", "openai", "--papers", str(paper)])

    err = capsys.readouterr().err
    assert "1 already extracted, 0 to query" in err
    assert "nothing to do" in err
    # The decisive part: no backend was ever constructed, so nothing was paid for.
    made_client.assert_not_called()


def test_ignore_exceptions_reports_which_papers_failed(monkeypatch, tmp_path):
    """The bar owns the console, so failures come back as a value."""
    calls = []

    async def batch(_client, papers, **_kwargs):
        calls.append(papers[0].name)
        if papers[0].name == "bad.txt":
            raise RuntimeError("boom")

    monkeypatch.setattr(paperext.query, "batch_extract_models_names", batch)
    papers = [tmp_path / "good.txt", tmp_path / "bad.txt"]

    failures = asyncio.run(paperext.query.ignore_exceptions(MagicMock(), papers))

    assert calls == ["good.txt", "bad.txt"]
    assert failures == ["bad.txt"]
