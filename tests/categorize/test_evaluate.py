"""The eval harness end to end, with no network at all (WS-D D1b-3, #53)."""

import asyncio
import json
import math

import pytest

from paperext.categorize import adjudicate, evaluate, metrics
from paperext.categorize.actions import (
    AddSurface,
    CreateNode,
    Decision,
    MarkIgnore,
    Outcome,
    Provenance,
)
from paperext.categorize.apply import ApplyResult, DecisionRecord
from paperext.categorize.items import Item, Mention
from paperext.categorize.sampling import SplitItem, Splits


@pytest.fixture
def split_items():
    return [
        SplitItem(
            node_id="resnet50",
            surface="resnet50",
            name="ResNet-50",
            anchoring="parent",
            cut_category="neural networks.CNN",
        ),
        SplitItem(
            node_id="vit",
            surface="vit",
            name="ViT",
            anchoring="cold",
            cut_category="neural networks.transformer",
        ),
    ]


@pytest.fixture
def corpus():
    return [
        Item(
            dimension="test",
            surface="resnet50",
            name="ResNet-50",
            spellings=["ResNet-50"],
            n_mentions=1,
            n_papers=1,
            mentions=[
                Mention(paper="p1", spelling="ResNet-50", quote="a ResNet-50 backbone")
            ],
        )
    ]


def recorded(surface, node_id, name, parent):
    """A decision that creates *name* under *parent* and points *surface* at it."""
    return DecisionRecord(
        decision=Decision(
            surface=surface,
            outcome=Outcome.CREATED,
            confidence=0.8,
            actions=[
                CreateNode(
                    node_id=node_id,
                    name=name,
                    parent=parent,
                    justification="j",
                    confidence=0.8,
                ),
                AddSurface(
                    surface=surface,
                    canonical=node_id,
                    justification="j",
                    confidence=0.8,
                ),
            ],
        ),
        result=ApplyResult(ok=True),
        provenance=Provenance(
            run_id="r", seq=0, dimension="test", base_version="v0", base_content_hash=""
        ),
    )


# --------------------------------------------------------------------------- #
# Eval items
# --------------------------------------------------------------------------- #


def test_items_without_corpus_evidence_are_kept_not_dropped(
    tiny, tiny_cut, split_items, corpus
):
    """Roughly one held-out name in seven; dropping them would narrow the eval."""
    built = evaluate.build_eval_items(
        tiny, split_items, corpus, dimension="test", cut=tiny_cut
    )
    assert [item.has_evidence for item in built] == [True, False]
    assert built[1].item.n_mentions == 0
    assert built[1].item.name == "ViT"


def test_the_reference_placement_comes_from_the_intact_tree(
    tiny, tiny_cut, split_items, corpus
):
    built = evaluate.build_eval_items(
        tiny, split_items, corpus, dimension="test", cut=tiny_cut
    )
    assert built[0].reference.ancestor_path == ["nn", "cnn", "resnet", "resnet50"]
    assert built[0].reference.cut_category == "CNN"


def test_residue_is_reported_when_ablation_cannot_hide_a_name(tiny, tiny_cut):
    """`resnet50` survives inside its parent's description; v0 does this 24/300 times."""
    items = [
        SplitItem(
            node_id="resnet50", surface="resnet50", name="ResNet-50", anchoring="parent"
        )
    ]
    built = evaluate.build_eval_items(tiny, items, [], dimension="test", cut=tiny_cut)
    assert built[0].residue == []  # the description is scrubbed, not the names
    tiny.create_node("rn50dup", "ResNet-50 variant", parent="cnn")
    built = evaluate.build_eval_items(tiny, items, [], dimension="test", cut=tiny_cut)
    assert built[0].residue == ["ResNet-50 variant"]


# --------------------------------------------------------------------------- #
# Replay decider
# --------------------------------------------------------------------------- #


