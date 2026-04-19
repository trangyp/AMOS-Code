# AMOS SuperBrain Multi-tenancy v2.0.0

## Overview

Tenant isolation, resource quotas, and billing integration for all 12 systems. Supports pooled and silo deployment models with SuperBrain governance.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 MULTI-TENANCY LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Tenant     │  │   Resource   │  │   Usage            │   │
│  │   Context    │  │   Quotas     │  │   Tracking         │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐           ┌────▼────┐           ┌────▼────┐
   │Pooled   │           │Silo     │           │Bridge   │
   │Resources│           │Resources│           │Hybrid   │
   └─────────┘           └─────────┘           └─────────┘
```

---

## Tenant Tiers

| Tier | Description |
|------|-------------|
| **FREE** | Limited resources, evaluation tier |
| **BASIC** | Standard resources for small teams |
| **PROFESSIONAL** | Enhanced resources for growing teams |
| **ENTERPRISE** | Unlimited resources for large organizations |

---

## Resource Quotas by Tier

| Resource | FREE | BASIC | PROFESSIONAL | ENTERPRISE |
|----------|------|-------|--------------|------------|
| Requests/min | 20 | 100 | 500 | 10,000 |
| Storage (MB) | 100 | 1,000 | 10,000 | 1,000,000 |
| Compute hours/month | 10 | 100 | 1,000 | 10,000 |
| Concurrent jobs | 2 | 5 | 20 | 100 |
| Max users | 1 | 10 | 50 | 1,000 |
| API keys | 1 | 5 | 20 | 100 |
| Webhooks | 1 | 3 | 10 | 50 |

---

## Deployment Models

| Model | Description | Use Case |
|-------|-------------|----------|
| **POOLED** | Shared resources across tenants | Cost-efficient, standard isolation |
| **SILO** | Dedicated resources per tenant | Maximum isolation, compliance |
| **BRIDGE** | Hybrid approach | Flexible, gradual migration |

---

## Usage

### Creating a Tenant

```python
from backend.tenancy.multi_tenant import create_tenant, TenantTier

# Create basic tenant
tenant_id = create_tenant(
    name="Acme Corp",
    tier="basic",
    deployment_model="pooled",
    admin_email="admin@acme.com"
)

# Create enterprise tenant
tenant_id = create_tenant(
    name="Enterprise Inc",
    tier="enterprise",
    deployment_model="silo",
    admin_email="admin@enterprise.com"
)
```

### Using Tenant Context

```python
from backend.tenancy.multi_tenant import tenant_context, set_current_tenant

# Method 1: Context manager
with tenant_context("tenant-123"):
    # All operations are scoped to tenant-123
    result = process_data()

# Method 2: Direct set
set_current_tenant("tenant-123")
# ... do work ...
```

### Checking Resource Quotas

```python
from backend.tenancy.multi_tenant import check_quota, record_tenant_usage

# Check if quota available
allowed, reason = check_quota("requests_per_minute", amount=1)
if not allowed:
    print(f"Quota exceeded: {reason}")
    return

# Record usage
record_tenant_usage("requests", amount=1, metadata={"endpoint": "/api/v1/data"})
```

### Getting Tenant Statistics

```python
from backend.tenancy.multi_tenant import tenant_manager

stats = tenant_manager.get_tenant_stats("tenant-123")
print(f"Tier: {stats['tier']}")
print(f"Storage used: {stats['usage']['storage_used_mb']}MB")
print(f"Storage utilization: {stats['utilization']['storage']:.1f}%")
```

---

## Tenant Data Isolation

All tenant data is prefixed with tenant ID:

```python
from backend.tenancy.multi_tenant import get_tenant_data_prefix

prefix = get_tenant_data_prefix("tenant-123")
# Returns: "tenant:tenant-123:data:"

# Store tenant-specific data
redis.set(f"{prefix}user:1", user_data)
redis.set(f"{prefix}config:app", config_data)
```

---

## Upgrading Tenant Tier

```python
from backend.tenancy.multi_tenant import tenant_manager, TenantTier

success = tenant_manager.upgrade_tenant(
    tenant_id="tenant-123",
    new_tier=TenantTier.PROFESSIONAL
)
```

---

## Suspending a Tenant

```python
from backend.tenancy.multi_tenant import tenant_manager

success = tenant_manager.suspend_tenant(
    tenant_id="tenant-123",
    reason="Payment overdue"
)
```

---

## Integration with Other Systems

### API Gateway

The API Gateway automatically extracts tenant context from JWT tokens:

```python
# JWT payload includes tenant_id
{
  "sub": "user-123",
  "tenant_id": "tenant-abc",
  "role": "admin"
}
```

### Task Queue

Jobs are automatically tagged with tenant context:

```python
from backend.workers.task_queue import submit_task

# Tenant context is propagated to job
with tenant_context("tenant-123"):
    job_id = submit_task(
        task_name="process_data",
        payload={"data": "large_dataset"}
    )
```

### Data Pipeline

Tenant usage events are published to the streaming pipeline:
- `tenant_created`
- `tenant_upgraded`
- `tenant_suspended`
- `tenant_usage`

---

## Monitoring

### Tenant Usage Metrics

| Metric | Description |
|--------|-------------|
| `requests_this_minute` | Current minute request count |
| `requests_today` | Daily request count |
| `storage_used_mb` | Storage consumption |
| `compute_hours_this_month` | Monthly compute usage |
| `active_jobs` | Currently running jobs |

### Quota Utilization

```python
stats = tenant_manager.get_tenant_stats(tenant_id)

# Alert if utilization > 80%
if stats['utilization']['storage'] > 80:
    alert_tenant_admin(tenant_id, "Storage quota nearly full")
```

---

## Best Practices

### 1. Always Use Tenant Context

```python
# Good - explicit tenant context
with tenant_context(tenant_id):
    process_data()

# Bad - no isolation
process_data()  # Accesses global/default data
```

### 2. Check Quotas Before Heavy Operations

```python
# Check before processing
allowed, _ = check_quota("compute_hours", estimated_hours)
if not allowed:
    return {"error": "Quota exceeded"}

# Process data
result = heavy_computation()
record_tenant_usage("compute_hours", actual_hours)
```

### 3. Handle Suspended Tenants

```python
tenant = tenant_manager.get_tenant(tenant_id)
if tenant.status != "active":
    return {"error": f"Tenant is {tenant.status}"}
```

---

**Maintainer:** Trang Phan  
**Last Updated:** 2026-04-16  
**Version:** 2.0.0
