Frozen: Tue Oct  6 04:20:03 PM UTC 2026

# Draft ontology of machine-learning algorithms — Phase 1 (knowledge-only, no corpus)

The shape I arrived at is a **forest of lineage families crossed with three facets**. Lineage is not
rooted in a single tree and has no imposed top-level taxonomy: imposing one would have required
dividing the whole field by *something*, and every candidate divider (slot, signal, problem class) is
already one of the facets, so the top of lineage would have duplicated a facet and then immediately
broken on families whose descendants drift across it — diffusion is the clearest case, where DDPM is a
training objective and its own descendant DDIM is a decoder. So lineage is 94 independent family
roots, each 2-4 levels deep, and *grouping* families is the job of `role` and `signal`. The second
structural change is inside `signal`: the hypothesis mixed *where the target comes from* (label,
reward, reconstruction) with *how prediction and target are compared* (likelihood, score, contrast),
which are orthogonal — supervised classification and autoregressive pretraining share a form
(likelihood) and differ in source; BYOL and SimCLR share a source and differ in form. I split `signal`
into two multi-valued sub-facets, `signal.source` and `signal.form`, and added `S.src.none` because a
large and legitimate part of this dimension (beam search, BPE, CutMix, pruning) fits nothing at all.
`role` kept all eleven hypothesised slots but grew six more (initialization, gradient post-processing,
retrieval/context construction, calibration, prediction rule, parameter-space rewriting) and lost "compression", which
turned out to be a *goal* rather than a slot: pruning and quantization rewrite parameters, distillation
is an objective, and they only look like one category because people reach for them for the same
reason. `attributes` became 16 families, each declared single- or multi-valued, with `federated`
demoted from a standalone flag to a value of a coordination-topology family. The faceted hypothesis
survives the orthogonality test cleanly (SPR and ConSpec sit in different lineages, share
`role`=objective and `attributes`=off-policy/model-free, and differ only on `signal.form`), and the
structure's main strain is at its edges, not its centre: see `## Tensions`.

Node counts: lineage 351 (94 family roots), signal 52, role 45, attributes 76 (16 families + 60 values). Total 524.

**Reading conventions.** `node_id` prefixes: `L.` lineage, `S.` signal, `R.` role, `A.` attributes.
A node's `parents` column is empty for a root. In the lineage tables, `characteristic` is filled only
where the children are *divisions*; it is blank where parent to child means *descent* (the child paper
frames itself as deriving from the parent). Leaf variants that add no new test live in `examples`, not
as nodes — that is how depth stays at 3-4 without padding. Multi-parent entries are written
`parentA; parentB`. The `###` headings inside the lineage section are **navigational only, not nodes**;
they group families by the role their founder occupies, purely so the table can be read.

---

## Axis 1 — lineage

**What this axis is.** Descent between named methods, as framed by the paper that introduced the
descendant. This is the aggregation surface: "what proportion of papers used a DQN-family algorithm"
is a roll-up here. Admission to this axis requires a *name*; an unnamed procedure has no lineage.

**Axis-level test.** Positive: the entity is a named procedure, and either it founds a family or a
paper introducing it positions it as a modification of a specific named predecessor. Negative: a
procedure that is only described, never named; a dataset, library, hardware or architecture; a
property of a method rather than a method.

### Data preparation families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.tok | Subword vocabulary induction | | criterion by which the next vocabulary item is chosen | fits a finite token vocabulary to a corpus before any model is trained | a fixed hand-written vocabulary or a whitespace split with no induction step | BPE, WordPiece, Unigram LM | tokenizer choice is reported as a method, not a library setting |
| L.tok.bpe | Byte-pair-encoding merges | L.tok | | merges the most frequent adjacent pair, iteratively, to a target vocabulary size | likelihood-driven vocabulary pruning | BPE, byte-level BPE, SentencePiece-BPE | |
| L.tok.wp | Likelihood-gain merges | L.tok | | merges the pair that most increases corpus likelihood under a unigram model | pure frequency counting | WordPiece | |
| L.tok.uni | Vocabulary pruning from a superset | L.tok | | starts from a large candidate set and removes items that cost least likelihood | bottom-up merging | Unigram LM, SentencePiece-Unigram | |
| L.tok.byte | Tokenizer-free byte or character units | L.tok | | uses raw bytes or characters, so no vocabulary is induced from data | any corpus-fitted vocabulary | ByT5 scheme, CANINE scheme, character-level LM input | boundary: arguably the absence of an algorithm |
| L.aug | Input-space data augmentation | | what is transformed and how the transform is chosen | replaces or perturbs a training example with a transformed version, leaving the label rule intact | transformations applied at test time only; architectural noise layers | RandAugment, CutMix, SpecAugment | |
| L.aug.geom | Geometric and photometric transforms | L.aug | | applies a fixed hand-specified image transform family with sampled parameters | transforms whose parameters are themselves learned or searched | random resized crop, horizontal flip, rotation, color jitter | named weakly; include only when the paper names the recipe |
| L.aug.erase | Occlusion and erasing | L.aug | | deletes a contiguous region of the input and does not replace it with other data | mixing two examples together | Cutout, Random Erasing, GridMask, token dropout | |
| L.aug.mix | Example mixing | L.aug | | builds a training example by combining two or more examples and their labels | single-example perturbation | mixup, CutMix, Manifold Mixup, FMix, Mosaic, AugMix | label is mixed too, which also touches the objective |
| L.aug.policy | Searched augmentation policies | L.aug; L.hpo | | selects which augmentations to apply by searching over policies against a validation signal | a fixed augmentation list chosen by hand | AutoAugment, Fast AutoAugment, RandAugment, TrivialAugment, PBA | sits on two axes at once by construction |
| L.aug.text | Text-space augmentation | L.aug | | perturbs tokens or re-generates text while preserving the label | prompt engineering at inference | EDA, back-translation, synonym substitution, round-trip translation | |
| L.aug.adv | Adversarial example generation | L.aug; L.robust | | constructs an input perturbation that maximises the model's loss under a norm budget | random noise with no maximisation step | FGSM, PGD, C&W, AutoAttack | same procedure serves as attack and as training-data source |
| L.resamp | Class-imbalance resampling | | whether examples are added, removed or synthesised | changes the class frequencies seen by the learner, without changing the loss definition | a reweighted loss, which is an objective change | SMOTE, ADASYN, Tomek links, NearMiss, random oversampling | |
| L.curate | Dataset curation and selection | | what score decides whether an example is kept, ordered or weighted | selects, deduplicates, weights or orders the training examples before or during fitting | generating new examples; transforming individual examples | SemDeDup, DoReMi, curriculum learning | |
| L.curate.dedup | Near-duplicate removal | L.curate | | removes examples that are near-identical to another under a similarity threshold | removing examples for being low-quality rather than redundant | MinHash/LSH dedup, SemDeDup, exact-substring dedup | |
| L.curate.filter | Quality and contamination filtering | L.curate | | drops examples scored below a threshold by a classifier, perplexity model or rule | dropping examples to balance classes | quality classifier filtering, perplexity filtering, decontamination | |
| L.curate.mix | Domain mixture weighting | L.curate | | chooses sampling proportions across labelled data sources | choosing which single corpus to use | DoReMi, DoGE, hand-tuned domain weights | |
| L.curate.order | Curriculum ordering | L.curate | | changes the order or schedule in which examples are presented, not which are present | changing the set of examples | curriculum learning, self-paced learning, anti-curriculum, sequence-length warmup | |
| L.curate.active | Active and coreset selection | L.curate | | repeatedly selects which unlabelled points to label or keep, using the current model | a one-shot random subsample | uncertainty sampling, BALD, core-set selection, GraNd, EL2N | |
| L.curate.distill | Dataset distillation | L.curate | | optimises a small synthetic dataset so that training on it reproduces training on the full set | compressing the model rather than the data | dataset distillation, gradient matching, distribution matching | |
| L.prep | Classical feature preprocessing | | what statistic of the training data the transform is fitted to | fits a fixed transform to the training split and applies it to every split | a transform with no fitted parameters | z-scoring, ZCA whitening, target encoding | |
| L.prep.scale | Location-scale and whitening transforms | L.prep | | removes mean and rescales or decorrelates using first and second moments | rank-based transforms | standardisation, min-max scaling, PCA whitening, ZCA whitening | |
| L.prep.rank | Rank and quantile transforms | L.prep | | maps values through their empirical rank or quantile | moment-based rescaling | quantile normalisation, rank-gauss, Box-Cox, Yeo-Johnson | |
| L.prep.disc | Discretisation and encoding | L.prep | | converts a continuous or categorical column into a new coded representation | continuous rescaling | equal-width/equal-frequency binning, MDLP, one-hot, target/mean encoding | |
| L.prep.impute | Missing-data imputation | L.prep | | fills missing entries with values estimated from observed data | dropping incomplete rows | mean/median imputation, MICE, kNN imputation, matrix-completion imputation | |
| L.prep.select | Feature selection | L.prep; L.lin.pen | | removes input variables before or during fitting based on a relevance score | projecting features into a new space | mutual-information filtering, recursive feature elimination, lasso selection, Boruta | |
| L.synth | Synthetic training-data generation | | what produces the synthetic example | creates new training examples from a model, a simulator or a rule, rather than transforming real ones | perturbing an existing real example | Self-Instruct, domain randomisation, Evol-Instruct | |
| L.synth.model | Model-generated corpora | L.synth | | a generative model emits the training examples, optionally filtered | a human or simulator emits them | Self-Instruct, Alpaca-style generation, Evol-Instruct, synthetic textbooks | overlaps distillation when the generator is a stronger model |
| L.synth.sim | Simulation and domain randomisation | L.synth | | a simulator with randomised parameters emits examples to cross a reality gap | data collected in the target domain | domain randomisation, procedural scene generation, sim-to-real pipelines | |
| L.synth.cf | Counterfactual example construction | L.synth; L.causal | | constructs an example differing in one causal factor while holding others fixed | arbitrary perturbation with no factor held fixed | counterfactual data augmentation, CAD, minimal-pair generation | |

### Experience-generation families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.explore | Exploration rules | | what quantity drives the deviation from the greedy action | decides which action to take for the purpose of gathering data, separately from the update rule | a rule that defines the learning target rather than action selection | epsilon-greedy, UCB1, RND | the single most under-named slot in RL papers |
| L.explore.rand | Undirected stochastic exploration | L.explore | | perturbs the greedy action with noise that does not depend on uncertainty | noise scaled by a learned or counted uncertainty | epsilon-greedy, Boltzmann/softmax, OU noise, parameter-space noise, NoisyNets | |
| L.explore.opt | Optimism under uncertainty | L.explore | | adds a confidence bonus to value estimates and acts greedily on the inflated value | sampling from a posterior instead of inflating | UCB1, UCB-V, LinUCB, optimistic initialisation, RLSVI | |
| L.explore.post | Posterior sampling | L.explore | | samples a hypothesis from a posterior and acts greedily with respect to it | adding a deterministic bonus | Thompson sampling, bootstrapped DQN, posterior sampling for RL | |
| L.explore.intr | Intrinsic-motivation bonuses | L.explore | | adds a learned novelty or prediction-error term into the reward the agent optimises | a bonus used only for action selection and never entering the return | RND, ICM, pseudo-counts, Disagreement, NGU, empowerment | also alters the objective, so it carries two roles |
| L.explore.div | Diversity-driven and archive-based search | L.explore | | maintains an archive of behaviours and explicitly selects for behavioural novelty | selecting for return only | Go-Explore, novelty search, MAP-Elites, DIAYN, DADS | |
| L.replay | Experience storage and relabelling | | what decides which past transition is reused and with what target | stores past interaction and re-serves it to the learner, possibly with a changed target | generating fresh interaction | uniform replay, PER, HER | |
| L.replay.unif | Uniform experience replay | L.replay | | samples stored transitions uniformly at random | sampling with a priority or a changed goal | experience replay, replay ratio schedules | |
| L.replay.prio | Priority-weighted replay | L.replay | | samples stored transitions in proportion to a learning-progress score | uniform sampling | PER, ERE, LAP, topological replay | |
| L.replay.relabel | Goal and reward relabelling | L.replay | | rewrites the goal or reward of a stored transition so a failure becomes a success | reusing a transition with its original reward | HER, hindsight relabelling, GCSL relabelling | |
| L.selfplay | Opponent and task generation | | what determines the opponent or task distribution | generates the training distribution by playing against or generating versions of the system itself | a fixed opponent or fixed task set | self-play, PSRO, PLR | |
| L.selfplay.naive | Self-play against current or past selves | L.selfplay | | plays the learner against copies of itself drawn from its own training history | playing against a fixed scripted opponent | naive self-play, fictitious self-play, self-play with opponent pools | |
| L.selfplay.popul | Population and league training | L.selfplay | | maintains a population with explicit exploiter or niche roles and matchmaking | a single-copy self-play loop | PSRO, double oracle, AlphaStar league, NFSP | |
| L.selfplay.curr | Automatic environment curricula | L.selfplay | | generates or selects environments or goals to match the agent's current competence | a fixed environment distribution | POET, PLR, ADR, ALP-GMM, asymmetric self-play | |

### Reinforcement-learning objective families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.dp | Dynamic programming for MDPs | | | computes a value or policy by sweeping Bellman backups over a known transition model | learning from sampled transitions without a given model | policy iteration, value iteration, generalised policy iteration, asynchronous DP | founder of the whole value-based lineage |
| L.td | Temporal-difference learning | L.dp | | updates a value estimate toward a bootstrapped target built from the next state's own estimate | updating toward a full Monte-Carlo return only | TD(0), TD(lambda), true online TD, GTD | |
| L.td.q | Off-policy TD control | L.td | | bootstraps from the max (or an argmax-decoupled estimate) over next-state actions | bootstrapping from the action the behaviour policy actually took | Q-learning, Double Q-learning, Expected SARSA(off-policy form) | |
| L.td.sarsa | On-policy TD control | L.td | | bootstraps from the action the current policy actually selects | bootstrapping from a max over actions | SARSA, Expected SARSA, n-step SARSA | |
| L.dqn | Deep Q-networks | L.td.q | | fits Q-learning with a neural network plus a target network and a replay buffer | tabular Q-learning; actor-critic with an explicit policy head | DQN, Double DQN, Dueling DQN, NoisyNet-DQN, Rainbow, Ape-X, R2D2, Munchausen DQN | the canonical "ancestor worth aggregating to" |
| L.dqn.dist | Distributional value learning | L.dqn | | learns the full return distribution rather than only its expectation | learning a scalar expected return | C51, QR-DQN, IQN, FQF | |
| L.dqn.eff | Sample-efficient deep value learning | L.dqn | | raises updates-per-environment-step with explicit remedies for the resulting overfitting | scaling data rather than updates | DrQ, SPR, SR-SPR, BBF, REDQ | SPR is multi-parent with self-predictive SSL |
| L.pg | Policy-gradient methods | | | differentiates expected return with respect to policy parameters via the score-function identity | updating a value table or network with no explicit policy parameterisation | REINFORCE, actor-critic, A3C, A2C | |
| L.pg.ac | Actor-critic | L.pg | | reduces policy-gradient variance with a learned value baseline or critic | using an empirical return baseline only | actor-critic, A3C, A2C, GAE, IMPALA/V-trace, ACER | |
| L.pg.trust | Trust-region and clipped policy updates | L.pg.ac; L.precond.trust | | bounds the size of the policy change per update by a divergence or ratio constraint | an unconstrained gradient step on the policy | natural policy gradient, TRPO, PPO, PPO-clip, V-MPO | |
| L.pg.trust.grpo | Group-relative policy optimisation | L.pg.trust | | replaces the learned critic with a baseline computed across a sampled group of completions | using a learned value network as the baseline | GRPO, RLOO, DAPO, Dr.GRPO | the dominant recent RL-for-reasoning branch |
| L.dpg | Deterministic policy gradients | L.pg | | backpropagates the critic's gradient through a deterministic actor | sampling actions from a stochastic policy and using the score function | DPG, DDPG, TD3, D4PG | requires continuous actions |
| L.maxent | Maximum-entropy RL | L.pg | | optimises return plus a policy-entropy term as part of the objective, not as a bonus | entropy added only as an auxiliary regulariser with no soft-Bellman consistency | soft Q-learning, SAC, MPO, soft actor-critic variants, REDQ | |
| L.mbrl | Model-based RL | | what the learned dynamics model is used for | learns a transition or reward model and uses it to improve the policy or the value estimate | learning a value or policy directly from environment samples only | Dyna, PETS, Dreamer, MuZero | |
| L.mbrl.dyna | Model-generated experience | L.mbrl | | uses the learned model to synthesise extra transitions for a model-free learner | using the model only inside an action-selection search | Dyna, Dyna-Q, MBPO, SLBO | |
| L.mbrl.plan | Model-predictive control over a learned model | L.mbrl | | re-plans an action sequence at each step by rolling the model forward | amortising the plan into a policy network and never re-planning | PILCO, PETS, CEM-MPC, MPPI, iCEM | |
| L.mbrl.latent | Latent-dynamics world models | L.mbrl | | learns dynamics in a compressed latent space and trains the policy inside it | planning directly in observation space | World Models, PlaNet, Dreamer, DreamerV2, DreamerV3, TD-MPC | |
| L.mbrl.search | Learned-model tree search | L.mbrl; L.tts.plan | | combines a learned model with an explicit tree search that produces the acting policy | planning by trajectory sampling without a tree | AlphaGo, AlphaZero, MuZero, EfficientZero, Sampled MuZero | the clearest case of one lineage spanning two roles |
| L.orl | Offline reinforcement learning | | how the policy is kept inside the data's support | learns a policy from a fixed logged dataset with no further environment interaction | collecting new interaction at any point in training | BCQ, CQL, IQL, Decision Transformer | |
| L.orl.polcon | Explicit policy constraint | L.orl | | penalises or projects the learned policy toward the behaviour policy | penalising the value function instead | BCQ, BEAR, TD3+BC, BRAC | |
| L.orl.valpen | Pessimistic value penalty | L.orl | | lowers values of out-of-distribution actions so they are never selected | constraining the policy's action distribution directly | CQL, COMBO, pessimistic MDPs, EDAC | |
| L.orl.implicit | Implicit and weighted-regression policy extraction | L.orl | | extracts a policy by advantage-weighted regression without querying unseen actions | computing a max over actions outside the data | AWR, AWAC, IQL, XQL, SQL | |
| L.orl.seq | Return-conditioned sequence modelling | L.orl | | casts control as supervised next-token prediction conditioned on a desired return | fitting a value function and improving a policy against it | Decision Transformer, Trajectory Transformer, RvS, Multi-Game DT | signal is a label, not a reward, despite being RL |
| L.il | Imitation learning | | what replaces the reward signal | fits a policy from expert demonstrations with no environment reward | learning from an environment reward signal | behaviour cloning, DAgger, GAIL | |
| L.il.bc | Behaviour cloning | L.il | | fits actions to states by supervised regression or classification on demonstrations | inferring a reward function first | behaviour cloning, DAgger, DART, ACT, diffusion policy training | |
| L.il.irl | Inverse reinforcement learning | L.il | | infers a reward function that rationalises the demonstrations, then plans or learns on it | directly copying actions | MaxEnt IRL, guided cost learning, AIRL, Bayesian IRL | |
| L.il.adv | Adversarial imitation | L.il; L.gan | | trains a discriminator to separate agent from expert transitions and uses it as reward | matching actions pointwise | GAIL, DAC, AIRL, f-GAIL | |
| L.pref | Preference-based alignment | | whether a reward model is fit, and how the policy is updated against preferences | optimises a policy against pairwise or ranked human or AI preference judgements | optimising against a scalar reward supplied by the environment | RLHF, DPO, GRPO-with-reward-model | |
| L.pref.rm | Reward modelling plus policy optimisation | L.pref | | fits an explicit reward model on comparisons, then runs an RL algorithm against it | optimising the policy on preferences in closed form, with no reward model | RLHF with PPO, RLAIF, Constitutional AI, reward-model ensembles | |
| L.pref.direct | Direct preference optimisation | L.pref | | derives a closed-form policy loss from the preference pairs, skipping the reward model | fitting a separate reward network | DPO, IPO, KTO, ORPO, SimPO, cDPO, CPO | |
| L.pref.reject | Rejection-sampled finetuning | L.pref | | samples candidates, keeps the best by a scorer, then does supervised finetuning on them | updating with a policy-gradient step | best-of-n finetuning, RAFT, STaR, rejection-sampling SFT, ReST | sits between SFT and RL |
| L.pref.verif | Verifier-rewarded RL | L.pref | | the reward comes from a programmatic checker rather than a learned or human judgement | a reward model trained on human comparisons | RLVR, unit-test reward, math-answer-match reward | |
| L.marl | Multi-agent RL | | how the joint value or joint policy is factored | trains two or more interacting policies whose returns depend on each other | a single agent in a stationary environment | QMIX, MADDPG, MAPPO | |
| L.marl.indep | Independent learners | L.marl | | each agent runs a single-agent algorithm treating others as part of the environment | any explicit factorisation of a joint value or a centralised critic | IQL, IPPO, independent A2C | |
| L.marl.factor | Value factorisation | L.marl | | decomposes a joint action-value into per-agent terms under a monotonicity or additivity condition | learning the joint value without any decomposition | VDN, QMIX, QTRAN, QPLEX, Qatten | |
| L.marl.ctde | Centralised critic, decentralised actors | L.marl | | trains a critic with access to global state while each actor sees only its own observation | both training and execution use only local information | MADDPG, MAPPO, COMA, FACMAC | |
| L.marl.game | Equilibrium-computing methods | L.marl; L.selfplay.popul | | computes an approximate equilibrium rather than a best response to fixed others | optimising against a frozen opponent | fictitious play, CFR, Deep CFR, NFSP, Nash-Q, regret matching | |
| L.hrl | Hierarchical RL | | what the temporal abstraction is defined over | learns a policy over temporally extended sub-policies with their own termination | a flat policy over primitive actions | options framework, option-critic, FeUdal networks, HIRO, HAC | |
| L.bandit | Bandit algorithms | | how uncertainty about arm values is turned into a choice | selects among actions with immediate feedback and no state transition | a setting with state dynamics and delayed credit | UCB1, Thompson sampling, EXP3 | shares its characteristic with L.explore by design |
| L.bandit.stoch | Stochastic and contextual bandits | L.bandit; L.explore.opt | | assumes i.i.d. rewards per arm, possibly conditioned on a context vector | an adversarial reward sequence | UCB1, LinUCB, LinTS, Thompson sampling, KL-UCB | |
| L.bandit.adv | Adversarial bandits | L.bandit | | guarantees regret against an arbitrary, possibly adaptive reward sequence | an i.i.d. reward assumption | EXP3, EXP4, Tsallis-INF | |
| L.bandit.bai | Best-arm identification | L.bandit; L.hpo.bandit | | spends a fixed budget to identify the best arm, not to maximise cumulative reward | minimising cumulative regret while acting | successive halving, sequential halving, LUCB, racing | |
| L.bandit.ope | Off-policy evaluation and learning | L.bandit; L.causal.adjust | | estimates the value of a policy from logs collected under a different policy | evaluating a policy by running it | inverse propensity scoring, self-normalised IPS, doubly robust OPE, FQE | shares estimators with causal inference |

