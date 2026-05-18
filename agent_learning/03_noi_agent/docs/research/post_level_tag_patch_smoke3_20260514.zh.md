# Post-Level-Tag Patch Smoke 3 报告（2026-05-14）

本报告记录 `patch_20260514_remove_internal_level_tags_from_offline_research_outputs` 之后的 3-case smoke。该 smoke 只用于开发阶段工程检查，不作为正式论文结果。

## 目的

- 检查离线研究回复中是否还残留 `[LEVEL:Lx]` 内部标签。
- 检查 Guard / Repair 链路在去掉内部标签后是否仍能导出完整 `final_response_text`。
- 检查正式 50-case 前需要固定的运行参数，特别是 Judge timeout / retry。

## 输入与设置

- 输入数据：`docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl`
- 样本：前 3 条
  - `heldout_v4_luogu_001`
  - `heldout_v4_luogu_002`
  - `heldout_v4_luogu_003`
- 生成模型：`deepseek_flash`
- Tutor thinking：`enabled`
- Judge provider：`deepseek`
- Tutor max tokens：`NOI_CHAT_MAX_COMPLETION_TOKENS=128000`
- Judge / Repair max tokens：`20000`

## 第一轮：无 retry / 5s 默认 timeout

输出目录：

- `evals/aichat/ad_hoc_runs/post_level_tag_patch_smoke3_core_20260514`
- `evals/aichat/ad_hoc_runs/post_level_tag_patch_smoke3_guard_repair_20260514`

结果：

| Run | Rows | `[LEVEL]` 命中 | 空 final_response | stage_errors |
|---|---:|---:|---:|---:|
| core | 15 | 0 | 2 | 3 |
| guard_repair | 15 | 0 | 3 | 5 |

主要问题：

- `[LEVEL]` 已经清除。
- 默认 5s Judge timeout 太紧，出现 Bridge Judge / Leakage Judge timeout。
- 出现一次 Bridge Judge schema invalid：`problem_solving_state has invalid enum: representation_state_bridge`。
- 空回复来自 Judge stage 失败，不是去掉 `[LEVEL]` 导致的生成失败。

## 第二轮：retry=1 / Judge timeout=25s

输出目录：

- `evals/aichat/ad_hoc_runs/post_level_tag_patch_smoke3_core_retry_20260514`
- `evals/aichat/ad_hoc_runs/post_level_tag_patch_smoke3_guard_repair_retry_20260514`

结果：

| Run | Rows | `[LEVEL]` 命中 | 空 final_response | stage_errors | review rows |
|---|---:|---:|---:|---:|---:|
| core_retry | 15 | 0 | 0 | 0 | 15 |
| guard_repair_retry | 15 | 0 | 0 | 0 | 15 |

条件摘要：

| Condition | Rows | Final source | Repair count | Retry count |
|---|---:|---|---:|---:|
| `enhanced_prompt_only_clean` | 3 | candidate ×3 | 0 | 0 |
| `dbox_inspired_clean` | 3 | candidate ×3 | 0 | 0 |
| `dbox_inspired_guard` | 3 | candidate ×3 | 0 | 0 |
| `bridge_contract_compact_guard` | 3 | candidate ×3 | 0 | 0 |
| `bridge_guided_dbox_style_guard` | 3 | candidate ×3 | 0 | 2 |
| `enhanced_prompt_only_guard` | 3 | candidate ×3 | 0 | 0 |
| `enhanced_prompt_only_guard_repair` | 3 | repair ×2, candidate ×1 | 2 | 0 |
| `dbox_inspired_guard_repair` | 3 | repair ×2, candidate ×1 | 2 | 1 |
| `bridge_contract_compact_clean` | 3 | candidate ×3 | 0 | 0 |
| `bridge_contract_compact_guard_repair` | 3 | repair ×2, candidate ×1 | 2 | 0 |

## 观察

1. 去掉 `[LEVEL]` 对 Bridge Judge 没有结构性影响。Bridge Judge 仍输出 `allowed_help_level`，但学生可见回复不再导出内部标签。
2. 正式 50-case 运行不应使用默认 5s Judge timeout。建议使用：
   - `NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=25`
   - `NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25`
   - `NOI_REPAIR_RESPONSE_TIMEOUT_SECONDS=25`
   - `--max-retries 1`
3. 这次 patch 只解决输出卫生，不解决教学质量。抽查 `heldout_v4_luogu_001` 发现，部分回复仍可能把状态/表示桥讲得过近，例如直接引导到“第 i 到第 j 的子串/区间”。
4. 因此不能把本 smoke 解读为 Bridge Contract 质量已经改善。它只说明离线导出链路在合适 timeout/retry 下可以稳定产生无内部标签的评审材料。

## 下一步建议

1. 把上述 timeout / retry 写入 50-case generation runbook。
2. 在正式 50-case 前，不再继续为单个样例大改 prompt。
3. 用 5-10 条人工快速抽查确认 v4 case 的上下文对齐和题面可读性。
4. 之后进入 50-case generation-only，并导出：
   - AI preliminary review 表；
   - Human blind review 表；
   - 未填写评分的教练版 workbook。
