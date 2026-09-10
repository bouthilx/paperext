"""The decision payload: what the agent is shown for one name (WS-D D1b-2, #52).

A **pure function** of (ontology, item, candidates) -> :class:`Payload`, plus a
deterministic renderer. Nothing here calls a model, reads config, or touches the
clock: the same inputs render byte-identical text, which is the only reason
:func:`payload_hash` means anything. #53's self-consistency number compares k runs
of "the same" prompt; without a provable hash, a disagreement cannot be told apart
from a payload that quietly differed.

The payload is deliberately split in two, and the split is the cost lever. Unlike
extraction -- where the paper body dominates the input and caching saves ~3.5%
(``docs/model-cost-analysis.md``) -- almost all of a categorization prompt is
*shared*:

- :class:`Context` (system message): POLICY, ROOT MAP, TAXONOMY, ACTION SCHEMA.
  Identical for every item decided against the same tree, so it is written once
  and cached rather than re-billed per name. ~19k characters on ``models/v0``.
- :class:`Payload` (user message): the ITEM's grounding and its CANDIDATES.
  Hundreds of characters.

**The leak that must not happen.** Every category shown -- a candidate's, and every
co-occurring entity's -- is resolved against the *injected* ``onto``, never against
a map cached from pristine ``v0``. Under #53's leave-one-out protocol the injected
tree has the item ablated out of it, so a paper that mentions the held-out model
twice, or mentions it beside itself, must not get its answer handed back annotated.
A global cache would produce numbers that look fine and mean nothing;
``tests/categorize/test_prompt.py::test_no_leak_*`` is the guard.
"""

from __future__ import annotations

import hashlib
from typing import Any, Iterable, Sequence

from pydantic import BaseModel, Field

from paperext.analysis.rollup import Cut, str_normalize
from paperext.categorize.actions import OPS
from paperext.categorize.candidates import (
    DEFAULT_LIMIT,
    DEFAULT_SKELETON_DEPTH,
    Candidate,
    generate,
    normalized_keys,
    skeleton_ids,
)
from paperext.categorize.items import Item, Mention
from paperext.categorize.placement import (
    load_dimension_cut,
    normalize_cut,
    to_placement,
)
from paperext.ontology.ontology import Ontology

#: Longest quote rendered per mention. Extraction quotes are single sentences, but
#: a runaway one must not be able to dominate a payload.
MAX_QUOTE_CHARS = 400

#: Per-op guidance. The JSON schema instructor enforces says what an op *takes*;
#: this says when to reach for it, which is the part policy cannot infer.
#: Keyed by op name and checked against :data:`OPS` at import, so adding an op to
#: the vocabulary without telling the agent what it is for fails loudly here.
OP_GUIDANCE: "dict[str, str]" = {
    "add_surface": (
        "map the name onto an existing node. This is the primary action of a "
        "mapping decision; `flag` marks it for human review."
    ),
    "create_node": (
        "the entity is real but no node means it. Give it the most specific "
        "correct parent, a long-form `name`, and a `description`."
    ),
    "insert_above": (
        "several existing nodes are siblings that need a shared parent concept "
        "that does not exist yet."
    ),
    "rename": (
        "the node's name is a bare acronym or a spelling variant. Rename to "
        "`long form (acronym)`; identity is long form + acronym + description."
    ),
    "update_description": (
        "the node has no description, or a wrong one. `v0` has none at all, so "
        "writing one for a node you had to reason about is expected."
    ),
    "move": "the node sits under the wrong parent.",
    "demote_to_variant": (
        "the node is only a spelling of another node, not a distinct entity. "
        "Model *variants* (v2, Large, -50, -B-16) are nodes, not spellings."
    ),
    "remove_surface": "a surface maps to the wrong node.",
    "remove_node": (
        "the node is a duplicate concept with nothing under it. Destructive: "
        "prefer `demote_to_variant`."
    ),
    "mark_ignore": (
        "the name is not an entity of this dimension at all (a misextraction). "
        "Destructive: it removes the entity from every downstream count."
    ),
}

_MISSING_GUIDANCE = set(OPS) - set(OP_GUIDANCE)
if _MISSING_GUIDANCE:  # pragma: no cover - import-time contract
    raise RuntimeError(f"OP_GUIDANCE is missing ops: {sorted(_MISSING_GUIDANCE)}")

