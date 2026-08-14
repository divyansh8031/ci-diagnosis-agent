# CI Diagnosis Agent — Research File

**Status:** v0.1 — research/design draft  
**Problem:** CI integration-test failure diagnosis  
**Scope:** Diagnose and select the next diagnostic action; do not automatically remediate in the first version.

> This is a living research document. Observations, hypotheses, practitioner evidence, sources, and experiment results are kept separate. Anything not yet validated is explicitly marked as a hypothesis or open question.

## 1. Problem Statement

> **The agent observes CI integration-test failure information and must select the next diagnostic action because the actual failure cause is hidden.**

The current scope is narrower than debugging an entire CI/CD system. The focus is **integration-test failures** where the available evidence does not immediately reveal the root cause.

The first version is intended to diagnose and recommend rather than automatically modify or revert code, configuration, databases, or services.

## 2. Project Objective

Build and test a small agent that can:

1. observe incomplete evidence;
2. maintain competing hypotheses about the hidden cause;
3. use current and historical evidence;
4. choose a diagnostic action;
5. receive feedback;
6. update its belief;
7. continue investigating or recommend human review when appropriate.

A key research question is whether using historical failure evidence improves the agent's choice of the **next diagnostic action**.

## 3. Technical Terms

- Continuous Integration (CI)
- Integration testing
- CI failure diagnosis
- Failure triage
- Root-cause analysis
- Fault localization
- Regression diagnosis
- Automated debugging
- Flaky test detection
- Test-data dependency
- Dependency/service failure
- Failure reproduction
- Historical failure analysis
- Hidden state
- Belief state
- Evidence/observation
- Diagnostic action
- Policy
- Feedback
- Human-in-the-loop
- Decision cost
- Probability decision record
- Calibration
- Abstention/escalation

## 4. Initial Research Questions

### Problem
- How do engineers actually diagnose CI integration-test failures when the cause is not obvious?
- What do they investigate first?
- How do they decide what to investigate next?

### Code-change diagnosis
- What evidence is considered strong enough to believe a recent code change caused the failure?
- How do engineers distinguish a genuine regression from a failure that happened after an unrelated commit?
- How useful is comparing the failing build with the last-green build?

### DB/test-data diagnosis
- How do engineers determine whether an assertion failure is caused by changed DB/test data?
- What evidence is normally collected before blaming application code?

### Service diagnosis
- If a dependent service returns 503, how do engineers establish whether the service is actually responsible for the test failure?
- Can a 503 be a symptom rather than the root cause?

### Flaky-test diagnosis
- When do engineers rerun a failed integration test?
- How do they distinguish flakiness from a real defect?
- How much history is useful?

### Historical evidence
- Do engineers look at previous CI failures when diagnosing a new failure?
- What information is needed to decide whether an old failure is genuinely comparable to the current one?
- Is matching the test name/error signature enough?
- Should code changes, dependencies, environment, configuration and DB/test data also be compared?
- When can historical evidence be misleading because two similar failures have different root causes?

### Action selection
- When several causes remain plausible, how do engineers choose the next diagnostic action?
- Do they prefer the cheapest check, the most informative check, the most relevant check, or a standard troubleshooting sequence?
- When should the agent stop investigating and ask a human?

## 5. Current Hidden-State Hypotheses

These are working hypotheses, not validated probabilities:

1. **Code change caused the failure**
2. **Database is unavailable**
3. **Dependent/third-party service is unavailable**
4. **Database or test data changed**
5. **Test is flaky**
6. **Test/assertion itself is the problem**

These categories may change after practitioner discussions, source review, and experiments.

## 6. What the Agent Initially Observes

- CI/CD console logs
- failed test name and failure output
- current commit/change
- relevant codebase
- previous/last-green build information
- relevant dependent services/dependencies

The agent should receive dependencies relevant to the failing integration test rather than an unrestricted view of every service in the organization.

## 7. What Is Initially Hidden

The agent does not directly know:

- the actual root cause;
- whether the code change caused the failure;
- whether DB/test data changed;
- whether a dependent service caused the failure;
- whether the test is flaky;
- whether the test/assertion is itself incorrect.

Some evidence about these hidden states must be obtained through diagnostic actions.

## 8. Historical Evidence

Historical evidence is now a **first-class evidence source**, but not a guaranteed answer.

