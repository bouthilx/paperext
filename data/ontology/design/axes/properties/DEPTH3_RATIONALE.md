# Desired properties axis: depth-3 derivation

Derived 2026-09-29 from `AXES.md` §2 and §9 (authoritative), `GRANULARITY_AUDIT.md`,
and the depth-2 tree in `nodes.tsv` / `RATIONALE.md`. Level 1 and level 2 were
fixed inputs and no existing row was modified.

The procedure in §9 is ordered and the order is the deliverable as much as the
tree is. `DRAFT_PHASE1.md` holds the semantic draft, written before
`domain_names.tsv` was opened; this file holds the corpus check and the diff.

---

## 0. Procedural record, including where it was compromised

**Phase 1** (semantic, no corpus access). Wrote each expanded node's
characteristic first, then its children, from the field's own structure and the
parent's own characteristic. `DRAFT_PHASE1.md` written and timestamped
**2026-09-29T12:03:02-04:00**, before any read of `domain_names.tsv` and before
any tally. That file has not been edited since.

**Phase 2** (corpus check, two questions only). Read `domain_names.tsv` with a
plain tab split, 2055 name rows. Asked exactly: *is there a cluster with no
node* (blind spot → add or justify) and *is there a node with no support*
(keep → flag speculative). No other question was asked and no other change was
made.

**Phase 3** is this file plus the 23 appended rows.

### Declared contamination

The brief required `nodes.tsv` and `RATIONALE.md` to be read before phase 1, for
the parents' characteristics. Both are corpus-laden — `nodes.tsv` is a TSV, so
its `examples` and count columns are visible in any read of it, and
`RATIONALE.md` §4–§8 enumerates several hundred corpus surfaces with mentions. I
could not obtain the parents' characteristics without seeing them. I did not
consult either while drafting, ran no tally, and opened no name list. The
honest check on whether the `examples` cells anchored the draft is the
coincidence rate, so here it is, child by child:

| parent | its `examples` cell | my phase-1 children | verdict |
|---|---|---|---|
| Fairness | Group fairness criteria · Bias mitigation in LMs · Fairness in ranking and recommendation | Group · Individual · Representational | 1 of 3 coincides; the cell's other two are the *mitigation* and *task* cuts my draft explicitly rejects as principles |
| Robustness | Adversarial · Distribution-shift · Certified | Adversarial · Training-data integrity · Distribution-shift | 2 of 3 coincide; **`Certified` is rejected outright** as a guarantee-register import |
| Explainability | Post-hoc for deployed models · Intrinsically interpretable models · Right-to-explanation and disclosure | Intrinsic · Post-hoc · Recourse and contestability | 2 clear, 1 near |
| Privacy | Differentially private learning · Membership inference and memorization · Machine unlearning | Training-data confidentiality · User-input confidentiality · Data subject control | **0 of 3 coincide** — the cell lists three *mechanisms*, my draft divides by claim |
| Safety | AI alignment · Safe RL · Risk-sensitive control | Alignment · Safe control · Output safety | 1 coincides, 2 of the cell's collapse into my `Safe control`, and my `Output safety` is absent from the cell |
| Accountability | AI regulation and standards · Algorithmic auditing · Model documentation and provenance | Regulatory compliance · Auditability · Traceability | 3 of 3 coincide — these are simply the field's three governance terms |
| Computational cost | Inference latency · Communication-efficient training · Training-compute budgets | Training compute · Inference cost · Communication cost | 3 of 3 |
| Energy cost | Carbon footprint accounting · Energy-aware training · Sustainability reporting | Energy consumption · Carbon footprint | cell's three collapse into my two |
| Hardware cost | On-device/TinyML · Accelerator-aware design · Edge inference | **leaf** | the cell is *rejected* as three devices, not three demands |

