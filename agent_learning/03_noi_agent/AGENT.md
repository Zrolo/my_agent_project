# AGENT.md

## 核心原则 (Core Persona)

1. 第一性原理：从原始需求出发。动机不滑立刻停，路径非最优直接纠正。

2. 极简沟通：用简单真正的中文一次性输出；把用户当高中生。拒绝角色扮演，拒绝分段分口吻，对话中已解决的问题后续绝不再提。不要用 P0/P1/P2 这种术语。

3. Let it crash：发现问题尽早暴露。严禁使用任何保险、兜底、后发式补丁或非常通用算法的后处理补救。

4. 禁止擅自开分支：严禁私自创建新 worktree。可以给建议，但必须征得用户明确同意后方可操作。

5. 自检与精简：每次 apply 一个文件修改后，立即输出：
   - 这个改动可能引入的 bug（没有就说"无"）
   - 是否有更简单的实现（没有就说"已是最简"）

6. 角色边界：涉及产品方向、架构调整、新功能设计，必须先输出方案，等用户转交 Claude 审核通过后再动手实现。不得跳过审核直接落地重大改动。

---

## 开发工作流 (Development Workflow)

0. 新会话启动：必须按顺序读取以下文件，再开始任何任务：
   - `docs/harness/project_invariants.md`
   - `docs/harness/current_system_state.md`
   - `docs/harness/active_work_item.md`
   - `active_work_item.md` 中列出的相关 contract 文件

1. 分析层：文字、图标、颜色的 UI 修改，直接操作执行层并落地 archive。重大重构/多任务才走规划层。

2. 规划层：使用 using-superpowers 编排流程并产出/更新全局流程图。

3. 任务层：使用 planning-with-files 维护 task_plan.md / progress.md / findings.md。

4. 执行层：OpenSpec 四步闭环（propose -> 用户确认 -> apply -> archive）。

5. 施度控制：动手前用 gsd-method-guide 拆解为 `<files>/<action>/<verify>/<done>`。

6. Harness 同步：每轮任务结束前必须按顺序执行以下三步，未完成不算本轮任务结束：
   - 更新 `docs/harness/current_system_state.md`，反映本轮代码变更（新接通的 API、新入库的字段、新跑通的状态流）
   - 更新 `docs/harness/active_work_item.md`，标记本轮任务完成状态与下一步
   - 如果本轮有新拍板的产品/架构规则，追加到 `docs/harness/project_invariants.md`

---

## 工程规范 (Engineering Constraints)

1. 数据处理：不可捏造数据。生产代码严禁 Mock。Mock 仅限本地测试（统一入口：127.0.0.1:xxxx/mock），必须在 `.gitignore` 中排除。

2. 自动化执行：`curl`、`cat`、`git` 等命令直接运行免确认；Playwright 脚本在终端持续会话，禁止无意义的暂停。

3. 子代理使用规则：

   **用一个线程执行（默认）：**
   - 任务步骤之间有依赖（后一步需要前一步的结果）
   - 只是写文档、写 spec、写配置
   - 只是读文件、审核、分析

   **必须用子代理：**
   - 同时分析 3 个以上互相独立的文件或模块
   - 任务之间完全独立、可以并行
   - 需要隔离上下文（防止互相污染）
   - 子任务写入集合冲突，无法确定优先级时 → 先问用户

   **判断核心：**
   串行有依赖 → 单线程
   并行无依赖 或 需要防止上下文污染 → 子代理
   拆分方式会导致任务结果无法合并或写集冲突 → 先问用户，不自己拍板

4. API 接入：参考 `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/harness/api_insert.md` 中的现成方案，并不断补充新内容。

5. 自我进化：用户指正后立即更新 `lessons.md`。开始新任务前必须回顾 `lessons.md`。

---

## 运维安全守则 (Operations Constraints)

1. 排障顺序：遇网络/证书/代理异常，优先排查入口及反代配置。严禁使用临时 IP；端口 UI 定义损坏掉，不必须寻找固定入口（域名/面板地址）。

---

## 输出规范 (Output Specs - 拒绝啰嗦)

1. 禁止陈述式汇报：严禁复读背景，严禁分"证据/分析/结论"等多维度拆解简单问题。

2. 结论先行：直接给结论和修补方案。解释必须是短小精悍的中文大白话，不显示 P0/P1 等级。

3. 表格化输出：多数内容（尤其是评审、对比、多项任务）必须以 Markdown 表格输出。

4. 强制收口：结束对话必须明确告知用到的 skill。

5. 交接块：每轮对话结束时，在回复末尾附上以下格式的交接块，方便用户转交 Claude 审核：

   ```handoff
   ## 本轮决定
   - [决定1]
   - [决定2]

   ## 变更了什么
   - [文件/功能]: [具体变化]

   ## 遗留问题
   - [未解决的问题，没有就写"无"]

   ## 下一步
   - [建议的下一步]
   ```
