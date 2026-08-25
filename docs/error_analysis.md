# Error analysis protocol

The cohort requires examination of at least five incorrect decisions, named failure conditions, and identification of the highest-cost error. This file is the audit template to be populated from the saved case-level experiment output.

## Required case record

For every selected error, record:

1. case/seed
2. true cause
3. policy
4. final predicted cause
5. posterior at decision
6. diagnostic actions taken
7. observations received
8. total diagnostic cost
9. whether human escalation occurred
10. why the policy chose the action
11. what evidence would have changed the decision
12. design change, if any

## Error categories

### Code regression misclassified as flaky
Failure condition: rerun evidence receives too much weight relative to relevant code evidence.

### Flaky test misclassified as code regression
Failure condition: a failed rerun or recent code change is treated as sufficient evidence without repeated-history support.

### External dependency missed
Failure condition: the policy spends diagnostic budget on code/data checks while a service-health observation would have changed the action.

### CI infrastructure missed
Failure condition: transient runner/container/package/network evidence is not distinguished from application regression.

### Test-data/state missed
Failure condition: assertion/state evidence points to data changes but the policy commits to a code hypothesis.

### Other / unknown misclassified
Failure condition: the model is overconfident when evidence does not discriminate among known causes.

## Highest-cost error

The final report must select the error with the largest decision consequence, not simply the largest count. Human intervention/change is assigned the highest consequence class in the current simulation model.

## Status

Do not invent case-level errors. Populate this section only after the executable experiment has produced and saved per-case predictions/actions.
