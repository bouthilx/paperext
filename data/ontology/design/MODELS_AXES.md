# Models dimension — the axis set

Settled with the owner 2026-10-02. Supersedes the single-lineage-tree design in
`MODELS_DERIVATION_BRIEF.md` §3, which the two derivation runs showed to be
conflating independent properties into one sibling set.

**A model is not *in* a tree. It has values on several independent axes, one of
which is a position in a lineage tree.** Concepts combine combinatorially —
a spiking CNN, a convolutional autoencoder, an equivariant Transformer — and a
single tree forces each combination to pick one parent and lose the rest.

**Every axis may itself be hierarchical** (owner, 2026-10-02). Flat vocabularies
would push hierarchical structure that genuinely belongs to connectivity or
topology back into lineage, duplicating it under every family it applies to.

---

## The axes

| axis | cardinality | depth | what it answers |
|---|---|---|---|
| **lineage** | a tree position (rarely 2) | 3–4 | what was it built from |
| **connectivity** | **many** | 2–3 | how are learned units wired |
| **topology** | one | 2–3 | what shape is the computation as a whole |
| **attributes** | **many** | 2 | which properties are asserted of it |

**A lineage node pins values on the other three.** `BERT` ⇒ self-attention ·
bidirectional encoder stack · rate-based. That is what naming a design buys.

### Resolution: how to read a model's axis values

A lineage node **pins only what differs from its parent**, so a model's
effective values are never read off its own row. The rules differ per axis and
are implemented once in `axes_models/resolve.py`:

- **topology** — single-valued. The **nearest ancestor that pins it wins.**
- **connectivity** — multi-valued. **Union** up the ancestor chain. A parent's
  coarse value and a child's refinement may both appear (`Convolution` +
  `Standard convolution`); the child refines, it does not replace.
- **attributes** — multi-valued **across** families. **Within** a family,
  cardinality is **declared per family** in `attributes/nodes.tsv`:
  `one` → nearest pin wins (substrate, latent treatment, invertibility, weight
  treatment, routing, memory, attention sparsity); `many` → union (**symmetry**,
  **shortcut connections**).
- **negative pins** — a value written `!node-id` in a lineage row **blocks** it
  for that node and its descendants.

Each of those exists because the naive version produced a wrong answer on a real
model, and none was visible to the structural validators:

| rule | what it was wrong about before |
|---|---|
| per-family cardinality `one` | VQ-VAE resolved to `Deterministic` **and** `Stochastic` **and** `Quantized`. |
| per-family cardinality `many` | A blanket single-value rule then regressed **EGNN**, which really is permutation- *and* Euclidean-equivariant, and dropped one of V-Net's and Stable Diffusion's two shortcut kinds. |
| negative pins | Union inheritance gave a child no way to deny its parent. **MLP-Mixer** resolved to `Self-attention` although the paper's claim is an all-MLP architecture *without* attention; **FFJORD** resolved to `Standard convolution` because Neural ODE descends from ResNet. |
| explicit topology under multi-parent | **Flamingo** resolved to `Bidirectional encoder stack` purely because `vit` was listed before `transformer` in its `parents` column. `resolve.py --audit` now reports any node in that state rather than silently resolving it. |

### Two naming modes, both first-class

- **Named design** — `LLaMA`, `BERT`, `ResNet-50`. Resolves to a lineage node,
  which pins every other axis at once.
- **Generic description** — "a convolutional autoencoder", "a 3-layer MLP".
  Pins only the axes it names; layer counts and sizes come from the paper when
  stated and stay unknown when not. **No lineage node, and that is not a
  defect** — roughly half this corpus describes models this way.

---

## Axis 1 — Connectivity  *(multi-valued)*

**Characteristic: how learned units are wired to one another.**
Multi-valued because hybrids are real: `Conformer` is `{convolution,
self-attention}`. This dissolves most of what the old R5 handled as
multi-parent lineage edges.

```
Dense
├── Fully connected
└── Factorized / low-rank
Convolution
├── Standard convolution
├── Depthwise-separable convolution
└── Dilated convolution
Attention
├── Self-attention
└── Cross-attention
Recurrence
├── Gated recurrence          (LSTM, GRU)
└── State-space recurrence    (S4, Mamba)
Message passing
├── Spectral graph convolution
└── Spatial message passing
Set aggregation                     (Deep Sets, PointNet)
Tree traversal
Kernel expansion
```

`Set aggregation` was added 2026-10-02 — the axis had no value for a
permutation-invariant pooling stack. It is distinct from message passing, which
requires edges.

## Axis 2 — Macro topology  *(single-valued)*

**Characteristic: how many components the model has and how they are arranged.**
Nothing else. Everything that turned out to be an objective went to algorithms,
and everything that turned out to be a constraint on the function class went to
attributes.

```
Single component                    (ResNet, NeRF, SVM, Gaussian process)
├── Bidirectional encoder stack     (BERT)
└── Causal decoder stack            (GPT, LLaMA)
Encoder–decoder                     (T5, BART, U-Net, AE, VAE, MAE)
Multi-tower / dual encoder          (CLIP, DPR, Siamese)
Cascade / multi-stage               (Stable Diffusion, DALL-E 2, Imagen)
Ensemble
```

**`Encoder-only` / `Decoder-only` / `Encoder-decoder` lives here, not in
lineage.** Both derivation runs built it inside the Transformer subtree; it is a
topology distinction that would otherwise be re-encoded under every family it
applies to.

### Three things that look like topology and are not

