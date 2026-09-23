"""Common interface every model backend implements.

A backend bundles everything provider-specific behind one shape: how to build
the (instructor) client, how to normalize token usage, which errors count as
retryable rate limits, and how to run a connectivity smoke-check. The rest of
the codebase talks to backends only through this interface + the registry in
``paperext.backends``.

Every backend builds an async client (``instructor.AsyncInstructor``), so the
extraction pipeline always ``await``s a single, uniform client type.

**Failures say which backend they came from.** A run can hold two clients at
once (the categorization agent and a different-vendor judge), and provider SDKs
raise bare errors -- ``"Could not resolve authentication method"``, a 429, a 401
-- that name neither the provider nor the role. So a missing credential is
caught here, before the first request, and anything the SDK still raises gets a
note naming the backend, the model and the label the caller built the client
with.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

import instructor

from paperext.config import CFG


class BackendError(RuntimeError):
    """A backend problem, phrased so the backend that had it is identifiable."""


class BackendAuthError(BackendError):
    """A backend's credentials are missing."""


class Backend(ABC):
    #: Registry key. Doubles as the config section (``CFG.<name>``), the
    #: ``--platform`` value, and the storage-bucket provider.
    name: str = ""

    #: Exception types the query loop treats as retryable rate-limit errors.
    #: Empty tuple -> never retried (``except ():`` catches nothing).
    rate_limit_errors: tuple[type[BaseException], ...] = ()

    #: Environment variable holding this backend's credential. ``None`` when it
    #: authenticates some other way (the Vertex backends use GCP credentials).
    api_key_env: str | None = None

    #: Request kwargs the pipeline never sets but the provider requires.
    request_defaults: dict[str, Any] = {}

    #: Whether the model is named per request. False when it is bound to the
    #: client instead (Vertex's ``GenerativeModel``).
    names_model_per_request: bool = True

    def describe(self, label: str = "") -> str:
        """``anthropic/claude-opus-5 (judge)`` -- who this is, for an error."""
        who = f"{self.name}/{self.model}"
        return f"{who} ({label})" if label else who

    def check_credentials(self, label: str = "") -> None:
        """Raise before the first request if the credential is missing.

        The SDKs do not: OpenAI sends an empty key and gets a 401, Anthropic
        raises a ``TypeError`` from inside a retry wrapper. Neither names the
        provider, which is unreadable when two backends are in play.
        """
        if self.api_key_env and not os.environ.get(self.api_key_env):
            raise BackendAuthError(
                f"{self.describe(label)}: ${self.api_key_env} is not set in the "
                f"environment. Export it in the shell that runs this command; "
                f"the tracked config's [env] section holds a blank placeholder "
                f"on purpose, so credentials are never committed."
            )

    @property
    def config(self) -> Any:
        """This backend's config section (``CFG.<name>``)."""
        return getattr(CFG, self.name)

    @property
    def model(self) -> str:
        """Configured model for this backend (``CFG.<name>.model``)."""
        return self.config.model

    def make_client(self, label: str = "") -> instructor.AsyncInstructor:
        """A checked, instrumented async client for this backend.

        *label* is the caller's role for this client (``"agent"``, ``"judge"``):
        it appears in every error this client produces, which is what tells a
        two-client run which half failed.
        """
        self.check_credentials(label)
        return self.instrument(self.build_client(), label=label)

    @abstractmethod
    def build_client(self) -> instructor.AsyncInstructor:
        """Return the raw instructor client for this provider.

        :meth:`make_client` wraps it; it is separate so that credential checks
        and error context are applied uniformly rather than per backend.
        """

    def prepare_request(self, kwargs: "dict[str, Any]") -> None:
        """Per-provider fixups on the outgoing request (default: none)."""

    def instrument(
        self, client: instructor.AsyncInstructor, *, label: str = ""
    ) -> instructor.AsyncInstructor:
        """Pin the model, apply request defaults, normalize usage, name failures.

        The model and description are captured **now**: the caller may be
        building this client under a scoped config override
        (:func:`paperext.categorize.agent.make_client`), which is gone by the
        time a request is made.
        """
        model = self.model
        who = self.describe(label)
        credentials = (
            f"; credentials come from ${self.api_key_env}" if self.api_key_env else ""
        )
        create = client.chat.completions.create_with_completion

        async def create_with_completion(*args: Any, **kwargs: Any) -> tuple[Any, Any]:
            for key, value in self.request_defaults.items():
                kwargs.setdefault(key, value)
            self.prepare_request(kwargs)
            if self.names_model_per_request:
                kwargs.setdefault("model", model)
            try:
                extractions, completion = await create(*args, **kwargs)
            except Exception as error:
                # a note, not a wrapper: the retry loops match on the SDK's own
                # rate-limit types, and re-raising something else would blind them
                error.add_note(f"paperext: raised by {who}{credentials}")
                raise
            return extractions, self.normalize_usage(completion)

        setattr(
            client.chat.completions, "create_with_completion", create_with_completion
        )
        return client

    @abstractmethod
    def normalize_usage(self, completion: Any) -> dict[str, Any]:
        """Extract a serializable token-usage record from a raw completion.

        Returns a dict with the canonical, provider-agnostic keys
        ``input_tokens`` / ``output_tokens`` / ``total_tokens`` so usage is
        comparable across backends (cost analysis, the B1 bake-off). Backends
        may add provider-specific keys alongside these (e.g. Gemini's
        ``cached_content_token_count``).
        """

    @abstractmethod
    def smoke_check(self, model: str | None = None) -> tuple[str, Any]:
        """Make one trivial completion; return ``(reply_text, usage)``.

        Proves auth + model access without touching the extraction pipeline.
        Implementations call :meth:`check_credentials` first, so an unset key
        reads as such instead of as a provider error.
        """
