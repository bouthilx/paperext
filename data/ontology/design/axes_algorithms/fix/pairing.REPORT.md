# Pairing the signal axis — the 79 nodes that needed a judgement

Input `fix/pairing.tsv` (79 nodes with >1 source *and* >1 form), output
`fix/pairing.pinned.tsv` (same columns, same order, same 79 rows; `signal` and
`notes` changed only). Sources read: `signal/nodes.tsv`, `role/nodes.tsv`,
`attributes/nodes.tsv`, `lineage/nodes.tsv` (for the family pins each node
inherits), `phase1/DRAFT_PHASE1_A.md` worked examples, `PINNING_FINDINGS.md`.

---

## 1. Pairs per node

| pairs | nodes |
|---|---|
| 1 | **15** |
| 2 | **60** |
| 3 | **4** |
| 4+ | 0 |

147 pairs over 79 nodes, mean 1.86. The 3-pair nodes are `M.rlhf`,
`M.stargan`, `M.stable-diffusion-training` and `M.latent-diffusion`. Nothing
needed four.

**The cross-product was wrong on every one of the 79.** Before: these nodes
licensed 2×2 up to 5×2 and 3×3 combinations — 79 nodes licensed 419 pairs where
147 are true, so 65% of the licensed combinations were false. The three worst
cases collapse hard and cleanly:

- `M.rlhf` 3×3 = 9 licensed → **3** true (one per stage, each stage consuming
  exactly one source and one form).
- `M.stargan` 3×3 = 9 → **3** (adversarial / attribute-classification / cycle),
  one source and one form each, every pinned value used exactly once.
- `M.stable-diffusion-training` 3×3 = 9 → **3** (autoencoder reconstruction,
  autoencoder bound, latent denoising).
- `M.fqe` 5×2 = 10 → **1**, after dropping four values (see §2).
- `M.mdd` 2×4 = 8 → **2**, and two of its forms are not separately expressible
  (§4).
- `M.mean-teacher` 3×3 = 9 → **2**.

### Where a cross-product turned out to be *right*

Two nodes genuinely cross two sources with one form or vice versa, and the
check mattered:

- **`M.dinov2`** — two terms, same form (`S.form.agree`), different sources
  (`view + own` for the DINO term, `mask + own` for the iBOT term). The pair
  list carries this exactly.
- **`M.unreal-auxiliary-tasks`** — `(reward, lik)` looked like the classic false
  diagonal and is real: the reward-prediction auxiliary task *is* a
  classification of the next step's reward. Both of its licensed diagonals are
  true terms, so the cross-product happened to be sound here.
