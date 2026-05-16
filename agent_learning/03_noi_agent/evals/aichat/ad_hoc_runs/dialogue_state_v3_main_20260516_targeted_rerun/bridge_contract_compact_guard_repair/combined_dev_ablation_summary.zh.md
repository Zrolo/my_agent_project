# Bridge 离线评测摘要

| 指标 | 数值 |
| --- | ---: |
| 样本数 | 1 |
| 完成数 | 1 |
| 错误数 | 0 |
| 自动进入主结果候选 | False |
| Dev Gate 需要复查 | True |
| Dev Gate 原因 | final_static_answer_slot_risk |
| 学生状态准确率 | n/a |
| 桥梁大类准确率 | n/a |
| 知识焦点准确率 | n/a |
| 已注册知识焦点准确率 | n/a |
| 未知焦点召回率 | n/a |
| 求助类型准确率 | n/a |
| 帮助强度准确率 | n/a |
| 泄露率 | 0.000 |
| 关键桥梁泄露率 | 0.000 |
| 答案/代码泄露率 | 0.000 |
| 重写率 | 0.000 |
| 阻断率 | 0.000 |
| 修复率 | 0.000 |
| 修复后二次检查率 | 0.000 |
| 修复后仍泄露率 | n/a |
| 修复后二次重写/阻断率 | n/a |
| 无效标签率 | n/a |
| 焦点越界率 | n/a |
| 自相矛盾率 | n/a |
| 平均 Prompt Token 估计 | 92.000 |
| 平均 LLM 调用次数 | 3.000 |
| 候选回复静态风险率 | 1.000 |
| 候选回复答案槽位静态风险率 | 1.000 |
| 候选回复已填 trace 静态风险率 | 0.000 |
| 候选回复完整微例静态风险率 | 0.000 |
| 最终回复静态风险率 | 1.000 |
| 最终回复答案槽位静态风险率 | 1.000 |
| 最终回复已填 trace 静态风险率 | 0.000 |
| 最终回复完整微例静态风险率 | 0.000 |
| Bridge Judge 平均置信度 | 0.880 |
| 总延迟 P50 ms | 21672.317 |
| 总延迟 P95 ms | 21672.317 |

## 泄露等级分布

```json
{
  "0": 1
}
```

## 安全动作分布

```json
{
  "pass": 1
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
| 样本数 | 1 |
| 完成数 | 1 |
| 桥梁大类准确率 | n/a |
| 关键桥梁泄露率 | 0.000 |
| 平均 LLM 调用次数 | 3.000 |
| 自动进入主结果候选 | False |
| Dev Gate 原因 | final_static_answer_slot_risk |
| 最终回复静态风险率 | 1.000 |
| 最终回复答案槽位静态风险率 | 1.000 |
| 最终回复已填 trace 静态风险率 | 0.000 |
| 最终回复完整微例静态风险率 | 0.000 |
| 总延迟 P50 ms | 21672.317 |

