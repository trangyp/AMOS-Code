# AMOS SuperBrain Security Guide v2.0.0

## Overview

This document describes the security architecture for the AMOS SuperBrain ecosystem, covering RBAC, Policy as Code, API security, and audit trails across all 12 governed systems.

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SECURITY LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  RBAC        │  │  OPA Policies│  │   API Security       │   │
│  │  (Roles)     │  │  (Rego)      │  │   (Middleware)       │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐           ┌────▼────┐           ┌────▼────┐
   │SuperBrain│           │  JWT    │           │ Audit   │
   │Governance│           │Tokens   │           │ Trail   │
   └─────────┘           └─────────┘           └─────────┘
```

---

## Role-Based Access Control (RBAC)

### Roles

| Role | Description | System Access |
|------|-------------|---------------|
| **admin** | Full system access | All 12 systems (full) |
| **operator** | Production operations | All 12 systems (execute) |
| **developer** | Development and testing | 6 core systems (execute) |
| **auditor** | Audit and compliance | 7 systems (view/export) |
| **readonly** | Read-only access | 4 systems (view) |

### Permission Categories

```python
from backend.security.rbac import Permission

# Cognitive systems
Permission.COGNITIVE_ROUTER_ROUTE
Permission.COGNITIVE_ROUTER_ADMIN

# Resilience systems  
Permission.RESILIENCE_CIRCUIT_CONTROL
Permission.RESILIENCE_CONFIG_MODIFY

# Knowledge systems
Permission.KNOWLEDGE_LOAD
Permission.KNOWLEDGE_QUERY
Permission.KNOWLEDGE_MODIFY

# Orchestration systems
Permission.ORCHESTRATOR_SUBMIT_TASK
Permission.ORCHESTRATOR_CANCEL_TASK
Permission.ORCHESTRATOR_ADMIN

# API systems
Permission.API_PRODUCTION_ACCESS
Permission.API_GRAPHQL_QUERY
Permission.API_GRAPHQL_MUTATE

# Agent systems
Permission.AGENT_MESSAGING_SEND
Permission.AGENT_OBSERVABILITY_VIEW

# UBI systems
Permission.UBI_ANALYSIS_RUN
Permission.UBI_RESULTS_VIEW

# Tool systems
Permission.TOOLS_EXECUTE
Permission.TOOLS_ADMIN

# Audit systems
Permission.AUDIT_EXPORT
Permission.AUDIT_VIEW

# Governance systems
Permission.GOVERNANCE_POLICY_MODIFY
Permission.GOVERNANCE_AUDIT_VIEW
Permission.SUPERBRAIN_ADMIN
```

---

## Policy as Code (OPA)

### Policy File
**Location:** `policies/superbrain_authz.rego`

### Policy Rules

| Rule | Description |
|------|-------------|
| `allow` | Main authorization decision |
| `has_permission` | Check if role has specific permission |
| `has_system_access` | Check system access at required level |
| `violates_time_restrictions` | Enforce business hours for production |
| `satisfies_audit_requirements` | Ensure audit compliance |
| `governance_compliant` | Full governance check |

### Time-based Restrictions

Production modifications restricted outside business hours (9 AM - 6 PM) for non-admin users.

```rego
violates_time_restrictions(input) if {
    input.resource.system in ["production_api", "superbrain"]
    input.action.access_level in ["control", "full"]
    input.user.role != "admin"
    input.timestamp.hour < 9
}
```

### Usage Example

```python
import requests

# Query OPA for authorization
def check_opa_auth(user, action, resource):
    input_data = {
        "input": {
            "user": user,
            "action": action,
            "resource": resource,
            "timestamp": {"hour": 14}  # 2 PM
        }
    }
    
    response = requests.post(
        "http://localhost:8181/v1/data/amos/superbrain/authz/allow",
        json=input_data
    )
    
    return response.json().get("result", False)

# Check authorization
allowed = check_opa_auth(
    user={"role": "operator", "authenticated": True},
    action={"permission": "cognitive_router.route", "access_level": "execute"},
    resource={"system": "cognitive_router"}
)
```

---

## API Security

### Middleware Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from backend.security.rbac import rbac, Role, Permission

app = FastAPI()

def get_current_user_role() -> Role:
    # Extract from JWT token
    return Role.OPERATOR

@app.post("/orchestrator/tasks")
@rbac.require_permission(
    Permission.ORCHESTRATOR_SUBMIT_TASK,
    get_role=get_current_user_role
)
async def submit_task(task: dict):
    return {"status": "submitted"}
```

### Security Headers

All API responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

---

## Audit Trail

### Security Events Logged

| Event Type | Fields |
|------------|--------|
| Authentication | user_id, timestamp, success/failure, source_ip |
| Authorization | user_id, permission, system, decision, reason |
| Access | user_id, resource, action, timestamp, result |
| Policy Violation | user_id, policy, violation_type, timestamp |

### Audit Storage

- **Location:** CloudWatch `/aws/amossuperbrain/{env}/audit`
- **Retention:** 365 days
- **Encryption:** KMS

### Audit Query

```python
from clawspring.amos_brain.audit_exporter import AuditExporter

exporter = AuditExporter()

# Query security events
security_events = exporter.query(
    domain="security",
    since="2026-04-01",
    event_types=["authorization_denied", "policy_violation"]
)
```

---

## Security Checklist

### Deployment

- [ ] OPA server deployed and configured
- [ ] Policies loaded: `superbrain_authz.rego`
- [ ] RBAC roles assigned to users
- [ ] JWT signing keys rotated
- [ ] Audit logging enabled
- [ ] CloudWatch alarms for security events

### Operations

- [ ] Monitor failed authorization attempts
- [ ] Review policy violations weekly
- [ ] Rotate credentials quarterly
- [ ] Audit role assignments monthly
- [ ] Test incident response procedures

---

## Incident Response

### Security Incident Types

| Severity | Examples | Response Time |
|----------|----------|---------------|
| Critical | Unauthorized admin access | Immediate |
| High | Multiple failed auth attempts | 1 hour |
| Medium | Policy violations | 4 hours |
| Low | Suspicious patterns | 24 hours |

### Response Procedure

1. **Detect** - CloudWatch alarms trigger
2. **Contain** - Revoke affected tokens/roles
3. **Investigate** - Query audit logs
4. **Recover** - Reset passwords, reissue tokens
5. **Review** - Update policies if needed

---

## Compliance

### Standards

| Standard | Coverage |
|----------|----------|
| SOC 2 | Audit trails, access controls |
| GDPR | Data access logging |
| HIPAA | PHI access controls (if applicable) |

### Audit Reports

Generate compliance reports:

```bash
# Generate access report
python scripts/generate_access_report.py --start-date 2026-04-01 --end-date 2026-04-30

# Export audit trail
make sb-audit-export ENV=prod
```

---

**Maintainer:** Trang Phan  
**Last Updated:** 2026-04-16  
**Version:** 2.0.0
