# Pinning report — region `rl` (197 nodes)

Written against `role/nodes.tsv`, `signal/nodes.tsv`, `attributes/nodes.tsv` and
`phase1/DRAFT_PHASE1_A.md` only. Output: `pinning/rl.pinned.tsv`.

## Counts

| axis | values written | rows with a pin | rows with **no resolved value** after inheritance |
|---|---|---|---|
| `signal` | 123 | 77 | 2 (`L.mbrl`, `L.mbrl.plan`) |
| `role` | 75 | 60 | **20** |
| `attributes` | 345 | 127 | 0 |

Pins are written **only where they add to or contradict the inherited set**, per
rule 1 ("a blank is how inheritance is expressed"). 46 rows are intentionally
blank because every value they take is already pinned by an ancestor — `M.ppo`,
`M.qmix`, `M.sarsa`, `M.double-dqn` are all in that set and that is the correct
result, not a gap. The genuinely unpinnable rows are listed separately below.

Attribute-family reach after inheritance (of 197 nodes): `A.hier` 173, `A.param`
158, `A.agents` 153, `A.deriv` 152, `A.cadence` 144, `A.regime` 136, `A.world`
131, `A.rltarget` 115, `A.outspace` 105, `A.determinism` 65, `A.guar` 31,
`A.exec` 15, `A.uncert` 14, `A.topology` 7, `A.exact` 5.

### Pinning policy I applied (so the table is auditable)

- Where **one** descendant deviates from an otherwise uniform family, I pinned at
  the family and used a **negative pin** on the deviant (rule 2). Where a family
  genuinely splits, I left the cell blank (rule 1). Blanks for genuine splits are
  listed below; without that distinction the table loses most of its information.
