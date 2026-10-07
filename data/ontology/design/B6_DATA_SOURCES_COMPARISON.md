# B.6 for data sources — structure against structure

#102 step 2, run 2026-10-07. Companion to `CORRESPONDENCE_DATA_SOURCES.TSV`.

Run **first** rather than last, on #93 Part 3's instruction, because for this
dimension the comparison *is* the structural decision rather than a closing
risk check: *"a dataset may need no hierarchy of its own, because it is largely
characterised by axes that already exist."*

Two questions, deliberately not conflated.

---

## §1 Residual — does any organising category need a tree of its own?

**No. Of the 18 legacy roots: 14 map to an axis that already exists, 2 to the new
`access`/`provenance` axes, 1 to both, and 1 is the drop branch.** Nothing is
left over.

| what the root divides by | roots | where it goes |
|---|---|---|
| modality | 7 | domains `modality` |
| modality + discipline | 3 | domains `modality` + `discipline` |
| modality combination | 3 | domains `modality` — including `Multimodal › Vision-language`, which `vision + nlp` maps onto **exactly** |
| task | 1 | domains `modality › Tabular › Transactional & interaction logs › Implicit behaviour logs` |
| artifact type | 3 | 2 → the new `access`/`provenance`; 1 (`large multi-modal benchmarks`) → algorithms `R.eval` + a set of sources |
| — | 1 | `ignore`, the drop branch |

**Conclusion: the dimension needs `access` and `provenance` and no lineage
tree.** #93 Part 3's hypothesis is confirmed. A data source is a set of values on
existing axes, plus two new ones, plus the #93 compute attributes.

### Three things this surfaced that are worth more than the conclusion

**The domains modality axis already anticipated RL observations.** It contains
`Tabular & structured records › Low-dimensional state & proprioceptive vectors`
— which is exactly what a MuJoCo observation is. That axis was derived from field
knowledge with no RL dataset in view, and it landed on the right value anyway.
It is also what lets `vision + rl` decompose instead of staying a compound root.

**`vision + nlp` maps exactly onto `Multimodal › Vision-language`.** The domains
work had already diagnosed and fixed the compound-root problem (the
Multimodal-as-union case), and the fix transfers unchanged. That is evidence the
two dimensions were derived from the same understanding rather than
independently guessing.

**`simulation` was an empty root, and the characteristic behind it is real.** v0
had a root with zero children; `provenance = program-synthesised` is what it was
reaching for. A dividing characteristic with no members is a different defect
from a wrong characteristic, and it is the one that goes away for free here.

### A methodological caution about §1

This mapping is a **judgement made by reading the axes**, not a measurement. The
lexical test — do the legacy root names appear as node names elsewhere — returns
**0 of 18**, and is simply the wrong instrument: `computer vision` is not a
*node name* in domains, it is the `Vision & imaging` value of the `modality`
axis. Inferring absence from a string mismatch is the same error as inferring an
alias from string similarity, which this work has already paid for once. The
table is therefore offered for review, not as a result.

---

## §2 Collision — is the name vocabulary shared?

**Almost not at all, and this is the informative contrast.**

| | overlap |
|---|---|
| legacy `datasets/v0` node names colliding with any other dimension | **4 of 502** |
| corpus data-source names colliding | **10 of 2559** |
| *for comparison:* algorithms vs the domains `method` axis (`B6_ALGORITHMS_COMPARISON.md`) | **102 of 111** |
| *for comparison:* models lineage vs any domains axis | **0 of 358** |

So data sources sit at the models end of that range, not the algorithms end:
**their names are a genuinely separate namespace**, and the duplication risk
that dominated the algorithms comparison does not arise here.

### The collisions are misextractions, not shared vocabulary

Every corpus collision is a model or an algorithm that landed in the dataset
slot:

```
CLIP  IMAGEN  PGD  T0  AutoAttack  Evol-Instruct  GEDI  GP Regression  PCL
Logical Inference  (the one genuine domains overlap)
```

Each appears in exactly one paper. That makes them **evidence for #103 rather
than a risk for this dimension**: the data-source slot occasionally catches a
model, which is a prompt-precision measurement, and the v5 prompt now states the
exclusion ("a source that is itself a Model… report that Model in the Run
instead"). The expected result after re-extraction is fewer than 10.

Two legacy node names are simply junk and go away with `v0`: `offline` and
`software engineering` as *dataset* nodes.

---

## §3 What this does **not** settle

- Whether `access` and `provenance` have the right **values**. §1 says two axes
  are needed and names their load-bearing cases; deriving the value sets is step
  3, and is done with no corpus access until frozen.
- Whether the **tail** needs anything. 81% of names appear in one paper, and
  step 1 measured that the admission rule's named-only clause accounts for only
  ~1.6% of names. Faceting has to carry the tail; this comparison does not test
  whether it can.
- The `Uninformative` roots on the domains `modality` and `discipline` axes have
  zero children. Data sources will need the same branch for names like
  `dataset`, and whether it is shared or per-dimension is a step-3 question.
