# 20 条 Mini-Study 回复盲评分析（2026-05-10）

## 数据来源

- 已填盲评表：`/Users/kongyouli/Downloads/coach_response_review_workbook_mini_study_20_20260510_zh_filled.xlsx`
- 匿名 key：`docs/research/coach_response_review_workbook_mini_study_20_20260510.key.csv`
- 解析后的标注 JSONL：`docs/research/coach_response_review_labels_mini_study_20_20260510.jsonl`
- 样本规模：20 个 case × 5 个系统条件 = 100 条回复；100 条均已标注为 `labeled`。

这仍然是单教练小样本盲评，不是最终 gold truth。它适合用来判断 Research v1 的方向、发现系统误差，并为 50 条双标实验做准备。

## 总体结果

| 系统 | n | 核心均分 | 含微例均分 | 抓住卡点 | 帮助强度 | 泄露控制 | 微型例子 | 任意泄露 | 重大/答案泄露 | 第一名数 | 平均排名* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `current_system` | 20 | 1.408 | 1.375 | 1.700 | 0.550 | 0.750 | 1.125 | 70% | 55% | 0 | 2.667 |
| `single_llm_structured` | 20 | 1.800 | 1.782 | 1.850 | 1.550 | 1.700 | 1.667 | 25% | 5% | 8 | 1.750 |
| `bridge_contract` | 20 | 1.733 | 1.745 | 1.800 | 1.400 | 1.650 | 1.938 | 30% | 5% | 2 | 2.400 |
| `bridge_contract + guard` | 20 | 1.675 | 1.651 | 1.750 | 1.200 | 1.650 | 1.588 | 25% | 10% | 4 | 2.000 |
| `bridge_contract + guard + repair` | 20 | 1.733 | 1.717 | 1.650 | 1.450 | 1.850 | 1.706 | 15% | 0% | 6 | 1.500 |

\* 平均排名只统计你填写了数字排名的行，`tie` 行不计入平均排名。

## 泄露标签分布

| 系统 | no_leakage | minor | major | answer |
|---|---:|---:|---:|---:|
| `current_system` | 6 | 3 | 11 | 0 |
| `single_llm_structured` | 15 | 4 | 1 | 0 |
| `bridge_contract` | 14 | 5 | 1 | 0 |
| `bridge_contract + guard` | 15 | 3 | 2 | 0 |
| `bridge_contract + guard + repair` | 17 | 3 | 0 | 0 |

## 关键结论

1. `current_system` 已经可以作为强有力的负向 baseline：核心均分最低（1.408），重大/答案级泄露最高（55%），且没有任何 case 获得第一名。这说明当前线上 AIChat 的“自报 level hard gate + prompt 控制”不足以防住关键桥泄露。
2. `single_llm_structured` 在这批样本中表现非常强：核心均分最高（1.800），第一名最多（8/20），重大/答案级泄露只有 5%。这提醒我们，论文里不能简单声称多层 LLM 一定优于单 LLM；必须把 single-LLM structured 作为正式 baseline。
3. `bridge_contract` 的桥梁导向微型例子分最高（1.938），说明 Bridge Contract 对“让例子围绕桥梁展开”确实有帮助；但它的排名第一数只有 2/20，说明光有 contract 还不等于总体回复最好。
4. `bridge_contract + guard` 没有稳定优于 `bridge_contract`，重大/答案级泄露反而是 10%。这说明当前 Leakage Judge/Guard 还不能被直接视为“质量提升器”，它需要看触发条件、误判、以及是否真正影响 final response。
5. `bridge_contract + guard + repair` 的泄露控制最好：重大/答案泄露为 0%，任意泄露为 15%，第一名数为 6/20。但这批结果里 `repair_applied_count=0`，所以不能把改善归因于 Repair 本身，只能说“允许 guard/repair 的这组 final response 在盲评中更安全”。

## 质性发现

### 1. 当前系统的主要问题是“直接补完关键桥”

典型备注包括：直接给出 DP 状态、转移、可行性判断、并查集合并对应代码等。它不是简单的“完整代码泄露”，而是更符合我们论文里的 `critical bridge leakage`。

### 2. 过度保守也会伤害质量

最差样本里多次出现“泛泛要求学生再给题号或代码行”的备注。例如 01 背包倒序枚举、并查集合并映射这些 case，学生已经明确说出卡点，系统却仍要求补题号或代码行，导致没有回应当前桥梁。

后续自检显示，这不是主 system prompt 主动要求“必须给题号/代码行才能回答”，而是规则层误降级后触发了 `enforce_level_gate()` 的固定 L1 兜底语。具体表现为：同一概念内的对比追问被误判为 `multi_question`，以及“题目说...我知道...但不知道...”被误判为只复述题意。该问题已作为 hard-gate fallback artifact 进入回归测试。

