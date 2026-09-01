"""离线验证 RAG 全链路：载入教材 → 检索 → 拼 prompt → 调 LLM 回答。

跑：.venv/Scripts/python.exe test_rag.py
"""
import asyncio
from rag import ingest_dir, retrieve, build_prompt, KB_DIR
from llm import achat


async def main():
    print("=" * 60)
    print("1) 载入知识库")
    n = ingest_dir(KB_DIR)
    print(f"   载入 chunk 数：{n}")

    query = "什么是闭包？它为什么能记住外部变量？"
    print("=" * 60)
    print(f"2) 检索 top-5：{query}（小知识库用 top_k=5 保证召回定义）")
    chunks = retrieve(query, top_k=5)
    for i, (text, meta, dist) in enumerate(chunks):
        print(f"   #{i+1} 来源={meta['source']} 距离={dist:.4f}")
        print(f"       {text[:60]}...")

    print("=" * 60)
    print("3) 拼装 RAG prompt（只取前 220 字看长相）")
    prompt = build_prompt(query, [c[0] for c in chunks])
    print("   ", prompt[:220], "...")

    print("=" * 60)
    print("4) 调 LLM 基于教材回答")
    answer, usage = await achat([{"role": "user", "content": prompt}], temperature=0.3)
    print("   回答：", answer)
    print("   usage：", usage)

    print("=" * 60)
    print("✅ RAG 链路验证通过")


if __name__ == "__main__":
    asyncio.run(main())
