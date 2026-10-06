# Algorithms dimension — design brief

Written 2026-10-06, after the models dimension was built. Companion to
`MODELS_BRIEF.md` (the entity model), `MODELS_AXES.md` (what models became),
`MODELS_DERIVATION_BRIEF.md` (the method and R1–R7) and `PROCESS.md` (how the
domains design was run).

Issue **#96**. Siblings: **#95** models · **#91** domains · **#93** datasets ·
**#94** extraction (runs, schema v5).

**Read this file first when resuming.** It is the handover.

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

**A run's participants are constrained by `execution_mode`**: an `inference` run
has a model and **no parameter-updating algorithm** — though it may still carry
the preprocessing the model requires; `train` and `finetune` runs have both. The
invariant is checkable *because* the `role` axis (B.2) names which slot an
algorithm fills. Before the scope widened it was checkable by entity type alone.

## A.3 Settled, inherited from the models work — do not re-litigate

- **Admission rule.** A term is a **model** only if it names a *separable learned
  object* — parameters describable and runnable independently of the procedure
  that produced them. Otherwise it is an **algorithm**, and a run may carry an
  algorithm with **no model**.
- **`algorithms[]` holds the *learning procedure*, not only the learning.**
  *Widened by the owner, 2026-10-06*, replacing "strictly learning algorithms":
  data preprocessing, experience generation, configuration search and
  post-training compression are all in, because each is part of producing the
  learned object. The boundary is the **artifact test** — *a procedure is an
  algorithm if running it changes or determines the learned object.* Out:
  procedures that only consume a finished model without changing it — beam
  search, nucleus sampling, test-time retrieval, channel decoding. Bounded the
  way models bounded itself: **named procedures only** (`CutMix`, never "we
  normalised the images").
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

## A.4 MCTS, the declared boundary case

Training-time target generation is a learning algorithm; test-time planning is
not. MuZero, DreamerV2, PlaNet and QMIX were all ruled algorithm-side although
each specifies networks — a reviewer wanting "proportion of papers using
Dreamer" countable in the **models** dimension will disagree, and that is on
record.

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

> **Two algorithms that run together in a single training run cannot be
> siblings.** Siblings are alternatives for the same slot.

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
| **lineage** | descent — `REINFORCE → A2C → PPO`; `DQN → Rainbow → {C51, QR-DQN, IQN}`; `SGD → clipped-SGD → clipped-SSTM`. The aggregation surface. | parent set |
| **signal** | where the training target comes from: label, reward, reconstruction, agreement, score/denoising, likelihood, equilibrium, causal contrast | many, unions |
| **role** | which slot of the procedure it fills: data preparation · experience generation · objective/estimator · parameter update rule · parameter subset · coordination · configuration search · compression | many, unions |
| **attributes** | on/off-policy · model-based/free · value/policy · online/offline · centralised/decentralised · federated | per-family, as in models |

Four axes again — flagged rather than hidden. But only **lineage** is ported, for
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
2. **Scope is the learning procedure, not learning per se** — the revised A.3
   bullet and its artifact test. This admits `t-sne`/`phate` (running them
   produces the embedding) and `k-nearest neighbors` (nonparametric: an algorithm
   with no model, a legal state). It leaves `orbgrand` as the one likely
   exclusion — GRAND is channel decoding and changes no learned object.
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

- **`data/ontology/design/axes_models/ROUTING.tsv`** — the **114 `algorithm`
  rows are this dimension's vocabulary**, already identified, sized and
  justified. This derivation does **not** start from a blank corpus scan.
  It also carries 13 `unsure` rows, deliberately unresolved.
- **The corpus is in a different checkout**:
  `/home/bouthilx/projects/paperext-llm-backend/data/mdl/queries/openai/legacy-2024/`
  (2110 files) + `vertexai/` (102) = **1999 distinct papers**. This working copy
  holds only 102 extractions, so nothing here can be recomputed from it.
- `model_names.tsv` — 2483 names / 3549 mentions, with the header flagging that
  the corpus predates the model/algorithm split.

## Open

- [ ] `algorithms[]` does not exist in the schema yet — it is part of **#94**
  (schema v5), with `runs[]`. The ontology can be designed before it lands.
- [ ] **Not loadable**: like domains and models, whatever is built will be node
  tables, not ontology dimensions, until converted.
- [ ] `adam`/`adamw`/`bert` in `libraries[]` and `pytorch` in `models[]` are
  extraction defects on the #94 list.
- [ ] **The widened scope costs #94 an invariant.** `execution_mode: inference`
  no longer implies an empty `algorithms[]`, since preprocessing may be named.
  The check becomes "no algorithm whose `role` is `parameter update rule`" —
  which only works once the role axis exists and `runs[]` lands.
- [ ] The `generic`/`quarantine` line has to be drawn again for this dimension.
  The widened scope invites unnamed procedure descriptions ("data augmentation",
  "fine-tuning"); the named-procedures-only rule is what keeps it bounded, and it
  needs the same `ROUTING.tsv` treatment models gave it.
- [ ] Whether **libraries** are a third participant in a run (`MODELS_BRIEF`
  Part C) — `DeepSpeed`/`FSDP` are configuration, but library-based inference of
  parallelism is too imprecise to replace an explicit field.
