"""Layer 18: Distributed Systems Physics Invariants (Phase 5 - Ω∞∞∞∞∞).

Phase 5 invariants addressing distributed systems physics:
- Truth arbitration across domains
- Irreversibility classification and compensation
- Quiescence integrity for safe stopping
- Policy precedence hierarchy
- Adaptive stability bounds
- Architectural entropy
"""
from __future__ import annotations

from typing import Any

from ..layer18_physics_engine import DistributedPhysicsEngine, InvariantResult as PhysicsResult
from ..state.basis import StateDimension
from .base import Invariant, InvariantResult, InvariantSeverity


class TruthArbitrationInvariant(Invariant):
    """Invariant: Distributed truth domains must have arbitration mechanisms."""

    def __init__(self):
        super().__init__(
            name="truth_arbitration",
            severity=InvariantSeverity.CRITICAL
        )
        self.engine = DistributedPhysicsEngine()
        self.dimension = StateDimension.TRUTH_ARBITRATION

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check truth arbitration across domains."""
        ctx = context or {}
        domains = ctx.get("domains", [])

        if not domains:
            # No distributed domains defined - assume single domain, passes
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=InvariantSeverity.WARNING,
                message="No distributed domains defined - assuming single domain architecture",
                details={"domains_checked": 0},
            )

        result = self.engine.validate_truth_arbitration(domains)

        return InvariantResult(
            name=self.name,
            passed=result.satisfied,
            severity=InvariantSeverity.CRITICAL if not result.satisfied else InvariantSeverity.WARNING,
            message="; ".join(result.evidence) if result.evidence else "Truth arbitration validated",
            details={
                "domains_checked": len(domains),
                "failures": [e for e in result.evidence if "No mechanism" in e],
                "engine_id": self.engine.engine_id,
                "dimension": self.dimension.value,
            },
        )


class IrreversibilityInvariant(Invariant):
    """Invariant: State transitions must be classified by reversibility."""

    def __init__(self):
        super().__init__(
            name="irreversibility_management",
            severity=InvariantSeverity.CRITICAL
        )
        self.engine = DistributedPhysicsEngine()
        self.dimension = StateDimension.IRREVERSIBILITY_MANAGEMENT

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check irreversibility classification."""
        ctx = context or {}
        transitions = ctx.get("transitions", [])

        if not transitions:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=InvariantSeverity.WARNING,
                message="No state transitions defined",
                details={"transitions_checked": 0},
            )

        result = self.engine.validate_irreversibility(transitions)

        return InvariantResult(
            name=self.name,
            passed=result.satisfied,
            severity=InvariantSeverity.CRITICAL if not result.satisfied else InvariantSeverity.WARNING,
            message="; ".join(result.evidence) if result.evidence else "Irreversibility classification valid",
            details={
                "transitions_checked": len(transitions),
                "failures": [e for e in result.evidence if "Not classified" in e],
                "engine_id": self.engine.engine_id,
                "dimension": self.dimension.value,
            },
        )


class CompensationInvariant(Invariant):
    """Invariant: Irreversible transitions must have compensation actions."""

    def __init__(self):
        super().__init__(
            name="compensation_semantics",
            severity=InvariantSeverity.CRITICAL
        )
        self.engine = DistributedPhysicsEngine()
        self.dimension = StateDimension.IRREVERSIBILITY_MANAGEMENT

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check compensation for irreversible actions."""
        ctx = context or {}
        transitions = ctx.get("transitions", [])

        if not transitions:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=InvariantSeverity.WARNING,
                message="No state transitions to check for compensation",
                details={"transitions_checked": 0},
            )

        result = self.engine.validate_compensation(transitions)

        return InvariantResult(
            name=self.name,
            passed=result.satisfied,
            severity=InvariantSeverity.CRITICAL if not result.satisfied else InvariantSeverity.WARNING,
            message="; ".join(result.evidence) if result.evidence else "Compensation semantics valid",
            details={
                "transitions_checked": len(transitions),
                "failures": [e for e in result.evidence if "No compensation" in e],
                "engine_id": self.engine.engine_id,
                "dimension": self.dimension.value,
            },
        )


class QuiescenceInvariant(Invariant):
    """Invariant: Subsystems must define quiescent states."""

    def __init__(self):
        super().__init__(
            name="quiescence_integrity",
            severity=InvariantSeverity.ERROR
        )
        self.engine = DistributedPhysicsEngine()
        self.dimension = StateDimension.QUIESCENCE_INTEGRITY

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check quiescent state definitions."""
        ctx = context or {}
        subsystems = ctx.get("subsystems", [])

        if not subsystems:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=InvariantSeverity.WARNING,
                message="No subsystems defined",
                details={"subsystems_checked": 0},
            )

        result = self.engine.validate_quiescence(subsystems)

        return InvariantResult(
            name=self.name,
            passed=result.satisfied,
            severity=InvariantSeverity.ERROR if not result.satisfied else InvariantSeverity.WARNING,
            message="; ".join(result.evidence) if result.evidence else "Quiescence integrity valid",
            details={
                "subsystems_checked": len(subsystems),
                "failures": [e for e in result.evidence if "No quiescent" in e],
                "engine_id": self.engine.engine_id,
                "dimension": self.dimension.value,
            },
        )


