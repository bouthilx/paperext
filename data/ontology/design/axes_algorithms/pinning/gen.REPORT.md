# Pinning report — region `gen` (181 nodes)

Generative modelling (score/diffusion, GAN, VAE-adjacent, flows, autoregressive,
energy-based), all six self-supervised families, shallow embedding induction, and
multi-task/auxiliary objectives. 32 family (`L.*`) nodes, 149 named-method
(`M.*`) nodes.

## Counts

| axis | values pinned | nodes with ≥1 value | nodes blank |
|---|---|---|---|
| `signal` | 455 (incl. 34 negative) | 171 | 10 |
| `role` | 264 (incl. 4 negative) | 177 | 4 |
| `attributes` | 1024 (incl. 20 negative) | 179 | 2 |

Negative pins: **58, on 25 nodes**. Homeless cases: **11 distinct gaps affecting
36 nodes**. Proposed new values: **5** (3 on `S.form`/`S.src`, 1 on `A.param`,
1 structural). Forced multi-value in a *declared single-valued* family: **7 nodes**.

### Pinning policy I used (needed, because rules 1 and 2 collide here)

Rule 1 says blank a family cell where descendants differ; rule 2 gives negative
pins as the escape hatch. In this region those two rules point in opposite
directions constantly, because almost every family has exactly one deviant
descendant arriving through a *second* lineage parent. I split it:

- **Genuine split** (the family's characteristic column is what divides, and
  several descendants take different values) → **blank**. Used at `L.ssl.contrast`
  (source), `L.ssl.mask.vis` (form), `L.flow.cont`, `L.score.sample`,
  `L.score.guide`, `L.ssl.jepa`, `L.gan.stab`, `L.mtl`, `L.tta.ssl`, `L.emb` (form).
- **One deviant descendant breaking an otherwise real invariant** → **pin the
  invariant on the family, negative-pin the deviant**. Otherwise one misfiled leaf
  erases the only true statement about a 15-node family.

Methods are pinned with their **own complete values** (rule 2 read literally),
even where they repeat the family, so the file is auditable row by row.
`M.moco-v2` and `M.moco-v3` are the only fully blank rows — see
"axis-invisible nodes" below.

---

## 1. The `signal` split: does source × form deliver SimCLR vs BYOL?

**Partly. The motivating example in `SYNTHESIS.md` is not true as pinned.**

`SYNTHESIS.md` §"Signal splits into source × form" says *"SimCLR and BYOL agree
on source (two augmented views) and differ only on form"*. Pinned:

| node | `S.src` | `S.form` |
|---|---|---|
| `M.simclr` | `self.view` | `contrast` |
| `M.byol` | `self.view`, **`self.own`** | `agree` |
| `M.moco` | `self.view`, **`self.own`** | `contrast` |
| `M.simsiam` | `self.view`, `self.own` | `agree` |

BYOL needs a second source value, `S.src.self.own`, because the target is
produced by the EMA copy of the network — so the pair differs on **two** facets,
not one, and the claim that the split isolates the difference fails.

The split *is* vindicated one node over: **MoCo and BYOL** share both source
values exactly (`self.view` + `self.own`) and differ only on form
(`contrast`/`agree`). That is the clean pair the design wanted. The right example
to put in the design doc is MoCo vs BYOL, not SimCLR vs BYOL.

**Why it fails, and what to fix.** `S.src.self`'s characteristic is *"which part
of the input plays the role of target"*. `mask`, `next`, `view`, `corrupt`,
`ident` all answer that. **`S.src.self.own` and `S.src.self.struct` do not** —
`own` answers *who computed the target* (the model itself, in parallel to
`S.src.ext.model`), and `struct` answers *at what granularity the criterion is
defined*. Three questions are stacked in one sibling set. The consequence is
measurable: `S.src.self.own` is the second most used source value in the region
(31 nodes) and it co-occurs with a real `S.src.self.*` part-of-input value on 23
of them, so it is systematically doing double duty rather than discriminating.

Recommendation: either split `S.src.self` into two sub-facets (part-of-input
vs. target-producer), or move `S.src.self.own` up to be a sibling of
`S.src.ext.model` under `S.src`. Nodes that force this: every
`L.ssl.selfdist` and `L.ssl.cluster` descendant, `M.hubert`, `M.ance`,
`M.progressive-distillation`, `M.consistency-models`, `M.scheduled-sampling`.

