from __future__ import annotations
import redis
from ..core.config import settings

redis_client = redis.Redis.from_url(
    settings.redis_url,
    socket_timeout=5,
    socket_connect_timeout=3,
    health_check_interval=30,
)
