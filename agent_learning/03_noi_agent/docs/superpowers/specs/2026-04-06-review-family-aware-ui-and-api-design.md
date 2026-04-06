# Review 双 family 前后端契约设计

## 目标

在不重做 review 核心生成链路的前提下，把当前系统正式收敛成：

1. **两大复盘方向**
   - `failure_diagnosis`
   - `success_reflection`
2. **四个子 mode**
   - `failed_verdict`
   - `stuck_bridge`
   - `editorial_transfer`
   - `independent_reflect`
3. **一条统一的学生端主链**
   - 学生只描述事实，不直接选择 mode
   - 后端负责判定 mode 与 family
   - 前端在同一工作区里按 family 差异化渲染

本轮重点不是继续改 prompt，而是把“产品逻辑、接口契约、前端展示职责”说清楚，作为后续前后端接入和埋点实现的统一依据。

---

## 一、问题判断

当前系统已经形成了四个 mode 的 review 能力，但在产品实现层仍有一个隐含歧义：

- 教学逻辑上，我们已经把复盘分成了两大方向
- 但前端和接口层还没有正式承认这层 family

这会导致三个具体问题：

1. 前端不知道要不要拆成两个页面
2. 前端不知道 mode 应不应该由学生自己选择
3. 上线观测时，前后端都缺少对 family 的统一口径

因此，本轮要解决的不是“再发明一个新 UI”，而是统一这三个判断：

1. **mode 由后端判，不由学生选**
2. **family 是产品逻辑层，不一定对应两个独立页面**
3. **前后端要共享同一套 mode/family 契约**

---

## 二、最终决策

### 1. 正式承认两大 family

当前 review 系统的正式产品心智模型定义为：

#### `failure_diagnosis`

目标：
- 学生还没有建立起对当前题的主体性理解
- 系统的任务是帮助学生定位断点，建立关键事实，给出最小下一步

包含子 mode：
- `failed_verdict`
- `stuck_bridge`
- `editorial_transfer`

#### `success_reflection`

目标：
- 学生已经自己走通了当前题
- 系统的任务是帮助学生说明为什么这样做对，并抽出可迁移信号

包含子 mode：
- `independent_reflect`

### 2. 学生不直接选择 mode

学生端只提供事实输入，不直接暴露：

- `failed_verdict`
- `stuck_bridge`
- `editorial_transfer`
- `independent_reflect`

这四个 mode 名称不应作为学生按钮直接展示。

原因：
- 学生并不知道自己属于哪个教学模式
- 让学生直接选 mode，会把“事实采集”变成“教学判断外包给学生”
- 一旦学生选错，系统会在错误前提上生成复盘

### 3. 前端第一阶段不拆两个独立页面

本轮不做：
- 两个独立 review 页面
- 两套完全独立接口

本轮做：
- 一个统一 review 工作区
- 后端返回 `mode + family`
- 前端同页按 family 做差异化文案、顺序和反馈控件

### 4. 后端显式返回 `family`

第一阶段允许前端临时通过 `mode` 推导 `family`，但正式契约上应由后端直接返回：

```json
{
  "mode": "failed_verdict",
  "family": "failure_diagnosis"
}
```

原因：
- 防止前端自己维护映射表
- 避免未来扩 mode 后前后端口径漂移
- 为埋点和人工复核提供统一字段

---

## 三、两种实现方案比较

### 方案 A：两个独立页面 + 两个独立接口

做法：
- 失败/卡住型走一套页面和接口
- 做对/理解型走另一套页面和接口

优点：
- 产品表达清晰
- 两类体验边界很硬

缺点：
- 改动大
- 现有主链会被拆散
- 早期样本不足时容易过度设计

### 方案 B：一个页面 + 前端按 `mode` 自己猜 `family`

做法：
- 不改后端返回结构
- 前端根据 `mode` 自己判断 `family`

优点：
- 实现最快

缺点：
- 前端逻辑和后端逻辑会复制一份映射
- 后续扩 mode 易漂
- 埋点字段不统一

### 方案 C：一个页面 + 后端返回 `mode + family`

做法：
- 保持统一页面
- 后端显式返回 `mode + family`
- 前端根据 `family` 做差异化展示

优点：
- 改动小
- 契约清晰
- 适合当前系统阶段
- 便于后续接入埋点和人工复核

缺点：
- UI 层需要处理“同页双路径展示”

### 推荐

采用 **方案 C**。

原因：
- 最符合当前系统“核心 review 已可用，但正准备上线”的阶段
- 成本明显低于双页面方案
- 稳定性明显好于前端自己猜 family 的方案

---

## 四、学生输入与 mode 判定职责

### 1. 学生端采集的是事实，不是教学判断

学生端保留的输入包括：

- `completion_status`
- `submission_result`
- `bottleneck_text`
- `reflection`
- `problem_context`
- `student_code`

这些字段的作用是描述：
- 有没有做出来
- 有没有看题解
- 提交结果是对是错
- 具体卡点是什么

### 2. mode 判定由后端负责

后端根据事实输入判定：

- `failed_verdict`
- `stuck_bridge`
- `editorial_transfer`
- `independent_reflect`

第一阶段不改变现有核心 mode 判定逻辑，只要求：
- 将判定结果标准化暴露给前端
- 将判定结果暴露给观测埋点

### 3. family 由 mode 映射得出

