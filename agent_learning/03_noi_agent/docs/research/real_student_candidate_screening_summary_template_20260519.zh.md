# Real-Student Online Candidate-Turn Screening Summary Template 20260519

## 模板用途

本模板定义 `evals/aichat/summarize_real_student_candidate_screening.py` 生成正式中文 summary report 时应包含的字段和边界。生成报告的默认输出为：

- `docs/research/real_student_candidate_screening_summary_20260519.json`
- `docs/research/real_student_candidate_screening_summary_20260519.zh.md`

## 使用边界

本 summary 只汇总 137 条 real-student online AIChat substantial candidate turns 的轻量筛查结果。它不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

137 条 candidate turns 是 screening pool，不是 deep annotation sample。30 条 selected cases 是 deep annotation sample，不是全部线上 AIChat 数据。筛查结果只能作为 ecological validity 的数据漏斗和抽样说明，可放入 Discussion / Appendix，不能作为 main result。

## Script Command

```bash
python3 evals/aichat/summarize_real_student_candidate_screening.py \
  --input docs/research/real_student_online_candidate_screening_form_v1.csv \
  --output-json docs/research/real_student_candidate_screening_summary_20260519.json \
  --output-md docs/research/real_student_candidate_screening_summary_20260519.zh.md
```

## Required Report Sections

### Data Funnel

The generated report must include:

- raw AIChat message rows: 1156
- sessions: 87
- paired user-assistant turns: 578
- expected substantial candidate turns: 137
- actual screening rows in CSV
- selected deep candidates in CSV

### Coverage Summary

The generated report must include:

- total rows
- unique sessions
- unique students
- unique problems
- selected deep candidates count

### Screening Counts

The generated report must include counts for:

- `context_sufficiency`
- `rough_bridge_family`
- `surface_anchor`
- `help_seeking_type`
- `likely_slice`
- `candidate_for_deep_annotation`
- `exclusion_reason`
- `privacy_review_status`
- `consent_eligibility`

### Selected Deep Candidate Breakdown

The generated report must include selected deep candidates by:

- `rough_bridge_family`
- `surface_anchor`
- `student_id_hash`
- `problem_id_hash`

## Required Boundary Sentence

The generated report must include the following interpretation boundary:

```text
The 137 substantial candidate turns form a lightweight screening pool. They are used to describe the availability and diversity of real-student online AIChat dialogue-state candidates, not to report deep rubric annotations. The selected deep cases are chosen from this pool for privacy-reviewed case-specific annotation and are not the full online corpus.
```

## Claim Gate

| statement | allowed? | note |
| --- | --- | --- |
| The online AIChat logs provide a screening pool of 137 substantial candidate turns. | yes | Data funnel only |
| The screening pool helps select 30 deep pilot cases. | yes | Use stratified purposive sampling language |
| The 137 candidate turns are deeply annotated. | no | Forbidden |
| The 30 selected cases are all online AIChat data. | no | Forbidden |
| The pilot is a learning outcome study. | no | Forbidden |
| The pilot modifies dialogue-state v3 main results. | no | Forbidden |
