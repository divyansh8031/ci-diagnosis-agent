"""Reproducible P0/P2/P3 policy comparison.

This is the first 100+ case experiment harness. It intentionally keeps the
hidden cause inside the simulator only; policies receive observations and
update beliefs through the belief engine.
"""

from dataclasses import dataclass

from src.belief_engine import initial_beliefs, posterior_after_observation
from src.policies import PolicyState, p2_decision, p3_decision
from src.simulator import Action, Cause, Simulator

NUM_CASES = 120
SEED = 2026
MAX_DIAGNOSTIC_STEPS = len(Action)


@dataclass
class Result:
    correct: bool
    diagnostic_cost: int
    diagnostic_actions: int
    escalated: bool
    predicted: Cause


def p0_next_action(actions_taken):
    """Fixed sequence baseline: the same action order for every case."""
    order = list(Action)
    for action in order:
        if action not in actions_taken:
            return action
    return None


def terminal_result(case, predicted, cost, actions, escalated):
    return Result(
        correct=predicted == case.true_cause,
        diagnostic_cost=cost,
        diagnostic_actions=len(actions),
        escalated=escalated,
        predicted=predicted,
    )


def run_policy(simulator, policy_name):
    results = []

    for _ in range(NUM_CASES):
        case = simulator.new_case()
        beliefs = initial_beliefs()
        actions = []
        cost = 0

        for _step in range(MAX_DIAGNOSTIC_STEPS):
            state = PolicyState(
                beliefs=beliefs,
                actions_taken=actions,
                diagnostic_cost=cost,
            )

            if policy_name == "P0":
                action = p0_next_action(actions)
                if action is None:
                    break
            elif policy_name == "P2":
                decision = p2_decision(state)
                if decision["type"] == "terminal":
                    cause = decision["cause"]
                    results.append(
                        terminal_result(
                            case,
                            cause,
                            cost,
                            actions,
                            cause in {Cause.TEST_DATA_STATE, Cause.OTHER},
                        )
                    )
                    break
                action = decision["action"]
            elif policy_name == "P3":
                decision = p3_decision(state)
                if decision["type"] == "terminal":
                    cause = decision["cause"]
                    results.append(
                        terminal_result(
                            case,
                            cause,
                            cost,
                            actions,
                            cause in {Cause.TEST_DATA_STATE, Cause.OTHER},
                        )
                    )
                    break
                action = decision["action"]
            else:
                raise ValueError(policy_name)

            positive = simulator.observe(case, action)
            beliefs = posterior_after_observation(beliefs, action, positive)
            actions.append(action)
            cost += simulator_action_cost(action)
        else:
            predicted = max(beliefs, key=beliefs.get)
            results.append(
                terminal_result(case, predicted, cost, actions, True)
            )

    return results


def simulator_action_cost(action):
    from src.simulator import ACTION_COSTS
    return ACTION_COSTS[action]


def summarize(results):
    n = len(results)
    return {
        "cases": n,
        "accuracy": sum(r.correct for r in results) / n,
        "mean_diagnostic_cost": sum(r.diagnostic_cost for r in results) / n,
        "mean_diagnostic_actions": sum(r.diagnostic_actions for r in results) / n,
        "escalation_rate": sum(r.escalated for r in results) / n,
    }


def main():
    for policy_name in ("P0", "P2", "P3"):
        simulator = Simulator(seed=SEED)
        results = run_policy(simulator, policy_name)
        print(policy_name, summarize(results))


if __name__ == "__main__":
    main()
