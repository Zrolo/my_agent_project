# Real-Student Online 2-Case Adjudication Handoff 20260520

## 给裁决者的文件

请填写内部私有裁决包：

```text
.local_private/real_student_online_2case_adjudication_packet_20260520.xlsx
```

该文件只包含 9-case 二审焦点包中仍需裁决的 2 条记录。它属于内部裁决材料，不进入公开仓库，不公开学生原文、完整代码、完整 AIChat 回复、case-level labels、student hashes、problem hashes、hash salt 或可逆映射。

## 裁决者需要填写哪些 sheet

请优先填写：

1. `裁决评分`
2. `隐私与报告门`

请不要改动：

- `案例上下文`
- `二审参考`
- `AI预复核参考`
- `下拉选项`

`二审参考` 和 `AI预复核参考` 只用于说明争议来源。最终裁决应以裁决者对题面、学生状态、当前 AIChat 回复和评分标准的独立判断为准。

## 裁决评分字段

| 字段 | 填写要求 |
| --- | --- |
| 裁决状态 | 从下拉中选择：待裁决 / 已裁决 / 因隐私风险排除 / 因上下文不足排除 |
| 裁决上下文是否足够 | 判断题面、上下文、学生状态是否足够支持评分 |
| 裁决最终泄露标签 | 判断是否存在 critical-bridge leakage 或 answer/code leakage |
| 裁决总体质量（1-5） | 只作内部质量判断，不作为主实验结果 |
| 裁决是否愿意给学生看 | 判断该回复能否作为真实教学回复展示 |
| 裁决信心 | 高 / 中 / 低 |
| 是否可纳入内部汇总 | 若上下文足够且隐私风险可控，可选“是”；否则选“否”或“待定” |
| 裁决备注（中文） | 简要说明裁决理由，避免粘贴学生原文或完整代码 |

## 当前 AIChat 回复的身份

工作簿中的当前 AIChat 回复是：

```text
线上已展示回复，观察项，非实验条件
```

它不是 baseline、condition、control、online condition、Repair output，也不是 7 个 offline harness 之一。

## 隐私与报告门

即使裁决完成，也不自动意味着可以公开报告。公开前仍需确认：

- `隐私复核状态 = 可内部复核`
- `知情/报告门 = 可报告`
- 示例已 paraphrase / anonymize
- 不公开学生原文、完整代码、完整 AIChat 回复或 case-level labels

当前默认状态是：`reportable case-level evidence = 0`。

## 裁决完成后的建议文件名

请将完成后的内部文件另存为：

```text
.local_private/real_student_online_2case_adjudication_packet_human_adjudicated_20260520.xlsx
```

完成后运行：

```bash
python3 evals/aichat/validate_real_student_2case_adjudication_review.py \
  .local_private/real_student_online_2case_adjudication_packet_human_adjudicated_20260520.xlsx
```

## 本步骤不改变的研究边界

- 不新增 dialogue-state v3 主实验。
- 不新增 main experiment condition。
- 不重算 dialogue-state v3 主表。
- 不修改线上 AIChat、prompt 或 active mode。
- 不改变学生可见回复。
- 不把裁决包写成 main result。
- 不把 real-student pilot 写成 learning outcome study。
