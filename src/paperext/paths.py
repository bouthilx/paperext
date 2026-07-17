"""Filesystem helpers for model-scoped result storage.

Query and evaluation results are bucketed by ``<provider>/<model-slug>/`` so
that a run only overwrites previous results when both the platform (provider)
*and* the model+version match exactly. This lets several providers -- and
several models per provider -- coexist on disk without collisions.
"""

import re
from pathlib import Path

from paperext.config import CFG

# Everything that is not a plain path-safe character (alphanumerics, dot, dash,
# underscore) collapses to a single dash.
_SLUG_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def model_slug(model: str) -> str:
    """Normalize an LLM model identifier to a filesystem-safe path segment.

    Alphanumerics, ``.``, ``-`` and ``_`` are kept as-is; every other run of
    characters (path separators, ``@``, whitespace, ...) collapses to a single
    ``-``. e.g. ``models/gemini-1.5-pro`` -> ``models-gemini-1.5-pro`` and
    ``claude-3-5-sonnet@20240620`` -> ``claude-3-5-sonnet-20240620``.
    """
    if model is None or not str(model).strip():
        raise ValueError("model must be a non-empty string to build a storage bucket")
    slug = _SLUG_UNSAFE.sub("-", str(model).strip()).strip("-")
    if not slug:
        raise ValueError(f"model {model!r} normalized to an empty slug")
    return slug


def selected_model() -> str:
    """Model configured for the currently selected platform (``CFG.<select>.model``)."""
    return getattr(CFG, CFG.platform.select).model


def bucket(base: Path, provider: str, model: str) -> Path:
    """``base / <provider> / <model-slug>`` for an explicit provider + model.

    Use this to read or compare results across providers/models -- e.g. the
    bake-off scoring several arms, or cross-model analysis -- without mutating
    the global ``CFG.platform`` selection. ``platform_bucket`` is the wrapper
    that resolves both arguments from the current selection.
    """
    return Path(base) / provider / model_slug(model)


def platform_bucket(base: Path) -> Path:
    """``bucket`` for the currently selected platform and its configured model."""
    return bucket(base, CFG.platform.select, selected_model())
