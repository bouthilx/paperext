# Pinning pass — what pinning 1697 nodes to three axes found

Six agents, one per lineage region, each with the axis tables read-only and no
corpus access. Rules in `pinning/INSTRUCTIONS.md`; per-region detail in
`pinning/*.REPORT.md`; pins merged into `lineage/nodes.tsv`.

`resolve.py --audit`: **0 problems**. `resolve.py --homeless`: **93 signal, 47
role, 54 attributes**.

This was ranked the highest-yield instrument before it ran, on the evidence of
the models dimension. It was.

---

## 0. What the pass found that the pass was not built to find

Three of the largest findings were **invisible to the check written for them**.
Rule 4 said: if nothing fits, leave it blank and report it. That finds *absence*.
It cannot find a pin that exists and is **wrong or too weak**:

| finding | nodes | why `--homeless` missed it |
|---|---|---|
| the signal cross-product (SPR) | ~8 families | both facets have values; only their *pairing* is lost |
| `S.src.ext` with no "measured outcome" child | 169 | they resolve to the interior node, so they are not homeless |
| `A.deriv.closed` true-by-precedent, false-by-test | ~60 | a value was pinned, following phase 1's own EM precedent |

**Carry this to datasets:** a homelessness check validates coverage, not
correctness. Catching the other class took asking the agents to report *doubts*,
not just failures — which is why the `## Tensions` and "anything that made you
doubt an axis" sections earned more than the pins did.

## 1. Reliability: 91%

187 nodes fall in two regions through multi-parent edges, so they were pinned
twice independently. That was deliberate — it buys an inter-annotator number for
free.

| | count |
|---|---|
| comparisons (187 nodes × 3 axes) | 561 |
| identical | 44 |
| blank in one region (convention) | 350 |
| granularity or disjoint additions | 116 |
| **genuine contradictions** | **51 (9%)** |

**The 350 "blank in one region" are my fault, not the agents'.** The instructions
never fixed the pinning convention, so three regions wrote the full value set on
every method row and three wrote only deltas from the inherited set. Both are
defensible; mixing them makes raw pins incomparable. Union-merging is safe
because inheritance is monotone, but the convention must be stated before any
pass like this runs again.

The 51 real contradictions cluster on about six axis defects rather than
scattering, which is the useful part:

- `R.data.aug` vs `R.data.synth` on four nodes (counterfactual augmentation,
  minimal-pair generation). Is manufacturing a counterfactual *transforming* an
  example or *creating* one? Both positive tests pass. Axis defect.
- `S.src.ext` + `S.src.self.struct` vs `S.src.ext.human` across graph-based
  semi-supervised learning. The statistics-side agent counted graph geometry as a
  second source; the data-side agent did not. The former is right.
- `S.form.spars`/`lik` vs `S.form.none` on filter feature selection.
- `A.uncert.post` vs `A.uncert.ens` on MC-dropout — genuinely both.
- `A.uncert.interval` vs `A.uncert.point` across off-policy evaluation. IPS does
  return a confidence interval; the statistics-side reading is right.
- `A.deriv.first` vs `A.deriv.second` on VAT, whose power iteration is a
  Hessian-vector product.

## 2. Cardinality, derived rather than guessed

Left undeclared on purpose. 185 `AMBIGUOUS` reports named the families that
actually needed two values, and the count is the evidence:

`A.deriv` 64 · `A.uncert` 42 · `A.param` 25 · `A.guar` 14 · `A.cadence` 14 ·
`A.outspace` 10 · `A.determinism` 10 · `A.topology` 3 · `A.privacy` 2 ·
`A.agents` 1 → **many**. The other seven → **one**.

Declaring them took the audit from 188 problems to 3, and dropping three dead
negative pins took it to 0.

But **a high count is not always evidence of multi-valuedness — sometimes it is
evidence of a conflation**, and the two must not be confused:

- `A.uncert` (42): `A.uncert.post`'s test says "posterior over **parameters or
  functions**", and a VAE's `q(z|x)` is a posterior over **per-example latents**
  while its weights are a point estimate. So phase 1's own VAE worked example
  fails its own test. This is two questions — what is returned × over what.
