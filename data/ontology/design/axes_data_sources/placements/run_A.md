# Placement run A — 194 candidates on `access` and `provenance`

#102 step 4. One of three independent placement runs. Files read, in order:
`METHOD.md`, `SYNTHESIS.md`, `access/nodes.tsv`, `provenance/nodes.tsv`,
`placement_candidates.tsv`, and issue #102 (Parts A and E). **No other run's
output was read or looked for.**

**Headline: 169 of 194 names admitted, 25 rejected. 0 names reach
`provenance-other`. 0 names reach `stream`. 65 of 169 admitted names (38%) sit
on the `simulated`/`constructed` boundary — that boundary, not the folded
byproduct value, is where this sample hurts.**

---

## 0. How `access` is written below

`access` is a property of the **mention** (#102 Part E, SYNTHESIS §4). A *name*
therefore gets the set of values it can legitimately take, with the typical one
marked `*`. A frozen log of an interactive source reports `fixed`, never
`interactive`, so `interactive*` plus `fixed (frozen log)` is not a
multi-valued access claim — it is two mentions.

`provenance` is a property of the **entity** and is multi-valued; the full set
is written every time (METHOD §3: no deltas, no tree to inherit from).

Flags in the last column are machine-counted for §4:
`S/C` simulated–constructed boundary · `RULE` carries `rule` ·
`G/I` generator-vs-interactive access tie · `F/O` fixed-vs-oracle access tie ·
`STRAIN` strained `human-incidental` · `DERIV` `derived_from` load-bearing ·
`PAPER` undecidable from the name alone · `CONTRA` a node's positive and
negative tests disagree.

---

## 1. Placements

### 1.1 The Atari / ALE family — 20 admitted strings, one entity family

| name | access | provenance | note | flags |
|---|---|---|---|---|
| Arcade Learning Environment | `interactive*` | `constructed` | the emulator stepping a game ROM | S/C CONTRA |
| Arcade Learning Environment (ALE) | `interactive*` | `constructed` | alias of the above, written not inferred | S/C CONTRA |
| Sequential Arcade Learning Environment | `interactive*` | `constructed` | a named ALE variant (task-sequence wrapper) | S/C CONTRA |
| Atari 2600 | `interactive*` \| `fixed` | `constructed` | | S/C CONTRA PAPER |
| Atari | `interactive*` \| `fixed` | `constructed` | bare string; live-vs-dump genuinely unresolved | S/C CONTRA PAPER |
| Atari Games | `interactive*` \| `fixed` | `constructed` | | S/C CONTRA PAPER |
| Atari 2600 Games | `interactive*` \| `fixed` | `constructed` | | S/C CONTRA PAPER |
| Atari 57 | `interactive*` | `constructed` | the 57-game member set = a suite, provenance uniform across members | S/C CONTRA |
| Atari suite | `interactive*` | `constructed` | | S/C CONTRA |
| Atari 2600 suite | `interactive*` | `constructed` | | S/C CONTRA |
| Atari Benchmark | `interactive*` | `constructed` | | S/C CONTRA |
| Atari 2600 benchmark | `interactive*` | `constructed` | | S/C CONTRA |
| Atari 100k | `interactive*` | `constructed` | **a budget, not a source**: 100k steps is a protocol over ALE | S/C CONTRA |
| Atari 100k benchmark | `interactive*` | `constructed` | same | S/C CONTRA |
| 100k benchmark | `interactive*` | `constructed` | elliptical alias of Atari 100k; the quote is needed even to know the source | S/C CONTRA PAPER |
| Atari Boxing | `interactive*` | `constructed` | single game = member of ALE | S/C CONTRA |
| MsPacman Atari 2600 | `interactive*` | `constructed` | single game | S/C CONTRA |
| Atari DQN replay dataset | `fixed` | `constructed` + `model-generated` | derived_from ALE; the DQN that generated it set the state distribution | S/C CONTRA DERIV |
| Atari Dataset from RL Unplugged | `fixed` | `constructed` + `model-generated` | 100M steps of DQN training; derived_from ALE | S/C CONTRA DERIV |
| RL Unplugged Atari Dataset | `fixed` | `constructed` + `model-generated` | alias of the above | S/C CONTRA DERIV |

**21 of 194 strings (11%) in this candidate set are Atari.** One rejected
(`Atari games dataset`). The suite-granularity worry recorded at SYNTHESIS §3
(1/3, A) **does not bite here**: provenance is uniform across all 57 members, so
the suite-level union is informative, not meaningless. It bites on GLUE and
OpenML instead (§1.6) — which refines that tension rather than confirming it.

### 1.2 Physics-simulator environments and their offline logs

| name | access | provenance | note | flags |
|---|---|---|---|---|
| DeepMind Control Suite | `interactive*` \| `fixed` | `simulated` | | |
| DeepMind Control Suite (DMC) | `interactive*` \| `fixed` | `simulated` | alias | |
| DMC - DeepMind Control Suite | `interactive*` \| `fixed` | `simulated` | alias | |
| DeepMind Control | `interactive*` \| `fixed` | `simulated` | alias | |
| dm_control suite | `interactive*` \| `fixed` | `simulated` | alias; also the name of the *library* — one string, two entities | |
| hopper_stand | `interactive*` | `simulated` | a DMC task, not Gym's `Hopper` | PAPER |
| Gym MuJoCo Benchmark | `interactive*` \| `fixed` | `simulated` | the only properly *named* string for the Gym locomotion set | |
| HalfCheetah-v2 | `interactive*` \| `fixed` | `simulated` | | |
| HalfCheetah-v3 | `interactive*` \| `fixed` | `simulated` | v2≠v3 in dynamics; no slot records a version | |
| Hopper | `interactive*` \| `fixed` | `simulated` | | PAPER |
| Hopper-v2 | `interactive*` \| `fixed` | `simulated` | | |
| Walker2d-v2 | `interactive*` \| `fixed` | `simulated` | | |
| Humanoid | `interactive*` \| `fixed` | `simulated` | | |
| Humanoid-v2 | `interactive*` \| `fixed` | `simulated` | | |
| MuJoCo Reacher | `interactive*` | `simulated` | | |
| AntMaze | `interactive*` \| `fixed` | `simulated` | | |
| Meta-World | `interactive*` | `simulated` | | |
| MetaWorld environments | `interactive*` | `simulated` | alias | |
| Meta-World ML45 | `interactive*` | `simulated` | a *split* of Meta-World — Part C: not a derivation, same node | |
| MetaWorld MT10 | `interactive*` | `simulated` | split, same node | |
| Multi-Agent Particle environment (Mordatch & Abbeel, 2017) | `interactive*` | `simulated` | | |
| Multi-Agent Particle Environment (MPE) | `interactive*` | `simulated` | alias | |
| Multi-agent Particle Environments (MPE) | `interactive*` | `simulated` | alias | |
| Multi-Agent Particle Environments | `interactive*` | `simulated` | alias | |
| CALVIN | `interactive*` \| `fixed` | `simulated` + `elicited` | **ships an env and 24h of teleoperated play under one name** — the MineRL shape, with a name SYNTHESIS §3 did not have | PAPER |
| EARL benchmark | `interactive*` | `simulated` | a reset-free *protocol* over manipulation envs | |
| Real-World Reinforcement Learning Benchmark (RWRL) | `interactive*` | `simulated` | perturbation protocol over DMC | |
| Real-World RL benchmark | `interactive*` | `simulated` | alias | |
| Unsupervised Reinforcement Learning Benchmark (URLB) | `interactive*` | `simulated` | protocol over DMC | |
| Unsupervised RL Benchmark (URLB) | `interactive*` | `simulated` | alias | |
| URL Benchmark | `interactive*` | `simulated` | alias | |
| D4RL | `fixed*` | `simulated` + `model-generated` + `elicited` | derived_from MuJoCo/AntMaze/Adroit; behaviour policies are trained agents, adroit-human is teleop | DERIV PAPER |
| D4RL Benchmark | `fixed*` | `simulated` + `model-generated` + `elicited` | alias | DERIV |
| Multi-Agent MuJoCo (MAMuJoCo) Datasets | `fixed` | `simulated` + `model-generated` | derived_from MAMuJoCo envs | DERIV |
| Hopper Controller | `fixed*` \| `oracle` | `constructed` + `simulated` | Design-Bench: random weight vectors (`constructed`) scored by MuJoCo rollouts (`simulated`); an oracle when new designs are scored | S/C F/O PAPER |
| FDA-approved UVA/Padova Type1 Diabetes Mellitus Simulator | `interactive*` \| `generator` | `simulated` | properly named (Simglucose) | G/I |
| Gene Regulatory Network Simulation Data from SERGIO | `generator*` \| `fixed` | `simulated` | SERGIO is a named simulator; the *network simulated* is unnamed | G/I |
| Neuronal Network Simulation Data from NEST | `generator*` \| `fixed` | `simulated` | NEST is a general simulator = **library**; the specific model is unnamed → double-bind, see §3.1 | G/I |
| NeuroTouch FEM simulation dataset | `fixed*` \| `generator` | `simulated` | NeuroTouch is a named simulator; "a commercial-grade simulator" in the quote | G/I |
| Sitnikov Problem Simulation Dataset | `fixed*` \| `generator` | `simulated` / `constructed` | an idealised restricted-3-body system: Newtonian units (simulated) over a system that does not exist (constructed) | S/C G/I |
| CAMELS suite | `fixed*` | `simulated` | cosmological hydro runs | |
| Fast Folding Proteins Benchmark | `fixed` | `simulated` | MD trajectories | |
| CityLearn | `interactive*` | `simulated` + `human-incidental` | building/demand models driven by real recorded load traces | DERIV |
| PowerGridworld | `interactive*` | `simulated` + `human-incidental` | same shape | DERIV |
| Flatland | `interactive*` | `simulated` / `constructed` | a discretised railway abstraction: real referent, no physical units | S/C |
| MultiSensory Embodied 3D-Scene Environment | `interactive*` | `simulated` / `constructed` | contributed; authored multisensory scenes | S/C |

### 1.3 Embodied / driving simulators with scanned or authored scenes

| name | access | provenance | note | flags |
|---|---|---|---|---|
| CARLA | `interactive*` \| `generator` \| `fixed` | `simulated` / `constructed` | physics with units over artist-authored towns | S/C G/I |
| CARLA NoCrash benchmark | `interactive*` | `simulated` + `rule` | NoCrash's infraction/success signal is a hand-coded detector; the expert is a scripted autopilot | S/C RULE |
| AI2Thor | `interactive*` | `simulated` / `constructed` | authored household scenes + physics | S/C |
| Gibson Environment | `interactive*` **and** `generator` | `natural` + `simulated` + `human-incidental` | the quote uses it *both* to generate training sets and to evaluate — two accesses in one mention | S/C G/I CONTRA |
| Habitat Pick (HabPick) | `interactive*` | `natural` + `simulated` + `human-incidental` | laser-scanned real interiors, then rendered — nodes.tsv's named hard case, and it is a **three-way**, not a two-way | S/C CONTRA |
| Duckietown | `interactive*` \| `fixed` | `natural` + `constructed` | camera images of a physically constructed miniature town | S/C |
| WebArena | `interactive*` | `constructed` + `human-incidental` | real open-source web apps, seeded with synthetic content | S/C |
| MiniWoB | `interactive*` | `constructed` | synthetic web pages | S/C |

### 1.4 Grid worlds, games and other constructed environments

| name | access | provenance | note | flags |
|---|---|---|---|---|
| MiniGrid | `interactive*` \| `generator` | `constructed` | layouts minted per seed | S/C G/I |
| MiniGrid benchmark | `interactive*` \| `generator` | `constructed` | alias | S/C G/I |
| MiniGrid Dynamic Obstacles | `interactive*` | `constructed` | task within MiniGrid | S/C |
| MiniGridLoCA | `interactive*` | `constructed` | named LoCA variant | S/C |
| Two Rooms Dynamic Obstacles Environment (2RDO) | `interactive*` | `constructed` | paper-local but named | S/C |
| Four Rooms environment | `interactive*` | `constructed` | canonical named construction | S/C |
| BabyAI | `interactive*` \| `generator` | `constructed` + `elicited` | synthetic instruction grammar; the human-demo subset is elicited | S/C G/I |
| Hypergrid Environment | `interactive*` \| `generator` | `constructed` | GFlowNet benchmark; controllable sparsity = a generator knob | S/C G/I |
| 2D windy grid-world (Wet Chicken) | `interactive*` | `constructed` | Wet Chicken is a named benchmark problem | S/C |
| Squirrel’s World Environment (SW) | `interactive*` | `constructed` | paper-local name, admissible | S/C |
| GhostRun environment (Jiang, 2019) | `interactive*` | `constructed` | | S/C |
| Procgen | `interactive*` **and** `generator` | `constructed` | levels minted per seed then stepped — both access tests pass | S/C G/I |
| Procgen Benchmark | `interactive*` **and** `generator` | `constructed` | | S/C G/I |
| Procgen-Maze | `interactive*` **and** `generator` | `constructed` | | S/C G/I |
| ProcGen CoinRun | `interactive*` **and** `generator` | `constructed` | | S/C G/I |
| TextWorld | `interactive*` **and** `generator` | `constructed` | "a platform for *generating* synthetic worlds" — it generates environments, then you step them | S/C G/I |
| NetHack Learning Environment (NLE) | `interactive*` | `constructed` | | S/C |
| Behavior Suite (BSuite) | `interactive*` | `constructed` | also a library + analysis protocol | S/C |
| StarCraft Multi-Agent Challenge (SMAC) | `interactive*` | `constructed` | runs on the commercial SC2 binary → availability, not access | S/C |
| StarCraft Multi-Agent Challenge | `interactive*` | `constructed` | alias | S/C |
| StarCraft II Multi-Agent Challenge | `interactive*` | `constructed` | alias | S/C |
| Hanabi | `interactive*` | `constructed` + `rule` | outcomes from the rules of the game; partners may be pretrained agents | S/C RULE |
| Kuhn Poker | `interactive*` | `constructed` + `rule` | via OpenSpiel; terminal payoffs by rule | S/C RULE |
| Leduc Poker | `interactive*` | `constructed` + `rule` | | S/C RULE |
| MeltingPot | `interactive*` | `constructed` | background co-players are **trained agents**; per SYNTHESIS §4 they are catalogued as models, so no `model-generated` on the env | S/C |
| CartPole | `interactive*` | `simulated` / `constructed` | ODEs with physical units; no cart exists | S/C |
| Acrobot | `interactive*` | `simulated` / `constructed` | | S/C |
| Pendulum | `interactive*` | `simulated` / `constructed` | | S/C |
| Pendulum-v0 | `interactive*` | `simulated` / `constructed` | | S/C |
| MountainCar | `interactive*` | `simulated` / `constructed` | | S/C |
| Continuous Mountain Car | `interactive*` | `simulated` / `constructed` | | S/C |
| MountainCarLoCA | `interactive*` | `simulated` / `constructed` | named LoCA variant | S/C |
| SAGE Benchmark | `interactive*` | `constructed` + `elicited` | contributed; 50 authored smart-home tasks | |

### 1.5 Reference corpora and web text

| name | access | provenance | note | flags |
|---|---|---|---|---|
| Wikipedia | `fixed*` \| `oracle` \| `stream` | `human-incidental` | the **only** name in the 194 that can legitimately take `stream` (recent-changes feed), and it never does | F/O PAPER |
| Subset of English Wikipedia | `fixed*` \| `oracle` | `human-incidental` | a *subset* — Part C: same node as Wikipedia, so this string should collapse | F/O DERIV |
| WikiText-103 | `fixed` | `human-incidental` | derived_from Wikipedia; transformation injects nothing | DERIV |
| WikiText-2 | `fixed` | `human-incidental` | same | DERIV |
| Wikipedia-based Image Text | `fixed` | `human-incidental` | WIT; derived_from Wikipedia | DERIV |
| Wikipedia dataset | `fixed` | `human-incidental` + `elicited` | **not Wikipedia**: the quote shows the Wikipedia *Toxicity* set (comments + human toxicity labels) | PAPER |
| tkgl-wikidata | `fixed` | `human-incidental` | the *content* is human edits; the temporal signal is the machine-written edit log — on the fold's seam | STRAIN DERIV |
| Common Crawl | `fixed*` \| `oracle` | `human-incidental` | served by shard id; snapshots, never the live crawl | F/O |
| German Common Crawl | `fixed` | `human-incidental` | derived_from Common Crawl (language split) | DERIV |
| C4 | `fixed` | `human-incidental` | derived_from Common Crawl; heuristic filters **select**, so inject no value | DERIV |
| The Pile | `fixed` | `human-incidental` | | |
| Pile | `fixed` | `human-incidental` | alias | |
| PubMed | `fixed*` \| `oracle` | `human-incidental` | **three entities share this string**; the quote's node-embedding use makes it the Planetoid citation graph | F/O PAPER |
| PubMed Central | `fixed*` \| `oracle` | `human-incidental` | the quote reaches it via the Pile subset | F/O DERIV |
| MS MARCO | `fixed*` \| `oracle` | `human-incidental` + `elicited` | Bing query log (byproduct of operation) + human-written relevance/answers | STRAIN F/O |
| One Billion Word Benchmark (LM1B) | `fixed` | `human-incidental` | news crawl | |
| Reddit FL benchmark dataset | `fixed` | `human-incidental` | the name screams *federated*; the axes place it with no loss except locality — SYNTHESIS §1's decision confirmed on a real name | |
| IMDB-Wiki Dataset | `fixed` | `natural` + `human-incidental` | photographs + ages taken from existing metadata, **not** elicited labels | |
| Compositional Freebase Queries (CFQ) | `fixed*` \| `generator` | `constructed` + `human-incidental` | questions synthesised by grammar over Freebase facts | |
| Compositional Freebase Questions (CFQ) | `fixed*` \| `generator` | `constructed` + `human-incidental` | the same entity; `Queries` is a mis-rendering — alias **written**, not inferred from the one-word edit distance | |

### 1.6 Benchmark suites over heterogeneous members

| name | access | provenance | note | flags |
|---|---|---|---|---|
| GLUE Benchmark | `fixed` | `human-incidental` + `elicited` | union over members (SST/QQP incidental, MNLI/RTE elicited) | |
| GLUE | `fixed` | `human-incidental` + `elicited` | alias | |
| SuperGLUE | `fixed` | `human-incidental` + `elicited` | | |
| BIG-bench | `fixed` | `elicited` + `constructed` + `human-incidental` | contributed; 200+ author-written tasks, many programmatic | |
| BIG-Bench (BB) | `fixed` | `elicited` + `constructed` + `human-incidental` | alias | |
| BBH | `fixed` | `elicited` + `constructed` + `human-incidental` | a curated subset of BIG-bench | DERIV |
| BBH (BigBench Hard) | `fixed` | `elicited` + `constructed` + `human-incidental` | alias | DERIV |
| BigBench Hard | `fixed` | `elicited` + `constructed` + `human-incidental` | alias | DERIV |
| MMLU | `fixed` | `human-incidental` | **scraped from existing practice exams**, not written to order — counter-intuitive and needs the dataset paper, not the citing one | PAPER |
| MMLU benchmark | `fixed` | `human-incidental` | alias | PAPER |
| HELM | `fixed` | `human-incidental` + `elicited` + `constructed` | HELM is mostly a **harness**: one string, a library and a scenario collection | |
| Long Range Arena (LRA) | `fixed` | `constructed` + `human-incidental` + `natural` | ListOps/Pathfinder constructed, text incidental, CIFAR natural — a genuinely meaningless union | |
| Long Range Graph Benchmark (LRGB) | `fixed` | `natural` + `simulated` + `human-incidental` | peptides + images | |
| Visual Task Adaptation Benchmark (VTAB) | `fixed` | `natural` + `elicited` + `simulated` + `constructed` | 19 datasets; the widest union in the set | |
| SubpopBench suite | `fixed` | `natural` + `human-incidental` + `elicited` + `constructed` | Waterbirds is itself a composite | DERIV |
| CrossFit | `fixed` | `human-incidental` + `elicited` | 160 tasks | |
| T0 task suite | `fixed` | `human-incidental` + `elicited` | | |
| Super-Natural Instructions | `fixed` | `elicited` + `human-incidental` | contributor-written instructions over existing datasets | |
| Super-Natural Instructions (SuperNI) | `fixed` | `elicited` + `human-incidental` | alias | |
| IndicXTREME | `fixed` | `elicited` + `human-incidental` | 9 tasks, 19 languages | |
| XTREME-UP | `fixed` | `elicited` + `human-incidental` | | |
| OpenML-CC18 | `fixed*` \| `oracle` | `natural` + `human-incidental` + `elicited` + `constructed` | **defined as a set of API task ids** — pulled by identifier, which is `oracle`'s test verbatim | F/O |
| OpenML-CTR23 | `fixed*` \| `oracle` | `natural` + `human-incidental` + `elicited` + `constructed` | same | F/O |

### 1.7 Domain datasets and benchmarks

| name | access | provenance | note | flags |
|---|---|---|---|---|
| Canadian Urban Environmental Health Research Consortium (CANUE) | `fixed` | `human-incidental` + `rule` | area-level deprivation/access **indices computed by a stated formula** over administrative records; the keyword `environment` is wrong (built environment) | STRAIN RULE DERIV |
| Mandl benchmark | `fixed` | `human-incidental` | a 15-node city transit graph: infrastructure, nobody's artifact-collected-afterwards | STRAIN |
| Mumford benchmark | `fixed` | `human-incidental` | real city networks, same shape | STRAIN |
| ExtremeWeather | `fixed` | `simulated` + `elicited` | CAM5 climate runs + expert-drawn boxes — the channel problem on one row | |
| ProteinGym benchmark | `fixed` | `natural` | 217 deep mutational scanning assays: the signal exists **only because** the assay was ordered, so `natural`'s positive test fails on its own exemplar class | CONTRA |
| Neural Latents Benchmark | `fixed` | `natural` | monkeys performing an experimenter's task — `elicited` fits but is scoped to *people* | CONTRA |
| German Traffic Sign Recognition Benchmark (GTSRB) | `fixed` | `natural` + `elicited` | | |
| TNMIX benchmark | `fixed` | `natural` + `elicited` | **two parents** (TNSCUI + DDTI); the axes say nothing about a merge | DERIV |
| Juliet Test Suite | `fixed` | `constructed` + `rule` | template-synthesised vulnerable code; the label follows from the CWE template | S/C RULE |
| ER-Magellan benchmark datasets | `fixed` | `human-incidental` + `elicited` | product/bib records + match labels | |
| HalOmi benchmark dataset | `fixed` | `model-generated` + `elicited` | the annotated items are **MT outputs**; the only name here whose `model-generated` arrives entirely through a parent | DERIV |
| Semantic Textual Similarity Benchmark (STS-B) | `fixed` | `human-incidental` + `elicited` | news/caption sentences + similarity ratings | |
| BBQ Benchmark | `fixed` | `elicited` + `constructed` | hand-written templates, programmatically expanded | |
| PII Benchmark | `fixed` | `human-incidental` + `elicited` | contributed; 400 real code files + annotations | |
| MatSci-NLP Benchmark | `fixed` | `human-incidental` + `elicited` | contributed | |
| Advanced Arithmetic Benchmark | `fixed*` \| `generator` | `constructed` **/** `rule` | contributed; templates whose answers are computed by arithmetic | RULE G/I |
| Toy Arithmetic Benchmark | `fixed*` \| `generator` | `constructed` **/** `rule` | contributed; same | RULE G/I |
| Poker Hand | `fixed` | `constructed` + `rule` | enumerated hands, class computed by the rules of poker; the quote calls it a *data stream* yet it is replayable → `fixed` | RULE |
| RB benchmark | `fixed*` \| `generator` | `constructed` | RB-model instances are minted on demand but distributed as instance files | G/I |

---

## 2. Rejections — 25 names, by clause

### 2.1 "The software that implements a source" — 3

- **MuJoCo** (10 papers). Part A's own example: the physics engine is a library;
  `HalfCheetah`, `Hopper`, `Humanoid` are the data sources. The highest-frequency
  name in the whole candidate set is a rejection.
- **PyBullet**. Same clause; the quote says "classical PyBullet *environments*",
  and those environments are the sources.
- **OpenAI Gym**. An API plus a wrapper collection. **Contested**: in practice the
  string is also the de facto name of the classic-control + locomotion set, and
  rejecting it leaves that mention with no source at all.
- `dm_control suite` and `HELM` are the same one-string-two-entities shape but
  were **admitted**, because each also names a definite content set. The
  inconsistency is real and is recorded as a tension (§3.1), not smoothed over.

### 2.2 "Unnamed descriptions" — 22

Clean descriptions of a *kind* of source:
**GridWorld** (6 papers — the most-cited rejection in the set),
**Grid-world Environments**, **Grid World Dataset**, **Grid Environment Dataset**, **3D environments** ("grid worlds, continuous control, video games,
and 3-D environments"), **Molecule synthesis environment**, **Atari games
dataset**, **widely used activity recognition benchmark datasets**,
**Simulation Datasets of RAN** ("a system-level RAN simulator[36,37]"),
**Tuning MEG simulation dataset** ("we simulated a dataset of 108,000
realistic MEG sensor recordings"), **fixed-boundary mapping benchmark** and
**free-boundary mapping benchmark** (both "the benchmark data set in [Du et al.]").

Unnamed derivations — a fixed log drawn from an interactive source, which #102
Part E makes a *step*, not an entity:
**Offline Ant Maze** ("we collect new offline datasets"),
**CARLA Multi-Town dataset** ("we collect a dataset from Town01"),
**Generated Datasets from DeepMind Control Suite** (released, but still not
named), **Lunar Lander Game Data**, **Chess games annotated by Stockfish**.

Description-shaped strings for a de facto standard suite — **contested**, because
`Gym MuJoCo Benchmark` names the same thing properly:
**MuJoCo Environments**, **MuJoCo locomotion benchmark environments**,
**Mujoco-based environments**.

Private artifacts with no name — **contested**, see §3.2:
**5G Proprietary System-Level Network Simulator**,
**Proprietary System Level RAN Simulator Dataset** (`contributed=1`).

### 2.3 What the rejections cost, measured

- `Chess games annotated by Stockfish` was the **cleanest `rule` instance in the
  sample** — Stockfish is a non-learned engine, 15 billion labelled data points.
  The admission rule deletes it.
- Both proprietary RAN/5G simulators are **contributed** — institute output,
  which #102 Part E calls a headline question — and both are rejected for
  lacking a name. Run A's phase-1 prediction that the named-only threshold
  "biases away from private collection and simulation" is **confirmed on 2 of 2
  private simulators in this set**.
- The clause bites harder than Part E's ~1.6%-of-names figure suggested: **22 of
  194 (11%) here**, carrying 6+1+1 papers for `GridWorld`/`3D
  environments`/others. That is a property of this keyword-selected sample
  (`environment` selects descriptions), not a correction to Part E — but a step-5
  loader run on the full 2559 should re-measure the clause per keyword bucket.

---

## 3. Tensions

### 3.1 A value no node supplies

**(a) `elicited` is scoped to people; designed non-human experiments have no
value.** `ProteinGym benchmark` (217 deep mutational scanning assays) and
`Neural Latents Benchmark` (monkeys performing an experimenter's reaching task)
both satisfy `elicited`'s positive test verbatim — *"remove the research request
and the signal does not exist"* — and fail `natural`'s — *"remove every human
purpose and the process still runs"*. Neither is `elicited`, because no person
produced the signal. I place both `natural` and record the gap.
**Proposed (admission-rule-compliant: these names are placeable only by
overriding a test):** either rescope `elicited`'s characteristic to *"the signal
exists because the collection asked"*, dropping "from people" — which also
re-homes teleoperated demos and wet-lab assays coherently — or add a value for
*a designed experiment on a non-human system*. The first is cheaper and loses
nothing: "crowd vs expert is not a distinction on this axis" already says the
axis does not care who.

**(b) Protocol-over-a-source has no expression.** `Atari 100k`, `Atari 100k
benchmark`, `100k benchmark`, `Atari 2600 benchmark`, `Atari Benchmark`, `CARLA
NoCrash benchmark`, `EARL benchmark`, `URLB` ×3, `RWRL` ×2 — **12 admitted
strings** are *interaction budgets or perturbation schedules over an underlying
environment*, not sources. They are named, so the admission rule admits them;
both axes then return exactly the base environment's values, so 12 strings add
zero information and inflate every per-value count. Part D assigns the protocol
half to algorithms `R.eval`, which is right, but nothing in this dimension
records that these names *are* protocols. **This is not a request for an axis
value** — it wants either `derived_from`-like relation (`protocol_over`) or an
explicit alias-to-base ruling at step 5.

**(c) Version is not a derivation, a subset, or anything.** `HalfCheetah-v2` vs
`-v3`, `Hopper` vs `Hopper-v2`, `Pendulum` vs `Pendulum-v0`. Part C covers
subsets and unnamed transformations; a version bump that changes the dynamics is
neither. Low stakes, recorded.

**(d) One-string-two-entities at suite scale.** `dm_control suite`, `HELM`,
`Behavior Suite (BSuite)`, `OpenML-CC18/CTR23`, `OpenAI Gym` are each a library
*and* a content set. Part A's FlashAttention shape handles this for `MuJoCo`
because the engine and the environments have different names; here they do not.
I split inconsistently (rejected `OpenAI Gym`, admitted `dm_control suite`) and
flag that I could not find a principled line in the nodes.

### 3.2 Two values that fit equally well — not broken

**(a) `generator` vs `interactive`, within a single mention — 19 names.**
`Procgen`, `Procgen Benchmark`, `Procgen-Maze`, `ProcGen CoinRun`, `TextWorld`,
`MiniGrid`, `MiniGrid benchmark`, `BabyAI`, `Hypergrid Environment`, `CARLA`,
`Gibson Environment`, `Sitnikov Problem Simulation Dataset`, the two arithmetic
benchmarks, `RB benchmark`, the UVA/Padova simulator, SERGIO/NEST/NeuroTouch.
A procedurally generated source **mints a level on request** (`generator`'s
positive test passes: ask for twice as many, get twice as many; a seed change
yields fresh ones) **and then holds state across the episode**
(`interactive`'s passes: `reset` is a distinct operation, the agent's choices
determine the next observation). Each value's negative test is written to
exclude the other, so both exclusions fire and the axis is single-valued.
**This is a different tension from the 3/3 one SYNTHESIS §3 records.** That one
is resolved by the mention rule — a frozen log is a different mention. This one
is *one mention* in which both values are simultaneously true, which the mention
rule cannot touch. `Gibson Environment` makes it explicit in the quote: *"both
to generate training datasets and to evaluate navigation performance"*.
Not broken; recorded.

**(b) `simulated` vs `constructed` — 65 names.** See §4.5.

**(c) `rule` vs `constructed` — 6 names.** `Kuhn Poker`, `Leduc Poker`,
`Hanabi`, `Poker Hand`, `Advanced Arithmetic Benchmark`, `Toy Arithmetic
Benchmark`. `rule`'s positive test (*a person could check the signal by applying
a written rule with no learned parameters*) and `constructed`'s (*the generating
specification IS the ground truth*) are **both true**, and neither negative test
excludes the other. nodes.tsv itself records this as the B-vs-A/C divergence and
supplies no separating test. The corpus does not arbitrate (METHOD §1), so I
record both with `/` and do not break it.

**(d) `fixed` vs `oracle` — 9 names.** `Wikipedia`, `Subset of English
Wikipedia`, `Common Crawl`, `PubMed`, `PubMed Central`, `MS MARCO`,
`OpenML-CC18`, `OpenML-CTR23`, `Hopper Controller`. `oracle`'s negative test
("fails if the consumer downloaded the whole source first") is a fact about the
mention that the name never carries, and `OpenML-CC18` is *defined* as a list of
API task ids — `oracle`'s positive test verbatim — while every paper treats it
as a fixed table set. `oracle`'s own note predicted this ("its real differentia
is possession/enumerability"). **The tie is in the node, not in the names.**

### 3.3 Undecidable from the name alone — needs the paper

- **`PubMed`** — three distinct entities: the Planetoid citation *graph*, the
  abstracts *corpus*, the search *API*. Same provenance, different access,
  wildly different size. The quote (node embeddings) resolves it to the graph.
  The single worst string in the 194.
- **`Wikipedia dataset`** — the Wikipedia *Toxicity* set, not Wikipedia text.
  Name alone gives `human-incidental`; the quote adds `elicited`.
- **`Atari`, `Atari Games`, `Atari 2600 Games`, `Atari 2600`, `Atari 57`** — live
  emulator or replay dump. 5 undecidable strings against 3 unambiguously `fixed`
  (`Atari DQN replay dataset`, the two RL Unplugged strings) and 3 unambiguously
  `interactive` (the ALE strings). SYNTHESIS §3's 3/3 finding, instantiated 11
  times in one family.
- **`CALVIN`** — one name over a simulator and a 24-hour teleoperated play
  corpus. The MineRL shape with a new name.
- **`D4RL` / `D4RL Benchmark`** — denotes the offline datasets, yet papers
  routinely evaluate online in the shipped environments.
- **`Hopper` / `Hopper-v2` / `hopper_stand` / `Hopper Controller`** — four
  strings, **three** entities (Gym locomotion, a DMC task, a Design-Bench design
  set). `Hopper Controller` is `fixed` + `constructed`/`simulated`; the others
  are `interactive` + `simulated`. Token matching merges all four — the
  "aliases are written, never inferred" rule, instantiated.
- **`MMLU`** — `human-incidental` (scraped exams) or `elicited` (authored
  questions) is decided by the *dataset* paper, which the citing paper's quote
  never contains. The hardest kind: the paper you have does not help.
- **`100k benchmark`** — the quote is needed even to learn that the source is ALE.
- **`Wikipedia`** — `fixed` dump / `oracle` RAG index / `stream` recent-changes.

### 3.4 `positive_test` and `negative_test` give contradictory answers

**(a) `simulated`'s note contradicts `simulated`'s positive test, on 46 names.**
The note says the value *"absorbs `rendered` (graphics from authored assets)"*,
which routes every Atari frame, Procgen frame, MiniGrid render, SMAC frame and
NetHack glyph to `simulated`. The positive test demands *"a solver or engine
whose parameters have physical units, and 'the simulation is wrong' is a
meaningful complaint"* — **false** of an Atari emulator: the emulator is not
wrong about anything, it *is* the referent. Meanwhile `constructed`'s positive
test (*the generating specification IS the ground truth*) is true. Affected, 46
in all: 20 Atari strings, 4 Procgen, 4 MiniGrid-family, 3 SMAC, NetHack,
TextWorld, MiniWoB, Hanabi, 2 poker, MeltingPot, BSuite, BabyAI, Four Rooms,
2RDO, Hypergrid, Wet Chicken, Squirrel’s World, GhostRun. **This is the largest single
defect I found, and it is in a note rather than in a test** — exactly the
"a pin that exists and is wrong" failure METHOD §2 says to look for.
**Fix shape, no new value:** restrict the `rendered` absorption to *graphics of a
modelled real referent* (CARLA, Habitat), and say explicitly in
`constructed`'s row that games and emulators are `constructed`.

**(b) `natural`'s positive test excludes `natural`'s own exemplars.**
*"Remove every human purpose and the process still runs and the signal still
exists"* is **false** for a deep mutational scanning assay (`ProteinGym`), for a
monkey reaching task (`Neural Latents Benchmark`), for a Duckiebot camera pass
(`Duckietown`) — and false for `fastMRI`, which nodes.tsv lists as a `natural`
example. The negative test (*a human artifact or judgement arriving through an
instrument is not natural*) does not exclude them, so the two tests disagree.
Run A's recorded worry that `natural` "risks vacuity" is the same defect from
the other side: the positive test was tightened to fix vacuity and overshot.

**(c) `human-incidental`, `natural` and `simulated` all pass on Habitat/Gibson.**
`Gibson Environment` and `Habitat Pick`: the scanned interiors are human
artifacts that would exist unchanged had the dataset never been conceived
(`human-incidental` positive test: **true**), they are laser-measurement output
(`natural`: **true**), and they are served through a physics-plus-rendering
engine (`simulated`: **true**). nodes.tsv flags Habitat as the recurring hard
case on one boundary; it is a **three-way**. I record all three values, which is
legal on a multi-valued axis — so this one is survivable, unlike (a).

**(d) `fixed` on `Procgen`.** Positive test: *"every example could be enumerated
before the run starts, knowing nothing about the consumer"* — arguably **true**,
the seed space is fully determined and re-running a seed reproduces the level.
Negative test: *"fails if the consumer's sampling budget changes which examples
exist"* — the budget is exactly what determines which levels exist. Both fire.

### 3.5 Where `derived_from` is doing work the axes cannot

**It injects a value on the RL side and never on the text side — that asymmetry
is the finding.**

- **Injecting:** `Atari DQN replay dataset`, `Atari Dataset from RL Unplugged`,
  `RL Unplugged Atari Dataset`, `D4RL`, `D4RL Benchmark`, `Multi-Agent MuJoCo
  Datasets` — six names where `derived_from` flips `access` to `fixed` and the
  *transformation* adds `model-generated`, because a trained agent's policy
  determined the state distribution. Without the relation these read `fixed` +
  `constructed`/`simulated`, which loses the only fact that explains how they
  behave. `HalOmi benchmark dataset` is the text-side exception: `model-generated`
  arrives wholly from the parent (an MT system's outputs).
- **Pure bookkeeping:** `C4`←Common Crawl, `German Common Crawl`←Common Crawl,
  `WikiText-103`/`WikiText-2`/`Wikipedia-based Image Text`/`Subset of English
  Wikipedia`/`tkgl-wikidata`←Wikipedia, `BBH`←BIG-bench, `PubMed
  Central`←the Pile. Seven names, zero values injected. The model-based-selector
  question SYNTHESIS §2 leaves open (*does FineWeb-Edu-style filtering inject
  `model-generated`?*) **gets no instance in this sample**: every filter here is
  heuristic, so the open question stays open rather than being accidentally
  resolved.
- **Multi-parent, unexpressed:** `TNMIX benchmark` merges TNSCUI and DDTI. The
  axes say nothing about a merge, and `provenance` as a union hides that the
  two halves differ.
- **Transformation-introduces-a-value, non-model case:** `CANUE`. The
  administrative records are `human-incidental` (upstream) and the deprivation
  indices are `rule` (introduced by the transformation). The inheritance rule
  states this exactly; without it the row is an unreadable two-value set.
- **The seven logs that could not get an entity:** `Offline Ant Maze`, `CARLA
  Multi-Town dataset`, `Generated Datasets from DeepMind Control Suite`, `Lunar
  Lander Game Data`, `Atari games dataset`, `Grid World Dataset`, `Grid Environment Dataset` are all *exactly* "a fixed log drawn from an interactive
  source" and all unnamed, so `derived_from` cannot record them and the only
  trace is `access=fixed` on the mention. **The entity-versus-mention rule
  working as designed, at a cost of 7 of 194 strings.** One of them
  (`Generated Datasets from DMC`) was publicly released, which is the closest
  this sample comes to breaking the naming criterion.
- **Where `derived_from` is the *wrong* relation:** the 12 protocol names of
  §3.1(b). `Atari 100k` is not derived from ALE; it is a budget over it.

---

## 4. The five measurements

### 4.1 `provenance-other`: **0 names. Of those, 0 machine-emitted operational records.**

Not one of the 169 admitted names needs `provenance-other`. **This sample cannot
measure the thing SYNTHESIS §2 installed the instrument to measure**, and the
reason is structural, not evidential: the candidate set was selected by the
keywords `environment`, `suite` and `reference`, and a Borg/Alibaba-style
cluster trace matches none of them. The measurement needs a sample drawn across
all 2559 names.

What the 0 does say, which is not nothing:

- The only genuinely **machine-emitted** records in the set are agent replay logs
  — `Atari DQN replay dataset`, the two RL Unplugged strings, `D4RL`, `MAMuJoCo
  Datasets`. They are machine-emitted operational records in the strictest sense
  and **they already have a home**: `model-generated` + the source's own value.
  So machine-emitted ≠ homeless; §2's claim that telemetry "has nowhere else to
  go" holds only for machine records with *no model in the causal chain*.
- Per METHOD §1 and the rules of evidence: **this 0 is not evidence for or
  against restoring the byproduct value.** It is evidence that the step-4 sample
  cannot see it.

### 4.2 Strained `human-incidental`: **4 strained, 1 mild**

- **`CANUE`** — the strongest. An area-level deprivation/service-access *index*,
  computed by an institution. No individual's artifact was collected afterwards;
  the clinician/clicker/rater analogy that justifies the fold does not hold. Only
  the `+ rule` second value makes the row readable at all.
- **`Mandl benchmark`**, **`Mumford benchmark`** — a city's transit network is
  infrastructure. `human-incidental`'s positive test passes literally (the
  network would exist unchanged), but calling a rail topology "incidental human
  activity" is a stretch of the same kind C flagged.
- **`tkgl-wikidata`** — sits *on the seam*: the content is human edits
  (`human-incidental`, uncontested) but the temporal signal the dataset exists
  for is the **machine-written edit log**. The fold handles the content and has
  nothing to say about the timestamps, which are the data.
- Mild and intended: **`MS MARCO`** — a Bing query log is the paradigm byproduct
  of operation and the fold handles it cleanly. Recorded to show the fold
  working, not failing.

So: the fold's human sub-cases hold up (click logs, ratings, clinical records all
land cleanly where present); what strains is the **institutional/administrative**
sub-case — run A's phase-1 `institutional_record`, not `system_telemetry`. That
is a different sub-case from the one §2 predicted would resist.

### 4.3 `rule` (speculative): **used. 9 names strictly; ~31 more under a broader reading.**

Strict (the rule produces the primary signal): **`Poker Hand`**, **`Kuhn
Poker`**, **`Leduc Poker`**, **`Hanabi`**, **`Advanced Arithmetic Benchmark`**,
**`Toy Arithmetic Benchmark`**, **`Juliet Test Suite`**, **`CANUE`**,
**`CARLA NoCrash benchmark`** = **9 of 169 (5.3%)**.

Two things worth more than the count:

1. **`CANUE` is a use B did not anticipate.** B's examples are verifiers, proof
   checkers, game outcomes and distant supervision. A statistical index computed
   by a published formula over administrative records passes `rule`'s test
   exactly and is a *provenance of ordinary tabular science data*. The
   characteristic is broader than its proposer thought — which is evidence for
   coherence, which is the test METHOD sets for a speculative value.
2. **The 9-vs-40 spread is the channel problem, not a `rule` problem.** Under the
   reading that a rule-computed *reward* earns the value, every game environment
   qualifies — the Atari score, the SMAC win condition, the NetHack score, the
   Procgen reward: 31 more names, taking `rule` to 40 of 169 (24%). `provenance` is not channel-scoped
   (SYNTHESIS §3, 3/3), so there is no principled stopping point between 9 and
   40 — between 5% and 24% of the admitted set. I report the strict count and name the ambiguity rather than picking.
3. The cleanest instance in the sample, **`Chess games annotated by Stockfish`**,
   was **deleted by the admission rule** (§2.3).

`rule` should be kept. It is used, it is used in a domain its proposer did not
reach, and the names that carry it would otherwise be mis-filed as `constructed`
— which is false of real code (`Juliet`) and of real administrative records
(`CANUE`).

### 4.4 `stream`: **0 names.**

Zero of 169 admitted names take `stream` as their typical value. Exactly one —
**`Wikipedia`** — can legitimately take it (the recent-changes feed), and no
mention here does: every mention is a dump. **`Poker Hand` is the instructive
near-miss**: its quote calls it a "multiclass data stream", yet the file is
replayable and two runs consume identical examples, so `stream`'s positive test
fails and it is `fixed`. The name says stream and the test says fixed, correctly.

Per SYNTHESIS §3 and METHOD §1 this is **expected and is not evidence against
the value**, and I make no proposal about it. The sample is also the wrong one:
`environment`/`suite`/`reference` keywords cannot select a live feed. Recoding
`Wikipedia`-as-live-feed to `fixed` would assert a reproducibility it does not
have — which is the whole argument for keeping the value, unchanged.

### 4.5 `simulated` / `constructed`: **bites on 65 of 169 admitted names (38%).**

Breakdown, 65 = 20+4+11+7+3+4+2+14: the **20** Atari strings · **4** Procgen ·
**11** grid-world/toy-env (MiniGrid ×2, MiniGrid Dynamic Obstacles, MiniGridLoCA,
2RDO, Four Rooms, BabyAI, Hypergrid, Wet Chicken, Squirrel’s World, GhostRun) ·
**7** classic control (CartPole, Acrobot, Pendulum ×2, MountainCar, Continuous
Mountain Car, MountainCarLoCA) · **3** SMAC · **4** embodied (AI2Thor, Gibson,
HabPick, MESE) · **2** CARLA · and **14** singletons (Hanabi, Kuhn Poker, Leduc
Poker, NetHack, TextWorld, MiniWoB, WebArena, Flatland, Duckietown, MeltingPot,
BSuite, Sitnikov, Juliet, Hopper Controller).

**This is the single biggest result of the run.** All three phase-1 runs flagged
the boundary; the flag said "Habitat is the recurring hard case", i.e. an edge.
It is not an edge — it is **more than a third of the admitted names and the great
majority of the RL half of this dimension**, and the sub-populations differ:

- **Games and emulators** (46 names, enumerated in §3.4a) are `constructed` by
  both values' tests, and `simulated` claims them only through the `rendered`
  absorption note. A note is overruling a test on 46 of them.
- **Classic control** (7) is the genuine tie: physical units (`simulated`) over a
  system that does not exist (`constructed`). Not resolvable from the tests, and
  I record it unresolved.
- **Scanned-interior embodied sims** (4) are a *three-way* with `natural`,
  survivable because the axis is multi-valued.
- **`Flatland`, `Sitnikov`, `Hopper Controller`, `Juliet`** are one-off hybrids
  each for a different reason.

The corpus does not arbitrate (METHOD §1), so I propose no deletion and no
merge. What I do propose is a **test repair, not a value change**: tighten
`simulated`'s `rendered` absorption to graphics *of a modelled real referent*,
and add games/emulators to `constructed`'s examples. That resolves 46 of the 65
by making the note agree with the test, and leaves the 7 classic-control ties and
the 4 three-ways genuinely open — which is the right size for the thing all three
runs flagged.

---

## 5. What I would change about the two axes

Ordered by how much this sample supports it.

1. **Repair `simulated`'s `rendered` note** (§3.4a, 46 names). Highest-value,
   zero-cost: no value added, no value removed.
2. **Repair `natural`'s positive test** (§3.4b) so it does not exclude fastMRI,
   `ProteinGym` and `Neural Latents Benchmark`. The test currently reads as
   "unobserved by design", which is not the characteristic.
3. **Rescope `elicited`** from *"from people"* to *"because the collection
   asked"* (§3.1a). This is the only **addition-shaped** proposal in the run and
   the admission rule permits it: `ProteinGym` and `Neural Latents Benchmark`
   cannot be placed without overriding a test. Rescoping is cheaper than a new
   value and loses nothing the axis already says it does not care about.
4. **Decide the 12 protocol names** (§3.1b) at step 5 — alias-to-base, or a
   `protocol_over` relation. Not an axis value either way, but left alone they
   silently triple the `interactive` + `constructed` count.
5. **Keep `rule`** (§4.3). Used, coherent, and used outside its proposer's
   domain.
6. **Keep `stream` and `provenance-other` unchanged** (§4.1, §4.4), and record
   that this sample **cannot** measure either — the keyword buckets exclude live
   feeds and telemetry by construction. The revisit the owner scheduled still
   needs real annotations, as METHOD §1 says.
7. **No change to `access`'s single-valuedness** on the fixed-vs-interactive
   question — the mention rule handles it. But §3.2(a)'s 17
   `generator`-and-`interactive` names are a *within-mention* collision the
   mention rule cannot reach, and nothing in the frozen design addresses it.
