# Run D3 — the `referent` axis, and `provenance` as mechanism

Independent derivation, 2026-10-08. Entry point taken for this run: **what
makes a signal's values wrong** — i.e. derive the axis from the standard of
correctness a source is answerable to, rather than from what the source is
"about".

## What I read

Exactly these files, in this order:

1. `data/ontology/design/axes_data_sources/REFERENT_BRIEF.md`
2. `data/ontology/design/axes_data_sources/METHOD.md`
3. `data/ontology/design/axes_data_sources/access/nodes.tsv`
4. `data/ontology/design/axes_data_sources/provenance/nodes.tsv`
5. `data/ontology/design/axes_data_sources/SYNTHESIS.md`, lines 1–340
   (sections 1 to 5; §6 begins at line 341 and was not read)

Also read, incidentally, the output of `ls` on the directory, which shows the
names `placement_candidates.tsv`, `operational_sweep.tsv` and `placements/`.
No corpus file, no placement, no sweep, no `datasets/v0`, nothing under
`paperext-llm-backend/`, and no other run's derivation was opened. No name in
this report came from a corpus file; every exemplar is from field knowledge, and
where I name something the two allowed tables already name (fastMRI, MIMIC,
Habitat, Juliet, CANUE) I am reusing their row, not a placement.

Note that `access/nodes.tsv` and `provenance/nodes.tsv` carry **phase-2
annotations** (counts, `MEASURED 0`, per-run name lists). The brief permits
these files, so I read them, but I flag that they leak corpus results into a
supposedly blind derivation. Two places where that leak could have influenced
me, declared so they can be discounted: the `rule` row's "counts swing to 40 /
~55 / 37 under a reward-channel reading", which I use below as evidence about
the channel problem, and the `provenance` header's note that all three phase-2
runs read the `natural`/`human-incidental` rows as a contradiction, which I use
as evidence for redrawing that boundary. Both are arguments I would make from
the row text alone; the counts only tell me the size.

---

## 0. Disagreement with the brief, stated first

**The brief under-diagnoses the defect.** It frames `provenance` as a mechanism
axis with one value (`simulated`) that illegitimately asks a second question.
On my reading the column is carrying **four** questions, not two:

| question | values that actually turn on it |
|---|---|
| by what process were the values produced | all of them, nominally |
| what does the signal answer to | `simulated` vs `constructed`; and `rule`'s entire case for existing |
| what is the signal *about* (subject matter) | `natural` vs `human-incidental` |
| did the collection cause the signal to exist | `human-incidental` vs `elicited` |

The second is the `referent` axis and the brief has it right. The third is
**subject matter, which is the `domains` dimension's job**, and the right fix is
not a new axis but deletion of the subject test from `natural`. The fourth is
solicitation, which is a real fact that is not a production mechanism; I keep
the value and declare the defect rather than invent an axis for it.

The direct evidence for the second claim is in `SYNTHESIS.md` §2 itself. Run B's
defence of `rule` is quoted as: *"a unit test checks real code, so 'formal
construction with no empirical referent' is false of it."* That is a **referent**
argument, verbatim: `rule` was not proposed because unit-test rewards are
produced by a different mechanism than a PDE solver — they are not — but because
`constructed`'s test about empirical referents misfired on them. So `rule`'s
existence is itself a measurement of the defect this brief is fixing. Likewise
run A named the first value `measured` (a mechanism) while B and C named it
`natural` (a subject); that 1-vs-2 naming split falls exactly along the fault
line, and was recorded as agreement because alignment is by characteristic. It
was agreement on the cut and disagreement on what the cut *is*.

**I also reject the brief's gloss** — *is this a study of the world or an
exercise on a constructed object*. It is a hybrid of referent and subject, and
it has no place for the largest class of sources in the field: a human
preference dataset is not a study of the world and is not an exercise on a
constructed object either. An axis built to answer it would re-import the
subject question that broke `natural`. My division answers a narrower question
that is decidable: **what could make this source's values wrong?**

