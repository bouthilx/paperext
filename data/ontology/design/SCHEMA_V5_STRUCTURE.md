# Schema v5 — structure

The entity/run structural decision for schema v5, settled 2026-10-07 by the
owner. Companion to `SCHEMA_V5_BRIEF.md` (the handover — read that first) and
`ALGORITHMS_EXTRACTION_REQUIREMENTS.md` (the prompt spec for `algorithms[]`).

Issues: **#94** models/runs/algorithms · **#93** datasets · **#89** research
fields. One migration, one converter, one re-extraction.

---

## 1. The decision

> **Entity lists stay top-level. `runs[]` is a fact table that references them.
> The pointer runs entity-ward: `runs[] → algorithms[]`, exactly as
> `runs[] → models[]` and `runs[] → datasets[]`.**

```
PaperExtractions
├── title · description · type
├── research_fields[]   ResearchField   one list with a role          (#89)
├── models[]            RefModel        identity + paper-level role
├── datasets[]          RefDataset      identity + role + compute fields (#93)
├── libraries[]         RefLibrary      identity + paper-level role
├── algorithms[]        RefAlgorithm    identity + paper-level role   (#94, new)
└── runs[]              Run             the fact table                (#94, new)
     ├── models[]       RunModel        {name, role_in_run}
     ├── datasets[]     RunDataset      {name, roles_in_run[]}
     ├── algorithms[]   RunAlgorithm    {name}
     └── execution_mode · epochs · parameter_count · accelerator_type/model/count
         · precision · parallelism · duration · utilisation · repetitions
```

Built in `src/paperext/structured_output/mdl/model_v5.py`. The run-side field is
`role_in_run` rather than `role` because the referenced entity has a role too
(`RefDataset.role` spells it exactly that) — see section 3.

`RefAlgorithm` mirrors `RefModel`: `name` · `aliases` · `is_contributed` ·
`is_executed` · `is_compared` · `referenced_paper_title`. The last field is not
ceremonial — it is what disambiguates `iql`, which is both Implicit and
Independent Q-Learning and whose bare string resolves to neither.

## 2. Why this direction

1. **The cardinality is many-to-many, so the pointer is a list either way.** One
   run executes many algorithms; Adam appears in many runs. `algorithms[].runs[]`
   would be no less a list than `runs[].algorithms[]` — it would only move the
   join to the side with worse locality. On the run side a run row is
   self-describing: read it and the compute profile is complete. That is already
   why `models` and `datasets` hang off the run.

2. **Algorithms exist in papers that have no run.** "We compare against PPO as
   reported in [12]" is a real mention with `is_executed=False` and no run.
   `is_executed` is already the gate for whether a run record exists
   (`SCHEMA_V5_BRIEF.md` D.1). This matters more for algorithms than for models:
   the dimension answers *which methods does the institute's output touch*, and
   compared and referenced mentions count. A design where algorithms live only
   inside runs cannot represent them — so the top-level list is required
   regardless of pointer direction, and once it exists the reversal buys nothing.

3. **Identity must be de-duplicated once per paper, not once per run.**
   `analysis/rollup.py` counts papers per node. With `adam` inlined in six run
   rows, the loader has to re-identify them as one algorithm by string
   similarity — the operation recorded as a defect in `SCHEMA_V5_BRIEF.md` C.4
   (token matching paired `gpt-j` with `GPT-4`). One top-level record with
   **written** aliases gives exactly one thing to resolve, once.

4. **Everything the extraction captures is paper-level.**
   `ALGORITHMS_EXTRACTION_REQUIREMENTS.md` §5 asks for name-verbatim, a locating
   quote, the paper's own framing, contributed/executed/compared, and stated
   composition. None is a property of a compute configuration. Inlining them
   duplicates all five per run and invites copies that disagree.

## 3. What considering the reversal did reveal: pair-valued facts

The reversal is wrong, but the case for it points at something real: **some facts
belong to the `(run, entity)` edge, not to either end.** Hence a reference is a
small object rather than a bare string — for two of the three entity types.

- **Datasets need it for the compute formula, which is the whole point of #94.**
  `6 × parameters × training examples × epochs` needs the *training* examples.
  A dataset's run-level role — trained on / validated on / evaluated on — is a
  different fact from `RefDataset.role` (contributed/used/referenced, which is
  paper-level), and the formula is wrong without it. `roles_in_run` is a list
  because one dataset can be both trained and evaluated on within one run, and
  one reference per named entity per run keeps the reference list a clean
  key→attributes map for the check in section 4.
- **Models need it too**: student/teacher pairs and ensemble members are
  distinguishable roles inside one run, which the paper-level
  `is_contributed`/`is_compared` cannot express.
