"""The #103 verification pass: does the v5 prompt work, measured on a small run.

Schema v5 added ``runs[]``, ``algorithms[]`` and ``data_sources[]``, and **no
extraction has ever run against them**. #103 exists to spend one small run
finding that out rather than discovering it after ~2000 papers, because step 3
of ``design -> extract -> revise -> categorise`` (#99) revises the *ontology*
against the extraction -- so an extraction that failed for a **prompt** reason
would send #99 chasing a defect that is not in the ontology.

This module runs every mechanisable check #103 and #102 specify, over a
directory of extractions::

    uv run python -m paperext.structured_output.mdl.verify data/mdl/queries/anthropic/...

Three kinds of result, and the distinction is the point:

- **CHECK** -- a pass/fail with a stated reading. A failure is a prompt defect.
- **PROBE** -- a region that must be non-zero. Zero means the widened scope
  never reached the prompt, and the finding is about the prompt's *scope
  statement*, never its vocabulary: handing the extractor a closed list would
  make #99 circular, which is #103 section 5.
- **MEASURE** -- a number with no pass condition, because the risk being sized
  has no correct value. Over-splitting and field coverage are both of this kind.

Region probes are read off the algorithms ``role`` axis through the #100 loader
(``data/ontology/design/c0_verification/probe_sets.json``), never hand-typed.
Matching is by written name or written alias and **never by similarity** --
token matching once paired ``gpt-j`` with ``GPT-4``, and a morphological rule
put ``bayesian neural networks`` under the graphical-model node.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from paperext.structured_output.mdl.check import (
    check_references,
    iter_extractions,
)
from paperext.utils import str_normalize

PROBE_SETS = Path("data/ontology/design/c0_verification/probe_sets.json")


@dataclass
class Finding:
    """One result. ``ok`` is ``None`` for a measurement, which cannot fail."""

    kind: str
    name: str
    ok: bool | None
    detail: str
    reading: str = ""
    papers: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        mark = {True: "PASS", False: "FAIL", None: "----"}[self.ok]
        out = f"[{mark}] {self.kind:7} {self.name}\n         {self.detail}"
        if self.ok is False and self.reading:
            out += f"\n         READING: {self.reading}"
        if self.papers:
            shown = ", ".join(self.papers[:6])
            more = f" (+{len(self.papers) - 6})" if len(self.papers) > 6 else ""
            out += f"\n         papers: {shown}{more}"
        return out


def _raw_names(entries: Iterable[Any]) -> set[str]:
    """Names and aliases **as written**, before normalisation.

    The stem pass needs these, because `str_normalize` strips the separators and
    leaves nothing to tokenise.
    """
    out: set[str] = set()
    for entry in entries or []:
        name = getattr(getattr(entry, "name", None), "value", "") or ""
        if name.strip():
            out.add(name)
        for alias in getattr(entry, "aliases", None) or []:
            if alias.strip():
                out.add(alias)
    return out


def _names(entries: Iterable[Any]) -> set[str]:
    """Normalised name plus written aliases for every entry in a list."""
    out: set[str] = set()
    for entry in entries or []:
        name = getattr(getattr(entry, "name", None), "value", "") or ""
        if name.strip():
            out.add(str_normalize(name))
        for alias in getattr(entry, "aliases", None) or []:
            if alias.strip():
                out.add(str_normalize(alias))
    return out


def _value(obj: Any, attr: str) -> Any:
    """An ``Explained[T]``'s value, or a plain attribute, or ``None``."""
    got = getattr(obj, attr, None)
    got = getattr(got, "value", got)
    return getattr(got, "value", got)


#: Tokens too generic to carry a region on their own, so a shared one of these
#: is not evidence of anything.
_STOPWORDS = frozenset(
    {
        "the",
        "a",
        "of",
        "and",
        "with",
        "for",
        "on",
        "in",
        "to",
        "by",
        "based",
        "method",
        "model",
        "algorithm",
        "learning",
        "search",
        "network",
        "data",
        "loss",
        "function",
        "score",
        "test",
        "set",
    }
)


