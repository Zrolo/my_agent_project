"""Run CP-MissingBridgeBench v4.1 20-case dev stabilization.

This runner is intentionally separate from the dialogue-state v3 offline runner.
It does not modify online AIChat behavior and does not recompute any main result
table. The run uses frozen/de-identified case-rubric fields as internal dev
inputs, so the output is a prompt-stabilization artifact rather than autonomous
Bridge Judge evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from noi_agent import _chat_completion_create, _extract_json_object


DEFAULT_DEV_MANIFEST = Path(
    "docs/research/cp_missingbridgebench_v4_20case_dev_selection_manifest_20260522.csv"
)
DEFAULT_FREEZE_CSV = Path(
    "docs/research/cp_missingbridgebench_v2_100case_case_freeze_ai_prelim_v2_3_20260521.csv"
)
DEFAULT_OUTPUT_DIR = Path("evals/aichat/ad_hoc_runs/cp_missingbridgebench_v4_dev20_20260522")

REQUIRED_FREEZE_FIELDS = [
    "v2_selection_id",
    "problem_summary_zh",
    "constraints_io_summary_zh",
    "recent_dialogue_summary_zh",
    "current_learner_state_summary_zh",
    "missing_reasoning_bridge_zh",
    "forbidden_content_zh",
    "acceptable_reveal_zh",
    "expected_next_student_action_zh",
    "expected_tutor_move",
    "final_context_sufficiency",
    "case_role_final",
]

REQUIRED_DEV_FIELDS = [
    "dev_case_id",
    "source_v2_selection_id",
    "rough_bridge_family",
    "surface_anchor",
    "help_seeking_type",
    "must_not_use_for_holdout",
]

LEAKAGE_LABELS = {
    "no_leakage",
    "minor_bridge_leakage",
    "major_bridge_leakage",
    "answer_leakage",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require_fields(rows: list[dict[str, str]], fields: list[str], path: Path) -> None:
    if not rows:
        raise ValueError(f"No rows found: {path}")
    missing = [field for field in fields if field not in rows[0]]
    if missing:
        raise ValueError(f"{path} missing required columns: {', '.join(missing)}")


def load_dev_cases(dev_manifest: Path, freeze_csv: Path) -> list[dict[str, str]]:
    dev_rows = read_csv(dev_manifest)
    freeze_rows = read_csv(freeze_csv)
    require_fields(dev_rows, REQUIRED_DEV_FIELDS, dev_manifest)
    require_fields(freeze_rows, REQUIRED_FREEZE_FIELDS, freeze_csv)
    freeze_by_id = {row["v2_selection_id"]: row for row in freeze_rows}
    merged: list[dict[str, str]] = []
    for dev in dev_rows:
        if dev.get("must_not_use_for_holdout") != "yes":
            raise ValueError(f"{dev.get('dev_case_id')} must be marked must_not_use_for_holdout=yes")
        source_id = dev["source_v2_selection_id"]
        if source_id not in freeze_by_id:
            raise ValueError(f"Missing freeze row for {source_id}")
        merged.append({**freeze_by_id[source_id], **{f"dev_{k}": v for k, v in dev.items()}})
    return merged


def infer_public_context_level(row: dict[str, str]) -> str:
    text = "\n".join(
        row.get(field, "")
        for field in [
            "problem_summary_zh",
            "constraints_io_summary_zh",
            "recent_dialogue_summary_zh",
            "current_learner_state_summary_zh",
        ]
    )
    if "题名级摘要" in text or "私有工作簿" in text or "不释放" in text:
        return "title_only"
    return "summary"


TITLE_ONLY_SCAFFOLD_TEMPLATES = [
    "请用一句话写出你当前代码中一个关键状态、变量或维护对象的含义。写完后，再说明它在一步操作前后应该怎样变化。",
    "请选择你已有的最小样例，只记录你当前代码中一个变量在每一步后的值，并标出第一次和预期不同的位置。",
    "请写出你认为每一步后都应该保持的一条性质，然后用你已有的最小样例逐步检查它。",
    "请说明你当前实现里一次操作前后，哪些量应该改变、哪些量应该不变。先写这一句话，不要急着改代码。",
]

TITLE_ONLY_FORBIDDEN_TERMS = [
    "比如",
    "例如",
    "插入",
    "查询",
    "合并",
    "距离",
    "点集",
    "节点",
    "字段",
    "cnt",
    "end",
    "dp[",
    "Trie",
    "线段树",
]


def compact_case_packet(row: dict[str, str]) -> dict[str, Any]:
    return {
        "dev_case_id": row["dev_dev_case_id"],
        "source_v2_selection_id": row["dev_source_v2_selection_id"],
        "problem_summary": row.get("problem_summary_zh", ""),
        "constraints_io_summary": row.get("constraints_io_summary_zh", ""),
        "recent_dialogue_summary": row.get("recent_dialogue_summary_zh", ""),
        "current_student_state_summary": row.get("current_learner_state_summary_zh", ""),
        "public_context_level": infer_public_context_level(row),
        "title_only_scaffold_templates": TITLE_ONLY_SCAFFOLD_TEMPLATES,
        "title_only_forbidden_terms": TITLE_ONLY_FORBIDDEN_TERMS,
        "freeze_reference": {
            "rough_bridge_family": row.get("dev_rough_bridge_family", ""),
            "surface_anchor": row.get("dev_surface_anchor", ""),
            "help_seeking_type": row.get("dev_help_seeking_type", ""),
            "missing_reasoning_bridge": row.get("missing_reasoning_bridge_zh", ""),
            "forbidden_content": row.get("forbidden_content_zh", ""),
            "acceptable_reveal": row.get("acceptable_reveal_zh", ""),
            "expected_next_student_action": row.get("expected_next_student_action_zh", ""),
            "expected_tutor_move": row.get("expected_tutor_move", ""),
            "case_role_final": row.get("case_role_final", ""),
        },
        "privacy_boundary": {
            "public_reporting_allowed": row.get("dev_public_reporting_allowed", "no"),
            "consent_reporting_gate": row.get("dev_consent_reporting_gate", "pending"),
            "notes": "Use de-identified freeze/rubric summaries only; do not request or output raw student text, full code, or full observed AIChat response.",
        },
    }


def json_call(
    *,
    system_prompt: str,
    user_payload: dict[str, Any],
    provider_id: str,
    max_retries: int,
) -> tuple[dict[str, Any], int, float]:
    messages = [{"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, indent=2)}]
    last_error: Exception | None = None
    start = time.perf_counter()
    for attempt in range(max_retries + 1):
        try:
            response = _chat_completion_create(
                system_prompt=system_prompt,
                messages=messages,
                provider_id=provider_id,
                response_format_json=True,
            )
            payload = _extract_json_object(response.choices[0].message.content)
            if not isinstance(payload, dict):
                raise ValueError("Model did not return a JSON object")
            return payload, attempt, round((time.perf_counter() - start) * 1000, 3)
        except Exception as exc:  # pragma: no cover - live API failure path
            last_error = exc
            if attempt >= max_retries:
                raise
    raise RuntimeError(f"unreachable retry loop: {last_error}")


BRIDGE_JUDGE_SYSTEM = """You are the Bridge Judge for CP-MissingBridgeBench v4.1.
Use the frozen case-rubric reference as internal dev input. Separate private
diagnostic content from tutor-visible guidance. Return valid JSON only.

