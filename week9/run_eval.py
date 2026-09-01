"""W9 评测入口：跑 A/B 实验，输出量化对比结果。

用法（复用 week5 venv）：
  ..\\week5\\.venv\\Scripts\\python.exe run_eval.py
"""
from evaluator import evaluate, summarize


def main():
    print("开始评测（每个问题跑「无 RAG 基线」+「有 RAG 变体」+ 2 次 LLM 评委）...\n")
    rows = evaluate()
    s = summarize(rows)

    print("=" * 74)
    print(f"测试集规模：{s['n']} 题\n")
    print(f"{'指标':<16}{'基线(无RAG)':<16}{'变体(有RAG)':<16}{'变化':<12}")
    print("-" * 74)
    print(f"{'关键词命中率':<16}{s['kw_base']:.2%}{'':<11}{s['kw_rag']:.2%}{'':<11}{s['kw_rag']-s['kw_base']:+.2%}")
    print(f"{'LLM评委均分':<16}{s['judge_base']:.1f}/10{'':<7}{s['judge_rag']:.1f}/10{'':<7}{s['judge_rag']-s['judge_base']:+.1f}")
    print(f"{'编造率(越低越好)':<16}{s['hall_base']:.0%}{'':<11}{s['hall_rag']:.0%}{'':<11}{s['hall_rag']-s['hall_base']:+.0%}")
    print("=" * 74)

    print("\n逐题明细：")
    for r in rows:
        print(f"\nQ: {r['question'][:32]}")
        print(f"  无RAG → 关键词{r['kw_base']:.0%}  评委{r['judge_base']}分  编造{'是' if r['hall_base'] else '否'}")
        print(f"  有RAG → 关键词{r['kw_rag']:.0%}  评委{r['judge_rag']}分  编造{'是' if r['hall_rag'] else '否'}")


if __name__ == "__main__":
    main()
