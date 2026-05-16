# Held-out 50 Readiness Report

本报告汇总 50-case held-out 从草稿到正式主实验前的当前状态。它不是实验结果，只是发车门禁。

## 总结

- ready_for_main_experiment: `False`
- blocking_reasons: `coach_a_incomplete`, `coach_b_overlap_incomplete`, `frozen_jsonl_missing`

## 状态表

| 项 | 状态 | 备注 |
|---|---|---|
| draft validation | pass | `docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl` |
| Coach A labeled | blocked | 0 / 50 |
| Coach B overlap labeled | blocked | 0 / 20 |
| frozen JSONL exists | blocked | `docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl` |
| frozen formal preflight | blocked | require frozen reference status |

## 下一步

- 补齐 Coach A 全量标注；
- 补齐 Coach B overlap 复标；
- 计算 agreement 并裁决分歧；
- 导出 frozen reference JSONL；
- 重新运行 formal preflight，直到无 blocker。
