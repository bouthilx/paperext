# Re-pinning the 155 `A.deriv.closed` leaves

Input `fix/deriv_closed_leaves.tsv` (155 rows, every row carrying `A.deriv.closed`),
output `fix/deriv_closed_leaves.pinned.tsv` — same columns, same order, same 155 rows,
`attributes` / `role` / `notes` only.

Resolved pins (not raw columns) were read with `resolve.py --node` for all 155 before
any edit, so "the role it already has" means the role after inheritance and denials.

---

## 1. Counts

| bucket | nodes |
|---|---|
| `A.deriv.closed` only — no change | **101** |
| `A.deriv.fixed` only — `closed` replaced | **6** |
| **both** `closed` + `fixed` | **42** |
| **neither** — `closed` dropped, nothing added | **6** |

`A.deriv.closed` survives on 143 of 155. `A.deriv.fixed` is now carried by 48.
`R.fit.fixpoint` added to **31** nodes. `A.param.none` added to **1**.

The test applied was the mechanical one: *one solve* (normal equation,
eigendecomposition, SVD, matrix inverse, DP pass) versus *iterating a map until it
stops moving*. Two standing rules were derived from it and applied uniformly:

- **Numerical linear algebra's internal iteration is implementation, not method.**
  A method defined as "compute this decomposition" is `closed` even though LAPACK
  reaches the eigenvectors by iteration: PCA, Fisher LDA, CCA, kernel PCA/CCA, MDS,
  Isomap, LLE, Laplacian eigenmaps, truncated/randomised SVD, normalised cuts,
  spectral clustering, total least squares. A method whose *named algorithm* is the
  iteration gets `fixed`: NIPALS (PLS), FastICA (LiNGAM), Jacobi joint
  diagonalisation (JADE, SOBI), Lloyd (k-means), EM.
- **A downstream subroutine that has its own node does not re-pin its parent.**
  Spectral clustering ends in k-means and was still left `closed` only; the
  k-means iteration is pinned on `M.k-means`. This is the single most arguable of
  the 101 no-changes and is flagged below.

---

## 2. The 42 nodes given both, and the argument

The argument is the same shape in most cases — **a closed-form inner solve inside a
convergent outer loop** — so they are grouped by that shape. Per-node wording is in
the `notes` column of the output.

### 2a. EM and its subtree (13) — the inner maximisation is closed-form, E/M alternate to convergence
`M.em`, `M.hard-em`, `M.variational-em`, `M.baum-welch`, `M.hmm`, `M.hsmm`,
`M.gaussian-mixture-models`, `M.bayesian-gmm`, `M.latent-class-analysis`,
`M.plsa`, `M.dawid-skene`, `M.mace`, `M.gmm-likelihood-scoring`.

Phase 1's EM worked example is the origin of the defect, and this is the group it
propagated through. `M.gmm-likelihood-scoring` is in because its own role includes
`R.fit.est`, i.e. the node owns the mixture fit and not only the density evaluation.
`M.generalised-em` is deliberately **not** here — see §3.

### 2b. Alternating / block-coordinate solves (7) — each block solved exactly, blocks alternated
`M.als`, `M.als-collaborative-filtering`, `M.als-matrix-factorisation`,
`M.dictionary-learning`, `M.dictionary-learning-on-activations`, `M.soft-impute`,
`M.sindy`.

`M.soft-impute` is the cleanest instance in the file: its step is literally an SVD
with a soft-thresholded spectrum, re-run until the completion stops moving — one
closed-form decomposition per iteration, iterated. `M.sindy`'s solver (sequentially
thresholded least squares) is a closed-form regression re-solved until the active
support stops changing.

### 2c. Centroid clustering (6) — closed-form mean, reassignment, halt on no change
`M.k-means`, `M.k-means-plus-plus`, `M.kernel-k-means`, `M.mini-batch-k-means`,
`M.fuzzy-c-means`, `M.deepcluster`.

