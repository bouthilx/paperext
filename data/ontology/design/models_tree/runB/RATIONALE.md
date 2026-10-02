# Models hierarchy (run B) — rationale

Companion to `nodes.tsv`. Covers (1) the conventions, (2) the root set,
(3) the principle of division at every branch, (4) every phase-1 → phase-2
change with its reason, (5) the places where this derivation departs from the
letter of the brief, and (6) the boundary cases.

`DRAFT_PHASE1.md` is the corpus-free draft, frozen at 2026-10-02T11:16:21-04:00
before any data file was opened. `model_names.tsv` was read only afterwards and
only for the two permitted questions.

**Shape of the result**: 246 nodes, 17 roots, 63 division nodes, 166 descent
nodes, 30 multi-parent nodes, depth 0–5 (median designed depth 2).

---

## 1. Conventions

- **`depth`** is the shortest path to any root; roots are 0.
- **`relation`** is `root`, `division` (the node exists because a sibling set
  was divided by a stated principle — R4) or `descent` (the node exists because
  the field produced something that cannot be described without naming its
  parent — R1).
- **`characteristic`** is read as *the principle by which this node's children
  are divided*, stated once on the parent rather than repeated on each sibling.
  A node whose children are all `descent` carries `--`, because §5.1 of the
  brief requires a principle only "wherever a sibling set is produced by
  division rather than by descent".
- **Mixed sibling sets are legal.** `Convolutional network` has 7 division
  children sharing one principle, plus 11 nodes that arrive by descent or as a
  second parent (`DCGAN`, `ConvLSTM`, `wav2vec 2.0`, `Conformer`, `Graph
  convolutional network`, the detectors). Only the division subset must share a
  principle. This is the shape the brief's own Transformer sketch has.
- **No count columns**, per deliverable 2.

---

## 2. The root set

### 2.1 Why these are the roots

R6: a root is an architecture whose defining idea is not a modification of
another architecture **in this tree**. The 17 roots are, in file order:
`Linear model`, `Kernel machine`, `Decision tree`, `Probabilistic graphical
model`, `State-space model`, `Feedforward network`, `Convolutional network`,
`Recurrent network`, `Transformer`, `Graph neural network`, `Autoencoder`,
`Generative adversarial network`, `Energy-based network`, `Spiking neural
network`, `Normalizing flow`, `Factorization model`, `Neural operator`.

They are **historically contingent and do not partition any single
characteristic**, which R6 declares to be a property of a lineage backbone
rather than a defect. Concretely: `Transformer` and `Convolutional network` are
distinguished by a layer mechanism, `Autoencoder` and `GAN` by a composition of
two sub-networks, `Probabilistic graphical model` by a semantics, and `Neural
operator` by what the learned map is between. These are not values of one
variable, and no amount of rewriting makes them so without reintroducing one of
the three rejected characteristics.

### 2.2 Seventeen, against a smell test of 8–15

R6 says the bound is never a reason to merge a root one otherwise believes in.
Nothing was merged to reach the bound; here are the merges considered and
declined, so the judgement is reviewable:

| candidate merge | declined because |
|---|---|
| `Feedforward`, `Convolutional`, `Recurrent`, `Transformer`, `GNN`, `SNN` under one `Neural network` root | that is the generic the brief quarantines; it would put ~90% of the corpus in one level-1 bucket and answer none of the three questions the dimension exists for |
| `Feedforward network` under `Linear model` (via Perceptron) | B-01 |
| `State-space model` under `Probabilistic graphical model` | would place Mamba under PGM; instead HMM and the linear dynamical system take two parents (R5), which is what multi-parent is for |
| `Factorization model` under `Linear model` | a bilinear product of two learned tables is not a single inner product against the input; the root's positive test would stop working |
| `Autoencoder` and `GAN` under one "paired-network" root | the field names neither as a kind of the other, and no paper defines a GAN from an autoencoder; the shared property is a coincidence of shape (R2) |
| `Normalizing flow` under `Feedforward network` | invertibility-by-construction with a tractable Jacobian is the defining idea, not a constraint added to a dense stack |
| dropping `Spiking neural network` (zero corpus support) | PROCESS rule 1: the corpus bounds scope, it does not delete |

