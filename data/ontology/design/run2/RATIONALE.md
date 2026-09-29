# Rationale — base category structure for ML research topics

**12 top-level groupings, 90 categories total (12 top-level + 78 at depth 2).**
All 270 `example_children` entries are verbatim names from `domain_names.tsv`.

---

## 1. The structural question: one tree, not several axes

**One tree.** A single mutually exclusive classification of extracted *names*,
with `axis = topic` on every row.

The argument is about the unit of assignment. The brief says an agent will
assign *every extracted name* to exactly one category per axis. A name is a
single concept, and in this corpus the overwhelming majority of names make
exactly one kind of claim. `Nephrology` names a field and is silent about
method. `Stochastic Mirror Descent` names a method and is silent about field.
`Speech Enhancement` names a task. If I define a method axis and an application
axis, the annotator is forced to produce a value on the axis the name does not
speak to. There are only two ways to do that, and both are worse than having no
axis at all:

- Emit "not specified" — and on the application axis that is roughly 70% of the
  vocabulary, which turns the headline table into a column of nulls; or
- Infer the missing value from the paper's text — which means the method counts
  stop measuring *what papers say they study* and start measuring what a model
  guessed, silently and unevenly. This is the exact failure mode rule 2 warns
  about, and it is undetectable in the output.

The usual reason to want axes — "a paper is RL *and* healthcare, one label
loses that" — does not apply here, because the classified object is the name,
not the paper. The corpus has 5990 name-mentions over 1999 papers, about three
names per paper. A paper about RL for clinical decisions already contributes a
name to `Reinforcement Learning` and a name to `Clinical Medicine`. The
cross-tabulation falls out of the paper→names join for free. Adding axes would
recompute at the name level what the corpus already encodes at the paper level,
and would double-count while doing it.

**What one tree costs, stated plainly.** Three things:

1. **The top-level row is not a pie.** `Trustworthy Machine Learning` and
   `Biomedical Sciences` are not competing slices of one quantity; one is a kind
   of ML question, the other a subject matter. The top level of this proposal is
   deliberately typed — branches 1–7 are *what ML question*, branches 8–12 are
   *what the work is about* — and the report must present them as two tables,
   never one ranked list. I chose to make that typing visible in the tree rather
   than to encode it as an axis mechanism that forces nulls.
2. **Compound names lose their second aspect.** `Machine Learning for Materials
   Science` is filed under `Materials Science` and its ML content is not
   counted. The head rule below makes this consistent, but it is a real loss.
   About 130 names in the corpus are of the form *method* + for/in + *field*.
3. **Per-paper "how much of our work is applied?" needs the join.** A two-axis
   design would answer it from the name table alone.

I take those costs because the alternative corrupts the counts rather than
merely coarsening them.

### The head rule (needed by any single tree, stated once)

A compound name is classified by its **head**: the noun phrase it modifies, not
the modifier.

- `Machine Learning for Climate Science` → Climate Science (head = the science).
- `Graph-based Change Point Detection` → the detection task, unless the name
  commits to graphs as the data (`Graph Anomaly Detection` → Graph ML).
- `Medical Image Segmentation` → Medical Imaging: when a modality is paired with
  a science, the **science wins**. This is a deliberate, contestable choice. An
  institute survey is read to find out how much clinical, biological and
  physical-science work is being done; filing every medical image under Computer
  Vision would hide precisely that.
- When the specific term and a generic term are combined
  (`Machine Learning and Optimization`), the specific term wins; `Machine
  Learning` on its own is an umbrella label and carries no weight.

---

## 2. Judgement call: model architectures

**In scope as research topics, but split by how the name is being used, and one
category is flagged for the double-counting problem.**

- A name the field uses as **the name of a research area** is classified as that
  area even when the phrase is architectural. `Graph Neural Networks` (76
  papers, 8th most frequent name) is how this corpus says "graph machine
  learning"; `Generative Models` (83 papers) is how it says "generative
  modelling"; `Diffusion Models` and `Normalizing Flows` are how it names
  sub-literatures of that. These go to `Graph Machine Learning` and
  `Generative Modeling`.
- A name about **designing or selecting architecture itself** — `Attention
  Mechanisms`, `Neural Architecture Search`, `Mixture of Experts`,
  `Hypernetworks`, `Equivariant Neural Networks`, `State Space Models` — goes to
  the single category `Neural Architecture Design`.
- Bare `Deep Learning` / `Neural Networks` are umbrella labels (branch 1).

