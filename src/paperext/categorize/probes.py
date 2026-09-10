"""Reference-free control sets (WS-D D1b-3, #53).

Everything here has a **known-correct answer that does not come from the legacy
tree**, so none of it inherits the reference's subjectivity. That is what makes
these clauses of the gate hard pass/fail while the win rate needs a judge.

Four families, plus a canary:

- **No-op control** -- already-mapped names, *not* ablated. The tree already says
  where they go, so the correct behaviour is to change nothing. This is the probe
  that catches an agent that churns the tree for the sake of answering.
- **Policy conformance** -- alias pairs the corpus itself declares. The locked
  granularity policy fixes the answer: a size/variant qualifier (``ResNet`` ->
  ``ResNet-50``) is a **child node**; a form the entity's own display name
  declares to be the same thing (``Vision Transformer`` for ``ViT (Vision
  Transformer)``, or a plural) is a **surface**. Pairs whose short form is an
  ambiguous acronym are dropped -- the point of the probe is that the answer is
  not arguable.
- **Ambiguity 2x2** -- the natural collisions are far too few (4 in models), so
  they are constructed: acronym items with their grounding stripped (correct =
  abstain), *the same items with grounding* (correct = resolve), and injected
  homonyms (correct = abstain). The matched grounded arm is mandatory: abstention
  recall on its own is maximized by always abstaining, which is why the score is
  Youden's J and not a recall.
- **Memorization canary** -- ``data/categorized_models.json`` sits in a public
  repo, so it may be in the pinned model's training data. Probing for its
  structure out-of-band is five minutes and decisive; if it fires, every
  raw-agreement number is void and only the win rate and these probes count.

Case construction is deterministic given a seed and takes no API calls; running
the cases is :mod:`paperext.categorize.evaluate`'s job.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path
from typing import Any, Iterable, Sequence, Union

from pydantic import BaseModel, Field

from paperext.analysis.rollup import str_normalize
from paperext.categorize.ablate import ablatable, copy_ontology, name_matches
from paperext.categorize.actions import OPS, AddSurface, CreateNode, Outcome
from paperext.categorize.apply import DecisionRecord
from paperext.categorize.candidates import is_acronym_shaped
from paperext.categorize.items import Item, Mention
from paperext.ontology.ontology import Ontology

#: Size / variant suffixes that make the longer form a *child* of the shorter one.
#: Deliberately narrow: a remainder outside this set (``RoBERTa`` vs ``ROB``,
#: ``Transformer`` vs ``Transformer model``) is not a qualification and is dropped.
QUALIFIER = re.compile(
    r"^(?:\d+[a-z]?|v\d+|base|large|small|tiny|mini|huge|xl|xxl|xs)$"
)

#: ``Long Form (ACRONYM)`` -- a display name that declares two spellings of one thing.
PAREN = re.compile(r"^(.*?)\s*\(([^()]+)\)\s*$")

#: Shortest form that may anchor a policy pair; below this the containment is noise.
MIN_BASE_LEN = 3

#: Ops that delete or relocate someone else's data. A control-set decision must
#: not reach for these at all.
DESTRUCTIVE = frozenset(op for op, spec in OPS.items() if spec.dangerous)


class ProbeCase(BaseModel):
    """One control item and the answer that is correct by construction."""

    kind: str = Field(
        description="noop | child | surface | ambiguous | grounded | homonym"
    )
    surface: str = Field(description="The name the agent is asked about")
    expect: str = Field(description="noop | child | surface | abstain | resolve")
    base: str = Field(
        default="", description="Policy pairs: the form that must receive"
    )
    base_id: str = Field(default="", description="Node the base form resolves to")
    note: str = ""


# --------------------------------------------------------------------------- #
# No-op control
# --------------------------------------------------------------------------- #


def noop_cases(
    surfaces: "Sequence[str]", *, n: int = 100, seed: int = 42
) -> "list[ProbeCase]":
    """Sample *n* already-mapped names to be shown against an **un-ablated** tree.

    Draw these from ``reserve``: dev is iterated on and gate is sealed, and a
    control that overlaps either would stop being independent of them.
    """
    rng = random.Random(seed)
    pool = sorted(set(surfaces))
    picked = pool if len(pool) <= n else rng.sample(pool, n)
    return [
        ProbeCase(kind="noop", surface=surface, expect="noop")
        for surface in sorted(picked)
    ]


def is_noop(record: DecisionRecord) -> bool:
    """Whether a decision left the mapping alone.

    Judged on the *actions*, not on the declared outcome: a decision that claims
    ``no_op`` while emitting a ``move`` is churn whatever it calls itself.
    ``update_description`` is allowed -- ``v0`` has no descriptions at all, so
    writing one is a genuine improvement rather than churn.
    """
    return not any(
        action.op != "update_description" for action in record.decision.actions
    )


def destructive_ops(
    record: DecisionRecord, allowed: "Iterable[str]" = ()
) -> "list[str]":
    """Destructive actions aimed at a node outside *allowed*.

    *allowed* is the candidate set the agent was shown: deleting a node it was
    never offered means it reached outside its evidence, which is the failure
    mode this clause exists for.
    """
    permitted = set(allowed)
    hits: "list[str]" = []
    for action in record.decision.actions:
        if action.op not in DESTRUCTIVE:
            continue
        target = getattr(action, "node_id", "")
        if target not in permitted:
            hits.append(f"{action.op}({target})")
    return hits


# --------------------------------------------------------------------------- #
# Policy conformance
# --------------------------------------------------------------------------- #


def _declared_forms(item: Item) -> "set[str]":
    """The spellings an item's own display name declares to be the same thing."""
    match = PAREN.match(item.name)
    if not match:
        return set()
    return {str_normalize(match.group(1)), str_normalize(match.group(2))} - {
        "",
        str_normalize(item.surface),
    }


