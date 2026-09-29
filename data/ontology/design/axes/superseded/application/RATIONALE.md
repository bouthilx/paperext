# Application domain axis: depth-2 derivation

*What outside field does the work serve?* Derived 2026-09-25 from `AXES.md`
(authoritative) plus `TAIL_VALIDATION.md` and the 2055-name corpus in
`domain_names.tsv`. Nothing else was consulted: no previous ontology version,
no model outputs, no proposed-category list.

Deliverable: `nodes.tsv` — 8 fixed level-1 branches, **51 level-2 nodes**, one
per-axis uninformative branch, 3 example depth-3 labels per level-2 node.

## 1. The test, applied

A field is on this axis only if **it exists without AI** *and* **it supplies the
problem, not the machinery**. Both clauses did real work: the first removes
`Recommender Systems`, `Embodied AI`, `Multi-Agent Systems`, `Conversational
AI`; the second removes control theory, operations research, graph theory,
statistics and physics-informed learning, all of which pass the first.

One refinement was needed and is proposed as a schema amendment: **apply
"exists without AI" to the field served, not to the surface of the name.**
`MLOps` and `Software Engineering for Machine Learning` would fail a literal
reading, but the field they serve — software engineering — plainly exists
without AI, and the papers are SE papers. Without this, the test deletes a real
application cluster on a wording technicality.

## 2. Where each level-2 node came from

**Forced by `AXES.md` §7** (named there, inside a branch): medical physics,
public health, clinical medicine (implied by pediatric surgery + psychiatry),
computational neuroscience, cognitive neuroscience, genetics & genomics (as
"genomics, genetics"), molecular & cell biology (as "molecular & structural
biology"), immunology & microbiology (as "immunology"), ecology & evolution (as
"ecology"), software engineering, human-centered computing (HCI), computer
graphics, computer networks, computer security, astronomy & astrophysics,
chemistry, climate science, materials science, psychology, education,
economics, public policy & law, sociology, linguistics, control systems
engineering, multi-robot systems, energy & utilities, transportation &
logistics, manufacturing, finance & insurance. **30 of 51.**

**From an established classification system** (where §7 was silent and I
refused to invent a grouping):

