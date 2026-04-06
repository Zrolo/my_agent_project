# 项目长期规则（跨多轮任务不应漂移）

## 本文件的写入标准

只写**长期成立、跨多轮任务都不应漂移**的规则。

适合写：

- 产品信息架构原则
- 教学红线
- 题库接入边界
- prompt / harness 的优先级关系

不要写：

- 当前暂时的实现状态
- 还没落地的方案
- 局部 bug
- 某一轮任务的临时约束

---

## 一、学生端长期信息架构

1. 学生端长期固定为三个一级入口：
   - `AI 解答`
   - `打卡复盘`
   - `历史打卡`

2. 下列内容不是页面，而是**打卡复盘工作台内部的阶段状态**：
   - 复盘已生成
   - 小测进行中
   - self-check
   - 补救中

3. `历史打卡` 是学生区内部独立标签，不单独新增站外页面或新路由。

4. `历史打卡` 的角色仍然是**上下文选择器**，不是单纯展示列表：
   - 历史页负责紧凑浏览和选择记录
   - 选中记录后回到 `打卡复盘` 工作台继续看对应状态

5. 当前推荐的学生端工作台结构是：
   - 左侧：提交与历史
   - 中间：小测 / self-check / remedy
   - 右侧：AI 复盘 / 同类题 / 同题最近 AI 解答摘要

---

## 二、学生端响应式规则

1. 宽屏桌面端：
   - 左 / 中 / 右三段并排

2. 中等屏幕：
   - 左侧收窄
   - 保留中右主工作区

3. 移动端单栏顺序固定为：
   1. 右侧复盘
   2. 中间小测
   3. 左侧提交与历史

原因：
- 学生通常先看解释，再做题，不是反过来

---

## 三、AI 解答 与 复盘工作台 的关系

1. `AI 解答` 和 `复盘工作台` 是两个工作入口，不是两套孤立数据。

2. 如果学生先在 `AI 解答` 里问了某题，再去复盘同一道题，系统应允许把：
   - 同题最近 AI 解答摘要
作为辅助上下文带入复盘。

3. 这种上下文只能是**辅助线索**，不能替代：
   - 本次卡点描述
   - 本次错误类型
   - 本次代码 / 提交现象

---

## 四、quiz 红线（长期教学约束）

1. 学生端 quiz 禁止元认知口号题。

2. 判断标准不看题面是否像“怎么做”，而看：
   - **正确答案到底是结构事实，还是学习建议**

3. 如果正确答案本质上是：
   - 学习建议
   - 思维态度
   - 方法口号
   - 泛化流程
则该题不合格。

4. 学生端 quiz 正确答案必须落在这些之一：
   - 具体定义
   - 具体关系
   - 具体条件
   - 具体顺序
   - 具体维护量
   - 具体代价 / 价值 / 状态含义

5. judgement（对/错）题不再是主线 quiz 题型。

6. `main / followup / confirm` 都必须以结构事实为答案，不允许退回口号题。

---

## 五、main / followup / confirm 的长期边界

### `main`
- 在原题语境里测当前桥梁的最小结构事实

### `followup`
- 仍然用原题语境
- 但比 main 更小、更单步

### `confirm`
- 目标不是更简单，而是换一个角度验证**同一座桥**
- 新情境必须对应同一桥梁的结构迁移
- 不能只是“同类算法的另一道题”

---

## 六、学生分流长期规则

1. 学生分流按 `A -> B -> C` 顺序判定，不允许学生手动自报模式。

2. `A` 类只认显式卡住信号：
   - 求助关键词命中
   - 主动点“需要提示”
   - 提交失败

3. `B` 类代表“过了但讲不清”，统一引用现有 quality gate 判断 `main / followup / self-check` 是否过线。

4. `C` 类只有在：
   - `B` 已过线
   - `transfer_signal` 含明确触发信号
   - `confirm` 通过
才允许进入迁移层。

5. `remedy` 的长期定位不是重新灌输知识，而是重新暴露卡住点，再重走一次 review。

6. `confirm` 长期采用：
   - 固定题库优先
   - LLM 兜底

7. `confirm` 的固定池题目必须满足：
   - 表面不同
   - 结构相同
   - 难度略降

---

## 七、结构化题目卡长期边界

1. 复盘时不再默认把完整题面全文直接塞进 prompt。

2. 优先使用：
   - `problem_card`
   - compact / full 两级结构

3. 结构化题目卡的目标是：
   - 让模型知道题目结构
   - 但不让题面淹没学生本次卡点

4. 题目卡只保留最小必要信息：
   - `title`
   - `algo_tags`
   - `summary` 或 `description_compact`
   - `input/output compact`
   - `range_compact`
   - `time_limit_ms`
   - 以及完整卡里的 `strategy_types / knowledge_points / common_mistakes`

---

## 八、洛谷题库接入边界

1. 洛谷题目命中本地题库后：
   - 不再要求学生手填题面原文

2. 只有 `algo` 标签进入 AI 复盘上下文。

3. `contest / year / other` 标签只用于：
   - 展示
   - 统计
   - 后续筛选

4. `problem_analysis` 采用懒加载：
   - 不做全量预生成

---

## 九、prompt 与 harness 的优先级关系

1. `prompts/` 目录下的 prompt 文件，是 AI 行为的**直接约束**。

2. harness contract，是设计意图与运行契约的**记录层**。

3. 如果 prompt 文件与 harness 冲突：
   - 运行时以 prompt 文件的实际行为为准
   - 但本轮结束前必须同步 prompt 文件或 harness，不能长期保留两套权威来源

---

## 十、固定联调入口

### 常用启动

- `uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload`

### 常用页面

- `/app`

### 常用验证命令

- `python3 -m py_compile api_server.py database.py review_engine.py problem_bank.py`
- `node --check static/app.js`
- `python3 test_problem_bank.py`
- `python3 test_review_api_flow.py`
- `python3 test_focus_detection.py`
- `python3 test_v1_2_flow.py`

---

## 十一、版本治理长期规则

1. `docs/common/version_policy.md`、`docs/common/version_plan.md`、`docs/common/changelog.md` 是项目级长期资产。

2. 后续只要发生成体系的版本更新，就必须同步维护这三份文档，不能只改其中一份。

3. 如果某次版本更新后，其中某一份文档无需改动，也必须在本轮确认其内容仍然有效，不能默认跳过。

4. 版本治理文档的职责长期固定为：
   - `version_policy.md`：写版本规则
   - `version_plan.md`：写版本规划
   - `changelog.md`：写已发生更新
