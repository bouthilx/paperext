# Desired properties, depth 3 — PHASE 1 DRAFT (semantic, no corpus access)

Written 2026-09-29, **before** `domain_names.tsv` was opened, before any tally,
and without consulting the `examples` column of level-2 rows as a seed
(§9 rule 1). This file is the record and is **never edited**. Every later change
is recorded as a diff in `DEPTH3_RATIONALE.md`, not here.

## Declared contamination, stated up front

The brief instructed me to read `nodes.tsv` and `RATIONALE.md` before phase 1,
for the parents' characteristics. Both files are corpus-laden: `nodes.tsv` is a
TSV so its `examples` and count columns are visible in any read of it, and
`RATIONALE.md` §4-§8 lists several hundred corpus surfaces with mentions. I could
not obtain the parents' characteristics without seeing them. I did not consult
either while drafting below, and I did not run any tally, open `domain_names.tsv`
or look at any name list. Where a draft child below coincides with a level-2
`examples` cell, that coincidence is declared child-by-child in
`DEPTH3_RATIONALE.md` §0 so the reader can discount it. This is a real weakness
of the procedure on this axis and I am reporting it rather than claiming a
cleanliness I cannot prove.

## What a depth-3 set on this axis has to do

Parent characteristics are fixed:

- Level 2 under **Trustworthy AI** divides by *which mode of trust failure the
  work forestalls*.
- Level 2 under **Frugal AI** divides by *which resource is economised*.

So a depth-3 set must **refine the same question one turn finer** — within this
mode of failure, which variety of that failure; within this resource, which
computation/quantity is paid for. It may not import another aspect's question
(mitigation stage, technique family, modality, application field, who the
protected group is). Three importing principles are rejected by name under every
node below.

Two further constraints applied throughout:

- **The property test** (AXES.md §6): a modifier that can be true of a node's
  siblings is a property, not a sibling. This is what kills `certified`,
  `local/global`, `near-term vs long-term` and `by protected attribute` as
  sibling sets.
- **Techniques stay on Method** unless the technique has no purpose other than
  securing the property. Children are named for the *demand*, never for the
  family of methods that serves it.

---

## Trustworthy AI > Robustness  — 3 children

**Characteristic (level 3): WHERE THE DEPARTURE COMES FROM — who or what
authors the disturbance the system fails on.** This refines the parent
literally: the parent's own positive test already says "whether the departure is
natural (shift, corruption, noise) or authored (adversarial example, poisoning,
backdoor)", and it distinguishes two places an author can act.

| child | the failure |
|---|---|
| **Adversarial robustness** | an adversary authors the *input* the deployed system sees: evasion, adversarial perturbation, patches, input-level attacks on a model that was trained honestly. |
| **Training-data integrity** | an adversary authors the *learning process*: poisoning, backdoors, trojans, a tampered checkpoint. The model appears normal and misbehaves on the attacker's trigger. |
| **Distribution-shift robustness** | nobody authored it. Deployment differs from training — new site, new population, new sensor, drift over time, corruption, noise — and the system silently stops working. |

**Negative tests.** Studying shift as a *phenomenon*, or asking what is provable
about generalizing off-distribution, is Method > Learning theory (the parent
already says so, F9); this child holds the deployment demand, not the theory.
Attacks are filed by the property they break, so an attack that extracts
training data is Privacy, not Adversarial robustness.

**Competing principles rejected.**
1. *By guarantee register* — empirical / certified / formally verified. This
   divides by **what is established about a model that already exists**, which
   is verbatim the characteristic of Method > Model analysis, and
   `Neural Network Verification` is already routed there. `certified` is also a
   modifier true of all three children (there is certified adversarial
   robustness and certified shift robustness), so the property test kills it.
2. *By perturbation geometry* — Lp-bounded / semantic / patch / physical. A
   taxonomy of threat models used by technique papers; machinery register.

**Note on the declined level-2 split.** RATIONALE §5.1 declined
Robustness-vs-Security at level 2 for three reasons, two of which were naming
accidents: `Robustness & adversarial security` is a banned compound, and the
§8b head-noun rule hands `Adversarial Robustness` to the robustness side. Both
evaporate one level down — `Adversarial robustness` is not a compound, keeps its
head noun, and does not collide with Application > Computer security. The
conceptual distinction §5.1 called "conceptually real" is recovered here without
reopening the level-2 decision.

---

## Trustworthy AI > Fairness — 3 children

**Characteristic (level 3): WHICH FORM THE INEQUALITY TAKES — what the claimant
alleges was distributed unequally, and across whom.**