**A second, smaller form problem: `S.form.agree` and `S.form.inv` are not
distinct.** `M.mean-teacher` is listed in `S.form.agree`'s examples *and* its
mechanism ("consistency regularisation") is listed in `S.form.inv`'s examples. I
pinned both on it. The same ambiguity hits `M.dino`, where
`S.form.agree` (EMA + stop-grad) and `S.form.div` (cross-entropy to the teacher's
distribution) are both literally true; I pinned both. Either `agree` is a
*source* fact wearing a form's clothes (target comes from a target network) or
`inv`/`div` need their negative tests sharpened against it.

---

## 2. DDPM → DDIM: the negative pin carries the entire node

As predicted, and worse than predicted. `L.score` legitimately pins 9 values
(2 signal, 1 role, 6 attribute). `M.ddim` keeps **one** of them
(`A.outspace.cont`) and must deny **eight**:

```
M.ddim  signal: !S.src.self.corrupt;!S.form.score;S.src.none;S.form.none
        role:   !R.fit.obj;R.out.decode
        attrs:  !A.deriv.first;!A.cadence.mini;!A.param.param;!A.uncert.point;
                !A.determinism.stoch;A.determinism.det;A.outspace.cont
```

`M.dpm-solver` and `M.unipc` need the byte-identical set; `M.cfg-rescaling`
needs 7 of the 8. So **four nodes × ~8 negative pins = 31 of the region's 58
negative pins come from this one edge**, and at that point the lineage edge
transmits no information at all — the node is defined entirely by what it
denies.

Two findings follow.

**(a) The falsification is broader than signal.** `SYNTHESIS.md` records DDPM→DDIM
as falsifying *signal* union-inheritance. It equally falsifies union inheritance
on **role** and on **four universal attribute families** (`A.deriv`, `A.cadence`,
`A.param`, `A.uncert`), because those are all "facts about fitting" and DDIM
fits nothing. The rule that actually holds in this region is: **a descendant that
changes role inherits nothing on any axis.** That is testable and it is cheaper
to state than per-axis rules. Candidate edges it would cover here: `L.score →
L.score.sample`, `L.score → L.score.guide`, `L.gan → L.gan.stab` (ADA, instance
noise, TTUR), `L.ar → L.ar.exposure` (SeqGAN).

**(b) `L.score.sample` is not homogeneous, so the fix cannot sit on the family.**
Its six descendants split: `DDIM`, `DPM-Solver`, `UniPC` are pure solvers with no
training target; `progressive distillation`, `consistency models`, `LCM`
**do** train (and keep `R.fit.obj` + a corrupted-input source). So the family
cannot carry the negatives, and the negatives must be repeated per solver.
**Proposed structural fix:** split `L.score.sample` into
`L.score.sample.solver` (training-free, `S.src.none`/`S.form.none`/`R.out.decode`)
and `L.score.sample.distil` (a training objective that targets a teacher sampler).
That collapses 24 negative pins to 9.

**Bonus result that argues the form facet is real:** `consistency models` and
`LCM` land on **`S.form.agree`** — BYOL's value — because consistency training
regresses onto an EMA target with a stop-gradient. A diffusion-distillation method
and a self-supervised vision method sharing a form value across completely
unrelated lineages is exactly the cross-cutting the axis was supposed to buy, and
it would be invisible under a flat signal list.

---

## 3. Does a VAE need two values from one attribute family? Yes — `A.uncert`

`L.vae` itself sits in another region, but the question lands in mine through
`M.iaf` (inverse autoregressive flow was published *as* a VAE posterior), and
through `M.latent-diffusion` / `M.stable-diffusion-training`, which cannot be
pinned without their VAE stage.

`A.uncert.post`'s positive test is *"returns or samples an explicit **posterior
over parameters or functions**"*. A VAE's `q(z|x)` is a posterior over **latent
variables, per example**; its weights are a plain point estimate. So:

- read strictly, a VAE is `A.uncert.point` and `DRAFT_PHASE1_A`'s worked example
  (which pins `A.uncert.post` for VAE) is **wrong against its own positive test**;
- read as "what the procedure returns about uncertainty of anything it estimates",
  a VAE returns **both** — and `A.uncert` is declared **single-valued**.

I pinned `M.iaf` with **`A.uncert.point;A.uncert.post`** and flag it. This is the
cardinality case the instructions asked about, and the honest fix is not to raise
the cardinality: it is that `A.uncert` conflates *uncertainty about parameters*
with *a per-example latent posterior*, and the second is a property of the model
family, not of the algorithm. Either add `A.uncert.latent`, or restrict
`A.uncert`'s scope to parameter/prediction uncertainty and let `S.form.bound`
carry the amortised-posterior fact (which it already does for all five
`S.form.bound` nodes in this region).

