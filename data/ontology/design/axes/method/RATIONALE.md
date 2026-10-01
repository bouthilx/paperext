# Method axis, second derivation

Re-derived from `AXES.md` §3 and §8b, `GRANULARITY_AUDIT.md` M1–M7 and
`EXTERNAL_DIFF.md`. The first derivation under `axes/method/` was **not read**,
by instruction, so this is a re-derivation and not a patch.

Deliverable: `nodes.tsv` — 8 level-1 rows (7 substantive aspects + the
administrative `uninformative` row §8b requires) and 41 level-2 nodes, each with
a stated characteristic, a positive and a negative test, and three depth-3
example labels.

**All corpus counts in `nodes.tsv` are indicative and unvalidated.** They come
from one ordered keyword assignment over the 2054 names in `domain_names.tsv`
(first rule wins, one node per name), not from a mapping pass. They inherit
AXES.md's own caveat: `contributed` and `used` mentions are merged (issue #89),
and Method values skew heavily *used*. **No node in this file was created,
kept, merged or split because of its count.** Several nodes are deliberately
tiny.

---

## 1. The single principle per sibling set

This is the whole point of the re-derivation, so the principles are stated first
and everything else follows from them.

| parent | principle of division (the `characteristic`) |
|---|---|
| root (level 1) | which aspect of the method the name picks out (AXES §3, unchanged) |
| Learning signal | what supplies the training target |
| Training regime | the dimension along which one training run is spread |
| Computational machinery | which formal structure the machinery exploits to produce an answer |
| Model design | which family of structure the model belongs to (+1 declared exception) |
| Model analysis | which question is asked of a model that already exists |
| Learning theory | which property of learning is bounded or explained |
| Data curation | which part of the training set the work acts on |
| uninformative | administrative; not an aspect |

---

## 2. How each audited defect was fixed

### M4 + M5 — `Inference & optimization` mixed four principles

The worst defect, and the one that reshaped the branch. The old sibling set
divided simultaneously by variable type, by inferential framework, by problem
class (`Sequential decision-making`) and by stage (`Inference-time methods`).

**Principle used: which formal structure the machinery exploits to produce an
answer.** Applied without exception, it yields eight siblings:

- **Optimization** — exploits the analytic or combinatorial structure of an
  explicit objective over a feasible set.
- **Probabilistic inference** — exploits a probability model and its likelihood.
- **Causal inference** — exploits causal assumptions encoded as interventions.
- **Logical inference** — exploits entailment over symbolic formulas and constraints.
- **Game theory** — exploits strategic interaction, solved for an equilibrium.
- **Search** — exploits a goal test and a heuristic estimate over a state space.
- **Planning** — exploits an action model with preconditions and effects.
- **Evolutionary computation** — exploits nothing but evaluated fitness, under
  variation and selection.

Four consequences, each of which disposes of one of the audited mixes:

1. **Variable type stops being a level-2 principle.** `Continuous optimization`
   and `Combinatorial optimization` are no longer siblings; they are depth-3
   children of one `Optimization` node, split by the structure of the feasible
   set — a legitimate single principle one level down. This also gives bare
   `Optimization` (71 mentions) an exact home instead of forcing it to
   branch level, which was the hidden cost of promoting the split.
2. **`Sequential decision-making` is gone.** It named a problem formulation, not
   machinery. `Markov Decision Processes` (3) and `POMDPs` (5) now land under
   **Planning**, as formalisms solved by dynamic programming and MDP planning.
   When the surface says *reinforcement* learning, §8b's head-noun rule sends it
   to Learning signal instead. The overlap with the RL branch is therefore
   resolved by a mechanical rule rather than by two nodes covering one idea.
3. **`Inference-time methods` is gone.** Dividing by *when* computation happens
   is not available under this principle. Its contents were re-routed by what
   they actually are: `Retrieval-Augmented Generation` and
   `Memory-Augmented Neural Networks` name a *structure* → Model design >
   neural architectures; `In-Context Learning` (4) names adaptation across a
   task distribution → Training regime > meta-learning. `Prompt Engineering`
   and `Chain-of-Thought` are declared **unplaced** in §7 below rather than
   given a stage-shaped node.
