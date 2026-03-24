# NOI 竞赛教练 Agent - 项目记忆文档

> 本文档记录项目当前状态，供AI审核时快速了解上下文
> 最后更新：2026-03-24

---

## 1. 项目背景

### 1.1 目标
构建一个专为信息学竞赛（NOI/CSP-J/S/NOIP）教学设计的AI答疑Agent，核心差异化是**防止学生产生AI依赖**。

### 1.2 核心问题
- 通用AI（豆包/ChatGPT）直接给答案，导致学生依赖
- 教练需要反复回答相似基础问题，时间被占用
- 缺乏对学生"思考过程"的追踪和引导

### 1.3 解决方案
**苏格拉底式引导 + 分层配额机制**：
- 学生不展示思考 → Agent只反问（L1，不扣配额）
- 学生展示思考 → Agent给方向提示（L2，扣1次）
- 仍卡住 → Agent给代码片段（L3，扣1次）
- 配额耗尽 → 转人工（L4，不扣配额）

---

## 2. 技术架构

### 2.1 技术栈
- **LLM API**: Moonshot (Kimi) - `moonshot-v1-8k`
- **存储**: JSON文件（无数据库，无RAG）
- **语言**: Python 3.x
- **依赖**: `openai`库（Kimi兼容OpenAI格式）

### 2.2 核心设计决策
| 决策 | 说明 |
|-----|------|
| 轻量级 | 无LangChain、无ChromaDB、无向量数据库 |
| 本地存储 | quota.json文件存储配额，简单可靠 |
| 每题配额 | 每道题独立3次配额，换题重置 |
| 级别自标注 | LLM在回复末尾标注[LEVEL:Lx]，代码读取判定 |

---

## 3. 当前实现状态

### 3.1 已实现功能 ✅

#### 配额管理系统
```python
# quota.json 结构
{
  "学生ID": {
    "题目ID": {"count": 0, "max": 3}
  }
}
```
- `load_quota()` / `save_quota()` - 配额读写
- `consume_quota()` - 扣减配额，返回(成功, 剩余次数)
- `get_remaining_quota()` - 获取剩余配额

#### 级别判定系统
- **优先策略**: 读取LLM回复末尾的 `[LEVEL:Lx]` 标签
- **备用策略**: 标签缺失时，检测代码块（```）→ 判定为L3
- **保守策略**: 其他情况一律不扣配额

#### 对话管理
- `chat()` 函数返回 `tuple[display_reply, history_reply]`
- `display_reply`: 带配额提示，展示给学生
- `history_reply`: 干净内容（去标签、无配额提示），存入messages
- **解决重复提示问题**: 存历史和展示内容分离

#### 配额耗尽处理
- `generate_farewell_gift()` - 返回"临别礼物"（知识点总结+学习建议）
- 配额为0时不调用LLM，直接返回临别礼物

### 3.2 System Prompt 关键规则
```
## 分层响应规则
L1 - 引导反问（不消耗配额）
L2 - 方向提示（消耗1次配额）
L3 - 关键代码片段（消耗1次配额）
L4 - 转交老师（不消耗配额）

## 强制标注规则（必须遵守）
每次回复的最后一行必须是以下标签之一：
[LEVEL:L1]
[LEVEL:L2]
[LEVEL:L3]
[LEVEL:L4]

标签单独一行，放在回复最后，不加任何解释。
这条规则优先级最高，无论回复多长，最后一行必须是标签，不能省略。
```

---

## 4. 代码文件结构

```
03_noi_agent/
├── noi_agent.py           # 主程序（最新修复版）
├── quota.json             # 配额存储（运行时生成）
├── PROJECT_MEMORY.md      # 本文档
├── review_checklist.md    # AI审查清单
├── request_review.py      # 生成审查请求脚本
├── test_quota.py          # 自动化测试脚本
├── run_conversation_test.py  # 对话测试脚本
└── review_result.md       # 上次审查结论
```

---

## 5. 已知问题与解决方案

### 5.1 已修复 ✅

| 问题 | 解决方案 |
|-----|---------|
| 配额绑定维度不明确 | 改为两层嵌套：`{学生ID: {题目ID: {count, max}}}` |
| consume_quota()未被调用 | LLM自标注级别 + 代码读取标签自动扣减 |
| L1误判扣配额 | 改为LLM自标注级别，不再关键词匹配 |
| 配额提示重复出现 | display_reply和history_reply分离存储 |

### 5.2 当前限制 ⚠️

| 限制 | 说明 | 缓解方案 |
|-----|------|---------|
| LLM标签稳定性 | 约30%概率不输出[LEVEL:Lx]标签 | 备用检测：代码块→L3，其他→不扣 |
| API引擎过载 | 偶发429错误 | 重试机制（sleep 10-30s） |
| 无真实RAG | 临别礼物是模板，非个性化 | MVP阶段可接受，后续迭代 |

---

## 6. 测试验证结果

### 6.1 最新测试结果（修复重复提示后）

| 轮次 | 输入 | 标签识别 | 备用检测 | 扣减 | count |
|-----|------|---------|---------|------|-------|
| 1 | "这道题我不会做" | L1 | - | 0 | 0 |
| 2 | "我觉得可能要用递归..." | 无标签 | 无代码块 | 0 | 0 |
| 3 | "可以给我看一下代码吗" | 无标签 | 有代码块 | 1 | 1 |

**最终**: count=1/3 ✅

### 6.2 验证点
- ✅ 存进messages的内容无配额提示
- ✅ 给学生看的回复有配额提示
- ✅ 配额扣减逻辑正确（L2/L3扣，L1/L4不扣）
- ✅ 配额耗尽时返回临别礼物

---

## 7. 审核要点（供AI参考）

### 7.1 核心逻辑检查
1. **配额绑定**: 是否正确绑定到（学生ID + 题目ID）？
2. **扣减时机**: 是否在LLM回复后、展示前扣减？
3. **级别判定**: 标签检测 + 备用检测逻辑是否正确？
4. **历史存储**: 是否存储干净内容（无配额提示）？

### 7.2 边界条件检查
1. **配额为0**: 是否直接返回临别礼物，不调用API？
2. **标签缺失**: 备用检测是否合理（宁可少扣不误扣）？
3. **多轮对话**: messages累积是否导致上下文过长？
4. **异常处理**: API报错时程序是否崩溃？

### 7.3 代码质量检查
1. **函数职责**: chat()是否做太多事情？
2. **错误处理**: 是否有try-except包裹API调用？
3. **可读性**: 关键逻辑是否有注释？
4. **扩展性**: 如果要改配额数字，是否只需改一处？

---

## 8. 下一步计划

### 8.1 短期（本周）
- [ ] 找1-2名学生真实测试，观察接受度
- [ ] 收集真实问答数据，优化System Prompt
- [ ] 处理API 429错误，加指数退避重试

### 8.2 中期（2-4周）
- [ ] 接入简单的知识库（常见错误案例）
- [ ] 优化LLM标签稳定性（Prompt工程）
- [ ] 添加老师后台查看学生进度

### 8.3 长期（1-3月）
- [ ] 多Agent协作（答疑→推题→追踪）
- [ ] 学生画像系统（薄弱点分析）
- [ ] 沉淀数据资产，形成壁垒

---

## 9. 关键代码片段

### 9.1 级别判定逻辑
```python
def detect_quota_consumption(reply: str) -> bool:
    # 第一优先：找标签
    match = re.search(r'\[LEVEL:(L\d)\]', reply)
    if match:
        level = match.group(1)
        return level in ("L2", "L3")
    
    # 备用：只检测最可靠的特征
    if "```" in reply:  # L3：有代码块
        return True
    
    # 其他情况一律不扣（保守策略）
    return False
