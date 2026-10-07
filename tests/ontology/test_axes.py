"""The faceted-dimension loader and its resolution semantics (D1h, #100).

The load-bearing test here is :func:`test_resolution_matches_the_design_script`:
it asserts the engine resolves **every** backbone node on **every** axis exactly
as the authored design script does -- 5016 resolutions for algorithms, 1074 for
models. A port of inheritance semantics is either exact or it is a silent
rewrite of two ontologies, and only a node-by-node comparison can tell which.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from paperext.ontology.axes import Dimension, parse_term, split_top
from paperext.ontology.convert_axes import SPECS, convert, write_snapshot
from paperext.ontology.ontology import Ontology
from paperext.ontology.rollup import to_category_map, to_category_sets
from paperext.ontology.schema import (
    AxisSpec,
    DimensionDoc,
    Meta,
    Node,
    OntologyDoc,
)

DESIGN = Path("data/ontology/design")
SNAPSHOTS = Path("data/ontology")

#: Node counts the dimensions were signed off with (#91, #95, #96). A conversion
#: that quietly lost or invented a node would otherwise pass everything else.
EXPECTED = {
    "domains": {
        "discipline": 160,
        "method": 111,
        "modality": 81,
        "sector": 78,
        "properties": 35,
    },
    "models": {"lineage": 358, "connectivity": 24, "topology": 7, "attributes": 51},
    "algorithms": {"lineage": 1672, "signal": 56, "role": 46, "attributes": 97},
}


def _load_script(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- #
# conversion
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("dimension", sorted(SPECS))
def test_conversion_preserves_every_node(dimension):
    _, built = convert(dimension)
    assert {a: len(d.nodes) for a, (d, _) in built.items()} == EXPECTED[dimension]


@pytest.mark.parametrize("dimension", sorted(SPECS))
def test_committed_snapshot_matches_a_fresh_conversion(dimension):
    """The committed snapshot is regenerable, so the tables stay the source."""
    manifest, built = convert(dimension)
    live = Dimension.load(SNAPSHOTS / dimension / "v1")
    assert live.doc == manifest
    for axis, (doc, _) in built.items():
        assert live.axis(axis).doc == doc


@pytest.mark.parametrize("dimension", sorted(SPECS))
def test_snapshot_round_trips_through_disk(dimension, tmp_path):
    manifest, built = convert(dimension)
    write_snapshot(dimension, manifest, built, snapshot_root=tmp_path)
    reloaded = Dimension.load(tmp_path / dimension / "v1")
    assert reloaded.doc == manifest
    assert {a: len(o.nodes) for a, o in reloaded.axes.items()} == EXPECTED[dimension]


@pytest.mark.parametrize("dimension", sorted(SPECS))
def test_integrity_is_clean(dimension):
    assert Dimension.load(SNAPSHOTS / dimension / "v1").check_integrity() == []


def test_legacy_v0_still_loads_against_the_extended_schema():
    """Every field #100 adds is defaulted, so v0 must be untouched by them."""
    onto = Ontology.load("data/ontology/models/v0")
    assert len(onto.nodes) == 1409
    node = onto.node(onto.roots[0])
    assert node.axes == {} and node.parent_ids == [] and node.props == {}


def test_pairs_survive_conversion_as_single_items():
    """A ``(sources, forms)`` pair must not be split on the comma inside it."""
    dim = Dimension.load(SNAPSHOTS / "algorithms" / "v1")
    items = dim.pin_items("M.rlhf", "signal")
    assert items and all(i.startswith("(") for i in items)
    assert len(dim.terms("M.rlhf", "signal")) == len(items)


# --------------------------------------------------------------------------- #
# the equivalence gate
# --------------------------------------------------------------------------- #


