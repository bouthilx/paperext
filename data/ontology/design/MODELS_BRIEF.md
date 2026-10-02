# Models hierarchy: design brief and the entity model

Written 2026-10-01. Companion to `PROCESS.md` (how the domains design was run)
and `AXES.md` (what it decided). This file covers (A) how the dimensions relate
to one another and to the coming `runs` record, and (B) the brief for designing
the models hierarchy.

Issues: **#95** models structure · **#94** models extraction (runs) ·
**#93** datasets · **#89** research-field roles · **#91** domains axes.

---

# Part A — the entity model

## A.1 What a paper annotation becomes

```
paper
├── research_fields[]   term + role (contributed | used | referenced)      #89
├── models[]            term + is_contributed / is_executed / is_compared
├── algorithms[]        term + role                              NEW, #94
├── datasets[]          term + role + size + per-sample properties    #93
├── libraries[]         term + role
└── runs[]              references into the lists above, plus the
                        configuration and its cost                     #94
```

**Entity lists are dimension tables; `runs` is the fact table.** This is a star
schema, arrived at from the data rather than imposed.

The owner's worry that executed models would be "duplicated in `models[]` and in
`runs[]`" is **normalisation, not duplication**: a model appears exactly once as
an entity, carrying its identity and role, and runs *point at it by id*. Runs
must never re-describe an entity.

## A.2 A run is a distinct compute configuration, not an execution

Two executions are the **same run** when they share a compute profile, and
**different runs** when any of these differ:

```
execution_mode · precision · parallelism · accelerator count/type · scale · dataset
```

Hyperparameter variation that moves none of those — learning rate, seed,
dropout, weight decay — stays in **one** run, counted in `repetitions`.

**`repetitions` is load-bearing.** A paper running 5 seeds x 20 configurations
did 100x the compute of one training run, and in many ML papers the sweep *is*
the budget. Grouping without the multiplier loses compute, not just detail.

A run carries: `models[]`, `algorithms[]`, `datasets[]`, `execution_mode`,
`epochs`, `parameter_count`, `accelerator_type`/`_model`/`_count`, `precision`,
`parallelism` (set-valued), `duration`, `utilisation`, `repetitions`.

**A run's participants are constrained by its `execution_mode`** (owner,
2026-10-02): an `inference` run has a model and **no algorithm**; `train` and
`finetune` runs have both. `algorithms[]` holds *learning* algorithms only, so
this is a checkable invariant rather than a convention.

**(Model, Algorithm) pairs are why runs exist.** A paper testing three optimisers
on three models is nine runs over a 3x3 grid of two independent entity types —
not nine models. The algorithm is a *participant*, not a property of the model.

## A.3 Why this shape, from the purposes

- **domains** answers *what is this paper about* -> binned and multi-faceted
  analysis, comparing research areas.
- **models / algorithms / datasets** answer *what was used and what did it cost*
  -> compute estimation: kind of computation, I/O, memory.

These are different questions, so they want different structures. A paper
contributing an optimiser and benchmarking ten baselines has **one** research
field and **eleven** model entities — the baselines are irrelevant to domains and
essential to compute.

Target methodology is Epoch AI's, preferred method first:

```
preferred:  Compute = 6 x parameters x training examples x epochs
fallback:   peak FLOP/s (hardware x precision) x utilisation x duration
```

For this corpus the preferred method is also the more extractable one. Note
`training examples` is dataset-side, which is why #93 exists and why
`runs[].datasets` is the linkage that does not exist today.

## A.4 How the ontologies relate to each other

**The shared layer is vocabulary, not hierarchy.** Extraction yields bare terms;
a second pass places each term into the ontology for its dimension. Three
consequences:

1. **Changing an ontology never requires re-extraction.** `domains/v0` can be
   replaced outright without touching the corpus; the models restructure in #95
   is cheaper than it sounds.
2. **The same term may be placed in several dimensions, independently.** `PPO` is
   an algorithm entity *and*, where a paper researches it, a domains Method term.
   No structural coupling is needed for that.
3. **Ontologies may evolve on their own schedules.** Rejected: rooting the models
   tree in the domains Method axis (shared node ids). `Ontology.load(root / dim /
   version)` makes trees self-contained per dimension, so cross-dimension
   references are a format change, and coupling would make a Method re-derivation
   move models nodes underneath it.

**What domains already holds, and what it does not.** `Method > Model design >
Neural architectures` (236 mentions) has children *Convolutional networks,
Recurrent networks, Attention-based architectures, Equivariant architectures,
Conditional computation, Memory-augmented, Implicit-depth*. That is the
architecture **taxonomy as research topics**. It contains **no instances** — no
ResNet-50, no BERT, no GPT-4.

