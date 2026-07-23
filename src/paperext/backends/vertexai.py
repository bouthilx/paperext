"""Vertex AI backend (Gemini).

Kept named ``vertexai`` to match the current config section and ``--platform``
id; A4 (#9) renames this to ``gemini`` and A3 (#8) adds a sibling Claude
backend.
"""

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
    rate_limit_errors = ()

    def make_client(self):
        normalize_usage = self.normalize_usage
        vertexai.init(project=CFG.vertexai.project)
        client = instructor.from_vertexai(GenerativeModel(model_name=self.model))
        _create_with_completion = client.chat.completions.create_with_completion

        def _wrap(*args, **kwargs):
            # Gemini does not support the "system" role: fold system content
            # into the following user turn.
            system_messages = []
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
            extractions, completion = _create_with_completion(*args, **kwargs)
            return extractions, normalize_usage(completion)

        client.chat.completions.create_with_completion = _wrap
        return client

    def normalize_usage(self, completion):
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
        self, model=None, message="Reply with the single word: ok.", client=None
    ):
        model = model or self.model
        vertexai.init(project=CFG.vertexai.project)
        gen_model = client if client is not None else GenerativeModel(model_name=model)
        response = gen_model.generate_content(message)
        return response.text, getattr(response, "usage_metadata", None)
