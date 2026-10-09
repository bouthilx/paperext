# One-paper annotation session: instructions

You are producing a **schema-v5 reference annotation for one paper**, by
adjudicating two models' extractions with the owner. This is #111 Part B. The
result is ground truth for the #12 bake-off, so a guess recorded here becomes a
wrong score for every arm later.

**Start by asking for the paper id if it was not given.** One paper per session,
on purpose: the runs half is slow to adjudicate and a long session drifts.

---

## 1. Read these first, in this order

| file | what it gives you |
|---|---|
| `src/paperext/structured_output/mdl/model_v5.py` | the schema and — in `SYSTEM_MESSAGE` — every extraction rule, stated at length |
| this file, §3–§6 | the rules that decide most disagreements, and how to run the session |
| `data/ontology/design/SCHEMA_V5_STRUCTURE.md` §3, §7 | why `runs[]` references entities by name, and the settled data-source decisions |

The paper's text is at
`$PAPEREXT_DIR_CACHE/fulltext/<paper_id>/fulltext.txt` — set
`PAPEREXT_DIR_CACHE=/home/bouthilx/projects/paperext-llm-backend/data/cache`.
**Read the paper.** You cannot adjudicate from the two extractions alone; that
is the whole reason a human is in the loop.

The two extractions:

```
data/mdl/queries/anthropic/claude-opus-5/<paper_id>_00.json      # arm A
data/mdl/queries/openai/gpt-5.6-sol/<paper_id>_00.json           # arm B
```

Both buckets also hold an unrelated 25-paper batch. **Select by paper id**, never
by globbing the bucket.

---

## 2. What is NOT being annotated

