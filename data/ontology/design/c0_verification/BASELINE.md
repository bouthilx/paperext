# The legacy-2024 baseline, and why it is the harness's own test

`verify.py` runs every mechanisable check #103 and #102 specify. A harness whose
checks cannot fail is worse than no harness, so before trusting it on new
output it was run against **legacy-2024** — the corpus where the first checks
are *known* to fail, because that is where the misroutings were measured.

```console
uv run python -m paperext.structured_output.mdl.verify \
    .../data/mdl/queries/openai/legacy-2024
```

**2110 extraction files. 10 of 15 pass/fail checks failed, and every failure is
one the record predicted.**

| check | legacy-2024 | predicted by |
|---|---|---|
| `adam` in `libraries[]` | **27 papers** (0 in `algorithms[]`) | #99: *"`adam`/`adamw` landing in `libraries[]` is that bias caught in the act"* |
| `adamw` in `libraries[]` | **8 papers** (0 in `algorithms[]`) | same |
| `pytorch` in `models[]` | **3 papers** (444 correctly in `libraries[]`) | #103 §1 |
| `mujoco` in `data_sources[]` | **12 papers** (9 in `libraries[]`) | #102 Part A, the library clause |
| an evaluation protocol as a source | `atari 100k` 4 · `atari 57` 2 · `urlb` 3 · `helm` 1 | #102 Part A, the protocol clause |
| an unnamed description as a source | **13 papers** | #102 Part A |
| decoding non-zero | **0 of 98 probe nodes** | #99: *"decoding and evaluation have zero hits"* |
| evaluation non-zero | **0 of 38 probe nodes** | same |
| preprocessing non-zero | **0 of 255 probe nodes** | #99's measured 6% against 14% of the ontology |
| `check.py: executed-without-run` | 2541 | #103 §2: *"expect this in bulk on anything converted"* |

The two that passed are the two that *could not* fail here: there are no
`generate` runs in v4 output, and `runs[]` is empty by construction after
`convert_model_v4`, so every run-level measurement reads 0/0. That is the
correct behaviour, not coverage.

**`mujoco` is the sharpest row.** 12 papers put the engine in `data_sources[]`
against 9 in `libraries[]` — so on the legacy prompt the *wrong* slot was the
more popular one. That is the clause earning its place, measured rather than
argued.

## What this baseline is for

Two things, and only these:

1. **It proves each check fires.** Paired with `test_verify.py`, which exercises
   every check in both directions on synthetic input, the harness is known to
   detect what it claims to.
2. **It is the before-picture.** When the v5 run lands, the same command over
   the new output is directly comparable, because it is the same instrument.

**What it is not:** evidence about v5. Legacy-2024 was produced by a different
prompt against a schema with no `runs[]`, no `algorithms[]` and a `datasets[]`
slot that predates the admission rule. A v5 failure that also appears here is
*inherited*; one that appears only in v5 is *new*. Nothing else can be read off
the comparison.

## The three region probes, read carefully

Zero is the expected legacy result and it is **not** the finding. The finding
will be whether the v5 run moves them off zero. If it does not, #103 §5 governs:

> If a region comes back empty, the finding is about the prompt's **scope
> statement**, not its vocabulary.

Handing the extractor a closed list would make #99 circular — it would find
only what we listed and the revision would rubber-stamp the design. The probe
sets exist to *detect* the regions, never to be given to the extractor.