- `A.determinism` (scope "to any procedure") and `A.uncert` (scope "to any
  estimator") are pinned only where the value is characteristic of the method,
  not on all 197 nodes. See "doubts" — their scopes make them unfalsifiable.
- I treated rule 1 as applying along `derives-from` and in-region `divides`
  edges, **not** along cross-region attachment edges. This is a decision, not a
  reading of the rules, and it is the first finding below.

---

## 1. Rule 1 fails on the two edges that leave this region

Two in-region family nodes have a descendant from another region, and under a
literal reading of rule 1 those descendants empty the parent:

- **`L.pg` → `L.nas.rl`** (parents `L.nas; L.pg`). `INSTRUCTIONS.md` uses
  "`L.pg` can pin `R.fit.obj` and `S.form.return`" as the canonical correct
  example. In the actual table it cannot: `L.nas.rl`'s role is `R.search.arch`,
  and its "reward" is a validation metric, not environment feedback.
- **`L.bandit.bai` → `L.hpo.bandit`** (Hyperband/ASHA/PBT). The bandit families
  would have to drop `R.exp.act`, `S.src.env.reward` and `A.regime.*`, because
  an HPO scheduler pulls trials, not arms.

I pinned the parents anyway and absorbed the difference at the child, because the
alternative erases the two most aggregable family nodes in the region. **This
needs a ruling**: rule 1 is only well-defined once the two edge types
SYNTHESIS §4 already flagged (`derives-from` vs `instantiates`) are separated,
and inheritance is declared to run along one of them. Every other multi-parent
node in the region (`M.spr`, `M.thompson-sampling`, `M.viterbi`, `M.cem-mpc`,
`M.bohb`, `M.redq`) is harmless because the out-of-region parent adds rather than
contradicts.

## 2. The six RL-scoped families: what the pinning pass actually found

This region is where `A.regime`, `A.world`, `A.rltarget`, `A.hier`, `A.agents`
and `A.exec` apply, so it is the test of their scope predicates. Three of the six
have a structural defect, and it is the same defect in each case.

### 2a. The families are flat, so no family node can pin them (the big one)

`S.src` has internal nodes (`S.src.env`, `S.src.self`), which is what let me pin
`L.pg` with `S.src.env` and let `L.pg.trust.grpo` specialise it to
`S.src.env.verifier` without a contradiction. **Every `A.*` family is two levels
with no internal node**, so a family node whose descendants differ in detail but
agree in kind has nothing to pin and must go blank. Concretely:

- **`A.world` cannot be pinned on `L.mbrl`.** `L.mbrl.search` holds AlphaZero
  (`A.world.given`, per the family's own examples) and MuZero
  (`A.world.learned`); `L.mbrl.plan` holds CEM-MPC/MPPI/iCEM, which require *a*
  model but specify neither kind. So the family named "Model-based RL" has a
  blank cell in the family that exists to express model-based-ness, and
  "proportion of model-based papers" cannot be answered by `A.world` at the
  family level. **Needs `A.world.model`** as an internal parent of `learned` and
  `given`.
- **`A.agents` cannot be pinned on `L.marl`.** `factor`/`ctde` are cooperative,
  `game` is competitive, `indep` is agnostic. There is no "several learning
  agents, alignment unspecified" value, so the multi-agent family is blank on the
  multi-agent attribute. **Needs `A.agents.multi`.**
- **`A.rltarget` cannot be pinned on `L.pg`** (REINFORCE is `policy`, A2C is
  `ac`) **or on `L.dp`** (value iteration is `value`, policy iteration keeps an
  explicit policy table). There is no "parameterises a policy" value covering
  `policy`+`ac`, and no "learns a value" value covering `value`+`ac`.

### 2b. `A.rltarget.ac` is a conjunction masquerading as a sibling

`A.rltarget.ac` ("parameterises both a policy and a learned value estimate") is
the logical AND of its two siblings, so the family is not a partition of
independent properties. Two consequences I hit:

- **`M.policy-iteration` resolves to `A.rltarget.ac`.** Tabular policy iteration
  does maintain both a policy and a value, so the positive test passes, and the
  node now says "actor-critic". This is the MLP-Mixer→self-attention failure from
  the models dimension, reached through a positive test rather than through
  inheritance, so a negative pin cannot fix it.
- **Planning-only control has no value at all.** PlaNet, PETS, CEM-MPC, MPPI and
  iCEM parameterise neither a policy nor a value; the controller is derived from
  the model by search at each step. I negative-pinned `!A.rltarget.ac` on
  `M.planet` and left the family blank. `A.rltarget` is in scope (these are
  control procedures) and has no admissible value.

**Recommendation:** replace `A.rltarget`'s three values with two independent
flags (`parameterises a policy`, `learns a value function`), which makes
actor-critic the conjunction, policy-iteration the same conjunction without the
misleading name, and planning the empty conjunction.

### 2c. `A.regime` is vacuous for pure-exploration procedures

Its characteristic is "relation between the policy being improved and the policy
that produced the data". Best-arm identification (`L.bandit.bai`: LUCB, racing,
successive/sequential halving) and budget-allocation HPO (`L.hpo.bandit`) are
inside the scope — they learn from interaction — and **improve no policy**, so
none of `on`/`off`/`offline` is true and the family is blank for all nine nodes.
This is a scope predicate that admits nodes it has no value for, which is the
failure mode rule 3 exists to prevent.

Second, smaller problem: the scope reads "when the procedure learns from
interaction data", which on a literal reading excludes offline RL — yet
`A.regime.offline` exists for exactly that. Scope should read "learns from data
produced by acting in an environment, whether collected by this run or logged".

### 2d. `A.hier` and `A.exec` do not earn family status in this region

- `A.hier` resolves on 173 of 197 nodes and takes `hier` on exactly six:
  `L.hrl` and its five methods. It is 1-to-1 with membership in `L.hrl`, so it
  costs 173 pins to encode one lineage fact.
- `A.exec` resolves on 15 nodes, all of them under `L.marl`, and is 1-to-1 with
  `L.marl.indep` (`decen`) vs `L.marl.factor`/`L.marl.ctde` (`ctde`).
  `A.exec.central` is used by nothing in the region.

Both are candidates for demotion to a note on the lineage family. Against
demotion: option-style abstraction and CTDE do appear outside those families in
the wild. Worth deciding deliberately rather than by default.

Separately, **`A.exec`'s scope says "multi-agent *or partially observed*
control", but all three of its values are multi-agent-shaped.** A single-agent
recurrent method for a POMDP (`M.r2d2`, recurrent PPO) is admitted by the scope
and has no value: `A.exec.decen` ("no global information is used at any stage")
is a statement about other agents, not about history. Either drop "partially
observed" from the scope or add a value for it.

## 3. Rule 4 — the signal axis and methods that learn from more than reward

The task asked specifically whether signal can express "reward **and**
agreement". **It can, but only as two unordered sets, and that loses the
pairing.**

`M.spr` resolves to source `{S.src.env.reward, S.src.self.own, S.src.self.next}`
× form `{S.form.return, S.form.agree}`. The true content is two objective terms:
(reward, return) and (self-prediction, agreement). The pinned cell also licenses
(reward, agreement) and (self-prediction, return), neither of which exists.
Same shape on `M.efficientzero` (self-supervised consistency loss on top of
MuZero), `M.sr-spr`, `M.bbf`, `M.td-mpc` (latent consistency + return) and
`M.drq` (`S.src.self.view` + `S.form.inv` on top of the TD loss).

**This is the single change I would make to the signal axis**: make a signal pin
a *pair* — one `(S.src.*, S.form.*)` per objective term, multi-valued at the pin
level — instead of two independent multi-valued sub-facets. The sub-facet split
itself is right (SimCLR/BYOL still needs it); it is the flattening into two sets
that is lossy, and it is lossy exactly on the methods that combine an RL term
with a representation term. `M.cql` is a third case in the other direction: its
conservative penalty is a genuine `S.form.contrast` term (explicit negatives:
OOD action values pushed down, dataset action values pushed up) sitting on the
same source as its `S.form.return` term.

I did **not** need to leave any of these blank, so none is "homeless" — but the
pin is weaker than the truth, which rule 4 does not have a category for.

## 4. Homeless nodes

Grouped by the axis value that was needed and did not exist. Nothing below was
force-pinned; every one of these cells is blank in `rl.pinned.tsv`.

### H1. `S.src` — reward from a specified MDP (no acting)
`L.dp`, `M.value-iteration`, `M.policy-iteration`, `M.asynchronous-dp`,
`M.generalised-policy-iteration`. `S.src.env`'s test is "feedback returned after
the system acted"; dynamic programming never acts — the reward function is part
of the problem statement. `S.src.env.reward`'s test ("an external environment or
simulator *emits* the scalar") also fails. I pinned only `S.src.self.own` (the
bootstrap) on `L.dp`, so the reward half of DP's signal is unrecorded.

