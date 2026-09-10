"""Where a decision put a name — one shared definition (WS-D D1b-1, #51).

The runner records a placement per decision and the eval scores placements, so
this has to be computed in exactly one place or the two drift and every #53 number
becomes unattributable.

A placement is resolved against the **pre-decision** tree. That is not a detail:
the tree mutates as a run proceeds, so a bare ``create_node(parent=X)`` cannot be
resolved after the fact — scoring a run later would mean re-running the agent.

Two entry points, one roll-up:

- :func:`to_placement` — where an **existing** node sits.
- :func:`placement_for_new` — where a node *would* sit if created under a parent.
  Not the same answer: under a depth cut, a new child of a depth-1 node lands one
  level deeper than the parent and rolls up to a different category.

The roll-up itself reuses :mod:`paperext.ontology.rollup`'s helpers rather than
reimplementing them, for the same anti-drift reason.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Union

from pydantic import BaseModel, Field

from paperext.analysis.rollup import DEFAULT_DROP_ROOTS, Cut, str_normalize
from paperext.ontology.ontology import Ontology, UnknownNodeError
from paperext.ontology.rollup import (
    _category_at_depth,
    _category_at_nodes,
    _norm_dotpath,
)

if TYPE_CHECKING:  # pragma: no cover - import cycle: actions -> ontology -> here
    from paperext.categorize.actions import Decision

#: A cut normalized once: either a depth, or a set of normalized dot-paths.
NormalizedCut = Union[int, "set[str]"]


class Placement(BaseModel):
    """Where a name ended up, at every granularity the report consumes.

    ``node_id`` is ``None`` for a node that does not exist yet (a ``create_node``
    resolved against the pre-decision tree). ``cut_category`` is ``None`` when the
    placement sits under a dropped root (``ignore``), i.e. it contributes to no
    category at all — distinct from rolling up to ``Other``.
    """

    node_id: str | None = None
    name: str
    parent_id: str | None = None
    ancestor_path: list[str] = Field(default_factory=list)
    ancestor_names: list[str] = Field(default_factory=list)
    depth: int
    branch: str | None = None
    cut_category: str | None = None


def normalize_cut(cut: Cut) -> NormalizedCut:
    """Validate *cut* and normalize it once, mirroring :func:`to_category_map`."""
    if isinstance(cut, bool):  # bool is an int subclass; reject explicitly
        raise TypeError("cut must be an int depth or an iterable of dot-paths")
    if isinstance(cut, int):
        if cut < 1:
            raise ValueError(f"depth cut must be >= 1, got {cut}")
        return cut
    if isinstance(cut, str):
        cut = [cut]
    return {_norm_dotpath(entry) for entry in cut}


def load_dimension_cut(dimension: str) -> Cut:
    """The cut a dimension reports at: its milabench file, else depth 2.

    Same resolution as ``analysis/frequency.py:_default_dimensions`` — models and
    research fields have committed milabench cut files, datasets do not.
    """
    from paperext.analysis.rollup import load_cut
    from paperext.config import CFG

    cfg: Any = CFG  # the config proxy resolves attributes dynamically
    files = {
        "models": Path(cfg.dir.evaluation_mod_cat) / str(cfg.evaluation.mod_cat),
        "domains": Path(cfg.dir.evaluation_dom_cat) / str(cfg.evaluation.dom_cat),
    }
    path = files.get(dimension)
    if path is not None and path.exists():
        return load_cut(path)
    return 2


def _build(
    onto: Ontology,
    *,
    node_id: str | None,
    name: str,
    ancestors: "list[str]",
    cut: NormalizedCut,
    drop_roots: Iterable[str],
) -> Placement:
    """Assemble a placement from the ancestor ids of its *parent* chain.

    *ancestors* is the root-to-parent id chain; *name* is the placed node's own
    display name, appended to form the path the roll-up sees.
    """
    ancestor_names = [onto.name(nid) for nid in ancestors]
    raw_path = tuple(ancestor_names) + (name,)
    norm_path = tuple(str_normalize(part) for part in raw_path)

    drop = {str_normalize(root) for root in drop_roots}
    if norm_path and norm_path[0] in drop:
        category = None
    elif isinstance(cut, int):
        category = _category_at_depth(raw_path, cut)
    else:
        category = _category_at_nodes(norm_path, raw_path, cut)

    return Placement(
        node_id=node_id,
        name=name,
        parent_id=ancestors[-1] if ancestors else None,
        ancestor_path=list(ancestors) + ([node_id] if node_id is not None else []),
        ancestor_names=list(raw_path),
        depth=len(raw_path),
        branch=ancestor_names[0] if ancestor_names else name,
        cut_category=category,
    )


def to_placement(
    onto: Ontology,
    node_id: str,
    cut: Cut,
    *,
    drop_roots: Iterable[str] = DEFAULT_DROP_ROOTS,
) -> Placement:
    """Placement of an **existing** node."""
    if node_id not in onto:
        raise UnknownNodeError(node_id)
    ancestry = onto.ancestry(node_id)  # root -> node, inclusive
    return _build(
        onto,
        node_id=node_id,
        name=onto.name(node_id),
        ancestors=ancestry[:-1],
        cut=normalize_cut(cut),
        drop_roots=drop_roots,
    )


def placement_for_new(
    onto: Ontology,
    parent_id: str | None,
    name: str,
    cut: Cut,
    *,
    drop_roots: Iterable[str] = DEFAULT_DROP_ROOTS,
) -> Placement:
    """Placement a node named *name* **would** have if created under *parent_id*."""
    if parent_id is not None and parent_id not in onto:
        raise UnknownNodeError(parent_id)
    ancestors = onto.ancestry(parent_id) if parent_id is not None else []
    return _build(
        onto,
        node_id=None,
        name=name,
        ancestors=ancestors,
        cut=normalize_cut(cut),
        drop_roots=drop_roots,
    )


def resolve_placement(
    onto: Ontology,
    decision: "Decision",
    cut: Cut,
    *,
    drop_roots: Iterable[str] = DEFAULT_DROP_ROOTS,
) -> Placement | None:
    """Where *decision* puts its surface, against the **pre-decision** *onto*.

    Reads the decision's own actions rather than the mutated tree: the last
    ``add_surface`` naming the decision's surface fixes the target. When that
    target is a node the same decision creates, the placement is computed from the
    ``create_node`` that creates it (which does not exist in *onto* yet).

    ``None`` when the decision maps nothing — an abstention, a no-op, a failure, or
    a decision made purely of in-flight fixes.
    """
    from paperext.categorize.actions import AddSurface, CreateNode, InsertAbove

    want = str_normalize(decision.surface)
    target: str | None = None
    for action in decision.actions:
        if isinstance(action, AddSurface) and str_normalize(action.surface) == want:
            target = action.canonical
    if target is None:
        return None

    for action in decision.actions:
        if isinstance(action, CreateNode) and action.node_id == target:
            return placement_for_new(
                onto, action.parent, action.name, cut, drop_roots=drop_roots
            )
        if isinstance(action, InsertAbove) and action.new_id == target:
            parents = onto.parents(action.node_id)
            return placement_for_new(
                onto,
                parents[0] if parents else None,
                action.name,
                cut,
                drop_roots=drop_roots,
            )

    if target not in onto:
        raise UnknownNodeError(target)
    return to_placement(onto, target, cut, drop_roots=drop_roots)
