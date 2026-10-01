# Sector of application — axis derivation

*What economic or operational activity does this work serve?*

Derived 2026-09-28 against `AXES.md` §7b, with §1, §4, §5, §7, §8b and §9 as
constraints and `GRANULARITY_AUDIT.md` as the acceptance test. Node list in
`nodes.tsv`: **13 level-1 rows (12 substantive + `uninformative`), 27 level-2
rows, 40 nodes total.**

Headline: the axis claims **244 of 2055 corpus names / 389 mentions**. That is
**4.2x the ~93 mentions AXES.md §7b predicts**, and §6 of this document explains
why the prediction was low rather than why the derivation is loose.

---

## 1. Standard followed: ISIC Rev.4

**ISIC Rev.4** (UN, 21 sections A–U). Named once here and used consistently;
`source_code` on every node is an ISIC section or division.

Why ISIC and not the alternatives:

- **GICS is disqualified by construction.** GICS classifies *companies for
  investors*. It has no Public administration sector, no Education sector, and
  files health providers and pharma together under one Health Care sector. Three
  of this axis's twelve branches (public administration, education, healthcare &
  social care — 186 of 389 mentions) would have nowhere to go or would fuse.
- **NACE and NAICS are regional derivatives of ISIC.** NACE is ISIC with EU
  detail; NAICS diverges in its top level but answers the same question. Using
  the parent standard keeps the survey readable outside its own jurisdiction,
  which matters because the sibling axis (§7) is on **OECD FOS** — also a
  UN-family international standard. Pairing OECD FOS with ISIC keeps both axes
  on standards that are defensible without us, which is §7's whole argument for
  going external in the first place.
- ISIC is **activity-based**, which is literally this axis's question. GICS and,
  to a lesser degree, NAICS are entity-based.

Two places where NAICS is cited as corroboration for a deviation, never as
arbitration: the D+E merge, and the "utilities" label.

### Deviations from ISIC, each justified

| # | Deviation | Justification |
|---|---|---|
| D1 | **D + E merged** into `energy-and-utilities` | ISIC splits electricity/gas (D) from water/waste (E). E has one corpus name; as its own L1 it could never hold two substantive children, and "utilities" is the register a funder uses. The merged node is exactly NAICS 22. |
| D2 | **F + L + M71.1 merged** into `built-environment` | The corpus cluster (11 mentions) straddles construction, building operation and planning. No single ISIC section holds it, and *built environment* is the established cross-sector term for the union. |
| D3 | **`environment-and-natural-resources` promoted to L1** with no ISIC section behind it | ISIC has no environment section; the activity is scattered across E39, O84.12, A02 and S94. Its operational owners (environment ministries, conservation authorities, civil protection) are real and distinct from both science and general government. Filing 13 mentions under `public-administration` would make them unreadable — "we work with the public sector" is not the statement the work supports. **This is the axis's one register mismatch at L1 and it is declared, not hidden.** |
| D4 | **Games (J58.21) and live arts (R90) held inside `media-and-entertainment`** | ISIC files game publishing under publishing and performing arts under section R. Every business-facing classification reports them as one sector, and the corpus cluster is games-plus-content-recommendation-plus-creative-tools. |
| D5 | **Advertising (M73) held in `retail-and-consumer-services`** | Its customer is the brand, not the ad agency. |
| D6 | **ISIC M excluded entirely** | M72 is "Scientific research and development". Admitting section M would make every paper in the corpus an M72 paper. This is the §9 rule *"reject names general enough to attract out-of-scope entries"* applied to a whole ISIC section. |
| D7 | **Health-professions education filed under P (Education), not Q** | ISIC 85.42 is unambiguous: teaching is teaching. See §5 for the cost. |
| D8 | **ISIC B, I, L, N, S, T, U dropped as L1s** | Mining, accommodation & food service, real estate, administrative support, other services, households, extraterritorial bodies. Zero corpus support and (except real estate, folded into D2, and food service, folded into retail) no plausible near-term claim. Kept as declared blind spots in §7, not as empty nodes. |

---

## 2. Where AXES.md is silent, ambiguous or self-contradictory

