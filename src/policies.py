from dataclasses import dataclass, field

from .belief_engine import information_gain, most_likely_cause, posterior_after_observation
from .simulator import (
    ACTION_COSTS,
    Cause,
    DERIVED_DECISION_THRESHOLD,
    LIKELIHOODS,
    RESPONSE_COSTS,
    Action,
)


@dataclass
class PolicyState:
    beliefs: dict
    actions_taken: list = field(default_factory=list)
    diagnostic_cost: int = 0


CAUSE_RESPONSES = {
    Cause.FLAKY_TEST: "rerun",
    Cause.CODE_REGRESSION: "prepare_revert_pr_for_human_review",
    Cause.EXTERNAL_DEPENDENCY: "wait_for_health_then_rerun_or_escalate",
    Cause.CI_INFRASTRUCTURE: "transient_rerun_or_human_review",
    Cause.TEST_DATA_STATE: "human_review_with_suggested_data_remediation",
    Cause.OTHER: "human_escalation",
}

# Derived from the simulation's consequence costs:
# p* = C_FP / (C_FP + C_FN) = 80 / (80 + 90) = 47.06%.
P2_THRESHOLD = DERIVED_DECISION_THRESHOLD
P3_THRESHOLD = DERIVED_DECISION_THRESHOLD

P2_ACTION_ORDER = [
    Action.RERUN,
    Action.SEARCH_HISTORY,
    Action.CHECK_DEPENDENCY,
    Action.LOCAL_REPRODUCTION,
    Action.INSPECT_CODE,
    Action.CHECK_DB,
]


def update_state(state: PolicyState, action: Action, positive: bool):
    state.beliefs = posterior_after_observation(state.beliefs, action, positive)
    state.actions_taken.append(action)
    state.diagnostic_cost += ACTION_COSTS[action]
    return state


def _terminal(cause, confidence):
    return {
        "type": "terminal",
        "cause": cause,
        "confidence": confidence,
        "response": CAUSE_RESPONSES[cause],
    }


def _terminal_loss(beliefs, predicted):
    """Expected response consequence of one terminal diagnosis."""
    return sum(
        probability * RESPONSE_COSTS[predicted][true_cause]
        for true_cause, probability in beliefs.items()
    )


def _best_terminal_loss(beliefs):
    choices = {cause: _terminal_loss(beliefs, cause) for cause in Cause}
    best = min(choices, key=choices.get)
    return choices[best], best


def expected_decision_value(beliefs, action):
    """Expected reduction in terminal consequence from one more check.

    This is decision value, not entropy reduction. If every possible result
    leaves the same best terminal response, the value is zero.
    """
    current_loss, _ = _best_terminal_loss(beliefs)
    p_positive = sum(
        beliefs[cause] * LIKELIHOODS[action][cause]
        for cause in Cause
    )
    positive_beliefs = posterior_after_observation(beliefs, action, True)
    negative_beliefs = posterior_after_observation(beliefs, action, False)
    expected_after = (
        p_positive * _best_terminal_loss(positive_beliefs)[0]
        + (1 - p_positive) * _best_terminal_loss(negative_beliefs)[0]
    )
    return current_loss - expected_after


def p0_decision(state: PolicyState):
    """Trivial baseline: no evidence, always choose the modal prior cause."""
    cause = max(state.beliefs, key=state.beliefs.get)
    return _terminal(cause, state.beliefs[cause])


def p2_decision(state: PolicyState, threshold=None):
    """Threshold policy using the derived consequence threshold."""
    threshold = P2_THRESHOLD if threshold is None else threshold
    cause = most_likely_cause(state.beliefs)
    confidence = state.beliefs[cause]

    if confidence >= threshold:
        return _terminal(cause, confidence)

    for action in P2_ACTION_ORDER:
        if action not in state.actions_taken:
            return {
                "type": "diagnostic",
                "action": action,
                "cause": cause,
                "confidence": confidence,
            }

    return _terminal(cause, confidence)


def p3_decision(state: PolicyState, threshold=None):
    """Adaptive policy: EIG/cost ranking plus decision-value stopping."""
    threshold = P3_THRESHOLD if threshold is None else threshold
    cause = most_likely_cause(state.beliefs)
    confidence = state.beliefs[cause]

    if confidence >= threshold:
        return _terminal(cause, confidence)

    candidates = [a for a in Action if a not in state.actions_taken]
    if not candidates:
        return _terminal(cause, confidence)

    eig_scores = {
        a: information_gain(state.beliefs, a) / ACTION_COSTS[a]
        for a in candidates
    }
    value_scores = {
        a: expected_decision_value(state.beliefs, a)
        for a in candidates
    }

    # EIG/cost ranks the candidate; decision value is the stop gate. If the
    # best-ranked check cannot recover more consequence value than it costs,
    # stop rather than asking merely to reduce entropy.
    best_action = max(eig_scores, key=eig_scores.get)
    if value_scores[best_action] <= ACTION_COSTS[best_action]:
        return _terminal(cause, confidence)

    return {
        "type": "diagnostic",
        "action": best_action,
        "score": eig_scores[best_action],
        "decision_value": value_scores[best_action],
        "cause": cause,
        "confidence": confidence,
        "scores": eig_scores,
        "decision_values": value_scores,
    }
