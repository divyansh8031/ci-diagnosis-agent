"""Fair multi-seed threshold sensitivity and failure-driven retest.

For each seed, one shared set of cases is generated and reused by P0/P2/P3.
The threshold is varied without changing the underlying cases.

The retest deliberately changes only the DB likelihoods after the error analysis
found that a single positive DB signal could overwhelm dependency evidence.
It is a robustness/design experiment, not a replacement for the baseline model.
"""

from statistics import mean

from experiments.shared_case_experiment import generate_cases, run_policy, summarize, SEEDS
from src.simulator import Action, Cause, DERIVED_DECISION_THRESHOLD, LIKELIHOODS

# The derived threshold is the center point. Lower/higher values test the
# sensitivity of the policy rather than replacing the derivation.
THRESHOLDS = (0.40, DERIVED_DECISION_THRESHOLD, 0.55, 0.60, 0.70, 0.80)

# Failure-driven alternative: DB evidence is made more discriminative against
# external dependency, CI infrastructure, and flaky-test worlds. The baseline
# model remains unchanged; this is used only for the re-test.
RETEST_LIKELIHOODS = {action: dict(values) for action, values in LIKELIHOODS.items()}
RETEST_LIKELIHOODS[Action.CHECK_DB].update({
    Cause.EXTERNAL_DEPENDENCY: 0.0,
    Cause.CI_INFRASTRUCTURE: 0.02,
    Cause.FLAKY_TEST: 0.02,
})


def _run_model(threshold, likelihoods=None):
    """Run the normal experiment, optionally under a temporary likelihood model."""
    original = {action: dict(values) for action, values in LIKELIHOODS.items()}
    try:
        if likelihoods is not None:
            for action, values in likelihoods.items():
                LIKELIHOODS[action].clear()
                LIKELIHOODS[action].update(values)

        aggregates = {}
        for policy in ("P2", "P3"):
            runs = []
            for seed in SEEDS:
                cases = generate_cases(seed)
                runs.append(summarize(run_policy(cases, policy, threshold=threshold)))
            aggregates[policy] = {
                metric: mean(row[metric] for row in runs)
                for metric in runs[0]
            }
        return aggregates
    finally:
        for action, values in original.items():
            LIKELIHOODS[action].clear()
            LIKELIHOODS[action].update(values)


def run():
    for threshold in THRESHOLDS:
        for policy, aggregate in _run_model(threshold).items():
            print("BASELINE", policy, threshold, aggregate)

    print("FAILURE-DRIVEN RETEST at threshold 0.60")
    for policy, aggregate in _run_model(0.60, RETEST_LIKELIHOODS).items():
        print("RETEST", policy, aggregate)


if __name__ == "__main__":
    run()
