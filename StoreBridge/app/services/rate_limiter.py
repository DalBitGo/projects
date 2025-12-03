"""Rate limiter with atomic Redis operations using Lua script."""

import asyncio
import time
from typing import Optional

import redis.asyncio as aioredis

from app.config import settings


class NaverRateLimiter:
    """
    Rate limiter for Naver Commerce API (2 TPS limit).

    Uses Lua script for atomic GET-CHECK-INCR operation to prevent race conditions.
    Supports burst mode for temporary spikes.
    """

    # Lua script for atomic rate limit check and increment
    LUA_ACQUIRE = """
    local key = KEYS[1]
    local max_tps = tonumber(ARGV[1])
    local ttl = tonumber(ARGV[2])
    local burst_max = tonumber(ARGV[3])

    local current = redis.call('GET', key)
    if not current then
        current = 0
    else
        current = tonumber(current)
    end

    -- Check normal limit first
    if current < max_tps then
        redis.call('INCR', key)
        redis.call('EXPIRE', key, ttl)
        return 1  -- success (normal)
    -- Check burst limit
    elseif current < burst_max then
        redis.call('INCR', key)
        redis.call('EXPIRE', key, ttl)
        return 2  -- success (burst)
    else
        return 0  -- blocked
    end
    """

    def __init__(
        self,
        redis_client: Optional[aioredis.Redis] = None,
        max_tps: int = settings.naver_max_tps,
        burst_max: int = settings.naver_burst_max,
        ttl: int = 2,
    ) -> None:
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client (if None, creates new one)
            max_tps: Maximum transactions per second (default: 2)
            burst_max: Maximum burst limit (default: 3)
            ttl: Time-to-live for rate limit key in seconds (default: 2)
        """
        self.redis = redis_client or aioredis.from_url(
            settings.redis_url, decode_responses=True
        )
        self.max_tps = max_tps
        self.burst_max = burst_max
        self.ttl = ttl
        self._lua_script_sha: Optional[str] = None

    async def _ensure_lua_script(self) -> str:
        """Ensure Lua script is loaded into Redis and return SHA."""
        if self._lua_script_sha is None:
            self._lua_script_sha = await self.redis.script_load(self.LUA_ACQUIRE)
        return self._lua_script_sha

    async def acquire(self, resource_id: str = "naver_api") -> bool:
        """
        Acquire a rate limit token.

        Args:
            resource_id: Identifier for the resource (default: "naver_api")

        Returns:
            True if request is allowed, False if rate limited

        Raises:
            ConnectionError: If Redis is unavailable
            Exception: If Lua script execution fails
        """
        current_second = int(time.time())
        key = f"{resource_id}:ratelimit:{current_second}"

        try:
            # Ensure Lua script is loaded
            script_sha = await self._ensure_lua_script()

            # Execute Lua script atomically
            result = await self.redis.evalsha(
                script_sha,
                1,  # number of keys
                key,
                str(self.max_tps),
                str(self.ttl),
                str(self.burst_max),
            )

            return result > 0  # 1 or 2 = success, 0 = blocked

        except ConnectionError:
            # Re-raise ConnectionError as-is (for testing)
            raise
        except aioredis.RedisError as e:
            raise ConnectionError(f"Redis connection error: {e}") from e
        except Exception as e:
            raise Exception(f"Rate limiter error: {e}") from e

    async def acquire_with_wait(
        self, resource_id: str = "naver_api", max_retries: int = 3, backoff: float = 0.5
    ) -> bool:
        """
        Acquire a rate limit token with exponential backoff retry.

        Args:
            resource_id: Identifier for the resource
            max_retries: Maximum number of retries (default: 3)
            backoff: Initial backoff time in seconds (default: 0.5)

        Returns:
            True if acquired successfully, False if max retries exceeded
        """
        for attempt in range(max_retries):
            if await self.acquire(resource_id):
                return True

            # Exponential backoff
            wait_time = backoff * (2**attempt)
            await asyncio.sleep(wait_time)

        return False

    async def get_current_count(self, resource_id: str = "naver_api") -> int:
        """
        Get current request count for this second (for monitoring).

        Args:
            resource_id: Identifier for the resource

        Returns:
            Current request count
        """
        current_second = int(time.time())
        key = f"{resource_id}:ratelimit:{current_second}"

        try:
            count = await self.redis.get(key)
            return int(count) if count else 0
        except Exception:
            return 0

    async def reset(self, resource_id: str = "naver_api") -> None:
        """
        Reset rate limit (for testing purposes).

        Args:
            resource_id: Identifier for the resource
        """
        current_second = int(time.time())
        key = f"{resource_id}:ratelimit:{current_second}"
        await self.redis.delete(key)

    async def close(self) -> None:
        """Close Redis connection."""
        await self.redis.close()
