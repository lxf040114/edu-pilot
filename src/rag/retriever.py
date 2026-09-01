"""向量检索：把教材切片入库（BGE 嵌入），做语义检索。"""
import glob
import os

import chromadb

from src.rag.embedding import BGEZhEmbedding

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KB_DIR = os.path.join(_ROOT, "data", "knowledge_base")
CHROMA_DIR = os.path.join(_ROOT, ".chroma")

_embed = BGEZhEmbedding()
_client = chromadb.PersistentClient(path=CHROMA_DIR)
_col = _client.get_or_create_collection("edu_kb", embedding_function=_embed)


def ingest():
    """懒加载：首次调用把教材切片入库。"""
    if _col.count() > 0:
        return
    docs, ids, metas = [], [], []
    for fp in sorted(glob.glob(os.path.join(KB_DIR, "*.md"))):
        text = open(fp, encoding="utf-8").read()
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 10]
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
