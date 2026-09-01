"""A/B 评测流程（W9 核心）：基线（无 RAG） vs 变体（有 RAG）。

对应 JD「测试数据集 + 基线对比 + A/B 实验」：
- 测试数据集：eval_data.json（8 个问题 + 参考关键词）
- 基线：run_baseline —— 直接问 LLM，不带教材
- 变体：run_rag —— 先向量检索教材，再带上下文回答
- 对比：对每个问题同时跑两版，用 keyword_hit + llm_judge 打分，量化差距
"""
import json
import os

from llm import chat
from metrics import keyword_hit, llm_judge
from rag import retrieve

_EVAL_PATH = os.path.join(os.path.dirname(__file__), "eval_data.json")
EVAL_DATA = json.load(open(_EVAL_PATH, encoding="utf-8"))


def run_baseline(question: str) -> str:
    """基线：无 RAG，直接问 LLM。"""
    text, _ = chat([{"role": "user", "content": question}], temperature=0.3)
    return text


def run_rag(question: str, top_k: int = 3) -> str:
    """变体：有 RAG，先检索教材再回答。"""
    chunks = retrieve(question, top_k=top_k)
    context = "\n\n".join(c[0] for c in chunks)
    prompt = (
        "你是 EduPilot 的 Python 助教。请【只依据下面的教材内容】回答问题，"
        "不要编造教材之外的知识。如果教材里没有，就老实说『教材里没讲』。\n\n"
        f"【教材】\n{context}\n\n【问题】{question}\n\n回答："
    )
    text, _ = chat([{"role": "user", "content": prompt}], temperature=0.3)
    return text


def evaluate() -> list[dict]:
    """逐题跑基线 + 变体，返回每题的指标。"""
    rows = []
    for item in EVAL_DATA:
        q = item["question"]
        kws = item["keywords"]

        ans_a = run_baseline(q)
        ans_b = run_rag(q)

        ka = keyword_hit(ans_a, kws)
        kb = keyword_hit(ans_b, kws)
        ja, ha = llm_judge(q, ans_a)
        jb, hb = llm_judge(q, ans_b)

        rows.append({
            "question": q, "keywords": kws,
            "kw_base": ka, "kw_rag": kb,
            "judge_base": ja, "judge_rag": jb,
            "hall_base": ha, "hall_rag": hb,
        })
    return rows


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    return {
        "n": n,
        "kw_base": sum(r["kw_base"] for r in rows) / n,
        "kw_rag": sum(r["kw_rag"] for r in rows) / n,
        "judge_base": sum(r["judge_base"] for r in rows) / n,
        "judge_rag": sum(r["judge_rag"] for r in rows) / n,
        "hall_base": sum(1 for r in rows if r["hall_base"]) / n,
        "hall_rag": sum(1 for r in rows if r["hall_rag"]) / n,
    }
