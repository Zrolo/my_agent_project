# 实验日志

记录新方案、小范围试验、Prompt 调整和真实观察结果。

---

## 模板

### 实验标题
- 日期：
- 负责人：
- 学科：
- 关联版本：

#### 假设
- 我们以为改动后会发生什么？

#### 改动内容
- 改了哪些 prompt / 交互 / 字段 / 流程？

#### 测试样本
- 用哪些题、哪些学生、哪些路径验证？

#### 观察到的现象
- 学生端：
- 老师端：
- 模型输出：

#### 成功信号
- 哪些现象说明方向是对的？

#### 失败信号
- 哪些现象说明还不行？

#### 结论
- 保留 / 回退 / 继续观察 / 继续收紧

#### 后续动作
- 下一步改什么？

---

## 从抽象 Quiz 到结构型 Quiz
- 日期：2026-04-01
- 负责人：Codex + 用户协同评审
- 学科：NOI
- 关联版本：v1.2

#### 假设
- 如果把 quiz 从“抽象元认知题”改成“结构型小题”，学生会更容易看懂自己到底在判断什么。
- 如果答对后展示 `bridge_feedback`，答错后展示 `distractor_feedback`，学生会更容易知道：
  - 自己刚才答对了哪一步
  - 自己选的这个错误选项为什么错
- 如果 main / followup / confirm 的职责更明确，老师端证据链会更有解释力。

#### 改动内容
- 将结构型小题从 confirm 扩展到 main / followup / confirm
- 引入：
  - `bridge_feedback`
  - `distractor_feedback`
  - `options` 对象数组格式
  - `meta.focus`
  - `meta.algorithm_category`
- 将 prompt 重构为：
  - `system/user + snippets`
- 新增 / 扩展 focus：
  - Batch A：现有桥梁结构化
  - Batch B 第一批：`data_type / loop_boundary / recursion_structure / complexity_fit`

#### 测试样本
- 后端回归：
  - `test_v1_2_flow.py`
  - `test_review_api_flow.py`
  - `test_focus_detection.py`
- 浏览器抽样联调：
  - `main_clear`
  - `main_guessed_confirm`
  - `main_guessed_remedy`
  - `main_confused_remedy`
  - `followup_correct`
  - `followup_remedy`
- 人工评审重点：
  - 题面是否仍然“太空”
  - `这一步` / `过桥` 这类表达是否太抽象

#### 观察到的现象
- 学生端：
  - 旧版抽象题确实容易让学生只是在猜“老师想让我选哪句口号”
  - 当题面落到状态定义 / 转移 / check / 顺序后，学生更容易理解自己在判断什么
  - 仅改 confirm 不够，main quiz 如果仍然抽象，学生第一印象依然会觉得空
  - `这一步`、`过桥` 这类内部术语，单独作为主提示时对初中生不够友好
- 老师端：
  - `understanding_self_check + bridge_path` 能明显提高解释力
  - `followup_correct` 如果没有配中文语义说明，老师很容易误读成“独立掌握”
  - `distractor_feedback` 比统一错误提示更能暴露学生具体偏差
- 模型输出：
  - 在没有更强约束时，容易退化成抽象口号题
  - 如果不限制，错误选项反馈也容易退化成空话，如“这个选项不对”
  - 结构型题最适合先从高可控桥梁做起，例如：
    - `state_design`
    - `transition_design`
    - `check_condition`
    - `enumeration_order`

#### 成功信号
- 结构型 quiz 题面开始更像真实“小题”，而不是抽象问句
- 学生答错时，能看到“我选的这个为什么错”，而不只是“再想想”
- 老师端能区分：
  - 独立过桥
  - 提示后过桥
  - 补救后过桥
- Prompt 工程化后，新增 focus 的成本明显下降

#### 失败信号
- 即使进入结构型路线，题目仍可能“看起来具体，实际上还是空”
- `general_modeling / method_selection` 这类 focus 仍然最容易产出假具体题
- 如果 `bridge_feedback` 太像系统内部黑话，学生还是不知道自己到底会了什么
- 如果答错时直接把完整正确解释糊上去，还是会滑回“系统替学生讲答案”

#### 结论
- 保留，并继续收紧
- 方向被证明是对的，但还不能因为“看起来像小题了”就认为教学证据已经足够
- 结构型 quiz 必须继续朝“更具体、更贴当前桥、更少空话”的方向迭代

#### 后续动作
- 继续做真实页面抽样联调，重点看：
  - 哪些 focus 仍然会滑回抽象题
  - 哪些 `distractor_feedback` 仍然太空
- 继续沉淀 NOI 的好题 / 坏题案例
- 暂不急着进入 v2 模板库，先把 v1.2 结构型题质量跑稳

---

## 外部严格审核：结构型 Quiz 契约与渲染链路
- 日期：2026-04-01
- 负责人：Claude 审核 + Codex 修正
- 学科：NOI
- 关联版本：v1.2

#### 假设
- 如果让外部严格审稿人直接按代码、prompt、前端链路来审，能更早发现“看起来已经有设计，实际上落地有漏洞”的地方。
- 我们预期最可能出问题的是：
  - fallback 契约
  - confirm 渲染链路
  - 答错后是否过早暴露完整解释

#### 改动内容
- 让外部审核者同时检查：
  - `prompts/quiz-content/`
  - `prompts/snippets/`
  - `api_server.py`
  - `database.py`
  - `static/app.js`
- 根据审核意见补了：
  - `fallback_explain` 的输出契约
  - 后端 fallback 解释透传
  - `followup` 隐藏完整 explanation 的注释说明

#### 测试样本
- 审核输入：
  - 结构型 quiz 契约
  - 三层角色区分
  - 前端渲染逻辑
  - fallback 逻辑
- 修正后回归：
  - `python3 -m py_compile`
  - `node --check`
  - `test_v1_2_flow.py`

#### 观察到的现象
- 学生端：
  - 如果 fallback 只存在于 prompt 里、没有明确契约和页面预期，学生最终看到的体验会很不稳
  - follow-up 前不展示完整 explanation 这件事，如果没有明确说明，很容易被以后维护者误改
- 老师端：
  - 外部审核者非常关注“系统是不是把学生答错后的关键证据浪费掉了”
  - 对老师来说，答错后是否先指出“选中的这个为什么错”，比统一解释更重要
- 实现层：
  - `submitSelfCheck()` 的 `confirm_quiz` 渲染链路原本就已经接通，外部审核帮助我们确认了这不是 bug
  - `fallback_explain` 的契约原本确实不完整，属于真实结构漏洞

#### 成功信号
- 外部审核能指出真正的结构漏洞，而不是只做风格评论
- 经过这轮修正后：
  - fallback 不再只是 prompt 里的约定
  - 页面联调也有了明确的 fallback 验收标准
- `confirm_quiz` 渲染链路被明确验证存在，减少了误判

#### 失败信号
- 即使 prompt 工程化做得更规范，如果输出契约没写清，后面仍然会踩链路问题
- 维护者如果只看页面现象、不看设计意图，很容易把“故意不展示完整 explanation”当成 bug 改掉

#### 结论
- 保留，并把“外部审核回合”作为重要实验来源
- 这类审核最大的价值，不是告诉我们“方向对不对”，而是帮我们发现：
  - 哪些地方只是文档里有
  - 哪些地方在代码和页面里真的接通了

#### 后续动作
- 继续把外部审核发现的问题沉淀进：
  - 决策日志
  - 实验日志
  - 联调清单
- 以后每次涉及 prompt 契约或前后端链路的大改动，都建议至少做一次“外部严格审核”
