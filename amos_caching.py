#!/usr/bin/env python3
from __future__ import annotations

"""AMOS Caching & Performance Layer - Phase 19
================================================

Enterprise-grade caching system with Redis, multi-tenant isolation,
equation result memoization, and event-driven invalidation.

Features:
- Async Redis caching with connection pooling
- Multi-tenant cache namespaces (per workspace)
- Equation result memoization
- API response caching middleware
- Cache warming strategies
- Event-driven cache invalidation
- Cache analytics and statistics

Owner: Trang
Version: 1.0.0
Phase: 19
"""

import asyncio
import functools
import hashlib
import json
import os
import pickle
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, cast

# Redis imports
try:
    import redis.asyncio as aioredis
    from redis.asyncio import Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis not installed. Caching disabled.")

# FastAPI imports
try:
    from fastapi import Request, Response
    from fastapi.responses import JSONResponse
    from starlette.middleware.base import BaseHTTPMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Multi-tenancy imports
try:
    from amos_multitenancy import TenantContext

    MULTITENANCY_AVAILABLE = True
except ImportError:
    MULTITENANCY_AVAILABLE = False

import logging

logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_PREFIX = os.getenv("CACHE_PREFIX", "amos")
DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "300"))  # 5 minutes
EQUATION_TTL = int(os.getenv("CACHE_EQUATION_TTL", "3600"))  # 1 hour
API_TTL = int(os.getenv("CACHE_API_TTL", "60"))  # 1 minute
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

T = TypeVar("T")


# ============================================
# Enums
# ============================================


class CacheTier(str, Enum):
    """Cache storage tiers."""

    MEMORY = "memory"  # L1: In-memory, fastest
    REDIS = "redis"  # L2: Distributed, shared
    DISK = "disk"  # L3: Persistent, slowest


class CacheStrategy(str, Enum):
    """Cache invalidation strategies."""

    TTL = "ttl"  # Time-based expiration
    LRU = "lru"  # Least recently used
    LFU = "lfu"  # Least frequently used
    EVENT = "event"  # Event-driven invalidation
    WRITE_THROUGH = "wt"  # Write to cache and DB
    WRITE_BACK = "wb"  # Write to cache, async to DB


# ============================================
# Data Classes
# ============================================


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_keys: int = 0
    memory_usage: int = 0
    hit_rate: float = 0.0

    def record_hit(self) -> None:
        self.hits += 1
        self._update_hit_rate()

    def record_miss(self) -> None:
        self.misses += 1
        self._update_hit_rate()

    def _update_hit_rate(self) -> None:
        total = self.hits + self.misses
        if total > 0:
            self.hit_rate = self.hits / total


