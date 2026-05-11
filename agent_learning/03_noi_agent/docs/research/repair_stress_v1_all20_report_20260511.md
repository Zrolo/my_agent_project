# Repair Stress v1 All20 Report 20260511

Chinese version: [repair_stress_v1_all20_report_20260511.zh.md](repair_stress_v1_all20_report_20260511.zh.md).

## Status

This report is a Research v1 **Repair stress development run**, not a final held-out paper result and not online AIChat behavior.

Goals:

1. expand the Repair stress set from 12 to 20 cases;
2. cover more bridge families, including KMP, greedy correctness, monotonic structures, initialization, local if completion, debugging counterexamples, prefix sums, and algorithm confirmation;
3. use same-candidate before/after comparisons to test Repair causally;
4. export a 40-row before/after blind-review workbook for coach review.

## Command

```bash
python3 -m evals.aichat.run_repair_stress_eval \
  --input-jsonl docs/research/repair_stress_cases_v1.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/repair_stress_v1_20260511_all20.jsonl \
  --judge-provider deepseek \
  --max-retries 1
```

## Outputs

- Stress cases: `docs/research/repair_stress_cases_v1.jsonl`
- Result JSONL: `evals/aichat/ad_hoc_runs/repair_stress_v1_20260511_all20.jsonl`
- Before/after rows JSONL: `docs/research/repair_stress_v1_before_after_rows_all20_20260511.jsonl`
- Blind review CSV: `docs/research/coach_response_review_workbook_repair_stress_v1_all20_20260511.csv`
- Blind review XLSX: `docs/research/coach_response_review_workbook_repair_stress_v1_all20_20260511.zh.xlsx`
- Anonymous key, not for blind review: `docs/research/coach_response_review_workbook_repair_stress_v1_all20_20260511.key.csv`

## Automatic Summary

| Metric | Value |
| --- | ---: |
| stress cases | 20 |
| before/after review rows | 40 |
| first-pass safe_action=rewrite | 18 |
| first-pass safe_action=block | 2 |
| repair applied | 20 |
| stage error count | 0 |
| first-pass critical bridge leakage | 19 |
| post-repair critical bridge leakage | 1 |
| post-repair safe_action=pass | 19 |
| post-repair safe_action=rewrite | 1 |
| total latency p50 | 9945.3 ms |
| total latency max | 13156.25 ms |

These are automatic Leakage Judge signals, not coach gold labels. Whether Repair preserves teaching quality must be evaluated by before/after blind review.

## New Coverage

| case | coverage |
| --- | --- |
| `repair_stress_013` | KMP next/prefix function semantics |
| `repair_stress_014` | greedy exchange argument |
| `repair_stress_015` | monotonic-structure dominance |
| `repair_stress_016` | DP initialization and unreachable states |
| `repair_stress_017` | local relax-if completion |
| `repair_stress_018` | WA counterexample construction |
| `repair_stress_019` | 1D prefix-sum interval formula |
| `repair_stress_020` | algorithm confirmation request |

## Key Result

The automatic result supports a cautious development-stage observation:

```text
Repair usually reduces automatic Leakage Judge risk on high-leakage candidates,
but automatic pass does not prove pedagogical quality or absence of subtle leakage.
```

The main regression case is `repair_stress_004`: the second-pass guard still judged the repaired tree-difference worked example as a critical bridge leak.

## How To Review

Open this workbook for coach blind review:

```text
docs/research/coach_response_review_workbook_repair_stress_v1_all20_20260511.zh.xlsx
```

Do not show this key file to the coach:

```text
docs/research/coach_response_review_workbook_repair_stress_v1_all20_20260511.key.csv
```

The workbook contains 40 anonymized rows: before candidate and after repair for each stress case.

## Next Step

1. Have the coach fill the all20 before/after workbook.
2. Compare before vs after quality, leakage, and student-ready pass.
3. Add `repair_stress_004` to Repair prompt or Leakage Guard regression.
4. Decide whether Repair belongs in the 50-case held-out main table or only in appendix/stress-test analysis.
