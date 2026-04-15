# 当前工作项

## 本文件的写入标准

只写**当前正在推进的一轮任务**：

- 当前目标
- 本轮非目标
- 本轮需要加载的 contract 文件
- 本轮涉及文件
- 验收标准
- 当前风险 / 下一步

不要写：

- 长期规则
- 已完成的全部历史
- 与当前任务无关的讨论

---

## 当前目标

### 2026-04-12 补充：开放 bridge 可观测 P0/P1 已进入收口验证

当前状态：

- 已新增 `_resolve_bridge_decision(...)`，在不改变学生主链行为的前提下记录：
  - `known_bridge`
  - `candidate_bridge`
  - `open_bridge`
- 已新增 `reviews.bridge_route_meta` 存储字段
- `generate_review(...)` 已自动产出 `bridge_route_meta`
- `_generate_and_store_review(...)` 已把 `bridge_route_meta` 随 review 一起落库
- 学生详情 `/api/checkins/{checkin_id}` 已返回 `review.bridge_route_meta`
- 教师复核样例 `/api/teacher/review-samples` 已返回 `bridge_route_meta`
- 教师复核页已用可读字段展示：
  - 桥路由状态
  - 稳定桥
  - 候选桥
  - 置信度
  - 命中信号
  - 冲突信号
- P1 已补教师聚合审查：
  - `/api/teacher/stats` 返回 `bridge_route_stats`
  - `bridge_route_stats.status` 聚合 known / candidate / open
  - `bridge_route_stats.stable_focus` 聚合稳定父桥
  - `bridge_route_stats.candidate_bridge` 聚合候选桥
  - `bridge_route_stats.open_bridge` 聚合开放桥
  - `bridge_route_stats.conflict_signals` 聚合冲突信号
  - 教师总览页新增“桥路由审查”卡
  - 教师复核页新增“全部 / 只看候选桥 / 只看开放桥 / 只看稳定桥”筛选
- P2 已补“转正规则建议”安全闭环：
  - `/api/teacher/stats` 返回 `bridge_route_promotion_suggestions`
  - 只聚合 candidate/open bridge，不包含 known bridge
  - 建议项包含 `decision_policy=teacher_review_required`
  - 建议项包含 `auto_promote=false`
  - 教师总览页新增“转正规则建议”卡
  - 页面明确展示“需要教师确认”和“不会自动转正”
- P3 已补“规则草案”安全闭环：
  - 每条转正规则建议附带 `rule_draft`
  - `rule_draft.filename` 生成可落地的草案文件名
  - `rule_draft.integration_status=draft_only`
  - `rule_draft.auto_apply=false`
  - `rule_draft.acceptance_checks` 明确要求教师确认后才允许进入正式 resolver
  - 教师总览页显示“草案文件”和“草案状态”
- P4 已补“教师确认 + 草案导出”闭环：
  - 新增 `bridge_rule_draft_decisions` 审查记录表
  - 新增 `/api/teacher/bridge-rule-drafts/export`
  - 新增 `/api/teacher/bridge-rule-drafts/decision`
  - 教师总览页新增“下载草案”和“确认进入草案池”
  - 确认记录仍保存 `auto_promote=false`
  - 确认动作仍不改 `_resolve_bridge_decision`
- P5 已补“草案审查历史”闭环：
  - 新增 `/api/teacher/bridge-rule-drafts/decisions`
  - 新增 `list_bridge_rule_draft_decisions(...)`
  - 教师总览页新增“草案审查历史”
  - 确认草案后会刷新当前教师的历史记录
  - 历史记录仍只是审查记录，不触发自动转正
- P6 已补“正式 bridge registry 人工登记簿”闭环：
  - 新增 `bridge_registry_entries` 表
  - 新增 `/api/teacher/bridge-registry/entries` GET / POST
  - 只有 `decision=confirmed` 的草案才能登记到 registry
  - registry entry 固定 `registry_status=registry_only`
  - registry entry 固定 `resolver_enabled=false`
  - 教师总览页新增“正式 bridge registry”
  - 教师可从草案审查历史点击“登记到 registry”
- P7 已补“resolver patch 草案”闭环：
  - 新增 `/api/teacher/bridge-registry/entries/{entry_id}/resolver-patch-draft`
  - 新增 `build_resolver_patch_draft_for_registry_entry(...)`
  - patch 草案固定 `patch_status=patch_draft_only`
  - patch 草案固定 `auto_apply=false`
  - patch 草案固定 `resolver_enabled=false`
  - patch 草案只指向 `review_engine.py` 和 `_resolve_bridge_decision(...)`
  - 教师总览页新增“生成 resolver patch 草案”
- 这轮仍保持约束：
  - candidate/open bridge 只做观测
  - 不驱动 quiz
  - 不驱动知识卡
  - 不改 remedy 状态机

当前下一步：

- 跑完整后端与前端回归
- 如果全绿，再把 `docs/superpowers/plans/2026-04-12-open-bridge-observability-plan.md` 追加 P7 验证状态
- 后续应停止继续堆在本计划里，另开新计划处理“resolver patch 如何人工落地并加红测”

### 2026-04-12 补充：P3128 / OI Wiki bridge 试点已接通，下一步进入树上差分扩样

当前状态：

- 已新增 `tree_path_difference` focus
- P3128 当前会进入：
  - `tree_path_difference`
  - `graph.tree_path_difference`
- P3258 这类树上路线访问次数语境也会进入：
  - `tree_path_difference`
