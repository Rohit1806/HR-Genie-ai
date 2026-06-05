import redis.asyncio as aioredis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MockRedis:
    """Mock Redis client to bypass connection issues in local development."""
    def __init__(self):
        self._data = {}

    async def get(self, key):
        return self._data.get(key)

    async def set(self, name, value, ex=None, px=None, nx=False, xx=False, keepttl=False):
        self._data[name] = str(value)
        return True

    async def delete(self, *names):
        count = 0
        for name in names:
            if name in self._data:
                del self._data[name]
                count += 1
        return count

    async def incr(self, name, amount=1):
        val = int(self._data.get(name, 0)) + amount
        self._data[name] = str(val)
        return val

    async def expire(self, name, time, option=None):
        return True

    async def close(self):
        pass

    async def ping(self):
        return True

redis_client = None


async def get_redis():
    """Get Redis client instance."""
    return redis_client


async def init_redis():
    """Initialize Redis connection on startup.

    If Redis is unavailable the app will still start — features that
    depend on Redis (rate-limiting, token blacklist, Celery) will be
    degraded but the core API remains functional for development.
    """
    global redis_client
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning(
            f"Redis connection failed: {e}. "
            "App will continue with a mock Redis client — rate-limiting and token blacklisting will run in-memory."
        )
        redis_client = MockRedis()


async def close_redis():
    """Close Redis connection on shutdown."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")
