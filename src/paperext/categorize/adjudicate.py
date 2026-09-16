"""Blind pairwise adjudication of two placements (WS-D D1b-3, #53).

The gate's primary metric is a **win rate against the legacy tree**, and the only
way that number means anything is if whoever judges it cannot tell which side is
the legacy one. So the judge sees the paper evidence and two anonymized ancestor
paths in randomized order, and nothing else -- no node ids, no version labels, no
"reference"/"agent" wording anywhere in the rendered text.

Three properties this module has to hold up, because W is unfounded without them:

**Order-blindness is structural, not promised.** :func:`swap` mirrors a pair, and
:func:`render_pair` of the mirror is the original with the two option blocks
exchanged -- checked by a test rather than asserted in prose. Which side the agent
is on lives in :attr:`Pair.agent_option`, which is never rendered.

**The cache key is the semantic pair, not the A/B draw.** ``sha256(item_id ||
reference || agent)``, so re-running with a different shuffle seed reuses every
verdict, and a prompt tweak that changes 40 of 300 decisions costs 40
adjudications rather than 300.

**Agreements never reach the judge.** Identical placements are a tie by
definition and score 0.5; :func:`make_pair` returns ``None`` for them. That is why
adjudication cost scales with disagreements rather than with the sample size.

The judge must be a **different vendor** from the agent (``[categorize]
judge_platform``): a same-family judge preferring its own output would bias W
upward, which is the one direction that matters.

Note one residual confound, since it is better written down than discovered: when
the agent *creates* a node, both options render the item's own display name as the
leaf, so only the parent chains differ. When the agent instead maps onto an
existing node, that node's own name is the answer and is rendered as such -- the
paths then legitimately differ in shape, and a judge could in principle read
something into that. It cannot read *which side is legacy* from it, which is the
property W depends on.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
from pathlib import Path
from typing import Any, Awaitable, Callable, Literal, Sequence, Union

import instructor
from pydantic import BaseModel, Field

from paperext.categorize.placement import Placement

logger = logging.getLogger(__name__)

#: Judge verdicts, as the judge may express them.
Choice = Literal["A", "B", "tie"]

JUDGE_POLICY = """\
You are adjudicating where a machine-learning entity belongs in a taxonomy.

You are given the entity, the evidence extracted from the papers that mention it, \
and two proposed placements written as root-to-leaf paths. Decide which placement \
a careful expert would defend.

Rules:

1. Judge the placement, not the wording. A path is better when the entity really \
   is a kind of each node above it, and when the deepest node is the most specific \
   true statement the taxonomy supports.
2. A placement that is correct but shallower than another correct one is slightly \
   worse, not wrong. A placement under the wrong branch is wrong however deep it is.
3. Use the evidence. If a quote says what the thing actually is, that outranks what \
   its name looks like.
4. Answer "tie" when both are defensible, when the difference is a matter of taste, \
   or when the evidence does not settle it. "tie" is a real answer and is expected \
   often; do not break ties to seem decisive.
5. You are not told where either placement came from, and there is no pattern to \
   find. Judge each pair on its own.

Give your reasoning first, then the choice.\
"""


class Pair(BaseModel):
    """One blind comparison. ``agent_option`` is bookkeeping and is never rendered."""

    item_id: str
    name: str
    key: str
    evidence: str
    option_a: str
    option_b: str
    agent_option: Literal["A", "B"]


class JudgeChoice(BaseModel):
    """The judge's structured answer -- reason before value, per the repo idiom."""

    reason: str = Field(description="Why, in one or two sentences")
    choice: Choice = Field(
        description="'A' or 'B' for the better placement, 'tie' if equally defensible"
    )


class Verdict(BaseModel):
    """A judged pair, keyed so it can be cached and replayed."""

    key: str
    choice: Choice
    reason: str = ""
    judge: str = ""


#: A judge takes a rendered pair and returns its choice. Async so the real one can
#: be an API call and the test one cannot tell the difference.
Judge = Callable[[Pair], Awaitable[JudgeChoice]]


def render_placement(placement: Placement, *, leaf: str) -> str:
    """A placement as an anonymized ``root > ... > leaf`` path.

    A placement that creates a node renders the item's own display name as the
    leaf, so a proposed-name difference cannot stand in for a placement
    difference. A placement onto an existing node renders that node's name,
    because "it *is* that thing" is the answer being judged.
    """
    names = list(placement.ancestor_names)
    if placement.node_id is None and names:
        names[-1] = leaf
    return " > ".join(names)


def pair_key(item_id: str, reference: str, agent: str) -> str:
    """``sha256(item_id || reference || agent)`` -- stable across A/B shuffles."""
    digest = hashlib.sha256()
    for part in (item_id, reference, agent):
        digest.update(part.encode("utf-8"))
        digest.update(b"\x00")
    return digest.hexdigest()


def make_pair(
    item_id: str,
    name: str,
    evidence: str,
    reference: str,
    agent: str,
    *,
    rng: random.Random,
) -> "Pair | None":
    """Build a blind pair, or ``None`` when the two placements are identical.

    An agreement is a tie by definition and needs no judge at all.
    """
    if reference == agent:
        return None
    agent_first = rng.random() < 0.5
    return Pair(
        item_id=item_id,
        name=name,
        key=pair_key(item_id, reference, agent),
        evidence=evidence,
        option_a=agent if agent_first else reference,
        option_b=reference if agent_first else agent,
        agent_option="A" if agent_first else "B",
    )


def swap(pair: Pair) -> Pair:
    """The same comparison with the options exchanged. Same key, mirrored sides."""
    return pair.model_copy(
        update={
            "option_a": pair.option_b,
            "option_b": pair.option_a,
            "agent_option": "B" if pair.agent_option == "A" else "A",
        }
    )


