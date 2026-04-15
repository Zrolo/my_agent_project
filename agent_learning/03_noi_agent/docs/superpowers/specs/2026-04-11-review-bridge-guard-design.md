# 第五阶段设计：首轮 Review 的轻量 Bridge 约束

## 1. 背景

当前项目已经完成：

- 阶段一：高频 bridge 的学生主链路稳定
- 阶段二：外部知识源、统一 snippet、样例池与 teacher 统计基础设施
- 阶段三：最弱高频 bridge 的真实样例复审
- 阶段四：高频与代表性长尾 bridge 的 `visual_hint` 精修

现阶段最明显的剩余问题，不再是后续 quiz、remedy、knowledge card 跑不通，而是**首轮 review 仍然可能漂桥或退回泛化话术**。这会直接影响学生第一眼看到的解释质量，并且会把后续整条链路带偏。

典型风险：

- `P2922` 可能从 `shared_prefix_merging` 漂回泛 `state_design / implementation`
- `P2678` 可能从 `check_condition` 退回 `complexity_fit`
- `P2249` 可能从 `left_bound_update` 退回泛二分说明

因此第五阶段只解决一个问题：

> **首轮 review 不仅要判对 bridge，而且 `problem_focus / key_bridge / visual_hint / guided_walkthrough / try_now` 这 5 个字段都必须围着同一座 bridge 讲，不许泛化。**


## 2. 目标

第五阶段目标分两层：

1. 首轮 review 不判错桥
2. 首轮 review 的关键字段不泛化，必须围着当前 bridge 讲

这里的“关键字段”固定为：

- `problem_focus`
- `key_bridge`
- `visual_hint`
- `guided_walkthrough`
- `try_now`


## 3. 非目标

第五阶段**不做**以下内容：

- 不新增 bridge
- 不重写首轮 review 状态机
- 不改 quiz / remedy / knowledge card 路由
- 不把外部 snippet 深度接入首轮全文生成
- 不做按题号检索
- 不为每个 bridge 拆一整套独立 prompt 系统
- 不改 teacher 页面或统计协议


## 4. 范围

第五阶段只收这 4 类高频易漂 bridge：

1. `method_selection`
2. `shared_prefix_merging`
3. `check_condition`
4. `left_bound_update`

这 4 类之外的 bridge 暂时不纳入第五阶段。


## 5. 方案选择

### 方案 A：只加 prompt 约束

做法：

- 在首轮 review prompt 里补一句“必须围着当前 bridge 讲”

优点：

- 改动最小

问题：

- 只靠 prompt 不稳
- 无法保证最终落盘字段真的没有漂桥或泛化

### 方案 B：只做 post-generation repair

做法：

- 先正常生成首轮 review
- 生成后再修字段

优点：

- 更可控

问题：

- 如果首轮一开始就讲偏，后处理不一定能把 `guided_walkthrough` 这种连续字段拉回同一座桥

### 方案 C：轻量 prompt constraint + post-generation guard（推荐）

做法：

- 先用一层很薄的 prompt 约束减少明显跑偏
- 再用 post-generation guard 做最终兜底

优点：

- 风险最低
- 不需要重写首轮架构
- 更适合当前项目已经稳定的后半段链路

结论：

- 采用 **方案 C**


## 6. 设计

### 6.1 首轮 review 的两层约束

第五阶段首轮 review 采用两层约束：

#### 第一层：轻量 prompt constraint

目的：

- 减少首轮一上来就偏到别的桥

原则：

- 只补薄约束，不拆成每桥一整套大 prompt
- 只要求模型围绕当前 bridge 讲对象、关系和当前一小步

#### 第二层：post-generation bridge guard

目的：

- 对最终落盘的 review 结果做一致性检查与最小修复

这层是第五阶段的核心。


### 6.2 只 guard 5 个关键字段

只检查和修复：

- `problem_focus`
- `key_bridge`
- `visual_hint`
- `guided_walkthrough`
- `try_now`

不扩到其他字段。

原因：

- 这 5 个字段已经足以决定学生第一眼看到的“是不是在讲同一座桥”
- 扩到全部字段会显著增加维护成本，且不符合“轻量 guard”的目标


### 6.3 只修两类问题

post-generation guard 只处理：

