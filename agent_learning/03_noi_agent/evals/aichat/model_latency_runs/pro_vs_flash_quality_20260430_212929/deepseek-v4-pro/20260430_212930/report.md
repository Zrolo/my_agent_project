# 三模型 AIChat 速度测试报告

生成时间：2026-04-30T21:32:41

## 速度与质量概览

| 模型 | 思考模式 | 请求均值 | 请求 p95 | LLM 均值 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek (deepseek-v4-pro) | enabled | 47738 ms | 66693 ms | 42696 ms | 100% | 0% |

## 按输入形态

| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek | 未标注 | 4 | 47738 ms | 66693 ms | 100% | 0% |

## 按算法标签

| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek | 未标注 | 4 | 47738 ms | 66693 ms | 100% | 0% |

## 最慢 Case

| 模型 | Case | 请求耗时 | LLM 耗时 | 状态 |
| --- | --- | ---: | ---: | --- |
| DeepSeek | chat_socratic_004_bridge_attempt_p3128 | 66693 ms | 61993 ms | ok |
| DeepSeek | chat_socratic_006_binary_search_check_condition | 51087 ms | 45545 ms | ok |
| DeepSeek | chat_socratic_009_dp_state_design | 45135 ms | 40294 ms | ok |
| DeepSeek | chat_socratic_002_type_confirm_trie | 28040 ms | 22952 ms | ok |

## 错误与质量失败

- DeepSeek / chat_socratic_002_type_confirm_trie: too_many_questions:3
- DeepSeek / chat_socratic_004_bridge_attempt_p3128: reply_too_long:364
- DeepSeek / chat_socratic_006_binary_search_check_condition: too_many_questions:7; reply_too_long:367
- DeepSeek / chat_socratic_009_dp_state_design: reply_too_long:613
