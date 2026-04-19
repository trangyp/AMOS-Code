"""
Repo Doctor Ω∞∞∞∞∞ - Phase 3 Control System Invariants

Invariants for time, consistency, cache, identity, capability,
queue, fallback, lineage, deprecation, audit, escalation,
control loop, failure domains, and negative capability.

These invariants capture the deeper architectural truth that
a repo is a closed-loop control system, not just an implementation.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state.basis import StateDimension
    from ..state.observables import Observable


@dataclass
class InvariantResult:
    """Result of invariant check."""

    dimension: StateDimension
    passed: bool
    severity: float  # 0-1, higher is worse
    message: str
    observables: List[Observable]


class ClockInvariant:
    """
    I_clock = 1 iff all correctness-critical time semantics are
    explicitly modeled, bounded, and consistent across components.
    """

    DIMENSION = "clock_semantics"  # Will be StateDimension.CLOCK_SEMANTICS

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check clock semantics invariant."""
        from ..state.basis import StateDimension

        clock_obs = [o for o in observables if o.dimension == StateDimension.CLOCK_SEMANTICS]

        if not clock_obs:
            return InvariantResult(
                dimension=StateDimension.CLOCK_SEMANTICS,
                passed=True,
                severity=0.0,
                message="No clock semantic issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in clock_obs)
        return InvariantResult(
            dimension=StateDimension.CLOCK_SEMANTICS,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Clock semantic issues: {len(clock_obs)}",
            observables=clock_obs,
        )


class CacheInvariant:
    """
    I_cache = 1 iff every cache has declared authority, invalidation
    rules, staleness bounds, and safety under cold/warm transitions.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check cache coherence invariant."""
        from ..state.basis import StateDimension

        cache_obs = [o for o in observables if o.dimension == StateDimension.CACHE_COHERENCE]

        if not cache_obs:
            return InvariantResult(
                dimension=StateDimension.CACHE_COHERENCE,
                passed=True,
                severity=0.0,
                message="No cache coherence issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in cache_obs)
        return InvariantResult(
            dimension=StateDimension.CACHE_COHERENCE,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Cache coherence issues: {len(cache_obs)}",
            observables=cache_obs,
        )


class ConsistencyInvariant:
    """
    I_consistency = 1 iff each critical state domain declares its
    consistency model and all dependent workflows are valid within that model.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check consistency model invariant."""
        from ..state.basis import StateDimension

        consistency_obs = [
            o for o in observables if o.dimension == StateDimension.CONSISTENCY_MODEL
        ]

        if not consistency_obs:
            return InvariantResult(
                dimension=StateDimension.CONSISTENCY_MODEL,
                passed=True,
                severity=0.0,
                message="No consistency model issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in consistency_obs)
        return InvariantResult(
            dimension=StateDimension.CONSISTENCY_MODEL,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Consistency model issues: {len(consistency_obs)}",
            observables=consistency_obs,
        )


class IdentityLifecycleInvariant:
    """
    I_identity_lifecycle = 1 iff credentials, principals, trust anchors,
    rotation paths, and revocation semantics are explicit and compatible
    with all dependent surfaces.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check identity lifecycle invariant."""
        from ..state.basis import StateDimension

        identity_obs = [o for o in observables if o.dimension == StateDimension.IDENTITY_LIFECYCLE]

        if not identity_obs:
            return InvariantResult(
                dimension=StateDimension.IDENTITY_LIFECYCLE,
                passed=True,
                severity=0.0,
                message="No identity lifecycle issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in identity_obs)
        return InvariantResult(
            dimension=StateDimension.IDENTITY_LIFECYCLE,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Identity lifecycle issues: {len(identity_obs)}",
            observables=identity_obs,
        )


class CapabilityInvariant:
    """
    I_capability = 1 iff every privileged action is granted by
    explicit scoped capability rather than ambient authority.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check capability discipline invariant."""
        from ..state.basis import StateDimension

        cap_obs = [o for o in observables if o.dimension == StateDimension.CAPABILITY_DISCIPLINE]

        if not cap_obs:
            return InvariantResult(
                dimension=StateDimension.CAPABILITY_DISCIPLINE,
                passed=True,
                severity=0.0,
                message="No capability discipline issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in cap_obs)
        return InvariantResult(
            dimension=StateDimension.CAPABILITY_DISCIPLINE,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Capability discipline issues: {len(cap_obs)}",
            observables=cap_obs,
        )


class QueueInvariant:
    """
    I_queue = 1 iff retries, backpressure, queue ordering,
    idempotency, and failure sinks are explicit and mutually compatible.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check queue/backpressure invariant."""
        from ..state.basis import StateDimension

        queue_obs = [o for o in observables if o.dimension == StateDimension.QUEUE_BACKPRESSURE]

        if not queue_obs:
            return InvariantResult(
                dimension=StateDimension.QUEUE_BACKPRESSURE,
                passed=True,
                severity=0.0,
                message="No queue/backpressure issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in queue_obs)
        return InvariantResult(
            dimension=StateDimension.QUEUE_BACKPRESSURE,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Queue/backpressure issues: {len(queue_obs)}",
            observables=queue_obs,
        )


class FallbackInvariant:
    """
    I_fallback = 1 iff every fallback path preserves declared
    safety, authority, and observability properties.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check fallback topology invariant."""
        from ..state.basis import StateDimension

        fallback_obs = [o for o in observables if o.dimension == StateDimension.FALLBACK_TOPOLOGY]

        if not fallback_obs:
            return InvariantResult(
                dimension=StateDimension.FALLBACK_TOPOLOGY,
                passed=True,
                severity=0.0,
                message="No fallback topology issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in fallback_obs)
        return InvariantResult(
            dimension=StateDimension.FALLBACK_TOPOLOGY,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Fallback topology issues: {len(fallback_obs)}",
            observables=fallback_obs,
        )


class IdempotencyInvariant:
    """
    I_idempotency = 1 iff every retriable or replayable operation
    declares and preserves idempotency semantics at the correct
    architectural boundary.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check idempotency boundary invariant."""
        from ..state.basis import StateDimension

        idem_obs = [o for o in observables if o.dimension == StateDimension.IDEMPOTENCY_BOUNDARY]

        if not idem_obs:
            return InvariantResult(
                dimension=StateDimension.IDEMPOTENCY_BOUNDARY,
                passed=True,
                severity=0.0,
                message="No idempotency boundary issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in idem_obs)
        return InvariantResult(
            dimension=StateDimension.IDEMPOTENCY_BOUNDARY,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Idempotency boundary issues: {len(idem_obs)}",
            observables=idem_obs,
        )


class ControlLoopInvariant:
    """
    I_control_stable = 1 iff all critical architectural control loops
    are bounded, damped, and free of self-amplifying oscillation.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check control loop stability invariant."""
        from ..state.basis import StateDimension

        control_obs = [
            o for o in observables if o.dimension == StateDimension.CONTROL_LOOP_STABILITY
        ]

        if not control_obs:
            return InvariantResult(
                dimension=StateDimension.CONTROL_LOOP_STABILITY,
                passed=True,
                severity=0.0,
                message="No control loop stability issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in control_obs)
        return InvariantResult(
            dimension=StateDimension.CONTROL_LOOP_STABILITY,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Control loop stability issues: {len(control_obs)}",
            observables=control_obs,
        )


class FailureDomainsInvariant:
    """
    I_failure_domains = 1 iff declared independent paths do not
    share unmodeled critical failure domains.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check failure domain isolation invariant."""
        from ..state.basis import StateDimension

        failure_obs = [o for o in observables if o.dimension == StateDimension.FAILURE_DOMAINS]

        if not failure_obs:
            return InvariantResult(
                dimension=StateDimension.FAILURE_DOMAINS,
                passed=True,
                severity=0.0,
                message="No failure domain overlap issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in failure_obs)
        return InvariantResult(
            dimension=StateDimension.FAILURE_DOMAINS,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Failure domain overlap issues: {len(failure_obs)}",
            observables=failure_obs,
        )


class NegativeCapabilityInvariant:
    """
    I_negative_capability = 1 iff all forbidden states and forbidden
    transitions are explicitly represented and blocked.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check negative capability invariant."""
        from ..state.basis import StateDimension

        neg_obs = [o for o in observables if o.dimension == StateDimension.NEGATIVE_CAPABILITY]

        if not neg_obs:
            return InvariantResult(
                dimension=StateDimension.NEGATIVE_CAPABILITY,
                passed=True,
                severity=0.0,
                message="No negative capability issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in neg_obs)
        return InvariantResult(
            dimension=StateDimension.NEGATIVE_CAPABILITY,
            passed=max_severity < 0.5,
            severity=max_severity,
            message=f"Negative capability issues: {len(neg_obs)}",
            observables=neg_obs,
        )


class ArchitecturalDebtInvariant:
    """
    I_debt = 1 iff architecture debt remains explicitly measured,
    bounded, and non-compounding.
    """

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        """Check architectural debt invariant."""
        from ..state.basis import StateDimension

        debt_obs = [o for o in observables if o.dimension == StateDimension.ARCHITECTURAL_DEBT]

        if not debt_obs:
            return InvariantResult(
                dimension=StateDimension.ARCHITECTURAL_DEBT,
                passed=True,
                severity=0.0,
                message="No architectural debt issues detected",
                observables=[],
            )

        max_severity = max(o.severity for o in debt_obs)
        return InvariantResult(
            dimension=StateDimension.ARCHITECTURAL_DEBT,
            passed=max_severity < 0.7,  # Debt is less critical
            severity=max_severity,
            message=f"Architectural debt issues: {len(debt_obs)}",
            observables=debt_obs,
        )


# Registry of all Phase 3 invariants
PHASE3_INVARIANTS = [
    ClockInvariant,
    CacheInvariant,
    ConsistencyInvariant,
    IdentityLifecycleInvariant,
    CapabilityInvariant,
    QueueInvariant,
    FallbackInvariant,
    IdempotencyInvariant,
    ControlLoopInvariant,
    FailureDomainsInvariant,
    NegativeCapabilityInvariant,
    ArchitecturalDebtInvariant,
]
