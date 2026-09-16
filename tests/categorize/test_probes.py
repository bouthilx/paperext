"""Reference-free control sets (WS-D D1b-3, #53)."""

import json

import pytest

from paperext.categorize import probes
from paperext.categorize.actions import (
    AddSurface,
    CreateNode,
    Decision,
    Move,
    Outcome,
    RemoveNode,
    UpdateDescription,
)
from paperext.categorize.apply import ApplyResult, DecisionRecord
from paperext.categorize.items import Item, Mention
from paperext.categorize.placement import Placement


def record(decision, *, placement=None, ok=True):
    from paperext.categorize.actions import Provenance

    return DecisionRecord(
        decision=decision,
        result=ApplyResult(ok=ok, placement=placement),
        provenance=Provenance(
            run_id="r", seq=0, dimension="test", base_version="v0", base_content_hash=""
        ),
    )


def decision(*actions, outcome=Outcome.MAPPED, surface="x", **kwargs):
    return Decision(
        surface=surface,
        outcome=outcome,
        confidence=0.9,
        actions=list(actions),
        **kwargs,
    )


# --------------------------------------------------------------------------- #
# No-op control
# --------------------------------------------------------------------------- #


def test_noop_cases_are_deterministic_and_sorted():
    surfaces = [f"s{index}" for index in range(50)]
    first = probes.noop_cases(surfaces, n=10, seed=1)
    assert [case.surface for case in first] == sorted(case.surface for case in first)
    assert first == probes.noop_cases(surfaces, n=10, seed=1)
    assert first != probes.noop_cases(surfaces, n=10, seed=2)


def test_no_actions_is_a_noop():
    assert probes.is_noop(record(decision(outcome=Outcome.NO_OP)))


def test_writing_a_description_is_allowed():
    """v0 has no descriptions at all, so filling one in is not churn."""
    action = UpdateDescription(
        node_id="cnn", description="x", justification="j", confidence=0.9
    )
    assert probes.is_noop(record(decision(action)))


def test_a_move_is_churn_whatever_the_outcome_claims():
    action = Move(node_id="vit", new_parent="cnn", justification="j", confidence=0.9)
    assert not probes.is_noop(record(decision(action, outcome=Outcome.NO_OP)))


def test_destructive_ops_outside_the_candidate_set_are_reported():
    action = RemoveNode(node_id="elsewhere", justification="j", confidence=0.9)
    hits = probes.destructive_ops(record(decision(action)), allowed={"vit"})
    assert hits == ["remove_node(elsewhere)"]


def test_destructive_ops_inside_the_candidate_set_are_not():
    action = RemoveNode(node_id="vit", justification="j", confidence=0.9)
    assert probes.destructive_ops(record(decision(action)), allowed={"vit"}) == []


# --------------------------------------------------------------------------- #
# Policy conformance
# --------------------------------------------------------------------------- #


def corpus_item(name, surface, aliases):
    return Item(
        dimension="test", surface=surface, name=name, aliases=aliases, spellings=[name]
    )


def test_a_size_qualifier_becomes_a_child_case(tiny):
    items = [corpus_item("ResNet-50", "resnet50", ["ResNet"])]
    cases = probes.policy_cases(tiny, items)
    child = [case for case in cases if case.kind == "child"]
    assert [(case.surface, case.base, case.base_id) for case in child] == [
        ("resnet50", "resnet", "resnet")
    ]


def test_a_declared_expansion_becomes_a_surface_case(tiny):
    items = [
        corpus_item(
            "PPO (Proximal Policy Optimization)",
            "ppo",
            ["proximal policy optimization"],
        )
    ]
    cases = probes.policy_cases(tiny, items)
    surface = [case for case in cases if case.kind == "surface"]
    assert [(case.surface, case.base_id) for case in surface] == [
        ("proximalpolicyoptimization", "ppo")
    ]


def test_a_plural_is_a_surface_not_a_child(tiny):
    items = [corpus_item("ViT", "vit", ["ViTs"])]
    cases = probes.policy_cases(tiny, items)
    assert [(case.kind, case.surface) for case in cases] == [("surface", "vits")]


def test_a_non_qualifying_remainder_is_dropped(tiny):
    """RoBERTa/ROB and 'Transformer model' contain each other but qualify nothing."""
    items = [corpus_item("ResNet", "resnet", ["ResNet model", "ResNets extra"])]
    assert [c for c in probes.policy_cases(tiny, items) if c.kind == "child"] == []


def test_an_ambiguous_short_form_is_dropped(tiny):
    """`sam` names two nodes in the legacy trees; nothing about it is unarguable."""
    tiny.create_node("sam2", "SAM", parent="nn")
    items = [corpus_item("SAM-2", "sam2x", ["SAM"])]
    assert probes.policy_cases(tiny, items) == []


def test_policy_scoring_accepts_a_child_under_the_base(tiny):
    case = probes.ProbeCase(
        kind="child",
        surface="resnet101",
        expect="child",
        base="resnet",
        base_id="resnet",
    )
    good = decision(
        CreateNode(
            node_id="resnet101",
            name="ResNet-101",
            parent="resnet",
            justification="j",
            confidence=0.9,
        ),
        AddSurface(
            surface="resnet101",
            canonical="resnet101",
            justification="j",
            confidence=0.9,
        ),
        surface="resnet101",
    )
    assert probes.score_policy([case], [record(good)])["conformance"] == 1.0