class PolicyPrecedenceInvariant(Invariant):
    """Invariant: Policy layers must have defined precedence."""

    def __init__(self):
        super().__init__(
            name="policy_precedence",
            severity=InvariantSeverity.CRITICAL
        )
        self.engine = DistributedPhysicsEngine()
        self.dimension = StateDimension.POLICY_PRECEDENCE

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check policy layer precedence."""
        ctx = context or {}
        layers = ctx.get("policy_layers", [])

        if not layers:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=InvariantSeverity.WARNING,
                message="No policy layers defined",
                details={"layers_checked": 0},
            )

        result = self.engine.validate_policy_precedence(layers)

        return InvariantResult(
            name=self.name,
            passed=result.satisfied,
            severity=InvariantSeverity.CRITICAL if not result.satisfied else InvariantSeverity.WARNING,
            message="; ".join(result.evidence) if result.evidence else "Policy precedence established",
            details={
                "layers_checked": len(layers),
                "failures": [e for e in result.evidence if "No precedence" in e],
                "engine_id": self.engine.engine_id,
                "dimension": self.dimension.value,
            },
        )


class AdaptiveStabilityInvariant(Invariant):
    """Invariant: Adaptive control loops must have bounded drift."""

    def __init__(self):
        super().__init__(
            name="adaptive_stability",
            severity=InvariantSeverity.ERROR
        )
        self.engine = DistributedPhysicsEngine()
        self.dimension = StateDimension.ADAPTIVE_STABILITY

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check adaptive loop bounds."""
        ctx = context or {}
        loops = ctx.get("adaptive_loops", [])

        if not loops:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=InvariantSeverity.WARNING,
                message="No adaptive loops defined",
                details={"loops_checked": 0},
            )

        result = self.engine.validate_adaptive_bounds(loops)

        return InvariantResult(
            name=self.name,
            passed=result.satisfied,
            severity=InvariantSeverity.ERROR if not result.satisfied else InvariantSeverity.WARNING,
            message="; ".join(result.evidence) if result.evidence else "Adaptive stability bounds valid",
            details={
                "loops_checked": len(loops),
                "failures": [e for e in result.evidence if "No drift bound" in e],
                "engine_id": self.engine.engine_id,
                "dimension": self.dimension.value,
            },
        )


class EntropyInvariant(Invariant):
    """Invariant: Architectural entropy must remain bounded."""

    def __init__(self):
        super().__init__(
            name="architectural_entropy",
            severity=InvariantSeverity.WARNING
        )
        self.engine = DistributedPhysicsEngine()
        self.dimension = StateDimension.ARCHITECTURAL_ENTROPY

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check architectural entropy bounds."""
        ctx = context or {}
        measurements = ctx.get("entropy", [])

        if not measurements:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=InvariantSeverity.WARNING,
                message="No entropy measurements provided",
                details={"measurements_checked": 0},
            )

        result = self.engine.validate_entropy(measurements)

        high_entropy = [e for e in result.evidence if "High entropy" in e]

        return InvariantResult(
            name=self.name,
            passed=result.satisfied,
            severity=InvariantSeverity.WARNING,
            message="; ".join(result.evidence) if result.evidence else "Architectural entropy bounded",
            details={
                "measurements_checked": len(measurements),
                "high_entropy_count": len(high_entropy),
                "failures": high_entropy,
                "engine_id": self.engine.engine_id,
                "dimension": self.dimension.value,
            },
        )


# Export all Layer 18 invariants
__all__ = [
    "TruthArbitrationInvariant",
    "IrreversibilityInvariant",
    "CompensationInvariant",
    "QuiescenceInvariant",
    "PolicyPrecedenceInvariant",
    "AdaptiveStabilityInvariant",
    "EntropyInvariant",
]
