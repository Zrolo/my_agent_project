# BridgeBench CP Held-out v4 50 Draft Generation Report 20260514

English version: `bridgebench_cp_heldout_v4_50_generation_report_20260514.md`

v4 是在 v3 基础上生成的 follow-up scaffold 版本，不覆盖 v3。它专门修复 v3 前 10 条短问无上下文样本导致模型容易脑补的问题。

## Summary

- 行数：50
- 上下文增强状态：{'synthetic_followup_context_added': 10, 'context_preserved': 40}
- 上下文充分性：{'sufficient': 45, 'partial': 5}
- 推荐用途：{'main_scaffold_eval': 45, 'main_eval_with_caution': 3, 'policy_safety_slice': 2}

## 使用边界

- v4 的新增近期对话是 synthetic-but-grounded：基于真实题面和原学生短问补一个最小上一轮 AI probe。
- v4 更适合用于 50-case generation-only 和 scaffold 主实验前的 dev run。
- v3 仍保留为混合数据，可以单独报告 `clarification_safety_slice`。
- v4 仍是 `draft_needs_coach_review`，不能称为 gold。
