"""The payload: determinism, bounds, and the leak that must not happen (#52)."""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from paperext.analysis.rollup import str_normalize
from paperext.categorize.ablate import _redaction_pattern, ablate, residual_names
from paperext.categorize.actions import OPS
from paperext.categorize.items import Item, Mention, build_items
from paperext.categorize.prompt import (
    OP_GUIDANCE,
    build_context,
    build_messages,
    build_payload,
    payload_hash,
    render_context,
    render_payload,
)
from paperext.ontology import Ontology

ROOT = Path(__file__).parents[2]
V0 = ROOT / "data" / "ontology" / "models" / "v0"
BIT_PAPER = (
    ROOT / "data" / "mdl" / "queries" / "openai" / "legacy-2024" / "2306.03522_00.json"
)


@pytest.fixture(scope="module")
def v0() -> Ontology:
    return Ontology.load(V0)


@pytest.fixture(scope="module")
def bit() -> Item:
    items = build_items("models", files=[BIT_PAPER])
    return next(i for i in items if i.surface == "bits101")


@pytest.fixture
def tiny_item() -> Item:
    return Item(
        dimension="test",
        surface="resnet50v2",
        name="ResNet-50 v2",
        aliases=["ResNet"],
        spellings=["ResNet-50 v2", "resnet50v2"],
        n_mentions=2,
        n_papers=2,
        mentions=[
            Mention(
                paper="1234.5678",
                spelling="ResNet-50 v2",
                quote="We fine-tune a ResNet-50 v2 backbone.",
                justification="named in the experiments section",
                research_field="Computer Vision",
                is_executed=True,
                co_occurring=["ViT", "PPO", "Nonesuch-9000"],
            )
        ],
    )


# -- shape ------------------------------------------------------------------- #


def test_the_shared_half_carries_policy_roots_taxonomy_and_schema(tiny, tiny_cut):
    text = render_context(build_context(tiny, "test"))
    for section in ("## ROOT MAP", "## TAXONOMY", "## ACTION SCHEMA"):
        assert section in text
    assert "AMBIGUITY MEANS ABSTAIN" in text
    assert "`nn` neural networks" in text


def test_the_drop_root_is_marked_as_such(tiny):
    text = render_context(build_context(tiny, "test"))
    line = next(l for l in text.splitlines() if l.startswith("- `ignore`"))
    assert "misextractions" in line


def test_every_op_of_the_vocabulary_is_documented():
    """Adding an op without telling the agent what it is for must fail loudly."""
    assert set(OP_GUIDANCE) == set(OPS)


def test_the_action_schema_lists_every_op_and_flags_the_destructive_ones(tiny):
    text = render_context(build_context(tiny, "test"))
    for op, spec in OPS.items():
        assert f"`{op}(" in text
        if spec.dangerous:
            line = next(l for l in text.splitlines() if l.startswith(f"- `{op}("))
            assert "[destructive]" in line


def test_the_item_half_carries_grounding_and_candidates(tiny, tiny_cut, tiny_item):
    payload = build_payload(tiny, tiny_item, cut=tiny_cut)
    text = render_payload(payload)
    assert "## ITEM" in text and "## EVIDENCE" in text and "## CANDIDATES" in text
    assert "We fine-tune a ResNet-50 v2 backbone." in text
    assert "executed=yes" in text
    assert "`resnet`" in text  # reverse containment found the anchor


def test_co_occurrence_is_annotated_from_the_injected_tree(tiny, tiny_cut, tiny_item):
    payload = build_payload(tiny, tiny_item, cut=tiny_cut)
    annotated = {c.name: c for c in payload.evidence[0].alongside}
    assert annotated["ViT"].node_id == "vit"
    assert annotated["ViT"].cut_category == "transformer"
    assert annotated["PPO"].cut_category == "Other"  # mapped, but off the cut
    assert annotated["Nonesuch-9000"].node_id is None


