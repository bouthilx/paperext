# Data sources — phase-1 synthesis

#102 step 3. Three independent derivations, **frozen 2026-10-07 before any
corpus file was opened**, per `METHOD.md`. Entry points: **A** ML practice ·
**B** the compute-estimation requirement · **C** first principles about
information sources. None could see the others, the corpus, the legacy tree, or
the candidate value sets drafted in #102 Part B.

The comparison rules were fixed in `METHOD.md` before these were read: agreement
across entry points is the evidence, divergence is recorded rather than voted
on, and alignment is by **characteristic**, never by name.

---

## 1. `access` — unanimous on five values

The three runs used different names for the same cuts:

| characteristic | A | B | C |
|---|---|---|---|
| the set exists before the run; the run controls only order and subsetting | `fixed_sample` | `fixed` | `fixed` |
| a procedure mints examples on request, not conditioned on the run's outputs | `generator` | `generated` | `generator` |
| the run names what it wants; the responder carries no state across requests | `queried_store` | `queried` | `oracle` |
| the source holds state; the next example depends on the run's actions | `environment` | `interactive` | `interactive` |
| the source pushes on its own clock; missed examples do not come back | `stream` | `stream` | `stream` |

**Five values, three of three, from three different starting points.** This is
the strongest result the method can produce — and it *corrects #102 Part B*,
which had three values: all three runs independently split `oracle` and `stream`
out of what Part B had lumped together.

### `federated` — resolved by unanimous doubt

