"""
FastAPI HTTP wrapper for the NOI coaching agent.

Run:
    uvicorn api_server:app --reload
"""

import os
from typing import Literal, List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
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
    chat,
    get_remaining_quota,
    load_quota,
    save_quota,
)
from database import (
    init_db,
    create_checkin,
    get_student_checkins,
    get_all_checkins,
    create_review,
    get_review_by_checkin,
    get_error_stats,
    get_student_flags,
    record_checkin_stats,
    record_rejected_checkin,
    get_usage_stats,
)
from review_engine import generate_review, validate_bottleneck

# 初始化数据库
init_db()

app = FastAPI(
    title="NOI Coach Agent API",
    description="HTTP interface for the NOI coaching agent with training loop.",
    version="0.3.0",
)


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
    problem_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    history: list[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    history_reply: str
    history: list[Message]
    quota: dict


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


# ============ Checkin Models ============
class CheckinRequest(BaseModel):
    problem_url: str = Field(..., min_length=1)
    problem_title: str = Field(..., min_length=1)
    oj_source: str = Field(..., pattern="^(luogu|codeforces|atcoder|other)$")
    completion_status: str = Field(..., pattern="^(independent|hinted|editorial|unfinished)$")
    bottleneck_text: str = Field(..., min_length=15)
    error_types: List[str] = Field(..., min_items=1)
    reflection: Optional[str] = None


class CheckinResponse(BaseModel):
    checkin_id: int
    review: Optional[dict] = None
    message: str


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


class ErrorStatItem(BaseModel):
    error_type: str
    count: int
    avg_completion_score: float


class StudentFlagItem(BaseModel):
    student_id: str
    flag_type: str
    description: str
    severity: str


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
    Requires student authentication.
    Student ID is taken from token, cannot be forged.
    """
    student_id = user["user_id"]
    
    messages = [message.model_dump() for message in request.history]
    messages.append({"role": "user", "content": request.message})

    try:
        reply_for_display, reply_for_history = chat(
            messages,
            student_id,
            request.problem_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc

    updated_history = [
        *request.history,
        Message(role="user", content=request.message),
        Message(role="assistant", content=reply_for_history),
    ]

    return ChatResponse(
        reply=reply_for_display,
        history_reply=reply_for_history,
        history=updated_history,
        quota=build_quota_response(student_id, request.problem_id).model_dump(),
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
    - Students can only view their own quota
    - Teachers can view any student's quota
    """
    # Check permission
    if user["role"] == "student":
        if user["user_id"] != student_id:
            raise HTTPException(
                status_code=403,
                detail="Students can only view their own quota",
            )
    # Teachers can view any
    
    return build_quota_response(student_id, problem_id)


@app.post("/quota/reset", response_model=QuotaResponse)
def reset_quota_endpoint(
    request: ResetQuotaRequest,
    user: dict = Depends(require_teacher),
):
    """
    Reset quota for a student and problem.
    Only teachers can call this endpoint.
    """
    save_quota(
        request.student_id,
        request.problem_id,
        {"count": 0, "max": PER_PROBLEM_HINT_LIMIT},
    )
    return build_quota_response(request.student_id, request.problem_id)


# ============ Checkin Endpoints ============
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
    3. 校验通过：创建checkin，调用LLM生成复盘
    4. LLM失败：保留checkin，不创建review，返回review=null
    5. LLM成功：创建checkin和review
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
    
    # Step 2: 创建打卡记录（校验已通过）
    checkin_id = create_checkin(
        student_id=student_id,
        problem_url=request.problem_url,
        problem_title=request.problem_title,
        oj_source=request.oj_source,
        completion_status=request.completion_status,
        bottleneck_text=request.bottleneck_text,
        error_types=request.error_types,
        reflection=request.reflection,
    )
    
    # 记录打卡统计
    record_checkin_stats(len(request.bottleneck_text))
    
    # Step 3: 生成 AI 复盘
    review_result = generate_review(
        problem_title=request.problem_title,
        oj_source=request.oj_source,
        completion_status=request.completion_status,
        bottleneck_text=request.bottleneck_text,
        error_types=request.error_types,
        reflection=request.reflection,
    )
    
    # Step 4: 根据复盘结果处理
    if not review_result["ok"]:
        if review_result["kind"] == "llm_unavailable":
            # LLM 失败：保留有效打卡，但不保存 review
            return CheckinResponse(
                checkin_id=checkin_id,
                review=None,
                message=review_result["message"],
            )
        else:
            # 其他错误（理论上不会走到这里，因为前置校验已过）
            return CheckinResponse(
                checkin_id=checkin_id,
                review=None,
                message=review_result["message"],
            )
    
    # Step 5: LLM 成功，保存复盘
    review_data = review_result["review"]
    create_review(
        checkin_id=checkin_id,
        student_id=student_id,
        error_tags=review_data["error_tags"],
        diagnosis=review_data["diagnosis"],
        next_action=review_data["next_action"],
        suggested_topic=review_data["suggested_topic"],
    )
    
    return CheckinResponse(
        checkin_id=checkin_id,
        review=review_data,
        message="打卡成功，已生成复盘",
    )


@app.get("/api/checkins/me")
def get_my_checkins(
    user: dict = Depends(require_student),
    limit: int = 50,
):
    """Student gets their own checkin history"""
    checkins = get_student_checkins(user["user_id"], limit)
    return {"checkins": checkins}


# ============ Teacher Dashboard Endpoints ============
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
    stats = get_error_stats(days)
    return {"stats": stats}


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


@app.get("/")
def healthcheck() -> dict:
    """Health check endpoint - returns JSON (Step 1/2 compatibility)"""
    return {
        "message": "NOI Coach Agent API is running",
        "hint_limit": PER_PROBLEM_HINT_LIMIT,
        "version": "0.3.0",
    }


@app.get("/app")
def serve_frontend():
    """Serve the frontend HTML at /app"""
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