**A second single-valued family that genuinely needs two: `A.outspace`.** Every
autoregressive density model needs `A.outspace.disc` **and**
`A.outspace.struct` — the output is a *sequence* (struct: "scored jointly") *of
discrete tokens* (disc: "requires a finite enumerable set"). Pinned on 6 nodes:
`M.n-gram-mle`, `M.neural-lm`, `M.causal-lm-pretraining`, `M.pixelrnn`,
`M.pixelcnn`, `M.wavenet-training`. `A.outspace` is really two questions —
*element type* and *joint structure* — and should be split rather than made
multi-valued.

---

## 4. Homeless nodes (axis had no value that fits)

Grouped by gap. Rule 4 applied: cell left blank, node recorded.

| # | gap | axis | nodes (count) |
|---|---|---|---|
| H1 | the target is the **identity or parameter of a transformation the method itself applied** — a rotation angle, a permutation index, a patch offset, a frame ordering | `S.src` | `M.jigsaw`, `M.rotation-prediction`, `M.relative-patch-position`, `M.shuffle-and-learn`, `M.ttt`, and the family `L.ssl.pretext` (6) |
| H2 | **the observed sample as a density target** — the criterion is the (possibly unnormalised) probability the model assigns to the example itself, with nothing hidden, added or compared | `S.src` | `L.flow`+`M.nice`,`M.realnvp`,`M.glow`,`M.maf`,`M.neural-ode`,`M.ffjord`; `L.ebm`+`M.rbm`,`M.boltzmann-machine`,`M.contrastive-divergence`,`M.deep-belief-net`,`M.langevin-ebm` (13) |
| H3 | **plain numeric regression to a given target** (symmetric MSE/L1, no negatives, no target network, not a reconstruction of the input, not a normalised likelihood) | `S.form` | `M.vicreg`/`M.vicregl` invariance term, `M.w-mse`, `M.lsgan`, `M.gradnorm`, `M.progressive-distillation` (6) |
| H4 | **a weighted combination of other procedures' criteria** — the node's criterion is a combinator, so `S.form.none` is false and blank reads as unannotated | `S.src`+`S.form` | `L.mtl`, `M.uniform-weighting` (2) |
| H5 | **no artifact survives the run** — a sampler produces samples, not parameters, not stored training data, and not a transductive output needing refit | `A.param` | `M.ddim`, `M.dpm-solver`, `M.unipc`, `M.cfg-rescaling` (4) — I wrote `!A.param.param` rather than invent a value |
| H6 | **training-time self-rollout**: the procedure changes what the model conditions on during training by generating it. `R.exp.*` is scoped to *interaction* data, `R.data.aug` transforms an existing example, `R.fit.obj` is the scalar | `role` | `M.scheduled-sampling`, `M.professor-forcing`, `M.seqgan-style-corrections`, `L.ar.exposure` (4) — pinned `R.data.aug` under protest |
| H7 | **a memory bank / key queue of stale encodings** used to supply negatives. `R.exp.store` is scoped to interaction data; `R.data.select` is about which examples are used | `role` | `M.instdisc`, `M.moco` (2) |
| H8 | **weight reparameterisation or projection applied every step** (spectral normalisation, WGAN weight clipping). Not the objective, not the gradient (`R.fit.grad` is between backward and update), not the update rule | `role` | `M.sn-gan`, `M.wgan` (2) — pinned `R.fit.obj` as the GAN variant they are, and the mechanism itself is unplaced |
| H9 | **sequence-level RL with no environment**: policy-gradient training on the model's own text samples. `A.regime`/`A.world`/`A.rltarget` are scoped to "interaction data"; a decoder sampling its own continuations is on-policy in every respect but the scope predicate | `attributes` (scope) | `M.seqgan-style-corrections`, `M.professor-forcing` (2) |
| H10 | **two learners with opposed objectives that are not agents in an environment.** `A.agents.comp` ("rewards are opposed, approximately zero-sum") describes a GAN exactly, but `A.agents`'s scope is "interactive settings", i.e. control | `attributes` (scope) | all 31 `S.form.game` nodes; left blank |
| H11 | **ELECTRA's jointly-trained auxiliary generator.** `S.src.ext.model` says "another *trained* model"; `S.src.self.own` says "the learner's *own* output". A small generator trained inside the same run alongside the discriminator is neither | `S.src` | `M.electra` (1) — pinned `S.src.ext.model` as the lesser error |

