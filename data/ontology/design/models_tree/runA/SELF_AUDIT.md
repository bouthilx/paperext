# Self-audit — models hierarchy, run A

The granularity audit of `PROCESS.md` §3, run on my own output. Three questions
per sibling set:

1. Are these the same **kind** of thing?
2. Are they at the same level of **specificity**?
3. **Does any sibling exist only because it was large in this corpus?**

52 sibling sets have two or more members; all 52 were checked. Question 3 is
answered globally in §3, questions 1 and 2 set by set, and only the failures are
written up — a clean set is not interesting.

The section the brief asks for most loudly is §2: **the sets I am not confident
in.** It is ordered worst first.

---

## 1. The audit in one table

| | sets | verdict |
|---|---|---|
| clean on all three questions | 44 | not discussed below |
| **mixed kind** (question 1 fails) | 6 | §2.1–§2.6 |
| **mixed specificity** (question 2 fails) | 4 | §2.2, §2.3, §2.7, §2.8 (two also fail question 1, so 8 distinct sets fail) |
| corpus-shaped (question 3 fails) | 0 | §3 |

## 2. Sibling sets I am **not** confident in

### 2.1 `Convolutional network`, 30 children — the least defensible set in the tree
They are not the same kind of thing. The set mixes classification backbones
(VGG, ResNet, DenseNet), detection systems (R-CNN, YOLO, SSD, RetinaNet),
components that are sometimes run alone (FPN), sequence models (TCN, WaveNet),
video models (I3D, SlowFast), an equivariance generalisation (G-CNN) and six
hybrids that arrive from other roots (Conformer, wav2vec 2.0, DETR, ConvLSTM,
DCGAN, spiking CNN). One grouping node (`Encoder-decoder convnet`) sits among
them, which is legal under R4 but makes the set hard to read.

I could not find a division that survives R4. The field's names for CNN
sub-kinds (*residual networks*, *inception-style*, *depthwise-separable*)
coincide with their founding artifact, so a grouping node would be a rename of
its own first child; the alternatives are task (rejected: "function learned") or
kernel rank (rejected: "data structure consumed", B18). **This is the family
most likely to be wrong, and the one where I would most welcome being
overruled.** Flagged for a design pass in §4.

### 2.2 `Recurrent network`, 9 children — mixed kind *and* mixed specificity
`LSTM` and `GRU` are recurrent *cells*; `Seq2seq`, `Neural Turing Machine`,
`Memory network` and `RSSM` are *systems built from* cells. Putting a cell and a
system in one sibling set is precisely the defect the audit hunts. The honest
repair is a level the field does name (*recurrent unit* vs *recurrent
architecture*), but I could not satisfy R4(3) for it — "a recurrent unit" is not
definable without pointing at its members — so I left the defect in place rather
than invent a level. Declared, not fixed.

### 2.3 `Linear model`, 9 children — mixed kind
Supervised predictors (linear regression, logistic regression, GLM, Cox),
unsupervised projections (PCA, CCA), a discriminant (LDA), a time-series model
(ARIMA) and a learning rule (Perceptron) are not one kind at one specificity.
They share only "the learned object is an affine map", which is the root's
`positive_test` and not much else. Four of these arrived in phase 2 (B10), and
the underlying problem is that **R1's framing test cannot place classical
statistics at all**: there is no introducing paper that defines PCA relative to
the linear model. I placed them by kind and said so.

### 2.4 `Embedding model`, 5 children — the division I trust least
Its principle, *what discrete entity the table indexes*, is uncomfortably close
to the rejected level-1 characteristic "data structure consumed". It also
produces a mixed set: three grouping nodes (word / node / KG embedding) beside
two descent children (matrix factorization, factorization machine), which belong
to the same kind but did not fit the division. And the root itself is the only
one I **constructed** rather than found — no paper founds "embedding models".
An alternative division by *scoring function* (dot product / translation /
bilinear) is more structural but splits word2vec from GloVe, which no reader
would accept.

### 2.5 `Feedforward network (MLP)`, 5 children — mixed kind
`MLP-Mixer` is an artifact, `Deep Sets` an architecture class, `Coordinate MLP`
a grouping node, `DeepFM` a hybrid arriving from another root, and
`Bayesian neural network` is not an architecture at all but a *parameterisation*
(B09). Five children, four kinds. Of these, the Bayesian NN edge is the one I
would drop first if forced.

### 2.6 `Autoencoder`, 6 children, and the root itself
The root is defined partly by what it learns (reconstruction), which is the
rejected "function learned" characteristic. I kept it because the
encoder–bottleneck–decoder *shape* is structural and because it earns its keep
in the composite diffusion systems. But if the owner rejects it, VAE moves under
`Directed graphical model` and MAE under ViT alone, and little else changes —
so this root is cheap to overrule, which is a point in favour of flagging it
loudly now.

### 2.7 `BERT`, 16 children — mixed specificity, and it will get worse
RoBERTa (a full retraining recipe), DistilBERT (a compression), CodeBERT (a
corpus change) and BEiT (a hybrid arriving from ViT) are not at one level of
specificity. The division that would fix it does not partition (B17), so the set
stays flat and is the brief's named candidate for a deeper pass.

### 2.8 `Decoder-only Transformer`, 19 children — wide but, I think, sound
Nineteen is uncomfortable, and I checked it hardest for question 3. The members
are all *founding family nodes* of their own lineages at one level of
specificity, and the alternative groupings are licensing (not architecture) or
vendor (not architecture). I am reporting the width rather than fixing it,
because every fix I could construct divides by something that is not a property
of the model. If the owner wants a level here, the only candidate I can defend
is *positional-encoding scheme* (absolute / rotary / ALiBi / none), which the
corpus itself names — and which I did **not** adopt, because it is a layer
property (§3 of the brief) and because it would reshuffle families.

