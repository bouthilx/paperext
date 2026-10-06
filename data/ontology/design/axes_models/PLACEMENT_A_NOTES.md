# PLACEMENT_A — notes

Companion to `PLACEMENT_A.tsv`. 130 names from `WORKLIST_A.tsv` placed against
the axis set of `MODELS_AXES.md` on 2026-10-06. Classification only: no node was
created, no axis value invented, no existing row edited.

| verdict | n |
|---|---|
| algorithm | 59 |
| lineage | 40 |
| alias | 11 |
| unsure | 10 |
| generic | 6 |
| misextraction | 3 |
| quarantine | 1 |

Confidence: 60 high, 56 medium, 14 low.

---

## 1. Names that need an axis value which does not exist

Each of these is a name I could otherwise place; the pin it wants has nowhere to
go. None of them was forced into an approximate value — the cell is left empty,
following L-17's precedent.

1. **Hypernetwork** — `ghn-3`. A model whose *output is another model's
   parameters*. No connectivity value describes weight generation, and topology
   cannot say "two models, one of which emits the other". GHN-3 currently
   resolves as a plain GNN, which loses the entire point of it. This is the
   clearest missing concept in the batch.

2. **Weight tying between towers** — `siamese network`, and `protst` behind it.
   `Multi-tower / dual encoder` says the towers are parallel and joined at the
   end; it does not say whether they share weights. CLIP (untied) and a Siamese
   network (tied) therefore resolve identically, and *tied* is the only thing the
   word "Siamese" asserts. Candidate: a `Parameter sharing` attribute family
   (`untied` default / `tied towers`).

3. **Conditioning / feature modulation** — `film`. FiLM is a layer that lets one
   stream modulate another's activations. L-06 ruled conditioning schemes out of
   lineage but named no home for them, and no axis has a value for it. The same
   gap swallows the "+ conditioning" half of CVAE-shaped designs.

4. **Continuous-time / learned-ODE dynamics** — `goku-ui`, and the existing
   `Neural ODE` subtree. Connectivity has no value for "the layer is the solution
   of a learned ODE"; see §3.1 for what that costs today.

5. **Predictive-distribution output head** — `lag-llama`,
   `multi-headed bayesian deep learning probabilistic model`, and the
   `species distribution models` cluster. `Weight treatment` is about
   *parameters*, and its negative test explicitly excludes "uncertainty
   represented only in the output layer". So a model that outputs a distribution
   rather than a point — which is most of probabilistic forecasting — asserts
   nothing on any axis. Given how much of this corpus is uncertainty work, this
   looks like a real hole rather than a deliberate exclusion.

6. **Multi-head outputs** — `multi-headed bayesian deep learning probabilistic
   model`. One trunk, several heads. Not `Ensemble` (jointly trained, one
   forward pass), not `Multi-tower` (one input, not several).

7. **Temporal / dynamic graphs** — `dyg2vec`, `dyrep`. A continuous-time dynamic
   graph net is neither plain message passing nor plain recurrence; the pair of
   values approximates it but says nothing about the graph changing over time.
   This is a growing corpus cluster (the `dyrep` quote alone lists eight such
   models), so it will come back.

8. **A non-learned component composed with the network** — `itra` (a bicycle
   kinematic model after the CVRNN), `tankbind` (gradient descent from a
   predicted distance map to a pose). Topology counts *learned* components, so
   these models look like one component when they are a hybrid of a network and
   a physics/solver stage.

9. **Fixed random / non-learned front end** — `mosaiks` (random convolutional
   features), `dlinear` (series decomposition). Connectivity cannot distinguish
   a learned convolution from a frozen random one.

10. **Supervised intermediate representation** — `coop-cbm`. A concept
    bottleneck predicts human-named concepts and then the label from them. That
    is two components in sequence, but the thing that makes it a CBM is that the
    *intermediate is supervised*, which no axis records.

11. **Input modality** — `gpt-4v`, `gpt-4o`, and `protst` on the text side. I
    assume this is deliberate (modality is presumably a different dimension),
    but it means GPT-4V pins literally nothing that distinguishes it from GPT-4.

