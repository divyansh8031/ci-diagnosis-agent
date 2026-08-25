# Error analysis

The executable experiment produced 1,800 policy-case records (5 seeds × 120 cases × 3 policies). Five representative incorrect decisions are recorded below. They are drawn from the verified GitHub Actions artifact and are not invented examples.

## Case 1 — P3 flaky test → test-data/state

- Seed/case: 2026 / 2026-12
- True cause: `flaky_test`
- Prediction: `test_data_state`
- Final confidence: 38.20%
- Actions: `search_history > check_dependency > local_reproduction > rerun > inspect_code > check_db`
- Observations: history FAIL; dependency FAIL; local reproduction FAIL; rerun PASS; code inspection FAIL; DB PASS
- Decision cost: 17
- Escalated: yes
- Failure condition: later evidence outweighed the positive rerun under the current likelihood model.
- Evidence that could change the decision: stronger historical flakiness evidence or repeated rerun observations.
- Design implication: test repeated-history evidence and calibration before treating a single DB signal as decisive.

## Case 2 — P2 test-data/state → external dependency

- Seed/case: 2029 / 2029-5
- True cause: `test_data_state`
- Prediction: `external_dependency`
- Final confidence: 46.32%
- Actions: `rerun > search_history > check_dependency > local_reproduction > inspect_code > check_db`
- Observations: rerun FAIL; history FAIL; dependency PASS; local reproduction FAIL; code inspection FAIL; DB PASS
- Decision cost: 17
- Escalated: yes
- Failure condition: a positive dependency signal competed with positive DB evidence.
- Evidence that could change the decision: more discriminative DB/state evidence or a service-health persistence check.
- Design implication: distinguish a transient dependency observation from sustained service health.

## Case 3 — P2 external dependency → test-data/state

- Seed/case: 2028 / 2028-75
- True cause: `external_dependency`
- Prediction: `test_data_state`
- Final confidence: 68.56%
- Actions: `rerun > search_history > check_dependency > local_reproduction > inspect_code > check_db`
- Observations: rerun FAIL; history FAIL; dependency FAIL; local reproduction FAIL; code inspection FAIL; DB PASS
- Decision cost: 17
- Escalated: yes
- Failure condition: the DB signal dominated after several negative signals.
- Evidence that could change the decision: repeated service-health checks or dependency recovery timing.
- Design implication: add persistence/temporal evidence for external dependencies.

## Case 4 — P0 CI infrastructure → code regression

- Seed/case: 2026 / 2026-52
- True cause: `ci_infrastructure`
- Prediction: `code_regression`
- Final confidence: 62.98%
- Actions: `rerun > search_history > check_dependency > local_reproduction > inspect_code > check_db`
- Observations: rerun FAIL; history FAIL; dependency FAIL; local reproduction FAIL; code inspection PASS; DB FAIL
- Decision cost: 17
- Escalated: yes
- Failure condition: fixed-sequence diagnosis allowed code evidence to dominate infrastructure evidence.
- Evidence that could change the decision: package-download, runner, container, pod, or network-health evidence.
- Design implication: add an explicit CI-infrastructure diagnostic branch.

## Case 5 — P0 unknown/other → code regression

- Seed/case: 2026 / 2026-16
- True cause: `other`
- Prediction: `code_regression`
- Final confidence: 62.98%
- Actions: `rerun > search_history > check_dependency > local_reproduction > inspect_code > check_db`
- Observations: rerun FAIL; history FAIL; dependency FAIL; local reproduction PASS; code inspection FAIL; DB FAIL
- Decision cost: 17
- Escalated: yes
- Failure condition: the model must choose one of the known causes even when the evidence is weakly discriminative.
- Evidence that could change the decision: an explicit unknown/abstain action.
- Design implication: add an abstention state and calibrate the stopping rule around decision value, not just entropy.

## Highest-cost error

The maximum observed decision cost is **17**, tied across multiple incorrect cases. One representative is P0 / 2026-12. The consequence is important: a wrong diagnosis that leads to human review can cost more than an additional cheap automated check. This supports the cohort's emphasis on decision cost rather than accuracy alone.

## Failure categories covered

- Code regression misclassified as another cause
- Flaky test misclassified as state
- External dependency missed
- CI infrastructure missed
- Unknown/other overcommitted to a known cause

The complete case-level artifact is retained from the final GitHub Actions run; the repository's `results/final_results.md` contains the verified aggregate and selected case records.
