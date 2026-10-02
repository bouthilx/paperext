# Lineage axis — self audit

The granularity audit of `PROCESS.md` §3 run on the merged output, plus the two
things the brief asks for most loudly: **the sibling sets I am not confident in,
worst first**, and **every family I expect to need a deeper design pass** (R7 —
a family left flat stays flat).

90 nodes have children: 54 sibling sets of two or more, and 36 nodes with
exactly one child. 62 nodes pin a connectivity value, 66 a topology value, 25 an
attributes value.

---

## 1. Rule violations and discipline checks

### 1.1 R4 — "a parent with exactly one child is a rename of that child"

Checked mechanically on the output. **Eight `division` (grouping) nodes exist
and all eight have two or more children:**

| division node | children |
|---|---|
| `Bagged tree ensemble` | 2 |
| `Boosted tree ensemble` | 2 |
| `Directed graphical model` | 8 |
| `Undirected graphical model` | 4 |
| `Coordinate MLP` | 5 |
| `Reservoir network` | 2 |
| `Coupling-layer flow` | 3 |
| `Autoregressive flow` | 2 |

**Two one-child grouping nodes were inherited from the runs and repaired:**

- run B's `Topic model` had only `Latent Dirichlet allocation`. Deleted; LDA
  attaches to `Directed graphical model` (run A's placement).
- run B's `Continuous-time flow` had only `FFJORD`. Relabelled: it is `cnf`, a
  **descent** node naming a real design (Chen et al.), not a grouping node.
  Declared at L-13 — the cost is that the flow division is no longer total.

The remaining 36 one-child nodes are all **descent** edges from one named
design to one named descendant (`ID3`→C4.5, `AlexNet`→SqueezeNet, `NTM`→DNC,
`Gopher`→Chinchilla, `ChebNet`→GCN, `progan`→StyleGAN, …). R4(2) governs the
admission of *intermediate grouping* nodes, not the length of a derivation
chain, so none of these is a violation. The three I would still look at twice,
because the parent adds little beyond its child, are `Mistral`→Mixtral,
`Transe`→RotatE and `Slot attention`→SlotFormer.

### 1.2 Never shape structure to balance mentions

**No sibling anywhere exists because it was large in this corpus, and no node
was split or merged to even out a count.** `Transformer` holds 35 direct
children and `Convolutional network` 29; both are reported, not repaired.
`model_names.tsv` was opened only for blind spots (four coverage additions, §5)
and for speculative flags.

The inverse check is the one that fails honestly: **61 nodes have no corpus
support at all and are kept**, including the entire word-embedding chain
(word2vec, CBOW, skip-gram, fastText, DeepWalk, node2vec — zero mentions),
`3D Gaussian splatting` (zero), and the normalizing-flow coupling family (Glow,
NICE, IAF, FFJORD — zero). A corpus-led pass would have deleted all of them.

### 1.3 Rules I knowingly bend

1. **L-13** — the normalizing-flow division is not total: `Continuous
   normalizing flow` is a descent node sitting beside two division nodes.
2. **L-15 / run B's B-12 inverted** — `word2vec` is now placed by its paper's
   framing (R1 satisfied), but `GloVe`, `PCA`, `ICA`, `CCA`, `ARIMA`,
   `Cox model` and `Naive Bayes` are still placed **by kind**, because R1's
   framing test presupposes a paper-derivation culture that pre-1990 statistics
   does not have. Run A declared this at its B10; it is unrepaired here.
3. **L-25** — `Knowledge-graph embedding model`'s characteristic is a scoring
   design, but it is one sentence away from "data structure consumed".
4. `Transformer` has no topology pin, which is correct (topology is
   single-valued and varies) but means the root asserts less about its
   descendants than any other root in the file.

## 2. Sibling sets I am **not** confident in, worst first

**1. `Transformer`, 35 children.** The owner ordered this shape and the cut it
replaces survives on the topology axis, so it is not a mistake — but it is the
set a reader will stop at. It mixes founding LLM families (GPT, LLaMA, Mistral),
single artifacts (Whisper, Perceiver, AlphaFold), hybrids arriving from other
roots (Conformer, wav2vec 2.0, DETR, Graph Transformer, RWKV) and composites
(CLIP, Flamingo). R7 means it stays this way until a design pass opens it, and I
cannot name a division that is a property of the model and is not already an
axis. The one candidate both runs surfaced — positional/attention-block
configuration (absolute / rotary / ALiBi; dense / sparse FFN) — I did not adopt,
because it is a layer property and because sparse attention has no axis value
either (§4).

**2. `Convolutional network`, 29 children.** Deleting run B's four axis-value
groupings took the load off three of its seven divisions but made the set wider,
not narrower: FCN, LeNet, AlexNet, VGG, MobileNet, ShuffleNet, WaveNet, TCN and
DeepLab all moved up. The set still mixes classification backbones, detectors
(R-CNN, YOLO, SSD, RetinaNet, FPN), sequence models, video models, an
equivariance generalisation and six hybrids. Run A could not find a division
that survives R4 and neither can I: the field's names for CNN sub-kinds coincide
with their founding artifact, so a grouping node renames its own first child.
**This is the family where I would most welcome being overruled**, and the one
where the three axes genuinely carry less of the load than they do elsewhere.

**3. `Knowledge-graph embedding model` as a root** (L-25). Four children, one
principle, field-named — and the principle is the rejected characteristic in
good clothes. If any part of the M-01 resolution is wrong, it is this node. The
alternatives are both worse (two more roots, or reading TransE's explicit
contrast with tensor-factorization models as descent).

**4. `Linear model`, 9 children.** Supervised predictors (linear regression,
logistic regression, GLM, Cox), a discriminant (LDA), a time-series model
(ARIMA), a learning rule (Perceptron), a two-view projection (CCA) and a kernel
machine arriving as a second parent (Linear SVM) are not one kind at one
specificity. Moving PCA out to `Matrix factorization` helped; it did not fix it.
Underneath is §1.3(2): R1 cannot place classical statistics at all.

**5. `Matrix factorization`, 7 children.** The surviving half of the M-01
resolution, and it inherits run B's complaint about its own `Factorization
model`: a matrix, a tensor, a feature interaction and a word co-occurrence table
are not values of one variable so much as a list. The difference from run B is
that the list is now short and each member is a real design family, with the
shared "low-rank table" content on the connectivity axis instead. If this root
is ever trimmed, trim `Tensor factorization` and `GloVe` first.

**6. `Recurrent network`, 10 children — mixed kind.** `LSTM` and `GRU` are
recurrent *cells*; `Seq2seq`, `NTM`, `Memory network`, `RSSM` and `Reservoir
network` are *systems built from* cells. Run A declared this defect and could
not satisfy R4(3) for the repair ("a recurrent unit" is not definable without
pointing at its members). I inherit the defect unrepaired.

**7. `Directed graphical model`, 8 children.** Reads as a crossroads rather than
a family: two children (`HMM`, `LDS`) arrive as second parents from the
state-space root, and `Variational autoencoder` arrives from the deleted
autoencoder root (L-02). It is the only place where a deep-learning family sits
among classical statistics, and the join is R1-legitimate but visually jarring.

**8. `BERT`, 17 children — mixed specificity.** RoBERTa (a retraining recipe),
DistilBERT (a compression), CodeBERT (a corpus change), ViLBERT (a composite
arriving with a CNN parent) and BEiT (arriving from ViT) are not at one level.
Both runs refused the obvious four-value division because it does not partition
(DeBERTa changes architecture *and* objective; XLM-R is RoBERTa's objective on a
new corpus). Flagged for a design pass by both runs and by this one.

**9. `U-Net`, 8 children**, and the detection chain under `R-CNN`. Neither is
wrong; both will be the first places the second pass wants a grouping node.

## 3. Families that need a deeper design pass (R7)

R7 means a family left flat **stays** flat — the second pass may attach by
descent but may not create a grouping node. This list is a commitment.

| rank | family | why | candidate principle, if any |
|---|---|---|---|
| 1 | **`Transformer` (35)** | the widest set in the file, created by the owner's (correct) removal of the topology level | none that is a model property and not already an axis. The honest answer may be that it is flat by nature, and that the useful cuts are the topology axis above it and the family level below |
| 2 | **`BERT` (17)** | the brief's named case; ~30 corpus names in the family | *which aspect of BERT's recipe the variant changes*, accepting that a variant may take two values (multi-parent already permits this) |
| 3 | **`Convolutional network` (29)** | §2.2 | unknown. Every candidate is either an axis value (now pinned) or a rejected characteristic |
| 4 | **`ViT` (11)** | mixes scale variants (Swin), training variants (DeiT, BEiT, MAE) and composites (CLIP, SAM, DiT) | *whether the variant changes the patch/scale structure, the pretraining objective, or composes ViT with another encoder* |
| 5 | **`Slot attention` (1)** | a root with one designed child and a real ~8-name corpus cluster (DINOSAUR, BO-QSA, RSM, disentangled slot attention) that will otherwise hang flat off the root | *whether the variant changes the binding mechanism, the decoder, or adds dynamics* |
| 6 | **`U-Net` (8)** | nnU-Net, 3D U-Net, UNet++, Attention U-Net, and the medical-SAM adjacency | *which part of the U-shape the variant modifies: the skip path, the dimensionality, or the block type* |
| 7 | **`Recurrent network` (10)** | §2.6, the cell-vs-system level | the field does name *recurrent unit* vs *recurrent architecture*; R4(3) is the obstacle |
| 8 | **`Graph neural network` (8)** | the spectral/spatial division was refused by both runs on GCN's bridge status, and that refusal is now partly redundant because the split is pinned on the connectivity axis | re-examine: with connectivity pinned, a lineage division may no longer be needed at all |
| 9 | **`LLaMA`, `GPT`, `ResNet`** | wide, but almost entirely through R3 size/chat/generation variants | **no grouping needed** — recorded so a later pass does not invent one by analogy with BERT. This is the R7 distinction made concrete |

## 4. What the refactor did **not** fix

Three cross-cutting properties still have no home on any of the four axes, and
every one of them was deliberately refused as a lineage node by both runs:

- **attention sparsity / sub-quadratic attention** — Longformer, BigBird,
  Performer, Linformer, Reformer. `Longformer` is in the file as a descent child
  of RoBERTa and pins nothing, which is a lie of omission.
- **distillation / compression** — a relation between two releases (DistilBERT,
  TinyBERT, MobileBERT, DistilHuBERT, distilgpt2). It is a large and visible
  pattern in the corpus and it is recorded only in `notes`.
- **instruction tuning / chat alignment** — a training stage; the releases are
  R3 nodes under their base model, which is right, but "proportion of papers
  using an instruction-tuned model" is unanswerable from any axis.

And five connectivity gaps plus the above are listed in `MERGE_RATIONALE.md` §6.

## 5. Changes made on corpus evidence, declared

`model_names.tsv` was consulted for blind spots and speculative flags only.
Four nodes exist because of it, none of which created or changed a sibling set's
*principle*:

- **`EEGNet`** (3 papers) and **`ViLBERT`** (3 papers) — attested families that
  **neither run saw**. EEGNet is a depthwise-separable convnet over EEG arrays;
  ViLBERT is a two-stream BERT over text and CNN region features (R5 composite).
- **`UNet++`** and **`SlotFormer`** — added so that `U-Net`'s variant set and the
  `Slot attention` root are not left as the thinnest nodes in their families.

Other families the corpus names that **neither run saw** and that this file
still does not place: `GearNet` / `ESM-GearNet` (protein structure GNN — listed
as an `EGNN` example), `StarCoder` and `CodeGen` (code LLMs — second-pass
leaves under `Transformer`), `FAENet` (listed under `Group-equivariant CNN`),
`CNN14` (an audio convnet), `REALM` / `kNN-LM` (retrieval-augmented composites,
which both runs refused to group — A/B07 — and which now have no axis value for
retrieval either, although the attributes axis's `External memory` is the
nearest fit and should probably claim them).

## 6. What would falsify this merge fastest

1. **Check whether the `Transformer` and `topology` cuts actually split the
   corpus.** If the corpus is 95% causal-decoder by mention, the topology level
   is correct but useless, and the useful level is the family one below — which
   is an argument about where to cut, not about the structure.
2. **Count what leaves the hierarchy entirely.** GFlowNet (~33 names, among the
   ten most frequent), diffusion (~37 names), GAN-as-root, energy-based models,
   SimCLR/BYOL/DINO/VICReg/Barlow Twins, PPO/SAC/DQN/Rainbow/IMPALA/MuZero. The
   owner should see that number before the admission rule is frozen, because it
   is the single largest consequence of this design and it is not visible from
   the node count.
3. **Verify the R1 framings asserted from memory.** Roughly 270 edges rest on
   "the introducing paper defines A relative to B" and none was checked against
   a paper in this merge. The ones the root set turns on:
   word2vec-vs-feedforward-NNLM (L-15), GloVe's two parents (L-14), Hopfield-vs-
   Ising (L-04), U-Net-vs-FCN, GCN-vs-ChebNet, CycleGAN-vs-pix2pix,
   OPT/GPT-NeoX-vs-GPT-3, Kingma's directed-model framing (L-02).
4. **Re-run the pin column against the three axes** once they settle, since six
   nodes are unpinnable today (§4) and one node (`VQ-VAE`) reverses a parent's
   attribute — the only case of its kind, and worth confirming it is intended.
5. **Then** the step already scheduled: diff against the domains
   `Method › Model design` subtree, which was not read.
