"""Operational Architecture Bridge.

Integrates operational architecture validation with AMOS Brain cognition.

Provides API for:
- Operational integrity assessment
- Cache configuration validation
- Fallback topology checking
- Queue semantics validation
- Idempotency verification
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Import operational architecture engine
try:
    from repo_doctor.operational_architecture_engine import (
        CacheConfig,
        CacheStrategy,
        DeliveryGuarantee,
        FallbackConfig,
        FallbackLevel,
        IdempotencyConfig,
        InvalidationPolicy,
        OperationalArchitectureEngine,
        QueueConfig,
        QueueOrder,
    )
    OPERATIONAL_AVAILABLE = True
except ImportError:
    OPERATIONAL_AVAILABLE = False


class OperationalArchitectureBridge:
    """Bridge between operational architecture and AMOS Brain."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._engine: OperationalArchitectureEngine | None = None

    @property
    def engine(self) -> OperationalArchitectureEngine | None:
        """Lazy initialization of operational engine."""
        if self._engine is None and OPERATIONAL_AVAILABLE:
            self._engine = OperationalArchitectureEngine()
        return self._engine

    def assess_operational_integrity(self) -> dict[str, Any]:
        """Perform comprehensive operational architecture assessment."""
        if not OPERATIONAL_AVAILABLE or self.engine is None:
            return {"error": "operational_engine not available"}

        assessment = self.engine.assess_operational_integrity()
        return assessment.to_dict()

    def validate_cache_config(
        self,
        cache_id: str,
        strategy: str,
        invalidation: str,
        source_of_truth: str | None = None,
        ttl_seconds: int | None = None,
        staleness_bound_ms: int | None = None,
    ) -> dict[str, Any]:
        """Validate cache configuration (I_cache)."""
        if not OPERATIONAL_AVAILABLE or self.engine is None:
            return {"error": "operational_engine not available"}

        # Convert strings to enums
        try:
            strategy_enum = CacheStrategy(strategy)
            invalidation_enum = InvalidationPolicy(invalidation)
        except ValueError as e:
            return {"error": f"Invalid enum value: {e}"}

        # Create config
        config = CacheConfig(
            cache_id=cache_id,
            name=cache_id,
            strategy=strategy_enum,
            invalidation_policy=invalidation_enum,
            source_of_truth=source_of_truth,
            ttl_seconds=ttl_seconds,
            staleness_bound_ms=staleness_bound_ms,
        )
        self.engine.add_cache_config(config)

        # Check for issues
        issues = []
        if not source_of_truth:
            issues.append("Cache has no declared source of truth")
        if invalidation_enum == InvalidationPolicy.TTL and not ttl_seconds:
            issues.append("TTL policy requires ttl_seconds")
        if not staleness_bound_ms:
            issues.append("Unbounded staleness may cause consistency issues")

        return {
            "valid": len(issues) == 0,
            "cache_id": cache_id,
            "strategy": strategy,
            "invalidation": invalidation,
            "issues": issues,
            "invariant": "I_cache",
        }

    def validate_fallback_topology(
        self,
        service_id: str,
        levels: dict[str, list[str]],
        triggers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Validate fallback topology (I_fallback)."""
        if not OPERATIONAL_AVAILABLE or self.engine is None:
            return {"error": "operational_engine not available"}

        # Parse levels
        parsed_levels: dict[FallbackLevel, list[str]] = {}
        for level_str, features in levels.items():
            try:
                level = FallbackLevel(level_str)
                parsed_levels[level] = features
            except ValueError:
                return {"error": f"Invalid fallback level: {level_str}"}

        # Parse triggers
        parsed_triggers: dict[str, FallbackLevel] = {}
        if triggers:
            for condition, level_str in triggers.items():
                try:
                    level = FallbackLevel(level_str)
                    parsed_triggers[condition] = level
                except ValueError:
                    return {"error": f"Invalid trigger level: {level_str}"}

        # Create config
        config = FallbackConfig(
            service_id=service_id,
            name=service_id,
            current_level=FallbackLevel.FULL,
            levels=parsed_levels,
            triggers=parsed_triggers,
        )
        self.engine.add_fallback_config(config)

        # Check monotonicity
        level_order = [
            FallbackLevel.FULL,
            FallbackLevel.DEGRADED,
            FallbackLevel.MINIMAL,
            FallbackLevel.EMERGENCY,
            FallbackLevel.OFFLINE,
        ]

        issues = []
        for i in range(len(level_order) - 1):
            current = level_order[i]
            next_level = level_order[i + 1]

            if current in parsed_levels and next_level in parsed_levels:
                current_features = set(parsed_levels[current])
                next_features = set(parsed_levels[next_level])

                if not next_features.issubset(current_features):
                    extra = next_features - current_features
                    issues.append(
                        f"Non-monotonic fallback: {next_level.value} has extra features: {extra}"
                    )

        if not parsed_triggers:
            issues.append("No fallback triggers defined")

        return {
            "valid": len(issues) == 0,
            "service_id": service_id,
            "levels": list(levels.keys()),
            "issues": issues,
            "invariant": "I_fallback",
        }

    def validate_queue_config(
        self,
        queue_id: str,
        order: str,
        delivery_guarantee: str,
        max_retry: int = 3,
        dlq_enabled: bool = False,
        deduplication: bool = False,
        dedup_window_ms: int | None = None,
    ) -> dict[str, Any]:
        """Validate queue configuration (I_queue)."""
        if not OPERATIONAL_AVAILABLE or self.engine is None:
            return {"error": "operational_engine not available"}

        # Convert strings to enums
        try:
            order_enum = QueueOrder(order)
            delivery_enum = DeliveryGuarantee(delivery_guarantee)
        except ValueError as e:
            return {"error": f"Invalid enum value: {e}"}

        # Create config
        config = QueueConfig(
            queue_id=queue_id,
            name=queue_id,
            order=order_enum,
            delivery_guarantee=delivery_enum,
            max_retry=max_retry,
            dlq_enabled=dlq_enabled,
            deduplication=deduplication,
            dedup_window_ms=dedup_window_ms,
        )
        self.engine.add_queue_config(config)

        # Check for issues
        issues = []
        if delivery_enum == DeliveryGuarantee.EXACTLY_ONCE and not deduplication:
            issues.append("Exactly-once delivery requires deduplication")
        if deduplication and not dedup_window_ms:
            issues.append("Deduplication requires time window")
        if max_retry > 0 and not dlq_enabled:
            issues.append("Retries without DLQ may cause infinite loops")

        return {
            "valid": len(issues) == 0,
            "queue_id": queue_id,
            "order": order,
            "delivery_guarantee": delivery_guarantee,
            "issues": issues,
            "invariant": "I_queue",
        }

    def validate_idempotency(
        self,
        operation_id: str,
        idempotent: bool,
        key_extractor: str | None = None,
        storage_backend: str | None = None,
    ) -> dict[str, Any]:
        """Validate idempotency configuration (I_idempotency)."""
        if not OPERATIONAL_AVAILABLE or self.engine is None:
            return {"error": "operational_engine not available"}

        # Create config
        config = IdempotencyConfig(
            operation_id=operation_id,
            name=operation_id,
            idempotent=idempotent,
            key_extractor=key_extractor,
            storage_backend=storage_backend,
        )
        self.engine.add_idempotency_config(config)

        # Check for issues
        issues = []
        if idempotent:
            if not key_extractor:
                issues.append("Idempotent operation needs key extraction mechanism")
            if not storage_backend:
                issues.append("Idempotent operation needs storage backend")

        return {
            "valid": len(issues) == 0,
            "operation_id": operation_id,
            "idempotent": idempotent,
            "issues": issues,
            "invariant": "I_idempotency",
        }

    def get_operational_insights(self) -> dict[str, Any]:
        """Get operational architecture insights."""
        if not OPERATIONAL_AVAILABLE or self.engine is None:
            return {"error": "operational_engine not available"}

        insights = self.engine.get_operational_insights()
        return {
            "insights": insights,
            "count": len(insights),
        }


def get_operational_architecture_bridge(
    repo_path: str | Path,
) -> OperationalArchitectureBridge:
    """Factory function to get operational architecture bridge."""
    return OperationalArchitectureBridge(repo_path)
