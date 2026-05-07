# 三模型 AIChat 速度测试报告

生成时间：2026-04-30T21:42:17

## 速度与质量概览

| 模型 | 思考模式 | 请求均值 | 请求 p95 | LLM 均值 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Flash (current) (deepseek-v4-flash) | enabled | 12264 ms | 15031 ms | 9567 ms | 100% | 50% |

## 按输入形态

| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Flash (current) | 未标注 | 4 | 12264 ms | 15031 ms | 100% | 50% |

## 按算法标签

| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Flash (current) | 未标注 | 4 | 12264 ms | 15031 ms | 100% | 50% |

## 最慢 Case

| 模型 | Case | 请求耗时 | LLM 耗时 | 状态 |
| --- | --- | ---: | ---: | --- |
| DeepSeek V4 Flash (current) | chat_socratic_004_bridge_attempt_p3128 | 15031 ms | 12168 ms | ok |
| DeepSeek V4 Flash (current) | chat_socratic_002_type_confirm_trie | 12539 ms | 9898 ms | ok |
| DeepSeek V4 Flash (current) | chat_socratic_006_binary_search_check_condition | 11096 ms | 8416 ms | ok |
| DeepSeek V4 Flash (current) | chat_socratic_009_dp_state_design | 10392 ms | 7787 ms | ok |

## 错误与质量失败

- DeepSeek V4 Flash (current) / chat_socratic_004_bridge_attempt_p3128: too_many_questions:3; reply_too_long:815
- DeepSeek V4 Flash (current) / chat_socratic_006_binary_search_check_condition: forbidden_semantic:ab_bridge_leak; too_many_questions:3; reply_too_long:338
