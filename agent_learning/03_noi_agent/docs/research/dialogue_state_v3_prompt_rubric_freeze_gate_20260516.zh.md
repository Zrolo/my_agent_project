# Dialogue-State v3 Prompt / Rubric Freeze Gate 20260516

本记录说明 dialogue-state v3 50-case reviewed candidate 进入 response generation 前的 prompt / rubric / grader freeze gate。该 gate 的目标是把下一轮实验从“继续调 prompt”切换为“按固定条件生成回复并盲评”。

## 当前状态

数据集：

- `docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl`
- `reference_label_status=reviewed_candidate`
- `case_source_review_status=coach_A_case_source_review_passed`

校验报告：

- `docs/research/dialogue_state_v3_50_reviewed_candidate_validation_report_20260516.json`
- `row_count=50`
- `error_count=0`

重要边界：

- `reviewed_candidate` 只表示 case/source 已通过 Coach A 审核；
- 它不是 gold data；
- 它不是 adjudicated reference；
- 它不是 AI 回复盲评结果；
- 它还不能用于论文 headline result。

## 冻结目标

本 gate 冻结的是下一轮 response generation / blind review 的实验表面：

1. 数据输入；
2. 主实验 condition set；
3. tutor / judge / repair 模型配置；
4. response review rubric v3；
5. case-specific rubric 字段；
6. blind review workbook schema；
7. stage logging 字段。

冻结后，不应根据同一批 50-case response 结果回头修改本轮 prompt / rubric / grader。若必须修改，需重新打开 freeze gate，并记录 patch。

## 主实验 Condition Set

下一轮使用新增 condition set：

```text
dialogue_state_v3_main
```

该 set 固定为 7 个 condition：

| condition_id | tutor_mode | pipeline_mode | 论文角色 |
|---|---|---|---|
| `enhanced_prompt_only_clean` | `enhanced_prompt_only` | `tutor_only_no_diagnosis` | strong prompt-only baseline |
| `codehelp_codeaid_clean` | `codehelp_codeaid_no_direct_solution_tutor` | `tutor_only_no_diagnosis` | no-direct-solution programming guardrail baseline |
| `dbox_inspired_clean` | `dbox_inspired_decomposition_tutor` | `tutor_only_no_diagnosis` | DBox-inspired decomposition baseline |
| `dbox_inspired_guard` | `dbox_inspired_decomposition_tutor` | `tutor_plus_guard` | DBox-inspired + Guard strong baseline |
| `bridge_guided_dbox_style_guard` | `bridge_guided_dbox_style_tutor` | `tutor_plus_guard` | missing-bridge-guided decomposition hybrid |
| `bridge_contract_compact_guard` | `bridge_contract_compact` | `tutor_plus_guard` | compact Bridge Contract + Guard |
| `bridge_contract_compact_guard_repair` | `bridge_contract_compact` | `tutor_plus_guard_plus_repair` | compact Bridge Contract + Guard + Repair |

本轮不把 EDF-inspired、oracle/shuffled contract、risk-triggered routing、safe scaffold 放入主表。它们仍可作为 appendix / dev / stress test 条件。

## Repair 公平性 Add-on

为了避免“Repair 只加在 Bridge Contract 上”的公平性质疑，本 gate 允许一个窄版 appendix run：

```text
dialogue_state_v3_repair_fairness_addon
```

该 set 只包含 1 个 condition：

| condition_id | tutor_mode | pipeline_mode | 用途 |
|---|---|---|---|
| `dbox_inspired_guard_repair` | `dbox_inspired_decomposition_tutor` | `tutor_plus_guard_plus_repair` | 检查 DBox-inspired + Guard 如果也接 Repair，是否改变 quality / leakage trade-off |

该 add-on 不进入主表，不改变 `dialogue_state_v3_main` 的 7-condition 设计。它只用于 appendix / sensitivity analysis，回答：

