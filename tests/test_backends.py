import asyncio
from unittest.mock import MagicMock

import instructor
import openai
import pytest

from paperext.backends import available, get_backend
from paperext.backends.base import Backend
from paperext.backends.openai import OpenAIBackend


def test_registry_exposes_installed_backends():
    # openai + the vertexai extra (Gemini + anthropic[vertex]) are installed in
    # tests; the vertexai extra provides both the gemini and claude backends.
    assert "openai" in available()
    assert "gemini" in available()
    assert "claude" in available()
    assert "anthropic" in available()


def test_get_backend_returns_singleton_instance():
    backend = get_backend("openai")
    assert isinstance(backend, OpenAIBackend)
    assert isinstance(backend, Backend)
    assert backend.name == "openai"


def test_get_backend_unknown_raises():
    with pytest.raises(KeyError):
        get_backend("does-not-exist")


def test_backend_model_reads_config(cfg):
    # tests/config.ini -> [openai] model = gpt-4o
    assert get_backend("openai").model == cfg.openai.model == "gpt-4o"


def test_openai_backend_smoke_check_uses_model_and_returns_reply():
    client = MagicMock()
    client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="ok"))],
        usage={"total_tokens": 4},
    )

    reply, usage = get_backend("openai").smoke_check(model="gpt-5.6-sol", client=client)

    assert reply == "ok"
    assert usage["total_tokens"] == 4
    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-5.6-sol"


def test_openai_backend_rate_limit_errors_declared():
    import openai

    assert openai.RateLimitError in get_backend("openai").rate_limit_errors


def test_openai_normalize_usage_maps_to_canonical_schema():
    completion = MagicMock(
        usage=MagicMock(
            spec=["prompt_tokens", "completion_tokens", "total_tokens"],
            prompt_tokens=10,
            completion_tokens=4,
            total_tokens=14,
        )
    )
    usage = get_backend("openai").normalize_usage(completion)
    assert usage == {"input_tokens": 10, "output_tokens": 4, "total_tokens": 14}


def test_openai_normalize_usage_accepts_a_responses_object():
    """The agent path goes through /v1/responses, whose usage is already canonical."""
    response = MagicMock(
        usage=MagicMock(
            spec=["input_tokens", "output_tokens", "total_tokens"],
            input_tokens=10,
            output_tokens=4,
            total_tokens=14,
        )
    )
    usage = get_backend("openai").normalize_usage(response)
    assert usage == {"input_tokens": 10, "output_tokens": 4, "total_tokens": 14}


def test_openai_make_client_uses_the_responses_api(monkeypatch, cloud_keys):
    """Reasoning models refuse function tools on chat completions."""
    import instructor
    import openai

    captured: dict = {}

    def _from_openai(client, mode=None, **k):
        captured["mode"] = mode
        return MagicMock()

    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **k: MagicMock())
    monkeypatch.setattr(instructor, "from_openai", _from_openai)
    get_backend("openai").make_client()
    assert captured["mode"] is instructor.Mode.RESPONSES_TOOLS_WITH_INBUILT_TOOLS


# --- Gemini backend (Google on Vertex) ---


def test_gemini_backend_registered_and_model(cfg):
    from paperext.backends.vertexai import GeminiBackend

    backend = get_backend("gemini")
    assert isinstance(backend, GeminiBackend)
    assert backend.name == "gemini"
    assert backend.model == cfg.gemini.model == "models/gemini-1.5-pro"


def test_gemini_normalize_usage_maps_to_canonical_schema():
    # Distinct values guard against the prior copy-paste bug that sourced the
    # input/output counts from cached_content_token_count.
    completion = MagicMock(
        usage_metadata=MagicMock(
            cached_content_token_count=1,
            candidates_token_count=2,
            prompt_token_count=3,
            total_token_count=6,
        )
    )
    usage = get_backend("gemini").normalize_usage(completion)
    assert usage == {
        "input_tokens": 3,
        "output_tokens": 2,
        "total_tokens": 6,
        "cached_content_token_count": 1,
    }


# --- Claude backend (Anthropic on Vertex) ---


def test_claude_backend_registered_and_model(cfg):
    from paperext.backends.vertexai import ClaudeVertexBackend

    backend = get_backend("claude")
    assert isinstance(backend, ClaudeVertexBackend)
    assert backend.name == "claude"
    assert backend.model == cfg.claude.model == "claude-opus-4-8"


