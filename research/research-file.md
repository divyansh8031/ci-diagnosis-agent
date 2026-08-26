# CI Diagnosis Agent — Research File

**Status:** v0.3 — cohort-aligned research record with derived decision threshold, true baseline, decision-value stopping, verified experiment, failure-driven re-test, and explicit limitations.

**Problem:** CI integration-test failure diagnosis.

**Scope:** Diagnose and select the next diagnostic action; do not automatically modify code, configuration, databases, or services in the first version.

> This is a controlled simulation research document. Assumptions, practitioner reasoning, calculations, executable experiment results, and limitations are kept separate. Simulation numbers are not presented as production CI statistics.

## 1. Problem statement

> **The agent observes CI integration-test failure information and must select the next diagnostic action because the actual failure cause is hidden.**

Integration-test failures often provide incomplete evidence. A useful diagnosis system should not immediately collapse uncertainty into one label. It should maintain competing hypotheses, update them as evidence arrives, choose checks that are useful relative to their cost, and stop or escalate when further investigation is not justified.

## 2. Research question

The central question is:

> **Can belief-aware, value-sensitive action selection reduce diagnostic effort and decision consequence relative to a trivial no-evidence baseline while preserving useful diagnostic accuracy?**

A secondary question is whether the result is robust to the confidence threshold and to changes in the evidence model.

## 3. Hidden states

The simulation uses six mutually exclusive hidden causes:

| Cause | Meaning |
|---|---|
| `code_regression` | A recent code change caused the failure. |
| `flaky_test` | The test is nondeterministic/intermittently failing. |
| `external_dependency` | A relevant dependent/third-party service is responsible. |
| `ci_infrastructure` | CI runner, package, container, pod, network, or related infrastructure is responsible. |
| `test_data_state` | DB/test data/state changed in a way that explains the failure. |
| `other` | Residual category for causes not represented by the above states. |

The explicit `other` state is methodologically important. Without it, a closed-world classifier can become confidently wrong when none of the named causes explains the case.

## 4. Simulation priors

| Hidden cause | Prior |
|---|---:|
| Code regression | 0.40 |
| Flaky test | 0.30 |
| External dependency | 0.10 |
| CI infrastructure | 0.10 |
| Test-data/state | 0.05 |
| Other | 0.05 |
| **Total** | **1.00** |

These are research assumptions for a reproducible simulation, not measured real-world CI frequencies. They must not be treated as empirical prevalence estimates.

The external-data plan is documented separately in `docs/data_sources.md`. Those datasets are reserved for future calibration because the current experiment has not mapped real CI labels to these six hidden states.

## 5. Evidence model

For each diagnostic action, the simulator defines a binary positive/negative observation and specifies:

> `P(observation | hidden cause)`

The qualitative-to-numeric mapping is:

- **often → 0.8**
- **sometimes → 0.4**
- **rarely → 0.1**

Positive-observation likelihoods:

| Action | Code | Flaky | Dependency | CI infra | Test data | Other |
|---|---:|---:|---:|---:|---:|---:|
| Rerun | 0.4 | 0.8 | 0.4 | 0.1 | 0.1 | 0.1 |
| Search history | 0.4 | 0.8 | 0.1 | 0.1 | 0.1 | 0.1 |
| Check dependency | 0.1 | 0.4 | 0.8 | 0.1 | 0.1 | 0.1 |
| Local reproduction | 0.8 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 |
| Inspect code | 0.8 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 |
| Check DB | 0.1 | 0.1 | 0.1 | 0.1 | 0.8 | 0.1 |

These are controlled model assumptions. They are not claims that, for example, 80% of real flaky tests pass on rerun.

### Evidence-model checks

Each evidence row defines the positive probability for every state. The negative probability is its complement, so the two outcomes sum to 1.00 within each hidden state.

An action whose likelihood is identical across every state would have zero discriminative information. The current actions are not identical across all states, although some actions are deliberately redundant (for example, local reproduction and code inspection share the same simplified likelihood structure). This is a limitation of the first simulation model.

