# Sector of application — depth-3 draft, PHASE 1 (semantic, no corpus)

Written 2026-09-29, **before** any access to `domain_names.tsv`, any tally, or
any use of the `examples` column. This file is the record required by
`AXES.md` §9 step 2 and is **never edited**. Every later change lives in
`DEPTH3_RATIONALE.md` as a diff against this text.

## Disclosure of what was in front of me while drafting

Honest, because §9's whole point is that compliance be checkable:

- I did **not** open `domain_names.tsv`, ran **no** tally, and did not look at
  any count column, at `arxiv_primary_sample.tsv`, `tail_sample.tsv`, or at any
  of the forbidden paths.
- I **did** read `nodes.tsv` and `RATIONALE.md`, because the brief and §9
  require the parents' characteristics and the declared ISIC deviations. Both
  files contain corpus material the phase-1 rule would otherwise exclude:
  `nodes.tsv` carries an `examples` column and count columns in the same rows as
  the characteristics, and `RATIONALE.md` §3–§4 is a per-name disposition table.
  I could not read the mandated content without them being on screen.
  **I did not use either as a seed**: every sibling set below is derived from the
  activity's own structure and from ISIC Rev.4's lower level where one exists,
  and I state the external structure I used for each. Where a child happens to
  match an `examples` string, that is the examples column doing its §9 job (a
  step-3 checklist), not a step-1 seed. This is a declared, partial exposure, not
  a claim of zero exposure.

## Method used for each node

Three tests, applied in order, before anything is written down:

- **T1 — does the activity have its own division?** An ISIC Rev.4 lower level
  first; otherwise the structure the sector itself uses (a recognised framework,
  a value chain, a set of owning bodies). If neither, the node is a leaf.
- **T2 — would a person who funds or directs research read the children as
  different working relationships?** ("we work with mobile operators" /
  "we work with school boards"). If not, the node is a leaf.
- **T3 — does the set refine *this parent's own* characteristic?** Not another
  axis's, not the grandparent's, and not a second principle bolted on.

One principle per set, stated. The property test of `AXES.md` §6 is used
throughout: **a modifier that can be true of a node's siblings is a property,
not a sibling** — this is what keeps objectives, scopes and technologies out of
sibling sets.

---

## 1. `software-and-it-services` (ISIC J62–J63) — 4 children

**Principle: which function of the software & IT industry owns the system the
work acts on.** The parent's own positive test already names three of them —
"a development team, IT operation or security function" — and ISIC's own split
of J62 (programming / consultancy & facilities management / other IT services)
from J63 (data processing & hosting) supplies the fourth.

| child | ISIC | characteristic |
|---|---|---|
| Software product engineering | J62.01 | Producing and maintaining the software artefact itself as a team practice: requirements, design, code, review, test, debt, maintenance. |
| IT operations & service management | J62.02 / J62.03 | Running software and IT services in production for an organization: release, deployment, incident, configuration, capacity. |
| Cloud & data-centre services | J63.11 | Selling compute, storage and hosting capacity as a service: placement, utilisation, SLA, facility. |
| Cybersecurity operations | J62.09 | Defending deployed systems, code and data against adversaries, as an operational function. |

Negative tests carried down from the parent: program analysis, fuzzing, mutation
testing and repair are machinery → Method; code generation and summarization are
Task; securing *the model* is reflexive → Desired properties (rule S6).
`Cloud & data-centre services` additionally rejects the energy cost of training
(→ Frugal AI) and distributed-training machinery (→ Method); a data centre seen
as a grid load is energy & utilities.

**Competing principle rejected — the software life cycle (SWEBOK knowledge
areas: requirements → design → construction → testing → maintenance).** It
divides an engineering *process*, which is a curriculum, i.e. a field of study;
it would import the discipline axis one level down, and it has no home for
hosting, which is an industry rather than a stage.

**Declared gap:** online information services and web portals (J63.12, J63.99 —
search, portals, news aggregation) get no node. The audience-facing content
business is held in media & entertainment; the infrastructure behind it is cloud
& data-centre services. Recorded as a possible blind spot for phase 2.

## 2. `health-system-administration` (ISIC Q86 / O84.12) — 4 children

