from unittest.mock import MagicMock

import paperext.smoke_openai as smoke_openai
from paperext.config import Config


def _fake_completion(reply="ok"):
    return MagicMock(
        choices=[MagicMock(message=MagicMock(content=reply))],
        usage={"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4},
    )


def test_run_check_calls_configured_model_and_returns_reply():
    client = MagicMock()
    client.chat.completions.create.return_value = _fake_completion("ok")

    reply, usage = smoke_openai.run_check("gpt-5.6-sol", client=client)

    assert reply == "ok"
    assert usage["total_tokens"] == 4
    client.chat.completions.create.assert_called_once()
    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-5.6-sol"
    assert kwargs["messages"][0]["role"] == "user"


def test_main_defaults_to_cfg_model_and_returns_zero(cfg: Config, monkeypatch, capsys):
    client = MagicMock()
    client.chat.completions.create.return_value = _fake_completion("ok")
    monkeypatch.setattr(smoke_openai, "_default_client", lambda: client)

    rc = smoke_openai.main([])

    assert rc == 0
    # Model resolved from the active config (tests/config.ini -> gpt-4o).
    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == cfg.openai.model
    assert "OK:" in capsys.readouterr().out


def test_main_model_override(monkeypatch):
    client = MagicMock()
    client.chat.completions.create.return_value = _fake_completion("ok")
    monkeypatch.setattr(smoke_openai, "_default_client", lambda: client)

    assert smoke_openai.main(["--model", "gpt-5.6-terra"]) == 0
    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-5.6-terra"


def test_main_returns_one_on_failure(monkeypatch, capsys):
    def _boom():
        raise RuntimeError("no api key")

    monkeypatch.setattr(smoke_openai, "_default_client", _boom)

    rc = smoke_openai.main(["--model", "gpt-5.6-sol"])

    assert rc == 1
    assert "FAIL:" in capsys.readouterr().err
