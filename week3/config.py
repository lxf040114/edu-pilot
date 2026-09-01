"""配置管理：用 pydantic-settings 从 .env 读 LLM 配置。

为什么用 pydantic-settings 而不是直接 os.getenv？
- 类型自动转换（str/int/bool）
- 缺省值 + 校验
- 一处定义，全局 import，不会满屏 os.getenv
- 对应 JD 的「配置管理」基本功
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# 优先用当前目录 .env；没有就向上找 week1/week2 的 .env（避免重复填 key）
for cand in [".env", "../week1/.env", "../week2/.env",
             os.path.join(os.path.dirname(__file__), "../week1/.env")]:
    if os.path.exists(cand):
        load_dotenv(cand)
        break


class Settings(BaseSettings):
    llm_provider: str = "deepseek"
    request_timeout: int = 60

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus"

    glm_api_key: str = ""
    glm_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    glm_model: str = "glm-4-flash"

    model_config = SettingsConfigDict(extra="ignore")

    @property
    def active(self) -> dict:
        """根据 llm_provider 返回当前要用的 api_key / base_url / model。"""
        p = self.llm_provider
        return {
            "deepseek": (self.deepseek_api_key, self.deepseek_base_url, self.deepseek_model),
            "qwen": (self.qwen_api_key, self.qwen_base_url, self.qwen_model),
            "glm": (self.glm_api_key, self.glm_base_url, self.glm_model),
        }.get(p, (self.deepseek_api_key, self.deepseek_base_url, self.deepseek_model))


settings = Settings()
