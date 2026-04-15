# AI 复盘提速 + 并发处理 + 状态卡设计

## 目标

先把学生提交打卡后的等待体验变快，同时解决多人同时提交时的并发阻塞，但不在这一轮直接做“全文流式复盘”。

这份 spec 只做四件事：

1. 把 review / quiz 生成调用改成 `system / user` 分离
2. 把 `/api/checkins` 改成“创建成功即返回 `pending`，review 后台生成”
3. 给 review 生成链路加并发上限
4. 把学生端提交打卡后的体验改成“先拿到 `pending` 状态卡，再轮询刷新”

本 spec 不做：

- review 正文全文流式渲染
- SSE / WebSocket
- raw token 直接透传到学生端
- 单独新建状态页
- 动态进度条 / 队列位置显示
- 换架构、消息队列、Redis

---

## 一、问题判断

当前等待慢，主要是两层问题叠加：

1. `review_engine.py` 里的 `_call_llm(...)` 目前把 `system_prompt` 和 `user_prompt` 拼成一条 `user` 消息发送，没有做角色分离。
2. 学生端当前通过 `/api/checkins` 同步等待 review 结果，前端是普通 `fetch`，不是流式消费。
3. 当前多人同时提交时，review 生成在请求主链里串行阻塞，容易把后续请求一起拖慢。

因此，单独给 `_call_llm` 加 `stream=True`，并不能直接让当前页面边生成边显示。

更关键的是：

- review 现在是结构化 JSON 产物
- 模型输出后还要过 parse / guard / normalize

如果直接把原始 token 流到前端，学生可能先看到：

- 半截 JSON
- 未过 guard 的原始说法
- 中途被修正前的内容

所以这轮不直接做“全文流式”。

---

## 二、优先级

### 第一优先：`system / user` 分离

后端把长期规则和本次输入拆成两条消息：

- `system`：角色、输出契约、字段规则、长期教学约束
- `user`：当前题目、卡点、错误类型、反思、题目卡等本次上下文

目标：

- 让消息角色更清楚
- 让稳定规则部分可复用
- 为后续 Prompt Caching 和延迟优化打基础

### 第二优先：`pending` 快反馈 + 前端轮询

学生提交打卡后，不再优先追求“这一条请求里必须等到完整复盘”。

更稳的目标是：

- 先快速返回 `pending`
- 前端立刻显示“AI 正在整理复盘”
- 然后轮询单条状态接口
- 一旦 review 完成，再切到正式复盘视图

### 第三优先：未来再讨论 streaming

如果后面确实要做 streaming，优先考虑：

- 状态流
- 安全片段流

而不是原始全文 token 直出。

---

## 三、后端设计边界

### 1. `_call_llm(...)` 只改消息输入方式

从：

- 接收拼好的 `prompt: str`

改成：

- 接收 `messages: list[dict]`

例如：

```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
]
```

这一轮不要求 `_call_llm(...)` 同时承担 streaming 向前端透传职责。

### 2. review / quiz / problem_analysis 生成链路统一做角色分离

只要当前代码路径本来就有：

- `system_prompt`
- `user_prompt`

就不再拼成一条 `prompt = f"{system}\\n\\n{user}"`。

而是统一改成双 message 发送。

### 3. `/api/checkins` 的目标行为

目标不是“把 review 生成逻辑砍成大重构异步平台”，而是先保证学生端快速得到状态反馈。

第一版的目标行为直接定为：

- 创建 checkin 成功后，优先保证能返回一个明确状态
- 不再在请求线程里同步等待 review 完成
- review 生成改由 `BackgroundTasks` 触发
- 接口统一返回 `review_status = pending`
- 前端不把 pending 当失败

### 4. 单条状态接口

前端轮询不再依赖整包历史列表。

本轮需要新增：

- `GET /api/checkins/{checkin_id}`

该接口只返回当前 checkin 的最小状态视图，至少包含：

- `checkin_id`
- `problem_title`
- `created_at`
- `review_status`
- `review`
- `review_last_error`

目标：

- 让前端轮询成本更小
- 不必每次刷新整份历史记录

鉴权约束：

- 该接口必须通过 `require_student` 鉴权
- 只允许返回属于当前登录学生的 checkin 数据
- 如果 `checkin_id` 不属于当前学生，统一返回 `404`

### 5. `failed` 状态定义

既然前端要显示失败卡，就必须先定义失败状态。

本轮规则定死为：

- `pending`：后台仍在生成，或等待重试
- `completed`：review 已成功落库
- `failed`：本轮生成明确失败，且当前请求链不再自动继续

失败时：

