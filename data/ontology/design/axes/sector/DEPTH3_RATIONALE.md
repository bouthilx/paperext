# Sector of application — depth 3

Delivered 2026-09-29 against `AXES.md` §7b (axis), §7 (the sibling axis whose
boundary must not blur), §9 (the expansion procedure) and `GRANULARITY_AUDIT.md`
(the acceptance test). Level 1 and level 2 were fixed; **38 level-3 rows were
appended to `nodes.tsv` under 11 of the 12 level-2 nodes on the priority list.
One, `building-operations`, stays a leaf.**

The procedure was run in the order §9 mandates. The phase-1 record is
`DRAFT_PHASE1.md`, written before any corpus access and never edited. This file
is the diff.

---

## 1. Compliance with §9's ordering, stated honestly

**What was clean.** `domain_names.tsv` was not opened, no tally was run and no
count column was consulted until every sibling set, characteristic and rejected
principle in `DRAFT_PHASE1.md` had been written to disk. Nothing under
`domains/v0`, `models/`, `run1|2|3`, the other axes' directories or the
`paperext-llm-backend` repository was read at any point.

**What was not, and could not be.** The brief and §9 require reading the parents'
characteristics in `nodes.tsv` and the declared ISIC deviations in
`RATIONALE.md` *before* phase 1. Both files carry corpus material in the same
rows as the mandated content: `nodes.tsv` has an `examples` column and two count
columns beside every characteristic, and `RATIONALE.md` §3–§4 is a
name-by-name disposition table with mention counts. There is no way to read
what is required without those being on screen. This is declared in
`DRAFT_PHASE1.md` itself rather than after the fact.

The effect was controlled, not eliminated: each sibling set names the external
structure it came from (an ISIC lower level where one exists; otherwise the
sector's own framework — WHO health-system building blocks, essential
public-health functions, the electric power chain, the profession's training
bodies), and no set is a list of corpus names. Where a child matches an
`examples` string, that is the examples column doing the job §9 assigns it — a
**step-3 checklist** — not a step-1 seed. **Design implication worth recording
for the next axis: `examples` and the count columns should live in a separate
file from `characteristic`, or the phase-1 rule cannot be fully honoured by
anyone.**

---

## 2. The phase-1 → phase-2 diff

§9 licenses exactly two changes. **Neither produced a node change. The delivered
tree is the phase-1 draft, node for node.** What phase 2 produced was flags,
four written justifications, and one written refusal.

### 2a. Question 1 — corpus clusters with no node (blind spots)

Four were found. All four are **justified in writing rather than added**, and in
each case the reason is that adding a node would fuse a second principle into a
sibling set or reverse a fixed level-2 decision.

| cluster | mentions | disposition |
|---|---|---|
| **Digital care channels** — `Digital Health` 6, `Telemedicine` 3, `Mobile Health` 2, `eHealth`, `mHealth` | ~13 | **Justified, not added.** Level 2 ruled that a channel is not an actor and folded digital health into `clinical-services` as a delivery channel. My depth-3 principle there is *setting*; a teleconsultation happens *within* a setting (primary care by video, specialist by video), so a `Remote & digital care` sibling would be a channel standing beside four settings — two principles in one set. These names sit at the level-2 node by branch-level residence (§8b). **Declared cost: roughly half of `clinical-services`' 27 mentions sit above its children.** |
| **Educational technology & tutoring** — `Educational Technology`, `Educational Data Mining`, `Intelligent Tutoring Systems`, `Programming Education`, `Computer Science Education`, `Teaching Aids`, `Education` | ~8 | **Justified, not added.** Every one of these names a *function or a subject*, never a segment. A function set (instruction / assessment / retention) is exactly the competing principle phase 1 rejected, and §9 forbids re-opening a node by a different principle because the corpus is shaped that way — *volume plays no part in how a node opens*. They sit at `general-and-higher-education` by branch-level residence. **This is the sharpest test of the ordering rule in this delivery, and it is where a corpus-first derivation would visibly have produced a different tree.** |
| **Software firm & developer workforce** — `Open Source Software Development` ×3, `Software Startups`, `Remote Work`, `Software Documentation` | ~6 | **Justified, not added.** `Open Source Software Development` and `Software Documentation` are team practices in producing software and land in `software-product-engineering`. `Software Startups` and `Remote Work` name the *producing firm and its employment arrangements*, not a function owning a software system; a fifth child for them would fuse "the firm" with "the function that owns the system", which is the defect the set exists to avoid. Quote check confirms the reading (`Remote Work`: "software development teams … forced to work remotely"). They sit at the level-2 node. Recorded as the axis's smallest declared blind spot. |
| **Web portals & search** (the J63.12 / J63.99 gap `DRAFT_PHASE1.md` predicted) | — | **No blind spot after all.** The corpus content there is `Information Retrieval` 19 (a computing discipline that predates ML → discipline 1.2) and `Recommender Systems` 16+ (refused at level 2 by S1+S5 → Task). The gap is closed by existing rules, not by a missing node. |

