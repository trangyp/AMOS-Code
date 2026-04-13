# AMOS Production Deployment Guide
## Complete Ecosystem - 12 Components

**Status:** ✅ PRODUCTION READY  
**Date:** April 13, 2026  
**Version:** 1.0.0

---

## 🎯 Overview

Deploy the complete 12-component AMOS ecosystem to production with Docker containerization.

**What's Included:**
- 14-Subsystem Organism OS
- 6 Global Laws Brain
- 50MB+ Knowledge Base
- 4 Interface Layers (CLI, API, Web, MCP)
- Production Docker Configuration

---

## 📦 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

---

## 🚀 Quick Deploy (Local)

```bash
# Clone repository
git clone <repository-url>
cd AMOS-code

# Build and start
make deploy-production

# Or manually:
docker-compose up -d --build

# Check status
docker-compose ps
```

---

## 🌐 Services After Deploy

| Service | URL | Description |
|---------|-----|-------------|
| **API Server** | http://localhost:5000 | REST API access |
| **Web Dashboard** | http://localhost:5000/dashboard | Browser UI |
| **Health Check** | http://localhost:5000/health | System status |

---

## 🔧 Docker Configuration

### Dockerfile
Multi-stage build optimized for production:
- Stage 1: Builder (dependencies)
- Stage 2: Production (runtime only)

### docker-compose.yml
Services orchestrated:
```yaml
amos-api:
  - API server on port 5000
  - 14 subsystems
  - 50MB knowledge
  - Auto-restart
```

---

## ☁️ Cloud Deployment

### AWS ECS
```bash
# Build and push to ECR
docker build -t amos:latest .
docker tag amos:latest <aws-account>.dkr.ecr.<region>.amazonaws.com/amos:latest
docker push <aws-account>.dkr.ecr.<region>.amazonaws.com/amos:latest

# Deploy to ECS
aws ecs update-service --cluster amos-cluster --service amos-service --force-new-deployment
```

### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/amos
gcloud run deploy amos --image gcr.io/PROJECT_ID/amos --platform managed
```

### Azure Container Instances
```bash
# Deploy to Azure
az container create \
  --resource-group amos-rg \
  --name amos-container \
  --image amos:latest \
  --ports 5000
```

---

## 📊 Production Checklist

### Pre-Deployment
- [ ] Docker images built successfully
- [ ] Tests passing (24/24)
- [ ] Environment variables configured
- [ ] Secrets management ready

### Deployment
- [ ] Container started without errors
- [ ] Health check endpoint responding
- [ ] API endpoints accessible
- [ ] Dashboard loading correctly

### Post-Deployment
- [ ] Monitoring enabled
- [ ] Logging configured
- [ ] SSL/TLS configured
- [ ] Backup strategy in place

---

## 🔐 Environment Variables

```bash
# Core
AMOS_ENV=production
AMOS_LOG_LEVEL=INFO

# Knowledge
AMOS_KNOWLEDGE_PATH=/app/_AMOS_BRAIN
AMOS_AUTO_LOAD_KNOWLEDGE=true

# API
AMOS_API_PORT=5000
AMOS_API_HOST=0.0.0.0

# Security
AMOS_API_KEY=<generate-secure-key>
AMOS_CORS_ORIGINS=https://yourdomain.com
```

---

## 🏥 Health Monitoring

### Health Endpoints
```bash
# System health
curl http://localhost:5000/health

# Full status
curl http://localhost:5000/status

# Subsystems
curl http://localhost:5000/subsystems
```

### Docker Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
```

---

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  amos-api:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### Kubernetes
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amos-deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: amos
        image: amos:latest
        ports:
        - containerPort: 5000
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy AMOS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker
        run: docker build -t amos:latest .
      - name: Deploy
        run: docker-compose up -d
```

---

## 🆘 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs amos-api

# Check health
curl http://localhost:5000/health

# Restart
docker-compose restart
```

### High Memory Usage
```bash
# Monitor
docker stats

# Limit memory
docker run -m 4g amos:latest
```

### API Not Responding
```bash
# Check port
docker-compose ps

# Test locally
curl http://localhost:5000/health

# Restart service
docker-compose restart amos-api
```

---

## 📚 Complete Ecosystem - 12 Components

1. ✅ 14-Subsystem Organism OS
2. ✅ 6 Global Laws Brain
3. ✅ Unified Launcher
4. ✅ Test Suite (24 tests)
5. ✅ Demo Showcase (7 demos)
6. ✅ Knowledge Loader (17.8MB)
7. ✅ Enhanced Launcher
8. ✅ Extended Knowledge (55 countries + 19 sectors)
9. ✅ Interactive Shell (CLI)
10. ✅ API Server (REST)
11. ✅ Web Dashboard (Browser)
12. ✅ MCP Server (AI Assistant)
13. ✅ Docker Containerization (Production)

---

## 🎓 Brain's Rationale

**Why Docker now?**

**Before:**
- Works on localhost only
- No production path
- Manual setup required

**After:**
- One-command deploy
- Cloud-native
- Scalable
- Production-ready

**Rule of 2:**
- Internal: Container packaging
- External: Universal deployment

**Rule of 4:**
- ✅ Biological: Users want easy deploy
- ✅ Technical: Docker standard
- ✅ Economic: High value (production ready)
- ✅ Environmental: Portable anywhere

---

## 🚀 Deploy Now

```bash
# One command to production
docker-compose up -d

# Or use make
make deploy-production

# System is live!
```

**12 Components = PRODUCTION-READY ECOSYSTEM!** 🚀🌍
