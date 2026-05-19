# Real-Student Online Candidate Screening Execution Log 20260519

## 使用边界

本日志记录 real-student online candidate-turn screening 支持文件的当前执行状态。它不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

137 条 candidate turns 是 screening pool，不是 deep annotation sample。30 条 selected cases 是 deep annotation sample，不是全部线上 AIChat 数据。

## 当前状态

| check | status | note |
| --- | --- | --- |
| screening CSV 是否已填满 137 rows | yes | `real_student_online_candidate_screening_form_v1.csv` 已填入 137 条 candidate turns |
| 是否通过 validator | yes | `validate_real_student_candidate_screening.py` 返回 `ok=true`，错误列表为空 |
| selected deep cases 数量 | 30 | 30 rows 标记为 `candidate_for_deep_annotation=yes` |
| 所有 selected rows 是否有 `candidate_selection_reason` | yes | selected rows 的 `candidate_selection_reason` 均非空 |
| 所有 selected rows 隐私状态是否可进入 reporting | yes | selected rows 均为 `privacy_review_status=passed` |
| consent eligibility gate | passed with pending consent | selected rows 均不为 `consent_eligibility=not_eligible`；当前 137 rows 的 consent 状态均为 `pending` |

## Validator Command

```bash
python3 evals/aichat/validate_real_student_candidate_screening.py \
  --input docs/research/real_student_online_candidate_screening_form_v1.csv \
  --schema docs/research/real_student_online_candidate_screening_schema_v1.json \
  --expected-rows 137
```

Current validator result:

```text
passed; expected 137 screening rows, found 137; selected deep candidates = 30; errors = []
```

## Current Screening Summary

| metric | value |
| --- | ---: |
| total screening rows | 137 |
| unique candidate sessions | 59 |
| unique hashed students | 13 |
| unique hashed problems | 25 |
| selected deep candidates | 30 |
| selected rows missing `candidate_selection_reason` | 0 |
| selected rows with privacy status not passed | 0 |
| selected rows with `consent_eligibility=not_eligible` | 0 |

## Summary Command

```bash
python3 evals/aichat/summarize_real_student_candidate_screening.py \
  --input docs/research/real_student_online_candidate_screening_form_v1.csv \
  --output-json docs/research/real_student_candidate_screening_summary_20260519.json \
  --output-md docs/research/real_student_candidate_screening_summary_20260519.zh.md
```

## Reporting Boundary

The candidate-turn screening layer should only be reported as ecological-validity screening support. It must not be written as a deep annotation result, a main result, a learning-outcome study, a dialogue-state v3 table update, or evidence that online AIChat responses were changed.
