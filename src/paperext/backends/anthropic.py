"""Anthropic backend (direct API, not Vertex).

Registry name ``anthropic``, config section ``[anthropic]``, credentials from
``ANTHROPIC_API_KEY`` (settable under ``[env]`` like the OpenAI key).

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


class AnthropicBase(Backend):
    """Everything an Anthropic-SDK backend does except constructing the client."""

    name = ""

    def async_client(self) -> Any:
        raise NotImplementedError

    def sync_client(self) -> Any:
        raise NotImplementedError

    def make_client(self) -> instructor.AsyncInstructor:
        model = self.model
        normalize_usage = self.normalize_usage
        client = instructor.from_anthropic(self.async_client())
        _create_with_completion = client.chat.completions.create_with_completion

        async def _wrap(*args: Any, **kwargs: Any) -> tuple[Any, Any]:
            # Claude uses the native "system" role (instructor maps a system
            # message to the top-level system param) -- no folding needed.
            kwargs.setdefault("max_tokens", DEFAULT_MAX_TOKENS)
            extractions, completion = await _create_with_completion(
                model=model, *args, **kwargs
            )
            return extractions, normalize_usage(completion)

        # Wrap instructor's method to normalize the (extractions, usage) return.
        setattr(client.chat.completions, "create_with_completion", _wrap)
        return client

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
        client = client if client is not None else self.sync_client()
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

    def async_client(self) -> Any:
        return anthropic.AsyncAnthropic()  # ANTHROPIC_API_KEY from the environment

    def sync_client(self) -> Any:
        return anthropic.Anthropic()