## 6. Diagnostic costs

| Action | Cost |
|---|---:|
| Rerun | 1 |
| Search history | 1 |
| Check dependency | 1 |
| Local reproduction | 2 |
| Inspect code | 2 |
| Check DB | 2 |

These are simulation cost units, not money or minutes.

The relative scale makes cheap automated checks cheaper than heavier investigation. The absolute scale has no production interpretation.

## 7. Bayesian belief update

The agent starts with the prior distribution and updates after evidence `E` using:

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

For a passing rerun:

```text
Code       0.4
Flaky      0.8
Dependency 0.4
CI         0.1
Data       0.1
Other      0.1
```

Prior × likelihood:

```text
Code       0.160
Flaky      0.240
Dependency 0.040
CI         0.010
Data       0.005
Other      0.005
```

`P(PASS) = 0.46`.

Posterior:

```text
Code       34.78%
Flaky      52.17%
Dependency  8.70%
CI          2.17%
Data        1.09%
Other       1.09%
```

A passing rerun therefore increases the plausibility of flakiness but does not prove it.

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

Again, the failed rerun does not prove a code regression.

## 8. Entropy and information gain

Entropy is:

`H(S) = -Σ p(s) log2 p(s)`.

For the initial prior:

`H(before) = 2.1464 bits`.

After `RERUN = PASS`:

`H(after | PASS) = 1.5879 bits`.

Outcome-specific information gain:

`2.1464 - 1.5879 = 0.5585 bits`.

After `RERUN = FAIL`:

`H(after | FAIL) = 2.2527 bits`.

Outcome-specific gain:

`2.1464 - 2.2527 = -0.1063 bits`.

The negative value is not an arithmetic error. Evidence can increase entropy if it removes a leading hypothesis while leaving several alternatives plausible.

## 9. Expected information gain

Before a check is run, its outcome is unknown. Therefore the decision policy should use expected information gain:

`EIG(action) = H(S) - H(S | E)`

where `H(S | E)` is the probability-weighted entropy over all possible outcomes.

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

This is the quantity used to rank diagnostic checks before their result is known.

## 10. Information gain versus cost

At the initial prior:

| Action | Expected IG | Cost | IG / Cost |
|---|---:|---:|---:|
| Search history | 0.2402 | 1 | **0.2402** |
| Rerun | 0.1995 | 1 | **0.1995** |
| Local reproduction | 0.3879 | 2 | **0.1939** |
| Inspect code | 0.3879 | 2 | **0.1939** |
| Check dependency | 0.1819 | 1 | **0.1819** |
| Check DB | 0.0894 | 2 | **0.0447** |

Raw information gain and information-per-cost produce different orderings. This is the core reason the project treats diagnostic effort as part of the decision rather than merely maximizing entropy reduction.

For a fuller cost model, the research also recognizes time, human attention, and deadline effects as possible future cost dimensions. The current simulator keeps them collapsed into relative units.

## 11. Decision policy: derived threshold

The cohort requires the threshold to be derived rather than chosen as an arbitrary 70% or 80%.

The terminal consequence model uses:

- `C_FP = 80` simulation units for a false-positive human-review/intervention consequence;
- `C_FN = 90` simulation units for the highest-consequence false-negative path.

The break-even threshold is:

```text
p* = C_FP / (C_FP + C_FN)
   = 80 / (80 + 90)
   = 80 / 170
   = 0.470588...
   = 47.06%
```

The 80/90 scale is deliberately larger than diagnostic costs so that an additional check can have meaningful decision value. Multiplying both by 10 does not change the threshold; it only puts consequence and diagnostic costs on a useful common simulation scale.

**Important:** 47.06% is a derived threshold for this simulation's stated consequence assumptions. It is not a production CI threshold.

### Umbrella/break-even example

Suppose the agent must choose between:

- acting on a diagnosis with a possible high-consequence miss of 90 units;
- taking a human-review path costing 80 units when the risky state is absent.

