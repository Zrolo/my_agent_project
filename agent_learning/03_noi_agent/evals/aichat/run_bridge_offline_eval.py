import argparse
from contextlib import contextmanager
import inspect
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable

from evals.aichat.bridge_candidate_retriever import (
    retrieve_algorithm_topic_candidates,
    retrieve_focus_candidates,
)
from noi_agent import (
    _chat_completion_create,
    _extract_json_object,
    bridge_judge_v1,
    chat as noi_agent_chat,
    leakage_judge_v1,
    repair_response_v1,
)


DEFAULT_SEED_PATH = Path("docs/research/bridgebench_cp_seed_v1.jsonl")
DEFAULT_OUTPUT_PATH = Path("evals/aichat/bridge_offline_eval_results.jsonl")
DEFAULT_FOCUS_REGISTRY_PATH = Path("docs/research/focus_registry_v1.json")
PIPELINE_MODES = {
    "diagnosis_only",
    "tutor_only",
    "tutor_only_no_diagnosis",
    "tutor_plus_guard",
    "tutor_plus_guard_plus_repair",
}
JUDGE_SCHEMA_MODES = {
    "full_schema_judge",
    "compact_contract_judge",
    "retrieval_augmented_compact_judge",
}
TUTOR_MODES = {
    "current_system",
    "bridge_contract",
    "bridge_inspired_expert_decision_tutor",
    "codehelp_codeaid_no_direct_solution_tutor",
    "enhanced_prompt_only",
    "single_llm_structured",
    "dbox_inspired_decomposition_tutor",
    "socratic_no_answer_tutor",
}
STANDALONE_NO_DIAGNOSIS_TUTOR_MODES = {
    "current_system",
    "codehelp_codeaid_no_direct_solution_tutor",
    "dbox_inspired_decomposition_tutor",
    "enhanced_prompt_only",
    "bridge_inspired_expert_decision_tutor",
    "socratic_no_answer_tutor",
}
CONTRACT_TURN_TYPES = [
    "diagnosable_learning_turn",
    "insufficient_context",
    "complete_solution_request",
    "complete_code_request",
    "critical_bridge_request",
    "algorithm_confirmation_request",
    "local_completion_request",
    "code_debugging_without_evidence",
    "code_debugging_with_evidence",
    "step_validation_request",
    "reflection_or_transfer_turn",
    "emotional_or_time_pressure",
    "unknown",
]
CONTRACT_ALGORITHM_TOPICS_L1 = [
    "dp",
    "binary_search",
    "graph",
    "tree",
    "data_structure",
    "string",
    "greedy",
    "search",
    "math",
    "implementation",
    "debugging",
    "unknown",
]
CONTRACT_BRIDGE_FAMILIES = [
    "goal_constraint_bridge",
    "modeling_bridge",
    "method_selection_bridge",
    "representation_state_bridge",
    "transition_recurrence_bridge",
    "predicate_condition_bridge",
    "ordering_dependency_bridge",
    "aggregation_contribution_bridge",
    "data_structure_operation_bridge",
    "correctness_invariant_bridge",
    "complexity_optimization_bridge",
    "implementation_boundary_bridge",
    "debugging_evidence_bridge",
    "reflection_transfer_bridge",
    "unknown_or_not_applicable",
    "unknown_bridge",
]
CONTRACT_HELP_FORMS = [
    "question",
    "hint",
    "micro_example",
    "counterexample",
    "diagram",
    "checklist",
    "code_diagnosis",
    "guiding_question",
    "constraint_probe",
    "debug_evidence_request",
    "local_code_hint",
    "partial_trace",
    "summary_and_next_step",
    "understanding_check",
    "reflection_prompt",
]

BridgeJudgeFn = Callable[..., dict]
TutorFn = Callable[[dict, list[dict], dict], dict]
LeakageJudgeFn = Callable[..., dict]
RepairFn = Callable[..., dict]


def _judge_model_name(judge_provider: str = "deepseek") -> str:
    if judge_provider == "kimi":
        return os.environ.get("KIMI_MODEL", "kimi-k2.6")
    if judge_provider in {"deepseek", "deepseek_flash", "deepseek-v4-flash"}:
        return os.environ.get("NOI_PEDAGOGICAL_JUDGE_MODEL", "deepseek-v4-flash")
    return judge_provider


def load_seed_rows(path: Path = DEFAULT_SEED_PATH) -> list[dict]:
    rows = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def load_focus_registry(path: Path = DEFAULT_FOCUS_REGISTRY_PATH) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("focuses", [])
    if not isinstance(data, list):
        raise ValueError(f"Focus registry must be a list or contain a focuses list: {path}")
    registry = []
    for item in data:
        if isinstance(item, str):
            registry.append({"focus_id": item})
        elif isinstance(item, dict) and item.get("focus_id"):
            registry.append(dict(item))
    return registry


def _compact_focus_registry(focus_registry: list | None) -> list:
    compact = []
    for item in focus_registry or []:
        if isinstance(item, str):
            compact.append(item)
            continue
        if not isinstance(item, dict):
            continue
        focus_id = item.get("focus_id")
        if not focus_id:
            continue
        aliases = item.get("aliases") or []
        bridge_family = item.get("bridge_family_v2") or item.get("bridge_family", "")
        compact.append(
            {
                "focus_id": focus_id,
                "bridge_family": bridge_family,
                "legacy_bridge_family": item.get("bridge_family", ""),
                "description": item.get("description", ""),
                "aliases": aliases[:8] if isinstance(aliases, list) else [],
            }
        )
    return compact


def _focus_registry_for_row(row: dict, focus_registry: list | None) -> list:
    if "available_known_focus" in row:
        return _compact_focus_registry(row.get("available_known_focus") or [])
    return _compact_focus_registry(focus_registry)


def _compact_context_line(label: str, value: str, max_chars: int = 1800) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "..."
    return f"{label}: {text}"


def _dialogue_to_text(messages: list | None) -> str:
    parts = []
    for item in messages or []:
        if not isinstance(item, dict):
            continue
        role = item.get("role") or "unknown"
        content = (item.get("content") or "").strip()
        if content:
            parts.append(f"{role}: {content}")
    return "\n".join(parts)


def build_messages_from_seed_row(row: dict) -> list[dict]:
    messages = [dict(message) for message in row.get("prior_messages", [])]
    context_lines = [
        _compact_context_line("题目编号/链接", row.get("problem_ref", ""), 300),
        _compact_context_line("题面/题意/约束", row.get("problem_context", ""), 1800),
    ]
    context_lines = [line for line in context_lines if line]
    student_message = row.get("student_message", "")
    if context_lines:
        content = "\n".join(
            [
                "[学生原始问题]",
                student_message,
                "",
                "[当前题目上下文：只用于离线研究诊断，不要直接照抄题解]",
                *context_lines,
                "",
                "请围绕学生当前卡点生成或评估渐进脚手架。",
            ]
        )
    else:
        content = student_message
    messages.append({"role": "user", "content": content})
    return messages


def _call_current_system_tutor(row: dict, messages: list[dict], chat_model_provider: str | None = None) -> dict:
    problem_ref = (row.get("problem_ref") or row.get("id") or "unknown_problem").strip()
    case_id = row.get("id") or problem_ref
    response_text, history_text, level = noi_agent_chat(
        messages,
        "bridge_offline_eval_student",
        f"{problem_ref}::{case_id}",
        chat_model_provider=chat_model_provider,
    )
    return {
        "baseline_group": "current_system",
        "tutor_mode": "current_system",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": response_text,
        "history_text": history_text,
        "level": level,
    }


def _enhanced_prompt_message() -> dict:
    return {
        "role": "assistant",
        "content": "\n".join(
            [
                "[Offline Enhanced Tutor Prompt - research control, not student text]",
                "你正在生成算法竞赛辅导回复，但这一组实验不给你具体 Bridge Contract。",
                "请遵守以下通用教学规则：",
                "1. 不要直接给完整题解或完整代码。",
                "2. 不要直接补完学生当前缺失的关键桥，例如完整状态定义、转移式、check 条件、边界更新、贪心准则或标记公式。",
                "3. 先根据学生话语判断当前最可能缺的桥，但不要输出内部标签。",
                "4. 使用 bridge-first, topic-second 原则：先按学生缺失的推理桥决定教学动作，算法名只作为上下文。",
                "5. 如果使用微型例子，先说明这个例子要观察的桥梁问题；给足够小的例子；只问一个局部问题；最后要求学生抽象成可迁移规则。",
                "6. 不要在微型例子里预填关键操作的一半再让学生补另一半。",
                "7. 只给一个清晰、可回答的下一步问题。",
                "8. 如果信息不足，先索取题面、代码、错误现象或学生已有尝试。",
                "9. 回复自然，不输出 JSON、[LEVEL:] 或内部评测字段。",
            ]
        ),
    }


