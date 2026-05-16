# Dialogue-State Follow-up Case Design

## 背景

当前 `bridgebench_cp_heldout_v2_50_draft.jsonl` 主要覆盖真实题源驱动的首次求助场景：学生刚打开 AIChat，提出“这题怎么想 / check 是什么 / 状态怎么设”一类问题。这对测试初始 missing bridge diagnosis 有用，但还不足以评估 AIChat 的核心教学能力：根据学生对上一轮脚手架问题的回答，继续调整提示粒度。

因此需要新增一层 dialogue-state case 设计，用于评估 follow-up tutoring turn，也就是：

```text
学生首次提问
-> 固定上下文 AI 给出一个轻脚手架问题
-> 学生做出短回答、半对回答、错误回答或完全跟不上
-> 被评测系统生成当前轮 AI 回复
```

本设计不替换 held-out v2；它在 v2 真实题源基础上生成 v3 草稿。

## 目标

1. 测量 AI 是否能接住学生上一轮回答，而不是重新讲一遍题解。
2. 测量 AI 是否能根据学生跟随状态调整 scaffold 粒度。
3. 保持所有 baseline 的输入上下文一致，避免前一轮回复来自某个被评测 condition 而污染实验。
4. 支持论文中关于 contingent scaffolding / adaptive scaffolding 的分析。

## 非目标

- 不生成完整多轮真实教学实验。
- 不声称这些对话是真实学生原话。
- 不把历史线上 AI 回复作为被评测系统输入。
- 不让某个 baseline 先生成上文，再由另一个 baseline 接着回答。

## 核心字段

新增或强化以下字段：

```json
{
  "turn_position": "initial|followup",
  "context_type": "initial_question|followup_after_correct_short_answer|followup_after_partial_answer|followup_after_wrong_answer|followup_after_code_attempt|followup_after_prerequisite_gap",
  "student_scaffold_followability": "F1|F2|F3|F4",
  "followability_label_confidence": "high|medium|low",
  "followability_evidence_quote": "...",
  "followability_uncertainty_reason": "...",
  "prior_ai_scaffold": "...",
  "student_reply_to_prior_scaffold": "...",
  "expected_tutor_move": "advance|clarify|micro_step|prerequisite_repair|safe_redirect",
  "fixed_recent_dialogue_source": "synthetic_dialogue_state_v3"
}
```

`recent_dialogue` 仍保留为最终 runner 读取的上下文字段，但 v3 生成器需要从 `prior_ai_scaffold` 和 `student_reply_to_prior_scaffold` 组合出完整上下文。

## 学生脚手架跟随状态

`student_scaffold_followability` 不应只是教练经验判断。它必须由上一轮 `prior_ai_scaffold` 与学生的 `student_reply_to_prior_scaffold` 共同决定，作为一个可标注、可复核、可报告一致性的 learner-state 字段。

标注员只判断学生**对上一轮脚手架问题的反应**，不要因为“学生整体水平可能不错/很差”而改标签。

| 等级 | 中文名 | 可观察证据 | 当前轮 AI 应做什么 |
| --- | --- | --- | --- |
| F1 | 跟得上 | 学生回答了上一轮问题；方向正确；没有明显概念混淆；可以继续推进 | 简短确认，推进到下一座小桥 |
| F2 | 部分跟上 | 学生回答方向大致对，但表达含糊、漏关键条件、仍显得不确定，或只答了一半 | 先确认正确部分，再追问一个更细的点 |
| F3 | 跟得吃力 | 学生回答偏离上一轮问题、混淆关键概念、给出错误判断，或只用“不会/不知道”回应当前小问题 | 降低粒度，用极小例子、局部观察或二选一检查 |
| F4 | 基础断层 | 学生暴露出无法理解上一轮脚手架中的前置概念、符号、数据结构对象或代码基本含义 | 暂停本题推进，先补最小 prerequisite |

### 判定规则

1. 先看上一轮 AI 问了什么，再看学生是否回答了这个问题。
2. 如果学生回答正确且可继续推进，标 F1。
3. 如果学生方向对但不完整，标 F2。
4. 如果学生回答错误、明显偏题或无法处理当前小问题，标 F3。
5. 如果学生连上一轮问题中的基础概念都不懂，标 F4。
6. 如果无法判断，使用 `followability_label_confidence=low`，并填写 `followability_uncertainty_reason`；不要强行把所有样本塞进 F1-F4。

### 证据与置信度

每条 follow-up case 必须写：

```json
{
  "followability_label_confidence": "high|medium|low",
  "followability_evidence_quote": "...",
  "followability_uncertainty_reason": "..."
}
```

要求：

- `followability_evidence_quote` 必须引用学生对上一轮脚手架的回答。
- 低置信样本不能进入 headline metrics，只能进入 error analysis 或待裁决列表。
- 如果证据不足，应优先修 case，而不是让标注员硬判。

### 分歧裁决

