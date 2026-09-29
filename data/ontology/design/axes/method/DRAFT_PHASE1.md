# Method axis, depth 3 — PHASE 1 DRAFT (semantic, no corpus access)

Written before opening `domain_names.tsv`, before any tally, and without reading
the `examples` column of `nodes.tsv`. Inputs: `AXES.md` (§3, §8b, §9),
`GRANULARITY_AUDIT.md`, and the `characteristic` / `positive_test` /
`negative_test` / `notes` columns of the 8 level-1 and 42 level-2 rows.

**This file is the record. It is not edited after phase 2.**

---

## 0. The selection rule I use to choose between competing principles

Every node below admits more than one principle of division. The rule applied
throughout, stated once so it can be checked:

> **A depth-3 sibling set must refine its parent's own characteristic, not
> import a different aspect's characteristic.**

This is the rule the audit's M1, M5 and the locked `Model efficiency` exception
are all instances of, one level down. Where the field's most famous taxonomy of
a node divides by a principle belonging to a *different* level-1 aspect, that
taxonomy is pushed to depth 4 or declared a cross-cut, and the demotion is
stated. This is what decides the owner's RL worked example (§1).

Second rule, from AXES §8b: **branch-level residence is legitimate**. A depth-3
set does not have to be a partition that catches the plain name of the parent;
`Reinforcement Learning`, `Optimization`, `Transfer Learning` name the branch and
nothing narrower, and stay on it.

---

## 1. Reinforcement learning

Parent characteristic: *the target is a reward obtained by acting in an
environment.* Parent aspect: **Learning signal — what supplies the training
target.**

### The owner's worked example, decided

Three principles compete, and two of them are the ones the owner raised:

| candidate principle | what it yields |
|---|---|
| A. whether a model of the environment's transitions is used | model-based / model-free |
| B. what is parameterised | value-based / policy-gradient / actor-critic |
| C. who or what supplies the evaluative signal | the set below |

**Between A and B, A wins**, for two reasons that are the field's own and not
mine: (i) A partitions all of RL, whereas B is only defined *inside* model-free
methods — a model-based planner may parameterise nothing, its policy being
implicit in the planning procedure, so B leaves part of the space unlabelled;
(ii) the field's canonical taxonomy chart literally nests B under A. So B is
**depth 4 under A**, never A's sibling.

**But neither A nor B is the depth-3 sibling set here**, by §0. Both divide by
*machinery* — what algorithm is run, what object is fitted — under a parent
whose aspect is *what supplies the training target*. Admitting A at depth 3
would put a machinery-register set under a signal-register parent: the same
register slip as audit defects M1 and M5, reproduced by me rather than
inherited. **A therefore lands at depth 4**, as the first split inside
`Online reinforcement learning`, and cross-cuts `Offline reinforcement
learning` (which is also model-based or model-free); **B lands at depth 5**
under model-free. Both demotions are declared costs: a depth-2/3 report of this
axis will not show a model-based share.

**Chosen principle (C): who or what supplies the evaluative signal the learner
trains on.** This is the level-1 aspect's own principle — *what supplies the
training target* — applied one notch finer, which is what §0 asks for.

### Children

1. **Online reinforcement learning** — the signal is the environment's reward,
   obtained on actions the learner itself chose and can repeat.
2. **Offline reinforcement learning** — the signal is a fixed log of interaction
   the learner did not generate and cannot extend.
3. **Learning from demonstrations** — the signal is expert behaviour: imitation,
   behavioural cloning, apprenticeship learning, and inverse RL recovering the
   reward that explains the behaviour. (One concept in the field's idiom, LfD;
   not a fused pair.)
4. **Learning from human feedback** — the signal is a human judgment of the
   agent's behaviour: preference-based RL, RLHF, reward models fitted to
   comparisons.
5. **Intrinsically motivated reinforcement learning** — the signal is computed
   by the agent for itself: curiosity, novelty, empowerment, exploration bonuses.
6. **Multi-agent reinforcement learning** — the signal is jointly produced by
   other agents that are learning at the same time, so it is non-stationary by
   construction. (Weakest member of the set; declared in §16.)

