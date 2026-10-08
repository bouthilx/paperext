# Run D1 — the `referent` axis, and provenance as mechanism

## What I read

Exactly four things, all permitted by the brief:

- `REFERENT_BRIEF.md`
- `METHOD.md`
- `access/nodes.tsv` and `provenance/nodes.tsv` (full files, including their
  header comments and `notes` columns — note that those notes already carry
  phase-2 material: counts, and the names `Juliet Test Suite`, `CFQ`, `CANUE`,
  `IMDB-Wiki`, `ExtremeWeather`, `Neural Latents Benchmark`, `ProteinGym`,
  `Poker Hand`. I used two of them — Neural Latents and the `rule` count swing —
  because they are stated in a file the brief told me to read; if that is
  contamination it is contamination the brief authorised.)
- `SYNTHESIS.md` lines 1–340, i.e. §1–§5. I stopped at the `## 6.` heading.

Not opened: `SYNTHESIS.md` §6, `placements/`, `placement_candidates.tsv`,
`operational_sweep.tsv`, `data_source_names.tsv`, `datasets/v0`, anything under
`paperext-llm-backend/`, and anything in `derivations_referent/` other than this
file. Every source name used below as an example is one I know from the field or
one quoted in the two `nodes.tsv` files.

---

## 0. Where I disagree with the brief, before deriving anything

The brief claims the same split appears three times: `simulated`/`constructed`,
`natural`-expelling-street-signs, and the game's two channels. **Only the first
is a referent problem.** Treating all three as one justifies an axis that
answers two questions — which is the defect this brief exists to repair.

1. **The street-sign defect is an *instigation* defect, not a referent defect.**
   `natural`'s positive test is a conjunction: *(a)* an instrument stands between
   the process and the record, **and** *(b)* "remove every human purpose and the
   process still runs". Clause (b) is not about the subject and not about the
   mechanism — it is about whether the signal would have existed absent the
   intent to record it, which is the same question `human-incidental` versus
   `elicited` turns on. Street signs fail (b) not because their subject is an
   artifact but because a photographic dataset of them exists *because someone
   wanted the dataset*. Delete clause (b) and rename the value and the exemplars
   come back, with no referent value involved. A referent axis does not fix this
   and should not be asked to.
2. **The game is a channel defect** and survives (§3 below).
3. So `referent` has exactly one job: the `simulated`/`constructed` collapse,
   i.e. **answerability**. I derive it for that job alone.

Two further disagreements:

4. **"One mechanism value for *computed by a program*" is right in direction and
   wrong in cardinality.** The computed branch divides cleanly and exhaustively
   on one crisp question — does the producing program contain parameters fitted
   to data? — so `program-computed` should be the **genus**, never a leaf, and
   its two species are `rule`-descended and `model-generated`-descended. The
   superset problem the brief asks me to resolve is not resolved by choosing
   among the three; it is resolved by noticing that one of the three was never a
   sibling.
5. **The reader-facing question the brief offers — *is this a study of the world
   or an exercise on a constructed object* — cannot be answered by this axis**,
   or by any axis on the entity. It is a question about the paper's claim. A
   sim-to-real paper is a study of the world conducted entirely on a
   `stipulated` source; a paper that treats ImageNet as a benchmark number is an
   exercise on a constructed object whose source is `real-particular`. The axis
   answers *what the source is answerable to*. The gap between that and the
   brief's phrasing is permanent and should be stated wherever the axis is
   documented, or every roll-up built on it will be read as something it is not.

---

## 1. The `referent` axis

**Principle of division.** *What, outside the signal itself, could show the
signal's values to be wrong.*

Everything else follows from that. The axis is not about subject matter, not
about realism as a virtue, and not about whether a program was involved. It asks
whether there is an external adjudicator, and if so what kind.

### Scope, cardinality, coding state — decided

