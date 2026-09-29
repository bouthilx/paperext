# Modality / data — depth-2 re-derivation (modality2)

Re-derived from `AXES.md` §6 (with §1, §4, §5, §7, §8b as constraints),
`GRANULARITY_AUDIT.md` D1–D5, `EXTERNAL_DIFF.md`, and the 2055-name /
6123-mention corpus vocabulary. The previous `modality/` derivation was not
read; this is a re-derivation, not a patch.

Level 1 is delivered as §6's eight substantive branches plus §8b's
administrative `uninformative` row. The one change is the rename §6 itself
proposes (`Molecular & biological data` → `Molecular & materials data`),
argued in §4 below. An alternative level 1 is argued in §5 and **not**
adopted.

---

## 1. One principle that fixes D2, D3 and D4 at once

All three of those defects are the same mistake: **a modifier that can be true
or false of a node's siblings was promoted to be one of them.**

- `Video` — temporal extent qualifies tomographic, microscopy and satellite
  imagery too (4D flow MRI, time-lapse microscopy, satellite time series).
- `3D geometry` — dimensionality qualifies tomography and microscopy too.
- `Multilingual text` — language count qualifies prose, dialogue and even code
  comments.
- `Temporal graphs` — dynamism qualifies knowledge graphs, social networks and
  connectomes alike.

**The property test.** *Ask whether the candidate's distinguishing modifier can
be applied to each of its proposed siblings. If it can, it is a property of the
branch, not a member of it.* A property goes to depth 3 (where it qualifies one
node), or to branch level (where it qualifies all of them), or off the axis.

Applied here:

| defect | old sibling | disposal |
|---|---|---|
| D2 | `Video` | depth 3 under `Photographic imagery` — a camera read at a frame rate is the same sensor |
| D2 | `3D geometry` | **survives, renamed**: `Range & 3D scene geometry` is defined by *active ranging / multi-view reconstruction*, a formation process that cannot qualify tomography. The node passes the property test only under that definition; the dimensionality reading does not |
| D3 | `Multilingual text` | branch level (`Language & text` itself) — see §6 below for the facet it really wants |
| D3 | `Conversational language` | depth 3 under `Natural-language text` — register is a genre of a language, not a kind of language |
| D4 | `Temporal graphs` | depth 3 under every graph child |

This also removes D2's admitted two-clause characteristic. Vision now divides
by **one** thing — *how the image was formed: what physical process wrote the
array, and in what coordinate frame* — which is the field's own sense of the
word "modality" (in radiology, an imaging modality **is** the instrument).

D4's remaining half (`what the graph represents`) is replaced by a sharper
single principle: **where the edges come from** — asserted, observed, measured,
or built. That is the graph analogue of "what instrument produced this".

---

## 2. The D5 rule — when may a modality branch divide by the domain the data comes from?

This is the systemic defect and the most important thing in this file. The rule
is not invented; it is **§1's own axis-admission test applied one level down**,
which is precisely the extension AXES.md never states and the hole D5 fell
through.

§1 admits an *axis* when "two papers can differ on it while agreeing on every
other axis". The same test applied to a *child*:

> ### The D5 rule
>
> **Clause 1 — naming.** A modality node is named by the **measurement or
> record process** that produced the signal — the instrument, the sampling
> geometry, the encoding, the assay, the record-keeping practice — and never by
> the field, subject, sector or purpose the data serves.
>
> **Clause 2 — admission (determination test).** A candidate child is admitted
> only if **two papers can carry it and differ on the Scientific discipline /
> Sector axis**. If the child's name *determines* another axis's value, it is
> that axis in disguise; fold it into its structural sibling and recover the
> quantity by cross-tab, not by a node.
>
> **Clause 3 — generality.** Name the node at the **most general level of the
> measurement process that still picks out one signal kind**. This is what
> stops `EEG`, `ECG`, `seismometer` and `radio receiver` becoming four siblings
> and fragmenting the branch along field lines by the back door.
>
> **Stated exception.** Clause 2 may fail *empirically* while clause 1 holds:
> an instrument may happen to have only one user (cryo-EM, brachytherapy
> dosimetry). That is a fact about the world, not a leak, and the node stands,
> **because the leak is a naming fault, not a correlation.** What is forbidden
> is a node whose *definition* mentions a field.

### The rule applied, with the deciding test in each case

