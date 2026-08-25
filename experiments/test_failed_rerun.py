from math import isclose

from src.belief_engine import initial_beliefs, posterior_after_observation
from src.simulator import Action, Cause


def test_rerun_failed_updates_beliefs():
    posterior = posterior_after_observation(
        initial_beliefs(), Action.RERUN, positive=False
    )

    expected = {
        Cause.CODE_REGRESSION: 0.4444444444,
        Cause.FLAKY_TEST: 0.1111111111,
        Cause.EXTERNAL_DEPENDENCY: 0.1111111111,
        Cause.CI_INFRASTRUCTURE: 0.1666666667,
        Cause.TEST_DATA_STATE: 0.0833333333,
        Cause.OTHER: 0.0833333333,
    }

    for cause, value in expected.items():
        assert isclose(posterior[cause], value, rel_tol=1e-9, abs_tol=1e-9)


if __name__ == "__main__":
    test_rerun_failed_updates_beliefs()
    print("Failed-rerun Bayesian update check: PASS")
