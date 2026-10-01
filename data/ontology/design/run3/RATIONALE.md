# Rationale

Built from `domain_names.tsv` alone (2055 names, 5990 paper-mentions, 1489 names
appearing once). All counts below are paper-mentions from that file.

**Shape of the deliverable:** 12 top-level categories, 63 second-level
categories, 75 rows. Every one of the 225 example children is a label that
appears literally in the corpus.

---

## 1. The structural question: one tree, and the top split is *not* method vs. domain

**Decision: one tree, one label per name.**

The argument is empirical, and it is the argument I would most like the other
two proposals tested against.

I tagged every name for whether it mentions a machine-learning concept, a field
of application, both, or neither:

| | names | paper-mentions |
|---|---|---|
| names a method only | 530 | 2964 |
| names a domain only | 458 | 1177 |
| names both | 129 | 188 |
| names neither (tasks, properties, umbrellas) | 938 | 1661 |

**Only 3% of paper-mentions carry two facets.** The extraction did not produce
faceted names; it produced single-concept names of different kinds. A
multi-axis structure — "assign every name a method *and* a domain" — would
therefore spend roughly 80% of its Domain-axis cells and 20% of its Method-axis
cells on "not applicable". Axes whose cells are overwhelmingly empty are not
axes; they are a partition wearing a costume, and they would cost the report a
column of noise on every table.

The multi-facet description that a two-axis scheme is reaching for already
exists in the data, for free, at the right level of analysis. A paper carries
~3.0 names (5990/1999). A paper on RL for hospital scheduling contributes
`Reinforcement Learning` **and** `Healthcare` **and** `Scheduling` as three
separate names, each of which lands in a different branch of one tree. The
paper's profile is the *set* of its names' categories. Faceting belongs at the
paper level, where the corpus supplies it; imposing it at the name level, where
the corpus does not, manufactures it.

**What this costs.** Three things, stated plainly:

1. The 129 genuinely dual-facet names (`Medical Imaging`, `Machine Learning for
   Climate Science`, `Protein Representation Learning`) have to be arbitrated.
   I arbitrate them with a fixed precedence rule, below, not case by case.
2. A per-paper "is this applied work?" figure is not read off a single column;
   it is computed as "does this paper have any name under *Applied Research
   Domains*". That is a two-line query, not a redesign.
3. `Medical Imaging` (48 papers) counts as health and not as vision. I accept
   that; see §2.

**What I rejected, and why it matters for comparison.** I drafted and discarded
a version whose top level was `Machine Learning Methodology` / `Applied
Research Domains` / `Non-Specific` — three nodes, with everything else one
level lower. It is a tidier answer to the structural question and it makes the
method/domain distinction visible in the structure itself. I threw it away
because it pushes `Natural Language Processing` (~550 mentions),
`Computer Vision` (~400) and `Reinforcement Learning` (~400) to depth 3, which
means the depth-2 reporting table would show a single row lumping NLP with
vision, graphs and audio. That is the largest measurement in the corpus,
destroyed to buy a cleaner diagram. Rule 5's principle — never let structural
tidiness damage the quantity being measured — outranks the elegance. So: one
tree, shallow, with the big areas as rows.

### The precedence rule (this is the whole tie-break policy)

When a name names more than one thing, assign it to the **first** category kind
that applies:

> **Applied domain → trust property → empirical methodology → data modality →
> learning paradigm → architecture → non-specific**

Rationale: assign to the *scarcer, more specific* facet. Method vocabulary is
the corpus-wide default (50% of mentions); a domain word is rare information
and is the thing a survey of an institute most wants counted. Worked examples:

- `Medical Imaging`, `Reinforcement Learning in Healthcare`,
  `Deep Learning in Particle Physics`, `Code Search` → the domain.
- `Fairness in Recommender Systems`, `Adversarial Attacks on Large Language
  Models`, `Privacy-Preserving Graph Data` → the trust property.
- `Text Data Augmentation`, `NLP Benchmarking` → empirical methodology.
- `Semi-Supervised Node Classification` → Graph Machine Learning (modality
  beats paradigm).

**One named exception, not a fudge:** trust properties written *into* a
decision objective — `Safe Reinforcement Learning`, `Robust Reinforcement
Learning`, `Risk-Averse Reinforcement Learning`, `Constrained Markov Decision
Processes` — stay in *Sequential Decision Making*. The line is *internal
constraint* vs. *external audit*: fairness, privacy, interpretability and
adversarial robustness are properties you test a finished model for;
safe-RL is a term in the objective.

