# Bridge 审查总表（2026-04）

这份表只服务当前两周主线：

- 先盯 8 个高频 bridge
- 先看学生主链路是否真的像“小课”
- 先看：
  - 第一轮 review
  - deterministic remedy
  - knowledge bailout card

---

## 当前结论

| bridge | 代表题 | 当前判断 | 当前最明显问题 | 下一步 |
| --- | --- | --- | --- | --- |
| `state_design` | `P1434 滑雪` | 较稳 | 老历史里大多还停在 `not_started`，真实已完成样例少 | 继续补真实完成样例 |
| `transition_design` | `P1216 数字三角形` | 较稳 | 知识卡已顺，但真实新样例还少 | 再补 1 到 2 条真实复测 |
| `check_condition` | `P2678 跳石头` | 较稳 | 旧库里有修复前噪音，但现在已经有一条干净新链 | 以后评估优先看 `review_id=4073` |
| `left_bound_update` | `P2249 查找` | 较稳 | 库里存在 1 条 `focus/key_bridge` 为空的脏记录 | 标记旧噪音，不拿它当评估依据 |
| `lazy_semantics` | `P3372 线段树 1` | 较稳 | 真实链已顺，但 `visual_hint` 仍比文案更泛 | 继续精修图示，不急着改主链 |
| `shared_prefix_merging` | `P2922 Secret Message G` | 较稳 | 真实历史仍有旧噪音，评估时要和 `method_selection` 分开看 | 优先看 `review_id=4543 / 4190` 这类新链 |
| `tree_path_difference` | `P3128 / P3258` | 试点已扩样 | 点差分、路线访问次数已稳；边差分/纯 HLD 还未拆 variant | 继续找真实边差分题号并决定是否拆 variant |
| `complexity_fit` | `P2922 Secret Message G` | 较稳 | 真实库里和 `method_selection` 旧记录交织 | 标记旧样例噪音，继续补新样例 |
| `method_selection` | `P2922 Secret Message G` | 较稳 | 真实库里仍有旧 quiz 重复记录，且和 `shared_prefix_merging` 容易混评 | 新样例优先只看最新 review，并和机制桥分开审 |

---

## 已审代表样例

### `state_design`

- 代表题：
  - `P1434 滑雪`
- 代表记录：
  - `checkin_id=3126`
  - `review_id=3025`
- 当前运行时判断：
  - 知识卡和 remedy 都已经能稳定围绕：
    - `状态格记录的是哪个子问题结果`
- 当前结论：
  - 已经像一节小课

### `transition_design`

- 代表题：
  - `P1216 数字三角形`
- 代表记录：
  - `checkin_id=1720`
  - `review_id=1699`
  - `bridge_path=followup_remedy`
  - `mastery_status=assisted_success`
- 当前运行时判断：
  - remedy 会讲：
    - `先把当前状态可能从哪些更小状态转来想全`
  - 知识卡也继续围绕来源关系
- 当前结论：
  - 已经像一节小课

### `check_condition`

- 代表题：
  - `P2678 跳石头`
- 代表记录：
  - `checkin_id=4083`
  - `review_id=3940`
- 当前运行时判断：
  - remedy 会讲：
    - `check(mid)` 只判断当前 `mid` 可不可行
  - 知识卡会补：
    - `先单独判断可行性，再二分找边界`
  - 2026-04-10 已修掉一个真实误路由：
    - `error_layer=method` 但学生明确在问 `check(mid)` 语义时，主轮 quiz 不再错掉到 `complexity_fit`
- 当前问题：
  - `review_id=3940` 库里已经生成过一条修复前的错误主轮 quiz，不能再直接拿它当当前系统表现
- 当前结论：
  - 当前代码路径已顺
  - 当前应优先参考新的干净链：
    - `checkin_id=4225`
    - `review_id=4073`
    - `quiz_id=1150`（final micro confirm）
    - `quiz_id=1151`（knowledge confirm）
  - 这条干净链已真实走到：
    - `remedy_available -> remedy -> final_micro_confirm -> knowledge_bailout`
  - 修复前旧样例仍可作历史参考：
    - `checkin_id=4142`
    - `review_id=3994`
    - `quiz_id=1124`

### `left_bound_update`

- 代表题：
  - `P2249 查找`
