"""The action vocabulary and its contract with the mutation API (D1b-1, #51).

The point of these tests is the **anti-drift** guarantee: :data:`OPS` claims to be
the single source of truth for the op vocabulary, so it is checked against the
live :class:`~paperext.ontology.Ontology` signatures and against the pydantic
models, rather than being trusted.
"""

import inspect
from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from paperext.categorize.actions import (
    ACTION_MODELS,
    OPS,
    Action,
    AddSurface,
    CreateNode,
    Decision,
    Outcome,
)
from paperext.ontology import Ontology

ADAPTER: TypeAdapter[Any] = TypeAdapter(Action)


# --------------------------------------------------------------------------- #
# The table matches the mutation API it claims to describe
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("op", sorted(OPS))
def test_op_matches_ontology_signature(op):
    """Arg names and their positional/keyword split come from the real method."""
    spec = OPS[op]
    signature = inspect.signature(getattr(Ontology, spec.method))
    params = [p for name, p in signature.parameters.items() if name != "self"]

    positional = [
        p.name for p in params if p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    ]
    keyword = [p.name for p in params if p.kind is inspect.Parameter.KEYWORD_ONLY]

    assert list(spec.positional) == positional, op
    assert list(spec.optional) == keyword, op


@pytest.mark.parametrize("op", sorted(OPS))
def test_action_model_carries_every_arg(op):
    """Every arg the applier will read off an action exists on its model."""
    spec = OPS[op]
    fields = set(ACTION_MODELS[op].model_fields)
    assert set(spec.positional) <= fields, op
    assert set(spec.optional) <= fields, op
    assert spec.noderefs <= fields, op
    assert spec.creates <= fields, op


def test_every_mutation_op_has_an_action():
    """The vocabulary covers the whole D1a-2 mutation API and nothing else."""
    mutators = {
        name
        for name, member in vars(Ontology).items()
        if callable(member)
        and not name.startswith("_")
        and name
        not in {
            "load",
            "save",
            "node",
            "name",
            "children",
            "parents",
            "examples",
            "surfaces",
            "root_map",
            "ancestry",
            "root_of",
            "iter_nodes",
            "resolve",
            "search",
            "check_invariants",
        }
    }
    assert {spec.method for spec in OPS.values()} == mutators
    assert set(ACTION_MODELS) == set(OPS)


# --------------------------------------------------------------------------- #
# Schema behaviour
# --------------------------------------------------------------------------- #


def test_discriminated_union_picks_the_right_model():
    action = ADAPTER.validate_python(
        {
            "op": "add_surface",
            "justification": "spelling variant",
            "confidence": 0.9,
            "surface": "ResNet-50",
            "canonical": "resnet",
        }
    )
    assert isinstance(action, AddSurface)
    assert action.via == "agent" and action.flag is None


def test_flag_is_wired():
    """``add_surface``'s ``flag`` is how a low-confidence row gets marked."""
    assert "flag" in OPS["add_surface"].optional
    action = AddSurface(
        justification="ambiguous",
        confidence=0.4,
        surface="sam",
        canonical="sam",
        flag="ambiguous",
    )
    assert action.flag == "ambiguous"


def test_unknown_op_is_a_validation_error_not_a_crash():
    with pytest.raises(ValidationError, match="union_tag_invalid|discriminator"):
        ADAPTER.validate_python(
            {"op": "drop_database", "justification": "x", "confidence": 1.0}
        )


def test_malformed_args_are_a_validation_error():
    with pytest.raises(ValidationError):
        ADAPTER.validate_python(
            {"op": "move", "justification": "x", "confidence": 1.0, "node_id": "a"}
        )  # missing new_parent


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_confidence_is_a_bounded_float(confidence):
    with pytest.raises(ValidationError):
        CreateNode(justification="x", confidence=confidence, node_id="a", name="A")


def test_reason_comes_before_the_values_it_justifies():
    """Mirrors ``Explained[T]`` (``mdl/model_v4.py:65-80``)."""
    order = list(CreateNode.model_fields)
    assert order[:2] == ["justification", "confidence"]
    assert order.index("op") < order.index("node_id")


def test_outcome_is_explicit_not_inferred():
    """An empty action list is not the same thing as an abstention."""
    no_op = Decision(surface="ppo", outcome=Outcome.NO_OP, confidence=0.9)
    abstained = Decision(
        surface="sam",
        outcome=Outcome.ABSTAINED,
        confidence=0.3,
        unresolved=["sam", "sam__2"],
        review_notes=["bare acronym; two candidates"],
    )
    assert not no_op.actions and not abstained.actions
    assert no_op.outcome is not abstained.outcome


def test_decision_round_trips_through_json():
    """#53 replays stored decisions, so the schema has to survive a round trip."""
    decision = Decision(
        surface="BiT-S-101",
        outcome=Outcome.CREATED,
        confidence=0.8,
        actions=[
            CreateNode(
                justification="ResNetv2-101 backbone",
                confidence=0.8,
                node_id="bits101",
                name="BiT-S-101",
                parent="cnn",
            ),
            AddSurface(
                justification="the extracted spelling",
                confidence=0.9,
                surface="BiT-S-101",
                canonical="bits101",
            ),
        ],
    )
    reloaded = Decision.model_validate_json(decision.model_dump_json())
    assert reloaded == decision
    assert isinstance(reloaded.actions[0], CreateNode)