**Do not ask the owner about `provenance` or `referent`, or about the domains /
models / algorithms ontology axes.** None of them is extracted. They are
assigned post-hoc from the name and the quote (#102), and asking wastes the
owner's attention on a field that will not exist in the output.

Exactly one ontology value set is in the schema: **`access`** on
`runs[].data_sources[]`, because access is a property of the *mention*.

---

## 3. The rules that decide most disagreements

These are the ones that actually come up. The full text is in `SYSTEM_MESSAGE`.

**A run is a unit of compute the paper spent.** Two executions are the SAME run
unless one of these differs: execution mode, precision, parallelism, accelerator
count or type, scale, or dataset. 5 seeds × 20 learning rates is **one** run
with `repetitions` factors, not 100 runs.

**A fitting run is one coupled optimisation loop.** A GAN is ONE run — the
gradient flows through both networks. Actor+critic, encoder+decoder: one run. A
**frozen** network that only supplies targets or scores is a *participant*,
reported in the run's `models` with a non-`main` role, not a run of its own.

**`execution_mode`**: `train` / `finetune` if it fitted something, `inference`
if a **model** produced predictions, `generate` if the run produced data by
other means (stepping a simulator, transforming a corpus). `generate` must have
no `parameter_count` — that is the point of the value. Sampling a *model* for
training data IS `inference`.

**Only models THIS PAPER executed get a Run.** A model whose numbers are quoted
— from another paper, a leaderboard, or a shared benchmark's published results —
gets `is_executed=false` and **no run**. A comparison table is not evidence the
paper ran the rows.

**A Model is a separable learned object**: parameters that could be run
independently of the procedure that produced them. A SAT solver, a proof
checker, a hand-written heuristic is an **Algorithm or a Library, never a
Model**, even when the paper compares against it.

**A Data Source is a NAMED source of the examples a run consumes.** Excluded:
unnamed descriptions (`synthetic data`, `our drone recordings dataset`), the
software that implements a source (the MuJoCo *engine* is a Library; HalfCheetah
is a Data Source), and an **evaluation protocol** over a source (`Atari` yes,
`Atari 100k` no).

**`repetitions` is a list of factors, and the product is computed later.** One
entry per independent factor: 5 seeds of 20 learning rates is two entries,
`(seed, 5)` and `(hyperparameter, 20)`. **An empty list means the paper does not
say — never a count of 1.** And never record how many examples/episodes/items
the run *processed*: that is workload, not repetition. `1,540 test episodes` is
NOT a repetition.

**Never infer.** Every compute field is reported only when the paper states it.
`utilisation` especially: do not record an assumed 30–50%.

---

## 4. Procedure

**Entities first, runs last.** `runs[]` references entities by verbatim name, so
the names have to be settled before the runs that point at them.

Order: `title`, `description`, `type`, `research_fields`, `models`,
`data_sources`, `libraries`, `algorithms`, `runs`.

For each field:

1. **Diff the two arms.** Where they agree, say so in one line and move on —
   do not spend the owner's attention on it.
2. **For each disagreement, present it with the evidence**, in this shape:

   > **`models[]` — arm A has `Rainbow`, arm B does not.**
   > A's quote: *"...we compare against Rainbow (Hessel et al. 2018)..."*
   > Paper, §5.2: *"<the sentence you found yourself>"*
   > Rainbow appears only in Table 2 alongside published scores, and §5.2 says
   > *"numbers for baselines are taken from the original papers"*.
   > **Reading:** a quoted baseline gets `is_executed=false` and no run, so A is
   > right to list it and would be wrong to give it a run.
   > **Question:** keep it with `is_executed=false`?

   The paper citation is the part that matters. An arm's own quote is its
   *claim*, not evidence — the two arms quote different sentences precisely
   where they disagree.
3. **State a recommendation** when the rules decide it, and say which rule.
4. **When you do not know what context to provide, say so and explore.** Grep
   the fulltext, read the surrounding section, check a table. Then come back
   with what you found. Do not ask the owner to adjudicate a question you have
   not yet made answerable — and do not guess to avoid admitting that.

**Batch the easy ones.** If six entity names differ only by spelling, present
them as one list and ask for one decision. Reserve the slow, evidence-heavy
treatment for the ones that turn on a rule.

**`runs[]` deserves the most care and is where the arms differ most.** Walk the
paper's experiment section and establish what was actually run, then map it onto
the six criteria. Expect to find that *neither* arm's decomposition is right.

---

## 5. What to expect from the two arms (measured over all 26 papers)

| | |
|---|---|
| per-entity agreement | models **79%**, data sources **82%**, algorithms **69%**, libraries 68% |
| fields differing per paper | ~4.9 of 6, usually by one or two entries out of five |
| runs | arm A 185 total, arm B 224; same count on only **5 of 26** papers |

**Arm A (Opus 5) over-admits.** Its extras include unnamed descriptions
(`our drone recordings dataset (5.5 hours of traffic data)`, `vehicle dataset`)
and `Amazon Mechanical Turk` as a *library*. When A has an entity B lacks, check
the admission rules before assuming better recall.

**Arm B (gpt-5.6-sol) splits runs more.** It produced 224 runs to A's 185 and
reaches 15–16 runs on papers where A finds 10. Check against the six criteria
rather than averaging the two.

**Known failure modes, so you recognise them rather than rediscovering them:**

- **A frozen encoder labelled `main`.** Ten encoders saying `inference` inside a
  `train` run, on one paper, in *both* arms. The run is training a classifier
  *on top of* frozen embeddings; the encoders are participants. Their
  `role_in_run` should not be `main`.
- **`executed-without-run`**: a model family (e.g. all four Pythia sizes) marked
  executed with no run accounting for them. Either the runs are missing or the
  models were not executed — the paper decides which.
- **Protocols as data sources**: `Atari 100k`, `HELM`.
- **Non-learned tools as models**: solvers, proof checkers, tokenizers.

---

## 6. Output

Write the merged annotation to `data/mdl/merged/<paper_id>.yaml`, and
**validate it before writing**:

```python
from paperext.structured_output.mdl.model import PaperExtractions
from paperext.structured_output.utils import model_dump_yaml
# build the object, then:
text = model_dump_yaml(extractions)   # raises if it does not validate
```

`merge_papers.py` is the interactive alternative and does the same thing
field-by-field in `$EDITOR`; use it if the owner prefers, but **a session doing
the adjudication conversationally should write the file itself** — the point of
this format is that the reasoning happens in the chat, not in a text editor.

**Also append one row per adjudicated field** to
`data/ontology/design/c0_verification/adjudication_log.tsv`
(`paper_id`, `field`, `arm_A`, `arm_B`, `chosen`, `rule`, `note`). Create it
with that header if absent.

This log is the most valuable by-product of the exercise and it is free: it is
the only direct evidence of **which fields the models are unreliable on**, which
is what decides how much of the bake-off can rest on arm-to-arm agreement rather
than on ground truth (#111 Part C, tier 2).

Finally, commit: `git add` the yaml and the log, one commit per paper, message
`Reference annotation: <paper_id> (<arxiv>)`.

---

## 7. Rules for you, not for the schema

- **Never invent a value to finish a field.** `unknown` and an empty list are
  real answers and the schema is built to carry them.
- **Never default to one arm** because it is usually right. The reference set
  exists to measure that, and seeding it with the assumption destroys the
  measurement.
- **Absence is a real answer.** A paper with no runs — a survey, a position
  paper — correctly has `runs: []`. Two of the 26 are like this.
- **Report what the owner decided, not what you proposed.** If they overrule a
  recommendation, the log records their choice and the rule they invoked.
- If a field needs a schema change rather than a decision, **stop and say so**.
  Do not encode a workaround into ground truth.
