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
has a model and **no algorithm**; `train` and `finetune` runs have both. Since
`algorithms[]` holds *learning* algorithms only, this is a checkable invariant.

## A.3 Settled, inherited from the models work — do not re-litigate

- **Admission rule.** A term is a **model** only if it names a *separable learned
  object* — parameters describable and runnable independently of the procedure
  that produced them. Otherwise it is an **algorithm**, and a run may carry an
  algorithm with **no model**.
- **`algorithms[]` is strictly *learning* algorithms.** Inference-time
  procedures — beam search, sampling schedules, test-time planning — are out.
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

## B.2 What has to be decided

- **Is it faceted, and on which axes?** Or is the backbone a single
  characteristic — and if so, which?
- **How RL fits.** 112 of v0's `algorithms` nodes were RL. The routed set is RL-
  and SSL-heavy: ~13 RL update rules, 5 SSL objectives, 6 optimizers/distributed
  methods, 4 domain-adaptation methods.
- **Whether optimizers are a separate kind.** `adam`/`adamw` were extracted into
  `libraries[]` — a #94 defect, but it hints the field treats them as tooling.
- **What an "algorithm" is at the right grain**: is `PPO` a sibling of `Adam`?
  They are both procedures that change parameters, and nothing else about them is
  alike.

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
- [ ] Whether **libraries** are a third participant in a run (`MODELS_BRIEF`
  Part C) — `DeepSpeed`/`FSDP` are configuration, but library-based inference of
  parallelism is too imprecise to replace an explicit field.
