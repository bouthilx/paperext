"""The v5 cross-reference check: what it finds, and that it never raises."""

from __future__ import annotations

import pytest

from paperext.structured_output.mdl import model_v5
from paperext.structured_output.mdl.check import (
    EXECUTED_WITHOUT_RUN,
    EXECUTION_MODE_DISAGREES,
    GENERATE_RUN_WITH_MODELS,
    REFERENCED_BUT_NOT_EXECUTED,
    UNRESOLVED_REFERENCE,
    check_references,
)


def _expl(value):
    return {"quote": "q", "justification": "j", "value": value}


def _model(name, *, executed=True, mode="train", aliases=None):
    return {
        "name": _expl(name),
        "aliases": aliases or [],
        "is_contributed": _expl(False),
        "is_executed": _expl(executed),
        "is_compared": _expl(True),
        "execution_mode": _expl(mode),
        "referenced_paper_title": _expl(""),
    }


def _algorithm(name, *, executed=True, aliases=None):
    return {
        "name": _expl(name),
        "aliases": aliases or [],
        "is_contributed": _expl(False),
        "is_executed": _expl(executed),
        "is_compared": _expl(False),
        "paper_role": _expl("the optimiser"),
        "composed_of": [],
        "referenced_paper_title": _expl(""),
    }


def _data_source(name, *, aliases=None):
    return {
        "name": _expl(name),
        "aliases": aliases or [],
        "role": "used",
        "size": _expl("unknown"),
        "derived_from": [],
        "sample_properties": [],
        "referenced_paper_title": _expl(""),
    }


def _run(*, models=(), data_sources=(), algorithms=(), mode="train"):
    return {
        "models": [{"name": n, "role_in_run": "main"} for n in models],
        "data_sources": [
            {"name": n, "access": "fixed", "roles_in_run": ["train"]}
            for n in data_sources
        ],
        "algorithms": [{"name": n} for n in algorithms],
        "produces": [],
        "execution_mode": _expl(mode),
        "epochs": _expl("unknown"),
        "parameter_count": _expl("unknown"),
        "accelerator_type": _expl("unknown"),
        "accelerator_model": _expl("unknown"),
        "accelerator_count": _expl("unknown"),
        "precision": _expl("unknown"),
        "parallelism": _expl(["unknown"]),
        "duration": _expl("unknown"),
        "utilisation": _expl("unknown"),
        "repetitions": _expl("unknown"),
    }


def _paper(*, models=(), data_sources=(), algorithms=(), runs=()):
    return model_v5.PaperExtractions.model_validate(
        {
            "title": _expl("t"),
            "description": "d",
            "type": _expl("empirical"),
            "research_fields": [{"name": _expl("x"), "aliases": [], "role": "unknown"}],
            "models": list(models),
            "data_sources": list(data_sources),
            "libraries": [],
            "algorithms": list(algorithms),
            "runs": list(runs),
        }
    )


def _codes(extractions):
    return sorted(p.code for p in check_references(extractions))


def test_a_resolving_reference_is_not_a_problem():
    ext = _paper(
        models=[_model("ResNet-50")],
        data_sources=[_data_source("ImageNet")],
        algorithms=[_algorithm("AdamW")],
        runs=[
            _run(
                models=["ResNet-50"],
                data_sources=["ImageNet"],
                algorithms=["AdamW"],
            )
        ],
    )
    assert check_references(ext) == []


def test_an_alias_resolves_a_reference():
    """Written aliases count; a run may repeat the acronym the paper used."""
    ext = _paper(
        models=[_model("Vision Transformer", aliases=["ViT"])],
        runs=[_run(models=["ViT"])],
    )
    assert check_references(ext) == []


def test_normalization_absorbs_punctuation_and_case():
    ext = _paper(models=[_model("ResNet-50")], runs=[_run(models=["resnet 50"])])
    assert check_references(ext) == []