F1-F4 是新增教育判断字段，正式实验前需要做小规模双标：

```text
Coach A 标全部 v3 follow-up cases。
Coach B 至少复标 20 条 follow-up cases。
报告 F1-F4 agreement、相邻等级 weighted agreement、低置信率。
分歧样本进入 adjudication。
```

允许相邻等级分歧，例如 F1/F2、F2/F3；非相邻分歧，例如 F1/F3、F2/F4，需要重点复查 case 是否写得过于模糊。

## 推荐分布

对于 50-case dialogue-state v3 draft：

| 类型 | 数量 | 说明 |
| --- | ---: | --- |
| initial_question | 10 | 保留首次求助，用于和 v2 对齐 |
| followup_after_correct_short_answer | 7 | F1，学生能跟上 |
| followup_after_partial_answer | 8 | F2，学生半对但仍需追问 |
| followup_after_wrong_answer | 7 | F3，学生理解偏了 |
| followup_after_code_attempt | 10 | 学生贴代码或错误实现后继续问 |
| followup_after_prerequisite_gap | 5 | F4，学生需要补基础概念 |
| policy/direct-answer special | 3 | 保留直接要答案/代码类安全场景 |

这不是硬性论文最终分布；进入 50-case 主实验前可根据题源和教练复核调整，但 follow-up case 应占多数。

## 示例

### F1：跟得上

```text
学生：这题为什么要二分？
AI：先看候选值 x 变大时，条件是更容易满足还是更难满足？
学生：x 越大越难满足。
```

当前轮 AI 应该：确认这个观察，并让学生判断 true/false 后保留哪一侧。不要重新解释完整二分答案。

### F2：部分跟上

```text
学生：check 里面 true 到底是什么意思？
AI：你先拿一个很小的候选值试一下，看看它表示“能做到”还是“做不到”。
学生：应该是能做到吧，但我不知道后面往哪边。
```

当前轮 AI 应该：确认“能做到”是否和题意匹配，再让学生比较候选值变大/变小时可行性如何变化。

### F3：跟得吃力

```text
学生：dp 这一格是啥意思？
AI：先说这一格对应“处理到哪一步”。
学生：是不是记录答案？我不确定。
```

当前轮 AI 应该：降低粒度，要求学生先区分“下标表示范围/位置”和“值表示目标量”，可以给极小位置观察，不直接给完整状态定义。

### F4：基础断层

```text
学生：lazy 到底表示啥？
AI：先看一个节点 [1,2]，如果整段加了 5，但还没往两个叶子递归，你觉得叶子现在真的改了吗？
学生：我不太懂节点和叶子是什么意思。
```

当前轮 AI 应该：暂停 lazy 细节，先解释线段树节点/叶子/区间覆盖的最小概念，再回到题目。

## 生成原则

1. `prior_ai_scaffold` 必须固定，不属于任何被评测 condition。
2. `prior_ai_scaffold` 只能是轻脚手架，不能泄露完整 critical bridge。
3. `student_reply_to_prior_scaffold` 应短而自然，不要写成标准答案。
4. F1/F2/F3/F4 应体现不同跟随状态，而不是只改变文字长度。
5. 对代码场景，应允许学生贴代码后只问一句短问题。
6. 生成器应保留真实题源字段和 v2 兼容字段，避免后续 runner 大改。

## 评测影响

Response blind review 表格需要额外展示：

- 原题题面 / 必要题面；
- 固定近期对话；
- 学生对上一轮 AI 问题的回答；
- 当前待评分 AI 回复。

新增评分关注点：

- 是否接住学生上一轮回答；
- 是否正确判断学生跟随状态；
- 是否选择合适的下一步 tutor move；
- 是否在 F3/F4 场景中降低粒度，而不是继续推进完整题解。

## 论文写法

英文：

> We evaluate both initial help-seeking turns and follow-up tutoring turns. In follow-up turns, the tutor observes a fixed prior scaffold and a short student response, then must decide whether to advance, clarify, micro-scaffold, or repair prerequisite understanding.

中文：

> 我们同时评估首次求助轮和后续辅导轮。在后续辅导轮中，Tutor 会看到固定的上一轮脚手架问题和学生的短回答，并需要决定是继续推进、澄清条件、细化脚手架，还是回到前置概念修复。

## 验收标准

- v3 生成器不覆盖 v2 文件。
- v3 case 仍能通过 held-out dataset 校验，或新增对应 v3 校验器。
- 每条 follow-up case 都有 `student_scaffold_followability` 和 `expected_tutor_move`。
- 每条 follow-up case 都有 `followability_evidence_quote` 和 `followability_label_confidence`。
- 低置信 followability 样本必须标记，不进入 headline metrics。
- `recent_dialogue` 中的 prior AI 回复不来自任一被评测 baseline。
- 盲评表能显示固定上下文和当前目标 AI 回复。
- 文档与数据均明确 synthetic-but-grounded，不声称为真实学生原话。
