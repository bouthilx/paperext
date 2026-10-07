"""Idempotent migration for the three attribute families split in D.1.

Re-runnable: each rule replaces a retired value if present and does nothing
otherwise, so it can be applied again after merging an agent's edits.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent.parent
cells = lambda s: [x.strip() for x in re.split(r"[;,]", s) if x.strip()]

SEQ = {
    "L.pref",
    "L.ar",
    "L.dec.beam",
    "L.dec.constr",
    "L.dec.rerank",
    "L.seq.hmm",
    "L.seq.crf",
    "L.anom.cp",
    "M.baum-welch",
    "M.bayesian-online-change-point-detection",
    "M.crf",
    "M.cusum",
    "M.hmm",
    "M.hsmm",
    "M.memm",
    "M.pelt",
    "M.pixelcnn",
    "M.pixelrnn",
    "M.viterbi",
    "M.wavenet-training",
    "M.beam-search-as-search",
    "M.causal-lm-pretraining",
    "M.forward-backward",
    "M.linear-chain-crf",
    "M.matrix-profile",
    "M.n-gram-mle",
    "M.neural-lm",
}
RANK = {
    "L.rec.ltr",
    "M.lambdamart",
    "M.lambdarank",
    "M.listmle",
    "M.listnet",
    "M.ranknet",
}
TREE = {"L.tts.tree"}
# genuinely general structured predictors keep the interior node: they span shapes
INTERIOR = {"M.structured-svm", "M.structured-perceptron"}


def outstruct(nid: str) -> str:
    if nid in SEQ:
        return "A.outstruct.seq"
    if nid in RANK:
        return "A.outstruct.rank"
    if nid in TREE:
        return "A.outstruct.tree"
    if nid in INTERIOR:
        return "A.outstruct"
    return "A.outstruct.seq"


PARTIES = {
    "A.topology.feddev": "A.parties.device",
    "A.topology.fedsilo": "A.parties.silo",
}


def main() -> int:
    p = HERE / "lineage" / "nodes.tsv"
    rows = list(csv.DictReader(p.open(newline=""), delimiter="\t"))
    cols = list(rows[0].keys())
    n = 0
    for r in rows:
        vals = cells(r["attributes"])
        out: list[str] = []
        changed = False
        for v in vals:
            neg, bare = v.startswith("!"), v.lstrip("!")
            if bare == "A.outspace.struct":
                out.append(("!" if neg else "") + outstruct(r["node_id"]))
                changed = True
            elif bare in PARTIES:
                out.append(("!" if neg else "") + PARTIES[bare])
                changed = True
                # federated rounds are synchronous unless the node says otherwise
                if not any(x.lstrip("!").startswith("A.topology.") for x in vals):
                    out.append("A.topology.csync")
            else:
                out.append(v)
        if changed:
            seen: list[str] = []
            for v in out:
                if v not in seen:
                    seen.append(v)
            r["attributes"] = "; ".join(seen)
            r["notes"] = (
                (r["notes"] + "; " if r["notes"] else "")
                + "attributes migrated: A.outspace.struct -> A.outstruct.*, federated party values -> A.parties.*"
            )
            n += 1
    p.write_text(
        "\t".join(cols)
        + "\n"
        + "".join("\t".join(x.get(c, "") for c in cols) + "\n" for x in rows)
    )
    print(f"migrated {n} nodes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
