# Pinning report — region `data` (259 nodes)

Covers tokenizer induction, augmentation, classical preprocessing, curation and
selection, class-imbalance resampling, synthetic data, semi-supervised learning,
exploration rules, replay and relabelling, self-play and task generation, and
imitation learning.

## Conventions used

- **Interior lineage nodes carry only the intersection** of their descendants
  (rule 1). 60 `L.*` rows are interior or near-interior; a blank cell on one of
  them is inheritance, not a gap.
- **`M.*` instance rows carry their own complete set**, as the phase-1 worked
  examples do, so a leaf row is readable without walking the chain. 199 `M.*`
  rows, all pinned on role and attributes.
- Every value written exists in `role/`, `signal/` or `attributes/nodes.tsv`;
  verified mechanically. Nothing was invented in the table — the proposals below
  are proposals only.

## Counts

| axis | rows with a value | blank by divergence (rule 1) | **homeless** |
|---|---|---|---|
| `role` | 259 / 259 | 0 | 0 |
| `signal` — `S.src` | 237 / 259 | 16 | **6** |
| `signal` — `S.form` | 213 / 259 | 18 | **28** |
| `attributes` | 245 / 259 | 14 | 0 row-level; 2 **family-level** gaps (below) |

Negative pins: 10, on 8 nodes. Multi-value-in-one-family: 5 rows.
Nodes with nothing at all on any axis: **0**.

Signal-free is indeed the common case, and it checks out: 68 rows carry
`S.src.none` and 113 carry `S.form.none`. But the brief's warning was right —
several families that look signal-free are not, see **Confirmed-not-none**.

---

## 1. Homeless nodes

### 1a. `S.form` has no branch for a criterion that drives a *decision* (28 rows)

This is the largest gap in the region and it has three distinct shapes. In all
three a real number is computed and something is chosen by it, but `S.form.none`
("the procedure performs no comparison between an output and a target") is
**false**, and no other value fits because every `S.form` value is a *training*
criterion minimised by an optimiser.

**(i) Selection by a measured held-out metric** — 4 rows: `L.aug.policy`,
`M.autoaugment`, `M.fast-autoaugment`, `M.pba`. AutoAugment scores a candidate
policy by validation accuracy. There is a target (the validation labels, pinned
`S.src.ext.human`) and a comparison, so `S.form.none` is wrong; and validation
accuracy is not a likelihood, a bound, a distance or a divergence.
Needs `S.form.sel.metric`.

**(ii) Per-example acquisition or priority score** — 7 rows: `L.replay.prio`,
`M.per`, `M.ere`, `M.lap`, `M.topological-replay`, `M.grand`, `M.el2n`. PER
orders transitions by |TD error|; GraNd and EL2N order examples by gradient norm
and by error against the human label. The number is a comparison to a target but
no parameter moves because of it. Needs `S.form.sel.acq`.
*Contrast:* `M.uncertainty-sampling`, `M.bald` and `M.core-set-selection` were
pinned `S.form.none` and that is defensible — their scores involve no target at
all, only the model's own output or the data geometry. The split inside one
lineage family (`L.curate.active`) between score-with-a-target and
score-without-one is itself evidence the branch is needed.

**(iii) Per-candidate fitness, learning progress or win rate** — 17 rows: all of
`L.selfplay.*` (`M.self-play`, `M.naive-self-play`, `M.fictitious-self-play`,
`M.self-play-with-opponent-pools`, `M.psro`, `M.alphastar-league`,
`M.double-oracle`, `M.adr`, `M.alp-gmm`, `M.plr`, `M.poet`,
`M.asymmetric-self-play`) plus `M.novelty-search` and `M.map-elites`. A whole
policy, opponent or level is scored as a unit and selected by that score.
`S.form.return`'s negative test explicitly excludes it ("maximises a per-example
score with no temporal credit"), and nothing replaces it.
Needs `S.form.sel.fitness`. This one reaches outside the region: evolutionary
policy search (`CMA-ES` policies, OpenAI-ES) will hit the same wall in `rl`/`opt`.

