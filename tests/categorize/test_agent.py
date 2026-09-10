"""The agent loop, driven entirely by a stub client -- no network (WS-D D1b-2, #52)."""

import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from paperext.categorize import agent
from paperext.categorize.actions import (
    ActionStatus,
    AddSurface,
    CreateNode,
    Decision,
    Outcome,
    Provenance,
)
from paperext.categorize.apply import DECISIONS_FILE, read_decisions
from paperext.categorize.items import Item, Mention
from paperext.categorize.prompt import build_context
from paperext.config import Config
from paperext.ontology import Ontology


def stub_client(*responses, usage=None):
    """A client whose completions are the canned *responses*, in order.

    The established idiom (``tests/test_query.py``): patch the factory, give
    ``create_with_completion`` an ``async def`` side effect returning
    ``(model, usage)``.
    """
    queue = list(responses)
    calls: "list[list[dict]]" = []

    async def create_with_completion(*_a, messages=None, **_kw):
        calls.append(list(messages or []))
        response = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(response, Exception):
            raise response
        return response, dict(usage or {"input_tokens": 10, "output_tokens": 5})

    client = MagicMock()
    client.chat.completions.create_with_completion.side_effect = create_with_completion
    client.calls = calls
    return client


def mapping(surface: str, canonical: str) -> Decision:
    return Decision(
        surface=surface,
        outcome=Outcome.MAPPED,
        confidence=0.9,
        actions=[
            AddSurface(
                surface=surface,
                canonical=canonical,
                justification="the quote names it",
                confidence=0.9,
            )
        ],
    )


def item(name: str, surface: str) -> Item:
    return Item(
        dimension="test",
        surface=surface,
        name=name,
        spellings=[name],
        n_mentions=1,
        n_papers=1,
        mentions=[Mention(paper="0000.0", spelling=name, quote=f"We use {name}.")],
    )


@pytest.fixture
def provenance() -> Provenance:
    return Provenance(
        run_id="test", seq=0, dimension="test", base_version="v0", base_content_hash="h"
    )


# -- the pinned model -------------------------------------------------------- #


def test_the_agent_model_is_configured_separately_from_the_extraction_model(cfg):
    """If it read ``CFG.platform.select``, the gate number would stop being
    attributable to a model the moment the extraction backend changed."""
    platform, model = agent.categorize_settings()
    assert (platform, model) == (cfg.categorize.platform, cfg.categorize.model)

    cfg.openai.model = "some-other-extraction-model"
    assert agent.categorize_settings()[1] != "some-other-extraction-model"


def test_the_client_is_pinned_without_disturbing_the_global_config(cfg, monkeypatch):
    seen = {}

    class FakeBackend:
        @property
        def model(self):
            from paperext.config import CFG

            return CFG.openai.model

        def make_client(self):
            seen["model"] = self.model
            return MagicMock()

    monkeypatch.setattr(
        "paperext.backends.get_backend", lambda name: FakeBackend(), raising=False
    )
    before = cfg.openai.model
    agent.make_client("openai", "pinned-categorizer")
    assert seen["model"] == "pinned-categorizer"
    assert Config.get_global_config().openai.model == before


# -- one decision ------------------------------------------------------------ #


def test_decide_returns_a_validated_decision_and_usage():
    client = stub_client(mapping("resnet101", "resnet"))
    decision, usage = asyncio.run(
        agent.decide(client, [{"role": "user", "content": "x"}])
    )
    assert decision.actions[0].canonical == "resnet"
    assert usage["input_tokens"] == 10


def test_a_decision_is_applied_and_recorded(tiny, tiny_cut, provenance):
    client = stub_client(mapping("resnet101", "resnet"))
    ctx = build_context(tiny, "test")
    record = asyncio.run(
        agent.decide_item(
            client,
            tiny,
            ctx,
            item("ResNet-101", "resnet101"),
            cut=tiny_cut,
            provenance=provenance,
        )
    )
    assert record.result.ok
    assert tiny.resolve("resnet101") == "resnet"
    assert record.provenance.payload_hash
    assert record.provenance.params["usage"]["input_tokens"] == 10
    assert record.provenance.params["repairs"] == 0
    assert record.result.placement.cut_category == "CNN"


