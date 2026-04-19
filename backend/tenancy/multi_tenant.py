"""
AMOS SuperBrain Multi-tenancy & Resource Management v2.0.0

Tenant isolation, resource quotas, and billing integration for all 12 systems.
Supports pooled and silo deployment models with SuperBrain governance.

Architecture:
- Tenant context propagation across all requests
- Resource quotas and limits per tenant
- Usage tracking for billing
- Tenant-aware data partitioning
- SuperBrain governance on tenant operations

Owner: Trang Phan
Version: 2.0.0
"""


import hashlib
import json
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any

# Redis for tenant data
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# SuperBrain integration
try:
    from amos_brain import get_super_brain
    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

# Import existing modules
try:
    from backend.data_pipeline.streaming import publish_event
from typing import Set
from typing import Dict, List, Optional, Tuple
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False


class TenantTier(Enum):
    """Tenant subscription tiers."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class DeploymentModel(Enum):
    """Tenant deployment models."""
    POOLED = "pooled"  # Shared resources
    SILO = "silo"  # Dedicated resources
    BRIDGE = "bridge"  # Hybrid


@dataclass
class ResourceQuota:
    """Resource quota definition."""
    max_requests_per_minute: int = 100
    max_storage_mb: int = 1000
    max_compute_hours_per_month: int = 100
    max_concurrent_jobs: int = 5
    max_users: int = 10
    max_api_keys: int = 5
    max_webhooks: int = 3


@dataclass
class Tenant:
    """Tenant definition with resource management."""
    tenant_id: str
    name: str
    tier: TenantTier = TenantTier.BASIC
    deployment_model: DeploymentModel = DeploymentModel.POOLED
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "active"  # active, suspended, deleted
    quota: ResourceQuota = field(default_factory=ResourceQuota)
    usage: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    admin_user_ids: List[str] = field(default_factory=list)
    api_keys: List[str] = field(default_factory=list)
    webhook_endpoints: List[str] = field(default_factory=list)


@dataclass
class TenantUsage:
    """Tenant usage tracking."""
    tenant_id: str
    requests_this_minute: int = 0
    requests_today: int = 0
    storage_used_mb: int = 0
    compute_hours_this_month: float = 0.0
    active_jobs: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TenantContext:
    """Thread-local tenant context."""
    _local = threading.local()

    @classmethod
    def get_current_tenant(cls) -> str :
        """Get current tenant ID from thread-local storage."""
        return getattr(cls._local, "tenant_id", None)

    @classmethod
    def set_current_tenant(cls, tenant_id: str):
        """Set current tenant ID in thread-local storage."""
        cls._local.tenant_id = tenant_id

    @classmethod
    def clear(cls):
        """Clear tenant context."""
        cls._local.tenant_id = None


@contextmanager
def tenant_context(tenant_id: str):
    """Context manager for tenant context."""
    TenantContext.set_current_tenant(tenant_id)
    try:
        yield
    finally:
        TenantContext.clear()


class MultiTenantManager:
    """Central multi-tenancy manager with SuperBrain governance."""

    # Default quotas by tier
    DEFAULT_QUOTAS: dict[TenantTier, ResourceQuota] = {
        TenantTier.FREE: ResourceQuota(
            max_requests_per_minute=20,
            max_storage_mb=100,
            max_compute_hours_per_month=10,
            max_concurrent_jobs=2,
            max_users=1,
            max_api_keys=1,
            max_webhooks=1
        ),
        TenantTier.BASIC: ResourceQuota(
            max_requests_per_minute=100,
            max_storage_mb=1000,
            max_compute_hours_per_month=100,
            max_concurrent_jobs=5,
            max_users=10,
            max_api_keys=5,
            max_webhooks=3
        ),
        TenantTier.PROFESSIONAL: ResourceQuota(
            max_requests_per_minute=500,
            max_storage_mb=10000,
            max_compute_hours_per_month=1000,
            max_concurrent_jobs=20,
            max_users=50,
            max_api_keys=20,
            max_webhooks=10
        ),
        TenantTier.ENTERPRISE: ResourceQuota(
            max_requests_per_minute=10000,
            max_storage_mb=1000000,
            max_compute_hours_per_month=10000,
            max_concurrent_jobs=100,
            max_users=1000,
            max_api_keys=100,
            max_webhooks=50
        )
    }

    def __init__(self, redis_url: str  = None):
        self.redis_url = redis_url or "redis://localhost:6379/4"
        self._redis: redis.Redis  = None
        self._brain = None

        # Initialize connections
        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
                self._redis.ping()
            except Exception:
                self._redis = None

        if SUPERBRAIN_AVAILABLE:
            try:
                self._brain = get_super_brain()
            except Exception:
                pass

    def _get_tenant_key(self, tenant_id: str) -> str:
        """Get Redis key for tenant data."""
        return f"tenant:{tenant_id}"

    def _get_usage_key(self, tenant_id: str) -> str:
        """Get Redis key for tenant usage."""
        return f"tenant:{tenant_id}:usage"

    def create_tenant(
        self,
        name: str,
        tier: TenantTier = TenantTier.BASIC,
        deployment_model: DeploymentModel = DeploymentModel.POOLED,
        admin_email: str  = None
    ) -> str :
        """Create new tenant with SuperBrain governance."""
        # CANONICAL: Validate via SuperBrain
        if SUPERBRAIN_AVAILABLE and self._brain:
            try:
                if hasattr(self._brain, 'action_gate'):
                    action_result = self._brain.action_gate.validate_action(
                        agent_id="multi_tenant",
                        action="create_tenant",
                        details={
                            "name": name,
                            "tier": tier.value,
                            "deployment_model": deployment_model.value
                        }
                    )
                    if not action_result.authorized:
                        return None
            except Exception:
                pass  # Fail open

        # Generate tenant ID
        tenant_id = hashlib.sha256(
            f"{name}:{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:16]

        # Get quota for tier
        quota = self.DEFAULT_QUOTAS.get(tier, self.DEFAULT_QUOTAS[TenantTier.BASIC])

        # Create tenant
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            tier=tier,
            deployment_model=deployment_model,
            quota=quota,
            admin_user_ids=[admin_email] if admin_email else []
        )

        # Store in Redis
        if self._redis:
            try:
                self._redis.setex(
                    self._get_tenant_key(tenant_id),
                    86400 * 30,  # 30 day TTL
                    json.dumps(tenant.__dict__, default=str)
                )

                # Initialize usage tracking
                usage = TenantUsage(tenant_id=tenant_id)
                self._redis.setex(
                    self._get_usage_key(tenant_id),
                    86400,
                    json.dumps(usage.__dict__, default=str)
                )

                # Publish event
                if STREAMING_AVAILABLE:
                    publish_event(
                        event_type="tenant_created",
                        source_system="multi_tenant",
                        payload={
                            "tenant_id": tenant_id,
                            "name": name,
                            "tier": tier.value,
                            "deployment_model": deployment_model.value
                        },
                        requires_governance=False
                    )

                return tenant_id
            except Exception:
                pass

        return None

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        if not self._redis:
            return None

        try:
            data = self._redis.get(self._get_tenant_key(tenant_id))
            if data:
                tenant_dict = json.loads(data)
                tenant_dict["tier"] = TenantTier(tenant_dict.get("tier", "basic"))
                tenant_dict["deployment_model"] = DeploymentModel(
                    tenant_dict.get("deployment_model", "pooled")
                )
                tenant_dict["quota"] = ResourceQuota(**tenant_dict.get("quota", {}))
                return Tenant(**tenant_dict)
        except Exception:
            pass

        return None

    def check_resource_quota(
        self,
        tenant_id: str,
        resource_type: str,
        requested_amount: int = 1
    ) -> Tuple[bool, str ]:
        """Check if tenant has available resource quota."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False, "Tenant not found"

        if tenant.status != "active":
            return False, f"Tenant is {tenant.status}"

        # Get current usage
        usage = self._get_usage(tenant_id)
        if not usage:
            return False, "Usage data not available"

        quota = tenant.quota

        # Check specific resource type
        if resource_type == "requests_per_minute":
            if usage.requests_this_minute + requested_amount > quota.max_requests_per_minute:
                return False, f"Rate limit exceeded: {quota.max_requests_per_minute}/min"

        elif resource_type == "storage_mb":
            if usage.storage_used_mb + requested_amount > quota.max_storage_mb:
                return False, f"Storage quota exceeded: {quota.max_storage_mb}MB"

        elif resource_type == "concurrent_jobs":
            if usage.active_jobs + requested_amount > quota.max_concurrent_jobs:
                return False, f"Concurrent job limit exceeded: {quota.max_concurrent_jobs}"

        elif resource_type == "users":
            current_users = len(tenant.admin_user_ids)
            if current_users + requested_amount > quota.max_users:
                return False, f"User limit exceeded: {quota.max_users}"

        elif resource_type == "api_keys":
            if len(tenant.api_keys) + requested_amount > quota.max_api_keys:
                return False, f"API key limit exceeded: {quota.max_api_keys}"

        return True, None

    def _get_usage(self, tenant_id: str) -> Optional[TenantUsage]:
        """Get tenant usage data."""
        if not self._redis:
            return None

        try:
            data = self._redis.get(self._get_usage_key(tenant_id))
            if data:
                usage_dict = json.loads(data)
                return TenantUsage(**usage_dict)
        except Exception:
            pass

        return None

    def record_usage(
        self,
        tenant_id: str,
        resource_type: str,
        amount: int = 1,
        metadata: dict  = None
    ) -> bool:
        """Record resource usage for tenant."""
        if not self._redis:
            return False

        try:
            usage_key = self._get_usage_key(tenant_id)
            data = self._redis.get(usage_key)

            if data:
                usage_dict = json.loads(data)
            else:
                usage_dict = {"tenant_id": tenant_id}

            # Update usage based on resource type
            if resource_type == "requests":
                usage_dict["requests_this_minute"] = usage_dict.get("requests_this_minute", 0) + amount
                usage_dict["requests_today"] = usage_dict.get("requests_today", 0) + amount

            elif resource_type == "storage_mb":
                usage_dict["storage_used_mb"] = usage_dict.get("storage_used_mb", 0) + amount

            elif resource_type == "compute_hours":
                usage_dict["compute_hours_this_month"] = usage_dict.get("compute_hours_this_month", 0.0) + amount

            elif resource_type == "active_jobs":
                usage_dict["active_jobs"] = usage_dict.get("active_jobs", 0) + amount

            usage_dict["last_updated"] = datetime.now(timezone.utc).isoformat()

            # Store updated usage
            self._redis.setex(usage_key, 86400, json.dumps(usage_dict))

            # Publish usage event
            if STREAMING_AVAILABLE:
                publish_event(
                    event_type="tenant_usage",
                    source_system="multi_tenant",
                    payload={
                        "tenant_id": tenant_id,
                        "resource_type": resource_type,
                        "amount": amount,
                        "metadata": metadata or {}
                    },
                    requires_governance=False
                )

            return True
        except Exception:
            pass

        return False

    def get_tenant_data_prefix(self, tenant_id: str) -> str:
        """Get data key prefix for tenant isolation."""
        return f"tenant:{tenant_id}:data:"

    def is_tenant_data_key(self, key: str, tenant_id: str) -> bool:
        """Check if key belongs to tenant."""
        return key.startswith(self.get_tenant_data_prefix(tenant_id))

    def upgrade_tier(
        self,
        tenant_id: str,
        new_tier: TenantTier
    ) -> bool:
        """Upgrade tenant to new tier."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False

        # CANONICAL: Validate via SuperBrain
        if SUPERBRAIN_AVAILABLE and self._brain:
            try:
                if hasattr(self._brain, 'action_gate'):
                    action_result = self._brain.action_gate.validate_action(
                        agent_id="multi_tenant",
                        action="upgrade_tier",
                        details={
                            "tenant_id": tenant_id,
                            "old_tier": tenant.tier.value,
                            "new_tier": new_tier.value
                        }
                    )
                    if not action_result.authorized:
                        return False
            except Exception:
                pass

        # Update tier and quota
        tenant.tier = new_tier
        tenant.quota = self.DEFAULT_QUOTAS.get(new_tier, tenant.quota)

        # Store updated tenant
        if self._redis:
            try:
                self._redis.setex(
                    self._get_tenant_key(tenant_id),
                    86400 * 30,
                    json.dumps(tenant.__dict__, default=str)
                )

                # Publish event
                if STREAMING_AVAILABLE:
                    publish_event(
                        event_type="tenant_upgraded",
                        source_system="multi_tenant",
                        payload={
                            "tenant_id": tenant_id,
                            "new_tier": new_tier.value
                        },
                        requires_governance=False
                    )

                return True
            except Exception:
                pass

        return False

    def suspend_tenant(self, tenant_id: str, reason: str) -> bool:
        """Suspend tenant account."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False

        tenant.status = "suspended"

        if self._redis:
            try:
                self._redis.setex(
                    self._get_tenant_key(tenant_id),
                    86400 * 30,
                    json.dumps(tenant.__dict__, default=str)
                )

                # Publish event
                if STREAMING_AVAILABLE:
                    publish_event(
                        event_type="tenant_suspended",
                        source_system="multi_tenant",
                        payload={
                            "tenant_id": tenant_id,
                            "reason": reason
                        },
                        requires_governance=True
                    )

                return True
            except Exception:
                pass

        return False

    def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive tenant statistics."""
        tenant = self.get_tenant(tenant_id)
        usage = self._get_usage(tenant_id)

        if not tenant:
            return {"error": "Tenant not found"}

        quota = tenant.quota

        return {
            "tenant_id": tenant_id,
            "name": tenant.name,
            "tier": tenant.tier.value,
            "status": tenant.status,
            "deployment_model": tenant.deployment_model.value,
            "quotas": {
                "max_requests_per_minute": quota.max_requests_per_minute,
                "max_storage_mb": quota.max_storage_mb,
                "max_compute_hours_per_month": quota.max_compute_hours_per_month,
                "max_concurrent_jobs": quota.max_concurrent_jobs,
                "max_users": quota.max_users,
                "max_api_keys": quota.max_api_keys,
                "max_webhooks": quota.max_webhooks
            },
            "usage": {
                "requests_this_minute": usage.requests_this_minute if usage else 0,
                "requests_today": usage.requests_today if usage else 0,
                "storage_used_mb": usage.storage_used_mb if usage else 0,
                "compute_hours_this_month": usage.compute_hours_this_month if usage else 0.0,
                "active_jobs": usage.active_jobs if usage else 0
            } if usage else {},
            "utilization": {
                "requests": (usage.requests_this_minute / quota.max_requests_per_minute * 100) if usage else 0,
                "storage": (usage.storage_used_mb / quota.max_storage_mb * 100) if usage else 0,
                "compute": (usage.compute_hours_this_month / quota.max_compute_hours_per_month * 100) if usage else 0
            } if usage else {}
        }


# Global multi-tenant manager
tenant_manager = MultiTenantManager()


# Convenience functions
def create_tenant(
    name: str,
    tier: str = "basic",
    deployment_model: str = "pooled",
    admin_email: str  = None
) -> str :
    """Create new tenant."""
    tier_enum = TenantTier(tier)
    model_enum = DeploymentModel(deployment_model)
    return tenant_manager.create_tenant(name, tier_enum, model_enum, admin_email)


def get_current_tenant() -> str :
    """Get current tenant from context."""
    return TenantContext.get_current_tenant()


def set_current_tenant(tenant_id: str):
    """Set current tenant in context."""
    TenantContext.set_current_tenant(tenant_id)


def check_quota(resource_type: str, amount: int = 1) -> Tuple[bool, str ]:
    """Check quota for current tenant."""
    tenant_id = get_current_tenant()
    if not tenant_id:
        return False, "No tenant context"
    return tenant_manager.check_resource_quota(tenant_id, resource_type, amount)


def record_tenant_usage(resource_type: str, amount: int = 1, metadata: dict  = None) -> bool:
    """Record usage for current tenant."""
    tenant_id = get_current_tenant()
    if not tenant_id:
        return False
    return tenant_manager.record_usage(tenant_id, resource_type, amount, metadata)


def get_tenant_data_prefix(tenant_id: str  = None) -> str:
    """Get data prefix for tenant."""
    tenant_id = tenant_id or get_current_tenant()
    if not tenant_id:
        return ""
    return tenant_manager.get_tenant_data_prefix(tenant_id)
