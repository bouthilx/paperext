Frozen: Tue Oct  6 04:22:42 PM UTC 2026

# Algorithms dimension — phase 1 draft (B)

Derived from field knowledge only. No corpus, no existing ontology, no candidate
list was consulted.

## The shape and why

### The shape

**A faceted dimension: ten role axes plus one crosscutting axis.** Each axis is a
tree with one stated principle of division per sibling set, and lineage chains
(descent) at its leaves. An algorithm takes a value on *one or more* axes;
having no value on an axis is the normal case, not a gap.

| axis | one-line scope |
|---|---|
| `DAT` | what the run does to a given data source before or while the learner consumes it |
| `EXP` | how the run obtains training experience by interacting with something |
| `OBJ` | what quantity defines "better", and where its teaching signal comes from |
| `FIT` | how parameter values are produced |
| `EST` | what quantity the run estimates, and what licenses the estimate |
| `ADP` | which parameters the procedure is permitted to change |
| `SRCH` | what non-parameter choice the run varies and selects |
| `EXEC` | what the run partitions, defers, approximates or walls off to fit the hardware and the data boundaries |
| `PTX` | what is changed about an already-fitted model, after fitting |
| `OUT` | how the delivered output is produced at fixed parameters |
| `MACH` | crosscut: the computational strategy the procedure runs on |

The one-sentence argument: **the co-occurrence sibling test (rule 2) is a proof
that this dimension cannot be a single tree, because the only level-1
characteristic that survives the use-test is "which station of the run the
procedure fills", and the stations co-occur in every single run — Adam with
CutMix with beam search — so they cannot be siblings, so they cannot be children
of one root.**

### The proof, stated carefully

Rule 2 says two algorithms that run together in one run cannot be siblings.
Suppose a single tree whose root divides by role/station. Then `Data
preparation`, `Objective`, `Parameter update` and `Decoding` are siblings. But
every supervised-LLM run executes something from all four at once. Contradiction.
So either the level-1 characteristic is something other than role, or the
dimension is faceted. Section "What I killed" shows every non-role candidate
fails. Therefore: faceted.

This is not a presentational choice. In a tree, **siblings are alternatives**; in
this dimension the top-level groups are **co-participants**. A root whose
children are non-exclusive by construction is not a root — it is an axis set.

### The functional reading of rule 2 (needed, or the rule eats itself)

Taken literally, rule 2 destroys any structure at all: people stack RandAugment
*and* Mixup *and* CutMix in one run, so even those three could not be siblings.
The operative reading must be functional:

> Two nodes may be siblings only if an annotator can ask **"which one did this
> run use for X?"** with a *single* X, and the answers compete for that X.

Mixup and CutMix both answer "how are labelled examples perturbed?" — they are
alternatives that happen to compose. Adam and CutMix answer different questions.
Composability within a slot is allowed; cross-slot pairing is not. Every sibling
set below is checked against this reading, and I say where it strains.

### Why the stations are axes and not branches: the orthogonality instrument

The brief's own worked failure is a station confusion. "Reinforcement learning"
is a claim about **where the experience comes from** (`EXP`); "self-supervised"
is a claim about **where the training signal comes from** (`OBJ`). `SPR` and
`ConSpec` agree on `EXP` (off-policy replay from environment interaction) and
differ on `OBJ` (self-prediction vs contrast). By the orthogonality test that
makes `OBJ` an axis, not a level under `EXP`. The same test fires repeatedly:

- `PPO` and `A2C` agree on `EXP` (on-policy), differ on `OBJ` (clipped surrogate vs plain advantage actor-critic).
- `DQN` and `SAC` agree on `EXP` (off-policy replay), differ on `OBJ` (TD value vs max-entropy actor-critic).
- `SimCLR` and `MoCo` agree on `OBJ` (InfoNCE contrast) and on `DAT` (two-view augmentation), differ on `EXEC`/mechanics.
- `LoRA + instruction tuning + AdamW` is `ADP` + `OBJ` + `FIT`: three slots, one run, exactly as the brief states.
- `DrQ` is random-shift augmentation (`DAT`) **and** off-policy replay (`EXP`) in one run — so even "data" and "experience" cannot be one sibling set.

### What I killed, and what killed it