POLICY = """\
You are curating a hierarchical ontology of {plural} extracted from deep learning
research papers. You are given one extracted name at a time, the evidence the
extraction carried, and the part of the tree it might belong to. Decide where that
name belongs and emit the ordered list of edits that puts it there.

Rules, in order of precedence:

1. IDENTITY IS long form + acronym(s) + description -- never the bare string. Two
   different entities that share an acronym are two different nodes. Match on what
   the evidence says the thing *is*.
2. AMBIGUITY MEANS ABSTAIN. If the evidence does not tell you which of several
   candidates the name is, leave it unmapped: outcome `abstained`, the candidates
   you could not separate in `unresolved`, and why in `review_notes`. Never guess.
   Abstaining is a correct answer and is scored as one. Note this gates on
   *ambiguity*, not on acronym shape -- NumPy, GPT-2, SimCLR and BERT are
   unambiguous names and should be mapped.
3. GRANULARITY. A distinct *variant* -- a version, size or qualifier (v2, v3,
   Large, -50, -B-16, -S-101) -- is its own NODE, nested under the family it
   belongs to. Only a different *spelling* of the same thing (`mobilenet-v2`,
   `MobileNet v2`) is a SURFACE. When in doubt: would a reader consider these two
   different models? Then they are nodes.
4. FIX WHAT YOU SEE, in the same decision. If the node you are mapping onto is
   named with a bare acronym, rename it. If it has no description, write one. If
   it is misplaced, move it. Set a low `confidence` on any structural fix you are
   not sure of; it will be reviewed rather than applied blindly.
5. PREFER THE MOST SPECIFIC CORRECT PLACEMENT. Counting is hierarchical, so a node
   also counts toward every ancestor. Placing one level too high loses detail;
   placing under the wrong branch is an error.
6. CREATE RATHER THAN FORCE. If nothing in CANDIDATES is the entity, create a node
   under the best parent in the TAXONOMY. Most names are not in the tree yet; a
   new node under the right parent is a good outcome, a wrong mapping is not.

Every action needs a `justification` grounded in the evidence or the tree, and a
`confidence` in [0, 1]. Answer only about the ITEM.\
"""

#: Human-readable plural per dimension, for the policy header.
_PLURALS = {
    "models": "machine-learning models",
    "datasets": "datasets",
    "libraries": "deep learning libraries",
    "domains": "research fields and application domains",
}


class NodeView(BaseModel):
    """A node as the taxonomy section shows it."""

    id: str
    name: str
    depth: int
    n_children: int = 0


class CandidateView(BaseModel):
    """A node as the candidates section shows it, with its retrieval evidence."""

    id: str
    name: str
    path: "list[str]" = Field(default_factory=list)
    cut_category: "str | None" = None
    children: "list[str]" = Field(default_factory=list)
    surfaces: "list[str]" = Field(default_factory=list)
    examples: "list[str]" = Field(default_factory=list)
    description: str = ""
    score: float = 0.0
    stage: str = ""
    matched: str = ""
    n_children: int = 0


class CoOccurrence(BaseModel):
    """A same-paper entity, annotated from the **injected** ontology."""

    name: str
    node_id: "str | None" = None
    cut_category: "str | None" = None


class EvidenceView(BaseModel):
    """One paper's grounding for the item."""

    paper: str
    spelling: str
    quote: str = ""
    justification: str = ""
    research_field: str = ""
    is_contributed: "bool | None" = None
    is_executed: "bool | None" = None
    is_compared: "bool | None" = None
    execution_mode: "str | None" = None
    role: "str | None" = None
    alongside: "list[CoOccurrence]" = Field(default_factory=list)


class Context(BaseModel):
    """The shared half of the prompt: everything that does not depend on the item."""

    dimension: str
    base_version: str
    base_content_hash: str = ""
    roots: "list[NodeView]" = Field(default_factory=list)
    drop_roots: "list[str]" = Field(default_factory=list)
    taxonomy: "list[NodeView]" = Field(default_factory=list)
    skeleton_depth: int = DEFAULT_SKELETON_DEPTH


