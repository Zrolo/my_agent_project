# Real-Student Online 5-Case Dry Run Execution Log 20260519

## 当前状态

| item | status | note |
| --- | --- | --- |
| 5-case dry-run plan created | yes | `real_student_online_5case_dry_run_plan_20260519.zh.md` |
| dry-run form created | yes | `real_student_online_5case_dry_run_form_v1.csv` |
| local-only private annotation packet created | yes | `.local_private/real_student_online_5case_annotation_packet_20260519.*`; ignored by git |
| cases selected from 30 pilot candidate cases | yes | selected by coverage, not model performance |
| raw student text included in public dry-run files | no | only candidate ids and screening labels are included |
| complete deep annotation done | no | pending manual/coach annotation |
| consent/reporting gate complete | no | current status remains pending |
| reportable deep-pilot evidence produced | no | forbidden until consent/status gate is complete |

## Selected Case Coverage

| coverage dimension | included dry-run candidate |
| --- | --- |
| high-confidence debugging | `rs_screen_20260519_001` |
| partial context / unclear family | `rs_screen_20260519_004` |
| aggregation contribution / prefix-difference | `rs_screen_20260519_022` |
| partial implementation boundary | `rs_screen_20260519_028` |
| data-structure / tree anchor | `rs_screen_20260519_032` |

## Boundary Statement

The 5-case dry run is a schema and annotation-guide feasibility check. It is not a new main experiment, not a new condition, not a dialogue-state v3 table update, not a learning-outcome study, and not reportable deep-pilot evidence while consent/status gate remains incomplete.

## Next Manual Step

For each `candidate_turn_id`, use the internal non-public redacted candidate material to fill only paraphrased rubric fields in `real_student_online_5case_dry_run_form_v1.csv`. Do not paste full student messages, full code, full AIChat responses, real identifiers, individual student/problem hash tables, or hash mappings into public research documents.
