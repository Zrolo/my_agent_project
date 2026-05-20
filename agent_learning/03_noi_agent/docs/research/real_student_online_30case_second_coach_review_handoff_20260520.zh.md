# Real-Student Online 30-Case Second Coach Review Handoff 20260520

## 给教练的文件

优先填写 9-case 二审焦点包：

```text
.local_private/real_student_online_30case_second_coach_focus_packet_from_ai_prelim_20260520.xlsx
```

完整 30-case 工作簿保留为备用：

```text
.local_private/real_student_online_30case_human_coach_review_packet_cn_v2_full_problem_20260520.xlsx
```

这两个文件都属于内部复核材料，不进入公开仓库，不公开学生原文、完整代码、完整 AIChat 回复、身份信息、hash salt 或可逆映射。

## 教练优先填写哪个表

请优先打开 9-case 焦点包，并填写：

1. `二审评分`
2. `隐私与报告门`

请不要改动：

- `案例上下文`
- `AI预复核参考`
- `下拉选项`

`AI预复核参考` 只用于说明为什么该 case 被选入二审焦点包。它不是人类评分、不是 final gold，也不要求教练照着它填。

## 评分维度

二审评分维度应与 dialogue-state v3 / 50-case 人审逻辑保持一致，重点判断：

| 维度 | 教练判断重点 |
| --- | --- |
| critical-bridge leakage | 回复是否过早补完学生尚未完成的关键中间推理桥 |
| answer/code leakage | 回复是否泄露最终答案、完整做法、关键代码或可直接提交的实现 |
| helpfulness | 回复是否对学生当前问题有帮助 |
| learner burden | 回复是否让学生负担过高、过低或不合适 |
| scaffold quality | 回复是否保留学生下一步思考空间，并给出可执行提示 |
| student_ready | 学生是否已经准备好接收该层级提示 |
| safe_ready | 回复是否可以在教学场景中安全展示 |
| context_sufficiency_for_judgment | 当前题面、上下文、学生状态是否足够支持判断 |
| coach_confidence | 教练对本条判断的信心 |

如果题面或上下文不足，请优先标为上下文不足或不确定，不要硬判。

## 当前 AIChat 回复的身份

工作簿中的“当前AIChat回复”是：

```text
线上已展示 AIChat 回复（观察项，非实验条件）
```

它不是 baseline、不是 condition、不是 control、不是 Repair 输出，也不是 7 个 offline harness 之一。教练可以评价它是否适合作为真实场景观察项，但不要把它当成实验条件比较。

## 隐私与报告门

即使教练完成二审，当前材料仍需经过 privacy/consent/reporting gate 后才能决定是否公开任何 aggregate summary。

默认边界：

- 不公开 case-level labels。
- 不公开学生原文。
- 不公开完整代码。
- 不公开完整 AIChat 回复。
- 不公开 student hash / problem hash 明细。
- 如需论文示例，必须另行 paraphrase / anonymize，并经人工确认。

## 教练完成后建议文件名

请将完成后的内部文件另存为：

```text
.local_private/real_student_online_30case_second_coach_focus_packet_human_reviewed_20260520.xlsx
```

完成后再运行内部 validation，并生成公开安全状态文档。公开文档只报告 workflow status 和 aggregate process counts，不直接报告 case-level 内容。

## 本步骤不改变的研究边界

- 不新增 dialogue-state v3 主实验。
- 不新增 main experiment condition。
- 不重算 dialogue-state v3 主表。
- 不修改线上 AIChat、prompt 或 active mode。
- 不改变学生可见回复。
- 不把 pilot 写成 main result。
- 不把 pilot 写成 learning outcome study。
- 不把 AI preliminary triage 写成人类教练证据。
