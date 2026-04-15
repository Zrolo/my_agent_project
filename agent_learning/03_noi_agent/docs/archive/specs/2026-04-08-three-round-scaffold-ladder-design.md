# Three-Round Scaffold Ladder Design

## Goal

在现有 `quiz / self-check / remedy` 学习闭环上，明确引入“最多三轮支架”的停机规则，并把最终结果收束成教师与系统都能消费的高层标记：

- `independent_success`
- `assisted_success`
- `not_mastered`

这次设计不引入开放式多轮聊天，也不重写现有 quiz/remedy 流程，只是在当前链路上补齐：

1. 明确的三轮封顶
2. 统一的最终掌握状态
3. 教师后台可见的高层标签

---

## Why

当前系统已经有：

- 首轮小测
- self-check
- follow-up quiz
- remedy explanation / easier quiz
- needs_teacher_followup

但还缺两件事：

1. 缺一个对外清晰的高层判断
   现在老师能看到 `bridge_path`，但还不能一眼看出这次是“独立过桥”“辅助后过桥”还是“仍未掌握”。

2. 缺一个显式的停机规则口径
   代码里已经隐含了上限，但系统层没有正式表达“到第三轮还没过桥就停止，并转老师跟进”。

---

## Core Model

### Scaffold rounds

把当前学习链路理解为最多三轮支架：

1. **Round 1: Main bridge**
   - 主理解小测
   - 或主复盘后的 self-check

2. **Round 2: Narrowed scaffold**
   - follow-up quiz
   - 或更小范围的桥接确认

3. **Round 3: Bottom-out scaffold**
   - remedy explanation
   - 或 remedy easier quiz

到第 3 轮后仍未通过，系统停止当前桥，不再继续第 4 轮，而是：

- 标记 `not_mastered`
- 进入 `needs_teacher_followup`
- 创建 teacher flag

### Mastery status

新增高层掌握状态：

- `not_assessed`
  - 当前 review 尚未走到终局，或历史数据无法稳定推断

- `independent_success`
  - 学生在首轮主路径上就把当前桥讲清楚/确认清楚
  - 对应当前典型 `bridge_path = main_clear`

- `assisted_success`
  - 学生最终过桥了，但明显依赖了后续支架
  - 包括：
    - `main_guessed_confirm`
    - `main_guessed_remedy`
    - `main_confused_remedy`
    - `followup_correct`
    - `followup_remedy`

- `not_mastered`
  - 三轮后仍未过桥
  - 或补救完成后仍需老师跟进

---

## Product behavior

### If the student still does not understand after three rounds

系统不继续无上限追问，也不继续堆更长解释，而是：

1. 停止当前桥
2. 返回“这道题我们先停在这里，老师会来和你一起看一看”
3. 标记 `mastery_status = not_mastered`
4. 保留 `learning_status = needs_teacher_followup`
5. 创建 teacher flag

### If the student eventually passes with support

系统不再把它看成“完全独立掌握”，而是：

1. 正常结束当前 review
2. 标记 `mastery_status = assisted_success`
3. 保留已有 `bridge_path`，供老师看具体过桥轨迹

---

## Data model

### reviews table

新增列：

- `mastery_status TEXT NOT NULL DEFAULT 'not_assessed'`

### Read model

以下查询统一带出：

- `mastery_status`
- 学生侧别名：`review_mastery_status`

涉及：

- student checkin list/detail
- review context
- teacher review samples
- review serialization

---

## Derivation rules

在 review 进入终局状态时统一推导：

### Rule 1

如果终局是 `needs_teacher_followup`：

- `mastery_status = not_mastered`

### Rule 2

如果终局是 `resolved` 且 `bridge_path == main_clear`：

- `mastery_status = independent_success`

### Rule 3

如果终局是 `resolved` 且 `bridge_path` 属于以下任一：

- `main_guessed_confirm`
- `main_guessed_remedy`
- `main_confused_remedy`
- `followup_correct`
- `followup_remedy`

则：

- `mastery_status = assisted_success`

### Rule 4

如果终局已到，但历史数据或特殊路径无法稳定推导：

- `mastery_status = not_assessed`

---

## Teacher UX

老师端要同时看到两层信息：

1. **高层结果**
   - `independent_success / assisted_success / not_mastered`

2. **具体过桥路径**
   - 继续保留现有 `bridge_path`

建议呈现方式：

- 高层 mastery badge
- 低层 bridge_path badge / note

这样老师既能快速筛，也能理解发生了什么。

---

## Scope for this phase

### Included

- `mastery_status` 数据列与推导
- 三轮封顶规则的正式化表达
- teacher sample card 显示 mastery badge
- 学生/历史详情接口透出 mastery status
- 测试覆盖：
  - confirm 过桥
  - remedy 后过桥
  - 失败后 teacher followup

### Not included

- 新的开放式 bridge dialogue
- 新的多轮状态机字段（如 `scaffold_round`, `student_progress`）
- 教师统计页按 mastery_status 分组
- 新的 prompt 体系

---

## Success criteria

1. 学生在 confirm 后过桥时，详情接口可见 `independent_success`
2. 学生在 remedy 后过桥时，详情接口可见 `assisted_success`
3. 学生在第三轮后仍未过桥时，详情接口可见 `not_mastered`
4. 教师 review sample 卡片能显示 mastery badge
5. 现有 `run_test.sh` 继续通过
