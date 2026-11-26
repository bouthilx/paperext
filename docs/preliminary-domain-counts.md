# Preliminary domain counts (new Milabench)

Preliminary results of the domain taxonomy for the new Milabench, as given by
Xavier Bouthillier at the hand-off (November 2026), described as counts over
**~2,000 papers from 2023 to 2026**.

Recorded here so the numbers have a home in the repo. They are **not** a result
of the 2023–2026 corpus run, which has not happened yet — read the caveats
before quoting any of them.

## Where the numbers come from

Every count below is the `corpus_mentions` column of the axis node tables, one
per axis (checked 2026-11-26: every node in the tree matches):

| axis | node table |
|---|---|
| Method | `data/ontology/design/axes/method/nodes.tsv` |
| Modality / data | `data/ontology/design/axes/modality/nodes.tsv` |
| Desired properties | `data/ontology/design/axes/properties/nodes.tsv` |
| Scientific discipline | `data/ontology/design/axes/discipline/nodes.tsv` |
| Sector | `data/ontology/design/axes/sector/nodes.tsv` |

They were produced with the faceted domain design (commit `05c306b1`,
2026-09-29); the axis definitions and rulings are in
`data/ontology/design/AXES.md`, the design process in `PROCESS.md`.

## Caveats

- **The papers are the `legacy-2024` extractions, not a 2023–2026 corpus.**
  `AXES.md` calls the source "the 1999-paper corpus"; the 1,999 papers are the
  ones in `data/mdl/queries/openai/legacy-2024`. Of the ~860 with an arXiv id,
  almost all are 2022–2024 (568 from 2023, 102 from 2024, 150 from 2022) and
  **none is from 2025 or 2026**. The "2023–2026" label should be confirmed with
  Xavier before it is quoted.
- **Counts are name mentions, not papers.** A paper naming three vision
  research fields counts three times under Vision. No node count is a number of
  papers.
- **Indicative, not measured** (`AXES.md`): `contributed` and `used` mentions
  are merged, and arXiv suggests the Vision branch is inflated relative to
  Language. `AXES.md`: "Do not treat any per-branch size here as a finding."
- **Extracted by the old prompt** (schema v3/v4, before the v5 rules), so the
  2023–2026 run will produce different names and different counts.
- **A parent's count is not the sum of its children.** Names that map to the
  parent itself, or to no child, are counted only at the parent — e.g. Language
  & text 617 against 214 + 50 + 30 = 294 in its children.

## Text modality

From `axes/modality/nodes.tsv`, including the third level the overview tree
below leaves out. *Names* = distinct names mapped to the node; *mentions* =
times they were mentioned.

| node | id | names | mentions |
|---|---|---|---|
| **Language & text** | `language` | 617 | **617** |
| ├ Natural-language text | `natural-language-text` | 103 | 214 |
| │ ├ Edited published text | `nl-edited` | 9 | 13 |
| │ ├ Conversational transcripts | `nl-dialogue` | 4 | 14 |
| │ ├ Open-platform posts | `nl-posts` | 9 | 18 |
| │ └ Practitioner free-text records | `nl-practitioner` | 5 | 5 |
| ├ Source code | `source-code` | 36 | 50 |
| │ ├ General-purpose program source | `code-source` | 18 | 26 |
| │ ├ Compiled & low-level representations | `code-lowlevel` | 2 | 3 |
| │ ├ Hardware description | `code-hdl` | 5 | 5 |
| │ └ Query & configuration languages | `code-query` | 3 | 3 |
| └ Formal & mathematical notation | `formal-notation` | 22 | 30 |
|   ├ Mathematical expressions | `formal-math` | 5 | 7 |
|   ├ Logical formulae & proof terms | `formal-logic` | 16 | 21 |
|   └ Declarative problem specifications | `formal-specs` | 0 | 0 |

Multimodal text appears elsewhere: Vision-language (10) sits under Multimodal.

## The full taxonomy, as given

Counts in parentheses are mentions; no count means none.

