# Categorization eval -- models / dev

- base: `v0` (`568c0990c2fa`)
- model: `gpt-5.6-sol`  run: `b0f3d0933db6`
- items: 200 (181 decided, 18 abstained, 0 failed to apply)
- 28 items have no corpus evidence; 22 leave ablation residue

## Primary -- blind pairwise win rate

- **W = 0.627**  (95% CI 0.588-0.674, n=181)
- lost 21 / tied 93 / won 67  -- 0.5 is the analytic ceiling
- W@coverage=0.85: 0.624
- excluding the 22 residue items: W = 0.638 (n=159)

| stratum | W |
|---|---|
| anchoring=cold | 0.652 |
| anchoring=parent | 0.582 |
| anchoring=some | 0.630 |
| evidence=no | 0.625 |
| evidence=yes | 0.627 |
| residue=no | 0.638 |
| residue=yes | 0.545 |

## Judge guardrails

- judge: anthropic/claude-opus-5
- n_pairs: 101
- pro_agent_rate: 0.663
- swap_check_n: 101
- order_swap_consistency: 0.851

## Hierarchy-aware agreement

- n: 181
- precision: 0.805
- recall: 0.744
- f1: 0.759
- same_lineage_rate: 0.746
- **off_lineage_lca_depth**:
  - 0: 18
  - 1: 24
  - 2: 2
  - 3: 2

## Agreement with the legacy tree

- n: 181
- rate: 0.862
- cohen_kappa: 0.803
- macro_recall: 0.805
- **majority_baseline**:
  - rate: 0.448
  - macro_recall: 0.000
- **levenshtein_baseline**:
  - rate: 0.707
  - macro_recall: 0.666

## Distributional shape

- **agent_shares**:
  - Other: 0.514
  - convolutional neural network: 0.083
  - diffusion model: 0.039
  - generative flow networks: 0.028
  - graph neural network: 0.088
  - multi layer perceptron: 0.017
  - recurrent neural network: 0.033
  - transformer: 0.199
- **reference_shares**:
  - Other: 0.448
  - convolutional neural network: 0.083
  - diffusion model: 0.039
  - generative flow networks: 0.044
  - graph neural network: 0.088
  - multi layer perceptron: 0.022
  - recurrent neural network: 0.022
  - transformer: 0.254
- spearman: 0.910
- top5_overlap: 0.800
- total_variation: 0.077

## Harmlessness

- schema_valid: 1.000
- apply_success: 1.000

## Self-consistency

- k: 3
- fleiss_kappa: 0.936
- triple_agreement: 0.930
- payload_hash_stable: True
- exceeds_legacy_agreement: True

## Reference-free probes

- **noop**:
  - n: 100
  - noop_rate: 0.850
  - destructive: 0
- **policy**:
  - n: 56
  - conformance: 0.786
  - **per_kind**:
    - **child**:
      - n: 20
      - rate: 0.950
    - **surface**:
      - n: 36
      - rate: 0.694
  - misses: vgg13 (child, got created), gflownets (surface, got mapped), sac (surface, got mapped), mlp (surface, got mapped), iql (surface, got abstained), iql (surface, got abstained), dqn (surface, got mapped), gflownet (surface, got mapped) (+4 more)
- **ambiguity**:
  - n_should_abstain: 38
  - n_should_resolve: 40
  - recall_abstain: 0.974
  - false_abstain: 0.000
  - youden_j: 0.974
  - abstain_no_grounding_only: 0.575
- **ignore**:
  - n_positive: 45
  - n_negative: 60
  - precision: 1.000
  - recall: 0.733

## Gate

| clause | value | | threshold | verdict |
|---|---|---|---|---|
| 1. LB95(W) | 0.588 | >= | 0.450 | PASS -- W=0.627 (l=21, t=93, g=67) |
| 1b. W@coverage=0.85 | 0.624 | >= | 0.450 | PASS |
| 1c. judge order-swap consistency | 0.851 | >= | 0.800 | PASS -- below this the judge reads position, not content, and W is void |
| 2a. cut agreement | 0.862 | >= | 0.807 | PASS -- floor = max(0.70, levenshtein 0.707 + 0.10) |
| 2b. Cohen kappa | 0.803 | >= | 0.550 | PASS |
| 2c. macro-recall (non-Other) | 0.805 | >= | 0.766 | PASS -- floor = max(0.60, levenshtein 0.666 + 0.10) |
| 2d. Spearman rho | 0.910 | >= | 0.900 | PASS |
| 2e. top-5 unchanged | 0.800 | >= | 1.000 | FAIL |
| 3a. schema valid | 1.000 | >= | 1.000 | PASS |
| 3b. apply success | 1.000 | >= | 0.990 | PASS |
| 3c. no-op control | 0.850 | >= | 0.950 | FAIL |
| 3d. destructive ops outside candidates | 0.000 | <= | 0.000 | PASS |
| 4a. triple agreement | 0.930 | >= | 0.750 | PASS |
| 4b. self-consistency > legacy agreement | 1.000 | >= | 1.000 | PASS |
| 5a. Youden J | 0.974 | >= | 0.700 | PASS |
| 5b. coverage | 0.905 | >= | 0.850 | PASS |
| 5c. policy conformance | 0.786 | >= | 0.900 | FAIL |
| 6a. mark_ignore precision | 1.000 | >= | 0.800 | PASS |
| 6b. mark_ignore recall | 0.733 | >= | 0.600 | PASS |

**Verdict: FAIL** (16/19 clauses)
