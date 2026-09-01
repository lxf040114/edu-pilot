"""LLM 客户端（W8）：同步 + 异步 + 流式 + 带工具，四种能力齐全。

- chat()：同步普通对话
- chat_with_tools()：同步带工具（Agent 循环用）
- achat()：异步普通对话
- astream()：异步流式（SSE 接口用）
"""
from openai import OpenAI, AsyncOpenAI
from config import settings

_sync_client = None
_async_client = None


def _get_sync() -> OpenAI:
    global _sync_client
    if _sync_client is None:
        api_key, base_url, _ = settings.active
        _sync_client = OpenAI(api_key=api_key, base_url=base_url, timeout=settings.request_timeout)
    return _sync_client


def _get_async() -> AsyncOpenAI:
    global _async_client
    if _async_client is None:
        api_key, base_url, _ = settings.active
        _async_client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=settings.request_timeout)
    return _async_client


def _model() -> str:
    return settings.active[2]


def chat(messages: list[dict], temperature: float = 0.7) -> tuple[str, dict]:
    resp = _get_sync().chat.completions.create(model=_model(), messages=messages, temperature=temperature)
    text = resp.choices[0].message.content or ""
    usage = {
        "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
        "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
    }
    return text, usage


def chat_with_tools(messages: list[dict], tools: list[dict], temperature: float = 0.2):
    return _get_sync().chat.completions.create(
        model=_model(), messages=messages, tools=tools, temperature=temperature
    )


async def achat(messages: list[dict], temperature: float = 0.7) -> tuple[str, dict]:
    resp = await _get_async().chat.completions.create(model=_model(), messages=messages, temperature=temperature)
    text = resp.choices[0].message.content or ""
    usage = {
        "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
        "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
    }
    return text, usage


async def astream(messages: list[dict], temperature: float = 0.7):
    stream = await _get_async().chat.completions.create(
        model=_model(), messages=messages, temperature=temperature, stream=True
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