| rejected level-1 characteristic | what killed it |
|---|---|
| **Learning paradigm** (supervised / unsupervised / self-supervised / reinforcement) | Undefined for most of the dimension — Adam, CutMix, FedAvg, beam search, GPTQ have no value. It is a property of *one station* (`OBJ`), promoted to the root. And it is partly a property of *use*: the identical cross-entropy loss is "supervised" or "self-supervised" depending on where the target came from, which is a fact about the data pipeline, not about the loss. This is also precisely the characteristic the SPR/ConSpec example is designed to break. |
| **Task / application domain** (vision, NLP, RL, speech) | Property of use, immediately. Adam, dropout, k-fold CV and distillation present a different value in every paper that uses them. Fails the use-test at the first example. |
| **Model family it applies to** (neural / tree / kernel / probabilistic) | Property of use. SGD fits neural nets, matrix factorizations and logistic regressions; cross-validation applies to everything. Also splits co-occurring things: gradient boosting and SGD would sit in different top branches while a single AutoML run executes both. |
| **Lifecycle stage** (pretraining / finetuning / inference) | The most tempting near-miss, because it *looks* like role. It is a property of use: pretraining and full finetuning are the same procedure run at different project times; Adam appears at all three stages; distillation appears at two. **Role is not stage.** Role is the functional position in a run's dataflow and is intrinsic; stage is where in a project timeline the run sits and is not. |
| **Mathematical machinery** (gradient-based / evolutionary / Bayesian / kernel / spectral) | Intrinsic — it passes the use-test — but it fails the *alternatives* reading at level 2: "gradient-following" would contain Adam, PPO and DARTS, which never compete for anything, and Adam and DARTS co-occur in one run. It also buries every organizing question the field actually asks: nothing aggregates to "on-policy" or "self-supervised objective". **Demoted to a crosscutting axis (`MACH`)**, where it earns its keep because the same strategy recurs in `FIT`, `SRCH`, `DAT` and `OUT` and the field names it ("evolutionary methods", "Bayesian methods", "kernel methods"). |
| **Lineage as the backbone** (the models dimension's answer) | Fails rule 7. Hundreds of unrelated roots, and no node answers "what proportion used an on-policy method". Worse, most of this dimension has no citation lineage at all: CutMix, EM, IPW, k-fold CV, difference-in-differences are not "descended" from anything in the sense rule 4 means. Lineage is kept where it belongs — **as descent inside an axis**, at the leaves (REINFORCE → A2C → PPO lives inside `OBJ.3`; SGD → momentum → AdaGrad → RMSProp → Adam → AdamW lives inside `FIT.2`). |
| **Cost / scale** (cheap vs expensive, small vs large) | Property of use and of hardware, not of the procedure. Dead on arrival. |
| **Deterministic vs stochastic** | Intrinsic but nearly contentless: it produces two classes, neither of which anyone aggregates to, and most entries are stochastic. |

### The anchoring rule for composite names

Many of the field's headline names are composites: `PPO` fixes an objective *and*
an experience regime; `DQN` fixes a TD objective *and* replay *and* an
exploration rule; `AlphaZero` fixes experience, objective and inference search;
`SimCLR` fixes augmentation and objective. Under facets these decompose
naturally, but a lineage chain (rule 4) must live on **one** axis or it is not a
chain. So:

> **A composite method is anchored on the axis carrying its defining
> contribution as framed by the paper that introduced it, and carries secondary
> values on the other axes it fixes.** Descent edges are drawn only inside the
> home axis.

`PPO`'s contribution is the clipped surrogate → home `OBJ.3.2`, secondary
`EXP.1`. `Rainbow`'s contribution is the combination → home `OBJ.3.1`, with
secondaries across `EXP.2`. This keeps `REINFORCE → A2C → PPO` and
`DQN → Rainbow → {C51, QR-DQN, IQN}` as single, clean chains.

### What would have changed my mind

Concretely, and these are checkable in phase 2:

1. **If named algorithm entities turn out to be overwhelmingly single-station
   atoms** — if composites like PPO/SimCLR/AlphaZero are a thin minority of
   distinct names — then a single tree rooted at station with multi-parenting for
   the few composites is simpler, and I would take it. The facet claim rests on
   composites being structural, not exceptional.
2. **If the typical entity carried values on four or more axes**, the axes would
   not be independent and I would conclude the stations are not separable
   primitives — the decomposition would be mine, not the field's.
3. **If `OBJ` absorbed the overwhelming majority of distinct names and the other
   axes were near-empty**, the facet machinery would be overhead; I would collapse
   to a tree rooted at objective and treat the rest as modifiers.
4. **If two competent annotators disagreed on which axis a name occupies** more
   than they disagree within an axis, the station decomposition is the wrong
   primitive and the dimension should be rebuilt on lineage with roll-up tags.
5. **If `MACH` values were almost never recorded**, I would delete that axis; it
   is the one part of this proposal I expect to lose.

Note what would *not* change my mind: `OBJ` being far larger than every other
axis (rule 5 — that is a finding, reported in Tensions), or `EST.1` being the
value of almost every deep-learning paper (that node exists so classical and
causal work is not an afterthought).

### How an annotator uses this

For each named algorithm string: ask "what does this procedure *do* in the run?"
Assign it to every axis where it fixes something. Most names get one or two.
`N/A` on nine axes is the normal and expected state. Counting is non-exclusive
(rule 6) throughout.

## The structure

Column conventions: `characteristic` is filled only on nodes whose children are
*divisions*; it is blank where the edge is descent. `parents` is `—` for an axis
root. Multi-parent entries list both ids.

---

### Axis DAT — Data construction and transformation

Scope: procedures that act on an already-collected data source to decide what the
learner actually consumes. Does **not** cover data produced by interacting with
something (that is `EXP`).

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `DAT` | Data construction and transformation | — | What the procedure changes about the training stream drawn from an already-collected source | The run executes a named procedure that alters which examples reach the learner, or what each example looks like, before the loss is computed. | Excludes procedures that generate data by acting on an environment, model or teacher (`EXP`), and excludes architectural layers that transform activations inside the model (models dimension). | — | The four children compose rather than compete; see Tensions T6. |
| `DAT.1` | Example transformation | `DAT` | What aspect of an individual example is altered | A named procedure maps each example to a modified example, leaving the set of examples one-to-one or near it. | Excludes procedures that change *which* examples are drawn (`DAT.2`) or that add examples (`DAT.4`). | — | |
| `DAT.1.1` | Label-preserving perturbation | `DAT.1` | | The procedure produces a modified copy of an example whose target is unchanged by construction, and the perturbation is sampled per-epoch or per-batch. | Excludes perturbations that also change the target (`DAT.1.2`) and deterministic re-encodings applied identically to every example (`DAT.1.3`). | RandAugment, AutoAugment (applied), SpecAugment, Cutout, random-shift (DrQ), EDA, back-translation | Unnamed "we flipped the images" is out of scope by the naming rule. |
| `DAT.1.2` | Example mixing | `DAT.1` | | The procedure combines two or more examples into one and combines their targets correspondingly. | Excludes single-example perturbation (`DAT.1.1`) and synthesis from a model or a simulator (`DAT.4`). | Mixup, CutMix, Manifold Mixup, Copy-Paste, AugMix | |
| `DAT.1.3` | Representation re-encoding | `DAT.1` | | The procedure maps raw records into the fixed feature or token space the learner reads, deterministically given its own fitted parameters. | Excludes stochastic augmentation, and excludes learned embeddings that are the model's own layers. | BPE, WordPiece, SentencePiece, TF-IDF, target encoding, standardisation, whitening, patchification, mel-spectrogram | Tokenisers are named procedures a run executes, so they are in scope. |
| `DAT.1.4` | Dimensionality reduction and embedding construction | `DAT.1` | | The procedure fits a lower-dimensional representation of the data and the run consumes that representation. | Excludes reductions that are layers of the model being trained (autoencoder bottlenecks). | PCA, kernel PCA, ICA, NMF, t-SNE, UMAP, random projection, MDS, LLE | Several of these produce no separable model (t-SNE, UMAP in transductive use) — legal per the brief. Cross-listed `EST.3`, `FIT`. |
| `DAT.1.5` | Record cleaning and filtering | `DAT.1` | | The procedure removes or repairs records by a named criterion before training. | Excludes selection driven by the learner's current state (`DAT.2`). | MinHash dedup, SemDeDup, classifier-based quality filtering, decontamination, outlier removal | Dominant in modern corpus-construction papers. |
| `DAT.2` | Example selection and scheduling | `DAT` | What determines which of the available examples the learner sees, and when | A named procedure decides the order, frequency or subset of examples drawn from a fixed pool. | Excludes anything that modifies an example's content (`DAT.1`) or manufactures its target (`DAT.3`). | — | |
| `DAT.2.1` | Difficulty or competence ordering | `DAT.2` | | The presentation order of examples is governed by a named measure of example difficulty or learner competence. | Excludes orderings driven by class frequency (`DAT.2.2`) or by a fixed random shuffle. | Curriculum learning, self-paced learning, anti-curriculum, scheduled sampling | |
| `DAT.2.2` | Reweighting and resampling | `DAT.2` | | Examples are drawn or weighted non-uniformly according to a named statistic of the example (class, loss, importance). | Excludes reweighting expressed purely as a loss term (`OBJ.7`), e.g. focal loss. | Class-balanced sampling, oversampling, OHEM, hard-negative mining, importance sampling of data, prioritised replay when applied to a static pool | Focal loss is deliberately placed in `OBJ.1.1`, not here. |
| `DAT.2.3` | Subset construction | `DAT.2` | | A named procedure selects a permanent subset of the pool that the run trains on instead of the whole. | Excludes per-batch sampling schemes that still see the whole pool over time. | Coreset selection, data pruning, data mixture weighting (DoReMi), submodular selection | |
| `DAT.2.4` | Learner-driven label acquisition | `DAT.2` | | The learner's own state selects which unlabelled items are sent to an oracle for annotation. | Excludes selection among already-labelled data, and excludes reward-seeking interaction with an environment (`EXP`). | Uncertainty sampling, BALD, core-set active learning, query-by-committee | Sits on the border with `EXP`; kept here because the pool is pre-existing. |
| `DAT.3` | Target construction without new annotation | `DAT` | How a supervision target is manufactured for data that has none | The run produces targets for unlabelled or differently-labelled data by a named procedure, and then trains on them. | Excludes targets defined by the loss's own structure on the raw input (`OBJ.2`), and excludes human annotation. | — | Seam with `OBJ.2` is real; see T10. |
| `DAT.3.1` | Model-generated labels | `DAT.3` | | A model's predictions on unlabelled data become training targets for a subsequent fitting step. | Excludes a teacher's *soft* outputs used as a loss term in the same optimisation (`OBJ.5.1`). | Pseudo-labelling, self-training, Noisy Student, co-training, FixMatch pseudo-label branch | |
| `DAT.3.2` | Rule or heuristic labelling | `DAT.3` | | Targets are assigned by named hand-written rules, knowledge bases or labelling functions. | Excludes targets produced by a learned model (`DAT.3.1`). | Snorkel / data programming, distant supervision, heuristic weak supervision | |
| `DAT.3.3` | Outcome relabelling | `DAT.3` | | Stored trajectories or records are given new targets derived from what actually happened in them. | Excludes relabelling by an external model or rule. | Hindsight Experience Replay, goal relabelling, return-conditioned relabelling | Multi-parent with `EXP.2.3`. |
| `DAT.3.4` | Noisy-label handling | `DAT.3` | | A named procedure identifies and corrects or down-weights records whose given labels are judged wrong. | Excludes generic regularisers that merely tolerate noise (`OBJ.7`). | Co-teaching, confident learning, MentorNet, label cleaning | |
| `DAT.4` | Synthesis of new data | `DAT` | What generates the new examples | The run trains on examples that did not exist in any source dataset and were produced by a named generator. | Excludes modified copies of real examples (`DAT.1`) and excludes experience collected from an environment (`EXP.4`). | — | |
| `DAT.4.1` | Feature-space interpolation | `DAT.4` | | New examples are constructed by interpolating between existing examples in feature space, typically to rebalance classes. | Excludes mixing that also mixes targets for regularisation (`DAT.1.2`). | SMOTE, ADASYN, Borderline-SMOTE | |
| `DAT.4.2` | Generative-model synthesis | `DAT.4` | | A trained generative model produces the training examples or instructions. | Excludes simulator output (`DAT.4.3`). | Self-Instruct, Evol-Instruct, synthetic captions, diffusion-generated training images, model-written rationales | |
| `DAT.4.3` | Simulator and procedural generation | `DAT.4` | | A hand-built simulator or procedural generator produces the examples, with named randomisation over its parameters. | Excludes learned generators (`DAT.4.2`). | Domain randomisation, procedural level generation, physics-sim datasets | |
| `DAT.4.4` | Dataset distillation | `DAT.4` | | A small synthetic set is optimised so that training on it approximates training on the full set. | Excludes selecting real examples (`DAT.2.3`). | Dataset Distillation, Dataset Condensation, gradient/trajectory matching | |
| `DAT.4.5` | Privacy-preserving synthesis | `DAT.4` | | Synthetic records are generated under a stated formal privacy guarantee and used in place of the real ones. | Excludes synthesis with no formal guarantee (`DAT.4.2`). | DP-GAN, DP synthetic tabular data, PATE-GAN | `speculative` — believed real but I cannot name a paper in this review's likely scope. |

---

### Axis EXP — Experience acquisition

Scope: procedures by which a run *generates* its own training data by acting on
an environment, a learned model, an opponent, a teacher or a search.

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `EXP` | Experience acquisition | — | The relation between the process that generates the training experience and the learned object being updated | The run's training data is produced during the run, by something the run controls or queries. | Excludes any procedure operating on a fixed, pre-collected dataset (`DAT`). | — | |
| `EXP.1` | On-policy interaction | `EXP` | | Every gradient step consumes data generated by the current parameters, and the data is discarded after use. | Excludes any reuse of data generated by earlier parameters (`EXP.2`) and any fixed log (`EXP.3`). | REINFORCE rollouts, A2C/A3C workers, TRPO and PPO rollout phases, vanilla policy gradient | The node that answers "what proportion used an on-policy method". |
| `EXP.2` | Off-policy interaction | `EXP` | By which mechanism experience generated by a non-target behaviour is produced or made usable | The run updates on data produced by parameters or a policy other than the one currently being improved, while still interacting. | Excludes on-policy-only runs (`EXP.1`) and runs with no interaction at all (`EXP.3`). | — | |
| `EXP.2.1` | Behaviour-policy exploration rules | `EXP.2` | | A named rule perturbs the greedy action choice during collection, creating the behaviour/target mismatch deliberately. | Excludes bonuses added to the reward (`EXP.2.2`) and buffer policies (`EXP.2.3`). | epsilon-greedy, Boltzmann/softmax exploration, NoisyNets, parameter-space noise, UCB action selection, Thompson sampling | Structurally the same shape as `OUT.1`/`OUT.2`; see T9. |
| `EXP.2.2` | Intrinsic-motivation exploration | `EXP.2` | | An auxiliary learned or counted signal is added to steer collection toward novel states. | Excludes stochastic perturbation of the action distribution alone (`EXP.2.1`). | Count-based / pseudo-counts, RND, ICM, Go-Explore, NGU, DIAYN | Also carries an `OBJ` value for the auxiliary model it fits. |
| `EXP.2.3` | Replay-buffer management | `EXP.2` | | A named policy governs what is stored in, and drawn from, a buffer of past transitions. | Excludes exploration rules and off-policy weighting corrections. | Uniform experience replay, Prioritised Experience Replay, HER, n-step buffers, reservoir replay | Multi-parent with `DAT.3.3` for HER. |
| `EXP.2.4` | Off-policy correction | `EXP.2` | | The update is reweighted or truncated to account for the mismatch between behaviour and target policy. | Excludes buffer mechanics with no correction term. | Importance sampling ratios, V-trace (IMPALA), Retrace(lambda), tree-backup, per-decision IS | Shares content with `OBJ.3.4`; home kept here. |
| `EXP.3` | Offline / logged experience | `EXP` | | The run consumes a fixed log of interaction and takes no new actions in the environment. | Excludes any run that collects new transitions, however rarely. | Batch RL, BCQ, CQL, IQL, TD3+BC, behaviour-regularised offline RL | The constraint mechanisms also carry `OBJ.7.3` values. |
| `EXP.4` | Model-generated experience | `EXP` | | A learned or given model of the environment produces the transitions the learner trains on. | Excludes transitions from the real environment, and excludes data generated by a generative model of *examples* (`DAT.4.2`). | Dyna, MBPO, Dreamer imagination rollouts, PETS rollouts, world-model rollouts | |
| `EXP.5` | Self-generated opponent experience | `EXP` | | The data-generating process is the learner playing against itself or a population derived from itself. | Excludes a fixed scripted opponent or human demonstrations. | Self-play (AlphaZero), AlphaStar league, fictitious play, PSRO, autocurricula | |
| `EXP.6` | Demonstration and teacher experience | `EXP` | | Training data is supplied by an expert's behaviour, queried or logged. | Excludes reward-labelled interaction by the learner itself. | Behavioural cloning data, DAgger, imitation from observation, expert trajectories for IRL | |
| `EXP.7` | Search-generated experience | `EXP` | | A search procedure run at collection time produces improved targets that the learner is then fitted to. | Excludes search used only to produce the final answer (`OUT.3`). | AlphaZero MCTS-improved policy targets, expert iteration, MuZero search targets | The same MCTS appears again as `OUT.3`; genuinely two roles. |

---

### Axis OBJ — Learning objective and signal source

Scope: the named quantity a run tries to improve. This is the largest axis by a
wide margin. Per rule 5 that is reported, not corrected.

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `OBJ` | Learning objective and signal source | — | Where the signal that defines "better" originates | The run evaluates a named scalar (or vector of scalars) whose value the fitting procedure is trying to improve. | Excludes the mechanism that improves it (`FIT`), the data it is computed on (`DAT`/`EXP`), and the quantity finally reported (`EST`). | — | Largest axis: 45 nodes. Finding, not a defect. |
| `OBJ.1` | External annotation | `OBJ` | What the loss measures about the prediction/label pair | The target comes from an annotation supplied with the data and not derivable from the input. | Excludes targets manufactured by the run (`DAT.3`, `OBJ.2`). | — | |
| `OBJ.1.1` | Classification losses | `OBJ.1` | | The loss scores a predicted distribution or margin against a discrete gold class. | Excludes continuous targets (`OBJ.1.2`) and losses over whole structures (`OBJ.1.3`). | cross-entropy, focal loss, label smoothing, hinge loss, logistic loss, class-balanced loss | |
| `OBJ.1.2` | Regression losses | `OBJ.1` | | The loss scores a predicted real value against a continuous gold value. | Excludes discrete targets, and excludes likelihoods of an explicit density (`OBJ.4.1`). | MSE, MAE, Huber, quantile / pinball loss, log-cosh | |
| `OBJ.1.3` | Structured-output losses | `OBJ.1` | | The loss is defined over an entire structure (sequence, set, segmentation) rather than independent elements. | Excludes per-element losses summed naively. | CTC, CRF likelihood, Hungarian matching loss (DETR), Dice / IoU loss, edit-distance surrogates | |
| `OBJ.1.4` | Ranking and metric losses | `OBJ.1` | | The loss scores the *relative* ordering or distance of labelled items rather than their absolute labels. | Excludes contrast over automatically-constructed views (`OBJ.2.3`). | triplet loss, Hadsell contrastive loss, ArcFace, CosFace, pairwise ranking, LambdaRank | The seam with `OBJ.2.3` is the presence of annotation. |
| `OBJ.2` | The input itself (self-supervised pretext) | `OBJ` | What relation among parts or views of the input is scored | The target is constructed deterministically from the unlabelled input by a named rule. | Excludes human annotation, reward, and teacher outputs. | — | The node that answers "what proportion used a self-supervised objective". |
| `OBJ.2.1` | Masked reconstruction | `OBJ.2` | | Part of the input is hidden and the loss scores recovery of the hidden part from the visible part. | Excludes left-to-right prediction with no masking (`OBJ.2.2`) and corruption that is not a mask (`OBJ.2.7`). | MLM (BERT), SpanBERT, MAE, BEiT, masked audio modelling, masked point clouds | |
| `OBJ.2.2` | Autoregressive next-element prediction | `OBJ.2` | | The loss scores prediction of element t from elements before t, in a fixed order. | Excludes bidirectional reconstruction (`OBJ.2.1`). | causal language modelling, PixelCNN/PixelRNN objective, next-frame prediction | |
| `OBJ.2.3` | Instance discrimination by contrast | `OBJ.2` | | The loss raises the score of matched views and explicitly lowers the score of negatives. | Excludes objectives with no negative term (`OBJ.2.4`, `OBJ.2.5`). | InfoNCE, SimCLR, MoCo, CPC, CLIP, ALIGN, SupCon | CLIP's pairs are cross-modal but still constructed, not annotated. |
| `OBJ.2.4` | Non-contrastive self-prediction | `OBJ.2` | | One view predicts another view's representation with no negatives, collapse prevented by asymmetry (stop-grad, EMA target, centring). | Excludes objectives with explicit negatives (`OBJ.2.3`) and decorrelation penalties (`OBJ.2.5`). | BYOL, SimSiam, DINO, SPR, data2vec, I-JEPA | `SPR` is placed here — not in an "RL" branch. That is the point. |
| `OBJ.2.5` | Redundancy reduction | `OBJ.2` | | Collapse is prevented by a statistical penalty on the cross-correlation or covariance of embeddings. | Excludes negatives and excludes predictor-asymmetry schemes. | Barlow Twins, VICReg, W-MSE | |
| `OBJ.2.6` | Cluster-assignment prediction | `OBJ.2` | | Targets are cluster assignments computed online over the batch or dataset, and one view predicts the other's assignment. | Excludes direct representation prediction (`OBJ.2.4`). | DeepCluster, SwAV, SeLa, sinkhorn-balanced assignment | |
| `OBJ.2.7` | Denoising and corruption inversion | `OBJ.2` | | A named corruption is applied and the loss scores recovery of the clean input or detection of the corruption. | Excludes masking specifically (`OBJ.2.1`). | denoising autoencoder, ELECTRA replaced-token detection, T5/BART span corruption, diffusion denoising loss | Diffusion loss is also `OBJ.4.3`; see T4. |
| `OBJ.2.8` | Hand-designed pretext tasks | `OBJ.2` | | The target is a property of a transformation the run applied, and the task has no use beyond representation learning. | Excludes reconstruction and contrast. | rotation prediction, jigsaw, relative patch location, colourisation, temporal order verification | Largely historical; expect low counts. |
| `OBJ.3` | Environment reward | `OBJ` | What function of the reward is represented and improved | The objective is defined over scalar reward received from an environment. | Excludes preference comparisons (`OBJ.6`) and learned critics that are not reward-derived. | — | |
| `OBJ.3.1` | Value / temporal-difference objectives | `OBJ.3` | | The loss is a bootstrapped regression of a value or action-value toward a target built from its own later estimates. | Excludes direct differentiation of expected return through the policy (`OBJ.3.2`). | Q-learning, SARSA, TD(lambda), DQN loss, Double DQN, fitted-Q | Lineage chain: DQN → Rainbow → {C51, QR-DQN, IQN} hangs here. |
| `OBJ.3.1.1` | Rainbow | `OBJ.3.1` | | The method is the named combination of DQN extensions. | — | Rainbow | Descent from DQN; a bundle, see T1. |
| `OBJ.3.1.2` | Distributional value objectives | `OBJ.3.1.1` | | The regression target is a whole return distribution rather than its mean. | Excludes expectation-only TD losses. | C51, QR-DQN, IQN, FQF | Descent from Rainbow per the brief's example. |
| `OBJ.3.2` | Policy-gradient surrogates | `OBJ.3` | | The objective is a surrogate whose gradient estimates the gradient of expected return with respect to policy parameters. | Excludes value-regression losses (`OBJ.3.1`). | REINFORCE, A2C, TRPO, PPO, IMPALA, GRPO, RLOO | Lineage chain: REINFORCE → A2C → {TRPO → PPO → GRPO}. |
| `OBJ.3.3` | Entropy-regularised and deterministic actor-critic | `OBJ.3` | | The objective adds an explicit entropy term, or differentiates a critic through a deterministic policy. | Excludes plain stochastic policy gradients with no entropy term in the objective. | SAC, soft Q-learning, DDPG, TD3 | |
| `OBJ.3.4` | Return and advantage estimators | `OBJ.3` | | The procedure specifies how the regression or weighting target is assembled from a trajectory. | Excludes the loss form itself. | GAE, n-step returns, lambda-returns, Retrace targets | Overlaps `EXP.2.4` by design. |
| `OBJ.3.5` | Environment-model objectives | `OBJ.3` | | The loss fits a model of the environment's dynamics or reward rather than a policy or value. | Excludes policy and value losses. | dynamics MSE, latent dynamics (Dreamer, PlaNet), reward-model regression in model-based RL | Pairs with `EXP.4`. |
| `OBJ.3.6` | Inverse reward inference | `OBJ.3` | | A reward function is inferred from demonstrations rather than given. | Excludes direct imitation of actions (`OBJ.1.1` on demonstration data). | MaxEnt IRL, GAIL, AIRL | GAIL is also `OBJ.5.2`. |
| `OBJ.4` | A probability model of the data | `OBJ` | Which functional of the model distribution is optimised | The objective is an explicit statistical fit criterion between a parametrised distribution and the data. | Excludes losses with no probabilistic interpretation and excludes reward. | — | The home for most classical statistics. |
| `OBJ.4.1` | Maximum likelihood and MAP | `OBJ.4` | | The objective is the (log-)likelihood of the data under the model, optionally with a prior term. | Excludes bounds and surrogates on the likelihood (`OBJ.4.2`). | MLE, logistic-regression likelihood, GMM likelihood, Poisson/GLM likelihood, MAP estimation | |
| `OBJ.4.2` | Variational bounds | `OBJ.4` | | The objective is a tractable bound on an intractable likelihood or posterior, involving an approximating distribution. | Excludes exact likelihoods (`OBJ.4.1`, `OBJ.4.4`). | ELBO, VAE, beta-VAE, IWAE, variational inference, variational EM | |
| `OBJ.4.3` | Score and energy-based objectives | `OBJ.4` | | The objective targets the gradient of the log-density or an unnormalised energy, avoiding the partition function. | Excludes normalised-likelihood objectives. | score matching, denoising score matching, contrastive divergence, NCE, energy-based losses | Diffusion training sits here and in `OBJ.2.7`. |
| `OBJ.4.4` | Exact-likelihood flows | `OBJ.4` | | The objective is an exactly computable likelihood obtained through an invertible transform with tractable Jacobian. | Excludes bounds and score-based surrogates. | normalising-flow NLL, RealNVP/Glow objective, autoregressive flows | |
| `OBJ.4.5` | Moment and divergence matching | `OBJ.4` | | The objective matches summary statistics or a divergence between model and data distributions, without a likelihood. | Excludes likelihood-based fits and adversarial critics (`OBJ.5.2`). | MMD, method of moments, GMM (econometric), Wasserstein / Sinkhorn objectives, CRPS | |
| `OBJ.4.6` | Posterior as the target | `OBJ.4` | | The objective is to characterise a posterior distribution rather than a point estimate. | Excludes point MAP estimation (`OBJ.4.1`). | Bayesian posterior inference, Bayesian neural network posteriors, hierarchical model posteriors | Realised by `FIT.7` or `FIT.4`. |
| `OBJ.5` | Another model's judgement | `OBJ` | Which model supplies the target and in what form | The training target is produced by a second model whose outputs are not ground truth. | Excludes human annotation and excludes self-constructed pretext targets. | — | |
| `OBJ.5.1` | Teacher-output distillation | `OBJ.5` | | The loss matches a student's outputs or internal features to a fixed or slowly-updated teacher's. | Excludes hard pseudo-labels consumed as data (`DAT.3.1`). | Hinton KD, FitNets feature distillation, sequence-level KD, self-distillation, DistilBERT training | Cross-listed `PTX.5` when the purpose is compression; see T8. |
| `OBJ.5.2` | Adversarial critic | `OBJ.5` | | The objective is a minimax game against a discriminator trained simultaneously to tell the outputs apart. | Excludes fixed teachers and excludes adversarial *inputs* used as regularisation (`OBJ.7.2`). | GAN, WGAN, WGAN-GP, LSGAN, DANN, GAIL, adversarial autoencoders | |
| `OBJ.5.3` | Learned reward or preference model | `OBJ.5` | | A model fitted to human or AI judgements supplies the scalar the policy optimises. | Excludes objectives that use the comparisons directly with no reward model (`OBJ.6.2`). | RLHF reward model, RLAIF, Constitutional AI critique model | Pairs with `OBJ.3.2` for the policy step. |
| `OBJ.5.4` | Verifier and process reward | `OBJ.5` | | A model scores intermediate steps or verifies outcomes, and that score is the training signal. | Excludes final-answer-only correctness from ground truth (`OBJ.1.1`). | process reward models, outcome reward models, verifier-guided finetuning | |
| `OBJ.6` | Preference comparisons | `OBJ` | How pairwise or ranked comparisons are converted into a loss | The supervision is "A is preferred to B" rather than "the answer is A". | Excludes scalar quality scores and excludes gold answers. | — | |
| `OBJ.6.1` | Reward-model-mediated | `OBJ.6` | | Comparisons fit a reward model, which is then optimised by an RL procedure. | Excludes direct losses on the policy from comparisons. | RLHF (reward model + PPO), RLAIF | Multi-parent with `OBJ.5.3`. |
| `OBJ.6.2` | Direct preference objectives | `OBJ.6` | | The comparison enters a closed-form loss on the policy with no separate reward model and no rollouts. | Excludes any method that fits an explicit reward model first. | DPO, IPO, KTO, ORPO, SimPO, SLiC | |
| `OBJ.6.3` | Rejection-sampling finetuning | `OBJ.6` | | Candidates are generated, filtered by a judge or verifier, and the survivors become supervised targets. | Excludes losses that use the rejected candidates as negatives. | Best-of-n / rejection sampling finetuning, RAFT, RFT, STaR | Also `OUT.1` for the generation step. |
| `OBJ.7` | The hypothesis itself | `OBJ` | What property of the parameters or the learned function is penalised or constrained | A term in the objective depends only on the parameters, the function, or a reference model, not on how well the data is fitted. | Excludes data-fit terms of any kind. | — | |
| `OBJ.7.1` | Magnitude and complexity penalties | `OBJ.7` | | A named norm of the parameters is added to the objective. | Excludes penalties on function behaviour (`OBJ.7.2`). | L2 / weight decay, L1 / LASSO, elastic net, nuclear-norm penalty, ridge penalty | Weight decay as implemented in AdamW is also `FIT.2.3`. |
| `OBJ.7.2` | Smoothness and robustness penalties | `OBJ.7` | | The objective penalises how much the output changes under a named perturbation of the input or the computation. | Excludes parameter-norm penalties. | adversarial training (PGD-AT), TRADES, spectral-norm/Lipschitz penalty, Jacobian penalty, consistency regularisation, mean teacher, R-Drop, VAT | Consistency regularisation also touches `DAT.1.1`; see T10. |
| `OBJ.7.3` | Reference-model and behavioural constraints | `OBJ.7` | | The objective penalises divergence from a named reference distribution, policy or earlier parameter state. | Excludes penalties with no reference object. | KL-to-reference (RLHF, PPO-KL), trust-region constraint, EWC, SI, LwF, CQL conservatism, behaviour cloning regulariser | The home for continual-learning penalties. |
| `OBJ.7.4` | Structure-inducing penalties | `OBJ.7` | | The objective rewards a named structural property (sparsity pattern, orthogonality, disentanglement) of the solution. | Excludes plain magnitude penalties. | group lasso, L0 gates, orthogonality penalty, total variation, fairness constraints | |

---

### Axis FIT — Parameter estimation

Scope: how parameter values are actually produced. Classical and deep methods sit
side by side here by construction.

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `FIT` | Parameter estimation | — | What information about the objective the procedure uses to decide the next parameter values | The run executes a named procedure that computes or updates the numbers in the learned object. | Excludes what is being optimised (`OBJ`), what is varied above the parameters (`SRCH`), and transformations of already-fitted parameters (`PTX`). | — | `FIT.9` is the one child that modifies rather than determines the update; see T3. |
| `FIT.1` | Analytic solution | `FIT` | | Parameters are obtained in closed form by solving the optimality condition directly. | Excludes any iterative scheme, even a fast-converging one. | OLS normal equations, ridge closed form, LDA, Gaussian MLE, kernel ridge, exact GP posterior, Kalman update | |
| `FIT.2` | First-order iterative | `FIT` | How the gradient is turned into a step | Each update is a function of a (possibly stochastic) first derivative of the objective. | Excludes updates using curvature (`FIT.3`) or no derivative (`FIT.6`). | — | The field's dominant node. |
| `FIT.2.1` | Plain gradient descent | `FIT.2` | | The step is the gradient times a scalar learning rate, with no state carried between steps. | Excludes any accumulated or per-coordinate state. | GD, minibatch SGD | Root of the optimiser lineage. |
| `FIT.2.2` | Momentum and acceleration | `FIT.2.1` | | The step accumulates past gradients in a single velocity vector. | Excludes per-coordinate scaling (`FIT.2.3`). | heavy-ball momentum, Nesterov accelerated gradient | Descent from SGD. |
| `FIT.2.3` | Per-coordinate adaptive scaling | `FIT.2.2` | | Each parameter's step is divided by a running statistic of that parameter's own past gradients. | Excludes globally-scaled steps and curvature-matrix preconditioning (`FIT.3`). | AdaGrad, RMSProp, Adam, AdamW, Adafactor, LAMB, LARS, Lion, AdaBelief | Chain: AdaGrad → RMSProp → Adam → AdamW → {Lion, Adafactor, LAMB}. |
| `FIT.2.4` | Flatness-seeking steps | `FIT.2` | | The step is computed at a deliberately perturbed parameter point to bias toward flat minima. | Excludes averaging of iterates (`ADP.6`). | SAM, ASAM, GSAM, Adversarial Weight Perturbation | |
| `FIT.2.5` | Step-size scheduling and stabilisation | `FIT.2` | | A named rule varies the learning rate over the run, or bounds the step before it is applied. | Excludes rules that change the direction rather than the magnitude. | cosine decay, linear warmup, one-cycle, cyclical LR, gradient clipping, gradient accumulation, EMA of weights | Gradient clipping is also the mechanism inside DP-SGD (`EXEC.8`). |
| `FIT.2.6` | Structured preconditioning | `FIT.2` | | The step is multiplied by a matrix preconditioner estimated from gradient structure rather than per-coordinate scalars. | Excludes diagonal adaptive methods (`FIT.2.3`). | Shampoo, Muon, SOAP | |
| `FIT.2.7` | Gradient estimation under non-differentiability | `FIT.2` | How a usable gradient estimate is formed when exact backpropagation is unavailable | The run uses a named estimator to obtain a descent direction through a stochastic, discrete or implicit component. | Excludes plain backpropagation through a differentiable graph. | reparameterisation trick, score-function/REINFORCE estimator, Gumbel-Softmax, straight-through estimator, implicit differentiation (DEQ, iMAML), SPSA, forward-mode / DFA | Note REINFORCE appears both as an estimator here and as an RL objective in `OBJ.3.2`; the names are the same for a reason. |
| `FIT.2.8` | Multi-objective gradient combination | `FIT.2` | | Gradients from several losses are combined by a named rule before the step. | Excludes fixed scalar loss weights chosen by hand or by `SRCH`. | PCGrad, GradNorm, MGDA, CAGrad, gradient surgery, uncertainty weighting | |
| `FIT.3` | Curvature-informed updates | `FIT` | | The update uses second-derivative information or an approximation of it. | Excludes diagonal first-moment heuristics (`FIT.2.3`). | Newton, Gauss-Newton, L-BFGS, conjugate gradient (TRPO), natural gradient, K-FAC | |
| `FIT.4` | Surrogate construction and alternation | `FIT` | How a tractable surrogate or block decomposition replaces the objective | Each iteration optimises a constructed bound, or one block of variables with the rest held fixed. | Excludes direct gradient steps on the full objective. | EM, MM, variational EM, Lloyd's k-means, ALS, coordinate descent, proximal gradient / ISTA, ADMM, SMO (SVM) | The home for most classical iterative estimators. |
| `FIT.5` | Greedy structure growth | `FIT` | What local score drives each growth step | The learned object is built incrementally, each increment chosen to maximise a named local criterion and then frozen. | Excludes procedures that revise all parameters jointly at each step. | CART / ID3 / C4.5, AdaBoost, gradient boosting, XGBoost, LightGBM, CatBoost, forward stepwise selection, matching pursuit / OMP | Tree ensembles and boosting have a first-class home here, not an afterthought. |
| `FIT.6` | Population and derivative-free search over parameters | `FIT` | | Parameters are updated using objective *values* only, over a population or a perturbation set. | Excludes any use of a derivative, exact or estimated by backprop. | CMA-ES, OpenAI-ES, genetic algorithms, NEAT, simulated annealing, Nelder-Mead, cross-entropy method, particle swarm | Overlaps `MACH.7`; see T5. |
| `FIT.7` | Posterior sampling | `FIT` | | The procedure produces samples from a distribution over parameters rather than a point estimate. | Excludes point estimation of any kind, including MAP. | Metropolis-Hastings, Gibbs sampling, HMC, NUTS, SGLD, SMC / particle filters, slice sampling | Pairs with `OBJ.4.6` and `EST.8`. |
| `FIT.8` | No parameter fitting | `FIT` | | The "fitting" step stores or indexes the training data and computes nothing that could be called a parameter. | Excludes any procedure with trained parameters, however few. | k-NN, kernel density estimation, Nadaraya-Watson, locally weighted regression, memory-based retrieval | This is the node that makes "algorithm with no model" explicit. |
| `FIT.9` | Perturbation during fitting | `FIT` | What is randomised or corrupted during fitting to change the solution reached | A named stochastic perturbation is applied to the computation during fitting and removed at inference. | Excludes perturbations applied to the data (`DAT.1.1`) and penalties added to the loss (`OBJ.7`). | dropout, DropConnect, stochastic depth, DropPath, gradient noise, weight noise, stochastic rounding | Characteristic strain acknowledged: this child modifies the update rather than determining it (T3). |

---

### Axis EST — Estimand and identification

Scope: what the run is ultimately trying to *know*, and what assumption licenses
the claim. This axis exists so that statistics, causal inference and evaluation
protocols have a first-class home rather than being bolted onto a
deep-learning-shaped tree.

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `EST` | Estimand and identification | — | What quantity the run estimates and what licenses the estimate | The run produces a stated quantity — a predictor, an effect, a partition, an interval, a test decision — and a named procedure justifies it. | Excludes the mechanics of computing it (`FIT`) and the loss used (`OBJ`). | — | `EST.1` is the near-universal default; see T11. |
| `EST.1` | Predictive risk | `EST` | | The target quantity is expected loss on new draws from the same distribution, estimated by its empirical counterpart. | Excludes any causal, structural, or coverage claim. | empirical risk minimisation, regularised ERM, structural risk minimisation | Default value for the large majority of ML papers. |
| `EST.2` | Density and distribution | `EST` | | The target quantity is the data distribution itself or its density. | Excludes conditional prediction targets (`EST.1`). | KDE, GMM density estimation, generative density modelling, histogram estimation, copula estimation | |
| `EST.3` | Latent structure | `EST` | | The target quantity is an unobserved grouping, factorisation or coordinate system of the data. | Excludes supervised targets and excludes density per se. | k-means, DBSCAN, spectral clustering, hierarchical clustering, LDA topic models, factor analysis, matrix factorisation, t-SNE / UMAP embeddings | Cross-listed with `DAT.1.4` when the result is consumed as features. |
| `EST.4` | Causal effect under unconfoundedness | `EST` | How the estimator removes confounding given measured covariates | The run estimates a treatment effect and justifies it by conditioning on observed covariates. | Excludes effects identified by a design or instrument (`EST.5`) and excludes purely predictive models. | IPW, propensity-score matching, g-computation, S/T/X-learners, AIPW, TMLE, double machine learning, causal forests | Nuisance models inside these are separate `FIT` entries — DML with XGBoost is two algorithms. |
| `EST.5` | Causal effect under design-based identification | `EST` | What feature of the data-generating design supplies the identification | The run estimates an effect by exploiting an instrument, a discontinuity, a time structure or a control group rather than covariate adjustment. | Excludes covariate-adjustment-only estimators (`EST.4`). | instrumental variables / 2SLS, difference-in-differences, event study, regression discontinuity, synthetic control, front-door adjustment | |
| `EST.6` | Causal structure | `EST` | | The target quantity is the graph or the functional form of the causal mechanism, not an effect size. | Excludes effect estimation under a known graph. | PC, FCI, GES, LiNGAM, NOTEARS, invariant causal prediction | |
| `EST.7` | Off-policy value | `EST` | | The target quantity is the value of a decision rule that did not generate the data. | Excludes on-policy evaluation by direct rollout. | IPS / SNIPS, doubly-robust OPE, fitted Q-evaluation, MAGIC | Pairs with `EXP.3`. |
| `EST.8` | Uncertainty and coverage | `EST` | How the uncertainty statement is justified | The run produces an interval, a set or a distribution with a stated coverage or credibility property. | Excludes point estimates with no uncertainty claim. | bootstrap, jackknife, conformal prediction, Bayesian credible intervals, delta method, calibration curves | |
| `EST.9` | Hypothesis tests and comparisons | `EST` | | The run produces a decision or p-value about a stated null, by a named test. | Excludes model-selection criteria used only to pick a model (`SRCH.6`). | permutation test, t-test, ANOVA, Wilcoxon, A/B testing, Bonferroni, Benjamini-Hochberg FDR | Often reported in the evaluation section rather than as a "method"; expect undercounting. |
| `EST.10` | Generalisation estimation protocols | `EST` | | A named resampling protocol produces the reported performance estimate. | Excludes resampling used to produce parameters (`FIT`) or to select hyperparameters (`SRCH.6`). | k-fold cross-validation, nested CV, leave-one-out, hold-out, time-series CV, repeated CV | Multi-parent with `SRCH.6` when CV drives selection rather than reporting. |

---

### Axis ADP — Adaptation scope

Scope: which parameters the procedure is permitted to change, relative to an
existing learned object.

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `ADP` | Adaptation scope | — | What the procedure is permitted to change about an existing learned object | The named procedure's content is a restriction or extension of *which* parameters move, not how or toward what. | Excludes the update rule (`FIT`), the loss (`OBJ`), and post-hoc edits with no objective (`PTX`). | — | Deliberately scope-only; timing is not encoded here. See T2. |
| `ADP.1` | Full training from scratch | `ADP` | | All parameters are initialised randomly and all are updated. | Excludes any run starting from pretrained weights. | pretraining from scratch, end-to-end training | The default value; low information but needed as a contrast class. |
| `ADP.2` | Full update from a pretrained initialisation | `ADP` | | All parameters are updated, starting from weights produced by an earlier run. | Excludes runs that freeze any part of the base model. | full finetuning, continued pretraining, domain-adaptive pretraining, instruction tuning (when full) | |
| `ADP.3` | Subset of existing parameters | `ADP` | Which existing parameters are left unfrozen | A named rule freezes most of the model and updates a specified existing subset. | Excludes methods that add new parameters (`ADP.4`). | linear probing / head-only, last-k layers, BitFit (biases), LayerNorm-only, TENT (norm affine params), surgical finetuning | TENT lives here; "test-time adaptation" has no single node (T2). |
| `ADP.4` | Added modules with the base frozen | `ADP` | Where the added parameters attach to the frozen base | New parameters are introduced and only they are trained. | Excludes unfreezing any original parameter. | adapters (Houlsby, Pfeiffer), LoRA, QLoRA, DoRA, VeRA, prefix-tuning, prompt-tuning / P-tuning, IA3, ladder side-tuning | The parameter-efficient-finetuning node. |
| `ADP.5` | Inputs only | `ADP` | | The procedure changes what is fed to the model and changes no parameters at all. | Excludes soft prompts, which are trained parameters (`ADP.4`). | in-context / few-shot prompting, chain-of-thought prompting, demonstration selection | Only *named* prompting procedures are in scope. |
| `ADP.6` | Several parameter sets jointly, during fitting | `ADP` | How the multiple parameter sets are related during the run | The run maintains or combines more than one parameter set as part of fitting. | Excludes merging of independently finished models (`PTX.4`). | SWA, EMA teacher, deep-ensemble training, co-distillation, snapshot ensembles | Seam with `PTX.4` is "during" vs "after"; see T8. |
| `ADP.7` | Parameters of the learning procedure itself | `ADP` | | The quantity updated is an initialisation, an optimiser, a loss or a hyperparameter, through an inner learning loop. | Excludes search over configurations with no gradient through the inner loop (`SRCH`). | MAML, FOMAML, Reptile, learned optimisers (L2O), meta-learned losses, hypergradient descent | |
| `ADP.8` | Change constrained by earlier tasks | `ADP` | How the constraint from earlier tasks is enforced | The permitted change is restricted by what the model learned in a previous task or stage. | Excludes constraints toward a reference model that is not a previous *task* (`OBJ.7.3` general case). | EWC, SI, LwF, PackNet, replay-based continual learning, GEM / A-GEM | Penalty-based members are multi-parent with `OBJ.7.3`. |

---

### Axis SRCH — Configuration and structure search

Scope: procedures that vary something *above* the parameters and select among the
results.

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `SRCH` | Configuration and structure search | — | What non-parameter choice the run varies and selects | The run executes multiple fits or candidate configurations and a named procedure picks or ranks them. | Excludes updating parameters within one fit (`FIT`). | — | The search *strategy* is read off `MACH`; see T5. |
| `SRCH.1` | Hyperparameters | `SRCH` | | The varied quantity is a numeric or categorical setting of an otherwise fixed procedure. | Excludes changes to the model's structure (`SRCH.2`). | grid search, random search, Bayesian optimisation (GP-EI, TPE, SMAC), Hyperband, ASHA, BOHB, population-based training | |
| `SRCH.2` | Architecture | `SRCH` | | The varied quantity is the model's computational graph. | Excludes scalar width/depth settings treated as ordinary hyperparameters. | NAS-RL, ENAS, DARTS, ProxylessNAS, Once-for-All, AmoebaNet / evolutionary NAS, MnasNet | |
| `SRCH.3` | Input features | `SRCH` | | The varied quantity is which of the available features the model is given. | Excludes constructing new features (`DAT.1.3`). | forward / backward stepwise selection, RFE, mutual-information filters, Boruta, LASSO-based selection | LASSO selection is multi-parent with `OBJ.7.1`. |
| `SRCH.4` | Data composition and augmentation policy | `SRCH` | | The varied quantity is the mixture, curriculum or augmentation policy applied to the data. | Excludes a single fixed policy applied once (`DAT`). | AutoAugment search, Population-Based Augmentation, DoReMi, data-mixture search | |
| `SRCH.5` | Prompts and programs | `SRCH` | | The varied quantity is a natural-language prompt or a program over model calls, selected against a scored objective. | Excludes hand-written prompts (`ADP.5`). | APE, automatic prompt search, DSPy optimisers, OPRO, evolutionary prompt search | |
| `SRCH.6` | Among fitted candidates | `SRCH` | | A named criterion selects one of several already-fitted models, or a stopping point. | Excludes criteria used only to report performance (`EST.10`). | cross-validated model selection, AIC / BIC, early stopping, stacking / super learner, nested CV | |
| `SRCH.7` | Whole pipeline | `SRCH` | | The varied quantity is the composition of preprocessing, model family and hyperparameters jointly. | Excludes search over one stage only. | auto-sklearn, TPOT, AutoGluon, H2O AutoML | |

---

### Axis EXEC — Execution and resource strategy

Scope: what the run partitions, defers, approximates or walls off so the
computation fits the hardware and the data-governance boundaries.

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `EXEC` | Execution and resource strategy | — | What the run divides, defers, approximates or restricts to fit the computation onto the available devices and data boundaries | A named procedure changes how the same mathematical update is physically carried out, or what information may cross a boundary. | Excludes changes to the mathematics of the update itself (`FIT`) and excludes the hardware (out of scope). | — | |
| `EXEC.1` | Replicate the model, split the batch | `EXEC` | How the replicas synchronise | Each worker holds the full model and a slice of the batch, and a named rule combines their gradients. | Excludes schemes that split the model itself (`EXEC.2`). | synchronous data parallel / allreduce (DDP), asynchronous SGD, Hogwild, parameter server, local SGD, post-local SGD | Gradient accumulation is the single-device analogue (`FIT.2.5`). |
| `EXEC.2` | Split the model | `EXEC` | Along which dimension the model is partitioned | The model's own tensors or layers are partitioned across devices. | Excludes replication schemes (`EXEC.1`). | tensor parallelism (Megatron), pipeline parallelism (GPipe, PipeDream, 1F1B), sequence / context parallelism, expert parallelism | |
| `EXEC.3` | Shard or offload the training state | `EXEC` | | Optimiser state, gradients or parameters are partitioned or moved off-device and gathered on demand. | Excludes partitioning of the forward computation (`EXEC.2`). | ZeRO-1/2/3, FSDP, ZeRO-Offload, CPU/NVMe offload | |
| `EXEC.4` | Trade compute for memory in time | `EXEC` | | Intermediate values are discarded and recomputed rather than stored. | Excludes reductions in precision (`EXEC.5`). | gradient / activation checkpointing, selective recompute, rematerialisation | |
| `EXEC.5` | Reduce numeric precision during fitting | `EXEC` | | The run represents activations, weights or gradients in fewer bits while still training. | Excludes precision reduction applied only after training (`PTX.1`). | AMP / fp16, bf16 training, fp8 training, quantisation-aware training, stochastic rounding | QAT straddles this and `PTX.1`; see T8. |
| `EXEC.6` | Reduce communicated volume | `EXEC` | | The content exchanged between workers is compressed by a named scheme, with or without error correction. | Excludes reductions in how often workers communicate (`EXEC.1`). | QSGD, 1-bit Adam, DGC, top-k sparsification, PowerSGD, error feedback | |
| `EXEC.7` | Keep data at its source | `EXEC` | How the decentralised updates are aggregated | Training data never leaves the participant that holds it; only updates or statistics are exchanged. | Excludes centralised multi-device training on pooled data (`EXEC.1`). | FedAvg, FedProx, SCAFFOLD, gossip SGD, split learning, secure aggregation | The federated-learning node. |
| `EXEC.8` | Bound information release | `EXEC` | | A named mechanism provides a formal guarantee about what the released model reveals about individual records. | Excludes informal privacy heuristics. | DP-SGD, PATE, local DP, DP-FTRL | Its clipping and noise mechanics are `FIT.2.5` and `FIT.9`. |
| `EXEC.9` | Exploit algorithmic structure for throughput | `EXEC` | | A named reformulation computes the same function with better memory or time characteristics. | Excludes approximations that change the function computed. | FlashAttention, fused kernels, paged attention, continuous batching, grouped GEMM | Borderline between algorithm and implementation; see T7. |

---

### Axis PTX — Post-fitting transformation

Scope: what is changed about an already-fitted model, after fitting, without a
new task objective (or with only a reconstruction/matching objective).

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `PTX` | Post-fitting transformation | — | What is changed about an already-fitted model after fitting | The procedure takes a finished model as input and emits a different model, without optimising the original task objective on task data. | Excludes any procedure that is part of fitting (`FIT`, `ADP`) and excludes procedures that leave the parameters alone (`OUT`). | — | |
| `PTX.1` | Reduce numeric precision | `PTX` | How the quantisation parameters are chosen | Weights or activations of a finished model are mapped to a lower-precision representation. | Excludes low precision used during training (`EXEC.5`). | post-training quantisation, GPTQ, AWQ, SmoothQuant, LLM.int8, GGUF k-quants | |
| `PTX.2` | Remove structure | `PTX` | What granularity of structure is removed | Parameters, channels or layers are set to zero or deleted from a finished model. | Excludes factorisation, which keeps all information in compressed form (`PTX.3`). | magnitude pruning, structured / channel pruning, SparseGPT, Wanda, lottery-ticket IMP, layer dropping | |
| `PTX.3` | Factorise parameters | `PTX` | | Parameter tensors are replaced by a low-rank or shared-parameter approximation. | Excludes zeroing of individual weights (`PTX.2`). | SVD compression, Tucker / CP decomposition, weight clustering and sharing | |
| `PTX.4` | Combine finished models | `PTX` | How the parameter sets are combined | Several independently finished parameter sets are combined into one set of weights. | Excludes combination maintained during training (`ADP.6`) and excludes ensembling at inference (`OUT.6`). | model soups, task arithmetic, TIES-merging, DARE, Fisher merging, SLERP merging | |
| `PTX.5` | Transfer into a different model | `PTX` | | A finished model is used only as a source of targets for fitting a different, usually smaller, model. | Excludes distillation used for performance rather than compression — same mechanism, different purpose. | distillation-for-compression, prune-then-distill, DistilBERT, TinyBERT | Multi-parent with `OBJ.5.1`; see T8. |
| `PTX.6` | Edit specific behaviour | `PTX` | What is used to localise the edit | A named procedure changes a targeted fact, capability or behaviour while leaving the rest of the model intact. | Excludes whole-model finetuning on new data (`ADP.2`). | ROME, MEMIT, task-vector negation, activation steering vectors, machine unlearning, SISA | |
| `PTX.7` | Recalibrate outputs | `PTX` | | A small post-hoc transform is fitted on held-out data to make the model's scores match observed frequencies. | Excludes changes to the model's own weights. | temperature scaling, Platt scaling, isotonic regression, vector scaling, bias correction | Pairs with `EST.8`. |

---

### Axis OUT — Output production

Scope: how the delivered output is produced from a fitted model **at fixed
parameters**. The brief's "beam search is in" rule lives here.

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `OUT` | Output production | — | How the delivered output is produced from the model at fixed parameters | A named procedure stands between the model's scores and the answer the run reports, and it changes no parameters. | Excludes anything that updates parameters (`ADP`, `FIT`) or rewrites them (`PTX`). | — | |
| `OUT.1` | Deterministic selection from scores | `OUT` | How much of the candidate space the maximisation considers | Given the same scores, the procedure always returns the same output, chosen to maximise a score. | Excludes any sampling (`OUT.2`). | greedy / argmax decoding, beam search, Viterbi, MAP assignment, best-of-n reranking by a scorer | |
| `OUT.2` | Stochastic sampling from scores | `OUT` | How the score distribution is truncated or reshaped before sampling | The output is drawn at random from a distribution derived from the model's scores. | Excludes deterministic maximisation (`OUT.1`). | ancestral sampling, temperature sampling, top-k, nucleus / top-p, min-p, typical sampling, Gumbel top-k | |
| `OUT.3` | Search over multi-step outputs | `OUT` | What guides the expansion of the search tree | The procedure simulates or expands multiple future continuations before committing to a step. | Excludes single-pass scoring of complete candidates (`OUT.1`). | MCTS at play time (AlphaZero, MuZero), tree-of-thoughts, lookahead planning, CEM / MPPI model-predictive control, A* decoding | Same MCTS appears at training time as `EXP.7`; two genuinely different roles. |
| `OUT.4` | Iterative refinement of a full output | `OUT` | What governs the refinement schedule | The output is produced by repeatedly revising a complete candidate rather than extending a partial one. | Excludes left-to-right generation (`OUT.1`, `OUT.2`). | DDPM ancestral sampling, DDIM, DPM-Solver, Langevin sampling, Mask-Predict, self-refine loops | Diffusion *sampling* is here; diffusion *training* is `OBJ.2.7`/`OBJ.4.3`. |
| `OUT.5` | Steering with an auxiliary signal or constraint | `OUT` | What supplies the steering signal | An external model, classifier or grammar modifies the scores before selection. | Excludes modifications derived only from the model's own scores (`OUT.2`). | classifier guidance, classifier-free guidance, contrastive decoding, constrained / grammar decoding, logit bias, FUDGE, PPLM, negative prompting | |
| `OUT.6` | Aggregation over multiple passes | `OUT` | How the multiple outputs are combined | The reported output is a function of several independent forward passes or models. | Excludes a single pass with internal search (`OUT.3`). | self-consistency voting, test-time augmentation, MC-dropout, deep-ensemble averaging, Bayesian posterior predictive averaging | |
| `OUT.7` | Conditioning on retrieved content | `OUT` | | External items are retrieved at inference and placed in the model's input or mixed into its scores. | Excludes retrieval used to build the training set (`DAT`). | RAG, kNN-LM, FiD, retrieval-augmented decoding, REPLUG | `speculative` for tool-use / agent scaffolds, which may or may not be named consistently. |
| `OUT.8` | Nonparametric prediction rules | `OUT` | | The prediction is computed directly from stored training examples at query time. | Excludes predictions from fitted parameters. | k-NN vote, Nadaraya-Watson kernel regression, locally weighted regression, nearest-centroid | Pairs with `FIT.8`; together they cover "algorithm with no model". |
| `OUT.9` | Cost-reducing output procedures | `OUT` | What is skipped or approximated | The procedure produces the same or near-same output with less computation per output. | Excludes procedures that change the output distribution deliberately (`OUT.5`). | speculative decoding, Medusa, early exit, cascades, draft-and-verify, KV-cache compression | |
| `OUT.10` | Approximate inference in structured models | `OUT` | | Marginals or MAP states of a structured probabilistic model are computed by a named message-passing or sampling scheme at query time. | Excludes parameter estimation by the same machinery (`FIT.7`). | belief propagation, loopy BP, variational message passing, particle filtering at inference, junction tree | |

---

### Axis MACH — Computational strategy (crosscut)

Scope: the mathematical or algorithmic family the procedure runs on. This axis is
**not** a role; it crosscuts all ten. It exists because the field names these
families and asks aggregate questions about them, and because the same family
recurs in `FIT`, `SRCH`, `DAT` and `OUT` with no common ancestor otherwise.
This is the weakest part of the proposal (T5).

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| `MACH` | Computational strategy | — | What kind of mathematical object or search the procedure fundamentally manipulates | The procedure's mechanism can be named with a family term the field uses. | Excludes claims about where the procedure sits in the run (that is the role axes). | — | One level only, deliberately. |
| `MACH.1` | Exhaustive enumeration | `MACH` | | The procedure evaluates every candidate in a finite set. | Excludes any sampling or pruning. | grid search, exhaustive feature subsets, full Viterbi over small state spaces | |
| `MACH.2` | Random sampling / Monte Carlo | `MACH` | | The procedure's core step draws samples and averages or selects among them. | Excludes deterministic enumeration. | random search, Monte Carlo rollouts, bootstrap, MC-dropout, randomised sketching | |
| `MACH.3` | Gradient following | `MACH` | | The core step moves along a first derivative of a differentiable surrogate. | Excludes derivative-free and curvature-based steps. | SGD and descendants, DARTS, gradient-based dataset distillation, guided diffusion | |
| `MACH.4` | Curvature / second-order | `MACH` | | The core step uses a Hessian or an approximation of it. | Excludes diagonal adaptive scaling heuristics. | Newton, L-BFGS, K-FAC, natural gradient, Laplace approximation | |
| `MACH.5` | Bandit / sequential resource allocation | `MACH` | | The procedure allocates a budget across arms using observed partial results and an explore-exploit rule. | Excludes fixed-budget-per-candidate schemes. | Hyperband, ASHA, UCB, Thompson sampling, successive halving | |
| `MACH.6` | Bayesian probabilistic inference | `MACH` | | The procedure reasons explicitly about a posterior over unknowns. | Excludes point estimation with a regularisation term that merely *corresponds* to a prior. | Bayesian optimisation, MCMC, variational inference, Bayesian NNs, Gaussian processes, SMC | |
| `MACH.7` | Evolutionary / population | `MACH` | | The procedure maintains a population of candidates and generates new ones by variation and selection. | Excludes single-point iterative schemes. | CMA-ES, genetic algorithms, NEAT, AmoebaNet, PBT, OpenAI-ES | Redundant with `FIT.6`; see T5. |
| `MACH.8` | Kernel / RKHS | `MACH` | | The procedure operates through inner products in an implicit feature space defined by a kernel. | Excludes explicit finite feature maps. | SVM, kernel ridge, Gaussian processes, kernel PCA, MMD, Nystrom approximation | |
| `MACH.9` | Spectral / matrix and tensor factorisation | `MACH` | | The core step is an eigen-, singular-value or tensor decomposition. | Excludes iterative gradient fitting of a factorised model. | PCA, spectral clustering, SVD compression, NMF (ALS form), Tucker / CP, randomised SVD | |
| `MACH.10` | Combinatorial search and dynamic programming | `MACH` | | The core step searches a discrete space with pruning, memoisation or optimal substructure. | Excludes continuous optimisation. | beam search, Viterbi, MCTS, A*, CART split search, branch-and-bound, Apriori | |
| `MACH.11` | Game-theoretic / adversarial | `MACH` | | The procedure optimises a minimax or equilibrium objective between two or more optimising parties. | Excludes single-objective optimisation against a fixed target. | GAN family, adversarial training, GAIL, self-play, PSRO | |
| `MACH.12` | Optimal transport / geometric | `MACH` | | The core step computes a transport plan, a geodesic or a metric alignment between distributions or manifolds. | Excludes divergence computations with no transport structure. | Sinkhorn, Wasserstein distances, Gromov-Wasserstein, SWD, UMAP's manifold step | |
| `MACH.13` | Information-theoretic | `MACH` | | The procedure's criterion is an explicit mutual-information or entropy quantity. | Excludes losses that happen to be cross-entropy against labels. | InfoMax, information bottleneck, BALD, MINE, entropy regularisation | `speculative` as an aggregation target. |
| `MACH.14` | Message passing on graphs | `MACH` | | The core step propagates local quantities along a graph until convergence. | Excludes graph neural networks as models (models dimension). | belief propagation, label propagation, PageRank, loopy BP, gossip averaging | `speculative`. |

**Node count:** `DAT` 23, `EXP` 12, `OBJ` 45, `FIT` 18, `EST` 11, `ADP` 9,
`SRCH` 8, `EXEC` 10, `PTX` 8, `OUT` 11, `MACH` 15 — **170 nodes across 11 axes.**

---

## Worked examples

Every named method is placed against **all eleven axes**. `—` means the method
says nothing about that axis, which is the normal case. A `*` marks the **home**
axis (the anchoring rule): the axis carrying the method's defining contribution
and the one any lineage edge is drawn on.

| method | DAT | EXP | OBJ | FIT | EST | ADP | SRCH | EXEC | PTX | OUT | MACH | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **PPO** | — | `EXP.1` | `OBJ.3.2`* , `OBJ.7.3` | — | `EST.1` | — | — | `EXEC.1` | — | — | `MACH.3` | The brief's case, confirmed: PPO fixes objective and experience and **delegates** the step, so it has no `FIT` value at all. A run is PPO + Adam + two slots. |
| **DQN** | — | `EXP.2.1`, `EXP.2.3` | `OBJ.3.1`* | — | `EST.1` | `ADP.1` | — | — | — | `OUT.1` | `MACH.3` | One name, four axes. Replay and epsilon-greedy are separately nameable and separately counted. |
| **Rainbow** | — | `EXP.2.1`, `EXP.2.3` | `OBJ.3.1.1`* | — | `EST.1` | — | — | — | — | — | `MACH.3` | Resolves awkwardly. Rainbow is *defined* as a bundle of seven changes across three axes; calling `OBJ.3.1` its home is a convention, not a fact about the paper. See T1. |
| **CQL** | — | `EXP.3` | `OBJ.3.1`, `OBJ.7.3`* | — | `EST.1` | — | — | — | — | — | `MACH.3` | Clean: offline RL = an experience regime plus a conservatism penalty. The `EXP.3`/`OBJ.7.3` pair is exactly how the sub-field describes itself. |
| **AlphaZero** | — | `EXP.5`, `EXP.7` | `OBJ.1.1`, `OBJ.1.2`* | `FIT.2.3` | `EST.1` | `ADP.1` | — | `EXEC.1` | — | `OUT.3` | `MACH.10`, `MACH.11` | Five axes. Note MCTS appears twice with different roles — `EXP.7` at training, `OUT.3` at play — and that is correct, not duplication. |
| **SimCLR** | `DAT.1.1` | — | `OBJ.2.3`* | `FIT.2.3` | `EST.1` | `ADP.1` | — | `EXEC.1` | — | — | `MACH.3` | The augmentation is a separate, separately-counted algorithm; SimCLR without `DAT.1.1` is not SimCLR, but the two are different slots. |
| **SPR** | `DAT.1.1` | `EXP.2.3` | `OBJ.2.4`*, `OBJ.3.1` | — | `EST.1` | — | — | — | — | — | `MACH.3` | The orthogonality case. SPR's home is a *self-supervised* objective node while it sits on an off-policy RL experience regime. No branch choice is forced. |
| **ConSpec** | — | `EXP.2.3` | `OBJ.2.3`*, `OBJ.3.1` | — | `EST.1` | — | — | — | — | — | `MACH.3` | Agrees with SPR on `EXP`, differs on `OBJ`. The instrument the brief supplied fires and the structure survives it. |
| **BERT pretraining (MLM)** | `DAT.1.3` | — | `OBJ.2.1`* | `FIT.2.3` | `EST.1` | `ADP.1` | — | `EXEC.1` | — | — | `MACH.3` | Tokenisation is in scope and separately named; "BERT" the weights is the models dimension. |
| **DDPM** | — | — | `OBJ.2.7`, `OBJ.4.3`* | `FIT.2.3` | `EST.2` | `ADP.1` | — | — | — | `OUT.4` | `MACH.3` | Double-homed in `OBJ` (denoising pretext *and* score matching) — genuinely both, see T4. Training and sampling split across `OBJ` and `OUT`, which I think is right: DDIM swaps the sampler and keeps the objective. |
| **Classifier-free guidance** | — | — | — | — | — | — | — | — | — | `OUT.5`* | `MACH.3` | Resolves awkwardly. CFG requires a *training-time* change (dropping the condition) that has no node — the closest is `DAT.3`, which is wrong. See T12. |
| **WGAN** | — | — | `OBJ.5.2`*, `OBJ.4.5` | `FIT.2.3` | `EST.2` | `ADP.1` | — | — | — | `OUT.2` | `MACH.11`, `MACH.12` | The adversarial critic and the Wasserstein objective are two statements about signal source; both are true. |
| **AdamW** | — | — | `OBJ.7.1` | `FIT.2.3`* | — | — | — | — | — | — | `MACH.3` | The `OBJ.7.1` value is real: decoupled weight decay *is* an L2 penalty, applied in the step rather than the loss. Flagged in T13. |
| **SAM** | — | — | — | `FIT.2.4`* | — | — | — | — | — | — | `MACH.3` | Clean single-axis. Composes with AdamW: two `FIT` entries in one run — a within-slot composition, allowed under the functional reading. |
| **CMA-ES** | — | — | — | `FIT.6`* | — | — | — | — | — | — | `MACH.7` | Clean, but `FIT.6` and `MACH.7` say nearly the same thing. See T5. |
| **XGBoost** | `DAT.2.2` | — | `OBJ.1.1`, `OBJ.1.2`, `OBJ.7.1` | `FIT.5`* | `EST.1` | — | — | `EXEC.1` | — | — | `MACH.10` | Classical ML lands in a first-class node, not an afterthought. Column subsampling is `DAT.2.2`-adjacent and is the weakest of these assignments. |
| **Random forest** | `DAT.2.2` | — | — | `FIT.5`* | `EST.1` | — | — | — | — | `OUT.6` | `MACH.2` | Resolves awkwardly: bagging is "resampling of examples" (`DAT.2.2`) but it is really an *ensemble construction* rule, which only `ADP.6` half-covers. See T14. |
| **k-NN** | — | — | — | `FIT.8`* | `EST.1` | — | — | — | — | `OUT.8` | — | A legal algorithm with **no model** entity. `FIT.8` + `OUT.8` is the pattern for every instance-based method. |
| **SVM (SMO)** | — | — | `OBJ.1.1`, `OBJ.7.1` | `FIT.4`* | `EST.1` | — | — | — | — | — | `MACH.8` | Hinge loss, margin penalty, SMO as the alternating surrogate solver, kernel as the machinery. Four facts, four places. |
| **EM for a GMM** | — | — | `OBJ.4.1` | `FIT.4`* | `EST.2`, `EST.3` | — | — | — | — | — | — | No `MACH` value: EM is not kernel, Bayesian, spectral or evolutionary. An honest `—` on the crosscut, which is partly why I distrust that axis. |
| **HMC / NUTS** | — | — | `OBJ.4.6` | `FIT.7`* | `EST.8` | — | — | — | — | `OUT.10` | `MACH.6`, `MACH.2` | Statistics gets a full row across five axes; nothing about this ontology is deep-learning-shaped at this point. |
| **t-SNE** | `DAT.1.4`* | — | `OBJ.4.5` | `FIT.2.1` | `EST.3` | — | — | — | — | — | `MACH.12` | Second "algorithm with no model" case: transductive, no out-of-sample map. Home is `DAT` because in a run it is consumed as a representation. Arguable — `EST.3` has a claim. |
| **Double machine learning** | — | — | — | `FIT.2.x` or `FIT.5` (nuisance) | `EST.4`*, `EST.10` | — | — | — | — | — | `MACH.3` | **The proof that `EST` is its own axis**: DML co-occurs with XGBoost in one run, so identification and parameter fitting cannot be siblings. |
| **Difference-in-differences** | — | — | — | `FIT.1` | `EST.5`* | — | — | — | — | — | — | Pure classical econometrics, no model artefact, no loss, no optimiser. If the structure could not hold this row, rule 1 would be unmet. |
| **Conformal prediction** | — | — | — | — | `EST.8`* | — | — | — | — | `OUT.6` | `MACH.2` | Resolves awkwardly: it is an inference-time *construction* with an `EST` guarantee. I split it rather than inventing a node. |
| **LoRA** | — | — | — | — | — | `ADP.4`* | — | — | — | — | — | A **pure scope statement**: no objective, no optimiser, no data claim. The cleanest demonstration that `ADP` is a real, separable slot. |
| **QLoRA** | — | — | — | — | — | `ADP.4`* (descent from LoRA) | — | `EXEC.3` | `PTX.1` | — | — | Three axes for one name: adapters, a quantised frozen base, and paged offloading. |
| **Instruction tuning (SFT)** | `DAT.4.2` | — | `OBJ.1.1`* | `FIT.2.3` | `EST.1` | `ADP.2` or `ADP.4` | — | — | — | — | `MACH.3` | The `ADP` value genuinely varies by run — this is a case where an axis value is a property of *use*, not of the named procedure. Flagged in T15. |
| **DPO** | — | — | `OBJ.6.2`*, `OBJ.7.3` | `FIT.2.3` | `EST.1` | `ADP.2` | — | — | — | — | `MACH.3` | The implicit KL-to-reference is a real second `OBJ` value, and it is what makes DPO comparable to RLHF. |
| **RLHF (full pipeline)** | — | `EXP.1` | `OBJ.6.1`*, `OBJ.5.3`, `OBJ.3.2`, `OBJ.7.3` | `FIT.2.3` | `EST.1` | `ADP.2` | — | `EXEC.1` | — | `OUT.2` | `MACH.3` | The worst row in the table: **six `OBJ` values**. "RLHF" is a pipeline name, not an algorithm, and the structure says so loudly. See T1. |
| **FedAvg** | — | — | — | `FIT.2.1` | `EST.1` | — | — | `EXEC.7`* | — | — | — | Clean. Federated learning is an execution-and-governance statement, and FedProx adds `OBJ.7.3` on top — exactly the right discrimination. |
| **ZeRO-3 / FSDP** | — | — | — | — | — | — | — | `EXEC.3`* | — | — | — | Single-axis, mathematically a no-op on the update. Good evidence that `EXEC` is a real slot and not a disguised `FIT`. |
| **CutMix** | `DAT.1.2`* | — | — | — | — | — | — | — | — | — | `MACH.2` | The brief's canonical in-scope data entry, placed in one node with no strain. |
| **BPE tokenisation** | `DAT.1.3`* | — | — | `FIT.5` | — | — | — | — | — | — | `MACH.10` | The `FIT.5` value is real and slightly surprising: learning a BPE vocabulary *is* greedy structure growth. |
| **Beam search** | — | — | — | — | — | — | — | — | — | `OUT.1`* | `MACH.10` | In scope by the brief's rule; one node, one test. |
| **Nucleus (top-p) sampling** | — | — | — | — | — | — | — | — | — | `OUT.2`* | `MACH.2` | Sibling of top-k and temperature under "how the score distribution is truncated"; these do compose, which the functional reading permits. |
| **Speculative decoding** | — | — | — | — | — | — | — | — | — | `OUT.9`* | `MACH.2` | Needs a draft model — a second *model* entity, not a second algorithm. The models/algorithms boundary holds. |
| **GPTQ** | — | — | — | `FIT.1` | — | — | — | — | `PTX.1`* | — | `MACH.4` | Pleasingly, GPTQ's `MACH.4` (Hessian-based error compensation) is non-obvious and would be invisible without the crosscut axis. One point in `MACH`'s favour. |
| **MAML** | — | — | — | `FIT.2.7`, `FIT.2.3` | `EST.1` | `ADP.7`* | — | — | — | — | `MACH.3` | Meta-learning as a scope statement about *which* parameters (the initialisation) plus an estimator for the inner-loop gradient. |
| **Hyperband** | — | — | — | — | — | — | `SRCH.1`* | `EXEC.1` | — | — | `MACH.5` | Clean, and `MACH.5` is the only place "bandit" aggregates. |
| **DARTS** | — | — | — | `FIT.2.3`, `FIT.2.7` | — | — | `SRCH.2`* | — | — | — | `MACH.3` | Co-occurs with Adam in one run, which is exactly why `SRCH` cannot be a branch of `FIT`. |
| **TENT (test-time adaptation)** | — | — | **gap** | `FIT.2.1` | — | `ADP.3`* | — | — | — | — | `MACH.13` | **Two failures in one row.** (a) Entropy minimisation on the model's own output has no `OBJ` node — the signal source is "the model itself", which my seven-way division of `OBJ` does not contain. (b) Nothing aggregates "test-time adaptation", because `ADP` is scope-only. See T2 and T12. |
| **DrQ** | `DAT.1.1` | `EXP.2.3` | `OBJ.3.1`* | `FIT.2.3` | `EST.1` | — | — | — | — | — | `MACH.3` | The row that proves `DAT` and `EXP` must be separate axes: shift augmentation and replay co-occur and serve different functions. |

---

## Tensions

**T1 — Pipeline names are not algorithms, and the structure has no way to say so.**
`RLHF` takes six `OBJ` values; `Rainbow` is a declared bundle; `AlphaZero` spans
five axes. The anchoring rule gives each a home so lineage chains stay clean, but
the home is a convention I imposed, not something the introducing paper states.
If annotators record "RLHF" as one algorithm string, the structure will
faithfully explode it into six nodes and the roll-ups will double-count relative
to a paper that wrote "PPO + reward model". I do not have a fix. The honest
version is probably a node type I did not create: *composite/pipeline*, whose
only content is "expands to this set".

**T2 — There is no aggregation node for "test-time adaptation", and that is a
real loss.** I kept `ADP` strictly scope-only ("which parameters"), because
mixing in *when* would be two principles of division in one sibling set. The
price is that TENT, test-time training and online adaptation decompose into
`ADP.3` + an objective and nothing rolls them up. The alternative I rejected was
a crosscutting `TIME` axis (before fitting / during / post-hoc / at each
prediction); I rejected it because it is ~80% redundant with the role axes
themselves (`DAT` = before, `FIT` = during, `PTX` = post-hoc, `OUT` = at
prediction) and would earn its keep only for the handful of methods defined by
their timing. I am genuinely unsure this was right. If phase 2 shows
test-time-adaptation names are common, add the axis.

**T3 — `FIT.9` (dropout, stochastic depth, gradient noise) violates its parent's
characteristic.** `FIT`'s characteristic is "what information about the objective
decides the next parameter values". Dropout decides nothing; it *perturbs* the
computation. I kept it under `FIT` because the alternatives are worse — it is not
data (`DAT.1.1` is about examples), not a loss term (`OBJ.7` requires a term in
the objective), and treating dropout as a model layer pushes a training-only
procedure into the models dimension where it would silently vanish at inference.
This is the single clearest rule-3 violation in the draft and I am flagging it
rather than hiding it.

**T4 — `OBJ` is 43 nodes, a quarter of the whole structure, and several of its
members are double-homed.** Per rule 5 I did not rebalance. But the double-homing
is worth naming: the diffusion training loss is simultaneously `OBJ.2.7`
(denoising pretext) and `OBJ.4.3` (score matching); GAIL is `OBJ.3.6` and
`OBJ.5.2`; the RLHF reward model is `OBJ.5.3` and `OBJ.6.1`. Rule 6 says this
costs nothing semantically, and I believe that, but it means "proportion of
papers with a self-supervised objective" and "...with a likelihood objective"
will overlap in a way readers may not expect. Roll-ups from `OBJ` need an
explicit statement that the children are not a partition.

**T5 — `MACH` is the weakest axis and partly redundant.** `MACH.7`
(evolutionary) and `FIT.6` (derivative-free population search) are nearly the
same set. `MACH.3` (gradient following) is implied by any `FIT.2` value. The axis
earns its keep only where a strategy recurs across roles with no common ancestor
— bandit allocation in `SRCH.1` and exploration in `EXP.2.1`; kernels in `FIT.4`,
`OBJ.4.5` and `OUT.8`; second-order structure surfacing unexpectedly in GPTQ. If
phase 2 shows annotators never supply a `MACH` value, delete the axis; nothing
else depends on it. It is the first thing I would cut.

**T6 — `DAT`'s four children compose freely, so a stricter reading would split
`DAT` into four axes.** Augmentation, active learning, pseudo-labelling and
synthetic data genuinely co-occur in a single run (FixMatch is three of them).
Under the naive reading of rule 2 they cannot be siblings. I kept them together
because they share one characteristic ("what the procedure changes about the
training stream") and because annotators think of "the data pipeline" as one
thing. But the `DrQ` row shows I *did* split `DAT` from `EXP` on exactly this
ground, so my line is not principled — it is a judgement that interaction is a
bigger difference than relabelling. Someone could reasonably draw it elsewhere.

**T7 — The algorithm/implementation boundary is unresolved at `EXEC.9`.** Is
FlashAttention a named procedure a run executes, or a kernel the library
provides? By the participant rule it is the former — it is named, and the run
executes it. But the same argument admits fused optimisers, paged attention and
eventually any cuDNN path, and those will be reported inconsistently because they
are usually a library flag. I included the node with a warning. If phase 2 shows
these names appear mostly in `libraries[]`, the node should be deleted rather
than kept half-populated.

**T8 — Three seams where the same method appears twice for a defensible reason,
and annotators will not agree.** (a) Distillation is `OBJ.5.1` (a loss) and
`PTX.5` (a compression workflow) — the split is by *purpose*, which is a property
of use, exactly what the brief warns against. (b) Quantisation-aware training is
`EXEC.5` and `PTX.1`. (c) Weight averaging is `ADP.6` during training and `PTX.4`
after. Each seam is decided by a timing or purpose question rather than by the
procedure itself, and each is a place I expect disagreement.

**T9 — Exploration rules and decoding rules are the same kind of object and I
separated them anyway.** `EXP.2.1` (epsilon-greedy, Boltzmann, UCB, Thompson) and
`OUT.1`/`OUT.2` (greedy, temperature, top-p) are both "a rule for selecting from
a scored candidate set"; so are acquisition functions in `SRCH.1` and PUCT inside
MCTS. Unifying them would be elegant and would let "proportion using Thompson
sampling" roll up in one place. I did not do it because an annotator asked
"is nucleus sampling a sibling of epsilon-greedy?" would say no, and because the
brief names decoding as its own concern. This is the structure's most interesting
unused idea.

**T10 — The `DAT.3` / `OBJ.2` seam is thin.** Both manufacture targets from
unlabelled data. I drew the line at "does the target become a stored training
label (`DAT.3`) or is it defined by the loss on the raw input (`OBJ.2`)". FixMatch
sits astride it (pseudo-label *and* consistency loss), as does consistency
regularisation generally, which I placed in `OBJ.7.2` while its augmentation sits
in `DAT.1.1`. A run using mean teacher gets three nodes on three axes, which is
correct but feels heavier than the method does.

**T11 — `EST.1` is close to vacuous for deep learning.** Almost every ML paper is
`EST.1`, so the `EST` axis carries very little information for the bulk of the
corpus. I kept it because deleting it would make `EST` an axis that only causal
and statistical papers populate, which reintroduces exactly the "classical work
is an afterthought" failure rule 1 forbids. The contrast class has to exist for
the axis to be an axis. But expect `EST` to look lopsided.

**T12 — Two gaps the worked examples exposed that I did not patch.** (a) `OBJ`
has no node for *the model's own output as the training signal* — entropy
minimisation (TENT), self-training without stored labels, confidence
regularisation. My seven-way division (annotation / input / reward / probability
model / another model / preference / the hypothesis) has no slot for "this same
model". The honest fix is an eighth child; I left it as a gap because I want
phase 2 to say how big it is. (b) Classifier-free guidance requires a
training-time condition-dropout that has no node, so CFG is recorded as
inference-only, which understates it.

**T13 — `AdamW` carries an `OBJ.7.1` value, which looks like a category error
and is not.** Decoupled weight decay is an L2 penalty implemented in the update
rather than in the loss. The structure is right and the annotation will look
wrong to a reader. The same applies to gradient clipping inside DP-SGD
(`FIT.2.5` serving `EXEC.8`). Where a mechanism's mathematical identity and its
implementation site differ, I followed the identity, and I am not certain that
is the more useful convention for a literature review.

**T14 — Bagging has no good home.** Random forests resample examples
(`DAT.2.2`), grow trees greedily (`FIT.5`) and vote (`OUT.6`), but "bagging" as a
named ensemble-construction procedure is none of those cleanly — `ADP.6` is about
parameter sets maintained during one fit, not independently fitted members. The
`ADP.6` / `PTX.4` / `OUT.6` trio covers ensembling three times and still misses
the construction rule. A dedicated "ensemble construction" node, probably on
`ADP`, is likely needed.

**T15 — Some axis values are properties of use after all.** Instruction tuning's
`ADP` value is `ADP.2` in one paper and `ADP.4` in the next; that is a property of
the run, not of the procedure. The use-test was my main instrument for killing
level-1 candidates, and I am applying it less strictly to secondary values than
to homes. The defensible version of this is: **a home axis value must be
intrinsic; secondary values may be run-dependent and are therefore properties of
the run, which is fine because the annotation unit is a run.** That is a coherent
position but I arrived at it after the fact.

**T16 — Eleven axes is a lot, and I cannot prove the count is right.** The claim
is that ML's dataflow has about ten stations, and that this is a finding about
the field. The alternative — that I over-decomposed and three or four axes would
carry everything — is live. The check is in phase 2: if `SRCH`, `PTX`, `EST` and
`MACH` are populated by a thin tail of names each, the axis set should be
collapsed, probably to {data+experience, objective, fitting, scope, execution,
output}.
