# Pinning report — region `opt` (308 nodes)

Covers stochastic first-order descent, per-coordinate adaptive methods, matrix
preconditioning, schedules, gradient post-processing, variance reduction,
proximal methods, initialisation, stopping, explicit regularisation,
derivative-free optimisation, data-parallel training, model-state sharding,
federated learning, privacy-preserving training, memory-compute trade-offs,
operator-level execution, and weight averaging/merging.

62 family (`L.*`) nodes, 246 method (`M.*`) nodes.

## Coverage

Pins are written where they are *first true*; a blank means "inherits"
(rule 1). Numbers below are therefore given twice.

| axis | nodes with an explicit pin | nodes with a resolved value after inheritance |
|---|---|---|
| signal | 46 | 305 / 308 (`S.src` 302, `S.form` 300) |
| role | 76 | 297 / 308 |
| attributes | 108 | 287 / 308 |

Attribute families actually exercised, by resolved node count:

```
A.deriv 165   A.cadence 143   A.determinism 109   A.datalocality 83
A.exact  81   A.topology  75   A.guar        55   A.privacy   19
A.agents 13   A.world     13   A.regime      13   A.rltarget  12   A.uncert 1
```

Nine of the seventeen families take **no value anywhere in this region**:
`A.hier`, `A.exec`, `A.outspace`, `A.param`, plus the four control families are
near-empty and `A.uncert` fires once. That is the expected shape, but see
"Axes I doubt" on `A.param`.

**Signal-agnosticism is confirmed, not assumed.** `S.src.none` resolves on
279/308 nodes (91%) and `S.form.none` on 268/308 (87%). The 29 nodes that carry
a real target source are: the trust-region policy-gradient subtree (11), the
consistency-regularisation subtree (7), the norm-penalty subtree (`S.form.spars`,
7), plus `M.confidence-penalty`, `M.temperature-softened-targets`, `M.pate`,
`M.openai-es`, `M.augmented-random-search`, `M.gradient-penalty`,
`M.jacobian-hessian-penalties`, `M.mean-teacher`, `M.load-balancing-losses`.
Every one of those is a borderline resident of this region (an RL objective, an
SSL objective, a KD knob, a privacy method whose content is label production).
Strip them and the region is 100% `none/none`. The single-tree conclusion holds
with room to spare: signal cannot divide this region at all.

---

## Homeless nodes

### H1. `L.reg.act` — stochastic activation regularisation has no `role` slot (6 nodes + family)

`M.dropout`, `M.dropconnect`, `M.stochastic-depth`, `M.dropblock`,
`M.droppath`, `M.layerdrop`. Role left blank; these are the only nodes in the
region with no resolvable role at all.

They are not `R.fit.obj` (they add no term to the scalar), not `R.fit.grad`
(they act in the forward pass, before a gradient exists), not `R.fit.scope`
(they do not decide which parameters are *eligible to change* — all parameters
remain eligible; they decide which units are *active on this example*), not
`R.data.aug` (they perturb the model, not the example). `R.fit.est` is the only
near miss and it is about estimating an intractable expectation.

Value needed: a `R.fit` child for **training-time perturbation of the model's
own computation**. See P1.

### H2. `L.reg.geom` — sharpness/curvature penalties have no `S.form` value (4 nodes)

`M.sam`, `M.asam`, `M.gsam`, and the family `L.reg.geom`. `S.form` left blank.

SAM's criterion is `max_{||e||<r} L(w+e)` — a property of the loss surface in
*weight* space. `S.form.spars` is about the number/magnitude of components;
`S.form.inv` is about variation "under a declared nuisance transformation" of
the data, which a weight perturbation is not; `S.form.game` wants two optimisers
with opposed objectives and SAM's inner max is a closed-form single ascent step
on the same objective. I did pin `S.form.inv` on `M.gradient-penalty` and
`M.jacobian-hessian-penalties`, where the penalised derivative is w.r.t. the
*input* and the robustness reading is honest; the three SAM variants have no
value. See P2.

### H3. `L.priv.unlearn` — removing an example's influence has no `role` child (5 nodes)

