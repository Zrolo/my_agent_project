# 当前系统状态（以代码为准）

## 本文件的写入标准

只写**当前已经在代码中真实成立**的系统状态：

- 已接通的 API
- 已入库的字段
- 已跑通的状态流
- 仍然只是骨架或 fallback 的功能
- 已知但尚未解决的边界

不要写：

- 长期产品原则
- 理想上未来应该怎样
- 尚未落地的方案设想

---

## 2026-04-04 补充：review mode 路由与 eval 基线骨架

## 2026-04-09 补充：讲解文案进一步学生化

## 2026-04-10 补充：外部 bridge snippet 已开始接入运行时知识卡

## 2026-04-10 补充：teacher 统计已补到 bridge / knowledge_bailout

## 2026-04-10 补充：阶段二已完成

## 2026-04-10 补充：阶段三已开始复审最弱 bridge

## 2026-04-10 补充：阶段三已完成

## 2026-04-11 补充：阶段四已启动并完成首批 visual_hint 精修

## 2026-04-11 补充：第五阶段已为首轮 review 接入轻量 bridge 约束

## 2026-04-11 补充：整站前端已切到 Vue 3 + Vite 新壳

## 2026-04-11 补充：前端 UI 已按 `ui-ux-pro-max` 方向完成第一版视觉重构

## 2026-04-12 补充：P3128 已接入 `tree_path_difference` 试点桥

当前代码中已经真实成立：

- review engine 已新增 focus：
  - `tree_path_difference`
- 该 focus 当前用于处理：
  - 多条树上路径
  - 经过次数统计
  - 树上差分
  - LCA / 最近公共祖先
  - 树剖 / 树链剖分相关路径贡献语境
- `P3128 [USACO15DEC] Max Flow P` 的典型复盘语境现在会优先进入：
  - `tree_path_difference`
- `P3258 [JLOI2014] 松鼠的新家` 这类“树上路线 / 房间访问次数 / 公共祖先 / 向上汇总”的自然语言复盘语境也会进入：
  - `tree_path_difference`
- 树上边经过次数语境当前会被识别为：
  - `tree_path_difference` 的边界样例
- 它不会再因为：
  - `标记` 被误吸到 `lazy_semantics`
  - `经过次数` 被误吸到 `shared_prefix_merging`
- 线段树区间修改语境仍会保留在：
  - `lazy_semantics`
- 当前本地确定性链路已覆盖：
  - main quiz
  - followup quiz
  - final micro confirm quiz
  - knowledge bailout card
  - knowledge confirm quiz
  - remedy explanation
- 当前桥梁语言固定为：
  - `树上路径贡献 -> 端点/LCA 附近差分标记 -> DFS 子树汇总 -> 每个点经过次数`
- 当前 `graph.tree_path_difference` 知识卡已补小板书：
  - `s += 1`
  - `t += 1`
  - `lca -= 1`
  - `parent(lca) -= 1`
  - `DFS 向上汇总`
- 当前 `docs/subjects/noi/bridge_map.md`
  - 已登记 `tree_path_difference`
- 当前 `docs/common/oi_wiki_bridge_taxonomy_mapping_v1.md`
  - 已把 OI Wiki 的 LCA / 树上路径统计语境映射到 `tree_path_difference`
- 当前外部 snippet 已新增：
  - `docs/common/oi_wiki_bridge_sources_v1.jsonl`
  - `docs/common/oi_wiki_bridge_snippets_v1.jsonl`
  - `docs/common/bridge_external_snippets_v1.jsonl`
- 运行时 `graph.tree_path_difference` 知识卡和 remedy 已能通过 bridge key 自动追加：
  - OI Wiki 改写后的 misconception
  - OI Wiki 改写后的 mini_example

当前已知边界：

- 这张桥当前按 P3128 的“点经过次数”版本落地
- 边差分题、纯 HLD 区间维护题，后续需要拆 variant 或补更细分知识卡
- 当前 snippet 是教学化改写，不是把 OI Wiki 原文整段搬进 prompt

当前代码中已经真实成立：

- 运行时前端主入口已从旧的：
  - `static/index.html + static/app.js + static/js/main.js + static/js/router.js`
  切到新的：
  - `Vue 3 + Vite + Pinia + Vue Router`
- 当前前端源码目录已新增：
  - `frontend/`
- 当前构建输出已固定到：
  - `static/dist/`
- `static/index.html` 当前只负责挂载：
  - `<div id="app"></div>`
  - `/static/dist/assets/app.css`
  - `/static/dist/assets/app.js`
- 当前后端 `/app/{path:path}` 入口已兼容新学生/教师路径：
  - `/app/workspace/chat`
  - `/app/workspace/checkin`
  - `/app/archive`
  - `/app/archive/:checkinId`
  - `/app/teacher/overview`
  - `/app/teacher/review`
  - `/app/teacher/students`
  - `/app/teacher/checkins`
- 当前学生端运行时壳层已由 Vue Router 统一接管，不再依赖旧 tab 心智
- 当前教师端运行时壳层也已迁到 Vue，并保留旧 teacher 路由 alias：
  - `/app/teacher/manual-review -> /app/teacher/review`
  - `/app/teacher/stats -> /app/teacher/overview`
  - `/app/teacher/quota -> /app/teacher/students`
  - `/app/teacher/flags -> /app/teacher/students`
- 当前旧学生路由 alias 也已兼容：
  - `/app -> /app/workspace/chat`
  - `/app/chat -> /app/workspace/chat`
  - `/app/checkin -> /app/workspace/checkin`
  - `/app/history -> /app/archive`
  - `/app/history/:id -> /app/archive/:id`
- 当前 `run_test.sh` 已纳入：
  - `npm run build`
  - `test_frontend_vue_entry_unit.py`
  - `test_student_routes.mjs`
  - `test_teacher_routes.mjs`
  - `test_vue_app_shell.mjs`
- 当前 Vue 新前端视觉系统已完成第一版统一重构，采用：
  - `Swiss Modernism 2.0 + Bento Grid` 的信息布局方向
  - `Plus Jakarta Sans + Noto Sans SC` 的中英文字体组合
  - richer palette 的模块分区色，而不是单一后台蓝
- 当前学生端模块色已真实接入：
  - `workspace/chat`：蓝青
  - `workspace/checkin`：橙金
  - `archive`：靛紫
- 当前教师端页面也已完成第一版运营工作台视觉分区：
  - `overview`：蓝紫
  - `review`：橙红强调
  - `students/checkins`：青灰中性
- 当前应用壳层、hero 区、导航、统计卡、工作卡、详情面板都已切到统一的 Vue 组件样式系统，不再依赖旧静态页拼装出来的视觉层
- 当前 Vue 运行时已新增统一的路由访问收口层：
  - `frontend/src/router/routeAccess.js`
  - 负责：
    - 学生/教师默认主页
    - pending path 归一化
    - 错角色壳层重定向
- 当前 auth 恢复已前置到 Vue 启动阶段：
  - `main.js` 在 mount 前执行 `auth.restore()`
  - `router.beforeEach(...)` 统一处理：
    - 未登录访问受保护页时记录 `pendingPath`
    - 已登录但进入错误壳层时重定向到对应角色主页
- 当前学生端与教师端 layout 已不再各自承担主要路由恢复职责，而是只处理：
  - 成功登录后的最终落页
  - 同角色页面内的壳层导航显示
- 当前学生端打卡页的 `completion_status` 已与后端真实枚举对齐：
  - `unfinished`
  - `hinted`
  - `editorial`
  - `independent`
- 当前已通过真实 API 走查确认：
  - 学生登录成功
  - 学生聊天接口可用
  - 学生打卡提交不再因旧前端枚举 `attempted / solved` 触发 `422`
  - 新提交可以返回 `checkin_id` 并立刻拉取详情
- 当前学生端页面头部已移除大段解释性说明和“当前页面 / 路由状态 / 目标”提示卡，改成更紧凑的页眉
- 当前历史详情页已从原始 JSON 展示改成可读详情视图：
  - 提交摘要
  - 复盘状态
  - 学习链路
- 当前 `/api/checkins/{checkin_id}` 已允许详情页拿到学生提交内容字段：
  - `completion_status`
  - `bottleneck_text`
  - `reflection`
  - `problem_context`
  - `error_types`
  - `student_code`

当前已知边界：

- 旧 `static/app.js` 及若干旧前端辅助模块仍保留在仓库里，主要是为了兼容测试与渐进清理，不再是运行时主路径
- 当前 Vue 页面的业务展示已可用，但部分学生/教师页仍是“结构化工作台壳层 + 接口原始数据”的第一版，不是最终内容精修态
- 当前 UI 已完成第一版结构和视觉重构，但还没有完成真实浏览器走查后的交互细节收边；例如：
  - 长列表和详情页在真实内容密度下的节奏
  - 登录恢复后的页面首屏观感
  - 局部状态空态/加载态的精修