The distinction is load-bearing: `Neural architectures` means *this paper
researches architecture design*. Filing ResNet-50 under it would make every
paper that merely **uses** a ResNet into architecture research — the
contributed-vs-used error #89 exists to prevent. Same shape for algorithms:
`Learning signal > Reinforcement learning` (452) is a topic; `PPO`/`SAC`/`DQN`
are entities.

**Datasets may need no tree.** `datasets/v0`'s 18 roots mix modality, scientific
domain, task, artifact type and modality-combinations — which is why they fail
the audit. But a dataset is largely *characterised by axes that already exist*:
ImageNet = Modality>Vision>Natural imagery + Task>Classification; PubMedQA =
Modality>Text + Task>QA + Discipline>Medical. Candidate: axis values plus the
compute attributes in #93, and no fourth hierarchy. Not decided.

---

# Part B — designing the models hierarchy

## B.1 Settle entity types first

This is the lesson that arrived late for domains and must arrive first here.
Once typing is settled, #95's level-1 question largely dissolves: each type gets
its own smaller hierarchy with its own principle, instead of one tree whose
level 1 has to span four kinds of thing.

**The test**: *a model is the thing whose parameters are learned; an algorithm is
the procedure that changes them.* `ResNet` has weights -> model. `Adam` operates
on weights -> algorithm. `PPO` is an update rule; the policy network it updates
is the model. `parameter_count` being a model-side field is this test made
operational.

**The admission rule** (owner, 2026-10-02). A term enters the **models**
ontology only if it names a **separable learned object** — parameters that could
be described and run independently of the procedure that produced them. If there
is no such object (nonparametric), or the object cannot be separated from the
procedure, the term is an **algorithm only**, and a run then references an
algorithm with **no model**.

| term | model | algorithm |
|---|---|---|
| logistic regression | linear model, logit link | the fitting procedure |
| random forest | decision-tree ensemble | bagging + random subspace |
| XGBoost | gradient-boosted tree ensemble | the boosting procedure (+ a library) |
| k-NN, kernel density | *none* | algorithm only |
| PPO / SAC / DQN | the policy and value networks | the update rule |
| diffusion model | the denoiser (usually a U-Net) | the denoising procedure |
| GFlowNet | the flow network | the training objective (TB/DB/FM) |
| SimCLR / BYOL / DINO | the encoder the paper names | the SSL objective |

Thin on logistic regression, and accepted as such: a linear model is a real
compute profile, which is what the dimension is for.

**`algorithms[]` holds strictly *learning* algorithms** (owner, 2026-10-02).
An inference-only run has a **model and no algorithm**; a train or finetune run
has both. This makes `execution_mode` and the run's participants mutually
checkable, and it keeps inference-time procedures (beam search, sampling
schedules, planning at test time) out of the entity list. Declare MCTS a
boundary case: training-time target generation is a learning algorithm,
test-time planning is not.

