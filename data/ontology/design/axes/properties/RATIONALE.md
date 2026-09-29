# Desired properties axis: depth-2 derivation

Derived 2026-09-25 from `AXES.md` §2 (authoritative), `TAIL_VALIDATION.md` F9,
and `domain_names.tsv` (2055 names, 6123 mentions, 1999 papers).

## 1. The delivered tree

```
Trustworthy AI            296 mentions   (38 umbrella + 258 in children)
  Fairness                 67
  Privacy                  27
  Robustness               73
  Safety                   20
  Explainability           58
  Accountability           13
Frugal AI                  27 mentions   (6 umbrella + 21 in children)
  Computational cost       12
  Energy cost               3
  Hardware cost             6
Uninformative               0            (administrative, §8b)
```

Axis total **323 mentions / 5.3% of the vocabulary's mentions**. This is an
optional axis; most papers have no value on it, per §1.

### Branching factor

6 and 3, mean 4.5, max 6. Justified: Method carries 6 level-1 aspects and
Modality 8 branches, so 6 is inside the schema's own precedent, and every one
of the six is separated by the same single characteristic (below), not by
convenience. The alternative shapes were worse. Merging Fairness+Safety, or
Explainability+Accountability, would produce exactly the compound nodes §9
bans. Splitting Robustness into robustness-vs-security would raise the factor
to 7 while handing the split's biggest surface (`Adversarial Robustness`, head
noun *robustness*) to the wrong side under the §8b head-noun rule.

### The characteristic at each level, stated explicitly

This axis has failed twice by mixing principles, so each sibling set divides by
exactly one:

- **Level 1** — *which kind of external demand*: how the system must treat the
  world and the people in it (Trustworthy) vs what it may consume (Frugal).
- **Level 2 under Trustworthy AI** — *which mode of trust failure the work
  forestalls*. Not "which kind of property": that is what produced the earlier
  four-principle mixture (normative fairness + epistemic reliability + resource
  efficiency + the *activity* of evaluation). Failure-mode is one axis of
  division and it is exhaustive over the six: the system disadvantages a group
  (Fairness), leaks a data subject (Privacy), breaks off-distribution
  (Robustness), acts harmfully while working as built (Safety), cannot be
  scrutinised (Explainability), cannot be held to account (Accountability).
- **Level 2 under Frugal AI** — *which resource is economised*: compute, energy,
  hardware.

A consequence worth recording: **attacks are filed by the property they break,
not by being attacks.** Membership inference and reconstruction are Privacy;
poisoning and adversarial examples are Robustness; jailbreaks are Safety. This
is what keeps the failure-mode characteristic single, and it is why no
"Security" sibling is needed.

## 2. Forced by AXES.md vs. my judgement

**Forced.** The two level-1 branches; and §2's table names the level-2 children
outright: fairness, privacy, robustness/adversarial, safety, interpretability &
explainability, accountability & governance | compute & time, energy & carbon,
hardware/edge. All nine delivered nodes descend from that list. The
`uninformative` row is forced by §8b.

**Mine.**
1. **Naming.** Every one of §2's children is written as a compound
   (`interpretability & explainability`, `accountability & governance`,
   `compute & time cost`, `energy & carbon`, `hardware/edge efficiency`), which
   §9 bans for nodes. I renamed all of them to single concepts — Explainability,
   Accountability, Computational cost, Energy cost, Hardware cost — and pushed
   the second half of each compound down to depth 3 or into the characteristic.
   `robustness/adversarial` became **Robustness** with adversarial robustness as
   a depth-3 child.
2. **Declining the robustness/security split** (§5.1 below).
3. **Declining a Reliability & uncertainty node** (§5.2). The single biggest
   judgement call on this axis.
4. **Splitting interpretability** between this axis and Method (§4).
5. **The name-level technique rule** (§3), which AXES.md needs and lacks.
6. Alignment as depth-3 under Safety rather than a seventh sibling.
7. Communication cost as depth-3 under Computational cost rather than a fourth
   resource.

## 3. Where AXES.md is silent, ambiguous or self-contradictory

This is the most valuable section; six defects, in descending order of how much
rides on them.

