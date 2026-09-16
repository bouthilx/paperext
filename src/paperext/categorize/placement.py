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
reimplementing them, for the same anti-drift reason. Cuts match on node ids
(#62): a run against ``v<N>`` must use the cut resolved against the version the
cut file was written for — :func:`load_dimension_cut` does that — not one
re-resolved by name against a tree the agent has already renamed nodes in.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable

from pydantic import BaseModel, Field

from paperext.analysis.rollup import DEFAULT_DROP_ROOTS, str_normalize
from paperext.ontology.ontology import Ontology, UnknownNodeError
from paperext.ontology.rollup import (
    AnyCut,
    NodeCut,
    ResolvedCut,
    _category_at_depth,
    _category_at_nodes,
    resolve_cut,
)

if TYPE_CHECKING:  # pragma: no cover - import cycle: actions -> ontology -> here
    from paperext.categorize.actions import Decision

#: The version the committed cut files are spelled against. ``v0`` is the frozen
#: import of the legacy trees (its content hash is pinned in the eval manifest);
#: ids are never reassigned after it, so a cut resolved here holds for every
#: ``v<N>`` derived from it.
CUT_BASE = "v0"


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


def load_dimension_cut(
    dimension: str, *, root: Path | None = None, base: str = CUT_BASE
) -> ResolvedCut:
    """The cut a dimension reports at: its milabench file, else depth 2.

    Same file resolution as ``analysis/frequency.py:_default_dimensions`` — models
    and research fields have committed milabench cut files, datasets do not. The
    file's name paths are resolved to node ids against ``<root>/<dimension>/<base>``
    once, so the result is valid for any version derived from *base*.
    """
    from paperext.analysis.rollup import load_cut
    from paperext.categorize.apply import ontology_root
    from paperext.config import CFG

    cfg: Any = CFG  # the config proxy resolves attributes dynamically
    files = {
        "models": Path(cfg.dir.evaluation_mod_cat) / str(cfg.evaluation.mod_cat),
        "domains": Path(cfg.dir.evaluation_dom_cat) / str(cfg.evaluation.dom_cat),
    }
    path = files.get(dimension)
    if path is None or not path.exists():
        return 2
    root = root if root is not None else ontology_root()
    return resolve_cut(Ontology.load(root / dimension / base), load_cut(path))


def _build(
    onto: Ontology,
    *,
    node_id: str | None,
    name: str,
    ancestors: "list[str]",
    cut: ResolvedCut,
    drop_roots: Iterable[str],
) -> Placement:
    """Assemble a placement from the ancestor ids of its *parent* chain.

    *ancestors* is the root-to-parent id chain; *name* is the placed node's own
    display name, appended to form the path the roll-up sees. A node that does not
    exist yet has no id and so cannot itself be a cut node: it rolls up to the
    nearest cut node among its ancestors.
    """
    ancestor_names = [onto.name(nid) for nid in ancestors]
    raw_path = tuple(ancestor_names) + (name,)
    id_path = list(ancestors) + ([node_id] if node_id is not None else [])

    drop = {str_normalize(root) for root in drop_roots}
    if raw_path and str_normalize(raw_path[0]) in drop:
        category = None
    elif isinstance(cut, NodeCut):
        category = _category_at_nodes(onto, id_path, cut)
    else:
        category = _category_at_depth(raw_path, cut)

    return Placement(
        node_id=node_id,
        name=name,
        parent_id=ancestors[-1] if ancestors else None,
        ancestor_path=id_path,
        ancestor_names=list(raw_path),
        depth=len(raw_path),
        branch=ancestor_names[0] if ancestor_names else name,
        cut_category=category,
    )


def to_placement(
    onto: Ontology,
    node_id: str,
    cut: AnyCut,
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
        cut=resolve_cut(onto, cut),
        drop_roots=drop_roots,
    )


def placement_for_new(
    onto: Ontology,
    parent_id: str | None,
    name: str,
    cut: AnyCut,
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
        cut=resolve_cut(onto, cut),
        drop_roots=drop_roots,
    )


def resolve_placement(
    onto: Ontology,
    decision: "Decision",
    cut: AnyCut,
    *,
    drop_roots: Iterable[str] = DEFAULT_DROP_ROOTS,
) -> Placement | None:
    """Where *decision* puts its surface, against the **pre-decision** *onto*.

    Reads the decision's own actions rather than the mutated tree: the last
    ``add_surface`` naming the decision's surface fixes the target. When that
    target is a node the same decision creates, the placement is computed from the
    ``create_node`` that creates it (which does not exist in *onto* yet).

    When no action maps the surface but *onto* already resolves it (a ``no_op`` on
    an already-mapped name, #67), the placement is where it already sits. ``None``
    only when the surface is mapped nowhere — an abstention, a failure, or a
    decision made purely of in-flight fixes on an unmapped name.
    """
    from paperext.categorize.actions import CreateNode, InsertAbove

    target = decision.mapping_target()
    if target is None:
        target = onto.resolve(decision.surface)
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
