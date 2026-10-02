2026-10-02T11:16:21-04:00

# Models hierarchy — phase 1 draft (corpus-free)

**Protocol statement.** Everything below was derived before any data file was
opened. At the time of writing this file I had read exactly three files:
`MODELS_DERIVATION_BRIEF.md`, `MODELS_BRIEF.md`, `PROCESS.md`. I had not opened
`model_names.tsv`, `data/ontology/models/` (any version),
`data/ontology/design/axes/`, `run1`–`run3`, `models_tree/runA/`, any
`proposed_categories.csv` or `categorized_models.json`, or the datasets/domains
ontologies. The structure comes from my own knowledge of the ML literature,
with ACM CCS `Computing methodologies`, arXiv categories (cs.LG/cs.CV/cs.CL/
cs.NE/stat.ML) and Papers With Code used only as a breadth checklist against
which to ask "what founding architecture have I forgotten" — never as a referee.

The file is frozen at the timestamp above. Phase 2 may only (a) add blind
spots and (b) flag drafted nodes as speculative; every such change is recorded
in `RATIONALE.md`, and this file is not edited afterwards.

---

## 0. Conventions used throughout

- **Depth.** A root has `depth = 0`. Depth is the length of the *shortest* path
  from any root (R5 multi-parent nodes therefore take the smaller value).
- **`relation`.** `division` = the node exists because its parent's sibling set
  was divided by a stated principle (R4). `descent` = the node exists because
  the field produced an artifact or family that cannot be described without
  naming its parent (R1). A root has `relation = root`.
- **`characteristic`.** Read as *the single principle by which this node's
  children are divided*. It is stated once, on the parent, rather than repeated
  on each sibling. Nodes whose children are all `descent` carry `—`: per
  `MODELS_DERIVATION_BRIEF` §5.1 a principle of division is required only
  "wherever a sibling set is produced by division rather than by descent".
- **Mixed sibling sets are legal and expected.** A family node may have
  `division` children (field-named groupings) and `descent` children (artifacts)
  side by side; only the `division` subset must share one principle. This is the
  shape the brief's own Transformer sketch has.
- **Artifact nodes.** Per decisions 2 and 10 of `MODELS_BRIEF`, separately named
  releases are nodes. This draft creates artifact nodes only where the artifact
  is itself a *family* (it will have children) or where it is needed to make a
  lineage chain legible. Pure leaves are deliberately left for the second pass,
  which R7 permits to attach under descent. Size variants (`resnet-50`,
  `llama2-7b`) are therefore **not** enumerated here: they are nodes, but they
  are descent attachments the second pass is allowed — and required — to make.

---

## 1. The root set, and why these are the roots

R6: a root is an architecture whose defining idea is not a modification of
another architecture **in this tree**. Sixteen roots:

| # | root | the founding idea |
|---|---|---|
| 1 | Linear model | a learned weight vector applied to features through a link |
| 2 | Kernel machine | a prediction expanded over kernel evaluations against retained data |
| 3 | Decision tree | a learned partition of the input space by recursive axis tests |
| 4 | Probabilistic graphical model | a joint distribution factorized according to a graph |
| 5 | State-space model | a latent state carried through time by a learned transition |
| 6 | Feedforward network (MLP) | a stack of affine maps separated by pointwise nonlinearities |
| 7 | Convolutional network | weight-shared local receptive fields over a regular grid |
| 8 | Recurrent network | a hidden state fed back into the same parameters each step |
| 9 | Transformer | a stack of self-attention blocks over a set of positions |
| 10 | Graph neural network | message passing over the edges of an arbitrary graph |
| 11 | Autoencoder | an encoder and a decoder joined by a constrained code |
| 12 | Generative adversarial network | a generator and a discriminator as one paired object |
| 13 | Energy-based network | a learned scalar energy over units, with no feedforward direction |
| 14 | Spiking neural network | units communicating by discrete events in continuous time |
| 15 | Normalizing flow | an invertible map with a tractable Jacobian |
| 16 | Factorization model | a table of latent vectors whose products reconstruct a relation |

