# Bridge Schema Coach Annotation Guide v1

## Purpose

This guide is for competition coaches who annotate AIChat or offline examples for research.

The annotation goal is not to grade a student. The goal is to describe:

1. where the student is stuck in the problem-solving process;
2. what bridge is missing;
3. what level of scaffold is allowed without leaking the bridge or the full answer.

The final annotation can be exported as JSONL or CSV, but the coach-facing interface should look like a short survey form.

## Recommended Coach Workflow

Annotate one student turn at a time.

1. Read the problem context, student message, and optional code excerpt.
2. Choose one `student_state`.
3. Choose one `bridge_family`.
4. Choose one `known_focus`; choose `unknown` if the current system does not have a fitting focus.
5. Choose one `help_seeking_type`.
6. Write `missing_link` in one sentence.
7. Choose `allowed_help_level`.
8. Write `forbidden_completion` in one sentence.
9. Mark `needs_new_focus=true` if the bridge is real but not covered by current known focuses.
10. Add confidence and optional notes.

## Form Fields

| Field | UI control | Required | Coach-facing question |
| --- | --- | --- | --- |
| `student_state` | single choice | yes | 学生现在主要卡在解题流程的哪一步？ |
| `bridge_family` | single choice | yes | 学生缺失的是哪类中间关系？ |
| `known_focus` | single choice | yes | 当前系统已有 focus 里，最接近的是哪一个？ |
| `help_seeking_type` | single choice | yes | 学生这次是在怎样求助？ |
| `missing_link` | short text | yes | 学生缺的那一步关系，用一句话说明。 |
| `allowed_help_level` | single choice | yes | AI 本轮最多可以帮到 L1/L2/L3 哪一级？ |
| `forbidden_completion` | short text | yes | AI 本轮绝对不能直接说出的内容是什么？ |
| `needs_new_focus` | checkbox | yes | 这是否是现有 focus 覆盖不到的新桥梁？ |
| `confidence` | 1-5 scale | yes | 你对这条标注有多确定？ |
| `notes` | long text | no | 其他说明、反例、争议点。 |

## Student State Labels

Choose the state that best explains the student's current blockage.

| Label | Coach explanation | Example |
| --- | --- | --- |
| `text_comprehension_blocked` | 题面文字、输入输出、术语本身没有读懂。 | "题目看不懂，样例也不明白。" |
| `problem_representation_unclear` | 能读懂局部文字，但没有抽象出对象、状态、变量或结构。 | "学校和道路到底什么当点什么当边？" |
| `strategy_generation_blocked` | 题意基本懂，但没有可行思路或算法方向。 | "题目懂了，但完全不知道用什么算法。" |
| `strategy_misconception` | 有思路，但思路本身错了，学生还没有意识到。 | "我觉得每次选最大的就可以，为什么 WA？" |
| `strategy_application_gap` | 大方向对，但关键关系、公式、操作映射、证明入口不会落地。 | "知道二分，但 check(mid) 不会写。" |
| `implementation_execution_gap` | 思路关系基本明确，但代码表达、函数组织或语法实现卡住。 | "我知道要 pushdown，但代码不知道怎么写。" |
| `debugging_verification_gap` | 已有代码或近似解，但卡在边界、溢出、反例、局部 bug。 | "样例过了，大数据错，怀疑 int 不够。" |
| `reflection_transfer_gap` | 当前题会了或快会了，但不能解释、迁移、总结触发条件。 | "这题会了，下次怎么判断能用这个方法？" |

## Bridge Family Labels

Choose the missing relation that the next scaffold should target.

| Label | Coach explanation | Example |
| --- | --- | --- |
| `representation_bridge` | 不知道某个状态、变量、节点、数组格子、标记的含义。 | DP 状态含义、lazy 标记含义。 |
| `transition_bridge` | 不知道当前状态从哪些前置情况转移来。 | DP 转移、递归拆分。 |
| `predicate_bridge` | 不知道一个条件或 `check` 在判断什么。 | 二分答案的可行性判断。 |
| `modeling_bridge` | 不知道题面对象和限制如何建成结构。 | 建图、差分约束、对象关系。 |
| `selection_bridge` | 不知道为什么某个局部选择是安全的。 | 贪心选择、交换论证入口。 |
| `aggregation_bridge` | 不知道如何把多次局部影响压缩、累计、还原。 | 前缀和、差分、树上差分。 |
| `ordering_bridge` | 不知道为什么枚举或更新必须按某个顺序。 | 01 背包倒序、拓扑入度为 0。 |
| `mapping_bridge` | 不知道题面动作对应哪一个算法操作。 | 合并集合对应 union，取最小对应 heap pop。 |
| `boundary_bridge` | 不知道初始化、停止条件、边界或最小情况为什么成立。 | base case、左边界、下标范围。 |
| `complexity_bridge` | 不知道数据范围如何约束算法复杂度。 | `n=1e5` 时双循环是否可行。 |
| `unknown_bridge` | 明显有桥梁，但当前证据不足或不属于已有类。 | 学生描述太短，或出现新型关系。 |