## 3. Question 3: does any sibling exist only because it was large in this corpus?

**No, and this is the one claim in the audit I can make structurally rather than
by assertion.** Every node and every edge in `nodes.tsv` except eighteen was
written before `model_names.tsv` was opened — the timestamp on
`DRAFT_PHASE1.md`'s first line and the frozen draft make that checkable. Of the
eighteen phase-2 additions (`RATIONALE.md` §7), none created or changed a
sibling *set*: fifteen are leaves under an existing parent, and three are roots
with no siblings to balance against.

The inverse check — *did corpus size stop me from opening a node?* — is the
dangerous one, since PROCESS §2 rule 4 says volume may decide which node to open
next. I opened nodes by what I knew of the field, which is why the vision branch
is thinner below depth 3 than the language branch (`DRAFT_PHASE1.md` §5.5). That
is a recall bias, not a volume bias, and it is not repaired by this run.

The strongest evidence the corpus did not arbitrate: the whole
`Word embedding model` subtree has **zero** corpus support and was kept, while
`Rule-based model`, the root I had predicted would be deleted, turned out to be
attested. A corpus-led pass would have got both backwards.

## 4. Families that need a deeper design pass (R7)

R7 means **a family I leave flat stays flat**: the second pass may attach
children by descent but may not create a grouping node. So this list is a
commitment, not a caveat. Ordered by expected damage.

1. **`BERT` (16 children now, will be much wider).** The brief's named case. The
   pass must decide whether "same architecture, new corpus" is a value of a
   division, and B17 records why the obvious four-value division does not
   partition. The corpus shows the domain-variant pattern is larger and
   differently populated than my draft's instances (`RATIONALE.md` §8.1).
2. **`Convolutional network` (30).** §2.1. The widest set in the tree and the
   one with the weakest internal principle.
3. **`Flow network (GFlowNet)` (0 children now).** Added in phase 2 as a root
   with no designed members, while the corpus carries a large and structured
   variant cluster (conditional, continuous, dynamic, forward-looking,
   expected-flow, augmented, sampler-based). If this root is left as it is, the
   second pass will hang the entire cluster flat off the root — v0's failure
   mode, reproduced in the one family this institute contributes most to. **This
   is the highest-value follow-up after BERT.**
4. **`Decoder-only Transformer` (19).** §2.8. A pass should either confirm the
   flat set or rule on the positional-encoding candidate.
5. **`Recurrent network` (9).** §2.2 — the unit-vs-system level.
6. **`Graph neural network` (9).** The spectral/spatial division was considered
   and refused on GCN's bridge status (B16); a pass with more care may find a
   division I could not.
7. **`Linear model` (9) and the classical branch generally.** §2.3 — and more
   deeply, a ruling on whether R1 applies at all to pre-paper-culture
   statistics (B10).
8. **`ResNet` / `ViT` / `LLaMA` / `GPT` (5–10 each).** Not urgent. Each will
   collect size variants and fine-tunes from the second pass, which R3 and R7
   both permit without a design pass.

## 5. Repairs I made to my own draft during this audit

- **RWKV** was a direct child of `transformer`, sitting beside the three
  division nodes and breaking their totality — the v0 shape in miniature. Moved
  to `Decoder-only Transformer` (plus its RNN parent). Internal consistency
  repair, not a corpus-driven change.
- **`relation = root`** was added after noticing that labelling a root
  `division` asserts a rule it was not placed by (`RATIONALE.md` §2).
- **`Domain-adapted BERT`** was drafted during phase 2 and removed before
  publication; see `RATIONALE.md` §8.1 for why keeping it would have been the
  corpus arbitrating structure.

## 6. What would falsify this derivation fastest

In the order I would run them:

1. **Place 100 names from the singleton tail using only the written tests**, as
   the domains design did (`TAIL_VALIDATION.md`). The output that matters is not
   placements but a strain list. My prediction: the strain concentrates on
   (a) names that are algorithms under the admission rule, (b) out-of-type terms
   (`RATIONALE.md` §8.5), and (c) classical statistics, where R1 does not apply.
2. **Check the R1 framings I asserted from memory.** Roughly 250 edges rest on
   "the introducing paper defines A relative to B", and I checked none of them
   against a paper in this run. The ones I would verify first because the whole
   root set turns on them: Transformer-vs-RNN, GNN-vs-CNN, 3DGS-vs-NeRF,
   DenseNet-vs-ResNet, Neural ODE-vs-ResNet, EfficientNet-vs-MobileNet.
3. **Count what the admission rule removes** before anyone reads it as a drop in
   coverage (`RATIONALE.md` §8.5).
4. **Then** the step the brief already schedules: diff against the domains
   `Method > Model design` subtree, which I have not seen.

## 7. Confidence, stated plainly

| part | confidence |
|---|---|
| the lineage backbone, and that contrast is not descent | high |
| the Transformer division and its three values | high |
| Decision tree / PGM / Kernel machine / SSM branches | high |
| the root set being *roughly* right in kind | medium-high |
| the root set being right at **20**, against R6's 8–15 | medium — argued in `RATIONALE.md` §5, not defended |
| CNN's internal structure | **low** |
| RNN's internal structure | **low** |
| `Embedding model` as a root and its division | **low** |
| `Autoencoder` as a root | medium-low |
| `Bayesian neural network`'s parent | **low** |
| `Slot attention` and `3D Gaussian splatting` as roots | medium-low — single-member roots, declared |
| that no sibling set is corpus-shaped | high — structurally checkable, §3 |
