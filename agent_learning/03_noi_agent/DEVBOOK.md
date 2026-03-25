# NOI Coach Agent - 开发笔记

## 项目结构

```
.
├── api_server.py        # FastAPI HTTP 服务器（主入口）
├── noi_agent.py         # 核心 Agent 逻辑（分级提示、配额管理）
├── auth.py              # JWT 认证
├── database.py          # SQLite 数据库（打卡、复盘、教师标记）
├── review_engine.py     # AI 复盘生成引擎
├── static/              # 前端静态文件
│   ├── index.html       # 主页面（标签页：答疑/打卡/历史）
│   ├── app.js           # 前端逻辑
│   └── style.css        # 样式
├── test_quota_logic.py  # 配额逻辑回归测试
├── quota.json           # 配额数据（JSON 存储）
└── noi_agent.db         # SQLite 数据库（自动创建）
```

## 功能模块

### 1. AI 答疑（原有功能）
- **端点**: `POST /chat`
- **功能**: 学生提问，Agent 提供分级提示
- **分级标签**: `[LEVEL:L1]` 引导思考, `[LEVEL:L2]` 具体提示, `[LEVEL:L3]` 直接指导, `[LEVEL:L4]` 代码
- **配额控制**: L2/L3 消耗配额，每题最多 3 次

### 2. 打卡复盘系统（新增）
- **端点**: `POST /api/checkins`
- **功能**: 学生完成题目后打卡，AI 自动生成复盘
- **输入验证**:
  - 卡点描述至少 15 字
  - 拒绝无效描述（如"不会"、"没思路"等笼统词汇）
- **复盘内容**:
  - 错误标签（如"DP优化", "状态设计"）
  - 问题诊断（具体分析）
  - 下一步行动（可执行建议）
  - 推荐专题（相关知识点）

### 3. 教师面板（新增）
- **端点**:
  - `GET /api/teacher/checkins` - 查看所有打卡
  - `GET /api/teacher/stats` - 错误类型统计
  - `GET /api/teacher/flags` - 关注学员列表
- **关注学员逻辑**:
  - 连续未完成 ≥3 题 → high
  - 平均完成度 <1.5 且打卡 ≥5 次 → medium
  - 打卡 <3 次 → low

## 环境配置

```bash
# 必须
export MOONSHOT_API_KEY="your_api_key_here"

# 可选（默认）
export JWT_SECRET="your_secret_here"  # 默认: noi_secret_key_change_in_production
export JWT_ALGORITHM="HS256"
export JWT_EXPIRE_HOURS="24"
```

## 启动服务

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

## API 测试

### 登录
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id":"student_a","password":"password"}'
```

### 学生打卡
```bash
curl -X POST http://localhost:8000/api/checkins \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_url": "https://www.luogu.com.cn/problem/P1001",
    "problem_title": "A+B Problem",
    "oj_source": "luogu",
    "completion_status": "hinted",
    "bottleneck_text": "详细描述卡点（至少15字）",
    "error_types": ["代码实现"],
    "reflection": "可选的反思"
  }'
```

### 教师查看统计
```bash
curl -H "Authorization: Bearer $TEACHER_TOKEN" \
  http://localhost:8000/api/teacher/stats
```

## 数据库 Schema

```sql
-- 打卡表
checkins: id, student_id, problem_url, problem_title, oj_source,
          completion_status, bottleneck_text, error_types, reflection, created_at

-- 复盘表
reviews: id, checkin_id, student_id, error_tags, diagnosis,
         next_action, suggested_topic, created_at

-- 教师标记表
teacher_flags: id, student_id, flag_type, reason, created_at
```

## 关键设计决策

### 配额逻辑（已验证）
- 只解析消息末尾的 `[LEVEL:L1/L2/L3/L4]` 标签
- 正文中的标签不触发配额扣除
- 已通过 10 个回归测试验证

### 存储分离
- 新功能（打卡、复盘）→ SQLite (`noi_agent.db`)
- 原有配额 → JSON (`quota.json`)
- 避免破坏原有逻辑

### XSS 防护
- 前端使用 `textContent` 而非 `innerHTML` 渲染动态内容
- 所有用户输入都经过 HTML escape

## 待优化

1. **AI 复盘**: 需要有效的 MOONSHOT_API_KEY
2. **前端**: 可考虑 React/Vue 重构
3. **部署**: Docker 化、反向代理配置
