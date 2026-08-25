# Probability Decision Record — CI Diagnosis

## Scope

This is a reproducible simulation record, not a claim about real-world CI failure frequencies.

## Hidden states

- code regression
- flaky test
- external dependency
- CI infrastructure
- test-data/state
- other

## Initial prior

| Cause | Prior |
|---|---:|
| Code regression | 0.40 |
| Flaky test | 0.30 |
| External dependency | 0.10 |
| CI infrastructure | 0.10 |
| Test-data/state | 0.05 |
| Other | 0.05 |

## Likelihood model

The prototype maps qualitative research assumptions to simulation probabilities:

- often = 0.8
- sometimes = 0.4
- rarely = 0.1

These are model assumptions for controlled experimentation and are not calibrated production probabilities.

## Worked update

For `RERUN -> PASSED`, the current likelihood table gives a posterior of approximately:

- code regression: 34.78%
- flaky test: 52.17%
- external dependency: 8.70%
- CI infrastructure: 2.17%
- test-data/state: 1.09%
- other: 1.09%

For `RERUN -> FAILED`:

- code regression: 44.44%
- flaky test: 11.11%
- external dependency: 11.11%
- CI infrastructure: 16.67%
- test-data/state: 8.33%
- other: 8.33%

## Costs

| Action class | Relative cost |
|---|---:|
| Cheap automated check | 1 |
| Heavier automated diagnostic | 2 |
| Human review | 8 |
| Human intervention/change | 9 |

Diagnostic action costs in the simulator are 1 or 2. Human outcomes are evaluated separately as decision consequences.

## Decision threshold

The initial 70% threshold is a simulation parameter. Sensitivity analysis varies it; it must not be described as an empirically derived universal threshold.

## Audit requirements

Every experiment should record: seed, hidden cause, observations available to each policy, policy, actions taken, posterior after each observation, cost, final prediction, and escalation outcome.