`L.priv.unlearn`, `M.certified-removal`, `M.influence-function-unlearning`
(plus `M.sisa`, `M.exact-retraining-shards`, which escape differently).

I pinned the **interior** node `R.rewrite` with no child, which encodes
"parameter-space rewriting, none of the four listed kinds". None of
`R.rewrite.sparse` / `.precision` / `.factor` / `.combine` fits: unlearning
removes nothing structural, requantises nothing, factors nothing and combines
nothing. It also fails `R.rewrite`'s own positive test ("without redefining what
the model computes") — forgetting a training example *does* change what the
model computes. So this is a half-pin: the station is right and the axis has no
leaf. See P3.

`M.sisa` and `M.exact-retraining-shards` are different and I pinned them
`R.data.select; R.out.agg; !R.rewrite` — SISA's whole mechanism is a data
partition plus an inference-time vote, and the unlearning is a *consequence*.
That the two members of one lineage family land on disjoint role slots is itself
a sign the family is defined by its guarantee rather than by its procedure.

### H4. Target-transforming procedures have no `S.src` value (3 nodes)

`M.label-smoothing`, `M.mixup-labels`, and the family `L.reg.target`.

These rewrite an existing target. `S.src.none` is wrong (there *is* a target,
and they act on it); every positive `S.src` value names who *produced* the
target, and the answer here is "whoever produced the target this procedure then
smooths" — the value is inherited from the run, not a property of the method.
I pinned `S.form.none` (following the CutMix worked example) and left `S.src`
blank. The worked example gave CutMix `S.src.ext.human`, which I think was a
guess about its usual setting rather than a property of the method; label
smoothing applies equally to distillation targets and pseudo-labels.

Note this is only visible because `signal` is a *required* axis. A "source:
inherited from whatever the objective was" value would fix it, but it is really
the same gap as D2 below (signal is a property of the objective, and these nodes
are not objectives).

### H5. `M.load-balancing-losses` — auxiliary structural objectives have no `S.src` value

Pinned `!S.src.none; S.form.div; !S.form.none; R.fit.obj; !R.exec.partition`.
The target is "uniform expert utilisation", a designer-stated desideratum with
no data behind it. The closest value is `S.src.theory.logic` (a declared
constraint), which overreaches — there is no law being imposed. `S.form.div`
(match the routing distribution to uniform) is a fair reading of the form.
Same shape as the `S.src` gap in H4: a criterion with no *source*.

### H6. `M.continuous-batching` — no `role` below `R.exec`

Resolves to the interior node `R.exec` only. It is a request *scheduler*: it
admits and retires sequences from a running batch across independent requests.
It fails `R.exec.operator` (it reorganises no operator), `R.exec.mem` (it
trades no memory for recompute), `R.exec.partition`, `R.exec.replicate` and
`R.exec.comm`. It also fails `R.exec`'s own positive test, which is about "a
single logical run": continuous batching exists precisely to interleave many.
See P4.

### H7. Configuration search has no `S.src` value for "measured held-out performance"

Affects `L.nas.evo` (4 nodes), `M.mutransfer`, and every derivative-free node
used as a searcher. All pinned `S.src.none`, which is false in an interesting
way: evolutionary NAS *is* fitted to something — the validation accuracy of
sampled candidates — and that is the only signal it has. No `S.src` value covers
"a performance number the run itself measured". `S.src.env.verifier` is the
nearest (a programmatic checker) but it scores an output, not a configuration.
See P5. This matters beyond my region: it is the signal of the whole `R.search`
station.

### H8. Smaller ones

- **`M.orthogonality-penalties`** — pinned `!S.form.spars` with no replacement.
  Orthogonality penalises the *correlation structure* of parameters, not their
  number or magnitude. `S.form.redun` (decorrelation) is the right *idea* but is
  scoped to embedding cross-correlation matrices, i.e. to representations, not
  parameters. Candidate for widening `S.form.redun` rather than a new value.
