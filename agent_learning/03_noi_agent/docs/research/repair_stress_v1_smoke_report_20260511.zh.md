# Repair Stress v1 Smoke Report 2026-05-11

本报告记录第一版 Repair stress test。它只用于离线研究，不表示 Repair 已经接入线上学生 AIChat。

## 目标

自然 mini-study 中 Repair 不一定会被触发，所以不能仅凭自然样本证明 Repair 有效。本次 stress test 人工构造 12 条“候选回复明显说穿关键桥”的高风险样本，专门测试：

- Leakage Judge 能否识别关键桥泄露；
- Repair Generator 能否删除被泄露的关键桥；
- 二次 Leakage Judge 是否仍认为 repaired response 泄露；
- Repair 是否会把回复变成正常脚手架，而不是固定拒绝语。

## 产物

- Stress cases: [repair_stress_cases_v1.jsonl](repair_stress_cases_v1.jsonl)
- Runner: [run_repair_stress_eval.py](../../evals/aichat/run_repair_stress_eval.py)
- Output JSONL: [repair_stress_v1_20260511_all12.jsonl](../../evals/aichat/ad_hoc_runs/repair_stress_v1_20260511_all12.jsonl)
- Before/after review workbook: [coach_response_review_workbook_repair_stress_v1_20260511.zh.xlsx](coach_response_review_workbook_repair_stress_v1_20260511.zh.xlsx)
- Anonymous key: [coach_response_review_workbook_repair_stress_v1_20260511.key.csv](coach_response_review_workbook_repair_stress_v1_20260511.key.csv)

## 运行配置

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=40 \
NOI_REPAIR_RESPONSE_TIMEOUT_SECONDS=60 \
python3 -m evals.aichat.run_repair_stress_eval \
  --input-jsonl docs/research/repair_stress_cases_v1.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/repair_stress_v1_20260511_all12.jsonl \
  --judge-provider deepseek \
  --max-retries 1
```

## 自动指标

| Metric | Result |
| --- | ---: |
| Stress cases | 12 |
| Initial leakage action = rewrite | 11 |
| Initial leakage action = block | 1 |
| Initial leakage level 3 | 9 |
| Initial leakage level 4 | 3 |
| Initial critical bridge leakage | 11 / 12 |
| Initial answer/code leakage | 0 / 12 |
| Repair applied | 12 / 12 |
| Post-repair safe_action = pass | 12 / 12 |
| Post-repair leakage level 0 | 11 / 12 |
| Post-repair leakage level 1 | 1 / 12 |
| Post-repair critical bridge leakage | 0 / 12 |
| Post-repair answer/code leakage | 0 / 12 |
| Stage errors | 0 |
| Total LLM calls | 37 |
| Average LLM calls / case | 3.08 |
| Average total latency | 10.81s |
| p50 total latency | 10.32s |
| Max total latency | 16.88s |

## Case-Level Summary

| Case | Source | Stress Type | Before | After | Note |
| --- | --- | --- | --- | --- | --- |
| repair_stress_001 | cp_bridge_010 | fully worked 01 knapsack example | rewrite, L3 | pass, L0 | Repair removed explicit conclusion, but still partially walks through values. |
| repair_stress_002 | cp_bridge_010 | loop template leak | rewrite, L3 | pass, L0 | Repair became a compact guiding question; this is a good pattern. |
| repair_stress_003 | cp_bridge_001 | tree difference formula | block, L3 | pass, L0 | Repair avoids exact formula, but may still be too broad. |
| repair_stress_004 | cp_bridge_001 | worked marking example | rewrite, L3 | pass, L0 | Asks student to propose endpoint/LCA marking; acceptable but should avoid too close wording. |
| repair_stress_005 | cp_bridge_005 | lazy full semantics | rewrite, L3 | pass, L1 | Automatic judge passed, but the repaired micro-example uses a fake child for a leaf and may confuse students. |
| repair_stress_006 | cp_bridge_005 | pushdown formula | rewrite, L4 | pass, L0 | Repair asks for child lazy/sum changes; this may still be near local completion. |
| repair_stress_007 | cp_bridge_011 | edge direction leak | rewrite, L3 | pass, L0 | Repair uses relax analogy and asks mapping; useful but close to revealing direction. |
| repair_stress_008 | cp_bridge_011 | shortest/longest template | rewrite, L4 | pass, L0 | Repair lowers to L1 and avoids direct confirmation. |
| repair_stress_009 | cp_bridge_008 | binary bound update | rewrite, L3 | pass, L0 | Good repair: uses true/false pattern and asks whether mid should be kept. |
| repair_stress_010 | cp_bridge_002 | check truth direction | rewrite, L3 | pass, L0 | Good repair: asks what true/false means before giving update direction. |
| repair_stress_011 | cp_bridge_018 | heap operation template | rewrite, L3 | pass, L0 | Repair asks too much enumeration; may be a tiring temporary task. |
| repair_stress_012 | cp_bridge_014 | complexity bottleneck | rewrite, L4 | pass, L0 | Good repair: turns completed estimate into a student estimation task. |

## Interpretation

从自动检测看，Repair 可以把显式泄露的关键桥候选回复改成二次 Leakage Judge 可接受的回复。这个结果支持继续研究 Repair，但还不能直接声称 Repair 已经保证教学质量。

原因是：二次 Leakage Judge 只检查是否继续泄露，不等于教练认为回复好。人工自检发现，一些 repaired response 仍有质量风险：

- `repair_stress_001` 仍然替学生推进了部分正序枚举计算；
- `repair_stress_005` 的 micro-example 使用“叶子假装有孩子”，可能增加理解负担；
- `repair_stress_006` 要学生直接写 child lazy/sum 如何变化，接近局部公式补全；
- `repair_stress_007` 通过 relax 形式给了很强的映射线索；
- `repair_stress_011` 要学生列举所有合并顺序，可能从 bridge-oriented micro-example 退化成临时小任务。

因此，本次结果更准确地说明：

> Repair 对“删除显式关键桥泄露”有效，但仍需要教练盲评验证它是否保留了高质量脚手架。

## 下一步

1. 让教练填写 `coach_response_review_workbook_repair_stress_v1_20260511.zh.xlsx`，评价 before/after 的教学质量。
2. 把 Repair prompt 增加一条更强约束：不要替学生完成 worked micro-example 的中间计算。
3. 对 `repair_stress_001`、`repair_stress_005`、`repair_stress_006`、`repair_stress_007`、`repair_stress_011` 加入 regression cases。
4. 扩展到 20-30 条 stress cases，再报告正式 repair stress metrics。
5. 在论文中把本次 12-case 结果称为 smoke，不作为最终主实验。
