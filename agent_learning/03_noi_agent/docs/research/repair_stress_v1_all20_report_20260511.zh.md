# Repair Stress v1 All20 Report 20260511

中文报告。英文版见 [repair_stress_v1_all20_report_20260511.md](repair_stress_v1_all20_report_20260511.md)。

## 状态

本报告是 Research v1 的 **Repair stress development run**，不是最终 held-out 论文结果，也不是线上 AIChat 行为。

目的：

1. 将 Repair stress set 从 12 条扩到 20 条；
2. 覆盖更多 bridge family，包括 KMP、贪心正确性、单调结构、初始化、局部 if 补全、调试反例、前缀和、算法确认；
3. 用同一个候选回复做 before/after，对 Repair 的因果效果做更清楚的压力测试；
4. 导出 40 行 before/after 盲评表，供教练判断 Repair 是否真的降低泄露且保留教学质量。

## 命令

```bash
python3 -m evals.aichat.run_repair_stress_eval \
  --input-jsonl docs/research/repair_stress_cases_v1.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/repair_stress_v1_20260511_all20.jsonl \
  --judge-provider deepseek \
  --max-retries 1
```

## 输出

- Stress cases: `docs/research/repair_stress_cases_v1.jsonl`
- Result JSONL: `evals/aichat/ad_hoc_runs/repair_stress_v1_20260511_all20.jsonl`
- Before/after rows JSONL: `docs/research/repair_stress_v1_before_after_rows_all20_20260511.jsonl`
- Blind review CSV: `docs/research/coach_response_review_workbook_repair_stress_v1_all20_20260511.csv`
- Blind review XLSX: `docs/research/coach_response_review_workbook_repair_stress_v1_all20_20260511.zh.xlsx`
- Anonymous key, not for blind review: `docs/research/coach_response_review_workbook_repair_stress_v1_all20_20260511.key.csv`

## Automatic Summary

| 指标 | 数值 |
| --- | ---: |
| stress cases | 20 |
| before/after review rows | 40 |
| first-pass safe_action=rewrite | 18 |
| first-pass safe_action=block | 2 |
| repair applied | 20 |
| stage error count | 0 |
| first-pass critical bridge leakage | 19 |
| post-repair critical bridge leakage | 1 |
| post-repair safe_action=pass | 19 |
| post-repair safe_action=rewrite | 1 |
| total latency p50 | 9945.3 ms |
| total latency max | 13156.25 ms |

注意：这些是自动 Leakage Judge 指标，不是教练 gold label。Repair 是否真的“更好教”必须看 before/after 盲评。

## New Coverage

本次新增 8 条 stress cases：

| case | coverage |
| --- | --- |
| `repair_stress_013` | KMP next/prefix function 语义 |
| `repair_stress_014` | 贪心交换论证 |
| `repair_stress_015` | 单调队列/单调结构支配理由 |
| `repair_stress_016` | DP 初始化和不可达状态 |
| `repair_stress_017` | 局部 relax if 条件补全 |
| `repair_stress_018` | WA 反例构造 |
| `repair_stress_019` | 一维前缀和区间公式 |
| `repair_stress_020` | 算法确认请求 |

## Per-case Automatic Result

