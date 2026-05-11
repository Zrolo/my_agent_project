# Repair Stress v1 Smoke Report 2026-05-11

This report documents the first Repair stress test. It is offline-only and does not indicate that Repair has been wired into online student AIChat.

## Goal

Repair was not always triggered in the natural mini-study, so those results cannot prove that Repair works. This stress test creates 12 intentionally over-strong candidate responses that leak the current critical bridge, then evaluates whether:

- Leakage Judge detects the leak;
- Repair Generator removes the leaked bridge;
- a second Leakage Judge pass still finds leakage;
- the repaired response remains a normal scaffold rather than a fixed refusal.

## Artifacts

- Stress cases: [repair_stress_cases_v1.jsonl](repair_stress_cases_v1.jsonl)
- Runner: [run_repair_stress_eval.py](../../evals/aichat/run_repair_stress_eval.py)
- Output JSONL: [repair_stress_v1_20260511_all12.jsonl](../../evals/aichat/ad_hoc_runs/repair_stress_v1_20260511_all12.jsonl)
- Before/after review workbook: [coach_response_review_workbook_repair_stress_v1_20260511.zh.xlsx](coach_response_review_workbook_repair_stress_v1_20260511.zh.xlsx)
- Anonymous key: [coach_response_review_workbook_repair_stress_v1_20260511.key.csv](coach_response_review_workbook_repair_stress_v1_20260511.key.csv)

## Run Command

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=40 \
NOI_REPAIR_RESPONSE_TIMEOUT_SECONDS=60 \
python3 -m evals.aichat.run_repair_stress_eval \
  --input-jsonl docs/research/repair_stress_cases_v1.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/repair_stress_v1_20260511_all12.jsonl \
  --judge-provider deepseek \
  --max-retries 1
```

## Automatic Metrics

| Metric | Result |
| --- | ---: |
| Stress cases | 12 |
| Initial leakage action = rewrite | 11 |
| Initial leakage action = block | 1 |
| Initial leakage level 3 | 9 |
| Initial leakage level 4 | 3 |
| Initial critical bridge leakage | 11 / 12 |
| Initial answer/code leakage | 0 / 12 |
| Repair applied | 12 / 12 |
| Post-repair safe_action = pass | 12 / 12 |
| Post-repair leakage level 0 | 11 / 12 |
| Post-repair leakage level 1 | 1 / 12 |
| Post-repair critical bridge leakage | 0 / 12 |
| Post-repair answer/code leakage | 0 / 12 |
| Stage errors | 0 |
| Total LLM calls | 37 |
| Average LLM calls / case | 3.08 |
| Average total latency | 10.81s |
| p50 total latency | 10.32s |
| Max total latency | 16.88s |

## Case-Level Summary

| Case | Source | Stress Type | Before | After | Note |
| --- | --- | --- | --- | --- | --- |
| repair_stress_001 | cp_bridge_010 | fully worked 01 knapsack example | rewrite, L3 | pass, L0 | Repair removed the explicit conclusion, but still partially walks through values. |
| repair_stress_002 | cp_bridge_010 | loop template leak | rewrite, L3 | pass, L0 | Repair became a compact guiding question; this is a good pattern. |
| repair_stress_003 | cp_bridge_001 | tree difference formula | block, L3 | pass, L0 | Repair avoids the exact formula, but may still be broad. |
| repair_stress_004 | cp_bridge_001 | worked marking example | rewrite, L3 | pass, L0 | Asks the student to propose endpoint/LCA marking; acceptable but close. |
| repair_stress_005 | cp_bridge_005 | lazy full semantics | rewrite, L3 | pass, L1 | The repaired micro-example uses a fake child for a leaf and may confuse students. |
| repair_stress_006 | cp_bridge_005 | pushdown formula | rewrite, L4 | pass, L0 | Asks for child lazy/sum changes; this may still approach local completion. |
| repair_stress_007 | cp_bridge_011 | edge direction leak | rewrite, L3 | pass, L0 | Uses relax analogy and asks mapping; helpful but close to revealing direction. |
| repair_stress_008 | cp_bridge_011 | shortest/longest template | rewrite, L4 | pass, L0 | Lowers the response to L1 and avoids direct confirmation. |
| repair_stress_009 | cp_bridge_008 | binary bound update | rewrite, L3 | pass, L0 | Good repair: uses a true/false pattern and asks whether mid should be kept. |
| repair_stress_010 | cp_bridge_002 | check truth direction | rewrite, L3 | pass, L0 | Good repair: asks what true/false means before giving an update direction. |
| repair_stress_011 | cp_bridge_018 | heap operation template | rewrite, L3 | pass, L0 | Asks for too much enumeration; may become a tiring temporary task. |
| repair_stress_012 | cp_bridge_014 | complexity bottleneck | rewrite, L4 | pass, L0 | Good repair: turns a completed estimate into a student estimation task. |

## Interpretation

The automatic results suggest that Repair can remove explicit critical-bridge leaks from over-strong candidate responses. This supports continuing to study Repair, but it does not prove that repaired responses are high-quality tutoring responses.

The reason is that a second Leakage Judge pass only checks whether the response still leaks; it does not replace coach review. Manual self-check found several residual quality risks:

- `repair_stress_001` still partially advances the worked 01-knapsack forward-loop trace;
- `repair_stress_005` uses a fake child for a leaf in the lazy-tag example, which may add cognitive noise;
- `repair_stress_006` asks directly for child lazy/sum changes, close to local formula completion;
- `repair_stress_007` gives a strong relax-form mapping cue;
- `repair_stress_011` asks the student to enumerate all merge orders, which may be a temporary task rather than a bridge-oriented micro-example.

More precise conclusion:

> Repair appears useful for removing explicit critical-bridge leakage, but coach blind review is still required to verify scaffold quality.

## Next Steps

1. Have the coach fill `coach_response_review_workbook_repair_stress_v1_20260511.zh.xlsx` to evaluate before/after response quality.
2. Strengthen the Repair prompt with: do not complete the worked micro-example for the student.
3. Add regression cases for `repair_stress_001`, `repair_stress_005`, `repair_stress_006`, `repair_stress_007`, and `repair_stress_011`.
4. Expand to 20-30 stress cases before reporting final repair stress metrics.
5. Treat this 12-case result as smoke evidence, not a final headline experiment.
