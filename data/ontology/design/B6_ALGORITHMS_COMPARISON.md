# B.6 for algorithms — does this dimension duplicate domains?

Written 2026-10-07, closing the last design question on **#96** and the
`Re-run B.6 after algorithms` item on **#95**.

**Method: structure against structure.** Never sample against sample. The only
algorithms vocabulary available today was drawn through the `models[]` slot and
is biased ~5x toward RL, with zero hits on decoding and evaluation — so a
sample-level comparison would measure two differently-biased samples rather than
the two ontologies. This compares the 1672 algorithms nodes and 465 domains axis
nodes directly.

---

## 1. Lexical overlap: 15 shared names, one of them a homograph

| shared name | domains | algorithms |
|---|---|---|
| Continual learning | `method:continual-learning` | `L.cont` |
| Federated learning | `method:federated-learning` | `L.fed` |
| Kernel methods | `method:kernel-methods` | `L.kernel` |
| Knowledge distillation | `method:knowledge-distillation` | `L.kd` |
| Markov-chain Monte Carlo | `method:mcmc` | `L.mcmc` |
| Meta-learning | `method:meta-learning` | `L.meta` |
| Normalizing flows | `method:normalizing-flows` | `L.flow` |
| Offline reinforcement learning | `method:offline-rl` | `L.orl` |
| Pruning | `method:pruning` | `L.prune` |
| Quantization | `method:quantization` | `L.quant` |
| Self-distillation | `method:self-distillation` | `L.kd.self` |
| Semi-supervised learning | `method:semi-supervised-learning` | `L.semi` |
| Sequential Monte Carlo | `method:sequential-monte-carlo` | `L.seq.pf` |
| Variational inference | `method:variational-inference` | `L.vi` |
| **OPTICS** | `discipline:optics` | `M.optics` |

**The last row is a homograph, not a correspondence.** Domains `optics` is the
branch of physics; algorithms `M.optics` is Ordering Points To Identify the
Clustering Structure. Precisely what the rule *aliases are written, never
inferred* exists for — a string-similarity matcher would have merged them.

So: **14 real lexical matches**, every one of them between the domains `method`
axis and algorithms `lineage`.

## 2. Structural overlap: 102 of 111, which is the real answer

The lexical count badly understates it. Taken branch by branch
(`CORRESPONDENCE_ALGORITHMS.tsv`):

| domains `method` branch | nodes | verdict | algorithms counterpart |
|---|---|---|---|
| Learning signal | 12 | **axis** | the whole `signal` axis, plus `A.regime`, `A.agents` |
| Training regime | 14 | lineage | `L.da`, `L.mtl`, `L.cont`, `L.meta`, `L.fed`, `L.dpar` |
| Computational machinery | 26 | lineage | `L.mcmc`, `L.vi`, `L.seq.pf`, `L.causal`, `L.tts`, `L.dec` |
| Model design | 26 | split | architectures → **models**; efficiency → `L.prune`/`L.quant`/`L.kd` |
| Model analysis | 12 | lineage | `L.interp`, `L.robust`, `L.calib`, `L.priv` |
| Data curation | 4 | lineage | `L.curate`, `L.synth` |
| Learning theory | 6 | **none** | genuinely disjoint |
| Uninformative | 3 | none | a disposal branch, no counterpart by design |

**102 of 111 (91%) name something this dimension also names.** Models' B.6 found
zero of 358. The difference is not a defect in either: domains' `method` axis is
*about* methods, and so is this dimension.

**`Learning signal` is the sharpest case.** It is not merely overlapping, it is
the same question asked once per dimension: supervised / self-supervised /
reinforcement are `S.src.ext.human` / `S.src.self.*` / `S.src.env.reward`;
online-vs-offline RL is `A.regime`; multi-agent is `A.agents`.

**The genuinely disjoint branch is the informative one.** `Learning theory` —
generalization, sample complexity, expressivity, training dynamics, scaling
behaviour — has no algorithms counterpart and should never acquire one. Those are
*properties studied*, not procedures executed. That it comes out empty is
evidence the topic/entity line is real and not merely asserted.

## 3. This is not duplication, and the distinction is load-bearing

> **Domains holds research topics. This holds entities.**

`method:federated-learning` means *this paper researches federated learning*.
`L.fed` means *this paper used a federated algorithm*. A paper that trains a
classifier with FedAvg because its data is siloed is not federated-learning
research, and filing it under the domains node would make it so — the
contributed-versus-used error that **#89** exists to prevent.

The 91% is therefore a **risk list, not a merge list**: every one of those 102
nodes is a place where an annotator can make exactly that error, and the 14
lexical matches are where it is most likely because the strings are identical.

**Consequences:**

1. **Do not root either dimension in the other.** The shared layer between
   dimensions is vocabulary, not hierarchy (A.3); each stays re-derivable alone.
2. **The 14 identical strings need a disambiguation note on both sides**, saying
   which dimension means researched and which means used.
3. **`Learning signal` should not be re-derived per dimension.** It is one
   characteristic with two uses, and the two should be kept consistent by
   construction rather than by coincidence — a candidate for the shared
   vocabulary layer when the dimensions become loadable.
4. **`Model design` is the only branch straddling three dimensions**, and the
   models B.6 already recorded that `generative-models` and `model-efficiency`
   route algorithm-side. That prediction is now confirmed from this side.

## 4. What this does not settle

Whether annotators actually make the topic/entity error, and how often. That is
measurable only once `algorithms[]` is extracted and can be compared against
`research_fields[]` on the same paper — a disagreement rate between the two is
the natural check. Recorded for the post-extraction revision.
