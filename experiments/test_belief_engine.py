from math import isclose

from src.belief_engine import entropy, initial_beliefs, posterior_after_observation
from src.simulator import Action, Cause


def test_rerun_passed_matches_worked_example():
    beliefs = initial_beliefs()
    posterior = posterior_after_observation(
        beliefs, Action.RERUN, positive=True
    )

    # P(RERUN=PASSED | cause) comes from the likelihood assumptions
    # recorded in src/simulator.py.
    expected = {
        Cause.CODE_REGRESSION: 0.3478260870,
        Cause.FLAKY_TEST: 0.5217391304,
        Cause.EXTERNAL_DEPENDENCY: 0.0869565217,
        Cause.CI_INFRASTRUCTURE: 0.0217391304,
        Cause.TEST_DATA_STATE: 0.0108695652,
        Cause.OTHER: 0.0108695652,
    }

    for cause, value in expected.items():
        assert isclose(posterior[cause], value, rel_tol=1e-9, abs_tol=1e-9)

    assert isclose(entropy(posterior), 1.7345, rel_tol=1e-3)


if __name__ == "__main__":
    test_rerun_passed_matches_worked_example()
    print("Belief engine worked-example check: PASS")
