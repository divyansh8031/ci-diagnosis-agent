# Probability Decision Record — CI Diagnosis Agent (Current)

> **Archived note:** this file originally contained the v0.1 decision record. It is now aligned with the current simulation model. The canonical submission artifact is `docs/probability_decision_record.md`.

## Purpose

Capture a representative Bayesian belief-update path used by the current CI Diagnosis Agent. This is an audit artifact for the simulation, not a claim about real-world CI failure frequencies.

## Hidden states and priors

| Hypothesis | Prior |
|---|---:|
| Code regression | 40.00% |
| Flaky test | 30.00% |
| External dependency | 10.00% |
| CI infrastructure | 10.00% |
| Test-data/state | 5.00% |
| Other | 5.00% |

Initial entropy: **2.1464 bits**.

These are simulation assumptions, not calibrated production probabilities.

## Likelihood mapping

The current simulator maps qualitative assumptions to:

- often → 0.8
- sometimes → 0.4
- rarely → 0.1

For `RERUN -> PASS`, the current model gives:

| Hypothesis | Posterior |
|---|---:|
| Code regression | 34.78% |
| Flaky test | 52.17% |
| External dependency | 8.70% |
| CI infrastructure | 2.17% |
| Test-data/state | 1.09% |
| Other | 1.09% |

For `RERUN -> FAIL`:

| Hypothesis | Posterior |
|---|---:|
| Code regression | 44.44% |
| Flaky test | 11.11% |
| External dependency | 11.11% |
| CI infrastructure | 16.67% |
| Test-data/state | 8.33% |
| Other | 8.33% |

## Entropy and expected information gain

Initial entropy is **2.1464 bits**.

For a passing rerun, posterior entropy is **1.5879 bits** and outcome-specific information gain is **0.5585 bits**.

For a failed rerun, posterior entropy can increase because uncertainty is redistributed among several hypotheses. This is why the policy uses expected information gain before selecting an action rather than treating every observed outcome as guaranteed information.

For the rerun action:

```text
P(PASS) = 0.46
P(FAIL) = 0.54
Expected posterior entropy ≈ 1.9469 bits
EIG ≈ 0.1995 bits
```

P3 compares this expected value against action cost.

## Costs and threshold

Diagnostic costs are relative simulation units:

- cheap automated checks = 1
- heavier diagnostics = 2
- human review consequence = 8
- human intervention/change consequence = 9

The main comparison uses a **70% commitment threshold**. This is a simulation parameter and is tested at 60%, 70%, and 80%; it is not an empirically derived universal threshold.

## Policies

- **P0:** fixed diagnostic sequence.
- **P2:** posterior-threshold policy.
- **P3:** expected-information-gain per cost policy.

## Experiment

The current evaluation uses **5 fixed seeds × 120 cases**. Each policy receives the same pre-generated hidden cases and observation opportunities so that policy comparisons are fair.

The simulated cases evaluate policy behavior; they do not independently recalibrate the priors because the cases are generated from the same assumed probabilistic model.

## Canonical record

For the complete current model, likelihood table, cost model, posterior examples, experiment methodology and limitations, see:

`docs/probability_decision_record.md`

`research/research-file.md`

## Version

`probability-decision-record-current`
