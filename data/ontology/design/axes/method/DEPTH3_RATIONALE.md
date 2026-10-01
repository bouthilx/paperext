# Method axis, depth 3 — rationale

Extends `axes/method2/nodes.tsv` from 8 level-1 aspects + 42 level-2 nodes to
**61 level-3 nodes under 15 parents**. Level 1 and level 2 were fixed and are
unchanged; one existing cell was modified, the blank `characteristic` of
`inference-procedures`, which the brief permits.

Procedure, in the order the owner fixed it: **volume decided which node to open
next; volume played no part in how any node opened.**

- **Phase 1** — `DRAFT_PHASE1.md`, written with no corpus access: no
  `domain_names.tsv`, no tally, no reading of the `examples` column. It is the
  record and has not been edited since.
- **Phase 2** — corpus read, two questions only (cluster with no node → blind
  spot; node with no support → keep and flag).
- **Phase 3** — this file.

---

## 1. The selection rule, stated once

Every node admitted more than one principle of division. The rule used
throughout, and the thing to attack if this derivation is wrong:

> **A depth-3 sibling set must refine its parent's own characteristic, not
> import a different aspect's characteristic.**

M1, M4/M5 and the locked `Model efficiency` exception are all instances of that
rule being broken one level up. Where a node's most famous taxonomy divides by a
principle belonging to a *different* level-1 aspect, it was pushed to depth 4 and
the demotion declared. Second rule, from AXES §8b: **branch-level residence is
legitimate** — a depth-3 set need not catch the plain name of its parent.

---

## 2. The reinforcement-learning decision (the owner's worked example)

Three candidate principles:

| | principle | set |
|---|---|---|
| A | whether a model of the environment's transitions is used | model-based / model-free |
| B | what is parameterised | value-based / policy-gradient / actor-critic |
| C | who or what supplies the evaluative signal | the six children delivered |

**Between A and B, A wins**, on the field's own grounds: (i) A partitions all of
RL while B is only defined *inside* model-free methods — a model-based planner
may parameterise nothing, its policy being implicit in the planning procedure —
so B leaves part of the space unlabelled; (ii) the field's canonical taxonomy
chart literally nests B under A. **B is therefore depth 4 under A, never A's
sibling.**

**Neither A nor B is the depth-3 sibling set.** Both divide by *machinery* —
what algorithm runs, what object is fitted — under a parent whose level-1 aspect
is `Learning signal`, *what supplies the training target*. Admitting A at depth 3
puts a machinery-register set under a signal-register parent: audit defects M1
and M5 reproduced by me rather than inherited. So:

- **depth 3 = C**, the aspect's own principle at finer precision;
- **depth 4 = A**, as the first split inside `Online reinforcement learning`
  (and a cross-cut of `Offline reinforcement learning`, which is also either);
- **depth 5 = B**, under model-free.

**Declared cost, twice over.** A depth-3 report of this axis will not show a
model-based share, and the corpus does carry one (`Model-Based Reinforcement
Learning` 14 + variants ≈ 17). Phase 2 measured that and changed nothing,
because the cluster is *placeable* (it maps to `Online reinforcement learning`),
not homeless — and because counts may not re-cut a sibling set. If the owner
prefers the reportable cut to the principled one, A at depth 3 is the change to
make, and it costs `Learning from demonstrations`, `Learning from human
feedback` and `Multi-agent reinforcement learning` their nodes.

---

## 3. Phase 1 → phase 2 diff, change by change

**No node was added, removed, renamed, merged, split or reordered.** The
structure in `nodes.tsv` is the phase-1 draft exactly. Every phase-2 effect is an
annotation. Change by change:

| # | change | reason |
|---|---|---|
| 1 | `corpus_names` / `corpus_mentions` filled on all 61 rows from an explicit, verified name list per node | phase-2 measurement; indicative only, per AXES's own caveat and issue #89 |
| 2 | 10 nodes flagged **SPECULATIVE** in `notes` | phase-2 question 2: a node with no corpus support is kept and flagged, never deleted. Listed in §6 |
| 3 | 15 nodes flagged **THIN** (1–2 mentions) | same rule, weaker form; listed in §6 |
| 4 | Declared gap written into `intrinsically-motivated-rl`: ~7 generic *exploration* mentions that the node does not cover | phase-2 question 1, answered with a justified refusal (§4.1) |
| 5 | Declared gap written into `equivariant-architectures`: physics-informed networks have no depth-3 node | phase-2 question 1, justified refusal (§4.4) |
| 6 | `Generative Flow Networks` (4) mapped to `energy-based-models`, declared as the least comfortable mapping in that set | phase-2 question 1, justified refusal of a GFlowNet node (§4.5) |
| 7 | New homonyms declared in `notes`: **variational inequality vs variational inference** (4 mentions), **message passing** (belief propagation vs MPNN architecture), **self-distillation** (self-supervision vs compression), **sparse** (conditional routing vs pruning), **tensor decomposition** (model vs data), **game** (strategic interaction vs videogame — 8 of ~30 `game*` mentions are videogames), **diffusion** (generative vs Diffusion MRI), **concept** (concept-based models vs concept drift) | phase 2 surfaced each; a homonym note changes no node |
| 8 | Name-level traps written into `privacy-attacks` (~25 Differential-Privacy-family mentions must not land there) and `intermediate-reasoning` (~20 `X Reasoning` names are Task values) | phase 2; these are mapping rules, not structure |
| 9 | Mapping decisions recorded: `Sim-to-Real Transfer` (4) and cross-lingual transfer (4) → `domain-adaptation`; `State Space Models` → `recurrent-networks`; `Monte Carlo Methods` (5) → `mcmc` while `Monte Carlo Simulations` (5) leaves the axis as the declared `Simulation` homonym; `Language Modeling` (12) is a Task name and is *not* counted under `next-element-prediction` | phase 2 |
| 10 | `inference-procedures`.characteristic filled: *"the computation that produces the answer is spent at query time, on a model whose parameters are fixed"* | it was blank and the brief permits filling it |

**What phase 2 did NOT change, although it tempted:** `Continuous optimization`
holds ~54 mentions spread over 26 names that divide neatly by problem form
(stochastic 10, Bayesian 5, robust 4, constrained 3, bilevel 2, optimal
transport 4). That is exactly the evidence that would justify re-cutting
`Optimization` by problem form instead of by feasible set. It licenses nothing:
the rule is that counts may not merge, split, rename or reorder a sibling set.
Recorded, and left alone.