def test_a_thin_neighbourhood_says_so_rather_than_looking_empty(tiny, tiny_cut):
    item = Item(dimension="test", surface="zzzznothing", name="Zzzznothing")
    text = render_payload(build_payload(tiny, item, cut=tiny_cut))
    assert "nothing in the tree resembles this name" in text


def test_truncation_is_reported(v0, bit):
    payload = build_payload(v0, bit, limit=3)
    assert len(payload.candidates) == 3
    assert payload.n_candidates_found > 3
    assert "of " in render_payload(payload)


# -- determinism ------------------------------------------------------------- #


def test_rendering_is_stable_across_calls(v0, bit):
    ctx = build_context(v0, "models")
    a = build_messages(ctx, build_payload(v0, bit))
    b = build_messages(ctx, build_payload(v0, bit))
    assert a == b
    assert payload_hash(ctx, build_payload(v0, bit)) == payload_hash(
        ctx, build_payload(v0, bit)
    )


@pytest.mark.parametrize("seed", ["0", "1", "12345"])
def test_the_hash_is_stable_across_processes_and_hash_seeds(seed):
    """Self-consistency over k runs is uninterpretable unless the input is
    provably byte-identical, including across interpreter hash randomization."""
    script = (
        "from paperext.ontology import Ontology;"
        "from paperext.categorize.items import build_items;"
        "from paperext.categorize.prompt import build_context, build_payload, payload_hash;"
        f"o=Ontology.load({str(V0)!r});"
        f"i=[x for x in build_items('models', files=[{str(BIT_PAPER)!r}]) if x.surface=='bits101'][0];"
        "print(payload_hash(build_context(o,'models'), build_payload(o,i)))"
    )
    env = {
        **os.environ,
        "PYTHONHASHSEED": seed,
        "PAPEREXT_CFG": str(ROOT / "config.mdl.ini"),
    }
    out = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env=env,
        cwd=ROOT,
    )
    assert out.returncode == 0, out.stderr
    test_the_hash_is_stable_across_processes_and_hash_seeds.seen = getattr(
        test_the_hash_is_stable_across_processes_and_hash_seeds, "seen", set()
    )
    test_the_hash_is_stable_across_processes_and_hash_seeds.seen.add(out.stdout.strip())
    assert len(test_the_hash_is_stable_across_processes_and_hash_seeds.seen) == 1


def test_the_hash_moves_when_the_rendering_moves(v0, bit):
    """It hashes the rendered text, not the objects: a renderer change that leaves
    the payload identical still changes the answer, so it must change the hash."""
    ctx = build_context(v0, "models")
    payload = build_payload(v0, bit)
    before = payload_hash(ctx, payload)
    assert payload_hash(ctx, payload.model_copy(update={"name": "BiT-S-50"})) != before


# -- the leak ---------------------------------------------------------------- #


def _sections(text: str) -> "dict[str, str]":
    parts = re.split(r"^## ", text, flags=re.M)
    return {p.split("\n", 1)[0].strip(): p for p in parts if p.strip()}


def _item_for(onto: Ontology, node_id: str, neighbours: "list[str]") -> Item:
    """A corpus-shaped item for an existing node, listed beside *neighbours*.

    The co-occurrence list deliberately includes another spelling of the item
    itself -- the exact shape that hands a held-out item its own answer back.
    """
    name = onto.name(node_id)
    return Item(
        dimension="models",
        surface=str_normalize(name),
        name=name,
        aliases=[],
        spellings=[name],
        n_mentions=1,
        n_papers=1,
        mentions=[
            Mention(
                paper="0000.00000",
                spelling=name,
                quote=f"We evaluate {name} on ImageNet.",
                research_field="Computer Vision",
                is_executed=True,
                co_occurring=[*neighbours, name.upper()],
            )
        ],
    )


@pytest.fixture(scope="module")
def dev_items(v0):
    from paperext.categorize.sampling import Splits

    path = ROOT / "data" / "ontology" / "eval" / "models" / "splits.json"
    return Splits.model_validate_json(path.read_text()).dev


