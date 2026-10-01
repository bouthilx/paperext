# Method axis: depth-2 derivation rationale

Derived 2026-09-25 from `AXES.md` + `TAIL_VALIDATION.md` + `domain_names.tsv`
(2055 names, 1999 papers, 2024). Nothing from `domains/v0`, `models/`, or the
three design runs was consulted.

Level 1 is delivered exactly as `AXES.md` s3 fixes it: six aspects, none
invented, none dropped. One additional level-1 row, `uninformative`, is an
**administrative residual branch required by s8b**, not a seventh aspect; it is
marked as such and excluded from area shares. See D5.

Branching: **6 aspects -> 36 depth-2 nodes** (5 / 7 / 8 / 7 / 4 / 5), mean 6.0.

| L1 | depth-2 children | names | mentions |
|---|---|---|---|
| Learning signal | 5 | 114 | ~644 |
| Training regime | 7 | 92 | ~298 |
| Inference & optimization | 8 | 246 | ~591 |
| Model design & analysis | 7 | 182 | ~524 |
| Learning theory & generalization | 4 | 36 | ~65 |
| Data curation & supervision quality | 5 | 47 | ~72 |
| *(uninformative residual)* | 0 | 58 | ~602 |

Counts are a scripted keyword tally over the full vocabulary, not a hand
mapping; they are indicative to roughly +/-10% and are for scope-bounding only.
Nothing in the structure was decided by them, and no node was split or merged to
even them out. Reinforcement learning (446 mentions) and Compositional
generalization (4) are siblings-in-spirit at the same depth precisely because
the survey's job is to report that ratio.

## 1. What was forced by AXES.md, and what was judgement

**Forced (the schema names the node or rules on it explicitly):**

- `reinforcement-learning`, `self-supervised-learning`, `supervised-learning`,
  `unsupervised-learning` (s3 children of Learning signal).
- `transfer-learning`, `multi-task-learning`, `meta-learning`,
  `continual-learning`, `online-learning`, `distributed-training` (s3 children
  of Training regime; F9 additionally locks Domain Adaptation into transfer).
- `continuous-optimization`, `combinatorial-optimization`,
  `probabilistic-inference`, `game-theory` (s3), and `causal-inference` with
  its three named children (s3, owner-locked).
- `combinatorial-optimization` also absorbs `Operations Research` 19 by the
  s7 locked ruling.
- `model-efficiency` as a depth-2 family under Model design (s3 + s2 Frugal
  ruling + F1).
- `neural-architectures` and `formal-verification` as the landing sites for
  s5's "implies neither a modality nor a task" row.
- `expressive-power` holds s5's `Deep Learning Theory` and
  `Geometric Deep Learning`.
- `statistical-learning-theory`, `ood-generalization`,
  `compositional-generalization`, `scaling-behaviour` (s3 + F9).
- `data-augmentation`, `data-selection` (active learning), `data-quality`
  (noisy labels, label cleaning) (s3 + F2).
- The `uninformative` residual (s8b).

**Judgement (mine, each justified below):**

- `human-feedback` split out of reinforcement (s3 counts imitation inside RL).
- `constrained-learning` created (no home existed at all) - D2.
- `model-interpretation` and `adversarial-machine-learning` created by
  generalizing the Frugal precedent - D2.
- `generative-models` created as a depth-2 Method node - D6.
- `numerical-methods` and `inference-time-methods` created as blind-spot nodes.
- `synthetic-data` and `dataset-construction` split out of data curation.
- `sequential-decision-making` created to hold planning/control machinery
  distinct from RL.
- Uncertainty quantification **merged into** probabilistic inference rather
  than standing as a ninth sibling.
- Demotions to depth 3: semi-/weakly-supervised (into supervised learning),
  stochastic and first-order methods (into continuous optimization), NAS (into
  neural architectures), few-shot (into meta-learning), curriculum (moved to
  data selection).

## 2. Defects found in AXES.md

Ordered by how much of the corpus rides on them.

### D1. "Method is not one characteristic" is stated and then not acted on

s3 opens by saying Method fuses three orthogonal things, and s1 gives the test
for what deserves an axis: *two papers can differ on it while agreeing on every
other axis*. The six Method aspects pass that test against each other -
federated training can be self-supervised, a diffusion paper can be about
convergence rates. By the schema's own rule Method is **five or six axes, not
one axis with six children**, and the document acknowledges this in prose while
building the single tree anyway.

Consequence, not hypothetical: every within-Method compound name
(`Multi-Agent Reinforcement Learning`, `Federated Learning`,
`Meta-Reinforcement Learning`, `Offline Reinforcement Learning`,
`Distributed Optimization`, `Self-Supervised Learning (Graph Data)`) has to be
forced into one aspect and loses the other reading. s8b's compound-surface rule
("map to the nearest common parent") is unusable here because the nearest common
parent of two Method aspects is Method itself.

