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


# --------------------------------------------------------------------------- #
# Set-valued roll-up for multi-parent dimensions (D1h, #100)
# --------------------------------------------------------------------------- #
#
# :func:`to_category_map` above returns one category per name and must keep
# doing so: it reproduces the legacy map byte for byte, and ``models/v0`` is the
# sealed eval reference (#95). Two legacy collisions are cut-unstable, so the
# first-non-``Other`` dedup is a faithfulness requirement, not an oversight.
#
# The derived dimensions are DAGs on purpose -- counting is non-exclusive (E1,
# #16), so a node may sit under several parents and genuinely belong to several
# categories at once. Collapsing that to one category would not be a lossy
# summary, it would be a wrong answer. So the set-valued roll-up is an
# *additional* contract rather than a change to the existing one.


def _paths_to_cut(
    onto: Ontology, resolved: ResolvedCut
) -> "dict[str, set[tuple[str, str]]]":
    """``{node_id: {(root_id, cut_node_id_or_empty)}}``, one entry per path.

    Every root-to-node path is accounted for, because in a DAG each path can
    reach a different cut node, and the node belongs to all of them. The number
    of distinct ``(root, cut)`` pairs stays small even where the number of paths
    does not, which is what keeps this linear in practice.

    ``root_id`` is carried so a path through a dropped root can be discarded
    without discarding the node: a node reachable both from ``ignore`` and from
    a real branch still counts under the real one.
    """
    memo: "dict[str, set[tuple[str, int, str]]]" = {}

    def walk(node_id: str) -> "set[tuple[str, int, str]]":
        """``{(root, path_length, cut_node)}`` for every path reaching *node_id*."""
        if node_id in memo:
            return memo[node_id]
        memo[node_id] = set()  # cycle guard; a cycle is reported by the audit
        parents = onto.parents(node_id)
        if not parents:
            out = {(node_id, 1, node_id if _at_cut(onto, node_id, resolved, 1) else "")}
        else:
            out = set()
            for parent in parents:
                for root, length, cut in walk(parent):
                    here = length + 1
                    if isinstance(resolved, NodeCut):
                        nearest = node_id if node_id in resolved.ids else cut
                    else:
                        # Once the path is at least `depth` long the cut node is
                        # fixed; before that it is the node itself.
                        nearest = node_id if here <= resolved else cut
                    out.add((root, here, nearest))
        memo[node_id] = out
        return out

    return {nid: {(r, c) for r, _, c in walk(nid)} for nid in onto.nodes}


def _at_cut(onto: Ontology, node_id: str, resolved: ResolvedCut, length: int) -> bool:
    if isinstance(resolved, NodeCut):
        return node_id in resolved.ids
    return length <= resolved


def to_category_sets(
    onto: Ontology,
    cut: AnyCut,
    drop_roots: Iterable[str] = DEFAULT_DROP_ROOTS,
) -> "dict[str, set[str]]":
    """Roll *onto* up to *cut*, returning ``{normalized_name: {category, ...}}``.

    The multi-parent counterpart of :func:`to_category_map`. Differences, each
    because a single category would be wrong rather than merely coarse:

    - **A node under several parents yields several categories.** Non-exclusive
      counting is locked (#16), so this is the correct answer, not a tie to break.
    - **A name shared by several nodes yields the union of their categories**
      instead of the first in depth-first order. The legacy dedup exists to
      reproduce a map that had to pick one; here nothing has to.
    - **A path through a dropped root is discarded, not the node.** A node
      reachable from ``ignore`` *and* from a real branch still counts under the
      real one.

    A node that reaches no cut point on any path maps to ``{OTHER}`` -- aggregate,
    never drop, exactly as before.
    """
    resolved = resolve_cut(onto, cut)
    drop = {str_normalize(root) for root in drop_roots}

    mapping: "dict[str, set[str]]" = {}
    for node_id, paths in _paths_to_cut(onto, resolved).items():
        key = str_normalize(onto.name(node_id))
        if not key:
            continue
        live = [
            cut_id
            for root_id, cut_id in paths
            if str_normalize(onto.name(root_id)) not in drop
        ]
        if not live:
            continue
        mapping.setdefault(key, set()).update(
            onto.name(cut_id) if cut_id else OTHER for cut_id in live
        )
    return mapping
