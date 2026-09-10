"""LLM categorization agent for the layered ontology (WS-D D1b, #44).

Sits on top of :mod:`paperext.ontology` (the pure data model from D1a) and adds
the *decision* layer: what a name maps to, whether a node must be created, and
which in-flight fixes the tree needs.

This module (D1b-1, #51) is the **deterministic half** — the action vocabulary,
the transactional applier, and the eval scaffolding. It performs no API calls and
imports neither ``instructor`` nor :mod:`paperext.backends`; the prompt assembler
and agent loop are D1b-2 (#52), the eval harness D1b-3 (#53).

Layers::

    extraction record -> [agent]      -> Decision(actions=[Action, ...])
    Decision          -> [apply]      -> mutated Ontology + DecisionRecord
    DecisionRecord    -> decisions.jsonl (append-only audit + replay input)
"""

from paperext.categorize.ablate import AblationError, ablatable, ablate
from paperext.categorize.actions import (
    OPS,
    Action,
    ActionStatus,
    AddSurface,
    AppliedAction,
    CreateNode,
    Decision,
    DemoteToVariant,
    InsertAbove,
    MarkIgnore,
    Move,
    OpSpec,
    Outcome,
    Provenance,
    RemoveNode,
    RemoveSurface,
    Rename,
    UpdateDescription,
)
from paperext.categorize.apply import (
    ApplyResult,
    DecisionDiff,
    DecisionLog,
    DecisionRecord,
    apply_decision,
    content_hash,
    diff_snapshots,
    next_version,
    read_decisions,
    suggest_node_id,
    write_snapshot,
)
from paperext.categorize.placement import (
    Placement,
    load_dimension_cut,
    placement_for_new,
    resolve_placement,
    to_placement,
)

__all__ = [
    # actions
    "OPS",
    "OpSpec",
    "Action",
    "CreateNode",
    "Rename",
    "UpdateDescription",
    "AddSurface",
    "RemoveSurface",
    "Move",
    "InsertAbove",
    "DemoteToVariant",
    "RemoveNode",
    "MarkIgnore",
    "Decision",
    "Outcome",
    "ActionStatus",
    "AppliedAction",
    "Provenance",
    "DecisionRecord",
    # apply
    "apply_decision",
    "ApplyResult",
    "DecisionDiff",
    "DecisionLog",
    "read_decisions",
    "diff_snapshots",
    "content_hash",
    "next_version",
    "write_snapshot",
    "suggest_node_id",
    # placement
    "Placement",
    "to_placement",
    "placement_for_new",
    "resolve_placement",
    "load_dimension_cut",
    # ablation
    "ablate",
    "ablatable",
    "AblationError",
]
