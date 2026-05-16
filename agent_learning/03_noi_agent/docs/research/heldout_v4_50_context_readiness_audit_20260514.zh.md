# Held-out v4 50 Context Readiness Audit 20260514

English version: `heldout_v4_50_context_readiness_audit_20260514.md`

这份报告是 deterministic 数据审计，不调用 LLM，也不修改 prompt。目的不是评价模型，而是先判断每个 case 本身是否足够支撑“根据学生当前问题回答”的评测。

## Summary

- 行数：50
- 上下文充分性：`partial`=5, `sufficient`=45
- 学生问题具体性：`medium`=4, `policy_request`=2, `pronoun_dependent`=27, `specific`=17
- 期望教学动作：`continue_prior_scaffold`=27, `micro_scaffold`=21, `safe_refusal`=2
- 是否应推断 bridge：`low_confidence_only`=3, `no`=2, `yes`=45
- 推荐用途：`main_eval_with_caution`=3, `main_scaffold_eval`=45, `policy_safety_slice`=2

## Interpretation

- `insufficient` 样本不应直接进入“谁的辅导质量最好”的主比较；它们更适合测试系统是否会澄清、是否少脑补。
- `partial` 样本可以用于 dev，但正式分析时应单独标记或做 sensitivity analysis。
- `sufficient` 样本更适合作为 scaffolding 主评测样本。
- 如果短问题无近期对话，例如“分支该怎么列？”，好回复应优先澄清或给最小观察任务，而不是直接展开题解桥梁。
