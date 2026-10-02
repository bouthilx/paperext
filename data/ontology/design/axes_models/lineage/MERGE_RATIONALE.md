# Lineage axis — merge rationale

How `axes_models/lineage/nodes.tsv` was built from `models_tree/runA/` and
`models_tree/runB/` under the faceted design of `MODELS_AXES.md`. R1–R7 of
`MODELS_DERIVATION_BRIEF.md` §4 govern this axis and only this axis.

Three things live here, as the brief asks: **what was taken from which run and
why**, **every disagreement resolved with the losing reading recorded**, and
**every node dropped from either run with where its content went**.

---

## 0. Shape of the result

| | |
|---|---|
| nodes | 297 |
| roots (R6) | 17 |
| R4 grouping (`division`) nodes | 8 |
| nodes with more than one parent (R5) | 31 |
| leaves | 207 |
| maximum depth (shortest path to a root) | 4 |
| depth histogram | 0:17, 1:124, 2:118, 3:32, 4:6 |
| widest sibling sets | `Transformer` 35, `Convolutional network` 29, `BERT` 17, `ViT` 11 |

Run A had 284 nodes / 20 roots; run B had 246 / 17. The merged file is larger
than either because the deleted grouping levels **promote** their children
rather than removing them: deleting `Encoder-only Transformer` moves ten nodes
up to `Transformer`, deleting `Encoder-decoder convnet` moves `FCN` up to `CNN`,
and deleting `Embedding model` / `Factorization model` leaves all fourteen
disputed artifacts in place under three design families instead of one umbrella.
**Nothing in either run was deleted for being an axis value except the grouping
nodes themselves.**

## 1. The rule that decided every deletion

> Removing a grouping node **that was purely an axis value** is correct.
> Deleting a **named design family** because its defining property moved to an
> axis is wrong.

Applied uniformly, with the kept side made explicit so the rule is checkable:

| axis value removed as a node | the named design families it was hiding, all KEPT |
|---|---|
| topology = encoder–decoder + a reconstruction objective (`Autoencoder` root) | `Variational autoencoder` → β-VAE, CVAE, VQ-VAE → VQGAN; `MAE`; `VGAE` |
| adversarial training (`GAN` root, algorithm-side) | `DCGAN` → ProGAN → StyleGAN, BigGAN; `pix2pix` → CycleGAN; `SRGAN`; `VQGAN` |
| attributes = spiking (`Spiking neural network` root) | `Liquid state machine` |
| attributes = invertible | `Normalizing flow` and its coupling / autoregressive / continuous-time substructure, **kept** (§4.4) |
| attributes = euclidean-equivariance (`Equivariant graph network`) | `Group-equivariant CNN` → Steerable CNN; `SchNet`; `DimeNet`; `EGNN` |
| attributes = external-memory | `Neural Turing Machine` → DNC; `Memory network` |
| attributes = conditional-computation (`Mixture-of-experts network`) | `Mixtral`; `Switch Transformer` |
| attributes = bayesian-weights (`Bayesian neural network`) | `Gaussian process`; `PMF`; `Bayesian hierarchical model` |
| topology = bidirectional-encoder / causal-decoder / encoder–decoder | every Transformer family, now a direct child of `Transformer` |
| topology = ensemble (`Tree ensemble`) | `Bagged tree ensemble`, `Boosted tree ensemble` (kept: bagging-vs-boosting is a combination rule, not a topology value) |
| connectivity = factorized (`Embedding model`, `Factorization model`) | `Matrix factorization`, `Knowledge-graph embedding model`, `word2vec`, `Factorization machine` |
| connectivity = depthwise-separable | `MobileNet` → MobileNetV2, EfficientNet; `Xception`; `ShuffleNet`; `ConvNeXt` |
| connectivity = dilated-convolution | `WaveNet`; `TCN`; `DeepLab` |
| connectivity = spectral-graph-convolution (`Graph convolutional network`) | `ChebNet` → `GCN` → R-GCN |
| connectivity = set-aggregation + permutation-equivariance (`Permutation-invariant set network`) | `Deep Sets`; `PointNet` → PointNet++; `Set Transformer` |
| connectivity = state-space-recurrence (`Deep state-space model`) | `S4` → S5, H3 → Hyena, Mamba |
| topology = encoder–decoder + connectivity = convolution (`Encoder-decoder convnet`) | `FCN` → U-Net → (3D U-Net, nnU-Net, Attention U-Net, UNet++), SegNet |

