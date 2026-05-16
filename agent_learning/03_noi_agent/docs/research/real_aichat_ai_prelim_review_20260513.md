# Real AIChat Student-Only AI Preliminary Review 20260513

This note records an AI preliminary review of the real online AIChat `student-only` v3 candidate workbook. The result is for development screening and coach-review preparation only. It is not coach gold and not an adjudicated reference.

## Inputs And Outputs

Input workbook:

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_candidate_review_33_20260512_v3.zh.xlsx
```

AI preliminary filled workbook:

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_candidate_review_33_20260513_ai_prelim_filled.zh.xlsx
```

Strictly exportable student-only JSONL:

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_ai_prelim_exportable_20260513.jsonl
```

Strict screening report:

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_ai_prelim_strict_screen_20260513.json
```

These files contain real student questions and audit context, so they are not committed to the public repository.

## Review Policy

The AI preliminary review followed these rules:

- treat the output only as preliminary review / development screening;
- use old online AI replies only for contamination audit and legacy-system observation, not as gold;
- generation input for all new tutor conditions must contain only the real current student question and necessary problem metadata;
- cases that become unclear after removing old AI context must not enter main evaluation;
- near-duplicate, contaminated, context-insufficient, privacy-uncertain, or priority-recheck cases must not enter main evaluation;
- `missing_bridge` must describe the transferable reasoning relation the student lacks;
- `forbidden_content` must describe the critical bridge that must not be directly revealed;
- `success_criteria` must describe the next student action a good response should elicit.

## Results

Total candidates: 33.

| Status | Count |
|---|---:|
| Main-evaluation candidate | 8 |
| Dev/regression | 12 |
| Excluded | 13 |

Strict export result:

| Item | Count |
|---|---:|
| accepted_rows | 8 |
| exportable_rows | 8 |
| rejected_rows | 0 |

Category distribution among the 8 exportable rows:

| Category | Count |
|---|---:|
| binary_search_check | 2 |
| graph_tree_modeling | 6 |

Main-evaluation candidate ids:

```text
real_aichat_1
real_aichat_27
real_aichat_987
real_aichat_1293
real_aichat_247
real_aichat_249
real_aichat_827
real_aichat_257
```

Priority human recheck ids:

```text
real_aichat_163
real_aichat_219
real_aichat_981
real_aichat_259
real_aichat_1203
real_aichat_3
real_aichat_65
```

## Strict Gate

The exporter requires each main-evaluation row to satisfy:

- `审查状态=保留主评测`;
- `隐私风险=none`;
- `删除旧AI后是否可理解=yes`;
- `是否自包含=yes`;
- `是否需要补充题面/代码上下文=no`;
- `是否近重复样本=no`;
- `是否代表真实卡点=yes`;
- `是否适合主评测=yes`;
- `需重点复判=no`;
- `旧AI上下文污染初筛` must be `none` or `low`;
- `missing_bridge`, `forbidden_content`, and `success_criteria` must be non-empty.

Schema checks confirmed that the 8 exported rows satisfy:

- `generation_input.recent_dialogue=""`;
- `generation_input.context_ai_reply=""`;
- `generation_input.student_code_excerpt=""`;
- old AI context is retained only under `audit_context`;
- `observed_current_system_response` is legacy-system observation only, not gold.

## Interpretation Boundary

These 8 real-log rows should be treated only as a `real-log pilot subset` or development realism check, not as a complete held-out main result:

- the category distribution is skewed toward binary search and graph/tree cases;
- most debug, implementation, DP, data-structure, and greedy real-log rows were moved to dev or excluded due to context insufficiency, near-duplication, or old-AI contamination;
- labels are AI-preliminary and require human coach confirmation before becoming reference labels;
- even rows passing the strict gate still need a human anonymization spot check before public use.

Recommended paper wording:

> We additionally screened real online AIChat student questions as a small student-only pilot subset. Historical AI replies were removed from generation inputs and retained only for audit. Because the preliminary labels were AI-assisted and the resulting subset was category-skewed, these cases are used for development and realism checks rather than headline held-out claims.

Chinese wording:

> 我们额外筛选真实线上 AIChat 学生提问，形成一个 student-only pilot 子集。历史 AI 回复从生成输入中移除，只用于审计。由于当前标签为 AI 辅助预标注，且可导出样本类别偏斜，这些样本只用于开发阶段真实感检查，不作为 headline held-out 结论。

## Next Steps

1. Ask a human coach to verify the 8 main-evaluation candidates;
2. decide whether the 7 priority-recheck rows can become dev cases after context supplementation;
3. do not promote these 8 rows to headline paper results;
4. if a real-log held-out subset is needed, collect more DP, data-structure, implementation/debug, and greedy rows and apply the same student-only strict gate.