`M.deepcluster` now carries `first` + `closed` + `fixed`: the gradient half, the
closed-form centroid, and the k-means loop are three different true statements.
`M.mini-batch-k-means` is the weakest: Sculley calls it gradient descent, but the
pinned attributes carry no `A.deriv.first` and the update is a running average, so it
was treated as the k-means map on a sample.

### 2d. Message passing / propagation with a closed-form alternative (5)
`M.expectation-propagation`, `M.gp-classification-by-laplace-or-ep`,
`M.harmonic-functions`, `M.label-propagation`, `M.label-spreading`.

EP's site update solves a moment-matching equation in closed form and the sites are
refreshed to a fixed point. The three propagation nodes have a published closed-form
linear solve on the graph Laplacian *and* a published iteration, and the literature
uses both — a genuine disjunction inside one node, not a conflation.

### 2e. Variational coordinate ascent (3)
`M.cavi`, `M.mean-field-vi`, `M.latent-dirichlet-allocation`. Each coordinate update
is the closed-form conjugate optimum; the sweep repeats until the bound stops moving.
`CAVI` is named in `A.deriv.fixed`'s own example list.

### 2f. Classical multivariate methods whose named algorithm iterates (5)
`M.jade`, `M.sobi`, `M.lingam`, `M.pls-regression`, `M.probabilistic-pca`.

**These five are the weakest "both" calls in the set.** JADE and SOBI compute their
cumulant or lagged-covariance matrices in one shot and then run Jacobi sweeps of
closed-form rotations until the off-diagonal mass stops moving. LiNGAM's core is
FastICA, a named fixed-point algorithm. PLS's NIPALS iterates per component (SIMPLS
does not). PPCA has both a one-shot eigen solution and the EM algorithm Tipping and
Bishop published for it. A reader who takes "the method is the decomposition" will
want all five back to `closed` only; they are easy to revert as a group.

### 2g. One RL node (1)
`M.fqe`. Fitted Q evaluation re-fits a regressor to bootstrapped targets until the Q
estimate stops moving — approximate value iteration, a fixed point of the Bellman
operator, over an inner solve. It already carried `first` and `closed`; `fixed` is the
outer loop neither of those described.

### 2h. Tokenisation (2)
`M.sentencepiece-unigram`, `M.unigram-lm`. Each pruning round runs EM over closed-form
expected counts to convergence.

---

## 3. The 6 given `fixed` alone, and why `closed` was false

| node | why not closed |
|---|---|
| `M.pagerank` | the method *is* the power iteration; the equivalent linear solve is not what the paper does |
| `M.belief-propagation` | a message is an arithmetic sum-product, not an equation solved for |
| `M.affinity-propagation` | responsibilities/availabilities iterate until the exemplar set stops changing; nothing is solved |
| `M.mean-shift` | iterate the kernel-weighted mean map per point; no solve |
| `M.k-medoids-pam` | the medoid is chosen by **enumeration** (`A.deriv.comb`, already pinned) and the swap map is iterated — there is no algebraic solve anywhere in PAM, so `closed` was simply wrong |
| `M.generalised-em` | generalised EM is *defined* by its M-step not being a closed-form maximisation — any improvement step will do. It is the one node in the EM subtree where only the iterate-to-convergence half is true, which is a useful sharpness test for the new value |

---

## 4. The 6 given neither — a third failure mode the brief did not anticipate

`M.gibbs`, `M.gibbs-sampling`, `M.blocked-gibbs`, `M.collapsed-gibbs`,
`M.slice-sampling`, `M.dirichlet-process-mixtures`.

All six already carry `A.deriv.sample`. `A.deriv.closed`'s negative test ("iterating a
step rule to convergence") fires on them, and `A.deriv.fixed`'s negative test ("drawing
from a distribution") fires too. So the honest answer is *neither*, and `A.deriv.closed`
was dropped with no replacement.

What `A.deriv.closed` was recording on these nodes is that **the model's conditionals
are conjugate** — a property of the model, not information the step rule consumes. That
is a different question from the one `A.deriv` asks, and it is the same category of
error as the EM precedent: a true statement filed under a value whose test it fails.

