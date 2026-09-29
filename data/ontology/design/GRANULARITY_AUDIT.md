# Step 1: granularity audit of the four delivered axes

Test, applied to every sibling set (owner's, 2026-09-28): **are these the same
kind of thing, at the same level of specificity, and does any sibling exist only
because it was large in this corpus?**

Motivation: the application axis's level 1 failed this test against OECD FOS --
`Neuroscience` was a top branch at 84 mentions while `Chemistry` was not at 43,
i.e. granularity was set by corpus volume rather than by a principle. The
concern is that the same defect is present on the AI-side axes where no external
standard exists to expose it. It is.

Verdict: **Properties clean · Method 7 defects · Modality 5 defects ·
Application superseded** by the OECD-6 re-derivation.

## Method

**M1 (root, register mismatch).** Five aspects are stages of building a model
(learning signal, training regime, data curation, inference & optimization,
model design); `Learning theory & generalization` is a **kind of claim**. Not
the same kind of thing.

**M2 (learning-signal, granularity).** `Supervised / Unsupervised /
Self-supervised / Reinforcement` is the field's classic four-way partition by
supervision signal. `Learning from human feedback` is normally a *specialisation
of* RL or supervised learning, promoted here to sibling. Not volume-driven (23
mentions vs supervised's 28) but still a level mismatch. Also **missing**:
semi-supervised and weakly-supervised learning, both classic, both absent.

**M3 (training-regime, admitted misfit).** `Constrained learning` does not
satisfy the branch's own characteristic ("how training is organised across
tasks, time and agents") -- it is a modification of the *objective*, not of the
organisation. The deriving agent flagged this itself. Belongs in Inference &
optimization.

**M4 + M5 (inference-optimization, four principles in one sibling set).**
- by variable type: `Continuous optimization`, `Combinatorial optimization`
- by inferential framework: `Probabilistic inference`, `Causal inference`,
  `Game theory`
- by **problem class**: `Sequential decision-making` -- an MDP is a problem
  formulation, not machinery, and it overlaps `Reinforcement learning` on the
  learning-signal branch
- by **stage**: `Inference-time methods` (prompting, RAG, test-time compute) --
  divides by *when* computation happens, not by what machinery does it

This is the worst sibling set on the axis and the clearest instance of the
defect the audit was looking for.

**M6 (learning-theory, granularity).** `Statistical learning theory` is a
discipline-sized node; `OOD generalization`, `Compositional generalization` and
`Scaling behaviour` are topic-sized. A sibling set spanning two orders of
specificity.

**M7 (data-curation, unstated principle).** `Data augmentation`, `Synthetic
data`, `Data selection`, `Data quality`, `Dataset construction` overlap rather
than partition -- augmentation and synthetic data both *create* data, selection
and quality both *curate* it, and construction spans both. The principle is
never stated.

**Already fixed**: `Model design & analysis` held both design and analysis; the
split into Model design / Model analysis is in AXES.md but postdates this file.

## Modality

**D1 (root, three kinds fused).** Confirmed from the earlier spot-check:
- sensory signal kinds: Vision & imaging, Language & text, Speech & audio
- structural kinds: Graphs & relational, Time series & signals, Tabular records
- **domain-derived**: `Molecular & biological data` -- a *field's* data promoted
  to a signal kind because this institute does a lot of biology (306 mentions).
  Structurally, molecules are graphs plus 3D geometry.

`Multimodal` is a fourth kind (a combination), but it is explicitly declared and
argued in AXES.md, so it stands.

**D2 (vision, two principles).** `Natural / Biomedical / Remote-sensing /
Document imagery` divide by **capture instrument or subject**; `Video` divides
by **temporal structure**; `3D geometry` by **dimensionality**. The deriving
agent reported this and declared a two-clause characteristic rather than fixing
it.

**D3 (language).** `Written text` and `Conversational language` divide by
register; `Source code` is a kind of language; `Multilingual text` is a
**property** (how many languages), not a kind of text -- it cross-cuts all three
siblings.

**D4 (graphs, mild).** `Knowledge graphs` and `Social & information networks`
divide by what the graph represents; `Temporal graphs` by whether it changes.

**D5 (systemic -- cross-axis leak, the important one).** Several branches divide
their level 2 by **application domain**, which is another axis:
- time series: Physiological / Environmental / Financial / Sensor streams
- tabular: Electronic health records / User interaction records
- multimodal: `Multimodal biomedical data`
- vision: `Biomedical imagery`, `Remote-sensing imagery`

Where a modality branch's children are named by the field the data comes from,
that branch is reproducing the Application axis inside itself. Some of this is
unavoidable (an instrument *is* defined by its use), but it needs a stated rule
rather than happening silently.

## Properties -- clean

Root (Trustworthy / Frugal / admin) is one principle: which kind of external
demand. `Trustworthy AI`'s six children divide by **which mode of trust failure
the work forestalls** -- discrimination, leakage, failure under shift, harm,
opacity, absence of recourse -- and that holds across all six without strain.
`Frugal AI`'s three divide by resource, with a mild overlap between
computational and hardware cost (compute cost largely *is* hardware time).

This is the axis that was redesigned most deliberately, and it is the one that
passes.

## Application -- superseded

Level 1 failed the test; that is what prompted the OECD-6 decision. Not audited
further since it is being re-derived at depth 3 against OECD's own two levels.
