# Modality / data axis: depth-2 derivation

Derived 2026-09-25 from `AXES.md` (authoritative), `TAIL_VALIDATION.md`, and the
2055-name corpus in `domain_names.tsv`. Nothing else was read. Corpus counts are
regex-assigned over all 2055 names (`assign_mod.py`, `homonym_mod.py` in the
session scratchpad) and are accurate to a few percent, not exact; every number
below is a *bound on scope*, never an arbiter (AXES.md 9).

## 1. What the axis delivers

9 level-1 rows (8 substantive, fixed by AXES.md 6, plus the administrative
`uninformative` row required by 8b) and **34 level-2 nodes**.

| L1 | L2 children | names | mentions |
|---|---|---|---|
| Vision & imaging | Natural imagery, Video, 3D geometry, Biomedical imagery, Remote-sensing imagery, Document imagery | 126 | ~563 |
| Language & text | Written text, Conversational language, Source code, Multilingual text | 107 | ~522 |
| Speech & audio | Speech, Music, Environmental sound | 25 | ~46 |
| Graphs & relational | Knowledge graphs, Social & information networks, Temporal graphs | 47 | ~79 (+82 translated GNN mentions) |
| Time series & signals | Physiological signals, Sensor streams, Environmental time series, Financial time series | 44 | ~80 |
| Molecular & biological data | Small molecules, Proteins, Genomic sequences, Omics profiles, Materials | 111 | ~306 |
| Tabular & structured records | Tabular feature data, Electronic health records, User interaction records | 16 | ~34 |
| Multimodal | Vision-language, Audio-visual, Multimodal biomedical data, Sensor fusion | 26 | ~60 |
| *uninformative* (administrative) | Modality-unspecified learning, Generic data names | 27 | ~552 |

Branching factor: **9 at level 1** (fixed), **6/4/3/3/4/5/3/4/2 at level 2**,
mean 3.8, max 6. The maximum sits on vision, which carries 28% of all
modality-bearing mentions and has six distinct instrument communities; the
minimum sits on the administrative row. No node was created or merged to even
out counts (AXES.md 9): `Environmental sound` keeps 5 mentions and
`Biomedical imagery` keeps 161, because they are equally real divisions of their
parents.

## 2. Forced by AXES.md vs judgement

**Forced** (named in AXES.md 6 as branch content, kept, sometimes renamed):
video, 3D & point clouds, remote-sensing imagery, medical imagery, music,
knowledge graphs, physiological signals, molecules, proteins, materials,
sequences (renamed, see D2), tabular, vision-language, audio-visual,
multimodal medical.

**Judgement** (mine, with reasons):

- **Source code** under Language & text. AXES.md never mentions code on any
  axis; 7 explicitly keeps `Software Engineering` in Application. But 15 names /
  23 mentions (`Code Generation` 7, `Program Synthesis` 3, `Text-to-SQL`,
  `Code Search`) name code *as the data operated on*, and the field treats code
  LLMs as continuous with text LLMs. Placing it in Language is the only
  placement that keeps the translate-don't-drop principle (5) honest.
- **Multilingual text** as a modality child rather than a task. AXES.md 6 lists
  `machine translation 15` as a child of Language & text, but 4's own test makes
  MT a task. What MT contributes *to this axis* is the cross-lingual data
  regime, so the node names that regime and MT maps to it.
- **Conversational language** split from written text: dialogue data is a
  different signal regime (multi-turn, interactive) with its own community, 14
  mentions.
- **Omics profiles** split from genomic sequences: an expression matrix is not a
  sequence, and single-cell is a separate community (22 mentions).
- **Environmental sound**, **Document imagery**, **Sensor streams**,
  **Financial time series**, **Social & information networks**,
  **Temporal graphs**, **User interaction records**: each is a community the
  field has, with 0-24 corpus mentions here.
- **Tabular's three children**, and in particular routing `Recommender Systems`
  (16+3+2+1+1) to `User interaction records` (see D6).

## 3. Where AXES.md is silent, ambiguous or self-contradictory

This is the section that matters. Eleven defects, in descending order of how
much they would cost at mapping time.

