"""W5 端到端演示：进阶 RAG 完整问答（检索 → 重排 → 生成）。

用法：
  .venv/Scripts/python.exe demo_ask.py
"""
import asyncio

from rag_advanced import ingest, ask


async def main():
    n = ingest()
    print(f"知识库切片数: {n}\n")
    for q in [
        "什么是闭包？它为什么能记住外部变量？",
        "装饰器底层靠什么实现？",
    ]:
        text, chunks, usage = await ask(q, top_k=3)
        print("=" * 60)
        print(f"问: {q}")
        print(f"答: {text}\n")
        print(f"  引用教材片段数: {len(chunks)}, usage: {usage}")


if __name__ == "__main__":
    asyncio.run(main())
