from __future__ import annotations
import redis
from ..core.config import settings

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
