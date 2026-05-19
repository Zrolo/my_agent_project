# Submission Draft Skeleton: Dialogue-State v3 20260519

## Scope

This is a submission-prep manuscript skeleton, not a final paper. It provides section-level writing goals, available evidence, allowed claims, forbidden claims, and human-author work items. It adds no experiments and changes no results.

## 1. Abstract

- Writing goal: State the evaluation problem, benchmark contribution, human-review setup, and bounded findings in one restrained paragraph.
- Current evidence: 50 reviewed cases, 7 conditions, 350 responses, double coach review, priority60 adjudication, paired uncertainty, stress / sensitivity / calibration reports.
- Allowed claim: CP-MissingBridgeBench reveals quality-safety-burden trade-offs in turn-level CP tutoring.
- Forbidden claim: One tutor harness fully solves CP tutoring or significantly dominates all baselines.
- Human work: Finalize word count, venue style, and whether to include numeric highlights.

## 2. Introduction

- Writing goal: Motivate missing bridge and critical bridge leakage as safety/learning failures that remain after no-direct-answer rules.
- Current evidence: Task definition docs, result tables, no-direct-solution baseline behavior.
- Allowed claim: No-direct-code / no-direct-solution prompting does not eliminate critical bridge leakage.
- Forbidden claim: Existing tutoring systems are weak strawmen or solved by this work.
- Human work: Add verified citations and a concise motivating example.

## 3. Related Work

- Writing goal: Position against AI tutoring, programming-help assistants, DBox-inspired decomposition, LLM-as-judge, and agent-eval methodology.
- Current evidence: Citation checklist and candidate citation IDs.
- Allowed claim: Prior work motivates baselines and evaluation dimensions.
- Forbidden claim: We faithfully reproduce DBox, CodeHelp, CodeAid, EDF/Copa, or any related system unless settings are matched.
- Human work: Open every cited source, verify BibTeX, and update `citation_verification_log.csv`.

## 4. Task Definition: Missing Bridge and Critical Bridge Leakage

- Writing goal: Define missing bridge, critical bridge leakage, acceptable reveal, forbidden content, and expected student next action.
- Current evidence: `evaluation_protocol_v3`, `response_review_rubric_v3`, taxonomy revision summary.
- Allowed claim: Critical bridge leakage can occur without direct code or full solution leakage.
- Forbidden claim: The taxonomy is universal or complete for all CP tutoring.
- Human work: Polish definitions and include one non-sensitive example.

## 5. CP-MissingBridgeBench / Dialogue-State v3

- Writing goal: Describe the 50-case dialogue-state v3 evidence candidate, slice structure, and case-specific rubric workflow.
- Current evidence: reviewed candidate JSONL, context readiness audit, paper table source.
- Allowed claim: The main headline uses the 31-case `main_scaffold_eval` slice.
- Forbidden claim: all 50 cases are the headline or full CP tutoring coverage.
- Human work: Decide how much dataset detail belongs in main text versus appendix.

## 6. Systems and Baselines

- Writing goal: Explain the 7 offline human-review harnesses and their interpretation boundaries.
- Current evidence: baseline protocol, methods/evaluation draft, table source.
- Allowed claim: DBox-inspired decomposition is a strong baseline; Guard-only variants are guard-instrumented.
- Forbidden claim: Guard-only rewrites final output; DBox-inspired is a faithful DBox reproduction.
- Human work: Shorten condition descriptions for the main paper table.

## 7. Human Review Protocol

- Writing goal: Explain blind review, Coach A/B full scoring, priority60 adjudication, agreement, and sensitivity reporting.
- Current evidence: human-review result packet, reliability draft, agreement report.
- Allowed claim: Human review and adjudication remain necessary.
- Forbidden claim: Coach A, Coach B, or priority60 is final gold.
- Human work: Decide whether agreement metrics live in main text or appendix.

## 8. Main Results

- Writing goal: Present main scaffold table, paired W/T/L, uncertainty, and slice sensitivity.
- Current evidence: paper-ready tables, pairwise report, reproduction JSON, table source.
- Allowed claim: Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary view.
- Forbidden claim: significant dominance, stable advantage, or comprehensive superiority over all baselines.
- Human work: Convert markdown tables to venue-ready tables and verify every number against `result_number_verification_log.csv`.

## 9. Repair Same-Candidate Stress Test

- Writing goal: Separate Repair causality evidence from main-condition means.
- Current evidence: repair same-candidate stress result and workbook summary.
- Allowed claim: Repair reduced leakage severity in fixed-candidate stress testing, with student-burden trade-off.
- Forbidden claim: Repair causality is proven by main experiment means or fully solves leakage.
- Human work: Choose whether stress-test details are main text or appendix.

## 10. DBox+Repair Fairness Sensitivity

- Writing goal: Address the fairness question of adding Repair to a DBox-inspired baseline without promoting it to main condition.
- Current evidence: 20-case targeted DBox+Repair fairness report.
- Allowed claim: DBox+Repair is targeted fairness sensitivity.
- Forbidden claim: It is a full 50-case double-coach main validation.
- Human work: Put this in appendix unless page budget allows a short sensitivity paragraph.

## 11. LLM Grader Calibration

- Writing goal: Show why LLM graders are auxiliary only and why human review remains necessary.
- Current evidence: DeepSeek calibration report and reproduced key metrics.
- Allowed claim: Case-specific LLM grader may provide auxiliary low-stakes signals but cannot replace coaches.
- Forbidden claim: LLM grader is gold or can adjudicate critical leakage alone.
- Human work: Cite LLM-as-judge work, report critical false-negative risk clearly, and state that the DeepSeek calibration is backend-coupled rather than cross-backend validation. Cross-backend GPT-5.4 calibration belongs in future work or a revision add-on.

## 12. Discussion

- Writing goal: Interpret the benchmark as an evaluation framework and trade-off analysis.
- Current evidence: results/discussion draft, claim gate, observed taxonomy.
- Allowed claim: The evidence supports bounded trends and methodological lessons.
- Forbidden claim: System victory, universal benchmark coverage, or product deployment validation.
- Human work: Add implications for CP tutoring research and benchmark design.

## 13. Limitations

- Writing goal: State limitations visibly and concretely.
- Current evidence: reliability report, slice analysis, DBox+Repair sensitivity, LLM grader calibration.
- Allowed claim: Rater sensitivity, 50-case coverage, targeted add-ons, and automatic-grader limitations remain.
- Forbidden claim: Limitations are minor or irrelevant to the main interpretation.
- Human work: Tune wording for the target venue.

## 14. Ethics, Data Governance, and AI Writing Disclosure

- Writing goal: Explain data boundaries, human-review responsibility, and AI writing assistance.
- Current evidence: AI writing disclosure log, human revision checklist, citation/result verification logs.
- Allowed claim: AI assisted drafting/editing/checklist generation; humans verified claims and take responsibility.
- Forbidden claim: AI is an author or a source of scientific evidence.
- Human work: Adapt disclosure to venue policy and verify privacy/data statements.