- 代表记录：
  - `checkin_id=3518`
  - `review_id=3406`
- 当前运行时判断：
  - remedy 会讲：
    - `最左边那个满足条件的位置要保留 mid 作为候选`
  - 知识卡会继续补：
    - `不是问有没有，而是问最左边界在哪`
- 当前结论：
  - 已经比较稳

### `lazy_semantics`

- 代表题：
  - `P3372 线段树 1`
- 代表记录：
  - `checkin_id=4084`
  - `review_id=3941`
  - `quiz_id=1106`
- 当前运行时判断：
  - remedy 会讲：
    - `lazy 记录的是这段区间已经确定、但还没下传给孩子的信息`
  - 知识卡会继续补这层区间语义
- 当前结论：
  - 已经有干净新链可直接代表当前系统表现：
    - `checkin_id=4226`
    - `review_id=4074`
    - `quiz_id=1152`（final micro confirm）
    - `quiz_id=1153`（knowledge confirm）
  - 这条干净链也已真实走到：
    - `remedy_available -> remedy -> final_micro_confirm -> knowledge_bailout`
  - 2026-04-10 阶段三复审：
    - 当前 live 与运行时代码路径都能稳定给出：
      - `lazy` 是“这段区间已经确定、但还没下传给孩子的信息”
      - 最小算例：
        - `[1,4]`
        - `lazy=3`
        - `3×2`
    - `remedy / knowledge card / knowledge confirm` 都已经围着同一座桥讲
  - 当前结论更新为：
    - 这座桥已经较稳
    - 剩余问题更多是图示还可以继续精修，不是主链没跑顺

### `shared_prefix_merging`

- 代表题：
  - `P2922 Secret Message G`
- 代表记录：
  - `checkin_id=3374`
  - `review_id=3258`
- 当前运行时判断：
  - 机制桥本身已经能讲：
    - `相同开头先合在一起`
    - `查询时只沿前缀路径走`
- 2026-04-10 阶段三复审：
  - 以当前 live 样例：
    - `checkin_id=4701`
    - `review_id=4543`
    以及对照样例：
    - `checkin_id=4341`
    - `review_id=4190`
    来看，当前这座桥已经能稳定给出：
    - `review`
      - `pass_cnt / end_cnt` 对应的前缀关系
    - `remedy`
      - `经过次数`
      - `结束次数`
      - `101 / 100 / 11`
    - `knowledge card`
      - `前缀 10 这个节点`
      - `经过次数至少是 2`
      - `结束次数另算`
    - `knowledge confirm`
      - 明确确认“经过次数在说明什么”
- 当前问题：
  - 真实历史里仍常和 `method_selection / complexity_fit` 混在一起
  - 但这已经是旧噪音问题，不再是当前 live 主链问题
- 当前结论：
  - 这座桥当前已从“中等”提升到“较稳”
  - 当前系统里真正剩下的是评估隔离问题，不是学生链路内容问题

### `complexity_fit`

- 代表题：
  - `P2922 Secret Message G`
- 代表记录：
  - `checkin_id=3377`
  - `review_id=3261`
- 当前运行时判断：
  - remedy 会讲：
    - `先看输入规模`
    - `再估总操作量`
  - 知识卡会继续强调：
    - `先判断当前做法能不能过`
- 当前结论：
  - 已经比较稳

### `tree_path_difference`

- 代表题：
  - `P3128 [USACO15DEC] Max Flow P`
- 当前运行时判断：
  - focus 已新增为 `tree_path_difference`
  - `P3128` 的“经过次数 / 多条树上路径 / LCA / 树剖 / 差分标记”语境会优先进入这座桥
  - `P3258` 这类“路线 / 访问次数 / 公共祖先 / 向上汇总”的自然语言语境也会进入这座桥
  - 边经过次数语境已经被识别为这座桥的边界样例
  - 不再被 `lazy_semantics` 的“标记”或 `shared_prefix_merging` 的“经过次数”误吸走
  - main / followup / final micro confirm / knowledge card / knowledge confirm / remedy 都已有本地确定性链路
- 当前桥梁语言：
  - `一条树上路径贡献 -> 端点/LCA 附近差分标记 -> DFS 子树汇总 -> 每个点经过次数`
