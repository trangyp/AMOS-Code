# AMOS SuperBrain Configuration & Feature Flags v2.0.0

## Overview

Dynamic configuration system with governance-controlled feature flags for all 12 integrated systems. Supports gradual rollouts, A/B testing, and emergency kill switches.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION LAYER                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │ Feature Flags    │  │ Redis Cache      │  │ Governance   │   │
│  │ (Dynamic)        │  │ (TTL: 1 hour)    │  │ Validation   │   │
│  └──────────────────┘  └──────────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐           ┌────▼────┐           ┌────▼────┐
   │Rollout  │           │ A/B     │           │Emergency│
   │Control  │           │Testing  │           │Kill     │
   │(0-100%) │           │         │           │Switch   │
   └─────────┘           └─────────┘           └─────────┘
```

---

## Feature Flags

### Governance Features

| Flag | Status | Rollout | Description |
|------|--------|---------|-------------|
| `superbrain_actiongate` | ✅ Enabled | 100% | ActionGate validation |
| `superbrain_audit_trail` | ✅ Enabled | 100% | Audit trail recording |

### Cognitive Features

| Flag | Status | Rollout | Description |
|------|--------|---------|-------------|
| `cognitive_router_v2` | ✅ Enabled | 100% | Cognitive Router v2.0 |
| `advanced_routing` | 🔄 Canary | 10% | ML-enhanced routing |

### Resilience Features

| Flag | Status | Rollout | Description |
|------|--------|---------|-------------|
| `circuit_breaker_enhanced` | ✅ Enabled | 100% | Enhanced circuit breaker |
| `auto_healing` | 🔄 Canary | 5% | Self-healing automation |

### Knowledge Features

| Flag | Status | Rollout | Description |
|------|--------|---------|-------------|
| `knowledge_realtime_sync` | ✅ Enabled | 100% | Real-time sync |
| `knowledge_graph_v2` | ⏸️ Disabled | 0% | Graph v2 (coming soon) |

### API Features

| Flag | Status | Rollout | Description |
|------|--------|---------|-------------|
| `graphql_subscriptions` | ✅ Enabled | 100% | Live subscriptions |
| `api_rate_limiting` | ✅ Enabled | 100% | Rate limiting |

### Observability Features

| Flag | Status | Rollout | Description |
|------|--------|---------|-------------|
| `opentelemetry_tracing` | ✅ Enabled | 100% | Distributed tracing |
| `advanced_metrics` | 🔄 Partial | 25% | Enhanced metrics |

---

## Usage

### Check Feature Status

```python
from backend.config.feature_flags import is_feature_enabled

# Check if feature is enabled
if is_feature_enabled("advanced_routing", user_id="user123", user_role="operator"):
    # Use advanced routing
    pass
else:
    # Use standard routing
    pass
```

### Enable/Disable Features

```python
from backend.config.feature_flags import enable_feature, disable_feature

# Enable feature (requires admin role)
enable_feature("advanced_routing", user_role="admin")

# Disable feature
disable_feature("advanced_routing", user_role="admin")
```

### Emergency Kill Switch

```python
from backend.config.feature_flags import emergency_stop

# Emergency stop for a system
emergency_stop("cognitive_router")
```

### Get All Flags

```python
from backend.config.feature_flags import config_manager

# Get all visible flags for role
flags = config_manager.get_all_flags(user_role="operator")
```

---

## Rollout Strategy

### Percentage-Based Rollout

Uses consistent hashing for deterministic user assignment:

```python
# User gets consistent experience based on user_id
hash_value = md5(f"{flag_name}:{user_id}")
user_percentage = (hash_value % 10000) / 100.0

if user_percentage <= rollout_percentage:
    feature_enabled = True
```

### Gradual Rollout Stages

| Stage | Percentage | Duration | Purpose |
|-------|------------|----------|---------|
| Canary | 5% | 1 day | Detect major issues |
| Limited | 10% | 2 days | Monitor metrics |
| Expanded | 25% | 3 days | Gather feedback |
| Full | 100% | Ongoing | Full rollout |

---

## Governance Integration

### Permission Checks

Feature flag changes require SuperBrain validation:

```python
# CANONICAL: Validate via SuperBrain
if flag.requires_governance:
    action_result = brain.action_gate.validate_action(
        agent_id="config_manager",
        action="modify_feature_flag",
        details={
            "flag_name": flag_name,
            "new_value": enabled,
            "user_role": user_role
        }
    )
```

### Role-Based Access

| Role | Flag Operations |
|------|-----------------|
| admin | Enable/disable any flag |
| operator | Enable non-governance flags |
| developer | View flags only |
| auditor | View flags only |
| readonly | View flags only |

---

## Redis Storage

### Key Format

```
feature_flag:{flag_name}
```

### Value Format

```json
{
  "enabled": true,
  "updated_at": "2026-04-16T18:30:00Z",
  "updated_by": "admin"
}
```

### TTL

- Standard flags: 1 hour
- Emergency kills: 5 minutes

---

## Emergency Procedures

### Kill Switch

Disable all features for a system immediately:

```bash
# Via Python
python -c "from backend.config.feature_flags import emergency_stop; emergency_stop('cognitive_router')"

# Via API
POST /admin/kill-switch
{
  "system": "cognitive_router",
  "reason": "performance_degradation"
}
```

### Recovery

Features automatically re-enable after TTL expires, or manual re-enable:

```python
# Re-enable after fix
enable_feature("cognitive_router_v2", user_role="admin")
```

---

## Configuration Management

### Environment-Specific Config

```python
# Development
config_manager = ConfigurationManager(
    redis_url="redis://localhost:6379/0"
)

# Production
config_manager = ConfigurationManager(
    redis_url="redis://prod-redis:6379/0"
)
```

### Dynamic Updates

Configuration updates propagate in real-time via Redis pub/sub:

```python
# Subscribe to config changes
redis_conn.subscribe("config:updates")

# Handle update
for message in redis_conn.listen():
    if message["type"] == "message":
        refresh_local_cache()
```

---

## Monitoring

### Metrics

| Metric | Description |
|--------|-------------|
| `feature_flag_checks` | Total flag checks |
| `feature_flag_changes` | Total flag modifications |
| `feature_rollout_percentage` | Current rollout % |
| `emergency_kills` | Emergency stop count |

### Alerts

```yaml
# CloudWatch alarm for emergency kills
EmergencyKillSwitch:
  MetricName: emergency_kills
  Threshold: 1
  EvaluationPeriods: 1
  AlarmActions:
    - SNS_Topic_Alerts
```

---

## Best Practices

### 1. Always Use Governance

```python
# Good - requires governance
@config_manager.require_governance
def enable_advanced_feature():
    pass

# Bad - bypasses governance
def enable_advanced_feature():
    flag.enabled = True  # Don't do this
```

### 2. Gradual Rollouts

```python
# Start with small percentage
flag = FeatureFlag(
    name="new_feature",
    enabled=True,
    rollout_percentage=5.0,  # Start small
    requires_governance=True
)
```

### 3. Emergency Preparedness

```python
# Always have kill switch ready
if error_rate > threshold:
    emergency_stop("affected_system")
```

---

**Maintainer:** Trang Phan  
**Last Updated:** 2026-04-16  
**Version:** 2.0.0