### H2. `S.src` — a measured performance number from an inner run
`L.nas.rl`, `M.nasnet-zoph-le`, `M.enas`, `M.metaqnn`, `L.hpo.bandit`,
`M.hyperband`, `M.asha`, `M.pbt`, `M.bohb`, `M.successive-halving`. The reward is
validation accuracy from a child run. Not `env.reward` (no environment), not
`env.verifier` (not a correctness check), not `env.rm` (not fitted on
judgements), not `env.intr`. The whole configuration-search branch's signal
source is unexpressible; I left `S.src` blank on all ten and pinned only
`S.form.return` where the outer loop is a policy gradient.

### H3. `S.src` — actions logged from an arbitrary behaviour policy
`L.orl.seq` and all four of its methods (`M.decision-transformer`,
`M.trajectory-transformer`, `M.rvs`, `M.multi-game-dt`), plus the BC term in
`L.orl.polcon` (`M.td3-plusbc`) and the weighted regression in `L.orl.implicit`.
The target is the dataset's own action. `S.src.ext.demo` requires "an action
sequence produced by an **expert**", which is precisely what offline RL assumes
it does *not* have. `S.src.self.own` is wrong (it is another policy's output, not
the learner's). `L.orl.seq`'s own `notes` column already says "signal is a label,
not a reward, despite being RL" — this is that note, confirmed, with no value to
write.

### H4. `S.src` — reward emitted by another component of the same system
`L.hrl`, `M.feudal-networks`, `M.hiro`, `M.hac`, `M.option-critic`. The
low-level policy's reward is a subgoal-reaching signal produced by the manager
inside the same run. `S.src.env.intr` is "prediction error, novelty or counts" —
not goal-reaching. `S.src.env.rm` is a model fitted on external judgements. The
family that `A.hier` was built for cannot state where its inner reward comes
from.

### H5. `S.form` — quantile / distributional regression
`L.dqn.dist` for the quantile branch: `M.qr-dqn`, `M.iqn`, `M.fqf`. The only
place pinball loss appears is `S.form.cover`, whose positive test is "targets a
stated frequency guarantee on a held-out distribution" — distributional RL has
the loss shape and makes no coverage claim. I pinned `S.form.lik` on `M.c51`
(categorical cross-entropy, clean) and left the quantile three blank.
Relatedly, distributional value learning has **no `A.uncert` value**: it returns
a distribution over the *return*, which is aleatoric; `A.uncert` is about the
estimator's own uncertainty, and `A.uncert.point` ("no dispersion") is false.

### H6. `S.form` — plain regression to a supplied target
`M.td3-plusbc`, `M.awr`, `M.awac`, `M.fqe`'s regression term. MSE/Huber onto a
given value is not `S.form.lik` ("normalised log-probability the model can
compute exactly") and not `S.form.recon` (not the input). I pinned `S.form.lik`
on the cross-entropy cases (`L.orl.seq`, `M.td3-plusbc`) under protest; see
"doubts".

### H7. `R.*` — gradient-free fixed-point computation of the learned object
`L.dp`, `M.value-iteration`, `M.policy-iteration`, `M.asynchronous-dp`,
`M.generalised-policy-iteration`; also `M.cfr`, `M.fictitious-play`,
`M.regret-matching`, `M.nash-q` (which inherit `R.fit.obj` from `L.marl` only by
accident of the family pin), and `M.sinkhorn`/`M.sinkhorn-knopp`/`M.entropic-ot`.
`R.fit.update`'s positive test is "maps a **gradient** and optimiser state to a
parameter change"; a Bellman sweep, a regret-matching update and a matrix-scaling
iteration have no gradient. `R.fit.est` is about estimating an intractable
expectation. Twenty nodes resolve to **no role at all**, and this is the largest
group in them.

### H8. `R.*` — mid-training parameter reset
`M.sr-spr`, `M.bbf`. Their named contribution is periodically reinitialising part
of the network during training. `R.fit.init`'s negative test is explicitly
"changes parameters after updates have begun". `R.fit.scope` decides eligibility,
not values; `R.rewrite.*` is post-fitting. No slot.

### H9. `A.guar` — exact optimality
`M.hungarian-algorithm`, `M.branch-and-bound`, `M.mixed-integer-programming`,
`M.constraint-programming`, `M.sat-based-learning`, `M.viterbi`, `M.auction-algorithm`.
`A.guar.approx` is "a **bounded ratio** to the optimum"; these return the
optimum. An exact solver's guarantee is the strongest in the family and has no
value.

### H10. `A.guar` — sample complexity / fixed-confidence PAC
`M.lucb`, `M.racing`, `M.sequential-halving`, `M.successive-halving`,
`M.hyperband`, `M.asha`. Best-arm identification's theorem bounds the number of
pulls to be correct with probability 1−δ. Not `regret` (not cumulative), not
`conv` (not an optimisation property), not `consist` (not asymptotic in n).

### H11. `A.agents` — a non-learning adversarial environment
`L.bandit.adv`, `M.exp3`, `M.exp4`, `M.tsallis-inf`. `A.agents.single` says "one
policy interacts with a **stationary** environment", which adversarial bandits
explicitly deny; `A.agents.comp` requires another agent with opposed rewards,
and the adversary here is a sequence, not a learner. I left `A.agents` blank on
the whole adversarial-bandit branch.

### H12. `A.deriv` — contraction / fixed-point updates
Same node set as H7, plus `L.optdisc.ot` (Sinkhorn is iterative matrix scaling,
not combinatorial search and not gradient descent) and tabular TD
(`M.td-0`, `M.td-lambda`, `M.q-learning`, `M.sarsa`, `M.true-online-td`, whose
semi-gradient step is not the gradient of any fixed objective). I left `A.deriv`
blank on `L.dp`, `L.td`, `L.td.q`, `L.td.sarsa` and `L.optdisc.ot`; it is pinned
`first` only from `L.dqn` down.

### H13. `A.param` — the output is a configuration or an architecture
`L.hpo.bandit` and its five methods, `L.nas.rl` and its three. `A.param.param`
is "a fixed-size parameter set runnable on new inputs"; a hyperparameter
configuration or an architecture description is neither that, nor stored training
data, nor transductive.

### H14. `A.cadence` — updates per datum
`L.dqn.eff` (DrQ, SPR, SR-SPR, BBF, REDQ). The family's defining property is
"raises updates-per-environment-step". `A.cadence` measures data per update, the
reciprocal of the family's own axis of variation. Minor, but it means the family
node's content is invisible on every axis.

## 5. Proposed new axis values

Proposals only; not added to the tables.

| id | name | parent | positive_test | needed by |
|---|---|---|---|---|
| `S.src.env.spec` | Specified reward function | `S.src.env` | the scalar being maximised is given analytically as part of the problem specification, with no acting | H1 (5 nodes) |
| `S.src.env.metric` | Measured performance of an inner run | `S.src.env` | the reward is a performance number measured by training and evaluating a configuration the procedure proposed | H2 (10 nodes) |
| `S.src.ext.behav` | Logged behaviour | `S.src.ext` | the target is an action taken by a previous policy of unknown quality, read from a log | H3 (7+ nodes) |
| `S.src.env.internal` | Reward from another component of the same system | `S.src.env` | the scalar is emitted by a manager, goal generator or termination function trained in the same run | H4 (5 nodes) |
| `S.form.quant` | Quantile regression | `S.form` | regresses a set of quantiles of the target distribution under an asymmetric (pinball) loss, with no coverage claim | H5 (3 nodes) |
| `S.form.reg` | Regression to a supplied target | `S.form` | penalises a distance to a target value supplied from outside the model, with no probabilistic normalisation | H6 (4+ nodes) |
| `R.fit.fixpoint` | Fixed-point computation of the learned object | `R.fit` | produces the learned object by iterating an operator to convergence, with no gradient and no closed form | H7 (12 nodes) |
| `R.fit.reset` | Mid-training reinitialisation | `R.fit` | reinitialises part of the parameter set after updates have begun, as a declared part of the procedure | H8 (2 nodes) |
| `A.guar.optimal` | Exact optimality | `A.guar` | returns a provably optimal solution to the stated combinatorial problem | H9 (7 nodes) |
| `A.guar.sample` | Sample-complexity / PAC bound | `A.guar` | bounds the number of samples or pulls needed to be correct with probability 1−δ | H10 (6 nodes) |
| `A.agents.adv` | Adversarial non-learning environment | `A.agents` | the reward sequence may be chosen adversarially, by something that is not itself a learning agent | H11 (4 nodes) |
| `A.deriv.fixpoint` | Contraction / fixed-point step | `A.deriv` | the step applies a contraction or averaging operator toward a bootstrapped or constraint-satisfying target, consuming no derivative of a fixed objective | H12 (11 nodes) |
| `A.world.model` | Model-based (internal node) | `A.world` | a dynamics or reward model is available to the procedure, from either source | 2a |
| `A.agents.multi` | Multi-agent (internal node) | `A.agents` | two or more learning agents interact, alignment of interests unspecified | 2a |
| `A.rltarget.*` | — | — | restructure as two independent flags rather than three values | 2b |

## 6. Multi-value families (rule 5)

Seven nodes resolve to two values in one family. All seven are genuine; none is a
resolution accident.

| family | node | values | why |
|---|---|---|---|
| `A.deriv` | `M.trpo`, `M.natural-policy-gradient` | `first` + `second` | the policy gradient is first-order, the Fisher preconditioner is curvature. Dropping either loses the method's content. |
| `A.deriv` | `M.planet`, `M.td-mpc` | `first` + `zero` | the world model is fitted by gradient descent, the controller is a zeroth-order sampler (CEM/MPPI). Two different step rules in one named method. |
| `A.deriv` | `M.trajectory-transformer` | `first` + `comb` | trained by gradient, acts by beam search over the trajectory model. |
| `A.agents` | `M.muzero` | `single` + `comp` | published simultaneously on Atari (single agent) and Go/chess/shogi (two-player zero-sum). This one is a property of the *instance*, not the method — A's tension 10 reaching `A.agents`. |
| `A.guar` | `M.exp3` | `regret` + `unbias` | the regret bound is the headline; the importance-weighted loss estimator being unbiased is what makes the proof work. |

`A.deriv` carries five of the seven, which reproduces A's finding from NUTS:
`A.deriv` is not a single-valued family and should be declared multi-valued.
Nothing else needed two values, so I would **not** make the other families
multi-valued on this region's evidence — except `A.agents`, and only because of
instance-vs-method variation, which is a different problem and should be fixed by
marking the node rather than by raising cardinality.

## 7. Negative pins used (24)

| node | pin | denying |
|---|---|---|
| `L.pg.trust.grpo` | `!S.src.self.own`, `!A.rltarget.ac` | `L.pg.ac`'s critic. GRPO's whole point is replacing the learned critic with a group baseline, so it bootstraps from nothing and parameterises no value. Positive: `A.rltarget.policy`. |
| `L.orl.seq` | `!S.form.return` | `L.orl`'s expected-return form. Return-conditioned sequence modelling does no temporal credit assignment; the return is an input, not a maximand. Positive: `S.form.lik`. |
| `L.optdisc.submod`, `M.swav-assignment-step` | `!S.src.none`, `!S.form.none` | `L.optdisc`'s "a solver fits nothing". Coreset selection does minimise a dataset-level geometric objective. Positives: `S.src.self.struct`, `S.form.dist`. |
| `M.wasserstein-distance`, `M.gromov-wasserstein`, `M.entropic-ot` | `!S.form.none` | same; these are used *as objectives*. Positive: `S.form.dist`. |
| `M.awac`, `M.awr` | `!A.regime.offline` → `A.regime.off` | `L.orl`'s offline constraint. Both papers fine-tune online from an offline dataset. Instance-dependent; see doubts. |
| `M.combo`, `M.trajectory-transformer` | `!A.world.free` → `A.world.learned` | `L.orl`'s model-free pin. COMBO is model-based offline RL; TT models states as well as actions. |
| `M.redq` | `!A.rltarget.value`, `!A.outspace.disc` → `ac`, `cont` | `L.dqn`/`L.td.q`. REDQ sits under `L.dqn.eff` but is a continuous-action actor-critic. This pair is the clearest demonstration that rule 2 is load-bearing: without it REDQ resolves to "discrete-action value-based", which is false on both counts. |
| `M.sampled-muzero` | `!A.outspace.disc` → `cont` | `L.mbrl.search`'s discrete tree search; the whole contribution is continuous action spaces. |
| `M.metaqnn` | `!A.rltarget.policy` → `value`, `!A.regime.on` → `off` | `L.nas.rl`'s controller policy. MetaQNN's controller is Q-learning with replay. |
| `M.pilco` | `!R.out.search`, `!A.deriv.zero` → `R.fit.obj`, `A.deriv.first` | `L.mbrl.plan`'s re-planning sampler. PILCO optimises a policy analytically through a GP model; it does not re-plan at each step. It is arguably misfiled under `L.mbrl.plan`. |
| `M.planet`, `M.world-models` | `!A.rltarget.ac` | `L.mbrl.latent`'s actor-critic. PlaNet plans (no policy, no value); World Models evolves a linear controller. |
| `M.world-models` | `!A.deriv.first` → `zero` | CMA-ES on the controller. |
| `M.fictitious-play`, `M.regret-matching` | `!S.form.return` | `L.marl`'s expected-return form. Both are normal-form equilibrium procedures with no temporal structure. |
| `M.dyna`, `M.dyna-q` | `!A.cadence.mini` → `one` | `L.mbrl.dyna`'s minibatch pin (set for MBPO/SLBO); tabular Dyna updates per transition. |

## 8. Nodes I could not pin at all

**20 nodes resolve to no role**, in three groups:

1. *Gradient-free fixed-point control* (H7): `L.dp`, `M.value-iteration`,
   `M.policy-iteration`, `M.asynchronous-dp`, `M.generalised-policy-iteration`.
   Real procedures, no slot.
2. *Solvers whose role depends on what they are used for*: `L.optdisc`,
   `L.optdisc.ot`, `L.optdisc.exact`, `M.sinkhorn`, `M.sinkhorn-knopp`,
   `M.entropic-ot`, `M.branch-and-bound`, `M.mixed-integer-programming`,
   `M.constraint-programming`, `M.sat-based-learning`. Hungarian matching is
   `R.fit.obj` in DETR and `R.data.label` in SwAV; branch-and-bound is
   `R.fit.update` in exact tree learning and `R.eval` in verification. The role
   is a property of the use, which is what role is supposed to exclude — the
   `t-SNE` problem from A's worked examples, but for ten nodes instead of one.
3. *Family nodes whose children span slots*: `L.bandit` (its children occupy
   `R.exp.act`, `R.eval`, `R.search.hp`, `R.fit.stop`), `L.bandit.bai`,
   `L.mbrl` (model *learning* vs model *use*).

Nodes that are **descriptions rather than named procedures** (the `notes` review
flag, confirmed from the pinning side — each is a formalism, a paradigm or a
quantity, and that is why it would not pin):

- `M.options-framework`, `M.generalised-policy-iteration`,
  `M.pessimistic-mdps`, `M.soft-actor-critic-variants`, `M.constraint-programming`,
  `M.mixed-integer-programming`, `M.sat-based-learning` — formalisms/classes, not
  procedures.
- `M.wasserstein-distance`, `M.gromov-wasserstein` — **quantities, not
  procedures.** SYNTHESIS §3 rules that "a quantity that *is* the number is a
  different kind of entity"; by that ruling these two should not be lineage nodes
  at all (the *procedures* are Sinkhorn-Knopp and the exact OT solvers, which are
  separately present).
- `M.facility-location-coresets`, `M.greedy-maximum-coverage`, `M.k-center-greedy`,
  `M.racing` — descriptive, but each does name a specific algorithm; they pin
  fine through `L.optdisc.submod`/`L.bandit.bai`. I would keep them.
- `M.branch-and-bound`, `M.auction-algorithm`, `M.hungarian-matching`,
  `M.beam-search-as-search`, `M.regret-matching`, `M.fictitious-play`,
  `M.policy-iteration`, `M.value-iteration`, `M.natural-policy-gradient`,
  `M.successive-halving`, `M.sequential-halving` — genuinely named procedures
  despite the lowercase string. Keep.

**`M.iql` is unpinnable for a different reason: it is two methods.** Its parents
are `L.orl.implicit; L.marl.indep`, and IQL is both *Implicit* Q-Learning
(offline, actor-critic, continuous actions, expectile regression) and
*Independent* Q-Learning (multi-agent, decentralised, value-based, discrete).
Every axis would need contradictory values. This is a vocabulary collision, not a
multi-parent node, and it must be split into two nodes before annotation — note
that `L.marl.indep`'s own `examples` column lists "IQL" meaning the second one.

Duplicate nodes found while pinning (each pair/triple pins identically, so the
counts will double-count): `M.ppo` / `M.ppo-clip`; `M.hungarian-algorithm` /
`M.hungarian-matching` / `M.detr-bipartite-matching`; `M.sinkhorn` /
`M.sinkhorn-knopp`; `M.expected-sarsa` / `M.expected-sarsa-off-policy-form` (one
procedure split across two parents by a parenthetical); `M.actor-critic`
duplicates its own family `L.pg.ac`; `M.successive-halving` appears under
`L.hpo.bandit` while `L.bandit.bai` lists it as an example too.

## 9. Anything that made me doubt an axis

1. **`L.optdisc` is an attribute, not a lineage family.** Its five children and
   fifteen methods share exactly one thing: `A.deriv.comb` (and even that fails
   for the OT branch). They share no role, no signal and no lineage. The family's
   entire content is already a value on another axis. This is the strongest
   candidate in the region for a family that should not exist; the alternative
   reading is that it is a legitimate "technique applied across slots" family,
   which is A's tension 11 (`instantiates` edges) in a second guise.
2. **`A.determinism` (scope "to any procedure") and `A.uncert` (scope "to any
   estimator") are unfalsifiable as written.** Every one of my 197 nodes is in
   scope for `A.determinism`, and almost all would be `stoch` (exploration plus
   minibatch sampling), so the family carries ~1 bit that nobody would query. I
   pinned it on 65 nodes where it is characteristic and left the rest blank —
   which makes the blank mean "not characteristic", a third meaning on top of the
   two (not-applicable, not-annotated) that A's tension 12 already identified.
   Either these families need a real applicability predicate or they need an
   explicit `n.a.` value; as it stands they cannot be aggregated.
3. **`R.exp` has no slot for model-generated experience.** Dyna/MBPO synthesise
   transitions from a learned model: not acting (`R.exp.act`), not replaying past
   interaction (`R.exp.store`), not choosing a task (`R.exp.task`). I pinned
   `R.data.synth`, which is defensible ("creates training examples that did not
   exist before") but files the defining mechanism of model-based RL under data
   preparation. `R.exp.sim` would be cleaner.
4. **`L.mbrl.plan` crosses a role boundary inside one family**, exactly like
   DDPM→DDIM. PILCO and PETS *learn* a model (`R.fit.obj`); CEM-MPC, MPPI and
   iCEM *use* one (`R.out.search`) and have no training signal at all
   (`S.src.none`/`S.form.none`). That is why `L.mbrl` and `L.mbrl.plan` are the
   only two nodes in the region with no resolved signal. If role-crossing edges
   are allowed (and SYNTHESIS says they must be), then family-level pinning is
   structurally weak and the pass should expect blanks at exactly these nodes.
5. **GRPO's credit-assignment granularity is invisible.** GRPO/RLOO/DAPO assign
   one reward to a whole completion with no per-token signal — they are
   contextual bandits over sequences wearing policy-gradient clothes. Nothing on
   any of the four axes distinguishes that from PPO's per-step rewards, and this
   is the region's highest-volume recent branch (`L.pg.trust.grpo`'s own note
   says so). Either `A.*` needs a credit-assignment-granularity family or these
   nodes want a second lineage parent under `L.bandit`.
6. **`S.form.lik` is absorbing every regression loss.** I pinned it on
   `M.td3-plusbc`, `M.linucb`, `M.lints`, `L.orl.implicit` and `L.orl.seq`. For
   cross-entropy that is right; for MSE-to-a-logged-action it is "Gaussian MLE",
   which is true and uninformative. With `S.form.reg` (H6/§5) the offline-RL
   branch would separate cleanly into behaviour-regression vs value-regression.
7. **`A.regime` on `M.awac`/`M.awr` is instance-dependent**, not method-
   dependent: both papers run offline-only and offline-then-online. I used
   negative pins to record the online variant, but a cleaner answer is to mark
   these nodes the way A's tension 10 proposes for instruction tuning.
8. Two lineage repairs the pinning pass suggests: `M.rainbow` should also be a
   child of `L.dqn.dist` (its distributional loss is one of the six bundled
   components, and roll-ups under `L.dqn.dist` currently miss the most-cited
   distributional method); `M.munchausen-dqn` should also be a child of
   `L.maxent` (its log-policy term is the maxent objective, which is why it
   pins `S.form.conf`); `M.facmac` should also be a child of `L.marl.factor`.

---

## The three findings that matter most

1. **Every `A.*` family is flat, so no family node can pin a scoped attribute.**
   `L.mbrl` cannot pin `A.world`, `L.marl` cannot pin `A.agents`, `L.pg` and
   `L.dp` cannot pin `A.rltarget`. Signal survives the same test only because it
   has internal nodes (`S.src.env`) to pin. Fix: add `A.world.model` and
   `A.agents.multi`, and split `A.rltarget` into two flags — which also removes
   the `M.policy-iteration` → "actor-critic" mis-resolution and gives
   planning-only control (PlaNet, PETS, CEM-MPC) a value for the first time.
2. **Signal's two sub-facets are two sets, and the pairing between them is lost
   exactly on the methods the task asked about.** SPR, EfficientZero, TD-MPC,
   DrQ and CQL each have two objective terms; the axis says "sources {a,b,c},
   forms {x,y}" and licenses four combinations where two exist. Pin
   `(source, form)` pairs, one per objective term.
3. **Twenty nodes have no role.** Two causes worth separating: gradient-free
   fixed-point computation (dynamic programming, CFR, Sinkhorn — `R.fit` assumes
   a gradient or a closed form, needs `R.fit.fixpoint`), and combinatorial
   solvers whose slot is a property of their use, not of the procedure
   (`L.optdisc`, ten nodes). Also in this group: mid-training resets (SR-SPR,
   BBF) are excluded by `R.fit.init`'s negative test by name.
