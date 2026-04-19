# Analytics & Business Intelligence

Data warehouse and analytics for AMOS Equation System.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              AMOS Analytics Pipeline                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Application Events  →  Analytics Warehouse  →  BI     │
│       (FastAPI)            (PostgreSQL)         Tools    │
│                                                         │
│  Tracked Events:                                       │
│  • API requests (path, method, latency)               │
│  • User activity (signups, logins, active)             │
│  • Business (equations created, verified)              │
│  • System (cache hits, errors, webhooks)               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```python
# Track events in application
from analytics.warehouse import AnalyticsWarehouse, MetricType

warehouse = AnalyticsWarehouse("postgresql+asyncpg://...")

# Track API request
await warehouse.track_event(
    MetricType.API_REQUEST,
    user_id="user-123",
    value=1,
    metadata={"path": "/api/equations", "method": "GET"}
)

# Get dashboard metrics
metrics = await warehouse.get_dashboard_metrics()
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /analytics/dashboard` | Dashboard metrics (7d default) |
| `GET /analytics/timeseries/{metric}` | Time series data |
| `GET /analytics/aggregations/{metric}` | Aggregated statistics |
| `GET /analytics/report/weekly` | Weekly business report |
| `GET /analytics/health` | Analytics system health |

## Metrics Tracked

| Metric | Type | Use Case |
|--------|------|----------|
| `api_request` | Counter | Traffic volume |
| `api_latency` | Histogram | Performance monitoring |
| `api_error` | Counter | Error tracking |
| `user_active` | Gauge | DAU/MAU calculation |
| `user_signup` | Counter | Growth metrics |
| `equation_created` | Counter | Business activity |
| `equation_verified` | Counter | Business activity |
| `task_completed` | Counter | Background task health |
| `webhook_sent` | Counter | Integration health |
| `cache_hit` | Counter | Cache efficiency |
| `cache_miss` | Counter | Cache efficiency |

## Time Series Queries

```bash
# Get API requests last 24 hours
curl "http://localhost:8000/analytics/timeseries/api_request?hours=24"

# Get daily aggregations for equations
curl "http://localhost:8000/analytics/aggregations/equation_created?period=day"

# Weekly business report
curl "http://localhost:8000/analytics/report/weekly"
```

## CLI Usage

```bash
# Initialize warehouse
python analytics/warehouse.py --init

# Generate reports
python analytics/warehouse.py --report weekly
python analytics/warehouse.py --report dashboard

# Export data
python analytics/warehouse.py --export metrics.json
```

## Integration with FastAPI

```python
from fastapi import FastAPI
from analytics.api import router as analytics_router
from analytics.warehouse import create_analytics_middleware

app = FastAPI()
app.include_router(analytics_router)

# Add automatic tracking middleware
@app.middleware("http")
async def analytics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    
    await track_request(request, response, duration)
    return response
```

## External BI Integration

### Grafana

```json
{
  "datasource": "postgres",
  "query": "SELECT timestamp, value FROM analytics_events WHERE event_type = 'api_request'"
}
```

### Tableau/Metabase

Connect directly to `analytics_events` table for custom dashboards.

### Data Export

```bash
# Export for external analysis
psql $DATABASE_URL -c "COPY (SELECT * FROM analytics_events WHERE timestamp > NOW() - INTERVAL '7 days') TO STDOUT WITH CSV HEADER" > export.csv
```

## Performance Considerations

- Analytics writes are async (non-blocking)
- Partition table by date for large datasets
- Consider ClickHouse for high volume (>1M events/day)
- Retention policy: 90 days hot, 1 year cold storage

---

*Data-driven decisions start here*
