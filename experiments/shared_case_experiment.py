"""Fair P0/P2/P3 comparison on identical simulated cases.

Each case pre-generates a hidden cause and one observation outcome for every
available diagnostic action. Every policy therefore sees the same evidence
opportunities, removing random-stream bias.
"""

from dataclasses import dataclass
from statistics import mean
import csv
from pathlib import Path

from src.belief_engine import initial_beliefs, posterior_after_observation
from src.policies import PolicyState, p0_decision, p2_decision, p3_decision
from src.simulator import (
    ACTION_COSTS,
    Action,
    Cause,
    DERIVED_DECISION_THRESHOLD,
    LIKELIHOODS,
    Simulator,
    decision_consequence,
)

NUM_CASES = 120
SEEDS = (2026, 2027, 2028, 2029, 2030)


@dataclass(frozen=True)
class SharedCase:
    case_id: str
    true_cause: Cause
    observations: dict


def generate_cases(seed):
    simulator = Simulator(seed=seed)
    cases = []
    for index in range(NUM_CASES):
        case = simulator.new_case()
        observations = {}
        for action in Action:
            p = LIKELIHOODS[action][case.true_cause]
            observations[action] = simulator.random.random() < p
        cases.append(SharedCase(f"{seed}-{index + 1}", case.true_cause, observations))
    return cases


def run_policy(cases, policy_name, threshold=DERIVED_DECISION_THRESHOLD):
    results = []
    for case in cases:
        beliefs = initial_beliefs()
        actions = []
        observations_seen = []
        cost = 0

        # P0 is deliberately trivial: it sees no evidence and always chooses
        # the modal prior cause. This is the cohort's required no-evidence baseline.
        if policy_name == "P0":
            state = PolicyState(beliefs, actions, cost)
            decision = p0_decision(state)
            predicted = decision["cause"]
            confidence = decision["confidence"]
        else:
            for _ in range(len(Action)):
                state = PolicyState(beliefs, actions, cost)
                if policy_name == "P2":
                    decision = p2_decision(state, threshold=threshold)
                elif policy_name == "P3":
                    decision = p3_decision(state, threshold=threshold)
                else:
                    raise ValueError(policy_name)

                if decision["type"] == "terminal":
                    break

                action = decision["action"]
                observation = case.observations[action]
                beliefs = posterior_after_observation(beliefs, action, observation)
                actions.append(action)
                observations_seen.append(
                    f"{action.value}={'PASS' if observation else 'FAIL'}"
                )
                cost += ACTION_COSTS[action]

            predicted = max(beliefs, key=beliefs.get)
            confidence = beliefs[predicted]

        consequence_cost = decision_consequence(case.true_cause, predicted)
        results.append({
            "case_id": case.case_id,
            "true_cause": case.true_cause.value,
            "predicted_cause": predicted.value,
            "confidence": confidence,
            "correct": predicted == case.true_cause,
            "diagnostic_cost": cost,
            "consequence_cost": consequence_cost,
            "decision_cost": cost + consequence_cost,
            "actions": len(actions),
            "action_sequence": ">".join(a.value for a in actions),
            "observations": ";".join(observations_seen),
            "escalated": predicted != Cause.FLAKY_TEST,
        })
    return results


def summarize(results):
    return {
        "accuracy": mean(r["correct"] for r in results),
        "mean_diagnostic_cost": mean(r["diagnostic_cost"] for r in results),
        "mean_decision_cost": mean(r["decision_cost"] for r in results),
        "mean_diagnostic_actions": mean(r["actions"] for r in results),
        "escalation_rate": mean(r["escalated"] for r in results),
    }


def save_case_level(results, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)


def confusion_matrix(results):
    causes = [c.value for c in Cause]
    matrix = {actual: {pred: 0 for pred in causes} for actual in causes}
    for row in results:
        matrix[row["true_cause"]][row["predicted_cause"]] += 1
    return matrix


def run_all(threshold=DERIVED_DECISION_THRESHOLD, output_dir="results/generated"):
    output = {}
    for seed in SEEDS:
        cases = generate_cases(seed)
        for policy in ("P0", "P2", "P3"):
            results = run_policy(cases, policy, threshold)
            output[(seed, policy)] = summarize(results)
            save_case_level(results, Path(output_dir) / f"cases_{seed}_{policy}.csv")
    return output


def print_summary(threshold=DERIVED_DECISION_THRESHOLD):
    output = run_all(threshold)
    for policy in ("P0", "P2", "P3"):
        rows = [output[(seed, policy)] for seed in SEEDS]
        print(policy, {k: mean(row[k] for row in rows) for k in rows[0]})


if __name__ == "__main__":
    print_summary()
