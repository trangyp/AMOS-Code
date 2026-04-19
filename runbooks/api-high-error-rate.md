# Runbook: API High Error Rate

**Alert**: `APIHighErrorRate`  
**Severity**: Critical  
**Threshold**: Error rate > 0.1% (violates 99.9% availability SLO)  
**Runbook Owner**: SRE Team  
**Last Updated**: 2024-01-15

## Summary

This alert fires when the API error rate exceeds 0.1% over a 5-minute window, indicating potential service degradation or outages affecting customer requests.

## Initial Assessment (First 2 minutes)

### 1. Verify Alert Validity
```bash
# Check current error rate
kubectl exec -it prometheus-pod -- \
  promql 'sum(rate(http_requests_total{job="amos-equation",status_code=~"5.."}[5m])) / sum(rate(http_requests_total{job="amos-equation"}[5m]))'
```

### 2. Check Overall Health
- [ ] Grafana dashboard: [API Overview](../monitoring/grafana/README.md)
- [ ] Service health endpoint: `GET /health/ready`
- [ ] Error distribution by endpoint

### 3. Identify Scope
- [ ] Specific endpoints affected?
- [ ] Specific regions/AZs affected?
- [ ] Customer reports in #support channel?

## Common Causes & Solutions

### Cause 1: Database Connection Issues (40% of cases)

**Symptoms**: 
- Database connection pool errors
- High query latency

**Diagnosis**:
```bash
# Check DB connection pool
kubectl exec -it postgres-pod -- psql -c "
  SELECT state, count(*) 
  FROM pg_stat_activity 
  GROUP BY state;
"

# Check for blocked queries
kubectl exec -it postgres-pod -- psql -c "
  SELECT pid, state, query_start, query 
  FROM pg_stat_activity 
  WHERE state = 'active' 
  ORDER BY query_start 
  LIMIT 10;
"
```

**Immediate Mitigation**:
```bash
# Restart API pods to clear stuck connections
kubectl rollout restart deployment/amos-equation-api
```

**Resolution**:
- Scale database if connection limit reached
- Kill long-running queries if necessary
- Review recent migrations for N+1 queries

### Cause 2: Downstream Service Failures (30% of cases)

**Symptoms**:
- Circuit breaker open alerts
- External API timeout errors

**Diagnosis**:
```bash
# Check circuit breaker states
curl http://localhost:8000/metrics | grep circuit_breaker_state

# Check external service health
curl http://localhost:8000/metrics | grep http_client_requests
```

**Immediate Mitigation**:
- If specific service down, disable via feature flag
- Enable fallback/cache-only mode if available

### Cause 3: Resource Exhaustion (15% of cases)

**Symptoms**:
- High CPU/memory usage
- Container OOM kills

**Diagnosis**:
```bash
# Check resource usage
kubectl top pods -l app=amos-equation-api

# Check for OOM events
kubectl get events --field-selector reason=OOMKilled
```

**Immediate Mitigation**:
```bash
# Scale horizontally
kubectl scale deployment/amos-equation-api --replicas=10

# Or restart to clear memory leaks
kubectl rollout restart deployment/amos-equation-api
```

### Cause 4: Code Deployment Issues (15% of cases)

**Symptoms**:
- Errors started after deployment
- Specific endpoints failing

**Diagnosis**:
```bash
# Check recent deployments
kubectl rollout history deployment/amos-equation-api

# Check pod logs
kubectl logs -l app=amos-equation-api --tail=100 | grep ERROR
```

**Immediate Mitigation**:
```bash
# Rollback to previous version
kubectl rollout undo deployment/amos-equation-api
```

## Detailed Investigation

### Log Analysis
```bash
# Get error logs
kubectl logs -l app=amos-equation-api --tail=1000 | grep -E "(ERROR|Exception|Traceback)"

# Search for specific error patterns
kubectl logs -l app=amos-equation-api --tail=5000 | grep "DatabaseError"
kubectl logs -l app=amos-equation-api --tail=5000 | grep "TimeoutError"
kubectl logs -l app=amos-equation-api --tail=5000 | grep "CircuitBreakerOpen"
```

### Database Investigation
```sql
-- Check for locks
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.relation = blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Check slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

### Redis Investigation
```bash
# Check Redis connection errors
kubectl exec -it redis-pod -- redis-cli info stats | grep -E "(rejected_connections|total_connections_received)"

# Check memory usage
kubectl exec -it redis-pod -- redis-cli info memory | grep used_memory
```

## Escalation Criteria

Escalate to Senior SRE if:
- [ ] Error rate > 10% and increasing
- [ ] Database appears corrupt or unreachable
- [ ] Rollback doesn't resolve issue
- [ ] Incident duration > 30 minutes

Escalate to Engineering Manager if:
- [ ] Data loss suspected
- [ ] Security breach indicators
- [ ] All mitigation attempts failed

## Verification

After mitigation, verify:

```bash
# Wait for error rate to drop
echo "Monitoring error rate for 5 minutes..."
for i in {1..30}; do
  kubectl exec -it prometheus-pod -- \
    promql 'sum(rate(http_requests_total{job="amos-equation",status_code=~"5.."}[5m])) / sum(rate(http_requests_total{job="amos-equation"}[5m]))'
  sleep 10
done
```

**Success Criteria**:
- [ ] Error rate < 0.1% for 5 consecutive minutes
- [ ] All health checks passing
- [ ] Key transactions completing successfully
- [ ] Customer reports resolved (if applicable)

## Post-Resolution

1. **Document timeline** in incident tracking system
2. **Monitor for 1 hour** to ensure stability
3. **Schedule post-mortem** within 48 hours
4. **Update runbook** if new cause identified

## Prevention

- Set up [database query monitoring](database-slow-queries.md)
- Implement circuit breaker patterns (already in place)
- Use deployment canaries to catch issues early
- Maintain adequate resource headroom

## Related Runbooks

- [API High Latency](api-high-latency.md)
- [Database Slow Queries](database-slow-queries.md)
- [Circuit Breaker Open](circuit-breaker-open.md)
- [High CPU Usage](high-cpu-usage.md)

## Contacts

- **SRE On-Call**: #sre-oncall
- **Database Team**: #db-team
- **Backend Team**: #backend-team
- **Incident Commander**: Page if P1 > 30 min