def _call_enhanced_prompt_tutor(
    row: dict,
    messages: list[dict],
    bridge_result: dict,
    chat_model_provider: str | None = None,
) -> dict:
    enhanced_messages = (
        [*messages[:-1], _enhanced_prompt_message(), messages[-1]]
        if messages
        else [_enhanced_prompt_message()]
    )
    problem_ref = (row.get("problem_ref") or row.get("id") or "unknown_problem").strip()
    case_id = row.get("id") or row.get("case_id") or problem_ref
    response_text, history_text, level = noi_agent_chat(
        enhanced_messages,
        "bridge_offline_eval_student",
        f"{problem_ref}::{case_id}",
        chat_model_provider=chat_model_provider,
    )
    return {
        "baseline_group": "enhanced_prompt_only",
        "tutor_mode": "enhanced_prompt_only",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": response_text,
        "history_text": history_text,
        "level": level,
    }


def _default_tutor_fn(row: dict, messages: list[dict], bridge_result: dict) -> dict:
    return _call_current_system_tutor(row, messages)


def _make_default_tutor_fn(chat_model_provider: str | None) -> TutorFn:
    return lambda row, messages, bridge_result: _call_current_system_tutor(
        row,
        messages,
        chat_model_provider=chat_model_provider,
    )


def _bridge_contract_message(bridge_result: dict) -> dict:
    missing_bridge = bridge_result.get("missing_bridge") or {}
    contract = {
        "missing_bridge": {
            "family": missing_bridge.get("family", ""),
            "subtype": missing_bridge.get("subtype", ""),
            "known_focus": missing_bridge.get("known_focus", ""),
            "description": missing_bridge.get("description", ""),
        },
        "allowed_help_level": bridge_result.get("allowed_help_level", ""),
        "help_form": bridge_result.get("help_form", ""),
        "help_forms": _bridge_help_forms(bridge_result),
        "forbidden_content": bridge_result.get("forbidden_content") or [],
        "leakage_risk": bridge_result.get("leakage_risk", ""),
    }
    micro_example_policy = "\n".join(
        [
            "桥梁导向微型例子规则：",
            "如果 help_form/help_forms 包含 micro_example，微型例子不能只是让学生完成临时填空、选择题或计算任务。",
            "必须按四步组织：",
            "1. 先说明这个例子要观察的桥梁问题。",
            "2. 给一个足够小、但仍贴近原题的小例子。",
            "3. 只问一个局部、可回答的问题。",
            "4. 要求学生把观察抽象成一句可迁移规则。",
        ]
    )
    bridge_first_policy = "\n".join(
        [
            "bridge-first, topic-second 控制原则：",
            "1. 按 missing_bridge.family 控制教学动作，而不是按具体算法名套模板。",
            "2. 具体算法名只用于理解上下文和选择例子语言，不用于绕过 forbidden_content。",
            "3. 如果你想使用具体算法例子，必须先确认它服务于当前 bridge family，且不能补完整关键桥。",
        ]
    )
    return {
        "role": "assistant",
        "content": "\n".join(
            [
                "[Offline Bridge Contract - research control, not student text]",
                json.dumps(contract, ensure_ascii=False, indent=2),
                "请下一轮回复严格遵守 allowed_help_level 和 help_form，只补半步，不要出现 forbidden_content。",
                bridge_first_policy,
                micro_example_policy,
                "如果学生问的是“为什么/含义/原理”，可以先给一句简短概念解释，再用一个问题引导迁移；不要一次连续抛出多个问题。",
            ]
        ),
    }


def _call_bridge_contract_tutor(
    row: dict,
    messages: list[dict],
    bridge_result: dict,
    chat_model_provider: str | None = None,
) -> dict:
    if messages:
        contract_messages = [*messages[:-1], _bridge_contract_message(bridge_result), messages[-1]]
    else:
        contract_messages = [_bridge_contract_message(bridge_result)]
    problem_ref = (row.get("problem_ref") or row.get("id") or "unknown_problem").strip()
    case_id = row.get("id") or problem_ref
    response_text, history_text, level = noi_agent_chat(
        contract_messages,
        "bridge_offline_eval_student",
        f"{problem_ref}::{case_id}",
        chat_model_provider=chat_model_provider,
    )
    return {
        "baseline_group": "bridge_contract_tutor",
        "tutor_mode": "bridge_contract",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": response_text,
        "history_text": history_text,
        "level": level,
    }


def _single_llm_structured_system_prompt() -> str:
    turn_types = ", ".join(CONTRACT_TURN_TYPES)
    algorithm_topics_l1 = ", ".join(CONTRACT_ALGORITHM_TOPICS_L1)
    bridge_families = ", ".join(CONTRACT_BRIDGE_FAMILIES)
    help_forms = ", ".join(CONTRACT_HELP_FORMS)
    return "\n".join(
        [
            "你是算法竞赛 AI 辅导研究中的 single-LLM structured baseline。",
            "你必须一次性完成三件事：诊断本轮 compact bridge contract、生成学生可见回复、自检是否泄露关键桥。",
            "只输出 JSON，不要输出 Markdown 代码块，不要输出额外解释。",
            "所有 schema 字段必须使用英文枚举 key，不要输出中文自由标签。",
            "如果无法确定，输出 unknown，不要编造不存在的 focus 或 family。",
            "",
            "输出 schema：",
            "{",
            '  "runtime_bridge_contract": {',
            '    "turn_type": "one exact enum key",',
            '    "diagnosis_uncertainty": "low|medium|high|unknown",',
            '    "algorithm_topic_l1": "one exact enum key",',
            '    "algorithm_topic_l2": "short topic or unknown",',
            '    "primary_bridge_family": "one exact enum key",',
            '    "selected_focus_id": "one focus_id from top_k_registered_focus or unknown",',
            '    "selected_focus_confidence": 0.0,',
            '    "max_scaffold_level": "L0|L1|L2|L3",',
            '    "help_forms": ["最多两个英文 help form key"],',
            '    "forbidden_content": ["最多三条本轮不能直接补完的内容"],',
            '    "leakage_risk": "low|medium|high|unknown",',
            '    "confidence": 0.0',
            "  },",
            '  "student_response": "自然的学生可见回复，不要包含内部标签或 JSON",',
            '  "self_check": {',
            '    "predicted_leakage_risk": "low|medium|high|unknown",',
            '    "violated_forbidden_content": [],',
            '    "notes": "一句话说明"',
            "  }",
            "}",
            "",
            "严格枚举：",
            f"- turn_type 只能使用以下枚举值：{turn_types}",
            f"- algorithm_topic_l1 只能使用以下枚举值：{algorithm_topics_l1}",
            f"- primary_bridge_family 只能使用以下枚举值：{bridge_families}",
            f"- help_forms 每项只能使用以下英文 key，最多 2 个：{help_forms}",
            "- selected_focus_id 只能从后续 top_k_registered_focus 的 focus_id 里选择；如果没有合适项，写 unknown。",
            "- max_scaffold_level 只能是 L0、L1、L2、L3。",
            "- leakage_risk 只能是 low、medium、high、unknown。",
            "",
            "Prompt control policy: bridge-first, topic-second, focus-top-k.",
            "- 先用 primary_bridge_family 决定教学动作：问状态语义、转移来源、判定方向、依赖顺序、贡献汇总、数据结构操作、正确性不变量、复杂度瓶颈、实现边界或调试证据。",
            "- algorithm_topic 只作为轻量上下文，帮助你选择例子语言；不要用算法名覆盖 primary_bridge_family 的控制规则。",
            "- selected_focus_id 只能从 top_k_registered_focus 中选择，用来细化措辞；没有合适候选就写 unknown，不要编造具体算法 focus。",
            "- 不要试图覆盖所有具体算法，也不要因为 prompt 里出现过 DP、check、LCA 等例子，就把这些例子当作完整算法清单。",
            "- 具体算法例子只是 regression boundary，不是生成回复的主规则；遇到 KMP、Dijkstra、单调栈、区间 DP、lazy、滚动数组等未列举算法时，也先映射到抽象 bridge family。",
            "",
            "帮助强度校准：",
            "- L0：只澄清或索取证据，不给实质解题提示。适用于信息不足、没有题面、代码调试但没有代码/错误现象、完整代码/完整题解请求。",
            "- L1：轻提示，只给观察方向、约束追问或让学生表达已有想法。适用于算法名确认、关键桥直接索取、没有实质尝试且泄露风险高的情况。",
            "- L2：中提示。学生已经暴露明确卡点，且有足够题目上下文时，可以给微型例子、局部反例、半步关系、partial trace 或一个引导问题；仍不能补完当前关键桥。",
            "- L3：强提示。仅当学生已有 substantial attempt、局部代码、明确错误现象或接近完成时，才给局部 checklist、局部伪代码或代码诊断；仍不能给完整题解/完整代码。",
            "- 不要因为保守而把所有可诊断学习轮次都选成 L1；如果一个桥梁导向微型例子能保留关键桥让学生自己抽象，通常应选 L2。",
            "",
            "关键桥泄露校准：",
            "- 禁止内容不能包装成假设句或选择题答案。例如不要写“如果 dp 数组的格子代表……”，这等于直接给出状态语义。",
            "- 不要在微型例子里预填关键操作的一半再让学生补另一半；这仍可能泄露关键桥。应先让学生列出观察对象、影响因素或可行性判断，再让他自己提出关系。",
            "- 状态/表示类卡点：让学生自己说出状态格子应该记什么，可以问“哪些信息会影响后面的选择？”，不要替他定义 dp 含义。",
            "- 判定/check 类卡点：可以给小数据让学生判断可行性，不要直接告诉 true/false 对应哪一侧边界。",
            "- 汇总/贡献类卡点：可以问单条路径上哪些位置会贡献，不要直接给端点/LCA 的完整加减公式。",
            "- 如果 student_response 直接或变相说出了 forbidden_content，self_check 必须标为 medium 或 high，并把命中的内容写入 violated_forbidden_content。",
            "",
            "教学约束：",
            "- 不要直接给完整题解或完整代码。",
            "- 不要直接补完学生当前缺失的关键桥。",
            "- 如果给微型例子，必须先说明要观察的桥梁问题，再让学生抽象出可迁移规则。",
            "- 只问一个清晰、可回答的问题。",
            "- `student_response` 中不要出现 [LEVEL:] 或内部评测字段。",
        ]
    )


