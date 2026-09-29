# Categorization eval -- models / dev

- base: `v0` (`568c0990c2fa`)
- model: `gpt-5.6-sol`  run: `8a53a986fed1`
- items: 200 (180 decided, 18 abstained, 0 failed to apply)
- 28 items have no corpus evidence; 22 leave ablation residue

## Primary -- blind pairwise win rate

- **W = 0.606**  (95% CI 0.567-0.650, n=180)
- lost 21 / tied 100 / won 59  -- 0.5 is the analytic ceiling
- W@coverage=0.85: 0.618
- excluding the 22 residue items: W = 0.614 (n=158)

| stratum | W |
|---|---|
| anchoring=cold | 0.673 |
| anchoring=parent | 0.531 |
| anchoring=some | 0.562 |
| evidence=no | 0.500 |
| evidence=yes | 0.614 |
| residue=no | 0.614 |
| residue=yes | 0.545 |

## Judge guardrails

- judge: anthropic/claude-opus-5
- n_pairs: 96
- pro_agent_rate: 0.615
- swap_check_n: 20
- order_swap_consistency: 0.750

## Hierarchy-aware agreement

- n: 180
- precision: 0.795
- recall: 0.750
- f1: 0.760
- same_lineage_rate: 0.750
- **off_lineage_lca_depth**:
  - 0: 22
  - 1: 20
  - 2: 1
  - 3: 2

## Agreement with the legacy tree

- n: 180
- rate: 0.878
- cohen_kappa: 0.825
- macro_recall: 0.855
- **majority_baseline**:
  - rate: 0.467
  - macro_recall: 0.000
- **levenshtein_baseline**:
  - rate: 0.711
  - macro_recall: 0.673

## Distributional shape

- **agent_shares**:
  - (ignore): 0.006
  - Other: 0.500
  - convolutional neural network: 0.078
  - diffusion model: 0.039
  - generative flow networks: 0.022
  - graph neural network: 0.100
  - multi layer perceptron: 0.022
  - recurrent neural network: 0.028
  - transformer: 0.206
- **reference_shares**:
  - Other: 0.467
  - convolutional neural network: 0.078
  - diffusion model: 0.039
  - generative flow networks: 0.039
  - graph neural network: 0.089
  - multi layer perceptron: 0.022
  - recurrent neural network: 0.022
  - transformer: 0.244
- spearman: 0.945
- top5_overlap: 1.000
- total_variation: 0.056

## Harmlessness

- schema_valid: 1.000
- apply_success: 1.000

## Reference-free probes

- **noop**:
  - n: 100
  - noop_rate: 0.690
  - destructive: 0
- **policy**:
  - n: 96
  - conformance: 0.583
  - **per_kind**:
    - **child**:
      - n: 36
      - rate: 0.917
    - **surface**:
      - n: 60
      - rate: 0.383
  - misses: gpt40613 (child, got abstained), gpt40125 (child, got abstained), vgg13 (child, got created), ac (surface, got abstained), bib (surface, got abstained), bst (surface, got abstained), cbft (surface, got abstained), cca (surface, got abstained) (+32 more)
- **ambiguity**:
  - n_should_abstain: 38
  - n_should_resolve: 40
  - recall_abstain: 0.974
  - false_abstain: 0.000
  - youden_j: 0.974
  - abstain_no_grounding_only: 0.650
- **ignore**:
  - n_positive: 60
  - n_negative: 60
  - precision: 0.958
  - recall: 0.383

## Gate

| clause | value | | threshold | verdict |
|---|---|---|---|---|
| 1. LB95(W) | 0.567 | >= | 0.450 | PASS -- W=0.606 (l=21, t=100, g=59) |
| 1b. W@coverage=0.85 | 0.618 | >= | 0.450 | PASS |
| 1c. judge order-swap consistency | 0.750 | >= | 0.800 | FAIL -- below this the judge reads position, not content, and W is void |
| 2a. cut agreement | 0.878 | >= | 0.811 | PASS -- floor = max(0.70, levenshtein 0.711 + 0.10) |
| 2b. Cohen kappa | 0.825 | >= | 0.550 | PASS |
| 2c. macro-recall (non-Other) | 0.855 | >= | 0.773 | PASS -- floor = max(0.60, levenshtein 0.673 + 0.10) |
| 2d. Spearman rho | 0.945 | >= | 0.900 | PASS |
| 2e. top-5 unchanged | 1.000 | >= | 1.000 | PASS |
| 3a. schema valid | 1.000 | >= | 1.000 | PASS |
| 3b. apply success | 1.000 | >= | 0.990 | PASS |
| 3c. no-op control | 0.690 | >= | 0.950 | FAIL |
| 3d. destructive ops outside candidates | 0.000 | <= | 0.000 | PASS |
| 4a. triple agreement | n/a | >= | 0.750 | FAIL -- (not measured) |
| 4b. self-consistency > legacy agreement | n/a | >= | 1.000 | FAIL -- (not measured) |
| 5a. Youden J | 0.974 | >= | 0.700 | PASS |
| 5b. coverage | 0.900 | >= | 0.850 | PASS |
| 5c. policy conformance | 0.583 | >= | 0.900 | FAIL |
| 6a. mark_ignore precision | 0.958 | >= | 0.800 | PASS |
| 6b. mark_ignore recall | 0.383 | >= | 0.600 | FAIL |

**Verdict: FAIL** (13/19 clauses)