- 如果本地 8000 仍在运行旧进程，需要重启后才能在浏览器里看到这轮详情字段和页面文案调整

当前代码中已经真实成立：

- 第五阶段已为首轮 review 接入轻量 bridge 约束
- 当前只覆盖 4 个 bridge：
  - `method_selection`
  - `shared_prefix_merging`
  - `check_condition`
  - `left_bound_update`
- 这层约束分两层：
  - prompt 轻约束
  - post-generation bridge consistency guard
- guard 的字段范围固定为 5 个：
  - `problem_focus`
  - `key_bridge`
  - `visual_hint`
  - `guided_walkthrough`
  - `try_now`

当前下一步：

- 用真实样例继续复审：
  - `P2922`
  - `P2678`
  - `P2249`

当前代码中已经真实成立：

- 阶段四当前已经开始，并且已完成首批高频 bridge 的 `visual_hint` 精修：
  - `check_condition`
  - `method_selection`（trie 语境）
  - `lazy_semantics`
  - `shared_prefix_merging`
  - `left_bound_update`
  - `transition_design`
  - `greedy_basis`
  - `tree_diameter_candidates`
  - `constraint_modeling`
- 当前这些高频 bridge 的知识卡和 deterministic remedy，都已经不再只是泛箭头提示，而是更像学生能一眼抓住的小板书：
  - `check_condition`
    - `check(5)=true`
    - `只说明 5 可行 / 5 还可行`
    - `再决定区间往哪边缩`
  - `method_selection`（trie 语境）
    - `101 / 100 / 11`
    - `前两条前面两位一样`
    - `这就是“相同开头”的题面信号`
    - `这是支持 trie 的题面信号`
  - `lazy_semantics`
    - `[1,4]`
    - `lazy=3`
    - `左儿长度=2`
    - `pushdown: 左儿 sum += 3×2`
  - `shared_prefix_merging`
    - `101 / 100 / 11`
    - `前缀 10 先合在一起`
    - `查询时只沿前缀路径往下走`
  - `left_bound_update`
    - `[1,2,2,2,3]`
    - `a[mid] == 2`
    - `mid 先留作候选`
    - `r = mid 继续往左缩`
  - `transition_design`
    - `当前格 (i,j)`
    - `上一层 (i-1,j-1)`
    - `上一层 (i-1,j)`
    - `先把来源想全，再写转移式`
  - `greedy_basis`
    - `[1,3] 先选`
    - `[3,5] 还能接上`
    - `后面还有空间`
    - `这一步才不吃亏`
  - `tree_diameter_candidates`
    - `左边最远点`
    - `右边最远点`
    - `经过新边接起来`
    - `先比较这三类候选`
  - `constraint_modeling`
    - `A <= B + c`
    - `B <= C + d`
    - `先统一成同一种关系`
    - `再看谁限制谁`
- 这轮只收紧了学生可见图示，没有改：
  - review 状态机
  - bridge 路由
  - API 字段形状
- 第四阶段当前已经把高频 bridge 和代表性长尾 bridge 的主图示精修收口
- 如果继续往下做，下一步更适合转去：
  - 正式收阶段四
  - 或开启下一阶段

- 阶段三当前已经完成对三条最弱高频 bridge 的复审：
  - `method_selection`
  - `shared_prefix_merging`
  - `lazy_semantics`
- 当前复审结论是：
  - `method_selection`
    - 在 trie 语境下已较稳
    - 已能稳定讲清“不要凭题感猜 trie，要回到题面信号”
  - `shared_prefix_merging`
    - 已较稳
    - live 链里已经稳定出现：
      - `经过次数`
      - `结束次数`
      - `101 / 100 / 11`
      - `前缀 10 这个节点`
  - `lazy_semantics`
    - 已较稳
    - `remedy / knowledge card / knowledge confirm` 都已稳定围绕：
      - “这段区间已经确定、但还没下传给孩子的信息”
      - `[1,4] / lazy=3 / 3×2`
- 阶段三剩余问题主要不再是主链跑不通，而是：
  - 某些 bridge 的 `visual_hint` 还能继续精修
  - 历史库里仍有旧噪音需要在评估时隔离

- 阶段三当前已经开始围绕固定样例池复审最弱高频 bridge
- 第一条已复审的是：
  - `method_selection`
  - 代表题：
    - `P2922 [USACO08DEC] Secret Message G`
- 当前代码路径下，`method_selection` 在 trie 语境里已经能稳定给出：
  - 先破“凭题感猜 trie”的误解
  - 再点出：
    - `很多字符串`
    - `反复前缀关系`
    - `101 / 100 / 11`
  - remedy 和 knowledge confirm 也都围绕“题面信号支持 trie”这一步，不再只停在抽象方法名层
- 当前这座桥剩下的主要问题已不是运行时内容，而是：
  - 真实库里仍有旧 quiz 重复记录
  - 评估时容易和 `shared_prefix_merging` 混评

- 阶段二当前已经收完三件事：
  - 已固定 8 个高频 bridge 的代表样例池：
    - `docs/common/high_frequency_bridge_sample_pool_2026_04.md`
  - 统一 snippet 索引里已经真实存在：
    - `bridge_explanation`
    - `algorithm_overview`
    - `misconception`
    - `mini_example`
  - 这些 snippet 不再只停在文档层，而是已经真实接入：
    - `knowledge card`
    - `deterministic remedy`
- 当前统一 snippet 运行时入口是：
  - `docs/common/bridge_external_snippets_v1.jsonl`
- 阶段二当前重点覆盖的高频 bridge 为：
  - `state_design`
  - `transition_design`
  - `check_condition`
  - `left_bound_update`
  - `lazy_semantics`
  - `shared_prefix_merging`
  - `complexity_fit`
  - `method_selection`
- 这意味着当前系统已经不只是“有外部知识源文件”，而是形成了：
  - 固定样例池
  - 统一 snippet 索引
  - 运行时 bridge 级接线
  这一整套阶段二基础设施

- `/api/teacher/stats` 当前除了已有的：
  - `mastery_status_stats`
  - `bridge_path_stats`
  还新增返回：
  - `bridge_stats`
  - `knowledge_bailout_stats`
  - `topic_l1_stats`
  - `topic_l2_stats`
- `bridge_stats` 当前按 `reviews.key_bridge` 聚合
  - 目的是让老师直接看到最近 30 天学生最常卡在哪座知识桥
- `knowledge_bailout_stats` 当前按是否进入：
  - `knowledge_bailout_success`
  - `knowledge_bailout_failed`
  聚合成：
  - `entered`
  - `not_entered`
- teacher 前端统计页现在新增两张卡：
  - `高频知识桥分布`
  - `知识卡介入分布`
- teacher 前端统计页现在也新增两张 topic 卡：
  - `知识域分布`
  - `知识子域分布`
- `topic_l1/topic_l2` 当前不是从完整 taxonomy 自动推理，而是先按稳定的 `bridge -> topic_l1/topic_l2` 映射表聚合高频 bridge
- teacher 统计页当前也已补上高频：
  - `bridge`
  - `topic_l1`
  - `topic_l2`
  的中文标签映射
- 这一轮没有改：
  - teacher 手工复核协议
  - review 状态机
  - bridge 路由逻辑

当前代码中已经真实成立：

- `P2922` 这类 trie 题如果学生已经在说：
  - `节点该存什么`
  - `经过次数`
  - `公共前缀`
  - `前缀关系`
  后续 quiz 焦点现在会优先落到 `shared_prefix_merging`，不再轻易掉回通用 `state_design`
- `string.trie.shared_prefix_merging` 和 trie 语境下的 `modeling.method_selection`，现在在知识卡和 deterministic remedy 里都补了一个最小算例：
  - `101`
  - `100`
  - `11`
  - 前两条前面两位一样，所以这段相同开头值得先合在一起看
- `binary_search.check_condition` 的 deterministic remedy 和知识卡现在都补了一个最小算例：
  - `check(5)=true`
  - 只说明“答案至少还能达到 5/当前 mid 可行”这句话成立
- `segment_tree.lazy_semantics` 的 deterministic remedy 和知识卡现在都补了一个最小算例：
  - 节点管 `[1,4]`
  - `lazy=3`
  - 左儿子长度 `2`
  - pushdown 时左儿子的 `sum` 会先加 `3×2`
- 这两个桥现在都已经有**干净的新真实链**，而且都已真实走到知识卡阶段：
  - `check_condition`
    - `checkin_id=4225`
    - `review_id=4073`
    - `quiz_id=1150 / 1151`
  - `lazy_semantics`
    - `checkin_id=4226`
    - `review_id=4074`
    - `quiz_id=1152 / 1153`