**Sixteen is one over the brief's 8–15 smell test.** R6 says the bound is never
a reason to merge a root I believe in, so nothing was merged to reach it. The
closest merge candidates, and why they were not merged, are in `RATIONALE.md`
§2.2. The roots are **historically contingent and do not partition a single
characteristic** — that is a declared property of a lineage backbone (R6), not
a defect. Three of them (6, 7, 8) would collapse into one if "neural network"
were admitted as a node; §4 explains why it is not.

**Why the roots are not deeper-rooted.** Three tempting super-roots were
considered and rejected:

- *`Neural network` over roots 6–14.* It is the generic the brief quarantines
  (§4.7), it divides nothing, and a level-1 cut that puts 90% of a modern ML
  corpus in one bucket answers none of the three questions in §1 of the brief.
- *`Linear model` over `Feedforward network`*, via Perceptron → MLP. The name
  carries the lineage, but the perceptron's defining content is a **learning
  rule**, which the admission rule sends to the algorithms hierarchy; the
  surviving model is a linear classifier. Boundary case B-01.
- *`Probabilistic graphical model` over `State-space model`.* Rejected because
  it would place Mamba under PGM. Instead HMM and the linear dynamical system
  carry **two parents** (R5), which is exactly what multi-parent is for.

---

## 2. Roots 1–5: the non-neural lineages

### 1. Linear model  *(depth 0)*
- **positive test**: the prediction is a function of a single inner product
  between learned weights and the input features.
- **negative test**: any learned nonlinearity between input and the weights.
- **characteristic for children**: *the link function relating the linear
  predictor to the response.*
- children (division): `Linear regression` (identity), `Logistic regression`
  (logit), `Poisson regression` (log), `Perceptron` (step).
  - `Linear regression`'s own children divide by *the penalty imposed on the
    coefficients*: `Ridge`, `Lasso`, `Elastic net`.
- children (descent): `Generalized additive model` — "a GLM with each linear
  term replaced by a smooth function"; `Linear discriminant analysis` (B-02).

### 2. Kernel machine  *(depth 0)*
- **positive test**: prediction is a weighted sum of kernel evaluations between
  the query and retained training points.
- **negative test**: a fixed-dimensional parameter vector that makes the
  training set discardable (that is a linear model).
- **characteristic for children**: *the criterion under which the coefficients
  of the kernel expansion are fit.*
- children (division): `Support vector machine` (max margin), `Gaussian
  process` (Bayesian posterior over functions, B-03), `Kernel ridge regression`
  (penalized least squares).
  - SVM's children divide by *the loss the margin criterion is instantiated
    with*: `Support vector regression` (epsilon-insensitive), `One-class SVM`
    (origin-separating). `Linear SVM` takes a second parent, `Linear model`
    (R5, degenerate kernel).

### 3. Decision tree  *(depth 0)*
- **positive test**: prediction is read off a traversal of learned axis-aligned
  (or oblique) tests.
- **negative test**: no partition — a global parametric function.
- **characteristic for children**: *how member trees combine into one
  prediction.* The single tree is the root itself; the children are the two
  combination forms the field names.
- children (division): `Bagged tree ensemble` (independent trees, averaged or
  voted) → `Random forest`, `Extremely randomized trees`, `Isolation forest`;
  `Boosted tree ensemble` (stagewise additive sum) → `Gradient boosting
  machine` → `XGBoost`, `LightGBM`, `CatBoost`.
- *Algorithm side, for the record*: bagging, random subspace, AdaBoost and the
  boosting procedure are algorithms; only the resulting ensemble is here.

### 4. Probabilistic graphical model  *(depth 0)*
- **positive test**: the parameters are the factors of a joint distribution and
  the graph states which variables each factor couples.
- **negative test**: a feedforward map from input to output with no joint
  distribution defined over the variables.
- **characteristic for children**: *the orientation of the factorization the
  graph encodes.*
- children (division):
  - `Directed graphical model` — children divide by *the shape of the latent
    structure*: `Mixture model` (one discrete latent per observation) →
    `Gaussian mixture model`, `k-means` (B-04); `Topic model` (mixed membership)
    → `Latent Dirichlet allocation`; `Bayesian network` (general DAG).
  - `Undirected graphical model` → `Markov random field`, `Conditional random
    field`. `Boltzmann machine` reaches this node by a second parent (R5).

