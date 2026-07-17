"""Category roll-up / canonicalization engine (WS-E E1a, #23).

A pure, data-free primitive that turns a hierarchical category tree (the
``data/categorized_*.json`` files) into a flat ``{normalized_name: category}``
map, rolling every node up to a chosen cut level.

Two ways to specify the cut (mirroring the two mechanisms in the codebase):

- ``cut = <int>`` — a uniform *depth* (1 = top level). Every node rolls up to its
  ancestor at that depth, or to itself if it is shallower.
- ``cut = <iterable of dot-paths>`` — *per-branch* cut nodes, e.g. loaded from a
  milabench-style file like ``data/mdl/evaluation/model_categories/milabenchv1``.
  Every node rolls up to its **nearest** ancestor (or itself) whose dot-path is in
  the set. A single dot-path may be passed as a bare ``str`` (treated as one entry).
  Cut dot-paths are matched from the **root**, exactly as in the milabench file.

Semantics (locked in #16):

- **Aggregate, never drop.** A node with no cut match up to the root rolls up to
  ``Other`` — it is not discarded.
- The **only** thing dropped is the explicit ``ignore`` branch (genuine
  misextractions); nodes under a ``drop_roots`` top level are omitted entirely.
- Every node name in the tree (canonical *and* nested aliases, at any depth) is a
  key in the returned map, so a later lookup by any extracted name or alias
  resolves to the same category.

Names containing ``.``: ``str_normalize`` strips ``.`` (among other separators), so
a tree name like ``"gpt-3.5"`` collapses to the single segment ``"gpt35"``. Such a
node is still a valid key and rolls up correctly under a depth cut or a cut at any
ancestor whose own name has no ``.``. It **cannot** be targeted directly by a dotted
cut entry (the ``.`` would be read as a path separator) — ``roll_up`` logs a warning
for any cut entry that matches no node so this (and plain typos) never fails silently.

This module intentionally has no dependency on :mod:`paperext.config` or on
``paperext.structured_output.utils`` (whose import builds the category maps from
disk). ``str_normalize`` is duplicated below — kept byte-for-byte identical to
``paperext.structured_output.utils.str_normalize`` — to keep the engine pure and
unit-testable with no config or data files.
"""

import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Iterable, Union

logger = logging.getLogger(__name__)

#: Bucket for nodes that match no cut point up to the root.
OTHER = "Other"

#: Top-level branches dropped entirely (genuine misextractions).
DEFAULT_DROP_ROOTS = ("ignore",)

#: A cut is either a uniform depth (int >= 1) or an iterable of dot-paths.
Cut = Union[int, Iterable[str]]


def str_normalize(string: str) -> str:
    """Normalize a single name segment.

    Identical to ``paperext.structured_output.utils.str_normalize``. Note it
    strips ``.`` (among other separators), so dot-paths must be normalized
    **per segment**, never as a whole string.
    """
    string = unicodedata.normalize("NFKC", string).lower()
    string = re.sub(pattern=r"[\s/_\.\(\),\[\]\{\}-]", string=string, repl="")
    return string


def _normalize_path(dotted: str) -> str:
    """Normalize a dot-path segment-by-segment (``.`` survives as separator)."""
    return ".".join(str_normalize(seg) for seg in dotted.split("."))


def load_tree(path: Union[str, Path]) -> dict:
    """Load a ``categorized_*.json`` tree."""
    return json.loads(Path(path).read_text())


def load_cut(path: Union[str, Path]) -> "set[str]":
    """Read a milabench-style cut file into a set of normalized dot-paths.

    Blank lines and ``#`` comments are ignored; each remaining line is a dot-path
    normalized per segment.
    """
    cut = set()
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cut.add(_normalize_path(line))
    return cut