- `A.outspace` (10): element type (`disc`/`cont`) × joint structure (`struct`).
  Every autoregressive model needs `disc` **and** `struct`.
- `A.topology` (3): discipline (sync/async/decentralized) × parties
  (pooled/cross-device/cross-silo). Its own example lists contradict each other,
  and today no roll-up can answer "what fraction of distributed training is
  asynchronous", because every federated paper is filed by party.

`A.deriv`, `A.param`, `A.guar` and `A.privacy` are genuinely multi-valued.
`A.cadence` and `A.determinism` are `many` provisionally and need rulings (below).

## 3. The homeless clusters

### 3a. No signal value for "the response variable was measured in the world" — 169 nodes

**The largest gap in the pass.** `S.src.ext` has children for human, model, rule,
preference, demonstration and naturally co-occurring pairs — and none for a
measured outcome. So 169 nodes across the classical branch sit parked on the
*interior* node `S.src.ext`, and every `S.src.ext.*` roll-up will read "unknown
annotation type" when the truth is "no annotator exists". Proposed
`S.src.ext.obs`.

This is the clearest case of the blind spot in §0: those nodes resolve to a
value, so `--homeless` never names them.

### 3a-bis. No signal value for "a measured held-out score" — 23 nodes, found by four regions independently

`L.hpo` 10 · `L.nas` 7 · `L.automl` 6. **Four of six regions proposed this gap
without knowing the others had**, under four different names: `S.form.sel.metric`
(data), `S.src.meas` (opt), `S.src.env.metric` (rl), `S.src.trial`/`S.form.metric`
(infer). Independent rediscovery at that rate is as strong as this process gets.

Every existing `S.form` value is a criterion an optimiser minimises; every
`S.src` value is a target attached to an example. A trial's validation accuracy
is neither. NAS-RL literally calls accuracy a reward, which shows how near the
miss is — but `S.src.env.reward` requires an environment that was acted in.
Without it, these nodes are indistinguishable from beam search.

### 3b. Ruling evaluation in left it with no signal — 27 nodes

`L.boot` 19 · `L.test` 8. Resampling inference and hypothesis testing are in
scope by the owner's ruling, and `S.form.none` is false for them: a bootstrap
confidence interval *does* compare something. They need either signal values of
their own or an explicit rule that assessment procedures take no signal. This is
a direct consequence of widening the scope, arriving where the widening did not
look.

### 3c. Dropout has no role — 8 role + 14 attribute homeless under `L.reg`

Two regions reported it independently. One of the most-reported procedures in the
field resolves to no slot, because it is neither the objective, nor the update
rule, nor data preparation: it perturbs the model during training.
`R.fit.perturb` is the proposal. This is also the architecture-vs-algorithm
boundary arriving from the algorithms side — dropout is in, batch norm is out,
and nothing in either dimension says why.

### 3d. Gradient-free fixed-point computation has no role — 5 nodes

`R.fit.update`'s positive test demands a gradient, so value iteration, policy
iteration, CFR, regret matching and Sinkhorn have no slot. `R.fit.fixpoint`.

### 3e. `L.optdisc` is the strongest candidate for a family that should not exist

12 of its 20 nodes have no role at all. Its members share only `A.deriv.comb`,
and the optimal-transport branch fails even that. It has no common role, no
common signal and no lineage — it is an attribute wearing a family's clothes.

## 4. Two findings that change a representation, not a value

### 4a. The signal axis loses the pairing, and rule 4 could not see it

`SPR` resolves to sources `{env.reward, self.own, self.next}` × forms
`{return, agree}`. That cross-product licenses *(reward, agreement)* and
*(self-prediction, return)*, neither of which the method has. Same on
EfficientZero, BBF, TD-MPC, DrQ and CQL.

Nothing was left blank, so the gap is invisible to "report what you could not
pin": the pin is not missing, it is **weaker than the truth**. A check for
homelessness cannot find an over-permissive encoding — worth remembering for the
datasets dimension.

The fix is a representation change: a signal pin is a **(source, form) pair, one
per objective term**, not two independent multi-valued sets. The source/form
split itself survives; its independence does not. Note the rhyme with composites
— a method with several objective terms is a bundle of signals.

