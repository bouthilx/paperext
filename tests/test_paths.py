from pathlib import Path

import pytest

from paperext.config import CFG
from paperext.paths import bucket, model_slug, platform_bucket, selected_model


@pytest.mark.parametrize(
    "model,expected",
    [
        ("gpt-4o", "gpt-4o"),
        ("models/gemini-1.5-pro", "models-gemini-1.5-pro"),
        ("claude-3-5-sonnet@20240620", "claude-3-5-sonnet-20240620"),
        ("gpt 4o", "gpt-4o"),
        ("a//b@@c", "a-b-c"),
        ("  gpt-4o  ", "gpt-4o"),
        ("gpt_4o.1", "gpt_4o.1"),
        ("@@@gpt@@@", "gpt"),
    ],
)
def test_model_slug_normalizes_to_safe_segment(model, expected):
    slug = model_slug(model)
    assert slug == expected
    # A slug is always a single, safe path segment.
    assert "/" not in slug
    assert Path(slug).name == slug


@pytest.mark.parametrize("model", ["", "   ", "@@@", "///", None])
def test_model_slug_rejects_empty(model):
    with pytest.raises(ValueError):
        model_slug(model)


def test_selected_model_reads_selected_platform_section():
    # tests/config.ini selects openai with model gpt-4o
    assert CFG.platform.select == "openai"
    assert selected_model() == CFG.openai.model == "gpt-4o"


def test_bucket_takes_explicit_provider_and_model():
    base = Path("/tmp/queries")
    # Independent of the current CFG selection -- the comparison use case.
    assert bucket(base, "claude", "claude-3-5-sonnet@20240620") == (
        base / "claude" / "claude-3-5-sonnet-20240620"
    )
    assert bucket(base, "openai", "legacy-2024") == base / "openai" / "legacy-2024"


def test_bucket_does_not_read_global_selection():
    base = Path("/tmp/queries")
    assert CFG.platform.select == "openai"
    # A different provider/model resolves regardless of the active selection.
    assert bucket(base, "vertexai", "models/gemini-1.5-pro") == (
        base / "vertexai" / "models-gemini-1.5-pro"
    )


def test_platform_bucket_nests_provider_and_model():
    base = Path("/tmp/queries")
    assert platform_bucket(base) == base / "openai" / "gpt-4o"


def test_platform_bucket_delegates_to_bucket():
    base = Path("/tmp/queries")
    assert platform_bucket(base) == bucket(
        base, CFG.platform.select, selected_model()
    )


def test_platform_bucket_follows_runtime_platform_switch():
    base = Path("/tmp/queries")
    CFG.platform.select = "vertexai"
    try:
        assert platform_bucket(base) == base / "vertexai" / model_slug(
            CFG.vertexai.model
        )
    finally:
        CFG.platform.select = "openai"


def test_different_models_get_distinct_buckets():
    base = Path("/tmp/queries")
    a = platform_bucket(base)
    CFG.openai.model = "some-other-model"
    try:
        b = platform_bucket(base)
    finally:
        CFG.openai.model = "gpt-4o"
    assert a != b
