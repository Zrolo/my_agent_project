# LLM Judge Calibration Protocol v1

本协议用于校准 Research v1 中的 LLM Judge / Offline Grader。核心原则是：LLM Judge 可以帮助评估开放式语义维度，但不能被当成最终真理，也不能和系统运行时组件混用。

## 目标

1. 区分 runtime judge 和 offline grader。
2. 明确哪些维度用 deterministic checks，哪些维度用 LLM Judge。
3. 用 coach reference 校准 LLM Judge。
4. 支持 `UNKNOWN` / `INSUFFICIENT_CONTEXT`，避免强行猜测。
5. 在 held-out test 前冻结 judge prompt。

## 术语

| 名称 | 用途 | 是否参与生成学生回复 | 是否作为论文评分工具 |
|---|---|---:|---:|
| Runtime Bridge Diagnoser | 在线或离线系统内诊断 missing bridge，生成 compact contract | 可能 | 否 |
| Runtime Leakage Guard | 系统内检测候选回复是否泄露，决定 pass/rewrite/block | 可能 | 否 |
| Offline Bridge Grader | 实验后评估系统是否诊断对 missing bridge | 否 | 是 |
| Offline Leakage Grader | 实验后评估 final/candidate response 是否泄露 | 否 | 是 |
| Offline Response Grader | 实验后评估教学质量 | 否 | 是 |
| Offline Repair Grader | 实验后评估 repair 是否降低泄露且保留教学意图 | 否 | 是 |
| Coach Reference | 教练标注或裁决后的 expert reference | 否 | 校准与最终解释基准 |

论文中应避免笼统写 “Judge”。建议写清楚是 runtime diagnoser/guard 还是 offline grader。

## Grader 分层

### Deterministic Checks

以下内容优先用规则或脚本：

- JSON 是否可解析；
- required fields 是否存在；
- enum 是否合法；
- selected focus 是否在 registry；
- subtype 是否属于 family；
- response 是否为空；
- latency / LLM call count；
- repair 是否触发；
- final response source 是否合法；
- output file 是否可读。

### LLM Grader

以下内容可用 LLM Grader，但必须校准：

- missing bridge 是否被识别；
- scaffold 是否贴合当前卡点；
- micro-example 是否 bridge-oriented；
- 是否 critical bridge leakage；
- repair 是否删除泄露内容；
- final response 是否有清晰 next-step action。

LLM Grader 不应一次评价所有维度。优先拆成：

```text
Offline Bridge Grader
Offline Leakage Grader
Offline Response Grader
Offline Repair Grader
```

## 输出标签

所有 LLM Grader 都应支持：

```text
PASS
PARTIAL
FAIL
UNKNOWN
INSUFFICIENT_CONTEXT
```

要求：

- `UNKNOWN` 不算正确；
- `UNKNOWN` 也不算系统失败；
- 单独报告 `unknown_rate`；
- 如果上下文不足，优先输出 `INSUFFICIENT_CONTEXT`，不要编造学生卡点。

## 校准数据

| Split | 用途 |
|---|---|
| 20 old seeds | dev / regression；允许调 judge prompt |
| 50 held-out seeds | 主实验；judge prompt freeze 后评估 |
| 20-30 repair stress cases | Repair 和 Leakage Grader stress test |
| partial double-annotated subset | 校准教练一致性和 grader 上限 |

20 old seeds 已经被用于 pilot 和 prompt tuning，因此不能再作为正式 held-out 结果。

## 校准流程

1. 选定 grader 维度，例如 critical bridge leakage。
2. 写清 rubric 和 label definitions。
3. 用 dev/regression set 调整 grader prompt。
4. 在 `judge_prompt_patch_log.md` 记录每次修改。
5. 冻结 grader prompt，例如 `offline_leakage_grader_prompt_v1.0-dev`。
6. 在 held-out test 上运行 grader。
7. 与 coach reference / adjudicated reference 比较。
8. 报告指标和 error analysis。
9. held-out 之后发现的问题只能进入下一版 prompt，不得回头改当前主结果。

## 指标

### Bridge Grader

- bridge family accuracy；
- bridge family macro-F1；
- relaxed missing-bridge agreement；
- registered focus accuracy；
- UNKNOWN rate；
- invalid label rate。

### Leakage Grader

- critical leakage precision；
- critical leakage recall；
- critical leakage F1；
- false negative critical leakage rate；
- false positive leakage rate；
- answer/code leakage recall；
- ordinal leakage severity MAE；
- UNKNOWN rate。

对本项目最危险的是：

```text
false negative critical leakage
```

也就是系统已经说穿关键桥，但 grader 放过了。

### Response Grader

- correlation / agreement with coach quality bands；
- scaffold appropriateness agreement；
- next-step clarity agreement；
- bridge-oriented micro-example agreement；
- preference agreement。

### Repair Grader

- before/after leakage severity delta；
- repair still-leaks rate；
- repair degrades quality rate；
- repair preserves teaching intent rate；
- UNKNOWN rate。

## 报告格式

每个 judge validation report 至少包含：

- grader name and version；
- prompt version；
- model provider and model；
- calibration split；
- coach reference source；
- number of cases；
- UNKNOWN handling；
- metrics table；
- confusion matrix where applicable；
- false positive examples；
- false negative examples；
- rubric limitations；
- whether the grader is acceptable for headline metrics or only for exploratory analysis。

## 论文写法

推荐表述：

```text
We use LLM graders for open-ended semantic dimensions and calibrate them against coach references. LLM graders are not treated as ground truth. We report unknown rates, false positives, and false negatives, especially for critical bridge leakage.
```

中文：

```text
我们将 LLM Grader 用于开放式语义维度，并通过教练 reference 校准。LLM Grader 不被视为真值；我们报告 UNKNOWN rate、误报和漏报，尤其关注 critical bridge leakage 的漏检。
```

避免表述：

```text
LLM Judge 证明系统没有泄露。
LLM Judge 就是 gold label。
系统自己的 runtime guard 同时作为最终评分器。
```

## Research v1 接受标准

在正式主实验前，至少应完成：

1. Offline Leakage Grader 的 dev calibration。
2. Offline Response Grader 的 rubric freeze。
3. Runtime Guard 与 Offline Grader 的命名和 prompt 分离。
4. Judge prompt patch log。
5. UNKNOWN / INSUFFICIENT_CONTEXT 的统一处理。
