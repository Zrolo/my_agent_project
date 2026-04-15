# Bridge Quiz Ladder Design

## Goal

在现有 `quiz / self-check / followup / remedy` 学习流基础上，明确每一轮 quiz 的教学职责、通过后的状态含义，以及哪些讨论结论值得正式吸收到系统里。

这份设计解决两个问题：

1. 当前“第 1 轮、第 2 轮、第 3 轮”虽然已经存在，但每一轮 quiz 的教学意图还不够清楚。
2. 第 3 轮补救讲解后的收尾证据偏弱，需要一个更明确的“最终最小确认”设计口径。

---

## Why

当前系统已经具备：

- `main quiz`
- `self-check`
- `followup quiz`
- `remedy explanation / easier quiz`
- `mastery_status`
- 三轮封顶规则

但还缺一层统一定义：

- 每一轮 quiz 到底在考什么
- 为什么第 2 轮和第 3 轮不能继续沿用第 1 轮的题目粒度
- 哪些讨论结论适合正式纳入系统，哪些先不纳入

本设计的核心判断是：

> 三轮 quiz 必须围绕同一座桥，但“放大镜倍率”不同。

也就是：

- 第 1 轮：直接检查这座桥
- 第 2 轮：把桥拆小后再检查
- 第 3 轮：补救讲解后的最终最小确认

---

## Core model

### A. 同一座桥，不同粒度

三轮 quiz 都必须围绕同一个 `target_bridge`。

不允许出现：

- 第 1 轮考桥 A
- 第 2 轮突然变成桥 B
- 第 3 轮又开始考整题迁移

换句话说：

- 每一轮只是在同一桥上继续收缩
- 不允许借后续轮次偷偷换题

### B. 每一轮都比上一轮更小

轮次越往后，题目必须：

- 更具体
- 更局部
- 更贴当前误解

不允许：

- 第 2 轮比第 1 轮更综合
- 第 3 轮重新要求学生把整题讲顺

### C. 第 3 轮后必须停止

第 3 轮是最后一轮支架，不再开放第 4 轮。

第 3 轮后：

- 通过：`assisted_success`
- 未通过：`not_mastered + needs_teacher_followup`

---

## Round definitions

### Round 1: `main_quiz`

**目标**

看学生在看完第一轮结构化复盘后，能不能直接跨过当前桥。

**题目特点**

- 保留一点整题语境
- 只考当前桥
- 不能要求学生重新解整题

**适合考察的内容**

- 当前桥的核心判断
- 当前桥的候选结构
- 当前状态/条件的含义

**示例**

如果桥是“连边后新的最长路从哪里产生”，第 1 轮可以问：

> 新的最长路可能来自哪几类候选路径？

**通过后流转**

- 进入 `self_check_required`
- 由学生先做主观自评
- 必要时进入 `confirm_quiz`

### Round 2: `followup_quiz`

**目标**

如果第 1 轮没过，把桥拆得更小，只检查其中半步。

**题目特点**

- 比第 1 轮更小
- 一次只问一个对象、关系或局部判断
- 明显降低整题背景负担

**适合考察的内容**

- 当前桥中的一个局部事实
- 某个对象应该怎么选
- 某个关系为什么成立

**示例**

同样这道题，第 2 轮不再问“新最长路有哪些候选路径”，而是改问：

> 如果路径经过新边，左边这一端应该接到什么样的点？

**通过后流转**

本设计建议：

- 第 2 轮通过后不再追加完整 `confirm_quiz`
- 可以保留一个很轻的系统内部确认，但不再额外展开新的题链
- 最终高层结果标为：
  - `mastery_status = assisted_success`

原因：

- 第 2 轮已经说明学生需要微提示
- 继续加完整确认题，收益小于复杂度

### Round 3: `final_micro_confirm`

**目标**

在补救讲解后，对前三轮围绕的这座桥做最后一个最小确认。

它不是第 4 轮教学，而是：

- 第 3 轮补救的收尾客观证据

**题目特点**

- 比第 2 轮还小
- 不考综合
- 不考迁移
- 不考整题
- 只确认最核心的那一个点

**适合考察的内容**

- 一个关键判断
- 一个对象选择
- 一句核心解释

**示例**

