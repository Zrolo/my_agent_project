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
from functools import lru_cache
from typing import Literal, List, Optional, Dict
from urllib.parse import urlparse
from uuid import uuid4

import requests
from fastapi import Depends, FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from auth import (
    authenticate_user,
    create_token,
    get_current_user,
    require_student,
    require_teacher,
    security,
)
from noi_agent import (
    PER_PROBLEM_HINT_LIMIT,
    analyze_student_turn,
    build_policy_handoff_payload,
    chat,
    get_remaining_quota,
    load_quota,
    save_quota,
)
from database import (
    LEARNING_STATUS_NEEDS_TEACHER,
    LEARNING_STATUS_NOT_STARTED,
    LEARNING_STATUS_QUIZ_IN_PROGRESS,
    LEARNING_STATUS_SELF_CHECK_REQUIRED,
    LEARNING_STATUS_REMEDY_AVAILABLE,
    LEARNING_STATUS_REMEDY_IN_PROGRESS,
    LEARNING_STATUS_RESOLVED,
    REVIEW_STATUS_COMPLETED,
    REVIEW_STATUS_PENDING,
    init_db,
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
    get_student_flags,
    list_problem_analysis_failures,
    increment_review_remedy_count,
    increment_confirm_pool_skip,
    mark_review_attempt,
    mark_review_failed,
    mark_review_pending,
    record_quiz_attempt,
    record_checkin_stats,
    record_rejected_checkin,
    get_problem_by_luogu_pid,
    get_manual_review_stats,
    get_manual_review_stats_breakdown,
    get_review_events_for_checkin,
    list_teacher_review_samples,
    get_usage_stats,
    list_related_problems_by_luogu_pid,
    record_review_event,
    upsert_review_manual_review,
    update_quiz_status,
    update_review_bridge_path,
    update_review_learning_status,
    update_review_self_check,
    reset_review_for_student_retry,
)
from review_engine import (
    QUIZ_ROLE_CONFIRM,
    QUIZ_ROLE_FOLLOWUP,
    QUIZ_ROLE_MAIN,
    QUIZ_ROLE_REMEDY,
    REMEDY_ACTION_DYNAMIC,
    REMEDY_ACTION_EASIER_QUIZ,
    REMEDY_ACTION_REPHRASE,
    REMEDY_ACTION_SMALLER_EXAMPLE,
    _detect_review_mode,
    _family_for_review_mode,
    generate_bridge_quiz,
    generate_confirm_quiz_from_pool,
    generate_remedy_explanation,
    generate_review,
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
    return str(route_context.get("submission_result") or "").strip().lower() in FAILED_SUBMISSION_RESULTS


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
    title = (problem.get("title") or "").strip()
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


class ChatResponse(BaseModel):
    reply: str
    remaining_quota: int
    level: str
    handoff_payload: Optional[dict] = None


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
    oj_source: str = Field(..., pattern="^(luogu|codeforces|atcoder|other)$")
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
    created_at: str
    review_status: str
    review_mode: Optional[str] = None
    review_family: Optional[str] = None
    review: Optional[dict] = None
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
            review_quality_flags=review_result.get("review_quality_flags", []),
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
    if not os.environ.get("MOONSHOT_API_KEY"):
        return {
            "attempted": 0,
            "completed": 0,
            "still_pending": 0,
            "message": "MOONSHOT_API_KEY 未配置，已跳过待生成复盘重试",
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

    # 构建会话 key
    session_key = (user["user_id"], request.problem_id, request.session_id)
    
    # 获取或创建会话历史
    if session_key not in session_histories:
        session_histories[session_key] = []
    
    messages = session_histories[session_key].copy()
    messages.append({"role": "user", "content": request.message})
    handoff_payload = build_policy_handoff_payload(
        analyze_student_turn(messages[-1]["content"], messages),
        messages,
    )

    try:
        reply_for_display, reply_for_history, final_level = chat(
            messages,
            user["user_id"],
            request.problem_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc

    # 更新会话历史
    messages.append({"role": "assistant", "content": reply_for_history})
    session_histories[session_key] = messages
    
    # 清理旧会话（保留最近1000个）
    if len(session_histories) > 1000:
        oldest_key = next(iter(session_histories))
        del session_histories[oldest_key]

    # final_level 是 chat() 返回的真实最终等级（已经过硬闸门限制，与配额结算一致）
    return ChatResponse(
        reply=reply_for_display,
        remaining_quota=get_remaining_quota(user["user_id"], request.problem_id),
        level=final_level,
        handoff_payload=handoff_payload,
    )


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
    normalized_url = normalize_luogu_problem_url(request.url.strip())
    if not normalized_url:
        raise HTTPException(status_code=400, detail="当前仅支持导入洛谷题号或公开题目链接")

    try:
        payload = fetch_luogu_problem(normalized_url)
    except requests.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"读取洛谷题面失败：{exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ProblemImportResponse(
        problem_url=payload["problem_url"],
        problem_pid=payload.get("problem_pid"),
        problem_title=payload["problem_title"],
        problem_context=payload["problem_context"],
        problem_tags=payload.get("problem_tags", []),
        oj_source="luogu",
        message="已自动导入洛谷题目标题、题面和标签",
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
    is_valid, error_msg = validate_bottleneck(request.bottleneck_text)
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

    local_problem_id = None
    problem_card = None
    analysis_source = None
    session_id = _new_checkin_session_id()

    if request.oj_source == "luogu" and resolved_problem_url:
        try:
            imported_problem = fetch_luogu_problem(resolved_problem_url)
        except Exception as exc:
            if not resolved_problem_title or len(resolved_problem_context) < 10:
                raise HTTPException(
                    status_code=422,
                    detail=f"洛谷题目自动导入失败：{exc}",
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

    if request.oj_source == "luogu":
        if len(resolved_problem_context) < 10:
            raise HTTPException(status_code=422, detail="请提供可导入的洛谷题号 / 链接，或手动补充题面 / Markdown")
    else:
        if len(resolved_problem_context) < 10:
            raise HTTPException(status_code=422, detail="当前来源暂不支持自动导入，请至少粘贴10个字的题面 / Markdown")
    
    # Step 2: 创建打卡记录（校验已通过）
    checkin_id = create_checkin(
        student_id=student_id,
        problem_url=resolved_problem_url,
        problem_title=resolved_problem_title,
        oj_source=request.oj_source,
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
        oj_source=request.oj_source,
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

    if request.oj_source == "luogu" and local_problem_id:
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
    return item


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
    item = get_student_checkin_by_id(user["user_id"], checkin_id)
    if not item:
        raise HTTPException(status_code=404, detail="未找到对应打卡")

    def event_stream():
        last_status_signature = None
        last_draft_signature = None
        while True:
            payload = _build_checkin_stream_payload(checkin_id, item)
            status_signature = (
                payload.get("phase"),
                payload.get("review_status"),
                payload.get("message"),
                payload.get("updated_at"),
            )
            draft_review = payload.get("draft_review") or {}
            draft_signature = tuple(draft_review.get(key, "") for key in ("main_block", "key_bridge", "next_step", "transfer_signal"))
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
    if (review_context.get("remedy_count") or 0) >= 2:
        finalize_review_terminal_state(review_id, LEARNING_STATUS_NEEDS_TEACHER)
        create_teacher_flag(
            student_id=user["user_id"],
            flag_type="quiz_bridge_not_passed",
            reason=f"补救次数已用完，仍需老师跟进：{review_context['key_bridge']}",
            severity="medium",
            review_id=review_id,
            checkin_id=review_context["checkin_id"],
            target_bridge=review_context["key_bridge"],
        )
        return {
            "mode": "final",
            "learning_status": LEARNING_STATUS_NEEDS_TEACHER,
            "feedback_text": "这道题我们先停在这里，你的老师会来和你一起看一看。",
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
            round=3,
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
        finalize_review_terminal_state(review_id, LEARNING_STATUS_RESOLVED)
        return {"ok": True, "learning_status": LEARNING_STATUS_RESOLVED}

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
    manual_review_stats = get_manual_review_stats(days, teacher_id=user["user_id"])
    manual_review_stats_by_mode = get_manual_review_stats_breakdown(days, group_by="review_mode", teacher_id=user["user_id"])
    manual_review_stats_by_family = get_manual_review_stats_breakdown(days, group_by="review_family", teacher_id=user["user_id"])
    return {
        "stats": student_reported_stats,
        "student_reported_stats": student_reported_stats,
        "review_layer_stats": review_layer_stats,
        "review_status_summary": review_status_summary,
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
def serve_frontend():
    """Serve the frontend HTML at /app"""
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