H2 deserves emphasis. I pinned `S.src.self.struct` nowhere in the flow/EBM
families, because its positive test — *"the objective is defined on the geometry
or statistics of the whole dataset, not per example"* — is **false** for a
normalizing flow: its NLL is per-example. That value is `DRAFT_PHASE1_A`'s
"classical-unsupervised home" (k-means, PCA, t-SNE) and it does not stretch to
exact density estimation. I did use it for GANs (25 nodes), where the two-sample
game genuinely is a statement about the dataset's distribution rather than about
one example — but that leaves likelihood-based generative modelling with no
source value at all, which is a 13-node hole in the middle of the region this
axis was partly built for.

---

## 5. Proposed new axis values (proposals only; not added to the tables)

| id | name | parent | positive_test | needed by |
|---|---|---|---|---|
| `S.src.self.transform` | The transformation the procedure applied | `S.src.self` | the target is the identity or parameter of a transformation the procedure itself applied to the input, not the content it removed or the noise it added | H1 (6 nodes); outside the region, likely CutMix/mixup label mixing and `L.aug.*` |
| `S.src.self.dens` | The observed sample as a density target | `S.src.self` | the criterion is the probability, log-probability or unnormalised score the model assigns to the observed example itself, with nothing hidden, corrupted or compared | H2 (13 nodes); outside the region, GMM/KDE/topic-model likelihoods |
| `S.form.reg` | Numeric regression error | `S.form` | penalises a distance between a predicted value and a supplied numeric target, where the target is neither the input being reconstructed, nor a target network's output, nor a normalised probability | H3 (6 nodes); outside the region, reward-model regression, value regression |
| `A.param.none` | Produces no artifact | `A.param` | the procedure emits outputs for the inputs it was given and leaves behind no parameters, no stored data and nothing to refit | H5 (4 nodes); outside the region, beam search, top-p, all of `L.dec` |
| *(structural)* `L.score.sample.solver` / `L.score.sample.distil` | — | `L.score.sample` | solver: reduces sampling steps with no training target. distil: fits a student to a teacher sampler's trajectory | removes 15 of 58 negative pins |

Deliberately **not** proposed: a GAN value on `A.agents` (H10) and an
`A.uncert.latent` (§3). Both are real gaps but both are better fixed by changing
a scope predicate than by minting a value — see §7.

---

## 6. Negative pins used (58 on 25 nodes)

| node | denies | why |
|---|---|---|
| `M.ddim`, `M.dpm-solver`, `M.unipc` | 8 each: `!S.src.self.corrupt`, `!S.form.score`, `!R.fit.obj`, `!A.deriv.first`, `!A.cadence.mini`, `!A.param.param`, `!A.uncert.point`, `!A.determinism.stoch` | the named hard case: a training objective's descendant is a decoder that fits nothing. Note `!A.determinism.stoch` — **a single-valued family also needs negative pins**, because without one DDIM unions to both `det` and `stoch` |
| `M.cfg-rescaling` | 7 (same minus determinism) | a pure sampling-time rescaling under a lineage whose root is a training objective |
| `M.cpc` | `!S.form.agree` | CPC is multi-parented into `L.ssl.jepa` (→ `L.ssl.selfdist`, which pins `S.form.agree`) but uses InfoNCE with explicit negatives. The clearest case where union inheritance would silently relabel a method — the MLP-Mixer failure mode, reproduced |
| `M.wav2vec` | `!S.src.self.mask` | **misfiled**: wav2vec v1 is contrastive future prediction and masks nothing, yet it sits under `L.ssl.mask.aud`, whose positive test requires masking |
| `M.ttt`, `M.memo`, `M.ttt-layers` | `!S.src.self.mask` | `L.tta.ssl` is parented to `L.ssl.mask`, but only TTT-MAE masks: TTT predicts rotations, MEMO marginalises augmentations, TTT-layers reconstructs |
| `M.contrastive-representation-distillation` | `!S.src.ext.human` | **misfiled**: it sits under `L.ssl.contrast.sup` ("uses ground-truth labels") but its target is a teacher network's representation |
| `M.ttur`, `M.ada`, `M.instance-noise` | `!S.src.self.struct`, `!S.form.game` | `L.gan.stab` members are schedules and augmentations that modify a GAN run; they have no target and no criterion of their own |
| `M.ppl-regularisation` | `!S.src.self.struct`, `!S.form.game` | a path-length penalty on the generator; its criterion is output smoothness (`S.form.inv`), not the minimax |
| `M.seqgan-style-corrections` | `!S.form.lik` | descends from `L.ar` (maximum likelihood) but replaces it with a policy-gradient/adversarial criterion |
| `M.rectified-flow`, `M.flow-matching`, `M.stochastic-interpolants` | `!S.form.lik` | descend from `L.flow` (exact likelihood) but regress a velocity field; same role, different criterion |
| `M.iaf` | `!S.form.lik` | published as a variational posterior trained by ELBO, not by exact NLL, although it is a normalizing flow |
| `M.consistency-models`, `M.lcm` | `!S.form.score` | the criterion is self-consistency of the ODE map against an EMA target, not noise regression |
| `M.score-matching` | `!S.src.self.corrupt` | Hyvärinen score matching perturbs nothing; only the *denoising* variant does. `L.score`'s own name hides this |
| `M.classifier-guidance` | `!S.src.self.corrupt`, `!S.form.score` | the guidance classifier is fitted to human labels on noised images; the diffusion criterion is not part of the method |
| `M.gradnorm` | `!S.src.none`, `!S.form.none` | the only member of `L.gradproc.conflict` that actually fits something (a target gradient-norm balance) |
| `L.flow.cont` | `!A.determinism.det` | a **family-level** negative pin, overriding a single-valued parent value |

