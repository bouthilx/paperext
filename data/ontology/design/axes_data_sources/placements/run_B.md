# Data sources — step 4 placements, **run B of three**

#102 step 4. Independent placement run. Read, and nothing else:
`METHOD.md`, `SYNTHESIS.md`, `access/nodes.tsv`, `provenance/nodes.tsv`,
`placement_candidates.tsv`, and issue #102 Parts A and E. No other run's output
was read or looked for.

**194 candidate names. 175 admitted, 19 rejected.**

How to read the `access` column. `access` attaches to the **mention**
(SYNTHESIS §4), so a *name* cannot carry one value. The column therefore reads
`typical (+other legitimate values)`:

- `interactive (+fixed)` — normally stepped; a frozen log of it is `fixed`
- `fixed ONLY` — the name denotes a frozen artifact and `interactive` is **never**
  correct for it, however interactive its parent was
- `fixed (+oracle)` — normally downloaded; legitimately served by API

81 of 175 admitted names can take more than one `access` value legitimately.
9 are `fixed ONLY`. Typical values: `interactive` 96 · `fixed` 77 · `oracle` 1 ·
`generator` 1 · `stream` 0.

`provenance` attaches to the **entity** and is multi-valued, so the column is the
full set. `X ~ Y (TIE)` means the two node tests do not separate them and I am
recording the tie rather than breaking it (METHOD.md §2: the corpus does not
arbitrate). `[+ v]` means the value is live but undecidable from the name.

Provenance totals over 175 admitted names (non-exclusive):
`constructed` 99 · `simulated` 67 (of which **26 are the unresolved
`simulated ~ constructed` tie, counted in both**) · `human-incidental` 46 ·
`elicited` 37 · `rule` 12 · `natural` 12 · `model-generated` 10 ·
`provenance-other` **0**.

---

## 1. Placements