def _single_llm_candidate_message(candidate_retrieval: dict | None) -> dict | None:
    if not candidate_retrieval:
        return None
    compact_payload = {
        "top_k_algorithm_topics": candidate_retrieval.get("algorithm_topic_candidates") or [],
        "top_k_registered_focus": candidate_retrieval.get("focus_candidates") or [],
        "selection_rules": [
            "selected_focus_id must be one focus_id from top_k_registered_focus, or unknown.",
            "Do not invent focus ids.",
            "Use English enum keys for schema fields.",
        ],
    }
    return {
        "role": "assistant",
        "content": "\n".join(
            [
                "[Offline Single-LLM Candidate Set - research control, not student text]",
                json.dumps(compact_payload, ensure_ascii=False, indent=2),
            ]
        ),
    }


def _validate_single_llm_structured_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("single_llm_structured payload must be an object")
    contract = payload.get("runtime_bridge_contract")
    if not isinstance(contract, dict):
        raise ValueError("runtime_bridge_contract must be an object")
    student_response = payload.get("student_response")
    if not isinstance(student_response, str) or not student_response.strip():
        raise ValueError("student_response must be a non-empty string")
    self_check = payload.get("self_check")
    if not isinstance(self_check, dict):
        raise ValueError("self_check must be an object")
    contract["help_forms"] = [item for item in contract.get("help_forms") or [] if isinstance(item, str)][:2]
    contract["forbidden_content"] = [
        item for item in contract.get("forbidden_content") or [] if isinstance(item, str)
    ][:3]
    payload["runtime_bridge_contract"] = contract
    payload["student_response"] = student_response.strip()
    payload["self_check"] = self_check
    return payload


def _call_single_llm_structured_tutor(
    row: dict,
    messages: list[dict],
    bridge_result: dict,
    chat_model_provider: str | None = None,
) -> dict:
    candidate_message = _single_llm_candidate_message(bridge_result.get("candidate_retrieval"))
    if candidate_message and messages:
        messages = [*messages[:-1], candidate_message, messages[-1]]
    elif candidate_message:
        messages = [candidate_message]
    response = _chat_completion_create(
        system_prompt=_single_llm_structured_system_prompt(),
        messages=messages,
        provider_id=chat_model_provider,
    )
    payload = _validate_single_llm_structured_payload(
        _extract_json_object(response.choices[0].message.content)
    )
    return {
        "baseline_group": "single_llm_structured",
        "tutor_mode": "single_llm_structured",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": payload["student_response"],
        "history_text": payload["student_response"],
        "level": payload["runtime_bridge_contract"].get("max_scaffold_level", ""),
        "runtime_bridge_contract": payload["runtime_bridge_contract"],
        "self_check": payload["self_check"],
    }


def _dbox_inspired_decomposition_system_prompt() -> str:
    return "\n".join(
        [
            "你是算法竞赛 AI 辅导研究中的 DBox-inspired decomposition baseline。",
            "This is a DBox-inspired, single-turn, step-tree-style decomposition tutor, not a reproduction of DBox.",
            "你的任务是把学生当前的大问题拆成一个更小的当前子步骤，只给 first-level 的分解式脚手架。",
            "只输出 JSON，不要输出 Markdown 代码块，不要输出额外解释。",
            "",
            "输出 schema：",
            "{",
            '  "baseline_group": "literature_inspired_decomposition",',
            '  "decomposition_view": [',
            '    {"step_id": "s1", "step_name": "short step name", "status": "known_or_not_relevant"},',
            '    {"step_id": "s2", "step_name": "short step name", "status": "current_stuck_step"},',
            '    {"step_id": "s3", "step_name": "short step name", "status": "defer"}',
            "  ],",
            '  "current_substep": "one small substep the student should complete now",',
            '  "hint_level": "general_question",',
            '  "student_visible_response": "自然的学生可见回复，不要包含内部标签或 JSON"',
            "}",
            "",
            "Hard constraints:",
            "- step-tree-style decomposition: internally form a small step view with known/defer/current-stuck parts.",
            "- DBox material anchor: original DBox prompts use node signals such as correct/incorrect/missing and can/cannot be further divided; adapt these only into the compact statuses above.",
            "- DBox hint anchor: use only the spirit of `general_hint`, meaning a question-form general guide.",
            "- Do not use DBox reveal-like fields in student-visible text: no `detailed_hint`, no `correctStep`, no `correct_code`, no pseudocode.",
            "- only one current substep: exactly one decomposition_view item must have status current_stuck_step.",
            "- first-level hint only: use a general hint, guiding question, or decomposition micro-task.",
            "- no reveal substep: do not reveal the exact missing substep answer.",
            "- no reveal code: do not provide code, pseudocode, or implementation templates.",
            "- no full solution / full code.",
            "- no direct critical bridge completion.",
            "- no full state definition, full recurrence, full check condition, or full boundary update rule.",
            "- do not display a complete step tree answer to the student.",
            "",
            "学生可见回复要求：",
            "- 只围绕当前一个子步骤，不要同时问多个问题。",
            "- 帮学生把当前大问题缩小为一个可回答的小问题。",
            "- 可以给一个很小的 micro-task 或观察问题，但不要替学生完成关键桥。",
            "- 要让学生自己补完当前 substep，并说出理由或观察。",
            "- 如果学生直接要完整代码/完整题解，只做澄清或安全引导，不给实质解法。",
            "- 不要说你复现了 DBox；这只是单轮 DBox-inspired baseline。",
        ]
    )


