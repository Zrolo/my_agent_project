# 50-case Generation-only Runbook (2026-05-14)

This runbook defines the next **50-case generation-only** large-sample run. It only checks whether each condition can reliably produce reviewable responses. It does not include AI self-review, coach blind review, or paper-level conclusions.

## Goal

This run answers an engineering and experimental feasibility question:

```text
Across 50 held-out draft cases, can these five candidate conditions reliably generate reviewable tutor responses?
```

It does not answer:

```text
Which condition has the best pedagogical quality;
whether one condition significantly outperforms DBox;
whether Bridge Contract is the final paper winner;
whether Guard causally improves quality.
```

Those questions require coach blind review and formal held-out analysis.

## Input Data

Current input:

```text
docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl
```

Important notes:

- This is still a `draft`, not a frozen gold/reference dataset.
- This run is a generation-only stability check.
- If prompts are modified after this run, these generated responses cannot be used as formal paper headline results.
- v4 is a follow-up scaffold version derived from v3: the first 10 short no-context cases receive a minimal synthetic-but-grounded prior AI probe, so the main scaffolding comparison does not force models to infer the student's stuck point from the problem statement alone.
- v3 remains available as a mixed dataset and can be reported separately as a `clarification_safety_slice`; old v2 results should be kept only as development diagnostics.

## Context Injection

This run must use **AIChat-compatible context injection**. The offline runner follows the online `/chat` path:

```text
full_history[-10:]
-> append current user message built from:
   student_message
   problem title/url/context
   student_code_excerpt
   context strategy
```

Requirements:

- If a case has `prior_messages`, use them as the dialogue history.
- If it has no `prior_messages` but has `recent_dialogue`, parse `学生：... / AI：...` into real `user/assistant` messages.
- `student_message` must be the final user message and must not be embedded as another final turn inside `recent_dialogue`.
- `student_code_excerpt` is included in the current user message, matching the online AIChat `学生当前代码` field.
- Result rows must record `generation_context_source` and `generation_message_count`.

This is a precondition for the rerun. Otherwise, coaches would review with context that the model never saw, which makes the evaluation unfair.

## Condition Set

Use the existing condition set:

```text
--condition-set dbox_bridge_hybrid
```

It contains five conditions:

| condition_id | tutor_mode | pipeline_mode | Role in this run |
| --- | --- | --- | --- |
| `enhanced_prompt_only_clean` | `enhanced_prompt_only` | `tutor_only_no_diagnosis` | Strong prompt-only baseline |
| `dbox_inspired_clean` | `dbox_inspired_decomposition_tutor` | `tutor_only_no_diagnosis` | DBox-style no-Guard baseline |
| `dbox_inspired_guard` | `dbox_inspired_decomposition_tutor` | `tutor_plus_guard` | Guarded DBox baseline |
| `bridge_contract_compact_guard` | `bridge_contract_compact` | `tutor_plus_guard` | Current Bridge Contract main candidate |
| `bridge_guided_dbox_style_guard` | `bridge_guided_dbox_style_tutor` | `tutor_plus_guard` | Temporarily retained hybrid appendix/dev candidate |

`bridge_guided_dbox_style_guard` performed poorly in the 10-case human review, but it is temporarily retained here to observe whether the same instability persists at 50 cases. Unless later coach review reverses this finding, it should not enter the formal main table.

## Fixed Model Configuration

This run does not compare models. All conditions use the same fixed generation configuration:

```text
Tutor provider: deepseek_flash
Tutor model: deepseek-v4-flash
Tutor thinking mode: enabled
Tutor max tokens: 128k (`NOI_CHAT_MAX_COMPLETION_TOKENS=131072`)
Judge provider: deepseek
Judge model: deepseek-v4-flash
Judge thinking mode: disabled
Judge / Repair max tokens: 20k (`NOI_BRIDGE_JUDGE_MAX_TOKENS=20480`, `NOI_LEAKAGE_JUDGE_MAX_TOKENS=20480`, `NOI_REPAIR_RESPONSE_MAX_TOKENS=20480`)
Max retries: 1
```

To reduce generation-only row loss from incidental timeouts, use:

```text
NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=25
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25
NOI_REPAIR_RESPONSE_TIMEOUT_SECONDS=25
NOI_BRIDGE_JUDGE_MAX_TOKENS=20480
NOI_LEAKAGE_JUDGE_MAX_TOKENS=20480
NOI_REPAIR_RESPONSE_MAX_TOKENS=20480
NOI_CHAT_MAX_COMPLETION_TOKENS=131072
```

The 2026-05-14 3-case post-level-tag smoke showed that the default 5s timeout can produce empty final responses and missing review rows. With `timeout=25s` and `--max-retries 1`, both smoke runs reached `empty_final_response_count=0`, `stage_errors=0`, and `review_row_count=combined_row_count`. Therefore, the 50-case generation-only run should not use the default 5s Judge timeout.