Cross-cuts, recorded and not given nodes: model-based/model-free (A),
value/policy (B), on-policy/off-policy, hierarchical RL, bandits (a problem
formulation with no state — `Planning` already holds MDP/POMDP formalisms),
`Deep RL` (names what is parameterised → branch-level residence).

---

## 2. Neural architectures

Parent: *the structure is an arrangement of differentiable components*;
positive test *how a network is wired, independently of the data it sees*.

**Principle: which connectivity pattern routes information between units.**

Rejected: *how the architecture is obtained* (hand-designed vs searched). That
is a second principle and it is why **`Neural architecture search` is not a
child** — it stays a branch-level resident, since making it a sibling of
`Convolutional networks` fuses "which wiring" with "how the wiring was found".
Also rejected: *which component type* (spiking/analog), which would admit
neuromorphic units that are not differentiable and so fail the parent's own
characteristic.

### Children

1. **Convolutional networks** — connectivity is local and weight-shared over a
   regular lattice.
2. **Recurrent networks** — a state is carried forward across steps of a
   sequence and reused.
3. **Attention-based architectures** — routing is content-addressed among all
   positions rather than fixed by position. Transformers, attention mechanisms.
4. **Equivariant architectures** — the wiring is constrained by a symmetry group
   so that a transformation of the input is a transformation of the output.
   Geometric deep learning.
5. **Conditional computation** — which components run is decided per input:
   mixture-of-experts, routing networks, early exit, sparse activation.
6. **Memory-augmented architectures** — an external addressable store is read and
   written alongside the weights; neural Turing machines, memory networks,
   retrieval augmentation.
7. **Implicit-depth architectures** — the output is defined as the solution of an
   equation rather than by a fixed stack of layers: neural ODEs, deep
   equilibrium models. *Expected to be corpus-thin; kept on the field's
   structure.*

---

## 3. Optimization

Parent: *the machinery exploits the analytic or combinatorial structure of an
explicit objective **over a feasible set***.

**Principle: the structure of the feasible set.** The parent's own wording names
it, and `RATIONALE.md` §2 already ruled that continuous and combinatorial are
depth-3 children of one node rather than siblings at depth 2.

Rejected, each because it is a *second* principle that would reproduce M4:
*what information about the objective is used* (first-order / second-order /
zeroth-order); *the form of the problem* (constrained, robust, minimax, bilevel,
stochastic); *what the decision variable is* (model parameters /
hyperparameters / an operational decision). All of these become depth 4 under
`Continuous optimization`, or cross-cuts.

### Children

1. **Continuous optimization** — the feasible set is continuous, so derivatives
   and convexity are available to be exploited.
2. **Combinatorial optimization** — the feasible set is discrete, so the
   structure exploited is integrality, matroid, flow or polyhedral.

Only two children, with the first expected to hold most of the volume. That is
deliberate and is the clearest illustration of the owner's rule on this axis:
this is the second-largest node I touch, and volume bought it priority, not a
third child. A third child (`Riemannian optimization`, feasible set = a
manifold) is the only candidate that divides by the *same* principle and is
rejected on specificity: it is a technique-sized area beside two field-sized
ones.

---

## 4. Generative models

Parent: *the structure specifies a distribution it can sample from or score.*

**Principle: how the distribution is specified — what the model can compute
about a density, and how a sample comes out of it.** This is the field's own
taxonomy (explicit-tractable / explicit-approximate / implicit, extended with
the score-based family that postdates it).

Rejected: *what is generated* (images, text, molecules) — that is Modality and
Task, and §5 forbids importing them; *how the model is trained* (adversarial vs
maximum-likelihood vs denoising) — a learning-signal principle under a
model-design parent.

### Children

1. **Autoregressive models** — the density is factorised into a product of
   conditionals and evaluated exactly.
2. **Latent-variable models** — the density is defined by marginalising an
   unobserved variable and is bounded rather than computed. VAEs.
3. **Normalizing flows** — the density is obtained exactly by an invertible
   change of variables.
4. **Energy-based models** — the density is specified only up to an unknown
   normalising constant.
5. **Implicit generative models** — no density is defined at all; the model is a
   sampler, trained against a critic. GANs.
