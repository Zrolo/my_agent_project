# Review Prompt Split Design

## Goal

把当前堆在同一个 `review_prompt` 里的教学目标，拆成 3 套职责明确的 prompt：

- `normal_review_prompt`
- `clarify_prompt`
- `remedy_prompt`

目标不是一次做完整多轮对话，而是先降低单次 prompt 负担，减少规则漂移，让：

- 第一轮结构化复盘
- 模糊输入澄清
- 第二轮解释型补救

三种教学动作不再共享同一个大 prompt。

---

## Why

当前 [`review_engine.py`](/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py) 里已经存在两个问题：

1. 第一轮复盘 prompt 同时承担：
   - 教学目标
   - mode/family 路由
   - 新旧字段兼容
   - 长度限制
   - 一堆禁止项
2. 第二轮补救虽然行为不同，但仍然靠硬编码文案，不利于继续细化“缩小一步 / 换表示方式 / 纠正误解”的支架策略

因此这次设计的判断是：

> **继续往一个大 prompt 里加规则会漂；拆成单职责 prompt 才是在减负。**

---

## Scope

### 本次做

- 保留第一轮 `normal_review_prompt`
- 新增 `clarify_prompt`
- 新增 `remedy_prompt`
- 保持现有 API 形状不大改
- 让 `generate_remedy_explanation(...)` 真正走 `clarify/remedy` prompt + deterministic fallback

### 本次不做

- 不做自由多轮对话
- 不做 `bottom_out_prompt`
- 不大改前端协议
- 不重写整条 learning flow

---

## Prompt responsibilities

### 1. `normal_review_prompt`

负责第一轮结构化复盘：

- `problem_focus`
- `key_bridge`
- `guided_walkthrough`
- `try_now`
- `transfer_signal`

保留：

- `Evidence -> Decision -> Feedback`
- `ZPD + Adaptive Scaffolding`
- `family`
- `mode`

不再让它承担：

- 模糊输入澄清
- 第二轮补救文案
- 第三轮终局确认

### 2. `clarify_prompt`

只在证据不足时使用。

目标：

- 不讲题
- 不猜方法
- 帮学生把卡点说清楚

输出仍保持轻量：

- `remedy_text`
- `micro_action`

其中：

- `remedy_text` 解释为什么现在还不能直接讲题
- `micro_action` 只问一个最小澄清问题

### 3. `remedy_prompt`

只在第一轮未过后的解释型补救使用。

目标：

- 不重复第一轮复盘
- 只把桥缩小一步
- 或换一种表示方式
- 或纠正一个具体误解

输出同样保持：

- `remedy_text`
- `micro_action`

---

## Runtime routing

### A. 第一轮 review

`generate_review(...)`

- 继续走 `normal_review_prompt`

### B. 模糊输入 / insufficient

`generate_remedy_explanation(...)` 中：

- 如果 `error_layer == insufficient`
- 走 `clarify_prompt`
- 如果 LLM 失败或解析失败，回退到现有 deterministic clarify 文案

### C. 第二轮解释型补救

`generate_remedy_explanation(...)` 中：

- 如果 `error_layer != insufficient`
- 走 `remedy_prompt`
- 如果 LLM 失败或解析失败，回退到现有 deterministic remedy 文案

---

## Output contract

`clarify_prompt` 和 `remedy_prompt` 的输出 contract 统一为：

```json
{
  "remedy_text": "string",
  "micro_action": "string"
}
```

约束：

- `remedy_text` 必须解释当前为什么还不能继续讲整题
- `micro_action` 只能给一个 1 步内可回答或执行的小动作
- 禁止输出完整题解
- 禁止输出多个追问

---

## Fallback strategy

这次不把稳定性压在 LLM 上。

任何一个 prompt 调用失败时：

- 直接回退到当前 deterministic 文案
- 保证前端展示结构不变
- 保证学习流不崩

也就是说：

> **prompt split 提升的是教学表达，不牺牲系统稳定性。**

---

## Testing requirements

至少新增/更新以下测试：

1. `normal_review_prompt` 仍保留当前 5 段约束
2. `clarify_prompt` 明确要求“不讲题，只补证据”
3. `remedy_prompt` 明确要求“不重复第一轮，只缩小一步”
4. `generate_remedy_explanation(...)` 在 `insufficient` 时会走 clarify prompt
5. `generate_remedy_explanation(...)` 在非 `insufficient` 时会走 remedy prompt
6. LLM 失败时仍回退到 deterministic 文案
7. 默认回归继续通过

---

## Design decision

这次先不把 prompt 抽到单独文件模块。

原因：

- 当前最小风险路径是先在 [`review_engine.py`](/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/review_engine.py) 内完成函数级拆分
- 等 3 套 prompt 稳定后，再考虑抽到 `review_prompts.py` 或 `prompts/` 目录

所以本次的设计结论是：

> **先做函数级 prompt 拆分，先降模型负担，再考虑文件级迁移。**
