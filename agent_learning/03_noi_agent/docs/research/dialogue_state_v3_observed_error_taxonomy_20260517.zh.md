# Dialogue-State v3 Observed Error Taxonomy 20260517

## 范围

这是基于 dialogue-state v3 human review labels 的 observed taxonomy，不是 universal taxonomy。它把错误拆成三层：

```text
Level 1 = general tutoring failure type
Level 2 = operational cognitive bridge family
Level 3 = surface anchor example
```

Level 2 中的 `state_representation_semantics` 等 bridge bucket 是 operational cognitive bridge family；DP state、binary-search check、lazy propagation、tree difference、local code、greedy proof、debugging trace 等才是 surface anchors。下面的计数来自 `priority60 adjudicated + Coach A` 标签和现有 disagreement / adjudication pool 的机械派生。error pool 覆盖 major / answer leakage、minor leakage、overall <= 2、show = no、safe-ready = false、high student burden、Coach A/B disagreement、priority60 adjudication samples 和 rank-last rows。一个 row 可以同时属于多个 Level 1 error type，因此计数不是互斥分类。

## Level 1 定义

| id | error type | 定义 | 判定标准 | 非例子 |
| --- | --- | --- | --- | --- |
| E1 | `critical_bridge_leakage` | AI 提前替学生完成当前 missing bridge。 | `minor_bridge_leakage` 或 `major_bridge_leakage`，或备注显示关键关系被说穿。 | 只复述学生已说出的观察，或给出开放性检查问题。 |
| E2 | `answer_or_code_leakage` | 回复暴露完整答案、完整路线或关键代码。 | `answer_leakage`，或直接补完局部代码 / 完整模板。 | 给出不完整的变量检查点或让学生填写一处判断。 |
| E3 | `over_complete_micro_example` | micro-example / trace 把关键关系演完。 | 例子中已经给出状态、转移、check 结果、边界移动或证明结论。 | 例子只要求学生比较两个对象或填写中间观察。 |
| E4 | `wrong_or_shifted_focus` | 回复没有对准当前卡点，或把问题转成另一个任务。 | bridge identification / groundedness / single-focus 低，或备注指出答非所问。 | 回复先澄清上下文，但仍围绕当前学生问题。 |
| E5 | `under_scaffolded_or_too_vague` | 安全但帮助不足，学生下一步仍不知道做什么。 | scaffold sufficiency / next-step clarity 低，或 overall <= 2 且无泄露。 | 回复给出一个明确、低负担的局部判断任务。 |
| E6 | `excessive_student_burden` | 学生下一轮需要输出太多内容或推太远。 | `student_response_burden=high`。 | 只要求学生回答一个二选一、短解释或局部变量含义。 |
| E7 | `context_misalignment` | 对短问或上下文状态误判，过度脑补或没有澄清。 | no recent dialogue / context insufficient 下仍直接推断关键桥，且 show 不稳。 | 明确要求学生补充当前卡点或引用上一轮上下文。 |
| E8 | `over_safe_refusal_or_empty_help` | 过度拒绝或空泛安全提示，几乎不给学习推进。 | policy/request 场景中只拒绝、不提供替代微任务。 | 拒绝完整答案后给出一个可执行的安全下一步。 |
| E9 | `factual_or_algorithmic_error` | 回复中有事实、算法或题意错误。 | 教练备注指出错误、不准确或误导。 | 策略保守但没有错误信息。 |
| E10 | `policy_or_direct_answer_handling_failure` | 面对直接要答案/代码时安全重定向失败。 | policy_request case 中出现泄露、no-show 或没有替代学习动作。 | 不给完整解法，同时把学生引回最小可学习步骤。 |

## Level 2 families 与 Level 3 surface anchors

| Level 2 operational cognitive bridge family | Level 3 surface anchor examples |
| --- | --- |
| representation semantics | DP state, interval state, array meaning |
| transition / action mapping | recurrence branch, action source, previous-state dependency |
| predicate / decision semantics | binary-search check, feasibility predicate, true/false meaning |
| ordering / dependency control | binary boundary update, loop direction, update order |
| modeling relation | graph/tree abstraction, object-relation mapping |
| aggregation / contribution accounting | contribution sum, prefix/difference accumulation |
| data-structure operation mapping | lazy propagation, tree difference, maintained summary |
| correctness / invariant reasoning | greedy proof, exchange argument, invariant |
| implementation boundary | local code, index boundary, initialization |
| debugging evidence | debugging trace, minimal counterexample, print target |
| policy-request handling | direct-answer request, code-request redirect |

## 各 condition 的 observed error 分布

| condition | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 31 | 1 | 27 | 2 | 4 | 25 | 7 | 0 | 0 | 1 |
| `codehelp_codeaid_clean` | 11 | 0 | 7 | 11 | 5 | 3 | 5 | 0 | 0 | 1 |
| `dbox_inspired_clean` | 11 | 2 | 4 | 5 | 3 | 5 | 4 | 0 | 0 | 1 |
| `dbox_inspired_guard` | 10 | 0 | 2 | 9 | 6 | 2 | 4 | 0 | 0 | 1 |
| `bridge_guided_dbox_style_guard` | 16 | 2 | 15 | 10 | 2 | 2 | 6 | 0 | 1 | 2 |
| `bridge_contract_compact_guard` | 14 | 0 | 8 | 7 | 3 | 1 | 5 | 0 | 1 | 0 |
| `bridge_contract_compact_guard_repair` | 7 | 0 | 4 | 8 | 2 | 0 | 2 | 0 | 0 | 0 |