def render_pair(pair: Pair) -> str:
    """The judge's user message. Symmetric in A and B by construction."""
    return "\n".join(
        [
            pair.evidence,
            "",
            "## PLACEMENT A",
            "",
            pair.option_a,
            "",
            "## PLACEMENT B",
            "",
            pair.option_b,
            "",
            "## TASK",
            "",
            f"Which placement is better for {pair.name}? Answer A, B, or tie.",
        ]
    )


def judge_messages(pair: Pair) -> "list[dict[str, str]]":
    return [
        {"role": "system", "content": JUDGE_POLICY},
        {"role": "user", "content": render_pair(pair)},
    ]


def score_pair(pair: Pair, verdict: Verdict) -> float:
    """1.0 the agent won, 0.0 the reference won, 0.5 a tie."""
    if verdict.choice == "tie":
        return 0.5
    return 1.0 if verdict.choice == pair.agent_option else 0.0


def preferred(pair: Pair, verdict: Verdict) -> str:
    """``'agent'`` / ``'reference'`` / ``'tie'`` -- the side-independent verdict."""
    if verdict.choice == "tie":
        return "tie"
    return "agent" if verdict.choice == pair.agent_option else "reference"


def order_swap_consistency(
    pairs: "Sequence[Pair]",
    verdicts: "Sequence[Verdict]",
    swapped_verdicts: "Sequence[Verdict]",
) -> float:
    """Fraction of duplicated pairs the judge decided the same way both ways round.

    Below ~0.80 the judge is reading position rather than content, and every W
    computed from it is noise dressed as a measurement.
    """
    if not pairs:
        return float("nan")
    agree = 0
    for pair, first, second in zip(pairs, verdicts, swapped_verdicts):
        if preferred(pair, first) == preferred(swap(pair), second):
            agree += 1
    return agree / len(pairs)


def pro_agent_rate(pairs: "Sequence[Pair]", verdicts: "Sequence[Verdict]") -> float:
    """Share of judged pairs decided for the agent -- ties excluded from the top.

    Compared against the same rate on the human-audited subset: if the judge runs
    more than ~8 points hotter than the human, fall back to human adjudication.
    """
    if not pairs:
        return float("nan")
    return sum(preferred(p, v) == "agent" for p, v in zip(pairs, verdicts)) / len(pairs)


# --------------------------------------------------------------------------- #
# Verdict cache
# --------------------------------------------------------------------------- #


class VerdictCache:
    """Append-only jsonl of verdicts, keyed by :func:`pair_key`.

    Keeps agent revisions cheap: only pairs whose *placements* changed are new.
    """

    def __init__(self, path: "Union[str, Path, None]" = None) -> None:
        self.path = Path(path) if path is not None else None
        self._by_key: "dict[str, Verdict]" = {}
        if self.path is not None and self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    verdict = Verdict.model_validate_json(line)
                    self._by_key[verdict.key] = verdict

    def get(self, key: str) -> "Verdict | None":
        return self._by_key.get(key)

    def put(self, verdict: Verdict) -> None:
        self._by_key[verdict.key] = verdict
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(verdict.model_dump_json() + "\n")

    def __len__(self) -> int:
        return len(self._by_key)

    def __contains__(self, key: object) -> bool:
        return key in self._by_key


async def adjudicate(
    pairs: "Sequence[Pair]",
    judge: Judge,
    *,
    cache: "VerdictCache | None" = None,
    concurrency: int = 4,
    judge_name: str = "",
) -> "list[Verdict]":
    """Judge every pair, reusing cached verdicts. Order of the result matches *pairs*.

    Note the cache is keyed by the semantic pair, so two items that happen to pose
    the identical comparison are judged once.
    """
    semaphore = asyncio.Semaphore(max(1, concurrency))
    results: "list[Verdict | None]" = [None] * len(pairs)
    todo: "list[int]" = []

    for index, pair in enumerate(pairs):
        hit = cache.get(pair.key) if cache is not None else None
        if hit is not None:
            results[index] = hit
        else:
            todo.append(index)

    async def one(index: int) -> None:
        async with semaphore:
            choice = await judge(pairs[index])
        results[index] = Verdict(
            key=pairs[index].key,
            choice=choice.choice,
            reason=choice.reason,
            judge=judge_name,
        )

    await asyncio.gather(*(one(index) for index in todo))

    fresh = set(todo)
    verdicts: "list[Verdict]" = []
    for index, result in enumerate(results):
        assert result is not None  # every index is either cached or judged
        if cache is not None and index in fresh:
            cache.put(result)
        verdicts.append(result)
    return verdicts


# --------------------------------------------------------------------------- #
# The live judge
# --------------------------------------------------------------------------- #


def judge_settings() -> "tuple[str, str]":
    """``(platform, model)`` for the adjudicator, from ``[categorize]``."""
    from paperext.config import CFG

    cfg: Any = CFG  # the config proxy resolves attributes dynamically
    return str(cfg.categorize.judge_platform), str(cfg.categorize.judge_model)


def llm_judge(client: instructor.AsyncInstructor) -> Judge:
    """A :data:`Judge` backed by *client*, which must be a different vendor."""

    async def judge(pair: Pair) -> JudgeChoice:
        payload: Any = judge_messages(pair)
        choice, _ = await client.chat.completions.create_with_completion(
            response_model=JudgeChoice, messages=payload, max_retries=2
        )
        return choice

    return judge


def read_verdicts(path: "Union[str, Path]") -> "list[Verdict]":
    """Every verdict in a cache file, in write order."""
    return [
        Verdict.model_validate(json.loads(line))
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
