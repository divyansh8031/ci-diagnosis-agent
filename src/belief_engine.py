from math import log2

from .simulator import Cause, Action, LIKELIHOODS, PRIORS


def normalize(beliefs):
    total = sum(beliefs.values())
    if total == 0:
        raise ValueError("Belief mass cannot sum to zero.")
    return {cause: value / total for cause, value in beliefs.items()}


def posterior_after_observation(beliefs, action, positive):
    """Update beliefs using Bayes' rule for a binary observation."""
    updated = {}
    for cause, prior in beliefs.items():
        p_positive = LIKELIHOODS[action][cause]
        likelihood = p_positive if positive else (1 - p_positive)
        updated[cause] = prior * likelihood
    return normalize(updated)


def entropy(beliefs):
    return -sum(
        probability * log2(probability)
        for probability in beliefs.values()
        if probability > 0
    )


def expected_entropy(beliefs, action):
    """Expected posterior entropy before observing the action result."""
    p_positive = sum(
        beliefs[cause] * LIKELIHOODS[action][cause]
        for cause in beliefs
    )

    positive_beliefs = posterior_after_observation(beliefs, action, True)
    negative_beliefs = posterior_after_observation(beliefs, action, False)

    return (
        p_positive * entropy(positive_beliefs)
        + (1 - p_positive) * entropy(negative_beliefs)
    )


def information_gain(beliefs, action):
    return entropy(beliefs) - expected_entropy(beliefs, action)


def initial_beliefs():
    return dict(PRIORS)


def most_likely_cause(beliefs):
    return max(beliefs, key=beliefs.get)


if __name__ == "__main__":
    beliefs = initial_beliefs()
    print("Initial entropy:", round(entropy(beliefs), 4))
    for action in Action:
        print(
            action.value,
            "IG=",
            round(information_gain(beliefs, action), 4),
        )

    beliefs = posterior_after_observation(
        beliefs, Action.RERUN, positive=True
    )
    print("\nAfter RERUN=PASSED:")
    for cause, probability in beliefs.items():
        print(cause.value, round(probability, 4))
    print("Entropy:", round(entropy(beliefs), 4))