读法：该表是多标签 error pool 计数，不是 row 数。`enhanced_prompt_only_clean` 的 E1/E3/E6 高，说明强提示词仍容易用过完整例子或高负担任务替学生走完关键桥。`bridge_contract_compact_guard_repair` 的 E1/E3/E6 较低，但不能据此推断 Repair 因果有效，因为主实验 condition 的 candidate 不同。

## Level 1 × Level 2 覆盖摘要

| error type | observed bridge families |
| --- | --- |
| E1 critical bridge leakage | representation semantics; transition/action mapping; predicate/decision semantics; ordering/dependency; modeling relation; aggregation/contribution; data-structure operation; correctness/invariant; implementation; debugging evidence; policy request |
| E2 answer/code leakage | data-structure operation; correctness/invariant; implementation; policy request |
| E3 over-complete micro-example | representation semantics; transition/action mapping; predicate/decision semantics; ordering/dependency; modeling relation; aggregation/contribution; data-structure operation; correctness/invariant; implementation; debugging evidence; policy request |
| E4 wrong/shifted focus | representation semantics; transition/action mapping; predicate/decision semantics; ordering/dependency; modeling relation; aggregation/contribution; correctness/invariant; implementation; debugging evidence |
| E5 under-scaffolded / too vague | representation semantics; transition/action mapping; predicate/decision semantics; ordering/dependency; modeling relation; aggregation/contribution; correctness/invariant; implementation; debugging evidence; policy request |
| E6 excessive burden | all observed families |
| E7 context misalignment | mostly short-question representation / transition cases without recent dialogue |
| E8 over-safe refusal / empty help | not observed as a frequent row-level tag in this derived pool; keep as taxonomy slot for policy-safety analysis |
| E9 factual / algorithmic error | ordering/dependency; debugging evidence |
| E10 policy/direct-answer handling failure | policy-request handling |

## 典型 case_id

| error type | typical case_id / condition examples |
| --- | --- |
| E1 | `dialogue_v3_001_state_representation_semantics` / `enhanced_prompt_only_clean`; `dialogue_v3_012_predicate_check_semantics` / `dbox_inspired_guard`; `dialogue_v3_020_boundary_update_order` / `bridge_guided_dbox_style_guard` |
| E2 | `dialogue_v3_031_data_structure_operation_semantics` / `enhanced_prompt_only_clean`; `dialogue_v3_044_implementation_boundary` / `dbox_inspired_clean`; `dialogue_v3_049_policy_request` / `bridge_guided_dbox_style_guard` |
| E3 | `dialogue_v3_001_state_representation_semantics` / `enhanced_prompt_only_clean`; `dialogue_v3_015_predicate_check_semantics` / `bridge_contract_compact_guard`; `dialogue_v3_038_correctness_invariant` / `bridge_guided_dbox_style_guard` |
| E4 | `dialogue_v3_007_transition_recurrence_source` / `codehelp_codeaid_clean`; `dialogue_v3_024_modeling_object_relation` / `bridge_guided_dbox_style_guard`; `dialogue_v3_047_debugging_evidence` / `bridge_guided_dbox_style_guard` |
| E5 | `dialogue_v3_001_state_representation_semantics` / `bridge_guided_dbox_style_guard`; `dialogue_v3_011_transition_recurrence_source` / `bridge_contract_compact_guard`; `dialogue_v3_045_debugging_evidence` / `codehelp_codeaid_clean` |
| E6 | `dialogue_v3_001_state_representation_semantics` / `enhanced_prompt_only_clean`; `dialogue_v3_036_correctness_invariant` / `enhanced_prompt_only_clean`; `dialogue_v3_048_policy_request` / `enhanced_prompt_only_clean` |
| E7 | `dialogue_v3_001_state_representation_semantics` / `bridge_guided_dbox_style_guard`; `dialogue_v3_002_state_representation_semantics` / `dbox_inspired_guard`; `dialogue_v3_008_transition_recurrence_source` / `codehelp_codeaid_clean` |
| E8 | no stable high-frequency example in the derived pool; inspect policy slice manually if this becomes a reviewer concern |
| E9 | `dialogue_v3_017_boundary_update_order` / `bridge_contract_compact_guard`; `dialogue_v3_047_debugging_evidence` / `bridge_guided_dbox_style_guard` |
| E10 | `dialogue_v3_048_policy_request` / `bridge_guided_dbox_style_guard`; `dialogue_v3_049_policy_request` / `enhanced_prompt_only_clean`; `dialogue_v3_050_policy_request` / `dbox_inspired_clean` |

## 论文写法

可以写：Observed errors span multiple cognitive bridge families and surface anchors; critical bridge leakage is not limited to DP state definitions or binary-search checks.

不能写：本 taxonomy 已覆盖所有 CP tutoring 错误，或每个 error type 都有充分样本。当前 taxonomy 是 observed taxonomy，需要在更大、多题型、多轮数据上扩展。
