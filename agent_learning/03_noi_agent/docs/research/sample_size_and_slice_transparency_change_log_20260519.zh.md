# Sample Size And Slice Transparency Change Log 20260519

## 输入与输出

- 输入稿件：`docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_3.zh.md`
- 输出稿件：`docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_3_sample_transparency.zh.md`
- 本日志：`docs/research/sample_size_and_slice_transparency_change_log_20260519.zh.md`

## 主要修改

1. Abstract
   - 将样本设计句改为 case-level / response-level 双层表达：
     350 tutor responses、7 anonymized offline harnesses、50 reviewed dialogue-state cases。
   - 明确 primary scaffold analysis 为 31-case `main_scaffold_eval` slice，对应 217 tutor responses。
   - 明确 remaining cases 作为 sensitivity analyses 报告。

2. Methods / Dialogue-State v3 Cases And Slices
   - 新增双层数据结构说明：50 case-level tutoring situations 与 350 response-level outputs。
   - 说明每个 case under 7 anonymized conditions，因此 31-case headline scaffold slice 对应 217 tutor responses。
   - 扩展 slice 表，新增 `response_count` 和 `evaluation_target` 两列。
   - 添加 all cases 行：50 cases / 350 responses，但用途标为 sensitivity / appendix only。
   - 新增说明：full 50-case corpus is not discarded；non-main slices separately reported because they test different evaluation targets。

3. Results
   - Results 开头改为 headline results use 31 case-level situations and 217 response-level reviews。
   - 明确 all-case aggregate is sensitivity evidence。

4. Limitations
   - 第一条限制补充：headline slice is 31 cases / 217 responses，应解释为 bounded expert-reviewed evidence，而非 exhaustive CP tutoring coverage。

5. Appendix
   - 新增 Case inventory table，列出 50 个 case-level tutoring situations。
   - 表头包含：`case_id`、`slice`、`bridge_family`、`surface_anchor`、`student_message_short`、`expected_tutor_move`、`slice_assignment_rationale`。
   - 表格说明 217 responses 来自 31 cases x 7 offline harnesses；case-level unit 仍是 31 tutoring situations。

## Claim Gate 检查

| 检查项 | 结果 |
| --- | --- |
| 是否新增实验 | no |
| 是否修改数字 | no |
| 是否把 all-50 写成 headline | no |
| 是否把 217 提升为 case-level 样本量 | no |
| 是否违反 claim gate | no |

## 具体边界说明

- 没有新增 condition、prompt、线上系统或主实验数据。
- 没有改变 `main_scaffold_eval`、sensitivity、stress、fairness sensitivity、calibration 的 evidence class。
- 没有把 all-50 aggregate 写成 headline；all cases row 明确为 sensitivity / appendix only。
- 没有把 217 tutor responses 提升为 case-level 样本量；稿件中写为 response-level outputs / reviews。
- 没有写 Bridge Contract 强胜利口径。
- Appendix inventory 是透明性表，不是新增实验、结果或覆盖性主张。
