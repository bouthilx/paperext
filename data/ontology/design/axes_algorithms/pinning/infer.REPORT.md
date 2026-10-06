# Pinning report — region `infer` (503 nodes)

Output: `pinning/infer.pinned.tsv` — same 14 columns, same 503 rows, same order;
only `signal`, `role`, `attributes` written.

## How inheritance was applied

Rule 1 says a blank is how inheritance is expressed, so a value is written **at
the highest node where it is true of every descendant** and methods carry only
their own delta or a negative pin. Direct pins: **145 signal / 106 role / 172
attributes** cells on **271** of the 503 nodes. With inheritance resolved
(union over parents, minus negatives), **434/503** nodes carry at least one
signal value, **500/503** a role, **489/503** an attribute.

The two rules collide and I had to choose per case. Rule 1 forbids a family
pinning anything a descendant denies; rule 2's negative pin only exists because
ancestors *do* pin such things. I pinned at the family and denied at the child
when the exception was one or two nodes (`L.dec` → `!R.out.decode` on
`L.dec.rerank`; `L.hpo` → `!R.search.hp` on `M.zero-shot-hpo`), and left the
family blank when the split was even (`L.cont`, `L.robust`, `L.kd.feat`). That
choice is not derivable from the rules as written and should be ruled on: **a
family node's pins are only interpretable once it is stated whether they are
"true of all descendants" or "the default, overridable".** Everything in this
file assumes the second reading for the eight nodes listed under *Negative
pins*.

---

## 1. Homeless nodes

### 1a. Configuration search has no signal at all — 43 nodes, the largest gap

`L.hpo` (+`.enum`, `.model`, `.bandit`, `.transfer`), `L.nas` (+`.rl`, `.evo`,
`.oneshot`), `L.automl`, `L.aug.policy` and their ~30 methods (grid search,
random search, TPE, SMAC, BOHB, GP-EI, Hyperband, successive halving, ASHA,
PBT, NASNet, ENAS, MetaQNN, AmoebaNet, NEAT, SPOS, BigNAS, Once-for-All,
auto-sklearn, Auto-WEKA, TPOT, AutoGluon, H2O AutoML, AutoAugment, Fast
AutoAugment, PBA, muTransfer-adjacent transfer methods …) resolve to **no
signal value on either sub-facet**.

They are not signal-free: every one of them is driven toward a measured
held-out score. But

- `S.src.*` has no value for *"a performance measurement produced by a
  completed trial of this run's own procedure"*. `S.src.ext.human` names the
  validation labels, not the score computed from them; `S.src.self.own` is the
  model's own *prediction*, not its measured accuracy; `S.src.env.reward`
  requires an environment that the system acted in (NAS-RL literature does call
  accuracy a reward, which is exactly how close this gap is).
- `S.form.*` has no value for *"compare whole configurations by a held-out
  metric"*. `S.form.none` is wrong — these procedures do compare an output to
  something. `S.form.lik` only fits the two gradient-based members
  (`L.hpo.grad`, `L.nas.grad` differentiate a validation **loss**, and those
  two are the only ones I could pin).

Confirmed by the owner ruling in `SYNTHESIS.md` that metrics are a different
kind of entity: the signal axis currently cannot say that a procedure is driven
by a metric, and a fifth of my region is driven by nothing else. See proposals
S1/S2.

### 1b. `L.cont.reg` — no `S.form` for a penalty toward a reference parameter

EWC, SI, MAS, Riemannian walk penalise movement away from the previous task's
parameters. `S.form.spars` is "magnitude of active components" (a penalty
toward **zero**); `S.form.div` needs two distributions; `S.form.inv` needs a
nuisance transformation. Left blank. See proposal S3. The same value would
absorb PPO's KL-to-reference and DPO's implicit KL term, which are currently
coerced into `S.form.div`.

### 1c. `L.tta.ssl` / `M.ttt` — no `S.src.self` value for transformation prediction

