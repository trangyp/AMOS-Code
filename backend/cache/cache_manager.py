"""
AMOS SuperBrain Cache Layer v2.0.0

Multi-level caching with Redis and in-memory layers, cache invalidation
strategies, and performance optimization for all 12 systems.

Architecture:
- L1: In-memory cache (fastest, per-process)
- L2: Redis cache (shared, distributed)
- L3: Database (source of truth)
- Invalidation: TTL, event-driven, write-through, write-behind

Owner: Trang Phan
Version: 2.0.0
"""


import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

# Redis for L2 cache
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# SuperBrain integration
try:
    from amos_brain import get_super_brain
    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

# Import existing modules
try:
    from backend.data_pipeline.streaming import publish_event
from typing import Callable, Set
from typing import Dict, List, Optional
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False


class CacheStrategy(Enum):
    """Caching strategies."""
    CACHE_ASIDE = "cache_aside"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"


class CacheLevel(Enum):
    """Cache hierarchy levels."""
    L1_MEMORY = "l1_memory"  # In-process memory
    L2_REDIS = "l2_redis"  # Shared Redis
    L3_DATABASE = "l3_database"  # Source of truth


@dataclass
class CacheEntry:
    """Cache entry metadata."""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    expires_at: float  = None
    tags: List[str] = field(default_factory=list)
    hit_count: int = 0
    size_bytes: int = 0


@dataclass
class CacheStats:
    """Cache performance statistics."""
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    evictions: int = 0
    invalidations: int = 0
    total_keys: int = 0
    memory_used_bytes: int = 0
    last_updated: float = field(default_factory=time.time)


