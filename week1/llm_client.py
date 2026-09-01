"""
统一 LLM 客户端 —— W1 最核心的一个文件。

设计目标（按重要性排序）：
1. **一处切换**：把 deepseek/qwen/glm/openai 都封装成同一个接口
2. **同步 + 异步**：普通调调用 .chat()，流式输出用 .stream()
3. **错误处理**：网络超时/限流 自动重试，结构化错误
4. **可观测**：每次调用记录 token 数、延迟、错误
5. **零依赖外部**：只用 openai SDK（国产模型都兼容），不用 LangChain

为什么不用 LangChain？
- 框架抽象更新频繁，半年后代码就过期
- 面试会问"为什么这么设计"，自己写过能答
- 项目小，自己写反而清晰

【兼容性原理】
国产模型（DeepSeek/通义/智谱）都做了 OpenAI 兼容 endpoint，所以：
- client 用 openai.OpenAI(...) 初始化
- base_url 指向国产厂商的 /v1 兼容端点
- 模型名用厂商自己的（如 deepseek-chat）
- API key 用厂商自己的
其余 HTTP 协议完全一致，SDK 不感知差别。
"""

import os
import time
import logging
from dataclasses import dataclass, field
from typing import Generator, AsyncGenerator, List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion

# 加载 .env
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("llm_client")


# ====================================================================
#  配置 Provider —— 在 .env 里改 LLM_PROVIDER 就切换
# ====================================================================

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
    """从环境变量解析当前 provider 的配置"""
    provider = provider or os.getenv("LLM_PROVIDER", "deepseek")
    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown LLM_PROVIDER: {provider}. "
            f"Supported: {list(PROVIDERS.keys())}"
        )

    cfg = PROVIDERS[provider]
    api_key = os.getenv(cfg["api_key_env"])
    if not api_key:
        raise RuntimeError(
            f"环境变量 {cfg['api_key_env']} 未设置，请在 .env 里填入"
        )

    return {
        "provider": provider,
        "api_key": api_key,
        "base_url": os.getenv(cfg["base_url_env"], cfg["base_url_default"]),
        "model": os.getenv(cfg["model_env"], cfg["model_default"]),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("MAX_TOKENS", "1000")),
        "timeout": int(os.getenv("REQUEST_TIMEOUT", "30")),
    }


# ====================================================================
#  响应数据结构
# ====================================================================

@dataclass
class LLMResponse:
    """统一的 LLM 响应，所有 provider 都返回这个"""
    content: str                                # 生成的文本
    tokens_in: int = 0                          # 输入 token 数
    tokens_out: int = 0                         # 输出 token 数
    latency_ms: float = 0.0                     # 耗时（毫秒）
    model: str = ""                             # 实际用的模型
    raw: Optional[ChatCompletion] = field(default=None, repr=False)  # 原始响应


class LLMError(Exception):
    """LLM 调用失败的统一异常"""
    pass


# ====================================================================
#  LLMClient —— 整个 W1 最重要的类
# ====================================================================

