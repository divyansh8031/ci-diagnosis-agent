# CI Diagnosis Agent

An uncertainty-aware agent for diagnosing CI integration-test failures under incomplete information.

## Week 1 status

**Research + prototype evaluation completed for v0.1.**

This repository documents the work completed during the Week 1 research process:

- Problem framed as hidden-state diagnosis under incomplete evidence.
- Competing failure hypotheses defined.
- Prior, likelihood, posterior, entropy, information gain and EIG/cost reasoning worked through.
- Relative diagnostic costs defined as explicit simulation assumptions.
- **P0:** fixed-sequence baseline.
- **P1:** evidence-driven policy that selects the next action from the current belief state using expected information gain relative to assumed cost.
- 48 simulated cases used for the v0.1 comparison.
- Policy decisions/predictions and evaluation metrics recorded.
- Five P1 non-correct outcomes reviewed, distinguishing escalation from incorrect diagnosis.
- Probability Decision Record created for a representative belief-update path.

## Key v0.1 result

Under the current simulation assumptions:

| Metric | P0 — Fixed sequence | P1 — Evidence driven |
|---|---:|---:|
| Cases | 48 | 48 |
| Correct diagnoses | 5 | 13 |
| Accuracy | 10.4% | 27.1% |
| Escalations | 35 | 29 |
| Escalation rate | 72.9% | 60.4% |
| Average relative diagnostic cost | 13.96 | 11.42 |
| Average actions | 5.50 | 4.94 |

These are **simulation results only**. The priors, likelihoods, relative costs, observation model and stopping threshold are prototype assumptions and are not calibrated real-world measurements.

## Important finding

P1 performed better than P0 across the measured metrics in this v0.1 simulation, but its evidence model poorly distinguished several hidden states. P1 correctly diagnosed 6/8 code-regression cases and 7/8 flaky-test cases, while it correctly diagnosed 0/8 cases for external dependency, CI infrastructure, test-data/state and other.

This limitation is retained as a research finding rather than hidden through post-hoc tuning.

## Core concepts

### P0 — fixed sequence

P0 follows a predetermined diagnostic sequence regardless of the current evidence.

### P1 — evidence driven

P1 asks what diagnostic action is most useful **given what is currently known**. It updates its belief after each observation and uses expected information gain relative to assumed action cost when selecting the next action.

### Probability model

The prototype uses:

`prior → evidence/likelihood → posterior → entropy → information gain → action selection`

The numerical values are explicitly treated as assumptions for simulation, not real-world failure frequencies.

## Reproducibility artifacts

The following artifacts are intended to document the completed work:

- `research/research-file.md` — research framing and hypotheses.
- `decisions/probability-decision-record.md` — representative probability decision record.
- `data/ci_diagnosis_experiment_48_cases.csv` — 48-case experiment records.
- `results/ci_diagnosis_results_summary_v0_1.md` — experiment results and error analysis.

## Limitations

- The experiment uses simulated rather than production-labeled CI failures.
- Probability values are illustrative and not calibrated.
- Relative action costs are qualitative assumptions, not measured money/time costs.
- The historical evidence model has not yet been validated against a suitable historical dataset.
- The 80% confidence threshold is a prototype parameter.
- P2, a separate historical-aware policy, is not claimed as completed in v0.1.

## AI-assisted workflow

AI assistance was used for research structuring, conceptual explanation, implementation assistance, simulation, calculation, review and drafting. The researcher made the problem/design judgments, challenged assumptions, reviewed the calculations and decided what claims could be made. Unverified claims and simulated results are explicitly labeled rather than presented as established real-world findings.

## Next work

The next phase is packaging and reproducibility: finalize the research record, probability decision record, experiment artifacts, results discussion and paper. Future work may validate the likelihood/cost model with practitioner or labeled CI evidence and separately evaluate the historical-aware P2 policy.
