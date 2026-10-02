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

## 3. What the tree must not carry

- **Not compute patterns.** Compute is a property of a run
  (model × execution mode × parallelism × scale).
- **Not scale.** `MLP` spans orders of magnitude and that is fine.
  **Scale variance is not evidence of bad granularity** — an architecture may be
  well defined *and* scalable across orders of magnitude. A Transformer is one
  architecture from 100M to 1T parameters.
- **Not genealogy as the backbone.** `derives-from` is a DAG; `is-a-kind-of` is
  what aggregates. If a node seems to need two parents, suspect a fused second
  characteristic — ViT is *a transformer* (kind) applied to *images* (modality,
  which is a different dimension's business).
- **Not another dimension's characteristic.** Modality, task and research topic
  each have their own ontology. Importing one here is the error that produced
  v0's unprincipled roots.

## 4. Method

Follow `PROCESS.md` §2 in full. The rules that bind hardest:

1. **One principle of division per sibling set**, stated as the node's
   `characteristic`. Not one per level — different parents may divide by
   different characteristics and the tree is still coherent.
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
   fair input for breadth and blind spots. None of them is a referee.

## 5. Forbidden inputs

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

## 6. Deliverables

In `data/ontology/design/models_tree/`:

1. `DRAFT_PHASE1.md` — the corpus-free draft, frozen and timestamped **before**
   any data file is opened.
2. `nodes.tsv` — columns `node_id, name, parent_id, depth, characteristic,
   positive_test, negative_test, examples, notes`. Same shape as the domains
   axes. **No count columns**: they leak into any later phase-1 work.
3. `RATIONALE.md` — the principle of division at every branch, every change
   between phase 1 and phase 2 with its reason, and the boundary cases you
   declare (same shape as `BOUNDARY_CASES.tsv`).
4. `SELF_AUDIT.md` — run the granularity audit on your own output, and name the
   sibling sets you are **not** confident in. Under-confidence declared is worth
   more than confidence asserted.

## 7. Depth

Design the **upper and family levels** — roughly depth 3 to 4. The second pass
grows the rest from the corpus.

The risk this carries is specific and must be managed: the family level has to
be tight enough that on-the-fly categorization is **never asked to invent an
intermediate level**. That is exactly how v0 ended up with 95 flat leaves and a
lone `bert` family sitting among them as a sibling. Wherever you can foresee a
family becoming wide — BERT is the known case — say so in `SELF_AUDIT.md`, and
it will get a second, deeper designed pass.