def _validate_dbox_inspired_decomposition_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("dbox_inspired_decomposition payload must be an object")
    if payload.get("baseline_group") != "literature_inspired_decomposition":
        raise ValueError("baseline_group must be literature_inspired_decomposition")
    decomposition_view = payload.get("decomposition_view")
    if not isinstance(decomposition_view, list) or not decomposition_view:
        raise ValueError("decomposition_view must be a non-empty list")
    status_aliases = {
        "known_or_not_relevant": "known_or_not_relevant",
        "known": "known_or_not_relevant",
        "known_or_relevant": "known_or_not_relevant",
        "not_relevant": "known_or_not_relevant",
        "current_stuck_step": "current_stuck_step",
        "current": "current_stuck_step",
        "current_substep": "current_stuck_step",
        "current_step": "current_stuck_step",
        "stuck": "current_stuck_step",
        "missing": "current_stuck_step",
        "defer": "defer",
        "deferred": "defer",
        "future": "defer",
        "later": "defer",
    }
    normalized_view = []
    current_count = 0
    for index, item in enumerate(decomposition_view, 1):
        if not isinstance(item, dict):
            raise ValueError("each decomposition_view item must be an object")
        step_id = item.get("step_id")
        step_name = item.get("step_name")
        raw_status = item.get("status")
        status = status_aliases.get(str(raw_status).strip().lower()) if raw_status is not None else None
        if not isinstance(step_id, str) or not step_id.strip():
            raise ValueError("each decomposition_view item needs a step_id")
        if not isinstance(step_name, str) or not step_name.strip():
            raise ValueError("each decomposition_view item needs a step_name")
        if status is None:
            raise ValueError(f"invalid decomposition status at item {index}: {raw_status}")
        if status == "current_stuck_step":
            current_count += 1
        normalized_view.append(
            {
                "step_id": step_id.strip(),
                "step_name": step_name.strip(),
                "status": status,
            }
        )
    if current_count != 1:
        raise ValueError("decomposition_view must contain exactly one current_stuck_step")
    current_substep = payload.get("current_substep")
    if not isinstance(current_substep, str) or not current_substep.strip():
        raise ValueError("current_substep must be a non-empty string")
    if payload.get("hint_level") != "general_question":
        raise ValueError("hint_level must be general_question")
    student_response = payload.get("student_visible_response")
    if not isinstance(student_response, str) or not student_response.strip():
        raise ValueError("student_visible_response must be a non-empty string")
    return {
        "baseline_group": "literature_inspired_decomposition",
        "decomposition_view": normalized_view,
        "current_substep": current_substep.strip(),
        "hint_level": "general_question",
        "student_visible_response": student_response.strip(),
    }


def _call_dbox_inspired_decomposition_tutor(
    row: dict,
    messages: list[dict],
    bridge_result: dict,
    chat_model_provider: str | None = None,
) -> dict:
    response = _chat_completion_create(
        system_prompt=_dbox_inspired_decomposition_system_prompt(),
        messages=messages,
        provider_id=chat_model_provider,
    )
    payload = _validate_dbox_inspired_decomposition_payload(
        _extract_json_object(response.choices[0].message.content)
    )
    student_response = payload["student_visible_response"]
    return {
        "baseline_group": "literature_inspired_decomposition",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": student_response,
        "history_text": student_response,
        "level": "L1",
        "decomposition_view": payload["decomposition_view"],
        "current_substep": payload["current_substep"],
        "hint_level": payload["hint_level"],
        "dbox_inspired_decomposition_result": payload,
    }


def _codehelp_codeaid_no_direct_solution_system_prompt() -> str:
    return "\n".join(
        [
            "你是算法竞赛 AI 辅导研究中的 CodeHelp / CodeAid inspired no-direct-solution baseline。",
            "This is a literature-adapted no-direct-solution tutor, not a reproduction of CodeHelp or CodeAid.",
            "目标：给有帮助、技术上可信、可执行的下一步，但不直接泄露完整解法、完整代码或当前关键中间推理。",
            "只输出 JSON，不要输出 Markdown 代码块，不要输出额外解释。",
            "",
            "输出 schema：",
            "{",
            '  "baseline_group": "literature_inspired_guardrail",',
            '  "student_visible_response": "自然的学生可见回复，不要包含内部标签或 JSON",',
            '  "self_check": {',
            '    "reveals_full_solution": false,',
            '    "reveals_full_code": false,',
            '    "reveals_critical_bridge": false',
            "  }",
            "}",
            "",
            "Hard constraints:",
            "- no-direct-solution: do not provide a complete solution.",
            "- no full solution.",
            "- no full code.",
            "- no direct algorithm confirmation when the student only asks for the algorithm name.",
            "- do not reveal the critical intermediate reasoning that the student is currently missing.",
            "- do not complete full state definitions, recurrences, check conditions, boundary update rules, or local code lines.",
            "- do not ask for exact operations on u/v/LCA, true/false boundary directions, or other answer-bearing slots when that is the missing bridge; ask for an observation from a tiny example instead.",
            "- provide at most one actionable next step.",
            "- prefer conceptual guidance, debugging direction, evidence requests, or a small question.",
            "- if context is insufficient, ask for the missing problem/code/error evidence instead of guessing.",
        ]
    )


def _socratic_no_answer_system_prompt() -> str:
    return "\n".join(
        [
            "你是算法竞赛 AI 辅导研究中的 Socratic/no-answer literature baseline。",
            "This is a Socratic no-answer tutor baseline inspired by tutoring-dialogue scaffolding, not a reproduction of MathDial.",
            "目标：只用一个问题或一个极轻的追问帮助学生继续思考，不直接给答案。",
            "只输出 JSON，不要输出 Markdown 代码块，不要输出额外解释。",
            "",
            "输出 schema：",
            "{",
            '  "baseline_group": "literature_inspired_socratic",',
            '  "question_intent": "what this question is trying to make the student reason about",',
            '  "student_visible_response": "自然的学生可见回复，只包含一个清晰问题或极轻提示"',
            "}",
            "",
            "Hard constraints:",
            "- no-answer: do not provide the final answer, formula, algorithm confirmation, code, or complete reasoning step.",
            "- one question: ask at most one clear, answerable question.",
            "- do not state the missing bridge; make the student articulate it.",
            "- no formula-like decomposition: do not state relations such as path = root-path combination, recurrence equations, check direction rules, or contribution formulas.",
            "- do not mention parent/neighbor of LCA or any equivalent exact compensation node unless the student has already stated it.",
            "- do not ask for exact operations on u/v/LCA, true/false boundary directions, or other answer-bearing slots when that is the missing bridge; ask for a neutral observation from a tiny example instead.",
            "- for tree path marking/difference cases, do not pre-fill endpoint marks or ask where to subtract; ask the student to first shade one tiny path and compare which nodes should be counted.",
            "- for tree path marking/difference cases, do not mention +1/-1, endpoint marks, subtract marks, or any mark location; only ask the student to identify the path nodes and what the final aggregate should count.",
            "- keep question_intent generic; it must not contain the answer formula, exact forbidden completion, or answer-bearing slot list.",
            "- do not include multiple-choice answers if one option reveals the critical bridge.",
            "- if the student asks for full solution/code, ask for current attempt or evidence instead.",
            "- keep the response short and student-facing; do not output internal labels.",
        ]
    )


def _validate_socratic_no_answer_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("socratic_no_answer payload must be an object")
    if payload.get("baseline_group") != "literature_inspired_socratic":
        raise ValueError("baseline_group must be literature_inspired_socratic")
    question_intent = payload.get("question_intent")
    if not isinstance(question_intent, str) or not question_intent.strip():
        raise ValueError("question_intent must be a non-empty string")
    student_response = payload.get("student_visible_response")
    if not isinstance(student_response, str) or not student_response.strip():
        raise ValueError("student_visible_response must be a non-empty string")
    return {
        "baseline_group": "literature_inspired_socratic",
        "question_intent": question_intent.strip(),
        "student_visible_response": student_response.strip(),
    }


def _call_socratic_no_answer_tutor(
    row: dict,
    messages: list[dict],
    bridge_result: dict,
    chat_model_provider: str | None = None,
) -> dict:
    response = _chat_completion_create(
        system_prompt=_socratic_no_answer_system_prompt(),
        messages=messages,
        provider_id=chat_model_provider,
    )
    payload = _validate_socratic_no_answer_payload(_extract_json_object(response.choices[0].message.content))
    student_response = payload["student_visible_response"]
    return {
        "baseline_group": "literature_inspired_socratic",
        "tutor_mode": "socratic_no_answer_tutor",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": student_response,
        "history_text": student_response,
        "level": "L1",
        "socratic_no_answer_result": payload,
    }


def _validate_codehelp_codeaid_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("codehelp_codeaid payload must be an object")
    if payload.get("baseline_group") != "literature_inspired_guardrail":
        raise ValueError("baseline_group must be literature_inspired_guardrail")
    student_response = payload.get("student_visible_response")
    if not isinstance(student_response, str) or not student_response.strip():
        raise ValueError("student_visible_response must be a non-empty string")
    self_check = payload.get("self_check")
    if not isinstance(self_check, dict):
        raise ValueError("self_check must be an object")
    normalized_check = {
        "reveals_full_solution": bool(self_check.get("reveals_full_solution", False)),
        "reveals_full_code": bool(self_check.get("reveals_full_code", False)),
        "reveals_critical_bridge": bool(self_check.get("reveals_critical_bridge", False)),
    }
    return {
        "baseline_group": "literature_inspired_guardrail",
        "student_visible_response": student_response.strip(),
        "self_check": normalized_check,
    }


