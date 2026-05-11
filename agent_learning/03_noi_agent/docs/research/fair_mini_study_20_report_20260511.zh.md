# 20 条公平 mini-study 报告（2026-05-11）

本次实验把 `current_system`、`single_llm_structured`、`bridge_contract`、Guard 和 Repair 放进同一批 20 条 seed 上比较。目标不是证明某个系统已经最终胜出，而是补齐公平消融：Guard/Repair 不只接在 Bridge Contract 后面，也接在 strong single-LLM baseline 后面。

## 实验设置

- 输入集：`docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Tutor provider：`deepseek_flash`
- Judge provider：`deepseek`
- Chat thinking mode：`disabled`
- Judge schema：`retrieval_augmented_compact_judge`
- Guard mode：`predicted`
- 输出目录：`evals/aichat/ad_hoc_runs/fair_mini_study_20_20260511/`
- 合并结果：`combined_fair_mini_study_20.jsonl`
- 摘要：`combined_fair_mini_study_20_summary.json`
- 中文盲评表：`docs/research/coach_response_review_workbook_fair_mini_study_20_20260511.zh.xlsx`

运行过程中，`bridge_contract + guard` 和 `bridge_contract + guard + repair` 首次出现过 DeepSeek API `APITimeoutError` / `APIConnectionError`。这些错误集中在 Bridge Judge 或 Leakage Judge 阶段；重跑并提高 `max_retries` 后，最终 7 组均为 20/20 完成，最终摘要无 stage error。

## 系统矩阵

| 系统 | pipeline | 样本 | 错误 | 桥梁大类准确率 | registered focus 准确率 | LLM 调用均值 | P50 延迟 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| current_system | tutor_only_no_diagnosis | 20 | 0 | n/a | n/a | 1.00 | 6.24s |
| single_llm_structured | tutor_only | 20 | 0 | 0.90 | 0.80 | 1.05 | 6.84s |
| single_llm_structured + guard | tutor_plus_guard | 20 | 0 | 0.90 | 0.80 | 2.05 | 12.04s |
| single_llm_structured + guard + repair | tutor_plus_guard_plus_repair | 20 | 0 | 0.90 | 0.80 | 2.15 | 12.01s |
| bridge_contract | tutor_only | 20 | 0 | 0.90 | 0.80 | 2.00 | 13.85s |
| bridge_contract + guard | tutor_plus_guard | 20 | 0 | 0.90 | 0.80 | 3.40 | 21.73s |
| bridge_contract + guard + repair | tutor_plus_guard_plus_repair | 20 | 0 | 0.90 | 0.80 | 3.70 | 20.43s |

## Guard / Repair 自动指标

这些指标来自 Leakage Judge，不是教练盲评标签。它们用于定位候选风险，不能直接当成论文最终质量结论。

| 系统 | 泄露率 | 关键桥梁泄露率 | rewrite 率 | repair 率 | P95 延迟 |
| --- | ---: | ---: | ---: | ---: | ---: |
| single_llm_structured + guard | 0.10 | 0.00 | 0.10 | 0.00 | 14.21s |
| single_llm_structured + guard + repair | 0.15 | 0.10 | 0.15 | 0.15 | 15.54s |
| bridge_contract + guard | 0.10 | 0.05 | 0.10 | 0.00 | 31.78s |
| bridge_contract + guard + repair | 0.05 | 0.00 | 0.05 | 0.05 | 36.22s |

## 初步观察

1. `single_llm_structured` 是强基线：在这批 20 条上，它的桥梁大类准确率和 registered focus 准确率与 Bridge Contract 相同，但延迟更低。
2. Bridge Contract 的主要代价是延迟和调用次数：tutor-only 已经约为 single-LLM tutor-only 的 2 倍 P50 延迟；加 Guard/Repair 后 P95 明显上升。
3. Guard/Repair 的价值不能只看自动泄露率。`single_llm + guard + repair` 和 `bridge_contract + guard + repair` 都有 rewrite/repair 触发，但是否真正提高教学质量，必须由 response blind review 判断。
4. 目前最合理的论文说法不是“多层架构一定更好”，而是“我们用同一评测框架比较 strong single-LLM、Bridge Contract、Guard、Repair 在质量、泄露和延迟上的 trade-off”。

## 下一步

1. 让教练盲评 `coach_response_review_workbook_fair_mini_study_20_20260511.zh.xlsx`。
2. 基于盲评结果生成中英文分析报告，重点看：
   - 哪个系统实际回复质量更好；
   - Guard 是否减少关键桥泄露；
   - Repair 是否保留教学质量；
   - Bridge-oriented micro-example 是否比普通 micro-example 更好。
3. 如果 single-LLM 继续明显强，应把它作为论文主 baseline，而不是弱 baseline。

## 当前结论边界

本报告只说明 7 组离线链路已经能完整跑通，并给出自动诊断、Guard 和延迟指标。它还不能证明某个系统在教学质量上优于另一个系统，因为最终回复质量需要教练盲评。
