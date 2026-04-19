"""
AMOS SuperBrain Feature Flags & Configuration v2.0.0

Dynamic configuration and feature flag system with SuperBrain governance.
Supports gradual rollouts, A/B testing, and emergency kill switches.

Architecture:
- Redis-backed configuration store
- Governance-controlled feature toggles
- Real-time configuration updates
- Environment-specific overrides

Owner: Trang Phan
Version: 2.0.0
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any

# Redis integration
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
    get_super_brain = None


@dataclass
class FeatureFlag:
    """Feature flag definition with governance controls."""

    name: str
    enabled: bool = False
    rollout_percentage: float = 0.0  # 0-100
    allowed_roles: list[str] = field(default_factory=list)
    allowed_systems: list[str] = field(default_factory=list)
    requires_governance: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemConfig:
    """Per-system configuration."""

    system_name: str
    version: str = "2.0.0"
    features: dict[str, FeatureFlag] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class ConfigurationManager:
    """Central configuration manager with SuperBrain governance."""

    # Default feature flags for 12 systems
    DEFAULT_FLAGS: dict[str, FeatureFlag] = {
        # Governance features
        "superbrain_actiongate": FeatureFlag(
            name="superbrain_actiongate",
            enabled=True,
            rollout_percentage=100.0,
            allowed_roles=["admin", "operator", "developer", "auditor", "readonly"],
            allowed_systems=["*"],
            requires_governance=True,
        ),
        "superbrain_audit_trail": FeatureFlag(
            name="superbrain_audit_trail",
            enabled=True,
            rollout_percentage=100.0,
            allowed_roles=["admin", "operator", "developer", "auditor"],
            allowed_systems=["*"],
            requires_governance=True,
        ),
        # Cognitive features
        "cognitive_router_v2": FeatureFlag(
            name="cognitive_router_v2",
            enabled=True,
            rollout_percentage=100.0,
            allowed_roles=["admin", "operator", "developer"],
            allowed_systems=["cognitive_router"],
            requires_governance=True,
        ),
        "advanced_routing": FeatureFlag(
            name="advanced_routing",
            enabled=False,
            rollout_percentage=10.0,  # Gradual rollout
            allowed_roles=["admin", "operator"],
            allowed_systems=["cognitive_router"],
            requires_governance=True,
        ),
        # Resilience features
        "circuit_breaker_enhanced": FeatureFlag(
            name="circuit_breaker_enhanced",
            enabled=True,
            rollout_percentage=100.0,
            allowed_roles=["admin", "operator"],
            allowed_systems=["resilience_engine"],
            requires_governance=True,
        ),
        "auto_healing": FeatureFlag(
            name="auto_healing",
            enabled=False,
            rollout_percentage=5.0,  # Canary deployment
            allowed_roles=["admin"],
            allowed_systems=["resilience_engine", "cognitive_router"],
            requires_governance=True,
        ),
        # Knowledge features
        "knowledge_realtime_sync": FeatureFlag(
            name="knowledge_realtime_sync",
            enabled=True,
            rollout_percentage=100.0,
            allowed_roles=["admin", "operator", "developer"],
            allowed_systems=["knowledge_loader"],
            requires_governance=False,
        ),
        "knowledge_graph_v2": FeatureFlag(
            name="knowledge_graph_v2",
            enabled=False,
            rollout_percentage=0.0,  # Not yet rolled out
            allowed_roles=["admin"],
            allowed_systems=["knowledge_loader"],
            requires_governance=True,
        ),
        # API features
        "graphql_subscriptions": FeatureFlag(
            name="graphql_subscriptions",
            enabled=True,
            rollout_percentage=100.0,
            allowed_roles=["admin", "operator", "developer"],
            allowed_systems=["graphql_api"],
            requires_governance=False,
        ),
        "api_rate_limiting": FeatureFlag(
            name="api_rate_limiting",
            enabled=True,
            rollout_percentage=100.0,
            allowed_roles=["*"],
            allowed_systems=["production_api", "graphql_api"],
            requires_governance=True,
        ),
        # Observability features
        "opentelemetry_tracing": FeatureFlag(
            name="opentelemetry_tracing",
            enabled=True,
            rollout_percentage=100.0,
            allowed_roles=["admin", "operator", "auditor"],
            allowed_systems=["*"],
            requires_governance=False,
        ),
        "advanced_metrics": FeatureFlag(
            name="advanced_metrics",
            enabled=False,
            rollout_percentage=25.0,
            allowed_roles=["admin", "operator"],
            allowed_systems=["*"],
            requires_governance=False,
        ),
    }

    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self._redis: redis.Redis = None
        self._local_cache: dict[str, Any] = {}
        self._brain = None

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

    def _get_redis(self) -> redis.Redis:
        """Get Redis connection with fallback."""
        if self._redis:
            try:
                self._redis.ping()
                return self._redis
            except Exception:
                pass
        return None

    def _validate_config_change(self, flag_name: str, new_value: bool, user_role: str) -> bool:
        """Validate configuration change via SuperBrain."""
        if not SUPERBRAIN_AVAILABLE or not self._brain:
            return True  # Fail open

        try:
            if hasattr(self._brain, "action_gate"):
                action_result = self._brain.action_gate.validate_action(
                    agent_id="config_manager",
                    action="modify_feature_flag",
                    details={
                        "flag_name": flag_name,
                        "new_value": new_value,
                        "user_role": user_role,
                    },
                )
                return action_result.authorized
        except Exception:
            pass  # Fail open

        return True

    def get_feature_flag(
        self, flag_name: str, user_id: str = None, user_role: str = "readonly"
    ) -> bool:
        """Check if feature flag is enabled for user."""
        # Get flag definition
        flag = self.DEFAULT_FLAGS.get(flag_name)
        if not flag:
            return False

        # Check if feature is globally enabled
        if not flag.enabled:
            return False

        # Check role permissions
        if flag.allowed_roles and user_role not in flag.allowed_roles:
            if "*" not in flag.allowed_roles:
                return False

        # Percentage-based rollout (consistent hashing)
        if flag.rollout_percentage < 100.0 and user_id:
            hash_value = int(hashlib.md5(f"{flag_name}:{user_id}".encode()).hexdigest(), 16)
            user_percentage = (hash_value % 10000) / 100.0
            if user_percentage > flag.rollout_percentage:
                return False

        # Check Redis for dynamic override
        redis_conn = self._get_redis()
        if redis_conn:
            try:
                override = redis_conn.get(f"feature_flag:{flag_name}")
                if override:
                    return json.loads(override).get("enabled", flag.enabled)
            except Exception:
                pass

        return flag.enabled

    def set_feature_flag(self, flag_name: str, enabled: bool, user_role: str = "admin") -> bool:
        """Set feature flag state (requires governance approval)."""
        flag = self.DEFAULT_FLAGS.get(flag_name)
        if not flag:
            return False

        # CANONICAL: Validate via SuperBrain
        if flag.requires_governance:
            if not self._validate_config_change(flag_name, enabled, user_role):
                return False

        # Update in Redis
        redis_conn = self._get_redis()
        if redis_conn:
            try:
                redis_conn.setex(
                    f"feature_flag:{flag_name}",
                    3600,  # 1 hour TTL
                    json.dumps(
                        {
                            "enabled": enabled,
                            "updated_at": datetime.now(UTC).isoformat(),
                            "updated_by": user_role,
                        }
                    ),
                )
            except Exception:
                pass

        # Record audit
        if SUPERBRAIN_AVAILABLE and self._brain:
            try:
                if hasattr(self._brain, "record_audit"):
                    self._brain.record_audit(
                        action="feature_flag_changed",
                        agent_id="config_manager",
                        details={
                            "flag_name": flag_name,
                            "new_state": enabled,
                            "user_role": user_role,
                        },
                    )
            except Exception:
                pass

        return True

    def get_all_flags(self, user_role: str = "readonly") -> dict[str, dict[str, Any]]:
        """Get all feature flags visible to role."""
        visible = {}

        for name, flag in self.DEFAULT_FLAGS.items():
            # Check role visibility
            if flag.allowed_roles and user_role not in flag.allowed_roles:
                if "*" not in flag.allowed_roles:
                    continue

            visible[name] = {
                "name": flag.name,
                "enabled": flag.enabled,
                "rollout_percentage": flag.rollout_percentage,
                "requires_governance": flag.requires_governance,
                "allowed_systems": flag.allowed_systems,
            }

        return visible

    def kill_switch(self, system: str) -> bool:
        """Emergency kill switch for a system."""
        # CANONICAL: Requires SuperBrain validation
        if SUPERBRAIN_AVAILABLE and self._brain:
            try:
                if hasattr(self._brain, "action_gate"):
                    action_result = self._brain.action_gate.validate_action(
                        agent_id="config_manager",
                        action="emergency_kill_switch",
                        details={"system": system, "urgent": True},
                    )
                    if not action_result.authorized:
                        return False
            except Exception:
                pass

        # Disable all features for system
        redis_conn = self._get_redis()
        if redis_conn:
            try:
                for flag_name, flag in self.DEFAULT_FLAGS.items():
                    if system in flag.allowed_systems or "*" in flag.allowed_systems:
                        redis_conn.setex(
                            f"feature_flag:{flag_name}",
                            300,  # 5 minute emergency TTL
                            json.dumps(
                                {
                                    "enabled": False,
                                    "updated_at": datetime.now(UTC).isoformat(),
                                    "reason": f"emergency_kill_switch_{system}",
                                }
                            ),
                        )
            except Exception:
                pass

        return True


# Global configuration manager
config_manager = ConfigurationManager()


# Convenience functions
def is_feature_enabled(flag_name: str, user_id: str = None, user_role: str = "readonly") -> bool:
    """Check if feature is enabled."""
    return config_manager.get_feature_flag(flag_name, user_id, user_role)


def enable_feature(flag_name: str, user_role: str = "admin") -> bool:
    """Enable feature flag."""
    return config_manager.set_feature_flag(flag_name, True, user_role)


def disable_feature(flag_name: str, user_role: str = "admin") -> bool:
    """Disable feature flag."""
    return config_manager.set_feature_flag(flag_name, False, user_role)


def emergency_stop(system: str) -> bool:
    """Emergency stop for system."""
    return config_manager.kill_switch(system)
