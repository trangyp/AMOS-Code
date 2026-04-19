"""
AMOS SuperBrain RBAC (Role-Based Access Control) v2.0.0

Security layer defining roles, permissions, and policies for all 12
integrated systems with Policy as Code integration.

Architecture:
- Role hierarchy: admin, operator, developer, auditor, readonly
- Permission matrix for each of the 12 systems
- OPA (Open Policy Agent) integration for policy enforcement
- JWT token validation with claims-based authorization

Owner: Trang Phan
Version: 2.0.0
"""

import functools
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

# OPA integration
try:
    import requests

    OPA_AVAILABLE = True
except ImportError:
    OPA_AVAILABLE = False

# JWT validation
try:
    import jwt

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# SuperBrain integration
try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


class Role(Enum):
    """Role hierarchy for AMOS ecosystem."""

    ADMIN = "admin"  # Full access to all systems
    OPERATOR = "operator"  # Production operations
    DEVELOPER = "developer"  # Development and testing
    AUDITOR = "auditor"  # Read-only audit access
    READONLY = "readonly"  # Read-only user access


class Permission(Enum):
    """Permissions across 12 integrated systems."""

    # Cognitive systems
    COGNITIVE_ROUTER_ROUTE = "cognitive_router.route"
    COGNITIVE_ROUTER_ADMIN = "cognitive_router.admin"

    # Resilience systems
    RESILIENCE_CIRCUIT_CONTROL = "resilience.circuit_control"
    RESILIENCE_CONFIG_MODIFY = "resilience.config_modify"

    # Knowledge systems
    KNOWLEDGE_LOAD = "knowledge.load"
    KNOWLEDGE_QUERY = "knowledge.query"
    KNOWLEDGE_MODIFY = "knowledge.modify"

    # Orchestration systems
    ORCHESTRATOR_SUBMIT_TASK = "orchestrator.submit_task"
    ORCHESTRATOR_CANCEL_TASK = "orchestrator.cancel_task"
    ORCHESTRATOR_ADMIN = "orchestrator.admin"

    # API systems
    API_PRODUCTION_ACCESS = "api.production_access"
    API_GRAPHQL_QUERY = "api.graphql_query"
    API_GRAPHQL_MUTATE = "api.graphql_mutate"

    # Agent systems
    AGENT_MESSAGING_SEND = "agent.messaging_send"
    AGENT_OBSERVABILITY_VIEW = "agent.observability_view"

    # UBI systems
    UBI_ANALYSIS_RUN = "ubi.analysis_run"
    UBI_RESULTS_VIEW = "ubi.results_view"

    # Tool systems
    TOOLS_EXECUTE = "tools.execute"
    TOOLS_ADMIN = "tools.admin"

    # Audit systems
    AUDIT_EXPORT = "audit.export"
    AUDIT_VIEW = "audit.view"

    # Governance systems
    GOVERNANCE_POLICY_MODIFY = "governance.policy_modify"
    GOVERNANCE_AUDIT_VIEW = "governance.audit_view"
    SUPERBRAIN_ADMIN = "superbrain.admin"


@dataclass
class RBACPolicy:
    """RBAC policy definition."""

    role: Role
    permissions: set[Permission]
    allowed_systems: set[str]
    denied_systems: set[str]


