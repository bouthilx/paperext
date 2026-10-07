#!/usr/bin/env python3
"""Render the faceted ontology as an indented tree. Usage: render_tree.py [maxdepth]"""

import os
import sys

AX = [
    ("method", "METHOD — how does the work produce its result?"),
    ("modality", "MODALITY / DATA — what kind of signal does it operate on?"),
    ("properties", "DESIRED PROPERTIES — what property does it try to secure?"),
    (
        "discipline",
        "SCIENTIFIC DISCIPLINE — whose knowledge does it advance? (OECD FOS)",
    ),
    ("sector", "SECTOR — whose operational problem does it solve? (ISIC Rev.4)"),
]
MAXD = int(sys.argv[1]) if len(sys.argv) > 1 else 3
root = os.path.dirname(os.path.abspath(__file__))
for d, title in AX:
    f = os.path.join(root, "axes", d, "nodes.tsv")
    if not os.path.exists(f):
        print(f"\n### {title}\n  (not derived)")
        continue
    rows = [l.rstrip("\n").split("\t") for l in open(f) if l.strip()]
    i = {k.strip(): n for n, k in enumerate(rows[0])}

    def g(r, k, dflt=""):
        n = i.get(k)
        return r[n].strip() if n is not None and n < len(r) else dflt

    kids = {}
    for r in rows[1:]:
        if g(r, "node_id"):
            kids.setdefault(g(r, "parent_id"), []).append(r)
    print(f"\n### {title}\n    [{sum(len(v) for v in kids.values())} nodes]")

    def walk(pid, prefix=""):
        ch = kids.get(pid, [])
        for n, r in enumerate(ch):
            if int(g(r, "depth", "1") or 1) > MAXD:
                continue
            last = n == len(ch) - 1
            m = g(r, "corpus_mentions")
            m = f"  ({m})" if m and m != "0" else ""
            print(f"{prefix}{'└── ' if last else '├── '}{g(r,'name')}{m}")
            walk(g(r, "node_id"), prefix + ("    " if last else "│   "))

    walk("")
