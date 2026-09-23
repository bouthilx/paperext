"""Anthropic backend (direct API, not Vertex).

Registry name ``anthropic``, config section ``[anthropic]``, credentials from
``ANTHROPIC_API_KEY`` (settable under ``[env]`` like the OpenAI key).

``mode`` selects how instructor gets the structured output, as ``[local]``
does: ``tools`` (the default) sends the schema as one forced tool call, while
``json`` sends it in the system prompt and parses JSON back. Newer Claude
models -- Opus 5.5 and the Fable line -- **reject forced tool use**
(``tool_choice`` ``tool``/``any`` returns HTTP 400), and instructor forces it
by default, so those models need ``mode = json``.

Claude is also reachable through Vertex AI (:mod:`paperext.backends.vertexai`,
registry name ``claude``); the two differ only in how the SDK client is built,
so the request wrapping, usage normalization and smoke check live here in
:class:`AnthropicBase` and the Vertex backend subclasses it.
"""

from __future__ import annotations

from typing import Any

import anthropic
import instructor

from paperext.backends import register
from paperext.backends.base import Backend

# Anthropic requires max_tokens on every request; the extract loop does not set
# one, so the backend injects a default. Comfortably above the largest output
# seen in the 2024 corpus (~7.2k tokens); billing is per actual output token, so
# a generous ceiling only guards against truncation.
DEFAULT_MAX_TOKENS = 16384

#: Config ``mode`` value -> instructor mode.
MODES: dict[str, instructor.Mode] = {
    "tools": instructor.Mode.ANTHROPIC_TOOLS,
    "json": instructor.Mode.ANTHROPIC_JSON,
}

#: Default when the config section has no ``mode`` (every existing config).
DEFAULT_MODE = "tools"


class AnthropicBase(Backend):
    """Everything an Anthropic-SDK backend does except constructing the client."""

    name = ""

    def async_client(self) -> Any:
        raise NotImplementedError

    def sync_client(self) -> Any:
        raise NotImplementedError

    # Anthropic requires max_tokens on every request; the extract loop sets none.
    # Claude uses the native "system" role (instructor maps a system message to
    # the top-level system param), so no message folding is needed.
    request_defaults = {"max_tokens": DEFAULT_MAX_TOKENS}

    @property
    def mode(self) -> instructor.Mode:
        """instructor mode selected by ``mode`` in this backend's section."""
        try:  # Config raises KeyError for a missing option, so no getattr default
            raw = self.config.mode or DEFAULT_MODE
        except KeyError:
            raw = DEFAULT_MODE
        try:
            return MODES[raw]
        except KeyError:
            raise ValueError(
                f"[{self.name}] mode must be one of {sorted(MODES)}, got {raw!r}"
            ) from None

    def build_client(self) -> instructor.AsyncInstructor:
        return instructor.from_anthropic(self.async_client(), mode=self.mode)

    def normalize_usage(self, completion: Any) -> dict[str, Any]:
        # Anthropic's usage already matches the canonical schema.
        usage = completion.usage
        return {
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "total_tokens": usage.input_tokens + usage.output_tokens,
        }

    def smoke_check(
        self,
        model: str | None = None,
        message: str = "Reply with the single word: ok.",
        client: Any = None,
    ) -> tuple[str, Any]:
        model = model or self.model
        if client is None:
            self.check_credentials()
            client = self.sync_client()
        response = client.messages.create(
            model=model,
            max_tokens=16,
            messages=[{"role": "user", "content": message}],
        )
        return response.content[0].text, getattr(response, "usage", None)


@register
class AnthropicBackend(AnthropicBase):
    name = "anthropic"
    rate_limit_errors: tuple[type[BaseException], ...] = (anthropic.RateLimitError,)
    api_key_env = "ANTHROPIC_API_KEY"

    def async_client(self) -> Any:
        return anthropic.AsyncAnthropic()  # ANTHROPIC_API_KEY from the environment

    def sync_client(self) -> Any:
        return anthropic.Anthropic()
