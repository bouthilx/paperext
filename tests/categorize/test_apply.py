"""The transactional applier, the versioned writer and the audit log (#51).

The load-bearing property is **atomicity**: a decision is several ops, there is no
transaction API on :class:`~paperext.ontology.Ontology`, and ``mark_ignore`` is
itself composite and not atomic. So every rejection test below applies a *valid*
action first, and asserts the whole decision rolled back byte-identically.
"""

import json

import pytest

from paperext.categorize.actions import (
    ActionStatus,
    AddSurface,
    CreateNode,
    Decision,
    DemoteToVariant,
    InsertAbove,
    MarkIgnore,
    Move,
    Outcome,
    Provenance,
    RemoveNode,
    RemoveSurface,
    Rename,
    UpdateDescription,
)
from paperext.categorize.apply import (
    DecisionLog,
    DecisionRecord,
    apply_decision,
    content_hash,
    next_version,
    read_decisions,
    suggest_node_id,
    versions,
    write_snapshot,
)
from paperext.ontology import Ontology, to_category_map
from paperext.ontology.ontology import InvariantError


def _mapping(surface, canonical, **kwargs):
    return AddSurface(
        justification="j",
        confidence=0.9,
        surface=surface,
        canonical=canonical,
        **kwargs,
    )


def _decide(*actions, surface="x", outcome=Outcome.MAPPED):
    return Decision(
        surface=surface, outcome=outcome, confidence=0.9, actions=list(actions)
    )


# --------------------------------------------------------------------------- #
# Happy path
# --------------------------------------------------------------------------- #


def test_create_then_map_the_worked_example(tiny, tiny_cut):
    """BiT-S-101: ambiguous by name, resolved to the CNN branch by its grounding."""
    decision = Decision(
        surface="BiT-S-101",
        outcome=Outcome.CREATED,
        confidence=0.82,
        actions=[
            CreateNode(
                justification="'based on a ResNetv2-101 architecture' -> CNN branch",
                confidence=0.82,
                node_id="bits101",
                name="BiT-S-101",
                parent="cnn",
            ),
            _mapping("BiT-S-101", "bits101"),
        ],
    )
    result = apply_decision(tiny, decision, cut=tiny_cut)

    assert result.ok and result.error is None
    assert [a.status for a in result.actions] == [ActionStatus.APPLIED] * 2
    assert tiny.resolve("BiT-S-101") == "bits101"
    assert result.placement.cut_category == "CNN"
    assert result.diff.created == ["bits101"]
    assert result.diff.modified == ["cnn"]
    assert result.diff.surfaces_added == [("bits101", "bits101")]


def test_dry_run_reports_the_diff_and_changes_nothing(tiny, tiny_cut):
    before = content_hash(tiny)
    result = apply_decision(
        tiny,
        _decide(_mapping("residual network", "resnet")),
        cut=tiny_cut,
        dry_run=True,
    )
    assert result.ok and result.dry_run
    assert result.diff.surfaces_added == [("residualnetwork", "resnet")]
    assert [a.status for a in result.actions] == [ActionStatus.DRY_RUN]
    assert content_hash(tiny) == before


def test_flagged_surface_reaches_the_normalization_row(tiny, tiny_cut):
    """``add_surface``'s ``flag`` is how a low-confidence row is marked for review."""
    apply_decision(
        tiny,
        _decide(_mapping("SAM optimizer", "sam", flag="low-confidence")),
        cut=tiny_cut,
    )
    row = next(r for r in tiny.norm if r.surface == "samoptimizer")
    assert row.flag == "low-confidence" and row.via == "agent"


def test_an_empty_decision_is_a_clean_no_op(tiny, tiny_cut):
    before = content_hash(tiny)
    result = apply_decision(
        tiny, _decide(surface="ppo", outcome=Outcome.NO_OP), cut=tiny_cut
    )
    assert result.ok and result.diff.is_empty()
    assert result.placement is None
    assert content_hash(tiny) == before


# --------------------------------------------------------------------------- #
# Rejection: one per op, each proving the *whole decision* rolls back
# --------------------------------------------------------------------------- #

