# Bridge Contract Prompt Abstraction Smoke - 2026-05-12

本报告记录一次 dev smoke。它用于检查 prompt 抽象化和 clean offline Bridge Contract Tutor 的工程行为，不作为论文 headline 结果。

## 背景

项目-owner 指出：Repair / Leakage / Tutor prompt 不应把 DP、二分、LCA、lazy 等具体算法逐个列成修复规则，而应抽象成更通用的 bridge shape，例如：

- 表示含义；
- 关系或公式；
- 判定条件；
- 依赖或更新方向；
- 贡献或汇总规则；
- 局部代码槽位；
- 完整微型例子推导过程。

本次 patch 目标是：

1. 将 Leakage Judge、Repair Generator 和离线 generation prompts 从具体算法规则改成抽象泄露形态；
2. 修掉离线 `bridge_contract` 仍然调用线上 `noi_agent_chat()` 的污染问题；
3. 检查 clean offline Bridge Contract Tutor 是否仍会在高风险 bridge 上产生 answer-bearing micro-example。

## 修改范围

本次只影响离线研究链路：

- `docs/common/aichat_leakage_judge_v1_system_prompt.md`
- `docs/common/aichat_repair_response_v1_system_prompt.md`
- `evals/aichat/run_bridge_offline_eval.py`
- `test_bridge_offline_eval_runner_unit.py`
- `test_leakage_judge_v1_unit.py`
- `test_repair_response_v1_unit.py`
- `docs/research/prompt_patch_log.md`
- `docs/research/judge_prompt_patch_log.md`

线上学生 AIChat 未接入这些离线 patch。

## 工程检查

单测命令：

```bash
python3 -m unittest \
  test_bridge_offline_eval_runner_unit.py \
  test_leakage_judge_v1_unit.py \
  test_repair_response_v1_unit.py
```

结果：

```text
Ran 55 tests in 0.009s
OK
```

覆盖的关键检查包括：

- generation prompts 不再依赖具体算法例子作为主要规则；
- DBox / CodeHelp / Socratic / Bridge-inspired baseline 不编码具体 answer-bearing slots；
- Leakage Judge 和 Repair prompt 使用抽象泄露形态；
- offline `bridge_contract` 使用 clean system prompt，不再调用线上 `noi_agent_chat()`；
- clean Bridge Contract prompt 禁止候选答案式标记、完整公式、边界动作、代码行和二选一式关键槽位。

## Smoke 设置

### 11-condition smoke

命令：

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --limit 1 \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260512_prompt_abstraction_smoke1 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

输出：

- `evals/aichat/ad_hoc_runs/dev_ablation_20260512_prompt_abstraction_smoke1/combined_dev_ablation.jsonl`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260512_prompt_abstraction_smoke1/combined_dev_ablation_summary.zh.md`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260512_prompt_abstraction_smoke1/coach_response_review_workbook_dev_ablation.zh.xlsx`

自动摘要显示：

- rows: 11
- completed: 11
- suite-level errors: 0
- stage error: `leakage_judge` timeout 1 次
- total latency p50: 31.1s
- total latency p95: 117.9s

### Bridge Contract targeted reruns

目标 case：

```text
cp_bridge_001
学生：我知道要 LCA，但不知道每条路径到底在哪里加减标记。
```

输出目录：

```text
evals/aichat/ad_hoc_runs/bridge_contract_clean_prompt_abstraction_fix_20260512/
```

## 主要发现

### 1. Clean offline prompt 修掉了线上 prompt 污染

在最初的 abstraction smoke 中，`bridge_contract` 产生过与当前树上路径贡献问题无关的 trie 回复。检查后发现：

```text
bridge_contract -> noi_agent_chat()
```

这会继承线上 AIChat 的大型 system prompt 和产品兜底例子，使离线 `bridge_contract` ablation 不够干净。

修复后：

```text
bridge_contract -> clean Offline Bridge Contract Tutor prompt -> _chat_completion_create()
```

targeted rerun 不再出现 trie 跑偏。这说明 clean offline prompt 是必要的。

### 2. 但 prompt-only Bridge Contract 仍会在高风险 bridge 上泄露

即使 clean prompt 明确禁止完整公式、候选答案式标记、二选一关键槽位和完整规则，`cp_bridge_001` 的 repeated tutor-only reruns 仍多次产生 answer-bearing micro-example。