Required JSON keys:
- context_sufficiency: sufficient | partial | insufficient | unclear
- student_current_blocker: Chinese summary
- reasoning_focus: representation_semantics | transition_mapping | predicate_decision | ordering_dependency | modeling_relation | aggregation_contribution | data_structure_operation | correctness_invariant | implementation_boundary | debugging_evidence | policy_request | other_candidate
- proposed_reasoning_focus: empty unless reasoning_focus is other_candidate
- surface_cue: concise visible task/dialogue cue
- private_bridge_target: internal detailed missing bridge; not shown to Tutor
- tutor_visible_boundary: safer boundary for Tutor; do not include full formula, full predicate, full code, or full proof
- forbidden_content_pattern: array of pattern-level forbidden content
- allowed_support: array of specific but non-revealing supports
- expected_next_student_action: one concrete action
- clarification_needed: yes | no
- clarification_question: string
- freeze_status: draft_requires_human_review
- can_be_used_for_tutor_generation: yes | no
- judge_confidence: high | medium | low
- notes_no_raw_text: string

Rules:
- If the packet contains only title-level or summary-level problem context, mark
  the tutor boundary as conservative. Do not infer exact sample values,
  coordinates, state dimensions, data structures, variable names, or proof
  skeletons from the title alone.
- allowed_support may be concrete in action form, but it must stay grounded in
  supplied information. Prefer actions such as tracing one visible variable,
  writing one sentence explaining a candidate state meaning, or testing the
  smallest failing case the student already has over invented examples.