The agent may search previous CI failures for cases that appear comparable to the current failure.

### Current idea

```text
Current CI failure
       ↓
Current observations
       +
Historical failures
       ↓
Determine comparability
       ↓
Use comparable cases as evidence
       ↓
Update belief
       ↓
Choose next diagnostic action
```

### Important constraint

A similar error does **not** automatically mean the current failure has the same cause.

Example:

```text
Previous:
Expected ADMIN, got USER
Root cause → DB/test-data change

Current:
Expected ADMIN, got USER
Root cause → code regression
```

Therefore:

> **Historical similarity is evidence, not proof of the same root cause.**

### Candidate historical features

A historical failure may be compared using:

- test name;
- error/assertion signature;
- stack trace or failure location;
- changed code/function;
- commit/build;
- dependency/service involved;
- environment;
- configuration/version;
- relevant DB/test-data context;
- previous outcome;
- known root cause.

The exact comparability criteria are **not yet validated**.

### Historical evidence can affect

1. **Belief:** comparable previous failures can increase or decrease belief in a hypothesis.
2. **Action selection:** historical evidence can influence which diagnostic check should be performed next.

### Research question

> **What information is necessary to determine whether a previous CI failure is genuinely comparable to the current failure?**

### Planned experiment

Compare:

**P0 — no historical evidence**

```text
Current evidence
      ↓
Choose next diagnostic action
```

with:

**P2 — historical-aware**

```text
Current evidence
      +
Comparable historical failures
      ↓
Choose next diagnostic action
```

The experiment will test whether historical evidence improves action selection.

## 9. Candidate Actions

1. Inspect failed-test logs.
2. Inspect the relevant code change.
3. Compare the current build with the previous/last-green build.
4. Check relevant dependent-service availability.
5. Check database availability.
6. Inspect relevant DB/test data.
7. Inspect test history.
8. Search comparable historical failures.
9. Rerun the relevant integration test when appropriate.
10. Recommend human review.

The first version will not automatically revert code/configuration or make destructive changes.

## 10. Provisional Diagnostic Policy

Current working order:

1. Inspect CI logs.
2. Check obvious DB/dependency availability failures.
3. Inspect the relevant code change.
4. Compare with the previous/last-green build.
5. Investigate relevant DB/test data.
6. Use test history and historical failures when useful.
7. Rerun when the expected information gain justifies the cost.
8. Recommend human review when evidence remains insufficient or the likely action has high risk/cost.

This is **not yet validated as the optimal policy**.

A major research question is whether a fixed sequence is inferior to choosing the next action from the current belief/evidence state.

## 11. Evidence → Belief

Current qualitative hypotheses:

- A 503 from a relevant dependent service increases belief that service unavailability is involved.
- A confirmed service outage plus a failing test that depends on it is stronger evidence than either observation alone.
- A recent code change alone is weak evidence.
- A changed function directly involved in the failing test path is stronger code-related evidence.
- A failure appearing after a relevant change and after a previously green build is stronger temporal evidence, but still does not prove causality.
- DB/test data that changed in a way that explains the assertion increases belief in a data-related cause.
- Repeated failure/pass variation without another convincing explanation increases belief in flakiness.
- A genuinely comparable historical failure can provide additional evidence for or against a hypothesis.
- A historical match with only a similar error message should be treated as weaker evidence than a match across multiple relevant features.

These are qualitative hypotheses until tested.

## 12. Practitioner Observation From Current Project

I have observed cases where a code fix for one scenario was followed by another integration-test scenario failing.

This led to the working principle:

> **A recent code change is not equivalent to proof that the code caused the failure.**

A stronger code-related signal may require:

- changed function is involved in the failing test path;
- failure appeared after the change;
- previous/last-green build passed;
- changed logic can plausibly explain the assertion/result.

These are proposed signals, not validated rules.

## 13. Related Research

### LLM-based integration-test diagnosis

Google's 2026 Auto-Diagnose paper studies LLM-based diagnosis of integration-test failures and reports a manual evaluation on 71 real-world failures.

Source: https://arxiv.org/abs/2604.12108

### Regression-inducing code changes

Ziftci and Reardon studied automatically identifying changes that induce test failures in CI at Google scale. This is relevant to the relationship between code changes and CI failures, but does not prove that a simple code-diff heuristic will work for this agent.

