import json
from pathlib import Path

import pytest

from paperext.analysis.frequency import Dimension, aggregate, build_maps
from paperext.analysis.workload import (
    EXECUTION_MODE,
    IS_EXECUTED,
    ROLE,
    aggregate_split,
    write_reports,
)

pytest.importorskip("paperext.structured_output.mdl.model")
from paperext.structured_output.mdl.model import PaperExtractions  # noqa: E402


def _expl(v):
    return {"quote": "", "justification": "", "value": v}


def _model(name, is_executed=False, execution_mode="unknown"):
    return {
        "name": _expl(name),
        "aliases": [],
        "is_contributed": _expl(False),
        "is_executed": _expl(is_executed),
        "is_compared": _expl(False),
        "execution_mode": _expl(execution_mode),
        "parameter_count": _expl("unknown"),
        "referenced_paper_title": _expl(""),
    }


def _ref(name, role="used"):
    return {
        "name": _expl(name),
        "aliases": [],
        "role": role,
        "referenced_paper_title": _expl(""),
    }


def _rf(name):
    return {"name": _expl(name), "aliases": []}


def make_paper(models=None, datasets=None, libraries=None):
    return PaperExtractions.model_validate(
        {
            "title": _expl("t"),
            "description": "d",
            "type": _expl("empirical"),
            "primary_research_field": _rf("x"),
            "sub_research_fields": [],
            "models": [_model(**m) for m in (models or [])],
            "datasets": [_ref(**d) for d in (datasets or [])],
            "libraries": [_ref(**l) for l in (libraries or [])],
        }
    )


