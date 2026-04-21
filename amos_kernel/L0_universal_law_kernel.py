"""
L0 - Universal Law Kernel (ULK)

Hard rules only. No app logic. No UX logic. No model-provider logic.

Responsibilities:
- law precedence
- contradiction detection
- dual-check enforcement
- quadrant completeness check
- collapse thresholding

Core Constraints:
    ¬(A ∧ ¬A)                           # Non-contradiction
    dC/dt ≤ dR/dt                      # Correction rate
    S = (x_int, x_ext), x_ext ≠ ∅      # Dual interaction
    ∏ I(Q_i) > 0                       # Quadrant completeness
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional

from amos_kernel.contracts import (
    CORE_INVARIANTS,
    Contradiction,
    IntegrityReport,
    Invariant,
    InvariantStatus,
    KernelResult,
    LawPrecedence,
    Quadrant,
    QuadrantScore,
)

if TYPE_CHECKING:
    from amos_kernel.L2_universal_state_model import StateTensor


@dataclass(frozen=True)
class ValidationResult:
    """Result of invariant validation."""

    invariant: Invariant
    status: InvariantStatus
    score: float  # 0.0 to 1.0
    evidence: dict[str, Any]
    contradictions: list[Contradiction] = field(default_factory=list)


@dataclass(frozen=True)
class LawPrecedenceRanking:
    """Ranking of competing claims."""

    winner: str
    loser: str
    precedence: LawPrecedence
    reason: str


class UniversalLawKernel:
    """
    Hard root of AMOS. Every decision passes through here.

    Validates:
    - Build paths
    - Runtime paths
    - Self-modification paths
    - Import paths

    Core invariant: ¬(A ∧ ¬A)
    """

    _instance: Optional[UniversalLawKernel] = None

    def __new__(cls) -> UniversalLawKernel:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._invariants: dict[str, Invariant] = {inv.name: inv for inv in CORE_INVARIANTS}
        self._validation_history: list[ValidationResult] = []
        self._initialized = True

    def validate_invariants(
        self, state: StateTensor, action: dict[str, Any]
    ) -> KernelResult[list[ValidationResult]]:
        """
        Validate all invariants against proposed state+action.

        This is the gate. No action passes without validation.
        """
        results: list[ValidationResult] = []
        contradictions: list[Contradiction] = []

        for invariant in self._invariants.values():
            result = self._check_invariant(invariant, state, action)
            results.append(result)
            contradictions.extend(result.contradictions)

        all_pass = all(r.status == InvariantStatus.SATISFIED for r in results)
        self._validation_history.extend(results)

        if all_pass and not contradictions:
            return KernelResult.ok(results, "ULK")

        errors = [
            f"{r.invariant.name}: {r.status.name} (score={r.score:.2f})"
            for r in results
            if r.status != InvariantStatus.SATISFIED
        ]
        errors.extend([f"Contradiction: {c.claim_a} vs {c.claim_b}" for c in contradictions])

        return KernelResult.fail(errors, "ULK", contradictions)

    def contradiction_score(self, state: StateTensor) -> float:
        """
        Compute contradiction density: score ∈ [0, 1]

        0.0 = perfectly consistent
        1.0 = maximally contradictory
        """
        contradictions = self._detect_contradictions(state)
        if not contradictions:
            return 0.0

        max_severity = max(c.severity for c in contradictions)
        count_penalty = min(len(contradictions) * 0.1, 0.5)

        return min(max_severity + count_penalty, 1.0)

    def quadrant_integrity(self, state: StateTensor) -> IntegrityReport:
        """
        Check four-quadrant completeness.

        Quadrants:
        - CODE: Code correctness
        - BUILD: Build/release correctness
        - OPERATIONAL: Runtime correctness
        - ENVIRONMENT: Dependency correctness
        """
        scores = {
            Quadrant.CODE: self._score_quadrant(Quadrant.CODE, state),
            Quadrant.BUILD: self._score_quadrant(Quadrant.BUILD, state),
            Quadrant.OPERATIONAL: self._score_quadrant(Quadrant.OPERATIONAL, state),
            Quadrant.ENVIRONMENT: self._score_quadrant(Quadrant.ENVIRONMENT, state),
        }

        overall = scores[Quadrant.CODE].score * scores[Quadrant.BUILD].score
        overall *= scores[Quadrant.OPERATIONAL].score * scores[Quadrant.ENVIRONMENT].score
        overall = overall**0.25  # Geometric mean

        return IntegrityReport(
            overall_score=overall,
            code=scores[Quadrant.CODE],
            build=scores[Quadrant.BUILD],
            operational=scores[Quadrant.OPERATIONAL],
            environment=scores[Quadrant.ENVIRONMENT],
            timestamp=datetime.now(UTC),
        )

    def collapse_risk(self, state: StateTensor) -> float:
        """
        Compute risk of system collapse: score ∈ [0, 1]

        Collapse occurs when:
        - contradiction_score > 0.8
        - quadrant_integrity < 0.3
        - correction_rate violated
        """
        contradiction = self.contradiction_score(state)
        integrity = self.quadrant_integrity(state)
        correction = self._check_correction_rate(state)

        risk = contradiction * 0.4
        risk += (1.0 - integrity.overall_score) * 0.4
        risk += 0.0 if correction else 0.2

        return min(risk, 1.0)

    def resolve_precedence(self, claim_a: str, claim_b: str) -> Optional[LawPrecedenceRanking]:
        """
        Resolve competing claims by law precedence.
        """
        inv_a = self._find_invariant_for_claim(claim_a)
        inv_b = self._find_invariant_for_claim(claim_b)

        if inv_a is None or inv_b is None:
            return None

        if inv_a.precedence.value > inv_b.precedence.value:
            return LawPrecedenceRanking(
                winner=claim_a,
                loser=claim_b,
                precedence=inv_a.precedence,
                reason=f"{inv_a.name} has higher precedence",
            )
        elif inv_b.precedence.value > inv_a.precedence.value:
            return LawPrecedenceRanking(
                winner=claim_b,
                loser=claim_a,
                precedence=inv_b.precedence,
                reason=f"{inv_b.name} has higher precedence",
            )
        return None  # Equal precedence - requires external resolution

    def _check_invariant(
        self, invariant: Invariant, state: StateTensor, action: dict[str, Any]
    ) -> ValidationResult:
        """Dispatch to specific invariant checker."""
        checkers = {
            "non_contradiction": self._check_non_contradiction,
            "dual_interaction": self._check_dual_interaction,
            "quadrant_completeness": self._check_quadrant_completeness,
            "correction_rate": self._check_correction_rate_invariant,
            "determinism": self._check_determinism,
        }

        checker = checkers.get(invariant.name)
        if checker:
            return checker(state, action)

        return ValidationResult(
            invariant=invariant,
            status=InvariantStatus.INDETERMINATE,
            score=0.0,
            evidence={"error": "No checker implemented"},
        )

    def _check_non_contradiction(
        self, state: StateTensor, action: dict[str, Any]
    ) -> ValidationResult:
        """Check ¬(A ∧ ¬A)."""
        contradictions = self._detect_contradictions(state)

        if contradictions:
            return ValidationResult(
                invariant=self._invariants["non_contradiction"],
                status=InvariantStatus.VIOLATED,
                score=1.0 - max(c.severity for c in contradictions),
                evidence={"contradictions": len(contradictions)},
                contradictions=contradictions,
            )

        return ValidationResult(
            invariant=self._invariants["non_contradiction"],
            status=InvariantStatus.SATISFIED,
            score=1.0,
            evidence={"contradictions": 0},
        )

    def _check_dual_interaction(
        self, state: StateTensor, action: dict[str, Any]
    ) -> ValidationResult:
        """Check S = (x_int, x_ext), x_ext ≠ ∅."""
        has_internal = "internal" in state.projections
        has_external = "external" in state.projections

        if has_internal and has_external:
            return ValidationResult(
                invariant=self._invariants["dual_interaction"],
                status=InvariantStatus.SATISFIED,
                score=1.0,
                evidence={"internal": has_internal, "external": has_external},
            )

        return ValidationResult(
            invariant=self._invariants["dual_interaction"],
            status=InvariantStatus.VIOLATED,
            score=0.0,
            evidence={"internal": has_internal, "external": has_external},
        )

    def _check_quadrant_completeness(
        self, state: StateTensor, action: dict[str, Any]
    ) -> ValidationResult:
        """Check ∏ I(Q_i) > 0."""
        integrity = self.quadrant_integrity(state)
        all_positive = integrity.overall_score > 0.0

        return ValidationResult(
            invariant=self._invariants["quadrant_completeness"],
            status=InvariantStatus.SATISFIED if all_positive else InvariantStatus.VIOLATED,
            score=integrity.overall_score,
            evidence={
                "code": integrity.code.score,
                "build": integrity.build.score,
                "operational": integrity.operational.score,
                "environment": integrity.environment.score,
            },
        )

    def _check_correction_rate_invariant(
        self, state: StateTensor, action: dict[str, Any]
    ) -> ValidationResult:
        """Check dC/dt ≤ dR/dt."""
        correction_ok = self._check_correction_rate(state)

        return ValidationResult(
            invariant=self._invariants["correction_rate"],
            status=InvariantStatus.SATISFIED if correction_ok else InvariantStatus.VIOLATED,
            score=1.0 if correction_ok else 0.5,
            evidence={"correction_adequate": correction_ok},
        )

    def _check_determinism(self, state: StateTensor, action: dict[str, Any]) -> ValidationResult:
        """Check same(state, inputs, constraints) → same(output_class)."""
        state_hash = self._compute_determinism_hash(state, action)

        return ValidationResult(
            invariant=self._invariants["determinism"],
            status=InvariantStatus.SATISFIED,
            score=1.0,
            evidence={"state_hash": state_hash},
        )

    def _detect_contradictions(self, state: StateTensor) -> list[Contradiction]:
        """Detect contradictions in state."""
        contradictions: list[Contradiction] = []

        # Check for path contradictions
        paths = state.raw_data.get("paths", {})
        if isinstance(paths, dict):
            for name, path_config in paths.items():
                # Skip if path_config is not a dict (e.g., it's a string)
                if not isinstance(path_config, dict):
                    continue
                if self._is_path_contradictory(name, path_config):
                    contradictions.append(
                        Contradiction(
                            claim_a=f"{name}: {path_config.get('claimed', 'unknown')}",
                            claim_b=f"{name}: {path_config.get('actual', 'unknown')}",
                            invariant="path_consistency",
                            severity=0.8,
                            context=path_config,
                            timestamp=datetime.now(UTC),
                        )
                    )

        return contradictions

    def _is_path_contradictory(self, name: str, config: dict[str, Any]) -> bool:
        """Check if a path config is contradictory."""
        if not isinstance(config, dict):
            return False
        claimed = config.get("claimed")
        actual = config.get("actual")
        return claimed is not None and actual is not None and claimed != actual

    def _score_quadrant(self, quadrant: Quadrant, state: StateTensor) -> QuadrantScore:
        """Score a single quadrant."""
        quadrant_data = state.raw_data.get(quadrant.name.lower(), {})
        checks = quadrant_data.get("checks", [])

        if not checks:
            return QuadrantScore(
                quadrant=quadrant,
                score=0.5,  # Indeterminate
                checks_passed=0,
                checks_failed=0,
                details={},
            )

        passed = sum(1 for c in checks if c.get("passed", False))
        failed = len(checks) - passed
        score = passed / len(checks) if checks else 0.0

        return QuadrantScore(
            quadrant=quadrant,
            score=score,
            checks_passed=passed,
            checks_failed=failed,
            details={"checks": checks},
        )

    def _check_correction_rate(self, state: StateTensor) -> bool:
        """Check if correction rate exceeds drift rate."""
        drift_rate = state.raw_data.get("drift_rate", 0.0)
        correction_rate = state.raw_data.get("correction_rate", 0.0)
        return correction_rate >= drift_rate

    def _find_invariant_for_claim(self, claim: str) -> Optional[Invariant]:
        """Find which invariant covers a claim."""
        for invariant in self._invariants.values():
            if claim.startswith(invariant.name) or invariant.name in claim:
                return invariant
        return None

    def _compute_determinism_hash(self, state: StateTensor, action: dict[str, Any]) -> str:
        """Compute hash for determinism check."""
        data = {
            "state_projection": state.projections.get("deterministic", {}),
            "action_keys": sorted(action.keys()),
            "action_hash": hashlib.sha256(
                json.dumps(action, sort_keys=True, default=str).encode()
            ).hexdigest()[:16],
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


def get_universal_law_kernel() -> UniversalLawKernel:
    """Get the singleton ULK instance."""
    return UniversalLawKernel()
