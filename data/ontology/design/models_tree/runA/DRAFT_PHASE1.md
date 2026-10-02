2026-10-02T11:18:50-04:00

# Models hierarchy — Phase 1 draft (corpus-free)

**Run A.** This file was written with **no corpus access of any kind**. No file
under `data/ontology/` was opened except the three briefs I was told to read
(`MODELS_DERIVATION_BRIEF.md`, `MODELS_BRIEF.md`, `PROCESS.md`). In particular
`model_names.tsv` was not opened before this file was complete, and none of the
forbidden inputs (`models/v0`, `design/axes/`, `run1-3`,
`proposed_categories.csv`, `categorized_models.json`, `datasets/`, `domains/`)
was opened at any point in this run.

Everything below is derived from (a) the rules R1-R7 of the derivation brief and
(b) my own knowledge of the ML literature, with ACM CCS `Computing
methodologies`, arXiv categories (cs.LG / cs.CV / cs.CL / stat.ML / eess.AS) and
Papers With Code used from memory for **breadth and vocabulary only**.

---

## 0. How I read the rules before applying them

Four readings had to be fixed before any node could be written down. Each one is
a decision, not an observation, so each is recorded here and repeated in
`RATIONALE.md`.

**(a) `characteristic` is the principle that divides a node's *children*.**
`positive_test` / `negative_test` say what the node itself *is*. So a node whose
children are all lineage descendants (R1) has no dividing principle and its
`characteristic` reads `(descent)`; a node that introduces an R4 grouping level
states the principle there. This is PROCESS §2 rule 1 read literally — "one
principle of division per sibling set, **wherever a sibling set is produced by
division rather than by descent**" (R6).

**(b) Lineage is not subsumption, and where they disagree lineage wins.**
A generalized linear model is a *superset* of linear regression in extension but
a *descendant* of it in lineage (Nelder & Wedderburn generalized the linear
model in 1972). The backbone is "the child was derived from the parent" (§3), so
GLM is a child. Consequence to accept up front: an ancestor's extension does not
always contain its descendants', and the tree must not be read as an is-a
taxonomy. This recurs for `Tree ensemble` under `Decision tree` and for
`Kernel machine` over `SVM`.

**(c) Series-flattening rule.** Within a named series — GPT-2/3/4, LLaMA 2/3,
Fast / Faster / Mask R-CNN, StyleGAN2/3 — every release attaches to the
**founding node of the series**, and its immediate predecessor is recorded in
`notes`. A strict R1 chain would be truer to each paper's framing (GPT-3's paper
says "same model and architecture as GPT-2") but would push the designed depth
to 5-6 in the largest families and make the usable cut depend on generation
number. The brief's own diagram in §3 flattens exactly this way
(`GPT ───── GPT-2, GPT-3, GPT-4`), so this reading follows it. Declared as a
boundary case because it is a real loss: the generation order survives only in
`notes`.

**(d) Contrast is not descent.** A paper that names an architecture in order to
*replace* it has not derived from it. "Dispensing with recurrence and
convolutions entirely" (Transformer) makes the Transformer a root, not a child
of the RNN; "instead of summing features as in ResNets" (DenseNet) makes DenseNet
a child of the convolutional network, not of ResNet; "radiance field rendering
without neural networks" (3D Gaussian splatting) makes it a root. This is R2
applied in its sharpest form and it decides about a dozen placements below.

---

## 1. The root set (R6)

A root is an architecture whose defining idea is not a modification of another
architecture *in this tree*. Seventeen of them.

