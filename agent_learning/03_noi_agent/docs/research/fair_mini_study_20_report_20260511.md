# Fair 20-Case Mini-Study Report (2026-05-11)

This run compares `current_system`, `single_llm_structured`, `bridge_contract`, Guard, and Repair on the same 20 seed cases. The goal is not to claim a final winner, but to make the ablation fair: Guard and Repair are evaluated not only after Bridge Contract, but also after the strong single-LLM baseline.

## Setup

- Input set: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Tutor provider: `deepseek_flash`
- Judge provider: `deepseek`
- Chat thinking mode: `disabled`
- Judge schema: `retrieval_augmented_compact_judge`
- Guard mode: `predicted`
- Output directory: `evals/aichat/ad_hoc_runs/fair_mini_study_20_20260511/`
- Combined output: `combined_fair_mini_study_20.jsonl`
- Summary: `combined_fair_mini_study_20_summary.json`
- Chinese blind-review workbook: `docs/research/coach_response_review_workbook_fair_mini_study_20_20260511.zh.xlsx`

During the run, the `bridge_contract + guard` and `bridge_contract + guard + repair` groups initially hit DeepSeek API `APITimeoutError` / `APIConnectionError` failures in Bridge Judge or Leakage Judge stages. After rerunning with higher `max_retries`, all seven groups completed 20/20 cases and the final summary has no stage errors.

## System Matrix

| System | Pipeline | Cases | Errors | Bridge family acc. | Registered focus acc. | Avg LLM calls | P50 latency |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| current_system | tutor_only_no_diagnosis | 20 | 0 | n/a | n/a | 1.00 | 6.24s |
| single_llm_structured | tutor_only | 20 | 0 | 0.90 | 0.80 | 1.05 | 6.84s |
| single_llm_structured + guard | tutor_plus_guard | 20 | 0 | 0.90 | 0.80 | 2.05 | 12.04s |
| single_llm_structured + guard + repair | tutor_plus_guard_plus_repair | 20 | 0 | 0.90 | 0.80 | 2.15 | 12.01s |
| bridge_contract | tutor_only | 20 | 0 | 0.90 | 0.80 | 2.00 | 13.85s |
| bridge_contract + guard | tutor_plus_guard | 20 | 0 | 0.90 | 0.80 | 3.40 | 21.73s |
| bridge_contract + guard + repair | tutor_plus_guard_plus_repair | 20 | 0 | 0.90 | 0.80 | 3.70 | 20.43s |

## Guard / Repair Automatic Metrics

These metrics come from Leakage Judge, not coach blind-review labels. They are useful for risk tracing, but they are not final paper-quality judgments.

| System | Leakage rate | Critical bridge leakage rate | Rewrite rate | Repair rate | P95 latency |
| --- | ---: | ---: | ---: | ---: | ---: |
| single_llm_structured + guard | 0.10 | 0.00 | 0.10 | 0.00 | 14.21s |
| single_llm_structured + guard + repair | 0.15 | 0.10 | 0.15 | 0.15 | 15.54s |
| bridge_contract + guard | 0.10 | 0.05 | 0.10 | 0.00 | 31.78s |
| bridge_contract + guard + repair | 0.05 | 0.00 | 0.05 | 0.05 | 36.22s |

## Initial Observations

1. `single_llm_structured` is a strong baseline: on these 20 cases, its bridge-family and registered-focus accuracies match Bridge Contract while running faster.
2. Bridge Contract has a clear latency and call-count cost: even tutor-only mode roughly doubles the P50 latency of single-LLM tutor-only; Guard/Repair further increase the P95 latency.
3. Guard/Repair value cannot be judged by automatic leakage metrics alone. Both `single_llm + guard + repair` and `bridge_contract + guard + repair` trigger rewrite/repair, but coach blind review is needed to determine whether they preserve teaching quality.
4. The defensible paper claim is not “multi-stage architecture is always better.” It is: this framework compares strong single-LLM, Bridge Contract, Guard, and Repair under the same quality/leakage/latency protocol.

## Next Step

1. Have the coach review `coach_response_review_workbook_fair_mini_study_20_20260511.zh.xlsx`.
2. Generate bilingual blind-review analysis, focusing on:
   - which system produces better tutor responses;
   - whether Guard reduces critical bridge leakage;
   - whether Repair preserves teaching quality;
   - whether bridge-oriented micro-examples outperform generic micro-examples.
   - whether overall quality, would-show-to-student, and reviewer confidence agree with dimension-level scores.
3. If the single-LLM baseline remains strong under blind review, it should become the main baseline rather than a weak strawman.

## Boundary

This report only shows that the seven offline chains run end-to-end and provides automatic diagnosis, Guard, and latency metrics. It does not prove teaching-quality superiority; final response quality requires coach blind review.