def test_resolution_matches_the_design_script_algorithms():
    ref = _load_script("ref_algo", str(DESIGN / "axes_algorithms/resolve.py"))
    authored = ref.Dimension.load(DESIGN / "axes_algorithms")
    dim = Dimension.load(SNAPSHOTS / "algorithms" / "v1")

    checked = 0
    for nid in authored.lineage:
        for axis in ("signal", "role", "attributes"):
            want, want_notes = authored.effective(nid, axis)
            got, got_notes = dim.effective(nid, axis)
            assert got == want, f"{nid}.{axis}"
            assert sorted(got_notes) == sorted(want_notes), f"{nid}.{axis} notes"
            checked += 1
        assert sorted(dim.terms(nid, "signal")) == sorted(
            authored.signal_terms(nid)
        ), f"{nid} terms"
        assert sorted(dim.conflicting_parents(nid)) == sorted(
            authored.conflicting_parents(nid)
        ), f"{nid} conflicts"
    assert checked == 1672 * 3


def test_resolution_matches_the_design_script_models():
    ref = _load_script("ref_models", str(DESIGN / "axes_models/resolve.py"))
    lineage, _names, family = ref.load_axes()
    card = ref.family_cardinality()
    dim = Dimension.load(SNAPSHOTS / "models" / "v1")

    checked = 0
    for nid in lineage:
        for axis in ("connectivity", "topology", "attributes"):
            # Order matters here: the `nearest` mode returns the first value of
            # the nearest pinning cell, so a reordered chain is a different answer.
            assert dim.resolved_order(nid, axis) == ref.effective(
                lineage, family, nid, axis, card
            ), f"{nid}.{axis}"
            checked += 1
    assert checked == 358 * 3


# --------------------------------------------------------------------------- #
# each semantic in isolation
# --------------------------------------------------------------------------- #


def _toy(inherit="union", **over):
    """A three-node backbone over a two-family axis, for one semantic at a time.

    ``value`` axis::

        famA -> a1 -> a1x        famB (cardinality from `card`) -> b1, b2
    """
    card = over.pop("card", "one")
    value = OntologyDoc(
        meta=Meta(version="t", dimension="toy/value"),
        roots=["famA", "famB"],
        nodes={
            "famA": Node(name="famA", children=["a1"]),
            "a1": Node(name="a1", parent_ids=["famA"], children=["a1x"]),
            "a1x": Node(name="a1x", parent_ids=["a1"]),
            "famB": Node(
                name="famB", children=["b1", "b2"], props={"cardinality": card}
            ),
            "b1": Node(name="b1", parent_ids=["famB"]),
            "b2": Node(name="b2", parent_ids=["famB"]),
        },
    )
    pins = over.pop("pins")
    spine = OntologyDoc(
        meta=Meta(version="t", dimension="toy/spine"),
        roots=["root"],
        nodes={
            nid: Node(
                name=nid,
                parent_ids=parents,
                children=[c for c, (ps, _) in pins.items() if nid in ps],
                axes={"value": cell} if cell else {},
            )
            for nid, (parents, cell) in pins.items()
        },
    )
    doc = DimensionDoc(
        meta=Meta(version="t", dimension="toy"),
        backbone="spine",
        axes=[
            AxisSpec(name="spine", inherit="none"),
            AxisSpec(name="value", inherit=inherit, **over),
        ],
        chain_order=over.pop("chain_order", "breadth-first"),
    )
    return Dimension(
        doc=doc, axes={"spine": Ontology(spine, []), "value": Ontology(value, [])}
    )


def test_union_lets_a_child_refine_rather_than_replace():
    dim = _toy(
        inherit="union",
        subsume=False,
        pins={"root": ([], ["a1"]), "leaf": (["root"], ["a1x"])},
    )
    assert dim.effective("leaf", "value")[0] == {"a1", "a1x"}


def test_subsumption_drops_the_ancestor_the_specific_value_implies():
    dim = _toy(
        inherit="union",
        subsume=True,
        pins={"root": ([], ["a1"]), "leaf": (["root"], ["a1x"])},
    )
    assert dim.effective("leaf", "value")[0] == {"a1x"}