| # | root | defining idea (what the learned object is) |
|---|---|---|
| 1 | **Linear model** | an affine map of the input features; parameters are one weight vector per output |
| 2 | **Kernel machine** | prediction is a learned weighted sum of kernel evaluations against stored training points |
| 3 | **Decision tree** | a recursive axis-aligned partition of the input space; parameters are the splits and the leaf values |
| 4 | **Feedforward network (MLP)** | a stack of dense affine layers with elementwise nonlinearities; no weight sharing, no state |
| 5 | **Convolutional network** | weight-shared local filters swept over a grid-structured input |
| 6 | **Recurrent network** | a hidden state carried across sequence positions by a weight-shared transition |
| 7 | **Transformer** | stacked self-attention over a set of tokens with positional encoding; no recurrence, no convolution |
| 8 | **Graph neural network** | permutation-equivariant message passing over an input-supplied graph |
| 9 | **Probabilistic graphical model** | a factorization of a joint distribution whose factors follow a graph |
| 10 | **State space model** | a latent state evolving under a transition operator and read out by an emission operator |
| 11 | **Autoencoder** | an encoder and a decoder trained through a bottleneck so that the output reconstructs the input |
| 12 | **Generative adversarial network** | a generator paired with a discriminator that scores its samples |
| 13 | **Normalizing flow** | an invertible map with a tractable Jacobian determinant, so density transforms exactly |
| 14 | **Embedding model** | a table of learned vectors indexed by discrete entities, scored by a simple function of those vectors |
| 15 | **Spiking neural network** | units communicating by discrete spikes with membrane-potential dynamics |
| 16 | **Rule-based model** | an explicit set of symbolic conditions, learned and then applied as the predictor |
| 17 | **3D Gaussian splatting** | an explicit, optimizable set of geometric primitives rendered differentiably; no network |

### 1.1 Why there is no `Neural network` super-root

The brief settles it (`§4.7`): `neural networks` is an uninformative generic and
is quarantined, as `machine learning` was in the domains design. I would have
reached the same place from R6: "neural network" is not an architecture whose
defining idea could be modified into another; it is the union of six roots, and
a root that contains the Transformer, the CNN, the RNN, the MLP, the GNN and the
SNN makes every neural cut answer "yes". Its only effect would be to add one to
every depth.

### 1.2 Why 17 and not 8-15

R6 sets a smell test of 8-15 and says explicitly that it is **never** a reason to
merge or split a root I otherwise believe in. I am two over. The check R6 asks
for is whether releases have been promoted to roots because their lineage was not
traced. Working through the four thinnest:

- **Spiking neural network** — a different neuron model, not a modification of
  any architecture here. Thin family, real root.
- **Rule-based model** — thin and the one I most expect phase 2 to flag as
  speculative. Kept because the domains external diff found logic/relational
  learning to be a genuine blind spot that no corpus check could have revealed,
  and because R7 means an unplaceable name has nowhere to go later.
- **3D Gaussian splatting** — a *single artifact* promoted to a root, which is
  the exact smell R6 warns about. I promoted it anyway because its framing is
  explicitly a contrast with NeRF ("without neural networks"), so reading (d)
  forbids attaching it under `Coordinate MLP`, and nothing else in the tree is
  its ancestor. Declared, not defended.
- **Embedding model** — the one root I built rather than found; see §5.

One root I considered and **dropped**: `Energy-based network` (Hopfield,
Boltzmann machine, RBM, DBN). A Boltzmann machine *is* an undirected graphical
model with hidden units, and a Hopfield network is an Ising model with Hebbian
weights, so both attach under `Undirected graphical model` by R1. "Energy-based"
is a cross-cutting property, not a lineage; recording it as a root would have
been a fifth way of saying "has an energy function".

### 1.3 The declared property of a lineage backbone

