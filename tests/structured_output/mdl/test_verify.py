"""The #103 verification pass: that each check fires on the thing it names.

A harness whose checks cannot fail is worse than no harness, so every CHECK and
PROBE here is exercised in both directions. The real validation ran against the
legacy-2024 corpus, where the first checks are *known* to fail: it reproduced
all of them (27 papers with `adam` in `libraries[]`, 12 with `mujoco` in
`data_sources[]`, and zero on all three region probes), which is recorded in
`c0_verification/BASELINE.md`.
"""

from __future__ import annotations

from paperext.structured_output.mdl import model_v5
from paperext.structured_output.mdl.verify import (
    Corpus,
    acceptance,
    measurements,
    probes,
)


def _expl(value):
    return {"quote": "q", "justification": "j", "value": value}


def _named(name, **extra):
    base = {
        "name": _expl(name),
        "aliases": [],
        "is_contributed": _expl(False),
        "is_executed": _expl(True),
        "is_compared": _expl(False),
        "referenced_paper_title": _expl(""),
    }
    base.update(extra)
    return base


def _model(name):
    return _named(name, execution_mode=_expl("train"))


def _algorithm(name):
    return _named(name, paper_role=_expl("r"), composed_of=[])


def _library(name):
    return {
        "name": _expl(name),
        "aliases": [],
        "role": "used",
        "referenced_paper_title": _expl(""),
    }


def _data_source(name):
    return {
        "name": _expl(name),
        "aliases": [],
        "role": "used",
        "size": _expl("unknown"),
        "derived_from": [],
        "sample_properties": [],
        "referenced_paper_title": _expl(""),
    }


def _run(*, mode="train", parameter_count="unknown", repetitions="unknown"):
    return {
        "models": [],
        "data_sources": [],
        "algorithms": [],
        "produces": [],
        "execution_mode": _expl(mode),
        "epochs": _expl("unknown"),
        "parameter_count": _expl(parameter_count),
        "accelerator_type": _expl("unknown"),
        "accelerator_model": _expl("unknown"),
        "accelerator_count": _expl("unknown"),
        "precision": _expl("unknown"),
        "parallelism": _expl(["unknown"]),
        "duration": _expl("unknown"),
        "utilisation": _expl("unknown"),
        "repetitions": _expl(repetitions),
    }


def _paper(**slots):
    return model_v5.PaperExtractions.model_validate(
        {
            "title": _expl("t"),
            "description": "d",
            "type": _expl("empirical"),
            "research_fields": [{"name": _expl("x"), "aliases": [], "role": "unknown"}],
            "models": list(slots.get("models", [])),
            "data_sources": list(slots.get("data_sources", [])),
            "libraries": list(slots.get("libraries", [])),
            "algorithms": list(slots.get("algorithms", [])),
            "runs": list(slots.get("runs", [])),
        }
    )


def _corpus(**slots):
    return Corpus({"p1": _paper(**slots)})


def _by_name(findings, fragment):
    [found] = [f for f in findings if fragment in f.name]
    return found


def test_adam_in_libraries_fails_and_in_algorithms_passes():
    bad = acceptance(_corpus(libraries=[_library("Adam")]))
    assert _by_name(bad, "adam/adamw").ok is False
    good = acceptance(_corpus(algorithms=[_algorithm("Adam")]))
    assert _by_name(good, "adam/adamw").ok is True


def test_pytorch_as_a_model_fails():
    bad = acceptance(_corpus(models=[_model("PyTorch")]))
    assert _by_name(bad, "pytorch").ok is False
    good = acceptance(_corpus(libraries=[_library("PyTorch")]))
    assert _by_name(good, "pytorch").ok is True


def test_the_library_clause_fires_on_mujoco_as_a_data_source():
    """#102 Part A: the engine is a library, HalfCheetah is a data source."""
    bad = acceptance(_corpus(data_sources=[_data_source("MuJoCo")]))
    assert _by_name(bad, "mujoco").ok is False
    good = acceptance(
        _corpus(
            libraries=[_library("MuJoCo")],
            data_sources=[_data_source("HalfCheetah")],
        )
    )
    assert _by_name(good, "mujoco").ok is True


def test_the_protocol_clause_admits_atari_and_rejects_atari_100k():
    """The clause added 2026-10-08. `Atari` is a source, the protocol is not."""
    bad = acceptance(_corpus(data_sources=[_data_source("Atari 100k")]))
    assert _by_name(bad, "protocol").ok is False
    good = acceptance(_corpus(data_sources=[_data_source("Atari")]))
    assert _by_name(good, "protocol").ok is True


def test_an_unnamed_description_is_rejected_but_a_named_source_is_not():
    bad = acceptance(_corpus(data_sources=[_data_source("synthetic data")]))
    assert _by_name(bad, "unnamed description").ok is False
    good = acceptance(_corpus(data_sources=[_data_source("dSprites")]))
    assert _by_name(good, "unnamed description").ok is True


def test_a_generate_run_carrying_a_parameter_count_fails():
    """`generate` exists because stepping a simulator has no parameter count."""
    bad = acceptance(_corpus(runs=[_run(mode="generate", parameter_count="7B")]))
    assert _by_name(bad, "parameter count").ok is False
    ok = acceptance(_corpus(runs=[_run(mode="generate")]))
    assert _by_name(ok, "parameter count").ok is True
    # An inference run with a parameter count is correct, not a failure.
    fine = acceptance(_corpus(runs=[_run(mode="inference", parameter_count="7B")]))
    assert _by_name(fine, "parameter count").ok is True


PROBE_SETS = {
    "regions": {
        "decoding": [{"node_id": "M.beam", "name": "beam search", "surfaces": []}],
        "evaluation": [
            {"node_id": "M.kfold", "name": "k-fold CV", "surfaces": ["kfold"]}
        ],
    }
}


def test_a_region_probe_is_zero_until_a_matching_name_arrives():
    empty = probes(_corpus(algorithms=[_algorithm("SGD")]), PROBE_SETS)
    assert _by_name(empty, "decoding").ok is False
    hit = probes(_corpus(algorithms=[_algorithm("beam search")]), PROBE_SETS)
    assert _by_name(hit, "decoding").ok is True


def test_a_probe_matches_a_written_surface_but_never_a_similar_one():
    """Aliases count; similarity never does -- it paired gpt-j with GPT-4."""
    by_surface = probes(_corpus(algorithms=[_algorithm("kfold")]), PROBE_SETS)
    assert _by_name(by_surface, "evaluation").ok is True
    near_miss = probes(_corpus(algorithms=[_algorithm("k-fold-ish CV")]), PROBE_SETS)
    assert _by_name(near_miss, "evaluation").ok is False


def test_measurements_never_fail_and_report_the_repetitions_split():
    found = measurements(
        Corpus(
            {
                "p1": _paper(runs=[_run(repetitions="unknown"), _run(repetitions="1")]),
                "p2": _paper(runs=[]),
            }
        )
    )
    assert all(f.ok is None for f in found)
    reps = _by_name(found, "repetitions")
    assert "unknown:1" in reps.detail and "1:1" in reps.detail
    assert "0 runs" not in _by_name(found, "runs per paper").detail