def _stems(name: str) -> set[str]:
    """Content tokens of a name, crudely stemmed, for DETECTION ONLY.

    Never used to place a name on a node. It exists because the region probes
    ask "did this region come back", and exact matching answered "which node is
    this" -- reporting the evaluation region as empty while the extraction held
    `10-fold cross-validation` against a node spelled `k-fold`.
    """
    tokens = re.split(r"[^a-z0-9]+", name.lower())
    out = set()
    for token in tokens:
        if len(token) < 4 or token in _STOPWORDS or token.isdigit():
            continue
        out.add(token[:-1] if token.endswith("s") and len(token) > 4 else token)
    return out


#: What "the paper did not say" looks like once unwrapped.
_ABSENT: tuple[Any, ...] = (None, "", "unknown", [])


def _stated(obj: Any, attr: str) -> bool:
    """Whether the paper actually stated this field.

    A list-valued field needs unwrapping member by member:
    `Explained[list[Parallelism]]` spells "not stated" as `['unknown']`, which
    is neither empty nor the string `'unknown'`, so a scalar test counted every
    run as having stated its parallelism -- 77/77 on the first v5 run, which is
    what made the bug visible.
    """
    value = _value(obj, attr)
    if isinstance(value, (list, tuple, set)):
        return any(
            str(getattr(item, "value", item)).strip().lower()
            not in ("", "unknown", "none")
            for item in value
        )
    if value in _ABSENT:
        return False
    return str(value).strip().lower() not in ("", "unknown", "none")


@dataclass
class Corpus:
    """Every extraction, indexed the few ways the checks need."""

    papers: dict[str, Any] = field(default_factory=dict)

    #: Files that were found but did not validate against any model version.
    skipped: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, paths: Iterable[Path]) -> Corpus:
        paths = list(paths)
        papers = {path.stem: ex for path, ex in iter_extractions(paths)}
        skipped = sorted({p.stem for p in paths} - set(papers))
        return cls(papers, skipped)

    def where(self, slot: str, *wanted: str) -> list[str]:
        """Papers whose ``slot`` names any of ``wanted`` (exact, normalised)."""
        want = {str_normalize(w) for w in wanted}
        return sorted(
            p for p, ex in self.papers.items() if _names(getattr(ex, slot, [])) & want
        )

    def runs(self) -> list[tuple[str, Any]]:
        return [(p, r) for p, ex in self.papers.items() for r in ex.runs or []]


def _slot_exclusion(
    corpus: Corpus, label: str, name: str, wrong: str, right: str, reading: str
) -> Finding:
    """``name`` must appear in ``right`` and not in ``wrong``."""
    bad = corpus.where(wrong, name)
    good = corpus.where(right, name)
    return Finding(
        kind="CHECK",
        name=label,
        ok=not bad,
        detail=(
            f"{name!r} in {wrong}[]: {len(bad)} papers; in {right}[]: "
            f"{len(good)} papers"
        ),
        reading=reading,
        papers=bad,
    )


