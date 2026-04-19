# AMOS SuperBrain Cache Layer v2.0.0

## Overview

Multi-level caching with Redis and in-memory layers, cache invalidation strategies, and performance optimization for all 12 systems.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CACHE LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   L1 Memory  │  │   L2 Redis   │  │   L3 Database      │   │
│  │   (100MB)    │  │   (Shared)   │  │   (Source)         │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│         │                 │                      │              │
│         └─────────────────┴──────────────────────┘              │
│                              │                                  │
│                    ┌────────▼────────┐                         │
│                    │  Cache Manager  │                         │
│                    └─────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cache Hierarchy

| Level | Storage | Speed | Scope | Use Case |
|-------|---------|-------|-------|----------|
| **L1** | In-Memory | Fastest | Per-process | Hot data, sessions |
| **L2** | Redis | Fast | Distributed | Shared data, API responses |
| **L3** | Database | Slow | Persistent | Source of truth |

---

## Cache Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Cache-Aside** | App checks cache first, populates on miss | Read-heavy workloads |
| **Write-Through** | Write to cache and DB simultaneously | Consistency critical |
| **Write-Behind** | Write to cache async, update DB later | Write-heavy workloads |

---

## Default TTL by Data Type

| Data Type | TTL | Description |
|-----------|-----|-------------|
| `knowledge_data` | 1 hour | Knowledge base entries |
| `user_session` | 30 minutes | Session data |
| `api_response` | 5 minutes | API call results |
| `governance_decision` | 1 minute | SuperBrain decisions |
| `feature_flag` | 2 minutes | Feature toggles |
| `tenant_config` | 10 minutes | Tenant settings |
| `system_health` | 30 seconds | Health check data |
| `analytics` | 15 minutes | Analytics results |

---

## Usage

### Basic Cache Operations

```python
from backend.cache.cache_manager import cache_get, cache_set, cache_invalidate

# Set cache value
cache_set(
    key="user:123:profile",
    value={"name": "John", "role": "admin"},
    data_type="user_session",
    ttl=1800  # 30 minutes
)

# Get from cache with fetch fallback
user = cache_get(
    key="user:123:profile",
    data_type="user_session",
    fetch_func=lambda: fetch_user_from_db(123)
)

# Invalidate cache
cache_invalidate(key="user:123:profile")

# Invalidate by pattern
cache_invalidate(pattern="user:123:*")

# Invalidate by tags
cache_invalidate(tags=["user_session", "tenant:abc"])
```

### Tenant-Scoped Caching

```python
from backend.cache.cache_manager import get_tenant_cache, set_tenant_cache

# Set tenant-specific cache
set_tenant_cache(
    tenant_id="tenant-123",
    namespace="config",
    identifier="app_settings",
    value={"theme": "dark", "language": "en"},
    data_type="tenant_config"
)

# Get tenant cache
config = get_tenant_cache(
    tenant_id="tenant-123",
    namespace="config",
    identifier="app_settings"
)
```

### Cache Invalidation

```python
from backend.cache.cache_manager import (
    invalidate_tenant_cache,
    cache_manager
)

# Invalidate all tenant cache
invalidate_tenant_cache("tenant-123")

# Register invalidation callback
def on_user_cache_invalidated(key):
    print(f"Cache {key} was invalidated")

cache_manager.register_invalidation_callback(
    "user:123:profile",
    on_user_cache_invalidated
)
```

---

## Performance Statistics

```python
from backend.cache.cache_manager import get_cache_stats

stats = get_cache_stats()
print(f"L1 hits: {stats.l1_hits}")
print(f"L1 misses: {stats.l1_misses}")
print(f"L2 hits: {stats.l2_hits}")
print(f"L2 misses: {stats.l2_misses}")
print(f"Hit rate: {(stats.l1_hits + stats.l2_hits) / (stats.l1_hits + stats.l1_misses + stats.l2_hits + stats.l2_misses):.2%}")
print(f"Memory used: {stats.memory_used_bytes / 1024 / 1024:.1f}MB")
```

---

## Cache Warmup

```python
from backend.cache.cache_manager import cache_manager

# Pre-populate cache
entries = [
    ("config:feature_flags", {"feature_a": True}, "feature_flag"),
    ("config:api_endpoints", {"v1": "/api/v1"}, "general"),
]

warmed = cache_manager.warmup_cache(entries)
print(f"Warmed {warmed} cache entries")
```

---

## Integration with Other Systems

### Multi-tenancy

Cache keys automatically include tenant context:

```python
# Key generated as: hash("config:tenant:abc:app_settings")
set_tenant_cache("tenant-abc", "config", "app_settings", {...})
```

### Data Pipeline

Cache events are published to the streaming pipeline:
- `cache_set`
- `cache_invalidate`
- `cache_clear_all`

### SuperBrain Governance

Cache operations are validated via ActionGate:
- `cache_read` - Reading from cache
- `cache_write` - Writing to cache

---

## Best Practices

### 1. Use Appropriate TTL

```python
# Good - appropriate TTL for data type
cache_set(key="user_session", ..., data_type="user_session")  # 30 min TTL

# Bad - too long for volatile data
cache_set(key="api_response", ..., ttl=3600)  # Should be shorter
```

### 2. Use Cache-Aside Pattern

```python
# Good - fetch on miss
def get_user(user_id):
    return cache_get(
        key=f"user:{user_id}",
        fetch_func=lambda: db.get_user(user_id)
    )

# Bad - manual cache miss handling
user = cache_get(key=f"user:{user_id}")
if user is None:
    user = db.get_user(user_id)
    cache_set(key=f"user:{user_id}", value=user)
```

### 3. Invalidate on Data Change

```python
# Good - invalidate when updating
def update_user(user_id, data):
    db.update_user(user_id, data)
    cache_invalidate(key=f"user:{user_id}")
```

---

## Monitoring

### Key Metrics

| Metric | Target |
|--------|--------|
| L1 Hit Rate | > 80% |
| L2 Hit Rate | > 50% |
| Overall Hit Rate | > 90% |
| Memory Usage | < 100MB |
| Eviction Rate | < 1% |

---

**Maintainer:** Trang Phan  
**Last Updated:** 2026-04-16  
**Version:** 2.0.0
