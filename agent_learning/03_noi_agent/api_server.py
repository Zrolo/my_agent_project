"""
FastAPI HTTP wrapper for the NOI coaching agent.

Run:
    uvicorn api_server:app --reload
"""

import json
import os
import re
import threading
import time
import csv
import hashlib
import io
from datetime import datetime, timedelta, timezone
from html import unescape
from functools import lru_cache
from pathlib import Path
from typing import Literal, List, Optional, Dict
from urllib.parse import urlparse
from uuid import uuid4

import requests
from fastapi import Depends, FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSE_REVIEW_WORKBOOK_CSV_PATH = Path(BASE_DIR) / "docs/research/coach_response_review_workbook_deepseek_flash_thinking_n10.csv"
RESPONSE_REVIEW_LABELS_JSONL_PATH = Path(BASE_DIR) / "docs/research/coach_response_review_labels_v1.jsonl"
DEFAULT_RESPONSE_REVIEW_DATASET_ID = "repair_before_after_20260510"
RESPONSE_REVIEW_DATASETS = [
    {
        "dataset_id": "repair_before_after_20260510",
        "label": "Repair 前后对照 20260510",
        "description": "只包含 4 条触发 repair 的样例，每题各有候选回复和修复后回复，用于判断 Repair 是否真的改善 bridge-oriented micro-example。",
        "workbook_csv_path": Path(BASE_DIR) / "docs/research/coach_response_review_workbook_repair_before_after_20260510.csv",
        "labels_jsonl_path": Path(BASE_DIR) / "docs/research/coach_response_review_labels_repair_before_after_20260510.jsonl",
    },
    {
        "dataset_id": "deepseek_flash_thinking_n10",
        "label": "DeepSeek Flash Thinking 对照 n10",
        "description": "上一轮 thinking enabled/disabled 对照盲评批次。",
        "workbook_csv_path": RESPONSE_REVIEW_WORKBOOK_CSV_PATH,
        "labels_jsonl_path": RESPONSE_REVIEW_LABELS_JSONL_PATH,
    },
    {
        "dataset_id": "micro_example_policy_n10",
        "label": "桥梁导向微型例子 n10",
        "description": "加入 bridge-oriented micro-example 规则后的 DeepSeek Flash thinking disabled 批次。",
        "workbook_csv_path": Path(BASE_DIR) / "docs/research/coach_response_review_workbook_micro_example_policy_n10.csv",
        "labels_jsonl_path": Path(BASE_DIR) / "docs/research/coach_response_review_labels_micro_example_policy_n10.jsonl",
    },
]

from auth import (
    authenticate_user,
    change_own_password,
    create_student_account,
    create_token,
    get_current_user,
    list_student_accounts,
    require_student,
    require_teacher,
    reset_student_password,
    security,
    set_student_active,
)
from noi_agent import (
    PER_PROBLEM_HINT_LIMIT,
    analyze_student_turn,
    build_policy_handoff_payload,
    chat,
    evaluate_understanding_evidence,
    _chat_completion_create,
    _extract_json_object,
    generate_understanding_check,
    get_aichat_prompt_mode_public_info,
    get_chat_model_public_info,
    grade_understanding_check,
    get_remaining_quota,
    list_chat_model_options,
    load_quota,
    save_quota,
    summarize_aichat_problem_memory,
    analyze_aichat_session,
    tag_aichat_turn,
)
from database import (
    LEARNING_STATUS_KNOWLEDGE_BAILOUT,
    LEARNING_STATUS_NEEDS_TEACHER,
    LEARNING_STATUS_NOT_STARTED,
    LEARNING_STATUS_QUIZ_IN_PROGRESS,
    LEARNING_STATUS_SELF_CHECK_REQUIRED,
    LEARNING_STATUS_REMEDY_AVAILABLE,
    LEARNING_STATUS_REMEDY_IN_PROGRESS,
    LEARNING_STATUS_RESOLVED,
    MASTERY_STATUS_ASSISTED_SUCCESS,
    MASTERY_STATUS_INDEPENDENT_SUCCESS,
    MASTERY_STATUS_NOT_ASSESSED,
    MASTERY_STATUS_NOT_MASTERED,
    REVIEW_STATUS_COMPLETED,
    REVIEW_STATUS_PENDING,
    create_teacher_announcement,
    init_db,
    create_aichat_problem_closure,
    create_problem_bottleneck_event,
    create_student_problem_completion,
    create_student_feedback,
    create_checkin,
    get_checkin_detail_by_id,
    create_review_quiz,
    create_teacher_flag,
    get_confirm_pool_entry,
    get_latest_quiz_for_review,
    get_student_checkins,
    get_student_checkin_by_id,
    get_all_checkins,
    create_pending_review,
    create_review_session,
    create_review,
    get_review_by_checkin,
    get_review_context,
    get_quiz_by_id,
    get_quizzes_for_review,
    get_pending_judgement_quizzes,
    get_pending_quizzes,
    get_problem_tags,
    get_problem_analysis,
    get_error_stats,
    get_pending_review_jobs,
    get_review_layer_stats,
    get_review_status_summary,
    get_mastery_status_stats,
    get_topic_l1_stats,
    get_topic_l2_stats,
    get_bridge_stats,
    get_bridge_path_stats,
    get_bridge_route_stats,
    get_bridge_route_promotion_suggestions,
    get_bridge_route_promotion_suggestion,
    get_knowledge_bailout_stats,
    get_student_flags,
    list_problem_analysis_failures,
    increment_review_remedy_count,
    increment_confirm_pool_skip,
    mark_review_attempt,
    mark_review_failed,
    mark_review_pending,
    record_quiz_attempt,
    get_aichat_problem_closure,
    get_aichat_learning_issue_stats,
    get_aichat_problem_memory,
    get_db,
    get_latest_student_announcement,
    grade_aichat_problem_closure,
    record_aichat_message,
    record_aichat_turn_tag,
    get_aichat_session_analysis,
    get_aichat_session_analysis_health,
    list_aichat_messages,
    list_aichat_turn_tags,
    list_student_feedback,
    list_student_problem_completions,
    list_teacher_announcements,
    list_teacher_aichat_observations,
    list_teacher_aichat_evidence_students,
    list_teacher_aichat_evidence_sessions,
    list_bridge_research_samples,
    list_bridge_research_annotation_exports,
    get_teacher_aichat_evidence_session_detail,
    upsert_bridge_research_annotation,
    upsert_aichat_session_analysis,
    create_teacher_student_note,
    get_class_learning_diagnosis,
    get_student_learning_dossier,
    list_teacher_student_notes,
    record_checkin_stats,
    record_rejected_checkin,
    get_problem_by_luogu_pid,
    get_manual_review_stats,
    get_manual_review_stats_breakdown,
    get_review_events_for_checkin,
    list_teacher_review_samples,
    get_usage_stats,
    get_class_completion_summary,
    get_class_exit_trigger_summary,
    get_student_completion_summary,
    get_student_exit_trigger_summary,
    has_problem_bottleneck_event,
    list_related_problems_by_luogu_pid,
    upsert_external_problem,
    record_review_event,
    upsert_aichat_problem_memory,
    upsert_review_manual_review,
    upsert_bridge_rule_draft_decision,
    list_bridge_rule_draft_decisions,
    create_bridge_registry_entry_from_decision,
    list_bridge_registry_entries,
    get_bridge_registry_entry,
    build_resolver_patch_draft_for_registry_entry,
    update_quiz_status,
    update_review_bridge_path,
    update_review_learning_status,
    update_review_mastery_status,
    update_review_self_check,
    reset_review_for_student_retry,
)
from review_engine import (
    QUIZ_ROLE_CONFIRM,
    QUIZ_ROLE_FOLLOWUP,
    QUIZ_ROLE_KNOWLEDGE_CONFIRM,
    QUIZ_ROLE_MAIN,
    QUIZ_ROLE_REMEDY,
    REMEDY_ACTION_DYNAMIC,
    REMEDY_ACTION_EASIER_QUIZ,
    REMEDY_ACTION_REPHRASE,
    REMEDY_ACTION_SMALLER_EXAMPLE,
    _detect_review_mode,
    _family_for_review_mode,
    generate_knowledge_bailout_card,
    generate_knowledge_confirm_quiz,
    generate_final_micro_confirm_quiz,
    generate_bridge_quiz,
    generate_confirm_quiz_from_pool,
    generate_remedy_explanation,
    generate_review,
    is_review_llm_configured,
    transfer_signal_has_explicit_trigger,
    validate_bottleneck,
)
from problem_bank import (
    build_problem_context,
    classify_tag,
    ensure_problem_analysis,
    get_problem_card_by_ref,
    normalize_luogu_problem_ref,
    retry_problem_analysis_by_pid,
)
from code_runner import get_runner_health, run_cpp17_sample

# 初始化数据库
init_db()

# 内存会话历史存储：{(student_id, problem_id, session_id): [messages]}
session_histories: Dict[tuple, List[dict]] = {}

# 教师密钥（从环境变量读取）
NOI_TEACHER_SECRET = os.environ.get("NOI_TEACHER_SECRET", "")

app = FastAPI(
    title="NOI Coach Agent API",
    description="HTTP interface for the NOI coaching agent with training loop.",
    version="0.5.0",
)

LUOGU_TAGS_URL = "https://www.luogu.com.cn/_lfe/tags/zh-CN"
LUOGU_HEADERS = {
    "User-Agent": "Mozilla/5.0 (NOI Coach Agent)",
    "x-lentille-request": "content-only",
}
REVIEW_CONCURRENCY_LIMIT = 5
_review_generation_semaphore = threading.BoundedSemaphore(REVIEW_CONCURRENCY_LIMIT)
STREAM_STATUS_POLL_SECONDS = float(os.environ.get("NOI_REVIEW_STREAM_STATUS_POLL_SECONDS", "1.0"))
HELP_REQUEST_KEYWORDS = ("不会", "卡住", "需要提示", "看不懂", "没思路")
FAILED_SUBMISSION_RESULTS = {"wa", "tle", "re", "ce"}
CONCRETE_BRIDGE_TERMS = (
    "a[mid]",
    "mid",
    "dp[",
    "lazy",
    "懒标记",
    "下传",
    "前缀",
    "trie",
    "右边界",
    "左边界",
    "check(",
    "转移",
    "状态",
    "区间",
    "根节点",
    "sum",
    "long long",
    "越界",
)
MAX_SCAFFOLD_ROUNDS = 3
MAX_REMEDY_ACTIONS = 2
STRUCTURE_TYPE_TAG_MAP = {
    "差分约束": "difference_constraints",
    "拓扑排序": "topological_sort",
    "最小生成树": "minimum_spanning_tree",
    "二分图": "bipartite_graph",
    "单调队列": "monotonic_queue",
    "最短路": "shortest_path",
    "并查集": "union_find",
    "二分答案": "binary_search_answer",
    "树形dp": "tree_dp",
    "树形DP": "tree_dp",
    "区间dp": "interval_dp",
    "区间DP": "interval_dp",
}
_checkin_runtime_status: dict[int, dict] = {}
_checkin_runtime_status_lock = threading.Lock()


def update_checkin_runtime_status(
    checkin_id: int,
    phase: str,
    review_status: str,
    message: str,
    draft_review: dict | None = None,
) -> None:
    now = time.time()
    with _checkin_runtime_status_lock:
        current = _checkin_runtime_status.get(checkin_id) or {}
        started_at = current.get("started_at") or now
        _checkin_runtime_status[checkin_id] = {
            "phase": phase,
            "review_status": review_status,
            "message": message,
            "draft_review": draft_review if draft_review is not None else current.get("draft_review") or {},
            "started_at": started_at,
            "updated_at": now,
        }


def get_checkin_runtime_status(checkin_id: int) -> dict | None:
    with _checkin_runtime_status_lock:
        current = _checkin_runtime_status.get(checkin_id)
        return dict(current) if current else None


def clear_checkin_runtime_status(checkin_id: int) -> None:
    with _checkin_runtime_status_lock:
        _checkin_runtime_status.pop(checkin_id, None)


def update_checkin_runtime_draft(checkin_id: int, draft_review: dict) -> None:
    now = time.time()
    with _checkin_runtime_status_lock:
        current = _checkin_runtime_status.get(checkin_id) or {}
        started_at = current.get("started_at") or now
        _checkin_runtime_status[checkin_id] = {
            "phase": current.get("phase") or "llm_start",
            "review_status": current.get("review_status") or REVIEW_STATUS_PENDING,
            "message": current.get("message") or "正在调用模型",
            "draft_review": dict(draft_review or {}),
            "started_at": started_at,
            "updated_at": now,
        }


def _attach_review_route_fields(item: dict | None) -> dict | None:
    if not item:
        return item
    annotated = dict(item)
    review_mode = _detect_review_mode(
        annotated.get("completion_status", ""),
        annotated.get("submission_result"),
    )
    annotated["review_mode"] = review_mode
    annotated["review_family"] = _family_for_review_mode(review_mode)
    return annotated


def _new_checkin_session_id() -> str:
    return f"checkin_{uuid4().hex}"


def _build_checkin_stream_payload(checkin_id: int, item: dict) -> dict:
    runtime = get_checkin_runtime_status(checkin_id)
    now = time.time()
    if runtime:
        started_at = float(runtime.get("started_at") or now)
        updated_at = float(runtime.get("updated_at") or now)
        return {
            "checkin_id": checkin_id,
            "review_status": runtime.get("review_status") or item.get("review_status") or REVIEW_STATUS_PENDING,
            "phase": runtime.get("phase") or "queued",
            "message": runtime.get("message") or "已进入生成队列",
            "draft_review": runtime.get("draft_review") or {},
            "elapsed_seconds": max(0, int(now - started_at)),
            "updated_at": updated_at,
        }

    status = item.get("review_status") or REVIEW_STATUS_PENDING
    if status == REVIEW_STATUS_COMPLETED:
        phase = "completed"
        message = "复盘已就绪"
    elif status == "failed":
        phase = "failed"
        message = "复盘生成失败，可稍后重试"
    else:
        phase = "queued"
        message = "已进入生成队列"
    return {
        "checkin_id": checkin_id,
        "review_status": status,
        "phase": phase,
        "message": message,
        "draft_review": {},
        "elapsed_seconds": 0,
        "updated_at": now,
    }


def _encode_sse_event(event: str, payload: dict) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}\n\n"
    )


def extract_luogu_pid(raw_url: str) -> Optional[str]:
    pid, _ = normalize_luogu_problem_ref(raw_url)
    return pid


def normalize_luogu_problem_url(raw_url: str) -> Optional[str]:
    _, normalized_url = normalize_luogu_problem_ref(raw_url)
    return normalized_url


def normalize_jmfes_problem_url(raw_url: str) -> Optional[str]:
    raw = (raw_url or "").strip()
    if not raw:
        return None
    candidate = raw if re.match(r"^https?://", raw, re.I) else f"http://{raw}"
    parsed = urlparse(candidate)
    host = parsed.netloc.lower()
    path = parsed.path or ""
    if host not in {"oj.jmfes.com:8888", "oj.jmfes.com", "172.21.60.30:8888", "172.21.60.30"}:
        return None
    match = re.match(r"^/p/([A-Za-z0-9_-]+)$", path)
    if not match:
        return None
    return f"http://oj.jmfes.com:8888/p/{match.group(1)}"


def infer_oj_source_from_problem_ref(raw_ref: str, declared_source: str = "other") -> str:
    raw = (raw_ref or "").strip()
    declared = (declared_source or "other").strip().lower()
    if raw:
        if normalize_luogu_problem_ref(raw)[0]:
            return "luogu"
        if normalize_jmfes_problem_url(raw):
            return "jmfes"
        host = urlparse(raw if re.match(r"^https?://", raw, re.I) else f"https://{raw}").netloc.lower()
        if host.endswith("luogu.com.cn") or host.endswith("luogu.com"):
            return "luogu"
        if host.endswith("codeforces.com"):
            return "codeforces"
        if host.endswith("atcoder.jp"):
            return "atcoder"
        if re.match(r"^https?://", raw, re.I):
            return "other"
    return declared if declared in {"luogu", "jmfes", "codeforces", "atcoder", "other"} else "other"


@lru_cache(maxsize=1)
def get_luogu_tag_map() -> Dict[int, str]:
    response = requests.get(LUOGU_TAGS_URL, headers={"User-Agent": LUOGU_HEADERS["User-Agent"]}, timeout=20)
    response.raise_for_status()
    payload = response.json()
    return {
        int(item["id"]): item["name"]
        for item in payload.get("tags", [])
        if "id" in item and "name" in item
    }