def acceptance(corpus: Corpus) -> list[Finding]:
    """#103 section 1's name checks, plus #102's admission-rule clauses."""
    out = [
        _slot_exclusion(
            corpus,
            "adam/adamw are algorithms, not libraries",
            "adam",
            "libraries",
            "algorithms",
            "a known legacy misrouting. `adam` in libraries[] means the "
            "algorithms scope statement did not land.",
        ),
        _slot_exclusion(
            corpus,
            "adamw is an algorithm, not a library",
            "adamw",
            "libraries",
            "algorithms",
            "same misrouting as `adam`; both were measured in legacy-2024.",
        ),
        _slot_exclusion(
            corpus,
            "pytorch is a library, not a model",
            "pytorch",
            "models",
            "libraries",
            "a known legacy misrouting in the other direction.",
        ),
        _slot_exclusion(
            corpus,
            "mujoco is a library, not a data source",
            "mujoco",
            "data_sources",
            "libraries",
            "#102 Part A's library clause. One string, two entities: the "
            "engine is a library, HalfCheetah is a data source. HARD "
            "FAILURE -- `mujoco` was the most-cited name in the placement set.",
        ),
    ]

    # The protocol clause (#102 Part A, added 2026-10-08). A protocol says how
    # much of a source to use and how to score it, so it is not a source.
    protocols = ("atari 100k", "atari 57", "helm", "urlb", "carla nocrash")
    hits = {name: corpus.where("data_sources", name) for name in protocols}
    offenders = sorted({p for ps in hits.values() for p in ps})
    out.append(
        Finding(
            kind="CHECK",
            name="an evaluation protocol is not a data source",
            ok=not offenders,
            detail=", ".join(f"{k}: {len(v)}" for k, v in hits.items()),
            reading=(
                "#102 Part A's protocol clause. All three placement runs found "
                "these admitted because they are named, then returning their "
                "base environment's values -- double-counting it."
            ),
            papers=offenders,
        )
    )

    # Unnamed descriptions. `synthetic data` is the measured exemplar (~41
    # names, 1.6% of the corpus vocabulary).
    unnamed = ("synthetic data", "synthetic dataset", "synthetic datasets")
    offenders = sorted({p for n in unnamed for p in corpus.where("data_sources", n)})
    out.append(
        Finding(
            kind="CHECK",
            name="an unnamed description is not a data source",
            ok=not offenders,
            detail=f"{len(offenders)} papers name a bare synthetic-data description",
            reading="#102 Part A: a description is not an artifact.",
            papers=offenders,
        )
    )

    # `generate` must not carry a parameter count: the mode exists because the
    # cost of stepping a simulator is not parameter-shaped.
    offenders = [
        p
        for p, run in corpus.runs()
        if _value(run, "execution_mode") == "generate"
        and _stated(run, "parameter_count")
    ]
    out.append(
        Finding(
            kind="CHECK",
            name="a generate run has no parameter count",
            ok=not offenders,
            detail=f"{len(offenders)} generate runs carry a parameter_count",
            reading=(
                "HARD FAILURE. `generate` is deliberately not `inference`: "
                "stepping a simulator or transforming a corpus has no "
                "parameter count, and the 6ND/2ND formulas assume a network."
            ),
            papers=sorted(set(offenders)),
        )
    )
    return out


