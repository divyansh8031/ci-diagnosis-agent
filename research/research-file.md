# CI Diagnosis Agent — Research File

**Status:** v0.2 — probabilistic model, information-value analysis, and final simulation results incorporated  
**Problem:** CI integration-test failure diagnosis  
**Scope:** Diagnose and select the next diagnostic action; do not automatically remediate in the first version.

> This is a living research document. Assumptions, practitioner observations, research sources, calculations, experiment results, and limitations are kept separate. Simulation numbers are not presented as production statistics.

## 1. Problem Statement

> **The agent observes CI integration-test failure information and must select the next diagnostic action because the actual failure cause is hidden.**

The focus is integration-test failures where the available evidence does not immediately reveal the root cause. The first version diagnoses and recommends rather than automatically modifying code, configuration, databases, or services.

## 2. Project Objective

The agent should:

1. observe incomplete evidence;
2. maintain competing hypotheses about the hidden cause;
3. update beliefs when evidence arrives;
4. choose a diagnostic action;
5. account for diagnostic cost;
6. continue investigating when useful;
7. escalate when evidence is insufficient or consequences are high.

The central research question is whether **belief-aware, information-value-based action selection** can reduce diagnostic effort while retaining useful diagnostic accuracy.

## 3. Current Hidden States

The simulation currently uses six mutually exclusive hidden causes:

| Cause | Meaning |
|---|---|
| `code_regression` | A recent code change caused the failure. |
| `flaky_test` | The test is nondeterministic/intermittently failing. |
| `external_dependency` | A relevant dependent/third-party service is responsible. |
| `ci_infrastructure` | CI runner, package, container, pod, network, or related infrastructure is responsible. |
| `test_data_state` | DB/test data/state changed in a way that explains the failure. |
| `other` | Residual category for causes not represented by the above states. |

The explicit `other` state is important because an agent forced to choose among known causes can become confidently wrong when none of them explains the case.

## 4. Simulation Priors

The current simulation uses:

| Hidden cause | Prior |
|---|---:|
| Code regression | 0.40 |
| Flaky test | 0.30 |
| External dependency | 0.10 |
| CI infrastructure | 0.10 |
| Test-data/state | 0.05 |
| Other | 0.05 |
| **Total** | **1.00** |

These values are **research assumptions for simulation**, not measured real-world CI failure frequencies. They were chosen from the project's qualitative reasoning and should be replaced or calibrated with independent labeled historical data if such data becomes available.

A key methodological rule is that simulated cases generated from these priors cannot subsequently be treated as independent evidence that validates the same priors.

## 5. Evidence Model

For each diagnostic action, the simulator defines a binary positive/negative observation. The model specifies:

> `P(observation | hidden cause)`

The current qualitative-to-numeric mapping is:

- **often → 0.8**
- **sometimes → 0.4**
- **rarely → 0.1**

Current likelihoods for a positive observation are:

| Action | Code | Flaky | Dependency | CI infra | Test data | Other |
|---|---:|---:|---:|---:|---:|---:|
| Rerun | 0.4 | 0.8 | 0.4 | 0.1 | 0.1 | 0.1 |
| Search history | 0.4 | 0.8 | 0.1 | 0.1 | 0.1 | 0.1 |
| Check dependency | 0.1 | 0.4 | 0.8 | 0.1 | 0.1 | 0.1 |
| Local reproduction | 0.8 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 |
| Inspect code | 0.8 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 |
| Check DB | 0.1 | 0.1 | 0.1 | 0.1 | 0.8 | 0.1 |

These are assumptions used to create a reproducible diagnostic world. They are not claims that, for example, 80% of real flaky tests pass on rerun.

## 6. Diagnostic Actions and Relative Costs

The simulator currently assigns relative diagnostic costs:

| Action | Cost |
|---|---:|
| Rerun | 1 |
| Search history | 1 |
| Check dependency | 1 |
| Local reproduction | 2 |
| Inspect code | 2 |
| Check DB | 2 |

These are simulation units rather than money, minutes, or production resource measurements.

The design rationale is that a rerun/history/dependency check is comparatively cheap, while local reproduction, code inspection, and DB inspection require more investigation effort. Future versions should replace these assumptions with measured or practitioner-derived costs.

## 7. Bayesian Belief Update

The agent starts each case with the prior distribution. After observing evidence `E`, it updates using:

`P(cause | E) = P(E | cause) P(cause) / P(E)`

where:

`P(E) = Σ P(E | cause) P(cause)`.

### Worked example: RERUN = PASS