def _call_codehelp_codeaid_no_direct_solution_tutor(
    row: dict,
    messages: list[dict],
    bridge_result: dict,
    chat_model_provider: str | None = None,
) -> dict:
    response = _chat_completion_create(
        system_prompt=_codehelp_codeaid_no_direct_solution_system_prompt(),
        messages=messages,
        provider_id=chat_model_provider,
    )
    payload = _validate_codehelp_codeaid_payload(_extract_json_object(response.choices[0].message.content))
    student_response = payload["student_visible_response"]
    return {
        "baseline_group": "literature_inspired_guardrail",
        "tutor_mode": "codehelp_codeaid_no_direct_solution_tutor",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": student_response,
        "history_text": student_response,
        "level": "L1",
        "self_check": payload["self_check"],
        "codehelp_codeaid_result": payload,
    }


def _bridge_inspired_expert_decision_system_prompt() -> str:
    return "\n".join(
        [
            "你是算法竞赛 AI 辅导研究中的 Bridge-inspired expert-decision baseline。",
            "This is inspired by expert decision injection, not a CP-specific Bridge Contract and not a reproduction of the Bridge paper.",
            "你需要先内部显式化三个通用教学决策，再生成学生可见回复。",
            "只输出 JSON，不要输出 Markdown 代码块，不要输出额外解释。",
            "",
            "输出 schema：",
            "{",
            '  "baseline_group": "literature_inspired_expert_decision",',
            '  "student_error_or_gap": "what the student appears to be missing or misunderstanding",',
            '  "remediation_strategy": "generic tutoring strategy, not a CP bridge label",',
            '  "teaching_intention": "what the next response is trying to accomplish",',
            '  "student_visible_response": "自然的学生可见回复，不要包含内部标签或 JSON"',
            "}",
            "",
            "Hard constraints:",
            "- keep the decision fields generic: student_error_or_gap, remediation_strategy, teaching_intention.",
            "- do not output missing_bridge, bridge_family, registered_focus_id, or forbidden_content as if this were our Bridge Contract.",
            "- ask at most one focused question or give one next action.",
            "- do not give a full solution or full code.",
            "- do not directly complete the student's current critical reasoning step.",
            "- no formula-like decomposition: do not state relations such as path = root-path combination, recurrence equations, check direction rules, or contribution formulas.",
            "- do not mention parent/neighbor of LCA or any equivalent exact compensation node unless the student has already stated it.",
            "- keep analogies at the observation level; do not turn an analogy into the missing formula.",
            "- if the student asks for algorithm confirmation, avoid direct confirmation and ask for a constraint/attempt signal.",
        ]
    )


def _validate_bridge_inspired_expert_decision_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("bridge_inspired_expert_decision payload must be an object")
    if payload.get("baseline_group") != "literature_inspired_expert_decision":
        raise ValueError("baseline_group must be literature_inspired_expert_decision")
    required = [
        "student_error_or_gap",
        "remediation_strategy",
        "teaching_intention",
        "student_visible_response",
    ]
    normalized = {"baseline_group": "literature_inspired_expert_decision"}
    for key in required:
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")
        normalized[key] = value.strip()
    return normalized


def _call_bridge_inspired_expert_decision_tutor(
    row: dict,
    messages: list[dict],
    bridge_result: dict,
    chat_model_provider: str | None = None,
) -> dict:
    response = _chat_completion_create(
        system_prompt=_bridge_inspired_expert_decision_system_prompt(),
        messages=messages,
        provider_id=chat_model_provider,
    )
    payload = _validate_bridge_inspired_expert_decision_payload(
        _extract_json_object(response.choices[0].message.content)
    )
    student_response = payload["student_visible_response"]
    return {
        "baseline_group": "literature_inspired_expert_decision",
        "tutor_mode": "bridge_inspired_expert_decision_tutor",
        "tutor_model_provider": chat_model_provider or "default",
        "response_text": student_response,
        "history_text": student_response,
        "level": "L1",
        "expert_decision_result": payload,
    }


def _make_tutor_fn(tutor_mode: str, chat_model_provider: str | None) -> TutorFn:
    if tutor_mode == "bridge_contract":
        return lambda row, messages, bridge_result: _call_bridge_contract_tutor(
            row,
            messages,
            bridge_result,
            chat_model_provider=chat_model_provider,
        )
    if tutor_mode == "single_llm_structured":
        return lambda row, messages, bridge_result: _call_single_llm_structured_tutor(
            row,
            messages,
            bridge_result,
            chat_model_provider=chat_model_provider,
        )
    if tutor_mode == "enhanced_prompt_only":
        return lambda row, messages, bridge_result: _call_enhanced_prompt_tutor(
            row,
            messages,
            bridge_result,
            chat_model_provider=chat_model_provider,
        )
    if tutor_mode == "dbox_inspired_decomposition_tutor":
        return lambda row, messages, bridge_result: _call_dbox_inspired_decomposition_tutor(
            row,
            messages,
            bridge_result,
            chat_model_provider=chat_model_provider,
        )
    if tutor_mode == "codehelp_codeaid_no_direct_solution_tutor":
        return lambda row, messages, bridge_result: _call_codehelp_codeaid_no_direct_solution_tutor(
            row,
            messages,
            bridge_result,
            chat_model_provider=chat_model_provider,
        )
    if tutor_mode == "socratic_no_answer_tutor":
        return lambda row, messages, bridge_result: _call_socratic_no_answer_tutor(
            row,
            messages,
            bridge_result,
            chat_model_provider=chat_model_provider,
        )
    if tutor_mode == "bridge_inspired_expert_decision_tutor":
        return lambda row, messages, bridge_result: _call_bridge_inspired_expert_decision_tutor(
            row,
            messages,
            bridge_result,
            chat_model_provider=chat_model_provider,
        )
    return _make_default_tutor_fn(chat_model_provider)


def _make_bridge_judge_fn(judge_provider: str) -> BridgeJudgeFn:
    return bridge_judge_v1


def _make_leakage_judge_fn(judge_provider: str) -> LeakageJudgeFn:
    return leakage_judge_v1


def _make_repair_fn(judge_provider: str) -> RepairFn:
    return repair_response_v1


def _call_with_optional_judge_provider(fn: Callable, kwargs: dict, judge_provider: str) -> dict:
    signature = inspect.signature(fn)
    accepts_var_kwargs = any(
        param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values()
    )
    accepts_provider = "judge_provider" in signature.parameters or accepts_var_kwargs
    if not accepts_var_kwargs:
        kwargs = {key: value for key, value in kwargs.items() if key in signature.parameters}
    if accepts_provider:
        return fn(**kwargs, judge_provider=judge_provider)
    return fn(**kwargs)


def _call_stage_with_retries(
    fn: Callable,
    kwargs: dict,
    *,
    judge_provider: str,
    max_retries: int,
) -> tuple[dict, int]:
    retry_count = 0
    while True:
        result = _call_with_optional_judge_provider(fn, kwargs, judge_provider)
        if not result.get("_failed") or retry_count >= max_retries:
            return result, retry_count
        retry_count += 1


def _bridge_help_forms(bridge_result: dict) -> list[str]:
    help_forms = bridge_result.get("help_forms")
    if isinstance(help_forms, list):
        return [item for item in help_forms if isinstance(item, str) and item.strip()]
    help_form = bridge_result.get("help_form")
    return [help_form] if isinstance(help_form, str) and help_form.strip() else []


def _case_gold(row: dict) -> dict:
    return {
        "student_state": row.get("gold_student_state", ""),
        "bridge_family": row.get("gold_bridge_family", ""),
        "known_focus": row.get("gold_known_focus", ""),
        "help_seeking_type": row.get("gold_help_seeking_type", ""),
        "missing_link": row.get("gold_missing_link", ""),
        "allowed_help_level": row.get("gold_allowed_help_level", ""),
        "forbidden_completion": row.get("gold_forbidden_completion", ""),
        "needs_new_focus": bool(row.get("needs_new_focus", False)),
    }


def _confidence_to_uncertainty(confidence: float | int | None) -> str:
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        return "unknown"
    if confidence >= 0.8:
        return "low"
    if confidence >= 0.6:
        return "medium"
    return "high"


def _first_topic(candidates: list[dict] | None) -> dict:
    if candidates:
        return candidates[0]
    return {"topic_l1": "unknown", "topic_l2": "unknown"}