## 2. Single-valued topology: NOT falsified by this batch

No name in the 130 wanted two topology values at once. Reporting the near misses
so the absence is checkable rather than assumed:

- `equibind` processes two graphs, but they exchange messages at every layer, so
  `Multi-tower` ("combined only at the end") genuinely does not apply and
  `Single component` is correct. I left it inherited rather than pin it.
- `sepformer`, `goku-ui`, `coop-cbm` each have a plausible second reading, but in
  every case one value wins outright under the positive tests.
- `dart` is the one honest strain, and it is a **scoping** question, not an axis
  failure: a model-based RL agent is a world model *and* a policy network, each
  with its own topology. Topology describes a model; the name describes an agent
  assembled from two. Same shape as §5.1. Nothing here says the axis set is
  wrong; it says "what is the unit a name denotes" is undecided for agents.

**The axis set survived this batch.** The strain that did show up is in the
*inheritance rules*, not the values — §3.

## 3. Existing nodes that are misplaced, or that resolve wrongly

### 3.1 Connectivity is union-only, so a child can never deny its parent — and three nodes are wrong because of it

`resolve.py` unions connectivity up the ancestor chain, and an empty pin means
"same as parent". There is therefore **no way for a child to drop a value its
parent pins**. Three live consequences, all verified with `resolve.py`:

```
MLP-Mixer    conn = Fully connected, Self-attention
Neural ODE   conn = Standard convolution, Convolution   (also Neural SDE, CNF, FFJORD)
RWKV         conn = Self-attention, Recurrence
```

- **MLP-Mixer resolves to Self-attention.** The paper's whole claim is "an
  architecture based exclusively on MLPs ... without attention". The value comes
  in from the `vit` parent, which is a correct R1 edge. The edge is right and the
  resolution is wrong.
- **Neural ODE, Neural SDE, Continuous normalizing flow and FFJORD all resolve
  to `Standard convolution`,** inherited from `ResNet`. The ResNet edge is well
  grounded (the ODE is the continuous limit of a residual net), but FFJORD is
  not a convolutional network, and nothing can say so.
- **RWKV pins `self-attention` on its own row** although it replaces softmax
  attention with a linear recurrence; `attention-sparsity = linear-attention`
  looks like the value that row actually wants.

This needs a decision at the design level, not a row edit: either a negative pin
(an explicit "not X"), or a per-node `connectivity_override` that replaces rather
than unions. It bites exactly the "built from X but deliberately without X's
mechanism" designs, which is a recurring and historically important shape.

### 3.2 Topology under two parents is decided by parent order

`_chain` is breadth-first over the `parents` column, so with two parents the
**first one listed silently wins** a single-valued axis. `Flamingo`
(`vit|transformer`) resolves to **Bidirectional encoder stack**, although its
language model is a frozen causal decoder that cross-attends to a vision
encoder — it inherits ViT's topology purely because `vit` is written first.
`BLIP` (`vit|bert`) resolves the same way and is at least debatable. If the
column order is load-bearing, it should be documented as such; I suspect it is
not meant to be.

### 3.3 Acronym collision already in the tree

`lda_discriminant` (Linear discriminant analysis) and `lda_topic` (Latent
Dirichlet allocation) both have a legitimate claim on the bare string `lda`. The
SPELLINGS tie rule correctly refuses it, but `linear discriminant analysis (lda)`
in this worklist resolves only because the long form is present. A bare `lda`
mention is unresolvable and should be reported as such rather than assigned.

### 3.4 `Perceiver` and `Set Transformer` have no topology at all

Both inherit from the `Transformer` root, which deliberately pins none (L-10),
and neither pins its own. They are the only non-root nodes in the tree with an
empty topology. `perceiver io` in this batch has to pin `encoder-decoder` on a
parent that answers nothing, which is odd: Perceiver is a single stack of latent
self-attention fed by cross-attention, and should say so.

## 4. Families that need intermediate structure (R7 — flagged, not invented)

Nodes whose literal R1 parent does not exist. In each case I attached to the
nearest existing ancestor and recorded the gap rather than creating the missing
level.

