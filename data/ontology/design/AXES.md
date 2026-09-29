# Domains base ontology: axis design

Iterative design with the owner, 2026-09-25. Supersedes the single-tree vs
multi-axis question left open by the 3-agent experiment (`run{1,2,3}/`).

Decisions below are **locked** unless marked open. Nodes are derived in a second
pass; this file fixes the *principles of division*, not the node lists.

## 1. Structure: axes, and each axis is its own dimension

The base ontology is **faceted**, not a single tree. Each axis is its own
ontology with its own surface map, the way `models` and `domains` are dimensions
today (`load_dimension_cut(dimension)`). The same raw name is mapped
independently in each axis, which is what lets `Image Classification` reach
Modality > Vision *and* Task > Classification without a multi-target mapping.

Cost, stated up front: the 2055-name vocabulary is mapped once per axis, so the
mapping pass is ~5x a single tree (~8,200 decisions, matching run1's estimate).

A property earns an axis if **two papers can differ on it while agreeing on
every other axis**.

**Corpus counts in this file are indicative, not measured.** They merge
`contributed` and `used` mentions, a distinction the schema does not yet carry
(issue #89). Measured on the 1999-paper corpus: application domains skew
*contributed* (software engineering 79% primary, medical imaging 77%) while
methods skew *used* (transfer learning 10%, self-supervised 22%). arXiv
independently suggests the Vision branch is inflated -- `cs.CL` is ~2.2x the
whole vision cluster there, while our name counts make Vision larger than
Language. Do not treat any per-branch size here as a finding.

| axis | question | mandatory? |
|---|---|---|
| Method | how does the work produce its result? | near-mandatory |
| Modality / data | what does it operate on? | near-mandatory |
| Task | what is the system asked to do? | optional (see 5) |
| Application domain | what outside field does it serve? | optional |
| Desired properties | what property of the AI system does it try to secure? | optional |

**Optional axes may be empty, and that is a finding, not a coverage failure.**
Declaring this is what stops an annotator inventing a value to fill a blank --
the defect that gave run1 55/55/80% `Not Specified` and made it look broken.

Rejected as axes:
- **Contribution type** (new method / benchmark / evaluation study). It is a
  property of the paper, not a domain the paper is in. This is where run1's
  `Evaluation` belongs -- outside this ontology.
- **Architecture**. Not a research domain in its own right; see 6.

## 2. Desired properties

*What property of the AI system does this work try to secure?*

Positive test: a **demand that can be met or failed**. Naming test: the
community calls these `<Adjective> AI` -- Green AI, Explainable AI, Trustworthy
AI, Frugal AI. `Renewable Energy Forecasting` is not an adjective on AI and is
an application domain.

The normative clause is what excludes `Machine Learning Theory` (descriptive,
not a demand) and `Benchmarking` (an activity, not a property).

Sharper line, after the generalization question (F9): **Desired properties are
demands made on the research from outside it**. The axis is **exogenous, not
normative** -- those two predicates disagree on exactly one node, and
explainability is epistemic in content yet demanded in statute by regulators,
clinicians and applicants, so the exogenous test is the operative one. Where
this file said "normative", read "exogenous" (properties-axis derivation, D-P3).
The same cut sends `Mechanistic Interpretability` to Method > Model design:
circuit-level reverse-engineering has no outside claimant -- by society, by deployment, by
a budget. **Questions the field asks about its own learning machinery**
(generalization, sample complexity, expressivity, scaling) belong to
Method > Learning theory & generalization. Nobody outside the field demands
compositional generalization; it is an epistemic question about learning. This
keeps the axis normative and small rather than admitting an epistemic
sub-branch.

| L1 | children | corpus |
|---|---|---|
| Trustworthy AI | fairness, robustness, explainability, privacy, safety, accountability (single-concept names; the earlier compound spellings broke §9's own rule) | ~296 mentions |
| Frugal AI | computational cost, hardware cost, energy cost | **~27** -- the ~85 in an earlier draft double-counted the 33 mentions of compression techniques that §3 gives to Method, plus the sample/parameter-efficiency names §2 excludes. True ratio to Trustworthy is ~11:1, not 3.5:1. Reported, never engineered away |

**Why this is not folded into Application domain** (owner asked; three reasons):
1. The corpus contains the collision. `Renewable Energy Forecasting`,
   `Energy Storage`, `Energy Systems`, `Greenhouse Gas Emissions Analysis`
   (applying ML to a sector) vs `Green AI`, `Efficient Deep Learning`,
   `Model Efficiency`, `Communication Efficiency` (the energy cost of ML
   itself). One `Energy` branch fuses them. The corpus even has
   `Environmental Sustainability and Artificial Intelligence` pre-fused.
2. The headline table stops being one quantity: `Healthcare 16% ·
   Frugal AI 1.5%` mixes fields served with properties pursued.
3. It kills the cross-tab you most want -- "12% of our health work raises a
   fairness concern".

Discriminating test: an application domain is a field that **exists without
AI**. A desired property is reflexive -- the object of study is the AI system.

Honest counterweight: AI Safety/Ethics/FAccT are real communities with their own
venues, and `Explainable AI` sits on the line. A defensible fallback is three
axes with "the AI system itself" as a top-level *value* of Application domain;
that fixes (1) but not (2).

### Two rules the surface map needs (properties-axis derivation)

- **Technique names, at name level.** §2's original rule was paper-level ("a
  quantization paper gets Frugal AI *when its point is energy cost*"), which no
  annotator can apply to a surface map. Name-level form: **a technique name maps
  to this axis only when the technique has no purpose other than securing the
  property.** `Differential Privacy`, `Adversarial Training`, `Safe RL` pass;
  `Quantization`, `Pruning`, `Distillation`, `Compression` fail and stay
  Method-only.
- **A property node requires a demand-register surface**, not only a
  machinery-register one. This is what declines a `Reliability` node: `Reliable
  AI` and `Dependable AI` occur zero times in the corpus, while what does occur
  (`Uncertainty Estimation`, `Neural Network Verification`, calibration,
  conformal prediction, ~34 mentions) is machinery §3 already routes to Method.
  Admitting it would import Method into the axis -- the absorption failure this
  axis has twice had. Re-derive if extraction is ever asked about deployment
  requirements.

### Frugal AI scope (owner, locked)

- Frugal AI = **compute, time, energy, hardware** cost.
- **Methods stay in the method tree.** `Quantization`, `Knowledge Distillation`,
  `Model Pruning`, `Model Compression` (33 mentions) are Method values. A
  quantization paper gets Method = Quantization *and*, when its point is energy
  cost, Desired property = Frugal AI. This statement is only expressible with
  axes -- in a single tree you would have to pick one and lose the other. It is
  the strongest argument in the thread for the faceted design.
- `Sample Efficiency` (data) and `Parameter-Efficient Fine-Tuning` (parameters)
  are **not** Frugal AI under this definition; PEFT is a Method name anyway.

## 3. Method

Method is not one characteristic. `Self-Supervised Learning` and
`Federated Learning` are not two values of one thing -- federated training can
be self-supervised -- and neither is a sibling of `Optimization`. Three
orthogonal things under one word is the fusion that produced v0's `X and Y`
nodes.

Level 1 divides by **which aspect of the method the name picks out**:

| L1 | characteristic | children | corpus |
|---|---|---|---|
| Learning signal | what feedback drives learning | reinforcement (263 + deep 34 + MARL 14 + model-based 14 + imitation 14), self-supervised (73) + contrastive (21), supervised (10), unsupervised (10), semi/weakly-supervised | ~460 |
| Training regime | how training is organised across tasks, time and agents | transfer (42), continual (29), meta (26), federated (24), multi-task (19), few-shot (14), curriculum, online | ~170 |
| Computational machinery | which formal structure the machinery exploits (plus `Inference procedures` by owner ruling -- see below) | optimization (71), combinatorial (17), stochastic (10), first-order methods, Bayesian inference (19), variational, MCMC, game theory (20) | ~160 |
| Model design | what structure computes the function, **and at what cost** | architecture-as-topic, NAS (6), inductive biases, `Geometric Deep Learning` (11); efficiency techniques as a depth-2 family -- pruning (7+5), compression (9), distillation (8), quantization | ~90 |
| Model analysis | what is established about a model that already exists | expressive power, `Deep Learning Theory` (7), model interpretation (~65), adversarial machine learning (~64), formal verification (19) | ~155 |
| Learning theory | which property of learning is bounded | `Machine Learning Theory` 8, `Out-of-Distribution Generalization` 5, `Domain Generalization` 4, `Generalization` 3, `Sample Complexity`, `Scaling Laws`, compositional/systematic generalization | ~35 |
| Data curation | which part of the training set is acted on -- inputs, composition, labels | data augmentation (11), active learning (9), label cleaning, noisy labels | ~30 |

`Data curation & supervision quality` was added after the tail validation
(`TAIL_VALIDATION.md` F2); it also settles `Data Augmentation` -- data curation,
not a training regime.

**Model analysis was split off from Model design** (owner, 2026-09-28): once the
interpretability and adversarial *methods* arrived (see below), the branch
answered four questions at once and its characteristic had become "what
structure computes the function **and at what cost**" -- the `X and Y` fusion
moved out of the node name and into the principle. Design and transformation
stay together, since designing-against-a-cost-objective is exactly the owner's
rationale; explaining, verifying and attacking an existing model is a different
question.

**The "methods stay in the method tree" rule generalises beyond Frugal AI**
(method-axis derivation D2): interpretability (~65), adversarial robustness
(~64), privacy (~27) and fairness interventions (~15) are techniques and need
Method homes, or a paper proposing a new interpretability method records
Desired property = Interpretability and Method = nothing.

**Efficiency techniques are a depth-2 family under Model design**,
not a sixth aspect (owner, 2026-09-25): you design models against different
objectives -- better accuracy, lower cost, lower latency -- so pruning and
quantization are design with a different goal, and the aspect's characteristic
carries "and at what cost" to keep post-hoc compression in scope.

**`Causal Inference` (16) is Method** (owner). Both machinery and foundations
live in Method -- `Inference & optimization` and `Learning theory &
generalization` are two of its aspects -- and causal inference is inference:
identification, estimators, do-calculus. It earns a depth-2 family under
Inference & optimization with causal discovery, effect estimation and
`Causal Representation Learning` (8) beneath it.

### `Inference procedures` (owner ruling, 2026-09-29)

`Prompt Engineering` (6), `Chain-of-Thought` (1) and test-time computation go
under **Computational machinery** -- the branch formerly named `Inference &
optimization`, which is where the owner's "Inference" points.

**Declared strain**: this sibling divides by *stage* (when the computation
happens) while its siblings divide by *formal structure*, which is defect M5
re-entering by ruling rather than by accident. Two ways to discharge it, neither
taken yet: restate the branch characteristic as "which procedure computes the
answer" (covers optimization, probabilistic inference, search, planning and
prompting alike, at the cost of precision), or accept it as a declared exception.
It is the weakest sibling set on the axis and should be revisited if the
2023-2026 re-extraction makes it large.

### Known defects, to fix in the re-derivation

`GRANULARITY_AUDIT.md` M1-M7. The worst: **`Inference & optimization` mixes four
principles** -- by variable type (continuous/combinatorial), by inferential
framework (probabilistic/causal/game theory), by **problem class**
(`Sequential decision-making`, which is a formulation, not machinery, and
overlaps RL), and by **stage** (`Inference-time methods`, which divides by
*when* computation happens). Also: `Learning theory` is a kind of *claim* among
five pipeline stages -- ACM CCS independently files learning theory under
`Theory of computation`, not under Computing methodologies.

### Blind spots confirmed by two independent sources (`EXTERNAL_DIFF.md`)

ACM CCS 2012 and arXiv primary categories agree on three holes that neither the
corpus nor a corpus-derived structure could surface:

1. **Evolutionary / bio-inspired computation** -- genetic algorithms, genetic
   programming, artificial life. Nothing on any axis. (ACM `Bio-inspired
   approaches`; arXiv `cs.NE`.)
2. **Logical, relational and inductive-logic learning** -- nothing; the first
   derivation already reported `Neural-Symbolic Learning` as unplaceable.
   (ACM subtree; arXiv `cs.LO`.)
3. **Classical AI beyond learning** -- knowledge representation & reasoning,
   planning & scheduling, search methodologies. **Our Method axis is ML-shaped,
   not AI-shaped.** Largest gap; invisible from a 2024 single-institute corpus.

Note ACM CCS itself fails our granularity audit (`Supervised learning`,
`Machine learning approaches`, `Machine learning algorithms` and `Markov
decision processes` are siblings), so it supplies **vocabulary and breadth**,
never arbitration. Where we diverge because we are newer -- `Data curation`,
`Model efficiency techniques`, both postdating CCS 2012 -- that is not a defect.

## 4. Task (accepted; extraction deferred)

Discriminating test, which resolves the task/method collision:
**a term is a task if it names what the output must be, a method if it names
how the output is produced.**

Checks: `Anomaly Detection` (20) -> task. `Supervised Learning` -> method (names
the supervision signal). `Reinforcement Learning` -> method (names the
feedback); its task is control. `Question Answering` (14) -> task.
Two consequences: `Representation Learning` (56) becomes a **task**, and
`Generative Models` (83) stays an architecture while `Image Generation` is a
task.

**Clarification (method-axis derivation, D6):** the "do not map to both to
hedge" rule in §5 is a **within-axis** rule -- one name, one node, per axis.
Mapping the same name in *different* axes is not hedging, it is the design:
`Diffusion Models` is Method > generative models AND Task > Generation, exactly
as a quantization paper is Method > Quantization AND Desired property > Frugal
AI. §5's translation rule governs what an architecture name contributes to
Modality and Task; it never meant Method records nothing.

Task x modality correlation is fine -- that cross-product is informative and it
decomposes compound names (`Image Classification` = Vision x Classification, so
no node needs both words). Task x method collision is the real one, and the test
above settles it.

**Blocker is data, not design.** Task words appear in ~180 names / ~420
mentions; even assuming no overlap that caps Task at 21% of papers, realistically
~15%, because a paper names its *domain* when asked for research domains, not
its task. Getting `classification vs regression` counts needs the extractor
asked for the task directly -- a schema and re-extraction change, decidable
after depth-2 lands without invalidating any of this.

## 5. Architecture names: translate, don't drop

All three design runs said "quarantine architecture names". That is wrong.
The owner's counterexample: a theoretical paper *about* an architecture trains
nothing, so the models dimension -- which asks what the paper **used** -- never
records it. Drop the name and the paper's topic vanishes from the survey
entirely. Those papers concentrate exactly where a bare architecture name is
given, which is where a quarantine rule bites hardest.

Asymmetry test for which way to route: **does translating lose information that
nothing else recovers?** A GNN-applied-to-molecules paper carries ~3 names and
will also say `Molecular Modeling`, so translating costs nothing. A paper on
attention expressivity may carry only `Transformers` and `Machine Learning
Theory`.

| case | destination | examples |
|---|---|---|
| implies a modality or task (reading holds either way -- GNN expressivity theory is still graph learning) | translate | `Graph Neural Networks` 76 -> Modality > Graphs; `Diffusion Models` 13 -> Task > Generation; `Vision Transformers` -> Modality > Vision |
| implies neither | Method > Model design & analysis | `Recurrent Neural Networks` 8 (used on text, audio and time series alike, so it implies no single modality -- corrected after tail validation), `Transformers` 13+8, `Attention Mechanisms` 13, `Neural Architecture Search` 6, `Deep Learning Theory` 7, `Geometric Deep Learning` 11, `Neural Network Verification` 5 |
| carries nothing | uninformative branch, reported as a line, excluded from area shares | `Deep Learning` 177, `Neural Networks` 19, `Artificial Neural Networks` 4, `Machine Learning` 249, `Artificial Intelligence` 15 |

Do **not** map `Graph Neural Networks` to both Graphs and Model design to hedge:
the modality reading is certain, the architecture-research reading is not, and
hedging would inflate architecture research by ~76 mostly-applied papers.

## 6. Modality / data

*What kind of signal does it operate on?* Level 1 divides by **the kind of
signal as the field itself distinguishes it** -- explicitly NOT by mathematical
structure, since grid/sequence/graph would fuse text with time series and
images with video.

| L1 | children | corpus |
|---|---|---|
| Vision & imaging | natural imagery, video, 3D geometry, biomedical imagery, remote-sensing imagery, document imagery | ~563 |
| Language & text | written text, conversational language, source code, multilingual text | ~522 |
| Speech & audio | speech, music, environmental sound | ~46 |
| Graphs & relational | knowledge graphs, social & information networks, temporal graphs. **Reading: natively relational data only** -- "anything encodable as a graph" would swallow molecules, meshes and point clouds, contradicting this section's own ban on dividing by mathematical structure | ~161 incl. translated GNN |
| Time series & signals | physiological signals, sensor streams, environmental time series, financial time series | ~80 |
| Molecular & materials data | small molecules, proteins, **genomic sequences** (never bare `sequences` -- 65% of corpus names containing `sequen` are Sequence Modeling / Seq2Seq), omics profiles, materials. Proposed rename: the real characteristic is *matter*, not life, since this branch holds crystals and alloys | ~306 |
| Tabular & structured records | tabular feature data, electronic health records, user interaction records | **~34, not 1** -- the earlier figure was an artefact: §7 sends `Recommender Systems` (16+7 variants) to Task and never states its modality. Routed here to user interaction records |
| Multimodal | vision-language, audio-visual (0 corpus names, community real -- kept), multimodal biomedical data, sensor fusion | ~60 |

**Note on this table's children column** (modality derivation, defect 1): an
earlier version listed Task-axis names here -- machine translation, QA, language
modeling, ASR, forecasting, link prediction. Obeyed literally that rebuilds the
task/modality fusion §4 exists to prevent. Children divide by **kind of
signal**; task names in a modality row are volume evidence only.

### The D5 rule -- when a modality node may mention a field (never)

§1's admission test, applied one level down; its absence is the hole D5 fell
through.

1. **Naming.** A modality node is named by the *measurement or record process* --
   instrument, sampling geometry, encoding, assay, record-keeping practice --
   never by the field, subject, sector or purpose.
2. **Admission.** A child is admitted only if two papers can carry it and differ
   on Scientific discipline or Sector. If the child's name *determines* another
   axis's value, it is that axis in disguise: fold it into its structural
   sibling and recover the quantity by cross-tab.
3. **Generality.** Name at the most general level of the measurement process
   that still picks out one signal kind -- this stops EEG/ECG/seismometer
   becoming siblings and fragmenting along field lines by the back door.

**Stated exception**: clause 2 may fail empirically while clause 1 holds
(cryo-EM has one user). That stands -- **the leak is a naming fault, not a
correlation**. What is forbidden is a node whose *definition* mentions a field.

Consequences: `Biomedical imagery` -> `Tomographic & radiological imaging`
(dermoscopy and endoscopy correctly leave for photographic -- the instrument
decides, not the ward); `Remote-sensing imagery` -> `Multispectral & radar`;
`Physiological signals` dissolves into `Waveform signals`;
`Environmental`/`Financial time series` delete into `Sampled quantity series`;
`EHR` -> `Longitudinal administrative records`.

### Documented gap: geospatial & mobility data (owner, 2026-09-29)

Two independent derivations reported geospatial vector data as having no level-1
home. Measured, the residue is far smaller than either implied, and most of it
is not a modality problem at all: `Vehicle Routing Problem` (x3) is
combinatorial optimization (Method); `Traffic Signal Control` 2, `Urban
Planning` 1 and `Satellite Communication` (x2) are Sector; `Traffic Scene
Generation` 1 is Task + Sector. The genuinely modality-flavoured residue is
**`Trajectory Prediction` 1 and `Spatial Navigation` 1 -- two singletons**.

That does not justify a level-1 branch. Recorded as a **known gap**, to be
revisited at the 2023-2026 re-extraction, which will say whether it is real.

### The property test

**A modifier that can be true of a node's siblings is a property, not a
sibling.** This kills `Video`, `Multilingual text`, `Conversational language`
and `Temporal graphs` as nodes, and repairs D2, D3 and D4 with one rule. It
also extends §6's ban on dividing by mathematical structure **downward to every
level**, not just level 1.

### Reinforcement learning takes no modality of its own (owner, 2026-09-28)

A ninth branch for "interaction data" was proposed and **rejected**. The signal
an RL agent sees is its *observation space*, which varies by environment --
Atari is images, locomotion is proprioceptive vectors, text games are language,
robotics is sensor fusion. "Interaction" is not a kind of signal but a kind of
**feedback structure**, already recorded as Method > Learning signal >
reinforcement; a branch for it would divide this axis by a second principle,
which this section forbids.

Corpus check: **zero** occurrences of Atari, MuJoCo, gridworld, Procgen or
Minecraft. What exists (`Continuous Control` 10, `Embodied AI` 5, `Game
Playing` 2) names no signal either. There is nothing to label.

Rule: an RL name takes the modality of its observation **when the name says so**
(`Vision-Based Robot Navigation` -> Vision), and otherwise takes no modality
value, exactly as `Deep Learning` does. The 263 bare RL mentions being
modality-blank is correct.

Added to close the one real hole: **low-dimensional state & proprioceptive
vectors**, a depth-2 child of Tabular & structured records -- **for names that
actually name the observation** (proprioceptive state, joint angles, simulator
state), NOT for `Continuous Control` itself, which names no signal and takes no
modality. An earlier draft of this section said both and could not be executed
(modality derivation, defect 1).

### Multimodal is a subject, not a union

Positive test: **the research question is about the relationship between
modalities** -- alignment, fusion, cross-modal transfer or retrieval. A paper
testing one optimizer on ImageNet and on WikiText fails it; its modality values
are `{Vision, Text}` and the co-occurrence is incidental. A vision-language
model passes.

Two properties keep this from being duplication:
- **No combinatorial blow-up.** Children exist only where a research community
  does. Pairs are never enumerated.
- **A "vision-touching" total stays derivable**, because the children are named
  by their constituents (`Vision 350, plus Vision-language 26`). No node lives
  in two places.

Residual limit (owner's objection, real): when the extraction returns only
`Computer Vision` + `Natural Language Processing`, the domain names cannot
separate "one multimodal dataset" from "two unimodal experiments". That is an
extraction limit, not an ontology one, and it is partly recoverable from
another field of the same paper -- `PaperExtractions.datasets` distinguishes
`{ImageNet, WikiText}` from `{LAION}`. The ontology should not encode it.

### Known defects, to fix in the re-derivation

`GRANULARITY_AUDIT.md` D1-D5. Level 1 fuses three kinds: sensory (vision,
language, audio), structural (graphs, time series, tabular) and **domain-derived**
(`Molecular & biological data` -- a field's data promoted to a signal kind
because this institute does a lot of biology). D5 is systemic: several branches
divide their level 2 **by application domain** (time series into
physiological/environmental/financial; tabular into EHR/user-interaction; vision
into biomedical/remote-sensing), reproducing the Application axis inside
themselves. Some of that is unavoidable -- an instrument is defined by its use --
but it needs a stated rule rather than happening silently.

## 7. Scientific discipline -- OECD Fields of Science, depth 3

Renamed from "Application domain" (owner, 2026-09-28) so the axis states what it
measures: **what field's knowledge does this work advance?**

**Level 1 is OECD FOS, not ours.** The previous eight branches were derived
bottom-up and failed the granularity audit: `Neuroscience` was a top branch at
84 mentions while `Chemistry` was not at 43 -- granularity set by corpus volume,
which is the balancing-by-paper-count rule violated through the back door. OECD
FOS is a designed classification with stated principles, defensible without us,
and it holds when the institute starts working in fields it has not yet touched.

| L1 (OECD) | L2 (OECD's own second level) |
|---|---|
| 1. Natural sciences | 1.1 Mathematics · 1.2 Computer & information sciences · 1.3 Physical sciences · 1.4 Chemical sciences · 1.5 Earth & related environmental · 1.6 Biological sciences |
| 2. Engineering & technology | 2.1 Civil · 2.2 Electrical, electronic & information · 2.3 Mechanical · 2.4 Chemical · 2.5 Materials · 2.6 Medical engineering · 2.7 Environmental |
| 3. Medical & health sciences | 3.1 Basic medicine · 3.2 Clinical medicine · 3.3 Health sciences · 3.4 Medical biotechnology |
| 4. Agricultural & veterinary | 4.1 Agriculture, forestry & fisheries · 4.2 Animal & dairy science · 4.3 Veterinary · 4.4 Agricultural biotechnology |
| 5. Social sciences | 5.1 Psychology · 5.2 Economics & business · 5.3 Educational sciences · 5.4 Sociology · 5.5 Law · 5.6 Political science · 5.7 Social & economic geography · 5.8 Media & communications |
| 6. Humanities | 6.1 History & archaeology · 6.2 Languages & literature · 6.3 Philosophy, ethics & religion · 6.4 Arts |

**Level 3 is the deliverable** -- OECD's two levels, then ours. Depth 2 is too
coarse to report (`Biological sciences` holds genomics, ecology and molecular
biology together). This costs almost nothing because **`NodeCut` matches node
ids, not depth**: the report cut can sit at `Biological sciences` in one branch
and at a depth-3 node in another, wherever the informative granularity is.

### Costs accepted deliberately

- **Neuroscience splits two ways, not three** (corrected 2026-09-28 by the
  discipline derivation; the earlier claim that OECD files it under 1.6 was
  wrong -- Frascati 2015 puts "Neurosciences (incl. psychophysiology)" under
  **3.1 Basic medicine**, and 1.6 has no neuroscience item). Measured placement:
  3.1 `neurosciences` 185 · 3.2 `psychiatry` 38 · 3.2 `clinical-neurology` 15 ·
  2.6 `neural-engineering` 15 · 5.1 `cognitive-science` 36. So 289 of ~304
  mentions land in **two** L1 branches (Medical & health 253, Social 38), and
  the split is decided from the name alone: cognitive construct -> 5.1;
  disease or population -> 3.2; device -> 2.6; else biological substrate -> 3.1.
  The residual cost has changed shape: `neurosciences` is now a **185-mention
  leaf**, the coarsest node on the axis, and the depth-4 split it needs must
  come from an external standard (e.g. SfN session categories), never from
  corpus volume.
- **Robotics is no longer a top branch** (OECD 2.2/2.3).
- **Software engineering sits two levels down** despite being the third-largest
  arXiv primary category in the corpus (6.6%, larger than all of vision). That
  is a cut-placement decision, not a structural one.

### OECD 1.2 would swallow the whole corpus

OECD's `1.2 Computer and information sciences` covers computer science -- which
contains AI and ML -- and names bioinformatics explicitly. Read literally, all
1999 papers are 1.2 and the axis measures nothing.

**Owner's ruling, 2026-09-29**: anything about AI/ML belongs on the AI-side axes
(Method, Task, Modality, Desired properties), never on this one. A computing
discipline is on this axis only when it is the **target** of the research --
using AI to study or improve software engineering is `2.x`/`1.2` software
engineering; *writing code to run your experiments* is not, and never licenses
the label. This is the `contributed` vs `used` distinction of issue #89, which
will enforce it mechanically once the schema carries a role; until then it is a
mapping rule. (The measured shares suggest the mistake is rare in this corpus.)

Resolution: **1.2 admits only computing disciplines that predate and survive
ML** -- software engineering, HCI, information retrieval, graphics, security,
theory of computation, data management, programming languages. `Machine
Learning`, `Deep Learning` and `AI` (~750 mentions) are **absent from this
axis**, not uninformative on it. The report must describe this axis's level 1
as *OECD FOS minus the field the institute is in*.

### Precedence rules for this axis

- **The axis test beats OECD's placement.** OECD supplies vocabulary and
  breadth, never arbitration -- the same status §3 gives ACM CCS. This decides
  bioinformatics, medical imaging, remote sensing and materials.
- **Field served beats head noun** -- the inverse of Method's rule, matching the
  inversion §8b already records for Modality.

### Tests (unchanged)

A field belongs here only if **it exists without AI** AND **it supplies the
problem, not the machinery**. The first clause applies to **the field served,
not the name's surface**, so `MLOps` and `Software Engineering for ML` are not
deleted on a technicality.

- `Game Theory` (20) and `Operations Research` (19) supply machinery -> Method.
- `Control Systems` (9) splits the same way: control *theory* -> Method; control
  *engineering of a physical plant* -> Engineering & technology.
- `Recommender Systems` (16) fails "exists without AI" and names what the output
  must be -> Task.

### Bioinformatics, and branch-level surfaces generally

`Bioinformatics` (40) and `Computational Biology` (33) are **general names for a
branch**, not leaves beside `Genomics`. Both are surfaces of the branch node.
The NIH BISTIC distinction (tools for biological *data* vs modelling biological
*systems*) is not recoverable from a bare name and need not be adjudicated.

This generalises -- see §8b: `Neuroscience` 84, `Medical Imaging` 48,
`Robotics` 25 and `Healthcare` 16 do the same, which is ~25% of this axis's
mentions landing at depth 1.

## 7b. Sector of application -- second axis

*What economic or operational activity does this serve?*

**Why this is not the same axis as discipline** (owner, 2026-09-28). Mapping a
fleet-routing paper to civil engineering asserts a contribution to civil
engineering's knowledge that the paper does not make; it solves a transit
agency's operational problem. Discipline says **whose knowledge is advanced**;
sector says **whose operational problem is solved**.

Independent in both directions, which is the strongest form of the admission
test: two civil-engineering papers differ on sector (structural materials vs
transit operations); two energy-sector papers differ on discipline (battery
chemistry vs load forecasting with no science content).

**Name-level test**: is the name a **field of study** -- journals, degrees, a
research community -- or an **economic activity** -- firms, markets, customers?
`Civil Engineering`, `Climate Science`, `Astrophysics` are fields; `Renewable
Energy Forecasting`, `Traffic Signal Control`, `Technical Debt` are activities.

**The name-level test alone is not sufficient** (sector derivation, S-D3): the
"genuinely both" case is ~150 mentions, not a handful. Object-level test to
settle it: **discipline-only when the object of knowledge is natural or social
reality; both axes when the object is itself a human-built operating system.**
Disease is natural reality, so clinical specialties (`Medical Imaging` 51,
`Pediatric Surgery` 16, `Epidemiology` 20 -- ~200 mentions) are discipline-only.
A hospital's scheduling and patient flow is a built system, so it is both.
This is what stops the axis becoming a lossy copy of OECD branch 3.

Two examples in an earlier draft of this section were invented and are
withdrawn: `Supply Chain Optimization` has **zero** occurrences in the corpus,
and `Operations Management` (1) names no sector, so it is not a "genuinely
both" case.

**Standard: ISIC Rev.4**, used consistently (GICS has no public-administration
or education sections and would lose 186 mentions; NACE/NAICS are regional
derivatives). Same-family international standard as the discipline axis's OECD
FOS. ISIC section M is excluded outright -- M72 "Scientific R&D" would swallow
every paper, the same trap as OECD 1.2 in §7.

**Measured: 244 names / 389 mentions, not the ~93 estimated here earlier.**
That estimate was an artefact of an incomplete candidate list -- it omitted
software & IT services (89), education (25) and environment (13), and excluded
healthcare while §7b's own candidate list named it. **~154 mentions are
sector-only**, with no home on any other axis: transit scheduling, demand
response, building energy, patient experience, conservation monitoring, content
recommendation, technical debt. The axis earns its keep.

Level 1 (13, incl. the administrative row): healthcare & social care 154 ·
information & communication 116 · education 25 · transportation & logistics 20 ·
energy & utilities 17 · environment & natural resources 13 · built environment
12 · public administration 7 · manufacturing 6 · agriculture, forestry &
fishing 5 · retail & consumer services 5 · finance & insurance 4.

**Healthcare is claimed by both axes and that is now reconciled**, not an
oversight: §7 lists `Healthcare` among the discipline axis's branch-level
surfaces while this section lists healthcare delivery as a sector. The
object-level test above decides which names go where.

Caveat recorded by the derivation: extraction asks for *research domains*, so a
paper whose sector is obvious from its datasets names its method instead. 389 is
a floor, not a measurement.

## 8. Still to design

- Task axis vocabulary (after the extraction decision).
- Per-axis residual and uninformative policy.
- The division schema proper: per branch, characteristic + positive test +
  negative test + residual policy, so `scope_out` becomes derivable.
- Depth-2 node lists per axis, each with 3 example depth-3 labels.

## 8b. Disposal and residual policy (from tail validation)

- **Contribution-type names** (`Benchmarking` 7, `Empirical Analysis of
  Algorithms`, `Multimodal Model Evaluation`) are not domains on any axis.
  They are `mark_ignore` on every axis. Written down because an unwritten rule
  gets improvised.
- **Too-generic names** (`Predictive Modeling`, `Event Classification`,
  `Optimization Techniques`, `Computing Research`) are on-axis but carry no
  information. **Every axis gets its own uninformative branch**, not just the
  one holding `Machine Learning` / `Deep Learning`; it is reported as a line and
  excluded from that axis's shares.
- **Homonyms** must be declared, not discovered mid-run: `Policy Evaluation`
  (off-policy evaluation vs evaluation of public policy), `Compression
  Algorithms` (data vs model). Each axis resolves its own surface, and the
  ambiguity probe exists for exactly this.
- **Branch-level residence is legitimate** (flagged independently by the
  application, properties and modality derivations). A surface may map to a
  branch node itself, not only to a leaf: `Computer Vision` 240, `NLP` 295,
  `Neuroscience` 84, `Bioinformatics` 40, `AI Ethics` 7 and translated `GNN` 82
  all name the branch and nothing narrower. Forcing them into a leaf invents
  precision the name does not carry. **Consequence for reporting**: depth-2
  shares must be stated against a denominator that names the branch-level
  bucket explicitly -- roughly 25% of the application axis's mentions and 264 of
  563 on Vision sit at depth 1.
- **Precedence is per-axis, not global.** The head-noun rule below is a Method
  rule; on Modality it inverts (`Molecular Graphs`, `Protein Language Models`,
  `Graph Signal Processing` all take the token naming the *signal*, which is the
  modifier). Each axis states its own precedence.
- **Homonym lists are per-axis.** Measured on Modality: a node named `Networks`
  would be ~59% wrong by papers and 78% by names; `programming` 83% wrong;
  `sequen` 65%; `spectral` 89%. `vision`/`visual` is a name-level trap invisible
  to a paper-level check -- 29% of names but only 3% of papers.
- **Method stays one axis** (owner, 2026-09-28), although by §1's own test its
  seven aspects are independent and behave like axes. Splitting would multiply the
  largest axis sixfold to recover ~50-80 mentions. **Papers are not constrained
  by this**: a paper carries ~3 names, each mapped independently, so a paper that
  covers several methods still receives several Method values. The loss bites
  only when a *single name* fuses two aspects (`Multi-Agent Reinforcement
  Learning`), and then the head-noun rule decides.
- **Within-axis precedence (head-noun rule).** When a surface names two things
  on the *same* axis (`Multi-Agent Reinforcement Learning`, `Distributed
  Optimization`, `Meta-RL`), map it to the branch named by the **head noun**,
  unless the head is generic (`learning`, `methods`, `models`), in which case
  the modifier decides. Mechanical, and it reproduces every placement §3 already
  asserts. Adopted from the method-axis derivation (D4).
- **On an optional axis, "no value" is not "uninformative value".** A name that
  simply says nothing about the axis is absent from it, not uninformative; the
  uninformative branch is for on-axis names too vague to inform. On Desired
  properties the vague-but-on-axis surfaces (`AI Ethics` 7, `Responsible AI` 5,
  ~28 mentions) are absorbed as **umbrella surfaces on the branch node itself**,
  by the same precedent as `Bioinformatics` in §7, so that axis's uninformative
  branch is legitimately empty (D-P4/D-P5).
- **The uninformative branch is an administrative level-1 row**, not an aspect
  (D5). §3's seven aspects and §6's eight branches are the *substantive* level-1
  sets; each axis additionally carries `uninformative`, flagged as not an aspect
  and excluded from that axis's shares. On Method it is the second-largest
  cluster (~600 mentions).
- **Homonyms to declare before any run**, extending F7: `Policy Evaluation`,
  `Compression Algorithms`, `Distributed Optimization`, `Control Systems` /
  `Control Theory`, `Clustering` / `Density Estimation` / `Dimensionality
  Reduction`, `Robustness` (three axes), `Bandits`, `Simulation`, `bias` (fairness vs
  inductive/estimator bias), `alignment` (4 of 6 corpus surfaces are
  multimodal/sequence/ontology alignment, not AI safety), `efficiency`.
- **Compound *surface* names** (`Fairness and Interpretability in Machine
  Learning`, `Probability and Statistics`, `Task and Motion Planning`) are not
  banned -- the ban is on compound *category* names. A compound surface maps to
  the **nearest common parent** of the concepts it fuses; it maps to a single
  sibling only when one is clearly dominant and the other incidental.

## 9. Carried-over constraints

- **Never balance categories by paper count.** Extended to the expansion
  procedure (owner, 2026-09-29): **volume decides which node to open next; it
  plays no part in how it opens.** The ordering is mandatory and is what makes
  compliance checkable rather than merely promised:
  1. draft the sibling set and its characteristic from **the field's own
     structure**, with no corpus access -- no tally, no name list, no examples;
  2. record that draft verbatim and do not edit it;
  3. only then consult the corpus, for **two questions and no others** -- a
     cluster with no node is a blind spot to add or justify; a node with no
     support is kept and flagged speculative, never deleted;
  4. deliver both versions plus every change between them, with its reason.
  Nothing else licenses a change: a sibling set may not be merged, split,
  renamed or reordered because of counts.
- **Phase 1 must not read `nodes.tsv` at all** (properties depth-3 derivation,
  2026-09-29, self-reported). A deriver needs its parents' `characteristic`
  before drafting, but that column sits in the same file as `examples`,
  `corpus_names` and `corpus_mentions`, so any read leaks counts and the
  count-free phase is fiction. The agent that found this reported its own
  coincidence rate child by child -- Privacy 0/3, but Accountability and
  Computational cost 3/3 -- rather than claiming purity. **Fix: publish each
  axis's characteristics to a separate count-free file and point phase 1 at
  that.** Until that exists, treat any phase-1 draft whose brief required
  reading `nodes.tsv` as partially contaminated, and say so.
- **A child sibling set must refine its parent's own characteristic, never
  import a different aspect's characteristic** (method depth-3 derivation,
  2026-09-29). Worked case: under `Learning signal > Reinforcement learning`,
  *both* candidate principles -- model-based/model-free and
  value-based/policy-gradient -- divide by **machinery**, so either as the
  depth-3 sibling set reproduces defect M1/M5 one level down. Depth 3 divides by
  **who or what supplies the evaluative signal** (online · offline · from
  demonstrations · from human feedback · intrinsically motivated · multi-agent);
  model-based/model-free moves to depth 4 inside `Online RL`. Declared cost: a
  depth-3 report shows no model-based share although the corpus names ~17. The `examples` column is a **step-3
  checklist**, never a step-1 seed -- it was written alongside the counts and
  would anchor the draft. The study measures the proportion
  of research per area; engineering equal sizes destroys that quantity. Group by
  conceptual relatedness only.
- Watch branching factor; many siblings means specialising too early.
- No compound names **where two different principles are fused** (`Inference &
  optimization`, `Data curation & supervision quality`, `Molecular & biological
  data` -- a substance kind fused with a field word; all three renamed
  2026-09-28). A doublet naming **one** concept in the field's own idiom
  (`Speech & audio`, `Vision & imaging`, `Language & text`) is not a fusion and
  is allowed at level 1. Otherwise: find the family's real name or split. A parent needs >=2
  substantive children. Reject names general enough to attract out-of-scope
  entries.
- Corpus **bounds scope and exposes blind spots**; semantics decides what a
  category is. A category with no corpus support is *possibly speculative,
  justify or keep*; a corpus cluster with no category is a *blind spot*.
  Neither auto-deletes. (Fixes rules 7/8 of `BRIEF.md`.)
- Depth 2 is the deliverable **except on Scientific discipline, where §7 makes
  it depth 3** (OECD's two levels plus ours).

