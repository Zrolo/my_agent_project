# Bridge 离线评测摘要

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 140 |
| 完成数 | 140 |
| 错误数 | 0 |
| 学生状态准确率 | 0.567 |
| 桥梁大类准确率 | 0.900 |
| 知识焦点准确率 | 0.800 |
| 已注册知识焦点准确率 | 0.800 |
| 未知焦点召回率 | n/a |
| 求助类型准确率 | 0.533 |
| 帮助强度准确率 | 0.908 |
| 泄露率 | 0.100 |
| 关键桥梁泄露率 | 0.037 |
| 答案/代码泄露率 | 0.000 |
| 重写率 | 0.100 |
| 阻断率 | 0.000 |
| 修复率 | 0.029 |
| 无效标签率 | 0.000 |
| 焦点越界率 | 0.000 |
| 自相矛盾率 | 0.000 |
| 平均 Prompt Token 估计 | 406.436 |
| 平均 LLM 调用次数 | 2.193 |
| Bridge Judge 平均置信度 | 0.892 |
| 总延迟 P50 ms | 12490.538 |
| 总延迟 P95 ms | 31250.261 |

## 泄露等级分布

```json
{
  "0": 72,
  "1": 1,
  "2": 4,
  "3": 2,
  "4": 1
}
```

## 安全动作分布

```json
{
  "pass": 72,
  "rewrite": 8
}
```

## 阶段错误

```json
{}
```

## 分组结果

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 2.000 |
| 总延迟 P50 ms | 13848.969 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 3.700 |
| 总延迟 P50 ms | 20432.824 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | 0.050 |
| 平均 LLM 调用次数 | 3.400 |
| 总延迟 P50 ms | 21726.513 |

### tutor_mode=current_system|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 6241.816 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.050 |
| 总延迟 P50 ms | 6843.860 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | 0.100 |
| 平均 LLM 调用次数 | 2.150 |
| 总延迟 P50 ms | 12014.984 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 2.050 |
| 总延迟 P50 ms | 12043.094 |

