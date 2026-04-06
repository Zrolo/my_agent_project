# NOI Agent v2.1 升级摘要

## 新增功能

### 1. MiniMax 意图预分类器 (`classifier.py`)
- **功能**: 对学生输入进行意图分类
- **输出类别**:
  - `direct`: 直接索取答案/代码
  - `type_confirm`: 猜测或确认题型/方法
  - `bridge`: 索取关键算法桥梁
  - `substantive`: 有一定实质尝试
- **特点**:
  - 2秒超时保护
  - 失败时优雅降级为代码层逻辑
  - 仅用于**降级**限制，永不升档

### 2. 硬门控机制 (`enforce_level_gate`)
- **位置**: `noi_agent.py:689-717`
- **功能**: 模型输出级别超过 `max_level` 时强制降级
- **兜底回复**:
  - L1: "先别想快不快。最笨的方法你会怎么做？"
  - L2: "这道题你最终要记录什么信息？"
- **关键**: 降级在**配额消耗前**执行，防止超限

### 3. Session ID 会话隔离
- **API**: `ChatRequest` 模型新增 `session_id` 字段
- **存储**: `session_histories[(student_id, problem_id, session_id)]`
- **前端**: 自动生成并存储在 localStorage
- **好处**: 同一学生同一题目的不同会话完全隔离

### 4. 教师密钥认证
- **环境变量**: `NOI_TEACHER_SECRET`
- **端点**: `POST /quota/reset`
- **验证**: 403 如果密钥不匹配
- **前端**: 重置表单新增密码输入框

### 5. Type Confirm 特殊处理
- **触发**: 当分类器检测到题型确认意图
- **行为**: 
  - 强制限制 max_level <= L2
  - Prompt 添加特殊约束
  - **绝对禁止**确认题型（不能说"对，这是DP"）
  - **必须反问**: "你为什么会这么猜？题目里哪个特征让你想到这个方法？"

## 文件变更

| 文件 | 变更 |
|------|------|
| `classifier.py` | 新增 MiniMax 意图分类器 |
| `noi_agent.py` | 添加 `merge_intent_with_control()`, `enforce_level_gate()` |
| `api_server.py` | 添加 session 存储, teacher_secret 验证 |
| `static/index.html` | 添加 teacher_secret 输入框 |
| `static/app.js` | 添加 sessionId 生成/存储/使用 |
| `.env.example` | 添加 MINIMAX_API_KEY, NOI_TEACHER_SECRET |
| `requirements.txt` | 添加 requests 依赖 |

## 环境变量要求

```bash
# 必需
MOONSHOT_API_KEY=xxx          # Kimi API
NOI_TEACHER_SECRET=xxx        # 教师重置配额密钥

# 可选
MINIMAX_API_KEY=xxx           # MiniMax 分类器（未设置则只用代码层）
MINIMAX_GROUP_ID=xxx          # 部分账号需要
```

## API 变更

### POST /chat
**请求体**:
```json
{
  "student_id": "S001",
  "problem_id": "P1001",
  "message": "这题怎么做？",
  "session_id": "sess_abc123"  // 新增
}
```

### POST /quota/reset
**请求体**:
```json
{
  "student_id": "S001",
  "problem_id": "P1001",
  "teacher_secret": "your_secret"  // 新增
}
```

## 控制流（简化）

```
学生输入
  ↓
┌─────────────────────────────────────┐
│ 1. 检查配额 (get_remaining_quota)   │
│    - 耗尽则返回 farewell gift       │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 2. 代码层分析 (analyze_student_turn)│
│    - L1 强拦关键词                  │
│    - L3 证据检测                    │
│    - 桥梁套取识别                   │
│    - L2 槽位分析                    │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 3. MiniMax 分类 (classify_intent)   │
│    - 超时2秒，失败则跳过            │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 4. 合并控制 (merge_intent_with_)    │
│    - 仅降级，永不升档               │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 5. 构建 Prompt (build_system_)      │
│    - 注入控制块                     │
│    - type_confirm 特殊约束          │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 6. 调用 LLM (moonshot-v1-8k)        │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 7. 硬门控 (enforce_level_gate)      │
│    - 模型级别 > max_level?          │
│    - 是: 强制降级 + 兜底回复        │
│    - 否: 保持原样                   │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 8. 配额消耗 (consume_quota)         │
│    - 基于 enforced_level            │
│    - L2/L3 消耗配额                 │
│    - L1 不消耗                      │
└─────────────────────────────────────┘
  ↓
返回 (display_reply, history_reply)
```

## 降级策略总结

| 触发条件 | max_level | bridge_redline | 兜底回复 |
|---------|-----------|----------------|---------|
| 直接索取代码 | L1 | - | "先别想快不快。最笨的方法..." |
| 极短无思考 | L1 | - | 同上 |
| 情绪催促 | L1 | - | 同上 |
| 只复述题意 | L1 | - | 同上 |
| 猜测题型 | L2 | - | "你为什么会这么猜？" |
| 索取桥梁 | L2/L3 | True | 可指错，不可补正确答案 |
| 无L3证据 | L2 | - | 槽位化追问 |
| 有L3证据 | L3 | False | 针对性指出问题 |

## 启动命令

```bash
cd /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent
source .env
uvicorn api_server:app --reload --port 8000
```

访问: http://localhost:8000
