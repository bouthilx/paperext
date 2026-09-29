# Rationale — base category structure for ML research topics (run1)

**Scale of the proposal.** 4 axes, 39 substantive top-level categories, 204
substantive categories in total (208 rows including one `Not Specified` per
axis). Depth 2 throughout; every category carries three example children taken
verbatim from `domain_names.tsv`.

---

## 1. The structural decision: four independent axes, not one tree

**Four axes: `method`, `modality`, `domain`, `concern`.** A name is labelled on
each axis independently, and `Not Specified` is a first-class, frequently
correct value on every one of them.

This is not a compromise position. A single tree is *wrong* for this corpus,
and the data says so in four separate ways.

### 1.1 The vocabulary is already a cross-product, in writing

155 of the 2055 names (7.5%, 211 paper-mentions) are literally of the form
`X in/for/with Y`, where X and Y come from different registers:

- method × domain — `Machine Learning for Climate Science`, `Deep Learning in
  Particle Physics`, `Reinforcement Learning in Healthcare`, `Generative Models
  in Material Science`, `Natural Language Processing (NLP) for Biological
  Sequence Design`
- method × modality — `Self-Supervised Learning (Graph Data)`, `Visual
  Reinforcement Learning`, `Protein Representation Learning`, `Transformers in
  Vision`, `Time Series Out-of-Distribution Generalization`
- concern × everything — `Fairness in Ranking`, `Fairness in Recommender
  Systems`, `Privacy-Preserving Graph Data`, `Adversarial Attacks on Large
  Language Models`, `Uncertainty Estimation in Generative Models`,
  `Reproducibility in Medical Imaging`, `Efficient Training of Transformer
  Models`, `Scalability in Graph Neural Networks`

A single tree has to throw away one coordinate of each of these names. Which
one it throws away is arbitrary, and the arbitrariness lands directly in the
counts the survey is meant to produce.

### 1.2 Large parts of the vocabulary are pure on exactly one axis

- **Domain-only, zero ML content**: `Pediatric Surgery` (16 papers),
  `Brachytherapy` (8), `Gastroenterology`, `Hepatology`, `Vaccinology`,
  `Galaxy Evolution`, `Soil Science`, `Trophic Ecology`, `Patient Experience`.
  In one tree these force an "Applications" branch that swallows a third of the
  tail and tells the reader nothing about what was *done*.
- **Method-only, zero domain content**: `Stochastic Mirror Descent`,
  `PAC-Bayesian Theory`, `Submodularity`, `Variational Inequality`.
- **Concern-only**: `Differential Privacy`, `Algorithmic Transparency`,
  `Conformal Prediction`.

A tree with an "Applications" branch and a "Methods" branch is already two
axes, badly implemented: it makes the annotator choose between them instead of
recording both.

### 1.3 The two largest names in the corpus are modality names

`Natural Language Processing` (295 papers) and `Computer Vision` (240) are the
#1 and #4 names — 9% of all paper-mentions between them. They are not methods,
not applications and not concerns; they name the data. If modality is folded
into the method axis, then `Self-Supervised Learning` and `Computer Vision`
become siblings and `Visual Representation Learning` becomes a coin flip. The
corpus has that coin flip written out ~25 times: `Visual`, `Video`, `Graph`,
`Protein`, `Molecular`, `Audio-Text`, `Object-Centric`, `Geometric`,
`Unsupervised`, `Disentangled` Representation Learning. Modality has to be its
own axis, or representation learning fragments across the tree.

### 1.4 The cross-cutting concerns attach to anything

Fairness, privacy, robustness, interpretability, efficiency and evaluation each
appear attached to a method (`Fairness Algorithms`), a modality (`Ethics in
NLP`), a domain (`Bias in Medical Technology`) and an architecture (`Graph
Neural Networks Explainability`). They are properties predicated *of* systems,
not regions of the field. Placed in a tree they either duplicate under every
branch or sit in a "responsible AI" bucket that means nothing.

### 1.5 What four axes cost — stated plainly

1. **Four decisions per name, ~8,200 in total.** Error compounds; the method
   axis is the hardest and will carry most of it.
2. **`Not Specified` dominates three axes.** I expect roughly: modality ~55%
   unspecified, domain ~55%, concern ~80%, method ~40%. Readers must be told
   that "most papers have no fairness label" is the *finding*, not a gap.
3. **Four tables instead of one.** Percentages no longer sum across the report,
   and a paper appears in several. Any headline of the form "X% of the
   institute's research is Y" now needs an axis named in it.
4. **Overlap pairs still have to be adjudicated by scope lines**, not by
   structure: Self-Supervised vs Representation Learning, Domain Adaptation vs
   Robustness to Shift, Anomaly Detection vs OOD Detection. The `scope_out`
   column carries that weight; it is where I spent the most effort.

