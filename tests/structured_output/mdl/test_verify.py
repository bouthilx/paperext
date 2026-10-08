"""The #103 verification pass: that each check fires on the thing it names.

A harness whose checks cannot fail is worse than no harness, so every CHECK and
PROBE here is exercised in both directions. The real validation ran against the
legacy-2024 corpus, where the first checks are *known* to fail: it reproduced
all of them (27 papers with `adam` in `libraries[]`, 12 with `mujoco` in
`data_sources[]`, and zero on all three region probes), which is recorded in
`c0_verification/BASELINE.md`.
"""

from __future__ import annotations

from paperext.query import get_extraction_response
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


def _run(*, mode="train", parameter_count="unknown", repetitions=None):
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
        "repetitions": _expl(repetitions or []),
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
    assert _by_name(empty, "decoding is non-zero").ok is False
    hit = probes(_corpus(algorithms=[_algorithm("beam search")]), PROBE_SETS)
    assert _by_name(hit, "decoding is non-zero").ok is True


def test_a_probe_matches_a_written_surface_but_never_a_similar_one():
    """Aliases count; similarity never does -- it paired gpt-j with GPT-4."""
    by_surface = probes(_corpus(algorithms=[_algorithm("kfold")]), PROBE_SETS)
    assert _by_name(by_surface, "evaluation is non-zero").ok is True
    near_miss = probes(_corpus(algorithms=[_algorithm("k-fold-ish CV")]), PROBE_SETS)
    assert _by_name(near_miss, "evaluation is non-zero").ok is False
    # The detection pass needs TWO shared content tokens, and this node name
    # yields only one ("fold"), so it stays silent here too. One shared token is
    # a coincidence, not a region.
    assert "0 papers" in _by_name(near_miss, "evaluation: region-shaped").detail


RICH_PROBE = {
    "regions": {
        "evaluation": [
            {
                "node_id": "M.kfold",
                "name": "k-fold cross-validation",
                "surfaces": [],
            }
        ]
    }
}


def test_a_region_the_ontology_cannot_spell_is_reported_separately():
    """The batch-2 finding, in miniature.

    openai returned `10-fold cross-validation` while the exact probe read zero,
    because the node is spelled `k-fold cross-validation`. That is an ontology
    normalisation gap, NOT the scope failing to reach the prompt, and the two
    must not collapse into one verdict.
    """
    corpus = _corpus(algorithms=[_algorithm("10-fold cross-validation")])
    found = probes(corpus, RICH_PROBE)

    exact = _by_name(found, "evaluation is non-zero")
    assert exact.ok is False, "no node is spelled 10-fold, so nothing is placed"
    assert "COMPANION" in exact.reading

    near = _by_name(found, "evaluation: region-shaped")
    assert near.ok is None
    assert "1 papers" in near.detail
    assert "10-fold cross-validation" in near.detail


def _factor(kind, count, what):
    return {"kind": kind, "count": count, "what": what}


def test_measurements_never_fail_and_multiply_the_repetition_factors():
    """The product is computed here, not asked of the extractor.

    v5's free-text field returned prose for 79 of 81 stated values, and the one
    answer that did arithmetic got it wrong (`96 configurations x 3 seeds =
    576`). So the factors are reported and multiplied here, where the result can
    be checked.
    """
    found = measurements(
        Corpus(
            {
                "p1": _paper(
                    runs=[
                        _run(),  # empty list: the paper did not say
                        _run(
                            repetitions=[
                                _factor("seed", 5, "random seeds"),
                                _factor("hyperparameter", 20, "learning rates"),
                            ]
                        ),
                    ]
                ),
                "p2": _paper(runs=[]),
            }
        )
    )
    assert all(f.ok is None for f in found)
    reps = _by_name(found, "factors and product")
    assert "1/2 runs state a factor" in reps.detail
    assert "seed:1" in reps.detail and "hyperparameter:1" in reps.detail
    assert "x100:1" in reps.detail, reps.detail


def test_a_workload_count_reported_as_a_repetition_is_flagged():
    """`'1,540 test episodes'` is the run's workload, not a repetition.

    The real v5 output used the free-text field for both, which would multiply a
    per-run cost by the number of items processed.
    """
    found = measurements(
        Corpus(
            {
                "p1": _paper(
                    runs=[_run(repetitions=[_factor("other", 1540, "test episodes")])]
                )
            }
        )
    )
    flagged = _by_name(found, "misread as workload")
    assert "1 factors" in flagged.detail and "test episodes" in flagged.detail

    clean = measurements(
        Corpus({"p1": _paper(runs=[_run(repetitions=[_factor("seed", 3, "seeds")])])})
    )
    assert "0 factors" in _by_name(clean, "misread as workload").detail


def _run_with_reference_source():
    run = _run()
    run["data_sources"] = [
        {
            "name": "Wikipedia",
            "access": "fixed",
            "roles_in_run": ["reference"],
        }
    ]
    return run


def test_a_reference_role_is_found_through_the_enum_not_its_repr():
    """`str()` on an enum member gives 'DataSourceRunRole.REFERENCE'.

    The membership test originally compared that against 'reference', so it
    never matched and the harness reported 0 reference-role sources while the
    extraction was returning them. Same unwrapping mistake as the `['unknown']`
    parallelism bug, so it is pinned here.
    """
    from paperext.structured_output.mdl.verify import manual

    found = manual(_corpus(runs=[_run_with_reference_source()]))
    [reference] = [f for f in found if "retrieval corpus" in f.name]
    assert reference.papers == ["p1"]
    assert "1 papers" in reference.detail

    none = manual(_corpus(runs=[_run()]))
    [reference] = [f for f in none if "retrieval corpus" in f.name]
    assert reference.papers == []


def test_an_unreadable_file_is_reported_not_silently_dropped(tmp_path):
    """A header that overstates the corpus makes every number under it false.

    When `repetitions` became a factor list, 23 of 25 batch-1 extractions
    stopped validating and the report still opened with "25 extraction files"
    while the measurements came from the 2 papers that had no runs.
    """
    from paperext.structured_output.mdl.verify import Corpus, loaded

    good = tmp_path / "good.json"
    good.write_text(
        get_extraction_response()(
            paper="good", words=1, extractions=_paper(), usage=None
        ).model_dump_json()
    )
    bad = tmp_path / "bad.json"
    bad.write_text('{"extractions": {"nope": true}}')

    corpus = Corpus.load([good, bad])
    assert set(corpus.papers) == {"good"}
    assert corpus.skipped == ["bad"]

    [finding] = loaded(corpus)
    assert finding.ok is False
    assert "1 loaded, 1 skipped" in finding.detail
    assert "EXCLUDES THE SKIPPED FILES" in finding.detail

    [clean] = loaded(Corpus.load([good]))
    assert clean.ok is True and "0 skipped" in clean.detail
