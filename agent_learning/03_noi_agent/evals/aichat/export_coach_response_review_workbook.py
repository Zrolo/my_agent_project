import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import TextIO


DEFAULT_INPUT_PATH = Path("evals/aichat/bridge_offline_eval_results.jsonl")
DEFAULT_OUTPUT_PATH = Path("docs/research/coach_response_review_workbook_v1.csv")
DEFAULT_KEY_PATH = Path("docs/research/coach_response_review_workbook_v1.key.csv")
DEFAULT_CASE_SOURCE_PATH = Path("docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl")

FORBIDDEN_CONTENT_LABELS_ZH = {
    "no_exact_state_definition": "不要直接给出完整状态/表示定义",
    "no_exact_recurrence": "不要直接给出完整转移或递推关系",
    "no_exact_check_condition": "不要直接给出完整 check/判定条件",
    "no_complete_check_condition": "不要直接给出完整 check/判定条件",
    "no_exact_boundary_update_rule": "不要直接给出完整边界更新或循环方向规则",
    "no_exact_guard_condition": "不要直接给出完整守卫/过滤条件",
    "no_exact_modeling_plan": "不要直接给出完整建模方案",
    "no_full_invariant_proof": "不要直接给出完整正确性/不变量证明",
    "no_full_proof": "不要直接给出完整证明",
    "no_complete_exchange_argument": "不要直接给出完整交换论证或贪心正确性论证",
    "no_exact_contribution_formula": "不要直接给出完整贡献汇总公式",
    "no_complete_marking_formula": "不要直接给出完整标记/差分/贡献公式",
    "no_exact_iteration_template": "不要直接给出完整迭代模板",
    "no_exact_data_structure_template": "不要直接给出完整数据结构模板或维护流程",
    "no_complete_operation_sequence": "不要直接给出完整数据结构操作序列或维护步骤",
    "no_complete_local_condition": "不要直接补完当前局部条件",
    "no_fully_worked_micro_trace": "不要把微型例子完整演算到关键结论",
    "no_complete_model_mapping": "不要直接给出完整建模映射或对象关系",
    "no_direct_current_bridge": "不要直接补完当前关键桥",
    "no_full_solution": "不要给出完整题解或完整思路",
    "no_full_code": "不要给出完整可提交代码",
    "no_complete_code_patch": "不要直接给出完整代码补丁",
    "no_direct_bug_fix": "不要直接指出并修完具体 bug",
    "no_direct_answer_confirmation": "不要直接确认完整答案/算法路线",
    "no_full_keypress_mapping_table": "不要直接给出完整按键映射表",
}

TURN_POSITION_LABELS_ZH = {
    "initial": "初始提问",
    "followup": "后续辅导轮",
}

CONTEXT_TYPE_LABELS_ZH = {
    "initial_question": "初始提问",
    "followup_after_correct_short_answer": "后续：学生短答基本正确",
    "followup_after_partial_answer": "后续：学生回答部分正确",
    "followup_after_wrong_answer": "后续：学生回答错误",
    "followup_after_code_attempt": "后续：学生贴了代码/错误代码",
    "followup_after_prerequisite_gap": "后续：学生有前置知识断层",
    "policy_direct_answer_special": "策略请求：直接要答案/代码",
}

EXPECTED_TUTOR_MOVE_LABELS_ZH = {
    "advance": "推进到下一小步",
    "clarify": "澄清当前回答",
    "micro_step": "拆成更小一步",
    "prerequisite_repair": "补前置概念",
    "safe_redirect": "安全重定向",
}

FOLLOWABILITY_LABELS_ZH = {
    "F1": "F1 能一直跟上",
    "F2": "F2 勉强/部分跟上",
    "F3": "F3 比较难跟上",
    "F4": "F4 基础断层",
    "NA": "不适用",
}

