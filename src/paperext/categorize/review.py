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

import glob
import io
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Union

from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from rich.text import Text

from paperext.categorize.apply import DecisionRecord
from paperext.categorize.items import DEFAULT_MAX_MENTIONS, Item, Mention
from paperext.categorize.progress import Pace
from paperext.categorize.prompt import Payload, render_payload
from paperext.ontology.ontology import Ontology

#: What the reviewer can say about a decision. ``apply`` and ``skip`` are about
#: the tree; ``wrong`` and ``unsure`` are ``skip`` plus a recorded judgment.
COMMANDS = {
    "a": "apply",
    "s": "skip",
    "w": "wrong",
    "u": "unsure",
    "e": "evidence",
    "p": "payload",
    "r": "retry",
    "q": "quit",
}

HELP = (
    "[a]pply  [s]kip  [w]rong  [u]nsure  [e]vidence (e N: one paper)  "
    "[p]ayload  [r]etry  [q]uit"
)

#: Column caps for the evidence table. Quote and rationale wrap; everything else
#: is clipped, so a row's height is set by the quote alone.
PAPER_WIDTH = 46
ALONGSIDE_WIDTH = 24
QUOTE_CHARS = 200
RATIONALE_CHARS = 110

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


def role_glyphs(mention: Mention) -> str:
    """``CEK`` for contributed / executed / compared; ``·`` where false or unknown."""
    return "".join(
        glyph if flag else "·"
        for flag, glyph in (
            (mention.is_contributed, "C"),
            (mention.is_executed, "E"),
            (mention.is_compared, "K"),
        )
    )


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "\u2026"


def render_mentions_table(
    item: Item,
    *,
    seen: "int | None" = DEFAULT_MAX_MENTIONS,
    width: "int | None" = None,
) -> str:
    """Every paper that mentions *item*, best evidence first.

    The first *seen* rows are what the agent was actually given (``\u25b8``);
    the rest are dimmed. That split is the point of the table: it separates
    "the agent ignored good evidence" from "the harness never showed it", which
    are different failures with different fixes.
    """
    shown = len(item.mentions) if seen is None else seen
    table = Table(
        title=(
            f"{item.name}  \u2014  {item.n_mentions} mention(s) in {item.n_papers} "
            f"paper(s)  (\u25b8 = shown to the agent)"
        ),
        title_justify="left",
        expand=True,
        show_lines=True,
        pad_edge=False,
    )
    table.add_column("#", width=2, no_wrap=True)
    table.add_column("paper", width=PAPER_WIDTH, no_wrap=True, overflow="ellipsis")
    table.add_column("role", width=4, no_wrap=True)
    table.add_column("quote", ratio=5)
    table.add_column("rationale", ratio=2)
    table.add_column(
        "alongside", width=ALONGSIDE_WIDTH, no_wrap=True, overflow="ellipsis"
    )
    for index, mention in enumerate(item.mentions, start=1):
        given = index <= shown
        paper = Text(no_wrap=True, overflow="ellipsis")
        paper.append(
            ("\u25b8 " if given else "  ") + mention.paper,
            style="bold" if given else "dim",
        )
        if mention.research_field:
            paper.append("  " + mention.research_field, style="dim")
        paper.append("\n" + (mention.title or "(no title)"))
        if mention.referenced_paper:
            paper.append("\n\u21b3 " + mention.referenced_paper, style="italic")
        others = mention.co_occurring
        alongside = ", ".join(others[:3]) + (
            f" +{len(others) - 3}" if len(others) > 3 else ""
        )
        table.add_row(
            str(index),
            paper,
            role_glyphs(mention),
            _clip(mention.quote, QUOTE_CHARS) or "\u2014",
            _clip(mention.justification, RATIONALE_CHARS) or "\u2014",
            alongside or "\u2014",
            style=None if given else "dim",
        )
    console = Console(file=io.StringIO(), width=width, force_terminal=False)
    console.print(table)
    return console.file.getvalue()  # type: ignore[attr-defined]