@dataclass
class CacheEntry:
    """Cache entry metadata."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = None
    tags: List[str] = field(default_factory=list)
    tenant_id: str = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


# ============================================
# Cache Manager
# ============================================


class AMOSCache:
    """
    Multi-tenant Redis cache manager with async support.
    """

    _instance: Optional[AMOSCache] = None
    _lock = asyncio.Lock()

    def __new__(cls) -> AMOSCache:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._redis: Optional[Redis] = None
        self._stats = CacheStats()
        self._local_cache: Dict[str, CacheEntry] = {}
        self._initialized = True
        self._enabled = CACHE_ENABLED

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE or not self._enabled:
            logger.info("Cache disabled or Redis not available")
            return

        try:
            self._redis = await aioredis.from_url(
                REDIS_URL, decode_responses=True, socket_keepalive=True, health_check_interval=30
            )
            logger.info(f"Cache connected to {REDIS_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._enabled = False

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _get_tenant_prefix(self, tenant_id: str = None) -> str:
        """Get cache key prefix with tenant isolation."""
        if tenant_id is None and MULTITENANCY_AVAILABLE:
            tenant_id = TenantContext.get_current_workspace_id()

        if tenant_id:
            return f"{CACHE_PREFIX}:tenant:{tenant_id}"
        return CACHE_PREFIX

    def _build_key(self, key: str, tenant_id: str = None, namespace: str = None) -> str:
        """Build namespaced cache key."""
        prefix = self._get_tenant_prefix(tenant_id)

        if namespace:
            return f"{prefix}:{namespace}:{key}"
        return f"{prefix}:{key}"

    async def get(self, key: str, tenant_id: str = None, namespace: str = None) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key
            tenant_id: Optional tenant for isolation
            namespace: Optional namespace (equation, api, session)

        Returns:
            Cached value or None if miss
        """
        if not self._enabled:
            return None

        full_key = self._build_key(key, tenant_id, namespace)

        # Try L1 (local) cache first
        if full_key in self._local_cache:
            entry = self._local_cache[full_key]
            if not entry.is_expired():
                self._stats.record_hit()
                return entry.value
            else:
                del self._local_cache[full_key]

        # Try L2 (Redis) cache
        if self._redis:
            try:
                value = await self._redis.get(full_key)
                if value is not None:
                    self._stats.record_hit()
                    # Deserialize
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return pickle.loads(value)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")

        self._stats.record_miss()
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = DEFAULT_TTL,
        tenant_id: str = None,
        namespace: str = None,
        tags: List[str] = None,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            tenant_id: Optional tenant for isolation
            namespace: Optional namespace
            tags: Tags for cache invalidation

        Returns:
            True if successful
        """
        if not self._enabled:
            return False

        full_key = self._build_key(key, tenant_id, namespace)

        # Serialize
        try:
            serialized = json.dumps(value, default=str)
        except (TypeError, ValueError):
            serialized = pickle.dumps(value)

        # Store in L1 (local) cache
        entry = CacheEntry(
            key=full_key,
            value=value,
            expires_at=datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None,
            tags=tags or [],
            tenant_id=tenant_id,
        )
        self._local_cache[full_key] = entry

        # Store in L2 (Redis) cache
        if self._redis:
            try:
                await self._redis.setex(full_key, ttl, serialized)

                # Store tags for invalidation
                if tags:
                    for tag in tags:
                        tag_key = f"{CACHE_PREFIX}:tags:{tag}"
                        await self._redis.sadd(tag_key, full_key)
                        await self._redis.expire(tag_key, ttl)

                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")

        return True

    async def delete(self, key: str, tenant_id: str = None, namespace: str = None) -> bool:
        """Delete key from cache."""
        if not self._enabled:
            return False

        full_key = self._build_key(key, tenant_id, namespace)

        # Remove from L1
        if full_key in self._local_cache:
            del self._local_cache[full_key]

        # Remove from L2
        if self._redis:
            try:
                await self._redis.delete(full_key)
                return True
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")

        return True

    async def invalidate_by_tag(self, tag: str) -> int:
        """
        Invalidate all cache entries with given tag.

        Args:
            tag: Tag to invalidate

        Returns:
            Number of keys invalidated
        """
        if not self._enabled or not self._redis:
            return 0

        try:
            tag_key = f"{CACHE_PREFIX}:tags:{tag}"
            keys = await self._redis.smembers(tag_key)

            if keys:
                # Remove from Redis
                await self._redis.delete(*keys)
                await self._redis.delete(tag_key)

                # Remove from local cache
                for key in keys:
                    if key in self._local_cache:
                        del self._local_cache[key]

                logger.info(f"Invalidated {len(keys)} keys with tag '{tag}'")
                return len(keys)
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")

        return 0

    async def clear_tenant_cache(self, tenant_id: str) -> int:
        """Clear all cache for a tenant."""
        if not self._enabled or not self._redis:
            return 0

        prefix = self._get_tenant_prefix(tenant_id)
        pattern = f"{prefix}:*"

        try:
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await self._redis.delete(*keys)

                # Clear local cache
                local_keys = [k for k in self._local_cache.keys() if k.startswith(prefix)]
                for k in local_keys:
                    del self._local_cache[k]

                logger.info(f"Cleared {len(keys)} keys for tenant {tenant_id}")
                return len(keys)
        except Exception as e:
            logger.error(f"Tenant cache clear error: {e}")

        return 0

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._stats

    @asynccontextmanager
    async def cache_context(self, tenant_id: str = None):
        """Async context manager for cache operations."""
        await self.initialize()
        try:
            yield self
        finally:
            await self.close()


# ============================================
# Decorators
# ============================================


def cached(
    ttl: int = DEFAULT_TTL,
    namespace: str = None,
    tags: List[str] = None,
    key_func: Callable[..., str] = None,
):
    """
    Decorator to cache function results.

    Args:
        ttl: Cache TTL in seconds
        namespace: Cache namespace
        tags: Tags for invalidation
        key_func: Custom key generation function
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            cache = AMOSCache()

            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Default: hash of function name and arguments
                key_parts = [func.__name__, str(args), str(sorted(kwargs.items()))]
                key = hashlib.md5("".join(key_parts).encode()).hexdigest()

            # Try cache
            cached_value = await cache.get(key, namespace=namespace)
            if cached_value is not None:
                return cast(T, cached_value)

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await cache.set(key, result, ttl=ttl, namespace=namespace, tags=tags)

            return result

        return wrapper

    return decorator


# ============================================
# Middleware
# ============================================