- **`M.max-norm`** — pinned `S.form.none; !S.form.spars; R.fit.update;
  !R.fit.obj`. It is a hard constraint enforced by projection after the step,
  not a penalty. `S.form` has no value for a *feasible set* as opposed to a
  penalty term (`S.form.resid` is a soft residual). Same for `M.spectral-norm`
  if it means spectral normalisation rather than a spectral penalty — the name
  in the table is ambiguous and I pinned the penalty reading.
- **`L.shard.expert`** — takes no `A.exact` value (see A.exact section) and its
  role pin `R.exec.partition` is only true of the *parallelism*, not of the
  routing. `M.load-balancing-losses` had to deny it outright.
- **`M.sophia`** — pinned `A.deriv.first` per the family note, but it uses a
  *diagonal curvature* estimate, which is neither "the gradient, scaled only per
  coordinate" (`A.deriv.first`) nor "a matrix approximation of curvature across
  coordinates" (`A.deriv.second`). AdaHessian is the same case. A one-line fix
  to `A.deriv.first`'s positive test would close it.
- **`M.loss-scaling`** — pinned `R.exec.mem` for lack of anywhere better. It is a
  numerical range workaround for fp16 gradients; it trades no memory for
  compute. It is a component of mixed precision, not a sibling of gradient
  checkpointing.

---

## Proposed new axis values

Proposals only; not added to the tables.

**P1. `R.fit.perturb` — Training-time perturbation of the model's computation**
- parent: `R.fit`
- positive test: randomly removes or perturbs part of the model's own
  computation during training only, leaving the deployed computation unchanged
- negative test: perturbs the example (`R.data.aug`), the target
  (`R.fit.obj`), the gradient (`R.fit.grad`), or which parameters may change
  (`R.fit.scope`)
- needed by: `M.dropout`, `M.dropconnect`, `M.stochastic-depth`, `M.dropblock`,
  `M.droppath`, `M.layerdrop` (H1). Would also catch `M.r-drop`'s two forward
  passes and, outside this region, scheduled sampling and weight noise.
- caveat: this reopens the "dropout is in, batch norm is out" item left open in
  SYNTHESIS §4. Giving dropout a role slot of its own makes the inconsistency
  sharper, not softer.

**P2. `S.form.smooth` — Sharpness and smoothness criteria**
- parent: `S.form`
- positive test: the criterion is a property of the loss surface itself — its
  worst case in a neighbourhood, or the magnitude of one of its derivatives
- negative test: penalises the parameters' own magnitude or structure
  (`S.form.spars`), or variation of the output under a transformation of the
  data (`S.form.inv`)
- needed by: `M.sam`, `M.asam`, `M.gsam`, `L.reg.geom` (H2). Arguably also
  `M.gradient-penalty` and `M.jacobian-hessian-penalties`, which I parked on
  `S.form.inv`; if this value is added, all five should move here.

**P3. `R.rewrite.forget` — Influence removal**
- parent: `R.rewrite`
- positive test: edits a trained parameter set so that a designated subset of
  the training data no longer influences it
- negative test: edits parameters to shrink, requantise, factor or combine them
- needed by: `L.priv.unlearn`, `M.certified-removal`,
  `M.influence-function-unlearning` (H3)
- note: adding it requires relaxing `R.rewrite`'s "without redefining what the
  model computes", which this value necessarily violates.

**P4. `R.exec.serve` — Request-level serving strategy**
- parent: `R.exec`
- positive test: schedules or shares resources across *independent inference
  requests* — admission, batching, cache placement or cache reuse between them
- negative test: reorganises one operator (`R.exec.operator`) or trades memory
  within one run (`R.exec.mem`)
- needed by: `M.continuous-batching`, `M.pagedattention`, `M.radix-attention`
  (H6 and the `L.operator` section below). Adding it also forces a decision on
  `R.exec`'s "single logical run" wording, which currently excludes all three.

**P5. `S.src.meas` — The run's own measured performance**
- parent: `S.src`
- positive test: the quantity driving the procedure is a performance number the
  run measured on held-out data for candidate configurations it produced
- negative test: a per-example target, or a reward returned by an environment
  after an action