Two roots I expected to need and did **not** create: `Rule-based model`
(decision lists, ILP, association rules) — `Decision tree` covers the cases I
could name, and the corpus holds only two neuro-symbolic singletons; and
`Classical time-series model` (ARIMA and relatives) — no corpus support at all,
and the latent-state cases are already covered by `State-space model`.

---

## 3. The principle of division at every branch

Every sibling set below was produced by division and therefore states one
principle. Sets not listed here are produced by descent and are exempt.

- **Linear model** — the link function relating the linear predictor to the response
- **Linear regression** — the penalty imposed on the coefficients
- **Kernel machine** — the criterion under which the coefficients of the kernel expansion are fit
- **Support vector machine** — the loss the margin criterion is instantiated with
- **Decision tree** — how the member trees combine into one prediction
- **Probabilistic graphical model** — the orientation of the factorization the graph encodes
- **Directed graphical model** — the shape of the latent structure the factorization encodes
- **Undirected graphical model** — whether the factorization is joint over all variables or conditional on an observed input
- **State-space model** — the form of the latent state and of its transition
- **Feedforward network** — the input domain the fully-connected stack is specialized to, and the invariance it is given
- **Convolutional network** — the connectivity pattern by which convolutional layers are composed into a stack
- **Recurrent network** — the form of the recurrent state update
- **Transformer** — which block types the model stacks, and how attention is masked across them
- **Graph neural network** — how a node's neighbourhood is aggregated into its update
- **Autoencoder** — the constraint imposed on the latent code
- **Energy-based network** — the form of the energy and the connectivity it is defined over
- **Spiking neural network** — the neuron model
- **Normalizing flow** — the form of the invertible transformation
- **Factorization model** — what the latent factors reconstruct
- **Neural operator** — the form of the integral kernel the operator layer parameterizes

Three checks applied to each (PROCESS rules 2, 3, 6):

1. **Does the child set refine the parent's characteristic, or import another
   aspect's?** The one that nearly failed is `Transformer`: the obvious child
   sets "efficient vs dense attention" and "dense vs mixture-of-experts" both
   import a cost aspect into a set divided by block structure. Both were
   rejected and the artifacts placed by descent instead (B-18).
2. **Does any sibling exist only because it was large in this corpus?** No
   sibling set was created after phase 2, with the single exception of the
   `Neural operator` root, whose *existence* the corpus revealed and whose
   *structure* came from field knowledge. Nothing was split because it was big
   and nothing merged because it was small.
3. **Is any node a residual?** There is no `Other`, no `Misc` and no `Classic`
   node anywhere — the three defects B.5 records for v0's root set.

---

## 4. Phase 1 → phase 2: every change and its reason

Phase 2 consulted `model_names.tsv` for exactly two questions. Volume was used
only to decide which names to look at.

### 4.1 Blind spots added (the corpus named a family the draft had no home for)