def probes(corpus: Corpus, probe_sets: dict[str, Any]) -> list[Finding]:
    """#103 section 1's three region checks, read off the `role` axis."""
    out = []
    for region, entries in probe_sets["regions"].items():
        want: set[str] = set()
        for entry in entries:
            want.add(str_normalize(entry["name"]))
            want.update(str_normalize(s) for s in entry["surfaces"])
        hits = {
            p: sorted(_names(ex.algorithms) & want)
            for p, ex in corpus.papers.items()
            if _names(ex.algorithms) & want
        }
        found = sorted({n for ns in hits.values() for n in ns})

        # A second, DETECTION-ONLY pass. Exact matching is the right rule for
        # resolution -- similarity is what paired `gpt-j` with `GPT-4` -- but as
        # a probe it answers the wrong question: it asks "which node is this"
        # when the region check only asks "did anything in this region come
        # back". It gave a FALSE NEGATIVE on real output: openai returned
        # `10-fold cross-validation`, `five-fold cross-validation` and `95%
        # stratified bootstrap CIs` while the probe reported the evaluation
        # region as zero, because the node is spelled `k-fold cross-validation`.
        # Batch 1 passed only because Anthropic happened to emit that exact
        # string. These counts never place a name on a node; the exact set above
        # is still the only thing that does.
        # Stems come from the names AS WRITTEN, not their normalised forms:
        # `str_normalize` strips the separators, so a normalised
        # `kfoldcrossvalidation` has no tokens left and the first version of
        # this pass silently matched nothing -- the same bug it was added to
        # fix, one layer down.
        stems: set[str] = set()
        for entry in entries:
            stems |= _stems(entry["name"])
            for surface in entry["surfaces"]:
                stems |= _stems(surface)
        near: dict[str, list[str]] = {}
        for paper, ex in corpus.papers.items():
            if paper in hits:
                continue
            # Two shared content tokens, not one: one is a coincidence.
            loose = sorted(
                n for n in _raw_names(ex.algorithms) if len(_stems(n) & stems) >= 2
            )
            if loose:
                near[paper] = loose
        out.append(
            Finding(
                kind="PROBE",
                name=f"{region} is non-zero",
                # Exact matching only. A near match cannot flip this: the stem
                # pass is noisy -- it offered `AGRE-KD` for the evaluation
                # region -- and the two outcomes have DIFFERENT causes, which a
                # single PASS would merge. See the companion finding.
                ok=bool(hits),
                detail=(
                    f"{len(hits)} papers by exact name, {len(found)} distinct, "
                    f"against a probe of {len(entries)} nodes / {len(want)} "
                    "surfaces" + (f": {', '.join(found[:6])}" if found else "")
                ),
                reading=(
                    "READ THE COMPANION FINDING FIRST. Zero exact matches AND "
                    "zero near matches means the widened scope never reached "
                    "the prompt, which is about the prompt's SCOPE STATEMENT "
                    "and never its vocabulary (#103 section 5) -- do NOT hand "
                    "the extractor a closed list, which makes #99 circular. "
                    "Zero exact matches WITH near matches is the opposite "
                    "finding: the prompt worked and the ontology has no "
                    "spelling for what came back."
                ),
                papers=sorted(hits),
            )
        )
        out.append(
            Finding(
                kind="MEASURE",
                name=f"{region}: region-shaped names matching no node",
                ok=None,
                detail=(
                    "0 papers -- so an exact zero above means the region really "
                    "is absent, not merely unspellable"
                    if not near
                    else (
                        f"{len(near)} papers: "
                        + ", ".join(sorted({n for ns in near.values() for n in ns})[:6])
                        + ". DETECTION ONLY and noisy -- two shared content "
                        "tokens, never a placement. An exact zero above with a "
                        "non-zero here is a NORMALISATION GAP for #99, not a "
                        "prompt defect: openai returned `10-fold "
                        "cross-validation` against a node spelled `k-fold "
                        "cross-validation`"
                    )
                ),
                papers=sorted(near),
            )
        )
    return out


def manual(corpus: Corpus) -> list[Finding]:
    """Cases no assertion can settle, surfaced for a human read."""
    out = []
    iql = corpus.where("algorithms", "iql")
    out.append(
        Finding(
            kind="MANUAL",
            name="iql comes back with its context, unresolved",
            ok=None,
            detail=(
                f"{len(iql)} papers name `iql`. Read each one's quote: the bare "
                "string is both Implicit and Independent Q-Learning and "
                "resolves to neither, so a usable extraction returns the "
                "context rather than picking one"
            ),
            papers=iql,
        )
    )
    # `str()` on an enum member gives "DataSourceRunRole.REFERENCE", so the
    # membership test silently never matched and this reported 0 while the
    # genomics paper was returning three reference-role sources. Same unwrapping
    # mistake as the `['unknown']` parallelism bug: read `.value`.
    refs = [
        p
        for p, run in corpus.runs()
        for ds in run.data_sources or []
        if "reference"
        in {
            str(getattr(r, "value", r)).lower()
            for r in (getattr(ds, "roles_in_run", None) or [])
        }
    ]
    out.append(
        Finding(
            kind="MANUAL",
            name="a retrieval corpus comes back with roles_in_run=['reference']",
            ok=None,
            detail=(
                f"{len(set(refs))} papers report a reference-role data source. "
                "Corpus frequency of this shape was 12 names / 23 pairs, so a "
                "flat zero on a RAG-containing sample is the thing to notice"
            ),
            papers=sorted(set(refs)),
        )
    )
    return out