def test_nearest_takes_only_the_closest_pinning_ancestor():
    dim = _toy(
        inherit="nearest",
        pins={"root": ([], ["b1"]), "mid": (["root"], ["b2"]), "leaf": (["mid"], [])},
    )
    assert dim.effective("leaf", "value")[0] == {"b2"}


def test_deny_nearest_lets_a_child_reassert_what_an_ancestor_denied():
    """The L.causal.struct / M.lingam case: a denial governs what it inherits."""
    dim = _toy(
        inherit="union",
        deny="nearest",
        subsume=False,
        pins={
            "root": ([], ["b1"]),
            "mid": (["root"], ["!b1"]),
            "leaf": (["mid"], ["b1"]),
        },
    )
    assert dim.effective("leaf", "value")[0] == {"b1"}
    assert dim.effective("mid", "value")[0] == set()


def test_deny_chain_makes_a_denial_anywhere_final():
    dim = _toy(
        inherit="union",
        deny="chain",
        subsume=False,
        pins={
            "root": ([], ["b1"]),
            "mid": (["root"], ["!b1"]),
            "leaf": (["mid"], ["b1"]),
        },
    )
    assert dim.effective("leaf", "value")[0] == set()


def test_many_inherit_chain_keeps_an_inherited_sibling_value():
    """EGNN really is permutation- AND Euclidean-equivariant."""
    dim = _toy(
        inherit="nearest-in-family",
        card="many",
        many_inherit="chain",
        subsume=False,
        pins={"root": ([], ["b1"]), "leaf": (["root"], ["b2"])},
    )
    assert dim.effective("leaf", "value")[0] == {"b1", "b2"}


def test_many_inherit_nearest_keeps_only_the_closest_depth():
    dim = _toy(
        inherit="nearest-in-family",
        card="many",
        many_inherit="nearest",
        subsume=False,
        pins={"root": ([], ["b1"]), "leaf": (["root"], ["b2"])},
    )
    assert dim.effective("leaf", "value")[0] == {"b2"}


def test_a_single_valued_family_keeps_the_nearest_pin():
    dim = _toy(
        inherit="nearest-in-family",
        card="one",
        subsume=False,
        pins={"root": ([], ["b1"]), "leaf": (["root"], ["b2"])},
    )
    assert dim.effective("leaf", "value")[0] == {"b2"}


def test_equal_depth_in_a_single_valued_family_is_reported_not_settled():
    """Picking one by column order is the defect the whole design avoids."""
    dim = _toy(
        inherit="nearest-in-family",
        card="one",
        subsume=False,
        pins={"leaf": ([], ["b1", "b2"])},
    )
    values, notes = dim.effective("leaf", "value")
    assert values == {"b1", "b2"}
    assert notes and "equal depth" in notes[0]


def test_value_parent_picks_which_parent_values_flow_along():
    dim = _toy(
        inherit="union",
        subsume=False,
        pins={"pa": ([], ["b1"]), "pb": ([], ["b2"]), "leaf": (["pa", "pb"], [])},
    )
    assert dim.effective("leaf", "value")[0] == {"b1", "b2"}
    dim.backbone.node("leaf").value_parent = "pb"
    assert dim.effective("leaf", "value")[0] == {"b2"}


def test_conflicting_parents_reports_assert_against_deny():
    dim = _toy(
        inherit="union",
        deny="nearest",
        subsume=False,
        pins={"pa": ([], ["b1"]), "pb": ([], ["!b1"]), "leaf": (["pa", "pb"], [])},
    )
    assert any("asserts what" in w for w in dim.conflicting_parents("leaf"))


def test_agreeing_parents_need_no_declaration():
    """Explicitness is required where ambiguity exists, not everywhere."""
    dim = _toy(
        inherit="union",
        subsume=False,
        pins={"pa": ([], ["b1"]), "pb": ([], ["b1"]), "leaf": (["pa", "pb"], [])},
    )
    assert dim.conflicting_parents("leaf") == []


