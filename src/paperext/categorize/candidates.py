"""Multi-stage candidate retrieval for one extracted name (WS-D D1b-2, #52).

Retrieval — not judgment — is the most likely cause of a bad decision. Measured on
the 1208 unmapped model names of the 2024 corpus against ``models/v0``,
:meth:`Ontology.search` alone returns **nothing at all** for 96.4% of them: it
matches ``query ⊆ node key``, so ``resnet50`` finds no ``resnet`` and
``mobilenetv3large`` finds no ``mobilenet``. Whatever the agent is asked, it cannot
place a name whose neighbourhood it never sees.

So this is a generator with stages, not a wrapper over ``search``:

1. **exact** — the normalization DB, plus any node whose own name is the query.
2. **forward containment** — ``query ⊆ key`` (:meth:`Ontology.search`).
3. **reverse containment** — ``key ⊆ query``. The single highest-value addition:
   it is what finds the *anchors* (``resnet50 → resnet``, ``bits101 → bit``). It is
   also noisy — ``resnet50`` drags in ``sne`` — which is why 4 and 5 exist.
4. **acronym** — an acronym-shaped query matched against the *initials* of
   multi-word candidate names, the idea ported from
   ``ontology_mapping/build_models_tree.py:209-249`` (the code there is dead and
   buggy; only the idea survives).
5. **ranking** — one score per node over the union, so a caller can take the top
   *k* and get a payload that fits.

Ranking is deliberately explainable rather than learned: every candidate carries
the stage and the key that earned it its score, so a retrieval miss can be read off
the payload instead of guessed at. Scores are pure functions of the two strings, so
the same ontology and query always produce the same ordered list — which is what
makes the payload hash in :mod:`paperext.categorize.prompt` mean anything.

:func:`anchor_ids` is the unranked stage 2+3 union, and is what the frozen
anchoring probe in :mod:`paperext.categorize.sampling` strata on. It lives here so
there is one containment rule rather than two that can drift apart; the sealed
splits pin its behaviour.
"""

from __future__ import annotations

import re
from typing import Iterable, Sequence

from pydantic import BaseModel, Field
from rapidfuzz import fuzz

from paperext.analysis.rollup import str_normalize
from paperext.ontology.ontology import Ontology

#: Shortest node key allowed to anchor a longer query by reverse containment.
#: Below this it is noise -- "ml" is a substring of a great many names.
MIN_ANCHOR_LEN = 3

#: Default number of candidates handed to the prompt. Across the 2342 extracted
#: model names the worst raw ``Ontology.search`` returns 159 hits (``AR``), so a
#: bound is mandatory, not a nicety. In practice the ranked, branch-collapsed list
#: averages ~9.
DEFAULT_LIMIT = 20

#: Candidates scoring below this are dropped even if the limit is not reached --
#: a bad candidate costs tokens *and* invites a wrong mapping.
MIN_SCORE = 0.30

#: How many candidates may sit *below* an already-selected candidate. A query like
#: ``BiT-S-101`` matches ``resnet`` and then nine of its children, all of which are
#: already visible as that node's ``children`` -- so they cost slots and tokens and
#: add nothing, while pushing the genuinely different concept off the list. Two is
#: measured: ``0`` costs 1.5pp of parent recall on the dev split (the true parent is
#: sometimes itself under a better-scoring node), ``1`` and up cost nothing.
DEFAULT_MAX_PER_BRANCH = 2

#: Fuzzy similarity is a fallback signal, so it is capped below the weakest
#: containment score: a real substring anchor always outranks a near-miss.
_FUZZY_CEILING = 0.50

#: A query is "acronym-shaped" when it is short and unspaced, following
#: ``is_probably_an_acronym`` in the legacy builder.
_ACRONYM_MAX_LEN = 5

_WORD = re.compile(r"[0-9]+|[^\W\d_]+")


class Candidate(BaseModel):
    """One retrieved node, with the evidence that retrieved it."""

    node_id: str
    score: float = Field(ge=0.0, le=1.0)
    #: Retrieval stage that produced the winning score.
    stage: str
    #: The node key (normalized name or surface) the score was computed against.
    key: str
    #: The query or alias that matched, when it was not the primary surface.
    via: str