**D-P1 (blocking). No name-level rule for technique names, only a paper-level
one.** §2 says "A quantization paper gets Method = Quantization *and*, when its
point is energy cost, Desired property = Frugal AI." But the deliverable of the
mapping pass is a **surface map: name → node, per axis**. "When its point is
energy cost" is a property of a *paper*, not of the string `Quantization`, and
no annotator holding a name list can evaluate it. Left unfixed, every mapper
improvises, and the axis either absorbs all 33 compression mentions or none.

*Rule derived here, which I applied:* **a technique name maps onto this axis
only when the technique has no purpose other than securing the property.**
`Differential Privacy` passes (you do not use DP for accuracy) → Privacy.
`Adversarial Training`, `Safe Reinforcement Learning`, `Risk-Averse RL` pass.
`Quantization`, `Model Pruning`, `Knowledge Distillation`, `Model Compression`
**fail** — you quantize for latency, for memory, or to study lottery tickets —
so they stay Method-only at name level and reach Frugal AI only if the
extraction is later asked for the motivation. This is the whole of the 296 vs
27 asymmetry: see D-P2.

**D-P2. §2's corpus estimates are inconsistent with the vocabulary.**
§2 gives Trustworthy ~300 / Frugal ~85. Trustworthy measures at **296** — an
excellent match. Frugal measures at **27**. The ~58-mention gap is
compression/pruning/distillation/quantization (33 mentions, which §3 and F1
assign to Method) plus, presumably, the sample- and parameter-efficiency names
that §2's own scope rule excludes two paragraphs later. So §2's Frugal figure
double-counts against its own rulings. The true ratio on demand-register names
is **~11:1, not ~3.5:1**. Per rule 9 this is reported, not repaired: Frugal AI
is delivered with three children and 27 mentions.

**D-P3. §2 calls the axis "normative" but its own test is about exogeneity.**
The F9 paragraph concludes the line "keeps the axis normative and small rather
than admitting an epistemic sub-branch." But the test it actually states is
*"demands made on the research from outside it"*. These are different
predicates, and they disagree on exactly one node: explainability, which is
epistemic in content and exogenous in demand (§4). AXES.md then lists
interpretability as a child anyway — so the file contradicts its own gloss. The
operative word must be **exogenous**; "normative" is the wrong summary and
should be struck.

**D-P4. §8b's uninformative branch assumes a mandatory axis.** It says "every
axis gets its own uninformative branch", built from examples like
`Predictive Modeling` and `Computing Research`. On an *optional* axis those
names are **off-axis** — they assert no demand, so they get no value, which §1
says is a finding, not a gap. The genuinely vague-but-on-axis surfaces
(`Responsible AI`, `Efficient Deep Learning`) are absorbed by the two branch
nodes as umbrellas under the §8b nearest-common-parent rule. The branch is
therefore delivered **empty**, and §8b should distinguish *no value* from
*uninformative value* before the mapping run.

**D-P5. The "ethics" cluster is unaddressed.** ~28 mentions of `AI Ethics`,
`Ethics in AI`, `Responsible AI`, `Ethical AI`, `FAccT` — the third-largest
concentration on the axis — appear nowhere in §2. They are not a child of
anything: they are umbrella names for the whole Trustworthy branch. §7 already
solved this shape (`Bioinformatics`/`Computational Biology` are surfaces of the
Life sciences *branch node*), and §8b's compound rule points the same way, but
neither is cited in §2. Applied here: they map to `trustworthy-ai` itself.
Note the near-miss — `Ethics` is not an adjective on AI and would fail §2's
naming test read literally, while `Ethical AI` passes; the naming test is a
heuristic for identifying the *category*, not a filter on surfaces.

**D-P6. Homonyms this axis must declare, beyond §8b's list.** §8b flags
`Robustness` (three axes) and `Policy Evaluation`. Three more bite here:
- **`bias`** — fairness sense (this axis) vs estimator/inductive sense (Method).
  `Inductive Biases` and `Dataset Bias` are one word apart and different axes.