**`Autoencoder` is not a topology value** (owner, 2026-10-02). An autoencoder is
an encoder and a decoder — so is T5, so is U-Net. The topology is identical; what
differs is **what the target is**, which is the training objective, which the
backbone test puts on the algorithm side. The bottleneck does not rescue the
distinction: U-Net has one, denoising autoencoders do not require one, and MAE's
encoder and decoder are deliberately asymmetric.
*Consequence*: "proportion of papers using autoencoders" is a cut in the
**algorithms** dimension, with reconstruction, masked reconstruction,
variational inference and adversarial training.
*Residue*: a VAE's encoder emits (μ, σ) rather than z, which is a real
difference in the network. That is the attribute `Latent treatment`.

**`Invertible` is not a topology value** (owner, 2026-10-02). Invertibility is a
constraint on the function class, which is what equivariance is, and equivariance
is an attribute. A normalizing flow is a single stack with `Invertibility:
invertible`. The coupling / autoregressive / continuous-time split is **lineage**
substructure under a `Normalizing flow` family, not a topology one.

**`Implicit field` is not a topology value.** NeRF and SIREN are single stacks —
coordinate in, value out. What is distinctive is what they *represent*, not their
shape, so `Coordinate MLP (implicit neural representation)` is a **lineage**
family under the feedforward root, where run A had it.

## Axis 3 — Attributes  *(multi-valued)*

**Characteristic: which property of the model is being asserted.** Level 1 names
the property family; level 2 its values. **Substrate is an attribute** (owner) —
outside the neural branch it is implied by lineage, so it does not earn an axis.

```
Substrate
├── Rate-based neuron               (the default)
└── Spiking neuron
Weight treatment
├── Point estimate                  (the default)
└── Bayesian / distributional
Symmetry
├── Permutation equivariance
├── Euclidean equivariance          (E(n), SE(3))
└── Translation equivariance
Routing
├── Dense computation               (the default)
└── Conditional / mixture-of-experts
Memory
└── External memory
Shortcut connections
├── No shortcut                     (the default: VGG, plain MLPs)
├── Additive residual               (ResNet, Transformer blocks)
└── Concatenative skip              (DenseNet, U-Net)
Latent treatment
├── Deterministic                   (the default)
└── Stochastic                      (VAE: the encoder emits μ, σ)
Invertibility
├── Non-invertible                  (the default)
└── Invertible                      (normalizing flows)
```

## Axis 4 — Lineage  *(a tree)*

**Characteristic: what the model was built from.** R1–R7 of
`MODELS_DERIVATION_BRIEF.md` §4 continue to govern this axis and only this axis.

What changes from the two runs: their **lineage spines survive** — BERT and its
variants, the ResNet family, the detection convnets, the GNN families. Their
**root sets are taken apart**, because `Autoencoder`, `Normalizing flow`,
`Spiking neural network`, `GAN` and `Embedding/Factorization model` were axis
values wearing lineage clothing.

Roots become the genuine design lineages: `Transformer`, `Convolutional
network`, `Recurrent network`, `Graph neural network`, `Multilayer perceptron`,
`State-space model`, `Neural operator`, `Decision tree`, `Linear model`,
`Kernel machine`, `Probabilistic graphical model`.

---

## On `Single component` holding 57% of nodes

Raised by the owner 2026-10-06: ResNet, SVM, HMM and Gaussian process all
resolve to the same value, which looks wrong for four such different models.

**Part of it was the name.** The value was `Single stack`, and a *stack* means a
stack of layers — which asserts something false about an SVM even though the
underlying claim, *this model has one component*, is true. Renamed to
`Single component`; its two children keep `stack` because they are genuinely
layer stacks.

A compute-pattern reading was considered and rejected. It half works — an SVM at
inference really is one matmul, one elementwise kernel and one reduction, so it
matches a single dense layer — but a Gaussian process needs an O(n³) Cholesky at
fit time, which has no analogue in any neural network, and SVM training is a
quadratic program. More decisively, reading topology as compute would reverse
the settled decision that compute belongs to the **run**, and would make a
model's topology depend on whether it is training or predicting.

The rest is correct, and worth stating why. **Topology asks only how many
components a model has and how they are arranged** — nothing else. All four
have one. What separates them lives on `connectivity`, which does so cleanly:
ResNet is convolution, SVM and GP are kernel expansion, HMM is a factor graph
over a state-space recurrence. SVM and GP then separate on an attribute,
`Bayesian / distributional`, which is the actual difference between them.

Measured distribution over the 297 lineage nodes:

| value | nodes | |
|---|---|---|
| Single component | 168 | 57% |
| Causal decoder stack | 43 | 14% |
| Encoder–decoder | 33 | 11% |
| Bidirectional encoder stack | 33 | 11% |
| Ensemble | 10 | 3% |
| Multi-tower / dual encoder | 7 | 2% |

So topology is **low-information for the majority and sharply discriminating
for 43%**. That is a property to know, not a defect to fix — an axis earns its
keep by the distinctions it makes, not by spreading entities evenly, and
engineering an even spread is the rebalancing this design forbids.

## Coverage, restated

**The ontology covers the field, not the corpus.** A concept with no corpus
mention is flagged speculative and **kept** — the day a mention arrives it must
have a home. This was already locked in the domains design and is restated here
because it bears on axis values as much as on lineage nodes.

(Checked, since it came up: `support vector machine` **is** attested — 13 names,
15 mentions — as are random forest 34, perceptron 22, Gaussian process 6, naive
Bayes 4, Boltzmann machine 3. Both runs placed SVM under `Kernel machine`.)
