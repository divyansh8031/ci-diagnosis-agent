"""Generate final case-level evidence for the Week 1 rubric."""

from pathlib import Path
import json
from statistics import mean

from experiments.shared_case_experiment import (
    SEEDS,
    confusion_matrix,
    generate_cases,
    run_policy,
    summarize,
)
from src.simulator import DERIVED_DECISION_THRESHOLD

OUT = Path("results/generated")


def main(threshold=DERIVED_DECISION_THRESHOLD):
    OUT.mkdir(parents=True, exist_ok=True)
    aggregate = {}
    errors = []

    for seed in SEEDS:
        cases = generate_cases(seed)
        for policy in ("P0", "P2", "P3"):
            results = run_policy(cases, policy, threshold)
            aggregate.setdefault(policy, []).append(summarize(results))
            (OUT / f"confusion_{seed}_{policy}.json").write_text(
                json.dumps(confusion_matrix(results), indent=2), encoding="utf-8"
            )
            for row in results:
                if not row["correct"]:
                    errors.append({"policy": policy, "seed": seed, **row})

    summary = {
        policy: {
            metric: mean(row[metric] for row in rows)
            for metric in rows[0]
        }
        for policy, rows in aggregate.items()
    }
    (OUT / "aggregate_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (OUT / "experiment_config.json").write_text(
        json.dumps({
            "threshold": threshold,
            "threshold_source": "C_FP / (C_FP + C_FN)",
            "seeds": list(SEEDS),
            "cases_per_seed": 120,
            "policies": ["P0", "P2", "P3"],
            "same_shared_cases": True,
        }, indent=2),
        encoding="utf-8",
    )

    selected = []
    seen = set()
    for row in sorted(errors, key=lambda r: r["decision_cost"], reverse=True):
        key = (row["policy"], row["true_cause"])
        if key not in seen:
            selected.append(row)
            seen.add(key)
        if len(selected) == 5:
            break
    (OUT / "five_error_cases.json").write_text(
        json.dumps(selected, indent=2), encoding="utf-8"
    )

    highest = max(errors, key=lambda r: r["decision_cost"])
    (OUT / "highest_cost_error.json").write_text(
        json.dumps(highest, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print("Selected five errors:", len(selected))
    print("Highest-cost error:", highest["case_id"], highest["policy"], highest["decision_cost"])


if __name__ == "__main__":
    main()
