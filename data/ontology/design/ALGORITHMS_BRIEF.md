# Algorithms dimension — design brief

Written 2026-10-06, after the models dimension was built. Companion to
`MODELS_BRIEF.md` (the entity model), `MODELS_AXES.md` (what models became),
`MODELS_DERIVATION_BRIEF.md` (the method and R1–R7) and `PROCESS.md` (how the
domains design was run).

Issue **#96**. Siblings: **#95** models · **#91** domains · **#93** datasets ·
**#94** extraction (runs, schema v5).

**Read this file first when resuming.** It is the handover. Phase 1 is done —
`axes_algorithms/SYNTHESIS.md` carries what the two runs agreed on, what they
overturned in B.2, and the owner rulings that followed.

---

# Part A — where this dimension sits

## A.1 Why it exists

`models/v0`'s `other algorithms` (110 children) was read as a junk drawer. It is
a **type confusion**: algorithms were never given their own entity type, so
`ant colony optimization`, `c51` and `bm25` shared a tree with `blip`. No
restructuring *within* one tree fixes that.

Measured cost of the split: **114 of 260 recurring corpus names route here**,
including the corpus's most-mentioned name in the model slot, `simclr`
(20 papers). Nearly half of what sits in `models[]` today is not a model.

## A.2 The paper annotation this serves

```
paper
├── research_fields[]   term + role                                  #89
├── models[]            term + is_contributed / is_executed / is_compared
├── algorithms[]        term + role                          NEW,    #94
├── datasets[]          term + role + size + per-sample properties   #93
├── libraries[]         term + role
└── runs[]              references into the lists above, plus the
                        configuration and its cost                   #94
```

Entity lists are dimension tables; `runs` is the fact table. **(Model, Algorithm)
pairs are why runs exist** — three optimisers on three models is nine runs over a
3×3 grid of two independent entity types, not nine models.

**`execution_mode` no longer constrains *whether* a run has algorithms** — an
`inference` run carries its preprocessing and its decoder. It constrains which
**roles** may appear: no `parameter update rule` under `inference`. The invariant
survives the widening only because `role` is an axis (B.2); before the widening
it was checkable from entity type alone. This is the clearest argument that the
role axis is load-bearing rather than decorative.

## A.3 Settled, inherited from the models work — do not re-litigate

- **Admission rule.** A term is a **model** only if it names a *separable learned
  object* — parameters describable and runnable independently of the procedure
  that produced them. Otherwise it is an **algorithm**, and a run may carry an
  algorithm with **no model**.
- **`algorithms[]` holds every procedure a run executes, not only learning.**
  *Widened twice by the owner, 2026-10-06* — from "strictly learning algorithms",
  through a learning-procedure scope, to the **participant rule**:

  > An algorithm is a **named procedure a run executes**: preparing the data,
  > producing or adapting the learned object, or using it to produce outputs.

  So data preprocessing, experience generation, configuration search,
  post-training compression, **decoding and test-time search** are all in. Beam
  search is in: it decides which token is selected, so two papers reporting the
  same metric under different decoders are not reporting the same number, and
  that variance is exactly what a review of this kind has to see.

  Out are the things that are not procedures — datasets, libraries, hardware, and
  the learned object itself. This defines the dimension by **entity type**, not by
  a boundary in the pipeline, which is why it needs no test about *when* a
  procedure runs. It restores the symmetry of the four lists: models are the
  learned object, datasets the data, libraries the implementations, algorithms the
  procedures.

  **Named procedures only** (`CutMix`, never "we normalised the images"). Naming
  is what bounds the dimension now that topic does not.