def normalized_keys(onto: Ontology) -> "dict[str, list[str]]":
    """node id -> its normalized name plus its (already normalized) surfaces."""
    keys: "dict[str, list[str]]" = {}
    for node_id, node in onto.nodes.items():
        keys[node_id] = [str_normalize(node.name), *onto.surfaces(node_id)]
    return keys


def initials(name: str) -> str:
    """Normalized initials of a multi-word *name* (``"vision transformer" -> "vt"``).

    Empty for a single-word name: matching a one-word name's single initial against
    a query would fire on every name starting with the same letter.
    """
    words = _WORD.findall(name)
    if len(words) < 2:
        return ""
    return str_normalize("".join(word[0] for word in words))


def is_acronym_shaped(query: str) -> bool:
    """Whether *query* looks like an acronym rather than a spelled-out name."""
    return 0 < len(query.strip()) <= _ACRONYM_MAX_LEN and " " not in query.strip()


def anchor_ids(
    onto: Ontology,
    query: str,
    *,
    keys: "dict[str, list[str]] | None" = None,
) -> "set[str]":
    """Unranked containment hits for *query*: stage 2 (forward) + stage 3 (reverse).

    The baseline retrieval the sealed splits are stratified on
    (:func:`paperext.categorize.sampling.anchoring`). Ranking, exact resolution and
    acronym expansion are deliberately *not* included: the strata must keep meaning
    the same thing as retrieval improves, or a sealed manifest stops describing the
    splits it names.
    """
    q = str_normalize(query)
    if not q:
        return set()
    keys = keys if keys is not None else normalized_keys(onto)
    hits = set(onto.search(query))
    for node_id, node_keys in keys.items():
        if node_id in hits:
            continue
        if any(len(k) >= MIN_ANCHOR_LEN and k != q and k in q for k in node_keys):
            hits.add(node_id)
    return hits


def _containment_score(q: str, key: str) -> "tuple[float, str] | None":
    """Score *key* against query *q* by containment, or ``None`` if neither way.

    Coverage — how much of the longer string the shorter one accounts for — is what
    separates a real anchor from an accident: for ``resnet50``, ``resnet`` covers
    6/8 and ``sne`` covers 3/8.
    """
    if key == q:
        return 1.0, "exact"
    if len(key) >= MIN_ANCHOR_LEN and key in q:
        return 0.55 + 0.35 * (len(key) / len(q)), "reverse"
    if len(q) >= MIN_ANCHOR_LEN and q in key:
        return 0.55 + 0.35 * (len(q) / len(key)), "forward"
    return None


def _score_node(
    onto: Ontology,
    node_id: str,
    node_keys: "Sequence[str]",
    q: str,
    *,
    acronym: bool,
) -> "tuple[float, str, str]":
    """Best ``(score, stage, key)`` for one node against one normalized query."""
    best = (0.0, "none", "")

    for key in node_keys:
        if not key:
            continue
        scored = _containment_score(q, key)
        if scored is not None and scored[0] > best[0]:
            best = (scored[0], scored[1], key)

    if acronym:
        acro = initials(onto.name(node_id))
        if acro and acro == q and best[0] < 0.90:
            best = (0.90, "acronym", acro)

    if best[0] < _FUZZY_CEILING:
        for key in node_keys:
            if not key:
                continue
            sim = fuzz.ratio(q, key) / 100.0 * _FUZZY_CEILING
            if sim > best[0]:
                best = (sim, "fuzzy", key)

    return best