- 这轮改动只收紧了学生可见文案，没有改：
  - review 路由
  - quiz 状态机
  - API 字段形状

- `review_engine.py` 已新增外部 snippet 读取与 bridge 级选择逻辑：
  - `_load_external_bridge_snippets()`
  - `_pick_external_bridge_snippet(...)`
  - `_augment_knowledge_card_with_external_snippets(...)`
- 外部 snippet 的运行时入口现在已统一优先走：
  - `docs/common/bridge_external_snippets_v1.jsonl`
- 只有当统一索引缺失时，才回退读取：
  - `docs/common/cp_pdf_bridge_snippets_v1.jsonl`
  - `docs/common/oi_wiki_bridge_snippets_v1.jsonl`
- 当前会从两类来源加载教学化 snippet：
  - `docs/common/cp_pdf_bridge_snippets_v1.jsonl`
  - `docs/common/oi_wiki_bridge_snippets_v1.jsonl`
- 当前不是把外部资料原文直接丢给学生，而是：
  - 先做 bridge 级片段
  - 再在知识卡阶段按 bridge 追加进学生化文案
- 当前已经接入运行时知识卡的 bridge 有五类：
  - `string.trie.shared_prefix_merging`
  - `segment_tree.lazy_semantics`
  - `binary_search.check_condition`
  - `binary_search.left_bound`
  - `dp.state_design`
- 其中：
  - `shared_prefix_merging` 会优先吸收：
    - OI Wiki 的 `bridge_explanation`
    - cp-pdf 的 `algorithm_overview`
    - cp-pdf 的补充 `bridge_explanation`
  - `lazy_semantics` 会优先吸收：
    - OI Wiki 的 `bridge_explanation`
  - `check_condition` 会优先吸收：
    - OI Wiki 的 `bridge_explanation`
  - `left_bound_update` 会优先吸收：
    - OI Wiki 的 `bridge_explanation`
    - cp-pdf 的补充边界图景
  - `state_design` 会优先吸收：
    - OI Wiki 的 `bridge_explanation`
    - cp-pdf 的补充状态语义图景
- 当前这层接线只发生在：
  - `generate_knowledge_bailout_card(...)`
- 同一套统一 snippet 入口现在也已开始轻量接进 deterministic remedy：
  - `dp.state_design`
  - `binary_search.check_condition`
  - `binary_search.left_bound`
  - `dp.transition_design`
  - `modeling.scale_estimation`
  - `modeling.method_selection`
- 当前没有改：
  - review 首轮诊断
  - quiz 角色与状态机
  - API 字段形状
  - 前端渲染协议

这说明外部知识源现在已经不只是文档层，而是开始真实进入学生补课链路。

当前代码中已经真实成立：

- `api_server.has_explicit_help_signal(...)` 现在不再把所有 `wa/tle/re/ce` 一刀切成“显式求助”
  - 如果学生已经点名了具体桥，如 `a[mid] == x`、`lazy`、`trie`、`左边界` 等，就仍然优先进入 quiz 梯子
- `review_engine._detect_quiz_focus(...)` 在 `core_design` 下已把：
  - `left_bound_update`
  - `tree_diameter_candidates`
  放在泛 `constraint_modeling / general_modeling` 之前判断
- `constraint_modeling` 现在也已接入 deterministic remedy
  - 差分约束/关系建模这类桥在补课阶段不再默认先卡一轮 LLM
- `remedy/resolve` 当前真实学习流是：
  - 先进入 `final_micro_confirm`
  - 答对后再 `resolved`
  - 不再是旧版“补课点完成就直接 resolved”

- 高频桥里新增并接通了 3 个更细的 focus：
  - `left_bound_update`
  - `shared_prefix_merging`
  - `lazy_semantics`
- `review_engine._detect_quiz_focus(...)` 现在已经能：
  - 把 `P2249` 这类“找最左边界”更稳定地判到 `left_bound_update`
  - 把 `P2922` 这类题里的“题面为什么支持 trie”与“trie 为什么只沿前缀走”拆成两个桥：
    - `method_selection`
    - `shared_prefix_merging`
  - 把带明显 `lazy / 下传 / 懒标记` 信号的卡点判到 `lazy_semantics`
- 高频桥知识卡现在新增并接通：
  - `binary_search.left_bound`
  - `segment_tree.lazy_semantics`
- 高频桥知识卡命中规则已收紧：
  - `method_selection + trie` 现在优先留在 `modeling.method_selection`
  - 只有显式机制桥才进入 `string.trie.shared_prefix_merging`
- `trie + method_selection` 的后半段已继续收紧：
  - deterministic remedy 会明确过渡到“很多消息有相同开头，值不值得先合在一起看”
  - knowledge card 后确认题也会显式确认“相同开头 + 反复按前缀查”这组信号，不再只停在抽象的方法名层
- 高频桥的 deterministic remedy 已新增本地参数化讲解，不再默认先打 LLM：
  - `modeling.scale_estimation`
  - `modeling.method_selection`
  - `string.trie.shared_prefix_merging`
  - `segment_tree.lazy_semantics`
  - `binary_search.left_bound`
  - `binary_search.check_condition`
  - `dp.state_design`
  - `dp.transition_design`
- 当前这些桥在 `generate_remedy_explanation(...)` 里已经会优先走本地讲解，再决定是否需要更重兜底
- 其中 `check_condition / left_bound / state_design / transition_design / complexity_fit / method_selection` 现在会继续吸收统一 snippet 入口里的外部桥级片段，不再只有知识卡能看到这层外部知识
- 当前已经把高频 bridge 的人工审查结果固化到：
  - `docs/common/bridge_audit_board_2026_04.md`
- 这份总表当前最重要的两个结论是：
  - `state_design / transition_design / left_bound_update / complexity_fit` 已经比较稳
  - `P2922` 相关的 `method_selection / shared_prefix_merging` 仍然最需要继续盯
- 当前现在已经有真实主轮历史链路的代表桥：
  - `check_condition`
    - `checkin_id=4142`
    - `review_id=3994`
    - `quiz_id=1124`
  - `lazy_semantics`
    - `checkin_id=4084`
    - `review_id=3941`
    - `quiz_id=1106`
- 另外，当前还新增了两条更干净、适合优先评估当前系统表现的新链：
  - `checkin_id=4225 / review_id=4073`
  - `checkin_id=4226 / review_id=4074`
- `check_condition` 这类二分判定桥现在又补稳了一层：
  - 当 `error_layer=method` 但学生文本明确在问：
    - `check(mid)`
    - `返回 true`
    - `当前 mid 可行`
    - `二分方向`
  - `_detect_quiz_focus(...)` 现在会优先判到：
    - `check_condition`
  - 主轮 quiz 也不再从 generic structural 路径打到 LLM，而是优先走本地 deterministic `check_condition` 主轮
- 当前历史库里的：
  - `checkin_id=4083`
  - `review_id=3940`
  仍然证明首轮 review 能落到 `check_condition`
  但它库里的主轮 quiz 是修复前生成的旧噪音，当前评估应优先看：
  - `checkin_id=4225`
  - `review_id=4073`
  - `quiz_id=1150`
  - `quiz_id=1151`
- 当前这轮没有改：
  - review JSON schema
  - API 字段形状
  - quiz 角色与状态机
  - 前端渲染协议

- `review_engine._build_review_system_prompt(...)` 的通用规则已新增一条更明确的学生化约束：
  - 能对比时，先说学生最容易误会的一句话
  - 再说正确的一句话
- 当前第一轮复盘 prompt 已不只要求“短句、说人话”，还要求更明确地做“误解 -> 正解”对比
- 当前高频知识卡模板已统一往“最容易误会什么 / 真正要站稳什么”收口，不再只给平铺直叙的说明
- 当前高频知识卡的 `algorithm_overview` 已进一步压缩成：
  - 这一步在整套方法里负责什么
  - 不再默认写成更大块的算法讲义

当前这轮已明确收紧的卡片包括：

- `dp.state_design`
- `dp.transition_design`
- `binary_search.check_condition`
- `greedy.greedy_basis`
- `graph.tree_diameter.tree_diameter_candidates`
- `string.trie.shared_prefix_merging`
- `modeling.method_selection`
- `modeling.scale_estimation`

当前这轮没有改：

- review JSON schema
- quiz 角色与状态机
- API 字段形状
- 前端渲染协议

当前代码中已经真实成立：

- `review_engine.generate_review(...)` 入口会先做：
  - `submission_result = (submission_result or "unknown").strip().lower()`
- `review_engine.py` 已新增 `_detect_review_mode(...)`
  - `wa/tle/re/ce -> failed_verdict`
  - `editorial -> editorial_transfer`
  - `unfinished/hinted -> stuck_bridge`
  - 其他 -> `independent_reflect`
