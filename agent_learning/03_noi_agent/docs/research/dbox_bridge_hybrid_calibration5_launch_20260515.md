# DBox / Bridge Hybrid 5-Case Calibration Blind Review Pack

Date: 2026-05-15

This file documents the first coach-calibration pack for the 50-case generation-only dev run. The pack is used to align the review rubric; it is not a formal paper result.

## Files

- Coach blind-review workbook: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/coach_response_review_workbook_calibration5_20260515.zh.xlsx`
- Hidden key: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/coach_response_review_workbook_calibration5_20260515.key.csv`

The `key.csv` contains real condition names and must not be shared with blind-review coaches. Coaches should only use the `.xlsx` workbook.

## Purpose

This round is calibration only:

1. Familiarize coaches with the updated review dimensions.
2. Align the boundary between `minor_bridge_leakage`, `major_bridge_leakage`, and `answer_leakage`.
3. Align judgments for student-readiness and student response burden.
4. Identify confusing rubric points before a larger review round.

## Selected 5 Cases

| case_id | Source | Bridge type | Selection rationale |
|---|---|---|---|
| `heldout_v4_luogu_001` | Luogu P2890 | State / representation semantics | AI-preliminary labels showed large differences across conditions on whether state semantics were leaked. |
| `heldout_v4_luogu_012` | Luogu P2857 | Predicate / check semantics | Several responses sit near the minor-leakage boundary, useful for calibrating check-direction hints. |
| `heldout_v4_luogu_019` | Luogu P1719 | Boundary update / loop direction | Includes a high-risk Bridge Contract compact example, useful for calibrating whether a boundary update rule was completed for the student. |
| `heldout_v4_luogu_031` | Luogu P1908 | Data-structure operation semantics | Several responses are borderline, useful for calibrating whether a data-structure semantics explanation is too strong. |
| `heldout_v4_luogu_041` | Luogu P1050 | Implementation boundary / code slot | Includes answer-slot or code-like leakage risks, useful for calibrating local implementation hints. |

## Coach Workflow

Please follow the workbook sheets “评审流程” and “评分指南”. Recommended order:

1. Read the problem statement and current student question.
2. Then read recent dialogue and context AI reply as background only; they should not override the current student question.
3. Evaluate whether `AI 回复（要评分）` directly addresses the current student question.
4. Fill all rubric fields. Notes are required when:
   - the leakage label is `major_bridge_leakage` or `answer_leakage`;
   - `是否愿意给学生看` is `no`;
   - overall quality is 1 or 2;
   - preference rank is 1 or the last rank;
   - reviewer confidence is low;
   - needs discussion is yes.

## What This Round Does Not Do

- It does not produce a formal system ranking.
- It does not decide whether DBox-inspired, Bridge Contract, or the hybrid is best.
- It does not change online AIChat.
- It does not treat AI-preliminary labels as gold labels.

## Next Step

After this 5-case calibration:

1. Summarize coach disagreements.
2. If needed, adjust rubric instructions before changing tutor prompts.
3. Proceed to the 50-case / 250-response human blind review or partial double annotation.
