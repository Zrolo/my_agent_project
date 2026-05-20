# Real-AIChat-100 Selection Log 20260520

## 使用边界

本日志记录从 137 条 real-student online AIChat candidate-turn screening pool 中生成 Real-AIChat-100 observational validation manifest 的选择结果。它不修改 dialogue-state v3 主实验，不新增 main experiment condition，不重算主表，不调用线上 AIChat，不生成 Replay responses，也不评估 learning outcome。

公开 manifest 不包含学生原文、完整代码、完整 AIChat 回复、真实身份、hash salt、可逆映射或 row-level hash 表。`observed_current_aichat_response` 只表示线上已展示回复的观察项，非实验条件。

## Selection Summary

| field | value |
| --- | ---: |
| source screening rows | 137 |
| eligible screening rows | 137 |
| target count | 100 |
| selected manifest rows | 100 |
| selected unique sessions | 59 |
| selected unique students | 13 |
| selected unique problems | 25 |

## Selection Rule

选择规则为 deterministic stratified purposive sampling：先保留现有 30 条 selected pilot candidate cases，再覆盖 rough bridge family、surface anchor、help-seeking type、likely slice、context sufficiency、student、problem 和 session，最后用低集中度优先的确定性排序补足到目标数量。选择不依据 observed AIChat response 好坏，不依据是否支持 Bridge Contract / Repair，也不依据是否支持论文主结论。

### Context Sufficiency Counts

| value | count |
| --- | ---: |
| `partial` | 16 |
| `sufficient` | 84 |

### Rough Bridge Family Counts

| value | count |
| --- | ---: |
| `aggregation_contribution_bridge` | 7 |
| `boundary_order_bridge` | 1 |
| `correctness_bridge` | 2 |
| `data_structure_bridge` | 13 |
| `debugging_bridge` | 26 |
| `implementation_bridge` | 29 |
| `policy_bridge` | 2 |
| `predicate_check_bridge` | 3 |
| `state_representation_bridge` | 1 |
| `unclear` | 16 |

### Surface Anchor Counts

| value | count |
| --- | ---: |
| `DP state` | 1 |
| `binary-search check` | 3 |
| `boundary update order` | 1 |
| `conceptual hint request` | 15 |
| `correctness / invariant reasoning` | 2 |
| `data-structure operation` | 4 |
| `debugging trace` | 26 |
| `direct-answer / code request` | 2 |
| `implementation boundary` | 29 |
| `insufficient-context help seeking` | 1 |
| `prefix/difference contribution` | 7 |
| `tree / graph traversal` | 9 |

### Help-Seeking Type Counts

| value | count |
| --- | ---: |
| `clarification` | 1 |
| `code_request` | 3 |
| `conceptual_hint` | 29 |
| `debugging` | 34 |
| `implementation` | 33 |

### Likely Slice Counts

| value | count |
| --- | ---: |
| `clarification_safety_slice` | 1 |
| `main_eval_with_caution` | 25 |
| `main_scaffold_eval` | 71 |
| `policy_safety_slice` | 3 |

### Privacy Review Status Counts

| value | count |
| --- | ---: |
| `passed` | 30 |
| `pending` | 70 |

### Consent Eligibility Counts

| value | count |
| --- | ---: |
| `pending` | 100 |

### Candidate For Replay Counts

| value | count |
| --- | ---: |
| `no` | 16 |
| `yes` | 84 |

### Public Reporting Allowed Counts

| value | count |
| --- | ---: |
| `no` | 100 |

## Reporting Boundary

- Real-AIChat-100 is observational ecological-validity validation only.
- It is not a 7-harness condition-comparison experiment.
- It is not a main result and does not update dialogue-state v3 tables.
- Consent/reporting gate is pending for the selected rows, so public reporting is limited to aggregate/process counts.
- Replay candidates are only candidates; no Replay-30/50 generation or coach review is created by this selection step.
