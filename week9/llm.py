"""LLM 客户端（W7）：chat()（普通）+ chat_with_tools()（带工具）。

W7 的教学工具（出题/批改/讲概念）用 chat()；Agent 循环用 chat_with_tools()。
"""
from openai import OpenAI
from config import settings

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key, base_url, _ = settings.active
        _client = OpenAI(api_key=api_key, base_url=base_url, timeout=settings.request_timeout)
    return _client


def _model() -> str:
    return settings.active[2]


def chat(messages: list[dict], temperature: float = 0.7) -> tuple[str, dict]:
    """普通对话，返回 (文本, usage)。"""
    resp = _get_client().chat.completions.create(
        model=_model(), messages=messages, temperature=temperature
    )
    text = resp.choices[0].message.content or ""
    usage = {
        "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
        "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
    }
    return text, usage


def chat_with_tools(messages: list[dict], tools: list[dict], temperature: float = 0.2):
    """带工具调用：返回完整 response 对象（message.tool_calls 或 message.content）。"""
    return _get_client().chat.completions.create(
        model=_model(),
        messages=messages,
        tools=tools,
        temperature=temperature,
    )
