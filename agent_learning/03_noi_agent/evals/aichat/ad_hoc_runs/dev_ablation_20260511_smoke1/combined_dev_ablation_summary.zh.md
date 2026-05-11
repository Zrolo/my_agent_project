# Bridge 离线评测摘要

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 11 |
| 完成数 | 9 |
| 错误数 | 2 |
| 学生状态准确率 | 1.000 |
| 桥梁大类准确率 | 0.800 |
| 知识焦点准确率 | 0.600 |
| 已注册知识焦点准确率 | 0.600 |
| 未知焦点召回率 | n/a |
| 求助类型准确率 | 0.000 |
| 帮助强度准确率 | 1.000 |
| 泄露率 | 0.333 |
| 关键桥梁泄露率 | 0.000 |
| 答案/代码泄露率 | 0.000 |
| 重写率 | 0.333 |
| 阻断率 | 0.000 |
| 修复率 | 0.111 |
| 无效标签率 | 0.000 |
| 焦点越界率 | n/a |
| 自相矛盾率 | 0.000 |
| 平均 Prompt Token 估计 | 46.000 |
| 平均 LLM 调用次数 | 1.778 |
| Bridge Judge 平均置信度 | 0.923 |
| 总延迟 P50 ms | 55155.098 |
| 总延迟 P95 ms | 244735.074 |

## 泄露等级分布

```json
{
  "0": 2,
  "2": 1
}
```

## 安全动作分布

```json
{
  "pass": 2,
  "rewrite": 1
}
```

## 阶段错误

```json
{
  "tutor": 2
}
```

## 分组结果

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 1 |
| 桥梁大类准确率 | 1.000 |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 2.000 |
| 总延迟 P50 ms | 244735.074 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 1 |
| 桥梁大类准确率 | 1.000 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 4.000 |
| 总延迟 P50 ms | 175391.471 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 1 |
| 桥梁大类准确率 | 1.000 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 3.000 |
| 总延迟 P50 ms | 80142.793 |

### tutor_mode=bridge_inspired_expert_decision_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 1 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 36465.784 |

### tutor_mode=codehelp_codeaid_no_direct_solution_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 1 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 5713.800 |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 0 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | n/a |
| 总延迟 P50 ms | n/a |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 0 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | n/a |
| 总延迟 P50 ms | n/a |

### tutor_mode=enhanced_prompt_only|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 1 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 28146.812 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 1 |
| 桥梁大类准确率 | 0.000 |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 103744.661 |

### tutor_mode=single_llm_structured|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 1 |
| 桥梁大类准确率 | 1.000 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 2.000 |
| 总延迟 P50 ms | 36867.193 |

### tutor_mode=socratic_no_answer_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 1 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 总延迟 P50 ms | 55155.098 |


## 错误样本

- cp_bridge_001
- cp_bridge_001