def test_policy_scoring_rejects_a_child_under_the_wrong_parent(tiny):
    case = probes.ProbeCase(
        kind="child",
        surface="resnet101",
        expect="child",
        base="resnet",
        base_id="resnet",
    )
    bad = decision(
        CreateNode(
            node_id="resnet101",
            name="ResNet-101",
            parent="cnn",
            justification="j",
            confidence=0.9,
        ),
        AddSurface(
            surface="resnet101",
            canonical="resnet101",
            justification="j",
            confidence=0.9,
        ),
        surface="resnet101",
    )
    assert probes.score_policy([case], [record(bad)])["conformance"] == 0.0


def test_policy_scoring_rejects_a_new_node_where_a_surface_was_required():
    case = probes.ProbeCase(
        kind="surface", surface="vits", expect="surface", base="vit", base_id="vit"
    )
    invented = decision(
        CreateNode(
            node_id="vits",
            name="ViTs",
            parent="transformer",
            justification="j",
            confidence=0.9,
        ),
        AddSurface(surface="vits", canonical="vits", justification="j", confidence=0.9),
        surface="vits",
    )
    plain = decision(
        AddSurface(surface="vits", canonical="vit", justification="j", confidence=0.9),
        surface="vits",
    )
    scored = probes.score_policy([case, case], [record(invented), record(plain)])
    assert scored["per_kind"]["surface"]["rate"] == 0.5


def test_abstaining_conforms_to_nothing():
    case = probes.ProbeCase(
        kind="surface", surface="vits", expect="surface", base="vit", base_id="vit"
    )
    scored = probes.score_policy([case], [record(decision(outcome=Outcome.ABSTAINED))])
    assert scored["conformance"] == 0.0
    assert "abstained" in scored["misses"][0]


# --------------------------------------------------------------------------- #
# Ambiguity 2x2
# --------------------------------------------------------------------------- #


def test_stripping_grounding_leaves_only_the_name():
    item = Item(
        dimension="test",
        surface="sam",
        name="SAM",
        aliases=["Segment Anything"],
        spellings=["SAM"],
        mentions=[
            Mention(
                paper="p1",
                spelling="SAM",
                quote="we use SAM to segment",
                justification="stated",
                research_field="vision",
                co_occurring=["ViT"],
            )
        ],
    )
    stripped = probes.strip_grounding(item)
    assert stripped.aliases == []
    assert stripped.mentions[0].paper == "p1"
    assert stripped.mentions[0].quote == ""
    assert stripped.mentions[0].justification == ""
    assert stripped.mentions[0].co_occurring == []
    assert item.mentions[0].quote  # the original is untouched


def test_injecting_a_homonym_makes_two_nodes_share_a_name(tiny):
    scratch = probes.inject_homonym(
        tiny, "CLIP", ["rl", "transformer"], node_ids=["h1", "h2"]
    )
    assert scratch.name("h1") == scratch.name("h2") == "CLIP"
    assert "h1" not in tiny  # the original is untouched
    scratch.check_invariants()


def test_injecting_a_homonym_rejects_mismatched_arguments(tiny):
    with pytest.raises(ValueError):
        probes.inject_homonym(tiny, "CLIP", ["rl"], node_ids=["h1", "h2"])


def test_abstention_needs_a_reason_not_just_an_outcome():
    assert not probes.abstained(record(decision(outcome=Outcome.ABSTAINED)))
    assert probes.abstained(
        record(decision(outcome=Outcome.ABSTAINED, review_notes=["two candidates"]))
    )


def test_youden_j_is_zero_for_always_abstain():
    """The whole reason the grounded arm is mandatory."""
    always = [record(decision(outcome=Outcome.ABSTAINED, unresolved=["a", "b"]))] * 5
    scored = probes.score_ambiguity(always, always)
    assert scored["recall_abstain"] == 1.0
    assert scored["false_abstain"] == 1.0
    assert scored["youden_j"] == 0.0


def test_youden_j_is_one_for_a_discriminating_agent():
    abstains = [record(decision(outcome=Outcome.ABSTAINED, unresolved=["a", "b"]))] * 5
    resolves = [record(decision(outcome=Outcome.MAPPED))] * 5
    assert probes.score_ambiguity(abstains, resolves)["youden_j"] == 1.0


def test_branch_of_returns_the_depth_two_ancestor(tiny):
    assert probes.branch_of(tiny, "resnet50") == "cnn"
    assert probes.branch_of(tiny, "nn") is None


# --------------------------------------------------------------------------- #
# Memorization canary
# --------------------------------------------------------------------------- #


def test_canary_probes_ask_about_the_real_structure(tmp_path):
    path = tmp_path / "categorized.json"
    path.write_text(json.dumps({"a": {"x": {}, "y": {}}, "b": {}}))
    questions = probes.canary_probes(path, branches=1)
    assert questions[0].expected == ["a", "b"]
    assert questions[1].expected == ["x", "y"]
    assert "guess" in questions[0].question


def test_canary_scores_recall_after_normalization():
    probe = probes.CanaryProbe(question="q", expected=["neural networks", "algorithms"])
    assert probes.score_canary(probe, ["Neural-Networks"]) == 0.5
    assert probes.score_canary(probe, []) == 0.0


def test_canary_fires_on_the_best_answer_not_the_average():
    assert probes.canary_fired([0.0, 0.0, 0.9])
    assert not probes.canary_fired([0.1, 0.2])
    assert not probes.canary_fired([])
