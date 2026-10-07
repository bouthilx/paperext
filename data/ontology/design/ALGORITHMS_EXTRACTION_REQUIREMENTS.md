# `algorithms[]` extraction — requirements

Written 2026-10-07, closing **D.2** of `ALGORITHMS_BRIEF.md`. The deliverable
itself belongs to **#94** (schema v5, with `runs[]`); this file is what #96 hands
over, so the prompt is written against the ontology without being trapped by it.

Sequencing context: **design → extract → revise → categorise**. This extraction
is step 2, and step 3 exists *because* step 2 is the first real evidence this
dimension will ever have.

---

## 1. The scope rule the prompt must carry

> An algorithm is a **named procedure a run executes**: preparing the data,
> producing or adapting the learned object, or using it to produce outputs.

In scope: data preprocessing and augmentation, experience generation, training
objectives and gradient estimators, parameter update rules, which parameters are
adapted, coordination across workers, configuration and architecture search,
post-training compression, **decoding and test-time search**, and **evaluation
procedures** (cross-validation, bootstrap intervals, train/test splitting).

Out of scope: things that are not procedures — datasets, libraries, hardware, and
the learned object itself — and **unnamed descriptions** of procedures. `CutMix`
is an entry; "we normalised the images" is not.

Two boundaries that were decided and must be stated, because an extractor will
otherwise guess:

- **A model component is not an algorithm.** The test is whether specifying the
  **network** requires it or specifying the **run** requires it. Dropout and
  batch norm are model components (`nn.Dropout(p=0.1)` is a module with a
  placement and a rate); weight decay, label smoothing and gradient clipping are
  algorithms. R-Drop and VAT *are* algorithms although both are built out of
  dropout, because each adds a term to the objective.
- **A procedure is not its implementation.** FlashAttention is an algorithm — it
  has a published procedure with a complexity claim, reimplementable in CUDA,
  Triton or JAX. The `flash-attn` package is a library. The same string can name
  both; record the procedure.

## 2. The prompt must take an open vocabulary — this is the critical constraint

**Do not hand the extractor this ontology as a closed list to choose from.** Ask
for **free-text names plus the paper's own framing**, and use the ontology only
to define scope and to give examples of the *kinds* of thing in range.

The reason is structural, not stylistic. A closed vocabulary makes step 3
circular: the extractor finds only what we already listed, the revision has
nothing to revise against, and it rubber-stamps the design. The 77 corpus names
that currently match no node exist *only* because the models extraction was open.
That property has to be preserved on purpose.

## 3. Why the existing sample cannot be reused, measured

The 105 names available today were all drawn from the `models[]` slot by an agent
prompted to find **models**, so they over-represent algorithms with the surface
form of a named system:

| region | % of ontology | % of corpus hits |
|---|---|---|
| reinforcement learning | 10% | **52%** |
| classical ML / statistics | 23% | 9% |
| optimisation / systems | 16% | 6% |
| data preparation | 14% | 6% |
| inference / adaptation | 26% | 18% |
| generative / SSL | 10% | 9% |

**Decoding and evaluation have zero hits.** Direct evidence rather than
inference: `adam` and `adamw` were extracted into `libraries[]` — that
misrouting *is* the bias.

So: use the 105 for **blind-spot detection only** (a name with no node is a real
gap however the sample was drawn). **Never** treat absence as evidence, and never
report frequencies from this sample as describing the field.

## 4. Acceptance tests for the new prompt

Known misroutings, which a correct prompt fixes:

- [ ] `adam`, `adamw` come back under `algorithms[]`, not `libraries[]`
- [ ] `pytorch` does not come back under `models[]`
- [ ] at least some **decoding** procedures appear (beam search, nucleus
      sampling) — zero would mean the widened scope did not reach the prompt
- [ ] at least some **evaluation** procedures appear (k-fold, bootstrap)
- [ ] at least some **preprocessing** appears beyond augmentation
- [ ] `iql` is returned with its surrounding context, never resolved: it is both
      Implicit and Independent Q-Learning, and the bare string resolves to
      neither

## 5. What the extraction must capture per mention

- the **name as written**, verbatim, including the paper's own abbreviation
- a **quote** locating it, as the models extraction did — this is what let 13
  `unsure` rows be recorded as questions instead of guesses
- the **role the paper gives it**, in the paper's words, not ours
- whether it is **contributed, executed or compared**, mirroring `models[]`
- for a composite, **what the paper says it is made of**, if it says

Deliberately *not* asked for: an ontology node, an axis value, or a slot. Those
are assigned afterwards, from the name and the quote. Asking the extractor to
classify is what makes the vocabulary closed.

## 6. What the ontology gives back in return

- **`role`** lets `runs[]` keep its invariant: `execution_mode: inference`
  forbids an algorithm whose role is `parameter update rule`, but permits the
  preprocessing and the decoder. Before the scope widened this was checkable
  from entity type alone.
- **`expands_to`** holds node_ids, so `RLHF` and `SFT + reward model + PPO` roll
  up to the same thing. A `pipeline` also tells `runs[]` how many rows to
  expect — RLHF is three runs with three `execution_mode`s, Rainbow is one.
- **`SPELLINGS.tsv`** absorbs surface variants without new nodes.

## 7. Known gaps the extraction should be expected to expose

Reported honestly so that finding them is not mistaken for a surprise:

- **71 nodes resolve to no signal**, 27 of them the evaluation procedures just
  brought into scope (`L.boot`, `L.test`) — a bootstrap interval does compare
  something, so `S.form.none` is false for it. Deferred to step 3 on purpose.
- **38 nodes resolve to no role**, concentrated in combinatorial solvers whose
  slot is a property of their *use*: Hungarian matching is an objective in DETR
  and a label-assignment step in SwAV.
- **65 nodes behave as bundles and 14 as stage pipelines, while only 9 are
  marked.** A rule keyed on `kind` will miss them until the marker is populated,
  and roll-ups over `role` are not comparable between the classical and deep
  branches until it is (1.69 roles per classical method against ~1.5 deep, and
  the excess is whole-run naming rather than bundling).
- **~346 nodes are flagged as possibly descriptions rather than named
  procedures.** The test is whether any paper cites them, which only this
  extraction can answer.
