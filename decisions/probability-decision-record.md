# Probability Decision Record — v0.1

## Purpose

This record captures a representative belief-update path used by the CI Diagnosis Agent prototype. It is an audit artifact for the simulation, not a claim about real-world CI failure frequencies.

## Hidden states

The v0.1 simulator uses six competing hypotheses:

- Code regression
- Flaky test
- External dependency
- CI infrastructure
- Test-data/state
- Other

## Initial prior

| Hypothesis | Prior |
|---|---:|
| Code regression | 40.00% |
| Flaky test | 30.00% |
| External dependency | 10.00% |
| CI infrastructure | 10.00% |
| Test-data/state | 5.00% |
| Other | 5.00% |

Initial entropy: **2.1464 bits**.

These values are illustrative simulation assumptions, not measured real-world probabilities.

## Evidence 1 — rerun passes

Illustrative likelihoods used by the simulator:

| Hypothesis | Likelihood |
|---|---:|
| Code regression | 0.10 |
| Flaky test | 0.70 |
| External dependency | 0.40 |
| CI infrastructure | 0.40 |
| Test-data/state | 0.10 |
| Other | 0.50 |

Posterior after the observation:

| Hypothesis | Posterior |
|---|---:|
| Code regression | 11.11% |
| Flaky test | 58.33% |
| External dependency | 11.11% |
| CI infrastructure | 11.11% |
| Test-data/state | 1.39% |
| Other | 6.94% |

Entropy after evidence: **1.8632 bits**.

The rerun makes flakiness the leading hypothesis, but does not establish a diagnosis.

## Action selection

At this belief state, P1 evaluates available diagnostic actions using expected information gain relative to assumed action cost. `SEARCH_HISTORY` is selected because it has the strongest EIG/cost score under the v0.1 model.

The action costs are relative simulation units:

- 1 = Low
- 2 = Low–Medium
- 3 = Medium
- 4 = Medium–High

They are assumptions, not measured time or monetary costs.

## Evidence 2 — flaky pattern found in history

Illustrative likelihoods:

| Hypothesis | Likelihood |
|---|---:|
| Code regression | 0.10 |
| Flaky test | 0.80 |
| External dependency | 0.10 |
| CI infrastructure | 0.10 |
| Test-data/state | 0.10 |
| Other | 0.50 |

Updated posterior:

| Hypothesis | Posterior |
|---|---:|
| Code regression | 2.07% |
| Flaky test | 87.05% |
| External dependency | 2.07% |
| CI infrastructure | 2.07% |
| Test-data/state | 0.26% |
| Other | 6.48% |

Entropy after evidence: **0.7999 bits**.

Information gain from the historical evidence: **1.0632 bits**.

## Interpretation

The two observations progressively reduce uncertainty and shift belief toward the flaky-test hypothesis. The probability is a model output under illustrative assumptions, not a calibrated probability that a production failure is flaky.

## Limitations

- Priors are illustrative.
- Likelihoods are illustrative.
- Relative action costs are qualitative assumptions.
- Historical comparability is not validated against a production dataset.
- The 80% stopping threshold is a prototype parameter.
- The 48 evaluation cases are simulated.

## Version

`probability-decision-record-v0.1`