Pattern: **16 of the 25 nodes carrying a negative pin do so because of a second
lineage parent or an outright misfiling, not because the method is unusual.**
The negative pin is currently absorbing taxonomy errors as well as genuine
exceptions, and nothing in the schema distinguishes those two uses. Worth a
`reason` marker, or the `derives-from`/`instantiates` edge split from
`SYNTHESIS.md` §4 would prevent most of them — `M.cpc`, `M.spr`,
`M.mean-teacher`, `L.tta.ssl`, `L.retr.dense`, `L.gradproc.conflict`,
`L.score.guide` all arrive at their conflict through an `instantiates`-style edge
while their *descent* parent is unproblematic.

---

## 7. Anything that made me doubt an axis

**7.1 Rule 1, applied strictly, deletes families' defining content.** Nine
families here have exactly one deviant descendant arriving through a second
parent. Under strict rule 1, `L.ssl.mask` would pin **nothing** on signal — the
family whose whole characteristic column reads "what is masked" — because
`L.tta.ssl` is parented into it and MEMO does not mask. Same for
`L.ssl.mask.aud` (wav2vec v1), `L.ar` (SeqGAN), `L.gan` (TTUR), `L.ssl.contrast.sup`
(CRD). I chose rule 2 + a negative pin in all five and recorded it. If rule 1 is
to stay strict, it must be scoped to `divides`/`derives-from` descendants only;
otherwise one cross-filing silently blanks a family and the blank is
indistinguishable from "not yet annotated" (`DRAFT_PHASE1_A` tension 12).

**7.2 Four attribute families are degenerate in this region and three are empty.**
`A.param`: 173 pins, **all** `A.param.param`. `A.uncert`: 170 pins, 169 of them
`A.uncert.point`. `A.cadence`: 167 pins, **all** `A.cadence.mini`. `A.deriv`: 177
pins, 167 `A.deriv.first`. Meanwhile `A.guar`, `A.privacy`, `A.topology`,
`A.datalocality`, `A.exec` and `A.exact` are used **zero** times across 181
nodes. These columns cost one annotation decision each per node and return no
discrimination inside the region. That is not an argument to drop them —
`A.deriv` and `A.uncert` clearly discriminate in the classical and RL regions —
but it does say the *universal* families are not universal in cost-benefit, and
a default-value mechanism ("deep minibatch training unless stated") would remove
~650 of this region's 1024 attribute pins without losing a single distinction.
`A.guar` being empty is itself a finding: generative and self-supervised
modelling is an entirely empirically-justified region, and `A.guar`'s absence
there is informative rather than missing.

**7.3 `A.determinism`'s positive test is unusable as written.** "Any internal
sampling" makes every deep run stochastic — minibatch shuffling, dropout, random
crop. I had to invent a reading — *sampling that is constitutive of the
procedure's definition* — to get `A.determinism.det` for CLIP (random crop,
incidental) and `A.determinism.stoch` for SimCLR (augmentation, the paper's main
ablation). That line is mine, not the table's, and 167 pins depend on it. The
family needs its test rewritten or it will not be reproducible between
annotators.