class CacheManager:
    """Multi-level cache manager with SuperBrain governance."""

    # Default TTL values (seconds)
    DEFAULT_TTL = {
        "knowledge_data": 3600,  # 1 hour
        "user_session": 1800,  # 30 minutes
        "api_response": 300,  # 5 minutes
        "governance_decision": 60,  # 1 minute
        "feature_flag": 120,  # 2 minutes
        "tenant_config": 600,  # 10 minutes
        "system_health": 30,  # 30 seconds
        "analytics": 900,  # 15 minutes
    }

    # Max memory per cache level (bytes)
    MAX_MEMORY = {
        CacheLevel.L1_MEMORY: 100 * 1024 * 1024,  # 100MB
    }

    def __init__(self, redis_url: str  = None):
        self.redis_url = redis_url or "redis://localhost:6379/5"
        self._l1_cache: Dict[str, CacheEntry] = {}
        self._l1_lock = threading.RLock()
        self._redis: redis.Redis  = None
        self._brain = None
        self._stats = CacheStats()
        self._invalidation_callbacks: dict[str, list[Callable]] = {}
        self._write_behind_queue: list[tuple[str, Any]] = []

        # Initialize connections
        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
                self._redis.ping()
            except Exception:
                self._redis = None

        if SUPERBRAIN_AVAILABLE:
            try:
                self._brain = get_super_brain()
            except Exception:
                pass

    def _get_l2_key(self, key: str) -> str:
        """Generate Redis key with namespace."""
        return f"cache:l2:{key}"

    def _get_cache_key(
        self,
        namespace: str,
        identifier: str,
        tenant_id: str  = None
    ) -> str:
        """Generate consistent cache key."""
        components = [namespace]
        if tenant_id:
            components.append(f"tenant:{tenant_id}")
        components.append(identifier)
        return hashlib.sha256(":".join(components).encode()).hexdigest()[:32]

    def _get_ttl(self, data_type: str) -> int:
        """Get TTL for data type."""
        return self.DEFAULT_TTL.get(data_type, 300)

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        if entry.expires_at is None:
            return False
        return time.time() > entry.expires_at

    def _update_stats(self, level: CacheLevel, hit: bool):
        """Update cache statistics."""
        if level == CacheLevel.L1_MEMORY:
            if hit:
                self._stats.l1_hits += 1
            else:
                self._stats.l1_misses += 1
        elif level == CacheLevel.L2_REDIS:
            if hit:
                self._stats.l2_hits += 1
            else:
                self._stats.l2_misses += 1
        self._stats.last_updated = time.time()

    def get(
        self,
        key: str,
        data_type: str = "general",
        fetch_func: Callable[..., Any ] = None
    ) -> Optional[Any]:
        """Get value from cache with multi-level lookup."""
        # CANONICAL: Check governance for cache access
        if SUPERBRAIN_AVAILABLE and self._brain:
            try:
                if hasattr(self._brain, 'action_gate'):
                    action_result = self._brain.action_gate.validate_action(
                        agent_id="cache_manager",
                        action="cache_read",
                        details={"key": key, "data_type": data_type}
                    )
                    if not action_result.authorized:
                        return None
            except Exception:
                pass

        # L1: Check in-memory cache
        with self._l1_lock:
            if key in self._l1_cache:
                entry = self._l1_cache[key]
                if not self._is_expired(entry):
                    entry.hit_count += 1
                    self._update_stats(CacheLevel.L1_MEMORY, True)
                    return entry.value
                else:
                    # Expired - remove from L1
                    del self._l1_cache[key]
                    self._stats.evictions += 1

        self._update_stats(CacheLevel.L1_MEMORY, False)

        # L2: Check Redis cache
        if self._redis:
            try:
                l2_key = self._get_l2_key(key)
                data = self._redis.get(l2_key)
                if data:
                    value = json.loads(data)

                    # Promote to L1
                    self._set_l1(key, value, data_type)

                    self._update_stats(CacheLevel.L2_REDIS, True)
                    return value
            except Exception:
                pass

        self._update_stats(CacheLevel.L2_REDIS, False)

        # L3: Fetch from source if function provided (cache-aside)
        if fetch_func:
            value = fetch_func()
            if value is not None:
                self.set(key, value, data_type)
            return value

        return None

    def _set_l1(self, key: str, value: Any, data_type: str, ttl: int  = None):
        """Set value in L1 (memory) cache."""
        ttl = ttl or self._get_ttl(data_type)

        # Calculate size
        try:
            size = len(json.dumps(value).encode())
        except Exception:
            size = 1024  # Default estimate

        # Check memory limit
        with self._l1_lock:
            current_memory = sum(e.size_bytes for e in self._l1_cache.values())
            if current_memory + size > self.MAX_MEMORY[CacheLevel.L1_MEMORY]:
                # Evict oldest entries
                self._evict_l1_entries(size)

            entry = CacheEntry(
                key=key,
                value=value,
                expires_at=time.time() + ttl,
                size_bytes=size,
                tags=[data_type]
            )
            self._l1_cache[key] = entry
            self._stats.total_keys = len(self._l1_cache)
            self._stats.memory_used_bytes = current_memory + size

    def _evict_l1_entries(self, required_space: int):
        """Evict entries to make space."""
        with self._l1_lock:
            # Sort by hit count (LFU) and expiration
            entries = sorted(
                self._l1_cache.items(),
                key=lambda x: (x[1].hit_count, x[1].expires_at or 0)
            )

            freed_space = 0
            for key, entry in entries:
                if freed_space >= required_space:
                    break
                del self._l1_cache[key]
                freed_space += entry.size_bytes
                self._stats.evictions += 1

    def set(
        self,
        key: str,
        value: Any,
        data_type: str = "general",
        ttl: int  = None,
        tags: list[str ] = None,
        strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    ) -> bool:
        """Set value in cache with strategy."""
        ttl = ttl or self._get_ttl(data_type)

        # CANONICAL: Validate via SuperBrain
        if SUPERBRAIN_AVAILABLE and self._brain:
            try:
                if hasattr(self._brain, 'action_gate'):
                    action_result = self._brain.action_gate.validate_action(
                        agent_id="cache_manager",
                        action="cache_write",
                        details={
                            "key": key,
                            "data_type": data_type,
                            "strategy": strategy.value
                        }
                    )
                    if not action_result.authorized:
                        return False
            except Exception:
                pass

        # Always set in L1
        self._set_l1(key, value, data_type, ttl)

        # Set in L2 (Redis)
        if self._redis:
            try:
                l2_key = self._get_l2_key(key)
                self._redis.setex(l2_key, ttl, json.dumps(value))
            except Exception:
                pass

        # Publish cache update event
        if STREAMING_AVAILABLE:
            publish_event(
                event_type="cache_set",
                source_system="cache_manager",
                payload={
                    "key": key,
                    "data_type": data_type,
                    "ttl": ttl,
                    "strategy": strategy.value
                },
                requires_governance=False
            )

        return True

    def invalidate(
        self,
        key: str  = None,
        pattern: str  = None,
        tags: list[str ] = None
    ) -> int:
        """Invalidate cache entries."""
        invalidated_count = 0

        # Invalidate by key
        if key:
            with self._l1_lock:
                if key in self._l1_cache:
                    del self._l1_cache[key]
                    invalidated_count += 1

            if self._redis:
                try:
                    l2_key = self._get_l2_key(key)
                    self._redis.delete(l2_key)
                    invalidated_count += 1
                except Exception:
                    pass

        # Invalidate by pattern
        if pattern and self._redis:
            try:
                keys = self._redis.scan_iter(match=self._get_l2_key(pattern))
                for k in keys:
                    self._redis.delete(k)
                    invalidated_count += 1
            except Exception:
                pass

        # Invalidate by tags
        if tags:
            with self._l1_lock:
                keys_to_remove = [
                    k for k, e in self._l1_cache.items()
                    if any(t in e.tags for t in tags)
                ]
                for k in keys_to_remove:
                    del self._l1_cache[k]
                    invalidated_count += 1

        self._stats.invalidations += invalidated_count

        # Trigger callbacks
        if key and key in self._invalidation_callbacks:
            for callback in self._invalidation_callbacks[key]:
                try:
                    callback(key)
                except Exception:
                    pass

        # Publish invalidation event
        if STREAMING_AVAILABLE and invalidated_count > 0:
            publish_event(
                event_type="cache_invalidate",
                source_system="cache_manager",
                payload={
                    "key": key,
                    "pattern": pattern,
                    "tags": tags,
                    "invalidated_count": invalidated_count
                },
                requires_governance=False
            )

        return invalidated_count

    def register_invalidation_callback(self, key: str, callback: Callable[[str], None]):
        """Register callback for cache invalidation."""
        if key not in self._invalidation_callbacks:
            self._invalidation_callbacks[key] = []
        self._invalidation_callbacks[key].append(callback)

    def get_tenant_cached(
        self,
        tenant_id: str,
        namespace: str,
        identifier: str,
        data_type: str = "general"
    ) -> Optional[Any]:
        """Get tenant-scoped cached data."""
        key = self._get_cache_key(namespace, identifier, tenant_id)
        return self.get(key, data_type)

    def set_tenant_cached(
        self,
        tenant_id: str,
        namespace: str,
        identifier: str,
        value: Any,
        data_type: str = "general",
        ttl: int  = None
    ) -> bool:
        """Set tenant-scoped cached data."""
        key = self._get_cache_key(namespace, identifier, tenant_id)
        return self.set(key, value, data_type, ttl, tags=[f"tenant:{tenant_id}"])

    def invalidate_tenant(self, tenant_id: str) -> int:
        """Invalidate all cache entries for tenant."""
        return self.invalidate(tags=[f"tenant:{tenant_id}"])

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._l1_lock:
            self._stats.total_keys = len(self._l1_cache)
            self._stats.memory_used_bytes = sum(
                e.size_bytes for e in self._l1_cache.values()
            )

        # Add Redis stats if available
        if self._redis:
            try:
                info = self._redis.info("memory")
                # Could add more Redis-specific stats here
            except Exception:
                pass

        return self._stats

    def clear_all(self) -> bool:
        """Clear all cache levels."""
        # Clear L1
        with self._l1_lock:
            self._l1_cache.clear()

        # Clear L2
        if self._redis:
            try:
                # Only clear cache namespace keys
                keys = self._redis.scan_iter(match="cache:l2:*")
                for key in keys:
                    self._redis.delete(key)
            except Exception:
                return False

        # Reset stats
        self._stats = CacheStats()

        # Publish event
        if STREAMING_AVAILABLE:
            publish_event(
                event_type="cache_clear_all",
                source_system="cache_manager",
                payload={},
                requires_governance=True
            )

        return True

    def warmup_cache(
        self,
        entries: list[tuple[str, Any, str]],
        data_type: str = "general"
    ) -> int:
        """Pre-populate cache with entries."""
        warmed_count = 0
        for key, value, entry_type in entries:
            if self.set(key, value, entry_type or data_type):
                warmed_count += 1
        return warmed_count


