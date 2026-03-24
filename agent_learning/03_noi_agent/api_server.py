"""
FastAPI HTTP wrapper for the NOI coaching agent.

Run:
    uvicorn api_server:app --reload
"""

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

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
    version="0.1.0",
)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    problem_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    history: list[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    history_reply: str
    history: list[Message]
    quota: dict


class QuotaResponse(BaseModel):
    student_id: str
    problem_id: str
    count: int
    max: int
    remaining: int


class ResetQuotaRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    problem_id: str = Field(..., min_length=1)


def build_quota_response(student_id: str, problem_id: str) -> QuotaResponse:
    quota = load_quota(student_id, problem_id)
    return QuotaResponse(
        student_id=student_id,
        problem_id=problem_id,
        count=quota["count"],
        max=quota["max"],
        remaining=get_remaining_quota(student_id, problem_id),
    )


@app.get("/")
def healthcheck() -> dict:
    return {
        "message": "NOI Coach Agent API is running",
        "hint_limit": PER_PROBLEM_HINT_LIMIT,
    }


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    messages = [message.model_dump() for message in request.history]
    messages.append({"role": "user", "content": request.message})

    try:
        reply_for_display, reply_for_history = chat(
            messages,
            request.student_id,
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
        quota=build_quota_response(request.student_id, request.problem_id).model_dump(),
    )


@app.get("/quota/{student_id}/{problem_id}", response_model=QuotaResponse)
def get_quota_endpoint(student_id: str, problem_id: str) -> QuotaResponse:
    return build_quota_response(student_id, problem_id)


@app.post("/quota/reset", response_model=QuotaResponse)
def reset_quota_endpoint(request: ResetQuotaRequest) -> QuotaResponse:
    save_quota(
        request.student_id,
        request.problem_id,
        {"count": 0, "max": PER_PROBLEM_HINT_LIMIT},
    )
    return build_quota_response(request.student_id, request.problem_id)
