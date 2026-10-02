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
Tree traversal
Kernel expansion
```

## Axis 2 — Macro topology  *(single-valued)*

**Characteristic: the shape of the computation as a whole — what feeds what.**

```
Single stack
├── Bidirectional encoder stack     (BERT)
└── Causal decoder stack            (GPT, LLaMA)
Encoder–decoder                     (T5, BART, U-Net)
Reconstruction
├── Autoencoder
├── Variational autoencoder
└── Masked autoencoder              (MAE, BEiT, SatMAE)
Invertible
├── Coupling flow
├── Autoregressive flow
└── Continuous-time flow
Multi-tower
└── Two-tower / dual encoder        (CLIP)
Implicit field                      (NeRF, SIREN, DeepSDF)
Ensemble
```

**`Encoder-only` / `Decoder-only` / `Encoder-decoder` lives here, not in
lineage.** Both derivation runs built it inside the Transformer subtree; it is a
topology distinction that would otherwise be re-encoded under every family it
applies to. **`Normalizing flow` is topology** (owner), because invertibility is
a structural demand on the whole model, like a bottleneck.

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

## Coverage, restated

**The ontology covers the field, not the corpus.** A concept with no corpus
mention is flagged speculative and **kept** — the day a mention arrives it must
have a home. This was already locked in the domains design and is restated here
because it bears on axis values as much as on lineage nodes.

(Checked, since it came up: `support vector machine` **is** attested — 13 names,
15 mentions — as are random forest 34, perceptron 22, Gaussian process 6, naive
Bayes 4, Boltzmann machine 3. Both runs placed SVM under `Kernel machine`.)