def _ambiguous(onto: Ontology, surface: str) -> bool:
    """Whether *surface* names more than one node -- a real collision, not a variant."""
    return len(name_matches(onto, surface)) > 1


def policy_cases(
    onto: Ontology,
    items: "Sequence[Item]",
    *,
    limit: "int | None" = None,
    seed: int = 42,
) -> "list[ProbeCase]":
    """Derive child-node and surface cases from the corpus's own alias pairs.

    A case survives only when the *base* form resolves in *onto* (so there is
    something to attach to), the target is ablatable, and neither form is an
    ambiguous acronym.
    """
    child: "list[ProbeCase]" = []
    surface: "list[ProbeCase]" = []
    seen: "set[tuple[str, str]]" = set()

    for item in items:
        base_norm = str_normalize(item.surface)
        declared = _declared_forms(item)
        for alias in item.aliases:
            alias_norm = str_normalize(alias)
            if not alias_norm or alias_norm == base_norm:
                continue
            key = (base_norm, alias_norm)
            if key in seen:
                continue
            seen.add(key)

            forms = declared | {base_norm}
            plural = any(
                alias_norm == form + "s" or form == alias_norm + "s" for form in forms
            )
            if alias_norm in declared or plural:
                case = _surface_case(onto, item, alias_norm, base_norm, declared)
                if case is not None:
                    surface.append(case)
                continue

            short, long = sorted((base_norm, alias_norm), key=len)
            if len(short) < MIN_BASE_LEN or not long.startswith(short):
                continue
            if not QUALIFIER.match(long[len(short) :]):
                continue
            case = _child_case(onto, short, long)
            if case is not None:
                child.append(case)

    return _cap(child, limit, seed) + _cap(surface, limit, seed)


def _child_case(onto: Ontology, short: str, long: str) -> "ProbeCase | None":
    base_id = onto.resolve(short)
    if base_id is None or _ambiguous(onto, short):
        return None
    if onto.resolve(long) is not None and not ablatable(onto, long):
        return None
    return ProbeCase(
        kind="child",
        surface=long,
        expect="child",
        base=short,
        base_id=base_id,
        note=f"{long!r} qualifies {short!r}; the policy says child node",
    )


def _surface_case(
    onto: Ontology,
    item: Item,
    alias_norm: str,
    base_norm: str,
    declared: "set[str]",
) -> "ProbeCase | None":
    """The alias is another spelling of the same entity; it must become a surface."""
    for candidate in (base_norm, *sorted(declared)):
        if candidate == alias_norm:
            continue
        base_id = onto.resolve(candidate)
        if base_id is None or _ambiguous(onto, candidate):
            continue
        if _ambiguous(onto, alias_norm):
            return None
        if onto.resolve(alias_norm) is not None and not ablatable(onto, alias_norm):
            return None
        return ProbeCase(
            kind="surface",
            surface=alias_norm,
            expect="surface",
            base=candidate,
            base_id=base_id,
            note=f"{item.name!r} declares {alias_norm!r} and {candidate!r} to be one thing",
        )
    return None


def _cap(cases: "list[ProbeCase]", limit: "int | None", seed: int) -> "list[ProbeCase]":
    if limit is None or len(cases) <= limit:
        return cases
    return sorted(
        random.Random(seed).sample(cases, limit), key=lambda case: case.surface
    )


