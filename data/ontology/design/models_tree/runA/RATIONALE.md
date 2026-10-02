# Models hierarchy — rationale (run A)

Companion to `nodes.tsv`. Three things live here, as the brief's section 7.4
asks: the principle of division at every branch, every phase-1 → phase-2 change
with its reason, and the declared boundary cases (which are in
`BOUNDARY_CASES.tsv`, in the shape the domains design used).

Files, in the order they were written and frozen:
`DRAFT_PHASE1.md` (corpus-free, timestamped first line) → then and only then
`model_names.tsv` was opened → `nodes.tsv`, `SPELLINGS.tsv`,
`BOUNDARY_CASES.tsv`, this file, `SELF_AUDIT.md`.

---

## 1. Shape of the result

| | |
|---|---|
| nodes | 284 |
| roots (R6) | 20 — 17 from phase 1, 3 added in phase 2 |
| R4 grouping nodes | 12 |
| R1 descent nodes | 252 |
| nodes with more than one parent (R5) | 26 |
| maximum depth (shortest path to a root) | 4 |
| depth histogram | 0:20, 1:99, 2:98, 3:61, 4:6 |
| leaves | 204 |
| widest sibling sets | CNN (30), Decoder-only Transformer (19), BERT (16), ViT (10) |

Size variants are deliberately absent: they are nodes under R3 but the second
pass creates them (R7 permits descent attachment), and designing them here would
have doubled the file without adding a level.

## 2. How the columns are used

- **`parents`** — pipe-separated; empty for a root.
- **`depth`** — shortest path to a root, so a composite like `Stable Diffusion`
  takes the depth of its shallowest part.
- **`relation`** — `root` (placed by R6), `descent` (R1) or `division` (R4).
  The brief lists only `descent` and `division`; a root is placed by neither
  rule, and labelling it `division` would have been false. This is the one
  column-vocabulary addition, and it is visible rather than silent.
- **`characteristic`** — **the principle that divides this node's children**.
  PROCESS §2 rule 1 attaches a principle to a *sibling set*, and R6 says the
  machinery applies only where a set is produced by division. So a node whose
  children are lineage descendants carries `(descent — …)` and a leaf carries
  `(leaf)`. What the node *itself* is lives in `positive_test` /
  `negative_test`, which is where a placement decision actually gets made.
- **`examples`** — member spellings or close relatives. **No counts anywhere**,
  per the brief's section 7.2.

## 3. The principle of division at every branch

Only twelve sibling sets in this tree are produced by division; everything else
is descent, and descent sets have no principle by construction. Each of the
twelve is justified against R4's three tests in `DRAFT_PHASE1.md` §3, and the
principle is stated on the parent node in `nodes.tsv`.

| parent | principle of division | values |
|---|---|---|
| Tree ensemble | how the member trees enter the prediction | bagged (averaged over independent trees) / boosted (summed over sequentially fitted trees) |
| MLP | what the MLP's input is | the `Coordinate MLP` value only; its siblings are descent |
| CNN | the spatial-resolution path | the `Encoder-decoder convnet` value only; its siblings are descent |
| Transformer | which of the original two stacks is retained, hence the attention mask | encoder-only / decoder-only / encoder-decoder |
| Probabilistic graphical model | the edge semantics of the factorization | directed conditional factors / undirected potentials |
| Embedding model | what discrete entity the vector table indexes | word type / graph node / KG entity-relation |

Two of those parents (MLP, CNN) have a *mixed* sibling set: one grouping node
beside many descent children. That is legal under R4, which admits a node
"between P and its children", not necessarily between P and *all* of them. It is
also the hardest part of this tree to audit, and it is declared in
`SELF_AUDIT.md`.

Seven divisions were considered and refused; they are in `DRAFT_PHASE1.md` §3.1
and `BOUNDARY_CASES.tsv` rows B16–B18 and B30. The refusals matter more than the
admissions, because R7 means a refusal is permanent until a design pass revisits
it.

## 4. The four readings that shaped everything

Stated in full in `DRAFT_PHASE1.md` §0 and repeated here because every reviewer
will want them in one place:

**(a) `characteristic` divides the children** — see §2 above.

**(b) Lineage is not subsumption, and lineage wins.** GLM is a *child* of the
linear model although it contains it in extension, because it was derived by
generalising it. Same for `Tree ensemble` under `Decision tree` and for `MPNN`
over GCN/GAT. Consequence: **this tree is not an is-a taxonomy**, and a reader
who treats it as one will misread half a dozen edges. (B11)

