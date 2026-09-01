"""LLM 客户端包装：把 openai SDK 的同步 + 异步 + 流式调用封一层。

W5 相比 week3 多了「同步 chat()」——Multi-Query 改写需要在普通函数里调 LLM 生成查询变体，
用 AsyncOpenAI 在同步上下文里跑会有事件循环麻烦，所以单独建一个同步 OpenAI 客户端。

设计要点：
- async（achat/astream）：LLM 是 IO 等待，async 才能高并发（W1 并发实验已验证）
- stream：逐 token yield，打字机效果（W1 实验 2）
- 同步 chat()：给 W5 的 Multi-Query 改写用
"""
from openai import AsyncOpenAI, OpenAI
from config import settings

_async_client = None
_sync_client = None


def _get_async_client() -> AsyncOpenAI:
    global _async_client
    if _async_client is None:
        api_key, base_url, _ = settings.active
        _async_client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=settings.request_timeout)
    return _async_client


def _get_sync_client() -> OpenAI:
    global _sync_client
    if _sync_client is None:
        api_key, base_url, _ = settings.active
        _sync_client = OpenAI(api_key=api_key, base_url=base_url, timeout=settings.request_timeout)
    return _sync_client


def _model() -> str:
    return settings.active[2]


def chat(messages: list[dict], temperature: float = 0.7) -> tuple[str, dict]:
    """同步一次性对话：返回 (文本, usage)。Multi-Query 改写用。"""
    client = _get_sync_client()
    resp = client.chat.completions.create(model=_model(), messages=messages, temperature=temperature)
    text = resp.choices[0].message.content or ""
    usage = {
        "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
        "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
    }
    return text, usage


async def achat(messages: list[dict], temperature: float = 0.7) -> tuple[str, dict]:
    """异步一次性对话：攒完所有 token 再返回 (文本, usage)。"""
    client = _get_async_client()
    resp = await client.chat.completions.create(model=_model(), messages=messages, temperature=temperature)
    text = resp.choices[0].message.content or ""
    usage = {
        "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
        "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
    }
    return text, usage


async def astream(messages: list[dict], temperature: float = 0.7):
    """流式对话：异步生成器，每次 yield 一个 token 片段。"""
    client = _get_async_client()
    stream = await client.chat.completions.create(
        model=_model(), messages=messages, temperature=temperature, stream=True
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
