# CI Diagnosis Agent

An uncertainty-aware agent for diagnosing CI integration-test failures under incomplete information.

## Week 1 status

The core Week 1 implementation and experiment are complete and reproducible. The repository contains the simulator, Bayesian belief engine, P0/P2/P3 policies, fair shared-case experiment, sensitivity harness, confusion matrices, case-level error analysis, architecture diagram, probability decision record, extension analysis, AI-review audit, Jupyter notebook, and LaTeX preprint.

The final verified GitHub Actions experiment used 5 fixed seeds (2026–2030) × 120 cases and evaluated all policies on the same pre-generated observation opportunities.

## Verified 70% results

| Policy | Accuracy | Mean diagnostic cost | Mean decision cost | Mean actions |
|---|---:|---:|---:|---:|
| P0 | 75.83% | 9.00 | 14.25 | 6.00 |
| P2 | 71.00% | 5.83 | 10.75 | 4.28 |
| P3 | 73.17% | 5.36 | 10.63 | 3.64 |

P3 is therefore more efficient than P0 under the current simulation assumptions, but it is not a universal winner over P2. Threshold sensitivity at 60%, 70%, and 80% is included in `results/final_results.md`.

## Policies

- **P0:** fixed diagnostic sequence baseline.
- **P2:** threshold policy; update beliefs and commit when the leading hypothesis reaches a configured threshold.
- **P3:** value-of-information proxy; select the unused action with highest expected information gain per unit diagnostic cost.

## Probability model

The simulation prior is 40% code regression, 30% flaky test, 10% external dependency, 10% CI infrastructure, 5% test-data/state, and 5% other. These are explicit simulation assumptions, not measured real-world frequencies.

Qualitative likelihood assumptions are mapped to 0.8 (often), 0.4 (sometimes), and 0.1 (rarely). Relative diagnostic costs are 1 for cheap automated checks and 2 for heavier diagnostics; human review/intervention are consequence classes of 8/9.

## Experiment and reproducibility

```bash
PYTHONPATH=. python experiments/test_simulator.py
PYTHONPATH=. python experiments/test_belief_engine.py
PYTHONPATH=. python experiments/test_failed_rerun.py
PYTHONPATH=. python experiments/test_information_gain.py
PYTHONPATH=. python experiments/shared_case_experiment.py
PYTHONPATH=. python experiments/sensitivity_analysis.py
PYTHONPATH=. python experiments/generate_report.py
```

GitHub Actions executes the same validation and experiment and uploads the complete case-level evidence artifact.

## Research artifacts

- `research/research-file.md`
- `results/final_results.md`
- `results/confusion_matrices.md`
- `docs/architecture.dot`
- `docs/probability_decision_record.md`
- `docs/extension_concepts.md`
- `docs/error_analysis.md`
- `docs/ai_review_log.md`
- `docs/data_sources.md`
- `paper/preprint.tex`
- `notebooks/experiment_results.ipynb`
- `experiments/shared_case_experiment.py`
- `experiments/sensitivity_analysis.py`
- `experiments/generate_report.py`

## Submission discipline

Simulation probabilities are not real-world frequencies. P3 is not described as universally superior. External datasets listed in `docs/data_sources.md` are references for calibration/validation context only; they were not used to generate the current 120-case simulation unless explicitly stated otherwise.

## AI use

AI assistance was used for terminology discovery, research-query generation, source discovery, explanation, reasoning checks, implementation support, simulation support, and document structuring. The project records accepted/rejected AI review comments and distinguishes AI assistance from the user's design decisions and from experiment evidence.