### 5. State-space model  *(depth 0)*
- **positive test**: a latent state is carried across steps by a learned
  transition and read out by a learned emission.
- **negative test**: the whole history is attended to or convolved directly
  with no carried state.
- **characteristic for children**: *the form of the latent state and of its
  transition.*
- children (division): `Hidden Markov model` (discrete state; second parent
  `Directed graphical model`), `Linear dynamical system / Kalman filter`
  (continuous linear-Gaussian; second parent `Directed graphical model`),
  `Deep state-space model` (learned structured linear transition, stacked) →
  `S4` → `Mamba`.
- **Note on recurrent networks.** An RNN is a nonlinear deterministic
  state-space model, and S4/Mamba are routinely *described* as linear RNNs.
  Neither relation is R1 — Elman does not define his network from state-space
  theory, and Gu defines S4 from the continuous-time SSM, not from the RNN
  literature. Under R2 this stays an influence, not an edge. Boundary case B-05.

---

## 3. Roots 6–16: the neural and latent-factor lineages

### 6. Feedforward network (multilayer perceptron)  *(depth 0)*
- **positive test**: every unit is connected to every unit of the previous
  layer, with no weight sharing, no recurrence and no graph structure.
- **negative test**: any structural constraint on the connectivity — that
  constraint names a different root.
- **characteristic for children**: *the input domain the fully-connected stack
  is specialized to, and the invariance it is given.*
- children (division): `Implicit neural representation` (the input is a
  coordinate; the weights *are* the signal) → `NeRF`, `SIREN`, `DeepSDF`;
  `Permutation-invariant set network` (the input is a set; the output is
  invariant to its order) → `Deep Sets`, `PointNet`.
- children (descent): `Radial basis function network`; `MLP-Mixer` (second
  parent `Vision Transformer` — it is ViT with the attention block replaced by
  token-mixing MLPs, R5 hybrid).
- *Low-confidence sibling set* (see `SELF_AUDIT.md`): the two division children
  are the only two the field names, and the principle was written after the
  children rather than before.

### 7. Convolutional network  *(depth 0)*
- **positive test**: the same learned kernel is applied at every position of a
  regular grid.
- **negative test**: position-specific weights, or an irregular neighbourhood
  (that is a graph network).
- **characteristic for children**: *the connectivity pattern by which
  convolutional layers are composed into a stack.* Every child below is a
  pattern the field has named; none is an efficiency class or an application.
- children (division):
  - `Plain convolutional network` (a linear stack) → `LeNet`, `AlexNet` →
    `SqueezeNet`, `VGG`
  - `Residual network (ResNet)` (identity shortcuts) → `ResNeXt`, `Wide
    ResNet`, `SE-ResNet`, `Neural ODE` (continuous-depth limit of a residual
    network)
  - `DenseNet (densely connected network)` (every layer reads all earlier ones)
  - `Inception network` (parallel multi-scale branches) → `Inception-v3`,
    `Xception` (second parent `Depthwise-separable network`)
  - `Depthwise-separable network` (channel and spatial mixing factorized) →
    `MobileNet` → `MobileNetV2`; `EfficientNet`; `ShuffleNet`
  - `Fully convolutional encoder–decoder` (contracting then expanding path) →
    `FCN` → `U-Net`; `SegNet`
  - `Dilated convolutional network` (receptive field grown by dilation rather
    than depth or pooling) → `WaveNet`, `Temporal convolutional network`,
    `DeepLab`
- children (descent): `Capsule network`; the detector lineage `R-CNN` →
  `Fast R-CNN` → `Faster R-CNN` → `Mask R-CNN`; `YOLO`; `SSD`; `RetinaNet`.
  Detectors are backbone-parametric — see B-06.
- **Deliberately absent**: no `3D CNN` node. Input dimensionality is the data
  structure consumed, which is a rejected dividing characteristic. `C3D` and
  `I3D` are descent artifacts here, not a class.

