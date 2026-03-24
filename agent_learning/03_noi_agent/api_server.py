"""
FastAPI HTTP wrapper for the NOI coaching agent.

Run:
    uvicorn api_server:app --reload
"""

from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

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

app = FastAPI(
    title="NOI Coach Agent API",
    description="HTTP interface for the NOI coaching agent with per-problem quota control.",
    version="0.2.0",
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


@app.get("/")
def healthcheck() -> dict:
    return {
        "message": "NOI Coach Agent API is running",
        "hint_limit": PER_PROBLEM_HINT_LIMIT,
        "version": "0.2.0",
    }
