# NOI Focus 分类与触发线索

这份文档记录 focus 的典型触发词和识别线索，供后续规则和 prompt 调整时参考。

## data_type
- 典型词：
  - `long long`
  - `溢出`
  - `精度`
  - `1e18`
  - `10^18`

## loop_boundary
- 典型词：
  - `0-indexed`
  - `1-indexed`
  - `下标`
  - `越界`
  - `循环范围`

## recursion_structure
- 典型词：
  - `递归`
  - `base case`
  - `什么时候停`
  - `分治`

## complexity_fit
- 典型词：
  - `复杂度`
  - `TLE`
  - `n <=`
  - `O(n^2)`
  - `能不能过`

## tree_path_difference
- 典型词：
  - `树上差分`
  - `多条路径`
  - `经过次数`
  - `访问次数`
  - `路线`
  - `每段路`
  - `路径加一`
  - `LCA`
  - `公共祖先`
  - `最近公共祖先`
  - `树剖`
  - `树链剖分`
  - `端点打标记`
  - `DFS 汇总`
- 代表题：
  - `P3128 [USACO15DEC] Max Flow P`
  - `P3258 [JLOI2014] 松鼠的新家`
- 识别提醒：
  - `经过次数` 在 trie 题里也会出现，但如果同时有树、路径、LCA、差分或树剖信号，应优先进入 `tree_path_difference`
  - `标记` 在 lazy 题里也会出现，但如果语境是树上路径贡献，不应误路由到 `lazy_semantics`

## 维护原则
- 优先看学生自然语言，不要只看理论术语
- 每加一个新触发词，最好带一条例子