REVIEW_COLUMNS = [
    "case_id",
    "anonymized_response_id",
    "problem_ref",
    "problem_source_platform",
    "problem_source_id",
    "problem_source_url",
    "problem_statement",
    "problem_statement_public_summary",
    "problem_statement_rights_note",
    "problem_statement_access_level",
    "student_message",
    "student_message_length_bucket",
    "problem_context",
    "recent_dialogue",
    "context_ai_reply",
    "context_alignment_flag",
    "success_criteria",
    "forbidden_content",
    "critical_bridge_boundary",
    "acceptable_reveal",
    "expected_student_next_action",
    "turn_position",
    "context_type",
    "student_scaffold_followability",
    "expected_tutor_move",
    "prior_ai_scaffold",
    "student_reply_to_prior_scaffold",
    "response_text",
    "coach_overall_quality_score",
    "coach_would_show_to_student",
    "coach_leakage_label",
    "coach_bridge_reveal_justification",
    "coach_scaffold_sufficiency_score",
    "coach_student_response_burden",
    "coach_bridge_identification_score",
    "coach_groundedness_score",
    "coach_scaffold_appropriateness_score",
    "coach_next_step_clarity_score",
    "coach_single_focus_coherence_score",
    "coach_micro_example_applicability",
    "coach_bridge_oriented_micro_example_score",
    "coach_bridge_leakage_control_score",
    "coach_preference_rank",
    "coach_reviewer_confidence",
    "coach_needs_discussion",
    "coach_notes",
    "review_status",
]

KEY_COLUMNS = [
    "anonymized_response_id",
    "case_id",
    "tutor_mode",
    "guard_mode",
    "pipeline_mode",
    "tutor_model_provider",
    "chat_thinking_mode",
    "final_response_source",
    "repair_applied",
    "blocked",
]


def load_result_rows(path: Path = DEFAULT_INPUT_PATH) -> list[dict]:
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


def load_case_source_rows(path: Path) -> dict[str, dict]:
    rows = {}
    if not path or not path.exists():
        return rows
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
        case_id = str(row.get("case_id") or row.get("id") or "").strip()
        if case_id:
            rows[case_id] = row
    return rows


def _case_source_for_row(row: dict, case_source_by_id: dict[str, dict] | None) -> dict:
    if not case_source_by_id:
        return {}
    case_id = str(row.get("case_id") or row.get("id") or "").strip()
    return case_source_by_id.get(case_id, {})


def _context_from_row(row: dict, key: str) -> str:
    value = row.get(key)
    if value:
        return str(value)
    if key == "recent_dialogue" and isinstance(row.get("prior_messages"), list):
        return _dialogue_to_text(row["prior_messages"])
    seed = row.get("seed") or row.get("input") or {}
    if isinstance(seed, dict):
        return str(seed.get(key) or "")
    return ""


def _metadata_from_row(row: dict, key: str, case_source: dict | None = None) -> str:
    value = row.get(key)
    if value is not None and str(value).strip():
        return str(value)
    if case_source:
        value = case_source.get(key)
        if value is not None and str(value).strip():
            return str(value)
    seed = row.get("seed") or row.get("input") or {}
    if isinstance(seed, dict) and seed:
        return _metadata_from_row(seed, key, case_source)
    return ""


def _stringify_rubric_value(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, list):
        return "\n".join(
            f"- {FORBIDDEN_CONTENT_LABELS_ZH.get(str(item).strip(), str(item).strip())}"
            for item in value
            if str(item).strip()
        )
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _rubric_field_from_row(row: dict, key: str, case_source: dict | None = None) -> str:
    for source in (row, case_source or {}):
        if not source:
            continue
        value = source.get(key)
        if value is not None and value != "":
            return _stringify_rubric_value(value)
    seed = row.get("seed") or row.get("input") or {}
    if isinstance(seed, dict) and seed:
        return _rubric_field_from_row(seed, key, case_source)
    return ""


def _missing_bridge_from_row(row: dict, case_source: dict | None = None) -> str:
    return _metadata_from_row(row, "missing_bridge", case_source)


def _critical_bridge_boundary(row: dict, case_source: dict | None = None) -> str:
    explicit = _rubric_field_from_row(row, "critical_bridge_boundary", case_source)
    if explicit:
        return explicit
    missing_bridge = _missing_bridge_from_row(row, case_source)
    forbidden = _rubric_field_from_row(row, "forbidden_content", case_source)
    parts = []
    if missing_bridge:
        parts.append(f"如果回复直接说出或完整推导出当前关键桥：{missing_bridge}，通常应判为关键桥泄露。")
    if forbidden:
        parts.append(f"尤其要避免命中“本轮禁止补完”中的内容：\n{forbidden}")
    return "\n".join(parts)


