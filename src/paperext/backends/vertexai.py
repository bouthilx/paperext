"""Vertex AI backends (Gemini and Claude).

Vertex AI is a *hosting platform*, not a model family: it serves both Google's
Gemini models and Anthropic's Claude models. Both backends live here because
they share one SDK extra -- ``paperext[vertexai]`` installs ``instructor``'s
Vertex support *and* ``anthropic[vertex]`` -- and one auth surface (a GCP
project/region).

The *native* Anthropic API is :mod:`paperext.backends.anthropic` (registry name
``anthropic``); the Vertex-hosted one here keeps the id ``claude`` and shares
its request handling with the native one through ``AnthropicBase``.
"""

from __future__ import annotations

from typing import Any

import anthropic
import instructor
import vertexai
from vertexai.generative_models import GenerativeModel

from paperext.backends import register
from paperext.backends.anthropic import AnthropicBase
from paperext.backends.base import Backend


@register
class GeminiBackend(Backend):
    name = "gemini"
    # Google rate-limit exception types are wired up when the live path is
    # verified (GCP-gated); none retried for now.
    rate_limit_errors: tuple[type[BaseException], ...] = ()

    def make_client(self) -> instructor.AsyncInstructor:
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
            "input_tokens": metadata.prompt_token_count,
            "output_tokens": metadata.candidates_token_count,
            "total_tokens": metadata.total_token_count,
            # Provider-specific: portion of the input served from cache (billed
            # at a lower rate); kept for cost accounting.
            "cached_content_token_count": metadata.cached_content_token_count,
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
class ClaudeVertexBackend(AnthropicBase):
    name = "claude"
    # Anthropic-on-Vertex rate-limit types are wired up when the live path is
    # verified (GCP-gated); none retried for now.
    rate_limit_errors: tuple[type[BaseException], ...] = ()

    def async_client(self) -> Any:
        return anthropic.AsyncAnthropicVertex(
            project_id=self.config.project, region=self.config.location
        )

    def sync_client(self) -> Any:
        return anthropic.AnthropicVertex(
            project_id=self.config.project, region=self.config.location
        )
