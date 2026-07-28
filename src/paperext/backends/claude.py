"""Claude backend (Anthropic on Vertex AI)."""

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
_DEFAULT_MAX_TOKENS = 16384


@register
class ClaudeBackend(Backend):
    name = "claude"
    # Anthropic-on-Vertex rate-limit types are wired up when the live path is
    # verified (GCP-gated); none retried for now.
    rate_limit_errors: tuple[type[BaseException], ...] = ()

    def make_client(self) -> instructor.client.AsyncInstructor:
        model = self.model
        normalize_usage = self.normalize_usage
        client = instructor.from_anthropic(
            anthropic.AsyncAnthropicVertex(
                project_id=self.config.project,
                region=self.config.location,
            )
        )
        _create_with_completion = client.chat.completions.create_with_completion

        async def _wrap(*args: Any, **kwargs: Any) -> tuple[Any, Any]:
            # Claude uses the native "system" role (instructor maps a system
            # message to the top-level system param) -- no folding needed.
            kwargs.setdefault("max_tokens", _DEFAULT_MAX_TOKENS)
            extractions, completion = await _create_with_completion(
                model=model, *args, **kwargs
            )
            return extractions, normalize_usage(completion)

        # Wrap instructor's method to normalize the (extractions, usage) return.
        setattr(client.chat.completions, "create_with_completion", _wrap)
        return client

    def normalize_usage(self, completion: Any) -> dict[str, Any]:
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
            client = anthropic.AnthropicVertex(
                project_id=self.config.project,
                region=self.config.location,
            )
        response = client.messages.create(
            model=model,
            max_tokens=16,
            messages=[{"role": "user", "content": message}],
        )
        return response.content[0].text, getattr(response, "usage", None)
