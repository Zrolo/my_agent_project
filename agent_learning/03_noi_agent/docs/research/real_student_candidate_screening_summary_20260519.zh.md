# Real-Student Online Candidate-Turn Screening Summary 20260519

## 使用边界

本报告汇总 real-student online AIChat candidate-turn screening CSV 的轻量筛查统计。它不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

137 条 candidate turns 是 screening pool，不是 deep annotation sample。30 条 selected cases 是 deep annotation sample，不是全部线上 AIChat 数据。本报告只能作为 ecological validity 的数据漏斗和抽样说明，可放入 Discussion / Appendix，不能作为 main result。

## Data Funnel

| layer | unit | count | boundary |
| --- | --- | ---: | --- |
| Online log corpus summary | raw AIChat message rows | 1156 | source-corpus background only |
| Online log corpus summary | sessions | 87 | source-corpus background only |
| Online log corpus summary | paired user-assistant turns | 578 | source-corpus background only |
| Candidate-turn screening | expected substantial candidate turns | 137 | lightweight screening pool |
| Candidate-turn screening | actual screening rows in CSV | 137 | generated from screening form |
| Deep pilot annotation | selected deep candidates in CSV | 30 | complete annotation only after privacy review |

## Coverage Summary

| metric | value |
| --- | ---: |
| total rows | 137 |
| unique sessions | 59 |
| unique students | 13 |
| unique problems | 25 |
| selected deep candidates count | 30 |

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

## Selected Deep Candidates By Bridge Family

| rough_bridge_family | count |
| --- | ---: |
| `implementation_bridge` | 12 |
| `debugging_bridge` | 10 |
| `data_structure_bridge` | 3 |
| `unclear` | 3 |
| `aggregation_contribution_bridge` | 2 |

## Selected Deep Candidates By Surface Anchor

| surface_anchor | count |
| --- | ---: |
| `implementation boundary` | 12 |
| `debugging trace` | 10 |
| `conceptual hint request` | 3 |
| `prefix/difference contribution` | 2 |
| `tree / graph traversal` | 2 |
| `data-structure operation` | 1 |

## Selected Deep Candidates By Student

| student_id_hash | count |
| --- | ---: |
| `stu_925ad19bad497ce0` | 5 |
| `stu_9589f185858ab7f4` | 4 |
| `stu_d8240700d7b4a573` | 4 |
| `stu_e8d61ca1e8d38a6d` | 4 |
| `stu_2874c3bc5292937e` | 3 |
| `stu_4b2d444c6851750d` | 3 |
| `stu_a449c196f0b55660` | 2 |
| `stu_b531e3ef57c1904a` | 2 |
| `stu_05c8a0464f305ce6` | 1 |
| `stu_28310c7c6f47decf` | 1 |
| `stu_fdff3e566a4a4271` | 1 |

## Selected Deep Candidates By Problem

| problem_id_hash | count |
| --- | ---: |
| `prob_3b5a682d7bb8c38a` | 7 |
| `prob_ff5e477452170911` | 5 |
| `prob_0a1afc175b781068` | 2 |
| `prob_19d6a797891845ab` | 2 |
| `prob_b8897aede85aa2a0` | 2 |
| `prob_e5ce6c02c6a4ab64` | 2 |
| `prob_e893e49d29d156d7` | 2 |
| `prob_068410236aed77d1` | 1 |
| `prob_08af834e8fc24af1` | 1 |
| `prob_36845b05fe98edf2` | 1 |
| `prob_4f29cdd992363857` | 1 |
| `prob_9177928a1c886d3d` | 1 |
| `prob_a0bf3fe990f7682a` | 1 |
| `prob_b807a713f7bfb63b` | 1 |
| `prob_d115d0e01d0a0f4f` | 1 |

## Interpretation Boundary

The 137 substantial candidate turns form a lightweight screening pool. They are used to describe the availability and diversity of real-student online AIChat dialogue-state candidates, not to report deep rubric annotations. The selected deep cases are chosen from this pool for privacy-reviewed case-specific annotation and are not the full online corpus.
