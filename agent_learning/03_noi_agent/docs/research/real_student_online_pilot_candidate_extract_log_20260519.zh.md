# Real-Student Online AIChat Pilot Candidate Extract Log 20260519

## 使用边界

本记录说明 2026-05-19 从我们自己线上 AIChat / 教学系统中只读抽取 real-student online pilot 候选对话的过程。该抽取不使用洛谷讨论区、公开论坛、问答网站、社交媒体或任何第三方公开社区数据；不修改 dialogue-state v3 主实验；不新增主实验 condition；不新增 baseline；不重算主表；不改变 evidence class；不上线 active mode；不改变学生可见回复；不评估长期学习效果。

本次抽取只生成 pilot 候选材料，用于后续 privacy review、coach annotation 和 taxonomy / rubric ecological validity check。它不是 main result，也不能合并进 dialogue-state v3 主表。

## 数据源

数据源为我们自己线上系统数据库中的 `aichat_messages` 表。抽取内容仅来自线上 AIChat 中已经发生的学生消息、近期对话和当前系统 AI 回复。

本次未采集：

- 洛谷讨论区、题解区、评论区或任何公开社区内容；
- 第三方平台学生对话、公开求助帖、论坛或社交媒体数据；
- 需要抓取第三方页面才能获得的学生问题；
- 真实姓名、学校、手机号、邮箱、账号或精确时间戳。

## 只读抽取摘要

| item | value |
| --- | ---: |
| source table | `aichat_messages` |
| raw AIChat message rows observed | 1156 |
| total sessions observed | 87 |
| paired user-assistant turns observed | 578 |
| substantial candidate turns after keyword / code-context filtering | 137 |
| sessions with candidate turns | 59 |
| selected pilot candidate cases | 30 |
| unique hashed students in selected cases | 11 |
| unique hashed problems in selected cases | 15 |

## 抽取策略

候选 case 的基本单位是一个 real-student dialogue-state turn：一个学生消息、其最近上下文和紧随其后的当前系统 AIChat 回复。

筛选策略：

1. 只从我们自己线上 AIChat 表读取消息。
2. 要求学生消息存在紧随其后的 assistant 回复。
3. 优先包含求助、错误、代码、思路、样例、二分、DP、check、调试等真实学习信号的 turn。
4. 每个 session 最多选择一个较有信息量的 turn，以增加学生和题目多样性。
5. 按近期优先选择 30 个候选 cases。

该策略只用于 pilot candidate extraction，不构成抽样代表性声明。

## 脱敏与字段处理

本次输出已进行规则脱敏：

- `student_id` 写为 `student_id_hash`；
- `problem_id` / problem title 组合写为 `problem_id_hash`；
- 精确时间写为粗粒度 `timestamp_bucket`；
- URL 写为 `[URL]`；
- 邮箱写为 `[EMAIL]`；
- 手机号写为 `[PHONE]`；
- 8 位以上长数字写为 `[LONG_NUMBER]`；
- 文件路径写为 `[PATH]`；
- 明显身份字段写为 `[REDACTED]`。

`coach_missing_bridge_family`、`coach_missing_bridge_instance`、`surface_anchor`、`expected_next_student_action`、`forbidden_content` 等字段当前为待教练标注状态。所有候选的 `privacy_review_status` 均为 `pending`，`consent_status` 均为 `pending`，不能直接进入论文报告。

## 输出文件

| file | role |
| --- | --- |
| `real_student_online_pilot_candidate_cases_20260519.jsonl` | schema-compatible redacted candidate cases |
| `real_student_online_pilot_candidate_cases_20260519.csv` | spreadsheet-friendly collection / annotation table |

## 本地校验结果

| check | result |
| --- | --- |
| JSONL record count | 30 |
| CSV row count | 30 |
| JSONL required fields present | passed |
| enum values compatible with `real_student_online_case_schema_v1.json` | passed |
| CSV columns match schema properties | passed |
| residual `http(s)://` URL scan | 0 |
| residual email scan | 0 |
| residual CN phone scan | 0 |
| residual 8+ digit number scan | 0 |

## 解释边界

这些候选 cases 可以支持后续 5-case dry run 和 20-30 case pilot annotation，但只能作为 ecological validity material。它们目前不能支持以下写法：

- 不能作为 dialogue-state v3 main result；
- 不能与 7 个 offline conditions 比较；
- 不能用于重算 dialogue-state v3 主表；
- 不能作为长期学习效果证据；
- 不能说明 active mode 已上线；
- 不能说明 Bridge Judge、Leakage Judge 或 Repair 改变了学生可见回复；
- 不能在未经人工隐私审查和改写前公开完整原文。

推荐论文边界句：

```text
The real-student online pilot candidates were extracted from privacy-redacted AIChat dialogue-state turns in our own teaching system. They are used only for ecological-validity checking of taxonomy and rubric transfer, not as main results, not as a seven-condition comparison, and not as learning-outcome evidence.
```