- **Applies to every source. No scope predicate.** Two reasons. (i) A
  predicate like "only if computed" would make `referent` a function of
  `provenance`, and `provenance` is multi-valued: a hybrid source (a classical
  solver with a learned closure, a renderer over scanned geometry) would be in
  scope and out of scope at once. (ii) The non-computed branch is not constant:
  **human-authored invented material** — ARC-style hand-built puzzle sets,
  hand-written toy tasks, authored fiction used as a task corpus — is
  non-computed and not answerable to anything real. A scope predicate would
  silently code those as the default.
- **Multi-valued**, for the reason `provenance` is multi-valued: one named
  source can carry channels with different answerability. OC20 is the clean
  case — combinatorially enumerated adsorbate/surface geometries (stipulated)
  with DFT energies answerable to real quantum mechanics (real-general). A
  **singleton is the norm**, and a routine `{real-particular, real-general}`
  coding should be read as channel leakage rather than as a mixed source.
- **`unknown` is a coding state, not a node**, as on both existing axes. One
  sharpening: on `provenance` an empty value set legitimately means "nothing
  applies". On `referent` it almost never can — a signal is answerable to
  something or its construction stipulates its correctness — so **an empty
  referent set should be treated as a coding error, not as data.** Say so in the
  header, or the one statistic worth having here (how often the field states
  what its synthetic data is supposed to resemble) is destroyed by silence.
- **Recorded on the entity**, like `provenance` and for the same criterion from
  §4: it is a property of what the source *is*, not of how a run used it.

### Values

Column order matches `nodes.tsv`: `node_id`, `name`, `characteristic`,
`positive_test`, `negative_test`, `examples`, `notes`.

---

**`real-particular` — Answerable to a particular real system**

- *characteristic*: the values purport to correspond to an identifiable system,
  event or artifact that exists independently of the source, and could be
  checked against it item by item.
- *positive_test*: you can name the thing each item is a record of — this
  patient, this galaxy, this building, this repository, this cluster, this
  person's utterance — and "this item is wrong" means "it does not match that
  thing".
- *negative_test*: fails if no individual can be named and only a class, a
  population or a law is being approximated (`real-general`); fails if the only
  thing an item can contradict is the source's own specification
  (`stipulated`).
- *examples*: SDSS/LSST imaging; fastMRI k-space; MIMIC records; Common Crawl,
  Wikipedia and The Stack; ImageNet photographs and labels; HH-RLHF
  comparisons; Borg and Alibaba cluster traces; HM3D/Gibson laser scans;
  Juliet-style test suites over real code.
- *notes*: this will be the large majority value, which METHOD says is a finding
  and not a defect. It absorbs the whole of the measured and authored branches
  of `provenance` and is therefore nearly implied by them — see §4, defect 6.

**`real-general` — Answerable to a real regularity**

- *characteristic*: the values are produced so as to agree with a real law,
  population or class, but correspond to no identifiable individual;
  "unrealistic" is a meaningful complaint and "that is not patient 4" is not.
- *positive_test*: the source could be shown to be wrong by appeal to
  measurements of the world (experiment, observation, a validated population),
  while no item is a record of any particular thing.
- *negative_test*: fails if an individual real referent can be named
  (`real-particular`); fails if the only available ground truth is the
  generating specification (`stipulated`); fails if "unrealistic" would be
  rejected as a category mistake rather than argued about.
- *examples*: CMIP6 scenario runs; PDEBench solutions of real PDEs on invented
  initial conditions; OC20/ANI-1x DFT energies; a regulated physiological or
  pharmacokinetic simulator; SUMO traffic; CARLA's invented towns; GAN- or
  diffusion-generated "synthetic patients" fitted to a real cohort.
- *notes*: this is the value the brief's regulated-simulator case needs, and the
  value that makes the brief's locomotion case nameable as its opposite. Its
  risk is motivated coding: authors of any simulator would prefer to be here.
  The test is deliberately social — *would the complaint be argued or dismissed*
  — because there is no syntactic property that distinguishes a validated
  engine from an unvalidated one.