- `_build_review_system_prompt(mode=...)` 已在原有 JSON schema / 字段骨架不变的前提下，接入 4 套 supplement
- 当前没有改：
  - `_parse_review(...)`
  - 现有 guard
  - `_call_llm(...)`
  - review JSON schema

当前仓库里已经新增评测骨架：

- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/export_cases.py`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/run_review_case.py`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/run_review_case_kimi_cli.py`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.yaml`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.kimi-cli.yaml`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/cases.jsonl`
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo_tests.jsonl`

其中：

- `export_cases.py` 会从真实 `checkins + reviews` 中筛 `review_status=completed` 且四字段非空的样例
- 当前已导出 `20` 条真实 case：
  - `independent_reflect = 6`
  - `failed_verdict = 6`
  - `stuck_bridge = 6`
  - `editorial_transfer = 2`
- `editorial_transfer` 当前只有 `2` 条，不是脚本 bug，而是现有真实库里满足“非 failed 且 editorial 且四字段完整”的高质量样例本来就少
- `run_review_case.py` 已能直接读取单条 case，并真实调用 `generate_review(...)`
- `run_review_case_kimi_cli.py` 已能：
  - 复用 `review_engine` 当前真实的 system/user prompt builder
  - 显式向 `kimi-cli` 注入 Moonshot OpenAI Legacy 配置，避免默认 `kimi-code` provider 导致的 `LLM not set`
  - 自动剥掉 `kimi-cli` 返回中的 ```json fenced block``` 后再解析 JSON
- 当前已经用 `cases.jsonl` 第一条真实 case 验证过：
  - `run_review_case_kimi_cli.py` 可返回实体 review JSON，不再停在接入错误
- `promptfoo 0.121.3` 已安装，`promptfoo.yaml` 已成功启动评测，不存在 YAML/exec provider 级语法错误
- `promptfoo.kimi-cli.yaml` 也已成功启动 baseline + mode-route 的双 provider 评测，不存在 exec provider 级错误
- `build_promptfoo_sample.py` 已可生成一套更轻的 sample 测试集：
  - 每种 mode 各 `1` 条
  - 当前总计 `4` 条 case、`8` 个 provider-case 组合
- `promptfoo.kimi-cli.sample.yaml` 已能成功启动 sample 版评测
- 已用 `kimi-cli` runner 对“去 editorial、去 llm-rubric”的 `3 case x 2 provider` 组合做了一轮快指标对比：
- 已继续复测同一组快指标；当前最新一轮结果为：
  - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 24.31`
  - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 30.95`
- 已确认上一轮 mode-route 的主要短板确实是 JSON 稳定性；抓到过至少一条真实坏样例是字段内容里出现未转义半角双引号，导致 `invalid_json`
- 已在 `_build_review_system_prompt(...)` 的全局规则中新增：不要在字段内容里使用半角双引号；引用题面词语时直接改写，或不用引号
- 针对 `stuck_bridge_57` 的第一轮直接回测已恢复为合法 JSON，但后续复测中又暴露出第二类 `invalid_json`：`transfer_signal` 会把题面特征再次包进半角双引号
- 已在 `stuck_bridge` supplement 中新增：`transfer_signal` 不要给题面特征加引号
- `stuck_bridge_57` 在第二轮单点回测后已再次恢复为合法 JSON；继续复测同一组快指标后，mode-route 重新稳定在 `fields_ok_rate = 1.0`
- 当前最新一轮快指标为：
  - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 24.31`
  - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 29.98`
- 已继续收“报告太元知识化”的问题：当前在全局规则中新增 `next_action / suggested_topic` 优先回到当前题，不写专项训练、经典题、做3道、变式或拓展；`failed_verdict` supplement 也新增了“先检查当前题哪一处代码、判断或输出”
- 对 `failed_verdict_296` 的直接回测已验证：`next_action` 现可回到当前题里的 `且/或` 判断逻辑，不再默认滑向“做3道”式建议
- 当前已重新切回带 `llm-rubric` 的非 editorial sample promptfoo 长跑，用于验证 mode-route 是否在质量分上优于 baseline
- 当前已新增一条不依赖 promptfoo 落表的直接质量评测脚本：
  - `evals/review/run_review_quality_eval.py`
  - 会沿用同一批 case、同一组 `baseline_current_kimi_cli / mode_route_kimi_cli` 和同一套 rubric 规则，直接输出：
    - `json_ok_rate`
    - `fields_ok_rate`
    - `rubric_avg_score`
- 当前这条质量评测链的 rubric 规则已从脚本内联文本收成独立资产：
  - `evals/review/review_rubric_v2.json`
  - 后续更新 judge 标准时，可优先改 rubric 文件，而不必改脚本主体
- 已用 non-editorial sample 跑出一轮三指标：
  - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 0.667`、`rubric_avg_score = 1.667`
  - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`rubric_avg_score = 2.667`
- 当前这轮直接质量评测已证明：mode-route 不只是追平快指标，而且在 non-editorial sample 上已经明显优于 baseline
- 继续针对 `stuck_bridge_57` 做低分 case 回测时，又观察到同一 prompt 存在轮次波动：
  - 单点直接回测可返回合法 JSON 和完整四字段
  - 但单 case 质量评测中，mode-route 偶发仍可能掉到 `fields_ok = 0`
- 当前剩余问题已从“提示词规则缺失”收窄到“同一 prompt 的稳定性波动”；后续评测更适合引入重复跑或聚合分数，而不是只看单次结果
- `run_review_quality_eval.py` 当前已支持 `repeats` 参数，可对同一 case/provider 做重复跑并输出聚合均值与逐次 `attempts`
- 已用 `stuck_bridge_57` 做 `repeats=2` 的最小聚合验证：
  - `baseline_current_kimi_cli`：`rubric_avg_score = 2.0`
  - `mode_route_kimi_cli`：`rubric_avg_score = 2.0`
  - mode-route 当前在这条 case 上仍会出现 `3 分 / 1 分` 的波动，说明这条样例的主要剩余风险已从“必然失败”变成“表达稳定性不足”
- 已继续收这条低分样例：在 `stuck_bridge` supplement 中新增“不要只写限制条件、最优选择、当前进度这些抽象词”
- 当前真实瓶颈是：全量 `40` 个 provider-case 组合跑得很慢，不是评测骨架起不来

## 一、当前学生端主结构

学生端当前已经是三个一级入口：

- `AI 解答`
- `打卡复盘`
- `历史打卡`

其中：

- `AI 解答` 是聊天工作区，按 `student_id + problem_id + session_id` 维持会话历史
- `打卡复盘` 是统一工作台，当前只保留提交表单和当前选中记录的工作台
- `历史打卡` 是学生区内部独立标签，用现有 `GET /api/checkins/me` 数据源展示紧凑历史列表

学生端工作台已经接通：

- 左侧：提交表单
- 中间：理解检查 / quiz / self-check / remedy
- 右侧：AI 复盘 + 同类题 + 同题最近 AI 解答摘要

移动端折叠顺序已经在前端实现为：

1. 右侧复盘区
2. 中间小测区
3. 左侧提交与历史区

---

## 二、当前已接通的主要 API

### 认证与聊天

- `POST /auth/login`
- `POST /chat`
- `GET /quota/{student_id}/{problem_id}`
- `POST /quota/reset`

### 学生端题目导入 / 打卡 / 复盘

- `POST /api/problem-import`
  - 当前支持洛谷题号或公开题目链接
  - 本地题库优先，网页抓取兜底
- `GET /api/problems/related`
  - 基于本地洛谷题库按 `algo_tags + difficulty` 找同类题
- `POST /api/checkins`
- `GET /api/checkins/{checkin_id}`
- `GET /api/checkins/{checkin_id}/stream`
- `POST /api/checkins/{checkin_id}/review/retry`
- `GET /api/checkins/me`

### 理解检查链路

- `POST /api/reviews/{review_id}/quiz/generate`
- `POST /api/quizzes/{quiz_id}/answer`
- `POST /api/reviews/{review_id}/self-check`
- `POST /api/reviews/{review_id}/remedy`
- `POST /api/reviews/{review_id}/remedy/resolve`

### 教师端

- `GET /api/teacher/checkins`
- `GET /api/teacher/stats`
- `GET /api/teacher/flags`
- `GET /api/teacher/usage`
- `POST /api/teacher/reviews/retry-pending`
- `GET /api/teacher/problems/analysis-failures`
- `POST /api/teacher/problems/analysis/retry`

### 页面入口

- `GET /`
- `GET /app`

其中学生端打卡复盘当前已经接通一条“流式状态、非流式正文”的等待链：

