"""Vertex AI backend (Gemini).

Kept named ``vertexai`` to match the current config section and ``--platform``
id; A4 (#9) renames this to ``gemini`` and A3 (#8) adds a sibling Claude
backend.
"""

from __future__ import annotations

from typing import Any

import instructor
import vertexai
from vertexai.generative_models import GenerativeModel

from paperext.backends import register
from paperext.backends.base import Backend
from paperext.config import CFG


@register
class VertexAIBackend(Backend):
    name = "vertexai"
    # Google rate-limit exception types are wired up with the Vertex arms in
    # A3 (#8) / A4 (#9); none retried for now.
    rate_limit_errors: tuple[type[BaseException], ...] = ()

    def make_client(self) -> instructor.client.AsyncInstructor:
        normalize_usage = self.normalize_usage
        # CFG.<section> is typed Config | Path by the config proxy; .project is
        # only on the Config branch.
        vertexai.init(project=CFG.vertexai.project)  # type: ignore[union-attr]
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
        # NOTE: preserves the existing usage mapping verbatim, including the
        # candidates/prompt copy-paste bug that A4 (#9) fixes -- A9 is a
        # structural move with no behavior change.
        metadata = completion.usage_metadata
        return {
            "cached_content_token_count": metadata.cached_content_token_count,
            "candidates_token_count": metadata.cached_content_token_count,
            "prompt_token_count": metadata.cached_content_token_count,
            "total_token_count": metadata.total_token_count,
        }

    def smoke_check(
        self,
        model: str | None = None,
        message: str = "Reply with the single word: ok.",
        client: Any = None,
    ) -> tuple[str, Any]:
        model = model or self.model
        vertexai.init(project=CFG.vertexai.project)  # type: ignore[union-attr]
        gen_model = client if client is not None else GenerativeModel(model_name=model)
        response = gen_model.generate_content(message)
        return response.text, getattr(response, "usage_metadata", None)