Two cells were rejected wholesale (Hardware, and Privacy's mechanism list), one
child in a cell was rejected on principle (`Certified`), and one child was added
that no cell contains (`Output safety`). That is not the fingerprint of a draft
copied from the cells. Where the sets do coincide (Accountability, Computational
cost) the reason is visible in the draft's own argument — those are the field's
standard terms and any honest derivation reaches them. Reported so the reader can
discount it; this is a real weakness of running phase 1 after a mandated read of
corpus-laden files, and it should be fixed for the next axis by splitting the
characteristics into a separate file.

### On the count columns

`corpus_names` and `corpus_mentions` are left **empty on every level-3 row**, and
support is recorded qualitatively in `notes` instead. Filling them would require
a per-child tally, and a per-child number in a count column is precisely the
artefact that later gets used to balance a sibling set — the thing §9 forbids.
Counts are indicative, not measured (issue #89), and a level-3 tally would be
less measured than the level-2 one.

---

## 1. The delivered tree

```
Trustworthy AI
  Fairness             → Group fairness · Individual fairness · Representational fairness
  Privacy              → Training-data confidentiality · User-input confidentiality · Data subject control
  Robustness           → Adversarial robustness · Training-data integrity · Distribution-shift robustness
  Safety               → Alignment · Safe control · Output safety
  Explainability       → Intrinsic interpretability · Post-hoc explanation · Recourse and contestability
  Accountability       → Regulatory compliance · Auditability · Traceability
Frugal AI
  Computational cost   → Training compute · Inference cost · Communication cost
  Energy cost          → Energy consumption · Carbon footprint
  Hardware cost        → LEAF (deliberate)
Uninformative          → LEAF (administrative)
```

23 level-3 nodes under 8 expanded parents; 1 substantive leaf declared.

---

## 2. Phase 1 → phase 2 diff

**No change. Zero nodes added, zero removed, zero renamed, zero merged, zero
split, zero reordered.** The delivered tree is the phase-1 draft verbatim.

This is the intended outcome of the procedure rather than a lucky one: the two
questions phase 2 is allowed to ask can only *add* a node (blind spot) or *flag*
one (no support). Six blind-spot candidates were examined and all six were
refused with reasons (§3); six nodes were found unsupported and all six were
kept and flagged (§4). Nothing else was licensed, and nothing else was done.

The only thing phase 2 changed is **text**: every level-3 row's `notes` field
was written after the corpus check, and the negative tests were populated with
the specific surfaces each boundary has to repel. Characteristics, names,
positive tests and the sibling sets themselves are as drafted.

---

## 3. Blind spots: six clusters examined, six refused in writing

A corpus cluster with no node must be added *or justified*. All six are
justified refusals, and each one is refused by a rule that predates the count.

**3.1 Bias mitigation** — `Bias Mitigation` 6, `Bias Mitigation in Machine
Learning` 2, `Debiasing` 1, `Fairness Algorithms` 1 (~10 mentions). This is the
third-largest concentration on the Fairness branch and it has no node.
**Refused.** It names a *mitigation*, not a form of inequality; a node for it
would divide Fairness by mitigation stage, which is Method's characteristic and
is forbidden by name in both the brief and §9. These surfaces map to the
`fairness` branch node by the §8b nearest-common-parent rule, exactly as
`AI Ethics` maps to `trustworthy-ai`. That this is the largest refused cluster on
the axis is the clearest illustration of the rule doing work: ~10 mentions were
not enough to buy a node that divides by the wrong question.

**3.2 Adversarial detection** — `Adversarial Detection` 3, `Adversarial Attack
Detection` 2, `Adversarial Examples Detection` 1, `Textual Adversarial Attack
Detection` 1 (7). **Refused.** Detecting an attack is a *task*, not a mode of
trust failure; these map to `Adversarial robustness` on this axis and to
Task > Detection on that one, which is the faceted design working as intended.

**3.3 Certified and verified robustness** — `Certified Robustness` 1,
`Robustness Verification` 1. **Refused**, and this refusal was written in phase 1
before the count was known. Certification divides by *guarantee register*, i.e.
by what is established about a model that already exists, which is verbatim the
characteristic of Method > Model analysis; `Neural Network Verification` 5 is
already routed there. It also fails the property test — certified adversarial
robustness and certified shift robustness both exist, so `certified` is a
modifier true of siblings.

**3.4 Fairness in ranking and recommendation** — `Fairness in Ranking` 2,
`Fairness in Recommender Systems` 1. **Refused.** It divides by the *task* in
which the fairness demand arises. Ranking fairness can be group, individual or
representational, so by the property test the task is a modifier, not a sibling.
Mapped to `Group fairness` (exposure between groups) with the Task axis carrying
the rest.

**3.5 Scalability** — `Scalability in Deep Learning`, `Scalability in Graph
Neural Networks`, `Scalable Graph Neural Networks`, `Scalable Machine Learning`,
`Scalable Reinforcement Learning` (~5). **Refused.** Scalability is a modifier
true of training, inference and communication alike, and the parent node already
declared that it sometimes means graph size rather than budget.

**3.6 Safety–governance compounds** — `AI Safety and Regulation` 2, `AI Safety
and Governance` 1, `Model Safety, Ethics in AI` 1. **Refused.** These are
compound *surfaces*, which §8b permits and routes to the nearest common parent —
here `trustworthy-ai`, since they span children of two different level-2 nodes.
No new node.

**Nothing else.** A sweep for demand-register surfaces outside the nine parents
found only the assurance cluster (`Uncertainty Estimation` 12, `Uncertainty
Quantification` 5, `Neural Network Verification` 5, `Model Calibration` 2,
`Conformal Prediction` 1, ~34 mentions) and the human-centeredness pair
(`Human-Centered AI` 1, `Usability` 1, `Accessibility` 1). Both were adjudicated
at **level 2** — RATIONALE §5.2 and §9 — and level 2 is a fixed input here. They
are not depth-3 blind spots and this derivation does not reopen them.

---

## 4. Nodes with no corpus support: six, all kept and flagged speculative

Rule 9: a category with no corpus support is *possibly speculative, justify or
keep* — never deleted. Each is flagged in its row's `notes` and justified there;
the short form:

| node | support | why it is kept |
|---|---|---|
| `Individual fairness` | zero | one of the two canonical answers the field gives to "what makes this unfair"; without it `Group fairness` is an only child and divides nothing |
| `Recourse and contestability` | zero | the whole case for Explainability being on this axis is that regulators, clinicians and applicants demand explanations. **This node is where that claimant lives.** Deleting it removes the branch's warrant for membership while keeping the branch |
| `User-input confidentiality` | zero | the only child holding the deployment-side privacy claimant; the same frontier-LLM hole RATIONALE §7 already documented for Safety, found a second time |
| `Output safety` | zero | the parent's positive test names "produces harmful output" as one of its three cases; deleting the node leaves a clause of the parent's own characteristic with no child to discharge it |
| `Traceability` | zero | the precondition of answerability that the AI Act, NIST AI RMF and ISO 42001 all mandate; the parent is itself kept on semantics, not count, for the same reason |
| `Carbon footprint` | zero | AXES.md §2 builds the entire case for a separate properties axis on the Green-AI / energy-sector collision. Deleting this node deletes the axis's founding example one level down |

Three further nodes are **thin rather than empty** and are noted as such:
`Training-data integrity` (2), `Inference cost` (~2), `Energy consumption` (1),
`Data subject control` (2), `Auditability` (~4).

The pattern is worth stating as a finding rather than a defect: **every
unsupported node is a demand made by a regulator or by a generative-model-era
claimant.** Five of the six are governance or LLM-safety nodes. A 2024
single-institute corpus of extracted *research domains* is exactly the instrument
that would not see them, and the axis's own rationale predicted four of the six
before this derivation began.

---

## 5. Each expanded node: its characteristic and the principle rejected

| node | characteristic (level 3) | principal competitor rejected | second competitor |
|---|---|---|---|
| Robustness | where the departure comes from — who or what authors the disturbance | **guarantee register** (empirical/certified/verified): Method > Model analysis's own question, and a modifier by the property test | perturbation geometry (Lp/semantic/patch): a threat-model taxonomy, machinery register |
| Fairness | which form the inequality takes — what was distributed unequally, and across whom | **mitigation stage** (pre/in/post-processing): Method's question, forbidden by name; the axis's historical absorption route | by protected attribute (gender/race/language): fragments without limit and cross-cuts every child |
| Explainability | what the owed account is about — the model, an output, or the person's position | **explanation technique family** (attribution/surrogate/example/concept): Method > Model analysis verbatim | local vs global scope: a property of the explanation artefact, and it cross-cuts |
| Privacy | which of the data subject's claims fails | **privacy mechanism** (DP/crypto/federated/anonymisation): Method's question, and mechanisms cross-cut | attack vs defence: a *register* split, which would separate membership inference from DP although they are one claim seen twice |
| Safety | what the system gets wrong while working as built — objective, actions, or outputs | **severity / time horizon** (near-term vs existential): divides the safety *community*, not the system's failure; cross-cuts | who is harmed (user/bystander/society): Sector's claimant structure imported |
| Accountability | which precondition of answerability is missing | **governance instrument** (law/standard/voluntary code): a fact about the regulatory landscape, not a mode of failure; instruments cross-cut | — |
| Computational cost | which computation is paid for | **the metric used** (FLOPs/wall-clock/memory): divides by how the cost is counted, not which cost is incurred | — |
| Energy cost | which quantity is budgeted — joules or emissions | **by mitigation** (efficient architectures / scheduling / offsetting): Method's question | — |
| Hardware cost | — (leaf) | **which device** (edge/mobile/TinyML/datacenter): a deployment context, i.e. Sector's question; and magnitude is not a principle | |

### Leaves declared

- **`Hardware cost` — leaf, on principle.** Every candidate subdivision divides
  by *which device*, which is a deployment context rather than a resource, and a
  phone's NPU and a datacenter GPU impose the same demand at different
  magnitudes. The one other candidate — *fit a given chip* vs *co-design the
  chip* — is already settled by the node's own negative test, which sends
  hardware-design-as-a-subject to Application, so only one side of the pair is
  in scope. The corpus check independently agreed: all four surfaces
  (`Hardware Acceleration` 4, `Neural Network Acceleration` 1, `Edge Computing`
  1, `Mobile Edge Computing` 1) assert the same single demand and none
  distinguishes a sub-kind. Note this was decided in phase 1; the corpus merely
  failed to disturb it.
- **`Uninformative` — leaf**, administrative and deliberately empty, unchanged.

### Children considered and not created, in writing

- **`Human oversight`** under Accountability. Under this characteristic it is a
  genuine fourth missing precondition (no responsible human), and the EU AI Act
  makes it a requirement in its own right. Folded into `Regulatory compliance`'s
  positive test because as a node it collides with Safety and with
  Application > HCI, and `Human-in-the-loop` is predominantly a Method surface,
  so the node would attract out-of-scope entries — which §9 forbids. **The
  likeliest fourth child.**
- **`Lifecycle and embodied footprint`** under Energy cost (hardware
  manufacture, datacenter water, e-waste). Declined because it sits one step
  from Application > environment and the reflexive test gets genuinely hard when
  the object of study is a building. **Not** declined for thinness — both
  delivered siblings are thin too. The likeliest third child.
- **`Memory cost`** as a fourth child of Computational cost. Declined: training
  memory is part of a training run's budget and serving memory is part of the
  per-query budget, so it is a *metric* spanning two children rather than a
  fourth computation, and the footprint-on-a-device reading is Hardware cost.

### One level-2 decision revisited without being reopened

RATIONALE §5.1 declined a Robustness-vs-Security split at level 2, calling the
distinction "conceptually real" but rejecting the split for three reasons, two of
which were naming accidents: `Robustness & adversarial security` is a banned
compound, and the §8b head-noun rule hands the flagship surface
`Adversarial Robustness` to the robustness side. **Both evaporate one level
down.** `Adversarial robustness` and `Training-data integrity` are not compounds,
keep their head nouns, and do not collide with Application > Computer security.
The conceptual content §5.1 wanted is recovered at depth 3 without disturbing the
level-2 node, which is the shape §5.1 itself predicted ("revisit if …").

---

## 6. My own granularity audit

Test (owner's, 2026-09-28): *are these the same kind of thing, at the same level
of specificity, and does any sibling exist only because it was large in this
corpus?*

### The volume question — the one this procedure was designed to answer

**No sibling on this axis exists because of its size, and the file can prove it
rather than promise it.** Every level-3 set was written before any count was
seen, and six of the 23 nodes have zero corpus support while the largest refused
cluster (bias mitigation, ~10 mentions) got no node at all. If volume had leaked
into the shape, the inverse would show: a `Bias mitigation` node and no
`Recourse` node. Volume was used for exactly one thing — the order in which the
nine parents were opened, which §9 permits.

### Sibling-set verdicts

| set | same kind? | same specificity? | verdict |
|---|---|---|---|
| Robustness ×3 | yes — three sources of the departure | yes | **pass** |
| Fairness ×3 | *see strain F-1* | yes | **pass with declared strain** |
| Explainability ×3 | yes — three objects of the owed account | yes | **pass** |
| Privacy ×3 | yes — three claims of the data subject | yes | **pass** |
| Safety ×3 | yes — objective / actions / outputs | yes | **pass** |
| Accountability ×3 | yes — three preconditions of answerability | yes | **pass** |
| Computational cost ×3 | *see strain F-2* | yes | **pass with declared strain** |
| Energy cost ×2 | yes — two quantities, two claimants | yes | **pass** |

### Sets I am not confident in — declared, not concealed

**F-1 (Fairness, moderate).** `Group` and `Individual` divide by the *comparison*
that exposes the wrong; `Representational` divides by the *kind of good* at stake
— a depiction rather than a decision. I read the stated characteristic ("what was
distributed unequally, and across whom") as covering both, but a reader who
scores this as one-and-a-half principles is not being unreasonable. **This is the
weakest sibling set I am delivering.** The alternative — a clean two-child set of
Group and Individual — would exclude the entire generative-model fairness
literature, which is where the field is moving and which the node has to survive
into. Declared in the draft before the corpus was opened and unchanged since.

**F-2 (Computational cost, mild).** Training-vs-inference can be read as a
division by *stage*, which is defect M5 on the Method axis re-entering one axis
over. My defence is that these are two budgets with two payers and
incommensurable units (one-off GPU-hours versus cost per query), which is the
grandparent's "which resource" question and not "when the computation happens".
I believe it, and I record it so a reader can disagree.

**F-3 (Robustness, naming).** `Training-data integrity` is **narrower than its
own positive test**: Byzantine gradient tampering corrupts the training
*process*, not the training *data*, and `Byzantine Robustness` 1 is in the
corpus. `Training-process integrity` is the better name. **I did not apply it**,
because the §9 procedure licenses only two corpus-driven changes — add a
blind-spot node, flag an unsupported one — and a rename is neither. Flagged for
the owner; it is a one-word fix that needs an authorisation this procedure does
not grant me.

**F-4 (Safety, homonym exposure).** `Safe control` carries the `control`
homonym, already declared on this axis for `Control Systems` / `Control Theory`
(~40 mentions split between Method and Application). The `Safe` modifier protects
it, but it is the level-3 node most likely to attract out-of-scope entries at
mapping time.

**F-5 (Explainability, live boundary).** RATIONALE §4 flagged `Interpretable
Machine Learning` 9 and `Interpretable Models` 2 as readable either as the demand
or as the glass-box technique family. Creating `Intrinsic interpretability` turns
that flag into a **live boundary between a node and Method**, worth ~11 mentions.
The ambiguity probe should carry it.

### Does the axis still pass the granularity audit?

**Yes, and level 3 is the least strained level on it.** The root and level 2 are
untouched, so the audit's "Properties — clean" verdict stands there by
construction. At level 3: no sibling set mixes two questions the way
`Inference & optimization` mixes four (M4/M5); no set spans two orders of
specificity the way `Learning theory` does (M6); no set overlaps rather than
partitions with an unstated principle (M7) — every principle is stated in the
`characteristic` column of every row; no branch divides itself by application
domain (D5). The two strains above are both *within one principle read
generously*, not two principles fused, and both are declared in the row itself
rather than in a file the mapper will not read.

The audit's one recorded weakness on this axis — "a mild overlap between
computational and hardware cost (compute cost largely *is* hardware time)" — is
**not repaired and is slightly sharpened**: `Inference cost` (serving memory,
latency) and `Hardware cost` (fitting the device) now abut directly. Both nodes'
negative tests point at each other explicitly, which is the best available
mitigation short of merging them, and merging them is a level-2 change this
derivation may not make.

### Branching factors

| level | factors | mean | max |
|---|---|---|---|
| 1 | 3 (2 substantive + 1 administrative) | — | 3 |
| 2 | 6, 3 | 4.5 | 6 |
| 3 | 3,3,3,3,3,3,3,2, and one declared leaf | 2.9 | **3** |

Level 3 is the flattest level on the axis and the most uniform. §9 warns that
many siblings means specialising too early; a max of 3 is comfortably inside
that. Total axis: 3 + 9 + 23 = 35 nodes, of which 1 is administrative and 1 is a
declared substantive leaf.

---

## 7. What a reader should not conclude from this file

- **Not that the level-3 shares will be reportable.** Six nodes are empty and a
  further five are near-empty, and a large share of each expanded branch's mass
  sits on the *branch node* as an umbrella (`Fairness in Machine Learning` 19,
  `Explainable AI` 10 + variants, `Privacy-Preserving Machine Learning` 4, and
  the 38 `AI Ethics`-class mentions on `trustworthy-ai` itself). §8b already
  requires depth-2 shares to be stated against a denominator naming the
  branch-level bucket; at depth 3 that requirement is **much stronger**, and a
  depth-3 report on this axis that does not state it will be wrong.
- **Not that the empty nodes are a defect.** They are the axis's finding: this
  institute's 2024 output contains essentially no governance, documentation,
  recourse or LLM-output-safety research, while it contains a great deal of
  adversarial robustness and fairness. That contrast is only visible because the
  nodes exist to be empty.
- **Not that the cut should sit at depth 3.** `NodeCut` matches node ids, not
  depth (§7). On this axis the informative cut is depth 3 under Robustness,
  Fairness and Explainability, and depth 2 nearly everywhere else.