- 提交打卡后，前端优先用 `fetch + ReadableStream` 订阅 `GET /api/checkins/{checkin_id}/stream`
- 后端通过固定阶段埋点推送状态事件，不直接流正文 token
- 当前阶段包括：
  - `received`
  - `queued`
  - `llm_start`
  - `llm_done`
  - `review_parse`
  - `review_saved`
  - `quiz_generating`
  - `completed`
  - `failed`
- 当前前端不会用裸 `EventSource`，因为认证仍依赖 `Authorization: Bearer ...` 请求头
- 流式状态链断开或不可用时，前端会自动退回现有单条 checkin 轮询

在此基础上，当前又补了一层“流式正文草稿预览”：

- review 调用仍保持结构化 JSON 输出，不改最终 schema
- 后端会在模型流式 chunk 到来时，尽量从累计 JSON 文本里抽出：
  - `main_block`
  - `key_bridge`
  - `next_step`
  - `transfer_signal`
- SSE 当前除了 `status / review_ready / error / keepalive` 之外，还会发：
  - `review_chunk`
- 前端 `pending` 卡会优先显示：
  - 当前阶段
  - 已等待秒数
  - `AI 草稿预览`
- 正式复盘完成后，右侧仍由现有详情接口覆盖成正式内容

学生端最终复盘卡当前也已收成两层：

- 默认只展示：
  - `你卡在哪`
  - `关键一步`
  - `现在先做`
  - `下次提醒`
- `错误标签 / 统一归类 / 判断把握 / 子标签 / 详细诊断 / 下一步行动 / 推荐专题`
  只有在有内容时才进入折叠层显示

---

## 三、数据库已入库的关键结构

### 1. `checkins`

当前已经包含：

- 基础字段：
  - `student_id`
  - `problem_url`
  - `problem_title`
  - `oj_source`
  - `completion_status`
  - `bottleneck_text`
  - `error_types`
  - `reflection`
- v2.1 输入增强字段：
  - `problem_context`
  - `submission_result`
  - `student_code`
  - `problem_tags`
  - `chat_context_summary`

### 2. `reviews`

当前已经包含：

- 旧字段：
  - `error_tags`
  - `diagnosis`
  - `next_action`
  - `suggested_topic`
- 当前结构化复盘字段：
  - `review_status`
  - `error_layer`
  - `error_layer_confidence`
  - `core_design_subtags`
  - `main_block`
  - `key_bridge`
  - `next_step`
  - `transfer_signal`
  - `review_quality_flags`
- 学习状态流字段：
  - `learning_status`
  - `understanding_self_check`
  - `bridge_path`
  - `remedy_count`
- 异常 / 重试字段：
  - `retry_count`
  - `last_error`
  - `last_attempt_at`

### 3. `review_quizzes`

当前已经包含：

- `quiz_role`
- `quiz_type`
- `question_text`
- `options_json`
- `correct_answer`
- `explanation`
- `bridge_feedback`
- `distractor_feedback`
- `target_bridge`
- `source_error_layer`
- `status`
- `meta_json`

### 4. `quiz_attempts`

当前已记录：

- `answer_text`
- `is_correct`
- `feedback_text`

### 5. 本地题库

#### `problems`

当前已经包含：

- `luogu_pid`
- `title`
- `difficulty`
- `statement_json`
- `samples_json`
- `time_limit_ms`
- `memory_limit_kb`
- `raw_json`
- `source`
- `source_url`
- `imported_at`
- `updated_at`

#### `problem_tags`

当前已经包含：

- `problem_id`
- `tag_name`
- `tag_type`

并且已经有：

- `(problem_id, tag_name)` 唯一约束
- `(tag_type, tag_name)` 索引

#### `problem_analysis`

当前已经包含：

- `summary`
- `strategy_types`
- `knowledge_points`
- `common_mistakes`
- `analysis_version`
- `status`
- `last_error`
- `retry_count`

#### `review_sessions`

当前已经包含：

- `student_id`
- `problem_id`
- `checkin_id`
- `prompt_tokens`
- `completion_tokens`
- `latency_ms`
- `model_tier`
- `analysis_source`
- `prompt_cache_hit`
- `review_result_json`

### 6. `confirm_pool`

当前已经新增：

- `problem_id`
- `problem_url`
- `structure_type`
- `difficulty`
- `bridge_note`
- `status`
- `skip_count`

并且已经有：

- `(status, structure_type)` 索引
- `structure_type` 唯一约束

---

## 四、题库与题目卡当前状态

当前本地洛谷题库链路已经成立：

- `import_luogu_problemset.py` 可从本地 `latest.ndjson` 导入题库
- `problem_bank.py` 已负责：
  - 洛谷题号 / 链接归一化
  - `tag_type` 分类
  - `build_problem_context`
  - `build_compact_card`
  - `build_full_card`
  - `problem_analysis` 懒加载
  - 失败后重试

当前题目卡分为两种：

- `compact_fallback`
  - 不经过 LLM
  - 直接由官方题面裁剪
- `full_card`
  - 依赖 `problem_analysis.status = completed`
  - 含 `summary / strategy_types / knowledge_points / common_mistakes`

当前复盘时：

- 如果有 `full_card`，优先传结构化完整卡
- 否则传 `compact_fallback`

---

## 五、AI 复盘当前真实行为

### 复盘输入当前可利用的上下文

`generate_review(...)` 当前已经会综合：

- 题目标题
- 来源
- 完成状态
- `problem_card`（优先）
- 或 `problem_context`
- 平台标签（仅辅助）
- 同题最近 AI 解答摘要 `chat_context_summary`
- 提交现象
- 卡点描述
- 错误类型
- 反思
- 学生代码

### 复盘输出当前已稳定字段

- `error_tags`
- `error_layer`
- `error_layer_confidence`
- `core_design_subtags`
- `diagnosis`
- `next_action`
- `suggested_topic`
- `main_block`
- `key_bridge`
- `next_step`
- `transfer_signal`
- `review_quality_flags`

### 当前已知复盘守卫

代码里已存在多层 guard，用于：

- topic drift 收紧
- overclaim 收紧
- teacher guidance 收紧
- insufficient 保守处理
- 学生语言简化
- review quality flag 检查

### review 上游桥梁稳定性当前已落地状态

针对高风险 review focus，当前代码里已经有第一轮专门收紧：

- `general_modeling`
- `constraint_modeling`
- `greedy_basis`
- `method_selection`

当前这轮已真实落地的内容包括：

- `test_review_regression.py` 已把这 4 个 focus 纳入回归门
- `B1 / D1` 已不再只靠固定短词命中；当前脚本里已经增加独立结构断言函数，并新增 `test_review_regression_unit.py` 做正反例单测
- 回归脚本会把以下情况直接判失败：
  - `review_status != completed`
  - 请求异常
  - 明显泛建议
  - 结构词命中明显不足
- `B1` 当前会额外检查：
  - 时间 / 地点两个条件是否被讲成平级同时成立
  - 是否滑成“先满足 A，再检查 B”的顺序结构
  - `next_step` 是否仍是学生可直接执行的动作
- `D1` 当前会额外检查：
  - 是否先看规模 / 范围再决定方法
  - 是否明确落到可直接枚举而不是先上 DP
  - `next_step` 是否给出规模判断或枚举起手动作
- `review_engine.py` 已对这 4 个 focus 增加更积极的 bridge stability guard
- guard 当前不只会兜底 `key_bridge / next_step`，也会兜底 `main_block / transfer_signal`
- `general_modeling` 已补过一次 focus 优先级修正，避免对象-关系题被过早拉到约束建模
- `method_selection` 已补过一次 topic drift 修正，避免“小规模先看范围”的题因为学生提到 DP 就被拉回 DP 兜底文案

---

## 六、quiz / 理解检查当前真实状态

当前理解检查链路已经跑通：

- `main`
- `followup`
- `confirm`
- `remedy`

当前 quiz 已经具备：

- `bridge_feedback`
- `distractor_feedback`
- `answer_type`
- `fallback_explain`

当前已经做过的收紧包括：

- judgement（对/错）题已被禁用
- 元认知口号题被 prompt 规则和后端双重过滤
- `answer_type = learning_advice` 时会退回 `fallback_explain`
- `general_modeling / constraint_modeling / greedy_basis / method_selection` 等易滑回口号题的 focus，当前在部分场景下会“宁可 fallback，也不放坏题”

---

## 七、学生端当前数据流已接通情况

### 1. AI 解答 → 复盘工作台

当前已经接通：

- 同题最近 AI 解答会在前端本地缓存为摘要
- 学生提交打卡时，`chat_context_summary` 会一起带给后端
- AI 复盘会把它作为辅助线索，不替代本次卡点
- 右侧复盘区可展示这条关联摘要

### 2. 历史记录 → 工作台切换

当前已经接通：

