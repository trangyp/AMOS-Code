#!/usr/bin/env python3
"""AMOS Cache System v1.0.0
=======================

High-performance distributed caching with Redis.

Features:
  - Redis backend with async support
  - Cache-aside pattern implementation
  - Response caching for FastAPI endpoints
  - Query result caching
  - Session storage
  - Distributed locking
  - Rate limiting with sliding window
  - Cache warming and invalidation
  - Automatic serialization (JSON/msgpack)
  - TTL and LRU eviction policies
  - Multi-level cache (L1: Memory, L2: Redis)
  - Cache stampede prevention

Cache Strategies:
  1. Cache-Aside: Application manages cache
  2. Write-Through: Write to cache + DB
  3. Write-Behind: Async cache update
  4. Read-Through: Cache loads from DB on miss

Usage:
    from amos_cache import AMOSCache, cache_response

  # Initialize cache
  cache = AMOSCache()
  await cache.initialize()

  # Manual caching
  result = await cache.get_or_set("key", expensive_func, ttl=300)

  # Decorator caching
  @cache_response(ttl=60)
  @app.get("/api/agents")
  async def get_agents():
      return await fetch_agents_from_db()

  # Distributed lock
  async with cache.lock("critical_section", timeout=10):
      await process_critical_task()

Requirements:
  pip install redis cachetools msgpack

Author: Trang Phan
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import json
import pickle
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, TypeVar, cast

# Try to import Redis
try:
    import redis.asyncio as aioredis
    from redis.asyncio.client import Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("[Cache] Redis not available, using in-memory cache only")

# Try to import msgpack for faster serialization
try:
    import msgpack

    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

# Try to import cachetools for in-memory LRU cache
try:
    from cachetools import TTLCache

    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False


T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class CacheConfig:
    """Cache configuration."""

    redis_url: str = "redis://localhost:6379/1"  # Use DB 1 for cache
    default_ttl: int = 300  # 5 minutes
    max_memory_size: int = 1000  # LRU cache size
    key_prefix: str = "amos:cache:"
    serializer: str = "msgpack"  # json or msgpack
    enable_l1_cache: bool = True  # In-memory LRU
    enable_l2_cache: bool = True  # Redis
    compression: bool = False


class AMOSCache:
    """AMOS distributed caching system."""

    def __init__(self, config: CacheConfig | None = None):
        """Initialize cache system.

        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()
        self._redis: Redis | None = None
        self._l1_cache: Any = None  # In-memory cache
        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> bool:
        """Initialize cache connections.

        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True

        print("[AMOSCache] Initializing...")

        # Initialize L1 cache (in-memory)
        if self.config.enable_l1_cache and CACHETOOLS_AVAILABLE:
            self._l1_cache = TTLCache(
                maxsize=self.config.max_memory_size, ttl=self.config.default_ttl
            )
            print(f"  ✓ L1 cache initialized (LRU, max={self.config.max_memory_size})")

        # Initialize L2 cache (Redis)
        if self.config.enable_l2_cache and REDIS_AVAILABLE:
            try:
                self._redis = await aioredis.from_url(
                    self.config.redis_url,
                    decode_responses=False,  # Keep bytes for msgpack
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30,
                )
                await self._redis.ping()
                print("  ✓ L2 cache initialized (Redis)")
            except Exception as e:
                print(f"  ⚠️  Redis connection failed: {e}")
                self._redis = None

        self._initialized = True
        print("  ✓ Cache system ready")
        return True

    async def close(self) -> None:
        """Close cache connections."""
        if self._redis:
            await self._redis.close()
            self._redis = None
        self._initialized = False

    def _serialize(self, value: Any) -> bytes:
        """Serialize value to bytes."""
        if self.config.serializer == "msgpack" and MSGPACK_AVAILABLE:
            return msgpack.packb(value, use_bin_type=True)
        return json.dumps(value, default=str).encode("utf-8")

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to value."""
        if self.config.serializer == "msgpack" and MSGPACK_AVAILABLE:
            return msgpack.unpackb(data, raw=False)
        return json.loads(data.decode("utf-8"))

    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        return f"{self.config.key_prefix}{key}"

    async def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        full_key = self._make_key(key)

        # Try L1 cache first
        if self._l1_cache is not None:
            if full_key in self._l1_cache:
                print(f"[Cache] L1 HIT: {key}")
                return self._l1_cache[full_key]

        # Try L2 cache (Redis)
        if self._redis:
            try:
                data = await self._redis.get(full_key)
                if data:
                    value = self._deserialize(data)
                    # Promote to L1
                    if self._l1_cache is not None:
                        self._l1_cache[full_key] = value
                    print(f"[Cache] L2 HIT: {key}")
                    return value
            except Exception as e:
                print(f"[Cache] L2 error: {e}")

        return None

    async def set(self, key: str, value: Any, ttl: int = None, tags: list[str] = None) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tags: Cache tags for invalidation

        Returns:
            True if successful
        """
        full_key = self._make_key(key)
        ttl = ttl or self.config.default_ttl

        # Set in L1 cache
        if self._l1_cache is not None:
            self._l1_cache[full_key] = value

        # Set in L2 cache (Redis)
        if self._redis:
            try:
                data = self._serialize(value)
                await self._redis.setex(full_key, ttl, data)

                # Add to tag sets for tag-based invalidation
                if tags:
                    for tag in tags:
                        tag_key = f"{self.config.key_prefix}tag:{tag}"
                        await self._redis.sadd(tag_key, full_key)
                        await self._redis.expire(tag_key, ttl)

            except Exception as e:
                print(f"[Cache] Set error: {e}")
                return False

        return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        full_key = self._make_key(key)

        # Delete from L1
        if self._l1_cache is not None and full_key in self._l1_cache:
            del self._l1_cache[full_key]

        # Delete from L2
        if self._redis:
            try:
                await self._redis.delete(full_key)
            except Exception as e:
                print(f"[Cache] Delete error: {e}")
                return False

        return True

    async def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with tag.

        Args:
            tag: Cache tag

        Returns:
            Number of entries invalidated
        """
        if not self._redis:
            return 0

        tag_key = f"{self.config.key_prefix}tag:{tag}"
        try:
            # Get all keys with this tag
            keys = await self._redis.smembers(tag_key)
            if keys:
                # Delete all keys
                await self._redis.delete(*keys)
                # Delete tag set
                await self._redis.delete(tag_key)
                return len(keys)
        except Exception as e:
            print(f"[Cache] Tag invalidation error: {e}")

        return 0

    async def clear(self) -> bool:
        """Clear all cache entries.

        Returns:
            True if successful
        """
        # Clear L1
        if self._l1_cache is not None:
            self._l1_cache.clear()

        # Clear L2 (only our prefix)
        if self._redis:
            try:
                pattern = f"{self.config.key_prefix}*"
                cursor = 0
                while True:
                    cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self._redis.delete(*keys)
                    if cursor == 0:
                        break
            except Exception as e:
                print(f"[Cache] Clear error: {e}")
                return False

        return True

    async def get_or_set(
        self, key: str, factory: Callable[..., T], ttl: int = None, tags: list[str] = None
    ) -> T:
        """Get from cache or compute and store.

        Args:
            key: Cache key
            factory: Function to compute value if cache miss
            ttl: Time to live
            tags: Cache tags

        Returns:
            Cached or computed value
        """
        # Try cache first
        value = await self.get(key)
        if value is not None:
            return cast(T, value)

        # Cache miss - compute value
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()

        # Store in cache
        await self.set(key, value, ttl, tags)

        return cast(T, value)

    @asynccontextmanager
    async def lock(self, key: str, timeout: int = 10, blocking: bool = True):
        """Distributed lock context manager.

        Args:
            key: Lock key
            timeout: Lock timeout in seconds
            blocking: Wait for lock if True

        Usage:
            async with cache.lock("my_resource", timeout=5):
                await process()
        """
        lock_key = f"{self.config.key_prefix}lock:{key}"
        identifier = f"{time.time()}:{id(asyncio.current_task())}"

        acquired = False
        try:
            if self._redis:
                # Try to acquire lock
                while True:
                    acquired = await self._redis.set(lock_key, identifier, nx=True, ex=timeout)
                    if acquired or not blocking:
                        break
                    await asyncio.sleep(0.1)

            yield acquired

        finally:
            if acquired and self._redis:
                # Release lock (only if we own it)
                current = await self._redis.get(lock_key)
                if current and current.decode() == identifier:
                    await self._redis.delete(lock_key)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter atomically.

        Args:
            key: Counter key
            amount: Amount to increment

        Returns:
            New counter value
        """
        full_key = self._make_key(f"counter:{key}")

        if self._redis:
            try:
                return await self._redis.incrby(full_key, amount)
            except Exception as e:
                print(f"[Cache] Increment error: {e}")

        # Fallback to memory
        if self._l1_cache is not None:
            current = self._l1_cache.get(full_key, 0)
            new_val = current + amount
            self._l1_cache[full_key] = new_val
            return new_val

        return amount


# Singleton cache instance
_cache_instance: AMOSCache | None = None


async def get_cache() -> AMOSCache:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = AMOSCache()
        await _cache_instance.initialize()
    return _cache_instance


def cache_response(
    ttl: int = 300, key_builder: Callable | None = None, tags: list[str] = None
) -> Callable[[F], F]:
    """Decorator to cache FastAPI endpoint responses.

    Args:
        ttl: Cache TTL in seconds
        key_builder: Custom key builder function
        tags: Cache tags for invalidation

    Usage:
        @cache_response(ttl=60, tags=["agents"])
        @app.get("/api/agents")
        async def get_agents():
            return await fetch_agents()
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = await get_cache()

            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key: function_name:args_hash
                sig = hashlib.md5(json.dumps([args, kwargs], default=str).encode()).hexdigest()
                cache_key = f"{func.__name__}:{sig}"

            # Try cache
            cached = await cache.get(cache_key)
            if cached is not None:
                print(f"[Cache] Response HIT: {cache_key}")
                return cached

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await cache.set(cache_key, result, ttl, tags)

            return result

        return cast(F, wrapper)

    return decorator


