"""OpenAI backend (direct API)."""

from __future__ import annotations

from typing import Any

import instructor
import openai

from paperext.backends import register
from paperext.backends.base import Backend


@register
class OpenAIBackend(Backend):
    name = "openai"
    rate_limit_errors: tuple[type[BaseException], ...] = (openai.RateLimitError,)

    def make_client(self) -> instructor.client.AsyncInstructor:
        model = self.model
        normalize_usage = self.normalize_usage
        client = instructor.from_openai(
            # TODO: update to use the new feature Mode.TOOLS_STRICT
            # https://openai.com/index/introducing-structured-outputs-in-the-api/
            openai.AsyncOpenAI(),
            mode=instructor.Mode.TOOLS_STRICT,
        )
        _create_with_completion = client.chat.completions.create_with_completion

        async def _wrap(*args: Any, **kwargs: Any) -> tuple[Any, Any]:
            extractions, completion = await _create_with_completion(
                model=model, *args, **kwargs
            )
            return extractions, normalize_usage(completion)

        # Wrap instructor's method to normalize the (extractions, usage) return.
        setattr(client.chat.completions, "create_with_completion", _wrap)
        return client

    def normalize_usage(self, completion: Any) -> Any:
        # openai's CompletionUsage is a pydantic model -> serializable as-is.
        return completion.usage

    def smoke_check(
        self,
        model: str | None = None,
        message: str = "Reply with the single word: ok.",
        client: Any = None,
    ) -> tuple[str, Any]:
        model = model or self.model
        client = client if client is not None else openai.OpenAI()
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
        )
        return completion.choices[0].message.content, getattr(
            completion, "usage", None
        )
