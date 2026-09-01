"""FastAPI 应用：把 LLM 能力暴露成 HTTP 接口。

3 个接口：
- GET  /health            健康检查
- POST /v1/chat           一次性返回（JSON）
- POST /v1/chat/stream    SSE 流式返回（打字机效果）

运行：
  .venv/Scripts/python.exe -m uvicorn main:app --reload --port 8000
  文档：http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from loguru import logger
import json
import time

from llm import achat, astream
from config import settings

app = FastAPI(title="EduPilot API", version="0.1.0")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    temperature: float = 0.7


def _to_openai_msgs(messages: list[Message]) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in messages]


@app.get("/health")
async def health():
    return {"status": "ok", "provider": settings.llm_provider}


@app.post("/v1/chat")
async def chat(req: ChatRequest):
    t0 = time.time()
    reply, usage = await achat(_to_openai_msgs(req.messages), req.temperature)
    logger.info(f"chat done | tokens={usage} | {time.time()-t0:.2f}s")
    return {"reply": reply, "usage": usage}


@app.post("/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    async def event_gen():
        async for delta in astream(_to_openai_msgs(req.messages), req.temperature):
            # SSE 格式：每行 "data: <json>\n\n"，前端用 EventSource 读
            yield f"data: {json.dumps({'delta': delta}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
