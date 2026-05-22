# CP-MissingBridgeBench v4：20 个开发样例稳定性检查记录

日期：2026-05-22

这份文件是给我们自己看的中文总结，用来说明 v4 prompt 到目前为止做了什么、发现了什么问题、为什么现在还不能直接进入 30-case holdout 或 100-case 正式实验。

一句话结论：

> v4.0/v4.1 的链路已经能稳定跑通；v1.0 已经把“根据题名乱补题目细节”的问题改成了更稳的输入支撑原则 + title-only 精确模板模式。但是 v1.0 仍然比较保守、模板化，所以还需要先做 20-case 的教练式质量检查，确认它不是“安全但没用”。

## 1. 本轮没有做什么

这次只是 v4 的开发集稳定性检查，没有碰主实验，也没有碰线上系统。

- 没有修改 dialogue-state v3 主实验。
- 没有重算 dialogue-state v3 主表。
- 没有新增 dialogue-state v3 主实验 condition。
- 没有修改线上 AIChat、active mode、生产 prompt 或学生可见回复。
- 没有生成 30-case holdout 结果。
- 没有生成 100-case final responses。
- 没有使用学生原文、完整代码、完整线上 AIChat 回复、真实身份、hash salt 或可逆映射。
- 本轮只使用 v2 100-case case-freeze CSV 里的脱敏摘要和 rubric 字段。

## 2. 本轮新增/使用的文件

主要运行脚本：

- `evals/aichat/run_cp_missingbridgebench_v4_dev20.py`

本轮逐步生成的 prompt 草稿：

- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_2_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_3_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_4_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_5_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_6_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_7_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_8_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_9_20260522.md`
- `docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v1_0_20260522.md`

运行结果文件在：

- `evals/aichat/ad_hoc_runs/`

这些运行结果目前是内部开发产物，不是论文结果，也不建议公开。

## 3. v4 链路现在怎么跑

v4 是一个离线四段式链路：

1. **Bridge Judge**
   先判断学生当前缺的“关键推理桥”是什么，同时把“内部知道的桥”和“给 Tutor 看的安全边界”分开。

2. **Tutor**
   生成中文学生可见回复。目标是让学生能往前走，但不替学生走完关键一步。

3. **Leakage Guard**
   检查 Tutor 回复有没有过早说出关键推理桥。标签和教练评分表保持一致，例如 `no_leakage`、`minor_bridge_leakage`、`major_bridge_leakage`、`answer_leakage`。

4. **Targeted Repair**
   只有 Guard 判断需要修复时才运行。它只应该定点软化越界句子，不应该整段重写成空泛鼓励。

这条链路只用于离线实验，不接入线上 AIChat。

## 4. v0.1 暴露出的主要问题

第一轮完整 20-case dev 能跑通，但 prompt 不稳定。

当时统计是：

- 20 行全部跑完。
- JSON / validation 错误：0。
- 泄露标签：`no_leakage=19`，`answer_leakage=1`。
- 触发 Repair：1 条。

真正的问题不是程序报错，而是 **Tutor 会根据题名或很短摘要乱补题目细节**。

例如它可能会自己编：

- 具体样例；
- 坐标；
- 二进制串；
- 状态维度；
- 数据结构名；
- 节点字段；
- 操作顺序。

这很危险。因为公开 freeze 包很多 case 只有题名级摘要，模型不能靠题名自己猜题面。如果它猜了，回复看起来很具体，但其实可能是编出来的，也可能泄露学生该自己想的东西。

所以 v0.1 不能冻结。

## 5. 从 v0.2 到 v0.8 改了什么

### v0.2

加入“不要凭空补题面细节”的规则。

重点是：

- 不要编样例；
- 不要编坐标；
- 不要编数组；
- 不要编数据结构名；
- 不要编状态维度。

### v0.3

继续收紧“候选答案形状”。

也就是说，Tutor 不能说：

- “是不是前 i 个？”
- “是不是二维状态？”
- “试三个点？”
- “用这个结构？”

除非这些内容本来就在输入材料里。

### v0.4

加入 `public_context_level`。

如果 `public_context_level = title_only`，意思是：

> 当前给模型看的只是题名级/摘要级上下文，不能当作完整题面来发挥。

### v0.5

发现问题不只在 Tutor，还可能从 Bridge Judge 的 `allowed_support` 传进去。

所以 v0.5 开始要求：

> Bridge Judge 给 Tutor 看的字段里，也不能出现编造的样例、数字、状态维度、数据结构名。

### v0.6

加入 title-only 模板。

如果上下文只有题名级信息，Tutor 不再自由发挥，而是从少数几个“学生自己已有材料”的动作里选一个。

例如：

- 让学生写出当前变量/状态的含义；
- 让学生用已有最小样例记录一个变量每一步的值；
- 让学生写出每一步后应该保持的一条性质；
- 让学生说明一次操作前后哪些量应该改变或不变。

### v0.7

把 title-only 模式进一步变成接近固定模板。

要求：

- 回复最多两句；
- 不用“比如”“例如”；
- 不加括号里的例子；
- 不写节点、字段、插入、查询、距离等具体操作词。

### v0.8

加入显式禁止词表 `title_only_forbidden_terms`。

禁止词包括：

- `比如`
- `例如`
- `插入`
- `查询`
- `合并`
- `距离`
- `点集`
- `节点`
- `字段`
- `cnt`
- `end`
- `dp[`
- `Trie`
- `线段树`

如果 title-only 场景里出现这些词，Guard 应该要求 Repair。

## 6. v0.8 完整 20-case dev 结果

运行目录：

- `evals/aichat/ad_hoc_runs/cp_missingbridgebench_v4_dev20_20260522_v0_8/`

结果摘要：

- 样例数：20
- 唯一 case 数：20
- 使用模型后端：`deepseek_flash`
- 总 LLM 调用次数：60
- validation error：0
- 泄露标签：`no_leakage=20`
- 是否需要 Repair：`no=20`
- 最终回复来源：`candidate=20`
- 模型自评空泛度：`low=18`，`medium=2`
- 是否允许公开 case-level 内容：全部 `no`

额外检查：

- 对最终回复做 forbidden-term 检查。
- 命中行数：0。

也就是说，v0.8 已经基本解决了“title-only 情况下乱补具体题目细节”的问题。

## 7. 现在的风险

v0.8 的优点是安全、干净、稳定。

但它的问题也很明显：

> 它可能太保守、太模板化。

比如很多回复会变成：

> “请用一句话写出你当前代码中一个关键状态、变量或维护对象的含义。写完后，再说明它在一步操作前后应该怎样变化。”

这种回复安全，但不一定足够贴题，也不一定足够帮助学生继续推进。

所以 v0.8 还不能直接冻结。

## 8. 下一步应该做什么

下一步不是直接跑 30-case，也不是直接跑 100-case。

下一步应该做：

1. 对 v1.0 的 20-case 输出做一次教练式质量检查。
2. 重点看它是不是太空、太弱、太模板化。
3. 如果太弱，只能继续在这 20 个 dev case 上改。
4. 不能偷看 30-case holdout 来调 prompt。
5. 等 dev review 通过后，才能冻结 prompt。
6. prompt 冻结后，再进入 30-case holdout。

## 9. 当前结论

当前结论是：

> v1.0 可以作为“安全稳定候选 prompt”，但还不是最终冻结 prompt。v0.8 是前一版禁词表方案，v1.0 是现在更推荐的输入支撑原则 + title-only 精确模板方案。

它通过了：

- 20-case dev 跑通；
- JSON 稳定；
- 无 validation error；
- 无 forbidden-term 命中；
- 无明显 title-only 乱补题面细节。

它还没通过：

- 教练式有用性检查；
- 30-case holdout；
- 100-case final evaluation。

因此不能把 v1.0 写成论文结果，也不能说 v4 已经成功。

## 10. v0.9 和 v1.0 的补充记录

用户指出一个关键问题：

> 不能靠禁止某些词来控制模型，因为模型很容易换一种说法绕过去。prompt 应该抽象出共性规则。

这个判断是对的。因此我们在 v0.9 做了方向调整。

### v0.9：从“禁词表”改成“输入支撑原则”

v0.9 不再把 `Trie`、`dp[`、`插入`、`查询` 这类词当成主要控制机制，而是改成更一般的规则：

> 如果输入材料没有支撑，模型就不能主动引入新的具体信息。

这里的“新的具体信息”包括：

- 具体样例；
- 数值；
- 坐标；
- 变量名；
- 字段名；
- 状态维度；
- 数据结构名；
- 具体操作名；
- 证明骨架；
- 题目关系或算法关系。

v0.9 targeted run 结果显示，这个方向比禁词表更合理，但仍有一个问题：模型又在一个 data-structure case 里写出了“插入或查询操作”。这说明仅有抽象原则还不够，title-only 场景下模型仍可能把“操作”细化成没有输入支撑的具体操作。

### v1.0：title-only exact-template mode

v1.0 保留 v0.9 的抽象原则，但在 `public_context_level = title_only` 时增加了更硬的实现方式：

> 学生可见回复必须精确复制一个通用模板，最多只能加一句中性开头，例如“先别急着改代码”。不能把模板改写成题目特定说法。

这不是回到禁词表。它的逻辑是：

- 如果只有题名级上下文，模型没有足够依据生成题目特定提示；
- 所以它只能要求学生使用“自己已有的代码、样例、变量、状态解释”；
- 这样可以避免模型靠题名或记忆补题面。

v1.0 完整 20-case dev 结果：

- 样例数：20
- validation error：0
- 泄露标签：`no_leakage=20`
- 是否需要 Repair：`no=20`
- 最终回复来源：`candidate=20`
- 模型自评空泛度：`low=18`，`medium=2`
- watch scan 命中：0
- 总 LLM 调用次数：60

当前判断：

> v1.0 比 v0.8/v0.9 更符合工程和教育原则：它不是靠封闭禁词表，而是在上下文不足时强制进入通用、学生自有材料驱动的模板模式。

但 v1.0 仍然不能直接冻结，因为它可能太模板化。下一步仍然是 20-case 教练式有用性检查：看这些回复是否太弱、太重复、太不像真实老师。