def _runtime_bridge_contract_from_result(
    bridge_result: dict,
    *,
    algorithm_topic_candidates: list[dict] | None = None,
) -> dict:
    existing = bridge_result.get("runtime_bridge_contract")
    if isinstance(existing, dict):
        contract = dict(existing)
    else:
        missing_bridge = bridge_result.get("missing_bridge") or {}
        topic = _first_topic(algorithm_topic_candidates)
        focus_id = missing_bridge.get("known_focus") or bridge_result.get("selected_focus_id") or "unknown"
        confidence = bridge_result.get("confidence")
        contract = {
            "turn_type": bridge_result.get("turn_type") or "diagnosable_learning_turn",
            "diagnosis_uncertainty": bridge_result.get("diagnosis_uncertainty")
            or _confidence_to_uncertainty(confidence),
            "algorithm_topic_l1": topic.get("topic_l1") or "unknown",
            "algorithm_topic_l2": topic.get("topic_l2") or "unknown",
            "primary_bridge_family": missing_bridge.get("family")
            or bridge_result.get("primary_bridge_family")
            or "unknown_or_not_applicable",
            "selected_focus_id": focus_id,
            "selected_focus_confidence": confidence if isinstance(confidence, (int, float)) else 0,
            "max_scaffold_level": bridge_result.get("allowed_help_level")
            or bridge_result.get("max_scaffold_level")
            or "L1",
            "help_forms": _bridge_help_forms(bridge_result)[:2],
            "forbidden_content": list(bridge_result.get("forbidden_content") or [])[:3],
            "leakage_risk": bridge_result.get("leakage_risk") or "unknown",
            "confidence": confidence if isinstance(confidence, (int, float)) else 0,
        }
    contract["help_forms"] = list(contract.get("help_forms") or [])[:2]
    contract["forbidden_content"] = list(contract.get("forbidden_content") or [])[:3]
    return contract


def _bridge_result_from_runtime_contract(contract: dict) -> dict:
    return {
        "turn_type": contract.get("turn_type") or "unknown",
        "diagnosis_uncertainty": contract.get("diagnosis_uncertainty") or "unknown",
        "missing_bridge": {
            "family": contract.get("primary_bridge_family") or "unknown_or_not_applicable",
            "subtype": "",
            "description": contract.get("missing_bridge_summary", ""),
            "evidence": [],
            "known_focus": contract.get("selected_focus_id") or "unknown",
            "needs_new_focus": contract.get("selected_focus_id") in {None, "", "unknown"},
        },
        "allowed_help_level": contract.get("max_scaffold_level") or "L1",
        "help_forms": list(contract.get("help_forms") or [])[:2],
        "forbidden_content": list(contract.get("forbidden_content") or [])[:3],
        "leakage_risk": contract.get("leakage_risk") or "unknown",
        "confidence": contract.get("confidence") if isinstance(contract.get("confidence"), (int, float)) else 0,
        "runtime_bridge_contract": contract,
    }


def _estimate_tokens_from_payload(payload: object) -> int:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return max(1, round(len(text) / 4))


def _build_candidate_retrieval(
    row: dict,
    *,
    focus_registry: list | None,
) -> dict:
    student_message = row.get("student_message", "")
    problem_context = row.get("problem_context", "")
    topic_candidates = retrieve_algorithm_topic_candidates(
        student_message=student_message,
        problem_context=problem_context,
        limit=5,
    )
    focus_candidates = retrieve_focus_candidates(
        student_message=student_message,
        problem_context=problem_context,
        algorithm_topic_candidates=topic_candidates,
        focus_registry=focus_registry,
        limit=5,
    )
    return {
        "algorithm_topic_candidates": topic_candidates,
        "focus_candidates": focus_candidates,
        "focus_candidate_ids": [candidate.get("focus_id", "") for candidate in focus_candidates],
    }


def _write_progress(progress_stream, event: str, **fields) -> None:
    if progress_stream is None:
        return
    line = " ".join([event] + [f"{key}={value}" for key, value in fields.items()])
    progress_stream.write(line + "\n")
    flush = getattr(progress_stream, "flush", None)
    if callable(flush):
        flush()


def _finish_case_result(
    result: dict,
    *,
    latency_ms: dict[str, float],
    stage_errors: dict[str, str],
    total_start: float,
) -> dict:
    latency_ms["total_latency_ms"] = round((time.perf_counter() - total_start) * 1000, 3)
    result["latency_ms"] = latency_ms
    result["stage_errors"] = stage_errors
    result.setdefault("retry_count", 0)
    result.setdefault("candidate_response_text", "")
    result.setdefault("final_response_text", "")
    result.setdefault("final_response_source", "none")
    result.setdefault("repair_applied", False)
    result.setdefault("blocked", False)
    result.setdefault("llm_call_count", 0)
    return result


def _record_latency(latency_ms: dict[str, float], key: str, start: float) -> None:
    latency_ms[key] = round((time.perf_counter() - start) * 1000, 3)


def _add_llm_calls(result: dict, count: int = 1) -> None:
    result["llm_call_count"] = int(result.get("llm_call_count") or 0) + count


def _effective_chat_thinking_mode(chat_thinking_mode: str | None) -> str:
    return (chat_thinking_mode or os.environ.get("NOI_CHAT_THINKING_MODE") or "profile_default").strip()


@contextmanager
def _temporary_chat_thinking_mode(chat_thinking_mode: str | None):
    if not chat_thinking_mode:
        yield
        return
    previous = os.environ.get("NOI_CHAT_THINKING_MODE")
    os.environ["NOI_CHAT_THINKING_MODE"] = chat_thinking_mode
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("NOI_CHAT_THINKING_MODE", None)
        else:
            os.environ["NOI_CHAT_THINKING_MODE"] = previous


