# Models hierarchy — derivation brief

Task brief handed to the design agent. Authority for every rule here is
`MODELS_BRIEF.md` (the entity model and the settled decisions) and `PROCESS.md`
(the method, reused from the domains design). Read this file as the *task*;
read those two as the *reasons*.

**Scope of this derivation: the `models` hierarchy only.** The `algorithms`
hierarchy is a separate, later derivation. Datasets may need no hierarchy at all
(`MODELS_BRIEF` A.4) and are out of scope.

---

## 1. What the dimension is for

Two purposes, and every structural choice answers to them.

1. **Aggregation at several levels.** The analyses ask *what proportion of
   models were Transformers*, and also *what proportion were BERT*, and also
   *what the BERT variants were*. Those are three different cuts of the same
   corpus, so the tree must carry three real levels. A structure that can only
   answer the first is a failure.
2. **Compute estimation**, Epoch AI style. The model contributes the *kind of
   computation*; scale, precision, parallelism and duration all live on the
   `run` record, never in the tree.

## 2. What is a model here

**Admission rule.** A term enters this hierarchy only if it names a **separable
learned object** — parameters that could be described and run independently of
the procedure that produced them. No separable object (nonparametric), or object
inseparable from procedure, means the term is an **algorithm**, and belongs to
the other hierarchy. A paper may legitimately yield an algorithm and no model.

Worked cases, already settled — treat as fixed points, not as examples to
re-litigate:

| term | model | algorithm |
|---|---|---|
| logistic regression | linear model, logit link | the fitting procedure |
| random forest | decision-tree ensemble | bagging + random subspace |
| XGBoost | gradient-boosted tree ensemble | the boosting procedure |
| k-NN, kernel density | *none* | algorithm only |
| PPO / SAC / DQN | the policy and value networks | the update rule |
| diffusion model | the denoiser, usually a U-Net | the denoising procedure |
| GFlowNet | the flow network | the training objective |
| SimCLR / BYOL / DINO | the encoder the paper names | the SSL objective |

**Artifacts are nodes.** `Transformer › … › BERT › RoBERTa` is the intended
shape. Do not attach recurring artifacts as mere spellings of a family node;
that is the capping proposal the owner rejected on 2026-10-02, because it makes
every cut below Transformer impossible.

## 3. The backbone is lineage

**Settled with the owner, 2026-10-02**, after three candidate level-1
characteristics were rejected.

Rejected, and why — the three failures are one failure. Each divides a model by
something that is not a property of the model:

| rejected candidate | it is actually a property of |
|---|---|
| computational primitive | a **layer**. Models mix primitives layer by layer; representing one by a single primitive is not useful. |
| data structure consumed | the **application**. The same Transformer runs on text sequences or image patches. |
| function learned | the **use**. The same architecture discriminates in BERT and generates in GPT. |

What is invariant to a model under modality, task and layer-mix is **what it was
built from**. So the hierarchy is **architectural lineage**: parent → child means
*the child was derived from the parent*.

```
Transformer
├── Encoder-only ──── BERT ──── RoBERTa, DistilBERT, CodeBERT, ALBERT…
├── Decoder-only ──── GPT ───── GPT-2, GPT-3, GPT-4
│                 └── LLaMA ─── LLaMA 2, Vicuna, Alpaca
└── Encoder-decoder ─ T5, BART
```

**Composition recipes were considered and are out of scope.** Describing each
model by the primitives it composes would be ideal for compute estimation, but
the owner judged it unrealistic to extract. **We classify names.**

### 3.1 It is a DAG, and that is fine

