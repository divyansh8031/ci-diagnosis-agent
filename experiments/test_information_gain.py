from math import isclose

from src.belief_engine import entropy, information_gain, initial_beliefs
from src.policies import PolicyState, expected_decision_value, p0_decision, p3_decision
from src.simulator import Action, C_FP, C_FN, Cause, DERIVED_DECISION_THRESHOLD


def test_information_gain_is_non_negative():
    beliefs = initial_beliefs()
    for action in Action:
        assert information_gain(beliefs, action) >= 0


def test_information_gain_is_entropy_reduction():
    beliefs = initial_beliefs()
    prior_entropy = entropy(beliefs)

    for action in Action:
        gain = information_gain(beliefs, action)
        assert gain <= prior_entropy


def test_cost_adjusted_information_gain_uses_locked_costs():
    beliefs = initial_beliefs()
    gains = {action: information_gain(beliefs, action) for action in Action}

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


def test_threshold_is_derived_from_consequence_costs():
    expected = C_FP / (C_FP + C_FN)
    assert isclose(DERIVED_DECISION_THRESHOLD, expected, rel_tol=1e-12)
    assert isclose(DERIVED_DECISION_THRESHOLD, 8 / 17, rel_tol=1e-12)


def test_p0_is_no_evidence_modal_prior_baseline():
    state = PolicyState(initial_beliefs())
    decision = p0_decision(state)
    assert decision["type"] == "terminal"
    assert decision["cause"] == Cause.CODE_REGRESSION
    assert state.actions_taken == []
    assert state.diagnostic_cost == 0


def test_decision_value_is_non_negative_for_available_checks():
    beliefs = initial_beliefs()
    for action in Action:
        assert expected_decision_value(beliefs, action) >= -1e-12


def test_p3_has_a_decision_value_stop_gate():
    state = PolicyState(initial_beliefs())
    decision = p3_decision(state)
    assert decision["type"] in {"diagnostic", "terminal"}
    if decision["type"] == "diagnostic":
        assert decision["decision_value"] > 0
        assert decision["action"] in set(Action)


if __name__ == "__main__":
    test_information_gain_is_non_negative()
    test_information_gain_is_entropy_reduction()
    test_cost_adjusted_information_gain_uses_locked_costs()
    test_threshold_is_derived_from_consequence_costs()
    test_p0_is_no_evidence_modal_prior_baseline()
    test_decision_value_is_non_negative_for_available_checks()
    test_p3_has_a_decision_value_stop_gate()
    print("Information-gain and policy validation: PASS")
