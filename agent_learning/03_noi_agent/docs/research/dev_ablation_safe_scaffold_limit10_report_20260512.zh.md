# Dev Ablation 10-case + Safe Scaffold Report 20260512

中文报告。英文版见 [dev_ablation_safe_scaffold_limit10_report_20260512.md](dev_ablation_safe_scaffold_limit10_report_20260512.md)。

## 状态

本报告是 Research v1 的 **P1 development ablation**，不是最终 held-out 论文结果。

这次运行在 2026-05-11 的 10-case dev ablation 基础上，显式加入一个 appendix / stress 条件：

```text
bridge_contract_safe_scaffold
```

它对应：

```text
tutor_mode=bridge_contract
pipeline_mode=deterministic_safe_scaffold
```

该条件只用于离线研究对照，不接入线上学生 AIChat，不进入默认 dev suite，也不应直接作为主表结论。

## 为什么加这个条件

前一轮 prompt abstraction smoke 暴露了一个重要问题：

```text
clean offline Bridge Contract Tutor 已经修掉线上 prompt 污染，
但在高风险 contribution / aggregation bridge 上，
prompt-only Bridge Contract 仍可能通过微型例子把关键桥说穿。
```

所以本次加入 `deterministic_safe_scaffold`，不是为了证明它质量最好，而是为了检验：

1. 当风险很高时，保守安全脚手架能否显著降低调用成本；
2. 它是否能作为 high-risk route 的安全下界；
3. 教练盲评时，它的安全性提升是否伴随明显教学质量下降。

## 命令

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10 \
  --limit 10 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1 \
  --include-safe-scaffold
```

## 输出

- Manifest: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/manifest.json`
- Combined JSONL: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation.jsonl`
- Summary JSON: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_summary.json`
- English summary: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_summary.md`
- Chinese summary: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_summary.zh.md`
- Blind review CSV: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.csv`
- Blind review XLSX: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.zh.xlsx`
- Key CSV, not for blind review: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.key.csv`

## Conditions

本次跑了 10 个 seed case × 12 个条件，共 120 条系统回复：

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
| `bridge_contract_safe_scaffold` | Bridge Judge + deterministic safe scaffold appendix condition |

## Automatic Run Summary

| 指标 | 数值 |
| --- | ---: |
| case count | 10 |
| condition count | 12 |
| combined rows | 120 |
| completed rows | 120 |
| error count | 0 |
| blind review rows | 120 |
| answer/code leakage rate, auto Leakage Judge | 0.000 |
| critical bridge leakage rate, auto Leakage Judge | 0.075 |
| rewrite rate, auto Leakage Judge | 0.100 |
| block rate, auto Leakage Judge | 0.025 |
| repair rate | 0.008 |
| average LLM call count | 1.742 |
| total latency p50 | 17881.903 ms |
| total latency p95 | 47912.565 ms |
| stage error count | 1 leakage_judge |

注意：自动 leakage 指标来自 runtime/offline Leakage Judge，不是教练盲评标签。它只能作为风险追踪信号，不能作为论文 headline 质量结论。

## Per-condition Operational Summary

| condition | 完成 | safe_action/source | repair | avg calls | p50 latency ms | max latency ms |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 10/10 | n/a | 0 | 1.0 | 23317.5 | 47912.6 |
| `socratic_no_answer_clean` | 10/10 | n/a | 0 | 1.1 | 29341.0 | 58060.1 |
| `codehelp_codeaid_clean` | 10/10 | n/a | 0 | 1.0 | 10016.4 | 17475.8 |
| `dbox_inspired_clean` | 10/10 | n/a | 0 | 1.0 | 11060.8 | 16623.9 |
| `dbox_inspired_guard` | 10/10 | block 1, pass 8, unknown 1 | 0 | 3.2 | 23417.9 | 30500.2 |
| `bridge_inspired_expert_decision_clean` | 10/10 | n/a | 0 | 1.0 | 8700.0 | 9672.1 |
| `single_llm_structured_clean` | 10/10 | n/a | 0 | 1.0 | 16201.8 | 25572.6 |
| `single_llm_structured_guard` | 10/10 | pass 10 | 0 | 2.2 | 23936.8 | 41411.3 |
| `bridge_contract_clean` | 10/10 | n/a | 0 | 2.0 | 20841.2 | 47071.1 |
| `bridge_contract_guard` | 10/10 | pass 7, rewrite 3 | 0 | 3.2 | 31865.5 | 53539.6 |
| `bridge_contract_guard_repair` | 10/10 | pass 9, rewrite 1 | 1 | 3.2 | 31949.0 | 60161.4 |
| `bridge_contract_safe_scaffold` | 10/10 | safe_fallback 10 | 0 | 1.0 | 3739.1 | 4899.1 |

## Early Observations

1. **工具链已经稳定生成 120 条盲评回复。**
   Manifest 显示 `combined_row_count=120`，盲评 key 也是 120 条。Safe scaffold 没有被导出器漏掉。

2. **Safe scaffold 明显更快。**
   `bridge_contract_safe_scaffold` 平均只需 1 次 LLM 调用，p50 latency 约 3.7 秒。它只跑 Bridge Judge，然后直接返回确定性安全观察任务。

3. **Safe scaffold 的质量不能由自动摘要判断。**
   它没有经过 Leakage Judge，所以自动 critical bridge leakage rate 是 n/a。它是否“安全但太空泛”，必须由教练盲评判定。

4. **Bridge Contract + Guard / Repair 仍然昂贵。**
   `bridge_contract_guard` 和 `bridge_contract_guard_repair` 平均约 3.2 次 LLM 调用，p50 latency 约 31.9 秒。这进一步说明线上不能默认 full multi-stage every turn。

5. **Guard 的拦截不是 Bridge-only。**
   `dbox_inspired_guard` 出现 block / unknown，`single_llm_structured_guard` 全部 pass，`bridge_contract_guard` 出现 rewrite。这说明 Guard 的作用要跨 generator 比较，不能只作为 Bridge Contract 的附属模块。

6. **Repair 自然触发仍然少。**
   10-case × 12 条件中只有 1 条最终由 repair 输出。Repair 的真实因果价值仍应主要看 repair stress before/after 实验。

## How To Review

教练盲评时打开：

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.zh.xlsx
```

