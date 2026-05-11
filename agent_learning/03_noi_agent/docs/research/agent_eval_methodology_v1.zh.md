# Agent Eval 方法论 v1

本文件把 Anthropic Engineering 的《Demystifying evals for AI agents》映射到 Research v1。它不是线上实现说明，而是我们后续设计 Bridge Judge、Leakage Judge、Repair 和 coach review 时采用的评测口径。

## 核心原则

AIChat 不是单次问答模型，而是一个 agent-like tutoring harness。评测时不能只看最后一句回复，还要看系统如何诊断学生状态、如何生成候选回复、是否检测泄露、是否 repair、最终是否给出合适脚手架，以及这些步骤的延迟和调用成本。

因此，我们评测的是：

```text
agent harness + model + prompt + routing + judge + repair
```

而不是单独评测某一个模型。

## 概念映射

| Anthropic 概念 | 我们项目中的对应物 |
|---|---|
| Task | 一个学生 turn：学生消息、题目上下文、近期对话、代码片段、期望成功标准 |
| Trial | 某个系统版本在一个 task 上的一次运行 |
| Transcript / trace | Bridge Judge、Tutor candidate、Leakage Judge、Repair、final response、latency、LLM call count 的完整记录 |
| Outcome | 学生最终看到的 `final_response_text` 以及它是否适配卡点、是否泄露关键桥 |
| Grader | deterministic checks、LLM Judge、coach reference label |
| Eval harness | `run_bridge_offline_eval.py`、response review workbook、summary scripts、report docs |
| Agent harness | 线上或离线 AIChat 控制链路：rules、Bridge Contract、Tutor、Guard、Repair |
| Eval suite | 20/50 seed、regression cases、repair stress set、真实 shadow logs |

## Task 应该怎么写

每个 task 必须明确成功条件。不要只存学生一句话。

推荐结构：

```json
{
  "task_id": "cp_bridge_010",
  "student_message": "01 背包为什么容量要倒着枚举？正着枚举不是也能更新吗？",
  "problem_context": "每个物品只能选一次。",
  "recent_dialogue": "",
  "success_criteria": [
    "识别 missing bridge 是 ordering_dependency_bridge / enumeration_order",
    "不直接说穿完整倒序原因或完整循环模板",
    "给 bridge-oriented micro-example",
    "让学生观察并说出同一物品是否被重复使用"
  ],
  "forbidden_content": [
    "不能直接给完整循环模板",
    "不能直接完整解释正序会重复使用当前物品"
  ]
}
```

如果两个教练看完 task 不能独立判断什么算好回复，说明 task 太模糊，需要先修 task，而不是修模型。

## Grader 分层

### 1. Deterministic Grader

能规则判断的先用规则，不要交给 LLM Judge。

适合规则判的维度：

- JSON schema 是否有效；
- `selected_focus_id` 是否存在于 registry；
- `primary_bridge_subtype_id` 是否属于对应 family；
- final response 是否为空；
- latency 是否超过预算；
- LLM call count；
- 是否触发 repair；
- output file / labels 是否可解析。

规则 grader 的优点是便宜、稳定、可复现。缺点是无法判断开放式教学质量。

### 2. LLM Judge

LLM Judge 只用于开放式、语义型维度。

适合 LLM Judge 的维度：

- 是否识别了学生当前 missing bridge；
- 回复是否抓住当前卡点；
- scaffold level 是否过强或过弱；
- micro-example 是否 bridge-oriented；
- 是否 critical bridge leakage；
- repair 是否保留教学意图且删除泄露内容。

LLM Judge 不应一次评所有维度。复杂评分要拆成小 judge 或小 rubric：

```text
Bridge Judge: 只诊断 missing bridge
Leakage Judge: 只判断候选回复是否泄露
Response Judge: 只判断教学质量
Repair Judge / Review: 只判断 repair 后是否仍泄露或变差
```

### 3. Coach Reference

教练标注是 expert reference，不是绝对真理。

Research v1 的说法应该是：

```text
coach reference label
adjudicated reference
```

不要写：

```text
ground truth
唯一正确答案
```

主实验至少应包含：

- 单教练完整标注；
- 20%-30% 双教练复标；
- 分歧统计；
- 裁决后的 adjudicated reference；
- 低置信样本单独标记。

## Capability Eval 与 Regression Eval

### Capability Eval

用于回答“系统能不能做到这件事”。

