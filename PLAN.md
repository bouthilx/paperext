# PLAN — Literature-Review Refresh for the Milabench Follow-up

## 1. Context & motivation

This work is the **literature-review half** of a follow-up to the 2024 Milabench
paper ([arXiv:2411.11940](https://arxiv.org/abs/2411.11940), *"Introducing
Milabench: Benchmarking Accelerators for AI"*). That paper grounded its
selection of benchmark workloads in a literature review of **867 Mila papers**
plus community surveys, yielding 26 primary + 16 optional workloads.

We are renewing that analysis on a fresh **2023–2026** corpus to refresh the
selection of workloads and feed a new Milabench release and report. The
downstream workload-building and the new Milabench release are **out of scope
here** — this plan covers only:

1. Refreshing the extraction **pipeline** (paperoni + LLM extraction of models,
   datasets, libraries, research fields), and
2. The **analysis** of those extraction results (frequencies, 2023–2026 trends,
   comparison vs 2024) that will inform workload selection.

### Explicitly out of scope
- Building/selecting the actual new Milabench workloads.
- The community survey component of the original study.
- Perf/procurement analysis.

## 2. Pipeline recap (current state)

| Step | Entry point | Output |
|------|-------------|--------|
| Fetch paper metadata | `paperoni-report` (`paperoni/report.py`) — curl to paperoni server, `validation=validated&peer-reviewed=True`, date-ranged | `data/.../paperoni-*.json` |
| Download + convert | `download-convert` | PDF → `.txt` |
| LLM extraction | `query` (`query.py`) — `instructor` + OpenAI/VertexAI, schema `structured_output/mdl/model_v3.py` | per-paper JSON in `data/mdl/queries/{platform}/` |
| Merge attempts | `merge-papers` | human-validated `data/mdl/merged/*.yaml` (ground truth) |
| Quality evaluation | `evaluate` (`evaluate.py`) — confusion / multi-label confusion matrices | `data/mdl/evaluation/{platform}/*.csv` |
| Aggregate stats (legacy) | `stats_spaghetti.py` (untracked, 1825 lines) | ad-hoc plots/counts |

Key fact: `evaluate.py` measures **extraction accuracy** vs annotations. The
**aggregate frequency/trend analysis that actually drives workload selection**
lives only as spaghetti in `stats_spaghetti.py` and must be reimplemented
cleanly.

## 3. Decisions locked in (from planning interview)

- **Corpus**: fresh full pull of Mila papers, **2023–2026**, keeping the existing
  paperoni filter (`validation=validated`, `peer-reviewed=True`). Re-extract
  everything with the new pipeline.
- **Compute / cost**: use Mila's **free GCP credits via VertexAI** as the LLM
  host.
- **Backend model**: **bake-off** — run **Claude-via-VertexAI** (AnthropicVertex)
  vs **Gemini-via-VertexAI** on the reused 2024 validation set and pick the
  winner by `evaluate.py` precision. (Rationale: free GCP credits, but higher
  trust in Claude than Gemini — Vertex can serve both.)
- **Elicitation / instructor**: **keep `instructor` with JSON tool-use; no XML.**
  The rigorous evidence ([*Let Me Speak Freely?*, EMNLP 2024](https://aclanthology.org/2024.emnlp-industry.91/))
  shows the format penalty (a) mostly hits *reasoning* tasks, not *extraction*,
  (b) is largely closed on recent closed models like Claude/Gemini, and (c) is
  driven not by JSON-vs-XML syntax but by **answer-before-reason field ordering**.
  XML would also cost materially more tokens (against the free-credit budget) for
  an unproven gain. So we stay on instructor/JSON and instead apply the ordering
  fix directly (next bullet).
- **`Explained[T]` field ordering**: **reorder to reason-first**
  (`quote` → `justification` → `value`) and just ship it — believed better
  (evidence before answer, per *Let Me Speak Freely?*), cheap
  (declaration-order-only change, no downstream impact), so **no A/B measurement**.
  Applied uniformly in v4 (below), so both bake-off models use the identical
  implementation.
- **Schema**: go to **v4** = v3 + the reason-first reorder + cleanup + two
  *additive* model fields:
  - **`execution_mode`** — single enum `train` / `finetune` / `inference` /
    `unknown`, **in addition to** `is_executed`, with **precedence** (training and
    finetuning always imply inference afterward): `train` if the model was trained,
    else `finetune` if finetuned, else `inference` **only when used for inference
    only**, else `unknown`. `is_executed` stays "did *this paper* run it";
    `execution_mode` captures the mode even when the model was only *referenced*
    with results (`is_executed=False`) — workload-relevant.
  - **`parameter_count`** — best-effort model scale with an explicit **`unknown`**
    option. The LLM must report only what the paper *states* (grounded by the
    `quote`) and **never infer from the model name** — an inferred value is noise.
  Additive over v3, so the stored 2024 extractions (already v3) up-convert
  losslessly via a trivial `v3→v4` converter (new fields default to `unknown`).
  Cleanup: delete dead `DatasetSubset` and the stale `caracteristics` references
  in the `__lt__` methods.
- **Validation**: **reuse the 2024 validation set** (`validated.txt` /
  `data/mdl/merged/*.yaml`) as ground truth; re-run `evaluate.py` with the new
  backend rather than re-annotating.
- **Analysis code**: **reimplement cleanly**, using `stats_spaghetti.py` only as
  inspiration (do not build on it). **Refresh the category mappings**
  (`data/categorized_*.json`, milabench categories) for new models/datasets.
- **Ranking metric**: **count all mentions equally** (simple per-paper
  frequency); role fields are still extracted and kept, but the headline ranking
  is raw frequency.
- **2024 comparison baseline**: **full clean re-extraction** — re-run the entire
  2024 corpus through the *final* pipeline (same backend, schema, categories) and
  compare against the new corpus extracted identically. This removes the
  extractor/schema confound so any distribution shift is a real temporal signal.
  The stored 2024 `openai` extractions become a cross-check, not the baseline.

### Deliverables of this phase
1. **Analysis report** — frequency tables/figures for models, datasets,
   libraries, research fields.
2. **Time-trend analysis** — evolution across 2023–2026 (now that we have
   multi-year data).
3. **2024 comparison** — distribution shift vs the **re-extracted** 2024 corpus
   (stored `openai` stats as a secondary cross-check).
4. **Reproducible pipeline** — a clean, documented, re-runnable
   paperoni → VertexAI → analysis flow.

## 4. Pending (settled by empirical result, not a decision)

- **Backend winner** — Claude-via-Vertex vs Gemini-via-Vertex is decided by the
  WS-B bake-off on the 2024 validation set, not by a prior choice.

All design decisions are otherwise locked in §3.

## 5. Workstreams & tasks

### WS-A — Pipeline plumbing (the original 3 lines)
- [ ] **Adapt to new paperoni API.** paperoni is pinned to
      `deploy-2024-12-06`; investigate the current server API/endpoint & params,
      update `paperoni/report.py` (and the pin) to fetch the 2023–2026 corpus.
- [ ] **Set up VertexAI** with Mila GCP credits (project/auth config in
      `config.mdl.ini` → `CFG.vertexai`).
- [ ] Add a **Claude-via-VertexAI** client path
      (`instructor.from_anthropic(AnthropicVertex(...))`) alongside the existing
      Gemini path (`instructor.from_vertexai(GenerativeModel(...))`) in `query.py`.
      Keep instructor (JSON tool-use) for both providers.
- [ ] Clean up the hacky vertexai wrapper in `query.py` (system-role rewriting,
      non-serializable usage metadata) — instructor stays, so this is tidy-up, not
      a rewrite.
- [ ] **Build `model_v4.py`** (copy v3; point `model.py` proxy at it):
      - Reorder `Explained` to reason-first (`quote` → `justification` → `value`).
      - Add `RefModel.execution_mode: Explained[ExecutionMode]` — single enum
        `train`/`finetune`/`inference`/`unknown`, kept alongside `is_executed`;
        prompt encodes precedence train > finetune > inference (`inference` only if
        used for inference ONLY, since train/finetune imply later inference).
      - Add `RefModel.parameter_count: Explained[str]` — description must force
        `unknown` when the paper doesn't state it and forbid inferring from the
        name; the `quote` is the grounding.
      - Delete dead `DatasetSubset` and stale `caracteristics` refs.
      - Update the extraction prompt (`FIRST_MESSAGE`/system) to mention mode and
        the "don't guess scale" rule.
- [ ] Add a **`v3→v4` converter** in `convert.py` (copy all fields; default
      `execution_mode` and `parameter_count` to `unknown`) so the stored 2024
      `openai` extractions validate as v4 for the cross-check.

### WS-B — Backend bake-off & validation
Single variable: the model. Both arms use the **identical implementation**
(instructor + JSON tool-use, reason-first `Explained` ordering, same schema
version) and score on the **reused 2024 validation set** via `evaluate.py`
(precision/recall on models, datasets, libraries, research fields).
- [ ] Run **Claude-via-Vertex** vs **Gemini-via-Vertex**.
- [ ] Run `evaluate.py` for both; compare precision/recall per dimension, plus
      token cost.
- [ ] **Pick the backend**; record the decision and the numbers.

### WS-C — Corpus extraction at scale
- [ ] Fresh paperoni pull 2023–2026 (validated + peer-reviewed).
- [ ] `download-convert` the corpus; track download/convert failures.
- [ ] Run `query` extraction across the corpus on the chosen backend; monitor
      cost against GCP credits.
- [ ] Sanity-check coverage vs the paper list; log gaps.
- [ ] **Re-extract the 2024 corpus with the final pipeline** for the clean
      comparison baseline: re-`download-convert` the old corpus from the stored
      paperoni lists (`data/paperoni-2022-01-01-2025-01-01-*.json`) — the
      converted texts are no longer on disk — then `query` under the same
      backend/schema/categories as the new corpus.

### WS-D — Category refresh
- [ ] Refresh name→category mappings (`data/categorized_models.json`,
      `categorized_datasets.json`, `categorized_domains.json`) to canonicalize new
      models/datasets and cover the 2023–2026 vocabulary.
- [ ] Reconcile with milabench category tags used in `data/mdl/evaluation/`.

### WS-E — Analysis & report (clean reimplementation)
- [ ] New analysis module (inspired by, not built on, `stats_spaghetti.py`):
      per-paper frequency counts for models / datasets / libraries / research
      fields, using refreshed categories for canonicalization.
- [ ] **Time-trend analysis** across 2023–2026 (per-year breakdowns).
- [ ] *(secondary view)* **Workload characterization** using `is_executed` +
      `execution_mode` (train/finetune/inference) and dataset/library `role` —
      e.g. split the model ranking by "actually executed in-paper" vs referenced,
      and by mode. Not the headline ranking (that stays raw frequency), but the
      signal most relevant to picking real GPU workloads.
- [ ] **2024 comparison** — new corpus vs the **re-extracted** 2024 corpus (both
      final pipeline) for a clean distribution shift; use the stored 2024 `openai`
      extractions as a cross-check on how much the extractor/schema alone moved
      rankings.
- [ ] Produce report tables/figures for the four dimensions.
- [ ] Write up findings feeding workload selection.

## 6. Risks & considerations
- **Cost blow-up** — full re-extraction now covers *two* corpora (new 2023–2026
  + the re-extracted 2024 baseline). Validate cost per paper on the sample before
  scaling; watch GCP credit burn.
- **Old-corpus re-download** — the 2024 comparison depends on re-`download-convert`
  succeeding on the stored paper lists; some old URLs may no longer resolve. Log
  and quantify any drop-out vs the original paper count.
- **paperoni API drift** — the new API may change fields/auth; treat WS-A as a
  spike before committing the corpus pull.
- **Comparison confound** — mostly mitigated: the primary 2024 comparison
  re-extracts the old corpus with the *final* pipeline, so backend/schema changes
  can't masquerade as trends. Residual risk applies only to the stored-`openai`
  cross-check (different extractor); treat that as directional and document it.
- **Name fragmentation** — trend/frequency quality hinges on category refresh
  (WS-D); under-invest here and rankings fragment (ResNet-50 vs resnet50 …).