- `历史打卡` 标签内的历史卡点击后，会切换整条工作台上下文
- 点击历史记录后，前端会自动切回 `打卡复盘` 标签
- 中间区和右侧区会随当前选中 checkin 一起更新
- 学生提交打卡后，`POST /api/checkins` 已改成立即返回 `review_status = pending`
- 前端会轮询单条状态接口，而不是反复拉整页历史列表
- 右侧工作区当前已区分：
  - `pending` 等待卡
  - `failed` 失败卡 + 重新生成按钮
  - `timeout` 超时提示卡
  - `completed` 正式复盘内容

### 2.1 打卡复盘的快反馈状态流

当前已经真实成立：

- checkin 入库成功后，请求线程不再等待整条 review 生成完成
- review 生成已改为后台任务执行
- 当前代码已增加“最多 5 个并发 review 生成”的上限控制
- `review_engine.py` 当前已给 LLM 调用补上请求级 timeout，避免后台线程无限挂住
- 学生端单条状态接口当前有鉴权边界：
  - 必须是当前登录学生本人
  - 不属于当前学生的 checkin 返回 `404`
- retry 接口当前只允许：
  - `review_status = failed`
- retry 接口当前明确拒绝：
  - `pending`
  - `completed`
- 学生端单条状态接口不会暴露真实 `review_last_error`

### 3. 复盘 → 同类题

当前已经接通：

- 右侧可以按题号调用 `/api/problems/related`
- 当前规则基于 `algo_tags + difficulty`

---

## 八、仍然只是骨架或半成品的部分

### 学生分流 / confirm 当前已落地边界

当前后端已经有统一学习路由入口：

- `A` 类显式卡住信号：
  - 关键词枚举：`不会`、`卡住`、`需要提示`、`看不懂`、`没思路`
  - `completion_status = hinted`
  - `submission_result in {wa, tle, re, ce}`
- `B` 类解释层过线：
  - `main` 必须答对
  - `followup` 若存在必须答对
  - `confirm` 若存在必须答对
  - `self-check = clear`

当前 `A` 类已经真实接进主链：

- 当复盘命中显式卡住信号后，调用 `POST /api/reviews/{review_id}/quiz/generate`
  - 不再继续生成 `main` quiz
  - 直接返回 `learning_status = remedy_available`
  - `next_state = remedy_available`
  - 前端应直接引导学生先回到卡住点，而不是继续做理解小测

当前 `self-check` 状态流已经收成：

- `clear`
  - 若解释层过线，且 `transfer_signal` 含明确触发信号，则进入 `confirm`
  - 否则直接 `resolved`
- `confused`
  - 进入 `remedy_available`
- `guessed`
  - 进入 `remedy_available`

当前 `confirm` 已接通：

- 固定池优先：先按 `problem_tags -> structure_type` 命中 `confirm_pool`
- LLM 兜底：固定池未命中时最多重试 2 次
- 若某个 `structure_type` 连续跳过累计达到 4 次，会自动标记为 `needs_backfill`
- `test_learning_routing_unit.py` 当前已明确断言：命中固定池时，返回的 `confirm` quiz 必须带 `meta.confirm_mode = fixed_pool`
- 当前固定池已实际导入 8 个结构类型种子题：
  - `difference_constraints`
  - `topological_sort`
  - `bipartite_graph`
  - `monotonic_queue`
  - `shortest_path`
  - `union_find`
  - `tree_dp`
  - `interval_dp`

当前 `remedy` 已收紧为：

- 必须带回学生原始 `bottleneck_text` 或当前 `main_block`
- 不再只输出泛化讲解
- 当前真实接口联调已确认：
  - `B` 类：`self-check = clear` 且解释层不过线时，会进入 `remedy_available`
  - `C` 类：解释层过线且固定池命中时，会返回 `confirm_quiz`
  - `A` 类：显式卡住信号存在时，`quiz/generate` 会直接短路到 `remedy_available`
  - `A -> remedy -> resolve` 这一整段接口链已经跑通
  - `C -> confirm answer -> resolved` 这一整段接口链已经跑通
  - 上面两段链路都已经补到从 `POST /api/checkins` 起步的更长接口链，不再只是从 `review_id` 中段开始测

### confirm_pool 数据准备产物

当前仓库已经有：

- `prepare_confirm_pool.py`
  - 读取 `latest.ndjson`
  - 输出 `total_rows / tag_type_counts / top_algo_tags / top_tag_pairs`
- `docs/subjects/noi/confirm_pool_tag_stats_v1.json`
  - 已基于真实 `latest.ndjson` 跑出第一轮标签统计
- `docs/subjects/noi/confirm_pool_mapping_v1.json`
  - 第一版 10 个 `structure_type` 草案
  - `bridge_note` 模板
  - 当前已经补上第一轮 `usable / defer` 与 `luogu_tags`
  - 当前保守策略是：直接能和真实细粒度标签对上的先 `usable`，过粗的先 `defer`
- `docs/subjects/noi/confirm_pool_seed_v1.json`
  - 第一批 8 个固定池种子题清单
- `seed_confirm_pool.py`
  - 支持 dry-run 和实际导入

以下能力已经有骨架，但还不算完全成熟：

### 1. `problem_analysis` 懒加载链路

已有：

- placeholder
- failed 状态
- retry_count
- 老师端失败列表和手动重试 API

但仍然是第一版，缺少：

- 更细的任务调度策略
- 批量/延迟重试策略
- 更完整的教师端可视化

### 2. `review_sessions.prompt_cache_hit`

字段已建表，能写入，但目前主要是骨架字段。

当前没有 provider 级真实 Prompt Caching 统计闭环，因此：

- 字段存在
- 但不应被当成“缓存系统已经真正上线”

### 2.1 review / quiz / problem_analysis 的消息结构

当前代码里已经完成：

- `_call_llm(...)` 不再接收单条字符串 prompt，而是接收 `messages`
- `generate_review(...)` 已改成 `system + user` 两条消息
- `generate_problem_analysis(...)` 已改成 `system + user` 两条消息
- 结构型 quiz 生成当前也已改成 `system + user` 两条消息

当前已新增单测：

- `test_review_engine_messages_unit.py`
  - 检查 review / problem_analysis / structural quiz 三条链都不再把 system 和 user 拼成一坨字符串

### 3. 同类题推荐

当前已经能用，但还是规则版：

- 只按 `algo_tags + difficulty`
- 还没有接 `focus / bridge_path / problem_bridge_labels`

### 4. 学生端视觉与信息层级

整体工作台结构已经成立。

当前已知现状包括：

- 文本溢出问题最近已收一轮
- 学生端当前已经把历史记录从 `打卡复盘` 页抽离到独立 `历史打卡` 标签
- 历史卡摘要、推荐方向说明等原先纯文本输出位，当前已统一接入 `.rich-text` + KaTeX hydration
- 视觉层级、阶段感、细节交互目前还不完全统一

---

## 九、已知但尚未彻底解决的边界问题

1. 某些 focus 当前仍会因为“结构题生成质量不稳”而 fallback，尤其是：
   - `general_modeling`
   - `constraint_modeling`
   - `greedy_basis`
   - `method_selection`

2. `review -> key_bridge / next_step` 在高风险 focus 上已经比上一轮更稳：
   - `A1`、`D2` 当前可稳定通过
   - `B1 / D1` 当前在新结构回归门下已完成一次真实 AI 联跑 `2/2` 通过
   - `B1` 这轮已补过一次 focus 检测顺序修正，避免并列约束题被 `general_modeling` 抢走
   - 当前 `B1 / D1` 的主要风险已从“固定词表误伤”收回到“真实输出表述仍会波动，但新结构门已能更稳地兜住”

3. `problem_analysis` 和 prompt/snippet 规则之间，目前仍依赖人工保持一致，没有自动冲突检查。

4. 学生端虽然已经按工作台重排，但老师端还没有完全统一到同一套布局语言。

5. `problem_context` 对洛谷题虽然已经明显弱化，但当前前端仍保留该输入入口。

6. 当前项目 still 依赖 Moonshot API 环境变量和本地运行环境。

7. “复盘提速 + 快反馈”当前已完成两组第一版落地：
   - 第一组：后台生成 + 前端轮询 + 单条状态接口 + retry
   - 第二组：`system/user` 分离
   - 当前仍未做全文 streaming

---

## 十、当前稳定可用的验证入口

### 基础测试

- `python3 -m py_compile api_server.py database.py review_engine.py problem_bank.py`
- `python3 -m unittest test_review_async_api_unit.py`
- `python3 -m unittest test_review_engine_messages_unit.py`
- `node --check static/app.js`
- `python3 test_problem_bank.py`
- `python3 test_review_api_flow.py`
- `python3 test_focus_detection.py`
- `python3 test_v1_2_flow.py`

### 页面联调