- 当前结论：
  - P3128 点经过次数版本已接通
  - P3258 路线访问次数自然语言触发已接通
  - 线段树 lazy 反向保护线仍然稳定
  - 树剖 LCA + 差分作为同一座桥处理，不把它讲成单纯“树剖模板”
- 当前风险：
  - 这张卡当前偏点差分
  - 边差分题、只问 HLD 区间维护的题，后续可能需要拆成 variant

### `method_selection`

- 代表题：
  - `P2922 Secret Message G`
- 代表记录：
  - `checkin_id=3447`
  - `review_id=3337`
- 当前运行时判断：
  - remedy 会讲：
    - `很多字符串`
    - `反复前缀关系`
    - `相同开头能不能先合在一起看`
  - 知识卡会继续往 `shared_prefix_merging` 过渡
- 2026-04-10 阶段三复审：
  - 以当前 live 输入语境重新拉链后，`method_selection` 现在已经能稳定给出：
    - `bridge_explanation`
      - 先破“凭题感猜 trie”的误解
    - `algorithm_overview`
      - 明确点出：
        - `很多字符串`
        - `反复前缀关系`
        - `101 / 100 / 11`
    - `remedy`
      - 明确要求学生先指出支持 trie 的题面信号
    - `knowledge confirm`
      - 不再只考“是不是 trie”，而是考“很多相同开头值不值得先合在一起看”
- 当前结论：
  - 当前代码路径下，这座桥已经从“中等偏稳”提升到“较稳”
  - 剩余问题不是讲不清，而是：
    - 真实库里仍有旧 quiz 重复记录
    - 容易和 `shared_prefix_merging` 混在一起被一起评

---

## 旧历史噪音

这些记录当前不要再当“系统现状”直接评估依据：

### `P2922`

- 同题里同时混有：
  - `complexity_fit`
  - `method_selection`
  - `shared_prefix_merging`
- 还存在历史上重复生成的 quiz 记录，例如：
  - `review_id=3337`
  - `review_id=3264`
- 解释：
  - 这些记录跨越了多个旧版本，不代表当前运行时唯一行为
- 当前已做数据库标记：
  - 旧 `P2922` 噪音样例已统一追加
    - `legacy_bridge_noise`
    - `exclude_from_current_bridge_audit`
  - 当前优先看的新链路是：
    - `review_id=4190`
    - `review_id=4200`
  - 其中 `4190` 已在 live 服务里确认：
    - 主轮 `shared_prefix_merging`
    - follow-up
    - remedy
    - knowledge_bailout`
    全链都能跑到“经过次数 / 结束次数 / 101-100-11”这版小课

### `P2249`

- 存在一条空 focus 脏记录：
  - `checkin_id=3578`
  - `review_id=3465`
- 解释：
  - 当前评估应优先参考：
    - `review_id=4932`
    - `review_id=3406`
    - `review_id=3351`
    - 这类有明确 `left_bound_update` 语义的记录

- 最新 fresh live 已确认：
  - `checkin_id=5120`
  - `review_id=4932`
  - 首轮 review 已稳定围绕：
    - `a[mid] == x`
    - `mid 先保留为候选`
    - `继续向左缩`

---

## 当前这轮 fresh live 复核结果

这轮已经补完并复核：

1. `P2678 跳石头`
   - 对应 bridge：
     - `check_condition`
   - 当前 fresh live：
     - `checkin_id=5121`
     - `review_id=4935`
   - 已确认：
     - 首轮 review
     - main
     - follow-up
     - remedy
     都围着 `check_condition`

2. `P2922 Secret Message G`
   - 对应 bridge：
     - `shared_prefix_merging`
   - 当前 fresh live：
     - `checkin_id=5122`
     - `review_id=4936`
   - 已确认：
     - 首轮 review
     - main
     - follow-up
     - remedy
     都围着“经过次数 / 结束次数 / 101-100-11”

---

## 当前最该继续修的桥

按优先级：

1. `method_selection`
2. `shared_prefix_merging`
3. `complexity_fit`

原因：
- 它们在 `P2922` 这类题里最容易互相缠住
- 真实历史噪音也最多
- 但 fresh live 现在已经证明：
  - `P2249`
  - `P2678`
  - `P2922`
 这 3 条代表链路都能稳定落在当前目标 bridge 上
