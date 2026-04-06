目标：
围绕同一座桥，生成一题“结构型小题”，帮助学生在具体情境里判断定义、关系、条件、顺序或理由是否正确。

学生原题上下文：
- 题目：{{problem_title}}
- 题意补充：{{problem_context}}
- 学生卡点：{{bottleneck_text}}
- 当前主错误层：{{error_layer}}
- 当前关键桥梁：{{key_bridge}}
- 当前下一步：{{next_step}}
- 当前设计子类型：{{core_design_subtags}}
- 当前要验证的 focus：{{focus}}
- 当前算法大类：{{algorithm_category}}
- 目标桥梁：{{target_bridge}}
- 上一题 quiz：{{previous_question}}
- 上一题正确答案：{{previous_correct_answer}}
- 当前题目层级：{{difficulty_level}}

输出要求：
- 只围绕同一座桥出题，不能换主题
- 题目必须短、白话、对初中生友好
- 错误选项必须像学生真实会犯的错，不能出现搞笑选项
- 不能重复上一题问法
- 如果当前桥梁不适合稳定生成结构型小题，请输出：
  - `mode`: `fallback_explain`
  - `fallback_explain`: 一句说明为什么当前这一步更适合先讲清，而不是继续出题
  - 不要硬出题

meta 要求：
- `difficulty_level` 必须输出 `{{difficulty_level}}`
- `focus` 必须输出 `{{focus}}`
- `algorithm_category` 必须输出 `{{algorithm_category}}`
- 如果当前是 confirm quiz，且确实生成了题目，则 `confirm_mode` 输出 `structure`

额外输出要求：
- `options` 必须输出为对象数组，格式是 `{ "value": "A", "label": "..." }`
- 每个错误选项都要在 `distractor_feedback` 里给出一条对应说明