def _run_one_bridge_offline_case(
    row: dict,
    *,
    bridge_judge_fn: BridgeJudgeFn,
    tutor_fn: TutorFn,
    leakage_judge_fn: LeakageJudgeFn,
    repair_fn: RepairFn,
    chat_model_provider: str | None,
    focus_registry: list | None,
    guard_mode: str,
    tutor_mode: str,
    pipeline_mode: str,
    judge_schema_mode: str,
    judge_provider: str,
    max_retries: int,
    chat_thinking_mode: str | None,
) -> dict:
    total_start = time.perf_counter()
    latency_ms: dict[str, float] = {}
    stage_errors: dict[str, str] = {}
    messages = build_messages_from_seed_row(row)
    student_message = row.get("student_message", "")
    problem_context = {
        "problem_ref": row.get("problem_ref", ""),
        "summary": row.get("problem_context", ""),
    }
    case_id = row.get("id") or row.get("case_id") or ""
    result = {
        "case_id": case_id,
        "problem_ref": row.get("problem_ref", ""),
        "topic": row.get("topic", ""),
        "student_message": student_message,
        "problem_context": row.get("problem_context", ""),
        "recent_dialogue": _dialogue_to_text(row.get("prior_messages") or row.get("recent_dialogue")),
        "student_code_excerpt": row.get("student_code") or row.get("student_code_excerpt") or "",
        "tutor_mode": tutor_mode,
        "guard_mode": guard_mode,
        "pipeline_mode": pipeline_mode,
        "judge_schema_mode": judge_schema_mode,
        "focus_registry_size": len(_focus_registry_for_row(row, focus_registry)),
        "models": {
            "judge_model": _judge_model_name(judge_provider),
            "judge_provider": judge_provider,
            "tutor_model_provider": chat_model_provider or "default",
            "chat_thinking_mode": _effective_chat_thinking_mode(chat_thinking_mode),
            "tutor_mode": tutor_mode,
            "guard_mode": guard_mode,
            "pipeline_mode": pipeline_mode,
            "judge_schema_mode": judge_schema_mode,
        },
        "gold": _case_gold(row),
        "llm_call_count": 0,
    }

    single_llm_structured = tutor_mode == "single_llm_structured"
    available_focus = _focus_registry_for_row(row, focus_registry)
    candidate_retrieval = None
    bridge_result: dict = {}
    skip_bridge_diagnosis = pipeline_mode == "tutor_only_no_diagnosis"
    if judge_schema_mode == "retrieval_augmented_compact_judge" and not skip_bridge_diagnosis:
        stage_start = time.perf_counter()
        candidate_retrieval = _build_candidate_retrieval(row, focus_registry=available_focus)
        _record_latency(latency_ms, "candidate_retrieval_latency_ms", stage_start)
        result["candidate_retrieval"] = candidate_retrieval
        if single_llm_structured:
            bridge_result["candidate_retrieval"] = candidate_retrieval

    if not single_llm_structured and not skip_bridge_diagnosis:
        stage_start = time.perf_counter()
        try:
            bridge_kwargs = {
                "student_message": student_message,
                "messages": messages,
                "problem_context": problem_context,
                "student_code": row.get("student_code"),
                "available_known_focus": (candidate_retrieval or {}).get("focus_candidates") or available_focus,
            }
            if candidate_retrieval:
                bridge_kwargs.update(
                    {
                        "top_k_algorithm_topics": candidate_retrieval["algorithm_topic_candidates"],
                        "top_k_registered_focus": candidate_retrieval["focus_candidates"],
                    }
                )
            bridge_result, bridge_retries = _call_stage_with_retries(
                bridge_judge_fn,
                bridge_kwargs,
                judge_provider=judge_provider,
                max_retries=max_retries,
            )
            _add_llm_calls(result, 1 + bridge_retries)
            result["retry_count"] = bridge_retries
        except Exception as exc:
            _add_llm_calls(result)
            _record_latency(latency_ms, "bridge_judge_latency_ms", stage_start)
            stage_errors["bridge_judge"] = f"{type(exc).__name__}: {exc}"
            result["error"] = "bridge_judge_exception"
            return _finish_case_result(
                result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start
            )
        _record_latency(latency_ms, "bridge_judge_latency_ms", stage_start)
        result["bridge_judge_result"] = bridge_result
        if bridge_result.get("_failed"):
            stage_errors["bridge_judge"] = str(
                bridge_result.get("_error") or bridge_result.get("_reason") or "_failed"
            )
            result["error"] = "bridge_judge_failed"
            return _finish_case_result(
                result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start
            )

    if not single_llm_structured and not skip_bridge_diagnosis and judge_schema_mode != "full_schema_judge":
        result["runtime_bridge_contract"] = _runtime_bridge_contract_from_result(
            bridge_result,
            algorithm_topic_candidates=(candidate_retrieval or {}).get("algorithm_topic_candidates"),
        )
    result["prompt_budget_estimate"] = {
        "total_prompt_tokens_estimate": _estimate_tokens_from_payload(
            {
                "student_message": student_message,
                "problem_context": problem_context,
                "candidate_retrieval": candidate_retrieval or {},
                "runtime_bridge_contract": result.get("runtime_bridge_contract", {}),
            }
        )
    }

    if pipeline_mode == "diagnosis_only":
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)

    stage_start = time.perf_counter()
    tutor_retries = 0
    while True:
        try:
            with _temporary_chat_thinking_mode(chat_thinking_mode):
                tutor_result = tutor_fn(row, messages, bridge_result)
            _add_llm_calls(result)
            result["retry_count"] = result.get("retry_count", 0) + tutor_retries
            break
        except Exception as exc:
            _add_llm_calls(result)
            if tutor_retries >= max_retries:
                result["retry_count"] = result.get("retry_count", 0) + tutor_retries
                _record_latency(latency_ms, "tutor_latency_ms", stage_start)
                stage_errors["tutor"] = f"{type(exc).__name__}: {exc}"
                result["error"] = "tutor_exception"
                return _finish_case_result(
                    result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start
                )
            tutor_retries += 1
    _record_latency(latency_ms, "tutor_latency_ms", stage_start)
    result["tutor_response"] = tutor_result
    result["baseline_group"] = tutor_result.get("baseline_group", tutor_mode)
    candidate_response = tutor_result.get("response_text", "")
    result["candidate_response_text"] = candidate_response
    result["final_response_text"] = candidate_response
    result["final_response_source"] = "candidate"
    if single_llm_structured:
        contract = tutor_result.get("runtime_bridge_contract") or {}
        result["runtime_bridge_contract"] = contract
        result["single_llm_structured_result"] = {
            "runtime_bridge_contract": contract,
            "student_response": candidate_response,
            "self_check": tutor_result.get("self_check") or {},
        }
        bridge_result = _bridge_result_from_runtime_contract(contract)
        result["bridge_judge_result"] = {}
    if tutor_mode == "dbox_inspired_decomposition_tutor":
        result["decomposition_view"] = tutor_result.get("decomposition_view") or []
        result["current_substep"] = tutor_result.get("current_substep") or ""
        result["hint_level"] = tutor_result.get("hint_level") or ""
        result["dbox_inspired_decomposition_result"] = (
            tutor_result.get("dbox_inspired_decomposition_result") or {}
        )
    if tutor_mode == "codehelp_codeaid_no_direct_solution_tutor":
        result["codehelp_codeaid_result"] = tutor_result.get("codehelp_codeaid_result") or {}
    if tutor_mode == "socratic_no_answer_tutor":
        result["socratic_no_answer_result"] = tutor_result.get("socratic_no_answer_result") or {}
    if tutor_mode == "bridge_inspired_expert_decision_tutor":
        result["expert_decision_result"] = tutor_result.get("expert_decision_result") or {}

    if pipeline_mode in {"tutor_only", "tutor_only_no_diagnosis"}:
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)

    forbidden_content = list(bridge_result.get("forbidden_content") or [])
    used_gold_forbidden = False
    if (
        guard_mode == "oracle"
        and row.get("gold_forbidden_completion")
        and row["gold_forbidden_completion"] not in forbidden_content
    ):
        forbidden_content = [*forbidden_content, row["gold_forbidden_completion"]]
        used_gold_forbidden = True
    result["guard_contract"] = {
        "guard_mode": guard_mode,
        "used_gold_forbidden_completion": used_gold_forbidden,
        "forbidden_content": forbidden_content,
    }

    stage_start = time.perf_counter()
    try:
        leakage_result, leakage_retries = _call_stage_with_retries(
            leakage_judge_fn,
            {
                "student_message": student_message,
                "messages": messages,
                "problem_context": problem_context,
                "current_missing_bridge": bridge_result.get("missing_bridge", {}),
                "allowed_help_level": bridge_result.get("allowed_help_level", ""),
                "help_forms": _bridge_help_forms(bridge_result),
                "forbidden_content": forbidden_content,
                "candidate_response": candidate_response,
                "student_already_stated_bridge": bool(row.get("student_already_stated_bridge", False)),
            },
            judge_provider=judge_provider,
            max_retries=max_retries,
        )
        _add_llm_calls(result, 1 + leakage_retries)
        result["retry_count"] = result.get("retry_count", 0) + leakage_retries
    except Exception as exc:
        _add_llm_calls(result)
        _record_latency(latency_ms, "leakage_judge_latency_ms", stage_start)
        stage_errors["leakage_judge"] = f"{type(exc).__name__}: {exc}"
        result["error"] = "leakage_judge_exception"
        return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)
    _record_latency(latency_ms, "leakage_judge_latency_ms", stage_start)
    result["leakage_judge_result"] = leakage_result
    if leakage_result.get("_failed"):
        stage_errors["leakage_judge"] = str(leakage_result.get("_error") or leakage_result.get("_reason") or "_failed")

    safe_action = leakage_result.get("safe_action")
    if safe_action == "block" and pipeline_mode == "tutor_plus_guard":
        result["final_response_text"] = ""
        result["final_response_source"] = "blocked"
        result["blocked"] = True

    if (
        pipeline_mode == "tutor_plus_guard_plus_repair"
        and safe_action in {"rewrite", "block"}
        and not leakage_result.get("_failed")
    ):
        stage_start = time.perf_counter()
        try:
            repair_result, repair_retries = _call_stage_with_retries(
                repair_fn,
                {
                    "original_candidate_response": candidate_response,
                    "leakage_judge_result": leakage_result,
                    "bridge_judge_result": bridge_result,
                    "student_message": student_message,
                    "messages": messages,
                },
                judge_provider=judge_provider,
                max_retries=max_retries,
            )
            _add_llm_calls(result, 1 + repair_retries)
            result["repair_result"] = repair_result
            result["retry_count"] = result.get("retry_count", 0) + repair_retries
            repaired_response = repair_result.get("repaired_response")
            if repaired_response:
                result["final_response_text"] = repaired_response
                result["final_response_source"] = "repair"
                result["repair_applied"] = True
                result["blocked"] = False
            elif safe_action == "block":
                result["final_response_text"] = ""
                result["final_response_source"] = "blocked"
                result["blocked"] = True
        except Exception as exc:
            _add_llm_calls(result)
            stage_errors["repair"] = f"{type(exc).__name__}: {exc}"
            result["error"] = "repair_exception"
            if safe_action == "block":
                result["final_response_text"] = ""
                result["final_response_source"] = "blocked"
                result["blocked"] = True
        finally:
            _record_latency(latency_ms, "repair_latency_ms", stage_start)

    return _finish_case_result(result, latency_ms=latency_ms, stage_errors=stage_errors, total_start=total_start)