- 树上边经过次数语境当前作为 `tree_path_difference` 的边界样例处理
- 线段树 lazy 语境仍有反向保护线，不会因为“标记”被树上差分误吸走
- 当前 main / followup / final micro confirm / knowledge card / knowledge confirm / remedy 都已围绕：
  - `端点/LCA 附近差分标记`
  - `DFS 子树汇总`
  - `每个点经过次数`
- 当前已修掉两类误路由：
  - 树上路径里的 `标记` 不再优先误进 `lazy_semantics`
  - 树上路径里的 `经过次数` 不再优先误进 `shared_prefix_merging`
- 当前新增扩样测试：
  - P3128 点经过次数
  - P3258 路线访问次数
  - 树上边经过次数边界样例
  - P3372 线段树 lazy 反向保护线
- 当前已同步文档：
  - `docs/subjects/noi/bridge_map.md`
  - `docs/subjects/noi/focus_taxonomy.md`
  - `docs/common/oi_wiki_bridge_taxonomy_mapping_v1.md`
  - `docs/common/oi_wiki_bridge_sources_v1.jsonl`
  - `docs/common/oi_wiki_bridge_snippets_v1.jsonl`
  - `docs/common/bridge_external_snippets_v1.jsonl`
  - `docs/common/bridge_audit_board_2026_04.md`
  - `docs/harness/current_system_state.md`
- 当前运行时也已把 `graph.tree_path_difference` 映射到 `tree_path_difference` bridge key，用于知识卡 / remedy 外部片段追加

当前下一步：

- 找一个真实洛谷边差分题号，替换当前“树上边经过次数统计题”占位
- 决定是否拆：
  - 点差分 variant
  - 边差分 variant
  - 纯 HLD 区间维护 variant
- 继续补更多 OI Wiki / 外部资料 snippet，尤其是边差分和 HLD 纯维护语境

### 2026-04-11 补充：整站前端 Vue 新壳与第一版 UI 重构已落地，当前进入真实走查与收边

当前状态：

- Vue 3 + Vite + Pinia + Vue Router 新前端已接管运行时主入口
- 学生端已重排到：
  - `/app/workspace/chat`
  - `/app/workspace/checkin`
  - `/app/archive`
  - `/app/archive/:checkinId`
- 教师端已重排到：
  - `/app/teacher/overview`
  - `/app/teacher/review`
  - `/app/teacher/students`
  - `/app/teacher/checkins`
- 旧 student / teacher URL alias 已接通
- `run_test.sh` 已切到新前端回归口径并通过
- 基于 `ui-ux-pro-max` 的第一版视觉系统已接入：
  - 学生端采用 richer palette 的竞赛工作台
  - 教师端采用更克制的运营工作台
  - 当前构建与 Node 前端测试已通过
- 路由恢复与角色壳层切换已进一步收口：
  - auth 恢复前置到 Vue 启动阶段
  - `router.beforeEach(...)` 统一处理 pending path 与错角色壳层跳转
  - layout 不再各自用分散 watch 兜主要路由恢复
- 真实接口走查已抓到并修掉一个学生端阻塞 bug：
  - `CheckinPage.vue` 原先提交 `attempted / solved`
  - 后端只接受 `unfinished / hinted / editorial / independent`
  - 当前已改为共享常量并补测试锁定
- 当前已继续收学生端可用性：
  - 去掉页面顶部解释性大段文案
  - 去掉“当前页面 / 路由状态 / 目标”提示卡
  - 历史详情页改成可读视图，不再主要依赖 JSON
  - 详情接口已补齐学生提交内容字段供前端使用
- 当前已完成教师端四页第一轮产品化收边：
  - `overview` 不再显示统计 JSON，改成排行卡
  - `review` 不再显示样例 JSON，改成复核摘要卡
  - `students` 改成稳定的 `学生维度` 页面，并把标记做成关注卡
  - `checkins` 已补空状态
  - `test_teacher_vue_ui.mjs` 已纳入总回归
- 当前已完成打卡题目来源自动识别：
  - 学生端不显示 OJ 下拉框
  - 贴洛谷题号/链接时自动按 `luogu` 提交并支持自动读题
  - 贴 Codeforces / AtCoder 链接时自动按对应来源提交，但要求补标题和题面
  - 后端会兜底修正旧客户端传来的错误 `oj_source`
- 当前已完成过期 token 处理：
  - 401 不再直接显示 `Invalid or expired token`
  - API 层会统一触发 logout 并显示 `登录已过期，请重新登录`
  - 当前路径会保存为 pending path，重新登录后可回到原目标页

当前目标：

1. 把 Vue 新壳的第一版运行时彻底收稳
2. 做一轮真实浏览器走查，优先收学生端最关键路径：
   - 登录恢复
   - chat
   - checkin
   - archive list/detail
3. 再走教师 overview / review / students / checkins 的真实交互
4. 基于走查结果决定哪些旧静态脚本可以正式退场

本轮非目标：

- 不改后端业务 API 协议
- 不在这轮里重构 review / bridge 逻辑
- 不继续扩 teacher 新功能
- 不在这一轮里再做第二版大视觉改稿

当前涉及文件：

- `package.json`
- `vite.config.js`
- `tailwind.config.js`
- `postcss.config.js`
- `frontend/`
- `static/index.html`
- `static/student_routes.js`
- `static/teacher_routes.js`
- `api_server.py`
- `run_test.sh`

当前验收标准：

- `npm run build` 稳定通过
- `/app/workspace/chat`、`/app/archive/:id`、`/app/teacher/overview` 都能回到统一前端入口
- 新旧路由 contract 测试通过
- 整体回归继续通过
- 真实浏览器走查后，不再出现：
  - 登录后空白或壳层错页
  - 刷新后 URL 与页面主体不一致
  - 历史详情与提交页视觉语义混淆
