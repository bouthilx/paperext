"""The :class:`Ontology` read object — load, index, accessors, search (D1a, #36).

Parses a versioned snapshot once and builds the in-memory indexes the D1b payload
needs: surface -> canonical, node -> surfaces (reverse), and node -> parents. All
accessors are O(1)/O(depth) against those indexes.

On-disk is diffable and DAG-ready; in-memory is indexed. The read/index/accessor
half is D1a-1; the mutation API (edit + re-index + invariant enforcement) is D1a-2
(#42) — every mutator guards its preconditions *before* touching state, so a
rejected edit leaves the object unchanged, then calls :meth:`_reindex`.
"""

import json
from pathlib import Path
from typing import Iterator, Union

from paperext.analysis.rollup import DEFAULT_DROP_ROOTS, str_normalize
from paperext.ontology.schema import Meta, Node, NormRow, OntologyDoc

ONTOLOGY_FILE = "ontology.json"
NORMALIZATION_FILE = "normalization.jsonl"


class OntologyError(Exception):
    """Base class for mutation/invariant violations (D1a-2, #42)."""


class DuplicateNodeError(OntologyError):
    """A node id that must be new already exists."""


class UnknownNodeError(OntologyError):
    """An operation referenced a node id that is not in the tree."""


class CycleError(OntologyError):
    """An edit would make a node its own ancestor."""


class InvariantError(OntologyError):
    """A structural invariant would be (or is) violated.

    Covers referential integrity (dangling child/canonical), orphaned nodes,
    the 1:1 surface rule, and empty-name / has-children preconditions.
    """