- **`security`** — see §6.
- **`alignment`** — AI alignment (Safety) vs `Multimodal Alignment`,
  `Vision-Language Alignment`, `Ontology Alignment`, `Multiple Sequence
  Alignment` (Task/Modality/Application). Four of the six `alignment` surfaces
  in the corpus are not safety.
- minor: **`efficiency`** — resource sense (Frugal) vs sample/parameter sense
  (excluded by §2), and `Communication Efficiency` vs communication *systems*.

## 4. Interpretability: normative or epistemic, and does it belong here?

**Verdict: it belongs here, but the corpus term splits, and AXES.md's stated
reason for keeping it is the wrong one.**

The property is **epistemic in content**. "Can a human follow why this model
produced this output?" is a claim about knowledge, not about a wrong done. On a
normative/epistemic sort, interpretability lands with generalization and
expressivity — outside this axis. That is the strongest argument against it and
§2's word "normative" endorses it, which is defect D-P3.

But test 2 as *written* sorts by **where the demand originates**, and on that
test interpretability separates cleanly from generalization:

| | who demands it | consequence of failure |
|---|---|---|
| compositional generalization | the field, of itself | a research question stays open |
| explanation | a regulator, a clinician, a loan applicant, an auditor | a deployment is impermissible |

Nobody outside the field demands compositional generalization — §2's own
sentence. People outside the field demand explanations *constantly*, in
statute. And the naming test is decisive in the same direction: `Explainable AI`
is the canonical `<Adjective> AI` term, more so than any other surface on this
axis. Two of the three defining tests pass at full strength; the third
(normativity) is not one of the three tests, it is a gloss.

**Therefore the sort that matters is exogenous/endogenous, not
normative/epistemic** — and the axis does admit epistemic properties, provided
the demand comes from outside. Saying so out loud is necessary, because the
unspoken "normative" framing is what will otherwise be used to smuggle the
whole reliability cluster back in (§5.2 explains why it still does not get in).

The price is a split the corpus makes visible:

- `Explainable AI` 10, `Interpretable Machine Learning` 9, `Model
  Interpretability` 7, `Interpretability` 6, `Explainability` 4 … → **here**.
  Someone is owed an account.
- `Mechanistic Interpretability` 2, `Model Understanding and Mechanistic
  Interpretability` 1, `Automated Interpretability Methods` 1 → **Method >
  Model design & analysis**. Circuit-level reverse-engineering asks what
  networks compute; no outside party is owed the answer. This is the same cut
  F9 made on OOD, applied one node over.

Residual risk, stated: `Interpretable Machine Learning` and `Interpretable
Models` could be read as naming a technique family (glass-box models) rather
than the demand, which under D-P1's rule would send them to Method and cost
this node 11 of its 58 mentions. I read them as the research area named by its
goal. Flag for the ambiguity probe.

## 5. The two splits I declined

### 5.1 Robustness vs Security

Conceptually real — the world changing is not the same failure as someone
attacking. Declined because: (a) `Robustness & adversarial security` is a banned
compound and the honest split names would be `Robustness` and `Security`, which
collides head-on with Application > Computer security (§6); (b) the dominant
surface `Adversarial Robustness` 10 has head noun *robustness*, so §8b's
mechanical rule sends the flagship adversarial name to the robustness side and
leaves Security with ~4 mentions; (c) the attacks-by-broken-property rule (§1)
already distributes attack names correctly without a security node. Revisit if
LLM red-teaming/jailbreak names appear at volume — the corpus has none in 2024.

### 5.2 Reliability & uncertainty — the closest call on this axis

`Uncertainty Estimation` 12, `Uncertainty Quantification` 5, `Model
Calibration` 2, `Uncertainty Characterization` 2, `Conformal Prediction` 1,
`Neural Network Verification` 5 and ~6 more: **~34 mentions**, larger than
Accountability, with no home on this axis. A deployer plainly does demand that
a system know when it does not know, so test 1 and arguably test 2 pass.

Declined, on a rule this derivation had to invent and now states for reuse:

> **A property node requires a demand-register surface, not only a
> machinery-register one.**