Where I agree without reservation: the channel case is a scope problem, not a
value problem, and a channel axis would not fix it. I sharpen that in §5 — it is
not even a scope problem, it is a *key* problem, and no axis can fix it.

---

## (a) The `referent` axis

### Principle of division

**What the signal's values are answerable to: particular individuals that
existed independently of the source, a real class of phenomena and nothing
narrower, or only the source's own specification.**

Equivalently, and this is the form I used to run every test: *name the thing
that could show one of these values to be in error.* Three kinds of answer
exist, and the axis records which.

Two guards that keep the axis from drifting back into the swamp:

- **Kind of referent is not this axis.** Whether the referent is a galaxy, a
  patient, a market or a web page is subject matter, and the `domains`
  dimension already owns it. This axis records only the *existence and
  bindingness* of the referent. Any value I could only state by naming a
  subject area is out of scope by construction.
- **Mechanism is not this axis.** No value name may contain a production verb
  (measured, simulated, computed, generated, rendered). I enforced this on the
  names below; `simulated` fails the rule, which is one more way of seeing why
  it could not hold a referent distinction.

### Is it single- or multi-valued? — **multi-valued, with an admission rule**

I started from single-valued with a precedence rule (`particular` beats
`generic` beats `stipulated`), because the roll-up the axis exists for is a
share and shares want exclusivity. I reversed it, for two reasons.

1. **Precedence can be applied at query time; it cannot be undone at coding
   time.** A single-valued coder deciding OC20's enumerated candidate geometries
   (`stipulated`) against its DFT energies (`generic`) destroys information that
   a multi-valued record keeps, and the share can still be computed by a stated
   rule (below). Single-valued is strictly weaker here.
2. A case in §6 forced it: a formal-mathematics corpus is both an actual
   collection of files that exist and a body of statements whose correctness is
   internal. Multi-valued is the only honest record of it, and I did not
   anticipate that when I chose.

The analogy to `access` does **not** carry: `access` was kept single-valued
because `{fixed, interactive}` makes the example count unrecoverable. There is
no arithmetic on `referent`, so a set costs nothing numerically.

The cost of multi-valued is value creep — `generic` will accrete onto anything
loosely motivated by a real phenomenon. Hence the **admission rule: a second
value is admissible only if the coder can name the channel or component it holds
of** ("geometries vs energies", "image vs caption", "observations vs reward").
If the channel cannot be named, the source gets one value. This makes the axis
self-reporting about the channel problem: a multi-valued referent row is a
flag that the source is composite.

**Stated roll-up rule**, so that the share survives the set: a source *answers
to something outside itself* iff its value set contains anything other than
`stipulated`; it is *wholly self-contained* iff its set is exactly
`{stipulated}`; it is *partly* self-contained if `stipulated` appears alongside
another value. The third bucket is not an artefact to be eliminated — it is the
honest answer for OC20 and for every benchmark with constructed inputs and
worldly targets.

### Scope — **every source, no scope predicate**

Rejected: *applies only to computed sources.* Three reasons.

- A scope predicate conditioned on provenance values makes the two axes
  non-orthogonal, which is precisely the coupling this split exists to remove.
- It is false that collected sources have no referent question. A scrape of web
  pages answers to the pages; a formal-mathematics corpus answers to nothing
  outside itself; those are different answers and both are useful.
