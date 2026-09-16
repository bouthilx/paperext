"""Metrics for the held-out categorization eval (WS-D D1b-3, #53).

Pure functions over plain sequences and mappings: no ontology, no I/O, no
network, no RNG that is not seeded here. Everything the gate reads is computed
in this module so the numbers can be checked against hand-worked cases.

**Why no flat accuracy.** The classes nest (``transformer`` contains ``vision
transformer``) and are heavily skewed (45% ``Other`` at the milabench cut), so an
accuracy figure mostly measures the prior, and it scores "one level up" exactly
like "the wrong branch". The families here are the three that survive that:
hierarchy-aware per-item agreement, distributional shape, and the blind pairwise
win rate that has an *analytic* 0.5 ceiling.

**The lineage convention, stated once because every hierarchical number depends
on it.** An eval item is scored against a tree its own node was ablated from, so
the correct answer is often to *re-create* the node. Comparing full node paths
would therefore score the correct action as a miss, every time. So lineage means
the **parent chain** -- the root-to-parent id list, the placed node itself
excluded -- on both sides:

===========================================  ======  ======  =============
placement vs reference ``transformer > vit``  ``hP``  ``hR``  same lineage?
===========================================  ======  ======  =============
new child of ``vit`` (the correct action)      1.00    1.00   yes
existing node ``vit`` itself                   1.00    1.00   yes
new child of ``transformer``                   1.00    0.67   yes
new child of ``graph neural network``          0.50    0.33   no
===========================================  ======  ======  =============

Undefined statistics return ``nan`` rather than a neutral-looking number: a
constant ranking has no Spearman rho, and a gate clause comparing ``nan`` to a
threshold fails, which is the safe direction.
"""

from __future__ import annotations

import math
import random
from typing import Callable, Iterable, Mapping, Sequence

from pydantic import BaseModel, Field

from paperext.categorize.placement import Placement

#: Label used for a placement that rolls up to no category at all (under a
#: dropped root). Distinct from ``Other``, which *is* a category.
IGNORED = "(ignore)"

#: Bootstrap resamples. 10k puts the Monte-Carlo error on a 95% bound well below
#: the 0.014 sampling SE the gate is sized for.
DEFAULT_RESAMPLES = 10_000

DEFAULT_SEED = 42


# --------------------------------------------------------------------------- #
# Hierarchy-aware per-item agreement
# --------------------------------------------------------------------------- #


def lineage(placement: Placement) -> "list[str]":
    """The root-to-parent id chain of *placement*, its own node excluded.

    See the module docstring: excluding the node is what keeps a correct
    re-creation from being scored as a miss.
    """
    path = list(placement.ancestor_path)
    if placement.node_id is not None and path and path[-1] == placement.node_id:
        path.pop()
    return path


class HierScore(BaseModel):
    """Hierarchical precision / recall / F1 for one item."""

    precision: float
    recall: float
    f1: float
    same_lineage: bool
    lca_depth: int


def hierarchical_prf(pred: "Sequence[str]", ref: "Sequence[str]") -> HierScore:
    """Compare two parent chains as ancestor *sets*.

    ``hP = |anc(pred) & anc(ref)| / |anc(pred)|`` and ``hR`` likewise over
    ``|anc(ref)|``. An empty chain (a root-level placement) has nothing to get
    wrong or to recover, so the corresponding rate is 1.0 by convention.
    """
    a, b = set(pred), set(ref)
    shared = len(a & b)
    precision = shared / len(a) if a else 1.0
    recall = shared / len(b) if b else 1.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return HierScore(
        precision=precision,
        recall=recall,
        f1=f1,
        same_lineage=same_lineage(pred, ref),
        lca_depth=lca_depth(pred, ref),
    )


def same_lineage(pred: "Sequence[str]", ref: "Sequence[str]") -> bool:
    """Whether the two parent chains sit on one root-to-leaf line.

    True when either chain is a prefix of the other -- the placement is at, above
    or below the reference's parent. Siblings of the reference *do* count: with
    the reference node ablated, "a new node under the same parent" is the correct
    action, not a near miss.
    """
    short, long = (pred, ref) if len(pred) <= len(ref) else (ref, pred)
    return list(short) == list(long[: len(short)])


