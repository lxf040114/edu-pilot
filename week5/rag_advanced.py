"""RAG 进阶（W5）：在 W4 基础上做三件事，根治中文检索排序差的问题。

三板斧（对应 JD「RAG 知识库」的核心进阶能力）：
1. 换中文嵌入：BGE-zh 替代 MiniLM（英文），让中文语义距离更准
2. Multi-Query：让 LLM 把学生问题改写成多个查询，从不同角度召回，降低漏检
3. Rerank 重排序：用 cross-encoder 对召回候选做精排，把最相关的顶上来

同时保留一个「基线 collection」（Chrom 默认英文 MiniLM）用于量化对比 W4→W5 的提升。
"""
import os
import glob
import json
import re

import chromadb

from config import settings  # noqa: F401  (保持与其他周一致，实际配置在 llm 里用)
from llm import chat, achat, astream
from embedding import BGEZhEmbedding

KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), ".chroma")
COLLECTION_ZH = "edu_kb_zh"
COLLECTION_BASE = "edu_kb_base"

# 中文嵌入（首次实例化会下载约 130MB bge-small-zh 权重，之后缓存）
_embed_zh = BGEZhEmbedding()
_client = chromadb.PersistentClient(path=CHROMA_DIR)
# 进阶库：中文 BGE 嵌入
_col_zh = _client.get_or_create_collection(COLLECTION_ZH, embedding_function=_embed_zh)
# 基线库：Chrom 默认英文 MiniLM，用于量化对比（= W4 的做法）
_col_base = _client.get_or_create_collection(COLLECTION_BASE)

_reranker = None  # 懒加载，避免 import 时就下载 450MB


def ingest(dir_path: str = KB_DIR) -> int:
    """读取教材 .md，按空行切 chunk，写入「中文库」和「基线库」两个 collection。"""
    docs, ids, metas = [], [], []
    for fp in sorted(glob.glob(os.path.join(dir_path, "*.md"))):
        text = open(fp, encoding="utf-8").read()
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 10]
        for i, c in enumerate(chunks):
            docs.append(c)
            ids.append(f"{os.path.basename(fp)}#{i}")
            metas.append({"source": os.path.basename(fp)})
    if docs:
        _col_zh.upsert(documents=docs, ids=ids, metadatas=metas)
        _col_base.upsert(documents=docs, ids=ids, metadatas=metas)
    return len(docs)


def retrieve_baseline(query: str, top_k: int = 3):
    """基线检索：Chrom 默认英文 MiniLM（= W4），用于对比。"""
    res = _col_base.query(query_texts=[query], n_results=top_k)
    return list(zip(res["documents"][0], res["metadatas"][0], res["distances"][0]))


def retrieve_zh(query: str, top_k: int = 3):
    """只用中文 BGE 嵌入检索（不加 MQ/rerank），用于拆解各环节贡献。"""
    res = _col_zh.query(query_texts=[query], n_results=top_k)
    return list(zip(res["documents"][0], res["metadatas"][0], res["distances"][0]))


def multi_query_generate(query: str, n: int = 3) -> list[str]:
    """让 LLM 把问题改写成 n 个不同表述的查询，返回 list[str]。"""
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
        if not arr:
            arr = [l.strip(" -0123456789.").strip() for l in text.splitlines() if l.strip()]
    if isinstance(arr, list) and arr:
        return [str(x) for x in arr if str(x).strip()][:n]
    return [query]


def rerank(query: str, candidates, final_k: int):
    """cross-encoder 精排：对 (query, chunk) 逐对打分，取 top final_k。"""
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder("BAAI/bge-reranker-base")  # ~450MB 首次下载
    pairs = [(query, c[0]) for c in candidates]
    scores = _reranker.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return [c for c, _ in ranked[:final_k]]


def retrieve_multi_query(query: str, final_k: int = 3, n_queries: int = 3, per_query: int = 5):
    """Multi-Query + Rerank：多查询召回 → 去重合并 → cross-encoder 精排。"""
    queries = [query] + multi_query_generate(query, n_queries)
    seen = {}
    for q in queries:
        res = _col_zh.query(query_texts=[q], n_results=per_query)
        for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            key = (m.get("source") or "") + "||" + d[:24]
            if key not in seen:
                seen[key] = (d, m, dist)
    candidates = list(seen.values())
    if len(candidates) <= final_k:
        return candidates
    return rerank(query, candidates, final_k)


SYSTEM_PROMPT = (
    "你是 EduPilot 的 Python 助教。请【只依据下面的教材内容】回答学生问题，"
    "不要编造教材之外的知识。如果教材里没有，就老实说『教材里没讲这部分』。"
)


def build_user_prompt(query: str, chunks: list[str]) -> str:
    context = "\n\n----\n\n".join(chunks)
    return f"【教材内容】\n{context}\n\n【学生问题】{query}\n\n回答："


async def ask(query: str, top_k: int = 3, use_multi_query: bool = True):
    """完整问答：检索 → 拼 prompt → 生成。返回 (答案, 用到的 chunk 列表, usage)。"""
    chunks = retrieve_multi_query(query, final_k=top_k) if use_multi_query else retrieve_zh(query, top_k)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(query, [c[0] for c in chunks])},
    ]
    text, usage = await achat(messages, temperature=0.3)
    return text, [c[0] for c in chunks], usage


async def astream_ask(query: str, top_k: int = 3, use_multi_query: bool = True, temperature: float = 0.3):
    chunks = retrieve_multi_query(query, final_k=top_k) if use_multi_query else retrieve_zh(query, top_k)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(query, [c[0] for c in chunks])},
    ]
    async for tok in astream(messages, temperature=temperature):
        yield tok
