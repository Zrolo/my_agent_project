# 三模型 AIChat 速度测试报告

生成时间：2026-04-30T21:33:53

## 速度与质量概览

| 模型 | 思考模式 | 请求均值 | 请求 p95 | LLM 均值 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek (deepseek-v4-flash) | enabled | 17877 ms | 26042 ms | 15015 ms | 100% | 50% |

## 按输入形态

| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek | 未标注 | 4 | 17877 ms | 26042 ms | 100% | 50% |

## 按算法标签

| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek | 未标注 | 4 | 17877 ms | 26042 ms | 100% | 50% |

## 最慢 Case

| 模型 | Case | 请求耗时 | LLM 耗时 | 状态 |
| --- | --- | ---: | ---: | --- |
| DeepSeek | chat_socratic_004_bridge_attempt_p3128 | 26042 ms | 23432 ms | ok |
| DeepSeek | chat_socratic_006_binary_search_check_condition | 18602 ms | 15631 ms | ok |
| DeepSeek | chat_socratic_009_dp_state_design | 16764 ms | 13746 ms | ok |
| DeepSeek | chat_socratic_002_type_confirm_trie | 10103 ms | 7251 ms | ok |

## 错误与质量失败

- DeepSeek / chat_socratic_006_binary_search_check_condition: too_many_questions:5; reply_too_long:553
- DeepSeek / chat_socratic_009_dp_state_design: reply_too_long:470
