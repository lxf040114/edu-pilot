"""配置管理：pydantic-settings 从 .env 读 LLM 配置（支持国产模型 OpenAI 兼容协议）。"""
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# 定位 edu-pilot 根目录，向上找 .env（week1/.env 已填真实 key）
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for cand in [os.path.join(_ROOT, ".env"), os.path.join(_ROOT, "week1", ".env")]:
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
        p = self.llm_provider
        return {
            "deepseek": (self.deepseek_api_key, self.deepseek_base_url, self.deepseek_model),
            "qwen": (self.qwen_api_key, self.qwen_base_url, self.qwen_model),
            "glm": (self.glm_api_key, self.glm_base_url, self.glm_model),
        }.get(p, (self.deepseek_api_key, self.deepseek_base_url, self.deepseek_model))


settings = Settings()
