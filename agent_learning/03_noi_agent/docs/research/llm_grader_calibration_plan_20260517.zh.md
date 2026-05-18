# LLM Grader Calibration Plan (20260517)

## 目标

验证 LLM grader 是否能作为 scalable auxiliary grader，而不是替代人类教练。核心问题是 case-specific bridge rubric judge 是否比 generic rubric / likert-only 更接近 adjudicated labels。

## 待比较 grader

| grader | 输入 | 预期作用 |
| --- | --- | --- |
| `likert_only_judge` | response + coarse Likert rubric | 检查单纯评分量表是否足够 |
| `generic_rubric_judge` | response + 通用辅导 rubric | 检查非 case-specific 评审能力 |
| `case_specific_bridge_rubric_judge` | response + success criteria / forbidden content / critical boundary / acceptable reveal | 检查 MissingBridgeBench 的 case-specific 信息是否提升一致性 |

## 参考标签

1. `priority60_adjudicated_labels`：只评估被裁决的高分歧行，最接近高风险 gold，但 N 小且偏难。
2. `priority60_adjudicated_plus_coachA`：主论文分析口径。
3. `priority60_adjudicated_plus_coachB`：rater-strictness sensitivity。
4. 可选：Coach A only / Coach B only，用于估计 grader 是否过拟合某一位教练口径。

## 指标

- critical binary precision / recall / F1。
- major leakage false negative rate：人类 major/answer，但 grader 判非 critical 的比例。
- student-ready agreement：二值 ready 一致率与 Cohen kappa。
- safe-ready agreement：ready 且非 major/answer 的一致率。
- overall correlation：Spearman / Kendall；同时报告 mean absolute error。
- calibration slices：main_scaffold_eval、clarification_safety_slice、policy_safety_slice 分开报告。

## 最小输出

- `llm_grader_calibration_results_20260517.csv`：逐 row 人类标签 + 三个 grader 预测。
- `llm_grader_calibration_report_20260517.zh.md/.md`：指标表、错误样例、false-negative 分析。

## 论文写法

可以写：case-specific bridge rubric judge 更接近 coach-adjudicated labels，但仍只作为 scalable auxiliary grader。不要写：LLM Judge 可替代人类人审或 priority60 已足以训练/验证最终自动评测。