R6 says to expect roots to be historically contingent rather than a clean
partition, and to say so. Said: **this root set does not partition anything.**
`Decision tree` and `Rule-based model` overlap in extension (a tree *is* a rule
set) and are separate roots because neither was derived from the other.
`Probabilistic graphical model` and `Recurrent network` overlap at the HMM.
`Linear model` and `Kernel machine` overlap at the linear SVM. Counting is
non-exclusive by design (E1 #16), so overlap costs nothing; pretending to a
partition would have cost the backbone.

---

## 2. The tree

Notation: `[D]` marks a node admitted by **R4 as a grouping/division node** —
every other node is there by **R1 descent**. `{a,b}` after a node lists its
parents when there is more than one (R5); `H` = hybrid, `C` = composite.
Indentation is the edge. Size variants (`resnet-50`, `llama2-7b`) are **not**
listed: they are nodes by R3 but they are the second pass's job under R7.

```
Linear model
├── Linear regression
├── Logistic regression
│   └── Multinomial logistic regression
├── Generalized linear model
├── Perceptron
└── ARIMA

Kernel machine
├── Support vector machine
│   ├── Linear SVM
│   ├── Support vector regression
│   └── One-class SVM
├── Gaussian process
│   └── Deep Gaussian process
└── Kernel ridge regression

Decision tree
├── CART
├── ID3
│   └── C4.5
├── Decision stump
└── Tree ensemble                                   [D] divides by combination
    ├── Bagged tree ensemble                        [D]
    │   ├── Random forest
    │   │   └── Extremely randomized trees
    │   └── Isolation forest
    └── Boosted tree ensemble                       [D]
        ├── Gradient-boosted decision trees
        │   ├── XGBoost
        │   ├── LightGBM
        │   └── CatBoost
        └── AdaBoost ensemble

Feedforward network (MLP)
├── MLP-Mixer
├── Deep Sets
│   └── PointNet
├── Coordinate MLP (implicit neural representation) [D]
│   ├── NeRF
│   │   ├── Instant-NGP
│   │   └── Mip-NeRF
│   ├── SIREN
│   ├── DeepSDF
│   └── Occupancy network
└── (MADE listed under Autoencoder)

Convolutional network
├── LeNet
├── AlexNet
├── VGG
├── Inception (GoogLeNet)
│   └── Xception
├── ResNet
│   ├── ResNeXt
│   ├── Wide ResNet
│   ├── SE-ResNet (SENet)
│   ├── ConvNeXt
│   └── Neural ODE
├── DenseNet
├── MobileNet
│   └── EfficientNet
├── ShuffleNet
├── SqueezeNet
├── R-CNN
│   ├── Fast R-CNN
│   ├── Faster R-CNN
│   └── Mask R-CNN
├── YOLO
├── SSD
├── RetinaNet
├── Feature pyramid network
├── Encoder-decoder convnet                         [D] divides by resolution path
│   ├── FCN
│   ├── U-Net
│   │   ├── 3D U-Net
│   │   ├── nnU-Net
│   │   └── Attention U-Net
│   └── SegNet
├── DeepLab
├── WaveNet
├── Temporal convolutional network
├── PixelCNN
├── I3D
├── SlowFast
├── Group-equivariant CNN
│   └── Steerable CNN
└── Capsule network

Recurrent network
├── Elman RNN
├── LSTM
│   ├── BiLSTM
│   ├── ConvLSTM        {LSTM, Convolutional network}  H
│   └── Tree-LSTM
├── GRU
├── Echo state network
├── Neural Turing Machine
│   └── Differentiable Neural Computer
├── Memory network
├── Seq2seq
│   └── Attentional seq2seq
├── PixelRNN
└── RWKV                {Recurrent network, Transformer}  H

Transformer                                         [D] divides by stacks retained
├── Encoder-only Transformer                        [D]
│   ├── BERT
│   │   ├── RoBERTa
│   │   │   └── XLM-R
│   │   ├── ALBERT
│   │   ├── DistilBERT
│   │   ├── ELECTRA
│   │   ├── DeBERTa
│   │   ├── TinyBERT
│   │   ├── MobileBERT
│   │   ├── Sentence-BERT
│   │   ├── mBERT
│   │   ├── BioBERT
│   │   ├── SciBERT
│   │   ├── ClinicalBERT
│   │   ├── CodeBERT
│   │   └── ProtBERT
│   ├── Vision Transformer (ViT)
│   │   ├── DeiT
│   │   ├── Swin Transformer
│   │   ├── BEiT            {ViT, BERT}                 H
│   │   ├── Masked autoencoder (MAE)  {ViT, Autoencoder} H
│   │   ├── DINOv2
│   │   ├── Segment Anything (SAM)
│   │   └── Diffusion Transformer (DiT)
│   ├── wav2vec 2.0         {Convolutional network, Encoder-only}  H
│   │   └── HuBERT
│   ├── Conformer           {Convolutional network, Encoder-only}  H
│   ├── Perceiver
│   └── ESM
├── Decoder-only Transformer                        [D]
│   ├── GPT
│   │   ├── GPT-2
│   │   ├── GPT-3
│   │   ├── GPT-3.5
│   │   ├── GPT-4
│   │   └── GPT-NeoX
│   ├── LLaMA
│   │   ├── Llama 2
│   │   ├── Llama 3
│   │   ├── Vicuna
│   │   ├── Alpaca
│   │   └── Code Llama
│   ├── Mistral
│   │   └── Mixtral
│   ├── OPT
│   ├── BLOOM
│   ├── Falcon
│   ├── PaLM
│   ├── Gopher
│   │   └── Chinchilla
│   ├── Qwen
│   ├── Gemma
│   ├── Phi
│   ├── DeepSeek
│   ├── OLMo
│   ├── Claude
│   ├── Gemini
│   ├── Transformer-XL
│   │   └── XLNet
│   └── Decision Transformer
├── Encoder-decoder Transformer                     [D]
│   ├── T5
│   │   ├── mT5
│   │   ├── Flan-T5
│   │   ├── ByT5
│   │   └── UL2
│   ├── BART
│   │   └── mBART
│   ├── Pegasus
│   ├── Whisper
│   └── DETR               {Convolutional network, Encoder-decoder}  H
└── (composites, attached to their parts)
    ├── CLIP               {ViT, Decoder-only}                      C
    ├── BLIP               {ViT, BERT}                              C
    ├── Flamingo           {ViT, Decoder-only}                      C
    ├── LLaVA              {CLIP, LLaMA}                            C
    └── Stable Diffusion   {U-Net, VAE, CLIP}                       C

Graph neural network
├── ChebNet
├── GCN
│   └── R-GCN
├── GAT
├── GraphSAGE
│   └── PinSAGE
├── GIN
├── Message passing neural network
│   ├── SchNet
│   └── DimeNet
├── E(n)-equivariant GNN
├── Graph Transformer      {GNN, Encoder-only Transformer}          H
└── Graph autoencoder      {GNN, Autoencoder}                       H

Probabilistic graphical model                       [D] divides by edge semantics
├── Directed graphical model (Bayesian network)     [D]
│   ├── Naive Bayes
│   ├── Hidden Markov model   {Directed GM, State space model}      H
│   ├── Latent Dirichlet allocation
│   └── Mixture model
│       └── Gaussian mixture model
└── Undirected graphical model (Markov random field)[D]
    ├── Conditional random field
    ├── Markov random field (Ising/Potts)
    ├── Hopfield network
    │   └── Modern Hopfield network
    └── Boltzmann machine
        ├── Restricted Boltzmann machine
        │   └── Deep belief network
        └── Deep Boltzmann machine

State space model
├── Linear dynamical system (Kalman filter model)
├── S4
│   ├── S5
│   ├── H3
│   └── Mamba
└── Recurrent state space model (RSSM)  {SSM, Recurrent network}    H

Autoencoder
├── Variational autoencoder
│   ├── beta-VAE
│   ├── Conditional VAE
│   └── VQ-VAE
│       └── VQGAN          {VQ-VAE, GAN}                            H
├── Denoising autoencoder
├── Sparse autoencoder
└── MADE

Generative adversarial network
├── DCGAN                  {GAN, Convolutional network}             H
├── Progressive GAN
│   └── StyleGAN
├── Conditional GAN
├── Pix2Pix
├── CycleGAN
├── BigGAN
└── SRGAN

Normalizing flow
├── NICE
│   └── RealNVP
│       └── Glow
├── Masked autoregressive flow  {Normalizing flow, MADE}            H
├── Inverse autoregressive flow
└── Continuous normalizing flow {Normalizing flow, Neural ODE}      H
    └── FFJORD

Embedding model                                     [D] divides by entity indexed
├── Word embedding model                            [D]
│   ├── word2vec
│   │   ├── CBOW
│   │   └── Skip-gram
│   ├── GloVe
│   └── fastText
├── Node embedding model                            [D]
│   ├── DeepWalk
│   ├── node2vec
│   └── LINE
├── Knowledge graph embedding model                 [D]
│   ├── TransE
│   ├── DistMult
│   ├── ComplEx
│   └── RotatE
├── Matrix factorization model
│   └── Non-negative matrix factorization
└── Factorization machine
    └── DeepFM             {Factorization machine, MLP}             H

Spiking neural network
└── Spiking CNN            {SNN, Convolutional network}             H

Rule-based model
├── Decision list
├── Rule set (RIPPER / CN2)
└── Logic program (ILP hypothesis)

3D Gaussian splatting
```

**Counts of this draft**: **266 nodes**, of which **17 are roots** and **13 are
R4 grouping nodes**; the remaining 236 are there by R1 descent. Maximum depth is
**4** (`Transformer › Encoder-only › BERT › RoBERTa › XLM-R`; also `Decision
tree › Tree ensemble › Boosted › GBDT › XGBoost`). Twelve nodes have two or more
parents. Size variants are excluded by design, so the second pass will roughly
double this before it stabilises.

---

## 3. Every grouping node, against R4

R4 admits a node N between P and its children only when (1) the field names the
distinction, (2) N has at least two substantive children, (3) N is definable
without listing its children. Thirteen nodes claim R4; here is each one's case.
A grouping node that cannot pass all three is not a grouping node, and the
alternative I rejected is named.

| grouping node | parent | principle of division | (1) field names it | (2) ≥2 children | (3) definable alone |
|---|---|---|---|---|---|
| **Tree ensemble** | Decision tree | — (descent; it divides its own children) | "ensemble methods" | ✓ | "a predictor that aggregates many decision trees" |
| **Bagged tree ensemble** | Tree ensemble | *how the member trees enter the prediction*: averaged over independently grown trees | "bagging" | RF, Isolation forest | ✓ |
| **Boosted tree ensemble** | Tree ensemble | same principle, other value: summed over sequentially fitted trees | "boosting" | GBDT, AdaBoost | ✓ |
| **Coordinate MLP** | MLP | *what the MLP's input is*: continuous coordinates, the signal stored in the weights | "implicit neural representation" | NeRF, SIREN, DeepSDF, Occupancy | ✓ |
| **Encoder-decoder convnet** | CNN | *the spatial-resolution path*: reduced then restored by learned upsampling to the input grid | "encoder-decoder / fully convolutional" | FCN, U-Net, SegNet | ✓ |
| **Encoder-only Transformer** | Transformer | *which of the original two stacks the model keeps, hence the attention mask*: full bidirectional attention over the whole input | universal usage | BERT, ViT, Conformer… | ✓ |
| **Decoder-only Transformer** | Transformer | same principle: causal attention over the model's own output | universal usage | GPT, LLaMA… | ✓ |
| **Encoder-decoder Transformer** | Transformer | same principle: both stacks, joined by cross-attention | universal usage | T5, BART, Whisper | ✓ |
| **Directed graphical model** | PGM | *the edge semantics of the factorization*: directed conditional factors | "Bayesian network" | NB, HMM, LDA, mixtures | ✓ |
| **Undirected graphical model** | PGM | same principle: undirected potentials over cliques | "Markov random field" | CRF, MRF, Hopfield, BM | ✓ |
| **Word embedding model** | Embedding model | *what the discrete entity indexed is*: a word/subword type | "word embeddings" | word2vec, GloVe, fastText | ✓ |
| **Node embedding model** | Embedding model | same principle: a node of one graph | "network embedding" | DeepWalk, node2vec, LINE | ✓ |
| **KG embedding model** | Embedding model | same principle: an entity or relation of a knowledge graph | "KG embedding" | TransE, DistMult, ComplEx, RotatE | ✓ |

### 3.1 Grouping nodes I considered and did **not** create

Each of these would have reduced a branching factor, which R4 explicitly forbids
as a motive. They are listed so that the absence is a decision rather than an
oversight, and so the second pass knows they were weighed (R7: it may not create
them on its own; it must flag the family).

- **Under CNN, by block type** — `Residual networks`, `Inception-style networks`,
  `Depthwise-separable networks`. Fails R4(2)/(3) in an interesting way: the
  field's name for each of these *is* its founding artifact ("residual network"
  ≡ the ResNet lineage), so the grouping node would be a rename of its own first
  child. The lineage edge already carries it.