*What I did:* delivered one tree, and adopted an explicit precedence rule so the
loss is at least systematic - D4.

*Recommended:* either split Method into `method-signal`, `method-regime`,
`method-machinery`, `method-model`, `method-theory`, `method-data` as sibling
axes (the cost is per-name mapping, which s1 has already accepted for five
axes), or state in the schema that Method is deliberately a lossy single tree
and adopt D4's precedence rule as policy.

### D2. The "methods stay in the method tree" rule is written for Frugal AI only, and Method has no room for it

s2's strongest argument for faceting is: `Quantization` is a Method value *and*
`Frugal AI` is the Desired property, and only axes can say both. That argument
generalizes without modification to every desired property - and the schema
never generalizes it, so the Method tree has no home for:

| property | method names with no Method home | mentions |
|---|---|---|
| interpretability | Mechanistic Interpretability, Model Interpretability, feature attribution, GNN explainers, concept bottlenecks, probing | ~65 |
| robustness | Adversarial ML 13, Adversarial Robustness 10, attacks & defences, adversarial training, certified robustness | ~64 |
| privacy | Differential Privacy 8, Privacy-Preserving ML 4, unlearning | ~27 |
| fairness | Bias Mitigation 8, Fairness Algorithms, Fair Classification, Intersectional Fairness | ~15 |

That is ~170 mentions, more than the whole Training regime aspect, that s3
silently drops. Only efficiency was noticed (F1, "blocking"), and it was
noticed because the owner had ruled on it by name.