- **The `execution_mode` invariant is a pair predicate.** *"No algorithm whose
  `role` is `R.fit.update` in an inference run"* constrains the edge, and is
  checkable at all only because role is an axis (`SCHEMA_V5_BRIEF.md` B.3). But
  the `role` it reads is the **ontology's**, resolved after extraction from the
  name and the quote — not a field an extractor fills. So that invariant needs
  the dimension loadable (#100); it is not a schema field.

**The field is named `role_in_run`, not `role`, deliberately.** `RefDataset.role`
and `RefLibrary.role` already mean contributed/used/referenced. Two fields named
`role` meaning different things on the two ends of one reference is the kind of
conflation the ontology work paid for twice (`A.deriv.fixed`; the respondent vs
annotator wording). The vocabularies also differ per entity type, so the enums
are separate.

### Correction to this section as first drafted: algorithms get no `role_in_run`

The evidence first quoted for giving algorithms one — *38 nodes resolve to no
role, concentrated in combinatorial solvers whose slot is a property of their
use*, Hungarian matching being an objective in DETR and a label-assignment step
in SwAV (`ALGORITHMS_EXTRACTION_REQUIREMENTS.md` §7) — is evidence about
**assigning the ontology's role axis**, which happens post-hoc from the name and
the quote. It is not evidence that an extractor can or should emit a per-run
role, and asking it to classify is precisely what would close the vocabulary.

The one algorithm fact that genuinely varies is *what the algorithm did in this
paper*, and that is recorded once, in free text, as `RefAlgorithm.paper_role`.
`RunAlgorithm` is therefore a bare reference. If #99 finds that a per-run
algorithm role is extractable after all, adding it is a field, not a redesign.

## 4. How a reference is spelled: by verbatim name, validated afterwards

There are no ids in the schema today — `RefModel.name` is `Explained[str]`.

**Reference by the verbatim name string**, and have the extractor copy it. Asking
an LLM to mint and maintain synthetic or integer ids across two lists is a known
failure mode; asking it to repeat a string it just wrote is not.

**The cross-reference check must report, never raise.** It does *not* belong in a
pydantic validator: the extraction runs inside an `instructor` retry loop, so a
raise would discard an entire paper's extraction over one mistyped name. Keep the
schema permissive and run the check afterwards, in the shape of
`axes_algorithms/resolve.py --audit` — list unmatched references and let them be
read, the same way 13 model names became recorded questions instead of guesses.

This is **one decision covering models, datasets and algorithms**, not three.

**Built**: `src/paperext/structured_output/mdl/check.py`, run over a corpus with
`uv run python -m paperext.structured_output.mdl.check --details`. Four codes,
and it raises on none of them:

| code | what it means |
|---|---|
| `unresolved-reference` | a run names something no entity list holds. A **written alias** resolves a reference; **similarity never does** — `gpt-j` against `GPT-4` stays unresolved, because a wrong repair is worse than a reported gap |
| `referenced-but-not-executed` | a run executes an entity whose `is_executed` is `False`. One of the two statements is wrong |
| `execution-mode-disagrees` | `RefModel.execution_mode` and `Run.execution_mode` disagree for a model that ran. `unknown` on either side is an absence of evidence and contradicts nothing |
| `executed-without-run` | an executed model no run accounts for. **Expected in bulk on converted data** — `convert_model_v4` leaves `runs[]` empty — so it is read per corpus, not per record |

`tests/structured_output/mdl/test_check.py` covers each, including the one that
is really a statement about the schema: an unresolved reference **validates**.

## 5. Sparse by design

Most papers say "we used RLHF" in a methods sentence and never tie it to a
configuration. So:

- **Many algorithms will have no run pointing at them.** An empty
  `runs[].algorithms` is **not** a defect and must not be validated as one. Same
  for a `RefAlgorithm` no run references — that is the `is_executed=False` case
  of §2.2 behaving correctly.
- **Expansion stays an ontology property, not an extraction demand**
  (`SCHEMA_V5_BRIEF.md` B.4). This structure *permits* RLHF to appear as one
  `RefAlgorithm` with three `Run` rows each referencing its stage's algorithms,
  and it permits the common case of one name and no runs. The composite node is
  what makes the two shapes comparable; neither is required of the extractor.

## 6. Consequences

**For the prompt.** The two lists are filled by different questions and should be
asked as such: `algorithms[]` asks *what named procedures does this paper name*
(open vocabulary — the load-bearing constraint, `SCHEMA_V5_BRIEF.md` D.2);
`runs[]` asks *what distinct compute configurations did it execute*, with the
grouping rule as an explicit positive **and** negative test, since `runs[]` is
where over-splitting lives (B.6).

**For #93 and #89.** Both inherit the same shape. #93's compute-estimation fields
split by locus: what a dataset *is* (size, modality, example count) stays on
`RefDataset`; how a run *used* it (which split, how many examples consumed) is a
`role_in_run` matter. #89's `research_fields[]` is a plain top-level list with a
role and no run reference — a paper's field is not a per-run fact.

**For the converter.** `convert_model_v4` adds `algorithms: []` and `runs: []` as
empty lists and moves `parameter_count` off `RefModel`. The field has **never
been populated** (A.3), so there is nothing to carry over — only a field to
relocate. No v4 extraction exists to migrate.

## 7. Open items

Settled while building:

- [x] **The `role_in_run` enums.** Datasets: train/validation/test/unknown,
      list-valued. Models: main/teacher/student/ensemble-member/unknown,
      single-valued. Algorithms: **none**, for the reason in section 3.
- [x] **A reference is a plain `str`, not `Explained[str]`.** A reference is a
      pointer and its quote lives on the entity it names; the quote that would
      matter for a run is the one locating the *run*, which the run's own fields
      already carry.

Still open:

- [ ] Whether `Run` needs a `checkpoint` reference to another run. It has its
      motivating case — the edge between RLHF stage 1 and stages 2–3 *is* a
      checkpoint reference (`SCHEMA_V5_BRIEF.md` B.3) — but it is the one field
      with no second use yet, and nothing in the first extraction will populate
      it, so it can wait for evidence instead of being guessed at now
- [ ] `Explained[list[Parallelism]]` is the first generic in this schema with a
      list argument. It produces a valid closed strict schema (checked against
      `backends.anthropic.strict_schema`: every object closed, every property
      required, definition names clean), but no live API call has used it yet,
      and the v4 comment about `instructor.Mode.TOOLS_STRICT` is a standing
      reminder that schema *shape* has broken at the API before
- [ ] The ontology-role half of the `execution_mode` invariant needs the
      algorithms dimension loadable (#100). Until then `check.py` covers only
      the schema-level half