The original TTT auxiliary task is rotation prediction. `S.src.self.*` has
mask / next / view / corrupt / ident / own / struct; the target here is *the
identity of the transformation applied*, which is none of them (`.view` is
about agreeing across views, not naming the view). `M.ttt-mae` pins cleanly
(`S.src.self.mask`), `M.ttt` does not. This also means the whole classical
pretext-task family (rotation, jigsaw, colorisation) has no home. Proposal S4.

### 1d. `L.lowrankc` — no `S.src` for "fitted to the parameters, not the data"

SVD compression, Tucker, CP fit a factorisation of a weight tensor. I pinned
`S.form.recon` and left `S.src` blank: every `S.src.self.*` value is about the
*input example*. `M.asvd` escapes because it uses activation statistics from a
calibration set. Proposal S5. The same stretch is already present but hidden in
the accepted GPTQ pin (`S.src.self.struct` for a layer-output reconstruction),
so this gap is latent in the draft, not new.

### 1e. `L.hpo.transfer` / `M.zero-shot-hpo` — prediction without search has no role

`R.search`'s positive test requires *running or simulating multiple
configurations*. `M.scaling-law-extrapolation` and `M.mutransfer` pass (small
proxy runs); `M.zero-shot-hpo` and `M.meta-learned-priors` do not — the target
run executes one configuration, chosen from a meta-model. I wrote
`!R.search.hp` on `M.zero-shot-hpo`, which leaves it with **no role value at
all** (one of three such nodes). `R.fit.sched` covers the subset that sets a
step size (`L.sched.scale`, pinned), not the rest. Proposal R1.

### 1f. `L.tts.loop` — no role for acting against an external tool at inference

ReAct, Reflexion, self-debug, multi-agent debate call a tool, an interpreter or
another model instance and condition the next output on what came back.
`R.exp.act` is scoped to *data collection for learning* and these runs learn
nothing; `R.out.search` (pinned) covers the deliberation but says nothing about
the external interaction, so ReAct and Tree-of-Thoughts are indistinguishable
on all four axes. Proposal R2.

### 1g. `L.robust.cert` — certification is not evaluation, and is pinned as if it were

IBP, CROWN, convex relaxations produce a *proof about a model's behaviour in a
region*. I pinned `R.eval` + `A.guar.cert` because `R.eval` is the only slot
whose test ("computes a reported inference claim about the fitted object")
admits it, but a certificate is not a performance number — and the same ruling
that admitted `R.eval` explicitly kept metrics out. `M.randomised-smoothing`
splits further: it also changes what is emitted (majority vote over noise), so
it carries `R.out.agg` too.

### 1h. `M.classifier-free-guidance` — the training-time half has no slot

CFG requires dropping the conditioning signal during training. That is not an
example transformation (`R.data.aug` acts on examples), not label construction,
not an objective change. I pinned `R.data.aug` under protest; this reproduces
B's T12 independently.

### 1i. `L.fair.post` — no `S.form` for a group-parity constraint

Equalized-odds post-processing, group-wise thresholds and reject-option
classification target a parity constraint across groups. `S.form.cover` is a
coverage frequency, `S.form.inv` is invariance of the *output* under a nuisance
transformation, not equality of error rates across groups. Signal left blank,
role pinned `R.out.calib`. Proposal S6.

### 1j. `L.calib.post` — `A.uncert` has no value for a calibrated predictive distribution

