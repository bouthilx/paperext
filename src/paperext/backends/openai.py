"""OpenAI backend (direct API)."""

import instructor
import openai

from paperext.backends import register
from paperext.backends.base import Backend


@register
class OpenAIBackend(Backend):
    name = "openai"
    rate_limit_errors = (openai.RateLimitError,)

    def make_client(self):
        model = self.model
        normalize_usage = self.normalize_usage
        client = instructor.from_openai(
            # TODO: update to use the new feature Mode.TOOLS_STRICT
            # https://openai.com/index/introducing-structured-outputs-in-the-api/
            openai.AsyncOpenAI(),
            mode=instructor.Mode.TOOLS_STRICT,
        )
        _create_with_completion = client.chat.completions.create_with_completion

        async def _wrap(*args, **kwargs):
            extractions, completion = await _create_with_completion(
                model=model, *args, **kwargs
            )
            return extractions, normalize_usage(completion)

        client.chat.completions.create_with_completion = _wrap
        return client

    def normalize_usage(self, completion):
        # openai's CompletionUsage is a pydantic model -> serializable as-is.
        return completion.usage

    def smoke_check(
        self, model=None, message="Reply with the single word: ok.", client=None
    ):
        model = model or self.model
        client = client if client is not None else openai.OpenAI()
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
        )
        return completion.choices[0].message.content, getattr(
            completion, "usage", None
        )
