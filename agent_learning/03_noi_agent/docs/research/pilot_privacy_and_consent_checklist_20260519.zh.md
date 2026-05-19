# Pilot Privacy And Consent Checklist v1

## 使用边界

本清单用于 real-student pilot validity check 与 shadow mode pilot 的隐私、脱敏和知情说明。它不修改线上 AIChat，不上线 Bridge Judge / Leakage Judge / Repair，不改变学生可见回复，不新增主实验数据，不重算 dialogue-state v3 主表，也不把 pilot 写成 learning outcome study。

## 1. 不收集直接身份信息

进入 pilot 的数据不得包含：

- 真实姓名；
- 学校、班级、教师姓名；
- 手机号、邮箱、社交账号；
- 平台账号、登录名、头像；
- 住址、定位、身份证明；
- 代码路径中的本机用户名；
- 注释、文件名或截图中的身份线索。

检查结果：

| item | status | note |
| --- | --- | --- |
| real name removed | pending / passed / needs_redaction |  |
| school removed | pending / passed / needs_redaction |  |
| phone number removed | pending / passed / needs_redaction |  |
| account id removed | pending / passed / needs_redaction |  |
| local path removed | pending / passed / needs_redaction |  |

## 2. Hash 字段

每个 case 只保留匿名编号：

- `student_id_hash`
- `problem_id_hash`
- `pilot_case_id`

要求：

- hash 或匿名编号应稳定，便于同一 pilot 内去重；
- 不保留 hash salt、原始 ID 或映射表在研究稿件目录中；
- 不在论文、附录或公开材料中暴露可逆映射。

## 3. 对话脱敏

`recent_dialogue_redacted` 与 `student_message` 必须完成脱敏：

- 删除姓名、学校、联系方式；
- 删除与题目无关的私人信息；
- 保留学生求助意图、卡点和上下文依赖；
- 如果脱敏后无法判断 missing bridge，则标记为 insufficient context，而不是补造信息。

## 4. Code Excerpt 脱敏

`student_code_excerpt_redacted` 只保留判断 bridge 所需的最小代码片段。

必须删除：

- 文件路径；
- 本机用户名；
- 账号、token、URL；
- 真实姓名或学校注释；
- 与当前 missing bridge 无关的大段代码。

如果代码片段不是判断 bridge 所必需，应留空并说明 not applicable。

## 5. 学生 / 家长 / 教练知情说明

pilot 前应提供简短知情说明。说明应覆盖：

1. 数据仅用于教学改进和研究。
2. 数据会被脱敏，不记录真实姓名、学校、手机号等直接身份信息。
3. pilot 不改变学生可见回复。
4. shadow mode 只在后台记录 judge signals，不进行实时拦截或改写。
5. pilot 不评估学生长期学习效果，不影响成绩或课程评价。
6. 学生 / 家长 / 教练可询问数据使用方式。
7. 参与者可以退出 pilot。

建议知情说明文本：

```text
我们可能使用脱敏后的编程学习对话片段来改进教学反馈研究。记录不会包含真实姓名、学校、手机号或账号信息。该 pilot 不会改变你看到的回复，也不会影响成绩或课程评价；后台分析只用于判断研究中的 bridge-family taxonomy 和 rubric 是否适用于真实学生问题。你可以选择不参与或之后退出。
```

## 6. 可退出机制

必须提供退出机制：

- 学生或家长可以要求不纳入 pilot；
- 教练可以要求删除某个 case；
- 退出后不再使用该 case 进入分析；
- 已公开或已提交材料中的撤回处理应遵循机构和投稿规范。

记录字段建议：

| field | allowed values |
| --- | --- |
| `consent_status` | `pending` / `consented` / `declined` / `withdrawn` |
| `withdrawal_requested_at` | ISO date string or empty |
| `withdrawal_action_status` | `not_applicable` / `pending_removal` / `removed` |

## 7. Privacy Review Status

每个 case 必须有 `privacy_review_status`：

| status | meaning |
| --- | --- |
| `pending` | 尚未完成隐私检查 |
| `passed` | 可进入 pilot 标注 |
| `needs_redaction` | 需要继续脱敏 |
| `excluded_privacy_risk` | 因隐私风险排除 |

只有 `passed` cases 可以进入 annotation 或 reporting。

## 8. 数据使用边界

允许用途：

- 教学改进；
- bridge-family taxonomy 生态效度检查；
- case-specific rubric 适用性检查；
- shadow judge latency / disagreement 风险评估；
- EAIT / 教育技术论文 appendix 中的生态效度补充。

禁止用途：

- 修改 dialogue-state v3 主实验数字；
- 新增主实验 condition 或 baseline；
- 接入线上 active mode；
- 改变学生可见回复；
- 评估长期学习效果；
- 公开可识别学生或学校的信息。

## 9. 提交前检查

| checklist item | status | note |
| --- | --- | --- |
| no real names retained | pending / passed / failed |  |
| no school names retained | pending / passed / failed |  |
| no phone numbers retained | pending / passed / failed |  |
| student_id_hash present | pending / passed / failed |  |
| problem_id_hash present | pending / passed / failed |  |
| dialogue redacted | pending / passed / failed |  |
| code excerpt redacted | pending / passed / failed |  |
| consent / notice completed | pending / passed / failed |  |
| withdrawal mechanism documented | pending / passed / failed |  |
| student-visible response unchanged | pending / passed / failed |  |

## 10. 固定边界句

对外报告时应保留：

```text
This pilot uses privacy-reviewed and redacted real-student dialogue-state cases only to examine ecological validity of the benchmark construct. It does not change student-visible responses, does not deploy active-mode judges or repair, does not add main-experiment data, and does not evaluate long-term learning outcomes.
```