On double counting: the risk is real but it is not solved by excluding
architectures, which would blow a 160-paper hole in the vocabulary and violate
rule 8. It is solved by *isolation*. `Neural Architecture Design` (~50
paper-mentions) is the only category in this proposal whose members are
architectures-as-architectures, so it is the only one that overlaps the
project's separate architecture ontology. Report it flagged, and never sum the
two surveys: they answer different questions ("what is studied" vs "what is
built with").

---

## 3. What I deliberately excluded or refused to do

- **A balanced structure.** `Reinforcement Learning` holds ~380 paper-mentions
  and `Agricultural Science` holds ~6. Both stay. `Clinical Medicine` alone has
  a deeper one-paper tail (~200 names) than five other branches combined; it is
  not split to make the table look even.
- **A "Deep Learning" or "Machine Learning" category.** The two most frequent
  names in the corpus — `Machine Learning` (249) and `Deep Learning` (177) —
  carry no information. Filing them in a substantive branch would instantly
  make that branch the largest area in the report for no reason. Branch 1,
  `Field-Level Umbrella Labels`, quarantines them: **501 of 5990 paper-mentions
  (8.4%)**. Report it as a line, then exclude it from the area shares. I expect
  this to be the biggest structural difference between my proposal and the other
  two, and I think it is the highest-value decision in the task.
- **A "Large Language Models" top-level branch.** Tempting in 2024, but the
  corpus splits LLM work cleanly between language tasks (→ NLP) and
  modality-agnostic steering techniques (→ `Foundation Model Adaptation`).
  A third home would have taken members from both.
- **A separate `Meta-Learning` category** (26 papers). The corpus contains only
  two other meta-* names, so it fails the three-example test; it is folded into
  `Transfer Learning`.
- **An `Information Theory` category.** ~8 names; folded into `Learning Theory`.
- **A generic `Other` branch.** The only residual is `Non-Specific Research
  Descriptors` (`Algorithms`, `Theory`, `Empirical Study`,
  `Interdisciplinary Studies`): **31 of 5990 paper-mentions, 0.52%**.

---

## 4. Tail coverage (rule 8)

Thirty names sampled at random from the 1489 one-paper tail (seeded `shuf`).
Quotes were consulted only for the ten that were not immediately obvious.

**Two of thirty had no obvious home on the first pass.** Both were repaired, and
the repairs are in the proposal:

| name | outcome |
|---|---|
| `Dynamic Learning` | no home. Quote is about weighting in a dynamic matching problem. **Added `Online Learning`** to branch 2, which also rescued `Concept Drift`, `Performative Prediction`, `Streaming SGD` and `Sequential Learning`. |
| `Air Pollution` / `Fire Monitoring` | no home under a narrow `Remote Sensing`. **Widened that category to `Environmental Monitoring`.** |

**One remains genuinely ambiguous after the repairs:** `AI System Integration`
(quote: deploying AI models in health care) splits between `Health Informatics`
and `Responsible AI` and I cannot make it obvious with a scope line. So the
honest post-repair figure is **1 of 30 without an obvious home (3%)**.

Four more needed the head rule or the quote to resolve but then resolved
cleanly: `Machine Learning and Optimization`, `Locomotion`,
`Graph-based Change Point Detection`, `Model Selection Strategies`. That is the
rule working, not the rule failing — but it means the head rule has to ship with
the structure, not as an appendix.

---

## 5. The three calls I am least sure about

1. **Splitting `Biomedical Sciences` out as a top-level branch while
   `Astrophysics` sits at depth 2 under `Physical Sciences`.** This looks like a
   frequency-driven asymmetry, which rule 4 forbids. My justification is
   internal differentiation, not size: biomedicine in this corpus has nine
   sub-areas that are separately named dozens of times each (clinical medicine,
   medical imaging, medical physics, neuroscience, computational biology, drug
   discovery, public health, health informatics), whereas the physical sciences
   have four, each with 15–25 mentions. Since depth 2 is the reportable level,
   nesting biomedicine one level deeper would push its sub-areas to depth 3 and
   hide the survey's single largest applied signal. A reviewer who weights rule 4
   more heavily than reportability should collapse branches 8–10 into one
   `Natural Sciences` branch and accept the loss of resolution.

2. **The `Neural Network Training` / `Optimization Algorithms` seam.** I split
   "practice" from "proof": `Neural Network Optimization`, `Training Dynamics`,
   `Loss Landscape Analysis` on one side; `Convex Optimization`, `First-Order
   Methods`, convergence rates on the other. The corpus does not respect this —
   `Optimization in Deep Learning`, `Optimization for Machine Learning` and
   `Adaptive Gradient Methods` could go either way, and the rule I wrote ("if
   the name mentions a network or a training run, it lands in Deep Learning
   Methodology") is a convention, not a discovery. Roughly 40 paper-mentions
   move depending on which way you decide. If the other proposals put all
   optimization in one place, they are probably right and I am over-splitting.

3. **`Information Retrieval` placed under `Data-Modality Subfields`.** IR and
   recommendation (19 + 16 papers) are individuated by a task shape, not by a
   data type, so they sit awkwardly beside NLP and Computer Vision. The
   alternatives were worse: a top-level branch of its own (a 13th branch with
   one real member) or `Applied Engineering Domains` (which would make it an
   industry, not a research field). I would accept being overruled here.

Two more that nearly made the list, recorded so a disagreement can be traced:
placing `Control Theory` under foundations rather than engineering (~40
mentions), and placing `RLHF` under `Foundation Model Adaptation` rather than
`Reinforcement Learning` (~8 mentions).

---

## 6. Branching factor (rule 6)

Twelve top-level groupings exceeds the ~10 guideline and I am not hiding it.
The justification is that they are two lists, not one: **seven ML-question
branches** (umbrella labels, learning problem formulations, data-modality
subfields, deep learning methodology, formal foundations, trustworthy ML,
experimental methodology) and **five subject-matter branches** (biomedical,
physical, environmental, applied engineering, social). Within each list the
branching is 7 and 5. The alternative — one `Application Domains` super-branch —
would have put `Neuroscience`, `Clinical Medicine` and `Software Engineering` at
depth 3, below the deliverable depth, which defeats the instrument.

Two branches sit at the per-level limit for a reason worth stating:
`Learning Problem Formulations` has 10 children and `Trustworthy Machine
Learning` and `Biomedical Sciences` have 9. In each case every child is a name
the corpus uses at least a dozen times, none subsumes another, and I could not
find a middle level that was a real family rather than an invented one. The
three-child branch (`Experimental Methodology`) is equally deliberate: the
corpus genuinely does not subdivide further there.