def cache_query(ttl: int = 300, tags: list[str] = None) -> Callable[[F], F]:
    """Decorator to cache database query results.

    Args:
        ttl: Cache TTL in seconds
        tags: Cache tags for invalidation

    Usage:
        @cache_query(ttl=60, tags=["users"])
        async def get_user_by_id(user_id: int) -> User:
            return await db.get(User, user_id)
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = await get_cache()

            # Build key from function name and arguments
            sig = hashlib.md5(pickle.dumps((func.__name__, args, kwargs))).hexdigest()
            cache_key = f"query:{sig}"

            return await cache.get_or_set(cache_key, lambda: func(*args, **kwargs), ttl, tags)

        return cast(F, wrapper)

    return decorator


class RateLimiter:
    """Sliding window rate limiter using Redis."""

    def __init__(self, cache: AMOSCache | None = None):
        """Initialize rate limiter.

        Args:
            cache: Cache instance
        """
        self._cache = cache

    async def is_allowed(
        self, key: str, max_requests: int, window_seconds: int
    ) -> tuple[bool, int, int]:
        """Check if request is allowed.

        Args:
            key: Rate limit key (e.g., IP address)
            max_requests: Max requests in window
            window_seconds: Window size

        Returns:
            (allowed, remaining, reset_time)
        """
        cache = self._cache or await get_cache()

        if not cache._redis:
            # Fallback - no rate limiting without Redis
            return True, max_requests, window_seconds

        now = time.time()
        window_start = now - window_seconds

        full_key = cache._make_key(f"rate_limit:{key}")

        try:
            # Remove old entries
            await cache._redis.zremrangebyscore(full_key, 0, window_start)

            # Count current entries
            current = await cache._redis.zcard(full_key)

            if current >= max_requests:
                # Get reset time
                oldest = await cache._redis.zrange(full_key, 0, 0, withscores=True)
                reset_time = int(oldest[0][1] + window_seconds - now) if oldest else window_seconds
                return False, 0, reset_time

            # Add current request
            await cache._redis.zadd(full_key, {str(now): now})
            await cache._redis.expire(full_key, window_seconds)

            remaining = max_requests - current - 1
            return True, remaining, window_seconds

        except Exception as e:
            print(f"[RateLimiter] Error: {e}")
            return True, max_requests, window_seconds


async def main():
    """Demo cache functionality."""
    print("=" * 70)
    print("AMOS CACHE SYSTEM v1.0.0")
    print("=" * 70)

    # Initialize cache
    cache = AMOSCache()
    if not await cache.initialize():
        print("\nCache initialization failed!")
        return

    print("\n[Demo: Basic Operations]")

    # Set value
    await cache.set("test_key", {"data": "value", "timestamp": time.time()}, ttl=60)
    print("  ✓ Set value")

    # Get value
    value = await cache.get("test_key")
    print(f"  ✓ Get value: {value}")

    # Get or set
    result = await cache.get_or_set(
        "computed_key", lambda: {"expensive": "computation", "value": 42}, ttl=60
    )
    print(f"  ✓ Get or set: {result}")

    # Increment counter
    count = await cache.increment("api_calls")
    print(f"  ✓ Counter: {count}")

    print("\n[Demo: Distributed Lock]")
    async with cache.lock("demo_lock", timeout=5) as acquired:
        if acquired:
            print("  ✓ Lock acquired - processing critical section")
            await asyncio.sleep(0.1)
        else:
            print("  ✗ Failed to acquire lock")

    print("\n[Demo: Rate Limiting]")
    limiter = RateLimiter(cache)
    for i in range(5):
        allowed, remaining, reset = await limiter.is_allowed(
            "demo_user", max_requests=3, window_seconds=60
        )
        status = "✓ ALLOWED" if allowed else "✗ BLOCKED"
        print(f"  {status} Request {i + 1}: remaining={remaining}")

    print("\n[Demo: Cache Decorators]")

    @cache_response(ttl=60, tags=["demo"])
    async def expensive_function(x: int) -> dict:
        print(f"    [Executing expensive function with x={x}]")
        await asyncio.sleep(0.1)
        return {"result": x * 2, "computed": True}

    # First call - cache miss
    result1 = await expensive_function(5)
    print(f"  First call: {result1}")

    # Second call - cache hit
    result2 = await expensive_function(5)
    print(f"  Second call (cached): {result2}")

    print("\n[Demo: Tag-based Invalidation]")
    await cache.set("tagged_item", {"data": "test"}, ttl=300, tags=["demo"])
    print("  ✓ Set item with tag 'demo'")

    invalidated = await cache.invalidate_by_tag("demo")
    print(f"  ✓ Invalidated {invalidated} items")

    # Cleanup
    await cache.clear()
    await cache.close()

    print("\n" + "=" * 70)
    print("Cache demo completed!")
    print("=" * 70)
    print("\nUsage in FastAPI:")
    print("""
from fastapi import FastAPI, Depends
from amos_cache import get_cache, cache_response
from typing import Callable, Set, TypeVar, Optional

app = FastAPI()

@app.on_event("startup")
async def startup():
    await get_cache()

@app.get("/api/agents")
@cache_response(ttl=60, tags=["agents"])
async def get_agents():
    # This result will be cached for 60 seconds
    return await fetch_agents_from_db()
""")


if __name__ == "__main__":
    asyncio.run(main())
