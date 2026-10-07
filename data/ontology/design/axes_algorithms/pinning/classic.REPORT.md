# Pinning report — region `classic` (438 nodes)

## 0. What was written, and the convention used

`pinning/classic.pinned.tsv` — same 438 rows, same order, same 14 columns, only
`signal`, `role`, `attributes` filled.

Two row kinds are written differently, on purpose, because rule 1 and the worked
examples want different things:

- **Family rows (88 `L.*` nodes)** carry *only* values true of every descendant.
  A blank cell means "inherited, or descendants differ". Nothing is repeated from
  an ancestor.
- **Method rows (350 `M.*` nodes)** carry the **fully resolved** set
  (ancestor union + own additions − denials), as the worked-example table in
  `DRAFT_PHASE1_A.md` does. Redundant, but it makes the file usable for roll-ups
  without a resolver, and it is how the precedent entries are written.
- `!X` records a denial **declared at that node**. A denied value is already
  absent from the resolved sets of that node and its descendants; the `!` is
  there to say the denial was deliberate.
- Where resolution produced both an interior value and one of its own children
  (`S.src.ext` + `S.src.ext.human`), the interior one is dropped.

Coverage:

| axis | nodes with ≥1 value | values pinned |
|---|---|---|
| signal | 390 / 438 | 879 |
| role | 393 / 438 | 659 |
| attributes | 423 / 438 | 2128 |

Negative pins: **159 on 89 nodes**. Methods with no role at all: **4**. Methods
with no `S.form`: **40**. Methods with no `S.src`: **27**. Nothing in the region
was pinned to a value I invented.

---

## 1. The granularity problem, measured

This is the number the brief asked for.

Resolved roles per **method** node:

| roles | 1 | 2 | 3 | 4 | 5 | none |
|---|---|---|---|---|---|---|
| methods | 184 | 97 | 49 | 14 | 2 | 4 |

- mean **1.69** roles per method
- **46 %** of methods carry ≥2 roles, **19 %** carry ≥3
- role totals: `R.fit.est` 157, `R.fit.obj` 147, `R.fit.update` 118,
  `R.out.predict` 63, `R.data.repr` 57, `R.eval` 31, `R.out.calib` 28; everything
  else ≤13.

For comparison, the 37 worked examples in `DRAFT_PHASE1_A.md` average ≈1.5 roles
per entry, and the entries at ≥3 roles there are *all* acknowledged bundles
(DQN, MuZero, XGBoost, FixMatch). So the mismatch is real but it is not a clean
2× : the honest statement is that **classical entries are 10–15 % higher on mean
role count and ~2.5× more likely to sit at ≥3 roles**, and the ≥3 cases here are
not exceptional papers — they are ordinary ones (k-means, CART-style forests,
CRFs, change-point detectors, AdaBoost, causal forest).

Consequences for roll-ups, concretely:

- `R.fit.update` is carried by 118 nodes, of which roughly 60 are *tree or
  structure growth* (CART, every boosting entry, every forest, Theil-Sen, LARS,
  k-medoids), not a numeric step rule. A roll-up of "papers with a parameter
  update rule" therefore counts tree papers alongside Adam papers.
- `R.fit.est` is carried by 148 of 350 methods (42 %). In the deep branch that
  slot is rare (reparameterisation trick, REINFORCE estimator, STE). So
  "proportion of papers defining an estimator" is not comparable across branches
  at all: in classical work it is the default, not a contribution.
- The file marks `kind=bundle` on exactly **two** nodes (`M.xgboost`,
  `M.lightgbm`, both with `expands_to`). By the role count, **65** nodes behave
  as bundles. Phase-1 tension 1's third option (an explicit `slot` vs `bundle`
  marker) is, on this evidence, needed; the two existing bundle rows are not a
  representative sample of the problem, they are the two cases someone happened
  to decompose.

---

## 2. Homeless nodes, by axis

### 2.1 `S.src` — the measured outcome variable (the largest single gap)

`S.src.ext` has children for human labels, model-produced targets, programmatic
labels, preferences, demonstrations and co-occurring pairs. It has **no child for
"the response variable was measured or recorded in the world"** — a price, a
survival time, a claim count, a yield, a test score. That is the target of most
of classical statistics.

