"""Consistency checks over one paper's extractions, reported rather than raised.

Schema v5 gave ``runs[]`` references into the top-level entity lists, spelled as
verbatim names rather than ids (``data/ontology/design/SCHEMA_V5_STRUCTURE.md``
section 4). Nothing in the schema can enforce that a reference resolves, and
nothing should: extraction runs inside an ``instructor`` retry loop, so a
validator that raised would discard a whole paper's extraction over one mistyped
name. The reference check therefore lives here and runs afterwards -- the same
shape as ``axes_algorithms/resolve.py --audit``, which reports what it finds and
leaves the reading to a person.

Run it over a corpus with::

    uv run python -m paperext.structured_output.mdl.check --details
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator

import pydantic_core
import yaml

from paperext import CFG
from paperext.log import logger
from paperext.utils import str_normalize

#: ``runs[]`` list attribute -> the top-level entity list it references.
REFERENCE_FIELDS: dict[str, str] = {
    "models": "models",
    "data_sources": "data_sources",
    "algorithms": "algorithms",
}

#: A reference naming nothing in the corresponding entity list. The most likely
#: cause is a spelling the extractor did not repeat exactly.
UNRESOLVED_REFERENCE = "unresolved-reference"
#: A run references an entity the paper says was not executed. One of the two
#: statements is wrong; `is_executed` is the gate for whether a run exists at
#: all, so a run pointing at a `False` is a contradiction, not a gap.
REFERENCED_BUT_NOT_EXECUTED = "referenced-but-not-executed"
#: `RefModel.execution_mode` and `Run.execution_mode` disagree for a model the
#: paper ran. The model-level field exists for models with no run; where both
#: exist they are the same claim, so disagreement is free evidence of an error.
EXECUTION_MODE_DISAGREES = "execution-mode-disagrees"
#: A `generate` run that references a model. `generate` means the run's cost is
#: not parameter-shaped; if a model produced the data, the mode is `inference`.
#: Encodes that discriminator directly, so a mode that would send the estimator
#: to the wrong formula is reported rather than silently accepted.
GENERATE_RUN_WITH_MODELS = "generate-run-with-models"
#: An executed model no run accounts for. Expected in bulk on converted data --
#: `convert_model_v4` leaves `runs[]` empty because v4 held no compute
#: configuration to carry over -- so read it per-corpus, not per-record.
EXECUTED_WITHOUT_RUN = "executed-without-run"


@dataclass(frozen=True)
class Problem:
    """One finding. ``where`` is a path into the extractions, for locating it."""

    code: str
    where: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code}\t{self.where}\t{self.detail}"


def _surfaces(entry: Any) -> set[str]:
    """Every spelling an entity answers to: its name plus its written aliases.

    Aliases count, but similarity never does. An unresolved reference is
    reported, not repaired by the nearest match -- string similarity is what
    paired `gpt-j` with `GPT-4` and put `bayesian neural networks` under the
    graphical-model node, and a wrong repair is worse than a reported gap.
    """
    name = getattr(getattr(entry, "name", None), "value", "") or ""
    out = {str_normalize(name)} if name.strip() else set()
    for alias in getattr(entry, "aliases", None) or []:
        if alias.strip():
            out.add(str_normalize(alias))
    return out


def _executed(entry: Any) -> bool | None:
    value = getattr(getattr(entry, "is_executed", None), "value", None)
    return value if isinstance(value, bool) else None


def _mode(obj: Any) -> str | None:
    value = getattr(getattr(obj, "execution_mode", None), "value", None)
    value = getattr(value, "value", value)
    return value if isinstance(value, str) and value != "unknown" else None


def check_references(extractions: Any, *, paper: str = "") -> list[Problem]:
    """Every consistency problem in one paper's extractions.

    Returns an empty list for a paper with no runs, which is the common and
    correct case: most papers name a procedure without tying it to a compute
    configuration, and converted pre-v5 records have no runs at all.
    """
    problems: list[Problem] = []
    prefix = f"{paper}:" if paper else ""

    index: dict[str, dict[str, Any]] = {}
    for field in REFERENCE_FIELDS.values():
        index[field] = {
            surface: entry
            for entry in getattr(extractions, field, None) or []
            for surface in _surfaces(entry)
        }

    # Which models a run accounts for, for EXECUTED_WITHOUT_RUN below.
    accounted: set[str] = set()

    for i, run in enumerate(getattr(extractions, "runs", None) or []):
        run_mode = _mode(run)

        if run_mode == "generate" and (getattr(run, "models", None) or []):
            names = [
                (getattr(m, "name", "") or "").strip()
                for m in (getattr(run, "models", None) or [])
            ]
            problems.append(
                Problem(
                    GENERATE_RUN_WITH_MODELS,
                    f"{prefix}runs[{i}]",
                    f"execution_mode is 'generate' but the run references "
                    f"{names}; a model producing the data makes it 'inference'",
                )
            )

        for ref_field, entity_field in REFERENCE_FIELDS.items():
            for j, ref in enumerate(getattr(run, ref_field, None) or []):
                where = f"{prefix}runs[{i}].{ref_field}[{j}]"
                name = (getattr(ref, "name", "") or "").strip()
                if not name:
                    problems.append(Problem(UNRESOLVED_REFERENCE, where, "empty name"))
                    continue

                entry = index[entity_field].get(str_normalize(name))
                if entry is None:
                    problems.append(
                        Problem(
                            UNRESOLVED_REFERENCE,
                            where,
                            f"{name!r} names nothing in {entity_field}[]",
                        )
                    )
                    continue

                if entity_field == "models":
                    accounted |= _surfaces(entry)

                if _executed(entry) is False:
                    problems.append(
                        Problem(
                            REFERENCED_BUT_NOT_EXECUTED,
                            where,
                            f"{name!r} has is_executed=False but a run executes it",
                        )
                    )

                entry_mode = _mode(entry)
                if (
                    entity_field == "models"
                    and run_mode is not None
                    and entry_mode is not None
                    and entry_mode != run_mode
                ):
                    problems.append(
                        Problem(
                            EXECUTION_MODE_DISAGREES,
                            where,
                            f"{name!r} says {entry_mode!r}, its run says {run_mode!r}",
                        )
                    )

    for i, model in enumerate(getattr(extractions, "models", None) or []):
        if _executed(model) is not True:
            continue
        if _surfaces(model) & accounted:
            continue
        name = getattr(getattr(model, "name", None), "value", "") or ""
        problems.append(
            Problem(
                EXECUTED_WITHOUT_RUN,
                f"{prefix}models[{i}]",
                f"{name!r} is executed but no run references it",
            )
        )

    return problems


def iter_extractions(paths: Iterable[Path]) -> Iterator[tuple[Path, Any]]:
    """``(path, extractions)`` for every readable extraction file, up-converted.

    Unreadable files are logged and skipped rather than raised on, for the same
    reason the reference check reports: a corpus pass must survive one bad file.
    Shared with :mod:`paperext.structured_output.mdl.verify` so both read the
    corpus the same way -- two loaders would be two version-detection rules.
    """
    from paperext.structured_output.mdl import model as dest_model
    from paperext.structured_output.mdl.convert import (
        CONVERT_CHAIN,
        CONVERT_MODEL,
        _detect_version,
    )

    for path in paths:
        text = path.read_text()
        try:
            data = json.loads(text)
        except json.decoder.JSONDecodeError:
            try:
                data = yaml.safe_load(text)
            except yaml.YAMLError:
                logger.warning("%s: not JSON or YAML, skipped", path)
                continue

        try:
            module, _, extractions = _detect_version(data)
        except pydantic_core._pydantic_core.ValidationError:
            module, extractions = None, None

        if module is None or extractions is None:
            logger.warning("%s: validates against no model version, skipped", path)
            continue

        if module is not dest_model:
            for src in CONVERT_CHAIN[CONVERT_CHAIN.index(module) :]:
                convert: Any = CONVERT_MODEL[src]
                extractions = convert(extractions)

        yield path, extractions


def check_paths(paths: Iterable[Path]) -> Iterator[tuple[Path, list[Problem]]]:
    """``(path, problems)`` for every extraction file, up-converted first."""
    for path, extractions in iter_extractions(paths):
        yield path, check_references(extractions, paper=path.stem)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="paperext.structured_output.mdl.check",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="extraction files to check; defaults to the configured corpus",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="print every problem, not just the count per code",
    )
    args = parser.parse_args(argv)

    # `CFG.dir` is typed `Config | Path` project-wide, so the attribute access
    # below is only resolvable at runtime.
    corpus: Any = CFG.dir
    paths = args.paths or sorted(
        p
        for root in (corpus.merged, corpus.queries)
        for p in [*root.rglob("*.json"), *root.rglob("*.yaml")]
    )

    counts: Counter[str] = Counter()
    checked = 0
    for _, problems in check_paths(paths):
        checked += 1
        for problem in problems:
            counts[problem.code] += 1
            if args.details:
                print(problem)

    print(f"checked {checked} file(s)")
    for code, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{count:7d}  {code}")
    if not counts:
        print("      0  problems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