**Principle: which building block of the health system the work runs.** ISIC has
no lower level for the administrative function, so the external structure is the
**WHO health-system building blocks** (service delivery, workforce, information,
financing, medicines & supplies, governance), used the way ISIC is used
elsewhere: for vocabulary and breadth, never arbitration.

| child | ISIC | characteristic |
|---|---|---|
| Care operations & capacity | Q86 | Planning and running the capacity that delivers care: beds, theatres, staff rosters, appointments, patient flow. (WHO: service delivery + workforce.) |
| Health information systems & records | Q86 (+J62) | Running the information machinery of care: records, coding, interoperability, data quality, registries. (WHO: information.) |
| Health financing & coverage | K65.12 / O84.30 — **deviation** | Paying for care and deciding what is covered: reimbursement, claims, cost, utilisation, benefit design. (WHO: financing.) |
| Health policy, planning & governance | O84.12 | Setting priorities, configuring services across a system and regulating them, including access and equity planning and health technology assessment. (WHO: governance.) |

**Deviation declared:** ISIC files health insurance under K65.12 and compulsory
social health insurance under O84.30, i.e. outside section Q. `Health financing
& coverage` is held here because the payer is a part of the health system in the
register a funder reads, and because putting it under finance & insurance would
file a ministry of health under banking. Same form as the parent axis's D1–D5.

**Property-test fold:** `Access & equity` was drafted as a fifth child and
folded into policy & planning — access can be true of operations, financing and
policy alike, so it is a criterion, not a sibling.

**Considered and declined:** `Pharmacy & medical supply management` (WHO's
medicines block, ISIC G46.46 / Q86). Declined as a node and folded into care
operations & capacity as a logistics function, to avoid splitting a node four
ways when one of the four has no operational distinctness from capacity
planning. Recorded for phase 2.

**Competing principle rejected — by level of the system** (unit → hospital →
region → nation). Scale cross-cuts every function (there is information,
financing and governance work at each level), so it is a property.

## 3. `public-and-population-health` (ISIC Q86.9 / O84.12) — 3 children

**Principle: which core public-health function the agency performs.** External
structure: the essential public-health functions as WHO and the US 10 Essential
Public Health Services both state them, collapsed to the three that name
distinct operating programmes.

| child | ISIC | characteristic |
|---|---|---|
| Disease surveillance & outbreak response | Q86.9 / O84.12 | Watching the health of a population and running the response to what is detected: notification, early warning, investigation, tracing, emergency response. |
| Prevention & health promotion programmes | Q86.9 | Running programmes that act before disease occurs: immunisation, screening, risk-factor and behaviour programmes, targeting and uptake. |
| Environmental & occupational health protection | Q86.9 / O84.12 | Protecting a population from exposures in the environment and the workplace, as a health mandate. |

**This is where the discipline boundary is most tempting at depth 3, and the
temptation is named here so it can be checked.** The obvious depth-3 set is
**by disease area** — infectious / chronic / mental / maternal & child. It is
refused: disease is natural reality, so a disease area is discipline-only
(`AXES.md` §7b object-level test; `Epidemiology`, `Oncology`, `Psychiatry` are
already refused at level 2). A sector child named `Infectious disease` would
re-import OECD 3.2 under a sector label and make this branch a lossy copy of it.

**Also rejected by the property test: by geographic scope** (global / national /
local health). Scope can be true of every function.

**Boundary with `environmental-quality-and-emissions`** (sibling L1 branch):
the tiebreak is the mandate named — a health outcome in a population here, a
regulated ambient quantity there.

## 4. `clinical-services` (ISIC Q86.1–Q86.2) — 4 children

**Principle: which care-delivery setting the work serves.** This is ISIC's own
division of Q86 (86.1 hospital activities; 86.21 general medical practice;
86.22 specialist medical and dental practice; 86.9 other human health
activities) and it coincides with the health system's levels-of-care structure.
It refines the grandparent's actor principle rather than replacing it: a setting
*is* the care-delivery organization that owns the decision.

