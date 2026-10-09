"""Highlight a paper's PDF with what each extraction arm claimed (#111).

Adjudicating a reference annotation from quoted fragments is the wrong
instrument: the owner's objection, 2026-10-09 --

    "It is difficult for me to get proper context with this only. I would need
    an annotated version of the pdf, like highlighted text in the PDF, so that
    I can browse the paper and see if I agree."

So this writes a PDF where every sentence an arm quoted is highlighted, colour
coded by **who claimed it**, with a note naming the field and entity. Reading
the paper then answers the question directly: a highlight only one arm made is
where to look, and a table row nobody highlighted is a recall gap.

    uv run python -m paperext.annotate_pdf <paper_id>

Colours:

- **green**  -- both arms quoted it. Agreement; skim.
- **yellow** -- arm A (anthropic) only.
- **blue**   -- arm B (openai) only.

Phrase location is pdfplumber's word boxes, because a quote spans words and
only word boxes give a rectangle. Matching is on normalised text, since the
extractions carry the PDF's text with its line breaks and ligatures resolved
differently from the PDF layer.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from paperext import CFG
from paperext.log import logger

#: (r, g, b) per claimant. Light enough to read the text through.
COLOURS = {
    "both": (0.72, 0.93, 0.72),
    "A": (1.0, 0.94, 0.60),
    "B": (0.70, 0.85, 1.0),
}

#: Arms, as `<provider>/<model>` under the queries directory.
DEFAULT_ARMS = ("anthropic/claude-opus-5", "openai/gpt-5.6-sol")

#: A quote shorter than this matches too much to be worth highlighting.
MIN_QUOTE = 24


def _cfg_dir(name: str) -> Path:
    """A configured directory as a ``Path``.

    One place for the `CFG.dir` access because mypy types it `Config | Path`
    and cannot know which -- the rest of the codebase carries 39 such errors in
    `merge_papers.py` alone. Narrowed here rather than ignored twice.
    """
    return Path(str(getattr(CFG.dir, name)))  # type: ignore[union-attr]


@dataclass
class Claim:
    """One quote, and every (arm, field) that offered it."""

    quote: str
    sources: "set[str]" = field(default_factory=set)
    labels: "list[str]" = field(default_factory=list)

    @property
    def colour(self) -> "tuple[float, float, float]":
        if len(self.sources) > 1:
            return COLOURS["both"]
        return COLOURS[next(iter(self.sources))]


def _norm(text: str) -> str:
    """Letters and digits only, lowercased.

    The extraction's quote and the PDF's text layer disagree about line breaks,
    hyphenation and ligatures, so comparing anything finer than this fails on
    quotes that are plainly present.
    """
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _walk(obj: Any, path: str = "") -> "Iterable[tuple[str, str]]":
    """Every ``(field path, quote)`` in an extraction, at any depth."""
    if isinstance(obj, dict):
        quote = obj.get("quote")
        if isinstance(quote, str) and quote.strip():
            name = obj.get("value")
            label = path
            if isinstance(name, str) and name.strip():
                label = f"{path} = {name}"
            yield label, quote
        for key, value in obj.items():
            if key in ("quote", "justification"):
                continue
            yield from _walk(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            yield from _walk(item, f"{path}[{i}]")


def collect_claims(paper_id: str, arms: "Iterable[str]") -> "list[Claim]":
    """Every quote both arms made, merged by quote text."""
    claims: "dict[str, Claim]" = {}
    for letter, arm in zip("AB", arms):
        provider, _, model = arm.partition("/")
        bucket = _cfg_dir("queries") / provider / model
        found = sorted(bucket.glob(f"{paper_id}_*.json"))
        if not found:
            logger.warning("no extraction for %s in %s", paper_id, arm)
            continue
        data = json.loads(found[0].read_text()).get("extractions", {})
        for label, quote in _walk(data):
            if len(quote.strip()) < MIN_QUOTE:
                continue
            key = _norm(quote)
            if not key:
                continue
            claim = claims.setdefault(key, Claim(quote=quote))
            claim.sources.add(letter)
            claim.labels.append(f"{letter}: {label}")
    return list(claims.values())


#: Normalised characters that must match before a highlight is worth placing.
#: Below this a prefix matches many sentences; above it a quote truncated by the
#: extractor or split across columns matches none.
MIN_MATCH = 30


def _page_index(page: Any) -> "tuple[str, list[Any]]":
    """The page's normalised text, and the box of every character in it.

    CHARACTERS, not words, because this corpus's PDFs have **no space
    characters in the text layer**: pdfplumber then returns one "word" per
    line, e.g. `'trainedforjointmotionforecasting,usingtheirreported...'`, and
    any word-boundary match fails on a quote starting mid-line. Matching that
    way placed 77 of 142 quotes on the first paper. Characters have no
    boundaries to disagree about.
    """
    text: "list[str]" = []
    boxes: "list[Any]" = []
    for ch in page.chars:
        norm = _norm(ch.get("text") or "")
        if not norm:
            continue
        text.append(norm)
        boxes.append(ch)
    return "".join(text), boxes


def _rects(boxes: "list[Any]") -> "list[tuple[float, float, float, float]]":
    """One rectangle per line the characters span."""
    by_line: "dict[float, list[Any]]" = defaultdict(list)
    for ch in boxes:
        by_line[round(ch["top"], 0)].append(ch)
    return [
        (
            min(c["x0"] for c in line),
            min(c["top"] for c in line),
            max(c["x1"] for c in line),
            max(c["bottom"] for c in line),
        )
        for line in by_line.values()
    ]


def _locate(page: Any, needle: str) -> "list[tuple[float, float, float, float]]":
    """Rectangles covering as much of ``needle`` as this page carries.

    The longest prefix, not the whole quote: a quote the extractor truncated or
    the typesetter split across columns would otherwise match nothing, and a
    prefix still points the reader at the right sentence, which is the job.
    """
    target = _norm(needle)
    if not target:
        return []
    text, boxes = _page_index(page)
    if not text:
        return []

    # A quote shorter than the floor must match IN FULL rather than be dropped.
    # Requiring a 30-character prefix of a 25-character quote silently discarded
    # every short one -- `'We train DJINN on two A100 GPUs'` is 25 normalised
    # characters and is plainly in the paper. A short exact match is specific
    # enough; it is a long partial that is not.
    floor = min(len(target), MIN_MATCH)

    # Longest prefix of the quote that appears on this page.
    lo, hi, found = floor, len(target), -1
    while lo <= hi:
        mid = (lo + hi) // 2
        at = text.find(target[:mid])
        if at >= 0:
            found, best_len, lo = at, mid, mid + 1
        else:
            hi = mid - 1
    if found < 0:
        return []
    return _rects(boxes[found : found + best_len])


def annotate(paper_id: str, arms: "Iterable[str]", out: "Path | None" = None) -> Path:
    import pdfplumber
    from pypdf import PdfReader, PdfWriter
    from pypdf.annotations import Highlight
    from pypdf.generic import (
        ArrayObject,
        FloatObject,
        NameObject,
        TextStringObject,
    )

    arms = list(arms)
    claims = collect_claims(paper_id, arms)
    if not claims:
        raise SystemExit(f"no quotes found for {paper_id} in {arms}")

    pdf = _cfg_dir("cache") / "fulltext" / paper_id / "fulltext.pdf"
    if not pdf.is_file():
        raise SystemExit(f"no PDF at {pdf}")

    placed: "dict[int, list[tuple[Claim, Any]]]" = defaultdict(list)
    unplaced: "list[Claim]" = []
    with pdfplumber.open(str(pdf)) as doc:
        heights = [p.height for p in doc.pages]
        for claim in claims:
            for i, page in enumerate(doc.pages):
                rects = _locate(page, claim.quote)
                if rects:
                    placed[i].append((claim, rects))
                    break
            else:
                unplaced.append(claim)

    reader = PdfReader(str(pdf))
    writer = PdfWriter()
    writer.append(reader)
    for page_no, items in placed.items():
        height = heights[page_no]
        for claim, rects in items:
            for x0, top, x1, bottom in rects:
                # pdfplumber measures from the top, PDF annotations from the
                # bottom: a highlight placed without flipping lands mirrored
                # on the page, which looks like a location bug rather than a
                # coordinate-system one.
                y0, y1 = height - bottom, height - top
                quad = ArrayObject(
                    [FloatObject(v) for v in (x0, y1, x1, y1, x0, y0, x1, y0)]
                )
                note = Highlight(
                    rect=(x0, y0, x1, y1),
                    quad_points=quad,
                    highlight_color="#%02x%02x%02x"
                    % tuple(int(c * 255) for c in claim.colour),
                )
                # The popup note: which arm claimed this, and for which field.
                # Reading a highlight without it tells you a sentence mattered
                # but not to whom, which is the whole question.
                note[NameObject("/Contents")] = TextStringObject(
                    "\n".join(claim.labels)
                )
                writer.add_annotation(page_number=page_no, annotation=note)

    out = out or pdf.parent / f"{paper_id}.annotated.pdf"
    with out.open("wb") as fh:
        writer.write(fh)

    total = len(claims)
    # Two different reasons a quote cannot be placed, kept apart because they
    # mean different things. An ELIDED quote is not verbatim by construction --
    # arm B writes these and arm A does not, which is a difference in how the
    # arms answer "quote", not evidence about the paper.
    #
    # The other bucket is NOT evidence of a fabricated citation, and the label
    # must not imply it. On the first paper its single entry was B quoting
    # "stochastic differential editing can be used to fine-tune the scene",
    # where the paper's sentence reads "DIFFERENTIAL STOCHASTIC editing can be
    # used to fine-tune the scene" -- two words transposed, in a paper that
    # spells the term both ways itself. Transposition and light paraphrase are
    # the ordinary causes; check before concluding anything stronger.
    elided = [c for c in unplaced if "..." in c.quote or "\u2026" in c.quote]
    missing = [c for c in unplaced if c not in elided]
    print(f"{paper_id}: {total} distinct quotes")
    print(f"  placed  {total - len(unplaced)}")
    print(
        f"  elided  {len(elided)} -- contain '...', so not verbatim; cannot be located"
    )
    for claim in elided[:4]:
        print(f"    [{'+'.join(sorted(claim.sources))}] {claim.quote[:68]!r}")
    print(
        f"  UNMATCHED {len(missing)} -- no verbatim span found. Usually a "
        "transposition or light paraphrase; check the paper before reading it "
        "as anything stronger"
    )
    for claim in missing[:6]:
        print(f"    [{'+'.join(sorted(claim.sources))}] {claim.quote[:68]!r}")
        for label in claim.labels[:2]:
            print(f"        {label}")
    both = sum(1 for c in claims if len(c.sources) > 1)
    print(
        f"  green (both) {both}   "
        f"yellow (A only) {sum(1 for c in claims if c.sources == {'A'})}   "
        f"blue (B only) {sum(1 for c in claims if c.sources == {'B'})}"
    )
    print(f"-> {out}")
    return out


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper_id")
    parser.add_argument("--arm", nargs="+", default=list(DEFAULT_ARMS))
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    annotate(args.paper_id, args.arm, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