- 角色错误的深链访问会被统一拉回正确壳层，而不是留在错误登录页

当前下一步：

- 学生端真实浏览器走查已完成：
  - 登录
  - 打卡提交后跳详情
  - 历史列表进入详情
  - 375px 移动端历史列表/详情无横向溢出
- 教师端真实浏览器走查已完成：
  - 登录 `teacher`
  - overview / review / students / checkins 四页标题和路由稳定
  - 教师页正文不再暴露调试 JSON
- 下一步进入“前端旧运行时代码退场审查”：
  - 已确认运行时入口只认 Vite 构建产物，不再加载旧 `static/app.js`
  - 已新增 `static/teacher_stats_ui.js`，先切出教师统计/复核筛选纯 helper
  - `test_teacher_stats_ui.mjs` 的教师统计相关断言已改为 import 新 helper
  - 当前旧 `static/app.js` 仍被同一测试文件用于 quiz、visual_hint、knowledge bailout 等旧渲染 helper
  - 下一步继续按 helper 维度拆：
    - 先拆 visual_hint / rich text 渲染 helper
    - 再拆 quiz timeline/helper
    - 最后再评估 `static/app.js` 是否可归档

### 2026-04-11 补充：第五阶段已为首轮 review 接入轻量 bridge 约束

当前状态：

- 第五阶段已经完成首轮 review 的轻量 bridge 约束接入
- 当前只覆盖 4 个 bridge：
  - `method_selection`
  - `shared_prefix_merging`
  - `check_condition`
  - `left_bound_update`
- 这轮已经完成两层接线：
  - prompt 轻约束
  - bridge consistency guard

已完成：

- prompt 轻约束
- bridge consistency guard

下一步：

- 用真实样例继续复审：
  - `P2922`
  - `P2678`
  - `P2249`

### 2026-04-10 补充：阶段四已启动并完成首批 visual_hint 精修

阶段四这轮已经开始，并且当前高频/长尾代表 bridge 的 `visual_hint` 已完成三批精修：

- `check_condition`
- `method_selection`（trie 语境）
- `lazy_semantics`
- `shared_prefix_merging`
- `left_bound_update`
- `transition_design`
- `greedy_basis`
- `tree_diameter_candidates`
- `constraint_modeling`

这轮真实完成的收口是：

1. `check_condition`
   - 知识卡和 deterministic remedy 的图示都已经收成：
     - `check(5)=true`
     - `只说明 5 还可行 / 5 可行`
     - `再决定区间往哪边缩`
2. `method_selection`（trie 语境）
   - 知识卡和 deterministic remedy 的图示都已经收成：
     - `101 / 100 / 11`
     - `前两条前面两位一样`
     - `这就是“相同开头”的题面信号`
     - `这是支持 trie 的题面信号`
3. `lazy_semantics`
   - 知识卡和 deterministic remedy 的图示都已经收成：
     - `[1,4]`
     - `lazy=3`
     - `左儿长度=2`
     - `pushdown: 左儿 sum += 3×2`
4. `shared_prefix_merging`
   - 知识卡和 deterministic remedy 的图示都已经收成：
     - `101 / 100 / 11`
     - `前缀 10 先合在一起`
     - `查询时只沿前缀路径往下走`
5. `left_bound_update`
   - 知识卡和 deterministic remedy 的图示都已经收成：
     - `[1,2,2,2,3]`
     - `a[mid] == 2`
     - `mid 先留作候选`
     - `r = mid 继续往左缩`
6. `transition_design`
   - 知识卡和 deterministic remedy 的图示都已经收成：
     - `当前格 (i,j)`
     - `上一层 (i-1,j-1)`
     - `上一层 (i-1,j)`
     - `先把来源想全，再写转移式`
7. `greedy_basis`
   - 知识卡图示已经收成：
     - `[1,3] 先选`
     - `[3,5] 还能接上`
     - `后面还有空间`
     - `这一步才不吃亏`
8. `tree_diameter_candidates`
   - 知识卡图示已经收成：
     - `左边最远点`
     - `右边最远点`
     - `经过新边接起来`
     - `先比较这三类候选`
9. `constraint_modeling`
   - deterministic remedy 图示已经收成：
     - `A <= B + c`
     - `B <= C + d`
     - `先统一成同一种关系`
     - `再看谁限制谁`

当前主文档：

- `docs/common/noi_agent_stage3_execution_2026_04.md`
- `docs/common/bridge_audit_board_2026_04.md`

当前验收标准：

- `visual_hint` 的首批红测全部转绿
- 第二批 `shared_prefix_merging / left_bound_update / transition_design` 红测也已转绿
- 第三批 `greedy_basis / tree_diameter_candidates / constraint_modeling` 红测也已转绿
- 不改状态机、不改 bridge 路由
- 全量回归继续保持通过

当前下一步：

- 阶段四的代表性 `visual_hint` 精修已基本收口
- 下一步应转去：
  1. 正式收阶段四
  2. 或开启下一阶段

### 2026-04-10 补充：阶段三已完成

阶段三这轮已经完成：

- 围绕固定样例池，复审了最弱高频 bridge 的真实学生链路

已完成：

1. `method_selection`
2. `shared_prefix_merging`
3. `lazy_semantics`

当前主文档：

- `docs/common/noi_agent_stage3_execution_2026_04.md`
- `docs/common/high_frequency_bridge_sample_pool_2026_04.md`
- `docs/common/bridge_audit_board_2026_04.md`

当前验收标准：

- 每个目标 bridge 至少有 1 条最新 live 样例被重新复审
- `bridge_audit_board` 更新到当前真实判断
- harness 文档不再依赖聊天上下文记忆阶段三状态

当前下一步：