# --------------------------------------------------------------------------- #
# pairs and composites
# --------------------------------------------------------------------------- #


def test_split_top_respects_parentheses():
    assert split_top("(a, b); !c") == ["(a, b)", "!c"]


def test_parse_term_reads_both_multi_valued_sides():
    assert parse_term("(S.src.a + S.src.b, S.form.x)") == (
        frozenset({"S.src.a", "S.src.b"}),
        frozenset({"S.form.x"}),
    )
    assert parse_term("R.fit.obj") is None


def test_rlhf_resolves_to_three_terms_not_a_cross_product():
    """The pairs exist to kill a cross-product that licensed 62% false combos."""
    dim = Dimension.load(SNAPSHOTS / "algorithms" / "v1")
    terms = dim.terms("M.rlhf", "signal")
    assert len(terms) == 3
    values, _ = dim.effective("M.rlhf", "signal")
    sources = {v for v in values if v.startswith("S.src")}
    forms = {v for v in values if v.startswith("S.form")}
    # Flattened, it would license len(sources) * len(forms) combinations.
    assert len(sources) * len(forms) > len(terms)


def test_expansion_is_transitive_and_excludes_the_node_itself():
    dim = Dimension.load(SNAPSHOTS / "algorithms" / "v1")
    composites = [
        nid for nid in dim.backbone_nodes() if dim.backbone.node(nid).expands_to
    ]
    assert composites
    for nid in composites:
        assert nid not in dim.expand(nid)
        assert dim.expand(nid) >= set(dim.backbone.node(nid).expands_to)


# --------------------------------------------------------------------------- #
# set-valued roll-up
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("dimension", ["models", "domains"])
@pytest.mark.parametrize("cut", [1, 2, 3])
def test_set_roll_up_contains_the_flat_answer(dimension, cut):
    """The flat map is one choice among the set, never outside it."""
    onto = Ontology.load(f"data/ontology/{dimension}/v0")
    flat = to_category_map(onto, cut)
    sets = to_category_sets(onto, cut)
    assert set(flat) == set(sets)
    for key, category in flat.items():
        assert category in sets[key]


def test_set_roll_up_recovers_what_the_flat_map_had_to_collapse():
    """The legacy dedup keeps one category per name; a DAG has several."""
    onto = Ontology.load("data/ontology/models/v0")
    sets = to_category_sets(onto, 2)
    assert any(len(v) > 1 for v in sets.values())


def test_a_dropped_path_does_not_drop_a_node_reachable_another_way():
    doc = OntologyDoc(
        meta=Meta(version="t", dimension="toy"),
        roots=["ignore", "real"],
        nodes={
            "ignore": Node(name="ignore", children=["shared"]),
            "real": Node(name="real", children=["shared"]),
            "shared": Node(name="shared"),
        },
    )
    onto = Ontology(doc, [])
    assert to_category_sets(onto, 1) == {"real": {"real"}, "shared": {"real"}}


def test_a_node_reaching_no_cut_point_aggregates_to_other():
    doc = OntologyDoc(
        meta=Meta(version="t", dimension="toy"),
        roots=["top"],
        nodes={
            "top": Node(name="top", children=["mid"]),
            "mid": Node(name="mid", children=["leaf"]),
            "leaf": Node(name="leaf"),
        },
    )
    onto = Ontology(doc, [])
    # Cut dot-paths are matched from the root, exactly as in a milabench file.
    sets = to_category_sets(onto, ["top.mid"])
    assert sets["top"] == {"Other"}
    assert sets["mid"] == {"mid"}
    assert sets["leaf"] == {"mid"}