- **Under CNN, by task** — `Detection architectures`, `Segmentation
  architectures`. This is the rejected "function learned" characteristic (§3 of
  the brief) one level down: Mask R-CNN detects and segments, U-Net segments
  medical images and denoises latents inside Stable Diffusion. Rejected.
- **Under CNN, by kernel rank** — 1-D / 2-D / 3-D convnets. This is "data
  structure consumed", rejected at level 1 for being a property of the
  application. I note it is the *least* clearly wrong of the three, because the
  kernel rank really is fixed in the weights, and leave it as a boundary case.
- **Under BERT, by what the variant changed** — `pretraining-objective variants`
  (RoBERTa, ELECTRA, ALBERT, DeBERTa), `domain/corpus variants` (BioBERT,
  SciBERT, CodeBERT, ProtBERT), `compressed variants` (DistilBERT, TinyBERT,
  MobileBERT), `multilingual variants` (mBERT, XLM-R). The field does name all
  four, and this is the family the brief singles out as needing a deeper pass.
  **Not created**, because the four values do not partition: DeBERTa changes
  architecture *and* objective, TinyBERT is compressed *and* re-distilled on new
  data, XLM-R is RoBERTa's objective on a multilingual corpus. A division whose
  values overlap produces exactly the `X and Y` nodes PROCESS §2 rule 2 warns
  about. Flagged in `SELF_AUDIT.md` as the number-one candidate for the deeper
  design pass instead.
