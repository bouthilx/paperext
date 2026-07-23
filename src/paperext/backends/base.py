"""Common interface every model backend implements.

A backend bundles everything provider-specific behind one shape: how to build
the (instructor) client, how to normalize token usage, which errors count as
retryable rate limits, and how to run a connectivity smoke-check. The rest of
the codebase talks to backends only through this interface + the registry in
``paperext.backends``.
"""

from abc import ABC, abstractmethod
from typing import Any, Tuple

from paperext.config import CFG


class Backend(ABC):
    #: Registry key. Doubles as the config section (``CFG.<name>``), the
    #: ``--platform`` value, and the storage-bucket provider.
    name: str = ""

    #: Exception types the query loop treats as retryable rate-limit errors.
    #: Empty tuple -> never retried (``except ():`` catches nothing).
    rate_limit_errors: Tuple[type, ...] = ()

    @property
    def model(self) -> str:
        """Configured model for this backend (``CFG.<name>.model``)."""
        return getattr(CFG, self.name).model

    @abstractmethod
    def make_client(self):
        """Return an instructor client whose
        ``chat.completions.create_with_completion`` yields
        ``(extractions, usage)`` for this provider."""

    @abstractmethod
    def normalize_usage(self, completion) -> Any:
        """Extract a serializable token-usage record from a raw completion."""

    @abstractmethod
    def smoke_check(self, model: str = None) -> Tuple[str, Any]:
        """Make one trivial completion; return ``(reply_text, usage)``.

        Proves auth + model access without touching the extraction pipeline.
        """
