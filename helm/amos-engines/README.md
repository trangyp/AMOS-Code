# AMOS Engines Helm Chart

Helm chart for deploying AMOS Engines (Temporal, Field, Safety, Integration) to Kubernetes.

## TL;DR

```bash
# Add Helm repository (if hosted)
helm repo add amos https://charts.amos.io
helm repo update

# Install the chart
helm install amos-engines amos/amos-engines

# Or install from local
helm install amos-engines ./helm/amos-engines
```

## Introduction

This Helm chart deploys the complete AMOS Engines infrastructure:
- **Temporal Engine**: Workflow orchestration and event scheduling
- **Field Dynamics Engine**: Lagrangian field simulation
- **Safety Engine**: Self-evolution code validation
- **Integration Engine**: Unified API layer

Optional dependencies:
- **Redis**: Caching and pub/sub (enabled by default)
- **Prometheus**: Metrics collection (enabled by default)

## Prerequisites

- Kubernetes 1.24+
- Helm 3.8+
- PV provisioner support in the underlying infrastructure
- Ingress controller (nginx recommended)

## Installing the Chart

### Basic Installation

```bash
helm install amos-engines ./helm/amos-engines
```

### Custom Configuration

```bash
# Create custom values file
cat > my-values.yaml << EOL
image:
  registry: my-registry.io
  repository: amos/engines
  tag: v2.1.0

temporal:
  replicaCount: 3
  autoscaling:
    maxReplicas: 15

field:
  config:
    gridSize: 128
    mass: 1.5
EOL

helm install amos-engines ./helm/amos-engines -f my-values.yaml
```

### Production Installation

```bash
helm install amos-engines ./helm/amos-engines \
  --namespace amos-production \
  --create-namespace \
  --set global.amos.environment=production \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=amos-engines.example.com
```

## Uninstalling the Chart

```bash
helm uninstall amos-engines
```

## Configuration

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.imageRegistry` | Global Docker image registry | `""` |
| `global.amos.logLevel` | Log level (DEBUG, INFO, WARN, ERROR) | `INFO` |
| `global.amos.environment` | Environment (development, staging, production) | `production` |

### Image Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.registry` | Image registry | `docker.io` |
| `image.repository` | Image repository | `amos/engines` |
| `image.tag` | Image tag | `v2.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |

### Temporal Engine Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `temporal.enabled` | Enable Temporal Engine | `true` |
| `temporal.replicaCount` | Number of replicas | `2` |
| `temporal.resources.limits.cpu` | CPU limit | `500m` |
| `temporal.resources.limits.memory` | Memory limit | `512Mi` |
| `temporal.autoscaling.enabled` | Enable autoscaling | `true` |
| `temporal.autoscaling.maxReplicas` | Maximum replicas | `10` |

### Field Dynamics Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `field.enabled` | Enable Field Engine | `true` |
| `field.replicaCount` | Number of replicas | `2` |
| `field.resources.limits.cpu` | CPU limit | `1000m` |
| `field.resources.limits.memory` | Memory limit | `1Gi` |
| `field.config.gridSize` | Default field grid size | `64` |
| `field.config.mass` | Field mass parameter | `1.0` |
| `field.config.coupling` | Field coupling | `0.1` |

### Safety Engine Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `safety.enabled` | Enable Safety Engine | `true` |
| `safety.replicaCount` | Number of replicas | `1` |

### Integration Engine Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `integration.enabled` | Enable Integration Engine | `true` |
| `integration.replicaCount` | Number of replicas | `2` |

### Ingress Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.annotations` | Ingress annotations | See values.yaml |
| `ingress.hosts` | List of hosts and paths | See values.yaml |
| `ingress.tls` | TLS configuration | `[]` |

### Autoscaling Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `temporal.autoscaling.enabled` | Enable HPA for Temporal | `true` |
| `temporal.autoscaling.minReplicas` | Minimum replicas | `2` |
| `temporal.autoscaling.maxReplicas` | Maximum replicas | `10` |
| `temporal.autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization | `70` |

### Security Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `podSecurityContext.runAsNonRoot` | Run as non-root user | `true` |
| `podSecurityContext.runAsUser` | User ID | `1000` |
| `securityContext.readOnlyRootFilesystem` | Read-only root filesystem | `true` |
| `securityContext.allowPrivilegeEscalation` | Allow privilege escalation | `false` |

## Dependencies

This chart includes the following subcharts:

### Redis (optional)

```yaml
redis:
  enabled: true
  architecture: standalone
  auth:
    enabled: false
```

### Prometheus (optional)

```yaml
prometheus:
  enabled: true
  server:
    persistentVolume:
      enabled: true
      size: 10Gi
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n amos-engines
kubectl describe pod <pod-name> -n amos-engines
```

### View Logs

```bash
# Temporal Engine
kubectl logs -f deployment/amos-engines-temporal-engine -n amos-engines

# Field Engine
kubectl logs -f deployment/amos-engines-field-engine -n amos-engines

# All engines
kubectl logs -f -l app.kubernetes.io/name=amos-engines -n amos-engines
```

### Port Forward for Local Testing

```bash
# API
kubectl port-forward svc/amos-engines-temporal-service 8000:8000 -n amos-engines

# Health check
kubectl port-forward svc/amos-engines-temporal-service 8080:8080 -n amos-engines

# Metrics
kubectl port-forward svc/amos-engines-temporal-service 9090:9090 -n amos-engines
```

### Helm Upgrade

```bash
helm upgrade amos-engines ./helm/amos-engines \
  --reuse-values \
  --set image.tag=v2.1.0
```

### Rollback

```bash
helm rollback amos-engines 1
```

## Development

### Lint Chart

```bash
helm lint ./helm/amos-engines
```

### Template Rendering

```bash
helm template amos-engines ./helm/amos-engines
```

### Dry Run Installation

```bash
helm install amos-engines ./helm/amos-engines --dry-run --debug
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Ingress (nginx)                       │
│  /temporal → Temporal Service                               │
│  /field    → Field Service                                  │
│  /safety   → Safety Service                                 │
│  /integration → Integration Service                         │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │Temporal │       │  Field  │       │ Safety  │
   │ Engine  │       │ Engine  │       │ Engine  │
   │ (2 pods)│       │ (2 pods)│       │ (1 pod) │
   └────┬────┘       └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Integration │
                    │   Engine    │
                    │  (2 pods)   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
         │  Redis  │  │Prometheus│  │ Grafana │
         │ (cache) │  │(metrics) │  │(dash)   │
         └─────────┘  └─────────┘  └─────────┘
```

## Support

For support, please refer to:
- AMOS Documentation: https://amos.io/docs
- GitHub Issues: https://github.com/amos-project/amos-engines/issues
- Helm Chart Issues: https://github.com/amos-project/amos-engines/issues?q=label:helm