def test_an_unresolved_reference_is_reported_not_repaired():
    """Similarity is never used to resolve a reference.

    `gpt-j` against `GPT-4` is the pairing token matching actually produced
    during the models work; a wrong repair is worse than a reported gap.
    """
    ext = _paper(models=[_model("GPT-4")], runs=[_run(models=["GPT-J"])])
    problems = check_references(ext)
    unresolved = [p for p in problems if p.code == UNRESOLVED_REFERENCE]
    assert len(unresolved) == 1
    assert unresolved[0].where == "runs[0].models[0]"
    assert "GPT-J" in unresolved[0].detail
    # The reference resolving to nothing also leaves GPT-4 unaccounted for, so
    # the second code is correct rather than noise: the run exists but nothing
    # in it names a model the paper declared.
    assert EXECUTED_WITHOUT_RUN in _codes(ext)


def test_an_unresolved_reference_still_validates():
    """The schema must accept it -- this is the whole reason the check is here.

    Extraction runs inside an `instructor` retry loop, where a validator that
    raised on a mistyped name would discard the entire paper's extraction.
    """
    ext = _paper(models=[_model("GPT-4")], runs=[_run(models=["GPT-J"])])
    assert ext.runs[0].models[0].name == "GPT-J"
    assert check_references(ext)  # reported, not raised


@pytest.mark.parametrize("field", ["models", "data_sources", "algorithms"])
def test_every_reference_field_is_checked(field):
    ext = _paper(
        models=[_model("m")],
        data_sources=[_data_source("d")],
        algorithms=[_algorithm("a")],
        runs=[_run(**{field: ["absent"]})],
    )
    assert _codes(ext).count(UNRESOLVED_REFERENCE) == 1


def test_a_run_executing_a_non_executed_entity_is_a_contradiction():
    ext = _paper(
        models=[_model("ResNet-50", executed=False)],
        runs=[_run(models=["ResNet-50"])],
    )
    assert REFERENCED_BUT_NOT_EXECUTED in _codes(ext)


def test_execution_mode_disagreement_between_a_model_and_its_run():
    ext = _paper(
        models=[_model("ResNet-50", mode="finetune")],
        runs=[_run(models=["ResNet-50"], mode="train")],
    )
    assert EXECUTION_MODE_DISAGREES in _codes(ext)


def test_execution_mode_agreement_is_silent():
    ext = _paper(
        models=[_model("ResNet-50", mode="train")],
        runs=[_run(models=["ResNet-50"], mode="train")],
    )
    assert check_references(ext) == []


@pytest.mark.parametrize(
    "model_mode,run_mode", [("unknown", "train"), ("train", "unknown")]
)
def test_unknown_on_either_side_is_not_a_disagreement(model_mode, run_mode):
    """`unknown` is an absence of evidence, so it cannot contradict anything."""
    ext = _paper(
        models=[_model("ResNet-50", mode=model_mode)],
        runs=[_run(models=["ResNet-50"], mode=run_mode)],
    )
    assert EXECUTION_MODE_DISAGREES not in _codes(ext)


def test_an_executed_model_with_no_run_is_reported():
    ext = _paper(models=[_model("ResNet-50")])
    problems = check_references(ext)
    assert [p.code for p in problems] == [EXECUTED_WITHOUT_RUN]


def test_a_referenced_only_model_needs_no_run():
    """`is_executed` is the gate: a baseline quoted from another paper is done."""
    ext = _paper(models=[_model("ResNet-50", executed=False)])
    assert check_references(ext) == []


def test_an_empty_paper_is_clean():
    assert check_references(_paper()) == []


def test_the_paper_name_prefixes_every_location():
    ext = _paper(models=[_model("GPT-4")], runs=[_run(models=["GPT-J"])])
    assert check_references(ext, paper="2401.14487_00")[0].where.startswith(
        "2401.14487_00:"
    )


def test_a_generate_run_referencing_a_model_is_reported():
    """`generate` means the cost is not parameter-shaped.

    If a model produced the data the mode is `inference`, and the difference
    decides which compute formula applies -- so a `generate` run that names a
    model is a mode that would send the estimator to the wrong formula.
    """
    ext = _paper(
        models=[_model("ResNet-50")],
        runs=[_run(models=["ResNet-50"], mode="generate")],
    )
    assert GENERATE_RUN_WITH_MODELS in _codes(ext)


