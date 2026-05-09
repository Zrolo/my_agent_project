# Human Annotation Schema vs Runtime Bridge Contract v1

本文件固定一个边界：教练标注表可以细，运行时 Judge 必须轻。两者服务的目标不同，不能把 `coach_seed_labeling_workbook_v2` 的所有字段原样塞给在线 AIChat 或一次性要求 Judge LLM 全部预测。

## 为什么要拆成两套

`coach_seed_labeling_workbook_v2` 面向论文数据建设。它需要支持教练复核、分歧讨论、错误分析和数据集扩展，所以保留 `secondary_bridge_family`、`secondary_bridge_subtype_id`、`evidence_quote`、`coach_free_notes`、`new_focus_candidate` 等细字段。

注意：人类标注字段是 expert reference，不是天然唯一真值。单个教练导出的文件应称为 `single_coach_reference`；只有经过双标和分歧裁决的文件才应称为 `adjudicated_gold`。可靠性流程见 [annotation_reliability_protocol_v1.md](/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/research/annotation_reliability_protocol_v1.md)。

运行时 Bridge Judge 面向快速路由和 tutor 控制。它只需要输出一个紧凑的 bridge contract，告诉主 tutor：

- 这一轮属于什么交互场景；
- 学生当前最主要缺哪类 bridge；
- 应该最多给到什么脚手架强度；
- 可以用哪一两种帮助形式；
- 本轮不能直接补完什么；
- 这一轮泄露关键桥的风险有多高。

## 字段映射

| Human Annotation 字段 | Runtime Bridge Contract 字段 | 说明 |
| --- | --- | --- |
| `turn_type` | `turn_type` | 直接映射，但 runtime 可用 `unknown` 表示不确定。 |
| `diagnosis_uncertainty` | `diagnosis_uncertainty` | 直接映射；用于决定是否先追问证据。 |
| `student_problem_solving_state` | 不直接进入 contract | 作为离线评估和误差分析字段；runtime 可把它压缩进自然语言 `student_state_summary`。 |
| `policy_risk_type` | 不直接进入 contract | 主要用于 route policy；明显完整代码/题解请求可以走 deterministic safe response。 |
| `primary_bridge_family` | `primary_bridge_family` | 运行时只保留主桥梁大类。 |
| `primary_bridge_subtype_id` | 不要求每轮预测 | 可由 `selected_focus_id` 或自然语言 missing bridge summary 间接表达。 |
| `secondary_bridge_family` / `secondary_bridge_subtype_id` | 不进入 contract | 只用于人类标注、分歧分析和多桥案例统计。 |
| `registered_focus_id` | `selected_focus_id` | runtime 只能从 top-k focus candidates 中选择，或者输出 `unknown`。 |
| `focus_match_status` / `new_focus_candidate` | 不进入 contract | 用于维护 focus registry，不要求运行时 Judge 每轮生成新 focus。 |
| `help_seeking_type` | 可选压缩进 contract 或日志 | runtime 主要用它辅助 `max_scaffold_level` 和 `help_forms`。 |
| `max_scaffold_level` | `max_scaffold_level` | 只允许 `L0/L1/L2/L3`。 |
| `help_forms` | `help_forms` | runtime 最多输出 2 个。 |
| `general_forbidden_content` / `bridge_specific_forbidden_content` | `forbidden_content` | runtime 最多输出 3 条，优先放当前关键桥红线。 |
| `leakage_risk` | `leakage_risk` | 直接映射；决定是否触发 Leakage Judge。 |
| `evidence_type` / `evidence_quote` | 不进入 contract | 用于 expert reference 解释、双标分歧讨论和人工复核。 |
| `coach_note_tags` / `coach_free_notes` | 不进入 contract | 只用于教练协作。 |

## Runtime Contract Schema

运行时 schema 以 [runtime_bridge_contract_schema_v1.json](/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/research/runtime_bridge_contract_schema_v1.json) 为准。核心字段是：

```json
{
  "turn_type": "diagnosable_learning_turn",
  "diagnosis_uncertainty": "low",
  "algorithm_topic_l1": "binary_search",
  "algorithm_topic_l2": "binary_search_answer",
  "primary_bridge_family": "predicate_condition_bridge",
  "selected_focus_id": "check_condition",
  "selected_focus_confidence": 0.86,
  "max_scaffold_level": "L2",
  "help_forms": ["micro_example", "guiding_question"],
  "forbidden_content": ["不要直接给完整 check 条件。"],
  "leakage_risk": "high",
  "confidence": 0.86
}
```

## Top-k 候选原则

运行时不要把完整算法体系和完整 focus registry 一次性塞给 Judge。离线研究工具链先用轻量候选检索得到：

- `top_k_algorithm_topics`：最多 5 个粗算法域/子域候选；
- `top_k_registered_focus`：最多 5 个 focus 候选，始终包含 `unknown`。

Bridge Judge 只能从 top-k 候选里选 `selected_focus_id`，或者输出 `unknown`。如果候选都不贴合，后续由人类标注和 registry 维护流程决定是否新增 focus。

## 三种离线 Judge 对照

后续离线评测比较三种 Judge 方式：

- `full_schema_judge`：接近人类标注字段，主要用于观察标签过载问题。
- `compact_contract_judge`：只输出 compact bridge contract。
- `retrieval_augmented_compact_judge`：先检索 top-k topic/focus，再输出 compact bridge contract。

论文中应把它们作为消融变量，而不是默认假设“标签越细 Judge 越好”。

## 论文表述

建议论文中使用如下表述：

> The human annotation schema is intentionally richer than the runtime prediction schema. Human labels support detailed error analysis and dataset construction, while the runtime Bridge Judge predicts a compact bridge contract for low-latency tutor control.

中文表述：

> 人类教练标注 schema 故意比运行时 Judge schema 更细。前者用于专家参考标注、分歧裁决、误差分析和数据集建设；后者只输出紧凑 bridge contract，用于低延迟路由和主 tutor 控制。