| # | added | reason |
|---|---|---|
| A1 | **`Neural operator`** root + `Fourier neural operator` + `DeepONet` | `fourier neural operator (fno)` and relatives are in the corpus and the draft had no node that could hold them. The only root added after the draft. Placement decided on field knowledge; the corpus only revealed the gap. |
| A2 | `wav2vec 2.0` + `HuBERT` + `WavLM` | a whole self-supervised speech family (wav2vec 2.0, HuBERT, WavLM, DistilHuBERT, XLSR) with no drafted home. R5 composite: CNN feature encoder + Transformer context network. |
| A3 | `ESM` | protein language models (`esm-2`, `esm-1b`) with no drafted home. |
| A4 | `AlphaFold` | present and structurally distinctive; attached to the attention lineage only. |
| A5 | `Hyena` | present (`hyena`, `hyenadna`) and in the S4 line, which the draft had. |
| A6 | `Recurrent state-space model` | `recurrent state space model (rssm)` is in the corpus; it is the Dreamer/PlaNet world model and sits across the SSM and recurrent roots (R5). |
| A7 | `Physics-informed neural network` | present; it is a coordinate MLP, so the drafted `Implicit neural representation` node was the right parent — the draft simply had not named it. |
| A8 | `Bayesian neural network` | present and frequent enough to need a home; R5 across feedforward and directed-graphical lineages. |
| A9 | `Mixture-of-experts network` | `mixture of experts (moe)` is named as a model in its own right, separately from Switch/Mixtral. |
| A10 | `Bayesian hierarchical model` | a named statistical family in the corpus. |
| A11 | `DETR`, `Segment Anything (SAM)` | detection and segmentation transformers, both present and both family-forming. |
| A12 | `Stable Diffusion`, `DALL-E` | the named diffusion *releases*, admitted as R5 composites while `diffusion model` itself stays algorithm-side (B-14). |
| A13 | `Set Transformer` | present; completes the permutation-invariant set family across two lineages. |
| A14 | `Time-delay neural network` | `ecapa-tdnn` and `tdnn` are present; TDNN is the original weight-shared temporal network. |
| A15 | `Neural SDE` | `neural sde` / `nsde` present; a direct descent child of the drafted `Neural ODE`. |
| A16 | `Independent component analysis`, `Canonical correlation analysis` | both present as model names; both are latent-factor models the draft had not enumerated. |
| A17 | `Slot attention` | present (`slot attention`, `slotformer`); placement is the least settled in the file (B-19). |

**Two additions are draft defects, not corpus findings, and are labelled as
such in `nodes.tsv`:** `Conformer` and `CLIP` both appear in the brief's own
worked table (§4.7) as the canonical R5 hybrid and R5 composite, and phase 1
omitted both. The corpus is where I noticed, but the brief is where they were
already specified. `BLIP` and `LLaVA` were added alongside CLIP as further
composites.

### 4.2 Drafted nodes flagged as speculative (corpus support absent or thin)

None were deleted — PROCESS rule 1: "a category with no corpus support is
*possibly speculative — justify or keep*". Each is marked in `nodes.tsv`:

| node(s) | corpus support | kept because |
|---|---|---|
| `Spiking neural network` root, `Integrate-and-fire`, `Conductance-based` | **none** | a real founding idea with its own community and hardware; absence in a one-year single-institute snapshot is not evidence of absence in the field |
| `Reservoir network`, `Echo state network`, `Liquid state machine` | none | same |
| `Capsule network` | none | same |
| `Word embedding model` subtree (word2vec, GloVe, fastText, DeepWalk, node2vec) | **none** | the most surprising finding of phase 2; a 2024 corpus has moved past standalone word embeddings. Kept, and flagged — this subtree is the most likely to be dead weight |
| `Restricted Boltzmann machine`, `Deep belief network` | none (`boltzmann machine` and `hopfield networks` do appear) | historically load-bearing and still named in surveys |
| `Extremely randomized trees`, `Isolation forest`, `CatBoost` | none | the siblings around them are well supported |
| `Poisson regression`, `Generalized additive model` | none | they are the other link functions; removing them would leave the division principle stating a distinction with two values |
| `Depthwise-separable network` subtree (MobileNet, EfficientNet, ShuffleNet, Xception) | **thin** — VGG, DenseNet and SqueezeNet appear, these do not | efficiency-oriented backbones are standard vocabulary; thin here, not absent |
| `SIREN`, `DeepSDF` | none (`nerf` appears once) | they are the other two canonical implicit representations |
| `Mamba` | none (this corpus predates it) | a certainty for the next corpus |
| `Tensor factorization` children | indirect (`hitf`, `chitf`) | supported in substance if not in name |

### 4.3 What the corpus made me want to restructure, and I did not