def measurements(corpus: Corpus) -> list[Finding]:
    """#103 section 3: over-splitting and field coverage. No pass condition."""
    per_paper = Counter(len(ex.runs or []) for ex in corpus.papers.values())
    runs = corpus.runs()
    out = [
        Finding(
            kind="MEASURE",
            name="runs per paper",
            ok=None,
            detail=(
                f"{len(runs)} runs over {len(corpus.papers)} papers; "
                "distribution "
                + " ".join(f"{k}:{v}" for k, v in sorted(per_paper.items()))
                + ". Read against what the papers describe -- `runs[]` gives "
                "room to list eight configurations where one sweep happened"
            ),
        )
    ]

    # `repetitions` is a list of factors and the product is computed HERE, not
    # by the extractor: the first v5 run returned prose for 79 of 81 stated
    # values, and asking for the product invited arithmetic it got wrong.
    stated = 0
    kinds: Counter[str] = Counter()
    totals: Counter[int] = Counter()
    suspect: list[str] = []
    WORKLOAD = (
        "episode",
        "item",
        "sample",
        "structure",
        "molecule",
        "example",
        "problem",
        "token",
    )
    for paper, run in runs:
        factors = _value(run, "repetitions") or []
        if not factors:
            continue
        stated += 1
        total = 1
        for factor in factors:
            kinds[str(_value(factor, "kind") or "")] += 1
            count = _value(factor, "count")
            total *= count if isinstance(count, int) and count > 0 else 1
            what = str(getattr(factor, "what", "") or "").lower()
            if any(w in what for w in WORKLOAD):
                suspect.append(f"{paper}:{what[:34]}")
        totals[total] += 1

    out.append(
        Finding(
            kind="MEASURE",
            name="repetitions: factors and product",
            ok=None,
            detail=(
                f"{stated}/{len(runs)} runs state a factor; kinds "
                + (" ".join(f"{k}:{v}" for k, v in kinds.most_common()) or "none")
                + "; product "
                + (" ".join(f"x{k}:{v}" for k, v in sorted(totals.items())) or "none")
                + ". An EMPTY list means the paper did not say, never 1: 5 seeds "
                "x 20 configurations is 100x the compute, so a silent 1 "
                "undercounts compute rather than losing detail"
            ),
        )
    )
    out.append(
        Finding(
            kind="MEASURE",
            name="repetitions misread as workload",
            ok=None,
            detail=(
                f"{len(suspect)} factors describe items PROCESSED rather than "
                "executions repeated -- the v5-prose failure this field was "
                "restructured to stop"
                + (": " + "; ".join(suspect[:5]) if suspect else "")
            ),
        )
    )

    for fld in ("duration", "utilisation", "parallelism", "accelerator_count"):
        present = sum(1 for _, r in runs if _stated(r, fld))
        out.append(
            Finding(
                kind="MEASURE",
                name=f"{fld} coverage",
                ok=None,
                detail=(
                    f"{present}/{len(runs)} runs"
                    + (
                        ". Partial coverage is EXPECTED and accepted -- #92 "
                        "fills gaps from repositories and reference papers. "
                        "This is a baseline, not a target"
                        if fld != "utilisation"
                        else ". Also check the VALUES: Epoch's 30-50% is "
                        "applied later, in analysis. Recorded at extraction "
                        "time it would read as something the paper stated"
                    )
                ),
            )
        )

    access = Counter(
        str(_value(ds, "access")) for _, r in runs for ds in r.data_sources or []
    )
    out.append(
        Finding(
            kind="MEASURE",
            name="access distribution",
            ok=None,
            detail=(
                " ".join(f"{k}:{v}" for k, v in access.most_common())
                + ". `stream` near-zero is EXPECTED and is not evidence "
                "against the value. `interactive` at zero on an RL-containing "
                "sample is the thing to notice"
            ),
        )
    )

    modes = Counter(str(_value(r, "execution_mode")) for _, r in runs)
    out.append(
        Finding(
            kind="MEASURE",
            name="execution_mode distribution",
            ok=None,
            detail=" ".join(f"{k}:{v}" for k, v in modes.most_common()),
        )
    )
    return out


