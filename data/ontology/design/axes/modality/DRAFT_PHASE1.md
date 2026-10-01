# Modality / data — depth-3 expansion, PHASE 1 DRAFT (semantic, no corpus access)

**This file is the record of the phase-1 draft and is not edited after phase 2.**

Written from `AXES.md` §6 (the D5 rule, the property test, the ban on dividing
by mathematical structure at every level), the `modality2` level-2
characteristics in `nodes.tsv`, and `RATIONALE.md`. **`domain_names.tsv` was not
opened, no tally was run, and the `examples` column of the level-2 rows was not
read.** Every child below is derived from the field's own structure at finer
precision: what the research and instrument communities themselves distinguish.

Ordering of the sections follows the volume priority supplied by the owner —
that is the *only* use of volume — and nothing inside a section is decided by it.

---

## The three tests applied to every candidate child

1. **D5 clause 1 (naming).** The child is named by the measurement or record
   process — instrument, sampling geometry, encoding, assay, record-keeping
   practice. Never by the field, subject, sector or purpose.
2. **D5 clause 2 (admission).** Two papers can carry the child and differ on
   Scientific discipline or Sector. (May fail empirically while clause 1 holds.)
3. **D5 clause 3 (generality).** Name at the most general level of the process
   that still picks out one signal kind.
4. **Property test.** A modifier that can be true of the candidate's siblings is
   a property, not a sibling.
5. **No division by mathematical structure**, at this level as at every other.

---

## 1. `natural-language-text` — Natural-language text

**Characteristic chosen:** *the setting in which the string was produced and put
on record — who produced it, for whom, and whether it was revised before it was
recorded.*

The parent's own negative test already fixes the depth: "prose, dialogue, chat
and clinical notes are all this node, at depth 3." So register/production
setting is the intended cut; the work of phase 1 is to state it as one principle
and to name its members by the production process rather than by the field.

| id | name | positive test | negative test |
|---|---|---|---|
| `nl-edited` | Edited published text | A single author composes and revises the string before it is recorded, addressing an absent reader: books, articles, newswire, encyclopedic and scientific writing, reports | Reject text that reaches the record unrevised |
| `nl-dialogue` | Conversational transcripts | Two or more participants produce turns addressed to each other and the record is the exchange: chat logs, call and meeting transcripts, interviews, human–agent dialogue | Reject a monologue transcribed from speech with no addressee turn structure |
| `nl-posts` | Open-platform posts | The string is self-published to an open platform with no editorial gate: posts, comments, reviews, forum threads | Reject editorially gated publication and reject turn-addressed exchange |
| `nl-practitioner` | Practitioner free-text records | The string is narrative text entered into an operational record in the course of doing the work: notes, reports, case files, incident and defect descriptions | Reject the coded fields of the same record, which are Tabular > Longitudinal administrative records |

**Competing principle rejected: by subject-matter domain** (biomedical text,
legal text, financial text, scientific text). This is the single most tempting
cut in the whole axis and it is a straight D5 clause-1 violation: it names the
field. `nl-practitioner` is the D5-legal way to keep what that cut was reaching
for, because "text entered into an operational record" is a record-keeping
practice and two papers carrying it differ on discipline (clinical notes, court
filings, maintenance logs, bug reports).

**Second competing principle rejected: by production channel — natively written
versus transcribed from speech.** This is the most instrument-shaped cut
available (the string is either typed or derived from an acoustic record) and it
was seriously considered. Rejected because it splits the dialogue community in
half (typed chat and transcribed calls are one research object) and because a
transcript's provenance is a property that can be true of `nl-edited` (published
oral histories) and `nl-posts` (voice posts) alike — the property test.

**Declared weakness:** `nl-posts` versus `nl-edited` is cut by the presence of an
editorial gate. That is a real record-keeping distinction but a soft one; it is
the least confident member of this set.

---

## 2. `tomographic-imaging` — Tomographic & radiological imaging

**Characteristic chosen:** *which physical interaction is measured and
reconstructed into the array.*

This is the field's own structure with no translation needed: in radiology an
"imaging modality" **is** the interaction — transmission, resonance, echo,
emission. It continues the parent's principle (how the image was formed) one
level down without changing principle.