def _iter_nodes(tree: dict, norm_prefix: tuple = (), raw_prefix: tuple = ()):
    """Depth-first walk yielding ``(norm_path, raw_path)`` for every node.

    ``norm_path`` is the tuple of normalized names from the top level down to and
    including the node; ``raw_path`` is the matching tuple of original names.
    """
    for raw_name, sub in tree.items():
        norm_path = norm_prefix + (str_normalize(raw_name),)
        raw_path = raw_prefix + (raw_name,)
        yield norm_path, raw_path
        if sub:
            yield from _iter_nodes(sub, norm_path, raw_path)


def _category_at_depth(norm_path: tuple, raw_path: tuple, depth: int) -> str:
    """Category for a node under a uniform *depth* cut (1-indexed)."""
    idx = min(depth, len(norm_path)) - 1
    return raw_path[idx]


def _category_at_nodes(norm_path: tuple, raw_path: tuple, cut: "set[str]") -> str:
    """Category for a node under a per-branch *node* cut.

    Rolls up to the nearest ancestor (or self) whose dot-path is a cut point;
    falls back to :data:`OTHER`.
    """
    for i in range(len(norm_path), 0, -1):
        if ".".join(norm_path[:i]) in cut:
            return raw_path[i - 1]
    return OTHER


def roll_up(
    tree: dict,
    cut: Cut,
    drop_roots: Iterable[str] = DEFAULT_DROP_ROOTS,
) -> "dict[str, str]":
    """Roll a category *tree* up to *cut*, returning ``{normalized_name: category}``.

    ``cut`` is either an ``int`` depth (1 = top level) or an iterable of dot-paths
    (cut nodes). See the module docstring for the full semantics.
    """
    if isinstance(cut, bool):  # bool is an int subclass; reject it explicitly
        raise TypeError("cut must be an int depth or an iterable of dot-paths")

    if isinstance(cut, str):
        # A bare string is iterable char-by-char; treat it as a single cut node
        # rather than silently rolling every node up to Other.
        cut = [cut]

    if isinstance(cut, int):
        if cut < 1:
            raise ValueError(f"depth cut must be >= 1, got {cut}")
        cutset = None
    else:
        cutset = {_normalize_path(entry) for entry in cut}

    drop = {str_normalize(root) for root in drop_roots}

    all_paths: "set[str]" = set()
    mapping: "dict[str, str]" = {}
    seen_reserved = False
    for norm_path, raw_path in _iter_nodes(tree):
        all_paths.add(".".join(norm_path))

        if raw_path[-1] == OTHER and not seen_reserved:
            # A real node named exactly like the fallback bucket would be
            # indistinguishable from it in the output.
            seen_reserved = True
            logger.warning(
                "tree contains a node named %r, the reserved fallback label; "
                "its counts will merge with unmatched nodes",
                OTHER,
            )

        if norm_path[0] in drop:
            continue

        key = norm_path[-1]
        if not key:  # empty name after normalization — nothing to key on
            continue

        if cutset is None:
            category = _category_at_depth(norm_path, raw_path, cut)
        else:
            category = _category_at_nodes(norm_path, raw_path, cutset)

        previous = mapping.get(key)
        if previous is not None and previous != category:
            logger.warning(
                "Name %r maps to multiple categories: %r vs %r; keeping %r",
                key,
                previous,
                category,
                previous if previous != OTHER else category,
            )
            # Deterministic: keep the first non-Other mapping.
            if previous != OTHER:
                continue

        mapping[key] = category

    if cutset is not None:
        # A cut entry that matches no node is a typo, or a name whose '.' was
        # read as a path separator (str_normalize strips '.', so a tree name
        # containing '.' collapses to a single segment and cannot be targeted by
        # a dotted cut entry). Surface it loudly instead of silently no-op'ing.
        for entry in sorted(cutset - all_paths):
            logger.warning("cut node %r matches no node in the tree", entry)

    return mapping


def build_category_map(
    tree_path: Union[str, Path],
    cut: Cut,
    drop_roots: Iterable[str] = DEFAULT_DROP_ROOTS,
) -> "dict[str, str]":
    """Convenience: :func:`load_tree` + :func:`roll_up`."""
    return roll_up(load_tree(tree_path), cut, drop_roots=drop_roots)
