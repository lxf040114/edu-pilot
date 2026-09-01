"""LLM 客户端包装：把 openai SDK 的异步 + 流式调用封一层。

设计要点（呼应前两周）：
- async：LLM 是 IO 等待，async 才能高并发（W1 并发实验已验证）
- stream：用 AsyncOpenAI 的 stream=True 拿到逐 token 迭代器
- 一个 chat()（攒完返回）+ 一个 stream()（逐 token yield）
W6 的 Agent 会在这个基础上加 Function Calling 循环。
"""
from openai import AsyncOpenAI
from config import settings

_client = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key, base_url, _ = settings.active
        _client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=settings.request_timeout,
        )
    return _client


def _model() -> str:
    return settings.active[2]


async def achat(messages: list[dict], temperature: float = 0.7) -> tuple[str, dict]:
    """一次性对话：攒完所有 token 再返回 (文本, usage)。"""
    client = _get_client()
    resp = await client.chat.completions.create(
        model=_model(),
        messages=messages,
        temperature=temperature,
    )
    text = resp.choices[0].message.content or ""
    usage = {
        "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
        "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
    }
    return text, usage


async def astream(messages: list[dict], temperature: float = 0.7):
    """流式对话：异步生成器，每次 yield 一个 token 片段。"""
    client = _get_client()
    stream = await client.chat.completions.create(
        model=_model(),
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