def test_replay_reapplies_against_the_tree_it_is_handed(tiny, tiny_cut, split_items):
    """Placements and apply failures are recomputed, never trusted from the recording."""
    built = evaluate.build_eval_items(
        tiny, split_items, [], dimension="test", cut=tiny_cut
    )
    decider = evaluate.replay_decider(
        [
            recorded("resnet50", "r50", "ResNet-50", "resnet"),
            recorded("vit", "v", "ViT", "transformer"),
        ],
        cut=tiny_cut,
    )
    records = asyncio.run(
        evaluate.leave_one_out(tiny, built, decider, dimension="test", cut=tiny_cut)
    )
    assert [record.result.ok for record in records] == [True, True]
    assert records[0].result.placement.ancestor_path == ["nn", "cnn", "resnet"]


def test_replay_marks_an_unrecorded_surface_as_failed(tiny, tiny_cut, split_items):
    built = evaluate.build_eval_items(
        tiny, split_items, [], dimension="test", cut=tiny_cut
    )
    decider = evaluate.replay_decider([], cut=tiny_cut)
    records = asyncio.run(
        evaluate.leave_one_out(tiny, built, decider, dimension="test", cut=tiny_cut)
    )
    assert all(record.decision.outcome is Outcome.FAILED for record in records)


def test_leave_one_out_never_mutates_the_base_tree(tiny, tiny_cut, split_items):
    before = tiny.doc.model_dump_json()
    built = evaluate.build_eval_items(
        tiny, split_items, [], dimension="test", cut=tiny_cut
    )
    decider = evaluate.replay_decider(
        [recorded("resnet50", "r50", "ResNet-50", "resnet")], cut=tiny_cut
    )
    asyncio.run(
        evaluate.leave_one_out(tiny, built, decider, dimension="test", cut=tiny_cut)
    )
    assert tiny.doc.model_dump_json() == before


def test_each_item_is_decided_against_its_own_ablated_tree(tiny, tiny_cut, split_items):
    """Non-accumulating: item n+1 must not see item n's ablation."""
    seen = []

    async def spy(onto, ctx, item, provenance):
        seen.append(sorted(onto.nodes))
        return recorded(item.surface, "x", item.name, None)

    built = evaluate.build_eval_items(
        tiny, split_items, [], dimension="test", cut=tiny_cut
    )
    asyncio.run(
        evaluate.leave_one_out(tiny, built, spy, dimension="test", cut=tiny_cut)
    )
    assert "resnet50" not in seen[0] and "vit" in seen[0]
    assert "vit" not in seen[1] and "resnet50" in seen[1]


def test_the_noop_control_sees_the_tree_intact(tiny, tiny_cut, split_items):
    seen = []

    async def spy(onto, ctx, item, provenance):
        seen.append(sorted(onto.nodes))
        return recorded(item.surface, "x", item.name, None)

    built = evaluate.build_eval_items(
        tiny, split_items, [], dimension="test", cut=tiny_cut
    )
    asyncio.run(
        evaluate.leave_one_out(
            tiny, built, spy, dimension="test", cut=tiny_cut, ablated=False
        )
    )
    assert "resnet50" in seen[0] and "vit" in seen[0]


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #


def score_run(tiny, tiny_cut, split_items, decisions):
    built = evaluate.build_eval_items(
        tiny, split_items, [], dimension="test", cut=tiny_cut
    )
    decider = evaluate.replay_decider(decisions, cut=tiny_cut)
    records = asyncio.run(
        evaluate.leave_one_out(tiny, built, decider, dimension="test", cut=tiny_cut)
    )
    return built, records, evaluate.score_items(built, records)


def test_a_perfect_re_creation_scores_full_hierarchical_f1(tiny, tiny_cut, split_items):
    _, _, scores = score_run(
        tiny,
        tiny_cut,
        split_items,
        [
            recorded("resnet50", "r50", "ResNet-50", "resnet"),
            recorded("vit", "v", "ViT", "transformer"),
        ],
    )
    assert [score.hier.f1 for score in scores] == [1.0, 1.0]
    assert [score.agent_category for score in scores] == ["CNN", "transformer"]