```text
Bridge Contract + Repair 的改善是否来自 Repair 本身，而不是 missing-bridge-aware generation？
```

Add-on 命令：

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516 \
  --condition-set dialogue_state_v3_repair_fairness_addon \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

预期：

```text
50 cases × 1 condition = 50 rows
```

分析时将该 50-row add-on 与主 run 中的 `dbox_inspired_guard`、`bridge_contract_compact_guard`、`bridge_contract_compact_guard_repair` 合并比较。

## 模型与运行配置

主实验不比较模型，只比较 tutoring harness。下一轮 response generation 固定为：

```text
tutor_model_provider = deepseek_flash
tutor_model = deepseek-v4-flash
tutor_thinking_mode = profile_default / effective enabled
judge_provider = deepseek
judge_model = deepseek-v4-flash
judge_thinking_mode = disabled
repair_provider = deepseek
repair_model = deepseek-v4-flash
repair_thinking_mode = disabled
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS = 25
max token budgets = provider/default Research v1 values
```

不要在本轮命令中传 `--chat-thinking-mode disabled`。若要比较 thinking enabled / disabled，应另设 model-setting ablation。

## Rubric / Workbook 冻结

本轮 response review 使用：

- `docs/research/response_review_rubric_v3.zh.md`
- `docs/research/response_review_rubric_v3.md`
- `docs/research/evaluation_protocol_v3.zh.md`
- `docs/research/evaluation_protocol_v3.md`
- `docs/research/case_specific_rubric_policy_v1.zh.md`
- `docs/research/case_specific_rubric_policy_v1.md`

盲评表必须显示：

- 原题链接 / 题号；
- 必要题面 / 公开摘要；
- 近期对话；
- 上下文 AI 回复；
- 学生当前问题；
- AI 回复（要评分）；
- success criteria；
- forbidden content；
- critical bridge boundary；
- acceptable reveal；
- expected student next action。

盲评表必须隐藏：

- condition / system 名称；
- tutor model；
- judge model；
- 是否使用 Guard / Repair；
- final response source。

## Response Generation 命令

冻结通过后，生成 50-case × 7-condition 回复：

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516 \
  --condition-set dialogue_state_v3_main \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

预期：

```text
50 cases × 7 conditions = 350 rows
```

生成后立即运行完整性检查；若有空回复、缺 pair、stage warning 或重复 pair，需要定向重跑并合并后再导出给教练盲评。

## 仍不能声称

即使本 gate 通过，也不能声称：

- Bridge Contract 已优于 DBox-inspired；
- Guard 已可靠防止 critical bridge leakage；
- Repair 已可靠解决泄露；
- LLM Judge 可替代教练盲评；
- 50-case 已是 gold benchmark；
- reviewed candidate 结果可作为论文 headline result。

更稳的表述是：

```text
The case/source reviewed candidate set is ready for frozen response generation and coach blind review.
```

中文：

```text
case/source 已审核的 reviewed candidate 集可以进入冻结条件下的回复生成和教练盲评。
```

## Go / No-go

Go 条件：

- reviewed candidate validation `ok=true`；
- `dialogue_state_v3_main` condition set 已在 runner 中实现并有单测；
- rubric v3 / evaluation protocol v3 / case-specific rubric policy 已固定；
- 模型配置按本文件记录；
- 后续 reviewer 只拿盲评表，不拿 hidden key。

No-go 条件：

- 继续修改 case 内容但未重开 case/source gate；
- 继续新增主表 condition；
- 改 prompt / rubric 后不记录；
- response generation 结果出现完整性 blocker；
- 教练盲评前暴露 condition key。

## 下一步

1. 按本 gate 命令生成 350-row response run。
2. 做完整性检查和必要的 targeted rerun。
3. 导出中英文盲评表和 hidden key。
4. 先做 5-case calibration blind review。
5. 再进入 Coach A 全量盲评和 Coach B 部分复评。
