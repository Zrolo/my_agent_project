# Dev Ablation 10-case Report 20260511

中文报告。英文版见 [dev_ablation_limit10_report_20260511.md](dev_ablation_limit10_report_20260511.md)。

## 状态

本报告是 Research v1 的 **P1 development ablation**，不是最终 held-out 论文结果。

它的目的不是证明某个系统已经最好，而是检查：

1. strong prompt-only baseline 是否足够强；
2. DBox-inspired decomposition baseline 是否能稳定进入同一评测链路；
3. DBox-inspired + Guard 是否能和 Bridge Contract + Guard 公平比较；
4. Bridge Contract / Guard / Repair 的成本和自动 leakage signal 是否值得进入下一步教练盲评。

## 命令

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10 \
  --limit 10 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

## 输出

- Manifest: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/manifest.json`
- Combined JSONL: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/combined_dev_ablation.jsonl`
- Summary JSON: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/combined_dev_ablation_summary.json`
- English summary: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/combined_dev_ablation_summary.md`
- Chinese summary: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/combined_dev_ablation_summary.zh.md`
- Blind review CSV: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/coach_response_review_workbook_dev_ablation.csv`
- Blind review XLSX: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/coach_response_review_workbook_dev_ablation.zh.xlsx`
- Key CSV, not for blind review: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/coach_response_review_workbook_dev_ablation.key.csv`

## Conditions

本次跑了 10 个 seed case × 11 个条件，共 110 条系统回复：

| 条件 | 角色 |
| --- | --- |
| `enhanced_prompt_only_clean` | 强 prompt-only baseline |
| `socratic_no_answer_clean` | Socratic/no-answer 文献启发 baseline |
| `codehelp_codeaid_clean` | no-direct-solution 编程教育 baseline |
| `dbox_inspired_clean` | DBox-inspired decomposition baseline |
| `dbox_inspired_guard` | DBox-inspired + same Leakage Guard |
| `bridge_inspired_expert_decision_clean` | Bridge-inspired expert decision baseline |
| `single_llm_structured_clean` | one-call structured LLM baseline |
| `single_llm_structured_guard` | single LLM + same Leakage Guard |
| `bridge_contract_clean` | Bridge Contract tutor |
| `bridge_contract_guard` | Bridge Contract + Leakage Guard |
| `bridge_contract_guard_repair` | Bridge Contract + Leakage Guard + Repair |

## Automatic Run Summary

| 指标 | 数值 |
| --- | ---: |
| case count | 10 |
| condition count | 11 |
| combined rows | 110 |
| completed rows | 110 |
| stage error count | 0 |
| blind review rows | 110 |
| answer/code leakage rate, auto Leakage Judge | 0.000 |
| critical bridge leakage rate, auto Leakage Judge | 0.075 |
| rewrite rate, auto Leakage Judge | 0.200 |
| repair rate | 0.009 |
| average LLM call count | 1.755 |
| total latency p50 | 21934.524 ms |
| total latency p95 | 50102.215 ms |

注意：自动 leakage 指标来自 runtime/offline Leakage Judge，不是教练盲评标签。它只能作为风险追踪信号，不能作为论文 headline 质量结论。

## Per-condition Operational Summary

| condition | 完成 | safe_action | repair | avg calls | p50 latency ms | max latency ms |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 10/10 | n/a | 0 | 1.0 | 24351.5 | 34538.2 |
| `socratic_no_answer_clean` | 10/10 | n/a | 0 | 1.0 | 26331.0 | 72096.7 |
| `codehelp_codeaid_clean` | 10/10 | n/a | 0 | 1.0 | 10232.7 | 19662.7 |
| `dbox_inspired_clean` | 10/10 | n/a | 0 | 1.0 | 10515.9 | 19597.0 |
| `dbox_inspired_guard` | 10/10 | pass 8, rewrite 2 | 0 | 3.0 | 24993.5 | 33268.6 |
| `bridge_inspired_expert_decision_clean` | 10/10 | n/a | 0 | 1.0 | 10331.7 | 16431.8 |
| `single_llm_structured_clean` | 10/10 | n/a | 0 | 1.0 | 17663.0 | 25848.7 |
| `single_llm_structured_guard` | 10/10 | pass 8, rewrite 2 | 0 | 2.0 | 22654.5 | 27379.5 |
| `bridge_contract_clean` | 10/10 | n/a | 0 | 2.0 | 41629.0 | 52130.1 |
| `bridge_contract_guard` | 10/10 | pass 7, rewrite 3 | 0 | 3.2 | 41360.6 | 84366.8 |
| `bridge_contract_guard_repair` | 10/10 | pass 9, rewrite 1 | 1 | 3.1 | 34845.5 | 65898.9 |

## Early Observations

1. **工具链已经可以进入教练盲评。**
   这次所有 110 条系统回复都生成成功，盲评 XLSX 也有 110 行。

2. **DBox-inspired baseline 现在稳定。**
   上一轮 smoke 暴露出的 status alias 问题已经修复。本次 DBox-inspired clean 和 DBox-inspired + Guard 均 10/10 完成。

3. **DBox-inspired 和 CodeHelp/CodeAid-style 在延迟上明显更轻。**
   它们都是 1-call baseline，p50 latency 约 10 秒左右。它们会是很强的工程 baseline。

4. **Bridge Contract 条件成本明显更高。**
   `bridge_contract_clean` p50 latency 约 41.6 秒；加 Guard 后 p50 仍约 41.4 秒，max latency 达到 84.4 秒。这说明论文必须把 latency/cost 作为一等指标。

5. **Guard 的 rewrite 触发不是 Bridge-only。**
   DBox-inspired + Guard、single-LLM + Guard、Bridge Contract + Guard 都出现 rewrite。这说明 Guard 的价值需要跨 generator 比较，不能只归因于 Bridge Contract。

6. **Repair 自然触发很少。**
   在 10-case dev ablation 中，Repair 只触发 1 次。Repair 的因果效果仍需要单独的 repair stress before/after 实验。

## How To Review

教练盲评时打开：

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/coach_response_review_workbook_dev_ablation.zh.xlsx
```

不要给教练看：

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/coach_response_review_workbook_dev_ablation.key.csv
```

key CSV 只用于盲评后把匿名 response id 映射回 system condition。

## Interpretation Boundary

本报告只说明：

```text
P1 dev ablation 已经能稳定运行；
strong prompt / DBox-inspired / CodeHelp-style / Bridge-inspired / Bridge Contract variants 可以在同一评测链路中比较；
下一步可以进入教练盲评和 paired analysis。
```

本报告不能说明：

```text
Bridge Contract 已经优于 DBox-inspired；
Guard/Repair 已经证明有效；
自动 Leakage Judge 标签就是最终 gold；
10-case dev set 可以作为最终论文 headline result。
```

## Next Step

1. 让教练填写 `coach_response_review_workbook_dev_ablation.zh.xlsx`。
2. 解析 filled workbook，生成 blind-review JSONL。
3. 按 condition 做 paired analysis：
   - `enhanced_prompt_only` vs `bridge_contract_clean`
   - `dbox_inspired_clean` vs `bridge_contract_clean`
   - `dbox_inspired_guard` vs `bridge_contract_guard`
   - `single_llm_structured_guard` vs `bridge_contract_guard`
   - `bridge_contract_guard` vs `bridge_contract_guard_repair`
4. 根据盲评结果决定哪些条件进入 50-case held-out 主表，哪些放 appendix。