| name | missing R1 parent | what I did instead |
|---|---|---|
| `coop-cbm` | **`Concept bottleneck model`** — a family, not a descent node | **verdict `unsure`.** This is the one case where no backbone is honest: coop-CBM descends from CBM, not from a CNN. Needs a design pass. |
| `starcoder` | `StarCoderBase` | parent `transformer` |
| `instructblip` | `BLIP-2` | parent `blip` |
| `ghn-3` | `GHN` / `GHN-2` | parent `gnn` |
| `goku-ui` | `GOKU-net` | parent `vae` |
| `itra` | `Variational RNN` (CVRNN) | parent `rnn`, pinning the VRNN's stochastic latent directly |
| `sepformer` | `DPRNN` (the dual-path framework it transformerises) | parent `transformer` |
| `shallowconvnet` | its sibling `DeepConvNet` is also absent | parent `cnn` |

A strict reading of R7 would let a second pass attach `StarCoderBase` under
`Transformer` and `StarCoder` under it, since both are descent edges. The output
format is one row per input name, so I could not express that here; it is worth
deciding whether chained descent attachment is in scope for the second pass.

## 5. Gaps in the verdict set itself

### 5.1 Composite pipeline strings — `contriever + flan-t5`, `dpr + fid`

Neither is a name: each is a retriever-plus-reader **configuration** of two
models, which L-21 already settled is not a lineage edge. They are not
`misextraction` (nothing non-model was extracted), not `generic` (they name
specific releases), and not `alias`. Both are marked `unsure` for want of a
value. **A `split` verdict is needed** — "this string denotes N models, here they
are" — otherwise every pipeline string in the corpus is either dropped or
mis-parented. Contriever itself has no node yet (a BERT-family dense retriever).

### 5.2 Scientific, clinical and cognitive models that are not ML architectures

Four names in this batch are models that are not learned architectures:

- `rapidbrachymctps`, `egs_brachy graphical user interface (eb_gui)` — Monte
  Carlo dose-engine software. Filed as `misextraction` (tools), which is right.
- `species distribution models (sdms)` — a **task-defined** class (realised as
  GLMs, MaxEnt or random forests). Filed `generic`, pinning nothing, because
  what it names belongs to the task/domain dimension.
- `sample-based expected utility (sbeu)` — a cognitive **process model** of human
  decision making. Filed `unsure`: it is not a misextraction (it really is a
  model), it is not an ML architecture, and the backbone test has no purchase on
  it.

These are not defects in the extraction. The corpus contains domain simulation
and cognitive models, and the models dimension currently has no place to put one
that is neither an ML architecture nor a tool. Worth a holding value.

### 5.3 Learned optimizers — `lagg-a`, `lopt-a`

Both `unsure`, for one question: **is a learned optimizer model-side or
algorithm-side?** It is a parameterised network with its own wiring (model), and
it exists only inside the training procedure (algorithm). The paper calls both
"architectures". Neither the backbone test nor R1–R7 decides this, and the answer
governs a whole corpus cluster (learned optimization, hypernetworks, learned
samplers).

### 5.4 Architectural components — `film`

A layer is neither a model nor an algorithm. FiLM, attention heads, adapters and
gating mechanisms all have this shape; some of them (sparse attention, MoE
routing) were absorbed as attributes, and FiLM was not. `unsure` until the design
says whether components are in scope.

## 6. Where I drew the self-supervised line, and why it is the softest call here

This batch contains the SSL cluster that L-18 explicitly left open. I used one
test, applied consistently:

- **algorithm** when the paper contributes a *recipe* that other papers
  reproduce on their own backbone: `simclr`, `byol`, `swav`, `simsiam`,
  `barlow twins`, `diffpret`, `siamdiff`, `geossl-ddm`.
- **lineage** when the paper releases a *model family that other papers execute
  as a pretrained artifact*: `dino` (under `vit`), `v-jepa` (under `vit`),
  `videomae` (under `mae`). This matches how L-18 kept MAE and how DINOv2 is
  already a node.

The corpus columns support the split (`dino` is executed in 3 of its 6 papers;
`simclr` in 16 of 20 but always as a method being compared). It is still a
judgement, and if the owner collapses it either way, 8 rows move together. If
MAE and DINOv2 are ever demoted to algorithm-side, `dino`, `v-jepa` and
`videomae` go with them.

