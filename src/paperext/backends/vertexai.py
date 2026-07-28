"""Vertex AI backends (Gemini and Claude).

Vertex AI is a *hosting platform*, not a model family: it serves both Google's
Gemini models and Anthropic's Claude models. Both backends live here because
they share one SDK extra -- ``paperext[vertexai]`` installs ``instructor``'s
Vertex support *and* ``anthropic[vertex]`` -- and one auth surface (a GCP
project/region).

The *native* Anthropic API (Claude not via Vertex) would live in a separate
``claude``/``anthropic`` module with its own extra; hence the Vertex-hosted
backend here is ``ClaudeVertexBackend``, keeping the selectable id ``claude``
while it is the only Claude path.
"""

from __future__ import annotations

from typing import Any

import anthropic
import instructor
import vertexai
from vertexai.generative_models import GenerativeModel

from paperext.backends import register
from paperext.backends.base import Backend

# Anthropic requires max_tokens on every request; the extract loop does not set
# one, so the backend injects a default. Comfortably above the largest output
# seen in the 2024 corpus (~7.2k tokens); billing is per actual output token, so
# a generous ceiling only guards against truncation.
_DEFAULT_MAX_TOKENS = 16384


@register
class GeminiBackend(Backend):
    name = "gemini"
    # Google rate-limit exception types are wired up when the live path is
    # verified (GCP-gated); none retried for now.
    rate_limit_errors: tuple[type[BaseException], ...] = ()

    def make_client(self) -> instructor.client.AsyncInstructor:
        normalize_usage = self.normalize_usage
        vertexai.init(project=self.config.project)
        # use_async=True -> AsyncInstructor, so all backends share one client
        # type and the pipeline can uniformly await create_with_completion.
        client = instructor.from_vertexai(
            GenerativeModel(model_name=self.model), use_async=True
        )
        _create_with_completion = client.chat.completions.create_with_completion

        async def _wrap(*args: Any, **kwargs: Any) -> tuple[Any, Any]:
            # Gemini does not support the "system" role: fold system content
            # into the following user turn.
            system_messages: list[str] = []
            for message in kwargs["messages"][:]:
                if message["role"] == "system":
                    system_messages.append(message["content"])
                    kwargs["messages"].remove(message)
                    continue
                if system_messages:
                    message["content"] = "\n".join(
                        (*system_messages, message["content"])
                    )
                    system_messages = []
            extractions, completion = await _create_with_completion(*args, **kwargs)
            return extractions, normalize_usage(completion)

        # Wrap instructor's method to normalize the (extractions, usage) return.
        setattr(client.chat.completions, "create_with_completion", _wrap)
        return client

    def normalize_usage(self, completion: Any) -> dict[str, Any]:
        metadata = completion.usage_metadata
        return {
            "cached_content_token_count": metadata.cached_content_token_count,
            "candidates_token_count": metadata.candidates_token_count,
            "prompt_token_count": metadata.prompt_token_count,
            "total_token_count": metadata.total_token_count,
        }

    def smoke_check(
        self,
        model: str | None = None,
        message: str = "Reply with the single word: ok.",
        client: Any = None,
    ) -> tuple[str, Any]:
        model = model or self.model
        vertexai.init(project=self.config.project)
        gen_model = client if client is not None else GenerativeModel(model_name=model)
        response = gen_model.generate_content(message)
        return response.text, getattr(response, "usage_metadata", None)


@register
class ClaudeVertexBackend(Backend):
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