| child | ISIC | characteristic |
|---|---|---|
| Primary & community care | Q86.21 | First-contact and continuing care in the community, owned by a general practice or community clinic. |
| Hospital & acute care | Q86.1 | Care delivered inside a hospital episode: emergency, inpatient, critical and peri-operative services. |
| Specialist & ambulatory care | Q86.22 | Scheduled specialist consultation, diagnostic and day-treatment services outside an inpatient episode. |
| Rehabilitation & continuing care | Q86.9 | Clinical care after the acute episode: rehabilitation, chronic follow-up, home-based clinical care and clinician-owned remote monitoring. |

**The depth-3 temptation, stated:** `Specialist & ambulatory care` is one word
away from re-importing the clinical specialties (`Oncology`, `Radiology`,
`Pediatric Surgery`, `Medical Imaging`, ~200 mentions) that level 2 refused. Its
negative test is therefore explicit: a specialty names a body of knowledge and is
discipline-only; this node is claimed only when the object is the **running of
the service** (referral, access, clinic throughput, day-surgery scheduling), and
never because a specialty is named.

**Competing principles rejected:**
- **By channel** (in-person / tele / mobile / digital). The parent already ruled
  a channel is not an actor and folded digital health in as a delivery channel;
  using it at depth 3 would reverse a level-2 decision by the back door.
- **By stage of the care pathway** (triage → diagnosis → treatment → follow-up).
  Diagnosis and triage are Task names, so the set would drift into the Task axis.

**Boundary:** non-medical residential and home support → social care & community
services (the sibling L2), not rehabilitation & continuing care.

## 5. `professional-and-continuing-education` (ISIC P85.3–P85.4) — 3 children

**Principle: which body in the profession's training system owns the activity.**
The parent's own positive test enumerates exactly three — "a residency
programme, professional college or employer".

| child | ISIC | characteristic |
|---|---|---|
| Entry-to-practice training | P85.3 / P85.49 | Training a novice into a licensed practitioner: residency, clerkship, apprenticeship, supervised practice. |
| Continuing professional development | P85.49 | Keeping qualified practitioners current, run by an employer or a professional association. |
| Certification, licensure & competency assessment | P85.49 / O84.12 | Examining, scoring, certifying and licensing practitioners against a standard. |

Negative tests: the clinical or technical content being taught → discipline; a
simulator or a video model is machinery/modality → Method/Modality; a licensing
body regulating a profession in general (not its training) → public
administration.

**Competing principle rejected — by function (teach vs assess).** It is a clean
two-way split and it is what the parent's characteristic literally says
("training and assessing"), but assessment is owned by a different body from
training in every regulated profession, so the owner principle subsumes it while
also separating initial from continuing training. Recorded because it is a close
call and the two sets are not far apart.

## 6. `patient-and-caregiver-support` (ISIC Q86.9) — 3 children

