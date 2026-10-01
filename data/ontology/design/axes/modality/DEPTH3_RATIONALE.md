# Modality / data — depth-3 derivation

Extends `modality2` from depth 2 to depth 3. **Level 1 and level 2 are fixed**;
no existing row was modified. 43 level-3 rows appended to `nodes.tsv` under 15 of
the 29 level-2 nodes; 14 level-2 nodes stay leaves.

Procedure, in the order the owner fixed it:

1. **Phase 1 — semantic draft, no corpus access.** `AXES.md` §6 and the level-2
   characteristics were read; `domain_names.tsv` was not opened, no tally was
   run, and the `examples` column was not read. The draft is
   [`DRAFT_PHASE1.md`](DRAFT_PHASE1.md) and has not been edited since.
2. **Phase 2 — corpus check, two questions only.** *A corpus cluster with no
   node* → blind spot: add a node or justify in writing. *A node with no corpus
   support* → keep it and flag it speculative. Nothing else licensed a change.
3. **Phase 3 — this file**, plus the appended rows.

Volume was used once, for the owner's expansion order. It is used nowhere in
this file to justify a node.

---

## 1. Phase-1 → phase-2 diff, change by change

**No node was added, removed, renamed, merged, split or reordered in phase 2.**
The structure delivered is the phase-1 structure. What phase 2 produced:

| # | change | licensed by | reason |
|---|---|---|---|
| 1 | `tomo-xray` flagged **SPECULATIVE** | *node with no corpus support* | The vocabulary contains **no** CT, radiography or X-ray surface. Kept: the interaction principle is non-exhaustive without it, and never deleted on a count. |
| 2 | `tomo-optical` flagged **SPECULATIVE** | same | Zero support. `Optical Imaging` (1) is ambiguous between this node and microscopy and was not counted for it. |
| 3 | `ms-radar` flagged **SPECULATIVE** | same | Zero support. The only `satellite` surfaces are `Satellite Communication`, which the parent's own negative test routes to Graphs. |
| 4 | `wave-optical` flagged **SPECULATIVE** | same | Zero support; no photoplethysmography, fluorescence-trace or light-curve surface. |
| 5 | `doc-scanned` flagged **SPECULATIVE** | same | Zero support; no OCR, handwriting or scanned-page surface anywhere in 2055 names. |
| 6 | `formal-specs` flagged **SPECULATIVE** | same | Zero support **once the homonym guard is applied**: `Constraint Programming`, `Probabilistic Planning`, `Optimization Models` are Method surfaces under the measured 83%-wrong `programming` rule and AXES.md's planning ruling. |
| 7 | `atom-surface` flagged **effectively speculative** | same | Its two surfaces (`Catalysis`, `Catalyst Design`) are field names that D5 sends to Scientific discipline, so its own support is near zero. |
| 8 | `nl-edited` flagged **indirect support only** | same (partial) | Every counted surface is a *task* name over the text kind; no corpus name states the production setting. |
| 9 | `code-query` flagged **CONTESTED** | neither question — recorded, not acted on | The fixed sibling row `Formal & mathematical notation` lists "Structured queries (SQL, SPARQL)" in its examples, so two nodes claim `Text-to-SQL`. Level-2 rows are fixed and the phase-2 rules license no change here. |
| 10 | indicative `corpus_names` / `corpus_mentions` filled on all 43 rows | — | Hand-assigned in the phase-2 pass, not a keyword run. Indicative, never measured (issue #89). |
| 11 | six blind spots declared (§5) | *cluster with no node* → justified in writing | See §5; none was converted into a node, each with a stated reason. |

### Divergences from the level-2 rows' `examples` column — read in phase 2, acted on in none

The `examples` column carries the level-2 authors' own guesses at depth-3
labels. Eight of them disagree with the phase-1 draft. **None was adopted**: an
illustrative example is neither of the two things phase 2 may act on, and in six
of the eight cases the example fails a rule the axis states.

| level-2 node | its examples | what was delivered | why |
|---|---|---|---|
| `atomistic-structure` | "Small-molecule graphs & conformers; Macromolecular 3-D structure; Crystal & periodic solid" | `atom-finite` holds both small molecules and folds | The row's own **notes** forbid that split ("splitting them would reproduce the chemistry / structural-biology field boundary"). The row contradicts itself; the notes are the rule and the examples are not. |
| `biomolecular-sequences` | "Genomic nucleotide; Transcript & RNA; Amino-acid" | two children, nucleotide and amino-acid | D5 **clause 3**: DNA and RNA come off the same sequencing process, so the most general level that still picks out one signal kind merges them. |
| `omics-profiles` | "Bulk expression; **Single-cell** abundance matrices; **Mass-spectrometry** profiles" | four children by molecular species class | The example set divides by **resolution** and by **platform**, and `single-cell` is true of every child — a property, by the test that killed `Video`. |
| `waveform-signals` | "Bioelectric (EEG…); Vibration & seismic; **Radio & channel**" | bioelectric and radio are **one** node (`wave-em`) | Splitting them puts medicine on one side and telecom on the other, which is the field boundary the level-2 node exists to remove. Clause 3 names the transduced field, not the user. |
| `photographic-imagery` | "Natural-scene; Video; **Close-range clinical photography**" | two children; close-range capture has **no node** | See §4 and §5 — optical access is a property of both children, and admitting it fuses two principles in one sibling set. **This is the largest declared gap in the output.** |
| `document-imagery` | "Scanned pages; **Charts & diagrams**; Screen & UI" | two children | "Charts & diagrams" names depicted **content**, not a formation process. Absorbed into `doc-screen` / `doc-scanned` by how the raster was obtained. |
| `microscopy-imaging` | "Light & fluorescence; **Whole-slide histopathology**; Electron" | two children | A slide scanner *is* light microscopy, and "histopathology" names the ward (D5 clause 1). |
| `sampled-series` | "Transducer telemetry; **Metered utility**; Aggregated counts" | two children | A meter is a transducer; clause 3 merges them. |

---

## 2. The expanded nodes: characteristic, and the principle rejected

One principle per sibling set, stated as the `characteristic` on every row.

| node | characteristic adopted | competing principle rejected, and why |
|---|---|---|
| `natural-language-text` | the setting in which the string was produced and put on record | **By subject-matter domain** (biomedical / legal / financial text) — a straight D5 clause-1 violation and the most tempting cut on the axis. Also rejected: **natively written vs transcribed from speech**, the most instrument-shaped option, because a transcript's provenance can be true of every sibling. |
| `tomographic-imaging` | which physical interaction is measured and reconstructed | **By anatomy or clinical service** (brain / cardiac / chest imaging) — would re-import `Biomedical imagery` at depth 3 after removing it at depth 2. Also rejected: **structural vs functional** (functional is true of MR, PET and CT alike — a property) and **2-D vs 3-D** (mathematical structure). |
| `photographic-imagery` | the exposure regime: what one datum covers | **By platform and optical path** (scene camera / instrument-coupled optics / airborne standoff). Under it, video becomes a property and disappears — contradicting the fixed D2 disposal that places `Video` here. Adopting both fuses two principles (§9). |
| `microscopy-imaging` | what probe the magnifying instrument uses | **By what is on the slide** (histopathology, cytology, materials sections) — D5 clause 1. |
| `multispectral-imagery` | whether the instrument samples radiation it receives or radiation it emits | **By platform** (satellite / airborne / drone) — a property of any sensor, and it names the sector that operates the platform. |
| `range-geometry` | where the coordinates came from: ranged, reconstructed, or authored | **By geometric representation** (point cloud / mesh / voxel / implicit field) — banned twice: mathematical structure, and interconvertible, therefore a property. |
| `document-imagery` | how the raster of symbolic material was obtained | **By document genre** (invoices, forms, papers, charts) — names the purpose and, through it, the filing sector. |
| `atomistic-structure` | the spatial boundary condition of the arrangement | **By provenance, experimentally solved vs computed** — attractive under clause 1, but `RATIONALE.md` §7 already rules a data-*generating* process is not a signal kind, so half the partition would be a Method value. Also rejected: **small molecule vs macromolecule**, forbidden by the parent's notes. |
| `biomolecular-sequences` | which biochemical alphabet the assay read | **The central dogma as a three-way** (clause 3) and **by sequencing protocol** (short/long-read, metagenomic — vendor and pipeline lines, and a property of a run). |
| `source-code` | what interprets the string | **By software-engineering activity** (bug fixing, review, testing) — names the purpose; every child would determine the discipline. |
| `waveform-signals` | which physical field the transducer couples to | **By the organ or field the trace comes from** (neural / cardiac / geophysical / communications) — D5's own worked example one level down; the parent exists because that cut was dissolved. |
| `sampled-series` | how a reading gets into the series: transduced or tallied | **By spatial support** (single-site vs sensor-network / spatio-temporal) — a sensor network can be either child, so it is a property. Also rejected: a **`quoted ledger series`** child, which passes clause 1 but fails clause 2 outright. |
| `omics-profiles` | which class of molecular species the assay quantifies | **By tissue, organism or clinical question** (D5 clause 1), and **by resolution** (`single-cell`, `spatial`) — properties of every child. |
| `interaction-logs` | whether the row records the act or a solicited judgement | **By the sector operating the system** (retail, streaming, education) — D5 clause 1; the parent is already the D5-compliant rename of `User interaction records`. |
| `formal-notation` | which formal calculus the string belongs to | **By mathematical subject** (algebra, geometry, number theory) — names the field of mathematics. |

---

## 3. How the D5 rule held at depth 3

D5 bites hardest here, exactly as AXES.md predicts: at depth 3 the field word is
usually the *only* word the corpus offers. Five cases where naming by instrument
was hard and naming by field was the obvious move.

**3.1 Tomographic imaging — the hardest case, and the one with the most volume.**
The corpus's vocabulary for this node is `Medical Imaging` 51, `Medical Image
Analysis` 10, `Medical Image Segmentation` 9, `Neuroimaging` 28, `Brain Imaging`
3, `Spinal Cord Imaging` 4, `Oncology Imaging`, `Radiomics` 5 — **anatomy, ward
and specialty, almost without exception**. A corpus-shaped depth 3 here is
`Brain imaging / Cardiac imaging / Oncologic imaging`, which is the Scientific
discipline axis wearing a lab coat. The children are named by the reconstructed
interaction instead (attenuation, resonance, echo, emission, optical), which is
*also the field's own word*: in radiology an imaging modality **is** the
interaction. Clause 2 then passes — `tomo-xray` carries industrial CT and
airport inspection as well as chest radiography.
**Cost, stated:** most of this node's mass will report at **depth 2**, because
the corpus names the ward and only MR names the instrument. That is a reporting
limitation produced by D5 compliance, and it is the honest outcome, not a defect
to engineer away.

**3.2 Waveform signals — where the parent's own examples leak and the children do not.**
The row's examples split "bioelectric" from "radio & channel". Both are voltage
transduction; the split is *medicine vs telecom*. `wave-em` merges them under
clause 3 and lets the discipline axis carry the difference. This is the single
clearest place where following the inherited example would have re-opened D5.

**3.3 Sampled quantity series — a node whose only available cut is forbidden.**
The parent's negative test bans division by field, and the corpus offers nothing
else: `Renewable Energy Forecasting`, `Epidemic Modeling`, `Climate Data
Downscaling`, `Energy Prediction in Buildings`. The transduced/tallied cut is
what remains that is a genuine record process — a thermometer and a case count
are different acts of recording, and both span many disciplines. A
`quoted ledger series` child was drafted and refused: it would pass the naming
clause and fail the admission clause, which is the definition of a leak with
better manners.

**3.4 Longitudinal administrative records and measured interaction networks — where the parent's notes *list* the forbidden children.**
Both rows name their intended depth-3 members explicitly — "EHR, claims,
registry, student and court records", "gene networks, connectomes and food
webs". Every one of those determines the Scientific discipline value, so clause
2 refuses all of them, and no D5-safe alternative survives (see §6). Both stay
leaves. This is the rule costing real reportable structure and being applied
anyway.

**3.5 Molecular structure — a field boundary that looks like a signal boundary.**
`atom-finite` vs `atom-periodic` reads like chemistry vs materials science. It
survives because the node is named by the **boundary condition of the
specification** (a lattice or no lattice), which is a fact about the datum, and
because clause 2 passes strongly on both sides: periodic structures carry
battery chemistry, semiconductor physics, mineralogy and pharmaceutical
polymorphs. The *forbidden* version of the same cut — small molecules vs protein
folds — is exactly the one the parent's notes refuse, and it is refused here.

**One place where D5 clause 2 fails empirically and the node stands:**
`micro-electron` has one corpus name, and cryo-EM has essentially one user. This
is AXES.md's stated exception in its literal form — the leak is a naming fault,
not a correlation, and there is no naming fault.

---

## 4. Level-2 nodes deliberately left as leaves

Fourteen. In every case the reason is a rule, not a count.

| leaf | reason |
|---|---|
| `speech-voice` | The field's own divisions (read vs spontaneous, near- vs far-field, clean vs noisy, scripted vs conversational) are **properties true of every candidate sibling**. Below "a human vocal tract" there is no second source predicate. The corpus agrees: `Speaker Verification`, `Accent Classification`, `Speech Emotion Recognition`, `Infant Cry Analysis`, `Speech Enhancement` are all *tasks over one signal*. |
| `music-audio` | The one real cut — recorded audio vs symbolic score — **crosses the level-1 branch's characteristic** (a score is not acoustic pressure). That is a level-1/level-2 question and is not mine to decide. |
| `environmental-audio` | Candidate children (bioacoustics, machine and traffic sound, ambient scenes) refine the *source* while sharing one **recording process**, a field microphone. Clause 3 keeps the node general. |
| `knowledge-graphs` | The finer cut is curation route (hand-curated ontology vs text-extracted base), but stores are routinely **mixed provenance**, so the route is a property. |
| `interaction-networks` | Candidate children (social, citation, hyperlink, messaging) name the **platform or document genre**, which determines the sector. Clause 2 fails. |
| `measured-networks` | See §3.4. The parent's own list of members is a list of fields; the D5-safe alternative (traced vs statistically inferred edges) divides by **estimation method**, i.e. the Method axis. |
| `engineered-networks` | Every candidate child (power, transport, communication, water) names the **operating sector**. The node is already declared soft at level 2 (audit A5). |
| `event-streams` | Already at its most general: the datum is a timestamp. Any subdivision names the system that logged it. |
| `feature-tables` | The generic case by construction; any child names **what the columns are about**. |
| `longitudinal-records` | See §3.4. |
| `state-vectors` | Retained at level 2 **by ruling, with near-zero support** under AXES.md's own strict reading (audit A6). Expanding a node kept by design rather than by evidence would compound the problem. |
| `vision-language`, `audio-visual`, `multisensor-perception` | Children would either **enumerate pairs**, which §6 forbids outright, or name **tasks** (captioning, VQA, retrieval), which is the Task axis. |
| `uninformative` | Administrative row; AXES.md states it has no children. |

Note the shape of this list: **eight of the fourteen stay leaves because the only
available subdivision is by field or sector.** That is D5 acting as a brake on
depth, and it is the main reason depth 3 is uneven across the axis.

---

## 5. Blind spots — corpus clusters with no node

Each was found in phase 2. None was converted into a node; each refusal is
argued, as the procedure requires.

1. **Close-range instrument-coupled photography** — `Endoscopy` 1, `Skin Lesion
   Classification` 1, `Gastroenterology` 2, and the parent's **own examples
   column** names it. *Not added*: endoscopic and dermoscopic capture can be
   still **or** video, so "instrument-coupled optical access" is a modifier true
   of both siblings — a property by the same test that killed `Video` at level 2
   — and admitting it would fuse optical access with exposure regime in one
   sibling set. **This is the largest declared gap in the output**, and closing
   it properly requires re-opening the level-2 ruling that pins `Video` at depth
   3, which is not mine to re-open.
2. **Single-cell and spatial resolution** — 8 names (`Single-cell Analysis` 3,
   `Single-Cell Genomics` 2, `Single-cell Sequencing` 2, `Single-Cell
   Transcriptomics`, `Single-Cell Data Science`, `Single-Cell Multi-Omics`,
   two RNA-seq surfaces). *Not added*: true of every omics child **and** of
   `bioseq-nucleotide`, so it is a resolution property of an assay, not a kind
   of assay. The corpus here is unusually clear evidence **for** the property
   test rather than against it.
3. **Multi-omics integration** — `Multi-Omics`, `Multi-omic Biomarker
   Discovery`, `Single-Cell Multi-Omics`, `Integrative Analysis`. *Not added*:
   a question about the relationship **between** assays is the Multimodal
   branch's positive test. Putting it under `omics-profiles` would make a
   relation a sibling of values — the level-1 irregularity the derivation
   already declares (audit A4) — and the deleted `Multimodal biomedical data`
   shows the D5-safe multimodal name is not available either. Real hole,
   recorded.
4. **Particle-physics detector readout** — ~12 names (`High Energy Physics` 5,
   `Neutrino Physics` 3, `Particle Physics` 2, `Radiation Detection`, `Deep
   Learning in Particle Physics`, `Dark Matter Studies`, `Lorentz Invariance
   Violation Analysis`, …). Calorimeter hits and track data are not an image,
   not a waveform and not a feature table. *Not added*: this needs a **level-2**
   sibling, and level 2 is fixed. Most of these surfaces are discipline names in
   any case, and the simulation surfaces (`N-body simulations`, `Monte Carlo
   Simulations`) are Method per `RATIONALE.md` §7.
5. **Haptic / tactile signals and gaze** — `Tactile Sensing`, `Haptics and
   Tactile Interaction`, `Eye Tracking` 2. Inherited level-2 blind spot,
   re-confirmed. Currently absorbed by `samp-transduced` as transducer
   telemetry, which is honest and coarse. Not fixable at depth 3.
6. **Geospatial vector data** — `Geographical Information Systems (GIS)`,
   `Species Distribution Modeling` 3+1+1, `Spatial Prioritization`. Inherited
   level-2 blind spot, re-confirmed; split across `ms-passive` and
   `engineered-networks`.

Also noted and **not** treated as blind spots: extended/virtual reality
(~7 names) names a display medium and an HCI discipline, not a signal — its data
is `range-authored` plus camera and pose streams; `Radiomics` 5 names a
feature-extraction practice over an image, not an image kind; molecular
**reactions** (`Retrosynthetic Planning` 2) are a transformation between two
`atom-finite` data, and a node for them would divide by change rather than by
boundary condition.

### Speculative nodes kept with no corpus support

`tomo-xray` · `tomo-optical` · `ms-radar` · `wave-optical` · `doc-scanned` ·
`formal-specs`, plus `atom-surface` (support is two field names D5 sends
elsewhere) and `omics-metabolite` / `omics-epigenomic` (one name each). The
keeping rule is the one the level-2 derivation states and this one inherits:
**keep a zero-support node only if an external classification or a standing
venue names it AND dropping it would make its sibling set's principle
non-exhaustive.** All eight pass both clauses. `tomo-xray` having zero support
while being the oldest radiological modality in existence is the strongest
evidence in this file that the corpus vocabulary is a naming sample, not a
census.

---

## 6. Granularity audit of this output

Test, from `GRANULARITY_AUDIT.md`: *are these the same kind of thing, at the same
level of specificity, and does any sibling exist only because it was large in
this corpus?* The second clause is satisfied by construction — the sibling sets
were written before any count existed — so the audit below is about the first.

**Passes.**

- *Tomographic (5)* — one principle (reconstructed interaction), no volume-driven
  member, four of five thin or empty and kept anyway.
- *Range & 3D (3)* — one principle (coordinate provenance), uniform specificity.
- *Waveform (3)* — one principle (transduced field), and the only set where the
  output is *more* D5-compliant than the parent's own examples.
- *Molecular structure (3)* — one principle (boundary condition), and it obeys the
  parent's prohibition rather than its examples.
- *Omics (4)* — one principle (species class), with the resolution property
  correctly excluded.
- *Natural-language text (4)* — one principle (production setting); the corpus
  independently supports three of four.
- *Microscopy (2)*, *Multispectral (2)*, *Document (2)*, *Sampled series (2)*,
  *Biomolecular sequences (2)* — one principle each, at the two-child minimum.

**Failures and low-confidence sets, declared.**

- **B1 — `photographic-imagery` (2), the weakest set in the output.** Its
  principle (exposure regime) is the closest this derivation comes to dividing
  by **mathematical structure**, which the axis bans at every level; it survives
  only because the fixed D2 disposal places `Video` here. It also leaves the
  node's largest real sub-family (instrument-coupled close-range capture) with
  no home. 114 indicative mentions divided two ways, on a principle I would not
  have chosen if `Video` were not pinned. **I am not confident in this set.**
- **B2 — `code-query` vs `formal-logic` / `formal-specs`.** Two level-2 nodes
  claim structured queries, and the examples column of the *other* parent is
  where the claim is written. The operational/declarative line the level-2 audit
  flagged as A2 does not survive contact with SQL. Declared, not resolved,
  because resolving it means changing a fixed row.
- **B3 — `source-code` (4) mixes specificity.** `code-source` is the whole
  general-purpose-language world; `code-hdl` and `code-query` are narrow
  families. Same principle throughout (what interprets the string), but not the
  same size of thing. Compare M6 on the Method axis.
- **B4 — `omics-epigenomic`.** Strains its own parent's characteristic: a
  methylation level is a per-position state, not an abundance of a species.
  Kept, flagged on the row.
- **B5 — `nl-posts` vs `nl-edited`.** Cut by the presence of an editorial gate,
  which is a real record-keeping distinction and a soft one. A moderated forum
  and a lightly edited blog fall either way.
- **B6 — `interaction-logs` (2)** inherits the parent's declared A3 low
  confidence (overlaps `longitudinal-records`, and is claimed by the Graphs
  branch's own reading). Nothing at depth 3 repairs that.
- **B7 — `atom-surface`** is admitted to complete a three-case principle and has
  essentially no support of its own. Honest, but it is a node kept by symmetry.
- **B8 — depth is uneven across the axis**, and the unevenness is *not* random:
  eight of fourteen leaves stay leaves because their only subdivision is by
  field. The axis is therefore deeper where the measurement process is rich
  (imaging, molecules, signals) and shallower where the record-keeping practice
  is the whole story (logs, records, networks). That is a structural consequence
  of D5 and should be reported as one, not smoothed.

**Volume check, explicit.** No sibling set was created, sized, merged or split
by a count. Five of the 43 nodes have zero support and are kept; the
best-supported nodes (`bioseq-nucleotide` 46, `atom-finite` 40, `samp-transduced`
38) were written before those numbers were visible and were not adjusted after.

---

## 7. Branching factors

**Level 3 per expanded parent:** Tomographic 5 · Natural-language text 4 ·
Source code 4 · Omics 4 · Range & 3D 3 · Waveform 3 · Molecular structure 3 ·
Formal notation 3 · Photographic 2 · Microscopy 2 · Multispectral 2 · Document 2
· Biomolecular sequences 2 · Sampled series 2 · Interaction logs 2.

- Expanded parents: 15 of 29. Level-2 leaves: 14.
- Level-3 nodes: 43. Mean over expanded parents **2.87**, max 5, min 2.
- Per level-1 branch: Vision 16 (across 6 of 6 level-2 nodes) · Language 11
  (3 of 3) · Molecular & materials 9 (3 of 3) · Time series 5 (2 of 3) ·
  Records 2 (1 of 4) · Audio 0 (0 of 3) · Graphs 0 (0 of 4) · Multimodal 0
  (0 of 3).
- Whole axis: 9 level-1 rows (8 substantive + 1 administrative), 29 level-2,
  43 level-3 = **81 nodes**.

No set reaches the branching factor §9 warns about; five sets sit at the
two-child minimum §9 permits, and each is argued above rather than padded.
