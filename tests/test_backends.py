from unittest.mock import MagicMock

import pytest

from paperext.backends import available, get_backend
from paperext.backends.base import Backend
from paperext.backends.openai import OpenAIBackend


def test_registry_exposes_installed_backends():
    # openai + vertexai extras are installed in the tests env.
    assert "openai" in available()
    assert "vertexai" in available()


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

    reply, usage = get_backend("openai").smoke_check(
        model="gpt-5.6-sol", client=client
    )

    assert reply == "ok"
    assert usage["total_tokens"] == 4
    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-5.6-sol"


def test_openai_backend_rate_limit_errors_declared():
    import openai

    assert openai.RateLimitError in get_backend("openai").rate_limit_errors