### Self-supervised and representation-learning families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.ssl.contrast | Instance-discrimination contrastive learning | | | pulls together views of the same instance and explicitly pushes apart other instances | a method with no negative examples in its loss | InstDisc, CPC, MoCo, MoCo v2, MoCo v3, SimCLR, SimCLR v2 | |
| L.ssl.contrast.x | Cross-modal contrastive alignment | L.ssl.contrast | | contrasts paired items from two different modalities against mismatched pairs | contrasting two augmented views of one item | CLIP, ALIGN, SigLIP, AudioCLIP, ImageBind | pairing is a supervision source, which blurs self vs supervised |
| L.ssl.contrast.sup | Label-aware contrastive learning | L.ssl.contrast; L.sft | | treats all same-class examples as positives using ground-truth labels | treating only augmented views of one instance as positives | SupCon, contrastive representation distillation | |
| L.ssl.selfdist | Negative-free self-distillation | | | regresses a student view onto a target produced by a momentum or stop-gradient copy | a loss containing explicit negative pairs | Mean Teacher, BYOL, SimSiam, DINO, DINOv2 | collapse avoidance is the defining engineering problem |
| L.ssl.redun | Redundancy-reduction objectives | | | decorrelates embedding dimensions via a cross-correlation or covariance criterion | contrasting whole embeddings against other samples | Barlow Twins, VICReg, VICRegL, W-MSE | |
| L.ssl.cluster | Clustering-based self-supervision | | | alternates assigning pseudo-cluster labels and predicting them from another view | a loss defined directly between embeddings with no assignment step | DeepCluster, SeLa, SwAV, PCL, ODC | |
| L.ssl.mask | Masked-input prediction | | what is masked and what the reconstruction target is | hides part of the input and trains the model to recover it from the remainder | predicting the next element with no masking of a visible context | BERT MLM, MAE, wav2vec 2.0 | |
| L.ssl.mask.lm | Masked language modelling | L.ssl.mask | | masks tokens and predicts their identity from bidirectional context | predicting only the next token left to right | CBOW, BERT MLM, RoBERTa, SpanBERT, T5 span corruption, ELECTRA | ELECTRA replaces the target with a detection task |
| L.ssl.mask.vis | Masked visual modelling | L.ssl.mask | | masks image or video patches and reconstructs pixels, tokens or features | reconstructing the whole unmasked image | Context Encoders, BEiT, MAE, SimMIM, iBOT, VideoMAE | |
| L.ssl.mask.aud | Masked and contrastive speech modelling | L.ssl.mask | | masks spans of audio and predicts quantised or clustered units | predicting transcribed text | wav2vec, wav2vec 2.0, HuBERT, WavLM, data2vec | |
| L.ssl.pretext | Handcrafted pretext tasks | | | invents a label from a known transformation of the input and predicts it | predicting part of the raw input content itself | relative patch position, jigsaw, rotation prediction, colourisation, shuffle-and-learn | largely historical; kept as an aggregation ancestor |
| L.ssl.jepa | Latent predictive self-supervision | L.ssl.selfdist | | predicts the representation of unobserved content rather than its raw content | regressing raw pixels or tokens | CPC, I-JEPA, V-JEPA, SPR, PBL | SPR applies this inside RL, hence multi-parent |
| L.emb | Shallow embedding induction | | what co-occurrence structure the embedding factorises | fits a lookup-table embedding directly from co-occurrence statistics, with no deep encoder | training a deep encoder end to end | word2vec, GloVe, fastText, DeepWalk, node2vec, item2vec | produces a model, but the procedure is the entry |

### Generative-modelling families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.ar | Autoregressive density modelling | | | factorises the joint density into a product of conditionals and fits each by maximum likelihood | fitting a bound on the likelihood or an implicit density | n-gram MLE, neural LM, PixelRNN, PixelCNN, causal LM pretraining, WaveNet training | the dominant pretraining objective; needs its own ancestor |
| L.ar.exposure | Exposure-bias corrections | L.ar | | changes which context the model conditions on during training to match inference | plain teacher forcing | scheduled sampling, professor forcing, SeqGAN-style corrections | |
| L.vae | Variational autoencoding | L.vi | | maximises an evidence lower bound with an amortised inference network | maximising exact likelihood; using a discriminator | wake-sleep, VAE, beta-VAE, IWAE, NVAE | |
| L.vae.vq | Discrete-latent autoencoding | L.vae | | quantises the latent to a learned codebook and trains through a straight-through estimator | a continuous Gaussian latent | VQ-VAE, VQ-VAE-2, VQGAN, FSQ, RQ-VAE | the tokeniser for most latent generative stacks |
| L.gan | Adversarial generative training | | which part of the minimax setup is altered | trains a generator against a discriminator whose loss it maximises | any objective with an explicit likelihood or reconstruction term | GAN, WGAN, StyleGAN, CycleGAN | |
| L.gan.loss | Adversarial divergence variants | L.gan | | changes the divergence or the discriminator's loss form | changes conditioning or architecture only | LSGAN, WGAN, WGAN-GP, SN-GAN, hinge GAN, f-GAN, relativistic GAN | |
| L.gan.cond | Conditional and translation GANs | L.gan | | conditions the generator on a label, image or text and pairs or cycles the mapping | unconditional sampling | cGAN, pix2pix, CycleGAN, StarGAN, SPADE | |
| L.gan.stab | Adversarial training stabilisers | L.gan | | adds a regulariser or update-timing rule aimed at the minimax dynamics | a change in the generator's data distribution | R1 regularisation, instance noise, TTUR, PPL regularisation, ADA | |
| L.flow | Normalizing flows | | how the invertible map is constructed | models density through an exactly invertible map with a tractable Jacobian determinant | a non-invertible decoder with a bound | NICE, RealNVP, Glow, MAF, IAF | |
| L.flow.cont | Continuous-time flows | L.flow | | defines the map as the solution of a learned ODE rather than a stack of coupling layers | discrete stacked bijectors | Neural ODE, FFJORD, rectified flow, flow matching, stochastic interpolants | flow matching is also the modern diffusion-training formulation |
| L.score | Score-based and diffusion modelling | | | learns the score or the noise of a progressively corrupted data distribution | learning an exact or bounded likelihood of the clean data directly | score matching, denoising score matching, NCSN, DDPM, improved DDPM, EDM, SDE diffusion | |
| L.score.guide | Guidance of the diffusion trajectory | L.score; L.dec.guide | | steers sampling with an external or implicit conditional signal during generation | conditioning only through the training objective | classifier guidance, classifier-free guidance, ControlNet conditioning, CFG rescaling | role is decoding although the lineage is generative |
| L.score.latent | Latent-space diffusion | L.score | | runs the diffusion process in a learned compressed space rather than pixel space | diffusing directly on raw observations | latent diffusion, Stable Diffusion training, DiT training | |
| L.score.sample | Diffusion samplers and distillation | L.score; L.dec | | reduces the number of denoising steps needed to produce a sample | the training procedure that fits the denoiser | DDIM, DPM-Solver, UniPC, progressive distillation, consistency models, LCM | lineage drifts from objective to decoder; see Tensions |
| L.ebm | Energy-based modelling | | | fits an unnormalised energy whose normaliser is never computed exactly | a model with a tractable normalising constant | Boltzmann machine, RBM, contrastive divergence, deep belief net, JEM, Langevin EBM | |

### Parameter-update families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.sgd | Stochastic first-order descent | | | steps the parameters along a stochastic gradient with a scalar step size | a per-coordinate or matrix-preconditioned step | Robbins-Monro, SGD, heavy-ball momentum, Nesterov acceleration, averaged SGD | |
| L.sgd.sign | Sign-based and normalised updates | L.sgd | | uses only the sign or the normalised direction of the gradient | a magnitude-proportional step | signSGD, Lion, normalised SGD, LARS layer-wise normalisation | |
| L.adapt | Per-coordinate adaptive step sizes | L.sgd | | scales each coordinate's step by an accumulated statistic of its own gradients | a single global step size for all coordinates | AdaGrad, RMSProp, Adadelta, Adam, AdamW, AMSGrad, NAdam, RAdam, AdaBelief, Adafactor, LAMB, Sophia | the single most frequent algorithm in the field |
| L.precond | Matrix-preconditioned optimisation | | how the curvature matrix is approximated | multiplies the gradient by an approximation of an inverse curvature matrix | scaling coordinates independently | L-BFGS, K-FAC, Shampoo, Muon | |
| L.precond.quasi | Quasi-Newton methods | L.precond | | builds the inverse-Hessian approximation from successive gradient differences | computing curvature from the model's Fisher or Gauss-Newton structure | Newton's method, BFGS, L-BFGS, DFP, SR1 | |
| L.precond.ng | Natural-gradient and Kronecker preconditioners | L.precond | | preconditions with the Fisher information or a Kronecker-factored surrogate of it | secant-condition updates | natural gradient, K-FAC, Shampoo, SOAP, Muon, PSGD | |
| L.precond.cg | Matrix-free curvature methods | L.precond | | solves the Newton system with Hessian-vector products instead of forming the matrix | forming or factoring a curvature matrix explicitly | conjugate gradient, Hessian-free optimisation, Gauss-Newton, Levenberg-Marquardt | |
| L.precond.trust | Trust-region control | L.precond | | restricts each step to a region where the local model is trusted | a fixed step size with no region constraint | trust-region Newton, TRPO's KL region, Cauchy-point methods | TRPO inherits from here and from policy gradients |
| L.vr | Variance-reduced stochastic gradients | | | corrects the stochastic gradient with a stored snapshot to shrink its variance | plain minibatch sampling | SAG, SVRG, SAGA, SARAH, SPIDER | strong theory, thin practical uptake in deep learning |
| L.prox | Proximal and splitting methods | | how the non-smooth part of the objective is handled | handles a non-smooth term with a proximal operator or by splitting the problem | taking a subgradient step on the non-smooth term | proximal gradient, ISTA, FISTA, ADMM, coordinate descent, Frank-Wolfe, mirror descent | the main vehicle for sparse classical estimators |
| L.sched | Step-size and update schedules | | what the schedule is a function of | changes the step size or other optimiser hyperparameter over the course of training | changing the direction of the update | cosine annealing, SGDR, one-cycle, warmup | |
| L.sched.time | Time-indexed schedules | L.sched | | the step size is a fixed function of the iteration or epoch index | a schedule reacting to observed loss | step decay, exponential decay, polynomial decay, cosine annealing, SGDR, linear warmup, WSD | |
| L.sched.state | Feedback-driven schedules | L.sched | | the step size changes in response to a measured training statistic | a schedule computable in advance | ReduceLROnPlateau, adaptive gradient clipping, loss-based restarts | |
| L.sched.scale | Scaling-rule hyperparameter transfer | L.sched; L.hpo.transfer | | sets step sizes by a width or compute scaling law transferred from a smaller model | tuning the step size on the target model directly | muP, muTransfer, linear batch-size scaling rule, square-root scaling | |
| L.gradproc | Gradient post-processing | | what the gradient is modified to satisfy | modifies the gradient between backward pass and update step | modifying the loss, or the update rule's state | gradient clipping, gradient accumulation, PCGrad, DP-SGD clipping | |
| L.gradproc.clip | Norm and value clipping | L.gradproc | | rescales or truncates the gradient when it exceeds a threshold | adding noise or projecting onto another gradient | global-norm clipping, value clipping, adaptive gradient clipping, per-sample clipping | |
| L.gradproc.conflict | Multi-objective gradient surgery | L.gradproc; L.mtl | | alters per-task gradients to remove mutual interference before summing | weighting task losses as scalars | PCGrad, CAGrad, GradDrop, GradNorm | |
| L.gradproc.priv | Privacy-noised gradients | L.gradproc; L.priv | | clips per-example gradients and adds calibrated noise to meet a privacy budget | clipping without a noise mechanism or accountant | DP-SGD, DP-Adam, DP-FTRL | |
| L.wavg | Weight averaging and merging | | over what the parameters are averaged | produces a parameter vector by combining several parameter vectors | combining predictions rather than parameters | Polyak averaging, EMA, SWA | |
| L.wavg.traj | Averaging along one trajectory | L.wavg | | averages iterates produced by a single training run | averaging independently trained models | Polyak-Ruppert averaging, EMA of weights, SWA, LAWA, checkpoint averaging | |
| L.wavg.merge | Merging independently trained models | L.wavg | | combines parameters of separately finetuned models into one | averaging checkpoints from one run | model soups, task arithmetic, TIES-merging, DARE, SLERP merge, Fisher merging | role is parameter rewriting, not fitting |
| L.init | Parameter initialisation schemes | | what statistic the initialisation is designed to preserve | sets the initial parameter distribution by an explicit named rule | a learned or pretrained initialisation | LeCun init, Xavier/Glorot, He init, orthogonal init, LSUV, Fixup, muP init | boundary with architecture; see Tensions |
| L.em | Expectation-maximisation | | | alternates computing responsibilities under the current parameters and maximising the expected complete-data likelihood | optimising the marginal likelihood by direct gradient ascent | EM, generalised EM, variational EM, Baum-Welch, hard EM | the classical-statistics counterpart of an optimiser |
| L.derivfree | Derivative-free optimisation | | how new candidate points are proposed | searches parameter or configuration space using only function evaluations | using analytic or automatic gradients | CMA-ES, genetic algorithms, Nelder-Mead, simulated annealing | |
| L.derivfree.es | Evolution strategies | L.derivfree | | samples a population from a distribution and updates that distribution's parameters | recombining discrete genotypes | NES, CMA-ES, sep-CMA-ES, OpenAI-ES, Augmented Random Search | |
| L.derivfree.ga | Genetic and evolutionary programming | L.derivfree | | uses crossover and mutation over structured individuals with selection | updating a parametric search distribution | genetic algorithms, NEAT, regularised evolution, genetic programming | |
| L.derivfree.local | Direct local search | L.derivfree | | moves a simplex or pattern of points by comparison of function values | maintaining a population or a probabilistic model | Nelder-Mead, pattern search, Powell's method, coordinate search | |
| L.derivfree.anneal | Annealed stochastic search | L.derivfree; L.mcmc.temper | | accepts worsening moves with a temperature-controlled probability | greedy acceptance only | simulated annealing, parallel tempering, basin hopping | |
| L.ls | Closed-form and spectral estimators | | which matrix problem the estimate reduces to | obtains parameters by solving an equation or decomposition, not by iterating a step rule | any iterative descent procedure | normal equations, QR least squares, ridge closed form, truncated SVD, method of moments | the home for "no optimiser was used" |

