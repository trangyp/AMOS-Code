# Performance Optimization Guide

Performance tuning for AMOS Equation System v2.0.

## Database Optimization

### PostgreSQL Tuning

```sql
-- Connection pooling (PgBouncer recommended)
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 768MB
work_mem = 4MB
maintenance_work_mem = 64MB

-- Query optimization
random_page_cost = 1.1  -- For SSD storage
effective_io_concurrency = 200

-- WAL settings for write-heavy workloads
wal_buffers = 16MB
max_wal_size = 1GB
min_wal_size = 512MB
```

### Index Strategy

```sql
-- Already implemented in migrations, verify with:
SELECT schemaname, tablename, indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'equations';

-- Query to check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE tablename = 'equations'
ORDER BY idx_scan DESC;
```

### Query Optimization

```python
# Use selectinload for relationships (N+1 prevention)
from sqlalchemy.orm import selectinload

results = await session.execute(
    select(Equation)
    .options(selectinload(Equation.tags))
    .filter(Equation.status == "active")
)

# Use asyncpg for raw queries when needed
# connection.execute() with prepared statements
```

## Caching Strategy

### Redis Configuration

```python
# Cache hierarchy (already implemented)
L1: In-memory (async-lru) - 100 items
L2: Redis - 1 hour TTL
L3: Database

# Cache key patterns
equation:{id}           # Single equation
equations:list:{hash}   # Query results
health:status          # Health checks (short TTL)
```

### Cache Warming

```python
# Warm cache on startup
async def warm_cache():
    """Pre-populate cache with hot data."""
    equations = await get_popular_equations(limit=100)
    for eq in equations:
        await cache.set(f"equation:{eq.id}", eq, ttl=3600)
```

## API Performance

### Response Time Targets

| Endpoint | Target P95 | Optimization |
|----------|-----------|--------------|
| GET /health | < 50ms | In-memory cache |
| GET /equations | < 100ms | Redis cache + pagination |
| POST /equations | < 200ms | Async validation |
| GraphQL Query | < 150ms | DataLoader pattern |

### Connection Pooling

```python
# HTTP client pooling (aiohttp)
aiohttp.ClientSession(
    connector=aiohttp.TCPConnector(
        limit=100,
        limit_per_host=30,
        ttl_dns_cache=300,
        use_dns_cache=True,
    ),
    timeout=aiohttp.ClientTimeout(total=30)
)

# Database pooling (asyncpg via SQLAlchemy)
async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=1800,
)
```

## Load Balancing

### ALB Configuration

```yaml
# Target group settings
health_check:
  path: /health/ready
  interval: 30
  timeout: 5
  healthy_threshold: 2
  unhealthy_threshold: 3

# Sticky sessions (if needed)
stickiness:
  enabled: true
  duration: 3600
```

### Auto-scaling Policies

```yaml
# Scale on CPU
cpu_utilization:
  target: 70
  scale_in_cooldown: 300
  scale_out_cooldown: 60

# Scale on request count
request_count:
  target: 1000
```

## CDN & Static Assets

### CloudFront Configuration

```bash
# Cache behaviors
/health/*    - No cache (TTL 0)
/static/*   - Long cache (TTL 86400)
/api/*      - Short cache (TTL 60)
/graphql    - No cache (TTL 0)
```

### Static Asset Optimization

```bash
# Enable gzip compression
# nginx.conf
gzip on;
gzip_types application/json application/javascript text/css;
gzip_min_length 1000;
gzip_comp_level 5;
```

## Celery Optimization

### Worker Configuration

```python
# Optimal worker settings
celery worker \
  --concurrency=4 \
  --prefetch-multiplier=1 \
  --max-tasks-per-child=1000 \
  --time-limit=300 \
  --soft-time-limit=240
```

### Task Prioritization

```python
# Route tasks to queues
task_routes = {
    'equation_tasks.process_equation': {'queue': 'processing'},
    'equation_tasks.send_webhook': {'queue': 'notifications'},
    'equation_tasks.*': {'queue': 'default'},
}

# Worker specialization
celery -A equation_tasks worker -Q processing --concurrency=8
celery -A equation_tasks worker -Q notifications --concurrency=2
```

## Monitoring Performance

### Key Metrics

```promql
# API latency
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)

# Database connections
postgres_stat_activity_count{state="active"}

# Cache hit rate
redis_keyspace_hits / (redis_keyspace_hits + redis_keyspace_misses)

# Worker utilization
celery_worker_tasks_active / celery_worker_pool_capacity
```

### Performance Tests

```bash
# Load test with Locust
locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 10

# Database load test
pgbench -c 50 -j 10 -T 60 -f queries.sql

# Redis benchmark
redis-benchmark -n 100000 -c 50 -q
```

## Bottleneck Troubleshooting

### Database Bottlenecks

```sql
-- Find slow queries
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Connection usage
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
```

### Application Bottlenecks

```bash
# Profile with py-spy
py-spy top --pid $(pgrep -f "uvicorn")

# Memory profiling
python -m memory_profiler app.py
```

## Scaling Decision Tree

```
High Latency?
├── Database queries slow? → Add indexes, optimize queries
├── Cache hit rate low? → Increase cache size, warm cache
├── CPU saturated? → Scale ECS tasks
└── Memory high? → Optimize data structures

High Error Rate?
├── Database connections? → Increase pool size
├── Timeout errors? → Increase timeout, optimize code
└── Rate limiting? → Implement backoff
```

## Production Checklist

- [ ] Database indexes created
- [ ] Redis cache configured
- [ ] Connection pools sized
- [ ] Auto-scaling enabled
- [ ] CDN configured
- [ ] Compression enabled
- [ ] Monitoring alerts set
- [ ] Load tests passed
- [ ] Circuit breakers active
- [ ] Graceful shutdown implemented

---

*Target: P95 < 200ms, 99.9% availability*