- 启动：`uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload`
- 页面：`/app`

当前人工联调最该重点看：

- 洛谷题导入
- 提交打卡后工作台右侧/中间联动
- `历史打卡` 标签点击后是否能回切到当前工作台
- 题干/选项/复盘/历史摘要里的 LaTeX 是否稳定渲染
- quiz 流转（main/followup/confirm/remedy）
- 长文本是否继续溢出
- 同类题推荐是否正常出现

### 真实联调补充

当前已经做过一轮真实接口联调验证：

- 在最新代码实例上，`POST /api/checkins` 已可在极短时间内直接返回 `review_status = pending`
- 后台 review 失败后，单条状态接口可读到 `failed`
- `POST /api/checkins/{checkin_id}/review/retry` 已可把失败记录重新切回 `pending`
- 前端轮询当前已不再优先读本地旧缓存，而会真实请求单条状态接口
- 单条状态接口返回的嵌套 `review` 当前已在前端摊平到现有工作区渲染字段

已知运行边界：

- 如果本地正在跑的 `uvicorn` 不是最新代码实例，旧进程不会自动吃到这轮改动
- startup 阶段的待生成复盘修复任务当前已改成后台线程，不再阻塞服务启动
- 当前真实 review 生成延迟仍偏长，最近一批 `review_sessions` 平均耗时约 48 秒，因此页面出现较长 `pending` 可能是后端真实仍在生成，而不一定是前端卡住
- 已确认一次真实故障边界：旧进程里模型调用可能长期挂住并把单条记录卡在 `pending`；重启到带 timeout 的实例后，该记录可继续推进到 `completed` 或 `failed`
- 在当前 `kimi-k2.5` 实例上，已真实观测到 `Request timed out.`；这时学生端会看到“复盘生成失败”，而不是无限停在 `pending`
- 已用真实服务复现 `P5536` 树直径卡点样例：打卡内容可通过校验并创建记录，但后台 review 生成在当前环境里可能出现两种不稳定表现：
  - 超时后进入 `failed`
  - 超过 50 秒仍停在 `pending`
- 已确认真实 `review_sessions` 存在超长生成：`checkin 254` 曾出现 `completion_tokens = 9663`、`latency_ms = 263682`；`checkin 260` 的未限流成功样例也有 `completion_tokens = 1620`、`latency_ms = 134507`
- `review_engine.py` 当前已给 `_call_llm()` 增加 `max_tokens` 上限；对 `P5536` 样例的直接烟雾验证里，`generate_review(...)` 耗时已降到约 `35.92s`
- 但当前 `1200` 上限会把部分复盘压成“信息不足”式保守输出，说明“限制输出长度”方向有效，但参数仍需继续校准
- `P5536` 这类“树直径公式来源”题还暴露出另一条质量边界：模型可能给出较准的 `diagnosis`，但 `core_design_subtags=["greedy_basis", ...]` 会把学生端字段拉回贪心模板；当前已增加“无贪心信号时不直接套 greedy_basis 模板”的保护
- review prompt 压缩 v1 当前已补 3 条输入保护，避免“压短后把关键信号裁没”：
  - 只有泛标签时不再回填 `O2优化 / NOIP / 模板` 这类标签
  - 代码裁剪不再只保留头尾，而会优先带上中段的关键公式/赋值行
  - `problem_card` 存在时，仍允许补一小段 `problem_context` 作为题目补充，避免证明/关系类细节被完全遮掉
- 已用真实 `P5536` 样例再次做压缩版 prompt 烟雾验证：
  - `generate_review(...)` 约 `37.82s` 返回成功，未超时
  - `prompt_tokens = 841`，`completion_tokens = 1200`
  - 但当前输出被压成 `error_layer = insufficient`、`error_layer_confidence = low`
  - 说明“压缩 prompt + 当前 1200 上限”已能保住可用性，但仍会把“知道直径、卡在公式证明”误判成信息不足
- 已进一步拆链验证：上述 `insufficient` 不是后处理 guard 拉回去，而是 `_call_llm()` 在 `completion_tokens = 1200` 时直接返回空字符串 `content=""`
- 已确认这条边界同样适用于评测链：若把 `max_tokens/max_completion_tokens` 压得过低，`kimi-k2.5` 会出现空输出、`invalid_json` 或直接错误；这类结果反映的是预算过低，不应当被当作 prompt 质量结论。
  - `_parse_review("")` 因此回落到默认 `insufficient + low`
  - `_guard_review_against_topic_drift(...)`、`_guard_review_for_insufficient(...)` 在这条样例上没有进一步改坏结果
  - 当前主风险已收敛为：`kimi-k2.5 + 压缩版 prompt + max_tokens=1200` 会出现“请求成功但正文为空”的输出阶段边界
- 已补双轨实验验证输出阶段边界：
  - `compressed prompt + max_tokens=1400`：约 `41.31s`，`prompt_tokens = 841`，`completion_tokens = 1400`，仍返回空字符串
  - `4 字段极简 prompt + max_tokens=1200`：约 `35.17s`，`prompt_tokens = 240`，`completion_tokens = 1200`，仍返回空字符串
  - 说明当前问题不只是“字段太多”或“1200 太紧”，而是 `kimi-k2.5` 在这类结构化 review 请求上存在“成功但空 content”的输出阶段异常
- 已按 Moonshot 官方文档收正 `_call_llm()` 的调用方式：
  - review 调用已改成 `response_format={"type":"json_object"}`
  - 已由 `max_tokens` 切到 `max_completion_tokens`
  - 对 `kimi-k2.5` 不再显式传 `temperature`
  - 已开始记录 `finish_reason`
- 改正后补了真实烟雾验证：
  - 极简 JSON 请求不再出现“成功但空正文”
  - 当前新的真实边界变成：`finish_reason = length`，`completion_tokens = 1200` 时会被明确判成截断失败
  - 说明“Moonshot 接法不规范”这条问题已收掉一部分，但 review 任务本身仍然会撞到输出上限
- 已继续对 `P5536` 样例做 `max_completion_tokens` 档位实测（在已对齐 Moonshot 文档的接法上）：
  - `1200`：约 `41.69s`，`prompt_tokens = 582`，`completion_tokens = 1200`，`finish_reason = length`
  - `1400`：约 `138.39s`，最终 `Request timed out.`
  - `1600`：约 `83.19s`，`completion_tokens = 1600`，`finish_reason = length`
  - `1800`：约 `87.44s`，`completion_tokens = 1800`，`finish_reason = length`
  - 当前没有出现“略微提高上限就自然恢复可用正文”的稳定窗口
- 已单独验证 timeout 语义：
  - 将 `LLM_REQUEST_TIMEOUT_SECONDS` 压到 `5` 后，同样的 review 请求会在约 `19.5s` 后报 `Request timed out.`
  - 说明当前 SDK 调用里的 `timeout` 不是严格硬上限，不能把它当作“到了 N 秒一定会立刻中断”的保护
- review 主链当前已改为 `stream=true` 按 chunk 收集正文，并对空正文/超时/截断增加一次定向重试
- 但真实 `P5536` 默认样例在新链路下仍未恢复可用正文：
  - 第一次流式请求先落到 `finish_reason = length`
  - 一次重试后仍失败，整次调用约 `83.78s`
  - 说明“stream + 单次重试”本身还不足以把当前 Kimi review 主链救活
- 当前 `NOI_REVIEW_MAX_TOKENS` 的代码默认值已从 `1200` 调回 `32768`
- 这一步的含义是：不再默认用一个极保守上限人为截断 review；但是否稳定、是否会重新拉长耗时，仍需要新的真实样例验证
- 已补真实默认链路验证：当前代码默认 `32768` 下，`P5536` 样例在约 `80.04s` 后恢复出了实体正文，`finish_reason = stop`
- 当前新边界是：
  - 默认上限 `32768` 已足以让这条样例不再被 `length` 截断
  - 但代价是单次 review 耗时明显变长
  - 当前流式调用下这次未拿到 `usage`，所以 `prompt_tokens/completion_tokens` 记为 `0`
- `shared_prefix_merging` 当前已细分出两类学生语境：
  - 公共前缀先合在一起、查询时只沿当前前缀路径走
  - trie 节点的经过次数/结束次数到底在记录什么
- 当 `P2922` 这类样例明确提到：
  - `经过次数`
  - `结束次数`
  - `节点该存什么`
  运行时的知识卡、知识卡后确认题、deterministic remedy 都会切到“节点计数语义”版本，不再只讲泛化的公共前缀合并