### Objective shaping, regularisation and training recipes

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.reg | Explicit regularisation | | what the penalty or perturbation is applied to | adds a term or perturbation whose purpose is to constrain the solution, not to fit the data | a term that encodes the task target | weight decay, dropout, label smoothing, SAM | |
| L.reg.weight | Parameter-norm penalties | L.reg | | penalises a norm or spectral property of the parameters | perturbing activations or inputs | L2/weight decay, decoupled weight decay, L1, max-norm, spectral norm, orthogonality penalties | |
| L.reg.act | Stochastic activation regularisation | L.reg | | randomly removes or perturbs units or paths during training only | a deterministic penalty term | dropout, DropConnect, stochastic depth, DropBlock, DropPath, LayerDrop | partly a layer, partly a procedure |
| L.reg.target | Target smoothing | L.reg | | softens or perturbs the training target rather than the model | perturbing the input | label smoothing, confidence penalty, mixup labels, temperature-softened targets | |
| L.reg.consist | Consistency regularisation | L.reg; L.semi | | penalises disagreement between the model's outputs on two perturbed versions of one input | penalising disagreement with an external label | Pi-model, temporal ensembling, Mean Teacher, VAT, UDA, R-Drop | |
| L.reg.geom | Loss-geometry regularisation | L.reg | | explicitly seeks flat minima or bounds a derivative of the loss surface | penalising parameter magnitude | SAM, ASAM, GSAM, gradient penalty, Jacobian/Hessian penalties | |
| L.stop | Stopping and checkpoint selection | | what signal triggers the stop | decides when training ends or which checkpoint is kept | deciding how large a step to take | early stopping, patience rules, best-checkpoint selection, validation-plateau stopping | |
| L.semi | Semi-supervised learning | | how an unlabelled example is given a target | uses labelled and unlabelled data in one fitting procedure | pretraining on unlabelled data then finetuning separately | FixMatch, Noisy Student, label propagation | |
| L.semi.self | Self-training and pseudo-labelling | L.semi | | labels unlabelled data with the current model and retrains on confident predictions | deriving the target from a transformation rather than a prediction | self-training, pseudo-labelling, Noisy Student, FixMatch, FlexMatch, SoftMatch | FixMatch is multi-parent with consistency |
| L.semi.mix | Interpolation-based semi-supervision | L.semi; L.aug.mix | | mixes labelled and unlabelled examples and their guessed labels | training on each example separately | MixMatch, ReMixMatch, ICT | |
| L.semi.graph | Graph-based label propagation | L.semi; L.graphalg | | spreads labels across a similarity graph built over labelled and unlabelled points | assigning labels by a parametric model's prediction | label propagation, label spreading, harmonic functions | |
| L.semi.weak | Weak supervision and label aggregation | L.semi | | combines noisy labelling rules or annotators into probabilistic labels | using a single trusted label source | Snorkel/data programming, Dawid-Skene, MACE, majority-vote aggregation | |
| L.semi.cotrain | Multi-view co-training | L.semi | | two or more learners on different views label data for one another | a single learner labelling its own data | co-training, tri-training, democratic co-learning | |
| L.da | Domain adaptation and invariance | | what quantity is aligned across domains | trains with data from a source domain to perform on a shifted target domain | adapting after deployment with no training-time target data | DANN, CORAL, IRM | |
| L.da.adv | Adversarial domain alignment | L.da; L.gan | | trains a domain discriminator the feature extractor is trained to fool | matching moments or kernels in closed form | DANN, ADDA, CDAN, MDD | |
| L.da.stat | Statistic-matching alignment | L.da | | minimises an explicit discrepancy between source and target feature statistics | using a learned discriminator | CORAL, Deep CORAL, MMD/DAN, JAN, optimal-transport alignment | |
| L.da.inv | Invariant risk and environment-based objectives | L.da | | requires the optimal predictor to be simultaneously optimal across labelled environments | aligning marginal feature distributions | IRM, REx, GroupDRO, Fish, CLOvE | |
| L.robust | Distributional and adversarial robustness | | what adversary the objective is minimised against | minimises a worst-case rather than an average risk | minimising the empirical mean loss | DRO, PGD adversarial training, randomised smoothing | |
| L.robust.dro | Distributionally robust optimisation | L.robust | | minimises the worst-case loss over a set of reweightings of the training distribution | minimising worst case over input perturbations | DRO, CVaR-DRO, GroupDRO, chi-square DRO | |
| L.robust.adv | Adversarial training | L.robust; L.aug.adv | | solves an inner maximisation over input perturbations inside each training step | perturbing inputs without maximising the loss | PGD adversarial training, TRADES, MART, FastAT, free adversarial training | |
| L.robust.cert | Certified robustness | L.robust | | returns a provable guarantee of invariance within a stated input region | providing only empirical attack resistance | randomised smoothing, IBP, CROWN, convex relaxations | |
| L.mtl | Multi-task and auxiliary objectives | | how multiple losses are combined | fits one parameter set against two or more distinct task losses | finetuning sequentially, one task at a time | uniform weighting, uncertainty weighting, GradNorm, UNREAL auxiliary tasks | |
| L.meta | Meta-learning | | what quantity is meta-learned | optimises across a distribution of tasks so that per-task adaptation is cheap | training on one task distribution with no inner adaptation loop | MAML, prototypical networks, RL-squared | |
| L.meta.init | Optimisation-based meta-learning | L.meta | | meta-learns an initialisation whose few-step adaptation performs well | meta-learning a metric or a black-box update | MAML, FOMAML, Reptile, ANIL, Meta-SGD, iMAML | |
| L.meta.metric | Metric-based few-shot learning | L.meta | | classifies by distance to class representatives in a learned embedding | updating parameters per task | Siamese networks, Matching Networks, Prototypical Networks, Relation Networks | |
| L.meta.black | Black-box and in-context adaptation | L.meta | | adaptation happens in activations or recurrent state, with no parameter update | adapting by gradient steps at task time | RL-squared, SNAIL, in-context learning as meta-learning | partly speculative as a *training* procedure |
| L.meta.opt | Learned optimisers | L.meta | | meta-trains a parametric update rule applied to another model's parameters | using a hand-designed update rule | learning to learn by gradient descent, VeLO, L2O | the learned optimiser is a model; the meta-training is the algorithm |
| L.cont | Continual learning | | how interference with earlier tasks is resisted | trains on a sequence of tasks without full access to earlier data | training on all tasks jointly | EWC, A-GEM, iCaRL | |
| L.cont.reg | Importance-weighted parameter anchoring | L.cont | | penalises movement of parameters deemed important to earlier tasks | storing and replaying earlier examples | EWC, SI, MAS, Riemannian walk | |
| L.cont.replay | Rehearsal | L.cont; L.replay | | stores or regenerates earlier examples and mixes them into current training | constraining parameters without any stored data | experience replay, GEM, A-GEM, DER, iCaRL, generative replay | |
| L.cont.arch | Capacity isolation | L.cont | | allocates disjoint parameters or masks per task | sharing all parameters across tasks | progressive networks, PackNet, HAT, supermasks | |
| L.cont.proj | Gradient projection | L.cont; L.gradproc | | projects updates onto directions that do not disturb earlier-task outputs | penalising parameter movement isotropically | orthogonal gradient descent, GPM, Adam-NSCL | |

### Adaptation-scope families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.peft | Parameter-efficient adaptation | | where the new degrees of freedom live | adapts a pretrained model while updating only a small fraction of, or an addition to, its parameters | updating every parameter of the pretrained model | LoRA, adapters, prefix tuning, BitFit | |
| L.peft.adapter | Inserted adapter modules | L.peft | | inserts new trainable submodules into the frozen network and trains only those | reparameterising existing weight matrices | Houlsby adapters, Pfeiffer adapters, AdapterFusion, Compacter, Parallel adapters | |
| L.peft.lowrank | Low-rank weight reparameterisation | L.peft | | adds a trainable low-rank update to existing weight matrices, mergeable at inference | adding modules that change the computation graph at inference | LoRA, QLoRA, AdaLoRA, DoRA, LoRA+, ReLoRA, VeRA | |
| L.peft.prompt | Prompt and prefix tuning | L.peft | | trains continuous vectors prepended to the input or to the attention keys and values | training weights inside the network | prefix tuning, prompt tuning, P-tuning v2, soft prompts | |
| L.peft.select | Sparse parameter selection | L.peft | | trains a chosen sparse subset of the existing parameters | adding new parameters of any kind | BitFit, IA3, diff pruning, Fish-Mask, surgical finetuning | |
| L.peft.freeze | Freezing and staged unfreezing | L.peft | | holds some existing layers fixed and trains the rest, with no new parameters beyond a head | training all layers from the first step | linear probing, feature extraction, gradual unfreezing, ULMFiT schedule, LP-FT | |
| L.sft | Supervised adaptation recipes | | what the demonstration data is and how it is composed | finetunes a pretrained model on labelled demonstrations of the target behaviour | fitting from random initialisation | BERT finetuning, FLAN, Alpaca-style SFT | |
| L.sft.inst | Instruction tuning | L.sft | | finetunes on instruction-response pairs across many tasks to induce instruction following | finetuning on a single downstream task | FLAN, T0, Natural Instructions, Alpaca, Tulu-style SFT | |
| L.sft.task | Single-task finetuning | L.sft | | adapts a pretrained model to one labelled downstream task | multi-task instruction mixtures | BERT finetuning, ULMFiT, task-specific heads | |

### Coordination families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.dpar | Data-parallel training | | how and when workers exchange their updates | replicates the model across workers that process different data and combine gradients | splitting the model itself across devices | synchronous all-reduce SGD, Hogwild!, local SGD | |
| L.dpar.sync | Synchronous gradient aggregation | L.dpar | | every worker's gradient is combined before any worker steps | workers step on stale or partial information | synchronous SGD, ring all-reduce, large-batch recipes with LARS/LAMB | |
| L.dpar.async | Asynchronous and stale updates | L.dpar | | workers apply updates without waiting, tolerating staleness | a global barrier per step | Hogwild!, Downpour SGD, ASGD, stale-synchronous parallel | |
| L.dpar.local | Infrequent communication | L.dpar | | workers take several local steps before any averaging | averaging after every single step | local SGD, post-local SGD, EASGD, DiLoCo, FedAvg-style local steps | shares its idea with federated averaging |
| L.dpar.comp | Communicated-update compression | L.dpar | | quantises, sparsifies or low-rank-projects the tensor that is communicated | changing the communication schedule only | 1-bit SGD, QSGD, Deep Gradient Compression, PowerSGD, top-k sparsification | |
| L.dpar.decen | Decentralised and gossip training | L.dpar | | workers exchange only with neighbours, with no global aggregation step | a central server or a global all-reduce | D-PSGD, SGP, gossip averaging, AD-PSGD | |
| L.shard | Model-state sharding and pipelining | | which dimension of the computation is split across devices | splits one model's parameters, activations or layers across devices | replicating the full model on every device | ZeRO, FSDP, Megatron tensor parallel, GPipe | |
| L.shard.opt | Optimiser-state and parameter sharding | L.shard | | partitions optimiser state, gradients or parameters across data-parallel ranks | partitioning the computation of a single layer | ZeRO-1, ZeRO-2, ZeRO-3, FSDP, ZeRO-Offload, ZeRO-Infinity | |
| L.shard.tensor | Intra-layer tensor parallelism | L.shard | | splits a single matrix multiplication across devices | assigning whole layers to devices | Megatron-LM tensor parallelism, sequence parallelism, 2D/2.5D parallel | |
| L.shard.pipe | Pipeline parallelism | L.shard | | assigns consecutive layer blocks to devices and streams microbatches through them | splitting within a layer | GPipe, PipeDream, 1F1B, interleaved pipeline, zero-bubble pipeline | |
| L.shard.expert | Sparse-expert routing | L.shard | | routes each token or example to a subset of experts and balances the load | dense computation on all parameters | top-k gating, Switch routing, expert-choice routing, BASE layers, load-balancing losses | boundary with architecture; routing itself is a procedure |
| L.shard.ctx | Context and sequence sharding | L.shard | | splits one long sequence's attention computation across devices | splitting the batch | ring attention, context parallelism, Blockwise parallel transformers | |
| L.memtrade | Memory-compute trade-offs | | what is recomputed or moved rather than stored | reduces memory by recomputing or relocating intermediate state | reducing memory by changing the model | gradient checkpointing, selective recompute, CPU offload, mixed-precision training, loss scaling | boundary: closer to systems than to learning |
| L.fed | Federated learning | | what is changed relative to the local-steps-then-average loop | trains across clients that never transmit their raw data | centralised training on pooled data | FedAvg, FedProx, SCAFFOLD | |
| L.fed.avg | Federated averaging and its corrections | L.fed; L.dpar.local | | averages client models after local epochs, with corrections for client drift | personalising a separate model per client | FedAvg, FedProx, SCAFFOLD, FedNova, FedOpt, FedAdam | |
| L.fed.pers | Personalised federated learning | L.fed | | each client keeps a model that differs from the global one by design | producing a single shared global model | Per-FedAvg, pFedMe, FedRep, Ditto, FedBN | |
| L.fed.sys | Federated system procedures | L.fed | | changes which clients participate, when, or how updates are buffered | changes the aggregation rule's mathematics | client selection, FedBuff, asynchronous FL, split learning, hierarchical FL | |
| L.priv | Privacy-preserving training | | what the privacy mechanism protects against | provides a stated privacy property for the training data | a method whose privacy claim is only informal | DP-SGD, PATE, secure aggregation | |
| L.priv.dp | Differentially private learning | L.priv; L.gradproc.priv | | bounds any single example's influence and accounts for a cumulative epsilon | protecting data in transit without an epsilon bound | DP-SGD, DP-Adam, DP-FTRL, PATE, DP-FedAvg | |
| L.priv.crypto | Cryptographic aggregation | L.priv | | hides individual updates from the aggregator using a cryptographic protocol | adding statistical noise to the update | secure aggregation, homomorphic-encryption aggregation, secure multiparty computation | |
| L.priv.unlearn | Machine unlearning | L.priv | | removes a specific training example's influence from an already-trained model | preventing influence from being recorded in the first place | SISA, influence-function unlearning, certified removal, exact retraining shards | |

### Configuration-search families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.hpo | Hyperparameter optimisation | | how the next configuration is chosen | runs multiple training trials to select hyperparameters by a validation signal | picking hyperparameters by hand or by citation | grid search, TPE, Hyperband, PBT | |
| L.hpo.enum | Enumerative and random search | L.hpo | | draws configurations from a fixed design with no adaptation to past trials | choosing the next point from previous results | grid search, random search, Sobol/quasi-random, Latin hypercube | random search is the baseline everyone must beat |
| L.hpo.model | Surrogate-model search | L.hpo; L.gp | | fits a probabilistic surrogate to past trials and maximises an acquisition function | allocating budget without modelling the response surface | GP-EI Bayesian optimisation, TPE, SMAC, BOHB, BORE | |
| L.hpo.bandit | Budget-allocation search | L.hpo; L.bandit.bai | | reallocates compute across running trials by early-stopping the weak ones | running every trial to completion | successive halving, Hyperband, ASHA, BOHB, PBT | |
| L.hpo.grad | Gradient-based hyperparameter optimisation | L.hpo | | differentiates a validation loss with respect to hyperparameters | treating the trial as a black box | hypergradient descent, implicit differentiation, DARTS-style relaxation | |
| L.hpo.transfer | Transferred and predicted configurations | L.hpo | | sets hyperparameters from a scaling rule or a meta-model, without search on the target | searching directly at the target scale | muTransfer, meta-learned priors, scaling-law extrapolation, zero-shot HPO | |
| L.nas | Neural architecture search | | how the architecture space is traversed | searches over architectures using a measured or predicted performance signal | designing the architecture by hand | NASNet, DARTS, Once-for-All | the product is a model; the search is the algorithm |
| L.nas.rl | Controller-based search | L.nas; L.pg | | trains a controller policy that emits architectures, rewarded by their accuracy | mutating a population or relaxing the space | NASNet/Zoph-Le, ENAS, MetaQNN | |
| L.nas.evo | Evolutionary architecture search | L.nas; L.derivfree.ga | | mutates and selects architectures in a population | following a gradient through architecture weights | AmoebaNet/regularised evolution, NEAT, hierarchical evolution | |
| L.nas.grad | Differentiable architecture search | L.nas; L.hpo.grad | | relaxes discrete choices into continuous weights and follows their gradient | evaluating discrete candidates separately | DARTS, PC-DARTS, GDAS, ProxylessNAS, SNAS | |
| L.nas.oneshot | Supernet and weight-sharing search | L.nas | | trains one over-parameterised network whose subnetworks are the candidates | training each candidate from scratch | one-shot NAS, Once-for-All, BigNAS, SPOS | |
| L.nas.zero | Training-free architecture scoring | L.nas | | ranks architectures by a proxy computable without training | ranking by measured post-training accuracy | zero-cost proxies, NASWOT, synflow score | |
| L.automl | Pipeline and algorithm selection | | what part of the pipeline is searched | searches jointly over preprocessing, model family and hyperparameters | searching hyperparameters of a fixed model family | Auto-WEKA, auto-sklearn, TPOT, AutoGluon, H2O AutoML | |

### Parameter-rewriting families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.prune | Pruning | | what score decides which parameters are removed | sets a subset of parameters to zero and removes them from the computation | lowering the numeric precision of all parameters | magnitude pruning, lottery ticket, SparseGPT | |
| L.prune.sal | Curvature-based saliency pruning | L.prune | | scores parameters by an estimated loss increase from removing them | scoring by magnitude alone | OBD, OBS, WoodFisher, SNIP, GraSP | |
| L.prune.mag | Magnitude and movement pruning | L.prune | | removes the smallest weights, or those moving toward zero during finetuning | estimating a second-order saliency | magnitude pruning, iterative magnitude pruning, lottery ticket, movement pruning, RigL | |
| L.prune.struct | Structured pruning | L.prune | | removes whole channels, heads, layers or structured blocks | removing individual scattered weights | channel pruning, head pruning, LLM-Pruner, 2:4 structured sparsity, ShortGPT | |
| L.prune.oneshot | One-shot post-training pruning | L.prune | | prunes a trained model using a small calibration set and a local reconstruction | pruning during training with retraining between steps | SparseGPT, Wanda, Optimal BERT Surgeon | |
| L.quant | Quantization | | whether and how the network is retrained to the quantized grid | reduces the numeric precision of weights or activations | removing parameters entirely | GPTQ, LSQ, BinaryConnect | |
| L.quant.ptq | Post-training quantization | L.quant | | quantises a finished model using only a small calibration set, with no gradient training | training the model with quantization in the loop | min-max calibration, GPTQ, AWQ, SmoothQuant, LLM.int8, QuIP, SpQR | |
| L.quant.qat | Quantization-aware training | L.quant | | simulates quantization in the forward pass and trains through a straight-through estimator | calibrating without any training | QAT, LSQ, PACT, DoReFa | |
| L.quant.bin | Binarisation and ternarisation | L.quant | | reduces weights or activations to one or two bits | reducing to 4 or 8 bits | BinaryConnect, XNOR-Net, BNN, TWN | |
| L.quant.kv | Inference-cache quantization | L.quant | | quantises the attention cache rather than the parameters | quantising weights | KV-cache quantization, KIVI, per-channel cache scaling | |
| L.kd | Knowledge distillation | | what of the teacher is matched | trains a student against targets produced by a teacher model | training against ground-truth labels only | Hinton KD, FitNets, DistilBERT | role is objective; compression is a goal, not a slot |
| L.kd.logit | Output-distribution distillation | L.kd | | matches the teacher's softened output distribution | matching internal representations | Hinton KD, born-again networks, DistilBERT, decoupled KD, sequence-level KD | |
| L.kd.feat | Representation distillation | L.kd | | matches internal activations, attention maps or relations | matching outputs only | FitNets, attention transfer, CRD, relational KD, TinyBERT | |
| L.kd.self | Self-distillation | L.kd | | teacher and student are the same architecture, or the model's own earlier state | a strictly larger separate teacher | born-again networks, self-distillation, BAN, deep mutual learning | |
| L.lowrankc | Weight factorisation | | which decomposition is applied | replaces a weight tensor with a product of smaller factors | zeroing or requantising the original tensor | SVD compression, Tucker decomposition, CP decomposition, ASVD | speculative: often reported without a name |