如果桥是“经过新边时两端都要接到最远点”，第 3 轮可以问：

> 这一端为什么不能接任意点？

或选择题版本：

> 这一端应该接：
- 任意点
- 离连接点最远的点
- 度数最大的点

**通过后流转**

- `learning_status = resolved`
- `mastery_status = assisted_success`

**失败后流转**

- `learning_status = needs_teacher_followup`
- `mastery_status = not_mastered`
- 创建 teacher flag
- 不再进入第 4 轮

---

## Product decisions absorbed from discussion

### 应吸收

#### 1. 结构化单轮优先于自由多轮对话

当前系统应该继续优先：

- 结构化复盘
- 有限轮次的 quiz ladder

而不是上自由聊天。

原因：

- 当前场景是“事后复盘”
- 重点是聚焦当前错误桥
- 不是开放探索

#### 2. `guided_walkthrough` 负责第一轮支架

`guided_walkthrough` 的职责是：

- 带学生走第一轮
- 不解决所有轮次的问题

如果学生仍未过桥，后续轮次通过更小 quiz 和补救继续推进，而不是把第一轮写得越来越长。

#### 3. 第 3 轮需要客观收尾证据

这是本次讨论最值得纳入系统的新结论。

当前讲解型补救后直接 `resolve`，证据偏弱。
因此应正式引入：

- 第 3 轮补救后的 `final_micro_confirm`

#### 4. `assisted_success` 不等于独立掌握

无论是第 2 轮还是第 3 轮通过，只要依赖了 follow-up 或补救，都只能记作：

- `assisted_success`

这条结论必须在：

- teacher UI
- 统计看板
- 后续评测

中保持一致。

### 暂缓吸收

#### 1. Level 2“基础概念 AI 微课”

讨论里提到“基础概念 AI”或预制微课层。这个方向不是没价值，但当前不应进入第一阶段实现。

原因：

- 复杂度高
- 需要额外知识点体系
- 当前收益不如先把三轮 quiz ladder 做稳

#### 2. 自由多轮桥接对话

当前阶段不进入。

原因：

- topic drift 风险高
- 当前已有 `main/followup/remedy` 足够先做结构化闭环

---

## Interface and state implications

### Current route names

当前系统已有这些 quiz 角色：

- `main`
- `followup`
- `confirm`
- `remedy`

本设计的对齐关系：

- `main` = Round 1
- `followup` = Round 2
- `remedy` quiz = Round 3 的题型实现
- `remedy` explain + `resolve` = Round 3 的讲解实现

### Required behavior changes

本设计建议新增或收紧以下行为：

1. 第 2 轮通过后，直接终局，不再追加完整 `confirm_quiz`
2. 如果第 3 轮走讲解型补救，讲解后应新增一个 `final_micro_confirm`
3. 第 3 轮的最终小题答错后，直接终局并转老师
4. 第 3 轮的最终小题答对后，直接记为 `assisted_success`

---

## Quiz generation rules

每一轮 quiz 生成时必须遵守：

### Rule 1

`target_bridge` 必须与上一轮一致。

### Rule 2

本轮题目粒度必须不大于上一轮。

### Rule 3

第 3 轮禁止考迁移题、变形题、整题整合题。

### Rule 4

第 3 轮通过与否都必须终局，不再派生新 quiz。

### Rule 5

如果某一轮无法稳定生成“结构事实题”，应退回解释/补救，而不是硬造坏题。

---

## Teacher meaning

老师侧应继续同时看到两层信息：

1. 高层结果
   - `independent_success`
   - `assisted_success`
   - `not_mastered`

2. 具体过桥路径
   - `main_clear`
   - `followup_correct`
   - `followup_remedy`
   - 等等

这两层不能互相替代：

- `mastery_status` 负责高层判断
- `bridge_path` 负责解释学生是怎么过桥的

---

## Success criteria

1. 三轮 quiz 各自的教学目标在代码和文档中都有统一定义
2. 第 2 轮通过后，系统稳定标记 `assisted_success`
3. 第 3 轮讲解型补救后，系统会给一个 `final_micro_confirm`
4. 第 3 轮后无论对错都停止，不进入第 4 轮
5. teacher 侧能继续稳定区分：
   - 独立过桥
   - 辅助后过桥
   - 仍未掌握