- needed by: `L.nas.evo`, `M.amoebanet-regularised-evolution`, `M.neat`,
  `M.hierarchical-evolution`, `M.regularised-evolution`, `M.genetic-programming`,
  `M.mutransfer` (H7); and, outside this region, the whole of `R.search` and
  `L.stop`'s validation-driven members. This is the one proposal I would expect
  another region to raise independently.

---

## Multi-value families

`A.deriv` is already declared multi-valued; `A.privacy` and `A.guar` too. Those
three behaved. The two that are **declared single-valued and broke** are the
finding.

### `A.deriv` — 5 nodes, as predicted

| node | values | why |
|---|---|---|
| `L.derivfree.anneal` (family) | `A.deriv.zero; A.deriv.sample` | annealed search is simultaneously evaluation-only and a Metropolis sampler |
| `M.simulated-annealing` | ″ | inherited |
| `M.parallel-tempering` | ″ | also `A.uncert.post` — it is an MCMC method filed under derivative-free optimisation |
| `M.basin-hopping` | ″ | inherited |
| `M.vat` | `A.deriv.first; A.deriv.second` | the adversarial direction is a power iteration on a Hessian-vector product; the outer step is plain SGD |

So the prediction holds, but with a twist: the forcing case is not an optimiser
needing gradient + curvature, it is the **`L.derivfree` / `L.mcmc` multi-parent
edge** — `L.derivfree.anneal` has parents `L.derivfree` and `L.mcmc.temper`, and
the two values are one from each parent. `M.vat` is the only node where a single
method genuinely consumes two kinds of derivative information. Multi-valued
`A.deriv` is correct, but 4 of the 5 cases would be solved equally well by
honest inheritance from two parents.

### `A.topology` — 3 nodes, and it is single-valued (defect)

| node | values |
|---|---|
| `M.ad-psgd` | `A.topology.decen; A.topology.casync` |
| `M.fedbuff` | `A.topology.feddev; A.topology.casync` |
| `M.asynchronous-fl` | `A.topology.feddev; A.topology.casync` |

AD-PSGD is asynchronous *and* decentralised; FedBuff is cross-device federated
*and* asynchronous. The family's own table admits this: `A.topology.casync`'s
examples list **FedBuff**, while `A.topology.feddev`'s examples list DP-FedAvg —
two values whose example lists name the same system. See D1; this is my headline
finding.

### `A.privacy` — 2 nodes (legitimate, family is multi-valued)

`M.homomorphic-encryption-aggregation` and `M.secure-multiparty-computation` both
take `A.privacy.crypto; A.privacy.secagg`: they compute on encrypted shares
*and* thereby hide individual updates from the aggregator. `secagg` is the
property, `crypto` the mechanism, which is a mild category mix inside one family.

### `A.guar` — 3 nodes (legitimate)

`M.mirror-descent` (`conv; regret`), `M.qsgd` (`conv; unbias`),
`M.polyak-ruppert-averaging` (`conv; consist`).

---

## Negative pins used

16 nodes. Grouped by what forced them.

**Multi-parent import — 1 node, 4 denials.** `L.pg.trust` has parents `L.pg.ac`
and `L.precond.trust`. The second edge is correct lineage (TRPO *is* a trust-
region method) but imports the whole optimiser-branch profile into a policy-
gradient objective:
`!S.src.none; !S.form.none` (PPO has a target; `L.precond` says optimisers do
not), `!R.fit.update` (the worked example is explicit that PPO does not occupy
that slot), `!A.deriv.second` (PPO is first-order; `L.precond` says
preconditioned). Four denials on one node, all from one edge. See D4.

**Federated vs data-parallel.** `L.fed.avg` → `!A.datalocality.pooled`. Parents
`L.fed` (local-only) and `L.dpar.local` (pooled) contradict on a single-valued
family; the federated reading wins. This is the same edge the table itself
flags ("shares its idea with federated averaging").

**Critic removal.** `L.pg.trust.grpo` → `!A.rltarget.ac; !S.src.self.own`. GRPO
replaces the learned baseline with a group statistic, so it is policy-based, and
it has no bootstrapped value target. Both are inherited from `L.pg.ac`.

