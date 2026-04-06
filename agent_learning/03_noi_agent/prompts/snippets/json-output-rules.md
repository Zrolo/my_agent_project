JSON 输出规则：

Part 1：通用格式规则
- 输出纯 JSON，不要加 Markdown 代码块
- 不要加解释前缀或额外自然语言
- 确保输出内容可以被 `json.loads()` 直接解析

Part 2：当前结构型 quiz 必须输出的字段
- 必须输出以下字段，不能省略、不能改名：
  - 当 `mode` = `quiz` 时：
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
  - 当 `mode` = `fallback_explain` 时：
    - `mode`
    - `fallback_explain`
    - `difficulty_level`
    - `meta`
- `options` 必须是对象数组，格式为：`{ "value": "A", "label": "选项正文" }`
- `correct_answer` 必须等于某个 option 的 `value`
- `answer_type` 只能是：
  - `structural_fact`
  - `learning_advice`
- `distractor_feedback` 必须是对象，key 为错误选项的 `value`
- `fallback_explain` 必须是一句不少于 15 字的说明，解释为什么当前桥梁更适合先讲清，而不是继续出题
- `meta` 必须是对象
