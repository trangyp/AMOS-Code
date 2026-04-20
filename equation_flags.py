#!/usr/bin/env python3
"""AMOS Equation Feature Flags - Feature Toggle Management System.

Production-grade feature flag system:
- Local file-based flags for development
- Redis-backed flags for production
- User targeting and segmentation
- Percentage-based rollouts (canary)
- A/B testing support
- Scheduled flag activation
- Flag analytics and metrics
- Emergency kill switches
- Gradual rollout strategies
- Environment-specific flags

Architecture Pattern: Feature flag evaluation with context
Flag Features:
    - Boolean flags (on/off)
    - Percentage rollouts
    - User segmentation
    - A/B testing buckets
    - Scheduled releases
    - Multi-environment support

Integration:
    - equation_app: Middleware for flag context
    - equation_auth: User targeting
    - equation_cache: Redis flag storage
    - equation_metrics: Flag analytics

Usage:
    # In endpoint
    from equation_flags import is_enabled, get_flag_value

    @app.post("/api/v1/equations/advanced")
    async def advanced_equation(
        request: Request,
        current_user = Depends(get_current_user)
    ):
        # Check if feature is enabled for this user
        if is_enabled("advanced_equations", user_id=current_user.id):
            return await process_advanced()
        else:
            raise HTTPException(status_code=404)

    # A/B testing
    variant = get_flag_value(
        "new_ui_experiment",
        user_id=current_user.id,
        default="control"
    )

Environment Variables:
    FEATURE_FLAGS_BACKEND: Storage backend (redis, file, memory)
    FEATURE_FLAGS_FILE: Path to flags JSON file
    FEATURE_FLAGS_REFRESH: Refresh interval in seconds (default: 60)
    FEATURE_FLAGS_DEFAULT: Default flag state when unknown (default: false)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum

UTC = UTC
from functools import wraps
from pathlib import Path
from typing import Any, Optional

# Redis imports
try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None

# FastAPI imports
try:
    from fastapi import HTTPException, Request
    from starlette.middleware.base import BaseHTTPMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    Request = None
    BaseHTTPMiddleware = None

# Auth imports
try:
    from equation_auth import get_current_user_id

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Cache imports
try:
    from amos_cache import get_redis_client

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

# Metrics imports
try:
    from equation_metrics import record_metric

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

# Logging imports
try:
    from equation_logging import get_logger

    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

logger = logging.getLogger("amos_equation_flags")


# ============================================================================
# Enums and Constants
# ============================================================================


class FlagType(str, Enum):
    """Feature flag types."""

    BOOLEAN = "boolean"  # Simple on/off
    PERCENTAGE = "percentage"  # Percentage rollout
    VARIANT = "variant"  # A/B test with multiple variants
    TARGETED = "targeted"  # User-specific targeting


class FlagStatus(str, Enum):
    """Feature flag status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SCHEDULED = "scheduled"  # Will activate at specific time
    DEPRECATED = "deprecated"  # Will be removed


# Default configuration
DEFAULT_REFRESH_INTERVAL = 60  # seconds
DEFAULT_FLAG_STATE = False
FLAGS_FILE_PATH = os.getenv("FEATURE_FLAGS_FILE", "./feature_flags.json")


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class FlagCondition:
    """Condition for targeting flag."""

    attribute: str  # e.g., "role", "plan", "user_id"
    operator: str  # e.g., "equals", "in", "contains"
    value: Any


@dataclass
class FlagVariant:
    """A/B test variant configuration."""

    name: str
    weight: int  # Percentage weight (0-100)
    payload: Any = None  # Variant-specific data


@dataclass
class FeatureFlag:
    """Feature flag definition."""

    key: str
    name: str
    description: str
    type: FlagType
    status: FlagStatus

    # For boolean flags
    enabled: bool = False

    # For percentage rollout
    rollout_percentage: int = 0  # 0-100

    # For targeted flags
    conditions: list[FlagCondition] = field(default_factory=list)

    # For variant/A-B testing
    variants: list[FlagVariant] = field(default_factory=list)
    default_variant: str = "control"

    # Scheduling
    activate_at: datetime = None
    deactivate_at: datetime = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "status": self.status.value,
            "enabled": self.enabled,
            "rollout_percentage": self.rollout_percentage,
            "conditions": [
                {"attribute": c.attribute, "operator": c.operator, "value": c.value}
                for c in self.conditions
            ],
            "variants": [
                {"name": v.name, "weight": v.weight, "payload": v.payload} for v in self.variants
            ],
            "default_variant": self.default_variant,
            "activate_at": self.activate_at.isoformat() if self.activate_at else None,
            "deactivate_at": self.deactivate_at.isoformat() if self.deactivate_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "tags": self.tags,
        }


