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

## 维护原则
- 优先看学生自然语言，不要只看理论术语
- 每加一个新触发词，最好带一条例子
