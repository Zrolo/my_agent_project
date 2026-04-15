# Review Scaffold Framework（2026-04）

这份文档用于统一当前 NOI 教学复盘系统的设计语言、prompt 方向和后续重构原则。

目标不是继续把 AI 做成“更会讲题”的系统，而是把它做成：

- 能先判断学生当前状态
- 能只补当前最关键的一步
- 能用最小有效支架帮助学生继续推进
- 能被 teacher review、rubric、baseline 稳定评估

---

## 1. 这份文档解决什么问题

当前系统已经具备：

- `review_mode / review_family` 路由
- 结构化 AI 复盘
- `quiz / self-check / remedy`
- teacher manual review
- observability / stats / by-mode-family breakdown

当前最主要的问题不是“系统不能用”，而是：

- AI 复盘太像摘要，不像老师在带学生走
- 复盘有定位，但引导不足
- prompt 规则逐渐变多，有臃肿和漂移风险

所以这一轮的总目标是：

> 把 review 从“总结答案”升级成“最小有效教学支架”。

---

## 2. 核心框架

当前 review 系统采用三层框架：

- `ZPD`：只补学生当前最可能跨过去的那一步
- `Adaptive Scaffolding`：支架强度随学生状态而变
- `EDF`：`Evidence -> Decision -> Feedback`

这三层里：

- `ZPD` 负责控制支架大小
- `Adaptive Scaffolding` 负责控制支架类型
- `EDF` 负责组织整个系统流程

注意：

- 这里的 `ZPD` 是工程化、产品化的使用方式
- 它不是对 Vygotsky 原始理论的强学术复现
- 内部使用时，更推荐把它理解成：
  - `最小有效支架`
  - `只补当前一步`
  - `不讲太满`

---

## 3. EDF：系统主线

### 3.1 Evidence

先看学生当前给了什么证据。

包括：

- 题目标题 / 来源 / 题面
- `completion_status`
- `submission_result`
- `bottleneck_text`
- `student_code`
- `reflection`
- 后续 quiz / self-check / remedy 回复

系统的第一原则：

> 没有证据，就不应直接进入完整复盘。

### 3.2 Decision

系统根据证据，先做教学判断。

包括两个层级：

#### A. 学习状态判断

- `failed_verdict`
- `stuck_bridge`
- `editorial_transfer`
- `independent_reflect`

并映射到：

- `failure_diagnosis`
- `success_reflection`

#### B. 当前最该补哪一步

例如：

- 是先定位错误
- 还是先补关键桥梁
- 还是先解释“为什么这样做对”
- 还是先帮助学生把问题说清楚

系统第二原则：

> 每次只解决一个当前桥梁，不同时展开多个难点。

### 3.3 Feedback

在完成判断后，才输出 AI 复盘。

第一阶段采用结构化复盘，不直接做自由聊天。

结构统一为：

- `problem_focus`
- `key_bridge`
- `guided_walkthrough`
- `try_now`
- `transfer_signal`

系统第三原则：

> 输出不是为了“总结”，而是为了让学生真的跨过当前这一步。

---

## 4. ZPD 在当前系统里的可执行定义

在本系统中，`ZPD` 不作为抽象口号使用，而是落成以下 5 条规则：

### 4.1 先判断学生已经会到哪一步

review 不是直接开讲，而是先判断：

- 学生已经会什么
- 学生当前卡在哪一步
- 当前卡点是否足够清晰

### 4.2 一次只补一座桥

不能在一次 review 里同时做这些事情：

- 讲完整题意
- 解释关键方法
- 讲完整解法
- 再补代码细节

必须只选其中最关键的一步。

### 4.3 支架只能推进半步到一步

如果一条 review 已经让学生不需要自己补最后一步，说明支架过大。

换句话说：

- 不能把整题讲完
- 不能把整条证明讲完
- 不能把整段代码打平给学生

### 4.4 不确定时默认更保守

如果系统不能稳定判断学生已经会到哪一步，默认按更低层级处理：

- 宁可支架更小
- 不要一次讲过头

### 4.5 证据不足时先澄清，不先讲题

如果学生只说：

- “不会”
- “没思路”
- “看不懂”

