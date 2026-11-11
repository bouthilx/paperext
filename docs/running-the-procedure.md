# Running the procedure

The command sequence from a list of papers to a loaded ontology, with the
decision points marked and the places it currently stops.

Companion to `docs/annotation-and-ontology-handoff.md`, which carries the
judgment — why each check exists, which numbers mean what, what we paid to
learn. This file is the mechanics. Every command below was run against this
checkout; where a stage is blocked, the blockage was reproduced, and the
measured numbers are from this repo as it stands.

```
  paperoni-report ──▶ paperoni-enrich ──▶ download-convert ──▶ query
   paper metadata      abstracts +          PDF ──▶ .txt        extraction JSON
                       OpenAlex topics                         per paper
                                                                   │
                       ┌───────────────────────────────────────────┤
                       ▼                                           ▼
                   verify + check                         categorize-items
                   is the output sound?                    one Item per name
                                                                   │
                 axis design (TSV) ──▶ convert_axes ──▶ snapshot   │
                                                             │     │
                                                             ▼     ▼
                                                        categorize
                                                     place names, write vN+1
                                                             │
                                             categorize-eval │ categorize-report
                                             the gate        ▼ what the run did
```

The left-hand half (through `query`) produces the corpus. The right-hand half
turns names into a hierarchy. **They are joined only by vocabulary** — the
extraction carries terms, categorisation is a second pass — so the right half
can be re-run without re-extracting.

---

## Stage 0 — environment

```console
uv sync --all-extras
uv run pytest tests
```

`uv sync --extra <one>` **replaces** the environment and drops the provider
SDKs. Always `--all-extras`.

Credentials are supplied at runtime and never committed; `[env]` in
`config.mdl.ini` holds blank placeholders and the file is tracked. Export what
the backend you picked needs (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
`PAPEREXT_PAPERONI_TOKEN`).

Every config key has an env override, `PAPEREXT_<SECTION>_<KEY>`. The ones that
matter here: `PAPEREXT_DIR_CACHE`, `PAPEREXT_ANTHROPIC_MODEL`,
`PAPEREXT_ANTHROPIC_MODE`, `PAPEREXT_OPENAI_MAX_OUTPUT_TOKENS`.

---

## Stage 1 — assemble the corpus

```console
uv run paperoni-report   ...                      # paper metadata -> JSON
uv run paperoni-enrich   <papers.json>            # abstracts + OpenAlex topics, in place
uv run download-convert  --paperoni <papers.json> # PDF -> <cache>/fulltext/<id>/fulltext.txt
```

`download-convert` and `paperoni-enrich` are documented in `README.md` with
their full option lists and worked examples; both are re-runnable and skip what
they already have. `paperoni-report` has no README section — read
`src/paperext/paperoni/report.py`.

**Decision point — where the cache lives.** `download-convert --cache-dir` and
`PAPEREXT_DIR_CACHE` must agree, and every later command that touches paper text
needs the same value. `data/cache/` does not exist in this checkout; nothing is
tracked under it.

---

## Stage 2 — extract

### 2a. Prove the backend answers, before spending

```console
uv run backend-check --platform anthropic
```

One trivial completion. Costs nothing and separates an auth problem from a
schema problem, which otherwise look alike three hours in.

### 2b. Prove the papers resolve, before spending

```console
export PAPEREXT_DIR_CACHE=<path-to-fulltext-cache>
uv run python -c "
import json; from pathlib import Path; from paperext.utils import Paper
raw = json.loads(Path('<papers.json>').read_text())
got = [Paper(p).get_link_id_pdf() for p in raw]
print(f'{sum(g is not None for g in got)}/{len(got)} papers resolve')"
```

Expect `N/N`. `0/N` means the cache path is wrong: `Paper._pdfs` globs
`CFG.dir.cache`, every paper resolves to `None`, the filter empties the list and
the run completes having queried nothing. `query.py` now refuses an empty list,
but this check costs a second and has caught a real run.

### 2c. Extract one paper and read it

```console
uv run query --platform anthropic --papers <one-paper-id>
```

Then open the JSON. On a new model or after any prompt change this is the whole
early-warning system — see the handoff doc §1.1 for the three unrelated
constraints that can each block a different backend.

### 2d. Extract the corpus

```console
uv run query --platform anthropic --concurrency 4 --paperoni <papers.json>
```

Output: `data/mdl/queries/<provider>/<model-slug>/<paper_id>_00.json`.