**SimCLR, worked through.** Its architecture *is* separable — a standard encoder
plus a 2-layer MLP projection head discarded after pretraining, a shape MoCo,
SwAV and BYOL reuse. So it is an algorithm, and the model is the backbone.
Measured caveat: of 33 legacy-2024 papers naming an SSL method, only 8 (24%)
also had a backbone extracted — but **that corpus was annotated under a schema
with no algorithm slot**, so "SimCLR" was a complete answer and the extractor
stopped there (owner's reading, 2026-10-02). In the fulltext cache, 25 of 38
SSL-method papers (66%) name a concrete backbone in the text; that is an upper
bound, since a grep hit may be a related-work mention. The gap is the schema,
not the papers. The (model, algorithm) pair requirement should close most of it,
and the remainder are legitimate algorithm-only runs.

Scale: `algorithms` holds 273 of 1409 nodes in v0 (RL 112, other algorithms 110,
optimizer 50, federated 1). **`other algorithms` is a type confusion, not a junk
drawer** — `ant colony optimization`, `c51`, `bm25` are algorithms; `blip` is a
model. No restructuring *within* one tree fixes that.

## B.2 What the ontology carries, and what it must not

- **Carries: structural primitives** — attention, convolution, recurrence, sparse
  routing, tree traversal, factorisation. Invariant per family.
- **Does not carry compute patterns.** Compute is a property of a *run*
  (model x execution mode x parallelism x scale). The same model trained vs used
  for inference, or on one GPU vs tensor-parallel, is a different workload.
- **Never *divides by* scale.** No `Large models` / `Small models` node exists
  anywhere, and **scale variance is not a granularity criterion** (owner,
  2026-10-02): an architecture may be perfectly well defined *and* scalable
  across several orders of magnitude — a Transformer is one architecture from
  100M to 1T parameters.
  But **separately named size variants ARE nodes** (owner, 2026-10-02,
  overruling a second proposal of mine to collapse them): `llama2-7b` sits under
  `LLaMA 2`. Run statistics aggregate upward to recover the size distribution,
  while the reverse is impossible — and larger variants are often trained
  differently from smaller ones (parallelism, precision, hardware), a
  correlation collapsing would destroy.
- **Genealogy IS the backbone** (owner, 2026-10-02 — this bullet previously
  said the opposite). An earlier version held that `derives-from` is a DAG while
  `is-a-kind-of` aggregates and is closer to a tree, so genealogy should be a
  separate optional relation. Superseded: for models the two largely coincide —
  RoBERTa *is a* BERT because it was *built as* one — and the three candidate
  dividing characteristics (computational primitive, data structure consumed,
  function learned) were all rejected because each is a property of a layer, an
  application or a use, never of the model. **Multi-parent is legal**, because
  the project's counting is non-exclusive already (E1, #16). Rules in
  `MODELS_DERIVATION_BRIEF.md` §4.

## B.3 Attributes attach to families, not entities

Forced by the data: **2342 names, 3601 mentions, 51% of mentions appear once** —
twice as tail-heavy as domains (25%) — because papers name specific artifacts
(`llama2-7b`, `bert-base-uncased`). Top 200 names cover only 32% of mentions, so
there is no head to describe by hand.

The hierarchy therefore earns its keep by **tail-collapse**: it turns ~2342
entities into ~50-150 described groups. Attributes attach to those groups, and a
property attaches at **the highest node where it holds for every descendant**.

## B.3b What the hierarchy is for: aggregation at several levels

**Settled 2026-10-02, after a rejected proposal of mine.** I proposed that only
families be nodes and that artifacts (`llama2-7b`, `roberta`) be attached as
*surfaces* — spellings resolving to a family node — to cap the tree at ~100–150
nodes. **Rejected by the owner, correctly.** The analyses this dimension exists
to serve ask *what proportion of models were Transformers*, and also *what
proportion were BERT*, and also *what the BERT variants were*. Those are three
different cuts, and they require three real levels. Squashing artifacts into
surfaces of a family node makes every cut below Transformer impossible.

So: **artifacts are nodes.** `Transformer › Encoder-only › BERT › RoBERTa` is
the shape, and the cut may sit at any of those depths. The brief's tail-collapse
argument (B.3) survives only as a statement about *singletons*, not about
recurring artifacts.

### Depth of the designed tree (owner, 2026-10-02)

Two readings were put to the owner:

- **(a)** design the upper and family levels; the second pass grows the rest.
- **(b)** also design every recurring variant up front.

**Decision: mostly (a), then assess.** Derive the upper/family levels first,
then identify the few leaves whose breadth warrants a second, deeper designed
pass — **the BERT family is the named example**: it is wide enough that
on-the-fly categorization would reinvent the missing middle, which is precisely
how v0 ended up with 95 flat leaves under `transformer`.

The risk (a) carries is exactly that: the family level must be specified tightly
enough that the second pass is never asked to invent an intermediate level. Any
node the agent can foresee needing one is a candidate for the deeper pass.

## B.4 Procedure

Reuse `PROCESS.md` §2 in full. Specific to this derivation:

1. **Publish a count-free characteristics file first.** Phase 1 must not read
   `nodes.tsv` — its `examples`, `corpus_names` and `corpus_mentions` columns
   leak counts and make the corpus-free phase fiction. Two agents reported this
   contamination independently.
2. **Forbid reading `models/v0`**, so the hierarchy is derived from the field's
   structure rather than patched from the legacy shape. The corpus vocabulary is
   an input; the legacy tree is not.
3. **Two-phase protocol**: draft from the field's structure with no corpus
   access -> freeze in `DRAFT_PHASE1.md` -> consult the corpus for blind spots
   and speculative flags only -> deliver both versions with every change
   explained.
4. **Volume prioritises which node to open; it never shapes how it opens.**
5. Agent runs the **granularity audit on its own output** and declares sets it is
   not confident in.
6. **External breadth**: ACM CCS `Computing methodologies`, arXiv categories,
   Papers With Code. For breadth and blind spots, never arbitration.

## B.5 Defects not to inherit from v0

Root set `algorithms` / `classic_ml` / `neural networks` / `others` / `ignore`
fails the audit: a neural network *is* an algorithm, so those are not siblings;
`classic_ml` divides by **era**, not by any property; `others` is an unprincipled
residual. Four characteristics that overlap rather than partition.

Also: 66 duplicate clusters over 143 nodes (`deep q-network (dqn)` /
`deep q networks (dqn)` / `deep q-networks (dqn)` / `dqn`); the cut names 8 of 25
categories, which is most of the 43% `Other`. Full list in #95.

**Correction, 2026-10-02.** An earlier version of this file, and #95, said
`transformer`'s 131 children "are artifacts, not sub-architectures". Measured:
false. `bert` is a proper family with 22 children (`roberta`, `distilbert`,
`codebert`, `albert`, `tinybert`, `protbert`…), and 36 of the 131 have children.
The real defect is **asymmetry and a missing middle**: `bert` sits as a sibling
of 95 one-off leaves, `llama` gets no family grouping at all, and between
`transformer` and those leaves there is no encoder-only / decoder-only /
encoder-decoder level. You can aggregate at Transformer or at a single artifact,
with nothing in between — which is the capability the dimension exists for. The
task is therefore **principled upper levels plus consistent intermediate family
levels**, not pruning the tree.

**v0 is not a reference for a good hierarchy** (owner, 2026-10-02). The corpus
may be consulted for *what needs to be covered*; v0's shape informs nothing.
B.4 step 2 (forbid reading `models/v0`) stands on this.

## B.6 The comparison step (owner's plan, 2026-10-01)

**Design the models hierarchy first, then compare it against the domains
`Method > Model design` subtree** to settle empirically whether a separate models
hierarchy earns its keep or is duplicated work. Do not decide this in advance,
and do not root one tree in the other while the question is open.

Expect legitimate divergence on granularity: `Attention-based architectures`
carries 41 mentions as a research topic, while the models dimension needs
BERT-family vs GPT-family distinctions under 131 transformer artifacts.

If a correspondence is worth recording without coupling, use a **declared
correspondence table** — same shape as `BOUNDARY_CASES.tsv` — which is checkable
and documents the relationship with no runtime dependency.

---

# Part C — open

- Are **libraries** a third participant in a run? `DeepSpeed`/`FSDP` are part of
  the configuration and already extracted, but library-based inference of
  parallelism is too imprecise to replace an explicit field. Note `libraries[]`
  is a contaminated source: `adam` (23 papers), `adamw` (8) and `bert` (8) were
  extracted into it, with quotes that leave no doubt — *"The networks are trained
  using the Adam optimizer"*, *"We use BERT as the encoder"*. The extractor
  treats anything tool-shaped as a library. On the #94 list.
- Does the **datasets** dimension need a tree at all (A.4), or axis values plus
  attributes?
- **Repair or restructure `models/v0`**, and before or after the gate. The gate
  has not run, so changing v0 is at its cheapest now; afterwards the same change
  costs the gate.
- Whether to gate on a **16-case surface arm** in clause 5c (PR #90, merged).
- Which leaves earn the **deeper designed pass** of B.3b. Assessed after (a)
  lands; BERT is the one already named.

---

# Decisions log

**2026-10-01** — entity model (Part A): star schema, runs as the fact table,
shared layer is vocabulary not hierarchy.

**2026-10-02** — five decisions, all the owner's, three of them overruling me:

1. **Scale variance is not a granularity criterion** (B.2). An architecture can
   be well defined and scalable across orders of magnitude.
2. **Artifacts are nodes, not surfaces** (B.3b). Multi-level aggregation is the
   purpose of the dimension; my capping proposal would have destroyed it.
3. **Admission rule for `models`**: a separable learned object, else
   algorithm-only, and a run may carry an algorithm with no model (B.1).
4. **`algorithms[]` is strictly learning algorithms**; inference-only runs have
   a model and no algorithm (B.1).
5. **Designed depth is (a), then assess** which leaves need more (B.3b).

**2026-10-02, second round** — the backbone:

6. **Three candidate level-1 characteristics rejected** — computational
   primitive, data structure consumed, function learned. One objection, not
   three: each is a property of a layer, an application or a use, not of the
   model, which is invariant under all three.
7. **The backbone is architectural lineage.** Parent → child means the child was
   derived from the parent.
8. **Multi-parent is legal and a DAG is fine.** Aggregation here is already
   non-exclusive (E1 #16: paper → *set* of categories, columns overlap), so no
   primary lineage is designated and no edge is dropped to force a tree.
   Code consequence: `analysis/rollup.py` returns `dict[str, str]` and needs
   `dict[str, set[str]]`.
9. **Composition recipes are out of scope** — ideal for compute estimation, but
   judged unrealistic to extract. We classify names.
10. **Every separately named release is a node, size variants included**
   (`llama2-7b` under `LLaMA 2`, `ResNet-18` and `ResNet-50` under `ResNet`).
   I proposed collapsing them; overruled for the same reason as decision 2 —
   aggregation can always go up, never down, and large variants are often
   trained differently from small ones. A name is a spelling **only** when it
   denotes the same release under a different string.
11. **Only a design pass may create grouping nodes; the second pass may only
   attach under descent** (R7). This is what closes v0's missing middle: 95 flat
   leaves under `transformer` exist because categorization was left to invent
   structure it had no mandate to invent.

Also corrected on 2026-10-02: the "131 transformer children are artifacts"
claim was false (B.5); the 24% SSL-backbone figure measures the *old* schema and
is not evidence of an extraction defect (B.1).