def test_claude_normalize_usage_shape():
    completion = MagicMock(usage=MagicMock(input_tokens=10, output_tokens=4))
    usage = get_backend("claude").normalize_usage(completion)
    assert usage == {"input_tokens": 10, "output_tokens": 4, "total_tokens": 14}


def test_claude_make_client_injects_max_tokens(monkeypatch):
    import asyncio

    import anthropic
    import instructor

    captured: dict = {}

    async def _cwc(*_a, **kwargs):
        captured.update(kwargs)
        return MagicMock(), MagicMock(usage=MagicMock(input_tokens=1, output_tokens=2))

    def _from_anthropic(client, *a, **k):
        c = MagicMock()
        c.chat.completions.create_with_completion.side_effect = _cwc
        return c

    monkeypatch.setattr(anthropic, "AsyncAnthropicVertex", lambda **k: MagicMock())
    monkeypatch.setattr(instructor, "from_anthropic", _from_anthropic)

    client = get_backend("claude").make_client()
    _, usage = asyncio.run(
        client.chat.completions.create_with_completion(
            response_model=object, messages=[{"role": "user", "content": "x"}]
        )
    )

    # Anthropic requires max_tokens; the backend injects a default.
    assert captured["max_tokens"] == 16384
    assert captured["model"] == "claude-opus-4-8"
    assert usage == {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3}


def test_claude_smoke_check_uses_model_and_max_tokens():
    client = MagicMock()
    client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="ok")],
        usage=MagicMock(input_tokens=1, output_tokens=1),
    )

    reply, _ = get_backend("claude").smoke_check(
        model="claude-haiku-4-5", client=client
    )

    assert reply == "ok"
    _, kwargs = client.messages.create.call_args
    assert kwargs["model"] == "claude-haiku-4-5"
    assert kwargs["max_tokens"] == 16


def test_anthropic_backend_registered_and_model(cfg):
    from paperext.backends.anthropic import AnthropicBackend

    backend = get_backend("anthropic")
    assert isinstance(backend, AnthropicBackend)
    assert backend.name == "anthropic"
    assert backend.model == cfg.anthropic.model == "claude-opus-5"


def test_anthropic_backend_mode_selects_instructor_mode(cfg, monkeypatch, cloud_keys):
    """`[anthropic] mode` picks the instructor mode; Opus 5.5 and the Fable
    models reject the forced tool call instructor sends by default."""
    import anthropic
    import instructor

    captured: dict = {}

    def _from_anthropic(client, *a, mode=None, **k):
        captured["mode"] = mode
        return MagicMock()

    monkeypatch.setattr(anthropic, "AsyncAnthropic", lambda **k: MagicMock())
    monkeypatch.setattr(instructor, "from_anthropic", _from_anthropic)

    backend = get_backend("anthropic")
    assert backend.mode is instructor.Mode.ANTHROPIC_TOOLS  # tests/config.ini
    backend.make_client()
    assert captured["mode"] is instructor.Mode.ANTHROPIC_TOOLS

    cfg.anthropic.mode = "json"
    assert backend.mode is instructor.Mode.ANTHROPIC_JSON
    backend.make_client()
    assert captured["mode"] is instructor.Mode.ANTHROPIC_JSON

    cfg.anthropic.mode = "forced"
    with pytest.raises(ValueError, match=r"\[anthropic\] mode must be one of"):
        backend.mode


def test_anthropic_backend_mode_defaults_without_the_option(cfg, monkeypatch):
    # Configs written before the option existed keep the previous behaviour.
    import instructor

    backend = get_backend("anthropic")
    monkeypatch.delitem(cfg.anthropic._config, "mode")
    assert backend.mode is instructor.Mode.ANTHROPIC_TOOLS


def test_anthropic_backend_rate_limit_errors_declared():
    import anthropic

    assert get_backend("anthropic").rate_limit_errors == (anthropic.RateLimitError,)