def test_an_ablated_name_appears_only_in_the_item_block(v0, dev_items):
    """The single most likely silent-invalidation bug in the feature.

    If any category shown came from a map cached off pristine ``v0``, a held-out
    item arrives as its own neighbour carrying its own answer, and every #53
    number is quietly meaningless. Checked over the whole dev split so it cannot
    pass by luck of one example.
    """
    for split_item in dev_items:
        item = _item_for(v0, split_item.node_id, ["ResNet-50", "BERT"])
        scratch = ablate(v0, item.surface)
        ctx = build_context(scratch, "models")
        payload = build_payload(scratch, item)

        # The same token-delimited, separator-flexible matcher the ablation scrub
        # uses -- so "ResNet-50" is caught as "resnet 50" and "ResNet50", while a
        # four-letter name like NEAT does not fire on "need a" in the policy prose.
        patterns = [_redaction_pattern(item.name), _redaction_pattern(item.surface)]
        # `v0` keeps duplicate concepts on purpose, so a held-out name can survive
        # inside another node's name. That residue is a property of the ablation
        # (measured and reported by `residual_names`), not of the payload; strip it
        # so this test fails only on what the payload itself derived.
        residue = residual_names(scratch, item.surface, item.name)
        sections = {
            **_sections(render_context(ctx)),
            **_sections(render_payload(payload)),
        }
        for name, body in sections.items():
            if name in ("ITEM", "EVIDENCE", "TASK"):
                continue
            for surviving in residue:
                body = body.replace(surviving, "")
            for pattern in patterns:
                assert not pattern.search(body), f"{item.name!r} leaked into {name}"


def test_an_ablated_item_is_not_offered_as_its_own_candidate(v0, dev_items):
    for split_item in dev_items[:50]:
        item = _item_for(v0, split_item.node_id, [])
        scratch = ablate(v0, item.surface)
        assert scratch.resolve(item.surface) is None
        payload = build_payload(scratch, item)
        assert all(c.id != split_item.node_id for c in payload.candidates)


def test_an_item_never_gets_its_own_answer_back_through_co_occurrence(v0, dev_items):
    """A paper that spells the same model two ways must not annotate one with the
    other's category."""
    split_item = dev_items[0]
    item = _item_for(v0, split_item.node_id, [])
    scratch = ablate(v0, item.surface)
    payload = build_payload(scratch, item)
    for co in payload.evidence[0].alongside:
        assert co.node_id != split_item.node_id


def test_categories_come_from_the_injected_tree_not_a_cached_map(v0, bit):
    """Same item, two trees: the annotation must follow the tree it was given."""
    intact = build_payload(v0, bit)
    ablated = build_payload(ablate(v0, "densenet121"), bit)

    def category(payload, name):
        return next(
            (
                c.cut_category
                for e in payload.evidence
                for c in e.alongside
                if c.name == name
            ),
            "MISSING",
        )

    assert category(intact, "DenseNet-121") == "convolutional neural network"
    assert category(ablated, "DenseNet-121") is None


# -- the golden payload ------------------------------------------------------ #


def test_bit_s_101_payload_against_v0(v0, bit, file_regression):
    ctx = build_context(v0, "models")
    payload = build_payload(v0, bit)
    rendered = "\n".join(
        f"===== {m['role']} =====\n{m['content']}" for m in build_messages(ctx, payload)
    )
    file_regression.check(rendered, extension=".txt")


def test_bit_s_101_payload_against_tiny(tiny, tiny_cut, bit, file_regression):
    payload = build_payload(
        tiny, bit.model_copy(update={"dimension": "test"}), cut=tiny_cut
    )
    ctx = build_context(tiny, "test")
    rendered = "\n".join(
        f"===== {m['role']} =====\n{m['content']}" for m in build_messages(ctx, payload)
    )
    file_regression.check(rendered, extension=".txt")