- 数据库保留 `last_error`
- 学生端只显示统一失败文案
- 原始报错不直接暴露给学生
- `review_last_error` 仅供老师端或内部调试使用；学生端调用 `GET /api/checkins/{checkin_id}` 时，该字段固定返回 `null`

### 6. 学生端重试入口

既然失败卡上要有“重新生成”按钮，本轮必须同步定义对应后端入口。

建议本轮新增：

- `POST /api/checkins/{checkin_id}/review/retry`

行为：

- 仅允许该 checkin 所属学生触发
- 仅当 `review_status = failed` 时允许触发
- 如果当前状态是 `pending`，返回 `400`，提示“复盘正在生成中，请稍候”
- 如果当前状态是 `completed`，返回 `400`，提示“复盘已生成，无需重试”
- 把 review 状态重置回 `pending`
- 再次进入后台生成

### 7. 并发上限

本轮必须限制同时发给模型的 review 生成数量。

目标行为写死为：

- 最多同时 5 个 review 生成任务

但这一轮不把实现方式先写死成 `asyncio.Semaphore`。

原因：

- 当前主链里仍有同步调用路径
- 具体应使用异步信号量、线程信号量，还是其它轻量限流包装，应以现有执行模型为准

也就是说：

- spec 只规定并发上限是 `5`
- 实现时再选择与现有代码最贴合的限流方式

---

## 四、前端状态机

前端这轮不做流式正文渲染，只做状态型反馈，并且状态卡放在复盘工作台右侧区块，不新建页面。

### 提交后的状态

| 状态 | 前端行为 |
|---|---|
| `pending` | 继续轮询，显示“AI 正在整理复盘” |
| `completed` | 停止轮询，渲染复盘内容 |
| `failed` | 停止轮询，显示“生成失败，请重试”状态卡 |
| 轮询超时 | 停止轮询，显示超时状态卡 |

### 轮询规则

建议第一版写死简单规则：

- 前 3 次：每 `2s` 一次
- 之后：每 `5s` 一次
- 最大轮询时间：`60s`
- 超时后不再继续自动轮询

### `pending` 状态卡

右侧区块固定显示：

- 标题：`AI 正在整理复盘`
- 题目：当前 `problem_title`
- 提交时间：当前 checkin 创建时间
- 固定文案：`预计等待：约 15-30 秒`
- 一个手动刷新入口

这轮不显示：

- 队列位置
- 动态进度条
- 动态剩余时间

### `failed` 状态卡

右侧区块显示：

- 标题：`复盘生成失败`
- 文案：`你的打卡已保存，可以稍后重试。`
- 按钮：`重新生成`

### 超时状态卡

超时后不应继续让学生一直看转圈。

统一提示为：

- “复盘生成时间较长，请刷新页面或稍后查看历史记录。”

并提供：

- `刷新页面` 或 `重新获取状态` 按钮

---

## 五、为什么这轮不直接做全文 streaming

### 不做的原因

1. 当前前端不是流式消费架构。
2. 当前 review 是结构化 JSON，不是普通聊天文本。
3. 当前 review 生成后还要经过 parse / guard / normalize。
4. 直接流模型原始 token，会把不稳定中间态暴露给学生。

### 未来如果要做

未来应单独开一期设计，至少先定清：

1. 流的是：
   - 状态
   - 安全片段
   - 还是完整正文
2. 流的内容是否先过 guard
3. 前端如何处理中途失败、重试、断流

在这些问题没单独定清前，不应把全文 streaming 顺手塞进本轮。

---

## 六、实施顺序

### 第一组：先做低风险快反馈

1. `/api/checkins` 改成 `BackgroundTasks` 触发 review
2. 给 review 生成链路加“最多 5 个并发”
3. 新增单条状态接口 `GET /api/checkins/{checkin_id}`
4. 前端接入轮询状态机
5. 右侧区块接入 `pending / failed / timeout` 三种状态卡

### 第二组：单独收口 prompt 角色分离

6. `_call_llm(...)` 改为接收 `messages`
7. review / quiz / problem_analysis 的调用方统一改成 `system / user` 分离

原因：

- 第一组能先解决学生体感慢和多人并发堵塞
- 第二组改动面更广，适合单独回归验证

---

## 七、验收口径

这轮方向成立，至少应满足：

1. 学生提交打卡后 `2s` 内拿到 `pending` 响应。
2. 20 人同时提交时，请求不再彼此同步阻塞。
3. review 生成同时最多 5 个并发任务。
4. 前端轮询有明确终止条件，不会无限转圈。
5. `pending / failed / timeout` 三种状态卡都有对应 UI。
6. review / quiz / problem_analysis 调用链完成 `system / user` 分离。
7. 不把原始半截 review token 暴露给学生。