Temperature scaling, Platt, beta, vector/matrix scaling produce a calibrated
distribution **over the outcome**. `A.uncert.point` ("a single prediction with
no dispersion") is actively false of them; `interval`, `post` and `ens` are all
about dispersion over *parameters or predictors*. I left `A.uncert` blank on the
whole `L.calib.post` branch rather than force it — in a region whose name is
calibration, that is a conspicuous hole. Proposal A1.

### 1k. Signal is blind to inference-time scorers

`M.best-of-n` (reward-model-scored), `M.prm-guided-beam` (process reward
model), `M.self-consistency-majority-vote` (no scorer) and `M.mbr-decoding`
(utility function) all resolve to `S.src.none; S.form.none`, which is correct —
nothing is fitted — and leaves verifier-guided test-time search
indistinguishable from unguided test-time search on every axis except lineage.
If "how many papers used a verifier at inference" is a question anyone will
ask, it needs either an `S.src` extension scoped to inference scorers or a new
attribute family.

---

## 2. Proposed new axis values (proposals only; not added to the tables)

| id | name | parent | positive_test | nodes that need it |
|---|---|---|---|---|
| `S.src.trial` | Measured outcome of a trial | `S.src` | the target is a performance measurement produced by a completed trial of the run's own procedure | all of §1a (43), plus `L.meta.opt` (learned optimisers meta-trained on inner-loop loss), `L.pref.reject` scorers |
| `S.form.metric` | Configuration comparison by a held-out measure | `S.form` | configurations are ranked by a measured held-out score rather than by a per-example criterion | same 43 nodes |
| `S.form.anchor` | Reference-anchored penalty | `S.form` | penalises movement of parameters or outputs away from a named reference model or earlier state | `L.cont.reg`, `M.ewc`, `M.si`, `M.mas`, `M.riemannian-walk`; would also hold PPO/DPO KL-to-reference |
| `S.src.self.transform` | Identity of the applied transformation | `S.src.self` | the target is which transformation was applied to the input | `M.ttt`, `L.tta.ssl`; rotation/jigsaw/colorisation pretexts generally |
| `S.src.param` | The model's own parameters | `S.src` | the quantity fitted to is the existing parameter tensor, not any data | `L.lowrankc`, `M.svd-compression`, `M.tucker-decomposition`, `M.cp-decomposition` |
| `S.form.parity` | Group-parity constraint | `S.form` | the criterion is equality of an error or selection rate across declared groups | `L.fair.post` and its three methods |
| `R.search.predict` or widen `R.search` | Configuration prediction | `R.search` | the configuration is set from a rule or meta-model with no trial on the target task | `L.hpo.transfer`, `M.zero-shot-hpo`, `M.meta-learned-priors` |
| `R.out.act` | Environment and tool interaction at inference | `R.out` | takes actions against an external tool or environment at inference and conditions the output on what is returned | `L.tts.loop`, `M.react`, `M.reflexion`, `M.self-debug`, `M.multi-agent-debate` |
| `A.uncert.predict` | Calibrated predictive distribution | `A.uncert` | returns a calibrated distribution over the outcome for each input (not over parameters or predictors) | `L.calib.post` + 5 methods, `M.vector-and-matrix-scaling`, `M.beta-calibration` |

A tenth, weaker one: nothing in `A.guar` holds an *axiomatic* guarantee
(Shapley's uniqueness for `M.shap`), and nothing holds Hyperband's budget bound
cleanly — I pinned `A.guar.regret` on `M.hyperband` / `M.successive-halving` /
`M.asha` / `M.uct` as the nearest fit.

---

## 3. Multi-value families

Forced to pin two values from a family declared **single-valued**:

- **`A.param`, 28 nodes.** Every retrieval-augmented and every
  prototype/metric method is *both* parametric and instance-based: `L.retr`
  pins `A.param.inst` (prediction needs the stored corpus) and `L.retr.dense` /
  `L.retr.aug` add `A.param.param` (the encoder / the generator). Same for
  `L.meta.metric` (ProtoNets: a learned embedding **and** the support set),
  `L.tta.proto`, `M.knn-lm`, `M.icarl`. This is the clearest cardinality
  finding in the region: **`A.param` must become multi-valued, or "is this an
  algorithm with a model" is unanswerable for the entire retrieval branch.**
  Note also that `A.param.inst`'s test says "the stored *training* examples",
  and a retrieval corpus is not training data — the test needs widening to
  "stored data the procedure needs at prediction time".
- **`A.deriv` (already declared multi-valued), `L.nas.rl` and `M.nasnet`.**
  Controller-based NAS is zeroth-order with respect to the architecture score
  and first-order with respect to the controller's own parameters. Both pinned.
  `L.prune.oneshot`/`L.retr.index`/`L.calib.conf` also take two.
- **`A.exact`, `L.quant.qat` (and QAT, LSQ, DoReFa, PACT).** `L.quant` pins
  `A.exact.approx`; QAT does not approximate a fixed computation, it changes
  the trajectory → resolved with `!A.exact.approx; A.exact.altered` rather than
  two values. Flagging because the alternative reading is that `A.exact` needs
  both.
- **`A.world`, every `kind=pipeline` node under `L.mbrl.search`** — see §5.

---

## 4. Negative pins used (64 values on 34 nodes)

Grouped by what they deny:

| nodes | denies | because |
|---|---|---|
| `L.score.sample`, `M.cfg-rescaling`, `M.classifier-guidance` | `S.src.self.corrupt`, `S.form.score` | the DDPM→DDIM case, exactly as predicted in draft A: a sampler inherits a diffusion *training* signal through its `L.score` parent and has no training target. Note `L.score.sample` simultaneously inherits `S.src.none` through `L.dec` — union inheritance hands it two contradictory signals and only the negative pin resolves it |
| `L.dec.rerank` | `R.out.decode` | `R.out.decode`'s negative test is literally "explores multiple complete candidate outputs", which is what reranking and MBR do; replaced with `R.out.search; R.out.agg` |
| `M.zero-shot-hpo` | `R.search.hp` | no trial is run (§1e) |
| `M.randaugment`, `M.trivialaugment` | `R.search.policy`, `A.deriv.zero` | **both are parented under "Searched augmentation policies" and their entire published contribution is removing the search.** A lineage defect, not a pinning one |
| `M.linear-probing`, `M.feature-extraction`, `M.adapterfusion` | `S.src.none`, `S.form.none` | they inherit "scope statements carry no signal" from `L.peft` but they *are* the whole recipe: a head fitted on labels |
| `M.cka`, `M.svcca`, `M.activation-patching`, `M.causal-tracing` | `R.fit.scope`, `A.param.param` | `L.interp.probe`'s second parent is `L.peft.freeze`, so representation-similarity analysis inherits "parameter-efficient adaptation" and "produces parameters". It fits nothing and emits nothing |
| `M.medusa`, `M.eagle`, `M.fudge`, `M.gedi`, `M.pplm`, `M.quality-estimation-reranking` | `S.src.none`, `S.form.none` | named decoding methods that include a training stage (draft heads, attribute discriminators, a QE model) |
| `M.self-distillation`, `M.deep-mutual-learning` | `S.src.ext.model` | `L.kd` asserts the target comes from *another* model; here it is the same one |
| `M.contrastive-representation-distillation` | `S.src.ext.human` | inherited from `L.ssl.contrast.sup` (label-aware positives); CRD's positives come from the teacher |
| `M.llm-int8`, `M.wanda`, `M.splade-hybrid` | `S.src.self.struct` / `S.form.recon` | PTQ and one-shot pruning families assert a calibration-set fit; LLM.int8 decides outliers per input, Wanda minimises no reconstruction, SPLADE is trained on relevance not corpus statistics |
| `M.snip`, `M.wanda` | `A.deriv.second` | parented under curvature-based saliency / one-shot reconstruction; both are first-order |
| `M.ilqr`, `M.ddp`, `M.cem-mpc`, `M.mppi` | `A.deriv.comb` | `L.tts.plan` is pinned combinatorial for the tree searchers; continuous optimal control is second-order or zeroth-order |
| `M.alphago`, `M.alphazero` | `A.world.learned` | they use the game's rules, not a learned model |
| `M.mc-dropout` | `A.uncert.post` | parented under approximate Bayesian inference; the table itself calls it "MC dropout as approximation" under `A.uncert.ens` |
| `M.rl-squared` | `S.src.ext.human`, `S.form.lik` | meta-RL inheriting few-shot-classification signal from `L.meta` |
| `M.der`, `M.icarl`, `M.lime`, `M.reciprocal-rank-fusion` | various | replay/reranking families pinned signal-free, these members fit something (or vice versa for RRF) |

---

## 5. The composite (`kind=pipeline`) nodes

Seven: `M.rlhf`, `M.rlhf-with-ppo`, `M.rlaif`, `M.constitutional-ai`,
`M.alphago`, `M.alphazero`, `M.muzero`.

**Signal and role pin fine as a union over stages** and are genuinely
informative: `M.rlhf` carries
`S.src.ext.human; S.src.ext.pref; S.src.env.rm; S.form.lik; S.form.rank; S.form.return`
and `R.fit.obj`, which is a true statement about the pipeline as a whole and is
exactly B's "worst row in the table" reproduced. `M.rlaif` and
`M.constitutional-ai` differ from it on one value (`S.src.ext.model`) plus a
role (`R.data.synth`, and `R.data.label` for CAI's critique-and-revise stage),
which is the right discrimination.

**Attributes do not pin, and cannot.** `A.regime` is declared single-valued and
RLHF's stages are offline (SFT), offline (reward model) and on-policy (PPO).
Any single value is false of the composite; a blank is indistinguishable from
"not annotated". Same for `A.rltarget` (no value during SFT, actor-critic
during PPO) and `A.cadence`. I therefore **left `A.regime` blank on all four
preference pipelines**, and — because three of `L.pref.rm`'s four children are
pipelines — could not pin `A.regime.on` at `L.pref.rm` either, even though it
is true of "the RL stage of RLHF", which is what people mean by the family. The
only non-pipeline member of that family is `M.reward-model-ensembles`, an
ensembling trick. So the attribute axis says nothing about the single most
reported method family in this region.

**My answer to "should a composite carry pins at all":** it should carry
`signal` and `role` (the union is true and it is what a paper reports), and it
should carry **no** value from any single-valued attribute family. That is not
expressible today. The cheapest fix is a declared rule — *single-valued
attribute families are undefined on `kind=pipeline`; read them off the
expansion* — which requires the expansion's stages to be nodes rather than the
free-text strings they are now (`expands_to` on `M.rlhf` is
`supervised finetuning; reward-model fitting; PPO against the reward model`,
none of which is a node_id).

`M.alphago` / `M.alphazero` / `M.muzero` behave better because their stages
share an attribute profile; the only per-stage conflict is `A.world`
(`given` for AlphaGo/AlphaZero, `learned` for MuZero), which resolves at the
node. `M.alphago` is the one composite whose signal genuinely needs the
expansion: `S.src.ext.demo` is true only of its first stage.

---

## 6. `L.tta` versus `R.adapt` — the role axis is double-counting lineage

**In this region `R.adapt` and the lineage family `L.tta` are co-extensive.**
Every node I pinned `R.adapt` on is a descendant of `L.tta`, and every
descendant of `L.tta` has it. No other role value behaves this way: `R.out.decode`
spans `L.dec` and `L.score`, `R.fit.obj` spans fifteen families, `R.search.hp`
spans `L.hpo` and `L.sched`. `R.adapt` cross-cuts nothing, so it carries zero
information beyond lineage — it is a lineage family wearing a role value's
clothes, and it exists for the reason the role table itself admits: *"kept
separate because 'when' is definitional here."*

Worse, it is additive rather than exclusive. `L.tta.ent` resolves to
`R.adapt; R.fit.obj; R.fit.scope` (TENT's worked-example pins), `L.tta.ssl` to
`R.adapt; R.fit.obj`, `L.tta.proto` to `R.adapt; R.out.predict`. So every TTA
node is counted once under test-time adaptation and again under parameter
fitting or output production, which is the double-count draft A predicted. The
honest options are (a) delete `R.adapt` and let `L.tta` do the aggregating,
which is what B's structure did and what B flagged as a loss (T2) — but B's
loss was that *nothing* rolled up TTA, and in the merged structure `L.tta`
does; or (b) keep it and declare it excluded from role roll-ups. I would delete
it. The one argument against: `M.ttt-layers` and `M.prediction-time-bn` adapt
at test time without being "a test-time adaptation paper", and a role value can
be attached to them where a lineage family cannot — but `M.ttt-layers` is an
architecture (see §7), which weakens even that.

---

## 7. Nodes I could not pin, and why

- **`M.zero-shot-hpo`** — no role (§1e), no signal (§1a), no attributes. The
  only node in the region with nothing on three axes.
- **`M.ttt-layers`** — left blank on signal and role beyond the inherited
  `R.adapt`. TTT-layers put the inner adaptation loop *inside the forward pass*:
  it is a layer, i.e. part of the computed function, which `SYNTHESIS.md`'s own
  FlashAttention ruling places on the models side. It should probably be moved
  out of this dimension.
- **`M.chain-of-thought-prompting`, `M.in-context-learning-as-meta-learning`** —
  pinned only by inheritance. Both are prompting/framing claims rather than
  procedures with an independently reimplementable description; draft A's
  tension 3 (the naming boundary) is exactly this, and `L.tts.tree`'s own note
  concedes CoT is admitted *because it is named*.
- **`M.ablation-studies`** — pinned `R.eval; R.out.explain` and nothing else.
  It is a description of practice, not a named procedure, and carries the review
  flag. I would drop it.
- **108 of the 503 nodes carry the `lowercase descriptive string -- confirm it
  is a named procedure` flag.** Most are fine as names (beam search, magnitude
  pruning, integrated gradients, split conformal). The ones I would not keep:
  `M.ablation-studies`, `M.in-context-learning-as-meta-learning`,
  `M.chain-of-thought-prompting`, `M.task-specific-heads`,
  `M.feature-extraction`, `M.zero-cost-proxies` (a class, not a method —
  `M.synflow-score` and `M.naswot` are its members and are siblings of it),
  `M.one-shot-nas` (same relation to `M.spos`/`M.bignas`),
  `M.min-max-calibration`, `M.reranking-by-model-score`.
- **Near-duplicate pairs where one copy sits one level too high**, which forced
  me to pin the same values twice: `M.nucleus-sampling`@`L.dec` vs
  `M.nucleus-top-p`@`L.dec.sample`; `M.conformal-prediction`@`L.calib` vs
  `M.split-conformal`/`M.full-conformal`; `M.self-consistency`@`L.tts` vs
  `M.self-consistency-majority-vote`@`L.tts.sample`; `M.adapters`@`L.peft` vs
  the four named adapter methods; `M.nasnet`@`L.nas` vs
  `M.nasnet-zoph-le`@`L.nas.rl`; `M.alpaca-style-sft`@`L.sft` vs
  `M.alpaca`@`L.sft.inst`; `M.beam-search` vs `M.argmax-decoding`/
  `M.greedy-decoding` (the last two are the same procedure under two names).
  These are deduplication work, but they also broke the inheritance test: the
  high copy inherits less than the low copy, so the same method resolves to two
  different pin sets.

---

## 8. Things that made me doubt an axis

1. **`R.adapt` should not exist** (§6). It is the only role value with no
   cross-cutting behaviour, and it double-counts.
2. **`R.out` covers decoding and test-time search well, with two leaks.** The
   caller's question: yes — `R.out.decode` holds beam search, greedy, all the
   truncation samplers, constrained decoding, speculative decoding, the
   diffusion solvers and guidance; `R.out.search` holds sample-and-select, tree
   search, refinement loops and planning; `R.out.context`, `R.out.calib`,
   `R.out.agg`, `R.out.predict` and `R.out.explain` each hold a clean family. The
   widened scope is justified: 169 of my 503 nodes resolve to an `R.out.*` value
   and none of them had to be forced. The two leaks are (i) **selecting among
   complete candidates falls between `R.out.decode` (whose negative test
   excludes it), `R.out.search` and `R.out.agg`** — reranking/MBR/best-of-n/
   quality-estimation reranking all land here and I had to pin two values and a
   negative to place `L.dec.rerank`; the cleanest fix is a sibling
   `R.out.select` or an explicit ruling that `R.out.agg` covers selection as
   well as combination; and (ii) **tool-using inference loops have no slot**
   (§1f).
3. **`L.score.sample` is one family with two roles in it.** DDIM, DPM-Solver and
   UniPC are training-free samplers (`R.out.decode`, no signal); progressive
   distillation, consistency models and LCM are *training* procedures
   (`R.fit.obj`, `S.src.ext.model`). They are grouped because they share a goal
   (fewer steps), which is the same error the draft rejected when it killed the
   "compression" role for KD. The family should split, or its role pin should be
   removed.
4. **`R.search.hp` and `R.fit.sched` are hard to separate**, and both are needed
   by one node. PBT mutates hyperparameters *during* training; muP sets the step
   size from a width rule; ULMFiT's schedule and gradual unfreezing change which
   layers are trainable as training proceeds. I pinned `R.fit.sched` on all four
   and `R.search.hp` additionally on PBT. If `R.fit.sched`'s test ("changes a
   hyperparameter of the update over the course of training") is read literally,
   it swallows the online half of HPO.
5. **`A.param`'s test is written for supervised learning and breaks on
   retrieval** (§3) — 28 nodes need two values and the "stored *training*
   examples" wording excludes a retrieval corpus outright.
6. **`L.interp.probe`'s second parent (`L.peft.freeze`) imports four wrong pins
   into representation analysis** (§4). This is the models-dimension MLP-Mixer
   failure recurring: union inheritance across an "instantiates"-style edge, not
   a descent edge. It is the strongest evidence in my region for draft A's
   tension 11 (two edge types).
7. **`R.eval` is absorbing everything that produces a claim rather than a
   prediction** — certification (§1g), ablation studies, permutation importance.
   If `R.eval` is "measures the fitted object", certification and attribution
   are not that, and three different things are now sharing one slot.

---

## 9. Counts

| axis | direct pins written | nodes resolving to ≥1 value | nodes with none |
|---|---|---|---|
| signal | 145 | 434 / 503 | 69 (43 of them the §1a search gap) |
| role | 106 | 500 / 503 | 3 (`L.robust`, `L.cont` — legitimate family blanks; `M.zero-shot-hpo` — homeless) |
| attributes | 172 | 489 / 503 | 14 (10 legitimate family blanks, 4 under `L.hpo.transfer`) |

Homeless cases: **11 distinct gaps** covering **~70 nodes**, of which the
configuration-search signal gap alone is 43. Negative pins: 64 values on 34
nodes. Multi-value-in-a-single-valued-family: 28 nodes on `A.param`, 4 on
`A.exact`, 7 pipelines on `A.regime`/`A.world`.

### The three findings I think matter most

1. **The signal axis cannot express "driven by a measured metric", and that is
   a fifth of this region** (HPO + NAS + AutoML + augmentation-policy search, 43
   nodes). Two new values fix it (`S.src.trial`, `S.form.metric`). Without them
   these nodes look signal-free, i.e. indistinguishable from beam search.
2. **`R.adapt` is co-extensive with the lineage family `L.tta` and additive on
   top of `R.fit.*`** — the only role value that cross-cuts nothing and the only
   one that guarantees a double-count. Delete it and let lineage aggregate.
3. **Composite (`pipeline`) nodes can carry `signal` and `role` but no
   single-valued attribute**, because their stages disagree (`A.regime` is
   offline-offline-on-policy within RLHF). And because three of four children of
   `L.pref.rm` are pipelines, the family cannot carry those attributes either —
   so the attribute axis currently says nothing about RLHF, RLAIF or
   Constitutional AI. `expands_to` must name node_ids for the fallback "read it
   off the expansion" to be usable.
