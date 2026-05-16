# CP-MissingBridgeBench 评测协议 v2

日期：2026-05-15

本协议用于 Research v1 之后的 AIChat / CP-MissingBridgeBench 回复评测。它的目标不是消除教育评审中的所有主观性，而是把教练判断变成可校准、可复核、可报告的 expert reference。

## 1. 为什么需要 v2

算法竞赛辅导回复不是单纯的正确/错误分类。一个回复可能：

- 没给完整代码，但说穿了关键桥梁；
- 没有泄露，但过于空泛，学生无法继续；
- 语言很自然，但没有接住学生当前问题；
- 给了一个微型例子，但例子已经把学生要发现的关系演示完。

这些都需要教育判断。参考 AI tutor / agent eval 相关工作，开放式辅导任务通常采用 rubric-based human evaluation、sample-specific criteria、partial double annotation 和 LLM judge calibration，而不是只靠自动指标。

## 2. 角色定义

| 角色 | 作用 | 是否作为最终真值 |
| --- | --- | --- |
| Coach A | 主评审，完成全部样本 | expert reference |
| Coach B | 复评 20%-40% 样本 | agreement / calibration |
| Adjudicator | 处理重大分歧 | adjudicated reference |
| AI prelim reviewer | 开发阶段初筛高风险样本 | 否 |
| Offline deterministic checks | 检查空回复、代码块、内部标签、延迟等 | 客观工程指标 |
| LLM judge / grader | 辅助检测开放语义维度 | 否，需和 coach reference 校准 |

正式论文中应使用 `coach reference`、`expert reference` 或 `adjudicated reference`，避免把单一教练标签称为绝对 ground truth。

## 3. 数据分工

| 数据集 | 用途 | 是否可调 prompt |
| --- | --- | --- |
| dev / regression set | 调 prompt、调 rubric、定位错误 | 可以，但必须记录 patch |
| calibration set | 教练共同校准评分标准 | 可以讨论，不进 headline |
| held-out test set | 正式报告系统结果 | 不允许看结果后再改 prompt |
| repair stress set | same-candidate before/after Repair 因果分析 | 可单独报告，不混入主表 |

当前 `dbox_bridge_hybrid_generation_only_50_20260515_merged` 属于 dev / regression 阶段，不作为最终 held-out headline result。

## 4. 标准评测流程

### Step 0：固定版本

在正式 held-out 前冻结：

- tutor prompt；
- Bridge Contract prompt；
- DBox-inspired / Bridge-guided prompt；
- Guard prompt；
- Repair prompt；
- review rubric；
- AI prelim reviewer prompt 或启发式脚本；
- run model configuration。

冻结后不再根据 held-out 结果回头修改 prompt。

### Step 1：校准轮

正式盲评前，抽取 5 条 case 做 calibration round。

流程：

1. Coach A 和 Coach B 同时看同一批样本。
2. 独立给出初始判断。
3. 讨论分歧，重点讨论：
   - 什么算 `major_bridge_leakage`；
   - 什么算合理概念解释；
   - 什么算“安全但帮助不足”；
   - 什么算学生回复负担过高；
   - 微型例子什么时候是 scaffold，什么时候是泄露。
4. 把新边界写回 rubric 或 calibration notes。

校准样本不用于 headline result。

### Step 2：盲评

教练只看匿名回复编号，不看真实 condition。

每条样本按以下顺序读：

1. 原题链接、必要题面、题目上下文；
2. 近期对话；
3. 上一轮 AI 提问/提示；
4. 学生当前问题；
5. AI 回复（要评分）。

所有评分只针对 `AI 回复（要评分）`，不要评价近期对话本身。

### Step 3：强制备注

以下情况必须写 `coach_notes`：

- `coach_leakage_label = major_bridge_leakage`；
- `coach_leakage_label = answer_leakage`；
- `coach_would_show_to_student = no`；
- `coach_overall_quality_score <= 2`；
- `coach_preference_rank = 1` 或本题最差；
- `coach_needs_discussion = yes`；
- 上下文疑似错配；
- 评分置信度为 low。

备注应说明原因，而不是只写“差”或“好”。

推荐格式：

```text
优点：……
问题：……
建议：……
```

### Step 4：部分双标

正式 50-case 评测中，至少 20%-40% case 由 Coach B 独立复评。

建议抽样覆盖：

- 不同 bridge family；
- 不同题目难度；
- 有代码和无代码 case；
- follow-up 轮次；
- AI prelim 标为高风险的样本；
- 各 condition 表现差距大的样本。

### Step 5：一致性报告

报告至少包含：

- 分类项 percent agreement；
- 有序分数 weighted agreement / weighted kappa；
- 同题偏好 rank 的 win/tie/loss agreement；
- `major_bridge_leakage` 的一致性；
- `would_show_to_student` 的一致性；
- `needs_adjudication_case_ids`。

如果样本数较小，应优先报告 percent agreement、分歧样例和裁决过程，不要过度解读 p-value。

### Step 6：裁决

以下样本进入 adjudication：

- Coach A/B 在泄露等级上相差 `no_leakage` vs `major/answer`；
- `would_show_to_student` 相差 `yes` vs `no`；
- 总体质量差异 >= 2 档；
- 一方标记 `needs_discussion=yes`；
- 上下文疑似错配。

裁决输出：

- final label；
- adjudication note；
- 是否进入 headline metric；
- 是否只作为 error analysis。

## 5. 指标分层

### 主观 / 专家指标

- overall quality；
- core6 / micro7；
- scaffold appropriateness；
- scaffold sufficiency；
- next-step clarity；
- would show to student；
- preference rank。

### 半客观教学风险

- leakage label；
- bridge reveal justification；
- student response burden；
- context alignment flag。

### 客观工程指标

- empty final response；
- stage error；
- internal tag leakage；
- latency p50 / p95；
- LLM call count；
- token usage；
- repair applied；
- blocked / fallback。

论文中应分开报告，不应把所有指标压成一个总分。

## 6. AI 初筛使用规则

AI prelim reviewer 只能用于：

- 开发阶段找高风险样本；
- 按 case 排查明显失败；
- 辅助选择 Coach B 复评样本；
- 给 human review 提供优先级。

AI prelim 不能用于：

- 替代 coach reference；
- 作为 headline result；
- 单独证明某个 condition 更好；
- 自动改 prompt。

LLM judge / grader 必须和 coach reference 做 calibration，报告 precision / recall / false negative / false positive / unknown rate。

## 7. 结果表述边界

允许写：

```text
在 coach-calibrated blind review 中，某条件在 dev set 上表现出更高 student-ready pass。
```

不允许写：

```text
AI 初筛证明某系统显著更好。
```

允许写：

```text
该结果提示 DBox-style scaffold 是强 baseline，Bridge-guided DBox-style 值得进入 held-out 主实验。
```

不允许写：

```text
Bridge-guided DBox-style 已经被证明优于 DBox。
```

## 8. 对当前项目的直接要求

从本协议开始，后续 response blind review 必须满足：

1. 表格包含评分流程、评分说明和强制备注规则；
2. 人类教练使用匿名 workbook；
3. key 文件不进入盲评；
4. AI 初筛报告必须标注 `dev only / not coach gold`；
5. 人类最终分析必须和 AI 初筛分开；
6. 正式 held-out 结果必须至少做部分双标和 adjudication。