class Ontology:
    """An indexed, read-only view over one ontology snapshot."""

    def __init__(self, doc: OntologyDoc, norm: "list[NormRow]"):
        self.doc = doc
        self.norm = norm
        self._reindex()

    # -- construction ---------------------------------------------------------

    @classmethod
    def load(cls, version_dir: Union[str, Path]) -> "Ontology":
        """Load ``ontology.json`` + ``normalization.jsonl`` from *version_dir*."""
        version_dir = Path(version_dir)
        doc = OntologyDoc.model_validate_json((version_dir / ONTOLOGY_FILE).read_text())
        norm: "list[NormRow]" = []
        norm_path = version_dir / NORMALIZATION_FILE
        if norm_path.exists():
            for line in norm_path.read_text().splitlines():
                line = line.strip()
                if line:
                    norm.append(NormRow.model_validate_json(line))
        return cls(doc, norm)

    def _reindex(self) -> None:
        self.nodes: "dict[str, Node]" = self.doc.nodes
        self.roots: "list[str]" = self.doc.roots

        # parents adjacency (derived; DAG-ready — a node may have several).
        self._parents: "dict[str, list[str]]" = {nid: [] for nid in self.nodes}
        for pid, node in self.nodes.items():
            for cid in node.children:
                self._parents.setdefault(cid, []).append(pid)

        # normalization indexes: surface -> canonical (1:1) and its reverse.
        self._surface_to_canonical: "dict[str, str]" = {}
        self._node_surfaces: "dict[str, list[str]]" = {nid: [] for nid in self.nodes}
        for row in self.norm:
            self._surface_to_canonical[row.surface] = row.canonical
            self._node_surfaces.setdefault(row.canonical, []).append(row.surface)

    # -- basic accessors ------------------------------------------------------

    def __contains__(self, node_id: str) -> bool:
        return node_id in self.nodes

    def node(self, node_id: str) -> Node:
        return self.nodes[node_id]

    def name(self, node_id: str) -> str:
        return self.nodes[node_id].name

    def children(self, node_id: str) -> "list[str]":
        return list(self.nodes[node_id].children)

    def parents(self, node_id: str) -> "list[str]":
        return list(self._parents.get(node_id, []))

    def examples(self, node_id: str) -> "list[str]":
        return list(self.nodes[node_id].examples)

    def surfaces(self, node_id: str) -> "list[str]":
        """All surface forms that normalize to *node_id*."""
        return list(self._node_surfaces.get(node_id, []))

    def root_map(self) -> "dict[str, str]":
        """``{root_id: name}`` in declared order."""
        return {rid: self.nodes[rid].name for rid in self.roots}

    def ancestry(self, node_id: str) -> "list[str]":
        """Primary path from root to *node_id* (inclusive).

        Follows the first parent at each step (single-primary convention). Guards
        against cycles defensively even though the invariants forbid them.
        """
        path = [node_id]
        seen = {node_id}
        cur = node_id
        while True:
            parents = self._parents.get(cur)
            if not parents:
                break
            cur = parents[0]
            if cur in seen:  # defensive; acyclicity is an enforced invariant
                break
            seen.add(cur)
            path.append(cur)
        path.reverse()
        return path

    def root_of(self, node_id: str) -> str:
        return self.ancestry(node_id)[0]

    # -- traversal ------------------------------------------------------------

    def iter_nodes(self) -> Iterator["tuple[str, tuple, tuple]"]:
        """Pre-order DFS yielding ``(node_id, norm_path, raw_path)``.

        ``raw_path`` is the tuple of node names from a root down to the node;
        ``norm_path`` is the per-segment :func:`str_normalize` of it. Order mirrors
        :func:`paperext.analysis.rollup._iter_nodes` over the legacy tree, so the
        converter can reproduce that map exactly (its dedup is order-sensitive).
        """

        def walk(nid: str, norm_prefix: tuple, raw_prefix: tuple):
            node = self.nodes[nid]
            norm_path = norm_prefix + (str_normalize(node.name),)
            raw_path = raw_prefix + (node.name,)
            yield nid, norm_path, raw_path
            for cid in node.children:
                yield from walk(cid, norm_path, raw_path)

        for rid in self.roots:
            yield from walk(rid, (), ())

    # -- lookup / search ------------------------------------------------------

    def resolve(self, surface: str) -> "str | None":
        """Normalize *surface* and return its canonical node id, or ``None``."""
        return self._surface_to_canonical.get(str_normalize(surface))

    def search(self, query: str) -> "list[str]":
        """Global multi-hit substring search over node names and surfaces.

        Returns **all** node ids whose normalized name or any normalized surface
        contains the normalized *query* — e.g. ``"bit"`` returns every node under
        which a ``bit`` surface/name sits, not just the first. Ids are returned in
        deterministic DFS order.
        """
        q = str_normalize(query)
        if not q:
            return []
        hits: "list[str]" = []
        for node_id, norm_path, _ in self.iter_nodes():
            if q in norm_path[-1] or any(
                q in s for s in self._node_surfaces.get(node_id, [])
            ):
                hits.append(node_id)
        return hits

    # -- persistence ----------------------------------------------------------

    def save(self, version_dir: Union[str, Path]) -> None:
        """Write ``ontology.json`` + ``normalization.jsonl`` into *version_dir*.

        Byte-compatible with :func:`paperext.ontology.migrate.write_snapshot`, so
        a mutated tree round-trips through ``save`` -> :meth:`load`.
        """
        version_dir = Path(version_dir)
        version_dir.mkdir(parents=True, exist_ok=True)
        (version_dir / ONTOLOGY_FILE).write_text(
            json.dumps(self.doc.model_dump(), indent=2, ensure_ascii=False) + "\n"
        )
        lines = [
            json.dumps(row.model_dump(exclude_none=True), ensure_ascii=False)
            for row in self.norm
        ]
        (version_dir / NORMALIZATION_FILE).write_text("\n".join(lines) + "\n")

    # -- mutation helpers -----------------------------------------------------

    def _require(self, *node_ids: str) -> None:
        for nid in node_ids:
            if nid not in self.nodes:
                raise UnknownNodeError(nid)

    def _descendants(self, node_id: str) -> "set[str]":
        """All node ids strictly below *node_id* (DAG-safe)."""
        seen: "set[str]" = set()
        stack = list(self.nodes[node_id].children)
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(self.nodes[cur].children)
        return seen

    def _detach(self, node_id: str) -> None:
        """Unlink *node_id* from every parent's children list and from roots.

        Edits ``doc`` in place; the caller re-indexes.
        """
        for parent in self._parents.get(node_id, []):
            kids = self.nodes[parent].children
            self.nodes[parent].children = [c for c in kids if c != node_id]
        if node_id in self.doc.roots:
            self.doc.roots = [r for r in self.doc.roots if r != node_id]

    # -- mutation API (D1a-2, #42) --------------------------------------------

    def create_node(
        self,
        node_id: str,
        name: str,
        *,
        parent: "str | None" = None,
        description: str = "",
        examples: "list[str] | None" = None,
    ) -> None:
        """Add a new node under *parent* (or as a new root when ``parent`` is None)."""
        if not node_id.strip():
            raise InvariantError("node id must be non-empty")
        if node_id in self.nodes:
            raise DuplicateNodeError(node_id)
        if not name.strip():
            raise InvariantError("node name must be non-empty")
        if parent is not None:
            self._require(parent)
        self.doc.nodes[node_id] = Node(
            name=name, description=description, examples=list(examples or [])
        )
        if parent is None:
            self.doc.roots.append(node_id)
        else:
            self.nodes[parent].children.append(node_id)
        self._reindex()

    def rename(self, node_id: str, new_name: str) -> None:
        """Change a node's display *name* (does not touch its surfaces)."""
        self._require(node_id)
        if not new_name.strip():
            raise InvariantError("node name must be non-empty")
        self.nodes[node_id].name = new_name
        self._reindex()

    def update_description(self, node_id: str, description: str) -> None:
        """Set a node's description (bootstrapped during D1b)."""
        self._require(node_id)
        self.nodes[node_id].description = description
        self._reindex()

    def add_surface(
        self,
        surface: str,
        canonical: str,
        *,
        via: str = "curated",
        flag: "str | None" = None,
    ) -> None:
        """Map *surface* to node *canonical* (normalized, strictly 1:1)."""
        self._require(canonical)
        norm = str_normalize(surface)
        if not norm:
            raise InvariantError("surface normalizes to empty")
        owner = self._surface_to_canonical.get(norm)
        if owner == canonical:
            return  # idempotent
        if owner is not None:
            raise InvariantError(f"surface {norm!r} already maps to {owner!r} (1:1)")
        self.norm.append(NormRow(surface=norm, canonical=canonical, via=via, flag=flag))
        self._reindex()

    def remove_surface(self, surface: str) -> None:
        """Drop the *surface* -> canonical row."""
        norm = str_normalize(surface)
        kept = [r for r in self.norm if r.surface != norm]
        if len(kept) == len(self.norm):
            raise InvariantError(f"no surface {norm!r} to remove")
        self.norm = kept
        self._reindex()

    def move(self, node_id: str, new_parent: str) -> None:
        """Re-parent *node_id* under *new_parent* (single-primary).

        A no-op when *new_parent* is already *node_id*'s sole parent, so a
        redundant move never silently reorders it among its siblings.
        """
        self._require(node_id, new_parent)
        if new_parent == node_id or new_parent in self._descendants(node_id):
            raise CycleError(f"moving {node_id!r} under {new_parent!r} makes a cycle")
        if self._parents.get(node_id) == [new_parent] and node_id not in self.doc.roots:
            return
        self._detach(node_id)
        self.nodes[new_parent].children.append(node_id)
        self._reindex()

    def insert_above(
        self,
        node_id: str,
        new_id: str,
        name: str,
        *,
        description: str = "",
        examples: "list[str] | None" = None,
    ) -> None:
        """Insert a new parent *new_id* between *node_id* and its current parent.

        The new node takes *node_id*'s position among its parent's children (or in
        ``roots``), preserving DFS order; *node_id* becomes its only child.
        """
        if new_id in self.nodes:
            raise DuplicateNodeError(new_id)
        self._require(node_id)
        if not name.strip():
            raise InvariantError("node name must be non-empty")
        parents = list(self._parents.get(node_id, []))
        self.doc.nodes[new_id] = Node(
            name=name,
            description=description,
            examples=list(examples or []),
            children=[node_id],
        )
        for parent in parents:
            kids = self.nodes[parent].children
            kids[kids.index(node_id)] = new_id
        if node_id in self.doc.roots:
            self.doc.roots[self.doc.roots.index(node_id)] = new_id
        self._reindex()

    def demote_to_variant(self, node_id: str, target_id: str) -> None:
        """Fold leaf *node_id* into *target_id* as normalization surface(s).

        This is the concept-vs-variant resolution deferred from D1a-1: a node that
        turns out to be a mere spelling of another concept is removed, and its
        surfaces (plus its own name, unless that name is an ambiguous surface owned
        by a third node) re-point to *target_id*. Rejects a node that still has
        children — reattach them first.
        """
        self._require(node_id, target_id)
        if node_id == target_id:
            raise InvariantError("cannot demote a node into itself")
        if self.nodes[node_id].children:
            raise InvariantError(
                f"{node_id!r} has children; reattach them before demoting"
            )
        transfer = set(self._node_surfaces.get(node_id, []))
        name_surf = str_normalize(self.name(node_id))
        if name_surf and self._surface_to_canonical.get(name_surf) in (None, node_id):
            transfer.add(name_surf)
        kept = [r for r in self.norm if r.canonical != node_id]
        owned_elsewhere = {r.surface for r in kept}
        for surf in sorted(transfer):
            if surf in owned_elsewhere:  # never hijack another node's surface
                continue
            kept.append(NormRow(surface=surf, canonical=target_id, via="demote"))
        self.norm = kept
        self._detach(node_id)
        del self.doc.nodes[node_id]
        self._reindex()

    def remove_node(self, node_id: str) -> None:
        """Delete a childless *node_id* and cascade-drop its surface rows."""
        self._require(node_id)
        if self.nodes[node_id].children:
            raise InvariantError(f"{node_id!r} has children; remove or move them first")
        self.norm = [r for r in self.norm if r.canonical != node_id]
        self._detach(node_id)
        del self.doc.nodes[node_id]
        self._reindex()

    def mark_ignore(self, node_id: str) -> None:
        """Move *node_id* under the reserved ``ignore`` root (drops from roll-up).

        Creates the ignore root if the dimension has none.
        """
        self._require(node_id)
        drop = set(DEFAULT_DROP_ROOTS)
        ignore_id = next(
            (r for r in self.doc.roots if str_normalize(self.name(r)) in drop), None
        )
        if ignore_id is None:
            ignore_name = next(iter(DEFAULT_DROP_ROOTS))
            base = str_normalize(ignore_name) or "ignore"
            ignore_id, n = base, 2
            while ignore_id in self.nodes:  # id may be taken by an unrelated node
                ignore_id, n = f"{base}__{n}", n + 1
            self.create_node(ignore_id, ignore_name)
        if node_id == ignore_id:
            raise InvariantError("cannot ignore the ignore root itself")
        self.move(node_id, ignore_id)

    # -- invariants -----------------------------------------------------------

    def check_invariants(self) -> None:
        """Raise if any structural invariant is violated; return None if clean.

        Enforces: roots exist; every child edge and every normalization canonical
        references a live node (referential integrity); surfaces are 1:1; the
        children graph is acyclic; and every node is reachable from some root
        (no orphans).
        """
        nodes = self.doc.nodes
        for rid in self.doc.roots:
            if rid not in nodes:
                raise InvariantError(f"root {rid!r} is not a node")
        for nid, node in nodes.items():
            for cid in node.children:
                if cid not in nodes:
                    raise InvariantError(f"node {nid!r} has unknown child {cid!r}")
        seen_surface: "dict[str, str]" = {}
        for row in self.norm:
            if row.canonical not in nodes:
                raise InvariantError(
                    f"surface {row.surface!r} -> unknown node {row.canonical!r}"
                )
            prior = seen_surface.get(row.surface)
            if prior is not None and prior != row.canonical:
                raise InvariantError(f"surface {row.surface!r} maps to two nodes")
            seen_surface[row.surface] = row.canonical

        WHITE, GRAY, BLACK = 0, 1, 2
        color = {nid: WHITE for nid in nodes}

        def visit(start: str) -> None:
            stack = [(start, iter(nodes[start].children))]
            color[start] = GRAY
            while stack:
                nid, kids = stack[-1]
                advanced = False
                for cid in kids:
                    if color[cid] == GRAY:
                        raise CycleError(f"cycle through {cid!r}")
                    if color[cid] == WHITE:
                        color[cid] = GRAY
                        stack.append((cid, iter(nodes[cid].children)))
                        advanced = True
                        break
                if not advanced:
                    color[nid] = BLACK
                    stack.pop()

        for rid in self.doc.roots:
            if color[rid] == WHITE:
                visit(rid)
        orphans = [nid for nid, c in color.items() if c != BLACK]
        if orphans:
            raise InvariantError(f"orphan nodes unreachable from roots: {orphans[:5]}")

        # a root must not also be someone's child, else its subtree double-counts
        # in the DFS roll-up. Checked after cycle detection so a genuine cycle
        # (which also makes a root a child) still reports as a CycleError.
        child_ids = {cid for node in nodes.values() for cid in node.children}
        for rid in self.doc.roots:
            if rid in child_ids:
                raise InvariantError(
                    f"root {rid!r} is also a child (its subtree double-counts)"
                )