### 1b. `S.src` has no value for a target derived from existing targets (6 rows)

`L.aug.mix`, `M.mixup`, `M.cutmix`, `M.fmix`, `M.manifold-mixup`, `M.mosaic`.
Mixing augmentations construct a target — the interpolated label — which is why
they take `R.fit.obj` as a second role. But the *source* of that label is
"whatever the labels already were": human in ImageNet, model-produced in a
distillation run, self-supervised in a contrastive run. `S.src.none` is false
(there is a target). Needs `S.src.derived`.

**This is a disagreement with the phase-1 worked examples**, which pinned CutMix
`S.src.ext.human`. That is correct for the supervised instance and wrong for
mixup inside SimCLR or inside distillation, and the whole point of mixing is
that it is agnostic to where the label came from. Pinning the supervised case
makes the axis report a property of the paper, not of the method (tension 10,
here in a form the existing values cannot absorb). I left the cell blank.

### 1c. `A.param` claims universal scope and has no value for "produces nothing"

`A.param`'s scope column reads *"to every algorithm"*, and its three values are
parameters / stored data / transductive output. Exactly **168 rows in this
region carry no `A.param` value**, and most of them produce no artifact at all:
every augmentation, every exploration rule, every replay rule, every selection
and ordering rule, every self-play loop. None of the three values is true of
them. The phase-1 worked examples
already handle this by silently leaving the cell blank (AdamW, L-BFGS, beam
search, DDIM, nucleus sampling all have no `A.param` value), which contradicts
the declared scope. I followed the worked examples and left it blank.
This is tension 12 confirmed and quantified: either mint `A.param.none`, or
rewrite the scope to "procedures that fit something".

Two narrower variants of the same gap:

- `L.tok.byte` + `M.byt5-scheme`, `M.canine-scheme`,
  `M.character-level-lm-input`: a byte tokenizer applies to unseen inputs, so
  `A.param.trans` is wrong, but nothing was fitted, so `A.param.param` is wrong
  too. By contrast `L.tok.bpe/wp/uni` *do* get `A.param.param` — the vocabulary
  is a fixed artifact runnable on new input without the corpus. That asymmetry
  inside one tokenizer family is the sharpest version of the SYNTHESIS open
  question "is a tokenizer vocabulary a model".
- `L.curate.distill` + `M.dataset-distillation`, `M.gradient-matching`,
  `M.distribution-matching`: the artifact is a **dataset**. It is reusable, but
  it is not runnable on new inputs, so `A.param.param` fails on its own positive
  test; it is not the training data, so `.inst` fails; new points do not need a
  refit, so `.trans` fails. Needs `A.param.data` (which would also claim the
  tokenizer vocabulary, NAS outputs and learned-optimiser weights).

### 1d. `A.cadence`'s scope rule and the worked examples disagree

Scope: *"to iterative fitting procedures"*; negative test: *"a one-shot
closed-form fit"*. Under that rule z-scoring, PCA/ZCA whitening, min-max
scaling, one-hot, mean/median imputation and kNN imputation take **no**
`A.cadence` value — and I left them blank, because rule 3 is explicit. But
phase 1 pinned `A.cadence.full` alongside `A.deriv.closed` on EM, TMLE, GPTQ and
BPE, i.e. used it to mean "sees the whole dataset" rather than "iterates over
it". These cannot both be right. ~30 rows in this region turn on the answer.
I pinned `A.cadence.full` only where the fit really iterates (BPE merges,
Unigram EM, MICE, matrix completion, lasso, label propagation, Snorkel/
Dawid-Skene EM).

### 1e. `role` has no slot for acquiring a *new* annotation in-run

`R.data.label` exists for "target construction for unlabelled data" but its
negative test explicitly excludes *"assigns targets by a human annotator inside
the run"* — which is precisely the defining step of active learning and of
DAgger's expert query. `R.data.select` covers *which* points are queried, and
nothing covers the query itself. Affected: `L.curate.active` and its 5 members,
`M.dagger`, `M.dart`. I pinned `R.data.select` (for the selection) and, for
DAgger/DART, `R.exp.act` (for the on-policy rollout that generates the states),
leaving the annotation step unrepresented. Needs `R.data.annot`.