**Relocation between slots.** `M.decoupled-weight-decay` → `!R.fit.obj` and
`M.max-norm` → `!R.fit.obj` (both act in the update, not the objective; the
AdamW worked example is the precedent). `M.adaptive-gradient-clipping` →
`!R.fit.sched`: it is filed under `L.sched.state`, but it clips a gradient, it
does not change a hyperparameter of the update — a lineage misplacement, not a
property of the method.

**Function preservation.** `M.pipedream` → `!A.exact.exact` (weight stashing
makes the step stale), replacing it with `A.exact.altered` against a family that
is otherwise exact.

**Signal where the family says there is none.** `M.pate`
(`!S.src.none; !S.form.none; !R.fit.grad` — PATE produces noisy teacher labels
for a student, so it is `R.data.label`, not a gradient mechanism like its
`L.priv.dp` siblings), `M.openai-es` and `M.augmented-random-search`
(`!S.src.none; !S.form.none` — these are RL policy searches sitting under a
generic derivative-free family), `M.load-balancing-losses`
(`!S.src.none; !S.form.none; !R.exec.partition`).

**Cardinality rescue.** `M.hogwild` → `!A.cadence.mini` (per-example, under a
minibatch family), `M.dare` → `!A.determinism.det` (random drop, under a
deterministic merging family).

**Station denial.** `M.sisa`, `M.exact-retraining-shards` → `!R.rewrite`.

**Assessment.** Without negative pins this region would be wrong on 16 nodes,
and the `L.pg.trust` case alone would make every trust-region policy method look
like a second-order optimiser with no training signal. The escape hatch is
load-bearing, exactly as the models dimension found.

---

## Nodes I could not pin at all

Only `L.reg` and `L.priv` are blank on all three axes, and both are correct
blanks under rule 1: their children genuinely disagree. `L.reg`'s children span
objective penalties, model perturbations, target rewrites and consistency losses
— the only thing they share is "constrains rather than fits", which is the
family's own characteristic and not a value on any axis. `L.priv`'s children
span gradient noise, cryptographic aggregation and post-hoc forgetting.

**On the 83 review flags.** 83 `M.*` nodes carry
`lowercase descriptive string -- confirm it is a named procedure, not a
description`. I pinned all of them; the flag did not block pinning in a single
case, which is weak evidence that they are real procedures. But the flag is
asking the wrong question for this region. My reading, having pinned them:

- **Genuinely named procedures that merely lack capitals** (~60): `cosine
  annealing`, `gradient checkpointing`, `ring all-reduce`, `local SGD`,
  `simulated annealing`, `top-k sparsification`, `label smoothing`, `mirror
  descent`, `secure aggregation`, `conjugate gradient`, `natural gradient`,
  `proximal gradient`, `model soups`, `task arithmetic`, `ring attention`,
  `continuous batching`, `split learning`. Each has a citable procedure
  description. Keep.
- **Duplicates of a capitalised sibling, which is the real problem** (see D6):
  `M.weight-decay` vs `M.l2-weight-decay` vs `M.decoupled-weight-decay`;
  `M.gradient-clipping` vs `M.global-norm-clipping` / `M.value-clipping`;
  `M.ema` vs `M.ema-of-weights`; `M.polyak-averaging` vs
  `M.polyak-ruppert-averaging` vs `M.averaged-sgd`; `M.regularised-evolution`
  vs `M.amoebanet-regularised-evolution`; `M.megatron-tensor-parallel` vs
  `M.megatron-lm-tensor-parallelism`; `M.ppo` vs `M.ppo-clip`;
  `M.dp-sgd-clipping` vs `M.per-sample-clipping`; `M.fedavg-style-local-steps`
  vs `M.local-sgd`; `M.gradient-checkpointing` vs `M.selective-recompute`.
  These pin *identically*, which is how I found them.
- **Not procedures but recipes or fragments** (3): `M.large-batch-recipes-with-lars-lamb`
  is a bundle (it fills `R.exec.replicate`, `R.fit.update` and `R.fit.sched` at
  once, and should carry `kind=bundle`); `M.trpo-s-kl-region` is a *fragment* of
  TRPO, which already exists as `M.trpo` — I pinned it as a bare trust-region
  mechanism and it should be deleted; `M.fedavg-style-local-steps` is a
  description of what `M.local-sgd` is.

