# Single-LLM Structured Baseline: Scaffold Calibration Smoke

Date: 2026-05-10

## Purpose

The strict single-LLM structured baseline fixed schema drift, but the previous smoke run selected `L1` for all three diagnostic learning turns. This run checks whether explicit scaffold-level calibration can make the one-call baseline choose `L2` when a bridge-oriented micro-example is appropriate.

## Change

The `single_llm_structured` system prompt now includes:

- explicit `L0/L1/L2/L3` scaffold-level boundaries;
- a rule that diagnosable learning turns with a clear missing bridge may use `L2` micro-examples or partial traces;
- an anti-leakage warning that forbidden content must not be wrapped as a hypothetical statement;
- a self-check rule: if the student-facing response directly or indirectly states forbidden content, `self_check.predicted_leakage_risk` must be `medium` or `high`.

## Command

```bash
NOI_CHAT_TIMEOUT_SECONDS=180 NOI_CHAT_MAX_COMPLETION_TOKENS=9000 \
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/single_llm_structured_calibrated_smoke_20260510/single_llm_structured_calibrated_antileak_tutor_only_smoke3.jsonl \
  --limit 3 \
  --tutor-mode single_llm_structured \
  --pipeline-mode tutor_only \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode disabled \
  --judge-schema-mode retrieval_augmented_compact_judge
```

## Results

| Variant | Cases | Errors | LLM calls / turn | p50 latency | p95 latency | Bridge family acc. | Focus acc. | Help level acc. | Invalid labels |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Loose one-call prompt | 3 | 0 | 1.0 | 5828.631 ms | 5908.953 ms | 0.0 | 0.0 | 0.333 | 1.0 |
| Strict enum + top-k focus | 3 | 0 | 1.0 | 6413.114 ms | 7712.401 ms | 1.0 | 1.0 | 0.0 | 0.0 |
| Calibrated + anti-leak prompt | 3 | 0 | 1.0 | 8171.739 ms | 8410.813 ms | 1.0 | 1.0 | 1.0 | 0.0 |

## Interpretation

Scaffold-level calibration fixed the over-conservative `L1` behavior in this three-case smoke run. The one-call baseline now matches bridge family, registered focus, and help level for all three cases.

However, the generated responses still show why the one-call baseline should remain a baseline rather than the default production controller. In two cases, the model's own `self_check` marked leakage risk as `medium`. The DP state-design response still gives strong cues about the state contents, even though it avoids a full recurrence. This supports keeping an independent Leakage Judge / Repair path in the research ablation.

## Artifacts

- JSONL: `evals/aichat/ad_hoc_runs/single_llm_structured_calibrated_smoke_20260510/single_llm_structured_calibrated_antileak_tutor_only_smoke3.jsonl`
- Summary JSON: `evals/aichat/ad_hoc_runs/single_llm_structured_calibrated_smoke_20260510/single_llm_structured_calibrated_antileak_tutor_only_smoke3_summary.json`
- English summary: `evals/aichat/ad_hoc_runs/single_llm_structured_calibrated_smoke_20260510/single_llm_structured_calibrated_antileak_tutor_only_smoke3_summary.md`
- Chinese summary: `evals/aichat/ad_hoc_runs/single_llm_structured_calibrated_smoke_20260510/single_llm_structured_calibrated_antileak_tutor_only_smoke3_summary.zh.md`
