# Schema v5 — design brief and handover

Written 2026-10-07, after the models (#95) and algorithms (#96) ontologies were
built and closed. Companion to `ALGORITHMS_BRIEF.md` (which this file succeeds as
the active handover), `ALGORITHMS_EXTRACTION_REQUIREMENTS.md` (the prompt spec
for `algorithms[]`), `MODELS_BRIEF.md` (the entity model) and
`B6_ALGORITHMS_COMPARISON.md`.

**Read this file first when resuming.** It is the handover.

Issues: **#94** models/runs · **#93** datasets · **#89** research fields ·
**#99** post-extraction revision · **#100** loadable dimensions.
Closed and done: **#95** models ontology · **#96** algorithms ontology.

---

# Part A — where we are

## A.1 The sequencing this sits in (owner, 2026-10-07)

> **1. Design the ontologies from field knowledge → 2. Plan and run the
> extraction → 3. Revise the ontologies against real data → 4. Categorise.**

**Step 1 is complete.** Step 3 is budgeted (#99) *because* step 1 had no usage
evidence; with reliable data it could have been skipped. **Schema v5 is step 2,
and it is now the only thing on the critical path.**

What v5 unblocks: #13 (fresh 2023–2026 extraction) and #14 (re-extract 2024),
which unblock #17/#18/#19 (the analysis and report). Nothing downstream moves
until v5 lands.

## A.2 One migration, three changes

v5 is **one** migration, **one** converter and **one** re-extraction, but three
independent changes to three parts of the schema:

| issue | change | state |
|---|---|---|
| **#94** | `runs[]` as a fact table; `algorithms[]` as a new entity list; `parameter_count` moves from `RefModel` to the run | designed, unbuilt |
| **#93** | dataset compute-estimation fields (Part 1 decided) | designed, unbuilt |
| **#89** | `research_fields[]` as one list with a role, replacing `primary`/`sub` | designed, unbuilt |

They can be implemented in any order but must ship together, because a single
converter and a single re-extraction run cover all three.

## A.3 What the code actually looks like today

`src/paperext/structured_output/mdl/` holds `model_v1` … `model_v4` plus
`convert.py`. `PAPEREXT_CFG` defaults to `config.mdl.ini`.

- **`model_v4.py` is the active proxy** and already defines `ExecutionMode`,
  `RefModel.execution_mode` and `RefModel.parameter_count`.
- **Neither has ever been produced.** No corpus has been extracted with v4; the
  legacy-2024 corpus (1999 papers) carries only
  `name · aliases · is_contributed · is_executed · is_compared ·
  referenced_paper_title`. So v4's new fields are untested in practice, and v5
  moves one of them (`parameter_count`) before it has ever been populated.
- `convert.py` has `convert_model_v1/v2/v3`, a `CONVERT_MODEL` map, a
  `CONVERT_CHAIN` and `_detect_version`. **v5 needs a `convert_model_v4` and an
  extension of both the chain and the detector.**
- Everything is `Explained[T]` — `quote` + `justification` + `value`. **Keep
  this.** The quote is what let 13 model names be recorded as open questions
  instead of guesses, and it is the only reason the ontology work could audit
  the extractor at all.

---

# Part B — #94, the main piece

The issue body is the specification and is still accurate. What follows is what
the models and algorithms work added to it, which the issue does not yet say.

## B.1 `algorithms[]` is a new entity list, and its ontology is built

`models/v0`'s `other algorithms` (110 children) was a **type confusion**, not a
junk drawer: algorithms had no entity type, so `ant colony optimization`, `c51`
and `bm25` shared a tree with `blip`. **114 of 260 recurring corpus names route
algorithm-side**, including the most-mentioned name in the model slot (`simclr`,
20 papers).

The dimension now exists: **1672 lineage nodes** plus three facet axes (signal
56, role 46, attributes 97), `axes_algorithms/resolve.py --audit` clean.

**The scope rule, widened twice by the owner:**

> An algorithm is a **named procedure a run executes**: preparing the data,
> producing or adapting the learned object, or using it to produce outputs.

So data preprocessing, experience generation, objectives, update rules,
parameter subsets, coordination, configuration search, post-training
compression, **decoding, test-time search and evaluation procedures** are all in.
Out: non-procedures (datasets, libraries, hardware, the learned object) and
**unnamed descriptions**. `CutMix` is an entry; "we normalised the images" is not.

**`ALGORITHMS_EXTRACTION_REQUIREMENTS.md` is the prompt spec.** Read it before
writing any prompt. Its load-bearing constraint, and the one most likely to be
dropped: **the prompt must take an open vocabulary** — free-text names plus the
paper's own framing, with the ontology used only for scope and for examples of
the kinds of thing in range. Hand the extractor a closed list and **step 3
becomes circular**: it finds only what we listed and the revision rubber-stamps
the design. The 77 corpus names that match no node exist only because the models
extraction was open.

## B.2 Two boundaries the extractor will otherwise guess

- **A model component is not an algorithm.** The test is whether specifying the
  **network** requires it or specifying the **run** requires it.
  `nn.Dropout(p=0.1)` is a module with a placement and a rate, so dropout and
  batch norm are model components (they live in models' new
  `stochastic-regularisation` and `normalisation` attribute families). Weight
  decay is an optimiser argument, label smoothing a loss argument, gradient
  clipping a training-loop argument — all algorithms. **R-Drop and VAT are
  algorithms although both are built out of dropout**, because each adds a term
  to the objective.
- **A procedure is not its implementation.** FlashAttention is an algorithm; the
  `flash-attn` package is a library; neither is a model. The owner killed the
  tempting "identical output means implementation" test with sorting: mergesort
  and bubble sort produce identical output and mergesort is not an
  implementation of sorting.

## B.3 What the ontology gives `runs[]` in return

- **`role` keeps the `execution_mode` invariant checkable.** Widening the scope
  cost #94 the old invariant: `execution_mode: inference` no longer implies an
  empty `algorithms[]`, because an inference run carries its preprocessing and
  its decoder. The check becomes **"no algorithm whose `role` is
  `R.fit.update`"**, which is expressible only because role is an axis.
- **`expands_to` holds node_ids, so composites are countable.** A paper writing
  `RLHF` and one writing `SFT + reward model + PPO` roll up identically.
- **`kind=pipeline` tells `runs[]` how many rows to expect.** `RLHF` is three
  runs with three `execution_mode`s — supervised finetuning, reward-model
  fitting, then PPO against the frozen reward model — because **a run is the unit
  that produces one learned object**, and RLHF produces three (the SFT model, the
  reward model, the aligned policy). `Rainbow` is `kind=bundle`: six named
  improvements active simultaneously in one optimisation loop, one network out,
  one run.
- **`runs[].checkpoint` now has its motivating case.** The edge between RLHF's
  stage 1 and stages 2–3 *is* a checkpoint reference. It was an open item with no
  worked example; this is it.

## B.4 Expansion is an ontology property, not an extraction demand

Most papers say "we used RLHF" and that is the only term we will get. The
ontology records what that decomposes into; **the extraction is not required to
enumerate three runs.** When a paper does describe its stages, `runs[]` can carry
them and they will agree with `expands_to`. The composite node is what makes the
two shapes of reporting comparable — it is not a reporting requirement.

## B.5 Acceptance tests for the new prompt

Known misroutings a correct prompt fixes, plus coverage checks:

- [ ] `adam`, `adamw` come back under `algorithms[]`, not `libraries[]`
- [ ] `pytorch` does not come back under `models[]`
- [ ] **non-zero** decoding procedures (beam search, nucleus sampling) — zero
      means the widened scope never reached the prompt
- [ ] **non-zero** evaluation procedures (k-fold, bootstrap)
- [ ] non-zero preprocessing beyond augmentation
- [ ] `iql` returned **with its context and unresolved**: it is both Implicit and
      Independent Q-Learning, and the bare string resolves to neither

## B.6 The risk the issue already names, and why it matters more now

**Over-splitting.** `runs[]` gives the extractor room to list eight
configurations where the paper described one sweep. The grouping rule — same run
unless `execution_mode`, `precision`, `parallelism`, accelerator count/type,
scale or dataset differs; hyperparameter variation stays in one run counted in
`repetitions` — must go into the prompt as an **explicit positive and negative
test**, not as prose.

`repetitions` is not optional detail: 5 seeds × 20 configurations is 100× the
compute, and in many ML papers the sweep *is* the budget. **Unknown, not 1, when
absent.**

---

# Part C — what the ontology work learned that applies here

These are process findings, paid for, and each would cost the same again to
rediscover.

1. **A coverage check is not a correctness check.** The rule "if nothing fits,
   leave it blank and report it" finds *absence*. Three of the largest findings
   in step 1 were pins that existed and were **wrong or too weak** — a
   cross-product licensing 62% false combinations, 169 nodes parked on an
   interior node, and a value true-by-precedent and false-by-test on ~60 nodes.
   **Ask for doubts, not just failures.** The `## Tensions` sections earned more
   than the deliverables did.
2. **A worked example propagates further than a rule.** Phase 1 pinned
   `A.deriv.closed` on EM; sixty nodes inherited the error by precedent. If the
   v5 prompt carries examples, they will be copied more faithfully than the
   instructions — so get the examples right first.
3. **State the convention, not just the task.** Six agents pinning the same axes
   used two different conventions (full value set vs deltas), producing 350 of
   401 apparent disagreements that were pure artefact. For v5 this means: fix in
   writing whether a field means "stated in the paper" or "inferred", before any
   extraction runs.
4. **Never infer an alias from string similarity.** Token matching paired `gpt-j`
   with `GPT-4`; a morphological rule put `bayesian neural networks` under the
   graphical-model node; and B.6 caught `optics` (the branch of physics) against
   `M.optics` (the clustering algorithm). Aliases are **written**, with claim
   priority, and ties are **rejected**.
5. **Agreement across independent runs is the evidence; divergence is the
   finding.** Two phase-1 derivations with different instructions produced the
   same ten pipeline stations. Four of six pinning regions independently asked
   for the same missing value. That is what justified keeping it.
6. **Measure before diagnosing.** "`divides` edges do not propagate values" was
   stated, justified with a misread count, and withdrawn: only 19 of 170
   denial-carrying nodes were multi-parent at all.

---

# Part D — open items and traps

## D.1 Specific to #94

- [ ] `convert_model_v4` + `CONVERT_CHAIN` + `_detect_version` extension
- [ ] `parameter_count` moves `RefModel` → run. Note it has **never been
      populated**, so there is no migration data to preserve — only the field
- [ ] `is_executed` stays the gate: a referenced-but-not-run baseline gets no run
- [ ] `parallelism` is **extracted, never inferred from libraries** — DeepSpeed
      alone spans ZeRO-1/2/3 and offload variants. `MODELS_BRIEF.md` Part C has
      the open question of whether libraries are a third run participant; the
      conclusion was that library-based inference is too imprecise to replace an
      explicit field
- [ ] `utilisation`: record Epoch's 30–50% as **an assumption, not a
      measurement**, when absent
- [ ] Partial coverage of `duration`/`utilisation`/`parallelism` is **expected
      and accepted**. Filling it from repositories and reference papers is #92,
      deliberately out of WS-A…WS-E

## D.2 Traps

- **The open-vocabulary constraint is the whole value of step 3.** If it is
  dropped, #99 cannot do its job and there is no second chance without another
  extraction.
- **`algorithms[]` has no usage evidence at all** — not weak evidence, none. The
  105 names available today came through the `models[]` slot and are biased ~5×
  toward RL with **zero** decoding and evaluation hits (`adam`/`adamw` in
  `libraries[]` is that bias caught in the act). Do not report frequencies from
  that sample as describing the field, and do not use absence in it as evidence.
- **`analysis/rollup.py` returns `dict[str, str]` and needs
  `dict[str, set[str]]`** for multi-parent. Nothing can be rolled up correctly
  until it lands. Tracked in #100.
- **The corpus lives in a different checkout**:
  `/home/bouthilx/projects/paperext-llm-backend/data/mdl/queries/openai/legacy-2024/`
  (2110 files) + `vertexai/` (102) = 1999 distinct papers. This working copy has
  only 102 extractions, so nothing here can be recomputed from it.
- **Tracked config files must not hold credentials**; `[env]` entries in
  `config.mdl.ini` are blank placeholders.

## D.3 Standing constraints

- **Never push to `main`. Open a PR.**
- **Get agreement before posting issue plans.** Opening PRs needs no permission.
- New code must be typed — Python ≥ 3.14, built-in generics, `from __future__
  import annotations`. `uv run mypy src/paperext tests`, `uv run black . && uv run
  isort --profile black .`, `uv run pytest tests`.

---

# Part E — artefact map

```
data/ontology/design/
├── SCHEMA_V5_BRIEF.md                      <- this file, the active handover
├── ALGORITHMS_EXTRACTION_REQUIREMENTS.md   <- the prompt spec for algorithms[]
├── ALGORITHMS_BRIEF.md                     <- superseded as handover; Parts A/B/D still the rationale
├── B6_ALGORITHMS_COMPARISON.md             <- 102 of 111 domains `method` nodes overlap; a risk list, not a merge list
├── CORRESPONDENCE_ALGORITHMS.tsv
├── MODELS_BRIEF.md / MODELS_AXES.md / MODELS_DERIVATION_BRIEF.md
├── axes/            (domains, 5 axes, 465 nodes, #91)
├── axes_models/     (lineage 358 · connectivity 24 · topology 7 · attributes 51; resolve.py; HANDOVER_TO_MODELS.tsv)
└── axes_algorithms/
    ├── lineage/ signal/ role/ attributes/   (1672 · 56 · 46 · 97)
    ├── resolve.py                           (--audit, --homeless, --redundant, --node)
    ├── SYNTHESIS.md                         (what phase 1 settled)
    ├── PINNING_FINDINGS.md                  (what pinning 1697 nodes found)
    ├── phase1/ pinning/ fix/                (drafts and per-region reports; keep the REPORTs)
    └── phase2/VOCABULARY.tsv                (105 names, count-free, blind-spot use ONLY)
```

`resolve.py --audit` must stay green. It is the only thing that detects breakage
rather than letting it be discovered later.
