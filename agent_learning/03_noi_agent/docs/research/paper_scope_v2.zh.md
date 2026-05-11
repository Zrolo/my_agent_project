# Paper Scope v2

本文件用于冻结当前论文主线，防止 Research v1 继续被新模块、新理论和线上功能扩展拉散。它描述的是论文范围，不表示所有能力已经接入线上学生 AIChat。

## 一句话定位

```text
CP-MissingBridgeBench 是一篇算法竞赛 LLM 辅导的 AI+教育评测框架论文。
```

论文中心不是“我们做了一个复杂多 Agent 系统”，而是：

```text
我们提出 missing bridge 作为算法竞赛辅导中的逐轮卡点表示；
我们提出 critical bridge leakage 作为传统答案泄露之外的教学失败类型；
我们构建 coach-reference-based offline evaluation workflow；
我们公平比较 current AIChat、strong single-LLM baseline、Bridge Contract、Guard、Repair 在质量、泄露和成本上的权衡。
```

## 四条范围锁

1. 这篇论文是 evaluation framework paper，不是完整线上系统论文。
2. 核心构念是 `missing bridge`，不是算法标签本身。
3. 核心风险指标是 `critical bridge leakage`，不是只有完整代码/完整题解泄露。
4. Bridge Judge、Leakage Guard、Repair 和 risk routing 是 ablation conditions，不是论文唯一主贡献。

## 推荐题目

英文：

```text
CP-MissingBridgeBench:
Turn-level Missing-Bridge Diagnosis and Critical-Bridge Leakage Evaluation
for LLM Tutors in Competitive Programming
```

中文：

```text
CP-MissingBridgeBench：
面向算法竞赛 LLM 辅导的逐轮缺失桥梁诊断与关键桥梁泄露评测框架
```

## 研究问题

### RQ1: Missing Bridge Diagnosis

`missing bridge schema` 是否能支持逐轮诊断？

要回答的问题：

- 给定学生当前 turn、题目上下文和近期对话，教练能否标出学生当前缺失的关键推理桥？
- runtime diagnoser / offline grader 是否能接近 coach reference？
- 这些标签是否比单纯算法标签更能解释学生卡点？

主要证据：

- coach reference labels；
- partial double annotation；
- agreement / adjudication；
- Bridge diagnosis accuracy / macro-F1 / invalid-label rate；
- UNKNOWN / low-confidence rate。

### RQ2: Critical Bridge Leakage

`critical bridge leakage` 是否能捕捉传统 answer leakage 看不到的过度帮助？

要回答的问题：

- LLM 没给完整代码或完整题解，但直接说穿状态定义、转移、check 条件、边界更新或贪心依据时，是否应视为教学失败？
- coach 能否稳定区分 minor / major / answer-level leakage？
- offline leakage grader 能否识别 critical bridge leakage？

主要证据：

- coach leakage label；
- critical leakage precision / recall / F1；
- false negative critical leakage rate；
- response blind review examples；
- repair stress test。

### RQ3: Harness Trade-off

Bridge Contract / Guard / Repair 是否在 strong single-LLM baseline 之外提供额外价值？

要回答的问题：

- strong `single_llm_structured` baseline 是否已经足够强？
- Bridge Contract 是否提升脚手架贴合度或可解释控制？
- Guard 是否降低 critical bridge leakage？
- Repair 是否降低泄露且不明显损害教学质量？
- risk-triggered routing 是否在接近 full multi-judge 安全性的同时降低延迟和调用成本？

主要证据：

- current_system vs single_llm_structured vs bridge_contract；
- single_llm_structured + guard / repair；
- bridge_contract + guard / repair；
- latency p50 / p95；
- LLM call count；
- coach quality score；
- repair before/after review。

## 主实验矩阵

| System | 目的 |
|---|---|
| `current_system` | 当前线上 AIChat baseline |
| `single_llm_structured` | 检验一个结构化 LLM 调用是否已经足够 |
| `single_llm_structured + guard` | 检验 Guard 的收益是否不依赖 Bridge Contract |
| `single_llm_structured + guard + repair` | 检验 Repair 是否也能增强 strong single-LLM baseline |
| `bridge_contract` | 检验 explicit missing bridge contract 是否改善脚手架 |
| `bridge_contract + guard` | 检验 post-generation leakage detection |
| `bridge_contract + guard + repair` | 检验泄露修复是否保留教学质量 |
| `risk_triggered_simulation` | 检验质量、泄露和延迟的部署权衡 |

## 数据划分

| Split | 用途 | 状态 |
|---|---|---|
| 20 old seeds | dev / regression；允许 prompt tuning | 已用于 pilot，不再作为正式 test |
| 50 held-out seeds | 主实验 test；prompt freeze 后只跑主结果 | 待构建 |
| 20-30 repair stress cases | 专门测试 Repair 是否能降低高泄露 candidate | 已有 12-case smoke；正式实验仍需扩展和 before/after 盲评 |
| shadow logs | 未来真实学生数据，只做线上前观察 | 待设计/待实现 |

## Prompt 与 Judge Freeze

Prompt design 是 harness 的一部分，不应假装不存在。论文中应明确：

- prompt 只在 dev/regression set 上调；
- 每次修改进入 `prompt_patch_log.md` 或 `judge_prompt_patch_log.md`；
- tutor、bridge diagnoser、leakage guard、repair、offline graders 都需要版本号；
- held-out test 前冻结 prompt；
- test 后发现的问题进入 error analysis，不回头改主结果。

## 可以声称

- 提出 CP-specific missing bridge schema。
- 提出 critical bridge leakage 作为算法竞赛辅导的重要评测维度。
- 构建 coach-reference-based offline evaluation workflow。
- 比较 current system、strong single-LLM baseline、Bridge Contract、Guard、Repair。
- 发现 strong single-LLM baseline 很强，多模块机制的价值需要通过泄露控制、稳定性、解释性和高风险场景进一步验证。

## 不应声称

- 多层 LLM 天然优于单 LLM。
- LLM Judge 是最终真理。
- 单教练标签是唯一正确答案。
- Repair 已经被自然样本充分证明有效。
- 当前线上 AIChat 已经完整实现 Bridge-aware Tutor。
- risk-triggered routing 已经是成熟线上系统贡献。

## 投稿定位

当前最稳定位是 AI+教育评测框架论文。近期路线：

```text
Research v0.3 / Pilot
-> Research v1: 50-case held-out + partial double annotation + judge validation + fair ablation
-> Journal or conference submission
```

更长期的真实学生学习收益、长期画像、线上 risk-triggered active mode 应留给后续系统论文。