`M.dirichlet-process-mixtures` is the only judgement call in the six: variational DP
(truncated stick-breaking CAVI) would be `fixed`, but the node is pinned
`A.deriv.sample` + `A.determinism.stoch`, i.e. the collapsed-Gibbs reading, so it was
treated with the rest.

---

## 5. `R.fit.fixpoint` — 31 nodes, under a stated rule

Added **iff** the node resolves `A.deriv.fixed` **and** either

1. it carries `R.fit.update`, whose positive test is *"maps a gradient and optimiser
   state to a parameter change"* and the procedure forms no gradient (21 nodes:
   the three ALS, `baum-welch`, `bayesian-gmm`, `em`, `gaussian-mixture-models`,
   `hmm`, `hsmm`, `plsa`, `dictionary-learning`, `fuzzy-c-means`, `generalised-em`,
   `hard-em`, `k-means`, `k-means-plus-plus`, `k-medoids-pam`,
   `latent-class-analysis`, `mini-batch-k-means`, `soft-impute`, `variational-em`); or
2. it resolves to **no `R.fit.*` value at all** and the fixed point it iterates to *is*
   the procedure's whole output (9 nodes: `dawid-skene`, `mace`, `pagerank`,
   `affinity-propagation`, `harmonic-functions`, `kernel-k-means`, `label-propagation`,
   `label-spreading`, `mean-shift`); or
3. the axis table names the method in `R.fit.fixpoint`'s own example list
   (1 node: `belief-propagation`, whose only role was `R.fit.est`).

**Nothing was removed.** The 21 wrong `R.fit.update` pins are still there — undoing
them needs negative pins or deletions, which is outside this task, but they are the
obvious follow-up: `R.fit.update` is carried by 118 nodes and §9 of
`PINNING_FINDINGS.md` already measured that ~60 of them are not step rules.

**Deliberately not added**, so the rule stays legible: nodes that resolve
`A.deriv.fixed` but already have a correct `R.fit.*` slot — `cavi`, `mean-field-vi`,
`expectation-propagation`, `gp-classification-by-laplace-or-ep`,
`latent-dirichlet-allocation`, `probabilistic-pca`, `fqe` (all `R.fit.est`), `sindy`,
`deepcluster`, `dictionary-learning-on-activations` (all `R.fit.obj`) — and the nodes
whose fixed-point sweep is an inner subroutine of a representation-construction method
rather than the output: `jade`, `sobi`, `lingam`, `pls-regression`,
`sentencepiece-unigram`, `unigram-lm` (all `R.data.repr`).

One incidental defect found while resolving: **`M.lingam` resolves to no role at all.**
Its own pin is `R.fit.est` and its parent `L.causal.struct` carries `!R.fit.est`, so the
denial cancels the child's own assertion. Left alone — it is a lineage defect, not an
`A.deriv` one.

---

## 6. `A.param.none` — 1 node, and why the harvest is this small

Exactly **three** of the 155 resolve to no `A.param` value, so three were candidates:

| node | verdict |
|---|---|
| `M.reweighing` | **`A.param.none` added.** The run computes per-example weights that the downstream learner consumes inside the same run; nothing survives it that could be applied to anything. Arguable: the reweighing rule `w(a,y)` is a function of group and label and *could* be applied to a new example, which would make it `A.param.param`. Taken as `none` because the weights are an intermediate, not the run's deliverable. |
| `M.ucb-v` | **not added.** Its sibling `M.ucb1` resolves `A.param.param` through `L.bandit.stoch`; `M.ucb-v` is blank only because its parent `L.explore.opt` pins no attributes at all. The right fix is `A.param.param` on the family, not `none` on the leaf. |
| `M.mahalanobis-score` | **not added.** It fits a class-conditional mean and a shared covariance and scores unseen inputs with them — `A.param.param`, blank only because `L.calib.ood` pins nothing but `A.determinism.det`. |

**Finding: `A.param.none` is not the fix for this region's `A.param` blanks.** The
168/308 blanks that motivated the value live in the generative and systems regions,
where runs really do leave nothing behind. These 155 are estimation, inference and
preprocessing procedures, and every one of them leaves an artifact; the three blanks
here are *missing family defaults*, which `A.param.none` cannot supply. §7 of
`PINNING_FINDINGS.md` asked for family-level defaults with only deviations pinned —
that is what these three need.