def score_policy(
    cases: "Sequence[ProbeCase]", records: "Sequence[DecisionRecord]"
) -> "dict[str, Any]":
    """Conformance rate overall and per kind. *records* align with *cases*."""
    per_kind: "dict[str, list[bool]]" = {}
    misses: "list[str]" = []
    for case, record in zip(cases, records):
        ok = _policy_ok(case, record)
        per_kind.setdefault(case.kind, []).append(ok)
        if not ok:
            misses.append(
                f"{case.surface} ({case.kind}, got {record.decision.outcome.value})"
            )
    flat = [ok for hits in per_kind.values() for ok in hits]
    return {
        "n": len(flat),
        "conformance": (sum(flat) / len(flat)) if flat else float("nan"),
        "per_kind": {
            kind: {"n": len(hits), "rate": sum(hits) / len(hits)}
            for kind, hits in sorted(per_kind.items())
        },
        "misses": misses,
    }


def _policy_ok(case: ProbeCase, record: DecisionRecord) -> bool:
    """Did the decision attach *case.surface* the way the policy requires?"""
    want = str_normalize(case.surface)
    target: "str | None" = None
    for action in record.decision.actions:
        if isinstance(action, AddSurface) and str_normalize(action.surface) == want:
            target = action.canonical
    if target is None:
        return False

    created = {
        action.node_id: action
        for action in record.decision.actions
        if isinstance(action, CreateNode)
    }
    if case.expect == "surface":
        # same node as the base form, and nothing new invented for it
        return target == case.base_id and target not in created
    new = created.get(target)
    return new is not None and new.parent == case.base_id


# --------------------------------------------------------------------------- #
# Ambiguity 2x2
# --------------------------------------------------------------------------- #


def strip_grounding(item: Item) -> Item:
    """The same item with every textual clue removed -- name and paper id only.

    What is left cannot settle an ambiguous acronym, which is the point: the
    correct answer becomes "abstain" by construction rather than by opinion.
    """
    return item.model_copy(
        update={
            "mentions": [
                Mention(
                    paper=mention.paper,
                    spelling=mention.spelling,
                    aliases=[],
                    co_occurring=[],
                )
                for mention in item.mentions
            ],
            "aliases": [],
        }
    )


def acronym_items(
    onto: Ontology,
    items: "Sequence[Item]",
    *,
    n: int = 40,
    seed: int = 42,
) -> "list[Item]":
    """Acronym-shaped corpus items that the tree currently resolves **uniquely**.

    Deliberately *not* selected by tree ambiguity. ``Ontology.search`` is
    substring-only, so "ambiguous" by that measure means ``bert`` matching
    ``hubert`` and ``art`` matching ``stuart-landau`` -- accidents of spelling,
    not homonyms. Asking the agent to abstain on those would be asking it to be
    wrong, and the false-abstention arm would then measure the opposite of what
    it claims.

    So the ambiguity is **injected** (:func:`inject_homonym`) rather than found,
    and this returns the items to inject it into: one clear referent today, an
    acronym shape, and at least one quote so there is grounding to strip.
    """
    picked: "list[Item]" = []
    for item in items:
        if not is_acronym_shaped(item.surface):
            continue
        if not any(mention.quote for mention in item.mentions):
            continue  # nothing to strip
        node_id = onto.resolve(item.surface)
        if node_id is None or len(name_matches(onto, item.surface)) > 1:
            continue
        if not ablatable(onto, item.surface):
            continue
        picked.append(item)
    if len(picked) <= n:
        return picked
    return sorted(random.Random(seed).sample(picked, n), key=lambda item: item.surface)


def branch_of(onto: Ontology, node_id: str, *, depth: int = 2) -> "str | None":
    """The depth-*depth* ancestor of a node, or ``None`` if it is shallower."""
    ancestry = onto.ancestry(node_id)
    return ancestry[depth - 1] if len(ancestry) >= depth else None


def inject_homonym(
    onto: Ontology, name: str, parents: "Sequence[str]", *, node_ids: "Sequence[str]"
) -> Ontology:
    """A copy of *onto* carrying *name* as a node under **each** of *parents*.

    Two nodes, one name, different branches -- the shape of the real ``sam`` /
    ``bit`` collisions, built on demand because there are only four natural ones.
    Neither copy gets a description, so nothing but the paper evidence can tell
    them apart: with the grounding stripped, abstention is correct by
    construction rather than by opinion.
    """
    if len(parents) != len(node_ids):
        raise ValueError("parents and node_ids must line up")
    scratch = copy_ontology(onto)
    for parent, node_id in zip(parents, node_ids):
        scratch.create_node(node_id, name, parent=parent)
    scratch.check_invariants()
    return scratch


