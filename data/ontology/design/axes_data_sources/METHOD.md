# Data sources — method

Written **before** the phase-1 derivations came back (#102 step 3, 2026-10-07),
deliberately. Two of the conventions below exist because not fixing them in
advance cost real work on the algorithms dimension, and a convention agreed
after seeing the results is not a convention, it is a rationalisation.

---

## 1. The two-phase protocol

**Phase 1 — derive with no corpus access.** Three independent agents, each given
the admission rule and the two axes and nothing else: no `data_source_names.tsv`,
no `datasets/v0`, no `B6_DATA_SOURCES_COMPARISON.md`, and not the value sets
proposed in #102 Part B. They were told to read no files at all.

They are `general-purpose` agents rather than forks **on purpose**: a fork would
inherit the proposing context, including the candidate value names, which is
exactly the contamination the parallel runs exist to rule out.

Three different entry points, so that errors are not correlated:

| run | entry point |
|---|---|
| A | what ML practice actually trains on |
| B | the compute-estimation requirement — what distinction changes how `training examples` is counted |
| C | first principles about sources of information |

**Freeze.** The synthesis is written and timestamped before any corpus file is
opened.

**Phase 2 — corpus for blind spots only.** A name with no value is a real gap
however the sample was drawn. **Absence is never evidence**, and the corpus never
arbitrates between two candidate values.

### What cannot be verified here, stated plainly

On the algorithms dimension the freeze was verified from the agents' tool-call
order. Through the agent interface used here only the final report comes back,
so **the no-file-reads instruction cannot be verified mechanically.** Each run
was asked to state what it read; beyond that, the only available check is
negative — output containing a corpus-specific name it could not have known
would betray a read. That is a weak check and is recorded as weak.

## 2. How the three runs are compared

Fixed before reading them:

- **Agreement across runs is the evidence.** A value all three reach
  independently, from three different entry points, is kept.
- **Divergence is the finding, not a tie to break.** Where two runs differ the
  divergence is recorded in the synthesis with both readings. It is *not*
  resolved by majority: two runs agreeing can both be wrong for the same reason,
  and the whole point of three entry points is that the third's disagreement
  carries information.
- **Alignment is by characteristic, not by name.** Two runs naming the same
  distinction differently agree; two runs using the same word for different
  distinctions do not. Nothing is matched on string similarity — that rule is
  already recorded twice on this project.
- **A value only one run proposes** is kept and flagged `speculative` if its
  characteristic survives the positive/negative test, dropped if it does not.
  Rarity is not the test; coherence is.
- **The `## Tensions` sections are read first.** On the sibling dimensions they
  were worth more than the deliverables, and three of the largest findings were
  pins that existed and were *wrong* rather than missing — invisible to any
  coverage check.

## 3. The placement convention, which this dimension does not need

Every placement records the **full value set** for the source. There are no
deltas, because **there is no lineage tree to inherit from** (#102 step 2,
`B6_DATA_SOURCES_COMPARISON.md` §1).

This is worth stating rather than leaving implicit: on the algorithms dimension,
placements inherited down a lineage tree, so a row could mean either "the full
resolved set" or "what differs from my parent". Six agents used both readings and
**350 of 401 apparent inter-region disagreements were artefact of that
ambiguity**. A dimension with no tree cannot produce that failure. One real
benefit of the no-tree result, collected in advance.

## 4. Rules carried over unchanged

- **Never rebalance**, and no bound on the number of values. A value holding most
  of the corpus is a finding, not a defect.
- **The ontology covers the field, not the corpus.** A value with no corpus
  support is flagged `speculative` and kept. Measured here: 81% of corpus names
  appear in exactly one paper and the admission rule's named-only clause accounts
  for only ~1.6% of names, so **faceting has to carry the tail** — culling will
  not.
- **Counting is non-exclusive** (#16), so multi-axis membership costs nothing
  semantically.
- **Aliases are written, never inferred.** Token matching paired `gpt-j` with
  `GPT-4`; a morphological rule put `bayesian neural networks` under the
  graphical-model node; `optics` the branch of physics collided with `optics` the
  clustering algorithm.
- **`access` is assumed single-valued and `provenance` multi-valued**, and each
  run was asked to challenge the first. `provenance = many` means it unions up a
  chain with denial as the escape hatch (#104) — though with no tree there is no
  chain, so for now it simply means a source may carry several values.
- **No `mixed` value on `provenance`** (owner, 2026-10-07). A mixed source
  resolves to the *set* of its kinds. `mixed` would discard which kinds mixed,
  would silently drop such sources out of every per-kind roll-up, and is a
  statement about *how many answers there are* rather than about what produced
  the signal — the category error that forced `A.deriv` to be split and the
  `(source, form)` pairs to exist.