**Decision point — `--platform` is not optional in practice.** Omitting it uses
`[platform] select` (`openai`). And the *model* half of the output path comes
from that backend's own config section, not from the flag, so editing
`[anthropic] model` changes the output directory with it.

**Decision point — `--concurrency`.** Default 4. The ceiling is the provider's
per-organisation rate limit, which this code cannot know; raise it only after a
run has shown headroom. Measured pace on one 25-paper batch: ~3m20s per paper,
so ~28 hours for 2000 papers at 4, ~14 at 8. Exceeding the limit degrades into
backoff rather than failing.

**Decision point — a prompt change means a new bucket.** Re-running queries only
what is missing or stale, which is what makes a long run practical and also how a
corpus ends up holding two prompt versions.

The run is resumable and reports how many papers are already extracted versus
how many it will actually query, because the ETA covers only the second number.

---

## Stage 3 — is the extraction sound?

```console
uv run python -m paperext.structured_output.mdl.verify data/mdl/queries/<provider>/<model>
uv run python -m paperext.structured_output.mdl.check  data/mdl/queries/<provider>/<model> --details
```

`verify` reports three kinds of result and the distinction is the point: **CHECK**
is pass/fail and a failure is a prompt defect; **PROBE** must be non-zero and zero
means a widened scope never reached the prompt; **MEASURE** is a number with no
pass condition. `check` reports per-record invariants by code
(`unresolved-reference`, `referenced-but-not-executed`,
`execution-mode-disagrees`, `generate-run-with-models`, `executed-without-run`).

`BASELINE.md` is the same `verify` run over `legacy-2024`, and the comparison
supports exactly one inference: a failure that appears in both is **inherited**, a
failure that appears only in the new run is **new**.

**Decision point — what a bad result means.** A CHECK failure sends you to the
prompt. A zero PROBE sends you to the prompt's *scope statement*, **never** its
vocabulary — handing the extractor the probe vocabulary as a closed list makes the
ontology revision circular. An ontology-shaped problem is not fixed here at all.

**Do not proceed to Stage 4 on an extraction you have not read this way.** The
ontology revision is *against* the extraction, so an extraction that failed for a
prompt reason sends the revision chasing a defect that is not in the ontology.

---

## Stage 4 — build or revise the ontology

Per dimension. Four exist on disk: `models`, `datasets` (reporting name) /
`data_sources` (schema field), `libraries`, `domains`, plus `algorithms` as a
snapshot with no items path (§5).

### 4a. Fold the corpus into items

```console
uv run categorize-items --dim models --platform openai --model gpt-5.6-sol \
    --out items_models.jsonl --top 20
```

```
# models: 368 distinct names, 402 mentions
      6     6p  GPT-4
      5     5p  LLAMA2-7B
      4     4p  BERT
```

One `Item` per distinct name, ordered most-mentioned first — which is also the
order to run the agent in, since common names move the counts and their decisions
inform the rest. Grounding is **extraction-records-only**: quote, justification,
aliases, `is_executed`, co-occurring entities. **No fulltext is read**, so this
half needs no cache, no PDFs and no paperoni token.

**Trap — `--queries-dir` is the base, not the bucket.** It composes
`<queries-dir>/<platform>[/<model>]`. Passing the bucket itself
(`--queries-dir data/mdl/queries/openai/legacy-2024`) silently yields
`0 distinct names, 0 mentions` rather than an error, because the composed path
does not exist. Use `--platform` / `--model`, or point `--queries-dir` at
`data/mdl/queries`.

**Dimension names do not match schema field names, on purpose.** `--dim datasets`
reads the v5 `data_sources` field; the dimension keeps its old name because
renaming it would invalidate every recorded decision keyed on it. The mapping is
in `DIMENSION_FIELDS` (`items.py`): `models→models`,
`datasets→data_sources`, `libraries→libraries`, `domains→research_fields`.

### 4b. Author the axes, then convert

Axes are authored as TSV node tables under
`data/ontology/design/axes*/<axis>/nodes.tsv`, with `characteristic`,
`positive_test` and `negative_test` columns — those are what make a placement
checkable by someone who did not design the node. The TSV stays the source of
truth because a TSV is what a person reviews in a diff.

```console
uv run python -m paperext.ontology.convert_axes                    # report only
uv run python -m paperext.ontology.convert_axes --write            # all dimensions
uv run python -m paperext.ontology.convert_axes --write models     # one
```

Report mode on this checkout:

```
algorithms   backbone=lineage    lineage 1672, signal 56, role 46, attributes 97, 29 spellings
data_sources backbone=--         access 6, provenance 6, referent 5
domains      backbone=--         discipline 160, method 111, modality 81, sector 78, properties 35
models       backbone=lineage    lineage 358, connectivity 24, topology 7, attributes 51, 96 spellings
```

**Run it without `--write` first.** The parent column and separator differ per
dimension (`parent_id` single-parent for domains and the models facet axes;
`parents` with `|` for models lineage; `;` or `,` for algorithms). A parent id
that does not resolve is a dangling edge the audit reports.

For the design work itself — how to choose the axes and derive the nodes — read
`data/ontology/design/PROCESS.md` before writing any TSV. The ordering in it is
load-bearing: draft a sibling set with **no corpus access**, freeze it, then
consult the corpus for two questions only.

### 4c. Place the names

Three modes, in increasing order of commitment:

```console
# 1. payload only, no model call, no mutation
uv run categorize --dim models --base v6 --items items_models.jsonl \
    --limit-items 1 --dump-payload

# 2. one item at a time; nothing applied without [a]pply, verdicts to review.jsonl
uv run categorize --dim models --base v6 --items items_models.jsonl --interactive

# 3. batch, writing a new snapshot
uv run categorize --dim models --base v6 --items items_models.jsonl --out v7
```

`--no-apply` decides without mutating (dry run per decision). `--unmapped-only`
and `--surfaces <name> ...` narrow the work. Output lands in
`data/ontology/<dim>/<out>/` with `decisions.jsonl` beside the snapshot.

**Decision point — start with `--dump-payload`.** It is free and it answers the
question that actually decides placement quality: *does the candidate set contain
the right neighbourhood?* Measured against the legacy tree, `Ontology.search`
alone returns nothing at all for **96.4%** of 1208 unmapped model names, so
retrieval — not judgment — is the usual cause of a bad decision.

**Decision point — the categorisation model is pinned separately** from the
extraction model (`[categorize] platform` / `model`). Keep it that way: sharing
them makes the gate number unattributable and silently invalidates it whenever
the extraction backend is swapped.

### 4d. The gate

```console
uv run categorize-eval --dim models --base v6 --split dev
uv run categorize-eval --dim models --base v6 --split gate --probes --adjudicate
```

Leave-one-out and non-accumulating: each item is decided against its own
single-item-ablated copy of the tree. `--probes` runs the reference-free control
sets, `--adjudicate` runs the blind judge over disagreements, `--k` repeats for
self-consistency, `--resume` continues a run already recorded under `--out`.

**The `gate` split is sealed — open it deliberately, once.** Score on `dev` while
iterating. There is no flat accuracy figure by design: the classes nest and are
heavily skewed, so accuracy would mostly measure the prior.

### 4e. Read back what a run did

```console
uv run categorize-report data/ontology/models/v7/decisions.jsonl --base v6
```

`--base` is the version the decisions were taken **against**, not the one the run
wrote; replaying onto the output fails with *already exists* / *unknown node*.

---

## Stage 5 — analysis

```console
uv run evaluate --input <papers.txt>          # extraction accuracy vs data/mdl/merged
uv run python -m paperext.analysis.frequency  # name/mention frequencies
uv run python -m paperext.analysis.workload
```

`evaluate` scores extractions against the human-merged YAMLs using the legacy
milabench category files. `analysis/frequency.py` and `analysis/workload.py` have
`main()` functions but no console-script entry points, so invoke them with
`python -m`. `analysis/rollup.py` is a library (no CLI).

---

## 5. Where the procedure currently stops

Reproduced in this checkout. These are the gaps between "the code runs" and "the
procedure completes", and three of them sit exactly on the join between the two
halves.

### G1 — `categorize-items` has no `algorithms` dimension

`algorithms/v1` is a real ontology (lineage 1672 nodes, plus signal / role /
attributes), and `DIMENSION_FIELDS` has no `algorithms` entry, so no items can be
built for it. The extraction has produced `algorithms[]` since schema v5.
**Corpus algorithm names currently cannot reach their own ontology.** The fix is
one `DIMENSION_FIELDS` entry plus whatever `iter_mentions` needs for that entity
type.

### G2 — the placement agent cannot load a faceted dimension

`categorize` resolves its tree as `Ontology.load(root / dim / base)`, which needs
a flat `ontology.json`. Measured:

| snapshot | `Ontology.load` |
|---|---|
| `models/v0`, `models/v6` | OK (1409 nodes) |
| `models/v1` | OK (1418) — hybrid: flat files *and* facet axes |
| `domains/v0` | OK (1536) |
| `domains/v1`, `data_sources/v1`, `algorithms/v1` | **FileNotFoundError: no `ontology.json`** |

The faceted snapshots load fine **per axis** (`Ontology.load('domains/v1/discipline')`
→ 160 nodes) and as a whole through `Dimension.load`, which is the #100 loader
built for them. But `categorize` does not use `Dimension`. So the current
faceted design — domains v1, data_sources v1, algorithms v1 — is **not reachable
by the agent that places corpus names**. Either the agent learns `Dimension`, or
each axis is categorised against separately.

### G3 — one stale file stops `categorize-items` dead

`load_extractions` raises `ValueError: Could not validate <path> against any
model version` on the first file that fails, with no skip. Measured today:

| bucket | files | validate | fail |
|---|---|---|---|
| `anthropic/claude-opus-5` | 51 | **28** | **23** |
| `openai/gpt-5.6-sol` | 51 | 51 | 0 |
| `openai/legacy-2024` | 2110 | 2110 (1750 as v3, 360 as v4, up-converted) | 0 |

The 23 predate the `repetitions` string→list change. `verify.py` skips such files
with a warning; `load_extractions` does not, so `categorize-items --platform
anthropic --model claude-opus-5` fails outright while the same command on batch 2
returns 368 names. **At corpus scale this matters more, not less**: one stale or
truncated file blocks the whole fold. Either re-extract the stale files or make
the loader skip-and-count like `verify` does.

### G4 — the gate exists for `models` only

`data/ontology/eval/` contains `models/` and nothing else; `splits.json` is there
alone. `categorize-eval --dim <anything else>` has no sealed split to score
against, so a new dimension's agent cannot be gated the way models' was. Splits
are drawn by `categorize/sampling.py` — deliberately hoisted so that prompt
iteration never happens while looking at names that later land in the gate set.
**Draw a dimension's splits before iterating on its prompt, not after.**

### G5 — `models/v4` is a records-only directory

It holds `decisions.jsonl` and `review.jsonl` but no `ontology.json`, so
`--base v4` fails. The usable chain is v3 → v5 → v6. Don't infer the latest
snapshot from the highest version number; check for `ontology.json`.

### G6 — cut files exist for two dimensions

`load_dimension_cut` finds a committed milabench cut for `models` and `domains`;
every other dimension falls back to depth 2. That fallback is a default, not a
decision — if a dimension reports at a different level, the cut has to be
authored.

### G7 — one thing a live call still has to settle

`Explained[list[...]]` produces a valid closed strict schema when checked
locally, but no live API call has exercised it. Schema *shape* has broken at the
API before. The first few papers of a corpus run settle it — look at them.

---

## Decision points, collected

| point | default | when to change it |
|---|---|---|
| backend + structured-output mode | `anthropic` / `claude-opus-5` / `tools` | never casually; a newer model can be blocked in all three modes |
| `--platform` on `query` | `[platform] select` = `openai` | always pass it explicitly |
| `--concurrency` | 4 | raise only after a run shows headroom |
| output ceiling | 48k | raise freely; billing is per actual token |
| new bucket vs re-run | re-runs skip existing files | always a new bucket after a prompt change |
| which dimension first | — | the one whose names dominate the corpus |
| `--dump-payload` → `--interactive` → batch | — | never start at batch on a new dimension |
| `dev` vs `gate` split | `dev` | open `gate` once, deliberately |

## Command inventory

| command | stage |
|---|---|
| `paperoni-report`, `paperoni-enrich`, `download-convert` | 1, corpus |
| `backend-check` | 2, pre-flight |
| `query` | 2, extraction |
| `python -m paperext.structured_output.mdl.verify` | 3, prompt-level checks |
| `python -m paperext.structured_output.mdl.check` | 3, per-record invariants |
| `merge-papers`, `python -m paperext.annotate_pdf`, `python -m paperext.adjudication_report` | reference annotations (see the handoff doc) |
| `categorize-items` | 4a |
| `python -m paperext.ontology.convert_axes` | 4b |
| `python -m paperext.ontology.migrate` | 4b, legacy v0 snapshots only |
| `categorize` | 4c |
| `categorize-eval` | 4d |
| `categorize-report` | 4e |
| `evaluate`, `python -m paperext.analysis.frequency`, `...workload` | 5 |
| `parse-validation-errors` | diagnostics on a query log |
