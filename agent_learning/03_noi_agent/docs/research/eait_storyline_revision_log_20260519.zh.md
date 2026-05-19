# EAIT Storyline Revision Log 20260519

## 输出文件

- `docs/research/paper_submission_manuscript_dialogue_state_v3_eait_v0_4_storyline.zh.md`

## 主要故事线改动

- Abstract 从“过程清单”改为“教育问题 -> 研究缺口 -> 方法 -> 主要发现 -> 边界”，减少了 blind review / sensitivity / stress / calibration 的长列表堆叠，同时保留 50 cases、7 conditions、350 responses 和 31-case `main_scaffold_eval` headline slice。
- Introduction 增加 binary-search check 的 CP tutoring vignette，并把 DP state / LCA 等场景作为同一教学张力的补充例子。
- Introduction 明确说明：不直接给代码仍可能泄露 critical bridge，因为泄露对象可能是 predicate、state semantics、invariant、update rule 或 debugging evidence。
- Contributions 保持三点，但改为更自然的教育技术语言：评价问题、human-review workflow、bounded evidence。
- Related Work 保留 5 小节结构，每节加入未绑定 citation placeholder，并在小节末尾增加 gap statement。
- Methods 增加 running example，将 missing bridge、forbidden content、acceptable reveal 和 expected next action 串起来解释。
- Results 每节标题改为 RQ / evaluation question，并在各节内显式区分 what we tested、what we observed、what this supports、what it does not support。
- Discussion 强化四个教育技术启示：no-direct-answer rules are insufficient；human review is necessary；repair is promising but burden-bearing；automatic graders remain auxiliary。
- Conclusion 保持 bounded close，不写 product victory。

## Claim Gate Check

- 是否新增 claim：no
- 是否改数字：no
- 是否新增 citation：no；只加入未绑定 citation placeholders，未加入正式作者-年份引用、DOI、URL 或 bibliography entry
- 是否改变 evidence class：no
- 是否把 sensitivity / stress / calibration 写成 main result：no
- 是否把 Coach A/B/priority60 写成 final gold：no
- 是否把 all 50 写成 headline：no
- 是否写 Bridge Contract 显著全面优于 baseline：no
- 是否写 Guard-only 修复最终输出：no
- 是否写 Repair 主实验因果：no
- 是否写 LLM grader 替代人类：no
- 是否违反 claim gate：no

## Before / After 示例

### 示例 1：Introduction 问题进入方式

Before:
> Students often need help at exactly the moment when they have not yet completed a reasoning bridge. That is also the moment when a tutor can most easily over-help.

After:
> Consider a competitive-programming tutoring dialogue in which a student says, “I know this may need binary search, but I do not know how to write `check(x)`.” A helpful tutor could ask what `x` represents, what condition should become easier or harder as `x` changes, and what evidence from the problem constraints should be tested.

作用：从抽象张力改为具体 CP tutoring vignette，让 EAIT 读者先看到教育问题，再看到 benchmark construct。

### 示例 2：Methods construct 解释

Before:
> A missing bridge is the local reasoning step that the student has not yet completed but needs for the next productive move.

After:
> As a running example, suppose the student has already suspected binary search but has not yet formulated `check(x)`. The missing bridge is not “binary search” itself. It is the monotonic predicate: what candidate `x` means, what property should be tested, and why the test becomes easier or harder as `x` changes.

作用：把 missing bridge、forbidden content、acceptable reveal 和 expected next action 解释成可操作评审对象，而不是纯定义。

### 示例 3：Results 呈现方式

Before:
> Same-case paired comparisons constrain the strength of the headline.

After:
> What we tested: Same-case paired comparisons test whether observed condition differences remain strong when each condition is compared on the same cases rather than only through aggregate means.

作用：把 Results 从证据表说明改为评价问题驱动，明确每节能支持什么、不能支持什么。
