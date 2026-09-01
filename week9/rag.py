"""W9 向量检索：供 A/B 实验的「有 RAG」分支使用。

切片策略：按 markdown 标题切（而不是按空行），让每个知识点（## 标题 + 内容）自成完整 chunk，
避免"答案被切碎在多个 chunk"导致检索召回不完整（W9 深化发现的根因）。
"""
import glob
import os
import re

import chromadb

from embedding import BGEZhEmbedding

KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), ".chroma")

_embed = BGEZhEmbedding()
_client = chromadb.PersistentClient(path=CHROMA_DIR)
_col = _client.get_or_create_collection("edu_kb", embedding_function=_embed)


def _split_by_heading(text: str) -> list[str]:
    """按 markdown 标题（# / ## / ###）切分，每个标题块作为一个 chunk。"""
    parts = re.split(r"(?=^#{1,3}\s)", text, flags=re.MULTILINE)
    return [p.strip() for p in parts if len(p.strip()) > 10]


def ingest():
    """懒加载：首次调用把教材切片入库。"""
    if _col.count() > 0:
        return
    docs, ids, metas = [], [], []
    for fp in sorted(glob.glob(os.path.join(KB_DIR, "*.md"))):
        text = open(fp, encoding="utf-8").read()
        chunks = _split_by_heading(text)
        for i, c in enumerate(chunks):
            docs.append(c)
            ids.append(f"{os.path.basename(fp)}#{i}")
            metas.append({"source": os.path.basename(fp)})
    if docs:
        _col.upsert(documents=docs, ids=ids, metadatas=metas)


def retrieve(query: str, top_k: int = 3):
    """返回 [(文本, 元数据, 距离), ...]。"""
    ingest()
    res = _col.query(query_texts=[query], n_results=top_k)
    return list(zip(res["documents"][0], res["metadatas"][0], res["distances"][0]))