---

## `A.exact` — does the three-value test hold?

**In-scope population: 81 nodes.** `A.exact.exact` 47, `A.exact.altered` 27,
`A.exact.approx` 7. Every distributed/sharding/memtrade/operator node took a
value, and the assignments were easy to make. The family earns its place: it is
the only axis that separates `M.ring-all-reduce` from `M.local-sgd`, which agree
on role, signal, topology and locality and differ only in whether the answer
changes.

**Three problems.**

1. **`approx` and `altered` are not disjoint.** Approximating a per-step
   quantity *necessarily* alters the trajectory. Mixed precision (`approx`)
   changes the trajectory; FedAvg's local steps (`altered`) are precisely an
   approximation of the global gradient. I separated them by asking whether the
   *fixed point* moves, and that is not what the positive tests say. `M.qsgd` is
   the clean demonstration: its quantizer is provably unbiased, so the
   optimisation problem and its solution are untouched and only the variance
   grows — by the stated tests it is both `approx` (bounded change to the
   communicated value) and `altered` (different trajectory). I pinned `approx`.
   A sharper pair of tests: *does the per-step output differ* × *does the
   optimum the run converges to differ*.
2. **The scope predicate is narrower than `altered`'s natural reach.** Scope is
   "every procedure that reorganises or distributes an existing computation".
   `A.exact.altered` ("changes the trajectory the run follows, so the learned
   object differs") describes `M.dp-sgd`, `M.label-smoothing`, `M.dropout` and
   every regulariser in the region perfectly — but none of them reorganises or
   distributes anything, so all are out of scope and I left them blank. That is
   the right call, but it means `altered` means something narrower than it says:
   "alters the optimisation *as a side effect of being a reorganisation*".
3. **A fourth case exists that none of the three covers: changing the function.**
   `L.shard.expert` (`M.top-k-gating`, `M.switch-routing`,
   `M.expert-choice-routing`, `M.base-layers`) is filed under execution but
   sparse routing changes what the network computes — it is not exact, not a
   bounded approximation of a dense forward pass, and not merely a different
   trajectory. I left `A.exact` blank there. I do **not** propose a fourth
   value: a procedure that changes the function computed is model-side, so the
   blank is correctly indicting `L.shard.expert`'s placement (see D3) rather
   than the attribute.

Also worth noting: `A.exact` is the one family whose `notes` column states **no
cardinality**. Every other family says single- or multi-valued. Given problem 1,
that needs settling before the overlap is resolved by accident.

---

## `L.operator` — is it wrong?

**Half right.** The family's positive test ("recomputes a standard operator with
a different memory-access or scheduling pattern, emitting the same values") and
`A.exact.exact` fit all 8 nodes, so the *attribute* story is clean. The role
story is not.

- **`L.operator.tile` is right.** `M.flashattention`, `-2`, `-3`,
  `M.flashdecoding`, `M.fused-layer-norm` pin `R.exec.operator` with no strain.
  The SYNTHESIS ruling (an algorithm is a named procedure; FlashAttention is one;
  `flash-attn` is a library) is confirmed by pinning: all five resolve to
  `S.src.none / S.form.none`, `R.exec.operator`, `A.exact.exact`, and nothing
  else — exactly the ZeRO/FSDP profile, one level further down the hardware.
- **`L.operator.cache` is a different kind of thing and does not belong under
  `L.operator`.** `M.pagedattention` is a memory allocator (paging, to kill
  fragmentation); `M.radix-attention` is cross-request prefix *sharing*;
  `M.continuous-batching` is request admission scheduling. None of the three
  "recomputes an operator". Two of the three act *between independent requests*,
  which also breaks `R.exec`'s "a single logical run". I pinned
  `R.exec.mem` on PagedAttention and radix attention (trading data movement
  against stored state is a fair reading of both) and left continuous batching
  on the bare interior node `R.exec` (H6).
- **Consequence.** `L.operator`'s role pin had to be demoted to the interior
  `R.exec`, because no single child of `R.exec` is true of all its descendants.
  A family whose role cannot be pinned below the station root is a family
  holding two things. Either split `L.operator.cache` out as its own root
  (serving-time resource management, next to `L.memtrade`), or add
  `R.exec.serve` (P4) and keep the family with two role slots.

A naming hazard while this is being fixed: the `notes` already record the
`L.kernel` collision. There is a live one too — **`R.exec` (role: execution
strategy) and `A.exec` (attribute: information available at execution)** are
different senses of "exec" in the same dimension, and they now co-occur in this
region's pins.

---

## Anything that made me doubt an axis

**D1. `A.topology` conflates two orthogonal questions and should be split.**
This is my top finding. The six values answer two different questions at once:

| | synchronisation discipline | who the parties are |
|---|---|---|
| `single` | — | one worker |
| `csync` | barrier per step | pooled workers |
| `casync` | no barrier | pooled workers |
| `decen` | neighbour exchange | pooled workers |
| `feddev` | *unspecified* | many transient devices |
| `fedsilo` | *unspecified* | few persistent organisations |

The first four fix the discipline and leave the parties implicit; the last two do
the reverse. So any asynchronous or decentralised federated method needs two
values from a single-valued family — three nodes here (`M.fedbuff`,
`M.asynchronous-fl`, `M.ad-psgd`), and `M.hierarchical-fl` is a fourth if its
tree structure counts as a discipline. The table's own example lists give it
away: FedBuff appears under `casync` while DP-FedAvg appears under `feddev`.

Proposed split: keep `A.topology` for the discipline (`single`, `sync`, `async`,
`decentralized`) and add a second family for the parties, e.g. `A.parties`
(`one`, `pooled-workers`, `cross-device`, `cross-silo`). `A.datalocality`
already carries the raw-data constraint, so the federated values are
*triply* encoded today: `A.topology.feddev` + `A.datalocality.local` +
`R.exec.agg` all say "federated". Splitting removes the redundancy and fixes
the cardinality break in one move. Measurement consequence: today
"what proportion of distributed-training papers are asynchronous" cannot be
answered, because every federated paper is filed by party and not by discipline.

**D2. `R.exec.comm` and `R.fit.grad` both claim gradient compression.**
`R.fit.grad`'s own examples end with "gradient compression at the worker";
`R.exec.comm`'s positive test is "changes what or how often workers transmit".
`L.dpar.comp` (`M.qsgd`, `M.powersgd`, `M.1-bit-sgd`,
`M.deep-gradient-compression`, `M.top-k-sparsification`) satisfies both
literally. I pinned `R.exec.comm` on the grounds that the *purpose* is
communication, but the mechanism is a gradient transform and the tie-break is
intent, which role is supposed to exclude. Either drop "gradient compression at
the worker" from `R.fit.grad`'s examples, or accept that these five nodes are
two-role.

The same boundary bites `L.vr` from the other side. SAG/SAGA keep a table of
past gradients, which is "the optimiser's internal state rule" —
`R.fit.grad`'s explicit negative test — while SVRG/SARAH/SPIDER compute a
correction term, which is squarely `R.fit.grad`. I pinned `R.fit.grad` for the
whole family. The `R.fit.grad` / `R.fit.update` line is drawn by *statefulness*,
which is a thin and implementation-flavoured criterion.

**D3. `L.shard.expert` is on the wrong axis.** Its own note says "boundary with
architecture", and pinning makes the boundary a wall: it takes no `A.exact`
value (because routing changes the function), its role pin is only true of the
expert-*parallelism* and not of the routing rule, and its one objective member
had to deny the family's role outright. Expert parallelism belongs in
`L.shard`; the gate (`top-k`, Switch, expert-choice, BASE) is a model component;
the load-balancing loss is an `R.fit.obj` entry. Three different homes in one
family of five.

**D4. Lineage multi-parenting imports axis values it should not.** Four nodes
needed denials purely because a correct lineage edge crossed a facet boundary:
`L.pg.trust` ← `L.precond.trust` (4 denials), `L.fed.avg` ← `L.dpar.local` (1),
`L.derivfree.anneal` ← `L.mcmc.temper` (produced the `A.deriv` two-value case),
`M.adaptive-gradient-clipping` ← `L.sched.state` (1). In every case the edge is
real and the imported values are wrong. If attribute inheritance is going to
union across multiple parents, the negative pin is not an escape hatch for rare
defects — it is the normal cost of multi-parenting, and someone has to maintain
it. The cheaper alternative is to declare attributes **non-inherited** (per-node,
like signal already is) and accept more explicit pins.

**D5. `S.form.agree` and `S.form.inv` overlap on the whole consistency family.**
`S.form.agree`'s examples include "Mean Teacher consistency"; `S.form.inv`'s
include "consistency regularisation" and VAT. `L.reg.consist` (Pi-model,
temporal ensembling, Mean Teacher, VAT, UDA, R-Drop) satisfies both tests. I
pinned `S.form.inv` on the family (the penalty is on variation under a declared
perturbation) and gave `M.mean-teacher` **both**, because its EMA target branch
with a stop-gradient is literally `S.form.agree`'s signature. If `S.form.agree`
is meant to be "no negatives + stop-gradient/EMA" and `S.form.inv` "variation
under a nuisance transformation", then Mean Teacher is genuinely both and that
is fine; but the example lists should stop naming the same methods, or roll-ups
over `S.form` will double-count the semi-supervised literature.

**D6. 10 duplicate node pairs, found because they pin identically.** Listed under
"review flags" above. Pinning is a surprisingly good deduplicator: when two
nodes resolve to the same values on all three axes and have the same parent
family, they are the same procedure under two names. Worth running as a check
over the whole lineage table once all regions are pinned.

**D7. `A.param` claims universal scope and is unusable here.** Scope: "to every
algorithm". Value needed for Adam: none of parametric / instance-based /
transductive. Adam does not decide what artifact survives the run — the run
does. The worked examples agree with me (AdamW, L-BFGS and ZeRO-3 all carry no
`A.param`), which means the scope line is already false in the derivation that
wrote it. I left `A.param` blank on all 308 nodes. Either its scope becomes
"procedures that produce the run's output artifact", or the axis has to say
explicitly that a slot-filler takes the value of the run it is in — and that is
a *run* property, not an algorithm property, which is a different dimension.
`A.determinism` has the same universal-scope claim and is nearly as awkward: by
its own negative test ("the only randomness is in data ordering") minibatch SGD
is *deterministic*, which is true and useless. I pinned it only where it
discriminates (109 nodes), and the honest reading is that it discriminates
dropout-like and sampling-like procedures and nothing else.

**D8. `L.memtrade` and `R.exec.mem` are the same thing, and one of them is a
lineage family.** All five members of `L.memtrade` pin `R.exec.mem` and nothing
else; `R.exec.mem`'s examples list are `L.memtrade`'s members verbatim. That is
not a defect — it is what a one-to-one lineage/role correspondence looks like —
but it is worth knowing that for this family the lineage axis carries zero
information beyond the role axis. The same is nearly true of `L.stop` /
`R.fit.stop` and `L.init` / `R.fit.init`. If one is looking for axes to thin,
these are the places where lineage and role are redundant; `L.sgd`/`L.adapt`/
`L.precond` (all `R.fit.update`) is where lineage genuinely adds.

---

## Summary of what matters most

1. **`A.topology` must be split into discipline × parties** (D1). It is
   single-valued, it broke on three nodes, its own example lists contradict
   each other, and today no roll-up can report what fraction of distributed
   training is asynchronous.
2. **The role axis has no station for stochastic regularisers** (H1/P1). Six
   nodes — including dropout, one of the most-reported procedures in the field —
   have no role at all. This is the exact failure mode that forced
   `R.out.predict` and `S.src.self.ident` in phase 1.
3. **`L.operator.cache` is not operator-level** (the `L.operator` section). The
   family was added to catch FlashAttention and it catches it cleanly; the cache
   half is request-level serving and needs either its own root or `R.exec.serve`.
4. Runner-up: **`A.exact`'s `approx` and `altered` are not disjoint**, and the
   family declares no cardinality. QSGD is the node that shows it.
