"""进阶检索（深化 W9）：Multi-Query + Rerank，修复基础 RAG 的「召回不完整」问题。

W9 发现：基础 RAG（BGE top3）在第 3 题「递归两要素」翻车——正确答案的 chunk 排到 top3 外。
进阶版三板斧：
1. Multi-Query：让 LLM 把问题改写成多个查询，从不同角度召回
2. 合并去重：多个查询的结果合并
3. Rerank：cross-encoder 精排，把最相关的顶上来
"""
import json
import os
import re

import chromadb

from embedding import BGEZhEmbedding
from llm import chat

CHROMA_DIR = os.path.join(os.path.dirname(__file__), ".chroma")

_embed = BGEZhEmbedding()
_client = chromadb.PersistentClient(path=CHROMA_DIR)
# 复用 rag.py 已 ingest 的同一个 collection
_col = _client.get_or_create_collection("edu_kb", embedding_function=_embed)

_reranker = None


def multi_query_generate(query: str, n: int = 3) -> list[str]:
    """让 LLM 把问题改写成 n 个不同表述的查询。"""
    system = (
        "你是检索查询改写器。给定一个学生问题，生成多个不同表述的检索查询，"
        "帮助向量库从不同角度召回相关教材。只输出 JSON 字符串数组，不要解释，不要代码块。"
    )
    user = f"原问题：{query}\n\n请生成 {n} 个不同表述的检索查询，输出 JSON 数组："
    text, _ = chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.4,
    )
    try:
        arr = json.loads(text)
    except Exception:
        arr = re.findall(r'"([^"]+)"', text)
    if isinstance(arr, list) and arr:
        return [str(x) for x in arr if str(x).strip()][:n]
    return [query]


def rerank(query: str, candidates, final_k: int):
    """cross-encoder 精排。"""
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder("BAAI/bge-reranker-base")
    pairs = [(query, c[0]) for c in candidates]
    scores = _reranker.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return [c for c, _ in ranked[:final_k]]


def retrieve_advanced(query: str, final_k: int = 3, n_queries: int = 3, per_query: int = 5):
    """Multi-Query 召回 + 合并去重 + Rerank 精排。"""
    from rag import ingest  # 确保教材已入库
    ingest()

    queries = [query] + multi_query_generate(query, n_queries)
    seen = {}
    for q in queries:
        res = _col.query(query_texts=[q], n_results=per_query)
        for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            key = (m.get("source") or "") + "||" + d[:24]
            if key not in seen:
                seen[key] = (d, m, dist)
    candidates = list(seen.values())
    if len(candidates) <= final_k:
        return candidates
    return rerank(query, candidates, final_k)
