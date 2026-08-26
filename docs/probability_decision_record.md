# Probability Decision Record — CI Diagnosis

## Scope

This is a reproducible simulation record, not a claim about real-world CI failure frequencies.

## Hidden states

- code regression
- flaky test
- external dependency
- CI infrastructure
- test-data/state
- other

## Initial prior

| Cause | Prior |
|---|---:|
| Code regression | 0.40 |
| Flaky test | 0.30 |
| External dependency | 0.10 |
| CI infrastructure | 0.10 |
| Test-data/state | 0.05 |
| Other | 0.05 |

## Likelihood model

The prototype maps qualitative research assumptions to simulation probabilities:

- often = 0.8
- sometimes = 0.4
- rarely = 0.1

These are model assumptions for controlled experimentation and are not calibrated production probabilities.

## Worked update

For `RERUN -> PASSED`, the current likelihood table gives a posterior of approximately:

- code regression: 34.78%
- flaky test: 52.17%
- external dependency: 8.70%
- CI infrastructure: 2.17%
- test-data/state: 1.09%
- other: 1.09%

For `RERUN -> FAILED`:

- code regression: 44.44%
- flaky test: 11.11%
- external dependency: 11.11%
- CI infrastructure: 16.67%
- test-data/state: 8.33%
- other: 8.33%

## Costs

| Cost class | Simulation units |
|---|---:|
| Cheap automated check | 1 |
| Heavier automated diagnostic | 2 |
| Human review/intervention | 8 |
| Highest-consequence outcome | 9 |

Diagnostic action costs are 1 or 2. Human consequence costs are 8 or 9. These are simulation units, not production money or minutes.

## Derived decision threshold

The decision threshold is no longer a round-number confidence assumption.

For a binary decision where a false positive costs `C_FP = 8` and a false negative costs `C_FN = 9`:

```text
p* = C_FP / (C_FP + C_FN)
   = 8 / (8 + 9)
   = 8 / 17
   = 0.470588...
   = 47.06%
```

This is the **derived simulation decision threshold** used by P2 and P3 by default. It is not an empirically derived production threshold. Threshold sensitivity remains necessary because the consequence costs themselves are assumptions.

The result is deliberately lower than the previous 70% heuristic. That is a finding, not a typo: the cohort requirement is to derive the threshold from consequences and then investigate what the resulting policy does.

## P0 baseline

P0 is now a true no-evidence baseline. It does not run diagnostics and always selects the modal prior cause, `code_regression` at 40% prior probability. This establishes whether adaptive evidence use beats a trivial policy.

## P2 threshold policy

P2 updates beliefs and stops when the highest posterior reaches the derived 47.06% threshold. Otherwise it follows the fixed diagnostic order.

The threshold is a decision-policy parameter derived from the stated simulation consequence costs, not a claim about production CI.

## P3 value-of-information policy

P3 ranks available checks by expected information gain per unit diagnostic cost. It additionally applies a **decision-value stop gate**:

> Run another check only when its expected reduction in terminal decision consequence exceeds that check's cost.

This prevents the agent from buying entropy reduction when no possible result would improve the eventual decision enough to pay for the check.

The intended loop is:

```text
Initial prior
    ↓
Check whether threshold already supports a terminal decision
    ↓
Rank candidate checks by expected IG / cost
    ↓
Estimate expected decision-value of the best check
    ↓
If decision value > check cost: run it
Otherwise: stop / escalate
    ↓
Observe result
    ↓
Bayesian posterior update
    ↓
Repeat
```

## Audit requirements

Every experiment records or can reconstruct: seed, hidden cause, observations available to each policy, policy, actions taken, posterior evolution through the action sequence, diagnostic cost, consequence cost, final prediction, and escalation outcome.

The P0/P2/P3 experiment uses identical pre-generated cases and observation opportunities for all policies. This prevents random-world differences from masquerading as policy improvements.
