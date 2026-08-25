# Aggregate confusion matrices

Counts are aggregated across 5 seeds × 120 cases for each policy. Rows are true causes; columns are predicted causes. The `other` hidden cause has no corresponding predicted `other` class in the current policy implementation, which is itself a documented failure mode.

## P0

| True \ Pred | CI infrastructure | Code regression | External dependency | Flaky test | Test-data/state |
|---|---:|---:|---:|---:|---:|
| CI infrastructure | 31 | 9 | 9 | 10 | 5 |
| Code regression | 4 | 200 | 6 | 23 | 2 |
| External dependency | 2 | 4 | 44 | 7 | 1 |
| Flaky test | 4 | 5 | 16 | 163 | 3 |
| Other | 14 | 9 | 1 | 2 | 2 |
| Test-data/state | 2 | 2 | 2 | 1 | 17 |

## P2

| True \ Pred | CI infrastructure | Code regression | External dependency | Flaky test | Test-data/state |
|---|---:|---:|---:|---:|---:|
| CI infrastructure | 31 | 9 | 9 | 10 | 5 |
| Code regression | 4 | 174 | 6 | 49 | 2 |
| External dependency | 2 | 4 | 44 | 7 | 1 |
| Flaky test | 4 | 6 | 16 | 162 | 3 |
| Other | 14 | 9 | 1 | 2 | 2 |
| Test-data/state | 2 | 4 | 2 | 1 | 15 |

## P3

| True \ Pred | CI infrastructure | Code regression | External dependency | Flaky test | Test-data/state |
|---|---:|---:|---:|---:|---:|
| CI infrastructure | 31 | 7 | 9 | 12 | 5 |
| Code regression | 4 | 195 | 6 | 28 | 2 |
| External dependency | 2 | 5 | 44 | 6 | 1 |
| Flaky test | 4 | 13 | 16 | 155 | 3 |
| Other | 14 | 9 | 1 | 2 | 2 |
| Test-data/state | 2 | 4 | 2 | 2 | 14 |

## Interpretation

P3 retains more code-regression cases correctly than P2 while using fewer diagnostic actions. All three policies struggle with the `other` category because the current action space forces a choice among known causes. This motivates an explicit abstention/unknown action as a future design improvement.
