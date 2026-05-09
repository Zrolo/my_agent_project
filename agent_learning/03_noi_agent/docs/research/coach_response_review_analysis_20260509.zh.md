# 教练回复盲评小样本分析（2026-05-09）

## 数据来源

- 教练标注文件：外部导出的 `response_review_labels_20260509154713.csv`（不提交进仓库）；已导入的研究标签见 `docs/research/coach_response_review_labels_v1.jsonl`。
- 匿名 key：`docs/research/coach_response_review_workbook_deepseek_flash_thinking_n10.key.csv`
- 盲评样本：20 条回复，覆盖 10 个 case。
- 系统条件：`bridge_contract` tutor，`predicted` guard，`tutor_only` pipeline，`deepseek_flash`。
- 对照变量：`chat_thinking_mode = enabled / disabled`，每组 10 条。

这是一轮小样本教练主观盲评，不应当当成最终 gold truth；它更适合作为 prompt/rubric 迭代和论文 error analysis 的初步证据。

## 总体分布

| 指标 | 数量 | 比例 |
|---|---:|---:|
| good | 6 | 30% |
| okay | 9 | 45% |
| bad | 5 | 25% |
| no_leakage | 17 | 85% |
| minor_bridge_leakage | 2 | 10% |
| answer_leakage | 1 | 5% |

初步判断：当前问题主要不是大规模答案泄露，而是回复质量不稳定。很多回复能做到“不泄露”，但没有把微型例子变成桥梁理解活动。

## Thinking 开关对比

| 条件 | n | good | okay | bad | 无泄露 | 轻微泄露 | 答案/代码泄露 |
|---|---:|---:|---:|---:|---:|---:|---:|
| thinking enabled | 10 | 2 | 5 | 3 | 8 | 1 | 1 |
| thinking disabled | 10 | 4 | 4 | 2 | 9 | 1 | 0 |

在这批样本里，`thinking disabled` 的教练评分反而略好：good 更多，bad 和 answer_leakage 更少。这个结果不能外推为“thinking 一定不好”，但它支持一个工程判断：

> 当前 DeepSeek Flash 的 thinking enabled 并没有在这批 Bridge Contract Tutor 回复中稳定提升教学质量，反而可能增加绕远、抽象、泄露或不聚焦的风险。

## 主要质性发现

### 1. 微型例子经常变成“临时任务”

多条标注都指出：AI 给了小例子，但学生可能只是在完成 AI 布置的小任务，不知道自己到底要观察什么。

典型问题：

- 只问学生算一个数字、选 A/B、填一个空。
- 没有先说明这个例子要观察哪座桥。
- 没有让学生把观察抽象成一句可迁移规则。

这说明论文里的 `micro_example` 不应只统计“有没有小例子”，还要区分：

- 低质量 micro-example：让学生完成临时填空。
- 高质量 bridge-oriented micro-example：让学生带着桥梁问题观察，并提炼可迁移规则。

### 2. 例子可能太抽象或太小，迁移性不足

一些回复虽然方向正确，但教练担心学生无法从极小例子迁移到真实问题。例如：

- 例子有用，但过小，不能自然推广。
- 解释严谨，但学生可能理解不了太抽象的表达。
- 缺少“这个小例子和原题关系是什么”的连接句。

这提示 prompt 需要要求 AI 在例子后补一句迁移桥：

> 这个小例子对应原题中的哪一类关系？下次遇到类似情况应观察什么？

### 3. 有些回复问太多，学生不知道先回答哪个

`trie` 类型确认样本中，教练指出 AI 一连串发问，会让学生不知道先回答哪一个。对低确定度或方法确认类问题，更好的策略是：

1. 先给一个观察方向。
2. 只问一个可回答的小问题。
3. 在回答过程中让学生逐步发现为什么像 trie。

### 4. 有些“为什么”问题应该先给概念解释，再引导迁移

例如 01 背包倒序枚举，学生问的是“为什么正序不行”。教练反馈中明确指出：这类知识/原理问题不能只问学生，也不能只给空泛任务；应该先解释关键原因，再引导学生思考如何迁移到其他地方。

这说明 AIChat 不能把所有教学都压成 Socratic 提问。对 `correctness / invariant / ordering dependency` 问题，应该允许短解释 + 引导问题。

### 5. 少量样本仍有关键桥泄露

共有 3 条泄露相关标注：

- `answer_leakage`: 1 条。
- `minor_bridge_leakage`: 2 条。

典型风险：

- 学生只是模糊说“像背包”，AI 直接跳到答案或关键知识点。
- 学生还没建立状态语义，AI 让学生围绕已经暗示的状态做选择题。
- 直接给出解法，再让学生二选一，容易让学生碰巧选中。

## 对 AIChat Prompt 的建议

这轮最值得加入 prompt 的不是新模块，而是一条微型例子规则：

```text
当你使用微型例子时，必须满足四步：
1. 先说明这个例子要观察的桥梁问题。
2. 给一个足够小但贴近原题的例子。
3. 只问一个局部、可回答的问题。
4. 要求学生把观察抽象成一句可迁移规则。

不要只让学生完成临时填空、选择题或计算任务。
```

同时增加两条约束：

```text
如果学生问“为什么/含义/原理”，可以先给一句简短概念解释，再用问题引导迁移。
一次回复只保留一个主要问题，避免连续抛出多个问题。
```

## 论文写法建议

这条发现适合写进论文，但不建议变成新的大 baseline。最合适的位置是：

1. response quality rubric 的子标准；
2. error analysis / case study；
3. bridge-aware scaffolding 的设计原则。

推荐表述：

> A micro-example is considered bridge-oriented only when it explicitly frames the relation to be observed and prompts the learner to generalize the observation into a transferable rule.

中文：

> 只有当微型例子明确指出要观察的推理关系，并要求学生把观察抽象成可迁移规则时，我们才认为它是桥梁导向的脚手架。

## 下一步

1. 将 `bridge-oriented micro-example` 规则加入 Bridge Contract Tutor prompt。
2. 先离线重新生成 10-20 条回复，不直接改线上 AIChat。
3. 用同一套网页盲评流程复评，比较 good/okay/bad 与 leakage 是否改善。
4. 如果改善稳定，再考虑同步到线上 AIChat system prompt。
