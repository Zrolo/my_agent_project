# Real-Student Online Candidate-Turn Screening Summary 20260519

## 使用边界

本报告汇总 real-student online AIChat candidate-turn screening CSV 的轻量筛查统计。它不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

137 条 candidate turns 是 screening pool，不是 deep annotation sample。30 条 selected cases 是 pending consent/reporting gate 的 pilot candidate cases，不是全部线上 AIChat 数据，也不能在 consent/reporting gate 完成前写成可公开报告的 deep-pilot evidence。本报告只能作为 ecological validity 的数据漏斗和抽样说明，可放入 Discussion / Appendix，不能作为 main result。

## Data Funnel

| layer | unit | count | boundary |
| --- | --- | ---: | --- |
| Online log corpus summary | raw AIChat message rows | 1156 | source-corpus background only |
| Online log corpus summary | sessions | 87 | source-corpus background only |
| Online log corpus summary | paired user-assistant turns | 578 | source-corpus background only |
| Candidate-turn screening | expected substantial candidate turns | 137 | lightweight screening pool |
| Candidate-turn screening | actual screening rows in CSV | 137 | generated from screening form |
| Deep pilot candidate selection | selected pilot candidate cases in CSV | 30 | selected for possible deep annotation; reporting waits for consent/status gate |

## Coverage Summary

| metric | value |
| --- | ---: |
| total rows | 137 |
| unique sessions | 59 |
| unique students | 13 |
| unique problems | 25 |
| selected pilot candidate cases pending consent/reporting gate | 30 |
| selected reportable after consent/status gate | 0 |

## Context Sufficiency Counts

| context_sufficiency | count |
| --- | ---: |
| `sufficient` | 118 |
| `partial` | 19 |

## Rough Bridge Family Counts

| rough_bridge_family | count |
| --- | ---: |
| `implementation_bridge` | 45 |
| `debugging_bridge` | 42 |
| `unclear` | 18 |
| `data_structure_bridge` | 14 |
| `aggregation_contribution_bridge` | 9 |
| `predicate_check_bridge` | 3 |
| `correctness_bridge` | 2 |
| `policy_bridge` | 2 |
| `boundary_order_bridge` | 1 |
| `state_representation_bridge` | 1 |

## Surface Anchor Counts

| surface_anchor | count |
| --- | ---: |
| `implementation boundary` | 45 |
| `debugging trace` | 42 |
| `conceptual hint request` | 17 |
| `tree / graph traversal` | 10 |
| `prefix/difference contribution` | 9 |
| `data-structure operation` | 4 |
| `binary-search check` | 3 |
| `correctness / invariant reasoning` | 2 |
| `direct-answer / code request` | 2 |
| `DP state` | 1 |
| `boundary update order` | 1 |
| `insufficient-context help seeking` | 1 |

## Help-Seeking Type Counts

| help_seeking_type | count |
| --- | ---: |
| `debugging` | 50 |
| `implementation` | 49 |
| `conceptual_hint` | 34 |
| `code_request` | 3 |
| `clarification` | 1 |

## Likely Slice Counts

| likely_slice | count |
| --- | ---: |
| `main_scaffold_eval` | 96 |
| `main_eval_with_caution` | 37 |
| `policy_safety_slice` | 3 |
| `clarification_safety_slice` | 1 |

## Candidate For Deep Annotation Counts

| candidate_for_deep_annotation | count |
| --- | ---: |
| `no` | 107 |
| `yes` | 30 |

## Exclusion Reason Counts

| exclusion_reason | count |
| --- | ---: |
| `not_selected_for_30_case_deep_sample` | 107 |
| `(blank)` | 30 |

## Privacy Review Status Counts

| privacy_review_status | count |
| --- | ---: |
| `pending` | 107 |
| `passed` | 30 |

## Consent Eligibility Counts

| consent_eligibility | count |
| --- | ---: |
| `pending` | 137 |

## Selected Pilot Candidate Cases By Bridge Family

| rough_bridge_family | count |
| --- | ---: |
| `implementation_bridge` | 12 |
| `debugging_bridge` | 10 |
| `data_structure_bridge` | 3 |
| `unclear` | 3 |
| `aggregation_contribution_bridge` | 2 |

## Selected Pilot Candidate Cases By Surface Anchor

| surface_anchor | count |
| --- | ---: |
| `implementation boundary` | 12 |
| `debugging trace` | 10 |
| `conceptual hint request` | 3 |
| `prefix/difference contribution` | 2 |
| `tree / graph traversal` | 2 |
| `data-structure operation` | 1 |

## Selected Pilot Candidate Student Coverage

| coverage field | value |
| --- | ---: |
| unique hashed students covered | 11 |
| min cases per hashed students | 1 |
| median cases per hashed students | 3 |
| max cases per hashed students | 5 |
| count distribution | 1 cases: 3 ids, 2 cases: 2 ids, 3 cases: 2 ids, 4 cases: 3 ids, 5 cases: 1 ids |

## Selected Pilot Candidate Problem Coverage

| coverage field | value |
| --- | ---: |
| unique hashed problems covered | 15 |
| min cases per hashed problems | 1 |
| median cases per hashed problems | 1 |
| max cases per hashed problems | 7 |
| count distribution | 1 cases: 8 ids, 2 cases: 5 ids, 5 cases: 1 ids, 7 cases: 1 ids |

## Interpretation Boundary

The 137 substantial candidate turns form a lightweight screening pool. They are used to describe the availability and diversity of real-student online AIChat dialogue-state candidates, not to report deep rubric annotations. The 30 selected pilot candidate cases are chosen from this pool for possible case-specific annotation and are not the full online corpus. They are not reportable deep-pilot evidence until consent/reporting eligibility is completed. Public-facing reporting should use aggregate coverage and distribution summaries rather than individual student or problem hash tables.
