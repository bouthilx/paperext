# D1 · Refresh category mappings — plan

D1 "Refresh category mappings" (#15) is an **umbrella**. It is large, tedious manual
curation, so the strategy is **LLM does the bulk categorization; humans validate, not
author**.

## Locked layered model (governs all sub-issues)

```
raw name → normalization (surface→canonical id) → ontology (id→hierarchy) → roll-up to cut → category
```

- Splits surface-variant folding (**normalization DB**, flat JSONL, many-to-one) from the
  concept hierarchy (**ontology**, id-keyed nodes). Fixes duplicate/self-nesting nodes and
  stops deletes from orphaning papers (papers attach via stable ids, not tree positions).
- **Identity = long-form/common-name + acronym(s) + description.** Two entities sharing an
  acronym → distinct ontology nodes; matching on identity, never bare string. Normalization
  is strictly **1:1 (no candidate-sets)** — ambiguous bare acronyms left **unmapped**
  (shown in fragmentation report), never guessed. Gate on **ambiguity, not acronym shape**
  (keep unambiguous proper-name acronyms: NumPy/GPT-2/SimCLR/BERT).
- **Granularity policy (locked):** distinct *model* variants — versions/sizes/qualifiers
  (v2, v3, Large, -50, -B-16, -S-101) — are **nodes** nested under a common parent
  (`MobileNet › MobileNetV3 › MobileNetV3 Large`); only *name-spelling* variants
  (`mobilenet-v2`, `MobileNet v2`) are **normalization surfaces**. Ontology stays
  fine-grained; normalization absorbs spelling only. Alias-breadth caveat: an extracted
  alias may name a broader family than the entity — don't absorb it as a surface if it
  already resolves to a different/broader node. Agent fixes dirty nodes **in-flight**.
- Ontology on-disk: `data/ontology/<dim>/v<N>/{ontology.json, normalization.jsonl}`;
  nodes carry `name`/`description`/`examples`/`children` + `roots`. On-disk = diffable;
  in-memory = indexed once (O(1) descent; parents index derived). DAG-ready (id under
  multiple parents) but **single-primary first**; DAG (`name→set` roll-up) is a fast-follow.
- **Versioned per full run** (never overwrite); `v0` = faithful legacy import, curated runs
  → v1, v2. Code package: `src/paperext/ontology/`.

## Sub-issues (each own PR to main)

### D1a (#36) — data model foundation, scoped as the **mutable ontology object**
- format + loader/index/accessors + **mutation API + invariants**
  (create_node/add_surface/move/rename/insert_above/demote_to_variant/remove_node/
  remove_surface/mark_ignore; enforce id-uniqueness/referential-integrity/acyclicity)
- `v0` faithful migration (only safe demotions; concept-vs-variant deferred to D1b)
- roll-up converter keeping E1 unchanged.
- Loader must offer a **global multi-hit fuzzy surface search** + accessors
  (ancestry/children/surfaces/examples/root-map/node→surfaces).
- `v<N>/` layout has an optional `decisions.jsonl` audit slot.
- **Acceptance: v0 reproduces current `build_category_map` exactly** (depths 1/2/3 +
  milabench cut) + mutation/invariant unit tests. No categorization.

### D1b — LLM categorization agent (consumes D1a primitives)
Per-entity decision with a designed **prompt payload** = policy + ITEM/grounding (quote,
justification, primary/sub fields, **co-occurring models annotated with current_category**,
is_executed) + CANDIDATES (global multi-hit, each with path/children/surfaces/examples) +
ROOT MAP + action-schema; output = ordered `Action` list (op/args/justification/confidence)
+ unresolved/review_notes, applied via D1a mutation ops. A decision is often
**multi-action incl. in-flight fixes** (rename acronym-in-name, move misplaced node);
low-confidence structural fixes flagged. Descriptions **bootstrap** (v0 has none → infer
from children/siblings/examples). Plus the **held-out re-mapping eval** (branch/cut-level
accuracy vs hand-built trees). Decision gate before rollout. Full worked prompt example
built for BiT-S-101 (paper 2306.03522).

### D1c models; D1d datasets + libraries; D1e research-fields
- D1c models; D1d datasets (wire existing tree) + libraries (**new tree from scratch**);
  D1e research-fields. Each = run agent + cleanup pass + reconcile that dimension's
  milabench cut.

## Scope now vs later
Built/validated against the **2024 openai corpus now**; 2023–2026 vocab is a re-run after
C1 (new extraction). Extraction improvement for C1: prefer full name as `name`, acronym in
aliases, verify all aliases resolve to same canonical.

## Evidence (2024 corpus, 1999 papers)
Unmapped distinct names ~models 1128 / datasets 2051 / research-fields 1003 (52–82%);
libraries 738 with **no tree**. Every name matters (hierarchical ancestor counting —
singletons still bump ancestor counts). Multi-branch ambiguity today: 10 models (acronym
collisions like `sam`, hybrids like `hubert`/`mcan`), 12 domains (self-nesting), 0 datasets.

## Reuse assets
`ontology_mapping/` (user's semi-manual builders — Levenshtein candidates, grounding,
tree-edit ops), `ai4hcat/` (LLM-categorization precedent, instructor).
