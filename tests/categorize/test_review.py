"""The interactive review loop, driven by fed keystrokes (WS-D D1b)."""

import asyncio

from paperext.categorize import agent, review
from paperext.categorize.actions import AddSurface, CreateNode, Decision, Outcome
from paperext.categorize.apply import apply_decision
from paperext.categorize.prompt import build_payload
from tests.categorize.test_agent import item, mapping, stub_client


def keystrokes(*answers):
    """A `read` callable returning *answers* in order; the log records the prompts."""
    queue = list(answers)
    prompts = []

    def read(prompt):
        prompts.append(prompt)
        return queue.pop(0)

    read.prompts = prompts
    return read


def run_interactive(tiny, tiny_cut, decisions, read, log=None):
    shown = []
    reviewer = review.interactive(log, read=read, write=shown.append)
    client = stub_client(*decisions)
    records = asyncio.run(
        agent.run(
            client,
            tiny,
            [item("ResNet-101", "resnet101"), item("ViT-L", "vitl")],
            dimension="test",
            cut=tiny_cut,
            reviewer=reviewer,
        )
    )
    return records, shown, client


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def test_render_decision_shows_reasoning_actions_and_landing(tiny, tiny_cut):
    decision = Decision(
        reasoning="The quote says it is a residual network.",
        surface="resnet101",
        outcome=Outcome.CREATED,
        confidence=0.8,
        actions=[
            CreateNode(
                node_id="resnet101",
                name="ResNet-101",
                parent="resnet",
                justification="a size variant of ResNet",
                confidence=0.8,
            ),
            AddSurface(
                surface="resnet101",
                canonical="resnet101",
                justification="maps the name",
                confidence=0.9,
            ),
        ],
    )
    result = apply_decision(tiny, decision, cut=tiny_cut, dry_run=True)
    from paperext.categorize.actions import Provenance
    from paperext.categorize.apply import DecisionRecord

    record = DecisionRecord(
        decision=decision,
        result=result,
        provenance=Provenance(
            run_id="r",
            seq=0,
            dimension="test",
            base_version="v0",
            base_content_hash="",
            params={"usage": {"input_tokens": 9, "output_tokens": 2}},
        ),
    )
    text = review.render_decision(record, tiny)
    assert "reasoning:" in text and "residual network" in text
    assert "0. create_node(node_id='resnet101'" in text
    assert "because: a size variant of ResNet  [0.80]" in text
    assert "lands at: neural networks > CNN > ResNet > ResNet-101   [CNN]" in text
    assert "creates resnet101" in text and "maps resnet101 -> resnet101" in text
    assert "tokens: 9 in / 2 out" in text


def test_render_decision_surfaces_an_applier_rejection(tiny, tiny_cut):
    decision = mapping("resnet101", "nowhere")
    result = apply_decision(tiny, decision, cut=tiny_cut, dry_run=True)
    from paperext.categorize.actions import Provenance
    from paperext.categorize.apply import DecisionRecord

    record = DecisionRecord(
        decision=decision,
        result=result,
        provenance=Provenance(
            run_id="r", seq=0, dimension="test", base_version="v0", base_content_hash=""
        ),
    )
    assert "REJECTED by the applier" in review.render_decision(record, tiny)


def test_render_candidates_lists_path_and_score(tiny, tiny_cut):
    payload = build_payload(tiny, item("ResNet-101", "resnet101"), cut=tiny_cut)
    text = review.render_candidates(payload)
    assert "`resnet`" in text and "neural networks > CNN > ResNet" in text


# --------------------------------------------------------------------------- #
# The loop
# --------------------------------------------------------------------------- #


def test_apply_applies_and_skip_does_not(tiny, tiny_cut, tmp_path):
    read = keystrokes("a", "looks right", "s", "")
    log = review.ReviewLog(tmp_path / "review.jsonl")
    records, shown, _ = run_interactive(
        tiny,
        tiny_cut,
        [mapping("resnet101", "resnet"), mapping("vitl", "vit")],
        read,
        log,
    )
    assert tiny.resolve("resnet101") == "resnet"  # applied
    assert tiny.resolve("vitl") is None  # skipped
    assert [r.provenance.params["review"] for r in records] == ["apply", "skip"]
    reviews = review.read_reviews(tmp_path / "review.jsonl")
    assert [(r.verdict, r.note) for r in reviews] == [
        ("apply", "looks right"),
        ("skip", ""),
    ]
    assert reviews[0].agent_path == "neural networks > CNN > ResNet"


def test_wrong_and_unsure_are_recorded_verdicts_that_skip(tiny, tiny_cut, tmp_path):
    read = keystrokes("w", "should be under transformer", "u", "")
    log = review.ReviewLog(tmp_path / "review.jsonl")
    run_interactive(
        tiny,
        tiny_cut,
        [mapping("resnet101", "resnet"), mapping("vitl", "vit")],
        read,
        log,
    )
    assert tiny.resolve("resnet101") is None and tiny.resolve("vitl") is None
    assert [r.verdict for r in review.read_reviews(tmp_path / "review.jsonl")] == [
        "wrong",
        "unsure",
    ]


def test_retry_asks_the_model_again_for_the_same_item(tiny, tiny_cut):
    read = keystrokes("r", "a", "", "a", "")
    records, _, client = run_interactive(
        tiny,
        tiny_cut,
        [
            mapping("resnet101", "resnet"),
            mapping("resnet101", "cnn"),
            mapping("vitl", "vit"),
        ],
        read,
    )
    assert len(records) == 2
    assert tiny.resolve("resnet101") == "cnn"  # the second answer won
    assert len(client.calls) == 3


def test_quit_stops_and_returns_what_was_decided(tiny, tiny_cut):
    read = keystrokes("a", "", "q")
    records, _, client = run_interactive(
        tiny, tiny_cut, [mapping("resnet101", "resnet"), mapping("vitl", "vit")], read
    )
    assert len(records) == 1
    assert len(client.calls) == 2  # the second was decided, then abandoned
    assert tiny.resolve("vitl") is None


def test_payload_shows_the_full_prompt_and_reprompts(tiny, tiny_cut):
    read = keystrokes("p", "s", "", "s", "")
    _, shown, _ = run_interactive(
        tiny, tiny_cut, [mapping("resnet101", "resnet"), mapping("vitl", "vit")], read
    )
    assert any("## TASK" in text for text in shown)
    assert len(read.prompts) == 5


def test_an_unknown_key_reprompts_with_help(tiny, tiny_cut):
    read = keystrokes("x", "s", "", "s", "")
    _, shown, _ = run_interactive(
        tiny, tiny_cut, [mapping("resnet101", "resnet"), mapping("vitl", "vit")], read
    )
    assert shown.count(review.HELP) == 1


def test_interactive_forces_a_sequential_run(tiny, tiny_cut):
    """Item two must be decided against the tree *after* item one's verdict."""
    seen = []
    original = agent.decide_item

    async def spy(client, onto, ctx, it, **kw):
        seen.append(onto.resolve("resnet101"))
        return await original(client, onto, ctx, it, **kw)

    agent.decide_item = spy
    try:
        run_interactive(
            tiny,
            tiny_cut,
            [mapping("resnet101", "resnet"), mapping("vitl", "vit")],
            keystrokes("a", "", "s", ""),
        )
    finally:
        agent.decide_item = original
    assert seen == [None, "resnet"]
