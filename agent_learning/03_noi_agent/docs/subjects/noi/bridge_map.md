# NOI 桥梁地图

这份文档记录 NOI 当前使用的桥梁（focus）与其教学用途。

## 现有 focus（Batch A）

| focus | error_layer | 说明 |
| --- | --- | --- |
| state_design | core_design | 状态定义、维度选择、状态含义 |
| transition_design | core_design | 转移是否完整、是否漏情况 |
| check_condition | core_design | check 在验证什么 |
| enumeration_order | core_design | 枚举/循环顺序为什么这样写 |
| greedy_basis | core_design | 贪心选择依据 |
| tree_path_difference | core_design | 树上多条路径贡献如何转成端点/LCA 差分标记，并用 DFS 汇总还原经过次数 |
| general_modeling | modeling | 对象与关系如何抽象成结构 |
| constraint_modeling | modeling | 约束如何转成结构关系 |
| boundary_debug | implementation | 边界、特判、下标/初始化相关错误 |
| method_selection | method | 根据题面特征选择方法 |

## 新增 focus（Batch B 第一批）

| focus | error_layer | 说明 |
| --- | --- | --- |
| data_type | implementation | int / long long / 精度 / 溢出 |
| loop_boundary | implementation | 循环起止、0/1 下标、范围越界 |
| recursion_structure | core_design | 递归 base case、递归拆分结构 |
| complexity_fit | method | 数据规模和复杂度是否匹配 |

## 预留 focus（后续再做）

| focus | 预期 error_layer | 备注 |
| --- | --- | --- |
| tree_property | modeling | 容易滑成概念题，需谨慎 |
| graph_traverse | method | 容易和 method_selection 重叠 |
| stl_selection | method | 容易退化成 API 记忆题 |

## 使用提醒
- 新增 focus 前，先判断是不是“学生高频卡点”
- 优先做能稳定出结构型小题的 focus
- 不要为了凑完整性，把 API 记忆题硬塞进桥梁体系