`Reliable AI` / `Dependable AI` / `Trustworthy prediction` occur **zero** times
in the corpus. What occurs is the machinery: estimation, quantification,
calibration, conformal prediction, verification — which §3 already routes to
Method > Inference & optimization (with Bayesian inference, variational, MCMC)
and §5 already routes `Neural Network Verification` to Method > Model design &
analysis. Admitting a Reliability node would therefore not record a demand; it
would import ~34 mentions of Method machinery into a normative axis, which is
precisely the absorption failure this axis has suffered twice. Compare
Robustness, which has `Model Robustness` 7, `Robustness` 2, `Robustness in
Machine Learning` 1, `Certified Robustness` 1 — a genuine demand register.

This is the node most likely to be right later and wrong now. Flag it for
re-derivation if the extraction is ever asked about deployment requirements.

## 6. The Computer security collision

Application's node is deliberately `Computer security`, not "Security &
privacy", to avoid attracting ~40 mentions of privacy-of-ML. The boundary:

> **Who is the victim — a computer system that ML is defending, or the ML
> system itself?**

This is the reflexive test of §2 applied to one word. Computer security exists
without AI and supplies problems (intrusion, malware, IoT, IaC) to which ML is
the machinery → **Application**. When the ML model is what is attacked, the
work is securing a property *of the AI system* → **this axis**, and then split
by the property broken: confidentiality → Privacy, integrity/availability →
Robustness.

Adjudicated surfaces:

| surface | m | axis | why |
|---|---|---|---|
| `Adversarial Machine Learning` | 13 | Properties > Robustness | the model is the target |
| `Machine Learning Security` | 3 | Properties > Robustness | ditto, said plainly |
| `Membership Inference Attacks` | 1 | Properties > Privacy | confidentiality of training data |
| `Reconstruction Attacks` | 1 | Properties > Privacy | ditto |
| `Data Poisoning` | 1 | Properties > Robustness | training-set integrity |
| `Cybersecurity` | 3 | Application > Computer security | the field |
| `IoT Security` | 1 | Application | the victim is a device fleet |
| `Security in Infrastructure as Code` | 1 | Application | the victim is a deployment pipeline |
| `Security`, `Security Analysis` | 2 | Application | bare field names |
| `Security and Privacy` | 1 | Application | compound *surface*; the pairing is the CS-field idiom (the S&P/SIGSAC register), and §8b maps a compound to the nearest common parent — which for "the security field and the privacy field" is Computer security, not this axis. Flag for the ambiguity probe |

Net: ~18 mentions to this axis, ~9 to Application. The naming choice works; the
one genuine straddle is `Security and Privacy`.

## 7. Blind spots — kept regardless of count

Per rule 9, a category with no corpus support is *possibly speculative, justify
or keep*.

- **Energy cost: 3 mentions** (`Green AI` 2, `Energy Efficiency` 1). Kept. §2
  builds the entire case for a separate properties axis on the Green-AI /
  energy-sector collision, and the owner calls Frugal AI strategically
  important and expects growth. Deleting the node for thinness would delete the
  axis's own founding example.
- **Hardware cost: 6 mentions**, and `TinyML`, `On-device learning`, `Model
  serving cost` occur **zero** times. Kept for the same reason.
- **Accountability: 13 mentions**, and `Model Cards`, `Algorithmic Auditing`,
  `Provenance`, `Watermarking` occur zero times. Kept: it is the only node
  carrying the institutional demand, and its absence from a 2024 Canadian ML
  institute's output is itself a publishable line.
- **Safety: 20 mentions**, with no jailbreak/red-teaming/guardrail/hallucination
  surfaces at all in 2024. Kept, and the gap is a finding about the corpus's
  frontier-LLM-safety share, not about the node.
- Absent entirely and *not* added: copyright/provenance of training data,
  environmental justice of datacentres, labour conditions of annotation. Zero
  surfaces, and inventing nodes with no semantics to anchor them is the run1
  failure mode.

## 8. Every corpus name rejected to another axis

Grouped by the test that rejected it. (m = mentions.)

