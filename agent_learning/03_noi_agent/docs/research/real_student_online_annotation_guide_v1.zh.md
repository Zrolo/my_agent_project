# Real-Student Online AIChat Annotation Guide v1

## 使用边界

本指南用于我们自己系统线上 AIChat / 教学场景中的真实学生 dialogue-state cases。它不使用洛谷讨论区、公开讨论区、第三方公开社区或第三方平台学生数据；不新增主实验 condition；不修改 dialogue-state v3 主实验；不重算主表；不上线 active mode；不改变学生可见回复；不把 pilot 写成 learning outcome study。

## 标注目标

标注只用于 ecological validity check：

1. 判断真实学生问题是否能映射到现有 cognitive bridge family。
2. 判断真实对话中的 surface anchor 是否能被现有口径描述。
3. 判断 case-specific rubric 是否能定义 forbidden content 与 expected next student action。
4. 判断当前 AIChat 回复是否可能泄露 critical bridge，但该判断不改变学生可见回复，不进入主实验结果。

## 数据源检查

标注前先确认数据来源：

- 必须来自我们自己系统线上 AIChat / 教学场景。
- 不得来自洛谷讨论区、题解区、评论区或公开社区。
- 不得来自第三方论坛、问答网站、社交媒体或公开讨论区。
- 不得通过抓取第三方平台获得学生问题。

若数据源不确定，标记为 `privacy_review_status=needs_redaction` 或排除，不进入 pilot annotation。

## 如何标注 Missing Bridge

missing bridge 是学生当前尚未完成、但下一步需要构造的局部推理关系。标注时先问：

1. 学生已经知道什么？
2. 学生当前卡在哪里？
3. 如果 tutor 直接说出哪一层关系，学生的核心推理机会会被替代？
4. 理想回复后，学生能做出的最小下一步是什么？

`coach_missing_bridge_instance` 应用自然语言写具体关系。例如：

```text
学生知道可能要二分，但还没有定义候选值 x 的含义和 check(x) 的真假方向。
```

不要把 missing bridge 写成完整题解，也不要只写算法名。

## 如何映射到 Cognitive Bridge Family

优先使用现有 family：

- `state_representation_bridge`
- `transition_recurrence_bridge`
- `predicate_check_bridge`
- `boundary_order_bridge`
- `modeling_bridge`
- `aggregation_contribution_bridge`
- `data_structure_bridge`
- `correctness_bridge`
- `implementation_bridge`
- `debugging_bridge`
- `policy_bridge`

填写 `matches_existing_taxonomy`：

| value | meaning |
| --- | --- |
| `yes` | 能清晰映射到现有 family |
| `uncertain` | 大致可映射，但边界、subtype 或 surface anchor 不够清楚 |
| `no` | 现有 family 难以覆盖，应记录为 candidate boundary |

如果选择 `no` 或 `uncertain`，在 `new_bridge_candidate` 中说明问题。该字段只用于 validity discussion，不立即修改主实验 taxonomy。

## 如何标注 Surface Anchor

`surface_anchor` 记录真实对话中的算法/实现表面场景，而不是 taxonomy 本体。例子包括：

- DP state；
- recurrence source；
- binary-search check；
- boundary update order；
- tree-difference marking；
- data-structure operation；
- invariant proof；
- local implementation boundary；
- debugging trace；
- direct-answer / code request。

如果 surface anchor 不清楚，不要猜测算法模板；应结合 `context_sufficiency` 标记为 `partial`、`insufficient` 或 `unclear`。

## 如何判断 Context Sufficiency

填写 `context_sufficiency`：

| value | meaning |
| --- | --- |
| `sufficient` | 脱敏后仍足以判断 missing bridge、forbidden content 和 expected next action |
| `partial` | 可判断大致 bridge，但缺少部分上下文 |
| `insufficient` | 不足以可靠标注 bridge，应优先要求澄清 |
| `unclear` | 标注者无法判断是否足够 |

Context insufficient 的 case 不应强行归入 main scaffold 类型；在 reporting 中计入 requiring clarification。

## 如何标注 Forbidden Content

`forbidden_content` 写本轮不应直接补完的内容。推荐写成抽象泄露形状：

- `no_exact_state_definition`
- `no_exact_recurrence`
- `no_exact_check_condition`
- `no_exact_boundary_update_rule`
- `no_exact_contribution_formula`
- `no_complete_local_condition`
- `no_full_solution`
- `no_direct_code`

如果当前 AIChat 回复直接提供了这些内容，可能构成 critical bridge leakage。

## 如何判断 Current AIChat 是否泄露 Critical Bridge

判断当前 AIChat 回复时，只比较三个对象：

1. 学生当前 message 与 recent dialogue 显示的已知状态；
2. `coach_missing_bridge_instance` 与 `forbidden_content`；
3. `ai_response_current_system_redacted` 中实际给出的信息。

如果 AIChat 回复直接补完学生尚未构造的关键关系，即使没有给完整代码，也应标记为 potential critical bridge leakage in annotation notes。该判断只用于 pilot ecological-validity reporting，不改变学生可见回复，不接入 active mode，不回写主实验结果。

边界：

- 当前学生已明确说出的内容，不应重复判为泄露。
- 必要的澄清、复述、低强度提示可视为 acceptable reveal。
- 上下文不足时，不应强判泄露，应标记 unclear / needs clarification。

## 如何记录 Observed Next-Turn Progress

若有下一轮学生回复，填写 `observed_next_turn_progress`：

| value | meaning |
| --- | --- |
| `progress_observed` | 学生完成或接近完成 expected next action |
| `partial_progress_observed` | 学生有部分推进 |
| `no_progress_observed` | 没有看到推进 |
| `unclear` | 无法判断 |
| `unavailable` | 没有下一轮 |

该字段只用于判断 rubric 是否贴近真实互动，不是长期学习效果指标，不应报告为 learning outcome。

## 如何处理 Unclear Cases

出现以下情况时标记 unclear 或 requiring clarification：

- 脱敏后题目摘要不足；
- recent dialogue 缺失；
- 学生消息过短或只说“不会”；
- 代码片段缺失但当前问题依赖代码；
- AIChat 回复与学生问题之间的上下文关系不清楚；
- 数据源、隐私或 consent 状态不清楚。

Unclear cases 可以用于讨论真实场景中的 context sufficiency challenge，但不能强行作为 taxonomy 支持证据。

## 质量控制

每个 case 至少检查：

- 是否来自我们自己系统；
- 是否已脱敏；
- 是否有 `student_id_hash` 和 `problem_id_hash`；
- 是否不含第三方公开社区内容；
- 是否能判断 context sufficiency；
- missing bridge 是否不是完整题解；
- surface anchor 是否不是过度算法清单；
- forbidden content 是否能定义 leakage boundary；
- observed progress 是否没有被写成学习效果。
