# 50-case Generation-only Runbook（2026-05-14）

本 runbook 用于下一轮 **50-case generation-only** 大样本生成。它只检查不同 condition 是否能稳定产出可评审回复，不做 AI 自评、不做教练盲评、不写论文结论。

## 目的

本轮要回答的是工程和实验可行性问题：

```text
在 50 条 held-out draft cases 上，这 5 个候选 condition 是否能稳定生成可评审回复？
```

本轮不回答：

```text
哪个 condition 教学质量最好；
哪个 condition 显著优于 DBox；
Bridge Contract 是否论文主结果成立；
Guard 是否因果提升质量。
```

这些问题必须等教练盲评和正式 held-out 分析后再判断。

## 输入数据

当前使用：

```text
docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl
```

注意：

- 这是 `draft`，不是 frozen gold。
- 本轮只做 generation-only stability check。
- 如果后续根据本轮结果修改 prompt，这轮结果不能作为正式论文 headline。
- v4 是在 v3 基础上生成的 follow-up scaffold 版本：前 10 条短问无上下文样本补入最小 synthetic-but-grounded 上一轮 AI probe，避免模型在主 scaffolding 评测中靠题面脑补学生卡点。
- v3 保留为混合数据，可单独用于 `clarification_safety_slice`；旧 v2 结果只保留为 development diagnostic。

## Context Injection

本轮必须使用 **AIChat-compatible context injection**。离线 runner 参照线上 `/chat` 路径：

```text
full_history[-10:]
-> append current user message built from:
   student_message
   problem title/url/context
   student_code_excerpt
   context strategy
```

具体约束：

- 如果 case 含 `prior_messages`，优先使用它作为历史。
- 如果没有 `prior_messages` 但有 `recent_dialogue`，runner 会把 `学生：... / AI：...` 解析成真实 `user/assistant` messages。
- `student_message` 必须作为最后一轮 user message，不得混入 `recent_dialogue`。
- `student_code_excerpt` 会进入当前 user message，和线上 AIChat 的 `学生当前代码` 字段对齐。
- 输出结果必须记录 `generation_context_source` 和 `generation_message_count`。

这一步是正式重跑的前置条件。否则会出现“教练盲评看到了上下文，但模型生成时没看到上下文”的不公平评测。

## Condition Set

使用现有：

```text
--condition-set dbox_bridge_hybrid
```

包含 5 个 condition：

| condition_id | tutor_mode | pipeline_mode | 本轮角色 |
| --- | --- | --- | --- |
| `enhanced_prompt_only_clean` | `enhanced_prompt_only` | `tutor_only_no_diagnosis` | 强 prompt-only baseline |
| `dbox_inspired_clean` | `dbox_inspired_decomposition_tutor` | `tutor_only_no_diagnosis` | DBox-style no-Guard baseline |
| `dbox_inspired_guard` | `dbox_inspired_decomposition_tutor` | `tutor_plus_guard` | guarded DBox baseline |
| `bridge_contract_compact_guard` | `bridge_contract_compact` | `tutor_plus_guard` | 当前 Bridge Contract 主候选 |
| `bridge_guided_dbox_style_guard` | `bridge_guided_dbox_style_tutor` | `tutor_plus_guard` | 暂时保留的 hybrid appendix/dev 候选 |

`bridge_guided_dbox_style_guard` 在 10-case 人类复核中表现较弱，但本轮先保留，用于观察它在 50-case 上是否仍然不稳定。除非后续教练盲评反转，否则它不进入正式主表。

## 固定模型配置

本轮不做模型比较。所有 condition 使用同一固定生成模型配置：

```text
Tutor provider: deepseek_flash
Tutor model: deepseek-v4-flash
Tutor thinking mode: enabled
Tutor max tokens: 128k (`NOI_CHAT_MAX_COMPLETION_TOKENS=131072`)
Judge provider: deepseek
Judge model: deepseek-v4-flash
Judge thinking mode: disabled
Judge / Repair max tokens: 20k (`NOI_BRIDGE_JUDGE_MAX_TOKENS=20480`, `NOI_LEAKAGE_JUDGE_MAX_TOKENS=20480`, `NOI_REPAIR_RESPONSE_MAX_TOKENS=20480`)
Max retries: 1
```

为减少 generation-only 阶段因偶发超时丢行，建议设置：

```text
NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=25
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25
NOI_REPAIR_RESPONSE_TIMEOUT_SECONDS=25
NOI_BRIDGE_JUDGE_MAX_TOKENS=20480
NOI_LEAKAGE_JUDGE_MAX_TOKENS=20480
NOI_REPAIR_RESPONSE_MAX_TOKENS=20480
NOI_CHAT_MAX_COMPLETION_TOKENS=131072
```

2026-05-14 的 3-case post-level-tag smoke 显示：默认 5s timeout 会导致空回复和缺失盲评行；使用 `timeout=25s` 与 `--max-retries 1` 后，两组 smoke 均达到 `empty_final_response_count=0`、`stage_errors=0`、`review_row_count=combined_row_count`。因此 50-case generation-only 不应使用默认 5s Judge timeout。