- The VAE family, the penalised-regression family and the matrix-completion
  family all produce two pairs with the **same** source and different forms. For
  those, "a source with two forms" was correct, because fit term and penalty are
  separately weighted (beta-VAE's `beta` is the proof).

---

## 2. Values dropped

59 values dropped across 43 nodes, in three distinct classes. Only the second
class is a correction of substance.

### 2a. Redundant interior ancestor (17) — bookkeeping, not judgement

A pair needs one value per slot, so where a node pinned both an interior node
and its own child, the child wins:

- `S.src.design` dropped beside `S.src.design.adjust`/`.quasi`/`.indep` on
  `M.tmle`, `M.double-ml`, `M.g-computation`, `M.fuzzy-rd`, `M.liml`,
  `M.notears`, `M.dag-gnn`, `M.synthetic-control`, `M.synthetic-did` (9).
- `S.src.ext` dropped beside `S.src.ext.pref`/`.human` on `M.bpr`, `M.listmle`,
  `M.listnet`, `M.ranknet`, `M.lasso-selection`, `M.boruta`,
  `M.mutual-information-filtering`, `M.recursive-feature-elimination` (8).

### 2b. Mis-pinned — false of the node (28)

| node | dropped | why |
|---|---|---|
| **`M.fqe`** | `S.form.moment`, `S.src.design`, `S.src.design.adjust`, `S.src.ext` | all four arrive through `L.bandit.ope`'s second parent `L.causal.adjust`. FQE is a Bellman-residual regression, not an estimating-equation estimator; the moment/design values belong to its IPS and doubly-robust siblings. Exactly the §10 pathology. **Caveat:** FQE's identification does rest on a coverage assumption, so the dropped design value was a true claim with no mechanism on this node. |
| **`L.optdisc.submod`** | `S.src.none`, `S.form.none` | imported from `L.optdisc`, which `value_parent` already says no longer propagates; a submodular coverage objective *is* a criterion. Supports §3e. |
| **`L.causal.rep`** | `S.src.ext.human` | arrives via the `L.da.stat` → `L.da` parent. The outcome a counterfactual estimator fits is measured, not annotated: the `S.src.ext.obs` case. |
| **`M.cevae`, `M.dragonnet`, `M.ganite`** | `S.form.div` | inherited from `L.causal.rep` (itself from `L.da.stat`). Only CFR/TARNet has an IPM balance penalty; these three do not. |
| **VAE family** (`M.vae`, `M.beta-vae`, `M.nvae`, `M.iwae`, `M.wake-sleep`, `M.vae-elbo-scoring`) | `S.src.self.struct` | the `L.vi` family default. Phase 1's own VAE example has `S.src.self.ident` alone. |
| **`M.diffusion-reconstruction-scoring`** | `S.src.self.struct` | the `L.anom` family default; the target is the per-example input. |
| **`M.ivf-pq`** | `S.form.none`, `S.src.ext` | the codebooks *are* fitted (`none` is the `L.retr.index`/`L.inst` default for the search step); and the indexed corpus is not a training target — the same confusion §8 records for `A.param.inst`. |
| **`M.boruta`, `M.mutual-information-filtering`, `M.recursive-feature-elimination`** | `S.form.none` | contradicts the `lik`/`spars` on the same row; this is the merge clash §1 names for filter selection. |
| **`M.bayesian-online-change-point-detection`** | `S.form.lik`, `S.src.self.struct` | `lik` is the `L.anom.cp` default for likelihood-ratio change detection; in the Bayesian member the predictive likelihood is a component *inside* the posterior recursion. `struct` is wrong: the target is the next element. |
| **`M.bpr`** | `S.src.self.struct` | the sampled negative is a per-example target, which `S.src.self.struct`'s own negative test excludes. Confirms the §1 ruling from the other side. |
| **`M.sindy`** | `S.src.ext` | the `L.symreg` default; the target derivative is computed from the input series itself. |
| **`M.liml`** | `S.form.moment` | the `L.causal.iv` default. LIML's k-class/GMM representation is the same single criterion, not a second term. |
| **`M.der`** | `S.form.recon` | named the logit-matching distance that `S.form.agree` already names, and `recon`'s own negative test excludes it. |

Note the pattern: **24 of these 28 are a family default or a second-parent
import**, not an agent error. Five of the six nodes
`PINNING_FINDINGS.md` §5 predicted (second-parent imports) show up here —
`M.fqe` is the worst single case in the file.

### 2c. Co-description of a term already encoded (14) — information lost to the representation

A pair carries one form, so where two forms describe one term, one had to go.
These are **not** mis-pins; see §4.

`M.airl` (`lik`), `M.bpr` (`contrast`), `M.dino` and `M.dinov2` (`div`),
`M.f-gail` (`div`), `M.lcm` and `M.progressive-distillation` (`recon`),
`M.listmle`, `M.listnet`, `M.ranknet` (`lik`), `M.mdd` (`div`, `margin`),
`M.mean-teacher` (`inv`), `M.v-mpo` (`bound`).

### 2d. Values added (2) — flagged, not silent

A pinned source cannot be written without a form, so two nodes would have had to
lose a real term:

- `M.der` + `S.form.lik` — the current-task supervised cross-entropy had no form
  pinned at all.
- `M.dragonnet` + `S.form.lik` — the outcome and propensity head losses had no
  form pinned.

Three more nodes have a term whose source or form is simply absent and I did
**not** invent it; they are recorded in `notes` as gaps:
`M.fixmatch`/`M.flexmatch`/`M.softmatch` (no `S.src.ext.human` for the labelled
term), `M.ganite` (no form for the factual supervised loss),
`M.seqgan-style-corrections` (no `S.src.env.rm` for the discriminator reward),
`M.simclr-v2` (the supervised finetuning stage between its two pinned stages),
`M.wake-sleep` (the sleep phase's own generated data).

---

## 3. Composites: one pair per stage, and composites must not defer

Only one of the 79 is marked composite (`M.rlhf`, `kind=pipeline`). My answer:

**One pair per stage is right, and composites should carry signal, not defer to
their expansion.** Three reasons.

1. It is lossless and it is exactly what fixes the bug. RLHF's three stages
   consume exactly its three sources and three forms, one each:
   `(ext.human, lik); (ext.pref, rank); (env.rm, return)`. The 3×3 product
   licensed six combinations the pipeline does not have; the stage pairing
   licenses none of them and drops nothing.
2. There is nothing to defer *to*. `expands_to` on `M.rlhf` is prose
   (`supervised finetuning; reward-model fitting; PPO against the reward model`),
   not node ids. Deferring would make "which papers fitted a reward model"
   unanswerable for every paper that says only "we used RLHF" — which is most of
   them, because RLHF is the name the corpus uses.
3. The same shape appears on nodes that are *not* marked composite and would
   therefore never defer: `M.stable-diffusion-training` and `M.latent-diffusion`
   (autoencoder stage then diffusion stage), `M.hubert` and `M.wavlm` (clustering
   stage then masked-prediction stage), `M.simclr-v2` (pretrain → finetune →
   distil), `M.tmle`/`M.double-ml`/`M.g-computation`/`M.fuzzy-rd` (nuisance fit
   then targeting step), `M.wake-sleep`, `L.pref.rm`,
   `M.grpo-with-reward-model`. That is 14 nodes behaving as stage composites
   against 1 marked one — the same order-of-magnitude undercount §9 measured for
   `kind=bundle` (2 set, 65 behaving). Any rule keyed on `kind` would miss them,
   so one pair per stage has to be the convention for ordinary `method` nodes
   too.

**The cost, and a recommendation.** The pair list cannot say *that* pairs are
stages: `M.rlhf` (three sequential stages) and `M.stargan` (three simultaneous
weighted terms) have structurally identical encodings. A query like "papers that
fit a reward model as a separate stage" cannot be distinguished from "papers with
a reward-model term". If stage-vs-term matters, the pair list needs either a
separator that is stronger than `; ` or a per-pair stage index. I kept pair
*order* meaningful (stage order / main term first) as a weak convention, and
said so in the notes of every staged node.

---

## 4. What the pair representation still cannot say

Five distinct failures, in rough order of how much they cost.

1. **One term, two forms** — the representation's own blind spot, and the signal
   table already documents it. `S.form.rank`'s note says of Bradley-Terry
   "both values apply"; `M.ranknet`'s single loss *is* a ranking criterion and
   *is* a likelihood. Same on `M.listmle`/`M.listnet` (Plackett-Luce),
   `M.bpr` (pairwise ranking *and* explicit negatives), `M.airl` (an adversarial
   objective that *is* the MaxEnt-IRL likelihood), `M.dino`/`M.dinov2`
   (cross-entropy to an EMA teacher = KL to a teacher), `M.v-mpo` (an EM lower
   bound on the return objective), `M.lcm`/`M.progressive-distillation`
   (a distillation regression that is also a distance to a target image).
   Twelve of the 14 §2c drops are this. The spec's rule "two forms means two
   terms" is clean but false in these cases.
2. **Two of these drops erase a method's whole contribution.**
   `M.f-gail` loses `S.form.div`, which is the only thing distinguishing it from
   `M.gail` — their signal cells are now identical. `M.mdd` loses
   `S.form.margin` and `S.form.div`, making it identical to `M.dann` although
   "margin disparity discrepancy" is the paper's title. A per-pair *secondary
   form* slot (or allowing a pair to name a form set with the understanding that
   it is still one term) would fix both; two independent facet sets would not.
3. **A gate is not a term.** `S.form.conf` on `M.fixmatch`/`M.flexmatch`/
   `M.softmatch` is a threshold on the pseudo-label's *eligibility*, not an
   additive criterion. I wrote it as its own pair `(S.src.self.own, S.form.conf)`
   to keep it queryable and flagged every one in notes, but the encoding claims a
   second term that does not exist. (For `TENT`, outside this file, the same pair
   is a genuine term — the value is doing two jobs.)
4. **A penalty has no target source.** `S.form.spars` is the clearest case: on
   `M.notears`, `M.lasso-selection`, `M.sindy`, `M.dag-gnn`, the dictionary/SAE
   family, the matrix-completion family and the synthetic-control family, the
   penalty is a genuine separately-weighted term that is *not driven toward
   anything*. A pair demands a source, so I repeated the fit term's source, which
   is the least-wrong available and still wrong. Either `S.src.none` has to
   become legal inside a pair (term-level "no target", distinct from node-level
   "fits nothing"), or `S.form` needs a marker for penalty-shaped values.
   Nine nodes, 18 pairs.
5. **Conditioning is neither source nor form.** `M.stable-diffusion-training`
   carries `S.src.ext.pair` for the caption. The caption is not what the loss is
   driven toward (the noise is); it conditions the denoiser. I put it in the
   score pair as a second source, which reads as "the target came partly from
   image–text pairs" — not true. Same wrinkle on `M.cdan` (adversary conditioned
   on classifier output) and `M.pix2pix`.

Two smaller items:

- **Part vs sibling.** The VAE family's `(ident, bound); (ident, recon)` claims
  two sibling terms where `recon` is a *component* of the bound. Defensible
  because `beta` reweights them, but the representation cannot distinguish
  "whole and part" from "two terms". Six nodes.
- **`S.src.self.own` plays two roles at once.** The brief's own `M.spr` pairing
  puts `self.own` only in the `agree` pair, although the bootstrapped value
  target of the RL term is *also* the model's own output. I reproduced the
  brief's pairing verbatim for `M.spr` and included `self.own` in the return pair
  on the other value-based nodes (`M.fqe`, `M.pbl`, `M.v-mpo`,
  `M.unreal-auxiliary-tasks`, `L.mbrl.search`), following phase 1's PPO and DQN
  examples. That asymmetry needs a ruling: either bootstrapping always earns
  `self.own` in the return pair, or it never does.
- Three nodes carry a criterion with **no `S.form` value at all**: `M.boruta`'s
  shadow-feature permutation test, `M.notears`/`M.dag-gnn`'s smooth acyclicity
  constraint, and the filter methods' feature–target dependence measure. Same
  shape as the gap §3a-bis just filled with `S.form.metric` — these are the next
  three candidates.

---

## 5. Multiple sources per pair: needed **often**

48 of 147 pairs (33%) carry more than one source, on **36 of 79 nodes** (46%).
Two carry three sources (`M.wavlm`, `M.progressive-distillation`). This is not a
rare escape hatch — it is the load-bearing half of the fix, and it falls into two
recurring patterns:

1. **A self-prediction target against the model's own target network** (24
   pairs): `S.src.self.own` plus whatever the target is a prediction *of* —
   `view` (`M.dino`, `M.mean-teacher`, `M.swav`, the `*Match` family), `next`
   (`M.spr`, `M.pbl`), `mask` (`M.dinov2`, `M.hubert`, `M.wavlm`), or
   `env.reward` (value bootstrapping: `M.fqe`, `M.v-mpo`,
   `M.unreal-auxiliary-tasks`, `L.mbrl.search`). The target genuinely *is* the
   EMA network's prediction of that thing, exactly as the SPR brief describes.