REJECTIONS = {
    "create_node": CreateNode(
        justification="j", confidence=0.5, node_id="resnet", name="dup"
    ),
    "rename": Rename(justification="j", confidence=0.5, node_id="nope", new_name="X"),
    "update_description": UpdateDescription(
        justification="j", confidence=0.5, node_id="nope", description="X"
    ),
    "add_surface": AddSurface(
        justification="j", confidence=0.5, surface="ppo", canonical="vit"
    ),
    "remove_surface": RemoveSurface(
        justification="j", confidence=0.5, surface="never seen"
    ),
    "move": Move(
        justification="j", confidence=0.5, node_id="cnn", new_parent="resnet50"
    ),
    "insert_above": InsertAbove(
        justification="j", confidence=0.5, node_id="vit", new_id="cnn", name="X"
    ),
    "demote_to_variant": DemoteToVariant(
        justification="j", confidence=0.5, node_id="resnet", target_id="vit"
    ),
    "remove_node": RemoveNode(justification="j", confidence=0.5, node_id="cnn"),
    "mark_ignore": MarkIgnore(justification="j", confidence=0.5, node_id="nope"),
}


@pytest.mark.parametrize("op", sorted(REJECTIONS))
def test_rejected_action_rolls_the_whole_decision_back(tiny, tiny_cut, op):
    before = content_hash(tiny)
    decision = _decide(
        _mapping("a first, valid edit", "vit"),  # applied, then must be undone
        REJECTIONS[op],
    )
    result = apply_decision(tiny, decision, cut=tiny_cut)

    assert not result.ok
    assert result.failed_index == 1
    assert result.actions[0].status is ActionStatus.ROLLED_BACK
    assert result.actions[1].status is ActionStatus.REJECTED
    assert result.actions[1].error
    assert result.diff.is_empty()
    assert content_hash(tiny) == before
    tiny.check_invariants()


def test_actions_after_the_failure_are_skipped_not_rejected(tiny, tiny_cut):
    result = apply_decision(
        tiny,
        _decide(REJECTIONS["rename"], _mapping("later", "vit")),
        cut=tiny_cut,
    )
    assert result.actions[0].status is ActionStatus.REJECTED
    assert result.actions[1].status is ActionStatus.SKIPPED


def test_mark_ignore_failing_mid_composite_leaves_no_orphan_root(tiny, tiny_cut):
    """The known D1a non-atomicity, contained by the transaction.

    ``mark_ignore`` creates the ``ignore`` root and *then* moves the node under it
    (``ontology.py:399-418``); a failure in between leaves the fresh root behind.
    The fault is injected because the composite cannot fail on its own — that it
    cannot *today* is not something the applier is entitled to assume.
    """
    tiny.doc.roots.remove("ignore")
    tiny.remove_node("junk")
    tiny.doc.nodes.pop("ignore")
    tiny._reindex()
    tiny.check_invariants()
    before = content_hash(tiny)

    def boom(node_id, new_parent):
        raise InvariantError("injected failure inside the composite op")

    tiny.move = boom

    result = apply_decision(
        tiny,
        _decide(
            MarkIgnore(justification="misextraction", confidence=0.9, node_id="sam")
        ),
        cut=tiny_cut,
    )

    assert not result.ok
    assert "ignore" not in tiny.nodes  # the half-created root is gone
    assert content_hash(tiny) == before


def test_invariant_violation_after_a_locally_legal_decision_rolls_back(tiny, tiny_cut):
    """Every mutator guards only *local* preconditions; the global check is ours."""
    before = content_hash(tiny)
    decision = _decide(
        CreateNode(justification="j", confidence=0.5, node_id="orphan", name="orphan"),
    )
    # each op is individually legal; corrupt the tree the way a bad edit would
    original = tiny.check_invariants

    def failing_check():
        original()
        raise InvariantError("simulated global violation")

    tiny.check_invariants = failing_check
    result = apply_decision(tiny, decision, cut=tiny_cut)

    assert not result.ok
    assert result.failed_index is None  # the decision as a whole, not one action
    assert result.actions[0].status is ActionStatus.ROLLED_BACK
    del tiny.check_invariants
    assert content_hash(tiny) == before


def test_unknown_ids_surface_as_one_exception_family(tiny, tiny_cut):
    """Read accessors raise bare ``KeyError``; the applier normalizes it."""
    result = apply_decision(
        tiny,
        _decide(Move(justification="j", confidence=1.0, node_id="vit", new_parent="?")),
        cut=tiny_cut,
    )
    assert result.error_type == "UnknownNodeError"
    assert "move.new_parent" in result.error


