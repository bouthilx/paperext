# Acceptance cases the data-sources dimension owes #103

Step 6 of #102. Each case names a rule, the shape a correct extraction has, and
what a failure would mean — because a case whose failure is uninterpretable is
not a test. Four were specified when #102 was planned; the rest come from the
phase-2 placements and the mechanism/referent split, which found the rules the
prompt was silent about.

A case fails **soft** if a human reading the paper would also hesitate. Only the
hard failures below are prompt defects.

## From the original plan

**1. A RAG paper returns its retrieval corpus with `roles_in_run=['reference']`.**
A corpus queried at inference is not training data and must not be counted as
such. Failure means every "how much data did this paper train on" figure is
inflated by the retrieval index. The corpus-measured frequency of this shape was
12 names / 23 paper-pairs.

**2. An RL paper returns its environment at all.**
The legacy schema's `datasets[]` slot made this awkward enough that environments
were sometimes dropped. 59 names / 107 pairs are interactive environments, so a
silent miss here removes the institute's entire RL footprint from the survey.

**3. `synthetic data` does NOT come back as a named source.**
The admission rule excludes unnamed descriptions. ~41 names / 50 pairs are of
this kind. Failure is the cheap-to-detect direction: a node whose name is a
description rather than an artifact.

**4. A collect-then-train paper reports `access: fixed`, not `interactive`.**
`access` is a property of the mention. A paper that freezes a buffer and trains
on it did not do interactive RL, and coding it as if it did inflates exactly the
count the survey exists to produce.

## From the admission rule, as amended

**5. `MuJoCo` comes back as a Library; `HalfCheetah` comes back as a Data Source.**
One string, two entities. `MuJoCo` is the most-cited name in the placement set
(10 papers) and the engine is not a source. **Hard failure** if the engine
appears in `data_sources[]`.

**6. `Atari` comes back as a Data Source; `Atari 100k` does not.**
The protocol clause, added 2026-10-08. A protocol says how much of a source to
use and how to score it. All three placement runs found these admitted and then
returning the base environment's values, double-counting it. 12–22 names.

**7. A paper naming a released derivation gets an entity; a paper describing an
ad-hoc one does not.**
`D4RL` and the DQN Replay dataset are entities with `derived_from`. "We
collected 1M transitions and trained on them" is a step the run records, with no
entity. The criterion is **named as an artifact**, not "a derivation happened".

## From the run criterion and `execution_mode`

**8. A GAN paper returns ONE run, not two.**
The gradient passes through both networks; it is one coupled optimisation loop.
Same for actor-critic and VAE. **Hard failure** if generator and discriminator
appear as separate runs.

**9. Online RL returns ONE run, not generation plus training.**
The negative test for the production-stage rule. A run is a unit of compute the
paper spent, and an online RL loop is one.

**10. A bulk data-production stage returns `execution_mode='generate'`, not
`'inference'`.**
`inference` means a *model* producing predictions, and the cost formulas assume
a parameter count. Stepping a simulator or transforming a corpus has none.
**Hard failure** if a simulator-stepping run reports a `parameter_count`.

**11. Sampling a model for training data DOES return `'inference'`.**
The nuance that makes case 10 a real distinction rather than a blanket rule.

## From the phase-2 placements

**12. A source used as both a generator and an environment does not silently
lose one.** `access` is single-valued per (source, use), and two placement runs
found 19 and 22 names where both positive tests pass on different units — a
procedural level is minted on request, then stepped. This case **measures the
known limit** rather than asserting a correct answer; record which value comes
back, and how often the quote mentions the other.

**13. A frozen log of a simulator reports `fixed` and names its parent.**
The `derived_from` relation carries provenance, not sizing. One known
unsatisfiable sub-case, recorded so it is not read as a defect: when the parent
simulator is proprietary and unnamed, the relation has no node to point at.

## Not testable at #103, recorded so nobody looks for them

`provenance` and `referent` are assigned **post-hoc** from the name and the
quote, not extracted, so no prompt case can test them. The extraction's only
obligation to those axes is to return the name and a usable quote. The axes'
own open questions — the channel problem, and whether `referent` is entity-level
at all given that one engine spans several of its values — are design questions
and are recorded in `SYNTHESIS.md` §7, not here.
