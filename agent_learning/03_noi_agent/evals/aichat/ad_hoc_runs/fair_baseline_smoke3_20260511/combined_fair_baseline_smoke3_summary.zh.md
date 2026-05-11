# Bridge 离线评测摘要

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 12 |
| 完成数 | 12 |
| 错误数 | 0 |
| 学生状态准确率 | 0.833 |
| 桥梁大类准确率 | 1.000 |
| 知识焦点准确率 | 1.000 |
| 已注册知识焦点准确率 | 1.000 |
| 未知焦点召回率 | n/a |
| 求助类型准确率 | 0.667 |
| 帮助强度准确率 | 0.917 |
| 泄露率 | 0.083 |
| 关键桥梁泄露率 | 0.000 |
| 答案/代码泄露率 | 0.000 |
| 重写率 | 0.083 |
| 阻断率 | 0.000 |
| 修复率 | 0.083 |
| 无效标签率 | 0.000 |
| 焦点越界率 | 0.000 |
| 自相矛盾率 | 0.000 |
| 平均 Prompt Token 估计 | 481.417 |
| 平均 LLM 调用次数 | 2.750 |
| Bridge Judge 平均置信度 | 0.922 |
| 总延迟 P50 ms | 14143.832 |
| 总延迟 P95 ms | 34648.289 |

## 泄露等级分布

```json
{
  "0": 11,
  "2": 1
}
```

## 安全动作分布

```json
{
  "pass": 11,
  "rewrite": 1
}
```

## 阶段错误

```json
{}
```

## 分组结果

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 3 |
| 完成数 | 3 |
| 桥梁大类准确率 | 1.000 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 3.667 |
| 总延迟 P50 ms | 19798.445 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 3 |
| 完成数 | 3 |
| 桥梁大类准确率 | 1.000 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 3.333 |
| 总延迟 P50 ms | 16949.876 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 3 |
| 完成数 | 3 |
| 桥梁大类准确率 | 1.000 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 2.000 |
| 总延迟 P50 ms | 10843.644 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 3 |
| 完成数 | 3 |
| 桥梁大类准确率 | 1.000 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 2.000 |
| 总延迟 P50 ms | 12932.248 |
