"""Apply one mutation to an ontology and print the result — a manual test harness
for the D1a-2 mutation API (#42).

Loads a version dir, applies a single op, prints the created/modified/deleted
nodes exactly as their entries appear in ``ontology.json`` (plus any ``roots`` and
``normalization.jsonl`` changes), runs ``check_invariants()``, then prints the
(sub)tree with the same options as ``print_ontology_tree.py`` (``--node`` /
``--depth`` / ``--examples``). The edit is **in memory only** unless you pass
``--save DIR`` — so it never clobbers the committed ``v0``.

Examples:
    # move a node, then show the destination subtree two levels deep
    python scripts/mutate_ontology.py data/ontology/models/v0 \
        move resnet optimizer --node optimizer --depth 1

    # fold a node into another as a surface variant, inspect the target
    python scripts/mutate_ontology.py data/ontology/models/v0 \
        demote resnet-50 resnet --node resnet

    # a rejected op prints the reason and exits 1 (state untouched)
    python scripts/mutate_ontology.py data/ontology/models/v0 remove optimizer

    # persist the mutated snapshot elsewhere to test the round-trip
    python scripts/mutate_ontology.py data/ontology/models/v0 \
        rename resnet "ResNet (residual net)" --save /tmp/models_v1 --node resnet
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from print_ontology_tree import find_nodes, print_tree

from paperext.ontology import Ontology
from paperext.ontology.ontology import OntologyError

# op name -> (Ontology method, positional arg names, optional-arg names, noderefs)
# `noderefs` lists the args that name an *existing* node: they accept either a raw
# node id or a display name (resolved to its id). Everything else is literal — new
# ids for create/insert, free text for names/descriptions, and surface strings.
OPS: dict[str, tuple[str | None, list[str], list[str], set[str]]] = {
    "create-node": (
        "create_node",
        ["node_id", "name"],
        ["parent", "description"],
        {"parent"},
    ),
    "rename": ("rename", ["node_id", "new_name"], [], {"node_id"}),
    "update-description": (
        "update_description",
        ["node_id", "description"],
        [],
        {"node_id"},
    ),
    "add-surface": ("add_surface", ["surface", "canonical"], ["via"], {"canonical"}),
    "remove-surface": ("remove_surface", ["surface"], [], set()),
    "move": ("move", ["node_id", "new_parent"], [], {"node_id", "new_parent"}),
    "insert-above": ("insert_above", ["node_id", "new_id", "name"], [], {"node_id"}),
    "demote": (
        "demote_to_variant",
        ["node_id", "target_id"],
        [],
        {"node_id", "target_id"},
    ),
    "remove": ("remove_node", ["node_id"], [], {"node_id"}),
    "mark-ignore": ("mark_ignore", ["node_id"], [], {"node_id"}),
    "check": (None, [], [], set()),  # no-op: just load + check_invariants + print
}


def resolve_ref(o: Ontology, value: str) -> str:
    """Map a node-reference arg to an id, accepting an id or a display name."""
    if value in o.nodes:
        return value
    matches = find_nodes(o, value)
    if len(matches) == 1:
        if matches[0] != value:
            print(f"# resolved {value!r} -> id {matches[0]!r}")
        return matches[0]
    if not matches:
        raise SystemExit(f"no node id or name matches {value!r}")
    paths = "; ".join(" > ".join(o.name(a) for a in o.ancestry(m)) for m in matches)
    raise SystemExit(f"{value!r} is ambiguous ({len(matches)} matches): {paths}")


def add_print_opts(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--node", help="print only the subtree under this node (name or dot-path)"
    )
    p.add_argument(
        "--depth",
        type=int,
        default=None,
        metavar="N",
        help="max levels below the printed root (0 = root only)",
    )
    p.add_argument("--examples", action="store_true", help="show each node's examples")
    p.add_argument(
        "--save",
        metavar="DIR",
        help="persist the mutated snapshot to DIR (default: in memory only)",
    )


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("version_dir", help="e.g. data/ontology/models/v0")
    sub = ap.add_subparsers(dest="op", required=True, metavar="OP")
    for op, (_method, positionals, optionals, _refs) in OPS.items():
        sp = sub.add_parser(op, help=f"{op} {' '.join(positionals)}".strip())
        for name in positionals:
            sp.add_argument(name)
        for name in optionals:
            sp.add_argument(f"--{name}", default=None)
        add_print_opts(sp)
    return ap


def print_result(o: Ontology, args: argparse.Namespace) -> None:
    if args.node is None:
        for rid in o.roots:
            print_tree(o, rid, show_examples=args.examples, max_depth=args.depth)
        return
    matches = find_nodes(o, args.node)
    if not matches:
        print(f"(no node matches {args.node!r})", file=sys.stderr)
        return
    for i, nid in enumerate(matches):
        if len(matches) > 1:
            path = " > ".join(o.name(a) for a in o.ancestry(nid))
            print(f"# match {i + 1}/{len(matches)}: {path}")
        print_tree(o, nid, show_examples=args.examples, max_depth=args.depth)
        if i != len(matches) - 1:
            print()


def _nodes_dump(o: Ontology) -> dict[str, dict]:
    return {nid: node.model_dump() for nid, node in o.doc.nodes.items()}


def _norm_pairs(o: Ontology) -> list[tuple[str, str]]:
    return [(r.surface, r.canonical) for r in o.norm]


def _entry(node_id: str, dump: dict) -> str:
    """A node rendered exactly as its entry appears in ``ontology.json``."""
    body = json.dumps(dump, indent=2, ensure_ascii=False)
    text = f"{json.dumps(node_id, ensure_ascii=False)}: {body}"
    return "\n".join("  " + line for line in text.splitlines())


def print_changes(
    before: dict[str, dict],
    after: dict[str, dict],
    before_roots: list[str],
    after_roots: list[str],
    before_norm: list[tuple[str, str]],
    after_norm: list[tuple[str, str]],
) -> None:
    created = [nid for nid in after if nid not in before]
    modified = [nid for nid in after if nid in before and after[nid] != before[nid]]
    deleted = [nid for nid in before if nid not in after]

    print("# node changes (ontology.json):")
    if not (created or modified or deleted):
        print("  (none)")
    for nid in created:
        print("+ created")
        print(_entry(nid, after[nid]))
    for nid in modified:
        print("~ modified")
        print(_entry(nid, after[nid]))
    for nid in deleted:
        print("- deleted")
        print(_entry(nid, before[nid]))

    if before_roots != after_roots:
        added = [r for r in after_roots if r not in before_roots]
        removed = [r for r in before_roots if r not in after_roots]
        print(f"# roots changed: +{added} -{removed}")

    diff_add = list((Counter(after_norm) - Counter(before_norm)).elements())
    diff_del = list((Counter(before_norm) - Counter(after_norm)).elements())
    if diff_add or diff_del:
        print("# normalization changes (normalization.jsonl):")
        for surface, canonical in diff_add:
            print(f'+ "{surface}" -> "{canonical}"')
        for surface, canonical in diff_del:
            print(f'- "{surface}" -> "{canonical}"')


def main() -> None:
    args = build_parser().parse_args()
    o = Ontology.load(args.version_dir)

    method_name, positionals, optionals, refs = OPS[args.op]
    if method_name is not None:
        pos = [
            resolve_ref(o, getattr(args, name)) if name in refs else getattr(args, name)
            for name in positionals
        ]
        kw = {}
        for name in optionals:
            val = getattr(args, name)
            if val is None:
                continue
            kw[name] = resolve_ref(o, val) if name in refs else val

        before_nodes, before_roots, before_norm = (
            _nodes_dump(o),
            list(o.doc.roots),
            _norm_pairs(o),
        )
        try:
            getattr(o, method_name)(*pos, **kw)
        except OntologyError as e:
            print(f"REJECTED ({type(e).__name__}): {e}", file=sys.stderr)
            raise SystemExit(1)
        print(f"# applied: {args.op} {' '.join(map(str, pos))}".rstrip())
        print_changes(
            before_nodes,
            _nodes_dump(o),
            before_roots,
            list(o.doc.roots),
            before_norm,
            _norm_pairs(o),
        )

    try:
        o.check_invariants()
    except OntologyError as e:
        print(
            f"INVARIANT VIOLATION after op ({type(e).__name__}): {e}", file=sys.stderr
        )
        raise SystemExit(2)

    if args.save:
        o.save(args.save)
        print(f"# saved snapshot -> {args.save}")

    print_result(o, args)


if __name__ == "__main__":
    main()
