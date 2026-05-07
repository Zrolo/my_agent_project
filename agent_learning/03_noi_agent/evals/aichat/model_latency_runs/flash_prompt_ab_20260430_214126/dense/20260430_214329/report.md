# 三模型 AIChat 速度测试报告

生成时间：2026-04-30T21:43:29

## 速度与质量概览

| 模型 | 思考模式 | 请求均值 | 请求 p95 | LLM 均值 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Flash (dense) (deepseek-v4-flash) | enabled | 17885 ms | 22759 ms | 15132 ms | 100% | 0% |

## 按输入形态

| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Flash (dense) | 未标注 | 4 | 17885 ms | 22759 ms | 100% | 0% |

## 按算法标签

| 模型 | 分组 | 数量 | 请求均值 | 请求 p95 | 成功率 | 质量通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Flash (dense) | 未标注 | 4 | 17885 ms | 22759 ms | 100% | 0% |

## 最慢 Case

| 模型 | Case | 请求耗时 | LLM 耗时 | 状态 |
| --- | --- | ---: | ---: | --- |
| DeepSeek V4 Flash (dense) | chat_socratic_004_bridge_attempt_p3128 | 22759 ms | 20271 ms | ok |
| DeepSeek V4 Flash (dense) | chat_socratic_006_binary_search_check_condition | 21416 ms | 18546 ms | ok |
| DeepSeek V4 Flash (dense) | chat_socratic_009_dp_state_design | 16171 ms | 13260 ms | ok |
| DeepSeek V4 Flash (dense) | chat_socratic_002_type_confirm_trie | 11194 ms | 8452 ms | ok |

## 错误与质量失败

- DeepSeek V4 Flash (dense) / chat_socratic_002_type_confirm_trie: too_many_questions:4
- DeepSeek V4 Flash (dense) / chat_socratic_004_bridge_attempt_p3128: reply_too_long:604
- DeepSeek V4 Flash (dense) / chat_socratic_006_binary_search_check_condition: reply_too_long:685
- DeepSeek V4 Flash (dense) / chat_socratic_009_dp_state_design: forbidden_semantic:dp_state_definition; reply_too_long:601
