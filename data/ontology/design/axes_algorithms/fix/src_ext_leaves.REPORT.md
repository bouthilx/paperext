# Re-pinning the 163 bare `S.src.ext` leaves

Input `fix/src_ext_leaves.tsv`, output `fix/src_ext_leaves.pinned.tsv` — same 163
rows, same order, same columns; only `signal` and `notes` changed. Values taken
from `signal/nodes.tsv` only.

## 1. Counts

What the bare `S.src.ext` token became, per row:

| destination | nodes |
|---|---|
| `S.src.ext.obs` | 110 |
| `S.src.ext.human` | 23 |
| `S.src.ext.obs` **and** `S.src.ext.human` (both) | 3 |
| `S.src.self.struct` | 2 |
| `S.src.none` | 2 |
| `S.src.ext.pair` | 1 |
| removed — a specific `S.src.ext.*` child was already pinned on the row | 19 |
| **kept as `S.src.ext`** | **3** |

The 19 removals are the rows where the classical region wrote parent *and* child
(`S.src.ext; S.src.ext.pref`). Those rows never had the roll-up defect — the
child was already there — so the bare interior pin was pure redundancy. The
region-local convention of pinning the parent alongside the child is also the
minority convention in `lineage/nodes.tsv` (63 rows do it, 675 pin the depth-3
child alone), which is why removing it is the consistent fix rather than a loss.

Resulting `S.src.ext.*` state over all 163 rows:

| final ext value set | nodes |
|---|---|
| `S.src.ext.obs` | 106 |
| `S.src.ext.human` | 23 |
| *no ext value at all* | 13 |
| `S.src.ext.human; S.src.ext.obs` | 7 |
| `S.src.ext.human; S.src.ext.pref` | 5 |
| `S.src.ext.pair` | 3 |
| `S.src.ext` | 3 |
| `S.src.ext.prog` | 2 |
| `S.src.ext.pref` | 1 |

## 2. The rule used for the hard cases

The brief's question — *what does the literature that names this method fit it
to* — reduces, for the classical branch, to a sharper distinction than
"regression vs classification":

> An **annotation** is a value created by someone outside the data-generating
> process for the purpose of labelling examples (`S.src.ext.human`). A
> **response variable** is a value recorded as an attribute of the unit itself,
> whether continuous or categorical (`S.src.ext.obs`).

Under that rule a categorical target is routinely `obs`: disease status, species,
credit default, recidivism, churn, the winner of a trial. That is the whole
UCI/statistical-learning tradition, and it is what trees, boosting, forests,
discriminant analysis and GLMs are named for. `human` then falls where somebody
was actually hired to label: annotated corpora (CRF, MEMM, structured
SVM/perceptron), annotated categories in vision/text (SVM, perceptron, naive
Bayes for documents and spam, GP classification), a labelled seed set in
semi-supervised graph methods, user ratings in collaborative filtering, and
assessor relevance grades in learning-to-rank.

## 3. Every node where `S.src.ext` was kept (3)

- **`M.bagging`** — bagging is a wrapper, not an estimator. Breiman's paper runs
  it over classification *and* regression with an identical resampling
  procedure, and the wrapper is indifferent to what the base learner is fitted
  to. Nothing more specific is true *of bagging*. (Its concrete descendants
  `M.random-forest`, `M.extremely-randomised-trees`, `M.rotation-forest` did get
  `obs`, because those are named estimators with a tabular home literature.)
- **`M.nuclear-norm-completion`**, **`M.soft-impute`** — matrix completion is
  fitted to whatever entries happened to be observed; ratings, physical
  measurements and counts are all the same optimisation, and the low-rank
  structure (`S.src.self.struct`, already pinned) is what the method actually
  exploits. `obs` was tempting (the signal-processing framing: observed entries
  of a measured matrix) and `human` was equally arguable (both papers' headline
  benchmark is Netflix ratings) — which is exactly the test for keeping the
  interior node.

## 4. Nodes given two values (and the near-doubles)

Deliberate doubles (3):

- **`M.k-nn`**, **`M.weighted-k-nn`** — k-NN classification on annotated
  categories and k-NN regression on a measured response are the *same*
  procedure, both canonical, both named "k-NN". (`human` was already pinned;
  `obs` was added.)
- **`M.logistic-regression`** — simultaneously the canonical GLM for a measured
  binary response (biostatistics, epidemiology) and the canonical linear
  classifier on annotated labels. Nothing in the fitting changes between the
  two. Note the tension with its siblings in `L.lin.glm` (Poisson, negative
  binomial, ordinal/multinomial logit), which I pinned `obs` alone: a survey
  respondent's Likert answer is the *unit's* recorded response, not a judgement
  an annotator made about an example.

Rows that now carry two ext values without being a deliberate double (4 + 5):

- **`M.boruta`, `M.lasso-selection`, `M.mutual-information-filtering`,
  `M.recursive-feature-elimination`** — I replaced the bare pin with `obs` (the
  feature-selection literature's home is omics, clinical and tabular data,
  scoring features against a measured response) and left the pre-existing
  `S.src.ext.human`, which is **inherited from the family row `L.prep.select`**
  (`S.src.ext; S.src.ext.human`) rather than independently judged. I think that
  family pin is the real defect on these four; see §5.
- **`M.lambdamart`, `M.lambdarank`, `M.listmle`, `M.listnet`, `M.ranknet`** — I
  added `S.src.ext.human` beside the inherited `S.src.ext.pref`. The raw target
  in learning-to-rank is an *absolute* graded relevance judgement from a human
  assessor; `S.src.ext.pref`'s own negative test ("the target is an absolute
  score or class") therefore excludes it. `pref` is recording the *form* of the
  loss (pairwise/listwise), which `S.form.rank` already carries. Left in place
  rather than deleted, but `pref` is doing the wrong job here.