def test_an_abstention_produces_no_placement_and_no_hier_score(
    tiny, tiny_cut, split_items
):
    abstain = DecisionRecord(
        decision=Decision(
            surface="vit",
            outcome=Outcome.ABSTAINED,
            confidence=0.2,
            review_notes=["two candidates"],
        ),
        result=ApplyResult(ok=True),
        provenance=Provenance(
            run_id="r", seq=0, dimension="test", base_version="v0", base_content_hash=""
        ),
    )
    _, _, scores = score_run(tiny, tiny_cut, split_items, [abstain])
    vit = [score for score in scores if score.surface == "vit"][0]
    assert vit.agent_path == "" and vit.hier is None
    assert evaluate.decided(scores) == []


# --------------------------------------------------------------------------- #
# Adjudication wiring
# --------------------------------------------------------------------------- #


def test_agreements_score_the_definitional_half(tiny, tiny_cut, split_items):
    built, _, scores = score_run(
        tiny,
        tiny_cut,
        split_items,
        [
            recorded("resnet50", "r50", "ResNet-50", "resnet"),
            recorded("vit", "v", "ViT", "transformer"),
        ],
    )
    pairs, index = evaluate.build_pairs(built, scores, onto=tiny, cut=tiny_cut)
    assert pairs == []  # both agree with the reference path
    evaluate.apply_verdicts(scores, pairs, [], index)
    assert [score.win for score in scores] == [0.5, 0.5]


def test_a_disagreement_is_judged_and_written_back(tiny, tiny_cut, split_items):
    built, _, scores = score_run(
        tiny,
        tiny_cut,
        split_items,
        [
            recorded("resnet50", "r50", "ResNet-50", "cnn"),
            recorded("vit", "v", "ViT", "transformer"),
        ],
    )
    pairs, index = evaluate.build_pairs(built, scores, onto=tiny, cut=tiny_cut)
    assert len(pairs) == 1

    async def judge(pair):
        return adjudicate.JudgeChoice(reason="r", choice=pair.agent_option)

    verdicts = asyncio.run(adjudicate.adjudicate(pairs, judge))
    evaluate.apply_verdicts(scores, pairs, verdicts, index)
    assert scores[0].win == 1.0  # judge preferred the agent
    assert scores[1].win == 0.5  # agreed, never judged


def test_the_judge_sees_no_candidate_annotations(tiny, tiny_cut, split_items, corpus):
    """The blind pair must not show where the current tree puts the neighbours."""
    built = evaluate.build_eval_items(
        tiny, split_items, corpus, dimension="test", cut=tiny_cut
    )
    decider = evaluate.replay_decider(
        [recorded("resnet50", "r50", "ResNet-50", "cnn")], cut=tiny_cut
    )
    records = asyncio.run(
        evaluate.leave_one_out(tiny, built, decider, dimension="test", cut=tiny_cut)
    )
    pairs, _ = evaluate.build_pairs(
        built, evaluate.score_items(built, records), onto=tiny, cut=tiny_cut
    )
    assert "## CANDIDATES" not in pairs[0].evidence
    assert "## EVIDENCE" in pairs[0].evidence


# --------------------------------------------------------------------------- #
# Baselines
# --------------------------------------------------------------------------- #


def test_majority_baseline_answers_the_commonest_reference_class():
    assert evaluate.majority_baseline(["Other", "Other", "t"]) == ["Other"] * 3


def test_levenshtein_baseline_places_under_the_nearest_name(
    tiny, tiny_cut, split_items
):
    built = evaluate.build_eval_items(
        tiny, split_items, [], dimension="test", cut=tiny_cut
    )
    predictions = evaluate.levenshtein_baseline(tiny, built[:1], cut=tiny_cut)
    # with resnet50 ablated the nearest surviving name is "ResNet"
    assert predictions == ["CNN"]


# --------------------------------------------------------------------------- #
# Sequential replay
# --------------------------------------------------------------------------- #


