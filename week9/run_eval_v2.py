"""深化评测（三方 A/B）：无 RAG vs 基础 RAG vs 进阶 RAG。

验证：进阶 RAG（Multi-Query + Rerank）能否修复 W9 第 3 题「递归要素」的召回翻车。

用法（复用 week5 venv）：
  ..\\week5\\.venv\\Scripts\\python.exe run_eval_v2.py
"""
from evaluator import EVAL_DATA, run_baseline, run_rag
from llm import chat
from metrics import keyword_hit, llm_judge
from rag_advanced import retrieve_advanced


def run_rag_advanced(question: str, final_k: int = 3) -> str:
    """变体 C：进阶 RAG（Multi-Query + Rerank）。"""
    chunks = retrieve_advanced(question, final_k=final_k)
    context = "\n\n".join(c[0] for c in chunks)
    prompt = (
        "你是 EduPilot 的 Python 助教。请【只依据下面的教材内容】回答问题，"
        "不要编造教材之外的知识。如果教材里没有，就老实说『教材里没讲』。\n\n"
        f"【教材】\n{context}\n\n【问题】{question}\n\n回答："
    )
    text, _ = chat([{"role": "user", "content": prompt}], temperature=0.3)
    return text


def main():
    print("三方 A/B 评测：无 RAG vs 基础 RAG vs 进阶 RAG（Multi-Query+Rerank）\n")
    rows = []
    for item in EVAL_DATA:
        q = item["question"]
        kws = item["keywords"]
        a = run_baseline(q)          # 无 RAG
        b = run_rag(q)               # 基础 RAG（BGE top3）
        c = run_rag_advanced(q)      # 进阶 RAG
        ja, ha = llm_judge(q, a)
        jb, hb = llm_judge(q, b)
        jc, hc = llm_judge(q, c)
        rows.append({
            "q": q,
            "kw_base": keyword_hit(a, kws), "kw_rag": keyword_hit(b, kws), "kw_adv": keyword_hit(c, kws),
            "j_base": ja, "j_rag": jb, "j_adv": jc,
            "h_base": ha, "h_rag": hb, "h_adv": hc,
        })
        print(f"  [完成] {q[:24]}...")

    n = len(rows)
    kw = lambda k: sum(r[k] for r in rows) / n
    jj = lambda k: sum(r[k] for r in rows) / n
    hh = lambda k: sum(1 for r in rows if r[k]) / n

    print("\n" + "=" * 74)
    print(f"测试集：{n} 题\n")
    print(f"{'指标':<16}{'无RAG':<14}{'基础RAG':<14}{'进阶RAG':<14}")
    print("-" * 74)
    print(f"{'关键词命中率':<16}{kw('kw_base'):<14.2%}{kw('kw_rag'):<14.2%}{kw('kw_adv'):<14.2%}")
    print(f"{'LLM评委均分':<16}{jj('j_base'):<14.1f}{jj('j_rag'):<14.1f}{jj('j_adv'):<14.1f}")
    print(f"{'编造率':<16}{hh('h_base'):<14.0%}{hh('h_rag'):<14.0%}{hh('h_adv'):<14.0%}")
    print("=" * 74)

    # 重点看第 3 题（递归两要素，W9 翻车的那题）
    print("\n关键题明细（W9 翻车的「递归两要素」）：")
    for r in rows:
        if "递归" in r["q"] and "要素" in r["q"]:
            print(f"  Q: {r['q']}")
            print(f"    无RAG   → 评委{r['j_base']}分  编造{'是' if r['h_base'] else '否'}")
            print(f"    基础RAG → 评委{r['j_rag']}分  编造{'是' if r['h_rag'] else '否'}")
            print(f"    进阶RAG → 评委{r['j_adv']}分  编造{'是' if r['h_adv'] else '否'}")


if __name__ == "__main__":
    main()
