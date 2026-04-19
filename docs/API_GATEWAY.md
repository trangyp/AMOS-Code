# AMOS SuperBrain API Gateway v2.0.0

## Overview

Unified entry point for all 12 SuperBrain systems with advanced traffic management, security enforcement at the edge, and full observability integration.

---

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │          API Gateway                 │
                    │  ┌─────────┐ ┌─────────┐ ┌────────┐  │
                    │  │  JWT    │ │  Rate   │ │Circuit │  │
                    │  │  Auth   │ │  Limit  │ │Breaker │  │
                    │  └─────────┘ └─────────┘ └────────┘  │
                    └─────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐           ┌────▼────┐           ┌────▼────┐
   │Cognitive│           │Resilience│           │Knowledge│
   │ Router  │           │ Engine   │           │ Loader  │
   └─────────┘           └─────────┘           └─────────┘
```

---

## Gateway Routes

### Core API Routes

| Route | Target | Methods | Auth | Governance |
|-------|--------|---------|------|------------|
| `/api/v1/production` | Production API | GET, POST, PUT, DELETE | ✅ | ✅ |
| `/graphql` | GraphQL API | GET, POST | ✅ | ✅ |

### System Routes (12 Systems)

| System | Route | Methods | Rate Limit Tier |
|--------|-------|---------|-----------------|
| **Cognitive Router** | `/api/v1/router` | POST | standard |
| **Resilience Engine** | `/api/v1/resilience` | GET, POST | standard |
| **Knowledge Loader** | `/api/v1/knowledge` | GET, POST | standard |
| **Master Orchestrator** | `/api/v1/orchestrator` | POST | premium |
| **Agent Messaging** | `/api/v1/agents/messages` | GET, POST | standard |
| **Agent Observability** | `/api/v1/agents/telemetry` | GET, POST | unlimited |
| **UBI Engine** | `/api/v1/ubi` | POST | standard |
| **AMOS Tools** | `/api/v1/tools` | POST | premium |
| **Audit Exporter** | `/api/v1/audit` | GET | standard |
| **SuperBrain Governance** | `/api/v1/governance` | GET, POST | unlimited |

---

## Gateway Features

### 1. JWT Authentication

```bash
# Request with JWT token
curl -H "Authorization: Bearer <token>" \
     https://api.amos.example.com/api/v1/router
```

### 2. Rate Limiting

| Tier | Requests/Minute |
|------|-----------------|
| standard | 100 |
| premium | 500 |
| unlimited | ∞ |

### 3. Circuit Breaking

Circuit states: CLOSED → OPEN → HALF_OPEN → CLOSED

| State | Behavior |
|-------|----------|
| CLOSED | Normal operation |
| OPEN | Reject requests, fail fast |
| HALF_OPEN | Test recovery |

### 4. Security Layers

Request processing order:
1. Feature flag check
2. Circuit breaker check
3. JWT authentication
4. RBAC permission check
5. Rate limit check
6. SuperBrain governance validation
7. Route to backend

---

## Usage

### Starting the Gateway

```python
from backend.gateway.api_gateway import create_gateway_app
import uvicorn

app = create_gateway_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Docker Compose

```yaml
version: '3.8'
services:
  gateway:
    build: .
    ports:
      - "8080:8080"
    environment:
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - redis
      - kafka
```

---

## Monitoring

### Gateway Metrics

```bash
# Get gateway status
curl https://api.amos.example.com/gateway/metrics

# Response
{
  "rate_limits": {"active_limits": 42},
  "circuits": {
    "cognitive_router": "closed",
    "resilience_engine": "open"
  },
  "routes": 12
}
```

### Health Check

```bash
curl https://api.amos.example.com/health

# Response
{
  "status": "healthy",
  "version": "2.0.0",
  "systems": 12,
  "timestamp": 1744918800.0
}
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_PORT` | 8080 | Gateway port |
| `REDIS_URL` | redis://localhost:6379/2 | Redis for rate limiting |
| `JWT_SECRET` | superbrain-jwt-secret | JWT signing key |
| `JWT_ALGORITHM` | HS256 | JWT algorithm |
| `RATE_LIMIT_REQUESTS` | 100 | Requests per window |
| `RATE_LIMIT_WINDOW` | 60 | Window in seconds |
| `CIRCUIT_FAILURE_THRESHOLD` | 5 | Failures to open circuit |
| `CIRCUIT_RECOVERY_TIMEOUT` | 30 | Seconds before recovery |

---

## Security

### Request Flow

```
Request → CORS → Trusted Host → Feature Check → Circuit Check
  ↓
Auth (JWT) → RBAC Check → Rate Limit → SuperBrain → Backend
```

### Response Codes

| Code | Reason |
|------|--------|
| 200 | Success |
| 401 | Unauthorized (JWT invalid) |
| 403 | Forbidden (RBAC/Governance denied) |
| 429 | Rate limit exceeded |
| 502 | Backend error |
| 503 | Service unavailable (circuit open) |

---

## Integration with Other Systems

### Observability

- Tracing context propagated to all backends
- Gateway spans include routing decisions

### Data Pipeline

- Routing events published to `api_gateway.events`
- Access denied events tracked

### Feature Flags

- Gateway checks if API routes are enabled
- Can disable routes via feature flags

---

## Best Practices

### 1. Always Use JWT in Production

```python
# Good - JWT validation
Authorization: Bearer <token>

# Bad - no auth in production
# (Works in development with JWT_AVAILABLE=False)
```

### 2. Monitor Circuit States

```python
# Check circuit health
metrics = gateway.get_gateway_metrics()
for system, state in metrics["circuits"].items():
    if state == "open":
        alert_ops_team(system)
```

### 3. Configure Rate Limits Per Client

```python
# Premium clients get higher limits
RouteConfig(
    path="/api/v1/tools",
    rate_limit_tier="premium"  # 500 req/min
)
```

---

**Maintainer:** Trang Phan  
**Last Updated:** 2026-04-16  
**Version:** 2.0.0
