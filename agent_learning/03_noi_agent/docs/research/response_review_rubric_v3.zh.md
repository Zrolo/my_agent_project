# AIChat 回复盲评 Rubric v3

本文档定义 Research v1 后续回复盲评的 v3 评分口径。v3 的目标不是增加更多分数，而是把评价拆成主指标、诊断指标和可靠性字段，减少冗余与教练口径漂移。

## 使用边界

- 本 rubric 用于离线 response review、dev ablation、50-case held-out 和 LLM Judge 校准。
- 本 rubric 不用于 RL 训练，不把 rubric 分数当 reward。
- 人工教练评分是 expert reference，不是绝对真值；正式实验需要校准轮、部分双标和分歧裁决。
- 当前 500-row 人工盲评仍是 dev/regression evidence，不是最终论文 headline result。

## 主指标

这些字段进入论文主表或主分析。

| 字段 | 含义 | 评分口径 |
| --- | --- | --- |
| `overall_quality` | 教练整体质量判断 | 1-5；是否愿意把这条回复作为高质量辅导给学生看 |
| `student_ready_pass` | 是否达到可给学生看的综合门槛 | 派生指标：overall >= 4、show=yes、无 major/answer leakage、核心诊断分不为 0 |
| `critical_leakage_label` | 关键桥/答案泄露标签 | `no_leakage` / `minor_bridge_leakage` / `major_bridge_leakage` / `answer_leakage` |
| `scaffold_sufficiency` | 帮助是否足够 | 0-2；专门防止“安全但没帮助” |
| `student_response_burden` | 学生下一轮回复负担 | `low` / `medium` / `high`；作为交互成本指标，不进入 core score |

## 诊断指标

这些字段用于 error analysis、prompt 修订和 LLM Judge 校准，不作为论文主表的唯一结论。

| 字段 | 0 | 1 | 2 |
| --- | --- | --- | --- |
| 是否抓住卡点 | 答非所问或没有抓住当前 missing bridge | 相关但偏宽/只抓到一部分 | 直接针对学生当前缺失桥梁 |
| 是否贴合题目/对话 | 泛泛讲算法 | 部分贴合 | 明显利用题面、学生话语和近期对话 |
| 帮助强度是否合适 | 太强直接给答案，或太弱空泛追问 | 略强/略弱但仍可用 | 强度适合当前学生状态 |
| 下一步是否清楚 | 学生不知道下一步做什么 | 有下一步但偏宽或偏费力 | 下一步明确、具体、低输入成本 |
| 是否保持单一焦点 | 多目标混杂 | 少量漂移 | 围绕一个主要卡点推进 |
| 桥梁导向微型例子 | 例子无关或直接泄露关键桥 | 相关但像临时任务 | 能引导学生抽象可迁移关系 |

## Micro-example 适用性

`bridge_oriented_micro_example_score` 必须先判断 `micro_example_applicability`。

- `applicable`：回复使用了例子，或本轮明显需要用小例子帮助学生观察桥梁。
- `not_applicable`：本轮不需要单独评价小例子，或回复没有使用例子且不用例子也合理。

当 `not_applicable` 时，微型例子分数可以留空，分析脚本不把它当作 0 分。

## 泄露与透露正当性

v3 不再把 `是否控制关键桥泄露 0-2` 作为论文主安全指标。主安全判断使用：

```text
critical_leakage_label + bridge_reveal_justification
```

`bridge_reveal_justification` 的含义：

- `no_reveal`：没有实质透露当前关键桥。
- `pedagogically_justified`：学生已经说出、当前允许强提示或正在复盘总结，透露有教学理由。
- `borderline`：有透露，但是否过早或过完整不确定。
- `unjustified`：过早或过完整替学生补完当前关键桥。

这可以避免把所有有信息量的教学解释都误判为泄露。

## 可靠性字段

| 字段 | 用途 |
| --- | --- |
| `reviewer_confidence` | 标记教练对本次评分的把握 |
| `needs_discussion` | 标记是否需要二次讨论/裁决 |
| `coach_notes` | 记录 major leakage、show=no、overall<=2、rank 第一/最后、low confidence 等强制备注 |
| `review_status` | 标记 unlabeled / labeled / needs_discussion / ai_prelim_reviewed |

## 开发用综合分

`rubric_eval_score_v1` 只用于 dev 阶段快速筛查 condition，不替代原始教练评分，也不作为论文唯一结论。

它会奖励：

- 高 `overall_quality`
- `student_ready_pass`
- 高 `scaffold_sufficiency`
- 清楚的下一步
- 对准卡点

它会惩罚：

- `major_bridge_leakage` / `answer_leakage`
- `show=no`
- `student_response_burden=high`

正式论文应报告原始主指标和配对比较，而不是只报告这个综合分。
