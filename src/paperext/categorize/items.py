"""Extraction corpus -> one decidable :class:`Item` per distinct name (WS-D D1b-2, #52).

The agent decides about *names*, but the corpus stores *mentions*: the same model
appears in twenty papers, spelled six ways, with a different supporting quote each
time. This module does that fold, and it is the only place that touches the stored
query JSONs.

**Grounding is extraction-records-only.** ``data/cache/`` is gitignored and empty,
so no paper full text exists locally and ``ontology_mapping``'s
``get_paper_model_excerpt`` cannot be ported. It costs nothing: the quote,
justification, aliases, ``is_executed`` and the co-occurring entities in the
git-tracked query JSONs are exactly the ITEM payload #44 specifies.

Two traps in that data, both handled here rather than in the prompt:

- **All 2110 stored 2024 records are pre-v4.** Up-conversion fills
  ``execution_mode`` and ``parameter_count`` with ``"unknown"`` and an *empty*
  quote/justification, so those two fields are dropped unless a record actually
  carries them. Rendering "execution mode: unknown" for every item of this corpus
  would be a thousand tokens of noise per run and, worse, reads as evidence.
- **``is_*.value`` is ``bool`` in 3305 records and ``int`` 0/1 in 296**, so every
  read goes through :func:`_as_bool`.

Loading is delegated to :mod:`paperext.analysis.frequency`
(``iter_paper_files`` / ``load_extractions`` / ``group_files_by_paper``), which
already handles the flat and model-scoped layouts and the v1-v4 up-conversion
chain. Duplicating it here would be a second thing to fix when the schema moves.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence, Union

from pydantic import BaseModel, Field

from paperext.analysis.rollup import str_normalize

#: Dimensions an item can be built for -> the ``PaperExtractions`` attribute(s)
#: that hold them. ``domains`` spans two fields, which is why this is a tuple.
DIMENSION_FIELDS: "dict[str, tuple[str, ...]]" = {
    "models": ("models",),
    "datasets": ("datasets",),
    "libraries": ("libraries",),
    "domains": ("primary_research_field", "sub_research_fields"),
}

#: Cap on mentions kept per item. The most-mentioned model has hundreds; three
#: well-chosen quotes ground a decision and the rest is repetition at full price.
DEFAULT_MAX_MENTIONS = 3

#: Cap on co-occurring entity names recorded per mention.
DEFAULT_MAX_CO_OCCURRING = 12


class Mention(BaseModel):
    """One paper's evidence about one name."""

    paper: str
    spelling: str
    quote: str = ""
    justification: str = ""
    aliases: "list[str]" = Field(default_factory=list)
    is_contributed: "bool | None" = None
    is_executed: "bool | None" = None
    is_compared: "bool | None" = None
    execution_mode: "str | None" = None
    role: "str | None" = None
    research_field: str = ""
    #: Raw names of the other same-dimension entities in this paper. Annotated
    #: with their current category at payload time -- against the *injected*
    #: ontology, never a cached map. See :mod:`paperext.categorize.prompt`.
    co_occurring: "list[str]" = Field(default_factory=list)


class Item(BaseModel):
    """Everything the corpus knows about one distinct name."""

    dimension: str
    #: Normalized lookup key -- what the normalization DB is keyed on.
    surface: str
    #: Display name: the most frequent raw spelling, ties broken alphabetically.
    name: str
    aliases: "list[str]" = Field(default_factory=list)
    spellings: "list[str]" = Field(default_factory=list)
    n_mentions: int = 0
    n_papers: int = 0
    mentions: "list[Mention]" = Field(default_factory=list)


def _as_bool(value: Any) -> "bool | None":
    """Coerce an ``Explained[bool]`` value that may be stored as ``int`` 0/1."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    return None


def _explained(entry: Any, field: str) -> Any:
    inner = getattr(entry, field, None)
    return getattr(inner, "value", None) if inner is not None else None


def _text(entry: Any, field: str, attr: str) -> str:
    inner = getattr(entry, field, None)
    return (getattr(inner, attr, "") or "").strip() if inner is not None else ""


def _entries(extractions: Any, dimension: str) -> "list[Any]":
    """Every entity of *dimension* in one paper's extractions, in stored order."""
    out: "list[Any]" = []
    for field in DIMENSION_FIELDS[dimension]:
        value = getattr(extractions, field, None)
        if value is None:
            continue
        out.extend(value if isinstance(value, list) else [value])
    return out


