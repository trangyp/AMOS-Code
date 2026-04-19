# AMOS GitOps Platform v2.10.0

Production-grade GitOps continuous delivery for AMOS using ArgoCD.

## Overview

This directory contains ArgoCD manifests for declarative, GitOps-based deployment of AMOS across multiple environments.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GITOPS ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Git Repository (Source of Truth)                               │
│  ├─ k8s/amos/          (Helm chart)                             │
│  ├─ gitops/apps/       (ArgoCD Applications)                    │
│  ├─ gitops/appsets/    (Multi-cluster ApplicationSets)          │
│  ├─ gitops/environments/ (dev, staging, prod values)              │
│  └─ gitops/progressive/ (Canary/Blue-green configs)              │
│                                                                  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    ArgoCD Server                          │  │
│  │  ├─ API Server                                            │  │
│  │  ├─ Web UI (argocd.amos.ai)                              │  │
│  │  ├─ Application Controller                               │  │
│  │  └─ Repo Server                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Kubernetes Clusters                        │  │
│  │  ├─ Dev Cluster     (amos-dev namespace)                │  │
│  │  ├─ Staging Cluster (amos-staging namespace)            │  │
│  │  └─ Prod Cluster    (amos-prod namespace)               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install ArgoCD

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd

# Port forward for access
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial password
argocd admin initial-password -n argocd
```

### 2. Configure ArgoCD CLI

```bash
# Login
argocd login localhost:8080

# Add repository
argocd repo add https://github.com/amos/amos.git
```

### 3. Deploy AMOS Applications

```bash
# Apply Application manifests
kubectl apply -f gitops/apps/amos-core.yaml
kubectl apply -f gitops/appsets/amos-multicluster.yaml

# Check status
argocd app list
```

## Directory Structure

```
gitops/
├── apps/                    # ArgoCD Applications
│   ├── amos-core.yaml      # Main AMOS application
│   └── amos-monitoring.yaml # Monitoring stack
├── appsets/                 # ApplicationSets (multi-cluster)
│   └── amos-multicluster.yaml
├── environments/            # Environment-specific values
│   ├── dev/values.yaml
│   ├── staging/values.yaml
│   └── prod/values.yaml
├── progressive/             # Progressive delivery configs
│   └── canary-api.yaml
└── notifications/           # Notification configs
    └── slack.yaml
```

## Features

### ✅ Automated Sync
- Drift detection and auto-healing
- Self-healing on configuration changes
- Prune resources not in git

### ✅ Progressive Delivery
- Canary deployments with Flagger
- Automated promotion/rollback
- A/B testing support

### ✅ Multi-Environment
- Dev: Single replica, no autoscaling
- Staging: HA with autoscaling
- Prod: Full production setup with canary

### ✅ Notifications
- Slack integration
- Webhook support
- Email notifications

### ✅ Security
- SSO integration (OIDC, SAML)
- RBAC policies
- Resource finalizers

## Environments

| Environment | Namespace | Replicas | Autoscaling | Canary |
|-------------|-----------|----------|-------------|--------|
| Dev | amos-dev | 1 | No | No |
| Staging | amos-staging | 2-5 | Yes | No |
| Production | amos-prod | 3-20 | Yes | Yes |

## Progressive Delivery

### Canary Deployment Flow

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  v1.0   │ → │ 10% v2  │ → │ 25% v2  │ → │ 50% v2  │ → │ 100% v2 │
│  100%   │   │ 90% v1  │   │ 75% v1  │   │ 50% v1  │   │  0% v1  │
└─────────┘   └─────────┘   └─────────┘   └─────────┘
     ↑                                            
  Deploy                                          
  v2.0                                           
```

### Automated Rollback

If success rate drops below 99% or error rate exceeds 1%, Flagger automatically rolls back to the previous version.

## Monitoring

Access ArgoCD UI:

```bash
# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Open browser
open https://localhost:8080

# Login with admin/initial-password
```

## Best Practices

### 1. Git Workflow

```
feature-branch → main → tag → deploy
     ↓              ↓      ↓        ↓
   PR review    CI tests  Version  ArgoCD sync
```

### 2. Deployment Strategy

- **Dev**: Direct push to main
- **Staging**: Tag-based deployment
- **Production**: PR-based with canary analysis

### 3. Rollback

```bash
# Rollback via ArgoCD
argocd app rollback amos-prod 1

# Or via Git
git revert HEAD
git push origin main
```

## Troubleshooting

### Check Sync Status

```bash
argocd app get amos-prod
```

### View Events

```bash
argocd app logs amos-prod
```

### Force Sync

```bash
argocd app sync amos-prod
```

### Check Resource Health

```bash
kubectl get applications -n argocd
kubectl describe application amos-prod -n argocd
```

## References

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Flagger Documentation](https://flagger.app/)
- [GitOps Best Practices](https://www.gitops.tech/)

---

**Created by Trang Phan** - AMOS v2.10.0
