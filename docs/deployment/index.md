# Deployment Guide

Deploy AMOS in various environments from development to production.

## Deployment Options

AMOS supports multiple deployment scenarios:

### 🐳 [Docker](docker.md)
Containerized deployment for easy setup and consistency.

### ☸️ [Kubernetes](kubernetes.md)
Scalable deployment on Kubernetes clusters.

### 🖥️ [Production](production.md)
Bare metal and VM deployment for production use.

### 📊 [Monitoring](monitoring.md)
Observability, logging, and alerting setup.

---

## Quick Deployment

### Docker (Recommended)

```bash
# Start all services
docker-compose -f docker-compose.amos.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f amos-api
```

### Production Checklist

Before deploying to production:

- [ ] Configure environment variables
- [ ] Set up authentication (JWT secrets)
- [ ] Enable rate limiting
- [ ] Configure observability (Prometheus/Grafana)
- [ ] Set up backups
- [ ] Test disaster recovery
- [ ] Review security settings

---

## Environment Requirements

| Environment | CPU | RAM | Storage | Notes |
|-------------|-----|-----|---------|-------|
| Development | 2 cores | 4GB | 10GB | Local development |
| Staging | 4 cores | 8GB | 50GB | Pre-production testing |
| Production | 8+ cores | 16GB+ | 100GB+ | High availability |

---

## Getting Help

- [Architecture Overview](../architecture/index.md) - Understand AMOS architecture
- [Configuration](../getting-started/configuration.md) - Configure AMOS for your environment
- [GitHub Issues](https://github.com/trangyp/AMOS-Code/issues) - Report deployment issues