def test_a_generate_run_with_no_models_is_clean():
    """Bulk preprocessing has no model at all, and that is the normal case."""
    ext = _paper(
        data_sources=[_data_source("ImageNet")],
        runs=[_run(data_sources=["ImageNet"], mode="generate")],
    )
    assert check_references(ext) == []


def test_a_model_trained_then_evaluated_is_not_a_disagreement():
    """The ordinary shape, and the one the pairwise check called an error.

    `RefModel.execution_mode` describes what the paper did with the model
    overall; `Run.execution_mode` describes one run. A paper that trains a model
    and then evaluates it states both truthfully. Measured on the first v5 run,
    `run=inference, model=train` was the single largest group of pairwise
    "disagreements" -- 16 of 43.
    """
    ext = _paper(
        models=[_model("ResNet-50", mode="train")],
        runs=[
            _run(models=["ResNet-50"], mode="train"),
            _run(models=["ResNet-50"], mode="inference"),
        ],
    )
    assert EXECUTION_MODE_DISAGREES not in _codes(ext)


def test_a_mode_matching_no_run_the_model_appears_in_is_reported():
    """The real signal: usually the run that would justify it was never listed."""
    ext = _paper(
        models=[_model("Phi-3", mode="finetune")],
        runs=[
            _run(models=["Phi-3"], mode="train"),
            _run(models=["Phi-3"], mode="inference"),
        ],
    )
    [problem] = [p for p in check_references(ext) if p.code == EXECUTION_MODE_DISAGREES]
    assert "finetune" in problem.detail
    assert "'inference', 'train'" in problem.detail


def test_a_participant_role_does_not_create_a_disagreement():
    """A teacher in a train run is not being trained; it was trained elsewhere."""
    ext = _paper(
        models=[
            _model("Student", mode="train"),
            _model("Teacher", mode="inference"),
        ],
        runs=[
            _run(models=["Student", "Teacher"], mode="train"),
            _run(models=["Teacher"], mode="inference"),
        ],
    )
    assert EXECUTION_MODE_DISAGREES not in _codes(ext)


def test_a_frozen_participant_is_not_compared_at_all():
    """A teacher and a data-source model are participants, not what ran.

    The owner's run criterion is "a frozen network is a participant", so a
    teacher's own `inference` mode and the `train` run it takes part in are both
    true. On the first v5 run this was 3 of 10 remaining disagreements: a
    tokenizer, a binding proxy and a pair of scoring oracles, each appearing
    only in a frozen role.
    """
    ext = _paper(
        models=[_model("Scoring oracle", mode="inference")],
        runs=[_run(models=["Scoring oracle"], mode="train")],
    )
    # The fixture's RunModel role is "main", so this IS compared and flagged.
    assert EXECUTION_MODE_DISAGREES in _codes(ext)

    frozen = _paper(
        models=[_model("Scoring oracle", mode="inference")],
        runs=[
            {
                **_run(mode="train"),
                "models": [{"name": "Scoring oracle", "role_in_run": "data-source"}],
            }
        ],
    )
    assert EXECUTION_MODE_DISAGREES not in _codes(frozen)


def test_a_role_is_read_by_value_not_by_its_enum_repr():
    """`str(ModelRunRole.DATA_SOURCE)` is not `'data-source'`.

    Reading an enum by `str()` has been a bug three times here, and each time it
    made a check silently report nothing. Pinned so the fourth is caught.
    """
    from paperext.structured_output.mdl.check import _enum_value
    from paperext.structured_output.mdl.model_v5 import ModelRunRole

    assert _enum_value(ModelRunRole.DATA_SOURCE) == "data-source"
    assert _enum_value(ModelRunRole.TEACHER) == "teacher"
    assert _enum_value("main") == "main"
    assert _enum_value(None) == ""
    assert str(ModelRunRole.DATA_SOURCE) != "data-source"  # the trap itself
