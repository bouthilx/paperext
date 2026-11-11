# Handoff: reference annotation, then ontology construction

For an agent (and its owner) picking this work up without having been in the
earlier sessions. It covers **two jobs that run in sequence**:

1. **Reference annotation** — build human-adjudicated ground-truth extractions
   for a sample of papers, by reconciling two models' extractions with the owner.
2. **Ontology construction** — turn the extracted *names* into a layered,
   faceted ontology, and get an agent to place new names into it.

They are deliberately separable: the extraction schema carries **terms**, and
categorisation happens in a **second pass**. That layering is load-bearing — the
shared surface between extraction and ontology is *vocabulary, not hierarchy*, so
an ontology can be revised without re-extracting anything. Never design a change
that breaks it.

Everything below is grounded in files in this repo. Where a number is quoted, the
file it came from is named so you can re-derive it rather than trust it.

---

## 0. Before anything: environment

```console
uv sync --all-extras          # NOT --extra <one>: that replaces the env
uv run pytest tests           # should be green before you change anything
uv run mypy src/paperext tests
```

`uv sync --extra annotate` (or any single extra) **replaces** the environment and
drops the provider SDKs. If imports of `anthropic`/`openai` start failing, this is
why. Always `--all-extras`.

Configuration: `PAPEREXT_CFG` defaults to `config.mdl.ini`. Every setting has an
env override, `PAPEREXT_<SECTION>_<KEY>`; the useful ones are
`PAPEREXT_DIR_CACHE`, `PAPEREXT_ANTHROPIC_MODEL`, `PAPEREXT_ANTHROPIC_MODE`,
`PAPEREXT_OPENAI_MAX_OUTPUT_TOKENS`, `PAPEREXT_PAPERONI_TOKEN`,
`PAPEREXT_PDF_VIEWER`.

