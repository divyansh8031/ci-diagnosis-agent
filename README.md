# CI Diagnosis Agent

An uncertainty-aware agent for diagnosing CI integration-test failures under incomplete information.

## Current Week 1 status

The repository now contains the simulator, Bayesian belief engine, P0/P2/P3 policies, fair shared-case experiment, sensitivity harness, architecture diagram, probability decision record, extension analysis, error-analysis protocol, AI-review audit, and LaTeX preprint draft.

The cohort framing treats the failure cause as hidden, evidence as observable signals, and diagnosis as sequential information gathering. The research notes explicitly warn against treating a passing rerun as proof of flakiness, a recent code change as proof of causality, or heuristic scores as calibrated probabilities.

## Policies

- **P0:** fixed diagnostic sequence baseline.
- **P2:** threshold policy; update beliefs and commit when the leading hypothesis reaches a configured threshold.
- **P3:** value-of-information proxy; select the unused action with highest expected information gain per unit diagnostic cost.

Historical failure comparison is retained as an extension because the research process promoted historical evidence to a first-class evidence source.

## Probability model

The simulation prior is 40% code regression, 30% flaky test, 10% external dependency, 10% CI infrastructure, 5% test-data/state, and 5% other. These are explicit simulation assumptions, not measured real-world frequencies.

Qualitative likelihood assumptions are mapped to 0.8 (often), 0.4 (sometimes), and 0.1 (rarely). Relative diagnostic costs are 1 for cheap automated checks and 2 for heavier diagnostics; human review/intervention are consequence classes of 8/9.

## Experiment

The fair experiment generates 120 cases for each fixed seed (2026–2030), pre-generates the observation opportunity for every action, and evaluates P0/P2/P3 on the same cases. The experiment saves case-level predictions and action sequences under `results/generated/` when executed.

Threshold sensitivity is evaluated at 60%, 70%, and 80%. The threshold is a tunable simulation parameter, not a universal empirical value.

## Reproducibility

Run locally:

```bash
PYTHONPATH=. python experiments/test_simulator.py
PYTHONPATH=. python experiments/test_belief_engine.py
PYTHONPATH=. python experiments/test_failed_rerun.py
PYTHONPATH=. python experiments/test_information_gain.py
PYTHONPATH=. python experiments/shared_case_experiment.py
PYTHONPATH=. python experiments/sensitivity_analysis.py
```

GitHub Actions runs the same checks and uploads case-level output as an artifact.

## Research artifacts

- `docs/architecture.dot`
- `docs/probability_decision_record.md`
- `docs/extension_concepts.md`
- `docs/error_analysis.md`
- `docs/ai_review_log.md`
- `docs/rubric_audit.md`
- `paper/preprint.tex`
- `notebooks/experiment_results.ipynb`
- `experiments/shared_case_experiment.py`
- `experiments/sensitivity_analysis.py`

## Important submission discipline

Do not treat the existing notebook/result tables as final empirical evidence until the current GitHub Actions run succeeds and its case-level artifact has been inspected. The final paper must include the actual confusion matrix, at least five case-level error analyses, highest-cost error, and completed AI-review record.

## AI use

AI assistance was used for terminology discovery, research-query generation, source discovery, explanation, implementation assistance, reasoning checks, simulation support, and document structuring. The researcher made the project/design judgments and should retain the distinction between personal decisions, external evidence, and AI-assisted implementation.