- If public_context_level=title_only, treat all problem-specific facts beyond
  the title as unavailable. The tutor-visible boundary should explicitly say
  not to invent illustrative examples or problem-specific objects.
- In title_only context, tutor-visible Judge fields (tutor_visible_boundary,
  forbidden_content_pattern, allowed_support, expected_next_student_action,
  clarification_question) must not introduce numeric examples or counts,
  coordinates, binary strings, names, roster entries, points, edges, nodes,
  candidate state dimensions, exact data-structure names, or stored fields
  unless those details already appear in the packet.
- Safe title_only allowed_support should use learner-owned wording: "use your
  existing smallest sample", "trace one variable already in your code", "write
  one sentence for your current state meaning", or "state one condition you
  think should remain true after a step".
- In title_only context, set allowed_support by selecting from the provided
  title_only_scaffold_templates. Do not rewrite the templates into
  problem-specific examples.
- In title_only context, tutor-visible fields should avoid nouns copied from the
  problem title unless they are necessary to refer to the task. Prefer "这题",
  "当前实现", "当前状态/变量", "已有样例", and "当前代码".
- In title_only context, do not use "比如", "例如", parentheses examples,
  invented variable names, stored-field names, object counts, operation names,
  or problem-specific nouns in tutor-visible fields.
- In title_only context, tutor-visible fields must not contain any item from
  title_only_forbidden_terms unless the same term is explicitly present in the
  public input packet.
"""

TUTOR_SYSTEM = """You are a Chinese competitive-programming tutor for
CP-MissingBridgeBench v4.1. Use decomposition first, bridge boundary second.
Write the student-facing response in Chinese. Return valid JSON only.

Required JSON keys:
- student_facing_response: Chinese student-facing reply only
- scaffold_plan: array with 1-3 concise decomposition/scaffold steps
- concrete_next_action: one specific next action for the student
- boundary_self_check: object with does_not_reveal_missing_bridge, does_not_give_complete_solution_or_code, uses_case_specific_context, not_too_vague; each yes | no
- expected_student_reply_shape: short Chinese description
- vagueness_self_check: low | medium | high
- notes_no_raw_text: string

Rules:
1. Do not reveal the exact missing bridge.
2. Do not give complete code, full recurrence, full predicate, full proof, or a complete debugging fix.
3. Avoid generic encouragement. The next action must be concrete and low burden.
4. If the case is a direct-answer/code request, redirect to a bounded diagnostic step.
5. Do not mention Bridge Contract, DBox, judge, leakage, repair, JSON, or internal labels in the student-facing response.
6. Do not invent problem details that are not present in the input packet. This
   includes concrete arrays, coordinates, binary strings, sample values, numbers
   of objects, variable names, exact data structures, state dimensions, or
   stored-field meanings.
7. If the problem statement or recent dialogue is restricted to title-level or
   summary-level context, use generic but actionable diagnostics grounded in the
   packet: ask the student to trace a variable already visible to them, compare
   two interpretations they propose, or write one sentence about the maintained
   object. Do not create a new example instance.
8. For state-representation cases, do not suggest exact dimensions such as
   dp[i][j], do not assign meanings to dimensions, and do not list candidate
   state definitions unless those exact definitions are already in the input.
9. For data-structure cases, do not name a specific structure such as Trie,
   segment tree, heap, map, or queue unless it appears in the supplied packet or
   is already named by the student/problem summary.
10. For correctness, invariant, or geometry-style cases, do not fabricate
    coordinates, counterexamples, arrays, or proof skeletons. Ask the student to
    choose or report their own minimal case instead.
11. Do not offer candidate answer shapes such as "is it about the first i
    items?", "does this dimension mean X?", "try three points", "use this
    structure", or "record this exact field" unless that shape already appears
    in the packet. Ask the student to propose the shape instead.
12. When the packet says detailed context is restricted to private workbook or
    seed, treat all problem-specific facts beyond the title as unavailable. Use
    wording such as "用你当前代码里的变量" or "选择你已有的最小样例", not new invented
    facts.
