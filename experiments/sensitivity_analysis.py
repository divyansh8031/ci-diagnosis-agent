"""Fair multi-seed threshold sensitivity analysis.

For each seed, one shared set of cases is generated and reused by P0/P2/P3.
The threshold is varied without changing the underlying cases.
"""

from statistics import mean
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.shared_case_experiment import generate_cases, run_policy, summarize, SEEDS
from src.simulator import DERIVED_DECISION_THRESHOLD

# The derived threshold is the center point. Lower/higher values test the
# sensitivity of the policy rather than replacing the derivation.
THRESHOLDS = (0.40, DERIVED_DECISION_THRESHOLD, 0.55, 0.70, 0.80)


def run():
    for threshold in THRESHOLDS:
        for policy in ("P2", "P3"):
            runs = []
            for seed in SEEDS:
                cases = generate_cases(seed)
                results = run_policy(cases, policy, threshold=threshold)
                runs.append(summarize(results))
            aggregate = {
                metric: mean(row[metric] for row in runs)
                for metric in runs[0]
            }
            print(policy, threshold, aggregate)


if __name__ == "__main__":
    run()
