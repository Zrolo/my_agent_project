# Dialogue-State v3 Main Generation Integrity Record (2026-05-16)

## Conclusion

The dialogue-state v3 reviewed-candidate 50-case set has completed main response generation and integrity repair. The final merged main run contains:

- 50 reviewed-candidate cases;
- 7 main-table conditions;
- 350 case-condition response rows;
- 350 target AI responses exported for blind review;
- no missing pairs;
- no duplicate pairs;
- no empty `final_response_text`;
- no stage warnings.

The generation pack is ready for human coach response blind review. This is not an experimental result and does not imply that any condition has won.

## Main Conditions

The main table is fixed to 7 conditions:

1. `enhanced_prompt_only_clean`
2. `codehelp_codeaid_clean`
3. `dbox_inspired_clean`
4. `dbox_inspired_guard`
5. `bridge_guided_dbox_style_guard`
6. `bridge_contract_compact_guard`
7. `bridge_contract_compact_guard_repair`

These conditions follow the reviewed-candidate response generation plan fixed in `dialogue_state_v3_prompt_rubric_freeze_gate_20260516`.

## Generation And Repair Process

Initial main run directory:

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516/
```

The initial run completed 350 combined rows but produced 11 rows with empty `final_response_text`, so it was not directly usable for blind review. We then used targeted reruns for the affected case-condition pairs and merged the successful retry rows into a new run pack.

Final merged directory:

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/
```

Final integrity checks:

```text
docs/research/dialogue_state_v3_main_merged_integrity_20260516.json
docs/research/dialogue_state_v3_main_merged_integrity_20260516.md
```

Integrity result:

```text
expected_row_count = 350
combined_row_count = 350
final_response_row_count = 350
review_row_count = 350
blocking_reasons = []
warning_reasons = []
analysis_ready = true
headline_ready = true
```

## Deliverables

Main blind-review workbook:

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/coach_response_review_workbook_dev_ablation.zh.xlsx
```

Main by-case blind-review workbook (recommended for coaches):

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/coach_response_review_workbook_dialogue_state_v3_main_by_case_20260516.zh.xlsx
```

Anonymous key:

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/coach_response_review_workbook_dev_ablation.key.csv
```

Full response JSONL:

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/combined_dev_ablation.jsonl
```

Manifest:

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/manifest.json
```

## DBox + Repair Fairness Add-On

To avoid giving Repair only to Bridge Contract variants, we also generated one appendix/sensitivity condition:

```text
dbox_inspired_guard_repair
```

This add-on is not part of the main table. It answers:

```text
If DBox-inspired + Guard also receives Repair, how does its quality/safety trade-off change?
```

Add-on run directory:

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/
```

Add-on integrity result:

```text
expected_row_count = 50
combined_row_count = 50
final_response_row_count = 50
review_row_count = 50
blocking_reasons = []
warning_reasons = []
analysis_ready = true
headline_ready = true
```

Add-on integrity checks:

```text
docs/research/dialogue_state_v3_repair_fairness_addon_integrity_20260516.json
docs/research/dialogue_state_v3_repair_fairness_addon_integrity_20260516.md
```

Add-on by-case blind-review workbook:

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/coach_response_review_workbook_dialogue_state_v3_dbox_repair_addon_by_case_20260516.zh.xlsx
```

## Research Boundary

This record only states:

```text
The reviewed-candidate 50-case main run and the DBox+Repair appendix run are complete enough for blind review.
```

It does not state:

```text
any condition has higher teaching quality;
any condition has less leakage;
Guard / Repair is causally effective;
these results are ready as paper headline claims.
```

Formal claims still require:

1. human coach blind review;
2. partial double annotation;
3. agreement / adjudication;
4. paired analysis;
5. LLM grader calibration;
6. a same-candidate Repair stress test.