The threshold is the probability at which the two expected consequences balance. Below the threshold, the review-side expected cost dominates less; above it, the risk-side expected cost becomes more important. This is the same break-even logic as any decision where carrying a protective action has a cost but failing to protect has a larger cost.

The important lesson is that a probability threshold is not a property of the classifier alone. It comes from the consequences of the actions attached to the probability.

## 12. Decision consequence model

Unlike the earlier version, consequence cost is now tied to the **terminal response selected by the diagnosis**, not merely to whether the predicted label is non-flaky.

Representative correct-response costs are:

| Predicted cause / response | Correct-state cost |
|---|---:|
| Flaky test → rerun | 0 |
| Code regression → human review/revert preparation | 30 |
| External dependency → wait for health/rerun | 20 |
| CI infrastructure → rerun/human review | 20 |
| Test-data/state → human data review | 40 |
| Other → human escalation | 90 |

Wrong paths generally incur 80 units of human-review consequence, with the `other`/highest-consequence path at 90.

The total metric is:

`decision cost = diagnostic cost + response consequence cost`.

This makes decision cost more meaningful than accuracy alone: an error can be operationally expensive even when it is only one classification error.

## 13. P0 — true no-evidence baseline

P0 is deliberately trivial:

> **Do not inspect any evidence; always choose the modal prior cause.**

The modal prior is `code_regression` at 40%.

This baseline is required because an adaptive policy should be compared with doing essentially nothing. It prevents a model from presenting an apparently good accuracy number without showing whether it beats a trivial policy.

## 14. P2 — threshold policy

P2:

1. starts from the prior;
2. updates beliefs after each observation;
3. stops when the highest posterior reaches the derived threshold;
4. otherwise follows the fixed diagnostic order:
   - rerun;
   - search history;
   - check dependency;
   - local reproduction;
   - inspect code;
   - check DB.

The default threshold is the derived 47.06%. Sensitivity analysis deliberately tests values below and above it.

## 15. P3 — value-of-information policy

P3:

1. updates beliefs after evidence;
2. ranks remaining checks by expected information gain per diagnostic cost;
3. estimates the expected **decision value** of the best-ranked check;
4. runs another check only when the expected reduction in terminal consequence exceeds that check's cost;
5. otherwise stops rather than buying information that cannot pay for itself.

The stop rule is therefore:

> **If no possible outcome of the next check can improve the expected terminal decision by more than the check costs, stop.**

This is stronger than an entropy-only stopping rule because information is valuable only when it can change the decision enough to matter.

## 16. Extension concepts beyond the supplied ladder

### 16.1 Value of information

**Plain meaning:** How much could a piece of information improve the eventual decision, after accounting for its possible outcomes and costs?

**Small example:** If a check costs 1 unit and is expected to reduce terminal consequence by 4 units, its net value is positive. If it reduces entropy by many bits but cannot change the eventual action, its decision value is effectively zero.

**When it is a mistake:** Treating every information gain as useful. A diagnostic result that never changes the action is not worth buying merely because it is statistically informative.

**Use in this project:** P3 uses EIG/cost to rank checks and a decision-value calculation as its stop gate.

### 16.2 Value of sample information / decision-aware evidence acquisition

**Plain meaning:** The value of a future observation depends on what decisions it could change, not only on how much uncertainty it removes.

**Small example:** If two hypotheses lead to exactly the same operational response, separating them may have zero decision value. If they lead to different and costly responses, even a modest probability shift can be valuable.

**When it is a mistake:** Using it to justify unlimited investigation. The check still has to have positive net value after diagnostic cost and operational delay.

**Use in this project:** This motivated the terminal consequence matrix and the P3 stop rule rather than using entropy alone.

### New question raised by the results

The results expose a further question not answered by entropy or EIG alone:

> **How should the agent behave when the residual `other` state is genuinely plausible and the available binary evidence cannot separate it from known causes?**