def _mention(
    entry: Any,
    *,
    paper: str,
    spelling: str,
    research_field: str,
    co_occurring: "list[str]",
) -> Mention:
    mode = _explained(entry, "execution_mode")
    mode = getattr(mode, "value", mode)  # ExecutionMode enum -> str
    quote = _text(entry, "name", "quote")
    # Pre-v4 records up-convert to execution_mode="unknown" with an empty quote;
    # that is an absence of evidence, not evidence of an unknown mode.
    if mode in (None, "unknown") or not _text(entry, "execution_mode", "quote"):
        mode = None
    role = getattr(entry, "role", None)
    return Mention(
        paper=paper,
        spelling=spelling,
        quote=quote,
        justification=_text(entry, "name", "justification"),
        aliases=[a.strip() for a in getattr(entry, "aliases", []) or [] if a.strip()],
        is_contributed=_as_bool(_explained(entry, "is_contributed")),
        is_executed=_as_bool(_explained(entry, "is_executed")),
        is_compared=_as_bool(_explained(entry, "is_compared")),
        execution_mode=mode,
        role=getattr(role, "value", role),
        research_field=research_field,
        co_occurring=co_occurring,
    )


def _primary_field(extractions: Any) -> str:
    field = getattr(extractions, "primary_research_field", None)
    name = getattr(field, "name", None)
    return (getattr(name, "value", "") or "").strip()


def iter_mentions(
    extractions: Any,
    dimension: str,
    *,
    paper: str = "",
    max_co_occurring: int = DEFAULT_MAX_CO_OCCURRING,
) -> "Iterator[tuple[str, str, Mention]]":
    """``(surface, spelling, mention)`` for every entity of *dimension* in a paper.

    Co-occurrence is computed once per paper and shared: for each entity, the
    *other* distinct names in the same paper and dimension. Names normalizing to
    the entity's own surface are excluded -- a paper that spells the same model two
    ways must not list it as its own neighbour, which in an ablated run would hand
    the agent the answer it is being asked for.
    """
    research_field = _primary_field(extractions)

    entries = []
    for entry in _entries(extractions, dimension):
        raw = (_explained(entry, "name") or "").strip()
        if not raw:
            continue
        surface = str_normalize(raw)
        if surface:
            entries.append((surface, raw, entry))

    names: "list[str]" = []
    for _, raw, _entry in entries:
        if raw not in names:
            names.append(raw)

    for surface, raw, entry in entries:
        others = [n for n in names if str_normalize(n) != surface]
        yield surface, raw, _mention(
            entry,
            paper=paper,
            spelling=raw,
            research_field=research_field,
            co_occurring=others[:max_co_occurring],
        )


def _rank_mentions(mentions: "list[Mention]", limit: int) -> "list[Mention]":
    """Keep the *limit* most informative mentions, deterministically.

    Longer quotes carry more of the sentence the name appeared in, and a mention
    whose paper actually ran the model is better evidence than one that cites it,
    so both rank ahead. Paper id breaks every remaining tie, so the selection does
    not depend on filesystem order.
    """
    return sorted(
        mentions,
        key=lambda m: (
            not bool(m.quote),
            not bool(m.is_executed),
            -len(m.quote),
            m.paper,
        ),
    )[:limit]