| old child | verdict | deciding test |
|---|---|---|
| `Biomedical imagery` | **renamed** → `Tomographic & radiological imaging` | Clause 1: "biomedical" names the ward; "tomographic" names the reconstruction physics. Clause 2 then passes — industrial and materials CT sit in the same node. Dermoscopy and endoscopy correctly leave for `Photographic imagery`: the instrument decides, not the ward |
| `Remote-sensing imagery` | **renamed** → `Multispectral & radar imagery` | Clause 1: named by band structure and georeferencing. Clause 2 passes strongly — forestry, disaster response, agriculture, archaeology, astronomy |
| `Physiological signals` | **dissolved** → `Waveform signals` | Clause 1 fails ("physiological" is a field). Clause 3: the general process is *high-rate transduction where the trace shape is the signal*, which covers EEG, ECG, vibration, seismic and RF. The exception was available (EEG has one user) but clause 3 outranks it — a more general honest node beats a narrower field-shaped one |
| `Environmental time series` | **deleted** | Clause 2 fails by construction: every paper carrying it is Earth/environmental science. A temperature series and a load series are the same signal |
| `Financial time series` | **deleted** | Clause 2 fails hardest. There is also no instrument: a price is a ledger entry, so clause 1 has nothing to name it with. Folded into `Sampled quantity series` |
| `Sensor streams` | **folded** into `Sampled quantity series` | Clause 3: a wearable, an IoT node and a utility meter are one recording process at different labels |
| `Electronic health records` | **renamed** → `Longitudinal administrative records` | Clause 1: the structure that motivated the node (irregular per-subject accumulation, coded vocabularies, censoring) belongs to institutional record-keeping, not to medicine. Clause 2 then passes — claims, registries, student and court records |
| `User interaction records` | **renamed** → `Transactional & interaction logs` | Clause 1 already satisfied ("interaction" is a record process, not a field); only tightened |
| `Multimodal biomedical data` | **deleted** | Clause 1 fails outright. Nothing replaces it: a multimodal child must name its constituent modalities (§6), and "biomedical" names none |
| `Molecular & biological data` (L1) | **renamed** → `Molecular & materials data` | See §4 |

### What the rule costs, stated

Every deletion above removes a reportable number. **None of it is lost.** A
paper on ICU vitals still records `Waveform signals` × `Medical & health
sciences`; a load-forecasting paper records `Sampled quantity series` ×
`Energy & utilities`. Recovering "how much of our time-series work is clinical"
by cross-tab rather than by a node is exactly what §1 buys with the faceted
design, and it is *more* informative, because the cross-tab also answers the
question for branches that never had a clinical child.

---

## 3. D1 and the level-1 verdict on `Molecular & biological data`

**Verdict: the branch survives at level 1, renamed `Molecular & materials
data`. D1's structural objection is rejected; D1's naming objection is
accepted.**

D1's argument was: *structurally, molecules are graphs plus 3D geometry*, so
the branch is a field's data promoted to a signal kind.

Three reasons that fails:

1. **It is a representation argument, and §6 forbids representation as a
   principle of division.** "Molecules are graphs plus 3D geometry" has the same
   form as "images are grids" and "text is a token sequence". Applied
   consistently it dissolves Vision and Language too, which is precisely the
   grid/sequence/graph fusion §6 bans in its first sentence. A structural
   argument cannot be admitted against one branch and refused against the rest.
2. **A molecule is the invariant, not the encoding.** The *same* molecule
   arrives as a bond graph, a 3D conformer, a SMILES string or a fingerprint
   vector, interchangeably, and the research question is unchanged. What is
   stable across those encodings is the signal kind. That is the strongest
   available evidence that it *is* a kind rather than a representation.
3. **It passes the D5 rule, which is the test D1 was reaching for.** Two papers
   carrying `Molecular & crystal structure` differ on discipline routinely —
   catalysis (chemistry), alloys (materials), folding (biology), drug discovery
   (medicine). A field-derived node cannot do that.

What D1 **is** right about is the *name*. `Molecular & biological data` fuses
a material kind with a field word, which breaks the D5 naming clause and also
§9's ban on compound category names — a ban the rest of level 1 does not break,
since `Vision & imaging`, `Speech & audio`, `Graphs & relational` and `Tabular &
structured records` are near-synonym doublets naming one thing, whereas
"molecular" and "biological" name two different things. §6 already proposed the
fix ("the real characteristic is *matter*, not life"). `Molecules and
materials` is the community's own doublet for one thing (the NeurIPS workshop
series, "ML for molecules and materials"), so the compound is licensed.

