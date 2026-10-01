# Scientific discipline axis — levels 2 and 3

Derived 2026-09-28 against `AXES.md` §7 (level 1 = OECD Fields of Science, fixed),
§7b, §8b and §9, and audited against `GRANULARITY_AUDIT.md`.

Deliverable: `nodes.tsv` — 160 nodes: 6 OECD L1 + 1 administrative `uninformative`
row, 33 L2, 120 L3.

Corpus figures throughout are **indicative**, produced by an ordered surface-matching
script over `domain_names.tsv` (2055 names / 6123 mentions). They merge `contributed`
and `used` mentions (issue #89) and are used only to expose blind spots and to
justify judgement nodes. No node was created, kept or dropped because of its size,
with one declared exception (§7 of this file).

---

## 1. Where the level-3 nodes came from

| provenance | count | which |
|---|---|---|
| **OECD FOS's own lower level** (Frascati Manual 2015, Annex: Fields of R&D) | 91 | all of 1.1, 1.3 (except quantum information), 1.4 (except cheminformatics), 1.5, 1.6 (except systems biology), 2.1–2.4, 2.7, 3.1, 3.3 (except health informatics), 3.4, 4.1, 5.2, 5.4, 5.7, 5.8, 6.2, 6.3, and 11 of the 13 clinical specialties in 3.2 |
| **ACM CCS 2012** top-level categories | 8 | every child of 1.2: software engineering, human-centered computing (→ HCI), security & privacy, computing methodologies>graphics, information systems>information retrieval, theory of computation, information systems>data management, software & its engineering>programming languages |
| **Established psychology subdisciplines** (APA divisional structure) | 5 | children of 5.1 — OECD's own lower level for 5.1 is only "Psychology" and "Psychology, special", which is unusable |
| **Judgement** | 16 | quantum-information-science, cheminformatics, systems-biology, computational-materials-science, neural-engineering, biomechanics, water-engineering, medical-physics, radiation-oncology, health-informatics, biomarker-discovery, pedagogy, educational-technology, professional-education, social-inequality-studies, regulation-and-governance |

Every judgement node is named after a field's **own established name** (AAPM's
*medical physics*, the *cheminformatics* community, *neural engineering* as an IEEE
EMBS sub-discipline), never a fused `X and Y` label invented here. `ceramics-and-composites`
and `atomic-molecular-and-chemical-physics` are compounds only because they are
OECD's and the field's own spellings respectively.

**Unusable OECD lower levels, declared:**
- **1.4 Chemical sciences.** OECD divides chemistry by matter class (organic /
  inorganic / physical / analytical / polymer / electrochemistry / colloid). The
  corpus's entire chemistry cluster (~25 mentions: molecular property prediction,
  molecule generation, chemoinformatics, molecular design) is a *methodological*
  field that cross-cuts all seven. Added `cheminformatics`.
- **3.2 Clinical medicine.** OECD lists ~25 specialties and has no node for the
  single largest clinical cluster in this corpus (medical physics + radiation
  therapy + dosimetry + brachytherapy, ~57 mentions). Added `medical-physics` and
  `radiation-oncology`; instantiated 11 of OECD's 25 specialties (those the corpus
  reaches) plus OECD's own residual `general-and-internal-medicine`.
- **5.1 Psychology.** OECD's two lower-level items are a category and its
  exception. Replaced wholesale.
- **5.3 Educational sciences.** OECD's "Education, general" / "Education, special"
  splits by learner disability, which no corpus name touches. Replaced.
- **2.5 Materials engineering.** OECD's list is material classes; ML-driven
  materials discovery has no home. Added `computational-materials-science`.

**Retention rule for nodes with no corpus support** (stated because AXES.md does
not have one): an OECD lower-level node is instantiated when it has corpus support,
or when its parent would otherwise have fewer than two children, or when it names a
field the institute plausibly reaches in a 2023–2026 re-extraction given its current
collaborations. Otherwise the L2 is left a **leaf**, which is not a coverage failure:
`NodeCut` matches ids not depth, and an unforeseen paper lands on the L2 node itself
by the branch-level residence rule (§8b). Six L2 nodes are leaves for this reason:
4.2, 4.3, 4.4, 5.6, 6.1, 6.4. Twenty L3 nodes are kept empty (marked
*speculative-keep* in `notes`), most of them in 1.3 physics and 1.5 earth sciences,
where ML-for-fluids, ML-for-optics, hydrology and oceanography are large literatures
that this institute simply has not touched.

