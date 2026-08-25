from dataclasses import dataclass, field

from .belief_engine import information_gain, most_likely_cause, posterior_after_observation
from .simulator import Action, Cause, ACTION_COSTS


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

# Operational commitment threshold used by both adaptive policies. It is a
# v0.1 parameter and must be stress-tested/tuned in the final experiment;
# it is not claimed to be an empirical universal threshold.
P2_THRESHOLD = 0.70
P3_THRESHOLD = P2_THRESHOLD

P2_ACTION_ORDER = [
    Action.RERUN,
    Action.SEARCH_HISTORY,
    Action.CHECK_DEPENDENCY,
    Action.LOCAL_REPRODUCTION,
    Action.INSPECT_CODE,
    Action.CHECK_DB,
]


def update_state(state: PolicyState, action: Action, positive: bool):
    state.beliefs = posterior_after_observation(
        state.beliefs, action, positive
    )
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


def p2_decision(state: PolicyState):
    cause = most_likely_cause(state.beliefs)
    confidence = state.beliefs[cause]

    if confidence >= P2_THRESHOLD:
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


def p3_decision(state: PolicyState):
    """Choose the unused action with maximum EIG per diagnostic cost.

    P3 uses the same explicit commitment threshold as P2 so the comparison
    isolates the value of adaptive action selection rather than silently
    changing the stopping criterion.
    """
    cause = most_likely_cause(state.beliefs)
    confidence = state.beliefs[cause]

    if confidence >= P3_THRESHOLD:
        return _terminal(cause, confidence)

    candidates = [
        action for action in Action if action not in state.actions_taken
    ]
    if not candidates:
        return _terminal(cause, confidence)

    scores = {
        action: information_gain(state.beliefs, action) / ACTION_COSTS[action]
        for action in candidates
    }
    best_action = max(scores, key=scores.get)

    return {
        "type": "diagnostic",
        "action": best_action,
        "score": scores[best_action],
        "cause": cause,
        "confidence": confidence,
        "scores": scores,
    }
