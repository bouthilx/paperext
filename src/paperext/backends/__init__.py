"""Model-backend registry.

Each backend lives in its own module and registers itself via ``@register`` on
import. A module is imported only if its SDK is installed, so a backend is
available exactly when its dependencies are -- the same SDK-guard the old
``PLATFORMS`` try/except blocks provided, but uniform.
"""

import logging
from importlib import import_module

from paperext.backends.base import Backend

logger = logging.getLogger(__name__)

_BACKENDS: "dict[str, Backend]" = {}

# Backend modules to attempt to load. Each registers itself on import; a missing
# SDK raises ModuleNotFoundError and the backend is simply skipped.
_BACKEND_MODULES = ("openai", "vertexai")


def register(backend_cls):
    """Class decorator: instantiate and register a :class:`Backend`."""
    instance = backend_cls()
    if not instance.name:
        raise ValueError(f"{backend_cls.__name__} must define a non-empty name")
    _BACKENDS[instance.name] = instance
    return backend_cls


def get_backend(name: str) -> Backend:
    try:
        return _BACKENDS[name]
    except KeyError:
        raise KeyError(
            f"Backend {name!r} is not available "
            f"(installed: {available() or 'none'}). Is its SDK extra installed?"
        )


def available() -> "list[str]":
    """Names of backends whose SDKs are installed and registered."""
    return sorted(_BACKENDS)


for _mod in _BACKEND_MODULES:
    try:
        import_module(f"{__name__}.{_mod}")
    except ModuleNotFoundError as e:
        logger.info("Backend %r unavailable: %s", _mod, e)
