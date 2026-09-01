"""LLM 客户端（精简版）：同步 chat + chat_with_tools。

说明：异步 achat/astream 已移除——它们只用于 FastAPI 流式接口（main.py），
Streamlit Cloud 部署只跑 app.py，不需要异步。openai 新版本移除了 AsyncOpenAI 的
直接 import 路径，去掉它避免部署时 import 失败。

统一走 OpenAI 兼容协议，切换国产模型只改 base_url（见 config.Settings.active）。
"""
from openai import OpenAI

from src.core.config import settings

_sync_client = None


def _get_sync() -> OpenAI:
    global _sync_client
    if _sync_client is None:
        api_key, base_url, _ = settings.active
        _sync_client = OpenAI(api_key=api_key, base_url=base_url, timeout=settings.request_timeout)
    return _sync_client


def _model() -> str:
    return settings.active[2]


def chat(messages: list[dict], temperature: float = 0.7) -> tuple[str, dict]:
    """普通对话，返回 (文本, usage)。"""
    resp = _get_sync().chat.completions.create(model=_model(), messages=messages, temperature=temperature)
    text = resp.choices[0].message.content or ""
    usage = {
        "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
        "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
    }
    return text, usage


def chat_with_tools(messages: list[dict], tools: list[dict], temperature: float = 0.2):
    """带工具调用：返回完整 response 对象（Agent 循环用）。"""
    return _get_sync().chat.completions.create(
        model=_model(), messages=messages, tools=tools, temperature=temperature
    )