def run_bridge_offline_eval_rows(
    rows: list[dict],
    *,
    bridge_judge_fn: BridgeJudgeFn | None = None,
    tutor_fn: TutorFn | None = None,
    leakage_judge_fn: LeakageJudgeFn | None = None,
    repair_fn: RepairFn | None = None,
    chat_model_provider: str | None = None,
    tutor_mode: str = "current_system",
    guard_mode: str = "predicted",
    pipeline_mode: str = "tutor_plus_guard_plus_repair",
    judge_schema_mode: str = "full_schema_judge",
    judge_provider: str = "deepseek",
    max_retries: int = 0,
    chat_thinking_mode: str | None = None,
    focus_registry: list | None = None,
    focus_registry_path: Path | None = DEFAULT_FOCUS_REGISTRY_PATH,
    limit: int | None = None,
    progress_stream=None,
) -> list[dict]:
    if guard_mode not in {"predicted", "oracle"}:
        raise ValueError(f"Unsupported guard_mode: {guard_mode}")
    if tutor_mode not in TUTOR_MODES:
        raise ValueError(f"Unsupported tutor_mode: {tutor_mode}")
    if tutor_mode == "single_llm_structured" and pipeline_mode == "diagnosis_only":
        raise ValueError("single_llm_structured requires a tutor pipeline, not diagnosis_only")
    if pipeline_mode not in PIPELINE_MODES:
        raise ValueError(f"Unsupported pipeline_mode: {pipeline_mode}")
    if pipeline_mode == "tutor_only_no_diagnosis" and tutor_mode not in STANDALONE_NO_DIAGNOSIS_TUTOR_MODES:
        allowed = ", ".join(sorted(STANDALONE_NO_DIAGNOSIS_TUTOR_MODES))
        raise ValueError(f"tutor_only_no_diagnosis requires one of: {allowed}")
    if judge_schema_mode not in JUDGE_SCHEMA_MODES:
        raise ValueError(f"Unsupported judge_schema_mode: {judge_schema_mode}")
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    if chat_thinking_mode not in {None, "enabled", "disabled"}:
        raise ValueError(f"Unsupported chat_thinking_mode: {chat_thinking_mode}")
    selected = rows[:limit] if limit is not None else rows
    effective_bridge_judge_fn = bridge_judge_fn or _make_bridge_judge_fn(judge_provider)
    effective_tutor_fn = tutor_fn or _make_tutor_fn(tutor_mode, chat_model_provider)
    effective_leakage_judge_fn = leakage_judge_fn or _make_leakage_judge_fn(judge_provider)
    effective_repair_fn = repair_fn or _make_repair_fn(judge_provider)
    effective_focus_registry = focus_registry
    if effective_focus_registry is None and focus_registry_path is not None:
        effective_focus_registry = load_focus_registry(focus_registry_path)
    result_rows = []
    total = len(selected)
    for index, row in enumerate(selected, 1):
        case_id = row.get("id") or row.get("case_id") or f"case_{index}"
        _write_progress(progress_stream, "CASE_START", index=index, total=total, case_id=case_id)
        try:
            result = _run_one_bridge_offline_case(
                row,
                bridge_judge_fn=effective_bridge_judge_fn,
                tutor_fn=effective_tutor_fn,
                leakage_judge_fn=effective_leakage_judge_fn,
                repair_fn=effective_repair_fn,
                chat_model_provider=chat_model_provider,
                focus_registry=effective_focus_registry,
                guard_mode=guard_mode,
                tutor_mode=tutor_mode,
                pipeline_mode=pipeline_mode,
                judge_schema_mode=judge_schema_mode,
                judge_provider=judge_provider,
                max_retries=max_retries,
                chat_thinking_mode=chat_thinking_mode,
            )
            _write_progress(progress_stream, "CASE_DONE", index=index, total=total, case_id=case_id)
        except Exception as exc:
            result = {
                "case_id": case_id,
                "problem_ref": row.get("problem_ref", ""),
                "student_message": row.get("student_message", ""),
                "problem_context": row.get("problem_context", ""),
                "recent_dialogue": _dialogue_to_text(row.get("prior_messages") or row.get("recent_dialogue")),
                "student_code_excerpt": row.get("student_code") or row.get("student_code_excerpt") or "",
                "tutor_mode": tutor_mode,
                "guard_mode": guard_mode,
                "pipeline_mode": pipeline_mode,
                "judge_schema_mode": judge_schema_mode,
                "models": {
                    "judge_model": _judge_model_name(judge_provider),
                    "judge_provider": judge_provider,
                    "tutor_model_provider": chat_model_provider or "default",
                    "chat_thinking_mode": _effective_chat_thinking_mode(chat_thinking_mode),
                    "tutor_mode": tutor_mode,
                    "guard_mode": guard_mode,
                    "pipeline_mode": pipeline_mode,
                    "judge_schema_mode": judge_schema_mode,
                },
                "gold": _case_gold(row),
                "error": f"{type(exc).__name__}: {exc}",
                "latency_ms": {},
                "stage_errors": {"case": f"{type(exc).__name__}: {exc}"},
                "retry_count": 0,
                "candidate_response_text": "",
                "final_response_text": "",
                "final_response_source": "none",
                "repair_applied": False,
                "blocked": False,
                "llm_call_count": 0,
            }
            _write_progress(
                progress_stream,
                "CASE_ERROR",
                index=index,
                total=total,
                case_id=case_id,
                error=str(exc)[:120],
            )
        result_rows.append(result)
    return result_rows


def write_result_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run offline Bridge Judge + Leakage Judge evaluation rows.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_SEED_PATH, help="Seed turn JSONL file.")
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_PATH, help="Where to write result JSONL.")
    parser.add_argument("--limit", type=int, help="Optional case limit for smoke tests.")
    parser.add_argument(
        "--chat-model-provider",
        help="Optional provider id passed to current AIChat tutor, for model-controlled experiments.",
    )
    parser.add_argument(
        "--tutor-mode",
        choices=sorted(TUTOR_MODES),
        default="current_system",
        help="Tutor generation mode for offline comparison.",
    )
    parser.add_argument(
        "--guard-mode",
        choices=["predicted", "oracle"],
        default="predicted",
        help="Whether Leakage Judge sees only predicted forbidden content or oracle gold forbidden content.",
    )
    parser.add_argument(
        "--pipeline-mode",
        choices=sorted(PIPELINE_MODES),
        default="tutor_plus_guard_plus_repair",
        help="Offline ablation pipeline: diagnosis only, tutor only, tutor plus guard, or full guard plus repair.",
    )
    parser.add_argument(
        "--judge-schema-mode",
        choices=sorted(JUDGE_SCHEMA_MODES),
        default="full_schema_judge",
        help="Bridge Judge schema mode: full human-like schema, compact contract, or retrieval-augmented compact contract.",
    )
    parser.add_argument(
        "--judge-provider",
        default="deepseek",
        help="Provider for offline Bridge/Leakage/Repair judges. Use deepseek or kimi.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=0,
        help="Retry count for failed offline judge stages.",
    )
    parser.add_argument(
        "--chat-thinking-mode",
        choices=["enabled", "disabled"],
        help="Optional thinking mode override for current AIChat tutor calls.",
    )
    parser.add_argument(
        "--focus-registry",
        type=Path,
        default=DEFAULT_FOCUS_REGISTRY_PATH,
        help="Focus registry JSON used when seed rows do not provide available_known_focus.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    rows = run_bridge_offline_eval_rows(
        load_seed_rows(args.input_jsonl),
        limit=args.limit,
        chat_model_provider=args.chat_model_provider,
        tutor_mode=args.tutor_mode,
        guard_mode=args.guard_mode,
        pipeline_mode=args.pipeline_mode,
        judge_schema_mode=args.judge_schema_mode,
        judge_provider=args.judge_provider,
        max_retries=args.max_retries,
        chat_thinking_mode=args.chat_thinking_mode,
        focus_registry_path=args.focus_registry,
        progress_stream=sys.stderr,
    )
    write_result_rows(args.output_jsonl, rows)
    error_count = sum(1 for row in rows if row.get("error"))
    print(
        json.dumps(
            {
                "output_jsonl": str(args.output_jsonl),
                "case_count": len(rows),
                "error_count": error_count,
            },
            ensure_ascii=False,
        )
    )
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
