"""Metric functions against hand-computed cases (WS-D D1b-3, #53).

Every number here is worked out by hand in the test name or a comment. A metric
whose value is only ever produced by the code it is testing is not tested.
"""

import math

import pytest

from paperext.categorize import metrics
from paperext.categorize.placement import Placement


def placement(node_id, ancestors, *, name="x"):
    return Placement(
        node_id=node_id,
        name=name,
        parent_id=ancestors[-1] if ancestors else None,
        ancestor_path=list(ancestors) + ([node_id] if node_id else []),
        ancestor_names=list(ancestors) + [name],
        depth=len(ancestors) + 1,
    )


# --------------------------------------------------------------------------- #
# Lineage
# --------------------------------------------------------------------------- #


def test_lineage_drops_the_node_itself():
    assert metrics.lineage(placement("vit", ["nn", "transformer"])) == [
        "nn",
        "transformer",
    ]


def test_lineage_of_a_created_node_is_its_parent_chain():
    # node_id None -> the placement is a create_node against the pre-decision tree
    assert metrics.lineage(placement(None, ["nn", "transformer"])) == [
        "nn",
        "transformer",
    ]


def test_recreating_the_ablated_node_scores_a_perfect_match():
    """The whole point of the parent-chain convention.

    The reference node was ablated, so re-creating it under the true parent *is*
    the correct action; comparing full node paths would score it as a miss.
    """
    reference = metrics.lineage(placement("vit", ["nn", "transformer"]))
    created = metrics.lineage(placement(None, ["nn", "transformer"]))
    score = metrics.hierarchical_prf(created, reference)
    assert (score.precision, score.recall, score.f1) == (1.0, 1.0, 1.0)
    assert score.same_lineage


def test_one_level_up_is_full_precision_partial_recall():
    # pred {nn}, ref {nn, transformer} -> hP = 1/1, hR = 1/2, F1 = 2/3
    score = metrics.hierarchical_prf(["nn"], ["nn", "transformer"])
    assert score.precision == 1.0
    assert score.recall == 0.5
    assert score.f1 == pytest.approx(2 / 3)
    assert score.same_lineage
    assert score.lca_depth == 1


def test_wrong_branch_is_off_lineage():
    score = metrics.hierarchical_prf(["nn", "gnn"], ["nn", "transformer"])
    assert score.precision == 0.5
    assert score.recall == 0.5
    assert not score.same_lineage
    assert score.lca_depth == 1


def test_empty_chains_have_nothing_to_get_wrong():
    score = metrics.hierarchical_prf([], [])
    assert (score.precision, score.recall) == (1.0, 1.0)


def test_root_reference_with_a_deep_prediction():
    score = metrics.hierarchical_prf(["nn"], [])
    assert score.precision == 0.0  # nothing shared, one predicted ancestor
    assert score.recall == 1.0  # vacuous: there was nothing to recover
    assert score.f1 == 0.0


# --------------------------------------------------------------------------- #
# Categorical agreement
# --------------------------------------------------------------------------- #


def test_none_is_its_own_label_not_other():
    """A placement under a dropped root contributes to no category at all."""
    assert metrics.agreement([None], ["Other"]) == 0.0
    assert metrics.agreement([None], [None]) == 1.0
    assert metrics.label(None) == metrics.IGNORED


def test_agreement_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        metrics.agreement(["a"], ["a", "b"])


def test_macro_recall_kills_the_always_other_degenerate():
    """45% prevalence makes always-Other look fine on plain agreement."""
    reference = ["Other"] * 9 + ["transformer"] * 6 + ["gnn"] * 5
    always_other = ["Other"] * 20
    assert metrics.agreement(always_other, reference) == pytest.approx(0.45)
    assert metrics.macro_recall(always_other, reference) == 0.0


def test_macro_recall_is_unweighted_across_buckets():
    # transformer 1/2, gnn 2/2 -> (0.5 + 1.0) / 2
    reference = ["transformer", "transformer", "gnn", "gnn", "Other"]
    predicted = ["transformer", "Other", "gnn", "gnn", "Other"]
    assert metrics.macro_recall(predicted, reference) == pytest.approx(0.75)


def test_cohen_kappa_hand_computed():
    # po = 3/4; pe = (2/4)(2/4) + (2/4)(2/4) = 0.5; k = (0.75-0.5)/0.5 = 0.5
    predicted = ["a", "a", "b", "b"]
    reference = ["a", "a", "a", "b"]
    assert metrics.cohen_kappa(predicted, reference) == pytest.approx(0.5)


def test_cohen_kappa_is_one_when_everything_agrees_on_one_label():
    assert metrics.cohen_kappa(["a", "a"], ["a", "a"]) == 1.0


def test_fleiss_kappa_hand_computed():
    # 2 items, 3 raters. item 1: aaa -> P=1. item 2: aab -> P=(4+1-3)/6=1/3.
    # Pbar = 2/3. p_a = 5/6, p_b = 1/6 -> Pe = 25/36 + 1/36 = 26/36.
    # kappa = (2/3 - 26/36) / (1 - 26/36) = (-2/36) / (10/36) = -0.2
    assert metrics.fleiss_kappa([["a", "a", "a"], ["a", "a", "b"]]) == pytest.approx(
        -0.2
    )