4. **M3 is fixed in passing.** `Constrained learning` — which the first
   derivation itself flagged as not satisfying the training-regime
   characteristic — is an objective modification and sits under Optimization,
   with regularized and robust objectives.

The closest-to-strained pair in this set is **Optimization vs Evolutionary
computation**: both produce an optimum. The line held is *structure-exploiting
vs evaluation-only*, which is exactly why `Bayesian Optimization` (a
structure-exploiting surrogate) sits under Optimization and `Metaheuristics`
does not. Declared, not laundered.

### M1 — register mismatch at level 1

The audit is right that `Learning theory` is a *claim* while the other rows look
like *stages*, and ACM CCS independently files learning theory outside
`Computing methodologies`. Two things are nevertheless true:

- §3's own stated level-1 characteristic is **"which aspect of the method the
  name picks out"**, not "which stage of the pipeline". Under that reading, "what
  is established about learning" is as legitimate an aspect as "what feedback
  drives learning": both are questions a *name* can answer. The mismatch is in
  the stage-reading, not in the set.
- The set already contains a second claim-register row, `Model analysis`, split
  off by the owner on 2026-09-28. So the register split is 5 construction
  aspects + 2 claim aspects, not 5 + 1.

**Fix applied:** the level-1 set is kept, the characteristic is restated in the
node file in name-picks-out form, and the two claim-register rows carry a note
saying so, so that a report never presents the seven as a pipeline whose shares
sum to a process. See §5 for the alternative level 1 and the argument.

### M6 — a discipline-sized node beside topic-sized ones

`Statistical learning theory` was a sibling of `Compositional generalization`.

**Principle used: which property of learning is bounded or explained.** Every
sibling must name a *quantity or property*, never a discipline:
`Generalization`, `Sample complexity`, `Expressivity`, `Training dynamics`,
`Scaling behaviour`. All five are question-sized.

The discipline-sized surfaces did not disappear — they became **branch-level
residents** under §8b's `Bioinformatics` precedent: `Machine Learning Theory`
(8), `Deep Learning Theory` (7), `Theoretical Machine Learning` (5) and
`Statistical Learning Theory` (2) name the branch and nothing narrower, so they
map to `learning-theory` itself (4 names / 22 mentions, i.e. ~35% of the
branch). That is the structurally correct home for a name whose specificity is
the branch, and it is what M6 was really pointing at.

### M7 — `Data curation` children overlapped and no principle was stated

**Principle used, now stated: which part of the training set the work acts on** —
its inputs, its composition, or its labels. Three children, and the old overlaps
resolve mechanically:

- augmentation and synthetic data *both create inputs* → one node,
  **Data synthesis**;
- selection, filtering, weighting and ordering all *choose among existing
  examples* → **Data selection**;
- annotation, label cleaning and label noise all *act on targets* →
  **Annotation**;
- `Dataset construction`, which the audit noted spans both, is a **branch-level
  surface** on `data-curation` rather than a fifth sibling.

Two boundaries had to be declared for this to partition:

- **Noisy labels.** A method that *tolerates* bad labels is a supervision
  paradigm → Learning signal > weakly supervised. Work that *measures or
  repairs* labels is → Data curation > annotation.
- **Active learning** selects which examples to label, so it touches two
  children. It is filed under Data selection, because what it contributes is the
  selection rule; the annotation itself is assumed.

### M2 — level mismatch in the learning-signal set

Not on the required list, but the audit found it and the instruction is to run
the same audit on this output, so it is fixed.

