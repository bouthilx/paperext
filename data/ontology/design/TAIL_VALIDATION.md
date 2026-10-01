# Step 1: schema validation against the tail

Sample: `tail_sample.tsv`, seed 20260925 -- 50 names drawn from the 341 with
>=3 papers, 100 from the 1489 singletons. Each placed using only the tests in
`AXES.md`. ~120/150 placed cleanly. The 30 that strained fall into 9 findings.

This measures the **schema**, not the corpus: a name we cannot place is a
schema defect, not evidence the name is junk.

## Confirmed working

- **Multi-axis decomposition holds on real names.** `Protein Structure
  Prediction` -> Task>Prediction + Modality>Molecular + Application>Life
  sciences. `Node Classification` -> Task>Classification + Modality>Graphs.
  `Automatic Speech Recognition` -> Task>Recognition + Modality>Speech.
- **The OR ruling validates**: `Operational Research in Public Transportation`
  splits cleanly into Method (machinery) + Application>Industry (sector),
  exactly as the rule predicts.
- **Translate-don't-drop works** on `Protein Language Models` (-> Modality>
  Molecular), `Graph Positional Encoding`, `Transformers in Vision`.
- Cross-register `X in/for Y` names decompose without a residual:
  `Ethics in NLP`, `Data Augmentation in Medicine`, `Machine Learning for
  Climate Science`, `Privacy in Machine Learning`.

## F1. Method has no home for efficiency *techniques* (blocking)

`Model Pruning` 7, `Model Compression` 9, `Knowledge Distillation` 8,
`Model Quantization`, `Neural Network Pruning` 5 -- the owner ruled these stay
in the Method tree, but Method's five aspects (learning signal / training
regime / inference & optimization / model design & analysis / theory) have no
slot for them. Direct consequence of the Frugal AI ruling, missed when Method
was drafted.

Fix: either a sixth aspect **Model efficiency techniques**, or fold them into
Model design & analysis and rename it. Sixth aspect is cleaner -- pruning does
not study architecture, it shrinks one.

## F2. Method has no data-centric aspect (blocking)

`Label Cleaning`, `Learning with Noisy Labels`, `Data Quality and Metadata
Inference`, `Data Augmentation` 11, and arguably `Active Learning` 9 (currently
parked in Training regime). Data curation is a substantial research aspect with
no characteristic it matches.

Fix: aspect **Data curation & supervision quality**. This also settles the open
`Data Augmentation` question from section 3.

## F3. `Recurrent Neural Networks` translates to a node that does not exist

`AXES.md` section 5 gives `Recurrent Neural Networks` 8 -> Modality>Sequences,
but the modality axis has no `Sequences` -- it has `Time series & signals`, and
RNNs are used on text, audio and time series alike.

Fix: RNN implies no single modality, so it routes to **Method > Model design &
analysis**. Correct the example in section 5.

## F4. Contribution-type names have no disposal policy

`Benchmarking` 7, `Empirical Analysis of Algorithms`, `Multimodal Model
Evaluation`, `Patient Decision Aids Evaluation`. Section 1 rejects contribution
type as an axis but never says where such names *go*. Presumably `mark_ignore`,
but unwritten rules get improvised by annotators.

## F5. Generic names need a per-axis "too generic" policy

`Predictive Modeling`, `Event Classification`, `Optimization Techniques`,
`Computing Research`. Each is on-axis but carries no information. The
uninformative branch currently exists only for `Machine Learning` /
`Deep Learning`; every axis needs the same escape.

## F6. Missing application branch: linguistics, psychology, humanities

`Linguistic Semantics`, `Personality and Social Psychology`, `Lifespan
Development`, `Theory of Mind`. Neither `Society, policy & education` nor
`Neuroscience & cognitive science` is right for linguistics, and psychology
straddles the two.

## F7. Homonyms across axes

`Policy Evaluation` -- off-policy evaluation in RL vs evaluation of public
policy. `Compression Algorithms` -- data compression vs model compression.
The surface map is per-axis so each can be resolved, but the design must flag
homonyms rather than discover them mid-run (v0's ambiguity probe exists for
exactly this).

## F8. Corpus compound names spanning two siblings

`Fairness and Interpretability in Machine Learning`, `Probability and
Statistics`, `Task and Motion Planning`, `Human Factors and Ergonomics`. Our
rule bans compound *category* names but says nothing about compound *surface*
names, which the corpus is full of. Policy needed: map to the parent, or to the
dominant sibling.

## F9. Generalization and OOD -- RESOLVED

`Compositional Generalization`, `Out-of-Distribution Generalization` 5,
`Domain Generalization` 4, `Generalization` 3 -- ~35 mentions with the theory
names -- go to **Method > Learning theory & generalization** (the renamed
Theory & analysis aspect), not to Desired properties.

The line: Desired properties are **demands from outside the research**;
generalization is a **question the field asks about its own machinery**.

`Out-of-Distribution Detection` 12 splits three ways once you ask *why detect
it* -- you detect it to abstain or flag before acting on an input you should
not trust:

| concept | axis |
|---|---|
| distribution shift (the phenomenon) | Method > Learning theory & generalization |
| OOD detection (the activity) | Task > Detection |
| robustness to shift (the demand) | Desired properties > Trustworthy > Robustness |

One string, three concepts, three axes -- the faceted design doing its job.
`Domain Adaptation` 10 is a neighbour but not the same thing: adapting across
domains is a **Training regime**, not a claim about generalization.

## F6. Application branch -- CORRECTED

The first fix invented a branch called "Language, mind & behaviour", which
matches no existing classification system. Replaced by renaming
`Society, policy & education` to **Social & behavioural sciences**, following
ACM CCS ("Law, social and behavioral sciences"); psychology is filed there in
LCC (BF), Dewey (150) and OECD FOS (5.1) alike. Linguistics is genuinely
contested -- OECD and LCC put it in Humanities, Scopus lists it in both -- and
is filed here with a flag.
