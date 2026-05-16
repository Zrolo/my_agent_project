# Held-out 50 Coach Labeling Launch 20260512

本文件用于启动 Research v1 的 50-case held-out 教练审查与部分双标。它不是论文结果，只是进入正式主实验前的数据冻结准备。

## 文件

| 用途 | 文件 |
|---|---|
| 50 条 held-out 草稿 JSONL | `docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl` |
| Coach A 全量标注表 | `docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx` |
| Coach B 20 条复标子集 JSONL | `docs/research/bridgebench_cp_heldout_v1_50_coach_b_overlap_20.jsonl` |
| Coach B 20 条复标表 | `docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_b_overlap_20.zh.xlsx` |
| 数据集说明 | `docs/research/bridgebench_cp_heldout_v1_50_card.zh.md` |
| 结构校验报告 | `docs/research/bridgebench_cp_heldout_v1_50_validation_report.json` |

## 当前校验状态

最新结构校验通过：

```text
row_count = 50
recent_dialogue_distribution = none: 10, short: 25, long: 15
student_code_excerpt_distribution = none: 38, present: 12
reference_label_status = draft_needs_coach_review
dev_seed_overlap = 0
error_count = 0
```

这说明数据集可以进入教练审查，但还不能作为 gold label。

## 先标 case，后评 AI 回复

这一步是 **case/reference annotation**，不是 AI 回复盲评，所以工作簿里没有“AI 回复（要评分）”。教练现在要判断的是样本本身：

- 学生问题是否真实；
- 上下文和近期对话是否足够；
- 学生已经知道什么；
- 当前 missing bridge、forbidden content、success criteria 是否合理。

等 Coach A / B 完成 reference 标注并冻结 held-out 后，我们才会用冻结 prompt / judge / rubric 让各个系统生成 AI 回复，再导出 response blind review workbook。那一阶段的表格会包含：

- `上下文 AI 回复`：近期对话中的上一轮 assistant 回复；
- `AI 回复（要评分）`：当前系统生成、需要盲评的目标回复。

## Coach A 任务

Coach A 审查全部 50 条，目标是形成 single-coach reference draft。

请重点检查：

1. 学生问题是否像真实信息学竞赛学生会问的话；
2. `problem_context` 是否足够判断当前卡点；
3. `recent_dialogue` 是否会改变“学生已经知道什么”的判断；
4. 这轮是否能合理标出 missing bridge；
5. `forbidden_content` 是否真的对应“当前不该直接告诉学生的关键桥”；
6. `success_criteria` 是否能让后续回复盲评有标准。

标注表里，至少需要为 `review_status=labeled` 的行填写：

- `turn_type`
- `diagnosis_uncertainty`
- `student_problem_solving_state`
- `student_attempt_level`
- `student_already_stated_bridge`
- `policy_risk_type`
- `primary_bridge_family`
- `primary_bridge_subtype_id`
- `evidence_type`
- `evidence_quote`
- `registered_focus_id`
- `focus_match_status`
- `help_seeking_type`
- `max_scaffold_level`
- `help_forms`
- `general_forbidden_content`
- `bridge_specific_forbidden_content`
- `leakage_risk`
- `coach_confidence`
- `review_status`

如果某条样本不适合进入 held-out，请把 `review_status` 设为 `needs_discussion`，并在 `coach_free_notes` 说明问题。

## Coach B 任务

Coach B 独立标注 20 条 overlap 子集。该子集仍覆盖 10 个 category，并在有代码的类别中提高代码样本占比，用于估计普通文本卡点和带代码卡点的标注一致性。

Coach B 不应参考 Coach A 的标签。完成后用于计算：

- bridge family agreement；
- subtype / focus relaxed agreement；
- help level agreement；
- leakage risk agreement；
- coach confidence distribution；
- needs-adjudication case list。

## 双标子集

Coach B 子集包含：

```text
heldout_cp_016, heldout_cp_017,
heldout_cp_011, heldout_cp_012,
heldout_cp_030, heldout_cp_032,
heldout_cp_041, heldout_cp_042,
heldout_cp_001, heldout_cp_002,
heldout_cp_006, heldout_cp_007,
heldout_cp_020, heldout_cp_021,
heldout_cp_025, heldout_cp_026,
heldout_cp_035, heldout_cp_036,
heldout_cp_046, heldout_cp_049
```

