"""The sealed eval splits (#51).

The manifest is committed and #53's gate number is only meaningful if it names the
same 300 items every time, so determinism and the reseal guard are the point.
"""

import json

import pytest

from paperext.analysis.rollup import str_normalize
from paperext.categorize.sampling import (
    DEFAULT_SEED,
    Splits,
    anchoring,
    build_pool,
    draw_splits,
    stratum_of,
    write_splits,
)
from paperext.ontology import Ontology

SIZES = {"dev": 10, "gate": 15}


@pytest.fixture
def wide():
    """A tree big enough to stratify: 50 mapped leaves over both axes.

    ``tiny`` has four poolable names — fine for the pool rules, useless for
    checking that the allocation actually spreads across strata. This one has all
    three anchoring values and three cut classes by construction.
    """
    from paperext.ontology.schema import Meta, Node, NormRow, OntologyDoc

    nodes = {
        "nn": Node(name="neural networks", children=["cnn", "transformer"]),
        "cnn": Node(name="CNN", children=["resnet"]),
        "resnet": Node(name="resnet", children=[]),
        "transformer": Node(name="transformer", children=["gpt"]),
        "gpt": Node(name="gpt", children=[]),
        "misc": Node(name="miscellaneous", children=[]),
    }
    norm = [
        NormRow(surface="resnet", canonical="resnet"),
        NormRow(surface="gpt", canonical="gpt"),
    ]

    def leaf(parent: str, name: str) -> None:
        node_id = str_normalize(name)
        nodes[node_id] = Node(name=name)
        nodes[parent].children.append(node_id)
        norm.append(NormRow(surface=node_id, canonical=node_id))

    for i in range(15):
        leaf("resnet", f"resnet-{i}")  # anchoring 'parent', cut CNN
        leaf("gpt", f"gpt-{i}")  # anchoring 'parent', cut transformer
        leaf("misc", f"zzz-{chr(ord('a') + i)}")  # anchoring 'cold', cut Other
    for i in range(5):
        leaf("misc", f"resnet-clone-{i}")  # anchoring 'some', cut Other

    doc = OntologyDoc(
        meta=Meta(version="v0", dimension="test"), roots=["nn", "misc"], nodes=nodes
    )
    onto = Ontology(doc, norm)
    onto.check_invariants()
    return onto


def _draw(onto, cut, **kwargs):
    kwargs.setdefault("sizes", SIZES)
    return draw_splits(onto, "test", cut, **kwargs)


def test_pool_is_mapped_leaves_outside_the_ignore_branch(tiny, tiny_cut):
    pool = {item.node_id for item in build_pool(tiny, tiny_cut)}
    assert "resnet50" in pool and "ppo" in pool and "vit" in pool
    assert "resnet" not in pool  # has a child
    assert "junk" not in pool  # under the dropped root
    assert "algorithms" not in pool  # a root, and unmapped


def test_pool_items_carry_the_display_name_and_the_lookup_key(tiny, tiny_cut):
    """#52 shows the agent the display name; ablation keys off the surface."""
    item = next(i for i in build_pool(tiny, tiny_cut) if i.node_id == "resnet50")
    assert item.name == "ResNet-50"
    assert item.surface == "resnet50"
    assert item.cut_category == "CNN"


def test_anchoring_axis(tiny, tiny_cut):
    """``parent`` / ``some`` / ``cold`` is the retrieval-difficulty axis."""
    # 'resnet50' reverse-contains 'resnet', which is its own parent
    assert anchoring(tiny, "resnet50", "resnet50") == "parent"
    # 'ppo' has no containment relative anywhere in the tree
    assert anchoring(tiny, "ppo", "ppo") == "cold"

    tiny.create_node("cnnzoo", "CNN zoo", parent="transformer")
    tiny.add_surface("cnnzoo", "cnnzoo")
    # 'cnn' is contained in the query but is not on this node's lineage
    assert anchoring(tiny, "cnnzoo", "cnnzoo") == "some"


def test_the_item_itself_never_anchors_itself(tiny, tiny_cut):
    """The probe reports what survives ablation, not what is there now."""
    assert anchoring(tiny, "vit", "vit") == "cold"