**`stipulated` — Correctness fixed by its own construction**

- *characteristic*: whatever ground truth the source has is set by its own
  construction — a grammar, a rule set, an engine's equations as written, or an
  author's stipulation — and nothing outside it can contradict it.
- *positive_test*: the construction *is* the ground truth; a disagreement can
  only be a bug, never a discrepancy with the world; "this is unrealistic" is
  not a defect report because nothing was being resembled.
- *negative_test*: fails if an external measurement could adjudicate
  (`real-*`); note that having physical *units*, a solver, or a name borrowed
  from physics does not create an external adjudicator.
- *examples*: Dyck-k, PCFG and modular-arithmetic string sets; dSprites and
  Shapes3D; BBOB; random k-SAT families; Erdős–Rényi graphs; Go and chess
  terminal outcomes; a rigid-body locomotion task approximating no animal;
  hand-authored puzzle sets.
- *notes*: holds of authored as well as computed sources, which is why there is
  no scope predicate. The phrase "with physical units" is explicitly **not** a
  test — the brief's locomotion case is the demonstration.

**`referent-other` — Other answerability**

- *characteristic*: an answerability relation none of the above describes.
- *positive_test*: a reviewer can state what the signal is answerable to and why
  no value fits.
- *negative_test*: not the case where the paper does not say — that is the
  `unknown` coding state.
- *examples*: none named on purpose.
- *notes*: exists so an ontological miss is recorded as a miss, per the 3/3
  convention in §1 of the synthesis. The live candidate is a source whose
  referent is *itself contested as the research question* (sim-to-real transfer
  studies), which I deliberately did not make a value — see §4, defect 2.

**A fourth value I derived and then killed.** My first cut had
`self-constituting`: the signal *is* the object, so fidelity does not apply
(Wikipedia text, a click log, a preference label). Its own test destroyed it in
two directions at once. A Wikipedia dump is answerable to the actual pages — a
truncated page is a wrong item — so it is `real-particular`; an authored puzzle's
grids are fixed by the author, so it is `stipulated`. Nothing was left in the
middle. What made the value feel real was *use*: nobody studying a web corpus
cares whether it matches the pages. Use-dependence cannot live on an entity-level
axis (§3 of the synthesis, 3/3, for `access`), so the value had to go. Recorded
because the next derivation will reach for it too.

---

## 2. The consequent mechanism set for `provenance`

### 2a. The superset problem among `rule`, `model-generated`, `program-computed`

**Resolution: the superset is the genus, and the two others are its exhaustive
species.** `program-computed` does not become a value.

| node | status |
|---|---|
| `computed` | **non-leaf genus**, never assigned directly; exists for roll-up |
| `rule-computed` | leaf — the producing program has no parameters fitted to data |
| `model-computed` | leaf — the producing program has parameters fitted to data |

- `simulated` and `constructed` **both collapse into `rule-computed`**, not into
  a new value. Their mechanism was always identical; their differentia was
  entirely answerability, which is now `referent`. MuJoCo, PDEBench, CMIP6,
  DFT, dSprites, Dyck-k, BBOB, a renderer and a game's reward function are one
  mechanism.
- `model-generated` becomes `model-computed`, unchanged in substance.
- The division is **exhaustive and exclusive on a crisp property of the
  producer**, so no superset remains. Hybrid producers (a learned closure inside
  a classical solver, a neural PDE emulator, a learned reward model inside a
  verifier harness) carry both leaves, which `provenance`'s multi-valuedness
  already permits.
- **`rule`'s positive test must be replaced.** As written — "a person could
  check the signal by applying a written rule" — it is false of every long
  numerical integration, so the existing test *rejects* precisely the sources
  the collapse assigns to it. The correct test is about the producer's
  constitution: **no parameter in the producing program was fitted to data.**
  That is checkable, learned-vs-not is the only thing that actually varies, and
  it does not care how many FLOPs the rule took to apply.