- **Backbone test.** A paradigm that leaves network topology unchanged and alters
  only the **training objective or sampling procedure** is an algorithm. Settled:
  GFlowNet (its papers use Transformer backbones — the owner's evidence),
  diffusion, the SSL objectives, GAN, LoRA, distillation, instruction tuning,
  reconstruction, the RL update rules.
- **Name the network.** Where a training-paradigm paper also contributes an
  architecture, that architecture is a *model* entity under the name the paper
  gives **that network** (MUDiff → MUformer). Where none is named, the models
  axes describe it. Where there genuinely is none (Crystal-GFN), the absence is
  recorded — "algorithm with no model" is a legal state, not a gap.
- **A network whose output drives a procedure is a MODEL, not an algorithm** —
  learned optimizers (`LAgg-A`, `LOpt-A`), hypernetworks (`GHN-3`), learned
  samplers. The procedure consuming its output is the algorithm.
- **Counting is non-exclusive** (E1, #16): a paper maps to a *set* of
  categories-at-cut and columns overlap. So multi-parent and multi-axis
  membership cost nothing semantically. (`analysis/rollup.py` returns
  `dict[str, str]` and needs `dict[str, set[str]]` — bounded, not yet done.)
- **The shared layer between dimensions is vocabulary, not hierarchy.** Nothing
  is rooted in anything; each dimension is re-derivable alone.
- **Never rebalance**, and **no root-count bound**. A node holding most of the
  corpus is a finding to report.
- **The ontology covers the field, not the corpus.** A node with no corpus
  support is flagged speculative and **kept**.
- **Non-ML entries are `out-of-scope`**, deliberately distinct from
  `misextraction`.

## A.4 MCTS — a boundary case that dissolved

It was declared because the old scope needed a line between training-time target
generation (in) and test-time planning (out). The participant rule needs no such
line: MCTS is in either way, and so is beam search. The widening removed a
distinction the design was straining to draw.

What stays on record is a *different* objection, untouched by this: MuZero,
DreamerV2, PlaNet and QMIX were ruled algorithm-side although each specifies
networks, and a reviewer wanting "proportion of papers using Dreamer" countable
in the **models** dimension will disagree.

---

# Part B — the derivation

## B.1 Do not assume the models shape transfers

Models ended as four axes — lineage · connectivity · topology · attributes —
because three candidate single-tree level-1 characteristics were each rejected
for being a property of something *other than the model*: a computational
primitive is a property of a **layer**, a data structure of the **application**,
a function learned of the **use**.

**Those reasons are model-specific.** Algorithms may want fewer axes, more, or
different ones, and may well want a single tree. Derive it; do not port it.

The transferable instrument is the **axis admission test**:

> Two entities can differ on it while agreeing on every other → it is an **axis**,
> not a tree level.

That is what caught `Spiking neural network` sitting beside `Transformer`
(a spiking CNN exists), and then `Autoencoder` beside it (a convolutional *and* a
transformer autoencoder exist).

## B.2 Decided in the structural discussion (owner, 2026-10-06)

### The sibling test for this dimension

The models axis-admission test has a sharper, mechanical form here:

> **Siblings are mutually substitutable** — swap one for the other and the rest
> of the run still makes sense.

*Revised after phase 1.* It first read "two algorithms that run together cannot
be siblings", which is over-strong: people stack RandAugment, Mixup and CutMix,
and those are siblings. Co-occurrence is only *evidence* of non-siblinghood, and
only when the two are not substitutable. Mixup ↔ CutMix substitutes;
PPO ↔ Adam does not.

`PPO` is not a sibling of `Adam`. PPO fixes the objective (clipped surrogate) and
the experience source (on-policy rollouts), then delegates the parameter step to
Adam. A tree that makes them siblings asserts a choice nobody ever makes. A real
setup stacks several algorithms at once — LoRA + instruction tuning + AdamW is
three algorithms, three slots, one run.

### Faceted, on four axes — and *not* by porting models

The honest single-tree candidate was **learning signal** (supervised / RL /
self-supervised / unsupervised / causal), which is how the field talks. It fails
on this vocabulary: at least 13 of the 114 are **signal-agnostic** —
`clipped-sgd`, `clipped-sgda`, `clipped-sstm`, `clipped-seg`, `byz-vr-marina`,
`gradient descent`, `slowmo`, `papa`, `fedavg`, `lora`, `polytropon`, `mixup`,
`mixupe` — and the widened scope (A.3) adds the preprocessing entries to them.
Under a signal tree they are homeless: the same defect as the efficient-attention
families in models, caught before building instead of after.

The second failure is combinatorial, and it is the spiking-CNN case again: **`SPR`
is an RL algorithm that learns from self-prediction**; `ConSpec` is RL that learns
from contrast. An RL tree or an SSL tree misfiles both.

| axis | what it is | cardinality |
|---|---|---|
| **lineage** | descent — `REINFORCE → A2C → PPO`; `DQN → Rainbow → {C51, QR-DQN, IQN}`. A **forest with no imposed top layer**, and *not* the backbone: both phase-1 runs demoted it, because most of this vocabulary (CutMix, EM, IPW, k-fold CV) descends from nothing. | parent set |
| **signal** | split in phase 1 into **source** (where the target comes from) × **form** (how prediction and target are compared). MoCo and BYOL agree on source and differ on form; supervised and autoregressive agree on form and differ on source. (The pinning pass corrected this: *SimCLR*/BYOL differ on both facets, because BYOL's target comes from the EMA copy.) Does **not** union up the chain — DDPM → DDIM falsifies that, and on **every** axis, not just this one: a descendant that changes role inherits nothing. | per-node, pinned |
| **role** | which slot of the pipeline it fills: data preparation · experience generation · objective/estimator · parameter update rule · parameter subset · coordination · configuration search · compression · **output generation/decoding** · **test-time search** · **test-time adaptation** | many, unions |
| **attributes** | on/off-policy · model-based/free · value/policy · online/offline · centralised/decentralised · federated | per-family, as in models |

Four axes again — flagged rather than hidden. Phase 1 kept the *set* and
rebuilt three of the four; see `axes_algorithms/SYNTHESIS.md` §2. But only **lineage** is ported, for
a stated reason: the aggregation need is identical. `role` and `signal` are new
and come from this vocabulary; connectivity and topology have no analogue here.
The axis *values* above are a starting hypothesis for phase 1, not a fixed list.
Axes may carry internal hierarchy, as the models axes do.

**`role` survives the test that killed three models characteristics.** Those were
rejected for being properties of a layer, an application or a *use*. Does Adam
ever fill a slot other than the parameter update? Does mixup ever do anything but
prepare data? Does PPO ever not be the policy objective? Role is stable per
algorithm, not per use.

### RL is a value, not a level

`reward` is a value on **signal**; the RL families live on **lineage**. RL is ~40%
of this vocabulary and was 112 of v0's algorithm nodes — under *never rebalance*
that is a finding to report, not a reason to build an RL root. Making it a value
is what lets `SPR` carry both `reward` and `agreement`.

### Optimizers are a role value, not a separate kind

Not libraries, not siblings of PPO. The `clipped-sgd` / `clipped-sstm` /
`byz-vr-marina` cluster is optimisation-theory contribution with real lineage
(convergence under heavy-tailed noise, under Byzantine workers) and belongs.

### Three owner rulings

1. **Classical ML and statistics are covered**, not only deep learning. `t-sne`,
   `phate`, `k-nearest neighbors`, `erm` and the CATE meta-learners
   `s-/t-/x-/r-/dr-learner` are in, and the structure must have somewhere to put
   them that is not an afterthought.
2. **Scope is every procedure a run executes** — the participant rule in A.3.
   This admits `t-sne`/`phate` (running them produces the embedding),
   `k-nearest neighbors` (nonparametric: an algorithm with no model, a legal
   state) and `orbgrand` (channel decoding is output generation). **Nothing in
   the 114 is excluded by scope.** What the dimension excludes is non-procedures,
   and unnamed descriptions of procedures.

   Precision is not lost to the widening: counting is non-exclusive and `role` is
   an axis, so "training-time algorithms only" is a filter, not a scope decision.
   That is the point of putting role on an axis instead of in the tree.
3. **An ambiguous bare string gets no node.** `iql` is both Implicit Q-Learning
   and Independent Q-Learning. Only the spelled-out forms are nodes; resolving
   the bare string needs **paper context**, which makes it an extraction-time
   question, not an alias. Ties are rejected, never guessed (B.5).

## B.3 Method

Reuse `PROCESS.md` §2 and `MODELS_DERIVATION_BRIEF.md` §5.

1. **Two-phase protocol.** Draft from the field's own structure with **no corpus
   access**, freeze it in `DRAFT_PHASE1.md` with a timestamp **before** opening
   any data file, then consult the corpus for **two questions only** — blind
   spots to add, speculative nodes to flag. The corpus **bounds scope and
   exposes blind spots; it never arbitrates.** Verify the freeze from the
   transcript's tool-call order, not from the agent's claim.
2. **One principle of division per sibling set**, stated as the node's
   `characteristic`, wherever a sibling set comes from division rather than
   descent.
3. **A child sibling set refines its parent's characteristic**, never imports
   another aspect's.
4. **Volume decides which node to open next; it never shapes how it opens.**
5. **External classifications supply vocabulary and breadth, never arbitration.**
6. **Forbid `models/v0`** and the domains axes (the B.6-style comparison comes
   after), plus `proposed_categories.csv` and `categorized_models.json`.

## B.4 The instruments, in order of how much each caught in models

Every one of these found a class the others could not. Use all of them.

| instrument | what it caught in models |
|---|---|
| **Pinning every node to its axes** | 4 missing connectivity values; efficient-attention families homeless on all four axes |
| **Reading worked examples** | Longformer ≡ BERT; VQ-VAE both Deterministic and Stochastic; the per-family resolution rule |
| **The owner reading those examples** | ResNet's skip connection unrepresentable; `Single stack` a neural-centric misnomer |
| **Placing real corpus names** (260) | three inheritance defects, none visible to a validator |
| **An `--audit` mode** | 7 nodes resolving by `parents` column order, or to no topology at all |
| **Structural validation** | a one-child division node (R4) |

**The cheapest by far was asking for worked examples.** If this dimension gets
one check, make it that one.

## B.5 Defects not to repeat

- **Inheritance needs an escape hatch.** Union inheritance gave a child no way to
  deny its parent (`MLP-Mixer` resolved to `Self-attention`; `FFJORD` to
  `Standard convolution`). Negative pins (`!value`) fixed it.
- **Cardinality is per *family*, not per axis.** A blanket single-value rule
  fixed VQ-VAE and regressed EGNN, which really is permutation- *and*
  Euclidean-equivariant.
- **Never resolve ambiguity by column order.** Multi-parent topology was being
  decided by the order of the `parents` field. An audit must report it, not
  silently pick.
- **Never infer an alias from string similarity.** Token-set matching paired
  `gpt-j` with `GPT-4`; an unguarded morphological rule assigned
  `bayesian neural networks` to the `Bayesian network` graphical-model node.
  Aliases are **written**, with claim priority, and ties are rejected.
- **A corpus-count file leaks into phase 1.** Publish characteristics separately.

## B.6 The comparison, which matters more here than it did for models

Run a `CORRESPONDENCE.tsv`-style comparison against the **domains** ontology
once this is derived — and expect a different answer.

For models it found **zero of 358 lineage nodes sharing a name with any domains
axis node**. But `Method › Model design › generative-models` and
`model-efficiency` both route **algorithm-side**, and the domains `Method` axis
has `Learning signal › Reinforcement learning` (452 mentions), self-supervised
learning, and an `Inference & optimization` branch. **Roughly a third of the
domains `Model design` subtree, plus much of `Learning signal`, meets this
dimension.** This is where the duplication question has teeth.

The distinction to hold onto: **domains holds research topics, this holds
entities.** `Learning signal › Reinforcement learning` means *this paper
researches RL*; `PPO` is a thing a paper *used*. Filing PPO under the domains
node would make every paper that merely uses PPO into RL research — the
contributed-vs-used error #89 exists to prevent.

---

# Part C — inputs and open items

## Inputs

- **`data/ontology/design/axes_models/ROUTING.tsv`** — the 114 `algorithm` rows,
  deduplicated to 105 names in `axes_algorithms/phase2/VOCABULARY.tsv`
  (count-free, alphabetical). It also carries 13 `unsure` rows, all of which
  turned out to be model-side questions.

  **This sample is biased, and the bias is measured.** Every one of those names
  was extracted from the `models[]` slot by an agent prompted to find *models*,
  so the sample over-represents algorithms with the surface form of a named
  system and under-represents everything else. Against the ontology's own
  regions:

  | region | % of ontology | % of corpus hits |
  |---|---|---|
  | reinforcement learning | 10% | **52%** |
  | classical ML / statistics | 23% | 9% |
  | optimisation / systems | 16% | 6% |
  | data preparation | 14% | 6% |
  | inference / adaptation | 26% | 18% |
  | generative / SSL | 10% | 9% |

  RL over-represented ~5x; classical, optimisation and data preparation each
  under-represented ~2.5x; **decoding and evaluation have zero hits**. Direct
  evidence rather than inference: `adam` and `adamw` were extracted into
  `libraries[]` (a #94 defect). That misrouting *is* the bias.

  **Consequences, binding on phase 2:**
  1. **Blind-spot detection is still valid.** A corpus name with no node is a
     real gap however the sample was drawn; bias cannot manufacture a false
     positive. 77 of the 105 match no node today.
  2. **Speculative flagging from corpus absence is INVALID — do not do it.**
     Beam search's absence from a models-slot sample says nothing about beam
     search. Treating absence as evidence would re-bias the structure toward
     model-like algorithms, defeating the "field, not corpus" rule through the
     back door after it survived the front.
  3. **This dimension has no usage evidence at all** — not weak evidence, none.
     Do not report frequencies derived from this sample as if they described the
     field. Real evidence requires re-extraction with an algorithms-aware prompt
     (#94, schema v5), and until that runs the structure stands on field
     coverage alone.
- **The corpus is in a different checkout**:
  `/home/bouthilx/projects/paperext-llm-backend/data/mdl/queries/openai/legacy-2024/`
  (2110 files) + `vertexai/` (102) = **1999 distinct papers**. This working copy
  holds only 102 extractions, so nothing here can be recomputed from it.
- `model_names.tsv` — 2483 names / 3549 mentions, with the header flagging that
  the corpus predates the model/algorithm split.

# Part D — sequencing (owner, 2026-10-07)

Four phases, in this order:

1. **Design the base ontology from field knowledge** — done: 1697 lineage nodes,
   four axes, pinned, `resolve.py --audit` clean.
2. **Plan and run the extraction** — `algorithms[]` with an algorithms-aware
   prompt (#94, schema v5).
3. **Revise the ontology** against real data.
4. **Execute the categorisation.**

**Why step 3 exists.** With reliable usage data the ontology could go straight to
categorisation. We have none (Part C: the only sample was drawn through the
`models[]` slot and is biased ~5x toward RL, with zero hits on decoding and
evaluation). So a revision pass is budgeted rather than hoped for.

**This changes the bar for step 1.** The structure does not have to be right. It
has to be *good enough to write an extraction prompt against* and *cheap to
revise*. That reorders the remaining work by whether data could speak to the
question at all.

## D.1 Fix now — logical defects, which no amount of data would settle

Each of these is wrong on its own terms: a pin that contradicts its own test, a
value that carries no information, an inheritance rule that manufactures work.

- The signal axis takes **(source, form) pairs, one per objective term**. SPR's
  cross-product licenses combinations the method does not have, data or no data.
- `S.src.ext.obs` — 169 nodes are parked on an interior node for want of
  "the response variable was measured in the world".
- `A.deriv.fixed` — `A.deriv.closed`'s negative test is "iterating a step rule
  to convergence", and ~60 nodes carry it *while iterating a fixed-point map*,
  because phase 1's EM worked example set the precedent.
- `R.fit.perturb` (dropout and five siblings have no role) and `R.fit.fixpoint`
  (`R.fit.update` demands a gradient, so value iteration, CFR and Sinkhorn have
  none).
- **Delete `R.adapt`**: it resolves on exactly the 20 `L.tta` descendants, so it
  cross-cuts nothing and only double-counts.
- Split the three conflations whose own tests convict them: `A.uncert`
  (parameters vs per-example latents), `A.outspace` (element type vs joint
  structure), `A.topology` (discipline vs parties).
- ~~`divides` edges do not propagate axis values~~ — **this diagnosis was too
  broad and is withdrawn.** Only 19 of 170 denial-carrying nodes are multi-parent
  at all, and the worst offenders (`M.ddim` with 8 denials) are single-parent.
  What the denials actually localise is narrower and more useful: **a family that
  grouped by goal or mechanism instead of by a characteristic**, which is itself
  multi-parent, and whose children then disagree wildly on denial count. Two such
  families accounted for 45 denials: `L.score.sample` held training-free samplers
  beside training procedures (goal: cheaper sampling), `L.derivfree.anneal` held
  an optimiser beside an MCMC sampler (mechanism: annealing). Replaced by:
  **an explicit `value_parent`** naming the parent values flow along, declared
  and never inferred from `parents` column order, and required by the audit only
  where parents actually conflict. 18 were derived from the denial evidence --
  a denial is the node saying which parent was wrong. Denials 281 -> 200.
- Widen `S.form.post`'s test, which says "approached by sampling" and so excludes
  the closed-form posteriors of GPs, Kalman filters and Laplace approximation —
  ~25 of its own 53 pins.
- Dissolve `L.optdisc` (12 of 20 nodes roleless; members share one attribute).
- Clear ~25 duplicate node pairs and rename one of `R.exec` / `A.exec`.

## D.2 Settle before the extraction — they change what gets collected

- **Dropout vs batch norm.** Dropout is in and batch norm is out with nothing in
  either dimension explaining why. An extractor cannot be told what to record
  until this is ruled. *Open.*
- **Composites.** The extractor records what the paper says (`RLHF`), and the
  ontology expands it; `expands_to` must hold **node_ids, not free text**, or the
  expansion is unusable at roll-up time. The 65 unmarked bundles can wait, but
  the mechanism cannot.
- **Open vocabulary.** The prompt must ask for free-text names and the paper's
  own framing, and use this ontology only for *scope* and for examples of the
  kinds of thing in range. Handing over a closed list makes step 3 circular: the
  extractor would find only what we listed, and the revision would rubber-stamp
  it. The 77 currently unmatched names exist because the models extraction was
  open.
- **Known misroutings are the acceptance test** for the new prompt:
  `adam`/`adamw` in `libraries[]`, `pytorch` in `models[]`.

## D.3 Defer to the step-3 revision — only data can settle these

- `slot` vs `bundle` for the 65 candidates: how often is a bundle cited as a
  unit? Phase 1 named this and said it could not be tested without data.
- Whether role roll-ups are comparable across the classical and deep branches
  (measured 1.69 roles per classical method against ~1.5, but the shape of the
  excess is what matters).
- Which of ~346 "may be a description, not a named procedure" flags are real —
  the test is whether anyone cites it.
- Whether thin attribute families (`A.hier` non-default on 6 of 173 nodes,
  `A.exec` on one subfamily) earn family status.
- Speculative flags, which Part C forbids deriving from the current sample.

## D.4 What makes the revision cheap

- `resolve.py --audit` stays green, so revision breakage is detectable rather
  than discovered.
- **Fix the pinning convention in writing** before any re-pin: a method row
  carries deltas from what it inherits, never the full resolved set. Mixing the
  two produced 350 of 401 apparent inter-region disagreements.
- Stable `node_id`s, so re-extraction maps onto existing nodes.
- A `support` column that stays **empty** until step 2 delivers real counts —
  never backfilled from the `models[]` sample.
- Keep `pinning/*.REPORT.md`: the tensions, not the pins, are what found the
  defects that mattered.

---

## Open

- [ ] `algorithms[]` does not exist in the schema yet — it is part of **#94**
  (schema v5), with `runs[]`. The ontology can be designed before it lands.
- [ ] **Not loadable**: like domains and models, whatever is built will be node
  tables, not ontology dimensions, until converted.
- [ ] `adam`/`adamw`/`bert` in `libraries[]` and `pytorch` in `models[]` are
  extraction defects on the #94 list.
- [ ] **The widened scope costs #94 an invariant.** `execution_mode: inference`
  no longer implies an empty `algorithms[]` — it carries preprocessing and a
  decoder. The check becomes "no algorithm whose `role` is `parameter update
  rule`", which needs the role axis built and `runs[]` landed.
- [ ] **Where metrics sit is the one line the participant rule still needs.**
  Beam search is in because it *determines* the output; BLEU only *measures* it,
  and `ROUTING.tsv` currently calls a metric a misextraction. That holds only
  while metrics have no dimension of their own — worth revisiting with #93/#94,
  since "which metric was reported" is as much a review question as "which
  decoder".
- [ ] The `generic`/`quarantine` line has to be drawn again for this dimension.
  The widened scope invites unnamed procedure descriptions ("data augmentation",
  "fine-tuning"); the named-procedures-only rule is what keeps it bounded, and it
  needs the same `ROUTING.tsv` treatment models gave it.
- [ ] Whether **libraries** are a third participant in a run (`MODELS_BRIEF`
  Part C) — `DeepSpeed`/`FSDP` are configuration, but library-based inference of
  parallelism is too imprecise to replace an explicit field.