def _trim_markdown_block(text: Optional[str], limit: int = 1800) -> str:
    cleaned = (text or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "\n\n……"


def has_explicit_help_signal(route_context: dict) -> bool:
    combined_text = "\n".join(
        [
            str(route_context.get("bottleneck_text") or "").strip(),
            str(route_context.get("reflection") or "").strip(),
        ]
    )
    if any(keyword in combined_text for keyword in HELP_REQUEST_KEYWORDS):
        return True
    if str(route_context.get("completion_status") or "").strip() == "hinted":
        return True
    if str(route_context.get("submission_result") or "").strip().lower() not in FAILED_SUBMISSION_RESULTS:
        return False
    return not any(term in combined_text for term in CONCRETE_BRIDGE_TERMS)


def passes_explanation_gate(review_context: dict, quizzes: list[dict]) -> bool:
    if (review_context.get("understanding_self_check") or "").strip() != "clear":
        return False
    if not quizzes:
        return False

    main_quiz = next((quiz for quiz in quizzes if quiz.get("quiz_role") == QUIZ_ROLE_MAIN), None)
    if not main_quiz or main_quiz.get("status") != "correct":
        return False

    for role in (QUIZ_ROLE_FOLLOWUP, QUIZ_ROLE_CONFIRM):
        role_quizzes = [quiz for quiz in quizzes if quiz.get("quiz_role") == role]
        if role_quizzes and any(quiz.get("status") != "correct" for quiz in role_quizzes):
            return False
    return True


def resolve_structure_type(problem_tags: list[str]) -> str | None:
    for raw_tag in problem_tags or []:
        tag = str(raw_tag).strip()
        if tag in STRUCTURE_TYPE_TAG_MAP:
            return STRUCTURE_TYPE_TAG_MAP[tag]
    return None


def build_confirm_payload(review_context: dict, previous_quiz: dict | None) -> dict:
    structure_type = resolve_structure_type(review_context.get("problem_tags") or [])
    if structure_type:
        pool_entry = get_confirm_pool_entry(structure_type)
        if pool_entry and pool_entry.get("status") == "usable":
            return generate_confirm_quiz_from_pool(
                review_context,
                structure_type=structure_type,
                bridge_note=pool_entry.get("bridge_note") or "",
                problem_url=pool_entry.get("problem_url") or "",
            )
    fallback_payload = None
    for _ in range(2):
        fallback_payload = generate_bridge_quiz(
            review_context,
            previous_quiz=previous_quiz,
            quiz_role=QUIZ_ROLE_CONFIRM,
        )
        if fallback_payload.get("mode") == "quiz":
            return fallback_payload
    if structure_type:
        increment_confirm_pool_skip(structure_type)
    return fallback_payload or {
        "mode": "fallback_explain",
        "explanation": "当前这一步更适合先换一种方式讲清楚，我们先不继续出确认题。",
    }


def build_luogu_problem_context(problem_payload: dict) -> str:
    content = problem_payload.get("content") or {}
    contenu = problem_payload.get("contenu") or {}

    sections: List[str] = []
    background = _trim_markdown_block(content.get("background") or contenu.get("background"), limit=1200)
    description = _trim_markdown_block(content.get("description") or contenu.get("description"), limit=2200)
    input_format = _trim_markdown_block(
        content.get("inputFormat") or contenu.get("inputFormat") or contenu.get("formatI"),
        limit=800,
    )
    output_format = _trim_markdown_block(
        content.get("outputFormat") or contenu.get("outputFormat") or contenu.get("formatO"),
        limit=800,
    )
    hint = _trim_markdown_block(content.get("hint") or contenu.get("hint"), limit=600)
    samples = problem_payload.get("samples") or []
    limits = problem_payload.get("limits") or {}

    if description:
        sections.append(f"## 题目描述\n{description}")
    if input_format:
        sections.append(f"## 输入格式\n{input_format}")
    if output_format:
        sections.append(f"## 输出格式\n{output_format}")
    if samples:
        sample_blocks = []
        for idx, sample in enumerate(samples[:2], start=1):
            if not isinstance(sample, list) or len(sample) < 2:
                continue
            sample_in = (sample[0] or "").strip()
            sample_out = (sample[1] or "").strip()
            sample_blocks.append(
                f"### 样例 {idx}\n输入：\n```text\n{sample_in}\n```\n输出：\n```text\n{sample_out}\n```"
            )
        if sample_blocks:
            sections.append("## 样例\n" + "\n\n".join(sample_blocks))
    if limits:
        time_limits = limits.get("time") or []
        memory_limits = limits.get("memory") or []
        time_ms = next((item for item in time_limits if item), None)
        memory_kb = next((item for item in memory_limits if item), None)
        limit_parts = []
        if time_ms:
            limit_parts.append(f"时间限制：{time_ms} ms")
        if memory_kb:
            limit_parts.append(f"内存限制：{memory_kb // 1024 if isinstance(memory_kb, int) else memory_kb} MB")
        if limit_parts:
            sections.append("## 限制\n" + "；".join(limit_parts))
    if background and len(background) <= 800:
        sections.append(f"## 题目背景\n{background}")
    if hint and "淘宝" not in hint and "广告" not in hint:
        sections.append(f"## 提示\n{hint}")

    return "\n\n".join(section for section in sections if section).strip()


def fetch_luogu_problem(raw_url: str) -> dict:
    normalized_url = normalize_luogu_problem_url(raw_url)
    if not normalized_url:
        raise ValueError("请输入有效的洛谷题号或公开题目链接")

    pid = extract_luogu_pid(normalized_url)
    local_problem = get_problem_by_luogu_pid(pid) if pid else None
    if local_problem:
        return {
            "problem_url": local_problem["source_url"],
            "problem_pid": local_problem["luogu_pid"],
            "problem_title": f"{local_problem['luogu_pid']} {local_problem['title']}",
            "problem_context": build_problem_context(local_problem),
            "problem_tags": get_problem_tags(local_problem["problem_id"], tag_type="algo"),
            "oj_source": "luogu",
            "problem_id": local_problem["problem_id"],
        }

    response = requests.get(normalized_url, headers=LUOGU_HEADERS, timeout=20)
    response.raise_for_status()
    payload = response.json()
    problem = (payload.get("data") or {}).get("problem") or {}
    if not problem:
        raise ValueError("未读取到洛谷题目信息")

    pid = problem.get("pid") or extract_luogu_pid(normalized_url)
    content_title = problem.get("content") if isinstance(problem.get("content"), dict) else {}
    contenu_title = problem.get("contenu") if isinstance(problem.get("contenu"), dict) else {}
    title = (
        problem.get("title")
        or problem.get("name")
        or content_title.get("name")
        or contenu_title.get("name")
        or ""
    ).strip()
    if not title:
        raise ValueError("未读取到题目标题")

    try:
        tag_map = get_luogu_tag_map()
    except Exception:
        tag_map = {}
    tag_names = [
        tag_map.get(int(tag_id), str(tag_id))
        for tag_id in (problem.get("tags") or [])
        if str(tag_id).strip()
    ]
    tag_names = [tag for tag in tag_names if tag and classify_tag(tag) == "algo"]

    context = build_luogu_problem_context(problem)
    if not context:
        raise ValueError("未读取到题面正文，请稍后重试或手动补充题面")

    full_title = f"{pid} {title}" if pid and not title.startswith(f"{pid} ") else title
    return {
        "problem_url": normalized_url,
        "problem_pid": pid,
        "problem_title": full_title,
        "problem_context": context,
        "problem_tags": tag_names,
        "oj_source": "luogu",
    }


def _clean_jmfes_problem_html(fragment: str) -> str:
    cleaned = fragment or ""
    cleaned = re.sub(r"<span class=\"katex-mathml\">.*?</span>", "", cleaned, flags=re.S)
    cleaned = re.sub(r"<span class=\"katex-html\"[^>]*>", "", cleaned, flags=re.S)
    cleaned = re.sub(r"</span>", "", cleaned, flags=re.S)
    cleaned = re.sub(
        r"<h[1-6][^>]*>(.*?)</h[1-6]>",
        lambda m: f"\n\n## {re.sub(r'<[^>]+>', '', m.group(1)).strip()}\n",
        cleaned,
        flags=re.S,
    )
    cleaned = re.sub(
        r"<pre[^>]*><code[^>]*>(.*?)</code></pre>",
        lambda m: f"\n```text\n{unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()}\n```\n",
        cleaned,
        flags=re.S,
    )
    cleaned = re.sub(r"<li[^>]*>", "\n- ", cleaned, flags=re.S)
    cleaned = re.sub(r"</li>", "", cleaned, flags=re.S)
    cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.S)
    cleaned = re.sub(r"</p>", "\n\n", cleaned, flags=re.S)
    cleaned = re.sub(r"<p[^>]*>", "", cleaned, flags=re.S)
    cleaned = re.sub(r"<[^>]+>", "", cleaned, flags=re.S)
    cleaned = unescape(cleaned)
    cleaned = re.sub(r"\r\n?", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def fetch_jmfes_problem(raw_url: str) -> dict:
    normalized_url = normalize_jmfes_problem_url(raw_url)
    if not normalized_url:
        raise ValueError("请输入有效的 JMYSOJ 题目链接")

    response = requests.get(normalized_url, timeout=20)
    response.raise_for_status()
    html = response.text

    title_match = re.search(r"<h1 class=\"section__title\">\s*(?:#\d+\.\s*)?(.*?)\s*</h1>", html, re.S)
    content_match = re.search(r"<div class=\"problem-content\"[^>]*>(.*?)<div class=\"medium-3 columns\">", html, re.S)
    body_match = re.search(
        r"data-fragment-id=\"problem-description\"[^>]*>(.*)",
        content_match.group(1) if content_match else "",
        re.S,
    )
    pid_match = re.search(r"/p/([A-Za-z0-9_-]+)$", normalized_url)

    title = _clean_jmfes_problem_html(title_match.group(1)) if title_match else ""
    context = _clean_jmfes_problem_html(body_match.group(1)) if body_match else ""
    pid = pid_match.group(1) if pid_match else None

    if not title:
        raise ValueError("未读取到 JMYSOJ 题目标题")
    if not context:
        raise ValueError("未读取到 JMYSOJ 题面正文，请稍后重试或手动补充题面")

    return {
        "problem_url": normalized_url,
        "problem_pid": pid,
        "problem_title": title,
        "problem_context": context,
        "problem_tags": [],
        "oj_source": "jmfes",
    }


def _normalize_ai_problem_tags(raw_tags) -> list[str]:
    tags = []
    seen = set()
    for raw_tag in raw_tags or []:
        tag = str(raw_tag).strip()
        tag = re.sub(r"\s+", "", tag)
        if not tag or len(tag) > 18 or tag in seen:
            continue
        if any(ch in tag for ch in "{}[]<>`"):
            continue
        seen.add(tag)
        tags.append(tag)
        if len(tags) >= 6:
            break
    return tags


def generate_problem_tags_with_ai(
    *,
    problem_title: str,
    problem_context: str,
    oj_source: str = "",
    chat_model_provider: str | None = None,
) -> list[str]:
    context = (problem_context or "").strip()
    if not context:
        return []
    system_prompt = (
        "你是信息学竞赛题库标注助手。请只根据题目标题和题面，提取 2 到 6 个简短中文标签，"
        "优先标算法/数据结构/建模方式，例如：树、图论、最短路、差分、动态规划、二分、贪心、字符串。"
        "不要输出题解、不要推理过程、不要写代码。只输出 JSON：{\"tags\":[\"标签1\",\"标签2\"]}。"
    )
    user_text = (
        f"题源：{oj_source or 'unknown'}\n"
        f"标题：{(problem_title or '').strip()[:120]}\n"
        f"题面：{context[:4000]}"
    )
    try:
        response = _chat_completion_create(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_text}],
            provider_id=chat_model_provider,
        )
        content = response.choices[0].message.content or ""
        parsed = _extract_json_object(content)
        return _normalize_ai_problem_tags(parsed.get("tags") or [])
    except Exception as exc:
        print(f"[problem_tags] AI tag generation failed: {exc}")
        return []


def trigger_problem_analysis_if_needed_by_pid(pid: str | None):
    if not pid:
        return
    problem = get_problem_by_luogu_pid(pid)
    if not problem:
        return
    try:
        ensure_problem_analysis(problem)
    except Exception as exc:
        print(f"[problem_analysis] lazy generation failed for {pid}: {exc}")


def serialize_problem_analysis_status(problem: dict | None) -> dict | None:
    if not problem:
        return None
    analysis = get_problem_analysis(problem["problem_id"])
    if not analysis:
        return {
            "problem_id": problem["problem_id"],
            "luogu_pid": problem["luogu_pid"],
            "title": problem["title"],
            "status": "missing",
            "last_error": None,
            "retry_count": 0,
            "updated_at": None,
        }
    return {
        "problem_id": problem["problem_id"],
        "luogu_pid": problem["luogu_pid"],
        "title": problem["title"],
        "status": analysis.get("status") or "missing",
        "last_error": analysis.get("last_error"),
        "retry_count": analysis.get("retry_count", 0),
        "updated_at": analysis.get("updated_at"),
    }


# ============ Auth Models ============
class LoginRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    token: str
    user_id: str
    role: str


# ============ Chat Models ============
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    student_id: str = Field(..., min_length=1, description="学生ID")
    problem_id: str = Field(..., min_length=1, description="题目ID")
    message: str = Field(..., min_length=1, description="学生输入内容")
    session_id: str = Field(..., min_length=1, description="会话ID，用于隔离不同会话")
    problem_title: str = Field(default="", description="当前题目标题")
    problem_url: str = Field(default="", description="当前题目链接")
    problem_context: str = Field(default="", description="当前题面、约束或学生整理的题意")
    student_code: str = Field(default="", description="学生当前相关代码片段")
    chat_context_summary: str = Field(default="", description="同题上下文摘要")
    chat_model_provider: str = Field(default="", description="AIChat 模型提供方")
    aichat_prompt_mode: str = Field(default="current_system", description="AIChat 回答方式")


class ChatResponse(BaseModel):
    reply: str
    remaining_quota: int
    level: str
    handoff_payload: Optional[dict] = None
    understanding_state: str = "not_ready"
    understanding_evidence: List[str] = Field(default_factory=list)
    chat_model_provider: str = ""
    chat_model_label: str = ""
    aichat_prompt_mode: str = "current_system"
    aichat_prompt_mode_label: str = "简洁提示"


class BridgeResearchAnnotationRequest(BaseModel):
    sample_id: str = Field(..., min_length=1)
    student_message_id: int
    student_state: str = Field(..., min_length=1)
    bridge_family: str = Field(..., min_length=1)
    known_focus: str = Field(default="unknown")
    help_seeking_type: str = Field(..., min_length=1)
    missing_link: str = Field(..., min_length=1)
    allowed_help_level: Literal["L1", "L2", "L3"]
    forbidden_completion: str = Field(..., min_length=1)
    needs_new_focus: bool = False
    confidence: int = Field(default=0, ge=0, le=5)
    notes: str = ""


class ResponseReviewLabelRequest(BaseModel):
    dataset_id: str = ""
    anonymized_response_id: str = Field(..., min_length=1)
    case_id: str = ""
    overall_quality: str = Field(..., min_length=1)
    leakage_label: str = Field(..., min_length=1)
    preference_rank: str = ""
    notes: str = ""
    review_status: str = "labeled"


class UnderstandingCheckGenerateRequest(BaseModel):
    problem_id: str = Field(default="")
    session_id: str = Field(default="")
    problem_title: str = Field(default="")
    problem_context: str = Field(default="")
    student_code: str = Field(default="")
    chat_model_provider: str = Field(default="")


class UnderstandingCheckGradeRequest(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    target_focus: str = Field(default="")
    quiz_format: str = Field(default="")
    problem_id: str = Field(default="")
    session_id: str = Field(default="")
    problem_title: str = Field(default="")
    problem_context: str = Field(default="")
    student_code: str = Field(default="")
    chat_model_provider: str = Field(default="")


class ProblemClosureStartRequest(BaseModel):
    problem_id: str = Field(default="")
    session_id: str = Field(default="")
    problem_title: str = Field(default="")
    problem_context: str = Field(default="")
    student_code: str = Field(default="")
    chat_model_provider: str = Field(default="")


class ProblemClosureGradeRequest(BaseModel):
    closure_id: int = Field(..., ge=1)
    answer: str = Field(..., min_length=1)
    quiz_format: str = Field(default="")
    problem_id: str = Field(default="")
    session_id: str = Field(default="")
    problem_title: str = Field(default="")
    problem_context: str = Field(default="")
    student_code: str = Field(default="")
    chat_model_provider: str = Field(default="")


class CodeRunRequest(BaseModel):
    language: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    stdin: str = Field(default="")
    expected_output: str = Field(default="")
    problem_ref: str = Field(default="")


class CodeRunResponse(BaseModel):
    status: str
    message: str
    stdout: str = ""
    stderr: str = ""
    compile_output: str = ""
    elapsed_ms: int = 0
    exit_code: Optional[int] = None
    matched_expected: Optional[bool] = None
    output_limited: bool = False


class StudentFeedbackRequest(BaseModel):
    category: Literal["aichat", "checkin", "code", "page", "other"] = "other"
    rating: int = Field(..., ge=1, le=5)
    content: str = Field(..., min_length=1)
    page_context: str = Field(default="")


class StudentProblemCompletionRequest(BaseModel):
    problem_id: str = Field(default="")
    problem_title: str = Field(default="")
    problem_url: str = Field(default="")
    reported_completion: Literal[
        "self_solved",
        "small_hint",
        "classroom_taught",
        "aichat_assisted",
        "editorial_completed",
        "unsure",
    ] = "unsure"
    result_status: Literal["accepted", "sample_passed", "unsure"] = "unsure"
    key_step_summary: str = Field(..., min_length=6, max_length=500)
    session_id: str = Field(default="")


class TeacherAnnouncementRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=80)
    body_markdown: str = Field(..., min_length=1, max_length=5000)
    pinned: bool = True
    status: Literal["published", "draft"] = "published"


class TeacherAnnouncementStatusRequest(BaseModel):
    status: Literal["published", "draft", "archived"]


def _compact_chat_context_line(label: str, value: str, max_chars: int = 1200) -> Optional[str]:
    text = (value or "").strip()
    if not text:
        return None
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "..."
    return f"{label}: {text}"


def _has_chat_problem_context(request: ChatRequest) -> bool:
    return any(
        [
            bool(request.problem_title.strip()),
            bool(request.problem_url.strip()),
            len(request.problem_context.strip()) >= 10,
        ]
    )


def _build_chat_context_strategy(request: ChatRequest) -> list[str]:
    has_problem = _has_chat_problem_context(request)
    has_code = bool(request.student_code.strip())

    if has_problem and has_code:
        return [
            "上下文状态：有题目 + 有代码",
            "回答策略：必须结合题面目标、学生问题和学生代码；先对齐题目目标与代码实现，再定位一个最小可疑位置。",
            "边界：可以指出可疑行、变量含义或判断条件的不一致，但不要直接给最终代码。",
        ]
    if has_problem and not has_code:
        return [
            "上下文状态：有题目 + 无代码",
            "回答策略：苏格拉底提问为主，基于题面证据和学生原话搭台阶；不要突然抛出学生尚未铺垫过的算法术语。",
            "费曼验证：只在关键小步后让学生用自己的话复述当前小关系，不要展开成长讲解。",
        ]
    if not has_problem and has_code:
        return [
            "上下文状态：无题目 + 有代码",
            "回答策略：先说明现在只看到了代码，但不知道题目目标；请学生先补题目链接或题号。",
            "边界：不要先分析代码，不要猜题意，不能判断算法是否正确。",
        ]
    return [
        "上下文状态：无题目 + 无代码",
        "回答策略：先索取最小上下文，包括题号/链接、简短题意、学生卡在哪一步。",
        "边界：不要直接进入算法教学，不要猜题型，不要给通用题解。",
    ]


def build_chat_message_with_problem_context(request: ChatRequest, memory_summary: str = "") -> str:
    context_lines = [
        _compact_chat_context_line("题目标题", request.problem_title, 200),
        _compact_chat_context_line("题目链接", request.problem_url, 300),
        _compact_chat_context_line("同题短摘要记忆", memory_summary, 1000),
        _compact_chat_context_line("题面/题意/约束", request.problem_context, 1800),
        _compact_chat_context_line("学生当前代码", request.student_code, 1800),
        _compact_chat_context_line("同题上下文摘要", request.chat_context_summary, 800),
    ]
    context_lines = [line for line in context_lines if line]
    return "\n".join([
        "[学生原始问题]",
        request.message,
        "",
        "[当前上下文状态与回答策略]",
        *_build_chat_context_strategy(request),
        "",
        "[当前题目上下文：只用于理解学生卡点，不要直接照抄题解]",
        *context_lines,
        "",
        "请优先围绕学生当前问题给渐进提示；即使学生要求完整代码，也不要直接给最终代码；只指出当前最小卡点和下一步验证方式。",
    ])


def enrich_chat_request_with_luogu_context(request: ChatRequest) -> ChatRequest:
    has_enough_context = bool(request.problem_title.strip()) and len(request.problem_context.strip()) >= 10
    if has_enough_context:
        return request

    problem_ref = (request.problem_url or request.problem_id or "").strip()
    normalized_luogu_url = normalize_luogu_problem_url(problem_ref)
    normalized_jmfes_url = normalize_jmfes_problem_url(problem_ref)
    normalized_url = normalized_luogu_url or normalized_jmfes_url
    if not normalized_url:
        return request

    try:
        if normalized_luogu_url:
            imported_problem = fetch_luogu_problem(normalized_url)
        else:
            imported_problem = fetch_jmfes_problem(normalized_url)
    except Exception as exc:
        print(f"[chat_context] luogu import skipped for {problem_ref}: {exc}")
        return request

    if not request.problem_url.strip():
        request.problem_url = imported_problem.get("problem_url") or normalized_url
    if not request.problem_title.strip():
        request.problem_title = imported_problem.get("problem_title") or ""
    if len(request.problem_context.strip()) < 10:
        request.problem_context = imported_problem.get("problem_context") or request.problem_context
    return request


# ============ Quota Models ============
class QuotaResponse(BaseModel):
    student_id: str
    problem_id: str
    count: int
    max: int
    remaining: int


class ResetQuotaRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    problem_id: str = Field(..., min_length=1)
    teacher_secret: str = Field(..., min_length=1, description="教师密钥")


# ============ Checkin Models ============
class CheckinRequest(BaseModel):
    problem_url: str = Field(default="")
    problem_title: str = Field(default="")
    oj_source: str = Field(..., pattern="^(luogu|jmfes|codeforces|atcoder|other)$")
    completion_status: str = Field(..., pattern="^(independent|hinted|editorial|unfinished)$")
    bottleneck_text: str = Field(..., min_length=15)
    error_types: List[str] = Field(..., min_items=1)
    reflection: Optional[str] = None
    problem_context: str = Field(default="", description="题面正文或 Markdown：至少说清楚题意、样例或关键约束")
    problem_tags: List[str] = Field(default_factory=list)
    chat_context_summary: str = Field(default="", description="同题近期 AI 解答摘要，仅作辅助线索")
    submission_result: Optional[Literal["not_submitted", "wa", "tle", "re", "ce", "unknown"]] = None
    student_code: Optional[str] = None
    handoff_payload: Optional[dict] = Field(default=None, description="AIChat 移交 payload（v0 合约）")


class CheckinResponse(BaseModel):
    checkin_id: int
    session_id: Optional[str] = None
    review_status: str
    review_mode: Optional[str] = None
    review_family: Optional[str] = None
    review: Optional[dict] = None
    message: str


class CheckinStatusResponse(BaseModel):
    checkin_id: int
    session_id: Optional[str] = None
    problem_title: str
    problem_url: Optional[str] = None
    oj_source: Optional[str] = None
    created_at: str
    completion_status: Optional[str] = None
    submission_result: Optional[str] = None
    student_id: Optional[str] = None
    bottleneck_text: Optional[str] = None
    reflection: Optional[str] = None
    problem_context: Optional[str] = None
    error_types: List[str] = Field(default_factory=list)
    student_code: Optional[str] = None
    review_status: str
    review_mode: Optional[str] = None
    review_family: Optional[str] = None
    learning_status: Optional[str] = None
    review: Optional[dict] = None
    quiz_history: Optional[List[dict]] = None
    review_last_error: Optional[str] = None


class ReviewEventRequest(BaseModel):
    checkin_id: int
    session_id: str = Field(..., min_length=1)
    event_name: Literal["review_request_submitted", "review_shown", "review_feedback_submitted"]
    client_ts: Optional[str] = None
    app_version: Optional[str] = None
    user_id: Optional[str] = None
    problem_id: Optional[str] = None
    problem_title: Optional[str] = None
    has_code: Optional[bool] = None
    problem_context_length: Optional[int] = Field(default=None, ge=0)
    bottleneck_text_length: Optional[int] = Field(default=None, ge=0)
    student_feedback: Optional[Literal["understood", "neutral", "confused"]] = None
    bad_reason: Optional[str] = None
    followup_clicked: Optional[bool] = None
    followup_question_count: Optional[int] = Field(default=None, ge=0)
    latency_ms: Optional[int] = Field(default=None, ge=0)
    review_text_length: Optional[int] = Field(default=None, ge=0)


class ReviewEventResponse(BaseModel):
    status: str = "ok"


class TeacherManualReviewRequest(BaseModel):
    mode_correct: Literal["correct", "incorrect", "unsure"]
    review_grounded: Literal["grounded", "mixed", "vague"]
    student_can_move_next: Literal["yes", "no", "unsure"]
    notes: str = Field(default="", max_length=500)


