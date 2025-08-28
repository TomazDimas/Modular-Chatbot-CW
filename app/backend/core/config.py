from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    app_name: str = "SWE Coding Challenge"
    env: str = os.getenv("ENV", "local")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    cors_allow_origins: list[str] = ["*"]
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    math_llm_model: str = os.getenv("MATH_LLM_MODEL", "gpt-4o-mini")
    log_format: str = os.getenv("LOG_FORMAT", "json")
    router_mode: str = os.getenv("ROUTER_MODE", "llm")

settings = Settings()