**One place where phase 2 supported a phase-1 call.** §12 of the draft rejected
the replay/regularisation/architecture taxonomy for `Continual learning`. The
corpus's replay surfaces turn out to be `Experience Replay` (2) and `Replay
Buffer` (1) — off-policy **RL machinery**, not continual-learning strategies. The
rejected taxonomy's apparent corpus support was not support for it.

---

## 4. Blind-spot question: clusters with no node, and why none was added

Phase-2 question 1 permits adding a node **or** justifying in writing why not.
Ten candidate clusters were examined. **None produced a new node**; each is
*placeable*, and each refusal is on a design rule that counts may not override.

1. **Generic exploration in RL, ~7** (`Exploration in Reinforcement Learning` 4,
   `Exploration` 1, `Exploration Strategies` 1, `Cooperative Exploration` 1).
   `Intrinsically motivated reinforcement learning` covers agent-generated
   reward, not ε-greedy or UCB. An `Exploration` node would divide by *how
   actions are chosen* — machinery — inside a signal-register set. Refused; the
   surfaces sit at branch level, and the gap is written into the node's notes.
2. **Model-based / model-free RL, ~17, and value/policy/actor-critic, ~14.**
   Placeable at depth 4/5 (§2). Refused: second principle.
3. **Neural architecture search, 6.** Divides by *how the architecture was
   obtained*, not by how it is wired. Refused; branch-level resident, as the
   level-2 row already provides.
4. **Physics-informed networks, ~3** (`Physics-Informed Neural Networks` 2,
   `Physics-Constrained Deep Learning` 1). They constrain the *objective*, not
   the wiring. Refused under the connectivity principle; branch level, or
   machinery > optimization. This is the clearest cost of the principle: three
   of the seven families the parent's own note claims — physics-informed,
   object-centric, neuromorphic — have no depth-3 node.
5. **Generative flow networks, 4.** Refused on **specificity**: one method family
   beside six field-sized ones. Mapped to `energy-based-models` (an amortised
   sampler for a given unnormalised reward) and declared as the least
   comfortable mapping in that sibling set. This is the refusal I am least sure
   of — it is an institute-native method with a real community.
6. **Neuromorphic and spiking, 3.** Divides by *component type*, and spiking
   units are not differentiable, so they strain the parent's own
   characteristic. Refused; branch level.
7. **Problem-form optimization families, ~30.** Refused: second principle (§3).
8. **Communication efficiency, 4.** Belongs to `Federated learning` /
   `Distributed training`, not to a change in model form. Placeable elsewhere.
9. **Few-shot 16 / zero-shot 5.** They name the *setting*, not the adaptation
   mechanism; cross-cut, branch level on `Meta-learning`. This is why
   `Metric-based meta-learning` measures zero beside a 16-mention `Few-Shot
   Learning`.
10. **Experience replay, 3.** RL machinery, not continual learning (§3).

Two side effects worth recording, both improvements to problems the level-2
derivation left open:

- `Multi-Agent Systems` (11), declared **unplaced** by `RATIONALE.md` §7, now has
  the two homes that ruling asked for: `Multi-agent reinforcement learning` and
  `Game theory > Learning in games`.
- `Tensor Decomposition` / `Tensor Factorization` (2), also declared unplaced,
  now have `Model efficiency > Low-rank factorisation` for the
  model-compression reading, with the numerical-machinery reading declared as a
  homonym.

---

## 5. The 15 expanded nodes: principle kept, principle rejected

| parent | principle kept (the `characteristic`) | principle rejected, and where it went |
|---|---|---|
| Reinforcement learning (6) | who or what supplies the evaluative signal | model-based/model-free → depth 4; what is parameterised → depth 5 (§2) |
| Neural architectures (7) | which connectivity pattern routes information | how the architecture was obtained (NAS) → branch level; which component type (spiking) → branch level |
| Optimization (2) | the structure of the feasible set | the form of the problem (stochastic/robust/bilevel/constrained); what information is used (first/second/zeroth order); what the decision variable is → all depth 4 |
| Generative models (7) | how the distribution is specified | what is generated → Modality/Task; how it is trained (adversarial/MLE/denoising) → a learning-signal principle |
| Self-supervised learning (5) | what pretext target is constructed | which modality the pretext is built for → Modality; joint-embedding vs generative → Model design |
| Probabilistic inference (5) | how the posterior is obtained | what the model is (Bayes nets, GPs) → Model design; probabilistic programming (a language) → branch level |
| Transfer learning (2) | what differs between source and target | what is carried across (instance/feature/parameter — the canonical survey's other axis) → depth 4; what target-side access exists → depth 4 |
| Interpretability (4) | the vocabulary in which the account is stated | local vs global → cross-cut; post-hoc vs by-design → the by-design half is Model design |
| Model efficiency (4) | what is removed or replaced | which resource is saved → Desired properties > Frugal AI; when the saving is applied → a stage principle (M5's shape) |
| Adversarial ML (3) | which attack surface the adversary reaches | attack vs defence → cross-cut (a defence maps to the attack it forestalls); threat model → cross-cut |
| Meta-learning (3) | what the outer loop produces as the adaptation mechanism | a flat "what is meta-learned" list → mixes specificities, duplicates Optimization and Neural architectures; the problem setting (few-/zero-shot) → cross-cut |
| Continual learning (3) | what changes from one step of the sequence to the next | replay / regularisation / parameter isolation → depth 4 (see below) |
| Causal inference (3) | which part of the causal model is unknown | which identification assumption is used → depth 4 under effect estimation |
| Game theory (4) | what the work does with the strategic interaction | the kind of game (zero-sum/general-sum; normal/extensive form) → depth 4; it would leave mechanism design homeless |
| Inference procedures (3) | which part of the query-time computation is manipulated | — inherits the parent's declared stage-shaped strain rather than repairing it |

**The hardest rejection** is `Continual learning`'s. Replay /
regularisation / parameter isolation is the taxonomy every survey uses and would
serve a reader better. It is rejected because its three members each belong to a
*different* level-1 aspect — replay is data curation, regularisation is an
objective modification under Optimization, parameter isolation is an
architecture — which is M5 in pure form. The delivered set (task-, class-,
domain-incremental) is the field's other standard taxonomy and refines the
parent. It also costs the most: two of its three children measure zero.

---

## 6. Speculative and thin nodes kept

**Zero corpus support (10), all kept and flagged; never a deletion ground:**
`Masked prediction`, `Next-element prediction`, `Transformation prediction`,
`Message passing`, `Metric-based meta-learning`, `Task-incremental learning`,
`Domain-incremental learning`, `Learning in games`, `Mechanism design`,
`Test-time search`.

Four of these are worth a sentence, because their emptiness is informative
rather than accidental:

- `Masked prediction` and `Next-element prediction` are two of the most-used
  methods in the field. Their absence says how researchers *name their research
  domain*: they write `Self-Supervised Learning` (73) and `Language Modeling`
  (12, a Task name). This is the `contributed` vs `used` problem of issue #89
  appearing at depth 3.
- `Message passing` measures zero because the corpus's only message-passing
  surface is `Message Passing Neural Networks` (1), a GNN architecture that
  AXES §5 translates to Modality. A pure homonym, now declared.
- `Metric-based meta-learning` measures zero beside `Few-Shot Learning` (16),
  because few-shot names the setting and not the mechanism.
- `Test-time search` is owner-sanctioned (AXES §3 names "test-time computation"
  in the ruling that created its parent) and predated by the 2024 corpus.

**Thin, 1–2 mentions (15):** `Implicit-depth architectures` (1),
`Autoregressive models` (1), `Self-distillation` (1), `Sequential Monte Carlo`
(1), `Feature attribution` (2), `Concept-based explanation` (2),
`Example-based explanation` (1), `Low-rank factorisation` (2), `Poisoning
attacks` (1), `Privacy attacks` (2), `Optimization-based meta-learning` (1),
`Class-incremental learning` (1), `Effect estimation` (2), `Cooperative game
theory` (1), `Intermediate reasoning` (1).

`Feature attribution` and `Effect estimation` are the two that should worry a
reader most: each is the *centre* of its literature and each measures 2, because
the branch's mass sits at branch level (`Explainable AI` 10, `Interpretable
Machine Learning` 9, `Model Interpretability` 7, `Interpretability` 6; `Causal
Inference` 16). That is AXES §8b's branch-level residence working as designed,
and it is the dominant fact about reporting these two branches at depth 3.

---

## 7. Level-2 nodes deliberately left as leaves (27 of 42)

- **Supervision paradigms** — `Supervised`, `Semi-supervised`, `Weakly
  supervised`, `Unsupervised learning`. Each names a single supplier of the
  target and has no finer division of that kind. `Unsupervised learning`'s
  apparent children (clustering, density estimation, dimensionality reduction —
  `Manifold Learning` 8, `Dimensionality Reduction` 4 in the corpus) are AXES
  §8b's **declared Task-axis homonyms**; putting them here imports the Task axis.
- **Training-regime leaves** — `Multi-task`, `Federated`, `Distributed
  training`, `Online learning`. Their natural sub-divisions name another aspect:
  federated by *what is communicated* (machinery), multi-task by *how losses are
  combined* (Optimization).
- **Classical-AI and non-neural machinery leaves** — `Logical inference`,
  `Search`, `Planning`, `Evolutionary computation`, `Symbolic models`, `Kernel
  methods`, `Ensemble methods`. Each has a real sub-structure (planning into
  classical / probabilistic / motion; evolutionary into GA/GP/ES/swarm;
  ensembles into bagging/boosting/stacking). `RATIONALE.md` §6 already declares
  several the thinnest nodes on the axis, kept on external breadth alone;
  adding depth beneath a node kept on breadth asserts a resolution the axis
  cannot carry. **`Ensemble methods` (12 indicative mentions) and `Planning` are
  the two to open first** if a later extraction makes them large.
- **Claim-register leaves** — `Formal verification`, `Uncertainty
  quantification`, `Generalization`, `Sample complexity`, `Expressivity`,
  `Training dynamics`, `Scaling behaviour`. These are already question-sized;
  that was the M6 fix. Splitting `Uncertainty quantification` into Bayesian /
  conformal / ensemble would put a *method* set under a *claim* parent — M1 one
  level down.
- **Data-curation leaves** — `Data synthesis`, `Data selection`, `Annotation`.
  One level below the M7 fix, `Data selection`'s candidates (active learning 9,
  curriculum 3, coreset, weighting) divide by *what decides the selection*, a
  second principle, and active learning straddles it.
- **Administrative** — `Generic field names`, `Generic technique names`.
  Excluded from shares; depth would be meaningless.

---

## 8. My own granularity audit of my own output

Test: *are these the same kind of thing, at the same level of specificity, and
does any sibling exist only because it was large in this corpus?*

**The volume test passes, and can be checked mechanically.** The largest node I
opened (`Reinforcement learning`, 452) got 6 children; the second largest
(`Optimization`, 227) got 2 — fewer than `Game theory` (36), which got 4. No
sibling was created, kept, merged or split on a count; 10 children have no
corpus support at all and 15 more have one or two mentions.

**Sets I am confident in** (one principle, one specificity level, no overlap):
generative models' seven, causal inference's three, model efficiency's four,
interpretability's four, probabilistic inference's five, adversarial ML's three
(externally checked against the NIST evasion/poisoning/privacy taxonomy),
transfer learning's two, optimization's two.

**Sets I am NOT confident in — declared, not laundered:**

1. **`Multi-agent reinforcement learning` as a signal source.** The honest
   reading is *how many agents*, a second principle; it is admitted on the
   co-learner non-stationarity reading. Declared in the phase-1 draft before any
   count was seen. The single weakest node I add.
2. **`Continual learning`'s three scenarios.** Two of three measure zero, and
   the rejected mechanism taxonomy is the one the field actually writes surveys
   about. If any of my sets is overturned, I expect it to be this one.
3. **`Optimization` at two children.** Principled, and nearly useless to a
   report: one child will hold the great majority.
4. **`Autoregressive models` vs `Graphical models`.** An autoregressive
   factorisation *is* a graphical-model factorisation over a complete DAG. Two
   traditions, one mathematics.
5. **`Masked prediction` vs `Next-element prediction`.** Both withhold part of
   the input; only *which* part differs. Arguably one node.
6. **`Search` vs `Test-time search`** — a new cross-branch strain I introduce:
   tree search over generations is state-space search run at query time, so
   `Inference procedures > Test-time search` and `Computational machinery >
   Search` will compete for the same surface. It follows from the parent's
   declared stage-shaped strain and is not repaired here.
7. **`Conditional computation`'s extension.** It is defined by input-conditional
   routing, but absorbs modularity surfaces (`Modular Neural Networks`, `Neural
   Network Modularity`, `Hypernetworks`) that are modular without being
   conditional.
8. **`Energy-based models` absorbing GFlowNets** (§4.5).
9. **Three families claimed by the `Neural architectures` note have no child**
   (physics-informed, object-centric, neuromorphic). The set is not a partition
   of what its parent holds.

**Register check.** Every delivered set refines its parent's characteristic
(§1); the two places this bends are `Inference procedures`' children, which
inherit an owner-declared stage-shaped parent, and `Neural architectures`, whose
own parent `Model design` already carries the locked `Model efficiency` register
exception one level up.

**Branching factors**

| parent | children | | parent | children |
|---|---|---|---|---|
| Neural architectures | 7 | | Adversarial machine learning | 3 |
| Generative models | 7 | | Meta-learning | 3 |
| Reinforcement learning | 6 | | Continual learning | 3 |
| Self-supervised learning | 5 | | Causal inference | 3 |
| Probabilistic inference | 5 | | Inference procedures | 3 |
| Interpretability | 4 | | Optimization | 2 |
| Model efficiency | 4 | | Transfer learning | 2 |
| Game theory | 4 | | | |

61 level-3 nodes under 15 parents: **mean 4.07, max 7, min 2**. 27 of 42
level-2 nodes stay leaves. No set exceeds 7, against the level-2 maximum of 8,
so AXES §9's "many siblings means specialising too early" is not newly strained.
