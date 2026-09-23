"""Anthropic backend (direct API, not Vertex).

Registry name ``anthropic``, config section ``[anthropic]``, credentials from
``ANTHROPIC_API_KEY`` (settable under ``[env]`` like the OpenAI key).

``mode`` selects how instructor gets the structured output, as ``[local]``
does: ``tools`` (the default) sends the schema as one forced tool call, while
``json`` sends it in the system prompt and parses JSON back. Newer Claude
models -- Opus 5.5 and the Fable line -- **reject forced tool use**
(``tool_choice`` ``tool``/``any`` returns HTTP 400), and instructor forces it
by default, so those models need ``mode = json``.

Claude is also reachable through Vertex AI (:mod:`paperext.backends.vertexai`,
registry name ``claude``); the two differ only in how the SDK client is built,
so the request wrapping, usage normalization and smoke check live here in
:class:`AnthropicBase` and the Vertex backend subclasses it.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import anthropic
import instructor

from paperext.backends import register
from paperext.backends.base import Backend

# Anthropic requires max_tokens on every request; the extract loop does not set
# one, so the backend injects a default. The 2024 corpus's largest extraction was
# ~7.2k tokens, but thinking tokens count toward this ceiling on the models that
# think by default (Opus 5 and later), and 16k truncated the longest papers --
# `IncompleteOutputException` on 8 of 40 papers in the tier comparison, every one
# of them a fulltext call. Billing is per actual output token, so a generous
# ceiling only guards against truncation.
DEFAULT_MAX_TOKENS = 32768

# The SDK refuses a non-streaming request whose `max_tokens` implies more than
# its 10-minute default timeout -- `_calculate_nonstreaming_timeout` estimates
# 1h * max_tokens / 128k, so anything above ~21.3k raises -- *unless* the client
# carries an explicit timeout. The extraction path does not stream, so the
# clients below set one: a long extraction is slow, not hung.
REQUEST_TIMEOUT = 60 * 60

#: Config ``mode`` value -> instructor mode, for the modes instructor drives.
INSTRUCTOR_MODES: dict[str, instructor.Mode] = {
    "tools": instructor.Mode.ANTHROPIC_TOOLS,
    "json": instructor.Mode.ANTHROPIC_JSON,
}

#: The mode this module drives itself, through the SDK. instructor cannot: its
#: Anthropic structured-outputs handler probes for a
#: ``Messages.create(output_format=...)`` parameter the SDK renamed to
#: ``output_config`` (anthropic 1.6.0), so the probe fails, the handler falls
#: back to prompt instructions without saying so, and its parser then demands a
#: text block that never arrives.
STRUCTURED_OUTPUTS = "json_schema"

#: Beta flag the ``output_config`` schema enforcement is behind.
STRUCTURED_OUTPUTS_BETA = "structured-outputs-2025-11-13"

#: Server-side refusal fallbacks. Opus 5.5 runs broader safety classifiers than
#: Opus 5 and declines some papers outright -- observed on a biology paper:
#: `stop_reason: refusal`, `category='bio'`. Pulling model and dataset names out
#: of a published paper is what the fallback is for: the API re-runs the request
#: on another model inside the same call, billed at that model's rates, instead
#: of handing back nothing. "default" lets the API route by refusal category
#: rather than us pinning a model list.
FALLBACKS_BETA = "server-side-fallback-2026-07-01"
FALLBACKS = "default"

MODES = tuple(INSTRUCTOR_MODES) + (STRUCTURED_OUTPUTS,)

#: Default when the config section has no ``mode`` (every existing config).
DEFAULT_MODE = "tools"


def strict_schema(node: Any) -> Any:
    """A pydantic JSON schema closed the way structured outputs require.

    Every object must set ``additionalProperties: false`` and list all of its
    properties as required, or the API answers 400.
    """
    if isinstance(node, list):
        return [strict_schema(child) for child in node]
    if not isinstance(node, dict):
        return node
    node = {key: strict_schema(value) for key, value in node.items()}
    if node.get("type") == "object" or "properties" in node:
        node["additionalProperties"] = False
        if node.get("properties"):
            node["required"] = list(node["properties"])
    return node


def structured_outputs_client(client: Any) -> Any:
    """An instructor-shaped client that uses the API's own schema enforcement.

    Exposes the one method the pipeline calls --
    ``chat.completions.create_with_completion`` -- so
    :meth:`Backend.instrument` wraps it like any instructor client. The schema
    goes in ``output_config`` and the API enforces it, so the reply is JSON,
    not prose with JSON in it. Models that reject forced tool use (Opus 5.5,
    the Fable line) need this path.
    """

    async def create_with_completion(
        *,
        response_model: Any,
        messages: list[dict[str, Any]],
        model: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        **kwargs: Any,
    ) -> tuple[Any, Any]:
        # Claude takes the system prompt top-level, not as a message.
        system = "\n\n".join(
            str(m["content"]) for m in messages if m["role"] == "system"
        )
        conversation = [m for m in messages if m["role"] != "system"]
        kwargs.pop("max_retries", None)  # instructor's, meaningless here

        response = await client.beta.messages.create(
            model=model,
            max_tokens=max_tokens,
            betas=[STRUCTURED_OUTPUTS_BETA, FALLBACKS_BETA],
            fallbacks=FALLBACKS,
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": strict_schema(response_model.model_json_schema()),
                }
            },
            **({"system": system} if system else {}),
            messages=conversation,
            **kwargs,
        )

        if response.stop_reason == "max_tokens":
            raise ValueError(
                f"output truncated at max_tokens={max_tokens}; raise it "
                "(paperext.backends.anthropic.DEFAULT_MAX_TOKENS)"
            )
        if response.stop_reason == "refusal":
            # every model in the fallback chain declined
            raise ValueError(
                f"model refused: {getattr(response, 'stop_details', None)}"
            )
        text = next(
            (b.text for b in response.content if getattr(b, "type", None) == "text"),
            None,
        )
        if text is None:
            blocks = [getattr(b, "type", "?") for b in response.content]
            raise ValueError(f"no text block in the response (blocks: {blocks})")
        return response_model.model_validate_json(text), response

    return SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create_with_completion=create_with_completion)
        )
    )


class AnthropicBase(Backend):
    """Everything an Anthropic-SDK backend does except constructing the client."""

    name = ""

    def async_client(self) -> Any:
        raise NotImplementedError

    def sync_client(self) -> Any:
        raise NotImplementedError

    # Anthropic requires max_tokens on every request; the extract loop sets none.
    # Claude uses the native "system" role (instructor maps a system message to
    # the top-level system param), so no message folding is needed.
    request_defaults = {"max_tokens": DEFAULT_MAX_TOKENS}

    @property
    def mode_name(self) -> str:
        """``mode`` from this backend's config section, validated."""
        try:  # Config raises KeyError for a missing option, so no getattr default
            raw = self.config.mode or DEFAULT_MODE
        except KeyError:
            raw = DEFAULT_MODE
        if raw not in MODES:
            raise ValueError(
                f"[{self.name}] mode must be one of {sorted(MODES)}, got {raw!r}"
            )
        return str(raw)

    @property
    def mode(self) -> instructor.Mode | None:
        """The instructor mode, or None when this module drives the request."""
        return INSTRUCTOR_MODES.get(self.mode_name)

    def build_client(self) -> instructor.AsyncInstructor:
        mode = self.mode
        if mode is None:  # STRUCTURED_OUTPUTS: driven here, not by instructor
            return structured_outputs_client(self.async_client())
        return instructor.from_anthropic(self.async_client(), mode=mode)

    def normalize_usage(self, completion: Any) -> dict[str, Any]:
        # Anthropic's usage already matches the canonical schema.
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
            self.check_credentials()
            client = self.sync_client()
        response = client.messages.create(
            model=model,
            max_tokens=16,
            messages=[{"role": "user", "content": message}],
        )
        # Models that think by default (Opus 5 and later) put a thinking block
        # first, so the reply is the first *text* block, not `content[0]`.
        text = next(
            (b.text for b in response.content if getattr(b, "type", None) == "text"),
            "",
        )
        return text, getattr(response, "usage", None)


@register
class AnthropicBackend(AnthropicBase):
    name = "anthropic"
    rate_limit_errors: tuple[type[BaseException], ...] = (anthropic.RateLimitError,)
    api_key_env = "ANTHROPIC_API_KEY"

    def async_client(self) -> Any:
        return anthropic.AsyncAnthropic(
            timeout=REQUEST_TIMEOUT
        )  # ANTHROPIC_API_KEY from the environment

    def sync_client(self) -> Any:
        return anthropic.Anthropic(timeout=REQUEST_TIMEOUT)