2. **A classical estimator where the value and the comparability come from
   different places** (18 pairs): `S.src.ext` (the measured outcome) plus
   `S.src.design.adjust`/`.quasi` — `M.tmle`, `M.double-ml`, `M.g-computation`,
   `M.fuzzy-rd`, `M.liml`, `M.synthetic-control`, `M.synthetic-did`,
   `L.causal.rep`, `M.cevae`, `M.dragonnet`, `M.ganite`. And the analogous
   "per-example target plus dataset geometry" on the dictionary/SAE and
   matrix-completion families.

If multi-source had been disallowed, pattern 1 would have forced every
self-distillation method back into a false cross-product and pattern 2 would have
forced every design-based estimator to choose between its outcome and its
identification strategy. **Keep it.**

---

## 6. Carry-forward

- The `S.src.ext.obs` migration touches this file: `S.src.ext` on the eleven
  causal/matrix-completion pairs and `S.src.ext.human` on the four
  feature-selection wrappers are all the "measured, not annotated" case under
  that value's sharpened test. The pairs are written so the substitution is a
  one-value rewrite inside the pair.
- `S.form.spars`'s missing source (§4.4) and the one-term-two-forms case (§4.1)
  are the two items a datasets-dimension pairing pass should settle *before* it
  runs, not after.
- The 24-of-28 split in §2b says it again: **a family default and a
  second-parent import are the two ways a wrong pin arrives**, and neither is
  visible to a homelessness check. §10's rule — only `derives-from` and
  `instantiates` carry values — would have prevented about half of them,
  `M.fqe`'s four included.