| id | name | positive test | negative test |
|---|---|---|---|
| `tomo-xray` | X-ray attenuation imaging | The array's contrast is attenuation of transmitted X-rays: projection radiography, computed tomography, industrial and materials CT | Reject dose, treatment-planning and therapy names, which are a procedure, not an image |
| `tomo-mr` | Magnetic resonance imaging | Contrast comes from nuclear spin relaxation in an applied magnetic field | Reject magnetic-resonance spectroscopy read as a spectrum with no spatial sampling |
| `tomo-ultrasound` | Ultrasound & echo imaging | The array is reconstructed from reflected acoustic pulses insonifying the specimen | Reject sonar used as ranging (Range & 3D scene geometry) and audible acoustics (Speech & audio) |
| `tomo-emission` | Emission & tracer imaging | The array is reconstructed from radiation emitted by a tracer introduced into the specimen: PET, SPECT, scintigraphy | Reject the tracer chemistry itself, which is Molecular & materials data |
| `tomo-optical` | Optical & photoacoustic tomography | Depth is resolved from backscattered light or from light-induced acoustic waves: OCT, diffuse optical tomography, photoacoustic imaging | Reject surface photography of an illuminated specimen, which resolves no depth |

**Competing principle rejected: by anatomy or by clinical service** (brain
imaging, cardiac imaging, chest radiography, oncological imaging). This is the
cut the corpus's vocabulary will most want, and it is exactly the D5 defect the
parent node was created to repair one level up. Naming children by anatomy would
re-import `Biomedical imagery` at depth 3 after removing it at depth 2, and every
such child would determine the Scientific discipline value (clause 2 fails
outright).

**Competing principle rejected: structural versus functional imaging.** Property
test: "functional" is true of MR (fMRI), of emission imaging (FDG-PET), and of
CT (perfusion). A modifier true of every sibling is a property of the branch.

**Competing principle rejected: 2-D cross-section versus 3-D volume.** Division
by mathematical structure, banned at every level; also a property (the same
scanner yields both).

---

## 3. `photographic-imagery` — Photographic imagery

**Characteristic chosen:** *the exposure regime — what one datum covers.*

| id | name | positive test | negative test |
|---|---|---|---|
| `photo-still` | Still photographs | One exposure of a scene is the datum; there is no temporal ordering to destroy | Reject a frame drawn from a stream where the stream is the object of study |
| `photo-video` | Video & frame streams | The same sensor is read continuously at a frame rate and the ordered stream is the datum | Reject an unordered image collection, and reject frame-rate capture by a non-photographic sensor |

**This is the weakest expansion in the draft and it is constrained rather than
chosen.** `RATIONALE.md` §1 (D2 disposal) and the parent's own note fix `Video`
at depth 3 under this node. The principle that would otherwise be right here —
*the platform and optical path through which the camera reaches the scene*
(free-standing scene camera · instrument-coupled close-range optics such as
endoscopy, dermoscopy and fundus photography · platform-mounted standoff and
airborne RGB) — makes video a **property**, since any of those three can be run
at a frame rate. Adopting it would delete the node the inherited derivation
explicitly places here. Adopting both would fuse two principles in one sibling
set, which §9 forbids.

**Consequence, declared:** endoscopic, dermoscopic, aerial-RGB and egocentric
capture take no depth-3 node and sit at the level-2 node itself (branch-level
residence, §8b). Two substantive children is the minimum §9 allows and this set
is at that minimum.

---

## 4. `microscopy-imaging` — Microscopy & histological imaging