## 2. The three real disagreements

### M-01 · `Embedding model` (A) vs `Factorization model` (B) — **both lose**

The owner's hint was right and the dispute does mostly dissolve. What the two
roots shared, and what each agent named as its own weakest set, is exactly *"the
learned object is a learned low-rank table"* — which is now
`connectivity=factorized` on the connectivity axis. Neither umbrella survives.

What survives are the design families, and on the substructure **run B wins
almost everywhere**, because run A's three division children (`Word embedding
model`, `Node embedding model`, `Knowledge graph embedding model`) divided by
*what discrete entity the table indexes*, which is the rejected level-1
characteristic "data structure consumed" applied one level down — run A says so
itself in its SELF_AUDIT §2.4.

All fourteen disputed nodes survive. Where each went:

| node | merged parent | rule |
|---|---|---|
| word2vec | **`Feedforward network (MLP)`** (new root for it) | R1 — Mikolov's own framing: the two architectures are the feedforward NNLM with the nonlinear hidden layer removed. Run B's B-12 named this reading and rejected it; the refactor removes its objection, because what word2vec shares with GloVe and TransE is now visible on the connectivity axis. |
| CBOW, Skip-gram | `word2vec` | R1/R3 — the two architectures named in the paper (run A) |
| fastText | `Skip-gram` | R1 — skip-gram extended with subword units (run B) |
| DeepWalk | `Skip-gram` | R1 (run B) — run A's `Node embedding model` grouping is deleted |
| node2vec | `DeepWalk` | R1 (run B) |
| GloVe | **`Matrix factorization` + `word2vec`** (R5 hybrid) | R1 — the paper's own words: it "combines … global matrix factorization and local context window methods" |
| NMF | `Matrix factorization` | both runs |
| PCA | `Matrix factorization` | run B — see L-03 for the rejected reading |
| CCA | **`Linear model`** | run A — two linear projections over two towers, not a factorization of one matrix |
| Factorization machine | `Matrix factorization` | R1 — Rendle defines FM against factorization models |
| DeepFM | `Factorization machine` + `MLP` | R5, both runs |
| TransE, DistMult, ComplEx, RotatE | **`Knowledge-graph embedding model`**, now a root | R6 |

`Knowledge-graph embedding model` is the one piece of the old umbrella that is
kept as a grouping node, promoted to a root. Its characteristic is a *scoring
design* ("a triple is scored by an algebraic form on three looked-up vectors"),
not a data structure — but it is the closest thing in this file to the rejected
characteristic, and it is flagged first in `SELF_AUDIT.md` §2.

**Rejected readings, recorded:** (a) keeping `Embedding model` with run A's
three-value division — rejected because the division is by data structure
consumed, and because its principle is now an axis value; (b) keeping
`Factorization model` as run B's root with six loose children — rejected for the
same reason, and because run B itself called the six children "a list" rather
than values of one variable.

### M-02 · Hopfield networks — probabilistic-graphical (A) vs energy-based (B)

**Run A wins.** `Energy-based network` is deleted as a root; `Hopfield network`
and `Boltzmann machine` sit under `Undirected graphical model`.

Three reasons, in order of weight:

1. **The backbone test disposes of run B's third child.** `Neural energy-based
   model` is "a deep network emitting a scalar, sampled by MCMC or Langevin
   dynamics" — a network left structurally unchanged with a different objective
   and a different sampling procedure. That is the brief's §2.1 definition of an
   algorithm, exactly as for diffusion and GFlowNets. Removing it leaves the
   root with two members that have a better home.
2. **Admitting it would re-import what the refactor removes.** `Autoencoder`
   goes because it names an objective; `GAN` goes because it names a training
   game. An `Energy-based network` root names an energy function plus a
   relaxation/sampling procedure — the same category of thing. Run A's own B05
   says it: "a root for it would be a fifth way of saying *has an energy
   function*."
3. **The undirected-GM edge is a genuine R1 edge, not a convenience.** Hopfield
   1982 is framed in Ising spin-glass terms, and an Ising model *is* an
   undirected graphical model; Hinton & Sejnowski define the Boltzmann machine
   by a Boltzmann distribution over configurations, i.e. a globally normalised
   potential model. Run B asserted the same Boltzmann–undirected-GM edge as a
   second parent, so the two runs only disagreed about which edge is primary.

**Rejected reading, recorded:** run B's `Energy-based network` root with
`Hopfield network`, `Boltzmann machine` and `Neural energy-based model` as
division children of "the form of the energy and the connectivity it is defined
over". Cost of being wrong: the ~5 corpus names containing "energy-based"
produce an algorithm mention plus a backbone instead of a lineage node, and
`Modern Hopfield network` loses the sibling that makes its attention
equivalence legible. Repair is mechanical: re-root two nodes.

### M-03 · `Slot attention` — root (A) vs under `Transformer` (B)

**Run A wins: it is a root.** Run B's own BOUNDARY_CASES calls this "the least
settled placement in the file" and its SELF_AUDIT ranks it 8th-worst, so the
losing run concedes the ground.

The deciding rule is **R2**, not R1: Locatello et al. define slot attention
against *dot-product attention* (citing Luong's recurrent attention), not
against the Transformer, and the mechanism they define is a **redefinition** of
it — the softmax is normalised over slots so that slots compete, and the update
is recurrent. R2 says two models that both use attention are unrelated unless
one was built from the other, and "built from attention" is a shared *primitive*,
which R2 names explicitly as never an edge. Run B's counter-argument — "the
defining mechanism is attention" — is precisely the primitive edge R2 forbids.

The refactor also removes the only *structural* argument run B had: under a
single tree, a root that fit none of the three Transformer stack divisions
looked like an orphan. Those divisions are now topology, so the question is
purely R1-vs-R2 and R2 answers it.

What changed from run A: it is no longer a **single-member** root. The corpus
carries `slot attention` (5 papers) plus SlotFormer, disentangled slot
attention, reusable slotwise mechanisms and DINOSAUR, so `SlotFormer` is added
as a child (R5 hybrid with `Transformer`), and the object-centric cluster has a
home with room in it.

**Rejected reading, recorded:** `Slot attention` as a descent child of
`Transformer`. Cost of being wrong: an object-centric cluster of ~8 names counts
as Transformer work at the depth-1 cut when it should count separately.

## 3. What was taken from which run

Neither run was a base that the other patched. The merge went family by family.

**Taken from run A:** the root set's shape and the contrast-is-not-descent
reading (A/B13) that produces it; `Coordinate MLP` as a family under the
feedforward root (the owner fixes this explicitly); `Rule-based model`,
`3D Gaussian splatting` and `Slot attention` as roots; the refusal of a
spectral/spatial division under GNN and of a 1-D/2-D/3-D division under CNN;
`Neural process`; `ChatGPT`/`Codex`/`Gemini` and the product-name-is-a-node
policy (A/B23); the `lda` / `dino` / `sam` / `complex` non-resolution policy;
ridge and lasso as *notes* on linear regression rather than nodes; `AdaBoost
ensemble`; `Extremely randomized trees` under `Random forest`; `EfficientNet`
under `MobileNet`; `Latent Dirichlet allocation` directly under
`Directed graphical model`; `S4` directly under `State-space model`.

**Taken from run B:** every R1 chain run A had flattened — `SqueezeNet`→AlexNet,
`U-Net`→FCN, `SegNet`→{FCN, VGG}, `R-CNN`→Fast→Faster→Mask, `OPT`/`GPT-NeoX`→
GPT-3, `Pythia`→GPT-NeoX, `ProGAN`→DCGAN, `CycleGAN`→pix2pix, `GCN`→ChebNet,
`DeepWalk`→Skip-gram, `node2vec`→DeepWalk, `ComplEx`→DistMult; `k-means` under
`Mixture model`; `Bayesian network` as a node; `Linear SVM`'s second parent;
`Seq2seq`'s two parents; `Reservoir network` and `Liquid state machine`;
`Recursive neural network`; `PINN`, `Hyena`, `WavLM`, `Longformer`,
`Switch Transformer`, `Neural SDE`, `DeepONet`, `ICA`, `PMF`,
`Tensor factorization`, `DALL-E`; the coupling / autoregressive /
continuous-time flow substructure.

**Taken from neither — coverage additions** (`model_names.tsv` consulted for
blind spots only, never for arbitration): `EEGNet` (3 papers), `ViLBERT` (3),
`UNet++`, `SlotFormer`. `EEGNet` and `ViLBERT` are attested families that both
runs missed; the other two were added to give a root and a wide family a second
child.

## 4. Every node dropped, and where its content went

### 4.1 Dropped from run A

| dropped | where its content went |
|---|---|
| `autoencoder` (root) | `topology=encoder-decoder` + the reconstruction objective → **algorithms** |
| `denoising_autoencoder` | algorithms (corruption is an objective); the model is the backbone |
| `sparse_autoencoder` | algorithms (a sparsity penalty is an objective) |
| `made` (MADE) | algorithms; `MAF` loses it as a second parent (M-04 below) |
| `gan` (root) | algorithms (adversarial training), per the owner |
| `conditional_gan` | deleted: conditioning is an input, not a lineage. pix2pix → U-Net, BigGAN → DCGAN, SRGAN → ResNet |
| `snn` (root) | `attributes=spiking` |
| `spiking_cnn` | `CNN` + `attributes=spiking` — an axis composition, not a named design |
| `embedding_model` (root) | `connectivity=factorized` (M-01) |
| `word_embedding`, `node_embedding` (divisions) | deleted: divided by data structure consumed. Members re-attached by R1 (M-01) |
| `kg_embedding` (division) | **promoted to a root** |
| `matrix_factorization` | **promoted to a root** |
| `encoder_only_` / `decoder_only_` / `encoder_decoder_transformer` | the **topology** axis, per the owner. The cut survives, on another axis |
| `cnn_encoder_decoder` | `topology=encoder-decoder`; `FCN` promoted to a direct CNN child |
| `tree_ensemble` | `topology=ensemble` + `connectivity=tree-traversal`; bagged/boosted attach to `Decision tree` (run B's shape) |
| `bayesian_nn` | `attributes=bayesian-weights`. Run A called this "the edge I would drop first" |
| `gflownet` (root) | **algorithms**, per the owner's disposition. The largest routing consequence in the corpus |
| `graph_autoencoder` | replaced by `VGAE`, the named design, under {`GNN`, `VAE`} |
| `one_class_svm` … | kept (all leaves kept) |

### 4.2 Dropped from run B

| dropped | where its content went |
|---|---|
| `energy_based_network` (root) | deleted (M-02). Hopfield + Boltzmann → `Undirected graphical model` |
| `neural_energy_based_model` | **algorithms** — the backbone test: an unchanged network, a new objective and a sampling procedure |
| `spiking_neural_network` (root) | `attributes=spiking` |
| `integrate_and_fire_network`, `conductance_based_network` | the **substrate** attribute's internal detail. A neuron model is not a design lineage; `Liquid state machine` is the one genuine spiking design and it survives under `Reservoir network` |
| `factorization_model` (root) | `connectivity=factorized` (M-01) |
| `word_embedding_model` (division) | deleted (M-01); run B declared it an R1 violation itself (B-12) |
| `autoencoder` (root), `denoising_`, `sparse_autoencoder` | as in §4.1 |
| `masked_autoencoder` | kept as `MAE`, re-parented to `ViT` alone — run A's own pre-committed repair |
| `generative_adversarial_network` (root) | algorithms |
| `plain_convolutional_network` | deleted: definable only by negating its siblings, so R4(3) fails. LeNet/AlexNet/VGG → `CNN` |
| `depthwise_separable_network` | `connectivity=depthwise-separable` |
| `dilated_convolutional_network` | `connectivity=dilated-convolution` |
| `fully_convolutional_encoder_decoder` | `topology=encoder-decoder`; `FCN` promoted |
| `graph_convolutional_network` | `connectivity=spectral-graph-convolution`; `ChebNet` promoted |
| `equivariant_graph_network` | `attributes=euclidean-equivariance` |
| `permutation_invariant_set_network` | `connectivity=set-aggregation` + `attributes=permutation-equivariance` |
| `mixture_of_experts_network` | `attributes=conditional-computation`. Run B called it "a placement of convenience" |
| `bayesian_neural_network` | `attributes=bayesian-weights` |
| `deep_state_space_model` | `connectivity=state-space-recurrence`; `S4` promoted (run A's shape) |
| `topic_model` | **R4 repair** — one child (`LDA`) means it is a rename of that child. LDA → `Directed graphical model` |
| `continuous_time_flow` | kept as `cnf`, relabelled `descent` rather than `division`, so its single child is not an R4 violation |
| `ridge_regression`, `lasso`, `elastic_net` | notes on `Linear regression`: the penalty is part of the fitting procedure, which is an algorithm (run A's reading) |
| `resnet_18`, `resnet_50` | R3 size variants, left to the second pass as both runs' stated policy; run B included them only as templates |
| `encoder_only_` / `decoder_only_` / `encoder_decoder_transformer` | the topology axis |
| `poisson_regression` | **kept**, moved under `Generalized linear model` so GLM has two children |

### 4.3 Two edges lost as collateral, recorded explicitly

- **M-04 · `MAF` loses its `MADE` parent.** MADE is "an autoencoder with masked
  connections"; with the autoencoder root gone, MADE's remaining content is a
  masking scheme (algorithm-side) over an MLP, so it is not a lineage node. MAF
  keeps only its `Autoregressive flow` parent, and the MADE derivation is in
  `notes`.
- **M-05 · `VQGAN` loses its `GAN` parent**, and `Liquid state machine` loses
  its `Spiking neural network` parent (it keeps `Reservoir network` and pins
  `attributes=spiking`). Both are simplifications, not losses.

### 4.4 `Normalizing flow`: judged under R6 and **kept**

The owner asked for a ruling rather than a default. Invertibility is now an
attribute, so the question is whether the flow *designs* form a lineage of their
own. They do: `NICE` founds the coupling-layer design, `RealNVP` is framed as
extending NICE, `Glow` as extending RealNVP, `MAF` and `IAF` as the
autoregressive counterpart, and `CNF` as the ODE limit (which is why it takes a
second parent from `Neural ODE`). `MODELS_AXES.md` itself speaks of "a
`Normalizing flow` family" and calls the coupling / autoregressive /
continuous-time split lineage substructure. Root kept; the split is built as run
B had it, with one repair (L-13).

## 5. Pinning policy

A node **inherits** its parents' pinned values and records only what it
**changes or adds**. Empty therefore means "same as parent", never "unknown".
Defaults declared on the attributes axis (point-estimate, rate-based,
no-symmetry, dense-computation, no-memory, deterministic-latent, non-invertible)
are never pinned — pinning a default everywhere would hide the real pins.

Three consequences worth stating:

- **`Transformer` pins no topology.** Topology is single-valued and varies
  across its children, so each child pins its own: BERT and ViT
  `bidirectional-encoder`, GPT and LLaMA `causal-decoder`, T5/BART/Whisper
  `encoder-decoder`, CLIP `multi-tower`. This is the owner's worked example and
  it is what replaces the deleted division level.
- **A multi-parent node pins the union it needs**, because inheritance from two
  parents is ambiguous. `Conformer` pins `self-attention|convolution` although
  each half is inherited from one parent; the redundancy is deliberate.
- **`VQ-VAE` pins `deterministic-latent`**, overriding the `stochastic-latent`
  it inherits from `VAE`: a codebook lookup is not a sampled Gaussian. This is
  the only place where a child *reverses* a parent's attribute, and it is the
  clearest evidence that the pin column carries information the tree does not.

## 6. Axis gaps found while pinning

Pinning 297 nodes is a stress test of the other three axes. Five nodes could not
be pinned on connectivity at all, and the gaps are real rather than clerical:

| node | gap |
|---|---|
| `Rule-based model`, `Rule set`, `Logic program` | no connectivity value for a symbolic rule set (`tree-traversal` fits only a decision list) |
| `Probabilistic graphical model` | no value for a factor graph over *variables*; `message passing` is about learned units wired by edges |
| `Recursive neural network` | no value for composition over a parse tree |
| `Neural operator` | no value for a learned kernel integral between function spaces (`FNO` is pinned `convolution`, which is approximate) |
| `3D Gaussian splatting` | no value — correctly, since it has no learned units wired to one another |

One attribute gap: **attention sparsity** (Longformer, BigBird, Performer) has
no attributes value, and both runs listed it as a cross-cutting property they
deliberately refused to make a node. It is now homeless on every axis.

These are reported, not patched: the three axes are owned elsewhere.
