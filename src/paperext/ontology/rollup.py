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

Cuts are matched on node **ids**, not names (D1a-3, #62). A milabench cut file is
spelled in names, so :func:`resolve_cut` converts it once — against the version it
was written for — into a :class:`NodeCut`; ids survive every mutation the agent may
apply, while names are display text it is told to improve. The category label is
the cut node's *current* name, so renaming a cut node relabels its category
instead of emptying it into ``Other``.
"""

import logging
from dataclasses import dataclass
from typing import Iterable, Sequence, Union

from paperext.analysis.rollup import (
    DEFAULT_DROP_ROOTS,
    OTHER,
    Cut,
    str_normalize,
)
from paperext.ontology.ontology import Ontology

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NodeCut:
    """A per-branch cut resolved to node ids.

    Valid for every version derived from the one it was resolved against: ids are
    never reassigned. A cut node that a later version removed simply matches no
    ancestry any more.
    """

    ids: frozenset[str]


#: A cut once resolved: a depth, or a set of node ids.
ResolvedCut = Union[int, NodeCut]
#: What roll-up and placement accept: a resolved cut, or the legacy spelling
#: (a depth, or name dot-paths resolved against the tree being rolled up).
AnyCut = Union[Cut, NodeCut]


class UnresolvedCutError(ValueError):
    """A cut dot-path names no node in the tree it was resolved against."""


def _norm_dotpath(dotted: str) -> str:
    """Normalize a dot-path segment-by-segment (``.`` kept as separator)."""
    return ".".join(str_normalize(seg) for seg in dotted.split("."))


def resolve_cut(onto: Ontology, cut: AnyCut) -> ResolvedCut:
    """Validate *cut* and resolve name dot-paths to node ids against *onto*.

    A depth or an already-resolved :class:`NodeCut` passes through. Name paths
    must every one match a node: a silent miss would send a whole branch to
    ``Other``, which is exactly the failure this module exists to prevent.
    """
    if isinstance(cut, NodeCut):
        return cut
    if isinstance(cut, bool):  # bool is an int subclass; reject explicitly
        raise TypeError("cut must be an int depth or an iterable of dot-paths")
    if isinstance(cut, int):
        if cut < 1:
            raise ValueError(f"depth cut must be >= 1, got {cut}")
        return cut
    if isinstance(cut, str):
        cut = [cut]
    wanted = {_norm_dotpath(entry) for entry in cut}
    if not wanted:
        logger.warning("cut is empty: every node will roll up to %r", OTHER)

    ids: "set[str]" = set()
    found: "set[str]" = set()
    for node_id, norm_path, _raw_path in onto.iter_nodes():
        dotted = ".".join(norm_path)
        if dotted in wanted:
            ids.add(node_id)
            found.add(dotted)
    missing = sorted(wanted - found)
    if missing:
        raise UnresolvedCutError(
            f"cut entries match no node in {onto.doc.meta.dimension}/"
            f"{onto.doc.meta.version}: {missing}"
        )
    return NodeCut(frozenset(ids))


def _category_at_depth(raw_path: tuple, depth: int) -> str:
    idx = min(depth, len(raw_path)) - 1
    return raw_path[idx]


def cut_node_of(id_path: Sequence[str], cut: NodeCut) -> "str | None":
    """Id of the nearest cut node in *id_path* (self first); ``None`` when none."""
    for node_id in reversed(id_path):
        if node_id in cut.ids:
            return node_id
    return None


def _category_at_nodes(onto: Ontology, id_path: Sequence[str], cut: NodeCut) -> str:
    """Current name of the cut node *id_path* rolls up to, else ``Other``."""
    node_id = cut_node_of(id_path, cut)
    return onto.name(node_id) if node_id is not None else OTHER


def to_category_map(
    onto: Ontology,
    cut: AnyCut,
    drop_roots: Iterable[str] = DEFAULT_DROP_ROOTS,
) -> "dict[str, str]":
    """Roll *onto* up to *cut*, returning ``{normalized_name: category}``.

    Semantics are identical to :func:`paperext.analysis.rollup.roll_up`: aggregate
    (never drop) to ``Other``, drop only the configured root branch(es), key by
    normalized node name, first-non-``Other`` wins on collision. Name dot-paths
    are resolved against *onto* itself; pass a :class:`NodeCut` to roll a derived
    version up at the cut of the version it came from.
    """
    resolved = resolve_cut(onto, cut)
    drop = {str_normalize(root) for root in drop_roots}

    mapping: "dict[str, str]" = {}
    seen_reserved = False
    id_path: "list[str]" = []  # root-to-node ids, maintained along the pre-order walk
    for node_id, norm_path, raw_path in onto.iter_nodes():
        del id_path[len(norm_path) - 1 :]
        id_path.append(node_id)

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

        if isinstance(resolved, NodeCut):
            category = _category_at_nodes(onto, id_path, resolved)
        else:
            category = _category_at_depth(raw_path, resolved)

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

    return mapping
