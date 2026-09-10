"""Hiding a held-out name (#51).

A leak here does not fail loudly — it silently turns every #53 number into a
measurement of lookup rather than judgment. So these tests are about what is
*still visible* after ablation, not only about what is gone.
"""

import pytest

from paperext.categorize.ablate import (
    REDACTED,
    AblationError,
    ablatable,
    ablate,
    copy_ontology,
    residual_names,
)
from paperext.categorize.apply import content_hash


def test_the_name_is_gone_every_way_it_could_be_found(tiny):
    scratch = ablate(tiny, "ResNet-50")

    assert scratch.resolve("ResNet-50") is None
    assert scratch.resolve("resnet50") is None
    assert "resnet50" not in scratch
    assert not [n for n in scratch.nodes if scratch.name(n) == "ResNet-50"]
    assert not [r for r in scratch.norm if r.surface == "resnet50"]
    scratch.check_invariants()


def test_the_source_ontology_is_untouched(tiny):
    """Deep copy, never a filtering view."""
    before = content_hash(tiny)
    scratch = ablate(tiny, "ResNet-50")
    assert content_hash(tiny) == before
    assert tiny.resolve("ResNet-50") == "resnet50"

    scratch.rename("vit", "Vision Transformer")
    assert tiny.name("vit") == "ViT"


def test_ancestors_and_siblings_stay_visible(tiny):
    """They are legitimate context — the agent has to place the name somewhere."""
    scratch = ablate(tiny, "ResNet-50")
    assert scratch.resolve("resnet") == "resnet"
    assert scratch.resolve("cnn") == "cnn"
    assert scratch.children("resnet") == []


def test_homonyms_in_other_branches_go_too(tiny):
    """The legacy trees keep cross-branch homonyms as separate nodes.

    Leaving one behind would hand the agent the answer under a different id.
    """
    tiny.create_node("sam__2", "SAM", parent="vit")
    assert len([n for n in tiny.nodes if tiny.name(n) == "SAM"]) == 2

    scratch = ablate(tiny, "sam")
    assert not [n for n in scratch.nodes if scratch.name(n) == "SAM"]
    assert scratch.resolve("sam") is None


def test_token_delimited_mentions_are_scrubbed_from_text(tiny):
    """``v0`` has no descriptions, but D1b bootstraps them from ``v1`` on."""
    scratch = ablate(tiny, "ResNet-50")
    assert "ResNet-50" not in scratch.node("cnn").description
    assert REDACTED in scratch.node("cnn").description
    assert "VGG" in scratch.node("cnn").description  # the rest of the context stays
    assert scratch.examples("cnn") == ["1512.03385"]


@pytest.mark.parametrize(
    "written", ["ResNet-50", "resnet 50", "ResNet50", "resnet_50", "RESNET-50"]
)
def test_the_scrub_catches_every_spelling_of_the_name(tiny, written):
    tiny.update_description("vit", f"Unlike {written}, it has no convolutions.")
    scratch = ablate(tiny, "ResNet-50")
    assert written not in scratch.node("vit").description


def test_the_scrub_does_not_gut_longer_words(tiny):
    """Normalization strips separators, so bare containment would over-redact.

    ``bit`` is a substring of ``arbitrary``; redacting on containment would
    destroy the context the agent legitimately needs.
    """
    tiny.create_node("bit", "BiT", parent="cnn")
    tiny.add_surface("bit", "bit")
    tiny.update_description("vit", "Patches of arbitrary size; see also BiT.")

    scratch = ablate(tiny, "bit")
    assert "arbitrary" in scratch.node("vit").description
    assert "BiT." not in scratch.node("vit").description


def test_a_name_with_children_is_refused_not_mangled(tiny):
    """Ablating a non-leaf would orphan real concepts; such names leave the pool."""
    assert not ablatable(tiny, "ResNet")
    with pytest.raises(AblationError):
        ablate(tiny, "ResNet")


def test_an_unknown_name_is_refused(tiny):
    assert not ablatable(tiny, "never heard of it")
    with pytest.raises(AblationError):
        ablate(tiny, "never heard of it")


def test_copy_ontology_shares_no_state(tiny):
    copy = copy_ontology(tiny)
    assert content_hash(copy) == content_hash(tiny)
    copy.remove_node("vit")
    assert "vit" in tiny


def test_the_scrub_matches_every_spelling_the_removed_node_carried(tiny):
    """A caller holding the *normalized* surface must still get a full scrub.

    ``_redaction_pattern("resnet50")`` cannot see "ResNet-50" -- normalization has
    already welded the separators away -- so `ablate` builds its patterns from the
    removed nodes' own names too.
    """
    tiny.update_description("cnn", "Convolutional nets, e.g. ResNet-50 and VGG.")
    scratch = ablate(tiny, "resnet50")
    assert "ResNet-50" not in scratch.node("cnn").description
    assert "VGG" in scratch.node("cnn").description
    assert scratch.node("cnn").examples == ["1512.03385"]


def test_residual_names_reports_a_duplicate_the_ablation_cannot_remove(tiny):
    """``v0`` keeps duplicate concepts for D1b to resolve, so a held-out name can
    survive inside a *different* node's name. That is reported, not scrubbed:
    telling a duplicate from a genuinely different entity is the judgment the
    agent is being asked to make."""
    tiny.create_node("resnet50v2", "residual networks (ResNet-50)", parent="resnet")
    scratch = ablate(tiny, "resnet50")
    assert "resnet50" not in scratch.nodes
    assert residual_names(scratch, "resnet50", "ResNet-50") == [
        "residual networks (ResNet-50)"
    ]


def test_residual_names_is_empty_for_a_cleanly_hidden_name(tiny):
    assert residual_names(ablate(tiny, "vit"), "vit", "ViT") == []