其中 8 条包含 `student_code_excerpt`，用于覆盖学生贴代码、局部条件补全和调试证据场景。

## 重要边界

- 这批 50 条现在是 `draft_needs_coach_review`，不是 adjudicated gold。
- 可以在教练审查阶段修改样本文本和 `success_criteria`。
- 2026-05-13 已重新导出 Coach A / B 标注表，桥梁细分下拉选项改为抽象 subtype；具体算法信息请写入 `algorithm_topic` 语境、`registered_focus_id` 或 `primary_bridge_subtype_note`，不要为了 Dijkstra / SPFA / Floyd 等算法分别新增 subtype。
- 桥梁禁止内容应使用抽象泄露形状，例如 `no_exact_guard_condition`、`no_exact_boundary_update_rule`、`no_fully_worked_micro_trace`。详细规则见 `bridge_taxonomy_abstraction_policy_v1.zh.md`。
- 一旦冻结为正式 held-out，不能再根据同一批主实验结果回头调 prompt / judge / rubric。
- EDF-inspired 仍是 dev / appendix 候选，不进入当前建议主表。
- 主实验 prompt / judge / rubric 需要按 `prompt_freeze_decision_20260512.zh.md` 冻结后再运行。

## 下一步命令

Coach A / B 填完后，先运行 workbook validation：

```bash
python3 -m evals.aichat.validate_coach_workbook_v2 \
  --input docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx
```

导出 Coach A JSONL：

```bash
python3 -m evals.aichat.export_coach_v2_gold_jsonl \
  --input docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx \
  --output-jsonl docs/research/coach_reference_heldout_v1_50_a.jsonl
```

Coach B 同理导出为：

```text
docs/research/coach_reference_heldout_v1_50_b_overlap_20.jsonl
```

之后再做 agreement summary 和 adjudication。

Coach A / B 都导出 JSONL 后，计算 agreement：

```bash
python3 -m evals.aichat.summarize_coach_label_agreement \
  --annotator-a-jsonl docs/research/coach_reference_heldout_v1_50_a.jsonl \
  --annotator-b-jsonl docs/research/coach_reference_heldout_v1_50_b_overlap_20.jsonl \
  --output-json docs/research/coach_agreement_heldout_v1_50_overlap20_20260512.json \
  --output-md-zh docs/research/coach_agreement_heldout_v1_50_overlap20_20260512.zh.md \
  --output-md docs/research/coach_agreement_heldout_v1_50_overlap20_20260512.md
```

该 summary 只用于判断哪些 case 需要 adjudication。正式论文中应称为 `coach reference agreement`，不要称为绝对 ground truth。

根据 agreement summary 生成裁决表：

```bash
python3 -m evals.aichat.export_coach_adjudication_workbook \
  --agreement-json docs/research/coach_agreement_heldout_v1_50_overlap20_20260512.json \
  --annotator-a-jsonl docs/research/coach_reference_heldout_v1_50_a.jsonl \
  --annotator-b-jsonl docs/research/coach_reference_heldout_v1_50_b_overlap_20.jsonl \
  --draft-jsonl docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl \
  --output-xlsx docs/research/coach_adjudication_workbook_heldout_v1_50_overlap20.zh.xlsx
```

这张表会把 Coach A / Coach B 的关键标签并排展示，只导出 `needs_adjudication_case_ids`。如果你希望人工复核全部 20 条 overlap，可以额外加：

```text
--include-all-paired
```

裁决表不是 AI 回复盲评表；它用于形成最终 held-out reference。

完成必要裁决后，导出正式 frozen held-out JSONL：

```bash
python3 -m evals.aichat.export_heldout_frozen_reference \
  --draft-jsonl docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl \
  --coach-a-workbook docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx \
  --output-jsonl docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --reference-status coach_reference
```

如果已经完成 Coach A / Coach B 分歧裁决，可以把 `--reference-status` 改成：

```text
adjudicated_reference
```

导出器不会补造标签；如果 50 条中任何一条没有 `review_status=labeled`，它会失败并报告 `missing_labeled_reference`。导出后必须再跑 formal preflight：

```bash
python3 -m evals.aichat.validate_heldout_50_dataset \
  --dataset docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --output-json docs/research/bridgebench_cp_heldout_v1_50_formal_preflight_report.json \
  --require-frozen-status
```

只有该检查 `ok=true` 后，才进入 400-row 主实验。
