# What the code won't tell you

For whoever runs the **extraction over the whole corpus** and then **builds the
ontology** from it. You can read the modules; their docstrings carry the design
reasoning and are accurate. So this document deliberately does *not* explain the
code. It carries the other half: what we learned by running it, what we paid to
learn, which numbers mean what, and which clauses in the prompt exist because a
specific paper broke a specific rule.

Read it as a set of warnings and calibrations, not as a procedure.

---

## 0. Orientation: what exists, and what each number rests on

Three corpora are tracked in this repo, and conflating them produces wrong
conclusions fast.

| what | where | size | produced by |
|---|---|---|---|
| **legacy-2024** | `data/mdl/queries/openai/legacy-2024` | **2110** extractions | the old prompt, schema v4-era: no `runs[]`, no `algorithms[]`, a `datasets[]` slot predating the admission rules |
| **v5 batch 1** | `data/mdl/queries/anthropic/claude-opus-5` | 51 files (25 papers + 26 queue papers) | current schema, `tools` mode |
| **v5 batch 2** | `data/mdl/queries/openai/gpt-5.6-sol` | 51 files | current schema, Responses API |
| **reference annotations** | `data/mdl/merged` | 114 YAMLs, of which **4** are v5-era human-adjudicated | 110 are legacy-era merges |

Two facts about that table matter more than the numbers:

**The reference set is four papers.** Not 26. The queue in
`data/ontology/design/c0_verification/annotation_queue.tsv` lists 26 and the
work is ongoing, but four exist today. Everything below that cites the reference
set is citing four papers, and one further paper was adjudicated without its
YAML ever being written (§6). Treat reference-derived F1 numbers as orientation,
never as a gate.

**`legacy-2024` is in this checkout.** `PROCESS.md` tells a story about a name
file that could not be reproduced and an hour lost to archaeology, ending with
the corpus being in a *different checkout*. That is historical — all three
corpora are tracked here now. If you read that section, don't go looking.

### The one architectural guarantee, and why it is the most useful fact here

The extraction schema carries **terms**. Categorisation happens in a **second
pass**. The shared surface between extraction and ontology is **vocabulary, not
hierarchy**.