def test_schema_growth_does_not_move_the_content_hash():
    """The guard behind the sealed eval reference (#95).

    ``tests/categorize/test_sampling.py`` compares ``models/v0`` against a
    *committed* hash, so that test is the real seal; this one states the rule it
    depends on, which is easy to break from the other direction: a field added
    to ``Node`` must contribute to the hash only where a node uses it.
    """
    from paperext.categorize.apply import _OPTIONAL_NODE_FIELDS, content_hash

    onto = Ontology.load("data/ontology/models/v0")
    before = content_hash(onto)

    # Every optional field is at its default on a legacy tree, so clearing them
    # explicitly must be a no-op for the hash.
    for node in onto.doc.nodes.values():
        for field in _OPTIONAL_NODE_FIELDS:
            setattr(node, field, type(getattr(node, field))())
    assert content_hash(onto) == before

    # Using one of them is content, and must move it.
    next(iter(onto.doc.nodes.values())).kind = "bundle"
    assert content_hash(onto) != before


# --------------------------------------------------------------------------- #
# the `many`-family triage (#100, PINNING_FINDINGS.md §9)
# --------------------------------------------------------------------------- #

#: ``(node, value, should_resolve)``. A `many` family unions up the chain, so an
#: inherited value holds unless the node denies it. These are the cases that
#: changed when that was fixed, and each was decided individually -- a silent
#: regression here would put a wrong claim about a real algorithm back in.
TRIAGE = [
    # True values the old nearest-depth resolution dropped.
    ("M.exp3", "A.guar.regret", True),  # EXP3's headline theorem
    ("M.mirror-descent", "A.guar.conv", True),  # has both conv and regret
    ("M.mirror-descent", "A.guar.regret", True),
    ("L.mcmc.gibbs", "A.deriv.sample", True),  # closed-form conditionals, sampled
    ("L.mcmc.gibbs", "A.deriv.closed", True),
    ("M.blocked-gibbs", "A.deriv.closed", True),
    ("M.collapsed-gibbs", "A.deriv.closed", True),
    ("M.simulated-annealing", "A.deriv.sample", True),
    ("L.hpo.model", "A.deriv.closed", True),  # the GP posterior is closed-form
    # Ancestor pins that claimed more than they should.
    ("M.nash-q", "A.guar.regret", False),  # convergence, not regret
    ("M.nfsp", "A.guar.regret", False),
    ("M.fictitious-play", "A.guar.regret", False),
    ("M.cfr", "A.guar.regret", True),  # the narrow must not cost these three
    ("M.deep-cfr", "A.guar.regret", True),
    ("M.regret-matching", "A.guar.regret", True),
    ("M.viterbi", "A.deriv.closed", False),  # a DP recursion
    ("M.k-medoids-pam", "A.deriv.closed", False),  # a swap search, unlike k-means
    ("M.slice-sampling", "A.deriv.closed", False),  # its conditionals are not
    ("L.causal.hte", "A.uncert.ens", False),  # bagged, but not ensemble-uncertainty
    ("M.causal-forest", "A.uncert.ens", True),  # the one child for which it holds
]


@pytest.mark.parametrize("node_id,value,expected", TRIAGE)
def test_many_family_triage(node_id, value, expected):
    dim = Dimension.load(SNAPSHOTS / "algorithms" / "v1")
    assert (value in dim.effective(node_id, "attributes")[0]) is expected


def test_the_many_fix_only_added_values():
    """Chain-union is additive: nothing the old resolution found was lost.

    Which is what makes the triage safe to read as a gain -- the four narrowed
    and denied pins removed values that chain-union had newly introduced, not
    values the dimension previously relied on.
    """
    chain = Dimension.load(SNAPSHOTS / "algorithms" / "v1")
    nearest = Dimension.load(SNAPSHOTS / "algorithms" / "v1")
    for spec in nearest.doc.axes:
        if spec.name == "attributes":
            spec.many_inherit = "nearest"

    gained = lost = 0
    for nid in chain.backbone_nodes():
        new, _ = chain.effective(nid, "attributes")
        old, _ = nearest.effective(nid, "attributes")
        gained += len(new - old)
        lost += len(old - new)
    assert (gained, lost) == (10, 0)
