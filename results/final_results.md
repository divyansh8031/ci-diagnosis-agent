# Final Week 1 experiment results

These values come from the GitHub Actions run on commit `eefde21978a47e4bcab61290fbc49304304c9439` using 5 fixed seeds (2026–2030), 120 cases per seed, and identical pre-generated observation opportunities for P0/P2/P3.

## Main comparison at 70% threshold

| Policy | Accuracy | Mean diagnostic cost | Mean decision cost | Mean actions | Escalation |
|---|---:|---:|---:|---:|---:|
| P0 fixed sequence | 75.83% | 9.00 | 14.25 | 6.00 | 65.67% |
| P2 threshold | 71.00% | 5.83 | 10.75 | 4.28 | 61.50% |
| P3 EIG/cost | 73.17% | 5.36 | 10.63 | 3.64 | 65.83% |

P3 reduces mean diagnostic cost by about 40.4% relative to P0 and mean diagnostic actions by about 39.3%, while losing 2.67 percentage points of accuracy. P2 is cheaper than P0 but loses more accuracy.

Mean decision cost includes diagnostic cost plus the simulated human-consequence class: 0 for an automated flaky-test rerun, 8 for human review/intervention classes, and 9 for the `other`/highest-consequence class. These consequence assignments are explicit simulation assumptions, not production monetary values.

## Threshold sensitivity

| Threshold | Policy | Accuracy | Mean diagnostic cost | Mean decision cost | Mean actions |
|---:|---|---:|---:|---:|---:|
| 60% | P2 | 66.17% | 4.53 | 10.03 | 3.63 |
| 60% | P3 | 72.50% | 4.60 | 9.86 | 3.19 |
| 70% | P2 | 71.00% | 5.83 | 10.75 | 4.28 |
| 70% | P3 | 73.17% | 5.36 | 10.63 | 3.64 |
| 80% | P2 | 75.17% | 6.75 | 11.98 | 4.88 |
| 80% | P3 | 74.50% | 6.09 | 11.51 | 4.19 |

Interpretation: P3 is not universally dominant. At 60% and 70% it has lower decision cost and higher accuracy than P2; at 80%, P2 has slightly higher accuracy while P3 remains cheaper. The defensible conclusion is an efficiency/accuracy trade-off, not universal superiority.

## Error-analysis cases

The executable experiment produced 1,800 policy-case records. Five representative incorrect decisions are recorded below; the complete case-level artifact is retained in the GitHub Actions run.

1. **P3, seed 2026, case 2026-12:** true `flaky_test`, predicted `test_data_state`, confidence 38.20%, decision cost 17. Evidence: history FAIL, dependency FAIL, local reproduction FAIL, rerun PASS, code inspection FAIL, DB PASS. Failure condition: the current likelihood model makes the combination of later evidence outweigh a single positive rerun. Design implication: repeated-history evidence and stronger calibration for state checks should be tested.
2. **P2, seed 2029, case 2029-5:** true `test_data_state`, predicted `external_dependency`, confidence 46.32%, decision cost 17. Evidence: rerun FAIL, history FAIL, dependency PASS, local reproduction FAIL, code inspection FAIL, DB PASS. Failure condition: a positive dependency signal competes with a positive DB signal. Design implication: make the DB/state observation more discriminative when test-data is suspected.
3. **P2, seed 2028, case 2028-75:** true `external_dependency`, predicted `test_data_state`, confidence 68.56%, decision cost 17. Evidence: rerun FAIL, history FAIL, dependency FAIL, local reproduction FAIL, code inspection FAIL, DB PASS. Failure condition: the model overweights the DB observation after several negative signals. Design implication: add service-health persistence/availability evidence rather than relying on one binary dependency check.
4. **P0, seed 2026, case 2026-52:** true `ci_infrastructure`, predicted `code_regression`, confidence 62.98%, decision cost 17. Evidence: rerun FAIL, history FAIL, dependency FAIL, local reproduction FAIL, code inspection PASS, DB FAIL. Failure condition: P0 keeps executing the full sequence even when infrastructure evidence is already plausible. Design implication: an adaptive policy should prioritize infrastructure-specific checks when runner/package/container evidence appears.
5. **P0, seed 2026, case 2026-16:** true `other`, predicted `code_regression`, confidence 62.98%, decision cost 17. Evidence: rerun FAIL, history FAIL, dependency FAIL, local reproduction PASS, code inspection FAIL, DB FAIL. Failure condition: the model is forced to choose a known cause when evidence does not support any cause strongly. Design implication: add an explicit abstention/unknown decision state.

## Highest-cost error

The maximum observed decision cost is **17**, with ties among multiple incorrect cases. One representative highest-cost case is P0 / seed 2026 / case 2026-12. The important finding is not that this particular case is uniquely worst; it is that incorrect decisions requiring human review can dominate total decision cost.

## Reproducibility

The validation workflow passed simulator, Bayesian-update, failed-rerun, and information-gain checks, then generated the shared-case experiment, sensitivity analysis, case-level records, confusion matrices, five-error selection, and highest-cost-error record. The artifact is `ci-diagnosis-final-evidence` from the final-evidence GitHub Actions run.

These are simulation results under explicit priors, likelihoods, action costs, and consequence classes. They are not estimates of real-world CI failure frequencies or production ROI.