*What I did:* `model-interpretation` and `adversarial-machine-learning` under
Model design (they analyse a trained model, which the aspect's name covers), and
`constrained-learning` under Training regime for privacy/fairness/safety, whose
techniques are all training-time modifications under a behavioural requirement.
`constrained-learning` does **not** satisfy Training regime's stated
characteristic; I extended that characteristic to "...or constrained by" and
flag it here rather than hide it.

*Recommended:* write the general rule in s2 - "for every Desired property there
is a technique family, and the technique family is a Method value" - and either
broaden Training regime's characteristic as I did, or split Model design per D3.

### D3. Two level-1 characteristics are themselves fused

- **Model design & analysis**: s3 already bolts "**and at what cost**" onto it
  to make compression fit. With D2's additions it now carries four unrelated
  questions: what shape the structure has, what it can represent, what it costs,
  and what can be established about a trained instance. Its seven children do
  not differ by a single principle, which is exactly the `X and Y` fusion the
  document set out to remove - the fusion has simply moved from the node name
  into the node's characteristic.
  *Recommended split:* **Model design** (architectures, generative families,
  expressivity), **Model analysis** (interpretation, adversarial analysis,
  verification), **Model transformation** (pruning/quantization/distillation,
  unlearning, merging). Three non-compound aspects, each with >= 2 substantive
  children.
- **Training regime**: "how training is organised across tasks, time, agents,
  **data**" collides head-on with Data curation's "how the training data is
  selected, cleaned or labelled". Drop "data" from Training regime.

### D4. No within-axis precedence rule for multi-aspect names

s8b covers compound *surfaces* across siblings but not names that name two
different Method aspects. I adopted and used:

> **Head-noun precedence.** Map to the aspect named by the head noun, unless the
> head is generic ("learning", "methods", "models", "algorithms"), in which case
> map to the aspect named by the modifier.

`Multi-Agent Reinforcement Learning` -> Learning signal (head is "reinforcement
learning"), matching s3's own count. `Federated Learning` -> Training regime
(generic head, "federated" modifier). `Contrastive Learning` -> self-supervised.
`Graph Contrastive Learning` -> self-supervised (the graph reading is the
Modality axis's job). This rule is mechanical, reproducible by an annotator, and
reproduces every placement s3 already asserts. It should be added to s8b.

### D5. s8b's uninformative branch has nowhere to live

s8b: "**Every axis gets its own uninformative branch**". s3 fixes exactly six
level-1 aspects and every one of them is a substantive aspect. `Machine
Learning` 250, `Deep Learning` 233, `Neural Networks` 19, `Artificial
Intelligence` 15 - ~600 mentions, the second-largest cluster on the axis - have
no node. I delivered it as a level-1 row explicitly marked administrative. The
schema should say whether residual branches count as level-1 nodes; as written,
"the six aspects" and "every axis gets an uninformative branch" cannot both be
satisfied.

### D6. `Generative Models` (83) is ruled both ways

- s4: "`Generative Models` (83) **stays an architecture** while `Image
  Generation` is a task."
- s5: `Diffusion Models` 13 -> **Task > Generation** ("implies a task ->
  translate"), and "**do not** map to both to hedge".

Diffusion models are generative models, so the two rules classify the same
concept into different axes, and the no-hedging clause forbids the obvious
repair. ~160 mentions (Generative Models 87, Diffusion 13, GANs 14, Generative
Modeling 9, VAEs, flows, energy-based, GFlowNets, score-based) turn on it.

The Frugal precedent settles it in the opposite direction from s5: a quantization
paper is Method=Quantization **and** Desired=Frugal, so a diffusion paper should
be Method=diffusion **and** Task=generation. I built `generative-models` as a
Method node on that reading. s5's asymmetry test ("does translating lose
information nothing else recovers?") also points this way: a paper on diffusion
sampler design that is translated to Task>Generation loses its entire topic.

*Recommended:* restrict s5's exclusivity clause to names whose Method reading is
the *uncertain* one (its original target was `Graph Neural Networks`, where the
architecture-research reading is a minority), and state that generative-model
families carry both.

### D7. `Active Learning` is listed in two rows of the same table

s3's Training regime row lists "active (9)" and its Data curation row lists
"active learning (9)". F2 says it is "currently parked in Training regime" and
argues for data. Resolved here to Data curation > Data selection: the
contribution is choosing what to label. One of the two table cells should go.

### D8. `Deep Learning Theory` vs `Machine Learning Theory`

s3 files `Deep Learning Theory` 7 under Model design and `Machine Learning
Theory` 8 under Learning theory. No annotator reproduces that from the strings.
I implemented a principled line instead - **capacity of a hypothesis class**
(Model design > Expressive power) vs **guarantee from a finite sample**
(Learning theory > Statistical learning theory) - which happens to keep both
names where s3 put them, but for a stateable reason.

### D9. Declared homonyms, beyond F7's two

F7 names `Policy Evaluation` and `Compression Algorithms`. The Method axis also
needs these declared before the run, not during it:

- `Distributed/Decentralized Optimization` - Training regime > Distributed
  training (a training run) vs Continuous optimization (a convergence rate).
- `Control Systems` 9 / `Control Theory` 2 - s7 files Control Systems under
  Application > Robotics; the machinery reading is Inference & optimization >
  Sequential decision-making.
- `Clustering`, `Density Estimation`, `Dimensionality Reduction` - Task values
  (what the output must be) and Method values (the fitting procedure).
- `Robustness` - Desired property (a demand) vs Adversarial ML (an attack model)
  vs OOD generalization (natural shift). Three axes, as F9 did for OOD.
- `Bandits` - Reinforcement learning (reward feedback) vs Online learning
  (regret on a stream).
- `Simulation` - Numerical methods (a solver), Synthetic data (training data),
  or Application (a domain's simulator). 15+ mentions, currently unruled.

### D10. Uncertainty is unassigned across axes

`Uncertainty Estimation` 12, `Uncertainty Quantification` 5, `Model Calibration`
2, `Bayesian Deep Learning` 2, ensembles ~9 - ~35 mentions. s2's Trustworthy AI
children (fairness, privacy, robustness, safety, interpretability,
accountability) do not include calibration, and s3 does not name uncertainty
either. "The model should know when it does not know" reads as a deployment
demand, which is s2's own positive test. Filed here under Probabilistic
inference; the schema should decide whether Trustworthy AI gains a calibration
child.

## 3. Blind spots kept despite little or no corpus support

Each is structural, not count-driven; the brief's rule is that corpus bounds
scope and exposes gaps but does not arbitrate.

1. **`inference-time-methods` (~16 mentions)** - the biggest hole. Prompting,
   in-context adaptation, RAG, tool use, chain-of-thought, decoding and
   test-time compute are not a learning signal, not a training regime and not a
   model structure; no AXES aspect accepts them. 2024 barely shows them
   (Prompt Engineering 6, In-Context Learning 4, RAG 1, Tool-Augmented 1); a
   2023-2026 re-extraction will make this one of the largest Method nodes. The
   node's positive test - **no parameter changes** - is sharp and survives.
2. **`numerical-methods` (~36)** - AI for science machinery (neural PDE solvers,
   operator learning, physics-informed models, differentiable simulation,
   surrogates). AXES names no numerical machinery anywhere despite s7 carrying
   astrophysics, chemistry and climate application branches that consume it.
3. **`synthetic-data` (7, all singletons)** - distinct from augmentation
   (fabricated vs perturbed). Growing fast; would have been deleted by any
   count rule.
4. **`scaling-behaviour` (5)** and **`compositional-generalization` (4)** - both
   named by AXES itself; the second is the worked example s2 uses to draw the
   Desired-properties line, so it cannot be dropped without removing the
   schema's own justification.
5. **`online-learning` (11)** and **`formal-verification` (19)** - standing
   field-level areas (COLT; safety-critical ML) under-represented in one
   institute-year.
6. **Mechanism design** (0 mentions) kept as a depth-3 example under Game
   theory; **AutoML** beyond NAS (~8) kept only at depth 3.
7. **ML systems** (~17: Deep Learning Compilers 2, Model Parallelism 2+1,
   Memory Optimization, Neural Network Acceleration, Deep Learning Frameworks,
   Efficient Inference, Hardware Acceleration 4) is **half-homed** - split
   between `model-efficiency` and `distributed-training`, with neither owning
   compilers, kernels or serving. Recommend an explicit ML-systems node under
   the D3 "Model transformation" aspect at the next revision. This is a real
   blind spot I did **not** fully close.

## 4. Corpus names I could not place with the schema's tests

- **`Representation Learning` 56** (+ Graph/Visual/Video/Protein/3D/Audio-Text
  variants, ~75 total). s4 rules it a **Task**. Method therefore records nothing
  for the single largest research-programme name in the corpus after the
  uninformative ones. Whether "learning a representation" is what the output
  must be or how the output is produced is genuinely undecidable by s4's test,
  and the ruling should at least be flagged as costly.
- **`Multimodal Learning` 15**, `Cross-Modal Learning`, `Multimodal Alignment` -
  s6 handles these on the Modality axis, but "how do you train across
  modalities" is a training-regime question with no Method node. Left off-axis.
- **`Neuromorphic Computing` 2, `Reservoir Computing` 2, `Stochastic Computing`,
  `Quantum Computing`, VLSI names** - a computational-substrate cluster. Parked
  in `neural-architectures`; no test in AXES distinguishes substrate from
  architecture, and Application > Computing & software systems is about software
  engineering as a field.
- **`Object-Centric Learning` 4, `Disentanglement` 3, `Identifiable
  Representation Learning`** - inductive-bias-driven representation programmes
  that straddle Learning signal (unsupervised), Model design (inductive bias)
  and Task (representation learning). Mapped to `unsupervised-learning`; low
  confidence.
- **`Model Evaluation` 7, `Evaluation Metrics` 7, `Machine Learning Evaluation`,
  `Metric Evaluation`** (~20) - s8b makes these mark_ignore as contribution
  type, but *metric design* is methodology. The line between designing a metric
  and running an evaluation is not drawn anywhere.
- **`Dataset Creation` 3 vs `Dataset Evaluation` 1** - same problem at the data
  end; `dataset-construction` is delivered with the boundary flagged.
- **`Ensemble Learning` 6 / `Ensemble Methods` 3** - a model-combination design
  pattern, a variance-reduction device, and an uncertainty estimator. Mapped to
  `probabilistic-inference`; defensible in at most two of the three readings.
- **`Sequence Modeling` 8, `Sequence-to-Sequence Models`, `State Space Models`** -
  F3 corrected RNNs to Method > Model design because they imply no modality; the
  same argument applies to these and s5 does not mention them.

## 5. Why these branching factors

- **Level 1 = 6 (+1 residual)**: fixed; not mine to justify. Given D1 I would
  rather see them as six axes.
- **Learning signal = 5**: one clean principle (what supplies the signal) with
  five values. AXES's list would have given 7-8 by keeping semi-/weakly-
  supervised and the RL variants as siblings; both demote to depth 3 because
  they differ on a *second* principle (amount of labelling; training structure),
  which is what the sibling test forbids.
- **Training regime = 7**: six regimes plus the constrained-learning node D2
  forced. At the boundary of comfortable; if D3's "drop data from the
  characteristic" and D2's general rule are adopted, constrained learning moves
  out and this returns to 6.
- **Inference & optimization = 8**, the widest. Justified because this aspect's
  characteristic ranges over genuinely different bodies of mathematics, and
  merging any two (discrete into continuous, causal into probabilistic) fuses
  principles rather than finding a relationship. Two merges were made rather
  than carried as siblings: uncertainty quantification into probabilistic
  inference, and empirical deep-net optimization into continuous optimization
  (same machinery, different object). Without those it would be 10.
- **Model design & analysis = 7**: the weakest parent on the axis, and the
  reason is D3, not the children. Under the recommended three-aspect split it
  becomes 3 + 3 + 3.
- **Learning theory = 4** and **Data curation = 5**: small aspects, small
  branching, and deliberately *not* padded or merged upward. Learning theory
  holds ~65 mentions against Learning signal's ~644; that 10x ratio is a finding
  about the institute, and flattening it into one "theory" leaf would destroy
  the quantity the survey measures.
- **Depth-3 examples**: every depth-2 node takes three plausible depth-3 labels
  that are recognizable subfield names, which is the granularity check. The one
  node where depth 3 strains is `reinforcement-learning`: value-based,
  policy-gradient, model-based, offline, multi-agent, hierarchical, safe and
  exploration are all real depth-3 siblings, so that node alone will want a
  depth-4 pass if the survey ever reports inside RL.
