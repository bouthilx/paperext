# Categorization eval -- models / dev

- base: `v0` (`568c0990c2fa`)
- model: `gpt-5.6-sol`  run: `a204fb891c18`
- items: 1 (0 decided, 1 abstained, 0 failed to apply)
- 1 items have no corpus evidence; 0 leave ablation residue

## Primary -- blind pairwise win rate

_not adjudicated_

## Agreement with the legacy tree

- n: 0
- rate: n/a
- cohen_kappa: n/a
- macro_recall: n/a
- **majority_baseline**:
  - rate: n/a
  - macro_recall: n/a

## Distributional shape

- spearman: n/a
- top5_overlap: n/a
- total_variation: 0.000

## Harmlessness

- schema_valid: 1.000
- apply_success: 1.000

## Reference-free probes

- **noop**:
  - n: 100
  - noop_rate: 0.970
  - destructive: 0
- **policy**:
  - n: 56
  - conformance: 0.750
  - **per_kind**:
    - **child**:
      - n: 20
      - rate: 0.950
    - **surface**:
      - n: 36
      - rate: 0.639
  - misses: vgg13 (child, got created), gflownets (surface, got mapped), sac (surface, got mapped), mlp (surface, got mapped), iql (surface, got abstained), graphconvolutionalnetwork (surface, got mapped), iql (surface, got abstained), dqn (surface, got mapped) (+6 more)
- **ambiguity**:
  - n_should_abstain: 38
  - n_should_resolve: 40
  - recall_abstain: 0.974
  - false_abstain: 0.025
  - youden_j: 0.949
  - abstain_no_grounding_only: 0.550
- **ignore**:
  - n_positive: 45
  - n_negative: 60
  - precision: 1.000
  - recall: 0.689

## Gate

| clause | value | | threshold | verdict |
|---|---|---|---|---|
| 1. LB95(W) | n/a | >= | 0.450 | FAIL -- (not measured) |
| 1b. W@coverage=0.85 | n/a | >= | 0.450 | FAIL -- the agent never reaches that coverage (not measured) |
| 1c. judge order-swap consistency | n/a | >= | 0.800 | FAIL -- below this the judge reads position, not content, and W is void (not measured) |
| 2a. cut agreement | n/a | >= | 0.700 | FAIL -- no levenshtein baseline computed (not measured) |
| 2b. Cohen kappa | n/a | >= | 0.550 | FAIL -- (not measured) |
| 2c. macro-recall (non-Other) | n/a | >= | 0.600 | FAIL -- floor = 0.60 (baseline not measured) (not measured) |
| 2d. Spearman rho | n/a | >= | 0.900 | FAIL -- (not measured) |
| 3a. schema valid | 1.000 | >= | 1.000 | PASS |
| 3b. apply success | 1.000 | >= | 0.990 | PASS |
| 3c. no-op control | 0.970 | >= | 0.950 | PASS |
| 3d. destructive ops outside candidates | 0.000 | <= | 0.000 | PASS |
| 4a. triple agreement | n/a | >= | 0.750 | FAIL -- (not measured) |
| 4b. self-consistency > legacy agreement | n/a | >= | 1.000 | FAIL -- (not measured) |
| 5a. Youden J | 0.949 | >= | 0.700 | PASS |
| 5b. coverage | 0.000 | >= | 0.850 | FAIL |
| 5c. policy conformance | 0.750 | >= | 0.900 | FAIL |
| 6a. mark_ignore precision | 1.000 | >= | 0.800 | PASS |
| 6b. mark_ignore recall | 0.689 | >= | 0.600 | PASS |

**Verdict: FAIL** (7/18 clauses)