- **Under GNN, spectral vs spatial** — genuinely field-named and nearly
  admitted. Rejected because GCN, the largest member, is the bridge case
  (derived as a first-order approximation of a spectral filter, universally
  implemented as message passing), so the division would put its biggest member
  in the wrong box or in both. Boundary case.
- **Under Decoder-only Transformer, open-weights vs proprietary** — licensing,
  not architecture. Not a characteristic of the model at all.
- **Under RNN, gated vs ungated** — field-named, but it would hold exactly two
  children on one side (LSTM, GRU) and the rest on the other, and "gating" is a
  property of a *unit*, i.e. a layer. Rejected under the brief's §3 argument.

---

## 4. Admission: what did **not** enter this hierarchy

The admission rule (§2) sends a term to the `algorithms` hierarchy when it names
no separable learned object, or an object inseparable from the procedure. These
are the families I expect to meet most often in the corpus and route away. The
rule I applied follows `MODELS_BRIEF` B.1's worked SimCLR case: **when the named
term's architecture is a standard one already in the tree and the paper's
contribution is the objective or the update rule, the term is an algorithm and
the model is the backbone.**

| term or family | routed to | the model, if a run has one |
|---|---|---|
| PPO, SAC, DQN, A3C, TD3, DDPG, Rainbow, IMPALA, MCTS | algorithms | the policy / value network (usually an MLP or a CNN) |
| SimCLR, MoCo, BYOL, DINO, SwAV, BarlowTwins | algorithms | the encoder the paper names (usually ResNet or ViT) |
| Diffusion, DDPM, DDIM, score matching, latent diffusion *as procedures* | algorithms | the denoiser — a U-Net, or a DiT |
| GFlowNet objectives (TB, DB, FM) | algorithms | the flow network |
| Adam, AdamW, SGD, LAMB, Adafactor | algorithms | — |
| k-NN, kernel density estimation, k-means | algorithms | none — no separable learned object |
| LoRA, QLoRA, adapters, prefix tuning | algorithms | the base model being adapted |
| RLHF, DPO, instruction tuning, knowledge distillation | algorithms | the student / the tuned release, which *is* a node when separately named |
| Bagging, boosting, stacking *as procedures* | algorithms | the ensemble, which is a node |
| Beam search, nucleus sampling, CFG | neither (inference-time; `algorithms[]` is learning-only) | — |

