from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_name: str = "SWE Coding Challenge"
    env: str = os.getenv("ENV", "local")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    router_mode: str = os.getenv("ROUTER_MODE", "rule")
    cors_allow_origins: list[str] = ["*"]

settings = Settings()