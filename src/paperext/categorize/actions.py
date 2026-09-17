"""The action vocabulary the categorization agent emits (WS-D D1b-1, #51).

One extracted name in, one :class:`Decision` out. A decision is an *ordered* list
of :class:`Action` s over the D1a-2 mutation API (#42): the primary mapping
(``add_surface``, or ``create_node`` when nothing fits) plus any in-flight cleanup
the agent noticed — renaming a bare-acronym node, moving a misplaced one, demoting
a spelling variant.

Three things in here are load-bearing beyond D1b-1, and all of them exist because
#53 **replays stored decisions**: a schema change later invalidates recorded (and
paid-for) runs.

- ``confidence`` is a **float in [0, 1]**, per action *and* per decision. A string
  or a three-level enum makes the risk-coverage curve in #53 impossible to draw.
- ``outcome`` is an **explicit enum**, never inferred from ``len(actions) == 0``:
  "abstained", "correctly did nothing" and "the response failed to parse" are
  three different things, and the coverage / abstention / no-op metrics all
  collapse if they are conflated.
- :class:`Provenance` and the resolved placement (:mod:`paperext.categorize.placement`)
  ship now even though nothing consumes them until #53.

:data:`OPS` is the **single source of truth** for the op vocabulary — op name,
:class:`~paperext.ontology.Ontology` method, argument order, and which arguments
must (or must not) name an existing node. The applier reads arguments off an
action *through* this table, ``scripts/mutate_ontology.py`` builds its CLI from
it, and ``tests/categorize/test_actions.py`` checks it against the live
:class:`~paperext.ontology.Ontology` signatures — so the schema, the applier and
the dev harness cannot drift apart.

Field order follows the repo's **reason-before-value** convention from
``Explained[T]`` (``structured_output/mdl/model_v4.py:65-80``): the justification
comes before the values it justifies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated, Any, Literal, Union, get_args

from pydantic import BaseModel, Field, ValidationInfo, model_validator
from pydantic.json_schema import (
    DEFAULT_REF_TEMPLATE,
    GenerateJsonSchema,
    JsonSchemaMode,
    JsonSchemaValue,
)


@dataclass(frozen=True)
class OpSpec:
    """How one op maps onto an :class:`~paperext.ontology.Ontology` method.

    ``positional`` and ``optional`` name the action fields to pass through, in
    order; ``noderefs`` are the arguments that must name an **existing** node and
    ``creates`` the ones that must **not** (a fresh id). ``dangerous`` marks the
    ops that can remove a node from the tree — #53's no-op control asserts none of
    these fire outside the candidate set.
    """

    op: str
    method: str
    positional: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()
    noderefs: frozenset[str] = field(default_factory=frozenset)
    creates: frozenset[str] = field(default_factory=frozenset)
    dangerous: bool = False


#: op name -> spec. Op names are the ``Ontology`` method names, so there is one
#: vocabulary rather than a CLI spelling and an API spelling.
OPS: dict[str, OpSpec] = {
    spec.op: spec
    for spec in (
        OpSpec(
            op="create_node",
            method="create_node",
            positional=("node_id", "name"),
            optional=("parent", "description", "examples"),
            noderefs=frozenset({"parent"}),
            creates=frozenset({"node_id"}),
        ),
        OpSpec(
            op="rename",
            method="rename",
            positional=("node_id", "new_name"),
            noderefs=frozenset({"node_id"}),
        ),
        OpSpec(
            op="update_description",
            method="update_description",
            positional=("node_id", "description"),
            noderefs=frozenset({"node_id"}),
        ),
        OpSpec(
            op="add_surface",
            method="add_surface",
            positional=("surface", "canonical"),
            optional=("via", "flag"),
            noderefs=frozenset({"canonical"}),
        ),
        OpSpec(
            op="remove_surface",
            method="remove_surface",
            positional=("surface",),
        ),
        OpSpec(
            op="move",
            method="move",
            positional=("node_id", "new_parent"),
            noderefs=frozenset({"node_id", "new_parent"}),
        ),
        OpSpec(
            op="insert_above",
            method="insert_above",
            positional=("node_id", "new_id", "name"),
            optional=("description", "examples"),
            noderefs=frozenset({"node_id"}),
            creates=frozenset({"new_id"}),
        ),
        OpSpec(
            op="demote_to_variant",
            method="demote_to_variant",
            positional=("node_id", "target_id"),
            noderefs=frozenset({"node_id", "target_id"}),
            dangerous=True,
        ),
        OpSpec(
            op="remove_node",
            method="remove_node",
            positional=("node_id",),
            noderefs=frozenset({"node_id"}),
            dangerous=True,
        ),
        OpSpec(
            op="mark_ignore",
            method="mark_ignore",
            positional=("node_id",),
            noderefs=frozenset({"node_id"}),
            dangerous=True,
        ),
    )
}


# --------------------------------------------------------------------------- #
# Actions
# --------------------------------------------------------------------------- #


class _ActionBase(BaseModel):
    """Reason first, then the op and its arguments."""

    justification: str = Field(
        description="Why this edit is the right one, grounded in the item evidence",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in this edit, 0.0 (guess) to 1.0 (certain)",
    )


class CreateNode(_ActionBase):
    """Add a new concept, under *parent* or as a new root."""

    op: Literal["create_node"] = "create_node"
    node_id: str = Field(description="New, unused node id (normalized name slug)")
    name: str = Field(description="Display name: long form, acronym in parentheses")
    parent: str | None = Field(
        default=None, description="Existing node id to nest under; null for a root"
    )
    description: str = ""
    examples: list[str] = Field(default_factory=list)


class Rename(_ActionBase):
    """Change a node's display name (does not touch its surfaces)."""

    op: Literal["rename"] = "rename"
    node_id: str
    new_name: str