```

### 9.2 对话处理逻辑
```python
def chat(messages, student_id, problem_id) -> tuple[str, str]:
    # ... 调用LLM ...
    
    level, clean_reply = parse_level_tag(raw_reply)
    
    if detect_quota_consumption(raw_reply):
        consume_quota(student_id, problem_id)
        reply_for_display = clean_reply + "\n\n---\n💡 还剩X次"
    else:
        reply_for_display = clean_reply + "\n\n---\n💡 还剩X次（本次未消耗）"
    
    reply_for_history = clean_reply  # 干净内容存历史
    
    return reply_for_display, reply_for_history
```

---

## 10. 当前状态（实时更新）

### 10.1 代码提交状态 ✅
- **提交ID**: `27e257b`
- **提交信息**: `Fix quota: label-based detection + split display/history`
- **推送状态**: ✅ 已推送到 GitHub
- **仓库地址**: https://github.com/Zrolo/my_agent_project

### 10.2 当前阻塞问题 🔴
**API 服务不稳定** - 遇到 503 Service Unavailable 错误
```
Unexpected status 503: All providers unavailable
url: https://moacode.org/v1/responses
```

**影响**: 
- 无法进行真实对话测试
- LLM级别标注稳定性验证受阻

**临时方案**:
- 等待服务恢复（503通常是临时性）
- 或添加指数退避重试机制

### 10.3 最新验证结果
在API可用时，已验证：
- ✅ 配额绑定逻辑正确（学生+题目维度）
- ✅ 级别判定逻辑正确（标签优先+代码块备用）
- ✅ 重复提示问题已解决（display/history分离）
- ✅ 三轮对话测试通过

### 10.4 下一步行动
| 优先级 | 任务 | 状态 |
|-------|------|------|
| P0 | 处理API 503错误，加自动重试 | 待做 |
| P1 | 找真实学生测试接受度 | 等API恢复 |
| P2 | 优化System Prompt提高标签稳定性 | 等API恢复 |

---

## 11. 快速状态摘要（给其他AI）

```
【NOI Agent 当前状态 - 2026-03-24】

✅ 已完成：
- 配额系统：每题3次，绑定学生+题目维度
- 级别判定：LLM自标注[LEVEL:Lx]标签 + 代码块备用检测
- 对话管理：display_reply（带配额提示）和 history_reply（干净内容）分离
- 代码已提交并推送到GitHub

🔴 当前阻塞：
- API 503错误，服务暂时不可用
- 无法进行真实对话测试验证

📋 需要帮忙：
1. 审查当前代码逻辑是否有漏洞
2. 设计API 503错误的重试机制
3. 优化System Prompt提高标签稳定性（当前约70%成功率）

📁 关键文件：
- noi_agent.py: 主程序
- PROJECT_MEMORY.md: 完整项目文档
- quota.json: 配额存储

💻 运行测试：
cd ~/Downloads/my_agent_project/agent_learning/03_noi_agent
export MOONSHOT_API_KEY=xxx
python3 noi_agent.py
```

---

## 12. 审查请求模板

如需AI审查，使用以下模板：

```
【NOI Agent 审查请求】

项目状态：见 PROJECT_MEMORY.md 第10节"当前状态"
改动文件：noi_agent.py
改动范围：[填写具体修改]
改动目的：[填写目的]
当前阻塞：[如有，说明API 503等问题]

请重点审查：
1. [具体检查点1]
2. [具体检查点2]
3. [具体检查点3]

参考文档：
- PROJECT_MEMORY.md: 完整项目背景和当前状态
- review_checklist.md: 审查维度清单
```

---

**文档结束 - 最后更新：2026-03-24**