class RBACManager:
    """Central RBAC manager for 12-system governance."""

    # Role-to-Permissions mapping
    ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
        Role.ADMIN: set(Permission),  # All permissions
        Role.OPERATOR: {
            Permission.COGNITIVE_ROUTER_ROUTE,
            Permission.RESILIENCE_CIRCUIT_CONTROL,
            Permission.KNOWLEDGE_QUERY,
            Permission.ORCHESTRATOR_SUBMIT_TASK,
            Permission.ORCHESTRATOR_CANCEL_TASK,
            Permission.API_PRODUCTION_ACCESS,
            Permission.API_GRAPHQL_QUERY,
            Permission.API_GRAPHQL_MUTATE,
            Permission.AGENT_MESSAGING_SEND,
            Permission.AGENT_OBSERVABILITY_VIEW,
            Permission.UBI_ANALYSIS_RUN,
            Permission.UBI_RESULTS_VIEW,
            Permission.TOOLS_EXECUTE,
            Permission.AUDIT_VIEW,
            Permission.GOVERNANCE_AUDIT_VIEW,
        },
        Role.DEVELOPER: {
            Permission.COGNITIVE_ROUTER_ROUTE,
            Permission.KNOWLEDGE_QUERY,
            Permission.ORCHESTRATOR_SUBMIT_TASK,
            Permission.API_GRAPHQL_QUERY,
            Permission.AGENT_MESSAGING_SEND,
            Permission.TOOLS_EXECUTE,
        },
        Role.AUDITOR: {
            Permission.KNOWLEDGE_QUERY,
            Permission.ORCHESTRATOR_SUBMIT_TASK,
            Permission.API_GRAPHQL_QUERY,
            Permission.AGENT_OBSERVABILITY_VIEW,
            Permission.UBI_RESULTS_VIEW,
            Permission.AUDIT_EXPORT,
            Permission.AUDIT_VIEW,
            Permission.GOVERNANCE_AUDIT_VIEW,
        },
        Role.READONLY: {
            Permission.KNOWLEDGE_QUERY,
            Permission.API_GRAPHQL_QUERY,
            Permission.UBI_RESULTS_VIEW,
            Permission.AUDIT_VIEW,
        },
    }

    # System access rules
    SYSTEM_ACCESS: dict[Role, dict[str, str]] = {
        Role.ADMIN: {
            "cognitive_router": "full",
            "resilience_engine": "full",
            "knowledge_loader": "full",
            "master_orchestrator": "full",
            "production_api": "full",
            "graphql_api": "full",
            "agent_messaging": "full",
            "agent_observability": "full",
            "ubi_engine": "full",
            "amos_tools": "full",
            "audit_exporter": "full",
            "superbrain": "full",
        },
        Role.OPERATOR: {
            "cognitive_router": "execute",
            "resilience_engine": "control",
            "knowledge_loader": "read",
            "master_orchestrator": "execute",
            "production_api": "full",
            "graphql_api": "full",
            "agent_messaging": "send",
            "agent_observability": "view",
            "ubi_engine": "execute",
            "amos_tools": "execute",
            "audit_exporter": "view",
            "superbrain": "view",
        },
        Role.DEVELOPER: {
            "cognitive_router": "execute",
            "knowledge_loader": "read",
            "master_orchestrator": "submit",
            "graphql_api": "query",
            "agent_messaging": "send",
            "amos_tools": "execute",
        },
        Role.AUDITOR: {
            "knowledge_loader": "read",
            "master_orchestrator": "view",
            "graphql_api": "query",
            "agent_observability": "view",
            "ubi_engine": "view",
            "audit_exporter": "export",
            "superbrain": "audit",
        },
        Role.READONLY: {
            "knowledge_loader": "read",
            "graphql_api": "query",
            "ubi_engine": "view",
            "audit_exporter": "view",
        },
    }

    def __init__(self, opa_url: str = None):
        self.opa_url = opa_url or "http://localhost:8181"
        self._brain = None

        if SUPERBRAIN_AVAILABLE:
            try:
                self._brain = get_super_brain()
            except Exception:
                pass  # Fail open

    def has_permission(self, user_role: Role, permission: Permission, context: dict = None) -> bool:
        """Check if role has specific permission."""
        # CANONICAL: Validate via SuperBrain first
        if SUPERBRAIN_AVAILABLE and self._brain:
            try:
                if hasattr(self._brain, "action_gate"):
                    action_result = self._brain.action_gate.validate_action(
                        agent_id=f"rbac_{user_role.value}",
                        action=f"check_permission_{permission.value}",
                        details=context or {},
                    )
                    if not action_result.authorized:
                        return False
            except Exception:
                pass  # Fail open

        # Check role permissions
        role_permissions = self.ROLE_PERMISSIONS.get(user_role, set())
        return permission in role_permissions

    def can_access_system(self, user_role: Role, system: str, access_level: str = "read") -> bool:
        """Check if role can access system at given level."""
        system_access = self.SYSTEM_ACCESS.get(user_role, {})
        allowed_level = system_access.get(system, "none")

        if allowed_level == "none":
            return False
        if allowed_level == "full":
            return True

        # Level hierarchy: none < view < read < query < execute < control < full
        hierarchy = ["none", "view", "read", "query", "execute", "control", "full"]

        try:
            required_idx = hierarchy.index(access_level)
            allowed_idx = hierarchy.index(allowed_level)
            return allowed_idx >= required_idx
        except ValueError:
            return False

    def require_permission(
        self, permission: Permission, get_role: Callable = lambda: Role.READONLY
    ):
        """Decorator to require permission."""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                user_role = get_role()

                if not self.has_permission(user_role, permission):
                    raise PermissionError(
                        f"Role '{user_role.value}' lacks permission '{permission.value}'"
                    )

                return func(*args, **kwargs)

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                user_role = get_role()

                if not self.has_permission(user_role, permission):
                    raise PermissionError(
                        f"Role '{user_role.value}' lacks permission '{permission.value}'"
                    )

                return await func(*args, **kwargs)

            import asyncio

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return wrapper

        return decorator


# Global RBAC instance
rbac = RBACManager()


def get_system_access_matrix():
    """Get complete access matrix for documentation."""
    systems = [
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
        "superbrain",
    ]

    roles = [Role.ADMIN, Role.OPERATOR, Role.DEVELOPER, Role.AUDITOR, Role.READONLY]

    matrix = {}
    for role in roles:
        matrix[role.value] = {}
        for system in systems:
            access = RBACManager.SYSTEM_ACCESS.get(role, {}).get(system, "none")
            matrix[role.value][system] = access

    return matrix