| child | the failure |
|---|---|
| **Group fairness** | outcomes or error rates differ between demographic groups: disparate impact, demographic parity, equalized odds, performance gaps across a protected attribute. The comparison is between groups. |
| **Individual fairness** | two people alike in every relevant respect are treated differently, or the decision would flip if a protected attribute were changed. The comparison is between individuals, including counterfactually. |
| **Representational fairness** | nothing is allocated at all: the system's *depictions* of a group are demeaning, stereotyped, erased or systematically poorer — in generated text and images, in embeddings, in retrieved results. |

**Negative tests.** A statistical bias with no human claimant (estimator bias,
`Inductive Biases`, dataset shift) is Method — the parent's own negative test.
A disparity that exists in the world and is not produced by the system is
Application. A *technique* for reducing a disparity (reweighting, adversarial
debiasing, constrained ERM) is Method.

**Competing principles rejected.**
1. *By mitigation stage* — pre-processing / in-processing / post-processing.
   Forbidden explicitly: it is Method's question (how the result is produced),
   not the parent's (which mode of trust failure). It is also the single most
   common way this axis has absorbed Method in the past.
2. *By protected attribute* — gender / race / language / disability / age. It
   fragments without limit, it names social categories rather than modes of
   failure, and every attribute can be true of all three children, so the
   property test makes it a modifier.

**Declared strain (small).** `Group` and `Individual` divide by the *comparison*
that exposes the wrong; `Representational` divides by the *kind of good* at
stake (a depiction rather than a decision). I judge this one principle stated at
its natural level — "what was distributed unequally, and across whom" answers
both — but a reader who reads it as one-and-a-half principles is not being
unreasonable, and I declare it rather than hide it. The alternative, dropping
`Representational fairness`, loses the whole generative-model fairness
literature, which is the part of fairness that has grown fastest.

---

## Trustworthy AI > Explainability — 3 children

**Characteristic (level 3): WHAT THE OWED ACCOUNT IS ABOUT — the model, a single
output, or the affected person's own position with respect to it.**

| child | the failure |
|---|---|
| **Intrinsic interpretability** | the demand is that the model itself be legible, and no separate explanation is accepted as a substitute: rule lists, sparse and additive models, concept bottlenecks, the "do not explain black boxes in high-stakes settings" position. |
| **Post-hoc explanation** | the model stays opaque and an account of a *particular output* must be produced about it, for the professional acting on it. |
| **Recourse and contestability** | the affected person is owed an actionable reason and a route to challenge: what would have had to be different, how to appeal, the statutory right to an explanation of a decision made about you. |

**Negative tests.** Opening a model to answer a scientific question about how
networks compute, with no outside claimant, is Method > Model analysis
(`Mechanistic Interpretability` — the parent says so). A named attribution
technique (saliency, SHAP, probing, surrogate fitting) is Method. Transparency
as institutional disclosure or documentation is Accountability, not here — the
parent already states that split, and `Recourse` stays on this side because its
claimant is the individual, whereas Accountability's claimant is an institution.

**Competing principles rejected.**
1. *By explanation technique family* — attribution / example-based / surrogate /
   concept-based. Method > Model analysis's characteristic exactly.
2. *By scope* — local vs global. Scope is a property of the explanation
   artefact, and it cross-cuts: there are global post-hoc surrogates and local
   intrinsic rules. Property test → modifier, not sibling.

---

## Trustworthy AI > Privacy — 3 children

**Characteristic (level 3): WHICH OF THE DATA SUBJECT'S CLAIMS FAILS.**

| child | the failure |
|---|---|
| **Training-data confidentiality** | something about an individual training record is recoverable from what was released — the model, its outputs, or a dataset derived from it. Membership inference, memorization and verbatim regurgitation, reconstruction and model inversion, re-identification of a released or synthetic dataset, and the guarantee register that answers them. |
| **User-input confidentiality** | the exposure is at use, not at training: what a person gives a deployed system, and the fact they gave it, does not stay private. |
| **Data subject control** | nothing leaks, and the subject is still wronged: they cannot withdraw, limit or revoke the use of their data. Erasure and unlearning, consent, purpose limitation, data minimisation. |

**Negative tests.** The subject is a computer system being defended rather than a
data subject being exposed → Application > Computer security (parent's own
test). A training architecture chosen partly for privacy but not making a
privacy claim (`Federated Learning`) is Method > Training regime.

**Competing principles rejected.**
1. *By privacy mechanism* — differential privacy / cryptographic / federated /
   anonymisation. Method's question, and the mechanisms cross-cut the children.
