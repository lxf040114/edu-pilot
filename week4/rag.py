"""RAG 核心：把教材切成 chunk → 向量化 → 存 Chroma → 检索 → 拼成带上下文的 prompt。

复用 week3 的 llm.py / config.py（通过 sys.path 引入，不重复造轮子）。

W4 用 Chroma 自带 ONNX MiniLM 本地嵌入（无需额外 key）。
W5 会把它换成中文更强的嵌入模型 + 重排序，检索质量会明显提升。
"""
import sys
import os
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "week3"))

import chromadb
from chromadb.utils import embedding_functions

KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), ".chroma")
COLLECTION = "edu_kb"

_client = chromadb.PersistentClient(path=CHROMA_DIR)
# 本地 embedding，不调外部 API；ONNXMiniLM 首次使用会下载约几 MB 模型权重
_embed = embedding_functions.ONNXMiniLM_L6_V2()
_collection = _client.get_or_create_collection(COLLECTION, embedding_function=_embed)


def ingest_dir(dir_path: str = KB_DIR) -> int:
    """读取目录下所有 .md，按空行分段切成 chunk，写入向量库。返回 chunk 数。"""
    docs, ids, metas = [], [], []
    for fp in sorted(glob.glob(os.path.join(dir_path, "*.md"))):
        text = open(fp, encoding="utf-8").read()
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 10]
        for i, c in enumerate(chunks):
            docs.append(c)
            ids.append(f"{os.path.basename(fp)}#{i}")
            metas.append({"source": os.path.basename(fp)})
    if docs:
        _collection.upsert(documents=docs, ids=ids, metadatas=metas)
    return len(docs)


def retrieve(query: str, top_k: int = 3):
    """返回 [(文本, 元数据, 距离), ...]，距离越小越相关。"""
    res = _collection.query(query_texts=[query], n_results=top_k)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    return list(zip(docs, metas, dists))


def build_prompt(query: str, chunks: list[str]) -> str:
    """把检索到的教材片段拼进 system 指令，约束模型『只依据教材回答』。"""
    context = "\n\n----\n\n".join(chunks)
    return (
        "你是 EduPilot 的 Python 助教。请【只依据下面的教材内容】回答学生问题，"
        "不要编造教材之外的知识。如果教材里没有，就老实说『教材里没讲这部分』。\n\n"
        f"【教材内容】\n{context}\n\n"
        f"【学生问题】{query}\n\n回答："
    )
