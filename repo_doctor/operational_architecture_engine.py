"""Operational Architecture Engine.

Validates operational, caching, queue, and fallback aspects of architecture.

Addresses:
- Cache coherence (I_cache)
- Fallback topology (I_fallback)
- Queue ordering semantics (I_queue)
- Idempotency boundaries (I_idempotency)

Mathematical Foundation:
- Cache coherence: all observers see consistent state transitions
- Fallback topology: L(d) ⊆ L(primary) for all degradation levels d
- Queue semantics: FIFO, LIFO, priority ordering guarantees
- Idempotency: f(x) = f(f(x)) for idempotent operations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CacheStrategy(Enum):
    """Cache coherence strategies."""

    WRITE_THROUGH = "write_through"  # Write to cache and source
    WRITE_BACK = "write_back"  # Write to cache, async to source
    WRITE_AROUND = "write_around"  # Write to source, invalidate cache
    CACHE_ASIDE = "cache_aside"  # App manages cache
    READ_THROUGH = "read_through"  # Cache loads from source on miss


class InvalidationPolicy(Enum):
    """Cache invalidation policies."""

    TTL = "ttl"  # Time-to-live expiration
    LRU = "lru"  # Least recently used
    LFU = "lfu"  # Least frequently used
    EXPLICIT = "explicit"  # Manual invalidation
    EVENT_DRIVEN = "event_driven"  # Invalidate on change event


class FallbackLevel(Enum):
    """Levels of graceful degradation."""

    FULL = "full"  # All features operational
    DEGRADED = "degraded"  # Reduced functionality
    MINIMAL = "minimal"  # Core only
    EMERGENCY = "emergency"  # Read-only, critical only
    OFFLINE = "offline"  # Complete shutdown


class QueueOrder(Enum):
    """Queue ordering semantics."""

    FIFO = "fifo"  # First in, first out
    LIFO = "lifo"  # Last in, first out
    PRIORITY = "priority"  # Priority-based
    TIME_BASED = "time_based"  # Scheduled execution


class DeliveryGuarantee(Enum):
    """Message delivery guarantees."""

    AT_MOST_ONCE = "at_most_once"  # May lose, never duplicate
    AT_LEAST_ONCE = "at_least_once"  # May duplicate, never lose
    EXACTLY_ONCE = "exactly_once"  # Exactly one delivery


@dataclass
class CacheConfig:
    """Cache configuration."""

    cache_id: str
    name: str
    strategy: CacheStrategy
    invalidation_policy: InvalidationPolicy
    ttl_seconds: int | None = None
    max_size: int | None = None
    source_of_truth: str | None = None  # Where canonical data lives
    staleness_bound_ms: int | None = None  # Max acceptable staleness


@dataclass
class FallbackConfig:
    """Fallback/degradation configuration."""

    service_id: str
    name: str
    current_level: FallbackLevel
    levels: dict[FallbackLevel, list[str]]  # Level -> available features
    triggers: dict[str, FallbackLevel]  # Condition -> level transition


@dataclass
class QueueConfig:
    """Queue configuration."""

    queue_id: str
    name: str
    order: QueueOrder
    delivery_guarantee: DeliveryGuarantee
    max_retry: int = 3
    dlq_enabled: bool = False  # Dead letter queue
    deduplication: bool = False  # Deduplication enabled
    dedup_window_ms: int | None = None  # Deduplication time window


@dataclass
class IdempotencyConfig:
    """Idempotency configuration."""

    operation_id: str
    name: str
    idempotent: bool
    key_extractor: str | None = None  # How to extract idempotency key
    storage_backend: str | None = None  # Where to store processed keys
    ttl_hours: int = 24  # How long to remember processed keys


@dataclass
class OperationalViolation:
    """Violation of operational architecture rules."""

    violation_id: str
    violation_type: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    invariant_broken: str
    component: str
    evidence: list[str] = field(default_factory=list)
    remediation: str = ""


@dataclass
class OperationalAssessment:
    """Complete operational architecture assessment."""

    assessment_id: str
    timestamp: str

    # Configurations
    cache_configs: list[CacheConfig]
    fallback_configs: list[FallbackConfig]
    queue_configs: list[QueueConfig]
    idempotency_configs: list[IdempotencyConfig]

    # Violations
    violations: list[OperationalViolation]

    # Invariant status
    cache_valid: bool
    fallback_valid: bool
    queue_valid: bool
    idempotency_valid: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "timestamp": self.timestamp,
            "summary": {
                "cache_configs": len(self.cache_configs),
                "fallback_configs": len(self.fallback_configs),
                "queue_configs": len(self.queue_configs),
                "idempotency_configs": len(self.idempotency_configs),
                "violations": len(self.violations),
                "critical": len([v for v in self.violations if v.severity == "critical"]),
            },
            "invariants": {
                "cache": self.cache_valid,
                "fallback": self.fallback_valid,
                "queue": self.queue_valid,
                "idempotency": self.idempotency_valid,
            },
        }


class OperationalArchitectureEngine:
    """
    Engine for operational architecture validation.

    Validates:
    - Cache coherence (I_cache)
    - Fallback topology (I_fallback)
    - Queue ordering semantics (I_queue)
    - Idempotency boundaries (I_idempotency)
    """

    def __init__(self):
        self.cache_configs: list[CacheConfig] = []
        self.fallback_configs: list[FallbackConfig] = []
        self.queue_configs: list[QueueConfig] = []
        self.idempotency_configs: list[IdempotencyConfig] = []
        self.assessments: list[OperationalAssessment] = []

    def add_cache_config(self, config: CacheConfig) -> None:
        """Add cache configuration."""
        self.cache_configs.append(config)

    def add_fallback_config(self, config: FallbackConfig) -> None:
        """Add fallback configuration."""
        self.fallback_configs.append(config)

    def add_queue_config(self, config: QueueConfig) -> None:
        """Add queue configuration."""
        self.queue_configs.append(config)

    def add_idempotency_config(self, config: IdempotencyConfig) -> None:
        """Add idempotency configuration."""
        self.idempotency_configs.append(config)

    def assess_operational_integrity(self) -> OperationalAssessment:
        """
        Perform comprehensive operational architecture assessment.

        Returns:
            Assessment with all violations found
        """
        violations: list[OperationalViolation] = []

        # 1. Check cache coherence (I_cache)
        for config in self.cache_configs:
            # Check source of truth declared
            if not config.source_of_truth:
                violations.append(
                    OperationalViolation(
                        violation_id=f"cache_{len(violations)}",
                        violation_type="missing_source_of_truth",
                        severity="high",
                        description=f"Cache {config.name} has no declared source of truth",
                        invariant_broken="I_cache",
                        component=config.cache_id,
                        evidence=["source_of_truth=None"],
                        remediation="Declare authoritative source for cache data",
                    )
                )

            # Check invalidation policy
            if config.invalidation_policy == InvalidationPolicy.TTL and not config.ttl_seconds:
                violations.append(
                    OperationalViolation(
                        violation_id=f"cache_{len(violations)}",
                        violation_type="missing_ttl",
                        severity="medium",
                        description=f"Cache {config.name} uses TTL policy without TTL value",
                        invariant_broken="I_cache",
                        component=config.cache_id,
                        evidence=["invalidation_policy=TTL", "ttl_seconds=None"],
                        remediation="Set explicit TTL or change invalidation policy",
                    )
                )

            # Check staleness bounds
            if not config.staleness_bound_ms:
                violations.append(
                    OperationalViolation(
                        violation_id=f"cache_{len(violations)}",
                        violation_type="unbounded_staleness",
                        severity="medium",
                        description=f"Cache {config.name} has no staleness bound",
                        invariant_broken="I_cache",
                        component=config.cache_id,
                        evidence=["staleness_bound_ms=None"],
                        remediation="Declare maximum acceptable staleness",
                    )
                )

        # 2. Check fallback topology (I_fallback)
        for config in self.fallback_configs:
            # Verify monotonic degradation: each level has subset of previous
            level_order = [
                FallbackLevel.FULL,
                FallbackLevel.DEGRADED,
                FallbackLevel.MINIMAL,
                FallbackLevel.EMERGENCY,
                FallbackLevel.OFFLINE,
            ]

            for i in range(len(level_order) - 1):
                current = level_order[i]
                next_level = level_order[i + 1]

                if current in config.levels and next_level in config.levels:
                    current_features = set(config.levels[current])
                    next_features = set(config.levels[next_level])

                    # Next level should have subset of current features
                    if not next_features.issubset(current_features):
                        extra = next_features - current_features
                        violations.append(
                            OperationalViolation(
                                violation_id=f"fb_{len(violations)}",
                                violation_type="non_monotonic_fallback",
                                severity="critical",
                                description=(
                                    f"Fallback level {next_level.value} has features "
                                    f"not available in {current.value}: {extra}"
                                ),
                                invariant_broken="I_fallback",
                                component=config.service_id,
                                evidence=[
                                    f"{current.value} has {current_features}",
                                    f"{next_level.value} has {next_features}",
                                ],
                                remediation="Ensure fallback levels are monotonic subsets",
                            )
                        )

            # Check triggers defined
            if not config.triggers:
                violations.append(
                    OperationalViolation(
                        violation_id=f"fb_{len(violations)}",
                        violation_type="no_fallback_triggers",
                        severity="high",
                        description=f"Service {config.name} has no fallback triggers defined",
                        invariant_broken="I_fallback",
                        component=config.service_id,
                        evidence=["triggers={}"],
                        remediation="Define conditions for automatic degradation",
                    )
                )

        # 3. Check queue ordering semantics (I_queue)
        for config in self.queue_configs:
            # Check exactly-once requires deduplication
            if (
                config.delivery_guarantee == DeliveryGuarantee.EXACTLY_ONCE
                and not config.deduplication
            ):
                violations.append(
                    OperationalViolation(
                        violation_id=f"queue_{len(violations)}",
                        violation_type="exactly_once_without_dedup",
                        severity="critical",
                        description=(
                            f"Queue {config.name} claims exactly-once delivery "
                            f"without deduplication"
                        ),
                        invariant_broken="I_queue",
                        component=config.queue_id,
                        evidence=["delivery_guarantee=EXACTLY_ONCE", "deduplication=False"],
                        remediation="Enable deduplication or change delivery guarantee",
                    )
                )

            # Check deduplication has window
            if config.deduplication and not config.dedup_window_ms:
                violations.append(
                    OperationalViolation(
                        violation_id=f"queue_{len(violations)}",
                        violation_type="dedup_without_window",
                        severity="medium",
                        description=f"Queue {config.name} has deduplication without time window",
                        invariant_broken="I_queue",
                        component=config.queue_id,
                        evidence=["deduplication=True", "dedup_window_ms=None"],
                        remediation="Set deduplication time window",
                    )
                )

            # Check retry with DLQ
            if config.max_retry > 0 and not config.dlq_enabled:
                violations.append(
                    OperationalViolation(
                        violation_id=f"queue_{len(violations)}",
                        violation_type="retry_without_dlq",
                        severity="medium",
                        description=f"Queue {config.name} has retries without dead letter queue",
                        invariant_broken="I_queue",
                        component=config.queue_id,
                        evidence=[f"max_retry={config.max_retry}", "dlq_enabled=False"],
                        remediation="Enable DLQ for poison message handling",
                    )
                )

        # 4. Check idempotency boundaries (I_idempotency)
        for config in self.idempotency_configs:
            if config.idempotent:
                # Idempotent operations need key extraction
                if not config.key_extractor:
                    violations.append(
                        OperationalViolation(
                            violation_id=f"idemp_{len(violations)}",
                            violation_type="idempotent_without_key",
                            severity="high",
                            description=(
                                f"Operation {config.name} is idempotent but "
                                f"has no key extraction mechanism"
                            ),
                            invariant_broken="I_idempotency",
                            component=config.operation_id,
                            evidence=["idempotent=True", "key_extractor=None"],
                            remediation="Define how to extract idempotency key from requests",
                        )
                    )

                # Need storage for processed keys
                if not config.storage_backend:
                    violations.append(
                        OperationalViolation(
                            violation_id=f"idemp_{len(violations)}",
                            violation_type="idempotent_without_storage",
                            severity="high",
                            description=(
                                f"Operation {config.name} is idempotent but "
                                f"has no storage backend for processed keys"
                            ),
                            invariant_broken="I_idempotency",
                            component=config.operation_id,
                            evidence=["idempotent=True", "storage_backend=None"],
                            remediation="Declare storage for idempotency key tracking",
                        )
                    )

        # Build assessment
        assessment = OperationalAssessment(
            assessment_id=f"operational_{len(self.assessments)}",
            timestamp="2024-01-01T00:00:00Z",  # Placeholder
            cache_configs=list(self.cache_configs),
            fallback_configs=list(self.fallback_configs),
            queue_configs=list(self.queue_configs),
            idempotency_configs=list(self.idempotency_configs),
            violations=violations,
            cache_valid=not any(v for v in violations if v.invariant_broken == "I_cache"),
            fallback_valid=not any(v for v in violations if v.invariant_broken == "I_fallback"),
            queue_valid=not any(v for v in violations if v.invariant_broken == "I_queue"),
            idempotency_valid=not any(
                v for v in violations if v.invariant_broken == "I_idempotency"
            ),
        )

        self.assessments.append(assessment)
        return assessment

    def check_cache_safety(
        self,
        cache_id: str,
        cold_start: bool,
        warm_hit_rate: float,
    ) -> dict[str, Any]:
        """
        Check cache safety under cold/warm transitions.

        Args:
            cache_id: Cache identifier
            cold_start: Whether cache is cold
            warm_hit_rate: Hit rate when warm

        Returns:
            Safety assessment
        """
        issues = []

        # Cold cache should not cause cascading failures
        if cold_start and warm_hit_rate > 0.8:
            issues.append(
                f"Cache {cache_id}: High hit rate dependency (warm={warm_hit_rate:.1%}) "
                f"may cause issues during cold start"
            )

        return {
            "valid": len(issues) == 0,
            "cache_id": cache_id,
            "cold_start": cold_start,
            "warm_hit_rate": warm_hit_rate,
            "issues": issues,
            "invariant": "I_cache",
        }

    def validate_fallback_transition(
        self,
        service_id: str,
        from_level: str,
        to_level: str,
        feature_set: list[str],
    ) -> dict[str, Any]:
        """Validate fallback transition preserves monotonicity."""
        try:
            from_enum = FallbackLevel(from_level)
            to_enum = FallbackLevel(to_level)
        except ValueError:
            return {"error": f"Invalid fallback level: {from_level} or {to_level}"}

        # Check if transition is allowed (degradation only)
        level_order = [
            FallbackLevel.FULL,
            FallbackLevel.DEGRADED,
            FallbackLevel.MINIMAL,
            FallbackLevel.EMERGENCY,
            FallbackLevel.OFFLINE,
        ]

        from_idx = level_order.index(from_enum) if from_enum in level_order else -1
        to_idx = level_order.index(to_enum) if to_enum in level_order else -1

        if from_idx == -1 or to_idx == -1:
            return {"error": "Unknown fallback level"}

        # Recovery (to_idx < from_idx) is always allowed
        # Degradation (to_idx > from_idx) must preserve feature subset
        if to_idx > from_idx:
            # Find config for this service
            config = next(
                (c for c in self.fallback_configs if c.service_id == service_id), None
            )
            if config and from_enum in config.levels:
                allowed_features = set(config.levels[from_enum])
                actual_features = set(feature_set)

                if not actual_features.issubset(allowed_features):
                    extra = actual_features - allowed_features
                    return {
                        "valid": False,
                        "service_id": service_id,
                        "from": from_level,
                        "to": to_level,
                        "extra_features": list(extra),
                        "issue": f"Degraded level has features not in parent: {extra}",
                        "invariant": "I_fallback",
                    }

        return {
            "valid": True,
            "service_id": service_id,
            "from": from_level,
            "to": to_level,
            "transition_type": "recovery" if to_idx < from_idx else "degradation",
            "invariant": "I_fallback",
        }

    def check_queue_ordering(
        self,
        queue_id: str,
        expected_order: str,
        observed_sequence: list[str],
    ) -> dict[str, Any]:
        """Check if observed sequence matches expected ordering."""
        try:
            order_enum = QueueOrder(expected_order)
        except ValueError:
            return {"error": f"Invalid queue order: {expected_order}"}

        if order_enum == QueueOrder.FIFO:
            # Check if sequence is FIFO (should be chronological by arrival)
            is_valid = observed_sequence == sorted(observed_sequence)
        elif order_enum == QueueOrder.LIFO:
            # Check if sequence is LIFO (should be reverse chronological)
            is_valid = observed_sequence == sorted(observed_sequence, reverse=True)
        elif order_enum == QueueOrder.PRIORITY:
            # Priority ordering - can't validate without priorities
            is_valid = True
        else:
            is_valid = True

        return {
            "valid": is_valid,
            "queue_id": queue_id,
            "expected_order": expected_order,
            "observed_count": len(observed_sequence),
            "invariant": "I_queue",
        }

    def verify_idempotency(
        self,
        operation_id: str,
        key: str,
        first_result: Any,
        second_result: Any,
    ) -> dict[str, Any]:
        """Verify operation is idempotent by comparing repeated results."""
        # Find config
        config = next(
            (c for c in self.idempotency_configs if c.operation_id == operation_id), None
        )

        if not config:
            return {"error": f"Unknown operation: {operation_id}"}

        if not config.idempotent:
            return {
                "idempotent": False,
                "operation_id": operation_id,
                "note": "Operation is not declared idempotent",
            }

        # Check results are equivalent
        equivalent = first_result == second_result

        return {
            "idempotent": config.idempotent,
            "verified": equivalent,
            "operation_id": operation_id,
            "key": key,
            "equivalent_results": equivalent,
            "invariant": "I_idempotency",
        }

    def get_operational_insights(self) -> list[dict[str, Any]]:
        """Get general operational architecture insights."""
        return [
            {
                "insight": "Cache without source of truth causes data loss",
                "evidence": "Writes to cache lost when cache evicted or cleared",
                "recommendation": "Always declare authoritative source for cached data",
                "invariant": "I_cache",
            },
            {
                "insight": "Unbounded staleness causes consistency violations",
                "evidence": "Reading stale data after source update causes bugs",
                "recommendation": "Declare and enforce maximum staleness bounds",
                "invariant": "I_cache",
            },
            {
                "insight": "Non-monotonic fallback creates surprise features",
                "evidence": "Degraded mode exposing features not in full mode",
                "recommendation": "Each fallback level must be subset of previous",
                "invariant": "I_fallback",
            },
            {
                "insight": "Exactly-once delivery requires deduplication",
                "evidence": "Network retries cause duplicate processing",
                "recommendation": "Enable deduplication with explicit time window",
                "invariant": "I_queue",
            },
            {
                "insight": "Retries without DLQ cause infinite loops",
                "evidence": "Poison messages retried forever blocking queue",
                "recommendation": "Enable dead letter queue for failed messages",
                "invariant": "I_queue",
            },
            {
                "insight": "Idempotent operations need key extraction",
                "evidence": "Cannot deduplicate without identifying key",
                "recommendation": "Define how to extract idempotency key",
                "invariant": "I_idempotency",
            },
        ]
