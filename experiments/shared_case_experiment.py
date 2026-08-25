"""Fair P0/P2/P3 comparison on identical simulated cases.

Each case pre-generates a hidden cause and one observation outcome for every
available diagnostic action. Every policy therefore sees the same evidence
opportunities, removing the random-stream bias that occurs when policies
consume different numbers of random draws.
"""

from dataclasses import dataclass
from statistics import mean

from src.belief_engine import initial_beliefs, posterior_after_observation
from src.policies import PolicyState, p2_decision, p3_decision
from src.simulator import ACTION_COSTS, Action, Cause, LIKELIHOODS, PRIORS, Simulator

NUM_CASES = 120
SEEDS = (2026, 2027, 2028, 2029, 2030)


@dataclass(frozen=True)
class SharedCase:
    true_cause: Cause
    observations: dict


def generate_cases(seed):
    simulator = Simulator(seed=seed)
    cases = []
    for _ in range(NUM_CASES):
        case = simulator.new_case()
        observations = {}
        for action in Action:
            p = LIKELIHOODS[action][case.true_cause]
            observations[action] = simulator.random.random() < p
        cases.append(SharedCase(case.true_cause, observations))
    return cases


def run_policy(cases, policy_name, threshold=0.70):
    results = []
    for case in cases:
        beliefs = initial_beliefs()
        actions = []
        cost = 0
        for _ in range(len(Action)):
            state = PolicyState(beliefs, actions, cost)
            if policy_name == "P0":
                candidates = [a for a in Action if a not in actions]
                if not candidates:
                    break
                action = candidates[0]
            elif policy_name == "P2":
                decision = p2_decision(state, threshold=threshold)
                if decision["type"] == "terminal":
                    break
                action = decision["action"]
            elif policy_name == "P3":
                decision = p3_decision(state, threshold=threshold)
                if decision["type"] == "terminal":
                    break
                action = decision["action"]
            else:
                raise ValueError(policy_name)

            beliefs = posterior_after_observation(
                beliefs, action, case.observations[action]
            )
            actions.append(action)
            cost += ACTION_COSTS[action]
        predicted = max(beliefs, key=beliefs.get)
        escalated = predicted in {Cause.TEST_DATA_STATE, Cause.OTHER}
        results.append((predicted == case.true_cause, cost, len(actions), escalated))
    return results


def summarize(results):
    return {
        "accuracy": mean(r[0] for r in results),
        "mean_diagnostic_cost": mean(r[1] for r in results),
        "mean_diagnostic_actions": mean(r[2] for r in results),
        "escalation_rate": mean(r[3] for r in results),
    }


def run_all(threshold=0.70):
    output = {}
    for seed in SEEDS:
        cases = generate_cases(seed)
        for policy in ("P0", "P2", "P3"):
            output[(seed, policy)] = summarize(run_policy(cases, policy, threshold))
    return output


def print_summary(threshold=0.70):
    output = run_all(threshold)
    for policy in ("P0", "P2", "P3"):
        rows = [output[(seed, policy)] for seed in SEEDS]
        print(policy, {k: mean(row[k] for row in rows) for k in rows[0]})


if __name__ == "__main__":
    print_summary()
