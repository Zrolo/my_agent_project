# Real-Student Pilot Validity Check Plan v1

## 使用边界

本文档只新增一个真实学生 dialogue-state pilot validity check 的设计方案，用于补充 EAIT / 教育技术期刊可能关心的真实教育场景效度。该 pilot 不修改 dialogue-state v3 主实验，不新增主实验 condition，不重算主表，不修改线上 AIChat、active mode、prompt 或主实验数据，也不改变学生可见回复。

该 pilot 的目标不是评估长期学习效果，也不是比较 baseline 或验证产品胜利。它只检查 CP-MissingBridgeBench 的 bridge-family taxonomy 与 case-specific rubric 是否能迁移到真实学生对话中的 20-30 个 dialogue-state cases。

## 研究目的

真实学生对话可能比离线构造样本更短、更含混、更依赖上下文，也可能包含不完整代码、口语化表述、错误前提或直接要答案的请求。pilot validity check 关注两个问题：

1. 现有 bridge-family taxonomy 是否能覆盖真实学生卡住的位置。
2. 现有 case-specific rubric 字段是否足以定义真实学生当前轮次的 missing bridge、forbidden content 和 expected next student action。

如果 pilot 发现 taxonomy 或 rubric 不适用，结果只作为 validity discussion / future revision evidence，不回写现有 dialogue-state v3 evidence package，不改变主实验数字。

## 样本规模与单位

- 目标规模：20-30 个真实学生 dialogue-state cases。
- 基本单位：case-level tutoring situation，而不是 response-level 多条件比较。
- 每个 case 至少包含一个学生当前问题、必要的已脱敏近期对话、必要的题目摘要，以及可选的已脱敏代码片段。
- pilot 不生成新的主实验 responses，不新增主实验 harness，不新增 baseline，不改变线上回复。

## 纳入标准

一个真实学生 dialogue-state case 可以纳入 pilot，当且仅当：

1. 学生正在解决 competitive-programming / algorithmic-programming 问题。
2. 当前学生消息能反映一个局部卡点、求助意图或直接要答案/代码风险。
3. 经过脱敏后仍能判断 problem context、recent dialogue 和 student state。
4. 教练能够尝试标注 missing bridge family 与 expected next student action。

## 排除标准

以下材料不进入 pilot：

1. 含真实姓名、学校、手机号、社交账号、住址或其他直接身份信息且无法可靠脱敏的记录。
2. 仅包含最终成绩、考试分数或长期学习轨迹、但缺少具体 dialogue-state 的材料。
3. 无法判断题目背景或学生当前问题的片段。
4. 需要修改线上 AIChat、prompt、active mode 或主实验流程才能获得的样本。

## 数据字段

每个 pilot case 使用 `real_student_pilot_case_schema_v1.json` 中的字段：

| field | role |
| --- | --- |
| `pilot_case_id` | pilot 内部匿名 case 编号 |
| `student_id_hash` | 学生匿名 hash，不保留真实身份 |
| `problem_id_hash` | 题目或作业匿名 hash |
| `problem_context_summary` | 题目上下文摘要，不转载不必要完整题面 |
| `student_message` | 当前学生求助消息，脱敏后保留原意 |
| `recent_dialogue_redacted` | 已脱敏近期对话 |
| `student_code_excerpt_redacted` | 已脱敏代码片段，可为空 |
| `coach_missing_bridge_family` | 教练选择的 bridge family |
| `coach_missing_bridge_instance` | 当前 case 的具体 missing bridge |
| `coach_forbidden_content` | 本轮不应直接补完的内容 |
| `expected_next_student_action` | 理想回复后学生应完成的下一步 |
| `observed_next_turn_progress` | 如果有下一轮，记录学生是否推进；没有则标记 unavailable |
| `privacy_review_status` | 隐私审查状态 |

## 标注流程

1. 数据整理者先完成脱敏，不保留真实姓名、学校、手机号、社交账号、住址等直接身份信息。
2. 隐私审查者检查 `privacy_review_status`，未通过的 case 不进入标注。
3. 教练标注 `coach_missing_bridge_family` 与 `coach_missing_bridge_instance`。
4. 教练补充 `coach_forbidden_content`、`expected_next_student_action`。
5. 如果存在下一轮学生回复，记录 `observed_next_turn_progress`；该字段只用于观察 rubric 是否贴近真实互动，不评估长期学习效果。
6. 汇总时只报告适用性、覆盖性和不适用原因，不生成新的主实验条件比较。

## 分析问题

pilot reporting 只回答以下 validity questions：

1. 20-30 个真实学生 cases 中，有多少能被现有 bridge-family taxonomy 合理覆盖。
2. 哪些 cases 需要新的 bridge-family、subtype note 或更清晰的 surface anchor，但不应立即改动主实验 taxonomy。
3. case-specific rubric 字段是否足以区分 forbidden content、acceptable reveal 和 expected next student action。
4. 真实对话中最常见的不确定性来自哪里：上下文不足、学生表述含混、代码片段缺失、题目摘要不足、或直接要答案/代码风险。
5. `observed_next_turn_progress` 是否能帮助判断 rubric 的生态效度，但不作为学习效果指标。

## 报告边界

pilot 报告必须使用以下边界语言：

- This pilot is a validity check, not a main experiment.
- The pilot does not evaluate long-term learning outcomes.
- The pilot does not introduce new baselines or conditions.
- The pilot does not modify dialogue-state v3 main results.
- The pilot does not change student-visible responses.
- The pilot checks whether the taxonomy and rubric remain usable in real student dialogue-state cases.

禁止写法：

- 不能说 pilot 证明 CP-MissingBridgeBench 覆盖所有真实 CP tutoring。
- 不能把 20-30 个真实 cases 写成学习效果实验。
- 不能把 pilot 写成线上 AIChat 部署验证。
- 不能把 pilot 结果合并进 dialogue-state v3 主表。
- 不能根据 pilot 重排现有 condition 或修改主实验数字。
- 不能改变学生可见回复或把 shadow / judge 结果用于实时干预。

## 隐私与数据治理

- 不记录真实姓名、学校、手机号、社交账号、住址或其他直接身份信息。
- 学生、题目和来源只使用 hash 或内部匿名编号。
- 题目上下文只保留摘要和必要的局部信息，不转载不必要完整题面。
- 代码片段只保留判断 bridge 所需的最小片段，并删除姓名、路径、账号、注释中的身份线索。
- 所有 case 在标注前必须通过 `privacy_review_status`。

## 预期输出

pilot 完成后可生成一个独立 validity appendix / supplement，建议包含：

1. case collection summary。
2. taxonomy fit summary。
3. rubric fit summary。
4. privacy and exclusion summary。
5. limitations and non-main-result statement。

该输出只能作为 EAIT / 教育技术期刊的生态效度补充，不替代 dialogue-state v3 主实验结果。
