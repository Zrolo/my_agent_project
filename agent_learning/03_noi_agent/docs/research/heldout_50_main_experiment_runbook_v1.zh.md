# 50-case Held-out 主实验 Runbook v1

日期：2026-05-13

本 runbook 规定 Research v1 正式 50-case held-out 主实验的可复现执行流程。它不是实验结果；只有在 prompt / judge / rubric / model runtime / dataset 全部冻结后，才能按本流程发车。

## 前置条件

正式运行前必须满足：

- Coach A 完成 50 条 held-out task/reference 审查；
- Coach B 完成至少 20 条 overlap 复标；
- 低置信、多桥梁和重大泄露分歧已裁决；
- held-out 输入 JSONL 已冻结，例如：

```text
docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl
```

- 不再使用该 50-case 结果回头调同一批 prompt / judge / rubric；
- `prompt_patch_log.md`、`judge_prompt_patch_log.md` 和 review rubric 版本已经冻结。

如果这些条件未满足，只能做 dry run 或 dev check，不能写成 held-out headline。

## 数据集 Formal Preflight

可先运行总 readiness check，确认 Coach A/B 标注、frozen export 和 formal preflight 是否齐全：

```bash
python3 -m evals.aichat.check_heldout_50_readiness \
  --output-json docs/research/heldout_50_readiness_YYYYMMDD.json \
  --output-md-zh docs/research/heldout_50_readiness_YYYYMMDD.zh.md \
  --output-md docs/research/heldout_50_readiness_YYYYMMDD.md
```

只有 `ready_for_main_experiment=true` 且 `blocking_reasons=[]` 时，才继续执行主实验。

正式主实验只接受 frozen reference 数据集。开跑前先执行：

```bash
python3 -m evals.aichat.validate_heldout_50_dataset \
  --dataset docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --output-json docs/research/bridgebench_cp_heldout_v1_50_formal_preflight_report.json \
  --require-frozen-status
```

Go 条件：

```text
ok = true
row_count = 50
error_count = 0
require_frozen_status = true
```

如果数据集仍是 `draft_needs_coach_review`，该检查会返回 `frozen_status_required`。这时只能进入教练审查 / 裁决 / freeze export，不能启动正式 400-row 主实验。

当前草稿 preflight 记录见 [heldout_50_formal_preflight_report_20260513.zh.md](heldout_50_formal_preflight_report_20260513.zh.md)。

Coach A / B 审查和必要裁决完成后，用导出器生成 frozen JSONL：

```bash
python3 -m evals.aichat.export_heldout_frozen_reference \
  --draft-jsonl docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl \
  --coach-a-workbook docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx \
  --output-jsonl docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --reference-status adjudicated_reference
```

如果只有 Coach A single-coach reference，还没有完成裁决，使用 `--reference-status coach_reference`，并且不能在论文中称为 adjudicated reference。

## 主实验条件集

离线 runner 使用：

```text
--condition-set heldout_main
```

该条件集包含 8 个主表条件：

| condition_id | tutor_mode | pipeline_mode | 论文角色 |
|---|---|---|---|
| `current_system_deployment` | `current_system` | `tutor_only_no_diagnosis` | deployment baseline |
| `enhanced_prompt_only_clean` | `enhanced_prompt_only` | `tutor_only_no_diagnosis` | strong prompt-only baseline |
| `codehelp_codeaid_clean` | `codehelp_codeaid_no_direct_solution_tutor` | `tutor_only_no_diagnosis` | programming guardrail baseline |
| `dbox_inspired_guard` | `dbox_inspired_decomposition_tutor` | `tutor_plus_guard` | DBox-inspired decomposition + guard baseline |
| `bridge_inspired_expert_decision_clean` | `bridge_inspired_expert_decision_tutor` | `tutor_only_no_diagnosis` | expert-decision baseline |
| `single_llm_structured_guard` | `single_llm_structured` | `tutor_plus_guard` | strong single-LLM guarded baseline |
| `bridge_contract_guard` | `bridge_contract` | `tutor_plus_guard` | Bridge Contract + Guard method |
| `bridge_contract_guard_repair` | `bridge_contract` | `tutor_plus_guard_plus_repair` | Bridge Contract + Guard + Repair method |

EDF-inspired、oracle/shuffled contract、safe scaffold 和 risk-triggered simulation 只进入 appendix / dev，不进入主表。

## 固定运行配置

主实验比较 tutoring harness，不比较模型。默认固定为：

```text
Tutor provider: deepseek_flash
Tutor model: deepseek-v4-flash
Tutor thinking mode: profile_default / effective enabled
Judge provider: deepseek
Judge model: deepseek-v4-flash
Judge thinking mode: disabled
Leakage Judge timeout: 25s
Max token budgets: 当前默认值，不提高到 128k
```

