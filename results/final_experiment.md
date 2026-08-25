# Final CI Diagnosis Experiment

## Design

The comparison uses identical simulated cases for P0, P2 and P3. Each run contains 120 cases and five seeds (2026–2030). The hidden cause is sampled from the stated prior distribution, and potential observations are generated once per case/action and reused by every policy.

Relative diagnostic costs are simulation units: 1 for cheap automated checks and 2 for heavier automated diagnostics. Human review/intervention costs (8/9) are part of the operational model but are not charged as diagnostic actions in the policy-selection experiment.

P0 is the fixed-sequence baseline. P2 is the threshold/evidence-driven policy. P3 selects the unused diagnostic action with maximum expected information gain per unit diagnostic cost. P2 and P3 use the same commitment threshold so the comparison isolates action-selection behavior.

## Multi-seed results at 70% threshold

| Policy | Accuracy | Mean diagnostic cost | Mean actions | Escalation |
|---|---:|---:|---:|---:|
| P0 | 73.50% | 9.00 | 6.00 | 5.33% |
| P2 | 69.00% | 5.86 | 4.30 | 4.50% |
| P3 | 71.83% | 5.25 | 3.57 | 4.00% |

Compared with P0, P3 reduces mean diagnostic cost by about 41.7% and mean diagnostic actions by about 40.4%, while losing about 1.67 percentage points of accuracy under this simulation model.

## Threshold sensitivity

| Threshold | Policy | Accuracy | Mean cost | Mean actions |
|---:|---|---:|---:|---:|
| 60% | P2 | 66.17% | 4.53 | 3.63 |
| 60% | P3 | 72.50% | 4.60 | 3.19 |
| 70% | P2 | 71.00% | 5.83 | 4.28 |
| 70% | P3 | 73.17% | 5.36 | 3.64 |
| 80% | P2 | 75.17% | 6.75 | 4.88 |
| 80% | P3 | 74.50% | 6.09 | 4.19 |

## Interpretation

P3 does not universally dominate P2. At 60% and 70%, P3 has the better simulated accuracy/cost trade-off. At 80%, P2 has slightly higher accuracy while P3 remains cheaper. Therefore the defensible claim is not that EIG-per-cost is universally superior; it is that adaptive information-value-based action selection can reduce diagnostic work while preserving competitive accuracy under the stated assumptions.

These are simulated results, not production evidence. The priors, likelihoods, action costs and threshold are assumptions and must be reported as such.

## Reproducibility

Run:

```bash
python experiments/shared_case_experiment.py
python experiments/sensitivity_analysis.py
```

The shared-case design is required for fair policy comparison: different policies may take different numbers of actions, so they must not consume independent random streams and thereby receive different hidden cases/evidence.
