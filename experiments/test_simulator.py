from src.simulator import Action, Simulator


def run_sanity_check(seed: int = 42):
    simulator = Simulator(seed=seed)
    rows = []

    for index in range(5):
        case = simulator.new_case()
        observation = simulator.observe(case, Action.RERUN)
        rows.append((case.true_cause.value, observation, case.cost))

    return rows


if __name__ == "__main__":
    first = run_sanity_check(seed=42)
    second = run_sanity_check(seed=42)

    assert first == second, "Fixed seed should reproduce the same simulation."
    assert all(cost == 1 for _, _, cost in first)

    for index, (cause, observation, cost) in enumerate(first, start=1):
        print(
            f"case={index} hidden_cause={cause} "
            f"rerun_positive={observation} cost={cost}"
        )

    print("Simulator reproducibility check: PASS")
