# 桥梁导向微型例子盲评分析（micro_example_policy_n10）

日期：2026-05-10

## 数据来源

- 评审批次：`micro_example_policy_n10`
- 页面名称：`桥梁导向微型例子 n10`
- 标注文件：`docs/research/coach_response_review_labels_micro_example_policy_n10.jsonl`
- 盲评 workbook：`docs/research/coach_response_review_workbook_micro_example_policy_n10.csv`
- 样本数量：10 条 AIChat 回复，覆盖 `cp_bridge_001` 到 `cp_bridge_010`

这轮结果是小样本教练盲评，不应作为最终 gold truth。它更适合用于 prompt/rules 迭代、失败样例归档和论文的初步 error analysis。

## 总体结果

| 指标 | 数量 | 比例 |
|---|---:|---:|
| good | 6 | 60% |
| okay | 2 | 20% |
| bad | 2 | 20% |
| no_leakage | 9 | 90% |
| major_bridge_leakage | 1 | 10% |
| minor_bridge_leakage | 0 | 0% |
| answer_leakage | 0 | 0% |

初步判断：加入 bridge-oriented micro-example 规则后，回复整体质量比早期更稳定，多数回复能做到“不泄露且有教学推进”。但仍有两个明显风险：

1. 模板化和 prompt 痕迹会破坏真实教练感。
2. 字段匹配式兜底仍会产生“安全但没用”的低质量回复。

## 逐条标注概览

| case_id | response_id | 质量 | 泄露 | 关键备注摘要 |
|---|---|---|---|---|
| cp_bridge_001 | resp_4669ab0d1f | good | no_leakage | 质量可以，但“桥梁问题、极小例子、问题”显得模板化，语气太 AI。 |
| cp_bridge_002 | resp_0d184fc091 | okay | no_leakage | 作为第一层支架不错，但只讲了 check 语义，没有接回边界移动和二分不变量。 |
| cp_bridge_003 | resp_d5afdfdf5f | okay | no_leakage | 选择题能降低表达门槛，但公式和状态提示仍有凭空引导感。 |
| cp_bridge_004 | resp_cbc62c6b2a | good | no_leakage | 质量可以，分清楚了例子和问题。 |
| cp_bridge_005 | resp_39ee4cbfd4 | good | no_leakage | lazy 例子抓得准，但 A/B 有带路风险，缺少迁移追问。 |
| cp_bridge_006 | resp_c6a7c28f0a | bad | major_bridge_leakage | 直接回复模板，泄露了 prompt。 |
| cp_bridge_007 | resp_6153ec99d9 | good | no_leakage | 能把学生拉回结构依据，但“先不急着确认方法”等语气生硬，且略早锚定 trie。 |
| cp_bridge_008 | resp_321d77f1e3 | good | no_leakage | 通过反问点醒学生，没有直接说明答案。 |
| cp_bridge_009 | resp_4fe27dbcff | good | no_leakage | 很接近桥梁型提问，抓住贪心安全性，但还差一般化论证。 |
| cp_bridge_010 | resp_9a6d6ed1e2 | bad | no_leakage | 没有有用信息，像字段匹配后截断，应去掉或降级这类规则。 |

## 主要发现

### 1. Bridge-oriented micro-example 的方向是有效的

`good = 6/10` 且 `no_leakage = 9/10`，说明“用微型例子让学生观察关系，再抽象成规则”这个方向有明显价值。

尤其是 `cp_bridge_004`、`cp_bridge_005`、`cp_bridge_009`，都能把学生当前卡点压缩成一个较小、可回答的问题。这支持论文中的一个细分标准：

> 高质量 micro-example 不只是让学生完成临时任务，而是让学生观察一个缺失桥梁关系，并把观察抽象成可迁移规则。

### 2. 模板化语气会降低教练感

多条备注指出回复有明显模板味：

