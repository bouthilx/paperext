from unittest.mock import MagicMock

import pytest

from paperext.backends import available, get_backend
from paperext.backends.base import Backend
from paperext.backends.openai import OpenAIBackend


def test_registry_exposes_installed_backends():
    # openai + vertexai (incl. anthropic[vertex]) extras are installed in tests.
    assert "openai" in available()
    assert "vertexai" in available()
    assert "claude" in available()


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


# --- Claude backend (Anthropic on Vertex) ---


def test_claude_backend_registered_and_model(cfg):
    from paperext.backends.claude import ClaudeBackend

    backend = get_backend("claude")
    assert isinstance(backend, ClaudeBackend)
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
