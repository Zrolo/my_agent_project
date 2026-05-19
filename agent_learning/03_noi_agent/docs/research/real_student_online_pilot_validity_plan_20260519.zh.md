# Real-Student Online AIChat Pilot Validity Plan v1

## 使用边界

本文档设计一个 real-student online AIChat pilot validity check，用于补充 CP-MissingBridgeBench 的生态效度。该 pilot 不修改 dialogue-state v3 主实验，不新增主实验 condition，不重算 dialogue-state v3 主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

## 数据源

本 pilot 只使用我们自己系统线上 AIChat / 教学场景中的学生真实问题。数据来源限定为我们自己系统内已经发生的、经隐私审查和脱敏处理的学生 dialogue-state cases。

本 pilot 明确不使用以下数据：

- 洛谷讨论区、题解区、评论区或任何洛谷公开社区内容；
- 任何第三方公开社区、论坛、问答网站、社交媒体或公开讨论区数据；
- 第三方平台上的学生对话、用户评论、公开求助帖；
- 需要抓取第三方页面才能获得的学生问题。

如果学生问题涉及公开题目背景，pilot 只保留我们自己系统中已经出现的必要题目摘要和匿名 `problem_id_hash`，不抓取或保存第三方讨论内容，不公开完整原文。

## Online Log Data Funnel

本 pilot 采用三层数据设计。它先报告线上 AIChat 日志漏斗，再从候选 turn 中选择小规模 pilot candidate set，用于后续 deep annotation。这样可以让读者看到真实数据来源和筛选规模，同时避免把轻量筛查池误写成深度标注样本。

| layer | unit | count | role | reporting boundary |
| --- | --- | ---: | --- | --- |
| Layer 1: Online log corpus summary | AIChat message rows / sessions / paired turns | 1156 message rows; 87 sessions; 578 paired user-assistant turns | 描述我们自己线上 AIChat 数据来源规模 | 只作数据漏斗背景，不作 main result |
| Layer 2: Substantial candidate-turn screening | candidate turns / candidate sessions | 137 substantial candidate turns; 59 candidate sessions | 轻量筛查 context sufficiency、rough bridge family、surface anchor、help-seeking type 和是否适合 deep annotation | 不做完整 case-specific rubric 深标，不写成深度标注样本 |
| Layer 3: Deep pilot candidate selection | selected dialogue-state candidate cases | 30 selected pilot candidate cases; 11 hashed students; 15 hashed problems | 被选入后续完整 case-specific rubric 标注的候选集，包括 missing bridge、forbidden content、expected next student action 和 taxonomy fit | consent/reporting gate 完成前只能作为候选集与数据漏斗说明；不作为 main result |

Layer 2 的 137 条是 candidate-turn screening pool，用于了解真实线上问题中哪些 turn 可能适合进入 deep annotation。它们不进行完整 rubric 深标，不参与 dialogue-state v3 主表，也不与 7 个 offline conditions 比较。

Layer 3 的 30 条是 selected pilot candidate cases。它不是全部线上数据，而是从 candidate-turn screening pool 中按覆盖性和可标注性选择的 purposive sample。进入正式报告前，每条 deep case 必须通过 privacy review 和 consent/status 检查；在 consent/reporting gate 完成前，这 30 条只能写成 selected candidate cases pending consent/reporting gate，不能写成可公开报告的 deep-pilot evidence。

## 目标

目标规模为 20-30 个 deep real-student dialogue-state cases，本次数据漏斗对应 30 个 selected pilot candidate cases。该 pilot 用于检查：

1. CP-MissingBridgeBench 的 cognitive bridge family 是否能覆盖真实学生问题中的 missing bridge。
2. 现有 surface anchor 口径是否能描述真实学生对话中的算法/实现表面场景。
3. case-specific rubric 是否能定义真实学生当前轮次的 forbidden content、expected next student action 和 context sufficiency。
4. 当前 AIChat 学生可见回复是否可能泄露 critical bridge，但该判断只用于生态效度讨论，不改变任何线上回复。

## 非目标

本 pilot 不做以下事情：

- 不作为 main result。
- 不比较 dialogue-state v3 的 7 个 conditions。
- 不新增 baseline。
- 不评估长期学习效果。
- 不修改现有 dialogue-state v3 evidence package。
- 不重算 dialogue-state v3 主表。
- 不改变学生可见回复。
- 不上线 Bridge Judge、Leakage Judge、Repair 或 active mode。

## 样本单位

基本单位是一个 real-student dialogue-state case，而不是完整学生轨迹、完整课程、长期学习记录或主实验 response-level 条件比较。

每个 case 至少包含：

- 匿名学生 ID；
- 匿名题目 ID；
- 粗粒度时间桶；
- 已脱敏学生当前消息；
- 已脱敏近期对话；
- 必要的题目上下文摘要；
- 可选的已脱敏代码片段；
- 当前系统 AIChat 回复的脱敏版本；
- 教练对 missing bridge、surface anchor、forbidden content 和 expected next student action 的标注。

