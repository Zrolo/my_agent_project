# GPT-5.4 External Method Review: LLM Grader Coupling 20260519

## 使用边界

本文档记录 GPT-5.4 子线程对 dialogue-state v3 LLM-grader wording 的方法审查。它是 reviewer-facing process audit，不是实验结果、grader calibration run 或模型比较。

## Verdict

```text
needs minor revision
```

审查结论是：当前 evidence package 已经正确地把 DeepSeek-backed LLM grader calibration 写成 auxiliary / limitation evidence，而不是 main result。主结果仍然基于 Coach A / Coach B 人类评审和 priority adjudication。

## Main Risk

审查指出一个 wording 风险：same-backend coupling 需要正面写出。Tutor generation、Bridge Judge / Leakage Guard 和 Repair 都位于固定的 DeepSeek-family offline stack 中。因此，DeepSeek-backed grader calibration 不应被解释为 cross-backend validation，也不应被解释为独立的人类评审替代。

## Implemented Wording Fixes

- 在 DeepSeek LLM grader calibration report 中新增 backend-coupling boundary。
- 将 `scalable triage` 降级为 auxiliary low-stakes / auxiliary signal wording。
- 明确 cross-backend grader calibration，包括 GPT-5.4-backed grading，是 future work 或 revision add-on。
- 明确 GPT-5.4 external audit 只能作为 method review / reproducibility audit，不能作为实验结果。

## Safe Wording

```text
本文将 DeepSeek-backed LLM grader calibration 仅作为辅助证据报告。由于 tutor generation、judge/guard 与 repair 都位于固定的 DeepSeek-family offline stack 中，该 calibration 存在 backend coupling，不应被解释为 cross-backend validation。论文主结论依赖双教练人审与 priority adjudication，而不是自动评分。跨后端 grader calibration，包括 GPT-5.4-backed grading，应作为 future work 或 revision add-on。
```

## Forbidden Interpretation

不要写：

- GPT-5.4 subagent review 是实验性 LLM-grader calibration。
- GPT-5.4 替代了 DeepSeek calibration。
- DeepSeek calibration 是 cross-backend validation。
- 任何 LLM grader 可以替代 Coach A / Coach B 人类评审。