**7.4 Masking is role-inconsistent against augmentation.** `DRAFT_PHASE1_A` gives
SimCLR `R.data.aug` ("the augmentation pipeline is constitutive") but gives MAE
`R.fit.obj` alone, although masking is equally constitutive and equally a
transformation of the example. I followed the draft (28 `R.data.aug` pins on
view-based and pretext methods, none on the 11 masked-modelling methods) to stay
comparable, but it is arbitrary: the same mechanism — manufacture the
input-target pair by transforming the input — is on the data axis in one family
and on the fit axis in another. Either all self-supervised target construction
carries `R.data.aug` (+`R.data.label`), or none does.

**7.5 `L.mtl` has no signal by construction**, and that is a *kind* problem, not
a value problem (H4). A combinator over other procedures' criteria is a third
thing beside `method`/`bundle`/`pipeline` from `SYNTHESIS.md` §3. The same shape
recurs at `L.gan.stab` (blank on signal *and* role) and at `L.gradproc.conflict`.
Suggest a `modifier` kind whose axes are explicitly "those of the procedure it
modifies".

**7.6 Two nodes are axis-invisible refinements.** `M.moco-v2`, `M.moco-v3`
(and nearly `M.roberta`, `M.simmim`) take identical values to their parent on all
four axes — they are engineering deltas (MLP head, augmentation strength, batch
size, training length). I left `M.moco-v2`/`M.moco-v3` fully blank to say so
explicitly. If a large share of the corpus's `M.*` nodes are axis-invisible, the
four axes cannot distinguish the papers people actually cite, and lineage is the
only axis carrying them — which is an argument for keeping lineage even after
its demotion from backbone.

**7.7 `M.simclr-v2`, `M.latent-diffusion`, `M.stable-diffusion-training` and
`M.dinov2` are `pipeline`s mislabelled `method`.** Each is two or three
sequential runs (SimCLR v2 = contrastive pretrain → supervised finetune →
self-distil; latent diffusion = train the autoencoder → train the diffusion in
its latent space). I pinned the union of their stages' values, which is exactly
the counting bug `SYNTHESIS.md` §3 introduced `expands_to` to prevent, and the
`expands_to` column is empty for all four.

**7.8 Nodes that are architecture, not procedure** (`DRAFT_PHASE1_A` tension 7,
still open): `M.sn-gan` (spectral normalisation), `M.spade`, `M.stylegan`,
`M.dit-training`, `M.ttt-layers`. I pinned them as the training methods their
names are attached to, but `M.ttt-layers` I left **blank on role** because it is
a layer, not a slot — the only node in the region I could not place on role at
all.

**7.9 Lowercase-flagged nodes.** 21 `M.*` nodes carry the `notes` flag
*"confirm it is a named procedure, not a description"*. I pinned all of them;
I judge **18 to be genuinely named procedures** (classifier-free guidance,
consistency models, contrastive divergence, flow matching, rectified flow,
progressive distillation, scheduled sampling, professor forcing, latent
diffusion, denoising score matching, score matching, deep belief net, instance
noise, stochastic interpolants, contrastive representation distillation, relative
patch position, rotation prediction, wav2vec 2.0). Three are descriptions rather
than named methods and should be reviewed for deletion: **`M.uniform-weighting`**
(the absence of a weighting scheme — and it is blank on signal for exactly that
reason), **`M.uncertainty-weighting`** (a description of Kendall et al.'s loss,
usually cited by author), and **`M.cfg-rescaling`** (a fix reported inside other
papers, never cited as a method — and it needs 7 negative pins, which is itself
the symptom).

---

## 8. Nodes I could not pin at all

None are fully unpinnable. The closest cases:

- `M.moco-v2`, `M.moco-v3` — blank on all three axes **by decision**, not by
  failure: they take their parent's values exactly (§7.6).
- `M.ttt-layers` — blank on `role` (§7.8); pinned on signal and attributes.
- `L.gan.stab` — blank on signal and role, because its five members split between
  objective terms (R1, PPL) and schedules/augmentations (TTUR, ADA, instance
  noise). Pinned `A.param.param` only.
- `L.mtl`, `M.uniform-weighting` — blank on signal, structurally (H4/§7.5).
- `L.ssl.jepa`, `L.flow.cont`, `L.score.guide`, `L.score.sample`, `L.tta.ssl` —
  blank on signal under rule 1; each is a genuine split, documented above.