class LLMClient:
    """统一 LLM 客户端。

    用法：
        client = LLMClient()
        resp = client.chat([{"role": "user", "content": "你好"}])
        print(resp.content, resp.tokens_in, resp.tokens_out, resp.latency_ms)

        # 流式
        for chunk in client.stream([{"role": "user", "content": "你好"}]):
            print(chunk, end="", flush=True)
    """

    def __init__(self, provider: Optional[str] = None, max_retries: int = 2):
        cfg = load_provider_config(provider)
        self.cfg = cfg
        self.max_retries = max_retries

        # 同步客户端
        self._sync = OpenAI(
            api_key=cfg["api_key"],
            base_url=cfg["base_url"],
            timeout=cfg["timeout"],
            max_retries=max_retries,
        )
        # 异步客户端
        self._async = AsyncOpenAI(
            api_key=cfg["api_key"],
            base_url=cfg["base_url"],
            timeout=cfg["timeout"],
            max_retries=max_retries,
        )
        log.info(
            "LLMClient ready | provider=%s model=%s base_url=%s",
            cfg["provider"], cfg["model"], cfg["base_url"]
        )

    # ------------------------------------------------------------------
    #  核心：同步对话
    # ------------------------------------------------------------------
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """发一次对话，返回完整结果。"""
        temperature = temperature if temperature is not None else self.cfg["temperature"]
        max_tokens = max_tokens or self.cfg["max_tokens"]

        t0 = time.perf_counter()
        try:
            resp: ChatCompletion = self._sync.chat.completions.create(
                model=self.cfg["model"],
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        except Exception as e:
            log.error("LLM call failed: %s", e)
            raise LLMError(f"LLM 调用失败: {e}") from e

        latency_ms = (time.perf_counter() - t0) * 1000

        choice = resp.choices[0]
        usage = resp.usage
        result = LLMResponse(
            content=choice.message.content or "",
            tokens_in=usage.prompt_tokens if usage else 0,
            tokens_out=usage.completion_tokens if usage else 0,
            latency_ms=latency_ms,
            model=resp.model,
            raw=resp,
        )

        log.info(
            "chat | tokens_in=%d tokens_out=%d latency=%.0fms model=%s",
            result.tokens_in, result.tokens_out, result.latency_ms, result.model,
        )
        return result

    # ------------------------------------------------------------------
    #  核心：流式对话（同步）
    # ------------------------------------------------------------------
    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Generator[str, None, None]:
        """流式输出，每 chunk 是一段文本（可能几个字/几十字）。"""
        temperature = temperature if temperature is not None else self.cfg["temperature"]
        max_tokens = max_tokens or self.cfg["max_tokens"]

        t0 = time.perf_counter()
        try:
            response = self._sync.chat.completions.create(
                model=self.cfg["model"],
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )
            for chunk in response:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            log.error("LLM stream failed: %s", e)
            raise LLMError(f"流式调用失败: {e}") from e
        finally:
            log.info("stream | total latency=%.0fms", (time.perf_counter() - t0) * 1000)

    # ------------------------------------------------------------------
    #  异步：批量调用时用（并行处理多个问题）
    # ------------------------------------------------------------------
    async def achat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """异步版 chat。"""
        temperature = temperature if temperature is not None else self.cfg["temperature"]
        max_tokens = max_tokens or self.cfg["max_tokens"]

        t0 = time.perf_counter()
        try:
            resp = await self._async.chat.completions.create(
                model=self.cfg["model"],
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        except Exception as e:
            raise LLMError(f"异步 LLM 调用失败: {e}") from e

        latency_ms = (time.perf_counter() - t0) * 1000
        choice = resp.choices[0]
        usage = resp.usage
        return LLMResponse(
            content=choice.message.content or "",
            tokens_in=usage.prompt_tokens if usage else 0,
            tokens_out=usage.completion_tokens if usage else 0,
            latency_ms=latency_ms,
            model=resp.model,
            raw=resp,
        )

    async def astream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """异步版流式。"""
        temperature = temperature if temperature is not None else self.cfg["temperature"]
        max_tokens = max_tokens or self.cfg["max_tokens"]

        response = await self._async.chat.completions.create(
            model=self.cfg["model"],
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content


# ====================================================================
#  单文件直接跑：做最简单的健康检查
# ====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LLM 客户端自检")
    print("=" * 60)

    try:
        client = LLMClient()
        resp = client.chat(
            [{"role": "user", "content": "说一句话证明你能正常工作，不超过 20 个字"}],
            temperature=0.0,
        )
        print(f"\n[模型回话]  {resp.content}")
        print(f"\n[用统计]")
        print(f"  模型      = {resp.model}")
        print(f"  输入 token = {resp.tokens_in}")
        print(f"  输出 token = {resp.tokens_out}")
        print(f"  延迟      = {resp.latency_ms:.0f} ms")
        print("\n✅ LLM 客户端工作正常")
    except LLMError as e:
        print(f"\n❌ 调用失败: {e}")
        print("\n排查：")
        print("  1. 是否填了 .env 里的 API key？")
        print("  2. 是否安装了依赖 (pip install -r requirements.txt)？")
        print("  3. provider 是否在支持列表里 (deepseek/qwen/glm/openai)？")