A model may have more than one parent. Aggregation in this project is already
**non-exclusive** — locked in E1 (#16): a paper maps to a *set* of
categories-at-cut, bucket count is the number of papers whose set contains the
bucket, and columns overlap by design. So "proportion of papers using a CNN" and
"proportion using a Transformer" may both count a Conformer paper, exactly as a
paper already counts under several research domains.

Do not invent a primary lineage, and do not drop an edge to keep a tree.

*(Known code consequence, not the agent's problem: `analysis/rollup.py` returns
`dict[str, str]`, one category per name, and will need `dict[str, set[str]]`.)*

---

## 4. The lineage rules

These are the rules that make the derivation checkable. Apply them literally.
Where a case resists them, do not improvise — put it in `BOUNDARY_CASES.tsv`
with the reading you chose and the reading you rejected.

### R1 — What makes an edge

> **A is a child of B when A cannot be described without naming B.**

Operationally: **the introducing paper's own framing** — its title, abstract or
method section defines A relative to B. If you have to reconstruct the
relationship yourself from architectural similarity, it is not an R1 edge; it is
R2 influence. When the framing is genuinely ambiguous, that is a
`BOUNDARY_CASES.tsv` row, not a judgement call to make silently.

| case | edge | why |
|---|---|---|
| RoBERTa → BERT | ✓ | "BERT with improved pretraining" |
| ViT → Transformer | ✓ | "a Transformer applied to image patches" |
| ResNet → convolutional network | ✓ | "a CNN with residual connections" |
| GPT-2 → GPT | ✓ | the same architecture, next generation |
| BERT → GPT | ✗ | siblings; neither is defined from the other |

### R2 — What is never an edge

Influence, citation, shared authors, shared modality, shared task, shared
primitive, or appearing in the same benchmark table. **Two models that both use
attention are unrelated** unless one was built from the other. This rule exists
because "inspired by" would make the DAG complete and meaningless.

### R3 — When a name is a spelling, not a node

Three cases collapse into an existing node:

1. **Orthographic variants** — `resnet-50` / `resnet50` / `ResNet 50`.
2. **Acronym and long form** — `vision transformer (vit)` / `vit`.
3. **Size variants of one release** — `llama2-7b` / `llama2-13b` / `llama2-70b`
   are spellings of `LLaMA 2`.

The rule that separates case 3 from a real child:

> **A variant that differs from its parent only in size is a spelling.
> A variant that differs in architecture, training data, or training objective
> is a node.**

| name | verdict | why |
|---|---|---|
| ResNet-18 / ResNet-50 / ResNet-101 | spellings of `ResNet` | depth is size; `runs[].parameter_count` carries it |
| LLaMA-2-7B / -70B | spellings of `LLaMA 2` | size only |
| DistilBERT | **node** | distillation is a different training objective |
| CodeBERT | **node** | different training data |
| Vicuna | **node** | instruction-finetuned on different data |
| GPT-3 → GPT-4 | **node** | a different architecture generation, not a size setting |

Nothing is lost by case 3: scale lives on the run, where the brief has always
put it, and where compute estimation reads it.

### R4 — When an intermediate node is legitimate

Admit a node N between P and its children when **all three** hold:

1. **The field names the distinction.** You are not inventing a layer.
2. **N has at least two substantive children.** One child means N is a rename
   of that child.
3. **N is definable without listing its children.**

`Encoder-only` / `Decoder-only` / `Encoder-decoder` under Transformer passes all
three. An intermediate invented only to reduce a large branching factor fails
rule 1 — **that is balancing by size, which is forbidden** here as it is in the
domains design.

### R5 — Second parents

Add a second edge under R1's test applied again: the model cannot be described
without naming that parent either. Two shapes, both legal, distinguished in
`notes`:

- **Hybrid** — one block mixes what two lineages contributed. `Conformer` →
  {Transformer, convolutional network}.
- **Composite** — two named sub-models combined. `CLIP` → {its image encoder,
  its text encoder}.

### R6 — Lineage roots

A root is an architecture **whose defining idea is not a modification of another
architecture in this tree**. Expect roots to be historically contingent rather
than a clean partition of a characteristic — that is a declared property of a
lineage backbone, not a defect to engineer away. Say so in `RATIONALE.md`.

The principle-of-division machinery from `PROCESS.md` still governs **within** a
family — how BERT's children are grouped is a division question — but it does
**not** govern the root set.

**Sanity bound on the root set: expect roughly 8 to 15.** Far more than that
means releases have been promoted to roots because their lineage was not
traced; far fewer means distinct founding ideas have been fused. This is a
smell test, not a target, and it is **never** a reason to merge or split a root
you otherwise believe in — balancing by count is forbidden.

### 4.7 Worked end to end

Fifteen real names from the corpus, classified with the rule that decides each.
Match this pattern; where your case does not match it, write the boundary row.

| name | verdict | rule |
|---|---|---|
| `transformer` | root | R6 |
| `bert` | node under `Encoder-only` | R1, parent via R4 |
| `roberta` | node under `bert` | R1 — "a robustly optimized BERT pretraining" |
| `distilbert` | node under `bert` | R1 + R3 — distillation is a training objective, so a node, not a size variant |
| `codebert` | node under `bert` | R1 + R3 — different training data |
| `resnet-50` | **spelling** of `resnet` | R3 case 3 — depth is size |
| `resnet` | node under `Convolutional network` | R1 — "a CNN with residual connections" |
| `llama2-7b` | **spelling** of `llama 2` | R3 case 3 |
| `vicuna` | node under `llama` | R1 + R3 — instruction-tuned on different data |
| `vision transformer (vit)` | node under `transformer`; `vit` is its acronym spelling | R1 + R3 case 2 |
| `conformer` | node, parents `transformer` **and** `convolutional network` | R5 hybrid |
| `clip` | node, parents = its image and text encoders | R5 composite |
| `u-net` | node under `Convolutional network` | R1 |
| `neural networks` | **not a node** — uninformative generic | §2; quarantine as the domains design did with `machine learning` |
| `dovesei` | not your problem | §8 — one-paper tail, grown by the second pass |

**On the last two rows.** Bare generics (`neural networks`, `deep neural
networks`, `transformers` as a plural mass noun) are quarantined, reported as a
line, and excluded from family shares — the same treatment `machine learning`
and `deep learning` got in the domains design. And you are deriving the upper
and family levels only: a name appearing in one paper is placed later, by
categorization, against the structure you build.

---

## 5. Method

Follow `PROCESS.md` §2. The rules that bind hardest:

1. **One principle of division per sibling set**, stated as the node's
   `characteristic`, **wherever a sibling set is produced by division rather
   than by descent** (see R6).
2. **A child sibling set must refine its parent's characteristic**, never import
   another aspect's.
3. **Two-phase protocol.** Phase 1: draft from the field's own structure with
   **no corpus access whatsoever**, and freeze it in `DRAFT_PHASE1.md` before
   opening any data file. Phase 2: consult `model_names.tsv` for **two questions
   only** — which blind spots must be added, and which drafted nodes look
   speculative. The corpus **bounds scope and exposes blind spots; it never
   arbitrates**. Deliver both versions and explain every change between them.
4. **Volume decides which node to open next; it plays no part in how it opens.**
5. **A property attaches at the highest node where it holds for all descendants.**
6. **External classifications supply vocabulary and breadth, never arbitration.**
   ACM CCS `Computing methodologies`, arXiv categories and Papers With Code are
   fair input. None of them is a referee.

## 6. Forbidden inputs

Reading any of these invalidates the derivation:

- **`data/ontology/models/v0`** in any form. It is not a reference for a good
  hierarchy — it is 1409 nodes of which 1136 are leaves, with roots that do not
  partition and a normalization file that is almost entirely identity seeds.
- **`data/ontology/design/axes/`** — the domains axes, including
  `Method › Model design`. The whole point of step B.6 is to compare this
  derivation against that subtree *afterwards*; seeing it first destroys the
  comparison.
- `proposed_categories.csv`, `categorized_models.json`, and anything under
  `data/ontology/design/run{1,2,3}/` or `axes/superseded/`.

## 7. Deliverables

In `data/ontology/design/models_tree/`:

1. `DRAFT_PHASE1.md` — the corpus-free draft, frozen and timestamped **before**
   any data file is opened.
2. `nodes.tsv` — columns `node_id, name, parents, depth, relation,
   characteristic, positive_test, negative_test, examples, notes`.
   `parents` is **pipe-separated** — a node may have more than one (R5).
   `relation` is `descent` or `division`, naming which rule produced the node's
   place (R1 or R4). `depth` is the **shortest** path to a root.
   **No count columns**: they leak into any later phase-1 work.
3. `SPELLINGS.tsv` — columns `spelling, node_id, case`, where `case` is
   `orthographic`, `acronym` or `size` (R3). Every name you collapse goes here,
   so the decision is reviewable rather than invisible.
4. `RATIONALE.md` — the principle of division at every branch, every change
   between phase 1 and phase 2 with its reason, and the boundary cases you
   declare (same shape as `BOUNDARY_CASES.tsv`).
5. `SELF_AUDIT.md` — run the granularity audit on your own output, and name the
   sibling sets you are **not** confident in. Under-confidence declared is worth
   more than confidence asserted.

## 8. Depth

Design the **upper and family levels** — roughly depth 3 to 4. The second pass
grows the rest from the corpus.

The risk this carries is specific and must be managed: the family level has to
be tight enough that on-the-fly categorization is **never asked to invent an
intermediate level**. That is exactly how v0 ended up with 95 flat leaves and a
lone `bert` family sitting among them as a sibling. Wherever you can foresee a
family becoming wide — BERT is the known case — say so in `SELF_AUDIT.md`, and
it will get a second, deeper designed pass.
