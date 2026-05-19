# Sample Unit Clarity Change Log 20260519

## 输入与输出

- 输入稿件：`docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_3_sample_transparency.zh.md`
- 输出稿件：`docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_4_sample_unit_clarity.zh.md`
- 本日志：`docs/research/sample_unit_clarity_change_log_20260519.zh.md`

## 主要修改

1. Methods / Dialogue-State v3 Cases And Slices
   - 增加 case-level 与 response-level 的单位边界说明。
   - 明确 case-level tutoring situation 是 slice assignment 的 primary unit。
   - 明确 response-level outputs 来自 7 anonymized conditions applied to each case。
   - 明确 condition differences 通过 same-case paired comparisons 解释，而不是把 217 tutor responses 当作 independent cases。

2. Appendix A
   - 在 Case Inventory Table 前新增 audit tag 说明。
   - 新增 audit tag pattern -> human-readable interpretation 小表。
   - 解释 `no_recent_dialogue` / `vague_question`、`recent_dialogue_ends_with_assistant` / `has_problem_context`、`pronoun_dependent_question`、`has_code_excerpt`、`safe_refusal`。

3. `dialogue_v3_045_debugging_evidence`
   - 已检查原始记录。
   - Context-readiness audit: `recommended_use=policy_safety_slice`、`expected_tutor_move=safe_refusal`、`current_question_specificity=policy_request`。
   - Reviewed candidate case file: `expected_tutor_move=prerequisite_repair`。
   - 本次没有重新分配 slice；在 Appendix note 和该行 `slice_assignment_rationale` 中标记 `needs_manual_audit`，等待人工确认。

4. Limitations
   - 增加说明：50 cases are curated high-risk dialogue-state cases rather than a random sample of all CP tutoring interactions。

## Claim Gate 检查

| 检查项 | 结果 |
| --- | --- |
| 是否新增实验 | no |
| 是否修改数字 | no |
| 是否改变 evidence class | no |
| 是否重新分配 slice | no，未人工确认前不重新分配 |
| 是否把 217 当 independent cases | no |
| 是否违反 claim gate | no |

## 具体边界说明

- 没有新增 condition、prompt、线上系统或主实验数据。
- 没有改变 `main_scaffold_eval`、sensitivity、stress、fairness sensitivity、calibration 的 evidence class。
- 没有把 all-50 aggregate 写成 headline。
- 没有把 217 tutor responses 提升为 case-level 样本量。
- 没有修改 `dialogue_v3_045_debugging_evidence` 的 slice；只增加 needs-manual-audit 注释。
- 没有写 Bridge Contract 强胜利口径。
