# Real-Student Pilot Annotation Guide v1

## 使用边界

本指南用于 20-30 个真实学生 dialogue-state cases 的 pilot validity check。它不用于修改 dialogue-state v3 主实验，不新增主实验 condition，不重算主表，不修改线上 AIChat，也不评估长期学习效果。

标注目标只有一个：检查现有 CP-MissingBridgeBench bridge-family taxonomy 与 case-specific rubric 是否能用于真实学生对话。

## 标注前隐私检查

标注前必须先完成隐私审查。以下信息不得进入 pilot case：

- 真实姓名；
- 学校、班级、教师姓名；
- 手机号、邮箱、社交账号、平台账号；
- 住址、定位、身份证明；
- 代码路径、文件系统用户名、注释中的身份线索。

`privacy_review_status` 未标记为 `passed` 的 case 不进入正式标注。需要继续脱敏的 case 标记为 `needs_redaction`；无法安全脱敏的 case 标记为 `excluded_privacy_risk`。

## 标注单位

标注单位是一个真实学生的当前 dialogue-state case，而不是完整课程、完整学生轨迹或长期学习效果。

一个 case 包括：

1. 题目上下文摘要；
2. 当前学生消息；
3. 已脱敏近期对话；
4. 可选的已脱敏代码片段；
5. 教练对当前 missing bridge 与下一步学生动作的判断。

## 字段填写规范

### `student_id_hash`

填写匿名 hash 或稳定匿名编号。不得填写真实姓名、昵称、学校、手机号或平台账号。

### `problem_id_hash`

填写题目或作业的匿名 hash。若题目来自公开平台，也建议在 pilot schema 中只保留匿名 hash，并在 `problem_context_summary` 中保留必要摘要。

### `problem_context_summary`

填写判断当前 missing bridge 所需的题目摘要。不要粘贴不必要的完整题面。摘要应足以让第二位教练理解学生卡点。

### `student_message`

填写当前学生消息的脱敏版本。尽量保留学生原始表达的含混程度、口语化和求助意图，因为这会影响 bridge 判断。

### `recent_dialogue_redacted`

填写必要的近期对话，尤其是上一轮 tutor / coach 已经提示过什么。若没有近期对话，填空字符串并在标注备注中说明上下文不足。

### `student_code_excerpt_redacted`

只保留判断 bridge 所需的最小代码片段。删除文件路径、账号、姓名、注释身份线索和与当前 bridge 无关的大段代码。

### `coach_missing_bridge_family`

优先使用现有 taxonomy 中的 bridge family，例如：

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

如果无法归入现有 family，不要立刻新增正式 taxonomy；先填写最接近的 family，并在 reporting template 中列入 “taxonomy-fit concern”。

### `coach_missing_bridge_instance`

用自然语言描述本 case 的具体 missing bridge。例如：

```text
学生知道可能要二分，但还没有定义候选 x 的含义和 check(x) 的真假方向。
```

不要把它写成完整题解，也不要写成算法标签清单。

### `coach_forbidden_content`

列出本轮 tutor 不应直接补完的内容。推荐写成抽象泄露形状，例如：

- `no_exact_state_definition`
- `no_exact_recurrence`
- `no_exact_check_condition`
- `no_exact_boundary_update_rule`
- `no_exact_contribution_formula`
- `no_complete_local_condition`
- `no_full_solution`
- `no_direct_code`

### `expected_next_student_action`

写学生在理想 scaffold 之后应该完成的最小下一步。它应短、具体、可观察。例如：

```text
学生用一句话说明 check(x)=true 表示候选 x 是否满足限制，并判断真假方向。
```

### `observed_next_turn_progress`

如果有下一轮学生回复，选择：

- `progress_observed`
- `partial_progress_observed`
- `no_progress_observed`
- `unclear`

如果没有下一轮，填写 `unavailable`。该字段只用于检查 rubric 贴近真实互动，不得写成学习效果指标。

### `privacy_review_status`

只允许：

- `pending`
- `passed`
- `needs_redaction`
- `excluded_privacy_risk`

## 标注判断顺序

1. 先确认隐私是否通过。
2. 再判断当前学生消息是否形成一个可标注 dialogue-state case。
3. 选择最接近的 `coach_missing_bridge_family`。
4. 写出具体 `coach_missing_bridge_instance`。
5. 写出本轮不能直接补完的 `coach_forbidden_content`。
6. 写出最低足够的 `expected_next_student_action`。
7. 若有下一轮，记录 `observed_next_turn_progress`。
8. 标记 taxonomy 或 rubric 不适用的原因，供 reporting template 汇总。

## 质量控制

每个 case 至少检查：

- 是否含未脱敏个人信息；
- bridge family 是否过度算法模板化；
- missing bridge instance 是否写成完整解法；
- forbidden content 是否能真正定义 leakage boundary；
- expected next student action 是否可观察；
- observed next turn progress 是否被误写成学习效果。

## 禁止事项

- 不把 pilot 结果合并进 dialogue-state v3 主表。
- 不新增主实验 condition 或 baseline。
- 不把 pilot 写成长期学习效果实验。
- 不修改线上 AIChat、active mode 或 prompt。
- 不根据 pilot 结果直接改主实验数字、slice 或 evidence class。
