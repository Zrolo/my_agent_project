# Bridge 离线评测摘要

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 错误数 | 0 |
| 学生状态准确率 | 0.600 |
| 桥梁大类准确率 | 0.900 |
| 知识焦点准确率 | 0.700 |
| 已注册知识焦点准确率 | 0.700 |
| 未知焦点召回率 | n/a |
| 求助类型准确率 | 0.500 |
| 帮助强度准确率 | 0.950 |
| 泄露率 | n/a |
| 关键桥梁泄露率 | n/a |
| 答案/代码泄露率 | n/a |
| 重写率 | n/a |
| 阻断率 | n/a |
| 修复率 | 0.000 |
| 无效标签率 | 0.000 |
| 焦点越界率 | 0.000 |
| 自相矛盾率 | 0.000 |
| 平均 Prompt Token 估计 | 521.850 |
| 平均 LLM 调用次数 | 2.050 |
| Bridge Judge 平均置信度 | 0.899 |
| 总延迟 P50 ms | 21120.987 |
| 总延迟 P95 ms | 43397.752 |

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
{}
```

## 分组结果

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 2.100 |
| 总延迟 P50 ms | 14732.092 |

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_only|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=enabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 10 |
| 完成数 | 10 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | n/a |
| 平均 LLM 调用次数 | 2.000 |
| 总延迟 P50 ms | 32169.317 |