Ethics names are governed by whose ethics: `Medical Ethics`, `Surgical Ethics`
and `Neuroethics` are about a profession → *Health Research* / *Neuroscience*.
`AI Ethics` and `Responsible AI` are about ML systems → *AI Governance*.

---

## 2. Model architectures: in scope, dissolved into the problem they serve, and
## isolated in one node so the overlap is auditable

The brief flags the double-counting risk against the separate architecture
ontology. My policy:

**Architectures are research topics here, but almost none of them get an
architecture-shaped home.** Each architecture name is routed by the research
question it answers:

- `Graph Neural Networks` (76 papers), `Graph Transformers`, `Message Passing
  Neural Networks` → **Graph Machine Learning**. The corpus context is
  decisive: the quote for `Graph Neural Networks` is about representing
  molecules and materials as geometric graphs. The name is being used to
  denote *learning on graph-structured data*, not to denote a layer type.
- `Generative Models` (83), `Diffusion Models`, `Normalizing Flows`, `GANs`,
  `Variational Autoencoders`, `Energy-based Models`, `Consistency Models` →
  **Deep Generative Modelling**. These are a problem (learn to sample), not a
  wiring diagram.
- `Vision Transformers`, `Transformers in Vision` → **Computer Vision**.
- `Neural Networks` (19), `Artificial Neural Networks`, `Deep Neural Networks`
  → **Non-Specific Research Labels**. These are field labels, not topics.
- Only names whose subject genuinely *is* the network structure —
  `Transformers`, `Attention Mechanisms`, `Recurrent Neural Networks`,
  `Convolutional Neural Networks`, `Neural Architecture Search`, `State Space
  Models`, `Mixture of Experts`, `Hypernetworks`, `Equivariant Neural
  Networks` — go to **Neural Architecture Design**.

**That residue is 95 paper-mentions: 1.6% of the corpus, 39 names.** That is
the entire double-counting exposure, it sits in exactly one node, and the
report can subtract it, footnote it, or reconcile it against the architecture
ontology without touching anything else.

I rejected the two alternatives explicitly. *A separate architecture axis*
fails for the reason in §1 — it would be empty for ~95% of names, and it would
force an annotator to decide whether `Reinforcement Learning` "uses" an
architecture, which the name does not say. *Out of scope* fails rule 8 — it
would delete the 8th most frequent name in the corpus and leave 76 papers with
a hole, and it would silently re-weight the survey away from graph learning,
which is a real research area here and not an artifact of architecture
extraction.

---

## 3. What I deliberately excluded or refused to build

- **A residual "Other".** There is no catch-all. *Non-Specific Research Labels*
  is not one: it has a positive definition (names that would be true of a large
  fraction of the corpus) and a stated size. **523 paper-mentions, 8.7%, in 47
  names.** `Machine Learning` (249) and `Deep Learning` (177) alone are 7.1% —
  the 3rd and 5th most frequent names in the corpus carry no discriminative
  content. Reporting that number is more useful than hiding it inside
  *Learning Paradigms*, where it would have inflated a real category by a third.
- **Balanced categories.** *Natural Language Processing* (~550 mentions) and
  *Parameter-Efficient Adaptation* (~5) are siblings' siblings. The spread is
  the measurement.
- **A "Machine Learning Tasks" node.** Generic task words (`Classification`,
  `Regression`, `Segmentation`, `Prediction`) would have made a large,
  frictionless bucket that absorbs anything. Instead, tasks are placed with
  the modality or paradigm that owns them, and the bare umbrella spellings go
  to *Non-Specific*.
- **`Information Theory`, `Monte Carlo Methods`, `Reproducibility` and
  `Computer Graphics` as their own nodes.** Each has 15–25 mentions but fewer
  than three distinct sub-areas in this corpus; rule 1's converse applies and
  they are absorbed (into *Statistical Learning Theory*, *Bayesian Inference*,
  *Benchmarking* and *Computer Vision* respectively).
- **A `Medicine and Biology` merge.** Health (~460) and Life Sciences (~330)
  are separated because the corpus separates them: `Pediatric Surgery`,
  `Brachytherapy` and `Shared Decision Making` share no methods and no
  questions with `Protein Structure Prediction` and `Single-cell
  Transcriptomics`.
- **Category names of the form "X and Y".** Every "and" I wanted was resolved
  by finding the containing concept (`Audio Processing` for speech + music;
  `Combinatorial Optimization` for discrete optimization + operations
  research; `Continual Learning` for continual + online + incremental) or by
  splitting (`AI Safety` vs `AI Governance`; `Dataset Construction` vs
  `Data Quality`).

