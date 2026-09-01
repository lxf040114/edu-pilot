"""LLM 客户端（W6）：在 W5 基础上加「带工具的调用」。

两个能力：
- chat()：普通对话（无工具）
- chat_with_tools()：把 tools 定义传给模型，模型可返回 tool_calls（要调哪个工具 + 参数）

Agent 循环（agent.py）会反复调 chat_with_tools，直到模型不再返回 tool_calls。
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
    """带工具调用：返回完整 response 对象。

    resp.choices[0].message 可能是：
      - message.tool_calls 非空 → 模型想调工具（含 name + arguments）
      - message.content 非空   → 模型直接回答（不再调工具）
    """
    return _get_client().chat.completions.create(
        model=_model(),
        messages=messages,
        tools=tools,
        temperature=temperature,
    )