映射规则固定为：

```text
failed_verdict      -> failure_diagnosis
stuck_bridge        -> failure_diagnosis
editorial_transfer  -> failure_diagnosis
independent_reflect -> success_reflection
```

正式实现中，这个映射由后端输出，不要求前端维护。

---

## 五、前端展示设计

### 1. 页面结构

本轮保持现有统一 review 工作区，不新增“失败页”和“理解页”。

现有工作区继续包含：
- review 主体
- quiz / self-check 区域
- 相关题目区域

### 2. family-aware 展示差异

#### `failure_diagnosis`

页面重点：
- 我到底错在哪 / 卡在哪
- 这题里的关键桥梁是什么
- 我现在先做哪一步

建议展示策略：
- `main_block`
- `key_bridge`
- `next_step`
- `transfer_signal`

文案语气：
- 更像“定位问题 + 最小入口”

说明：
- failure 方向先把学生带回“现在先查哪一步”，再补迁移信号；因此 `next_step` 放在 `transfer_signal` 前。

#### `success_reflection`

页面重点：
- 为什么这样做对
- 这题的核心决策流程是什么
- 下次看到什么题面特征会想到它

建议展示策略：
- `main_block`
- `key_bridge`
- `transfer_signal`
- `next_step`

文案语气：
- 更像“解释为什么成立 + 迁移”

说明：
- success 方向先帮助学生说清“为什么这道题可迁移”，再给回到原题的验证动作；因此 `transfer_signal` 放在 `next_step` 前。

### 3. review 反馈问题要按 family 分开

#### failure_diagnosis 方向

推荐反馈主问题：
- `现在知道先查哪一步了吗？`

推荐差评原因：
- 太抽象
- 不贴这道题
- 还是不知道先从哪下手
- 说得对，但我不会查

#### success_reflection 方向

推荐反馈主问题：
- `现在能说清为什么这样做对了吗？`

推荐差评原因：
- 太抽象
- 不贴这道题
- 还是说不清为什么对
- 知道结论，但不会迁移

---

## 六、后端接口契约调整

### 1. `POST /api/checkins`

当前职责不变：
- 创建 checkin
- 启动 review 生成

本轮新增要求：
- 为本次 checkin 建立可追踪 `session_id`
- 后续返回结构中允许前端拿到 family 判定结果

补充约束：
- 第一阶段将 `session_id` 视为一次 checkin / 一次 review 会话的 1:1 标识。
- `session_id` 在 checkin 创建时写入并持久化，后续由 `GET /api/checkins/{checkin_id}` 直接返回，不单独引入 1:n 会话层。

### 2. `GET /api/checkins/{checkin_id}`

当前会返回 review 内容。

本轮新增要求：
- 返回 `review_mode`
- 返回 `review_family`

推荐返回片段：

```json
{
  "checkin_id": 123,
  "review_status": "completed",
  "review_mode": "stuck_bridge",
  "review_family": "failure_diagnosis",
  "review": {
    "main_block": "...",
    "key_bridge": "...",
    "next_step": "...",
    "transfer_signal": "..."
  }
}
```

### 3. `GET /api/checkins/{checkin_id}/stream`

当前职责保持：
- 推送生成状态

本轮不要求：
- 在 SSE 事件里立即加 family-aware 内容

原因：
- family 展示由最终详情接口驱动即可
- 本轮不扩大 SSE 复杂度

---

## 七、与上线观测的关系

这份 spec 与 `review_observability_spec.md` 的关系如下：

### 本文解决
- family 是什么
- mode/family 由谁判断
- 前端为什么不拆双页面
- 学生为什么不直接选 mode

### 观测 spec 解决
- 上线后如何知道 mode 分得对不对
- 学生是否看懂
- 哪类输入导致差复盘
- 时延是否可接受

因此，后续埋点字段应直接使用：
- `review_mode`
- `review_family`

避免前端再二次推断。

---

## 八、本轮不做

本轮明确不做：

- 两个独立 review 页面
- 两套独立 review 接口
- 让学生直接选择 mode
- 改 review prompt 或 review schema
- 改 quiz 主链逻辑

---

## 九、实现顺序

### 第一步：后端补 family 契约

做法：
- 在现有 checkin / review 返回结构中补 `review_mode + review_family`

### 第二步：前端同页差异化渲染

做法：
- 不拆页面
- 根据 `review_family` 调整：
  - 字段顺序
  - 标题文案
  - 反馈问题

### 第三步：埋点与人工复核接入

做法：
- 埋点统一带 `review_mode + review_family`
- 人工复核也按同样口径判断

---

## 十、验收标准

本 spec 落地后，至少满足：

1. 学生端不存在 mode 选择按钮
2. 后端返回中存在 `review_mode` 与 `review_family`
3. 前端可以在同一工作区中根据 family 显示不同文案
4. 上线埋点字段与人工复核字段都能使用同一套 `mode/family` 口径

---

## 十一、为什么现在要先写这份 spec

当前 review 核心能力已经足够上线。

接下来最容易产生混乱的，不是 prompt 本身，而是：
- 前端会不会误以为要做双页面
- 后端会不会继续只暴露 mode、不暴露 family
- 埋点字段会不会和真实产品逻辑脱节

这份 spec 的作用，就是在真正实现前，把这三个分叉点提前收敛。