而没有给出足够题面/进度/错误证据，则 review 目标应切换成：

> 帮学生把问题说清楚。

这属于“澄清式支架”，不是“解题式支架”。

---

## 5. Adaptive Scaffolding 在当前系统里的可执行定义

`Adaptive Scaffolding` 在本系统中，主要体现为：

### 5.1 支架类型随 mode 变化

#### `failed_verdict`

重点：

- 点错误位置
- 缩小到具体判断、条件、代码位置
- 给一个最小修正动作

#### `stuck_bridge`

重点：

- 点当前关键桥
- 用 2-3 步帮助学生跨桥
- 不做整题总结

#### `editorial_transfer`

重点：

- 解释题目动作如何映射到算法操作
- 解释状态、结构、操作含义

#### `independent_reflect`

重点：

- 解释为什么这样做对
- 形成迁移触发信号

### 5.2 支架强度随证据变化

同样是 `stuck_bridge`，学生状态可能不同：

- 题目对象关系都没站稳
- 对象站稳了，但桥梁没抓住
- 桥抓住了，但不会落到当前步骤

因此：

- `guided_walkthrough` 的强度要跟着当前状态变
- 不能所有 case 都套一份固定话术

### 5.3 success / failure 两大方向不同

#### `failure_diagnosis`

目标：

- 先定位问题
- 再给最小下一步

#### `success_reflection`

目标：

- 先说明为什么这样做对
- 再帮助学生形成迁移能力

---

## 6. 第一阶段采用的 review 输出结构

第一阶段**不做纯对话式复盘**，先升级结构化复盘。

统一输出结构为：

### 6.1 `problem_focus`

中文展示：

- `你卡在哪`

定义：

- 只说学生当前卡住的那一步
- 不复述整题
- 不讲完整做法

### 6.2 `key_bridge`

中文展示：

- `先抓住什么`

定义：

- 说清当前题最该先抓住的关键事实
- 不只是算法名
- 必须贴题

### 6.3 `guided_walkthrough`

中文展示：

- `跟我走一遍`

定义：

- 第一阶段最重要的新字段
- 必须写成 `2-3` 步
- 每一步都要点名当前题里的对象、条件或量
- 不能只写：
  - 画图
  - 手推
  - 再想想
- 不能直接把整题讲完

这段的目标不是“解释”，而是：

> 带学生跨过当前这一小步。

### 6.4 `try_now`

中文展示：

- `现在你来试`

定义：

- 只给一个很小的问题或动作
- 学生能在 `1` 步内回答或执行
- 它不是建议清单
- 它承担的是“桥接确认”的作用

### 6.5 `transfer_signal`

中文展示：

- `下次怎么认出来`

定义：

- 只负责帮助学生识别下一次类似题面信号
- 必须贴题面里的具体对象、条件、数量关系
- 不能写抽象模板

---

## 7. 学生输入模糊时的处理方案

当学生输入过于模糊时，系统不能直接做完整复盘。

### 7.1 模糊输入的典型特征

- 只说“我不会”
- 只说“没思路”
- 只说“看不懂”
- 没有清楚说明题目要求
- 没有说明自己试到了哪一步

### 7.2 此时 review 的目标应切换

从：

- 解题式支架

切换为：

- 澄清式支架

### 7.3 澄清式支架的目标

帮助学生补齐最关键的证据：

- 这题最后要求求什么
- 目前已经试到哪一步
- 更卡在：
  - 读题
  - 建模
  - 转移/判断
  - 代码
  - 正确性解释

### 7.4 这时的字段应如何用

#### `problem_focus`

- 当前卡点还不够清楚

#### `key_bridge`

- 先把问题说清楚，系统才能稳定判断下一步

#### `guided_walkthrough`

改成 2-3 步澄清引导，例如：

1. 先说清题目最后要求什么
2. 再说清你已经试到哪一步
3. 最后指出你具体卡在什么位置

#### `try_now`

只问一个澄清问题，例如：

- 这题最后要求你求什么？

---

## 8. 对话式复盘的定位

### 8.1 第一阶段不做纯聊天复盘

原因：