---

## 2. Where AXES.md is silent, ambiguous or self-contradictory

This is the most valuable output of the derivation. Eleven findings, D1 worst.

**D1 — The axis's own test contradicts OECD's scope note for 1.2, and AXES.md never
notices.** OECD 1.2 is *"Computer sciences, information science and bioinformatics"*
and its Frascati gloss explicitly covers artificial intelligence. Read literally,
all 1999 papers are 1.2 and the axis measures nothing. §7's test ("exists without AI"
AND "supplies the problem, not the machinery") says the opposite: core ML/AI is
machinery and belongs to Method/Modality/Task. **Adopted resolution:** 1.2 admits
only computing disciplines that predate and survive machine learning — software
engineering (61 mentions), HCI (40), IR (24), graphics (18), security (11), theory
of computation (8), data management, programming languages. The bare AI surfaces
(`Machine Learning` 250, `Deep Learning` 233, `Neural Networks` 19, `Artificial
Intelligence` 15, ~750 mentions) are **absent from this axis**, not uninformative on
it (§8b's own distinction). Consequence that must be stated in the report: *this
axis's level 1 is OECD FOS minus the field the institute is in.*

**D2 — §7 is factually wrong about where OECD puts neuroscience.** §7's "Costs
accepted deliberately" says neuroscience splits across "1.6 biological, 5.1
psychology/cognitive, 3.2 clinical neurology". Frascati FOS 2015 places
*"Neurosciences (including psychophysiology)"* under **3.1 Basic medicine**; 1.6
Biological sciences contains no neuroscience item at all. The correction materially
improves the outcome — see §3 below.

**D3 — No stated precedence between OECD's placement and the axis's own test.**
OECD files bioinformatics in 1.2; §7 treats `Bioinformatics` (40) and `Computational
Biology` (33) as surfaces of the *biology* branch. Both cannot hold. **Adopted:** the
axis test wins and OECD supplies vocabulary and breadth only — exactly the status §3
gives ACM CCS ("vocabulary and breadth, never arbitration"). `Bioinformatics` and
friends (9 names, 81 mentions) therefore sit on the **1.6 branch node**, and this
file records the deviation rather than hiding it. The rule needs to be written into
AXES.md, because it recurs (medical imaging, remote sensing, materials).

**D4 — §7 fixes L2 = OECD L2 but says nothing about what to do when OECD's L3 fails.**
Four of OECD's lower levels are unusable (listed in §1 above) and one — 3.2 — is
usable but incomplete for a top-5 corpus cluster. AXES.md gives no policy. Adopted
policy is in §1.

**D5 — The learning-theory boundary is asserted on Method and left unstated here.**
§3 notes ACM CCS files learning theory under *Theory of computation*. Our 1.2
`theory-of-computation` must therefore **refuse** `Statistical Learning Theory`,
`Machine Learning Theory`, `Deep Learning Theory` and send them to Method. The
discipline axis and the Method axis thus jointly disagree with ACM on one node. Now
written as that node's negative test; it was previously implicit and would have been
improvised at mapping time.

**D6 — Governance is unadjudicated between this axis and Desired properties.** §8b
absorbs the vague AI-ethics umbrella (`AI Ethics` 7, `Responsible AI` 5, ~28
mentions) into the properties branch node. It is silent on `AI Governance` (3),
`AI Policy` (2), `Governance of AI`, `AI Safety and Governance`, `Climate Governance`,
`Ethical, Legal and Social Implications` — names whose *field served* is law or
political science, disciplines that plainly exist without AI. §2's "exogenous demand"
test and §7's "field served" test both fire. **Adopted:** demand-register surfaces
(`Responsible AI`, `Ethical AI`) → properties; institution-register surfaces
(`AI Governance`, `AI Policy`, `ELSI`) → 5.5 `regulation-and-governance`. Contested;
flagged for the owner.

**D7 — Cross-axis compounds have no rule.** §8b's "nearest common parent" rule for
compound surfaces is explicitly *within* an axis. `Operational Research in Public
Transportation` fuses a Method name (§7: OR is machinery), a Sector value (§7b:
transit operations) and arguably 5.7 transport planning. Six such surfaces exist.
Rejected them from this axis; the rule needs stating.

**D8 — §8b mandates an uninformative branch that its own other rules guarantee to be
empty.** Every vague-but-on-axis surface here names a *branch* (`Healthcare`,
`Bioinformatics`, `Physics`, `Medical Research`, `Biomedicine`), so branch-level
residence absorbs all of them — the identical outcome the properties axis reported
(D-P4/D-P5). The `uninformative` row is present, carries **0 names / 0 mentions**,
and is flagged "empty by construction". Two axes now report the same thing; the rule
should probably become "an axis may have an empty uninformative branch when its
branch nodes are addressable".

**D9 — §9 contradicts §7 on the deliverable depth.** §9's carried-over constraint
says "Depth 2 is the deliverable; 3 example depth-3 labels per category validate it";
§7 says "Level 3 is the deliverable". §7 is later and specific, so it wins, and
examples are given at L3 (not L4). §9's line should be amended.

**D10 — "Knowledge advanced" vs "supplies the problem" are not the same question.**
§7's headline is *what field's knowledge does this work advance?*; its test asks
whether the field *supplies the problem*. A paper applying a stock transformer to
protein folding takes biology's problem but may advance no biological knowledge.
That is exactly issue #89's contributed/used distinction, which the schema does not
carry. Until it does, this axis's shares cannot be read as "proportion of research
advancing field X"; they read as "proportion of research whose problem comes from
field X". The report must use the second wording.

**D11 — §8b requires each axis to state its own precedence; §7 never does.**
**Stated here: the field served wins over the head noun** — the inverse of Method's
head-noun rule, and the same inversion §8b already records for Modality.
`Machine Learning for Materials Science` → 2.5 (head noun generic, modifier names the
field). `Medical Image Segmentation` → 3.2 (head noun is a Task, modifier names the
field). `Reinforcement Learning in Healthcare` → branch 3. `Graph Signal Processing`
→ absent (neither token names a field served).

---

## 3. The Neuroscience split — concretely

With D2 corrected, neuroscience divides across **3.1 `neurosciences`, 5.1
`cognitive-science`, 3.2 `clinical-neurology`, 3.2 `psychiatry` and 2.6
`neural-engineering`** — not 1.6/5.1/3.2. Measured placement of the corpus's
neuro-surfaces:

| destination | names | mentions | what lands there |
|---|---|---|---|
| 3.1 `neurosciences` | 36 | **185** | `Neuroscience` 84, `Neuroimaging` 28, `Computational Neuroscience` 16, `Brain Imaging`, `Functional Connectivity`, `Connectomics`, `Electrophysiology`, `Diffusion MRI`, `Systems/Network/Theoretical/Visual/Developmental/Population Neuroscience`, `Neuroanatomy`, `Cortex Parcellation` |
| 5.1 `cognitive-science` | 12 | 36 | `Cognitive Neuroscience` 13, `Cognitive Science` 7, `Neuropsychology` 3, `Social Neuroscience` 4, `Cognitive Modeling`, `Brain Decoding`/`Brain Encoding`, `Cognitive Architecture` |
| 3.2 `psychiatry` | 15 | 38 | `Psychiatry` 13, `Autism Research` 8, `Mental Health` 3, `Computational Psychiatry`, `Neurodevelopmental Disorders`, `Psychopathology` |
| 3.2 `clinical-neurology` | 9 | 15 | `Neurology` 5, `Neurodegenerative Diseases` 3, `Neurocognitive Disorders`, `Spinal Cord Injury Rehabilitation`, `Clinical Neurophysiology` |
| 2.6 `neural-engineering` | 8 | 15 | `Brain-Computer Interfaces` 3+2+2, `Neurostimulation`, `Neuromodulation` 3, `Deep Brain Stimulation`, `Neuroprosthetics` |
| Method (rejected) | 9 | 10 | `Neuroscience-inspired AI`, `NeuroAI`, `Neuro-Symbolic AI`, `Biologically-Inspired RL`, `Social Neuro AI` — brain vocabulary naming machinery, not a field served |
| 2.2 `computer-hardware-and-architecture` | — | 2 | `Neuromorphic Computing`, `Neuromorphic Engineering` |
| 3.3 `medical-ethics` | — | 1 | `Neuroethics` |
| 5.1 `human-factors-and-ergonomics` | — | 2 | `Neuroergonomics` |

**Verdict: survivable, and cheaper than §7 feared.** Three facts.
1. 289 of ~304 neuro mentions land in **two** OECD level-1 branches (3 Medical &
   health: 253; 5 Social sciences: 38), not three. The corrected 3.1 placement is
   what does it. §7's "~140 mentions, our largest coherent research community"
   understated the cluster and overstated the fragmentation.
2. The split rule is mechanical and needs no paper-level judgement: *head noun or
   modifier names a cognitive construct or behaviour* → 5.1; *names a disease or
   patient population* → 3.2; *names a device or stimulator* → 2.6; *otherwise, the
   nervous system as biological substrate* → 3.1. Every corpus surface above is
   decided by that rule on the name alone.
3. The residual cost is real but has changed shape. It is no longer "the community is
   torn apart"; it is "**`neurosciences` is a 185-mention leaf**" — the single
   coarsest node on the axis, holding basic, systems, computational and imaging
   neuroscience together. A depth-4 split under it is the one refinement this axis
   clearly needs, and it must be derived from an external standard (e.g. SfN session
   categories) rather than from corpus volume, or it will repeat exactly the defect
   that killed the first derivation.

Reporting consequence: a "neuroscience" line in the survey is **derivable but not a
node** — it is `3.1 neurosciences + 5.1 cognitive-science + 3.2 clinical-neurology +
3.2 psychiatry + 2.6 neural-engineering`. That roll-up should be published alongside
the OECD view, exactly as §8b requires branch-level denominators to be named.

---

## 4. Names that map to a branch node rather than a leaf

| node | depth | names | mentions | examples |
|---|---|---|---|---|
| `medical-and-health-sciences` (L1) | 1 | 37 | 70 | `Healthcare` 16, `Healthcare AI` 6, `Medical Research` 4, `Artificial Intelligence in Medicine` 4, `Biomedicine`, `AI for Health`, `Patient Care` |
| `biological-sciences` (1.6) | 2 | 9 | 81 | `Bioinformatics` 40, `Computational Biology` 33, `Machine Learning for Biology`, `Biological Sequence Design` |
| `physical-sciences` (1.3) | 2 | 7 | 11 | `Physics` 5, `Computational Physics`, `Machine Learning for Physical Sciences` |
| **total** | | **53** | **162** | **10.1% of the 1600 mapped mentions** |

This is a **correction to §8b's "~25% of the application axis's mentions land at
depth 1"**: under OECD's extra level the figure for this axis is 10%, because OECD
supplies proper depth-3 homes for three of the surfaces §8b listed as branch-level —
`Medical Imaging` 51 → 3.2 `radiology-and-medical-imaging`, `Robotics` 26 → 2.2
`robotics-and-automation`, `Neuroscience` 84 → 3.1 `neurosciences`. The branch-level
problem did not disappear; for neuroscience it moved *into* a very large leaf (§3).

---

## 5. Blind spots kept, and blind spots found

**Categories kept with no corpus support** (speculative-keep, never deleted):
4.2 animal & dairy science, 4.3 veterinary science, 4.4 agricultural biotechnology,
5.6 political science, 6.1 history & archaeology, 6.4 arts (six childless L2 nodes),
plus 20 empty L3 nodes concentrated in physics (fluids & plasma, condensed matter,
optics, quantum information), earth sciences (meteorology, hydrology, oceanography,
geosciences), chemistry (organic, analytical, polymer) and the thin social-science
branches. Justification: each is OECD's own or an established field, each is a large
ML literature *outside* this institute, and deleting them makes the axis a
description of one year of one lab rather than a classification.

**Corpus clusters with no category — real blind spots:**
1. **`Medical Physics` + radiation therapy (~57 mentions)** had no OECD L3. Fixed
   here with two judgement nodes; flagged because it is the clearest case of OECD's
   clinical level being a 1960s specialty list.
2. **Computational chemistry / cheminformatics (~48 mentions)** had no OECD L3.
   Fixed; same cause.
3. **Bioinformatics / computational biology (81 mentions)** is homeless *by design*
   under OECD (it is filed in 1.2). Parked on the 1.6 branch node; the NIH BISTIC
   distinction §7 declines to adjudicate would be the natural depth-3 split if
   extraction ever supports it.
4. **`Human-Computer Interaction` (40 mentions with variants)** is split in OECD's
   own scope notes: computing HCI in 1.2, "social aspects" in 5.8. Placed in 1.2
   (ACM's home) with a negative test; genuinely ambiguous.
5. **"AI for science" as such** has no node on any axis. `Machine Learning for
   Physical Sciences`, `AI for Health`, `Machine Learning for Biology` are treated as
   branch-level surfaces of the served field, which loses the cross-field
   methodological community these names actually denote.

---

## 6. Names rejected to another axis, with the test that rejected them

| rejected | names / mentions | destination | test |
|---|---|---|---|
| `Machine Learning` 250, `Deep Learning` 233, `Neural Networks` 19, `Artificial Intelligence` 15, and all method surfaces | — / ~2900 | Method / Modality / Task | "supplies the problem, not the machinery" (§7); absent from this axis, not uninformative (§8b) |
| `AI Ethics` 7, `Responsible AI` 5, `Ethical AI`, `AI Safety` 6, `Model Safety` (20 names) | 20 / 45 | Desired properties | demand-register surface on the AI system itself; reflexive, so fails "exists without AI" (§2) |
| `Recommender Systems` 16, `Recommendation Systems` 3, `Music Recommendation Systems` (7 names) | 7 / 25 | Task | §7 explicit: fails "exists without AI", names what the output must be |
| `Policy Gradient Methods` 5, `Policy Optimization` 4, `Policy Evaluation`, `Proximal Policy Optimization` (8 names) | 8 / 15 | Method | declared homonym (§8b); `policy` here is an RL object, not governance. This is the trap the brief's `decision making` example warns about, and the reason 5.5 is named `regulation-and-governance`, not `policy` |
| `Neuroscience-inspired AI`, `NeuroAI`, `Neuro-Symbolic AI`, `Biologically-Inspired RL` (9 names) | 9 / 10 | Method | the field named is the *source of a metaphor*, not the field served |
| `Game Theory` 20, `Operations Research` 19, `Operational Research in Transportation` (+ OR compounds) | 5 / 43 | Method (+ Sector for the transit compounds) | §7 explicit: supplies machinery |
| `Optimal Transport` 4 | 1 / 4 | Method | mathematical machinery; the `transport` token is a surface trap for 5.7 |
| `Random Forest Proximities` | 1 / 1 | Method | `forest` token trap for 4.1 forestry |
| `Physics-Informed Neural Networks`, `Physics-Guided Learning`, `Physics-Constrained Deep Learning` | 3 / 4 | Method | physics supplies an inductive bias, i.e. machinery; the served field is whatever the application is |
| `Evolutionary Algorithms` 2, `Genetic Algorithm` | 2 / 3 | Method (a confirmed Method blind spot, `EXTERNAL_DIFF.md`) | `evolutionary`/`genetic` token trap for 1.6 |
| `Molecular Graphs`, `Protein Language Models`, `Molecular Representations` | 4 / 4 | Modality | §8b: on Modality the token naming the *signal* wins; here neither token names a field served |
| `Natural Language Processing` 306, `Computer Vision` 251, `Speech Recognition`, `Machine Translation` | — / ~600 | Modality / Task | **the single most consequential rejection on this axis**: NLP is not a contribution to 6.2 linguistics. Only `Linguistics`, `Computational Linguistics`, `Syntax`, `Sociolinguistics`, `Linguistic Semantics` (14 mentions) reach 6.2 |
| `Benchmarking` 7, `Model Evaluation` 7, `Evaluation Metrics` 8, `Empirical Analysis of Algorithms` | — | `mark_ignore` on every axis | §8b contribution-type rule |

Declared homonyms for this axis, to resolve before any mapping run (extending §8b's
list): **policy** (RL vs governance), **forest** (random forest vs forestry),
**transport** (optimal transport vs transport planning vs transit sector),
**genetic / evolutionary** (GA vs biology), **network** (telecom vs neural vs social),
**physics** (object of study vs inductive bias), **imaging** (radiology vs
neuroscience vs modality), **ethics** (AI-ethics demand vs philosophy vs medical
ethics), **education** (educational science vs machine `learning`), **materials**
(1.3 condensed matter vs 2.5 engineering), **decision making** (RL/POMDP vs the
clinical `Shared Decision Making` 5, which is routed to 3.3 health services research).

---

## 7. Branching factors and my own granularity audit

**Branching.** L1→L2: mean 5.5, range 4–8 (fixed by OECD). L2→L3: mean 4.4, range
2–13; six L2 leaves. Distribution of L3 per L2: 13 (3.2), 10 (1.6), 8 (1.2), 8 (1.3),
6 (1.5), 6 (3.1), 5 (1.4), 5 (2.2), 5 (3.3), 5 (5.1), then 3s and 2s.
Per L1 branch: Natural sciences 6 L2 / 40 L3 · Engineering 7 / 23 · Medical & health
4 / 27 · Agricultural & veterinary 4 / 3 · Social sciences 8 / 22 · Humanities 4 / 5.

**Audit test** (`GRANULARITY_AUDIT.md`): *are these the same kind of thing, at the
same level of specificity, and does any sibling exist only because it was large in
this corpus?*

- **Root.** Six OECD fields plus one administrative row explicitly flagged "not an
  OECD field", the same construction §8b requires. Passes.
- **A1 (L2, inherited).** 1.2 Computer & information sciences is not the same *kind*
  of sibling as 1.1/1.3/1.6 **in this corpus**, because the institute is inside it and
  it needs a scope carve-out no other L2 needs (D1). Inherited from OECD; not fixable
  without re-opening the locked level 1. Reported.
- **A2 (3.x, inherited).** 3.1/3.2/3.3 divide by level of the object (pre-clinical /
  patient / population) — one principle. 3.4 Medical biotechnology divides by
  *technique*. OECD's defect; reported, not fixed.
- **A3 (3.2, mine and OECD's).** The 13 clinical children are not one level of
  specificity: `oncology` is disease-defined, `pediatrics` and `geriatrics` are
  population-defined, `medical-physics` is a physics-of-medicine field,
  `general-and-internal-medicine` is a residual. OECD's own 3.2 has the same mixture
  (it lists "Critical care medicine" beside "Dentistry"). Fixing it would mean
  re-deriving clinical medicine against MeSH, i.e. substituting our judgement where a
  standard exists. Reported, not fixed. Highest branching factor on the axis.
- **A4 (1.6, inherited).** Ten children mix level of organisation (cell, molecule),
  relation (ecology, evolution) and a system view (systems biology). OECD's list has
  the same mixture; `systems-biology` is my one addition and is the least
  well-partitioned sibling.
- **A5 (2.5, mine).** `computational-materials-science` is method-flavoured beside
  `ceramics-and-composites` and `coatings-and-films`, which are material classes —
  two principles in one sibling set. It exists because OECD 2.5 has no home for
  ML-driven materials discovery. Flagged as the weakest sibling set I created.
- **A6 (the volume question — the honest answer).** Two nodes exist partly because
  they were large here: **`medical-physics` (30) and `radiation-oncology` (27)**.
  Both are accredited, named fields (AAPM; a primary ABMS/RCPSC specialty), so they
  would be defensible at this granularity in any classification of medicine — but had
  the corpus contained none of them, I would probably not have added them to 3.2
  while leaving out dentistry, ophthalmology and anaesthesiology, which I did leave
  out. **That is the one place on this axis where corpus volume set granularity, and
  it is declared rather than laundered.** The same charge does not stick to
  `neurosciences` (OECD's own node), `robotics-and-automation` (OECD's own) or
  `cheminformatics` (a named field with a journal and a society).
- **A7.** No node is named so generally that it attracts out-of-scope entries: 5.5 is
  `regulation-and-governance`, not `policy`; 5.4's child is `social-inequality-studies`,
  not `fairness`; 1.2's child is `computer-security`, not `security`;
  `general-and-internal-medicine` is explicitly a residual with a negative test
  ("a specialty is named → that specialty").
- **A8.** Every parent has ≥2 children; no parent has exactly one. Six L2 nodes have
  zero children by the stated retention rule, which is a leaf, not a one-child parent.

**Coverage.** 622 of 2055 names (1600 of 6123 mentions, 26%) map to this axis. The
remaining 74% are Method/Modality/Task/Properties surfaces that correctly take **no
value** here — this is an optional axis and a blank is a finding, not a failure (§1).