I did not force these onto `S.src.ext.human` (the worked-example precedent for
XGBoost). Instead **169 nodes** are pinned to the interior node `S.src.ext`,
which is honest about "the target comes from outside the run" and silent about
who produced it. Affected whole families: `L.lin` and all five children, `L.tree`,
`L.boost`, `L.bag`, `L.nb`, `L.kernel.svm`, `L.gp`, `L.seq.crf`, `L.seq.ts`,
`L.causal.*` (outcome side), `L.rec`, `L.symreg`, `L.prep.select`.

If this is left as-is, every `S.src.ext.*` roll-up in the classical branch reads
as "unknown annotation type" when the right answer is "no annotator exists".

### 2.2 `S.src` — the target of a surrogate / evaluation procedure

27 methods have **no `S.src` value**. Two distinct groups:

- **Surrogate search** (`L.hpo.model`, `M.gp-ei-bayesian-optimisation`, `M.tpe`,
  `M.smac`, `M.bore`, `M.bohb`): the surrogate is fitted to the *measured
  performance of an inner trial*. Not external annotation, not environment
  reward (nothing acts), not a function of the input.
- **Assessment procedures** (`L.test` ×7, `L.boot.ci` ×5, `L.boot.cv` ×7,
  `L.boot.perm` ×3): they are fitted to nothing; but `S.src.none` is excluded by
  its own negative test ("any fitted parameter, even a single calibration
  statistic") because a p-value or an interval *is* a calibrated quantity.

### 2.3 `S.form` — 40 methods with no comparison form

Grouped by what was missing:

| group | nodes | what was needed |
|---|---|---|
| resampling-based assessment | `M.bootstrap`, `M.bootstrap-t`, `M.bca-bootstrap`, `M.block-bootstrap`, `M.jackknife`, `M.k-fold-cv`, `M.stratified-cv`, `M.leave-one-out`, `M.nested-cv`, `M.time-series-cv`, `M.group-cv`, `M.k-fold-cross-validation`, `M.permutation-feature-importance` (13) | a criterion that is an *estimate of an estimator's own risk or variability* |
| hypothesis testing and error control | `M.t-test`, `M.anova`, `M.mann-whitney`, `M.chi-square`, `M.bonferroni`, `M.holm`, `M.benjamini-hochberg-fdr`, `M.permutation-test`, `M.randomisation-test` (9) | a criterion that is a *stated Type-I / FWER / FDR rate under a null* |
| correlation / variance-ratio projections | `M.cca`, `M.kernel-cca`, `M.deep-cca`, `M.pls-regression`, `M.fisher-lda` (5) | maximise an *association or between/within ratio*, not a per-example loss |
| robust regression with a chosen loss | `M.huber-regression`, `M.theil-sen`, `M.ransac` (3) | empirical risk under a loss that is not a standard likelihood (Huber), a median-of-slopes estimator (no criterion), an inlier-count criterion (RANSAC) |
| graph partition quality | `M.louvain`, `M.leiden`, `M.affinity-propagation` (3) | modularity maximisation / message-passing exemplar selection |
| relevance screening | `M.mutual-information-filtering`, `M.recursive-feature-elimination`, `M.boruta` (3) | a filter statistic used to select features |
| meta-procedures | `M.bagging` (1) | an ensemble shell has no form of its own, and `S.form.none` is forbidden because something *is* fitted |
| structure discovery by tests | `M.pc`, `M.fci`, `M.ccm` (3) | conditional-independence test outcomes as the criterion |

Separately, **`S.form.post`'s positive test is too narrow**. It says "approached
by sampling"; its examples include "Bayes rule updates". I pinned it on 53 nodes,
of which roughly 25 are closed-form conjugate inference with no sampling at all:
all of `L.gp` (exact GP posteriors), all of `L.seq.kalman`, `M.laplace-approximation`,
`M.expectation-propagation`, `M.belief-propagation`. Either the test is widened or
Gaussian-process and state-space inference are form-less.

### 2.4 `role` — 4 methods with no role, and one slot that does not exist

`M.pc`, `M.fci`, `M.ges`, `M.ccm` are pinned with **no role**. They induce a
*causal graph* from conditional-independence tests or a score. They are not data
preparation, not objective, not update, not estimator ("how an intractable
expectation or posterior is estimated" does not describe orienting edges), not
output-from-a-model, not evaluation. `R.search.arch` is NAS (searching a model's
structure as a hyper-procedure around a run), not structure estimation as the
run's product.

The same slot would clean up two documented stretches I had to accept:
tree induction and boosting split-finding currently sit on `R.fit.update` with
`A.deriv.comb` (precedent: XGBoost), and `L.symreg` sits on `R.search.arch`.

### 2.5 `role` — `R.out` assumes a trained model exists

`R.out.predict` was added (per its note) for k-NN. It is now carrying three
different jobs in this region:

1. a nonparametric prediction rule over stored data (k-NN, KDE, LOESS, RBF
   interpolation, GP posterior mean, kNN-CF) — what it was designed for;
2. decoding a structured output (Viterbi, CRF decoding) — fine;
3. **emitting a transductive grouping / embedding / score when no model was
   trained at all**: `L.clust.hier`, `L.clust.density`, `L.clust.graph` (14
   methods), `M.pagerank`, `M.shortest-paths`, plus `L.dimred.dist` which I put
   on `R.data.repr`.

For (3) the parent `R.out`'s own characteristic — "what the procedure contributes
*between a trained model and an emitted result*" — is false. DBSCAN's output is
not between anything. This is the clustering analogue of the k-NN finding that
forced `R.out.predict` in the first place, and it was not fixed by that addition.

### 2.6 `A.guar` — the two guarantees classical statistics actually claims

`A.guar` earns its place (146 values pinned: `consist` 73, `conv` 41, `unbias` 21),
but two of its children are nearly unused here (`cert` 0, `approx` 2, `regret` 1)
while the two most common claims in the branch have no value:

- **Asymptotic coverage.** `A.guar.cover` explicitly excludes it ("guarantees
  only asymptotic coverage" is its *negative* test). So bootstrap intervals,
  Wald/profile-likelihood CIs, GLM and mixed-model CIs, and every causal
  estimator's CI have no guarantee value — 90 nodes carry `A.uncert.interval`
  and only 4 could take `A.guar.cover` (the permutation tests, which are exact).
- **Error-rate control.** Bonferroni/Holm/BH-FDR and every hypothesis test
  control a Type-I error, FWER or FDR. `A.guar.cover` is about coverage of an
  interval, not the level of a test.

### 2.7 `A.uncert` — no value for a predictive distribution

`A.uncert` = {point, interval, posterior, ensemble}. A method that returns a full
*conditional distribution of the outcome for each new input* fits none of them:
`M.quantile-regression` (pinball loss), `M.ngboost`, `M.prophet`,
`M.structural-time-series` forecast densities, distributional forests. I pinned
`point` or `interval` and it is wrong in both directions.

### 2.8 `A.param` — no value for "produces no object about data points at all"

`A.param.trans` ("produces an output only for the points it was given") is
carried by 106 nodes. Roughly 26 of them are not transductive in that sense at
all: a t-test, a bootstrap interval, a cross-validation score, an IPS value
estimate produce *a verdict about an estimator*, not per-point outputs. The
precedent already stretched this for MCMC ("a stretch", per the NUTS note); this
region stretches it 26 more times.

### 2.9 `A.deriv.closed` is absorbing fixed-point iteration (most load-bearing defect)

`A.deriv.closed` says "obtains the solution by solving an equation or
decomposition in one shot" and its **negative test is "iterating a step rule to
convergence"**. The precedent nonetheless pins EM as `A.deriv.closed`. Following
it, I pinned `A.deriv.closed` on 144 nodes — and roughly 60 of them *iterate*:
the whole `L.em` subtree, IRLS/Fisher scoring in `L.lin.glm`, k-means, ALS, NMF
multiplicative updates, mean-shift, affinity propagation, belief propagation,
PageRank power iteration, CAVI, Kalman recursions, soft-impute.

So the value is currently true-by-precedent and false-by-test for the majority of
its uses in this region. Either the test changes, or a value is added (§3).

---

## 3. Proposed new axis values

Proposals only — nothing below was added to the tables.

| id | name | parent | positive_test | nodes that need it |
|---|---|---|---|---|
| `S.src.ext.obs` | Measured outcome variable | `S.src.ext` | the target is an outcome measured or recorded in the world; no annotator, rule or model produced it | 169 nodes now parked on the interior `S.src.ext`: all `L.lin.*`, `L.tree`, `L.boost`, `L.bag`, `L.nb`, `L.kernel.svm`, `L.gp`, `L.seq.ts`, `L.seq.crf`, `L.causal.*`, `L.rec`, `L.symreg` |
| `S.src.trial` | Measured performance of an inner run | `S.src` | the target is the measured score of a configuration or trial that this run itself executed | `L.hpo.model`, `M.gp-ei-bayesian-optimisation`, `M.tpe`, `M.smac`, `M.bore`, `M.bohb`; arguably `L.boot.cv` |
| `S.form.assess` | Out-of-sample risk or sampling-variability estimation | `S.form` | the computed quantity is an estimate of an estimator's own risk or variability, obtained by refitting on resampled or held-out data | `L.boot.ci` +5, `L.boot.cv` +7, `M.jackknife`, `M.permutation-feature-importance` (13) |
| `S.form.level` | Error-rate control under a null | `S.form` | the criterion is a stated Type-I error, FWER or FDR under an explicit null distribution | `L.test` +7, `L.boot.perm` +3, `M.chaid`, `M.conditional-inference-trees`, `M.cusum`, `M.pc`, `M.fci`, `M.boruta` (≈16) |
| `S.form.assoc` | Association maximisation | `S.form` | maximises an explained correlation, covariance or between/within variance ratio between variable sets, with no per-example loss | `L.dimred.disc` +5 (`M.cca`, `M.kernel-cca`, `M.deep-cca`, `M.pls-regression`, `M.fisher-lda`) |
| `S.form.risk` | Empirical risk under a chosen pointwise loss | `S.form` | minimises an average per-example loss selected for its shape or robustness, not stated as a log-likelihood | `M.huber-regression`, `M.m-estimators`, `M.loess`, `L.lin.robust`, and (honestly) a share of the 134 nodes I pinned `S.form.lik` on the Gaussian-likelihood reading |
| `S.form.part` | Graph partition quality | `S.form` | maximises modularity or minimises a graph cut / partition score defined on an adjacency or similarity graph | `M.louvain`, `M.leiden`, `M.affinity-propagation`, `M.normalised-cuts`, `L.clust.graph` |
| `R.fit.struct` | Structure induction | `R.fit` | produces the discrete structure of the fitted object (graph, tree, variable set, expression) by search over structures, rather than by updating numeric parameters | `M.pc`, `M.fci`, `M.ges`, `M.ccm` (currently role-less); would also take `L.tree` (+5), `L.boost` (+7), forests, `M.notears`, `M.dag-gnn`, `L.symreg`, `L.prep.select` off `R.fit.update`/`R.search.arch` |
| `R.out.struct` | Transductive structure output | `R.out` (with `R.out`'s characteristic reworded) | the run's output is a grouping, embedding, ordering or score over exactly the points it was given; new points need a refit | `L.clust.hier` +3, `L.clust.density` +4, `L.clust.graph` +5, `L.dimred.dist` +8, `L.semi.graph` +3, `M.pagerank`, `M.shortest-paths` (≈26) |
| `R.eval.interval` / `R.eval.test` / `R.eval.select` / `R.eval.resample` | children of `R.eval` | `R.eval` | — | 31 nodes in this region sit on the single leaf `R.eval` while `R.fit` has 8 children; interval estimation, significance testing, multiplicity control, CV-based selection and off-policy evaluation are not one slot |
| `A.deriv.fixed` | Fixed-point or majorisation iteration | `A.deriv` | iterates an analytic update map derived from the model (E/M steps, IRLS, power iteration, message passing, multiplicative updates) rather than stepping along a gradient | ≈60 of the 144 nodes now on `A.deriv.closed`: `L.em` subtree, `L.lin.glm`, `L.clust.centroid`, ALS, NMF, `M.mean-shift`, `M.affinity-propagation`, `M.belief-propagation`, `M.pagerank`, `M.cavi`, `L.seq.kalman` |
| `A.guar.asym` | Asymptotic coverage or level | `A.guar` | a stated coverage probability or test level that holds as sample size grows | `L.boot.ci` +5, `L.lin.ols`, `L.lin.glm`, `L.lin.mixed`, `L.mle`, `L.causal.*`, `L.test` — i.e. most of the 90 nodes carrying `A.uncert.interval` |
| `A.uncert.pred` | Predictive distribution | `A.uncert` | returns a full conditional distribution (or a set of quantiles) of the outcome for each new input | `M.quantile-regression`, `M.ngboost`, `M.prophet`, `M.structural-time-series`, `L.seq.ts` forecast densities |
| `A.param.none` | Produces no object about data points | `A.param` | the run's product is a verdict or a scalar estimate about an estimator, not a map or a stored set of points | `L.test` +7, `L.boot.ci` +5, `L.boot.cv` +7, `M.inverse-propensity-scoring`, `M.self-normalised-ips`, `M.doubly-robust-ope` (≈26 now on `A.param.trans`) |

Also recommended without a new id: **widen `S.form.post`'s positive test** to
"approached by sampling *or by a closed-form conjugate update*" (§2.3), and
**widen `R.out`'s characteristic** so it does not presuppose a trained model
(§2.5).

---

## 4. Multi-value attribute families

Families where I had to pin two values from one family, with the node that forced
it. `A.deriv`, `A.guar` and `A.privacy` are already declared multi-valued; the
rest are declared **single**-valued, so these are findings.

| family | declared | nodes | forced by |
|---|---|---|---|
| `A.uncert` | single | **27** | **`M.ols`** — a classical estimator reports a point estimate *and* a standard error / CI, and both are what the method is for. Same for `M.glm`, `M.mle`, `M.m-estimation`, `M.generalised-method-of-moments`, `M.gee`, `M.linear-mixed-models`, `M.partial-likelihood-cox`, `M.arima`, `M.prophet`, and the rest of `L.mle`/`L.lin.ols`/`L.lin.glm`/`L.lin.mixed`/`L.seq.ts`. **Recommendation: `A.uncert` must be multi-valued, or it must be split into "what is returned about the parameter" and "what is returned about a prediction".** |
| `A.deriv` | multi (confirmed) | 32 | `M.hmc`/`M.nuts` (sample+first, the precedent case), `M.xgboost`/`M.lightgbm`/`M.catboost` (comb+second), `M.gibbs` (sample+closed), `M.propensity-score-matching` (closed+comb), `M.k-medoids-pam`, `M.sparse-pca`, `M.entropy-balancing`, `M.rotation-forest` |
| `A.guar` | multi (confirmed) | 12 | `M.tmle`, `M.aipw-doubly-robust`, `M.ipw`, `M.double-ml`, `M.doubly-robust-ope`, `M.ols` (consistency + unbiasedness are *different* selling points and papers claim both); `M.k-means-plus-plus` (convergence + approximation ratio) |
| `A.param` | single | 0 written, 1 real | **`L.rec.cf`**: an id-indexed factorisation is `param` for known users/items and needs a refit for new ones (`trans`). I pinned `trans` and denied `param`; neither is right. Cold start is a genuine two-value case. |
| `A.outspace` | single | 0 written, 4 real | change-point detectors (`M.cusum`, `M.pelt`, `M.matrix-profile`, `M.bayesian-online-change-point-detection`) operate on a continuous series and emit a structured segmentation. I denied `cont` and kept `struct`. |
| `A.cadence` | single | 0 written, 2 real | `L.seq.kalman`: the filter is `stream`, the smoother over the same model is `full`; `L.seq.pf` likewise. Resolved per method with denials. |

---

## 5. Negative pins used (159 on 89 nodes)

Grouped by what the denial is for. The full list is in the TSV (`!` prefix).

**(a) Multi-parent `divides` edges whose second parent is a different kind of
thing — 52 denials.** This is the dominant cause and the one worth acting on.

| node | denies | because |
|---|---|---|
| `M.viterbi` (`L.seq.hmm; L.optdisc`) | 8: `S.src.self.struct`, `S.form.lik`, `R.fit.est`, `R.fit.update`, `A.deriv.closed`, `A.guar.conv`, `A.param.param`, `A.cadence.full` | Viterbi fits nothing; it inherits a whole EM-family profile through `L.seq.hmm ← L.em` |
| `L.hpo.model` (`L.hpo; L.gp`) | 7: `S.src.ext`, `S.form.post`, `R.fit.est`, `R.out.predict`, `A.deriv.closed`, `A.determinism.det`, `A.param.inst` | the edge is "the surrogate is a GP", not "BO is a kind of GP inference"; TPE/SMAC/BORE use no GP at all |
| `M.simulated-annealing`, `M.basin-hopping` (`L.derivfree.anneal ← L.mcmc.temper`) | 6 each | they are optimisers, not samplers: no posterior, no `R.fit.est`, no `A.deriv.sample` |
| `L.prep.select` (`L.prep; L.lin.pen`) | 4: `S.form.lik`, `S.form.spars`, `R.fit.obj`, `R.fit.update` | the edge is "lasso can select features"; mutual-information filtering fits no linear model |
| `L.anom.isol` (`L.anom; L.tree`) | 4: `S.src.ext`, `S.form.lik`, `R.fit.obj`, `A.determinism.det` | isolation forests are unsupervised, objective-free and randomised |
| `M.matrix-profile` (`L.anom.cp ← L.seq.ts`) | 5 | a distance computation, not a fitted autoregressive model |
| `L.causal.struct`, `L.anom.cp`, `L.retr.index`, `L.interp.dict`, `L.boot.perm`, `M.lsh`, `M.kernel-pca`, `M.kernel-cca`, `M.ccm`, `M.weisfeiler-lehman-kernel`, `M.lingam` | 1–2 each | same pattern |

**(b) The neural member of a classical family — 18 denials.**
`M.deep-gp`, `M.deep-cca`, `M.deep-iv`, `M.svgp`, `M.neural-cf`,
`M.adversarial-debiasing`, `M.deep-svdd`, `M.dag-gnn` deny
`A.deriv.closed` / `A.cadence.full` / `A.determinism.det` / `A.param.trans`.

**(c) The Bayesian member — 8 denials.** `M.bayesian-gmm`,
`M.dirichlet-process-mixtures`, `M.latent-dirichlet-allocation`,
`M.probabilistic-pca`, `M.bart-for-causal-effects`, `M.cevae`,
`M.structural-time-series`, `M.vae-elbo-scoring` deny `A.uncert.point`.

**(d) The online/streaming member — 11 denials.** `M.sgld`, `M.sghmc`,
`M.mini-batch-k-means`, `M.incremental-pca`, `M.particle-filter`,
`M.auxiliary-particle-filter`, `M.rrcf`, `M.cusum`,
`M.bayesian-online-change-point-detection`, `M.bpr`, `M.svd-plus-plus` deny
`A.cadence.full`.

**(e) A method whose criterion differs from its family's — 12 denials.**
`M.gee`, `M.m-estimation`, `M.method-of-moments`,
`M.generalised-method-of-moments` deny `S.form.lik` for `S.form.moment`;
`M.structured-svm`, `M.structured-perceptron`, `M.lambdamart` deny `S.form.lik`;
`M.expectation-propagation`, `M.autoencoder-reconstruction-error`,
`M.diffusion-reconstruction-scoring` deny `S.form.bound`; `M.bpr` and
`M.user-knn-and-item-knn-cf` deny `S.form.recon`; `M.sindy` denies
`S.src.theory` and `S.form.resid` (SINDy *discovers* a law, it does not impose
one); `M.total-least-squares` denies `A.guar.unbias`; `M.ransac` and
`M.theil-sen` deny `R.fit.obj` (they minimise no criterion).

**Verdict on the escape hatch:** it is necessary and it works. But 52 of 159
denials exist only to undo a `divides` edge, which means the lineage axis is
currently paying for inheritance it did not intend. Either `divides` edges should
not propagate axis values (only `instantiates`/`derives-from` should), or
multi-parent nodes need a declared "primary" parent for inheritance.

---

## 6. Nodes I could not pin, and the review flags

- **No node in the region is empty on all three axes except five family rows**:
  `L.boot`, `L.kernel`, `L.fair.pre` (empty because their descendants genuinely
  share nothing — see §8), and `L.mcmc.mh`, `L.mcmc.temper` (empty because they
  add nothing to `L.mcmc`; that is inheritance working, not a gap).
- **4 methods have no role**: `M.pc`, `M.fci`, `M.ges`, `M.ccm` (§2.4).
- **96 nodes carry the review flag** "lowercase descriptive string — confirm it
  is a named procedure". My reading: **the flag is mostly a false positive.**
  Lowercase is simply how statistics writes method names — lasso, random forest,
  isolation forest, logistic regression, bootstrap, permutation test, propensity
  score matching, difference-in-differences, synthetic control, label
  propagation, spectral clustering, nested sampling are all named, citable
  procedures. All 96 pinned cleanly on at least role and attributes; only 5 are
  missing a signal value, and for the same reasons as their uppercase siblings.
  The ones I would genuinely reclassify as *descriptions of a class, not
  procedures*: `M.fair-regularisers`, `M.fair-representation-learning`,
  `M.group-wise-thresholds`, `M.genetic-symbolic-regression`,
  `M.neural-guided-symbolic-regression`, `M.doubly-robust-estimation`,
  `M.penalised-likelihood`, `M.dictionary-learning-on-activations` (8).
- **Duplicate nodes (a counting hazard, not an axis problem).** At least 14
  pairs/triples denote the same procedure at different nodes and will double
  count in any roll-up: `M.gibbs`/`M.gibbs-sampling`,
  `M.metropolis`/`M.metropolis-hastings`, `M.mala`/`M.langevin-mala`,
  `M.k-fold-cv`/`M.k-fold-cross-validation`,
  `M.kernel-ridge`/`M.kernel-ridge-regression`,
  `M.als`/`M.als-collaborative-filtering`/`M.als-matrix-factorisation`,
  `M.ward-linkage`/`M.single-complete-average-ward-linkage`,
  `M.svm`/`M.hard-and-soft-margin-svm`, `M.hmm` vs `L.seq.hmm`, `M.crf` vs
  `L.seq.crf`, `M.glm` vs `L.lin.glm`, `M.em` vs `L.em`,
  `M.isolation-forest`/`M.extended-isolation-forest` (arguably distinct),
  `M.doubly-robust-estimation`/`M.aipw-doubly-robust`/`M.doubly-robust-ope`,
  `M.truncated-svd`/`M.randomised-svd`/`M.random-svd-sketching`. Also
  `M.parallel-tempering` sits under `L.derivfree.anneal` while being listed as an
  example of `L.mcmc.temper`.

---

## 7. The three values added late for this region — do they hold up?

**`S.form.moment` (estimating-equation solving): yes, and it is load-bearing.**
34 pins. Without it, every CATE estimator, every IV estimator, GEE, M-estimation,
method of moments, GMM, entropy balancing, DiD, IPS/SNIPS/DR-OPE and the
TMLE targeting step would be form-less — 20+ nodes. Two observations:

1. It turned out to be the right home for something nobody designed it for:
   **cumulant / moment-matching ICA** (`M.jade`, `M.sobi`, `M.fastica`) and
   `M.expectation-propagation` (moment matching), which otherwise had no form.
2. It does **not** distinguish a just-identified estimating equation from an
   over-identified GMM with a weighting matrix, and it co-occurs with
   `S.form.lik` on every doubly-robust estimator (the nuisance models are
   likelihoods). So a form roll-up cannot separate "a moment estimator" from "a
   likelihood model with a moment correction".

**`A.guar` (formal-guarantee family): necessary but incomplete.** 146 pins. It is
the only axis on which conformal-style and causal-style claims are visible at
all. But its child set is shaped by the deep/online-learning literature: `cert`
is unused here, `approx` twice, `regret` once, while the two claims classical work
actually makes — asymptotic interval coverage and test-level control — have no
value (§2.6). Add `A.guar.asym` (and either widen `cover` or add a level value)
and this family becomes the strongest axis in the region.

**`R.out.predict` (nonparametric prediction rule): necessary, and now
overloaded.** 63 pins; without it k-NN, KDE, LOESS, RBF interpolation, GP
posterior mean, Viterbi, kNN-CF and all of density/hierarchical/graph clustering
have no role. But it is doing three jobs and its parent's definition is wrong for
one of them (§2.5). The fix is not a fourth job: it is `R.out.struct` plus a
reworded `R.out`.

**`R.eval`: the branch the brief wants first-class is one undifferentiated
leaf.** 31 pins, no children, and phase-1 tension 4 (does evaluation belong at
all?) is still open. If it is ruled out of scope, 26 nodes
(`L.test` + `L.boot.ci` + `L.boot.cv` + `L.boot.perm` subtrees) lose their only
role and become unpinnable; if it is in, it needs children and the participant
rule needs its fourth clause. This decision blocks more of this region than any
other open question.

---

## 8. Things that made me doubt an axis

1. **Hub family nodes end up empty, and that is a lineage problem showing up on
   the axes.** `L.boot`, `L.kernel`, `L.fair.pre`, `L.ls`, `L.em`, `L.graphalg`
   share almost nothing with their descendants, because they are not procedure
   families — they are *tricks* (`L.kernel`: substitute a kernel), *solver
   classes* (`L.ls`: closed-form), or *stages* (`L.fair.pre`). `L.boot` is the
   worst: bagging and cross-validation are both "resample and refit", and they
   agree on no axis value whatsoever (`R.out.agg` vs `R.eval`). A roll-up over
   `L.boot` means nothing. 41 of 88 family nodes have an empty `role` cell.
2. **`A.deriv` mixes "what information the step uses" with "what class of
   algorithm it is".** `first`/`second` are information; `closed`/`comb`/`sample`
   are algorithm classes; and `closed` is additionally absorbing fixed-point
   iteration against its own negative test (§2.9). This is why it needed to be
   multi-valued: the two questions are orthogonal, so of course some methods need
   one value of each.
3. **`A.cadence`'s scope note ("to iterative fitting procedures", negative test
   "a one-shot closed-form fit") contradicts the precedent**, which pins
   `A.cadence.full` on closed-form fits (EM, TMLE, L-BFGS, GPTQ). I followed the
   precedent — 297 nodes carry `A.cadence.full` — but under the scope note as
   written, most of them should take no value. Decide which it is; the number of
   affected nodes is enormous.
4. **`S.src.self.struct` is doing two jobs.** It is the "classical-unsupervised
   home" (k-means distortion, PCA variance) *and*, by the NUTS precedent, the
   source for "a posterior given the whole dataset". 144 pins. Those are not the
   same relation to the data, and merging them means `S.src` cannot distinguish
   unsupervised structure learning from Bayesian inference about any model.
5. **`R.adapt` / `R.exp.*` / `R.exec.*` / `R.rewrite.*` are entirely unused in
   this region** (0 pins), as expected. Combined with tension 2, that supports
   marking role children and attribute families with scope conditions rather than
   treating them as peers — otherwise `role` looks like a 23-value axis of which
   16 are used here and `attributes` looks mostly empty.
6. **Two roles I would merge, tentatively**: `R.fit.est` and `R.fit.update`
   co-occur on 39 nodes in this region (EM, every mixture model,
   k-means, boosting, PLSA), and the distinction — "estimates an
   intractable quantity" vs "maps that to a parameter change" — is a *sentence
   boundary inside one algorithm*, not two citable contributions. In the deep
   branch they separate cleanly (reparameterisation trick vs Adam). I did not
   merge them, because `R.fit.est`'s own note says it is "the slot that makes
   classical statistics fit"; but if a reviewer wants a slot removed, this pair is
   where the evidence is.
7. **`R.data.repr` is being used for feature *selection*** (`L.prep.select`,
   `M.lasso-selection`, RFE, Boruta, 4 nodes) and for *producing a kernel feature
   map* (`L.kernel.approx`, `M.weisfeiler-lehman-kernel`). Its positive test is
   about *constructing* the units a model consumes; nothing is constructed when
   variables are dropped. Minor, but it is a second instance of the same pattern
   as §2.5: a slot defined from the deep pipeline being stretched sideways.