| name | access | provenance | note |
|---|---|---|---|
| DeepMind Control Suite | interactive (+fixed) | simulated | `access` is stable across the suite, `provenance` is not -- A's granularity-per-axis point (T6) |
| MuJoCo | -- | -- | REJECTED: admission rule, software-that-implements clause -- the physics engine, named explicitly in Part A. 10 papers; see Tension T1 |
| PubMed | oracle (+fixed) | human-incidental | typical access is genuinely `oracle` (E-utilities), but the paper's quote is about node embeddings and says nothing about supply: undecidable (T13) |
| D4RL | fixed ONLY | simulated + constructed + elicited + model-generated | the set's worst single row: locomotion from trained SAC policies (simulated + model-generated), AntMaze (the seam), Adroit human demos (elicited). `derived_from` -> MuJoCo/Adroit. One suite row, four provenance values, none of them informative (T6, T7) |
| MiniGrid | interactive (+fixed) | constructed |  |
| GridWorld | interactive | constructed | generic string admitted as the field's de facto family; borderline on the unnamed clause |
| Meta-World | interactive (+fixed) | simulated |  |
| Wikipedia | fixed (+oracle) | human-incidental | `fixed`'s test says 'predetermined independently of the consumer', which a rolling dump satisfies while being a different artifact every month -- C's temporal-stability gap (T12) |
| WikiText-103 | fixed | human-incidental |  |
| Arcade Learning Environment | interactive (+fixed) | constructed | alias cluster round the ALE; `simulated` is also arguable -- the ALE emulates real 2600 hardware (T5) |
| Arcade Learning Environment (ALE) | interactive (+fixed) | constructed | alias cluster round the ALE; `simulated` is also arguable -- the ALE emulates real 2600 hardware (T5) |
| Atari 2600 | interactive (+fixed) | constructed | alias cluster round the ALE; `simulated` is also arguable -- the ALE emulates real 2600 hardware (T5) |
| Atari 100k benchmark | interactive (+fixed) | constructed | NOT a distinct source: an interaction BUDGET / game subset over the ALE. Part D sends it to algorithms R.eval; the admission rule has no clause for it (T4) |
| BabyAI | interactive | constructed | instruction language is grammar-generated, so `elicited` does NOT apply |
| OpenAI Gym | -- | -- | REJECTED: admission rule, software-that-implements clause -- an environment-interface library. See T1 |
| The Pile | fixed | human-incidental |  |
| AI2Thor | interactive (+fixed) | simulated | artist-authored interiors: `rendered` folded into `simulated` |
| Atari | interactive (+fixed) | constructed | alias cluster round the ALE; `simulated` is also arguable -- the ALE emulates real 2600 hardware (T5) |
| Atari 100k | interactive (+fixed) | constructed | NOT a distinct source: an interaction BUDGET / game subset over the ALE. Part D sends it to algorithms R.eval; the admission rule has no clause for it (T4) |
| BIG-bench | fixed | elicited + constructed | tasks written BECAUSE the benchmark asked (elicited) and many of them programmatically instantiated (constructed); BBH is additionally a subset-by-difficulty, i.e. protocol (T4) |
| C4 | fixed | human-incidental | heuristically rule-filtered; the node is explicit that selection is not origination |
| Common Crawl | fixed (+oracle) | human-incidental |  |
| GLUE Benchmark | fixed | human-incidental + elicited | union over 9 tasks is near-meaningless at suite granularity (T6) |
| MMLU | fixed | human-incidental + elicited | exam questions scraped from existing practice material |
| WikiText-2 | fixed | human-incidental |  |
| Atari 57 | interactive (+fixed) | constructed | NOT a distinct source: an interaction BUDGET / game subset over the ALE. Part D sends it to algorithms R.eval; the admission rule has no clause for it (T4) |
| CARLA | interactive (+fixed) | simulated | rendered observations: `rendered` folded here |
| CartPole | interactive (+generator) | simulated ~ constructed (TIE) | classical control: physical units, no real referent. Same seam (T10) |
| CityLearn | interactive (+fixed) | simulated + natural | building-energy simulation driven by real weather files. If a given paper's instantiation uses real smart-METER traces the row gains a machine-emitted operational record and moves to `provenance-other` -- undecidable from the name (M1) |
| D4RL Benchmark | fixed ONLY | simulated + constructed + elicited + model-generated | alias |
| DeepMind Control Suite (DMC) | interactive (+fixed) | simulated | alias |
| EARL benchmark | interactive (+fixed) | simulated |  |
| Gibson Environment | interactive (+fixed) | natural + simulated | laser-scanned real buildings, then rendered: the node file names Habitat as this hard case and Gibson is the same shape (M5) |
| HalfCheetah-v2 | interactive (+fixed) | simulated ~ constructed (TIE) | sits on the boundary all three phase-1 runs flagged: it PASSES `simulated`'s positive test (engine with physical units) and PASSES `constructed`'s (the spec IS the ground truth -- 'the simulation is wrong' is not a meaningful complaint, there is no real referent). Resolved to `simulated` only because the node's examples list names MuJoCo rollouts (T10) |
| Hopper | interactive (+fixed) | simulated ~ constructed (TIE) | sits on the boundary all three phase-1 runs flagged: it PASSES `simulated`'s positive test (engine with physical units) and PASSES `constructed`'s (the spec IS the ground truth -- 'the simulation is wrong' is not a meaningful complaint, there is no real referent). Resolved to `simulated` only because the node's examples list names MuJoCo rollouts (T10) |
| Hopper-v2 | interactive (+fixed) | simulated ~ constructed (TIE) | sits on the boundary all three phase-1 runs flagged: it PASSES `simulated`'s positive test (engine with physical units) and PASSES `constructed`'s (the spec IS the ground truth -- 'the simulation is wrong' is not a meaningful complaint, there is no real referent). Resolved to `simulated` only because the node's examples list names MuJoCo rollouts (T10) |
| Hypergrid Environment | interactive | constructed | reward is an analytic function |
| MiniWoB | interactive | constructed | hand-built page templates |
| MountainCar | interactive (+generator) | simulated ~ constructed (TIE) | classical control: physical units, no real referent. Same seam (T10) |
| MS MARCO | fixed (+oracle) | human-incidental + elicited | Bing query log plus human-written answers: the channel case SYNTHESIS 3/3 names by name |
| MuJoCo Environments | -- | -- | REJECTED: admission rule, unnamed-description clause -- quote is "in both tabular and Mujoco environments" |
| Pendulum | interactive (+generator) | simulated ~ constructed (TIE) | classical control: physical units, no real referent. Same seam (T10) |
| Pendulum-v0 | interactive (+generator) | simulated ~ constructed (TIE) | classical control: physical units, no real referent. Same seam (T10) |
| Pile | fixed | human-incidental | alias of The Pile |
| StarCraft Multi-Agent Challenge (SMAC) | interactive (+fixed) | constructed | alias triple |
| SuperGLUE | fixed | human-incidental + elicited |  |
| 100k benchmark | interactive (+fixed) | constructed | NOT a distinct source: an interaction BUDGET / game subset over the ALE. Part D sends it to algorithms R.eval; the admission rule has no clause for it (T4) |
| 2D windy grid-world (Wet Chicken) | interactive | constructed | an abstract physical story with no units -- `constructed`, not `simulated` |
| 3D environments | -- | -- | REJECTED: admission rule, unnamed-description clause -- quote enumerates task classes: "grid worlds, continuous control, video games, and 3-D environments" |
| 5G Proprietary System-Level Network Simulator | interactive (+generator, +fixed) | simulated |  |
| Acrobot | interactive (+generator) | simulated ~ constructed (TIE) | classical control: physical units, no real referent. Same seam (T10) |
| Advanced Arithmetic Benchmark | fixed (+generator) | constructed ~ rule (TIE) | template-minted items whose answers are computed by arithmetic: the generating specification and the verifying rule are the SAME object, so the two node tests cannot separate them (M3) |
| AntMaze | interactive (+fixed) | simulated ~ constructed (TIE) | sits on the boundary all three phase-1 runs flagged: it PASSES `simulated`'s positive test (engine with physical units) and PASSES `constructed`'s (the spec IS the ground truth -- 'the simulation is wrong' is not a meaningful complaint, there is no real referent). Resolved to `simulated` only because the node's examples list names MuJoCo rollouts (T10) |
| Atari 2600 benchmark | interactive (+fixed) | constructed | alias; `benchmark`/`suite` is the R.eval half (Part D) |
| Atari 2600 Games | interactive (+fixed) | constructed | alias cluster round the ALE; `simulated` is also arguable -- the ALE emulates real 2600 hardware (T5) |
| Atari 2600 suite | interactive (+fixed) | constructed | alias; `benchmark`/`suite` is the R.eval half (Part D) |
| Atari Benchmark | interactive (+fixed) | constructed | alias; `benchmark`/`suite` is the R.eval half (Part D) |
| Atari Boxing | interactive | constructed | single game: member granularity, sitting in the same list as its suite (T6) |
| Atari Dataset from RL Unplugged | fixed ONLY | constructed + model-generated | frozen log of a LEARNING DQN agent stepping the ALE. `derived_from` -> ALE; the `model-generated` value comes from the transformation, not the parent (T7) |
| Atari DQN replay dataset | fixed ONLY | constructed + model-generated | frozen log of a LEARNING DQN agent stepping the ALE. `derived_from` -> ALE; the `model-generated` value comes from the transformation, not the parent (T7) |
| Atari Games | interactive (+fixed) | constructed | alias cluster round the ALE; `simulated` is also arguable -- the ALE emulates real 2600 hardware (T5) |
| Atari games dataset | -- | -- | REJECTED: admission rule, unnamed-description clause -- the quote does not even assert a dataset exists |
| Atari suite | interactive (+fixed) | constructed | alias; `benchmark`/`suite` is the R.eval half (Part D) |
| BBH | fixed | elicited + constructed | tasks written BECAUSE the benchmark asked (elicited) and many of them programmatically instantiated (constructed); BBH is additionally a subset-by-difficulty, i.e. protocol (T4) |
| BBH (BigBench Hard) | fixed | elicited + constructed | tasks written BECAUSE the benchmark asked (elicited) and many of them programmatically instantiated (constructed); BBH is additionally a subset-by-difficulty, i.e. protocol (T4) |
| BBQ Benchmark | fixed | elicited + constructed | hand-written templates instantiated by rule |
| Behavior Suite (BSuite) | interactive | constructed | synthetic probe environments |
| BIG-Bench (BB) | fixed | elicited + constructed | tasks written BECAUSE the benchmark asked (elicited) and many of them programmatically instantiated (constructed); BBH is additionally a subset-by-difficulty, i.e. protocol (T4) |
| BigBench Hard | fixed | elicited + constructed | tasks written BECAUSE the benchmark asked (elicited) and many of them programmatically instantiated (constructed); BBH is additionally a subset-by-difficulty, i.e. protocol (T4) |
| CALVIN | interactive (+fixed) | simulated + elicited | ships teleoperated human play + crowd language annotations |
| CAMELS suite | fixed | simulated | cosmological hydro runs |
| Canadian Urban Environmental Health Research Consortium (CANUE) | -- | -- | REJECTED: an institution / data provider, not a source of examples. NO CLAUSE IN PART A REJECTS THIS -- see T2 |
| CARLA Multi-Town dataset | fixed ONLY | simulated [+ rule | model-generated] | frozen log, derived_from CARLA. UNDECIDABLE: the "expert driver" is a hand-coded privileged autopilot (`rule`) or a trained policy (`model-generated`) and the name cannot say (T7, M3) |
| CARLA NoCrash benchmark | interactive | simulated | a route/weather/traffic PROTOCOL over CARLA, not a source (T4) |
| Chess games annotated by Stockfish | -- | -- | REJECTED: admission rule, unnamed-description clause + Part E entity-vs-mention: a derivation earns an entity only when NAMED as an artifact. See T8 -- this rejection deletes the clearest `rule` case in the set |
| Compositional Freebase Queries (CFQ) | fixed (+generator) | constructed + rule + human-incidental | questions minted by a grammar (constructed), answers computed by executing SPARQL against Freebase (rule), Freebase itself human-edited (human-incidental). Three channels, one row |
| Compositional Freebase Questions (CFQ) | fixed (+generator) | constructed + rule + human-incidental | alias -- "Queries" vs "Questions" for one artifact; must be written, never inferred |
| Continuous Mountain Car | interactive (+generator) | simulated ~ constructed (TIE) | classical control: physical units, no real referent. Same seam (T10) |
| CrossFit | fixed | human-incidental + elicited | a suite of 160 existing datasets: a suite-of-suites, union meaningless (T6) |
| DeepMind Control | interactive (+fixed) | simulated | alias |
| dm_control suite | interactive (+fixed) | simulated | alias -- the SOFTWARE name used for the task suite; the mirror image of the MuJoCo rejection (T1) |
| DMC - DeepMind Control Suite | interactive (+fixed) | simulated | alias |
| Duckietown | fixed (+interactive) | natural | KEYWORD IS WRONG: the quote is RGB images from a real Duckiebot camera, not a simulator. A physical measurement, not `simulated` |
| ER-Magellan benchmark datasets | fixed | human-incidental + elicited | product/bibliographic records + human match labels |
| ExtremeWeather | fixed | simulated [+ rule] | CAM5 climate output with labels from a threshold-based detection toolkit. The `rule` half is undecidable from the name (M3) |
| Fast Folding Proteins Benchmark | fixed | simulated | long MD trajectories |
| FDA-approved UVA/Padova Type1 Diabetes Mellitus Simulator | interactive (+generator) | simulated | validated against real patients, so 'the simulation is wrong' is meaningful: a clean `simulated`, unlike the MuJoCo seam |
| fixed-boundary mapping benchmark | -- | -- | REJECTED: admission rule, unnamed-description clause -- "the benchmark data set in [Du et al. 2020]"; the name is the extractor's paraphrase |
| Flatland | interactive | simulated ~ constructed (TIE) | railway scheduling: real referent, grid dynamics, no units. Same seam (T10) |
| Four Rooms environment | interactive | constructed |  |
| free-boundary mapping benchmark | -- | -- | REJECTED: admission rule, unnamed-description clause -- "the benchmark data set of [Du et al. 2021]" |
| Gene Regulatory Network Simulation Data from SERGIO | fixed (+generator) | simulated |  |
| Generated Datasets from DeepMind Control Suite | -- | -- | REJECTED: admission rule, unnamed-description clause -- released but unnamed; see T9 |
| German Common Crawl | fixed | human-incidental | UNDECIDABLE: a named released corpus, or a language subset of Common Crawl (and therefore not an entity at all, Part C)? (T3) |
| German Traffic Sign Recognition Benchmark (GTSRB) | fixed | human-incidental + elicited | STRAINED (M2): video frames of real traffic signs. The signal is a camera measurement, but `natural`'s negative test excludes it because the subject is a human artifact, so it lands on `human-incidental` -- the same strain as IMDB-Wiki, on a far larger class of vision datasets |
| GhostRun environment (Jiang, 2019) | interactive | constructed |  |
| GLUE | fixed | human-incidental + elicited | alias |
| Grid Environment Dataset | -- | -- | REJECTED: admission rule, unnamed-description clause -- "a modified version of the grid environment from (Bengio et al., 2021)" |
| Grid World Dataset | -- | -- | REJECTED: admission rule, unnamed-description clause -- "images generated by a Grid World environment" |
| Grid-world Environments | -- | -- | REJECTED: admission rule, unnamed-description clause -- "four different grid-world environments" |
| Gym MuJoCo Benchmark | interactive (+fixed) | simulated ~ constructed (TIE) | suite name for the locomotion tasks; same seam |
| Habitat Pick (HabPick) | interactive (+fixed) | natural + simulated | the node file's own recurring hard case, now with a name attached (M5) |
| HalfCheetah-v3 | interactive (+fixed) | simulated ~ constructed (TIE) | sits on the boundary all three phase-1 runs flagged: it PASSES `simulated`'s positive test (engine with physical units) and PASSES `constructed`'s (the spec IS the ground truth -- 'the simulation is wrong' is not a meaningful complaint, there is no real referent). Resolved to `simulated` only because the node's examples list names MuJoCo rollouts (T10) |
| HalOmi benchmark dataset | fixed | human-incidental + model-generated + elicited | source sentences (incidental), MT system outputs being judged (model-generated), human hallucination labels (elicited). The only clean `model-generated` use in the set |
| Hanabi | interactive (+generator) | constructed [+ rule] | `rule` is what the rule node's OWN examples claim (terminal outcomes from the rules of a game) while A and C route them to `constructed`. Unresolvable fork, not a tie I may break (T11) |
| HELM | fixed | human-incidental + elicited | HELM is overwhelmingly a PROTOCOL over other people's scenarios. Part D assigns that half to algorithms R.eval, and nothing in the admission rule rejects it here (T4) |
| Hopper Controller | fixed | constructed + simulated | Design-Bench task: INPUTS are 3,200 sampled weight vectors (constructed), TARGETS are MuJoCo returns (simulated). The channel problem (SYNTHESIS 3/3) in one row |
| hopper_stand | interactive (+fixed) | simulated ~ constructed (TIE) | sits on the boundary all three phase-1 runs flagged: it PASSES `simulated`'s positive test (engine with physical units) and PASSES `constructed`'s (the spec IS the ground truth -- 'the simulation is wrong' is not a meaningful complaint, there is no real referent). Resolved to `simulated` only because the node's examples list names MuJoCo rollouts (T10) |
| Humanoid | interactive (+fixed) | simulated ~ constructed (TIE) | sits on the boundary all three phase-1 runs flagged: it PASSES `simulated`'s positive test (engine with physical units) and PASSES `constructed`'s (the spec IS the ground truth -- 'the simulation is wrong' is not a meaningful complaint, there is no real referent). Resolved to `simulated` only because the node's examples list names MuJoCo rollouts (T10) |
| Humanoid-v2 | interactive (+fixed) | simulated ~ constructed (TIE) | sits on the boundary all three phase-1 runs flagged: it PASSES `simulated`'s positive test (engine with physical units) and PASSES `constructed`'s (the spec IS the ground truth -- 'the simulation is wrong' is not a meaningful complaint, there is no real referent). Resolved to `simulated` only because the node's examples list names MuJoCo rollouts (T10) |
| IMDB-Wiki Dataset | fixed | human-incidental | STRAINED (M2): the signal is photographs -- camera measurements -- and `natural`'s negative test kicks them out because the subject is a human artifact, so `human-incidental` claims them on the strength of the SUBJECT rather than the signal |
| IndicXTREME | fixed | elicited + human-incidental |  |
| Juliet Test Suite | fixed | constructed + elicited + rule | NIST: human-authored flaw templates (elicited) instantiated by a generator (constructed) with labels guaranteed by the generator and checkable by a stated rule (rule). The strongest non-game `rule` case (M3) |
| Kuhn Poker | interactive (+generator) | constructed [+ rule] | `rule` is what the rule node's OWN examples claim (terminal outcomes from the rules of a game) while A and C route them to `constructed`. Unresolvable fork, not a tie I may break (T11) |
| Leduc Poker | interactive (+generator) | constructed [+ rule] | `rule` is what the rule node's OWN examples claim (terminal outcomes from the rules of a game) while A and C route them to `constructed`. Unresolvable fork, not a tie I may break (T11) |
| Long Range Arena (LRA) | fixed | constructed + human-incidental + elicited | ListOps and Pathfinder are constructed, text is scraped, the image task is labelled photographs: one row, three origins (T6) |
| Long Range Graph Benchmark (LRGB) | fixed | natural + simulated + human-incidental + elicited | peptides from the PDB (natural), PCQM4M DFT targets (simulated), image superpixels (human-incidental + elicited) |
| Lunar Lander Game Data | fixed | constructed [+ rule | model-generated] | "simulated user commands": a scripted user is `rule`, a learned one is `model-generated`. Undecidable from the name (M3) |
| Mandl benchmark | fixed | human-incidental | STRAINED (M2): a real Swiss transit network hand-transcribed to a 15-node graph. The content is infrastructure measurement, not human artifact-as-signal, and no value covers 'a real system transcribed by hand' |
| MatSci-NLP Benchmark | fixed | human-incidental + elicited |  |
| MeltingPot | interactive | constructed |  |
| Meta-World ML45 | interactive (+fixed) | simulated | a task SPLIT, i.e. protocol (T4) |
| MetaWorld environments | interactive (+fixed) | simulated | alias |
| MetaWorld MT10 | interactive (+fixed) | simulated | a task SPLIT, i.e. protocol (T4) |
| MiniGrid benchmark | interactive (+fixed) | constructed | alias |
| MiniGrid Dynamic Obstacles | interactive | constructed | member granularity (T6) |
| MiniGridLoCA | interactive | constructed |  |
| MMLU benchmark | fixed | human-incidental + elicited | alias |
| Molecule synthesis environment | -- | -- | REJECTED: admission rule, unnamed-description clause -- "a large-scale, a molecular synthesis environment" |
| MountainCarLoCA | interactive (+generator) | simulated ~ constructed (TIE) | classical control: physical units, no real referent. Same seam (T10) |
| MsPacman Atari 2600 | interactive | constructed | single game: member granularity (T6) |
| MuJoCo locomotion benchmark environments | interactive (+fixed) | simulated ~ constructed (TIE) | borderline unnamed; admitted as a suite alias |
| MuJoCo Reacher | interactive (+fixed) | simulated ~ constructed (TIE) | sits on the boundary all three phase-1 runs flagged: it PASSES `simulated`'s positive test (engine with physical units) and PASSES `constructed`'s (the spec IS the ground truth -- 'the simulation is wrong' is not a meaningful complaint, there is no real referent). Resolved to `simulated` only because the node's examples list names MuJoCo rollouts (T10) |
| Mujoco-based environments | -- | -- | REJECTED: admission rule, unnamed-description clause -- quote is "Mujoco-based and MetaWorld environments" |
| Multi-Agent MuJoCo (MAMuJoCo) Datasets | fixed ONLY | simulated + model-generated | frozen log; `derived_from` -> MAMuJoCo. T7 |
| Multi-Agent Particle environment (Mordatch & Abbeel, 2017) | interactive | simulated ~ constructed (TIE) | point-mass dynamics: four spellings of one source; same seam (T10) |
| Multi-Agent Particle Environment (MPE) | interactive | simulated ~ constructed (TIE) | point-mass dynamics: four spellings of one source; same seam (T10) |
| Multi-Agent Particle Environments | interactive | simulated ~ constructed (TIE) | point-mass dynamics: four spellings of one source; same seam (T10) |
| Multi-agent Particle Environments (MPE) | interactive | simulated ~ constructed (TIE) | point-mass dynamics: four spellings of one source; same seam (T10) |
| MultiSensory Embodied 3D-Scene Environment | interactive | natural + simulated | multisensory scenes from scanned real objects plus simulated contact/audio |
| Mumford benchmark | fixed | human-incidental | STRAINED, same shape as Mandl (M2) |
| NetHack Learning Environment (NLE) | interactive | constructed |  |
| Neural Latents Benchmark | fixed | natural | VALUE NO NODE SUPPLIES (T15): macaque motor-cortex recordings during a trained reaching task. `elicited`'s characteristic holds in every respect except species -- its test says 'a person produced it to order'. Animal-elicited behaviour has no value, and `natural` only covers the recording half |
| Neuronal Network Simulation Data from NEST | fixed (+generator) | simulated |  |
| NeuroTouch FEM simulation dataset | fixed | simulated |  |
| Offline Ant Maze | fixed ONLY | simulated ~ constructed (TIE) + model-generated | borderline unnamed ("we collect new offline datasets"); if admitted it is derived_from AntMaze (T7, T9) |
| One Billion Word Benchmark (LM1B) | fixed | human-incidental | news crawl |
| OpenML-CC18 | fixed (+oracle) | natural + human-incidental + elicited + constructed | `oracle` is a real second reading: the suite is fetched by task id from a server. Provenance union is the whole axis (T6) |
| OpenML-CTR23 | fixed (+oracle) | natural + human-incidental + elicited + constructed | as CC18 |
| PII Benchmark | fixed | human-incidental + elicited | 400 code files (incidental) + per-item annotation (elicited) |
| Poker Hand | fixed | constructed ~ rule (TIE) | hand rank computed by the rules of poker: `constructed` and `rule` are the same object here. The paper calls it a "data stream" and the correct access is still `fixed` (M4) |
| PowerGridworld | interactive | simulated + constructed | power-flow physics (units) inside a gridworld shell |
| Procgen | interactive (+generator) | constructed | both access values are legitimate and the choice is not resolvable from the name; unbounded supply has nowhere to be recorded (SYNTHESIS 2/3) |
| Procgen Benchmark | interactive (+generator) | constructed | both access values are legitimate and the choice is not resolvable from the name; unbounded supply has nowhere to be recorded (SYNTHESIS 2/3) |
| ProcGen CoinRun | interactive (+generator) | constructed | member granularity (T6) |
| Procgen-Maze | interactive (+generator) | constructed | member granularity (T6) |
| Proprietary System Level RAN Simulator Dataset | fixed ONLY | simulated | derived_from a simulator that is itself proprietary and UNNAMED -- `derived_from` has no parent node to point at (T7) |
| ProteinGym benchmark | fixed | natural + constructed | 217 wet-lab DMS assays over a designed mutant library: measurement of a biological process whose INPUTS are specified |
| PubMed Central | fixed (+oracle) | human-incidental | the OA bulk dump is `fixed`; the API is `oracle` |
| PyBullet | -- | -- | REJECTED: admission rule, software-that-implements clause -- a physics engine. See T1 |
| RB benchmark | generator (+fixed) | constructed | `generator` as typical, which almost nothing else in this set earns: instances are minted at a requested size |
| Real-World Reinforcement Learning Benchmark (RWRL) | interactive | simulated | the name says "real-world"; the source is a simulator. A naming trap for any coder |
| Real-World RL benchmark | interactive | simulated | alias |
| Reddit FL benchmark dataset | fixed | human-incidental | the NAME says federated and the access is `fixed`: positive confirmation of the unanimous decision to keep `federated` off this axis, and of the mis-coding risk |
| RL Unplugged Atari Dataset | fixed ONLY | constructed + model-generated | frozen log of a LEARNING DQN agent stepping the ALE. `derived_from` -> ALE; the `model-generated` value comes from the transformation, not the parent (T7) |
| SAGE Benchmark | interactive (+fixed) | constructed + elicited | UNDECIDABLE from the name: if the 50 smart-home tasks run against REAL devices the signal is machine-emitted telemetry and the row moves to `provenance-other` (M1) |
| Semantic Textual Similarity Benchmark (STS-B) | fixed | human-incidental + elicited | scraped sentence pairs + crowd scores |
| Sequential Arcade Learning Environment | interactive | constructed | a task-ORDERING protocol over the ALE, not a source (T4) |
| Simulation Datasets of RAN | -- | -- | REJECTED: admission rule, unnamed-description clause -- quote is "a system-level RAN simulator[36,37] consisting of seven eNBs" |
| Sitnikov Problem Simulation Dataset | fixed (+generator) | simulated ~ constructed (TIE) | an IDEALISED restricted three-body problem: physical units, no physical system it is a model OF. The seam at its sharpest (T10, M5) |
| Squirrel’s World Environment (SW) | interactive | constructed |  |
| StarCraft II Multi-Agent Challenge | interactive (+fixed) | constructed | alias triple |
| StarCraft Multi-Agent Challenge | interactive (+fixed) | constructed | alias triple |
| SubpopBench suite | fixed | human-incidental + elicited + constructed | Waterbirds is real photographs COMPOSITED to a specification -- `constructed` applied to a transformation over natural content |
| Subset of English Wikipedia | -- | -- | REJECTED: Part C: a subset or split is NOT a derivation -- same node as Wikipedia, with size on the mention. Not Part A. See T3 |
| Super-Natural Instructions | fixed | elicited + human-incidental | contributor-written instructions over existing task data |
| Super-Natural Instructions (SuperNI) | fixed | elicited + human-incidental | alias |
| T0 task suite | fixed | elicited + human-incidental | prompt templates written to order over existing datasets |
| TextWorld | interactive | constructed | text games from a grammar |
| tkgl-wikidata | fixed | human-incidental | temporal KG extracted from Wikidata; human-edited |
| TNMIX benchmark | fixed | natural + elicited | CONTRADICTORY TESTS (T14): clinical ultrasound images. `human-incidental`'s positive test PASSES (the scans would exist unchanged without the dataset); `natural`'s positive test FAILS (remove human purpose and no scan is taken) while its characteristic -- instrument measurement of a biological process -- plainly HOLDS. The node files place clinical imaging both ways: fastMRI under `natural`, MIMIC under `human-incidental` |
| Toy Arithmetic Benchmark | fixed (+generator) | constructed ~ rule (TIE) | same tie; and the name may be the extractor's paraphrase of "a synthetic benchmark" rather than an artifact name |
| Tuning MEG simulation dataset | fixed | simulated |  |
| Two Rooms Dynamic Obstacles Environment (2RDO) | interactive | constructed |  |
| Unsupervised Reinforcement Learning Benchmark (URLB) | interactive | simulated | three spellings of one DMC-based suite; aliases must be WRITTEN, not inferred |
| Unsupervised RL Benchmark (URLB) | interactive | simulated | three spellings of one DMC-based suite; aliases must be WRITTEN, not inferred |
| URL Benchmark | interactive | simulated | three spellings of one DMC-based suite; aliases must be WRITTEN, not inferred |
| Visual Task Adaptation Benchmark (VTAB) | fixed | natural + human-incidental + elicited + constructed + simulated | the maximal union in the set: 5 of 6 non-model provenance values on one row. If a suite gets one row its provenance is noise (T6) |
| Walker2d-v2 | interactive (+fixed) | simulated ~ constructed (TIE) | sits on the boundary all three phase-1 runs flagged: it PASSES `simulated`'s positive test (engine with physical units) and PASSES `constructed`'s (the spec IS the ground truth -- 'the simulation is wrong' is not a meaningful complaint, there is no real referent). Resolved to `simulated` only because the node's examples list names MuJoCo rollouts (T10) |
| WebArena | interactive | constructed + human-incidental | self-hosted functional replicas of real sites: the software is constructed, the content is scraped human artifact |
| widely used activity recognition benchmark datasets | -- | -- | REJECTED: admission rule, unnamed-description clause -- the name is the description |
| Wikipedia dataset | fixed (+oracle) | human-incidental | alias |
| Wikipedia-based Image Text | fixed | human-incidental |  |
| XTREME-UP | fixed | elicited + human-incidental |  |
---