6. **Diffusion & score-based models** — the density is specified through its
   score along a prescribed noising process. (A doublet naming one family in the
   field's idiom, which §9 permits.)
7. **Graphical models** — the density is specified by a conditional-independence
   structure over a graph. Bayesian networks, Markov random fields. (The
   parent's note asks for graphical and Bayesian-network models at depth 3.)

---

## 5. Self-supervised learning

Parent: *the target is constructed from the input itself.*

**Principle: what pretext target is constructed.** This is the parent's
characteristic asking one further question, which is the cleanest case of §0 on
the axis.

Rejected: *which modality the pretext is built for* (Modality axis); *joint
embedding vs generative* — a real recent framing, but it divides by the output
structure, which is Model design.

### Children

1. **Masked prediction** — the target is a withheld part of the input, predicted
   from the rest. Masked language and masked image modelling, denoising
   autoencoding.
2. **Next-element prediction** — the target is the continuation of the input in
   its natural order. Causal language modelling, next-frame prediction.
3. **Contrastive learning** — the target is which candidate shares a source with
   the anchor, against negatives.
4. **Self-distillation** — the target is the representation produced by another
   view or by a slowly-updated copy of the network itself. BYOL, DINO, JEPA-style
   latent prediction. (Homonym declared against Model efficiency >
   `Knowledge distillation`: there the teacher is a *larger* model and the point
   is cost.)
5. **Transformation prediction** — the target is the identity of a
   transformation applied to the input: rotation, permutation, jigsaw ordering.

---

## 6. Probabilistic inference

Parent: *the machinery exploits a probability model and its likelihood*;
positive test *the answer is a distribution, a posterior or a sample from one.*

**Principle: how the posterior is obtained.**

Rejected: *what the model is* (Bayesian nets, GPs, state-space models) — that is
Model design; *probabilistic programming*, which names the **language in which a
model is written** rather than a way of obtaining a posterior, so it stays a
branch-level resident rather than becoming a sixth sibling.

### Children

1. **Markov chain Monte Carlo** — the posterior is approximated by simulating a
   chain whose stationary distribution is it.
2. **Variational inference** — the posterior is approximated by optimising over
   a tractable family.
3. **Sequential Monte Carlo** — the posterior is propagated along a sequence by
   weighted particles and resampling.
4. **Message passing** — the posterior is computed by propagating local messages
   over the model's factorisation. Belief propagation, junction tree,
   expectation propagation.
5. **Simulation-based inference** — the likelihood cannot be evaluated, so the
   posterior is obtained from simulations. ABC, neural posterior estimation.

---

## 7. Transfer learning

Parent: *training is spread across a source and a target domain or task.*

**Principle: what differs between source and target.** The parent's own wording
names the two things that can differ, so the refinement asks which one does.

Rejected: *what is carried across* (instances / features / parameters /
relations — the other axis of the canonical transfer survey). It is a single
coherent principle and was a close call, but under it `Domain adaptation` — the
one sub-area of transfer the community names constantly — dissolves into
"feature transfer" and stops being reportable. Recorded as the competing
principle, available at depth 4. Also rejected: *what access the target side
gives* (supervised / unsupervised / source-free / test-time), which becomes
depth 4 under `Domain adaptation`.

### Children

1. **Domain adaptation** — the input distribution changes and the task does not.
2. **Cross-task transfer** — the task changes: a new label space or objective,
   reached by fine-tuning or by reusing a pretrained representation.

Two children, the minimum §9 allows. No third division exists under this
principle: `Domain generalization` is already assigned to
Learning theory > `Generalization` by the level-2 rows, and cross-lingual and
cross-modal transfer name a Modality value, not a transfer relation.

---

## 8. Interpretability

Parent: *the question is what the model computes internally and why it produced
an output*; deliverable is *a human-readable account.*

**Principle: the vocabulary in which the account is stated.**

Rejected: *local vs global* (what is explained — one prediction or the whole
model): a genuine single principle, but it cross-cuts every child below and is
therefore a cross-cut, not a sibling set. Rejected: *post-hoc vs
interpretable-by-design*: the by-design half is a claim about a **structure**,
so it belongs to Model design, and a set containing it would straddle two
level-1 aspects.

### Children

1. **Feature attribution** — the account assigns credit to parts of the input.
   Saliency, gradient attribution, Shapley-value attribution, surrogate local
   models.
2. **Concept-based explanation** — the account is stated in human-named concepts
   the model is shown to encode. Probing, concept activation vectors, concept
   bottlenecks.
3. **Mechanistic interpretability** — the account is a circuit over internal
   components: which units and paths implement the behaviour. (AXES §2 routes
   this name to Method explicitly.)
4. **Example-based explanation** — the account names other data points:
   influential training examples, prototypes, counterfactual instances.

---

## 9. Model efficiency

Parent: *the model form is changed so the same function costs less to store or
run.*

**Principle: what is removed or replaced to obtain the saving.**

Rejected: *which resource is saved* (memory / latency / energy) — that is
Desired properties > Frugal AI read into Method, exactly the absorption failure
AXES §2 warns about; *when the saving is applied* (during training vs post-hoc)
— a stage principle, defect M5's shape.

### Children

1. **Pruning** — parameters or whole structures are removed.
2. **Quantization** — the numerical precision of weights and activations is
   reduced.
3. **Knowledge distillation** — the model is replaced by a smaller one trained
   to reproduce its behaviour.
4. **Low-rank factorisation** — dense operators are replaced by factored or
   low-rank approximations.

---

## 10. Adversarial machine learning

Parent: *the question is how the model fails under a worst-case or malicious
input*; positive test *an adversary is modelled explicitly.*

**Principle: which attack surface the adversary reaches.** This is the standard
three-way taxonomy of the adversarial-ML community and of the NIST adversarial-ML
taxonomy, which makes it an external check rather than my invention.

Rejected: *attack vs defence*. It is one principle, but it cross-cuts all three
children below — every defence is defined by the attack it forestalls — so it is
a cross-cut. A defence maps to the child naming the attack it answers.
Rejected: *threat model* (white-box / black-box / physical), likewise a
cross-cut.

### Children

1. **Evasion attacks** — the adversary perturbs the input at inference time.
   Adversarial examples, and the robust training and certification that answer
   them.
2. **Poisoning attacks** — the adversary corrupts the training data or the
   training process. Backdoors, trojans, data poisoning.
3. **Privacy attacks** — the adversary learns about the training data or the
   model from access to it. Membership inference, model inversion, model
   extraction. (Named as an attack family; this is not a Desired-properties
   privacy node, which RATIONALE §4.3 refuses and which this is not.)

---

## 11. Meta-learning

Parent: *training is spread across a distribution of tasks **in order to produce
a learner***; the outer objective is how well a learner adapts.

**Principle: what the outer loop produces as the adaptation mechanism.** This
refines the parent's own final clause, and it coincides with the field's
canonical three-way split.

Rejected: *what is meta-learned* stated as a flat list (initialisation /
hyperparameters / architecture / loss / optimizer) — it mixes specificities and
duplicates `Optimization` and `Neural architectures`; *the problem setting*
(few-shot / zero-shot / cross-domain), which is a cross-cut and where `Few-shot
learning` therefore sits.

### Children

1. **Optimization-based meta-learning** — the outer loop produces a starting
   point from which a few gradient steps suffice. MAML and descendants.
2. **Metric-based meta-learning** — the outer loop produces an embedding in
   which adaptation is comparison with labelled examples. Prototypical and
   matching networks.
3. **Amortised meta-learning** — the outer loop produces a model that reads the
   task's examples and adapts in a single forward pass, with no weight update.
   Black-box meta-learners; **in-context learning lands here**, as the parent's
   note requires.

A fourth candidate under the same principle — the outer loop produces the update
rule itself (learned optimizers, learned losses) — is rejected on specificity:
it is a technique-sized area beside three paradigm-sized ones, and it collides
with `Optimization`.

---

## 12. Continual learning

Parent: *training is spread across a sequence of tasks arriving over time*, with
earlier tasks no longer available.

**Principle: what changes from one step of the sequence to the next.** By §0
this beats the alternative, because the parent's aspect is Training regime — how
a training run is *organised* — so the refinement must be about the sequence,
not about the algorithm.

**Rejected, and this is the hardest call in the draft**: *how forgetting is
prevented* — replay / regularisation / parameter isolation. This is the
taxonomy every continual-learning survey uses, and it would very likely be more
useful to a reader. It is rejected because it is a **machinery-and-design**
principle under a training-regime parent: `Replay` is data curation,
`Regularisation` is an objective modification belonging to Optimization, and
`Parameter isolation` is an architecture. A sibling set whose three members each
belong to a different level-1 aspect is the M5 defect in pure form. Recorded as
depth 4.

### Children

1. **Task-incremental learning** — the steps are distinct tasks and the task
   identity is given at test time.
2. **Class-incremental learning** — new classes arrive and must be told apart
   from all earlier ones, with no task identity given.
3. **Domain-incremental learning** — the task stays fixed while its input
   distribution shifts from step to step.

---

## 13. Causal inference

Parent: *the machinery exploits causal assumptions encoded as interventions.*

**Principle: which part of the causal model is unknown.** AXES §3 names the
same three children ("causal discovery, effect estimation and causal
representation learning"), so this is the owner's own set with a principle
supplied.

Rejected: *which identification assumption is used* (back-door, front-door,
instruments, difference-in-differences) — an assumption-sized set beside
field-sized siblings, and it only applies to one of the three; available as
depth 4 under effect estimation.

### Children

1. **Causal discovery** — the structure is unknown and is recovered from data.
2. **Effect estimation** — the structure is assumed and the magnitude of an
   intervention's effect is the unknown. Identification, estimators,
   do-calculus, treatment effects.
3. **Causal representation learning** — the causal variables themselves are
   unknown and must be recovered from low-level observations.

---

## 14. Game theory

Parent: *the machinery exploits strategic interaction between agents, solved for
an equilibrium.*

**Principle: what the work does with the strategic interaction.**

Rejected: *the kind of game* (zero-sum / general-sum / cooperative;
normal-form / extensive-form / repeated). It is a single principle and it is how
textbooks open the subject, but it classifies *objects* where the corpus names
*activities*, and it would leave mechanism design — a whole community — with no
node. Recorded as depth 4.

### Children

1. **Equilibrium computation** — a solution concept of a given game is computed.
2. **Learning in games** — agents reach, or fail to reach, an equilibrium
   through repeated play. No-regret dynamics, fictitious play, convergence of
   learning agents. (Not multi-agent RL: the head-noun rule keeps that on the
   Learning signal branch.)
3. **Mechanism design** — the game is designed so the desired outcome is an
   equilibrium. Auctions, matching, incentive compatibility, social choice.
4. **Cooperative game theory** — value is allocated among coalitions. Shapley
   values, core, bargaining. (Cross-link declared: Shapley attribution is used
   by Interpretability > `Feature attribution`; the node's surface decides.)

---

## 15. Inference procedures

The level-2 row whose `characteristic` is blank and whose note declares a
strain: it divides by *stage* while its siblings divide by *formal structure*.
I fill the blank as the deliverable permits, and I expand it, because the node
otherwise gives one label to three distinct areas.

**Characteristic filled**: *the computation that produces the answer is spent at
query time, on a model whose parameters are fixed.*

**Principle for the children: which part of the query-time computation the
method manipulates.** This principle is only well-formed because the parent is
stage-shaped, so the children inherit the parent's declared strain rather than
repairing it. Stated, not laundered.

### Children

1. **Prompting** — the input given to the fixed model is engineered:
   instructions, demonstrations, formatting, prompt optimisation.
2. **Intermediate reasoning** — the model is made to emit and consume its own
   intermediate steps before answering. Chain-of-thought, scratchpads,
   self-critique.
3. **Test-time search** — several candidate answers are produced and one is
   selected. Self-consistency, best-of-n, verifier reranking, tree search over
   generations, test-time compute scaling.

Not here: retrieval augmentation (a structure → Model design >
`Memory-augmented architectures`) and in-context learning (adaptation across a
task distribution → Training regime > `Amortised meta-learning`), both already
routed by RATIONALE §2.

---

## 16. Level-2 nodes deliberately left as leaves

Beyond the 14 the owner prioritised plus `Inference procedures`, the remaining
27 level-2 nodes stay leaves. Reasons, by group:

- **The classic supervision paradigms** — `Supervised`, `Semi-supervised`,
  `Weakly supervised`, `Unsupervised learning`. Under the branch's principle
  (what supplies the target) each names a single supplier and has no finer
  division of the same kind. `Unsupervised learning`'s apparent children —
  clustering, density estimation, dimensionality reduction — are AXES §8b's
  **declared Task-axis homonyms**: they name what the output must be, so putting
  them here imports the Task axis.
- **Training-regime leaves** — `Multi-task`, `Federated`, `Distributed
  training`, `Online learning`. Their natural sub-divisions all name a different
  aspect: federated splits by *what is communicated* (machinery) and by *who
  holds the data* (not a method), multi-task by *how the losses are combined*
  (Optimization).
- **The classical-AI and non-neural machinery leaves** — `Logical inference`,
  `Search`, `Planning`, `Evolutionary computation`, `Symbolic models`, `Kernel
  methods`, `Ensemble methods`. Each has a real field sub-structure (planning
  into classical / probabilistic / motion; evolutionary into GA / GP / ES /
  swarm; ensembles into bagging / boosting / stacking). They stay leaves because
  `RATIONALE.md` §6 already declares several of them the thinnest nodes on the
  axis, kept on external breadth rather than on anything observed, and adding
  depth-3 precision beneath a node kept on breadth alone asserts a resolution
  the axis cannot carry. **Re-derive these first if a later extraction makes
  them large** — `Ensemble methods` and `Planning` are the two I would open next.
- **Model-analysis and learning-theory leaves** — `Formal verification`,
  `Uncertainty quantification`, `Generalization`, `Sample complexity`,
  `Expressivity`, `Training dynamics`, `Scaling behaviour`. These are
  question-sized already: that was the M6 fix. Splitting `Generalization` into
  in-distribution / out-of-distribution, or `Uncertainty quantification` into
  Bayesian / conformal / ensemble, would put a *method* set under a *claim*
  parent — M1 one level down.
- **Data curation leaves** — `Data synthesis`, `Data selection`, `Annotation`.
  The M7 fix set their principle as which part of the training set is acted on;
  one level down, `Data selection`'s candidates (active learning, curriculum,
  filtering, weighting) divide by *what decides the selection*, which is a
  second principle, and active learning would straddle it.
- **The administrative rows** — `Generic field names`, `Generic technique
  names`. Excluded from shares; depth here would be meaningless.

## 17. Phase-1 self-audit, before any corpus contact

Sibling sets I am **not** confident in, declared now so phase 2 cannot be
mistaken for having found them:

1. `Multi-agent reinforcement learning` as a signal source (§1.6) — the honest
   reading is that MARL divides by *how many agents there are*, and I admitted it
   under "the signal is jointly produced by co-learners", which is a rescue.
2. `Continual learning`'s scenario children (§12) — the rejected mechanism
   taxonomy is the one the field actually uses in surveys.
3. `Optimization` at two children (§3) — principled, but a report gets almost
   nothing from it.
4. `Autoregressive models` vs `Graphical models` (§4) — an autoregressive
   factorisation *is* a graphical-model factorisation over a complete DAG; two
   traditions, one mathematics.
5. `Masked prediction` vs `Next-element prediction` (§5) — both withhold part of
   the input; only *which* part differs.
6. `Implicit-depth architectures` (§2.7) — expected to be the thinnest node I
   add.
7. `Inference procedures`' children (§15) — inherit a declared parent strain.

Expected branching: RL 6 · neural architectures 7 · optimization 2 · generative
models 7 · self-supervised 5 · probabilistic inference 5 · transfer 2 ·
interpretability 4 · model efficiency 4 · adversarial ML 3 · meta-learning 3 ·
continual 3 · causal 3 · game theory 4 · inference procedures 3 = **61 level-3
nodes under 15 parents**.
