# Run D2 — the `referent` axis and the consequent mechanism value set

## What I read

Exactly these files, in this order:

1. `data/ontology/design/axes_data_sources/REFERENT_BRIEF.md`
2. `data/ontology/design/axes_data_sources/METHOD.md`
3. `data/ontology/design/axes_data_sources/access/nodes.tsv`
4. `data/ontology/design/axes_data_sources/provenance/nodes.tsv`
5. `data/ontology/design/axes_data_sources/SYNTHESIS.md`, lines 1–341 — i.e.
   sections 1 to 5 and the `## 6.` heading line only. I did not read §6's body.

Plus a directory listing of `axes_data_sources/` (which shows the filenames of
the forbidden files, nothing of their content) and of `access/`, `provenance/`.

I did not open `placements/`, `placement_candidates.tsv`,
`operational_sweep.tsv`, `data_source_names.tsv`, `datasets/v0`,
`SYNTHESIS.md` §6, anything under `paperext-llm-backend/`, or any other file in
`derivations_referent/`. Every data-source name in this report is one I know
from the field, not one I read here, except where I explicitly quote the
`examples` or `notes` column of `provenance/nodes.tsv`, which the brief permits.

---

## 0. Where I disagree with the brief, before deriving

The brief is right that `provenance` asks two questions. I think it
under-counts, and one of its two framings is slightly off.

**(i) "What the signal is a record of" is the wrong frame for the second
question.** "Record of" presupposes a trace: something happened and the signal
retains it. That works for measurements and for human artifacts and breaks for
every computed source, which is where the axis is needed. A DFT energy in OC20
is not a record of anything — no molecule was ever in that configuration. Yet it
is emphatically about something: it answers to quantum mechanics, and DFT's
error against experiment or against CCSD(T) is published. So the second question
is not *what did this signal come from* (that is the mechanism question again)
but **what does it answer to** — where the standard of correctness lives. I
derive the axis on that principle and keep the owner's name `referent` for the
axis id, noting that `answers_to` would be the accurate name.

**(ii) The split is three-way, not two-way.** Factoring mechanism out of
referent leaves a third question still inside `provenance`: **did the producer
originate the content, or did it assign a value to content that came from
somewhere else?** A unit test does not write the code it labels. An annotator
does not take the photograph she labels. A DFT relaxation does not choose the
geometry it scores. That question is what `rule` is actually made of (§3), and
it is the channel problem wearing a mechanism's clothes. So the brief's
"one mechanism value plus a `referent` axis" is a genuine improvement that does
**not** finish the factoring, and (b) cannot be fully answered inside (b).

**(iii) The brief names `natural` vs `human-incidental` as the second collapse
candidate. I think it picked the wrong pair.** Under a strict mechanism reading
`natural` vs `human-incidental` *survives* — instrument-transduction versus
human authorship is a difference in producer — once `natural`'s test stops
mentioning the subject. The pair that does not survive is
`human-incidental` vs `elicited`, which share a producer (a person) and differ
only in **why the content exists**. See §4.

---

## (a) The `referent` axis

### Principle of division — one sentence

**By what kind of check the source's values could be shown wrong: none at all,
a computation or proof, or an observation of the system the values are about.**

That is a statement about what the values answer to, which is why the axis is
called `referent`; it is phrased as a check because a check is the only
operational handle a coder has on aboutness.

### Two rules the values depend on

**Rule R1 — the machinery is a channel, not a referent.** The referent is what
the source's values are *offered as evidence about*, not what its production
machinery happens to obey. A rigid-body solver obeys Newtonian mechanics
whatever scenario it runs; that does not make a stipulated humanoid gait a study
of animals. This is the exact parallel of `natural`'s existing clause, *"the
instrument is a channel, not an origin"*, and it is what makes a MuJoCo
locomotion task and a sim2real model of a specific Franka arm — identical
engine, identical mechanism — land on different values.

**Rule R2 — the axis is single-valued and scoped, by fiat, to the target
channel.** Where a source ships a ground-truth signal, the referent is that
signal's. Where it ships none (an unlabeled corpus, an environment's
observations), it is the referent of the signal it does ship. I considered
making the axis multi-valued and rejected it with the same argument the three
phase-1 runs used against a multi-valued `access`: a source coded
`{empirical, stipulated}` tells a reader nothing, and the one statistic this
axis exists to produce — how much of this work is on constructed objects — is
destroyed by it. The cost of R2 is real and is recorded in §5: SWE-bench's real
repositories and its test-derived rewards have different referents and only one
is coded.

### Scope and cardinality, stated explicitly