def test_anthropic_make_client_uses_the_direct_sdk_and_injects_max_tokens(
    monkeypatch, cloud_keys
):
    """Same request handling as the Vertex path, different client constructor."""
    import asyncio

    import anthropic
    import instructor

    captured: dict = {}
    constructed: dict = {}

    async def _cwc(*_a, **kwargs):
        captured.update(kwargs)
        return MagicMock(), MagicMock(usage=MagicMock(input_tokens=1, output_tokens=2))

    def _from_anthropic(client, *a, **k):
        constructed["client"] = client
        c = MagicMock()
        c.chat.completions.create_with_completion.side_effect = _cwc
        return c

    sentinel = MagicMock(name="AsyncAnthropic")
    monkeypatch.setattr(anthropic, "AsyncAnthropic", lambda **k: sentinel)
    monkeypatch.setattr(instructor, "from_anthropic", _from_anthropic)

    client = get_backend("anthropic").make_client()
    _, usage = asyncio.run(
        client.chat.completions.create_with_completion(
            response_model=object, messages=[{"role": "user", "content": "x"}]
        )
    )

    assert constructed["client"] is sentinel
    assert captured["max_tokens"] == 16384
    assert captured["model"] == "claude-opus-5"
    assert usage == {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3}


def test_anthropic_smoke_check_uses_model_and_max_tokens():
    client = MagicMock()
    client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="ok")],
        usage=MagicMock(input_tokens=1, output_tokens=1),
    )
    reply, _ = get_backend("anthropic").smoke_check(
        model="claude-haiku-4-5", client=client
    )
    assert reply == "ok"
    _, kwargs = client.messages.create.call_args
    assert kwargs["model"] == "claude-haiku-4-5"
    assert kwargs["max_tokens"] == 16


def test_vertex_claude_shares_the_anthropic_request_handling():
    from paperext.backends.anthropic import AnthropicBase

    assert isinstance(get_backend("claude"), AnthropicBase)


def test_openai_parses_a_function_call_that_follows_a_reasoning_item(monkeypatch):
    """gpt-5.x puts a ResponseReasoningItem before the tool call; instructor 1.8's
    plain RESPONSES_TOOLS reads output[0] and dies on it."""
    import asyncio
    import json

    from openai.types.responses import ResponseFunctionToolCall, ResponseReasoningItem
    from pydantic import BaseModel

    class Answer(BaseModel):
        word: str

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    client = get_backend("openai").make_client()

    class FakeResponse:
        output = [
            ResponseReasoningItem(id="rs_1", type="reasoning", summary=[]),
            ResponseFunctionToolCall(
                id="fc_1",
                type="function_call",
                call_id="c1",
                name="Answer",
                arguments=json.dumps({"word": "ok"}),
            ),
        ]
        usage = MagicMock(
            spec=["input_tokens", "output_tokens", "total_tokens"],
            input_tokens=1,
            output_tokens=2,
            total_tokens=3,
        )

    async def fake_create(**kwargs):
        return FakeResponse()

    client.client.responses.create = fake_create
    answer, usage = asyncio.run(
        client.chat.completions.create_with_completion(
            response_model=Answer,
            max_retries=0,
            messages=[{"role": "user", "content": "x"}],
        )
    )
    assert answer.word == "ok"
    assert usage["total_tokens"] == 3


# --- Local backend (OpenAI-compatible server, e.g. vLLM) ---


@pytest.fixture
def local_key(monkeypatch):
    """Provide the bearer token the way deployments do: in the environment."""
    monkeypatch.setenv("LOCAL_API_KEY", "local")


@pytest.fixture
def cloud_keys(monkeypatch):
    """Credentials for the hosted backends, which check before building a client."""
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")


def test_local_backend_registered_and_config(cfg, local_key):
    from paperext.backends.local import LocalBackend

    backend = get_backend("local")
    assert "local" in available()
    assert isinstance(backend, LocalBackend)
    assert backend.name == "local"
    assert backend.model == cfg.local.model == "qwen-test"
    assert backend.base_url == "http://localhost:8000/v1"
    assert backend.api_key == "local"


@pytest.mark.parametrize("value", [None, ""])
def test_local_api_key_missing_raises_clear_error(monkeypatch, value):
    # Like the other API backends, the key lives in the environment, never in
    # the tracked config file. Empty counts as unset (the SDK rejects it too).
    if value is None:
        monkeypatch.delenv("LOCAL_API_KEY", raising=False)
    else:
        monkeypatch.setenv("LOCAL_API_KEY", value)
    with pytest.raises(ValueError, match="LOCAL_API_KEY is not set"):
        get_backend("local").api_key


def test_local_backend_never_retries_rate_limits():
    assert get_backend("local").rate_limit_errors == ()


def test_local_normalize_usage_maps_to_canonical_schema():
    completion = MagicMock(
        usage=MagicMock(prompt_tokens=10, completion_tokens=4, total_tokens=14)
    )
    usage = get_backend("local").normalize_usage(completion)
    assert usage == {"input_tokens": 10, "output_tokens": 4, "total_tokens": 14}


