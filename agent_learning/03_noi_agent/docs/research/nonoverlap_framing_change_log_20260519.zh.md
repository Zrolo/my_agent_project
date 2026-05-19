# Nonoverlap Framing Change Log 20260519

## 输出文件

- `docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_1.zh.md`

## 与 final-answer / adversarial-attack leakage 工作的区分

- 标题改为 `CP-MissingBridgeBench: Evaluating Critical-Bridge Leakage in LLM Tutors for Competitive Programming`，把研究对象固定在 critical-bridge leakage 和 competitive-programming tutoring。
- Abstract 明确说明邻近 tutor-leakage 工作主要关注 final-answer / complete-solution disclosure，且常见设置是 adversarial student attacks；本文关注 ordinary turn-level tutoring 中的 case-specific intermediate reasoning bridge。
- Introduction 增加 “Positioning Against Nearby Work”，说明本文不是研究学生诱导 tutor 给出完整答案的设置，而是研究正常求助中 tutor 是否提前完成学生当前推理桥。
- Related Work 新增 `Answer Leakage And Tutor Robustness` 小节，并在 gap statement 中明确：final-answer disclosure under adversarial attacks 不评估 ordinary tutoring 中的 critical intermediate bridge leakage。
- Methods 的 Task Definition 明确写出：critical bridge leakage is not the same as final-answer leakage；它是 premature completion of a case-specific reasoning bridge。
- Discussion 增加窄化安全边界：本文的 safety framing 是 pedagogical and tutoring-specific，不是覆盖所有 AI-supported education settings 的广义安全框架。

## 与 DBox 的区分

- Abstract 明确说明 DBox-style work studies LLM-supported algorithmic-programming decomposition；本文评估 case-specific tutor responses and bridge preservation。
- Introduction 的 positioning 段说明本文不提出 DBox-style decomposition system；DBox-inspired condition 只作为 strong offline baseline。
- Related Work 新增 `Algorithmic-Programming Scaffolding And DBox` 小节，并在 gap statement 中说明：DBox-style decomposition work 不提供 case-specific human-review benchmark for critical bridge leakage。
- Methods 的 harness table 和解释句保留 DBox-inspired 条件，但新增边界：这些 rows 是 offline review baseline harnesses，不是完整 DBox 系统主张。
- Results 中 DBox+Repair 仍保持 targeted 20-case sensitivity add-on，不升格为 full main condition。

## Claim Gate Check

- 是否新增 claim：no
- 是否修改数字：no
- 是否新增实验：no
- 是否新增正式 citation：no
- 是否改变 evidence class：no
- 是否把 sensitivity / stress / calibration 写成 main result：no
- 是否把 Coach A/B/priority60 写成单一确定标签：no
- 是否把 all 50 写成 headline：no
- 是否写 Bridge Contract 对全部 baseline 的强支配：no
- 是否写 Guard-only 改写最终输出：no
- 是否写 Repair 主实验因果：no
- 是否写 LLM grader 承担人类裁决角色：no
- 是否违反 claim gate：no