| node | system | citation |
|---|---|---|
| Cellular & molecular neuroscience, Systems neuroscience | Scopus ASJC | 2804, 2806; 2801/2809 |
| Ecology & evolution (fused name) | Scopus ASJC | 1105 "Ecology, Evolution, Behavior and Systematics" |
| Immunology & microbiology (fused name) | Scopus ASJC | 2400 |
| Molecular & cell biology | OECD FOS | 1.6 biochemistry & molecular biology + cell biology |
| Agricultural & plant sciences | OECD FOS | 4 (a *top-level* field with no branch here) |
| Computer systems & architecture, Theory of computation | ACM CCS 2012 | "Computer systems organization"+"Hardware"; "Theory of computation" |
| Human-centered computing (name taken verbatim) | ACM CCS 2012 | incl. Visualization, which is therefore not under Graphics |
| Physics, Earth & environmental sciences | OECD FOS | 1.3; 1.5 (the fused name is OECD's own label) |
| Pharmacology, Biomedical engineering | OECD FOS | 3.1 "pharmacology and pharmacy"; 2.6 "medical engineering" |
| Health informatics | Scopus ASJC | 2718 |
| Public policy & law (merging two thin fields) | ACM CCS | "Law, social and behavioral sciences" |
| Built environment, Telecommunications, Retail & consumer services, Media & entertainment | ISIC Rev.4 / GICS | F+urban; J61; G+consumer; Media & Entertainment |
| Robotic manipulation, Mobile robotics, Autonomous vehicles, Human-robot interaction | IEEE RAS technical-committee structure | the canonical robot capability families |

**My judgement, no system decides it** (4): *Health services research* and
*Medical education* (both defensible from OECD 3.3 / health-faculty practice,
but the decision to raise them to depth 2 is mine); *Cognitive science* as
distinct from Psychology (a boundary no system draws this way — see D4);
*Climate science* promoted out of OECD 1.5 to depth 2 because AI-for-climate is
a standing worldwide family that must survive a re-extraction.

**Deviations from §7, stated openly.** §7 lists Life sciences' children as
"genomics, genetics, immunology, molecular & structural biology and ecology".
I merged genomics+genetics (genome-scale vs heredity is a granularity
difference, not a principle of division; OECD 1.6 and Scopus 1311 carry one
field), renamed "molecular & structural biology" (a §9-banned compound of two
levels; structural biology becomes depth 3), widened immunology per Scopus
2400, and added agricultural & plant sciences.

## 3. Schema defects: where `AXES.md` is silent, ambiguous or self-contradictory

This is the part worth reading.

**D1 — the eighth branch is named twice, differently.** §7's table says
`Industry & commerce`; §7's prose says "this is why the eighth branch is named
Industry & economics". One of them has to go. I used the table's name.

**D2 — control systems contradicts the Operations Research ruling
(blocking).** §7 lists "control systems 9" inside *Robotics & autonomous
systems*, while §7's own locked ruling sends `Game Theory` and `Operations
Research` to Method because they supply machinery. Optimal control, model
predictive control, Lyapunov stability and LQG are machinery by exactly the
same argument: they are mathematics that predates and exceeds robotics. My
resolution mirrors the validated `Operational Research in Public
Transportation` split — the mathematics to Method, the engineered plant to
`Robotics > Control systems engineering` — but it needs an owner decision,
because ~20 corpus mentions move depending on the answer, and `Control Systems`
9 itself is ambiguous between the two readings.

**D3 — `Health Economics` is placed by the wrong rule.** §7 files it under
Social & behavioural sciences as "economics-as-discipline". Health economics is
a health-services discipline (OECD FOS 3.3 "health policy and services";
Scopus 2719 "Health Policy") and travels with health policy, HTA and
pharmacoeconomics, all present in this corpus. I filed it under
`Health > Health services research` and flag the conflict.

**D4 — the level-1 branch `Neuroscience & cognitive science` matches no listed
system, and is the same failure mode that withdrew "Language, mind &
behaviour".** OECD FOS groups cognitive science *with psychology* (5.1
"Psychology and cognitive sciences") and neurosciences under 3.1 Medical;
Scopus splits "Cognitive Neuroscience" (2805, Neuroscience) from "Experimental
and Cognitive Psychology" (3205, Psychology); LCC splits BF from QP. No system
fuses neuroscience and cognitive science into one branch. It is also a
compound branch name, which §9 bans for categories. It is locked, so I
delivered it — but the boundary between `Cognitive science` here and
`Psychology` in Social & behavioural is then *declared, not derived*:
mechanisms of cognition here, behaviour of persons and groups there. Expect
mapping disagreement on `Cognitive Modeling`, `Theory of Mind`, `Lifespan
Development`, `Physiological Psychology`.

**D5 — two whole top-level fields have no branch: mathematics and the
humanities.** OECD FOS 1.1 (mathematics) and 6 (humanities & the arts) are
top-level fields; ACM CCS has "Applied computing > Arts and humanities". With
eight branches fixed, AI-for-mathematics (autoformalization, conjecture
generation) has to be parked in `Computing > Theory of computation`, and
digital humanities, cultural heritage and art history have nowhere at all.
Neither is an accident of this corpus: both are growing application areas.

**D6 — no branch for agriculture & food systems.** OECD FOS 4 makes it a
top-level field. I filed it as a *science* under Life sciences; the sector
reading (agri-business, precision farming for producers) would want Industry &
commerce. Whichever is chosen must be written down, or annotators will split
`Agricultural Data Analysis` from `Crop Phenotyping` at random.

**D7 — engineering is dismembered without anyone saying so.** OECD FOS 2
(Engineering & technology) is one field; under these eight branches its members
scatter: biomedical engineering → Health, materials → Physical, electrical and
telecom → Computing and Industry, civil → Industry, environmental engineering →
Physical. The corpus contains `Aerospace Engineering`, `Electrical
Engineering`, `Chemical Engineering`, `Environmental Engineering`, `Antenna
Design`, `VLSI Systems` — six names, six different branches. This is a
defensible design, but it is undeclared and it is the single most likely source
of annotator drift.

**D8 — branch-level surfaces are a bigger deal at depth 2 than §7 admits.** §7
rules that `Bioinformatics` and `Computational Biology` are surfaces of the
*branch node*. That ruling generalises, and when it does it takes a quarter of
the axis with it: `Neuroscience` 84, `Medical Imaging` 48, `Neuroimaging` 28,
`Robotics` 25, `Healthcare` 16, `Embodied AI` 5 are all branch-level names.
Measured: **~465 of ~1,880 application mentions (25%) sit at depth 1 and reach
no depth-2 node.** The design needs an explicit rule that depth-1 placement is
a legal, non-residual outcome, and the survey's depth-2 shares need a stated
denominator.

**D9 — §8b's "compound surface → nearest common parent" rule needs scoping.**
It is written for within-axis compounds (`Fairness and Interpretability`), but
the corpus's most common compounds are *cross-axis* (`Medical Imaging`,
`Neuroimaging`, `Medical Image Segmentation`), where the right answer is a
different value on each axis, not a common parent. Scope the rule to
within-axis compounds (`Healthcare Systems and Surgery` → parent
`Health & medicine`) and say so.

**D10 — the `Policy` homonym is worse than F7 estimated, and I measured it.**
11 corpus names contain "Policy". Six are reinforcement-learning policies
(`Policy Optimization` 4, `Proximal Policy Optimization`, `Policy Ensemble`,
`Policy Regularization`, `Generalized Policy Iteration`, `Stable Policy
Learning`), five are public policy. A node named `Policy` on this axis would be
55% wrong; hence `Public policy & law`. The same trap exists for `Security`
(computer security vs Trustworthy AI), `Network` (carrier network vs graph vs
neural network), `Control` (control engineering vs RL continuous control) and
`Learning` (education vs machine learning).

**D11 — §7's corpus figures undercount this axis by ~2.5x.** §7's per-branch
estimates total ~720 mentions. A keyword sweep of the full vocabulary, after
removing names claimed by Method / Modality / Task / Desired properties,
assigns **~1,880 mentions across ~800 names (~31% of the 5,990 name mentions)**
to the application axis. Any planning that uses §7's numbers — mapping effort,
expected `Not Specified` rate, the headline area table — will be wrong. Per
branch (names / mentions, approximate): Health 256/544 · Neuro 83/262 · Life
100/267 · Computing 150/268 · Physical 86/170 · Robotics 57/108 · Industry
70/89 · Social 59/72.

**D12 — this axis had no uninformative branch.** §8b requires one per axis and
names none here. Added: `Application domain not specified`, holding
`Application-Driven Machine Learning`, `Deep Learning Applications`,
`Interdisciplinary Studies`, `Scientific Machine Learning`, `Real-world
Applications` (~22 names / ~35 mentions), reported as a line and excluded from
shares.

**D13 — Desired properties vs computer security is an undeclared collision.**
§2 assigns robustness and privacy to Trustworthy AI, but the corpus also holds
`Cybersecurity` 3, `IoT Security`, `Vulnerability Detection`, `Digital
Forensics` — computer security as an outside field supplying problems. Declared
split: an adversary attacking *the model* (adversarial examples, membership
inference, poisoning) → Desired properties; an adversary attacking *a deployed
computing system* → Application > Computer security. The node is deliberately
**not** named "Security & privacy" (ACM CCS's name), because that name would
attract ~40 mentions of privacy-of-ML work.

**D14 — §8b's contribution-type rule collides with a real health cluster.**
`Patient Decision Aids Evaluation`, `Reproducibility in Medical Imaging`,
`Metric Evaluation` are contribution-type by F4's rule and therefore
`mark_ignore` on every axis — yet they are unmistakably health-services and
medical-imaging papers. The rule as written discards their application value.
Suggested amendment: contribution-type names are `mark_ignore` on Method, Task
and Desired properties, but still map on Application when they name a field.

## 4. Blind spots: kept despite little or no corpus support

Every one of these is a field ML is applied to broadly elsewhere. None is
deleted; §9 forbids the corpus arbitrating.

| node / gap | corpus | why kept |
|---|---|---|
| Cellular & molecular neuroscience | 2 names | Scopus 2804/2806; the institute does no wet-lab neuro in 2024 |
| Human-robot interaction | 3 | a field with its own ACM/IEEE conference |
| Finance & insurance | 3 | among the largest industrial users of ML worldwide |
| Retail & consumer services | 4 | ditto; omitting it would encode this institute's lack of a retail partner |
| Manufacturing | 5 | industrial ML is a major sector; §7 names it |
| Economics, Public policy & law | 5 each | full OECD FOS 5 disciplines |
| Immunology & microbiology | 5 names | microbiology specifically is absent |
| Agricultural & plant sciences | 6 | OECD FOS 4, a top-level field |
| Sociology / computational social science | 10 | a large ML application area elsewhere |
| *no node*: defence & security, veterinary science, sports science, journalism, archaeology, library & information science, insurance actuarial, mining & extraction, public administration | 0–1 | reported as gaps; several have no branch that could host them |
| *no branch*: mathematics, arts & humanities | — | D5 |

Conversely, two clusters are **over-represented** relative to any general
ontology and were kept at full weight rather than merged: medical physics /
radiation oncology (20 names, 59 mentions, essentially one collaboration) and
software engineering (44 names, 95 mentions). §9 forbids balancing; the
asymmetry is the measurement.

## 5. Corpus names rejected as belonging to another axis

Grouped by the test that rejected them. Counts are papers.

**Exists without AI, but supplies machinery → Method.**
`Game Theory` 20, `Operations Research` 19 (settled in §7), `Cooperative Game
Theory`, `Random Utility Models`, `Social Welfare Optimization`,
`Simulation of auction data` — mechanism-design machinery, not the sector it
prices. `Control Theory` 2, `Optimal Control`, `Model Predictive Control` 3,
`Lyapunov Stability`, `Linear Quadratic Gaussian Systems`, `System
Identification` — see D2. `Vehicle Routing Problem` (×4 spellings),
`Travelling Salesman Problem`, `Job-Shop Scheduling`, `Personnel Scheduling`,
`Facility Location`, `Column Generation`, `Mixed-Integer Linear Programming`,
`Integer Programming`, `Constraint Programming`, `Stochastic Programming`,
`Metaheuristics`, `Simulated Annealing`, `Evolutionary Algorithms` — OR problem
classes; the *sector* they are applied to stays here. `Graph Theory` 6,
`Spectral Graph Theory`, `Network Science`, `Network Design`, `Information
Theory` 3, `Random Matrix Theory`, `Probability and Statistics`, `Statistics`,
`Statistical Inference`, `High-Dimensional Statistics`, `Partial Differential
Equations`, `Dynamical Systems` 4, `Optimal Transport`, `Koopman Operators` —
mathematical machinery. `Physics-Informed Neural Networks` 2,
`Physics-Guided Learning`, `Physics-Constrained Deep Learning`, `Neural
Operators`, `Surrogate Modeling` — physics supplying an inductive bias, not a
problem; the borderline case of the axis, flagged. `Neuromorphic Computing` 2,
`Neuroscience-inspired AI` 2, `NeuroAI`, `Biologically-Inspired Reinforcement
Learning`, `Reservoir Computing` — the brain supplying machinery; the reverse
direction (deep nets *as models of* cortex) stays in Computational
neuroscience. `Biostatistics` — statistics; flagged as arguable, since it
travels with health methodology.

**Fails "exists without AI" → Task, Method or uninformative.**
`Recommender Systems` 16 / `Recommendation Systems` 3 (settled in §7),
`Multi-Agent Systems` 11, `Embodied AI` 5 (kept as a Robotics *branch-level
surface*), `Artificial General Intelligence`, `Conversational AI` 4,
`Generative AI`, `Creative AI`, `Interactive AI`, `Foundation Models`,
`AutoML`, `Prompt Engineering` 6, `In-Context Learning` 4,
`Retrieval-Augmented Generation`, `Information Retrieval` 19 (settled),
`Data Mining`, `Decision Support Systems` 2 (generic; `Clinical Decision
Support Systems` does map, to Health informatics).

**Names a demand on the AI system → Desired properties.**
`Fairness in Machine Learning` 19, `Fairness in AI` 12, `Algorithmic Fairness`,
`Differential Privacy` 8, `Privacy in Machine Learning`, `Adversarial
Robustness` 9, `Adversarial Machine Learning` 13, `Model Robustness`,
`Explainable AI` 10, `Interpretable Machine Learning` 9, `AI Ethics` 7, `AI
Safety` 6, `Responsible AI` 5, `Green AI`, `Efficient Deep Learning`, `Model
Efficiency`, `Hardware Acceleration` 4, `Machine Learning Security`. Critically
**`AI Governance` 3, `AI Policy` 2, `AI Regulation`, `AI Safety and
Regulation`** → Desired properties > accountability & governance, *not*
Application > Public policy & law: the object is the AI system.

**Names what the output must be → Task.**
`Anomaly Detection` 20, `Out-of-Distribution Detection` 12, `Object Detection`,
`Continuous Control` 10, `Misinformation Detection` 3, `Fraud Detection`,
`Toxicity Detection`, `Vulnerability Detection`, `Trajectory Prediction`,
`Code Generation` 7, `Program Synthesis`, `Mathematical Reasoning` 3,
`Theorem Proving`, `Game Playing`, `Question Answering` 14. Several carry an
application value *as well* (fraud → Finance; vulnerability → Computer
security; code generation → Software engineering); the Task value does not
remove it.

**Names the signal, not the field → Modality** (each also carries an
application value, usually at branch level): `Medical Imaging` 48,
`Neuroimaging` 28, `Remote Sensing` 11, `Radiomics` 5, `Medical Image
Analysis` 10, the MRI/fMRI/EEG/MEG family, `Microscopy` 3, `Ultrasound
Imaging` 3, `Point Clouds`, `Protein Language Models`, `Molecular Graphs`,
`Single-cell RNA Sequencing Analysis`.

**Contribution type → `mark_ignore` on every axis** (§8b): `Benchmarking` 7,
`Empirical Analysis of Algorithms`, `Multimodal Model Evaluation`, `Dataset
Creation` 3, `Empirical Study`, `Qualitative Research`, `Scientific Literature
Review`, `Patient Decision Aids Evaluation` (see D14), `Open Science` (arguably
Sociology > science & technology studies; flagged).

**Too generic → this axis's uninformative branch**: `Application-Driven Machine
Learning`, `Deep Learning Applications`, `Machine Learning Applications`,
`Interdisciplinary Studies`, `Interdisciplinary - Other`, `Real-world
Applications`, `Scientific Machine Learning`, `Simulation` 5, `Computer
Simulation`, `Mathematical Modeling`, `Data Analysis` 4, `Big Data Analytics`,
`Predictive Analytics`, `Intelligent Systems`, `Digital Innovations`,
`Computing Research`.

## 6. Branching factor

| level | factor | justification |
|---|---|---|
| L1 | 8 | fixed by `AXES.md` §7; not mine to change (objections: D1, D4, D5, D6) |
| L2 | 51 total; 5–8 per branch, mean 6.4 | |

Per branch: Health 8 · Industry 8 · Computing 7 · Physical 6 · Social 6 ·
Robotics 6 · Neuro 5 · Life 5.

Why the two 8s are not over-specialisation. **Health** is the largest branch by
a factor of two (256 names / 544 mentions) and its eight children are eight
distinct *functions* of the health enterprise — treat a patient, deliver a
beam, protect a population, run the system, inform it, train its workforce,
develop a therapy, build a device — each a named profession with its own
venues. Merging any two (say medical physics into biomedical engineering)
would fuse two principles, the §3 failure that produced v0's `X and Y` nodes.
**Industry**'s children are not my invention at all: they are ISIC/GICS
sectors, and a sector list is enumerable from outside the corpus. Dropping
thin ones (finance 3, retail 4) would mean letting a single institute's 2024
partner list define what industry is — exactly what §9 forbids.

Why no branch has fewer than 5: §9 requires ≥2 substantive children, and each
branch here has at least five children that are named fields in OECD FOS,
Scopus ASJC, ACM CCS, ISIC or the IEEE RAS structure.

Depth 3 is exemplified (3 labels per level-2 node in `nodes.tsv`), not
enumerated; several examples are deliberately thin in this corpus
(`Microbiology`, `Assembly & insertion`, `E-commerce & pricing`) to show that
the structure has room for what a re-extraction will bring.
