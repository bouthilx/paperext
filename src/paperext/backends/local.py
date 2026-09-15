"""Local backend: any OpenAI-compatible chat-completions server.

Targets self-hosted models (vLLM, SGLang, llama.cpp, TGI, ...) exposed behind
the OpenAI ``/v1/chat/completions`` wire format. It deliberately does *not*
reuse :class:`paperext.backends.openai.OpenAIBackend`: that backend is pinned
to OpenAI's own endpoint/modes, while local servers only speak chat
completions and differ in how reliably they implement tool calling -- hence
the ``mode`` knob below.

Config section ``[local]``:

* ``base_url`` -- server root including ``/v1``, e.g. ``http://host:8000/v1``.
* ``model`` -- model id as served (``vllm serve <model> --served-model-name``).
* ``api_key`` -- any non-empty string; the SDK refuses an empty key, and most
  local servers ignore it (vLLM checks it only when started with ``--api-key``).
* ``mode`` -- how instructor extracts the structured output:
  ``tools`` (default) sends the pydantic schema as a single forced tool call;
  ``json_schema`` sends it as ``response_format`` (structured outputs), the
  fallback for servers whose tool-call parser is unreliable.
"""

from __future__ import annotations

from typing import Any

import instructor
import openai

from paperext.backends import register
from paperext.backends.base import Backend

#: Config ``mode`` value -> instructor mode.
MODES: dict[str, instructor.Mode] = {
    "tools": instructor.Mode.TOOLS,
    "json_schema": instructor.Mode.JSON_SCHEMA,
}


@register
class LocalBackend(Backend):
    name = "local"
    #: Local servers apply no quota; an HTTP 429 there means the server is
    #: saturated, which retrying with more concurrency would not help.
    rate_limit_errors: tuple[type[BaseException], ...] = ()

    @property
    def base_url(self) -> str:
        return self.config.base_url

    @property
    def api_key(self) -> str:
        return self.config.api_key

    @property
    def mode(self) -> instructor.Mode:
        """instructor mode selected by ``[local] mode``."""
        raw = self.config.mode
        try:
            return MODES[raw]
        except KeyError:
            raise ValueError(
                f"[local] mode must be one of {sorted(MODES)}, got {raw!r}"
            ) from None

    def make_client(self) -> instructor.AsyncInstructor:
        model = self.model
        normalize_usage = self.normalize_usage
        client = instructor.from_openai(
            openai.AsyncOpenAI(base_url=self.base_url, api_key=self.api_key),
            mode=self.mode,
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

    def normalize_usage(self, completion: Any) -> dict[str, Any]:
        """Map chat-completions usage to the canonical keys.

        Counts come from the served model's own tokenizer, so they are not
        comparable with cloud backends' counts (and carry no price); for this
        arm the cost metric is throughput, not tokens.
        """
        usage = completion.usage
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
        client = (
            client
            if client is not None
            else openai.OpenAI(base_url=self.base_url, api_key=self.api_key)
        )
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
        )
        return completion.choices[0].message.content, getattr(completion, "usage", None)
