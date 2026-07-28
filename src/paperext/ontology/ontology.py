"""The :class:`Ontology` read object — load, index, accessors, search (D1a, #36).

Parses a versioned snapshot once and builds the in-memory indexes the D1b payload
needs: surface -> canonical, node -> surfaces (reverse), and node -> parents. All
accessors are O(1)/O(depth) against those indexes.

On-disk is diffable and DAG-ready; in-memory is indexed. This object is read-only;
the mutation API that edits and re-indexes it lands in D1a-2.
"""

import json
from pathlib import Path
from typing import Iterator, Union

from paperext.analysis.rollup import str_normalize
from paperext.ontology.schema import Meta, Node, NormRow, OntologyDoc

ONTOLOGY_FILE = "ontology.json"
NORMALIZATION_FILE = "normalization.jsonl"


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