class TeacherStudentCreateRequest(BaseModel):
    display_name: str = Field(..., min_length=1, description="显示姓名")
    user_id: str = Field(default="", description="登录账号，留空则自动生成")
    password: str = Field(default="", description="初始密码，留空则自动生成")


class TeacherStudentBulkCreateRow(BaseModel):
    row_index: Optional[int] = None
    display_name: str = Field(default="", description="显示姓名")
    user_id: str = Field(default="", description="登录账号，留空则自动生成")
    password: str = Field(default="", description="初始密码，留空则自动生成")


class TeacherStudentBulkCreateRequest(BaseModel):
    rows: List[TeacherStudentBulkCreateRow] = Field(default_factory=list)


class TeacherStudentPasswordResetRequest(BaseModel):
    password: str = Field(default="", description="新密码，留空则自动生成")


class TeacherChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, description="当前密码")
    new_password: str = Field(..., min_length=4, description="教师自己输入的新密码")
    confirm_password: str = Field(..., min_length=4, description="再次输入新密码")


class TeacherStudentStatusRequest(BaseModel):
    active: bool


class TeacherStudentNoteRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    note: str = Field(..., min_length=1, max_length=2000)
    status: Literal["handled", "continue_followup", "watch", "resolved"] = "continue_followup"
    next_followup_at: str = Field(default="", max_length=80)
    intervention_type: str = Field(default="", max_length=80)
    target_issue: str = Field(default="", max_length=120)


class AichatSessionAnalysisRetryRequest(BaseModel):
    session_id: str = Field(..., min_length=1)


class BridgeRuleDraftDecisionRequest(BaseModel):
    route_kind: Literal["candidate_bridge", "open_bridge"]
    bridge_id: str = Field(..., min_length=1, max_length=160)
    decision: Literal["confirmed", "rejected", "needs_changes"]
    notes: str = Field(default="", max_length=500)
    days: int = Field(default=30, ge=1, le=365)


class BridgeRegistryEntryRequest(BaseModel):
    decision_id: int = Field(..., ge=1)


class ProblemImportRequest(BaseModel):
    url: str = Field(..., min_length=1, description="洛谷题号或题目链接")


class ProblemImportResponse(BaseModel):
    problem_url: str
    problem_pid: Optional[str] = None
    problem_title: str
    problem_context: str
    problem_tags: List[str] = Field(default_factory=list)
    oj_source: str = "luogu"
    message: str = "导入成功"


class RelatedProblemsResponse(BaseModel):
    pid: str
    related: List[dict] = Field(default_factory=list)


# ============ Teacher Dashboard Models ============
class TeacherCheckinItem(BaseModel):
    id: int
    student_id: str
    problem_title: str
    oj_source: str
    completion_status: str
    bottleneck_text: str
    error_types: List[str]
    created_at: str
    has_review: bool
    review_status: Optional[str] = None
    review_error_layer: Optional[str] = None
    review_confidence: Optional[str] = None
    review_last_error: Optional[str] = None


class ErrorStatItem(BaseModel):
    error_type: str
    count: int
    avg_completion_score: float


class StudentFlagItem(BaseModel):
    student_id: str
    flag_type: str
    description: str
    severity: str


class RetryPendingReviewsRequest(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)


class ProblemAnalysisRetryRequest(BaseModel):
    luogu_pid: str = Field(..., min_length=1, description="洛谷题号，如 P1003")


class QuizAnswerRequest(BaseModel):
    answer_text: str = Field(..., min_length=1)


class SelfCheckRequest(BaseModel):
    status: Literal["clear", "guessed", "confused"]


class RemedyActionRequest(BaseModel):
    action_type: Literal["rephrase", "smaller_example", "dynamic_bridge_help", "easier_quiz"]


class RemedyResolveRequest(BaseModel):
    status: Literal["resolved", "needs_teacher_followup"]


# ============ Helper Functions ============
def build_quota_response(student_id: str, problem_id: str) -> QuotaResponse:
    quota = load_quota(student_id, problem_id)
    return QuotaResponse(
        student_id=student_id,
        problem_id=problem_id,
        count=quota["count"],
        max=quota["max"],
        remaining=get_remaining_quota(student_id, problem_id),
    )


def dynamic_remedy_label(error_layer: str) -> str:
    return {
        "reading": "我还是没看清这题到底要我做什么",
        "method": "我还是看不出来为什么该用这个方法",
        "modeling": "我还是不知道怎么把题目变成模型",
        "core_design": "我还是不明白这一步为什么这样设计",
        "implementation": "我还是不知道这一步代码怎么写",
        "insufficient": "我还是说不清自己具体卡在哪",
    }.get(error_layer or "insufficient", "我还是说不清自己具体卡在哪")


def serialize_quiz(quiz: dict | None) -> dict | None:
    if not quiz:
        return None
    return {
        "quiz_id": quiz["id"],
        "review_id": quiz["review_id"],
        "round": quiz["round"],
        "quiz_role": quiz["quiz_role"],
        "quiz_type": quiz["quiz_type"],
        "question_text": quiz["question_text"],
        "options": quiz["options"],
        "status": quiz["status"],
        "explanation": quiz["explanation"],
        "bridge_feedback": quiz.get("bridge_feedback", ""),
        "distractor_feedback": quiz.get("distractor_feedback", {}),
        "target_bridge": quiz["target_bridge"],
        "meta": quiz.get("meta", {}),
        "latest_answer_text": quiz.get("latest_answer_text"),
        "latest_is_correct": quiz.get("latest_is_correct"),
        "latest_feedback_text": quiz.get("latest_feedback_text"),
    }


def get_quiz_option_value(option) -> str:
    if isinstance(option, dict):
        return str(option.get("value", "")).strip()
    return str(option or "").strip()


def normalize_quiz_answer(answer_text: str, quiz_type: str) -> str:
    answer = (answer_text or "").strip()
    if quiz_type == "judgement":
        lowered = answer.lower()
        if lowered in {"true", "yes", "y", "1", "对", "正确"}:
            return "对"
        if lowered in {"false", "no", "n", "0", "错", "错误"}:
            return "错"
    return answer


def is_quiz_answer_correct(quiz: dict, answer_text: str) -> bool:
    answer = normalize_quiz_answer(answer_text, quiz["quiz_type"])
    correct = normalize_quiz_answer(quiz["correct_answer"], quiz["quiz_type"])
    if quiz["quiz_type"] == "short_fill":
        norm = lambda s: "".join((s or "").lower().split())
        return norm(answer) == norm(correct)
    return answer == correct


def selected_distractor_feedback(quiz: dict, answer_text: str) -> str:
    answer = normalize_quiz_answer(answer_text, quiz["quiz_type"])
    distractor_feedback = quiz.get("distractor_feedback") or {}
    if not isinstance(distractor_feedback, dict):
        return ""
    return str(distractor_feedback.get(answer, "")).strip()


def fallback_feedback_text(payload: dict, default: str = "") -> str:
    if not isinstance(payload, dict):
        return default
    return str(payload.get("fallback_explain") or payload.get("explanation") or default).strip()


def is_legacy_judgement_quiz(quiz: dict | None) -> bool:
    return bool(quiz and quiz.get("status") == "pending" and quiz.get("quiz_type") == "judgement")


def is_legacy_process_advice_quiz(quiz: dict | None) -> bool:
    if not quiz or quiz.get("status") != "pending":
        return False
    question_text = str(quiz.get("question_text", "")).strip()
    process_patterns = (
        "更该先",
        "是不是先要",
        "先做什么",
        "先确定什么",
        "先看清哪件事",
        "先补哪一小步",
    )
    if any(pattern in question_text for pattern in process_patterns):
        return True
    options = quiz.get("options") or []
    labels = []
    for option in options:
        if isinstance(option, dict):
            labels.append(str(option.get("label", "")).strip())
        else:
            labels.append(str(option).strip())
    if not labels:
        return False
    starts_with_process = sum(1 for label in labels if label.startswith("先"))
    structural_markers = (
        "dp[",
        "check(",
        "状态",
        "转移",
        "定义",
        "顺序",
        "条件",
        "表示",
        "是否可行",
        "复杂度",
        "base case",
    )
    has_structural_marker = any(any(marker in label for marker in structural_markers) for label in labels)
    return starts_with_process >= 2 and not has_structural_marker


def is_stale_pending_quiz(quiz: dict | None) -> bool:
    return is_legacy_judgement_quiz(quiz) or is_legacy_process_advice_quiz(quiz)


def replacement_learning_status_for_legacy_quiz(quiz_role: str) -> str:
    if quiz_role == QUIZ_ROLE_MAIN:
        return LEARNING_STATUS_NOT_STARTED
    return LEARNING_STATUS_REMEDY_AVAILABLE


def replace_legacy_pending_quiz(review_context: dict, stale_quiz: dict) -> dict | None:
    quizzes = get_quizzes_for_review(review_context["review_id"])
    previous_quiz = None
    for quiz in quizzes:
        if quiz["id"] == stale_quiz["id"]:
            break
        if quiz.get("status") != "replaced":
            previous_quiz = quiz

    payload = generate_bridge_quiz(
        review_context,
        previous_quiz=previous_quiz,
        quiz_role=stale_quiz["quiz_role"],
    )

    update_quiz_status(stale_quiz["id"], "replaced")

    if payload.get("mode") != "quiz":
        update_review_learning_status(
            review_context["review_id"],
            replacement_learning_status_for_legacy_quiz(stale_quiz["quiz_role"]),
        )
        return None

    quiz_id = create_review_quiz(
        review_id=review_context["review_id"],
        student_id=review_context["student_id"],
        checkin_id=review_context["checkin_id"],
        round=stale_quiz["round"],
        quiz_role=stale_quiz["quiz_role"],
        quiz_type=payload["quiz_type"],
        question_text=payload["question_text"],
        options=payload["options"],
        correct_answer=payload["correct_answer"],
        explanation=payload["explanation"],
        bridge_feedback=payload.get("bridge_feedback", ""),
        distractor_feedback=payload.get("distractor_feedback", {}),
        target_bridge=payload["target_bridge"],
        source_error_layer=review_context["error_layer"],
        meta={
            **payload.get("meta", {}),
            "replaces_legacy_quiz_id": stale_quiz["id"],
        },
    )
    return get_quiz_by_id(quiz_id)


def migrate_pending_judgement_quizzes(limit: int = 100) -> dict:
    stale_quizzes = get_pending_judgement_quizzes(limit)
    summary = {"found": len(stale_quizzes), "replaced": 0, "fallback_reset": 0}
    for stale_quiz in stale_quizzes:
        review_context = get_review_context(stale_quiz["review_id"])
        if not review_context:
            update_quiz_status(stale_quiz["id"], "replaced")
            continue
        replacement = replace_legacy_pending_quiz(review_context, stale_quiz)
        if replacement:
            summary["replaced"] += 1
        else:
            summary["fallback_reset"] += 1
    return summary


def migrate_pending_stale_quizzes(limit: int = 100) -> dict:
    candidates = get_pending_quizzes(limit)
    stale_quizzes = [quiz for quiz in candidates if is_stale_pending_quiz(quiz)]
    summary = {"found": len(stale_quizzes), "replaced": 0, "fallback_reset": 0}
    for stale_quiz in stale_quizzes:
        review_context = get_review_context(stale_quiz["review_id"])
        if not review_context:
            update_quiz_status(stale_quiz["id"], "replaced")
            continue
        replacement = replace_legacy_pending_quiz(review_context, stale_quiz)
        if replacement:
            summary["replaced"] += 1
        else:
            summary["fallback_reset"] += 1
    return summary


def compute_bridge_path(review_context: dict, quizzes: list[dict], terminal_status: str) -> str | None:
    if terminal_status not in {LEARNING_STATUS_RESOLVED, LEARNING_STATUS_NEEDS_TEACHER}:
        return None

    self_check = review_context.get("understanding_self_check")
    quiz_roles = [quiz.get("quiz_role") for quiz in quizzes]
    has_knowledge_confirm = QUIZ_ROLE_KNOWLEDGE_CONFIRM in quiz_roles
    has_knowledge_confirm_correct = any(
        quiz.get("quiz_role") == QUIZ_ROLE_KNOWLEDGE_CONFIRM and quiz.get("status") == "correct"
        for quiz in quizzes
    )
    has_confirm = QUIZ_ROLE_CONFIRM in quiz_roles
    has_confirm_correct = any(
        quiz.get("quiz_role") == QUIZ_ROLE_CONFIRM and quiz.get("status") == "correct"
        for quiz in quizzes
    )
    has_followup_correct = any(
        quiz.get("quiz_role") == QUIZ_ROLE_FOLLOWUP and quiz.get("status") == "correct"
        for quiz in quizzes
    )
    remedy_count = review_context.get("remedy_count") or 0

    if has_knowledge_confirm_correct and terminal_status == LEARNING_STATUS_RESOLVED:
        return "knowledge_bailout_success"
    if has_knowledge_confirm and terminal_status == LEARNING_STATUS_NEEDS_TEACHER:
        return "knowledge_bailout_failed"

    if self_check == "clear":
        return "main_clear"
    if self_check == "guessed":
        if has_confirm_correct:
            return "main_guessed_confirm"
        if has_confirm or remedy_count > 0:
            return "main_guessed_remedy"
        return None
    if self_check == "confused":
        if remedy_count > 0 or terminal_status == LEARNING_STATUS_NEEDS_TEACHER:
            return "main_confused_remedy"
        return None

    if has_followup_correct:
        return "followup_correct"
    if QUIZ_ROLE_FOLLOWUP in quiz_roles or remedy_count > 0:
        return "followup_remedy"
    return None


def compute_mastery_status(bridge_path: str | None, terminal_status: str) -> str:
    if terminal_status == LEARNING_STATUS_NEEDS_TEACHER:
        return MASTERY_STATUS_NOT_MASTERED
    if terminal_status != LEARNING_STATUS_RESOLVED:
        return MASTERY_STATUS_NOT_ASSESSED
    if bridge_path == "main_clear":
        return MASTERY_STATUS_INDEPENDENT_SUCCESS
    if bridge_path in {
        "main_guessed_confirm",
        "main_guessed_remedy",
        "main_confused_remedy",
        "followup_correct",
        "followup_remedy",
        "knowledge_bailout_success",
    }:
        return MASTERY_STATUS_ASSISTED_SUCCESS
    return MASTERY_STATUS_NOT_ASSESSED


def finalize_review_terminal_state(review_id: int, status: str):
    update_review_learning_status(review_id, status)
    review_context = get_review_context(review_id)
    if not review_context:
        return
    quizzes = get_quizzes_for_review(review_id)
    bridge_path = compute_bridge_path(review_context, quizzes, status)
    if bridge_path:
        update_review_bridge_path(review_id, bridge_path)
    else:
        print(f"[bridge_path] unable to infer route for review {review_id} with status {status}")
    update_review_mastery_status(review_id, compute_mastery_status(bridge_path, status))


def _generate_and_store_review(
    checkin_id: int,
    student_id: str,
    problem_title: str,
    oj_source: str,
    completion_status: str,
    bottleneck_text: str,
    error_types: List[str],
    reflection: Optional[str],
    problem_context: Optional[str] = None,
    problem_tags: Optional[List[str]] = None,
    chat_context_summary: Optional[str] = None,
    problem_card: Optional[dict] = None,
    analysis_source: Optional[str] = None,
    local_problem_id: Optional[int] = None,
    submission_result: Optional[str] = None,
    student_code: Optional[str] = None,
    handoff_payload: Optional[dict] = None,
):
    started_at = time.perf_counter()
    try:
        def handle_review_draft(_raw_text: str, draft_preview: dict):
            if draft_preview:
                update_checkin_runtime_draft(checkin_id, draft_preview)

        update_checkin_runtime_status(checkin_id, "llm_start", REVIEW_STATUS_PENDING, "正在调用模型")
        create_pending_review(checkin_id, student_id)
        mark_review_attempt(checkin_id)

        review_result = generate_review(
            problem_title=problem_title,
            oj_source=oj_source,
            completion_status=completion_status,
            bottleneck_text=bottleneck_text,
            error_types=error_types,
            reflection=reflection,
            problem_context=problem_context,
            problem_tags=problem_tags,
            chat_context_summary=chat_context_summary,
            problem_card=problem_card,
            submission_result=submission_result,
            student_code=student_code,
            draft_callback=handle_review_draft,
            handoff_payload=handoff_payload,
        )
    except Exception as exc:
        error_message = f"{type(exc).__name__}: {exc}"
        print(f"[review_retry] review generation exception for checkin {checkin_id}: {error_message}")
        try:
            create_pending_review(checkin_id, student_id)
            mark_review_failed(checkin_id, error_message)
            update_checkin_runtime_status(checkin_id, "failed", "failed", "复盘生成失败，可稍后重试")
        except Exception as persist_exc:
            print(f"[review_retry] failed to persist pending state for checkin {checkin_id}: {persist_exc}")
        return {
            "ok": False,
            "kind": "review_exception",
            "message": "AI 复盘服务暂时不可用，你的打卡已保存，请稍后查看或联系老师",
        }

    update_checkin_runtime_status(checkin_id, "llm_done", REVIEW_STATUS_PENDING, "模型已返回，正在整理内容")
    telemetry = review_result.get("telemetry") or {}
    latency_ms = int((time.perf_counter() - started_at) * 1000)
    create_review_session(
        student_id=student_id,
        problem_id=local_problem_id,
        checkin_id=checkin_id,
        prompt_tokens=int(telemetry.get("prompt_tokens") or 0),
        completion_tokens=int(telemetry.get("completion_tokens") or 0),
        latency_ms=latency_ms,
        model_tier="standard" if student_code else "lite",
        analysis_source=analysis_source,
        prompt_cache_hit=False,
        review_result_json={
            "kind": review_result.get("kind"),
            "ok": review_result.get("ok"),
            "error_layer": (review_result.get("review") or {}).get("error_layer"),
        },
    )

    if not review_result["ok"]:
        mark_review_failed(checkin_id, review_result["message"])
        update_checkin_runtime_status(checkin_id, "failed", "failed", "复盘生成失败，可稍后重试")
        return review_result

    review_data = review_result["review"]
    try:
        update_checkin_runtime_status(checkin_id, "review_parse", REVIEW_STATUS_PENDING, "正在整理复盘内容")
        create_review(
            checkin_id=checkin_id,
            student_id=student_id,
            error_tags=review_data["error_tags"],
            diagnosis=review_data["diagnosis"],
            next_action=review_data["next_action"],
            suggested_topic=review_data["suggested_topic"],
            error_layer=review_data["error_layer"],
            error_layer_confidence=review_data["error_layer_confidence"],
            core_design_subtags=review_data["core_design_subtags"],
            main_block=review_data["main_block"],
            key_bridge=review_data["key_bridge"],
            next_step=review_data["next_step"],
            transfer_signal=review_data["transfer_signal"],
            problem_focus=review_data.get("problem_focus", review_data["main_block"]),
            visual_hint=review_data.get("visual_hint", ""),
            guided_walkthrough=review_data.get("guided_walkthrough", ""),
            try_now=review_data.get("try_now", review_data["next_step"]),
            review_quality_flags=review_result.get("review_quality_flags", []),
            bridge_route_meta=review_result.get("bridge_route_meta", {}),
        )
    except Exception as exc:
        error_message = f"{type(exc).__name__}: {exc}"
        print(f"[review_retry] review persistence exception for checkin {checkin_id}: {error_message}")
        mark_review_failed(checkin_id, error_message)
        update_checkin_runtime_status(checkin_id, "failed", "failed", "复盘生成失败，可稍后重试")
        return {
            "ok": False,
            "kind": "review_exception",
            "message": "AI 复盘已排队，结果保存稍后会自动重试，请稍后查看",
        }
    update_checkin_runtime_status(checkin_id, "review_saved", REVIEW_STATUS_PENDING, "复盘已生成，正在准备理解检查")
    update_checkin_runtime_status(checkin_id, "quiz_generating", REVIEW_STATUS_PENDING, "正在准备理解检查")
    update_checkin_runtime_status(checkin_id, "completed", REVIEW_STATUS_COMPLETED, "复盘已就绪")
    return review_result


def _generate_and_store_review_limited(*args, **kwargs):
    with _review_generation_semaphore:
        return _generate_and_store_review(*args, **kwargs)


def _start_review_generation_job(**kwargs):
    worker = threading.Thread(
        target=_generate_and_store_review_limited,
        kwargs=kwargs,
        daemon=True,
    )
    worker.start()
    return worker


def _start_problem_analysis_job(pid: str):
    worker = threading.Thread(
        target=trigger_problem_analysis_if_needed_by_pid,
        args=(pid,),
        daemon=True,
    )
    worker.start()
    return worker


