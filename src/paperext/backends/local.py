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
* ``LOCAL_API_KEY`` (environment, listed under ``[env]`` like
  ``OPENAI_API_KEY``) -- bearer token for the server / proxy. Required: the
  SDK refuses an empty key. Servers that don't check it accept any value.
* ``mode`` -- how instructor extracts the structured output:
  ``tools`` (default) sends the pydantic schema as a single forced tool call;
  ``json_schema`` sends it as ``response_format`` (structured outputs), the
  fallback for servers whose tool-call parser is unreliable.
"""

from __future__ import annotations

import os
from typing import Any

import instructor
import openai

from paperext.backends import register
from paperext.backends.base import Backend

#: Environment variable holding the server's bearer token.
API_KEY_ENV = "LOCAL_API_KEY"

#: Config ``mode`` value -> instructor mode.
MODES: dict[str, instructor.Mode] = {
    "tools": instructor.Mode.TOOLS,
    "json_schema": instructor.Mode.JSON_SCHEMA,
}


@register
class LocalBackend(Backend):
    name = "local"
    api_key_env = API_KEY_ENV
    #: Local servers apply no quota; an HTTP 429 there means the server is
    #: saturated, which retrying with more concurrency would not help.
    rate_limit_errors: tuple[type[BaseException], ...] = ()

    @property
    def base_url(self) -> str:
        return self.config.base_url

    @property
    def api_key(self) -> str:
        """Bearer token from ``$LOCAL_API_KEY``; empty/unset is an error."""
        key = os.environ.get(API_KEY_ENV, "")
        if not key:
            raise ValueError(
                f"{API_KEY_ENV} is not set; export it (or PAPEREXT_ENV_{API_KEY_ENV})"
                f" -- any non-empty value if the server does not check it"
            )
        return key

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

    def build_client(self) -> instructor.AsyncInstructor:
        return instructor.from_openai(
            openai.AsyncOpenAI(base_url=self.base_url, api_key=self.api_key),
            mode=self.mode,
        )

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
