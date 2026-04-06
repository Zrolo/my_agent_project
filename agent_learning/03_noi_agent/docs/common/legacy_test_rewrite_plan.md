# 旧测试重写计划

## 这份计划解决什么问题

仓库里仍保留两条历史测试：

- `test_review_api_flow.py`
- `test_v1_2_flow.py`

它们本身不是无价值，而是依赖的系统前提已经变了：

- review 现在是异步生成
- quiz 现在依赖 review 已完成
- 一些列表字段也不再按旧时序立即回显

所以这份计划的目标不是“删掉旧测试”，而是：

1. 说明它们为什么不再能当默认绿灯
2. 说明各自应该怎么重写
3. 约定重写完成前的降级策略

---

## 一、`test_review_api_flow.py` 重写计划

### 当前旧测试在测什么

它现在主要覆盖三件事：

1. `validate_bottleneck(...)` 的基本放行逻辑
2. review 生成异常时，checkin 是否保留
3. 学生是否能伪装他人身份

### 为什么当前会失败

旧断言默认认为：

- review 生成异常后
- `GET /api/checkins/me`
- 立刻能从 `review_last_error` 读到 `RuntimeError(...)`

但当前真实行为是：

- checkin 会保留
- review 保持 `pending`
- 历史列表接口不再立刻回显旧测试预期里的错误字符串

也就是说，**业务目标没丢，但观察点已经变了**。

### 应该怎么重写

建议改成下面这组断言：

#### 1. 保留的断言

- `POST /api/checkins` 返回 `200`
- `review_status == "pending"`
- `review is None`
- `GET /api/checkins/me` 里还能查到这条 checkin
- `problem_context` 等有效字段没有丢

#### 2. 删除或替换的旧断言

- 删除：
  - “历史列表里的 `review_last_error` 必须立刻包含 `RuntimeError`”

#### 3. 替代断言建议

二选一：

##### 方案 A：只测“保留 checkin，不测错误展示”

优点：

- 最稳
- 只验证当前 API 合同里仍稳定存在的行为

缺点：

- 不再覆盖“异常细节是否可观测”

##### 方案 B：改成查更适合的错误落点

如果后续你们决定让错误进入：

- review detail 接口
- review event
- teacher 失败重试队列

那就应该改成测那个**当前真实承载错误语义的位置**，而不是历史列表。

### 推荐重写口径

优先推荐 **方案 A**：

> 把它收成“checkin 创建与保留 + 学生权限边界”的轻量 API 回归

---

## 二、`test_v1_2_flow.py` 重写计划

### 当前旧测试在测什么

它想测的是一整条学习路径：

- main quiz
- self-check
- confirm
- remedy
- bridge_path

### 为什么当前会失败

旧测试默认假设：

- 创建 checkin 后
- review 已经同步完成
- 所以可以立刻调用 `/api/reviews/{review_id}/quiz/generate`

但当前真实行为是：

- review 是异步生成
- review 未完成时，`quiz/generate` 会返回：
  - `400: 复盘尚未完成，暂时不能生成理解小测`

所以失败点不是 quiz 本身，而是**测试前置条件已经失效**。

### 应该怎么重写

建议把它拆成两层：

#### 1. 前置等待层

新 helper 需要先等待 review 进入 `completed`

可以用两种方式：

##### 方案 A：轮询 `GET /api/checkins/{id}`

轮询直到：

- `review_status == "completed"`

优点：

- 最贴近真实 API 行为

##### 方案 B：在测试里直接 stub 成同步完成

优点：

- 更快
- 更稳定

缺点：

- 不覆盖当前异步主链

#### 2. 学习流断言层

在确认 review 已完成后，再继续测：

- `quiz/generate`
- `answer`
- `self-check`
- `confirm`
- `remedy`

### 推荐重写口径

推荐分成两条测试：

1. 一条**轻量异步前置测试**
   - 只确认 review 未完成时 quiz 不能生成
   - review 完成后 quiz 才能生成

2. 一条**学习流状态机测试**
   - 不再把“等待 review 完成”混在主状态机断言里
   - 主状态机专注测 `main_clear / guessed / confused / confirm / remedy`

这样更符合当前系统结构。

---

## 三、重写前的降级策略

在这两条旧测试重写完成之前：

| 项目 | 当前策略 |
| --- | --- |
| `run_test.sh` | 不再运行这两条旧测试 |
| `TESTING.md` | 明确标记这两条为“待重写” |
| 发布判断 | 不依赖这两条旧测试是否全绿 |
| 文件保留 | 保留，不删除 |

---

## 四、建议的重写顺序

| 顺序 | 项目 | 原因 |
| --- | --- | --- |
| 1 | `test_review_api_flow.py` | 改动小，先把最基础 API 回归收稳 |
| 2 | `test_v1_2_flow.py` | 涉及异步前置和学习流拆层，复杂度更高 |

---

## 五、完成标准

只有满足下面两条，才算旧测试重写完成：

1. 新测试断言基于**当前真实 API 合同**，而不是历史同步假设
2. 重写后的测试能重新纳入 `run_test.sh` 或新的默认测试入口
