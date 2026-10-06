# Pinning pass — fill the axis columns on every lineage node

You are pinning one region of the **algorithms** lineage axis to the other three
axes of the same dimension. This is the highest-yield check in this design
process: in the sibling **models** dimension, pinning exposed four missing axis
values and a whole family of methods that had no home on any axis. **Finding the
gaps is the deliverable. The pins are the by-product.**

## Inputs (read-only, do not edit)

- `role/nodes.tsv` — which slot of the pipeline a procedure fills
- `signal/nodes.tsv` — two sub-facets: `S.src.*` where the training target comes
  from, `S.form.*` how prediction and target are compared
- `attributes/nodes.tsv` — orthogonal property families, each with a `scope`
- `phase1/DRAFT_PHASE1_A.md` and `phase1/DRAFT_PHASE1_B.md` — the derivations
  these tables came from. A's `## Worked examples` section shows the intended
  semantics; read it before you start.

## Forbidden

Do not read `pinning/VOCABULARY.tsv`, anything under `../axes_models/` or
`../axes_domains/`, any file named `ROUTING*`, `proposed_categories*`,
`categorized_models*`, or anything under
`/home/bouthilx/projects/paperext-llm-backend/`. Those are corpus and other
dimensions; this pass must not be shaped by either. Do not read or write another
region's files.

## What to write

Rewrite your region file to `pinning/<region>.pinned.tsv` — **same columns, same
row order, same number of rows**, with only `signal`, `role` and `attributes`
filled in. Semicolon-separate multiple values. Use node_ids, never names.

## Rules

1. **A family node pins only what is true of every descendant.** `L.pg`
   (policy-gradient methods) can pin `R.fit.obj` and `S.form.return` because all
   of its descendants share them. It must **not** pin `A.regime.on`, because PPO
   is on-policy and DDPG is not. Leave a cell blank where descendants differ —
   children add their own, and a blank is how inheritance is expressed.

2. **A method node pins its own values**, including ones that contradict an
   ancestor. Where a method must *deny* an inherited value, write a negative pin:
   `!S.form.contrast`. This exists because union inheritance with no escape hatch
   is a known defect: in models it made MLP-Mixer resolve to self-attention.

3. **Respect the `scope` column on attribute families.** Only pin a value from a
   family whose scope covers the node. `A.regime` is scoped to procedures that
   learn from interaction data, so a tokenizer takes no value from it — and that
   is different from taking an unknown value.

4. **Do not invent axis values.** If nothing in the three tables fits, leave the
   cell **blank** and record the node in your report. A forced bad pin hides the
   finding; a blank with a report entry is the finding. This is the single most
   important rule here.

5. **If you need two values from one attribute family, pin both and flag it.**
   Per-family cardinality is not yet decided, and we want it derived from where
   it is actually needed rather than guessed. In models, a blanket one-value-
   per-family rule fixed VQ-VAE and broke EGNN, which genuinely is both
   permutation- and Euclidean-equivariant.

## Your report

Write `pinning/<region>.REPORT.md`:

- **Homeless nodes** — every node where an axis had no value that fits. Name the
  node, the axis, and what value would have been needed. Grouped, if many share
  a gap.
- **Proposed new axis values** — id, name, parent, positive_test, and the nodes
  that need it. Proposals only; do not add them to the tables.
- **Multi-value families** — every attribute family where you had to pin two
  values, with the node that forced it.
- **Negative pins used**, and what each was denying.
- **Nodes you could not pin at all**, and whether that is because the node is a
  description rather than a named procedure (many carry a review flag in `notes`
  saying exactly that).
- **Anything that made you doubt an axis**, including a slot you think should not
  exist or two that should merge.

Report back: counts pinned per axis, the number of homeless cases, your proposed
new values, and the two or three findings you think matter most.