**A. §7b double-claims healthcare and never notices.** §7b's candidate L1 list
contains "healthcare delivery". §7 simultaneously lists `Healthcare` (16) among
the *discipline* axis's branch-level surfaces, alongside `Neuroscience` and
`Bioinformatics`. Nothing reconciles them. I resolve it by claiming `Healthcare`
on **both** axes (§3, rule S-D3) — but the file should say so, because the
silent version of this is two agents producing incompatible surface maps for the
single largest name on either axis.

**B. §7b's own worked examples are not in the corpus.** §7b offers three
exemplars of an economic activity: `Public Transportation`, `Supply Chain
Optimization`, `Renewable Energy Forecasting`. Only the third exists as a corpus
name (1 mention). **There is no `Supply Chain` name anywhere in the 2055** —
checked by substring. The canonical example of this axis is invented. That is
not fatal (the corpus does not arbitrate) but it means §7b's intuition about
what this axis catches was never checked against the vocabulary.

**C. The ~93-mention estimate is an artefact of an incomplete candidate list.**
Summing only the branches §7b names, and excluding healthcare, gives **103
mentions** — within noise of its ~93. So the estimate silently assumed
(i) healthcare goes to discipline, contradicting §7b's own list, and (ii) the
three largest real sectors in this corpus are not on the list at all: **software
& IT services (89), education (25), environment & natural resources (13)**.
"Thin, ~93" is therefore a statement about the candidate list, not about the
corpus.

**D. §7b gives a name-level test but no *object*-level test, and the name-level
test alone is unusable.** "Field of study vs economic activity" fails on the
names that matter: `Software Engineering` has journals *and* firms;
`Power Systems` is an IEEE society *and* a grid; `Health Informatics` is a degree
*and* a hospital IT department. §7b's escape hatch — "the few that are genuinely
both map in both axes" — describes **~150 of my 389 mentions**, not "a few". §3
below supplies the missing test.

**E. §7b's headline "genuinely both" example is wrong on this axis.**
`Operations Management` is offered as the name that maps in both axes. On the
sector axis it lands in `uninformative`: it is on-axis (an economic activity) but
names **no sector** — the corpus surface is about supply chains *and* retail
operations at once. The §8b distinction between "no value" and "uninformative
value" is exactly what §7b's example needed and did not get.

**F. Silence on task names.** §4 routes `Recommender Systems`, `Anomaly
Detection`, `Code Generation` to Task. It never says whether a task name may
*also* carry a sector. Left unstated, `Recommender Systems` (16 + `Recommendation
Systems` 3 + `Fairness in Recommender Systems`) would be the single easiest way
to inflate this axis. Rule S5 below closes it.

**G. Silence on the reflexive/governance block.** §2 makes the properties axis
reflexive ("the object of study is the AI system") and §8b absorbs `AI Ethics`
and `Responsible AI` there. It does not say where `AI Governance` (3),
`AI Policy` (2), `AI Regulation`, `Governance of AI`, `AI Safety and Regulation`
(2), `Regulatory Science` go. They look like public administration — the
operational owner is a regulator. I decline them (rule S6): the object is the AI
system, and admitting them would put ~10 mentions on two axes for the same
reason twice. Worth writing down in §8b.

**H. Ambiguity between §2's Frugal AI and this axis's energy names is real and
under-specified.** §2 argues the split with `Renewable Energy Forecasting` vs
`Green AI`. The corpus has a harder case: `Energy Efficiency` (1), which reads
as Frugal AI and is in fact radio-access-network power consumption under a QoS
constraint. Resolved here to telecommunications; declared as a homonym.

---

## 3. The discipline/sector boundary — the operative section

### The rules

§7b's name-level test is necessary but not sufficient. I add an object-level
test underneath it, and the two together decide every claim.

- **S1 — exists without AI.** Inherited verbatim from §7, including its clause
  that it applies *to the activity served, not the name's surface*. This is what
  keeps `MLOps` in (IT operations exist without AI) and throws `Recommender
  Systems` out (they do not).
- **S2 — object-of-operation test.** The name's referent must be a **human-run
  operating activity** — an organization's process, service, network, facility,
  plant or market — and not a natural or social phenomenon, and not a body of
  knowledge about one.
