"""Mechanical comparison of the design proposals. Countable criteria only:
impressions are written separately, afterwards, so they cannot contaminate this."""
from __future__ import annotations

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

DESIGN = Path(__file__).parent
COMPOUND = re.compile(r"\band\b|&|,| / ", re.I)


def load(run: Path) -> list[dict]:
    with (run / "proposal.tsv").open(encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t") if r.get("category")]


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def score(run: Path) -> dict:
    rows = load(run)
    top = [r for r in rows if not (r.get("parent") or "").strip()]
    children = Counter(norm(r["parent"]) for r in rows if (r.get("parent") or "").strip())
    axes = {r.get("axis", "") for r in rows}
    compound = [r["category"] for r in rows if COMPOUND.search(r["category"])]
    thin = [r["category"] for r in rows
            if len([e for e in (r.get("example_children") or "").split(";") if e.strip()]) < 3]
    no_out = [r["category"] for r in rows if not (r.get("scope_out") or "").strip()]
    return {
        "categories": len(rows),
        "top_level": len(top),
        "axes": len(axes),
        "max_branching": max(children.values(), default=0),
        "compound_names": len(compound),
        "compound_examples": compound[:5],
        "fewer_than_3_examples": len(thin),
        "missing_scope_out": len(no_out),
        "depth": 1 + (1 if children else 0),
    }


def overlap(runs: dict[str, list[dict]]) -> None:
    seen: dict[str, set[str]] = defaultdict(set)
    for name, rows in runs.items():
        for r in rows:
            seen[norm(r["category"])].add(name)
    by_count = Counter(len(v) for v in seen.values())
    print(f"\ncategory-name overlap across {len(runs)} runs (exact, normalised):")
    for n in sorted(by_count, reverse=True):
        print(f"   in {n} run(s): {by_count[n]}")
    shared = sorted(k for k, v in seen.items() if len(v) == len(runs))
    print(f"   present in all: {', '.join(shared) if shared else '(none)'}")


if __name__ == "__main__":
    runs = {}
    for run in sorted(DESIGN.glob("run*")):
        if not (run / "proposal.tsv").exists():
            print(f"{run.name}: no proposal.tsv yet")
            continue
        runs[run.name] = load(run)
        print(f"\n== {run.name}")
        for k, v in score(run).items():
            print(f"   {k}: {v}")
    if len(runs) > 1:
        overlap(runs)