不要给教练看：

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.key.csv
```

key CSV 只用于盲评后把匿名 response id 映射回 system condition。

## 重点盲评比较

本次最值得看的 paired comparison：

- `bridge_contract_safe_scaffold` vs `bridge_contract_clean`
- `bridge_contract_safe_scaffold` vs `bridge_contract_guard`
- `bridge_contract_safe_scaffold` vs `enhanced_prompt_only_clean`
- `bridge_contract_safe_scaffold` vs `dbox_inspired_guard`

判断重点：

```text
安全性是否明显提升？
是否因为太保守导致教学质量下降？
学生是否仍然知道下一步该做什么？
是否适合作为 high-risk fallback，而不是默认 tutor？
```

## Interpretation Boundary

本报告只说明：

```text
safe scaffold appendix condition 已经能进入同一 dev ablation 链路；
它成本明显更低；
它产生了可盲评的学生可见回复；
下一步可以通过教练盲评判断质量-安全权衡。
```

本报告不能说明：

```text
safe scaffold 比 Bridge Contract 更好；
safe scaffold 应该进入正式主表；
automatic Leakage Judge 结果就是最终 gold；
10-case dev set 可以作为最终论文 headline result。
```

## Next Step

1. 让教练填写 `coach_response_review_workbook_dev_ablation.zh.xlsx`。
2. 解析 filled workbook，生成 blind-review JSONL。
3. 按 condition 做 paired analysis，尤其比较 safe scaffold 与 Bridge Contract variants。
4. 根据盲评结果决定：
   - safe scaffold 是否只放 appendix；
   - 是否作为 high-risk routing 的候选策略；
   - 哪些条件进入 50-case held-out 主表。