## Help-Seeking Labels

| Label | Coach explanation | Example |
| --- | --- | --- |
| `instrumental_help` | 学生仍在参与解题，希望获得提示、解释、检查或下一步。 | "给我一点提示", "为什么这里要倒序？" |
| `executive_help` | 学生希望 AI 接管决策、完整思路、完整代码或最终答案。 | "直接告诉我怎么做", "帮我写完整代码。" |
| `help_avoidance` | 学生明显卡住但回避求助、拒绝提示或只表达放弃。 | "算了不会", "你别问我了。" |
| `unclear` | 信息太短或太模糊，无法判断求助方式。 | "不会", "？" |

## Help Levels

| Level | Meaning | Allowed scaffold | Avoid |
| --- | --- | --- | --- |
| `L1` | Minimal prompt | Ask a diagnostic question, point to evidence, or ask for one comparison. | Confirming the algorithm, giving formulas. |
| `L2` | Targeted scaffold | Give a micro-example, partial contrast, or one missing subquestion. | Giving the full bridge relation. |
| `L3` | Strong scaffold | Give a structured outline after the student has enough prerequisite work. | Full AC code, full proof, or direct final answer unless explicitly allowed by study design. |

## Annotation Examples

### Example A: Binary Search Check

Student message:

> 我知道要二分答案，但是 check(mid) 到底返回 true 还是 false 我总写反。

Recommended annotation:

```json
{
  "student_state": "strategy_application_gap",
  "bridge_family": "predicate_bridge",
  "known_focus": "check_condition",
  "help_seeking_type": "instrumental_help",
  "missing_link": "学生缺少把候选答案 mid 翻译成可行性判断的关系。",
  "allowed_help_level": "L2",
  "forbidden_completion": "不能直接给完整 check 条件和左右边界更新方向。",
  "needs_new_focus": false
}
```

### Example B: Wrong Greedy Confidence

Student message:

> 我觉得每次选当前最大的奖励就行，样例也过了，为什么不对？

Recommended annotation:

```json
{
  "student_state": "strategy_misconception",
  "bridge_family": "selection_bridge",
  "known_focus": "greedy_basis",
  "help_seeking_type": "instrumental_help",
  "missing_link": "学生缺少判断局部选择是否保留全局最优可能性的交换或反例关系。",
  "allowed_help_level": "L2",
  "forbidden_completion": "不能直接给完整正确贪心策略或完整反例构造过程。",
  "needs_new_focus": false
}
```

### Example C: Wants Full Solution

Student message:

> 这题我看懂了，但你直接告诉我用什么算法和代码怎么写吧。

Recommended annotation:

```json
{
  "student_state": "strategy_generation_blocked",
  "bridge_family": "complexity_bridge",
  "known_focus": "method_selection",
  "help_seeking_type": "executive_help",
  "missing_link": "学生缺少从数据范围和题面结构判断可行算法方向的关系。",
  "allowed_help_level": "L1",
  "forbidden_completion": "不能直接确认算法名称，不能给完整思路或代码。",
  "needs_new_focus": false
}
```

## Disagreement Rule

If two coaches disagree, discuss in this order:

1. Is the disagreement about `student_state` or `bridge_family`?
2. What exact sentence in the student message supports each choice?
3. Would the next best AI scaffold change if we choose label A instead of label B?

If the scaffold would not change, keep the more general label and record the disagreement in `notes`.

## Paper Use

For the paper, use coach annotation as the reference label. LLM labels should be treated as model predictions, not ground truth.

Recommended reporting:

- label distribution across `student_state` and `bridge_family`;
- Bridge Judge accuracy against coach labels;
- agreement between two coaches on 20-30 percent of samples;
- leakage rate and response quality before and after bridge-guided scaffolding;
- examples of newly discovered `unknown` focuses that field matching missed.

## Research Basis

This annotation design combines three traditions:

- problem-solving phase/state models, represented by Rott et al.'s descriptive phase model of problem-solving processes ([Springer](https://link.springer.com/article/10.1007/s11858-021-01244-3));
- programming problem-solving decomposition, represented by the PCDIT framework ([arXiv:2109.08896](https://arxiv.org/abs/2109.08896));
- adaptive help-seeking and metacognitive feedback in intelligent tutors, represented by Help Tutor research ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0959475210000538)).

In this project, the `bridge_family` layer is the domain-specific contribution: it turns general scaffolding into competition-programming-specific missing relation diagnosis.
