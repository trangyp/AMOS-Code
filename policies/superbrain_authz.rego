# AMOS SuperBrain Authorization Policies v2.0.0
#
# Open Policy Agent (OPA) policies for governing access to all 12 systems.
# These policies enforce RBAC, audit requirements, and operational constraints.
#
# Owner: Trang Phan
# Version: 2.0.0

package amos.superbrain.authz

import future.keywords.if
import future.keywords.in

# ============================================
# Default Deny
# ============================================
default allow := false

# ============================================
# Role Definitions
# ============================================
roles := {
    "admin": {
        "permissions": ["*"],
        "systems": ["*"],
        "access_level": "full"
    },
    "operator": {
        "permissions": [
            "cognitive_router.route",
            "resilience.circuit_control",
            "knowledge.query",
            "orchestrator.submit_task",
            "orchestrator.cancel_task",
            "api.production_access",
            "api.graphql_query",
            "api.graphql_mutate",
            "agent.messaging_send",
            "agent.observability_view",
            "ubi.analysis_run",
            "ubi.results_view",
            "tools.execute",
            "audit.view",
            "governance.audit_view"
        ],
        "systems": [
            "cognitive_router",
            "resilience_engine",
            "knowledge_loader",
            "master_orchestrator",
            "production_api",
            "graphql_api",
            "agent_messaging",
            "agent_observability",
            "ubi_engine",
            "amos_tools",
            "audit_exporter",
            "superbrain"
        ],
        "access_level": "execute"
    },
    "developer": {
        "permissions": [
            "cognitive_router.route",
            "knowledge.query",
            "orchestrator.submit_task",
            "api.graphql_query",
            "agent.messaging_send",
            "tools.execute"
        ],
        "systems": [
            "cognitive_router",
            "knowledge_loader",
            "master_orchestrator",
            "graphql_api",
            "agent_messaging",
            "amos_tools"
        ],
        "access_level": "execute"
    },
    "auditor": {
        "permissions": [
            "knowledge.query",
            "orchestrator.submit_task",
            "api.graphql_query",
            "agent.observability_view",
            "ubi.results_view",
            "audit.export",
            "audit.view",
            "governance.audit_view"
        ],
        "systems": [
            "knowledge_loader",
            "master_orchestrator",
            "graphql_api",
            "agent_observability",
            "ubi_engine",
            "audit_exporter",
            "superbrain"
        ],
        "access_level": "view"
    },
    "readonly": {
        "permissions": [
            "knowledge.query",
            "api.graphql_query",
            "ubi.results_view",
            "audit.view"
        ],
        "systems": [
            "knowledge_loader",
            "graphql_api",
            "ubi_engine",
            "audit_exporter"
        ],
        "access_level": "view"
    }
}

# ============================================
# System Access Levels Hierarchy
# ============================================
access_levels := ["none", "view", "read", "query", "execute", "control", "full"]

access_level_index[level] := i if {
    some i, l in access_levels
    l == level
}

can_access_at_level(required, allowed) if {
    access_level_index[allowed] >= access_level_index[required]
}

# ============================================
# Main Authorization Rule
# ============================================
allow if {
    # Input must have required fields
    input.user.role
    input.action.permission
    input.resource.system

    # Check role exists
    role_config := roles[input.user.role]

    # Check permission
    has_permission(role_config, input.action.permission)

    # Check system access
    has_system_access(role_config, input.resource.system, input.action.access_level)

    # Check time-based restrictions (business hours for production)
    not violates_time_restrictions(input)

    # Check audit requirements
    satisfies_audit_requirements(input)
}

# ============================================
# Permission Check
# ============================================
has_permission(role_config, permission) if {
    # Admin has all permissions
    "*" in role_config.permissions
}

has_permission(role_config, permission) if {
    # Check specific permission
    permission in role_config.permissions
}

# ============================================
# System Access Check
# ============================================
has_system_access(role_config, system, required_level) if {
    # Admin has access to all systems
    "*" in role_config.systems
}

has_system_access(role_config, system, required_level) if {
    # Check system is in allowed list
    system in role_config.systems

    # Check access level
    can_access_at_level(required_level, role_config.access_level)
}

# ============================================
# Time-based Restrictions
# ============================================
violates_time_restrictions(input) if {
    # Production modifications restricted during off-hours
    input.resource.system in ["production_api", "superbrain"]
    input.action.access_level in ["control", "full"]
    input.user.role != "admin"

    # Get current hour (0-23)
    hour := input.timestamp.hour

    # Outside business hours (9 AM - 6 PM)
    hour < 9
}

violates_time_restrictions(input) if {
    input.resource.system in ["production_api", "superbrain"]
    input.action.access_level in ["control", "full"]
    input.user.role != "admin"

    hour := input.timestamp.hour
    hour >= 18
}

# ============================================
# Audit Requirements
# ============================================
satisfies_audit_requirements(input) if {
    # All actions are auditable (always true)
    true
}

# ============================================
# Audit Decision Logging
# ============================================
audit_decision := {
    "timestamp": input.timestamp,
    "user_id": input.user.id,
    "role": input.user.role,
    "permission": input.action.permission,
    "system": input.resource.system,
    "access_level": input.action.access_level,
    "allowed": allow,
    "reason": decision_reason
}

decision_reason := "authorized" if {
    allow
}

decision_reason := "unauthorized_role" if {
    not input.user.role
    not allow
}

decision_reason := "missing_permission" if {
    input.user.role
    not roles[input.user.role]
    not allow
}

decision_reason := "system_not_allowed" if {
    input.user.role
    roles[input.user.role]
    not has_system_access(roles[input.user.role], input.resource.system, input.action.access_level)
    not allow
}

decision_reason := "time_restriction" if {
    input.user.role
    roles[input.user.role]
    has_system_access(roles[input.user.role], input.resource.system, input.action.access_level)
    violates_time_restrictions(input)
    not allow
}

# ============================================
# Governance Compliance Check
# ============================================
governance_compliant if {
    # Action must be allowed by policy
    allow

    # Action must satisfy audit requirements
    satisfies_audit_requirements(input)

    # User must have valid authentication
    input.user.authenticated

    # Token must not be expired
    not input.user.token_expired
}

# ============================================
# Deny Messages
# ============================================
deny[msg] {
    not input.user.role
    msg := "Missing user role"
}

deny[msg] {
    input.user.role
    not roles[input.user.role]
    msg := sprintf("Invalid role: %s", [input.user.role])
}

deny[msg] {
    input.user.role
    roles[input.user.role]
    not has_permission(roles[input.user.role], input.action.permission)
    msg := sprintf("Role '%s' lacks permission '%s'", [input.user.role, input.action.permission])
}

deny[msg] {
    input.user.role
    roles[input.user.role]
    not has_system_access(roles[input.user.role], input.resource.system, input.action.access_level)
    msg := sprintf("Role '%s' cannot access system '%s' at level '%s'", [input.user.role, input.resource.system, input.action.access_level])
}

deny[msg] {
    violates_time_restrictions(input)
    msg := "Action restricted outside business hours (9 AM - 6 PM) for non-admin users"
}

deny[msg] {
    input.user.token_expired
    msg := "Authentication token expired"
}

# ============================================
# SuperBrain Governance Integration
# ============================================
superbrain_authorized if {
    # Check with SuperBrain if available
    input.superbrain_available
    input.superbrain_authorized
}

superbrain_authorized if {
    # Fail open if SuperBrain unavailable
    not input.superbrain_available
}

# Final authorization requires both policy and SuperBrain (if available)
fully_authorized if {
    allow
    superbrain_authorized
}
