# Nonoverlap Framing v0.2 Change Log 20260519

## 输出文件

- `docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_2.zh.md`

## v0.2 相比 v0.1 改善了哪些故事线问题

- Abstract 改为“教育问题 -> critical bridge leakage -> CP-MissingBridgeBench -> evidence design -> main finding -> boundary”的顺序，减少开头对邻近工作的说明，使读者先进入教育技术问题。
- 邻近工作的区别从 Abstract 前两句移到 Abstract 后半段和 Introduction 的 `Positioning Against Nearby Work`，避免标题和摘要看起来像 final-answer leakage work 的变体。
- Introduction 保留 binary-search check vignette，并在 contributions 前明确写入：`This is a pedagogical-safety framing, not a general AI-safety benchmark.`
- Related Work 2.1-2.6 使用已规划的 citation placeholders；这些只是占位符，不是正式 citation、DOI、URL 或 bibliography entry。
- Related Work 每节继续保留 gap statement，突出本文补的是 ordinary turn-level tutoring 中 case-specific critical bridge leakage 的评测缺口。
- Results 保留 RQ 结构，但将 `What we tested / What we observed / What this supports / What it does not support` 的显式标签改成自然段落，减少 evidence-audit-report 口吻。
- Results 每节结尾仍保留 evidence boundary，确保 main result、sensitivity、stress、fairness sensitivity 和 calibration 不混线。
- Discussion 将 `The Safety Framing Is Pedagogical And Tutoring-Specific` 提前，并明确 critical bridge leakage 是 tutoring-specific pedagogical safety failure。
- Conclusion 继续 bounded close，不写 product victory。

## Claim Gate Check

- 是否新增 claim：no
- 是否修改数字：no
- 是否新增实验：no
- 是否新增 citation：only placeholders / no formal unverified citation
- 是否改变 evidence class：no
- 是否把 sensitivity / stress / calibration 写成 main result：no
- 是否把 Coach A/B/priority60 写成单一最终金标：no
- 是否把 all 50 写成 headline：no
- 是否写 Bridge Contract 显著全面优于 baseline：no
- 是否写 Guard-only 修复最终输出：no
- 是否写 Repair 主实验因果：no
- 是否写 LLM grader 替代人类教练：no
- 是否违反 claim gate：no