The rename is not cosmetic: it forces the branch's characteristic to be *a
description of matter — its atoms, its covalent sequence, or the abundance of
its constituents* — which is what admits crystals and alloys without strain and
keeps genomics in (a genome is the covalent composition of a molecule, measured
by an assay), while keeping human text out (an artefact of communication, not a
measurement of matter). That single line is also what routes
`Protein Language Models` here rather than to Language, independently of §8b's
inverted-precedence rule.

---

## 4. Should level 1 change? The alternative, argued and declined

D1's deeper point stands: the eight branches are not one kind of thing. They
divide by three different things — **sensory** (vision, language, audio),
**structural** (graphs, time series, records) and, before the rename,
**domain-derived**.

### The alternative: level 1 by provenance

Make the register explicit and demote the current level 1:

| proposed L1 | principle | would contain |
|---|---|---|
| Perceptual signals | transduced from radiation or pressure reaching a sensor | vision, audio |
| Symbolic artefacts | produced by a human or a machine under a grammar | language |
| Instrumented measurements of matter | produced by a chemical/physical/biochemical assay | molecular & materials |
| Records of relations and events | written down by a system as it operates | graphs, time series, records |
| Cross-modal | a relation over the above | multimodal |

**For it.** It is one principle — *what process produced the signal* — and it is
the *same* principle this derivation uses inside every branch at level 2. The
tree would be principled all the way down, and D1 would be answered rather than
contained.

**Against it, decisively.**

1. **It relocates the axis's reportable quantity.** The survey's headline
   question is "what share of our 2024 output is vision work / language work".
   Under the alternative, `Vision` and `Language` are level-2 rows and the
   level-1 table reads `Perceptual signals 46%`, which answers nobody's
   question. §9 makes depth 2 the deliverable; this proposal spends the whole
   depth budget on a register distinction no reader asked for.
2. **It over-fuses at the top.** `Graphs`, `Time series` and `Records` in one
   branch is a bigger granularity failure than the one it fixes: a connectome, a
   price series and a claims table share only that a system wrote them down.
3. **§6's own ruling forbids the move.** Level 1 divides by "the kind of signal
   **as the field itself distinguishes it**". No research community calls itself
   "perceptual signals". Several call themselves computer vision, NLP, speech,
   graph learning, and molecular ML.
4. **The heterogeneity is now contained rather than ignored.** After the D5 rule
   is applied, **all eight branches pass both of its clauses** — each is named
   by a process or an encoding, and each leaves the discipline axis free. The
   sensory/structural difference is then a difference in *which* process, not a
   second principle. That is a weaker claim than "level 1 is uniform", and it is
   stated as such rather than laundered.

**Verdict: keep §6's level 1, renamed.** Record the register heterogeneity as a
declared, bounded cost, with the containment condition above as the thing to
re-check whenever a branch is added.

One residual level-1 irregularity is *not* repaired and is inherited, as the
granularity audit already noted: **`Multimodal` is a relation over values of
the axis, not a value of it.** The clean fix is a cross-modal *flag* plus the
constituent modality values, not a ninth branch. §6 declares and argues the
branch explicitly, so it stands; but the flag design is the better one and
should be revisited if the extraction ever names observations directly.

---

## 5. Where AXES.md is silent, ambiguous or self-contradictory

1. **Self-contradiction on `Continuous Control` (§6, RL ruling).** The section
   says the RL names "name no signal either. There is nothing to label", and
   four lines later adds the state-vector node "so `Continuous Control` has a
   home". Both cannot be executed. This derivation keeps the node (it is a
   fixed ruling) and reports its support **twice**: 11 names / 24 mentions
   permissively, ~0 under the strict reading. The node is retained by design,
   not by evidence, and `nodes.tsv` says so.
2. **The ban on dividing by mathematical structure is stated for level 1 only.**
   §6's own level-2 lists then divide by it — `video` (temporal), `3D geometry`
   (dimensional), `temporal graphs` (dynamism). Silence about depth. This
   derivation extends the ban downward (§1 above) and declares the extension.
