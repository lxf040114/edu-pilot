"""W5 检索质量对比：量化 W4(基线 MiniLM) → W5(中文嵌入+MQ+rerank) 的提升。

用法：
  .venv/Scripts/python.exe test_rag_advanced.py

思路：准备一组『黄金问题』，每个问题已知答案应该来自哪篇教材（gold source）。
对比两种检索策略的 top1 是否命中 gold source，统计命中率。
"""
from rag_advanced import ingest, retrieve_baseline, retrieve_multi_query, retrieve_zh

# (问题, 期望命中的教材文件)
GOLD = [
    ("什么是闭包？它为什么能记住外部变量？", "闭包.md"),
    ("装饰器底层是靠什么实现的？", "装饰器.md"),
    ("递归和迭代有什么区别？", "递归.md"),
    ("列表推导式比普通 for 循环快吗？为什么？", "列表推导式.md"),
]


def top_source(chunks):
    return chunks[0][1]["source"] if chunks else None


def main():
    n = ingest()
    print(f"知识库切片数: {n}\n")

    base_hit = adv_hit = zh_hit = 0
    print("=" * 64)
    for q, gold in GOLD:
        base = retrieve_baseline(q, top_k=3)          # W4 基线
        zh = retrieve_zh(q, top_k=3)                  # 只换中文嵌入
        adv = retrieve_multi_query(q, final_k=3)      # 中文嵌入 + MQ + rerank

        bh = top_source(base) == gold
        zh_h = top_source(zh) == gold
        ah = top_source(adv) == gold
        base_hit += bh
        zh_hit += zh_h
        adv_hit += ah

        print(f"\nQ: {q}")
        print(f"  期望源: {gold}")
        print(f"  [W4 基线 MiniLM]        top1={top_source(base):<12} {'OK' if bh else 'X'} | top3={[c[1]['source'] for c in base]}")
        print(f"  [W5 仅换中文嵌入]       top1={top_source(zh):<12} {'OK' if zh_h else 'X'} | top3={[c[1]['source'] for c in zh]}")
        print(f"  [W5 中文+MQ+rerank]     top1={top_source(adv):<12} {'OK' if ah else 'X'} | top3={[c[1]['source'] for c in adv]}")
    print("\n" + "=" * 64)
    total = len(GOLD)
    print(f"top1 命中率:")
    print(f"  W4 基线 (MiniLM)            : {base_hit}/{total}")
    print(f"  W5 仅换中文嵌入 (BGE-zh)    : {zh_hit}/{total}")
    print(f"  W5 中文嵌入+MQ+rerank       : {adv_hit}/{total}")


if __name__ == "__main__":
    main()
