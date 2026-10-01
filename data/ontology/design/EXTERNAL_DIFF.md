# Step 2: diff against external classifications

Two sources reached, one deferred.

- **arXiv primary categories** -- 810 of 1742 corpus papers carry an arXiv id
  (47%). Random sample of 200 (seed 20260928), 183 resolved, in
  `arxiv_primary_sample.tsv`.
- **ACM CCS 2012**, `Computing methodologies` subtree.
- **Papers With Code** task taxonomy -- deferred to the Task axis build.

## Scope limit on arXiv, stated before the numbers

arXiv is usable **only for the CS-side axes**. Health & medicine is the largest
application branch by name mentions (544) but q-bio + eess.IV together are ~3%
of the arXiv sample, because clinical work does not post to arXiv. Any use of
arXiv to check the application axis would read that absence as evidence. It is
not.

Also: arXiv gives one primary label per paper against our ~3 names per paper, so
only *ratios* between categories are comparable, never absolute shares.

## arXiv findings

| category | share | reading |
|---|---|---|
| cs.LG | **47.0%** | Half the arXiv-visible corpus is primary-category "machine learning" -- no modality, no application. Direct support for Modality and Application being **optional** axes whose blanks are findings, and for the RL-takes-no-modality ruling |
| cs.CL | 12.0% | |
| cs.SE | 6.6% | Third-largest. Bigger than all of vision |
| math.OC | 4.4% | Consistent with Inference & optimization being a large aspect |
| cs.CV (+eess.IV, cs.GR) | 5.4% | |
| cs.AI · cs.IR · cs.RO | 2.2-2.7% each | |
| cs.LO | 1.1% | **blind spot, see below** |
| cs.NE | 0.5% | **blind spot, see below** |

**Divergence worth investigating: the language/vision ratio inverts.** arXiv
puts cs.CL at ~2.2x the whole vision cluster. Our corpus *names* put `NLP` 295
against `Computer Vision` 240 (1.2:1), and our modality branch sizes make Vision
(~563) **larger** than Language (~522). Two structures disagree about which is
the bigger research area. Most likely explanation: `Computer Vision` is being
used as a generic descriptor in the name extraction more often than it names the
paper's actual subject. Not resolvable from here, but it means the Vision branch
size should not be trusted until the mapping runs.

**cs.SE at 6.6%** is larger than vision, yet under OECD-6 software engineering
sits two levels down (Natural sciences > Computer & information sciences >
Software engineering). That is a cut-placement question, not a structural one --
`NodeCut` matches node ids, so the report cut can sit deeper in that branch than
elsewhere -- but it has to be a deliberate choice.

## ACM CCS findings

**First, the important one: ACM CCS fails our own granularity audit.** Under
`Machine learning`, these are siblings: `Supervised learning` (a paradigm),
`Machine learning approaches` (a grouping of model families), `Machine learning
algorithms` (holding Q-learning, boosting, cross-validation), `Markov decision
processes` (a formalism), and `Bio-inspired approaches`. Paradigm, grouping,
algorithm and formalism at one level.

So ACM CCS **cannot arbitrate for Method the way OECD FOS arbitrated for
application**. It supplies vocabulary and exposes blind spots; it is not a
cleaner structure than ours. That is a real answer to the worry that started
step 2: for the AI side there is no standard that is better-principled than what
we derived, only standards that are broader.

**Confirms M1 (learning theory is a different kind).** ACM does not put learning
theory under Computing methodologies at all -- it lives under `Theory of
computation > Machine learning theory`. An independent classification made the
same cut the granularity audit made.

**Three blind spots, two of them confirmed independently by arXiv:**

1. **Bio-inspired / evolutionary computation** -- ACM has genetic algorithms,
   genetic programming, artificial life, evolvable hardware, evolutionary
   robotics. We have **nothing**, on any axis. arXiv's cs.NE agrees.
2. **Logical, relational and inductive-logic learning** -- ACM has a whole
   subtree. We have nothing; the method derivation already reported
   `Neural-Symbolic Learning` as unplaceable. arXiv's cs.LO agrees.
3. **Classical AI beyond learning** -- knowledge representation & reasoning
   (description logics, nonmonotonic reasoning, ontology engineering, logic
   programming), planning & scheduling, and search methodologies (heuristic,
   game-tree, randomized search). Our Method axis is **ML-shaped, not AI-shaped**.
   This is the largest gap and neither the corpus nor our derivation could have
   surfaced it, because the institute does little of it *this year*.

**Where we are ahead of the standard, defensibly**: `Data curation & supervision
quality` and `Model efficiency techniques` have no ACM counterpart -- both
postdate CCS 2012. Divergence here is not a defect.

**A design contrast, not a defect**: ACM files `Computer vision` and `Natural
language processing` under *Artificial intelligence*, as siblings of `Machine
learning` -- i.e. as methodology areas, not as data types. We treat them as
modalities. Worth holding next to the language/vision ratio anomaly above.
