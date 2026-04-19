# AMOS Equation API Helm Chart

Production-ready Helm chart for deploying the AMOS Equation API on Kubernetes.

## Features

- **115+ Executable Equations** across 12 domains
- **Symbolic Computation** with SymPy integration
- **Redis Caching** for equation results
- **Auto-scaling** via HorizontalPodAutoscaler
- **Pod Disruption Budgets** for high availability
- **Network Policies** for security
- **Prometheus Monitoring** support
- **Ingress** with rate limiting and TLS

## Prerequisites

- Kubernetes 1.24+
- Helm 3.12+
- (Optional) Prometheus for monitoring
- (Optional) cert-manager for TLS certificates

## Installation

```bash
# Add the Helm repository (if published)
helm repo add amos https://charts.amos.io
helm repo update

# Install the chart
helm install amos-equation amos/amos-equation \
  --namespace amos \
  --create-namespace \
  --set image.tag=13.0.0
```

## Quick Start

```bash
# Install with default values
helm install amos-equation ./helm/amos-equation \
  --namespace amos \
  --create-namespace

# Check deployment status
kubectl get pods -n amos
kubectl get svc -n amos

# Port forward for local access
kubectl port-forward svc/amos-equation 8080:80 -n amos

# Test the API
curl http://localhost:8080/health
curl http://localhost:8080/equations
curl -X POST http://localhost:8080/compute \
  -H "Content-Type: application/json" \
  -d '{"equation": "kinetic_energy", "inputs": {"m": 10, "v": 5}}'
```

## Configuration

### Basic Configuration

```yaml
# values.yaml
replicaCount: 5

image:
  repository: my-registry/amos-equation
  tag: "13.0.0"

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 20
```

### Enabling Ingress

```yaml
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: api.amos.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: amos-equation-tls
      hosts:
        - api.amos.example.com
```

### Redis Caching

```yaml
redis:
  enabled: true
  architecture: standalone
  auth:
    enabled: true
    password: "your-redis-password"
  master:
    persistence:
      size: 5Gi
```

### Monitoring with Prometheus

```yaml
serviceMonitor:
  enabled: true
  namespace: monitoring
  labels:
    release: prometheus

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

## Values Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `3` |
| `image.repository` | Image repository | `amos/equation-api` |
| `image.tag` | Image tag | `13.0.0` |
| `resources.limits.cpu` | CPU limit | `1000m` |
| `resources.limits.memory` | Memory limit | `1Gi` |
| `autoscaling.enabled` | Enable HPA | `true` |
| `autoscaling.minReplicas` | Minimum replicas | `3` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |
| `redis.enabled` | Enable Redis | `true` |
| `ingress.enabled` | Enable Ingress | `false` |
| `serviceMonitor.enabled` | Enable Prometheus monitoring | `false` |
| `pdb.enabled` | Enable Pod Disruption Budget | `true` |
| `networkPolicy.enabled` | Enable Network Policy | `true` |

## Upgrading

```bash
# Upgrade the release
helm upgrade amos-equation ./helm/amos-equation \
  --namespace amos \
  --set image.tag=13.1.0

# Rollback if needed
helm rollback amos-equation -n amos
```

## Uninstallation

```bash
helm uninstall amos-equation -n amos
kubectl delete namespace amos
```

## Production Recommendations

1. **Resource Limits**: Set appropriate CPU/memory limits based on workload
2. **Pod Disruption Budget**: Keep at least 2 replicas available
3. **Network Policies**: Restrict traffic to necessary ports only
4. **Ingress TLS**: Always enable TLS for production
5. **Monitoring**: Enable Prometheus ServiceMonitor
6. **Redis**: Enable persistence for equation caching
7. **Anti-affinity**: Spread pods across nodes/zones

## Troubleshooting

```bash
# Check pod logs
kubectl logs -f deployment/amos-equation -n amos

# Check events
kubectl get events -n amos --sort-by='.lastTimestamp'

# Debug a specific pod
kubectl exec -it amos-equation-xxx -n amos -- /bin/sh

# Test equation computation
kubectl run test --rm -it --image=curlimages/curl -- \
  curl -X POST http://amos-equation/equations/compute \
  -H "Content-Type: application/json" \
  -d '{"equation": "sigmoid", "inputs": {"x": 1.0}}'
```

## License

MIT