I take these costs because the alternative loses information that is
*explicitly present in the extracted names*. A survey instrument may be
laborious; it may not be lossy by construction.

---

## 2. The judgement call: model architectures

**Policy: architectures are not research topics on any axis, but architecture
*design* is a method category, and a backbone name is evidence about
modality.**

Three rules, in order:

1. If the architecture name implies a data type, record that on the `modality`
   axis and leave `method` unspecified. `Graph Neural Networks` (76 papers,
   the 8th most frequent name) reliably means *the data are graphs*; that is
   exactly what the modality axis measures, and it is not double-counting an
   architecture ontology to say so. Same for `Vision Transformers`,
   `Graph Convolutional Networks`, `Message Passing Neural Networks`.
2. If the name implies a modelling goal, record that on `method`.
   `Diffusion Models`, `Normalizing Flows`, `Energy-based Models`,
   `Autoregressive Generative Models` → `Deep Generative Modelling`.
   `Generative Models` (83 papers) is a goal, not a network — the corpus quote
   for it lists GANs *and* flows *and* diffusion as instances of a modelling
   aim.
3. If the name states nothing but the backbone — `Transformers`, `Transformer
   Networks`, `Convolutional Neural Networks`, `Recurrent Neural Networks`,
   `Autoencoders`, `Attention Mechanisms` — it goes to `method: Not Specified`
   and is **reported and then excluded** in favour of the project's separate
   architecture ontology.

**Measured cost of rule 3:** 28 backbone-only names cover 161 paper-mentions
(2.7% of 5990). 76 of those are `Graph Neural Networks`, which rule 1 rescues
onto the modality axis. The genuinely discarded residue is **~1.4% of
paper-mentions** — small enough that excluding it cannot tilt the survey, and
excluding it is what prevents the survey from tilting toward architecture work.

What I did *keep* as method is `Neural Architecture Design`: work whose
contribution is an inductive bias (`Equivariant Neural Networks`, `Geometric
Deep Learning`, `Mixture of Experts`, `Modular Neural Networks`,
`Neuromorphic Computing`). That is a research question. "We used a transformer"
is not.

Related redirections that fall out of the same reasoning: `Neural Architecture
Search` → `Black-Box Optimization` (the contribution is the search);
`Model Compression`, `Quantization`, `Pruning`, `Knowledge Distillation` →
`concern: Computational Efficiency` (the contribution is a budget).

---

## 3. What I deliberately excluded

- **A "Machine Learning" / "Deep Learning" / "AI" category.** 40 contentless
  umbrella names account for **517 of 5990 paper-mentions (8.6%)** — including
  `Machine Learning` (249) and `Deep Learning` (177), the #3 and #5 names.
  Giving them a home would create the largest category in the survey out of
  names that say nothing. They go to `Not Specified` on all four axes, and that
  8.6% is a number the report must print, because it measures the extraction,
  not the research.
- **An "Operations Research" domain.** `Operations Research` (19 papers),
  `Vehicle Routing Problem`, `Personnel Scheduling`, `Facility Location` are
  routed to `method: Discrete Optimization` plus whatever domain is stated.
  A domain that is really a method family would have double-counted.
- **A "Natural Sciences" parent** over Life / Physical / Environmental
  Sciences. It would be a three-child level that no research community
  corresponds to, and it would hide exactly the contrast (bio vs physics vs
  climate) the report wants.
- **A "Tabular Data" modality.** The word does not occur in the corpus. If
  three children cannot be found, the category is not real.
- **An "Environmental Cost of Computing" child** under Computational
  Efficiency (`Green AI`, `Energy Efficiency` — only two real names) and a
  **"Machine Unlearning"** child under Privacy (two names). Both dropped under
  the three-children test rather than padded.
- **Balanced sizes.** `Health` has eight children and ~220 names; `Creative
  Media` has three children and ~25; `Causal Inference` has exactly two
  children. `Radiation Oncology Physics` is a first-level child of Health on
  ~28 names because that is a visible, separately funded concentration in this
  corpus. None of this was adjusted for tidiness.

### Branching-factor justifications (rule 6)

Three levels exceed a comfortable width, each deliberately:

- **`domain` has 12 substantive top-level categories.** External fields do not
  nest. Any further grouping ("Sciences", "Engineering", "Computing") is a word
  with no community behind it, and merging would destroy the contrasts the
  report exists to show.
- **`method` has 11.** The method axis holds roughly half the vocabulary;
  11 branches for ~1000 names is not over-branching.
- **`Health` and `Sequential Decision-Making` have 8 children each.** These are
  the two largest concentrations in the corpus (~220 and ~200 names). Rule 5
  forbids merging them into tidier shapes.