**(c) Series-flattening.** GPT-2/3/4, Llama 2/3, Fast/Faster/Mask R-CNN,
StyleGAN2/3 attach to the founding node of the series, with the predecessor in
`notes`. A strict R1 chain is truer to each paper but costs two levels of depth
in the biggest families; the brief's own §3 diagram flattens this way. (B02)

**(d) Contrast is not descent.** A paper that names an architecture in order to
*replace* it gets no edge to it. This single reading makes the Transformer a
root rather than an RNN descendant, DenseNet a child of CNN rather than of
ResNet, YOLO a child of CNN rather than of R-CNN, and 3D Gaussian splatting a
root rather than a NeRF descendant. It is the highest-leverage reading in the
derivation. (B13)

## 5. Roots

20 roots, against R6's smell test of 8–15. R6 forbids merging or splitting a
root to hit the number, so none was. The honest diagnosis:

- **Not caused by promoted releases.** R6's stated failure mode is releases
  promoted to roots because their lineage was not traced. One root is a single
  artifact (`3D Gaussian splatting`) and one has a single real member
  (`Slot attention`); the other eighteen are founding architectures with
  families.
- **Caused by scope.** Six roots are non-neural (`Linear model`,
  `Kernel machine`, `Decision tree`, `Probabilistic graphical model`,
  `Embedding model`, `Rule-based model`). A tree covering only deep learning
  would sit at 12–14 and inside the bound.
- **The lever, if the owner wants ≤15, is scope, not merging.** The obvious
  merge — one umbrella over the non-neural roots — is exactly v0's defect
  (`classic_ml` divides by *era*, not by any property of a model). Declining a
  cheap number is the point of R6's last sentence.
