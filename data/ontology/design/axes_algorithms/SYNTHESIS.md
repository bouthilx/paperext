# Algorithms — phase 1 synthesis and the rulings that followed

Written 2026-10-06, after runs A and B. Working document for the build; the
handover remains `../ALGORITHMS_BRIEF.md`.

Drafts: `phase1/DRAFT_PHASE1_A.md` (524 nodes, built from the four-axis
hypothesis) and `phase1/DRAFT_PHASE1_B.md` (170 nodes, derived free). Both
freezes were verified from tool-call order, not from the agents' claims: zero
Grep/Glob/WebFetch in either, and no tool input naming `ROUTING`, `models/v0`,
`proposed_categories`, `categorized_models` or the backend checkout.

---

## 1. What the two runs agree on

A was given the four-axis hypothesis. B was given only the participant rule and
the orthogonality test. Agreement across that gap is the evidence; divergence is
the question.

**They derived the same pipeline stations.** Seven match near one-to-one:

| A — one `role` axis, 9 top nodes | B — 10 separate axes |
|---|---|
| `R.data` Data preparation | `DAT` data construction |
| `R.exp` Experience generation | `EXP` experience acquisition |
| `R.fit` Producing/adapting the object | `FIT` parameter estimation |
| *(A's separate `signal` axis)* | `OBJ` objective and signal source |
| `R.coord` Coordination across workers | `EXEC` execution and resource strategy |
| `R.search` Configuration search | `SRCH` configuration/structure search |
| `R.rewrite` Parameter-space rewriting | `PTX` post-fitting transformation |
| `R.out` Producing outputs | `OUT` output production |
| `R.adapt` Test-time adaptation | — (B's tension T2: it had no slot) |
| `R.eval` Evaluation and assessment | `EST` estimand and identification |

**Both demoted lineage from the backbone** — the one part of the hypothesis
ported from models, and it survived neither run. B's reason is the sharper:
*most of this vocabulary has no citation lineage at all* (CutMix, EM, IPW,
k-fold CV, difference-in-differences). A reached the same place by a different
route: 94 independent family roots with no imposed top layer, because every
candidate top-divider was already a facet. Lineage stays an axis; it stops being
the organizing principle.

**Both hit the same boundary case by name**, FlashAttention, and both said they
could not draw the rule. Two agents landing on one example makes it a real gap.

**Both named the same top unresolved problem**: classical methods are named as
whole runs, deep methods as parts. A called it a granularity mismatch, B called
it a missing `composite/pipeline` node type.

## 2. Decisions

### Role is one hierarchical axis, not ten

B's own sentence settles it: *"`N/A` on most axes is the normal state."* Ten axes
where nine are always N/A **is** one axis with ten children, written the long
way — and the long way loses the roll-up, since nothing can then answer "what
proportion named a data-preparation procedure".

### Signal splits into source × form (A)

Orthogonal by the axis test, symmetrically: **MoCo and BYOL** agree on source and
differ only on form (`contrast` vs `agree`); supervised classification and
autoregressive pretraining agree on form and differ only on source. A flat list
makes one of those pairs look identical. It also dissolves B's worry that `OBJ`
was absorbing the dimension.

*Corrected during the pinning pass.* This first read "SimCLR and BYOL", which is
wrong: BYOL's target comes from the EMA copy, so it needs `S.src.self.own` too
and the pair differs on **both** facets. MoCo also carries a momentum encoder, so
MoCo/BYOL is the pair that isolates form. The split survives -- its motivating
example did not.

The pinning pass also found *why*: `S.src.self`'s stated characteristic is "which
part of the input is the target", which `mask`/`next`/`view`/`corrupt`/`ident`
answer and **`self.own` does not** -- that one answers *who computed the target*,
which is what `S.src.ext.model` answers on the other branch. It is a principle-of-
division violation inside the axis, and it shows up as redundancy: `self.own` is
the second-most-used source in the generative region and co-occurs with a real
part-of-input value on 23 of its 31 nodes.

### Signal does not union up the chain

The hypothesis said it would. **DDPM → DDIM falsifies it**: DDPM is a training
objective and its own descendant is a decoder with no training target. Signal
takes per-node values with negative pins, as in models — not union inheritance.

### Attributes families need an explicit scope predicate

Six families are universal; six (`regime`, `world`, `rltarget`, `hier`, `exec`,
`agents`) are empty outside sequential decision-making. Without a scope, *"what
proportion of papers are on-policy"* has an ambiguous denominator. A measurement
bug, not a cosmetic one. Kept — sparsity is never a reason to drop (A.3).

### `R.exec` is added to role

Neither draft had the right slot: A's `R.coord` is about workers, B's `EXEC`
bundles too much. `R.exec` is **how the computation is carried out without
changing what is computed** — FlashAttention, ZeRO, tensor parallelism, gradient
checkpointing, mixed precision.

## 3. Owner rulings, 2026-10-06

### Evaluation procedures are in

Cross-validation, bootstrap confidence intervals, train/test splitting. The
participant rule as first written excluded them — they measure rather than
produce — but classical statistics is in scope and is close to unrepresentable
without them. A's `R.eval` is confirmed rather than flagged.

Consequence to settle with #93/#94: **metrics** are still not in this dimension.
The line is that a procedure which *determines* a reported number is in, and a
quantity that *is* the number is a different kind of entity.

### The numerics test is withdrawn

It read: *if it only changes time or memory for an identical result, it is an
implementation.* The owner killed it with sorting — mergesort and bubble sort
produce identical output, and mergesort is not "an implementation of sorting".
Identical output does not demote a procedure.

Replacement:

> **An algorithm is a named procedure. A library is a named artifact that
> implements procedures.** The test is whether it has a procedure description
> that could be independently reimplemented.

**FlashAttention is an algorithm** — tiling, online softmax rescaling, backward
recomputation, with a complexity claim (O(N²d) FLOPs, O(N) HBM accesses instead
of O(N²)), implementable in CUDA, Triton or JAX. The `flash-attn` *package* is a
library. One string, two entities, in two dimensions — the `mujoco` trap from
#93.

**It is not a model-side entity.** It computes the same function as standard
attention; a model trained with it has the same architecture and the same
parameter semantics, and swapping in standard attention reproduces the outputs.
That is exactly what separates it from Longformer or Performer, which change the
function computed and therefore change the model.

### Composite nodes, replacing the `slot`/`bundle` granularity tag

The counting bug: `PPO` names one slot, `XGBoost` names four (second-order
boosting objective, greedy split-finding search, regularized tree learners,
shrinkage schedule), `RLHF` names three stages. As ordinary multi-valued nodes,
a paper writing `RLHF` and a paper writing `SFT + reward model + PPO` are
incomparable, and role roll-ups inflate the classical branch systematically.

A `kind` column on lineage, with `expands_to` for the composites:

| kind | meaning | runs |
|---|---|---|
| `method` | fills one or more slots directly | one run |
| `bundle` | components combined **simultaneously** — Rainbow, XGBoost | one run |
| `pipeline` | **stages in sequence** — RLHF, self-play loops | **several runs** |

The bundle/pipeline split is not cosmetic: it is what connects to #94. `RLHF` is
three runs with three `execution_mode`s; `Rainbow` is one. A composite that
expands into stages tells `runs[]` how many rows to expect.

### The sibling test is substitutability, not co-occurrence

B caught the defect: read literally, "two algorithms that run together cannot be
siblings" forbids RandAugment, Mixup and CutMix from being siblings, and people
stack all three. B's patch ("a single X") presumes the slots it is deriving.

> **Siblings are mutually substitutable** — swap one for the other and the rest
> of the run still makes sense. Mixup ↔ CutMix substitutes. PPO ↔ Adam does not.

Co-occurrence is then only *evidence* of non-siblinghood, and only when the two
are not substitutable.

## 4. Open after phase 1

- [ ] **Merge A and B** into one structure: A's four axes, A's role hierarchy
      plus `R.exec`, A's signal split, with B's station definitions where they
      are sharper and B's rejected-alternatives argument preserved.
- [ ] B's `MACH` crosscut — B called it "the first thing I would cut" and
      measured it ~80% redundant with the role axes. Resolve on merge.
- [ ] A's `R.eval` subtree was drafted under a flag that is now lifted; it needs
      building out properly, since classical statistics depends on it.
- [ ] The two lineage edge types A found (`derived-from` vs `instantiates`)
      probably need separating.
- [ ] Dropout and parameter initialisation are in, batch norm is out — A flags
      this as inconsistent on its face. Needs a joint ruling with models.
- [ ] Whether a tokenizer vocabulary is a model (A), and where `BPE`-the-merge-
      procedure sits versus the learned merge table.
