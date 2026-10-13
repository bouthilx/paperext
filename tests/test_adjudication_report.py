"""Agreement between the assistant's recommendation and the owner's decision."""

from __future__ import annotations

from paperext.adjudication_report import classify, report

HEADER = "paper_id\tfield\tarm_A\tarm_B\trecommended\tchosen\trule\tnote\n"


def _row(**kw):
    base = dict(
        paper_id="p",
        field="models",
        arm_A="x",
        arm_B="y",
        recommended="keep x",
        chosen="keep x",
        rule="r",
        note="n",
    )
    base.update(kw)
    return (
        "\t".join(
            str(base[k])
            for k in (
                "paper_id",
                "field",
                "arm_A",
                "arm_B",
                "recommended",
                "chosen",
                "rule",
                "note",
            )
        )
        + "\n"
    )


def test_agreement_is_insensitive_to_spelling_but_not_to_substance():
    assert classify({"recommended": "keep X", "chosen": "keep x"}) == "agreed"
    assert classify({"recommended": "keep x", "chosen": "drop x"}) == "overruled"


def test_a_missing_recommendation_is_unscored_not_agreement():
    """The first three papers predate the column.

    Counting them as agreement would overstate the rate on exactly the papers
    where the owner overruled most -- paper 1 had roughly six overrides.
    """
    for placeholder in ("", "(not recorded)", "-", "pending"):
        assert classify({"recommended": placeholder, "chosen": "keep"}) == "unscored"
    # A row asked but not yet answered is also unscored, not agreement.
    assert classify({"recommended": "keep", "chosen": "pending"}) == "unscored"


def test_report_separates_scored_from_unscored(tmp_path, capsys):
    log = tmp_path / "log.tsv"
    log.write_text(
        HEADER
        + _row(field="models")  # agreed
        + _row(field="runs", recommended="7 runs", chosen="8 runs")  # overruled
        + _row(field="runs", recommended="(not recorded)")  # unscored
    )
    assert report(log) == 0
    out = capsys.readouterr().out
    assert "3 logged decisions over 1 papers" in out
    assert "UNSCORED" in out
    # models: 1 of 1 scored agreed; runs: 0 of 1 scored agreed, 1 unscored.
    models = next(l for l in out.splitlines() if l.strip().startswith("models"))
    runs = next(l for l in out.splitlines() if l.strip().startswith("runs"))
    assert "100%" in models
    assert "0%" in runs and "unscored   1" in runs


def test_a_missing_log_is_reported_rather_than_raised(tmp_path, capsys):
    assert report(tmp_path / "absent.tsv") == 1
    assert "no log at" in capsys.readouterr().out
