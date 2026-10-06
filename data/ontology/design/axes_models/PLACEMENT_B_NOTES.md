# PLACEMENT_B — notes

Companion to `PLACEMENT_B.tsv` (130 names from `WORKLIST_B.tsv`, placed
2026-10-06). Classification against the settled axis set, not design.

Counts: **algorithm 62 · lineage 44 · alias 11 · unsure 6 · misextraction 3 ·
quarantine 2 · generic 2.**

---

## 1. Did anything falsify the axis set?

### Topology survived this list. Attributes did not.

**No name in this worklist wants two values on single-valued `topology`.** I
looked for it specifically, including at the four multimodal models (ALBEF,
FLAVA, X-VLM, UNITER) that are the obvious candidates, and the axis held: each
is either one tower (UNITER) or parallel towers plus a fusion stage
(`Multi-tower / dual encoder`). That is one value, not two.

**The single-valued-within-family rule on `attributes` does break, on
`Shortcut connections`, and it is already breaking silently in the tree.**

`v-net` is the clean case. V-Net has U-Net concatenative skips between encoder
and decoder **and** ResNet-style additive residuals inside each stage. Both are
load-bearing: the skips are what makes it a U-Net, the residuals are what the
paper's own framing is about. `Shortcut connections` is single-valued within the
family, so pinning `additive-residual` would make `concatenative-skip` vanish by
nearest-pin-wins. I pinned **neither** and left the row's attribute column empty
rather than delete half the truth.

This is not hypothetical, and it is not confined to my worklist — the existing
tree already loses information this way:

```
$ python3 resolve.py stable_diffusion
  Stable Diffusion (latent diffusion)  ...  attr=Concatenative skip, Stochastic
```

Stable Diffusion's denoiser is a U-Net whose blocks are **ResBlocks** and whose
cross-attention blocks are **Transformer blocks** — both additive-residual. The
resolver returns `Concatenative skip` alone, because `unet` is nearer in the
chain than `transformer`. Same for any Transformer-inside-U-Net design. No
lineage row currently double-pins inside one attribute family (I checked all
297), so the loss happens purely through inheritance and is invisible unless you
run the resolver and compare against the paper.

Reading, for the owner to settle: the family bundles two questions — *is there a
bypass path* and *what does it carry*. A model can have one of each kind in
different places. Either `Shortcut connections` becomes multi-valued (and the
VQ-VAE argument that motivated nearest-pin-wins does not apply here, because
`additive` and `concatenative` are not mutually exclusive the way
`deterministic` and `stochastic` are), or it needs a `Both` value, or the axis
accepts that it records only the *distinctive* shortcut and says so. I did not
choose; the design is settled and this is a design question.

## 2. Axis values a name needed and could not get

| name(s) | what is missing |
|---|---|
| `gemnet`, and `painn`/`gvp` on the other side | **Invariance vs equivariance.** The corpus quote partitions the molecular models literally: *"Invariant Model: SchNet, DimeNet, SphereNet, GemNet"* against *"Vector Frame Basis Equivariant Model: EGNN, PaiNN, GVP"*. `Symmetry` has only `Euclidean equivariance`, so both halves collapse onto one value and the distinction the field draws — scalar features of distances/angles vs vector features that rotate with the input — is unrecordable. Suggests a child split under `Euclidean equivariance`. |
| `ecapa-tdnn` (and existing `senet`) | **Channel attention / squeeze-excitation.** Connectivity's `Attention` is "wiring weights computed from the content of the inputs", which SE satisfies, but SE gates *channels*, not positions, and the axis's examples are all positional. `senet` currently pins nothing for it, so I followed that precedent and pinned nothing for ECAPA-TDNN either. If SE is meant to be attention, `senet` is under-pinned; if it is not, the axis should say so in a negative test. |
| `constant memory attentive neural processes (cmanps)` | **Constant-memory attention.** `Attention sparsity` offers dense / sparse / linear. CMAB's claim is constant memory in the context size, which is neither restricting the pattern nor replacing the softmax with a feature map. I pinned `linear-attention` as nearest, which is an approximation. |
| `wurstchen` (and existing `dalle2`, `imagen`) | **Multi-stage cascade.** Würstchen is three separately trained stages chained at inference. `Encoder–decoder` claims two bodies with a latent between them, which is half right and hides the third stage; `Ensemble` is wrong (members are not pooled, they are composed). Topology has no value for a cascade. |
| `knn-lm` vs `realm` vs existing `ntm` | **`External memory` is one value doing three jobs**: a differentiable tape written during the forward pass (NTM), a frozen kNN datastore of cached activations (kNN-LM), and a learned retriever over an external document corpus (REALM). They differ in whether the store is learned, written to, and part of the gradient. Children would be cheap and the corpus already has all three. |

## 3. Existing nodes I think are misplaced