---

## 7. Where `A.deriv` is asking two questions at once

**This is the main finding, and it is structural: `A.deriv.fixed` is not a sibling of
the other six values.**

`A.deriv.first`, `.second`, `.zero`, `.closed`, `.comb` and `.sample` all answer
*"what information does one step consume?"*. `A.deriv.fixed` answers *"what stops the
loop?"*. That is why 42 nodes are legitimately both: the step consumes a solved
equation **and** the loop halts when the iterate stops moving. Those are two
independent questions and the family's own characteristic — "what information about the
objective the step rule consumes" — only names the first.

If this were split into **inner-step information** × **outer-loop termination**, every
one of the 42 would become a single value on each facet, `A.deriv.closed`'s negative
test ("iterating a step rule to convergence") would stop being a contradiction, and the
MCMC six would land on (`sample`, `converged-chain`) instead of nothing. This is the
same shape as the three conflations §2 of `PINNING_FINDINGS.md` already names for
`A.uncert`, `A.outspace` and `A.topology`, and the evidence here is stronger: 42 of 155
pins on one family, with a mechanical rather than a judgement-based derivation.

Other nodes where the family is being asked two things:

- **The five Kalman nodes** (`M.kalman-filter`, `M.ekf`, `M.ukf`, `M.rts-smoother`,
  `M.information-filter`) — see §8, this is the sharpest case.
- **The five model-based HPO nodes** (`M.bohb`, `M.tpe`, `M.smac`, `M.bore`,
  `M.gp-ei-bayesian-optimisation`) carry `closed` *and* `zero`: `closed` for the inner
  surrogate fit, `zero` for the outer search over configurations. One node, two nested
  procedures, one `A.deriv` pin set that cannot say which value belongs to which loop.
  Left unchanged — neither is wrong, but the pair is uninterpretable.
- **The four index bandits** (`M.ucb1`, `M.kl-ucb`, `M.linucb`, `M.lints`) carry
  `closed` for computing an index, while the search they perform is over arms.
  `A.deriv`'s scope predicate — "any procedure that searches a parameter or
  configuration space" — barely applies, and the value describes a side computation.
- **`M.mice`** is a Gibbs sampler over conditional regressions: each conditional is a
  closed-form solve, the chain iterates, and the imputations are *drawn*, so
  `A.deriv.fixed`'s negative test fires. Left `closed` only; the correct pin is
  probably `closed` + `sample`, which is outside this task's mandate.
- **`M.adaboost`** carries `closed` + `comb`: the analytic `alpha` is closed-form, the
  stump search is enumeration, and the stagewise additive loop is neither — it is
  coordinate descent on the exponential loss. No value in the family describes a
  greedy stagewise ensemble growth, which is §9 of `PINNING_FINDINGS.md`'s observation
  about `R.fit.update` arriving on the attributes axis.
- **`M.mds`** is one node covering classical MDS (one eigendecomposition) and metric
  MDS by SMACOF (majorisation iterated to convergence). Left `closed`. The ambiguity is
  in the lineage node, not the axis — the same "same method filed at two depths" defect
  §5 names.
- **`M.spectral-clustering`** ends in k-means. Left `closed` only under the subroutine
  rule in §1; it is the arguable one, and a reader who wants the whole procedure pinned
  should give it both.

---

## 8. Did `A.deriv.fixed` survive contact with 155 cases?

**Yes — the value is correct and load-bearing. 48 of 155 nodes need it, and no case
was found where the value is incoherent.** But four adjustments are needed, one of
them to the value's own example list.

### 8a. "the Kalman recursions" is in the example list and fails the positive test

`A.deriv.fixed`'s examples name *the Kalman recursions*, and the brief names them among
the ~60 wrong pins. **The five Kalman nodes were nevertheless left `A.deriv.closed`.**