**Rejected by test 2 — endogenous, a question the field asks of its own
machinery → Method (F9):** `Out-of-Distribution Generalization` 5, `Domain
Generalization` 4, `Generalization` 3, `Generalization Performance` 2,
`Generalization Bounds` 1, `Generalization in Deep Learning` 1, `Generalization
in Neural Networks` 1, `Generalization in RL` 1, `Hyperparameter
Generalization` 1, `Compositional Generalization` 1, `Systematic
Generalization` 1, `Worst-Group Generalization` 1, `Time Series OOD
Generalization` 1, `Goal Misgeneralization` 1 (head noun decides, though the
concept is alignment — flagged), `Scaling Laws` 1, `Deep Learning Scaling Laws`
1, `Sample Complexity`, `Covariate Shift` 1, `Data Shift` 1, `Label
Distribution Shift` 1, `Sub-population Shift` 1, `Catastrophic Forgetting` 6
(continual-learning phenomenon), `Empirical Risk Minimization` 1. **~36.**

**Rejected by test 2 — machinery, no demand-register surface (§5.2):**
`Uncertainty Estimation` 12, `Uncertainty Quantification` 5, `Neural Network
Verification` 5, `Model Calibration` 2, `Uncertainty Characterization` 2,
`Calibration and Uncertainty Estimation` 1, `Model Uncertainty` 1, `Conformal
Prediction` 1, `Planning with Uncertainty` 1, `Uncertainty Estimation in Deep
Learning` 1, `Uncertainty Estimation in Generative Models` 1, `Robustness
Verification` → kept (robustness register), `Quantitative Verification` 1,
`Program Verification` 1, `Software Verification` 1. **~34.**

**Rejected by the method rule (D-P1) — technique whose purpose is ambiguous →
Method only:** `Model Compression` 9, `Knowledge Distillation` 8, `Model
Pruning` 7, `Neural Network Pruning` 5, `Quantization` 4, `Network Compression`
1, `Neural Network Compression` 1, `Network Pruning` 1, `Pruning` 1, `Model
Quantization` 1, `Model Distillation` 1, `Model Compression and Sparse
Training` 1, `Network Sparsity` 1, `Image Compression` 1 (data, not model —
§8b homonym), `Compression Algorithms` 1 (declared homonym). **~43**, of which
~33 would reach Frugal AI with paper-level motivation evidence.

**Rejected by §2's explicit Frugal scope rule (data/parameters are not
resources):** `Sample Efficiency` 1, `Sample-efficient Reinforcement Learning`
1, `Data Efficiency` 1, `Parameter-Efficient Fine-Tuning (PEFT)` 1,
`Parameter-efficient Learning` 1, `Parameter-Efficient Training` 1,
`Cost-sensitive Learning` 1 (loss weighting, not budget), `Low-Resource
Languages` 1 (→ Modality/Application). **8.**

**Rejected by the reflexive test — the object of study is not the AI system →
Application:** `Cybersecurity` 3, `Human-Centered Computing` 3, `Medical
Ethics` 2, `Climate Science` 2, `Climate Change Impact` 2, `Energy Systems` 2,
`Environmental Monitoring` 4, `Neuroethics` 1, `Surgical Ethics` 1,
`Environmental Justice` 1, `Environmental Sustainability` 1, `Health Equity` 1,
`Healthcare Access` 1, `Accessibility` 1, `IoT Security` 1, `Security` 1,
`Security Analysis` 1, `Security in Infrastructure as Code` 1, `Security and
Privacy` 1, `Regulatory Science` 1, `Climate Governance` 1, `Health Policy` 1,
`Public Health Policy` 1, `Healthcare Policy Analysis` 1, `Public Policy
Analysis using AI` 1, `Policy Recommendations` 1, `Economic Policy Simulation`
1, `Renewable Energy Forecasting` 1, `Energy Storage` 1, `Thermal Energy
Storage` 1, `Energy Management` 1 + 3 building/robotics variants, `Energy
Prediction` 1 + 1, `Energy Market Modeling` 1, `Greenhouse Gas Emissions
Analysis` 1, `Aviation Emissions` 1, `Carbon Capture` 1 + 1 (CCUS), `Grid-Edge
Technologies` 1, `Fashion Sustainability` 1, `Ecology and Environment` 1 + 1,
`Environmental Engineering` 1, `Environmental Health` 1, `Environmental
Conservation` 1, `Environmental Science` 1, `Natural Environment` 1, `AI in
Environmental Engineering` 1, `Hardware Design` 1, `Hardware Description
Languages` 1, `Hardware Implementation of Algorithms` 1, `Functional
Programming for Hardware` 1, `Human Factors` 1, `Human Factors and Ergonomics`
1, `Software Reliability Engineering` 1, `Software Quality Analysis` 1,
`Toxicology` 2, `Pharmacology` 2, `Resource Allocation` 1, `Load Balancing and
Quality of Service` 1, `Child Welfare Systems` 1, `Social Welfare
Optimization` 1, `Societal Impacts and Adaptation` 1. **~75.** Note `AI Ethics
and Society` 1 and `ELSI` 1 are *not* here — their object is the AI system.

