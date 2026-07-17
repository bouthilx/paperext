import json
from pathlib import Path

import pytest

from paperext.analysis.frequency import (
    Dimension,
    _paper_id,
    aggregate,
    build_maps,
    group_files_by_paper,
    write_reports,
)

# --- fixtures: build v4 PaperExtractions from plain dicts --------------------

pytest.importorskip("paperext.structured_output.mdl.model")
from paperext.structured_output.mdl.model import PaperExtractions  # noqa: E402


def _expl(v):
    return {"quote": "", "justification": "", "value": v}


def _model(name, aliases=None):
    return {
        "name": _expl(name),
        "aliases": aliases or [],
        "is_contributed": _expl(False),
        "is_executed": _expl(False),
        "is_compared": _expl(False),
        "execution_mode": _expl("unknown"),
        "parameter_count": _expl("unknown"),
        "referenced_paper_title": _expl(""),
    }


def _ref(name, role="used", aliases=None):
    return {
        "name": _expl(name),
        "aliases": aliases or [],
        "role": role,
        "referenced_paper_title": _expl(""),
    }


def _rf(name, aliases=None):
    return {"name": _expl(name), "aliases": aliases or []}


def make_paper(
    models=None, datasets=None, libraries=None, primary_rf="x", sub_rfs=None
):
    return PaperExtractions.model_validate(
        {
            "title": _expl("t"),
            "description": "d",
            "type": _expl("empirical"),
            "primary_research_field": _rf(primary_rf),
            "sub_research_fields": [_rf(s) for s in (sub_rfs or [])],
            "models": [
                _model(*m) if isinstance(m, tuple) else _model(m)
                for m in (models or [])
            ],
            "datasets": [_ref(d) for d in (datasets or [])],
            "libraries": [_ref(l) for l in (libraries or [])],
        }
    )


TREE = {
    "algorithms": {
        "reinforcement learning": {"ppo": {}, "dqn": {}},
        "optimizer": {"adam": {}},
    },
    "neural networks": {"cnn": {"resnet": {"resnet-50": {}}}},
    "ignore": {"badname": {}},
}


@pytest.fixture
def tree_path(tmp_path: Path) -> Path:
    p = tmp_path / "models.json"
    p.write_text(json.dumps(TREE))
    return p


@pytest.fixture
def depth2_dim(tree_path):
    return build_maps(Dimension("models", tree_path, 2))


@pytest.fixture
def node_dim(tree_path):
    # Only the RL branch is selected -> optimizer/adam and the CNN branch are Other.
    return build_maps(
        Dimension("models", tree_path, {"algorithms.reinforcement learning"})
    )


# --- category / name counting ----------------------------------------------


def test_within_paper_category_dedup(depth2_dim):
    # Two models in the same category -> that category counted once for the paper.
    papers = [make_paper(models=["ppo", "dqn"])]
    res = aggregate(papers, depth2_dim)
    assert res.category_counts["reinforcement learning"] == 1
    # ... but each distinct name is still counted once.
    assert res.name_counts["ppo"] == 1
    assert res.name_counts["dqn"] == 1


def test_non_exclusive_across_categories(depth2_dim):
    # One paper spanning two categories counts toward both.
    papers = [make_paper(models=["ppo", "adam"])]
    res = aggregate(papers, depth2_dim)
    assert res.category_counts["reinforcement learning"] == 1
    assert res.category_counts["optimizer"] == 1


def test_alias_folds_at_category_level(depth2_dim):
    # resnet and its nested alias resnet-50 both roll up to cnn.
    papers = [make_paper(models=["resnet"]), make_paper(models=["resnet-50"])]
    res = aggregate(papers, depth2_dim)
    assert res.category_counts["cnn"] == 2


def test_paper_frequency_not_mention_frequency(depth2_dim):
    # Three mentions of ppo in one paper is still one paper.
    papers = [make_paper(models=["ppo", "ppo", "ppo"])]
    res = aggregate(papers, depth2_dim)
    assert res.name_counts["ppo"] == 1
    assert res.category_counts["reinforcement learning"] == 1


# --- Other policy -----------------------------------------------------------


def test_inclusive_other_counts_even_with_selected(node_dim):
    # Paper has a selected model (ppo) AND an unselected one (adam -> Other).
    papers = [make_paper(models=["ppo", "adam"])]
    res = aggregate(papers, node_dim, other_policy="inclusive")
    assert res.category_counts["reinforcement learning"] == 1
    assert res.category_counts["Other"] == 1


def test_residual_other_excludes_papers_with_a_selected_bucket(node_dim):
    papers = [
        make_paper(models=["ppo", "adam"]),  # has a selected bucket -> not Other
        make_paper(models=["adam"]),  # only Other -> counts as residual Other
    ]
    inc = aggregate(papers, node_dim, other_policy="inclusive")
    res = aggregate(papers, node_dim, other_policy="residual")
    assert inc.category_counts["Other"] == 2
    assert res.category_counts["Other"] == 1
    # Non-Other counts are identical under both policies.
    assert inc.category_counts["reinforcement learning"] == 1
    assert res.category_counts["reinforcement learning"] == 1


