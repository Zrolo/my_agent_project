# 高频 Bridge 样例池（2026-04）

这份样例池服务阶段二：

- 固定 8 个高频 bridge 的代表样例
- 每个 bridge 至少保留：
  - 1 条代表好样例
  - 1 条历史噪音/坏样例
  - 1 条修复后样例（如果已有）

后续 bridge 审查、teacher 统计复核、真实链路回归，都优先从这里选样例，不再临时翻全库。

---

## 1. `state_design`

- 代表好样例：
  - `P1434 滑雪`
  - `checkin_id=3126`
  - `review_id=3025`
- 历史噪音：
  - 旧库里大量 `not_started` 历史，不作为当前主链路判断依据
- 修复后样例：
  - 当前代码路径已稳定，以 `3025` 为代表

## 2. `transition_design`

- 代表好样例：
  - `P1216 数字三角形`
  - `checkin_id=1720`
  - `review_id=1699`
- 历史噪音：
  - 暂无明显噪音主样例
- 修复后样例：
  - 当前 deterministic remedy + 外部 snippet 已接通，`1699` 可继续作为主代表

## 3. `check_condition`

- 代表好样例：
  - `P2678 跳石头`
  - `checkin_id=5121`
  - `review_id=4935`
- 历史噪音：
  - `checkin_id=4083`
  - `review_id=3940`
  - 主轮 quiz 曾误落到 `complexity_fit`
- 修复后样例：
  - `checkin_id=4225`
  - `review_id=4073`
  - 当前 fresh live 已确认：
    - 首轮 review
    - main
    - follow-up
    - remedy
    全链都稳定围着 `check_condition`

## 4. `left_bound_update`

- 代表好样例：
  - `P2249 查找`
  - `checkin_id=5120`
  - `review_id=4932`
- 历史噪音：
  - `checkin_id=3578`
  - `review_id=3465`
  - `focus/key_bridge` 为空
- 修复后样例：
  - `checkin_id=3518`
  - `review_id=3406`
  - fresh live 首轮已确认：
    - `a[mid] == x`
    - `mid 先保留为候选`
    - `继续向左缩`

## 5. `lazy_semantics`

- 代表好样例：
  - `P3372 线段树 1`
  - `checkin_id=4226`
  - `review_id=4074`
- 历史噪音：
  - 旧模板题 `P3372 【模板】线段树 1`
  - `checkin_id=3446`
  - `review_id=3336`
  - 可作参考，但优先级低于新样例
- 修复后样例：
  - `checkin_id=4084`
  - `review_id=3941`

## 6. `shared_prefix_merging`

- 代表好样例：
  - `P2922 [USACO08DEC] Secret Message G`
  - `checkin_id=5122`
  - `review_id=4936`
- 历史噪音：
  - `checkin_id=4342`
  - `review_id=4200`
  - 曾出现主轮 quiz 仍是旧的 `state_design` 脏记录
- 修复后样例：
  - `checkin_id=4701`
  - `review_id=4543`
  - fresh live 已确认：
    - 首轮 review
    - main
    - follow-up
    - remedy
    都走到“经过次数 / 结束次数 / 101-100-11”这版小课

## 7. `complexity_fit`

## 7A. `tree_path_difference`

- 代表好样例：
  - `P3128 [USACO15DEC] Max Flow P`
  - 当前代码试点样例，尚未绑定真实 checkin_id
- 扩样样例：
  - `P3258 [JLOI2014] 松鼠的新家`
  - 树上边经过次数统计题
- 历史噪音：
  - 之前 `P3128` 语境里的 `标记` 容易误进 `lazy_semantics`
  - `经过次数` 容易误进 `shared_prefix_merging`
- 修复后样例：
  - 当前本地测试已覆盖：
    - P3128 点经过次数
    - P3258 路线访问次数
    - 边经过次数边界样例
    - 线段树 lazy 反向保护线

## 8. `complexity_fit`

- 代表好样例：
  - `P2922 [USACO08DEC] Secret Message G`
  - `checkin_id=3377`
  - `review_id=3261`
- 历史噪音：
  - 与 `method_selection / shared_prefix_merging` 旧样例交织
- 修复后样例：
  - 当前代码路径稳定，继续以 `3261` 为代表

## 9. `method_selection`

- 代表好样例：
  - `P2922 [USACO08DEC] Secret Message G`
  - `checkin_id=3447`
  - `review_id=3337`
- 历史噪音：
  - 旧库里有重复 quiz 记录
- 修复后样例：
  - 当前代码路径已能把 trie 题的方法桥自然过渡到机制桥
  - 继续优先参考：
    - `checkin_id=5122`
    - `review_id=4936`
    - `checkin_id=4701`
    - `review_id=4543`

---

## 使用规则

- bridge 级评估时，优先看“代表好样例 + 修复后样例”
- 不再直接把全库里同题所有记录都混在一起看
- 带有旧噪音的记录，只作历史对照，不作当前系统表现判断
