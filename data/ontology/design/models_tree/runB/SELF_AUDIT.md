# Models hierarchy (run B) — self audit

The granularity audit of `PROCESS.md` §3, run by the author on the author's own
output. Three questions per sibling set: are these the same *kind* of thing, at
the same level of specificity, and **does any sibling exist only because it was
large in this corpus?**

Then, and more importantly: **the sets I am not confident in**, and **every
family I expect to need a deeper design pass** (R7 — a family left flat stays
flat).

---

## 1. Audit result, set by set

**Sets that pass cleanly** (same kind, same specificity, no corpus-shaped
sibling): `Linear model`'s link children; `Kernel machine`; `Decision tree`;
`Probabilistic graphical model`; `Undirected graphical model`; `State-space
model`; `Convolutional network`'s seven connectivity patterns; `Recurrent
network`'s cell forms; `Transformer`'s three block structures; `Graph neural
network`'s aggregation forms; `Normalizing flow`; `Energy-based network`;
`Knowledge-graph embedding`; `Variational autoencoder`.

**No sibling anywhere exists because it was large in this corpus.** The one
structural element added after the corpus was read is the `Neural operator`
root, and it was added because the corpus proved a family existed that the draft
could not hold — not because it was big (it is small). The reverse check also
passes: eleven subtrees with zero corpus support were kept, not pruned.

**No residual nodes.** No `Other`, no `Misc`, no era-based node (`classic_ml`),
no size-based node (`Large models`). Those are the four defects B.5 records for
v0's root set, and none is present.

---

## 2. Sibling sets I am NOT confident in

Listed worst first. Each is a place where I would expect a second designer to
disagree with me.

1. **`Feedforward network`'s division children** (`Implicit neural
   representation`, `Permutation-invariant set network`). The principle — "the
   input domain the stack is specialized to, and the invariance it is given" —
   was written *after* I had the two children, which is the failure mode
   PROCESS §1 step 2 exists to prevent. The principle also skates close to
   "data structure consumed", a rejected characteristic. I kept it because both
   children are field-named and useful, but this set is the weakest in the file.

2. **`Autoencoder`'s children.** Two of the four (`Denoising`, `Masked`) are
   defined by a training objective, not by a constraint on the code's
   *structure*, so the stated principle only half holds (B-10). Under the
   brief's SimCLR fixed point both could be algorithms, which would leave the
   root with two children and make it a near-rename of `Variational
   autoencoder`.

3. **`Generative adversarial network` as a root** (B-11). I admitted it by
   symmetry with `Autoencoder`; the diffusion fixed point argues the other way.
   If the owner rules it an algorithm, 25-plus corpus names move under
   `Convolutional network` and a whole level-1 bucket disappears. I would not
   be surprised to be overruled here, and the repair is mechanical.

4. **`Factorization model`'s children.** Six children whose shared principle
   ("what the latent factors reconstruct") is real but loose — a matrix, a
   tensor, a triple, a co-occurrence table, a feature interaction, a pair of
   views are not values of one variable so much as a list. `Word embedding
   model` is additionally a declared R1 violation (B-12) and has zero corpus
   support. If this root is ever trimmed, trim it here.

5. **`Spiking neural network`'s two children.** Divided by neuron model, which
   I believe is right, but I have low confidence that `Integrate-and-fire` and
   `Conductance-based` are the two the field would choose, and the whole root
   has zero corpus support.

6. **`Directed graphical model`'s children.** Seven children, of which two
   (`Hidden Markov model`, `Linear dynamical system`) arrive as second parents
   from the state-space root and one (`Bayesian neural network`) as a second
   parent from the feedforward root. The division subset is coherent; the node
   as a whole reads as a crossroads rather than a family.

7. **`Decoder-only Transformer`'s children.** Eleven open and proprietary LLM
   families as a flat descent set. It is correct under R1 and R7 — but see §3.

8. **`Slot attention`'s placement** (B-19), the single least settled node.

9. **`Convolutional network` at 18 children**. The division subset is 7 and
   shares one principle, so the set is legal; but a reader scanning the file
   will see a wide node, and the detectors in particular (`R-CNN`, `YOLO`,
   `SSD`, `RetinaNet`) sit there because they have nowhere better to be, not
   because "connectivity pattern of the conv stack" describes them.

---

## 3. Families that WILL need a deeper design pass (R7)

R7 forbids the second pass from creating grouping nodes, so each family below
will stay flat unless a design pass opens it. Listed with the division
principle I would propose, so the later pass starts from a position rather than
a blank page.

| family | why it needs one | candidate principle |
|---|---|---|
| **`BERT`** (the brief's named case; ~30 corpus names) | its variants differ along *several* aspects at once — pretraining corpus (BioBERT, SciBERT, CodeBERT, MatBERT, ProtBERT, AfriBERTa), compression (DistilBERT, TinyBERT, ALBERT), language coverage (mBERT, XLM-R), and objective (RoBERTa, ELECTRA, DeBERTa). A flat set makes "what kind of BERT variant" unanswerable | *which aspect of BERT's recipe the variant changes*; note that a variant may take two values, which multi-parent already permits |
| **`Decoder-only Transformer`** (~43 GPT names, ~26 LLaMA names, plus 8 other families) | eleven flat families today and growing monthly; the second pass will want to group them and R7 forbids it | **not** by size and **not** by openness. The only defensible candidate I see is *positional and attention-block configuration* (absolute vs rotary vs ALiBi; dense vs sparse feedforward). If no such principle survives review, the honest answer is that this set is flat by nature |
| **`Vision Transformer`** (~25 corpus names) | nine children already, mixing hierarchical variants (Swin), training variants (DeiT, BEiT, MAE) and composites (CLIP, BLIP, LLaVA, SAM) | *whether the variant changes the patch/scale structure, the pretraining objective, or composes ViT with another encoder* |
| **`Residual network`** | the widest R3 size-variant family in the corpus (ResNet-18/20/34/50/101/152, plus ResNeXt/WRN/SE) | no grouping node — size must never divide a sibling set. Named here so the later pass does **not** invent one |
| **`U-Net`** | nnU-Net, 3D U-Net, UNet++, Attention U-Net, MedSAM-adjacent variants | *which part of the U-shape the variant modifies: the skip path, the dimensionality, or the block type* |
| **`LLaMA`** | wide, but almost entirely R3 size and chat variants | **no grouping needed** — recorded so a later pass does not create one by analogy with BERT. This is the R7 distinction made concrete |
| **`YOLO`** | generation chain v1–v8+ | none needed; pure descent |

---

## 4. Cross-cutting properties that are deliberately NOT nodes

Each would have been a tempting grouping node and each would have put a second
principle into a sibling set. Each is instead a candidate **attribute** on the
node or the mention, and the owner should decide whether the schema grows a
slot for them:

- **sub-quadratic / sparse attention** (Longformer, BigBird, Performer,
  Linformer, Reformer) — cuts across all three Transformer block structures
- **mixture-of-experts routing** (Switch, Mixtral, GShard) — same
- **equivariance to a symmetry group** — appears on GNNs, Transformers and MLPs
  in this corpus alike
- **Bayesian treatment of weights** — in principle applies to any lineage;
  currently a single node under the feedforward root (A8), which is a
  compromise, not a conviction
- **distillation / compression** — a relation between two releases, not a class
- **instruction tuning / chat alignment** — a training stage; the releases are
  R3 nodes under their base model
- **parameter-efficient adaptation** (LoRA, adapters, prefix tuning) — B-15,
  algorithm-side

---

## 5. Known rule violations in this output

Stated plainly rather than buried:

1. **B-12 is an R1 violation**: `word2vec` is placed by its learned object, not
   by its paper's framing.
2. **B-09 contradicts the brief's worked table** on ViT's depth (one level
   deeper).
3. **17 roots** exceed the 8–15 smell test.
4. **`SPELLINGS.tsv` uses a case value (`synonym`) the spec does not define**
   (B-26), and uses `plural` where the spec says `size`.
5. `Mixture-of-experts network` under `Feedforward network` (B-18) is a
   placement of convenience: the 1991 gated-experts architecture is genuinely a
   feedforward object, but most corpus mentions of "MoE" mean a routing layer
   inside a Transformer, and those mentions will land in the wrong root.

## 6. What I would want measured before this is adopted

- The **share of corpus mentions that leave this hierarchy entirely** under
  B-24 (GFlowNet) and B-14 (diffusion). My estimate from name counts is large
  enough that the owner should see the number before the rules are frozen.
- The **`Other` rate at a cut placed at depth 1**, which is the measure that
  condemned v0's cut file (8 of 25 categories named). This design is only
  worth its complexity if that rate is low at several depths, not just one.
- Whether `Encoder-only` / `Decoder-only` / `Encoder-decoder` actually
  **splits the corpus three ways**, or whether it is 95% decoder-only by
  mention — in which case the level is correct but not useful, and the useful
  level is the family one below it.
