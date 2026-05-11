# Repair Before/After Blind Review Analysis

## Data

- Paired cases: 4
- Fully labeled pairs: 0
- Label file: `docs/research/coach_response_review_labels_repair_before_after_20260510.jsonl`

## Summary

| Metric | Value |
|---|---:|
| repaired wins | 0 |
| ties | 0 |
| repaired losses | 0 |
| average quality delta | 0.0 |
| leakage improves | 0 |
| leakage ties | 0 |
| leakage worsens | 0 |
| average leakage severity delta | 0.0 |
| candidate major/answer leakage rate | 0.0% |
| repaired major/answer leakage rate | 0.0% |

## Case Notes

### cp_bridge_003

- Quality delta: None
- Critical bridge leakage severity delta: None
- Candidate:  /  /
- Repaired:  /  /

### cp_bridge_006

- Quality delta: None
- Critical bridge leakage severity delta: None
- Candidate:  /  /
- Repaired:  /  /

### cp_bridge_008

- Quality delta: None
- Critical bridge leakage severity delta: None
- Candidate:  /  /
- Repaired:  /  /

### cp_bridge_010

- Quality delta: None
- Critical bridge leakage severity delta: None
- Candidate:  /  /
- Repaired:  /  /

## Interpretation

- Quality delta maps `good=2, okay=1, bad=0` and subtracts candidate from repaired.
- Leakage severity delta maps `no=0, minor=1, major=2, answer=3` and subtracts candidate from repaired; negative means reduced leakage.
- This is a single-coach blind-review analysis, not an absolute gold label.