- **S3 — named owner.** You must be able to name the firm, agency or provider
  whose problem it is, without inventing one.
- **S4 — machinery excluded.** An OR problem class or a technique names
  machinery, not a customer: `Vehicle Routing Problem`, `Travelling Salesman
  Problem`, `Job-Shop Scheduling`, `Facility Location`, `Network Design`,
  `Channel Estimation`, `Program Analysis`, `Mutation Testing`. This is §7's
  "supplies the problem, not the machinery" carried across.
- **S5 — bare task names excluded.** A Task name alone names no sector
  (`Code Generation`, `Summarization`, `Anomaly Detection`, `Recommender
  Systems`). A task name **qualified by a sectoral object** does
  (`Fraud Detection` → payments; `Traffic Signal Control` → road operations;
  `Movie Recommendation` → content).
- **S6 — reflexive names excluded.** If the object is the AI system, the name
  belongs to Desired properties or Method, whatever sector the demand comes from
  (`AI Governance`, `Model Risk Management`, `Machine Learning Security`).

### S-D3: when does discipline ALSO claim a name?

> **Discipline only** when the object of knowledge is natural or social reality
> — matter, life, disease, mind, society, markets-as-phenomena.
> **Both axes** when the object of knowledge is *itself a human-built operating
> system* — a grid, a fleet, a hospital's information flow, a software system, a
> network, a city.
> **Sector only** when the name denotes the operation and no research community
> claims it.

