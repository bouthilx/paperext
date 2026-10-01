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

**The fuzzy band is real**: `GFlowNet` (flow network has parameters; flow
matching is a procedure), `Diffusion model` (denoiser has parameters; the
diffusion procedure does not), `XGBoost` (a library, an algorithm *and* a model
family). Handle as in domains: **the same term maps into both types**, because it
answers two different questions. Never force one arbitrary choice — that is
exactly the duplicate-node failure that corrupted three eval clauses.

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
- **Does not carry scale.** `MLP` spans orders of magnitude; `parameter_count`
  lives on the run. Variance of that value within a node then becomes a
  *measurable* criterion for whether the node is at the right granularity.
- **Genealogy is a separate, optional relation.** `derives-from` is a DAG;
  `is-a-kind-of` is what aggregates and is closer to a tree. Multi-parent
  kind-membership usually signals a fused second characteristic — ViT is *a
  transformer* (kind) on *images* (modality).

## B.3 Attributes attach to families, not entities

Forced by the data: **2342 names, 3601 mentions, 51% of mentions appear once** —
twice as tail-heavy as domains (25%) — because papers name specific artifacts
(`llama2-7b`, `bert-base-uncased`). Top 200 names cover only 32% of mentions, so
there is no head to describe by hand.

The hierarchy therefore earns its keep by **tail-collapse**: it turns ~2342
entities into ~50-150 described groups. Attributes attach to those groups, and a
property attaches at **the highest node where it holds for every descendant**.

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
`deep q networks (dqn)` / `deep q-networks (dqn)` / `dqn`); `neural networks >
transformer` has 131 children that are artifacts, not sub-architectures; the cut
names 8 of 25 categories, which is most of the 43% `Other`. Full list in #95.

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
  parallelism is too imprecise to replace an explicit field.
- Does the **datasets** dimension need a tree at all (A.4), or axis values plus
  attributes?
- **Repair or restructure `models/v0`**, and before or after the gate. The gate
  has not run, so changing v0 is at its cheapest now; afterwards the same change
  costs the gate.
- Whether to gate on a **16-case surface arm** in clause 5c (PR #90).