## 2. Rejections — 19 names, each with the clause

### 2.1 The software that implements a source (3)

- **`MuJoCo`** (10 papers, the single most-cited name in the set) — the physics
  engine, named in Part A as the type case. Rejected.
- **`PyBullet`** — a physics engine. Rejected by the same clause.
- **`OpenAI Gym`** (4 papers) — an environment-interface library.

### 2.2 Unnamed descriptions (13)

`3D environments` · `Simulation Datasets of RAN` ·
`widely used activity recognition benchmark datasets` · `MuJoCo Environments` ·
`Mujoco-based environments` · `Grid-world Environments` ·
`Grid Environment Dataset` · `Grid World Dataset` ·
`Molecule synthesis environment` · `fixed-boundary mapping benchmark` ·
`free-boundary mapping benchmark` · `Atari games dataset` ·
`Generated Datasets from DeepMind Control Suite`.

Each quote confirms it. `3D environments` is a clause in an enumeration of task
classes; `Simulation Datasets of RAN` is "a system-level RAN simulator … consisting
of seven eNBs"; `Atari games dataset`'s quote does not assert a dataset at all;
the two mapping benchmarks are the extractor's paraphrase of "the benchmark data
set in [Du et al. 2020]".

### 2.3 Named as a derivation, not as an artifact (1)