class Payload(BaseModel):
    """The per-item half of the prompt."""

    dimension: str
    surface: str
    name: str
    spellings: "list[str]" = Field(default_factory=list)
    aliases: "list[str]" = Field(default_factory=list)
    n_mentions: int = 0
    n_papers: int = 0
    evidence: "list[EvidenceView]" = Field(default_factory=list)
    candidates: "list[CandidateView]" = Field(default_factory=list)
    #: Candidates found before the limit was applied, so a truncated payload says
    #: so instead of silently looking like a thin neighbourhood.
    n_candidates_found: int = 0


# --------------------------------------------------------------------------- #
# Building
# --------------------------------------------------------------------------- #


def build_context(
    onto: Ontology,
    dimension: str,
    *,
    skeleton_depth: int = DEFAULT_SKELETON_DEPTH,
    drop_roots: Iterable[str] = ("ignore",),
    base_content_hash: str = "",
) -> Context:
    """The shared prefix for a run against *onto*.

    Rebuilt whenever the tree changes -- which, in an accumulating run, is after
    any decision that adds a branch node. Cheap: one DFS.
    """
    ids = skeleton_ids(onto, max_depth=skeleton_depth)
    taxonomy = [
        NodeView(
            id=node_id,
            name=onto.name(node_id),
            depth=len(raw_path),
            n_children=len(onto.children(node_id)),
        )
        for node_id, _, raw_path in onto.iter_nodes()
        if node_id in ids
    ]
    return Context(
        dimension=dimension,
        base_version=onto.doc.meta.version,
        base_content_hash=base_content_hash,
        roots=[
            NodeView(id=rid, name=name, depth=1, n_children=len(onto.children(rid)))
            for rid, name in onto.root_map().items()
        ],
        drop_roots=[str(r) for r in drop_roots],
        taxonomy=taxonomy,
        skeleton_depth=skeleton_depth,
    )


def _annotate(onto: Ontology, name: str, cut: Any) -> CoOccurrence:
    """Resolve one co-occurring name **against the injected ontology**.

    The whole leak-avoidance rule is this one function being called per item
    rather than a dict built once per run.
    """
    node_id = onto.resolve(name)
    if node_id is None or node_id not in onto:
        return CoOccurrence(name=name)
    return CoOccurrence(
        name=name,
        node_id=node_id,
        cut_category=to_placement(onto, node_id, cut).cut_category,
    )


def _evidence(onto: Ontology, item: Item, mention: Mention, cut: Any) -> EvidenceView:
    own = {item.surface, *(str_normalize(a) for a in item.aliases)}
    alongside = [
        _annotate(onto, name, cut)
        for name in mention.co_occurring
        if str_normalize(name) not in own
    ]
    return EvidenceView(
        paper=mention.paper,
        spelling=mention.spelling,
        quote=mention.quote[:MAX_QUOTE_CHARS],
        justification=mention.justification,
        research_field=mention.research_field,
        is_contributed=mention.is_contributed,
        is_executed=mention.is_executed,
        is_compared=mention.is_compared,
        execution_mode=mention.execution_mode,
        role=mention.role,
        alongside=alongside,
    )


def _candidate_view(onto: Ontology, cand: Candidate, cut: Any) -> CandidateView:
    node = onto.node(cand.node_id)
    children = onto.children(cand.node_id)
    return CandidateView(
        id=cand.node_id,
        name=node.name,
        path=[onto.name(a) for a in onto.ancestry(cand.node_id)],
        cut_category=to_placement(onto, cand.node_id, cut).cut_category,
        children=[onto.name(c) for c in children[:8]],
        n_children=len(children),
        surfaces=onto.surfaces(cand.node_id),
        examples=list(node.examples)[:5],
        description=node.description or "",
        score=cand.score,
        stage=cand.stage,
        matched=cand.key,
    )