This motivates explicit abstention, calibration, richer evidence, and eventually real labeled CI data rather than endlessly tuning the same six-state binary simulator.

## 17. Experiment design

The verified experiment uses:

- **120 cases per seed**;
- **5 fixed seeds: 2026, 2027, 2028, 2029, 2030**;
- **600 cases per policy**;
- **1,800 policy-case records across P0/P2/P3**;
- one hidden cause per case;
- one pre-generated observation opportunity for every action;
- identical shared cases and observations for all policies.

The policies do not receive the hidden cause. They receive only the observations revealed by the actions they choose.

This shared-case construction avoids comparing policies on different random worlds.

## 18. Verified final experiment results

The final GitHub Actions validation and experiment completed successfully on commit `069368ccf784518c00c343df08af6cc139372da9`. The validation suite passed, the experiment completed, and the case-level artifact was uploaded.

### Main comparison at the derived 47.06% threshold

| Policy | Accuracy | Mean diagnostic cost | Mean decision cost | Mean actions | Escalation |
|---|---:|---:|---:|---:|---:|
| P0 no-evidence baseline | 39.17% | 0.00 | 60.88 | 0.00 | 100.00% |
| P2 derived-threshold | 58.00% | 3.04 | 46.17 | 2.46 | 52.50% |
| P3 EIG/cost + decision-value stop | 51.50% | 1.56 | 48.13 | 1.56 | 56.00% |

At the derived threshold, P2 improves accuracy by **18.83 percentage points** over P0 and reduces mean decision cost by approximately **24.2%**. P3 reduces diagnostic effort more aggressively than P2, but at this low threshold it gives up accuracy and has slightly higher decision cost than P2.

This is an important negative result: **P3 is not universally superior.**

### Threshold sensitivity

Verified multi-seed sensitivity results:

| Threshold | Policy | Accuracy | Diagnostic cost | Decision cost | Mean actions |
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

The sensitivity experiment shows the central trade-off clearly:

- low thresholds produce fewer checks but can terminate with weak classifications;
- higher thresholds improve accuracy but require more investigation;
- P3 becomes especially useful around 60–70%, where it combines lower decision cost with competitive or higher accuracy than P2;
- at 80%, P2 has the higher accuracy while P3 retains lower diagnostic effort and lower decision cost.

Therefore the defensible claim is **not** "P3 always wins." The defensible claim is that decision-aware evidence selection changes the efficiency/accuracy frontier, with the best operating point depending on the consequence assumptions and threshold.

## 19. Failure analysis

Five representative failures from the verified artifact:

1. **P2, seed 2026, case 2026-28:** true `other`, predicted `test_data_state`, confidence 68.56%, six actions, decision cost 99. A positive DB signal dominated the residual state. This motivated the failure-driven DB likelihood re-test.
2. **P3, seed 2026, case 2026-16:** true `other`, predicted `code_regression`, confidence 50%, two actions, decision cost 92. The residual class was not sufficiently separated by the available evidence.
3. **P0, seed 2026, case 2026-16:** true `other`, predicted `code_regression`, confidence 40%, no actions, decision cost 90. This demonstrates the expected weakness of the trivial baseline.
4. **P2, seed 2026, case 2026-77:** true `test_data_state`, predicted `ci_infrastructure`, confidence 51.39%, six actions, decision cost 89. All six observations were negative, leaving the posterior weakly discriminated.
5. **P2, seed 2027, case 2027-37:** true `code_regression`, predicted `ci_infrastructure`, confidence 51.39%, six actions, decision cost 89. Again, all six observations were negative and the simplified likelihood model could not separate the remaining hypotheses reliably.

These failures fall into the cohort categories of missing/under-modeled hidden state, weak or misleading evidence, insufficient information, and policy limitations.

## 20. Failure-driven design change and re-test

The first failure suggested that the DB signal was too easily interpreted as state evidence. A controlled re-test made the DB observation more discriminative:

| Cause | Baseline `P(DB+ | cause)` | Re-test |
|---|---:|---:|
| Flaky test | 0.10 | 0.02 |
| External dependency | 0.10 | 0.00 |
| CI infrastructure | 0.10 | 0.02 |
| Test-data/state | 0.80 | 0.80 |

The re-test used the same five seeds, 120 cases/seed, and a 60% threshold.

| Policy | Baseline accuracy | Re-test accuracy | Baseline decision cost | Re-test decision cost |
|---|---:|---:|---:|---:|
| P2 | 66.17% | **66.33%** | 44.24 | **44.14** |
| P3 | 72.83% | **73.00%** | 39.78 | **39.69** |

The improvement is small. That is a useful result rather than a failure of the experiment: changing one likelihood assumption does not solve the broader problem. The evidence points toward richer temporal/service-health evidence and calibration rather than hand-tuning one binary likelihood repeatedly.

## 21. Limitations

### 21.1 Simulation assumptions are not production frequencies

The priors and likelihoods are assumed for controlled experimentation. They are not learned from production CI.

### 21.2 Circularity of simulator and policy model

The simulator generates observations using the same likelihood model that the Bayesian policy assumes. Therefore the experiment evaluates policy behavior **under the assumed probabilistic world**. It does not validate whether those likelihoods are correct in reality.

An important future test is deliberate model misspecification and, eventually, held-out real CI data.

### 21.3 Binary evidence is oversimplified

Real CI diagnosis uses logs, stack traces, timing, dependency health, commit diffs, test history, runner metadata, and correlated signals. Collapsing these into independent binary checks is useful for a first controlled experiment but not sufficient for production diagnosis.

### 21.4 Independence is simplified

The current posterior update effectively treats observations according to the specified likelihood model. In reality, rerun behavior, history, code inspection, and reproduction can be correlated.

### 21.5 Consequence costs are assumptions

The 80/90 scale and response-specific costs are simulation units. They demonstrate how decision cost changes policy behavior; they do not represent real engineering costs.

### 21.6 Threshold sensitivity matters

The derived 47.06% threshold is principled relative to the stated costs, but the costs themselves are assumptions. The sensitivity experiment therefore remains necessary.

### 21.7 Small experiment size

600 cases per policy across five fixed seeds is enough for the cohort experiment and reproducibility requirement, but it is not enough to establish production-level statistical confidence.

## 22. External-data path

Credible external CI sources have been identified in `docs/data_sources.md`, including TravisTorrent, UniLoc, CI-Datasets/Rails, and Continuous Defect Prediction.

The correct future calibration pipeline is:

```text
External labeled CI data
        ↓
Validate the six-state taxonomy
        ↓
Estimate priors and evidence likelihoods
        ↓
Calibrate probabilities
        ↓
Hold out evaluation cases
        ↓
Run P0/P2/P3
        ↓
Compare simulation and empirical performance
```

No claim in this research file should be read as saying those datasets already validated the current probabilities.

## 23. Current conclusion

The strongest conclusion supported by the experiment is:

> **A probabilistic CI diagnosis agent can trade diagnostic effort against decision consequence, and value-aware evidence selection can materially change the efficiency/accuracy frontier. However, the best policy and threshold depend on consequence assumptions, and the current six-state binary evidence model is not sufficiently calibrated to support production claims.**

At the derived 47.06% threshold, P2 is the stronger policy in this simulation. At 60–70%, P3 becomes stronger on the combined efficiency/accuracy trade-off. This is why the paper should report the trade-off rather than claiming universal superiority.

The most important unresolved problem is the `other` state: the failures show that an agent can still become confidently specific when the available evidence does not justify specificity. That points directly to the next research step: richer evidence, calibration, abstention, and evaluation on held-out real CI failures.

## 24. AI-use and reproducibility note

AI assistance may be used for implementation review, mathematical checking, experiment design critique, and editing. The repository retains executable code, fixed seeds, case-level artifacts, decision records, failure analysis, and limitations so that the reported experiment can be independently rerun.