13. When public_context_level=title_only, do not use "例如" to introduce
    problem-specific objects, counts, coordinates, strings, arrays,
    data-structure names, or state shapes. If an example is needed, phrase it as
    "用你已有的一个小样例" without specifying what the sample contains.
14. In public_context_level=title_only context, choose one action from
    title_only_scaffold_templates and write one short response around it. Do not
    add a second problem-specific mini-example.
15. In title_only context, avoid problem-title nouns if a generic phrase works.
    Prefer "这题", "当前实现", "当前状态/变量", "已有样例", and "当前代码".
16. In title_only context, the student-facing response should be at most two
    short sentences. It may add a brief opener such as "先别急着改代码", but the
    main action should stay close to one template. Do not use "比如", "例如", or
    parenthetical examples.
17. In title_only context, do not mention operation-specific words such as
    insert, query, merge, distance, point set, roster, node, field, counter,
    array names, or state dimensions unless they are present in the packet.
18. In title_only context, do not use any item from title_only_forbidden_terms.
    For data-structure cases, use "一次操作" instead of insert/query/update-specific
    wording.
"""

GUARD_SYSTEM = """You are the CP-MissingBridgeBench v4.1 Leakage Guard.
Compare the candidate tutor response with the private bridge target and
tutor-visible boundary. Return valid JSON only.

Required JSON keys:
- leakage_label: no_leakage | minor_bridge_leakage | major_bridge_leakage | answer_leakage
- leakage_rationale: Chinese explanation
- answer_or_code_leakage: none | minor | major | critical | unclear
- student_ready_risk: low | medium | high
- learner_burden_risk: low | medium | high
- needs_repair: yes | no
- repair_target_sentences: array of concise sentence summaries, not raw private text
- guard_confidence: high | medium | low

Guard is auxiliary. Do not score overall quality here.

Additional rules:
- Treat unsupported specificity as a risk. If the candidate invents sample
  values, coordinates, arrays, binary strings, variable names, exact data
  structures, state dimensions, or stored-field meanings that are not present in
  the input packet, set student_ready_risk to at least medium; if the invented
  detail could steer the solution, set needs_repair=yes.
- In state-representation cases, suggesting exact state dimensions, dp[i][j],
  or candidate dimension meanings can be major_bridge_leakage even when no final
  answer or code is given.
- In data-structure cases, naming the exact structure or stored fields can be
  major_bridge_leakage if the learner has not already supplied that structure.
- Candidate answer shapes are also risky. If a response proposes exact state
  shape, exact field meaning, exact structure choice, or a newly invented
  concrete instance instead of asking the student to propose/use their own,
  usually set needs_repair=yes.
- In public_context_level=title_only context, any newly introduced
  problem-specific illustration should usually trigger needs_repair=yes, even if
  it is phrased as an example.
- In title_only context, introducing problem-title-derived concrete nouns,
  numeric counts, candidate dimensions, or operation-specific examples should be
  treated as unsupported specificity unless those details are present in the
  packet.
- In title_only context, the words "比如", "例如", parenthetical examples,
  invented variable names, stored-field names, operation-specific nouns, or more
  than one action request should normally trigger needs_repair=yes.
- In title_only context, if the candidate response contains any item from
  title_only_forbidden_terms, set needs_repair=yes and include that phrase in
  repair_target_sentences.
"""

REPAIR_SYSTEM = """You are the CP-MissingBridgeBench v4.1 Targeted Repair.
Rewrite only over-revealing parts of the tutor response. Preserve safe and useful
parts. Return valid JSON only.

Required JSON keys:
- repaired_student_facing_response: Chinese response
- repair_scope: minimal_sentence_edit | partial_rewrite | full_rewrite
- preserved_helpful_parts: array
- removed_or_softened_parts: array
- concrete_next_action_after_repair: one concrete action
- anti_vagueness_check: pass | fail
- post_repair_leakage_self_check: no_leakage | minor_bridge_leakage | major_bridge_leakage | answer_leakage
- notes_no_raw_text: string

