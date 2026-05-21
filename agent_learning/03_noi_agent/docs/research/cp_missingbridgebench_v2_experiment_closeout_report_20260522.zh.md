# CP-MissingBridgeBench v2 实验收尾报告（aggregate）

本报告只汇总 v2 100-case / 700-response 人审实验的 aggregate 结果；不公开学生原文、完整代码、完整 AIChat 回复、真实身份、hash salt 或可逆映射。

- case count: 100
- response rows: 700
- evidence role: v2 benchmark/evaluation closeout; not dialogue-state v3 main result

## 主结果摘要

| design | n | overall | student-ready | safe-ready | major+answer | answer | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Prompt-only | 100 | 3.91 | 64 | 44 | 13 | 3 | 37/55/8 |
| No-direct-solution help | 100 | 3.57 | 50 | 37 | 12 | 2 | 48/50/2 |
| DBox-inspired | 100 | 4.08 | 64 | 51 | 4 | 0 | 66/32/2 |
| DBox-inspired + Guard | 100 | 4.23 | 72 | 54 | 1 | 0 | 69/30/1 |
| Bridge-guided DBox-style + Guard | 100 | 3.7 | 45 | 39 | 5 | 0 | 57/42/1 |
| Bridge Contract + Guard | 100 | 3.82 | 57 | 51 | 6 | 0 | 63/35/2 |
| Bridge Contract + Guard/Repair | 100 | 3.75 | 53 | 45 | 9 | 0 | 58/37/5 |

## 关键配对比较

| comparison | cases | Δ overall | W/T/L | CI95 |
| --- | --- | --- | --- | --- |
| Bridge Contract + Guard - DBox-inspired + Guard | 100 | -0.41 | 18/45/37 | [-0.63, -0.19] |
| Bridge-guided DBox-style + Guard - DBox-inspired + Guard | 100 | -0.53 | 14/45/41 | [-0.76, -0.32] |
| Bridge Contract + Guard/Repair - DBox-inspired + Guard | 100 | -0.48 | 22/37/41 | [-0.74, -0.24] |
| Bridge Contract + Guard/Repair - Bridge Contract + Guard | 100 | -0.07 | 24/45/31 | [-0.36, 0.19] |
| DBox-inspired + Guard - DBox-inspired | 100 | 0.15 | 30/47/23 | [-0.04, 0.35] |
| Prompt-only - DBox-inspired + Guard | 100 | -0.32 | 25/34/41 | [-0.55, -0.11] |
| No-direct-solution help - DBox-inspired + Guard | 100 | -0.66 | 16/35/49 | [-0.9, -0.42] |

## 样本结构摘要

```json
{
  "row_count": 100,
  "context_sufficiency_counts": {
    "sufficient": 100
  },
  "reasoning_focus_counts": {
    "aggregation_contribution_bridge": 8,
    "boundary_order_bridge": 1,
    "correctness_bridge": 2,
    "data_structure_bridge": 13,
    "debugging_bridge": 34,
    "implementation_bridge": 39,
    "policy_bridge": 2,
    "state_representation_bridge": 1
  },
  "help_seeking_context_counts": {
    "code_request": 3,
    "conceptual_hint": 12,
    "debugging": 42,
    "implementation": 43
  }
}
```

## 700 条评审行完整性审计

```json
{
  "source": "computed_from_review_labels",
  "expected": {
    "row_count": 700,
    "case_count": 100,
    "rows_per_case": 7,
    "rows_per_design": 100,
    "designs": [
      "Prompt-only",
      "No-direct-solution help",
      "DBox-inspired",
      "DBox-inspired + Guard",
      "Bridge-guided DBox-style + Guard",
      "Bridge Contract + Guard",
      "Bridge Contract + Guard/Repair"
    ]
  },
  "observed": {
    "row_count": 700,
    "case_count": 100,
    "unique_response_id_count": 700,
    "design_counts_by_label": {
      "Prompt-only": 100,
      "No-direct-solution help": 100,
      "DBox-inspired": 100,
      "DBox-inspired + Guard": 100,
      "Bridge-guided DBox-style + Guard": 100,
      "Bridge Contract + Guard": 100,
      "Bridge Contract + Guard/Repair": 100
    }
  },
  "checks": {
    "labels_rows_present": true,
    "row_count_matches_expected": true,
    "case_count_matches_expected": true,
    "payload_row_count_matches_labels": true,
    "payload_case_count_matches_labels": true,
    "each_design_has_expected_rows": true,
    "each_case_has_expected_rows": true,
    "each_case_has_all_designs": true,
    "no_duplicate_case_design_pairs": true,
    "no_duplicate_response_ids": true,
    "no_missing_required_fields": true,
    "allowed_values_valid": true,
    "numeric_scores_valid": true,
    "no_unexpected_designs": true
  },
  "missing_required_fields": {},
  "missing_score_fields": {},
  "missing_optional_score_fields": {
    "bridge_oriented_micro_example": 280
  },
  "invalid_allowed_values": {},
  "invalid_numeric_scores": {},
  "duplicate_response_id_count": 0,
  "cases_with_wrong_row_count": 0,
  "cases_missing_designs_total": 0,
  "cases_with_duplicate_designs": 0,
  "unexpected_design_count": 0,
  "design_count_mismatches": {},
  "external_validation_summary": null,
  "passed": true
}
```

## 人审可靠性边界

```json
{
  "primary_review_rows": 700,
  "primary_validation_passed": true,
  "completed_rows_missing_required_fields": 0,
  "integrity_audit_summary": {
    "source": "computed_from_review_labels",
    "passed": true,
    "row_count": 700,
    "case_count": 100,
    "unique_response_id_count": 700,
    "duplicate_response_id_count": 0,
    "cases_missing_designs_total": 0,
    "cases_with_duplicate_designs": 0
  },
  "second_review_summary": {
    "interpretation": "Targeted second-review focus selection; reliability support only, not final gold.",
    "overlap_case_count": 30,
    "passed": true,
    "sampled_rows": 210,
    "status": "selection_artifact_present"
  },
  "authority_boundary": "Coach review is treated as expert review evidence, not final gold. Second review or adjudication, when linked, is a bounded reliability check."
}
```

## 解释边界

- v2 closeout 不修改 dialogue-state v3 主结果。
- v2 closeout 不证明线上部署效果或学习效果。
- 如果 DBox-inspired + Guard 在 v2 中领先，应直接报告为强 baseline，而不是改写成 Bridge Contract 方法胜利。
- Bridge Contract / Repair 变体应作为被评估设计和失败分析对象报告，除非结果支持更强 claim。
