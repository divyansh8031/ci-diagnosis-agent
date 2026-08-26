"""Fair multi-seed threshold sensitivity and failure-driven retest.

For each seed, one shared set of cases is generated and reused by P0/P2/P3.
The threshold is varied without changing the underlying cases.

The retest deliberately changes only the DB likelihoods after the error analysis
found that a single positive DB signal could overwhelm dependency evidence.
It is a robustness/design experiment, not a replacement for the baseline model.
"""

from statistics import mean
import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.shared_case_experiment import generate_cases, run_policy, summarize, SEEDS
from src.belief_engine import entropy, posterior_after_observation
from src.simulator import Action, Cause, DERIVED_DECISION_THRESHOLD, LIKELIHOODS, PRIORS
from src.policies import expected_decision_value

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


def _generate_cases_with_likelihoods(seed, likelihoods):
    rng = random.Random(seed)
    cases = []
    for index in range(120):
        true_cause = rng.choices(
            list(PRIORS.keys()),
            weights=list(PRIORS.values()),
            k=1,
        )[0]
        observations = {
            action: rng.random() < likelihoods[action][true_cause]
            for action in Action
        }
        cases.append((f"{seed}-{index + 1}", true_cause, observations))
    return cases


def _run_retest_policy(cases, policy, threshold=0.60):
    """Run the same policy logic against the failure-driven likelihood model."""
    from experiments.shared_case_experiment import run_policy as baseline_run_policy
    from src.belief_engine import initial_beliefs
    from src.policies import PolicyState, p0_decision, p2_decision, p3_decision
    from src.simulator import ACTION_COSTS, Cause, decision_consequence

    results = []
    for case_id, true_cause, observations in cases:
        beliefs = initial_beliefs()
        actions = []
        cost = 0
        if policy == "P0":
            predicted = p0_decision(PolicyState(beliefs))["cause"]
        else:
            for _ in Action:
                state = PolicyState(beliefs, actions, cost)
                decision = p2_decision(state, threshold) if policy == "P2" else p3_decision(state, threshold)
                if decision["type"] == "terminal":
                    break
                action = decision["action"]
                positive = observations[action]
                # Recalculate the posterior with the alternative DB likelihoods.
                if action == Action.CHECK_DB:
                    p = sum(beliefs[c] * RETEST_LIKELIHOODS[action][c] for c in Cause)
                    if positive:
                        weights = {c: beliefs[c] * RETEST_LIKELIHOODS[action][c] for c in Cause}
                    else:
                        weights = {c: beliefs[c] * (1 - RETEST_LIKELIHOODS[action][c]) for c in Cause}
                    total = sum(weights.values())
                    beliefs = {c: w / total for c, w in weights.items()}
                else:
                    beliefs = posterior_after_observation(beliefs, action, positive)
                actions.append(action)
                cost += ACTION_COSTS[action]
            predicted = max(beliefs, key=beliefs.get)

        consequence = decision_consequence(true_cause, predicted)
        results.append({
            "correct": predicted == true_cause,
            "diagnostic_cost": cost,
            "decision_cost": cost + consequence,
            "actions": len(actions),
            "escalated": predicted != Cause.FLAKY_TEST,
        })
    return results


def _summary(results):
    return {
        "accuracy": mean(row["correct"] for row in results),
        "mean_diagnostic_cost": mean(row["diagnostic_cost"] for row in results),
        "mean_decision_cost": mean(row["decision_cost"] for row in results),
        "mean_diagnostic_actions": mean(row["actions"] for row in results),
        "escalation_rate": mean(row["escalated"] for row in results),
    }


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
            print("BASELINE", policy, threshold, aggregate)

    print("FAILURE-DRIVEN RETEST at threshold 0.60")
    for policy in ("P2", "P3"):
        runs = []
        for seed in SEEDS:
            cases = _generate_cases_with_likelihoods(seed, RETEST_LIKELIHOODS)
            runs.append(_summary(_run_retest_policy(cases, policy, threshold=0.60)))
        aggregate = {metric: mean(row[metric] for row in runs) for metric in runs[0]}
        print("RETEST", policy, aggregate)


if __name__ == "__main__":
    run()