Do not introduce new algorithm content. Do not turn the response into vague encouragement.
Remove unsupported concrete examples, invented variables, exact data structures,
state dimensions, coordinates, arrays, or sample values. Replace them with a
grounded action that asks the student to use their own visible code, sample, or
interpretation. If the unsafe part is an exact state definition or exact
structure choice, soften it into a question about what the student thinks the
maintained object should mean.
If the unsafe part asks the student to create a new concrete instance from
invented values, replace it with "use the smallest sample you already have" or
"choose one failing sample from your current test".
In public_context_level=title_only context, remove all problem-specific
illustrative examples and replace them with "你已有的最小样例", "你当前代码中的一个变量",
or "你自己提出的一句话定义".
In title_only context, if the candidate response contains several action
requests, keep only one learner-owned action template and remove the rest.
In title_only context, remove "比如", "例如", parenthetical examples, invented
variable/field names, and operation-specific nouns. The repaired response should
be no longer than two short sentences.
In title_only context, remove every item from title_only_forbidden_terms; replace
operation-specific wording with "一次操作" or "一步操作".
"""


def validate_stage_payload(stage: str, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if stage == "judge":
        for key in [
            "context_sufficiency",
            "student_current_blocker",
            "reasoning_focus",
            "private_bridge_target",
            "tutor_visible_boundary",
            "forbidden_content_pattern",
            "allowed_support",
            "expected_next_student_action",
            "can_be_used_for_tutor_generation",
        ]:
            if key not in payload:
                errors.append(f"judge missing {key}")
    elif stage == "tutor":
        for key in ["student_facing_response", "scaffold_plan", "concrete_next_action", "boundary_self_check", "vagueness_self_check"]:
            if key not in payload:
                errors.append(f"tutor missing {key}")
    elif stage == "guard":
        if payload.get("leakage_label") not in LEAKAGE_LABELS:
            errors.append(f"guard invalid leakage_label={payload.get('leakage_label')!r}")
        if payload.get("needs_repair") not in {"yes", "no"}:
            errors.append(f"guard invalid needs_repair={payload.get('needs_repair')!r}")
    elif stage == "repair":
        if payload.get("post_repair_leakage_self_check") not in LEAKAGE_LABELS:
            errors.append(
                f"repair invalid post_repair_leakage_self_check={payload.get('post_repair_leakage_self_check')!r}"
            )
    return errors


def run_case(row: dict[str, str], *, provider_id: str, max_retries: int) -> dict[str, Any]:
    packet = compact_case_packet(row)
    result: dict[str, Any] = {
        "dev_case_id": row["dev_dev_case_id"],
        "source_v2_selection_id": row["dev_source_v2_selection_id"],
        "rough_bridge_family": row.get("dev_rough_bridge_family", ""),
        "surface_anchor": row.get("dev_surface_anchor", ""),
        "help_seeking_type": row.get("dev_help_seeking_type", ""),
        "privacy_review_status": row.get("dev_privacy_review_status", ""),
        "public_reporting_allowed": row.get("dev_public_reporting_allowed", "no"),
        "provider_id": provider_id,
        "stage_errors": {},
        "validation_errors": [],
        "llm_call_count": 0,
        "latency_ms": {},
    }

    judge, retry, latency = json_call(
        system_prompt=BRIDGE_JUDGE_SYSTEM,
        user_payload=packet,
        provider_id=provider_id,
        max_retries=max_retries,
    )
    result["llm_call_count"] += 1 + retry
    result["latency_ms"]["judge"] = latency
    result["bridge_judge_v4_1"] = judge
    result["validation_errors"].extend(validate_stage_payload("judge", judge))

    tutor_input = {
        "case": {
            k: packet[k]
            for k in [
                "problem_summary",
                "constraints_io_summary",
                "recent_dialogue_summary",
                "current_student_state_summary",
                "public_context_level",
                "title_only_scaffold_templates",
                "title_only_forbidden_terms",
            ]
        },
        "bridge_boundary": {
            "context_sufficiency": judge.get("context_sufficiency", ""),
            "student_current_blocker": judge.get("student_current_blocker", ""),
            "reasoning_focus": judge.get("reasoning_focus", ""),
            "surface_cue": judge.get("surface_cue", ""),
            "tutor_visible_boundary": judge.get("tutor_visible_boundary", ""),
            "forbidden_content_pattern": judge.get("forbidden_content_pattern", []),
            "allowed_support": judge.get("allowed_support", []),
            "expected_next_student_action": judge.get("expected_next_student_action", ""),
            "clarification_needed": judge.get("clarification_needed", "no"),
        },
        "privacy_boundary": packet["privacy_boundary"],
    }
    tutor, retry, latency = json_call(
        system_prompt=TUTOR_SYSTEM,
        user_payload=tutor_input,
        provider_id=provider_id,
        max_retries=max_retries,
    )
    result["llm_call_count"] += 1 + retry
    result["latency_ms"]["tutor"] = latency
    result["tutor_v4_1"] = tutor
    result["candidate_response_text"] = str(tutor.get("student_facing_response") or "")
    result["validation_errors"].extend(validate_stage_payload("tutor", tutor))

    guard_input = {
        "case": {
            "problem_summary": packet["problem_summary"],
            "current_student_state_summary": packet["current_student_state_summary"],
            "public_context_level": packet["public_context_level"],
            "title_only_scaffold_templates": packet["title_only_scaffold_templates"],
            "title_only_forbidden_terms": packet["title_only_forbidden_terms"],
        },
        "bridge_boundary": {
            "private_bridge_target": judge.get("private_bridge_target", ""),
            "tutor_visible_boundary": judge.get("tutor_visible_boundary", ""),
            "forbidden_content_pattern": judge.get("forbidden_content_pattern", []),
            "allowed_support": judge.get("allowed_support", []),
            "expected_next_student_action": judge.get("expected_next_student_action", ""),
        },
        "candidate_response": result["candidate_response_text"],
    }
    guard, retry, latency = json_call(
        system_prompt=GUARD_SYSTEM,
        user_payload=guard_input,
        provider_id=provider_id,
        max_retries=max_retries,
    )
    result["llm_call_count"] += 1 + retry
    result["latency_ms"]["guard"] = latency
    result["guard_v4_1"] = guard
    result["validation_errors"].extend(validate_stage_payload("guard", guard))

    result["final_response_text"] = result["candidate_response_text"]
    result["final_response_source"] = "candidate"
    if guard.get("needs_repair") == "yes":
        repair_input = {
            "candidate_response": result["candidate_response_text"],
            "bridge_boundary": {
                "tutor_visible_boundary": judge.get("tutor_visible_boundary", ""),
                "forbidden_content_pattern": judge.get("forbidden_content_pattern", []),
                "allowed_support": judge.get("allowed_support", []),
                "expected_next_student_action": judge.get("expected_next_student_action", ""),
            },
            "guard_result": guard,
            "public_context_level": packet["public_context_level"],
            "title_only_scaffold_templates": packet["title_only_scaffold_templates"],
            "title_only_forbidden_terms": packet["title_only_forbidden_terms"],
        }
        repair, retry, latency = json_call(
            system_prompt=REPAIR_SYSTEM,
            user_payload=repair_input,
            provider_id=provider_id,
            max_retries=max_retries,
        )
        result["llm_call_count"] += 1 + retry
        result["latency_ms"]["repair"] = latency
        result["repair_v4_1"] = repair
        result["validation_errors"].extend(validate_stage_payload("repair", repair))
        repaired = str(repair.get("repaired_student_facing_response") or "").strip()
        if repaired:
            result["final_response_text"] = repaired
            result["final_response_source"] = "repair"
    return result


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    leakage = Counter((row.get("guard_v4_1") or {}).get("leakage_label", "missing") for row in rows)
    repair_needed = Counter((row.get("guard_v4_1") or {}).get("needs_repair", "missing") for row in rows)
    final_source = Counter(row.get("final_response_source", "missing") for row in rows)
    vagueness = Counter((row.get("tutor_v4_1") or {}).get("vagueness_self_check", "missing") for row in rows)
    repair_scope = Counter((row.get("repair_v4_1") or {}).get("repair_scope", "not_applied") for row in rows)
    validation_error_rows = [row["dev_case_id"] for row in rows if row.get("validation_errors")]
    return {
        "run_role": "20-case dev stabilization only",
        "row_count": len(rows),
        "unique_cases": len({row.get("dev_case_id") for row in rows}),
        "provider_counts": dict(Counter(row.get("provider_id", "") for row in rows)),
        "family_counts": dict(Counter(row.get("rough_bridge_family", "") for row in rows)),
        "help_seeking_counts": dict(Counter(row.get("help_seeking_type", "") for row in rows)),
        "privacy_counts": dict(Counter(row.get("privacy_review_status", "") for row in rows)),
        "public_reporting_allowed_counts": dict(Counter(row.get("public_reporting_allowed", "") for row in rows)),
        "leakage_label_counts": dict(leakage),
        "needs_repair_counts": dict(repair_needed),
        "final_response_source_counts": dict(final_source),
        "vagueness_self_check_counts": dict(vagueness),
        "repair_scope_counts": dict(repair_scope),
        "validation_error_case_ids": validation_error_rows,
        "total_llm_calls": sum(int(row.get("llm_call_count") or 0) for row in rows),
        "boundary": (
            "Not a paper result; not a holdout result; not online AIChat; "
            "not a learning-outcome study; public case-level reporting is not allowed."
        ),
    }


def write_summary_md(path: Path, summary: dict[str, Any], output_jsonl: Path) -> None:
    lines = [
        "# CP-MissingBridgeBench v4.1 Dev20 Run Summary",
        "",
        "This is a 20-case prompt-stabilization run only. It is not a paper result, not a holdout result, and not online AIChat evidence.",
        "",
        f"- Output JSONL: `{output_jsonl}`",
        f"- Rows: {summary['row_count']}",
        f"- Unique cases: {summary['unique_cases']}",
        f"- Total LLM calls: {summary['total_llm_calls']}",
        "",
        "## Counts",
        "",
    ]
    for key in [
        "family_counts",
        "help_seeking_counts",
        "privacy_counts",
        "public_reporting_allowed_counts",
        "leakage_label_counts",
        "needs_repair_counts",
        "final_response_source_counts",
        "vagueness_self_check_counts",
        "repair_scope_counts",
    ]:
        lines.append(f"### {key}")
        lines.append("")
        for name, value in sorted(summary.get(key, {}).items()):
            lines.append(f"- {name}: {value}")
        lines.append("")
    lines.extend(
        [
            "## Validation Errors",
            "",
            f"Cases with validation errors: {', '.join(summary['validation_error_case_ids']) if summary['validation_error_case_ids'] else 'none'}",
            "",
            "## Boundary",
            "",
            summary["boundary"],
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run v4.1 20-case dev stabilization.")
    parser.add_argument("--dev-manifest", type=Path, default=DEFAULT_DEV_MANIFEST)
    parser.add_argument("--freeze-csv", type=Path, default=DEFAULT_FREEZE_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--provider-id", default="deepseek_flash")
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--case-id", action="append", dest="case_ids")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    rows = load_dev_cases(args.dev_manifest, args.freeze_csv)
    if args.case_ids:
        requested = set()
        for item in args.case_ids:
            requested.update(part.strip() for part in item.split(",") if part.strip())
        rows = [row for row in rows if row["dev_dev_case_id"] in requested]
    if args.limit is not None:
        rows = rows[: args.limit]
    if not rows:
        raise ValueError("No rows selected for v4 dev run")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, 1):
        print(f"[v4-dev20] {index}/{len(rows)} {row['dev_dev_case_id']}", file=sys.stderr, flush=True)
        try:
            result = run_case(row, provider_id=args.provider_id, max_retries=args.max_retries)
        except Exception as exc:  # pragma: no cover - live API failure path
            result = {
                "dev_case_id": row.get("dev_dev_case_id", ""),
                "source_v2_selection_id": row.get("dev_source_v2_selection_id", ""),
                "provider_id": args.provider_id,
                "stage_errors": {"run_case": f"{type(exc).__name__}: {exc}"},
                "validation_errors": ["run_case_exception"],
                "llm_call_count": 0,
            }
        result_rows.append(result)

    output_jsonl = args.output_dir / "v4_dev20_results.jsonl"
    summary_json = args.output_dir / "v4_dev20_summary.json"
    summary_md = args.output_dir / "v4_dev20_summary.md"
    write_jsonl(output_jsonl, result_rows)
    summary = summarize(result_rows)
    summary.update(
        {
            "dev_manifest": str(args.dev_manifest),
            "freeze_csv": str(args.freeze_csv),
            "output_jsonl": str(output_jsonl),
            "prompt_draft": "docs/research/cp_missingbridgebench_v4_prompt_freeze_draft_v0_8_20260522.md",
        }
    )
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary_md(summary_md, summary, output_jsonl)
    manifest = {
        "dev_manifest": str(args.dev_manifest),
        "freeze_csv": str(args.freeze_csv),
        "output_dir": str(args.output_dir),
        "provider_id": args.provider_id,
        "max_retries": args.max_retries,
        "row_count": len(result_rows),
        "result_jsonl": str(output_jsonl),
        "summary_json": str(summary_json),
        "summary_md": str(summary_md),
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
