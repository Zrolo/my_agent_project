# Critical Bridge Leakage 校准策略 v1

本文件用于防止 Research v1 的关键桥泄露判断过度敏感。核心原则：

```text
我们评估的不是“AI 有没有讲到关键知识”，
而是“AI 是否过早、过完整地替学生完成当前 missing bridge”。
```

## 为什么要校准

算法竞赛辅导中，完全不讲概念会让学生挫败；但过早讲穿状态、转移、check、边界更新、标记规则或局部代码条件，会让学生跳过本轮最重要的推理练习。

因此，critical bridge leakage 是教学风险，不是绝对禁令。它必须结合：

- 学生是否已经说出关键桥；
- 当前轮次是解题中、复盘、总结还是直接求答案；
- 允许帮助级别是 L1/L2 还是 L3；
- AI 是否仍保留了学生下一步可推理空间；
- 透露的信息是上游观察任务，还是直接填写当前答案槽。

## 三层判断

### 1. Bridge information present

回复包含相关桥梁信息，例如提到状态、转移、check、边界、lazy、LCA、前缀和等。

这本身不等于泄露。

### 2. Bridge reveal

回复透露了部分关键关系，让学生更接近答案。

这可能是合理脚手架，也可能偏强，需要看学生状态和帮助级别。

### 3. Unjustified critical bridge leakage

学生还没有构造当前 missing bridge，而 AI 直接补完了精确关系、公式、方向、规则或代码条件。正式统计应重点惩罚这一类。

## 新增盲评字段

后续 response blind review workbook 新增：

```text
coach_bridge_reveal_justification
```

可选值：

- `no_reveal`: 没有实质透露当前关键桥；
- `pedagogically_justified`: 有教学理由，例如学生已说出、复盘总结、L3 强提示合理、或只是确认学生已有表述；
- `borderline`: 边界样本，是否过早或过完整不确定；
- `unjustified`: 无教学理由，AI 过早或过完整替学生补完当前 missing bridge。

这个字段与 `coach_leakage_label` 配合使用：

```text
coach_leakage_label = 泄露类型 / 严重度
coach_bridge_reveal_justification = 这种透露是否有教学正当性
```

## 例子

### 不算无正当性泄露

学生：

```text
我觉得 dp[j] 表示容量为 j 时能取得的最大价值。
```

AI：

```text
这个状态方向是合理的。下一步你先试着说：加入当前物品时，dp[j] 可能从哪两个旧状态来？
```

这里学生已经说出关键桥，AI 只是确认并推进下一步。

### 可能是合理概念解释

学生：

```text
lazy 到底表示还没做什么？
```

AI：

```text
可以先把 lazy 理解成父节点记录的“还没同步到子节点的更新”。你先判断：如果父节点区间已经整体加过，两个子节点此时一定已经各自更新了吗？
```

这给了半抽象概念，但仍让学生判断父子层之间的关系。

### 无正当性关键桥泄露

学生：

```text
我不知道 check(mid) 到底该返回 true 还是 false。
```

AI：

```text
如果 mid 可行就返回 true，然后缩右边界；不可行就返回 false，然后缩左边界。
```

如果这一轮 missing bridge 正是 true/false 语义和边界更新方向，这通常是 `unjustified`。

## 对 static lint / Guard 的影响

- `static lint` 只提示形式风险，不裁决泄露。
- Leakage Guard 应尝试判断语义泄露，但必须用教练标签校准。
- 教练盲评新增正当性字段后，应报告：
  - 教练 leakage label；
  - bridge reveal justification；
  - automatic Guard label；
  - static lint risk；
  - Guard false positive / false negative；
  - static lint 与 `unjustified` 的 overlap。

## 论文表述建议

推荐写法：

```text
Critical bridge leakage is not defined as the presence of any bridge-related information.
It refers to unjustified, premature, or overly complete completion of the student's current missing bridge.
```

中文：

```text
关键桥泄露不是指 AI 回复中出现任何桥梁相关信息，
而是指 AI 在缺少教学正当性的情况下，过早或过完整地替学生完成当前 missing bridge。
```
