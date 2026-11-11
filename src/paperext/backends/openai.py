"""OpenAI backend (direct API)."""

from __future__ import annotations

from typing import Any

import instructor
import openai

from paperext.backends import register
from paperext.backends.base import Backend

#: Output ceiling per request, injected because the Responses API otherwise
#: applies the model's own default and a truncation here is **much harder to
#: read than on Anthropic**: that backend inspects `stop_reason` and raises
#: "output truncated at max_tokens=...", while a truncated Responses reply
#: arrives as partial JSON and surfaces as a parse or validation failure with no
#: mention of a ceiling. Schema v5 measured mean 20.5k and max 40.4k output
#: tokens over 25 fulltext papers (#103), so 48k matches the Anthropic default
#: and the same evidence. Override with `max_output_tokens` in the `[openai]`
#: config section, or PAPEREXT_OPENAI_MAX_OUTPUT_TOKENS.
DEFAULT_MAX_OUTPUT_TOKENS = 49152


@register
class OpenAIBackend(Backend):
    name = "openai"
    rate_limit_errors: tuple[type[BaseException], ...] = (openai.RateLimitError,)
    api_key_env = "OPENAI_API_KEY"

    @property
    def max_output_tokens(self) -> int:
        """``max_output_tokens`` from config, or the default."""
        try:  # Config raises KeyError for a missing option
            raw = self.config.max_output_tokens
        except KeyError:
            return DEFAULT_MAX_OUTPUT_TOKENS
        if not str(raw).strip():
            return DEFAULT_MAX_OUTPUT_TOKENS
        try:
            value = int(raw)
        except TypeError, ValueError:
            raise ValueError(
                f"max_output_tokens must be an integer, got {raw!r}"
            ) from None
        if value <= 0:
            raise ValueError(f"max_output_tokens must be positive, got {value}")
        return value

    @property
    def request_defaults(self) -> "dict[str, Any]":
        # The Responses API's parameter is `max_output_tokens`, NOT the
        # `max_tokens` the Anthropic backend injects; sending the wrong name
        # would be rejected rather than ignored.
        return {"max_output_tokens": self.max_output_tokens}

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