正式运行命令不要传 `--chat-thinking-mode disabled`，除非明确声明为 thinking-mode ablation。

## 主实验命令

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD \
  --condition-set heldout_main \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

预期输出：

```text
50 cases × 8 conditions = 400 rows
```

## 完整性检查

运行后立即执行：

```bash
python3 -m evals.aichat.check_ablation_run_integrity \
  --manifest evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD/manifest.json \
  --output-json docs/research/heldout_50_main_integrity_YYYYMMDD.json \
  --output-md docs/research/heldout_50_main_integrity_YYYYMMDD.md
```

Go 条件：

```text
expected_row_count = 400
combined_row_count = 400
final_response_row_count = 400
review_row_count = 400
blocking_reasons = []
warning_reasons = []
analysis_ready = true
headline_ready = true
```

如果出现空回复、缺 pair、重复 pair 或 stage warning，不能进入盲评 headline。先按完整性报告中的 `targeted_rerun_commands` 定向重跑。

## 定向重跑与合并

示例：

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_targeted_rerun/CONDITION_CASE \
  --condition-set heldout_main \
  --condition-id CONDITION_ID \
  --case-id CASE_ID \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

合并：

```bash
python3 -m evals.aichat.merge_ablation_reruns \
  --source-manifest evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD/manifest.json \
  --retry-manifest evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_targeted_rerun/CONDITION_CASE/manifest.json \
  --output-dir evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_merged
```

合并后必须再次运行完整性检查。只有 merged run 通过完整性检查，才导出给教练盲评。

## 盲评表

runner 会自动生成：

```text
coach_response_review_workbook_dev_ablation.csv
coach_response_review_workbook_dev_ablation.zh.xlsx
coach_response_review_workbook_dev_ablation.key.csv
```

交给教练的只有 `.zh.xlsx` 盲评表。不要给教练 key 文件。盲评表必须隐藏：

- condition / system 名称；
- tutor model；
- judge model；
- 是否使用 Guard / Repair；
- final response source。

盲评表必须包含：

- `题目来源平台`、`平台题号`、`原题链接`：保证 case 来源真实可追溯，例如洛谷、Codeforces、AtCoder、NOI/NOIP、ICPC 等；
- `原题题面/必要题面`：教练需要先看题面，才能判断学生问题和 AI 回复是否贴合；
- `公开题面摘要`、`题面版权/使用说明`、`题面访问级别`：区分本地教练盲评使用的题面信息和未来公开 artifact 中可保留的信息；
- `学生问题长度类型`：用于检查 50-case 是否覆盖短、中短、中长、长问题；
- `题目/上下文`：作为压缩背景，不替代题面；
- `近期对话` 和 `上下文 AI 回复`：用于判断 AI 回复是否是在合理确认学生已说出的桥，还是过早补完当前桥。

50-case 主实验建议学生问题长度分布为：`short=20`、`medium_short=15`、`medium_long=10`、`long=5`。如果正式 dataset 未达成该分布，应在 preflight 中记录并修正，避免 benchmark 只覆盖短问题。

## AI 自评限制

可以用 AI 预评做 dev triage：

```bash
python3 -m evals.aichat.auto_fill_response_review \
  --input-csv evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_merged/coach_response_review_workbook_dev_ablation.csv \
  --output-csv evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_merged/coach_response_review_workbook_heldout_50_ai_prelim.csv \
  --output-xlsx evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_merged/coach_response_review_workbook_heldout_50_ai_prelim.zh.xlsx
```

但 AI 自评不能作为 gold label，也不能替代 Coach A / Coach B 盲评。

## 结果分析

教练盲评完成后运行：

```bash
python3 -m evals.aichat.analyze_dev_ablation_review \
  --review-xlsx PATH_TO_FILLED_REVIEW_XLSX \
  --key-csv evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_merged/coach_response_review_workbook_dev_ablation.key.csv \
  --output-labels-jsonl docs/research/coach_response_review_labels_heldout_50_YYYYMMDD.jsonl \
  --output-json docs/research/heldout_50_main_analysis_YYYYMMDD.summary.json \
  --output-md-zh docs/research/heldout_50_main_analysis_YYYYMMDD.zh.md \
  --output-md docs/research/heldout_50_main_analysis_YYYYMMDD.md
```

正式报告必须包含：

- quality / core6 / micro-example；
- critical bridge leakage；
- student-ready pass；
- response burden；
- paired win/tie/loss；
- p50 / p95 latency；
- LLM call count；
- stage error count；
- coach agreement / calibration 状态。

## 允许写的结论

可以写：

```text
Under a fixed DeepSeek V4 Flash tutor and judge stack, the frozen 50-case held-out evaluation compares tutoring harness variants.
```

不能写：

```text
某个系统显著更好
```

除非它来自冻结 50-case、教练盲评、配对分析和必要的统计/置信区间。