本轮按最新要求启用 tutor thinking，并将 tutor max tokens 设为 128k。Judge 仍保持 thinking disabled；如果后续要让 Judge 也启用 thinking，需要单独记录为新的评测配置。

## 执行命令

```bash
NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=25 \
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
NOI_REPAIR_RESPONSE_TIMEOUT_SECONDS=25 \
NOI_BRIDGE_JUDGE_MAX_TOKENS=20480 \
NOI_LEAKAGE_JUDGE_MAX_TOKENS=20480 \
NOI_REPAIR_RESPONSE_MAX_TOKENS=20480 \
NOI_CHAT_MAX_COMPLETION_TOKENS=131072 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --condition-set dbox_bridge_hybrid \
  --input-jsonl docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --chat-thinking-mode enabled \
  --max-retries 1
```

预期：

```text
50 cases × 5 conditions = 250 rows
```

## 输出文件

runner 会生成：

```text
combined_dev_ablation.jsonl
combined_dev_ablation_summary.json
combined_dev_ablation_summary.zh.md
coach_response_review_workbook_dev_ablation.csv
coach_response_review_workbook_dev_ablation.zh.xlsx
coach_response_review_workbook_dev_ablation.key.csv
manifest.json
```

本轮生成盲评表只是为了确认后续可交给教练，不立即填写。

## 完整性检查

生成后立即检查：

```bash
python3 -m evals.aichat.check_ablation_run_integrity \
  --manifest evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514/manifest.json \
  --output-json docs/research/dbox_bridge_hybrid_generation_only_50_integrity_20260514.json \
  --output-md docs/research/dbox_bridge_hybrid_generation_only_50_integrity_20260514.md
```

当前完整性检查脚本只支持 `--output-json` 和 `--output-md`。如需中文完整性报告，应后续扩展脚本，而不是在命令中直接添加 `--output-md-zh`。

Generation-only go 条件：

```text
expected_row_count = 250
combined_row_count = 250
final_response_row_count = 250
review_row_count = 250
empty_final_response_count = 0
duplicate_case_condition_count = 0
missing_case_condition_count = 0
```

允许有少量 non-blocking stage warnings，但必须记录：

```text
Bridge Judge timeout
Leakage Judge timeout
JSON parse error
Guard unknown
fallback response
```

如果出现空回复或缺 pair，不能进入后续教练盲评。先做 targeted rerun。

## Targeted Rerun

如果完整性检查发现某个 `(case_id, condition_id)` 缺失或空回复，使用：

```bash
NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=25 \
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
NOI_REPAIR_RESPONSE_TIMEOUT_SECONDS=25 \
NOI_BRIDGE_JUDGE_MAX_TOKENS=20480 \
NOI_LEAKAGE_JUDGE_MAX_TOKENS=20480 \
NOI_REPAIR_RESPONSE_MAX_TOKENS=20480 \
NOI_CHAT_MAX_COMPLETION_TOKENS=131072 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --condition-set dbox_bridge_hybrid \
  --condition-id CONDITION_ID \
  --case-id CASE_ID \
  --input-jsonl docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514_targeted/CONDITION_ID_CASE_ID \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --chat-thinking-mode enabled \
  --max-retries 1
```

合并：

```bash
python3 -m evals.aichat.merge_ablation_reruns \
  --source-manifest evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514/manifest.json \
  --retry-manifest evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514_targeted/CONDITION_ID_CASE_ID/manifest.json \
  --output-dir evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260514_merged
```

合并后必须重新跑完整性检查。

## 本轮只看哪些指标

只看稳定性和成本：

- row count；
- empty final response；
- stage error；
- timeout；
- JSON parse error；
- review workbook row count；
- LLM calls per turn；
- p50/p95 latency；
- Guard rewrite/block/unknown rate；
- final static risk，仅作为筛查，不作为人工质量结论。

不看或暂不解释：

- overall quality；
- ready/safe_ready；
- condition win/loss；
- coach preference；
- 是否显著优于某 baseline。

## 本轮结束后怎么决策

如果 250 条都可评审：

1. 暂不改 prompt；
2. 选择是否把这份盲评表交给教练；
3. 若交给教练，先小范围抽查 20-50 条，确认表格字段和题面足够；
4. 再决定是否进入正式 50-case blind review。

如果某 condition 明显不稳定：

1. 记录为 stability risk；
2. 只做工程性修复，例如 schema alias、JSON format、timeout；
3. 不做教学 prompt 大改；
4. 定向重跑受影响 condition/case。

如果 `bridge_guided_dbox_style_guard` 仍然质量/稳定性明显较差：

- 将它降级为 appendix/error-analysis condition；
- 不进入正式主表；
- 用它说明“简单拼接 Bridge Contract 与 DBox-style decomposition 不自动带来提升”。

## 禁止事项

本轮禁止：

- 根据 50-case generation-only 结果立即声称哪个系统更好；
- 用 AI 自评替代教练盲评；
- 一边跑一边改 prompt；
- 把 generation-only 的静态风险当作论文 leakage result；
- 把 `draft` 数据集当 frozen held-out gold。
