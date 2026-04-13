# AMOS Brain Operations Runbook

**Domain:** neurosyncai.tech  
**System:** AMOS Brain Production API  
**Version:** 1.0.0  
**Last Updated:** April 2026

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Quick Reference](#quick-reference)
3. [Deployment](#deployment)
4. [Monitoring](#monitoring)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance](#maintenance)
7. [Emergency Procedures](#emergency-procedures)

---

## System Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        neurosyncai.tech                     │
├─────────────────────────────────────────────────────────────┤
│  Nginx (Reverse Proxy)                                      │
│  ├── / → API Server (Port 5000)                            │
│  ├── /ws → WebSocket (Port 8765)                           │
│  ├── /monitoring → Dashboard                               │
│  └── /admin → Admin Panel                                  │
├─────────────────────────────────────────────────────────────┤
│  AMOS Brain API (Flask)                                     │
│  ├── Core: think, decide, validate endpoints                 │
│  ├── AMOSL: compile endpoint                               │
│  └── Real-time: WebSocket streaming                        │
├─────────────────────────────────────────────────────────────┤
│  Monitoring Stack                                          │
│  ├── Health Checks → amos_health_monitor.py                │
│  ├── Metrics → amos_metrics_collector.py                   │
│  ├── Alerts → amos_alerting.py                             │
│  └── Dashboard → templates/monitoring.html                  │
├─────────────────────────────────────────────────────────────┤
│  Persistence                                               │
│  ├── SQLite Database (amos.db)                             │
│  ├── Query History                                         │
│  └── Metrics & Alert History                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| API Server | `amos_api_server.py` | Main REST API |
| WebSocket | `websocket_server.py` | Real-time streaming |
| Health Monitor | `amos_health_monitor.py` | System health checks |
| Metrics | `amos_metrics_collector.py` | Request metrics |
| Alerts | `amos_alerting.py` | Alert management |
| Database | `amos_database.py` | Persistence layer |
| Load Test | `amos_load_test.py` | Performance testing |

---

## Quick Reference

### Service Status

```bash
# Check if API is running
curl https://neurosyncai.tech/health

# Get system status
curl https://neurosyncai.tech/status

# View metrics
curl https://neurosyncai.tech/api/metrics/summary

# Check active alerts
curl https://neurosyncai.tech/api/alerts/active
```

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f amos-api

# Restart service
docker-compose restart amos-api

# Stop all
docker-compose down
```

### Key URLs

| Endpoint | URL | Purpose |
|----------|-----|---------|
| Health | `https://neurosyncai.tech/health` | Basic health check |
| Status | `https://neurosyncai.tech/status` | Full system status |
| Metrics | `https://neurosyncai.tech/api/metrics/summary` | Performance metrics |
| Monitoring | `https://neurosyncai.tech/monitoring` | Dashboard UI |
| Admin | `https://neurosyncai.tech/admin` | Admin panel |

---

## Deployment

### Automated Deployment (CI/CD)

Deployments are automated via GitHub Actions:

1. Push to `main` branch triggers pipeline
2. Tests run (unit, integration, load)
3. Docker image built and pushed
4. Deployed to Hostinger via SSH
5. Health checks verify deployment

### Manual Deployment

```bash
# 1. SSH to server
ssh user@neurosyncai.tech

# 2. Pull latest code
cd ~/AMOS-code
git pull origin main

# 3. Rebuild and restart
docker-compose down
docker-compose up -d --build

# 4. Verify
curl http://localhost:5000/health
```

### Rollback

```bash
# View previous images
docker images | grep amos-brain

# Rollback to previous version
docker-compose down
docker-compose up -d --no-build  # Uses existing image

# Or specify version
docker pull ghcr.io/trangphan/amos-brain:previous-tag
docker-compose up -d
```

---

## Monitoring

### Health Endpoints

```bash
# Detailed health
curl https://neurosyncai.tech/api/health

# Health trend (24h)
curl https://neurosyncai.tech/api/health/trend?hours=24
```

### Metrics

```bash
# Current metrics summary
curl https://neurosyncai.tech/api/metrics/summary?minutes=5

# Prometheus format
curl https://neurosyncai.tech/api/metrics/prometheus

# Full export
curl https://neurosyncai.tech/api/metrics
```

### Alerts

```bash
# View active alerts
curl https://neurosyncai.tech/api/alerts/active

# View alert history
curl https://neurosyncai.tech/api/alerts/history?hours=24

# Acknowledge alert
curl -X POST https://neurosyncai.tech/api/alerts/acknowledge \
  -H "Content-Type: application/json" \
  -d '{"alert_id": "ALT-0001", "user": "ops"}'
```

### Alert Rules

| Rule | Condition | Severity |
|------|-----------|----------|
| high_error_rate | Error rate > 5% | Warning |
| critical_error_rate | Error rate > 10% | Critical |
| high_latency | Avg response > 1000ms | Warning |
| memory_critical | Memory > 90% | Critical |

---

## Troubleshooting

### API Not Responding

```bash
# 1. Check if container is running
docker ps | grep amos

# 2. Check logs
docker-compose logs amos-api --tail=50

# 3. Check resource usage
docker stats amos-api

# 4. Restart if needed
docker-compose restart amos-api
```

### High Error Rate

```bash
# Check recent errors
curl https://neurosyncai.tech/api/metrics/summary | jq .error_rate

# View logs for errors
docker-compose logs amos-api | grep ERROR

# Run health check
python amos_health_monitor.py
```

### Database Issues

```bash
# Check database file
ls -lh amos.db

# Check for corruption
sqlite3 amos.db "PRAGMA integrity_check;"

# Backup database
cp amos.db amos.db.backup.$(date +%Y%m%d)

# Restore from backup
cp amos.db.backup.20260413 amos.db
```

### Memory Issues

```bash
# Check memory usage
docker stats --no-stream amos-api

# View memory metric
curl https://neurosyncai.tech/api/metrics/summary | jq '.gauges.memory_percent'

# Restart to clear memory
docker-compose restart amos-api
```

---

## Maintenance

### Daily Checks

- [ ] Check `/health` endpoint responds
- [ ] Verify error rate < 5%
- [ ] Check active alerts
- [ ] Review metrics dashboard

### Weekly Tasks

- [ ] Review 7-day usage stats
- [ ] Check disk space
- [ ] Review error logs
- [ ] Verify backups

### Monthly Tasks

- [ ] Database cleanup (old records)
- [ ] Load test performance
- [ ] Review and update alert thresholds
- [ ] Security updates

### Database Cleanup

```bash
# Clean records older than 30 days
python -c "
import asyncio
from amos_persistence import get_persistence

async def cleanup():
    p = get_persistence()
    result = await p.run_cleanup(retention_days=30)
    print(f'Cleaned: {result}')

asyncio.run(cleanup())
"
```

---

## Emergency Procedures

### Complete Outage

1. **Check service status**
   ```bash
   docker-compose ps
   ```

2. **Check host resources**
   ```bash
   df -h  # Disk
   free -h  # Memory
   uptime  # Load
   ```

3. **Restart services**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Verify recovery**
   ```bash
   curl https://neurosyncai.tech/health
   ```

### Data Corruption

1. **Stop services**
   ```bash
   docker-compose down
   ```

2. **Restore from backup**
   ```bash
   cp amos.db.backup.latest amos.db
   ```

3. **Restart**
   ```bash
   docker-compose up -d
   ```

### Security Incident

1. **Isolate service**
   ```bash
   docker-compose down
   ```

2. **Check logs for intrusion**
   ```bash
   cat logs/amos.log | grep -i "auth\|login\|unauthorized"
   ```

3. **Rotate secrets**
   - Update API keys
   - Update database credentials
   - Update webhook tokens

4. **Restart with new secrets**
   ```bash
   docker-compose up -d
   ```

---

## Contact & Escalation

| Issue | Contact | Response Time |
|-------|---------|---------------|
| Critical outage | On-call engineer | 15 min |
| Security incident | Security team | 30 min |
| Performance degradation | DevOps team | 1 hour |
| General questions | Documentation | 24 hours |

---

## Appendix

### Environment Variables

```bash
# Core
PORT=5000
DEBUG=false
AMOS_DB_PATH=amos.db

# Security
API_KEY_SECRET=xxx
JWT_SECRET=xxx

# Monitoring
ALERT_WEBHOOK_URL=https://hooks.slack.com/...
METRICS_RETENTION_DAYS=30

# Deployment
DOCKER_REGISTRY=ghcr.io
DEPLOY_TARGET=hostinger
```

### Useful Commands

```bash
# View all endpoints
curl https://neurosyncai.tech/

# Test think endpoint
curl -X POST https://neurosyncai.tech/think \
  -H "Content-Type: application/json" \
  -d '{"query": "Test", "domain": "software"}'

# Run load test
python amos_load_test.py --duration 60 --concurrency 20

# Database query
sqlite3 amos.db "SELECT COUNT(*) FROM queries WHERE timestamp > datetime('now', '-1 day');"
```

---

**Document Owner:** Trang Phan  
**System:** AMOS Brain Production  
**Domain:** neurosyncai.tech