def retry_pending_reviews(limit: int = 10) -> dict:
    if not is_review_llm_configured():
        return {
            "attempted": 0,
            "completed": 0,
            "still_pending": 0,
            "message": "复盘生成模型 API Key 未配置，已跳过待生成复盘重试",
        }

    jobs = get_pending_review_jobs(limit)
    summary = {
        "attempted": 0,
        "completed": 0,
        "still_pending": 0,
        "message": "未找到待生成复盘",
    }

    for job in jobs:
        problem_card = None
        analysis_source = None
        local_problem_id = None
        if job["oj_source"] == "luogu":
            problem_card, analysis_source = get_problem_card_by_ref(job.get("problem_url"))
            pid = extract_luogu_pid(job.get("problem_url") or "")
            local_problem = get_problem_by_luogu_pid(pid) if pid else None
            if local_problem:
                local_problem_id = local_problem["problem_id"]
        summary["attempted"] += 1
        result = _generate_and_store_review(
            checkin_id=job["checkin_id"],
            student_id=job["student_id"],
            problem_title=job["problem_title"],
            oj_source=job["oj_source"],
            completion_status=job["completion_status"],
            bottleneck_text=job["bottleneck_text"],
            error_types=job["error_types"],
            reflection=job["reflection"],
            problem_context=job.get("problem_context"),
            problem_tags=job.get("problem_tags") or [],
            chat_context_summary=job.get("chat_context_summary") or "",
            problem_card=problem_card,
            analysis_source=analysis_source,
            local_problem_id=local_problem_id,
            submission_result=job.get("submission_result"),
            student_code=job.get("student_code"),
        )
        if result["ok"]:
            summary["completed"] += 1
        else:
            summary["still_pending"] += 1

    if summary["attempted"] > 0:
        summary["message"] = (
            f"已尝试重试 {summary['attempted']} 条待生成复盘，"
            f"成功 {summary['completed']} 条，仍待生成 {summary['still_pending']} 条"
        )
    return summary


def _run_startup_repair_jobs():
    try:
        summary = retry_pending_reviews(limit=10)
        if summary["attempted"] or "跳过" in summary["message"]:
            print(f"[review_retry] {summary['message']}")
        legacy_summary = migrate_pending_stale_quizzes(limit=100)
        if legacy_summary["found"]:
            print(
                "[quiz_migration] 已检查旧小测："
                f"发现 {legacy_summary['found']} 条，"
                f"替换 {legacy_summary['replaced']} 条，"
                f"重置为解释路径 {legacy_summary['fallback_reset']} 条"
            )
    except Exception as exc:
        print(f"[review_retry] startup retry failed: {exc}")


@app.on_event("startup")
def retry_pending_reviews_on_startup():
    worker = threading.Thread(
        target=_run_startup_repair_jobs,
        daemon=True,
    )
    worker.start()


# ============ Auth Endpoints ============
@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """Authenticate user and return token"""
    user = authenticate_user(request.user_id, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid user_id or password",
        )
    
    token = create_token(user["id"], user["role"])
    return LoginResponse(
        token=token,
        user_id=user["id"],
        role=user["role"],
    )


@app.get("/api/health/runner")
def code_runner_healthcheck() -> dict:
    return get_runner_health().to_dict()


@app.post("/api/student/code/run", response_model=CodeRunResponse)
def run_student_code_endpoint(
    request: CodeRunRequest,
    user: dict = Depends(require_student),
):
    if request.language != "cpp17":
        return CodeRunResponse(
            status="invalid_request",
            message="目前只支持 C++17 代码运行。",
        )
    return CodeRunResponse(**run_cpp17_sample(
        code=request.code,
        stdin=request.stdin,
        expected_output=request.expected_output,
    ))


@app.get("/api/chat/models")
def get_chat_models_endpoint(user: dict = Depends(require_student)):
    return list_chat_model_options()


def _update_aichat_problem_memory_after_chat(
    *,
    student_id: str,
    problem_id: str,
    session_id: str,
    old_summary: str,
    student_message: str,
    assistant_reply: str,
    problem_context: str,
    student_code: str,
    provider_id: str = "",
) -> None:
    try:
        new_summary = summarize_aichat_problem_memory(
            old_summary=old_summary,
            student_message=student_message,
            assistant_reply=assistant_reply,
            problem_context=problem_context,
            student_code=student_code,
            provider_id=provider_id or None,
        )
        if new_summary.strip():
            upsert_aichat_problem_memory(
                student_id=student_id,
                problem_id=problem_id,
                summary=new_summary,
                source_session_id=session_id,
            )
    except Exception as exc:
        print(f"[aichat_memory] update skipped: {type(exc).__name__}: {exc}")


def _schedule_aichat_problem_memory_update(**kwargs) -> None:
    thread = threading.Thread(
        target=_update_aichat_problem_memory_after_chat,
        kwargs=kwargs,
        daemon=True,
    )
    thread.start()


TURN_TAGGER_PROMPT_VERSION = "turn_tagger_v1.0.0"
SESSION_ANALYST_PROMPT_VERSION = "session_analyst_v1.0.0"


