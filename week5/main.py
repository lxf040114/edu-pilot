"""EduPilot W5 接口：把进阶 RAG 暴露成 HTTP 服务。

在 week3 的 FastAPI 骨架上加：
  GET  /health                 健康检查
  POST /v1/rag/advanced        一次性检索增强问答（中文嵌入 + Multi-Query + Rerank）
  POST /v1/rag/advanced/stream 流式版本（打字机）

启动：
  .venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
  文档：http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from rag_advanced import ingest, ask, astream_ask, retrieve_multi_query, retrieve_zh, build_user_prompt

app = FastAPI(title="EduPilot RAG Advanced (W5)")


@app.on_event("startup")
def _startup():
    # 启动即入库（首次会下载 bge 嵌入模型 + reranker 在首次检索时下载）
    n = ingest()
    print(f"[startup] 知识库已入库，共 {n} 个 chunk")


class RAGRequest(BaseModel):
    query: str
    top_k: int = 3
    use_multi_query: bool = True
    temperature: float = 0.3


@app.get("/health")
def health():
    return {"status": "ok", "module": "rag-advanced"}


@app.post("/v1/rag/advanced")
async def rag_advanced(req: RAGRequest):
    text, chunks, usage = await ask(req.query, req.top_k, req.use_multi_query)
    return {
        "answer": text,
        "retrieved": [c[:60] + ("..." if len(c) > 60 else "") for c in chunks],
        "usage": usage,
    }


@app.post("/v1/rag/advanced/stream")
async def rag_advanced_stream(req: RAGRequest):
    async def event_gen():
        chunks = (
            retrieve_multi_query(req.query, final_k=req.top_k)
            if req.use_multi_query
            else retrieve_zh(req.query, req.top_k)
        )
        async for tok in astream_ask(req.query, req.top_k, req.use_multi_query, req.temperature):
            yield f"data: {tok}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
