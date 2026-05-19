# Real-Student Online Privacy And Consent Checklist v1

## 使用边界

本清单用于我们自己系统线上 AIChat / 教学场景中的 real-student online pilot。它不使用第三方公开社区数据，不修改线上 AIChat，不上线 active mode，不改变学生可见回复，不新增主实验数据，不重算 dialogue-state v3 主表，不把 pilot 写成 learning outcome study。

## 1. 数据源检查

| checklist item | status | note |
| --- | --- | --- |
| data comes from our own online AIChat / teaching system | pending / passed / failed |  |
| no Luogu discussion / solution / comment data used | pending / passed / failed |  |
| no public forum / Q&A / social media data used | pending / passed / failed |  |
| no third-party platform student dialogue used | pending / passed / failed |  |
| no web scraping needed for student questions | pending / passed / failed |  |

## 2. 不记录直接身份信息

进入 pilot 的数据不得包含：

- 真实姓名；
- 学校、班级、教师姓名；
- 手机号；
- 邮箱；
- 平台账号、登录名、社交账号；
- 头像、住址、定位；
- 代码路径中的本机用户名；
- 注释、截图或文件名中的身份线索。

## 3. Hash 与匿名编号

必须使用：

- `student_id_hash`
- `problem_id_hash`
- `pilot_case_id`

要求：

- 不在研究目录保存真实 ID 到 hash 的映射表；
- 不公开 hash 生成 salt；
- 不在论文、附录或公开材料中提供可逆身份线索；
- `timestamp_bucket` 使用粗粒度时间桶，不保存精确时间戳。

## 4. 文本脱敏

需要脱敏的字段：

- `student_message_redacted`
- `recent_dialogue_redacted`
- `ai_response_current_system_redacted`
- `problem_context_summary`

文本脱敏要求：

- 删除姓名、学校、手机号、邮箱、账号；
- 删除与题目和 bridge 判断无关的私人信息；
- 保留学生求助意图、卡点、上下文依赖；
- 不公开完整原文；
- 论文示例只能使用 paraphrased / anonymized examples。

## 5. 代码片段脱敏

`student_code_excerpt_redacted` 只保留判断 bridge 所需的最小片段。

必须删除：

- 文件路径；
- 本机用户名；
- 账号、token、URL；
- 姓名、学校、课程注释；
- 与当前 bridge 无关的大段代码。

若代码片段不是判断 bridge 所必需，保留为空并标记 not applicable。

## 6. 知情同意

pilot 前应提供学生 / 家长 / 教练知情说明。说明应包括：

1. 数据仅用于教学改进和研究分析。
2. 数据来自我们自己系统中的 AIChat / 教学场景，不使用公开社区或第三方平台学生数据。
3. 数据会脱敏，不记录真实姓名、学校、手机号、邮箱或账号。
4. pilot 不改变学生可见回复。
5. pilot 不影响成绩、课程评价或教师评价。
6. pilot 不评估长期学习效果。
7. 学生 / 家长 / 教练可以退出。

建议文本：

```text
我们可能使用脱敏后的编程学习对话片段进行教学改进和研究分析。数据只来自我们自己系统中的 AIChat / 教学场景，不使用公开讨论区或第三方平台学生数据。记录不会包含真实姓名、学校、手机号、邮箱或账号信息；论文中如需示例，只使用改写后的匿名示例。该 pilot 不会改变你看到的回复，不会影响成绩或课程评价，也不评估长期学习效果。你可以选择不参与或之后退出。
```

## 7. 可退出机制

必须支持：

- 学生或家长拒绝参与；
- 学生或家长后续撤回；
- 教练要求删除某个 case；
- 退出后该 case 不进入 pilot 分析；
- 已用于内部草稿的 case 应标记 removal status。

记录字段建议：

| field | allowed values |
| --- | --- |
| `consent_status` | `pending` / `notice_provided` / `consented` / `declined` / `withdrawn` |
| `withdrawal_requested_at` | ISO date string or empty |
| `withdrawal_action_status` | `not_applicable` / `pending_removal` / `removed` |

## 8. 数据保存与访问权限

建议要求：

- 原始可识别数据不进入论文仓库；
- 脱敏 pilot cases 与研究稿件分开保存；
- 访问权限限定在授权研究/教学改进人员；
- 导出给论文写作的只应是匿名统计、改写示例和 schema-compatible case fields；
- 不公开完整学生原文或完整代码；
- 不公开可逆 hash 映射表。

## 9. Privacy Review Status

每个 case 必须填写 `privacy_review_status`：

| status | meaning |
| --- | --- |
| `pending` | 尚未完成隐私检查 |
| `passed` | 可进入 pilot annotation/reporting |
| `needs_redaction` | 需要继续脱敏 |
| `excluded_privacy_risk` | 因隐私风险排除 |

只有 `passed` 且 consent 状态允许的 cases 可以进入 reporting。

## 10. 提交前检查

| checklist item | status | note |
| --- | --- | --- |
| source limited to our own online AIChat / teaching system | pending / passed / failed |  |
| no third-party public community data | pending / passed / failed |  |
| no real names retained | pending / passed / failed |  |
| no school names retained | pending / passed / failed |  |
| no phone numbers retained | pending / passed / failed |  |
| no email/account identifiers retained | pending / passed / failed |  |
| `student_id_hash` present | pending / passed / failed |  |
| `problem_id_hash` present | pending / passed / failed |  |
| dialogue text redacted | pending / passed / failed |  |
| code excerpt redacted | pending / passed / failed |  |
| no full original text published | pending / passed / failed |  |
| examples paraphrased/anonymized | pending / passed / failed |  |
| consent / notice completed | pending / passed / failed |  |
| withdrawal mechanism documented | pending / passed / failed |  |
| student-visible response unchanged | pending / passed / failed |  |

## 11. 固定边界句

对外报告时应保留：

```text
This real-student online pilot uses privacy-reviewed and redacted dialogue-state cases from our own AIChat / teaching system only. It does not use public community or third-party platform data, does not change student-visible responses, does not add main-experiment data, and does not evaluate long-term learning outcomes.
```
