"""
实验 2：流式输出 (Streaming)。

为什么流式？
- 同步调用：模型把整段答案生成完（约 5-10s）才返回，用户盯着白屏
- 流式调用：模型每生成几个字就推一次，前端可以"打字机"展示

技术上：
- 用 HTTP 长连接（chunked transfer encoding）
- 一边生成一边发，OAI 协议上叫 SSE (Server-Sent Events)

跑：python stream_chat.py

对比：
- 模式 A：一次性返回（同步）
- 模式 B：流式输出（同步）
- 模式 C：流式输出（异步）—— 演示批量场景
"""

import asyncio
import time

from llm_client import LLMClient


# 模式 A：一次性返回（同步）
def sync_full():
    print("\n--- 模式 A：一次性返回（同步） ---")
    client = LLMClient()
    messages = [{"role": "user", "content": "用 50 字解释什么是 Python 的装饰器"}]

    t0 = time.perf_counter()
    resp = client.chat(messages)
    elapsed = (time.perf_counter() - t0) * 1000

    print(f"❌ 等了 {elapsed:.0f}ms 后才一次打印：\n>>> {resp.content}\n")


# 模式 B：流式输出（同步）
def sync_stream():
    print("\n--- 模式 B：流式（同步）---")
    client = LLMClient()
    messages = [{"role": "user", "content": "用 50 字解释什么是 Python 的装饰器"}]

    print(">>> ", end="", flush=True)
    t0 = time.perf_counter()
    first_chunk_at = None
    for chunk in client.stream(messages):
        if first_chunk_at is None:
            first_chunk_at = (time.perf_counter() - t0) * 1000
        print(chunk, end="", flush=True)
    print()
    elapsed = (time.perf_counter() - t0) * 1000
    print(f"\n✅ 首个 chunk 在 {first_chunk_at:.0f}ms 就到了，全程 {elapsed:.0f}ms")


# 模式 C：批量并发（异步） —— 评测时一次跑 200 个问题就用这个
async def async_batch():
    print("\n--- 模式 C：批量并发（异步）---")
    client = LLMClient()
    questions = [
        "用 30 字解释 Python 的列表推导式",
        "用 30 字解释 Python 的生成器",
        "用 30 字解释 Python 的 lambda",
        "用 30 字解释 Python 的 map 函数",
    ]
    messages_batch = [
        [{"role": "user", "content": q}] for q in questions
    ]

    t0 = time.perf_counter()
    results = await asyncio.gather(*[client.achat(m) for m in messages_batch])
    elapsed = (time.perf_counter() - t0) * 1000

    for q, r in zip(questions, results):
        print(f"  Q: {q}")
        print(f"  A: {r.content}")
        print(f"     tokens={r.tokens_in + r.tokens_out} 延迟={r.latency_ms:.0f}ms")
        print()

    print(f"✅ 4 个问题并发，总耗时 {elapsed:.0f}ms")
    print("   （同步跑 4 个的话，耗时差不多 = 4 × 单个耗时）")


def main():
    print("=" * 60)
    print("   体验 LLM 流式输出")
    print("=" * 60)

    sync_full()
    sync_stream()
    asyncio.run(async_batch())

    print("\n" + "=" * 60)
    print("💡 小结")
    print("=" * 60)
    print("- 流式 = 用户体感快（首字早到）")
    print("- 并发 = 系统吞吐高（评测时一个跑 200 题就是用这个）")
    print("- FastAPI 接 LLM 时同时用 SSE + async 才能快")


if __name__ == "__main__":
    main()
