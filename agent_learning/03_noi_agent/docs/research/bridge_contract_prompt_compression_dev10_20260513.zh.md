# Bridge Contract Prompt 压缩 Dev10 结果（2026-05-13）

## 目的

本轮实验检查 Bridge Contract 生成 prompt 是否过重。我们不直接替换原 prompt，而是新增 compact/minimal 两个离线条件，与 long Bridge Contract 和 DBox-inspired guard 做开发阶段比较。

该结果来自 AI 自评，用于 dev 筛查，不是教练 gold label，也不是论文正式 headline result。

## 数据和条件

输入数据：

```text
docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl
```

选取 10 个覆盖不同 bridge bucket 的 case：

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

条件：

```text
dbox_inspired_guard
bridge_contract_guard
bridge_contract_compact_guard
bridge_contract_minimal_guard
```

最终输出目录：

```text
evals/aichat/ad_hoc_runs/prompt_compression_dev10_20260513_final/
```

## 完整性

最终合并包通过完整性检查：

```text
case_count = 10
condition_count = 4
combined_row_count = 40
final_response_row_count = 40
review_row_count = 40
empty_final_response_rows = 0
stage_warning_rows = 0
headline_ready = true
analysis_ready = true
```

## Prompt 长度

```text
long = 2848 chars
compact = 934 chars，约 long 的 33%
minimal = 719 chars，约 long 的 25%
```

## AI 自评摘要

| condition | overall | core6 | student_ready_pass | minor leakage | major/answer leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| dbox_inspired_guard | 3.90 | 1.98 | 9/10 | 1 | 0 |
| bridge_contract_compact_guard | 3.80 | 1.97 | 8/10 | 2 | 0 |
| bridge_contract_minimal_guard | 3.70 | 1.93 | 8/10 | 1 | 1 |
| bridge_contract_guard | 3.20 | 1.82 | 4/10 | 3 | 2 |

## 主要观察

1. `bridge_contract_compact_guard` 明显优于 long `bridge_contract_guard`：
   - student-ready 从 4/10 提升到 8/10；
   - major/answer leakage 从 2 降到 0；
   - overall 从 3.20 提升到 3.80。

2. `bridge_contract_minimal_guard` 不建议直接采用：
   - 质量比 long 高；
   - 但出现 1 条 major leakage；
   - 说明过度压缩会削弱关键桥控制。

3. `dbox_inspired_guard` 仍是强 baseline：
   - AI 自评中 student-ready 为 9/10；
   - major/answer leakage 为 0；
   - 这说明 DBox-inspired decomposition 仍值得保留为正式强 baseline。

4. long Bridge Contract 的主要问题不是“不够安全”，而是容易把提示写成过重的规则控制，反而产生 answer-slot 或过完整推理：
   - 例如把“下一步往哪边移动”“从哪里转来”直接问成答案槽；
   - 或把局部观察组织成接近完整转移/边界更新的问题。

## 当前建议

不要把 `bridge_contract_minimal` 进入正式主表。

`bridge_contract_compact` 值得进入下一轮人工盲评候选，因为它在 dev10 AI 自评中接近 DBox-inspired，并明显优于 long Bridge Contract。

下一步应做：

```text
1. 保留 long bridge_contract_guard 作为历史/消融对照。
2. 将 bridge_contract_compact_guard 加入下一轮教练盲评候选。
3. 不直接替换正式 prompt，等人工盲评确认。
4. 如果人工盲评也支持 compact，则考虑将 compact 作为 held-out 主实验的 Bridge Contract 版本。
```

## 重要边界

该结果是 AI self-review，不能作为正式论文结论。它的作用是筛选候选 prompt，并说明“prompt 越长不一定越好”。是否采用 compact 版本，必须由后续教练盲评和 held-out 实验决定。