One phase-1 flag was checked and **cleared**: the draft asked whether
operator-side service assurance (QoS, churn, billing) forms a telecom cluster
with no node. It does not — the corpus's only candidates (`Load Balancing and
Quality of Service`, `Network Optimization`) are the declared IT homonym. The
cross-cut stands as declared.

### 2b. Question 2 — nodes with no corpus support (kept, flagged speculative)

Twelve of 38 are flagged in the `notes` column. None was deleted; §9 forbids it.

**Zero support:** `cloud-and-data-centre-services` · `health-financing-and-coverage`
· `specialist-and-ambulatory-care` · `continuing-professional-development` ·
`certification-licensure-and-assessment` · `fixed-and-core-network-operations` ·
`publishing-and-news-media` · `school-education` · `higher-education`.

**No clean support (a name exists but a rule refuses it, or the quote reads the
other way):** `care-operations-and-capacity` (`Scheduling`, `Personnel
Scheduling` are refused as OR problem classes / too generic, even though one
quote is physician scheduling) · `self-management-and-home-support` (`Patient
Support Systems`' quote is clinician-facing) · `rehabilitation-and-continuing-care`.

**Thin but non-zero (1 mention):** `prevention-and-health-promotion`
(`Injury Prevention`) · `environmental-and-occupational-health-protection`
(`Environmental Health`) · `power-generation` · `electricity-markets-and-trading`
· `road-passenger-mobility-services` · `screen-and-recorded-media-production`.

Three of these are worth naming individually:

- **`certification-licensure-and-assessment` is empty although the level-2 row's
  own examples say "Surgical skill assessment from video; Competency examination
  scoring".** The corpus's professional-education cluster is entirely
  training-side (`Medical Education` 7, `Surgical Education`, `Simulation in
  Surgical Training`, `Non-technical Skills Training`). The one assessment-shaped
  name, `Examination and Assessment Techniques`, is LLM benchmarking by its quote
  and is `mark_ignore` under §8b. The node is kept: a regulated profession
  without a certifying body does not exist.
- **Both children of `general-and-higher-education` are speculative**, because no
  corpus name states a segment. The node's ~8 mentions all sit at the parent.
  This is the honest outcome of refusing to let the corpus choose the principle.
- **`specialist-and-ambulatory-care` is empty and I am glad it is.** It is the
  node whose emptiness would be reversed by one careless mapping decision, since
  ~200 mentions of clinical specialties are sitting one rule away from it.

### 2c. Two things the corpus tempted and did not change

- **`building-operations` stays a leaf** although the corpus would support an
  energy-vs-indoor-environment split (energy names outnumber comfort names ~4:1
  there). Splitting on that basis is precisely "volume deciding how a node
  opens". The semantic argument in `DRAFT_PHASE1.md` §12 stands unchanged.
- **`media-and-entertainment` keeps five children** although only two are well
  supported. Trimming a sibling set because its members are small is the
  balance-by-paper-count rule §9 bans, read backwards.

---

## 3. Characteristics, and the competing principle rejected for each

Full text of each characteristic is in `nodes.tsv`; the principle of division and
its rejected rival are here, as §9 requires them to be stated.

| parent | principle of division (one, stated) | competing principle rejected, and why |
|---|---|---|
| `software-and-it-services` | which **function of the software & IT industry** owns the system — the parent's own three actors (dev team, IT operation, security function) plus the hosting provider ISIC J63 names | **the software life cycle** (SWEBOK: requirements → design → construction → test → maintenance). It divides an engineering *process*, which is a curriculum and therefore a field of study — it would import the discipline axis one level down — and it has no home for hosting, which is an industry, not a stage |
| `health-system-administration` | which **health-system building block** is run (WHO's blocks used the way ISIC is used: vocabulary and breadth, never arbitration, since ISIC has no lower level for the administrative function) | **by level of the system** (unit → hospital → region → nation). Scale cross-cuts every function, so it is a property, not a sibling |
| `public-and-population-health` | which **core public-health function** the agency performs | **by disease area** (infectious / chronic / mental / maternal & child). This is the depth-3 discipline import in its purest form — see §4 |
| `clinical-services` | which **care-delivery setting** serves the patient — ISIC's own division of Q86, which coincides with levels of care and refines the grandparent's actor principle rather than replacing it | **by channel** (in-person / tele / digital), which reverses a level-2 ruling by the back door; and **by care-pathway stage** (triage → diagnosis → treatment → follow-up), which drifts into the Task axis |
| `professional-and-continuing-education` | which **body in the profession's training system** owns the activity — the parent's positive test names all three | **by function (teach vs assess)**, which is what the parent's characteristic literally says. Close call: the owner principle subsumes it (assessment is owned by a different body in every regulated profession) while also separating initial from continuing training |
| `patient-and-caregiver-support` | which part of the **patient's and family's own role in care** the work supports — deciding, managing, being heard | **by actor (patient vs informal caregiver)**. It refines the compound name most literally but the two participate in all three activities together, so it does not partition |
| `electricity-generation-and-grid` | which **stage of the electric power chain** — ISIC 35.11/35.12/35.13/35.14 exactly, and the parent's characteristic already enumerates the chain | **by primary energy source** (solar / wind / hydro / nuclear). It divides by generation technology, which is engineering knowledge (OECD 2.2), it cross-cuts the chain (a wind farm is generation *and* a market participant), and ISIC itself divides 35.1 by stage |
| `telecommunications` | which **transmission medium** the operator runs — ISIC 61.10/61.20/61.30 | **by network layer** (physical / MAC / network / service): the engineering-knowledge division, the sibling axis's territory, and it slices one operator three ways |
| `media-and-entertainment` | which **content business** owns the work — ISIC's own division of J58–J60 plus the R90 the parent claims by deviation D4 | **by stage** (create → distribute → consume). It would split every industry in two and bury games, the one node with an unambiguous operational owner |
| `road-traffic-and-automated-vehicles` | which **operator of the road system** acts — the parent's own three owners (network / vehicle / service) | **by automation level** (SAE L0–L5), which is a product-capability scale, not an activity, and would make the axis's weakest claim its organising principle |
| `general-and-higher-education` | which **education segment** teaches the learner — ISIC 851/852 vs 853, continuing the level-2 branch's stated principle | **by institutional function** (instruction / assessment / retention / admissions). It names the institution's internal process rather than whose activity it is, and every function occurs in both segments |

**Two declared strains**, neither hidden:

1. `media-and-entertainment`'s set is not a pure stage division, because ISIC's
   own sequence mixes producing businesses (58, 59) with a distributing one (60).
   Following ISIC is the lesser defect; the alternative was rejected above.
2. `health-financing-and-coverage` is a **declared ISIC deviation** in the same
   form as the level-2 derivation's D1–D8: ISIC files health insurance under
   K65.12 and compulsory health insurance under O84.30, outside section Q. It is
   held under health system administration because the payer is part of the
   health system in the register a funder reads, and filing a ministry of health
   under banking would be unreadable. **This is the only new deviation at depth 3.**
   Everything else cites an ISIC code that genuinely covers the node: J62.01,
   J62.02-03, J62.09, J63.11, Q86, Q86.1, Q86.21, Q86.22, Q86.9, O84.12, P85.1-2,
   P85.3, P85.49, D35.11–D35.14, J61.10, J61.20, J61.30, J58.1, J58.21, J59, J60,
   R90-91, H49, H49.3, H49.31-32. No GICS, NAICS or NACE node was imported; the
   only non-ISIC frameworks used are WHO's health-system building blocks and the
   essential public-health functions, both cited as vocabulary for a place where
   ISIC has no lower level, both named in the node `notes`.

---

## 4. Where the discipline boundary was tempting at depth 3

The brief predicted the temptation would be strongest here, and it was. Four
places, in descending order of pull.

**1. `public-and-population-health`, by disease area — the big one.** The natural
depth-3 set for a public-health agency looks like *infectious / chronic / mental /
maternal & child health*, and the corpus rewards it: `Infectious Diseases`,
`Infectious Disease Epidemiology`, `COVID-19 Research`, `Mental Health`,
`Healthcare and Chronic Diseases` are all sitting there. **Refused.** Disease is
natural reality, so a disease area is discipline-only under §7b's object-level
test, exactly as `Epidemiology` (20) and `Oncology` are already refused at level
2. A sector child named `Infectious disease` would re-import OECD 3.2 under a
sector label and make this branch a lossy copy of it. The set divides by
**function** — surveillance, prevention, protection — because a function is
something an agency *runs*.

**2. `clinical-services > specialist-and-ambulatory-care` — the one-word
failure.** "Specialist care" is one careless mapping decision away from
swallowing `Medical Imaging` 51, `Pediatric Surgery` 16, `Psychiatry` 13,
`Oncology` 7, `Radiology`, `Cardiology` — ~200 mentions the level-2 derivation
deliberately kept off the axis. The node is kept because ISIC Q86.22 is real and
an ambulatory service is genuinely run by someone, but its **negative test is
written stricter than its positive test**: a specialty names a body of knowledge
and is discipline-only; the node is claimed only when the object is the *running*
of the service (referral, access, clinic throughput, day-treatment pathway) and
**never because a specialty is named**. Its emptiness in the corpus is the
evidence that the rule is currently holding.

**3. `health-information-systems-and-records` vs `Bioinformatics`.** The pull is
to let the informatics node take everything with "informatics" in it. The
S-D3 contrast holds and is the rule working rather than straining: `Health
Informatics` 8 and `Medical Informatics` take both axes because their object is
the care system's information machinery, a human-built operating system;
`Bioinformatics` 40 takes discipline only because its object is biological data,
which is nature. The node's negative test says so explicitly.

**4. `entry-to-practice-training` vs the clinical content.** `Surgical Education`
and `Simulation in Surgical Training` are surgery names, and surgery is
discipline. The tiebreak, inherited from the level-2 row: the *training
programme* is the object here, the *procedure* is the object on the discipline
axis. A paper about what a resident learns is education; a paper about what the
operation achieves is not.

**A fifth, smaller one, noted for completeness:** `cybersecurity-operations` had
to be kept away from `Machine Learning Security` (3), which is reflexive under
rule S6 and belongs to Desired properties. Vulnerability detection in production
code is a security function's problem; securing the model is not a sector at all.

---

## 5. Leaves, and why

**`building-operations` (ISIC L68 / N81) — declared a leaf, with reasons.**

The four things its characteristic names — comfort, energy, occupancy,
maintenance — are **objectives of one activity, not four activities**. One owner
(whoever operates the building), one asset (the building and its plant) and
usually one system (the building management system) serve all four at once: the
same HVAC controller is tuned for energy cost and for thermal comfort, and
occupancy is an input to both. Under the property test of `AXES.md` §6 — *a
modifier that can be true of a node's siblings is a property, not a sibling* —
`energy / comfort / maintenance / space` is not a sibling set; it is one node
described four ways, and it would fail the granularity audit the way D2 fails.

The strongest argument for expanding it is that the facility-management market
sells energy management, maintenance and space management as separate contracts.
It is refused because a contract type is a commercial packaging, not a different
operational owner, and because "we work on building operations" is already the
sentence a funder says. Over-splitting a node this size into four near-synonymous
objectives is the failure mode the brief names.

**The level-2 nodes left unopened** (`finance-and-insurance`,
`public-administration` and `retail-and-consumer-services` are level-1 leaves
already, and below them
`water-and-waste-services`, `design-and-construction`, `urban-planning-and-development`,
`air-transport`, `freight-and-logistics`, `social-care-and-community-services`,
`crop-and-livestock-production`, `forestry`, `fishing-and-aquaculture`,
`process-industries`, `discrete-manufacturing`, `public-transit`,
`environmental-quality-and-emissions`, `biodiversity-and-conservation`,
`hazards-and-disaster-response`) were **not on the priority list and were not
opened.** That is the priority rule doing its only legitimate job. They are not
declared leaves — they are unexamined, and the distinction matters: a later pass
may open them, and this file makes no claim about them.

**Two nodes I considered leafing and expanded anyway**, recorded because they are
the closest calls after `building-operations`:
`patient-and-caregiver-support` (see §6) and `general-and-higher-education`
(two children only, deliberately minimal).

---

## 6. My own granularity audit

Test, as stated: *are these the same kind of thing, at the same level of
specificity, and does any sibling exist only because it was large in this
corpus?*

**Does any sibling exist only because it was large here?** No — and the
structural reason is that the draft was written before any count was seen. The
reverse check is more informative: **12 of 38 nodes have no corpus support and
6 more have one mention**, which is what a semantics-first derivation against a
389-mention floor should look like. If volume had been steering, the tree would
have grown where the names are (the education branch would divide by *function*,
`clinical-services` would have a *digital health* child, and `telecommunications`
would be one node) — the three places where this file records refusing exactly
that.

**Sets I am confident in (7 of 11).** Their principle is ISIC's own lower level
or the sector's own value chain, and it holds across every sibling without
strain:
`electricity-generation-and-grid` (D35.11–14) · `telecommunications` (J61.1/2/3)
· `clinical-services` (Q86.1/86.21/86.22/86.9) · `software-and-it-services`
(J62/J63 functions) · `road-traffic-and-automated-vehicles` (three named owners)
· `general-and-higher-education` (851/852 vs 853) · `professional-and-continuing-education`
(three named bodies).

**Sets I am NOT confident in, declared.**

- **`patient-and-caregiver-support` — the weakest set on the axis.** T1 is weak:
  the tri-split (deciding / managing / being heard) comes from the
  patient-engagement literature rather than from ISIC or a value chain, and one
  of its three children is empty while another has two mentions. A defensible
  alternative is to leaf this node entirely, and if one depth-3 set in this file
  is to be reversed, reverse this one. Recorded in the same register as
  RATIONALE §5.4's instruction about `Autonomous Driving`.
- **`media-and-entertainment` — the widest set (5) and the one most exposed to
  over-splitting.** Every child is a separately-owned industry, which is why it
  survived, but two of the five are thin and one is empty. It is also the set
  carrying a declared principle strain (ISIC mixes producers and distributors).
- **`health-system-administration` — the only set whose principle comes from a
  framework outside the standards family.** WHO's building blocks are not ISIC
  and not OECD; they are cited because ISIC has no lower level for the
  administrative function, and two of the four children (operations, financing)
  have no clean corpus support. Structurally sound, externally anchored, but it
  is the set where I had the least to check against.
- **`public-and-population-health` — sound principle, thin membership.** Two of
  three children rest on one mention each. The principle (public-health
  functions) is externally standard, so the thinness is a corpus fact, not a
  design fault — but a three-way split where two members hold one name each is
  worth declaring.

**Register mismatch at depth 3:** none found. Every sibling set names the same
kind of thing as its siblings (a function, a stage, a setting, a medium, a
business, an owner). The root's one declared defect (`environment-and-natural-resources`
having no ISIC section) is inherited, not added to.

**Compound names.** Five depth-3 names use `&`: `IT operations & service
management`, `Health information systems & records`, `Health financing &
coverage`, `Disease surveillance & outbreak response`, `Patient experience &
voice`, plus `Primary & community care`, `Specialist & ambulatory care`,
`Rehabilitation & continuing care`, `Mobile & wireless networks`,
`Games & interactive entertainment`, `Screen & recorded media production`,
`Publishing & news media`, `Broadcasting & content platforms`,
`Transmission & system operation`, `Distribution & grid-edge operations`,
`Electricity markets & trading`, `Self-management & home support`,
`Traffic management & road operations`, `Automated & assisted driving`,
`Cloud & data-centre services`, `Satellite & non-terrestrial networks`,
`Arts, culture & heritage`, `Certification, licensure & competency assessment`.
**Self-assessment: these are doublets naming one concept in the sector's own
idiom** — the case §9 explicitly permits (`Speech & audio`, `Vision & imaging`) —
not fusions of two principles. The three I would defend least, and therefore
declare: `Certification, licensure & competency assessment` (three words for one
activity is one too many), `Distribution & grid-edge operations` (the grid edge
is where distribution meets the customer, so the second half is arguably a
sub-case of the first), and `Arts, culture & heritage` (a genuinely broad
institutional bucket).

**Branching factor.** Level 1 = 13 · level 2 = 27 under 9 parents · level 3 = 38
under 11 parents, **mean 3.45, range 2–5**. No parent has one child. The tree is
78 nodes. Nothing here specialises earlier than its siblings: the deepest path
(3) is uniform across every branch that was opened, and the branches that were
not opened stop at 2.

**Two structural costs, inherited and restated rather than repaired:**

1. The level-2 row `road-traffic-and-automated-vehicles` carries ISIC H49.3–H49.4,
   which nominally includes road freight haulage, while `freight-and-logistics`
   holds freight by function. Level-2 rows are fixed, so the boundary is
   **declared in the `notes` of `road-passenger-mobility-services`** and not fixed.
2. Isolating `automated-and-assisted-driving` in its own depth-3 node was a
   deliberate choice for **reversibility**: RATIONALE §5.4 says `Autonomous
   Driving` is the claim to reverse first, and it can now be deleted as one row
   without touching the traffic-operations nodes beside it.

---

## 7. What a reader should not conclude from this file

The counts quoted throughout are **indicative, not measured** (issue #89), and
this axis has the recorded floor effect: extraction asks for *research domains*,
so a paper whose sector is obvious from its datasets names its method instead.
**389 is a floor, not a measurement**, and the 12 speculative depth-3 nodes are
evidence about the extraction, not about the institute. No mapping pass has been
run at depth 3, so the `corpus_names` and `corpus_mentions` columns are left
**empty on every level-3 row** rather than filled with grep-level approximations;
what support exists is described in words in each row's `notes`.