@dataclass
class EvaluationContext:
    """Context for flag evaluation."""

    user_id: int = None
    user_role: str = None
    user_plan: str = None
    session_id: str = None
    ip_address: str = None
    custom_attributes: dict[str, Any] = field(default_factory=dict)

    def get_attribute(self, name: str) -> Any:
        """Get attribute value by name."""
        if name == "user_id" and self.user_id:
            return str(self.user_id)
        if name == "role" and self.user_role:
            return self.user_role
        if name == "plan" and self.plan:
            return self.user_plan
        return self.custom_attributes.get(name)


# ============================================================================
# Flag Storage Backends
# ============================================================================


class FlagStorage:
    """Base class for flag storage backends."""

    async def get(self, key: str) -> Optional[FeatureFlag]:
        """Get flag by key."""
        raise NotImplementedError

    async def get_all(self) -> dict[str, FeatureFlag]:
        """Get all flags."""
        raise NotImplementedError

    async def set(self, flag: FeatureFlag) -> None:
        """Set flag."""
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        """Delete flag."""
        raise NotImplementedError


class FileFlagStorage(FlagStorage):
    """File-based flag storage."""

    def __init__(self, file_path: str = FLAGS_FILE_PATH):
        self.file_path = Path(file_path)
        self._flags: dict[str, FeatureFlag] = {}
        self._last_modified: float = 0
        self.logger = get_logger("flags") if LOGGING_AVAILABLE else logger

    async def _reload_if_changed(self) -> None:
        """Reload flags if file changed."""
        if not self.file_path.exists():
            return

        mtime = self.file_path.stat().st_mtime
        if mtime > self._last_modified:
            await self._load()
            self._last_modified = mtime

    async def _load(self) -> None:
        """Load flags from file."""
        try:
            with open(self.file_path) as f:
                data = json.load(f)

            self._flags = {}
            for flag_data in data.get("flags", []):
                flag = self._dict_to_flag(flag_data)
                self._flags[flag.key] = flag

            self.logger.info(f"Loaded {len(self._flags)} flags from {self.file_path}")

        except Exception as e:
            self.logger.error(f"Failed to load flags: {e}")

    async def _save(self) -> None:
        """Save flags to file."""
        data = {
            "version": "1.0",
            "updated_at": datetime.now(UTC).isoformat(),
            "flags": [flag.to_dict() for flag in self._flags.values()],
        }

        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

        self._last_modified = self.file_path.stat().st_mtime

    def _dict_to_flag(self, data: dict[str, Any]) -> FeatureFlag:
        """Convert dictionary to FeatureFlag."""
        conditions = [FlagCondition(**c) for c in data.get("conditions", [])]

        variants = [FlagVariant(**v) for v in data.get("variants", [])]

        return FeatureFlag(
            key=data["key"],
            name=data.get("name", data["key"]),
            description=data.get("description", ""),
            type=FlagType(data.get("type", "boolean")),
            status=FlagStatus(data.get("status", "inactive")),
            enabled=data.get("enabled", False),
            rollout_percentage=data.get("rollout_percentage", 0),
            conditions=conditions,
            variants=variants,
            default_variant=data.get("default_variant", "control"),
            tags=data.get("tags", []),
        )

    async def get(self, key: str) -> Optional[FeatureFlag]:
        await self._reload_if_changed()
        return self._flags.get(key)

    async def get_all(self) -> dict[str, FeatureFlag]:
        await self._reload_if_changed()
        return self._flags.copy()

    async def set(self, flag: FeatureFlag) -> None:
        self._flags[flag.key] = flag
        await self._save()

    async def delete(self, key: str) -> None:
        if key in self._flags:
            del self._flags[key]
            await self._save()