### Output-generation and test-time families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.dec | Sequence decoding | | how the next output is chosen from the model's scores | converts the model's scores into an emitted sequence at inference time | changing what the model scores | beam search, nucleus sampling, speculative decoding | decides what is selected, so it decides what the model says |
| L.dec.greedy | Greedy decoding | L.dec | | emits the argmax at every step with no lookahead and no sampling | keeping multiple hypotheses or sampling | greedy decoding, argmax decoding | |
| L.dec.beam | Beam search | L.dec | | maintains a fixed number of partial hypotheses ranked by cumulative score | keeping only one hypothesis, or sampling | beam search, length-normalised beam, diverse beam search, constrained beam search | |
| L.dec.sample | Truncated stochastic sampling | L.dec | | samples from the output distribution after reshaping or truncating its tail | deterministic selection | ancestral sampling, temperature, top-k, nucleus/top-p, typical sampling, min-p, eta sampling, Mirostat | |
| L.dec.contrast | Contrastive decoding | L.dec | | scores a token by the difference between two models' or two layers' log-probabilities | scoring with a single distribution | contrastive decoding, DoLa, context-aware decoding, contrastive search | |
| L.dec.constr | Constrained decoding | L.dec | | masks tokens that would violate a grammar, schema or lexical constraint | rejecting invalid outputs after generation | grammar-constrained decoding, FSM-constrained decoding, lexically constrained decoding, JSON-schema decoding | |
| L.dec.rerank | Candidate reranking and MBR | L.dec | | generates a candidate set and selects among complete candidates by a utility | selecting token by token | MBR decoding, reranking by model score, n-best reranking, quality-estimation reranking | |
| L.dec.spec | Speculative decoding | L.dec | | a cheap proposer drafts tokens that the target model verifies in parallel | a single model emitting one token per forward pass | speculative decoding, Medusa, EAGLE, lookahead decoding, self-speculative decoding | changes cost, not the output distribution |
| L.dec.guide | Guided generation | L.dec | | perturbs the output distribution with an auxiliary scorer or an unconditional contrast | selecting from the unmodified distribution | classifier guidance, classifier-free guidance, PPLM, FUDGE, GeDi | shared with the diffusion lineage |
| L.tts | Test-time search and deliberation | | what structure the search explores | spends extra inference compute exploring multiple reasoning or action paths | a single forward pass per output | self-consistency, tree of thoughts, MCTS | |
| L.tts.sample | Sample-and-select | L.tts | | samples several complete attempts and selects or aggregates among them | expanding a partial solution | best-of-n, self-consistency majority vote, weighted best-of-n, rejection sampling at inference | |
| L.tts.tree | Structured reasoning search | L.tts | | expands and scores partial reasoning states in a tree or graph | generating one linear chain | chain-of-thought prompting, least-to-most, tree of thoughts, graph of thoughts, PRM-guided beam, MCTS-guided decoding | CoT is a named procedure, so it is admissible |
| L.tts.loop | Iterative refinement loops | L.tts | | re-invokes the model on its own previous output plus feedback, in a loop | a single generation with no revision | ReAct, Reflexion, self-refine, self-debug, multi-agent debate | |
| L.tts.plan | Explicit planning over a model | L.tts | | searches over an environment or dynamics model to choose an action | choosing an action by a direct policy forward pass | A-star, Dijkstra, MCTS, UCT, PUCT, CEM-MPC, MPPI, iLQR, DDP | shared with model-based RL |
| L.retr | Retrieval and context construction | | how candidate context is scored | selects external items to place in the model's input at inference | selecting training examples before fitting | BM25, DPR, RAG | |
| L.retr.lex | Lexical retrieval | L.retr | | scores documents by weighted term overlap with the query | scoring by learned dense vectors | TF-IDF, BM25, BM25+, SPLADE (hybrid) | |
| L.retr.dense | Learned dense retrieval | L.retr; L.ssl.contrast | | scores by inner product of learned query and document embeddings | scoring by term statistics | DSSM, DPR, ANCE, ColBERT, E5, GTE | trained contrastively, used at inference |
| L.retr.index | Approximate nearest-neighbour search | L.retr; L.inst | | finds approximate nearest neighbours under an index structure with a recall-speed trade-off | exhaustive exact search | LSH, IVF-PQ, HNSW, DiskANN, ScaNN | |
| L.retr.aug | Retrieval-augmented generation | L.retr | | conditions generation on retrieved passages, possibly trained jointly | retrieving without feeding the result to a generator | kNN-LM, REALM, RAG, FiD, RETRO, Self-RAG | |
| L.retr.rerank | Retrieval reranking and fusion | L.retr | | re-scores or merges candidate lists from a first-stage retriever | producing the first-stage candidates | cross-encoder reranking, monoT5, reciprocal rank fusion, ColBERT late interaction | |
| L.calib | Calibration and uncertainty quantification | | what produces the uncertainty estimate | converts model outputs into calibrated probabilities, intervals or abstentions | changing which output is emitted | temperature scaling, conformal prediction, deep ensembles | |
| L.calib.post | Post-hoc probability recalibration | L.calib | | fits a small mapping from scores to probabilities on a held-out split | producing uncertainty from multiple models or a posterior | Platt scaling, isotonic regression, temperature scaling, vector and matrix scaling, beta calibration | |
| L.calib.conf | Conformal prediction | L.calib | | produces sets or intervals with a finite-sample coverage guarantee under exchangeability | producing a point probability with no coverage guarantee | split conformal, full conformal, CQR, conformal risk control, adaptive conformal | |
| L.calib.ens | Ensemble-based uncertainty | L.calib; L.ens | | estimates uncertainty from disagreement across independently trained or sampled models | estimating from one model's output distribution | deep ensembles, snapshot ensembles, batch ensembles, hyper-ensembles | |
| L.calib.bayes | Approximate Bayesian neural inference | L.calib; L.vi | | approximates a posterior over parameters and marginalises predictions over it | fitting a single point estimate | Laplace approximation, Bayes-by-backprop, MC dropout, SWAG, SGLD posteriors | |
| L.calib.ood | Out-of-distribution and selective prediction | L.calib | | scores whether an input is outside the training distribution and may abstain | calibrating probabilities on in-distribution data | max-softmax baseline, ODIN, Mahalanobis score, energy-based OOD, selective prediction | |
| L.tta | Test-time adaptation | | what is updated at test time | updates the model or its statistics using unlabelled test data during deployment | adapting with labelled target data before deployment | TENT, TTT, SHOT | adapting at test time is a property of the method, not its use |
| L.tta.norm | Normalisation-statistic adaptation | L.tta | | recomputes normalisation statistics on test batches, updating no weights | updating weights by an optimisation step | BN-statistic adaptation, DUA, prediction-time BN | |
| L.tta.ent | Entropy-minimisation adaptation | L.tta | | takes gradient steps on the entropy or a confidence surrogate of test predictions | taking steps on a self-supervised auxiliary loss | TENT, EATA, SAR, CoTTA, RoTTA | |
| L.tta.ssl | Self-supervised test-time training | L.tta; L.ssl.mask | | takes gradient steps on an auxiliary self-supervised loss computed on the test input | using the task head's own entropy | TTT, TTT-MAE, MEMO, TTT-layers | |
| L.tta.proto | Prototype and classifier-only adaptation | L.tta | | re-estimates class prototypes or the classifier head from test features | updating the feature extractor | SHOT, T3A, prototype refinement | |
| L.ens | Inference-time aggregation | | over what the predictions are combined | combines several models' or several runs' predictions into one output | combining their parameters instead | voting, averaging, stacking, Bayesian model averaging, mixture-of-experts routing at inference | |
| L.interp | Attribution and interpretation | | what the explanation is computed from | produces an explanation of a trained model's behaviour as an output | changing the model's predictions | Grad-CAM, SHAP, activation patching | an explanation is an output, so the participant rule admits this |
| L.interp.grad | Gradient-based attribution | L.interp | | attributes using gradients or gradient paths through the network | attributing by perturbing inputs and refitting a surrogate | saliency maps, Grad-CAM, integrated gradients, SmoothGrad, GradientSHAP | |
| L.interp.pert | Perturbation-based attribution | L.interp | | attributes by measuring output change under input occlusion or resampling | reading internal gradients | LIME, SHAP, occlusion, permutation importance, ablation studies | |
| L.interp.probe | Probing and representation analysis | L.interp; L.peft.freeze | | fits or compares a simple readout on frozen internal representations | explaining a single prediction | linear probing, CKA, SVCCA, causal tracing, activation patching | |
| L.interp.dict | Feature dictionary learning | L.interp; L.dimred.parts | | fits an overcomplete sparse basis over activations to name internal features | attributing to input dimensions | sparse autoencoders, dictionary learning on activations, transcoders | |
| L.fair | Fairness-constrained procedures | | at which stage the fairness constraint is applied | enforces a stated group or individual fairness criterion as part of the procedure | measuring disparity without acting on it | reweighing, adversarial debiasing, equalized-odds post-processing | |
| L.fair.pre | Pre-processing fairness interventions | L.fair | | modifies the data before fitting so that a disparity criterion is reduced | modifying the loss or the predictions | reweighing, disparate impact remover, fair representation learning, LFR | |
| L.fair.in | In-processing fairness constraints | L.fair | | adds a fairness constraint or penalty to the training objective | adjusting the trained model's thresholds | constrained ERM, reductions approach, adversarial debiasing, fair regularisers | |
| L.fair.post | Post-processing fairness adjustment | L.fair; L.calib.post | | adjusts thresholds or outputs per group on a trained model | retraining with a modified objective | equalized-odds post-processing, reject-option classification, group-wise thresholds | |