def _acceptable_reveal(row: dict, case_source: dict | None = None) -> str:
    explicit = _rubric_field_from_row(row, "acceptable_reveal", case_source)
    if explicit:
        return explicit
    return (
        "可以复述题意、确认学生已经说出的内容、指出观察方向、给一个未完整演算的局部问题或微任务；"
        "可以提示应比较哪些对象或变量，但不要替学生完整补完当前关键桥、完整公式、完整规则或完整代码。"
    )


def _expected_student_next_action(row: dict, case_source: dict | None = None) -> str:
    explicit = _rubric_field_from_row(row, "expected_student_next_action", case_source)
    if explicit:
        return explicit
    success_criteria = _rubric_field_from_row(row, "success_criteria", case_source)
    if success_criteria:
        return f"学生下一步应能围绕成功标准做一个短回答或局部判断：\n{success_criteria}"
    expected_move = _metadata_from_row(row, "expected_tutor_move_zh", case_source) or EXPECTED_TUTOR_MOVE_LABELS_ZH.get(
        _metadata_from_row(row, "expected_tutor_move", case_source),
        _metadata_from_row(row, "expected_tutor_move", case_source),
    )
    return f"学生下一步应能完成一个与“{expected_move or '当前教学动作'}”匹配的短回答、局部判断或小检查。"


def _display_metadata(row: dict, key: str, case_source: dict | None = None) -> str:
    zh_key = f"{key}_zh"
    value = _metadata_from_row(row, zh_key, case_source)
    if value:
        return value
    raw = _metadata_from_row(row, key, case_source)
    mappings = {
        "turn_position": TURN_POSITION_LABELS_ZH,
        "context_type": CONTEXT_TYPE_LABELS_ZH,
        "student_scaffold_followability": FOLLOWABILITY_LABELS_ZH,
        "expected_tutor_move": EXPECTED_TUTOR_MOVE_LABELS_ZH,
    }
    return mappings.get(key, {}).get(raw, raw)


def _problem_statement_from_row(row: dict) -> str:
    for key in (
        "problem_statement",
        "problem_statement_summary",
        "original_problem_statement",
        "full_problem_statement",
        "statement",
    ):
        value = row.get(key)
        if value:
            return str(value)
    seed = row.get("seed") or row.get("input") or {}
    if isinstance(seed, dict) and seed:
        return _problem_statement_from_row(seed)
    return ""


def _student_message_length_bucket(message: str) -> str:
    compact = "".join(str(message or "").split())
    length = len(compact)
    if length <= 30:
        return "short"
    if length <= 70:
        return "medium_short"
    if length <= 140:
        return "medium_long"
    return "long"


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


def _response_text(row: dict) -> str:
    if row.get("final_response_text"):
        return str(row["final_response_text"])
    tutor_response = row.get("tutor_response") or {}
    return str(tutor_response.get("response_text") or row.get("candidate_response_text") or "")


def _latest_prior_assistant_reply(row: dict) -> str:
    if row.get("context_ai_reply"):
        return str(row["context_ai_reply"]).strip()
    prior_messages = row.get("prior_messages")
    if isinstance(prior_messages, list):
        for item in reversed(prior_messages):
            if isinstance(item, dict) and item.get("role") == "assistant":
                return str(item.get("content") or "").strip()
    recent_dialogue = row.get("recent_dialogue")
    if isinstance(recent_dialogue, str):
        for line in reversed([part.strip() for part in recent_dialogue.splitlines() if part.strip()]):
            lower = line.lower()
            if lower.startswith("assistant:") or lower.startswith("ai:"):
                return line.split(":", 1)[1].strip()
    seed = row.get("seed") or row.get("input")
    if isinstance(seed, dict) and seed:
        return _latest_prior_assistant_reply(seed)
    return ""


def _split_dialogue_role_content(line: str) -> tuple[str, str] | None:
    text = line.strip()
    if not text:
        return None
    separators = ("：", ":")
    for separator in separators:
        if separator not in text:
            continue
        prefix, content = text.split(separator, 1)
        role = prefix.strip().lower()
        normalized = {
            "学生": "user",
            "user": "user",
            "human": "user",
            "assistant": "assistant",
            "ai": "assistant",
            "aichat": "assistant",
        }.get(role)
        if normalized:
            return normalized, content.strip()
    return None