@pytest.mark.parametrize(
    "mode, expected",
    [("tools", "TOOLS"), ("json_schema", "JSON_SCHEMA")],
)
def test_local_make_client_targets_base_url_with_configured_mode(
    cfg, local_key, monkeypatch, mode, expected
):
    import asyncio

    import instructor
    import openai

    cfg.local.mode = mode
    captured: dict = {}

    async def _cwc(*_a, **kwargs):
        captured.update(kwargs)
        return MagicMock(), MagicMock(
            usage=MagicMock(prompt_tokens=1, completion_tokens=2, total_tokens=3)
        )

    def _from_openai(client, *a, **k):
        captured["sdk_client"] = client
        captured["mode"] = k["mode"]
        c = MagicMock()
        c.chat.completions.create_with_completion.side_effect = _cwc
        return c

    def _async_openai(**k):
        captured["sdk_kwargs"] = k
        return "sdk-client"

    monkeypatch.setattr(openai, "AsyncOpenAI", _async_openai)
    monkeypatch.setattr(instructor, "from_openai", _from_openai)

    client = get_backend("local").make_client()
    _, usage = asyncio.run(
        client.chat.completions.create_with_completion(
            response_model=object, messages=[{"role": "user", "content": "x"}]
        )
    )

    assert captured["sdk_kwargs"] == {
        "base_url": "http://localhost:8000/v1",
        "api_key": "local",
    }
    assert captured["sdk_client"] == "sdk-client"
    assert captured["mode"] is getattr(instructor.Mode, expected)
    assert captured["model"] == "qwen-test"
    assert usage == {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3}


def test_local_unknown_mode_raises_clear_error(cfg):
    cfg.local.mode = "grammar"
    with pytest.raises(ValueError, match="json_schema.*tools.*'grammar'"):
        get_backend("local").mode


def test_local_smoke_check_uses_model_and_returns_reply(cfg):
    client = MagicMock()
    client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="ok"))],
        usage={"total_tokens": 4},
    )

    reply, usage = get_backend("local").smoke_check(client=client)

    assert reply == "ok"
    assert usage["total_tokens"] == 4
    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == "qwen-test"


def test_local_smoke_check_default_client_targets_base_url(cfg, local_key, monkeypatch):
    import openai

    captured: dict = {}

    def _openai(**k):
        captured.update(k)
        c = MagicMock()
        c.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="ok"))]
        )
        return c

    monkeypatch.setattr(openai, "OpenAI", _openai)

    reply, _ = get_backend("local").smoke_check()

    assert reply == "ok"
    assert captured == {"base_url": "http://localhost:8000/v1", "api_key": "local"}


# --------------------------------------------------------------------------- #
# Errors name the backend that had them (#80)
# --------------------------------------------------------------------------- #


def test_a_missing_credential_names_the_backend_and_the_variable(monkeypatch):
    """The SDKs raise before naming the provider; a two-client run needs the name."""
    from paperext.backends.base import BackendAuthError

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(BackendAuthError) as caught:
        get_backend("anthropic").make_client(label="judge")
    message = str(caught.value)
    assert "anthropic/" in message and "(judge)" in message
    assert "$ANTHROPIC_API_KEY" in message
    # and the check happens before any request is attempted
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(BackendAuthError, match=r"\$OPENAI_API_KEY"):
        get_backend("openai").smoke_check()


def test_a_provider_error_is_tagged_with_the_backend_and_model(monkeypatch, cloud_keys):
    """add_note, not a wrapper: the retry loops match on the SDK's own types."""
    boom = openai.RateLimitError(
        "no credits", response=MagicMock(status_code=429, headers={}), body=None
    )

    def _from_openai(*_a, **_k):
        client = MagicMock()

        async def _create(*_args, **_kwargs):
            raise boom

        client.chat.completions.create_with_completion = _create
        return client

    monkeypatch.setattr(instructor, "from_openai", _from_openai)
    client = get_backend("openai").make_client(label="agent")

    with pytest.raises(openai.RateLimitError) as caught:  # type unchanged
        asyncio.run(client.chat.completions.create_with_completion(messages=[]))
    note = "\n".join(getattr(caught.value, "__notes__", []))
    assert "openai/" in note and "(agent)" in note and "$OPENAI_API_KEY" in note
