# Bridge 离线评测摘要

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 100 |
| 完成数 | 100 |
| 错误数 | 0 |
| 学生状态准确率 | 0.650 |
| 桥梁大类准确率 | 0.900 |
| 知识焦点准确率 | 0.812 |
| 已注册知识焦点准确率 | 0.812 |
| 未知焦点召回率 | n/a |
| 求助类型准确率 | 0.583 |
| 帮助强度准确率 | 0.912 |
| 泄露率 | 0.100 |
| 关键桥梁泄露率 | 0.000 |
| 答案/代码泄露率 | 0.000 |
| 重写率 | 0.025 |
| 阻断率 | 0.000 |
| 修复率 | 0.000 |
| 无效标签率 | 0.000 |
| 焦点越界率 | 0.000 |
| 自相矛盾率 | 0.000 |
| 平均 Prompt Token 估计 | 405.030 |
| 平均 LLM 调用次数 | 2.160 |
| Bridge Judge 平均置信度 | 0.897 |
| 总延迟 P50 ms | 13497.609 |
| 总延迟 P95 ms | 22471.240 |

## 泄露等级分布

```json
{
  "0": 34,
  "1": 3,
  "2": 1,
  "unknown": 2
}
```

## 安全动作分布

```json
{
  "pass": 37,
  "rewrite": 1,
  "unknown": 2
}
```

## 阶段错误

```json
{
  "leakage_judge": 2
}
```

## 分组结果

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 2.100 |
| 总延迟 P50 ms | 13691.467 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 3.350 |
| 总延迟 P50 ms | 17094.474 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 3.350 |
| 总延迟 P50 ms | 18157.722 |

### tutor_mode=current_system|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 7631.893 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 7159.394 |