def build_items(
    dimension: str,
    *,
    platform: "str | None" = None,
    model: "str | None" = None,
    queries_dir: "Union[str, Path, None]" = None,
    files: "Iterable[Union[str, Path]] | None" = None,
    max_mentions: int = DEFAULT_MAX_MENTIONS,
    max_co_occurring: int = DEFAULT_MAX_CO_OCCURRING,
) -> "list[Item]":
    """Fold the stored extractions into one :class:`Item` per distinct name.

    Ordered most-mentioned first, ties by surface -- which is also the order the
    agent should run in, since the common names are the ones that move the counts
    and the ones whose decisions best inform the rest of the run.
    """
    if dimension not in DIMENSION_FIELDS:
        raise ValueError(
            f"unknown dimension {dimension!r}; expected one of "
            f"{sorted(DIMENSION_FIELDS)}"
        )
    from paperext.analysis.frequency import (
        group_files_by_paper,
        iter_paper_files,
        load_extractions,
    )

    if files is None:
        from paperext.config import CFG

        cfg: Any = CFG  # the config proxy resolves attributes dynamically
        platform = platform or cfg.platform.select
        paths = iter_paper_files(
            platform,
            model=model,
            queries_dir=Path(queries_dir) if queries_dir else None,
        )
    else:
        paths = sorted(Path(f) for f in files)

    mentions: "dict[str, list[Mention]]" = {}
    spellings: "dict[str, Counter]" = {}
    aliases: "dict[str, Counter]" = {}

    for paper_id, paper_files in group_files_by_paper(paths).items():
        for path in paper_files:
            extractions = load_extractions(path)
            for surface, spelling, mention in iter_mentions(
                extractions,
                dimension,
                paper=paper_id,
                max_co_occurring=max_co_occurring,
            ):
                mentions.setdefault(surface, []).append(mention)
                spellings.setdefault(surface, Counter())[spelling] += 1
                for alias in mention.aliases:
                    if str_normalize(alias) != surface:
                        aliases.setdefault(surface, Counter())[alias] += 1

    items = []
    for surface, records in mentions.items():
        counts = spellings[surface]
        items.append(
            Item(
                dimension=dimension,
                surface=surface,
                name=_most_common(counts)[0],
                aliases=_most_common(aliases.get(surface, Counter())),
                spellings=_most_common(counts),
                n_mentions=len(records),
                n_papers=len({m.paper for m in records}),
                mentions=_rank_mentions(records, max_mentions),
            )
        )
    items.sort(key=lambda item: (-item.n_mentions, item.surface))
    return items


def _most_common(counter: Counter) -> "list[str]":
    """Counter keys, most frequent first, alphabetical within a tie."""
    return [key for key, _ in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))]


def write_items(items: "Sequence[Item]", path: "Union[str, Path]") -> Path:
    """Write *items* as jsonl, so a run's input is a file that can be diffed.

    Folding the 2024 corpus takes ~1.5s, so this is about reproducibility -- an
    eval run and its replay must agree on what was asked -- not about speed.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        for item in items:
            fh.write(item.model_dump_json() + "\n")
    return path


def read_items(path: "Union[str, Path]") -> "list[Item]":
    """Read a jsonl file written by :func:`write_items`."""
    out = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line:
            out.append(Item.model_validate_json(line))
    return out


def main(argv: "Sequence[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(
        prog="categorize-items", description="Fold the extraction corpus into items."
    )
    parser.add_argument("--dim", default="models", choices=sorted(DIMENSION_FIELDS))
    parser.add_argument("--platform", default=None)
    parser.add_argument(
        "--model", default=None, help="model subdirectory to restrict to"
    )
    parser.add_argument("--queries-dir", default=None)
    parser.add_argument("--max-mentions", type=int, default=DEFAULT_MAX_MENTIONS)
    parser.add_argument("--out", default=None, metavar="JSONL")
    parser.add_argument("--top", type=int, default=20, help="rows to print")
    args = parser.parse_args(argv)

    items = build_items(
        args.dim,
        platform=args.platform,
        model=args.model,
        queries_dir=args.queries_dir,
        max_mentions=args.max_mentions,
    )
    print(
        f"# {args.dim}: {len(items)} distinct names, "
        f"{sum(i.n_mentions for i in items)} mentions"
    )
    for item in items[: args.top]:
        print(f"  {item.n_mentions:>5}  {item.n_papers:>4}p  {item.name}")
    if args.out:
        print(f"# wrote {write_items(items, args.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