All three reached the case (examples that never arrive at the run: FeTS, UK
Biobank's analysis platform, census enclaves) and **all three declined to make it
an `access` value**, for the same reason: its differentia is locality or
governance, not control over the next example, so putting it here would make the
axis two characteristics.

- A rejected it outright and recommends a separate governance axis.
- B gave it a value and called it *"the value I would drop first"*.
- C folded it into `oracle`, called that *"a stretch"*, and recommends a
  `locality` axis.

Three handlings, one shared diagnosis. **Not an `access` value.**

### Ontological miss vs information gap

A and B independently insisted these be different things: a value for *the scheme
has no slot for this*, and a separate marker for *the paper does not say*. A:
collapsing them "destroys the only signal that tells you whether the ontology is
wrong or the literature is silent." B: it "would destroy the one statistic worth
having here — how often the field states it at all."

Adopted. `*-other` is an axis value; `unknown` is a **coding state**, not a node.

---

## 2. `provenance` — unanimous on six values

| characteristic | A | B | C |
|---|---|---|---|
| a physical or biological process, measured by an instrument | `measured` | `natural` | `natural` |
| a human artifact made for its author's own purposes, collected later | `human_artifact` | `human` | `human_incidental` |
| human effort that exists *because the collection asked* | `human_elicited` | `elicited` | `elicited` |
| a mechanistic model of a real referent, executed | `simulated` | `simulated` | `simulated` |
| a formal construction with no empirical referent | `formal` | `constructed` | `constructed` |
| the output of a trained model | `model_generated` | `model` | `model_generated` |

**Six values, three of three.**

### Divergences, recorded rather than resolved

**Byproduct-of-operation records** (EHR, click logs, cluster traces, registries).
A splits this into **three** values (`interaction_log`, `system_telemetry`,
`institutional_record`); B has **one** (`operational`); C has **none**, folding
them into `human_incidental`. Two of three say the characteristic is there and
they disagree 3-vs-1 on granularity — while both carriers volunteer low
confidence: A, *"if a reviewer wanted to collapse all three into one
`operational_byproduct` value I could not mount a strong objection"*; B, *"the
provenance value I am least sure deserves to exist"*.

Resolution: **one value, flagged, pending corpus evidence.** Phase 2 can measure
whether the corpus distinguishes a cluster trace from a click log. Phase 1 cannot.

**`rule` — a non-learned verifier or engine produced the signal** (unit-test
pass/fail, Lean proof checking, game outcomes, labelling functions, distant
supervision). **Only B.** A and C both route game outcomes to
`formal`/`constructed`, but B's other examples resist that: a unit test checks
real code, so "formal construction with no empirical referent" is false of it.
The characteristic survives its own tests, so per `METHOD.md` it is **kept and
flagged speculative** rather than dropped — rarity is not the test, coherence is.

**`rendered` — computed from human-authored assets by a graphics pipeline.**
**Only A**, which holds it *"with low confidence"* and offers the alternative:
collapse `simulated`/`rendered`/`formal` into one `program_computed` value plus a
separate `referent` axis. Folded into `simulated`; the question is recorded, not
settled.

### `derived` is a relation, not a value — three of three

A *"deliberately refused a `derived` value and used inheritance instead."* C
proposed one and marked it **contested, recommending demotion to a relation.** B
never proposed one.

A and C independently stated the **same inheritance rule**: *a derived source
carries its parents' provenance values, plus any value the transformation itself
introduces.* That is the `derived_from` decision already shipped in v5 (PR #106),
semantics included, confirmed by two runs that could not see it.

One soft spot both found: when the transformation is a **model-based filter**
(FineWeb-Edu, DataComp, CLIP-filtered LAION) it injects no content but does set
the distribution. A recorded `model_generated` there and said *"I am not
confident that is right — selection is not generation."* Open.

---

## 3. Tensions by convergence — worth more than the axes

### 3/3 — `access` is a property of a *use*, not of a source name

All three, independently, with the same example class: an environment and a frozen
log drawn from it. **All three named MineRL**, which ships an interactive
environment and a human-demonstration corpus under one name; A and C both named
Habitat/HM3D; A and B both named the ALE-versus-replay-dump pair.

All three draw the same consequence: **any statistic over this axis is partly a
statistic over naming practice.** All three also reject making `access`
multi-valued — a source carrying `{fixed, interactive}` makes the example count
unrecoverable, defeating the axis's purpose.

A adds the within-run case: an offline-to-online RL paper pretrains on a fixed log
and finetunes in the environment, so *"coding one value per source hides half the
compute."*

**A structural question about where axis values attach. Not ours to settle** — §4.

### 3/3 — the admission rule's model-as-source exclusion hides the expensive case

All three object, and all three identify the same inversion: a **released dump**
of teacher outputs (Alpaca, Cosmopedia) is admissible with
`provenance = model_generated`, while the **live teacher** that produced it is
excluded — and the live case is the one that costs. Instances named across the
three: online distillation from a served API, RLAIF and Constitutional-AI
labelling, rejection-sampling/STaR loops, reward-model scoring in RLHF,
LLM-as-judge evaluation, LLM-simulated users, self-play, and learned world models
(Dreamer, Genie, GAIA-1), which are interactive sources by every test the runs
wrote.

B: *"its compute can exceed the training compute the survey is trying to
measure… the most consequential tension in the draft, and it is in the part I was
told not to revise."* C: *"the sharpest awkwardness the definition produces, and
it will get worse."* A: *"defensible for ontological hygiene and harmful for the
survey's purpose."*

A extends it to **intra-run data** generally — replay buffers, self-generated
rollouts, synthetic curricula, augmentation pipelines — unnamed and therefore
invisible, *"exactly where the compute goes in RL and in post-training."*

### 3/3 — `provenance` cannot say *which part* of the signal it applies to

All three give ImageNet (incidental photographs + elicited labels); also named:
OC20 (`formal` geometries + `simulated` labels), FineWeb-Edu, CheXpert, SNLI,
MS MARCO, Noisy Student. A calls it *"the single largest expressivity loss I
found."*

Two also note the axis has nothing to say about **self-supervised** sources, where
the target *is* the input and there is no second origin to record.

All three propose the same fix shape: scope provenance to a channel —
input / target / (reward) — rather than to the source. A and C both note the cost
is roughly doubling the annotation.

### 3/3 — availability is a missing axis, and `access` will be mis-coded as it

All three predict the same error: a coder reads "access" as *openness* and puts
`gated`/`proprietary` on it. All three name MIMIC or UK Biobank as `fixed` **and**
gated. All three recommend a separate axis; two recommend **renaming `access`**
(`acquisition`, `delivery`, `supply protocol`) so the collision cannot happen.

### 3/3 — `stream` is probably near-empty in the corpus

All three note that live feeds get frozen and **the snapshot is what gets the
name**. All three kept the value anyway, with the same argument: recoding a
genuinely non-replayable source as `fixed` asserts a reproducibility it does not
have. Phase 2 should expect few or none and **must not read that as the value
being wrong** — the absence-is-not-evidence rule, exactly.

### 2/3 — RL reward provenance is invisible

A and C. A: a programmatic reward, a human preference signal and a learned reward
model *"are three completely different research programs and three different
compute profiles, but all three appear as `environment`"* with provenance
dominated by whatever produced the observations. The channel problem again, with
worse consequences.

### 2/3 — boundedness of supply wants its own axis

A recommends `supply` {fixed-finite / unbounded / growing} explicitly, noting
Procgen is `environment` *and* unbounded with nothing to record it. B reaches it
from the other side: for `generated` the count is a budget, not a property of the
source. For compute sizing the difference is *a storage line versus a cluster
line*.

### 2/3 — `oracle` is the value most likely to be deleted

A and C, same objection: its real differentia is **possession and
enumerability**, not control over the next example — so it is arguably `fixed`
plus an attribute. Both kept it for the same reason: rate limits, latency and
non-reproducibility across runs are real and nothing else records them.

A also flags that `oracle` may be **structurally unpopulatable**: oracles are
*described* ("we asked three radiologists") rather than *named*, and the admission
rule excludes unnamed sources — so *"the exclusion of unnamed descriptions
silently deletes most of one access value."*

### 1/3 but sharp — granularity may belong per axis, not per dimension

A, on suites (GLUE, BIG-bench, D4RL, ALE's 57 games, Meta-World's 50 tasks):
`access` is stable within a suite while `provenance` is not. If a suite gets one
row its provenance is a meaningless union; if every member gets a row the coding
cost explodes and a paper citing only the suite cannot be coded. **"Granularity
should be decided per axis, not per dimension"** is a design idea nothing else in
this project has.

### 1/3 each, recorded

- **A:** retrieval corpora and agent tools (a RAG index, a search engine, a code
  interpreter) stretch *"the examples a run consumes"* — admit them and the
  dimension is also a tool inventory; exclude them and a growing share of
  inference compute is unaccounted for. v5's `roles_in_run = reference` partially
  covers this; A could not know.
- **A:** the "named" threshold biases the survey **toward public-benchmark compute
  and away from private collection and simulation** — which for an institute may
  be the larger number.
- **A:** pretrained weights import more compute than any dataset in a paper and
  are not a data source. Models' business; flagged so a reader of this dimension
  alone does not draw wrong conclusions.
- **C:** a `collection channel` axis (scraped / instrumented / solicited /
  donated / purchased / administrative) *"should be derived next, before anyone is
  tempted to smuggle it into provenance."* **B's `operational` value is arguably
  that exact smuggling** — C predicted B's weakest value without seeing it.
- **C:** temporal stability — `fixed` reads as "frozen forever" but the test only
  says "predetermined independently of the consumer", so a Wikipedia dump, a
  rolling crawl and a decaying tweet-ID set are all `fixed` and behave
  differently.
- **B:** promote the measurement column to a field — an `estimability` marker
  (stated / chosen / derived / undefined) derived from `access`, so a mention that
  cannot support `6ND` is flagged rather than silently mis-estimated.

---

## 4. What needs an owner decision

Both are objections to rules the owner set, raised independently by all three
runs. Neither is ours to overturn.

1. **Does a model used live as a data source get admitted?** The exclusion is
   ontologically clean and, per 3/3, hides the expensive case. Options the runs
   offered: admit a model-as-source entity; keep the exclusion and add a role
   marker on the *models* side meaning "this model produced the data for this
   run"; or accept the gap and document that the survey under-counts RL and
   post-training compute.
2. **Do axis values attach to the source, or to the (source, run) mention?** 3/3
   say `access` is relational. v5 already has a mention-level place for it —
   `runs[].data_sources[]` — so the schema can express it; the question is whether
   the ontology should.

## 5. Frozen now

- **`access`**: `fixed` · `generator` · `oracle` · `interactive` · `stream`,
  plus `access-other`. **Not** `federated`.
- **`provenance`**: `natural` · `human-incidental` · `elicited` · `simulated` ·
  `constructed` · `model-generated`, plus `operational` (flagged) and `rule`
  (flagged speculative), plus `provenance-other`.
- `unknown` is a coding state on both axes, not a node.
- `derived_from` stays a relation with the inheritance rule, as shipped.

Candidate further axes, all converged on, all **out of scope for #102**:
availability/governance (3/3), supply/boundedness (2/3), locality (2/3),
collection channel (1/3), temporal stability (1/3).

**Phase 2 may now open the corpus**, for blind spots only.