- **`Chess games annotated by Stockfish`** — Part E: *a derivation earns an entity
  when it is named as an artifact, not whenever it happens.* The quote is "the
  distillation dataset comprises 10 million chess games annotated by the Stockfish
  engine". No name, so no entity. **See T8 — this rejection deletes the single
  clearest `rule` case in the whole set.**

### 2.4 Rejected with no clause to do it (2)

- **`Canadian Urban Environmental Health Research Consortium (CANUE)`** — an
  institution. The header comment of the candidate file already says so. But
  **Part A has no clause that rejects a data provider**: its three exclusions are
  unnamed descriptions, implementing software, and (now withdrawn)
  other-dimension entities. CANUE is a named artifact of a sort, is not software,
  and is not another dimension's entity. I rejected it on the admission rule's
  *definition* ("a named source of the examples a run consumes" — a consortium is
  not) rather than on a clause. **T2.**
- **`Subset of English Wikipedia`** — rejected by **Part C**, not Part A: *a subset
  or split is not a derivation; same node, with size on the run's reference.* This
  is the only name in the set rejected by a rule outside the admission rule, and
  it is worth noting that step 4's framing ("apply the admission rule") would have
  admitted it. **T3.**

---

## 3. Tensions

### T1 — the library/source split is right and the corpus does not cooperate

