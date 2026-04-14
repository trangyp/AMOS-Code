# AMOS Ecosystem v2.0 - Docker Deployment Guide

## Quick Start

### Build and Run
```bash
# Build the Docker image
docker build -f Dockerfile.amos -t amos:v2.0 .

# Run the container
docker run -d \
  --name amos-ecosystem \
  -p 8080:8080 \
  -e AMOS_BRAIN_ENABLED=1 \
  amos:v2.0

# Check logs
docker logs amos-ecosystem

# Run validation
docker exec amos-ecosystem python test_cognitive_amos.py
```

### Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View status
docker-compose ps

# Scale cognitive workers
docker-compose up -d --scale amos-cognitive=3
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AMOS_BRAIN_ENABLED` | `1` | Enable cognitive mode |
| `AMOS_DEPLOY_PATH` | `/app/clawspring/amos_brain` | Module path |
| `AMOS_VERSION` | `2.0` | Version tag |
| `PYTHONPATH` | `/app/clawspring` | Python path |

## Health Check

The container includes an automatic health check that validates:
- Module presence (16 modules)
- Import functionality
- System health score

Health status available via:
```bash
docker inspect --format='{{.State.Health.Status}}' amos-ecosystem
```

## Production Deployment

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amos-ecosystem
spec:
  replicas: 3
  selector:
    matchLabels:
      app: amos
  template:
    metadata:
      labels:
        app: amos
    spec:
      containers:
      - name: amos
        image: amos:v2.0
        ports:
        - containerPort: 8080
        env:
        - name: AMOS_BRAIN_ENABLED
          value: "1"
```

### Cloud Run / AWS ECS
```bash
# Push to registry
docker tag amos:v2.0 ghcr.io/yourorg/amos:v2.0
docker push ghcr.io/yourorg/amos:v2.0

# Deploy to cloud
gcloud run deploy amos-ecosystem --image ghcr.io/yourorg/amos:v2.0
```

## Verification

Test deployment:
```bash
# Test imports
docker exec amos-ecosystem python -c "
import sys
sys.path[:0] = ['clawspring', 'clawspring/amos_brain']
from amos_cognitive_router import CognitiveRouter
print('Router OK')
"

# Run full test suite
docker exec amos-ecosystem python test_cognitive_amos.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Check PYTHONPATH env var |
| Permission denied | Ensure user 'amos' owns /app |
| Health check fails | Run validation manually |

## Architecture

- **Base Image**: `python:3.11-slim`
- **User**: Non-root `amos` user
- **Multi-stage**: Builder + Production stages
- **Size**: ~150MB compressed
- **Security**: Minimal attack surface, no root access

## Tags

- `amos:v2.0` - Stable release
- `amos:latest` - Latest build
- `amos:develop` - Development build