## 5. Where the placement, not the pin, is the problem

- **Approximate nearest-neighbour search (`L.retr.index`) has no target at all.**
  `M.diskann`, `M.hnsw` → `S.src.none`: a proximity graph is built, nothing is
  fitted (`S.form.none` is already pinned). `M.scann` → `S.src.self.struct` and
  `M.ivf-pq` keeps `S.src.self.struct`: their fitted part is a quantisation
  codebook over the dataset geometry. `M.lsh` already carried `S.src.none` and is
  data-independent. The family pin `L.retr.index: S.src.self.struct` is *false*
  for the pure graph indexes, and the original `S.src.ext` was false for all
  five — external annotation never enters ANN search.
- **One-class methods never had an external target.** `M.svdd`, `M.deep-svdd`,
  `M.one-class-svm` are fitted to unlabelled data assumed normal;
  `S.src.self.struct` (already pinned) is the whole truth. The bare `S.src.ext`
  was a straight error, not an under-specification.
- **Off-policy evaluation (`L.bandit.ope`): `M.fqe`, `M.doubly-robust-ope`,
  `M.inverse-propensity-scoring`, `M.self-normalised-ips`.** The target is a
  logged reward, already pinned `S.src.env.reward` by the family. No annotator
  exists and no second external target exists, so I removed the bare pin rather
  than adding `obs` — adding it would double-count one quantity under two
  sources. If the ontology ever wants "logged production outcome" to roll up with
  measured outcomes, this is where the two branches touch.
- **`M.als` / `M.als-collaborative-filtering` / `M.als-matrix-factorisation` are
  three nodes for one method**, filed under `L.rec.cf`, `L.rec` and
  `L.dimred.mf`. All three got the same pin, which is the deduplication signal
  `PINNING_FINDINGS.md` §5 describes.
- **`L.prep.select` pins `S.src.ext.human` at family level** and `L.causal.rep`
  pins it too (`S.form.div; S.src.ext; S.src.design.adjust; S.src.ext.human;
  S.form.lik`). Neither is true of its members: feature selection is
  target-agnostic, and CEVAE/TARNet/Dragonnet/GANITE/CFR estimate effects on
  measured outcomes (IHDP birth weight, Jobs earnings). Those two family pins
  should be dropped.
- **19 family rows still carry the bare `S.src.ext` and are outside this file**:
  `L.synth.cf`, `L.fair`, `L.lin`, `L.kernel.svm`, `L.gp`, `L.tree`, `L.bag`,
  `L.boost`, `L.inst`, `L.nb`, `L.dimred.disc`, `L.seq.crf`, `L.causal.adjust`,
  `L.causal.iv`, `L.causal.panel`, `L.causal.disc`, `L.causal.hte`, `L.rec`,
  `L.symreg`. Fixing only the leaves leaves every one of those roll-ups still
  reading "unknown annotation type", and under union inheritance the family pin
  propagates the interior node back onto the leaves I just fixed. The six causal
  families and `L.lin`, `L.tree`, `L.boost`, `L.bag`, `L.inst` should take
  `S.src.ext.obs`; `L.kernel.svm` and `L.seq.crf` should take `S.src.ext.human`;
  `L.rec` `S.src.ext.human`; `L.symreg` `S.src.ext.obs`; `L.dimred.disc` is
  split (`obs` for PLS/LDA, `pair` for CCA) and should probably pin nothing.
- **`M.disparate-impact-remover`** → `S.src.self.struct`: it maps features to
  within-group quantiles and uses no target whatsoever. It was the only row in
  the file with `S.src.ext` as its *entire* signal column.

## 6. What made me doubt the new value's definition

1. **"recorded from the world" vs recorded from an experiment.** The five
   surrogate-search nodes (`M.gp-ei-bayesian-optimisation`, `M.smac`, `M.tpe`,
   `M.bohb`, `M.bore`) regress a measured held-out score. It is a measurement
   with no annotator, so `obs`'s positive test passes — but the quantity was
   produced by the run's own training, so the *parent* `S.src.ext` ("produced by
   an agent outside the run's own model and environment") arguably fails, and
   `PINNING_FINDINGS.md` §3a-bis says four regions independently asked for a
   separate value here. I pinned `obs` because it is the least wrong available
   value, and flag it: `S.src.ext.obs` will silently absorb "measured held-out
   score" unless the §3a-bis value is added, and then these five should move.
   The same clause is why `M.ai-feynman` and `M.sindy` are comfortable (physical
   measurements) while the HPO five are not.
2. **The negative test does not separate a respondent from an annotator, and
   categorical response variables are recorded by people.** "A judgement a
   person assigned" reads as excluding a clinical diagnosis, a survey answer, an
   assessor's grade and a star rating — but only the last two are annotations in
   any useful sense. The whole tabular-classifier block (trees, boosting,
   forests, discriminant analysis, Bayesian network classifiers) turns on this,
   and the test as written gives no grip; I had to supply the rule in §2. I
   suggest the negative test say *"a value an annotator assigned to an example
   for the purpose of supervision"*, and the positive test add *"including a
   categorical response recorded as an attribute of the unit"*. Without that,
   the single largest group in this file (≈40 ensemble/tree/GLM nodes) is
   re-arguable in either direction, and an honest reading of the current wording
   might push the classification-named ones (`M.adaboost`, `M.cart`,
   `M.random-forest`) to a double.
3. Minor: `obs` now competes with `S.src.ext.pair` for click logs and with
   `S.src.env.reward` for logged production outcomes. I kept both existing
   values in those places (CF → `human`, OPE → `env.reward`), but the three
   values are not disjoint on behavioural data.