def _context_alignment_flag(row: dict, student_message: str, recent_dialogue: str) -> str:
    explicit = row.get("context_alignment_flag")
    if explicit:
        return str(explicit)
    source = row.get("generation_context_source")
    if source in {"none", "no_context"}:
        return "no_recent_dialogue"

    dialogue = (recent_dialogue or "").strip()
    if not dialogue or dialogue.upper() == "N/A":
        return "no_recent_dialogue"

    parsed_lines = []
    for raw_line in dialogue.splitlines():
        parsed = _split_dialogue_role_content(raw_line)
        if parsed:
            parsed_lines.append(parsed)
    if not parsed_lines:
        return "unparseable_recent_dialogue"

    last_role, last_content = parsed_lines[-1]
    if last_role == "assistant":
        return "aligned_prior_context_ends_with_assistant"

    compact_last = "".join(last_content.split())
    compact_current = "".join(str(student_message or "").split())
    if compact_last and compact_current and compact_last == compact_current:
        return "aligned_current_message_in_dialogue"
    return "dialogue_mismatch_last_student_differs"


def _anonymized_id(row: dict, ordinal: int, *, id_salt: str = "") -> str:
    case_id = str(row.get("case_id") or row.get("id") or ordinal)
    raw = "|".join(
        [
            id_salt,
            case_id,
            str(row.get("tutor_mode") or ""),
            str(row.get("guard_mode") or ""),
            str(row.get("pipeline_mode") or ""),
            str(row.get("final_response_source") or ""),
            str(ordinal),
        ]
    )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10]
    return f"resp_{digest}"


def build_review_rows(
    result_rows: list[dict],
    *,
    shuffle_seed: int = 17,
    id_salt: str = "",
    case_source_by_id: dict[str, dict] | None = None,
) -> tuple[list[dict], list[dict]]:
    paired_rows = []
    for ordinal, row in enumerate(result_rows, 1):
        case_source = _case_source_for_row(row, case_source_by_id)
        response_text = _response_text(row)
        if not response_text.strip():
            continue
        anonymized_id = _anonymized_id(row, ordinal, id_salt=id_salt)
        review_row = {
            "case_id": row.get("case_id") or row.get("id") or "",
            "anonymized_response_id": anonymized_id,
            "problem_ref": _metadata_from_row(row, "problem_ref", case_source),
            "problem_source_platform": _metadata_from_row(row, "problem_source_platform", case_source),
            "problem_source_id": _metadata_from_row(row, "problem_source_id", case_source),
            "problem_source_url": _metadata_from_row(row, "problem_source_url", case_source),
            "problem_statement": _problem_statement_from_row(row),
            "problem_statement_public_summary": _metadata_from_row(row, "problem_statement_public_summary", case_source),
            "problem_statement_rights_note": _metadata_from_row(row, "problem_statement_rights_note", case_source),
            "problem_statement_access_level": _metadata_from_row(row, "problem_statement_access_level", case_source),
            "student_message": _context_from_row(row, "student_message"),
            "student_message_length_bucket": _student_message_length_bucket(
                _context_from_row(row, "student_message")
            ),
            "problem_context": _context_from_row(row, "problem_context"),
            "recent_dialogue": _context_from_row(row, "recent_dialogue"),
            "context_ai_reply": _latest_prior_assistant_reply(row),
            "context_alignment_flag": _context_alignment_flag(
                row,
                _context_from_row(row, "student_message"),
                _context_from_row(row, "recent_dialogue"),
            ),
            "success_criteria": _rubric_field_from_row(row, "success_criteria", case_source),
            "forbidden_content": _rubric_field_from_row(row, "forbidden_content", case_source),
            "critical_bridge_boundary": _critical_bridge_boundary(row, case_source),
            "acceptable_reveal": _acceptable_reveal(row, case_source),
            "expected_student_next_action": _expected_student_next_action(row, case_source),
            "turn_position": _display_metadata(row, "turn_position", case_source),
            "context_type": _display_metadata(row, "context_type", case_source),
            "student_scaffold_followability": _display_metadata(row, "student_scaffold_followability", case_source),
            "expected_tutor_move": _display_metadata(row, "expected_tutor_move", case_source),
            "prior_ai_scaffold": _metadata_from_row(row, "prior_ai_scaffold", case_source),
            "student_reply_to_prior_scaffold": _metadata_from_row(row, "student_reply_to_prior_scaffold", case_source),
            "response_text": response_text,
            "coach_overall_quality_score": "",
            "coach_would_show_to_student": "",
            "coach_leakage_label": "",
            "coach_bridge_reveal_justification": "",
            "coach_scaffold_sufficiency_score": "",
            "coach_student_response_burden": "",
            "coach_bridge_identification_score": "",
            "coach_groundedness_score": "",
            "coach_scaffold_appropriateness_score": "",
            "coach_next_step_clarity_score": "",
            "coach_single_focus_coherence_score": "",
            "coach_micro_example_applicability": "",
            "coach_bridge_oriented_micro_example_score": "",
            "coach_bridge_leakage_control_score": "",
            "coach_preference_rank": "",
            "coach_reviewer_confidence": "",
            "coach_needs_discussion": "",
            "coach_notes": "",
            "review_status": "unlabeled",
        }
        models = row.get("models") or {}
        key_row = {
            "anonymized_response_id": anonymized_id,
            "case_id": review_row["case_id"],
            "tutor_mode": row.get("tutor_mode") or models.get("tutor_mode") or "",
            "guard_mode": row.get("guard_mode") or models.get("guard_mode") or "",
            "pipeline_mode": row.get("pipeline_mode") or models.get("pipeline_mode") or "",
            "tutor_model_provider": models.get("tutor_model_provider") or "",
            "chat_thinking_mode": models.get("chat_thinking_mode") or "",
            "final_response_source": row.get("final_response_source") or "",
            "repair_applied": str(bool(row.get("repair_applied", False))).lower(),
            "blocked": str(bool(row.get("blocked", False))).lower(),
        }
        paired_rows.append((review_row, key_row))

    rng = random.Random(shuffle_seed)
    rng.shuffle(paired_rows)
    return [item[0] for item in paired_rows], [item[1] for item in paired_rows]