3. **Two rules claim recommender data.** §6 defines Graphs as "natively
   relational data only" and simultaneously routes `Recommender Systems` to
   Tabular > user interaction records. A user–item interaction set *is* natively
   bipartite-relational. AXES.md decides by fiat, not by a test. Test supplied
   here: **a log is written row by row as events occur; a graph is asserted or
   estimated as a relation over a fixed entity set.** Clickstreams and ratings
   are logs. Flagged as low confidence in `nodes.tsv`.
4. **No boundary between `Speech & audio` and `Time series & signals`.** Both
   are 1-D sampled waveforms; only convention separates them, and AXES.md never
   states the convention. Test supplied: *audible acoustic pressure, produced
   to be heard or emitted by a source in air or water* → Audio; everything else
   sampled at waveform rates → Time series.
5. **No boundary between a time-indexed record and a time series.** §6 puts
   proprioceptive state vectors under Tabular, but a state trajectory satisfies
   the Time-series branch's own characteristic. Test supplied: a state *vector*
   (fixed fields, one timestep) → Records; a state *trajectory* analysed as a
   series → Time series.
6. **No residual policy for this axis.** §8 lists it as still to design and §8b
   gives only the uninformative branch. An on-axis, perfectly specific name
   with no child (haptics, olfaction, event cameras) has nowhere to go. Policy
   proposed: **it sits at branch level with a `residual` flag; never create an
   `Other` node**, because `Other` is exactly the kind of name §9 forbids as
   "general enough to attract out-of-scope entries".
7. **No decision procedure for a zero-support node.** "Never balance by count",
   "counts are indicative" and "no corpus support is *possibly speculative,
   justify or keep*" together decide nothing. Rule used here and stated so it
   can be overruled: **keep a zero-support node only if (a) an external
   classification or a standing venue names it AND (b) dropping it would make
   its sibling set's principle non-exhaustive.** `Audio–visual` (0 names) passes
   (b) — a formation-source partition of audio without it is incomplete.
8. **Branch-level residence has no reporting rule that survives this axis's
   numbers.** §8b says depth-2 shares need a denominator naming the
   branch-level bucket. On the measurements here that bucket is **258 of 641**
   on Vision and **323 of 617** on Language: the depth-2 layer describes under
   half of the two largest branches. That is a reporting-design hole, not a
   caveat, and it is the single biggest threat to this axis being useful.
9. **§1's axis-admission test is never stated as applying to children.** That
   silence is the hole D5 fell through, and §2 above is the repair.

---

## 6. Blind spots kept (not filled, declared)

- **Haptic and tactile signals.** `Tactile Sensing`, `Haptics and Tactile
  Interaction`. A real modality with no home; currently absorbed by
  `Sampled quantity series` as transducer telemetry, which is honest but coarse.
- **Chemical / olfactory sensing.** Absent from the corpus and from the tree.
- **Event-camera / neuromorphic vision.** Real externally (`Neuromorphic
  Computing` 2 is about hardware, not the sensor), absent here. It would be a
  genuine sibling under the image-formation principle if it appears.
- **Spectra as a modality** (NMR, IR, Raman, mass spectrometry). Currently split
  between `Omics abundance profiles` and `Waveform signals`. Deliberately *not*
  given a node: the `spectral` surface is measured **89% wrong** on this axis
  (spectral methods, spectral graph theory, scattering transforms), so a node
  named for spectra is a homonym trap. Re-derive only with a disambiguating
  surface.
- **Astronomical imaging** is folded into `Multispectral & radar imagery`
  rather than given its own node. Defensible under clause 3 (a survey telescope
  is a multi-band remote imager), but it is the place where clause 3 is doing
  the most work.
- **Geospatial vector data** (GIS polygons, trajectories, road geometry) has no
  clean home; it is split across `Multispectral & radar imagery` and
  `Physical & engineered networks`.
- **Language coverage as a facet.** Dissolving `Multilingual text` (D3) leaves
  multilingual / cross-lingual / low-resource work measurable only at branch
  level. It passes §1's admission test in its own right — two papers can differ
  on language coverage while agreeing on every other axis — so the correct fix
  is a small *property facet*, not a modality sibling. Recorded as a candidate,
  not proposed here.