- 这轮 live 复核已经补完：
  - `P2249 / review_id=4932`
  - `P2678 / review_id=4935`
  - `P2922 / review_id=4936`
- 第五阶段的首轮 bridge guard 已完成 fresh live 验证
- 当前这一轮可以收口
- 下一步应再单独开新阶段，不继续在这一轮里扩需求

### 2026-04-09 补充：桥拆分与高频方法桥补课层硬化

这轮已经真实落地：

- `has_explicit_help_signal(...)` 已收紧：
  - `wa/tle/re/ce` 不再自动把“已经点名具体桥”的学生直接送去 remedy
  - `P2249` 这类边界桥会优先保留 quiz 梯子
- `constraint_modeling` 已补进 deterministic remedy
- `test_learning_routing_unit.py` 和相关 async/message 测试已经对齐当前真实学习流：
  - `remedy -> final_micro_confirm -> resolved`

- `review_engine.py` 已新增并接通更细桥：
  - `left_bound_update`
  - `shared_prefix_merging`
  - `lazy_semantics`
- `P2249` 这类“找最左位置”不再默认掉进泛 `boundary_debug`
- `P2922` 这类题现在已经能把：
  - “为什么题面支持 trie”
  - “为什么 trie 查询时只沿前缀走”
  拆成两座桥，而不是混在一条里
- 高频方法桥的 remedy 已开始本地参数化，不再默认先走慢的 LLM：
  - `complexity_fit`
  - `method_selection`
  - `shared_prefix_merging`
  - `lazy_semantics`
  - `left_bound_update`
- `P2922` 这类 `trie + method_selection` 的后半段也继续收紧了：
  - remedy 已会自然过渡到“很多消息有相同开头，值不值得先合在一起看”
  - knowledge card 后确认题也已同步成这组更贴题的信号确认

当前下一步优先继续：

- 用真实历史样例重新审：
  - `P2249`
  - `P2922`
  - `P3372`
- 重点看：
  - 第一轮 quiz 是否更贴桥
  - constraint / left-bound / lazy 这几类 remedy 是否已经不再卡住
  - 知识卡是否仍然像“小课”而不是模板话术

### 2026-04-09 补充：规约对齐

已完成一轮文档对齐：

- `AGENT.md` 已去掉对不存在的 `lessons.md` 的硬依赖
- `AGENT.md` 已同步到当前学生端真实路由：
  - `/app/chat`
  - `/app/checkin`
  - `/app/history`
  - `/app/history/:checkin_id`
- `docs/harness/project_invariants.md` 已同步历史详情页语义与 `version_governance.md`

这轮补充的目的只是消除规约漂移，不改变当前产品主线。当前下一步仍应优先继续：

- 收紧 review / knowledge card 的内容质量
- 继续用真实历史样例检查学生链路

### 2026-04-09 补充：讲解文案继续学生化

这轮已经真实落地：

- review prompt 现在明确要求：
  - 能对比时，先说学生最容易误会的一句话
  - 再说正确的一句话
- 高频知识卡现在统一往：
  - `最容易误会的是 ...`
  - `真正要站稳的是 ...`
 这个结构收口
- 高频知识卡的 `algorithm_overview` 已统一压成：
  - “这一步在整套方法里负责什么”

当前下一步优先继续：

- 用真实历史样例重新审：
  - 第一轮复盘
  - 第二轮 follow-up
  - 第三轮 final micro-confirm
  - knowledge card
- 重点继续盯：
  - `method_selection`
  - `trie.shared_prefix_merging`
  - `complexity_fit`

### 2026-04-09 补充：洛谷批量测试数据已生成

这轮已经真实落地：

- 已为 `student_a` 批量创建 `24` 条新的洛谷 checkin 测试数据
- 覆盖高频知识点：
  - `dp.state_design`
  - `dp.transition_design`
  - `binary_search.check_condition`
  - `greedy.greedy_basis`
  - `graph.tree_diameter.tree_diameter_candidates`
  - `string.trie.shared_prefix_merging`
  - `modeling.scale_estimation`
  - `modeling.method_selection`
- 当前这批批量数据的 `checkin_id` 范围为：
  - `3359` 到 `3382`
- 机器可读清单已写入：
  - `docs/common/luogu_review_generated_batch_2026_04_09.json`

当前下一步优先继续：

- 用这 24 条批量数据继续做学生视角审查
- 优先盯：
  - `modeling.scale_estimation`
  - `modeling.method_selection`
  - `string.trie.shared_prefix_merging`

### 2026-04-10 补充：OI Wiki 到 bridge taxonomy 的第一版映射已建立

这轮已经真实落地：

- 已新增主文档：
  - `docs/common/oi_wiki_bridge_taxonomy_mapping_v1.md`
- 这份文档已经把 OI Wiki 主目录按当前系统语言收成：
  - `topic_l1`
  - `topic_l2`
  - `bridge`
- 当前不是做大 RAG，而是先建立：
  - OI Wiki 章节
  - 我们的 bridge
  - 后续知识卡/统计/检索
  之间的一致语言

当前下一步优先继续：

- 先把这份映射用于高频 bridge：
  - `complexity_fit`
  - `method_selection`
  - `shared_prefix_merging`
  - `lazy_semantics`
  - `left_bound_update`
- 后面再决定要不要把这份映射接进轻量检索

### 2026-04-10 补充：外部资料源分工已收敛

这轮已经真实落地：

- 已新增主文档：
  - `docs/common/bridge_external_sources_strategy_v1.md`
- 当前已经明确：
  - `cp-pdf` 做主外部知识源
  - 三本《算法竞赛入门经典》扫描版 PDF 不做主检索，只做高频 bridge 的人工补充与校对