def render_mention(
    mention: Mention, index: int, *, abstract: str = "", links: "Iterable[str]" = ()
) -> str:
    """One paper in full: nothing clipped, plus the abstract when we have it."""
    lines = [f"[{index}] {mention.paper}  {mention.title or '(no title)'}"]
    if mention.research_field:
        lines.append(f"    field: {mention.research_field}")
    if mention.referenced_paper:
        lines.append(f"    reference, as extracted: {mention.referenced_paper}")
    lines.append(
        f"    role: {role_glyphs(mention)}  (C contributed, E executed, K compared)"
    )
    if mention.execution_mode:
        lines.append(f"    execution: {mention.execution_mode}")
    if mention.aliases:
        lines.append(f"    aliases: {', '.join(mention.aliases)}")
    lines += ["", "    quote:", _indent(mention.quote or "(none)", "      ")]
    lines += [
        "",
        "    extractor's reason:",
        _indent(mention.justification or "(none)", "      "),
    ]
    if mention.co_occurring:
        lines += ["", "    alongside: " + ", ".join(mention.co_occurring)]
    for link in links:
        lines.append(f"    {link}")
    if abstract:
        lines += ["", "    abstract:", _indent(abstract, "      ")]
    return "\n".join(lines)


class PaperIndex:
    """Titles, abstracts and links from the paperoni dumps, keyed by every id.

    A query record's paper id is whatever the corpus used -- an arXiv id or an
    OpenReview id -- while the dump keys papers by its own hash; the dump's
    ``links`` carry both, so the index is built from those.
    """

    def __init__(self, paths: "Iterable[Union[str, Path]]" = ()) -> None:
        self._by_id: "dict[str, dict[str, Any]]" = {}
        for path in paths:
            for paper in json.loads(Path(path).read_text(encoding="utf-8")):
                for link in paper.get("links", []):
                    if link.get("type", "").endswith(".abstract"):
                        self._by_id.setdefault(str(link.get("link", "")), paper)

    @classmethod
    def default(cls, data_dir: "Union[str, Path]" = "data") -> "PaperIndex":
        return cls(sorted(glob.glob(str(Path(data_dir) / "paperoni-*.json"))))

    def abstract(self, paper_id: str) -> str:
        return str(self._by_id.get(paper_id, {}).get("abstract", "") or "")

    def links(self, paper_id: str) -> "list[str]":
        paper = self._by_id.get(paper_id)
        if paper is None:
            return []
        out = []
        for link in paper.get("links", []):
            kind, value = link.get("type", ""), str(link.get("link", ""))
            if kind == "arxiv.abstract":
                out.append(f"https://arxiv.org/abs/{value}")
            elif kind == "openreview.abstract":
                out.append(f"https://openreview.net/forum?id={value}")
            elif kind.startswith("html") or kind.startswith("pdf"):
                out.append(value)
        return out[:3]


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
    seen: "int | None" = DEFAULT_MAX_MENTIONS,
    papers: "PaperIndex | None" = None,
    width: "int | None" = None,
    total: "int | None" = None,
) -> Reviewer:
    """A :data:`Reviewer` that talks to a terminal (or to the test feeding it).

    *seen* is how many mentions the agent was given, so the evidence table can
    mark them; *papers* supplies abstracts for ``e N``, loaded lazily from the
    paperoni dumps if not given.
    """
    index = papers
    pace = Pace(total) if total else None

    def paper_index() -> PaperIndex:
        nonlocal index
        if index is None:
            index = PaperIndex.default()
        return index

    def review(
        item: Item, payload: Payload, record: DecisionRecord, onto: Ontology
    ) -> str:
        header = f"{record.provenance.seq + 1}. {item.name}  ({item.surface})"
        if pace is not None:
            header += "   " + pace.line(record.provenance.seq)
        write(f"\n{RULE}\n{header}\n{RULE}")
        write(render_mentions_table(item, seen=seen, width=width))
        write("## CANDIDATES\n")
        write(render_candidates(payload))
        write("\n## DECISION\n")
        write(render_decision(record, onto))

        while True:
            answer = read(f"\n{HELP} > ").strip().lower()
            command = COMMANDS.get(answer[:1] if answer else "")
            if command is None:
                write(HELP)
                continue
            if command == "evidence":
                rest = answer[1:].strip()
                if rest.isdigit() and 1 <= int(rest) <= len(item.mentions):
                    mention = item.mentions[int(rest) - 1]
                    write(
                        render_mention(
                            mention,
                            int(rest),
                            abstract=paper_index().abstract(mention.paper),
                            links=paper_index().links(mention.paper),
                        )
                    )
                else:
                    write(render_mentions_table(item, seen=seen, width=width))
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