### Classical machine learning and statistics families

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| L.lin | Linear and generalized linear estimation | | what penalty or link is added to least squares | fits a linear predictor, possibly through a link function, to observed responses | fitting a nonlinear function class | OLS, ridge, lasso, logistic regression, GLM | |
| L.lin.ols | Least-squares estimation | L.lin | | minimises squared residuals with no penalty term | adding a shrinkage penalty | OLS, weighted least squares, generalised least squares, total least squares | |
| L.lin.pen | Penalised regression | L.lin | | adds a norm penalty on coefficients to the least-squares objective | changing the loss on the residuals | ridge, lasso, elastic net, group lasso, LARS, adaptive lasso, SCAD | lasso doubles as feature selection |
| L.lin.glm | Generalized linear models | L.lin | | maps a linear predictor through a link to a non-Gaussian response distribution | using an identity link with Gaussian noise | logistic regression, Poisson regression, negative binomial, ordinal and multinomial logit | |
| L.lin.robust | Robust and quantile regression | L.lin | | replaces squared loss with a loss bounded in the residual, or targets a quantile | minimising mean squared error | Huber regression, RANSAC, Theil-Sen, quantile regression, M-estimators | |
| L.lin.mixed | Hierarchical and mixed-effects models | L.lin | | adds group-level random effects or a correlation structure to the linear predictor | treating all observations as independent with one coefficient vector | linear mixed models, GEE, multilevel models, random-effects meta-analysis | |
| L.kernel | Kernel methods | | which learning problem the kernel is substituted into | replaces inner products with a kernel so a linear method acts in a feature space | computing explicit high-dimensional features and fitting linearly | SVM, kernel ridge, kernel PCA | |
| L.kernel.svm | Margin-maximising classifiers | L.kernel | | maximises the margin to the separating surface, with slack for errors | minimising a likelihood or squared error | perceptron, hard and soft-margin SVM, SVR, one-class SVM, structured SVM | |
| L.kernel.ridge | Kernelised least squares and components | L.kernel | | substitutes a kernel into a closed-form least-squares or eigen problem | solving a hinge-loss quadratic program | kernel ridge regression, kernel PCA, kernel k-means, kernel CCA | |
| L.kernel.approx | Kernel approximation | L.kernel | | approximates the kernel matrix with explicit random or sampled features | computing the exact kernel matrix | random Fourier features, Nystrom approximation, random kitchen sinks | |
| L.gp | Gaussian-process inference | | how the posterior is made tractable | places a GP prior over functions and computes a posterior predictive distribution | fitting point-estimate parameters with no function-space posterior | GP regression, SVGP, deep GP | |
| L.gp.exact | Exact GP regression | L.gp | | inverts the full kernel matrix to obtain the exact posterior | approximating with inducing points or a variational bound | GP regression, GP with marginal-likelihood hyperparameter fitting | |
| L.gp.sparse | Sparse and approximate GPs | L.gp | | summarises the data with inducing points or a variational posterior | exact cubic-cost inference | FITC, SVGP, SKI/KISS-GP, deep GP, GP classification by Laplace or EP | |
| L.tree | Decision-tree induction | | split criterion and pruning rule | grows a tree by recursively partitioning the feature space on single-variable tests | combining many trees as one predictor | ID3, C4.5, CART, CHAID, conditional inference trees | |
| L.bag | Bootstrap aggregation | L.boot | | averages predictors each fitted to a resampled version of the data | fitting predictors sequentially on reweighted data | bagging, random forest, extremely randomised trees, rotation forest | |
| L.boost | Boosting | | | fits predictors sequentially, each targeting the previous ensemble's errors | fitting predictors independently in parallel | AdaBoost, gradient boosting, XGBoost, LightGBM, CatBoost, NGBoost, LambdaMART | the strongest tabular baseline family |
| L.inst | Instance-based learning | | | makes predictions directly from stored training examples with no fitted global model | fitting parameters that summarise the data | k-NN, weighted k-NN, condensed NN, Parzen windows/KDE, LOESS, RBF interpolation | the canonical algorithm with no model |
| L.nb | Generative classifiers | | what is assumed about the class-conditional density | models each class's feature distribution and classifies by Bayes rule | modelling the conditional label distribution directly | naive Bayes, Gaussian/multinomial/Bernoulli NB, LDA, QDA, Bayesian network classifiers | |
| L.clust | Clustering | | what defines cluster membership | partitions or groups unlabelled points without any target variable | grouping by a supplied label | k-means, DBSCAN, Ward linkage | |
| L.clust.centroid | Centroid-based clustering | L.clust; L.em | | assigns points to the nearest of k representatives and updates the representatives | growing clusters by density connectivity or by merging | k-means, k-means++, mini-batch k-means, k-medoids/PAM, fuzzy c-means | |
| L.clust.hier | Hierarchical clustering | L.clust | | builds a nested merge or split tree under a linkage criterion | producing a flat partition with a fixed k | agglomerative clustering, single/complete/average/Ward linkage, divisive clustering | |
| L.clust.density | Density-based clustering | L.clust | | defines clusters as connected regions above a density threshold | assuming a fixed number of convex clusters | DBSCAN, OPTICS, HDBSCAN, mean-shift | |
| L.clust.model | Mixture-model clustering | L.clust; L.em | | fits a probabilistic mixture and assigns soft responsibilities | assigning hard memberships by distance | Gaussian mixture models, Bayesian GMM, Dirichlet-process mixtures, latent class analysis | |
| L.clust.graph | Graph and spectral clustering | L.clust; L.graphalg | | clusters using the eigenstructure or modularity of a similarity or adjacency graph | clustering directly in feature space | spectral clustering, normalised cuts, affinity propagation, Louvain, Leiden | |
| L.dimred | Dimensionality reduction and factorisation | | what structure of the data the low-dimensional map preserves | produces a lower-dimensional representation of the data with no target variable | predicting a target from features | PCA, t-SNE, UMAP, NMF | many of these produce no separable model |
| L.dimred.var | Variance-preserving projections | L.dimred; L.ls | | finds orthogonal directions maximising retained variance or minimising reconstruction error | preserving pairwise distances or neighbourhoods | PCA, probabilistic PCA, sparse PCA, kernel PCA, randomised SVD, incremental PCA | |
| L.dimred.indep | Independent-component decomposition | L.dimred | | finds a linear basis whose coefficients are maximally statistically independent | finding a basis that is merely uncorrelated | FastICA, Infomax ICA, JADE, SOBI | |
| L.dimred.parts | Parts-based and topic factorisation | L.dimred | | factorises with non-negativity or a generative topic prior so components are additive parts | allowing arbitrary signed loadings | NMF, sparse NMF, PLSA, latent Dirichlet allocation, dictionary learning | LDA here is the topic model, not the discriminant |
| L.dimred.dist | Neighbourhood-preserving embedding | L.dimred | | places points so that local neighbourhood structure is preserved in low dimensions | maximising global variance | MDS, Isomap, LLE, Laplacian eigenmaps, t-SNE, UMAP, PaCMAP, TriMap | t-SNE produces coordinates, not a reusable model |
| L.dimred.disc | Supervised and multi-view projections | L.dimred | | finds directions that maximise class separation or cross-view correlation | ignoring labels and second views | Fisher LDA, CCA, kernel CCA, deep CCA, PLS regression | |
| L.dimred.rand | Random projection and sketching | L.dimred | | projects with a random matrix whose distortion is bounded in expectation | fitting the projection to the data | Johnson-Lindenstrauss projection, sparse random projection, CountSketch, random SVD sketching | |
| L.dimred.mf | Matrix completion and collaborative factorisation | L.dimred; L.rec | | factorises a partially observed matrix to predict its missing entries | factorising a fully observed matrix for representation | ALS matrix factorisation, SVD++, soft-impute, nuclear-norm completion | |
| L.seq | State-space and structured sequence inference | | what state representation inference runs over | infers a latent sequence or its parameters under an explicit temporal model | fitting an unstructured sequence model with no latent-state semantics | HMM, Kalman filter, CRF | |
| L.seq.hmm | Discrete-state sequence inference | L.seq; L.em | | runs forward-backward or Viterbi recursions over a discrete latent chain | assuming a continuous Gaussian state | forward-backward, Baum-Welch, Viterbi, HSMM | |
| L.seq.kalman | Gaussian state-space filtering | L.seq | | propagates a Gaussian belief through linear or linearised dynamics | representing the belief by particles | Kalman filter, EKF, UKF, RTS smoother, information filter | |
| L.seq.pf | Sequential Monte Carlo | L.seq; L.mcmc | | represents the belief by weighted particles that are resampled over time | maintaining a closed-form Gaussian belief | particle filter, auxiliary particle filter, SMC, SMC-squared, particle MCMC | |
| L.seq.crf | Discriminative structured prediction | L.seq | | models the conditional distribution over label sequences with global normalisation | modelling the joint distribution of observations and labels | MEMM, linear-chain CRF, structured perceptron, structured SVM | |
| L.seq.ts | Classical time-series forecasting | L.seq | | fits an explicit autoregressive, trend and seasonality decomposition | fitting a generic neural sequence model | ARIMA, SARIMA, exponential smoothing, Holt-Winters, Prophet, structural time series, VAR | |
| L.graphalg | Graph algorithms as learning procedures | | what is propagated across the graph | computes a quantity by propagating along a graph's edges to convergence | computing from feature vectors without a graph | PageRank, belief propagation, Louvain, Weisfeiler-Lehman kernel, shortest paths | |
| L.boot | Resampling-based inference | | what is resampled and for what estimate | re-fits an estimator on resampled data to quantify variability or select a model | computing an analytic standard error | bootstrap, jackknife, permutation test, k-fold cross-validation | |
| L.boot.ci | Resampling confidence estimation | L.boot | | builds intervals or standard errors from the distribution of resampled estimates | building intervals from an asymptotic formula | bootstrap, BCa bootstrap, block bootstrap, jackknife, bootstrap-t | |
| L.boot.cv | Cross-validation | L.boot | | partitions data into folds and averages held-out performance to select or assess | evaluating once on a single held-out split | k-fold CV, stratified CV, leave-one-out, nested CV, time-series CV, group CV | admissible only if evaluation is in scope; see Tensions |
| L.boot.perm | Permutation and randomisation tests | L.boot; L.test | | builds a null distribution by permuting labels or group assignment | assuming a parametric null distribution | permutation test, randomisation test, permutation feature importance | |
| L.mcmc | Markov-chain Monte Carlo | | how proposals are generated | draws correlated samples from a target density via a Markov chain with the right stationary law | optimising a parametric approximation to the posterior | Metropolis-Hastings, Gibbs, HMC, NUTS | |
| L.mcmc.mh | Metropolis-Hastings family | L.mcmc | | proposes from an arbitrary kernel and accepts with the Metropolis ratio | sampling each coordinate from its exact conditional | Metropolis, Metropolis-Hastings, random-walk MH, adaptive MH, MALA | |
| L.mcmc.gibbs | Gibbs sampling | L.mcmc | | samples each block from its exact full conditional, always accepting | using an accept-reject step | Gibbs sampling, collapsed Gibbs, blocked Gibbs, slice sampling | |
| L.mcmc.grad | Gradient-informed samplers | L.mcmc | | uses the gradient of the log density to propose distant, high-acceptance moves | proposing without derivative information | Langevin/MALA, HMC, NUTS, SGLD, SGHMC, Riemannian HMC | SGLD bridges to stochastic optimisation |
| L.mcmc.temper | Tempered and annealed sampling | L.mcmc | | runs chains at multiple temperatures or anneals between distributions | a single chain at a fixed target | parallel tempering, simulated tempering, annealed importance sampling, SMC samplers | |
| L.mcmc.nested | Evidence-oriented sampling | L.mcmc | | targets the marginal likelihood by sampling nested likelihood shells | targeting posterior expectations only | nested sampling, MultiNest, dynamic nested sampling | speculative in ML venues; standard in astrostatistics |
| L.vi | Variational inference | | what family and bound are used | approximates a posterior by optimising a divergence over a tractable family | drawing samples from the exact posterior | mean-field VI, CAVI, SVI, ADVI, black-box VI, expectation propagation | parent of the VAE lineage |
| L.mle | Likelihood-based point estimation | | what is maximised or matched | selects parameters by maximising a likelihood or matching moments | producing a full posterior distribution | MLE, MAP, penalised likelihood, partial likelihood (Cox), method of moments, generalised method of moments, M-estimation | note the GMM name collision with Gaussian mixtures |
| L.test | Hypothesis testing and error control | | what is being controlled | computes a test statistic and a decision rule with a stated error rate | reporting an effect size with no decision rule | t-test, ANOVA, Mann-Whitney, chi-square, Bonferroni, Holm, Benjamini-Hochberg FDR | admissible only if evaluation is in scope |
| L.causal | Causal effect estimation | | what source of identification the estimator leans on | estimates an interventional or counterfactual contrast under a stated identification assumption | estimating a predictive association with no identification claim | propensity score matching, doubly robust estimation, difference-in-differences | |
| L.causal.adjust | Adjustment and weighting estimators | L.causal | | identifies the effect by conditioning on or reweighting by observed confounders | using an instrument or a discontinuity | g-computation, propensity score matching, IPW, AIPW/doubly robust, TMLE, double ML, entropy balancing | |
| L.causal.iv | Instrumental-variable estimation | L.causal | | uses a variable affecting treatment but not the outcome except through treatment | adjusting for measured confounders only | 2SLS, LIML, GMM-IV, deep IV, Mendelian randomisation | |
| L.causal.panel | Panel and design-based estimators | L.causal | | identifies from repeated observation of the same units before and after treatment | identifying from cross-sectional variation | difference-in-differences, event study, synthetic control, synthetic DiD, two-way fixed effects | |
| L.causal.disc | Discontinuity designs | L.causal | | identifies from assignment determined by a threshold in a running variable | identifying from random or conditionally random assignment | sharp regression discontinuity, fuzzy RD, kink designs | |
| L.causal.hte | Heterogeneous-effect estimation | L.causal; L.bag | | estimates how the effect varies with covariates, not only its average | estimating a single average treatment effect | causal forest, S/T/X-learner, DR-learner, uplift modelling, BART for causal effects | |
| L.causal.struct | Causal structure discovery | L.causal | | infers the graph of causal relations rather than an effect size given a graph | estimating an effect from an assumed graph | PC, FCI, GES, NOTEARS, LiNGAM, DAG-GNN, CCM | |
| L.causal.rep | Representation-based counterfactual estimation | L.causal; L.da.stat | | learns a representation balancing treated and control groups and predicts both potential outcomes | using a fixed propensity model with no learned representation | TARNet, CFR/IPM-balanced representations, Dragonnet, CEVAE, GANITE | |
| L.anom | Anomaly and outlier detection | | what makes a point anomalous | scores points by how unusual they are, typically fitted without anomaly labels | classifying points against labelled anomaly classes | isolation forest, one-class SVM, LOF | |
| L.anom.density | Density-based anomaly scoring | L.anom | | scores by estimated density or local density ratio | scoring by a learned decision boundary | KDE scoring, LOF, GMM likelihood scoring, COPOD | |
| L.anom.bound | Boundary-based anomaly scoring | L.anom; L.kernel.svm | | fits a compact boundary around the normal data and scores by distance outside | estimating a density | one-class SVM, SVDD, Deep SVDD | |
| L.anom.isol | Isolation and partition scoring | L.anom; L.tree | | scores by how few random splits are needed to isolate a point | fitting a density or a boundary | isolation forest, extended isolation forest, RRCF | |
| L.anom.recon | Reconstruction-error anomaly scoring | L.anom; L.vae | | scores by how badly a generative or autoencoding model reconstructs the point | scoring by an explicit density estimate | autoencoder reconstruction error, VAE ELBO scoring, diffusion reconstruction scoring | |
| L.anom.cp | Change-point and sequence anomalies | L.anom; L.seq.ts | | detects a shift in a temporal process rather than a point outlier | flagging individual independent points | CUSUM, Bayesian online change-point detection, PELT, matrix profile | |
| L.rec | Recommendation and ranking procedures | | what the ranking signal is fitted to | fits a model to produce an ordering over items for a user or query | predicting an unordered label | ALS collaborative filtering, BPR, LambdaMART | |
| L.rec.cf | Collaborative filtering | L.rec; L.dimred.mf | | predicts preferences from the interaction matrix alone | using item or query content features | user-kNN and item-kNN CF, ALS, SVD++, BPR, neural CF | |
| L.rec.ltr | Learning to rank | L.rec | | optimises a listwise or pairwise ranking loss against relevance judgements | optimising a pointwise regression loss | RankNet, LambdaRank, LambdaMART, ListNet, ListMLE | |
| L.optdisc | Discrete optimisation inside learning | | what combinatorial structure is solved | solves a combinatorial subproblem as a step inside a learning procedure | solving a continuous parameter optimisation | Hungarian matching, Sinkhorn, Viterbi, beam search as search | underrated: appears inside many deep pipelines |
| L.optdisc.assign | Assignment and matching | L.optdisc | | solves a bipartite matching to pair predictions with targets or clusters | sorting or thresholding heuristically | Hungarian algorithm, DETR bipartite matching, auction algorithm | |
| L.optdisc.ot | Optimal transport | L.optdisc | | computes a coupling minimising transport cost between two distributions | computing a pointwise divergence | Sinkhorn-Knopp, entropic OT, Wasserstein distance, Gromov-Wasserstein, SwAV assignment step | |
| L.optdisc.submod | Greedy submodular selection | L.optdisc; L.curate.active | | selects a set greedily under a submodular objective with an approximation guarantee | selecting by independent per-item score | facility location coresets, greedy maximum coverage, k-center greedy | |
| L.optdisc.exact | Exact combinatorial solvers | L.optdisc | | solves to optimality with branch and bound or an integer program | using a heuristic with no optimality claim | branch and bound, mixed-integer programming, constraint programming, SAT-based learning | |
| L.pinn | Constraint- and physics-informed fitting | | what known structure is imposed | adds a known equation, conservation law or logical constraint as part of the objective | learning the relationship purely from data | PINN, Lagrangian/Hamiltonian neural network training, SINDy, Deep Ritz | |
| L.symreg | Symbolic regression | | how the expression space is searched | searches over symbolic expressions for one that fits the data | fitting coefficients of a fixed functional form | genetic symbolic regression, SINDy, AI Feynman, neural-guided symbolic regression | partly speculative in mainstream ML venues |

---

## Axis 2 — signal

**What this axis is, and what I changed.** The hypothesis listed `label, reward, reconstruction,
agreement/contrast, score/denoising, likelihood, game equilibrium, causal contrast` as one value list.
Three of those (`likelihood`, `score/denoising`, part of `agreement/contrast`) answer *how prediction
and target are compared*; the rest answer *where the target comes from*. They are orthogonal by the
axis test: supervised classification and autoregressive pretraining share a form (categorical
likelihood) and differ in source; BYOL and SimCLR share a source (two augmented views of one instance)
and differ in form (regression to an EMA target vs an InfoNCE contrast). Keeping them in one list would
have forced one of those two pairs to look identical. So `signal` has **two sub-facets**, both
**multi-valued**, both unioning up a lineage chain: `S.src.*` (where the target comes from) and
`S.form.*` (how the target becomes a loss). I also added `S.src.none` / `S.form.none`, because a large
part of this dimension fits nothing — beam search, BPE, CutMix and post-training quantization do not
have a training target, and the honest encoding of that is a value, not a blank.

Renames from the hypothesis: `label` → split into `S.src.ext.human`, `S.src.ext.model`,
`S.src.ext.prog` (who produced the label matters more than the fact of a label); `reward` → split into
environment / verifier / learned-model / intrinsic; `reconstruction` → moved to `S.form.recon`, with
its *source* being `S.src.self.mask` or `S.src.self.corrupt`; `game equilibrium` → `S.form.game`;
`causal contrast` → `S.src.design.*` since the contrast is manufactured by a design, not by a loss.

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| S.src | Target source (sub-facet root) | | who or what produced the quantity the procedure is driven toward | the procedure is fitted to something; name what supplies it | the procedure fits nothing | all values below | multi-valued |
| S.src.ext | External annotation | S.src | what kind of agent produced the annotation | the target was produced by an agent outside the run's own model and environment | the target is computed from the input itself | labels, preferences, demonstrations | |
| S.src.ext.human | Human-produced labels | S.src.ext | | a person assigned the target value to the example | a model or a rule assigned it | ImageNet labels, annotated spans, human ratings | |
| S.src.ext.model | Model-produced targets | S.src.ext | | another trained model produced the target the learner is fitted to | the learner produced its own target | knowledge distillation teacher logits, synthetic instruction data, RLAIF labels, pseudo-labels from a different model | distinct from self-labelling, which is S.src.self.own |
| S.src.ext.prog | Programmatic and weak labels | S.src.ext | | a rule, heuristic, lexicon or metadata field supplied the target | a human adjudicated each example | Snorkel labelling functions, distant supervision, regex labels, metadata-derived labels | |
| S.src.ext.pref | Comparisons and rankings | S.src.ext | | the target is a relative judgement between two or more candidates, not an absolute value | the target is an absolute score or class | RLHF comparison pairs, learning-to-rank relevance judgements, KTO thumbs | |
| S.src.ext.demo | Expert demonstrations | S.src.ext | | the target is an action sequence produced by an expert acting in the task | the target is a scalar score of the agent's own behaviour | behaviour-cloning trajectories, DAgger corrections, teleoperated robot data | |
| S.src.ext.pair | Naturally co-occurring pairs | S.src.ext | | supervision comes from items that were observed together in the world, not annotated | an annotator created the association | image-alt-text pairs for CLIP, audio-video sync, translation bitext, click logs | boundary between supervised and self-supervised |
| S.src.env | Environment feedback | S.src | what generates the scalar feedback | the target is feedback returned after the system acted | the target exists before the system acts | game score, verifier pass/fail, curiosity bonus | |
| S.src.env.reward | Task reward from the environment | S.src.env | | an external environment or simulator emits the scalar being maximised | the scalar is computed by a model the run also trained | Atari score, MuJoCo reward, game win/loss | |
| S.src.env.verifier | Programmatic verifier reward | S.src.env | | a deterministic checker decides correctness of the produced output | a learned model judges the output | unit-test pass, exact-match answer check, compiler success, formal proof check | the RLVR branch |
| S.src.env.rm | Learned reward model | S.src.env; S.src.ext.pref | | the reward is emitted by a model fitted on external judgements | the reward comes from the environment directly | RLHF reward models, process reward models, LLM-as-judge reward | derived from preferences, hence multi-parent |
| S.src.env.intr | Intrinsic reward | S.src.env | | the reward is computed from the agent's own prediction error, novelty or counts | the reward is supplied from outside the agent | RND bonus, ICM error, pseudo-counts, empowerment, DIAYN diversity reward | |
| S.src.self | The input itself | S.src | which part of the input plays the role of target | the target is a deterministic function of the unlabelled input | a separate agent or environment supplied the target | masked tokens, augmented views, noise added by the method | |
| S.src.self.mask | Hidden part of the input | S.src.self | | part of the input is removed and the procedure predicts exactly what was removed | the input is perturbed but nothing is withheld for prediction | BERT masked tokens, MAE masked patches, span corruption, inpainting | |
| S.src.self.next | The next or future element | S.src.self | | the target is the continuation of an observed prefix, in time or sequence order | the target is a hidden element of a bidirectional context | next-token prediction, PixelCNN, future-frame prediction, CPC futures | |
| S.src.self.view | A second view of the same instance | S.src.self | | two transformed copies of one instance are made and compared to each other | one copy only, compared to a stored label | SimCLR views, BYOL views, SwAV views, multi-crop | |
| S.src.self.corrupt | A deliberately corrupted copy | S.src.self | | noise of known magnitude is added and the procedure must undo or score it | a transformation whose inverse is not the learning target | DDPM noise, denoising autoencoder noise, score matching perturbation | |
| S.src.self.ident | The input itself, unmodified | S.src.self | | the target is the whole input, reproduced with no part hidden and no noise added | part of the input is withheld or corrupted first | autoencoder reconstruction, VAE reconstruction term, PCA reconstruction, self-reconstruction losses | added after the VAE worked example found no fitting value |
| S.src.self.own | The model's own prior output | S.src.self | | the learner's own current, averaged or past prediction serves as the target | another model produced the target | pseudo-labelling, Mean Teacher EMA targets, self-training, self-consistency, bootstrapped values | includes RL bootstrapping |
| S.src.self.struct | Structure of the unlabelled data | S.src.self | | the objective is defined on the geometry or statistics of the whole dataset, not per example | a per-example target | k-means distortion, PCA variance, t-SNE neighbourhoods, topic-model likelihood | the classical-unsupervised home |
| S.src.design | Identification by study design | S.src | what feature of the design creates the counterfactual contrast | the target is a contrast between conditions that a design argues is comparable | the target is a predictive association with no comparability claim | RCT arms, propensity-matched pairs, instrument, discontinuity | |
| S.src.design.rand | Randomised assignment | S.src.design | | treatment was assigned at random by the experimenter | treatment was observed as it occurred | A/B tests, randomised controlled trials, randomised encouragement | |
| S.src.design.adjust | Conditional comparability | S.src.design | | comparability is claimed after conditioning on measured covariates | comparability comes from an instrument, threshold or time structure | propensity matching, IPW, AIPW, double ML, g-computation | |
| S.src.design.quasi | Quasi-experimental structure | S.src.design | | comparability comes from an instrument, a threshold or a pre/post panel | comparability comes from covariate adjustment alone | 2SLS instruments, regression discontinuity, difference-in-differences, synthetic control | |
| S.src.design.indep | Conditional-independence signal | S.src.design | | the signal is the pattern of statistical (in)dependences used to orient edges | the signal is an effect magnitude | PC algorithm tests, FCI, GES score differences, LiNGAM non-Gaussianity | |
| S.src.theory | Known law or constraint | S.src | what kind of prior knowledge is imposed | the target is the residual of an equation or constraint assumed true a priori | a target measured from data | PDE residuals, conservation laws, logical constraints | |
| S.src.theory.pde | Differential-equation residual | S.src.theory | | the loss contains the residual of a differential equation evaluated at sampled points | the equation is used only to generate training data | PINN residual loss, Deep Ritz, Hamiltonian NN constraint | |
| S.src.theory.logic | Symbolic or logical constraint | S.src.theory | | the loss penalises violation of a declared logical or algebraic constraint | the constraint is enforced by construction in the architecture | semantic loss, constraint-satisfaction penalties, Lagrangian constraint terms | speculative outside neuro-symbolic venues |
| S.src.none | No training target | S.src | | the procedure has no quantity it is fitted to; it transforms or selects instead | any fitted parameter, even a single calibration statistic | beam search, top-p sampling, BPE merges (counting, not fitting), CutMix, gradient clipping, FSDP sharding | essential: roughly a third of the dimension sits here |
| S.form | Comparison form (sub-facet root) | | how the gap between model output and target is turned into a number | name the functional form of the training criterion | the procedure has no criterion | all values below | multi-valued |
| S.form.lik | Exact likelihood | S.form | | maximises a normalised log-probability the model can compute exactly | maximises a bound or an unnormalised score | cross-entropy, autoregressive LM loss, GLM likelihood, normalizing-flow likelihood, MLE | |
| S.form.bound | Variational bound | S.form | | maximises a tractable lower bound on an intractable log-likelihood | maximises the exact likelihood | ELBO, IWAE bound, variational EM, SVI, beta-VAE objective | |
| S.form.score | Score and denoising criteria | S.form | | regresses the gradient of the log-density, or equivalently the added noise | regresses the clean data point itself | score matching, denoising score matching, DDPM epsilon-prediction, flow-matching velocity | |
| S.form.recon | Reconstruction error | S.form | | penalises a distance between a reconstruction and the original input | penalises a distance between two different instances' representations | autoencoder MSE, MAE pixel loss, PCA reconstruction, VQ codebook loss | |
| S.form.contrast | Contrastive criteria | S.form | | the loss has explicit negatives whose similarity is pushed down | the loss only pulls positives together | InfoNCE, NT-Xent, triplet loss, BPR pairwise loss, noise-contrastive estimation | |
| S.form.agree | Agreement to a target network | S.form | | regresses one branch onto a target branch, with no negatives and a stop-gradient or EMA | uses negatives, or a fixed external label | BYOL, SimSiam, Mean Teacher consistency, SPR latent loss, data2vec | collapse-avoidance is the signature |
| S.form.redun | Decorrelation criteria | S.form | | drives an embedding cross-correlation or covariance matrix toward a target structure | compares individual sample pairs | Barlow Twins, VICReg, W-MSE, whitening losses | |
| S.form.margin | Margin criteria | S.form | | penalises violations of a required separation between scores | penalises probability error | hinge loss, SVM margin, triplet margin, large-margin softmax | |
| S.form.dist | Distortion and assignment criteria | S.form | | minimises total distance of points to assigned representatives or a layout | minimises a probabilistic loss | k-means distortion, MDS stress, t-SNE KL over neighbour distributions, OT cost | |
| S.form.game | Adversarial equilibrium | S.form | | the criterion is a minimax between two optimisers with opposed objectives | both terms are minimised by the same optimiser | GAN objective, WGAN critic, DANN domain adversary, adversarial training inner max, GAIL | |
| S.form.return | Expected-return maximisation | S.form | | maximises a discounted sum of future scalars, with credit assigned across time | maximises a per-example score with no temporal credit | policy gradient surrogates, Bellman TD error, PPO clipped surrogate, Q-learning loss | |
| S.form.div | Distribution matching | S.form | | minimises an explicit divergence or moment discrepancy between two distributions | minimises a per-example loss | MMD, CORAL, KL to a teacher, Sinkhorn divergence, moment matching | distillation's form when it is not plain cross-entropy |
| S.form.moment | Estimating-equation solving | S.form | | chooses parameters by setting a sample moment or influence-function equation to zero | minimising a loss by descent | method of moments, GMM-IV, Z-estimation, TMLE targeting step, estimating equations in GEE | added after the TMLE worked example found no fitting value |
| S.form.rank | Ranking and preference criteria | S.form | | the loss depends only on the order of scores, not their absolute values | the loss depends on absolute score values | DPO loss, Bradley-Terry likelihood, LambdaRank, ListNet, pairwise ranking loss | Bradley-Terry is also a likelihood; both values apply |
| S.form.resid | Constraint residual | S.form | | penalises violation of an equation or constraint evaluated on sampled points | penalises distance to observed data | PINN PDE residual, Lagrangian penalty, semantic loss | |
| S.form.post | Posterior targeting | S.form | | the procedure's criterion is correctness of a posterior, approached by sampling | the criterion is a point estimate's loss | MCMC detailed balance, SMC weighting, Bayes rule updates | no gradient descent needed to satisfy it |
| S.form.conf | Confidence and entropy criteria | S.form | | the criterion is a function of the model's own output confidence only | the criterion involves any target outside the model's output | entropy minimisation (TENT), confidence penalty, FixMatch thresholding, pseudo-label confidence gating | |
| S.form.spars | Sparsity and complexity criteria | S.form | | penalises the number or magnitude of active components, independent of fit | penalises fit error | L1 penalty, nuclear norm, MDL, AIC/BIC selection, sparse-autoencoder L1 | usually appears alongside a fit term |
| S.form.inv | Invariance and robustness criteria | S.form | | penalises variation of the output under a declared nuisance transformation or environment | penalises error on the observed distribution only | IRM penalty, consistency regularisation, GroupDRO worst-group risk, VAT | |
| S.form.cover | Coverage criteria | S.form | | targets a stated frequency guarantee on a held-out distribution | targets average accuracy | conformal quantile calibration, conformal risk control, quantile pinball loss | |
| S.form.none | No criterion | S.form | | the procedure performs no comparison between an output and a target | any fitted or calibrated quantity | beam search, all-reduce, pipeline scheduling, magnitude pruning, BPE | |