2. *By attack versus defence*. That divides by **register**, not by failure
   mode, and it would put membership inference and DP in different children
   although they are the same claim seen from two sides. The axis's own rule —
   attacks are filed by the property they break — already forbids it.

---

## Trustworthy AI > Safety — 3 children

**Characteristic (level 3): WHAT THE SYSTEM GETS WRONG WHILE WORKING AS BUILT —
its objective, its actions, or its outputs.** The parent's positive test names
these three in order ("it pursues the wrong objective, takes an unacceptable
risk, or produces harmful output"); this set is that sentence made into nodes.

| child | the failure |
|---|---|
| **Alignment** | the objective is wrong. The system competently pursues something other than what was intended: specification gaming, reward hacking, goal misgeneralization, the problem of conveying human values into an objective at all. |
| **Safe control** | the objective is right and the behaviour en route is not. Hard constraints must hold during operation and during learning: safe reinforcement learning, safe exploration, risk-averse and risk-sensitive policies, catastrophic-action avoidance. |
| **Output safety** | the objective and the actions are beside the point; the emitted content itself harms its reader — harmful, dangerous or abusive generation, unsafe advice, and resistance to being talked into producing it (jailbreaks, guardrails). |

**Negative tests.** The harm exists in the world and the system is merely asked
to find it (`Misinformation Detection`, `Toxicity Detection`) → Task > Detection
+ Application; the parent says this and it is the boundary `Output safety` must
hold. Alignment *machinery* (RLHF, preference models) is Method > Learning
signal; `Alignment` here is the demand. `Safe control` declares the `control`
homonym: control theory and control engineering of a physical plant are Method
and Application respectively (§8b), and only the safety demand on the AI
system's own behaviour is here.

**Competing principles rejected.**
1. *By severity or time horizon* — near-term harms vs catastrophic/existential
   risk. This divides the safety *community*, not the system's mode of failure,
   and it cross-cuts all three children. Property test → modifier.
2. *By who is harmed* — user / bystander / society. That is Sector's and
   Application's claimant structure imported, and it also cross-cuts.

---

## Trustworthy AI > Accountability — 3 children

**Characteristic (level 3): WHICH PRECONDITION OF ANSWERABILITY IS MISSING.**
To hold a system to account an institution needs a rule to apply to it, a way to
inspect it, and a record of what it is. Each child is one of those failing.

| child | the failure |
|---|---|
| **Regulatory compliance** | there is no rule, or the system does not meet one: law, standards, conformity assessment, certification, liability, and the statutory requirement that a human remain able to oversee and intervene. |
| **Auditability** | there is a rule but no independent party can check it: third-party audit access, algorithmic auditing, impact assessment, evaluation the deployer cannot mark themselves. |
| **Traceability** | there is no record travelling with the system: model documentation and cards, dataset datasheets, training-data provenance and disclosure, logging, and provenance of generated content (watermarking, origin of an output). |

**Negative tests.** Governance of a non-AI subject (`Climate Governance`,
`Health Policy`) is Application — the parent says so. A research *activity*
(`Benchmarking`, `Multimodal Model Evaluation`) is `mark_ignore` on every axis;
`Auditability` is the demand that auditing be possible, never the activity of
evaluating. Homonym to declare: `Traceability` in software engineering means
requirements traceability and is Application > Computing.

**Competing principle rejected.** *By governance instrument* — law / standard /
voluntary code / internal policy. It divides by the **kind of rule-maker**, which
is a fact about the regulatory landscape and not a mode of failure of the
system; and instruments cross-cut (a model card is demanded by statute, by
standards and by internal policy alike).

**Fourth child considered and not created: `Human oversight`.** The EU AI Act
treats meaningful human control as its own requirement, and under this
characteristic it would be a fourth missing precondition — no responsible human
in the loop. I place it inside `Regulatory compliance`'s positive test instead,
for two reasons: as a node it would collide with Safety (intervention to prevent
harm) and with Application > HCI, and `Human-in-the-loop` is predominantly a
Method surface (active and interactive learning), so a node by that name would
attract out-of-scope entries, which §9 forbids. It is the likeliest fourth child
if oversight language arrives at volume.

---

## Frugal AI > Computational cost — 3 children

**Characteristic (level 3): WHICH COMPUTATION IS PAID FOR** — a straight
refinement of the parent's "which resource is economised", one turn finer.
Each child has a different payer.

| child | the budget |
|---|---|
| **Training compute** | the one-off cost of producing the model: FLOPs, GPU-hours, wall-clock time to train, the size of a training run. Payer: whoever funds the run. |
| **Inference cost** | the recurring cost of each use: latency, throughput, serving cost, memory at serving time, test-time compute. Payer: whoever operates the deployment, per query. |
| **Communication cost** | the cost of moving data between the machines doing the computing: bandwidth and round-trips in distributed and federated training. Payer: the network. Forced by the parent's own note, which already files communication cost as depth 3 rather than a fourth resource. |

**Negative tests.** The economised quantity is data or parameters → excluded from
the branch by AXES.md §2. `Distributed Training` and `Federated Learning` name
how training is organised → Method > Training regime; only a cost claim about
them lands here. The budget is electricity or emissions → Energy cost; the
physical device → Hardware cost.

**Competing principle rejected.** *By the metric used* — FLOPs / wall-clock /
memory / parameters. That divides by **how the cost is counted**, not by which
cost is incurred, and every metric can be applied to all three children.
Property test → modifier.

**Declared strain (small).** Training-vs-inference can be read as a division by
*stage*, which is defect M5 on the Method axis. I claim it is not: these are two
distinct budgets with two distinct payers and different units (one-off
GPU-hours vs cost per query), which is the parent's own "which resource"
question, not "when the computation happens". Declared so a reader can disagree.

---

## Frugal AI > Energy cost — 2 children

**Characteristic (level 3): WHICH QUANTITY IS BUDGETED — the energy drawn, or
the emissions it causes.** These are not the same number and they do not have
the same claimant: the same joules carry different carbon depending on the grid,
the location and the hour.

| child | the budget |
|---|---|
| **Energy consumption** | joules and watts drawn by training or serving; energy-aware training and serving; measuring and reporting the power a run costs. Claimant: the operator paying the bill, and the device. |
| **Carbon footprint** | CO2e emitted, and what can be done about it independently of joules — carbon-aware scheduling, location and time shifting, carbon accounting and reporting for models. Claimant: a climate target, a regulator, a disclosure regime. |

**Negative test.** The paper applies ML to an energy or climate problem — the
object of study is a power grid, not an AI system — → Application. This is the
axis's founding collision and this node's boundary must hold it.

**Both children are flagged speculative in advance**: the parent node carries
very little, and it is kept on semantics, per rule 9 — AXES.md §2 builds the
entire case for a separate properties axis on the Green-AI / energy-sector
collision.

**Third child considered and not created: `Lifecycle and embodied footprint`**
(hardware manufacture, datacenter water, e-waste). The demand is real and
growing, but it sits one step from Application > environment, and the reflexive
test — is the object of study an AI system? — gets genuinely hard when the
object is a building. Declined for now, in writing, as the likeliest third
child. Not declined for thinness: both delivered children are thin too.

---

## Frugal AI > Hardware cost — LEAF, deliberately

**No depth-3 set.** The demand is single: the model must fit and run on the
substrate it is given. Every candidate subdivision I could state divides by
something other than the parent's question:

- *edge / mobile / embedded / datacenter accelerator* divides by **which device**,
  which is a deployment context — Sector's and Application's question, not
  "which resource is economised". A phone's NPU and a datacenter GPU impose the
  same demand at different magnitudes, and magnitude is not a principle.
- *fitting a given chip* vs *co-designing the chip* is already settled by the
  parent's negative test: hardware design as a subject runs from AI to hardware
  and is Application, so only one side of that pair is even in scope.

A parent needs two *substantive* children; this one has none, so it stays a
leaf. This is an honourable outcome, not a gap.

---

## Shape of the draft

| parent | children | branching |
|---|---|---|
| Robustness | Adversarial robustness · Training-data integrity · Distribution-shift robustness | 3 |
| Fairness | Group fairness · Individual fairness · Representational fairness | 3 |
| Explainability | Intrinsic interpretability · Post-hoc explanation · Recourse and contestability | 3 |
| Privacy | Training-data confidentiality · User-input confidentiality · Data subject control | 3 |
| Safety | Alignment · Safe control · Output safety | 3 |
| Accountability | Regulatory compliance · Auditability · Traceability | 3 |
| Computational cost | Training compute · Inference cost · Communication cost | 3 |
| Energy cost | Energy consumption · Carbon footprint | 2 |
| Hardware cost | (leaf) | 0 |

23 level-3 nodes. Branching factor at level 3: max 3, mean 2.9 over the eight
expanded parents. No name is a compound of two principles. No sibling set
divides by more than one question, with two small strains declared above
(Fairness, Computational cost) rather than concealed.

*END OF PHASE 1 DRAFT. Nothing below this line; this file is not edited again.*