### 3. Bridge Contract 对高质量 micro-example 有正向信号

`bridge_contract` 的微型例子均分最高。优质样本通常有三个共同点：先说明要观察的关系，给一个贴近原题的小例子，再让学生抽象出可迁移规则。

### 4. Guard/Repair 目前不能当成已验证模块

这轮 `+ repair` 组没有实际 repair 触发，所有 final response source 都是 `candidate`。所以后续必须专门构造或采样高泄露候选，才能验证 Repair Generator 是否真的有效。

## 最差样例摘录

- `cp_bridge_010` / `current_system` / `no_leakage` / rank `tie`: 模板式要求再给题号或代码行，未回应“01 背包为什么倒序枚举”的核心疑问。
- `cp_bridge_017` / `bridge_contract` / `no_leakage` / rank `tie`: 泛泛要求学生再给题号或代码行，未利用学生已经明确表达的“并查集合并对应哪步代码”的卡点。
- `cp_bridge_017` / `bridge_contract + guard` / `no_leakage` / rank `tie`: 泛泛要求学生再给题号或代码行，未利用学生已经明确表达的“并查集合并对应哪步代码”的卡点。
- `cp_bridge_010` / `bridge_contract + guard` / `no_leakage` / rank `tie`: 模板式要求再给题号或代码行，未回应“01 背包为什么倒序枚举”的核心疑问。
- `cp_bridge_017` / `bridge_contract + guard + repair` / `no_leakage` / rank `tie`: 泛泛要求学生再给题号或代码行，未利用学生已经明确表达的“并查集合并对应哪步代码”的卡点。
- `cp_bridge_010` / `bridge_contract + guard + repair` / `no_leakage` / rank `tie`: 模板式要求再给题号或代码行，未回应“01 背包为什么倒序枚举”的核心疑问。
- `cp_bridge_010` / `bridge_contract` / `no_leakage` / rank `tie`: 模板式要求再给题号或代码行，未回应“01 背包为什么倒序枚举”的核心疑问。
- `cp_bridge_013` / `bridge_contract + guard` / `major_bridge_leakage` / rank `tie`: 完整给出函数含义、base case 和递推式，直接把递归两座关键桥都讲完。

## 最好样例摘录

- `cp_bridge_004` / `single_llm_structured` / `no_leakage` / rank `2`: 很好地抓住“当前药草从哪些旧状态来”的卡点，用一株药草让学生列出选/不选来源，没有直接给公式。
- `cp_bridge_002` / `bridge_contract + guard + repair` / `no_leakage` / rank `2`: 用最小可行性例子钉住 check(mid) 的语义，让学生先判断 mid 是否可行，未直接规定 true/false。
- `cp_bridge_007` / `bridge_contract + guard` / `no_leakage` / rank `1`: 从两个 01 串的单向前缀关系入手，能让学生自己判断是否适合 Trie，焦点很准。
- `cp_bridge_016` / `bridge_contract` / `no_leakage` / rank `3`: 明确采用 1-based 数组并让学生比较两种循环，能够促成边界条件对齐。
- `cp_bridge_015` / `single_llm_structured` / `no_leakage` / rank `1`: 非常适合溢出排查：先看数据范围，再算极端和/积，能引导学生自己定位变量。
- `cp_bridge_012` / `bridge_contract` / `no_leakage` / rank `2`: 用村庄和道路的类比引导“对象当点、关系当边”，并要求抽象规则，教学性强。
- `cp_bridge_006` / `bridge_contract + guard + repair` / `no_leakage` / rank `1`: 把“逐条比较”与“沿 Trie 走几步”做数量对比，能让学生自己发现为什么不用重扫。
- `cp_bridge_009` / `bridge_contract` / `no_leakage` / rank `2`: 用先选早结束与晚结束的两个方案比较后续可选数，能帮助学生理解贪心不吃亏。

## 对论文的直接意义

这轮盲评支持三个论文判断：

1. `critical bridge leakage` 是必要指标，因为 current_system 的主要失败不是完整代码，而是关键中间桥梁泄露。
2. `single_llm_structured` 必须作为强 baseline，因为它在单教练 20-case 中质量和安全性都很强。
3. `bridge-oriented micro-example` 值得进入 response quality rubric，因为它能区分“临时填空任务”和“可迁移桥梁理解”。

## 下一步

1. 扩大到 50 条 seed，并做至少 15 条双教练标注，避免单教练主观性过高。
2. 单独做 Repair stress test：人为收集或生成高泄露 candidate，验证 Repair 是否能降低泄露且不损害教学质量。
3. 保留 `single_llm_structured` 作为正式 baseline，不要把论文写成“多 Judge 必然更好”。
4. 优先修 current_system 的关键桥泄露和 hard-gate fallback 误降级问题，但按 control harness 原则离线 patch，不直接在线改 system prompt。
