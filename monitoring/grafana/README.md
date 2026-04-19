# AMOS Equation System - Grafana Dashboards

Pre-built Grafana dashboards for monitoring the AMOS Equation System in production.

## Dashboards

### 1. API Overview (`api-overview.json`)

Core API metrics and business insights.

**Panels:**
- **Request Rate** - Requests per second by endpoint and method
- **Response Time** - p95 and p99 latency percentiles
- **HTTP Status Distribution** - Status code breakdown (pie chart)
- **Error Rate** - 5xx error percentage with alerting thresholds
- **Requests (1h)** - Total requests in last hour
- **Capacity Usage** - Active users vs limit gauge
- **Equation Operations** - CRUD operation trends
- **Cache Performance** - Redis hit ratio over time

**Use Case:** Daily operations monitoring, SLA tracking

### 2. System Performance (`system-performance.json`)

Infrastructure and resource utilization.

**Panels:**
- **CPU Usage** - Process CPU percentage
- **Memory Usage** - Resident memory bytes
- **Database Query Time** - p95 query latency by operation
- **Redis Operation Time** - p95 Redis command latency
- **Pending Tasks** - Celery queue depth
- **Failed Tasks** - Task failure count
- **Task Throughput** - Tasks processed per second

**Use Case:** Capacity planning, performance troubleshooting

## Quick Start

### Import via UI

1. Open Grafana → Create → Import
2. Upload JSON file or paste contents
3. Select Prometheus data source
4. Click Import

### Import via API

```bash
# Set Grafana credentials
GRAFANA_URL="http://localhost:3000"
GRAFANA_API_KEY="your-api-key"

# Import API Overview dashboard
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  "$GRAFANA_URL/api/dashboards/db" \
  -d @dashboards/api-overview.json

# Import System Performance dashboard
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  "$GRAFANA_URL/api/dashboards/db" \
  -d @dashboards/system-performance.json
```

### Docker Compose Setup

Add to your `docker-compose.yml`:

```yaml
services:
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    depends_on:
      - prometheus

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
```

## Datasource Configuration

Create `datasources.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

## Alerting Rules

Recommended alerts to configure:

| Alert | Condition | Severity |
|-------|-----------|----------|
| High Error Rate | `error_rate > 0.05` | Critical |
| Slow Response Time | `p95_latency > 500ms` | Warning |
| High CPU Usage | `cpu > 80%` | Warning |
| Low Cache Hit Ratio | `hit_ratio < 50%` | Warning |
| Database Slow Queries | `p95_query > 1000ms` | Critical |
| Task Queue Backlog | `pending_tasks > 1000` | Warning |
| Memory Leak | `memory_growth > 10%` | Warning |

## Customization

### Variables

Dashboards use Grafana variables for flexibility:

- `${prometheus_uid}` - Data source selection
- Add custom variables for environment tagging

### Panels

To add new panels:

1. Edit dashboard → Add panel
2. Use Prometheus queries from existing panels as templates
3. Configure thresholds and units
4. Save to JSON and commit to version control

## Metrics Reference

### Application Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | Request latency |
| `equation_operations_total` | Counter | Equation CRUD operations |
| `equation_active_users` | Gauge | Currently active users |
| `equation_cache_hit_ratio` | Gauge | Redis cache efficiency |

### System Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `process_cpu_percent` | Gauge | CPU usage percentage |
| `process_resident_memory_bytes` | Gauge | Memory consumption |
| `database_query_duration_seconds` | Histogram | Query latency |
| `redis_operation_duration_seconds` | Histogram | Redis latency |

### Task Queue Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `celery_tasks_total` | Counter | Tasks processed |
| `celery_tasks_pending` | Gauge | Queue depth |
| `celery_tasks_failed_total` | Counter | Failed tasks |

## Screenshots

### API Overview
```
┌─────────────────────┬─────────────────────┐
│   Request Rate      │   Response Time     │
│   (Line Graph)      │   (p95/p99)         │
├─────────┬───────────┼─────────────────────┤
│ Status  │ Error     │ Requests │ Capacity │
│ (Pie)   │ Rate      │ (Stat)   │ (Gauge)  │
├─────────┴───────────┴─────────────────────┤
│   Equation Operations  │   Cache Performance │
└─────────────────────┴─────────────────────┘
```

## Troubleshooting

### No Data Showing

1. Verify Prometheus is scraping metrics
2. Check data source is configured correctly
3. Ensure time range includes data
4. Validate metric names match

### Performance Issues

- Reduce time range for faster loading
- Add recording rules for complex queries
- Use down-sampling for historical data

## Contributing

When adding new dashboards:

1. Follow naming convention: `amos-{purpose}.json`
2. Include comprehensive panel descriptions
3. Add to this README
4. Export with "Export for sharing externally" checked
5. Commit both JSON and documentation updates

## References

- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Querying](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [FastAPI Prometheus Instrumentation](https://github.com/prometheus/client_python)