### D1. Section 6's "children" column is not a child list

It is populated mostly with **Task-axis names**: `machine translation`,
`QA`, `language modeling`, `ASR`, `speech synthesis`, `link prediction`,
`forecasting`. Section 4's own test ("a term is a task if it names what the
output must be") sends every one of those to Task. Read literally, 6 rebuilds
the task/modality fusion that 4 exists to prevent, and a depth-2 derivation that
obeyed it would produce `Language & text > Question Answering`. I read the
column as **evidence of volume**, not as a specification, and derived children
by asking what kind of *signal* each branch contains. **Fix: relabel the column
`corpus evidence`, and say that a branch's children divide the signal.**

### D2. `sequences` is named as a child, and it is a measured homonym

AXES.md 6 lists `sequences` under Molecular & biological. Measured: of the 14
corpus names containing `sequen` (26 papers), **7 names / 17 papers (65%) are
generic** -- `Sequence Modeling` 8, `Sequence-to-Sequence Models`,
`Sequential Learning`, `Sequential Monte Carlo` -- and only 7 names / 9 papers
are biological. A node called `Sequences` would be majority-wrong, and it is
also the node TAIL_VALIDATION F3 already caught as a phantom on the other side
(section 5's `RNN -> Modality > Sequences`). F3 fixed the *example* and left the
*node name* standing. Renamed here to **`Genomic sequences`**.

### D3. `Graphs & relational` is ambiguous between two readings, and one of them eats four other branches

Does the branch mean "data whose native form is relational" or "anything
representable as a graph"? The second reading swallows molecules
(`Molecular Graphs`), meshes, scenes, images-as-patches and point clouds --
which directly contradicts 6's own instruction not to divide by mathematical
structure. I adopted the **narrow reading** and wrote it into the branch's
negative test. Secondary collision: the word `relational` also names relational
*databases*, which belong to `Tabular & structured records`; the two L1 names
overlap on a word. **Fix: state the narrow reading in 6, and rename one of the
two branches or gloss `relational`.**

### D4. No branch owns agent-environment / control signals -- the biggest gap

`Reinforcement Learning` 263, `Deep RL` 34, `Model-Based RL` 14, `MARL` 14,
`Imitation Learning` 14, `Continuous Control` 10, `Embodied AI` 5,
`Robotic Manipulation` 4, `Sim-to-Real Transfer` 4, MDP/POMDP 6, plus
`Robotics` 25 on the Application axis: **400+ papers whose data is a stream of
states, actions and rewards from a simulator or a plant**. None of the eight
branches accepts it. Modality is "near-mandatory" (section 1), so annotators
will improvise -- `Visual Reinforcement Learning` 2 to Vision, the rest to
`uninformative` -- and the axis will report that a quarter of the institute's
output has no data. Two honest fixes: a **ninth branch** (`Interaction & control
data`, children: simulated environments, robot proprioception & control, game
state), or an **explicit ruling** in 6 that RL papers take no modality value and
that this is a finding, not a gap. I did not invent the branch, as instructed.
I recommend the ninth branch: state-action data is a kind of signal the field
distinguishes, exactly like the other eight.

### D5. Vision's fixed child list mixes two principles

`images / video / 3D / remote-sensing / medical` divides partly by **capture
geometry** (still, still+time, 3D) and partly by **capture instrument**
(satellite, scanner). No single characteristic covers both, so the branch
declares a two-clause one ("what sensing process produces the signal, and over
what domain it is sampled"). The clean alternative -- geometry at depth 2,
instrument at depth 3 -- would bury `Biomedical imagery` (161 mentions, the
second-largest node on the axis) one level down, which the survey cannot afford.
Flagged rather than silently fixed.

### D6. Tabular's "1 mention" is an artefact of an unmade routing decision

AXES.md 6 records `Tabular & structured records -- 1 mention: blind spot, keep`.
Measured, the branch holds **~34 mentions** once you ask what recommender and
clinical-record names *operate on*: `Recommender Systems` 16 + `Recommendation
Systems` 3 + 3 more (23), clinical/registry records (6), generic tabular (5).
Section 7 sends `Recommender Systems` to Task > Recommendation and **never says
what its modality is** -- the faceted design requires an answer on every axis.
I mapped it to `User interaction records` and flagged it; the conservative
alternative (modality-silent) restores the 1-mention blind spot. Either way the
schema must choose, because the choice moves a whole L1 branch between "empty
and kept on faith" and "the size of Speech & audio".

### D7. Section 8b's head-noun rule inverts on this axis

The within-axis precedence rule says map to the branch named by the **head
noun**. On this axis that is backwards: `Molecular Graphs` (head: graphs, signal:
molecule), `Graph Signal Processing` (head: processing), `Protein Language
Models` (head: models, signal: protein), `Image-to-Code Generation`. The rule
also contradicts TAIL_VALIDATION's own worked example, which routes `Protein
Language Models` to Modality > Molecular. **Fix: on the modality axis,
precedence goes to the token that names the *signal*; the head noun usually
names the machinery or the task, which live on other axes.**

### D8. The EEG/fMRI boundary is unstated

6 puts `physiological signals` under Time series and `medical imagery` under
Vision, but the corpus does not respect the split: `Electrophysiology and
Neuroimaging`, `Magnetoencephalography (MEG)`, `MEG Data Analysis`,
`Functional Connectivity` 4. MEG and EEG are traces; fMRI and MRI are volumes.
I wrote the boundary into both nodes' negative tests. Roughly 25 mentions ride
on it.

### D9. A translated architecture name can only reach depth 1, and that is never said

Section 5 translates `Graph Neural Networks` 82 to Modality > Graphs and
`Vision Transformers` to Modality > Vision, but a GNN paper's name does not say
whether the graph is a knowledge graph, a social network or a temporal one. So
82 of the Graphs branch's ~161 mentions sit **on the branch node**, as do 264 on
Vision (`Computer Vision`) and 367 on Language (`Natural Language Processing`).
Section 7 legitimises this once, for `Bioinformatics`/`Computational Biology`
("general names for the whole branch"), and never generalises it. **Fix: state
that branch-level residence is a legitimate mapping outcome on every axis.**
Without it, an annotator facing 295 `Natural Language Processing` mentions will
force them into a leaf and invent a distribution.

### D10. `Molecular & biological data` is the wrong name for its own contents

The branch holds `Materials` (16 mentions: crystals, alloys, atomistic systems),
which is neither molecular nor biological, and AXES.md 6 itself lists
`materials` there. Its real characteristic is **matter**. Keeping the name is
fine; the characteristic must not pretend the branch is about life.

### D11. Section 8b lists the homonyms to declare and misses this axis's worst ones

The declared list (`Policy Evaluation`, `Compression Algorithms`,
`Distributed Optimization`, `Control Systems`, `Clustering`, `Robustness`,
`Bandits`, `Simulation`) contains almost nothing that bites here. The measured
ones are in section 5 below. **Fix: the homonym list should be per-axis, since
8b already says each axis resolves its own surface.**

## 4. Blind spots kept

Nodes kept with little or no corpus support, under the `Tabular` precedent
(AXES.md 9: no corpus support means *justify or keep*, never auto-delete). Each
is a legitimate area of the field that a single institute-year misses and a
2023-2026 re-extraction will populate.

| node | corpus | why kept |
|---|---|---|
| Audio-visual (multimodal) | **0 names** | AXES.md 6 asserts it; AVSR / sound-localisation / audio-visual event communities exist with their own benchmarks. Zero measured support, so it is flagged, not silently carried. |
| Tabular feature data | 4 / 5 | The branch AXES.md already keeps deliberately. Tabular deep learning is an active, venue-bearing area. |
| Electronic health records | 5 / 6 | `Epidemiology` 20 and `Public Health` 12 almost certainly run on record data but name only their field: the modality is invisible to this extraction, which is an extraction limit, not evidence of absence. |
| Financial time series | 3 / 3, none unambiguous | Financial and operational forecasting is a large field with essentially no presence in this institute. |
| Document imagery | 2 / 2 | Document AI / OCR / chart understanding. |
| Sensor fusion (multimodal) | 1 / 1 | Autonomous-driving and robot perception; here robotics work is named by application, never by sensors. |
| Environmental sound | 3 / 5 | DCASE and bioacoustics (`Bioacoustic AI` 1). |
| Sensor streams | 7 / 7 | Wearables, IMU, mobility traces; also the only home for tactile and spectrometry signals. |

Blind spots I could **not** keep, because they have no level-1 home:
agent-environment/control data (D4), and geospatial vector/mobility data
(`GIS` 1, `Trajectory Prediction` 1, `Spatio-temporal Analysis` 1), which is
currently split between remote-sensing imagery and sensor streams.

## 5. Homonym traps on this axis (measured)

The brief's reference point: 6 of 11 corpus names containing `Policy` are RL
policies, so a node named `Policy` would be 55% wrong. This axis is worse.

| surface token | names | reading that is NOT this axis's | share |
|---|---|---|---|
| `network` | 77 (236 papers) | 50 names / 128 papers are **neural architectures** that imply no modality (`Neural Networks`, GAN, RNN, `Network Pruning`); 7 names / 9 papers are telecom and transport infrastructure. 16 names / 97 papers denote relational data -- but 86 of those 97 are the single surface `Graph Neural Networks`, which reaches this axis by translation (AXES.md 5), not by naming data. | a node named `Networks` would be **~59% wrong by papers**, and 78% wrong by names |
| `programming` | 16 (23 papers) | 12 names / 19 papers are mathematical programming (stochastic, integer, dynamic, bilevel, constraint) | **83% wrong by papers** |
| `sequen` | 14 (26 papers) | 7 names / 17 papers are generic sequence modeling, not biological sequence | **65% wrong** (this is AXES.md 6's own proposed node name, D2) |
| `signal` | 6 (17 papers) | `Graph Signal Processing` 5 (graph data) and `Traffic Signal Control` 2 (RL control) | **41% wrong** |
| `vision` / `visual` | 31 (294 papers) | 9 names are human vision as an object of study (`Vision Science`, `Visual Neuroscience`, `Visual Perception`, `Visual Perceptual Learning`) or chart rendering (`Data Visualization`, `Visualization`) | **29% of names**, only 3% of papers (the mass is `Computer Vision` 240) -- a name-level trap that a paper-level check would miss |
| `graph` | 55 (182 papers) | 7 names / 23 papers are `Computer Graphics` 9, `Graph Theory` 6, probabilistic `Graphical Models` 4, `Graphical User Interfaces` | **13% by papers** |
| `sensing`/`sensor` | 6 (16 papers) | 12 of the 16 papers are `Remote Sensing`, i.e. **imagery**, not sensor streams | a `Sensing` node would be 75% imagery |
| `cell` | 13 (19 papers) | `Cellular Network Optimization` 2 is telecom | 11% |
| `spectral` | 6 (9 papers) | `Spectral Methods` 3, `Spectral Graph Theory` 2, `Spectral Learning` are machinery; `Autism Spectrum Disorder` 2 is clinical; only `Mass Spectrometry` 1 is a signal | 89% wrong |
| `simulation` | ~20 | Simulated data is a *provenance* property, not a kind of signal; most are `Monte Carlo` / `Simulation-Based Inference` (Method) or domain simulation (Application) | no modality node may be named `Simulation` |

Consequence for node naming: every node on this axis is named for the **signal**
(`Genomic sequences`, `Social & information networks`, `Source code`), never for
the bare token (`Sequences`, `Networks`, `Programming`).

## 6. Corpus names rejected to another axis

Grouped by the test that rejected them. ~250 names / ~700 mentions total.

| names | count | destination | test applied |
|---|---|---|---|
| `Neural Networks` 19, `Transformers` 13+8, `Attention Mechanisms` 13+2, `Recurrent Neural Networks` 8, GAN 14, CNN 5, `Neural Architecture Search` 6, + ~40 more | 58 names / 214 papers | Method > Model design & analysis (or uninformative) | AXES.md 5 row 2: implies no single modality. `GNN` 82 and `Vision Transformers` 4 are the exceptions section 5 translates *to* this axis |
| `Software Engineering` 36, `Software Testing` 4, `Empirical Software Engineering` 3, + 19 more | 22 / 62 | Application > Computing & software systems | 7's amendment: serves a field that exists without AI. Only names denoting code *as data* stayed (`Code Generation`) |
| `Stochastic/Mixed-Integer/Dynamic/Constraint/Bilevel/Differentiable Programming` | 12 / 19 | Method > Inference & optimization | homonym: mathematical programming names machinery |
| `Graph Theory` 6, `Spectral Graph Theory` 2, `Graphical Models` 2+2, `Graph Kernels`, `Graph Rewiring`, `Graph Positional Encoding` | 8 / 16 | Method | names how the answer is computed, not what the data is |
| `Computer Graphics` 9, `Graphical User Interfaces`, `Texture Mapping` | 3 / 11 | Application > Computing | output rendering is not an input signal |
| `Vision Science` 2, `Visual Neuroscience`, `Visual Perception`, `Visual Perceptual Learning`, `Visual Attention`, `Naturalistic Stimuli Processing` | 7 / 8 | Application > Neuroscience | the object of study is the human visual system |
| `Data Visualization`, `Visualization`, `Neural Network Visualization` | 3 / 3 | Method / Desired properties > Interpretability | a plot of results is not the signal operated on |
| `Sequence Modeling` 8, `Seq2Seq` 2, `Sequential Learning` 2, `Sequence Generation` 2, + 3 | 7 / 17 | Method > Model design | same logic TAIL_VALIDATION F3 applied to RNN: implies no single modality |
| `Communication Networks` 2, `Computer Networks` 2, `Cellular Network Optimization` 2, `Wireless Networks`, `SDN`, `Network Routing`, `Transportation Networks` | 7 / 9 | Application > Computing / Industry | infrastructure served, not signal |
| `Benchmarking` 7, `Model Evaluation` 7, `NLP Benchmarking`, `Multimodal Model Evaluation`, `Empirical Analysis of Algorithms` | 9 / 21 | `mark_ignore` on every axis | 8b: contribution type is not a domain |
| `Model Predictive Control` 3, `Traffic Signal Control` 2, `Networked Control Systems` | 3 / 6 | Method / Application per 7's control split | control is machinery or engineering, not a signal |
| `Neuroscience` 84, `Epidemiology` 20, `Robotics` 25, `Healthcare` 16, `Astrophysics` 15, `Medical Physics` 18 | ~180 papers | Application only | names the field served; carries no modality claim (though most of them *have* one that the extraction never states -- see D4 and the EHR blind spot) |
| `Machine Learning` 249, `Deep Learning` 177+56, `Artificial Intelligence` 15, `Neural Networks` 19, `Data Analysis` 4, `Predictive Modeling` 3, + 21 | 27 / 552 | this axis's `uninformative` row | 5 row 3 and 8b/F5 |

Two decisions inside the corpus worth flagging as reversible:
`Graph Signal Processing` 5 stays on the Graphs branch (the signal is indexed by
a graph); `Molecular Graphs` 1 goes to Molecular, not Graphs (the graph is the
encoding). They pull in opposite directions and both follow D3's narrow reading.

## 7. Branching-factor justification

- **Level 1 = 9**: fixed by AXES.md 6 (8) plus 8b's administrative row. I did
  not add the ninth substantive branch D4 argues for.
- **Level 2 = 34, mean 3.8**: no branch exceeds 6. The distribution tracks how
  finely the *field* has subdivided each signal, not how many papers the
  institute wrote: vision 6 (six instrument communities), molecular 5 (five
  kinds of matter), language 4, time series 4, multimodal 4, speech 3, graphs 3,
  tabular 3.
- Nothing was split to fill a branch and nothing was merged to shrink one. The
  6 on vision is the one place worth re-examining, and D5 explains why the
  alternative is worse for the survey.
- Depth-3 examples are illustrative only: three per depth-2 node, chosen to show
  that the node has room to divide again without changing its characteristic.
