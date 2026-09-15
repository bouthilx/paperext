"""Step through decisions one at a time, as a human reviewer (WS-D D1b).

``categorize --interactive`` decides one item, shows what the model was given and
what it decided -- its reasoning, every action with its justification, where the
name lands, the exact diff a dry run produced -- and waits. Nothing touches the
tree until the reviewer says so.

Every verdict is appended to a ``review.jsonl``. That file is not a by-product:
the #53 gate wants a human audit of the agent's placements, and following along
here *is* that audit, recorded as it happens.

Rendering is pure (strings in, strings out) and the prompt takes its ``input`` /
``output`` callables as parameters, so the whole loop is testable by feeding it
keystrokes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Union

from pydantic import BaseModel

from paperext.categorize.apply import DecisionRecord
from paperext.categorize.items import Item
from paperext.categorize.prompt import Payload, render_evidence, render_payload
from paperext.ontology.ontology import Ontology

#: What the reviewer can say about a decision. ``apply`` and ``skip`` are about
#: the tree; ``wrong`` and ``unsure`` are ``skip`` plus a recorded judgment.
COMMANDS = {
    "a": "apply",
    "s": "skip",
    "w": "wrong",
    "u": "unsure",
    "p": "payload",
    "r": "retry",
    "q": "quit",
}

HELP = "[a]pply  [s]kip  [w]rong  [u]nsure  [p]ayload  [r]etry  [q]uit"

RULE = "-" * 78


class Review(BaseModel):
    """One human verdict on one decision."""

    run_id: str
    seq: int
    surface: str
    name: str
    verdict: str
    note: str = ""
    outcome: str
    agent_path: str = ""


def render_candidates(payload: Payload) -> str:
    """The candidate list as the reviewer needs it: id, path, score."""
    if not payload.candidates:
        return "(no candidates -- nothing in the tree resembles this name)"
    lines = []
    for view in payload.candidates:
        lines.append(
            f"  {view.score:.2f}  `{view.id}`  {' > '.join(view.path)}"
            f"  [{view.cut_category or 'no category'}]"
        )
    return "\n".join(lines)


def render_decision(record: DecisionRecord, onto: Ontology) -> str:
    """Everything a reviewer needs to judge one decision, model output first."""
    decision, result = record.decision, record.result
    lines = [
        f"outcome: {decision.outcome.value}   confidence: {decision.confidence:.2f}",
    ]
    if decision.reasoning:
        lines += ["", "reasoning:", _indent(decision.reasoning)]
    if decision.review_notes:
        lines += ["", "review notes:"] + [
            f"  - {note}" for note in decision.review_notes
        ]
    if decision.unresolved:
        lines.append(f"unresolved: {', '.join(decision.unresolved)}")

    lines += ["", "actions:" if decision.actions else "actions: (none)"]
    for index, action in enumerate(decision.actions):
        args = {
            key: value
            for key, value in action.model_dump().items()
            if key not in {"op", "justification", "confidence"}
            and value not in ("", [], None)
        }
        status = ""
        if index < len(result.actions) and result.actions[index].status.value in {
            "rejected",
            "rolled_back",
            "skipped",
        }:
            status = f"  <{result.actions[index].status.value}>"
        lines.append(f"  {index}. {action.op}({_args(args)}){status}")
        lines.append(f"     because: {action.justification}  [{action.confidence:.2f}]")

    if result.placement is not None:
        lines += [
            "",
            f"lands at: {' > '.join(result.placement.ancestor_names)}"
            f"   [{result.placement.cut_category or 'no category'}]",
        ]
    if not result.ok:
        lines += ["", f"REJECTED by the applier: {result.error}"]
    elif not result.diff.is_empty():
        diff = result.diff
        parts = []
        if diff.created:
            parts.append(f"creates {', '.join(diff.created)}")
        if diff.modified:
            parts.append(f"modifies {', '.join(diff.modified)}")
        if diff.deleted:
            parts.append(f"deletes {', '.join(diff.deleted)}")
        if diff.surfaces_added:
            parts.append(
                "maps " + ", ".join(f"{s} -> {c}" for s, c in diff.surfaces_added)
            )
        if diff.surfaces_removed:
            parts.append("unmaps " + ", ".join(s for s, _ in diff.surfaces_removed))
        lines += ["", "would change: " + "; ".join(parts)]
    usage = record.provenance.params.get("usage") or {}
    if usage:
        lines.append(
            f"tokens: {usage.get('input_tokens', '?')} in / "
            f"{usage.get('output_tokens', '?')} out"
        )
    return "\n".join(lines)


def _args(values: "dict[str, Any]") -> str:
    return ", ".join(f"{key}={value!r}" for key, value in values.items())


def _indent(text: str, prefix: str = "  ") -> str:
    return "\n".join(prefix + line for line in text.splitlines())


#: The reviewer callback ``agent.run`` calls before applying: returns the command
#: name (``apply`` / ``skip`` / ``retry`` / ``quit``).
Reviewer = Callable[[Item, Payload, DecisionRecord, Ontology], str]


class ReviewLog:
    """Append-only jsonl of :class:`Review` records."""

    def __init__(self, path: "Union[str, Path]") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, review: Review) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(review.model_dump_json() + "\n")


def interactive(
    log: "ReviewLog | None" = None,
    *,
    read: "Callable[[str], str]" = input,
    write: "Callable[[str], None]" = print,
    show_evidence: bool = True,
) -> Reviewer:
    """A :data:`Reviewer` that talks to a terminal (or to the test feeding it)."""

    def review(
        item: Item, payload: Payload, record: DecisionRecord, onto: Ontology
    ) -> str:
        write(
            f"\n{RULE}\n{record.provenance.seq + 1}. {item.name}  ({item.surface})\n{RULE}"
        )
        if show_evidence:
            write("\n".join(render_evidence(payload)))
            write("\n## CANDIDATES\n")
            write(render_candidates(payload))
        write(f"\n## DECISION\n")
        write(render_decision(record, onto))

        while True:
            answer = read(f"\n{HELP} > ").strip().lower()
            command = COMMANDS.get(answer[:1] if answer else "")
            if command is None:
                write(HELP)
                continue
            if command == "payload":
                write(f"\n{render_payload(payload)}\n")
                write(render_decision(record, onto))
                continue
            if command in {"apply", "skip", "wrong", "unsure"}:
                note = read("note (enter to skip) > ").strip()
                if log is not None:
                    log.write(
                        Review(
                            run_id=record.provenance.run_id,
                            seq=record.provenance.seq,
                            surface=item.surface,
                            name=item.name,
                            verdict=command,
                            note=note,
                            outcome=record.decision.outcome.value,
                            agent_path=(
                                " > ".join(record.result.placement.ancestor_names)
                                if record.result.placement
                                else ""
                            ),
                        )
                    )
                return "apply" if command == "apply" else "skip"
            return command  # retry / quit

    return review


def read_reviews(path: "Union[str, Path]") -> "list[Review]":
    return [
        Review.model_validate(json.loads(line))
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