- **Single-valued**, per R2. No `mixed` value (the precedent in `METHOD.md` §4
  rules it out, and the reasons transfer unchanged).
- **It applies to every source. No scope predicate.** Restricting it to computed
  sources would make the axis undefined exactly where its complement carries
  information: you cannot ask "what fraction of this institute's sources are
  about the world" if measurements have no value on the axis. It would also
  re-entangle the two questions the change exists to separate.
- **A consequence worth stating: the axis is free of mechanism but not
  independent of it.** `measured` entails `empirical` — an instrument can only
  transduce something that exists. I looked for a counterexample (a dataset of
  hardware-TRNG output: still a physical device; profiling traces of a simulator:
  still a real running machine) and found none. No other mechanism value fixes
  the referent: an annotator asked whether a string is in Dyck-*k* is `authored`
  and `stipulated`. So the coding effort on this axis belongs on computed and
  authored sources, and `measured` sources can be defaulted. Non-independence of
  two axes is not conflation; it is a prediction about where annotation pays.
- **Coding state for "the paper does not say": `unknown`, a coding state and not
  a node**, as on both shipped axes. Referent is assigned post-hoc from the name
  and the quote, like `provenance`, so `unknown` should be rare — and the case
  where it will not be rare is not silence but §5.3: an **engine named as the
  source** has no referent as an entity. That deserves its own marker
  (`use-determined`) rather than `unknown`, because conflating them destroys
  exactly the statistic the `unknown`-vs-`*-other` convention was invented to
  protect.

### Values

#### `empirical` — answers to an observable system

- **characteristic**: the values are offered as evidence about a physical,
  biological or social system that exists independently of the source, so they
  could be wrong and the arbiter is an observation of that system.
- **positive_test**: name the observation that would settle a disagreement with
  the source. If the referent were directly available, the source would be
  replaceable by it, and a discrepancy would be reported as the source's error.
- **negative_test**: fails if no measurement of anything could adjudicate the
  values — if the only recourse is re-running the generator, re-deriving the
  formula, or re-reading the specification.
- **examples**: SDSS/LSST imaging; fastMRI; MIMIC; Common Crawl and The Stack
  (a record of what people actually wrote); a photographic street-sign corpus;
  LAION; HH-RLHF preferences (a real fact about those raters, settled by asking
  more of them); CMIP6 runs; OC20/ANI-1x DFT energies; a regulated
  physiological simulator; GTA5/SYNTHIA driving renders (the domain gap *is* the
  error claim); Habitat/HM3D (those buildings exist); a differentially private
  synthetic census (no row is about a person, the marginals are about a real
  population).
