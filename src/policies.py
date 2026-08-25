from dataclasses import dataclass, field

from .belief_engine import information_gain, most_likely_cause, posterior_after_observation
from .simulator import Action, Cause, ACTION_COSTS


@dataclass
class PolicyState:
    beliefs: dict
    actions_taken: list = field(default_factory=list)
    diagnostic_cost: int = 0


# Cause-specific terminal responses defined during the research process.
CAUSE_RESPONSES = {
    Cause.FLAKY_TEST: "rerun",
    Cause.CODE_REGRESSION: "prepare_revert_pr_for_human_review",
    Cause.EXTERNAL_DEPENDENCY: "wait_for_health_then_rerun_or_escalate",
    Cause.CI_INFRASTRUCTURE: "transient_rerun_or_human_review",
    Cause.TEST_DATA_STATE: "human_review_with_suggested_data_remediation",
    Cause.OTHER: "human_escalation",
}


# P2: evidence-driven threshold policy.
# This is intentionally simple and interpretable. It commits to a cause-specific
# response once the leading posterior reaches the threshold; otherwise it asks
# a predefined diagnostic question.
P2_THRESHOLD = 0.70

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


def p2_decision(state: PolicyState):
    cause = most_likely_cause(state.beliefs)
    confidence = state.beliefs[cause]

    if confidence >= P2_THRESHOLD:
        return {
            "type": "terminal",
            "cause": cause,
            "confidence": confidence,
            "response": CAUSE_RESPONSES[cause],
        }

    for action in P2_ACTION_ORDER:
        if action not in state.actions_taken:
            return {
                "type": "diagnostic",
                "action": action,
                "cause": cause,
                "confidence": confidence,
            }

    return {
        "type": "terminal",
        "cause": cause,
        "confidence": confidence,
        "response": CAUSE_RESPONSES[cause],
    }


# P3: choose the unused action with the highest expected information gain per
# unit diagnostic cost. If no unused action has positive value, stop.
def p3_decision(state: PolicyState):
    candidates = [
        action
        for action in Action
        if action not in state.actions_taken
    ]

    if not candidates:
        cause = most_likely_cause(state.beliefs)
        return {
            "type": "terminal",
            "cause": cause,
            "confidence": state.beliefs[cause],
            "response": CAUSE_RESPONSES[cause],
        }

    scores = {
        action: information_gain(state.beliefs, action) / ACTION_COSTS[action]
        for action in candidates
    }
    best_action = max(scores, key=scores.get)

    if scores[best_action] <= 0:
        cause = most_likely_cause(state.beliefs)
        return {
            "type": "terminal",
            "cause": cause,
            "confidence": state.beliefs[cause],
            "response": CAUSE_RESPONSES[cause],
        }

    return {
        "type": "diagnostic",
        "action": best_action,
        "score": scores[best_action],
        "cause": most_likely_cause(state.beliefs),
        "confidence": state.beliefs[most_likely_cause(state.beliefs)],
        "scores": scores,
    }
