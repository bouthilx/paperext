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
    api_key_env = "OPENAI_API_KEY"

    def build_client(self) -> instructor.AsyncInstructor:
        # The Responses API, not chat completions: reasoning models (gpt-5.x)
        # refuse function tools on /v1/chat/completions unless reasoning is
        # switched off, and switching it off is not an option for a judgment
        # task. instructor maps the same create_with_completion(messages=...)
        # call onto client.responses.create(input=messages), so callers do not
        # change. The _WITH_INBUILT_TOOLS variant sends the identical request
        # when no other tools are given, but *scans* the output for the function
        # call instead of assuming it is output[0] -- a reasoning model emits a
        # ResponseReasoningItem first, and plain RESPONSES_TOOLS (instructor
        # 1.8) trips over it.
        return instructor.from_openai(
            openai.AsyncOpenAI(),
            mode=instructor.Mode.RESPONSES_TOOLS_WITH_INBUILT_TOOLS,
        )

    def normalize_usage(self, completion: Any) -> dict[str, Any]:
        usage = completion.usage
        # Responses objects already use the canonical names; chat completions
        # (the smoke check) still report prompt_/completion_tokens.
        if hasattr(usage, "input_tokens"):
            return {
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "total_tokens": usage.total_tokens,
            }
        return {
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
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
            client = openai.OpenAI()
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
        )
        return completion.choices[0].message.content, getattr(completion, "usage", None)
