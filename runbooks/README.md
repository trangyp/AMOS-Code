# AMOS Equation System - Operational Runbooks

Incident response and operational procedures for the AMOS Equation System v2.0.

## Quick Reference

| Alert | Severity | Runbook | Response Time |
|-------|----------|---------|---------------|
| APIHighErrorRate | Critical | [api-high-error-rate.md](api-high-error-rate.md) | 5 min |
| APIVeryHighLatency | Critical | [api-high-latency.md](api-high-latency.md) | 5 min |
| DatabaseVerySlowQueries | Critical | [database-slow-queries.md](database-slow-queries.md) | 5 min |
| CriticalTaskQueueBacklog | Critical | [task-queue-backlog.md](task-queue-backlog.md) | 5 min |
| CircuitBreakerOpen | Critical | [circuit-breaker-open.md](circuit-breaker-open.md) | 5 min |
| BackupFailed | Critical | [backup-failure.md](backup-failure.md) | 30 min |
| HighCPUUsage | Warning | [high-cpu-usage.md](high-cpu-usage.md) | 30 min |
| LowCacheHitRatio | Warning | [low-cache-hit-ratio.md](low-cache-hit-ratio.md) | 1 hour |

## Incident Severity Levels

### Critical (P1)
- Service completely unavailable
- Data loss or corruption risk
- Security breach
- **Response**: Immediate (5 min), page on-call engineer

### Warning (P2)
- Service degraded but functioning
- Performance issues
- Resource exhaustion risk
- **Response**: Within 30 minutes, during business hours

### Info (P3)
- Anomalous behavior detected
- Non-urgent issues
- **Response**: Next business day

## Incident Response Process

### 1. Detection
- Alert fires via PagerDuty/Opsgenie
- Grafana dashboard shows anomaly
- Customer reports issue

### 2. Triage (First 5 minutes)
1. Acknowledge alert
2. Check [Grafana dashboards](../monitoring/grafana/README.md)
3. Determine severity and impact
4. Create incident channel (Slack)

### 3. Mitigation
1. Follow specific runbook
2. Execute immediate mitigation if available
3. Monitor for recovery

### 4. Resolution
1. Confirm service is healthy
2. Document timeline
3. Update status page

### 5. Post-Incident
1. Schedule post-mortem (within 48h)
2. Document lessons learned
3. Update runbooks if needed
4. Implement preventive measures

## Common Commands

```bash
# Check service health
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

# View recent logs
docker logs amos-equation-api --tail 100 -f

# Check database connections
kubectl exec -it postgres-pod -- psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check Redis
kubectl exec -it redis-pod -- redis-cli info stats

# Check task queue
celery -A equation_tasks inspect active
celery -A equation_tasks inspect reserved

# Restart services
kubectl rollout restart deployment/amos-equation-api
```

## Escalation Path

1. **On-Call Engineer** (First 30 min)
2. **Senior SRE** (If unresolved after 30 min)
3. **Engineering Manager** (If unresolved after 1 hour)
4. **VP Engineering** (Major customer-impacting outage)

## Communication Templates

### Internal Slack
```
🚨 **INCIDENT ALERT: [SERVICE] - [SEVERITY]**

**Status**: Investigating
**Impact**: [Description]
**Started**: [Timestamp]
**Lead**: [Engineer name]

**Updates**: #incident-[YYYYMMDD]-[number]
```

### Status Page Update
```
[Investigating/Identified/Monitoring/Resolved] [Service] Issue

We are currently [investigating/experiencing/resolving] an issue with [service].
Impact: [Customer impact description]
Updated: [Timestamp]
```

## Tools Access

- **Grafana**: https://grafana.amos.internal
- **Prometheus**: https://prometheus.amos.internal
- **PagerDuty**: https://amos.pagerduty.com
- **Logs**: https://kibana.amos.internal
- **Traces**: https://jaeger.amos.internal

## Runbook Maintenance

- Review runbooks quarterly
- Update after each major incident
- Test procedures in staging monthly
- Keep diagrams and architecture docs updated

---

*Last updated: 2024-01-15*
*Owner: SRE Team*
*Next review: 2024-04-15*
