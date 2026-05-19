# Real-Student Online 5-Case 教练复核表 v2 中文填写说明

## 用途

本表用于 5 个 real-student online dry-run cases 的教练复核。它只检查真实学生对话中，CP-MissingBridgeBench 的 cognitive bridge family、surface anchor 和 case-specific rubric 是否容易迁移使用。

本表不修改 dialogue-state v3 主实验，不新增主实验 condition，不重算主表，不改变线上 AIChat 回复，不作为 learning outcome study，也不把 pending-consent cases 写成公开 deep-pilot evidence。

## 推荐填写入口

教练优先使用 `.xlsx` 工作簿，而不是直接填写 CSV：

- 公开空模板：`docs/research/real_student_online_5case_coach_review_form_cn_v2.xlsx`
- 本地私有真实案例表：`.local_private/real_student_online_5case_coach_review_packet_cn_v2_20260520.xlsx`

`.xlsx` 工作簿提供下拉选择、颜色提示、冻结表头和 50-case 字段对照。CSV 主要用于脚本校验和必要时的备份交换。

## 与 50-case 评分表是否一致

v2 表格把教练评分区改回 dialogue-state v3 / 50-case 人审口径。下面这些列与 50-case response-level rubric 对齐：

| 中文列名 | 对应 50-case 字段 | 填写方式 |
| --- | --- | --- |
| 识别当前缺失桥是否准确（0/1/2） | `coach_bridge_identification_score` | 0=没有抓住；1=部分抓住；2=准确抓住 |
| 回复是否基于当前材料（0/1/2） | `coach_groundedness_score` | 0=明显脱离材料；1=部分基于；2=充分基于 |
| 脚手架是否合适（0/1/2） | `coach_scaffold_appropriateness_score` | 0=不合适；1=可用但偏弱/偏强；2=合适 |
| 是否控制关键桥泄露（0/1/2） | `coach_bridge_leakage_control_score` | 0=严重泄露；1=轻微/边界；2=控制良好 |
| 下一步是否清楚（0/1/2） | `coach_next_step_clarity_score` | 0=学生不知道做什么；1=有方向但不清楚；2=下一步清楚 |
| 是否单焦点连贯（0/1/2） | `coach_single_focus_coherence_score` | 0=散乱；1=基本聚焦；2=单焦点清楚 |
| 微例是否围绕桥梁（0/1/2/不适用） | `coach_bridge_oriented_micro_example_score` | 0=微例误导/泄露；1=部分有用；2=围绕桥梁；不适用=没有微例或不需要微例 |
| 微例适用性 | `coach_micro_example_applicability` | 适用 / 不适用 / 不清楚 |
| 泄露标签 | `coach_leakage_label` | 无泄露 / 轻微关键桥泄露 / 重大关键桥泄露 / 答案或代码泄露 / 上下文不足未判断 |
| 总体质量（1-5） | `coach_overall_quality_score` | 1=很差；3=可用但有明显问题；5=很适合给学生 |
| 是否愿意给学生看 | `coach_would_show_to_student` | 是 / 边界 / 否 |
| 学生回答负担 | `student_response_burden` | 低 / 中 / 高 |
| 复核信心 | `coach_reviewer_confidence` | 高 / 中 / 低 |
| 是否需要讨论 | `coach_needs_discussion` | 是 / 否 |
| 教练备注（中文） | `coach_notes` | 用中文简要写判断依据 |

因此，v2 的评分维度与 50-case 是一致的；额外的 pilot validity 字段只用于真实学生迁移性检查。

## 教练填写顺序

1. 先看“学生问题、近期对话、学生代码、当前 AIChat 回复”。
2. 判断隐私是否足够：若仍有姓名、学校、账号、手机号、邮箱或过长原文，填“需继续脱敏”或“因隐私风险排除”。
3. 判断上下文是否足够：足够 / 部分足够 / 不足 / 不清楚。
4. 先独立填写 50-case 对齐评分区，不要先看 AI 预标注；有下拉框的列必须用下拉选择。
5. 再填写 pilot validity 区：缺失桥家族、缺失桥实例、禁止直接说出的内容、可以提示到什么程度、期望学生下一步。
6. 最后比较 AI 预标注，填写是否同意、是否需要裁决。
7. `知情/报告门` 默认保持“待完成”；只有完成知情/同意或报告资格审核后，才能改成“可报告”。

## 中文可选值

### 复核状态

- 待复核
- 已复核
- 需第二教练
- 因隐私风险排除
- 因上下文不足排除

### 隐私复核状态

- 待复核
- 可内部复核
- 需继续脱敏
- 因隐私风险排除

### 上下文是否足够

- 足够
- 部分足够
- 不足
- 不清楚

### 泄露标签

- 无泄露：没有替学生补完当前 critical bridge。
- 轻微关键桥泄露：提示偏强，但学生仍需完成重要推理。
- 重大关键桥泄露：基本替学生补完当前 case-specific reasoning bridge。
- 答案或代码泄露：直接给出最终答案、完整做法或关键代码。
- 上下文不足未判断：材料不足，不能可靠判断泄露。

### 是否愿意给学生看

- 是
- 边界
- 否

### 学生回答负担

- 低：学生可以用一句话、一个小判断或一个局部检查回应。
- 中：学生需要做一小段推理或局部改代码。
- 高：学生需要完成较重推导、重写方案或大范围调试。

## Pilot validity 字段

| 中文列名 | 含义 |
| --- | --- |
| 缺失桥家族（中文） | 用中文写 broad bridge family，例如“二分检查语义桥”“DP状态转移桥”“贡献/差分汇总桥”“调试定位桥”。 |
| 当前缺失桥实例（中文简述） | 写这个学生在这一轮具体没跨过去的桥。 |
| 禁止直接说出的内容（中文） | 写 tutor 这一轮不能直接补完什么。 |
| 可以提示到什么程度（中文） | 写可以给到的安全提示边界。 |
| 期望学生下一步（中文） | 写学生收到合适脚手架后应该能做什么。 |
| 是否匹配现有taxonomy | 是 / 否 / 不确定。 |
| 新桥候选（如无填“无”） | 如果不能放入现有 taxonomy，写候选新桥；否则填“无”。 |
| 观察到的下一轮进展 | 有进展 / 部分进展 / 无进展 / 不清楚 / 不可用。 |

## 公开报告边界

知情/报告门完成前，公开文件只能报告流程状态、schema 可用性和 aggregate counts。不能公开学生原文、完整代码、完整 AI 回复、个案泄露标签、hash 表或可识别的改写示例。
