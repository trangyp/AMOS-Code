# AMOS API Gateway - Traefik Configuration

Production-grade API Gateway for AMOS Cognitive Operating System.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY (Traefik)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Router    │  │  Middleware │  │   Service   │            │
│  │  (Routing)  │→ │  (Security) │→ │ (Upstream) │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌─────────┐    ┌──────────┐    ┌──────────┐
        │ REST API│    │ GraphQL  │    │ WebSocket│
        │  :8080  │    │  :8080   │    │  :8080   │
        └─────────┘    └──────────┘    └──────────┘
```

## Endpoints

| Domain | Service | Description |
|--------|---------|-------------|
| `api.amos.localhost` | REST API | AMOS REST endpoints |
| `graphql.amos.localhost` | GraphQL API | Strawberry GraphQL |
| `ws.amos.localhost` | WebSocket | Real-time updates |
| `traefik.amos.localhost` | Dashboard | Traefik UI (protected) |
| `flower.amos.localhost` | Flower | Celery monitoring |
| `prometheus.amos.localhost` | Prometheus | Metrics collection |
| `grafana.amos.localhost` | Grafana | Observability dashboards |

## Quick Start

```bash
# Start the API Gateway stack
docker-compose -f docker-compose.traefik.yml up -d

# View logs
docker-compose -f docker-compose.traefik.yml logs -f traefik

# Check service health
curl http://localhost:8080/ping

# Test API
curl -k https://api.amos.localhost/health
curl -k https://graphql.amos.localhost/graphql
```

## Security Features

### TLS/SSL
- Automatic Let's Encrypt certificates
- TLS 1.2+ only (modern cipher suites)
- HTTP → HTTPS redirect
- HSTS headers

### Middleware Chain
1. **Security Headers** - X-Frame-Options, CSP, etc.
2. **CORS** - Cross-origin request handling
3. **Rate Limiting** - 100 req/min average, 200 burst
4. **Compression** - Gzip/Brotli response compression
5. **Circuit Breaker** - Fail fast on degradation
6. **Authentication** - JWT/Basic Auth

### IP Protection
- Internal services (PostgreSQL, Redis) on isolated network
- Admin dashboards protected by IP allowlist
- Rate limiting excludes private ranges

## Configuration

### Static Config (`traefik.yml`)
Core settings that require restart:
- Entry points (ports)
- Certificate resolvers
- API/dashboard settings
- Provider configuration

### Dynamic Config (`dynamic/*.yml`)
Hot-reloadable settings:
- Middleware definitions
- Router rules
- Service definitions
- TLS options

### Environment Variables
```bash
# .env file
DB_PASSWORD=secure-password-here
JWT_SECRET=your-jwt-secret-here
GRAFANA_USER=admin
GRAFANA_PASSWORD=secure-password
FLOWER_AUTH=admin:secure-password
```

## Scaling

```yaml
# Scale API instances
docker-compose up -d --scale amos-api=3

# Traefik automatically:
# - Discovers new instances
# - Load balances requests
# - Health checks each instance
# - Removes unhealthy instances
```

## Monitoring

### Metrics
Traefik exposes Prometheus metrics at `:8080/metrics`:
- Request counts and latency
- Response codes
- Backend health
- TLS certificate expiry

### Dashboard
Access Traefik dashboard:
```bash
# Add to /etc/hosts
echo "127.0.0.1 traefik.amos.localhost" | sudo tee -a /etc/hosts

# Visit https://traefik.amos.localhost
# Login: admin / admin (change in production)
```

## Troubleshooting

### Check Router Status
```bash
curl -k https://traefik.amos.localhost/api/http/routers
curl -k https://traefik.amos.localhost/api/http/services
curl -k https://traefik.amos.localhost/api/http/middlewares
```

### Debug Mode
```yaml
# traefik.yml
log:
  level: DEBUG
```

### Common Issues

**503 Service Unavailable**
- Check if backend service is healthy: `docker-compose ps`
- Verify service labels are correct
- Check network connectivity

**Certificate Issues**
- Ensure ports 80/443 are available
- Check Let's Encrypt rate limits
- Use staging server for testing

**Rate Limiting**
- Check rate limit headers: `X-Rate-Limit-*`
- Adjust limits in middlewares.yml
- Excludes private IP ranges by default

## Production Checklist

- [ ] Change default passwords
- [ ] Configure production TLS certificates
- [ ] Set up proper logging (ELK/Loki)
- [ ] Configure monitoring alerts
- [ ] Enable access logs
- [ ] Set up rate limiting for public endpoints
- [ ] Configure circuit breakers
- [ ] Review security headers
- [ ] Set up DDoS protection
- [ ] Configure backup/restore

## References

- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Docker Compose Integration](https://doc.traefik.io/traefik/providers/docker/)
- [Middleware Overview](https://doc.traefik.io/traefik/middlewares/overview/)