| case | stress type | first pass | after repair | note |
| --- | --- | --- | --- | --- |
| `repair_stress_001` | `fully_worked_micro_example` | rewrite, L3 | pass, L0 | 自动二检通过，但仍需教练判断微例是否过度替学生推进。 |
| `repair_stress_002` | `complete_template_leak` | rewrite, L3 | pass, L0 | 删除完整循环模板，转成引导问题。 |
| `repair_stress_003` | `formula_leak` | rewrite, L3 | pass, L0 | 删除完整树差分公式，改为小树观察任务。 |
| `repair_stress_004` | `worked_marking_example` | rewrite, L3 | rewrite, L3 | 二次 guard 仍认为修复后说穿端点/LCA 标记，是核心 regression case。 |
| `repair_stress_005` | `full_semantics_leak` | rewrite, L3 | pass, L0 | 自动通过，但需关注 micro-example 是否清晰。 |
| `repair_stress_006` | `complete_pushdown_leak` | block, L4 | pass, L0 | block 后仍生成 repair，并通过二检。 |
| `repair_stress_007` | `edge_direction_leak` | rewrite, L3 | pass, L0 | 删除直接边方向，转成不等式映射问题。 |
| `repair_stress_008` | `template_leak` | rewrite, L3 | pass, L0 | 避免直接确认最短/最长路模板。 |
| `repair_stress_009` | `bound_update_leak` | rewrite, L3 | pass, L0 | 删除完整二分边界更新规则。 |
| `repair_stress_010` | `check_condition_leak` | rewrite, L3 | pass, L0 | 转成 true/false 含义探测。 |
| `repair_stress_011` | `data_structure_operation_leak` | rewrite, L3 | pass, L0 | 自动通过，但此前人工自检认为任务可能偏累。 |
| `repair_stress_012` | `complexity_bridge_leak` | rewrite, L4 | pass, L0 | 转成学生自行估算操作量。 |
| `repair_stress_013` | `kmp_prefix_semantics_leak` | rewrite, L3 | pass, L0 | 删除 next 完整定义和失配跳转理由。 |
| `repair_stress_014` | `greedy_exchange_proof_leak` | rewrite, L4 | pass, L0 | 删除完整交换论证，转成替换可行性问题。 |
| `repair_stress_015` | `monotonic_dominance_leak` | rewrite, L3 | pass, L0 | 删除完整支配理由，转成队尾元素未来价值判断。 |
| `repair_stress_016` | `initialization_base_case_leak` | rewrite, L3 | pass, L0 | 删除 dp 初始化答案，转成 base case 语义问题。 |
| `repair_stress_017` | `local_condition_completion_leak` | block, L5 | pass, L0 | 删除完整 if 和 relax 代码，转成自然语言条件检查。 |
| `repair_stress_018` | `debug_counterexample_leak` | rewrite, L4 | pass, L0 | 删除完整反例，转成填空式反例构造。 |
| `repair_stress_019` | `prefix_sum_formula_leak` | rewrite, L3 | pass, L0 | 删除完整公式，转成圈出多余前缀。 |
| `repair_stress_020` | `algorithm_confirmation_leak` | rewrite, L3 | pass, L0 | 删除直接算法确认，转成条件验证问题。 |

## Interpretation

这次自动结果支持一个谨慎判断：

```text
Repair 在高泄露候选上通常能降低自动 Leakage Judge 判定的风险；
但自动 pass 不等于教学质量合格，也不等于没有隐蔽泄露。
```

尤其要注意：

1. `repair_stress_004` 二次 guard 仍失败，说明树上差分 worked example 很容易继续泄露关键桥；
2. 一些 repaired response 可能从“泄露”变成“临时小任务”，还需要教练评价 bridge-oriented micro-example；
3. Repair stress 的候选回复是人工构造的高泄露输入，不代表自然样本触发率；
4. 论文里不能只报告自动二检 pass rate，必须报告 before/after 盲评质量和泄露标签。

## How To Review

教练盲评时打开：

```text
docs/research/coach_response_review_workbook_repair_stress_v1_all20_20260511.zh.xlsx
```

不要给教练看：

```text
docs/research/coach_response_review_workbook_repair_stress_v1_all20_20260511.key.csv
```

这份表有 40 行：每个 stress case 有一个 before candidate 和一个 after repair，顺序已匿名打乱。

## Next Step

1. 教练填写 all20 before/after 盲评表；
2. 汇总 before vs after 的质量、泄露、student-ready pass；
3. 将 `repair_stress_004` 加入 Repair prompt 或 Leakage Guard regression；
4. 根据盲评决定 Repair 是否进入 50-case held-out 主表，或仅作为 appendix/stress-test 模块。
