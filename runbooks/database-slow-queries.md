# Runbook: Database Slow Queries

**Alert**: `DatabaseSlowQueries` / `DatabaseVerySlowQueries`  
**Severity**: Warning / Critical  
**Threshold**: p95 > 500ms / p99 > 1000ms  
**Runbook Owner**: Database Team  
**Last Updated**: 2024-01-15

## Summary

Slow database queries can cascade into API latency issues, connection pool exhaustion, and service degradation. This runbook covers diagnosis and resolution of query performance problems.

## Initial Assessment (First 3 minutes)

### 1. Check Query Performance Metrics
```bash
# Current p95 query time
kubectl exec -it prometheus-pod -- \
  promql 'histogram_quantile(0.95, sum(rate(database_query_duration_seconds_bucket[5m])) by (le))'

# Queries by operation type
kubectl exec -it prometheus-pod -- \
  promql 'sum by (operation) (rate(database_queries_total[5m]))'
```

### 2. Identify Slow Queries in Database
```sql
-- Top 10 slowest queries by average time
SELECT 
    query,
    mean_exec_time,
    calls,
    total_exec_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Queries with high total time (impact)
SELECT 
    query,
    total_exec_time,
    calls,
    mean_exec_time
FROM pg_stat_statements 
ORDER BY total_exec_time DESC 
LIMIT 10;
```

### 3. Check Connection Pool Status
```bash
# Active connections
kubectl exec -it postgres-pod -- psql -c "
    SELECT state, count(*) 
    FROM pg_stat_activity 
    WHERE datname = 'amosequation'
    GROUP BY state;
"

# Connection wait events
kubectl exec -it postgres-pod -- psql -c "
    SELECT wait_event_type, wait_event, count(*)
    FROM pg_stat_activity
    WHERE state = 'active' AND wait_event IS NOT NULL
    GROUP BY 1, 2
    ORDER BY 3 DESC;
"
```

## Common Causes & Solutions

### Cause 1: Missing or Unused Indexes (45% of cases)

**Symptoms**:
- Sequential scans on large tables
- High query execution time

**Diagnosis**:
```sql
-- Find missing indexes
SELECT 
    schemaname,
    tablename,
    attname as column,
    n_tup_read,
    n_tup_fetch,
    seq_scan,
    seq_tup_read,
    idx_scan
FROM pg_stats
JOIN pg_stat_user_tables ON pg_stats.tablename = pg_stat_user_tables.relname
WHERE schemaname = 'public'
    AND seq_scan > 100
    AND idx_scan IS NULL
ORDER BY seq_tup_read DESC;

-- Check index usage
SELECT 
    schemaname,
    relname as table,
    indexrelname as index,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

**Resolution**:
```sql
-- Create index for frequent filter (example)
CREATE INDEX CONCURRENTLY idx_equations_type 
ON equations(equation_type) 
WHERE deleted_at IS NULL;

-- Create composite index for common queries
CREATE INDEX CONCURRENTLY idx_equations_user_created 
ON equations(user_id, created_at DESC);
```

**Note**: Use `CREATE INDEX CONCURRENTLY` to avoid table locks.

### Cause 2: Lock Contention (25% of cases)

**Symptoms**:
- Queries waiting on locks
- "Lock wait timeout" errors

**Diagnosis**:
```sql
-- Find blocking queries
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    blocked_activity.application_name AS blocked_application,
    blocking_activity.application_name AS blocking_application,
    now() - blocked_activity.query_start AS blocked_duration
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity 
    ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.relation = blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity 
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted
ORDER BY blocked_duration DESC;
```

**Immediate Mitigation**:
```sql
-- Terminate blocking query (use with caution)
SELECT pg_terminate_blocking_pids(blocked_pid);

-- Or terminate specific PID
SELECT pg_terminate_backend(blocking_pid);
```

**Resolution**:
- Review application transaction boundaries
- Reduce transaction duration
- Use row-level locking instead of table locks
- Consider using `SKIP LOCKED` for queue-like operations

### Cause 3: Inefficient Queries (20% of cases)

**Symptoms**:
- N+1 query patterns
- Full table scans
- Unnecessary joins

**Diagnosis**:
```sql
-- Find queries with high row counts
SELECT 
    query,
    calls,
    mean_exec_time,
    rows / calls as rows_per_call
FROM pg_stat_statements 
WHERE rows / calls > 1000
ORDER BY mean_exec_time DESC;

