"""W4 RAG 服务：在 W3 的 /v1/chat 基础上加 /v1/rag（先检索教材再回答）。

启动：.venv/Scripts/python.exe -m uvicorn main:app --reload --port 8000
文档：http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from loguru import logger
import json
import time

from rag import ingest_dir, retrieve, build_prompt, KB_DIR
from llm import achat, astream


@asynccontextmanager
async def lifespan(app: FastAPI):
    n = ingest_dir(KB_DIR)
    logger.info(f"RAG 知识库已载入 | chunks={n}")
    yield


app = FastAPI(title="EduPilot RAG API", version="0.2.0", lifespan=lifespan)


class RAGRequest(BaseModel):
    query: str
    top_k: int = 5
    temperature: float = 0.3


@app.post("/v1/rag")
async def rag_chat(req: RAGRequest):
    t0 = time.time()
    chunks = retrieve(req.query, req.top_k)
    prompt = build_prompt(req.query, [c[0] for c in chunks])
    answer, usage = await achat([{"role": "user", "content": prompt}], req.temperature)
    logger.info(f"rag done | top_k={req.top_k} | tokens={usage} | {time.time()-t0:.2f}s")
    return {
        "answer": answer,
        "retrieved": [
            {"text": c[0], "source": c[1]["source"], "distance": round(c[2], 4)}
            for c in chunks
        ],
        "usage": usage,
    }


@app.post("/v1/rag/stream")
async def rag_stream(req: RAGRequest):
    chunks = retrieve(req.query, req.top_k)
    prompt = build_prompt(req.query, [c[0] for c in chunks])

    async def event_gen():
        async for delta in astream([{"role": "user", "content": prompt}], req.temperature):
            yield f"data: {json.dumps({'delta': delta}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