- Consequence for the name: with the test fixed, "rule" is the wrong word for a
  10^8-cell CFD run. Hence `rule-computed` under a `computed` genus, rather than
  keeping `rule`. If the owner prefers a flat axis with no non-leaf nodes, the
  two leaves stand alone and the only loss is a cheap roll-up.

**One concrete thing this fixes.** `rule`'s note records its live problem as a
count swing — 9/12/4 firm, 40/~55/37 under a reward-channel reading, because a
game supplies observations by construction and rewards by rule. **Under the
collapse that swing is gone**: a game's observations are `rule-computed` by the
renderer and its rewards are `rule-computed` by the rule, so the source carries
`{rule-computed}` on either reading. The number stops depending on an
unresolved question. The *expressivity* loss underneath it does not go away —
§3.

### 2b. `natural` versus `human-incidental`

**Neither is a mechanism value.** The boundary cannot be drawn on mechanism
because both values are already composites of three independent facts, and they
differ on two of them at once:

| | mechanism | referent | instigation |
|---|---|---|---|
| `natural` | transduced | a real system | existed anyway |
| `human-incidental` | authored | a real artifact | existed anyway |
| `elicited` | authored **or** transduced | a real system | brought into being by the collection |

So the honest answer is: **factor, or accept that provenance stays
half-mechanism.** I give both, and recommend the minimal one.

**Minimal patch (recommended).** Two edits, no new axis, no value lost:

1. **Rename `natural` → `measured`** and **delete clause (b) of its positive
   test** ("remove every human purpose and the process still runs"). New test:
   *the values are not entailed by the recording apparatus's specification plus
   its inputs — they depend on a state of affairs the apparatus did not fix —
   and the apparatus's own characteristics (calibration, resolution, noise) are
   properties of the data.* Keep the negative test's intent but invert its
   conclusion: an instrument reading of a human artifact **is** `measured`,
   because the instrument is where the values come from even though the subject
   is an artifact. What the subject is now lives on `referent`.
2. Leave `human-incidental` and `elicited` as they are, with a recorded category
   error (below).

Three things this buys, all of them cases the current table concedes:

- The **street-sign** exemplars return (the brief's case).
- **Machine telemetry leaves `provenance-other`.** A Borg trace is a counter
  reading a running system: the values are not entailed by the recording code's
  spec, so it is `measured`, with `referent = real-particular`. The whole
  argument for routing it to `provenance-other` was that no *human* activity
  produced it — which is only an argument if `natural` means "nature". It stops
  being one the moment the value means "measured". This also means the
  measurement the owner scheduled — *the count that lands in `provenance-other`
  decides whether the byproduct value is restored* — is **destroyed by this
  change**, because its intended population moves. That must be said out loud
  before the change ships, and the revisit re-specified: the evidence for
  restoring a byproduct value is now whichever `human-incidental` placements
  read as strained, not a count in `provenance-other`.
- **Neural Latents stops needing an override.** Macaque recordings during a
  trained reaching task are `{measured, elicited}` — the recording is an
  instrument reading, the behaviour was asked for. Runs A and B could not place
  it without overriding a test precisely because `elicited` as written must
  carry both the mechanism and the asking.
- Bonus: `provenance-other`'s stated hard candidate, an analog or quantum device
  whose output is "both computed and measured", resolves to `measured` with
  `referent = stipulated` — measured because the values are not entailed by the
  problem spec, stipulated because the problem is.

**What the minimal patch does not fix, stated precisely.** `elicited` remains an
instigation fact wearing a mechanism value's clothes, so:

- a source is `{measured, elicited}` or `{human-incidental}` where the honest
  coding is a mechanism *and* an instigation value, and the two-valued set
  cannot distinguish "measured, and asked for" from "measured, and also
  separately authored";
- `human-incidental`'s differentia ("collected afterwards") and `measured`'s
  differentia (an instrument) are on different axes, so the two values are not
  alternatives and the header's warning that "both values hold of both" (fastMRI
  and MIMIC) is permanent rather than a corner case;