def test_sequential_replay_hides_every_held_out_name_first(tiny, tiny_cut, split_items):
    """Otherwise the decisions collide with the surfaces they are re-creating."""
    _, records, _ = score_run(
        tiny,
        tiny_cut,
        split_items,
        [
            recorded("resnet50", "r50", "ResNet-50", "resnet"),
            recorded("vit", "v", "ViT", "transformer"),
        ],
    )
    diagnostic = evaluate.sequential_replay(
        tiny, records, cut=tiny_cut, surfaces=["resnet50", "vit"]
    )
    assert diagnostic["applied"] == 2
    # drift is measured against the *hidden* tree: the pass put both names back
    assert diagnostic["node_drift"] == 2
    assert diagnostic["nodes_after"] == len(tiny.nodes)
    assert diagnostic["invariants_ok"]


def test_sequential_replay_without_hiding_collides(tiny, tiny_cut, split_items):
    _, records, _ = score_run(
        tiny,
        tiny_cut,
        split_items,
        [recorded("resnet50", "r50", "ResNet-50", "resnet")],
    )
    diagnostic = evaluate.sequential_replay(tiny, records, cut=tiny_cut)
    assert diagnostic["failed"] >= 1


# --------------------------------------------------------------------------- #
# Report and gate
# --------------------------------------------------------------------------- #


def build(tiny, tiny_cut, split_items, decisions):
    built, records, scores = score_run(tiny, tiny_cut, split_items, decisions)
    pairs, index = evaluate.build_pairs(built, scores, onto=tiny, cut=tiny_cut)

    async def judge(pair):
        return adjudicate.JudgeChoice(reason="r", choice="tie")

    verdicts = asyncio.run(adjudicate.adjudicate(pairs, judge))
    evaluate.apply_verdicts(scores, pairs, verdicts, index)
    report = evaluate.build_report(
        tiny, built, scores, dimension="test", split="dev", cut=tiny_cut
    )
    evaluate.add_levenshtein_baseline(report, tiny, built, scores, cut=tiny_cut)
    report.gate = evaluate.evaluate_gate(report)
    return report


def test_a_perfect_agent_sits_on_the_ceiling(tiny, tiny_cut, split_items):
    report = build(
        tiny,
        tiny_cut,
        split_items,
        [
            recorded("resnet50", "r50", "ResNet-50", "resnet"),
            recorded("vit", "v", "ViT", "transformer"),
        ],
    )
    assert report.win.w == 0.5
    assert report.agreement["rate"] == 1.0
    # two categories at equal share -> no variance, so rho is undefined, not 1.0
    assert math.isnan(report.distribution["spearman"])
    assert report.distribution["total_variation"] == 0.0
    assert report.distribution["top5_overlap"] == 1.0


def test_unmeasured_clauses_fail_rather_than_pass_silently(tiny, tiny_cut, split_items):
    report = build(
        tiny,
        tiny_cut,
        split_items,
        [recorded("resnet50", "r50", "ResNet-50", "resnet")],
    )
    unmeasured = [clause for clause in report.gate if math.isnan(clause.value)]
    assert unmeasured and not any(clause.passed for clause in unmeasured)
    assert not report.gate_passed


def test_the_canary_voids_the_report_facing_floor(tiny, tiny_cut, split_items):
    report = build(
        tiny,
        tiny_cut,
        split_items,
        [recorded("resnet50", "r50", "ResNet-50", "resnet")],
    )
    report.canary = {"fired": True}
    clauses = evaluate.evaluate_gate(report)
    floor = [clause for clause in clauses if clause.name.startswith("2")]
    assert len(floor) == 1
    assert floor[0].passed and "VOID" in floor[0].note
    assert not any(clause.name.startswith("2a") for clause in clauses)


def test_consistency_needs_at_least_two_repeats(tiny, tiny_cut, split_items):
    report = evaluate.Report(
        dimension="test", split="dev", base_version="v0", base_content_hash=""
    )
    evaluate.add_consistency(report, [[]])
    assert report.consistency == {}


