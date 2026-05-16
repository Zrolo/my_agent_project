# Bridge Contract Compact 人工盲评包（2026-05-13）

## 目的

`prompt_compression` dev10 的 AI 自评显示，`bridge_contract_compact_guard` 可能比 long `bridge_contract_guard` 更适合作为 Bridge Contract 的下一轮候选。但该结论来自 AI 自评，不能作为正式论文证据。

本轮生成一个小型人工盲评包，用于确认 compact prompt 的提升是否真实。

## 条件

每个 case 包含 4 条匿名回复：

```text
enhanced_prompt_only_clean
single_llm_structured_guard
dbox_inspired_guard
bridge_contract_compact_guard
```

这些条件分别代表：

- 强 prompt-only baseline；
- structured single-LLM + guard；
- DBox-inspired decomposition + guard；
- Bridge Contract compact + guard。

## 数据

使用与 `prompt_compression` dev10 相同的 10 个 case，覆盖：

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

## 输出

标准盲评表：

```text
evals/aichat/ad_hoc_runs/prompt_compression_human_review_pack_20260513/coach_response_review_workbook_prompt_compression_human_review_20260513.zh.xlsx
```

按同一题分 sheet 的盲评表：

```text
evals/aichat/ad_hoc_runs/prompt_compression_human_review_pack_20260513/coach_response_review_workbook_prompt_compression_by_case_20260513.zh.xlsx
```

Key 文件：

```text
evals/aichat/ad_hoc_runs/prompt_compression_human_review_pack_20260513/coach_response_review_workbook_dev_ablation.key.csv
```

Key 文件包含真实 condition，不给盲评教练。

## 完整性

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

## 使用方式

建议优先使用按题分 sheet 的版本，因为教练可以在同一题内横向比较 4 条匿名回复。评分时仍按每条回复独立打分，`coach_preference_rank` 可在同一题内排序。

该盲评结果只用于决定：

```text
bridge_contract_compact_guard 是否进入下一轮 held-out 候选。
```

不要把本包结果直接写成正式论文结论。
