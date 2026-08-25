# AI review log

This log records AI-assisted review performed on the repository before finalization. It distinguishes review comments from the user's design decisions and from empirical/simulation output.

## Review 1 — Model / policy correctness

- Reviewer: AI-assisted review
- Scope: priors, likelihood assumptions, Bayesian update, stopping rule, P2/P3 definitions.
- Accepted: keep priors and qualitative likelihood mapping as explicit simulation assumptions; keep P2 as threshold and P3 as EIG-per-cost; do not describe 70% as universally optimal.
- Rejected: treating a passing rerun as proof of flakiness; treating a recent code change as proof of regression; claiming EIG is equivalent to decision value.
- Changes made: probability decision record and preprint now state assumptions and limitations; P3 is described as a value-of-information proxy.

## Review 2 — Experiment validity

- Reviewer: AI-assisted review
- Scope: shared-case fairness, fixed seeds, baseline comparison, leakage, metrics.
- Accepted: pre-generate identical hidden cases and action observations for P0/P2/P3; use 5 fixed seeds × 120 cases; save case-level actions and predictions.
- Rejected: comparing policies using independent random streams, because policies consuming different numbers of draws would otherwise see different later cases.
- Changes made: added `experiments/shared_case_experiment.py`, fixed-seed validation, case-level evidence, and GitHub Actions execution.
- Validation result: simulator, belief-engine, failed-rerun, and information-gain checks all passed in the final-evidence workflow.

## Review 3 — Results / paper / reproducibility

- Reviewer: AI-assisted review
- Scope: unsupported claims, reproducibility, limitations, citations, AI-use disclosure.
- Accepted: report P3 as an efficiency/accuracy trade-off rather than a universal winner; include threshold sensitivity; report simulation assumptions and error cases.
- Rejected: presenting earlier exploratory numbers that were generated before the shared-case fairness correction; presenting simulation priors as real-world failure frequencies.
- Changes made: added `results/final_results.md`, populated `docs/error_analysis.md`, and recorded the final GitHub Actions artifact as the reproducibility evidence.

## Important disclosure

AI assistance was used for terminology discovery, research-query generation, source discovery, explanation, reasoning checks, implementation support, simulation support, and document structuring. The user's project decisions remain the source of the selected causes, priors, qualitative evidence assumptions, operational response boundaries, and research direction. Empirical/simulation claims are tied to executable artifacts rather than AI assertions.