```
### METHOD — how does the work produce its result?
    [50 nodes]
├── Learning signal  (615)
│   ├── Supervised learning  (22)
│   ├── Unsupervised learning  (33)
│   ├── Self-supervised learning  (98)
│   ├── Semi-supervised learning  (6)
│   ├── Weakly supervised learning  (4)
│   └── Reinforcement learning  (452)
├── Training regime  (227)
│   ├── Transfer learning  (70)
│   ├── Multi-task learning  (20)
│   ├── Continual learning  (43)
│   ├── Meta-learning  (47)
│   ├── Federated learning  (24)
│   ├── Distributed training  (11)
│   └── Online learning  (12)
├── Computational machinery  (471)
│   ├── Optimization  (227)
│   ├── Probabilistic inference  (78)
│   ├── Causal inference  (40)
│   ├── Logical inference  (20)
│   ├── Game theory  (36)
│   ├── Search  (7)
│   ├── Planning  (30)
│   ├── Evolutionary computation  (10)
│   └── Inference procedures  (7)
├── Model design  (513)
│   ├── Neural architectures  (236)
│   ├── Generative models  (176)
│   ├── Symbolic models  (15)
│   ├── Kernel methods  (6)
│   ├── Ensemble methods  (18)
│   └── Model efficiency  (62)
├── Model analysis  (164)
│   ├── Interpretability  (68)
│   ├── Adversarial machine learning  (46)
│   ├── Formal verification  (21)
│   └── Uncertainty quantification  (29)
├── Learning theory  (62)
│   ├── Generalization  (24)
│   ├── Sample complexity  (3)
│   ├── Expressivity  (1)
│   ├── Training dynamics  (7)
│   └── Scaling behaviour  (5)
├── Data curation  (63)
│   ├── Data synthesis  (33)
│   ├── Data selection  (26)
│   └── Annotation  (4)
└── Uninformative  (581)
    ├── Generic field names  (543)
    └── Generic technique names  (38)

### MODALITY / DATA — what kind of signal does it operate on?
    [38 nodes]
├── Vision & imaging  (641)
│   ├── Photographic imagery  (114)
│   ├── Tomographic & radiological imaging  (167)
│   ├── Microscopy & histological imaging  (8)
│   ├── Multispectral & radar imagery  (24)
│   ├── Range & 3D scene geometry  (65)
│   └── Document & screen imagery  (5)
├── Language & text  (617)
│   ├── Natural-language text  (214)
│   ├── Source code  (50)
│   └── Formal & mathematical notation  (30)
├── Speech & audio  (50)
│   ├── Speech & voice  (26)
│   ├── Music  (6)
│   └── Environmental sound  (7)
├── Graphs & relational  (116)
│   ├── Curated knowledge graphs  (6)
│   ├── Interaction & citation networks  (16)
│   ├── Measured interaction networks  (11)
│   └── Physical & engineered networks  (22)
├── Time series & signals  (109)
│   ├── Waveform signals  (32)
│   ├── Sampled quantity series  (54)
│   └── Event & point-process streams  (6)
├── Molecular & materials data  (293)
│   ├── Molecular & crystal structure  (82)
│   ├── Biomolecular sequences  (77)
│   └── Omics abundance profiles  (30)
├── Tabular & structured records  (85)
│   ├── Feature tables  (12)
│   ├── Transactional & interaction logs  (32)
│   ├── Longitudinal administrative records  (17)
│   └── Low-dimensional state & proprioceptive vectors  (24)
├── Multimodal  (42)
│   ├── Vision-language  (10)
│   ├── Audio-visual
│   └── Multi-sensor perception  (9)
└── Uninformative  (14)

### DESIRED PROPERTIES — what property does it try to secure?
    [12 nodes]
├── Trustworthy AI  (38)
│   ├── Fairness  (67)
│   ├── Privacy  (27)
│   ├── Robustness  (73)
│   ├── Safety  (20)
│   ├── Explainability  (58)
│   └── Accountability  (13)
├── Frugal AI  (6)
│   ├── Computational cost  (12)
│   ├── Energy cost  (3)
│   └── Hardware cost  (6)
└── Uninformative

### SCIENTIFIC DISCIPLINE — whose knowledge does it advance? (OECD FOS)
    [160 nodes]
├── Natural sciences
│   ├── Mathematics
│   │   ├── Pure mathematics  (4)
│   │   ├── Applied mathematics  (10)
│   │   └── Statistics & probability  (10)
│   ├── Computer & information sciences
│   │   ├── Software engineering  (61)
│   │   ├── Human-computer interaction  (40)
│   │   ├── Computer security  (11)
│   │   ├── Computer graphics & visualisation  (18)
│   │   ├── Information retrieval  (24)
│   │   ├── Theory of computation  (8)
│   │   ├── Data management systems  (4)
│   │   └── Programming languages  (1)
│   ├── Physical sciences  (11)
│   │   ├── Astronomy & astrophysics  (34)
│   │   ├── Particles & fields physics  (12)
│   │   ├── Nuclear physics  (1)
│   │   ├── Condensed matter physics
│   │   ├── Atomic, molecular & optical physics  (1)
│   │   ├── Fluids & plasma physics
│   │   ├── Optics  (6)
│   │   └── Quantum information science  (2)
│   ├── Chemical sciences
│   │   ├── Physical chemistry  (23)
│   │   ├── Cheminformatics  (25)
│   │   ├── Organic chemistry
│   │   ├── Analytical chemistry
│   │   └── Polymer science
│   ├── Earth & related environmental sciences
│   │   ├── Climate science  (11)
│   │   ├── Meteorology & atmospheric sciences
│   │   ├── Geosciences  (1)
│   │   ├── Hydrology & water resources
│   │   ├── Oceanography
│   │   └── Environmental sciences  (8)
│   └── Biological sciences  (81)
│       ├── Biochemistry & molecular biology  (37)
│       ├── Cell biology & microbiology  (22)
│       ├── Virology  (5)
│       ├── Genetics & heredity  (64)
│       ├── Plant sciences  (4)
│       ├── Zoology & behavioural biology  (3)
│       ├── Ecology  (27)
│       ├── Biodiversity conservation  (10)
│       ├── Evolutionary biology  (8)
│       └── Systems biology  (4)
├── Engineering & technology
│   ├── Civil engineering
│   │   ├── Architecture engineering  (7)
│   │   ├── Construction & structural engineering
│   │   └── Transport engineering  (4)
│   ├── Electrical, electronic & information engineering
│   │   ├── Robotics & automation  (51)
│   │   ├── Control engineering  (16)
│   │   ├── Telecommunications  (9)
│   │   ├── Computer hardware & architecture  (9)
│   │   └── Electrical power engineering  (5)
│   ├── Mechanical engineering
│   │   ├── Applied mechanics & thermodynamics  (1)
│   │   ├── Aerospace engineering  (1)
│   │   └── Nuclear engineering
│   ├── Chemical engineering
│   │   ├── Chemical process engineering  (2)
│   │   └── Chemical product engineering
│   ├── Materials engineering
│   │   ├── Computational materials science  (14)
│   │   ├── Ceramics & composites
│   │   └── Coatings & films
│   ├── Medical engineering
│   │   ├── Neural engineering  (15)
│   │   ├── Medical devices  (5)
│   │   ├── Biomechanics  (2)
│   │   └── Medical laboratory technology  (1)
│   └── Environmental engineering
│       ├── Remote sensing  (13)
│       ├── Energy & fuels engineering  (14)
│       └── Water engineering  (1)
├── Medical & health sciences  (70)
│   ├── Basic medicine
│   │   ├── Neurosciences  (185)
│   │   ├── Immunology  (14)
│   │   ├── Human genetics  (7)
│   │   ├── Pharmacology  (14)
│   │   ├── Physiology  (5)
│   │   └── Pathology  (1)
│   ├── Clinical medicine
│   │   ├── Radiology & medical imaging  (99)
│   │   ├── Medical physics  (30)
│   │   ├── Radiation oncology  (27)
│   │   ├── Oncology  (26)
│   │   ├── Clinical neurology  (15)
│   │   ├── Psychiatry  (38)
│   │   ├── Surgery  (22)
│   │   ├── Pediatrics  (7)
│   │   ├── Geriatrics  (15)
│   │   ├── Cardiovascular medicine  (3)
│   │   ├── Gastroenterology & hepatology  (4)
│   │   ├── Respiratory medicine  (1)
│   │   └── General & internal medicine  (17)
│   ├── Health sciences
│   │   ├── Epidemiology  (27)
│   │   ├── Public health  (27)
│   │   ├── Health services research  (34)
│   │   ├── Health informatics  (22)
│   │   └── Medical ethics  (5)
│   └── Medical biotechnology
│       ├── Cell & gene therapy  (3)
│       ├── Biomaterials
│       └── Biomarker discovery  (2)
├── Agricultural & veterinary sciences
│   ├── Agriculture, forestry & fisheries
│   │   ├── Agronomy  (2)
│   │   ├── Forestry  (3)
│   │   └── Fisheries
│   ├── Animal & dairy science
│   ├── Veterinary science
│   └── Agricultural biotechnology
├── Social sciences
│   ├── Psychology & cognitive sciences
│   │   ├── Cognitive science  (36)
│   │   ├── Social psychology  (2)
│   │   ├── Clinical psychology  (2)
│   │   ├── Developmental psychology  (1)
│   │   └── Human factors & ergonomics  (5)
│   ├── Economics & business
│   │   ├── Economics  (3)
│   │   ├── Econometrics  (1)
│   │   └── Business & management  (2)
│   ├── Educational sciences
│   │   ├── Pedagogy  (4)
│   │   ├── Educational technology  (2)
│   │   └── Professional education  (14)
│   ├── Sociology
│   │   ├── Demography  (1)
│   │   ├── Social policy & social work  (2)
│   │   └── Social inequality studies  (4)
│   ├── Law
│   │   ├── Regulation & governance  (1)
│   │   └── Criminology
│   ├── Political science
│   ├── Social & economic geography
│   │   ├── Urban studies  (1)
│   │   ├── Cultural & economic geography  (1)
│   │   └── Transport planning  (5)
│   └── Media & communications
│       ├── Media & communication studies  (9)
│       ├── Journalism
│       └── Library & information science  (2)
├── Humanities
│   ├── History & archaeology
│   ├── Languages & literature
│   │   ├── Linguistics  (14)
│   │   └── Literary studies
│   ├── Philosophy, ethics & religion
│   │   ├── Philosophy & history of science  (2)
│   │   ├── Ethics
│   │   └── Religious studies
│   └── Arts
└── Uninformative

### SECTOR — whose operational problem does it solve? (ISIC Rev.4)
    [40 nodes]
├── Agriculture, forestry & fishing  (5)
│   ├── Crop & livestock production  (2)
│   ├── Forestry  (3)
│   └── Fishing & aquaculture
├── Manufacturing  (6)
│   ├── Process industries  (5)
│   └── Discrete manufacturing  (1)
├── Energy & utilities  (17)
│   ├── Electricity generation & grid operations  (16)
│   └── Water & waste services  (1)
├── Built environment  (12)
│   ├── Building operations  (9)
│   ├── Design & construction  (1)
│   └── Urban planning & development  (2)
├── Transportation & logistics  (20)
│   ├── Public transit  (5)
│   ├── Road traffic & automated vehicles  (10)
│   ├── Air transport  (2)
│   └── Freight & logistics  (2)
├── Information & communication  (116)
│   ├── Telecommunications  (14)
│   ├── Software & IT services  (89)
│   └── Media & entertainment  (13)
├── Finance & insurance  (4)
├── Environment & natural resources  (13)
│   ├── Environmental quality & emissions  (2)
│   ├── Biodiversity & conservation  (4)
│   └── Hazards & disaster response  (3)
├── Public administration  (7)
├── Education  (25)
│   ├── General & higher education  (8)
│   └── Professional & continuing education  (17)
├── Healthcare & social care  (154)
│   ├── Clinical services  (27)
│   ├── Patient & caregiver support  (17)
│   ├── Health system administration  (31)
│   ├── Public & population health  (30)
│   └── Social care & community services  (4)
├── Retail & consumer services  (5)
└── Uninformative  (5)
```