def test_residual_other_dropped_when_empty(node_dim):
    papers = [make_paper(models=["ppo"])]  # everything selected, no Other
    res = aggregate(papers, node_dim, other_policy="residual")
    assert "Other" not in res.category_counts


# --- ignore / unmapped ------------------------------------------------------


def test_ignore_branch_dropped_not_counted(depth2_dim):
    papers = [make_paper(models=["badname"])]
    res = aggregate(papers, depth2_dim)
    assert "badname" not in res.name_counts
    assert res.n_papers == 1
    assert res.n_papers_with_dim == 0  # the only item was dropped
    assert "badname" not in res.unmapped_names


def test_unknown_name_is_unmapped_other(depth2_dim):
    papers = [make_paper(models=["totallynovelmodel"])]
    res = aggregate(papers, depth2_dim)
    assert res.name_counts["totallynovelmodel"] == 1
    assert res.category_counts["Other"] == 1
    assert "totallynovelmodel" in res.unmapped_names


# --- display name recovery / aliases in extraction --------------------------


def test_display_name_recovered_from_tree(depth2_dim):
    papers = [make_paper(models=["resnet-50"])]
    res = aggregate(papers, depth2_dim)
    rows = {r[1]: r for r in res.name_rows()}
    # normalized key resnet50, raw display "resnet-50" recovered from the tree.
    assert rows["resnet50"][0] == "resnet-50"


def test_extraction_alias_resolves(depth2_dim):
    # Primary name unknown, but an alias matches a tree node.
    papers = [make_paper(models=[("some marketing name", ["resnet-50"])])]
    res = aggregate(papers, depth2_dim)
    assert res.category_counts["cnn"] == 1
    assert "resnet50" in res.name_counts


# --- research fields --------------------------------------------------------


def test_research_fields_fan_primary_and_sub(tmp_path):
    tree = {"vision": {"computer vision": {}}, "nlp": {"language": {}}}
    p = tmp_path / "dom.json"
    p.write_text(json.dumps(tree))
    dim = build_maps(Dimension("research_fields", p, 1))
    papers = [make_paper(primary_rf="computer vision", sub_rfs=["language"])]
    res = aggregate(papers, dim)
    assert res.category_counts["vision"] == 1
    assert res.category_counts["nlp"] == 1


# --- no-tree dimension (datasets/libraries by name) -------------------------


def test_no_tree_dimension_reports_by_name():
    dim = build_maps(Dimension("datasets"))
    assert not dim.has_tree
    papers = [
        make_paper(datasets=["CIFAR-10", "ImageNet"]),
        make_paper(datasets=["CIFAR-10"]),
    ]
    res = aggregate(papers, dim)
    # Each name is its own category; raw display preserved.
    assert res.category_counts["CIFAR-10"] == 2
    assert res.category_counts["ImageNet"] == 1
    assert res.name_counts["cifar10"] == 2


# --- validation -------------------------------------------------------------


def test_bad_other_policy_raises(depth2_dim):
    with pytest.raises(ValueError):
        aggregate([], depth2_dim, other_policy="nope")


# --- file grouping ----------------------------------------------------------


def test_paper_id_strips_query_index():
    assert _paper_id(Path("abc123_00.json")) == "abc123"
    assert _paper_id(Path("abc123_07.json")) == "abc123"
    assert _paper_id(Path("no_index_here.json")) == "no_index_here"


def test_group_files_by_paper():
    files = [Path(f"{p}_{i:02d}.json") for p in ("a", "b") for i in (0, 1)]
    groups = group_files_by_paper(files)
    assert set(groups) == {"a", "b"}
    assert len(groups["a"]) == 2


# --- report writing ---------------------------------------------------------


def test_write_reports_creates_files(depth2_dim, tmp_path):
    papers = [make_paper(models=["ppo", "resnet"]), make_paper(models=["adam"])]
    res = aggregate(papers, depth2_dim)
    written = write_reports([res], tmp_path / "out", "inclusive")
    names = {p.name for p in written}
    assert "models_categories.csv" in names
    assert "models_names.csv" in names
    assert "frequency_summary.md" in names
    assert all(p.exists() for p in written)


# --- loader integration (real corpus, up-convert) ---------------------------


def test_load_extractions_upconverts_real_file():
    from paperext.analysis.frequency import load_extractions

    files = sorted(Path("data/mdl/queries/openai").glob("*.json"))
    if not files:
        pytest.skip("no real openai extractions available")
    ext = load_extractions(files[0])
    # v3 corpus lacks execution_mode; up-convert must add it as unknown.
    if ext.models:
        assert ext.models[0].execution_mode.value in (
            "train",
            "finetune",
            "inference",
            "unknown",
        )