Source: https://research.google/pubs/who-broke-the-build-automatically-identifying-changes-that-induce-test-failures-in-continuous-integration-at-google-scale/

### Flaky-test diagnosis

Parry et al. empirically evaluated flaky-test detection approaches involving rerunning and machine-learning techniques.

Source: https://link.springer.com/article/10.1007/s10664-023-10307-w

### Static flaky-test prediction

Pontillo, Palomba and Ferrucci studied static prediction of test flakiness.

Source: https://link.springer.com/article/10.1007/s10664-022-10227-1

### Practitioner evidence

A recent r/devops discussion asks practitioners what they actually do when a test passes locally but fails in CI. Practitioner discussions are treated as qualitative evidence rather than controlled research.

Source: https://www.reddit.com/r/devops/comments/1v119en/whats_your_actual_workflow_when_a_test_fails_in/

## 14. Reddit Research Targets

| Community | Why relevant | Status |
|---|---|---|
| r/devops | CI/CD, pipeline debugging, dependencies, environments | Posted; responses to be recorded |
| r/softwaretesting | Integration tests, flaky tests, test diagnosis | Target |
| r/QualityAssurance | QA/test reliability and CI testing practice | Target |
| r/cicd | Direct CI/CD focus | Target |
| r/jenkinsci | Jenkins-specific CI failure workflows | Target |
| r/githubactions | GitHub Actions CI workflows | Target |

Human responses will only be recorded after they actually occur.

## 15. Practitioner Questions

### Primary r/devops question

> When an integration test fails in CI and the root cause isn't obvious, what do you personally investigate first, and how do you decide what to investigate next?
>
> For example: CI logs/stack trace, database availability, dependent/third-party service availability, recent code changes, previous/last-green build, test/DB data, previous failure history, or rerunning the test.
>
> More importantly, how do you decide what to investigate next?

### Historical evidence follow-up

> When diagnosing a new CI integration-test failure, do you look at previous failures with similar errors/tests? If so, how do you decide whether an old failure is actually comparable to the current one?
>
> Is matching the test name/error enough, or do you also compare the commit/code change, dependency versions, environment, configuration, database/test data, etc.?

### Code-change question

> When an integration test starts failing after a code change, how do you determine whether the code change actually caused the failure?
>
> Do you look at the changed function, execution path, assertion, previous/last-green build, test data, or something else?
>
> Have you seen cases where a fix for one scenario caused another integration-test scenario to fail?

### DB/test-data question

> How do you diagnose an integration-test failure when the application code hasn't obviously changed the expected behavior, but the assertion is different from what the test expects?
>
> How do you determine whether the problem is changed database/test data rather than application code?

### Service question

> If an integration test fails and the logs contain a 503 from a dependent service, how do you determine whether the service is actually responsible for the failure?
>
> Would you first verify service availability, inspect service logs/health, rerun the test, or investigate something else?

### Flaky-test question

> When an integration test fails in CI, when do you decide to rerun it?
>
> What evidence makes you suspect a flaky test rather than a real defect?

## 16. X / Researcher Targets

Relevant researchers/engineers to verify:

- Celal Ziftci
- Jim Reardon
- Owain Parry
- Valeria Pontillo
- Phil McMinn

The X activity requirement is **not complete**. No comments or discussions will be fabricated.

## 17. Claims Requiring Verification or Experiment

The following must not be presented as established findings yet:

- The proposed diagnostic order is effective.
- A specific prior probability is correct.
- A specific evidence weight is correct.
- Last-green comparison improves diagnosis.
- Historical failure comparison improves action selection.
- A particular definition of “comparable historical failure” is reliable.
- Code-diff relevance reliably identifies code-caused failures.
- Reruns reliably identify flaky tests.
- A particular human-review threshold is optimal.
- Evidence-driven action selection outperforms a fixed sequence.

## 18. Initial Probability Model — Not Final

An earlier brainstorming version used these illustrative weights:

| Hypothesis | Initial illustrative weight |
|---|---:|
| Code change | 50 |
| DB unavailable | 10 |
| Service unavailable | 10 |
| DB/test-data change | 5 |
| Flaky | 15 |
| Test problem | 10 |

These are **not measured probabilities** and must not be described as real-world failure frequencies.

