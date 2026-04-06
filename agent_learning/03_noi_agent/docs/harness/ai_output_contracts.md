# AI 输出契约（review / quiz / problem_card）

## 本文件的写入标准

只写 AI 生成链路里的稳定契约：

- review 输出结构
- quiz 输出结构
- problem_card 的 compact / full 差异
- token 裁剪原则
- strategy_type 受控词表

不要写：

- 当前某个题目的特例
- 某次 prompt 调参结果
- 某次实验现象

如果本文件与 `prompts/` 目录下的 prompt 文件冲突：

- 运行时以 prompt 文件的实际行为为准
- 但本轮结束前必须同步两者，避免长期出现两套权威来源

---

## 一、review 输出契约

当前 review 的稳定结构包括：

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

### review 字段职责

#### 面向老师 / 结构判断

- `error_tags`
- `error_layer`
- `error_layer_confidence`
- `core_design_subtags`
- `diagnosis`
- `next_action`
- `suggested_topic`

#### 面向学生 / 纠偏引导

- `main_block`
- `key_bridge`
- `next_step`
- `transfer_signal`

### review 额外质量字段

- `review_quality_flags`

当前已有质量标记示例：

- `algorithm_name_leaked`

---

## 二、quiz 输出契约

当前结构型 quiz 采用单次生成、统一 JSON 输出。

### quiz 基本字段

- `mode`
- `quiz_type`
- `question_text`
- `options`
- `correct_answer`
- `answer_type`
- `distractor_feedback`
- `explanation`
- `bridge_feedback`
- `target_bridge`
- `difficulty_level`
- `meta`

### fallback 字段

当当前桥梁不适合稳定出题时，不强出坏题，改为：

- `mode = fallback_explain`
- `fallback_explain`
- `difficulty_level`
- `meta`

### 当前规则

1. `quiz_type` 当前主线只允许结构型 `choice`
2. judgement（对/错）题不再作为主线题型
3. `options` 使用对象数组：
   - `{ "value": "A", "label": "..." }`
4. `correct_answer` 必须是某个 option 的 `value`

---

## 三、answer_type 约束

`answer_type` 只能是：

- `structural_fact`
- `learning_advice`

### 含义

#### `structural_fact`

表示正确答案本质上是：

- 具体定义
- 具体关系
- 具体条件
- 具体顺序
- 具体维护量
- 具体代价 / 价值 / 状态含义

#### `learning_advice`

表示正确答案本质上只是：

- 学习建议
- 思维态度
- 方法口号
- 泛化流程

### 规则

如果模型产出的正确答案属于 `learning_advice`：

- 这道题不应出给学生
- 应退回 `fallback_explain`

---

## 四、bridge_feedback / distractor_feedback

### `bridge_feedback`

用于学生答对后显示：

- 你刚才真正答对的是哪一步
- 这一步与原题卡点的关系

### `distractor_feedback`

用于学生答错后显示：

- 你选的这个错误选项具体错在哪个结构

### 规则

1. 每个错误选项都必须有对应 `distractor_feedback`
2. 不能写成：
   - 这个选项不对
   - 这个写法错误
3. 必须指出具体结构错误

---

## 五、main / followup / confirm 规则

### `main`

- 在原题语境里测当前桥梁的最小结构事实
- 禁止“第一步该怎么做”类口号题

### `followup`

- 仍然用原题语境
- 但比 main 更小、更单步
- 不能退回元认知题

### `confirm`

- 目标不是更简单，而是换角度验证同一座桥
- 新情境必须与原桥梁结构直接对应
- 不能只是同类算法的另一道题

---

## 六、problem_card 契约

当前复盘使用两级题目卡：

### 1. `compact_card`

不经过 LLM，由本地题面直接裁剪。

字段：

- `title`
- `algo_tags`
- `description_compact`
- `input_compact`
- `output_compact`
- `range_compact`
- `time_limit_ms`

### 2. `full_card`

依赖 `problem_analysis.status = completed`。

字段：

- `title`
- `algo_tags`
- `summary`
- `input_compact`
- `output_compact`
- `range_compact`
- `time_limit_ms`
- `strategy_types`
- `knowledge_points`
- `common_mistakes`

### 使用规则

- 有 `full_card` 时，优先使用 `full_card`
- 否则使用 `compact_card`

---

## 七、problem_analysis 输出契约

`problem_analysis` 当前稳定字段包括：

- `summary`
- `strategy_types`
- `knowledge_points`
- `common_mistakes`
- `analysis_version`
- `status`
- `last_error`
- `retry_count`

### 生成策略

- 懒加载
- 不做全量预生成

### 状态

- `pending`
- `completed`
- `failed`

---

## 八、strategy_type 受控词表

`strategy_types` 只能从以下词表中选，最多 2 个，不能自造新词。

### 边界

`strategy_type` 是题目主策略的受控词表，不是所有实现技巧的完整枚举。

例如：

- “倒序扫描”
- “滚动数组”

这类更适合放进：

- `knowledge_points`

而不是强行放进 `strategy_types`。

### 当前词表

- `simulation`
- `greedy`
- `binary_search`
- `two_pointer`
- `prefix_diff`
- `sort`
- `divide_conquer`
- `monotone_structure`
- `stack_queue`
- `heap`
- `dsu`
- `bit`
- `segment_tree`
- `hash`
- `trie`
- `linked_list`
- `dp_linear`
- `dp_knapsack`
- `dp_interval`
- `dp_tree`
- `dp_bitmask`
- `dp_digit`
- `graph_traversal`
- `graph_shortest`
- `graph_mst`
- `graph_toposort`
- `graph_constraint`
- `graph_bipartite`
- `graph_scc`
- `tree_lca`
- `tree_hld`
- `math_number`
- `math_combinatorics`
- `math_fast_power`
- `math_game`
- `string_kmp`
- `string_hash`
- `composite`
- `other`

---

## 九、token 裁剪规则

当前复盘 prompt 应按三层理解：

### 诊断权重

1. 学生本次信号：最高
2. 题目结构化卡：中
3. 系统规则 / schema：低

### prompt 位置

1. 系统规则 / schema：最前
2. 题目卡：中间
3. 学生本次信号：最后

### 题目上下文裁剪规则

#### 必传

- `title`
- `algo_tags`（最多 3 个，只取 `algo`）
- `summary` 或 `description_compact`
- `input_compact`
- `output_compact`
- `range_compact`
- `time_limit_ms`

#### 仅完整卡附加

- `strategy_types`
- `knowledge_points`
- `common_mistakes`

#### 不传

- 完整题面全文
- 全部样例
- `hint` 全文
- 图片链接
- `contest / year / other` 标签
- `translations`
- `background`
- `limits_json` 原始数组

---

## 十、当前 prompt 文件中的直接约束

当前 `prompts/` 目录已经明确约束了以下事项：

1. 结构型 quiz 必须输出 JSON
2. `answer_type` 必须输出并自检
3. 元认知 / 方法态度题不合格
4. `main / followup / confirm` 各自有角色边界
5. `confirm` 的新情境必须验证同一座桥

因此，本文件必须与以下 prompt 文件保持一致：

- `prompts/snippets/json-output-rules.md`
- `prompts/snippets/structural-quiz-rules.md`
- `prompts/snippets/role-main.md`
- `prompts/snippets/role-followup.md`
- `prompts/snippets/role-confirm.md`
- 以及相关 focus snippets