Initial belief:

```text
Code regression       40%
Flaky test            30%
External dependency  10%
CI infrastructure    10%
Test data              5%
Other                  5%
```

For a passing rerun, the likelihoods are:

```text
Code       0.4
Flaky      0.8
Dependency 0.4
CI         0.1
Data       0.1
Other      0.1
```

Multiply prior × likelihood:

```text
Code       0.40 × 0.40 = 0.160
Flaky      0.30 × 0.80 = 0.240
Dependency 0.10 × 0.40 = 0.040
CI         0.10 × 0.10 = 0.010
Data       0.05 × 0.10 = 0.005
Other      0.05 × 0.10 = 0.005
```

The evidence probability is:

`P(PASS) = 0.46`.

Normalize:

```text
Code       0.160 / 0.46 = 34.78%
Flaky      0.240 / 0.46 = 52.17%
Dependency 0.040 / 0.46 =  8.70%
CI         0.010 / 0.46 =  2.17%
Data       0.005 / 0.46 =  1.09%
Other      0.005 / 0.46 =  1.09%
```

The important interpretation is:

> A passing rerun does not prove that the test is flaky. It changes the belief distribution, making flakiness more plausible under the current model.

### Worked example: RERUN = FAIL

For a failed rerun, use `1 - P(PASS | cause)`:

```text
Code       0.60
Flaky      0.20
Dependency 0.60
CI         0.90
Data       0.90
Other      0.90
```

The resulting posterior is approximately:

```text
Code       44.44%
Flaky      11.11%
Dependency 11.11%
CI         16.67%
Data        8.33%
Other       8.33%
```

Again, a failed rerun does not prove a code regression. It redistributes belief toward several competing explanations.

## 8. Entropy and Information Gain

Entropy measures uncertainty in the current belief state:

`H(S) = -Σ p(s) log2 p(s)`.

For the initial prior:

`H(before) = 2.1464 bits`.

### PASS outcome

After `RERUN = PASS`:

`H(after | PASS) = 1.5879 bits`.

The information gained for this particular outcome is:

`2.1464 - 1.5879 = 0.5585 bits`.

### FAIL outcome

After `RERUN = FAIL`:

`H(after | FAIL) = 2.2527 bits`.

The outcome-specific information gain is therefore:

`2.1464 - 2.2527 = -0.1063 bits`.

This is not an error. Evidence can increase entropy when it removes a leading hypothesis while leaving several alternatives plausible. The important distinction is between **outcome-specific information gain** and **expected information gain before running the check**.

## 9. Expected Information Gain

Before running a diagnostic action, the agent does not know its result. Therefore it uses expected information gain:

`EIG(action) = H(S) - H(S | E)`

where `H(S | E)` is the probability-weighted average entropy across all possible observations.

For the rerun:

```text
P(PASS) = 0.46
P(FAIL) = 0.54

Expected entropy
= 0.46 × 1.5879 + 0.54 × 2.2527
= 1.9469 bits

EIG
= 2.1464 - 1.9469
= 0.1995 bits
```

This is the quantity that should be used when deciding whether to run a check **before** knowing its result.

## 10. Information Gain per Cost

Using the current prior/likelihood model:

| Action | Expected IG | Cost | IG / Cost |
|---|---:|---:|---:|
| Search history | 0.2402 | 1 | **0.2402** |
| Rerun | 0.1995 | 1 | **0.1995** |
| Local reproduction | 0.3879 | 2 | **0.1939** |
| Inspect code | 0.3879 | 2 | **0.1939** |
| Check dependency | 0.1819 | 1 | **0.1819** |
| Check DB | 0.0894 | 2 | **0.0447** |

Thus, at the initial belief state, **search history has the highest expected information gain per unit simulation cost**.

This illustrates why the project is not simply choosing the action with the largest raw information gain. Cost matters.

## 11. Policy Definitions

### P0 — Fixed baseline

P0 follows a fixed action sequence without belief-aware stopping. It provides the baseline for asking whether adaptive reasoning is actually useful.

### P2 — Threshold policy

P2 updates beliefs after observations and stops when the highest posterior reaches the configured confidence threshold. The final experiment uses a 70% threshold as the main comparison and also evaluates 60% and 80% sensitivity.

The threshold is a simulation policy parameter, not a claim that 70% is the optimal production threshold.

### P3 — Value-of-information policy

P3 updates beliefs and selects the next action using expected information gain per cost. It stops according to the same terminal/threshold logic.

The intended loop is:

```text
Initial prior
    ↓
Choose action by EIG/cost
    ↓
Observe result
    ↓
Bayesian posterior update
    ↓
Recalculate uncertainty and EIG/cost
    ↓
Choose next action or stop/escalate
```

## 12. What the 120 Simulated Cases Actually Mean

The final experiment uses:

- **120 cases per seed**;
- **5 fixed seeds (2026–2030)**;
- **600 cases per policy**;
- **1,800 policy-case records across P0/P2/P3**.

Each simulated case contains:

1. a hidden true cause sampled from the simulation priors;
2. one pre-generated observation outcome for every available diagnostic action.

The policy does **not** receive the hidden cause. It receives only the observations revealed by the actions it chooses.

The important fairness property is that P0, P2, and P3 are evaluated on the **same pre-generated cases and observation opportunities**. This prevents one policy from receiving an easier random world than another.

### What these cases do not do

The 120 cases do **not** independently recalibrate the priors. They are generated from the priors and likelihoods that define the simulation world.

Therefore:

> The experiment evaluates policies **under the assumed probabilistic world**; it does not establish that the assumed world matches production CI.

Independent historical CI data would be required for empirical calibration.

## 13. Decision Consequence Model

The final simulation also includes a consequence class:

- `0` for the automated flaky-test path;
- `8` for human review/intervention classes;
- `9` for the highest-consequence `other` class.

These are explicit simulation units, not production monetary values.

The decision cost is:

`decision cost = diagnostic cost + consequence cost`.

This is why decision cost is more informative than accuracy alone: a wrong diagnosis that triggers expensive human intervention can matter more than a cheap diagnostic mistake.

## 14. Final Simulation Results

The final GitHub Actions experiment used commit `eefde21978a47e4bcab61290fbc49304304c9439`, five fixed seeds, 120 cases per seed, and identical pre-generated observation opportunities.

### Main comparison at 70% threshold

| Policy | Accuracy | Mean diagnostic cost | Mean decision cost | Mean actions | Escalation |
|---|---:|---:|---:|---:|---:|
| P0 fixed sequence | 75.83% | 9.00 | 14.25 | 6.00 | 65.67% |
| P2 threshold | 71.00% | 5.83 | 10.75 | 4.28 | 61.50% |
| P3 EIG/cost | 73.17% | 5.36 | 10.63 | 3.64 | 65.83% |

P3 reduces mean diagnostic cost by approximately **40.4% relative to P0** and mean diagnostic actions by approximately **39.3%**, while losing 2.67 percentage points of accuracy relative to P0.

P2 is cheaper than P0 but loses more accuracy.

### Threshold sensitivity

| Threshold | Policy | Accuracy | Mean diagnostic cost | Mean decision cost | Mean actions |
|---:|---|---:|---:|---:|---:|
| 60% | P2 | 66.17% | 4.53 | 10.03 | 3.63 |
| 60% | P3 | 72.50% | 4.60 | 9.86 | 3.19 |
| 70% | P2 | 71.00% | 5.83 | 10.75 | 4.28 |
| 70% | P3 | 73.17% | 5.36 | 10.63 | 3.64 |
| 80% | P2 | 75.17% | 6.75 | 11.98 | 4.88 |
| 80% | P3 | 74.50% | 6.09 | 11.51 | 4.19 |

The defensible conclusion is an **efficiency/accuracy trade-off**, not universal P3 superiority. At 60% and 70%, P3 has lower decision cost and higher accuracy than P2; at 80%, P2 has slightly higher accuracy while P3 remains cheaper.

## 15. Error Analysis

Five representative incorrect decisions from the executable experiment:

1. **P3, seed 2026, case 2026-12:** true `flaky_test`, predicted `test_data_state`, confidence 38.20%. The model allowed later state evidence to outweigh a positive rerun. This motivates stronger calibration for state-related checks and repeated-history evidence.
2. **P2, seed 2029, case 2029-5:** true `test_data_state`, predicted `external_dependency`, confidence 46.32%. Dependency and DB evidence competed. This motivates more discriminative DB/state evidence.
3. **P2, seed 2028, case 2028-75:** true `external_dependency`, predicted `test_data_state`, confidence 68.56%. The model over-weighted the DB observation after several negative signals. A persistent service-health/availability signal may be more useful than a single binary dependency check.
4. **P0, seed 2026, case 2026-52:** true `ci_infrastructure`, predicted `code_regression`, confidence 62.98%. The fixed sequence continued investigating even when infrastructure evidence was plausible. This illustrates the weakness of a fixed sequence.
5. **P0, seed 2026, case 2026-16:** true `other`, predicted `code_regression`, confidence 62.98%. The model was forced to choose a known cause when evidence did not support one strongly. This motivates an explicit abstention/unknown decision state.