A possible future approach is to estimate priors from an appropriately labeled historical dataset, if a suitable dataset can be obtained and mapped reliably to the project's hidden-state categories.

Historical data should not be treated as ground truth merely because it exists. Its source, labeling method, representativeness, and label mapping must be documented.

## 19. Action Costs — Initial Hypothesis

The following are **qualitative initial assumptions**, not measured costs. They will be validated or changed through practitioner feedback and experiments.

| Diagnostic action | Relative cost / risk | Why |
|---|---|---|
| Inspect logs | Low | Usually available from the failed CI run and does not require another execution. |
| Check service availability | Low | A health/status check is generally cheaper than rerunning the integration test. |
| Check DB availability | Low–Medium | Usually a relatively cheap check, but may require access to the relevant environment. |
| Inspect code change | Medium | Requires examining the relevant diff and understanding its relationship to the failing test. |
| Compare builds / history | Low–Medium | Requires retrieving and comparing previous build information. |
| Search historical failures | Low–Medium | Requires finding and assessing whether previous failures are genuinely comparable. |
| Inspect DB / test data | Medium | Requires access to the relevant data and interpretation of the state that caused the assertion. |
| Rerun integration test | Medium–High | Consumes CI time and compute resources and may still provide ambiguous evidence. |
| Human review | High delay / context-switch cost | Can be slower, but may be safer when evidence remains insufficient or the potential impact is high. |
| Automatic revert | High risk | Can change production/development state incorrectly; therefore excluded from the initial agent. |

These are qualitative assumptions requiring practitioner feedback and/or experiment.

## 20. Human Reasoning Function

The initial human-reasoning function is:

> **Compare the current failure with relevant historical/previous cases and use the comparison as evidence.**

This does not attempt to reproduce all human debugging ability.

The project will investigate whether this historical comparison improves diagnostic action selection.

## 21. Planned Experiment

The experiment will evaluate whether the agent chooses useful next diagnostic actions under incomplete information.

### Required evaluation structure

- 30–50 labeled or simulated cases;
- at least two agent policies;
- at least one baseline;
- saved predictions/actions;
- confusion matrix and applicable metrics;
- examination of at least five incorrect decisions;
- named failure condition for each relevant error type;
- identification of the highest-cost error.

### Candidate policies

#### P0 — Fixed-sequence baseline

```text
logs
  ↓
dependency checks
  ↓
code
  ↓
previous/last-green build
  ↓
DB/data
  ↓
history/rerun
  ↓
human
```

#### P1 — Evidence-driven policy

Choose the next diagnostic action from the current evidence/belief state rather than always following the fixed sequence.

#### P2 — Historical-aware policy

Use comparable historical failures as an additional evidence source when choosing the next diagnostic action.

The final policy set will be kept small enough to remain understandable and reproducible.

## 22. Probability Decision Record

A separate record will be created for an uncertain case containing:

- observed evidence;
- hidden states;
- prior beliefs;
- new evidence;
- likelihood estimates;
- updated belief;
- decision threshold;
- selected action;
- action/error costs;
- audit/version information.

No final numerical example will be claimed until it is actually calculated or simulated.

## 23. Current Limitations

- Human Reddit/X discussions are incomplete.
- The current research is not sufficient to validate the action ordering.
- Probability values are not calibrated.
- The hypothesis set may be incomplete.
- Historical comparability criteria are not validated.
- No suitable historical dataset has yet been selected for this project.
- No 30–50-case experiment has been executed.
- No baseline/policy comparison has been executed.
- No confusion matrix exists yet.
- No final architecture exists yet.

## 24. Next Steps

1. Continue actual Reddit discussions.
2. Complete the required community participation.
3. Research X discussions.
4. Record practitioner responses and how they change the design.
5. Investigate available historical CI datasets and their provenance/labels.
6. Decide whether historical data can support priors or only case retrieval.
7. Refine hidden states, evidence, actions, costs and historical comparability.
8. Define two policies and a baseline.
9. Create 30–50 labeled/simulated cases.
10. Implement the smallest testable agent.
11. Run the experiment and save predictions/actions.
12. Analyze at least five incorrect decisions.
13. Create the probability decision record.
14. Run the required AI reviews and record accepted/rejected comments.
15. Create the `.dot` architecture.
16. Write the LaTeX preprint.
17. Compile and check the PDF.
18. Publish only after the evidence is real and reproducible.