### Branching factor (rule 6), declared rather than hidden

Three levels exceed the ~10 guideline: **Applied Research Domains (11)**,
**Learning Paradigms (9)** and **Trustworthy Machine Learning (9)**. In each
case the alternative was an intermediate node whose name would have been too
general to repel anything — "Health and Life Sciences", "Supervision Regimes",
"Responsible AI Concerns" — and rule 2 (a name must repel what does not
belong) is a binding constraint while rule 6 is explicitly a soft heuristic.
The eleven applied fields are eleven real communities; the nine trust
properties have nine distinct venues. I would rather defend a wide level than a
vague node.

---

## 4. Tail coverage (rule 8)

Thirty names were sampled at random from the 1489 one-paper names (seed
20260925) and placed by the rules above.

**Result: 1 of 30 had no obvious home.**

- `Action State Tracking` — the name is opaque without the paper. It is a
  dialogue-state-tracking variant (→ *Natural Language Processing*), but a
  careful annotator reading only the name would plausibly route it to
  *Reinforcement Learning* on the words "action" and "state". This is a
  failure of the name, not of the structure, but it counts.

One further name, `Interdisciplinary - Other`, is placed in *Non-Specific
Research Labels* by design — that is the category doing its job, and I count it
as placed.

Six more were placed but were genuine judgement calls that the precedence rule,
not intuition, decided: `Motion Generation` (→ Computer Vision, over Deep
Generative Modelling), `Radiolysis` (→ Health Research/medical physics, over
Physical Sciences), `Environmental Justice` (→ Environmental Science, over AI
Governance), `Code Search` (→ Software Engineering, over Information
Retrieval), `Semi-Supervised Node Classification` (→ Graph Machine Learning,
over Learning with Limited Supervision), `Safe Reinforcement Learning`
(→ Reinforcement Learning, by the named exception).

The remaining 23 were unambiguous: `Immunotherapy`, `Consistency Models`,
`Parameter-Efficient Training`, `Communication Systems`, `Radiogenomics`,
`Synthetic Biology`, `Evidence-Based Medicine`, `Object-Centric
Representations`, `Mathematics of Deep Learning`, `Building Energy Management
Systems`, `Patient Support in Oncology`, `Generalization Bounds`, `Accent
Classification`, `Hamiltonian Monte Carlo`, `Explainability in AI`, `Semantic
Textual Similarity`, `Text Data Augmentation`, `Transformer Networks`, `Network
Pruning`, `Reproducibility in Medical Imaging`, `3D Modeling and
Reconstruction`, `Disentangled Representations`, and `Interdisciplinary -
Other`.

---

## 5. The three calls I am least sure about

**1. Placing `Information Retrieval` under *Applied Research Domains* rather
than among the method families.** ~57 mentions — search, ranking, recommender
systems, entity matching, music and movie recommendation, digital advertising.
These are methods papers by content, and a reviewer could reasonably say they
belong beside *Modality-Specific Machine Learning*. I put them with *Software
Engineering* and *Human-Computer Interaction* because in *this* corpus the
names are overwhelmingly product-facing, and because the precedence rule then
sends `Code Search` and `Cross-lingual Information Retrieval` somewhere
defensible. If the other two proposals both place IR among methods, move it;
nothing else in the structure depends on it.

**2. `Anomaly Detection` under *Trustworthy Machine Learning*.** ~30 mentions.
Out-of-distribution detection, outlier detection and novelty detection are
trust questions; `Fraud Detection`, `Log-based Anomaly Detection` and
`Time-Series Anomaly Detection` are plain prediction tasks that happen to share
the machinery. The node has no good parent anywhere else — it is not a
modality, not a paradigm, not a domain — and promoting it to top level for 30
mentions felt worse. This is the placement I would change first.

**3. Domain-beats-everything in the precedence rule.** It is what makes
`Medical Imaging` (48 papers) count as health rather than vision, and
`Reproducibility in Medical Imaging` count as health rather than as evaluation
methodology. I believe it is right — the applied signal is the scarce one, and
compound names almost always co-occur on a paper with a bare method name that
carries the method count anyway — but I cannot verify the co-occurrence claim
from this file, which has no paper identifiers. If it turns out that papers
naming `Medical Imaging` do *not* also name `Computer Vision`, the vision count
is understated by up to 48 papers and the rule should be weakened for
imaging-modality compounds specifically.
