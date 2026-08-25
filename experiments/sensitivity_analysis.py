"""Sensitivity analysis for the CI diagnosis policy experiment.

This experiment varies the P2/P3 commitment threshold and records results
across independent simulator seeds. It is intentionally a robustness study:
we do not treat the 70% threshold or current likelihood assumptions as facts.
"""

from statistics import mean

from src.belief_engine import initial_beliefs, posterior_after_observation
from src.policies import PolicyState, p2_decision, p3_decision
from src.simulator import ACTION_COSTS, Action, Cause, Simulator

NUM_CASES = 120
SEEDS = (2026, 2027, 2028, 2029, 2030)
THRESHOLDS = (0.60, 0.70, 0.80)


def run_policy(policy_name, threshold, seed):
    simulator = Simulator(seed=seed)
    results = []

    for _ in range(NUM_CASES):
        case = simulator.new_case()
        beliefs = initial_beliefs()
        actions = []
        cost = 0
        escalated = False

        for _step in range(len(Action)):
            state = PolicyState(beliefs=beliefs, actions_taken=actions, diagnostic_cost=cost)

            if policy_name == "P2":
                decision = p2_decision(state, threshold=threshold)
            else:
                decision = p3_decision(state, threshold=threshold)

            if decision["type"] == "terminal":
                predicted = decision["cause"]
                escalated = predicted in {Cause.TEST_DATA_STATE, Cause.OTHER}
                break

            action = decision["action"]
            observation = simulator.observe(case, action)
            beliefs = posterior_after_observation(beliefs, action, observation)
            actions.append(action)
            cost += ACTION_COSTS[action]
        else:
            predicted = max(beliefs, key=beliefs.get)
            escalated = True

        results.append((predicted == case.true_cause, cost, len(actions), escalated))

    return {
        "accuracy": mean(r[0] for r in results),
        "mean_cost": mean(r[1] for r in results),
        "mean_actions": mean(r[2] for r in results),
        "escalation_rate": mean(r[3] for r in results),
    }


def main():
    for policy in ("P2", "P3"):
        for threshold in THRESHOLDS:
            runs = [run_policy(policy, threshold, seed) for seed in SEEDS]
            print(policy, threshold, {
                metric: mean(run[metric] for run in runs)
                for metric in runs[0]
            })


if __name__ == "__main__":
    main()