A second, smaller version of the same question: **`prototypical networks`**. I
called it `algorithm`, but it changes the *prediction rule* (nearest class mean),
not only the objective, so it is not a clean pass of the backbone test as
written. The same applies to any metric-learning head.

A third: **`polytropon`**. Adapters and LoRA are settled algorithm-side, so Poly
is too — but its routing function makes `attributes = conditional-computation`
true of the resulting model, and that residue is currently unrecorded.

## 7. Extraction artifacts worth reporting upstream

- **`adaptive-`** is a truncated name: the paper's module is `Adaptive-η`. The
  Greek character was dropped, leaving a string that cannot be matched to
  anything. Likely a systematic loss wherever a name ends in a symbol.
- **`vit-b/16`** should not have been in this worklist at all — its header says
  size/version variants of placed nodes are left to the second pass, and this is
  one (under `vit`). The slash probably defeated the variant filter.
- **`gpt-3.5-turbo`** and **`gpt-3.5 turbo`** arrived as two rows; they are one
  release. I made the hyphenated one the node (proposed id `gpt35_turbo`, parent
  `gpt35`) and the spaced one its alias. The alias target is therefore a node
  that does not exist yet — the only row in the file whose `target` is not an
  existing `node_id`.
- **`deep q networks (dqn)`**, **`deep q-network`**, **`dqn`**, and
  **`sac`** / **`soft actor-critic (sac)`** are spelling variants of each other,
  but since both referents are algorithm-side there is no node to alias to, so
  each row carries the `algorithm` verdict. If the algorithms dimension gets its
  own spelling table, these four pairs are ready-made rows for it.
- **`random forest classifier`** → `random_forest` is an alias of a **fourth
  shape** R3 does not list: the design name plus its task ("X classifier",
  "X regressor"). It is not orthography, not an acronym, not a plural. Cheap to
  add as R3 case 4; I used it rather than inventing a node, but it is a rule
  extension, not a rule application.
- **`chatgpt-3.5`** is genuinely ambiguous between the `chatgpt` and `gpt35`
  nodes that L-24 deliberately keeps separate. I sent it to `chatgpt` because the
  quote uses bare "ChatGPT", at `medium`. By the SPELLINGS tie rule it arguably
  should be refused instead.

## 8. The rows I am least sure of

In rough order of how much I would want a second opinion:

1. `protst` (low) — lineage dual-encoder under `esm`, or algorithm-only? The
   paper says "framework"; the released artifact is a CLIP-shaped pair.
2. `dart` (low) — a named transformer world model, or "a sample-efficient
   method" as its own abstract calls it?
3. `mosaiks` (low) — I read "Kitchen Sinks" literally and parented it on
   `kernel_ridge`. `linear_model` is defensible if the random convolutional
   features are preprocessing rather than the model.
4. `goku-ui`, `itra`, `tankbind`, `ghn-3` (low) — each attached to a backbone
   that is the nearest *existing* ancestor rather than its true R1 parent (§4).
5. `google translate` (low) — admitted under L-24's product rule, but unlike
   ChatGPT or Gemini its backbone actually changed kind (GNMT/LSTM → Transformer),
   so its topology pin is true only of the current service.
6. `dinosaur` (medium) — `slot_attention` parent is solid; whether the frozen
   DINO encoder earns an R5 second parent is not.
7. `gatedgcn`, `equibind` (medium) — parent `gnn` versus the more specific `gcn`
   / `egnn`. I took the safer, shallower edge in both cases.
8. `dyngfn`, `crystal-gfn`, `swift-dyngfn`, `gsdm`, `mudiff`, `meshdiffusion`
   (medium) — the GFlowNet and diffusion families are settled algorithm-side, but
   several of these papers contribute a real denoiser/sampler **architecture**
   alongside the objective (GSDM's structured attention mask, MUDiff's MUformer,
   DynGFN's hypernetwork). Under the current rules those architectures vanish. If
   the owner wants denoiser architectures admitted, these six rows change
   together.
