# LLM Grader Calibration Protocol v2

本文档规定 v3 评价体系下的 LLM Grader 校准实验。目标是比较不同 grader 形式是否能接近教练 reference，而不是用 LLM Judge 替代教练。

## 校准对象

比较三种 grader：

1. `likert_only_judge`
   - 只给整体 Likert 分数或简单好坏判断。
   - 用来验证“直接打分”是否不稳定。

2. `generic_rubric_judge`
   - 使用通用 tutoring rubric。
   - 不读取 case-specific forbidden content / critical bridge boundary。

3. `case_specific_bridge_rubric_judge`
   - 读取 `success_criteria`、`forbidden_content`、`critical_bridge_boundary`、`acceptable_reveal`、`expected_student_next_action`。
   - 专门判断 missing bridge 与 critical bridge leakage。

## 输入

使用当前人工盲评 500-row 作为 dev reference。每条 grader 输入包含：

- 原题/必要题面；
- 学生当前问题；
- 近期对话；
- 上下文 AI 回复；
- case-specific rubric；
- 目标 AI 回复；
- 可选匿名 condition 信息不进入 grader prompt。

注意：历史 500-row dev 表可能缺少 v3 case-specific rubric 字段。校准包必须记录 `case_specific_rubric_present`；缺少这些字段的样本只能用于 Likert-only / generic-rubric 对照，不能作为 case-specific grader 的 headline 证据。

## 输出格式

LLM Grader 必须允许：

```text
UNKNOWN / INSUFFICIENT_CONTEXT
```

最低输出字段：

```json
{
  "overall_quality": 1,
  "student_ready": "yes|borderline|no|UNKNOWN",
  "leakage_label": "no_leakage|minor_bridge_leakage|major_bridge_leakage|answer_leakage|UNKNOWN",
  "bridge_reveal_justification": "no_reveal|pedagogically_justified|borderline|unjustified|UNKNOWN",
  "scaffold_sufficiency": 0,
  "student_response_burden": "low|medium|high|UNKNOWN",
  "rationale": "..."
}
```

## 指标

报告：

- overall agreement；
- student-ready agreement；
- leakage precision / recall / F1；
- major leakage false negative rate；
- answer leakage false negative rate；
- UNKNOWN / INSUFFICIENT_CONTEXT rate；
- case-specific rubric coverage；
- 与教练 notes 的 qualitative disagreement memo。

其中最重要的是：

```text
major leakage false negative rate
```

因为系统把严重关键桥泄露放过，比误判轻微泄露更危险。

## 分阶段运行

1. 20-row calibration smoke：检查格式、UNKNOWN、明显漏判。
2. 500-row dev reference：做正式 dev calibration。
3. freeze grader prompt。
4. 50-case held-out 后只报告 frozen grader 与 coach reference 的一致性，不再在 held-out 上调 grader。

## 解释边界

- LLM Grader 不是 gold truth。
- 如果 case-specific grader 明显优于 Likert-only grader，只能说明样本特定 rubric 对开放式回复评价有帮助。
- 本项目不做 RL，不使用 grader 输出训练 tutor。
- 与 Rubrics as Rewards 的关系只限于：我们采用 rubric-based evaluation 组织开放式评价，不采用 rubric-reward RL。
