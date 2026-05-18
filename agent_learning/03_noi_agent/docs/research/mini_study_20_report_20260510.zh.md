# 20 条 Seed Mini-Study 初步报告

日期：2026-05-10

## 目的

这次 mini-study 用同一批 20 条教练参考 seed，对比 5 条离线路径：

1. `current_system`：当前 AIChat，只跑学生可见 tutor，不跑 Bridge Judge。
2. `single_llm_structured`：一次 LLM 调用同时输出 compact contract、学生回复和 self-check。
3. `bridge_contract`：Bridge Judge 诊断后，将 contract 注入 tutor。
4. `bridge_contract + guard`：在 Bridge Contract Tutor 后增加 Leakage Judge。
5. `bridge_contract + guard + repair`：在 guard 后允许 rewrite/block 时触发 Repair。

这不是最终论文实验，而是 Research v1 的第一版完整闭环：用于检查 baseline 能否跑通、延迟是否可接受、哪些模块值得继续扩样本。

## 运行设置

- Seed：`docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Tutor provider：`deepseek_flash`
- Chat thinking：`disabled`
- Judge schema：`retrieval_augmented_compact_judge`
- Guard mode：`predicted`
- Bridge/guard/repair 路径使用 `--max-retries 1`，个别 timeout case 单独重跑并合并。

## 结果摘要

| 路径 | 完成数 | Bridge family acc. | Focus acc. | Help level acc. | Leakage rate | Rewrite rate | 平均调用 | p50 延迟 | p95 延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current_system | 20/20 | n/a | n/a | n/a | n/a | n/a | 1.00 | 7631.893 ms | 11015.386 ms |
| single_llm_structured | 20/20 | 0.900 | 0.800 | 0.900 | n/a | n/a | 1.00 | 7159.394 ms | 8843.530 ms |
| bridge_contract | 20/20 | 0.900 | 0.850 | 0.950 | n/a | n/a | 2.10 | 13691.467 ms | 18664.726 ms |
| bridge_contract + guard | 20/20 | 0.900 | 0.800 | 0.850 | 0.150 | 0.050 | 3.35 | 18157.722 ms | 22471.240 ms |
| bridge_contract + guard + repair | 20/20 | 0.900 | 0.800 | 0.950 | 0.050 | 0.000 | 3.35 | 17094.474 ms | 23998.282 ms |

## 初步解读

`single_llm_structured` 很重要。它只用一次 LLM 调用，延迟和 current_system 接近，同时在 20 条 seed 上达到了 0.90 的 bridge family accuracy 和 0.80 的 focus accuracy。这说明“单 LLM 结构化输出”是必须保留的强 baseline。

`bridge_contract` 诊断指标略强于 single-LLM，尤其 focus accuracy 从 0.80 到 0.85，help level 从 0.90 到 0.95。但代价也明显：平均调用从 1.0 到 2.1，p50 延迟从约 7 秒到约 13.7 秒。

`guard` 路径显示了后置 Leakage Judge 的成本：平均调用约 3.35，p50 延迟约 18 秒。当前 20 条 seed 中没有 critical bridge leakage 或 answer/code leakage，只有轻微泄露和 1 个 rewrite 建议。这说明 guard 不应默认每轮线上执行，更适合高风险触发或 shadow mode。

`repair` 这批数据几乎没有触发。full pipeline 的 repair rate 为 0，说明当前 seed 或 tutor 输出中 rewrite/block 不够多，暂时不能证明 Repair 有效。下一步如果要验证 Repair，需要构造更强的 leakage adversarial cases，或者使用 coach response review 找出实际过强回复。

## 盲评产物

已生成匿名中文盲评表：

- `docs/research/coach_response_review_workbook_mini_study_20_20260510.zh.xlsx`
- key 文件：`docs/research/coach_response_review_workbook_mini_study_20_20260510.key.csv`

盲评表包含 100 条回复，也就是 20 个 case × 5 个系统路径。表中隐藏了系统来源，需要教练只看学生问题、上下文和 AI 回复来评分。

新增评分项：

- `桥梁导向微型例子 0-2`

这个维度用于区分：

- 低质量 micro-example：只是让学生完成一次临时小任务；
- 高质量 bridge-oriented micro-example：通过例子让学生提炼可迁移的概念关系。

## 下一步

1. 你可以先盲评 20-30 条，不必一次评完 100 条。
2. 我们用 key 文件汇总不同系统路径的教练评分。
3. 根据盲评结果判断：`single_llm_structured` 是否已经足够强，`bridge_contract` 是否值得额外延迟，`guard/repair` 是否只应在高风险路由触发。