- 最新 live 样例已验证：
  - `review_id=4190`
  - 主轮 quiz、follow-up、remedy、knowledge_bailout
    都已经能走到“经过次数 / 结束次数 / 101-100-11”这版小课
  - `review_id=4932`
    - `P2249` fresh live 首轮已稳定围着：
      - `a[mid] == x`
      - `mid 先保留为候选`
      - `继续向左缩`
  - `review_id=4935`
    - `P2678` fresh live 已确认：
      - 首轮 review
      - main
      - follow-up
      - remedy
      都围着 `check_condition`
  - `review_id=4936`
    - `P2922` fresh live 已确认：
      - 首轮 review
      - main
      - follow-up
      - remedy
      都围着 `shared_prefix_merging`
      - 并已稳定出现：
        - `经过次数`
        - `结束次数`
        - `101 / 100 / 11`
- 2026-04-10 阶段一收口结论：
  - `method_selection`
  - `lazy_semantics`
  - `check_condition`
  - `shared_prefix_merging`
  这 4 条原先最弱的高频链，当前都已经有可工作的真实链路或当前代码路径验证。
  - `P2922`：首轮 review 漂移、节点计数语义、知识卡图示都已收顺。
  - `P3372`：`lazy` 语义链已稳定围绕“欠给孩子的信息”展开。
  - `P2678`：`check(mid)` 语义主轮已稳定落到 `check_condition`，旧 follow-up 噪音不再作为当前表现依据。
  - `P2249`：`left_bound_update` 已比旧的 `check_condition` 更贴学生卡点。
- 2026-04-10 又补了一层 trie 节点计数的 topic drift 纠偏：
  - 如果首轮 review 因为 `state`、`数量` 这类词被带偏
  - 但源文本已经明确是 `经过次数 / 结束次数 / 当前前缀节点`
  - `_guard_review_against_topic_drift(...)` 会直接短路拉回 `shared_prefix_merging`
  - 不再让后面的实现调试兜底把它覆盖掉
- 旧 `P2922` 历史噪音已做数据库标记：
  - `legacy_bridge_noise`
  - `exclude_from_current_bridge_audit`
  后续桥级审查时，默认不再把这些旧样例当成当前系统现状
- 第五阶段的首轮 bridge guard 已完成 live 复核：
  - `P2249`
  - `P2678`
  - `P2922`
  这 3 条 fresh 样例都已证明：
  - 首轮不会判错桥
  - 首轮文案也不会退回泛化话术
- 2026-04-11 学生端填写习惯已做一轮前端收边：
  - `ChatPage.vue` 已去掉学生可见的 `sessionId` 输入，只保留题号/题目链接 + 问题描述
  - `CheckinPage.vue` 已改成：
    - 主输入：题目、我卡在哪里、我已经试过什么
    - 可选补充：完成状态、提交结果、题面背景、卡点标签、相关代码
  - `ArchiveDetailPage.vue` 已弱化系统内部字段：
    - 去掉 `复盘模式 / 复盘家族 / 学习状态` 作为主摘要
    - 改成学生视角字段，如 `这次我卡在哪里 / 我已经试过什么 / 系统是怎么一步步带我过桥的`
  - 新增 `test_student_entry_ui.mjs`，用于钉住这三条学生端文案与结构约束
- 2026-04-12 已完成一轮真实浏览器学生路径走查：
  - 登录页 `账号 / 密码` label 已和输入框绑定，真实浏览器可通过 label 稳定填写
  - `CheckinPage.vue` 的主输入三项也已补 `id/for`，真实浏览器可按：
    - `题目链接 / 题号`
    - `我卡在哪里`
    - `我已经试过什么`
    定位输入框
  - 前端提交契约已对齐后端：
    - `submission_result` 默认规范为 `not_submitted`
    - 学生不选卡点标签时，`error_types` 默认补 `未说明`
    - 后端 422 数组错误不再显示成 `[object Object]`
  - 后端打卡校验现在会把 `bottleneck_text + reflection` 合起来看具体性：
    - 学生已在“我已经试过什么”里补充具体尝试时，不会因为卡点字段短而被误拒
  - Fresh browser walkthrough 已通过：
    - 登录 `student_a`
    - 进入 `打卡复盘`
    - 只填写主输入三项提交 `P2249`
    - 自动进入 `/app/archive/5567`
    - 返回历史列表
    - 再点 `继续看这次复盘`
    - 保持详情页，不再跳回 `/app/workspace/chat`
  - 2026-04-12 又完成移动端历史页收边：
    - `ArchiveListPage.vue` 和 `ArchiveDetailPage.vue` 已补 `min-w-0 / break-words`，长题目、长链接、长题面不会在 375px 宽度撑出横向滚动
    - 历史详情在 review pending 时会显示：
      - `系统正在整理复盘`
      - `刷新详情`
    - Fresh mobile walkthrough 已在 375px 宽度确认：
      - 历史列表无横向溢出
      - 历史详情无横向溢出
      - pending 提示和刷新按钮可见
- 2026-04-12 教师端 Vue 工作台完成一轮正式产品化收边：
  - `TeacherOverviewPage.vue` 已去掉原始 JSON 调试块，改成高频知识桥、知识域、知识子域、知识卡介入的可读排行卡
  - `TeacherReviewPage.vue` 已去掉样例原始 JSON，改成学生卡点、知识桥、系统建议、错误层级、掌握状态等复核摘要
  - `TeacherStudentsPage.vue` 已把主标题稳定为 `学生维度`，并把学生标记改成关注卡片
  - `TeacherCheckinsPage.vue` 已补 `暂无打卡记录` 空状态
  - 新增 `test_teacher_vue_ui.mjs` 并纳入 `run_test.sh`，防止教师端主 UI 再暴露 `<pre>` / `JSON.stringify`
  - Fresh browser walkthrough 已通过：
    - 登录 `teacher`
    - `/app/teacher/overview`
    - `/app/teacher/review`
    - `/app/teacher/students`
    - `/app/teacher/checkins`
    - 四页标题稳定，正文不再暴露调试 JSON，桌面宽度无横向溢出
  - 最新完整回归已通过：
    - `bash run_test.sh`
    - 后端 `197` tests
    - 学习流 `4` tests
    - 前端 Node `83` tests
    - `npm run build`
- 2026-04-12 旧静态前端运行时代码退场审查已开始：
  - 当前运行时入口仍只加载：
    - `/static/dist/assets/app.css`
    - `/static/dist/assets/app.js`
  - `static/index.html` 不再加载旧 `static/app.js`、`static/js/main.js`、`static/js/router.js`
  - 已新增 `static/teacher_stats_ui.js`，把教师统计/复核筛选相关纯 helper 从旧大运行时测试依赖中先切出一块
  - `test_teacher_stats_ui.mjs` 中教师统计相关断言已改为直接 import `static/teacher_stats_ui.js`
  - `run_test.sh` 已把 `static/teacher_stats_ui.js` 纳入前端语法检查
  - 当前旧 `static/app.js` 仍有测试依赖：
    - 主要集中在 quiz、visual_hint、knowledge bailout 等旧纯渲染 helper
    - 暂不删除，下一步应继续按 helper 维度拆出，而不是整文件硬删
- 2026-04-12 打卡复盘题目来源自动识别已接入：
  - 学生端仍不恢复 OJ 下拉框，保持“直接贴题号/链接”的填写习惯
  - `normalizeCheckinPayload(...)` 会根据 `problem_url` 自动推断：
    - `Pxxxx` / 洛谷链接 -> `luogu`
    - `codeforces.com` -> `codeforces`
    - `atcoder.jp` -> `atcoder`
    - 其他链接或空值 -> `other`
  - `CheckinPage.vue` 已在题目输入下提示：
    - 洛谷题号/链接可自动读取
    - 其他平台请补题目标题和题面
  - 后端 `create_checkin_endpoint(...)` 也会再次推断来源：
    - 防止旧客户端把 Codeforces / AtCoder 链接误写成 `luogu`
    - 非洛谷链接不再触发 `fetch_luogu_problem(...)`
  - 当前约束：
    - 只有洛谷支持自动读取题面
    - Codeforces / AtCoder / other 需要学生手动补题目标题和至少 10 个字的题面 / Markdown
  - 最新完整回归已通过：
    - `bash run_test.sh`
    - 后端 `198` tests
    - 前端 Node `84` tests
- 2026-04-12 前端过期 token 处理已收口：
  - API 层收到 `401` 时不再把后端 `Invalid or expired token` 原样展示给学生
  - `formatApiErrorDetail(..., 401)` 统一返回：
    - `登录已过期，请重新登录`
  - Vue 启动时会注册统一 unauthorized handler：
    - 记录当前路径为 pending path
    - 清空 auth store 和 localStorage token
    - 当前 shell 自动回到登录态
  - 新增测试覆盖：
    - 401 文案本地化
    - API 请求触发 unauthorized handler
  - 最新完整回归已通过：
    - `bash run_test.sh`
    - 后端 `198` tests
    - 前端 Node `86` tests