Not on the owner's volume list; expanded because the parent's **own positive
test names two distinct image-forming processes** ("magnifying optics **or** an
electron beam"), so the field's structure is already written into the node.

**Characteristic chosen:** *what probe the magnifying instrument uses to form the
array.*

| id | name | positive test | negative test |
|---|---|---|---|
| `micro-light` | Light microscopy | The array is formed by photons through magnifying optics: brightfield, fluorescence, confocal, whole-slide histology scans | Reject unmagnified photography of a specimen |
| `micro-electron` | Electron microscopy | The array is formed by an electron beam over a prepared specimen: TEM, SEM, cryo-EM micrographs | Reject the 3-D structure solved from those micrographs, which is Molecular & crystal structure |

**Competing principle rejected: by what is on the slide** (histopathology,
cytology, cell biology, materials sections). D5 clause 1: names the field, not
the instrument. The clause-2 exception is relevant here in the stated form —
cryo-EM has essentially one user — and the node still stands, because the leak
would be a naming fault and there is none.

---

## 5. `multispectral-imagery` — Multispectral & radar imagery

Not on the volume list; expanded because the parent's name is itself a doublet of
**two different formation processes**, passive band sampling and active
microwave ranging, which is precisely what depth 3 exists to separate.

**Characteristic chosen:** *whether the instrument samples radiation it receives
or radiation it emits.*

| id | name | positive test | negative test |
|---|---|---|---|
| `ms-passive` | Passive multispectral & hyperspectral imagery | The instrument records reflected or emitted radiation in more than three bands, georeferenced or sky-referenced: multispectral, hyperspectral, thermal and survey-telescope imagery | Reject three-band RGB capture (Photographic imagery) |
| `ms-radar` | Synthetic-aperture & active radar imagery | The instrument illuminates the scene with microwaves and images the returns, including interferometric and polarimetric products | Reject radar used only as a range measurement without image formation (Range & 3D scene geometry) |

**Competing principle rejected: by platform** (satellite, airborne, drone,
ground station). Platform is a property — a hyperspectral sensor and a SAR flies
on all of them — and it tends to name the sector that operates the platform.

---

## 6. `range-geometry` — Range & 3D scene geometry

**Characteristic chosen:** *where the coordinates came from — measured by active
ranging, inferred from multiple views, or authored.*

| id | name | positive test | negative test |
|---|---|---|---|
| `range-active` | Active range measurement | Coordinates are obtained by timing or triangulating an emitted beam: LiDAR, time-of-flight, structured light, depth sensors | Reject imaging radar and tomographic reconstruction |
| `range-multiview` | Image-based reconstruction | Coordinates are inferred from several passive views of the same scene: structure-from-motion, multi-view stereo, photogrammetry, neural scene reconstruction | Reject single-view depth estimation whose datum is the photograph |
| `range-authored` | Authored & synthetic scene geometry | Coordinates are written by a designer or a generator rather than measured: CAD models, asset meshes, simulated environments, rendered scenes | Reject the rendered raster output, which is Document & screen imagery or Photographic imagery depending on what it depicts |

**Competing principle rejected: by geometric representation** (point cloud, mesh,
voxel grid, implicit field, signed distance function). This is the obvious cut
and it is banned twice over: it divides by mathematical structure, and the same
scan is interconvertible between all four, so the representation is a property.
The parent node survives the property test only because it is defined by
acquisition, and that must continue downward.

---

## 7. `document-imagery` — Document & screen imagery

Not on the volume list; expanded because the node name again fuses two capture
processes (a page and a screen), and because the parent is declared `LOW
CONFIDENCE` precisely for naming the origin of depicted content rather than
sensing physics. Splitting by **how the raster was obtained** moves the set back
onto the branch's formation principle.

**Characteristic chosen:** *how the raster of symbolic material was obtained.*

| id | name | positive test | negative test |
|---|---|---|---|
| `doc-scanned` | Scanned & photographed pages | A sensor images a physical carrier of symbolic material: scanned pages, forms, receipts, manuscripts, whiteboards, photographed documents | Reject the extracted text itself (Language & text) |
| `doc-screen` | Rendered screen captures | The raster is read from a framebuffer that a renderer wrote: screenshots, GUI states, rendered charts and web pages | Reject the underlying markup or code, which is Source code |

**Competing principle rejected: by document genre** (invoices, forms, scientific
papers, tables, charts). Names the purpose of the document and, through it, the
sector that files it.

---

## 8. `atomistic-structure` — Molecular & crystal structure

**Characteristic chosen:** *the spatial boundary condition under which the
arrangement of atoms is specified.*

| id | name | positive test | negative test |
|---|---|---|---|
| `atom-finite` | Finite molecular structures | A bounded atom set with a molecular boundary and no lattice — of any size, from a ligand to a macromolecular fold or complex | Reject a structure specified in a unit cell with lattice vectors |
| `atom-periodic` | Periodic crystalline structures | Atoms are given in a unit cell with lattice vectors and periodic boundary conditions: crystals, alloys, framework materials, layered materials | Reject a finite cluster cut out of a solid |
| `atom-surface` | Surface & interface structures | An extended substrate terminated by a boundary, with adsorbates or a second phase at the interface: slabs, adsorption sites, grain boundaries, solvated interfaces | Reject bulk periodic structure with no terminating boundary |

**The parent forbids the obvious cut and the draft obeys it.** Splitting small
molecules from protein folds would reproduce the chemistry / structural-biology
field boundary inside the branch; `atom-finite` deliberately holds both, exactly
as the parent's note requires.

**Competing principle rejected: by provenance — experimentally solved versus
computed.** Attractive under D5 clause 1 (diffraction and cryo-EM are assays),
but `RATIONALE.md` §7 already rules that a data-*generating* process is not a
kind of signal ("Simulation" → Method), so half the partition would be a Method
value in disguise.

**Property, not a sibling: dynamics.** A trajectory qualifies finite molecules,
periodic solids and interfaces alike, so molecular-dynamics data is a property of
any of the three, never a fourth member.

---

## 9. `biomolecular-sequences` — Biomolecular sequences

**Characteristic chosen:** *which biochemical alphabet the assay read.*

| id | name | positive test | negative test |
|---|---|---|---|
| `bioseq-nucleotide` | Nucleotide sequences | The string is over a nucleotide alphabet, read by a sequencing assay from DNA or RNA: genomes, reads, variants, regulatory and coding regions | Never admit a bare `sequence` surface; 65% of corpus names containing `sequen` are Method or Task names |
| `bioseq-protein` | Amino-acid sequences | The string gives a protein's covalent residue order over the amino-acid alphabet | Reject the folded 3-D structure of the same protein, which is Molecular & crystal structure |

**Competing principle rejected: the central dogma as a three-way** (DNA · RNA ·
protein). Rejected under D5 clause 3: DNA and RNA are read by the *same*
sequencing process, so the most general level that still picks out one signal
kind merges them. Transcript *abundance* is a different assay and is already the
sibling node `Omics abundance profiles`.

**Competing principle rejected: by sequencing protocol** (short-read, long-read,
single-cell, metagenomic). Clause 3 again: it fragments one assay along vendor
and pipeline lines, and protocol is a property of a run, not a kind of string.

**Two children is the minimum**, and it is what the alphabet principle honestly
yields; a third was not invented to pad the set.

---

## 10. `source-code` — Source code

**Characteristic chosen:** *what interprets the string, and therefore which
grammar licenses it.*

| id | name | positive test | negative test |
|---|---|---|---|
| `code-source` | General-purpose program source | Source text in a general-purpose programming language, compiled or interpreted into a running process | Reject the `programming` homonym family — integer, stochastic, constraint, dynamic and probabilistic programming are Method, measured 83% wrong |
| `code-lowlevel` | Compiled & low-level representations | The string is the compiler's or assembler's output read by a machine or a decompiler: assembly, bytecode, compiler IR, binaries | Reject execution traces and profiles, which are Time series > Event & point-process streams |
| `code-hdl` | Hardware description | The string is in a hardware-description language and is synthesized into a circuit rather than into a process | Reject the fabricated device and its measurements |
| `code-query` | Query & configuration languages | The string is read by an engine that executes it directly against data or infrastructure: SQL and other query languages, build, deployment and configuration specifications | Reject a formal specification that is proved rather than executed (Formal & mathematical notation) |

**Competing principle rejected: by software-engineering activity** (bug fixing,
code review, testing, documentation). Names the purpose, not the artefact, and
every child would determine the discipline value.

**Property, not a sibling: version-control form.** A diff, a commit or a patch is
a *record* of a change and can be true of every sibling (there are HDL commits
and SQL commits), so change-set form is a property, not a fifth child.

**Declared weakness:** `code-query` sits on the operational/declarative line that
`RATIONALE.md` A2 already flags as the low-confidence cut of the parent's own
sibling set. It is the least confident member here.

---

## 11. `waveform-signals` — Waveform signals

**Characteristic chosen:** *which physical field the transducer couples to.*

The parent exists to stop `EEG`, `ECG`, `seismometer` and `radio receiver`
becoming four siblings (clause 3). The next general level down that still picks
out one signal kind is the transduced field itself, not the instrument.

| id | name | positive test | negative test |
|---|---|---|---|
| `wave-em` | Electrical & electromagnetic traces | A transducer records a voltage, current or induced field at waveform rates: EEG, ECG, EMG, local field potentials, spike traces, antenna and RF captures, power-quality traces | Reject a quantity read at intervals chosen by the recorder (Sampled quantity series) |
| `wave-mech` | Mechanical & vibrational traces | A transducer couples to displacement, acceleration or non-audible pressure: seismic traces, structural vibration, accelerometry, ultrasonic and sonar returns analysed as traces | Reject audible acoustic pressure produced to be heard (Speech & audio) |
| `wave-optical` | Optical intensity traces | A detector records light intensity against time at waveform rates: photoplethysmography, fluorescence and calcium traces, photometric light curves | Reject spatially sampled optical arrays (Vision & imaging) |

**Competing principle rejected: by the organ or the field the trace comes from**
(neural signals, cardiac signals, geophysical signals, communications signals).
This is D5's own worked example one level down; the parent was created by
dissolving exactly this cut, and re-creating it at depth 3 would undo the repair.

**No node is named for spectra**, at this level either: the `spectral` surface is
measured 89% wrong on this axis. Frequency-domain analysis is a method applied to
all three children.

---

## 12. `sampled-series` — Sampled quantity series

**Characteristic chosen:** *how a reading gets into the series — transduced from
a physical quantity, or tallied from events.*

The parent's negative test forbids the only division the corpus vocabulary will
offer ("financial, environmental, energy and epidemiological series are one
signal kind"). What remains that is a genuine record process is the difference
between a transducer's reading and a counted aggregate.

| id | name | positive test | negative test |
|---|---|---|---|
| `samp-transduced` | Transduced sensor readings | A transducer converts a physical quantity and the recorder samples it at a chosen interval: temperature, flow, load, occupancy, wearable and telemetry readings | Reject waveform-rate traces where the shape carries the information |
| `samp-tallied` | Tallied & aggregated counts | Each reading is a count or an aggregate computed over a reporting period from discrete events: case counts, volumes, consumption totals, incidence rates | Reject the individual timestamped events themselves (Event & point-process streams) |

**Competing principle rejected: by spatial support** (single-site series versus
sensor-network and spatio-temporal fields). A real community, but the property
test disposes of it: a sensor network can be transduced or tallied, so spatial
indexing is a property that qualifies both children rather than a member beside
them.

**Competing principle rejected: a `quoted ledger series` child** for prices,
rates and indices. It reads as a record-keeping practice and would therefore
survive clause 1, but clause 2 fails — essentially every paper carrying it is
economics or finance — and the parent deleted `Financial time series` for exactly
that reason. Re-admitting it under a process-shaped name is the same leak with
better manners.

---

## 13. `omics-profiles` — Omics abundance profiles

**Characteristic chosen:** *which class of molecular species the assay
quantifies.*

| id | name | positive test | negative test |
|---|---|---|---|
| `omics-transcript` | Transcript abundance profiles | The assay quantifies RNA species per sample: RNA-seq, single-cell RNA-seq, expression arrays | Reject the nucleotide string itself (Biomolecular sequences) |
| `omics-protein` | Protein & peptide abundance profiles | The assay quantifies proteins or peptides by mass spectrometry or affinity capture | Reject protein structure and protein sequence |
| `omics-metabolite` | Metabolite abundance profiles | The assay quantifies small-molecule metabolites or lipids by mass spectrometry or NMR | Reject the identification of an unknown compound's structure, which is Molecular & crystal structure |
| `omics-epigenomic` | Epigenomic & chromatin profiles | The assay quantifies base modification or chromatin state per genomic position: methylation arrays, ATAC-seq, ChIP-seq | Reject variant calling from the same reads, which reports sequence, not abundance |

**Property, not a sibling: resolution and spatial context.** `Single-cell` and
`spatial` are the two labels the field puts in front of every omics word, and
both can be true of every child above (single-cell transcriptomics, single-cell
proteomics, spatial transcriptomics, spatial metabolomics). They are properties
of an assay's resolution, not kinds of assay — the same test that killed `Video`
and `Multilingual text` at level 2. This is the clearest property-test case in
the whole depth-3 draft.

**Competing principle rejected: by tissue, organism or clinical question.** D5
clause 1.

**Declared weakness:** `omics-epigenomic` strains the parent's "how much of each
molecular species" wording — a methylation level is a per-position state, not an
abundance of a species. It is the least well-matched member of this set.

---

## 14. `interaction-logs` — Transactional & interaction logs

**Characteristic chosen:** *whether the row records the act itself or a judgement
the system asked for.*

| id | name | positive test | negative test |
|---|---|---|---|
| `log-implicit` | Implicit behaviour logs | The row records that an act occurred: a click, a view, a play, a dwell, a purchase, a query issued | Reject a judgement the agent was asked to supply |
| `log-elicited` | Elicited preference & rating records | The row records a judgement solicited from the agent: a rating, a thumbs signal, a pairwise preference, an annotation | Reject behaviour treated as a proxy for preference; the solicitation must have happened |

**Competing principle rejected: by the sector operating the system** (retail,
streaming, education, healthcare portals). D5 clause 1, and the parent is already
the D5-compliant rename of `User interaction records`.

**Declared weakness:** the parent is itself `LOW CONFIDENCE` at level 2 (it
overlaps `Longitudinal administrative records` and is claimed by the Graphs
branch's own reading). Everything below it inherits that.

---

## 15. `formal-notation` — Formal & mathematical notation

**Characteristic chosen:** *which formal calculus the string belongs to,
identified by the semantics that fixes its meaning.*

| id | name | positive test | negative test |
|---|---|---|---|
| `formal-math` | Mathematical expressions | The string is algebraic or analytic notation denoting quantities and relations, to be evaluated, simplified or rewritten | Reject a paper that merely uses mathematics; the notation must be what the system reads or writes |
| `formal-logic` | Logical formulae & proof terms | The string is in a deductive calculus and is checked, proved or refuted: proof-assistant developments, first-order and modal formulae, SAT/SMT instances | Reject informal mathematical prose, which is Natural-language text |
| `formal-specs` | Declarative problem specifications | The string states a problem for a solver in a specification language: constraint models, planning domains, declarative optimization models | Reject the solver algorithm itself, which is Method |

**Competing principle rejected: by mathematical subject** (algebra, geometry,
number theory, combinatorics). Names the field of mathematics, not the notation
process.

**Declared weakness, inherited:** the parent is `LOW CONFIDENCE` because source
code is also a formal language and the operational/declarative cut is not one the
field routinely makes. `formal-logic` and `code-query` sit on opposite sides of a
line that a Lean development or an SQL query can cross.

---

## Level-2 nodes deliberately left as leaves

| node | why it stays a leaf |
|---|---|
| `speech-voice` | The divisions the field makes — read versus spontaneous, near- versus far-field, clean versus noisy, scripted versus conversational — are all **properties that can be true of every candidate sibling**. There is no second source predicate below "a human vocal tract". |
| `music-audio` | The one real cut is audio recording versus symbolic score, and that cut **crosses the level-1 branch's own characteristic** (a score is not acoustic pressure). Resolving it is a level-1/level-2 question, not a depth-3 one, and it is not mine to decide. |
| `environmental-audio` | Candidate children (animal vocalisation, machine and traffic sound, ambient scenes) are refinements of the *source* whose **recording process is identical** — a field microphone. D5 clause 3 keeps the node at the general level. |
| `knowledge-graphs` | The finer cut would be by curation route (hand-curated ontology versus text-extracted knowledge base), but a graph's edges are routinely **mixed provenance**, so the route is a property of a store, not a kind of store. |
| `interaction-networks` | Candidate children (social, citation, hyperlink, messaging) are named by the **platform or the document genre**, which determines the sector. D5 clause 2 fails. |
| `measured-networks` | The parent's own note lists gene networks, connectomes and food webs as living inside it; each of those **determines the discipline** and cannot be a node. The D5-safe alternative — physically traced versus statistically inferred edges — divides by **estimation method**, which is the Method axis, not a signal kind. |
| `engineered-networks` | Every candidate child (power, transport, communication, water) names the **sector that operates the network**. The node is also already declared soft at level 2 (audit A5). |
| `event-streams` | Structurally already at its most general: the datum is a timestamp. Any subdivision names the system that logged it, i.e. the sector. |
| `feature-tables` | The generic case by construction. Any child names **what the columns are about**, which is the discipline. |
| `longitudinal-records` | The parent's own note lists EHR, claims, registry, student and court records as living inside it — that is a list of **institutions**, and the node exists precisely to stop them becoming siblings. |
| `state-vectors` | Retained by AXES.md ruling with near-zero support under that same section's strict reading (audit A6). Expanding a node that is kept by design and not by evidence would compound the problem. |
| `vision-language`, `audio-visual`, `multisensor-perception` | Children of a multimodal node would either **enumerate pairs**, which §6 explicitly forbids, or name **tasks** (captioning, VQA, retrieval), which belong to the Task axis. |
| `uninformative` | Administrative row; AXES.md states it has no children. |

---

## Phase-1 branching factors

Level 3 per expanded level-2 node: Natural-language text 4 · Tomographic 5 ·
Photographic 2 · Microscopy 2 · Multispectral 2 · Range & 3D 3 · Document &
screen 2 · Molecular & crystal structure 3 · Biomolecular sequences 2 · Source
code 4 · Waveform signals 3 · Sampled quantity series 2 · Omics 4 · Interaction
logs 2 · Formal notation 3.

15 expanded parents, 43 level-3 nodes, mean 2.9, max 5, min 2. Fourteen level-2
nodes stay leaves.

**Nothing in this draft was decided by a count, because no count was available
when it was written.**