1. **`decision_list` pins `tree-traversal`.** It resolves to *both* `Tree
   traversal` and `Rule set evaluation` — and the two values' negative tests
   directly contradict each other ("the conditions are a hierarchy" vs "the
   conditions are an unordered or flat set"). A decision list is a flat ordered
   if-then list; `rule_set_evaluation` is already inherited from
   `rule_based_model`, so the `tree-traversal` pin should simply be removed.
   This bears on my `corels` row, which I attached under `decision_list`.

2. **`neural_ode` (and so `cnf`, `ffjord`) inherits convolution and residuals
   from `resnet`.** `python3 resolve.py ffjord` returns `conn=Standard
   convolution, Convolution ... attr=Invertible, Additive residual`. A
   continuous normalizing flow is not convolutional, and the ODE *replaces* the
   residual block rather than containing one — "ResNet in the limit of
   infinitely many layers" is the derivation, not a description of the result.
   The R1 edge to `resnet` is right; the inherited pins are not. `neural_ode`
   probably needs to re-pin connectivity to `fully-connected` and the shortcut
   family to `no-shortcut`.

3. **`blip` and `vilbert` disagree on topology for the same shape.** BLIP is an
   image encoder plus a text encoder plus a cross-attention fusion encoder, same
   as ViLBERT; `vilbert` pins `multi-tower`, `blip` does not and so resolves to
   `Bidirectional encoder stack`. I had to pick a side for ALBEF, FLAVA and
   X-VLM and followed `vilbert`. If BLIP is right, those three rows should drop
   their topology pin — but then `clip`, which also pins `multi-tower`, is the
   odd one out. One of the two readings is wrong.

## 4. Missing intermediates (R7: flagged, not invented)

None of these is a **grouping** node, so R7's prohibition does not technically
bite — each is a named design that would attach by descent. I still did not
create them, because they are not names on my worklist, and attached the child
one level up instead. Each attachment is marked in the row's `why`.

| wanted node | where it belongs | the child I had to lift |
|---|---|---|
| `BiT` (Big Transfer) | under `resnet` | `bit-s-101` → `resnet` |
| `ViViT` (video ViT) | under `vit` | `crossvivit` → `vit` |
| `GraphGPS` | under `graph_transformer` | `gps++` → `mpnn\|graph_transformer` |
| `EquiBind` | under `gnn` | `e3bind` → `gnn` |
| `StarCoder` | under the `starcoderbase` node this list adds | (none yet; noted for the next pass) |
| `LaMDA`, `PaLM 2` | under `transformer` | `google bard` → `gemini`, true of the quoted release only |
| `Contriever`, `Atlas` | under `bert` / `t5` | `contriever + atlas` left `unsure` |
| `SphereNet`, `GearNet`, `CDConv` | under `mpnn` / `gnn` | named only in quotes; not on the worklist |

## 5. What made me hesitate

**The RL-agent boundary is the biggest source of soft calls in this list.**
PPO/SAC/DQN are settled fixed points, and `rainbow`, `der`, `iqn`, `td3`, `a2c`,
`qmix`, `maven`, `emc`, `drq()`, `iql` (both of them), `qtd`, `lola`, `pola`
follow straightforwardly. But `muzero`, `dreamerv2`, `planet` and `qmix` each
*do* specify networks: PlaNet introduced the RSSM, QMIX introduced a monotonic
mixing network. I ruled all four **algorithm** because `rssm` already exists as
the node for PlaNet's and Dreamer's network, and because the agents' named
contribution is the planning or factorisation scheme. A reviewer who wants
"proportion of papers using Dreamer" countable in *this* dimension will disagree,
and the fix would be lineage nodes under `rssm`. Flagging rather than deciding.

**Why HuBERT-style nodes exist but SimCLR-style ones do not.** `hubert` and
`wavlm` are lineage nodes under `wav2vec2` although they differ from it only in
the SSL objective — exactly the thing the backbone test sends to algorithms. I
placed `data2vec` and `distilhubert` the same way, and `simclrv2`, `moco`,
`vicreg` and `barlowtwins` as algorithms. The line I used: **a separately named,
separately released set of weights is a node; a named objective applied to
whatever encoder you like is an algorithm.** data2vec and HuBERT ship
checkpoints people load by name; SimCLR ships a loss. That line is defensible
but it is not written down anywhere, and it is the single rule doing the most
work in this file.

**`generative adversarial networks (gans)`** → algorithm, not quarantine. The
merge header says `GAN` was "an axis value wearing lineage clothing" and took it
apart, and adversarial training is an objective; meanwhile `dcgan`, `stylegan`,
`cyclegan` and `srgan` all survive as nodes. So the term names a real paradigm
with a real home — just not here. If the owner intended GAN to be quarantined
instead, that changes nothing downstream except the reported line.

**`t-sne`, `phate`, `mali`** → algorithm, on the admission rule: like k-NN and
kernel density they emit coordinates for the points you gave them and leave no
separable learned object behind. This makes "manifold learning" invisible in the
models dimension, which is correct but worth saying out loud since three names
in this worklist land there.

**`orbgrand`** → algorithm is the least comfortable fit of any row. It is a
channel-decoding search with *no learned parameters at all*, so it is not a
model; but the algorithms dimension is about learning algorithms and may not
want it either. It may need a third destination, or a `misextraction`-adjacent
verdict for "not machine learning".

**Convention for `generic` rows.** A generic has no parent, so nothing inherits.
I wrote the **most specific** value only (`cnn-lstm` → `convolution |
gated-recurrence`, not also `recurrence`); consumers must close upward through
the axis tree. Lineage rows get the coarse value for free from their ancestors,
so the two row kinds are not directly comparable without that step.

**Named-but-opaque models.** Six rows are `unsure`, and five of them are the
same shape: a named design whose *family* I can guess but whose R1 parent the
quote does not state (`charlm`, `jei-dnn`, `retreever`, `toxbuster`, and
`contriever + atlas`, which is a two-name string). R1 asks for the introducing
paper's own framing, and reconstructing the edge from architectural similarity
is explicitly R2, not R1 — so I left them rather than guess. Low-confidence
`lineage` rows where I *did* commit the family but not the edge: `e3bind`,
`moleculesde`, `protseed`, `muformer`, `fusionretro`. Those five are where I
would look first if these placements get audited.

**`-model`** is a mangled `δ-model` — extraction dropped the leading Greek
letter. Worth checking whether the same defect hit other names in the corpus
(`drq()` has lost its ε the same way, though it is still identifiable).
