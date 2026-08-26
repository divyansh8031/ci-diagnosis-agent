from dataclasses import dataclass, field
from enum import Enum
import random


class Cause(Enum):
    CODE_REGRESSION = "code_regression"
    FLAKY_TEST = "flaky_test"
    EXTERNAL_DEPENDENCY = "external_dependency"
    CI_INFRASTRUCTURE = "ci_infrastructure"
    TEST_DATA_STATE = "test_data_state"
    OTHER = "other"


class Action(Enum):
    RERUN = "rerun"
    SEARCH_HISTORY = "search_history"
    CHECK_DEPENDENCY = "check_dependency"
    LOCAL_REPRODUCTION = "local_reproduction"
    INSPECT_CODE = "inspect_code"
    CHECK_DB = "check_db"


# Simulation priors agreed during the research process.
PRIORS = {
    Cause.CODE_REGRESSION: 0.40,
    Cause.FLAKY_TEST: 0.30,
    Cause.EXTERNAL_DEPENDENCY: 0.10,
    Cause.CI_INFRASTRUCTURE: 0.10,
    Cause.TEST_DATA_STATE: 0.05,
    Cause.OTHER: 0.05,
}

# Relative diagnostic costs. These are simulation units, not money or minutes.
ACTION_COSTS = {
    Action.RERUN: 1,
    Action.SEARCH_HISTORY: 1,
    Action.CHECK_DEPENDENCY: 1,
    Action.LOCAL_REPRODUCTION: 2,
    Action.INSPECT_CODE: 2,
    Action.CHECK_DB: 2,
}

# Decision-consequence units used by the policy experiment.
# 8 = human review/intervention; 9 = highest-consequence unknown/wrong automation.
HUMAN_REVIEW_COST = 8
HIGH_CONSEQUENCE_COST = 9

# The cohort threshold is derived from false-positive and false-negative costs,
# rather than selected as a round confidence number.
# p* = C_FP / (C_FP + C_FN)
C_FP = HUMAN_REVIEW_COST
C_FN = HIGH_CONSEQUENCE_COST
DERIVED_DECISION_THRESHOLD = C_FP / (C_FP + C_FN)  # 8 / 17 = 47.06%

# Probability of the positive observation given the hidden cause.
# Values come from the research assumptions:
# often=0.8, sometimes=0.4, rarely=0.1.
LIKELIHOODS = {
    Action.RERUN: {
        Cause.CODE_REGRESSION: 0.4,
        Cause.FLAKY_TEST: 0.8,
        Cause.EXTERNAL_DEPENDENCY: 0.4,
        Cause.CI_INFRASTRUCTURE: 0.1,
        Cause.TEST_DATA_STATE: 0.1,
        Cause.OTHER: 0.1,
    },
    Action.SEARCH_HISTORY: {
        Cause.CODE_REGRESSION: 0.4,
        Cause.FLAKY_TEST: 0.8,
        Cause.EXTERNAL_DEPENDENCY: 0.1,
        Cause.CI_INFRASTRUCTURE: 0.1,
        Cause.TEST_DATA_STATE: 0.1,
        Cause.OTHER: 0.1,
    },
    Action.CHECK_DEPENDENCY: {
        Cause.CODE_REGRESSION: 0.1,
        Cause.FLAKY_TEST: 0.4,
        Cause.EXTERNAL_DEPENDENCY: 0.8,
        Cause.CI_INFRASTRUCTURE: 0.1,
        Cause.TEST_DATA_STATE: 0.1,
        Cause.OTHER: 0.1,
    },
    Action.LOCAL_REPRODUCTION: {
        Cause.CODE_REGRESSION: 0.8,
        Cause.FLAKY_TEST: 0.1,
        Cause.EXTERNAL_DEPENDENCY: 0.1,
        Cause.CI_INFRASTRUCTURE: 0.1,
        Cause.TEST_DATA_STATE: 0.1,
        Cause.OTHER: 0.1,
    },
    Action.INSPECT_CODE: {
        Cause.CODE_REGRESSION: 0.8,
        Cause.FLAKY_TEST: 0.1,
        Cause.EXTERNAL_DEPENDENCY: 0.1,
        Cause.CI_INFRASTRUCTURE: 0.1,
        Cause.TEST_DATA_STATE: 0.1,
        Cause.OTHER: 0.1,
    },
    Action.CHECK_DB: {
        Cause.CODE_REGRESSION: 0.1,
        Cause.FLAKY_TEST: 0.1,
        Cause.EXTERNAL_DEPENDENCY: 0.1,
        Cause.CI_INFRASTRUCTURE: 0.1,
        Cause.TEST_DATA_STATE: 0.8,
        Cause.OTHER: 0.1,
    },
}


def decision_consequence(true_cause: Cause, predicted_cause: Cause) -> int:
    """Return consequence cost for the terminal diagnosis decision.

    A correct flaky diagnosis follows the automated rerun path and costs 0.
    A flaky diagnosis that is wrong is costly because automation was applied to
    a non-flaky failure. Non-flaky diagnoses route to human review; ``other``
    carries the highest consequence class.
    """
    if predicted_cause == Cause.FLAKY_TEST:
        if true_cause == Cause.FLAKY_TEST:
            return 0
        return HIGH_CONSEQUENCE_COST if true_cause == Cause.OTHER else HUMAN_REVIEW_COST
    if predicted_cause == Cause.OTHER:
        return HIGH_CONSEQUENCE_COST
    return HUMAN_REVIEW_COST


@dataclass
class Case:
    true_cause: Cause
    action_history: list = field(default_factory=list)
    cost: int = 0


class Simulator:
    """Generate reproducible hidden-cause CI diagnosis cases."""

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)

    def sample_cause(self) -> Cause:
        causes = list(PRIORS.keys())
        weights = list(PRIORS.values())
        return self.random.choices(causes, weights=weights, k=1)[0]

    def new_case(self) -> Case:
        return Case(true_cause=self.sample_cause())

    def observe(self, case: Case, action: Action) -> bool:
        """Return the positive/diagnostic observation for an action.

        The true cause is used internally by the simulator only. A policy
        should receive only the returned observation, not case.true_cause.
        """
        p_positive = LIKELIHOODS[action][case.true_cause]
        positive = self.random.random() < p_positive
        case.action_history.append((action, positive))
        case.cost += ACTION_COSTS[action]
        return positive


if __name__ == "__main__":
    simulator = Simulator(seed=42)
    for index in range(5):
        case = simulator.new_case()
        observation = simulator.observe(case, Action.RERUN)
        print(
            f"case={index + 1} cause={case.true_cause.value} "
            f"rerun_positive={observation} cost={case.cost}"
        )