## 纳入标准

一个 case 可以纳入 pilot，当且仅当：

1. 来自我们自己系统线上 AIChat / 教学场景。
2. 学生正在解决 competitive-programming / algorithmic-programming 问题。
3. 当前学生消息能够形成一个 dialogue-state：即可以判断学生当前卡点、求助意图或直接要答案/代码风险。
4. 脱敏后仍能判断 problem context、recent dialogue、current AIChat response 和 student state。
5. 已通过 privacy review，并且 consent status 满足 pilot 使用要求。

## 排除标准

以下材料不进入 pilot：

1. 来自洛谷讨论区、公开讨论区、第三方社区、社交媒体或第三方问答平台的数据。
2. 含真实姓名、学校、手机号、邮箱、账号等直接身份信息且无法可靠脱敏的记录。
3. 脱敏后无法判断当前学生问题或上下文的片段。
4. 仅包含长期学习轨迹、分数或课程评价，但缺少具体 dialogue-state 的材料。
5. 需要接入 active mode、改变 final response 或修改线上系统才能获得的样本。

## 字段与 Schema

数据使用 `real_student_online_case_schema_v1.json`。核心字段包括：

| field | role |
| --- | --- |
| `pilot_case_id` | pilot 内部匿名 case 编号 |
| `student_id_hash` | 学生匿名 hash |
| `problem_id_hash` | 题目匿名 hash |
| `timestamp_bucket` | 粗粒度时间桶，不保存精确时间 |
| `problem_context_summary` | 题目上下文摘要 |
| `student_message_redacted` | 已脱敏学生当前问题 |
| `recent_dialogue_redacted` | 已脱敏近期对话 |
| `student_code_excerpt_redacted` | 已脱敏代码片段，可为空 |
| `ai_response_current_system_redacted` | 当前系统学生可见回复的脱敏版本 |
| `coach_missing_bridge_family` | 教练标注的 cognitive bridge family |
| `coach_missing_bridge_instance` | 当前 case 的具体 missing bridge |
| `surface_anchor` | 真实对话中的算法/实现表面场景 |
| `context_sufficiency` | 上下文是否足以标注 bridge/rubric |
| `expected_next_student_action` | 理想脚手架后学生应完成的下一步 |
| `forbidden_content` | 本轮不应直接补完的内容 |
| `matches_existing_taxonomy` | 是否能映射到现有 taxonomy |
| `new_bridge_candidate` | 若不能映射，记录候选边界问题 |
| `observed_next_turn_progress` | 下一轮是否有可观察推进；不是学习效果指标 |
| `privacy_review_status` | 隐私审查状态 |
| `consent_status` | 学生/家长/教练知情同意或退出状态 |

## 标注与分析

pilot 分两级标注。Layer 2 candidate-turn screening 使用 `real_student_online_candidate_screening_schema_v1.json`，只做轻量筛查；Layer 3 deep pilot case annotation 使用 `real_student_online_case_schema_v1.json`，才做完整 case-specific rubric 标注。

pilot 只回答 ecological validity questions：

1. 真实学生问题是否能映射到现有 cognitive bridge family。
2. surface anchor 是否足以描述真实学生问题中的算法/实现场景。
3. case-specific rubric 是否能定义 forbidden content 与 expected next student action。
4. 哪些 cases 需要 clarification，而不是强行标注 bridge。
5. 哪些 cases 可能提示 new bridge candidate，但不立即修改主实验 taxonomy。
6. 当前 AIChat 回复是否可能泄露 critical bridge；该判断只用于 appendix / discussion，不改变线上回复。

## 报告用途

pilot 可作为 Discussion / Appendix 中的 ecological validity evidence。推荐边界句：

```text
The real-student online pilot is used only to examine whether CP-MissingBridgeBench taxonomy and rubric fields transfer to privacy-reviewed AIChat dialogue-state cases from our own system. It is not a main result, does not compare the seven offline conditions, does not evaluate long-term learning outcomes, and does not change student-visible responses.
```

## 禁止写法

- 不能说 pilot 是 dialogue-state v3 main result。
- 不能把 pilot 写成 learning outcome study。
- 不能把 pilot cases 合并进 dialogue-state v3 主表。
- 不能根据 pilot 新增主实验 condition 或 baseline。
- 不能把 137 条 candidate turns 写成 deep annotation sample。
- 不能把 30 条 selected cases 写成全部线上数据。
- 不能说 active mode 已上线。
- 不能说 Bridge Judge / Leakage Judge / Repair 已改变学生可见回复。
- 不能使用洛谷讨论区、公开社区或第三方平台数据。

## 与 Shadow Mode 的关系

如果后续与 shadow mode pilot 联合报告，必须明确：

- shadow mode 只后台记录 judge signals；
- `final_response` 不改变；
- judge / repair 不进入学生可见回复；
- shadow logs 不形成 dialogue-state v3 主实验 condition；
- 只有 shadow 风险评估通过后，才可讨论未来 risk-triggered active mode。