### 1f. `role`'s `R.data.*` reads as example-space only; feature selection has no slot

`L.prep.select` + `M.mutual-information-filtering`,
`M.recursive-feature-elimination`, `M.lasso-selection`, `M.boruta` (5 rows)
operate on **columns**, not examples. `R.data.select` is "Example selection,
weighting and ordering"; `R.data.repr` is "converts raw input into the units or
features the model consumes", whose negative test is "changes which examples are
present" — so `R.data.repr` is the least-bad fit and I used it. But a variable-
space operation is not a representation construction, and `R.data.repr` now
mixes tokenizers, scalers and feature selectors. Low-confidence; flagged rather
than proposed, because a fifth `R.data` child may be over-cutting.

### 1g. `S.src.ext.prog` is doing duty for simulator ground truth

`L.synth.sim` + `M.domain-randomisation`, `M.procedural-scene-generation`,
`M.sim-to-real-pipelines` (4 rows). A renderer or physics engine supplies the
target. `S.src.env.*` is wrong — its test is "feedback returned **after** the
system acted", and procedural scene generation emits labelled images with no
action. `S.src.ext.prog` ("a rule, heuristic, lexicon or metadata field supplied
the target") is a stretch I took rather than leave blank, because a simulator is
a program. Proposing `S.src.ext.sim` instead; see §2.

---

## 2. Proposed new axis values

| id | name | parent | positive_test | nodes that need it |
|---|---|---|---|---|
| `S.form.sel` | Decision criteria (sub-root) | `S.form` | a number is computed and something is chosen by it, with no parameter update driven by that number | 28 rows, §1a |
| `S.form.sel.metric` | Measured held-out performance | `S.form.sel` | candidates are ranked by a performance number measured on held-out data, not by a differentiable criterion | `L.aug.policy`, AutoAugment, Fast AutoAugment, PBA (+ all of `R.search.hp`, outside this region) |
| `S.form.sel.acq` | Per-example acquisition or priority score | `S.form.sel` | a scalar score is computed per example and used to select, order or weight it | `L.replay.prio`, PER, ERE, LAP, topological replay, GraNd, EL2N |
| `S.form.sel.fitness` | Per-candidate fitness | `S.form.sel` | each candidate is evaluated whole and scored, and the score is maximised by selection rather than by descent | all `L.selfplay.*` (12 rows), novelty search, MAP-Elites (+ ES/CMA-ES policy search) |
| `S.src.derived` | Target derived from existing targets | `S.src` | the target is a deterministic function of targets the examples already carried, whatever their original source | `L.aug.mix` + mixup, CutMix, FMix, Manifold Mixup, Mosaic; partly `L.semi.mix`, SMOTE |
| `S.src.ext.sim` | Simulator-supplied ground truth | `S.src.ext` | the target is read off the generative process that produced the example — a renderer, physics engine or procedural generator | `L.synth.sim` + 3 members |
| `A.param.none` | Produces no artifact | `A.param` | the procedure emits no fitted object; it transforms, selects or decides | 168 rows here; already needed by AdamW, beam search, DDIM in phase 1 |
| `A.param.data` | Produces a dataset or vocabulary | `A.param` | the surviving artifact is data, not a runnable map from inputs to outputs | `L.curate.distill` + 3; candidate home for `L.tok.*` |
| `R.data.annot` | Annotation acquisition | `R.data` | obtains new targets from a human or oracle during the run | `L.curate.active` + 5, DAgger, DART |

`A.param.none` and the `A.cadence` ruling (§1d) are the two that should be
settled **before** annotation: both change what a blank cell means on a
universal family, and both affect the whole dimension, not just this region.

---

## 3. Multi-value families (rule 5)

Five rows needed two values from one single-valued family.

| node | family | values | why |
|---|---|---|---|
| `L.tok.uni`, `M.unigram-lm`, `M.sentencepiece-unigram` | `A.deriv` | `.comb` + `.closed` | Unigram LM runs EM to fit token probabilities (closed-form M-step) **and** a discrete prune-and-score search over the candidate superset. Dropping either loses half the algorithm — the same situation that made `A.deriv` multi-valued for HMC and XGBoost, so this is confirmation, not a new problem. |
| `M.autoattack` | `A.deriv` | `.first` + `.zero` | AutoAttack is an ensemble of attacks, APGD (gradient) and Square Attack (black-box). A genuine bundle. |
| `M.icarl` | **`A.param`** | `.param` + `.inst` | iCaRL ships trained parameters **and** requires its stored exemplar set at prediction time (nearest-class-mean classification over exemplars). This is a new multi-value pressure on a family phase 1 declared single-valued, and it is not an edge case — every exemplar-based continual learner and every retrieval-augmented fine-tune has the same shape. |

`A.deriv` being multi-valued is already decided. **`A.param` is not**, and
`M.icarl` breaks it.

---

## 4. Negative pins used (10 on 8 nodes)

| node | pin | denying |
|---|---|---|
| `M.augmix` | `!S.form.none` | `L.aug.mix` pins `S.form.none`; AugMix adds a real JS-divergence consistency loss across augmented copies, so it has a criterion (pinned `S.form.inv`) and does not mix labels. |
| `M.r-drop` | `!S.src.self.view`, `!R.data.aug` | `L.reg.consist` pins two augmented views and a data-augmentation role; R-Drop's two "views" are two dropout masks, so no input transform is made and no augmentation role is filled. Source is `S.src.self.own`. |
| `M.dagger`, `M.dart` | `!A.regime.offline` | `L.il.bc` pins `A.regime.offline`; DAgger and DART interact with the environment to collect the states they then have labelled, which is `A.regime.off`. |
| `M.randaugment`, `M.trivialaugment` | `!R.search.policy` | `L.aug.policy` is "searched augmentation policies" and pins `R.search.policy`; RandAugment's and TrivialAugment's entire contribution is *removing* the search. |
| `M.bootstrapped-dqn` | `!S.form.post`, `!A.uncert.post` | `L.explore.post` pins posterior targeting and `A.uncert.post`; bootstrapped DQN deliberately approximates the posterior with an ensemble of heads, so `A.uncert.ens`. |
| `M.diffusion-policy-training` | `!S.form.lik` | `L.il.bc` pins `S.form.lik`; a diffusion policy is trained by denoising score matching, `S.form.score`. |

The RandAugment pair deserves emphasis: **two of `L.aug.policy`'s five members
deny the family's division principle.** That is a lineage defect, not a pinning
one (§6).

---

## 5. Nodes that are descriptions rather than named procedures

64 rows in this region carry the `notes` review flag. The flag is a
capitalisation heuristic, so it is right about a minority. My verdicts:

**Flag is a false positive — genuinely named, conventionally lowercase (keep):**
behaviour cloning, curriculum learning, self-paced learning, experience replay,
label propagation, label spreading, harmonic functions, dataset distillation,
gradient matching, distribution matching (the last two are the named `DC`/`DM`
methods in the distillation literature), domain randomisation, fictitious play,
fictitious self-play, double oracle, regret matching, novelty search,
hindsight relabelling, k-center greedy, facility location coresets, greedy
maximum coverage, free adversarial training, generative replay, guided cost
learning, democratic co-learning, tri-training, mean/median imputation,
min-max scaling, quantile normalisation, lasso selection, recursive feature
elimination, mutual-information filtering, matrix-completion imputation,
optimistic initialisation, parameter-space noise, perplexity filtering,
exact-substring dedup, back-translation, synonym substitution, token dropout,
temporal ensembling, uncertainty sampling, core-set selection, counterfactual
data augmentation, procedural scene generation. All pinned normally.

**Flag is correct — these are descriptions, settings or duplicates. I pinned
them (inheriting the family) but they should be removed or merged:**

| node | verdict |
|---|---|
| `M.self-play` | duplicate of the family node `L.selfplay` itself |
| `M.uniform-replay` | duplicate of `L.replay.unif` / `M.experience-replay`; three strings for one thing |
| `M.naive-self-play`, `M.self-play-with-opponent-pools` | descriptions of `L.selfplay.naive`, not distinct procedures |
| `M.sim-to-real-pipelines` | a problem setting; restates `L.synth.sim` |
| `M.synthetic-textbooks` | a dataset description (phi-1), not a procedure |
| `M.hand-tuned-domain-weights` | the explicit *absence* of a procedure; it exists only as the baseline DoReMi beats |
| `M.replay-ratio-schedules` | a hyperparameter practice; also arguably `R.fit.sched`, not `R.exp.store` — I pinned both |
| `M.anti-curriculum` | a direction, not a procedure: curriculum learning with the order reversed |
| `M.sequence-length-warmup` | a setting; and it changes a hyperparameter over training, so `R.fit.sched` fits better than the `R.data.select` it inherits |
| `M.round-trip-translation` | synonym of `M.back-translation` under the same parent |
| `M.counterfactual-data-augmentation` vs `M.cad` | the same thing twice (CAD *is* counterfactually-augmented data); I pinned them differently (`ext.prog` vs `ext.human`) only because the strings suggest different provenance, which proves they are one node |
| `M.target-encoding` vs `M.target-mean-encoding` | one procedure, two nodes, **two different parents** (`L.prep` and `L.prep.disc`) |
| `M.equal-width-equal-frequency-binning` | two distinct procedures crammed into one node |
| `M.mean-median-imputation` | two distinct procedures in one node |
| `M.majority-vote-aggregation` | a description, though a conventional one; harmless to keep |
| `M.quality-classifier-filtering`, `M.decontamination` | recipes rather than named methods, but reported as discrete pipeline stages; keep |
| `M.horizontal-flip`, `M.rotation`, `M.color-jitter`, `M.random-resized-crop` | legal under the naming rule, but `L.aug.geom`'s own note is right: these are reported as settings, never cited. Expect systematic under-reporting at the region's highest-frequency nodes (tension 3). |

No node was left unpinnable because of this. Every description still has a role.

---

## 6. Things that made me doubt an axis or the lineage

**(a) `R.exp.act` and `R.fit.obj` are not substitutable, and intrinsic motivation
occupies both by construction.** All of `L.explore.intr` (RND, ICM, NGU,
pseudo-counts, Disagreement, empowerment) and the skill-discovery half of
`L.explore.div` (DIAYN, DADS) add a learned bonus **into the return the agent
maximises** — the lineage table's own note says so. So the bonus is an
exploration rule and an objective term at once, and a role roll-up double-counts
them. By contrast `L.explore.rand` and `L.explore.opt` are pure action rules with
`S.src.none` / `S.form.none`. The brief asked whether exploration sits awkwardly
between `R.exp` and the objective: **it does, and the split is clean and
measurable** — intrinsic reward crosses, undirected and optimistic exploration do
not. That is a reason to keep both slots, not to merge them.

**(b) `R.exp.store` holds two unrelated literatures.** `L.cont.replay`
(continual-learning rehearsal: GEM, A-GEM, DER, iCaRL, generative replay) is a
lineage descendant of `L.replay` (RL replay buffers), so it inherits
`R.exp.store` — whose parent `R.exp` is defined as "determines what interaction
data the learner sees, **by acting**" and is documented as "empty for any run
with a static dataset". Rehearsal in supervised continual learning does not act.
Consequences I had to work around:
- `L.replay` cannot pin `A.regime` even though every RL descendant has it,
  because `A.regime` is out of scope for its supervised descendants.
- `M.gem` / `M.a-gem` resolve to `R.exp.store` + `R.fit.grad` and never touch
  `R.exp`'s defining act of acting.
Either `R.exp.store` needs its "by acting" inheritance relaxed, or rehearsal
needs a home under `R.data.select` and the `L.cont.replay → L.replay` edge needs
to be an `instantiates` edge rather than a `divides` one.

**(c) `L.aug.policy` is mis-cut.** Its division principle is "selects which
augmentations to apply by searching over policies", and RandAugment and
TrivialAugment — two of its five members — are explicitly the no-search
alternatives. They are siblings of AutoAugment in the literature's framing and
antonyms of it in the tree's. Two negative pins papered over it. Suggest
splitting `L.aug.policy` into searched vs. sampled policies, or demoting
RandAugment/TrivialAugment to `L.aug` directly.

**(d) `M.ucb1` sits under `L.bandit.stoch`, `M.ucb-v` under `L.explore.opt`.**
These are the same kind of algorithm with the same pins; I pinned `M.ucb-v` as a
bandit algorithm, contradicting its parent's `S.src.none` / `S.form.none`. Same
story for `M.linucb` (under `L.bandit.stoch`) and `M.rlsvi` (under
`L.explore.opt`), and `M.lints` is a duplicate of `M.thompson-sampling`. The
exploration-rule / bandit-algorithm boundary is real — an exploration rule fits
nothing, a bandit algorithm estimates arm values — but the nodes are allocated
across it inconsistently.

**(e) `M.specaugment` hangs directly off `L.aug`** rather than any child, though
it is erasing applied in the time-frequency domain and belongs under
`L.aug.erase`. Pinned as a generic augmentation.

**(f) Judgement calls I would want reviewed, not gaps:**
- `S.form.moment` for UCB1/UCB-V (a sample mean *is* a method-of-moments
  estimate, but pinning an estimating-equation value on a bandit reads oddly);
  `S.form.lik` for KL-UCB and LinUCB.
- `S.form.dist` for `L.semi.graph` — label propagation minimises a graph
  harmonic energy, which is a smoothness penalty, not a distortion to assigned
  representatives. Closest available, not right.
- `S.src.self.struct` + `S.form.none` as the standard pattern for *fitted but
  criterion-free* transforms (z-scoring, whitening, binning, BPE merges). This
  follows phase 1's BPE treatment and covers 40+ rows in this region, so it is
  worth stating as a rule rather than rediscovering per node.
- `S.form.game` for `L.marl.game` (CFR, fictitious play): the criterion is
  regret minimisation converging to an equilibrium, which `S.form.game`'s
  minimax test covers only loosely.

**(g) Confirmed-not-none.** The brief asked me to confirm rather than assume
`S.src.none` / `S.form.none`. Four families that look signal-agnostic are not,
and the distinctions are discriminating:
- `L.tok.wp` and `L.tok.uni` carry `S.form.lik` — WordPiece merges by likelihood
  gain and Unigram prunes by likelihood loss. **Only `L.tok.bpe` is
  `S.form.none`** (pure frequency counting), so phase 1's "BPE has a source and
  no form" does not generalise to the family, and `L.tok` can pin neither.
- `L.aug.adv` (FGSM, PGD, C&W, AutoAttack) carries `S.src.ext.human` /
  `S.form.game` — the inner maximisation is against the true label, and phase 1
  lists "adversarial training inner max" under `S.form.game`. So the
  augmentation axis cannot pin `S.form.none` at the family root either.
- `L.prep.rank` splits: quantile normalisation and rank-gauss are
  `S.form.none`, Box-Cox and Yeo-Johnson fit λ by maximum likelihood.
  `L.prep.disc` splits the same way: binning and one-hot are none, MDLP uses an
  MDL criterion against the class label (`S.src.ext.human` / `S.form.spars`).
- `L.curate.mix`: DoReMi and DoGE optimise domain weights with Group DRO, so
  `S.form.inv` (worst-group risk); only the hand-tuned baseline is none.

So of the four "obviously signal-free" families in this region, **three cannot
pin `S.form.none` at their root**. Signal-free is common (68 and 113 rows) but it
is a per-node fact, which is further evidence for the phase-1 ruling that signal
does not union up the chain.