- the fold of the byproduct cases into `human-incidental` is a fold of
  *instigation-alike* cases into a value whose other half is mechanism, which is
  why it felt lossy.

**Consistent patch (not recommended for #102).** Mechanism becomes four leaves —
`measured`, `authored`, `rule-computed`, `model-computed` — plus
`provenance-other`; subject-kind moves to `referent`; and an **instigation**
fact (`found` / `elicited`) is required to carry what `elicited` and
`human-incidental`'s "afterwards" clause now carry. I do not propose shipping
it, for one reason that is not conservatism: `elicited` is a **3/3 phase-1
result**, the strongest evidence this method produces, and METHOD forbids
deleting it on an argument. So I record a **deadlock**: `elicited` cannot be
removed (METHOD) and cannot be kept coherently (the mechanism reading), and the
cost of the deadlock is exactly Neural Latents — which the minimal patch
mitigates by letting `measured` co-occur, without resolving.

### Amended `provenance`, minimal patch

| node_id | characteristic |
|---|---|
| `measured` | transduced from a state of affairs the apparatus did not fix; the apparatus's characteristics are part of the data |
| `human-incidental` | human activity or artifacts produced for the actors' own purposes and collected afterwards (unchanged) |
| `elicited` | the signal exists because the collection asked (unchanged) |
| `computed` | **non-leaf** — a program derived the values |
| `computed`/`rule-computed` | the producing program has no parameters fitted to data |
| `computed`/`model-computed` | the producing program has parameters fitted to data |
| `provenance-other` | unchanged in role, emptier in fact |

Deleted: `natural` (renamed and retested), `simulated`, `constructed`, `rule`,
`model-generated` (the last two renamed). Count unchanged at six leaves.

**Migration is not a rename.** Any placement already carrying `simulated` or
`constructed` must be **re-derived, not mapped**: the old value recorded a
mechanism *and* an answerability claim, and only the mechanism half survives, so
a mechanical rewrite to `rule-computed` silently discards the referent and
leaves it `unknown` with no marker saying it was once stated. §5 declared the
axis frozen; this unfreezes it, and that cost is real.

---

## 3. The channel problem

**Not solved. One symptom of it is cured; the problem is untouched.**

Cured: the `rule` count swing (§2a) — a game is `{rule-computed}` whichever
channel you read, so the statistic stops depending on an open question.

Untouched, and I can name where it now shows up:

- **Referent inherits it.** OC20 carries `{stipulated, real-general}` with no
  way to say the geometries are stipulated and the energies real-general. Any
  source whose inputs and targets differ in answerability lands in a mixed set.
- **The RL case gets worse, not better.** Observations rule-computed by a
  simulator and rewards emitted by a *learned* reward model now give
  `{rule-computed, model-computed}` — the right set, with the expensive half
  (the reward model) unrecoverable. The 2/3 tension "RL reward provenance is
  invisible" is unchanged, and the collapse makes the two channels *harder* to
  tell apart on the observation side because `constructed` no longer marks one
  of them by accident.
- **Self-supervised sources** still have no second origin to record, so the
  axis has nothing to say about them — unchanged.

**What would solve it**, with no new axis invented: make the annotated unit
`(source, channel)` rather than `source`, with channel in
{input, target, reward}, as all three phase-1 runs independently proposed. §3
prices that at roughly double annotation. A cheaper variant worth considering,
because it pays only where the cost is incurred: **require a channel qualifier
only when a value set has more than one member.** Multi-member sets are exactly
the sources where the ambiguity exists, singletons are the majority, and the
qualifier is then a disambiguator on an existing field rather than a new axis
multiplying every row. I am not proposing it as part of this derivation — it is
the fix I would test first.

---

## 4. Where my own tests contradicted each other

The seven I actually hit, in rough order of how much they threaten the design.

1. **`rule`'s old test rejects the sources the collapse hands it.** "A person
   could check it by applying a written rule" is false of CMIP6 or a DFT run, so
   my first draft concluded `simulated` was irreducible and the brief's adopted
   fix was wrong. Resolved by replacing the test with the fitted-parameters
   criterion — which then admits sources nobody would call "a rule", forcing the
   rename. The contradiction was in the test, not in the collapse, but it took a
   round trip to see.
2. **The fourth referent value died from both ends** (above). Worse, the same
   test gives opposite answers on one source depending on what you take the
   source to be: a corpus of authored fiction is `real-particular` as a record
   of the actual texts and `stipulated` as a set of task instances. That is
   use-dependence, which an entity-level axis cannot represent. **Unresolved**;
   it is the axis's weakest region and `referent-other` is not a hiding place
   for it.
3. **Model-generated content has no stable referent.** Cosmopedia is
   `real-general` under the direct test (synthetic textbooks purport to convey
   real facts, and "it hallucinates" is an argued complaint) and `stipulated`
   under the reading that a sampled corpus resembles only its training
   distribution. I tried a tie-break — referent flows through `derived_from`,
   reusing the shipped inheritance rule — and **it contradicts the direct test
   on exactly the sources it was invented for**: inheriting from web text makes
   Cosmopedia `real-particular`, which is plainly wrong since no item records
   any page. I kept the direct test and left the instability flagged. Anyone
   building a "how much synthetic data" roll-up should expect this column to be
   unstable for `model-computed` sources.
4. **Habitat moves rather than resolves.** `{real-particular}` by the
   identifiable-system test on the HM3D scans; `{stipulated}` by the
   can-an-item-be-wrong test on the rendered frames, which can only be wrong
   relative to the renderer. The answer depends on my own single-vs-multi
   decision. The hard case the current table flags on `simulated`/`constructed`
   becomes a referent-cardinality case. Progress — the mechanism is now
   unambiguous — but not a solution.
5. **My `measured` redefinition re-opens run A's vacuity warning.** If
   "measured" means "values not entailed by the recorder's spec", every HTTP
   fetch in a web crawl qualifies and `measured` swallows `human-incidental`. I
   patched it with the clause *the apparatus's characteristics are properties of
   the data* — but that is not a mechanism clause, it is the very move the
   current `natural` note already confesses to ("the test appeals to whether the
   capture pipeline is part of the source's identity"). **The vacuity is
   relocated, not cured.** A spectrogram of speech is the live case:
   `{measured, human-incidental}` is defensible and so is `{human-incidental}`
   alone.
6. **I argued both sides of the scope predicate.** Against: a predicate makes
   `referent` a function of a multi-valued `provenance`, so hybrids are in and
   out of scope at once. For: off the computed branch the value is nearly always
   `real-particular`, which is the standard argument *for* a predicate — and
   §1's own value, `real-particular`, concedes it is "nearly implied" by
   `measured`/`human-incidental`/`elicited`. I chose no predicate on the
   independence ground and accept the annotation cost. If a coder-time measure
   later shows the non-computed branch is 100% `real-particular`, the honest fix
   is a **default with an override**, not a scope predicate.
7. **The `elicited` deadlock** (§2b): protected by METHOD's 3/3 rule, incoherent
   under the mechanism reading. I recorded it rather than breaking either.

## 5. One prediction, so it can be checked against me

If the minimal patch ships, the coding error I expect to dominate is
**`real-general` claimed for `stipulated` sources** — a simulator with physical
units and a solver reads as "about the real world" to anyone who has not read
the negative test. It is the same error shape as the predicted `access`-as-
openness mis-coding (3/3, §3), and the same remedy applies: the value's name
should not contain the word "real" if that can be avoided. I kept it for
parallelism with `real-particular` and I am not confident that was right.