Recorded as findings, per the instruction that this is a signal to write down
rather than to act on:

1. **GFlowNets are ~33 names in this corpus** and the rules send all of them to
   the algorithms hierarchy (B-24). This is the single highest-impact
   consequence of the brief's diffusion fixed point, and I did not carve out an
   exception for it.
2. **`diffusion` is ~37 names** and most of them follow `gflownet` out of this
   tree, leaving a U-Net or a DiT behind (B-14).
3. **Equivariance is cross-cutting**: the corpus has equivariant GNNs,
   equivariant Transformers, equivariant MLPs and equivariant mesh networks.
   The tree keeps `Equivariant graph network` under GNN (where the field names a
   family) and records the rest as a property. A principled alternative — an
   `equivariant` attribute on the run or the mention — is for the owner.
4. **The BERT family is wide along several aspects at once** (~30 names:
   domain-adapted, compressed, multilingual, objective-modified), while the
   **LLaMA family is wide along one** (~26 names, nearly all R3 size and chat
   variants). That asymmetry is exactly the R7 distinction: LLaMA needs no
   grouping level, BERT does. Flagged, not built — see `SELF_AUDIT.md`.
5. **Half the top-50 names are algorithms** (PPO, SAC, DQN, Rainbow, MuZero,
   IMPALA, TD3, CQL, SimCLR, BYOL, VICReg, Barlow Twins, DINO, FedAvg, LoRA).
   This confirms the brief's type-confusion diagnosis and is the algorithms
   derivation's input, not a defect in this one.

---

## 5. Declared departures from the letter of the brief

1. **17 roots against a stated expectation of 8–15** (§2.2 above).
2. **`SPELLINGS.tsv` case values.** The deliverable spec lists
   `orthographic | acronym | size`, but R3's three cases are orthographic,
   acronym/long-form and **pluralisation**, and R3 also rules that size variants
   are *nodes*, so `size` cannot be a spelling case. This file uses
   `orthographic | acronym | plural`, plus one declared fourth value `synonym`
   (B-26). The spec and R3 disagree and the spec appears to carry a typo.
3. **ViT is one level deeper than the brief's worked table draws it** (B-09).
4. **Seven nodes are at depth 4–5**, above the "roughly 3 to 4" guidance. All
   seven are pure R1 descent chains, not extra designed levels:
   `gpt3 → gpt_neox → pythia`, `gpt3 → opt`, `roberta → {xlm_roberta,
   longformer}`, `faster_r_cnn → mask_r_cnn`, `deepwalk → node2vec`. Cutting
   them would mean asserting a lineage I believe to be false.
5. **Size-variant nodes are seeded, not enumerated.** Only `ResNet-18` and
   `ResNet-50` exist, as templates; the rest are descent attachments R7 permits
   the second pass to make. Enumerating them in a design pass would be guessing
   at the corpus.

---

## 6. Boundary cases

26 rows in `BOUNDARY_CASES.tsv`, each with the reading chosen, the reading
rejected, the rule in tension and the impact if the choice is wrong. The three
with the largest consequences:

- **B-24 GFlowNet** — algorithm-side by parity with diffusion. ~33 corpus names.
- **B-11 GAN** — admitted as a model (the paired-network shape), against the
  reading that would make it an algorithm like diffusion.
- **B-13 `large language model`** — quarantined as a scale-and-use generic.

The rest cover MLP/Perceptron (B-01), Gaussian processes (B-03), RNN-as-SSM
(B-05), backbone-parametric detectors (B-06), seq2seq (B-08), masked
autoencoders (B-10), word2vec (B-12), proprietary releases (B-16), the
ambiguous strings `lda` and `sam` (B-17, B-22), mixture of experts (B-18), slot
attention (B-19), the Transformer's own ancestry (B-20), LLM generations
(B-21), the plural `transformers` (B-23), application-named classes (B-25) and
synonyms at grouping nodes (B-26).