def test_the_wide_fixture_exercises_both_axes(wide, tiny_cut):
    """Guards the tests below: a fixture with one stratum proves nothing."""
    pool = build_pool(wide, tiny_cut)
    assert {i.anchoring for i in pool} == {"parent", "some", "cold"}
    assert {i.cut_category for i in pool} == {"CNN", "transformer", "Other"}


def test_splits_are_disjoint_and_cover_the_pool(wide, tiny_cut):
    splits = _draw(wide, tiny_cut)
    ids = [i.node_id for i in splits.dev + splits.gate + splits.reserve]
    assert len(ids) == len(set(ids)) == splits.pool_size
    assert len(splits.dev) == SIZES["dev"]
    assert len(splits.gate) == SIZES["gate"]


def test_the_draw_is_reproducible(wide, tiny_cut):
    first = _draw(wide, tiny_cut)
    second = _draw(wide, tiny_cut)
    assert first.model_dump() == second.model_dump()
    assert first.gate_ids_sha256 == second.gate_ids_sha256


def test_a_different_seed_draws_a_different_gate_set(wide, tiny_cut):
    a = _draw(wide, tiny_cut, seed=DEFAULT_SEED)
    b = _draw(wide, tiny_cut, seed=DEFAULT_SEED + 1)
    assert a.gate_ids_sha256 != b.gate_ids_sha256


def test_strata_counts_add_up(wide, tiny_cut):
    splits = _draw(wide, tiny_cut)
    for key, counts in splits.strata.items():
        assert counts["pool"] == counts["dev"] + counts["gate"] + counts["reserve"]
    assert sum(c["pool"] for c in splits.strata.values()) == splits.pool_size

    for split in ("dev", "gate", "reserve"):
        drawn = getattr(splits, split)
        by_stratum = {}
        for item in drawn:
            by_stratum[stratum_of(item)] = by_stratum.get(stratum_of(item), 0) + 1
        for key, n in by_stratum.items():
            assert splits.strata[key][split] == n


def test_gate_hash_is_order_independent(wide, tiny_cut):
    splits = _draw(wide, tiny_cut)
    shuffled = Splits.model_validate(splits.model_dump())
    shuffled.gate = list(reversed(shuffled.gate))
    redrawn = _draw(wide, tiny_cut)
    assert redrawn.gate_ids_sha256 == splits.gate_ids_sha256


def test_write_refuses_to_silently_reseal_a_different_gate_set(
    wide, tiny_cut, tmp_path
):
    path = tmp_path / "splits.json"
    write_splits(_draw(wide, tiny_cut), path)
    write_splits(_draw(wide, tiny_cut), path)  # same draw: fine

    with pytest.raises(FileExistsError, match="sealed gate set"):
        write_splits(_draw(wide, tiny_cut, seed=DEFAULT_SEED + 1), path)


# --------------------------------------------------------------------------- #
# The committed manifest
# --------------------------------------------------------------------------- #

MANIFEST = "data/ontology/eval/models/splits.json"


@pytest.mark.parametrize("split,size", [("dev", 200), ("gate", 300)])
def test_committed_manifest_has_the_sizes_d1b3_sized_for(split, size):
    splits = Splits.model_validate_json(open(MANIFEST).read())
    assert len(getattr(splits, split)) == size


def test_committed_manifest_matches_the_committed_v0():
    """If ``v0`` ever changes, the sealed splits stop describing it."""
    splits = Splits.model_validate_json(open(MANIFEST).read())
    onto = Ontology.load(f"data/ontology/{splits.dimension}/{splits.base_version}")

    from paperext.categorize.apply import content_hash

    assert splits.base_content_hash == content_hash(onto)
    for item in splits.gate:
        assert onto.resolve(item.surface) == item.node_id


def test_committed_manifest_is_what_the_sampler_draws():
    """Regenerating the manifest must reproduce it, or it was not sealed."""
    from paperext.categorize.placement import load_dimension_cut

    splits = Splits.model_validate_json(open(MANIFEST).read())
    onto = Ontology.load(f"data/ontology/{splits.dimension}/{splits.base_version}")
    redrawn = draw_splits(
        onto,
        splits.dimension,
        load_dimension_cut(splits.dimension),
        base_version=splits.base_version,
        seed=splits.seed,
        sizes={"dev": len(splits.dev), "gate": len(splits.gate)},
    )
    assert redrawn.gate_ids_sha256 == splits.gate_ids_sha256
    assert redrawn.model_dump() == json.loads(open(MANIFEST).read())
