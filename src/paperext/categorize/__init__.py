"""LLM categorization agent for the layered ontology (WS-D D1b, #44).

Sits on top of :mod:`paperext.ontology` (the pure data model from D1a) and adds
the *decision* layer: what a name maps to, whether a node must be created, and
which in-flight fixes the tree needs.

D1b-1 (#51) is the **deterministic half** — the action vocabulary, the
transactional applier, and the eval scaffolding. D1b-2 (#52) adds retrieval
(:mod:`~paperext.categorize.candidates`), the corpus fold
(:mod:`~paperext.categorize.items`) and the payload
(:mod:`~paperext.categorize.prompt`) — all still API-free and pure. Only
:mod:`~paperext.categorize.agent` imports ``instructor`` and
:mod:`paperext.backends`, and it is deliberately not re-exported here so that
importing this package never pulls in a provider SDK. The eval harness is D1b-3
(#53).

Layers::

    query JSONs       -> [items]      -> Item(surface, name, mentions)
    Item + Ontology   -> [candidates] -> ranked Candidate list
    Item + candidates -> [prompt]     -> Context (shared) + Payload (per item)
    payload           -> [agent]      -> Decision(actions=[Action, ...])
    Decision          -> [apply]      -> mutated Ontology + DecisionRecord
    DecisionRecord    -> decisions.jsonl (append-only audit + replay input)
"""

from paperext.categorize.ablate import (
    AblationError,
    ablatable,
    ablate,
    residual_names,
)
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
from paperext.categorize.candidates import (
    Candidate,
    anchor_ids,
    generate,
    normalized_keys,
    skeleton_ids,
)
from paperext.categorize.items import (
    Item,
    Mention,
    build_items,
    read_items,
    write_items,
)
from paperext.categorize.placement import (
    Placement,
    load_dimension_cut,
    placement_for_new,
    resolve_placement,
    to_placement,
)
from paperext.categorize.prompt import (
    CandidateView,
    Context,
    CoOccurrence,
    EvidenceView,
    NodeView,
    Payload,
    build_context,
    build_messages,
    build_payload,
    payload_hash,
    render_context,
    render_payload,
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
    # candidates (D1b-2)
    "Candidate",
    "generate",
    "anchor_ids",
    "skeleton_ids",
    "normalized_keys",
    # items (D1b-2)
    "Item",
    "Mention",
    "build_items",
    "read_items",
    "write_items",
    # prompt (D1b-2)
    "Context",
    "Payload",
    "NodeView",
    "CandidateView",
    "CoOccurrence",
    "EvidenceView",
    "build_context",
    "build_payload",
    "build_messages",
    "render_context",
    "render_payload",
    "payload_hash",
    # ablation
    "ablate",
    "ablatable",
    "AblationError",
    "residual_names",
]
