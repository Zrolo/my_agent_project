# 学生端页面契约修复设计

## 背景

当前学生端已经有历史列表与历史详情 URL，但页面语义仍然混杂：

- `/app/history/:checkin_id` 的 URL 语义是“历史详情”
- 实际 DOM 却切到了“打卡复盘工作区”
- `/app` 还同时承担聊天页和打卡输入页含义
- 历史详情缺显式“返回历史列表”

这会导致：

- 浏览器返回路径不稳定
- 刷新恢复语义不清
- 历史详情与当前工作区职责缠绕

## 目标

在不重写整站 UI 的前提下，建立稳定的学生端页面契约：

- `/app/chat`
- `/app/checkin`
- `/app/history`
- `/app/history/{checkin_id}`

同时让历史详情真正属于“历史打卡”语义，而不是复用“打卡工作区”。

## 设计

### 1. 学生端路由

新增明确路由种类：

- `chat`
- `checkin`
- `history-list`
- `history-detail`

兼容规则：

- `/app` 作为旧入口，解析时视为 `chat`
- 其余路径走显式页面语义

### 2. 页面职责

#### `/app/chat`

- 只负责 AI 解答页

#### `/app/checkin`

- 只负责新建打卡输入页
- 不再承载历史复盘详情

#### `/app/history`

- 负责历史打卡列表
- 默认显示列表阶段

#### `/app/history/{checkin_id}`

- 负责某条历史复盘详情
- 详情页仍使用现有复盘讲义 + 学习路径 + 推荐练习布局
- 但放在历史标签页内部的“详情阶段”中

### 3. 历史页双阶段

`history-tab` 内部拆成两个阶段：

- `history-list-stage`
- `history-detail-stage`

行为：

- 进入 `/app/history` 时显示列表阶段
- 进入 `/app/history/{id}` 时显示详情阶段
- 详情阶段提供显式“返回历史列表”按钮

### 4. 现有复盘详情壳迁移

当前 `checkin-review-stage` 迁入 `history-detail-stage`，保留已有 ID 和渲染逻辑：

- `active-review-title`
- `active-review-subtitle`
- `active-review-meta`
- `active-review-quiz-slot`
- `active-review-report`
- `active-review-related`

这样可以最小化业务逻辑改动。

### 5. 提交流转

新建打卡成功后：

- 不再停留在 `/app/checkin`
- 而是切到 `/app/history/{checkin_id}`
- 学生会直接看到这条新记录的复盘详情

这样“输入页”和“历史详情页”的职责清楚分开。

## 非目标

这次不做：

- teacher 侧路由化
- 整站大规模组件拆分
- 历史列表/详情的数据层重写

## 验收标准

- `/app/chat`、`/app/checkin`、`/app/history`、`/app/history/{id}` 都可直接打开
- 点击历史记录后，历史标签保持激活，进入详情阶段
- 详情页有显式“返回历史列表”
- 新建打卡成功后进入对应历史详情 URL
- 浏览器返回键可在历史列表和详情之间正确切换