def test_a_dry_run_decides_without_mutating(tiny, tiny_cut, provenance):
    client = stub_client(mapping("resnet101", "resnet"))
    record = asyncio.run(
        agent.decide_item(
            client,
            tiny,
            build_context(tiny, "test"),
            item("ResNet-101", "resnet101"),
            cut=tiny_cut,
            provenance=provenance,
            apply=False,
        )
    )
    assert record.result.ok and record.result.dry_run
    assert tiny.resolve("resnet101") is None


# -- the repair loop --------------------------------------------------------- #


def test_a_decision_the_applier_rejects_is_repaired(tiny, tiny_cut, provenance):
    bad = mapping("resnet101", "nosuchnode")
    client = stub_client(bad, mapping("resnet101", "resnet"))
    record = asyncio.run(
        agent.decide_item(
            client,
            tiny,
            build_context(tiny, "test"),
            item("ResNet-101", "resnet101"),
            cut=tiny_cut,
            provenance=provenance,
        )
    )
    assert record.result.ok
    assert record.provenance.params["repairs"] == 1
    # the repair turn quotes the applier's own error back to the model
    last = client.calls[-1]
    assert last[-1]["role"] == "user"
    assert "could not be applied" in last[-1]["content"]
    assert "nosuchnode" in last[-1]["content"]


def test_repairs_are_bounded_and_the_failure_is_recorded(tiny, tiny_cut, provenance):
    client = stub_client(mapping("resnet101", "nosuchnode"))
    record = asyncio.run(
        agent.decide_item(
            client,
            tiny,
            build_context(tiny, "test"),
            item("ResNet-101", "resnet101"),
            cut=tiny_cut,
            provenance=provenance,
            max_repairs=1,
        )
    )
    assert not record.result.ok
    assert record.provenance.params["repairs"] == 1
    assert record.result.actions[0].status is ActionStatus.REJECTED
    assert tiny.resolve("resnet101") is None  # rolled back
    assert len(client.calls) == 2


# -- the run ----------------------------------------------------------------- #


def test_a_run_accumulates_so_later_items_see_earlier_edits(tiny, tiny_cut):
    created = Decision(
        surface="convnext",
        outcome=Outcome.CREATED,
        confidence=0.8,
        actions=[
            CreateNode(
                node_id="convnext",
                name="ConvNeXt",
                parent="cnn",
                description="A modernized CNN.",
                justification="no node means it",
                confidence=0.8,
            ),
            AddSurface(
                surface="convnext",
                canonical="convnext",
                justification="primary mapping",
                confidence=0.8,
            ),
        ],
    )
    client = stub_client(created, mapping("convnextv2", "convnext"))
    records = asyncio.run(
        agent.run(
            client,
            tiny,
            [item("ConvNeXt", "convnext"), item("ConvNeXt V2", "convnextv2")],
            dimension="test",
            cut=tiny_cut,
            concurrency=1,
        )
    )
    assert [r.result.ok for r in records] == [True, True]
    assert tiny.resolve("convnextv2") == "convnext"
    tiny.check_invariants()


def test_a_run_writes_an_auditable_log(tmp_path, tiny, tiny_cut):
    from paperext.categorize.apply import DecisionLog

    client = stub_client(mapping("resnet101", "resnet"))
    path = tmp_path / DECISIONS_FILE
    with DecisionLog(path) as log:
        asyncio.run(
            agent.run(
                client,
                tiny,
                [item("ResNet-101", "resnet101")],
                dimension="test",
                cut=tiny_cut,
                model="pinned-model",
                run_id="r1",
                log=log,
            )
        )
    records = list(read_decisions(path))
    assert len(records) == 1
    assert records[0].provenance.model == "pinned-model"
    assert records[0].provenance.run_id == "r1"
    assert records[0].provenance.base_version == "v0"
    assert records[0].provenance.params["candidate_limit"] > 0