This is the rule that makes §7b's "genuinely both" workable instead of a
loophole. It is also falsifiable: it predicts that `Bioinformatics` (object:
biological data → nature) is discipline-only while `Health Informatics` (object:
the care system's information machinery) is both, and that is the answer §7
independently reached for `Bioinformatics`.

### Per-name disposition of everything I claim

| name (mentions) | my node | does discipline ALSO claim it? | rule |
|---|---|---|---|
| `Software Engineering` 36, `Empirical Software Engineering` 3 | software & IT services | **yes** — OECD 1.2/2.2, exactly where §7 puts it | S-D3 both: object is software systems, a human-built operating system with its own research community |
| `Software Testing` 5, `Software Maintenance` 2, `Requirements Engineering`, `Software Reliability Engineering` | software & IT services | yes (SE subfields) | S-D3 both |
| `DevOps`, `MLOps`, `Technical Debt` 2, `Continuous Integration`, `Software Startups`, `Remote Work`, `Open Source Software Development` ×3, `Software Documentation`, `Industry 4.0` 2 | software & IT services | **no** — industry practices, no field claims them | S2+S3, sector only |
| `Cybersecurity` 3, `IoT Security`, `Vulnerability Detection`, `Digital Forensics`, `Security in Infrastructure as Code` | software & IT services (depth-3 cybersecurity) | yes (2.2) | S-D3 both; distinguished from `Machine Learning Security` (S6, reflexive) |
| `Telecommunications` 3, `5G Communications`, `Wireless Networks`, `Cellular Network Optimization` 2, `Self-Organizing Networks`, `Satellite Communication Systems` | telecommunications | **yes** — OECD 2.2 | S-D3 both: the object is an operated network |
| `Computer Networks` 2, `Communication Systems`, `Communication Networks` 2, `OFDM Systems`, `Multi-Channel Access Techniques`, `Channel Estimation` | **not claimed** | discipline only | S4 / field-of-study surface |
| `Power Systems` 3, `Optimal Power Flow`, `Smart Grids`, `Demand Response` 2, `Energy Systems` 2, `Grid-Edge Technologies` | electricity & grid | **yes** — OECD 2.2 for the first, no for the rest | S-D3 both for `Power Systems` (an IEEE society *and* a grid); sector only for the operations names |
| `Renewable Energy Forecasting`, `Energy Market Modeling`, `Energy Storage`, `Thermal Energy Storage`, `Electric Vehicle Charging Detection`, `Energy Consumption Pattern Recognition` | electricity & grid | **no** | S2+S3 |
| `Public Transport`, `Operational Research in Public Transportation`, `Operational Research in Transportation`, `Vehicle and Crew Scheduling Problem` | public transit | **no** | S3; this is the owner's fleet-routing case, and the whole point is that discipline must *not* claim it |
| `Transportation Research` | public transit | **yes** — a field whose object is the transport system | S-D3 both |
| `Autonomous Driving` 5, `Autonomous Vehicle Simulation`, `Traffic Signal Control` 2, `Autonomous Mobility on Demand`, `Traffic Scene Generation` | road traffic & AVs | yes for `Autonomous Driving` (robotics, 2.2/2.3); no for the traffic-operations names | S3; see §4 for why `Autonomous Driving` is the weakest claim on the axis |
| `Transportation` 2, `Transportation Networks` | freight & logistics / branch-level | no | S2 |
| `Aviation Emissions`, `Aircraft Systems Simulation` | air transport | yes (2.3) for the simulation name | S-D3 |
| `Manufacturing`, `Thermomechanical Processing`, `Chemical Process Optimization`, `Production Control`, `Carbon Capture` ×2 | manufacturing | **yes** — OECD 2.4/2.5 for the materials/chemistry content | S-D3 both: object is a plant process |
| `Urban Planning`, `Buildings and Urban Planning` | urban planning | **yes** — OECD 5.7 | S-D3 both |
| `Building Information Modeling`, `Data-driven Building Models` 3, `Building Energy Management Systems`, `Energy Management in Buildings`, `Energy Prediction in Buildings`, `Deep Learning for Smart Buildings`, `Building and Indoor Environment Modeling`, `Energy Management` | built environment | **no** for the operations names; yes (2.1) for BIM | S3 |
| `Healthcare` 16 and the AI-in-healthcare umbrella family (~44 total) | healthcare & social care, **at depth 1** | **yes** — §7 already assigns it | S-D3 both; this is contradiction (A) above |
| `Health Informatics` 8, `Healthcare Informatics` 4, `Medical Informatics`, `Biomedical Informatics`, `Health Data Science` | health system administration | **yes** — OECD 3.3 | S-D3 both; contrast `Bioinformatics`, discipline-only |
| `Health Services Research` 2, `Healthcare Services Research`, `Health Policy`, `Healthcare Policy Analysis`, `Health Technology Assessment`, `Healthcare Access`, `Health Equity` | health system administration | yes for the `Research` surfaces (3.3) | S-D3 both |
| `Public Health` 12, `Public Health Surveillance` 3, `Global Health` 5, `Social Determinants of Health` | public & population health | **yes** for `Public Health` and `Global Health` (3.3); no for the surveillance programmes | S-D3 both — `Public Health` is the cleanest genuinely-both name on the axis |
| `Shared Decision Making` 5+1, `Patient-Centered Care`, `Family-Centered Care` ×2, `Doctor-Patient Communication`, patient-experience family | patient & caregiver support | **no** | S2+S3 |
| `Digital Health` 6, `Telemedicine` 3, `Mobile Health` 2, `eHealth`, `mHealth` | clinical services | no | S1 (care delivery exists without AI) + S3 |
| `Emergency Medical Services`, `Emergency Care`, `Trauma Care` 2, `Prenatal Care`, `Community-based Primary Health Care` | clinical services | **no** — these name services, not specialties | S2; contrast `Pediatric Surgery` 16, `Oncology` 7, `Psychiatry` 13, all discipline-only |
| `Medical Education` 7 and the surgical-training family | professional & continuing education | yes (5.3 educational sciences / 3.3) | S-D3 both |
| `Education`, `Educational Technology`, `Educational Data Mining`, `Intelligent Tutoring Systems`, `Computer Science Education`, `Programming Education` | general & higher education | **yes** — OECD 5.3 | S-D3 both |
| `Environmental Monitoring` 4, `Air Pollution`, `Greenhouse Gas Emissions Analysis`, `Biodiversity Monitoring` 2, `Environmental Conservation`, `Spatial Prioritization`, `Disaster Management`, `Fire Monitoring`, `Earthquake Monitoring` | environment & natural resources | **no** — these are programmes; the science beside them (`Ecology` 5, `Conservation Biology` 4, `Climate Science` 2, `Environmental Science`) is discipline-only | S2 |
| `Finance`, `Finance and Economics`, `Portfolio Optimization`, `Fraud Detection` | finance & insurance | yes for `Finance and Economics` (5.2) | S-D3 |
| `Public Policy Analysis using AI`, `Policy and Governance`, `Policy Recommendations`, `Economic Policy Simulation`, `Social Welfare Optimization`, `Climate Governance`, `Human Trafficking Detection` | public administration | yes for the policy-science surfaces (5.6) | S-D3 |
| `Agricultural Data Analysis`, `Agriculture and Land Use`, `Forest Biomass Monitoring`, `Forest Change Detection`, `Biomass Estimation` | agriculture, forestry & fishing | no — the science beside them (`Plant Biology` 3, `Soil Science`, `Ecophysiology`) is discipline-only | S2 |
| `Consumer Behavior`, `Fashion Sustainability`, `Revenue Management`, advertising ×2 | retail & consumer services | yes for `Consumer Behavior` (5.1/5.2) | S-D3 |
| `Game Development`, `Game Design and Analysis`, game-testing family, `Movie Recommendation`, `Music Recommendation Systems`, `Cultural Content Recommendation` 2, `3D Animation`, `Creativity Support Tools` 2, `Creative AI` | media & entertainment | no | S3+S5 (task qualified by sectoral object) |

**Summary of the boundary.** Of 244 claimed names, roughly **90 are claimed by
both axes** and **~154 are sector-only**. The both-axes set is dominated by two
blocks — software engineering (~50 mentions) and the health-services/informatics
block (~45) — and in both cases the doubling is *correct*: the paper does advance
the field's knowledge **and** the field's object is somebody's operation. The
sector-only set is where the axis pays for itself: transit scheduling, demand
response, building energy, patient experience, conservation monitoring, content
recommendation. None of those has a discipline whose knowledge is advanced.

**The direction of error I guarded hardest.** §7b exists because mapping
fleet-routing to civil engineering over-claims *discipline*. The mirror error —
mapping every clinical specialty to healthcare-delivery — over-claims *sector*
and would make this axis a lossy copy of OECD branch 3. Rule S2 blocks it:
**a clinical specialty names a body of knowledge, and the sector value it would
produce ("healthcare") is the same for all of them and therefore carries no
information.** That decision alone keeps ~200 mentions (`Medical Imaging` 51,
`Pediatric Surgery` 16, `Psychiatry` 13, `Oncology` 7, `Brachytherapy` 8,
`Radiation Therapy` 7, `Epidemiology` 20, …) off this axis.

---

## 4. Names rejected, with the test that rejected them

| name (mentions) | looks like | rejected by |
|---|---|---|
| `Recommender Systems` 16, `Recommendation Systems` 3 | retail / media | S1 (fails "exists without AI", per §7) + S5. **The largest available stretch on the axis, and it is refused.** |
| `Medical Imaging` 51, `Pediatric Surgery` 16, `Psychiatry` 13, `Epidemiology` 20, `Oncology` 7, `Brachytherapy` 8, `Radiation Therapy` 7, `Radiology`, `Cardiology`, … (~200) | healthcare delivery | S2 — a specialty is knowledge; the sector value would be constant and uninformative |
| `Drug Discovery` 7, `Drug Repurposing`, `Retrosynthetic Planning` 2, `Molecular Design` 2, `Materials Discovery` | pharmaceuticals / manufacturing | S2 — the object of knowledge is a molecule, i.e. nature, even though the operational owner is a firm. **Pharmaceuticals is consequently a blind spot inside a claimed L1**; see §7 |
| `Robotics` 26, `Robotic Manipulation` 4, `Swarm Robotics`, `Multi-Robot Systems`, `Human-Robot Interaction` | manufacturing / logistics | S2 — a field of study (OECD 2.2/2.3). §7 already demotes it |
| `Operations Research` 19, `Game Theory` 20 | many | §7 verbatim: supply machinery → Method |
| `Vehicle Routing Problem` ×3, `Travelling Salesman Problem`, `Job-Shop Scheduling`, `Facility Location` ×2, `Network Design` 2, `Personnel Scheduling` | transport / manufacturing | S4 — named OR problem classes. Quotes confirm: "applied to other CVRP variants and also to other routing problems" |
| `AI Governance` 3, `AI Policy` 2, `AI Regulation`, `Governance of AI`, `AI Safety and Regulation` 2, `Regulatory Science`, `Model Risk Management` (~11) | public administration / finance | S6 reflexive → Desired properties. Quote check on `Model Risk Management`: it is AI safety frameworks, not bank model risk |
| `Conservation Biology` 4, `Biodiversity Modeling`, `Biodiversity Informatics`, `Ecological Modelling`, `Species Distribution Modeling` 3+2, `Climate Science` 2, `Environmental Science`, `Soil Science`, `Plant Biology` 3 (~20) | environment | S2 — science, not programme. Claiming them would double the environment branch |
| `Misinformation Detection` 3, `Fact-checking`, `Toxicity Detection`, `AI content detection` | media & entertainment | S3 — no nameable operational owner; platforms, newsrooms and regulators all plausible. Left unclaimed rather than guessed |
| `Social Media Analysis` 3, `Social Media Analytics` | media | **declared homonym**: computational social science (majority reading) vs platform operations (this corpus's quote — "information asymmetry between a platform and its users"). Defaults to no value |
| `Internet of Things`, `Edge Computing`, `Mobile Edge Computing`, `Blockchain Technology`, `Cyber-Physical Systems` 2, `Autonomous Systems` 2 | several | S2 — technologies, not activities. Quote check: `Blockchain Technology` is swarm-robotics security |
| `Energy Prediction` | energy | **homonym**: adsorbate–catalyst relaxed energy. Computational chemistry → discipline |
| `Parallel Transmission`, `Radio Frequency Interference Mitigation` | telecommunications | **homonyms**: MRI parallel-transmit RF coils; radio-astronomy RFI |
| `Health Economics` 3, `Pharmacoeconomics`, `Econometrics`, `Behavioral Economics` | finance / healthcare | S2 — economics studies markets as phenomena → OECD 5.2 |
| `Decision Support Systems` 2, `Resource Allocation`, `Scheduling`, `Predictive Analytics`, `Risk Assessment`, `Accessibility` | several | S3 / too generic. `Scheduling`'s quote is physician scheduling, but the surface would attract everything |
| `Code Generation` 7, `Program Synthesis` 3, `Text Summarization`, `Machine Translation` 15 | software / media | S5 — Task names |
| `Aerospace Engineering`, `Electrical Engineering`, `Environmental Engineering`, `Chemical Engineering`, `Biomedical Engineering` | several | §7b's own test: engineering disciplines are fields of study |

### Homonyms declared for this axis (extending §8b's list)

`Energy Efficiency` (telecom power vs Frugal AI) · `Energy Prediction`
(chemistry) · `Industry 4.0` (software ecosystems, not factories) ·
`Parallel Transmission` (MRI) · `Radio Frequency Interference Mitigation`
(astronomy) · `Model Risk Management` (AI risk, not bank model risk) ·
`Social Media Analysis` (social science vs platform operations) ·
`Security` (code vulnerabilities vs model security) · `Scheduling` /
`Personnel Scheduling` (clinic rosters vs OR problem class) ·
`Network Optimization` (IT load balancing vs telecom vs neural nets) ·
`Environmental Monitoring` (agency programme vs field ecology).

---

## 5. Costs accepted deliberately

Stated in the same register as §7's "neuroscience splits three ways".

1. **The health-sector total is not a single node.** Medical education (~17
   mentions) sits under Education; environmental health sits under public &
   population health; clinical specialties sit on the discipline axis entirely.
   No `NodeCut` returns "all health-sector work", and summing across branches is
   not something `NodeCut` does. This is the price of using ISIC honestly.
2. **Software & IT services is the largest node on the axis (89 mentions).**
   That is a true fact about this institute — software engineering is its
   third-largest arXiv category per §7 — but it will read oddly in a sector table
   headed "who do we serve". Reported, never engineered away (§2's phrasing).
3. **Cybersecurity is a depth-3 node, not a sector.** Every sector has a security
   function. Filing it under software & IT services keeps that sibling set three
   industries instead of two industries and a function, at the cost of hiding
   ~10 mentions one level down.
4. **`Autonomous Driving` (5) is claimed and is the weakest claim on the axis.**
   It names a product capability, not an activity; its papers are perception and
   control papers. It is admitted only because S3 passes cleanly (car makers,
   mobility operators) and because dropping it would leave `road-traffic-and-
   automated-vehicles` with 5 mentions of traffic operations. **If one claim in
   this file is to be reversed, reverse this one.**

---

## 6. Does the axis earn its keep?

### The case against, stated first and honestly

- **§7b budgeted ~93 mentions.** An axis that optional and that thin arguably
  belongs as a handful of extra values on the discipline axis, which is precisely
  the "defensible fallback" §2 concedes for the properties axis.
- **~90 of 244 claimed names are claimed by both axes.** A reader could say the
  two axes are 37% redundant by name count and that the redundancy is
  concentrated exactly where the volume is (software engineering, health
  services).
- **The corpus cannot support the granularity.** Nine of 27 level-2 nodes have
  ≤2 corpus names; one L1 (`fishing-and-aquaculture`'s parent branch) rests on
  five mentions; `discrete-manufacturing` rests on one. Half this tree is
  argued, not observed.
- **Mapping cost is real.** §1 prices each axis at 2055 decisions. This axis
  spends them to put **12% of names** somewhere and to leave 88% blank.

### The case for, and my verdict

**The axis earns its keep, and by a wider margin than §7b expected.**

1. **The measured volume is 389 mentions, not 93** — 4.2x the estimate, because
   the estimate omitted software & IT services, education and environment, and
   was internally inconsistent about healthcare. At 244 of 2055 names this is not
   a boutique axis; it is comparable in size to §6's Graphs branch (161) plus
   Time series (80) combined.
2. **The sector-only half — ~154 mentions — has no home anywhere else.** Transit
   scheduling, demand response, building energy management, patient-experience
   work, conservation monitoring, content recommendation, technical debt. Without
   this axis they either vanish or get force-fitted into a discipline they do not
   advance, which is the exact error §7b was created to stop. That is the test
   §1 sets — *two papers differ on this property while agreeing on every other
   axis* — and it passes in both directions, as §7b already argued.
3. **The both-axes overlap is a feature, not redundancy.** §3's clarification in
   §4 of AXES.md settles this: mapping one name in two axes is the faceted
   design, not hedging. `Software Engineering` → discipline 1.2 **and** sector
   software & IT services is the same statement as `Quantization` → Method **and**
   Frugal AI, which §2 calls "the strongest argument in the thread for the
   faceted design".
4. **It is the only axis that answers the question funders actually ask.** OECD
   FOS answers "what science do you do". Nobody funds a sector table by accident.

**Condition on the verdict:** the axis earns its keep *at the level-1
granularity delivered here*. If the mapping pass finds level 2 unusable — and
`discrete-manufacturing`, `design-and-construction` and `water-and-waste-services`
are each one name — cut the report at level 1 and keep the tree. Level 1 alone
still carries the finding.

---

## 7. Blind spots kept

Zero corpus support, kept or declared because the corpus bounds scope and
exposes blind spots without arbitrating (§9).

**Kept as nodes:** `fishing-and-aquaculture` (ISIC A03) — the only empty node in
the tree, kept because it is an ISIC division and its absence is a finding.

**Declared but not given nodes** (adding an empty L1 for each would fail the
branching-factor and >=2-children rules):

- **Mining & quarrying (ISIC B).** Zero names. Notable for a Canadian institute.
- **Defence (ISIC O84.22).** Zero names. Notable for the same reason, and its
  absence should be *stated* in the survey rather than inferred.
- **Insurance (ISIC K65).** Zero names, inside a claimed L1.
- **Pharmaceuticals (ISIC C21).** ~12 mentions of drug-discovery names exist but
  are rejected by S2 as chemistry. So pharma is a blind spot *created by a rule*,
  not by the corpus — the most reversible decision in this file after §5.4.
- **Supply chain & warehousing (ISIC H52).** Zero names, despite §7b naming it as
  the canonical example.
- **Accommodation & food service (ISIC I).** Zero names, although a corpus paper
  is about recipe ingredient substitution — the name it emitted was `Natural
  Language Processing`. Direct evidence that extraction under-names sectors.
- **Law & justice, taxation, benefits administration, immigration** (inside
  ISIC O). Zero names each.
- **Real estate (ISIC L), administrative & support services (N), other services
  (S), households (T), extraterritorial (U).** Zero names.

**Systematic blind spot, and the important one:** the extraction asks for
*research domains*. A paper whose sector is obvious from its dataset will not
name the sector at all — it names its method and its modality. The 389 mentions
here are therefore a **floor**, and the axis's true coverage is unmeasurable
without either a sector-specific extraction field or a pass over
`PaperExtractions.datasets`. This mirrors §4's "blocker is data, not design" for
the Task axis and should be recorded the same way.

---

## 8. Granularity audit of this output

Applying `GRANULARITY_AUDIT.md`'s test — *are these the same kind of thing, at
the same level of specificity, and does any sibling exist only because it was
large in this corpus?*

**Root (12 substantive L1 + 1 admin).** Eleven are ISIC sections or declared
unions of ISIC sections. **One is not: `environment-and-natural-resources`.**
This is the same *kind* of defect as D1 in the audit (`Molecular & biological
data` promoted into a sibling set of signal kinds) — a register mismatch at
level 1 — but it differs in the way that matters: it is not corpus-volume-driven
(13 mentions, 7th of 12), it is argued from operational ownership, and it is
declared in the node's own `notes` and source_code field. **Self-assessed:
one declared defect at the root, no undeclared ones.**

**Does any sibling exist only because it was large here?** No. The three largest
branches (healthcare 154, information & communication 116, education 25) are all
ISIC sections that would exist at any institute. The test's motivating failure —
`Neuroscience` promoted to L1 at 84 mentions while `Chemistry` was not at 43 —
cannot recur here, because level 1 is not ours.

**Conversely, does any sibling exist despite being empty?** One:
`fishing-and-aquaculture`. Declared.

**Level-2 sibling sets, one principle each:**

| branch | principle of division | verdict |
|---|---|---|
| agriculture | ISIC divisions A01/A02/A03 | clean |
| manufacturing | production type (process vs discrete) — the sector's own primary split | clean; `discrete-manufacturing` has 1 name |
| energy & utilities | which utility service | clean |
| built environment | life-cycle stage (plan → build → operate) | clean |
| transportation | service segment | **mild defect**: three passenger modes plus one cargo function. Comparable to audit D4. Fixing it (passenger/freight at L2, modes at L3) would bury transit and AV — the two informative nodes — at depth 3 |
| information & communication | which industry inside ISIC J | clean, after folding cybersecurity to depth 3 rather than letting a *function* sit beside two industries |
| environment & natural resources | what is being managed (ambient quality / living systems / hazards) | clean, after moving the generic `Environmental Monitoring` surface to branch-level residence |
| education | education segment | clean |
| healthcare & social care | **which actor in the health system** (provider / patient / administrator / population agency / social-care agency) | clean; five siblings, one principle. Digital health is folded into clinical services as a *channel* rather than made a sibling, because a channel is not an actor |

**Branching factor.** L1 = 13. Nine parents hold 27 children: mean 3.0, range
2–5. Three L1s are leaves (`finance-and-insurance`, `public-administration`,
`retail-and-consumer-services`) because inventing a second substantive child
from 4–7 mentions would satisfy §9 formally and violate it in substance. No
parent has one child.

**Compound names.** Two fused names are used and both are the sector's own
established label: **Media & entertainment** and **Built environment**.
`Agriculture, forestry & fishing` and `Public administration` are ISIC's own
section titles. Everything else is a single concept.

**Branch-level residence** (§8b), by design and reported here so depth-2 shares
are quotable against an honest denominator:

| branch | mentions at depth 1 | share |
|---|---|---|
| healthcare & social care | 45 of 154 | 29% |
| public administration | 7 of 7 | 100% (leaf) |
| finance & insurance | 4 of 4 | 100% (leaf) |
| retail & consumer services | 5 of 5 | 100% (leaf) |
| environment & natural resources | 4 of 13 | 31% |
| transportation & logistics | 1 of 20 | 5% |
| **axis total** | **66 of 389** | **17%** |

Close to the ~25% §8b measured on the discipline axis, and for the same reason:
umbrella surfaces name the branch and nothing narrower.