def test_fleiss_kappa_is_one_on_degenerate_perfect_agreement():
    """Everything 'Other' three times: chance agreement is 1, kappa undefined."""
    assert metrics.fleiss_kappa([["Other"] * 3] * 4) == 1.0


def test_fleiss_kappa_needs_a_constant_panel():
    with pytest.raises(ValueError):
        metrics.fleiss_kappa([["a", "b"], ["a"]])


def test_triple_agreement_counts_unanimous_items():
    assert metrics.triple_agreement([["a", "a", "a"], ["a", "b", "a"]]) == 0.5


def test_youden_j_is_zero_for_both_degenerate_strategies():
    assert metrics.youden_j(1.0, 1.0) == 0.0  # always abstain
    assert metrics.youden_j(0.0, 0.0) == 0.0  # never abstain
    assert metrics.youden_j(1.0, 0.0) == 1.0


# --------------------------------------------------------------------------- #
# Distribution
# --------------------------------------------------------------------------- #


def test_shares_normalize_and_sort():
    assert metrics.shares(["a", "a", "b"]) == {
        "a": pytest.approx(2 / 3),
        "b": pytest.approx(1 / 3),
    }


def test_total_variation_of_disjoint_supports_is_one():
    assert metrics.total_variation({"a": 1.0}, {"b": 1.0}) == 1.0


def test_spearman_of_a_reversed_ranking_is_minus_one():
    assert metrics.spearman(
        {"a": 3, "b": 2, "c": 1}, {"a": 1, "b": 2, "c": 3}
    ) == pytest.approx(-1.0)


def test_spearman_handles_ties_with_average_ranks():
    # both vectors constant in one coordinate -> still defined here
    assert metrics.spearman(
        {"a": 1, "b": 1, "c": 2}, {"a": 1, "b": 1, "c": 2}
    ) == pytest.approx(1.0)


def test_spearman_is_nan_without_variance():
    assert math.isnan(metrics.spearman({"a": 1, "b": 1}, {"a": 1, "b": 1}))


def test_top_k_overlap_is_normalized_by_the_smaller_top_set():
    """Otherwise 'top-5 unchanged' is unsatisfiable when fewer than 5 exist."""
    assert metrics.top_k_overlap({"a": 0.6, "b": 0.4}, {"a": 1.0}, 5) == 1.0
    assert metrics.top_k_overlap({"a": 1.0}, {"b": 1.0}, 5) == 0.0


# --------------------------------------------------------------------------- #
# Win rate, bootstrap, risk-coverage
# --------------------------------------------------------------------------- #


def test_win_rate_decomposes_into_l_t_g():
    scores = [0.0, 0.5, 1.0, 1.0]
    win = metrics.win_rate(scores, resamples=200)
    assert win.w == pytest.approx(0.625)
    assert (win.lost, win.tied, win.won) == (1, 1, 2)


def test_all_agreements_sit_exactly_on_the_ceiling():
    """Memorizing the reference produces agreements, which score 0.5 -- never more."""
    win = metrics.win_rate([0.5] * 50, resamples=200)
    assert win.w == 0.5
    assert win.lower_bound == 0.5


def test_bootstrap_is_reproducible_and_seed_dependent():
    values = [0.0, 0.5, 1.0] * 20
    first = metrics.bootstrap_ci(values, seed=7, resamples=500)
    assert first == metrics.bootstrap_ci(values, seed=7, resamples=500)
    assert first != metrics.bootstrap_ci(values, seed=8, resamples=500)


def test_lower_bound_sits_below_the_point_estimate():
    values = [0.0, 0.5, 1.0] * 40
    bound = metrics.lower_bound(values, seed=1, resamples=1000)
    assert bound < sum(values) / len(values)
    assert metrics.bootstrap_ci(values, seed=1, resamples=1000)[0] <= bound


def test_risk_coverage_orders_by_confidence():
    curve = metrics.risk_coverage([(0.0, 0.1), (1.0, 0.9)], n_total=2)
    assert [point.w for point in curve] == [1.0, 0.5]
    assert [point.coverage for point in curve] == [0.5, 1.0]


def test_w_at_coverage_is_nan_when_the_agent_abstains_too_much():
    """Abstention lowers coverage; it must not buy a flattering headline."""
    curve = metrics.risk_coverage([(1.0, 0.9)], n_total=10)  # answered 1 of 10
    assert math.isnan(metrics.w_at_coverage(curve, 0.85))


def test_w_at_coverage_reads_the_confident_prefix():
    scored = [(1.0, 0.9), (1.0, 0.8), (0.0, 0.1), (0.0, 0.05)]
    curve = metrics.risk_coverage(scored, n_total=4)
    assert metrics.w_at_coverage(curve, 0.5) == 1.0
    assert metrics.w_at_coverage(curve, 1.0) == 0.5