**Principle used: what supplies the training target.** Six siblings, the
field's classic partition, with the two the audit reported missing restored:
supervised (an annotator), semi-supervised (an annotator, for part of the data),
weakly supervised (a cheap proxy for an annotator), self-supervised (the input
itself), unsupervised (nothing), reinforcement (the environment's reward).

`Learning from human feedback`, which the audit called a specialisation promoted
to sibling, is depth-3 under Reinforcement learning, alongside imitation
learning, inverse RL, offline RL, multi-agent RL, hierarchical RL and bandit
learning. Behavioural cloning is supervised by construction; it is filed with RL
because its target is expert *interaction* data. Declared.

---

## 3. Where the three blind spots landed, and what they cost

All three are kept on semantics and on the agreement of two independent external
sources, **not** on corpus support. Under AXES §9 they are "possibly
speculative, justify or keep". They are justified and kept, and each is flagged
in `nodes.tsv` as corpus-thin.

### 1. Evolutionary / bio-inspired computation

**Home: Computational machinery > `Evolutionary computation`** (level 2).
It required no new level-1 home: under "which formal structure the machinery
exploits", a population improved by variation and selection is a machinery
family exactly as a gradient method is.

Corpus, all of it: `Evolutionary Algorithms` 2, `Metaheuristics` 2,
`Swarm Robotics` 2, `Evolutionary Search` 1, `Simulated Annealing` 1,
`Neural-Guided Meta-Heuristic Algorithms` 1, `Optimization and Metaheuristics` 1
— ~7 names / ~10 mentions against ACM's whole `Bio-inspired approaches` subtree
and arXiv `cs.NE`.

Named `Evolutionary computation` and not `Bio-inspired computation` deliberately:
§9 forbids names general enough to attract out-of-scope entries, and
"bio-inspired" would attract neural networks, `Neuroscience-inspired AI` (2) and
`Neuromorphic Computing` (2). The negative test says so explicitly. The cost of
that choice is that **artificial life** sits under a name that does not quite
describe it; it is kept as a depth-3 member with a note.

### 2. Logical, relational and inductive-logic learning

**Home: split across two level-1 aspects, deliberately.**

- the *engine* → Computational machinery > `Logical inference`
  (SAT/SMT 2, `Theorem Proving` 1, `Constraint Programming`/`Constraint
  Solving`/`Constraint Inference` 3, `Automated Reasoning` 1, `Logical
  Inference`/`Logical Reasoning` 2, `Program Synthesis` 3);
- the *representation* → Model design > `Symbolic models`
  (`Knowledge Representation` 3+1, `Knowledge Graphs`, `Ontology Alignment`,
  `Expert Systems`, `Symbolic Systems`, inductive logic programming).

This split is not a hedge: it is forced by the level-1 characteristic. A solver
is machinery; a logic program is a structure that computes a function. The
practical payoff is that **`Neural-Symbolic Learning` (1) and `Neuro-Symbolic
AI` (1), reported unplaceable by the first derivation, are now placeable** — they
are hybrid *structures*, so Model design > symbolic models, with the head-noun
rule confirming it (head `Learning` is generic → the modifier decides).

### 3. Classical AI beyond learning — the largest gap

This is the one that required a real structural decision, because §3's level 1,
read as pipeline stages, has **no row that a planner or a knowledge base can
occupy**: nothing about them is a stage of building a learned model. Three
sub-gaps, three homes:

- **Search methodologies** → Computational machinery > `Search`.
- **Planning & scheduling** → Computational machinery > `Planning`.
- **Knowledge representation & reasoning** → split as in blind spot 2:
  Model design > `Symbolic models` for the representation, Computational
  machinery > `Logical inference` for the reasoning.

**What level-1 home this required:** it required **renaming
`Inference & optimization` to `Computational machinery`**, which is the one
level-1 change in this derivation. The justification is that §3's own
characteristic for that row is already *"what mathematical machinery computes
the answer"* — the *name* was narrower than the stated principle, and it was
also a compound name, which §9 bans. Under the restated name the row admits an
A\* search, a planner, a SAT solver and an SGD step on one principle, and the
axis stops being ML-shaped. The extension is widened; the characteristic is not
changed.

Corpus support for the classical-AI nodes is real but small and concentrated in
planning-as-an-application: `Motion Planning`, `Task and Motion Planning`,
`Robotic Motion Planning` 2, `Probabilistic Planning`, `Planning with
Uncertainty`, `Job-Shop Scheduling`, `Personnel Scheduling`,
`Vehicle and Crew Scheduling Problem`, `Scheduling`, `Retrosynthetic Planning` 2.
`Search` is the thinnest node on the axis (2 names / 7 mentions after
`Neural Architecture Search` is routed to architectures and `Code Search` to
Task) and is declared as such in §6.

---

## 4. Where AXES.md is silent, ambiguous or self-contradictory

Eight findings. The first four affected node placement.

1. **§3's table has seven rows; §3's prose and §8b both say "six aspects".**
   The count was never updated after `Data curation & supervision quality` was
   added (tail validation F2) and after `Model analysis` was split off
   (2026-09-28). This derivation delivers **seven substantive aspects plus
   `uninformative`**, and the brief's "six aspects" should be read as seven.
2. **Expressivity is assigned to two different branches.** §2 says questions the
   field asks about its own machinery, *naming expressivity explicitly*, belong
   to `Learning theory & generalization`; §3's `Model analysis` row lists
   `expressive power` among its children. **Resolved to §2**: a model *class* is
   not a model that exists, so expressivity is Learning theory > `Expressivity`
   and `Model analysis` keeps only claims about trained models.
3. **Privacy and fairness techniques are promised Method homes that §3 never
   provides.** §3 D2 says "interpretability (~65), adversarial robustness (~64),
   privacy (~27) and fairness interventions (~15) are techniques and need Method
   homes", but §2's technique rule sends `Differential Privacy`,
   `Adversarial Training` and `Safe RL` to Desired properties, and §3's own
   children list contains no privacy or fairness node. **Resolved**: this
   derivation gives Method nodes to interpretability and adversarial ML (which
   are questions asked of a model) and **no** privacy or fairness node, because
   such a node would be a property node imported into Method — the mirror of the
   absorption failure §2 warns about. On the Method side those names map to the
   machinery they modify: DP-SGD → Optimization, secure aggregation → Federated
   learning, membership-inference → Adversarial machine learning, reweighting
   for fairness → Data selection. Cross-axis double mapping is legal (§4, D6).
4. **Uncertainty machinery is routed to Method but has no Method node.** §2
   declines a `Reliability` property node on the grounds that
   `Uncertainty Estimation`, calibration, conformal prediction and
   `Neural Network Verification` (~34 mentions) are "machinery §3 already routes
   to Method" — but §3 lists none of them except verification. Closed here with
   Model analysis > `Uncertainty quantification` (11 names / 29 mentions).
5. **§3, §6 and §8b break §9's own compound-name ban at level 1.**
   `Inference & optimization`, `Learning theory & generalization`,
   `Data curation & supervision quality`, `Modality / data`, `Vision & imaging`,
   `Graphs & relational` are compound names, while §9 says "No compound names:
   find the family's real name or split". This derivation uses non-compound
   level-1 names (`Computational machinery`, `Learning theory`,
   `Data curation`) for the same aspects. The rule should be applied to AXES.md
   itself or explicitly relaxed for level 1.
6. **`Model design`'s characteristic is itself a compound principle.** §3 writes
   "what structure computes the function, **and at what cost**", and §3 admits
   the `X and Y` fusion "moved out of the node name and into the principle" when
   `Model analysis` was split off. §3 then locks efficiency techniques there as
   a depth-2 family. The two statements cannot both be satisfied; see §6 for how
   this derivation declares it rather than hiding it.
7. **No rule for names that are mathematics rather than method.**
   `Graph Theory` 6, `Information Theory` 3, `Random Matrix Theory`,
   `Automata Theory` 3, `Formal Language Theory`, `Theoretical Computer Science`
   4, `Dynamical Systems` 4, `Partial Differential Equations` 3. §7 sends
   `Game Theory` and `Operations Research` to Method as machinery but says
   nothing about mathematics that supplies no machinery. Ruled here: a
   mathematical field that supplies the *object of study* rather than a
   procedure leaves this axis for Scientific discipline (OECD 1.1/1.2, which §7
   explicitly opens to theory of computation).
8. **The uninformative row's internal structure is unspecified.** §8b calls it
   an administrative level-1 row but §9 requires ≥2 substantive children of any
   parent. Given two children here (`generic-field-names`,
   `generic-technique-names`) purely to satisfy §9; the distinction carries no
   reporting weight and the row is excluded from axis shares either way.

---

## 5. Should level 1 change? Argued.

**Primary proposal: no** — the §3 set is delivered, with one rename
(`Inference & optimization` → `Computational machinery`) and two
de-compoundings that do not change any extension.

**The alternative, stated fully.** M1's observation supports a three-node level 1
dividing by *what the work contributes*:

| L1 | children (= today's level 1) |
|---|---|
| Learning procedures | learning signal · training regime · data curation |
| Computed objects | model design · computational machinery |
| Claims | model analysis · learning theory |

This is register-consistent — every child of `Claims` is a claim, every child of
`Learning procedures` is an organisation of training — and it is the cut ACM CCS
made independently by putting machine-learning theory under
`Theory of computation`.

**Why it is not the primary proposal.** Three reasons, in order of weight.

1. **It costs the deliverable a level.** The survey reports at depth 2. Under
   the alternative, depth 2 *is* today's level 1, and the reportable granularity
   (`Reinforcement learning`, `Optimization`, `Interpretability`) moves to depth
   3 — so the whole axis has to be re-derived to depth 4 to say the same things.
   `NodeCut` matching ids rather than depth softens this but does not remove it:
   every consumer of the axis changes.
2. **Its top level is uninformative.** "62% of our method mentions are learning
   procedures" is not a finding. §1's admission test — two papers can differ on
   it while agreeing on everything else — is satisfied by the seven aspects and
   is *barely* satisfied by the three.
3. **M1's premise is a misreading.** §3's stated characteristic is "which aspect
   of the method the **name** picks out". A surface name can pick out a claim as
   easily as a stage; `Machine Learning Theory` is a name a paper gives for its
   research domain, and it picks out an aspect of its method. The register
   mismatch is real in the *pipeline* reading, which §3 never asserts.

**What should change instead.** Two cheap fixes, both applied in `nodes.tsv`:
restate the level-1 characteristic in name-picks-out form, and mark
`Model analysis` and `Learning theory` as claim-register so no report presents
the seven aspects as a process. If the owner nonetheless wants register purity at
level 1, the three-node version above is the form to adopt — and then
`uninformative` becomes the fourth row, not the eighth.

---

## 6. Granularity audit of this output

Test, as applied to the first derivation: *are these the same kind of thing, at
the same level of specificity, and does any sibling exist only because it was
large in this corpus?*

**No node here exists because it was large.** The volume test is passed
trivially: the branch with the largest count (`Optimization`, 227 indicative
mentions) and the branch with almost none (`Search`, 7) are siblings, and three
nodes were created against the corpus rather than from it.

**Sibling sets I am confident in** (one principle, one specificity level, no
overlap):

- Learning signal's six — the field's own partition by target supplier.
- Data curation's three — inputs / composition / labels; the M7 fix.
- Learning theory's five — all question-sized; the M6 fix.
- Model analysis's four — all are questions asked of a trained model.
- Training regime's seven, with one caveat below.

**Sibling sets I am NOT confident in — declared, not laundered:**

1. **Model design > `Model efficiency` is a register exception.** Its five
   siblings (`Neural architectures`, `Generative models`, `Symbolic models`,
   `Kernel methods`, `Ensemble methods`) are *families of structure*;
   `Model efficiency` is a *transformation of structure*, which is a different
   kind of thing. This is the same shape of defect as M1, one level down. It is
   here because the owner locked it on 2026-09-25 ("efficiency techniques are a
   depth-2 family under Model design, not a sixth aspect") and because §3's
   Model-design characteristic carries "and at what cost" specifically to hold
   it. **If that lock is ever reopened, this is the node to move** — the
   principled alternatives are an eighth aspect, or dissolving it into the
   family whose form it changes.
2. **`Optimization` vs `Evolutionary computation`** — both minimise an
   objective; the line is structure-exploiting vs evaluation-only. It holds for
   GA, GP, ES and swarm, and it holds for `Bayesian Optimization` (surrogate
   structure → Optimization). It is strained by single-solution metaheuristics:
   `Simulated Annealing` and tabu search have no population, and are admitted to
   `Evolutionary computation` on the variation-and-selection clause alone.
3. **`Search` vs `Planning`** — a planner is a searcher with an action model.
   They are separated because ACM CCS separates them, because they are two
   research communities, and because the corpus vocabulary that exists is
   almost all planning. If `Search` stays empty across a 2023–2026
   re-extraction, folding it into `Planning` is the right correction; today it
   would be deleting a field because one institute-year did not do it.
4. **`Continual learning` vs `Online learning`** — both divide by time. The
   line is task boundaries and forgetting vs example-by-example arrival. It is
   the weakest pair on Training regime and I expect surface names
   (`Sequential Learning` 2, `Offline Learning` 2, `Incremental Learning`) to
   land on it ambiguously.
5. **`Formal verification` vs `Adversarial machine learning`** — both are about
   worst-case behaviour; one searched, one proved. `Robustness Verification` and
   certified-defence work sit exactly on the line. Declared; the deciding test
   in `nodes.tsv` is whether the claim is quantified over all inputs in a stated
   set.
6. **Semi-supervised learning is a mixture, not a supplier.** Five of the six
   learning-signal children name one supplier of the target; semi-supervised
   names a *combination* of two (annotator + nothing). The field's classic
   partition has this wrinkle and I did not invent a repair for it.
7. **`Unsupervised learning`'s children are declared homonyms.** `Clustering`,
   `Density Estimation` and `Dimensionality Reduction` (§8b's own list) name
   what the output must be, so they are also Task-axis values. Under §4's test
   they read as tasks; under the head-noun rule `Manifold Learning` reads as
   method. Both mappings stand, which is legal (§4, D6), but the node's shares
   should never be quoted without saying so.

**Branching factor**

| level | node | children |
|---|---|---|
| root | — | 8 (7 substantive + 1 administrative) |
| 1 | Computational machinery | 8 |
| 1 | Training regime | 7 |
| 1 | Learning signal | 6 |
| 1 | Model design | 6 |
| 1 | Learning theory | 5 |
| 1 | Model analysis | 4 |
| 1 | Data curation | 3 |
| 1 | uninformative | 2 |

41 level-2 nodes; mean branching 5.1, max 8, min 2. The two widest sets
(machinery at 8, training regime at 7) are wide because every member is a
conference-sized research area at one level of specificity — IPCO, UAI, CLeaR,
IJCAR, EC, SoCS, ICAPS, GECCO for the first — which is what §9's
"many siblings means specialising too early" is actually testing for. Neither
was split to reduce the number, because splitting would have required a second
principle.

---

## 7. Names I could not place

- **`Prompt Engineering` (6), `Chain-of-Thought (CoT) Reasoning` (1).** Every
  home I could find for them divides by *stage* — what extra computation runs at
  query time — which is exactly the M4 defect. They are not a learning signal
  (no training), not a structure (the model is fixed), not machinery (they are
  an input format). Left unplaced deliberately. If the owner wants them, the
  honest options are (a) a Task-axis home, since a prompt names what the output
  must be, or (b) an explicit level-2 `Test-time computation` node under
  Computational machinery, accepted as a stated stage-shaped exception. I
  recommend (a). Note that `In-Context Learning` (4) and
  `Retrieval-Augmented Generation` (1) *were* placeable, at meta-learning and at
  neural architectures respectively, so the unplaced residue is small.
- **`Spectral Methods` (3), `Tensor Decomposition`, `Tensor Networks` (2).**
  Numerical linear algebra used as machinery, with no branch that exploits a
  distinctive formal structure. Filed at branch level on Computational
  machinery; `spectral` is already an §8b declared homonym (89% wrong on
  Modality).
- **`Multi-Agent Systems` (11).** A classical-AI area whose surface names
  neither a training organisation nor an equilibrium. Currently swept into
  `Game theory` by the indicative tally, which I do not endorse; the correct
  treatment is a declared homonym resolved per surface (training organisation →
  Training regime; equilibrium → Game theory; agent architecture → Model design).
- **`Simulation` (5) and `Monte Carlo Simulations` (5).** §8b declares
  `Simulation` a homonym; the Method reading is Monte Carlo machinery, the
  non-Method reading is a physics or clinical instrument
  (`Monte Carlo Simulations in Medical Physics`). Not resolvable from the name.

## 8. Names rejected to other axes, with the deciding test

| name(s) | destination | deciding test |
|---|---|---|
| `Representation Learning` 56 | Task | §4: names what the output must be. AXES §4 states this placement explicitly |
| `Anomaly Detection` 20, `Out-of-Distribution Detection` 12, `Classification` 5, `Regression` 2 | Task | §4: names the output, not how it is produced |
| `Fairness in Machine Learning` 19, `Fairness in AI` 12, `Explainable AI` 10, `AI Safety` 6, `Differential Privacy` 8, `Green AI` 2 | Desired properties | §2: a demand that can be met or failed, made on the research from outside it |
| `Graph Neural Networks` 76, `Vision Transformers` 3 | Modality | §5: the name implies a modality and translating loses nothing, because the paper carries other names |
| `Operations Research` 19 | Method, branch level | §7: supplies machinery, not a problem. But it names the whole machinery branch and nothing narrower, so §8b branch-level residence applies (not `Optimization`) |
| `Control Systems` 9, `Control Theory` 2 | split | §7: control *theory* → Method (Planning, via model predictive control); control *engineering of a plant* → Engineering. §8b already declares this homonym |
| `Game Theory` 20 | Method | §7: supplies machinery → Computational machinery > Game theory |
| `Graph Theory` 6, `Information Theory` 3, `Automata Theory` 3, `Theoretical Computer Science` 4, `Partial Differential Equations` 3, `Dynamical Systems` 4 | Scientific discipline | New rule, §4.7 above: mathematics that supplies the object of study rather than a procedure. OECD 1.1 / 1.2, which §7 opens to theory of computation |
| `Signal Processing` 6, `Graph Signal Processing` 5 | Scientific discipline | Exists without AI and supplies the problem framing (OECD 2.2) |
| `Information Retrieval` 19, `Recommender Systems` 16 | Task | §7 states this for recommender systems; retrieval follows by the same test |
| `Benchmarking` 7, `Model Evaluation` 7, `Evaluation Metrics` 7, `Machine Learning Evaluation` 2 | none — `mark_ignore` | §8b: contribution-type names are not domains on any axis |
| `Deep Learning` 233m, `Machine Learning` 250m, `Neural Networks` 19, `Artificial Intelligence` 15 | Method > uninformative | §5 row three and §8b: on-axis but narrows nothing. ~581 indicative mentions, the second-largest cluster on the axis, excluded from shares |

## 9. Precedence and homonyms this axis adopts

- **Head-noun rule (§8b) is this axis's within-axis precedence**, and it was used
  to settle every fused surface rather than inventing a node:
  `Multi-Agent Reinforcement Learning` → Learning signal > reinforcement;
  `Distributed Optimization` → Computational machinery > optimization;
  `Meta-RL` → Learning signal > reinforcement;
  `Neural Architecture Search` → Model design > neural architectures (head
  `Search` is not generic, but `Architecture` carries the meaning — declared as
  the one surface where the rule needs the modifier);
  `Neural-Symbolic Learning` → head `Learning` generic → Model design >
  symbolic models.
- **New homonyms this axis declares**, extending §8b's list: `Search` (code
  search / architecture search / state-space search), `Planning` (motion
  planning / urban planning / radiotherapy treatment planning — the last two
  leave the axis entirely), `Programming` (mathematical programming /
  logic programming / writing code), `Genetic` (genetic algorithms vs genetics —
  all 11 `genetic*` names in the corpus are biology and `Genetic Algorithms`
  never occurs, so a bare `genetic` rule would be 100% wrong here),
  `Inference` (statistical inference / logical inference / the forward pass).
