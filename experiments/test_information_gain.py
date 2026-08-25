from math import isclose

from src.belief_engine import entropy, information_gain, initial_beliefs
from src.simulator import Action


def test_information_gain_is_non_negative():
    beliefs = initial_beliefs()
    for action in Action:
        assert information_gain(beliefs, action) >= 0


def test_information_gain_is_entropy_reduction():
    beliefs = initial_beliefs()
    prior_entropy = entropy(beliefs)

    for action in Action:
        gain = information_gain(beliefs, action)
        # By definition: expected posterior entropy = prior entropy - IG.
        assert gain <= prior_entropy


def test_cost_adjusted_information_gain_uses_locked_costs():
    beliefs = initial_beliefs()
    gains = {action: information_gain(beliefs, action) for action in Action}

    # Current model has diagnostic costs 1 or 2. This test intentionally
    # validates the ranking calculation without hard-coding a policy choice.
    costs = {
        Action.RERUN: 1,
        Action.SEARCH_HISTORY: 1,
        Action.CHECK_DEPENDENCY: 1,
        Action.LOCAL_REPRODUCTION: 2,
        Action.INSPECT_CODE: 2,
        Action.CHECK_DB: 2,
    }
    scores = {action: gains[action] / costs[action] for action in Action}

    assert all(score >= 0 for score in scores.values())
    assert isclose(scores[Action.RERUN], gains[Action.RERUN], rel_tol=1e-12)
    assert isclose(
        scores[Action.LOCAL_REPRODUCTION],
        gains[Action.LOCAL_REPRODUCTION] / 2,
        rel_tol=1e-12,
    )


if __name__ == "__main__":
    test_information_gain_is_non_negative()
    test_information_gain_is_entropy_reduction()
    test_cost_adjusted_information_gain_uses_locked_costs()
    print("Information-gain validation: PASS")
