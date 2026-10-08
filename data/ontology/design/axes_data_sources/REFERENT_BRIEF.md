# Derivation brief: the `referent` axis, and provenance as mechanism

Owner decision, 2026-10-08. This brief is the input to three independent
derivations; it is written so that a run can work from field knowledge alone.

## Why this axis exists

The data-sources dimension shipped two axes (`access`, `provenance`). Placing
real names against them showed `provenance` asking **two independent questions
at once**:

1. **By what mechanism were the signal's values produced?** Measured off an
   instrument, authored by a person, computed by a program, emitted by a learned
   model.
2. **What, if anything, is the signal a record of?** A real physical or
   biological system, a formal object with no worldly referent, or something in
   between.

`provenance`'s `simulated` value demanded *both* — an engine with physical units
**and** that "the simulation is wrong" be a meaningful complaint — and the field
is full of sources that satisfy one and not the other. A locomotion task in a
rigid-body physics engine has the engine, the units and the solver, and
approximates no animal that exists: nothing is being got right or wrong. A
regulated physiological simulator has the identical machinery and a real patient
population behind it. Those are not the same kind of source, and one value
cannot hold both without one of its two tests being ignored.

The same split appears twice more. A photographic dataset of street signs is an
instrument measurement whose subject is a human artifact, so a `natural` value
defined by "remove every human purpose and the process still runs" expels its
own exemplars. And a game supplies observations by construction and rewards by a
stated rule — one source, two mechanisms, which is a *scope* problem rather than
a value problem.

The fix was named, with low confidence, when the first two axes were derived:
**one mechanism value for "computed by a program", plus a separate `referent`
axis.** The owner has adopted it. Your job is to derive it properly rather than
to ratify it.

## What to derive

**Both halves, because they are one change.**

**(a) The `referent` axis.** State its principle of division in one sentence,
then its values, each with: `characteristic`, `positive_test`, `negative_test`,
`examples`, and a `notes` field recording your own doubts. Decide and state
explicitly: is it single- or multi-valued; does it apply to every source or only
to computed ones (a scope predicate); and what the coding state is for "the
paper does not say". The question the axis must answer for a reader of the
survey is roughly *is this a study of the world or an exercise on a constructed
object* — but do not take that phrasing as the division; derive your own.

**(b) The consequent mechanism value set for `provenance`.** If `simulated` and
`constructed` differed only by referent, they collapse. Then say what happens to
the three values that are *also* program-computed under a strict mechanism
reading:

- `rule` — a stated non-learned rule or verifier computed the signal.
- `model-generated` — a learned model emitted it.
- the collapsed `program-computed` itself.

A mechanism axis on which one value is a superset of two others is not an axis.
Resolve it, or state precisely why it cannot be resolved and what that costs.
Do the same for `natural` versus `human-incidental`, whose boundary currently
turns on the *subject* rather than on the mechanism.

Say whether the channel problem (observations by construction, rewards by rule)
is solved by your design, and if not, what would solve it. Do not invent a
channel axis to make it go away; recording that it is unsolved is worth more.

## Method — binding

Follow `METHOD.md` in this directory. In particular:

- **Draft with no corpus access.** Derive from your knowledge of the field, not
  from this project's extraction data. **Do not open** `SYNTHESIS.md` §6,
  `placements/`, `placement_candidates.tsv`, `operational_sweep.tsv`,
  `data_source_names.tsv`, `datasets/v0`, or anything under
  `/home/bouthilx/projects/paperext-llm-backend/`. You may read `METHOD.md`,
  `access/nodes.tsv` and `provenance/nodes.tsv` — the current tables, so you can
  see what you are amending — and `SYNTHESIS.md` sections 1 to 5.
- State at the top of your report exactly what you read.
- **A value earns its place by its characteristic, never by how common it is.**
  Rarity is not an argument against a value; incoherence is.
- Record disagreement with this brief. The brief's framing of the problem is
  itself a claim, and if the division it assumes is wrong, say so.

## What a good report contains

The values with their tests, the two halves above, and — most valuable — the
cases where your own tests give contradictory answers, which is how all three of
the defects that prompted this brief were found.