典型风险不是完整代码泄露，而是：

```text
把学生当前缺失的贡献/汇总桥梁，通过微型例子中的标记动作、符号、位置或规则提前展示出来。
```

这正是 critical bridge leakage 的核心失败模式。

### 3. 抽象 prompt 是必要的，但不是充分安全机制

这次 patch 能降低两类风险：

- prompt 被具体算法清单绑死；
- 未覆盖算法因为没有专门规则而失控。

但它不能单独保证：

```text
高风险 missing bridge 不被微型例子说穿。
```

因此不能把这次结果解释为：

```text
只要把 prompt 抽象化，Bridge Contract 就安全了。
```

更合理的解释是：

```text
abstract bridge-shape prompting 是 prompt hygiene；
critical bridge leakage 仍需要 Guard / Repair / risk-triggered route 或更保守的 deterministic scaffold。
```

## 对 Research v1 的影响

本次 smoke 支持三个后续决策：

1. 不继续为单个算法追加专门 prompt 规则，避免 prompt 膨胀和 benchmark overfitting。
2. 将 `cp_bridge_001` 作为 high-risk aggregation/contribution regression case。
3. 在 10-20 case dev ablation 中单独观察：
   - `bridge_contract`
   - `bridge_contract + guard`
   - `bridge_contract + guard + repair`
   - `dbox_inspired_decomposition_tutor + guard`
   - `enhanced_prompt_only`

如果高风险 contribution/aggregation case 继续出现 answer-bearing micro-example，应考虑 route policy：

```text
critical_bridge_request
+ aggregation_contribution_bridge
+ high leakage risk
=> guard required / repair required / deterministic L1-L2 safe scaffold
```

本次修复后，离线 runner 已新增一个可选的 dev-only pipeline：

```text
pipeline_mode=deterministic_safe_scaffold
```

它只用于研究对照：

- 先运行 Bridge Judge；
- 跳过 Tutor / Leakage Judge / Repair；
- 直接返回确定性的 L1 安全观察任务；
- 对 contribution/aggregation bridge，只要求学生列出真实影响对象和最终应统计结果；
- 不给辅助标记、符号、位置、完整公式或代码；
- 不进入默认 dev ablation suite，也不影响线上 AIChat。

1-case 验证：

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --limit 1 \
  --tutor-mode bridge_contract \
  --pipeline-mode deterministic_safe_scaffold \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1 \
  --output-jsonl evals/aichat/ad_hoc_runs/bridge_contract_clean_prompt_abstraction_fix_20260512/deterministic_safe_scaffold_limit1.jsonl
```

结果：

- `case_count=1`
- `error_count=0`
- `llm_call_count=1`
- `final_response_source=safe_fallback`
- `stage_errors={}`

Suite-level 验证：

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_suite_smoke1 \
  --limit 1 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 0 \
  --include-safe-scaffold
```

结果：

- `condition_count=12`
- `combined_row_count=12`
- `bridge_contract_safe_scaffold` 已写入 manifest 和 key CSV
- `bridge_contract_safe_scaffold` 的 `final_response_source=safe_fallback`
- 该轮 review workbook 有 11 条可评审回复，因为其中一个非 safe-scaffold 条件没有生成可评审回复；safe scaffold 本身没有被漏导出。

## 不应声称

本报告不能用于声称：

- Bridge Contract 已经解决 critical bridge leakage；
- prompt 抽象化本身足够安全；
- Guard / Repair 的真实因果效果已经被证明；
- 这 1-case / 11-condition smoke 能代表正式 50-case held-out 结果。

## 下一步

建议顺序：

1. 保留这次 patch，不再继续为了 `cp_bridge_001` 无限追加算法或树上差分专门规则。
2. 在 dev ablation 报告中把 `cp_bridge_001` 标记为 high-risk regression case。
3. 进入 10-20 case dev ablation 前，决定是否把 `deterministic_safe_scaffold` 作为 appendix / stress condition：
   - 高风险 contribution/aggregation bridge 默认不走 tutor-only；
   - 至少走 `+ guard`；
   - 严重 direct critical bridge request 可比较 deterministic safe scaffold。
4. 正式 50-case held-out 前再冻结 prompt / grader。
