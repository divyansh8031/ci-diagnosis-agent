# Error analysis

The verified GitHub Actions experiment produced **1,800 policy-case records** (5 seeds × 120 cases × 3 policies). The five representative failures below come from the generated `five_error_cases.json` artifact rather than hand-written examples.

## Case 1 — P2 unknown/other → test-data/state

- Seed/case: 2026 / 2026-28
- True cause: `other`
- Prediction: `test_data_state`
- Final confidence: 68.56%
- Actions: `rerun > search_history > check_dependency > local_reproduction > inspect_code > check_db`
- Observations: rerun FAIL; history FAIL; dependency FAIL; local reproduction FAIL; code inspection FAIL; DB PASS
- Diagnostic cost: 9
- Consequence cost: 90
- Total decision cost: 99
- Escalated: yes
- Failure mechanism: the residual `other` state is weakly represented by the evidence model, so a single positive DB signal can dominate several non-diagnostic negatives.
- Design response: make state evidence more discriminative against dependency/infrastructure/flaky worlds and explicitly test the unknown-state failure mode.

## Case 2 — P3 unknown/other → code regression

- Seed/case: 2026 / 2026-16
- True cause: `other`
- Prediction: `code_regression`
- Final confidence: 50.00%
- Actions: `search_history > check_dependency`
- Observations: history FAIL; dependency FAIL
- Diagnostic cost: 2
- Consequence cost: 90
- Total decision cost: 92
- Escalated: yes
- Failure mechanism: the residual class is not sufficiently separated by the current evidence model. The derived threshold allows an early terminal decision before the agent has evidence that the world belongs to one of the modeled concrete causes.
- Design response: retain `other` as an explicit state and add calibration/abstention evaluation rather than forcing a concrete diagnosis whenever the posterior is diffuse.

## Case 3 — P0 no-evidence baseline → code regression

- Seed/case: 2026 / 2026-16
- True cause: `other`
- Prediction: `code_regression`
- Final confidence: 40.00% prior
- Actions: none
- Diagnostic cost: 0
- Consequence cost: 90
- Total decision cost: 90
- Failure mechanism: this is the expected weakness of the trivial baseline: it cannot adapt to evidence or the unknown state.
- Design response: keep the failure. It demonstrates why P0 is required by the cohort rather than hiding the baseline.

## Case 4 — P2 test-data/state → CI infrastructure

- Seed/case: 2026 / 2026-77
- True cause: `test_data_state`
- Prediction: `ci_infrastructure`
- Final confidence: 51.39%
- Actions: all six diagnostic actions
- Observations: rerun FAIL; history FAIL; dependency FAIL; local reproduction FAIL; code inspection FAIL; DB FAIL
- Diagnostic cost: 9
- Consequence cost: 80
- Total decision cost: 89
- Escalated: yes
- Failure mechanism: when every evidence source is negative, the remaining hypotheses are redistributed by the model rather than decisively identified.
- Design response: add a stronger explicit infrastructure-health observation and test whether negative-evidence patterns are calibrated rather than treating every binary negative as equally informative.

## Case 5 — P2 code regression → CI infrastructure

- Seed/case: 2027 / 2027-37
- True cause: `code_regression`
- Prediction: `ci_infrastructure`
- Final confidence: 51.39%
- Actions: all six diagnostic actions
- Observations: all six actions FAIL
- Diagnostic cost: 9
- Consequence cost: 80
- Total decision cost: 89
- Escalated: yes
- Failure mechanism: the model has little positive evidence for any cause, so the final posterior remains driven by the structure of the likelihood table.
- Design response: this supports adding richer non-binary evidence and calibration before treating a low-confidence terminal classification as reliable.

## Highest-cost error

The verified highest-cost selected error is **P2 / seed 2026 / case 2026-28**, with total decision cost **99**. The case is a true `other` failure that the model assigns to `test_data_state` at 68.56% confidence. This is exactly the type of failure the explicit `other` state was intended to expose.

## Failure-driven design change and re-test

The first failure suggested that a single positive DB signal could overpower dependency evidence. The re-test therefore changed only the DB likelihoods in a temporary robustness model:

| Cause | Baseline `P(DB+ | cause)` | Re-test |
|---|---:|---:|
| Flaky test | 0.10 | 0.02 |
| External dependency | 0.10 | 0.00 |
| CI infrastructure | 0.10 | 0.02 |
| Test-data/state | 0.80 | 0.80 |

The re-test was run on the same five seeds and 120 cases/seed at a 60% sensitivity threshold.

| Policy | Baseline accuracy | Re-test accuracy | Baseline decision cost | Re-test decision cost |
|---|---:|---:|---:|---:|
| P2 | 66.17% | **66.33%** | 44.24 | **44.14** |
| P3 | 72.83% | **73.00%** | 39.78 | **39.69** |

The change is small, which is itself useful evidence: merely making the DB likelihood more discriminative is not enough to solve the broader unknown-state/calibration problem. The next design step should therefore focus on richer evidence and calibration rather than repeatedly tuning one likelihood by hand.

## Failure categories covered

- Missing/under-modeled hidden state (`other`)
- Bad or weak evidence model
- Misleading binary evidence
- Poor calibration / low-confidence terminal classification
- Weak baseline policy
- Insufficient information after all available checks

The complete case-level evidence is retained in the GitHub Actions artifact, and the repository's generated results are reproducible from the fixed seeds and shared-case experiment.