if FASTAPI_AVAILABLE:

    class CacheMiddleware(BaseHTTPMiddleware):
        """
        FastAPI middleware for response caching.
        """

        def __init__(self, app, ttl: int = API_TTL, exclude_paths: List[str] = None):
            super().__init__(app)
            self.ttl = ttl
            self.exclude_paths = exclude_paths or ["/health", "/metrics"]

        async def dispatch(self, request: Request, call_next) -> Response:
            # Skip excluded paths
            path = request.url.path
            if any(path.startswith(ep) for ep in self.exclude_paths):
                return await call_next(request)

            # Skip non-GET requests
            if request.method != "GET":
                return await call_next(request)

            # Check cache
            cache = AMOSCache()
            tenant_id = None
            if MULTITENANCY_AVAILABLE:
                tenant_id = TenantContext.get_current_workspace_id()

            cache_key = f"api:{path}:{hash(str(request.query_params))}"
            cached_response = await cache.get(cache_key, tenant_id=tenant_id, namespace="api")

            if cached_response:
                # Return cached response
                return JSONResponse(
                    content=cached_response.get("body"),
                    status_code=cached_response.get("status_code", 200),
                    headers={"X-Cache": "HIT"},
                )

            # Execute request
            response = await call_next(request)

            # Cache successful responses
            if response.status_code == 200 and isinstance(response, JSONResponse):
                body = response.body
                if body:
                    try:
                        content = json.loads(body)
                        await cache.set(
                            cache_key,
                            {"body": content, "status_code": response.status_code},
                            ttl=self.ttl,
                            tenant_id=tenant_id,
                            namespace="api",
                        )
                    except json.JSONDecodeError:
                        pass

            return response


# ============================================
# Equation Caching
# ============================================


class EquationCache:
    """
    Specialized cache for equation results.
    """

    def __init__(self):
        self._cache = AMOSCache()

    def _build_equation_key(self, name: str, params: dict) -> str:
        """Build cache key for equation execution."""
        # Sort params for consistent key
        param_str = json.dumps(params, sort_keys=True, default=str)
        return hashlib.md5(f"{name}:{param_str}".encode()).hexdigest()

    async def get_result(self, name: str, params: dict, tenant_id: str = None) -> Optional[Any]:
        """Get cached equation result."""
        key = self._build_equation_key(name, params)
        return await self._cache.get(key, tenant_id=tenant_id, namespace="equation")

    async def cache_result(
        self, name: str, params: dict, result: Any, ttl: int = EQUATION_TTL, tenant_id: str = None
    ) -> bool:
        """Cache equation result."""
        key = self._build_equation_key(name, params)
        return await self._cache.set(
            key,
            result,
            ttl=ttl,
            tenant_id=tenant_id,
            namespace="equation",
            tags=[f"equation:{name}"],
        )

    async def invalidate_equation(self, name: str) -> int:
        """Invalidate all cached results for an equation."""
        return await self._cache.invalidate_by_tag(f"equation:{name}")


# ============================================
# Cache Warming
# ============================================


class CacheWarmer:
    """
    Pre-populates cache with frequently accessed data.
    """

    def __init__(self):
        self._cache = AMOSCache()
        self._warmers: List[Callable[[], Awaitable[dict]]] = []

    def register_warmer(self, func: Callable[[], Awaitable[dict]]) -> None:
        """Register a cache warming function."""
        self._warmers.append(func)

    async def warm_cache(self) -> Dict[str, Any]:
        """Execute all cache warmers."""
        results = {}

        for warmer in self._warmers:
            try:
                data = await warmer()
                results.update(data)
            except Exception as e:
                logger.error(f"Cache warmer failed: {e}")

        logger.info(f"Cache warmed with {len(results)} entries")
        return results


# ============================================
# Global Instance
# ============================================


def get_cache() -> AMOSCache:
    """Get global cache instance."""
    return AMOSCache()


def get_equation_cache() -> EquationCache:
    """Get equation cache instance."""
    return EquationCache()


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("AMOS Caching & Performance - Phase 19")
    print("=" * 60)

    if not REDIS_AVAILABLE:
        print("\n⚠️  Redis not installed")
        print("   Install: pip install redis")
    else:
        print("\n✅ Redis cache configured:")
        print(f"   URL: {REDIS_URL}")
        print(f"   Default TTL: {DEFAULT_TTL}s")
        print(f"   Equation TTL: {EQUATION_TTL}s")
        print(f"   API TTL: {API_TTL}s")
        print(f"   Enabled: {CACHE_ENABLED}")

    print("\n📊 Features:")
    print("   - L1 (local) + L2 (Redis) caching")
    print("   - Multi-tenant namespace isolation")
    print("   - Tag-based invalidation")
    print("   - Equation result memoization")
    print("   - API response caching")
    print("   - Cache warming")
    print("   - Async support")

    print("\n🔧 Usage:")
    print("   # Cache decorator")
    print("   @cached(ttl=300, namespace='api')")
    print("   async def get_expensive_data(): ...")

    print("\n   # Direct cache access")
    print("   cache = get_cache()")
    print("   await cache.set('key', value, ttl=300)")
    print("   value = await cache.get('key')")

    print("\n   # Equation caching")
    print("   eq_cache = get_equation_cache()")
    print("   await eq_cache.cache_result('softmax', params, result)")

    print("\n" + "=" * 60)
    print("✅ Phase 19: Caching layer ready!")
