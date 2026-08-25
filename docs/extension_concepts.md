# Extension concepts

The cohort asks for at least two concepts beyond the supplied ladder, used for something real in the design. This project uses the following extensions.

## 1. Value of perfect information (VPI)

**Plain meaning:** VPI asks how much the decision could improve if the true cause were known before paying for any diagnostic action.

**Use here:** It gives an upper bound on how much diagnostic information is worth purchasing. If the maximum possible improvement is smaller than the cost of another check, the agent should stop.

**Small example:** If knowing the cause perfectly would reduce expected decision loss from 5 to 2, VPI is 3. A diagnostic check costing 4 cannot be justified by perfect information alone.

**When it is a mistake:** VPI is an upper bound, not the value of a real imperfect test. Treating it as achievable can cause over-investigation.

## 2. Value of sample information (VSI)

**Plain meaning:** VSI measures the expected improvement from a particular imperfect observation after accounting for how the observation changes the decision.

**Use here:** The P3 policy uses expected information gain per cost as a tractable proxy, but VSI is the stronger decision-theoretic framing because information is valuable only when it can change the action.

**Small example:** Suppose a check costs 1. If it can cause the agent to switch from an expected-cost-6 action to an expected-cost-3 action in expectation, its gross value is 3 and net value is 2.

**When it is a mistake:** Pure information gain can rank an action highly even when both possible outcomes lead to the same final action. In that situation the information has zero decision value, despite positive entropy reduction.

## Design implication

This distinction exposes a limitation of the current P3 implementation: EIG/cost is an information-efficiency proxy, not a full expected-utility calculation. The stop rule should therefore be framed around whether an observation can change the eventual action, not merely whether it reduces entropy.
