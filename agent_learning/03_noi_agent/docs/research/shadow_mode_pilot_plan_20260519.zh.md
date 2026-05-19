# Shadow Mode Pilot Plan v1

## 使用边界

本文档只设计一个 shadow mode pilot，用于补充 CP-MissingBridgeBench 的生态效度与部署前风险评估。Shadow mode 不接入线上 active mode，不修改线上 AIChat，不改变学生可见回复，不上线 Bridge Judge / Leakage Judge / Repair，不新增 dialogue-state v3 主实验 condition，不重算 dialogue-state v3 主表。

Shadow mode 的核心原则是：所有 judge / rewrite / block 信号只在后台记录，不进入学生可见 `final_response`，不触发实时拦截或改写。

## 目标

Shadow mode pilot 用于回答以下工程与教育技术问题：

1. Bridge Judge 与 Leakage Judge 在真实学生 dialogue-state cases 上是否能稳定识别潜在 bridge leakage 风险。
2. `would_rewrite` 与 `would_block` 信号在真实对话中是否过于敏感或过于迟钝。
3. 后台 judge 的 latency 是否可能影响未来部署。
4. 多个 judge 信号之间是否存在高 disagreement，需要教练复核。
5. 教练抽样复核是否支持继续进入更小范围、risk-triggered 的 active 设计讨论。

## 非目标

Shadow mode pilot 不做以下事情：

- 不改变学生可见回复。
- 不上线 Repair。
- 不上线 Bridge Judge / Leakage Judge 作为实时干预。
- 不新增主实验 baseline 或 condition。
- 不评估长期学习效果。
- 不证明线上系统有效。
- 不修改 dialogue-state v3 evidence package 或主结果表。

## Shadow Mode 流程

1. 学生与现有系统或教练工作流正常互动。
2. 系统记录经过隐私审查允许的脱敏 dialogue-state case。
3. 后台异步运行 Bridge Judge 与 Leakage Judge。
4. 后台只记录以下 shadow signals：
   - `bridge_judge_label`
   - `leakage_judge_label`
   - `would_rewrite`
   - `would_block`
   - `judge_latency_ms`
   - `judge_disagreement`
5. 学生可见 `final_response` 保持不变。
6. 教练对抽样 cases 进行人工复核，判断 judge 信号是否合理。

## 建议记录字段

| field | role |
| --- | --- |
| `pilot_case_id` | shadow pilot 内部匿名 case 编号 |
| `student_id_hash` | 学生匿名 hash |
| `problem_id_hash` | 题目匿名 hash |
| `final_response_unchanged` | 固定为 true，表示学生可见回复未被 shadow 改写 |
| `bridge_judge_label` | 后台 Bridge Judge 输出 |
| `leakage_judge_label` | 后台 Leakage Judge 输出 |
| `would_rewrite` | 如果 active，是否会建议改写；shadow 中只记录 |
| `would_block` | 如果 active，是否会建议阻断；shadow 中只记录 |
| `judge_latency_ms` | judge 后台耗时 |
| `judge_disagreement` | 多 judge 或 judge-human 是否不一致 |
| `coach_sample_review_status` | 教练抽样复核状态 |
| `coach_review_note` | 教练对 shadow signal 的解释 |
| `privacy_review_status` | 隐私审查状态 |

## Latency 记录

Shadow mode 应记录 judge latency，但不把 latency 用于实时学生交互。建议至少记录：

- total judge latency；
- Bridge Judge latency；
- Leakage Judge latency；
- timeout / failure；
- 是否需要异步队列或批处理。

Latency 只用于判断未来部署可行性，不作为主实验结果。

## Judge Disagreement 记录

Judge disagreement 至少包括：

- Bridge Judge 与 Leakage Judge 判断不一致；
- `would_rewrite=true` 但 `would_block=false`；
- judge 认为高风险但教练抽样复核认为可接受；
- judge 认为低风险但教练抽样复核认为存在 major bridge leakage / answer leakage 风险。

Disagreement 只用于 shadow-mode 风险分析，不自动改变学生可见回复。

## 教练抽样复核

建议从 shadow logs 中抽样复核：

1. judge 高风险 cases；
2. judge disagreement cases；
3. high-latency cases；
4. 低风险随机样本；
5. 真实学生直接要答案/代码的 cases。

教练复核目标是判断 judge signals 是否适合进入下一阶段设计讨论，不是给现有主实验新增标注。

## 从 Shadow 到 Active 的门槛

只有 shadow mode 通过后，才考虑 active mode。进入 active 讨论前，至少需要：

1. 隐私与知情说明流程稳定。
2. `final_response_unchanged=true` 的 shadow logs 完整可审计。
3. Judge latency 不会明显影响实时交互。
4. Judge disagreement 可被教练复核解释。
5. 高风险误判和漏判有明确处理策略。
6. 教练同意只讨论 risk-triggered active，而不是 every-turn full multi-judge active。

## Active Mode 未来边界

若未来讨论 active mode，也必须遵守：

- active 只能 risk-triggered；
- 不能 every turn 都运行 full multi-judge；
- 不能默认改写所有回复；
- 不能将 Repair 直接上线为无人工复核的学生可见改写；
- 不能把 shadow pilot 写成 active deployment validation；
- 不能用 shadow pilot 修改 dialogue-state v3 主实验数字。

## 报告边界

Shadow mode pilot 报告必须写成：

```text
This shadow-mode pilot records backend judge signals without changing student-visible responses. It is used to evaluate ecological validity, latency, and disagreement risks before any active-mode discussion. It does not modify the dialogue-state v3 main experiment, does not add new baselines, and does not evaluate long-term learning outcomes.
```

禁止写法：

- 不能说 shadow mode 已上线 active mode。
- 不能说 Bridge Judge / Leakage Judge 已参与学生可见回复。
- 不能说 Repair 已修复学生最终回复。
- 不能把 shadow logs 合并为 dialogue-state v3 主实验 condition。
- 不能把 shadow mode 写成学习效果实验。
