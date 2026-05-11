# Bridge 离线评测摘要

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 110 |
| 完成数 | 110 |
| 错误数 | 0 |
| 学生状态准确率 | 0.575 |
| 桥梁大类准确率 | 0.833 |
| 知识焦点准确率 | 0.467 |
| 已注册知识焦点准确率 | 0.467 |
| 未知焦点召回率 | n/a |
| 求助类型准确率 | 0.525 |
| 帮助强度准确率 | 0.917 |
| 泄露率 | 0.225 |
| 关键桥梁泄露率 | 0.075 |
| 答案/代码泄露率 | 0.000 |
| 重写率 | 0.200 |
| 阻断率 | 0.000 |
| 修复率 | 0.009 |
| 无效标签率 | 0.000 |
| 焦点越界率 | n/a |
| 自相矛盾率 | 0.000 |
| 平均 Prompt Token 估计 | 49.300 |
| 平均 LLM 调用次数 | 1.755 |
| Bridge Judge 平均置信度 | 0.902 |
| 总延迟 P50 ms | 21934.524 |
| 总延迟 P95 ms | 50102.215 |

## 泄露等级分布

```json
{
  "0": 31,
  "2": 6,
  "3": 3
}
```

## 安全动作分布

```json
{
  "pass": 32,
  "rewrite": 8
}
```

## 阶段错误

```json
{}
```

## 分组结果

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 2.000 |
| 总延迟 P50 ms | 41628.967 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 3.100 |
| 总延迟 P50 ms | 34845.476 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | 0.200 |
| 平均 LLM 调用次数 | 3.200 |
| 总延迟 P50 ms | 41360.572 |

### tutor_mode=bridge_inspired_expert_decision_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 10331.701 |

### tutor_mode=codehelp_codeaid_no_direct_solution_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 10232.718 |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 10515.896 |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | 0.800 |
| 关键桥梁泄露率 | 0.100 |
| 平均 LLM 调用次数 | 3.000 |
| 总延迟 P50 ms | 24993.466 |

### tutor_mode=enhanced_prompt_only|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 24351.504 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | 0.700 |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 17662.978 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | 0.800 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 2.000 |
| 总延迟 P50 ms | 22654.532 |

### tutor_mode=socratic_no_answer_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 26330.951 |