def test_a_bare_keyerror_from_a_mutator_is_normalized(tiny, tiny_cut):
    """Read accessors raise bare ``KeyError``; nothing may escape as one."""

    def boom(node_id, new_name):
        raise KeyError(node_id)

    tiny.rename = boom
    result = apply_decision(
        tiny,
        _decide(Rename(justification="j", confidence=1.0, node_id="vit", new_name="X")),
        cut=tiny_cut,
    )
    assert result.error_type == "UnknownNodeError"


# --------------------------------------------------------------------------- #
# Persistence: version writer, round-trip, audit log
# --------------------------------------------------------------------------- #


def test_write_snapshot_bumps_the_version_and_refuses_to_clobber(tiny, tmp_path):
    assert next_version("test", root=tmp_path) == "v0"
    first = write_snapshot(tiny, "test", root=tmp_path)
    assert first.name == "v0"
    assert Ontology.load(first).doc.meta.version == "v0"

    assert next_version("test", root=tmp_path) == "v1"
    second = write_snapshot(tiny, "test", root=tmp_path)
    assert second.name == "v1"
    assert versions("test", root=tmp_path) == ["v0", "v1"]

    with pytest.raises(FileExistsError):
        write_snapshot(tiny, "test", "v0", root=tmp_path)
    with pytest.raises(ValueError):
        write_snapshot(tiny, "test", "latest", root=tmp_path)


def test_round_trip_preserves_the_roll_up(tiny, tiny_cut, tmp_path):
    apply_decision(
        tiny,
        _decide(
            CreateNode(
                justification="j",
                confidence=0.9,
                node_id="bits101",
                name="BiT-S-101",
                parent="cnn",
            ),
            _mapping("BiT-S-101", "bits101"),
        ),
        cut=tiny_cut,
    )
    expected = to_category_map(tiny, tiny_cut)

    out = write_snapshot(tiny, "test", root=tmp_path)
    reloaded = Ontology.load(out)
    reloaded.check_invariants()
    assert to_category_map(reloaded, tiny_cut) == expected
    assert reloaded.doc.model_dump() == tiny.doc.model_dump()


def test_snapshot_is_byte_stable_across_runs(tiny, tiny_cut, tmp_path):
    """Two independent runs of the same decisions write identical bytes."""
    base = write_snapshot(tiny, "test", "v0", root=tmp_path / "base")

    def build(root):
        onto = Ontology.load(base)
        apply_decision(
            onto, _decide(_mapping("residual network", "resnet")), cut=tiny_cut
        )
        return write_snapshot(onto, "test", "v1", root=root)

    first, second = build(tmp_path / "a"), build(tmp_path / "b")
    for name in ("ontology.json", "normalization.jsonl"):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_decisions_are_appended_one_per_line_and_replay(tiny, tiny_cut, tmp_path):
    """A crashed run keeps what it had already decided, and replays identically."""
    base = write_snapshot(tiny, "test", "v0", root=tmp_path)
    onto = Ontology.load(base)
    base_hash = content_hash(onto)

    decisions = [
        _decide(_mapping("residual network", "resnet"), surface="residual network"),
        _decide(_mapping("vision transformer", "vit"), surface="vision transformer"),
    ]

    path = tmp_path / "decisions.jsonl"
    with DecisionLog(path) as log:
        for seq, decision in enumerate(decisions):
            result = apply_decision(onto, decision, cut=tiny_cut)
            log.write(
                DecisionRecord(
                    provenance=Provenance(
                        run_id="r1",
                        seq=seq,
                        dimension="test",
                        base_version="v0",
                        base_content_hash=base_hash,
                    ),
                    decision=decision,
                    result=result,
                )
            )
    applied_hash = content_hash(onto)

    lines = path.read_text().splitlines()
    assert len(lines) == 2  # one object per line, not a JSON array
    assert all(json.loads(line)["provenance"]["run_id"] == "r1" for line in lines)

    records = list(read_decisions(path))
    assert [r.provenance.seq for r in records] == [0, 1]
    assert records[0].result.placement.node_id == "resnet"

    replay = Ontology.load(base)
    assert content_hash(replay) == base_hash  # the base was not mutated in place
    for record in records:
        assert record.provenance.base_content_hash == base_hash
        assert apply_decision(replay, record.decision, cut=tiny_cut).ok
    assert content_hash(replay) == applied_hash


def test_suggest_node_id_matches_the_v0_convention(tiny):
    assert suggest_node_id(tiny, "BiT-S-101") == "bits101"
    assert suggest_node_id(tiny, "ResNet") == "resnet__2"  # 'resnet' is taken
