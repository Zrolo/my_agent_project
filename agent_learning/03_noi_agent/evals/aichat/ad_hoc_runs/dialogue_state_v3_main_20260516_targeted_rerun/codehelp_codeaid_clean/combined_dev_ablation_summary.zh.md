# Bridge 离线评测摘要

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 5 |
| 完成数 | 4 |
| 错误数 | 1 |
| 自动进入主结果候选 | False |
| Dev Gate 需要复查 | True |
| Dev Gate 原因 | incomplete_or_error_rows, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| 学生状态准确率 | n/a |
| 桥梁大类准确率 | n/a |
| 知识焦点准确率 | n/a |
| 已注册知识焦点准确率 | n/a |
| 未知焦点召回率 | n/a |
| 求助类型准确率 | n/a |
| 帮助强度准确率 | n/a |
| 泄露率 | n/a |
| 关键桥梁泄露率 | n/a |
| 答案/代码泄露率 | n/a |
| 重写率 | n/a |
| 阻断率 | n/a |
| 修复率 | 0.000 |
| 修复后二次检查率 | 0.000 |
| 修复后仍泄露率 | n/a |
| 修复后二次重写/阻断率 | n/a |
| 无效标签率 | n/a |
| 焦点越界率 | n/a |
| 自相矛盾率 | n/a |
| 平均 Prompt Token 估计 | 94.500 |
| 平均 LLM 调用次数 | 1.250 |
| 候选回复静态风险率 | 0.500 |
| 候选回复答案槽位静态风险率 | 0.250 |
| 候选回复已填 trace 静态风险率 | 0.250 |
| 候选回复完整微例静态风险率 | 0.250 |
| 最终回复静态风险率 | 0.500 |
| 最终回复答案槽位静态风险率 | 0.250 |
| 最终回复已填 trace 静态风险率 | 0.250 |
| 最终回复完整微例静态风险率 | 0.250 |
| Bridge Judge 平均置信度 | n/a |
| 总延迟 P50 ms | 6269.612 |
| 总延迟 P95 ms | 22925.836 |

## 泄露等级分布

```json
{}
```

## 安全动作分布

```json
{}
```

## 阶段错误

```json
{
  "tutor": 1
}
```

## 分组结果

### tutor_mode=codehelp_codeaid_no_direct_solution_tutor|guard_mode=predicted|pipeline_mode=tutor_only_no_diagnosis|judge_schema_mode=full_schema_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=profile_default

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 5 |
| 完成数 | 4 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 1.250 |
| 自动进入主结果候选 | False |
| Dev Gate 原因 | incomplete_or_error_rows, final_static_answer_slot_risk, final_static_filled_trace_risk, final_static_worked_example_risk |
| 最终回复静态风险率 | 0.500 |
| 最终回复答案槽位静态风险率 | 0.250 |
| 最终回复已填 trace 静态风险率 | 0.250 |
| 最终回复完整微例静态风险率 | 0.250 |
| 总延迟 P50 ms | 6269.612 |


## 错误样本

- dialogue_v3_029_aggregation_contribution_summary