Maximum observed decision cost was **17**, with ties among multiple incorrect cases. The broader finding is that errors requiring human review can dominate total decision cost.

## 16. Human-in-the-Loop Policy

The project's operational reasoning is deliberately conservative:

### Flaky test

If rerun evidence and history support flakiness, rerunning is an automated low-cost action. A rerun failure should not automatically imply a code regression; the agent should update beliefs and continue diagnosis.

### Code regression

If evidence points to a recent code regression, the agent should present the evidence and a proposed remediation/revert to a human rather than automatically changing code in this first version.

### External dependency

Check relevant service health/availability. If the service is unavailable, retry when appropriate. If the issue persists or the agent cannot establish responsibility safely, escalate with the evidence and suggested next step.

### CI infrastructure

Use CI logs and infrastructure-specific evidence to identify package-download, container, runner, pod, or environment failures. Changes requiring configuration/version intervention should be escalated to a human.

### Test-data/state

DB/test-data changes can be high-context and potentially destructive to investigate. The agent should present evidence and suggestions for human review rather than modifying state automatically.

### Other/unknown

If the residual/unknown state remains plausible, the agent should abstain/escalate rather than force a confident known-cause diagnosis.

## 17. Claims and Limitations

The following remain **simulation findings or hypotheses**, not production claims:

- The priors are correct for real CI systems.
- The 0.8/0.4/0.1 likelihood mapping reflects production frequencies.
- The relative action costs correspond to actual engineering time or money.
- The 70% threshold is optimal.
- Historical similarity reliably identifies root cause.
- Rerun alone reliably identifies flakiness.
- P3 will outperform P0/P2 on production CI data.
- The simulated consequence costs correspond to real organizational impact.

The experiment demonstrates that the architecture can perform Bayesian updates, compute entropy/EIG, select actions adaptively, and produce a reproducible policy comparison under the stated assumptions.

## 18. Reproducibility

The repository contains executable tests for the simulator, Bayesian updates, failed-rerun behavior, and information gain. The final workflow generated the shared-case experiment, sensitivity analysis, case-level records, confusion matrices, representative error analysis, and highest-cost-error record.

The shared-case experiment uses fixed seeds and pre-generates all action observations so P0/P2/P3 receive identical evidence opportunities.

## 19. Research Sources

### LLM-based integration-test diagnosis
Google's 2026 Auto-Diagnose paper studies LLM-based diagnosis of integration-test failures and reports manual evaluation on 71 real-world failures.

Source: https://arxiv.org/abs/2604.12108

### Regression-inducing changes
Ziftci and Reardon studied automatically identifying changes that induce test failures in CI at Google scale.

Source: https://research.google/pubs/who-broke-the-build-automatically-identifying-changes-that-induce-test-failures-in-continuous-integration-at-google-scale/

### Flaky-test diagnosis
Parry et al. empirically evaluated flaky-test detection approaches involving rerunning and machine-learning techniques.

Source: https://link.springer.com/article/10.1007/s10664-023-10307-w

### Static flaky-test prediction
Pontillo, Palomba and Ferrucci studied static prediction of test flakiness.

Source: https://link.springer.com/article/10.1007/s10664-022-10227-1

### Practitioner evidence
A r/devops discussion is treated as qualitative practitioner evidence rather than controlled research.

Source: https://www.reddit.com/r/devops/comments/1v119en/whats_your_actual_workflow_when_a_test_fails_in/

## 20. Open Research Questions

1. Can the assumed priors and likelihoods be calibrated against a real labeled CI-failure dataset?
2. How should historical failures be scored for comparability?
3. How should evidence sources that are correlated be handled so information is not double-counted?
4. Can an explicit unknown/abstention state improve high-consequence cases?
5. Can consequence-sensitive thresholds outperform a single fixed threshold?
6. Can human review cost be estimated from real workflow data?
7. How does the policy behave under distribution shift when failure types change?
8. Can richer observations replace binary PASS/FAIL likelihoods without making the model overconfident?

## 21. Research Integrity Note

All numerical probabilities, likelihoods, costs, consequence classes, and simulation results in this document are explicitly labeled as assumptions or simulation outputs unless independently measured. No practitioner comments or researcher interactions are fabricated. Production conclusions require independent empirical validation.
