# Non-Overlap Framing v0.3 Change Log 20260519

## 输入与输出

- 输入稿件：`docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_2.zh.md`
- 输出稿件：`docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_3.zh.md`
- 本日志：`docs/research/nonoverlap_framing_v0_3_change_log_20260519.zh.md`

## 主要修改

1. Abstract
   - 保留 v0.2 的 non-overlap framing，但把开头集中在教育问题和 critical bridge leakage。
   - 将邻近工作区别放在后半段，避免第一二句显得像文献防御。
   - 按要求加入教育意义句：pedagogical safety 应在 learners' reasoning opportunities 层级评估，而不只看 final-answer disclosure。

2. Related Work
   - 保留 2.1-2.6 结构和 citation placeholders。
   - 每节改成更正式的段落逻辑：prior work -> limitation/gap -> our position。
   - 未新增未经核验事实；只使用占位符和已有定位语言。

3. Methods / Evaluation
   - 在 3.1 加入 conceptual table：Student state / Missing bridge / Acceptable reveal / Critical leakage。
   - 三个例子为 binary-search check、DP state、tree-difference marking。
   - 明确说明该表只解释概念，不新增实验、案例或结果。
   - 将 3.6 从内部 evidence-package 语气改成论文方法描述：说明 evidence role 如何约束 claim strength，并保留 evidence manifest / reproduction scripts 作为 audit trail。

4. Results
   - 保留 RQ 结构，但压缩数字密度。
   - 每个 RQ 只保留主文最关键数字；次要细节标注为 appendix candidate。
   - sensitivity / stress / calibration 继续作为 supporting evidence，不提升为 main result。

5. Discussion / Conclusion
   - 保持 pedagogical and tutoring-specific safety framing。
   - 继续强调 no-direct-answer rules are insufficient、human review is necessary、Repair is promising but burden-bearing、automatic graders remain auxiliary。
   - Conclusion 保持 bounded close，没有写 product victory。

## Claim Gate 检查

| 检查项 | 结果 |
| --- | --- |
| 是否新增 claim | no |
| 是否修改数字 | no |
| 是否新增实验 | no |
| 是否新增 citation | no, only placeholders |
| 是否改变 evidence class | no |
| 是否违反 claim gate | no |

## 具体边界说明

- 没有把 sensitivity / stress / calibration 写成 main result。
- 没有把 Coach A、Coach B 或 priority60 adjudication 写成单一确定 reference。
- 没有把 all 50 cases aggregate 写成 headline。
- 没有写 Bridge Contract 显著或全面优于所有 baseline。
- 没有把 Guard-only 描述成最终回复改写证据。
- 没有从主实验均值推出 Repair 因果。
- 没有把 LLM grader 描述成人类教练的替代方案。
- 没有将本文定位为通用 tutor robustness 评测、DBox 产品复现，或泛化 AI 教育安全评测。

## Before / After 示例

### 示例 1：Related Work 段落结构

Before:

> Work on AI tutoring and intelligent tutoring systems for programming has long treated feedback as more than correctness delivery.

After:

> Prior work on AI tutoring and intelligent tutoring systems for programming treats feedback as more than correctness delivery. Programming tutors are evaluated by how they help learners interpret errors, organize concepts, receive adaptive support, and make progress in realistic learning settings.

改动目的：从单句背景说明变成 EAIT 更常见的 prior work -> gap -> paper position 结构。

### 示例 2：Methods 概念解释

Before:

> As a running example, suppose the student has already suspected binary search but has not yet formulated `check(x)`.

After:

> Table 1 is a conceptual illustration only; it introduces the evaluation construct and does not add experimental cases or results.

改动目的：加入 conceptual table，并显式说明它不是新增实验或结果。

### 示例 3：Results 次要细节处理

Before:

> Rank agreement is also limited, with top-1 and last-place agreement both at 10/50.

After:

> Appendix candidate: top-1 and last-place rank agreement both at 10/50, plus detailed rater-strictness tables.

改动目的：保留数字，但降低主文数字密度，让主线更像正式 EAIT 结果叙事。
