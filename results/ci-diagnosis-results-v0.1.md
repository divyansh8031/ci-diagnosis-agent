# CI Diagnosis Agent — Results v0.1

## Experiment

The v0.1 experiment compares two policies on 48 simulated CI integration-test diagnosis cases.

- **P0 — Fixed sequence:** follows a predetermined diagnostic order.
- **P1 — Evidence driven:** selects the next action from the current belief state using expected information gain relative to assumed action cost.

The hidden true cause is available to the simulator for evaluation but is not treated as directly observable by the agent.

## Results

| Metric | P0 | P1 |
|---|---:|---:|
| Cases | 48 | 48 |
| Correct diagnoses | 5 | 13 |
| Accuracy | 10.4% | 27.1% |
| Escalations | 35 | 29 |
| Escalation rate | 72.9% | 60.4% |
| Average relative diagnostic cost | 13.96 | 11.42 |
| Average actions | 5.50 | 4.94 |

Within this simulator, P1 performed better than P0 across the measured metrics. This is a conditional simulation result, not evidence that P1 will outperform a fixed sequence in real CI systems.

## P1 per-class result

Eight cases were generated for each hidden state.

| Hidden state | Correct P1 diagnoses |
|---|---:|
| Code regression | 6 / 8 |
| Flaky test | 7 / 8 |
| External dependency | 0 / 8 |
| CI infrastructure | 0 / 8 |
| Test-data/state | 0 / 8 |
| Other | 0 / 8 |

The strongest current discrimination is for code-regression and flaky-test cases. Several other states are poorly distinguished by the current simulated observation model.

## Five-outcome review

The first five P1 non-correct outcomes were primarily escalations rather than false diagnoses.

### Case 1
- True state: CI infrastructure
- P1: Escalate
- Cost: 15 relative units
- Failure condition: available diagnostic actions were exhausted without sufficient evidence to cross the confidence threshold.

### Case 2
- True state: External dependency
- P1: Escalate
- Cost: 15 relative units
- Failure condition: dependency evidence was not sufficiently discriminating under the current likelihood model.

### Case 3
- True state: Other
- P1: Escalate
- Cost: 15 relative units
- Interpretation: escalation is not necessarily undesirable because the catch-all hypothesis is intentionally weakly specified.

### Case 4
- True state: CI infrastructure
- P1: Escalate
- Cost: 15 relative units
- Failure condition: infrastructure remained insufficiently distinguishable after available actions.

### Case 5
- True state: CI infrastructure
- P1: Escalate
- Cost: 15 relative units
- Failure condition: same infrastructure-evidence limitation.

## Cost interpretation

The 15-unit value is the sum of the assumed relative costs of the six actions used before escalation:

- Search history = 1
- Rerun = 1
- Check dependency = 2
- Reproduce locally = 3
- Inspect code = 4
- Check DB/data = 4

Therefore: **1 + 1 + 2 + 3 + 4 + 4 = 15**.

These are relative simulation units, not minutes or money.

## Main finding

The v0.1 simulation demonstrates that an evidence-driven policy can be implemented and compared with a fixed diagnostic sequence. P1 shows better measured outcomes in this simulated environment, while also exposing a concrete weakness: the current evidence model does not sufficiently distinguish external-dependency, infrastructure, test-data/state and other failures.

## Limitations

1. Priors and likelihoods are illustrative and not calibrated.
2. Action costs are qualitative assumptions.
3. Cases are simulated rather than drawn from a labeled production CI dataset.
4. Historical comparability is not validated.
5. The 80% confidence threshold is a prototype parameter.
6. P2, a separate historical-aware policy, is not claimed as completed in v0.1.

## Conclusion

The current result supports continuing the uncertainty-aware diagnosis approach as a prototype research direction. It does not establish real-world superiority. Future work should validate the observation model, costs and priors with appropriate evidence and separately evaluate a historical-aware policy if required by the later research phase.