class RedisFlagStorage(FlagStorage):
    """Redis-based flag storage for distributed systems."""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.logger = get_logger("flags") if LOGGING_AVAILABLE else logger

    async def _get_redis(self):
        """Get Redis connection."""
        if self.redis:
            return self.redis
        if CACHE_AVAILABLE:
            return await get_redis_client()
        if REDIS_AVAILABLE:
            return aioredis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        raise RuntimeError("Redis not available")

    async def get(self, key: str) -> Optional[FeatureFlag]:
        try:
            redis = await self._get_redis()
            data = await redis.get(f"flag:{key}")
            if data:
                flag_data = json.loads(data)
                return self._dict_to_flag(flag_data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get flag from Redis: {e}")
            return None

    async def get_all(self) -> dict[str, FeatureFlag]:
        try:
            redis = await self._get_redis()
            keys = await redis.keys("flag:*")
            flags = {}

            for key in keys:
                data = await redis.get(key)
                if data:
                    flag_data = json.loads(data)
                    flag = self._dict_to_flag(flag_data)
                    flags[flag.key] = flag

            return flags
        except Exception as e:
            self.logger.error(f"Failed to get all flags from Redis: {e}")
            return {}

    async def set(self, flag: FeatureFlag) -> None:
        try:
            redis = await self._get_redis()
            await redis.set(
                f"flag:{flag.key}",
                json.dumps(flag.to_dict()),
                ex=86400,  # 24 hour expiry
            )
        except Exception as e:
            self.logger.error(f"Failed to set flag in Redis: {e}")

    async def delete(self, key: str) -> None:
        try:
            redis = await self._get_redis()
            await redis.delete(f"flag:{key}")
        except Exception as e:
            self.logger.error(f"Failed to delete flag from Redis: {e}")

    def _dict_to_flag(self, data: dict[str, Any]) -> FeatureFlag:
        """Convert dictionary to FeatureFlag."""
        conditions = [FlagCondition(**c) for c in data.get("conditions", [])]

        variants = [FlagVariant(**v) for v in data.get("variants", [])]

        return FeatureFlag(
            key=data["key"],
            name=data.get("name", data["key"]),
            description=data.get("description", ""),
            type=FlagType(data.get("type", "boolean")),
            status=FlagStatus(data.get("status", "inactive")),
            enabled=data.get("enabled", False),
            rollout_percentage=data.get("rollout_percentage", 0),
            conditions=conditions,
            variants=variants,
            default_variant=data.get("default_variant", "control"),
            tags=data.get("tags", []),
        )


# ============================================================================
# Flag Manager
# ============================================================================


class FlagManager:
    """Central manager for feature flags."""

    def __init__(self, storage: Optional[FlagStorage] = None):
        self.storage = storage or self._create_default_storage()
        self.logger = get_logger("flags") if LOGGING_AVAILABLE else logger
        self._local_cache: dict[str, FeatureFlag] = {}
        self._cache_timestamp: float = 0
        self._cache_ttl = DEFAULT_REFRESH_INTERVAL

    def _create_default_storage(self) -> FlagStorage:
        """Create default storage based on environment."""
        backend = os.getenv("FEATURE_FLAGS_BACKEND", "file")

        if backend == "redis" and (REDIS_AVAILABLE or CACHE_AVAILABLE):
            return RedisFlagStorage()
        else:
            return FileFlagStorage()

    async def _get_flag(self, key: str) -> Optional[FeatureFlag]:
        """Get flag with caching."""
        now = datetime.now().timestamp()

        # Check local cache
        if key in self._local_cache and (now - self._cache_timestamp) < self._cache_ttl:
            return self._local_cache[key]

        # Fetch from storage
        flag = await self.storage.get(key)

        if flag:
            self._local_cache[key] = flag
            self._cache_timestamp = now

        return flag

    async def evaluate(
        self, key: str, context: Optional[EvaluationContext] = None, default: Any = False
    ) -> Any:
        """Evaluate a feature flag.

        Args:
            key: Flag key
            context: Evaluation context (user info, etc.)
            default: Default value if flag not found

        Returns:
            Flag value (bool for boolean flags, variant name for variant flags)
        """
        flag = await self._get_flag(key)

        if not flag:
            return default

        # Check status
        if flag.status == FlagStatus.INACTIVE:
            return default

        if flag.status == FlagStatus.DEPRECATED:
            return default

        # Check scheduling
        if flag.activate_at and datetime.now(UTC) < flag.activate_at:
            return default

        if flag.deactivate_at and datetime.now(UTC) > flag.deactivate_at:
            return default

        # Evaluate based on type
        if flag.type == FlagType.BOOLEAN:
            return flag.enabled

        if flag.type == FlagType.PERCENTAGE:
            return self._evaluate_percentage(flag, context)

        if flag.type == FlagType.TARGETED:
            return self._evaluate_targeted(flag, context)

        if flag.type == FlagType.VARIANT:
            return self._evaluate_variant(flag, context)

        return default

    def _evaluate_percentage(self, flag: FeatureFlag, context: EvaluationContext) -> bool:
        """Evaluate percentage-based rollout."""
        if not flag.enabled:
            return False

        # Use user_id for consistent hashing
        user_id = context.user_id if context else None

        if user_id is None:
            # Random for anonymous users
            return random.random() * 100 < flag.rollout_percentage

        # Consistent hash for user
        hash_input = f"{flag.key}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        user_bucket = hash_value % 100

        return user_bucket < flag.rollout_percentage

    def _evaluate_targeted(self, flag: FeatureFlag, context: EvaluationContext) -> bool:
        """Evaluate targeted flag."""
        if not flag.enabled:
            return False

        if not context:
            return False

        # Check all conditions
        for condition in flag.conditions:
            attr_value = context.get_attribute(condition.attribute)

            if not self._match_condition(attr_value, condition):
                return False

        return True

    def _match_condition(self, value: Any, condition: FlagCondition) -> bool:
        """Check if value matches condition."""
        if condition.operator == "equals":
            return str(value) == str(condition.value)

        if condition.operator == "in":
            return str(value) in [str(v) for v in condition.value]

        if condition.operator == "contains":
            return str(condition.value) in str(value)

        if condition.operator == "not_equals":
            return str(value) != str(condition.value)

        return False

    def _evaluate_variant(self, flag: FeatureFlag, context: EvaluationContext) -> str:
        """Evaluate variant flag for A/B testing."""
        if not flag.variants:
            return flag.default_variant

        # Use user_id for consistent variant assignment
        user_id = context.user_id if context else random.randint(1, 1000000)

        hash_input = f"{flag.key}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        user_bucket = hash_value % 100

        # Assign variant based on weights
        cumulative = 0
        for variant in flag.variants:
            cumulative += variant.weight
            if user_bucket < cumulative:
                return variant.name

        return flag.default_variant

    async def get_all_flags(self) -> dict[str, FeatureFlag]:
        """Get all flags."""
        return await self.storage.get_all()

    async def create_flag(self, flag: FeatureFlag) -> None:
        """Create new flag."""
        await self.storage.set(flag)
        self.logger.info(f"Created flag: {flag.key}")

    async def update_flag(self, key: str, updates: dict[str, Any]) -> None:
        """Update existing flag."""
        flag = await self._get_flag(key)
        if not flag:
            raise ValueError(f"Flag not found: {key}")

        # Apply updates
        for field, value in updates.items():
            if hasattr(flag, field):
                setattr(flag, field, value)

        flag.updated_at = datetime.now(UTC)
        await self.storage.set(flag)

        # Invalidate cache
        if key in self._local_cache:
            del self._local_cache[key]

        self.logger.info(f"Updated flag: {key}")

    async def delete_flag(self, key: str) -> None:
        """Delete flag."""
        await self.storage.delete(key)

        if key in self._local_cache:
            del self._local_cache[key]

        self.logger.info(f"Deleted flag: {key}")


# ============================================================================
# Global Manager Instance
# ============================================================================_flag_manager: Optional[FlagManager] = None


def get_flag_manager() -> FlagManager:
    """Get global flag manager."""
    global _flag_manager
    if _flag_manager is None:
        _flag_manager = FlagManager()
    return _flag_manager


async def is_enabled(key: str, user_id: int = None, **context_kwargs) -> bool:
    """Check if feature is enabled.

    Args:
        key: Feature flag key
        user_id: User ID for targeting
        **context_kwargs: Additional context attributes

    Returns:
        True if feature is enabled
    """
    manager = get_flag_manager()
    context = EvaluationContext(user_id=user_id, **context_kwargs)
    result = await manager.evaluate(key, context, default=False)

    # Record metric
    if METRICS_AVAILABLE:
        record_metric("flag_evaluation", 1, {"flag": key, "result": str(result)})

    return bool(result)


async def get_variant(
    key: str, user_id: int = None, default: str = "control", **context_kwargs
) -> str:
    """Get variant for A/B test.

    Args:
        key: Feature flag key
        user_id: User ID for consistent assignment
        default: Default variant
        **context_kwargs: Additional context attributes

    Returns:
        Variant name
    """
    manager = get_flag_manager()
    context = EvaluationContext(user_id=user_id, **context_kwargs)
    return await manager.evaluate(key, context, default=default)


# ============================================================================
# Decorators
# ============================================================================


def feature_flag_required(
    flag_key: str, user_id_param: str = "current_user", error_message: str = "Feature not available"
):
    """Decorator to require feature flag for endpoint.

    Args:
        flag_key: Feature flag key
        user_id_param: Parameter name for user ID extraction
        error_message: Error message when flag is disabled
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from kwargs
            user_id = None
            if user_id_param in kwargs:
                user_param = kwargs[user_id_param]
                if hasattr(user_param, "id"):
                    user_id = user_param.id
                elif isinstance(user_param, int):
                    user_id = user_param

            # Check flag
            enabled = await is_enabled(flag_key, user_id=user_id)

            if not enabled:
                raise HTTPException(status_code=403, detail=error_message)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# Default Flags
# ============================================================================

DEFAULT_FLAGS = [
    FeatureFlag(
        key="advanced_equations",
        name="Advanced Equation Processing",
        description="Enable advanced equation features",
        type=FlagType.BOOLEAN,
        status=FlagStatus.ACTIVE,
        enabled=False,
        tags=["beta", "equations"],
    ),
    FeatureFlag(
        key="new_ui_v2",
        name="New UI Version 2",
        description="Rollout of new UI version",
        type=FlagType.PERCENTAGE,
        status=FlagStatus.ACTIVE,
        enabled=True,
        rollout_percentage=10,
        tags=["ui", "gradual"],
    ),
    FeatureFlag(
        key="experiment_search",
        name="Search Algorithm Experiment",
        description="A/B test for new search algorithm",
        type=FlagType.VARIANT,
        status=FlagStatus.ACTIVE,
        enabled=True,
        variants=[FlagVariant(name="control", weight=50), FlagVariant(name="treatment", weight=50)],
        tags=["experiment", "search"],
    ),
]


async def init_default_flags() -> None:
    """Initialize default flags if none exist."""
    manager = get_flag_manager()
    existing = await manager.get_all_flags()

    if not existing:
        for flag in DEFAULT_FLAGS:
            await manager.create_flag(flag)
        logger.info(f"Initialized {len(DEFAULT_FLAGS)} default flags")


# ============================================================================
# FastAPI Integration
# ============================================================================

if FASTAPI_AVAILABLE and BaseHTTPMiddleware:

    class FeatureFlagMiddleware(BaseHTTPMiddleware):
        """Middleware to add flag context to requests."""

        async def dispatch(self, request: Request, call_next):
            """Add flag context to request state."""
            # Build context from request
            context = EvaluationContext()

            # Try to get user info
            if AUTH_AVAILABLE:
                try:
                    user_id = await get_current_user_id()
                    context.user_id = user_id
                except Exception:
                    pass

            # Add custom attributes from headers
            for header, value in request.headers.items():
                if header.startswith("x-flag-"):
                    attr_name = header[7:]  # Remove 'x-flag-' prefix
                    context.custom_attributes[attr_name] = value

            # Store in request state
            request.state.flag_context = context

            response = await call_next(request)
            return response


# ============================================================================
# Example Usage
# ============================================================================


async def example_usage():
    """Example usage of feature flags."""
    print("AMOS Equation Feature Flags")
    print("=" * 50)

    # Initialize default flags
    await init_default_flags()

    # Check boolean flag
    enabled = await is_enabled("advanced_equations", user_id=123)
    print(f"Advanced equations enabled for user 123: {enabled}")

    # Check percentage rollout (will be consistent for same user)
    for user_id in [1, 2, 3, 4, 5, 10, 20, 30, 40, 50]:
        enabled = await is_enabled("new_ui_v2", user_id=user_id)
        print(f"New UI v2 for user {user_id}: {enabled}")

    # Get A/B test variant
    for user_id in [1, 2, 3, 4, 5]:
        variant = await get_variant("experiment_search", user_id=user_id)
        print(f"User {user_id} gets variant: {variant}")

    print("\nFeature flag examples completed!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