---

## Axis 3 — role

**What this axis is, and what I changed.** Which slot of the run the procedure fills. The top-level
set below is a division of the axis by **the stage of the run at which the procedure acts and on what
it acts**; every child set refines that. The axis is **multi-valued**: a method that changes both the
objective and the experience distribution (intrinsic motivation, adversarial training) carries both,
and that is exactly what the co-occurrence sibling test predicts — PPO and Adam are not siblings
because they occupy different nodes here.

Changes to the hypothesis: added `R.fit.init` (initialisation schemes are named procedures with no
other home), `R.fit.grad` (gradient clipping and gradient surgery are neither the objective nor the
update rule), `R.fit.stop`, `R.out.context` (retrieval is a slot, and RAG papers fill no other),
`R.out.calib` and `R.out.predict` (a nonparametric method's prediction rule had no slot at all).
**Removed `compression`**, which failed the "property of the algorithm or of its use"
test: compression is a *goal* people pursue with three unrelated slots — pruning and quantization
rewrite the parameter tensor (now `R.rewrite`), distillation defines an objective (`R.fit.obj` with
`S.src.ext.model`), and speculative decoding is a decoder (`R.out.decode`). Grouping them by their
shared motivation would have made them look like alternatives for one slot, which they are not: you
can and do run all three in one pipeline. `R.eval` is included but flagged — see Tensions.

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| R.data | Data preparation | | what the procedure does to the example set | acts on the training examples before they reach the learner | acts on parameters, gradients or outputs | tokenization, augmentation, curriculum | |
| R.data.repr | Input representation construction | R.data | | converts raw input into the units or features the model consumes | changes which examples are present | BPE, WordPiece, feature scaling, discretisation, spectrogram extraction, one-hot encoding | |
| R.data.aug | Example transformation | R.data | | emits a transformed version of an existing example for training | emits an entirely new example | mixup, CutMix, RandAugment, SpecAugment, back-translation, adversarial perturbation | |
| R.data.select | Example selection, weighting and ordering | R.data | | decides which examples are used, with what weight, in what order | changes the content of an example | dedup, quality filtering, DoReMi, curriculum learning, active learning, class-imbalance resampling | |
| R.data.label | Target construction for unlabelled data | R.data | | assigns a target to an example that did not have one | assigns targets by a human annotator inside the run | pseudo-labelling, Snorkel, label propagation, Dawid-Skene, HER relabelling | |
| R.data.synth | Example synthesis | R.data | | creates training examples that did not exist before | transforms examples that already exist | Self-Instruct, domain randomisation, generative oversampling, dataset distillation | |
| R.exp | Experience generation | | what determines the distribution of collected interaction | determines what interaction data the learner sees, by acting | consumes a fixed dataset | epsilon-greedy, PER, self-play | empty for any run with a static dataset |
| R.exp.act | Behaviour and exploration policy | R.exp | | decides which action is taken for data-collection purposes | decides how the collected data updates parameters | epsilon-greedy, Boltzmann exploration, UCB, Thompson sampling, RND bonus, NoisyNets | |
| R.exp.store | Experience storage and reuse | R.exp | | decides which past interaction is replayed and with what target | decides which fresh action to take | experience replay, PER, HER, episodic memory, rehearsal buffers | |
| R.exp.task | Task and opponent generation | R.exp | | decides which environment, goal or opponent the agent faces next | decides the action within a fixed task | self-play, PSRO, league training, PLR, POET, automatic domain randomisation | |
| R.fit | Producing or adapting the learned object | | which part of the fitting loop the procedure defines | participates in turning data into parameters | acts before data reaches the learner, or after parameters are final | loss functions, optimisers, LoRA | |
| R.fit.init | Initialisation | R.fit | | sets parameter values before any update | changes parameters after updates have begun | He init, Xavier init, orthogonal init, LSUV, Fixup, muP init | boundary with architecture; see Tensions |
| R.fit.obj | Objective definition | R.fit | | defines the scalar the run minimises, including added penalty terms | defines how that scalar's gradient is turned into a step | cross-entropy, InfoNCE, ELBO, PPO surrogate, weight decay, KD loss, SAM | the most crowded slot in the dimension |
| R.fit.est | Estimator and inference engine | R.fit | | defines how an intractable expectation or posterior is estimated or sampled | defines the scalar being estimated | REINFORCE estimator, reparameterisation trick, straight-through estimator, Gumbel-softmax, EM E-step, MCMC, variational inference, SMC | the slot that makes classical statistics fit |
| R.fit.grad | Gradient post-processing | R.fit | | modifies the gradient between the backward pass and the update | modifies the loss, or the optimiser's internal state rule | gradient clipping, gradient accumulation, PCGrad, DP-SGD noise, gradient compression at the worker | |
| R.fit.update | Parameter update rule | R.fit | | maps a gradient and optimiser state to a parameter change | produces the gradient, or decides which parameters are eligible | SGD, momentum, Adam, AdamW, L-BFGS, Shampoo, Muon, CMA-ES, closed-form normal equations | Adam never fills any other slot; the slot test passes cleanly |
| R.fit.sched | Optimisation schedule and control | R.fit | | changes a hyperparameter of the update over the course of training | changes the direction of the update | cosine annealing, SGDR, warmup, one-cycle, ReduceLROnPlateau, batch-size ramps, EMA decay schedule | |
| R.fit.scope | Adaptation scope | R.fit | | decides which parameters are eligible to change, or adds new ones to change instead | decides how eligible parameters change | LoRA, adapters, prefix tuning, BitFit, linear probing, layer freezing, PackNet masks | |
| R.fit.stop | Stopping and checkpoint selection | R.fit | | decides when fitting ends or which produced checkpoint is kept | decides the step size while fitting continues | early stopping, patience, best-on-validation checkpointing, trial early-stopping in Hyperband | |
| R.coord | Coordination across workers | | which dimension of work or state is distributed | determines how a single logical run is executed across multiple workers or devices | determines the mathematics of the update on one device | all-reduce SGD, ZeRO, FedAvg | mathematically transparent methods still belong here |
| R.coord.replicate | Replicated data-parallel execution | R.coord | | every worker holds the full model and processes a different data shard | workers hold different parts of the model | synchronous SGD, ring all-reduce, Hogwild!, local SGD, DiLoCo, gossip SGD | |
| R.coord.partition | Model-state partitioning | R.coord | | the model's parameters, optimiser state or layers are split across devices | the model is replicated | ZeRO-1/2/3, FSDP, Megatron tensor parallel, GPipe, 1F1B, expert parallelism, ring attention | |
| R.coord.comm | Communication reduction | R.coord | | changes what or how often workers transmit, not what they compute locally | changes which worker computes what | gradient quantization, PowerSGD, top-k sparsification, infrequent averaging, hierarchical all-reduce | |
| R.coord.mem | Memory-compute trade-off | R.coord | | trades recomputation or data movement against stored state on one device | trades work across devices | gradient checkpointing, activation offload, CPU/NVMe offload, mixed precision with loss scaling | borderline systems rather than learning |
| R.coord.agg | Constrained aggregation of client updates | R.coord | | combines updates from parties that do not share raw data, under a stated constraint | combines gradients from workers that share one dataset | FedAvg aggregation, SCAFFOLD control variates, secure aggregation, trimmed-mean robust aggregation | |
| R.search | Configuration search | | which part of the configuration is searched | runs or simulates multiple configurations and selects among them by a measured signal | fixes the configuration in advance | random search, Hyperband, DARTS | the inner trials are themselves runs |
| R.search.hp | Hyperparameter search | R.search | | searches scalar or categorical settings of a fixed learning procedure | searches the model's structure | grid search, random search, TPE, SMAC, Hyperband, ASHA, PBT, muTransfer | |
| R.search.arch | Architecture search | R.search | | searches the structure of the model itself | searches the optimiser's settings | NASNet, ENAS, DARTS, Once-for-All, regularised evolution, zero-cost proxies | |
| R.search.pipe | Pipeline and algorithm selection | R.search | | searches jointly over preprocessing, model family and their hyperparameters | searches within one fixed model family | Auto-WEKA, auto-sklearn, TPOT, AutoGluon | |
| R.search.policy | Procedure-policy search | R.search | | searches over which data or training procedure to apply, rather than model settings | searches over the model or its scalars | AutoAugment, Population-Based Augmentation, learned curricula, data-mixture search | the slot AutoAugment really occupies |
| R.rewrite | Parameter-space rewriting | | what is changed about the stored parameters | transforms an existing parameter set without redefining what the model computes | fits parameters from data in the first place | magnitude pruning, GPTQ, model soups | replaces the hypothesis's "compression" |
| R.rewrite.sparse | Sparsification | R.rewrite | | removes parameters or structures from the computation | changes the numeric representation of retained parameters | magnitude pruning, lottery ticket, movement pruning, SparseGPT, Wanda, channel and head pruning | |
| R.rewrite.precision | Precision reduction | R.rewrite | | lowers the numeric precision of weights, activations or caches | removes parameters | GPTQ, AWQ, SmoothQuant, LLM.int8, QAT, LSQ, BinaryConnect, KV-cache quantization | QAT also occupies R.fit.est via the straight-through estimator |
| R.rewrite.factor | Factorisation | R.rewrite | | replaces a weight tensor with a product of smaller factors | zeroes or requantises the original tensor | SVD compression, Tucker and CP decomposition, ASVD | speculative: often unnamed |
| R.rewrite.combine | Parameter combination | R.rewrite | | produces one parameter set by combining several | produces one by combining several models' predictions | model soups, task arithmetic, TIES, DARE, Fisher merging, SWA, EMA of weights | |
| R.out | Producing outputs from the learned object | | what the procedure contributes between a trained model and an emitted result | runs at inference and changes what is emitted, how it is scored, or what it was given | changes the parameters | beam search, RAG, conformal prediction | |
| R.out.decode | Output generation | R.out | | converts model scores into the emitted output | explores multiple complete candidate outputs | greedy, beam search, top-p, contrastive decoding, constrained decoding, speculative decoding, diffusion samplers, classifier-free guidance | |
| R.out.search | Test-time search and deliberation | R.out | | spends extra inference compute exploring several reasoning or action paths | emits one pass through the model | self-consistency, best-of-n, tree of thoughts, ReAct, Reflexion, MCTS, MPC/CEM, A-star | the cost shows up in the run's budget |
| R.out.context | Retrieval and context construction | R.out | | selects external content to place in the model's input at inference | selects training examples before fitting | BM25, DPR, HNSW index lookup, RAG, FiD, reranking, kNN-LM | |
| R.out.calib | Calibration, uncertainty and abstention | R.out | | converts outputs into calibrated probabilities, intervals or an abstention decision | converts them into a different emitted answer | temperature scaling, isotonic regression, conformal prediction, deep ensembles, MC dropout, OOD scoring | |
| R.out.agg | Inference-time aggregation | R.out | | combines outputs of several models or several samples into one | combines their parameters | voting, prediction averaging, stacking, MBR, Bayesian model averaging, MoE inference routing | |
| R.out.predict | Prediction rule | R.out | | computes the output by an explicit named procedure over stored data or fitted structure, with no model forward pass to delegate to | emitting the forward pass of a separable model | k-NN majority vote, kernel density prediction, LOESS local fit, Viterbi decoding of a CRF, GP posterior mean | added after the k-NN worked example found no fitting slot |
| R.out.explain | Explanation production | R.out | | produces a statement about the model's behaviour as the run's output | produces a prediction about the data | Grad-CAM, integrated gradients, LIME, SHAP, activation patching, sparse autoencoder features, CKA | admitted because an explanation is an output |
| R.adapt | Test-time adaptation | | what is updated using test-time data | updates the model or its statistics after deployment, using unlabelled test inputs | updates using labelled target data before deployment | TENT, TTT, SHOT, BN-statistic adaptation, CoTTA, test-time prompt tuning | overlaps R.fit by construction; kept separate because "when" is definitional here |
| R.eval | Evaluation and model assessment | | what the assessment procedure controls | computes a reported performance or inference claim about the fitted object | contributes to producing the object or its outputs | k-fold cross-validation, bootstrap CIs, permutation tests, FDR control, LLM-as-judge scoring, significance tests | the participant rule as written excludes this; see Tensions |

---

## Axis 4 — attributes

**What this axis is, and what I changed.** Orthogonal properties that two algorithms can differ on
while agreeing on lineage, signal and role. Grouped into **families**; each family row states whether
it is single- or multi-valued. Every single-valued family implicitly admits *not applicable* (the
on/off-policy family is simply empty for AdamW), so "n.a." is not listed as a node. Only properties
that pass the "property of the algorithm, not of its use" test are here: `A.outspace` is a genuine
applicability constraint of the method (DDPG cannot be run on discrete actions), whereas "modality",
"application domain" and "compute scale" were rejected as properties of the run or the paper.

Changes to the hypothesis: `federated` was demoted from a standalone flag to two values of
`A.topology` plus the separate `A.datalocality` family, because "federated" bundles a topology claim
and a data-governance claim that can vary independently (cross-silo FL with pooled-equivalent trust
behaves like decentralised training). `centralised/decentralised` was split into `A.topology` (who
talks to whom during training) and `A.exec` (what information each agent has at execution time), since
CTDE is centralised on one and decentralised on the other. `online/offline` was split into `A.regime`
(RL data collection) and `A.cadence` (how much data each update sees), which the single word conflated.
Added `A.parametric` so that "the run has no model" is recorded as a property rather than inferred,
`A.deriv`, `A.uncertainty` and `A.guarantee` (which is what makes the classical-statistics branch
aggregable at all).

| node_id | name | parents | characteristic | positive_test | negative_test | examples | notes |
|---|---|---|---|---|---|---|---|
| A.regime | Data-collection regime | | relation between the policy being improved and the policy that produced the data | applies when the procedure learns from interaction data | a procedure consuming a fixed i.i.d. dataset | on-policy, off-policy, offline | single-valued |
| A.regime.on | On-policy | A.regime | | updates are computed only from data generated by the current policy | reusing data from an earlier policy version | REINFORCE, A2C, PPO, SARSA, MAPPO | |
| A.regime.off | Off-policy with interaction | A.regime | | reuses data from other or older policies while still collecting new data | never collecting new data | DQN, SAC, TD3, DDPG, Q-learning | |
| A.regime.offline | Offline | A.regime | | never interacts with the environment during learning | collecting even a small amount of fresh interaction | BCQ, CQL, IQL, Decision Transformer, behaviour cloning | |
| A.world | Use of a transition model | | whether a dynamics model exists and where it came from | applies to sequential decision procedures | supervised fitting on i.i.d. data | model-free, learned model, given model | single-valued |
| A.world.free | Model-free | A.world | | never predicts next states or rewards | predicting dynamics for any purpose | DQN, PPO, SAC, A3C | |
| A.world.learned | Learned dynamics model | A.world | | fits a transition or reward model from data and uses it | using a simulator or rules supplied exogenously | Dyna, PETS, Dreamer, MuZero, MBPO | |
| A.world.given | Given dynamics model | A.world | | uses an exact model of the environment supplied by the problem | learning the model from experience | value iteration, AlphaZero game rules, MPC with analytic dynamics, iLQR | |
| A.rltarget | Represented quantity in control | | which of value or policy is explicitly parameterised | applies to control procedures | prediction with no action selection | value-based, policy-based, actor-critic | single-valued |
| A.rltarget.value | Value-based | A.rltarget | | acts greedily on a learned value function with no separate policy parameters | maintaining explicit policy parameters | Q-learning, DQN, Rainbow, IQN, FQI | |
| A.rltarget.policy | Policy-based | A.rltarget | | parameterises the policy directly with no learned value baseline | learning a critic | REINFORCE, evolution-strategy policy search, CMA-ES policies | |
| A.rltarget.ac | Actor-critic | A.rltarget | | parameterises both a policy and a learned value estimate | having only one of the two | A2C, PPO, SAC, TD3, IMPALA, MAPPO | |
| A.hier | Temporal abstraction | | whether the procedure acts over extended sub-behaviours | applies to control procedures | single-step prediction | flat, hierarchical | single-valued |
| A.hier.flat | Flat control | A.hier | | selects one primitive action per environment step | selecting a sub-policy that runs for many steps | DQN, PPO, SAC | |
| A.hier.hier | Hierarchical control | A.hier | | selects temporally extended options or subgoals with their own termination | selecting a primitive action each step | options framework, option-critic, FeUdal, HIRO, HAC | |
| A.deriv | Information used to choose a step | | what information about the objective the step rule consumes | applies to any procedure that searches a parameter or configuration space | a procedure with no search at all | first-order, preconditioned, zeroth-order, closed-form, combinatorial, sampling | multi-valued; changed from single-valued after HMC and XGBoost each needed two values |
| A.deriv.first | First-order gradient | A.deriv | | uses the gradient, scaled only per coordinate | uses curvature across coordinates | SGD, momentum, Adam, AdamW, Adafactor, Lion | per-coordinate adaptivity is still first-order |
| A.deriv.second | Curvature-preconditioned | A.deriv | | uses a matrix approximation of curvature across coordinates | scaling each coordinate independently | L-BFGS, K-FAC, Shampoo, Muon, Gauss-Newton, natural gradient | |
| A.deriv.zero | Zeroth-order | A.deriv | | uses only function evaluations, never derivatives | differentiating the objective | CMA-ES, OpenAI-ES, Nelder-Mead, random search, simulated annealing | |
| A.deriv.closed | Closed-form | A.deriv | | obtains the solution by solving an equation or decomposition in one shot | iterating a step rule to convergence | OLS normal equations, ridge closed form, PCA by SVD, LDA, Platt-free isotonic fit | |
| A.deriv.comb | Combinatorial search | A.deriv | | searches a discrete structure with pruning, DP or enumeration | searching a continuous space | branch and bound, Viterbi, beam search, Hungarian matching, greedy submodular | |
| A.deriv.sample | Sampling-based | A.deriv | | explores by drawing from a target or proposal distribution, not by descending | descending a deterministic criterion | Metropolis-Hastings, Gibbs, HMC, NUTS, SMC, Langevin dynamics | SGLD carries this and A.deriv.first |
| A.cadence | Data seen per update | | how much data each parameter update consumes | applies to iterative fitting procedures | a one-shot closed-form fit | full-batch, minibatch, per-example, single-pass streaming | single-valued |
| A.cadence.full | Full-batch | A.cadence | | each update uses the entire training set | each update uses a sample | L-BFGS on full data, batch gradient descent, EM over the full dataset, IRLS | |
| A.cadence.mini | Minibatch stochastic | A.cadence | | each update uses a random subset of fixed size | each update uses the full dataset or one example | SGD, Adam, most deep learning | |
| A.cadence.one | Per-example online | A.cadence | | updates after each individual example, typically without storage | updating from a batch | perceptron, online gradient descent, Hogwild! per-sample, online k-means | |
| A.cadence.stream | Single-pass streaming | A.cadence | | each example is seen once and cannot be revisited | revisiting data across epochs | streaming k-means, reservoir methods, online change-point detection, sketching | |
| A.topology | Coordination topology | | who exchanges state with whom during training | applies when more than one worker participates | single-device training | single, centralized-sync, centralized-async, decentralized, federated-device, federated-silo | single-valued |
| A.topology.single | Single worker | A.topology | | one process holds the whole run | any inter-worker exchange | default single-GPU training | |
| A.topology.csync | Centralized synchronous | A.topology | | all workers synchronise their updates at a global barrier | workers proceeding on stale state | all-reduce SGD, FSDP, ZeRO, synchronous pipeline | |
| A.topology.casync | Centralized asynchronous | A.topology | | workers push to a shared aggregator without waiting for each other | a barrier per step | Hogwild!, Downpour, ASGD, FedBuff | |
| A.topology.decen | Decentralized peer-to-peer | A.topology | | workers exchange only with neighbours; there is no aggregator | an aggregator or all-reduce over all workers | D-PSGD, gossip SGD, SGP | |
| A.topology.feddev | Federated cross-device | A.topology | | very many intermittently available clients, each with little data | a few always-on organisational participants | FedAvg on phones, DP-FedAvg, client sampling | |
| A.topology.fedsilo | Federated cross-silo | A.topology | | a small number of persistent organisational parties | many transient device clients | hospital or bank consortium FL, split learning across silos | |
| A.datalocality | Raw-data locality constraint | | whether raw data may be moved to one place | applies when data originates in more than one place | all data already pooled | pooled, local-only | single-valued |
| A.datalocality.pooled | Pooled | A.datalocality | | raw training data is allowed to be centralised | a constraint forbidding raw-data transfer | standard distributed training, data-parallel pretraining | |
| A.datalocality.local | Raw data stays local | A.datalocality | | only model updates or statistics cross the party boundary | shipping raw examples to a central store | federated learning, split learning, local differential privacy pipelines | |
| A.privacy | Formal privacy or security property | | what adversary the guarantee is stated against | applies when the paper claims a protection property | an informal privacy claim | differential privacy, secure aggregation, encrypted computation, unlearning | multi-valued |
| A.privacy.dp | Differential privacy | A.privacy | | a per-example sensitivity bound and a reported epsilon budget | noise added without an accountant | DP-SGD, DP-FedAvg, PATE, DP-FTRL | |
| A.privacy.secagg | Secure aggregation | A.privacy | | the aggregator provably cannot see individual updates | only the raw data is withheld | secure aggregation protocols, masked summation | |
| A.privacy.crypto | Encrypted computation | A.privacy | | computation proceeds on encrypted or secret-shared values | computation on plaintext with noise | homomorphic-encryption training, secure multiparty computation | speculative in mainstream ML venues |
| A.privacy.unlearn | Removal guarantee | A.privacy | | provides a stated guarantee that a specific example's influence is gone | reducing influence without a guarantee | SISA, certified removal, exact shard retraining | |
| A.agents | Agent multiplicity | | how many learning agents interact and with what alignment of interests | applies to interactive settings | a single predictor on a dataset | single, cooperative, competitive, mixed | single-valued |
| A.agents.single | Single agent | A.agents | | one policy interacts with a stationary environment | another learning agent is present | DQN, PPO on MuJoCo | |
| A.agents.coop | Cooperative multi-agent | A.agents | | several agents share one team reward | agents with opposing rewards | VDN, QMIX, MAPPO, COMA | |
| A.agents.comp | Competitive multi-agent | A.agents | | agents' rewards are opposed, approximately zero-sum | agents sharing a reward | self-play in Go, CFR for poker, NFSP, AlphaStar league | |
| A.agents.mixed | Mixed-motive multi-agent | A.agents | | rewards are neither identical nor strictly opposed | a purely cooperative or purely zero-sum setting | sequential social dilemmas, mixed-motive MARL, negotiation agents | |
| A.exec | Information available at execution | | what each agent can observe when acting, as opposed to when training | applies to multi-agent or partially observed control | single-agent fully observed control | centralized, CTDE, decentralized | single-valued |
| A.exec.central | Centralized execution | A.exec | | the acting policy conditions on global state at deployment | acting on local observations only | joint-action controllers, centralized planners | |
| A.exec.ctde | Centralized training, decentralized execution | A.exec | | global information is used only during training | global information is used while acting | MADDPG, MAPPO, QMIX, COMA | |
| A.exec.decen | Fully decentralized | A.exec | | no global information is used at any stage | a centralized critic during training | IQL, IPPO, independent learners | |
| A.outspace | Required output or action space | | what structure the method's output must have | applies to any method whose output type is constrained | a method indifferent to output type | discrete, continuous, hybrid, structured | single-valued |
| A.outspace.disc | Discrete | A.outspace | | requires a finite enumerable set of outputs or actions | requires a real-valued output | DQN, Q-learning, top-k sampling, classification losses | |
| A.outspace.cont | Continuous | A.outspace | | requires a real-valued, differentiable output or action space | requires enumerable actions | DDPG, TD3, SAC continuous, CEM-MPC, regression losses | |
| A.outspace.hybrid | Hybrid or parameterised | A.outspace | | requires a mixture of discrete choice and continuous parameters | a purely discrete or purely continuous space | parameterised-action RL, hybrid action DDPG | speculative: a thin literature |
| A.outspace.struct | Structured or sequential | A.outspace | | the output is a sequence, tree or graph scored jointly | the output is a single label or scalar | beam search, CRF Viterbi, structured SVM, constrained decoding | |
| A.determinism | Determinism of the procedure's output | | whether repeated application with fixed inputs gives the same result | applies to any procedure | none | deterministic, stochastic | single-valued |
| A.determinism.det | Deterministic | A.determinism | | same inputs and same parameters always produce the same output | any internal sampling | greedy decoding, beam search, k-means given an initialisation, PCA | |
| A.determinism.stoch | Stochastic | A.determinism | | the procedure samples internally, so outputs vary across seeds | the only randomness is in data ordering | top-p sampling, dropout, MCMC, Thompson sampling, diffusion sampling | |
| A.uncert | Treatment of estimate uncertainty | | what the procedure returns about its own uncertainty | applies to any estimator | a procedure that returns no estimate | point, interval, posterior, ensemble | single-valued |
| A.uncert.point | Point estimate | A.uncert | | returns a single parameter or prediction with no dispersion | returns a distribution or interval | SGD-trained networks, OLS point estimates, k-means centroids | |
| A.uncert.interval | Frequentist interval or test | A.uncert | | returns an interval or decision with a stated long-run error rate | returns a subjective distribution | bootstrap CIs, conformal intervals, confidence intervals, hypothesis tests | |
| A.uncert.post | Posterior distribution | A.uncert | | returns or samples an explicit posterior over parameters or functions | returns an empirical spread across runs | GP posteriors, MCMC samples, variational posteriors, SWAG, Bayesian NN | |
| A.uncert.ens | Empirical ensemble spread | A.uncert | | expresses uncertainty as disagreement among independently obtained predictors | expresses it through an explicit posterior | deep ensembles, bagging variance, MC dropout as approximation, snapshot ensembles | |
| A.guar | Formal guarantee claimed | | what kind of mathematical statement the method comes with | applies when the method is accompanied by a theorem | a purely empirical method | convergence, regret, consistency, coverage, certification, approximation, unbiasedness | multi-valued |
| A.guar.conv | Convergence guarantee | A.guar | | proves convergence to a stationary or optimal point under stated conditions | reports empirical convergence only | FISTA rates, SVRG rates, convex SGD rates, ADMM convergence | |
| A.guar.regret | Regret bound | A.guar | | bounds cumulative loss relative to the best fixed or dynamic comparator | bounds a one-shot estimation error | UCB1, EXP3, LinUCB, online mirror descent, Thompson-sampling regret | |
| A.guar.consist | Statistical consistency or asymptotic normality | A.guar | | proves the estimate converges to the truth as sample size grows | proves only an optimisation property | MLE consistency, doubly robust estimators, TMLE, double ML, M-estimation theory | the main guarantee in the causal branch |
| A.guar.cover | Finite-sample coverage | A.guar | | guarantees a stated coverage probability at finite sample size | guarantees only asymptotic coverage | split conformal prediction, conformal risk control, distribution-free intervals | |
| A.guar.cert | Certified robustness | A.guar | | proves invariance of the prediction within a stated input region | reports empirical attack resistance | randomised smoothing, IBP, CROWN, convex relaxations | |
| A.guar.approx | Approximation ratio | A.guar | | proves a bounded ratio to the optimum of a hard combinatorial objective | proves no bound on solution quality | greedy submodular 1-1/e, k-means++ expected ratio, k-center greedy | |
| A.guar.unbias | Unbiasedness | A.guar | | the estimator's expectation equals the target quantity | the estimator is biased but lower variance | REINFORCE score-function estimator, IPS, Horvitz-Thompson, unbiased MLMC | often the explicit selling point over a biased rival |
| A.param | Separable-model production | | what artifact, if any, survives the run | applies to every algorithm | none | parametric, instance-based, transductive | single-valued |
| A.param.param | Produces parameters | A.param | | emits a fixed-size parameter set runnable on new inputs without the training data | needs the training data at prediction time | SGD-trained networks, OLS coefficients, GMM parameters, random forests | the models dimension has an entry |
| A.param.inst | Keeps the data as the model | A.param | | prediction requires the stored training examples themselves | prediction uses only fitted parameters | k-NN, kernel SVM support vectors, KDE, LOESS, Gaussian processes | the legal "algorithm with no model" case |
| A.param.trans | Transductive, produces no reusable object | A.param | | produces an output only for the points it was given; new points need a refit | produces a map applicable to unseen points | t-SNE, spectral clustering, DBSCAN, label propagation, MDS, UMAP-without-transform | the second legal "no model" case |

---

## Worked examples

37 named methods, each placed on all four axes. Signal is written `source / form`. Where a cell is
`-`, the axis genuinely has no value for that method, and that is informative rather than missing.
Three cells could not be filled at all on the first pass; those forced `S.src.self.ident`,
`S.form.moment` and `R.out.predict` into the tables above and `A.deriv` from single- to multi-valued.

| method | lineage path | signal | role | attributes | note |
|---|---|---|---|---|---|
| PPO | L.pg > L.pg.ac > L.pg.trust | S.src.env.reward, S.src.self.own / S.form.return | R.fit.obj | A.regime.on, A.world.free, A.rltarget.ac, A.deriv.first, A.cadence.mini, A.agents.single, A.param.param | Resolves cleanly, and demonstrates the co-occurrence rule: PPO does not occupy R.fit.update at all, it delegates to Adam. Its on-policy sampling is implied by A.regime.on rather than by an R.exp.act entry, because PPO specifies no exploration rule of its own. |
| DQN | L.dp > L.td > L.td.q > L.dqn | S.src.env.reward, S.src.self.own / S.form.return | R.fit.obj, R.exp.act, R.exp.store | A.regime.off, A.world.free, A.rltarget.value, A.deriv.first, A.cadence.mini, A.outspace.disc, A.param.param | Awkward: DQN as published is a bundle of three slots (TD loss, epsilon-greedy, replay buffer), so "how many papers used prioritised replay" cannot be answered by rolling up the DQN node. Rainbow is worse, bundling six. The bundle is what the name denotes, so I did not split it; the cost is that role is not a clean partition for named bundles. |
| SAC | L.pg > L.maxent | S.src.env.reward, S.src.self.own / S.form.return, S.form.conf | R.fit.obj | A.regime.off, A.world.free, A.rltarget.ac, A.deriv.first, A.cadence.mini, A.outspace.cont, A.param.param | The entropy term is S.form.conf, which is the same value that TENT carries; that coincidence is real, not an artifact. |
| MuZero | L.mbrl > L.mbrl.search | S.src.env.reward, S.src.self.own / S.form.return, S.form.lik | R.fit.obj, R.exp.act, R.out.search | A.regime.off, A.world.learned, A.rltarget.ac, A.deriv.first, A.outspace.disc, A.determinism.stoch | Awkward in an instructive way: MCTS is simultaneously the acting policy, the inference-time output procedure, and the generator of the training target. Three roles on one node. |
| DPO | L.pref > L.pref.direct | S.src.ext.pref / S.form.rank, S.form.lik | R.fit.obj | A.regime.offline, A.deriv.first, A.cadence.mini, A.param.param | Lineage placement is a judgement call: the DPO paper derives its loss from the RLHF objective, which argues for a descent edge from L.pref.rm rather than a sibling relation. I made L.pref.direct a sibling because the thing DPO removes (the reward model) is the division principle of L.pref's children. |
| SimCLR | L.ssl.contrast | S.src.self.view / S.form.contrast | R.fit.obj, R.data.aug | A.deriv.first, A.cadence.mini, A.param.param | The augmentation pipeline is constitutive, not incidental, so R.data.aug is a real second role. |
| BYOL | L.ssl.selfdist | S.src.self.view, S.src.self.own / S.form.agree | R.fit.obj, R.data.aug | A.deriv.first, A.cadence.mini, A.param.param | BYOL and SimCLR agree on lineage depth, role and every attribute, and differ on exactly one value of one sub-facet. This pair is the evidence that signal had to be split into source and form. |
| MAE | L.ssl.mask > L.ssl.mask.vis | S.src.self.mask / S.form.recon | R.fit.obj | A.deriv.first, A.cadence.mini, A.param.param | |
| SPR | L.dqn.eff, L.ssl.jepa | S.src.env.reward, S.src.self.next, S.src.self.own / S.form.return, S.form.agree | R.fit.obj | A.regime.off, A.world.free, A.rltarget.value, A.deriv.first | Multi-parent across an RL family and an SSL family, with no contortion. A.world.free is a close call: SPR learns a latent transition model but never uses it for control, so the attribute is about control, not about whether dynamics are modelled anywhere. |
| ConSpec | L.ssl.contrast (applied in RL) | S.src.env.reward, S.src.self.view / S.form.contrast, S.form.return | R.fit.obj | A.regime.off, A.world.free, A.agents.single | The orthogonality test case. ConSpec and SPR share role and every attribute and differ only on S.form; any structure forcing a choice between an RL branch and a self-supervised branch would separate them for the wrong reason. Its lineage is weak though: it has no clean RL ancestor, and attaching it only to the contrastive family under-reports that it is an RL method. |
| DDPM | L.score | S.src.self.corrupt / S.form.score | R.fit.obj | A.deriv.first, A.cadence.mini, A.determinism.stoch, A.param.param | |
| DDIM | L.score > L.score.sample | S.src.none / S.form.none | R.out.decode | A.determinism.det, A.outspace.cont | The sharpest structural finding. DDIM is a genuine descendant of DDPM by the lineage rule, yet it inherits neither its parent's role nor its parent's signal. Any design that made role the top-level division of lineage would have had to cut this edge. |
| WGAN-GP | L.gan > L.gan.loss | S.src.self.struct / S.form.game, S.form.div | R.fit.obj | A.deriv.first, A.determinism.stoch, A.param.param | The gradient penalty is also an R.fit.obj regulariser from L.reg.geom, so the entry has a second weak lineage parent I did not record. |
| VAE | L.vi > L.vae | S.src.self.ident / S.form.bound, S.form.recon | R.fit.obj, R.fit.est | A.deriv.first, A.cadence.mini, A.uncert.post, A.param.param | Forced the addition of S.src.self.ident: the hypothesis had values for masked and corrupted inputs but none for plain self-reconstruction. R.fit.est is the reparameterisation trick, which is separately named and separately citable. |
| AdamW | L.sgd > L.adapt | S.src.none / S.form.none | R.fit.update, R.fit.obj | A.deriv.first, A.cadence.mini | Slightly awkward and worth it: AdamW's entire contribution is moving the weight-decay term out of the objective and into the update rule, so it touches two slots precisely because it relocates something between them. |
| L-BFGS | L.precond > L.precond.quasi | S.src.none / S.form.none | R.fit.update | A.deriv.second, A.cadence.full, A.determinism.det, A.guar.conv | |
| XGBoost | L.boost | S.src.ext.human / S.form.lik, S.form.spars | R.fit.obj, R.fit.update, R.fit.est | A.deriv.second, A.deriv.comb, A.cadence.full, A.param.param, A.uncert.point | Awkward, and this is tension one. Classical methods are whole-run algorithms: XGBoost specifies the objective, the second-order step, the greedy split search and the model class at once. Deep-learning entries are slot-sized; classical entries are not. Role is multi-valued so this encodes, but three roles on one node means role roll-ups over-count classical papers relative to deep ones. |
| k-NN | L.inst | S.src.ext.human / S.form.none | R.out.predict | A.param.inst, A.determinism.det, A.uncert.point | Forced the addition of R.out.predict. The hypothesis's role list silently assumed a model exists whose forward pass produces the output, so a nonparametric prediction rule had nowhere to go even though the brief explicitly calls it a legal state. |
| t-SNE | L.dimred > L.dimred.dist | S.src.self.struct / S.form.dist | R.data.repr, R.out.explain | A.param.trans, A.deriv.first, A.cadence.full, A.determinism.stoch | Awkward: whether t-SNE is representation construction or explanation production depends on what the paper does next, which is a property of its use, exactly what role is supposed to exclude. I recorded both rather than choose, but the honest reading is that role has a soft spot here. |
| EM for a Gaussian mixture | L.em, L.clust.model | S.src.self.struct / S.form.lik, S.form.bound | R.fit.est, R.fit.update | A.deriv.closed, A.cadence.full, A.uncert.point, A.param.param, A.guar.conv | Shows why R.fit.est had to exist: without it, EM would land on R.fit.update alone and look like a sibling of Adam, which the co-occurrence test forbids only weakly here since they genuinely never co-occur. |
| NUTS | L.mcmc > L.mcmc.grad | S.src.self.struct / S.form.post | R.fit.est | A.deriv.sample, A.deriv.first, A.cadence.full, A.uncert.post, A.determinism.stoch, A.param.trans | Forced A.deriv to become multi-valued: HMC is simultaneously a sampler and a gradient-informed method, and collapsing it to one value loses whichever half you drop. A.param.trans is a stretch: MCMC produces samples, which are neither parameters nor stored training data. |
| TMLE | L.causal > L.causal.adjust | S.src.design.adjust, S.src.ext.human / S.form.moment, S.form.lik | R.fit.est | A.deriv.closed, A.cadence.full, A.guar.consist, A.guar.unbias, A.uncert.interval, A.param.param | Forced the addition of S.form.moment. Every estimating-equation estimator in statistics was unrepresentable under the original form list, which only had loss-minimisation shapes. This was the single largest blind spot the examples exposed. |
| Doubly robust OPE | L.bandit.ope, L.causal.adjust | S.src.env.reward, S.src.design.adjust / S.form.moment | R.eval, R.fit.est | A.regime.offline, A.guar.unbias, A.uncert.interval | A genuinely multi-parent entry: the same estimator is published in the bandit literature and in the causal literature. Its primary role is evaluation, which is the slot I am least sure belongs in this dimension. |
| LoRA | L.peft > L.peft.lowrank | S.src.none / S.form.none | R.fit.scope | A.param.param | Textbook case of the co-occurrence rule: LoRA + instruction tuning + AdamW is three algorithms in three slots in one run, and LoRA carries no signal of its own because it constrains which parameters move, not what they move toward. |
| Instruction tuning | L.sft > L.sft.inst | S.src.ext.human or S.src.ext.model / S.form.lik | R.fit.obj, R.data.select | A.deriv.first, A.cadence.mini, A.param.param | The signal source genuinely varies by paper (human-written vs model-generated instruction data), which is a property of the instance, not of the method. Multi-valued signal absorbs this, but it means the signal of an SFT paper must be read from the data description, not from the method name. |
| FixMatch | L.semi > L.semi.self, L.reg.consist | S.src.self.own, S.src.self.view / S.form.conf, S.form.lik | R.data.label, R.fit.obj, R.data.aug | A.deriv.first, A.cadence.mini | Three roles and two lineage parents, all of them real. The confidence threshold is S.form.conf, the strong-augmentation branch is R.data.aug, and the pseudo-label is R.data.label. |
| Knowledge distillation | L.kd > L.kd.logit | S.src.ext.model / S.form.div | R.fit.obj | A.deriv.first, A.cadence.mini, A.param.param | The entry that killed the "compression" role. KD's slot is the objective; compression is why people reach for it. Grouping it with pruning would have implied they are alternatives, when in fact they compose. |
| GPTQ | L.quant > L.quant.ptq | S.src.self.struct / S.form.recon | R.rewrite.precision | A.deriv.second, A.cadence.full, A.determinism.det | Not S.src.none: GPTQ fits something, namely a layerwise reconstruction on a calibration set, using second-order information. Treating all compression as signal-free would have been wrong. |
| FedAvg | L.fed > L.fed.avg | S.src.none / S.form.none | R.coord.replicate, R.coord.agg | A.topology.feddev, A.datalocality.local, A.cadence.mini, A.deriv.first | Federated split into topology plus data locality here: FedAvg's algorithmic content is local-steps-then-average, which it shares with local SGD; the data-locality constraint is what makes it federated. |
| ZeRO-3 / FSDP | L.shard > L.shard.opt | S.src.none / S.form.none | R.coord.partition, R.coord.mem | A.topology.csync, A.datalocality.pooled | Mathematically a no-op on the update, so it carries no signal and no attributes about learning. It earns its place because it is named, it is reported, and its cost appears in the run. |
| CutMix | L.aug > L.aug.mix | S.src.ext.human / S.form.none | R.data.aug, R.fit.obj | A.determinism.stoch | Slightly awkward: CutMix also rewrites the label, so it touches the objective's target even though it is a data-preparation method. Mixing methods are the only augmentations that do this. |
| BPE | L.tok > L.tok.bpe | S.src.self.struct / S.form.none | R.data.repr | A.deriv.comb, A.cadence.full, A.determinism.det, A.param.param | Awkward: BPE is fitted to a corpus but minimises no criterion, so it has a source and no form. It also produces a separable artifact (the vocabulary), which under the models dimension's own rule arguably makes a tokenizer a model. I left it here and flagged it. |
| Nucleus sampling | L.dec > L.dec.sample | S.src.none / S.form.none | R.out.decode | A.determinism.stoch, A.outspace.disc | |
| Beam search | L.dec > L.dec.beam | S.src.none / S.form.none | R.out.decode | A.deriv.comb, A.determinism.det, A.outspace.struct | Resolves cleanly, and confirms the brief's claim that it belongs: it decides which token is selected, so it decides what the model says, and it co-occurs with an objective rather than competing with one. |
| Speculative decoding | L.dec > L.dec.spec | S.src.none / S.form.none | R.out.decode | A.determinism.stoch, A.outspace.disc | The run contains two models and one algorithm, which the entity model handles but which makes "which model did this paper use" ambiguous for the draft model. |
| Tree of Thoughts | L.tts > L.tts.tree | S.src.none / S.form.none | R.out.search | A.deriv.comb, A.determinism.stoch, A.outspace.struct | Admissible because it is named. The surrounding gradient here is steep: ToT, ReAct and self-consistency are in, while "we prompted it to think step by step" without naming CoT is out, and in practice papers sit on both sides of that line in the same paragraph. |
| TENT | L.tta > L.tta.ent | S.src.self.own / S.form.conf | R.adapt, R.fit.scope | A.cadence.mini, A.deriv.first, A.param.param | R.adapt and R.fit overlap by construction. TENT passes the property-vs-use test because adapting at test time is definitional for it, but the overlap means a role roll-up double-counts TTA papers under "parameter update" unless R.adapt is excluded explicitly. |
| Split conformal prediction | L.calib > L.calib.conf | S.src.ext.human / S.form.cover | R.out.calib | A.guar.cover, A.uncert.interval, A.determinism.det, A.param.param | The clearest case that A.guar earns its place: conformal's entire claim is a guarantee, and without that family it would look like an unremarkable post-hoc rescaling. |
| Thompson sampling | L.bandit > L.bandit.stoch, L.explore.post | S.src.env.reward / S.form.post | R.exp.act | A.regime.on, A.uncert.post, A.determinism.stoch, A.guar.regret, A.outspace.disc | Multi-parent between the bandit family and the exploration family is correct and cheap, and it is the entry that justifies keeping R.exp.act separate from R.fit.obj. |

---

## Tensions

Ordered roughly by how much they should change the design before phase 2.

**1. Granularity mismatch between classical and deep entries (top tension).** Deep-learning methods are
slot-sized: PPO is an objective, Adam is an update rule, LoRA is a scope. Classical methods are
whole-run: XGBoost specifies an objective, a second-order step, a greedy split search and a model class
under one name; EM specifies an estimator and an update; k-means specifies an objective, an update and
a prediction rule. So role multiplicity is systematically higher for classical entries, and a role
roll-up ("what proportion of papers contain an R.fit.update entry") over-counts the classical branch
and under-counts the deep one. Multi-valued role records this correctly but does not make the counts
comparable. Three options: accept it and always report role counts per-paper rather than per-entry;
split the classical bundles into component nodes, which invents names the literature does not use; or
add a `granularity` marker (`slot` vs `bundle`) and report separately. I lean to the third, but did not
add it because I could not test it without seeing how often bundles are actually cited as units.

**2. `attributes` is not one axis; it is at least two (top tension).** Some families are universal
(`A.deriv`, `A.cadence`, `A.param`, `A.determinism`, `A.uncert`, `A.guar`): every algorithm either has
a value or demonstrably does not apply, and the "does not apply" is itself informative. Others
(`A.regime`, `A.world`, `A.rltarget`, `A.hier`, `A.exec`, `A.agents`) are empty for everything outside
sequential decision-making, which is to say they are a *facet pack scoped to one lineage region*, not
peers of the universal families. This matters for aggregation: "what proportion of papers are
on-policy" has an ambiguous denominator (all papers, or RL papers). I kept them as declared families
because the brief forbids dropping an axis for sparsity, but I believe the right structure marks each
family with a scope condition — "defined when the paper has an entry under L.dp, L.pg, L.bandit or
L.marl" — and that this is a change to the axis hypothesis, not a cosmetic note. Without it,
`attributes` will look like a mostly-empty table and will be mistaken for a failed axis.

**3. The naming boundary is the real scope rule and it is not sharp (top tension).** The brief bounds
the dimension by naming: `CutMix` is in, "we normalised the images" is out. But z-scoring, early
stopping, gradient clipping, cosine annealing and random cropping all *have* names and are almost never
cited as methods — they are reported as settings. Meanwhile chain-of-thought, ReAct and self-consistency
have names and are cited as methods, while the same procedures described without the name are out. So
the boundary partly tracks citation practice rather than the procedure. I resolved this by admitting
anything with a conventional name and writing tests that do not depend on whether the paper cites it,
which means nodes like `L.sched.time` and `L.gradproc.clip` exist and may be heavily used but rarely
*reported*. Phase 2 should expect systematic under-reporting precisely at the highest-frequency nodes,
and the right response is to treat absence at those nodes as uninformative, not as evidence of
non-use. I would rather have this stated now than discovered as a surprising frequency later.

**4. Does evaluation belong?** The participant rule covers "preparing the data, producing or adapting
the learned object, or using it to produce outputs". Cross-validation, bootstrap confidence intervals,
permutation tests, FDR control and LLM-as-judge scoring are none of those three, yet they are named
procedures a run executes, they appear in `runs[]`-style cost, and in statistics they are a large part
of what a paper's method section contains. I included `R.eval`, `L.boot.cv` and `L.test` and flagged
them rather than quietly dropping a branch that the "classical statistics needs a non-afterthought
home" instruction seems to want. If the answer is that evaluation is out of scope, three nodes and one
role value come out cleanly; if it is in, the participant rule needs a fourth clause. This should be
decided before annotation, not during.

**5. Lineage deliberately has no top, and that costs one kind of roll-up.** Every candidate top-level
divider of lineage is already a facet, and any of them breaks on a real edge (DDIM descends from DDPM
across a role change; GAIL descends from GAN across a signal change). So lineage is a forest of 94
roots. The cost: "what proportion of papers used a reinforcement-learning algorithm" is not a lineage
roll-up any more; it is answered by `S.src.env.*` plus the RL-scoped attribute families. I believe this
is correct, but it is a real behavioural change from how people expect to query a taxonomy, and someone
will ask for an "RL" node. If one is added it should be declared a *view*, not a parent.

**6. The hypothesis says signal "unions up the chain"; the examples say it must not, always.** Signal
unioning up lineage would give DDIM the signal of DDPM, and `L.score.sample` the signal of `L.score`,
which is wrong: the sampler has no training target at all. The same happens at `L.aug.policy` (searched
policies inherit no signal from augmentation) and `L.quant.qat` vs `L.quant.ptq`. My rule is that signal
is recorded per node and does not inherit across an edge where role changes. That is a weaker and more
annotation-expensive rule than the hypothesis, and I am not fully confident in it; the alternative is to
forbid lineage edges that cross roles, which would mean cutting the DDPM-to-DDIM edge, and that seems
clearly worse.

**7. The architecture/algorithm boundary is inconsistent on its face.** I included dropout, parameter
initialisation and sparse-expert routing; I excluded batch norm, layer norm and residual connections as
model architecture. The stated reason is that dropout, init and routing are *procedures that run*, while
normalisation layers are *parts of the computed function* — but dropout is also a layer, and init is
also a property of the model as shipped. StyleGAN sits on the line in the other direction: its lineage is
a training-procedure lineage, but most of its content is architecture. This needs a joint ruling with
the models dimension, because whichever way it goes, both dimensions must go the same way or some
entities will be in both and some in neither.

**8. A tokenizer may be a model.** BPE produces a fixed, separable, independently runnable artifact
fitted from data, which satisfies the models dimension's admission rule as I understand it. I put
tokenization in algorithms because the *induction procedure* is the named thing, but if vocabularies
are models, then `L.tok` entries are algorithms producing models and the vocabulary should be an entity
in `models[]`. The same question applies to `L.emb` (word2vec), learned optimisers (the brief already
rules these are models), NAS outputs and dataset distillation outputs.

**9. Systems procedures: where does the dimension stop?** ZeRO, FSDP, pipeline parallelism, gradient
checkpointing and mixed precision are named procedures a run executes, and they change nothing about
the function being learned. I admitted them because they are named, reported, and their cost is exactly
what `runs[]` records. But by the same argument FlashAttention, fused kernels, paged KV caches and
continuous batching are also named procedures a run executes, and I excluded them without a principled
rule. The best rule I can state is "admit a systems procedure when it changes what the run *could*
compute at all (sharding makes a model trainable that otherwise is not), exclude it when it only changes
how fast the same computation runs" — but that rule puts gradient checkpointing in and FlashAttention
out, and those two are hard to distinguish honestly.

**10. Signal is sometimes a property of the instance, not the algorithm.** Instruction tuning carries
`S.src.ext.human` or `S.src.ext.model` depending on whose data was used; distillation's source is the
teacher, but self-distillation's is the model itself; RLHF's reward may be human, AI or verifier. The
axis test says two entities should be able to differ on an axis while agreeing on everything else —
here one entity differs on the axis from itself across papers. Multi-valued signal absorbs this, but it
means signal must be read from the data description rather than the method name for a specific set of
nodes. Those nodes should probably be marked.

**11. Lineage currently carries two kinds of edge.** `DQN -> Rainbow` is descent as framed by the
Rainbow paper. `ConSpec -> L.ssl.contrast` is "instantiates a technique family in a new setting", which
is not the same relation, and `SPR -> L.ssl.jepa` is the same kind. Both are multi-parent attachments I
made because the alternative was leaving the entry with a misleadingly narrow ancestry. If the dimension
keeps one edge type, the aggregation "papers in the contrastive family" will silently include RL papers
that nobody would describe that way. I recommend two edge types, `derived-from` and `instantiates`, with
roll-ups defaulting to the former.

**12. Absence versus not-applicable.** For `A.outspace` I used absence to mean "the method constrains
nothing", but absence also means "not annotated". The same ambiguity hits every single-valued family
where I chose not to mint an explicit `n.a.` node. This is cheap to fix and should be fixed before
annotation: either mint `n.a.` values or carry an explicit applicability predicate per family.

**13. Named bundles cannot be decomposed by the ontology alone.** DQN is replay plus epsilon-greedy plus
a TD loss; Rainbow is six components; FixMatch is three. A paper saying "we used Rainbow" has used
prioritised replay, but the entry does not say so, and inferring it requires knowing the bundle's
composition rather than its ancestry. If "what proportion of papers used prioritised replay" matters,
bundles need a declared component list, which is a fifth structure (composition) and not one of the four
axes. I did not add it because I am not sure the question is asked often enough to justify it.

**14. On the four-axis hypothesis overall.** I think it is right, with the two modifications made above
(signal splits into source and form; attributes needs per-family scope). The strongest evidence for it is
negative: every place I was tempted to make a tree level — RL vs SSL, supervised vs unsupervised,
train-time vs test-time, efficient vs full finetuning — the orthogonality test killed it within one or
two examples. The weakest part is `attributes`, not because it is sparse but because it is heterogeneous;
if anything is going to be re-cut after phase 2, it is that axis.

**15. Known speculative or thin nodes.** `L.mcmc.nested`, `L.symreg`, `L.lowrankc`, `L.synth.cf`,
`A.privacy.crypto`, `A.outspace.hybrid`, `S.src.theory.logic`, `L.meta.black`, `L.automl` and
`L.quant.kv` are nodes I believe exist in the field but whose users I cannot name from an ML-venue
corpus specifically. `L.causal.*`, `L.seq.ts`, `L.test` and `L.rec.*` I am confident exist in the field
and much less confident appear in an ML-paper corpus at any volume — which is precisely the thing
phase 1 must not try to guess.