This run follows the latest requirement: tutor thinking is enabled and tutor max tokens are set to 128k. Judges remain thinking-disabled; enabling judge thinking would be a separate evaluation configuration.

## Command

```bash
NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=25 \
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
NOI_REPAIR_RESPONSE_TIMEOUT_SECONDS=25 \
NOI_BRIDGE_JUDGE_MAX_TOKENS=20480 \
NOI_LEAKAGE_JUDGE_MAX_TOKENS=20480 \
NOI_REPAIR_RESPONSE_MAX_TOKENS=20480 \
NOI_CHAT_MAX_COMPLETION_TOKENS=131072 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --condition-set dbox_bridge_hybrid \
  --input-jsonl docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --chat-thinking-mode enabled \
  --max-retries 1
```

Expected size:

```text
50 cases × 5 conditions = 250 rows
```

## Outputs

The runner will generate:

```text
combined_dev_ablation.jsonl
combined_dev_ablation_summary.json
combined_dev_ablation_summary.zh.md
coach_response_review_workbook_dev_ablation.csv
coach_response_review_workbook_dev_ablation.zh.xlsx
coach_response_review_workbook_dev_ablation.key.csv
manifest.json
```

The review workbook is generated only to confirm that the run can later be handed to coaches. Do not fill it immediately.

## Integrity Check

Run immediately after generation:

```bash
python3 -m evals.aichat.check_ablation_run_integrity \
  --manifest evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514/manifest.json \
  --output-json docs/research/dbox_bridge_hybrid_generation_only_50_integrity_20260514.json \
  --output-md docs/research/dbox_bridge_hybrid_generation_only_50_integrity_20260514.md
```

The current integrity checker supports only `--output-json` and `--output-md`. If a Chinese integrity report is needed, extend the checker first instead of adding `--output-md-zh` to this command.

Generation-only go conditions:

```text
expected_row_count = 250
combined_row_count = 250
final_response_row_count = 250
review_row_count = 250
empty_final_response_count = 0
duplicate_case_condition_count = 0
missing_case_condition_count = 0
```

A small number of non-blocking stage warnings may be acceptable, but must be recorded:

```text
Bridge Judge timeout
Leakage Judge timeout
JSON parse error
Guard unknown
fallback response
```

If any row has an empty final response or a missing case-condition pair, do not move to coach review. Run targeted reruns first.

## Targeted Rerun

If the integrity check finds a missing or empty `(case_id, condition_id)` pair:

```bash
NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=25 \
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
NOI_REPAIR_RESPONSE_TIMEOUT_SECONDS=25 \
NOI_BRIDGE_JUDGE_MAX_TOKENS=20480 \
NOI_LEAKAGE_JUDGE_MAX_TOKENS=20480 \
NOI_REPAIR_RESPONSE_MAX_TOKENS=20480 \
NOI_CHAT_MAX_COMPLETION_TOKENS=131072 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --condition-set dbox_bridge_hybrid \
  --condition-id CONDITION_ID \
  --case-id CASE_ID \
  --input-jsonl docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514_targeted/CONDITION_ID_CASE_ID \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --chat-thinking-mode enabled \
  --max-retries 1
```

Merge:

```bash
python3 -m evals.aichat.merge_ablation_reruns \
  --source-manifest evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514/manifest.json \
  --retry-manifest evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514_targeted/CONDITION_ID_CASE_ID/manifest.json \
  --output-dir evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514_merged
```

Run the integrity check again after merging.

## Metrics To Inspect In This Run

Only inspect stability and cost:

- row count;
- empty final response;
- stage error;
- timeout;
- JSON parse error;
- review workbook row count;
- LLM calls per turn;
- p50/p95 latency;
- Guard rewrite/block/unknown rate;
- final static risk, for triage only.

Do not interpret:

- overall quality;
- ready/safe_ready;
- condition win/loss;
- coach preference;
- significant superiority over any baseline.

## Decision After This Run

If all 250 rows are reviewable:

1. Do not modify prompts immediately.
2. Decide whether to give the workbook to coaches.
3. If using coach review, first sample-check 20-50 rows to confirm the workbook includes enough problem/context information.
4. Then decide whether to launch formal 50-case blind review.

If one condition is clearly unstable:

1. Record it as a stability risk.
2. Only make engineering fixes, such as schema aliases, JSON format, or timeout handling.
3. Do not make broad pedagogical prompt changes.
4. Rerun only affected condition/case pairs.

If `bridge_guided_dbox_style_guard` remains clearly worse or unstable:

- downgrade it to appendix/error-analysis status;
- keep it out of the formal main table;
- use it to show that simply combining Bridge Contract with DBox-style decomposition does not automatically improve tutoring quality.

## Prohibited Actions

This run must not:

- claim which system is better based on generation-only outputs;
- replace coach review with AI self-review;
- modify prompts while the run is in progress;
- treat static risk as the paper leakage result;
- treat this `draft` dataset as frozen held-out gold.