Three consequences worth stating, because each will look like a gap in the
corpus:

1. **There is no `Diffusion model` node.** The brief's table assigns the model
   role to the denoiser. `Stable Diffusion`, `Imagen`, `DALL-E 2` *are* nodes,
   as composites of named parts (R5). Bare `diffusion model` is routed to
   algorithms. This is the single most counter-intuitive consequence of the
   admission rule and it is written up as a boundary case.
2. **There is no `Large language model` / `Foundation model` node.** Both are
   generics over `Decoder-only Transformer` plus a licensing story. Quarantined
   with `neural network`.
3. **RL model names are mostly algorithms.** In a corpus with a heavy RL share
   this will remove a large block of names from the models dimension — which is
   the intended effect of settling entity types first (`MODELS_BRIEF` B.1), not
   a coverage failure.

### 4.1 Quarantine list (generics, excluded from family shares)

`neural network`, `deep neural network`, `deep learning model`, `machine
learning model`, `artificial neural network`, `foundation model`, `large
language model`, `language model`, `vision-language model`, `generative model`,
`discriminative model`, `classifier`, `regressor`, `encoder`, `decoder`,
`backbone`, `baseline`, `pretrained model`, `transformer-based model`,
`attention-based model`, `deep model`, `black-box model`, `surrogate model`,
`policy network`, `value network`, `critic`, `actor`, `student model`,
`teacher model`.

