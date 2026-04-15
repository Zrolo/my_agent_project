# Bottom-Out Prompt And Visual Hint Ladder Design

## Goal

在不引入自由多轮聊天的前提下，把当前三轮支架梯子补完整：

- 第一轮：`normal_review_prompt`
- 第二轮：`remedy_prompt`
- 第三轮：`bottom_out_prompt`
- 收尾：`final_micro_confirm`

同时为三轮都增加可选的 `visual_hint`，但按轮次控制强度：

- 第一轮：轻量定锚图
- 第二轮：更具体的过桥图
- 第三轮：围绕当前题的 worked example 图

## Why

当前系统已经有：

- 5 段结构化复盘
- `clarify_prompt`
- `remedy_prompt`
- 三轮封顶
- `final_micro_confirm`

但还缺两块：

1. 第三轮最强支架还没有独立 prompt，只能复用第二轮补救思路
2. 现在的解释主要靠文字，面对初中生时，对象关系、状态含义、候选分类不够直观

## Design Decisions

### 1. 第三轮继续围绕当前题，不切去前置知识微课

第三轮 `bottom_out_prompt` 继续围绕：

- 当前题
- 当前 `target_bridge`
- 当前学生的具体误解

它的目标不是重讲整题，而是：

- 用更白话的 worked example
- 或一个更靠近答案的半成品讲解
- 帮学生把这座桥最后走通

### 2. 第三轮讲解必须初中生能听懂

`bottom_out_prompt` 必须遵守：

- 一句只讲一件事
- 先讲对象，再讲关系
- 尽量不用术语
- 如果用了术语，立刻翻译成白话
- 优先使用“先…再…最后…”句式
- 禁止直接讲完整解法、完整证明、完整代码

### 3. 三轮都支持 `visual_hint`

`visual_hint` 是可选字段，不强制每题都出。

它优先使用：

- 文本化小图
- 小表格
- 小分类框
- 小流程箭头

第一阶段不做真实图片、SVG、canvas 自动绘图。

### 4. 图示强度分轮次递增

#### 第一轮：定锚图

作用：

- 帮学生快速看清对象、关系、候选结构

限制：

- 很短
- 很轻
- 不喧宾夺主

#### 第二轮：过桥图

作用：

- 把当前桥拆成更小的一步
- 辅助 `remedy_prompt` 的“更小一步 / 换表示方式 / 纠正误解”

限制：

- 仍只围绕当前桥
- 不扩成讲义

#### 第三轮：worked example 图

作用：

- 配合 `bottom_out_prompt`
- 用当前题里的最小例子，直接示范这一步怎么看

限制：

- 只讲当前桥
- 不是整题全讲

### 5. 第三轮后接 `final_micro_confirm`

第三轮仍然不是终点解释就完，而是：

- `bottom_out_prompt`
- `final_micro_confirm`
- 终局

无论对错都不再开第 4 轮。

## Data Contract

### Review / remedy 新增字段

- `visual_hint: string`

适用范围：

- 第一轮 review 可选
- clarify / remedy / bottom-out explanation 可选

### 字段内容约束

`visual_hint` 必须满足：

- 只表达当前桥需要的对象、关系、候选或步骤
- 优先纯文本可渲染
- 控制在小块内容内
- 不允许大段讲义式文本

示例：

```text
左边原来的路：  A --- B --- C
右边原来的路：  D --- E
新边连起来后：  C --- D

新的最长路只可能来自：
1. 左边内部
2. 右边内部
3. 穿过新边
```

## Prompt Split

### `normal_review_prompt`

继续负责：

- `problem_focus`
- `key_bridge`
- `guided_walkthrough`
- `try_now`
- `transfer_signal`
- `visual_hint`（可选、轻量）

### `clarify_prompt`

继续负责证据不足时的澄清式支架，并允许输出：

- `visual_hint`（可选）

例如：

- 题目对象小表
- 当前进度分类框

### `remedy_prompt`

继续负责第二轮补救，并允许输出：

- `visual_hint`（可选，强于第一轮）

### `bottom_out_prompt`

新增，负责第三轮最强支架。

输出：

- `remedy_text`
- `visual_hint`
- `micro_action`

目标：

- 用当前题里的最小 worked example，把当前桥讲明白

## UI Behavior

### 学生端

#### 第一轮 review

在 `key_bridge` 和 `guided_walkthrough` 之间展示 `visual_hint`：

- 默认像一个小的等宽提示块
- 比主段弱一级

#### 第二轮 / 第三轮 remedy 卡片

在 `remedy_text` 之前或之后展示 `visual_hint`：

- 使用等宽块
- 明显比正文更结构化

### 教师端

教师人工复核卡片也展示 `visual_hint`，便于老师判断：

- 这一轮有没有把对象关系讲清
- 图示是否真的贴桥，而不是装饰

## Flow Changes

### 第二轮

第一轮失败后，进入 `remedy_prompt`。

### 第三轮

如果第二轮解释型补救后仍未过：

- 不再复用第二轮 prompt
- 改走 `bottom_out_prompt`

### 终局

第三轮讲解后：

- 进入 `final_micro_confirm`
- 通过：`assisted_success`
- 失败：`not_mastered + needs_teacher_followup`

## What We Are Not Doing

- 不做自由聊天式复盘
- 不做真实图片生成
- 不做新的第 4 轮
- 不切到独立的前置知识微课系统

## Success Criteria

完成后应满足：

1. 第一轮、第二轮、第三轮都可以有 `visual_hint`
2. 第三轮必须有独立的 `bottom_out_prompt`
3. 第三轮讲解比第二轮更白话、更具体、更接近当前题例子
4. 第三轮后仍只接一个 `final_micro_confirm`
5. 前后端、teacher review、历史记录都不会因为缺少 `visual_hint` 崩溃