**Principle: which part of the patient's and family's own role in care the work
supports — deciding, managing, or being heard.** The parent's characteristic
names all three verbs ("what a patient or an informal caregiver knows, decides
or experiences"); this set refines that and nothing else.

| child | ISIC | characteristic |
|---|---|---|
| Patient information & decision support | Q86.9 | Helping a patient understand options and reach a decision with a clinician. |
| Self-management & home support | Q86.9 | Helping a patient or family carry out care day to day: adherence, monitoring they own, assistive support at home. |
| Patient experience & voice | Q86.9 | Collecting and acting on what patients and families report about their care. |

Negative tests: clinician-owned remote monitoring → clinical services >
rehabilitation & continuing care; non-medical home support → social care;
health communication as a social science → discipline 5.8; a provider-owned
quality dashboard → health system administration (tiebreak: whose instrument it
is, the patient's report or the manager's measure).

**Competing principle rejected — by actor (patient vs informal caregiver).** It
refines the parent's compound name most literally, but the two participate in
all three activities together, so the split does not partition the work.

**Lowest-confidence set in this draft.** T1 is weaker here than anywhere else:
the structure comes from the patient-engagement literature rather than from ISIC
or a value chain, and a defensible alternative is to leave this node a leaf.

## 7. `electricity-generation-and-grid` (ISIC D35.1) — 4 children

**Principle: which stage of the electric power chain the work acts on.** This is
ISIC's own lower level, exactly: 35.11 generation, 35.12 transmission, 35.13
distribution, 35.14 trade. The parent's characteristic already enumerates the
same chain ("generating, transmitting, distributing, storing and trading").

| child | ISIC | characteristic |
|---|---|---|
| Power generation | D35.11 | Operating generating assets and forecasting their output. |
| Transmission & system operation | D35.12 | Keeping the bulk power system balanced and secure: flow, commitment, reserves, congestion, stability. |
| Distribution & grid-edge operations | D35.13 | Running the distribution network and the flexible resources connected to it: DERs, EV charging, demand response, metering, outages. |
| Electricity markets & trading | D35.14 | Buying, selling and pricing electric power. |

**Storage is not a child.** It is an asset that sits at every stage of the chain
(generation-side, transmission-side, behind the meter), so by the property test
it is a technology cross-cutting the set; it is filed by where the asset sits,
defaulting to distribution & grid-edge. This makes the parent's own note
("storage sits here rather than as a sibling") operational one level down.

**Competing principle rejected — by primary energy source** (solar / wind /
hydro / nuclear / gas). It divides by generation technology, which is
engineering knowledge (OECD 2.2) rather than an operating activity, it
cross-cuts the chain (a wind farm is generation *and* a market participant), and
ISIC itself divides 35.1 by stage and not by source.

## 8. `telecommunications` (ISIC J61) — 3 children

**Principle: which transmission medium the operator runs.** ISIC's own lower
level: 61.10 wired, 61.20 wireless, 61.30 satellite.

| child | ISIC | characteristic |
|---|---|---|
| Mobile & wireless networks | J61.20 | Operating radio access networks that serve mobile subscribers: coverage, capacity, handover, scheduling, power. |
| Fixed & core network operations | J61.10 | Operating wireline access and the transport core that carries aggregated traffic. |
| Satellite & non-terrestrial networks | J61.30 | Operating satellite and other non-terrestrial links as a carrier service. |

**Declared cross-cut:** service assurance and subscriber management (QoS
assurance, churn, billing, customer care) is a *function* true of all three
media, so it is not a fourth sibling; it sits at the parent node unless the name
says which network. Flagged for phase 2 — if the corpus holds a cluster of
operator-side service-management names with no node, that is a blind spot to add
or justify in writing.

**Competing principle rejected — by network layer** (physical / MAC / network /
service). It is the engineering-knowledge division (OECD 2.2), the sibling axis's
territory, and it slices a single operator three ways.

## 9. `media-and-entertainment` (ISIC J58–J60 + R90) — 5 children

**Principle: which content business owns the work.** ISIC's own division of the
section, plus R90 which the parent already claims by declared deviation D4.

| child | ISIC | characteristic |
|---|---|---|
| Games & interactive entertainment | J58.21 (+R90) | Making and running interactive entertainment products: development, playtesting, content generation, live operation. |
| Screen & recorded media production | J59 | Producing film, television, video, animation, recorded music and sound. |
| Publishing & news media | J58.1 | Producing books, periodicals and journalism, and running the editorial process. |
| Broadcasting & content platforms | J60 (+J63.12) | Programming, scheduling and serving a catalogue to an audience. |
| Arts, culture & heritage | R90 / R91 | Running performing arts, museums, archives and collections as institutions. |

**Declared strain:** ISIC's own sequence mixes producing businesses (58, 59)
with a distributing one (60), so this set is not a pure stage division. The
alternative — **by stage (create → distribute → consume)** — is rejected because
it would split every industry in two and bury games, which is the one node with
an unambiguous operational owner.

`Broadcasting & content platforms` carries the parent's negative test: a
recommender is an output type → Task; the node is claimed only when the operator
of the catalogue or channel is the owner (rule S5, a task qualified by a
sectoral object).

**Widest set in this draft (5).** Declared in the audit rather than trimmed,
because every one of the five is a separately-owned industry, but it is the set
most exposed to the over-splitting failure mode.

## 10. `road-traffic-and-automated-vehicles` (ISIC H49.3–H49.4) — 3 children

**Principle: which operator of the road system acts on the result.** The
parent's own positive test names all three — "a road authority, municipality or
vehicle manufacturer".

| child | ISIC | characteristic |
|---|---|---|
| Traffic management & road operations | H49 / O84.13 | Running the road network itself: signals, flow, incidents, tolling, enforcement. |
| Automated & assisted driving | H49.3 (+C29) | Operating the vehicle itself under automation or driver assistance. |
| Road passenger mobility services | H49.31 / H49.32 | Running on-demand and shared road passenger services: ride-hailing dispatch, fleet rebalancing, shared vehicles. |

Negative tests: perception, planning and control as knowledge → discipline;
simulation engines as machinery → Method; scheduled fixed-route services →
public transit (sibling L2).

**Inherited weakness, restated not repaired:** `Automated & assisted driving`
inherits RATIONALE §5.4 — `Autonomous Driving` names a product capability, not
an activity, and is the claim to reverse first if any is reversed. Putting it in
its own depth-3 node makes that reversal cheap: it can be deleted without
touching the traffic-operations nodes.

**Declared boundary:** road freight haulage (H49.41) is filed with
`freight-and-logistics` by function, although the parent row's code range
nominally includes H49.4. Stated rather than fixed, because level-2 rows are
fixed.

## 11. `general-and-higher-education` (ISIC P85.1–P85.3) — 2 children

**Principle: which education segment teaches the learner.** ISIC's own lower
level: 851 primary, 852 secondary, 853 higher. It continues the parent branch's
stated principle (education segment) rather than switching to a new one.

| child | ISIC | characteristic |
|---|---|---|
| School education | P85.1 / P85.2 | Teaching and assessing in primary and secondary schools. |
| Higher education | P85.3 | Teaching, supervising and assessing in degree-granting tertiary institutions. |

**Competing principle rejected — by institutional function** (instruction /
assessment / student retention & support / admissions). It divides the
institution's internal process rather than naming whose activity it is, and each
function occurs in both segments, so it is a cross-cut. Two substantive children
is the honest answer here; the set is deliberately minimal.

## 12. `building-operations` (ISIC L68 / N81) — **LEAF, no children**

Declared a leaf on T1 and T3.

The four things the parent's characteristic names — comfort, energy, occupancy,
maintenance — are **objectives of one activity**, not four activities. One
owner (whoever operates the building), one asset (the building and its plant)
and usually one system (the building management system) serve all four at once:
the same HVAC controller is tuned for energy cost and for thermal comfort, and
occupancy is an input to both. By the property test, an objective that can be
true of its siblings is a property, not a sibling — so a set
`energy / comfort / maintenance / space` would fail the audit the way
GRANULARITY_AUDIT D2 fails.

The facility-management market does sell energy management, maintenance and
space management as separate contracts, which is the strongest argument for
expanding. It is refused because a contract type is a commercial packaging, not
a different operational owner, and because "we work on building operations" is
already the sentence a funder says. Over-splitting a node this size into four
near-synonymous objectives is the failure mode named in the brief.

---

## Summary of the phase-1 draft

| parent | children | branching | principle |
|---|---|---|---|
| software-and-it-services | 4 | 4 | which function of the software & IT industry owns the system |
| health-system-administration | 4 | 4 | which health-system building block is run |
| public-and-population-health | 3 | 3 | which core public-health function |
| clinical-services | 4 | 4 | which care-delivery setting |
| professional-and-continuing-education | 3 | 3 | which body in the profession's training system |
| patient-and-caregiver-support | 3 | 3 | which part of the patient's own role in care |
| electricity-generation-and-grid | 4 | 4 | which stage of the electric power chain |
| telecommunications | 3 | 3 | which transmission medium |
| media-and-entertainment | 5 | 5 | which content business |
| road-traffic-and-automated-vehicles | 3 | 3 | which operator of the road system |
| general-and-higher-education | 2 | 2 | which education segment |
| building-operations | **leaf** | — | — |

**38 depth-3 nodes across 11 parents; mean branching 3.45, range 2–5.**

Two questions, and only two, go to the corpus next (§9 step 3): a corpus cluster
with no node is a blind spot to add or justify in writing; a node with no corpus
support is kept and flagged speculative. Nothing else may change.