Two kinds are in that list and they should be reported separately: **class
generics** (`neural network`, `LLM`) and **role words** (`encoder`, `backbone`,
`policy network`, `teacher model`). A role word is not a weaker architecture
name, it is a different dimension — the role belongs on the entity's
`is_contributed` / `is_executed` fields or on the run, never in the tree.

---

## 5. Where this draft is weakest, before I look at anything

Written now so that phase 2 cannot be mistaken for having found it.

1. **`Embedding model` is a root I constructed.** No single paper founds it; I
   grouped word2vec, GloVe, DeepWalk, TransE and matrix factorization because
   their learned object is the same kind of thing (an indexed vector table with
   a cheap scoring function) and because otherwise each would strand. The
   division of its children by *what is indexed* is uncomfortably close to the
   rejected "data structure consumed" characteristic. Lowest-confidence root.
2. **`Autoencoder` as a root** is defined partly by what it learns
   (reconstruction), which is the rejected "function learned" characteristic. I
   kept it because the encoder-bottleneck-decoder *shape* is structural and the
   field treats it as an architecture class, and because a VAE's compute profile
   is genuinely autoencoder-shaped. Second-lowest-confidence root.
3. **Mixed sibling sets** at three places: under `MLP` (two descent children and
   a grouping node), under `Embedding model` (three grouping nodes beside two
   descent children), under `CNN` (one grouping node among twenty descent
   children). Legal under R4 but it makes those sets hard to audit.
4. **The Transformer division is load-bearing and I deviated from the brief to
   keep it total.** See the boundary cases.
5. **Everything after about depth 3 in the vision branch is thinner than the
   language branch**, not because vision is simpler but because my recall of
   lineage framings is better for language.

## 6. Predictions for phase 2

Stated before opening `model_names.tsv`, so that the two phase-2 questions can be
answered honestly and so the "corpus never arbitrates" claim is checkable.

I expect the corpus to show:

- **Blind spots I will have to add**: time-series/forecasting models (N-BEATS,
  Informer, PatchTST, Prophet), tabular deep models (TabNet, FT-Transformer),
  speech beyond wav2vec (Tacotron, HiFi-GAN, DeepSpeech), protein/molecule models
  (AlphaFold, ESM variants, MolGAN), recommender architectures (DeepFM is in,
  but DIN/SASRec/BERT4Rec are not), and a block of 2024-era open LLMs I have not
  named.
- **Nodes phase 2 will flag as speculative**: `Rule-based model` and its three
  children, `Spiking neural network`, `Echo state network`, `Occupancy network`,
  `LINE`, `Deep Gaussian process`, `Isolation forest`, `Modern Hopfield network`.
- **The generic/quarantine block to be large** — `neural network` and
  `deep learning` style strings, plus role words, plausibly in the top 30 by
  frequency.
- **A long tail of release strings** (`bert-base-uncased`, `llama2-7b`,
  `resnet50`) that are nodes under R3 but belong to the second pass, not here.

What I will **not** do with the corpus: move a node, create a node to cover a
cluster that an existing node already covers at a coarser level, delete a node
for being absent, or let a frequency change any division principle. A corpus
cluster that makes me want to restructure becomes a finding in `RATIONALE.md`.

**End of phase 1. Nothing below this line existed before `model_names.tsv` was
opened.**