1. **bridge 判错**
2. **文案泛化**

不做：

- 大范围润色
- 风格统一
- 摘要重写
- 额外教学内容扩展


### 6.4 每座桥的必备锚点词

第五阶段先为 4 座桥定义最小锚点词集合。

#### `check_condition`

必备锚点词至少命中其一组：

- `check(mid)`
- `可行`
- `当前 mid`

首轮文案要求：

- 不能把 `check(mid)` 写成“直接算答案”
- 必须明确它只在判断当前值是否可行

#### `left_bound_update`

必备锚点词至少命中其一组：

- `a[mid] == x`
- `保留 mid`
- `最左`

首轮文案要求：

- 不能退回泛“二分边界”
- 必须明确解释为什么相等时仍要保留 `mid`

#### `shared_prefix_merging`

必备锚点词至少命中其一组：

- `前缀`
- `沿前缀路径`
- `公共前缀`

如果检测到 trie 节点计数语境，再额外要求命中：

- `经过次数`
- `结束次数`

首轮文案要求：

- 不能退回泛“字符串处理”或泛“状态设计”
- 必须围着“公共前缀先合起来，查询只沿前缀路径走”来讲

#### `method_selection`

必备锚点词至少命中其一组：

- `题面信号`
- `结构信号`

如果检测到 trie 语境，再额外要求命中：

- `相同开头`
- `前缀关系`

首轮文案要求：

- 不能只说“方法选择”或“理解这个方法”
- 必须回到题面里的结构信号


### 6.5 文案泛化的定义

以下内容视为“泛化话术”，不能作为首轮关键字段的主要表达：

- `理解这个方法`
- `想清楚这个条件`
- `确认状态定义`
- `搞懂这个过程`
- `先理解思路`

如果关键字段主要停在这类抽象表达，就触发 guard 修正。


### 6.6 最小修复策略

如果检测到 bridge 判错或字段泛化：

1. 先保留当前已正确的 bridge 上下文
2. 只重写这 5 个字段
3. 重写后的字段必须重新满足该 bridge 的锚点词和桥一致性要求

这里不允许：

- 重跑整轮 review
- 改 quiz
- 改后续 remedy / knowledge card


## 7. 桥一致性规则

第五阶段新增一个明确验收概念：

> **桥一致性：`problem_focus / key_bridge / visual_hint / guided_walkthrough / try_now` 必须明显围着同一座 bridge。**

不允许出现：

- `problem_focus` 在讲 `shared_prefix_merging`
- `guided_walkthrough` 却退回 `state_design`

或：

- `key_bridge` 是 `check_condition`
- `try_now` 却变成泛“试试这个方法”


## 8. 验收标准

### 8.1 桥一致性

以下 5 个字段必须同时围着同一座 bridge：

- `problem_focus`
- `key_bridge`
- `visual_hint`
- `guided_walkthrough`
- `try_now`

### 8.2 禁止泛化

上述 5 个字段中，任何一个都不能主要依赖泛化话术充当解释主体。

### 8.3 代表样例回归

第五阶段至少钉住这 3 条真实代表样例：

- `P2922`
- `P2678`
- `P2249`

### 8.4 不破坏已稳定链

首轮 guard 改动不能让这些后半段退化：

- quiz
- remedy
- knowledge card
- visual_hint


## 9. 预期产物

第五阶段完成后，应得到：

1. 首轮 review 轻量 bridge guard
2. 4 座高频易漂桥的锚点词约束
3. 代表样例回归测试
4. bridge 一致性验证


## 10. 风险与边界

### 风险 1：规则写太细导致维护爆炸

控制方式：

- 只收 4 座桥
- 只 guard 5 个字段
- 只修桥错和文案泛化

### 风险 2：后处理修得太多，反而像重写

控制方式：

- 只重写 5 个字段
- 不动其他 review 结构

### 风险 3：首轮变稳了，但后半段被带坏

控制方式：

- 代表样例回归必须包含完整链路检查


## 11. 结论

第五阶段采用：

- **轻量 prompt constraint + post-generation guard**

并严格限制为：

- **4 座桥**
- **5 个字段**
- **两类问题：桥判错、文案泛化**

这是当前项目在不重写首轮架构的前提下，最稳、最小、最适合继续推进的一步。
