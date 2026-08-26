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

# Terminal response/consequence costs. The scale is deliberately larger than
# diagnostic costs so that information can have decision value. The absolute
# units are arbitrary simulation units; only the relative costs matter.
HUMAN_REVIEW_COST = 80
HIGH_CONSEQUENCE_COST = 90

# The decision threshold is derived from the consequence ratio, not selected
# as a round confidence number. Scaling both costs by 10 leaves the threshold
# unchanged while making diagnostic cost meaningfully comparable to consequence.
C_FP = HUMAN_REVIEW_COST
C_FN = HIGH_CONSEQUENCE_COST
DERIVED_DECISION_THRESHOLD = C_FP / (C_FP + C_FN)  # 80 / 170 = 47.06%

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

# Cost of the response selected by a terminal diagnosis, conditional on the
# true hidden cause. Correct diagnoses can still carry operational cost: e.g.
# a code-regression diagnosis may require human review. Wrong diagnoses carry
# the ordinary review cost or the highest consequence for an "other" case.
RESPONSE_COSTS = {
    Cause.FLAKY_TEST: {
        Cause.CODE_REGRESSION: HUMAN_REVIEW_COST,
        Cause.FLAKY_TEST: 0,
        Cause.EXTERNAL_DEPENDENCY: HUMAN_REVIEW_COST,
        Cause.CI_INFRASTRUCTURE: HUMAN_REVIEW_COST,
        Cause.TEST_DATA_STATE: HUMAN_REVIEW_COST,
        Cause.OTHER: HIGH_CONSEQUENCE_COST,
    },
    Cause.CODE_REGRESSION: {
        Cause.CODE_REGRESSION: 30,
        Cause.FLAKY_TEST: HUMAN_REVIEW_COST,
        Cause.EXTERNAL_DEPENDENCY: HUMAN_REVIEW_COST,
        Cause.CI_INFRASTRUCTURE: HUMAN_REVIEW_COST,
        Cause.TEST_DATA_STATE: HUMAN_REVIEW_COST,
        Cause.OTHER: HIGH_CONSEQUENCE_COST,
    },
    Cause.EXTERNAL_DEPENDENCY: {
        Cause.CODE_REGRESSION: HUMAN_REVIEW_COST,
        Cause.FLAKY_TEST: HUMAN_REVIEW_COST,
        Cause.EXTERNAL_DEPENDENCY: 20,
        Cause.CI_INFRASTRUCTURE: HUMAN_REVIEW_COST,
        Cause.TEST_DATA_STATE: HUMAN_REVIEW_COST,
        Cause.OTHER: HIGH_CONSEQUENCE_COST,
    },
    Cause.CI_INFRASTRUCTURE: {
        Cause.CODE_REGRESSION: HUMAN_REVIEW_COST,
        Cause.FLAKY_TEST: HUMAN_REVIEW_COST,
        Cause.EXTERNAL_DEPENDENCY: HUMAN_REVIEW_COST,
        Cause.CI_INFRASTRUCTURE: 20,
        Cause.TEST_DATA_STATE: HUMAN_REVIEW_COST,
        Cause.OTHER: HIGH_CONSEQUENCE_COST,
    },
    Cause.TEST_DATA_STATE: {
        Cause.CODE_REGRESSION: HUMAN_REVIEW_COST,
        Cause.FLAKY_TEST: HUMAN_REVIEW_COST,
        Cause.EXTERNAL_DEPENDENCY: HUMAN_REVIEW_COST,
        Cause.CI_INFRASTRUCTURE: HUMAN_REVIEW_COST,
        Cause.TEST_DATA_STATE: 40,
        Cause.OTHER: HIGH_CONSEQUENCE_COST,
    },
    Cause.OTHER: {
        Cause.CODE_REGRESSION: HIGH_CONSEQUENCE_COST,
        Cause.FLAKY_TEST: HIGH_CONSEQUENCE_COST,
        Cause.EXTERNAL_DEPENDENCY: HIGH_CONSEQUENCE_COST,
        Cause.CI_INFRASTRUCTURE: HIGH_CONSEQUENCE_COST,
        Cause.TEST_DATA_STATE: HIGH_CONSEQUENCE_COST,
        Cause.OTHER: HIGH_CONSEQUENCE_COST,
    },
}


def decision_consequence(true_cause: Cause, predicted_cause: Cause) -> int:
    """Return the response/consequence cost for a terminal diagnosis."""
    return RESPONSE_COSTS[predicted_cause][true_cause]


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