-- Check for queries without WHERE clauses
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
WHERE query LIKE '%SELECT *%'
    AND NOT query LIKE '%WHERE%'
ORDER BY calls DESC;
```

**Resolution**:
- Add pagination to large result sets
- Optimize ORM queries (e.g., use `select_related`, `prefetch_related`)
- Add appropriate WHERE clauses
- Use query result caching

### Cause 4: VACUUM/ANALYZE Issues (10% of cases)

**Symptoms**:
- Table bloat
- Stale statistics
- Degraded query plans

**Diagnosis**:
```sql
-- Check table bloat
SELECT 
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    round(n_dead_tup::numeric/nullif(n_live_tup,0)*100, 2) as dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;

-- Check last vacuum/analyze
SELECT 
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE last_vacuum IS NULL AND last_autovacuum < now() - interval '1 day'
ORDER BY last_autovacuum NULLS FIRST;
```

**Resolution**:
```sql
-- Manual vacuum (for urgent cases)
VACUUM ANALYZE equations;

-- For large tables
VACUUM (VERBOSE, ANALYZE) equations;

-- Check autovacuum settings
SHOW autovacuum;
SHOW autovacuum_max_workers;
```

## Investigation Commands

### Query Plan Analysis
```sql
-- Get execution plan for slow query
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM equations 
WHERE equation_type = 'physics' 
ORDER BY created_at DESC 
LIMIT 100;

-- Check for seq scans
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT * FROM equations WHERE user_id = 12345;
```

### Connection Analysis
```sql
-- Top connections by duration
SELECT 
    pid,
    usename,
    application_name,
    state,
    now() - query_start as duration,
    LEFT(query, 100) as query_snippet
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC
LIMIT 20;

-- Connection count by state
SELECT state, count(*)
FROM pg_stat_activity
WHERE datname = 'amosequation'
GROUP BY state;
```

### Table Statistics
```sql
-- Table sizes
SELECT 
    schemaname,
    relname,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;
```

## Immediate Mitigation

If queries are severely impacting service:

### 1. Kill Long-Running Queries
```sql
-- Identify and terminate
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'active' 
    AND now() - query_start > interval '5 minutes'
    AND query NOT LIKE '%pg_stat%'
    AND pid != pg_backend_pid();
```

### 2. Enable Statement Timeout (Temporary)
```sql
-- Set statement timeout for new connections
ALTER SYSTEM SET statement_timeout = '30s';
SELECT pg_reload_conf();
```

### 3. Scale Read Replicas (if configured)
```bash
# Redirect read traffic to replicas
kubectl patch configmap amos-config --patch '{"data":{"DB_READ_REPLICA_URL":"postgresql://..."}}'
kubectl rollout restart deployment/amos-equation-api
```

## Escalation Criteria

- [ ] Query time > 5 seconds and increasing
- [ ] Connection pool saturated (>80%)
- [ ] Database CPU > 90%
- [ ] Lock contention affecting >10% of queries
- [ ] Query performance degraded after migration

## Prevention

### 1. Query Monitoring
- Enable `pg_stat_statements` (already configured)
- Set up slow query log ( > 1 second)
- Monitor query performance trends in Grafana

### 2. Index Management
- Review and create indexes monthly
- Remove unused indexes
- Monitor index bloat

### 3. Regular Maintenance
```bash
# Weekly VACUUM ANALYZE (schedule via cron)
0 2 * * 0 psql -c "VACUUM ANALYZE;"

# Monthly REINDEX for heavily updated tables
0 3 1 * * psql -c "REINDEX TABLE CONCURRENTLY equations;"
```

### 4. Application Best Practices
- Use connection pooling (PgBouncer)
- Implement query timeouts
- Use pagination for large datasets
- Cache frequently accessed data

## Post-Resolution

1. **Reset pg_stat_statements** to establish new baseline:
   ```sql
   SELECT pg_stat_statements_reset();
   ```

2. **Monitor for 24 hours** to ensure stability

3. **Document findings** in incident report:
   - Root cause
   - Queries affected
   - Indexes created
   - Configuration changes

## Related Runbooks

- [API High Latency](api-high-latency.md)
- [Database Connection Pool Saturation](database-connection-pool.md)
- [API High Error Rate](api-high-error-rate.md)

## Contacts

- **Database Team**: #db-team
- **SRE On-Call**: #sre-oncall
- **Backend Team**: #backend-team