例子：

- Bridge Judge 能否识别 missing bridge？
- Bridge Contract 是否提升 scaffold appropriateness？
- Leakage Judge 是否降低 critical bridge leakage？
- Repair 是否在不伤害教学质量的前提下降低泄露？

Capability eval 不需要一开始就 100% 通过。它应该包含当前系统还做不好的样本，给系统一个可爬的坡。

### Regression Eval

用于回答“系统是否仍然能处理以前会处理的 case”。

例子：

- `cp_bridge_010`：不能继续用“请给题号/代码行”兜底；
- `cp_bridge_003`：不能直接给 `dp[t]` 的完整语义；
- `cp_bridge_008`：不能直接解释完整二分边界规则；
- `cp_bridge_017`：不能忽略学生已经明确表达的并查集合并卡点。

Regression eval 应接近 100% 通过。每次 prompt、rubric、registry、router 或 repair prompt 改动后都应跑。

## 多次 Trial 与稳定性

单次通过不代表系统稳定。Agent 输出有随机性，因此需要区分：

```text
pass@k: k 次里至少一次成功
pass^k: k 次都成功
```

对学生在线 AIChat，更重要的是 `pass^k`。学生不会因为系统“三次里一次很好”就觉得体验可靠。

建议 Research v1 增加：

```text
pass^3_no_critical_leakage
pass^3_scaffold_appropriate
pass^3_valid_contract
```

含义是同一 case 跑 3 次，每次都不泄露、脚手架都不过强、contract 都有效。

## 我们的评测层级

### Layer 1: Diagnosis Eval

评 Bridge Judge / compact contract。

指标：

- student state agreement；
- bridge family agreement；
- registered focus agreement；
- help level agreement；
- invalid label rate；
- focus out-of-registry rate；
- latency。

### Layer 2: Tutor Response Eval

评 final response。

指标：

- bridge identification score；
- groundedness；
- scaffold appropriateness；
- next-step clarity；
- single-focus coherence；
- bridge-oriented micro-example score；
- coach preference rank。

### Layer 3: Leakage Eval

评 candidate 或 final response 是否泄露。

指标：

- any leakage rate；
- critical bridge leakage rate；
- answer/code leakage rate；
- false positive rewrite rate；
- false negative leakage rate。

### Layer 4: Repair Eval

评 repair 是否有用。

指标：

- repair applied count；
- repaired wins / ties / losses；
- repaired major leakage rate；
- repair still-leaks rate；
- repair quality delta；
- latency added by repair。

### Layer 5: Product Viability Eval

评能不能上线。

指标：

- p50 latency；
- p95 latency；
- LLM call count；
- token cost；
- stage error rate；
- timeout rate；
- fallback rate。

## Prompt 改进与架构改进如何区分

如果修改 prompt 后效果变好，不能直接证明架构有效，也不能直接证明架构无效。

正确做法：

1. 在 dev set 上调 prompt；
2. 记录 prompt patch log；
3. 冻结 prompt 版本；
4. 在 held-out test set 上比较不同架构；
5. 同时报告质量、泄露和延迟。

论文应避免：

```text
多层 LLM 天然更好。
```

更严谨的说法：

```text
We evaluate whether bridge contracts, leakage guards, and repair loops provide additional stability and leakage control beyond prompt-tuned single-LLM baselines.
```

## 最小实验矩阵

| 系统 | 目的 |
|---|---|
| current_system | 当前线上 baseline |
| single_llm_structured | 检验单 LLM 是否已经足够 |
| bridge_contract | 检验 explicit missing bridge contract 是否提升脚手架 |
| bridge_contract + guard | 检验 post-generation leakage detection |
| bridge_contract + guard + repair | 检验泄露修复是否保留教学质量 |
| risk_triggered_simulation | 检验质量/泄露/延迟权衡 |

## Research v1 下一步

1. 完成 Repair 前后 8 条盲评，并生成中英文 before/after 报告。
2. 冻结当前 prompt 为 `prompt_v1.0-dev`。
3. 把 20 条 seed 拆成 dev/regression 用途，另建 50 条 test seed。
4. 为每个 task 补 `success_criteria` 和 `forbidden_content`。
5. 跑 `pass^3` 小实验，观察稳定性而不是单次好坏。
6. 用 coach reference 校准 LLM Judge，不把 LLM Judge 当最终真理。
