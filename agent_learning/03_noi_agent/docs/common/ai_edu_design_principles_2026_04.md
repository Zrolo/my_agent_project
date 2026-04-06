# AI + 教育系统下一轮设计原则（2026-04）

这份文档从近期 AI + 教育论文、Anthropic/OpenAI 官方教育文章中，提炼出对当前系统最值得执行的 10 条原则。

适用范围：

- `review_mode` 路由
- `review_family` 差异化反馈
- `failed_verdict / stuck_bridge / editorial_transfer / independent_reflect`
- `self-check`
- teacher manual review
- 线上 observability

## 1. 先判断学生处于哪种学习状态，再决定给什么反馈

系统不能把所有学生都当成一种状态处理。

至少要稳定区分：

- 失败/卡住，需要定位问题和最小下一步
- 做对/理解，需要解释为什么成立以及如何迁移

对当前系统的要求：

- `review_mode` 继续作为主路由入口
- `review_family` 必须是后端显式字段，不让前端自己猜

## 2. 答对后的反馈不应弱于答错后的反馈

学生“做出来了但讲不清为什么”不是边缘场景，而是重要学习场景。

对当前系统的要求：

- 保持 `independent_reflect`
- 不要让 `success_reflection` 退化成一句“你做对了”
- `transfer_signal` 和 `self-check` 要继续服务迁移解释

## 3. 高质量反馈应优先服务过程，而不是只服务答案

好反馈不仅指出结果对错，更要指出：

- 哪一步思路是关键
- 哪个判断条件决定了路径
- 学生下一步应先验证什么

对当前系统的要求：

- `main_block` 继续承担“当前具体卡点/核心决策流程”
- `key_bridge` 继续承担“把学生从当前点推一步”
- `next_step` 继续限制为最小验证动作

## 4. 不要教太满，必须留给学生自己补完的一步

教育型反馈和答案型反馈最大的不同，是它不应该把整条推理一次讲完。

对当前系统的要求：

- `key_bridge` 只给关键事实和判断支点
- 不直接把完整证明/完整解法打平给学生
- `self-check` 用来验证学生是否自己补上了那一步

## 5. failure_diagnosis 必须尽量贴具体对象、条件、步骤

空泛的“你这里思路不对”“注意边界”“检查状态设计”几乎没有教学价值。

对当前系统的要求：

- `failed_verdict` 优先点名：
  - 错误判断
  - 具体条件
  - 变量/公式/分支
- `stuck_bridge` 优先点名：
  - 题面对象
  - 原文条件
  - 下一步最小验证动作

## 6. success_reflection 必须能帮助学生形成迁移触发信号

“做对了”不等于“下次还会做”。

对当前系统的要求：

- `transfer_signal` 不是装饰字段
- 它必须帮助学生回答：
  - 下次看到什么具体题面特征时，应联想到这类做法
- 禁止：
  - 题型空话
  - 纯算法名
  - 题目名/题号

## 7. editorial_transfer 的核心不是报算法名，而是建立操作映射

学生看了题解还是不懂，通常不是因为没听过算法名，而是因为没建立：

- 题目动作
- 算法操作
- 状态/结构含义

对当前系统的要求：

- `editorial_transfer.key_bridge` 必须优先说清：
  - 这道题里的哪个动作
  - 对应算法里的哪个操作

## 8. 自动评估只能做护栏，不能当最终裁判

gate/rubric 很有用，但会误判，也会受样本质量影响。

对当前系统的要求：

- 继续保留 `rubric + gate`
- 但将其主要用于：
  - 回归检查
  - 大方向监控
- 不把它当作唯一真相
- teacher manual review 继续保留为必要层

## 9. 上线后的真实使用数据，比继续离线调 prompt 更重要

离线集能帮助建立基线，但不能替代真实学习场景。

对当前系统的要求：

- 继续记录：
  - `review_request_submitted`
  - `review_shown`
  - `review_feedback_submitted`
  - teacher manual review
- 优先看：
  - `mode_match_rate`
  - `understood_rate`
  - `student_can_move_next_rate`
  - `followup_rate`

## 10. 评估系统时，先问“学生是否真的能继续”

一个复盘就算写得像老师，也不一定真的帮助了学生。

对当前系统的要求：

- 教师统计应继续优先围绕：
  - `mode_correct_rate`
  - `grounded_rate`
  - `student_can_move_next_rate`
- 后续所有 prompt、UI、交互调整，都优先看它们是否改善这三个指标

## 对当前系统的三条直接行动建议

### A. 保持 mode/family 路由，不要回到单一复盘模板

当前系统已经证明：

- `failed_verdict`
- `stuck_bridge`
- `editorial_transfer`
- `independent_reflect`

用统一模板会损失大量教学针对性。

### B. 把 teacher manual review 视为核心产品能力，而不是运营补丁

它不仅用于“监督模型”，也用于：

- 累积真实失败模式
- 校正 eval
- 反哺样本池和 prompt 设计

### C. UI 和交互要继续围绕学习状态分流，而不是围绕模型能力炫技

学生端/教师端后续所有设计，都优先回答：

- 这个界面有没有更清楚地区分“诊断问题”和“理解原理”？
- 这个交互有没有让学生更容易跨出下一步？
- 这个统计有没有让老师更快看到哪一类样本在坏？

## 结论

下一轮系统演化不应再围绕“让模型说得更像老师”展开，而应围绕以下主线展开：

- 更准确地区分学习状态
- 更稳定地给出最小有效反馈
- 更可靠地验证学生是否真的理解
- 更快地让老师定位哪一类样本和哪一类模式在失败
