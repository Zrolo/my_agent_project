# 10-case Dev Ablation Static Lint 复分析（2026-05-12）

本报告是开发阶段复分析，不是正式 held-out 结果。目的：在已有 `dev_ablation_20260512_safe_scaffold_limit10` 输出上回填 static leakage risk lint，比较自动 Guard 标签和可解释静态风险信号之间的差异。

## 输入与输出

输入：

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation.jsonl
```

复分析输出：

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_static_lint_summary.json
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_static_lint_summary.md
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_static_lint_summary.zh.md
```

说明：这批 JSONL 生成于 static lint 字段加入之前。summary 脚本现在会从 `candidate_response_text` / `final_response_text` 临时回填：

```text
candidate_static_leakage_risk_lint
final_static_leakage_risk_lint
```

这些字段只作为诊断信号，不是教练 gold，也不会修改最终回复。

## 总体结果

| metric | value |
| --- | ---: |
| rows | 120 |
| automatic leakage rate | 0.150 |
| automatic critical bridge leakage rate | 0.075 |
| final static risk rate | 0.521 |
| final answer-slot risk rate | 0.118 |
| final filled-trace risk rate | 0.378 |
| final worked-example risk rate | 0.176 |

核心信号：

```text
自动 Guard 抓到的 critical bridge leakage 很少，
但超过一半最终回复含有静态高风险模式。
```

这不等于超过一半都是 major leakage；static lint 是高召回、低精度的诊断信号。但它说明后续教练盲评和 Judge calibration 需要特别检查这些位置。

## 分组结果

| condition | final static risk | answer-slot | filled-trace | worked-example | automatic critical leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| `bridge_contract_safe_scaffold` | 0.100 | 0.000 | 0.100 | 0.000 | n/a |
| `socratic_no_answer_clean` | 0.400 | 0.100 | 0.300 | 0.100 | n/a |
| `dbox_inspired_guard` | 0.444 | 0.111 | 0.222 | 0.111 | 0.100 |
| `dbox_inspired_clean` | 0.500 | 0.100 | 0.400 | 0.100 | n/a |
| `single_llm_structured_clean` | 0.500 | 0.100 | 0.400 | 0.100 | n/a |
| `single_llm_structured_guard` | 0.500 | 0.100 | 0.400 | 0.100 | 0.000 |
| `bridge_contract_clean` | 0.600 | 0.200 | 0.400 | 0.300 | n/a |
| `bridge_contract_guard` | 0.600 | 0.100 | 0.400 | 0.400 | 0.100 |
| `enhanced_prompt_only_clean` | 0.600 | 0.200 | 0.500 | 0.100 | n/a |
| `codehelp_codeaid_clean` | 0.600 | 0.000 | 0.400 | 0.400 | n/a |
| `bridge_inspired_expert_decision_clean` | 0.700 | 0.100 | 0.500 | 0.200 | n/a |
| `bridge_contract_guard_repair` | 0.700 | 0.300 | 0.500 | 0.200 | 0.100 |

## 解释

1. `bridge_contract_safe_scaffold` 的 static risk 最低。这符合预期，因为它是 deterministic L1 safe scaffold，不是主方法，只能作为高风险 appendix / fallback 条件。
2. `bridge_contract_guard_repair` 的 static risk 最高之一，说明 Repair 并没有稳定减少答案槽位、已填 trace 或完整微例风险。
3. `single_llm_structured_guard` 自动 critical leakage 为 0，但 static risk 仍为 0.5，说明自动 Guard 可能漏掉一些形式风险。
4. `dbox_inspired_guard` 的 static risk 低于 `dbox_inspired_clean`，但仍有 0.444；Guard 有帮助但不彻底。

## 对论文和实验设计的影响

这次复分析支持一个更稳的评价框架：

```text
coach label = reference / adjudicated label
LLM Guard = runtime detector under calibration
static lint = interpretable risk signal
```

正式 50-case held-out 中不应只报告 LLM Guard 的 leakage rate。建议同时报告：

1. 教练 leakage label；
2. 自动 Guard label；
3. static risk lint；
4. Guard false negative / false positive；
5. static lint 与教练 major leakage 的 overlap。

## 下一步

1. 把 static lint 字段保留在所有 dev/held-out result rows。
2. 在盲评分析脚本中加入 static lint 与教练标签的交叉表。
3. 不再继续无限堆 Guard prompt；下一步重点是校准 Guard recall 与解释 false negative。
4. 50-case held-out 前冻结 prompt / rubric，并保留 static lint 作为诊断而非裁决。