class UpdateDescription(_ActionBase):
    """Set a node's description — ``v0`` has none, so D1b bootstraps them."""

    op: Literal["update_description"] = "update_description"
    node_id: str
    description: str


class AddSurface(_ActionBase):
    """Map a surface form to a canonical node (normalized, strictly 1:1)."""

    op: Literal["add_surface"] = "add_surface"
    surface: str
    canonical: str
    via: str = "agent"
    flag: str | None = Field(
        default=None,
        description="Mark the row for review, e.g. 'low-confidence' or 'ambiguous'",
    )


class RemoveSurface(_ActionBase):
    """Drop a surface -> canonical row."""

    op: Literal["remove_surface"] = "remove_surface"
    surface: str


class Move(_ActionBase):
    """Re-parent a node (an in-flight fix for a misplaced concept)."""

    op: Literal["move"] = "move"
    node_id: str
    new_parent: str


class InsertAbove(_ActionBase):
    """Insert a new parent between a node and its current parent."""

    op: Literal["insert_above"] = "insert_above"
    node_id: str
    new_id: str
    name: str
    description: str = ""
    examples: list[str] = Field(default_factory=list)


class DemoteToVariant(_ActionBase):
    """Fold a leaf node into another as normalization surface(s)."""

    op: Literal["demote_to_variant"] = "demote_to_variant"
    node_id: str
    target_id: str


class RemoveNode(_ActionBase):
    """Delete a childless node and cascade-drop its surface rows."""

    op: Literal["remove_node"] = "remove_node"
    node_id: str


class MarkIgnore(_ActionBase):
    """Move a node under the reserved ``ignore`` root (drops it from roll-up)."""

    op: Literal["mark_ignore"] = "mark_ignore"
    node_id: str


#: Discriminated on ``op`` so a malformed action is a pydantic validation error
#: naming the op, not a crash inside the applier.
Action = Annotated[
    Union[
        CreateNode,
        Rename,
        UpdateDescription,
        AddSurface,
        RemoveSurface,
        Move,
        InsertAbove,
        DemoteToVariant,
        RemoveNode,
        MarkIgnore,
    ],
    Field(discriminator="op"),
]

#: op name -> action model, derived from the union so it cannot drift.
ACTION_MODELS: dict[str, type[_ActionBase]] = {
    model.model_fields["op"].default: model for model in get_args(get_args(Action)[0])
}


# --------------------------------------------------------------------------- #
# Decisions
# --------------------------------------------------------------------------- #


class Outcome(str, Enum):
    """What the agent concluded — explicit, never inferred from the action list.

    ``mapped``    the surface now resolves to an existing node
    ``created``   a new node was created and the surface points at it
    ``abstained`` genuinely ambiguous; left unmapped on purpose, with a note
    ``no_op``     already correct; nothing to change
    ``failed``    the response could not be parsed or validated
    """

    MAPPED = "mapped"
    CREATED = "created"
    ABSTAINED = "abstained"
    NO_OP = "no_op"
    FAILED = "failed"


class StrictJsonSchema(GenerateJsonSchema):
    """JSON schema in the subset OpenAI's strict structured outputs accept.

    Pydantic renders a discriminated union as ``oneOf`` plus a ``discriminator``
    block, and OpenAI rejects both (``'oneOf' is not permitted``). ``anyOf`` is
    accepted and, with disjoint ``op`` literals, means the same thing. ``default``
    goes too: strict mode marks every property required, so a default is noise
    on the wire. Validation is unaffected -- the discriminator still drives
    :meth:`Decision.model_validate`; only the *rendered* schema changes.
    """

    def tagged_union_schema(self, schema: Any) -> JsonSchemaValue:
        rendered = super().tagged_union_schema(schema)
        if "oneOf" in rendered:
            rendered["anyOf"] = rendered.pop("oneOf")
        rendered.pop("discriminator", None)
        return rendered

    def default_schema(self, schema: Any) -> JsonSchemaValue:
        rendered = super().default_schema(schema)
        rendered.pop("default", None)
        return rendered