def generate(
    onto: Ontology,
    query: str,
    *,
    aliases: Iterable[str] = (),
    limit: "int | None" = DEFAULT_LIMIT,
    min_score: float = MIN_SCORE,
    max_per_branch: "int | None" = DEFAULT_MAX_PER_BRANCH,
    keys: "dict[str, list[str]] | None" = None,
) -> "list[Candidate]":
    """Ranked candidate nodes for *query* (and its *aliases*), best first.

    Each alias is scored as its own query and a node keeps its best result, so an
    entity whose primary name retrieves nothing can still be placed through an
    alias — ``BiT-S-101`` retrieves through ``BiT ResNet``.

    Ties break on DFS order, so the list is a pure function of the ontology and the
    query strings: two runs with the same inputs produce byte-identical payloads.

    *limit* is a hard cap because the worst model query matches 159 nodes; pass
    ``None`` for the full ranked list (a caller that wants to report how much it
    truncated).
    """
    keys = keys if keys is not None else normalized_keys(onto)

    queries: "list[tuple[str, str]]" = []  # (normalized query, raw form it came from)
    for raw in (query, *aliases):
        norm = str_normalize(raw)
        if norm and all(norm != seen for seen, _ in queries):
            queries.append((norm, raw))
    if not queries:
        return []

    order = {node_id: i for i, (node_id, _, _) in enumerate(onto.iter_nodes())}
    best: "dict[str, tuple[float, str, str, str]]" = {}

    for norm, raw in queries:
        acronym = is_acronym_shaped(raw)
        for node_id, node_keys in keys.items():
            score, stage, key = _score_node(
                onto, node_id, node_keys, norm, acronym=acronym
            )
            if score < min_score:
                continue
            current = best.get(node_id)
            if current is None or score > current[0]:
                best[node_id] = (score, stage, key, raw)

    ranked = sorted(
        best.items(),
        key=lambda item: (-item[1][0], order.get(item[0], len(order)), item[0]),
    )

    out: "list[Candidate]" = []
    below: "dict[str, int]" = {}
    for node_id, (score, stage, key, via) in ranked:
        if max_per_branch is not None:
            ancestors = set(onto.ancestry(node_id)[:-1])
            owner = next((c.node_id for c in out if c.node_id in ancestors), None)
            if owner is not None:
                if below.get(owner, 0) >= max_per_branch:
                    continue
                below[owner] = below.get(owner, 0) + 1
        out.append(
            Candidate(
                node_id=node_id, score=round(score, 6), stage=stage, key=key, via=via
            )
        )
        if limit is not None and len(out) >= limit:
            break
    return out


#: Depth down to which every node joins the skeleton, whether or not it has
#: children. See :func:`skeleton_ids`.
DEFAULT_SKELETON_DEPTH = 2


def skeleton_ids(
    onto: Ontology,
    *,
    max_depth: int = DEFAULT_SKELETON_DEPTH,
) -> "set[str]":
    """The taxonomy's shape: every node down to *max_depth*, plus every node with
    children.

    **Ranked retrieval is not enough, and no amount of string matching would be.**
    Measured on the sealed ``dev`` split (200 held-out model names, each decided
    against its own ablated copy), the true parent is in the top 10 candidates for
    only 37.5% of items — and of the misses, 94 out of 125 have their true parent
    at *depth 2*: ``optimizer``, ``reinforcement learning``, ``other algorithms``,
    ``transformer``. Those are semantic placements. Nothing about the string
    ``vicreg`` points at ``optimizer``; retrieval cannot find it, and improving the
    matcher cannot either.

    What fixes it is giving the model the tree's shape as standing context. With
    this skeleton in the payload the true parent is present for **96.5%** of dev
    items, for ~433 nodes / ~19k characters on ``models/v0``:

    ===========================  =====  =============================
    payload context              nodes  parent present (dev, n=200)
    ===========================  =====  =============================
    roots only                       5  0.425
    ``max_depth=2`` only           219  0.895
    nodes with children only       273  0.960
    **this** (union)               433  0.965
    everything to depth 3          979  0.970
    ===========================  =====  =============================

    The skeleton is also the *shared prefix* the cost note in #52 is about: it is
    identical across items of a run, so it is cached rather than re-billed. (Under
    the #53 leave-one-out protocol it shifts for the items whose held-out node was
    itself in the skeleton, which is a property of the eval, not of the payload.)
    """
    if max_depth < 0:
        raise ValueError(f"max_depth must be >= 0, got {max_depth}")
    ids = {node_id for node_id in onto.nodes if onto.children(node_id)}
    for node_id, _, raw_path in onto.iter_nodes():
        if len(raw_path) <= max_depth:
            ids.add(node_id)
    return ids
