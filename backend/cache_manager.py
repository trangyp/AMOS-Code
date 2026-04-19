"""AMOS Cache Manager with Redis.

Provides high-performance caching layer for API responses,
database queries, and expensive computations.

Features:
- Redis-backed caching with async support
- Response caching middleware
- Cache invalidation strategies
- TTL-based expiration

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations


import hashlib
import json
import os
from collections.abc import Callable
from functools import wraps
from typing import Any

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes


class CacheManager:
    """Redis-backed cache manager for AMOS."""

    def __init__(self):
        self._redis = None
        self._enabled = CACHE_ENABLED
        self._default_ttl = DEFAULT_TTL

    async def _get_redis(self):
        """Get or create Redis connection."""
        if self._redis is None:
            try:
                import redis.asyncio as redis

                self._redis = redis.from_url(REDIS_URL, decode_responses=True)
            except ImportError:
                # Fallback to mock cache if Redis not available
                self._redis = MockCache()
        return self._redis

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if not self._enabled:
            return None

        try:
            redis = await self._get_redis()
            value = await redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL."""
        if not self._enabled:
            return False

        try:
            redis = await self._get_redis()
            ttl = ttl or self._default_ttl
            await redis.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._enabled:
            return False

        try:
            redis = await self._get_redis()
            await redis.delete(key)
            return True
        except Exception:
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self._enabled:
            return 0

        try:
            redis = await self._get_redis()
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
            return len(keys)
        except Exception:
            return 0

    async def health_check(self) -> dict:
        """Check cache health."""
        try:
            redis = await self._get_redis()
            await redis.ping()
            return {"status": "healthy", "type": "redis"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class MockCache:
    """In-memory mock cache for development/testing."""

    def __init__(self):
        self._data = {}

    async def get(self, key: str) -> str:
        import time

        if key in self._data:
            value, expiry = self._data[key]
            if expiry > time.time():
                return value
            del self._data[key]
        return None

    async def setex(self, key: str, ttl: int, value: str) -> None:
        import time

        self._data[key] = (value, time.time() + ttl)

    async def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                count += 1
        return count

    async def keys(self, pattern: str) -> list:
        import fnmatch

        return [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)]

    async def ping(self) -> bool:
        return True


# Global cache manager instance
cache_manager = CacheManager()


def generate_cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = None, key_prefix: str = ""):
    """Decorator to cache function results."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{generate_cache_key(args, kwargs)}"

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache keys matching pattern."""

    async def _invalidate():
        return await cache_manager.clear_pattern(pattern)

    return _invalidate
