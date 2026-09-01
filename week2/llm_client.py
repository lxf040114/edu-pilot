"""
week2 增强版 LLM 客户端。

相比 week1 的 llm_client.py：
1. 加 Function Calling 支持：chat_with_tools / astream_with_tools
2. 加 .env 查找 fallback（优先 cwd，否则向上找 week1/.env 和根 .env）
   —— 这样你不用在 week2 再填一遍 key

其余（sync/async/stream/sync）和 week1 完全一致。
W6 做 Agent 时，会在这个基础上加"工具执行 + 循环"逻辑。
"""

import os
import time
import json
import logging
from dataclasses import dataclass, field
from typing import Generator, AsyncGenerator, List, Dict, Optional
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage

# ----- .env fallback：向上找 key，避免每个 week 重复填 -----
def _load_env():
    load_dotenv()  # 先找 cwd 的 .env
    here = Path(__file__).resolve().parent
    candidates = [
        here / ".env",
        here.parent / "week1" / ".env",
        here.parent / ".env",
    ]
    for c in candidates:
        if c.exists():
            load_dotenv(c)
            break

_load_env()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("llm_client_w2")


PROVIDERS = {
    "deepseek": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url_env": "DEEPSEEK_BASE_URL",
        "base_url_default": "https://api.deepseek.com/v1",
        "model_env": "DEEPSEEK_MODEL",
        "model_default": "deepseek-chat",
    },
    "qwen": {
        "api_key_env": "QWEN_API_KEY",
        "base_url_env": "QWEN_BASE_URL",
        "base_url_default": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model_env": "QWEN_MODEL",
        "model_default": "qwen-turbo",
    },
    "glm": {
        "api_key_env": "GLM_API_KEY",
        "base_url_env": "GLM_BASE_URL",
        "base_url_default": "https://open.bigmodel.cn/api/paas/v4",
        "model_env": "GLM_MODEL",
        "model_default": "glm-4-flash",
    },
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_BASE_URL",
        "base_url_default": "https://api.openai.com/v1",
        "model_env": "OPENAI_MODEL",
        "model_default": "gpt-4o-mini",
    },
}


def load_provider_config(provider: Optional[str] = None):
    provider = provider or os.getenv("LLM_PROVIDER", "deepseek")
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Supported: {list(PROVIDERS.keys())}")
    cfg = PROVIDERS[provider]
    api_key = os.getenv(cfg["api_key_env"])
    if not api_key:
        raise RuntimeError(f"环境变量 {cfg['api_key_env']} 未设置，请在 .env 里填入")
    return {
        "provider": provider,
        "api_key": api_key,
        "base_url": os.getenv(cfg["base_url_env"], cfg["base_url_default"]),
        "model": os.getenv(cfg["model_env"], cfg["model_default"]),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("MAX_TOKENS", "1000")),
        "timeout": int(os.getenv("REQUEST_TIMEOUT", "30")),
    }


@dataclass
class LLMResponse:
    content: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    model: str = ""
    tool_calls: List[Dict] = field(default_factory=list)  # Function Calling 结果
    raw: Optional[ChatCompletion] = field(default=None, repr=False)


class LLMError(Exception):
    pass


class LLMClient:
    def __init__(self, provider: Optional[str] = None, max_retries: int = 2):
        cfg = load_provider_config(provider)
        self.cfg = cfg
        self.max_retries = max_retries
        self._sync = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"],
                             timeout=cfg["timeout"], max_retries=max_retries)
        self._async = AsyncOpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"],
                                   timeout=cfg["timeout"], max_retries=max_retries)
        log.info("LLMClient ready | provider=%s model=%s", cfg["provider"], cfg["model"])

    # ---------- 基础对话（同 week1） ----------
    def chat(self, messages, temperature=None, max_tokens=None, **kwargs) -> LLMResponse:
        temperature = temperature if temperature is not None else self.cfg["temperature"]
        max_tokens = max_tokens or self.cfg["max_tokens"]
        t0 = time.perf_counter()
        try:
            resp = self._sync.chat.completions.create(
                model=self.cfg["model"], messages=messages,
                temperature=temperature, max_tokens=max_tokens, **kwargs)
        except Exception as e:
            raise LLMError(f"LLM 调用失败: {e}") from e
        latency_ms = (time.perf_counter() - t0) * 1000
        choice = resp.choices[0]
        usage = resp.usage
        return LLMResponse(
            content=choice.message.content or "",
            tokens_in=usage.prompt_tokens if usage else 0,
            tokens_out=usage.completion_tokens if usage else 0,
            latency_ms=latency_ms, model=resp.model, raw=resp)

    def stream(self, messages, temperature=None, max_tokens=None, **kwargs) -> Generator[str, None, None]:
        temperature = temperature if temperature is not None else self.cfg["temperature"]
        max_tokens = max_tokens or self.cfg["max_tokens"]
        try:
            response = self._sync.chat.completions.create(
                model=self.cfg["model"], messages=messages,
                temperature=temperature, max_tokens=max_tokens, stream=True, **kwargs)
            for chunk in response:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            raise LLMError(f"流式调用失败: {e}") from e

    # ---------- Function Calling（W2 新增） ----------
    def chat_with_tools(self, messages, tools, temperature=None, max_tokens=None,
                         tool_choice="auto", **kwargs) -> LLMResponse:
        """
        让模型决定是否调用工具。

        返回：
        - resp.tool_calls 为空 → 模型直接回答了（没调工具）
        - resp.tool_calls 非空 → 模型想调工具，代码负责执行并把结果塞回 messages 再调一次

        注意：这里只封装"协议层"，不负责执行工具。
        工具执行逻辑在 W6 的 Agent 里（见 demo_function_calling.py 的最小示例）。
        """
        temperature = temperature if temperature is not None else self.cfg["temperature"]
        max_tokens = max_tokens or self.cfg["max_tokens"]
        t0 = time.perf_counter()
        try:
            resp = self._sync.chat.completions.create(
                model=self.cfg["model"], messages=messages, tools=tools,
                tool_choice=tool_choice, temperature=temperature, max_tokens=max_tokens, **kwargs)
        except Exception as e:
            raise LLMError(f"Function Calling 失败: {e}") from e

        latency_ms = (time.perf_counter() - t0) * 1000
        choice = resp.choices[0]
        msg = choice.message
        usage = resp.usage

        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,  # JSON 字符串
                })

        return LLMResponse(
            content=msg.content or "",
            tokens_in=usage.prompt_tokens if usage else 0,
            tokens_out=usage.completion_tokens if usage else 0,
            latency_ms=latency_ms, model=resp.model, tool_calls=tool_calls, raw=resp)


if __name__ == "__main__":
    try:
        c = LLMClient()
        r = c.chat([{"role": "user", "content": "用一句中文证明你正常"}])
        print("✅", r.content, f"({r.latency_ms:.0f}ms)")
    except LLMError as e:
        print("❌", e)