def build_payload(
    onto: Ontology,
    item: Item,
    *,
    cut: "Cut | None" = None,
    limit: int = DEFAULT_LIMIT,
    keys: "dict[str, list[str]] | None" = None,
    candidates: "Sequence[Candidate] | None" = None,
) -> Payload:
    """Everything shown for *item*, resolved against *onto* and nothing else.

    *candidates* may be supplied to reuse a ranked list (or, in tests, to pin one);
    otherwise :func:`~paperext.categorize.candidates.generate` is run over the
    item's name and aliases.
    """
    cut = load_dimension_cut(item.dimension) if cut is None else cut
    normalized = normalize_cut(cut)
    ranked = (
        generate(onto, item.name, aliases=item.aliases, limit=None, keys=keys)
        if candidates is None
        else list(candidates)
    )
    found = ranked[:limit]

    return Payload(
        dimension=item.dimension,
        surface=item.surface,
        name=item.name,
        spellings=item.spellings,
        aliases=item.aliases,
        n_mentions=item.n_mentions,
        n_papers=item.n_papers,
        evidence=[_evidence(onto, item, m, normalized) for m in item.mentions],
        candidates=[_candidate_view(onto, c, normalized) for c in found],
        n_candidates_found=len(ranked),
    )


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def _bullets(values: "Sequence[str]", empty: str = "(none)") -> str:
    return ", ".join(values) if values else empty


def _flags(ev: EvidenceView) -> str:
    """The boolean grounding, omitting what the record does not actually say."""
    parts = []
    for label, value in (
        ("contributed", ev.is_contributed),
        ("executed", ev.is_executed),
        ("compared", ev.is_compared),
    ):
        if value is not None:
            parts.append(f"{label}={'yes' if value else 'no'}")
    if ev.execution_mode:
        parts.append(f"execution={ev.execution_mode}")
    if ev.role:
        parts.append(f"role={ev.role}")
    return "; ".join(parts)


def render_action_schema() -> str:
    """The op table, generated from :data:`OPS` so it cannot drift from what the
    applier will accept."""
    lines = ["## ACTION SCHEMA", ""]
    lines.append(
        "Each action names one `op` and its arguments. Node arguments must be node "
        "`id`s from this payload -- except ids you create earlier in the same "
        "decision, which later actions may reference."
    )
    lines.append("")
    for op in sorted(OPS):
        spec = OPS[op]
        args = list(spec.positional) + [f"{name}=" for name in spec.optional]
        marker = " [destructive]" if spec.dangerous else ""
        lines.append(f"- `{op}({', '.join(args)})`{marker} -- {OP_GUIDANCE[op]}")
    lines.append("")
    lines.append(
        "Set `outcome` to `mapped` (surface added to an existing node), `created` "
        "(node created and mapped), `abstained` (ambiguous -- no mapping), `no_op` "
        "(already correct) or `failed`."
    )
    return "\n".join(lines)


def render_context(ctx: Context) -> str:
    """The shared prefix, as sent. Stable across items of a run -- that stability
    is what makes it cacheable, so do not put per-item text in here."""
    plural = _PLURALS.get(ctx.dimension, ctx.dimension)
    drop = {str_normalize(r) for r in ctx.drop_roots}

    lines = [POLICY.format(plural=plural), "", "## ROOT MAP", ""]
    for root in ctx.roots:
        note = (
            "  <- misextractions; nothing real belongs here"
            if str_normalize(root.name) in drop
            else ""
        )
        lines.append(f"- `{root.id}` {root.name} (children: {root.n_children}){note}")

    lines += [
        "",
        "## TAXONOMY",
        "",
        f"Every branch of the tree, plus every node down to depth "
        f"{ctx.skeleton_depth}. Leaves deeper than that are not listed here -- the "
        "CANDIDATES section carries the ones relevant to this item.",
        "",
    ]
    for node in ctx.taxonomy:
        indent = "  " * (node.depth - 1)
        # "(children: 3)" rather than a bare "(3)": a digit sitting right after a
        # name reads as part of it ("mixup (1)"), and it makes any check for "did
        # this name appear" -- the ablation leak test -- fire on the decoration.
        suffix = f" (children: {node.n_children})" if node.n_children else ""
        lines.append(f"{indent}- `{node.id}` {node.name}{suffix}")

    lines += ["", render_action_schema()]
    return "\n".join(lines)


