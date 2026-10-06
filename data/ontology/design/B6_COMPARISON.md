# B.6 — does the models dimension duplicate the domains `Method › Model design` subtree?

Run 2026-10-06. This comparison was the original justification for the whole
models exercise: *design the models hierarchy first, then compare it against the
domains subtree to settle empirically whether a separate models ontology earns
its keep or is duplicated work* (`MODELS_BRIEF` B.6, owner's plan, 2026-10-01).

## Answer: no duplication. They do not overlap at all lexically, and conceptually they meet only on the axes.

| | |
|---|---|
| domains `Method › Model design` subtree | **25 nodes**, 1204 corpus mentions |
| models lineage | **358 nodes** |
| models connectivity · topology · attributes | 24 · 7 · 39 |
| **lineage nodes sharing a name with ANY domains axis** | **0 of 358 (0.0%)** |
| connectivity values sharing a name | 1 of 24 (`Message passing`) |
| topology / attributes values sharing a name | 0 |

The zero is the headline. It is not a near-miss cleaned up by normalisation —
there is no literal overlap to clean up, because the two ontologies hold
different **kinds** of thing: domains holds architecture research **topics**,
the lineage axis holds **instances**, and A.4 said in advance that domains
"contains no instances."

## Where the domains concepts actually land

`CORRESPONDENCE.tsv` declares all 14, in the same checkable shape as
`BOUNDARY_CASES.tsv` and with no runtime dependency. The distribution is the
finding:

| lands on | count |
|---|---|
| models **connectivity** | 5 |
| models **attributes** | 3 |
| models **topology** | 1 |
| models **lineage** | **1** |
| no counterpart, or routed algorithm-side | 4 |

**Only one of fourteen lands on the lineage axis** — `implicit-depth-architectures`
→ `neural_ode`. Nine land on the three small axes.

## What this says about the faceting

Under the single-tree design the models hierarchy would have looked like a
genuine duplicate: its upper levels were `Convolutional network`, `Recurrent
network`, `Transformer`, `Autoencoder`, `Spiking neural network`,
`Normalizing flow`, `GAN` — which is nearly a restatement of the domains
`Model design` children.

Faceting moved exactly those concepts onto axes. So the apparent duplication was
real, and it was between the domains topics and what are now the models
**axes** — never the lineage. The redesign removed it as a side effect of
fixing a different problem, which is the strongest evidence available that the
axis split was the right cut.

## Consequence

**Keep both, and keep them independent.** Nothing is rooted in anything; the
shared layer remains vocabulary rather than hierarchy, exactly as A.4 required,
so either ontology can be re-derived without moving the other.

Two things worth remembering rather than re-deriving:

1. **The axes are where the dimensions meet.** A future change to the domains
   `Model design` subtree should be checked against `CORRESPONDENCE.tsv` —
   against the models *axes*, not the lineage.
2. **`generative-models` and `model-efficiency` are algorithm-side**, so a third
   of the domains subtree's concepts will meet the **algorithms** dimension, not
   this one. Re-run this comparison after algorithms is derived; the overlap
   there may be real where here it was not.