- 会显著增加系统复杂度
- 会削弱当前评测与 teacher review 稳定性
- 容易让 AI 过度自由发挥

### 8.2 第二阶段考虑“桥接对话”

不是自由聊天，而是：

- 先给结构化复盘
- 再围绕当前 `key_bridge` 发起一个受控对话
- 每轮只问一个小问题

学生可以：

- 选项回答
- 或一句自由文本回答

系统内部则将回复归类为有限状态，例如：

- 懂了
- 懂一半
- 误解了
- 跑偏了
- 需要更小支架

### 8.3 为什么不直接做开放聊天

因为本系统的目标是：

- 教学闭环
- 稳定评估
- teacher 可复核

而不是开放式闲聊。

---

## 9. prompt 重构原则

`review_engine.py` 后续不应继续无限追加规则，而应做分层。

### 9.1 Base Prompt

只放所有模式都共享的核心原则：

- 角色定义
- 主任务
- `Evidence -> Decision -> Feedback`
- 一次只补一步
- 禁止直接讲完整解法
- 输出结构

### 9.2 Family Prompt

只放两大方向的差异：

#### `failure_diagnosis`

- 定位错误 / 缩小问题 / 最小修正动作

#### `success_reflection`

- 解释为什么对 / 迁移信号 / 不重复做法

### 9.3 Mode Prompt

每个 mode 只放它最独特的 `1-2` 条规则：

- `failed_verdict`
- `stuck_bridge`
- `editorial_transfer`
- `independent_reflect`

### 9.4 Code Fallback

这些不应继续堆进 prompt：

- 旧字段兼容
- 历史数据 fallback
- 纯文本回退解析
- 新旧 UI 映射

它们应该尽量放在代码里。

---

## 10. rubric / cases / baseline 的新方向

后续评测建议不再只看“写得具体不具体”，而是围绕：

### 10.1 Evidence

- 有没有用到学生输入
- 有没有忽略代码、错误现象、卡点描述

### 10.2 Decision

- mode 判得对不对
- 当前桥梁判得对不对
- 支架强度是不是太大或太小

### 10.3 Feedback

- 有没有引导学生过桥
- 下一步是否可执行
- 有没有剧透整题

### 10.4 重点 rubric 维度

建议逐步引入：

- `evidence_use`
- `state_identification`
- `guidance`
- `actionability`
- `non_spoiling`

---

## 11. 当前系统模块与框架映射

### Evidence

- `bottleneck_text`
- `completion_status`
- `submission_result`
- `student_code`
- `reflection`
- quiz / self-check / remedy 回复

### Decision

- `review_mode`
- `review_family`
- prompt 路由
- teacher manual review 对 mode 的校正

### Feedback

- `problem_focus`
- `key_bridge`
- `guided_walkthrough`
- `try_now`
- `transfer_signal`
- quiz / self-check / remedy

---

## 12. 当前阶段的直接行动建议

### A. 先完成第一阶段结构化复盘升级

优先把 review 做成：

- 不是摘要
- 而是微型支架

### B. prompt 先重构，再扩规则

优先做：

- 分层
- 减负
- 去兼容化

而不是继续往一个 prompt 里无限堆规则。

### C. 历史兼容放代码，不放 prompt

所有：

- 旧字段兼容
- fallback
- parse
- UI 兼容

尽量由代码层承担。

### D. 第二阶段再考虑桥接对话

第一阶段先把结构化复盘和 bridge check 做稳。

---

## 13. 一句话版本

当前系统的目标，不是让 AI“更会讲题”，而是让它：

> 先根据学生证据判断当前状态，再只补当前最关键的一步，并用最小有效支架帮助学生继续往前走。

---

## 14. 对后续 AI / 开发者的使用说明

如果后续 AI 或开发者要继续改 review 系统，请先遵守下面 4 条：

1. 先问：这次改动是在增强 `Evidence`、`Decision` 还是 `Feedback`？
2. 如果一条规则只是在服务旧数据兼容，优先放代码，不放 prompt。
3. 如果一条输出已经让学生不需要自己补最后一步，说明支架过大。
4. 如果学生证据不足，优先做“澄清式支架”，不要直接讲题。