def render_evidence(payload: Payload, *, annotate: bool = True) -> "list[str]":
    """The ITEM + EVIDENCE lines, shared with the #53 blind adjudicator.

    With ``annotate=False`` the co-occurring entities render as bare names. The
    adjudicator compares two placements without being told which is the legacy
    one, and showing it where the *current* tree puts the neighbours would hand
    the reference a free hint.
    """
    lines = ["## ITEM", ""]
    lines.append(f"name: {payload.name}")
    lines.append(f"normalized: {payload.surface}")
    if len(payload.spellings) > 1:
        lines.append(f"also spelled: {_bullets(payload.spellings[1:])}")
    if payload.aliases:
        lines.append(f"aliases in papers: {_bullets(payload.aliases)}")
    lines.append(
        f"seen: {payload.n_mentions} mention(s) in {payload.n_papers} paper(s)"
    )

    lines += ["", "## EVIDENCE", ""]
    if not payload.evidence:
        lines.append("(none -- the extraction carried no supporting text)")
    for ev in payload.evidence:
        lines.append(f'- paper {ev.paper} (as "{ev.spelling}")')
        if ev.research_field:
            lines.append(f"  field: {ev.research_field}")
        if ev.quote:
            lines.append(f'  quote: "{ev.quote}"')
        if ev.justification:
            lines.append(f"  extractor's reason: {ev.justification}")
        flags = _flags(ev)
        if flags:
            lines.append(f"  {flags}")
        if ev.alongside:
            lines.append("  alongside in the same paper:")
            for co in ev.alongside:
                if not annotate:
                    lines.append(f"    - {co.name}")
                    continue
                where = (
                    f"-> `{co.node_id}` [{co.cut_category or 'no category'}]"
                    if co.node_id
                    else "-> not in the tree"
                )
                lines.append(f"    - {co.name} {where}")
    return lines


def render_payload(payload: Payload) -> str:
    """The per-item half, as sent."""
    lines = render_evidence(payload)

    lines += ["", "## CANDIDATES", ""]
    if not payload.candidates:
        lines.append(
            "(none -- nothing in the tree resembles this name. That is normal: "
            "place it in the TAXONOMY by meaning, not by spelling.)"
        )
    elif payload.n_candidates_found > len(payload.candidates):
        lines.append(
            f"Top {len(payload.candidates)} of {payload.n_candidates_found} "
            "matches, best first."
        )
        lines.append("")
    for cand in payload.candidates:
        # The acronym stage's key is the candidate's *own* initials, derived from
        # the query -- redundant next to the name, and echoing it would put the
        # queried string inside CANDIDATES, which the ablation leak test (rightly)
        # reads as the held-out name escaping the ITEM block.
        how = (
            cand.stage
            if cand.stage == "acronym"
            else f'{cand.stage} on "{cand.matched}"'
        )
        lines.append(f"- `{cand.id}` {cand.name} (match: {how}, {cand.score:.2f})")
        lines.append(f"  path: {' > '.join(cand.path)}")
        lines.append(f"  rolls up to: {cand.cut_category or 'no category'}")
        if cand.description:
            lines.append(f"  description: {cand.description}")
        if cand.surfaces:
            lines.append(f"  surfaces: {_bullets(cand.surfaces)}")
        if cand.children:
            more = (
                f" (+{cand.n_children - len(cand.children)} more)"
                if cand.n_children > len(cand.children)
                else ""
            )
            lines.append(f"  children: {_bullets(cand.children)}{more}")
        if cand.examples:
            lines.append(f"  examples: {_bullets(cand.examples)}")

    lines += [
        "",
        "## TASK",
        "",
        f'Decide where "{payload.name}" belongs and emit the actions that put it '
        "there.",
    ]
    return "\n".join(lines)


def build_messages(ctx: Context, payload: Payload) -> "list[dict[str, str]]":
    """The message list handed to the backend: shared system, per-item user."""
    return [
        {"role": "system", "content": render_context(ctx)},
        {"role": "user", "content": render_payload(payload)},
    ]


def payload_hash(ctx: Context, payload: Payload) -> str:
    """sha256 of exactly what is sent.

    Over the *rendered* text rather than the models, because the rendered text is
    what the model sees: a change to the renderer that leaves the payload objects
    identical still changes the answer, and must change the hash.
    """
    digest = hashlib.sha256()
    for message in build_messages(ctx, payload):
        digest.update(message["role"].encode())
        digest.update(b"\0")
        digest.update(message["content"].encode())
        digest.update(b"\0")
    return digest.hexdigest()