def abstained(record: DecisionRecord) -> bool:
    """Abstention as the policy defines it: outcome *and* a note saying why."""
    return record.decision.outcome is Outcome.ABSTAINED and bool(
        record.decision.review_notes or record.decision.unresolved
    )


def score_ambiguity(
    should_abstain: "Sequence[DecisionRecord]",
    should_resolve: "Sequence[DecisionRecord]",
    stripped_only: "Sequence[DecisionRecord]" = (),
) -> "dict[str, Any]":
    """Youden's J over the abstention 2x2, on matched items.

    ``J = recall_abstain + (1 - false_abstain) - 1``: 0 for both degenerate
    strategies (always abstain, never abstain), 1 only for an agent that abstains
    exactly when the question is not answerable.

    The two gated arms are the **same items** under two conditions -- injected
    homonym with the grounding stripped (answer: abstain) and the tree as it
    stands with the grounding intact (answer: resolve) -- so J is not confounded
    by which names were picked.

    *stripped_only* is a third, ungated cell: the same items with grounding
    stripped but **no** injected homonym. It separates "abstains because the
    question is genuinely ambiguous" from "abstains because it was given no
    quotes", which is a different failure and worth seeing.
    """
    from paperext.categorize.metrics import youden_j

    recall = (
        sum(abstained(record) for record in should_abstain) / len(should_abstain)
        if should_abstain
        else float("nan")
    )
    false_rate = (
        sum(abstained(record) for record in should_resolve) / len(should_resolve)
        if should_resolve
        else float("nan")
    )
    scores = {
        "n_should_abstain": len(should_abstain),
        "n_should_resolve": len(should_resolve),
        "recall_abstain": recall,
        "false_abstain": false_rate,
        "youden_j": youden_j(recall, false_rate),
    }
    if stripped_only:
        scores["abstain_no_grounding_only"] = sum(
            abstained(record) for record in stripped_only
        ) / len(stripped_only)
    return scores


# --------------------------------------------------------------------------- #
# Memorization canary
# --------------------------------------------------------------------------- #


CANARY_PREAMBLE = (
    "This is a recall question about a public GitHub repository, not a reasoning "
    "task. Answer from memory only; if you do not remember, say so rather than "
    "guessing from the names."
)


class CanaryProbe(BaseModel):
    """One recall question about the published reference file, and its true answer."""

    question: str
    expected: "list[str]"


class CanaryAnswer(BaseModel):
    """What the pinned model says it remembers -- reason before value, as usual."""

    reason: str = Field(default="", description="How you know, in one sentence")
    remembered: bool = Field(
        description="True if you actually recall the file, False if you are guessing"
    )
    keys: "list[str]" = Field(
        default_factory=list, description="The keys, exactly as they appear in the file"
    )


def canary_probes(
    path: "Union[str, Path]" = "data/categorized_models.json",
    *,
    repo: str = "satyaog/paperext",
    branches: int = 3,
) -> "list[CanaryProbe]":
    """Questions whose answers are only knowable by having seen the file.

    Deliberately structural: the top-level keys, then the children of the largest
    branches. A model that reconstructs these has the reference memorized, and
    every raw-agreement number measures recall rather than judgment.
    """
    data: "dict[str, Any]" = json.loads(Path(path).read_text(encoding="utf-8"))
    location = f"{repo}, file {Path(path).as_posix()}"
    probes = [
        CanaryProbe(
            question=(
                f"{CANARY_PREAMBLE}\n\nIn the repository {location}, the JSON is a "
                "nested tree of model categories. List its top-level keys exactly."
            ),
            expected=sorted(data),
        )
    ]
    biggest = sorted(data, key=lambda key: -len(data[key]))[:branches]
    for key in biggest:
        probes.append(
            CanaryProbe(
                question=(
                    f"{CANARY_PREAMBLE}\n\nIn the same file, list the keys directly "
                    f"under the top-level key {key!r}."
                ),
                expected=sorted(data[key]),
            )
        )
    return probes


def score_canary(probe: CanaryProbe, answer: "Iterable[str]") -> float:
    """Recall of the true keys in *answer*, compared after normalization."""
    want = {str_normalize(key) for key in probe.expected}
    got = {str_normalize(key) for key in answer}
    if not want:
        return float("nan")
    return len(want & got) / len(want)


def canary_fired(scores: "Sequence[float]", *, threshold: float = 0.5) -> bool:
    """Whether recall is high enough that the reference must be assumed memorized."""
    usable = [score for score in scores if score == score]  # drop nan
    if not usable:
        return False
    return max(usable) >= threshold