---

## 4. Tail coverage (rule 8)

30 names sampled uniformly at random from the 1489 one-paper names
(`random.seed(20260925)`). For each I asked: does this have an obvious home on
at least one axis?

**Result: 27 of 30 placed obviously; 3 did not.**

The three failures:

| name | why it has no home |
|---|---|
| `Interdisciplinary - Other` | Not a topic. The quote is `Interdiscplinary - Other` — a leaked form field. `Not Specified` on all four axes. An extraction artefact, not a structural gap. |
| `Action State Tracking` | Unresolvable from name or quote (`WD could be seen as a generalization of the recently proposed notion of Action State Tracking (AST).`). No structure could place this without reading the paper. |
| `Transformer Networks` | Backbone-only; lands in the declared architecture residue by policy (§2, rule 3). A deliberate no-home, not a miss. |

So: **one genuine structural gap out of 30 (`Action State Tracking`), and it is
a gap in the extraction rather than in the categories.** The other 27 placed
without hesitation, including awkward-looking ones — `Radiolysis` →
`domain: Radiation Oncology Physics` (the quote is about water radiolysis under
ionising radiation), `Consistency Models` → `method: Deep Generative
Modelling`, `Patient Support in Oncology` → `domain: Health Services Research`,
`Semi-Supervised Node Classification` → `modality: Node-Level Prediction` +
`method: Weakly Supervised Learning`, `AI Ethics and Human-Computer
Interaction` → `concern: AI Ethics` + `domain: Human-Computer Interaction`.

That last one is the four-axis design paying for itself: a name that a single
tree must cut in half is recorded whole.

### Residual-bucket fractions, as required

- `Not Specified` from contentless umbrellas: **8.6% of paper-mentions**.
- `Not Specified` from backbone-only architecture names: **~1.4%**.
- Every other `Not Specified` is a positive finding (the name genuinely has no
  domain, no modality or no concern), not a residual.

For orientation: the top 5 names are 20.4% of paper-mentions and names
appearing in ≤2 papers are 32.4%. A third of the signal is in the tail, which
is why `scope_out` lines are written to catch unfamiliar names rather than to
partition familiar ones.

---

## 5. The three calls I am least sure about

1. **`Self-Supervised Learning` (method) vs `Representation Learning`
   (method).** I split them by *training signal* vs *latent structure*. But
   `Contrastive Learning` (21 papers) is both, and the corpus offers
   `Contrastive and Non-Contrastive Learning`, `Graph Contrastive Learning` and
   `Unsupervised Representation Learning` as if they were one family. If a
   reviewer merges these two branches I would not fight hard. The reason I
   kept them apart is that `Representation Learning` (56 papers) has a large
   theory-facing tail (identifiability, disentanglement, object-centric) that
   has nothing to do with how the encoder was trained.

2. **`Reliability` as a parent over OOD detection, anomaly detection,
   distribution shift and uncertainty.** The corpus keeps these lexically
   separate and never uses the word "reliability". I grouped them because they
   answer one question — *can this prediction be trusted off-distribution* —
   but this is my most interpretive move, and the `Anomaly Detection` (20
   papers) members in particular are often plain application tasks (fraud, log
   analysis) with no trust framing at all. A reviewer who splits
   `Anomaly Detection` out to the modality axis as a task would have a case.

3. **`Engineered Infrastructure` as a domain parent.** Energy, telecom,
   transport, buildings, hardware and manufacturing are each 5–15 names. I
   grouped them under an engineering character rather than a research
   community, which is exactly the kind of convenience grouping rule 4
   prohibits. I did it because six extra top-level domains for ~60 names
   between them would have been worse. This is the row most likely to be wrong
   in the comparison across the three proposals.

Two honourable mentions, since they will probably show up as disagreements:
the `domain: Public Policy` vs `concern: AI Regulation` boundary (`AI Policy`
sits on the line), and placing `Language Model Behaviour` on the modality axis
rather than treating large language models as a method family.

---

## 6. Premises, so disagreements can be traced

If another proposal differs from this one, it is most likely because it does
not share one of these:

- **P1.** A name that carries two coordinates must be recorded with both.
  (⇒ multiple axes)
- **P2.** `Not Specified` is information, not failure. (⇒ axes can be sparse)
- **P3.** An architecture is evidence about data, not a research question.
  (⇒ `Graph Neural Networks` counts as graph data, `Transformers` counts as
  nothing)
- **P4.** Category size must never be adjusted. (⇒ Health has 8 children,
  Causal Inference has 2)
- **P5.** A category with fewer than three real children in the data is not a
  category. (⇒ several plausible-sounding categories were dropped)