def test_payload_hash_stability_is_checked_not_assumed():
    def rec(digest):
        return DecisionRecord(
            decision=Decision(surface="s", outcome=Outcome.NO_OP, confidence=1.0),
            result=ApplyResult(ok=True),
            provenance=Provenance(
                run_id="r",
                seq=0,
                dimension="t",
                base_version="v0",
                base_content_hash="",
                payload_hash=digest,
            ),
        )

    assert evaluate.payload_hashes_stable([[rec("a")], [rec("a")]])
    assert not evaluate.payload_hashes_stable([[rec("a")], [rec("b")]])


def test_render_report_states_the_verdict(tiny, tiny_cut, split_items):
    report = build(
        tiny,
        tiny_cut,
        split_items,
        [
            recorded("resnet50", "r50", "ResNet-50", "resnet"),
            recorded("vit", "v", "ViT", "transformer"),
        ],
    )
    text = evaluate.render_report(report)
    assert "# Categorization eval -- test / dev" in text
    assert "0.5 is the analytic ceiling" in text
    assert "**Verdict:" in text


def test_mark_ignore_is_detected_from_either_signal(tiny, tiny_cut):
    from paperext.categorize.placement import to_placement

    marked = DecisionRecord(
        decision=Decision(
            surface="junk",
            outcome=Outcome.MAPPED,
            confidence=0.9,
            actions=[MarkIgnore(node_id="junk", justification="j", confidence=0.9)],
        ),
        result=ApplyResult(ok=True),
        provenance=Provenance(
            run_id="r", seq=0, dimension="test", base_version="v0", base_content_hash=""
        ),
    )
    assert evaluate.marked_ignore(marked)
    placed = DecisionRecord(
        decision=Decision(surface="junk", outcome=Outcome.CREATED, confidence=0.9),
        result=ApplyResult(ok=True, placement=to_placement(tiny, "junk", tiny_cut)),
        provenance=Provenance(
            run_id="r", seq=0, dimension="test", base_version="v0", base_content_hash=""
        ),
    )
    assert evaluate.marked_ignore(placed)


def test_ignore_pool_is_every_ablatable_leaf_under_the_dropped_root(tiny):
    assert evaluate.ignore_pool(tiny) == []  # `junk` carries no surface
    tiny.add_surface("junk", "junk")
    assert evaluate.ignore_pool(tiny) == [("junk", "junk")]


# --------------------------------------------------------------------------- #
# CLI, end to end, zero API calls
# --------------------------------------------------------------------------- #


def test_cli_runs_the_whole_harness_against_a_recording(
    tmp_path, tiny, tiny_cut, split_items, corpus
):
    root = tmp_path / "ontology"
    tiny.save(root / "test" / "v0")

    splits = Splits(
        seed=42,
        dimension="test",
        base_version="v0",
        base_content_hash="",
        pool_size=2,
        dev=split_items,
        gate=[],
        reserve=[],
    )
    splits_path = tmp_path / "splits.json"
    splits_path.write_text(splits.model_dump_json())

    items_path = tmp_path / "items.jsonl"
    items_path.write_text("\n".join(item.model_dump_json() for item in corpus) + "\n")

    decisions_path = tmp_path / "recorded.jsonl"
    decisions_path.write_text(
        "\n".join(
            record.model_dump_json()
            for record in (
                recorded("resnet50", "r50", "ResNet-50", "resnet"),
                recorded("vit", "v", "ViT", "cnn"),
            )
        )
        + "\n"
    )

    out = tmp_path / "out"
    code = evaluate.main(
        [
            "--dim",
            "test",
            "--root",
            str(root),
            "--splits",
            str(splits_path),
            "--items",
            str(items_path),
            "--replay",
            str(decisions_path),
            "--replay-diagnostic",
            "--out",
            str(out),
        ]
    )
    assert code == 1  # unadjudicated clauses cannot pass
    report = json.loads((out / evaluate.REPORT_JSON).read_text())
    assert report["n_items"] == 2
    assert report["n_decided"] == 2
    assert (out / evaluate.REPORT_MD).read_text().startswith("# Categorization eval")
    assert len((out / evaluate.SCORES_FILE).read_text().strip().splitlines()) == 2
    assert (out / evaluate.DECISIONS_FILE).exists()
