
from typing import Optional
from redis.asyncio import Redis, from_url
from app.core.config import settings

class RedisClient:
    _client: Optional[Redis] = None

    @classmethod
    def get_client(cls) -> Redis:
        if cls._client is None:
            url = settings.REDIS_URL
            if settings.REDIS_PASSWORD and "@" not in url:
                # Inject password: redis://host:port/db -> redis://:password@host:port/db
                prefix = "redis://"
                if url.startswith(prefix):
                    rest = url[len(prefix):]
                    url = f"redis://:{settings.REDIS_PASSWORD}@{rest}"

            cls._client = from_url(
                url,
                encoding="utf-8",
                decode_responses=True
            )
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None

redis_client = RedisClient()

async def get_redis() -> Redis:
    return RedisClient.get_client()
