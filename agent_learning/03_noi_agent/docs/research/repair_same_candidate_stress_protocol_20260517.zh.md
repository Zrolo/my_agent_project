# Repair Same-Candidate Stress Protocol 20260517

## 研究问题

主实验显示 `bridge_contract_compact_guard_repair` condition 表现最好，但这不能单独证明 Repair 的因果效果。原因是：

1. Repair 只在部分样本触发；
2. 不同 condition 的 candidate 本来就不同；
3. 主表比较的是 condition-level pipeline，而不是同一个 candidate 的 before/after。

因此需要 same-candidate before/after stress test：固定同一条原始 candidate，比较 repair 前与 repair 后的学生可见回复。

## 三层 sample set

### A. Natural repair set

来自主实验和 DBox repair add-on 中真实触发 Repair 的行。当前已有候选：

| source_condition | count |
| --- | ---: |
| `bridge_contract_compact_guard_repair` | 13 |
| `dbox_inspired_guard_repair` | 17 |

用途：回答真实生成分布下，Repair 对已触发样本的泄露、质量和负担影响。

### B. Taxonomy-stratified risk set

从 observed error taxonomy 中分层抽样，不按 DP/二分/lazy/代码这些 surface anchors 直接配额，而按：

```text
leakage mechanism × cognitive bridge family × surface anchor
```

建议每个主要机制 2-4 条，总数 20-30 条。机制覆盖：

- direct bridge completion；
- answer-slot compression；
- worked-trace completion；
- local implementation completion；
- proof / invariant completion；
- decision-rule completion；
- debugging diagnosis completion；
- modeling-plan completion；
- over-constrained scaffold。

### C. Adversarial challenge set

可选补充压力测试，10-15 条极端泄露候选，例如完整状态定义、完整转移、完整 check、完整边界更新、完整局部代码、fully worked micro-example。该集合只能作为 adversarial appendix，不作为真实生成分布主结论。

## 当前已生成候选包

当前仓库已有 natural repair set 的 30-row template：

- CSV：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/repair_same_candidate_stress_candidate_list_20260517.csv`
- XLSX：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/repair_same_candidate_stress_workbook_template_20260517.xlsx`
- 盲评工作簿：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/repair_same_candidate_stress_blind_review_workbook_20260517.zh.xlsx`
- 盲化 key：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/repair_same_candidate_stress_blind_review_key_20260517.csv`

盲评工作簿只显示 Response A / Response B，不包含 `source_condition`、`before_repair` / `after_repair` 映射、original / repair 字段名。key 单独保存，供汇总脚本在评审结束后还原 before/after delta。

覆盖 bridge buckets：

| bridge_bucket | count |
| --- | ---: |
| `predicate_check_semantics` | 4 |
| `modeling_object_relation` | 3 |
| `aggregation_contribution_summary` | 5 |
| `data_structure_operation_semantics` | 5 |
| `transition_recurrence_source` | 3 |
| `correctness_invariant` | 2 |
| `implementation_boundary` | 1 |
| `state_representation_semantics` | 4 |
| `boundary_update_order` | 2 |
| `policy_request` | 1 |

## 固定 protocol

| item | fixed rule |
| --- | --- |
| sample pool | 不根据 repair 结果删除样本；所有触发 Repair 的 natural rows 都保留，除非字段缺失导致无法评分 |
| eligibility | 必须有 original candidate、repair output、case-specific rubric、student message |
| random seed | `20260517` |
| stratification | 先按 leakage mechanism × cognitive bridge family，surface anchor 只作为解释层 |
| blinding | 不向教练展示 before/after、source condition 或 repair status；随机显示为 Response A / Response B |
| review unit | 同一 case 下的两个回复独立评分，再汇总 pair-level delta |
| deletion rule | 不允许因 repair 后仍泄露、太弱或质量差而事后删除样本 |

## 评审字段

before 与 after 均需评分：

- overall quality；
- would show to student；
- leakage label；
- student response burden；
- notes。

after 额外标记：

- `after_too_vague`：repair 后是否变得过于空泛；
- `still_leaks`：repair 后是否仍为 major / answer leakage。

## 指标

| metric | definition |
| --- | --- |
| leakage delta | after leakage severity - before leakage severity；负数代表改善 |
| overall quality delta | after overall - before overall |
| student burden delta | after burden - before burden |
| student-ready / safe-ready delta | after pass - before pass |
| still-leaks rate | after 仍为 major / answer 的比例 |
| too-vague-after-repair rate | after 被标为 too vague 的比例 |
| repair win/tie/loss | 按 pair-level overall 或综合偏好计数 |

## Supporting scripts

新增离线脚本：

- `evals/aichat/build_repair_same_candidate_stress_workbook.py`：从已有 generation JSONL 重建 same-candidate review template。
- `evals/aichat/build_repair_same_candidate_blind_review_workbook.py`：将 candidate list 随机盲化为 Response A / Response B，并输出单独 key。
- `evals/aichat/summarize_repair_same_candidate_stress.py`：在教练填完 before/after 后汇总 leakage / quality / burden delta。

这两个脚本不调用模型、不改 prompt、不改线上系统。

## 论文解释

在该 stress test 完成前，只能写：

```text
The repair-enabled Bridge Contract condition performs best in the current condition-level human-review evidence.
```

完成 same-candidate stress test 后，若结果支持，才可以写：

```text
Under same-candidate stress testing, Repair reduces leakage with measurable quality/burden trade-offs.
```

不能写：

```text
Repair's causal effect is proven by the main experiment.
```