A Kalman filter's recursion is indexed by **arriving data** and terminates when the data
ends — not "when it stops moving". Each step is a closed-form Bayesian update: compute
the gain, solve, move to the next observation. Nothing is iterated to convergence on a
fixed input. (The covariance does approach the steady-state Riccati solution for a
stationary system, but that is a property of the system, not the purpose of the filter,
and the smoother `M.rts-smoother` runs a fixed two passes.) `M.holt-winters`,
`M.exponential-smoothing`, `M.structural-time-series` and `M.var` were left `closed` for
the same reason.

**Recommendation: drop "the Kalman recursions" from `A.deriv.fixed`'s examples.** If
they are kept, the positive test has to be widened to "iterates a map", which then
admits every streaming and online procedure in the dimension and the value stops
discriminating. This is a 5-node edit either way, and it is the owner's call — but as
written, the example contradicts the test.

### 8b. `IRLS`, also in the example list, fails the negative test

`A.deriv.fixed`'s negative test excludes "descending a gradient (`A.deriv.first`)", and
its examples name **IRLS** — but IRLS *is* Fisher scoring, a Newton step with the Fisher
information as the curvature matrix. By the negative test, IRLS should be
`A.deriv.second`, not `fixed`. (No IRLS node is in these 155, so this is from the
example list rather than a pin, but the same reasoning hit `M.entropy-balancing`, whose
`A.deriv.second` pin makes its dual Newton iterations a gradient method, not a
fixed-point map; left `closed`.)

**Recommendation: either widen the negative test to "descending a gradient or a
curvature-preconditioned step", which drops IRLS from the examples, or add an explicit
carve-out saying that a reweighting whose weights are recomputed from the current
iterate counts as a fixed-point map even when it is algebraically a Newton step.** The
second is probably what was intended, but it must be written down or every
majorisation-minimisation method is a coin flip.

### 8c. The negative test reads as exclusive on a family declared multi-valued

"solving in one shot (`A.deriv.closed`)" reads as *closed and fixed are alternatives*,
yet `A.deriv` is `cardinality=many` and **42 of 155 are genuinely both**.

**Recommendation: reword to "a procedure that terminates after a single solve", and add
to the notes: a convergent loop whose inner step is a closed-form solve takes both
`A.deriv.closed` and `A.deriv.fixed`.** Without that line the 42 look like annotator
error rather than the intended reading, and the next pinning pass will re-litigate them.

### 8d. "until it stops moving" excludes budgeted and sampled iteration

Three real cases are outside the positive test as written: `M.sentencepiece-unigram`
(a fixed number of pruning rounds), `M.mini-batch-k-means` (a sample-based map that
never exactly stops), and the MCMC six (a chain that converges in distribution, not to
a point). The first two were pinned `fixed` anyway; the six were not.

**Recommendation: "iterates a map that is not a gradient step until it stops moving, or
for a fixed budget of such iterations"**, and state explicitly that a chain converging
in *distribution* is `A.deriv.sample`, not `A.deriv.fixed` — which is the ruling the six
`neither` nodes need and the only one that keeps them from drifting back.

### 8e. One thing the value does not distinguish, offered rather than recommended

`A.deriv.fixed` covers both a **contraction with a unique fixed point** (PageRank, BP on
a tree, Sinkhorn) and a **monotone ascent to a local stationary point** (EM, k-means,
ALS). Those carry very different guarantees, and the difference is currently visible
only through `A.guar.conv`, which is pinned on some of these nodes and not others. Not
worth a split on this evidence — but if the roll-up "how much of the field relies on a
guaranteed-unique answer" is ever wanted, this is where it would have to come from.

---

## 9. Incidental, not acted on

Five rows (`M.baum-welch`, `M.hmm`, `M.hsmm`, `M.forward-backward`, `M.n-gram-mle`)
carry `A.outspace.struct`, which no longer exists in `attributes/nodes.tsv` — commit
`ffc1aa43` split `A.outspace` and the value appears to have moved to the new
`A.outstruct` family. Carried through unchanged, since the brief scoped this task to
`A.deriv`, `R.fit.fixpoint` and `A.param.none`. The same migration needs applying to
`lineage/nodes.tsv` wholesale.