def consistency(corpus: Corpus) -> list[Finding]:
    """``check.py``'s codes, summarised with #103 section 2's readings."""
    counts: Counter[str] = Counter()
    by_code: dict[str, list[str]] = {}
    for paper, ex in corpus.papers.items():
        for problem in check_references(ex, paper=paper):
            counts[problem.code] += 1
            by_code.setdefault(problem.code, []).append(paper)

    readings = {
        "unresolved-reference": (
            "the extractor is not repeating names exactly between runs[] and "
            "the entity lists. A prompt problem, and the one most likely to be "
            "systematic"
        ),
        "referenced-but-not-executed": "is_executed and runs[] contradict each other",
        "execution-mode-disagrees": (
            "RefModel.execution_mode and Run.execution_mode disagree for a "
            "model that ran"
        ),
        "generate-run-with-models": (
            "a generate run references a model -- if a model produced the data "
            "the mode is `inference`"
        ),
        "executed-without-run": (
            "an executed model no run accounts for. EXPECTED IN BULK on "
            "converted data, so read it only on freshly extracted output"
        ),
    }
    return [
        Finding(
            kind="CHECK",
            name=f"check.py: {code}",
            ok=counts.get(code, 0) == 0,
            detail=f"{counts.get(code, 0)} occurrences",
            reading=reading,
            papers=sorted(set(by_code.get(code, [])))[:12],
        )
        for code, reading in readings.items()
    ]


def loaded(corpus: Corpus) -> list[Finding]:
    """How many files actually parsed.

    Separate from the file count because they diverge and the divergence is
    invisible: after `repetitions` became a factor list, 23 of the 25 batch-1
    extractions stopped validating, and the report still opened with "25
    extraction files" while every measurement below it came from the 2 papers
    that happened to have no runs. A header that overstates the corpus turns
    every number under it into a false reading.
    """
    return [
        Finding(
            kind="CHECK",
            name="every file found was readable",
            ok=not corpus.skipped,
            detail=(
                f"{len(corpus.papers)} loaded, {len(corpus.skipped)} skipped"
                + (
                    " -- EVERY MEASUREMENT BELOW EXCLUDES THE SKIPPED FILES"
                    if corpus.skipped
                    else ""
                )
            ),
            reading=(
                "a skipped file validated against no model version. Usually a "
                "schema change the file predates, or a truncated write"
            ),
            papers=corpus.skipped[:12],
        )
    ]


def run(paths: Iterable[Path], probe_sets: dict[str, Any]) -> list[Finding]:
    corpus = Corpus.load(paths)
    return [
        *loaded(corpus),
        *acceptance(corpus),
        *probes(corpus, probe_sets),
        *consistency(corpus),
        *manual(corpus),
        *measurements(corpus),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="extraction files or dirs")
    parser.add_argument("--probe-sets", type=Path, default=PROBE_SETS)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    files: list[Path] = []
    for path in args.paths:
        files.extend(sorted(path.glob("*.json")) if path.is_dir() else [path])
    if not files:
        parser.error(f"no extraction files under {args.paths}")

    probe_sets = json.loads(args.probe_sets.read_text())
    findings = run(files, probe_sets)

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "kind": f.kind,
                        "name": f.name,
                        "ok": f.ok,
                        "detail": f.detail,
                        "papers": f.papers,
                    }
                    for f in findings
                ],
                indent=1,
            )
        )
        return 0

    print(f"{len(files)} extraction files found\n")
    for finding in findings:
        print(finding)
        print()
    failed = [f for f in findings if f.ok is False]
    print(f"{len(failed)} failed of {sum(1 for f in findings if f.ok is not None)}")
    for finding in failed:
        print(f"  - {finding.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
