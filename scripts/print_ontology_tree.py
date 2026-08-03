"""Print an ontology version dir as a `tree`-style structure.

Usage:
    # whole tree
    python scripts/print_ontology_tree.py data/ontology/models/v0

    # only the subtree(s) under a node, selected by name (case-insensitive)
    python scripts/print_ontology_tree.py data/ontology/models/v0 --node optimizer

    # disambiguate a name collision with a dot-path suffix of the ancestry
    python scripts/print_ontology_tree.py data/ontology/models/v0 \
        --node clipped-sgd.clipped-sgda

    # show each node's example surfaces
    python scripts/print_ontology_tree.py data/ontology/domains/v0 --examples
"""

from __future__ import annotations

import argparse

from paperext.analysis.rollup import str_normalize
from paperext.ontology.ontology import Ontology


def find_nodes(o: Ontology, node_str: str) -> list[str]:
    """Node ids whose normalized ancestry ends with *node_str*'s dot-path.

    ``"optimizer"`` matches every node named ``optimizer``; ``"a.b"`` matches a
    node ``b`` whose parent is ``a``. Matching is per-segment normalized, so it is
    case- and punctuation-insensitive. Results are in DFS order.
    """
    target = tuple(str_normalize(seg) for seg in node_str.split("."))
    n = len(target)
    return [
        nid
        for nid, norm_path, _ in o.iter_nodes()
        if len(norm_path) >= n and norm_path[-n:] == target
    ]


def print_tree(
    o: Ontology,
    start_id: str,
    show_examples: bool = False,
    max_depth: int | None = None,
) -> None:
    def label(nid: str, truncated: bool) -> str:
        text = o.name(nid)
        if show_examples:
            ex = o.examples(nid)
            if ex:
                text += f"  ({', '.join(ex)})"
        if truncated:
            text += f" [+{len(o.children(nid))}]"
        return text

    def walk(nid: str, prefix: str, is_last: bool, is_root: bool, depth: int) -> None:
        if is_root:
            branch, child_prefix = "", ""
        else:
            branch = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")
        children = o.children(nid)
        at_limit = max_depth is not None and depth >= max_depth
        print(prefix + branch + label(nid, truncated=at_limit and bool(children)))
        if at_limit:
            return
        for i, cid in enumerate(children):
            walk(cid, child_prefix, i == len(children) - 1, False, depth + 1)

    walk(start_id, "", True, is_root=True, depth=0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("version_dir", help="e.g. data/ontology/models/v0")
    ap.add_argument(
        "--node",
        help="print only the subtree under this node (name or dot-path suffix); "
        "prints every match when the name is ambiguous",
    )
    ap.add_argument(
        "--depth",
        type=int,
        default=None,
        metavar="N",
        help="max levels below the selected root to print (0 = root only); "
        "a truncated node is tagged [+K] with its hidden child count",
    )
    ap.add_argument(
        "--examples", action="store_true", help="show each node's example surfaces"
    )
    args = ap.parse_args()

    if args.depth is not None and args.depth < 0:
        raise SystemExit(f"--depth must be >= 0, got {args.depth}")

    o = Ontology.load(args.version_dir)

    if args.node is None:
        for rid in o.roots:
            print_tree(o, rid, show_examples=args.examples, max_depth=args.depth)
        return

    matches = find_nodes(o, args.node)
    if not matches:
        raise SystemExit(
            f"no node matches {args.node!r}; try `--node` with a broader name, "
            "or search interactively with Ontology.search()"
        )
    for i, nid in enumerate(matches):
        if len(matches) > 1:
            path = " > ".join(o.name(a) for a in o.ancestry(nid))
            print(f"# match {i + 1}/{len(matches)}: {path}")
        print_tree(o, nid, show_examples=args.examples, max_depth=args.depth)
        if i != len(matches) - 1:
            print()


if __name__ == "__main__":
    main()
