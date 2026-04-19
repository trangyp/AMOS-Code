# AMOS Kubernetes Deployment v2.9.0

Production-grade Kubernetes deployment with Helm charts for AMOS v2.9.0.

## Quick Start (Helm)

```bash
# Add required Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add traefik https://traefik.github.io/charts
helm repo update

# Install AMOS with dependencies
helm install amos ./amos -n amos --create-namespace

# Or upgrade existing deployment
helm upgrade amos ./amos -n amos

# Check status
helm status amos -n amos
kubectl get pods -n amos
```

## Architecture (Helm Deployment)

```
┌─────────────────────────────────────────────────────────────┐
│                    Ingress (Traefik)                        │
│     api.amos.local     graphql.amos.local                   │
│     ws.amos.local        traefik.amos.local                 │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  amos-api    │   │ amos-graphql │   │ amos-websocket│
│  (2-10 pods) │   │  (2-8 pods)  │   │  (2-6 pods)  │
│     HPA      │   │     HPA      │   │     HPA      │
└──────────────┘   └──────────────┘   └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Dependencies (Subcharts)                   │
│  ├─ PostgreSQL (1 primary + 1 replica)                     │
│  ├─ Redis (1 master + 2 replicas)                          │
│  ├─ Kafka (3 brokers + 3 Zookeeper)                        │
│  └─ Traefik (2 replicas, LoadBalancer)                     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Celery Workers (HPA)                     │
│              amos-workers (3-20 pods)                       │
└─────────────────────────────────────────────────────────────┘
```

## Helm Chart Structure

| Component | Type | Scaling | Resources |
|-----------|------|---------|-----------|
| API Server | Deployment | HPA: 2-10 pods | 250m-1000m CPU |
| GraphQL Server | Deployment | HPA: 2-8 pods | 250m-1000m CPU |
| WebSocket Server | Deployment | HPA: 2-6 pods | 100m-500m CPU |
| Celery Workers | Deployment | HPA: 3-20 pods | 500m-1000m CPU |
| PostgreSQL | StatefulSet | 1 primary + 1 replica | 1-2 CPU |
| Redis | StatefulSet | 1 master + 2 replicas | 500m-1000m CPU |
| Kafka | StatefulSet | 3 brokers + 3 Zookeeper | 1-2 CPU |
| Traefik | Deployment | 2 replicas | 100m-500m CPU |

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- NGINX Ingress Controller
- cert-manager (for TLS)
- Storage class for PostgreSQL PVC

## Configuration

### Custom Values

Create a `custom-values.yaml` file for environment-specific settings:

```yaml
# Production values example
global:
  environment: production
  domain: api.amos.ai

api:
  replicaCount: 3
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 15
    
resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

ingress:
  enabled: true
  hosts:
    - host: api.amos.ai
      paths:
        - path: /
          pathType: Prefix
          service: amos-api
  tls:
    - secretName: amos-tls
      hosts:
        - api.amos.ai

postgresql:
  persistence:
    size: 100Gi
  resources:
    limits:
      memory: 8Gi
```

### Install with Custom Values

```bash
helm install amos ./amos -n amos --create-namespace -f custom-values.yaml
```

### Upgrading

```bash
# Update dependencies
helm dependency update ./amos

# Upgrade deployment
helm upgrade amos ./amos -n amos -f custom-values.yaml

# Rollback if needed
helm rollback amos 1 -n amos
```

### Secrets Management

For production, use external secret management:

```bash
# Create secrets manually
kubectl create secret generic amos-db-credentials \
  --from-literal=password='secure-password' \
  -n amos

# Or use external-secrets operator with AWS/GCP/Azure
kubectl apply -f external-secrets.yaml
```

## Monitoring

Check deployment status:

```bash
# Pods
kubectl get pods -n amos

# Services
kubectl get svc -n amos

# HPA
kubectl get hpa -n amos

# Logs
kubectl logs -f deployment/amos-backend -n amos
```

## Scaling

Manual scaling:

```bash
# Scale backend
kubectl scale deployment amos-backend --replicas=5 -n amos

# Scale frontend
kubectl scale deployment amos-dashboard --replicas=3 -n amos
```

## Troubleshooting

```bash
# Check pod status
kubectl describe pod <pod-name> -n amos

# Check events
kubectl get events -n amos --sort-by=.lastTimestamp

# Exec into pod
kubectl exec -it <pod-name> -n amos -- /bin/sh

# Port forward for debugging
kubectl port-forward svc/amos-backend 8000:8000 -n amos
```

## Creator

**Trang Phan** - AMOS Brain v3.0.0
