# How the domains ontology was designed — process record

Written 2026-10-01, to be reused for the **models** hierarchy (#95) and
**datasets** (#93 part 2). `AXES.md` records *what* was decided; this records
*how*, including what went wrong and how it was caught. The failures are the
more useful half.

---

## 1. The sequence that worked

**Step 0 — measure before deciding anything.** Both legacy trees were measured
before any design: node counts, compound names, `Other` rate at the cut, depth,
branching. That produced the verdict "models usable, domains not" and the single
most useful early finding: **the cut file, not the tree, caused most of the
`Other` rate** — `domains/v0` named 4 of 63 available categories, `models/v0` 8
of 25. Without measuring we would have rebuilt a tree to fix a one-file problem.

**Step 1 — three independent agents, identical brief.** Same inputs, no sight of
the legacy tree or of a prior attempt (`proposed_categories.csv`). The point was
to see what replicates. Two of three converged on a single tree, one on four
axes; the *arguments* each gave mattered more than the structures.

**Step 2 — design the levels, not the nodes.** The turn that unlocked everything
was moving from "which categories should exist" to "**what characteristic
divides this sibling set**". Nodes are derived from the principle, never chosen
directly.

**Step 3 — iterate with the owner on principles, one axis at a time.** Long
conversation, not a document review. The owner's challenges changed the design
repeatedly (see §4).

**Step 4 — agents derive nodes, one per axis**, from the schema rather than from
the corpus. Then re-derive where an audit found defects.

**Step 5 — validate three ways**: a stratified tail sample, a granularity audit,
and a diff against external classifications.

---

## 2. Rules that survived, and why each exists

1. **The corpus bounds scope and exposes blind spots; it does not arbitrate.**
   A category with no corpus support is *possibly speculative — justify or keep*;
   a corpus cluster with no category is a *blind spot*. Neither auto-deletes.
   **Why**: the first brief said "if you cannot find three examples, the category
   is not real — merge or drop it". That deletes legitimate areas a one-year
   single-institute snapshot happens not to contain, and rewards fitting this
   corpus over describing the field. It would have deleted every regulator-facing
   property on the Desired-properties axis.

2. **One principle per sibling set, not per level.** Different parents may divide
   by different characteristics. Violating it produces `X and Y` node names and
   residual junk drawers.

3. **A child sibling set must refine its parent's characteristic**, never import
   another aspect's. **Worked case**: under `Learning signal > Reinforcement
   learning`, both candidate splits (model-based/model-free, value/policy) divide
   by *machinery*, so either reproduces the parent-level defect one level down.
   Depth 3 divides by *who supplies the evaluative signal*.

4. **Volume decides which node to open next; it plays no part in how it opens.**
   Ordered, and the ordering is what makes compliance checkable:
   draft the sibling set from the field's own structure with **no corpus
   access** -> freeze it in `DRAFT_PHASE1.md` -> only then consult the corpus,
   for two questions only (blind spot to add; speculative node to flag) ->
   deliver both versions and every change with its reason.
   **Result**: across four depth-3 expansions, *no corpus check changed any
   structure*. Verifiable from file timestamps.

5. **External classifications supply vocabulary and breadth, never arbitration.**
   ACM CCS fails our own granularity audit (`Supervised learning`, `Machine
   learning approaches`, `Machine learning algorithms` and `Markov decision
   processes` are siblings). OECD `1.2 Computer and information sciences`, read
   literally, swallows all 1999 papers. Use them to find *holes*, not to settle
   arguments.

6. **A property attaches at the highest node where it holds for every
   descendant.** The inverse is a check: a property that is not uniform across
   children means push it down, or the node fuses two things.

7. **An axis is admitted only if two papers can differ on it while agreeing on
   every other axis.**

8. **Never balance categories by paper count.** The study measures proportion of
   research per area; engineering equal sizes destroys the quantity being
   measured.

---

## 3. The validation instruments, and what each caught

**Tail validation** (`TAIL_VALIDATION.md`). Stratified random sample — 50 names
from the >=3-paper band, 100 singletons — placed using only the written tests.
Output is not placements but a **strain list**: where a rule was ambiguous or
missing. 9 findings from 150 names, including two blocking gaps in Method.
*This measures the schema, not the corpus: a name that cannot be placed is a
schema defect.*

**Granularity audit** (`GRANULARITY_AUDIT.md`). For every sibling set: are these
the same *kind* of thing, at the same level of specificity, and **does any
sibling exist only because it was large in this corpus?** Caught the defect that
reshaped the whole application axis — `Neuroscience` was a top branch at 84
mentions while `Chemistry` was not at 43. That is balancing by paper count
through the back door.

**External diff** (`EXTERNAL_DIFF.md`). ACM CCS for designed comparison, arXiv
primary categories for an author-chosen external label (810 of 1742 papers),
Papers With Code for task vocabulary. Found three blind spots **two sources
agreed on**: evolutionary computation, logic/relational learning, and classical
AI beyond learning (KR&R, planning, search). None was findable from the corpus.

**Agents auditing their own output.** Every derivation brief required the agent
to run the granularity audit on itself and **declare sets it was not confident
in**. This was consistently the highest-value section of their reports — one
declared that two of its nodes existed partly because they were large in this
corpus, which is exactly the defect being hunted.

---

## 4. Owner challenges that changed the design

These are worth re-reading before the models derivation, because each overturned
something that looked settled.

- *"Why is Physical & environmental sciences one category while Neuroscience is
  another, and where is Chemistry?"* -> the bottom-up level 1 was volume-shaped.
  Replaced wholesale by OECD FOS.
- *"Is v0 the previous Milabench ontology or the one we created?"* -> exposed
  that I had been blurring dimensions. Led to naming the dimension first, always.
- *"Are `other algorithms` relevant for models? Wouldn't they be covered by
  domains?"* -> produced the purpose distinction: **domains = what the paper is
  about; models = what it cost to run**, which reframed the entire models
  question and produced #94.
- *"We could have (Model, Algo) pairs per run."* -> runs are a relation over
  several typed entities; `other algorithms` is a **type confusion**, not a junk
  drawer. The models dimension is at least two entity types.
- *"The annotation provides only the term; it is categorised in a second pass."*
  -> the shared layer between dimensions is **vocabulary, not hierarchy**, so
  ontologies can evolve independently and changing one never requires
  re-extraction.
- *"Compute pattern depends on train-vs-inference and on parallelism."* ->
  compute is a property of a **run**, not of a model; the ontology carries only
  structural primitives, which are invariant.

---

## 5. Sources of confusion, and how they were resolved

**Which dimension are we in.** Recurring, and the owner said so explicitly.
Resolution: name the dimension in the first line of every issue and every
summary; `litreview-dimensions.md` in memory holds the issue map.

**Where the data lives.** `domain_names.tsv` (1999 papers) could not be
reproduced from this checkout, which has 102 extractions. Nearly an hour lost to
archaeology that ended with me unable to verify the file's provenance. Resolved
by the owner asking **"what is your cwd?"** — the corpus is in a *different
checkout of the same repo*,
`/home/bouthilx/projects/paperext-llm-backend/data/mdl/queries/openai/legacy-2024/`.
**Lesson: when a file cannot be reproduced, check sibling checkouts before
doubting the file.**

**Counts I asserted that were wrong.** Repeatedly, and always the same cause —
summing only the head of the distribution:
- §7's per-branch figures undercounted the application axis by **2.5x**.
- The sector axis was estimated at ~93 mentions and measured at **389**, with
  ~154 sector-only. I nearly argued the owner out of an axis they had correctly
  proposed, on a number I had constructed badly.
- `Tabular` was called a 1-mention blind spot; it is ~34 once an unmade routing
  decision is made.
**Lesson: never quote a per-branch size without computing it over the whole
vocabulary, and label every count in a design document as indicative.**

**Claiming a field was captured when it was never extracted.** I twice told the
owner that `parameter_count` and `execution_mode` were "already recorded per
mention". They exist in `model_v4` and **no corpus has ever been extracted with
v4**. **Lesson: check the data, not the schema, before saying something is
available.**

**Fixing from source instead of from a case.** Clause 5c was diagnosed by reading
the scorer and writing a POLICY rule. The rule changed nothing, cost a run, and
the first look at an actual failing record showed the agent had been correct all
along — the reference holds the same concept 2-4 times. **Lesson: look at one
failing example before writing any fix.**

**A justification that was wrong even though the conclusion held.** Clause 2e was
dropped with a comment saying it "fired on noise". It did not — it fired on
papers splitting across duplicate nodes. The clause is still worth dropping, for
a different reason. **Lesson: a correct decision with a false rationale is a trap
for whoever reads it next; correct the rationale in place.**

**A protocol hole I wrote myself.** Phase 1 was meant to be corpus-free, but the
brief required reading `nodes.tsv` for the parents' characteristics — and that
file carries `examples`, `corpus_names` and `corpus_mentions` in adjacent
columns. Two agents independently reported the contamination rather than
benefiting from it. **Fix for next time: publish characteristics to a separate
count-free file and point phase 1 at that.**

---

## 6. What to do differently for models

- Publish a **count-free characteristics file** before any derivation starts.
- Decide the **entity types first** (model / algorithm / released artifact), since
  #95's level-1 question largely dissolves once typing is settled — a lesson that
  arrived late for domains and should arrive first here.
- Expect models to be **twice as tail-heavy**: 2342 names, 51% of mentions are
  singletons, against 25% for domains. Head-only description does not scale;
  attributes attach to families and the hierarchy does tail-collapse.
- **Then compare the result against `Method > Model design`** (owner's plan,
  2026-10-01) to settle empirically whether a separate models hierarchy earns its
  keep or duplicates work. Do not decide this in advance.
