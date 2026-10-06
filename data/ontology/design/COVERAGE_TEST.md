# Extension test: all 2483 names against the four axes

Owner's step three (2026-10-02): *"extend this to all names to test."*
Run 2026-10-06, mechanically, before spending agent time.

## Result: the axis set survived

**Nothing in the corpus demanded an axis value that does not exist, and nothing
wanted two values on single-valued topology.** The gaps this exercise found were
found earlier, by the *pinning* pass during the lineage merge — four missing
connectivity values and the attention-sparsity family — and are already filled.
That is the honest headline: pinning falsifies an axis set, name-matching does
not.

## Where the 2483 names go

| bucket | names | mentions | |
|---|---|---|---|
| placed in a lineage node | 220 | 724 (20%) | |
| **algorithm-side**, deferred | ~148 | ~460 (13%) | SimCLR, PPO, DQN, GFlowNet, LoRA, FedAvg |
| size/version of a placed node | 78 | 193 (5%) | grown by the second pass under R7 |
| recurring, needs placing | ~200 | ~460 (13%) | ordinary categorization work |
| one-paper tail | 1854 | 1854 (52%) | grown by the second pass |

The design accounts for the first three directly; the last is tail by
construction. **The actionable residual is ~200 recurring names.**

## What the residual actually contains

- **Named designs neither run drafted**: `gearnet` (5), `starcoder` (4),
  `gpt-neo` (4), `codegen` (3), `distilhubert` (3), `ecapa-tdnn` (3),
  `faenet` (3), `knn-lm` (3), `realm` (3), `gpt-3.5-turbo` (4), `gpt-4v` (3),
  `midjourney` (3). Ordinary gaps, not structural ones.
- **Contributed one-offs** clustered in a few groups: `diffpret`, `dyngfn`,
  `lagg-a`, `lopt-a`, `gsdm`.
- **Generic descriptions** — `two-layer neural network` (4), `autoencoder` (3).
  These pin axes and have **no lineage node**, which is the design working, not
  a miss.
- **`pytorch` (3) extracted into `models[]`** — the extraction defect already
  on the #94 list, alongside `adam`/`adamw`/`bert` in `libraries[]`.

## The one real finding: alias coverage is thin

Lineage nodes carry almost no spellings, so string matching fails on forms that
are plainly the same concept: `recurrent neural networks` vs `Recurrent
network`, `convolutional neural network (cnn)`, `vision transformers`,
`transformers`, `graph attention network (gat)`. Every lineage node needs an
alias set covering plurals, the `X neural network` / `X network` alternation,
and parenthesised acronyms.

## Instrument caveat

These counts come from successively looser string matchers and each pass moved
the numbers, so **treat the shape as solid and the digits as approximate**. One
false match is worth recording as a warning: token-set matching paired `gpt-j`
with `GPT-4`, because dropping stopwords collapsed both to a single token. Alias
sets must be written, never inferred by a matcher.

Mechanical matching is now exhausted. What remains needs judgement, and the two
questions it would answer that this pass could not are whether any name needs a
*new* axis value and whether any needs two topology values.