**Credentials are never committed.** `[env]` in `config.mdl.ini` holds blank
placeholders on purpose; the file is tracked. Supply keys at runtime
(`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `PAPEREXT_PAPERONI_TOKEN`) and keep them
out of every file you write. Smoke-test one trivial completion before spending on
a batch:

```console
uv run python -m paperext.backend_check --platform anthropic
```

### The fulltext cache is not in this repo

`data/cache/` is absent from this checkout and nothing is tracked under it. The
converted fulltexts (`<cache>/fulltext/<paper_id>/fulltext.txt` plus the source
PDF) live wherever they were built. **Set `PAPEREXT_DIR_CACHE` to that directory
for every command that touches a paper's text**, and verify resolution before
spending anything:

```console
export PAPEREXT_DIR_CACHE=<path-to-fulltext-cache>
uv run python -c "
import json; from pathlib import Path; from paperext.utils import Paper
raw = json.loads(Path('data/ontology/design/c0_verification/sample.paperoni.json').read_text())
got = [Paper(p).get_link_id_pdf() for p in raw]
print(f'{sum(g is not None for g in got)}/{len(got)} papers resolve')"
```

If you get `0/25`, the cache path is wrong. `Paper._pdfs` globs `CFG.dir.cache`,
which defaults to `data/cache` — a directory that does not exist here. This
exact mistake once made an extraction run query *nothing* and report success;
`query.py` now refuses an empty list, but check anyway. If no cache exists at
all, build one with `uv run download-convert` (needs the `fulltext` extra and a
paperoni token).

---

# Part I — Reference annotation

## I.1 What it is and why it is this expensive

The deliverable per paper is **one validated YAML at
`data/mdl/merged/<paper_id>.yaml`**, plus **one row per adjudicated field** in
`data/ontology/design/c0_verification/adjudication_log.tsv`.

This is ground truth for a model bake-off. A guess recorded here becomes a wrong
score for every arm later, forever. That is the whole reason a human is in the
loop and the reason the protocol is slow.

**The authoritative instructions are
`data/ontology/design/c0_verification/ANNOTATION_SESSION.md` (374 lines).** Read
it in full at the start of every annotation session. This document does not
replace it — it explains the surrounding context, the traps, and what to do when
the instructions run out.

## I.2 One paper per session, fresh session each time

The queue is `data/ontology/design/c0_verification/annotation_queue.tsv`
(26 papers, ordered easiest-first by an arm-disagreement score). Each session
starts cold and is given:

> Read `data/ontology/design/c0_verification/ANNOTATION_SESSION.md` and annotate
> paper `<paper_id>` (arXiv `<n>`, "`<title>`"). It is #N of 26 in
> `annotation_queue.tsv`.

Plus the `PAPEREXT_DIR_CACHE` export and a short paper-specific "what to expect".

One paper per session is not a style preference: the `runs[]` half is slow to
adjudicate and a long session drifts — it starts batching questions, stops
reading the paper, and begins deferring to whichever arm it has learned to
trust. Both of those destroy the artifact.

## I.3 Inputs per paper, and checking them first

```
<cache>/fulltext/<paper_id>/fulltext.txt            the paper text — READ IT
<cache>/fulltext/<paper_id>/*.pdf                   the source PDF
data/mdl/queries/anthropic/claude-opus-5/<paper_id>_00.json    arm A
data/mdl/queries/openai/gpt-5.6-sol/<paper_id>_00.json         arm B
```

Both query buckets also hold an unrelated 25-paper verification batch. **Select
by paper id, never by globbing the bucket.** Confirm both arms' files and the PDF
exist *before* writing the session prompt; a session that discovers a missing arm
halfway has already wasted the owner's attention.

## I.4 The review protocol: one item, one PDF, one page, one question

This is the part most likely to be "improved" into uselessness. It is the owner's
explicit instruction and it is not negotiable.

Build the full highlighted PDF first and hand over the path:

```console
uv run python -m paperext.annotate_pdf <paper_id>
```

Colours: **green** both arms quoted it, **yellow** arm A only, **blue** arm B
only, **pink** your own `--note` highlights. A yellow or blue highlight is
exactly where to look. An *unhighlighted* table row is a recall gap in **both**
arms — which is why the full PDF stays built even once you are working item by
item.

Then, for each disputed item:

1. Write the sentences it turns on to a TSV: `quote<TAB>why you are asking`.
2. Build a PDF carrying **only** those highlights, and open it at the page:

```console
uv run python -m paperext.annotate_pdf <paper_id> \
    --note item.tsv --only-notes --open \
    --out <cache>/fulltext/<paper_id>/item-<n>.pdf
```

`--open` launches the viewer at the first highlight's page, detached, so the
conversation continues. `PAPEREXT_PDF_VIEWER` overrides the viewer; without
`--open` the tool prints every highlight's page and a ready-to-paste command.

3. **Then ask one question**: the two arms' answers, the rule you think decides
   it, your recommendation, and what to look at on the page now open.
4. Record the answer. Move on. **Do not queue several questions** — the owner is
   reading one page.

**Copy every quote verbatim from `fulltext.txt`.** A retyped paraphrase matches
nothing and shows up only as an `UNMATCHED` count. Read the tool's summary line:
`elided` counts quotes containing `...` (not verbatim, cannot be located — one
arm writes these), and `UNMATCHED` usually means a **transposition**, not a
fabricated citation. One real case: an arm quoted "stochastic differential
editing" where the paper reads "differential stochastic editing" — in a paper
that spells it both ways itself. Check before concluding anything stronger.

Order of work: **entities first, `runs[]` last**, because `runs[]` references
entities by verbatim name, so names must be settled first. Within entities:
`title`, `description`, `type`, `research_fields`, `models`, `data_sources`,
`libraries`, `algorithms`, `runs`.

**Batch the easy ones.** Six names differing only by spelling are one list and
one decision. Reserve the slow evidence-heavy treatment for items that turn on a
rule.

## I.5 What is *not* being annotated

Do not ask the owner about `provenance`, `referent`, or the domains / models /
algorithms ontology axes. **None of them is extracted.** They are assigned
post-hoc from the name and the quote. Exactly one ontology value set is in the
schema: `access` on `runs[].data_sources[]`, because access is a property of the
*mention*, not of the entity.

That mention-versus-entity split recurs. `consumed` on `runs[].data_sources[]`
('1M environment steps', '200k frames', '10% of the training split') is there for
the same reason: an interactive environment has no size of its own, so 1M steps
is a fact about one run. `RefDataSource.size` stays what the paper says the
*source* is.

## I.6 The rules that actually decide disagreements

`ANNOTATION_SESSION.md` §3 is the canonical list and every entry carries the date
and the paper that settled it. The ones that come up most:

- **A run is a unit of compute the paper spent.** Two executions are the same run
  unless execution mode, precision, parallelism, accelerator count/type, scale,
  or *amount of data processed* differs. 5 seeds × 20 learning rates is **one**
  run with two `repetitions` factors, not 100 runs.
- **A fitting run is one coupled optimisation loop.** A GAN is one run.
  Actor+critic, encoder+decoder: one run. A **frozen** network supplying targets
  or scores is a *participant* with a non-`main` role, not a run.
- **Only models THIS paper executed get a Run.** Quoted numbers from another
  paper or a leaderboard ⇒ `is_executed=false`, no run. *But* execution carries
  forward across related tables when an earlier table states the models were
  trained and a later related one is silent; a stated attribution elsewhere still
  wins.
- **A Model is a separable learned object.** A solver, proof checker or
  hand-written heuristic is an Algorithm or a Library, never a Model.
- **A Data Source is a source of examples a run consumes** — by name when it has
  one, by the paper's description when it does not. Excluded: the vendor/website
  the examples came from, the software implementing the source (the simulator
  *engine* is a Library; the environment is a Data Source), and an **evaluation
  protocol** over a source.
- **A subset is the same source** unless it is a standard artifact named and
  reused *beyond this paper*. The test is whether others use that name.
- **`repetitions` is a list of factors**; the product is computed later. An empty
  list means the paper does not say — **never** a count of 1. Never record how
  many examples the run processed: that is workload (and belongs in `consumed`).
- **A research field the paper only MENTIONS is not a field of the paper.** For
  every `referenced` field, name the reported entity that carries it; if you
  cannot, drop it. This check is mechanical — run it on yourself.
- **Never infer** a compute field the paper does not state. But **never-infer
  binds the extractor, not you**: the rule exists because a single-shot model
  with no lookup hallucinates. You can check, so *verified* outside knowledge
  belongs in the reference.
- **An alias names the SAME thing.** A concept that deserves its own node is
  never an alias.
- **Names stay as the paper writes them**, abbreviation included. Do not expand
  an acronym the paper leaves bare.

When a rule does not exist for the case in front of you, **say so and explore**:
grep the fulltext, read the section, check the table, come back with what you
found. Do not ask the owner to adjudicate a question you have not yet made
answerable, and do not guess to avoid admitting that.

If the case needs a **schema change** rather than a decision, stop and say so. Do
not encode a workaround into ground truth.

## I.7 The logging rule that the whole exercise depends on

Append the row to `adjudication_log.tsv` **when you ask, not when you finish**:
`recommended` filled, `chosen=pending`; update `chosen` once the owner answers.

A `recommended` written after the answer is known is worthless as evidence,
because the agent filling it in has already seen the outcome. **A recommendation
is only a prediction if it is recorded before the outcome.** And it must be
filled **even when it matches** — a column that records only disagreements cannot
measure agreement, and agreement is the quantity that decides how much of this
can ever be automated.

Check yourself as you go:

```console
uv run python -m paperext.adjudication_report
```

It deliberately counts a missing `recommended` as **UNSCORED**, not as agreement.
As of the last run: **81% over 27 scored decisions, with 61 unscored** — the 61
are the first three papers, logged before the column existed, and they say
nothing about the assistant either way.

## I.8 Output, validation, commit

Validate **before** writing:

```python
from paperext.structured_output.mdl.model import PaperExtractions
from paperext.structured_output.utils import model_dump_yaml
text = model_dump_yaml(extractions)   # raises if it does not validate
```

Then `data/mdl/merged/<paper_id>.yaml`, the log rows, **one commit per paper**,
message `Reference annotation: <paper_id> (<arxiv>)`.

`merge_papers.py` (`uv run merge-papers`) is the interactive field-by-field
alternative in `$EDITOR`. Use it only if the owner prefers it: a session doing the
adjudication conversationally should write the file itself, because the point of
this format is that the reasoning happens in the conversation.

Rules for the annotator, not the schema:

- **Never invent a value to finish a field.** `unknown` and `[]` are real answers
  and the schema is built to carry them.
- **Never default to one arm** because it is usually right. The reference set
  exists to measure that; seeding it with the assumption destroys the
  measurement.
- **Absence is a real answer.** A survey correctly has `runs: []`.
- **Report what the owner decided, not what you proposed.**

## I.9 What the two arms do, measured over all 26 papers

From `ANNOTATION_SESSION.md` §5:

| | |
|---|---|
| per-entity agreement | models **79%**, data sources **82%**, algorithms **69%**, libraries 68% |
| fields differing per paper | ~4.9 of 6 |
| runs | arm A 185 total, arm B 224; same count on only **5 of 26** papers |

**Arm A over-admits** (higher recall, lower precision) — its extras have included
a crowdsourcing platform as a *library*. **Arm B splits runs more** and
under-admits entities. Scored against the first three merged references:
libraries F1 1.00 both; models ~0.96 both; research_fields A 0.69 / B 1.00;
data_sources A 0.87 / B 1.00; algorithms A 0.91 / B 0.86.

**`runs[]` is where everything differs, and both arms are wrong in the same
direction.** Across the first three annotated papers the reference holds 89 runs
against arm A's 20 and arm B's 26; one paper alone has 61 in truth against 6 and
10 from the arms (verified as a genuine model × dataset cross-product, not
duplication). **Consequence: arm-to-arm agreement on `runs[]` is worthless as a
quality proxy.** Do not let it be used as one.

Known failure modes, so you recognise rather than rediscover them:

- a **frozen encoder labelled `main`** — ten encoders saying `inference` inside a
  `train` run, in *both* arms, on one paper;
- **`executed-without-run`** — a whole model family marked executed with no run
  accounting for it;
- **protocols as data sources**;
- **non-learned tools as models** — solvers, proof checkers, tokenizers.

---

# Part II — Building the ontology

## II.1 The shape of the pipeline

```
extractions (JSON per paper)
  └─ paperext.categorize.items        fold mentions -> one decidable Item per distinct name
       └─ design: axes authored as TSV node tables under data/ontology/design/axes*/
            └─ paperext.ontology.convert_axes --write    TSV -> loadable snapshot
                 └─ data/ontology/<dim>/v<N>/{dimension.json, <axis>/ontology.json,
                                              normalization.jsonl}
                      └─ paperext.ontology.Ontology.load     indexes + mutation API + invariants
                           └─ paperext.categorize.*          agent places new names
                                └─ paperext.categorize.evaluate   the gate: may it run at scale?
```

Two artifacts define a snapshot (`src/paperext/ontology/schema.py`):

- **`ontology.json`** — an id-keyed node map (adjacency via `children`), an
  ordered `roots` list, and `meta`. A node listed under more than one parent is a
  DAG edge; the format allows it, single-primary is the convention.
- **`normalization.jsonl`** — one row per surface form → the single canonical node
  id it resolves to. Strictly surface → one canonical. **Ambiguous bare surfaces
  are left out, never guessed.**

A **faceted** dimension adds `dimension.json`: which axis is the backbone (empty
when there is none) and how each axis inherits. Each axis is then its own
hierarchy with its own `ontology.json`, so cuts, roll-up, the mutation API and the
invariants all work per axis unchanged.

Current state on disk: `domains/v1` (5 independent axes: discipline, method,
modality, properties, sector), `models/v6` (lineage as backbone),
`algorithms/v1` (lineage, role, signal, attributes), `data_sources/v1` (access,
provenance, referent — no backbone).

## II.2 The design process that worked — and the order matters

`data/ontology/design/PROCESS.md` is the process record for the domains
hierarchy, written to be reused. Read it before designing any new dimension. The
sequence:

**Step 0 — measure before deciding anything.** Node counts, compound names,
`Other` rate at the cut, depth, branching. On the legacy trees this produced the
single most useful early finding: **the cut file, not the tree, caused most of the
`Other` rate**. Without measuring, a one-file problem would have been "fixed" by
rebuilding a tree.

**Step 1 — several independent agents, identical brief,** with no sight of the
legacy tree or of any prior attempt. The point is to see what *replicates*. The
*arguments* each gives matter more than the structures.

**Step 2 — design the levels, not the nodes.** The decisive move is from "which
categories should exist" to "**what characteristic divides this sibling set**".
Nodes are derived from the principle, never chosen directly.

**Step 3 — iterate with the owner on principles, one axis at a time.** A long
conversation, not a document review. Expect the design to change repeatedly.

**Step 4 — derive nodes per axis, from the schema rather than from the corpus.**

**Step 5 — validate three ways** (§II.5).

## II.3 Rules that survived, each for a reason

1. **The corpus bounds scope and exposes blind spots; it does not arbitrate.** A
   category with no corpus support is *possibly speculative — justify or keep*; a
   corpus cluster with no category is a *blind spot*. Neither auto-deletes. An
   earlier brief said "if you cannot find three examples, drop it" — that deletes
   legitimate areas a one-year single-institute snapshot happens not to contain,
   and rewards fitting this corpus over describing the field.
2. **One principle per sibling set, not per level.** Different parents may divide
   by different characteristics. Violating this produces `X and Y` node names and
   junk drawers.
3. **A child sibling set must refine its parent's characteristic**, never import
   another aspect's.
4. **Volume decides which node to open next; it plays no part in how it opens.**
   Draft the sibling set from the field's own structure with **no corpus
   access** → freeze it → *then* consult the corpus, for two questions only
   (blind spot to add, speculative node to flag) → deliver both versions with
   every change and its reason.
5. **External classifications supply vocabulary and breadth, never arbitration.**
   Widely used schemes fail our own granularity audit, and a literal reading of a
   broad category can swallow the entire corpus.
6. **A property attaches at the highest node where it holds for every
   descendant.** The inverse is a check: a property not uniform across children
   means push it down, or the node fuses two things.
7. **An axis is admitted only if two papers can differ on it while agreeing on
   every other axis.**
8. **Never balance categories by paper count.** The study measures proportion of
   research per area; engineering equal sizes destroys the quantity being
   measured.

**A protocol hole worth not repeating:** a corpus-free drafting phase was
undermined because the brief told agents to read `nodes.tsv` for the parents'
characteristics — and that file carries `examples`, `corpus_names` and
`corpus_mentions` in adjacent columns. Two agents reported the contamination
rather than benefiting from it. **Publish a count-free characteristics file and
point the corpus-free phase at that.**

## II.4 Authoring and converting

Axes are authored as **TSV node tables** under `data/ontology/design/axes*/<axis>/nodes.tsv`
— a TSV is what a person reviews in a diff, so it stays the source of truth.
Columns (domains/discipline, as an example):

```
node_id  name  parent_id  depth  oecd_code  characteristic  positive_test
negative_test  examples  corpus_names  corpus_mentions  notes
```

`characteristic` / `positive_test` / `negative_test` are the point: they are what
makes a placement checkable by someone who did not design the node.

Convert to the loadable snapshot:

```console
uv run python -m paperext.ontology.convert_axes --write
```

**Column spellings differ between dimensions and must not be guessed at** —
`parent_id` with a single parent (domains, models facet axes) vs `parents` with
`|` (models lineage) or `;`/`,` (algorithms). A parent id that does not resolve is
a dangling edge and the audit reports it; getting the separator wrong fails loudly
rather than silently.

The loader (`paperext.ontology.Ontology`) gives ancestry, roots, surfaces,
`resolve`, `search`, a mutation API (`create_node`, `rename`, `move`,
`add_surface`, `insert_above`, `demote_to_variant`, `mark_ignore`, …) and
`check_invariants()`. Mutations enforce the structural invariants — the pydantic
models themselves are deliberately permissive containers.

**Trap:** adding a field to `Node` changes the content hash. Expect it and plan
the migration (`paperext.ontology.migrate`) rather than being surprised by a
snapshot that no longer matches.

## II.5 The three validation instruments, and what each caught

**Tail validation.** A stratified random sample of names (e.g. 50 from the
≥3-paper band, 100 singletons), placed using **only the written tests**. The
output is not placements but a **strain list**: where a rule was ambiguous or
missing. 9 findings from 150 names, including two blocking gaps. *This measures
the schema, not the corpus — a name that cannot be placed is a schema defect.*

**Granularity audit.** For every sibling set: are these the same *kind* of thing,
at the same level of specificity, and **does any sibling exist only because it
was large in this corpus?** This caught the defect that reshaped an entire axis —
a 84-mention topic was a top-level branch while a 43-mention peer was not. That is
balancing by paper count through the back door.

**External diff.** Compare against a designed classification, an author-chosen
external label, and a task vocabulary. Found three blind spots that **two
independent sources agreed on**, none of them findable from the corpus.

**And: make agents audit their own output.** Every derivation brief required the
agent to run the granularity audit on itself and **declare the sibling sets it was
not confident in**. That was consistently the highest-value section of their
reports — one declared that two of its own nodes existed partly because they were
large in the corpus, which is exactly the defect being hunted.

## II.6 Categorising names into the tree

`paperext.categorize` is the agent that places an extracted name. Read the module
docstrings; they state the reasoning, not just the API.

- **`items.py`** — folds *mentions* into one decidable `Item` per distinct name.
  The agent decides about names; the corpus stores mentions (same model, twenty
  papers, six spellings, a different quote each time). Grounding is
  **extraction-records-only**: quote, justification, aliases, `is_executed` and
  co-occurring entities. No paper fulltext is required.
- **`candidates.py`** — multi-stage retrieval, and **the most likely cause of a
  bad decision is retrieval, not judgment**. Measured on 1208 unmapped model
  names against the legacy tree, `Ontology.search` alone returns **nothing at all
  for 96.4%** of them: it matches `query ⊆ node key`, so `resnet50` finds no
  `resnet`. An agent cannot place a name whose neighbourhood it never sees.
- **`prompt.py`** — a *pure* function of (ontology, item, candidates) → payload,
  with a deterministic renderer and a `payload_hash`. Without a provable hash, a
  self-consistency disagreement cannot be told apart from a payload that quietly
  differed.
- **`actions.py` / `apply.py`** — a decision is an *ordered* list of actions over
  the mutation API, applied transactionally with snapshot/rollback (`mark_ignore`
  is itself composite and non-atomic, so a failure halfway would leave a
  half-edited tree).
- **`review.py`** — `categorize --interactive` decides one item, shows what the
  model was given and what it decided, and waits. Every verdict is appended to
  `review.jsonl`: following along *is* the human audit, recorded as it happens.
- **`report.py`** — `categorize-report` replays a run's `decisions.jsonl` onto a
  copy of its base version, so it shows the tree before and after rather than
  trusting the recorded diffs.

The categorisation model is pinned **separately** from the extraction model
(`[categorize] platform` / `model`, never `[platform] select`). If the agent read
the extraction selection, swapping the extraction backend would silently change
what the gate was measured on.

## II.7 The gate: does the agent earn the right to run at scale?

`paperext.categorize.evaluate` — one question, answered before any bulk run.

The protocol is **leave-one-out and non-accumulating**: each item is decided
against its *own* single-item-ablated copy of the tree (`ablate.py`, a deep copy
with the item's node, surfaces and every textual trace scrubbed — never a
filtering view, which would leak the first time someone adds an accessor).
Ablating all items at once would gut the sibling context every placement depends
on and correlate the errors, making the confidence interval a decoration.

**No flat accuracy** (`metrics.py`). The classes nest and are heavily skewed, so
accuracy mostly measures the prior and scores "one level up" exactly like "the
wrong branch". The three families that survive: hierarchy-aware per-item
agreement, distributional shape, and a **blind pairwise win rate** with an
analytic 0.5 ceiling.

The win rate is only meaningful if the judge cannot tell which side is the legacy
tree (`adjudicate.py`): paper evidence plus two *anonymised* ancestor paths in
randomised order, no node ids, no version labels, no "reference"/"agent" wording.
Order-blindness is **structural** — a `swap` of a pair renders as the original
with the blocks exchanged. And the judge must be a **different vendor** from the
categorisation model; a same-family judge preferring its own output biases the
win rate in the one direction that matters.

Alongside it, `probes.py` gives reference-free control sets with known-correct
answers that do **not** come from the legacy tree, so they do not inherit its
subjectivity — including a **no-op control** of already-mapped, un-ablated names,
which catches an agent that churns the tree for the sake of answering.

## II.8 Checking extractions before trusting them

Two reference-free harnesses, both worth running on any new extraction corpus.

```console
uv run python -m paperext.structured_output.mdl.verify data/mdl/queries/<provider>/<model>
```

Three kinds of result, and the distinction is the point:

- **CHECK** — pass/fail. A failure is a **prompt defect**.
- **PROBE** — must be non-zero. Zero means a widened scope never reached the
  prompt.
- **MEASURE** — a number with no pass condition, because the risk being sized has
  no correct value.

What it currently covers: slot-misroute checks (optimiser names in `libraries[]`,
a framework in `models[]`, a simulator engine in `data_sources[]`), an evaluation
protocol as a data source, an unnamed description as a data source, a `generate`
run with a parameter count, three region probes with their unmatched-name
counterparts, two acceptance cases carried from the issue, runs-per-paper,
`repetitions` factors/product and repetitions-misread-as-workload, per-field and
`consumed` coverage, `access` and `execution_mode` distributions, and every
`check.py` code.

`check.py` is the per-record invariant checker:
`unresolved-reference` (a run naming nothing in the entity list — usually a
spelling the extractor did not repeat exactly), `referenced-but-not-executed`,
`execution-mode-disagrees`, `generate-run-with-models`, `executed-without-run`.

`BASELINE.md` is the same instrument over the legacy corpus, and it exists because
**a harness whose checks cannot fail is worse than no harness**. 10 of 15 pass/fail
checks failed there, and every failure was one the record predicted. Read the
comparison narrowly: **a v5 failure that also appears in the baseline is
inherited; one that appears only in v5 is new.** Nothing else can be read off it —
the baseline came from a different prompt against a schema with no `runs[]`.

**The trap this whole pass can walk into**, quoted because it is easy to
rationalise away:

> Do not fix a disappointing result by narrowing the prompt's vocabulary. If a
> region comes back empty, the finding is about the prompt's **scope statement**,
> not its vocabulary.

The probe sets exist to *detect* regions. Handing them to the extractor as a
closed list makes the whole exercise circular — it would find only what was
listed, and the revision would rubber-stamp the design.

---

# Part III — What could go wrong

## III.1 In annotation

- **Deferring to an arm.** The most expensive failure, and it is invisible in the
  output. The reference set exists to measure the arms; seeding it with
  "B is usually right on research_fields" destroys that measurement.
- **Batching questions.** Produces a table of decisions the owner cannot check
  against the page, which is how a wrong `runs[]` decomposition gets ratified.
- **Filling `recommended` after the answer.** Turns the only honest evidence about
  automation into decoration. If you realise you did this, mark the row unscored
  rather than keeping a contaminated prediction.
- **Paraphrased quotes.** Highlight nothing, so the owner adjudicates from your
  prose instead of the paper.
- **Inventing a value to finish a field.** `unknown` and `[]` are real answers.
- **Treating arm-to-arm agreement on `runs[]` as a quality signal.** Both arms
  are wrong by 3–4× in the same direction (§I.9).
- **Annotating without reading the paper.** You cannot adjudicate from two
  extractions; that is the entire reason for the human.

## III.2 In ontology design

- **Letting the corpus arbitrate.** Deletes real areas a one-year
  single-institute snapshot happens to miss.
- **Balancing by paper count**, including through the back door — a large-in-corpus
  topic promoted to a top-level branch while a peer of similar kind is not.
- **Choosing nodes instead of deriving them from a stated characteristic.**
  Produces `X and Y` names and junk drawers.
- **Corpus contamination of a corpus-free phase** via adjacent count columns in
  the file you told the agent to read.
- **Confusing the dimension you are in.** Recurring enough that the fix is
  procedural: name the dimension in the first line of every issue and summary.
- **Quoting a per-branch count computed over the head of the distribution.** This
  happened repeatedly and was wrong every time: one axis was estimated at ~93
  mentions and measured at **389**; per-branch figures for another undercounted by
  **2.5×**. Label every count in a design document as indicative, and never quote
  one without computing it over the whole vocabulary.
- **Fixing from source instead of from a failing case.** One rule was diagnosed by
  reading the scorer, changed nothing, cost a run — and the first look at an
  actual failing record showed the agent had been right all along. **Look at one
  failing example before writing any fix.**
- **A correct decision with a false rationale.** One clause was dropped with a
  reason that was wrong, though the decision held. That is a trap for whoever
  reads it next; correct the rationale in place.
- **Claiming a field is available because it is in the schema.** Two fields were
  described as "already recorded per mention" when they existed only in a schema
  version no corpus had ever been extracted with. **Check the data, not the
  schema.**

## III.3 In the plumbing

- **`PAPEREXT_DIR_CACHE` unset** → every paper resolves to `None` → a run that
  queries nothing. Verify `N/N papers resolve` first.
- **`--platform` omitted** → output lands in whichever bucket `[platform] select`
  names. The model half of the bucket path comes from that backend's own config
  section, not from the flag, so changing `model` silently changes the directory.
- **Truncation reads as a parse error on the Responses API.** The Anthropic
  backend inspects `stop_reason` and raises "output truncated at max_tokens=…";
  a truncated Responses reply arrives as **partial JSON** and surfaces as a
  validation failure with no mention of a ceiling. If unexplained validation
  failures appear, **check `output_tokens` on the neighbouring papers before
  looking anywhere else.**
- **Structured-output mode depends on the model.** Some newer models **reject a
  forced tool call** (HTTP 400) and need `json_schema`; the `json` mode puts the
  schema in the prompt and parses the reply with a strict decoder that extracted
  quotes trip. One known-good combination for the current extraction schema is
  `claude-opus-5` with `mode=tools`. Where `json_schema` is needed, a large schema
  can be refused outright with a compiled-grammar size error — which is the
  standing argument for splitting extraction into two calls (entities, then runs).
- **A schema change invalidates stored extractions.** When `repetitions` became a
  factor list, 25 existing extractions stopped validating (they skip with a
  warning rather than degrading). When a required field is *added*, previously
  valid files break — the fix is a pydantic `default_factory`, which costs nothing
  because `strict_schema()` marks every property required regardless of pydantic
  defaults, so the API still demands the field. **Before adding a required field,
  count how many stored extractions it invalidates** — the annotation sessions
  read those files.
- **Concurrency is bounded by a rate limit this repo cannot know.** Raise
  `--concurrency` only after a run has shown headroom. Exceeding it trades
  throughput for backoff rather than failing.

## III.4 Failure modes of *your own harness* (observed, four times)

Every one came from **matching more surface than the rule covers**, and two
produced **false FAILs on acceptance tests**:

- a literal `['unknown']` counted as a stated value;
- `str(enum)` yielding `ClassName.MEMBER` instead of the value;
- normalised names having no separators left to tokenise;
- a *generic alias* making a properly named source look unnamed.

So: before reporting that a check failed, read one failing record end to end.
And run the suite green **before** committing, not after — this was violated
twice.

---

# Part IV — What is missing or unfinished right now

Verified against the repo at the time of writing.

1. **One annotated paper has no merged YAML.** `adjudication_log.tsv` carries 14
   scored decisions for paper 5 of the queue, and the rules it settled were
   committed, but `data/mdl/merged/` holds only **4** of the 5 new annotations
   (`ls data/mdl/merged | grep -c '^69a5'` → 4). **Either reconstruct that YAML
   from the session's decisions or re-adjudicate it; do not let the queue advance
   past it unnoticed.**
2. **21 of 26 queue papers are un-annotated.** `data/mdl/merged/` holds 114 files,
   110 of them the legacy corpus.
3. **61 of 88 logged decisions are UNSCORED** — the first three papers predate the
   `recommended` column, so the assistant's agreement rate rests on 27 decisions
   (81%). It is a small sample and should be read as one.
4. **Papers annotated before the `consumed` field exists have it empty.**
   Backfilling is cheap (only the interactive-environment papers have anything to
   put there) but it has not been done, and `consumed coverage` in `verify.py`
   will read low until it is.
5. **A two-call extraction split (entities, then runs) is designed but not
   built.** Each added schema field narrows the margin on the structured-outputs
   path, which already cannot carry this schema on some models.
6. **An ontology revision pass is open**, carrying ~11 data-source items, at least
   one genuine coverage gap, and a duplicate-node pair that differ only in how the
   name is spelled out.
7. **Two deliberately-deferred conflicts in the annotation rules.** Two overrides
   on the data-source *unnamed-description* boundary produced an outcome that
   conflicts with the exclusion as written; the log flags it and the owner chose
   to look at it separately. Also, `derived_from` has no parent to name when the
   parent is unnamed (a proprietary simulator). Both are recorded, neither is
   resolved — do not silently resolve them in a session.
8. **`Explained[list[...]]` has never been exercised by a live API call.** It
   produces a valid closed strict schema when checked locally, but schema *shape*
   has broken at the API before.
9. **Half of one invariant is not mechanised**: the ontology-role side of the
   `execution_mode` check (no fitting-role algorithm inside an inference run) is
   not in `check.py`. It is mechanisable now; writing it blind would be guessing
   at the shape of the failure.

---

# Part V — What to look out for, as a checklist

**Before a session**

- [ ] `uv sync --all-extras`; `uv run pytest tests` green.
- [ ] `PAPEREXT_DIR_CACHE` set; fulltext and PDF present for the paper.
- [ ] Both arms' JSON present **for that paper id** (not globbed).
- [ ] `ANNOTATION_SESSION.md` read in full, this session.

**During**

- [ ] Full highlighted PDF built and its path handed over.
- [ ] Entities before runs; agreement stated in one line and skipped.
- [ ] Every quote copied verbatim from `fulltext.txt`.
- [ ] One item → one `--only-notes` PDF → one question.
- [ ] Log row appended **at the moment of asking**, `chosen=pending`.
- [ ] Every `referenced` research field can name the entity that carries it.
- [ ] Any rule gap stated out loud, not papered over.

**Before committing**

- [ ] `model_dump_yaml` ran without raising.
- [ ] `chosen` updated on every pending row; no blank `recommended`.
- [ ] `uv run python -m paperext.adjudication_report` reviewed.
- [ ] `uv run pytest tests` and `uv run mypy src/paperext tests` green.
- [ ] One commit per paper, on a branch — **never commit to `main`; open a PR.**
- [ ] No credentials in any tracked file.

**When touching the schema**

- [ ] Counted how many stored extractions a new required field invalidates.
- [ ] Added a pydantic default if that count is non-zero.
- [ ] Confirmed `strict_schema()` still marks the field required.
- [ ] Added a `verify.py` measurement that would reveal the field never arriving.

---

## File map

| path | what it is |
|---|---|
| `data/ontology/design/c0_verification/ANNOTATION_SESSION.md` | **the per-session annotation instructions — the authority** |
| `data/ontology/design/c0_verification/annotation_queue.tsv` | 26 papers, easiest-first |
| `data/ontology/design/c0_verification/adjudication_log.tsv` | one row per adjudicated field |
| `data/ontology/design/c0_verification/RUNBOOK.md` | how to run an extraction batch and read it |
| `data/ontology/design/c0_verification/BASELINE.md` | the same verification instrument over the legacy corpus |
| `data/ontology/design/c0_verification/probe_sets.json` | region probe vocabulary — **never given to the extractor** |
| `data/ontology/design/PROCESS.md` | how the first ontology dimension was designed, and what went wrong |
| `data/ontology/design/AXES.md` | the live axis design for domains |
| `data/ontology/design/axes*/` | authored TSV node tables (the source of truth) |
| `data/ontology/<dim>/v<N>/` | loadable snapshots |
| `data/mdl/merged/<paper_id>.yaml` | the annotation deliverable |
| `src/paperext/structured_output/mdl/model_v5.py` | the schema, and `SYSTEM_MESSAGE` with every extraction rule |
| `src/paperext/structured_output/mdl/verify.py` | reference-free CHECK / PROBE / MEASURE harness |
| `src/paperext/structured_output/mdl/check.py` | per-record invariants |
| `src/paperext/annotate_pdf.py` | the highlighted-PDF tool |
| `src/paperext/adjudication_report.py` | agreement rate from the log |
| `src/paperext/ontology/` | schema, loader, mutation API, TSV converter, migrations |
| `src/paperext/categorize/` | the placement agent, its retrieval, applier, probes and gate |

## Command reference

```console
uv sync --all-extras
uv run python -m paperext.backend_check --platform <provider>
uv run python -m paperext.query --platform <provider> --concurrency 4 --paperoni <sample.json>
uv run python -m paperext.structured_output.mdl.verify <queries-dir>
uv run python -m paperext.structured_output.mdl.check <queries-dir> --details
uv run python -m paperext.annotate_pdf <paper_id> [--note item.tsv --only-notes --open --out <path>]
uv run python -m paperext.adjudication_report
uv run python -m paperext.ontology.convert_axes --write
uv run categorize            # add --interactive to review every decision
uv run categorize-items
uv run categorize-eval
uv run categorize-report
uv run merge-papers
```