### 8. Recurrent network  *(depth 0)*
- **positive test**: the same parameters are applied at each step to a hidden
  state fed back from the previous step.
- **negative test**: a fixed-length context processed in one shot.
- **characteristic for children**: *the form of the recurrent state update.*
- children (division): `Elman RNN` (ungated tanh update), `LSTM` (gated cell
  state), `GRU` (gated, no separate cell state — B-07), `Reservoir network`
  (fixed random recurrence, learned readout) → `Echo state network`, `Liquid
  state machine` (second parent `Spiking neural network`), `Recursive neural
  network` (the update follows a tree, not a sequence).
- children of `LSTM` (descent): `BiLSTM`, `ConvLSTM` (second parent
  `Convolutional network`), `Tree-LSTM`, `Sequence-to-sequence (RNN
  encoder–decoder)` → `Attentional encoder–decoder`.
  - Seq2seq is a **composite** (two recurrent networks) and is placed by
    composition, not by division; Sutskever's is two LSTMs and Cho's two GRUs,
    so it takes both cells as parents. B-08.

### 9. Transformer  *(depth 0)*
- **positive test**: representations are updated by attention over a set of
  positions, with no recurrence and no fixed local window.
- **negative test**: attention bolted onto a recurrent or convolutional stack
  that still carries the computation (that is `Attentional encoder–decoder`).
- **characteristic for children**: *which block types the model stacks, and how
  attention is masked across them.*
- children (division):
  - `Encoder-only Transformer` (bidirectional attention, no causal mask)
    - `BERT` → `RoBERTa` → `XLM-R`, `Longformer`; `ALBERT`; `DistilBERT`;
      `ELECTRA`; `DeBERTa`. **Flagged for a deeper design pass** (R7, §8).
    - `Vision Transformer (ViT)` → `DeiT`, `Swin Transformer`, `BEiT`.
      **Flagged for a deeper design pass.** (B-09 on its depth.)
  - `Decoder-only Transformer` (causal mask)
    - `GPT` → `GPT-2` → `BLOOM`; `GPT-3` → `OPT`, `GPT-NeoX` → `Pythia`;
      `GPT-4`
    - `LLaMA` → `LLaMA 2`, `LLaMA 3`, `Vicuna`, `Alpaca`
    - `Mistral` → `Mixtral`; `PaLM`; `Gemma`; `Falcon`; `Qwen`; `Phi`
    - `Transformer-XL` (segment recurrence) → `XLNet`
    - `Decision Transformer`
  - `Encoder–decoder Transformer` (encoder plus cross-attending decoder) —
    Vaswani's own base/big models live here
    - `T5` → `mT5`, `FLAN-T5`, `Switch Transformer`; `BART` → `mBART`;
      `Whisper`
- children (descent): `Perceiver` (cross-attention into a latent array).
- **Deliberately absent**: no `Efficient Transformer` node and no
  `Mixture-of-experts` node. Sub-quadratic attention and sparse routing are
  **cross-cutting properties** a model has in addition to its lineage, not a
  place in it; Longformer attaches under RoBERTa, Switch under T5, Mixtral under
  Mistral. Recorded as a property candidate in `SELF_AUDIT.md`.
- **Deliberately absent**: no `Large language model` node. See §4.

### 10. Graph neural network  *(depth 0)*
- **positive test**: a node's representation is updated from messages along the
  edges of an arbitrary, instance-specific graph.
- **negative test**: a fixed regular neighbourhood (convolution) or a fully
  connected set (transformer).
- **characteristic for children**: *how a node's neighbourhood is aggregated
  into its update.*
- children (division): `Graph convolutional network` (degree-normalized mean;
  second parent `Convolutional network`) → `ChebNet`, `GCN`; `Graph attention
  network` (attention-weighted) → `GAT`; `GraphSAGE` (sampled neighbourhood,
  learned aggregator); `Graph isomorphism network` (injective sum);
  `Equivariant graph network` (messages constrained to transform under a
  symmetry group) → `SchNet`, `EGNN`.
- children (descent): `Graph Transformer` (second parent `Transformer`).