- **Roots do not partition anything** and are not meant to: `Decision tree`
  overlaps `Rule-based model`, `Linear model` overlaps `Kernel machine` at the
  linear SVM, `PGM` overlaps `SSM` at the HMM. Counting is non-exclusive (E1
  #16), so overlap costs nothing.

## 6. Two departures from the brief's column spec

1. **`relation = root`.** See §2.
2. **`SPELLINGS.case`.** The brief's §7.3 gives the cases as
   `orthographic | acronym | size`, but R3's own three cases are orthographic,
   acronym and **pluralisation**, and R3 states that size variants are *nodes*.
   `size` is therefore used nowhere, `plural` is used in its place, and
   **`synonym` is added** for a different string denoting the same thing with no
   shared morphology (`convnet` = `convolutional neural network`, `feedforward
   network` = `multilayer perceptron`, `gradient boosted trees` = `GBDT`). R3's
   three cases cannot express a synonym, and the corpus is full of them: 34 of
   204 spelling rows. If the owner refuses the extension, those 34 become nodes,
   producing ~34 duplicate-release nodes — which is v0's duplicate-cluster
   defect reintroduced by rule.

---

## 7. Phase 1 → phase 2: every change, with its reason

**No node was moved. No node was deleted. No division principle changed. No
root was merged or split.** 18 nodes were added, all under the brief's first
phase-2 question (blind spots that must be added), and 3 of them are roots
because R6 applied to them admits no parent. Everything else the corpus made me
want to do is in §8 as a finding.

The test used for "blind spot": *is there any node under which the second pass
could attach this cluster by descent (R1)?* If yes, it is not a blind spot — R7
lets the second pass attach it, and adding an anchor myself would be the corpus
shaping the tree. Five candidate additions failed that test and were refused
(§8.4).

| # | added | parent(s) | why it is a blind spot |
|---|---|---|---|
| 1 | **Flow network (GFlowNet)** | **root** | The largest miss in the draft: a very large name cluster (`gflownet`, `generative flow network`, and dozens of variants) with nothing in the tree it could descend from. Not a normalizing flow — not invertible, not a density map — and not an RL algorithm. R6 then makes it a root. **This is a failure of my own recall, not of the field**: GFlowNets are a flagship line of the institute this corpus comes from, and a corpus-free phase 1 is exactly where that bias shows. |
| 2 | **Neural operator** | **root** | A function-space-to-function-space learner; no ancestor in the tree. The graph-neural-operator framing would argue for a GNN parent, but FNO's own framing is operator-first. |
| 3 | Fourier neural operator | neural_operator | the named member that the corpus actually carries |
| 4 | **Slot attention** | **root** | An object-centric cluster with no home: slots competing through an attention softmax normalised over slots, refined recurrently. Fits none of the three Transformer stack divisions. See B20 — the Transformer-parent reading was rejected, not overlooked. |
| 5 | Neural process | deep_sets \| gaussian_process | A family with no home: the permutation-invariant context encoder is a DeepSets inheritance (R1), the GP edge records what it amortises (B19). |
| 6 | Transformer neural process | neural_process \| encoder_only_transformer | the attention-aggregator member, attested |
| 7 | Bayesian neural network | mlp | No home: a parameterisation in which weights are random variables, which changes what `parameter_count` means — a model-side field. Weakest of the additions (B09). |
| 8 | PCA | linear_model | A projection/decomposition cluster with no home. R1's framing test cannot place pre-1990 statistics at all (B10), so these are placed by kind. |
| 9 | Canonical correlation analysis | linear_model | same |
| 10 | Linear discriminant analysis | linear_model | same; also forces the `lda` acronym collision into the open (B22) |
| 11 | Cox proportional hazards model | linear_model | same, applied-statistics cluster |
| 12 | Bayesian hierarchical model | directed_gm | same; it is the directed-GM root earning its keep |
| 13 | Time-delay neural network | cnn | The speech cluster's ancestor: ECAPA-TDNN and x-vector models name TDNN, not CNN, so without this node they cannot attach by framing. |
| 14 | AlphaFold | encoder_only_transformer | A composite whose structure module is equivariant rather than a plain encoder stack; no existing node covers it. |
| 15 | ChatGPT | gpt | Not a blind spot but an **R3 spelling-vs-node decision**, which is a design question the second pass may not make: is `chatgpt` a spelling of GPT-3.5/GPT-4 or a node? Answered: a node, because the served release changes over time (B23). |
| 16 | Codex | gpt | same decision, and the parent of the Copilot product name |
| 17 | Imagen | unet \| t5 | A second and third template for the composite reading of diffusion systems, which is the most counter-intuitive consequence of the admission rule (B03). One template (Stable Diffusion) was too thin to generalise from. |
| 18 | DALL-E 2 | clip \| unet | same |

### 7.1 Speculative flags (phase-2 question two)

PROCESS §2 rule 1 is explicit: *a category with no corpus support is possibly
speculative — justify or keep; it never auto-deletes.* **Nothing was deleted.**
The flag is recorded in each node's `notes` as `Possibly speculative: no corpus
support (phase 2)`, so it is reviewable per node. 64 nodes carry it. The blocks
worth naming:

- **The whole `Word embedding model` subtree** (word2vec, CBOW, skip-gram,
  GloVe, fastText) — zero support. Kept: the field is real and a one-year
  snapshot post-dates it. Its sibling `Node embedding model` survives only
  through `graph2vec`/`gl2vec`/`dyg2vec`-style names, and `KG embedding` is well
  attested. This is the clearest case of the rule earning its keep: a corpus-led
  pass would have deleted word embeddings outright.
- **Pre-2015 neural relics** — RBM, DBN, DBM, capsule networks, PixelCNN,
  PixelRNN, WaveNet, SegNet, NTM, Modern Hopfield, MRF, GMM, Kalman/LDS. All
  kept. Several survive indirectly (`dnc`, `memory networks`, `echo-state
  network`, `boltzmann machine` are present).
- **Very recent families** — Mamba, sparse autoencoders, RWKV, 3D Gaussian
  splatting. Absent because the snapshot predates their uptake, not because they
  are wrong.
- **`Rule-based model`, the root I flagged in phase 1 as my most speculative,
  is attested** — CORELS and FairCORELS are decision-list learners in the
  corpus. The prediction was wrong in the useful direction.
- **BERT domain variants** — BioBERT/SciBERT/ClinicalBERT carry no support under
  those exact names, while the *pattern* is large and differently populated
  (PubMedBERT, AfriBERTa, BERTweet-shaped names, BERTOverflow, GraphCodeBERT).
  Kept as named instances; see §8.1 for the restructure this tempted and the
  reason it was refused.

## 8. Findings: what the corpus made me want to do, and did not do

The brief's instruction is explicit — *if the corpus makes you want to
restructure something, that is the signal to write it down as a finding, not to
restructure.* Five of these.

### 8.1 A `Domain-adapted BERT` grouping node — refused
The corpus shows the domain-variant pattern under BERT is large and populated by
different instances than the textbook list. I drafted a single
`Domain-adapted BERT` node to absorb them, then removed it. Two reasons: it is a
grouping node created in phase 2 *because of corpus evidence*, which is the
corpus arbitrating structure; and it contradicts my own phase-1 finding that the
BERT variant dimensions do not partition (B17). The finding stands on its own:
**BERT will be wider than the draft shows, and the deeper design pass should
treat "same architecture, new corpus" as its first candidate value.**

### 8.2 Returning an `Energy-based model` root — refused
Phase 1 dropped that root on principle (energy is a cross-cutting property;
Hopfield and Boltzmann machines are undirected graphical models). The corpus
carries the bare term in several papers. Restoring the root on that evidence
would be the corpus arbitrating a structural choice. The consequence is real and
is recorded in B05: those mentions resolve to nothing.

### 8.3 A `Diffusion model` node — refused
Diffusion-shaped strings are one of the two largest clusters in this corpus.
The admission rule and the brief's own table route the bare term to algorithms
and make the denoiser the model (B03). I added two more composite templates
(Imagen, DALL-E 2) so the second pass is not generalising from one example, but
no node for the procedure. **If the owner wants a "proportion of papers using
diffusion" cut, it has to come from the algorithms hierarchy, and that is a
reason to prioritise it.**

### 8.4 Five anchors refused as *placeable, not blind*
Translation encoder-decoders (NLLB, M2M-100), vision-language encoders (ViLBERT,
UNITER, ALBEF, FLAVA), code decoders (StarCoder, CodeGen), temporal graph
networks (TGN, DyRep, CAW), and Hyena. Each has a node it can descend from under
R1, so R7 lets the second pass attach it. Adding anchors would have been the
corpus deciding which branches get resolution — exactly "volume shaping how a
node opens", which PROCESS §2 rule 4 forbids.

### 8.5 Three findings about the *corpus*, not the tree
- **`models[]` holds out-of-type terms** in three distinguishable classes:
  libraries and tools (`pytorch`, `gurobi`, `core ml`, `google translate`),
  mechanistic or domain models (epidemiological compartmental models, cold dark
  matter, mouse models), and metrics or procedures (FID, Elo, t-SNE,
  backpropagation, Gibbs sampling). They must be reported and excluded
  **separately from** the class generics, because they are not uninformative
  model names — they are names for things that are not models (B24).
- **The entity-type split will move a large block of names out of this
  dimension**: self-supervised objectives (SimCLR, BYOL, Barlow Twins, VICReg,
  DINO, MoCo, SwAV), RL update rules (PPO, DQN, SAC, MuZero, Rainbow, IMPALA,
  TD3, CQL), federated aggregation (FedAvg and relatives), optimisers and
  adaptation methods (Adam, LoRA, MAML). This is the intended effect of settling
  entity types first (MODELS_BRIEF B.1), but it should be measured before anyone
  reads a drop in model coverage as a regression.
- **Acronym collisions are real and not rare**: `lda`, `dino`, `sam`, `complex`,
  `ar`, `art`, `ego`, `clean`, `goat`. None may be auto-collapsed (B22).

## 9. Quarantine

Unchanged from phase 1 and listed in `DRAFT_PHASE1.md` §4.1: class generics
(`neural network`, `deep learning model`, `large language model`, `foundation
model`, `generative model`) and role words (`encoder`, `backbone`, `policy
network`, `teacher model`, `baseline`). Reported as a line and excluded from
family shares, as `machine learning` was in the domains design. Phase 2 adds the
three out-of-type classes of §8.5 as separate quarantine reports, and extraction
noise (`-model`, `base model`, `fused`, `clean`) as a fourth.

One contested row: `transformers` as a plural string. R3 case 3 makes a
pluralisation a spelling, while the brief's §4.7 note lists "`transformers` as a
plural mass noun" among the quarantined generics. Resolved as a **spelling of
`Transformer`**: the architecture is unambiguously named, and quarantining it
would discard the corpus's third most frequent architecture term. The generic
quarantine keeps `neural networks`, which names no architecture.

---

## 10. Input disclosure

Opened in this run: `MODELS_DERIVATION_BRIEF.md`, `MODELS_BRIEF.md`,
`PROCESS.md` (before phase 1); `model_names.tsv` (after `DRAFT_PHASE1.md` was
complete and timestamped). External knowledge: my own recall of the ML
literature, with ACM CCS `Computing methodologies`, arXiv categories and Papers
With Code used from memory for breadth and vocabulary only — none of them
arbitrated anything.

None of the forbidden inputs was opened: `data/ontology/models/` (any version),
`data/ontology/design/axes/`, `design/run1|run2|run3/`, any
`proposed_categories.csv` or `categorized_models.json`,
`data/ontology/datasets/`, `data/ontology/domains/`.

One disclosure for completeness: the brief asks `BOUNDARY_CASES.tsv` to have
"the same shape as `BOUNDARY_CASES.tsv`", so the **first 14 lines** of the
domains file at `design/BOUNDARY_CASES.tsv` were read, after phase 1 was frozen
and after the node set was drafted, to copy its column convention. Those lines
contain rows from the *application* side of the domains design (discipline vs
sector); nothing from `Method > Model design`, which is the subtree step B.6
will compare this derivation against. No structural choice here was taken after
or because of that read.