- The survey question ("what share of this institute's data answers to the
  world") needs a value on every source or the denominator is a join.

The honest caveat, which §6 records as a contradiction with my own decision: the
axis is **near-constant** on `instrument-captured` and on human-produced
sources, which are almost always `particular`. Low entropy is not incoherence
(METHOD §4), but a reviewer who wanted a predicate would have a real argument,
and the only reason to refuse is the coupling.

### Coding state for "the paper does not say"

`unknown`, a coding state, not a node — the convention already settled on both
sibling axes. Two things specific to this axis:

- **`unknown` will be frequent here, more so than on `access` or
  `provenance`.** Papers routinely do not say whether their simulator was
  calibrated against anything, or where a synthetic generator's parameters came
  from. That makes "how often does the field state what its data answers to"
  a statistic worth having, and it is destroyed if `unknown` is folded into a
  value.
- **The specific mis-coding to block:** defaulting anything with "sim" in its
  name to `generic`. The word `simulated` carried the realism claim for free;
  this axis requires the claim to be evidenced. If the paper does not say and
  the generator's documentation does not say, the value is `unknown`, not
  `generic`.

### The values

#### `particular` — answers to specific individuals

- **characteristic:** the values report on specific individuals — objects,
  events, organisms, utterances, artifacts, records or runs — that existed
  independently of this source and could in principle be identified.
- **positive_test:** pick any item and ask *which one is this a record of*; the
  question has a determinate answer (this patient, this sky position, this URL,
  this repository at this commit, this game that was played, this training run
  that was executed), and an error in the item is an error **about that
  individual**.
- **negative_test:** fails when no individual can be named even in principle
  (then `generic` or `stipulated`). Fails when the only thing outside the source
  is the source's **own carrier**: that the file exists, or that the values were
  copied faithfully, is transcription fidelity, not a referent — otherwise every
  source whatever is `particular` and the value is vacuous.
- **examples:** SDSS and LSST imaging; fastMRI k-space; MIMIC-III records;
  Sentinel-2 scenes; Common Crawl and Wikipedia pages; The Stack repositories;
  recorded human game archives; measured tabular NAS/HPO benchmarks (the
  recorded accuracies of networks that were actually trained); machine-emitted
  cluster traces; annotator preference judgements; ImageNet's photographs.
- **notes:** inherits run A's vacuity worry about `natural` in a new shape —
  *every dataset is itself a real artifact*. The carrier clause in the negative
  test is the whole defence and it does not cleanly dispose of the
  formal-mathematics case (§6.4). Expect this value to be the largest on the
  axis by a wide margin; per METHOD §4 that is a finding, not a defect, and the
  distinctions a reader wants inside it (sky vs selfie vs clinic) are
  `domains`'. Note the value is **indifferent to whether the individual is
  physical**: a training run that happened and was measured is as particular as
  a galaxy, which is why machine telemetry gets a referent even though it has
  nowhere to sit on `provenance` today.

#### `generic` — answers to a real class, to no individual

- **characteristic:** no individual is reported, but the values are held to a
  real class of phenomena: the source is answerable to the complaint that it is
  unrealistic.
- **positive_test:** no item can be matched to an individual, **and** some part
  of the generating specification was fixed by measurement, fitting or
  calibration against the world, so that *"this is not like the real thing"* is
  a complaint the source's makers owe an answer to — and someone has in fact
  tried to validate it against the world.
- **negative_test:** fails if the specification was authored freely and nobody
  is entitled to call the output unrealistic (`stipulated`); fails if an
  individual is reported (`particular`); **being motivated by** a real
  phenomenon is not the same as **answering to** one, and motivation alone
  fails this test.
- **examples:** a regulated physiological or pharmacokinetic simulator whose
  parameters are fitted to a patient population; driving simulators whose
  sensor and vehicle-dynamics models are calibrated to real hardware; CMIP6
  climate runs; OC20 / ANI-1x DFT energies; synthetic patient records released
  in place of real ones; large model-generated text corpora intended to pass
  for human text; generative-model imagery used as training data.
- **notes:** this is the sim2real and synthetic-data-validity population, and it
  is the value the brief's motivating case needs — the physiological simulator
  and the rigid-body locomotion task have identical machinery and land here and
  on `stipulated` respectively. It is also the **weakest value in my design**:
  its positive test turns on a validity claim being *in force*, which is partly
  a fact about a community rather than about an artifact (§6.5). I considered
  deleting it and keeping a two-value axis; I kept it because without it the
  brief's two simulators are indistinguishable again, which is the exact defect
  being repaired. Rarity is not why it survives (METHOD §4) and it will not be
  rare.

#### `stipulated` — answers only to its own specification

- **characteristic:** the generating specification is the whole standard of
  correctness; there is nothing outside the source for a value to be wrong
  about.
- **positive_test:** given the specification (a grammar, a distribution, a rule
  set, an authored asset, an axiom system), every value is correct by
  construction, and no amount of looking at the world could show an item to be
  in error — only a bug could.
- **negative_test:** fails if any part of the specification was fixed by
  measurement of, or fitting to, the world; fails if an individual is reported.
  "Approximation error" being meaningful is the giveaway: if there is something
  to approximate, this is not the value.
- **examples:** Dyck-k and PCFG string sets; dSprites and Shapes3D factor grids;
  Erdos-Renyi graphs with swept parameters; BBOB analytic functions; random
  k-SAT families; hand-authored locomotion morphologies in a rigid-body engine;
  Lean or Coq proof-checking outcomes; terminal outcomes from the rules of Go or
  chess.
- **notes:** this is the old `constructed`'s exemplar list, which is expected —
  `constructed` was a referent value wearing a mechanism's name, so it maps
  almost one-to-one. The deliberate and contestable call: a source *motivated*
  by a real phenomenon but not fitted to one is `stipulated`, so a
  stochastic-block-model graph is `stipulated` even though community structure
  in real networks is why anyone studies it. Readers will push back on that;
  the motivation is recoverable from `domains`.

#### `referent-other`

- **characteristic:** a determinate standard of correctness that none of the
  above describes.
- **positive_test:** a reviewer can state what the values answer to and why no
  value above applies.
- **negative_test:** not the case where the paper does not say — that is the
  `unknown` coding state.
- **examples:** none named on purpose. The trichotomy is intended exhaustive
  (an individual, a class, nothing). The hard candidates I could construct and
  could not place confidently: a source whose standard is **normative** rather
  than factual (a legal code, a style guide, a safety policy, where "wrong" means
  non-compliant rather than inaccurate), and a source whose referent is
  **counterfactual** (a what-if scenario ensemble that is neither a real class
  nor freely authored).
- **notes:** exists so an ontological miss is recorded as a miss, per the
  convention on both sibling axes. Forecast targets are **not** a candidate:
  their referent is a real future event, so `particular`, verifiable late.

### Attachment and granularity

`referent` attaches to the **entity**, as `provenance` does, so the two
entity-level axes can be read together. But this axis has a **finer granularity
requirement than either sibling**, and that is new: one physics engine spans all
three values depending on which task model is loaded (a hand-authored humanoid
is `stipulated`, a CAD-derived model of a real robot arm is `generic`, a
digital twin of one specific deployed machine is `particular`). So the named
unit must be the task family or model, not the engine. This independently
corroborates run A's lone `granularity should be decided per axis, not per
dimension` finding (SYNTHESIS §3), from a direction A could not have seen.

Two exception classes where the value is genuinely a property of the **use**,
not the entity, recorded rather than resolved: a parametric random-graph family
whose parameters the paper *fitted to a real network* (`generic`) versus *swept*
(`stipulated`); and an engine used for a control result (`stipulated`) versus
for a sim2real transfer result (`generic`). Entity attachment mis-codes both. I
keep entity attachment because mention attachment doubles the annotation and
because §4's criterion — a derivation earns an entity when it is named as an
artifact — already handles the common case, where the fitted variant gets its
own name.

---

## (b) The consequent mechanism value set for `provenance`

### The collapse, and the superset problem

`simulated` and `constructed` differ **only** by referent: both are a stated
procedure executed. They collapse. `rule`'s characteristic already says
*"rule, verifier or engine"* — an engine is a solver, so under a strict mechanism
reading **`rule` and the collapsed `program-computed` are the same value too**.
Three values become one.

That is the resolution of the brief's superset question, and the general lesson
is worth stating because it is reusable:

> **A mechanism value named after the medium will always be a superset of
> mechanism values named after the kind of medium.** `program-computed` names the
> medium (a program); `rule` and `model-generated` name kinds of program. The
> repair is not to delete a value or to nest them — it is to stop naming any
> value after the medium, and to re-cut the computed region by a *differentia of
> production*.

The differentia that cuts it: **was the mapping from inputs to values stated, or
fitted?** That gives two disjoint values, neither a superset of the other:

- `computed` — a stated procedure determined the values.
- `model-generated` — a trained checkpoint stands in the causal chain.

Disjointness is by the fitted-content test, not by intuition: a learned model's
forward pass is a stated procedure *given the weights*, so the test has to be
about where the content lives. See `computed`'s negative test below.

**What happened to each of the three values the brief asks about:**

- **`rule`** — **dissolved into `computed`.** It was never a mechanism distinct
  from `simulated`; its case for existing was a referent argument (§0). Nothing
  is lost: what `rule` was actually tracking is now `referent`, and it tracked it
  badly, splitting one way for unit tests on real repositories (`computed` +
  `particular`) and another for proof checking (`computed` + `stipulated`) —
  two cases the old axis had to put in one value.
- **`model-generated`** — **kept, unchanged in substance.** It is the one value
  on the old axis whose test was purely about production (*"a model checkpoint
  stands in the causal chain... not merely scoring or filtering it"*). Its open
  question — whether a model-based *selector* injects the value — is untouched by
  this change, and the referent axis does not help with it: selection changes the
  distribution, not the referent either.
- **`program-computed`** — **renamed `computed` and it is the collapsed value,
  not a parent of the other two.** I considered the alternative available in the
  schema: the `parents` column is present and empty on every row, so a declared
  parent edge `rule -> program-computed` would make the superset a legitimate
  taxonomy rather than two siblings pretending to be disjoint. I rejected it
  **here** because after `referent` takes `rule`'s differentia there is nothing
  left for the child to be a child *of* — a child whose only differentia is
  "same as the parent" is not a node. The hierarchy option is the right answer
  to a superset problem **when the child carries a real additional fact**, and I
  use it once below, for `elicited`.

### `natural` versus `human-incidental`

Their boundary turns on the subject — the brief is right — and under a strict
mechanism reading the boundary is in the **wrong place entirely**. A
street-sign photograph and a galaxy image are the same mechanism: a sensor
transduced some state of the world into values. A scraped web page is a
different mechanism: the bytes were authored, with no instrument anywhere. So
the cut is:

- **`instrument-captured`** — a sensor, assay or logger transduced a state of
  the world into values. *Positive:* an identifiable instrument stands between
  the world and the record, and instrument error (calibration, noise, dropout) is
  a meaningful property of the values. *Negative:* fails when the values are
  symbolic output that a person or program emitted directly, with no
  transduction step.
- **`human-authored`** — a person's (or animal's) own action or artifact **is**
  the content. *Positive:* remove the human and there is no signal, and no
  instrument reading mediates between their act and the recorded value.
  *Negative:* fails if a sensor produced the values and the human only chose
  what to point it at.

The subject question — nature, artifact, person, institution — **moves out of
the dimension entirely, to `domains`.** That is the part of this proposal
likeliest to be resisted, so the argument plainly: subject matter is a second
characteristic, and the project has already refused, twice, to let a second
characteristic onto an axis (`federated` off `access`, by unanimous doubt; `mixed`
off `provenance`, by owner decision). Keeping "is the subject natural" on a
production axis is the same error with a longer tenure.

**What the redraw buys, concretely.** `provenance/nodes.tsv`'s own header has to
spend a paragraph explaining that `natural` lists fastMRI while
`human-incidental` lists MIMIC, that this is not a conflict, and that all three
phase-2 runs read it as one anyway. Under the redraw, there is nothing to
explain: fastMRI is `{instrument-captured}`; MIMIC is
`{instrument-captured, human-authored}` because its waveforms were transduced and
its notes and codes were written; and the reason both looked like they should be
`natural` — a body is natural — stops being expressible on the axis. A documented
three-of-three reader failure is removed by deleting the test that caused it.

It also recovers information the current table loses. A web-scale image-text
corpus is listed today only under `human-incidental`, which drops the camera
entirely; under the redraw it is `{instrument-captured, human-authored}` — the
pixels transduced, the captions written — which is both truer and exactly the
two-channel structure such corpora have.

**What it costs.** `instrument-captured` becomes the largest value and merges a
sky survey with a selfie. Per METHOD §4 that is not a reason to rebalance, and
every distinction a reader wants inside it survives elsewhere: subject on
`domains`, solicitation on `elicited`, and *what it answers to* on `referent`.
Also: **the name `natural` must be retired, not just re-tested.** The word is
what invites the subject reading, and a renamed test on an unrenamed value will
be coded as the old one.

### `elicited`, and the one place I do declare a parent edge

Under the strictest mechanism reading, `elicited` and `human-authored` are the
same mechanism — a person produced the content — differing only in whether the
collection caused it to exist, which is a fact about the **collection**, not
about production. That is run C's predicted `collection channel` axis
(SYNTHESIS §3, 1/3) reaching up and claiming a second value.

A defence of `elicited` as a genuine production fact exists, and I think it
holds: in elicited data the collection's **protocol co-determines the values** —
a label schema fixes which values are possible, an instruction fixes the form of
the question. The signal was produced by a human acting *under a specification
supplied by the collection*, and that is about production, not about who asked.

So: **`elicited` is kept, as a declared child of `human-authored`** (`parents =
human-authored`), with its note stating that its differentia is partly
solicitation and that a solicitation axis would take it. This is the honest
record of a defect rather than its concealment, and the parent edge means a
roll-up over "human-produced" cannot silently lose the elicited half. The
phase-2 widening to animals under protocol (trained reaching tasks, phenotyping)
is unaffected and in fact reads better: the species was never the point, the
specification was.

### Proposed mechanism value set

```
node_id               parents           differentia of production
instrument-captured   -                 a sensor/assay/logger transduced a world state into values
human-authored        -                 a person's or animal's own act or artifact IS the content
elicited              human-authored    that act was produced to a specification the collection supplied
computed              -                 a stated procedure, with no fitted content, determined the values
model-generated       -                 a trained checkpoint stands in the causal chain
provenance-other      -                 a production process none of the above describes
```

`computed`'s **negative test**, which carries the whole disjointness from
`model-generated`: *fails if any parameter that determines the values was
obtained by fitting to data and is not an interpretable named constant.* The
operational form: could the procedure, plus a finite table of named constants,
be applied by a person to check any single value? A tuned climate model: yes
(that is what the code is), so `computed`. A neural-network interatomic
potential: no, the weights are required, so `model-generated`.

`provenance-other` keeps its job and **gains** one: machine-emitted operational
records, which today have nowhere to go because `human-incidental`'s test fails
on them, now land on `instrument-captured` if a logger transduced machine state
— which I think is right and which removes the one case the byproduct-of-operation
fold left genuinely uncovered. That matters for the owner's scheduled revisit:
the count accumulating in `provenance-other` was designated as the evidence for
restoring the folded value, and **this redraw drains that instrument**. If
telemetry becomes `instrument-captured`, `provenance-other` stops measuring
anything about the fold, and the revisit needs a different instrument — most
plausibly the solicitation/collection-channel axis, where "administrative
byproduct" is a channel value, not a production value.

### Migration map from the shipped table

| old value | new mechanism | new referent |
|---|---|---|
| `natural` | `instrument-captured` | `particular` (near-invariably) |
| `human-incidental` | `human-authored`, often **+ `instrument-captured`** | `particular` |
| `elicited` | `elicited` (child of `human-authored`) | `particular` |
| `simulated` | `computed` | `generic`, **but not always** — see §6.1 |
| `constructed` | `computed` | `stipulated` |
| `rule` | `computed` | varies: `particular` for verifiers over real artifacts, `stipulated` for proof checking and game rules |
| `model-generated` | `model-generated` | `generic` when imitating real signal, `stipulated` when trained on a stipulated source |
| `provenance-other` | `provenance-other` | any |

Three facts to read off this table. **One**: `simulated -> generic` is not a
one-to-one rewrite, so the migration cannot be done mechanically — the cases
whose ground truth is the solver rather than a measurement move to
`stipulated`. **Two**: six old values become five, of which one is a declared
child, and the information released is entirely recovered by three referent
values plus `domains`. **Three**: `model-generated`'s referent varies, which is
the first time the axis can say that a pseudo-label corpus and a corpus of
synthetic Dyck strings sampled from a trained model are not the same kind of
object.

---

## 5. The channel problem — not solved, and no axis can solve it

**Not solved.** My design changes its failure mode and shrinks one instance of
it, and I want to claim exactly that and no more.

**What improves.** The `rule` row records that its counts swing from 9/12/4 to
40/~55/37 depending on whether the reward channel is read separately, *because a
game supplies observations by construction and rewards by rule*. Under my value
set that swing **disappears for the game case** — not because the channel is
addressed, but because the two values it swung between have merged: a game's
observations and its rewards are both `computed`, and both `stipulated`. The
channel reading no longer changes either answer. One large documented
instability is eliminated as a side effect of removing a referent test from a
mechanism axis, which is some evidence the split is real.

**What does not improve.** Wherever the channels genuinely differ, the pairing is
lost: a photograph corpus with ordered labels is `{instrument-captured,
elicited}` and `{particular}` with no record of which value belongs to which
channel; a catalogue of constructed candidate structures with solver-computed
energies is `{computed}` and `{stipulated, generic}` with no record of which
half is which; a code-agent environment over real repositories with
verifier rewards is `{human-authored, computed}`.

But the failure mode changes, and the change is strictly in the right direction:
**from a forced wrong value to a lost join.** Today a game forces a choice
between `constructed` and `rule`, and whichever is chosen is a false statement
about half the signal. Under the new set nothing is forced out — every channel's
mechanism and referent appears in the set — and what is missing is the pairing.
A missing join is recoverable by later annotation; a false value is not, and it
is invisible to any coverage check.

**What would solve it, and why it is not an axis.** The brief forbids inventing a
channel axis and is right, for a stronger reason than restraint: **an axis adds
a column, and the defect is in the table's key.** A `channels` axis listing
which channels a source supplies would not let anyone recover which referent
belongs to which channel — the information is in the *pairing*, and no
single-valued-per-source column holds a pairing. The only fix is to re-key the
two entity-level axes to a **(source, signal-role)** pair, with role from a small
closed set — observation/input, target/label, reward, auxiliary — and the project
already has the pattern for it: §4 records `(source, form)` pairs and
`roles_in_run`. Cost is roughly double annotation on both axes, which all three
phase-1 runs also estimated. Anything less than re-keying is cosmetic.

One further observation, free: **self-supervised sources are the case where
re-keying also fails**, because the target *is* the input and there is no second
channel to key on. Two of three phase-1 runs noticed the axis has nothing to say
there. A role-keyed table would record the same value twice and claim to have
said something. That is worth knowing before anyone pays for the re-key.

---

## 6. Where my own tests contradict each other

The most useful part of this report. Six cases, each a place where two tests I
wrote give different answers on the same source.

### 6.1 Numerical PDE benchmarks — `generic` or `stipulated`

The *specification-fixed-from-outside* test says `generic`: the governing
equations are physics and the viscosity has physical units. The *what-could-be-
wrong* test says `stipulated`: the only error in the data is numerical, measured
against the equation's own exact solution, and nobody rejects such a benchmark
because a wind tunnel disagrees. Two of my tests split a whole subfield
(learned PDE surrogates).

My tie-break, stated as a decision and not as a derivation: **ask what the
dataset's own evaluation compares against.** If the ground truth is the solver,
`stipulated`; if it is measurement of the world, `generic`. That puts PDE
benchmarks on `stipulated`, climate runs on `generic` (they are scored against
observations), and quantum-chemistry energy sets on `generic` (they are compared
to experimental values and the field argues about functionals). The consequence
is the one in the migration table: `simulated` does **not** map onto `generic`.

### 6.2 One physics engine, three referents

*Nothing outside is modelled* says the hand-authored locomotion morphology is
`stipulated`. *The engine's parameters have physical units and its contact model
is routinely called unphysical* says `generic`. I broke it by **constitution**
rather than by ambition — were the body's link lengths and torque limits
measured from anything? — which gives `stipulated` for an authored humanoid,
`generic` for a CAD-derived model of a real robot, `particular` for a digital
twin of one deployed machine. The contradiction is not fully dissolved: it
relocates into the granularity requirement, because the entity "the engine"
cannot carry a value at all. See the granularity note in (a).

### 6.3 Preference and annotation data — my test versus the axis's purpose

`particular`'s positive test passes cleanly on a preference dataset: annotator
k's judgement on item j really happened and could be mis-recorded. The brief's
motivating question says a preference dataset is neither a study of the world nor
an exercise on a constructed object. I resolved it by accepting `particular` and
rejecting the gloss (§0) — but the resolution has a price I should not hide: it
makes `particular` the answer for essentially every human-produced and
instrument-captured source, which is uncomfortably close to conceding the scope
predicate I refused. My scope decision and my own value distribution are in
tension. I keep universal scope only because the predicate would have to be
written in terms of provenance values and would re-couple the axes.

### 6.4 A formal-mathematics corpus — the recursion trap, unresolved

My `particular` negative test says transcription fidelity is not a referent, or
every source refers. Applied strictly to a web crawl, that test makes the crawl
`stipulated`, which is plainly wrong — the pages' content was fixed by people
outside the crawl's production. So I added *content fixed outside the source's
own production* as the rescue. Now apply both to a corpus of
machine-checked mathematics: the content was fixed outside (humans wrote it), so
`particular`; and the values' correctness is internal to an axiom system, so
`stipulated`. **Direct contradiction between two of my own tests on one source.**

Multi-valued rescues the record — the corpus is `{particular, stipulated}`, and
honestly so — and this case is why I reversed my single-valued decision. But it
leaves `particular` with the vacuity exposure run A warned about for `natural`,
in the form *every dataset is a real artifact*. The carrier clause is my only
defence and it does not settle this case; a reviewer who wanted to call it
unresolved would be right.

### 6.5 Synthetic-but-realism-claiming sources — a sociological test

A template-generated corpus of vulnerable source code: the code is synthetic, so
`stipulated`; the vulnerability classes are patterns abstracted from real
software and *"these do not look like real bugs"* is the standard criticism, so
`generic`. The two readings differ on whether a realism claim is **in force**,
which is a fact about what a community argues about rather than about the
artifact. Every `generic`/`stipulated` boundary case I could construct turned on
this, which makes it the weakest seam in the design. I did not find a
better test. The partial mitigation is in the positive test — *someone has in
fact tried to validate it against the world* requires evidence rather than
plausibility — and it will leave genuine cases on `unknown`.

### 6.6 Parametric random graphs — entity attachment versus use

Swept parameters give `stipulated`; the same family with parameters **fitted to a
real network** gives `generic`. Same named entity, two values, decided by the
paper. My entity attachment mis-codes one of them, and §4's naming criterion only
saves the case where the fitted variant was named as an artifact — which, for a
graph family, it usually is not. Recorded as a known mis-coding class, not
resolved.

---

## 7. What I would measure, and the one thing I would change first

If I could ask for one measurement after a real annotation pass, it would not be
a count of any value. It would be: **on how many sources does the referent value
set have more than one element, and can the coder name the channel each belongs
to?** The admission rule makes that answerable, and it is a direct measurement of
the channel problem's size — the number that decides whether re-keying to
(source, signal-role) is worth paying for. Every other open item in this report
is downstream of that number.

The one change I would make before anything else, independent of this axis:
**rename `natural`.** The redrawn test is the smaller part of the fix; the word is
the larger part, and a renamed test on an unrenamed value will be coded as the
old one by every reader who skims the row.