This came out of an owner ruling, not from the code, and it is what makes the
whole project tractable: **you can revise the ontology without re-extracting
anything.** A 2000-paper extraction is hours of wall clock and real money; an
ontology revision is a TSV edit and a converter run. If you ever find yourself
designing a change that puts hierarchy into the extraction schema, that is the
thing to push back on — there is exactly one ontology value set in the schema
(`access` on a run's data-source mention) and it is there because access is a
property of the *mention*, not of the entity.

The same mention-versus-entity split decides every similar question. `consumed`
('1M environment steps', '10% of the training split') is on the mention because
an interactive environment has no size of its own — two papers stepping the same
simulator would otherwise contend for one entity's `size`. When a new field
arrives, ask which of the two it is a fact about; that question has answered it
every time.

---

## 1. The extraction run over the whole corpus

### 1.1 The model × mode matrix, which cost real money to establish

`config.mdl.ini`'s comments state the conclusions. The sequence behind them:

- **`claude-opus-5` + `mode=tools`** is the combination that works. 25/25 on
  batch 1. Use it unless you have a reason not to.
- **Opus 5.5 and later refuse a forced tool call** — HTTP 400, *'tool_choice:
  type "tool" and "any" are not supported for this model'*. So they need
  `json_schema`.
- **`json_schema` then fails on this schema** with a *compiled grammar is too
  large* error. So all three Anthropic modes are blocked for 5.5: `tools`
  refused, `json_schema` over the grammar ceiling, and `json` (schema in the
  prompt, reply parsed back out) trips instructor's strict JSON decoder on the
  extracted quotes — which contain the punctuation that decoder rejects.
- The empty `data/mdl/queries/anthropic/claude-opus-5-5/` directory in this repo
  is the residue of that attempt. It is not a bucket waiting to be filled.

**Practical consequence: do not assume a newer model is a drop-in upgrade.** The
blocking issue is not capability, it is three unrelated plumbing constraints that
happen to close every door at once. Before a corpus run on any new model, extract
*one* paper and look at the file.

### 1.2 The schema is near a hard ceiling, and every field narrows it

Measured this session: adding one field (`consumed`) grew the strict schema from
**22,791 to 24,361 characters**. The `tools` path does not care. The
`json_schema` path has a grammar-size limit that this schema is already over on
at least one model.

That is the entire argument for splitting extraction into **two calls — entities
first, then runs**. It is designed and not built. If you add fields before
building it, you narrow the margin on the only path some models offer. If the
corpus run is on `opus-5`/`tools`, you are fine today and should still know this
is the constraint that will eventually force the split.

### 1.3 Pace, concurrency, and the limit you cannot see from here

Measured on the 25-paper batch, `anthropic`/`claude-opus-5`: **about 3m20s per
paper**.

| `--concurrency` | 25 papers | 2000 papers |
|---|---|---|
| 1 | ~83 min | ~4.5 days |
| 4 (default) | ~21 min | ~28 hours |
| 8 | ~10 min | ~14 hours |

Those are **ceilings assuming no throttling**, and the real limit is the
provider's rate limit, which is per-organisation and **not knowable from this
repo**. So raise `--concurrency` only after a run has shown headroom. Exceeding
it degrades rather than fails — each paper retries on its own coroutine honouring
`retry-after`, so one throttled paper does not stall the others.

Output tokens, same batch: **averaged 20.5k, peaked 40.4k**. The 48k default
ceiling comes from that measurement, with deliberate headroom; billing is per
actual output token, so raising it costs nothing unless used.

**The run is resumable and says so.** It opens by reporting how many papers are
already extracted versus how many will actually be queried, because the ETA
covers only the second number — counting reused papers as progress would quote
minutes for an hours-long job. At 2000 papers, treat interruption as normal and
re-run the same command.

### 1.4 Four ways a run lies to you

These are the ones that actually happened.

**1. It queries nothing and reports success.** `PAPEREXT_DIR_CACHE` unset →
`Paper._pdfs` globs a cache directory that does not exist → every paper resolves
to `None` → the `is not None` filter empties the list → the run completes having
done nothing. `query.py` now refuses an empty list, but **verify resolution
before spending anything**: the one-liner in `RUNBOOK.md` §1 prints `N/N papers
resolve`. If you see `0/N`, that is this.

**2. It writes to the wrong bucket.** `[platform] select` is `openai`, so
omitting `--platform` silently sends an Anthropic-intended run to the openai
bucket. Worse: **the model half of the bucket path comes from that backend's own
config section, not from the flag** — editing `[anthropic] model` changes the
output directory with it. A corpus run split across two buckets because the model
pin changed mid-flight is tedious to untangle.

**3. A truncation looks like a parse error.** The Anthropic backend inspects
`stop_reason` and raises *"output truncated at max_tokens=…"*. A truncated
Responses-API reply arrives as **partial JSON** and surfaces as a validation
failure with no mention of a ceiling. **If you see unexplained validation
failures on the openai path, check `output_tokens` on the neighbouring papers
before looking anywhere else.** Batch 1's single truncation would have been
misdiagnosed had it happened on that backend.

**4. Stale files look like fresh ones.** Re-running queries only what is missing
or stale. That is what makes a 2000-paper run practical, and it is also how a
corpus ends up with a mix of two prompt versions. If you change the prompt
mid-corpus, the only safe move is a new bucket.

### 1.5 Changing the schema once extractions exist

Twice now a schema change has invalidated stored output:

- `repetitions` changed from a string to a factor list → the **25 batch-1
  extractions stopped validating**. They skip with a warning rather than
  degrading, which is the right behaviour and also means a quiet corpus shrink.
- Adding `consumed` as required → **49 of 51 existing extractions invalidated
  instantly**. Those files are read by downstream sessions, so this would have
  broken work in progress.

The fix for the second was a pydantic `default_factory`, and the reason it costs
nothing is worth knowing: **`strict_schema()` marks every property required
regardless of pydantic defaults**, so the API still demands the field. The
default only rescues already-stored files. Only a backend bypassing strict mode
could omit it — which is what the `consumed coverage` measurement in `verify.py`
exists to reveal.

So, before adding a required field: **count how many stored extractions it
invalidates**, add the default if that count is non-zero, and add a measurement
that would show the field never arriving.

---

## 2. Deciding whether the output is good enough

`verify.py` and `check.py` are reference-free and will tell you what they tell
you. The judgment is in how you read them.

### 2.1 The only valid reading of the baseline comparison

`BASELINE.md` is the same instrument over `legacy-2024`, and it exists because
**a harness whose checks cannot fail is worse than no harness**. 10 of 15
pass/fail checks failed there, and every failure was one the written record had
predicted in advance.

The comparison supports exactly one inference: **a v5 failure that also appears
in the baseline is inherited; one that appears only in v5 is new.** Nothing else.
Legacy-2024 came from a different prompt against a schema with no `runs[]`, so
every run-level measurement there reads 0/0 — and **0/0 is correct behaviour, not
coverage**. Two checks "passed" on the baseline purely because they could not
fail; reading those as a green light would be the classic mistake.

Likewise `executed-without-run` at **2541** on the baseline is expected in bulk:
the v4 converter leaves `runs[]` empty because v4 held no compute configuration
to carry over. Read that code **per-corpus, not per-record**.

### 2.2 The sharpest row in the baseline

12 papers put a simulator *engine* in `data_sources[]` against 9 that correctly
put it in `libraries[]`. **On the legacy prompt the wrong slot was the more
popular one.** That is the admission clause earning its place by measurement
rather than argument, and it is the single best answer to "do we really need all
these rules in the prompt?" — yes, and here is the one that was losing.

### 2.3 What the reference set can and cannot settle

Scored against the first three merged references:

| field | arm A (opus-5) | arm B (gpt-5.6) |
|---|---|---|
| libraries | F1 1.00 | 1.00 |
| models | ~0.96 | ~0.96 |
| research_fields | 0.69 | **1.00** |
| data_sources | 0.87 | **1.00** |
| algorithms | **0.91** | 0.86 |

Shape of the difference: **A over-admits** (higher recall, lower precision — its
extras have included a crowdsourcing platform as a *library*); **B
under-admits**. Neither is uniformly better.

**And then there is `runs[]`, which is the hole.** Across those same three
papers: **89 runs in the reference, 20 from arm A, 26 from arm B.** One paper
alone holds 61 in the reference against 6 and 10 — verified as a genuine
model × dataset cross-product, not duplication.

Two consequences, and the second is the one to carry around:

1. Entity extraction is in decent shape; **run decomposition is wrong by 3–4× in
   both arms**.
2. **Arm-to-arm agreement on `runs[]` is worthless as a quality proxy**, because
   both arms are wrong in the *same direction*. Over all 26 queue papers the arms
   agree on run count for only 5 — but even where they agree, agreement is not
   evidence. Any plan that proposes to validate corpus-wide `runs[]` by comparing
   two models needs to be stopped.

For reference, per-entity agreement over all 26 queue papers: models 79%, data
sources 82%, algorithms 69%, libraries 68%; ~4.9 of 6 fields differ per paper.

### 2.4 The trap this whole exercise can walk into

Quoted because it is the easiest thing here to rationalise away:

> Do not fix a disappointing result by narrowing the prompt's vocabulary. If a
> region comes back empty, the finding is about the prompt's **scope statement**,
> not its vocabulary.

`probe_sets.json` exists to *detect* three under-covered regions. Handing those
sets to the extractor as a closed list would make the ontology revision
circular — it would find only what we listed, and the revision would
rubber-stamp the design it was supposed to test. The temptation arrives
specifically when a probe reads zero and you want a number to show.

### 2.5 The instruments shaped their own numbers once

Batch 1 produced one prompt change, one config change, and **ten fixes to the
plumbing and to the measuring instruments — five of them to the instruments
themselves.** So the numbers those instruments reported had never been read off
data they had not helped shape. That, plus two findings (`mujoco` and a protocol
name, one occurrence each) that cannot become a rate from a single occurrence, is
why a second 25-paper batch on a *different vendor* exists: the instructions had
been written and corrected against one model family, and a second family tests
the instructions rather than the model.

**Keep this instinct.** When you change a check and the number improves, the
number is no longer independent evidence until it has been read on data the
change did not touch.

---

## 3. The prompt's rules: what each one cost, and which are unsettled

`SYSTEM_MESSAGE` in `model_v5.py` reads oddly in places. Every oddity is a paper
that broke something. If you edit the prompt, know what you are deleting.

### 3.1 Settled, each by a specific case

- **A run is a unit of compute the paper spent** — same run unless execution
  mode, precision, parallelism, accelerator count/type, scale, or amount of data
  processed differs. 5 seeds × 20 learning rates is **one** run with two
  `repetitions` factors. Experiments that process the same data but are not
  crossed (a sweep over sampling steps, then one over variants) stay one run with
  their counts summed.
- **A fitting run is one coupled optimisation loop.** A GAN is one run.
  Actor+critic, encoder+decoder: one run. A **frozen** network supplying targets
  or scores is a *participant* with a non-`main` role.
- **Only models this paper executed get a run** — quoted leaderboard numbers get
  `is_executed=false` and no run. **But execution carries forward across related
  tables**: where an earlier table states the models were trained and a later
  related table is silent, infer trained. A stated attribution elsewhere still
  wins; this fills silence only. (Settled on a paper where Table 1's baselines
  were stated as trained and Table 4's same-model rows were not.)
- **A Data Source is a source of examples a run consumes** — by name when it has
  one, **by the paper's description when it does not**. A described source beats
  no source, because a run pointing at nothing loses the data it consumed.
  Excluded: the vendor or website the examples were licensed from, the software
  implementing the source, and an **evaluation protocol** over a source.
- **A subset is the same source** unless it is a standard artifact named and
  reused *beyond this paper*. The test is whether others use that name — not
  whether this paper coined one. This resolved a priority conflict that had been
  recorded as open between two parts of the data-source design.
- **`repetitions` is a list of factors**; an empty list means the paper does not
  say, **never a count of 1**. Never record how many examples the run processed —
  that is workload, and it belongs in `consumed`.
- **A research field the paper only mentions is not a field of the paper.** The
  case: an arm reported a field on the strength of one related-work sentence
  about a system that appeared nowhere else in its own extraction. The check is
  mechanical — for every `referenced` field, name the reported entity that
  carries it.
- **A size-suffixed checkpoint name is a stated parameter count.** The
  not-from-a-name rule targets *generic* names with many sizes.
- **Never infer** a compute field the paper does not state — `utilisation`
  especially. **But never-infer binds the extractor, not a human annotator.** The
  rule exists because a single-shot model with no lookup hallucinates when filling
  a gap from memory; someone who can check may use verified outside knowledge.
  That distinction is easy to over-apply in both directions.
- **An alias names the SAME thing.** A concept that deserves its own node is
  never an alias. The case: `sparsity research`, `pruning`, `sparse training` and
  `sparse neural networks` are an activity, two procedures and a property — four
  nodes, not four spellings.

### 3.2 One rule was reversed inside a single session

**Names stay as the paper writes them, abbreviation included** — do not expand an
acronym the paper leaves bare. This *reversed* an expanded-name rule made earlier
the same session, on the grounds that renaming creates more confusion than it
resolves.

Worth knowing for two reasons. First, so you don't reinstate it. Second as
calibration: a rule that looks obviously right at the moment it is written can be
wrong, and the fix is to reverse it in place with the reason, not to leave both
versions standing.

### 3.3 The acronym question, and the loose end it left

It was proposed that names be expanded for the categoriser's benefit. Rejected,
for reasons that still hold:

- `iql` is an acceptance test precisely *because* it is both Implicit and
  Independent Q-Learning — expanding it requires guessing;
- many "acronyms" have **no** expansion (`GSM8K`, `TD3`);
- expansion pressures `unresolved-reference`, which is currently **0 across all
  batches** — runs reference entities by verbatim name, so renaming at extraction
  time breaks that join;
- **normalisation is the layer designed for this**, and it is the only layer with
  corpus-wide information. `items.py` already hands the categoriser the quote,
  justification, aliases, `is_executed` and co-occurring entities.

Measured rate of acronym-only names with no expansion anywhere in the
extraction: **data_sources 19%, models 16%, libraries 10%, algorithms 3%.**

**The loose end:** the "EXACTLY as the paper writes it" instruction sits on the
*algorithms* entity only — which is the slot with the *lowest* acronym rate. The
clause recommended instead and **never implemented** was *"never drop the
expansion the paper gave you"*, on models / data_sources / libraries. If you want
one prompt improvement with a measured motivation behind it, that is the one.

### 3.4 Deliberately deferred, so do not resolve them silently

- **The unnamed-description boundary.** Two overrides on one paper both landed on
  data sources described but not named, and the outcome **conflicts with the
  unnamed-description exclusion as written**. The log flags it; the owner chose
  to look at it separately rather than hold up the queue. The rule text now says
  a described source is admitted *when a run consumes it and no named source
  covers the same examples* — that is the reconciliation, and it has not been
  tested against the exclusion's original cases.
- **`derived_from` has no parent to name** when the parent is unnamed (a
  proprietary simulator). Recorded, unresolved.
- **`Explained[list[...]]` has never been exercised by a live API call.** It
  produces a valid closed strict schema when checked locally, but schema *shape*
  has broken at the API before, on a class name. A corpus run will settle it one
  way or the other in the first few papers — look.
- **Half of one invariant is unmechanised**: the ontology-role side of the
  `execution_mode` check (no fitting-role algorithm inside an inference run) is
  not in `check.py`. Mechanisable now; writing it blind would be guessing at the
  shape of the failure.

---

## 4. From corpus names to the ontology

### 4.1 You do not need the fulltexts for this half

`items.py` folds mentions into one decidable item per distinct name, and
**grounding is extraction-records-only**: the quote, justification, aliases,
`is_executed` and co-occurring entities from the stored query JSONs. No paper
text is read.

That is a large practical fact. The ontology pass runs off git-tracked data, with
no cache, no PDFs, no paperoni token, and no download step. If a plan for the
ontology work includes fetching fulltexts, it is solving a problem that does not
exist.

### 4.2 The order that worked, and why step 0 is not skippable

`PROCESS.md` is the process record and is worth reading in full. The part that
earns its keep:

**Step 0 — measure before deciding anything.** Node counts, compound names,
`Other` rate at the cut, depth, branching. On the legacy trees this produced the
single most useful early finding: **the cut file, not the tree, caused most of the
`Other` rate** — one tree named 4 of 63 available categories, the other 8 of 25.
Without measuring, a one-file problem would have been "fixed" by rebuilding a
whole tree.

Then: several independent agents on an identical brief with no sight of the legacy
tree (to see what *replicates* — and the **arguments** matter more than the
structures); design the **levels, not the nodes**; iterate with the owner on
principles one axis at a time; derive nodes per axis from the schema rather than
from the corpus; validate three ways.

**For a new dimension, decide the entity types first.** That lesson arrived late
for domains and should arrive first: a level-1 question largely dissolves once
typing is settled. The case that produced it — asking whether "other algorithms"
belonged in the models hierarchy — turned out to be a **type confusion**, not a
junk-drawer problem: a run is a relation over several typed entities, so the
models dimension is at least two entity types.

The related framing, also from an owner challenge: **domains = what the paper is
about; models = what it cost to run.** That reframed an entire issue.

### 4.3 The three rules that keep getting violated

All eight rules in `PROCESS.md` §2 exist for a reason. These three are the ones
that were violated *after* being written down:

**The corpus bounds scope and exposes blind spots; it does not arbitrate.** The
first brief said "if you cannot find three examples, the category is not real".
That deletes legitimate areas a one-year single-institute snapshot happens not to
contain, and rewards fitting this corpus over describing the field — it would have
deleted every regulator-facing property on one axis. A category with no corpus
support is *possibly speculative — justify or keep*; a corpus cluster with no
category is a *blind spot*. **Neither auto-deletes.**

**Never balance categories by paper count** — including through the back door. The
granularity audit caught an 84-mention topic sitting as a top-level branch while a
43-mention peer of the same kind was not. That is balancing by count wearing a
different hat, and it reshaped the whole axis.

**Volume decides which node to open next; it plays no part in how it opens.** The
ordering is what makes compliance checkable: draft the sibling set from the
field's own structure **with no corpus access** → freeze it → *then* consult the
corpus, for two questions only (blind spot to add, speculative node to flag) →
deliver both versions with every change and its reason. Across four expansions,
**no corpus check changed any structure**, verifiable from file timestamps.

**And a protocol hole we wrote ourselves:** the corpus-free phase was undermined
because the brief told agents to read `nodes.tsv` for the parents' characteristics
— and that file carries `examples`, `corpus_names` and `corpus_mentions` in
adjacent columns. Two agents independently *reported* the contamination rather
than benefiting from it. **Fix before deriving anything: publish a count-free
characteristics file and point the corpus-free phase at that.**

### 4.4 Retrieval, not judgment, is the bottleneck

Measured on the 1208 unmapped model names of the legacy corpus against the legacy
tree: **`Ontology.search` alone returns nothing at all for 96.4% of them.** It
matches `query ⊆ node key`, so `resnet50` finds no `resnet` and
`mobilenetv3large` finds no `mobilenet`.

Whatever you ask the agent, it cannot place a name whose neighbourhood it never
sees. So when placement quality disappoints, **look at the candidate sets before
touching the prompt.** This is the single highest-leverage thing in the
categorisation half, and it is counter-intuitive enough that it was nearly missed.

### 4.5 Why there is no accuracy number, and what to use instead

The classes nest (`transformer` contains `vision transformer`) and are heavily
skewed (45% `Other` at the legacy cut). So an accuracy figure mostly measures the
prior, and it scores "one level up" exactly like "the wrong branch". Three
families survive that: **hierarchy-aware per-item agreement**, **distributional
shape**, and a **blind pairwise win rate** with an analytic 0.5 ceiling.

The win rate is only meaningful under constraints that are easy to erode:

- The judge sees paper evidence and two **anonymised** ancestor paths in
  randomised order — no node ids, no version labels, no "reference"/"agent"
  wording anywhere in the rendered text.
- Order-blindness is **structural**, not promised: swapping a pair renders as the
  original with the blocks exchanged.
- The judge **must be a different vendor** from the categorisation model. A
  same-family judge preferring its own output biases the number in the one
  direction that matters. `config.mdl.ini` pins them to different vendors and the
  comment says why.

The eval is **leave-one-out and non-accumulating**: each item is decided against
its own single-item-ablated tree. Ablating all items at once would gut the sibling
context every placement depends on and correlate the errors, which makes the
confidence interval a decoration. The price is a per-item prompt prefix, so the
gate does not benefit from caching the way an accumulating run will — budget for
that.

Alongside it, the probe sets have **known-correct answers that do not come from
the legacy tree**, so they do not inherit its subjectivity. The one to keep: a
**no-op control** of already-mapped, *un-ablated* names, which catches an agent
that churns the tree for the sake of answering.

### 4.6 What the validation instruments actually caught

Not theory — each of these found something no other instrument did.

- **Tail validation.** A stratified sample (50 names from the ≥3-paper band, 100
  singletons) placed using **only the written tests**. The output is not
  placements but a **strain list**: where a rule was ambiguous or missing. **9
  findings from 150 names**, two of them blocking gaps. *This measures the schema,
  not the corpus — a name that cannot be placed is a schema defect.*
- **Granularity audit.** Per sibling set: same kind of thing? same specificity?
  **does any sibling exist only because it was large in this corpus?** Caught the
  defect that reshaped an entire axis.
- **External diff.** Found three blind spots that **two independent external
  sources agreed on**, none findable from the corpus. And established the limit of
  external schemes: a widely used one fails our own granularity audit, and a broad
  category read literally swallows the entire corpus. **Vocabulary and breadth,
  never arbitration.**
- **Agents auditing their own output.** Every derivation brief required the agent
  to run the granularity audit on itself and **declare the sibling sets it was not
  confident in**. This was consistently the highest-value section of their
  reports — one declared that two of its own nodes existed partly because they
  were large in this corpus, which is exactly the defect being hunted. **Keep this
  requirement in any brief you write.**

### 4.7 What is open on the ontology side

- The **ontology revision pass** carries ~11 data-source items, at least one
  genuine coverage gap (a method family with no node), and a **duplicate node
  pair** differing only in how the name is spelled out. Revision is against the
  extraction, which is why it waits on a corpus run that is known-good — an
  extraction that failed for a *prompt* reason would send the revision chasing a
  defect that is not in the ontology.
- Expect models to be **about twice as tail-heavy as domains**: 2342 names, 51%
  of mentions are singletons, against 25% for domains. Head-only description does
  not scale; attributes attach to families and the hierarchy does tail-collapse.
- A planned empirical comparison — the models hierarchy against the method axis's
  model-design branch — to settle whether a separate models hierarchy earns its
  keep or duplicates work. **Do not decide that in advance.**
- **Adding a field to `Node` changes the content hash.** Plan the migration;
  don't be surprised by a snapshot that stops matching.

---

## 5. Time sinks, so you don't repeat them

Each of these cost real time in these sessions.

**Quoting a per-branch count computed over the head of the distribution.** This
happened repeatedly and was wrong every time: one axis was estimated at ~93
mentions and **measured at 389**; another axis's per-branch figures undercounted
by **2.5×**; a "1-mention blind spot" was ~34 once an unmade routing decision was
made. One of those nearly argued the owner out of an axis they had correctly
proposed. **Never quote a per-branch size without computing it over the whole
vocabulary, and label every count in a design document as indicative.**

**Fixing from source instead of from a failing case.** One rule was diagnosed by
reading the scorer and writing a policy clause. It changed nothing, cost a run,
and the first look at an actual failing record showed the agent had been right all
along. **Look at one failing example before writing any fix.**

**A correct decision with a false rationale.** A clause was dropped with a note
saying it "fired on noise". It did not — it fired on papers splitting across
duplicate nodes. The decision held; the reason was wrong, and a wrong reason is a
trap for whoever reads it next. **Correct the rationale in place.**

**Claiming a field is available because it is in the schema.** Two fields were
described as "already recorded per mention" when they existed only in a schema
version **no corpus had ever been extracted with**. **Check the data, not the
schema.**

**False positives in your own harness.** Four, all from **matching more surface
than the rule covers**, and two produced **false FAILs on acceptance tests**: a
literal `['unknown']` counted as a stated value; `str(enum)` yielding
`ClassName.MEMBER` instead of the value; normalised names having no separators
left to tokenise; a generic *alias* making a properly named source look unnamed.
**Before reporting that a check failed, read one failing record end to end.**

**Tooling.** `uv sync --extra <one>` **replaces** the environment and drops the
provider SDKs — always `--all-extras`. And run the suite green *before*
committing, not after; that was violated twice.

---

## 6. If you touch the reference set

You are not building it, but you inherit it as the only ground truth, so two
things matter.

**One adjudicated paper has no YAML.** `adjudication_log.tsv` carries 14 scored
decisions for queue paper 5, and the four rules that session settled are committed
— but `data/mdl/merged/` holds only 4 of the 5. The artifact the session existed
to produce was never written. Either reconstruct it from the log rows or
re-adjudicate; don't let it be counted as done.

**The agreement rate rests on 27 decisions, not 88.** `adjudication_report` says
**81%**, with **61 UNSCORED** — the first three papers predate the `recommended`
column. The report deliberately refuses to count a missing `recommended` as
agreement, and that refusal is the point: a recommendation recorded *after* the
answer is known is not a prediction. If you add rows, fill `recommended` **when
you ask**, with `chosen=pending`, and fill it **even when it matches** — a column
that records only disagreements cannot measure agreement.

Why anyone cares: the agreement rate is the only direct evidence of **which
fields a model is unreliable on**, which decides how much of any future
evaluation can rest on model-to-model agreement rather than on ground truth. The
current reading is that the assistant is reliable *where a rule exists* and
unreliable *where it must invent one* — so automation is bounded by rule coverage,
not by model quality.

---

## 7. Short pointers

Authoritative files, in the order they repay reading:

| file | why |
|---|---|
| `src/paperext/structured_output/mdl/model_v5.py` | the schema and, in `SYSTEM_MESSAGE`, every extraction rule at length |
| `data/ontology/design/c0_verification/RUNBOOK.md` | how to run a batch and read it; the cache trap in full |
| `data/ontology/design/c0_verification/BASELINE.md` | the before-picture, and the limits of the comparison |
| `data/ontology/design/PROCESS.md` | how a dimension was designed; the failures are the useful half |
| `data/ontology/design/AXES.md` | the live axis design, with per-axis rulings |
| `data/ontology/design/c0_verification/ANNOTATION_SESSION.md` | every settled annotation rule with the case that settled it |
| `src/paperext/categorize/*.py` docstrings | the design reasoning for the placement agent |

Before a corpus run:

- [ ] `uv sync --all-extras`; suite green.
- [ ] `backend_check` on the platform you will use.
- [ ] `N/N papers resolve` printed, with `PAPEREXT_DIR_CACHE` set.
- [ ] `--platform` explicit; model pin not about to change mid-run.
- [ ] One paper extracted and **read** before the other 1999.
- [ ] A new bucket if the prompt changed.

After it:

- [ ] `verify.py`, read against the baseline with the inherited-vs-new rule.
- [ ] `check.py` codes read per-corpus.
- [ ] `output_tokens` distribution checked for anything near the ceiling.
- [ ] Nothing fixed by narrowing the prompt's vocabulary.