def test_the_leave_one_out_mode_marks_records_ablated(tiny, tiny_cut):
    client = stub_client(mapping("resnet101", "resnet"))
    records = asyncio.run(
        agent.run(
            client,
            tiny,
            [item("ResNet-101", "resnet101")],
            dimension="test",
            cut=tiny_cut,
            apply=False,
        )
    )
    assert records[0].provenance.ablated is True
    assert tiny.resolve("resnet101") is None


def test_the_shared_prefix_is_identical_across_items(tiny, tiny_cut):
    """The cost lever: if the system message moved per item, nothing would cache."""
    client = stub_client(mapping("a", "resnet"), mapping("b", "resnet"))
    asyncio.run(
        agent.run(
            client,
            tiny,
            [item("A", "a"), item("B", "b")],
            dimension="test",
            cut=tiny_cut,
            apply=False,
            concurrency=2,
        )
    )
    systems = {c[0]["content"] for c in client.calls}
    assert len(systems) == 1


# -- the CLI ----------------------------------------------------------------- #


@pytest.fixture
def onto_root(tmp_path, tiny) -> Path:
    tiny.save(tmp_path / "test" / "v0")
    return tmp_path


def test_dump_payload_makes_no_calls(onto_root, tmp_path, capsys, monkeypatch):
    from paperext.categorize.items import write_items

    items = write_items([item("ResNet-101", "resnet101")], tmp_path / "items.jsonl")

    def explode(*_a, **_kw):  # pragma: no cover - must never run
        raise AssertionError("--dump-payload must not build a client")

    monkeypatch.setattr(agent, "make_client", explode)
    assert (
        agent.main(
            [
                "--dim",
                "test",
                "--root",
                str(onto_root),
                "--items",
                str(items),
                "--dump-payload",
            ]
        )
        == 0
    )
    messages = json.loads(capsys.readouterr().out)
    assert [m["role"] for m in messages] == ["system", "user"]
    assert "## TAXONOMY" in messages[0]["content"]


def test_a_run_yields_a_loadable_snapshot_with_invariants_intact(
    onto_root, tmp_path, monkeypatch, capsys
):
    from paperext.categorize.items import write_items

    items = write_items(
        [item("ResNet-101", "resnet101"), item("ViT-L", "vitl")],
        tmp_path / "items.jsonl",
    )
    client = stub_client(mapping("resnet101", "resnet"), mapping("vitl", "vit"))
    monkeypatch.setattr(agent, "make_client", lambda *a, **k: client)
    monkeypatch.setattr(
        "paperext.backends.get_backend",
        lambda name: MagicMock(rate_limit_errors=()),
        raising=False,
    )

    assert (
        agent.main(
            [
                "--dim",
                "test",
                "--root",
                str(onto_root),
                "--items",
                str(items),
                "--out",
                "v1",
                "--concurrency",
                "1",
            ]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "2 decisions (2 applied)" in out

    v1 = Ontology.load(onto_root / "test" / "v1")
    v1.check_invariants()
    assert v1.doc.meta.version == "v1"
    assert v1.resolve("resnet101") == "resnet"
    assert v1.resolve("vitl") == "vit"
    assert len(list(read_decisions(onto_root / "test" / "v1" / DECISIONS_FILE))) == 2


def test_selecting_only_unmapped_names(onto_root, tmp_path, monkeypatch):
    from paperext.categorize.items import write_items

    items = write_items(
        [item("ResNet", "resnet"), item("ResNet-101", "resnet101")],
        tmp_path / "items.jsonl",
    )
    client = stub_client(mapping("resnet101", "resnet"))
    monkeypatch.setattr(agent, "make_client", lambda *a, **k: client)
    monkeypatch.setattr(
        "paperext.backends.get_backend",
        lambda name: MagicMock(rate_limit_errors=()),
        raising=False,
    )
    agent.main(
        [
            "--dim",
            "test",
            "--root",
            str(onto_root),
            "--items",
            str(items),
            "--out",
            "v1",
            "--unmapped-only",
        ]
    )
    assert len(client.calls) == 1  # "resnet" already resolves
