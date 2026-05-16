# Bridge 离线评测摘要

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 350 |
| 完成数 | 350 |
| 错误数 | 0 |
| 自动进入主结果候选 | False |
| Dev Gate 需要复查 | True |
| Dev Gate 原因 | critical_bridge_leakage, repair_still_leaks, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| 学生状态准确率 | n/a |
| 桥梁大类准确率 | n/a |
| 知识焦点准确率 | n/a |
| 已注册知识焦点准确率 | n/a |
| 未知焦点召回率 | n/a |
| 求助类型准确率 | n/a |
| 帮助强度准确率 | n/a |
| 泄露率 | 0.345 |
| 关键桥梁泄露率 | 0.115 |
| 答案/代码泄露率 | 0.000 |
| 重写率 | 0.320 |
| 阻断率 | 0.000 |
| 修复率 | 0.037 |
| 修复后二次检查率 | 0.034 |
| 修复后仍泄露率 | 0.083 |
| 修复后二次重写/阻断率 | 0.167 |
| 无效标签率 | n/a |
| 焦点越界率 | n/a |
| 自相矛盾率 | n/a |
| 平均 Prompt Token 估计 | 101.720 |
| 平均 LLM 调用次数 | 2.294 |
| 候选回复静态风险率 | 0.369 |
| 候选回复答案槽位静态风险率 | 0.094 |
| 候选回复已填 trace 静态风险率 | 0.203 |
| 候选回复完整微例静态风险率 | 0.106 |
| 最终回复静态风险率 | 0.366 |
| 最终回复答案槽位静态风险率 | 0.094 |
| 最终回复已填 trace 静态风险率 | 0.200 |
| 最终回复完整微例静态风险率 | 0.106 |
| Bridge Judge 平均置信度 | 0.848 |
| 总延迟 P50 ms | 19157.898 |
| 总延迟 P95 ms | 42791.170 |

## 泄露等级分布

```json
{
  "0": 131,
  "1": 16,
  "2": 30,
  "3": 23
}
```

## 安全动作分布

```json
{
  "pass": 136,
  "rewrite": 64
}
```

## 阶段错误

```json
{}
```

## 分组结果

### tutor_mode=bridge_contract_compact|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 50 |
| 完成数 | 50 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | 0.080 |
| 平均 LLM 调用次数 | 3.540 |
| 自动进入主结果候选 | False |
| Dev Gate 原因 | critical_bridge_leakage, repair_still_leaks, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| 最终回复静态风险率 | 0.420 |
| 最终回复答案槽位静态风险率 | 0.120 |
| 最终回复已填 trace 静态风险率 | 0.240 |
| 最终回复完整微例静态风险率 | 0.080 |
| 总延迟 P50 ms | 20850.630 |

### tutor_mode=bridge_contract_compact|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 50 |
| 完成数 | 50 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | 0.100 |
| 平均 LLM 调用次数 | 3.080 |
| 自动进入主结果候选 | False |
| Dev Gate 原因 | critical_bridge_leakage, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| 最终回复静态风险率 | 0.360 |
| 最终回复答案槽位静态风险率 | 0.120 |
| 最终回复已填 trace 静态风险率 | 0.200 |
| 最终回复完整微例静态风险率 | 0.080 |
| 总延迟 P50 ms | 17349.247 |

### tutor_mode=bridge_guided_dbox_style_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 50 |
| 完成数 | 50 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | 0.160 |
| 平均 LLM 调用次数 | 3.180 |
| 自动进入主结果候选 | False |
| Dev Gate 原因 | critical_bridge_leakage, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| 最终回复静态风险率 | 0.300 |
| 最终回复答案槽位静态风险率 | 0.080 |
| 最终回复已填 trace 静态风险率 | 0.180 |
| 最终回复完整微例静态风险率 | 0.080 |
| 总延迟 P50 ms | 25739.477 |

### tutor_mode=codehelp_codeaid_no_direct_solution_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 50 |
| 完成数 | 50 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.080 |
| 自动进入主结果候选 | False |
| Dev Gate 原因 | final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| 最终回复静态风险率 | 0.440 |
| 最终回复答案槽位静态风险率 | 0.060 |
| 最终回复已填 trace 静态风险率 | 0.160 |
| 最终回复完整微例静态风险率 | 0.300 |
| 总延迟 P50 ms | 8454.553 |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 50 |
| 完成数 | 50 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.040 |
| 自动进入主结果候选 | False |
| Dev Gate 原因 | final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| 最终回复静态风险率 | 0.340 |
| 最终回复答案槽位静态风险率 | 0.120 |
| 最终回复已填 trace 静态风险率 | 0.180 |
| 最终回复完整微例静态风险率 | 0.060 |
| 总延迟 P50 ms | 11906.860 |

### tutor_mode=dbox_inspired_decomposition_tutor|guard_mode=predicted|pipeline_mode=tutor_plus_guard|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 50 |
| 完成数 | 50 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | 0.120 |
| 平均 LLM 调用次数 | 3.140 |
| 自动进入主结果候选 | False |
| Dev Gate 原因 | critical_bridge_leakage, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| 最终回复静态风险率 | 0.340 |
| 最终回复答案槽位静态风险率 | 0.080 |
| 最终回复已填 trace 静态风险率 | 0.240 |
| 最终回复完整微例静态风险率 | 0.020 |
| 总延迟 P50 ms | 24052.604 |

### tutor_mode=enhanced_prompt_only|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 50 |
| 完成数 | 50 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.000 |
| 自动进入主结果候选 | False |
| Dev Gate 原因 | final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| 最终回复静态风险率 | 0.360 |
| 最终回复答案槽位静态风险率 | 0.080 |
| 最终回复已填 trace 静态风险率 | 0.200 |
| 最终回复完整微例静态风险率 | 0.120 |
| 总延迟 P50 ms | 23636.265 |