**Rejected by test 1 — the harm exists in the world and the system is asked to
find it → Task > Detection + Application:** `Misinformation Detection` 3,
`Toxicity Detection` 1, `Toxic Language Detection` 1, `Toxicity Detection in
Online Gaming` 1, `Human Trafficking Detection` 1. **7.** The demand behind
content moderation is real but it is a demand on a *platform*, not on the
model; only `Model Safety` names a demand on the model.

**Rejected by the head-noun rule (§8b) — names a method or training regime:**
`Federated Learning` 24 (privacy-motivated but names how training is organised
— the single largest near-miss on this axis), `Differential Privacy` → **kept**
(passes D-P1), `Robust Optimization` 3 + `Conditional Robust Optimization` 1
(machinery), `Generative Adversarial Networks` 7 + 7 (architecture, the
`adversarial` homonym), `Reinforcement Learning from Human Feedback` 1 + 1
(alignment machinery), `Adversarial Learning` 1 (ambiguous GAN/robustness —
flagged), `Value Learning` 1 (RL value functions, not human values — homonym),
`Moral Decision-Making` 1 (→ Application, cognitive science), `Data Auditing`
→ **kept** (Accountability), `Data Quality` 1 + `Data Quality and Metadata
Inference` 1 (→ Method > Data curation, F2), `Control` names (~40 mentions,
already split by §7's OR analogy). **~50.**

**Rejected by §8b as contribution type — mark_ignore on every axis:**
`Benchmarking` 7, `Empirical Analysis of Algorithms`, `Multimodal Model
Evaluation`, `Patient Decision Aids Evaluation`, `Impact Evaluation` 1, `Risk
Assessment` 1 (activity, not property — but `Model Risk Management` 1 is a
governance function and is kept). This is the class the earlier proposal
mis-filed as a *property*; it is not one, on any axis.

## 9. Is a third level-1 branch justified?

**No, and the fixed two-branch level 1 is delivered as the primary proposal.**
Three candidate principles were tested:

1. **Capability properties** (accuracy, generalization, expressivity). Fails
   test 2 outright — F9 already assigned them to Method.
2. **Usability / human-centeredness** ("the system must serve the person using
   it"). Passes tests 1 and 2 and has an `<Adjective> AI` surface
   (`Human-Centered AI` 1, `Accessibility` 1) — but 2 mentions, and its content
   is already claimed on one side by Application > Computing (HCI, 28+) and on
   the other by Explainability. Rejected as a branch; `Human-Centered AI` maps
   to the Trustworthy umbrella.
3. **Reliability & assurance** ("the system must behave predictably and be
   certifiable"). The only serious candidate, ~34 mentions, and it is rejected
   for the reason in §5.2 — no demand-register surface, so as a branch it would
   import Method machinery. It is *also* the branch that would be needed if the
   epistemic/exogenous line in §4 were ever redrawn, so the two questions
   should be reopened together or not at all.

A 2-wide level 1 is thin but legal (§9 requires ≥2 substantive children, which
is met), and thinness here is the honest shape of the field's own vocabulary:
the community names exactly two adjectives on AI at scale — trustworthy and
frugal — and one of them is ten times the other in this corpus.
