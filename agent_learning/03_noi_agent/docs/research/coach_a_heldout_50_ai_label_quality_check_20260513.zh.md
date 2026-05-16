# Coach A Held-out 50 AI 初标质量检查（2026-05-13）

## 结论

本检查对象是 `coach_a_heldout_50_ai_labeled_v1_20260513.jsonl`。它可以作为 **AI-assisted draft reference** 进入下一步开发分析，但不应直接称为最终 gold label。

检查结论：

- 行数：50
- 与 `bridgebench_cp_heldout_v1_50_draft.jsonl` 的 `case_id` 集合一致：是
- 重复 case_id：0
- deprecated bridge subtype：0
- family-subtype mismatch：0
- `needs_new_focus` 但缺少候选名：0
- 置信度范围错误：0
- 建议人工复核：7 个低置信 case + 5 个 needs_new_focus case + 若干多桥/歧义 case

## 数据集门检

`bridgebench_cp_heldout_v1_50_draft.jsonl` 已通过 held-out 50 数据集验证：

- row_count：50
- category 覆盖：
  - `binary_search_boundary`: 4
  - `binary_search_predicate`: 5
  - `data_structure_semantics`: 5
  - `debugging_evidence`: 4
  - `dp_state`: 5
  - `dp_transition`: 5
  - `graph_tree_modeling`: 5
  - `greedy_correctness`: 5
  - `implementation_boundary`: 5
  - `policy_request`: 7
- recent dialogue 分布：
  - none: 10
  - short: 25
  - long: 15
- student_code_excerpt 分布：
  - none: 38
  - present: 12
- dev seed case id overlap：0 errors

## 标注分布

### Bridge Family

- `predicate_condition_bridge`: 8
- `debugging_evidence_bridge`: 6
- `representation_state_bridge`: 6
- `implementation_boundary_bridge`: 5
- `correctness_invariant_bridge`: 4
- `method_selection_bridge`: 4
- `transition_recurrence_bridge`: 4
- `unknown_or_not_applicable`: 4
- `modeling_bridge`: 3
- `aggregation_contribution_bridge`: 2
- `data_structure_operation_bridge`: 2
- `goal_constraint_bridge`: 1
- `ordering_dependency_bridge`: 1

### Bridge Subtype

- `predicate.boundary_update_direction`: 4
- `correctness.local_choice_exchange_argument`: 3
- `debug.minimal_failing_case`: 3
- `policy.direct_answer_request`: 3
- `predicate.feasibility_truth_direction`: 3
- `aggregation.cumulative_range_query`: 2
- `debug.wa_counterexample_construction`: 2
- `implementation.integer_overflow`: 2
- `method.stateful_subproblem_signal`: 2
- `state.augmented_process_state`: 2
- `state.table_or_memo_cell_semantics`: 2
- `transition.combinatorial_recurrence`: 2
- 其他 subtype：各 1

### Leakage Risk

- `high`: 37
- `medium`: 10
- `low`: 3

### Coach Confidence

- `5`: 28
- `4`: 15
- `3`: 7

## 需要人工优先复核的样本

### 低置信 case

- `heldout_cp_007`
- `heldout_cp_018`
- `heldout_cp_022`
- `heldout_cp_031`
- `heldout_cp_034`
- `heldout_cp_038`
- `heldout_cp_043`

### needs_new_focus case

- `heldout_cp_018`: `binary_search_answer_range_bounds`
- `heldout_cp_031`: `fenwick_index_range_semantics`
- `heldout_cp_034`: `rolling_hash_weight_alignment`
- `heldout_cp_038`: `modular_normalization_negative_remainder`
- `heldout_cp_043`: `debug_invariant_probe`

### 多桥 / 可接受非唯一 case

- `heldout_cp_003`
- `heldout_cp_004`
- `heldout_cp_007`
- `heldout_cp_008`
- `heldout_cp_014`
- `heldout_cp_015`
- `heldout_cp_018`
- `heldout_cp_019`
- `heldout_cp_022`
- `heldout_cp_024`
- `heldout_cp_026`
- `heldout_cp_027`
- `heldout_cp_029`
- `heldout_cp_031`
- `heldout_cp_033`
- `heldout_cp_034`
- `heldout_cp_038`
- `heldout_cp_042`
- `heldout_cp_043`

## 一个注意点

`heldout_cp_049` 是 `debugging_evidence_bridge`，其 `bridge_specific_forbidden_content` 为空，但 `general_forbidden_content` 已包含 `no_guess_without_context` 和 `no_full_solution`。

这不是当前 schema 的硬错误，因为调试证据不足类样本有时没有具体“关键桥公式”可禁止。后续如果希望所有非 policy case 都有 bridge-specific forbidden content，可以考虑新增一个更贴合调试证据的 forbidden label，例如：

```text
no_specific_bug_fix_without_evidence
```

当前不建议为这一条临时新增标签，以免在正式 50-case 前继续扩大 schema。

## 研究口径

这份 AI 初标目前适合：

- 作为 dev-stage reference draft；
- 生成系统回复时提供 provisional reference；
- 帮助发现 schema pain points；
- 辅助 Coach A / Coach B 后续人工复核。

不适合：

- 直接称为 final gold label；
- 直接用于论文 headline agreement；
- 跳过人工复核后进入正式 held-out 主结论。

## 下一步

建议下一步进入 **50-case response generation ablation**：

1. 固定 condition set。
2. 用这 50 个 case 批量生成各系统回复。
3. 导出匿名中文盲评表。
4. 让教练评审 AI 回复质量和泄露。
5. 做 paired analysis 和 quality-leakage-cost trade-off 分析。
