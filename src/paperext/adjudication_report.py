"""Agreement between the assistant's recommendation and the owner's decision.

The reference-annotation sessions (#111 Part B) log one row per adjudicated
field. This reads that log and answers the question it exists for: **how often
was the assistant right, and on which fields** -- which bounds how much of the
annotation could be automated.

    uv run python -m paperext.adjudication_report

A row whose `recommended` is `(not recorded)` is counted as UNSCORED rather than
as agreement. The first three papers were logged before that column existed, and
silently treating them as agreement would overstate the rate on exactly the
papers where the owner overruled most.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from paperext.utils import str_normalize

LOG = Path("data/ontology/design/c0_verification/adjudication_log.tsv")

#: Placeholders that mean "no prediction was recorded", not "no prediction".
UNRECORDED = {"", "(not recorded)", "-", "n/a", "pending"}


def classify(row: "dict[str, str]") -> str:
    """``agreed`` / ``overruled`` / ``unscored`` for one logged decision."""
    rec = (row.get("recommended") or "").strip()
    chosen = (row.get("chosen") or "").strip()
    if rec.lower() in UNRECORDED or chosen.lower() in UNRECORDED:
        return "unscored"
    return "agreed" if str_normalize(rec) == str_normalize(chosen) else "overruled"


def report(path: Path = LOG) -> int:
    if not path.is_file():
        print(f"no log at {path}")
        return 1
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    if not rows:
        print("log is empty")
        return 0

    by_field: "dict[str, Counter[str]]" = {}
    by_paper: "dict[str, Counter[str]]" = {}
    for row in rows:
        verdict = classify(row)
        by_field.setdefault(row.get("field", "?"), Counter())[verdict] += 1
        by_paper.setdefault(row.get("paper_id", "?"), Counter())[verdict] += 1

    def line(label: str, c: "Counter[str]") -> str:
        scored = c["agreed"] + c["overruled"]
        rate = f"{c['agreed'] / scored:5.0%}" if scored else "    -"
        return (
            f"{label:34} {rate}   agreed {c['agreed']:3}  "
            f"overruled {c['overruled']:3}  unscored {c['unscored']:3}"
        )

    total: "Counter[str]" = Counter()
    for c in by_field.values():
        total.update(c)

    print(f"{len(rows)} logged decisions over {len(by_paper)} papers\n")
    print("by field:")
    for field, c in sorted(by_field.items(), key=lambda kv: -sum(kv[1].values())):
        print("  " + line(field, c))
    print("\nby paper, in log order:")
    for paper, c in by_paper.items():
        print("  " + line(paper[:18], c))
    print("\n  " + line("TOTAL", total))

    if total["unscored"]:
        print(
            f"\n{total['unscored']} decisions are UNSCORED -- `recommended` was "
            "not recorded, so they say nothing about the assistant either way. "
            "Counting them as agreement would overstate the rate."
        )
    return 0


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, default=LOG)
    return report(parser.parse_args(argv).log)


if __name__ == "__main__":
    raise SystemExit(main())
