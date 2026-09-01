"""A/B 评测流程：基线（无 RAG） vs 变体（有 RAG）。"""
import json
import os

from src.core.llm import chat
from src.eval.metrics import keyword_hit, llm_judge
from src.rag.retriever import retrieve

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_EVAL_PATH = os.path.join(_ROOT, "data", "eval_data.json")
EVAL_DATA = json.load(open(_EVAL_PATH, encoding="utf-8"))


def run_baseline(question: str) -> str:
    text, _ = chat([{"role": "user", "content": question}], temperature=0.3)
    return text


def run_rag(question: str, top_k: int = 3) -> str:
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
    rows = []
    for item in EVAL_DATA:
        q = item["question"]
        kws = item["keywords"]
        ans_a = run_baseline(q)
        ans_b = run_rag(q)
        ja, ha = llm_judge(q, ans_a)
        jb, hb = llm_judge(q, ans_b)
        rows.append({
            "question": q,
            "kw_base": keyword_hit(ans_a, kws), "kw_rag": keyword_hit(ans_b, kws),
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