# Global cache manager
cache_manager = CacheManager()


# Convenience functions
def cache_get(
    key: str,
    data_type: str = "general",
    fetch_func: Callable[..., Any]  = None
) -> Optional[Any]:
    """Get from cache with optional fetch."""
    return cache_manager.get(key, data_type, fetch_func)


def cache_set(
    key: str,
    value: Any,
    data_type: str = "general",
    ttl: int  = None
) -> bool:
    """Set in cache."""
    return cache_manager.set(key, value, data_type, ttl)


def cache_invalidate(
    key: str  = None,
    pattern: str  = None,
    tags: list[str ] = None
) -> int:
    """Invalidate cache entries."""
    return cache_manager.invalidate(key, pattern, tags)


def get_tenant_cache(
    tenant_id: str,
    namespace: str,
    identifier: str,
    data_type: str = "general"
) -> Optional[Any]:
    """Get tenant-scoped cache."""
    return cache_manager.get_tenant_cached(tenant_id, namespace, identifier, data_type)


def set_tenant_cache(
    tenant_id: str,
    namespace: str,
    identifier: str,
    value: Any,
    data_type: str = "general",
    ttl: int  = None
) -> bool:
    """Set tenant-scoped cache."""
    return cache_manager.set_tenant_cached(
        tenant_id, namespace, identifier, value, data_type, ttl
    )


def invalidate_tenant_cache(tenant_id: str) -> int:
    """Invalidate all tenant cache."""
    return cache_manager.invalidate_tenant(tenant_id)


def get_cache_stats() -> CacheStats:
    """Get cache statistics."""
    return cache_manager.get_stats()