当前下一步优先继续：

- 从 `cp-pdf` 里挑第一批最适合的 PDF
- 抽第一版 bridge 片段索引
- 先只覆盖高频 bridge

### 2026-04-10 补充：`cp-pdf` 第一版 bridge 来源索引已落地

这轮已经真实落地：

- 已新增第一版结构化来源索引：
  - `docs/common/cp_pdf_bridge_sources_v1.jsonl`
- 当前已经先为高频 bridge 选好第一批来源 PDF：
  - `complexity_fit`
  - `check_condition`
  - `left_bound_update`
  - `state_design`
  - `transition_design`
  - `enumeration_order`
  - `shared_prefix_merging`
  - `method_selection`
  - `lazy_semantics`
  - `greedy_basis`
  - `tree_diameter_candidates`
  - `constraint_modeling`
- 每条来源记录当前都已具备：
  - `source_family`
  - `source_title`
  - `source_file`
  - `topic_l1`
  - `topic_l2`
  - `bridge`
  - `priority`
  - `reason`

当前下一步优先继续：

- 给 `cp-pdf` bridge 片段建立统一 snippet schema
- 先从第一批高频 bridge 里各抽 1 到 2 段知识片段
- 第一版只服务：
  - `knowledge_bailout`
  - 高频 deterministic remedy 的内容精修

### 2026-04-10 补充：`cp-pdf` 第一版真实 bridge snippet 已开始落地

这轮已经真实落地：

- 已新增第一版片段文件：
  - `docs/common/cp_pdf_bridge_snippets_v1.jsonl`
- 当前已经先从 `Competitive Programmer’s Handbook` 抽出并转述了这些高频 bridge：
  - `complexity_fit`
  - `left_bound_update`
  - `state_design`
  - `transition_design`
  - `shared_prefix_merging`
- 当前 snippet 全部采用：
  - bridge 级切片
  - 非原文搬运
  - 教学化转述

当前下一步优先继续：

- 继续补第一批高频 bridge 的：
  - `misconception`
  - `mini_example`
- 再从：
  - `字符串算法选讲-金策.pdf`
  - `挑战程序设计竞赛(第2版).pdf`
 里补 `method_selection`、`lazy_semantics`、`check_condition`

### 2026-04-10 补充：`OI Wiki` 第一版来源层与 snippet 已开始落地

这轮已经真实落地：

- 已新增第一版来源索引：
  - `docs/common/oi_wiki_bridge_sources_v1.jsonl`
- 已新增第一版教学改写规则：
  - `docs/common/oi_wiki_pedagogical_rewrite_rules_v1.md`
- 已新增第一版 snippet：
  - `docs/common/oi_wiki_bridge_snippets_v1.jsonl`

当前已经先覆盖这些高频 bridge：

- `complexity_fit`
- `left_bound_update`
- `check_condition`
- `state_design`
- `transition_design`
- `shared_prefix_merging`
- `method_selection`
- `lazy_semantics`

当前 OI Wiki 的定位已经收清楚：

- 提供 bridge 正确知识底稿
- 提供 `topic_l1 / topic_l2 / bridge` 的章节来源
- 不直接把原文给学生看，必须先教学化改写

当前下一步优先继续：

- 给 OI Wiki snippet 继续补：
  - `misconception`
  - `mini_example`
- 再把 `cp-pdf + OI Wiki` 的同桥 snippet 放到同一份统一索引里
- 然后先挑：
  - `shared_prefix_merging`
  - `lazy_semantics`
  做第一轮知识卡接线验证

## 本轮并行新增目标：NOI review mode routing + eval 基线

在不改 review JSON schema、不删现有 guard、不动 SSE/confirm_pool/A/B/C 触发器的前提下：

1. 在 `generate_review(...)` 入口归一化 `submission_result`
2. 用 `_detect_review_mode(...)` 把 review 分成：
   - `failed_verdict`
   - `stuck_bridge`
   - `independent_reflect`
   - `editorial_transfer`
3. 在 `_build_review_system_prompt(mode=...)` 末尾追加 4 套 supplement
4. 建立 `promptfoo` 评测骨架，先把真实 `cases.jsonl`、`run_review_case.py` 和 `promptfoo.yaml` 落到仓库
5. 用 baseline vs mode-route 做对比，不靠主观感觉判断 prompt 有没有进步

把“学生分流闭环 + confirm 迁移验证”这一轮继续往学生端真实体验推进，当前优先落地：

1. 保持当前 A/B/C 主链、remedy 收紧、confirm_pool 最小表与 self-check confirm 状态机稳定
2. 在不改 review JSON schema、不做多段生成的前提下，把“打卡后等待黑盒”改成“固定阶段可见”
3. 当前后端已经接通 `GET /api/checkins/{checkin_id}/stream`，用固定阶段埋点推送：
   - `received`
   - `queued`
   - `llm_start`
   - `llm_done`
   - `review_parse`
   - `review_saved`
   - `quiz_generating`
   - `completed`
   - `failed`
4. 当前前端已经从“只流状态”推进到“状态 + 正文草稿预览”：`pending` 时优先用 `fetch + ReadableStream` 订阅 SSE，失败后退回现有轮询
5. 当前 review 卡已做第一轮瘦身：默认只留 4 条主视图，详细诊断折叠
6. 当前 quiz 已开始沉淀模板与路径边的数据库骨架，但还未切换成模板优先生成
7. 在这条新链稳定后，再继续做浏览器级学生端联调，并决定是否扩第二批固定题

---

## 本轮非目标

本轮不做：

