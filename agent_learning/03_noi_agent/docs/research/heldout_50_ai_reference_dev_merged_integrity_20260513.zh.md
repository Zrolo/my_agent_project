# 50-case AI Draft Reference Dev Run 完整性报告

## 结论

本次 `heldout_main` 全量 dev run 已通过完整性检查，可以作为下一步 AI 自评 / 教练盲评输入。

但需要注意：本 run 使用的是 `AI-assisted draft reference`，不是最终人工裁决 gold。因此它可以用于开发阶段筛查、系统比较和发现问题，不能直接作为论文 headline 结果。

## Run 信息

- Manifest: `evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513_merged/manifest.json`
- 输入数据: `docs/research/bridgebench_cp_heldout_v1_50_ai_reference_draft_20260513.jsonl`
- 条件集: `heldout_main`
- case 数: 50
- condition 数: 8
- 预期行数: 400
- 合并后行数: 400
- 有最终回复行数: 400
- 盲评表行数: 400

## 条件列表

- `current_system_deployment`
- `enhanced_prompt_only_clean`
- `codehelp_codeaid_clean`
- `dbox_inspired_guard`
- `bridge_inspired_expert_decision_clean`
- `single_llm_structured_guard`
- `bridge_contract_guard`
- `bridge_contract_guard_repair`

## 定向补跑

原始全量 run 中有 1 行空最终回复：

- `heldout_cp_015` × `bridge_contract_guard`

根因是 Leakage Judge 判定 `safe_action=block` 后，旧 runner 对 guard-only block 输出空 `final_response_text`。已修正 runner：guard-only block 现在输出 deterministic safe scaffold，而不是空回复。

随后对该 pair 做定向补跑，并合并到新 run pack：

- 合并目录: `evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513_merged`
- 被替换 pair: `heldout_cp_015` × `bridge_contract_guard`

## 完整性检查结果

- missing pairs: 0
- duplicate pairs: 0
- empty final response rows: 0
- stage warning rows: 0
- blocking reasons: 0
- warning reasons: 0
- analysis ready: true
- headline ready: true

这里的 `headline ready` 只表示 run 文件完整，不表示结果可以作为正式论文 headline。正式论文 headline 仍需要人工复核标签、双标/裁决和盲评结果。

## 下一步

建议下一步先做 AI preliminary review，用来筛查 400 条回复中的明显问题、静态泄露风险和系统间大致趋势。之后再决定是否把完整 400 行交给教练盲评，或先抽样复核高风险/争议样本。