### 4b. `R.adapt` carries no information and should be deleted

It resolves on exactly the 20 `L.tta` descendants and on nothing else. It is the
only role value that cross-cuts no lineage family (`R.out.decode` spans `L.dec`
and `L.score`; `R.fit.obj` spans fifteen), so it duplicates lineage and is
additive on top of `R.fit.obj`/`R.fit.scope`, producing the double-count run A
predicted. Run B's objection that nothing rolled up test-time adaptation is
answered by `L.tta` itself.

## 5. Lineage defects pinning exposed

Pinning is a deduplicator: identical pins on two nodes means one node.

- **~25 duplicate pairs**, including `M.ppo`/`M.ppo-clip`, `M.weight-decay`/
  `M.l2-weight-decay`, `M.ema`/`M.ema-of-weights`, Hungarian matching ×3,
  `M.sinkhorn`/`M.sinkhorn-knopp`, `M.actor-critic` duplicating its own family.
  Seven more are the same method filed at two depths, which resolves to two
  different pin sets for one procedure.
- **`M.iql` is unpinnable because it is two methods** — Implicit Q-Learning
  (offline, actor-critic, continuous) and Independent Q-Learning (multi-agent,
  decentralised, value, discrete) — with both parents attached. The owner's
  ruling that an ambiguous bare string gets no node is now a blocker, not a
  tidiness preference.
- **`M.randaugment` and `M.trivialaugment` sit under "searched augmentation
  policies" and their whole published contribution is removing the search.**
  Forced `!R.search.policy`.
- **Negative pins are a misfiling detector.** In the generative region, 16 of 25
  nodes needing them needed them because of a second parent or an outright
  misfiling, not because the method is unusual: `M.cpc` inherits `S.form.agree`
  through `L.ssl.jepa` — the MLP-Mixer failure reproduced exactly. 31 of that
  region's 58 negative pins trace to the single `L.score` → `L.score.sample`
  edge. **A high negative-pin count on one edge means the edge is wrong.**
- `L.interp.probe`'s second parent imports four wrong pins into representation
  analysis — CKA and activation patching fit nothing and emit nothing.
- `M.ttt-layers` is an architecture (an inner loop inside the forward pass) and
  by the FlashAttention ruling belongs model-side.

## 6. Rule 1 is not well-defined, and the example I gave for it is wrong

The instruction said a family pins only what is true of every descendant, with
`L.pg` pinning `R.fit.obj` and `S.form.return` as the example. `L.nas.rl` is a
declared descendant of `L.pg` whose role is `R.search.arch`. So under a strict
reading `L.pg` can pin neither.

Three regions hit this independently and all three resolved it the same way —
pin the invariant, negative-pin the deviant, flag it. The deviants arrive through
**`instantiates`** edges from other families, never through descent, which is why
this is the same open item as separating the two edge types: **rule 1 should
quantify over `divides` and `derives-from` descendants only.** Until that is
settled a family's pins are ambiguous between "true of all descendants" and "the
default, overridable".

## 7. The attributes axis is largely degenerate

In the generative region: `A.param` 173 pins all one value; `A.cadence` 167 all
`mini`; `A.uncert` 169 of 170 `point`; `A.deriv` 167 of 177 `first`. Six of
seventeen families take no value at all in 181 nodes. Roughly 650 of 1024
attribute pins there carry no distinction.

The axis needs **family-level defaults with only deviations pinned**. As it
stands the information is real but buried under its own boilerplate — and
`A.guar` being empty across the whole generative region is itself a finding
worth reporting, not a gap: that region is entirely empirically justified.

## 8. Smaller items

- `A.param` claims universal scope and is blank on 168 nodes in one region and
  all 308 in another. Needs `A.param.none`, and `A.param.inst`'s test says
  "stored **training** examples", which excludes a retrieval corpus outright.
- `R.exec` (role) and `A.exec` (attribute) are two senses of "exec" now
  co-occurring in pins — the same collision as `L.kernel`/`L.operator`.
- `L.operator.cache` is wrong: PagedAttention and continuous batching reorganise
  no operator, and two of them act *between independent requests*, which breaks
  `R.exec`'s "single logical run".
