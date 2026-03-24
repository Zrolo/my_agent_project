"""
NOI Agent FastAPI HTTP 接口
复用 noi_agent.py 核心业务逻辑
"""

import os
import uuid
from contextlib import asynccontextmanager
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 复用现有业务逻辑
from noi_agent import (
    chat,
    load_quota,
    save_quota,
    get_remaining_quota,
    PER_PROBLEM_HINT_LIMIT,
)

# 内存会话存储 {session_id: [{role, content}, ...]}
sessions: Dict[str, List[dict]] = {}


class ChatRequest(BaseModel):
    student_id: str = Field(..., description="学生ID")
    problem_id: str = Field(..., description="题目ID")
    message: str = Field(..., description="学生消息内容")
    session_id: str | None = Field(None, description="会话ID，首次对话可不传")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    remaining_quota: int


class QuotaResponse(BaseModel):
    student_id: str
    problem_id: str
    used: int
    limit: int
    remaining: int


class ResetQuotaRequest(BaseModel):
    student_id: str = Field(..., description="学生ID")
    problem_id: str | None = Field(None, description="题目ID，不传则重置该学生所有题目")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时检查环境变量"""
    api_key = os.environ.get("MOONSHOT_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 警告：MOONSHOT_API_KEY 未设置，对话接口将无法正常工作")
    else:
        print("✅ API Key 已配置")
    yield
    # 关闭时可以清理资源
    sessions.clear()


app = FastAPI(
    title="NOI Agent API",
    description="NOI竞赛教练Agent HTTP接口",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    学生发消息，Agent回复
    - 首次对话：不传 session_id，返回新的 session_id
    - 继续对话：传入之前返回的 session_id 保持上下文
    """
    # 获取或创建会话
    if req.session_id and req.session_id in sessions:
        session_id = req.session_id
        messages = sessions[session_id]
    else:
        session_id = str(uuid.uuid4())[:8]
        messages = []
        sessions[session_id] = messages

    # 添加用户消息
    messages.append({"role": "user", "content": req.message})

    # 调用核心业务逻辑
    try:
        reply_for_display, reply_for_history = chat(
            messages, req.student_id, req.problem_id
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

    # 存储干净回复到历史（用于下次对话）
    messages.append({"role": "assistant", "content": reply_for_history})

    # 限制历史长度，防止过长（保留最近10轮）
    if len(messages) > 20:
        sessions[session_id] = messages[-20:]

    # 获取当前剩余配额
    remaining = get_remaining_quota(req.student_id, req.problem_id)

    return ChatResponse(
        session_id=session_id,
        reply=reply_for_display,
        remaining_quota=remaining,
    )


@app.get("/quota/{student_id}/{problem_id}", response_model=QuotaResponse)
async def get_quota(student_id: str, problem_id: str):
    """查询指定学生和题目的配额状态"""
    quota = load_quota(student_id, problem_id)
    return QuotaResponse(
        student_id=student_id,
        problem_id=problem_id,
        used=quota["count"],
        limit=quota["max"],
        remaining=quota["max"] - quota["count"],
    )


@app.post("/quota/reset")
async def reset_quota(req: ResetQuotaRequest):
    """
    重置配额
    - 传了 problem_id：只重置该题目的配额
    - 没传 problem_id：重置该学生所有题目的配额
    """
    from noi_agent import QUOTA_FILE
    import json

    if not os.path.exists(QUOTA_FILE):
        return {"message": "配额文件不存在，无需重置"}

    with open(QUOTA_FILE, "r", encoding="utf-8") as f:
        all_quota = json.load(f)

    if req.student_id not in all_quota:
        return {"message": "该学生无配额记录"}

    if req.problem_id:
        # 重置单个题目
        if req.problem_id in all_quota[req.student_id]:
            all_quota[req.student_id][req.problem_id] = {
                "count": 0,
                "max": PER_PROBLEM_HINT_LIMIT,
            }
            with open(QUOTA_FILE, "w", encoding="utf-8") as f:
                json.dump(all_quota, f, ensure_ascii=False, indent=2)
            return {
                "message": f"已重置 {req.student_id} 的 {req.problem_id} 配额",
                "student_id": req.student_id,
                "problem_id": req.problem_id,
            }
        else:
            return {"message": "该题目无配额记录"}
    else:
        # 重置该学生所有题目
        all_quota[req.student_id] = {}
        with open(QUOTA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_quota, f, ensure_ascii=False, indent=2)
        return {
            "message": f"已重置 {req.student_id} 的所有配额",
            "student_id": req.student_id,
        }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "sessions": len(sessions)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