`MuJoCo` is rejected as a library, and that rejection removes **the most-cited
name in the candidate set** (10 papers). Its quote — comparing PPO, DeepMDP,
PlaNet and Dreamer — does not say whether the paper stepped the engine directly
or used the gym locomotion tasks. The name is **undecidable from the name alone
and needs the paper**, which is exactly what the one-string-two-entities
resolution requires and exactly what a name-level placement cannot do.

The mirror case is sharper: **`dm_control suite`** is a *software package name*
used, in its own quote, for the task suite ("the Stickman environment is based on
the Walker environment from the dm_control suite"). By the letter of the clause
`dm_control` is a library and should be rejected; by its quote it denotes the
same source as `DeepMind Control Suite`. I admitted it as an alias. So the clause
rejects `MuJoCo` and admits `dm_control`, and the only thing separating them is
which string the field happens to use for the suite. **The clause is correct and
its application is a naming accident.**

`PyBullet`'s quote — "offline data collected from classical PyBullet
environments" — has the same shape: the engine's name standing in for its
environments.

### T2 — an institution has no rejecting clause

See §2.4. `CANUE` is a data provider whose quote describes an actual data product
("The CANUE data contain indicators for unemployment, social deprivation, access
to health services"). Those indicators are **computed aggregates over
administrative records** — run A's `institutional_record` sub-case, which the
fold of 2026-10-08 sends to `human-incidental`, and whose computation step is
arguably `rule`. The rejection therefore hides the purest
byproduct-of-operation case in the set from the very measurement
`provenance-other` was made the instrument for. **I recommend a fourth exclusion
clause naming data providers/repositories explicitly** — not because the
rejection is wrong, but because it is currently made on the definition rather
than on a clause, and because a coder will meet dozens of these.

### T3 — `Subset of English Wikipedia` and `German Common Crawl`: subset or entity?

Part C settles the first (a subset is not a derivation). It cannot settle the
second: **`German Common Crawl`** is either a released named corpus or a language
slice of Common Crawl, and the quote ("We select the German Common Crawl for a
stronger distribution shift") is consistent with both. **Undecidable from the
name; needs the paper.** This is a general hazard for every `<language> <corpus>`
name, and nothing on either axis records the difference — it is an
entity-existence question, upstream of both.

### T4 — 14 names are evaluation protocols, not sources, and nothing rejects them

`Atari 100k` · `Atari 100k benchmark` · `100k benchmark` · `Atari 57` ·
`Sequential Arcade Learning Environment` · `CARLA NoCrash benchmark` ·
`Meta-World ML45` · `MetaWorld MT10` · `BBH` (×3 spellings) ·
`BIG-bench`/`BIG-Bench (BB)` (as the harness) · `HELM`.

Each is a *budget*, a *game/task subset*, a *task ordering*, or a *scoring
harness* laid over a source that is separately named in the same list. Part D
assigns that half to algorithms `R.eval` — but **the admission rule has no clause
that rejects a protocol**, so a coder following step 4's instruction admits all
14. `Atari 100k`'s own quote is about interaction budget ("evaluates agents using
only 100,000 agent interactions"), i.e. a number, not a source. `HELM` is the
extreme: almost entirely protocol over other people's scenarios.

I admitted them with the flag rather than rejecting them, because rejecting on a
clause that does not exist is the error METHOD.md warns about. **This is a gap in
the admission rule, not in the axes.**

### T5 — the ALE: 21 names, one source, and an emulator reading nobody chose

`Arcade Learning Environment` · `Arcade Learning Environment (ALE)` ·
`Atari 2600` · `Atari` · `Atari Games` · `Atari 2600 Games` · `Atari suite` ·
`Atari 2600 suite` · `Atari Benchmark` · `Atari 2600 benchmark` · `Atari 57` ·
`Atari 100k` · `Atari 100k benchmark` · `100k benchmark` ·
`Sequential Arcade Learning Environment` · `Atari Boxing` ·
`MsPacman Atari 2600` · `Atari DQN replay dataset` ·
`Atari Dataset from RL Unplugged` · `RL Unplugged Atari Dataset` ·
(+ rejected `Atari games dataset`).

**21 of 194 names — 11% of the candidate set — denote one source, its two
protocol variants, two of its member games and three frozen logs of it.** Aliases
must be *written, never inferred* (METHOD.md §4), so this is 21 alias decisions
a human has to make, and three of them (`Atari 57`, `Atari 100k`, `Sequential
ALE`) are *not* aliases but protocols.

On provenance I placed the cluster `constructed`, following A's and C's routing of
game outcomes. But **the ALE is an emulator of real 2600 hardware**, so
`simulated`'s characteristic ("a mechanistic model of a real referent, executed")
holds of it — "the emulation is wrong" is a meaningful complaint about an
emulator. Its positive test fails only on "parameters have physical units". The
tie survives; I record it rather than break it.

### T6 — suite granularity: `access` is stable, `provenance` is noise

A's 1/3 finding, confirmed hard. The suite rows and their member rows are **both
in this candidate set**, which is the measurement A predicted:

| suite row | member rows in the same file |
|---|---|
| `Arcade Learning Environment` | `Atari Boxing`, `MsPacman Atari 2600` |
| `MiniGrid` | `MiniGrid Dynamic Obstacles`, `MiniGridLoCA` |
| `Procgen` | `ProcGen CoinRun`, `Procgen-Maze` |
| `DeepMind Control Suite` | `hopper_stand` |
| `Meta-World` | `Meta-World ML45`, `MetaWorld MT10` |
| `Gym MuJoCo Benchmark` | `HalfCheetah-v2/-v3`, `Hopper`, `Hopper-v2`, `Walker2d-v2`, `Humanoid`, `Humanoid-v2`, `MuJoCo Reacher` |

In every case `access` is identical for suite and member and `provenance` is
either identical (Procgen, MiniGrid) or an uninformative union (the next table).

The unions, measured:

| name | provenance values | why the union is noise |
|---|---|---|
| `Visual Task Adaptation Benchmark (VTAB)` | natural + human-incidental + elicited + constructed + simulated | **5 of the 6 non-model values on one row** |
| `OpenML-CC18`, `OpenML-CTR23` | natural + human-incidental + elicited + constructed | 72 / 35 unrelated tabular datasets |
| `D4RL` | simulated + constructed + elicited + model-generated | SAC-policy locomotion, AntMaze, Adroit human demos |
| `Long Range Graph Benchmark (LRGB)` | natural + simulated + human-incidental + elicited | PDB peptides, DFT targets, image superpixels |
| `Long Range Arena (LRA)` | constructed + human-incidental + elicited | ListOps, scraped text, labelled photographs |
| `CrossFit` | human-incidental + elicited | a suite of **160** existing datasets |

**A's "granularity should be decided per axis, not per dimension" is the single
design idea this placement run most strongly supports.** A suite-level row can
carry a correct `access` and cannot carry a meaningful `provenance`.

### T7 — `derived_from` carrying what the axes cannot: 8 names

| name | parent | value the transformation itself introduces |
|---|---|---|
| `Atari DQN replay dataset` | ALE | `model-generated` — logged from a *learning* DQN |
| `Atari Dataset from RL Unplugged` | ALE | `model-generated` — "100M environment steps of training a DQN agent" |
| `RL Unplugged Atari Dataset` | ALE | as above (alias) |
| `D4RL` | MuJoCo tasks / Adroit | `model-generated` (trained SAC) + `elicited` (human demos) |
| `Multi-Agent MuJoCo (MAMuJoCo) Datasets` | MAMuJoCo | `model-generated` |
| `Offline Ant Maze` | AntMaze | `model-generated` |
| `CARLA Multi-Town dataset` | CARLA | `rule` **or** `model-generated` — see below |
| `Proprietary System Level RAN Simulator Dataset` | an unnamed proprietary simulator | none |

Two things the axes cannot do alone:

1. **`access` would be wrong without the relation.** All 8 are `fixed ONLY`.
   Nothing on the `access` axis says that a `fixed` row's parent was
   `interactive` — only `derived_from` does, and SYNTHESIS §4's rule ("a run that
   trains on a frozen buffer reports `fixed`, **never** `interactive`") is
   precisely what makes the relation load-bearing rather than decorative. The
   axis would otherwise report these 8 papers as having done no interactive work
   at all, which is true of the *run* and false of the *lineage*.
2. **The last row breaks the relation.** `Proprietary System Level RAN Simulator
   Dataset` is derived from a simulator that is proprietary and **unnamed** — so
   `derived_from` has no node to point at. The inheritance rule ("carries its
   parents' values") cannot fire with no parent; I had to assign `simulated`
   directly, from the name. The admission rule's named-only clause and
   `derived_from` are in tension here, and the same will hold for every private
   simulator.

### T8 — the rejection that deletes the measurement

`Chess games annotated by Stockfish` is correctly rejected (unnamed derivation).
It is also:

- the clearest **`rule`** case in the 194 (Stockfish's search + hand-written
  evaluation is a stated non-learned engine; a person could check the signal), or
- a clean **`model-generated`** case if the Stockfish version is NNUE —
  **undecidable from the name**, and the name is the only thing the rejection
  leaves.

So the single name that would have given `rule` its least contestable support is
removed by a different rule. Noted as evidence about the *interaction* of the two
rules, not as an argument against either.

### T9 — a released artifact with no name

`Generated Datasets from DeepMind Control Suite` is rejected as an unnamed
description, yet its quote says "our learning code, generated datasets, and
custom continuous control environments … are publicly available at [URL]". The
artifact **exists and is published**; it simply was not given a name. Part E's
criterion ("a derivation earns an entity when it is **named** as an artifact") is
what rejects it, and here that criterion rejects a real, citable, reusable
artifact. `Offline Ant Maze` ("we collect new offline datasets that precisely test
for stitching") is the same shape and I admitted it only because the name reads
as a title. **The two are decided differently by nothing but capitalisation.**

### T10 — contradictory positive/negative tests: the `simulated ~ constructed` seam

**The headline finding.** For 26 names, applying the two nodes' tests gives
contradictory answers:

- `simulated` **positive** test passes: "there is a solver or engine whose
  parameters have physical units" — MuJoCo has mass, torque, gravity, timestep.
- `simulated` **positive** test's second half fails: "'the simulation is wrong' is
  a meaningful complaint about the output" — **it is not.** There is no real
  half-cheetah. Nobody has ever complained that HalfCheetah is an inaccurate
  model of anything.
- `constructed` **positive** test passes: "the generating specification IS the
  ground truth; there is no measurement or approximation error to speak of" —
  true of HalfCheetah.
- `constructed` **negative** test passes too: "fails when a real phenomenon is
  being approximated" — no real phenomenon is being approximated.

So `simulated`'s positive test is internally split and `constructed`'s both tests
are satisfied. The 26: `HalfCheetah-v2` `HalfCheetah-v3` `Hopper` `Hopper-v2`
`Walker2d-v2` `Humanoid` `Humanoid-v2` `MuJoCo Reacher` `AntMaze` `hopper_stand`
`Gym MuJoCo Benchmark` `MuJoCo locomotion benchmark environments`
`Offline Ant Maze` `CartPole` `MountainCar` `Continuous Mountain Car` `Pendulum`
`Pendulum-v0` `Acrobot` `MountainCarLoCA` `Flatland`
`Multi-Agent Particle environment (Mordatch & Abbeel, 2017)` (+3 spellings)
`Sitnikov Problem Simulation Dataset`.

**I resolved them to `simulated` only because the node's `examples` column names
"MuJoCo rollouts".** That is resolution by authority, not by test — and it means
the examples column is currently doing work the tests cannot do, for 15% of this
candidate set.

The contrast case proves the seam is real rather than a wording slip:
**`FDA-approved UVA/Padova Type1 Diabetes Mellitus Simulator`** is a clean
`simulated` — it is a validated model of human glucose metabolism and "the
simulation is wrong" is not only meaningful but regulated. **`Sitnikov Problem
Simulation Dataset`** is the sharpest ambiguity: a restricted-three-body
idealisation with physical units and no physical system it is a model *of*.

The fix shape run A offered and the synthesis folded — one `program-computed`
value plus a separate `referent` axis — **is exactly what these 26 names want**,
because what distinguishes them from the UVA/Padova simulator is the *referent*,
not the computation. I am not proposing it (one axis is out of scope), but the
26-name count is the evidence for it.

### T11 — `rule` vs `constructed` on game outcomes: an unresolvable fork, not a tie

`Kuhn Poker` · `Leduc Poker` · `Hanabi` (and, under the same argument, the entire
20-name ALE cluster and `NetHack`, `StarCraft`, `MeltingPot`, `TextWorld`).

- The **`rule` node's own examples** list "terminal outcomes from the rules of Go
  or chess". By that, every game environment's reward channel is `rule`.
- **A and C both route game outcomes to `constructed`**, and the synthesis records
  that.

The node file therefore contains both answers. The consequence is binary and
large: on the rule-node reading, `rule` picks up **~55 names** in this set and
becomes one of the largest values; on the A/C reading it picks up **0** of them.
I recorded `constructed [+ rule]` for the three card games and `constructed` for
the rest, and I am **not** breaking it. What makes it a fork rather than a tie is
that it is the **reward channel** that is `rule` while the observation channel is
`constructed` — so this is SYNTHESIS §3's channel problem (2/3, "RL reward
provenance is invisible") appearing as an apparent value-boundary dispute. **The
boundary dispute dissolves if provenance is scoped to a channel and is
unresolvable if it is not.**

### T12 — `fixed` has no way to say "frozen when?"

`Wikipedia` · `Wikipedia dataset` · `Common Crawl` · `German Common Crawl` ·
`PubMed` · `PubMed Central` · `tkgl-wikidata`.

C's 1/3 temporal-stability point, confirmed. `fixed`'s positive test — "every
example could be enumerated before the run starts, knowing nothing about the
consumer; re-running yields the same set" — is **false** of a Wikipedia dump
taken next month and **true** of a given dump. The name denotes the rolling
source; only the mention could denote the snapshot, and `access` has nothing but
the value. Nothing on either axis is wrong; the information has nowhere to go.

### T13 — `access` undecidable from the name: 4 named cases

- **`PubMed`** — typical access is genuinely `oracle` (E-utilities, queried by
  identifier, no state across requests). But the row's quote is about node
  embeddings and pairwise Euclidean distances and says nothing about supply. The
  keyword bucket says `reference`; I cannot tell whether the paper downloaded a
  dump (`fixed`) or queried the API (`oracle`).
- **`ExtremeWeather`** — `simulated` is certain; whether the event labels are
  threshold-detector output (`rule`) or expert annotation (`elicited`) is not
  stated by the name.
- **`CityLearn`** — `simulated` + `natural` (real weather files); whether a given
  instantiation uses real smart-meter traces (which would add a machine-emitted
  record and move the row to `provenance-other`) is not in the name.
- **`Lunar Lander Game Data`** — "simulated user commands": scripted (`rule`) or
  learned (`model-generated`).

Plus `CARLA Multi-Town dataset` (T7) and `MuJoCo` (T1). **6 names where the paper
is required and the name is insufficient** — and note that this is the *lower*
bound, because every `interactive (+fixed)` row is formally undecidable on
`access` until the mention is read; that is by design and is not counted here.

### T14 — clinical imaging: the node files place it on both sides

**`TNMIX benchmark`** — 4554 + 637 thyroid-nodule ultrasound images from two
clinical datasets, plus segmentation masks.

- `human-incidental` **positive** test passes: "the content would exist,
  unchanged, if this dataset had never been conceived" — the scans were taken for
  patient care.
- `natural` **positive** test fails: "remove every human purpose and the process
  still runs" — remove the clinician and no scan exists.
- `natural`'s **characteristic** nevertheless holds exactly: "the signal issues
  from a physical or biological process … an instrument stands between it and the
  record." An ultrasound of a thyroid is an instrument measurement of a
  biological process.

**And the node files themselves answer this both ways**: `natural`'s examples list
`fastMRI raw k-space` — clinical knee MRI — while `human-incidental`'s examples
list `MIMIC-III/IV clinical records`. Two clinical byproducts, two different
values, in the frozen axis, with no stated criterion separating them. I placed
TNMIX as `natural + elicited` on the characteristic and record the contradiction.

I read this as the **first real cost of the 2026-10-08 fold**: `human-incidental`
now has to absorb clinical records, and the moment the clinical record is an
*image* rather than a *note*, it collides with `natural`. The watch flag should
say "clinical imaging", not just "clinical records".

### T15 — a value no node supplies: animal-elicited signal

**`Neural Latents Benchmark`** — macaque motor-cortex population recordings
during trained reaching tasks (MC-Maze, MC-RTT; the quote names "new animals
performing novel tasks with different equipment").

- `natural` covers the **recording**: a biological process measured by an
  instrument.
- `elicited`'s characteristic — "the signal exists because the collection asked
  for it … there is a task description, protocol, prompt or payment that caused
  each item to be produced; remove the research request and the signal does not
  exist" — **holds in every respect except one**: its positive test and node name
  both say *people*. A macaque trained on a manipulandum is not a person acting
  for its own purposes (`human-incidental` fails) and the reach is not a process
  that would run regardless of intent to record (`natural`'s positive test fails
  for the behavioural half).

I placed `natural` and record the gap. This is the one place in the 194 where I
would **propose adding** a value, or minimally rewording `elicited` from "people"
to "a person or animal, to the collection's protocol" — the characteristic is
already right; only the species restriction excludes it. This generalises:
animal behaviour, animal imaging, plant phenotyping and ecology-with-protocol are
a large slice of the field.

**`ProteinGym benchmark`** is the adjacent case and does *not* need a new value:
`natural` (wet-lab DMS assay measurements) + `constructed` (the mutant library is
specified) composes correctly. The difference is that a protein does not act.

### T16 — the keyword bucket is wrong, with consequences

The file's header warns the `kinds` column is not a claim. Confirmed:

- **`Duckietown`** is bucketed `environment`; its quote is "RGB images gathered
  using the on-board camera of our Duckiebot" — a **real robot**. Placed `fixed`
  / `natural`. A coder trusting the bucket would have written
  `interactive`/`simulated`, getting both axes wrong.
- **`Poker Hand`** is bucketed `environment`; it is the UCI tabular dataset
  ("originally multiclass data streams"). Placed `fixed` / `constructed ~ rule`.
- **`Hopper Controller`** is bucketed `environment`; it is a Design-Bench offline
  model-based-optimisation dataset of 3,200 neural-net weight vectors scored by
  return. Placed `fixed` / `constructed + simulated`, and it is a textbook channel
  case: inputs `constructed`, targets `simulated`.
- **`CANUE`** is bucketed `environment` and is a consortium (the header says so).
- **`Real-World Reinforcement Learning Benchmark (RWRL)`** — the *name* says
  "real-world" and the source is a DMC simulator. The trap is in the name, not
  the bucket.
- **`Reddit FL benchmark dataset`** — the name says *federated*; the access is
  `fixed`. This is positive confirmation of the unanimous phase-1 decision to keep
  `federated` off `access`: the name carries a governance property and the supply
  protocol is unaffected by it.

---

## 4. The five measurements

### M1 — `provenance-other`: **0 of 175**, of which **0** machine-emitted operational records

No admitted name lands on `provenance-other`. **No name in the candidate set is a
cluster trace, a telemetry log or a machine-emitted operational record.**

**This count must not be read as evidence.** The candidate set was selected by
three keyword buckets — `environment`, `suite`, `reference` — and **no keyword in
that set can select a cluster trace.** A Borg trace is bucketed by neither
"environment", "suite" nor "reference". The sampling frame makes the measurement
SYNTHESIS §2 asked for structurally impossible on this file. Reporting 0 here is
reporting the frame, not the field.

Two names could land there and the name cannot say:

- **`SAGE Benchmark`** — 50 smart-home tasks. If they execute against real IoT
  devices, the observations are device telemetry: no human activity produced
  them, so `human-incidental` fails by its own stated test and
  `provenance-other` is the destination. If they execute in simulation,
  `constructed`. **Undecidable from the name.**
- **`CityLearn`** — if the building loads are real smart-meter traces rather than
  EnergyPlus output, the same applies.

And one rejected name is the purest case in the set: **`CANUE`**, whose
"indicators for unemployment, social deprivation, access to health services"
are computed aggregates over **administrative records** — run A's
`institutional_record` exactly. The admission rule removes it before
`provenance-other` can count it (T2).

**Conclusion for the revisit**: this candidate set cannot supply evidence for or
against restoring the byproduct-of-operation value. If the owner wants that
evidence before #103, the sample has to be drawn by a frame that can see
telemetry — a keyword sweep for `trace`, `log`, `telemetry`, `workload`,
`registry`, `claims`, `EHR`, `admin` over `data_source_names.tsv`. Absence here
is not evidence, and I am not treating it as any.

### M2 — strained `human-incidental`: **yes, 5 names, in two distinct patterns**

**Pattern 1 — photographs of human artifacts (the larger problem).**
`German Traffic Sign Recognition Benchmark (GTSRB)` · `IMDB-Wiki Dataset`.

The signal is a camera measurement. `natural`'s negative test —
*"a human artifact or judgement arriving through an instrument is not natural —
the instrument is a channel, not an origin"* — **expels it**, because the subject
is a traffic sign or a person. `human-incidental` then claims it on the strength
of the **subject** rather than the **signal**: a traffic sign does exist for its
own purposes, but what is in the dataset is a photon count, not a sign. Run A's
recorded warning that `natural` "risks vacuity, since every photograph is a camera
measurement" turns out to have the opposite failure mode: the negative test makes
`natural` not vacuous but *too narrow*, and the overflow lands on
`human-incidental`. This affects most of computer vision, not 2 names.

**Pattern 2 — a real system transcribed by hand.**
`Mandl benchmark` · `Mumford benchmark` — real city transit networks reduced to
15-node graphs. The content is infrastructure, measured and transcribed; no value
covers "a real system a human abstracted into a formal object". `human-incidental`
is where it goes and it reads as a residual.

**Pattern 3 — the fold's own case, and it does *not* read strained.**
`MS MARCO` (Bing query log + human answers) is a clean `human-incidental +
elicited`. The click-log half of the fold is fine. **What strains is the clinical
half the moment the record is an image** — `TNMIX benchmark`, T14, where the
frozen node files place fastMRI under `natural` and MIMIC under
`human-incidental` with no criterion between them. I count TNMIX as the fifth
strained name and the most consequential one, because it is the fold's own
territory.

So: the fold is sound for clicks and ratings, and the strain is real for clinical
**imaging** and for photographed artifacts.

### M3 — `rule`: **used, by 12 names, and crucially not only on games**

| name | why `rule` |
|---|---|
| `Juliet Test Suite` | NIST test cases with labels guaranteed by the generator and checkable by a stated CWE rule. **The strongest case in the set** |
| `Compositional Freebase Queries (CFQ)` | answers computed by executing SPARQL against Freebase — a non-learned engine |
| `Compositional Freebase Questions (CFQ)` | alias of the above |
| `Advanced Arithmetic Benchmark` | answers computed by arithmetic |
| `Toy Arithmetic Benchmark` | as above |
| `Poker Hand` | hand rank computed by the rules of poker |
| `Kuhn Poker` · `Leduc Poker` · `Hanabi` | game outcomes — the `rule` node's own example class |
| `ExtremeWeather` | threshold-based event detection labels (conditional) |
| `CARLA Multi-Town dataset` | hand-coded privileged expert autopilot (conditional) |
| `Lunar Lander Game Data` | scripted simulated user (conditional) |

**The speculative flag is supported, and by the right evidence.** `rule` would be
hollow if it were only reachable through game outcomes, since A and C route those
to `constructed`. It is not: `Juliet Test Suite` and `CFQ` are **non-game,
non-contested** `rule` cases, reached from names, and B's original argument (a
unit test checks real code, so "no empirical referent" is false of it) is exactly
what Juliet instantiates. **Keep it.**

Two caveats, both recorded rather than resolved:

1. **4 of the 12 are a `constructed ~ rule` tie I cannot break.** For
   `Advanced Arithmetic Benchmark`, `Toy Arithmetic Benchmark` and `Poker Hand`,
   the generating specification *is* the verifying rule — one object. The two
   nodes' tests ("the generating specification IS the ground truth" vs "a person
   could check the signal by applying a written rule") are both true, of the same
   fact.
2. **The count is 12 or ~55 depending on T11's fork**, and the fork is not mine to
   settle.

### M4 — `stream`: **0 names**, as expected, and one piece of positive evidence

No name takes `stream` as its typical value and none takes it as a legitimate
alternative. **This is not evidence against the value** — the node's own flag says
so and SYNTHESIS §3 predicted it exactly ("live feeds get frozen and the snapshot
is what gets the name"). The candidate set contains no live feed to begin with:
its three buckets are environments, suites and reference corpora.

The one result worth reporting beyond the 0: **`Poker Hand`**'s quote says *"the
'Poker Hand'… are originally multiclass data streams"* — the paper calls its
source a stream and the correct `access` value is `fixed`. The stream-learning
literature's "data stream" means *a fixed file consumed once in order*, not a
source on its own clock. So the first name in this set to use the word "stream"
is a name that must **not** get the value. That is positive evidence for the
node's mis-coding warning and for keeping the negative test's first clause
("fails if the consumer froze a snapshot first") prominent.

### M5 — the `simulated`/`constructed` boundary: **it bites, on 45 names**

- **26 names carry the tie as their recorded value** (T10): the MuJoCo
  morphologies, classical control, MPE's four spellings, `Flatland`,
  `Sitnikov Problem Simulation Dataset`. Resolved to `simulated` only by the
  examples column, not by any test.
- **16 names in the ALE cluster** are placed `constructed` while `simulated` is
  arguable, because an emulator *is* a mechanistic model of a real machine (T5).
- **3 names sit on a different face of the same boundary**: `Gibson Environment`,
  `Habitat Pick (HabPick)` and `MultiSensory Embodied 3D-Scene Environment` are
  laser-scanned **real** interiors/objects, then rendered — `natural + simulated`,
  which is the hard case the `constructed` node's note already names ("Habitat is
  the recurring hard case"). Now it has names attached.

The sharpest single pair, which shows the boundary is about the *referent* and not
about the computation:

| name | placement | why |
|---|---|---|
| `FDA-approved UVA/Padova Type1 Diabetes Mellitus Simulator` | `simulated`, clean | validated against real patients; "the simulation is wrong" is a regulated complaint |
| `HalfCheetah-v2` | tie | identical class of solver, identical physical units, **no referent at all** |

Same engine class, same units, opposite answers — and the only thing that
separates them is whether something outside the program is being modelled, which
is `constructed`'s negative test and not `simulated`'s positive one.
**The two nodes' tests do not divide at the same place.**

---

## 5. What I would change, and what I would not

**Would not.** Nothing in §5 of the synthesis should be deleted on this evidence.
`stream` gets 0 and that is predicted. `provenance-other` gets 0 and the frame
explains it. `oracle` gets 1 typical and 8 legitimate (`PubMed`, `PubMed Central`,
`Wikipedia` ×2, `Common Crawl`, `MS MARCO`, `OpenML-CC18`, `OpenML-CTR23`) —
A's prediction that it is structurally under-named is confirmed, and its low count
is not rarity. `generator` gets 1 typical (`RB benchmark`) and 24 legitimate.
`federated`'s exclusion is confirmed by `Reddit FL benchmark dataset`.

**Would propose, in order of the evidence behind it.**

1. **Reword `elicited` to admit non-human subjects** (T15, 1 name here, a large
   slice of the field). Its characteristic is already correct; only the word
   "people" excludes `Neural Latents Benchmark`. This is the one genuine
   add/amend the 194 names force.
2. **Give the admission rule a clause for evaluation protocols** (T4, 14 names)
   and **one for data providers/institutions** (T2, 1 name). Both are currently
   rejected or admitted on the definition rather than on a clause, and 15 of 194
   names turn on them.
3. **Split `simulated`'s positive test** (T10/M5, 45 names). Its two halves —
   "an engine with physical units" and "'the simulation is wrong' is meaningful" —
   disagree on 26 names, and the `constructed` negative test agrees with the
   second half. Either make the referent the operative test on both nodes, or
   adopt run A's folded alternative (one `program-computed` value + a `referent`
   axis). I am recording the measurement, not choosing.
4. **Widen the `human-incidental` watch note from "clinical records" to "clinical
   imaging"** (T14/M2), and state a criterion that separates fastMRI from MIMIC,
   since the node files currently place those two on opposite sides.
5. **Decide granularity per axis** (T6). Suite-level `access` is reliable;
   suite-level `provenance` is a union of up to 5 values. A raised this from one
   run; six suites in this set measure it.

**Would not do on this evidence.** Resolve T11 (`rule` vs `constructed` on game
outcomes) by majority — it is the channel problem in disguise and the corpus does
not arbitrate. Resolve T10 by picking `simulated` on the strength of the examples
column, which is what I had to do to produce a placement and which should not be
mistaken for a finding.