### 11. Autoencoder  *(depth 0)*
- **positive test**: an encoder and a decoder trained together, with the code
  between them constrained; the halves are separable afterwards.
- **negative test**: an encoder–decoder shape whose decoder output is a
  different modality or task (that is a seq2seq or a segmentation network).
- **characteristic for children**: *the constraint imposed on the latent code.*
- children (division): `Variational autoencoder` (a distribution with a prior)
  → `beta-VAE`, `Conditional VAE`, `VQ-VAE` (discrete codebook) → `VQGAN`
  (second parent `GAN`); `Sparse autoencoder` (sparsity); `Denoising
  autoencoder` (robustness to corruption — B-10); `Masked autoencoder`
  (reconstruction from masked patches; second parent `Vision Transformer`).

### 12. Generative adversarial network  *(depth 0)*
- **positive test**: the named object is a generator trained against a
  discriminator, and the pair is what the paper releases.
- **negative test**: only the training objective changes (WGAN — B-11).
- **characteristic for children**: `—` (all children are descent).
- children (descent): `DCGAN` (second parent `Convolutional network`) →
  `ProGAN` → `StyleGAN`; `Conditional GAN` → `pix2pix` → `CycleGAN`; `BigGAN`.

### 13. Energy-based network  *(depth 0)*
- **positive test**: the parameters define a scalar energy over units and
  inference is a relaxation or sampling procedure, not a forward pass.
- **negative test**: a directed forward computation from input to output.
- **characteristic for children**: *the form of the energy and the connectivity
  it is defined over.*
- children (division): `Hopfield network` (deterministic, symmetric, binary) →
  `Modern Hopfield network`; `Boltzmann machine` (stochastic units; second
  parent `Undirected graphical model`) → `Restricted Boltzmann machine` →
  `Deep belief network`; `Neural energy-based model` (energy parameterized by a
  deep network).

### 14. Spiking neural network  *(depth 0)*
- **positive test**: units communicate by discrete events whose timing carries
  information.
- **negative test**: real-valued activations exchanged once per layer.
- **characteristic for children**: *the neuron model.*
- children (division): `Integrate-and-fire network` (LIF and variants),
  `Conductance-based network` (Hodgkin–Huxley, Izhikevich).
- *Low-confidence sibling set.*

### 15. Normalizing flow  *(depth 0)*
- **positive test**: the network is invertible by construction and its Jacobian
  determinant is tractable.
- **negative test**: a decoder that is not invertible (that is a VAE or a GAN).
- **characteristic for children**: *the form of the invertible transformation.*
- children (division): `Coupling-layer flow` → `NICE`, `RealNVP`, `Glow`;
  `Autoregressive flow` → `MAF`, `IAF`; `Continuous-time flow` (second parent
  `Neural ODE`) → `FFJORD`.

### 16. Factorization model  *(depth 0)*
- **positive test**: the learned object is a table of latent vectors, and the
  prediction is a product (inner, bilinear or low-rank) of rows of that table.
- **negative test**: the latent vectors are produced by a learned encoder from
  input features rather than looked up per entity.
- **characteristic for children**: *what the latent factors reconstruct.*
- children (division): `Matrix factorization` (entries of an observed matrix) →
  `NMF`, `Probabilistic matrix factorization`, `PCA`; `Tensor factorization` →
  `CP decomposition`, `Tucker decomposition`; `Factorization machine` (feature
  interactions) → `DeepFM` (second parent `Feedforward network`);
  `Knowledge-graph embedding` (triples) → `TransE`, `DistMult`, `ComplEx`,
  `RotatE`; `Word embedding model` (corpus co-occurrence) → `word2vec` →
  `DeepWalk`, `node2vec`, `fastText`; `GloVe`.
- B-12 records that word2vec's own framing is a shallow log-linear network, not
  a factorization.

---

## 4. Quarantine: names that are not nodes

Treated exactly as `machine learning` and `deep learning` were in the domains
design — reported as a line, excluded from family shares, never a node:

`neural network`, `deep neural network`, `artificial neural network`, `deep
learning model`, `machine learning model`, `model`, `transformers` as a mass
noun, `encoder`, `decoder`, `backbone`, `baseline`, `classifier`, `regressor`,
`generative model`, `discriminative model`, `foundation model`, `pretrained
model`, `language model`, **`large language model` / `LLM`**, `vision-language
model`, `multimodal model`, `self-supervised model`, `ensemble`.

Three of these are worth their own line:

- **`large language model` / `LLM`.** Quarantined. It names no release, and
  what it adds to "decoder-only Transformer" is scale and use — the two things
  the brief forbids dividing by (`MODELS_BRIEF` B.2: no `Large models` node
  anywhere). B-13 records the rejected reading.
- **`vision-language model` / `multimodal model`.** Quarantined. CLIP, BLIP,
  LLaVA and Flamingo are **composites** (R5): their parents are their image and
  text encoders, which already expresses everything a VLM node would. Modality
  is the application, a rejected characteristic.
- **`diffusion model`.** Not a node, by the brief's own fixed point: the model
  is the denoiser (a U-Net or a DiT), the denoising procedure is the algorithm.
  Named *releases* (`Stable Diffusion`, `DiT`) are composites and do get nodes —
  via the second pass, under their denoiser and their autoencoder. B-14.

Algorithm-only terms encountered while drafting, listed so the algorithms
derivation inherits them rather than rediscovering them: k-NN, kernel density
estimation, bagging, boosting, AdaBoost, Lloyd's algorithm, EM, backpropagation,
Adam/SGD/AdamW, PPO/SAC/DQN/A3C (the update rules), MCTS, beam search, SimCLR/
BYOL/DINO/MoCo (the SSL objectives), the diffusion forward/reverse process,
WGAN's objective, contrastive and triplet losses, LoRA and QLoRA (B-15).

---

## 5. Pre-registered predictions for phase 2

Written now, so that phase 2 is a test rather than a rationalization. I expect
the corpus to:

1. contain a long tail of **size and checkpoint spellings** (`bert-base-uncased`,
   `resnet50`, `llama-2-7b-chat`) — handled by R3 nodes plus `SPELLINGS.tsv`;
2. contain **algorithm names filed as models** (PPO, SimCLR, Adam) — a type
   confusion, not a blind spot in this tree;
3. be **thin on roots 13, 14, 15, 16** (energy-based, spiking, flows,
   factorization) — thin is not absent, and PROCESS rule 1 says a node with no
   corpus support is *possibly speculative, justify or keep*, not deleted;
4. be **heavy on roots 7 and 9** (CNN, Transformer), which is where the
   designed intermediate levels have to earn their keep;
5. contain at least one family I have missed entirely. My own guesses at where:
   **rule-based / inductive-logic models**, **neuro-symbolic architectures**,
   **classical time-series models (ARIMA)**, **operator-learning networks
   (DeepONet, FNO)**, **physics-informed networks (PINN)**, **world models**,
   and **retrieval-augmented architectures (RAG, RETRO)**.

A root I considered and did not create: **`Rule-based model`** (decision lists,
association rules, ILP hypotheses, fuzzy rule systems). Dropped because
`Decision tree` already covers the partition-and-rule shape for the cases I
could name with confidence, and inventing a near-empty root is worse than
adding one in phase 2 if the corpus shows it is real.

## 6. Boundary cases raised in phase 1

B-01 MLP under Perceptron · B-02 LDA placement · B-03 Gaussian process
admission · B-04 k-means admission · B-05 RNN as a state-space model ·
B-06 backbone-parametric detectors · B-07 GRU under LSTM · B-08 seq2seq as a
composite · B-09 ViT's depth vs the brief's worked example · B-10 denoising and
masked autoencoders as objectives · B-11 WGAN · B-12 word2vec's framing ·
B-13 `large language model` · B-14 diffusion releases · B-15 LoRA adapters.
Full rows, with the reading chosen *and* the reading rejected, in
`BOUNDARY_CASES.tsv`.

## 7. Families flagged now for a deeper design pass (R7)

`BERT`, `Vision Transformer`, `LLaMA`, `GPT`, `Residual network`, `U-Net`,
`Decoder-only Transformer` as a whole. Reasons in `SELF_AUDIT.md`.
