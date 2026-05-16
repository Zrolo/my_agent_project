# Bridge Contract Compact Human Review Pack (2026-05-13)

## Purpose

The `prompt_compression` dev10 AI self-review suggested that `bridge_contract_compact_guard` may be a better next candidate than the long `bridge_contract_guard`. Because that signal comes from AI self-review, it cannot be treated as formal evidence.

This pack provides a small human blind-review set to check whether the compact-prompt improvement is real.

## Conditions

Each case contains four anonymized responses:

```text
enhanced_prompt_only_clean
single_llm_structured_guard
dbox_inspired_guard
bridge_contract_compact_guard
```

They represent:

- strong prompt-only baseline;
- structured single-LLM + guard;
- DBox-inspired decomposition + guard;
- Bridge Contract compact + guard.

## Data

The pack uses the same 10 cases as the `prompt_compression` dev10 run, covering:

```text
state_representation_semantics
transition_recurrence_source
predicate_check_semantics
boundary_update_order
modeling_object_relation
aggregation_contribution_summary
data_structure_operation_semantics
correctness_invariant
implementation_boundary
policy_request
```

## Outputs

Standard blind-review workbook:

```text
evals/aichat/ad_hoc_runs/prompt_compression_human_review_pack_20260513/coach_response_review_workbook_prompt_compression_human_review_20260513.zh.xlsx
```

By-case workbook:

```text
evals/aichat/ad_hoc_runs/prompt_compression_human_review_pack_20260513/coach_response_review_workbook_prompt_compression_by_case_20260513.zh.xlsx
```

Key file:

```text
evals/aichat/ad_hoc_runs/prompt_compression_human_review_pack_20260513/coach_response_review_workbook_dev_ablation.key.csv
```

The key file contains true conditions and must not be given to blind-review coaches.

## Integrity

```text
case_count = 10
condition_count = 4
review_row_count = 40
empty_response_rows = 0
problem_statement_present = 40/40
recent_dialogue_present = 40/40
context_ai_reply_present = 32/40
condition_hidden_from_review = true
by_case_sheets = 10
```

## Use

Prefer the by-case workbook for coach review, because it lets reviewers compare four anonymized responses for the same case side by side. Each response should still be scored independently; `coach_preference_rank` can be used within the same case.

This pack is only for deciding whether:

```text
bridge_contract_compact_guard should enter the next held-out candidate set.
```

Do not treat this review pack as a formal paper result.
