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
# one, so the backend injects a default. Billing is per actual output token, so
# a generous ceiling costs nothing and only guards against truncation.
#
# The history is a record of this ceiling being outgrown, which is why it is now
# configurable rather than a constant to edit:
#
# - v4, 2024 corpus: largest extraction ~7.2k tokens.
# - 16k truncated the longest papers -- `IncompleteOutputException` on 8 of 40 in
#   the tier comparison, every one a fulltext call -- because thinking tokens
#   count toward this ceiling on the models that think by default (Opus 5+).
# - 32k was outgrown by **schema v5**, measured on the C0 sample (#103): mean
#   output 20.2k, max 29.5k, i.e. 3.2k of headroom (10%) on the largest paper
#   that succeeded, and 1 of the first 9 papers truncated outright. v5 added
#   `runs[]`, `algorithms[]` and `data_sources[]`, so its output is about 3x v4's.
#
# 48k is ~1.6x the largest observed v5 extraction. Override per-backend with
# `max_tokens` in the config section, or `PAPEREXT_ANTHROPIC_MAX_TOKENS`.
DEFAULT_MAX_TOKENS = 49152

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
                f"output truncated at max_tokens={max_tokens}; raise "
                "`max_tokens` in the backend's config section (or "
                "PAPEREXT_ANTHROPIC_MAX_TOKENS). Billing is per actual output "
                "token, so a higher ceiling costs nothing unless used"
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
    @property
    def request_defaults(self) -> "dict[str, Any]":
        return {"max_tokens": self.max_tokens}

    @property
    def max_tokens(self) -> int:
        """``max_tokens`` from this backend's config section, or the default.

        Configurable because the ceiling has been outgrown twice, each time by a
        schema change rather than by a longer paper -- see DEFAULT_MAX_TOKENS.
        A truncation costs a whole paper's extraction, so this is worth being
        able to raise without editing code.
        """
        try:  # Config raises KeyError for a missing option, so no getattr default
            raw = self.config.max_tokens
        except KeyError:
            return DEFAULT_MAX_TOKENS
        if not str(raw).strip():
            return DEFAULT_MAX_TOKENS
        try:
            value = int(raw)
        except TypeError, ValueError:
            raise ValueError(f"max_tokens must be an integer, got {raw!r}") from None
        if value <= 0:
            raise ValueError(f"max_tokens must be positive, got {value}")
        return value

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

    def diagnose(self, error: BaseException) -> "str | None":
        """Name the fix for the one 400 that is purely a mode mismatch.

        Opus 5.5 and later refuse a forced tool call, so `mode = tools` fails
        every paper with *tool_choice: type "tool" and "any" are not supported
        for this model*. The structured-outputs path sends no `tool_choice` at
        all, so the fix is one environment variable -- but the API's message
        does not say that, and a run of 26 papers fails 26 times before anyone
        reads it.
        """
        message = str(error)
        if "compiled grammar is too large" in message:
            return (
                "the v5 extraction schema exceeds this model's strict-grammar "
                "limit on the structured-outputs path. All three modes are "
                "blocked for a model that also refuses forced tools: `tools` "
                "is rejected by the model, `json_schema` hits this limit, and "
                "`json` trips instructor's strict decoder on our quotes. Use a "
                "model that accepts forced tools (PAPEREXT_ANTHROPIC_MODEL="
                "claude-opus-5 with mode=tools is the combination the C0 batch "
                "ran at 25/25), or shrink the schema -- which is a design "
                "change, not a setting"
            )
        if "tool_choice" in message and "not supported for this model" in message:
            return (
                f"{self.model!r} does not support a forced tool call, which "
                f"mode={self.mode_name!r} requires. Use the structured-outputs "
                f"path instead: PAPEREXT_{self.name.upper()}_MODE="
                f"{STRUCTURED_OUTPUTS} (or set `mode = {STRUCTURED_OUTPUTS}` in "
                f"the [{self.name}] config section)"
            )
        return None

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
