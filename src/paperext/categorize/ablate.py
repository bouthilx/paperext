"""Hide one already-mapped name from an ontology (WS-D D1b-1, #51).

Held-out eval items are names the tree **already** maps, so without hiding them
the task is a lookup, not a decision. :func:`ablate` produces the tree the agent
should see: the item's node gone, its surfaces gone, and any textual trace of it
scrubbed from the nodes that remain.

**Deep-copy then mutate — never a filtering view.** A view would have to intercept
``resolve`` / ``search`` / ``iter_nodes`` / ``node`` / ``children`` / ``parents`` /
``surfaces`` / ``examples`` / ``root_map`` / ``ancestry``, and would start leaking
the day someone adds an accessor or reaches through to ``onto.doc.nodes``. Copying
lets ``_reindex()`` do the work once, correctly.

Scope of the scrub, stated precisely because a silent leak invalidates every #53
number: node names and surfaces are removed outright; descriptions and examples
lose **token-delimited** occurrences of the name. Occurrences buried inside a
longer word are deliberately left alone — normalization strips separators, so
"``bit``" is a substring of "arbitrary", and redacting on bare containment would
gut the surrounding context the agent legitimately needs.
"""

from __future__ import annotations

import re
from typing import Iterable

from paperext.analysis.rollup import str_normalize
from paperext.ontology.ontology import Ontology
from paperext.ontology.schema import NormRow, OntologyDoc

REDACTED = "[redacted]"

#: Separators ``str_normalize`` strips; a name may be written with any of them.
_SEPARATORS = r"[\s/_\.\(\),\[\]\{\}-]*"


class AblationError(Exception):
    """The name cannot be hidden without damaging the rest of the tree."""


def copy_ontology(onto: Ontology) -> Ontology:
    """An independent deep copy of *onto* (re-indexed, shares no state)."""
    return Ontology(
        OntologyDoc.model_validate(onto.doc.model_dump()),
        [NormRow.model_validate(row.model_dump()) for row in onto.norm],
    )


def name_matches(onto: Ontology, surface: str) -> "list[str]":
    """Every node whose own name normalizes to *surface*.

    Usually one, but the legacy trees keep cross-branch homonyms as distinct nodes
    (``sam``, ``bit``, ``hubert``), and leaving one of them behind would hand the
    agent the answer under a different id.
    """
    want = str_normalize(surface)
    return [nid for nid, node in onto.nodes.items() if str_normalize(node.name) == want]


def ablatable(onto: Ontology, surface: str) -> bool:
    """Whether :func:`ablate` can hide *surface* without orphaning a subtree.

    False when the name resolves nowhere, or when any node carrying it has
    children — removing such a node would orphan real concepts, so those names are
    excluded from the eval pool rather than mangled.
    """
    targets = set(name_matches(onto, surface))
    resolved = onto.resolve(surface)
    if resolved is not None:
        targets.add(resolved)
    if not targets:
        return False
    return all(not onto.children(nid) for nid in targets)


def _redaction_pattern(surface: str) -> "re.Pattern[str]":
    """Match *surface* however it is spelled, but only as a whole token.

    ``ResNet-50`` also matches ``resnet 50`` and ``ResNet50``; it does not match
    the tail of ``PreResNet50``.
    """
    parts = [re.escape(part) for part in re.findall(r"[0-9]+|[^\W\d_]+", surface)]
    if not parts:
        return re.compile(r"(?!)")  # matches nothing
    return re.compile(
        r"(?<![0-9A-Za-z])" + _SEPARATORS.join(parts) + r"(?![0-9A-Za-z])",
        re.IGNORECASE,
    )


def _redaction_patterns(spellings: "Iterable[str]") -> "list[re.Pattern[str]]":
    """One pattern per distinct spelling, in a deterministic order."""
    return [_redaction_pattern(text) for text in sorted(set(spellings)) if text]


def ablate(onto: Ontology, surface: str) -> Ontology:
    """Return a copy of *onto* with *surface* hidden. *onto* is not touched.

    Removes every node whose name is *surface* (cascading their normalization
    rows), drops any remaining row for that surface, and scrubs token-delimited
    occurrences -- in every spelling the removed nodes carried -- from the
    surviving descriptions and examples.
    """
    if not ablatable(onto, surface):
        raise AblationError(
            f"{surface!r} does not resolve to removable leaf node(s) in this ontology"
        )

    scratch = copy_ontology(onto)

    targets = set(name_matches(scratch, surface))
    resolved = scratch.resolve(surface)
    if resolved is not None:
        targets.add(resolved)
    # The scrub matches every *spelling* the removed nodes were written in, not
    # only the query. A caller holding a normalized surface ("vitb16") would
    # otherwise build a pattern that cannot see "ViT-B/16" in a description, since
    # normalization has already welded the separators away.
    spellings = {surface} | {scratch.name(nid) for nid in targets}
    for node_id in sorted(targets):
        spellings.update(scratch.surfaces(node_id))
        scratch.remove_node(node_id)  # cascade-drops that node's surface rows

    if scratch.resolve(surface) is not None:  # a row not owned by a removed node
        scratch.remove_surface(surface)

    for pattern in _redaction_patterns(spellings):
        for node in scratch.nodes.values():
            if node.description and pattern.search(node.description):
                node.description = pattern.sub(REDACTED, node.description)
            node.examples = [e for e in node.examples if not pattern.search(e)]

    scratch.check_invariants()
    return scratch


def residual_names(onto: Ontology, *spellings: str) -> "list[str]":
    """Surviving node names that still contain any of *spellings* as a whole token.

    Pass the raw display name as well as the normalized surface: a pattern built
    from ``vitb16`` cannot see ``ViT-B/16``, so the two find different residue.

    :func:`ablate` removes the nodes whose name **is** the surface, but ``v0``
    deliberately keeps duplicate and near-duplicate nodes for D1b to resolve, so a
    held-out name can survive inside a *different* node's name. Two shapes, and
    they are not the same thing:

    - a genuine duplicate of the same concept -- ``resnet-20`` left behind in
      ``residual networks (resnet-20)``, ``variational autoencoder`` in
      ``variational autoencoder (vae)``. The held-out answer is still on the page.
    - a legitimately different entity that happens to contain the string --
      ``gan`` inside ``dp-gan``, ``mpnn++`` beside its parent ``mpnn``. That is the
      neighbourhood the eval *intends* the agent to reason from.

    Telling those apart is the identity judgment the agent is being asked to make,
    so it cannot be decided here, and scrubbing the names would destroy the second
    case to fix the first. This reports them instead: on the sealed splits, 22 of
    200 ``dev`` and 24 of 300 ``gate`` items leave some residue. #53 should report
    its headline both with and without them rather than assume either answer.
    """
    patterns = _redaction_patterns(spellings)
    return sorted(
        node.name
        for node in onto.nodes.values()
        if any(p.search(node.name) for p in patterns)
    )
