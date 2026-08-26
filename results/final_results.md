# Final Week 1 experiment results

These values come from the verified GitHub Actions run on commit `069368ccf784518c00c343df08af6cc139372da9` using 5 fixed seeds (2026–2030), 120 cases per seed, and identical pre-generated observation opportunities for P0/P2/P3.

## Main comparison at derived 47.06% threshold

The threshold is derived from `p* = C_FP / (C_FP + C_FN) = 80 / (80 + 90) = 47.06%`.

| Policy | Accuracy | Mean diagnostic cost | Mean decision cost | Mean actions | Escalation |
|---|---:|---:|---:|---:|---:|
| P0 no-evidence baseline | 39.17% | 0.00 | 60.88 | 0.00 | 100.00% |
| P2 derived threshold | 58.00% | 3.04 | 46.17 | 2.46 | 52.50% |
| P3 EIG/cost + decision-value stop | 51.50% | 1.56 | 48.13 | 1.56 | 56.00% |

At the derived threshold, P2 improves accuracy by 18.83 percentage points over the trivial baseline and reduces mean decision cost by about 24.2%. P3 uses substantially fewer checks than P2 but gives up accuracy at this low threshold and has slightly higher decision cost than P2.

This is a deliberately non-cherry-picked result: P3 is not claimed to be universally superior.

## Threshold sensitivity

| Threshold | Policy | Accuracy | Mean diagnostic cost | Mean decision cost | Mean actions |
|---:|---|---:|---:|---:|---:|
| 40% | P2 | 39.17% | 0.00 | 60.88 | 0.00 |
| 40% | P3 | 39.17% | 0.00 | 60.88 | 0.00 |
| 47.06% | P2 | 58.00% | 3.04 | 46.17 | 2.46 |
| 47.06% | P3 | 51.50% | 1.56 | 48.13 | 1.56 |
| 55% | P2 | 63.67% | 4.01 | 45.76 | 3.28 |
| 55% | P3 | 61.33% | 3.61 | 44.20 | 2.70 |
| 60% | P2 | 66.17% | 4.53 | 44.24 | 3.63 |
| 60% | P3 | **72.83%** | 4.49 | **39.78** | 3.14 |
| 70% | P2 | 71.00% | 5.83 | 41.70 | 4.28 |
| 70% | P3 | **73.50%** | 4.57 | **39.42** | 3.18 |
| 80% | P2 | **75.17%** | 6.75 | 40.48 | 4.88 |
| 80% | P3 | 73.50% | 4.57 | 39.42 | 3.18 |

The defensible interpretation is an efficiency/accuracy frontier, not universal P3 dominance. P3 becomes particularly effective around 60–70%, while P2 reaches higher accuracy at 80%.

## Failure-driven re-test

The error analysis identified a case where a positive DB observation could overpower competing explanations. A controlled re-test made DB evidence more discriminative against flaky tests, external dependencies, and CI infrastructure while leaving the test-data likelihood unchanged.

| Policy | Baseline accuracy @60% | Re-test accuracy @60% | Baseline decision cost | Re-test decision cost |
|---|---:|---:|---:|---:|
| P2 | 66.17% | **66.33%** | 44.24 | **44.14** |
| P3 | 72.83% | **73.00%** | 39.78 | **39.69** |

The effect is intentionally reported as small. It shows that changing one likelihood assumption does not solve the broader calibration/unknown-state problem.

## Error-analysis cases

The executable experiment produced 1,800 policy-case records. Five representative incorrect decisions from the verified artifact are:

1. **P2, seed 2026, case 2026-28:** true `other`, predicted `test_data_state`, confidence 68.56%, decision cost 99. Six checks were run; DB was positive after all other checks were negative.
2. **P3, seed 2026, case 2026-16:** true `other`, predicted `code_regression`, confidence 50.00%, decision cost 92. The derived threshold allowed a terminal decision despite weak separation.
3. **P0, seed 2026, case 2026-16:** true `other`, predicted `code_regression`, confidence 40.00%, decision cost 90. No evidence was collected by design.
4. **P2, seed 2026, case 2026-77:** true `test_data_state`, predicted `ci_infrastructure`, confidence 51.39%, decision cost 89. All six observations were negative.
5. **P2, seed 2027, case 2027-37:** true `code_regression`, predicted `ci_infrastructure`, confidence 51.39%, decision cost 89. All six observations were negative.

## Highest-cost error

The verified highest-cost selected error is **P2 / seed 2026 / case 2026-28**, with total decision cost **99**. It is a true `other` case predicted as `test_data_state` at 68.56% confidence.

## Reproducibility

The validation workflow passed simulator, Bayesian-update, failed-rerun, information-gain, and policy checks. The experiment generated shared-case results, threshold sensitivity, confusion matrices, case-level records, five representative errors, and the highest-cost error.

The GitHub Actions artifact is `ci-diagnosis-final-evidence` from the verified final-evidence run.

These are simulation results under explicit priors, likelihoods, diagnostic costs, and response-consequence assumptions. They are not estimates of real-world CI failure frequencies or production ROI.
