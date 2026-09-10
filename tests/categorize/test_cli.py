"""The ``python -m paperext.categorize.apply`` entry point (#51)."""

import json

import pytest

from paperext.categorize.actions import AddSurface, Decision, Outcome
from paperext.categorize.apply import (
    DECISIONS_FILE,
    content_hash,
    main,
    write_snapshot,
)
from paperext.ontology import Ontology


@pytest.fixture
def workspace(tiny, tmp_path):
    write_snapshot(tiny, "models", "v0", root=tmp_path)
    decisions = tmp_path / "decisions.jsonl"
    decisions.write_text(
        "\n".join(
            Decision(
                surface=surface,
                outcome=Outcome.MAPPED,
                confidence=0.9,
                actions=[
                    AddSurface(
                        justification="j",
                        confidence=0.9,
                        surface=surface,
                        canonical=canonical,
                    )
                ],
            ).model_dump_json()
            for surface, canonical in [
                ("residual network", "resnet"),
                ("vision transformer", "vit"),
            ]
        )
        + "\n"
    )
    return tmp_path, decisions


def _argv(root, decisions, *extra):
    return [
        "--dim",
        "models",
        "--base",
        "v0",
        "--in",
        str(decisions),
        "--root",
        str(root),
        *extra,
    ]


def test_apply_writes_the_next_version_and_its_audit_log(workspace, capsys):
    root, decisions = workspace
    assert main(_argv(root, decisions)) == 0

    out = root / "models" / "v1"
    onto = Ontology.load(out)
    onto.check_invariants()
    assert onto.doc.meta.version == "v1"
    assert onto.resolve("residual network") == "resnet"

    records = [
        json.loads(line) for line in (out / DECISIONS_FILE).read_text().splitlines()
    ]
    assert [r["provenance"]["seq"] for r in records] == [0, 1]
    assert all(r["result"]["ok"] for r in records)
    assert records[0]["result"]["placement"]["cut_category"] is not None


def test_dry_run_writes_nothing(workspace):
    root, decisions = workspace
    before = content_hash(Ontology.load(root / "models" / "v0"))
    assert main(_argv(root, decisions, "--dry-run")) == 0
    assert not (root / "models" / "v1").exists()
    assert content_hash(Ontology.load(root / "models" / "v0")) == before


def test_a_rejected_decision_is_reported_and_sets_the_exit_code(workspace, capsys):
    root, decisions = workspace
    with decisions.open("a") as fh:
        fh.write(
            Decision(
                surface="nope",
                outcome=Outcome.MAPPED,
                confidence=0.5,
                actions=[
                    AddSurface(
                        justification="j",
                        confidence=0.5,
                        surface="nope",
                        canonical="does-not-exist",
                    )
                ],
            ).model_dump_json()
            + "\n"
        )
    assert main(_argv(root, decisions)) == 1
    assert "FAIL" in capsys.readouterr().out
    # the two good decisions still landed
    assert Ontology.load(root / "models" / "v1").resolve("vision transformer") == "vit"


def test_the_cli_refuses_to_overwrite_the_base(workspace):
    root, decisions = workspace
    with pytest.raises(FileExistsError):
        main(_argv(root, decisions, "--out", "v0"))


def test_records_can_be_replayed_back_through_the_cli(workspace, tmp_path):
    """``decisions.jsonl`` is accepted as input, not just as output."""
    root, decisions = workspace
    main(_argv(root, decisions))
    log = root / "models" / "v1" / DECISIONS_FILE
    expected = content_hash(Ontology.load(root / "models" / "v1"))

    replay_root = tmp_path / "replay"
    write_snapshot(
        Ontology.load(root / "models" / "v0"), "models", "v0", root=replay_root
    )
    assert main(_argv(replay_root, log)) == 0
    assert content_hash(Ontology.load(replay_root / "models" / "v1")) == expected