def lca_depth(pred: "Sequence[str]", ref: "Sequence[str]") -> int:
    """Depth of the lowest common ancestor: the common prefix length."""
    depth = 0
    for left, right in zip(pred, ref):
        if left != right:
            break
        depth += 1
    return depth


# --------------------------------------------------------------------------- #
# Categorical agreement
# --------------------------------------------------------------------------- #


def label(category: "str | None") -> str:
    """A cut category as a comparable label; ``None`` becomes :data:`IGNORED`."""
    return IGNORED if category is None else category


def agreement(pred: "Sequence[str | None]", ref: "Sequence[str | None]") -> float:
    """Plain cut-level agreement rate -- reported, never gated on its own."""
    if len(pred) != len(ref):
        raise ValueError("pred and ref must be the same length")
    if not pred:
        return float("nan")
    return sum(label(p) == label(r) for p, r in zip(pred, ref)) / len(pred)


def macro_recall(
    pred: "Sequence[str | None]",
    ref: "Sequence[str | None]",
    *,
    exclude: "Iterable[str]" = ("Other", IGNORED),
) -> float:
    """Mean per-class recall over the reference buckets, ``Other`` excluded.

    This is the clause that blocks the always-``Other`` degenerate: at 45%
    prevalence it scores 0.45 on plain agreement but 0.0 here.
    """
    skip = set(exclude)
    buckets: "dict[str, list[bool]]" = {}
    for p, r in zip(pred, ref):
        key = label(r)
        if key in skip:
            continue
        buckets.setdefault(key, []).append(label(p) == key)
    if not buckets:
        return float("nan")
    return sum(sum(hits) / len(hits) for hits in buckets.values()) / len(buckets)


def cohen_kappa(pred: "Sequence[str | None]", ref: "Sequence[str | None]") -> float:
    """Chance-corrected agreement between two labellings of the same items."""
    if len(pred) != len(ref) or not pred:
        return float("nan")
    n = len(pred)
    observed = agreement(pred, ref)
    p_counts: "dict[str, int]" = {}
    r_counts: "dict[str, int]" = {}
    for p, r in zip(pred, ref):
        p_counts[label(p)] = p_counts.get(label(p), 0) + 1
        r_counts[label(r)] = r_counts.get(label(r), 0) + 1
    expected = sum(
        (p_counts.get(key, 0) / n) * (r_counts.get(key, 0) / n)
        for key in set(p_counts) | set(r_counts)
    )
    if math.isclose(expected, 1.0):
        return 1.0 if math.isclose(observed, 1.0) else float("nan")
    return (observed - expected) / (1 - expected)


def fleiss_kappa(ratings: "Sequence[Sequence[str | None]]") -> float:
    """Chance-corrected agreement across *k* repeats of the same items.

    *ratings* is one row per item, each row the ``k`` labels that item received.
    Every row must have the same ``k >= 2``. When every rating everywhere is the
    same label, chance agreement is 1 and kappa is undefined; this returns 1.0 in
    that case (perfect, degenerate) and ``nan`` if agreement is not also perfect.
    """
    rows = [[label(value) for value in row] for row in ratings]
    if not rows:
        return float("nan")
    k = len(rows[0])
    if k < 2 or any(len(row) != k for row in rows):
        raise ValueError("fleiss_kappa needs a constant number of raters, >= 2")

    categories = sorted({value for row in rows for value in row})
    counts = [[row.count(cat) for cat in categories] for row in rows]

    p_item = [(sum(c * c for c in row) - k) / (k * (k - 1)) for row in counts]
    p_bar = sum(p_item) / len(p_item)
    totals = [sum(row[j] for row in counts) for j in range(len(categories))]
    p_cat = [total / (len(rows) * k) for total in totals]
    p_expected = sum(p * p for p in p_cat)

    if math.isclose(p_expected, 1.0):
        return 1.0 if math.isclose(p_bar, 1.0) else float("nan")
    return (p_bar - p_expected) / (1 - p_expected)


def triple_agreement(ratings: "Sequence[Sequence[str | None]]") -> float:
    """Fraction of items where all *k* repeats produced the same label."""
    if not ratings:
        return float("nan")
    return sum(len({label(v) for v in row}) == 1 for row in ratings) / len(ratings)


