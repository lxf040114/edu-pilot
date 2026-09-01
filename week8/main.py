"""EduPilot 智能答疑系统（W8）：把教学辅导 Agent 暴露成 HTTP 服务，带多轮记忆。

接口：
  GET  /health                   健康检查（含活跃会话数）
  POST /v1/tutor/chat            答疑（非流式，带 session 记忆）
  POST /v1/tutor/chat/stream     答疑（流式 SSE）
  POST /v1/tutor/reset           清空某个会话的历史

启动（复用 week5 venv）：
  ..\\week5\\.venv\\Scripts\\python.exe -m uvicorn main:app --reload --port 8000
  文档：http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent import Agent

app = FastAPI(title="EduPilot 智能答疑 (W8)")
agent = Agent()
_sessions: dict[str, list[dict]] = {}  # session_id -> 完整 messages 历史


class ChatRequest(BaseModel):
    session_id: str = "default"
    query: str


class ResetRequest(BaseModel):
    session_id: str = "default"


@app.get("/health")
def health():
    return {"status": "ok", "active_sessions": len(_sessions)}


@app.post("/v1/tutor/chat")
def tutor_chat(req: ChatRequest):
    history = _sessions.get(req.session_id)
    answer, new_history = agent.run(req.query, history)
    _sessions[req.session_id] = new_history  # 保存历史，实现多轮记忆
    return {"session_id": req.session_id, "answer": answer}


@app.post("/v1/tutor/chat/stream")
def tutor_chat_stream(req: ChatRequest):
    history = _sessions.get(req.session_id)
    answer, new_history = agent.run(req.query, history)
    _sessions[req.session_id] = new_history

    def gen():
        # 简化流式：Agent 循环完成后，把完整答案按 SSE 分块返回。
        # 真正的 token 级流式（边生成边吐）见 W3 的 /v1/chat/stream；Agent+工具场景的
        # 流式需要边调工具边生成，留到 W11 整合时再实现。
        for i in range(0, len(answer), 30):
            yield f"data: {answer[i:i + 30]}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/v1/tutor/reset")
def tutor_reset(req: ResetRequest):
    _sessions.pop(req.session_id, None)
    return {"status": "ok", "session_id": req.session_id}