- **Classical-AI-shaped data.** `Formal & mathematical notation` gives the
  corpus's unplaceable `Neural-Symbolic Learning` a home and partly answers
  EXTERNAL_DIFF's blind spot 2, but knowledge representation and planning
  remain a Method-axis gap, not a modality one.

---

## 7. Names rejected to other axes, with the deciding test

| surface (mentions) | destination | deciding test |
|---|---|---|
| `Computer Vision` 251, `NLP` 306, `Graph Neural Networks` 81 | **stay, at depth 1** | The name picks the branch and nothing narrower; forcing a leaf invents precision the name does not carry (§8b) |
| `Sequence Modeling` 8, `Sequence-to-Sequence` 2, `Sequential Learning` 2 | Method / Task | The `sequen` trap: 65% of corpus names containing it are not genomics. No node is ever named bare `sequences` |
| `Spectral Methods` 3, `Spectral Graph Theory` 2, `Scattering Transform` 2 | Method / Graphs | The `spectral` trap, 89% wrong |
| `Integer / Stochastic / Constraint / Dynamic / Probabilistic Programming` ~15 | Method | The `programming` trap, 83% wrong. Only `Programming Languages` and `Computer Programming` reach `Source code` |
| `Neural Networks` 19, `Network Pruning`, `Network Compression`, `Bayesian Networks`, `Tensor Networks`, `Network Optimization` | Method | The `Networks` trap: a node named `Networks` would be ~59% wrong by papers, 78% by names |
| `Recurrent Neural Networks` 8, `Transformers` 13, `Attention Mechanisms` 13 | Method > Model design | §5's asymmetry test: used on text, audio and time series alike, so they imply no single modality |
| `Medical Physics` 18, `Brachytherapy` 8, `Radiation Therapy` 7, `Dosimetry` 3 | Scientific discipline | Names a treatment procedure, not an image. The closest thing to a false friend in the tomographic branch |
| `Neuroscience` 84, `Epidemiology` 20, `Astrophysics` 15, `Genetics` 10, `Materials Science` 6 | Scientific discipline | §7: names a field that exists without AI and supplies the problem, not a signal |
| `Recommender Systems` 16 | Task (its datum only → `Transactional & interaction logs`) | §7: fails "exists without AI" and names what the output must be |
| `Reinforcement Learning` 271 and all bare RL names | **no modality value** | §6's RL ruling: interaction is a feedback structure, not a signal. Absence here is correct and is a finding, not a gap |
| `Simulation` 5, `Monte Carlo Simulations` 5 | Method | A data-*generating* process is not a kind of signal; the modality is whatever the simulator emits |
| `State Space Models` 1 | Method | On this corpus the surface is an architecture family, not an observation space. **Newly declared homonym**, alongside AXES.md §8b's list |
| `Graph Signal Processing` 5, `Molecular Graphs` 1, `Protein Language Models` 1 | Graphs / Molecular / Molecular | §8b's inverted precedence on this axis: take the token naming the *signal*, which is the modifier |
| `Vision Science` 2, `Visual Neuroscience` 1, `Visual Perception` 2 | Scientific discipline (+ the recording's modality) | The `vision`/`visual` trap — 29% of names but only 3% of papers, invisible to a paper-level check. Deciding test: **the signal is what was measured, not what was depicted**; a study of the visual cortex measures neural data. Known misassignment in the indicative tally below |
| `Data Analysis` 4, `Data Mining` 2, `Big Data Analytics` | `uninformative` | On-axis (asserts data) but names no kind |
| `Deep Learning` 233, `Machine Learning` 250 | **absent from this axis** | §8b: "no value" is not "uninformative value" |

---

## 8. Granularity audit of this output

Test applied, per `GRANULARITY_AUDIT.md`: *are these the same kind of thing, at
the same level of specificity, and does any sibling exist only because it was
large in this corpus?* Run against every sibling set below. **Nothing here is
justified by its size**; three nodes are kept at 5 names or fewer and one at
zero.

**Passes.**

- *Vision (6)* — one principle (image formation), no volume-driven sibling.
  `Microscopy` (5 names) is kept on the principle, not on volume.
- *Language (3)* — after D3's two removals the set is licensed by grammar type.
- *Audio (3)* — one principle (acoustic source), holds without strain.
- *Graphs (4)* — one principle (edge provenance); D4's dynamism sibling gone.
- *Time series (3)* — one principle (what a sample is); D5's four domain
  children gone.
- *Molecular & materials (3)* — one principle (which description of matter);
  small molecules and protein folds deliberately **not** split, because that
  split would have been the chemistry/structural-biology field boundary.
- *Records (4)* — one principle (what writes a row), with two caveats below.
- *Level 1 (8 + 1 admin)* — passes the D5 rule in all eight branches; the
  register heterogeneity is declared in §4, not laundered.

**Failures and low-confidence sets, declared rather than laundered.**

- **A1 — `Document & screen imagery` (vision).** Its principle names the
  *origin of the depicted content* ("rendered or scanned symbolic material"),
  while its five siblings name *sensing physics*. It is the least well-matched
  member of the set. 5 corpus names. Kept because dropping it makes the
  formation principle non-exhaustive and because ICDAR-style document analysis
  and GUI-agent work are large external communities. **This is a real
  specificity mismatch and I do not claim otherwise.**
- **A2 — `Source code` vs `Formal & mathematical notation` (language).** Source
  code *is* a formal language, so the pair is not a clean partition of a genus
  into species; I partition it by operational versus declarative semantics, a
  cut the field does not routinely make (a Lean development is both). **Low
  confidence.** The fallback is a single `Formal languages` node with both at
  depth 3, which loses the ML4Code community as a reportable row.
- **A3 — `Transactional & interaction logs` vs `Longitudinal administrative
  records` (records).** Both are timestamped per-entity event tables; the cut is
  by *who generates the row* (the user acting, versus the institution
  recording). Defensible but thin, and the first node is additionally claimed by
  the Graphs branch's own reading (§5 item 3). **Low confidence.**
- **A4 — `Multimodal` at level 1.** A relation over values, not a value.
  Inherited from §6, declared, not fixed.
- **A5 — `Physical & engineered networks` (graphs).** Several members
  (`Optimal Power Flow`, `Traffic Signal Control`, `Mobile Networks
  Optimization`) are arguably Method names whose subject is the algorithm, not
  the network as data. The node survives on the ones that are not
  (`Transportation Networks`, `Communication Networks`, `Power Systems`), but
  its measured support is soft.
- **A6 — `Low-dimensional state & proprioceptive vectors` (records).** Retained
  by AXES.md ruling with near-zero support under that same section's strict
  reading. The contradiction is AXES.md's (§5 item 1); the node is honest about
  it.
- **A7 — animal vocalisation** sits under `Environmental sound` while
  `Speech & voice` is defined by a *human* vocal tract. That is a strain in the
  audio principle (the source predicate is not applied uniformly). Small, and
  declared.

**Branching factors.** Level 1: 8 substantive + 1 administrative. Level 2 per
branch: Vision 6 · Language 3 · Audio 3 · Graphs 4 · Time series 3 · Molecular
& materials 3 · Records 4 · Multimodal 3 · Uninformative 0. Mean 3.6 over the
eight substantive branches; max 6. No branch specialises early enough to
trip §9's warning, and no branch has fewer than the two substantive children
§9 requires.

---

## 9. Corpus tallies: what they are and what they are not

The `corpus_names` / `corpus_mentions` columns are **indicative**, produced by
one keyword pass over the 2055-name vocabulary with explicit guards for the
four measured homonym traps (`Networks`, `programming`, `spectral`, `sequen`),
first-match-wins. Roughly 1967 of 6123 mentions land on this axis; 1176 names
take no modality value, which is expected and, per §1 and EXTERNAL_DIFF's
cs.LG 47%, is a finding.

They are **not** a measurement and must not size anything:

- Issue #89: `contributed` and `used` mentions are merged in the source.
- **This axis's Vision figure is the one known to be inflated.** arXiv puts
  cs.CL at ~2.2x the whole vision cluster, while this tally again makes Vision
  (641) larger than Language (617). The tally reproduces the anomaly; it does
  not resolve it. `Computer Vision` is most likely being used as a generic
  descriptor. **No node in this derivation was created, kept, merged or split
  on the basis of its count**, which is why the anomaly is harmless here — but
  it would not be harmless in a report.
- Known misassignments in the pass, left visible rather than hand-corrected:
  the `vision`/`visual` trap puts `Vision Science` and `Visual Neuroscience`
  into `Photographic imagery` (they are discipline names); `Continuous Control`
  and `Embodied AI` are counted although §6's RL rule says they name no signal.