def youden_j(recall_abstain: float, false_abstain: float) -> float:
    """``recall + specificity - 1``, on the abstention 2x2.

    Abstention recall alone is gamed by always abstaining; subtracting the
    false-abstention rate on the matched grounded controls is what makes the
    number mean anything.
    """
    return recall_abstain + (1.0 - false_abstain) - 1.0


# --------------------------------------------------------------------------- #
# Distributional shape
# --------------------------------------------------------------------------- #


def shares(categories: "Iterable[str | None]") -> "dict[str, float]":
    """Normalized per-category shares of a labelling."""
    counts: "dict[str, int]" = {}
    for category in categories:
        counts[label(category)] = counts.get(label(category), 0) + 1
    total = sum(counts.values())
    if not total:
        return {}
    return {key: value / total for key, value in sorted(counts.items())}


def total_variation(a: "Mapping[str, float]", b: "Mapping[str, float]") -> float:
    """Total-variation distance between two share vectors: one scalar for shape."""
    keys = set(a) | set(b)
    return 0.5 * sum(abs(a.get(key, 0.0) - b.get(key, 0.0)) for key in keys)


def _ranks(values: "Sequence[float]") -> "list[float]":
    """1-based ranks, ties averaged."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        stop = start
        while stop + 1 < len(order) and values[order[stop + 1]] == values[order[start]]:
            stop += 1
        average = (start + stop) / 2 + 1
        for index in range(start, stop + 1):
            ranks[order[index]] = average
        start = stop + 1
    return ranks


def pearson(a: "Sequence[float]", b: "Sequence[float]") -> float:
    """Pearson correlation; ``nan`` when either side has no variance."""
    n = len(a)
    if n != len(b) or n < 2:
        return float("nan")
    mean_a, mean_b = sum(a) / n, sum(b) / n
    da = [value - mean_a for value in a]
    db = [value - mean_b for value in b]
    denominator = math.sqrt(sum(x * x for x in da) * sum(y * y for y in db))
    if denominator == 0:
        return float("nan")
    return sum(x * y for x, y in zip(da, db)) / denominator


def spearman(a: "Mapping[str, float]", b: "Mapping[str, float]") -> float:
    """Rank correlation over the union of categories, absent counted as 0.

    The report is a ranking, so this is the number that says whether its
    conclusions survive the re-mapping.
    """
    keys = sorted(set(a) | set(b))
    if len(keys) < 2:
        return float("nan")
    return pearson(
        _ranks([a.get(key, 0.0) for key in keys]),
        _ranks([b.get(key, 0.0) for key in keys]),
    )


def top_k_overlap(
    a: "Mapping[str, float]", b: "Mapping[str, float]", k: int = 5
) -> float:
    """Overlap of the two top-*k* category sets.

    Normalized by the **smaller** of the two top sets, not by *k*: with fewer
    than *k* categories in play, dividing by *k* would cap the metric below 1 and
    make the "top-5 unchanged" gate clause unsatisfiable by construction.
    """

    def top(mapping: "Mapping[str, float]") -> "set[str]":
        return {
            key
            for key, _ in sorted(mapping.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
        }

    top_a, top_b = top(a), top(b)
    denominator = min(k, len(top_a), len(top_b))
    if not denominator:
        return float("nan")
    return len(top_a & top_b) / denominator


# --------------------------------------------------------------------------- #
# Blind pairwise win rate
# --------------------------------------------------------------------------- #


class WinRate(BaseModel):
    """The primary gate statistic, with its parts kept visible.

    ``W = 0.5 + 0.5*(g - l)``. The 0.5 ceiling is analytic -- an equally good
    annotator wins half of the blind comparisons -- so the gate carries no
    ceiling-estimation error, and an agent that merely *recalls* the published
    tree produces agreements, which score 0.5 and push W toward the ceiling
    rather than past it.
    """

    n: int
    w: float
    lost: int = Field(description="judge preferred the reference")
    tied: int = Field(description="agreements, plus 'equally defensible'")
    won: int = Field(description="judge preferred the agent")
    lower_bound: float = float("nan")
    upper_bound: float = float("nan")


def win_rate(
    scores: "Sequence[float]",
    *,
    seed: int = DEFAULT_SEED,
    resamples: int = DEFAULT_RESAMPLES,
    alpha: float = 0.05,
) -> WinRate:
    """Aggregate per-item scores in ``{0.0, 0.5, 1.0}`` into :class:`WinRate`."""
    if not scores:
        return WinRate(n=0, w=float("nan"), lost=0, tied=0, won=0)
    low, high = bootstrap_ci(scores, seed=seed, resamples=resamples, alpha=alpha)
    return WinRate(
        n=len(scores),
        w=sum(scores) / len(scores),
        lost=sum(1 for s in scores if s < 0.5),
        tied=sum(1 for s in scores if s == 0.5),
        won=sum(1 for s in scores if s > 0.5),
        lower_bound=lower_bound(scores, seed=seed, resamples=resamples, alpha=alpha),
        upper_bound=high,
    )


def _resample_means(
    values: "Sequence[float]",
    *,
    seed: int,
    resamples: int,
    statistic: "Callable[[Sequence[float]], float]",
) -> "list[float]":
    rng = random.Random(seed)
    n = len(values)
    draws: "list[float]" = []
    for _ in range(resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        draws.append(statistic(sample))
    draws.sort()
    return draws


def _mean(values: "Sequence[float]") -> float:
    return sum(values) / len(values)


def _percentile(sorted_values: "Sequence[float]", q: float) -> float:
    """Linear-interpolated percentile of an already-sorted sequence."""
    if not sorted_values:
        return float("nan")
    position = q * (len(sorted_values) - 1)
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return sorted_values[int(position)]
    weight = position - low
    return sorted_values[low] * (1 - weight) + sorted_values[high] * weight


def bootstrap_ci(
    values: "Sequence[float]",
    *,
    seed: int = DEFAULT_SEED,
    resamples: int = DEFAULT_RESAMPLES,
    alpha: float = 0.05,
    statistic: "Callable[[Sequence[float]], float]" = _mean,
) -> "tuple[float, float]":
    """Two-sided percentile bootstrap interval. Reproducible for a fixed *seed*."""
    if not values:
        return (float("nan"), float("nan"))
    draws = _resample_means(values, seed=seed, resamples=resamples, statistic=statistic)
    return (_percentile(draws, alpha / 2), _percentile(draws, 1 - alpha / 2))


def lower_bound(
    values: "Sequence[float]",
    *,
    seed: int = DEFAULT_SEED,
    resamples: int = DEFAULT_RESAMPLES,
    alpha: float = 0.05,
    statistic: "Callable[[Sequence[float]], float]" = _mean,
) -> float:
    """One-sided ``1 - alpha`` lower confidence bound -- the gate's primary form."""
    if not values:
        return float("nan")
    draws = _resample_means(values, seed=seed, resamples=resamples, statistic=statistic)
    return _percentile(draws, alpha)