def _is_aichat_turn_tagger_enabled() -> bool:
    raw = (os.environ.get("NOI_TURN_TAGGER_ENABLED") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _run_aichat_turn_tagging(
    *,
    student_id: str,
    student_username: str = "",
    student_real_name: str = "",
    problem_id: str = "",
    session_id: str = "",
    turn_id: str = "",
    user_input: str,
    messages: list,
    problem_context: dict | None = None,
    student_code: str = "",
    rule_weak_signals: list[str] | None = None,
) -> None:
    """Run Turn Tagger in the background and persist its observer labels."""
    try:
        tag = tag_aichat_turn(
            user_input=user_input,
            messages=messages,
            problem_context=problem_context,
            student_code=student_code,
            rule_weak_signals=rule_weak_signals,
        )
        if tag.get("_failed"):
            print(f"[aichat_turn_tagger] skipped failed={tag.get('_reason')}")
            return
        record_aichat_turn_tag(
            student_id=student_id,
            student_username=student_username or student_id,
            student_real_name=student_real_name or student_username or student_id,
            problem_id=problem_id,
            session_id=session_id,
            turn_id=turn_id,
            role="student",
            primary_intent=tag.get("primary_intent", ""),
            learning_issue=tag.get("learning_issue", ""),
            understanding_evidence=tag.get("understanding_evidence") or [],
            missing_evidence=tag.get("missing_evidence") or [],
            risk_flags=tag.get("risk_flags") or [],
            injection_detected=bool(tag.get("injection_detected")),
            injection_source=tag.get("injection_source", "none"),
            same_point_loop_signal=bool(tag.get("same_point_loop_signal")),
            suggested_level=tag.get("suggested_level", ""),
            confidence=float(tag.get("confidence") or 0),
            short_reason=tag.get("short_reason", ""),
            model=os.environ.get("NOI_TURN_TAGGER_MODEL", "deepseek-v4-flash"),
            prompt_version=TURN_TAGGER_PROMPT_VERSION,
        )
    except Exception as exc:
        print(f"[aichat_turn_tagger] record failed: {type(exc).__name__}: {exc}")


def _schedule_aichat_turn_tagging(**kwargs) -> None:
    if not _is_aichat_turn_tagger_enabled():
        return
    thread = threading.Thread(
        target=_run_aichat_turn_tagging,
        kwargs=kwargs,
        daemon=True,
    )
    thread.start()


def _messages_for_session_analyst(detail: dict) -> list[dict]:
    """Convert persisted teacher evidence messages into chat-style dialogue."""
    converted: list[dict] = []
    for message in detail.get("messages") or []:
        role = message.get("role")
        if role == "student":
            chat_role = "user"
        elif role == "ai_coach":
            chat_role = "assistant"
        else:
            chat_role = "system"
        converted.append(
            {
                "role": chat_role,
                "content": message.get("content", ""),
                "created_at": message.get("created_at", ""),
            }
        )
    return converted


def _run_aichat_session_analysis(session_id: str) -> None:
    """Generate teacher-facing analysis for one AIChat session."""
    detail = get_teacher_aichat_evidence_session_detail(session_id)
    if not detail:
        upsert_aichat_session_analysis(
            session_id=session_id,
            status="failed",
            failure_reason="session_not_found",
            model=os.environ.get("NOI_SESSION_ANALYST_MODEL", "deepseek-v4-pro"),
            prompt_version=SESSION_ANALYST_PROMPT_VERSION,
        )
        return

    summary = detail.get("summary") or {}
    student_id = summary.get("student_id", "")
    problem_id = summary.get("problem_id", "")
    try:
        turn_tags = list_aichat_turn_tags(session_id=session_id, limit=200, ascending=True)
        analysis = analyze_aichat_session(
            messages=_messages_for_session_analyst(detail),
            turn_tags=turn_tags,
            summary=summary,
            problem_context={"problem_ref": problem_id} if problem_id else None,
        )
        if analysis.get("_failed"):
            upsert_aichat_session_analysis(
                session_id=session_id,
                student_id=student_id,
                problem_id=problem_id,
                status="failed",
                failure_reason=analysis.get("_reason", "unknown_failure"),
                model=os.environ.get("NOI_SESSION_ANALYST_MODEL", "deepseek-v4-pro"),
                prompt_version=SESSION_ANALYST_PROMPT_VERSION,
            )
            return
        upsert_aichat_session_analysis(
            session_id=session_id,
            student_id=student_id,
            problem_id=problem_id,
            status="completed",
            analysis_json=analysis,
            main_issue=analysis.get("main_issue", ""),
            teacher_next_action=analysis.get("teacher_next_action", ""),
            needs_followup=bool(analysis.get("needs_followup")),
            model=os.environ.get("NOI_SESSION_ANALYST_MODEL", "deepseek-v4-pro"),
            prompt_version=SESSION_ANALYST_PROMPT_VERSION,
        )
    except Exception as exc:
        upsert_aichat_session_analysis(
            session_id=session_id,
            student_id=student_id,
            problem_id=problem_id,
            status="failed",
            failure_reason=f"{type(exc).__name__}: {exc}",
            model=os.environ.get("NOI_SESSION_ANALYST_MODEL", "deepseek-v4-pro"),
            prompt_version=SESSION_ANALYST_PROMPT_VERSION,
        )


def _session_analysis_response(row: dict | None) -> dict:
    if not row:
        return {"status": "missing", "analysis": None}
    return {
        "status": row.get("status") or "processing",
        "analysis": row.get("analysis_json") or None,
        "main_issue": row.get("main_issue", ""),
        "teacher_next_action": row.get("teacher_next_action", ""),
        "needs_followup": bool(row.get("needs_followup")),
        "failure_reason": row.get("failure_reason", ""),
        "model": row.get("model", ""),
        "prompt_version": row.get("prompt_version", ""),
        "updated_at": row.get("updated_at", ""),
    }


# ============ Chat Endpoint ============
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    user: dict = Depends(require_student),
):
    """
    Student chat endpoint.
    Requires authenticated student identity and session_id for history isolation.
    """
    if request.student_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="student_id 与当前登录账号不一致")
    request = enrich_chat_request_with_luogu_context(request)

    # 构建会话 key
    session_key = (user["user_id"], request.problem_id, request.session_id)
    memory_row = get_aichat_problem_memory(student_id=user["user_id"], problem_id=request.problem_id)
    memory_summary = (memory_row or {}).get("summary", "")
    
    # 获取或创建会话历史
    if session_key not in session_histories:
        restored_rows = list_aichat_messages(
            student_id=user["user_id"],
            problem_id=request.problem_id,
            session_id=request.session_id,
            limit=80,
            ascending=True,
        )
        session_histories[session_key] = [
            {"role": row["role"], "content": row["content"]}
            for row in restored_rows
            if row["role"] in {"user", "assistant"} and row["content"]
        ]
    
    full_history = session_histories[session_key]
    current_user_content = build_chat_message_with_problem_context(request, memory_summary=memory_summary)
    messages = full_history[-10:].copy()
    messages.append({"role": "user", "content": current_user_content})
    handoff_payload = build_policy_handoff_payload(
        analyze_student_turn(messages[-1]["content"], messages),
        messages,
    )

    try:
        selected_provider = request.chat_model_provider.strip()
        prompt_mode = request.aichat_prompt_mode.strip() or "current_system"
        if selected_provider:
            chat_kwargs = {"chat_model_provider": selected_provider}
        else:
            chat_kwargs = {}
        if prompt_mode in {"enhanced_prompt_only_clean", "dbox_inspired_clean"}:
            chat_kwargs["aichat_prompt_mode"] = prompt_mode
        reply_for_display, reply_for_history, final_level = chat(
            messages,
            user["user_id"],
            request.problem_id,
            **chat_kwargs,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc

    # 更新会话历史。内存里保留学生原始问题，当前题目上下文会在每轮请求重新拼接，
    # 避免旧题面/代码块随历史反复进入模型。
    full_history.append({"role": "user", "content": request.message})
    full_history.append({"role": "assistant", "content": reply_for_history})
    session_histories[session_key] = full_history

    try:
        has_problem_context = _has_chat_problem_context(request)
        has_student_code = bool(request.student_code.strip())
        record_aichat_message(
            student_id=user["user_id"],
            problem_id=request.problem_id,
            session_id=request.session_id,
            role="user",
            content=request.message,
            problem_title=request.problem_title,
            problem_url=request.problem_url,
            has_problem_context=has_problem_context,
            has_student_code=has_student_code,
        )
        record_aichat_message(
            student_id=user["user_id"],
            problem_id=request.problem_id,
            session_id=request.session_id,
            role="assistant",
            content=reply_for_history,
            problem_title=request.problem_title,
            problem_url=request.problem_url,
            has_problem_context=has_problem_context,
            has_student_code=has_student_code,
        )
    except Exception as exc:
        print(f"[aichat_message] record failed: {exc}")

    _schedule_aichat_problem_memory_update(
        student_id=user["user_id"],
        problem_id=request.problem_id,
        session_id=request.session_id,
        old_summary=memory_summary,
        student_message=request.message,
        assistant_reply=reply_for_history,
        problem_context=request.problem_context,
        student_code=request.student_code,
        provider_id=request.chat_model_provider.strip(),
    )

    _schedule_aichat_turn_tagging(
        student_id=user["user_id"],
        student_username=user.get("username") or user["user_id"],
        student_real_name=user.get("display_name") or user.get("real_name") or user.get("username") or user["user_id"],
        problem_id=request.problem_id,
        session_id=request.session_id,
        turn_id=str(uuid4()),
        user_input=request.message,
        messages=full_history[-12:],
        problem_context={
            "problem_ref": request.problem_id,
            "title": request.problem_title,
            "url": request.problem_url,
            "statement": request.problem_context,
        },
        student_code=request.student_code,
        rule_weak_signals=[],
    )
    
    # 清理旧会话（保留最近1000个）
    if len(session_histories) > 1000:
        oldest_key = next(iter(session_histories))
        del session_histories[oldest_key]

    # final_level 是 chat() 返回的真实最终等级（已经过硬闸门限制）
    chat_model_info = get_chat_model_public_info(request.chat_model_provider)
    prompt_mode_info = get_aichat_prompt_mode_public_info(request.aichat_prompt_mode)
    understanding = evaluate_understanding_evidence(full_history)
    if (
        understanding.get("understanding_state") == "evidence_seen"
        and request.problem_id
        and not has_problem_bottleneck_event(
            student_id=student_id,
            problem_ref=request.problem_id,
            session_id=request.session_id,
            source_event="aichat_exit_ready",
        )
    ):
        create_problem_bottleneck_event(
            student_id=student_id,
            problem_ref=request.problem_id,
            session_id=request.session_id,
            source_event="aichat_exit_ready",
            result_status="ready",
            bottleneck_type="understanding_ready",
            target_focus="学生已经留下可进入验证或记录的理解证据",
            evidence="、".join(understanding.get("evidence_types") or [])[:300],
        )
    return ChatResponse(
        reply=reply_for_display,
        remaining_quota=0,
        level=final_level,
        handoff_payload=handoff_payload,
        understanding_state=understanding["understanding_state"],
        understanding_evidence=understanding["evidence_types"],
        chat_model_provider=chat_model_info.get("provider_id", ""),
        chat_model_label=chat_model_info.get("label", ""),
        aichat_prompt_mode=prompt_mode_info.get("prompt_mode", "current_system"),
        aichat_prompt_mode_label=prompt_mode_info.get("label", "简洁提示"),
    )


@app.get("/api/chat/history")
def get_chat_history_endpoint(
    problem_id: str = "",
    session_id: str = "",
    limit: int = 80,
    user: dict = Depends(require_student),
):
    rows = list_aichat_messages(
        student_id=user["user_id"],
        problem_id=problem_id,
        session_id=session_id,
        limit=limit,
        ascending=True,
    )
    return {
        "messages": [
            {"role": row["role"], "content": row["content"]}
            for row in rows
            if row["role"] in {"user", "assistant"} and row["content"]
        ]
    }


@app.post("/api/chat/understanding-check/generate")
def generate_understanding_check_endpoint(
    request: UnderstandingCheckGenerateRequest,
    user: dict = Depends(require_student),
):
    recent_rows = list_aichat_messages(
        student_id=user["user_id"],
        problem_id=request.problem_id,
        session_id=request.session_id,
        limit=12,
        ascending=True,
    )
    recent_messages = [
        {"role": row["role"], "content": row["content"]}
        for row in recent_rows
        if row["role"] in {"user", "assistant"} and row["content"]
    ]
    return generate_understanding_check(
        messages=recent_messages,
        problem_title=request.problem_title,
        problem_context=request.problem_context,
        student_code=request.student_code,
        chat_model_provider=request.chat_model_provider,
    )


@app.post("/api/chat/understanding-check/grade")
def grade_understanding_check_endpoint(
    request: UnderstandingCheckGradeRequest,
    user: dict = Depends(require_student),
):
    del user
    return grade_understanding_check(
        question=request.question,
        answer=request.answer,
        target_focus=request.target_focus,
        quiz_format=request.quiz_format,
        problem_title=request.problem_title,
        problem_context=request.problem_context,
        student_code=request.student_code,
        chat_model_provider=request.chat_model_provider,
    )


@app.post("/api/chat/problem-closure/start")
def start_problem_closure_endpoint(
    request: ProblemClosureStartRequest,
    user: dict = Depends(require_student),
):
    recent_rows = list_aichat_messages(
        student_id=user["user_id"],
        problem_id=request.problem_id,
        session_id=request.session_id,
        limit=12,
        ascending=True,
    )
    recent_messages = [
        {"role": row["role"], "content": row["content"]}
        for row in recent_rows
        if row["role"] in {"user", "assistant"} and row["content"]
    ]
    result = generate_understanding_check(
        messages=recent_messages,
        problem_title=request.problem_title,
        problem_context=request.problem_context,
        student_code=request.student_code,
        chat_model_provider=request.chat_model_provider,
    )
    if result.get("status") != "ok":
        return {
            "status": result.get("status") or "unavailable",
            "message": result.get("message") or "这一步还没准备好验证，先继续问 AIChat。",
            "closure_id": None,
        }
    closure_id = create_aichat_problem_closure(
        student_id=user["user_id"],
        problem_id=request.problem_id,
        session_id=request.session_id,
        problem_title=request.problem_title,
        question=result.get("question") or "",
        target_focus=result.get("target_focus") or "",
    )
    create_problem_bottleneck_event(
        student_id=user["user_id"],
        problem_ref=request.problem_id,
        session_id=request.session_id,
        source_event="closure_quiz",
        result_status="generated",
        bottleneck_type=result.get("bottleneck_type") or "",
        quiz_format=result.get("quiz_format") or "",
        target_focus=result.get("target_focus") or "",
        evidence=result.get("evidence") or "",
    )
    return {
        "status": "ok",
        "closure_id": closure_id,
        "question": result.get("question") or "",
        "target_focus": result.get("target_focus") or "",
        "bottleneck_type": result.get("bottleneck_type") or "",
        "quiz_format": result.get("quiz_format") or "",
        "evidence": result.get("evidence") or "",
        "message": "先回答这个小问题，确认你是真的理解了这一题。",
    }


@app.post("/api/chat/problem-closure/grade")
def grade_problem_closure_endpoint(
    request: ProblemClosureGradeRequest,
    user: dict = Depends(require_student),
):
    closure = get_aichat_problem_closure(request.closure_id)
    if not closure or closure["student_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="没有找到这次结束本题记录")
    result = grade_understanding_check(
        question=closure["question"],
        answer=request.answer,
        target_focus=closure.get("target_focus", ""),
        quiz_format=request.quiz_format,
        problem_title=request.problem_title or closure.get("problem_title", ""),
        problem_context=request.problem_context,
        student_code=request.student_code,
        chat_model_provider=request.chat_model_provider,
    )
    raw_status = str(result.get("status") or "failed")
    status = raw_status if raw_status in {"passed", "partial", "failed", "unavailable"} else "failed"
    can_review = bool(result.get("can_review")) and status == "passed"
    final_status = "passed" if can_review else status
    points_awarded = 2 if can_review else 0
    next_review_at = ""
    next_review_message = ""
    if can_review:
        next_review_at = (datetime.now(timezone.utc) + timedelta(days=3)).replace(microsecond=0).isoformat()
        next_review_message = "已记录本题理解结果，建议 3 天后再做一次迁移复习。"
    updated = grade_aichat_problem_closure(
        closure_id=request.closure_id,
        student_id=user["user_id"],
        status=final_status,
        answer=request.answer,
        feedback=result.get("feedback") or "已检查你的回答。",
        followup=result.get("followup") or "",
        points_awarded=points_awarded,
        next_review_at=next_review_at,
    )
    create_problem_bottleneck_event(
        student_id=user["user_id"],
        problem_ref=closure.get("problem_id", ""),
        session_id=closure.get("session_id", ""),
        source_event="problem_closure_passed" if can_review else "problem_closure_failed",
        result_status=final_status,
        bottleneck_type=result.get("bottleneck_type") or "",
        quiz_format=request.quiz_format,
        target_focus=closure.get("target_focus", ""),
        evidence=(request.answer or "")[:300],
        ai_confidence=result.get("confidence") or "",
    )
    return {
        "status": final_status,
        "closure_id": request.closure_id,
        "feedback": updated["feedback"] if updated else result.get("feedback", ""),
        "followup": updated["followup"] if updated else result.get("followup", ""),
        "points_awarded": points_awarded,
        "next_review_at": next_review_at,
        "next_review_message": next_review_message,
        "can_start_next_problem": can_review,
    }


# ============ Quota Endpoints ============
@app.get("/quota/{student_id}/{problem_id}", response_model=QuotaResponse)
def get_quota_endpoint(
    student_id: str,
    problem_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Get quota for a student and problem.
    Students can only query their own quota; teachers can query any student.
    """
    if user["role"] == "student" and student_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="只能查询自己的题目配额")
    return build_quota_response(student_id, problem_id)


@app.post("/quota/reset", response_model=QuotaResponse)
def reset_quota_endpoint(
    request: ResetQuotaRequest,
    user: dict = Depends(require_teacher),
):
    """
    Reset quota for a student and problem.
    Requires teacher login and teacher_secret for authentication.
    """
    # 验证教师密钥
    if not NOI_TEACHER_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Teacher secret not configured",
        )
    
    if request.teacher_secret != NOI_TEACHER_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Invalid teacher secret",
        )
    
    save_quota(
        request.student_id,
        request.problem_id,
        {"count": 0, "max": PER_PROBLEM_HINT_LIMIT},
    )
    return build_quota_response(request.student_id, request.problem_id)


# ============ Checkin Endpoints ============
@app.post("/api/problem-import", response_model=ProblemImportResponse)
def import_problem(
    request: ProblemImportRequest,
    user: dict = Depends(require_student),
):
    del user
    raw_ref = request.url.strip()
    normalized_luogu_url = normalize_luogu_problem_url(raw_ref)
    normalized_jmfes_url = normalize_jmfes_problem_url(raw_ref)
    normalized_url = normalized_luogu_url or normalized_jmfes_url
    if not normalized_url:
        raise HTTPException(status_code=400, detail="当前支持导入洛谷题号/公开题目链接，以及 JMYSOJ 题目链接")

    try:
        if normalized_luogu_url:
            payload = fetch_luogu_problem(normalized_url)
        else:
            payload = fetch_jmfes_problem(normalized_url)
    except requests.HTTPError as exc:
        source_name = "洛谷" if normalized_luogu_url else "JMYSOJ"
        raise HTTPException(status_code=502, detail=f"读取{source_name}题面失败：{exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    oj_source = payload.get("oj_source") or ("luogu" if normalized_luogu_url else "other")
    problem_tags = _normalize_ai_problem_tags(payload.get("problem_tags", []))
    tag_type = "algo" if oj_source == "luogu" and problem_tags else "ai"
    if not problem_tags:
        problem_tags = generate_problem_tags_with_ai(
            problem_title=payload.get("problem_title", ""),
            problem_context=payload.get("problem_context", ""),
            oj_source=oj_source,
        )
        tag_type = "ai"
        payload["problem_tags"] = problem_tags

    problem_pid = str(payload.get("problem_pid") or "").strip()
    if problem_pid:
        try:
            upsert_external_problem(
                source=oj_source,
                source_problem_id=problem_pid,
                title=payload.get("problem_title", ""),
                problem_context=payload.get("problem_context", ""),
                problem_url=payload.get("problem_url", normalized_url),
                problem_tags=problem_tags,
                tag_type=tag_type,
                raw_payload=payload,
            )
        except Exception as exc:
            print(f"[problem_import] persist failed for {oj_source}:{problem_pid}: {exc}")

    return ProblemImportResponse(
        problem_url=payload["problem_url"],
        problem_pid=payload.get("problem_pid"),
        problem_title=payload["problem_title"],
        problem_context=payload["problem_context"],
        problem_tags=problem_tags,
        oj_source=oj_source,
        message="已自动导入题目标题和题面",
    )


@app.get("/api/problems/related", response_model=RelatedProblemsResponse)
def get_related_problems_endpoint(
    pid: str,
    limit: int = 4,
    user: dict = Depends(require_student),
):
    del user
    normalized_pid, _ = normalize_luogu_problem_ref(pid.strip())
    if not normalized_pid:
        raise HTTPException(status_code=400, detail="请输入有效的洛谷题号")
    related = list_related_problems_by_luogu_pid(normalized_pid, limit=max(1, min(limit, 8)))
    return RelatedProblemsResponse(pid=normalized_pid, related=related)


@app.post("/api/checkins", response_model=CheckinResponse)
def create_checkin_endpoint(
    request: CheckinRequest,
    user: dict = Depends(require_student),
):
    """
    Student creates a checkin after solving a problem.
    Also generates AI review automatically.
    
    流程：
    1. 先校验卡点描述（业务规则）
    2. 校验不通过：返回422，不创建记录，只增加rejected统计
    3. 校验通过：创建checkin，同时创建待生成review记录
    4. LLM失败：保留checkin，review保持pending，稍后自动/手动重试
    5. LLM成功：写入结构化review并标记completed
    """
    student_id = user["user_id"]
    
    # Step 1: 业务级卡点校验（在创建记录之前）
    validation_text = "\n".join(
        part.strip()
        for part in (request.bottleneck_text, request.reflection or "")
        if str(part or "").strip()
    )
    is_valid, error_msg = validate_bottleneck(validation_text)
    if not is_valid:
        # 记录被拒绝的打卡（用于统计质量）
        record_rejected_checkin()
        raise HTTPException(
            status_code=422,
            detail=error_msg,
        )

    resolved_problem_url = request.problem_url.strip()
    resolved_problem_title = request.problem_title.strip()
    resolved_problem_context = request.problem_context.strip()
    resolved_problem_tags = [tag.strip() for tag in (request.problem_tags or []) if str(tag).strip()]
    resolved_oj_source = infer_oj_source_from_problem_ref(resolved_problem_url, request.oj_source)

    local_problem_id = None
    problem_card = None
    analysis_source = None
    session_id = _new_checkin_session_id()

    if resolved_oj_source in {"luogu", "jmfes"} and resolved_problem_url:
        try:
            imported_problem = (
                fetch_luogu_problem(resolved_problem_url)
                if resolved_oj_source == "luogu"
                else fetch_jmfes_problem(resolved_problem_url)
            )
        except Exception as exc:
            if not resolved_problem_title or len(resolved_problem_context) < 10:
                raise HTTPException(
                    status_code=422,
                    detail=f"{'洛谷' if resolved_oj_source == 'luogu' else 'JMYSOJ'}题目自动导入失败：{exc}",
                ) from exc
        else:
            resolved_problem_url = imported_problem["problem_url"]
            if not resolved_problem_title:
                resolved_problem_title = imported_problem["problem_title"]
            if len(resolved_problem_context) < 10:
                resolved_problem_context = imported_problem["problem_context"]
            if not resolved_problem_tags:
                resolved_problem_tags = imported_problem.get("problem_tags", [])
            pid = imported_problem.get("problem_pid") or extract_luogu_pid(resolved_problem_url)
            local_problem = get_problem_by_luogu_pid(pid) if pid else None
            if local_problem:
                local_problem_id = local_problem["problem_id"]
                problem_card, analysis_source = get_problem_card_by_ref(imported_problem["problem_url"])

    if not resolved_problem_title:
        raise HTTPException(status_code=422, detail="请填写题目标题，或提供可自动导入的洛谷链接")

    if resolved_oj_source in {"luogu", "jmfes"}:
        if len(resolved_problem_context) < 10:
            source_name = "洛谷" if resolved_oj_source == "luogu" else "JMYSOJ"
            raise HTTPException(status_code=422, detail=f"请提供可导入的{source_name}题目链接，或手动补充题面 / Markdown")
    else:
        if len(resolved_problem_context) < 10:
            raise HTTPException(status_code=422, detail="当前来源暂不支持自动导入，请至少粘贴10个字的题面 / Markdown")
    
    # Step 2: 创建打卡记录（校验已通过）
    checkin_id = create_checkin(
        student_id=student_id,
        problem_url=resolved_problem_url,
        problem_title=resolved_problem_title,
        oj_source=resolved_oj_source,
        completion_status=request.completion_status,
        bottleneck_text=request.bottleneck_text,
        error_types=request.error_types,
        reflection=request.reflection,
        problem_context=resolved_problem_context,
        submission_result=request.submission_result,
        student_code=request.student_code,
        problem_tags=resolved_problem_tags,
        chat_context_summary=request.chat_context_summary,
        session_id=session_id,
    )
    
    # 记录打卡统计
    record_checkin_stats(len(request.bottleneck_text))
    
    # Step 3: 生成 AI 复盘
    update_checkin_runtime_status(checkin_id, "received", REVIEW_STATUS_PENDING, "已收到打卡")
    update_checkin_runtime_status(checkin_id, "queued", REVIEW_STATUS_PENDING, "已进入生成队列")
    _start_review_generation_job(
        checkin_id=checkin_id,
        student_id=student_id,
        problem_title=resolved_problem_title,
        oj_source=resolved_oj_source,
        completion_status=request.completion_status,
        bottleneck_text=request.bottleneck_text,
        error_types=request.error_types,
        reflection=request.reflection,
        problem_context=resolved_problem_context,
        problem_tags=resolved_problem_tags,
        chat_context_summary=request.chat_context_summary,
        problem_card=problem_card,
        analysis_source=analysis_source,
        local_problem_id=local_problem_id,
        submission_result=request.submission_result,
        student_code=request.student_code,
        handoff_payload=request.handoff_payload,
    )

    if resolved_oj_source == "luogu" and local_problem_id:
        pid = extract_luogu_pid(resolved_problem_url)
        if pid:
            _start_problem_analysis_job(pid)

    review_mode = _detect_review_mode(request.completion_status, request.submission_result)
    review_family = _family_for_review_mode(review_mode)

    return CheckinResponse(
        checkin_id=checkin_id,
        session_id=session_id,
        review_status=REVIEW_STATUS_PENDING,
        review_mode=review_mode,
        review_family=review_family,
        review=None,
        message="打卡已提交，AI 正在整理复盘，请稍候查看",
    )


@app.get("/api/checkins/me")
def get_my_checkins(
    user: dict = Depends(require_student),
    limit: int = 50,
):
    """Student gets their own checkin history"""
    checkins = [_attach_review_route_fields(item) for item in get_student_checkins(user["user_id"], limit)]
    return {"checkins": checkins}


@app.get("/api/checkins/{checkin_id}", response_model=CheckinStatusResponse)
def get_checkin_detail_endpoint(
    checkin_id: int,
    user: dict = Depends(require_student),
):
    item = _attach_review_route_fields(get_student_checkin_by_id(user["user_id"], checkin_id))
    if not item:
        raise HTTPException(status_code=404, detail="未找到对应打卡")
    item["review_last_error"] = None
    if item.get("review_id"):
        item["quiz_history"] = [
            serialize_quiz(quiz)
            for quiz in get_quizzes_for_review(item["review_id"])
            if quiz and quiz.get("status") != "replaced"
        ]
    return item


@app.post("/api/student/feedback")
def submit_student_feedback_endpoint(
    request: StudentFeedbackRequest,
    user: dict = Depends(require_student),
):
    content = (request.content or "").strip()
    if len(content) < 5:
        raise HTTPException(status_code=422, detail={"message": "反馈内容至少写 5 个字"})
    feedback_id = create_student_feedback(
        student_id=user["user_id"],
        category=request.category,
        rating=request.rating,
        content=content,
        page_context=request.page_context,
    )
    return {
        "status": "ok",
        "message": "反馈已提交，老师可以在教师端看到。",
        "feedback_id": feedback_id,
    }


@app.post("/api/student/problem-completions")
def create_student_problem_completion_endpoint(
    request: StudentProblemCompletionRequest,
    user: dict = Depends(require_student),
):
    record = create_student_problem_completion(
        student_id=user["user_id"],
        problem_id=request.problem_id,
        problem_title=request.problem_title,
        problem_url=request.problem_url,
        reported_completion=request.reported_completion,
        result_status=request.result_status,
        key_step_summary=request.key_step_summary,
        session_id=request.session_id,
    )
    points_awarded = int(record.get("points_awarded") or 0)
    if points_awarded > 0:
        message = f"做题记录已保存，获得 +{points_awarded} 积分。老师看到的是学习证据，不和别人比较。"
    else:
        message = "做题记录已保存。等你更确定这题后，再补一条记录也可以。"
    return {
        "status": "ok",
        "message": message,
        "record": record,
    }


@app.get("/api/student/problem-completions")
def list_student_problem_completion_endpoint(
    limit: int = 50,
    days: int = 365,
    user: dict = Depends(require_student),
):
    records = list_student_problem_completions(
        student_id=user["user_id"],
        limit=limit,
        days=days,
    )
    return {
        "status": "ok",
        "records": records,
    }


def _serialize_teacher_announcement(row: dict | None) -> dict | None:
    if not row:
        return None
    row = dict(row)
    return {
        "id": row["id"],
        "title": row.get("title") or "",
        "body_markdown": row.get("body_markdown") or "",
        "pinned": bool(row.get("pinned")),
        "status": row.get("status") or "published",
        "created_by": row.get("created_by") or "",
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "published_at": row.get("published_at"),
    }


BOTTLENECK_LABELS = {
    "problem_translation": "题意翻译",
    "concept_boundary": "概念边界",
    "representation_modeling": "表示建模",
    "constraint_relation": "约束关系",
    "process_tracing": "过程追踪",
    "strategy_choice": "策略选择",
    "transfer": "迁移不稳",
    "code_semantics": "代码语义",
    "debug_location": "调试定位",
    "complexity_awareness": "复杂度意识",
    "metacognition": "复盘表达",
    "affective": "情绪压力",
    "current_bottleneck": "当前这一步",
}


def _bottleneck_label(raw: str) -> str:
    text = (raw or "").strip()
    return BOTTLENECK_LABELS.get(text, text or "当前这一步")


def _build_student_home_snapshot(student_id: str) -> dict:
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT COUNT(DISTINCT problem_id) AS value
        FROM aichat_messages
        WHERE student_id = ?
          AND role = 'user'
          AND created_at >= datetime('now', '-30 days')
        ''',
        (student_id,),
    )
    active_problem_count = int((cursor.fetchone() or {"value": 0})["value"] or 0)

    cursor.execute(
        '''
        SELECT
            COALESCE(SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END), 0) AS passed_count,
            COALESCE(SUM(points_awarded), 0) AS points
        FROM aichat_problem_closures
        WHERE student_id = ?
          AND created_at >= datetime('now', '-30 days')
        ''',
        (student_id,),
    )
    closure_stats = cursor.fetchone()
    passed_count = int((closure_stats or {"passed_count": 0})["passed_count"] or 0)
    points = int((closure_stats or {"points": 0})["points"] or 0)
    cursor.execute(
        '''
        SELECT COALESCE(SUM(points_awarded), 0) AS points
        FROM student_problem_completions
        WHERE student_id = ?
          AND created_at >= datetime('now', '-30 days')
        ''',
        (student_id,),
    )
    completion_points = int((cursor.fetchone() or {"points": 0})["points"] or 0)
    points += completion_points

    cursor.execute(
        '''
        SELECT COUNT(*) AS value
        FROM reviews r
        JOIN checkins c ON c.id = r.checkin_id
        WHERE c.student_id = ?
          AND r.review_status = ?
          AND c.created_at >= datetime('now', '-30 days')
        ''',
        (student_id, REVIEW_STATUS_COMPLETED),
    )
    completed_reviews = int((cursor.fetchone() or {"value": 0})["value"] or 0)

    cursor.execute(
        '''
        SELECT id, problem_id, session_id, problem_title, status, question, target_focus, created_at
        FROM aichat_problem_closures
        WHERE student_id = ?
          AND status != 'passed'
        ORDER BY id DESC
        LIMIT 1
        ''',
        (student_id,),
    )
    pending_closure = cursor.fetchone()

    cursor.execute(
        '''
        SELECT problem_id, session_id, problem_title, problem_url, content, created_at
        FROM aichat_messages
        WHERE student_id = ?
          AND role = 'user'
        ORDER BY id DESC
        LIMIT 1
        ''',
        (student_id,),
    )
    latest_chat = cursor.fetchone()

    cursor.execute(
        '''
        SELECT bottleneck_type, COUNT(*) AS count
        FROM problem_bottleneck_events
        WHERE student_id = ?
          AND bottleneck_type != ''
          AND created_at >= datetime('now', '-30 days')
        GROUP BY bottleneck_type
        ORDER BY count DESC, MAX(id) DESC
        LIMIT 3
        ''',
        (student_id,),
    )
    bottlenecks = [
        {"label": _bottleneck_label(row["bottleneck_type"]), "count": int(row["count"] or 0)}
        for row in cursor.fetchall()
    ]

    cursor.execute(
        '''
        SELECT id, problem_id, problem_title, target_focus, next_review_at
        FROM aichat_problem_closures
        WHERE student_id = ?
          AND status = 'passed'
          AND next_review_at != ''
        ORDER BY next_review_at ASC, id DESC
        LIMIT 2
        ''',
        (student_id,),
    )
    reminders = [
        {
            "title": row["problem_title"] or row["problem_id"] or "复习提醒",
            "description": f"回看一下：{row['target_focus'] or '这一步思路'}",
            "action_label": "去复习",
            "action_path": "/app/workspace/chat",
            "next_review_at": row["next_review_at"],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    completion_summary = get_student_completion_summary(student_id, days=15)
    exit_trigger_summary = get_student_exit_trigger_summary(student_id, days=15)
    recent_completions = list_student_problem_completions(student_id=student_id, limit=3, days=30)

    if pending_closure:
        continue_learning = {
            "kind": "problem_closure",
            "title": pending_closure["problem_title"] or pending_closure["problem_id"] or "继续结束验证",
            "description": pending_closure["question"] or "还有一道结束验证等你确认。",
            "action_label": "继续结束验证",
            "action_path": "/app/workspace/chat",
            "problem_id": pending_closure["problem_id"],
            "problem_title": pending_closure["problem_title"],
        }
    elif latest_chat:
        continue_learning = {
            "kind": "aichat",
            "title": latest_chat["problem_title"] or latest_chat["problem_id"] or "继续上一题",
            "description": "你最近在 AIChat 里问过这道题，可以接着聊或整理一下。",
            "action_label": "继续问 AI",
            "action_path": "/app/workspace/chat",
            "problem_id": latest_chat["problem_id"],
            "problem_title": latest_chat["problem_title"],
        }
    else:
        continue_learning = {
            "kind": "empty",
            "title": "开始今天的练习",
            "description": "读入一道题，先把没想明白的地方发给 AIChat。",
            "action_label": "开始问 AI",
            "action_path": "/app/workspace/chat",
            "problem_id": "",
            "problem_title": "",
        }

    return {
        "announcement": _serialize_teacher_announcement(get_latest_student_announcement()),
        "continue_learning": continue_learning,
        "stats": [
            {"label": "本月练习题数", "value": active_problem_count},
            {"label": "理解验证通过", "value": passed_count},
            {"label": "复盘完成", "value": completed_reviews},
            {"label": "近 15 天做题记录", "value": completion_summary["last_15_days"]},
            {"label": "积分", "value": points},
        ],
        "completion_summary": completion_summary,
        "exit_trigger_summary": exit_trigger_summary,
        "recent_completions": recent_completions,
        "recent_bottlenecks": bottlenecks,
        "review_reminders": reminders,
    }


@app.get("/api/student/home")
def get_student_home_endpoint(user: dict = Depends(require_student)):
    return _build_student_home_snapshot(user["user_id"])


def _build_teacher_attention_students(days: int = 7) -> list[dict]:
    observations = list_teacher_aichat_observations(limit=80, days=days)
    grouped: dict[str, dict] = {}
    for item in observations:
        student_id = item.get("student_id") or ""
        if not student_id:
            continue
        row = grouped.setdefault(
            student_id,
            {
                "student_id": student_id,
                "status": "建议看看",
                "reason": "AIChat 有学习记录但缺少验证证据。",
                "evidence": item.get("evidence") or item.get("latest_student_message") or "",
                "teacher_action": item.get("teacher_action") or item.get("suggested_teacher_action") or "先看最近一次 AIChat 对话证据。",
                "problem_title": item.get("problem_title") or item.get("problem_id") or "未绑定题目",
                "severity": "medium",
            },
        )
        if (item.get("student_message_count") or 0) >= 4:
            row["status"] = "优先关注"
            row["reason"] = "同一题对话轮次较多，可能仍缺少可验证的理解证据。"
            row["severity"] = "high"
    completions_by_student: dict[str, dict] = {}
    for student_id in list(grouped.keys()):
        completions_by_student[student_id] = get_student_completion_summary(student_id, days=15)
    for student_id, summary in completions_by_student.items():
        if summary["last_15_days"] <= 0:
            grouped[student_id]["reason"] = "AIChat 有学习记录，但近 15 天缺少验证证据和做题记录。"
        elif summary["self_solved_15_days"] >= 1 and summary["aichat_assisted_15_days"] == 0:
            grouped[student_id]["status"] = "正在独立推进"
            grouped[student_id]["reason"] = "近 15 天有自主做题记录，建议继续观察是否能稳定迁移。"
            grouped[student_id]["severity"] = "low"
    return sorted(
        grouped.values(),
        key=lambda row: {"high": 0, "medium": 1, "low": 2}.get(row["severity"], 1),
    )[:8]


@app.post("/api/review-events", response_model=ReviewEventResponse)
def create_review_event_endpoint(
    request: ReviewEventRequest,
    user: dict = Depends(require_student),
):
    item = get_student_checkin_by_id(user["user_id"], request.checkin_id)
    if not item:
        raise HTTPException(status_code=404, detail="未找到对应打卡")
    if item.get("session_id") and item["session_id"] != request.session_id:
        raise HTTPException(status_code=400, detail="session_id 与当前打卡不一致")

    review_mode = _detect_review_mode(item.get("completion_status", ""), item.get("submission_result"))
    review_family = _family_for_review_mode(review_mode)
    payload = {
        "client_ts": request.client_ts,
        "app_version": request.app_version,
        "problem_id": request.problem_id,
        "problem_title": request.problem_title,
        "has_code": request.has_code,
        "problem_context_length": request.problem_context_length,
        "bottleneck_text_length": request.bottleneck_text_length,
        "student_feedback": request.student_feedback,
        "bad_reason": request.bad_reason,
        "followup_clicked": request.followup_clicked,
        "followup_question_count": request.followup_question_count,
        "latency_ms": request.latency_ms,
        "review_text_length": request.review_text_length,
    }
    record_review_event(
        session_id=item.get("session_id") or request.session_id,
        checkin_id=request.checkin_id,
        student_id=user["user_id"],
        event_name=request.event_name,
        review_mode=review_mode,
        review_family=review_family,
        payload=payload,
    )
    return ReviewEventResponse(status="ok")


def get_checkin_detail(checkin_id: int) -> dict | None:
    return get_checkin_detail_by_id(checkin_id)


@app.get("/api/checkins/{checkin_id}/stream")
def stream_checkin_status_endpoint(
    checkin_id: int,
    once: bool = False,
    user: dict = Depends(require_student),
):
    student_id = user["user_id"]
    item = get_student_checkin_by_id(student_id, checkin_id)
    if not item:
        raise HTTPException(status_code=404, detail="未找到对应打卡")

    def event_stream():
        last_status_signature = None
        last_draft_signature = None
        while True:
            latest_item = get_student_checkin_by_id(student_id, checkin_id)
            if not latest_item:
                yield _encode_sse_event(
                    "error",
                    {
                        "checkin_id": checkin_id,
                        "review_status": "failed",
                        "phase": "failed",
                        "message": "未找到对应打卡",
                        "draft_review": {},
                        "elapsed_seconds": 0,
                        "updated_at": time.time(),
                    },
                )
                break
            payload = _build_checkin_stream_payload(checkin_id, latest_item)
            status_signature = (
                payload.get("phase"),
                payload.get("review_status"),
                payload.get("message"),
                payload.get("updated_at"),
            )
            draft_review = payload.get("draft_review") or {}
            draft_signature = tuple(
                draft_review.get(key, "")
                for key in (
                    "problem_focus",
                    "main_block",
                    "key_bridge",
                    "visual_hint",
                    "guided_walkthrough",
                    "try_now",
                    "next_step",
                    "transfer_signal",
                )
            )
            emitted = False
            if status_signature != last_status_signature:
                event = "status"
                if payload["review_status"] == REVIEW_STATUS_COMPLETED:
                    event = "review_ready"
                elif payload["review_status"] == "failed":
                    event = "error"
                yield _encode_sse_event(event, payload)
                last_status_signature = status_signature
                emitted = True
            if any(draft_signature) and draft_signature != last_draft_signature:
                yield _encode_sse_event("review_chunk", payload)
                last_draft_signature = draft_signature
                emitted = True
            if not emitted:
                yield _encode_sse_event(
                    "keepalive",
                    {
                        "checkin_id": checkin_id,
                        "elapsed_seconds": payload.get("elapsed_seconds", 0),
                    },
                )
            if payload["review_status"] in {REVIEW_STATUS_COMPLETED, "failed"}:
                break
            if once:
                break
            time.sleep(STREAM_STATUS_POLL_SECONDS)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/checkins/{checkin_id}/review/retry")
def retry_checkin_review_endpoint(
    checkin_id: int,
    user: dict = Depends(require_student),
):
    item = get_student_checkin_by_id(user["user_id"], checkin_id)
    if not item:
        raise HTTPException(status_code=404, detail="未找到对应打卡")

    status = item["review_status"]
    if status == REVIEW_STATUS_PENDING:
        raise HTTPException(status_code=400, detail="复盘正在生成中，请稍候")
    if status == REVIEW_STATUS_COMPLETED:
        raise HTTPException(status_code=400, detail="复盘已生成，无需重试")
    if status != "failed":
        raise HTTPException(status_code=400, detail="当前状态不支持重试")

    ok = reset_review_for_student_retry(checkin_id, user["user_id"])
    if not ok:
        raise HTTPException(status_code=400, detail="当前状态不支持重试")

    update_checkin_runtime_status(checkin_id, "queued", REVIEW_STATUS_PENDING, "已进入生成队列")
    _start_review_generation_job(
        checkin_id=checkin_id,
        student_id=item["student_id"],
        problem_title=item["problem_title"],
        oj_source=item["oj_source"],
        completion_status=item["completion_status"],
        bottleneck_text=item["bottleneck_text"],
        error_types=item["error_types"],
        reflection=item["reflection"],
        problem_context=item["problem_context"],
        problem_tags=item["problem_tags"],
        chat_context_summary=item["chat_context_summary"],
        problem_card=None,
        analysis_source=None,
        local_problem_id=None,
        submission_result=item["submission_result"],
        student_code=item["student_code"],
    )

    return {
        "checkin_id": checkin_id,
        "review_status": REVIEW_STATUS_PENDING,
        "message": "已重新加入生成队列，请稍候查看",
    }


@app.post("/api/reviews/{review_id}/quiz/generate")
def generate_review_quiz_endpoint(
    review_id: int,
    user: dict = Depends(require_student),
):
    review_context = get_review_context(review_id)
    if not review_context or review_context["student_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="未找到对应复盘")
    if review_context["review_status"] != REVIEW_STATUS_COMPLETED:
        raise HTTPException(status_code=400, detail="复盘尚未完成，暂时不能生成理解小测")
    if review_context["learning_status"] == LEARNING_STATUS_SELF_CHECK_REQUIRED:
        raise HTTPException(status_code=400, detail="请先完成这一步的理解确认")
    if review_context["learning_status"] in {LEARNING_STATUS_RESOLVED, LEARNING_STATUS_NEEDS_TEACHER}:
        raise HTTPException(status_code=400, detail="当前复盘已经结束，不需要再生成新的理解小测")

    if has_explicit_help_signal(review_context):
        update_review_learning_status(review_id, LEARNING_STATUS_REMEDY_AVAILABLE)
        return {
            "message": "你已经明确说出自己卡住了，我们先回到卡住点，不直接继续出理解小测。",
            "learning_status": LEARNING_STATUS_REMEDY_AVAILABLE,
            "next_state": "remedy_available",
            "dynamic_button_label": dynamic_remedy_label(review_context["error_layer"]),
        }

    latest_quiz = get_latest_quiz_for_review(review_id)
    if is_stale_pending_quiz(latest_quiz):
        replacement = replace_legacy_pending_quiz(review_context, latest_quiz)
        if replacement:
            latest_quiz = replacement
        else:
            latest_quiz = None
            review_context = get_review_context(review_id) or review_context
    if latest_quiz and latest_quiz["status"] == "pending":
        return {
            "message": "已存在进行中的理解小测",
            "learning_status": review_context["learning_status"],
            "quiz": serialize_quiz(latest_quiz),
        }

    payload = generate_bridge_quiz(review_context, quiz_role=QUIZ_ROLE_MAIN)
    if payload["mode"] != "quiz":
        raise HTTPException(status_code=400, detail="当前复盘更适合先补充讲解，不适合直接出题")

    quiz_id = create_review_quiz(
        review_id=review_context["review_id"],
        student_id=review_context["student_id"],
        checkin_id=review_context["checkin_id"],
        round=1,
        quiz_role=QUIZ_ROLE_MAIN,
        quiz_type=payload["quiz_type"],
        question_text=payload["question_text"],
        options=payload["options"],
        correct_answer=payload["correct_answer"],
        explanation=payload["explanation"],
        bridge_feedback=payload.get("bridge_feedback", ""),
        distractor_feedback=payload.get("distractor_feedback", {}),
        target_bridge=payload["target_bridge"],
        source_error_layer=review_context["error_layer"],
        meta=payload.get("meta", {}),
    )
    update_review_learning_status(review_id, LEARNING_STATUS_QUIZ_IN_PROGRESS)
    return {
        "message": "已生成理解小测",
        "learning_status": LEARNING_STATUS_QUIZ_IN_PROGRESS,
        "quiz": serialize_quiz(get_quiz_by_id(quiz_id)),
    }


@app.post("/api/quizzes/{quiz_id}/answer")
def answer_quiz_endpoint(
    quiz_id: int,
    request: QuizAnswerRequest,
    user: dict = Depends(require_student),
):
    quiz = get_quiz_by_id(quiz_id)
    if not quiz or quiz["student_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="未找到这道理解小测")
    if quiz["status"] != "pending":
        raise HTTPException(status_code=400, detail="这道理解小测已经提交过答案了")

    review_context = get_review_context(quiz["review_id"])
    if not review_context:
        raise HTTPException(status_code=404, detail="未找到关联复盘")

    is_correct = is_quiz_answer_correct(quiz, request.answer_text)

    if is_correct:
        feedback_text = "答对了，这一步你跨过去了。"
        update_quiz_status(quiz_id, "correct")
        record_quiz_attempt(quiz_id, user["user_id"], request.answer_text, True, feedback_text)
        if quiz["quiz_role"] == QUIZ_ROLE_MAIN:
            update_review_learning_status(quiz["review_id"], LEARNING_STATUS_SELF_CHECK_REQUIRED)
            return {
                "is_correct": True,
                "feedback_text": feedback_text,
                "explanation": quiz["explanation"],
                "bridge_feedback": quiz.get("bridge_feedback", ""),
                "learning_status": LEARNING_STATUS_SELF_CHECK_REQUIRED,
                "next_state": "self_check_required",
            }
        if quiz["quiz_role"] == QUIZ_ROLE_KNOWLEDGE_CONFIRM:
            finalize_review_terminal_state(quiz["review_id"], LEARNING_STATUS_RESOLVED)
            return {
                "is_correct": True,
                "feedback_text": feedback_text,
                "explanation": quiz["explanation"],
                "bridge_feedback": quiz.get("bridge_feedback", ""),
                "learning_status": LEARNING_STATUS_RESOLVED,
                "next_state": "resolved",
            }

        finalize_review_terminal_state(quiz["review_id"], LEARNING_STATUS_RESOLVED)
        return {
            "is_correct": True,
            "feedback_text": feedback_text,
            "explanation": quiz["explanation"],
            "bridge_feedback": quiz.get("bridge_feedback", ""),
            "learning_status": LEARNING_STATUS_RESOLVED,
            "next_state": "resolved",
        }

    if quiz["quiz_role"] == QUIZ_ROLE_MAIN:
        feedback_text = selected_distractor_feedback(quiz, request.answer_text) or "这一步还差一点，我们把它再拆小一点。"
        update_quiz_status(quiz_id, "incorrect")
        record_quiz_attempt(quiz_id, user["user_id"], request.answer_text, False, feedback_text)

        followup_payload = generate_bridge_quiz(review_context, previous_quiz=quiz, quiz_role=QUIZ_ROLE_FOLLOWUP)
        if followup_payload["mode"] != "quiz":
            update_review_learning_status(quiz["review_id"], LEARNING_STATUS_REMEDY_AVAILABLE)
            return {
                "is_correct": False,
                "feedback_text": feedback_text,
                "explanation": fallback_feedback_text(
                    followup_payload,
                    "当前这一步更适合先换一种方式讲清楚，而不是继续出 follow-up 小题。",
                ),
                "learning_status": LEARNING_STATUS_REMEDY_AVAILABLE,
                "next_state": "remedy_available",
                "dynamic_button_label": dynamic_remedy_label(review_context["error_layer"]),
            }

        followup_quiz_id = create_review_quiz(
            review_id=review_context["review_id"],
            student_id=review_context["student_id"],
            checkin_id=review_context["checkin_id"],
            round=2,
            quiz_role=QUIZ_ROLE_FOLLOWUP,
            quiz_type=followup_payload["quiz_type"],
            question_text=followup_payload["question_text"],
            options=followup_payload["options"],
            correct_answer=followup_payload["correct_answer"],
            explanation=followup_payload["explanation"],
            bridge_feedback=followup_payload.get("bridge_feedback", ""),
            distractor_feedback=followup_payload.get("distractor_feedback", {}),
            target_bridge=followup_payload["target_bridge"],
            source_error_layer=review_context["error_layer"],
            meta=followup_payload.get("meta", {}),
        )
        update_review_learning_status(quiz["review_id"], LEARNING_STATUS_QUIZ_IN_PROGRESS)
        return {
            "is_correct": False,
            "feedback_text": feedback_text,
            "explanation": quiz["explanation"],
            "learning_status": LEARNING_STATUS_QUIZ_IN_PROGRESS,
            "next_state": "followup_quiz",
            "micro_hint": followup_payload.get("meta", {}).get("micro_hint", ""),
            "quiz": serialize_quiz(get_quiz_by_id(followup_quiz_id)),
        }

    if quiz["quiz_role"] == QUIZ_ROLE_FOLLOWUP:
        feedback_text = selected_distractor_feedback(quiz, request.answer_text) or "这一步还没完全打通，我们先换一种方式来帮你。"
        update_quiz_status(quiz_id, "incorrect")
        record_quiz_attempt(quiz_id, user["user_id"], request.answer_text, False, feedback_text)
        update_review_learning_status(quiz["review_id"], LEARNING_STATUS_REMEDY_AVAILABLE)
        return {
            "is_correct": False,
            "feedback_text": feedback_text,
            "explanation": quiz["explanation"],
            "learning_status": LEARNING_STATUS_REMEDY_AVAILABLE,
            "next_state": "remedy_available",
            "dynamic_button_label": dynamic_remedy_label(review_context["error_layer"]),
        }

    if quiz["quiz_role"] == QUIZ_ROLE_CONFIRM:
        feedback_text = selected_distractor_feedback(quiz, request.answer_text) or "这一步还是有点虚，我们先别硬往下冲，换一种方式继续带你。"
        update_quiz_status(quiz_id, "incorrect")
        record_quiz_attempt(quiz_id, user["user_id"], request.answer_text, False, feedback_text)
        update_review_learning_status(quiz["review_id"], LEARNING_STATUS_REMEDY_AVAILABLE)
        return {
            "is_correct": False,
            "feedback_text": feedback_text,
            "explanation": quiz["explanation"],
            "learning_status": LEARNING_STATUS_REMEDY_AVAILABLE,
            "next_state": "remedy_available",
            "dynamic_button_label": dynamic_remedy_label(review_context["error_layer"]),
        }

    if quiz["quiz_role"] == QUIZ_ROLE_KNOWLEDGE_CONFIRM:
        feedback_text = "这一步我们先停在这里，你的老师会来和你一起看一看。"
        update_quiz_status(quiz_id, "incorrect")
        record_quiz_attempt(quiz_id, user["user_id"], request.answer_text, False, feedback_text)
        finalize_review_terminal_state(quiz["review_id"], LEARNING_STATUS_NEEDS_TEACHER)
        create_teacher_flag(
            student_id=user["user_id"],
            flag_type="knowledge_bailout_not_passed",
            reason=f"知识卡后最小确认仍未通过：{quiz['target_bridge'] or review_context['key_bridge']}",
            severity="medium",
            review_id=quiz["review_id"],
            checkin_id=quiz["checkin_id"],
            target_bridge=quiz["target_bridge"] or review_context["key_bridge"],
        )
        return {
            "is_correct": False,
            "feedback_text": feedback_text,
            "explanation": quiz["explanation"],
            "learning_status": LEARNING_STATUS_NEEDS_TEACHER,
            "next_state": "needs_teacher_followup",
        }

    if (quiz.get("meta") or {}).get("confirm_stage") == "final_micro_confirm" or (quiz.get("meta") or {}).get("difficulty_level") == "final_micro_confirm":
        feedback_text = selected_distractor_feedback(quiz, request.answer_text) or "这一小步还是没站稳，我们换成一张知识卡把它单独讲清楚。"
        update_quiz_status(quiz_id, "incorrect")
        record_quiz_attempt(quiz_id, user["user_id"], request.answer_text, False, feedback_text)
        knowledge_card = generate_knowledge_bailout_card(review_context, quiz)
        knowledge_payload = generate_knowledge_confirm_quiz(review_context, knowledge_card, previous_quiz=quiz)
        knowledge_quiz_id = create_review_quiz(
            review_id=review_context["review_id"],
            student_id=review_context["student_id"],
            checkin_id=review_context["checkin_id"],
            round=MAX_SCAFFOLD_ROUNDS + 1,
            quiz_role=QUIZ_ROLE_KNOWLEDGE_CONFIRM,
            quiz_type=knowledge_payload["quiz_type"],
            question_text=knowledge_payload["question_text"],
            options=knowledge_payload["options"],
            correct_answer=knowledge_payload["correct_answer"],
            explanation=knowledge_payload["explanation"],
            bridge_feedback=knowledge_payload.get("bridge_feedback", ""),
            distractor_feedback=knowledge_payload.get("distractor_feedback", {}),
            target_bridge=knowledge_payload["target_bridge"],
            source_error_layer=review_context["error_layer"],
            meta=knowledge_payload.get("meta", {}),
        )
        update_review_learning_status(quiz["review_id"], LEARNING_STATUS_KNOWLEDGE_BAILOUT)
        return {
            "is_correct": False,
            "feedback_text": feedback_text,
            "explanation": quiz["explanation"],
            "learning_status": LEARNING_STATUS_KNOWLEDGE_BAILOUT,
            "next_state": "knowledge_bailout",
            "knowledge_card": knowledge_card,
            "quiz": serialize_quiz(get_quiz_by_id(knowledge_quiz_id)),
        }

    feedback_text = "这道题我们先停在这里，你的老师会来和你一起看一看。"
    update_quiz_status(quiz_id, "incorrect")
    record_quiz_attempt(quiz_id, user["user_id"], request.answer_text, False, feedback_text)
    finalize_review_terminal_state(quiz["review_id"], LEARNING_STATUS_NEEDS_TEACHER)
    create_teacher_flag(
        student_id=user["user_id"],
        flag_type="quiz_bridge_not_passed",
        reason=f"补救小测仍未通过：{quiz['target_bridge'] or review_context['key_bridge']}",
        severity="medium",
        review_id=quiz["review_id"],
        checkin_id=quiz["checkin_id"],
        target_bridge=quiz["target_bridge"] or review_context["key_bridge"],
    )
    return {
        "is_correct": False,
        "feedback_text": feedback_text,
        "explanation": quiz["explanation"],
        "learning_status": LEARNING_STATUS_NEEDS_TEACHER,
        "next_state": "needs_teacher_followup",
    }


@app.post("/api/reviews/{review_id}/self-check")
def review_self_check_endpoint(
    review_id: int,
    request: SelfCheckRequest,
    user: dict = Depends(require_student),
):
    review_context = get_review_context(review_id)
    if not review_context or review_context["student_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="未找到对应复盘")
    if review_context["review_status"] != REVIEW_STATUS_COMPLETED:
        raise HTTPException(status_code=400, detail="复盘尚未完成")
    if review_context["learning_status"] != LEARNING_STATUS_SELF_CHECK_REQUIRED:
        raise HTTPException(status_code=400, detail="当前复盘不在理解确认阶段")

    update_review_self_check(review_id, request.status)
    review_context["understanding_self_check"] = request.status

    if request.status == "clear":
        quizzes = get_quizzes_for_review(review_id)
        if not passes_explanation_gate(review_context, quizzes):
            update_review_learning_status(review_id, LEARNING_STATUS_REMEDY_AVAILABLE)
            return {
                "ok": True,
                "learning_status": LEARNING_STATUS_REMEDY_AVAILABLE,
                "next_state": "remedy_available",
                "feedback_text": "你现在还没有把这一步真正讲清楚，我们先回到卡住点，再走一遍。",
                "dynamic_button_label": dynamic_remedy_label(review_context["error_layer"]),
            }

        if not transfer_signal_has_explicit_trigger(
            review_context.get("transfer_signal", ""),
            review_context.get("key_bridge", ""),
        ):
            finalize_review_terminal_state(review_id, LEARNING_STATUS_RESOLVED)
            return {
                "ok": True,
                "learning_status": LEARNING_STATUS_RESOLVED,
                "next_state": "resolved",
                "feedback_text": "这一步已经讲清楚了，我们先停在这里，不继续开迁移确认题。",
            }

        confirm_payload = build_confirm_payload(
            review_context,
            previous_quiz=get_latest_quiz_for_review(review_id),
        )
        if confirm_payload["mode"] != "quiz":
            update_review_learning_status(review_id, LEARNING_STATUS_REMEDY_AVAILABLE)
            return {
                "ok": True,
                "learning_status": LEARNING_STATUS_REMEDY_AVAILABLE,
                "next_state": "remedy_available",
                "feedback_text": fallback_feedback_text(
                    confirm_payload,
                    "这一步更适合先换一种方式讲清楚，我们先不继续出确认题。",
                ),
                "explanation": fallback_feedback_text(
                    confirm_payload,
                    "这一步更适合先换一种方式讲清楚，我们先不继续出确认题。",
                ),
                "dynamic_button_label": dynamic_remedy_label(review_context["error_layer"]),
            }

        latest_quiz = get_latest_quiz_for_review(review_id)
        next_round = (latest_quiz["round"] if latest_quiz else 1) + 1
        quiz_id = create_review_quiz(
            review_id=review_context["review_id"],
            student_id=review_context["student_id"],
            checkin_id=review_context["checkin_id"],
            round=next_round,
            quiz_role=QUIZ_ROLE_CONFIRM,
            quiz_type=confirm_payload["quiz_type"],
            question_text=confirm_payload["question_text"],
            options=confirm_payload["options"],
            correct_answer=confirm_payload["correct_answer"],
            explanation=confirm_payload["explanation"],
            bridge_feedback=confirm_payload.get("bridge_feedback", ""),
            distractor_feedback=confirm_payload.get("distractor_feedback", {}),
            target_bridge=confirm_payload["target_bridge"],
            source_error_layer=review_context["error_layer"],
            meta=confirm_payload.get("meta", {}),
        )
        update_review_learning_status(review_id, LEARNING_STATUS_QUIZ_IN_PROGRESS)
        return {
            "ok": True,
            "learning_status": LEARNING_STATUS_QUIZ_IN_PROGRESS,
            "next_state": "confirm_quiz",
            "quiz": serialize_quiz(get_quiz_by_id(quiz_id)),
        }

    if request.status in {"confused", "guessed"}:
        update_review_learning_status(review_id, LEARNING_STATUS_REMEDY_AVAILABLE)
        return {
            "ok": True,
            "learning_status": LEARNING_STATUS_REMEDY_AVAILABLE,
            "next_state": "remedy_available",
            "dynamic_button_label": dynamic_remedy_label(review_context["error_layer"]),
        }

    confirm_payload = build_confirm_payload(
        review_context,
        previous_quiz=get_latest_quiz_for_review(review_id),
    )
    if confirm_payload["mode"] != "quiz":
        finalize_review_terminal_state(review_id, LEARNING_STATUS_RESOLVED)
        return {
            "ok": True,
            "learning_status": LEARNING_STATUS_RESOLVED,
            "next_state": "resolved",
            "feedback_text": "答对了，这一步你跨过去了。",
        }
    finalize_review_terminal_state(review_id, LEARNING_STATUS_RESOLVED)
    return {
        "ok": True,
        "learning_status": LEARNING_STATUS_RESOLVED,
        "next_state": "resolved",
        "feedback_text": "这一步已经过关，我们先停在这里。",
    }


@app.post("/api/reviews/{review_id}/remedy")
def remedy_review_endpoint(
    review_id: int,
    request: RemedyActionRequest,
    user: dict = Depends(require_student),
):
    review_context = get_review_context(review_id)
    if not review_context or review_context["student_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="未找到对应复盘")
    if review_context["review_status"] != REVIEW_STATUS_COMPLETED:
        raise HTTPException(status_code=400, detail="复盘尚未完成")
    if (review_context.get("remedy_count") or 0) >= MAX_REMEDY_ACTIONS:
        finalize_review_terminal_state(review_id, LEARNING_STATUS_NEEDS_TEACHER)
        create_teacher_flag(
            student_id=user["user_id"],
            flag_type="quiz_bridge_not_passed",
            reason=f"三轮支架已到上限，仍需老师跟进：{review_context['key_bridge']}",
            severity="medium",
            review_id=review_id,
            checkin_id=review_context["checkin_id"],
            target_bridge=review_context["key_bridge"],
        )
        return {
            "mode": "final",
            "learning_status": LEARNING_STATUS_NEEDS_TEACHER,
            "feedback_text": f"这一步我们已经连续带了 {MAX_SCAFFOLD_ROUNDS} 轮，先停在这里，你的老师会来和你一起看一看。",
        }

    if request.action_type == REMEDY_ACTION_EASIER_QUIZ:
        payload = generate_bridge_quiz(review_context, previous_quiz=get_latest_quiz_for_review(review_id), quiz_role=QUIZ_ROLE_REMEDY)
        if payload["mode"] != "quiz":
            explanation = generate_remedy_explanation(review_context, REMEDY_ACTION_DYNAMIC)
            count = increment_review_remedy_count(review_id)
            return {
                "mode": "explain",
                "learning_status": LEARNING_STATUS_REMEDY_IN_PROGRESS,
                "remedy_count": count,
                **explanation,
            }

        quiz_id = create_review_quiz(
            review_id=review_context["review_id"],
            student_id=review_context["student_id"],
            checkin_id=review_context["checkin_id"],
            round=MAX_SCAFFOLD_ROUNDS,
            quiz_role=QUIZ_ROLE_REMEDY,
            quiz_type=payload["quiz_type"],
            question_text=payload["question_text"],
            options=payload["options"],
            correct_answer=payload["correct_answer"],
            explanation=payload["explanation"],
            bridge_feedback=payload.get("bridge_feedback", ""),
            distractor_feedback=payload.get("distractor_feedback", {}),
            target_bridge=payload["target_bridge"],
            source_error_layer=review_context["error_layer"],
            meta=payload.get("meta", {}),
        )
        count = increment_review_remedy_count(review_id)
        return {
            "mode": "quiz",
            "learning_status": LEARNING_STATUS_REMEDY_IN_PROGRESS,
            "remedy_count": count,
            "quiz": serialize_quiz(get_quiz_by_id(quiz_id)),
        }

    explanation = generate_remedy_explanation(review_context, request.action_type)
    count = increment_review_remedy_count(review_id)
    return {
        "mode": "explain",
        "learning_status": LEARNING_STATUS_REMEDY_IN_PROGRESS,
        "remedy_count": count,
        **explanation,
    }


@app.post("/api/reviews/{review_id}/remedy/resolve")
def remedy_resolve_endpoint(
    review_id: int,
    request: RemedyResolveRequest,
    user: dict = Depends(require_student),
):
    review_context = get_review_context(review_id)
    if not review_context or review_context["student_id"] != user["user_id"]:
        raise HTTPException(status_code=404, detail="未找到对应复盘")

    if request.status == "resolved":
        payload = generate_final_micro_confirm_quiz(
            review_context,
            previous_quiz=get_latest_quiz_for_review(review_id),
        )
        if payload["mode"] == "quiz":
            quiz_id = create_review_quiz(
                review_id=review_context["review_id"],
                student_id=review_context["student_id"],
                checkin_id=review_context["checkin_id"],
                round=MAX_SCAFFOLD_ROUNDS,
                quiz_role=QUIZ_ROLE_REMEDY,
                quiz_type=payload["quiz_type"],
                question_text=payload["question_text"],
                options=payload["options"],
                correct_answer=payload["correct_answer"],
                explanation=payload["explanation"],
                bridge_feedback=payload.get("bridge_feedback", ""),
                distractor_feedback=payload.get("distractor_feedback", {}),
                target_bridge=payload["target_bridge"],
                source_error_layer=review_context["error_layer"],
                meta={**payload.get("meta", {}), "confirm_stage": "final_micro_confirm"},
            )
            update_review_learning_status(review_id, LEARNING_STATUS_QUIZ_IN_PROGRESS)
            return {
                "ok": True,
                "learning_status": LEARNING_STATUS_QUIZ_IN_PROGRESS,
                "next_state": "final_micro_confirm",
                "feedback_text": "好，我们用最后一个最小问题确认这一步是不是真的站稳了。",
                "quiz": serialize_quiz(get_quiz_by_id(quiz_id)),
            }

        finalize_review_terminal_state(review_id, LEARNING_STATUS_RESOLVED)
        return {
            "ok": True,
            "learning_status": LEARNING_STATUS_RESOLVED,
            "next_state": "resolved",
            "feedback_text": "这一步已经过关，我们先停在这里。",
        }

    finalize_review_terminal_state(review_id, LEARNING_STATUS_NEEDS_TEACHER)
    create_teacher_flag(
        student_id=user["user_id"],
        flag_type="quiz_bridge_not_passed",
        reason=f"补救讲解结束后仍需老师跟进：{review_context['key_bridge']}",
        severity="medium",
        review_id=review_id,
        checkin_id=review_context["checkin_id"],
        target_bridge=review_context["key_bridge"],
    )
    return {"ok": True, "learning_status": LEARNING_STATUS_NEEDS_TEACHER}


# ============ Teacher Dashboard Endpoints ============
@app.get("/api/teacher/announcements")
def list_teacher_announcements_endpoint(
    user: dict = Depends(require_teacher),
    limit: int = 20,
):
    del user
    return {
        "announcements": [
            _serialize_teacher_announcement(row)
            for row in list_teacher_announcements(limit=limit)
        ]
    }


@app.post("/api/teacher/announcements")
def create_teacher_announcement_endpoint(
    request: TeacherAnnouncementRequest,
    user: dict = Depends(require_teacher),
):
    title = (request.title or "").strip()
    body = (request.body_markdown or "").strip()
    if not title:
        raise HTTPException(status_code=422, detail={"message": "公告标题不能为空"})
    if not body:
        raise HTTPException(status_code=422, detail={"message": "公告内容不能为空"})
    announcement_id = create_teacher_announcement(
        title=title,
        body_markdown=body,
        pinned=request.pinned,
        status=request.status,
        created_by=user["user_id"],
    )
    announcement = next(
        (row for row in list_teacher_announcements(limit=50, include_archived=True) if row["id"] == announcement_id),
        None,
    )
    return {
        "status": "ok",
        "message": "公告已发布，学生首页会看到。",
        "announcement": _serialize_teacher_announcement(announcement),
    }


@app.get("/api/teacher/students")
def list_teacher_students_endpoint(
    user: dict = Depends(require_teacher),
):
    del user
    return {"students": list_student_accounts()}


@app.post("/api/teacher/change-password")
def change_teacher_password_endpoint(
    request: TeacherChangePasswordRequest,
    user: dict = Depends(require_teacher),
):
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail={"message": "两次输入的新密码不一致"})
    try:
        change_own_password(
            user_id=user["user_id"],
            current_password=request.current_password,
            new_password=request.new_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc
    return {"status": "ok", "message": "密码已修改，请妥善保存新密码"}


@app.post("/api/teacher/students")
def create_teacher_student_endpoint(
    request: TeacherStudentCreateRequest,
    user: dict = Depends(require_teacher),
):
    del user
    try:
        student = create_student_account(
            display_name=request.display_name,
            user_id=request.user_id,
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc
    return {"status": "ok", "student": student}


def _student_bulk_error_code(message: str) -> str:
    if "显示姓名" in message:
        return "missing_display_name"
    if "已经存在" in message:
        return "duplicate_user_id"
    if "登录账号" in message:
        return "invalid_user_id"
    if "密码" in message:
        return "invalid_password"
    return "parse_error"


@app.post("/api/teacher/students/bulk")
def create_teacher_students_bulk_endpoint(
    request: TeacherStudentBulkCreateRequest,
    user: dict = Depends(require_teacher),
):
    del user
    success_rows = []
    failed_rows = []
    for index, row in enumerate(request.rows, start=1):
        row_index = row.row_index or index
        display_name = (row.display_name or "").strip()
        user_id = (row.user_id or "").strip()
        password = (row.password or "").strip()
        if not display_name:
            failed_rows.append({
                "row_index": row_index,
                "display_name": display_name,
                "user_id": user_id,
                "error_code": "missing_display_name",
                "error_message": "请填写显示姓名",
            })
            continue
        try:
            student = create_student_account(
                display_name=display_name,
                user_id=user_id,
                password=password,
            )
        except ValueError as exc:
            message = str(exc)
            failed_rows.append({
                "row_index": row_index,
                "display_name": display_name,
                "user_id": user_id,
                "error_code": _student_bulk_error_code(message),
                "error_message": message,
            })
            continue
        success_rows.append({
            "row_index": row_index,
            "student": student,
        })
    return {
        "status": "ok",
        "success_rows": success_rows,
        "failed_rows": failed_rows,
    }


@app.post("/api/teacher/students/{student_id}/reset-password")
def reset_teacher_student_password_endpoint(
    student_id: str,
    request: TeacherStudentPasswordResetRequest,
    user: dict = Depends(require_teacher),
):
    del user
    try:
        student = reset_student_password(student_id, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc
    return {"status": "ok", "student": student}


@app.post("/api/teacher/students/{student_id}/status")
def update_teacher_student_status_endpoint(
    student_id: str,
    request: TeacherStudentStatusRequest,
    user: dict = Depends(require_teacher),
):
    del user
    try:
        student = set_student_active(student_id, request.active)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc
    return {"status": "ok", "student": student}


@app.get("/api/teacher/student-feedback")
def list_teacher_student_feedback_endpoint(
    user: dict = Depends(require_teacher),
    limit: int = 100,
    offset: int = 0,
):
    del user
    return {"feedback": list_student_feedback(limit=limit, offset=offset)}


@app.get("/api/teacher/review-samples")
def get_teacher_review_samples(
    user: dict = Depends(require_teacher),
    limit: int = 10,
):
    del user
    samples = list_teacher_review_samples(limit=max(1, min(limit, 30)))
    for sample in samples:
        review_mode = _detect_review_mode(sample.get("completion_status", ""), sample.get("submission_result"))
        sample["review_mode"] = review_mode
        sample["review_family"] = _family_for_review_mode(review_mode)
    return {"samples": samples}


@app.get("/api/teacher/bridge-rule-drafts/export")
def export_bridge_rule_draft(
    route_kind: Literal["candidate_bridge", "open_bridge"],
    bridge_id: str,
    days: int = 30,
    user: dict = Depends(require_teacher),
):
    del user
    suggestion = get_bridge_route_promotion_suggestion(
        route_kind=route_kind,
        bridge_id=bridge_id,
        days=max(1, min(days, 365)),
    )
    if not suggestion:
        raise HTTPException(status_code=404, detail="未找到对应桥规则草案")
    draft = suggestion.get("rule_draft") or {}
    filename = draft.get("filename") or "bridge_rule_draft.md"
    markdown = draft.get("draft_markdown") or ""
    return PlainTextResponse(
        markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/teacher/bridge-rule-drafts/decision")
def submit_bridge_rule_draft_decision(
    request: BridgeRuleDraftDecisionRequest,
    user: dict = Depends(require_teacher),
):
    suggestion = get_bridge_route_promotion_suggestion(
        route_kind=request.route_kind,
        bridge_id=request.bridge_id,
        days=max(1, min(request.days, 365)),
    )
    if not suggestion:
        raise HTTPException(status_code=404, detail="未找到对应桥规则草案")
    draft = suggestion.get("rule_draft") or {}
    record = upsert_bridge_rule_draft_decision(
        route_kind=request.route_kind,
        bridge_id=request.bridge_id,
        parent_focus=suggestion.get("parent_focus") or suggestion.get("stable_focus") or "",
        teacher_id=user["user_id"],
        decision=request.decision,
        notes=request.notes,
        draft_filename=draft.get("filename") or "",
        draft_markdown=draft.get("draft_markdown") or "",
        auto_promote=False,
    )
    return {"status": "ok", "decision": record}


@app.get("/api/teacher/bridge-rule-drafts/decisions")
def list_bridge_rule_draft_decision_endpoint(
    user: dict = Depends(require_teacher),
    limit: int = 30,
):
    decisions = list_bridge_rule_draft_decisions(
        teacher_id=user["user_id"],
        limit=max(1, min(limit, 100)),
    )
    return {"decisions": decisions}


@app.post("/api/teacher/bridge-registry/entries")
def create_bridge_registry_entry_endpoint(
    request: BridgeRegistryEntryRequest,
    user: dict = Depends(require_teacher),
):
    try:
        entry = create_bridge_registry_entry_from_decision(
            decision_id=request.decision_id,
            teacher_id=user["user_id"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok", "entry": entry}


@app.get("/api/teacher/bridge-registry/entries")
def list_bridge_registry_entries_endpoint(
    user: dict = Depends(require_teacher),
    limit: int = 50,
):
    del user
    entries = list_bridge_registry_entries(limit=max(1, min(limit, 100)))
    return {"entries": entries}


@app.get("/api/teacher/bridge-registry/entries/{entry_id}/resolver-patch-draft")
def get_bridge_registry_resolver_patch_draft(
    entry_id: int,
    user: dict = Depends(require_teacher),
):
    del user
    entry = get_bridge_registry_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="未找到对应 registry entry")
    patch_draft = build_resolver_patch_draft_for_registry_entry(entry)
    return {"patch_draft": patch_draft}


@app.post("/api/teacher/reviews/{review_id}/manual-review")
def submit_teacher_manual_review(
    review_id: int,
    request: TeacherManualReviewRequest,
    user: dict = Depends(require_teacher),
):
    review_context = get_review_context(review_id)
    if not review_context:
        raise HTTPException(status_code=404, detail="未找到对应 review")
    review_mode = _detect_review_mode(
        review_context.get("completion_status", ""),
        review_context.get("submission_result"),
    )
    review_family = _family_for_review_mode(review_mode)
    upsert_review_manual_review(
        review_id=review_id,
        checkin_id=review_context["checkin_id"],
        student_id=review_context["student_id"],
        teacher_id=user["user_id"],
        review_mode=review_mode,
        review_family=review_family,
        mode_correct=request.mode_correct,
        review_grounded=request.review_grounded,
        student_can_move_next=request.student_can_move_next,
        notes=request.notes or "",
    )
    return {"status": "ok"}


@app.get("/api/teacher/checkins")
def get_teacher_checkins(
    user: dict = Depends(require_teacher),
    limit: int = 100,
    offset: int = 0,
):
    """Teacher gets all checkins"""
    checkins = get_all_checkins(limit, offset)
    return {"checkins": checkins}


@app.get("/api/teacher/stats")
def get_teacher_stats(
    user: dict = Depends(require_teacher),
    days: int = 30,
):
    """Teacher gets error statistics"""
    student_reported_stats = get_error_stats(days)
    review_layer_stats = get_review_layer_stats(days)
    review_status_summary = get_review_status_summary(days)
    mastery_status_stats = get_mastery_status_stats(days)
    topic_l1_stats = get_topic_l1_stats(days)
    topic_l2_stats = get_topic_l2_stats(days)
    bridge_stats = get_bridge_stats(days)
    bridge_path_stats = get_bridge_path_stats(days)
    bridge_route_stats = get_bridge_route_stats(days)
    bridge_route_promotion_suggestions = get_bridge_route_promotion_suggestions(days)
    knowledge_bailout_stats = get_knowledge_bailout_stats(days)
    learning_issue_stats = get_aichat_learning_issue_stats(7)
    completion_summary = get_class_completion_summary(15)
    exit_trigger_summary = get_class_exit_trigger_summary(15)
    attention_students = _build_teacher_attention_students(days=7)
    teaching_suggestions = [
        {
            "title": row.get("label") or "近期学习问题",
            "reason": f"近 7 天有 {row.get('student_count', 0)} 名学生出现这一类问题。",
            "how_to_teach": row.get("teacher_action") or "先看学生最近一次 AIChat 证据，再用一个小样例讲清关键关系。",
            "students": [example.get("student_id", "") for example in (row.get("examples") or []) if example.get("student_id")],
            "evidence": row.get("examples") or [],
        }
        for row in learning_issue_stats[:3]
    ]
    manual_review_stats = get_manual_review_stats(days, teacher_id=user["user_id"])
    manual_review_stats_by_mode = get_manual_review_stats_breakdown(days, group_by="review_mode", teacher_id=user["user_id"])
    manual_review_stats_by_family = get_manual_review_stats_breakdown(days, group_by="review_family", teacher_id=user["user_id"])
    return {
        "stats": student_reported_stats,
        "student_reported_stats": student_reported_stats,
        "review_layer_stats": review_layer_stats,
        "review_status_summary": review_status_summary,
        "mastery_status_stats": mastery_status_stats,
        "topic_l1_stats": topic_l1_stats,
        "topic_l2_stats": topic_l2_stats,
        "bridge_stats": bridge_stats,
        "bridge_path_stats": bridge_path_stats,
        "bridge_route_stats": bridge_route_stats,
        "bridge_route_promotion_suggestions": bridge_route_promotion_suggestions,
        "knowledge_bailout_stats": knowledge_bailout_stats,
        "learning_issue_stats": learning_issue_stats,
        "completion_summary": completion_summary,
        "exit_trigger_summary": exit_trigger_summary,
        "attention_students": attention_students,
        "teaching_suggestions": teaching_suggestions,
        "manual_review_stats": manual_review_stats,
        "manual_review_stats_by_mode": manual_review_stats_by_mode,
        "manual_review_stats_by_family": manual_review_stats_by_family,
    }


@app.get("/api/teacher/flags")
def get_teacher_flags(
    user: dict = Depends(require_teacher),
):
    """Teacher gets flagged students"""
    flags = get_student_flags()
    return {"flags": flags}


@app.get("/api/teacher/aichat-observations")
def get_teacher_aichat_observations(
    user: dict = Depends(require_teacher),
    limit: int = 30,
    days: int = 30,
):
    """Teacher sees recent AIChat-only learning bottlenecks."""
    del user
    observations = list_teacher_aichat_observations(limit=limit, days=days)
    return {"observations": observations}


def _research_hash(value: str, prefix: str) -> str:
    digest = hashlib.sha256(f"bridge-research-v1|{value or ''}".encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _public_bridge_export_row(row: dict) -> dict:
    return {
        "sample_id": row.get("sample_id", ""),
        "student_hash": _research_hash(row.get("student_id", ""), "student"),
        "session_hash": _research_hash(row.get("session_id", ""), "session"),
        "problem_ref": row.get("problem_ref", ""),
        "problem_title": row.get("problem_title", ""),
        "problem_url": row.get("problem_url", ""),
        "student_message": row.get("student_message", ""),
        "assistant_reply": row.get("assistant_reply", ""),
        "gold_student_state": row.get("gold_student_state", ""),
        "gold_bridge_family": row.get("gold_bridge_family", ""),
        "gold_known_focus": row.get("gold_known_focus", ""),
        "gold_help_seeking_type": row.get("gold_help_seeking_type", ""),
        "gold_missing_link": row.get("gold_missing_link", ""),
        "gold_allowed_help_level": row.get("gold_allowed_help_level", ""),
        "gold_forbidden_completion": row.get("gold_forbidden_completion", ""),
        "needs_new_focus": bool(row.get("needs_new_focus")),
        "confidence": int(row.get("confidence") or 0),
        "annotator_id": row.get("annotator_id", ""),
        "notes": row.get("notes", ""),
        "has_problem_context": bool(row.get("has_problem_context")),
        "has_student_code": bool(row.get("has_student_code")),
        "annotated_at": row.get("annotated_at", ""),
    }


RESPONSE_REVIEW_LABEL_COLUMNS = [
    "dataset_id",
    "anonymized_response_id",
    "case_id",
    "overall_quality",
    "leakage_label",
    "preference_rank",
    "notes",
    "review_status",
    "annotator_id",
    "updated_at",
]


def _legacy_response_review_dataset() -> dict:
    return {
        "dataset_id": "default",
        "label": "默认回复盲评",
        "description": "默认本地回复盲评 CSV。",
        "workbook_csv_path": RESPONSE_REVIEW_WORKBOOK_CSV_PATH,
        "labels_jsonl_path": RESPONSE_REVIEW_LABELS_JSONL_PATH,
    }


def _response_review_dataset_list() -> list[dict]:
    datasets = list(globals().get("RESPONSE_REVIEW_DATASETS") or [])
    return datasets or [_legacy_response_review_dataset()]


def _resolve_response_review_dataset(dataset_id: str = "") -> dict:
    datasets = _response_review_dataset_list()
    requested_id = str(
        dataset_id
        or globals().get("DEFAULT_RESPONSE_REVIEW_DATASET_ID")
        or datasets[0].get("dataset_id")
        or "default"
    )
    for dataset in datasets:
        if str(dataset.get("dataset_id") or "") == requested_id:
            return dataset
    raise HTTPException(status_code=404, detail=f"Unknown response review dataset: {requested_id}")


def _response_review_dataset_public(dataset: dict, *, default_dataset_id: str) -> dict:
    workbook_path = Path(dataset.get("workbook_csv_path") or RESPONSE_REVIEW_WORKBOOK_CSV_PATH)
    return {
        "dataset_id": str(dataset.get("dataset_id") or ""),
        "label": str(dataset.get("label") or dataset.get("dataset_id") or ""),
        "description": str(dataset.get("description") or ""),
        "is_default": str(dataset.get("dataset_id") or "") == default_dataset_id,
        "workbook_exists": workbook_path.exists(),
    }


def _read_response_review_rows(dataset: dict | None = None) -> list[dict]:
    dataset = dataset or _resolve_response_review_dataset()
    path = Path(dataset.get("workbook_csv_path") or RESPONSE_REVIEW_WORKBOOK_CSV_PATH)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _read_response_review_labels(dataset: dict | None = None) -> dict[str, dict]:
    dataset = dataset or _resolve_response_review_dataset()
    path = Path(dataset.get("labels_jsonl_path") or RESPONSE_REVIEW_LABELS_JSONL_PATH)
    labels: dict[str, dict] = {}
    if not path.exists():
        return labels
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        response_id = str(row.get("anonymized_response_id") or "")
        if response_id:
            labels[response_id] = row
    return labels


def _public_response_review_item(row: dict, label: dict | None = None, *, dataset_id: str = "") -> dict:
    label = label or {}
    return {
        "dataset_id": dataset_id,
        "case_id": row.get("case_id", ""),
        "anonymized_response_id": row.get("anonymized_response_id", ""),
        "problem_ref": row.get("problem_ref", ""),
        "student_message": row.get("student_message", ""),
        "problem_context": row.get("problem_context", ""),
        "recent_dialogue": row.get("recent_dialogue", ""),
        "response_text": row.get("response_text", ""),
        "overall_quality": label.get("overall_quality", ""),
        "leakage_label": label.get("leakage_label", row.get("coach_leakage_label", "")),
        "preference_rank": label.get("preference_rank", row.get("coach_preference_rank", "")),
        "notes": label.get("notes", row.get("coach_notes", "")),
        "review_status": label.get("review_status", row.get("review_status", "unlabeled") or "unlabeled"),
        "updated_at": label.get("updated_at", ""),
    }


def _append_response_review_label(row: dict, dataset: dict | None = None) -> dict:
    dataset = dataset or _resolve_response_review_dataset(str(row.get("dataset_id") or ""))
    path = Path(dataset.get("labels_jsonl_path") or RESPONSE_REVIEW_LABELS_JSONL_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row


@app.get("/api/teacher/research/aichat-samples")
def get_teacher_research_aichat_samples(
    limit: int = 100,
    annotated: str = "all",
    user: dict = Depends(require_teacher),
):
    """Teacher lists AIChat student turns that can be annotated as BridgeBench samples."""
    del user
    return {"samples": list_bridge_research_samples(limit=limit, annotated=annotated)}


@app.get("/api/teacher/research/response-review-items")
def get_teacher_research_response_review_items(
    limit: int = 200,
    status: str = "all",
    dataset_id: str = "",
    user: dict = Depends(require_teacher),
):
    """List offline AIChat response-review rows for one-card coach blind review."""
    del user
    dataset = _resolve_response_review_dataset(dataset_id)
    resolved_dataset_id = str(dataset.get("dataset_id") or "")
    labels = _read_response_review_labels(dataset)
    items = [
        _public_response_review_item(
            row,
            labels.get(str(row.get("anonymized_response_id") or "")),
            dataset_id=resolved_dataset_id,
        )
        for row in _read_response_review_rows(dataset)
    ]
    if status == "labeled":
        items = [item for item in items if item.get("review_status") == "labeled"]
    elif status == "unlabeled":
        items = [item for item in items if item.get("review_status") != "labeled"]
    return {"items": items[: max(0, limit)], "total": len(items), "dataset_id": resolved_dataset_id}


@app.get("/api/teacher/research/response-review-datasets")
def get_teacher_research_response_review_datasets(user: dict = Depends(require_teacher)):
    """List available offline response-review batches."""
    del user
    datasets = _response_review_dataset_list()
    default_dataset_id = str(
        globals().get("DEFAULT_RESPONSE_REVIEW_DATASET_ID")
        or (datasets[0].get("dataset_id") if datasets else "")
        or ""
    )
    return {
        "default_dataset_id": default_dataset_id,
        "datasets": [
            _response_review_dataset_public(dataset, default_dataset_id=default_dataset_id)
            for dataset in datasets
        ],
    }


@app.post("/api/teacher/research/response-review-labels")
def save_teacher_research_response_review_label(
    request: ResponseReviewLabelRequest,
    user: dict = Depends(require_teacher),
):
    dataset = _resolve_response_review_dataset(request.dataset_id)
    dataset_id = str(dataset.get("dataset_id") or "")
    label = {
        "dataset_id": dataset_id,
        "anonymized_response_id": request.anonymized_response_id,
        "case_id": request.case_id,
        "overall_quality": request.overall_quality,
        "leakage_label": request.leakage_label,
        "preference_rank": request.preference_rank,
        "notes": request.notes,
        "review_status": request.review_status or "labeled",
        "annotator_id": user.get("user_id", ""),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "saved": True,
    }
    _append_response_review_label(label, dataset)
    return {"label": label}


@app.get("/api/teacher/research/response-review-labels/export")
def export_teacher_research_response_review_labels(
    format: Literal["jsonl", "csv"] = "csv",
    dataset_id: str = "",
    user: dict = Depends(require_teacher),
):
    """Export one-card coach response review labels."""
    del user
    dataset = _resolve_response_review_dataset(dataset_id)
    rows = list(_read_response_review_labels(dataset).values())
    if format == "jsonl":
        text = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
        if text:
            text += "\n"
        return PlainTextResponse(text, media_type="application/x-ndjson; charset=utf-8")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=RESPONSE_REVIEW_LABEL_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return PlainTextResponse(output.getvalue(), media_type="text/csv; charset=utf-8")


@app.post("/api/teacher/research/bridge-annotations")
def save_teacher_research_bridge_annotation(
    request: BridgeResearchAnnotationRequest,
    user: dict = Depends(require_teacher),
):
    annotation = upsert_bridge_research_annotation(
        sample_id=request.sample_id,
        student_message_id=request.student_message_id,
        annotator_id=user.get("user_id", ""),
        student_state=request.student_state,
        bridge_family=request.bridge_family,
        known_focus=request.known_focus,
        help_seeking_type=request.help_seeking_type,
        missing_link=request.missing_link,
        allowed_help_level=request.allowed_help_level,
        forbidden_completion=request.forbidden_completion,
        needs_new_focus=request.needs_new_focus,
        confidence=request.confidence,
        notes=request.notes,
    )
    return {"annotation": annotation}


@app.get("/api/teacher/research/bridge-annotations/export")
def export_teacher_research_bridge_annotations(
    format: Literal["jsonl", "csv"] = "jsonl",
    user: dict = Depends(require_teacher),
):
    """Export expert annotations as anonymized research data."""
    del user
    rows = [_public_bridge_export_row(row) for row in list_bridge_research_annotation_exports()]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if format == "csv":
        output = io.StringIO()
        fieldnames = [
            "sample_id",
            "gold_student_state",
            "gold_bridge_family",
            "gold_known_focus",
            "gold_help_seeking_type",
            "gold_missing_link",
            "gold_allowed_help_level",
            "gold_forbidden_completion",
            "needs_new_focus",
            "confidence",
            "student_hash",
            "session_hash",
            "problem_ref",
            "problem_title",
            "student_message",
            "assistant_reply",
            "annotator_id",
            "notes",
            "annotated_at",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        return PlainTextResponse(
            output.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="bridge_annotations_{timestamp}.csv"'},
        )
    content = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    if content:
        content += "\n"
    return PlainTextResponse(
        content,
        media_type="application/x-ndjson; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="bridge_annotations_{timestamp}.jsonl"'},
    )


@app.get("/api/teacher/student-dossier")
def get_teacher_student_dossier(
    student_id: str,
    days: int = 15,
    user: dict = Depends(require_teacher),
):
    """Teacher sees one student's recent learning diagnosis dossier."""
    del user
    clean_student_id = (student_id or "").strip()
    if not clean_student_id:
        raise HTTPException(status_code=422, detail={"message": "student_id 不能为空"})
    return get_student_learning_dossier(clean_student_id, days=days)


@app.get("/api/teacher/class-learning-diagnosis")
def get_teacher_class_learning_diagnosis(
    days: int = 15,
    user: dict = Depends(require_teacher),
):
    """Teacher sees class-level learning diagnosis for the homepage."""
    del user
    return get_class_learning_diagnosis(days=days)


@app.post("/api/teacher/student-notes")
def create_teacher_student_note_endpoint(
    request: TeacherStudentNoteRequest,
    user: dict = Depends(require_teacher),
):
    """Teacher writes a follow-up note for a student."""
    note = create_teacher_student_note(
        student_id=request.student_id,
        teacher_id=user.get("user_id", ""),
        note=request.note,
        status=request.status,
        next_followup_at=request.next_followup_at,
        intervention_type=request.intervention_type,
        target_issue=request.target_issue,
    )
    return {"status": "ok", "note": note}


@app.get("/api/teacher/student-notes")
def get_teacher_student_notes_endpoint(
    student_id: str,
    user: dict = Depends(require_teacher),
):
    """Teacher lists follow-up notes for a student."""
    del user
    clean_student_id = (student_id or "").strip()
    if not clean_student_id:
        raise HTTPException(status_code=422, detail={"message": "student_id 不能为空"})
    return {"notes": list_teacher_student_notes(clean_student_id)}


@app.get("/api/teacher/aichat_students")
def get_teacher_aichat_students(
    user: dict = Depends(require_teacher),
):
    """Teacher sees students who have complete AIChat evidence records."""
    del user
    return {"students": list_teacher_aichat_evidence_students()}


@app.get("/api/teacher/aichat_sessions")
def get_teacher_aichat_sessions(
    student_id: str,
    user: dict = Depends(require_teacher),
):
    """Teacher sees one student's AIChat evidence sessions."""
    del user
    clean_student_id = (student_id or "").strip()
    if not clean_student_id:
        raise HTTPException(status_code=422, detail={"message": "student_id 不能为空"})
    return {"sessions": list_teacher_aichat_evidence_sessions(clean_student_id)}


@app.get("/api/teacher/aichat_session_detail")
def get_teacher_aichat_session_detail(
    session_id: str,
    user: dict = Depends(require_teacher),
):
    """Teacher sees complete messages, summary, and judge labels for a session."""
    del user
    clean_session_id = (session_id or "").strip()
    if not clean_session_id:
        raise HTTPException(status_code=422, detail={"message": "session_id 不能为空"})
    detail = get_teacher_aichat_evidence_session_detail(clean_session_id)
    if not detail:
        raise HTTPException(status_code=404, detail={"message": "未找到对应 AIChat 会话"})
    return detail


@app.get("/api/teacher/aichat_session_analysis")
def get_teacher_aichat_session_analysis(
    session_id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_teacher),
):
    """Teacher-facing lazy session analysis.

    Trigger: teacher opens a session. If no analysis exists, create a
    processing row and generate outside the student reply path.
    """
    del user
    clean_session_id = (session_id or "").strip()
    if not clean_session_id:
        raise HTTPException(status_code=422, detail={"message": "session_id 不能为空"})

    detail = get_teacher_aichat_evidence_session_detail(clean_session_id)
    if not detail:
        raise HTTPException(status_code=404, detail={"message": "未找到对应 AIChat 会话"})

    existing = get_aichat_session_analysis(clean_session_id)
    if existing and existing.get("status") in {"completed", "failed", "processing"}:
        return _session_analysis_response(existing)

    summary = detail.get("summary") or {}
    upsert_aichat_session_analysis(
        session_id=clean_session_id,
        student_id=summary.get("student_id", ""),
        problem_id=summary.get("problem_id", ""),
        status="processing",
        model=os.environ.get("NOI_SESSION_ANALYST_MODEL", "deepseek-v4-pro"),
        prompt_version=SESSION_ANALYST_PROMPT_VERSION,
    )

    if (os.environ.get("NOI_SESSION_ANALYST_SYNC") or "").strip().lower() in {"1", "true", "yes", "on"}:
        _run_aichat_session_analysis(clean_session_id)
        return _session_analysis_response(get_aichat_session_analysis(clean_session_id))

    background_tasks.add_task(_run_aichat_session_analysis, clean_session_id)
    return _session_analysis_response(get_aichat_session_analysis(clean_session_id))


@app.post("/api/teacher/aichat_session_analysis/retry")
def retry_teacher_aichat_session_analysis(
    request: AichatSessionAnalysisRetryRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_teacher),
):
    """Teacher manually regenerates one session analysis."""
    del user
    clean_session_id = (request.session_id or "").strip()
    if not clean_session_id:
        raise HTTPException(status_code=422, detail={"message": "session_id 不能为空"})
    detail = get_teacher_aichat_evidence_session_detail(clean_session_id)
    if not detail:
        raise HTTPException(status_code=404, detail={"message": "未找到对应 AIChat 会话"})

    summary = detail.get("summary") or {}
    upsert_aichat_session_analysis(
        session_id=clean_session_id,
        student_id=summary.get("student_id", ""),
        problem_id=summary.get("problem_id", ""),
        status="processing",
        analysis_json={},
        main_issue="",
        teacher_next_action="",
        needs_followup=False,
        model=os.environ.get("NOI_SESSION_ANALYST_MODEL", "deepseek-v4-pro"),
        prompt_version=SESSION_ANALYST_PROMPT_VERSION,
        failure_reason="",
    )
    if (os.environ.get("NOI_SESSION_ANALYST_SYNC") or "").strip().lower() in {"1", "true", "yes", "on"}:
        _run_aichat_session_analysis(clean_session_id)
        return _session_analysis_response(get_aichat_session_analysis(clean_session_id))

    background_tasks.add_task(_run_aichat_session_analysis, clean_session_id)
    return _session_analysis_response(get_aichat_session_analysis(clean_session_id))


@app.get("/api/teacher/aichat_session_analysis/health")
def get_teacher_aichat_session_analysis_health(
    user: dict = Depends(require_teacher),
    days: int = 7,
):
    """Teacher sees whether the Session Analyst pipeline is healthy."""
    del user
    return get_aichat_session_analysis_health(days=days)


@app.get("/api/teacher/usage")
def get_teacher_usage(
    user: dict = Depends(require_teacher),
    days: int = 7,
):
    """Teacher gets usage statistics (daily checkins, rejections, avg chars)"""
    stats = get_usage_stats(days)
    return {"usage": stats}


@app.post("/api/teacher/reviews/retry-pending")
def retry_pending_reviews_endpoint(
    request: RetryPendingReviewsRequest,
    user: dict = Depends(require_teacher),
):
    """Teacher triggers a manual retry for pending reviews"""
    return retry_pending_reviews(limit=request.limit)


@app.get("/api/teacher/problems/analysis-failures")
def get_problem_analysis_failures_endpoint(
    user: dict = Depends(require_teacher),
    limit: int = 20,
):
    del user
    failures = list_problem_analysis_failures(limit=limit)
    return {"failures": failures}


@app.post("/api/teacher/problems/analysis/retry")
def retry_problem_analysis_endpoint(
    request: ProblemAnalysisRetryRequest,
    user: dict = Depends(require_teacher),
):
    del user
    pid = request.luogu_pid.strip()
    if not pid:
        raise HTTPException(status_code=422, detail="请提供要重试的洛谷题号")

    ok, status = retry_problem_analysis_by_pid(pid)
    problem = get_problem_by_luogu_pid(pid)
    if not problem:
        raise HTTPException(status_code=404, detail=f"本地题库中未找到 {pid}")

    analysis_status = serialize_problem_analysis_status(problem)
    if status == "completed":
        message = "题目分析已生成"
    elif status == "failed":
        message = "题目分析重试失败，请查看错误信息"
    else:
        message = "已重新触发题目分析"
    return {
        "ok": ok,
        "message": message,
        "analysis_status": analysis_status,
    }


@app.get("/")
def healthcheck() -> dict:
    """Health check endpoint - returns JSON (Step 1/2 compatibility)"""
    return {
        "message": "NOI Coach Agent API is running",
        "hint_limit": PER_PROBLEM_HINT_LIMIT,
        "version": "0.5.0",
    }


@app.get("/app")
@app.get("/app/{path:path}")
def serve_frontend(path: str = ""):
    """
    统一前端入口 - 所有学生端和教师端子路由都返回同一个前端壳层。
    兼容旧路径:
    - /app, /app/chat, /app/checkin, /app/history, /app/history/123
    新 Vue 路由:
    - /app/workspace/chat, /app/workspace/checkin
    - /app/archive, /app/archive/123
    - /app/teacher/*
    """
    allowed_prefixes = {"chat", "checkin", "history", "workspace", "archive", "teacher"}
    first_segment = path.split("/", 1)[0] if path else ""
    if first_segment and first_segment not in allowed_prefixes:
        return RedirectResponse(url="/app")

    return FileResponse(
        os.path.join(BASE_DIR, "static", "dist", "index.html"),
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
