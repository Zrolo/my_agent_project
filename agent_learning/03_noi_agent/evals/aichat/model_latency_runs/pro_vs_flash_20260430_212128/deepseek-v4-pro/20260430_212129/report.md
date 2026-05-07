# 三模型 AIChat 速度测试报告

生成时间：2026-04-30T21:25:07

## 速度与质量概览

| 模型 | 思考模式 | 请求均值 | 请求 p95 | LLM 均值 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek (deepseek-v4-pro) | enabled | 27190 ms | 31394 ms | 22324 ms | 38% | 38% |

## 按输入形态

| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek | 未标注 | 8 | 27190 ms | 31394 ms | 38% | 38% |

## 按算法标签

| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek | 未标注 | 8 | 27190 ms | 31394 ms | 38% | 38% |

## 最慢 Case

| 模型 | Case | 请求耗时 | LLM 耗时 | 状态 |
| --- | --- | ---: | ---: | --- |
| DeepSeek | chat_socratic_004_bridge_attempt_p3128 | 31394 ms | 26295 ms | HTTP 500: Chat failed: 模型没有返回可展示的正文，请稍后重试或切换模型 |
| DeepSeek | chat_socratic_003_type_confirm_p3128_multi_solution | 31328 ms | 26012 ms | HTTP 500: Chat failed: 模型没有返回可展示的正文，请稍后重试或切换模型 |
| DeepSeek | chat_socratic_006_binary_search_check_condition | 31211 ms | 26201 ms | HTTP 500: Chat failed: 模型没有返回可展示的正文，请稍后重试或切换模型 |
| DeepSeek | chat_socratic_007_binary_search_left_bound | 30173 ms | 25174 ms | HTTP 500: Chat failed: 模型没有返回可展示的正文，请稍后重试或切换模型 |
| DeepSeek | chat_socratic_001_direct_code_request | 26994 ms | 21907 ms | ok |
| DeepSeek | chat_socratic_005_p3128_stage3_micro_example | 25538 ms | 21028 ms | HTTP 500: Chat failed: 模型没有返回可展示的正文，请稍后重试或切换模型 |
| DeepSeek | chat_socratic_002_type_confirm_trie | 22027 ms | 17622 ms | ok |
| DeepSeek | chat_socratic_008_lazy_semantics_type_confirm | 18857 ms | 14354 ms | ok |

## 错误与质量失败

- DeepSeek / chat_socratic_003_type_confirm_p3128_multi_solution: HTTP 500: Chat failed: 模型没有返回可展示的正文，请稍后重试或切换模型
- DeepSeek / chat_socratic_004_bridge_attempt_p3128: HTTP 500: Chat failed: 模型没有返回可展示的正文，请稍后重试或切换模型
- DeepSeek / chat_socratic_005_p3128_stage3_micro_example: HTTP 500: Chat failed: 模型没有返回可展示的正文，请稍后重试或切换模型
- DeepSeek / chat_socratic_006_binary_search_check_condition: HTTP 500: Chat failed: 模型没有返回可展示的正文，请稍后重试或切换模型
- DeepSeek / chat_socratic_007_binary_search_left_bound: HTTP 500: Chat failed: 模型没有返回可展示的正文，请稍后重试或切换模型