# --------------------------------------------------------------------------- #
# Risk-coverage
# --------------------------------------------------------------------------- #


class CoveragePoint(BaseModel):
    coverage: float
    w: float
    n: int
    min_confidence: float


def risk_coverage(
    scored: "Sequence[tuple[float, float]]", *, n_total: int
) -> "list[CoveragePoint]":
    """The risk-coverage curve over ``(score, confidence)`` pairs.

    *n_total* is every item the agent was **asked** about, so abstentions --
    which have no score -- lower coverage without touching W. That is what stops
    abstention from inflating the headline: the gate reads W at a fixed coverage,
    and an agent that answers less than that never reaches the reading point.
    """
    if n_total <= 0:
        return []
    order = sorted(scored, key=lambda pair: (-pair[1], pair[0]))
    curve: "list[CoveragePoint]" = []
    running = 0.0
    for index, (score, confidence) in enumerate(order, start=1):
        running += score
        curve.append(
            CoveragePoint(
                coverage=index / n_total,
                w=running / index,
                n=index,
                min_confidence=confidence,
            )
        )
    return curve


def w_at_coverage(curve: "Sequence[CoveragePoint]", coverage: float = 0.85) -> float:
    """W at the largest curve point not exceeding *coverage*.

    ``nan`` when the agent never reaches that coverage -- an honest "the headline
    is not defined at this abstention rate" rather than a flattering number from
    a small confident subset.
    """
    eligible = [point for point in curve if point.coverage <= coverage + 1e-12]
    if not eligible or not curve or curve[-1].coverage < coverage - 1e-12:
        return float("nan")
    return eligible[-1].w