def write_review_csv(output: TextIO, rows: list[dict]) -> None:
    writer = csv.DictWriter(output, fieldnames=REVIEW_COLUMNS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def write_key_csv(output: TextIO, rows: list[dict]) -> None:
    writer = csv.DictWriter(output, fieldnames=KEY_COLUMNS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def export_response_review_workbook(
    *,
    input_jsonl: Path = DEFAULT_INPUT_PATH,
    output_csv: Path = DEFAULT_OUTPUT_PATH,
    key_csv: Path = DEFAULT_KEY_PATH,
    shuffle_seed: int = 17,
    id_salt: str = "",
    case_source_jsonl: Path | None = None,
) -> int:
    case_source_by_id = load_case_source_rows(case_source_jsonl) if case_source_jsonl else {}
    review_rows, key_rows = build_review_rows(
        load_result_rows(input_jsonl),
        shuffle_seed=shuffle_seed,
        id_salt=id_salt,
        case_source_by_id=case_source_by_id,
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    key_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        write_review_csv(f, review_rows)
    with key_csv.open("w", encoding="utf-8-sig", newline="") as f:
        write_key_csv(f, key_rows)
    return len(review_rows)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export blind coach response-review workbook from offline eval JSONL.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--key-csv", type=Path, default=DEFAULT_KEY_PATH)
    parser.add_argument("--shuffle-seed", type=int, default=17)
    parser.add_argument(
        "--id-salt",
        default="",
        help="Optional experiment/run id included in anonymized response ids to avoid cross-run collisions.",
    )
    parser.add_argument(
        "--case-source-jsonl",
        type=Path,
        default=None,
        help="Optional reviewed case JSONL used to backfill case-specific rubric fields by case_id.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    row_count = export_response_review_workbook(
        input_jsonl=args.input_jsonl,
        output_csv=args.output_csv,
        key_csv=args.key_csv,
        shuffle_seed=args.shuffle_seed,
        id_salt=args.id_salt,
        case_source_jsonl=args.case_source_jsonl,
    )
    print(
        json.dumps(
            {"output_csv": str(args.output_csv), "key_csv": str(args.key_csv), "row_count": row_count},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
