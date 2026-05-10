# Bridge 离线评测摘要

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 错误数 | 0 |
| 学生状态准确率 | 0.650 |
| 桥梁大类准确率 | 0.900 |
| 知识焦点准确率 | 0.800 |
| 已注册知识焦点准确率 | 0.800 |
| 未知焦点召回率 | n/a |
| 求助类型准确率 | 0.500 |
| 帮助强度准确率 | 0.950 |
| 泄露率 | 0.050 |
| 关键桥梁泄露率 | 0.000 |
| 答案/代码泄露率 | 0.000 |
| 重写率 | 0.000 |
| 阻断率 | 0.000 |
| 修复率 | 0.000 |
| 无效标签率 | 0.000 |
| 焦点越界率 | 0.000 |
| 自相矛盾率 | 0.000 |
| 平均 Prompt Token 估计 | 523.100 |
| 平均 LLM 调用次数 | 3.350 |
| Bridge Judge 平均置信度 | 0.904 |
| 总延迟 P50 ms | 17094.474 |
| 总延迟 P95 ms | 23998.282 |

## 泄露等级分布

```json
{
  "0": 18,
  "1": 1,
  "unknown": 1
}
```

## 安全动作分布

```json
{
  "pass": 19,
  "unknown": 1
}
```

## 阶段错误

```json
{
  "leakage_judge": 1
}
```

## 分组结果

### tutor_mode=bridge_contract|guard_mode=predicted|pipeline_mode=tutor_plus_guard_plus_repair|judge_schema_mode=retrieval_augmented_compact_judge|tutor_model_provider=deepseek_flash|chat_thinking_mode=disabled

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 20 |
| 完成数 | 20 |
| 桥梁大类准确率 | 0.900 |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 3.350 |
| 总延迟 P50 ms | 17094.474 |