class StrictSchemaModel(BaseModel):
    """Base for every model handed to a provider as a response schema.

    Only the rendered schema differs from :class:`pydantic.BaseModel`;
    ``instructor`` calls :meth:`model_json_schema` and gets the strict-compatible
    form.
    """

    @classmethod
    def model_json_schema(  # type: ignore[override]
        cls,
        by_alias: bool = True,
        ref_template: str = DEFAULT_REF_TEMPLATE,
        schema_generator: "type[GenerateJsonSchema]" = StrictJsonSchema,
        mode: JsonSchemaMode = "validation",
    ) -> "dict[str, Any]":
        return super().model_json_schema(
            by_alias=by_alias,
            ref_template=ref_template,
            schema_generator=schema_generator,
            mode=mode,
        )


class Decision(StrictSchemaModel):
    """One extracted name, one ordered list of edits."""

    reasoning: str = Field(
        default="",
        description="Your analysis, before anything else: what the evidence says "
        "this entity is, which candidates you considered, and why you chose or "
        "rejected each. A reviewer reads this to follow the decision.",
    )
    surface: str = Field(description="The extracted name this decision is about")
    review_notes: list[str] = Field(
        default_factory=list,
        description="Anything a human should look at: ambiguity, a low-confidence "
        "structural fix, a suspected duplicate elsewhere in the tree",
    )
    unresolved: list[str] = Field(
        default_factory=list,
        description="Candidate node ids that could not be told apart; the reason "
        "an 'abstained' outcome abstained. Empty otherwise.",
    )
    outcome: Outcome
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in the decision as a whole"
    )
    actions: list[Action] = Field(
        default_factory=list, description="Edits to apply, in order"
    )

    def mapping_target(self) -> str | None:
        """The node id this decision's own surface ends up pointing at, if any.

        The last ``add_surface`` naming the surface wins; a ``demote_to_variant``
        of the node the surface *is* maps it too (the fold transfers the name).
        ``None`` when no action maps the surface.
        """
        from paperext.analysis.rollup import str_normalize

        want = str_normalize(self.surface)
        target: str | None = None
        for action in self.actions:
            if isinstance(action, AddSurface) and str_normalize(action.surface) == want:
                target = action.canonical
            elif isinstance(action, DemoteToVariant) and action.node_id == want:
                target = action.target_id
        return target

    def implied_outcome(self) -> Outcome | None:
        """What the actions say happened to the surface: ``mapped``, ``created``,
        or ``None`` when nothing maps it (a no-op, an abstention, or pure fixes)."""
        target = self.mapping_target()
        if target is None:
            return None
        created = {
            a.node_id if isinstance(a, CreateNode) else a.new_id
            for a in self.actions
            if isinstance(a, (CreateNode, InsertAbove))
        }
        return Outcome.CREATED if target in created else Outcome.MAPPED

    @model_validator(mode="after")
    def _outcome_matches_actions(self, info: ValidationInfo) -> "Decision":
        """``outcome`` is a claim about the actions; hold it to them (#67).

        Left unchecked, a model that finds the surface already mapped says
        ``mapped`` with no ``add_surface`` -- true in spirit, but then nothing
        records where the name sits. ``instructor`` retries on this error, so the
        message says which outcome the actions do support. ``failed`` is the
        runner's own label and is not checked, and neither is a decision read
        back from disk (``context={"recorded": True}``): the log says what the
        run did, including runs from before this check.
        """
        if self.outcome == Outcome.FAILED or (info.context or {}).get("recorded"):
            return self
        implied = self.implied_outcome()
        if self.outcome in (Outcome.MAPPED, Outcome.CREATED):
            if implied is None:
                raise ValueError(
                    f"outcome '{self.outcome.value}' but no action maps the surface "
                    f"{self.surface!r} (add_surface naming it; for 'created', "
                    "pointing at a node this decision creates). If it already "
                    "resolves to the right node, the outcome is 'no_op'"
                )
            if implied != self.outcome:
                raise ValueError(
                    f"outcome '{self.outcome.value}' but the actions make it "
                    f"'{implied.value}': the surface points at {self.mapping_target()!r}"
                )
        elif implied is not None:
            raise ValueError(
                f"outcome '{self.outcome.value}' but an action maps the surface to "
                f"{self.mapping_target()!r}; that is '{implied.value}'"
            )
        return self


class ActionStatus(str, Enum):
    """Per-action fate within a decision's transaction.

    A decision is all-or-nothing, so a failure turns the actions *before* it into
    ``rolled_back`` and the ones after it into ``skipped``. Keeping the three
    apart is what lets #53 attribute an apply failure to a specific op.
    """

    APPLIED = "applied"
    DRY_RUN = "dry_run"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


class AppliedAction(BaseModel):
    """What actually happened to one action."""

    index: int
    op: str
    status: ActionStatus
    error: str | None = None


class Provenance(BaseModel):
    """Enough to replay a decision and to prove the run was genuinely ablated.

    ``base_content_hash`` pins the exact tree the decision was taken against —
    ``base_version`` alone is not enough once a ``v<N>`` is rewritten. #53 keys its
    adjudication verdict cache off these fields.
    """

    run_id: str
    seq: int
    dimension: str
    base_version: str
    base_content_hash: str
    payload_hash: str | None = None
    model: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    ablated: bool = False
