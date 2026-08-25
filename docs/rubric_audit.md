# Week 1 rubric audit

This audit is based on the current cohort/research files in the project. The cohort asks for a baseline plus at least two policies, a 100-case experiment, saved predictions/actions, confusion matrix/applicable metrics, five incorrect decisions, named failure conditions, highest-cost error, probability decision record, AI-review log, `.dot` architecture, and a LaTeX preprint.

| Requirement | Status | Evidence / next action |
|---|---|---|
| Problem framing | DONE | CI integration-test failure diagnosis |
| Hidden state / observation / belief framing | DONE | research notes + simulator |
| Prior/likelihood decision record | DONE | `docs/probability_decision_record.md` |
| P0 baseline | IMPLEMENTED | shared-case experiment |
| P2 threshold policy | IMPLEMENTED | `src/policies.py` |
| P3 EIG-per-cost policy | IMPLEMENTED | `src/policies.py` |
| 100+ cases | IMPLEMENTED IN HARNESS | 120 cases per seed |
| Same cases for all policies | DONE IN HARNESS | `experiments/shared_case_experiment.py` |
| Fixed seeds | DONE | seeds 2026–2030 |
| Accuracy/cost/actions/escalation | IMPLEMENTED | experiment + notebook |
| Confusion matrix | TODO | generate from saved case-level predictions |
| Five incorrect decisions | TODO | populate `docs/error_analysis.md` from case-level output |
| Highest-cost error | TODO | derive from case-level consequence records |
| Extension concepts beyond supplied ladder | DONE | VPI + VSI in `docs/extension_concepts.md` |
| Stop rule stated | PARTIAL | design exists; final decision-value implementation should be tightened |
| `.dot` architecture | DONE | `docs/architecture.dot` |
| AI review log | TODO/PENDING | `docs/ai_review_log.md` is the audit location; actual reviews must be performed and recorded |
| LaTeX preprint | TODO | create after final experiment output is verified |
| Community participation evidence | NOT VERIFIED HERE | research file lists participation as a required activity; attach actual records before claiming completion |
| Primary-source research | PARTIAL/NEEDS AUDIT | verify every external claim against primary sources |

## Critical correction

The cohort material distinguishes the threshold and value-of-information policies. Do not relabel the policies to make the paper sound stronger than the source: P2 is the threshold policy and P3 is the value-of-information/EIG policy for the current experiment. Historical-aware reasoning remains a useful extension because the research notes promoted historical failure evidence to a first-class evidence source.

## Submission rule

Do not mark a TODO as complete merely because code exists. A rubric item is complete only when the required evidence is present and reproducible.
