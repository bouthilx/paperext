# Design a base category structure for ML research topics

## What this is for

We are surveying ~2000 machine-learning papers from one institute to report
**what proportion of research activity falls in each area**. An LLM agent will
later assign every extracted name to exactly one category per axis you define,
and those assignments become the report's tables.

So the structure you produce is a measuring instrument. It has to be something
a careful annotator — human or model — can apply consistently to a name they
have never seen, using only the paper's own text.

## Your input

`domain_names.tsv` — every distinct research-topic name extracted from the
corpus, with how many papers mention it and one sentence of context. 2055 names
over 5990 paper-mentions. Read it. **1489 of the names appear in exactly one
paper**: the tail is not noise to be discarded, it is most of the vocabulary,
and your structure has to have somewhere to put it.

Work from this data. Do not reconstruct what you imagine a standard ML taxonomy
looks like and then check it against the data — read the data first, and let the
categories come from what is actually there.

## What to produce

A `proposal.tsv` with one row per category and these columns:

    axis | category | parent | scope_in | scope_out | example_children | notes

- **axis** — see the structural question below. Use a single value for all rows
  if you propose one tree.
- **category / parent** — `parent` empty for a top-level category.
- **scope_in** — one line: what belongs here.
- **scope_out** — one line: what a reader might wrongly put here, and where it
  goes instead. This column is where most of the value is.
- **example_children** — three labels **taken from the data** that would sit
  under this category at the next level down. If you cannot find three, the
  category is not real: merge it or drop it.
- **notes** — anything a reviewer needs, including your uncertainty.

Plus a short `RATIONALE.md`: the structural decision below, what you
deliberately excluded and why, and the three calls you are least sure about.

## The structural question you must answer

Is this **one tree**, or **several independent axes** a paper is labelled on
simultaneously? Decide, justify it from the data, and say what it costs.

Do not treat this as settled. It is the most consequential choice in the task
and we want to see it reasoned about, not assumed.

## Rules

1. **One concept per category.** No name of the form "X and Y" or "X, Y and Z".
   If two things genuinely belong together, find the name of the family that
   contains them both. If no such name exists, they are two categories.

2. **A name must be precise enough to repel what does not belong.** A category
   whose name is general enough to feel safe will attract out-of-scope entries
   and quietly corrupt the count. Test each name by asking what a careless
   annotator would file under it.

3. **A parent needs at least two substantive children.** A parent with one real
   child is just a rename of that child, and adds a level for nothing.

4. **Group by conceptual relatedness, not by frequency.** Two topics belong
   together because they are studied together, share methods, or answer the same
   question — never because merging them makes a tidier size.

5. **Do NOT balance category sizes.** This is the most important rule and the
   easiest to violate by instinct. We are measuring the proportion of research
   in each area; a structure engineered toward equal-sized categories destroys
   the very quantity being measured. A category holding 300 names and one
   holding 5 are both fine if that is what the field looks like.

6. **Watch the branching factor.** Many siblings at one level is usually a
   symptom: it means specialising too early and missing the relationships that a
   middle level would have expressed. There is no hard limit, but if a level has
   more than ~10 children, justify it or find the groupings you are missing.

7. **Depth 2 is the deliverable; depth 3 is how you validate it.** Propose the
   top two levels. The three example children per category are what demonstrate
   a category is real rather than plausible-sounding.

8. **Everything needs a home.** Before you finish, sample 30 names at random
   from the one-paper tail and check each one has an obvious category. Report
   how many did not — that number is a better quality signal than anything else
   you can measure. A residual "other" category is acceptable only if you state
   what fraction of paper-mentions lands in it.

## One judgement call to make explicitly

The extraction does not cleanly separate *research topics* from *model
architectures*: names like `Graph Neural Networks` and `Generative Models`
appear in this data as topics. State your policy — are model architectures
research topics here, a separate axis, or out of scope — and justify it. Note
that a separate ontology of model architectures already exists elsewhere in this
project, so counting them here risks double-counting and tilting the survey
toward architecture work.

## What we will do with three proposals

Two other people are answering this brief independently from the same data. We
will compare the three: categories that appear in all three are probably real,
categories that appear in one are probably taste. Write for that comparison —
be explicit about your reasoning so a disagreement can be traced to a premise
rather than a preference.

Do not hedge toward a safe middle. A clearly argued structure we reject is more
useful than a vague one we cannot evaluate.