- **notes**: deliberately indifferent to whether the referent is natural or
  man-made. That indifference is the point: it is what stops the subject
  question from re-entering the mechanism axis, and it is the direct fix for the
  brief's complaint that a `natural` defined by "remove every human purpose and
  the process still runs" expels its own photographic exemplars. My doubt: the
  value absorbs a great deal, and the social reading ("about human behaviour,
  checkable by sampling more of it") is elastic enough that a determined coder
  could route almost any human artifact here. The negative test is the only
  brake, and it is a strong one only when a coder is willing to say "no
  observation could settle this".

#### `formal` — answers to an abstract system

- **characteristic**: the values are offered as true of an abstract object —
  mathematics, a language's semantics, a stipulated rule set, a numerical
  problem — whose facts exceed what the source's own specification hands you, so
  the values could be wrong and the arbiter is a computation or a proof.
- **positive_test**: a disagreement is settled by running a checker, a solver or
  a proof, with no observation of the world; and getting the value right was
  *work* — it was not free from the generating specification.
- **negative_test**: fails if the generating specification already entails the
  value (then `stipulated`); fails if the decisive check is a measurement (then
  `empirical`).
- **examples**: mathlib/miniF2F statements with their proof status; Lean and Coq
  checking; SAT/TSP instances carrying solved labels; compiler and type-checker
  conformance suites; terminal outcomes under the rules of Go or chess;
  SWE-bench's pass/fail signal; PDEBench solver fields (see the doubt below).
- **notes**: two doubts, both real. **First**, "facts exceed the specification"
  is clean for mathematics and incompleteness, and only pragmatic for Go and for
  large SAT instances, where the rules do entail everything and merely not in
  practice. I accept the pragmatic reading because a value that nobody can
  compute is not free. **Second and worse**: for *lawful but unvalidated*
  computation the `formal`/`empirical` line turns on community practice rather
  than on the object. PDEBench's Navier–Stokes fields are checked by numerical
  convergence against a finer solver and are not offered as evidence about any
  fluid, so I code them `formal`; CMIP6's are validated against observed climate
  and are `empirical`. Same mechanism, same physics, different value, and what
  differs is whether anyone in that field validates against measurement. I
  believe the distinction is the right one — an exercise on the equations is not
  a study of a flow — but its test is sociological and will be coded
  inconsistently.

#### `stipulated` — answers only to its own specification

- **characteristic**: the generating specification *is* the standard; no value
  can be wrong, only differently drawn, and no verification step is even
  definable.
- **positive_test**: there is no procedure that could find an error in a value
  short of re-implementing the generator and comparing; "the source is wrong" is
  not a sentence anyone in the field utters about it.
- **negative_test**: fails if any independent arbiter exists — a solver, a
  checker, a measurement, a published law — that the source's values are
  accountable to.
- **examples**: dSprites and Shapes3D factor grids; Dyck-*k* and PCFG string
  sets; Erdős–Rényi and SBM graphs; BBOB analytic test functions; MuJoCo
  HalfCheetah / Humanoid dynamics; CARLA's and Procgen's invented layouts;
  ALE (see §5.4).
- **notes**: this is the value the axis exists to isolate, and its count is the
  one hard number the design delivers: a floor on "exercises on constructed
  objects". My doubt is the one in §5.5 — read by the letter of the test it also
  swallows synthetic instruction corpora such as Alpaca, which a survey reader
  would not expect to find beside dSprites.

#### `referent-other`

- **characteristic**: the values answer to something none of the three describes.
- **positive_test**: a reviewer can state what the standard of correctness is
  and why no value above holds.
- **negative_test**: not the case where the paper does not say — that is the
  `unknown` coding state.
- **examples**: none named on purpose.
- **notes**: same role as `access-other` and `provenance-other` — it keeps an
  ontological miss recorded as a miss. I expect it near-empty and, unlike
  `provenance-other`, I have no candidate to seed it with, which makes me mildly
  suspicious that my trichotomy is exhaustive by construction rather than by
  derivation. The honest version of that worry: "no check / formal check /
  observational check" is exhaustive over *kinds of check*, so the residue can
  only be a source whose standard of correctness is of a fourth kind — a
  convention settled by neither computation nor observation. I considered a
  `conventional` value for exactly that (SNLI's three-way labels, "is this
  summary helpful", aesthetic ratings) and **declined it**: persistent
  disagreement among competent observers is a property of hard referents, not of
  a different kind of referent, and inter-annotator agreement is itself an
  observation of a population. If that argument is wrong, `conventional` is the
  fourth value and this axis is wrong.

### A value I considered and did not take: particular vs generic

Inside `empirical` there is a further cut — does any item correspond to an
identifiable individual (fastMRI, Habitat's scanned rooms, a GitHub repo) or
only to a population or law (synthetic census, SYNTHIA, DFT energies)? It is
sharp, it is coherent, and I left it off because its consequences are
re-identification risk and representativeness, i.e. it is a governance property,
and `SYNTHESIS.md` §5 already has availability/governance queued as a candidate
axis. Putting it here would make this axis two characteristics, which is the
mistake all three phase-1 runs refused to make with `federated`. Recorded so the
governance derivation inherits it.

---

## (b) The consequent mechanism value set

### `simulated` and `constructed` do collapse

Strip the referent clause from each and read what is left of the mechanism:

- `simulated`: "values computed by executing a human-written mechanistic model
  **of a real referent**" → a human-written program computed the values.
- `constructed`: "values determined by a formal construction, grammar or random
  procedure **with no empirical referent**" → a human-written program computed
  the values.

Identical. Their entire difference is the bolded clause, and both of their
`negative_test`s cite each other by referent and by nothing else. They collapse
into `program-computed`, and `rendered` — which run A held with low confidence —
collapses with them. This is the one part of the brief I can confirm outright
rather than derive: the two values were one mechanism and two referents, and the
proof is that neither value's test can distinguish them once the referent clause
is deleted.

### The superset problem, and what it really is

Under a strict mechanism reading, `rule` ("a stated non-learned rule or
verifier computed the signal") and `model-generated` ("a learned model emitted
it") are both cases of a program computing the signal. `program-computed` as
stated contains both. The brief is right that this is not an axis.

It resolves in two unequal halves.

**`model-generated` survives, and the fix is one word in `program-computed`.**
The distinction learned/not-learned is mechanical, not epistemic: either the
program's parameters were fitted to data or they were not. A coder can answer it
from the name. It is also the most consequential fact on the axis for this
survey, because fitted parameters mean upstream training compute is implicated in
the source's existence. So define `program-computed` as **a program with no
fitted parameters**, and the two values become a partition rather than a
nesting. A hybrid pipeline — a diffusion model proposing candidate structures,
DFT relaxing them — carries both values, which a multi-valued axis handles at no
semantic cost.

**`rule` does not survive, and its failure is informative.** Look at what
`rule`'s test actually asks: *"a person could check the signal by applying a
written rule."* That is checkability, an epistemic property, and it does not
separate a unit test from a finite-element solver — nobody hand-applies a
10⁶-cell solve, and a strict reading of that clause expels the engine cases while
a loose reading readmits them. So `rule`'s stated differentia is not a
mechanism. But its *exemplars* have a shared property its characteristic never
states. Take the ones recorded in `provenance/nodes.tsv`: unit-test pass/fail
rewards, Lean and Coq checking, Go and chess outcomes, distant supervision by
alignment to a knowledge base, a published index formula over administrative
records. Every one of them is a **value computed over content the program did not
produce**. The unit test did not write the code. The aligner did not write the
sentence. The rules of Go did not choose the moves. The index formula did not
collect the administrative records.

So `rule` is not "a rule produced it". `rule` is **"a non-learned program
produced the *target*, over inputs from elsewhere"** — a statement about which
channel the mechanism acted on, not about the mechanism. Which is why its counts
behave as they do: the same table records the firm counts as 9 / 12 / 4 and the
counts *under a reward-channel reading* as 40 / ~55 / 37. A value whose count
moves fourfold when you change which channel you read it against is a channel
statement. That is the strongest evidence in this report and it is measured, not
argued.

### The 2×2 this exposes, and the fourth cell

Cross the two sub-characteristics that have now surfaced — **who computed it**
(non-learned program / learned program) and **what it computed** (the content
itself / a judgment over given content):

| | originates content | judges given content |
|---|---|---|
| no fitted parameters | solvers, engines, renderers, samplers (`program-computed`) | verifiers, checkers, formulas, aligners (`rule`) |
| fitted parameters | Alpaca, Cosmopedia, AlphaFold DB (`model-generated`) | **pseudo-labels, reward-model scores, model-based selectors** |

The fourth cell is empty in the shipped table — and the table's own open
question is exactly that hole: *"whether a model-based SELECTOR (FineWeb-Edu,
DataComp) injects this value. Run A recorded it and said 'selection is not
generation'."* Run A was right and could not say why: selection and pseudo-
labelling are learned *judgments*, and the axis has a name for learned
*generation* only. Noisy-Student pseudo-labels sit in `model-generated`'s
examples while being the same thing as the selector that sits in its open
question.

So the output-role cut is not special to `rule`. And it is not special to
programs either: ImageNet's labels are a human judgment over photographs the
annotator did not take, while SQuAD's questions are human-originated content,
and both are `elicited`. **The same distinction is missing three times, from
three different values.** A distinction that is missing identically across every
producer is an axis, not a value-level repair.

### Resolution, with costs

**R2 — the real fix, recommended as the target.** Scope `provenance` (and
`referent`) to a **channel**: input / target / reward / self (where target *is*
input). Then the mechanism axis needs exactly four producer values, no value
encodes what the program's output was for, the superset disappears without
special pleading, `rule` becomes `program-computed` on the target channel,
pseudo-labels become `model-generated` on the target channel, and the fourth
cell needs no name. Cost: roughly doubles the annotation, which runs A and C
both priced independently (`SYNTHESIS.md` §3). A second cost nobody has priced:
`SYNTHESIS.md` §4 settled that `provenance` attaches to the **entity**, and
channels do not attach uniformly — a dataset's input and label origins are
entity facts, but a *reward* channel is usually a property of the use, so
channel-scoped provenance would be split across entity and mention. That is the
unglamorous reason this fix has not happened, and it should be stated as the
blocker rather than the annotation count.

**R1 — what to ship if channels cannot be had now.** Four producer values, with
the output-role cut written **into the characteristics** so the values are
disjoint by construction rather than by charity:

- `measured` — an instrument transduced a physical signal.
- `authored` — a person composed or chose the content.
- `program-computed` — a program **with no fitted parameters** computed it.
- `model-generated` — a program **with fitted parameters** produced it.

and `rule` kept, if the owner wants its counts now, **explicitly marked as a
non-mechanism refinement** with its characteristic rewritten to what its
exemplars actually share: *a non-learned program assigned values to content it
did not produce*. Costs, stated precisely:

1. The refinement is written once (for non-learned programs) and not for the
   other three producers, so `model-generated` stays conflated with its own
   judgment case and `elicited` stays conflated with annotation. The asymmetry
   is arbitrary; only `rule`'s history justifies it.
2. `rule`'s boundary becomes "content it did not produce", which is **unstable
   for self-play**: the agent produced the moves and the rules judged them, one
   source with two producers, and the coder must decide whether the source is the
   trajectory or the outcome. This is the brief's own game case, returned.
3. The 9→40 / 12→55 / 4→37 swing is not fixed by R1. It is *labelled* by it:
   under R1 the low count is the correct one, and any coder reading rewards as a
   channel will produce the high one. The table's note should say which reading
   is normative, or the counts are uninterpretable.

**I recommend R1 now with R2 named as the target in the axis header**, and I
recommend against the intermediate temptation of a flat four-value program
mechanism (`program-computed`, `rule`, `model-generated`, `model-labeled`),
because it writes the channel question into four value names and thereby makes
R2 harder to adopt later: once `model-labeled` has counts, taking it away costs
a migration.

### `natural` versus `human-incidental`

The brief says this boundary turns on the subject rather than the mechanism, and
that is true of the *tests* but not of the *values*. There is a mechanism
difference here, and it is being obscured by two things.

`natural`'s test is written about the subject — *"remove every human purpose and
the process still runs"* — and its negative test is written about the subject
too: *"a human artifact or judgement arriving through an instrument is not
natural."* Run A already recorded the vacuity worry (*"every photograph is a
camera measurement"*). Both halves of the brief's complaint follow: a
photographic street-sign corpus is expelled by `natural`'s negative test, and it
is *also* expelled by `human-incidental`'s positive test under a strict reading,
because the signs would exist unchanged without the dataset but **the
photographs would not**. Neither value holds; the source lands in
`provenance-other`. That is a defect in the shipped table, reachable from the
tests alone.

Delete the subject from both tests and a clean mechanism difference remains:
**an instrument transduced a physical signal** versus **a person composed the
content, recorded as symbols**. So:

- **`natural` → `measured`**, retested on the producer and **indifferent to the
  subject**. Positive test: there is a sensor, assay or device whose calibration
  could be questioned, and the values are a transduction of a physical quantity.
  MRI, survey imaging, a photograph of a street sign, a scanned manuscript, a
  microphone recording of a read sentence — all `measured`. Run A's vacuity
  worry becomes a feature: yes, every photograph is a measurement; that *is* the
  mechanism; the subject question has moved to `referent`, where
  the street-sign corpus is `empirical` and no test expels it.
- **`human-incidental` → `authored`**, the producer being a person: the record
  is the content they composed or chose (text, code, a rating, a click, a move),
  not a measurement of their body. LibriSpeech is then `{authored, measured}`
  and IAM handwriting is `{authored, measured}`, which multi-valued provenance
  already supports and which is more accurate than either value alone.

So **`natural` vs `human-incidental` survives**, renamed and retested. And then
the strict reading runs past where the brief pointed it:

**`elicited` does not survive as a mechanism value.** Its producer is a person,
the same as `authored`'s. Its characteristic — *"the signal exists because the
collection asked for it"* — is about **why the content exists**, and the table's
own phase-2 note confirms this by widening it from "from people" to macaque
recordings and ProteinGym with the explanation that *"the characteristic always
turned on the ASKING, never on the species"*. Asking is not a mechanism. It is
precisely run C's predicted `collection channel` axis
(`scraped / instrumented / solicited / donated / purchased / administrative`),
and C's warning was that it would be *"smuggled into provenance"*.

This has to be handled carefully, because `elicited` is a 3/3 unanimous result
and `METHOD.md` makes 3/3 agreement the strongest evidence the method can
produce. My reading: the unanimity establishes that the distinction **matters**,
not that it belongs on **this** axis — which is the ruling the method already
made for `federated`, where all three runs reached the case and all three refused
to put it on `access` because its differentia was governance rather than
control. `elicited` is to `provenance` what `federated` was to `access`, with
one difference that should worry the owner: all three runs *did* place it, so
nobody flagged it, and there is no unanimous doubt to lean on.

Recommendation: **keep `elicited` for now, as a declared lodger**, with a header
note that its characteristic is solicitation and not mechanism and that it is
the first value of the collection-channel axis, to be moved when that axis is
derived. Moving it now would be correct and premature: it is the most used value
on the axis and the thing it records — whether somebody paid per item — is the
single most survey-relevant fact about annotation cost. The cost of keeping it
is that `provenance` remains, honestly labelled, an axis with one mechanism
characteristic plus two lodgers (`elicited` for solicitation, `rule` for
channel).

**A side effect worth flagging, because it moves an instrument the owner is
relying on.** The byproduct-of-operation decision routed machine-emitted records
(Borg and Alibaba cluster traces) to `provenance-other`, and `SYNTHESIS.md` §2
makes the count that accumulates there *the measurement* that decides whether
`operational` is restored. Under this design that count changes meaning: a
cluster trace is both a program's emission and an instrumented measurement of a
running system, so it codes `{measured, program-computed}` and
`provenance-other` empties. The telemetry case stops being "no value holds" and
becomes "two values hold", which multi-valued provenance supports. **This
disarms the instrument.** If the owner wants the restore decision to stay
measurable, the evidence has to be re-homed — the obvious candidate is the
collection-channel axis's `administrative`/`instrumented` values, which is where
that question belonged all along.

### Proposed table, R1

```tsv
node_id	name	parents	characteristic	positive_test	negative_test	examples	notes
measured	Instrument measurement		an instrument transduced a physical signal into the values	a sensor, assay or device stands in the chain and its calibration could be questioned; the values are a transduction of a physical quantity	fails if no device transduced anything -- a symbolic record of what a person composed is `authored`, not measured	fastMRI k-space; SDSS/LSST imaging; Sentinel-2; PDB experimental structures; a photographic street-sign corpus; LibriSpeech audio; scanned manuscripts	renamed from `natural` and INDIFFERENT TO THE SUBJECT. The old test ("remove every human purpose and the process still runs") was a referent test and expelled its own photographic exemplars; the subject question now lives on `referent`. Entails `referent = empirical`
authored	Authored by a person		a person composed or chose the content, and the record is that content rather than a measurement of the person	a human decision determined each value, and the record is symbolic -- keystrokes, text, code, a rating, a click, a move	fails if an instrument transduced it (`measured`); fails if a program or model computed it	Common Crawl and Wikipedia; The Stack; Gutenberg; MovieLens ratings; Criteo clicks; MIMIC clinical notes; ImageNet labels; SQuAD	absorbs `human-incidental`, and under a strict mechanism reading would absorb `elicited` too -- see that row. Co-occurs with `measured` wherever a device captured the authoring (speech, handwriting)
program-computed	Computed by a program		a program WITH NO FITTED PARAMETERS computed the values	there is an executable specification -- solver, engine, renderer, grammar, sampler, formula -- and re-running it reproduces the values	fails if any parameter in the producing program was fitted to data (`model-generated`); fails if the values were transduced or authored	PDEBench and CMIP6 solver output; OC20/ANI-1x DFT; MuJoCo rollouts; CARLA and Habitat renders; dSprites factor grids; Dyck-k and PCFG strings; ER and SBM graphs; BBOB functions	COLLAPSES `simulated` + `constructed` + `rendered`: once the referent clause is deleted from each, no test distinguishes them. "No fitted parameters" is what makes this disjoint from `model-generated` rather than a superset of it
model-generated	Produced by a learned model		a program WITH FITTED PARAMETERS produced the values	a trained checkpoint stands in the causal chain that produced the content, not merely scoring or filtering it	fails if the program has no fitted parameters (`program-computed`)	Self-Instruct / Alpaca; Cosmopedia; AlphaFold DB structures used as data; Noisy-Student pseudo-labels	still CONFLATES generation with learned judgment -- pseudo-labels and reward-model scores are judgments over given content, which is the fourth cell of the 2x2 and the same hole as the open selector question (FineWeb-Edu, DataComp). Not fixed by R1; fixed by channel scoping
elicited	Elicited to order		LODGER, not a mechanism: the signal exists because the collection asked for it	a task description, protocol, prompt or payment caused each item to be produced	repurposed pre-existing material stays `authored` however aggressively filtered	ImageNet class labels; MS COCO; SQuAD; HH-RLHF; teleoperated demonstrations; Neural Latents Benchmark; ProteinGym	its producer is a person, identical to `authored`; its differentia is WHY the content exists. That is run C's predicted `collection channel` axis. KEPT because it is 3/3 and carries the annotation-cost fact, MARKED because unanimity shows the distinction matters, not that it belongs here -- the `federated` ruling, applied to a value nobody flagged
rule	Computed over given content by a rule		LODGER, not a mechanism: a non-learned program assigned values to content it did not produce	the program decided or scored input that arrived from elsewhere, and its parameters are not fitted	fails if the program also produced the content it scored (`program-computed`); fails if its parameters are fitted	unit-test pass/fail; Lean and Coq checking; Go and chess terminal outcomes; distant supervision by KB alignment; a published index formula over administrative records	REWRITTEN from "a person could check it by applying a written rule", which is checkability, not mechanism, and does not separate a unit test from a finite-element solve. Every exemplar shares "computed over content from elsewhere", i.e. a CHANNEL. Evidence: its count swings 9->40, 12->55, 4->37 under a reward-channel reading. Unstable for self-play
provenance-other	Other provenance		a producing process none of the above describes	a reviewer can say what produced the values and why no value fits	not the case where the paper does not say -- that is the `unknown` coding state	none named on purpose	EMPTIES under this design: machine-emitted telemetry now codes {measured, program-computed}. This removes the instrument SYNTHESIS.md section 2 relies on for the byproduct-of-operation revisit; that evidence must be re-homed
```

---

## The channel problem

**It survives. My design does not solve it, and it makes it load-bearing in two
new places.**

1. `rule` versus `program-computed` is a channel distinction (§3). I can make
   the two values disjoint by writing "content it did not produce" into `rule`,
   but that phrase *is* the channel, written into a value name because there is
   nowhere else to put it. The 9→40 / 12→55 / 4→37 swing is the same defect,
   measured.
2. `referent` is single-valued only because R2 scopes it to the target channel
   by fiat. SWE-bench's real repositories (`empirical`) and its test-derived
   rewards (`formal`) have different referents, and R2 records one. CARLA's
   invented layout (`stipulated`) and its vehicle dynamics (`empirical`) have
   different referents, and R2 records one. OC20's enumerated geometries
   (`formal`) and its DFT energies (`empirical`) have different referents, and
   R2 records one.

So the honest accounting is that the referent axis **relocates** the channel
problem rather than reducing it: it removes a conflation from `provenance` and
declares a channel scope on the new axis, where before the scope was undeclared.
Declared is better than undeclared, and it is not solved.

Per the brief I am not inventing a channel axis. What would solve it, stated as
precisely as I can:

- A **channel enum** — `input` / `target` / `reward` / `self` — with
  `provenance` and `referent` recorded per channel present in the source. Not a
  new axis: a scope qualifier on two existing ones, which is why it does not
  double the value sets, only the rows.
- The blocker is **not** the annotation cost. It is that `SYNTHESIS.md` §4
  settled `provenance` onto the entity, and channels do not all live there: a
  dataset's input and target origins are entity facts, but the reward channel is
  usually a fact about the use (the same environment scored by a programmatic
  reward, a human preference and a learned reward model — run A's three research
  programs). So channel scoping forces `provenance` to be split across entity
  and mention, which reopens a settled decision. **That** is what has to be
  decided before the fix is available, and it is a cheaper question than the
  annotation one.
- Interim mitigation that costs nothing: state in both axis headers **which
  channel is normative** when channels disagree. Without that, every count on
  `rule` and every count on `referent` is ambiguous by a factor the corpus has
  already measured at four.

---

## 5. Where my own tests contradict each other

These are the ones I could not argue away. Each is a case where two of my own
tests both pass, or both fail, and the value is settled by my decision rather
than by the tests.

**5.1 Executable code.** SWE-bench's pass/fail: `empirical` passes — the
referent is a particular repository that exists, and running its tests *is* an
observation of that artifact's behaviour. `formal` passes — the arbiter is a
computation and nobody observes the world. I ruled `formal`, on the ground that
executing a program is deterministic computation rather than measurement, and I
am not confident. The ruling has a consequence I do like: it puts The Stack
(`empirical` — a record of what people wrote) and SWE-bench's reward (`formal` —
answers to the test suite) on different values, which is correct, and it is also
the clearest instance of §4's point that one source has two channels with two
referents.

**5.2 Habitat and every scan-then-render pipeline.** The geometry is a
measurement of actual interiors, so `empirical`'s substitution test passes: a
real photograph from that pose is what the render stands in for, and the
photorealism gap is reported as error. But the lighting and material models are
stipulated and are not about those rooms. Both readings pass, on different parts
of the same frame. `provenance/nodes.tsv` already records Habitat as *"the
recurring hard case"* for the `simulated`/`constructed` boundary; my design
moves the hard case from the mechanism axis to the referent axis and does not
dissolve it. That is worth knowing before anyone claims the collapse fixed
Habitat: **it relocated Habitat.**

**5.3 Engines named as the source — the contradiction with `SYNTHESIS.md` §4.**
R1 says machinery is a channel, so MuJoCo-the-engine has no referent; a MuJoCo
HalfCheetah task is `stipulated` and a MuJoCo model of a specific Franka arm is
`empirical`. Both are MuJoCo. If the named entity is the scenario, the axis is
well defined. If the named entity is the **engine** — which is exactly how
papers cite it ("we used MuJoCo") — the entity has no referent and only the use
fixes it. So `referent` is an entity property for scenario-named and
corpus-named sources and a **mention** property for engine-named sources, which
contradicts §4's settled "provenance attaches to the entity". I cannot resolve
this from inside the axis. My recommendation is the `use-determined` marker in
the scope section: code it as such on the entity, and if the counts there are
large, §4 has to be reopened for this axis. Note that §4's own criterion helps a
little — *a derivation earns an entity when it is named as an artifact* — because
it means the badly-behaved cases are concentrated in engine citations rather than
spread everywhere.

**5.4 Emulated systems.** ALE: `stipulated` passes (the emulator is the
authority; nothing can be wrong). `formal` passes (the ROM is a specification
whose behaviour must be computed and could be implemented incorrectly).
`empirical` passes on a stubborn reading (the arbiter is a 1982 console, a
physical artifact that exists, and faithfulness to it is a real property). All
three. I ruled `stipulated` on a pragmatic criterion — nobody in the field
reports ALE's fidelity to original hardware as error — and a pragmatic criterion
is not a test. This is the same weakness as the `formal`/`empirical` line in
5.6: where the community does not validate, my tests cannot tell what the source
answers to.

**5.5 Synthetic instruction corpora.** Alpaca's responses. By `empirical`'s
test: a disagreement is settled by asking people whether the response is good,
which is an observation of a social system — passes. By `stipulated`'s test: no
verification step is definable, the model's output *is* the data, and the only
recourse is re-sampling — also passes. The two tests give opposite answers on
the same signal, and the reason is that "is this response correct" and "do
people like this response" are different questions about one value. I lean
`stipulated` by the letter of the tests, and that puts Cosmopedia and Alpaca
beside dSprites under the one statistic the axis exists to produce. A survey
reader told that *N*% of this institute's sources are exercises on constructed
objects would not expect synthetic pretraining corpora in that number. This is
the contradiction I would fix first if I had one more revision, and the likely
shape of the fix is that `stipulated` needs splitting by whether the source is
*offered as a stand-in* for something (synthetic data is; dSprites is not),
which is suspiciously close to re-deriving `simulated`/`constructed` on the
referent axis where it belongs.

**5.6 Lawful computation nobody validates.** PDEBench `formal` versus CMIP6
`empirical`, same mechanism and same physics, separated by whether the field
validates against measurement (§(a), `formal` notes). Both of my tests can be
made to pass on either, and what decides is practice.

**5.7 Telemetry.** A cluster trace fails `authored` (no person produced it) and
passes both `measured` (an instrument on a running system) and
`program-computed` (a monitoring program emitted the record). Under the shipped
table it passes **nothing** and lands in `provenance-other`; under mine it
passes **two**, which multi-valued provenance accepts. A value that goes from
zero holders to two holders without any new evidence is a sign that both tables
are guessing. It also disarms the measurement §2 depends on, as flagged above.

**5.8 Self-play.** The agent produced the moves; the rules produced the outcome.
`rule`'s rewritten boundary ("content it did not produce") needs to know what
the source is, and the source is both. The shipped table routes game outcomes to
`rule` and the trajectories to nothing in particular; mine does the same. The
brief called the game case a scope problem rather than a value problem, and I
agree — and §3 is my claim that `rule`'s whole existence is that same scope
problem, so the two are one finding and neither half of this brief fixes it.

---

## 6. Summary of what I would ship

1. `referent`, **single-valued**, **all sources**, scoped by declared fiat to the
   target channel: `empirical` · `formal` · `stipulated`, plus
   `referent-other`; `unknown` a coding state; a separate `use-determined`
   marker for engine-named sources (5.3).
2. `provenance` becomes a **producer** axis: `measured` · `authored` ·
   `program-computed` (no fitted parameters) · `model-generated` (fitted
   parameters), plus `provenance-other`. `simulated`, `constructed` and
   `rendered` collapse into `program-computed`; `natural` is renamed `measured`
   and loses its subject clause.
3. `elicited` and `rule` are **kept and labelled as lodgers** with rewritten
   characteristics — solicitation and channel respectively — and are the first
   two values of the collection-channel axis and of channel scoping. The axis
   header should say so, so the next reader does not mistake them for mechanism.
4. The channel problem is **unsolved**; what would solve it is a channel scope
   on `provenance` and `referent`, and the blocker is the entity/mention split
   in `SYNTHESIS.md` §4, not the annotation cost.
5. The byproduct-of-operation measurement in `SYNTHESIS.md` §2 **needs
   re-homing**: under this design `provenance-other` empties and stops being the
   instrument it was chosen to be.
