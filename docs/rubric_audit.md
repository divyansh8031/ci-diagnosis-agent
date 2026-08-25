# Week 1 rubric audit

This audit is based on the current cohort/research requirements and the verified GitHub Actions experiment.

| Requirement | Status | Evidence |
|---|---|---|
| Problem framing | DONE | CI integration-test failure diagnosis |
| Hidden state / observation / belief framing | DONE | `src/simulator.py`, `src/belief_engine.py` |
| Prior/likelihood decision record | DONE | `docs/probability_decision_record.md` |
| P0 baseline | DONE | `experiments/shared_case_experiment.py` |
| P2 threshold policy | DONE | `src/policies.py` |
| P3 EIG/value-of-information policy | DONE | `src/policies.py` |
| 100+ cases | DONE | 120 cases × 5 fixed seeds |
| Same cases for all policies | DONE | shared-case generation |
| Fixed seeds | DONE | 2026–2030 |
| Saved predictions/actions/observations | DONE | GitHub Actions final-evidence artifact |
| Accuracy/cost/actions/escalation | DONE | `results/final_results.md` |
| Confusion matrices | DONE | generated JSON files in final-evidence artifact |
| Five incorrect decisions | DONE | `docs/error_analysis.md` |
| Named failure conditions | DONE | `docs/error_analysis.md` |
| Highest-cost error | DONE | maximum observed decision cost = 17; tied cases recorded |
| Extension concepts beyond ladder | DONE | VPI + VSI in `docs/extension_concepts.md` |
| Stop-rule / decision-value limitation | DONE WITH LIMITATION | P3 is explicitly documented as EIG/cost proxy; VSI/VPI extension explains limitation |
| `.dot` architecture | DONE | `docs/architecture.dot` |
| AI review log | DONE | `docs/ai_review_log.md` with accepted/rejected comments |
| LaTeX preprint | DONE | `paper/preprint.tex` with verified results |
| Executable reproducibility | DONE | final-evidence GitHub Actions run passed all validation and experiment steps |
| Community participation evidence | USER ACTION REQUIRED | Do not claim completion until actual cohort/community records are attached |
| Primary-source research audit | USER/RESEARCH RECORD REQUIRED | External claims must be checked against the actual primary sources used in the paper |

## Verified experiment

The final-evidence GitHub Actions run validated the simulator, Bayesian worked example, failed-rerun update, and information-gain checks, then generated the shared-case experiment, sensitivity analysis, case-level records, confusion matrices, five-error selection, and highest-cost error.

At the 70% threshold: P0 accuracy 75.83%, mean diagnostic cost 9.00, mean decision cost 14.25; P2 accuracy 71.00%, diagnostic cost 5.83, decision cost 10.75; P3 accuracy 73.17%, diagnostic cost 5.36, decision cost 10.63.

## Submission discipline

Do not claim community participation or primary-source verification without attaching the actual evidence. Do not describe simulation assumptions as measured real-world probabilities. Do not claim P3 universally dominates P2.
