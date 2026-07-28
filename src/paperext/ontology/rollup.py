"""Ontology -> flat ``{normalized_name: category}`` converter (D1a, #36).

Bridges the layered ontology back to the flat map
:func:`paperext.analysis.rollup.build_category_map` returns, so E1
(``frequency.py`` / ``workload.py``) keeps working unchanged while we validate
``v0`` against the legacy trees.

Reproduction, not composition-through-normalization. The legacy map keys every
node by its own normalized name and, on a key collision, keeps the **first**
category seen in depth-first order unless that first was ``Other`` (then the first
non-``Other`` wins). Two legacy collisions (``sam`` in models, ``classification``
in domains) are *cut-unstable*: the depth-1 winner and the milabench-cut winner
are different nodes, so no single ``surface -> one id`` map can reproduce both.
This converter therefore replays that exact per-cut dedup over the ontology's
DFS-ordered node names — the 1:1 normalization DB is the D1b lookup index, not the
mechanism that generates roll-up keys.
"""

import logging
from typing import Iterable

from paperext.analysis.rollup import (
    DEFAULT_DROP_ROOTS,
    OTHER,
    Cut,
    str_normalize,
)
from paperext.ontology.ontology import Ontology

logger = logging.getLogger(__name__)


def _norm_dotpath(dotted: str) -> str:
    """Normalize a dot-path segment-by-segment (``.`` kept as separator)."""
    return ".".join(str_normalize(seg) for seg in dotted.split("."))


def _category_at_depth(raw_path: tuple, depth: int) -> str:
    idx = min(depth, len(raw_path)) - 1
    return raw_path[idx]


def _category_at_nodes(norm_path: tuple, raw_path: tuple, cutset: "set[str]") -> str:
    for i in range(len(norm_path), 0, -1):
        if ".".join(norm_path[:i]) in cutset:
            return raw_path[i - 1]
    return OTHER


def to_category_map(
    onto: Ontology,
    cut: Cut,
    drop_roots: Iterable[str] = DEFAULT_DROP_ROOTS,
) -> "dict[str, str]":
    """Roll *onto* up to *cut*, returning ``{normalized_name: category}``.

    Semantics are identical to :func:`paperext.analysis.rollup.roll_up`: aggregate
    (never drop) to ``Other``, drop only the configured root branch(es), key by
    normalized node name, first-non-``Other`` wins on collision.
    """
    if isinstance(cut, bool):  # bool is an int subclass; reject explicitly
        raise TypeError("cut must be an int depth or an iterable of dot-paths")

    if isinstance(cut, str):
        cut = [cut]

    depth: int | None
    cutset: set[str] | None
    if isinstance(cut, int):
        if cut < 1:
            raise ValueError(f"depth cut must be >= 1, got {cut}")
        depth = cut
        cutset = None
    else:
        depth = None
        cutset = {_norm_dotpath(entry) for entry in cut}
        if not cutset:
            logger.warning("cut is empty: every node will roll up to %r", OTHER)

    drop = {str_normalize(root) for root in drop_roots}

    all_paths: "set[str]" = set()
    mapping: "dict[str, str]" = {}
    seen_reserved = False
    for _node_id, norm_path, raw_path in onto.iter_nodes():
        all_paths.add(".".join(norm_path))

        if raw_path[-1] == OTHER and not seen_reserved:
            seen_reserved = True
            logger.warning(
                "ontology contains a node named %r, the reserved fallback label; "
                "its counts will merge with unmatched nodes",
                OTHER,
            )

        if norm_path[0] in drop:
            continue

        key = norm_path[-1]
        if not key:
            continue

        if cutset is not None:
            category = _category_at_nodes(norm_path, raw_path, cutset)
        else:
            assert depth is not None  # depth and cutset are set in tandem
            category = _category_at_depth(raw_path, depth)

        previous = mapping.get(key)
        if previous is not None and previous != category:
            logger.warning(
                "Name %r maps to multiple categories: %r vs %r; keeping %r",
                key,
                previous,
                category,
                previous if previous != OTHER else category,
            )
            if previous != OTHER:
                continue

        mapping[key] = category

    if cutset is not None:
        for entry in sorted(cutset - all_paths):
            logger.warning("cut node %r matches no node in the tree", entry)

    return mapping
