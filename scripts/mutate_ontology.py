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

from print_ontology_tree import find_nodes, print_tree

from paperext.categorize.actions import OPS
from paperext.categorize.apply import diff_snapshots
from paperext.ontology import Ontology
from paperext.ontology.ontology import OntologyError

# CLI spelling -> op name in `paperext.categorize.actions.OPS`, which is the single
# source of truth for the mutation vocabulary (method, argument order, and which
# args must name an existing node). Keeping the table there rather than here is
# what stops this harness and the D1b applier from drifting apart.
CLI_OPS: dict[str, str | None] = {
    "create-node": "create_node",
    "rename": "rename",
    "update-description": "update_description",
    "add-surface": "add_surface",
    "remove-surface": "remove_surface",
    "move": "move",
    "insert-above": "insert_above",
    "demote": "demote_to_variant",
    "remove": "remove_node",
    "mark-ignore": "mark_ignore",
    "check": None,  # no-op: just load + check_invariants + print
}

# `examples` takes a list, which argparse cannot express as a single --flag here.
_CLI_SKIP_OPTIONAL = {"examples"}


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
    for cli_op, op in CLI_OPS.items():
        spec = OPS[op] if op else None
        positionals = spec.positional if spec else ()
        optionals = [
            o for o in (spec.optional if spec else ()) if o not in _CLI_SKIP_OPTIONAL
        ]
        sp = sub.add_parser(cli_op, help=f"{cli_op} {' '.join(positionals)}".strip())
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


def _snapshot(o: Ontology) -> tuple[dict, list[dict]]:
    return o.doc.model_dump(), [r.model_dump() for r in o.norm]


def _entry(node_id: str, dump: dict) -> str:
    """A node rendered exactly as its entry appears in ``ontology.json``."""
    body = json.dumps(dump, indent=2, ensure_ascii=False)
    text = f"{json.dumps(node_id, ensure_ascii=False)}: {body}"
    return "\n".join("  " + line for line in text.splitlines())


def print_changes(
    before: tuple[dict, list[dict]], after: tuple[dict, list[dict]]
) -> None:
    """Render the node/root/normalization diff the D1b audit record stores."""
    diff = diff_snapshots(before, after)
    before_nodes, after_nodes = before[0]["nodes"], after[0]["nodes"]

    print("# node changes (ontology.json):")
    if not (diff.created or diff.modified or diff.deleted):
        print("  (none)")
    for nid in diff.created:
        print("+ created")
        print(_entry(nid, after_nodes[nid]))
    for nid in diff.modified:
        print("~ modified")
        print(_entry(nid, after_nodes[nid]))
    for nid in diff.deleted:
        print("- deleted")
        print(_entry(nid, before_nodes[nid]))

    if diff.roots_added or diff.roots_removed:
        print(f"# roots changed: +{diff.roots_added} -{diff.roots_removed}")

    if diff.surfaces_added or diff.surfaces_removed:
        print("# normalization changes (normalization.jsonl):")
        for surface, canonical in diff.surfaces_added:
            print(f'+ "{surface}" -> "{canonical}"')
        for surface, canonical in diff.surfaces_removed:
            print(f'- "{surface}" -> "{canonical}"')


def main() -> None:
    args = build_parser().parse_args()
    o = Ontology.load(args.version_dir)

    op = CLI_OPS[args.op]
    if op is not None:
        spec = OPS[op]
        pos = [
            (
                resolve_ref(o, getattr(args, name))
                if name in spec.noderefs
                else getattr(args, name)
            )
            for name in spec.positional
        ]
        kw = {}
        for name in spec.optional:
            val = getattr(args, name, None)
            if val is None:
                continue
            kw[name] = resolve_ref(o, val) if name in spec.noderefs else val

        before = _snapshot(o)
        try:
            getattr(o, spec.method)(*pos, **kw)
        except OntologyError as e:
            print(f"REJECTED ({type(e).__name__}): {e}", file=sys.stderr)
            raise SystemExit(1)
        print(f"# applied: {args.op} {' '.join(map(str, pos))}".rstrip())
        print_changes(before, _snapshot(o))

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
