# #103: how to run the verification, and how to read it

Everything here is ready except the extraction itself, which needs the owner's
credentials. `config.mdl.ini`'s `[env]` keys are blank placeholders on purpose —
supply them at runtime, do not commit them.

## 1. The run

The sample lives at `sample.paperoni.json` — **25 papers, two tiers**, every one
with a cached fulltext under `cache/fulltext/<paper_id>/` in the
`paperext-llm-backend` checkout:

- **11 core papers**, chosen by greedy set cover so each acceptance case is
  exercised **at least 3×**. Selection was over **fulltext content**, not over
  the legacy prompt's slotting, because the three region checks had to be
  chosen by what the papers actually say — the legacy prompt returned zero for
  all three, so its output cannot select for them.
- **14 random papers**, seed 103, from the same fulltext pool. #103 §3's
  over-splitting checks are a *distribution*, and 11 papers cannot carry one.

```console
PAPEREXT_DIR_CACHE=/home/bouthilx/projects/paperext-llm-backend/data/cache \
uv run python -m paperext.query --platform anthropic \
    --paperoni data/ontology/design/c0_verification/sample.paperoni.json
```

**`PAPEREXT_DIR_CACHE` is required, and this was a real mistake in the first
version of this runbook.** The sample's converted fulltexts are cached only in
the `paperext-llm-backend` checkout, which is where the sample was *built*
from. `Paper._pdfs` globs `CFG.dir.cache`, which in this repo is `data/cache` --
a directory that does not exist. Every paper then resolved to `None`, the
`is not None` filter emptied the list, and the run queried nothing. Only the
cache moves: output still lands here, under `data/mdl/queries/`.

Verify the resolution before spending anything:

```console
PAPEREXT_DIR_CACHE=/home/bouthilx/projects/paperext-llm-backend/data/cache \
uv run python -c "
import json; from pathlib import Path; from paperext.utils import Paper
raw = json.loads(Path('data/ontology/design/c0_verification/sample.paperoni.json').read_text())
got = [Paper(p).get_link_id_pdf() for p in raw]
print(f'{sum(g is not None for g in got)}/{len(got)} papers resolve')"
```

Expected: `25/25`. `query.py` now refuses an empty list rather than succeeding
at nothing, but checking first costs a second.

`--platform` is the owner's call; the harness reads whatever lands in the
queries directory and does not care which provider produced it.

## 2. The reading

The run writes to a **configured** path, not the working directory.
`config.mdl.ini` sets `queries = ${data}/${platform:struct}/queries` and
`root = .` resolves relative to *the config file*, so it is always
`<repo>/data/mdl/queries/`, then bucketed per provider and model slug by
`paths.platform_bucket`:

| `--platform` | queries dir |
|---|---|
| `anthropic` | `data/mdl/queries/anthropic/claude-opus-5` |
| `openai` | `data/mdl/queries/openai/gpt-5.6-sol` |
| `local` | `data/mdl/queries/local/Qwen-Qwen3.8-Flash-Next-FP8` |

The model half comes from that backend's own config section, **not** from the
flag, so changing `[anthropic] model` changes the directory with it. Two traps:
`[platform] select` is `openai`, so omitting `--platform` writes to the openai
bucket; and this repo's `data/mdl/queries` is nearly empty, because the 2110
legacy-2024 extractions live in the `paperext-llm-backend` checkout — which is
why `BASELINE.md`'s command points there and this one does not.

```console
uv run python -m paperext.structured_output.mdl.verify \
    data/mdl/queries/anthropic/claude-opus-5
```

Three kinds of result, and the distinction is the whole point:

- **CHECK** — pass/fail. A failure is a **prompt defect**. Four are marked HARD
  in the output's reading line.
- **PROBE** — must be non-zero. Zero means the widened scope never reached the
  prompt.
- **MEASURE** — a number with no pass condition, because the risk being sized
  has no correct value.

Compare against `BASELINE.md`, which is the same instrument over legacy-2024.
**A v5 failure that also appears there is inherited; one that appears only in v5
is new.** Nothing else can be read off the comparison — legacy-2024 came from a
different prompt against a schema with no `runs[]`.

## 3. What would make this fail its own purpose

Straight from #103 §5, because it is the trap this whole pass can walk into:

> **Do not fix a disappointing result by narrowing the prompt's vocabulary.**
> If a region comes back empty, the finding is about the prompt's **scope
> statement**, not its vocabulary.

The probe sets exist to *detect* the three regions. Handing them to the
extractor as a closed list would make #99 circular — it would find only what we
listed, and the revision would rubber-stamp the design.

## 4. Two things only a live call can settle

- **`Explained[list[Parallelism]]`** is the first generic in this schema with a
  list argument. It produces a valid closed strict schema — checked against
  `backends.anthropic.strict_schema` — but **no live API call has exercised
  it**, and schema *shape* has broken at the API before, on a class name.
- The **ontology-role half** of the `execution_mode` invariant (no algorithm
  whose role is `R.fit.update` in an inference run) is not in `check.py`. It is
  mechanisable now that #100 is loadable, and is worth adding once there is
  output to run it against — writing it blind would be guessing at the shape of
  the failure.

## 5. After the run

| result | where it goes |
|---|---|
| a CHECK fails | fix the prompt, re-run the 11-paper core only |
| a PROBE is zero | #103 §5 governs: the scope statement, not the vocabulary |
| a MEASURE looks wrong | #103 §3 — read `runs` per paper against the papers |
| the ontology looks wrong | **#99**, not here. That is the whole reason #103 exists |

The last row is the point of the issue: #99 revises the ontology against the
extraction, so an extraction that failed for a prompt reason would send #99
chasing a defect that is not in the ontology.