TREE = {
    "algorithms": {
        "reinforcement learning": {"ppo": {}, "dqn": {}},
        "optimizer": {"adam": {}},
    },
    "neural networks": {"cnn": {"resnet": {}}},
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
    return build_maps(
        Dimension("models", tree_path, {"algorithms.reinforcement learning"})
    )


@pytest.fixture
def datasets_dim():
    return build_maps(Dimension("datasets"))


# --- is_executed split ------------------------------------------------------


def test_is_executed_split(depth2_dim):
    papers = [
        make_paper(
            models=[
                {"name": "ppo", "is_executed": True},
                {"name": "dqn", "is_executed": False},
            ]
        )
    ]
    res = aggregate_split(papers, depth2_dim, IS_EXECUTED)
    # Both models are in the RL category, one executed one referenced; assert the
    # whole cell dict so no stray cell can hide.
    assert res.category_split_counts == {
        ("reinforcement learning", "executed"): 1,
        ("reinforcement learning", "referenced"): 1,
    }
    # Union over splits: the paper counts once in the category.
    assert res.category_counts == {"reinforcement learning": 1}


def test_execution_mode_split(depth2_dim):
    papers = [
        make_paper(models=[{"name": "ppo", "execution_mode": "train"}]),
        make_paper(models=[{"name": "dqn", "execution_mode": "finetune"}]),
        make_paper(models=[{"name": "adam", "execution_mode": "inference"}]),
    ]
    res = aggregate_split(papers, depth2_dim, EXECUTION_MODE)
    assert res.category_split_counts == {
        ("reinforcement learning", "train"): 1,
        ("reinforcement learning", "finetune"): 1,
        ("optimizer", "inference"): 1,
    }
    assert res.category_counts == {"reinforcement learning": 2, "optimizer": 1}


def test_role_split_datasets(datasets_dim):
    papers = [
        make_paper(
            datasets=[
                {"name": "CIFAR-10", "role": "used"},
                {"name": "MyData", "role": "contributed"},
            ]
        )
    ]
    res = aggregate_split(papers, datasets_dim, ROLE)
    assert res.category_split_counts == {
        ("CIFAR-10", "used"): 1,
        ("MyData", "contributed"): 1,
    }


def test_cumulative_split_counts(depth2_dim):
    # Cells and totals must accumulate above 1. ppo executed in 3 papers, dqn
    # referenced in 2 (both RL); adam executed in 1 (optimizer). Same-category
    # items with different splits land in different cells, but the paper is only
    # counted once per (category, split) and once in the union total.
    papers = [
        make_paper(models=[{"name": "ppo", "is_executed": True}]),
        make_paper(models=[{"name": "ppo", "is_executed": True}]),
        make_paper(
            models=[
                {"name": "ppo", "is_executed": True},
                {"name": "dqn", "is_executed": False},
            ]
        ),
        make_paper(
            models=[
                {"name": "dqn", "is_executed": False},
                {"name": "adam", "is_executed": True},
            ]
        ),
    ]
    res = aggregate_split(papers, depth2_dim, IS_EXECUTED)
    assert res.category_split_counts == {
        ("reinforcement learning", "executed"): 3,  # papers 1,2,3 have executed ppo
        ("reinforcement learning", "referenced"): 2,  # papers 3,4 have referenced dqn
        ("optimizer", "executed"): 1,
    }
    # Union totals: RL in 4 distinct papers, optimizer in 1.
    assert res.category_counts == {"reinforcement learning": 4, "optimizer": 1}
    assert res.name_split_counts == {
        ("ppo", "executed"): 3,
        ("dqn", "referenced"): 2,
        ("adam", "executed"): 1,
    }
    assert res.name_counts == {"ppo": 3, "dqn": 2, "adam": 1}


# --- reconciliation with E1b ------------------------------------------------


def test_unsplit_reconciles_with_frequency_inclusive(node_dim):
    papers = [
        make_paper(
            models=[
                {"name": "ppo", "is_executed": True},
                {"name": "ppo", "is_executed": False},  # same name, other split
                {"name": "adam"},  # Other
            ]
        ),
        make_paper(models=[{"name": "resnet"}]),  # Other under node cut
        make_paper(models=[{"name": "dqn"}]),  # selected -> RL bumps to 2
    ]
    freq = aggregate(papers, node_dim, other_policy="inclusive")
    wl = aggregate_split(papers, node_dim, IS_EXECUTED, other_policy="inclusive")
    # Concrete expected values (so both sides aren't just identically wrong)...
    assert freq.category_counts == {"reinforcement learning": 2, "Other": 2}
    assert freq.name_counts == {"ppo": 1, "adam": 1, "resnet": 1, "dqn": 1}
    # ... and the workload union reproduces them exactly.
    assert wl.category_counts == freq.category_counts
    assert wl.name_counts == freq.name_counts


def test_unsplit_reconciles_with_frequency_residual(node_dim):
    papers = [
        make_paper(models=[{"name": "ppo"}, {"name": "adam"}]),  # selected + Other
        make_paper(models=[{"name": "adam"}]),  # only Other
        make_paper(models=[{"name": "ppo"}]),  # selected -> RL bumps to 2
    ]
    freq = aggregate(papers, node_dim, other_policy="residual")
    wl = aggregate_split(papers, node_dim, IS_EXECUTED, other_policy="residual")
    assert freq.category_counts == {"reinforcement learning": 2, "Other": 1}
    assert wl.category_counts == freq.category_counts


# --- Other policy on the split ----------------------------------------------


def test_residual_other_split_drops_papers_with_selected(node_dim):
    papers = [
        make_paper(
            models=[
                {"name": "ppo", "is_executed": True},  # selected
                {"name": "adam", "is_executed": True},  # Other
            ]
        ),
        make_paper(models=[{"name": "adam", "is_executed": False}]),  # only Other
    ]
    inc = aggregate_split(papers, node_dim, IS_EXECUTED, other_policy="inclusive")
    res = aggregate_split(papers, node_dim, IS_EXECUTED, other_policy="residual")
    # Inclusive: both papers' Other items counted (executed once, referenced once);
    # the selected RL cell is untouched by the policy.
    assert inc.category_split_counts == {
        ("reinforcement learning", "executed"): 1,
        ("Other", "executed"): 1,
        ("Other", "referenced"): 1,
    }
    # Residual: the first paper had a selected bucket -> its Other cell is dropped;
    # only the second (Other-only, referenced) survives. RL cell unchanged.
    assert res.category_split_counts == {
        ("reinforcement learning", "executed"): 1,
        ("Other", "referenced"): 1,
    }


# --- ignore dropped ---------------------------------------------------------


def test_ignore_dropped_in_split(depth2_dim):
    papers = [make_paper(models=[{"name": "badname", "is_executed": True}])]
    res = aggregate_split(papers, depth2_dim, IS_EXECUTED)
    assert res.category_counts == {}
    assert res.n_papers_with_dim == 0


# --- matrix shape -----------------------------------------------------------


def test_category_matrix_columns_and_total(depth2_dim):
    papers = [
        make_paper(
            models=[
                {"name": "ppo", "execution_mode": "train"},
                {"name": "dqn", "execution_mode": "unknown"},
            ]
        )
    ]
    res = aggregate_split(papers, depth2_dim, EXECUTION_MODE)
    header, rows = res.category_matrix()
    assert header == [
        "category",
        "train",
        "finetune",
        "inference",
        "unknown",
        "total",
    ]
    rl_row = next(r for r in rows if r[0] == "reinforcement learning")
    # train=1, finetune=0, inference=0, unknown=1, total(union)=1
    assert rl_row[1] == 1 and rl_row[4] == 1 and rl_row[-1] == 1


def test_matrix_includes_unexpected_split_values(datasets_dim):
    # A split value outside the declared order still appears as a column.
    papers = [make_paper(datasets=[{"name": "D", "role": "referenced"}])]
    res = aggregate_split(papers, datasets_dim, ROLE)
    header, _ = res.category_matrix()
    assert "referenced" in header


# --- validation & output ----------------------------------------------------


def test_bad_policy_raises(depth2_dim):
    with pytest.raises(ValueError):
        aggregate_split([], depth2_dim, IS_EXECUTED, other_policy="nope")


def test_write_reports(depth2_dim, tmp_path):
    papers = [make_paper(models=[{"name": "ppo", "is_executed": True}])]
    res = aggregate_split(papers, depth2_dim, IS_EXECUTED)
    written = write_reports([res], tmp_path / "out", "inclusive")
    names = {p.name for p in written}
    assert "models_is_executed_categories.csv" in names
    assert "models_is_executed_names.csv" in names
    assert "workload_summary.md" in names
    assert all(p.exists() for p in written)
