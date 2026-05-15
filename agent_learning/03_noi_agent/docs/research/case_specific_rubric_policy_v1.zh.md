# Case-specific Rubric Policy v1

本政策规定每个 case 必须携带的样本专属评价字段。目的不是让教练机械照表打分，而是减少“凭感觉猜这条回复好不好”的主观性。

## 必填字段

每个 response-review case 应尽量包含：

| 字段 | 作用 |
| --- | --- |
| `success_criteria` | 好回复至少要让学生能推进到什么程度 |
| `forbidden_content` | 本轮不能直接补完的内容 |
| `critical_bridge_boundary` | 哪些内容一旦直接说出，就算 critical bridge leakage |
| `acceptable_reveal` | 哪些信息可以说，不应被过敏地判为泄露 |
| `expected_student_next_action` | 学生看完理想回复后应该做的下一步 |

## 编写原则

1. 字段必须服务于当前学生问题，不是完整题解。
2. 禁止内容应写成抽象桥梁边界，而不是只列某个算法模板。
3. `acceptable_reveal` 要明确说明哪些概念性解释、复述或局部确认是合理的。
4. `expected_student_next_action` 应符合最低足够学生努力：短而有认知价值。
5. 如果 case 信息不足，应标记低置信或 clarification/safety slice，不应硬塞进主实验。

## 示例

学生问题：

```text
线段树区间加我会写一点，但 lazy 到底表示还没做什么，我说不清。
```

可用 rubric：

```json
{
  "success_criteria": [
    "学生能区分父节点 sum 已更新和子节点尚未下传的状态",
    "学生能说出 lazy 表示对孩子延迟执行的增量"
  ],
  "forbidden_content": [
    "不能直接给出完整 pushdown 代码",
    "不能直接把 lazy 的全部模板语义讲完"
  ],
  "critical_bridge_boundary": "如果回复直接说清 lazy 就是还没下传到子节点的增量，并完整解释父/子节点更新时机，则可能补完当前关键桥。",
  "acceptable_reveal": "可以让学生观察一次 [1,2] 节点打标后，叶子是否已经真的加上 5。",
  "expected_student_next_action": "学生判断子节点是否已更新，并用一句话解释。"
}
```

## 与泄露判断的关系

`critical_bridge_boundary` 不是为了让系统完全不解释知识，而是帮助教练判断：

```text
AI 是否在当前轮次替学生完成了本应由学生构造的关键关系。
```

如果学生已经说出关键关系，或者当前处于复盘总结、L3 强提示、调试确认等允许更强解释的场景，可以通过 `acceptable_reveal` 与 `bridge_reveal_justification` 标明。

## 质控

进入主实验前，应检查：

- 字段是否为空；
- 是否和题面、学生问题、近期对话一致；
- 是否存在把完整解法误写成 success criteria 的情况；
- 是否存在过细算法模板化标签；
- 是否能被外部教练理解。