- 新的学生端页面或模式选择
- review JSON schema 变更
- 删除现有 guard
- SSE / confirm_pool / A/B/C 分流触发器 / 多 agent 链路
- review 正文 token 流式输出
- review 多段生成或分段写库
- 重型独立 `Reviewer` 实例
- 全量自动化 confirm_pool 导入
- 全量洛谷标签映射
- 后端真实生成耗时优化
- retry 恢复首轮 `problem_card / analysis_source / local_problem_id`

---

## 本轮需要加载的 contract 文件

- `docs/harness/ai_output_contracts.md`
- `docs/harness/review_quiz_quality_gate.md`
- `docs/subjects/noi/confirm_pool_mapping_v1.json`

---

## 本轮涉及文件

- `docs/harness/current_system_state.md`
- `docs/harness/active_work_item.md`
- `evals/review/export_cases.py`
- `evals/review/run_review_case.py`
- `evals/review/run_review_case_kimi_cli.py`
- `evals/review/promptfoo.yaml`
- `evals/review/promptfoo.kimi-cli.yaml`
- `evals/review/build_promptfoo_sample.py`
- `evals/review/promptfoo.kimi-cli.sample.yaml`
- `evals/review/cases.jsonl`
- `evals/review/promptfoo_tests.jsonl`
- `evals/review/README.md`
- `api_server.py`
- `database.py`
- `review_engine.py`
- `prepare_confirm_pool.py`
- `seed_confirm_pool.py`
- `static/app.js`
- `test_review_stream_api_unit.py`
- `docs/superpowers/specs/2026-04-04-review-streaming-content-and-quiz-template-design.md`
- `docs/superpowers/plans/2026-04-04-review-streaming-content-and-quiz-template-implementation-plan.md`
- `test_learning_routing_unit.py`
- `docs/subjects/noi/confirm_pool_tag_stats_v1.json`
- `docs/subjects/noi/confirm_pool_mapping_v1.json`
- `docs/subjects/noi/confirm_pool_seed_v1.json`
- `docs/harness/project_invariants.md`

---

## 验收标准

0. `submission_result` 进入 `generate_review(...)` 后已统一归一化为小写值
0. `_detect_review_mode(...)` 与 4 套 `system prompt supplement` 有单测保护
0. `evals/review/` 目录已能从真实数据库导出 `cases.jsonl`
0. `run_review_case.py` 能对单条 case 返回真实 review JSON
0. `promptfoo.yaml` 至少能成功起跑，不存在配置级错误
0. `promptfoo.kimi-cli.yaml` 至少能成功起跑，不存在 provider 接入级错误
0. `build_promptfoo_sample.py` 能生成 sample 测试集，`promptfoo.kimi-cli.sample.yaml` 能成功起跑
1. `test_learning_routing_unit.py` 通过
2. `test_review_async_api_unit.py` 与 `test_review_engine_messages_unit.py` 不回退
3. `prepare_confirm_pool.py` 能输出稳定 JSON 统计
4. `seed_confirm_pool.py` dry-run 与实际导入都可用
5. `confirm_pool` 已至少有 8 个固定种子题可命中
6. 固定池优先于 LLM 的命中顺序已被 `test_learning_routing_unit.py` 回归保护
7. `current_system_state.md`、`active_work_item.md`、`project_invariants.md` 已同步
8. `project_invariants.md` 不再和当前三标签实现冲突
9. `GET /api/checkins/{checkin_id}/stream` 能按阶段推进，且 owner 之外访问返回 404
10. `static/app.js` 在 `pending` 时优先订阅流式状态/草稿，流不可用时自动退回轮询
11. `pending` 卡能显示 4 字段草稿预览，而不是只显示静态等待
12. quiz 首次生成后能入库到模板表，并记录最小路径边

---

## 当前风险

0. 当前 `promptfoo` 全量评测虽然已经成功启动，但 `40` 个 provider-case 组合在真实 LLM 上耗时很长；当前瓶颈是生成耗时，不是配置错误
0. 当前 `kimi-cli` 版 promptfoo 也已成功启动，但单条真实 review 仍需几十秒；它解决的是“评测链接法”，不是“单条评测很快”
0. `kimi-cli` 默认配置原本走 `kimi-code` provider；当前 runner 已显式注入 Moonshot 配置并对 fenced JSON 做兼容，否则会遇到 `LLM not set` 或 `invalid_json`
0. 已完成第二轮“去 editorial、去 llm-rubric”的快指标复测：baseline 和 mode-route 当前都达到 `json_ok_rate = 1.0`、`fields_ok_rate = 1.0`
0. mode-route 上一轮暴露出的 JSON 稳定性问题，已通过“禁止字段内容出现半角双引号”这条 prompt 约束显著收敛
0. 又捕获到一类新的 `invalid_json`：`stuck_bridge` 的 `transfer_signal` 会把题面特征再次包进半角双引号；当前已在 `stuck_bridge` supplement 中新增“不加引号”约束，并通过单点回测和整组快指标复测确认已收敛
0. 最新一轮“去 editorial、去 llm-rubric”的快指标为：
   - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 24.31`
   - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 29.98`
