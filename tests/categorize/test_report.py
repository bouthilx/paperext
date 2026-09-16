"""``categorize-report`` over a recorded run (WS-D D1b)."""

from paperext.categorize import report
from paperext.categorize.actions import (
    AddSurface,
    CreateNode,
    Decision,
    Outcome,
    Provenance,
    Rename,
)
from paperext.categorize.apply import ApplyResult, DecisionLog, apply_decision
from paperext.categorize.review import Review, ReviewLog


def record(tiny, tiny_cut, decision, seq=0, review=None):
    from paperext.categorize.ablate import copy_ontology
    from paperext.categorize.apply import DecisionRecord

    result = apply_decision(copy_ontology(tiny), decision, cut=tiny_cut)
    params = {"usage": {"input_tokens": 100, "output_tokens": 10}}
    if review:
        params["review"] = review
    return DecisionRecord(
        decision=decision,
        result=result,
        provenance=Provenance(
            run_id="r1",
            seq=seq,
            dimension="test",
            base_version="v0",
            base_content_hash="",
            model="m",
            params=params,
        ),
    )


def created(surface, node_id, name, parent, *extra):
    return Decision(
        surface=surface,
        outcome=Outcome.CREATED,
        confidence=0.9,
        actions=[
            CreateNode(
                node_id=node_id,
                name=name,
                parent=parent,
                justification="j",
                confidence=0.9,
            ),
            AddSurface(
                surface=surface, canonical=node_id, justification="j", confidence=0.9
            ),
            *extra,
        ],
    )


def test_report_replays_and_shows_every_section(tiny, tiny_cut):
    rename = Rename(
        node_id="vit",
        new_name="Vision Transformer (ViT)",
        justification="bare acronym",
        confidence=0.8,
    )
    records = [
        record(
            tiny, tiny_cut, created("resnet101", "resnet101", "ResNet-101", "resnet"), 0
        ),
        record(tiny, tiny_cut, created("vitl", "vitl", "ViT-L", "vit", rename), 1),
        record(
            tiny,
            tiny_cut,
            Decision(
                surface="sam2",
                outcome=Outcome.ABSTAINED,
                confidence=0.2,
                review_notes=["two SAMs"],
            ),
            2,
        ),
    ]
    replay = report.Replay(tiny, records, cut=tiny_cut)
    assert replay.replayed == [True, True, True]  # an abstention applies trivially
    assert set(replay.diff.created) == {"resnet101", "vitl"}
    assert "vit" in replay.diff.modified

    text = report.render(replay, width=140)
    assert "3 decision(s): 1 abstained, 2 created; 3 applied" in text
    assert "tokens: 300 in / 30 out" in text
    assert "ResNet-101" in text and "abstained: two SAMs" in text
    assert "rename(node_id='vit', new_name='Vision Transformer (ViT)')" in text
    assert "because: bare acronym" in text
    assert "(was: ViT)" in text  # the tree diff names the rename
    assert "+ ResNet-101" in text
    assert "at the cut" in text and "CNN" in text


def test_reviewer_skipped_records_are_not_replayed(tiny, tiny_cut):
    records = [
        record(
            tiny,
            tiny_cut,
            created("resnet101", "resnet101", "ResNet-101", "resnet"),
            0,
            review="apply",
        ),
        record(
            tiny, tiny_cut, created("vitl", "vitl", "ViT-L", "vit"), 1, review="skip"
        ),
    ]
    replay = report.Replay(tiny, records, cut=tiny_cut)
    assert replay.replayed == [True, False]
    assert "vitl" not in replay.after
    assert "(skipped by reviewer)" in report.render(replay, width=140)


def test_a_decision_that_no_longer_applies_is_flagged(tiny, tiny_cut):
    twice = created("resnet101", "resnet101", "ResNet-101", "resnet")
    records = [record(tiny, tiny_cut, twice, 0), record(tiny, tiny_cut, twice, 1)]
    replay = report.Replay(tiny, records, cut=tiny_cut)
    assert replay.replayed == [True, False]
    assert "NOT APPLIED on replay" in report.render(replay, width=140)


def test_reviews_are_overlaid(tiny, tiny_cut):
    records = [
        record(
            tiny, tiny_cut, created("resnet101", "resnet101", "ResNet-101", "resnet"), 0
        )
    ]
    reviews = [
        Review(
            run_id="r1",
            seq=0,
            surface="resnet101",
            name="ResNet-101",
            verdict="wrong",
            note="should be under CNN directly",
            outcome="created",
        )
    ]
    text = report.render(
        report.Replay(tiny, records, cut=tiny_cut, reviews=reviews), width=160
    )
    assert "reviewer: 1 wrong" in text
    assert "wrong  should be under CNN directly" in text


def test_cli_end_to_end(tiny, tiny_cut, tmp_path, capsys):
    root = tmp_path / "ontology"
    tiny.save(root / "test" / "v0")
    path = tmp_path / "decisions.jsonl"
    with DecisionLog(path) as log:
        log.write(
            record(
                tiny,
                tiny_cut,
                created("resnet101", "resnet101", "ResNet-101", "resnet"),
                0,
            )
        )
    ReviewLog(tmp_path / "review.jsonl").write(
        Review(
            run_id="r1",
            seq=0,
            surface="resnet101",
            name="ResNet-101",
            verdict="apply",
            outcome="created",
        )
    )
    assert report.main([str(path), "--root", str(root), "--width", "140"]) == 0
    out = capsys.readouterr().out
    assert "1 decision(s): 1 created; 1 applied" in out
    assert "reviewer: 1 apply" in out


def test_renaming_a_cut_node_relabels_its_row_instead_of_emptying_it(tiny, tiny_cut):
    """#62 as the report shows it: one row, same counts, new label."""
    from paperext.ontology.rollup import resolve_cut

    cut = resolve_cut(tiny, tiny_cut)
    rename = Rename(
        node_id="cnn",
        new_name="Convolutional Neural Network (CNN)",
        justification="bare acronym",
        confidence=0.8,
    )
    records = [
        record(
            tiny, cut, created("resnet101", "resnet101", "ResNet-101", "resnet", rename)
        ),
        # placed after the rename: the recorded label is already the new name
        record(tiny, cut, created("bit", "bit", "BiT", "cnn"), 1),
    ]
    replay = report.Replay(tiny, records, cut=cut)
    table = report.cut_table(replay)
    rows = {
        str(cells[0]).split("  ")[0]: [str(c) for c in cells[1:]]
        for cells in zip(*(col._cells for col in table.columns))
    }
    assert "CNN" not in rows  # no orphaned row under the old label
    label = "Convolutional Neural Network (CNN)"
    assert rows[label] == ["2", "3", "5", "+2"]
    assert "(was: CNN)" in str(table.columns[0]._cells[list(rows).index(label)])