- `S.form.agree` vs `S.form.inv` are not distinguishable — their example lists
  name the same methods, and three regions reported the overlap.
- `R.exec.comm` and `R.fit.grad` both literally claim gradient compression.
- Selecting among complete candidates (reranking, MBR, best-of-n) falls between
  `R.out.search` and `R.out.agg`; `R.out.decode` excludes it by name.
- Tool-using inference loops (ReAct, Reflexion) have no slot: `R.exp.act` is
  scoped to collecting data for learning.
- `L.memtrade`↔`R.exec.mem`, `L.stop`↔`R.fit.stop`, `L.init`↔`R.fit.init` are
  one-to-one, so lineage carries no extra information at those three nodes.
- `A.hier` resolves on 173 nodes and is non-default on 6; `A.exec` on 15, all
  one subfamily. Neither clearly earns family status.
- Of ~346 nodes flagged as possibly descriptions rather than named procedures,
  the regions judge roughly three quarters false positives (lowercase by
  convention: behaviour cloning, label propagation, fictitious play) and name
  ~35 genuine deletions.


## 9. The granularity question, measured

The classical region was asked how often it pins more roles per node than the
deep branch does, because that decides whether role roll-ups are comparable.

Roles per method: 1 → 184 · 2 → 97 · 3 → 49 · 4 → 14 · 5 → 2 · none → 4.
**Mean 1.69, 46% at two or more, 19% at three or more.** Phase 1's worked
examples average ≈1.5 with ~8% at three or more.

**They are not comparable, and the reason is sharper than the averages.** Phase
1's ≥3 cases are all acknowledged bundles — DQN, MuZero, XGBoost, FixMatch. The
classical ≥3 cases are *ordinary single-contribution papers*: k-means, random
forests, CRFs, change-point detection, AdaBoost, causal forest. So the excess is
not bundling, it is that classical methods are *named at whole-run grain*.

Two measurements make it concrete: `R.fit.update` is carried by 118 nodes of
which ~60 are tree or structure growth rather than a step rule, and `R.fit.est`
is carried by 148 of 350 classical methods (42%) against a rare slot in the deep
branch. And **`kind=bundle` is set on 2 nodes while 65 behave as bundles** — the
composite marker the owner approved is needed on an order of magnitude more
nodes than were hand-seeded.

## 10. `divides` edges should not propagate axis values

**52 of the classical region's 159 negative pins exist only to undo a
multi-parent `divides` edge.** `M.viterbi` needs eight; `L.hpo.model` seven;
simulated annealing and basin hopping six each.

This is the same root cause as §6, measured from the other side: a `divides` edge
says "this node is one of the ways its parent subdivides", which is a *statement
about the parent's characteristic*, not an inheritance of the parent's axis
values. Propagating values along it manufactures contradictions that then need
denials. The clean rule is that only `derives-from` and `instantiates` edges
carry axis values — which also makes rule 1 well-defined.

## 11. Three late phase-1 additions, judged

- **`S.form.moment` — load-bearing.** 34 pins, and without it every CATE, IV,
  GEE, GMM, IPS and TMLE node is form-less. It is also the only home for
  cumulant-matching ICA. Weakness: it does not separate just-identified
  estimating equations from over-identified GMM.
- **`A.guar` — necessary but incomplete.** 146 pins, but `cert` 0, `approx` 2,
  `regret` 1, while the two claims classical work actually makes have no value:
  **asymptotic coverage** (`A.guar.cover` explicitly excludes it, leaving 90
  interval-valued nodes with no guarantee) and **test-level or FDR control**.
- **`R.out.predict` — necessary, now overloaded.** 63 pins doing three jobs:
  nonparametric prediction, structured decoding, and transductive grouping
  (DBSCAN, Louvain, PageRank) — for which its parent `R.out`'s characteristic,
  "between a trained model and an emitted result", is simply false.

Also: **`S.form.post`'s positive test says "approached by sampling"**, which
excludes the closed-form posteriors of GPs, Kalman filters, Laplace approximation
and expectation propagation — roughly 25 of its 53 pins contradict their own
test.