0. 已开始继续收“报告太元知识化”的问题：当前全局规则新增 `next_action / suggested_topic` 要优先回到当前题，不写专项训练、经典题、做3道、变式或拓展；`failed_verdict` 也要求优先指出当前题该先检查哪一处代码、判断或输出
0. 对 `failed_verdict_296` 的回测已确认这条规则有效：`next_action` 已回到当前题的 `且/或` 判断逻辑，不再默认滑向“做3道”式建议
0. 当前主线已经从“先收 JSON 稳定性”切到“继续跑带 `llm-rubric` 的非 editorial sample”，验证 mode-route 是否真的在质量分上优于 baseline
0. 已新增 `evals/review/run_review_quality_eval.py`，绕开 promptfoo 落表慢的问题，直接沿用同一批 case 和同一套 rubric 输出三指标
0. 当前这条直接质量评测链已经跑出一轮 non-editorial sample 结果：
   - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 0.667`、`rubric_avg_score = 1.667`
   - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`rubric_avg_score = 2.667`
0. 当前已能确认：mode-route 在 non-editorial sample 上不只是追平快指标，而且质量分也明显优于 baseline
0. 继续收 `stuck_bridge_57` 低分样例时，已观察到同一 prompt 在不同轮次上仍有随机波动：单点回测可返回合法 JSON，但单 case 质量评测里 mode-route 偶发又会掉到 `fields_ok = 0`
0. 当前剩余风险已经从“规则没写到”缩到“同一 prompt 的稳定性波动”；后续需要用重复跑或更稳的聚合方式来判断质量，不宜只看单次结果
0. `run_review_quality_eval.py` 当前已支持 `repeats` 聚合；已用 `stuck_bridge_57` 做 `repeats=2` 的最小验证，baseline 和 mode-route 当前都在 `rubric_avg_score = 2.0`，但 mode-route 仍有 `3 分 / 1 分` 的轮次波动
0. 已继续针对这条低分 case 收 prompt：`stuck_bridge` 现在额外要求不要只写限制条件、最优选择、当前进度这些抽象词
0. 当前 quality eval 的 judge 规则已正式收成 `evals/review/review_rubric_v2.json`，后续继续改评测标准时优先改 rubric 资产，不再直接把规则写死在脚本里
0. 当前真实高质量 `editorial_transfer` 样例只有 `2` 条，距离“每类 5-7 条”的理想覆盖仍有缺口
1. 当前 `minimum_spanning_tree <- 生成树` 这条映射仍偏宽，尚未进首批固定池
2. `binary_search_answer <- 二分` 当前仍标为 `defer`
3. 当前 `structure_type` 命中仍只是第一版标签映射，不是完整覆盖
4. 还没按当前版本的浏览器走查清单完成学生端真实 confirm 联调
5. 当前 `kimi-k2.5` 真实存在超时边界；即使服务已不再无限 `pending`，单条记录仍可能进入 `failed`
6. 旧进程如果没重启到带 timeout 的实例，个别 review 可能长期卡在 `pending`
7. 已用真实 `P5536` 样例复现：输入本身能过校验，但 review 生成仍可能长时间停在 `pending` 或最终 timeout
8. 当前已确认一个新的质量风险：`P5536` 这类树直径公式题，模型可能给出较准 diagnosis，但学生端字段会被 `greedy_basis` 模板盖偏
9. 当前 `max_tokens = 1200` 虽能把 `generate_review(...)` 的直接烟雾耗时压到约 `35.92s`，但会把部分输出压成“信息不足”式保守复盘，参数仍需校准
10. 当前工作区依然很脏，后续提交需要谨慎拆分
11. review prompt 压缩 v1 虽已上线实验，但仍需继续盯 3 个边界：
   - 全是泛标签时不能把标签行重新塞回 prompt
   - 关键错误公式如果在代码中段，裁剪后也必须保留下来
   - `problem_card` 不能把和当前卡点最相关的 `problem_context` 细节完全遮掉
12. 已用真实 `P5536` 样例复测压缩版 prompt：当前能在约 37.82 秒内成功返回，但会被压成 `insufficient + low`，说明“可用性保住了，诊断质量还没保住”
13. 已拆链确认：`P5536 -> insufficient` 当前不是 guard 拉回去，而是 `_call_llm()` 在 `completion_tokens = 1200` 时直接返回空字符串，`_parse_review("")` 才回落到默认 `insufficient`
14. 已补双轨实验：`compressed_1400` 和 `minimal4_1200` 都是“请求成功但空正文”，说明当前问题不只是字段数或 1200 上限，而是 `kimi-k2.5` 在这类结构化 review 请求上存在输出阶段异常
14.1 后续继续跑 quality eval 时，不能再默认把 `max_tokens/max_completion_tokens` 压到很低；我们已经验证过，这会在评测链里制造空输出、`invalid_json` 或错误，结果不可直接当作 prompt 质量结论。
15. Moonshot 官方文档对齐已开始落地：review 调用已切到 `response_format=json_object`、`max_completion_tokens`，并去掉了 `kimi-k2.5` 的显式 `temperature`
16. 新的真实边界已收窄：当前极简 JSON 烟雾调用不再出现“成功但空正文”，而是会明确落到 `finish_reason=length` 的截断失败
17. 已继续测 `max_completion_tokens` 档位：`1200/1600/1800` 都会以 `finish_reason=length` 截断，`1400` 反而直接超时；当前没有稳定可用窗口
18. 已确认 `timeout` 不是硬上限：把 `LLM_REQUEST_TIMEOUT_SECONDS` 压到 `5` 后，请求仍在约 `19.5s` 后才超时报错
19. 已把 review 主链改成 `stream=true` 并加了一次定向重试，但默认 `P5536` 样例仍在首次截断后重试失败，整次调用约 `83.78s`；当前这条路仍不足以恢复稳定正文
20. 已按用户要求把 `NOI_REVIEW_MAX_TOKENS` 的代码默认值调回 `32768`；这会减少“默认上限过小”的人为截断，但也会重新放大时长/成本风险，需重新做真实样例验证
21. 已完成一次真实样例复测：当前默认 `32768` 下，`P5536` 样例约 `80.04s` 后恢复出实体正文，说明“默认上限太小”确实是当前主因之一；但时长明显变长，仍需继续盯真实可用性
22. 当前新增的流式状态链只解决“等待黑盒”问题，不直接减少 review 真正生成耗时；如果 review 仍要 50-80 秒，前端只会更可见，不会更快
23. 当前前端流式实现依赖 `fetch + ReadableStream` 才能携带 `Authorization` 头，不能回退成裸 `EventSource`
24. 当前“流式正文”仍是草稿级预览，不是最终结构化复盘的逐 token 正文；最终内容仍以详情接口落库结果为准
25. 当前 quiz 模板库只是“先存、先连边”的骨架，还没切成模板优先检索，因此尚未真正减少 LLM 生成次数

---

## 下一步建议

- 先继续跑出至少一轮可用的 promptfoo 对比结果
- 先优先跑出一轮 sample 版 `promptfoo.kimi-cli.sample.yaml` 对比结果
- 先继续把快指标结果向 rubric 评测和更大样本扩展，确认提升不是偶然波动
- 优先记录三个数字：
  - JSON 合法率
  - 四字段非空率
  - llm-rubric 平均分
- 只有当 mode-route 版本相对 baseline 至少一项上升且整体不退，才继续深化 prompt family

1. 先完成这轮“状态 + 草稿”流式前端联调，确认 `pending -> 草稿长出 -> completed/failed` 在页面上真实可见
2. 若浏览器环境不支持流式读取或流意外断开，确认能自动退回现有轮询，不出现卡死
3. 流式草稿链稳定后，再按 `BROWSER_WALKTHROUGH_V1_2.md` 做 A/B/C 分流闭环联调
4. 再决定 quiz 模板库下一轮是否切到“模板优先，LLM 兜底”
5. review 耗时优化仍放在后面处理：当前更实际的是先确认默认 `32768` 在更多真实样例下是否稳定、时长是否可接受
6. `binary_search_answer` 继续维持 defer，暂不放开

### 2026-04-10 补充：外部 snippet 运行时接线第一步已完成

这轮已经真实落地：

- 已新增统一索引：
  - `docs/common/bridge_external_snippets_v1.jsonl`
- `review_engine.py` 已开始真实读取：
  - `docs/common/cp_pdf_bridge_snippets_v1.jsonl`
  - `docs/common/oi_wiki_bridge_snippets_v1.jsonl`
- 当前已经先把外部 snippet 接进这两类知识卡：
  - `string.trie.shared_prefix_merging`
  - `segment_tree.lazy_semantics`
- 当前学生端补课链路已经变成：
  - 本地知识卡骨架
  - + bridge 级外部教学化 snippet
  - 而不是只靠手写卡片
- 当前这一轮相关测试已全绿：
  - `test_review_engine_messages_unit.py`
  - `test_review_async_api_unit.py`
  - `run_test.sh`

当前下一步优先继续：

- 把同样的接线扩到：
  - `check_condition`
  - `left_bound_update`
  - `state_design`
- 再决定要不要把外部 snippet 轻量接进 deterministic remedy，而不只接知识卡

### 2026-04-10 补充：`shared_prefix_merging` 已开始区分节点计数语境

- 已补一轮真实弱链修复：
  - 当 trie 相关文本明确提到 `经过次数 / 结束次数 / 节点该存什么` 时
  - `generate_knowledge_bailout_card(...)`
  - `generate_knowledge_confirm_quiz(...)`
  - `_generate_bridge_specific_remedy_explanation(...)`
    都会切到“节点计数语义”版本
- 当前下一步：
  - 已完成消息层和全量回归
  - 已用 live 样例 `review_id=4190` 确认：
    - 主轮 `shared_prefix_merging`
    - follow-up
    - remedy
    - knowledge_bailout
    都能看到“经过次数 / 结束次数 / 101-100-11”这版小课
  - 已补 trie 节点计数语境的首轮 review 漂移纠偏：
    - `review_id=4200` 这类被 `state_design/implementation_debug` 词汇带偏的样例
    - 现在会在 `_guard_review_against_topic_drift(...)` 里直接拉回 `shared_prefix_merging`
  - 已把旧 `P2922` 噪音样例标成：
    - `legacy_bridge_noise`
    - `exclude_from_current_bridge_audit`
  - 阶段一已完成：
    - `method_selection`
    - `lazy_semantics`
    - `check_condition`
    - `shared_prefix_merging`
    这 4 条弱链都已重新审过并补过关键修复
  - 下一步改成：
    - 进入阶段二
    - 固定 8 个高频 bridge 的代表样例池
    - 继续补统一 snippet 的 `misconception / mini_example`

### 2026-04-11 补充：学生端已开始按“学生填写习惯”收边

- 已完成：
  - `AI 解答` 去掉学生不该碰的 `sessionId` 输入
  - `打卡复盘` 改成主输入优先、补充信息折叠
  - `历史详情` 改成学生视角文案，弱化系统内部字段
- 对应验证：
  - `test_student_entry_ui.mjs`
  - `test_checkin_identity.mjs`
  - `test_checkin_options.mjs`
  - `test_student_routes.mjs`
  - `test_vue_app_shell.mjs`
  - `npm run build`
  - `run_test.sh`
- 当前下一步：
  - 学生端真实浏览器路径已走通：
    - 登录
    - 打卡主输入三项提交
    - 自动进入历史详情
    - 返回历史列表
    - 再进入详情
  - 下一步继续做学生端细节收边：
    - 真实浏览器下的移动端宽度已检查：历史列表和详情在 375px 下无横向溢出
    - 历史详情页的 pending/review 生成中状态已收边：显示 `系统正在整理复盘` 和 `刷新详情`
    - 教师端四页真实交互走查