- “这个卡点非常具体，我们直接看一个极小例子”
- “桥梁问题 / 极小例子 / 问题”
- “先不急着确认方法”

这些表达虽然结构清楚，但不像真实竞赛教练说话。后续 prompt 应要求主 LLM 保留教学结构，但不要显式暴露内部 scaffold/rubric 术语。

建议增加约束：

```text
不要向学生显式说“桥梁问题”“极小例子”“按照模板”等内部教学结构词。
可以自然地说“我们先拿一个很小的情况看一下”。
```

### 3. “不泄露”不等于“有教学价值”

`cp_bridge_010` 被标为 `bad + no_leakage`，说明当前系统仍可能产生安全但无用的回复。这个失败模式很重要，因为它说明 leakage control 不能单独作为质量指标。

论文评测中应同时保留：

- leakage control
- scaffold appropriateness
- next-step clarity
- bridge-oriented transfer

### 4. 字段匹配式兜底需要收敛

`cp_bridge_010` 的备注明确指出“完全是字段匹配然后截断”。这说明部分 rules 仍可能过度保守或误触发，导致主 LLM 没有给出真正的教学帮助。

下一步应把这类规则改成：

1. 只作为 weak signal；
2. 不直接生成最终回复；
3. 如果触发兜底，至少要求回复包含一个可回答的下一步问题。

### 5. 选择题可以保留，但要谨慎

`cp_bridge_003` 和 `cp_bridge_005` 的备注都提到选择题有价值：当学生基础薄弱时，让学生用自己的话组织语言可能太难，选择题能降低入口难度。

但选择题也有风险：

- 可能让学生碰巧选对；
- 可能把关键桥暗示得太明显；
- 可能变成“临时任务”而非桥梁理解。

建议规则：

```text
选择题可以用于低表达能力学生，但必须追加“为什么”或“用一句话总结观察到的关系”。
```

## 高优先级失败样例

### Regression Case A：Prompt/模板泄露

- case_id：`cp_bridge_006`
- response_id：`resp_c6a7c28f0a`
- 标注：`bad + major_bridge_leakage`
- 教练备注：直接回复了模板，直接泄露出了我们的 prompt。

应转成回归测试：

```text
AI 回复中不得出现内部 prompt、rubric、schema、模板标题、bridge contract 字段名或系统控制语。
```

### Regression Case B：字段匹配式无效回复

- case_id：`cp_bridge_010`
- response_id：`resp_9a6d6ed1e2`
- 标注：`bad + no_leakage`
- 教练备注：没有有用信息，完全是字段匹配然后截断了，建议去掉这部分规则。

应转成回归测试：

```text
当规则触发安全兜底时，回复仍必须提供一个贴合学生当前卡点的下一步动作，不能只有拒绝、截断或空泛提醒。
```

## 对论文的作用

这轮盲评可以支撑三个论文观点：

1. **Bridge-oriented micro-example 是一个有价值的脚手架质量维度。**
   单纯有例子不够，关键是例子是否帮助学生抽象可迁移关系。

2. **Critical bridge leakage 不能只看完整答案/代码。**
   模板泄露、关键桥暗示、过早锚定算法方向都可能影响教学有效性。

3. **安全性和教学价值需要同时评估。**
   `bad + no_leakage` 说明只降低泄露率不足以证明系统更好。

## 下一步建议

1. 把 `cp_bridge_006` 和 `cp_bridge_010` 加入 regression cases。
2. 修 Bridge Contract Tutor prompt，禁止内部模板词和 prompt 痕迹。
3. 修 rules 兜底逻辑，避免字段匹配后生成低价值回复。
4. 用同样 10 条样本重新生成 `micro_example_policy_n10_v2`。
5. 再跑一轮盲评，比较：
   - bad 是否下降；
   - major_bridge_leakage 是否消失；
   - good 是否保持或提升；
   - 备注里是否仍出现“模板化”“字段匹配截断”。