---

## §9 — `many` families did not union up the chain (found 2026-10-07, #100)

Found by porting these inheritance semantics into `paperext.ontology.axes` and
discovering the sibling **models** dimension disagreed. `resolve.py` contained:

```python
resolved.update(at_front if card == "many" or len(at_front) == 1 else at_front)
```

Both branches are identical. The intention to treat a `many` family differently
was written and then collapsed, so **every family resolved as if it were
single-valued whenever a descendant pinned anything of its own** — `cardinality
= many` applied only to values written on the same row, which is precisely the
case where it was least needed.

This is a fourth instance of the pattern §0–§8 keep finding: **the pin existed
and was wrong, so no coverage check could see it.** A node resolving to one
value where two were true looks identical to a node that correctly has one.

### Why chain-union is the fix rather than `one` cardinality

`many` was already doing real work — 21 nodes resolve to ≥2 `A.deriv` values, 14
to ≥2 `A.guar`, 5 to ≥2 `A.uncert`. The families genuinely hold several values at
once; only the *inheritance* was restricted. And the escape hatch chain-union
needs was already there and already used: **83 denials on this axis**, 12 of them
on `A.deriv`. `signal` (92 denials) and `role` (20) had taken the same route
already — union up the chain, deny where it does not hold. Attributes was the
only axis that shadowed instead.

### What it exposed, and the triage

17 node-axis pairs changed. **10 were true values being dropped**, kept as-is:

| node | gains | why it is true |
|---|---|---|
| `M.exp3` | `A.guar.regret` | the regret bound is EXP3's headline theorem; `A.guar.unbias` is also true |
| `M.mirror-descent` | `A.guar.conv` | has both regret and convergence results |
| `L.mcmc.gibbs` | `A.deriv.sample` | closed-form conditionals, drawn from — both |
| `M.blocked-gibbs`, `M.collapsed-gibbs` | `A.deriv.closed` | block/marginal conditionals are analytic |
| `M.dirichlet-process-mixtures` | `A.deriv.closed` | CRP conditionals are closed-form, sampled from |
| `L.derivfree.anneal` | `A.deriv.zero` | derivative-free *and* sampling-based |
| `M.simulated-annealing`, `M.basin-hopping` | `A.deriv.sample` | both propose by sampling |
| `L.hpo.model` | `A.deriv.closed` | the GP posterior is closed-form; 5 sibling BO methods already pin **both** explicitly, which is the precedent |
| `L.causal.hte` | — | see below |

**7 were ancestor pins claiming more than they should.** Under the standing rule
*a family pins only what is true of every descendant*, these were already
defective; nearest-depth had been hiding them.

| fix | where | why |
|---|---|---|
| **narrowed** `A.guar.regret` off `L.marl.game` | 3 of its 6 children have convergence results, not regret bounds (NFSP, Nash-Q, fictitious play). The 3 it *is* true of — CFR, Deep-CFR, regret-matching — already assert it on their own rows, so the narrow costs nothing | |
| **denied** `!A.deriv.closed` | `M.viterbi` | a max-plus DP recursion, not an equation solved in one shot |
| **denied** `!A.deriv.closed` | `M.k-medoids-pam` | a swap search; the contrast with k-means, whose mean update *is* closed-form, is what the value distinguishes |
| **denied** `!A.deriv.closed` | `M.slice-sampling` | it exists *because* the conditionals are not closed-form |
| **denied** `!A.uncert.ens` | `L.causal.hte` | it descends from `L.bag` for good reasons — it resamples examples, it aggregates outputs — but ensemble-based uncertainty is not one of them. Four of its five children already wrote this denial individually; saying it once at the parent is the same claim, said once |

`value_parent = L.causal` was the tempting fix for the last one and is **too
blunt**: measured, it also strips `R.out.agg`, `R.data.select`, `S.form.assess`
and `A.cadence.full` from the whole subtree, and those are true of it.

**Net: +10 resolved values, −0.** `resolve.py --audit` clean throughout
(0 problems, 1672 nodes), and `tests/ontology/test_axes.py` asserts the engine
and this script still agree on all 5016 resolutions.
