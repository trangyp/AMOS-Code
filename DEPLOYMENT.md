# AMOS Deployment Guide

Complete deployment instructions for AMOS v3.0.0 - Full Stack Cognitive Operating System.

**Creator:** Trang Phan  
**Version:** 3.0.0  
**Architecture:** React Dashboard + FastAPI Backend

---

## Quick Start (Docker)

The fastest way to deploy AMOS is using Docker Compose:

```bash
# Clone repository
git clone https://github.com/trangphan/amos.git
cd amos

# Start all services
docker-compose up -d

# Access points:
# - Dashboard: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - Landing Page: http://localhost:3000/landing.html
```

---

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐
│  AMOS Dashboard │────▶│  AMOS Backend   │
│   (React + Vite)│     │ (FastAPI + Python)
│   Port: 3000    │     │   Port: 8000    │
└─────────────────┘     └─────────────────┘
         │                       │
         └───────────────────────┘
              Docker Network
```

### Services:

1. **amos-dashboard** - React frontend with Nginx
2. **amos-backend** - FastAPI backend with WebSocket support
3. **amos-network** - Docker bridge network for communication

---

## Prerequisites

### System Requirements:

- **Docker**: 20.10+ with Docker Compose
- **CPU**: 2+ cores
- **RAM**: 4GB+ recommended
- **Disk**: 2GB free space

### Optional (Development):

- **Node.js**: 18+ (for frontend development)
- **Python**: 3.11+ (for backend development)
- **npm**: 9+ or **yarn**: 1.22+

---

## Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Production deployment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update to latest version
docker-compose pull
docker-compose up -d
```

### Option 2: Individual Containers

```bash
# Build backend
cd backend
docker build -t amos-backend:latest .
docker run -d -p 8000:8000 --name amos-backend amos-backend:latest

# Build frontend
cd ../dashboard
docker build -t amos-dashboard:latest .
docker run -d -p 3000:80 --name amos-dashboard amos-dashboard:latest
```

### Option 3: Local Development

```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd dashboard
npm install
npm run dev
```

---

## Environment Configuration

### Backend Environment Variables:

Create `.env` file in `backend/` directory:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# CORS (for production, specify your domain)
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Security (generate strong secret)
SECRET_KEY=your-secret-key-here

# Optional: Database (for persistent storage)
# DATABASE_URL=postgresql://user:pass@localhost:5432/amos

# Optional: Redis (for caching)
# REDIS_URL=redis://localhost:6379/0
```

### Frontend Environment Variables:

Create `.env` file in `dashboard/` directory:

```env
# API URL
VITE_API_URL=http://localhost:8000

# WebSocket URL
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Production Deployment

### 1. Cloud Platforms

#### AWS ECS/Fargate:
```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL
docker build -t amos-backend ./backend
docker build -t amos-dashboard ./dashboard
docker tag amos-backend:latest $ECR_URL/amos-backend:latest
docker tag amos-dashboard:latest $ECR_URL/amos-dashboard:latest
docker push $ECR_URL/amos-backend:latest
docker push $ECR_URL/amos-dashboard:latest
```

#### Google Cloud Run:
```bash
# Deploy backend
gcloud run deploy amos-backend --source ./backend --port 8000

# Deploy frontend
gcloud run deploy amos-dashboard --source ./dashboard --port 80
```

#### Azure Container Instances:
```bash
# Deploy using Azure CLI
az container create --resource-group myResourceGroup \
  --name amos-backend \
  --image amos-backend:latest \
  --ports 8000
```

### 2. VPS/Server Deployment

```bash
# On your server
git clone https://github.com/trangphan/amos.git
cd amos

# Create production docker-compose
cp docker-compose.yml docker-compose.prod.yml

# Edit docker-compose.prod.yml to use specific image versions
# Change 'latest' to specific version tags

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Setup reverse proxy (nginx)
sudo cp nginx.conf /etc/nginx/sites-available/amos
sudo ln -s /etc/nginx/sites-available/amos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Kubernetes (K8s)

```yaml
# amos-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amos-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: amos-backend
  template:
    metadata:
      labels:
        app: amos-backend
    spec:
      containers:
      - name: backend
        image: amos-backend:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: amos-backend-service
spec:
  selector:
    app: amos-backend
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

Deploy:
```bash
kubectl apply -f amos-deployment.yaml
```

---

## SSL/TLS Configuration

### Using Let's Encrypt (Certbot)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Manual SSL with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Health Checks & Monitoring

### Built-in Health Endpoints:

- **Frontend**: `http://localhost:3000/health`
- **Backend**: `http://localhost:8000/health`
- **API Docs**: `http://localhost:8000/docs`

### Docker Health Checks:

```bash
# Check container health
docker ps
docker inspect --format='{{.State.Health.Status}}' amos-dashboard
docker inspect --format='{{.State.Health.Status}}' amos-backend
```

### Prometheus Metrics (Optional):

Add to `backend/requirements.txt`:
```
prometheus-fastapi-instrumentator
```

Add to `backend/main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

---

## Troubleshooting

### Common Issues:

#### 1. Port Already in Use
```bash
# Find process using port
sudo lsof -i :3000
sudo lsof -i :8000

# Kill process or change port
```

#### 2. CORS Errors
- Check `CORS_ORIGINS` environment variable
- Ensure it includes your frontend URL

#### 3. WebSocket Connection Failed
- Check firewall rules
- Ensure nginx proxy is configured for WebSocket

#### 4. Container Won't Start
```bash
# View logs
docker-compose logs amos-backend
docker-compose logs amos-dashboard

# Check resource usage
docker stats
```

### Debug Mode:

```bash
# Run without daemon mode to see logs
docker-compose up

# Debug backend
docker run -it --rm amos-backend:latest bash

# Debug frontend
docker run -it --rm amos-dashboard:latest sh
```

---

## Backup & Recovery

### Data Persistence:

Docker volumes are used for:
- Memory storage
- Logs
- Checkpoints

```bash
# Backup volumes
docker run --rm -v amos-memory:/source -v $(pwd):/backup alpine tar czf /backup/amos-memory.tar.gz -C /source .
docker run --rm -v amos-logs:/source -v $(pwd):/backup alpine tar czf /backup/amos-logs.tar.gz -C /source .

# Restore volumes
docker run --rm -v amos-memory:/target -v $(pwd):/backup alpine tar xzf /backup/amos-memory.tar.gz -C /target
docker run --rm -v amos-logs:/target -v $(pwd):/backup alpine tar xzf /backup/amos-logs.tar.gz -C /target
```

---

## Security Best Practices

1. **Use specific image tags** (not `latest`)
2. **Run containers as non-root user**
3. **Keep base images updated**
4. **Scan images for vulnerabilities**:
   ```bash
   docker scan amos-backend:latest
   ```
5. **Use secrets management** for sensitive data
6. **Enable HTTPS** in production
7. **Set up firewalls** and security groups
8. **Regular security updates**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

---

## Support

- **Documentation**: http://localhost:8000/docs (when running)
- **GitHub Issues**: https://github.com/trangphan/amos/issues
- **API Status**: http://localhost:8000/health

---

## License

MIT License - See LICENSE file for details.

---

**AMOS - Absolute Meta Operating System**  
*Devin's Power, Your Control*
