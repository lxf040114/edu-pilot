"""EduPilot 统一入口：FastAPI 服务，整合 Agent + RAG + 评测。

启动（复用 week5 venv）：
  ..\\week5\\.venv\\Scripts\\python.exe -m uvicorn src.main:app --reload --port 8000
  文档：http://127.0.0.1:8000/docs
"""
import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.agent.agent import Agent

app = FastAPI(title="EduPilot", version="1.0")
agent = Agent()
_sessions: dict[str, list[dict]] = {}


class ChatRequest(BaseModel):
    session_id: str = "default"
    query: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "EduPilot", "active_sessions": len(_sessions)}


@app.post("/v1/chat")
def chat(req: ChatRequest):
    """教学辅导答疑（带多轮记忆）。"""
    history = _sessions.get(req.session_id)
    answer, new_history = agent.run(req.query, history)
    _sessions[req.session_id] = new_history
    return {"session_id": req.session_id, "answer": answer}


@app.post("/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    """token 级流式答疑：检索教材 + astream 逐 token 输出（真打字机，非分块）。"""
    from src.core.llm import astream
    from src.rag.retriever import retrieve

    chunks = retrieve(req.query, top_k=3)
    context = "\n\n".join(c[0] for c in chunks)
    prompt = (
        "你是 EduPilot 的 Python 助教。请【只依据下面的教材内容】回答问题，不要编造。\n\n"
        f"【教材】\n{context}\n\n【问题】{req.query}\n\n回答："
    )

    async def gen():
        async for tok in astream([{"role": "user", "content": prompt}], temperature=0.3):
            yield f"data: {json.dumps(tok, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/v1/evaluate")
def evaluate_endpoint():
    """跑 A/B 评测（无 RAG vs 有 RAG），返回汇总 + 明细。"""
    from src.eval.evaluator import evaluate, summarize
    rows = evaluate()
    return {"summary": summarize(rows), "detail": rows}
