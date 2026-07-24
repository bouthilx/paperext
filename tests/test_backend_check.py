from unittest.mock import MagicMock

import openai

import paperext.backend_check as backend_check


def _fake_completion(reply="ok"):
    return MagicMock(
        choices=[MagicMock(message=MagicMock(content=reply))],
        usage={"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4},
    )


def _mock_openai(monkeypatch, completion=None, raises=None):
    client = MagicMock()
    if raises is not None:
        client.chat.completions.create.side_effect = raises
    else:
        client.chat.completions.create.return_value = completion or _fake_completion()
    monkeypatch.setattr(openai, "OpenAI", lambda *a, **k: client)
    return client


def test_main_defaults_to_cfg_platform_and_model(cfg, monkeypatch, capsys):
    client = _mock_openai(monkeypatch)

    rc = backend_check.main([])  # cfg selects openai / gpt-4o

    assert rc == 0
    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == cfg.openai.model
    assert "OK:" in capsys.readouterr().out


def test_main_model_and_platform_override(monkeypatch):
    client = _mock_openai(monkeypatch)

    assert backend_check.main(["--platform", "openai", "--model", "gpt-5.6-terra"]) == 0
    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-5.6-terra"


def test_main_returns_one_on_failure(monkeypatch, capsys):
    _mock_openai(monkeypatch, raises=RuntimeError("no api key"))

    rc = backend_check.main(["--platform", "openai"])

    assert rc == 1
    assert "FAIL:" in capsys.readouterr().err
