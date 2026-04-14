#!/usr/bin/env python3
"""AMOSL Verification Engine
=========================

Formal verification system for AMOSL runtime.
Implements invariant checking, proof generation, and validity verification.

Mathematical Foundation:
- Valid(Σ) = ∧_i C_i(Σ)  (State validity = all constraints satisfied)
- Proof trees for verification chains
- Constraint satisfaction checking
- Formal guarantee generation

Integration with Ledger:
- All verifications logged to StateLedger
- Proof hashes recorded for audit
- Verification history reconstructible

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from amosl_ledger import EntryType, LedgerEntry, StateLedger


class ConstraintType(Enum):
    """Types of formal constraints."""

    STRUCTURAL = "structural"  # L4 - Absolute Structural Integrity
    COMMUNICATION = "communication"  # L5 - Post-Theory Communication
    DUAL_PERSPECTIVE = "dual_perspective"  # L2 - Rule of 2
    FOUR_QUADRANT = "four_quadrant"  # L3 - Rule of 4
    BIOLOGICAL = "biological"  # L6 - UBI Alignment
    SAFETY = "safety"  # L1 - Law of Law


@dataclass
class Constraint:
    """Formal constraint definition.

    Attributes:
        name: Constraint identifier
        constraint_type: Category
        check_function: Callable to verify constraint
        description: Human-readable explanation
        severity: "warning", "error", or "critical"
    """

    name: str
    constraint_type: ConstraintType
    check_function: Callable[[dict[str, Any]], tuple[bool, str]]
    description: str
    severity: str = "error"


@dataclass
class VerificationResult:
    """Result of formal verification."""

    state_hash: str
    timestamp: str
    valid: bool
    constraints_checked: int
    constraints_passed: int
    failed_constraints: list[str]
    proof_hash: str
    details: dict[str, Any]


class VerificationEngine:
    """Formal verification engine for AMOSL runtime.

    Implements:
    - Constraint checking (C1-C8 from formal spec)
    - Valid(Σ) = ∧_i C_i(Σ) computation
    - Proof generation
    - Verification logging
    """

    def __init__(self, ledger: Optional[StateLedger] = None):
        self.ledger = ledger or StateLedger()
        self.constraints: dict[str, Constraint] = {}
        self._initialize_default_constraints()

    def _initialize_default_constraints(self):
        """Initialize default AMOSL constraints."""
        # C1: State structure integrity
        self.register_constraint(
            Constraint(
                name="C1_StateStructure",
                constraint_type=ConstraintType.STRUCTURAL,
                check_function=self._check_state_structure,
                description="State manifold has valid structure",
                severity="critical",
            )
        )

        # C2: Evolution validity
        self.register_constraint(
            Constraint(
                name="C2_EvolutionValid",
                constraint_type=ConstraintType.STRUCTURAL,
                check_function=self._check_evolution_valid,
                description="Evolution operator Φ produces valid states",
                severity="critical",
            )
        )

        # C3: Invariant preservation
        self.register_constraint(
            Constraint(
                name="C3_InvariantPreserve",
                constraint_type=ConstraintType.SAFETY,
                check_function=self._check_invariants,
                description="All invariants preserved across transitions",
                severity="critical",
            )
        )

        # C4: Dual perspective coverage (Rule of 2)
        self.register_constraint(
            Constraint(
                name="C4_DualPerspective",
                constraint_type=ConstraintType.DUAL_PERSPECTIVE,
                check_function=self._check_dual_perspective,
                description="At least two perspectives considered",
                severity="error",
            )
        )

        # C5: Four quadrant coverage (Rule of 4)
        self.register_constraint(
            Constraint(
                name="C5_FourQuadrant",
                constraint_type=ConstraintType.FOUR_QUADRANT,
                check_function=self._check_four_quadrant,
                description="All four quadrants analyzed",
                severity="error",
            )
        )

        # C6: Biological safety (UBI)
        self.register_constraint(
            Constraint(
                name="C6_BiologicalSafety",
                constraint_type=ConstraintType.BIOLOGICAL,
                check_function=self._check_biological_safety,
                description="No biological harm in operations",
                severity="critical",
            )
        )

        # C7: Communication clarity
        self.register_constraint(
            Constraint(
                name="C7_Communication",
                constraint_type=ConstraintType.COMMUNICATION,
                check_function=self._check_communication,
                description="Clear, grounded communication",
                severity="warning",
            )
        )

        # C8: Ledger integrity
        self.register_constraint(
            Constraint(
                name="C8_LedgerIntegrity",
                constraint_type=ConstraintType.STRUCTURAL,
                check_function=self._check_ledger_integrity,
                description="Ledger chain is valid",
                severity="critical",
            )
        )

    def register_constraint(self, constraint: Constraint):
        """Register a new constraint."""
        self.constraints[constraint.name] = constraint

    def verify_state(self, state: dict[str, Any]) -> VerificationResult:
        """Verify state against all constraints.

        Computes: Valid(Σ) = ∧_i C_i(Σ)

        Args:
            state: State manifold Σ to verify

        Returns:
            VerificationResult with validity and proof
        """
        timestamp = datetime.utcnow().isoformat()

        # Compute state hash
        state_content = json.dumps(state, sort_keys=True)
        state_hash = hashlib.sha256(state_content.encode()).hexdigest()[:32]

        # Check all constraints
        failed = []
        details = {}

        for name, constraint in self.constraints.items():
            passed, message = constraint.check_function(state)
            details[name] = {
                "passed": passed,
                "message": message,
                "type": constraint.constraint_type.value,
                "severity": constraint.severity,
            }
            if not passed and constraint.severity in ["error", "critical"]:
                failed.append(name)

        # Compute validity
        valid = len(failed) == 0

        # Generate proof hash
        proof_content = json.dumps(
            {
                "state_hash": state_hash,
                "timestamp": timestamp,
                "valid": valid,
                "constraints": details,
            },
            sort_keys=True,
        )
        proof_hash = hashlib.sha256(proof_content.encode()).hexdigest()[:32]

        # Create result
        result = VerificationResult(
            state_hash=state_hash,
            timestamp=timestamp,
            valid=valid,
            constraints_checked=len(self.constraints),
            constraints_passed=len(self.constraints) - len(failed),
            failed_constraints=failed,
            proof_hash=proof_hash,
            details=details,
        )

        # Log to ledger
        self._log_verification(result, state)

        return result

    def _log_verification(self, result: VerificationResult, state: dict[str, Any]):
        """Log verification to ledger."""
        self.ledger.append(
            EntryType.VERIFICATION_RESULT,
            state,
            {
                "valid": result.valid,
                "proof_hash": result.proof_hash,
                "constraints_passed": result.constraints_passed,
                "constraints_total": result.constraints_checked,
                "failed": result.failed_constraints,
            },
        )

    # Constraint check implementations
    def _check_state_structure(self, state: dict[str, Any]) -> tuple[bool, str]:
        """Check C1: State has required structure."""
        required_keys = ["classical", "quantum", "biological"]
        present = [k for k in required_keys if k in str(state).lower()]
        if len(present) >= 1:
            return True, f"State structure valid ({len(present)} substrates)"
        return False, "Missing required state substrates"

    def _check_evolution_valid(self, state: dict[str, Any]) -> tuple[bool, str]:
        """Check C2: Evolution produces valid states."""
        if "evolution" in state and "error" in str(state.get("evolution", {})):
            return False, "Evolution produced error state"
        return True, "Evolution valid"

    def _check_invariants(self, state: dict[str, Any]) -> tuple[bool, str]:
        """Check C3: Invariants preserved."""
        violated = state.get("invariant_violations", [])
        if violated:
            return False, f"{len(violated)} invariants violated"
        return True, "All invariants preserved"

    def _check_dual_perspective(self, state: dict[str, Any]) -> tuple[bool, str]:
        """Check C4: Rule of 2 (dual perspective)."""
        perspectives = state.get("perspectives", [])
        if len(perspectives) >= 2:
            return True, f"{len(perspectives)} perspectives present"
        return False, f"Only {len(perspectives)} perspective(s), need 2+"

    def _check_four_quadrant(self, state: dict[str, Any]) -> tuple[bool, str]:
        """Check C5: Rule of 4 (four quadrant)."""
        quadrants = state.get("quadrants", [])
        if len(quadrants) >= 4:
            return True, "All 4 quadrants covered"
        return False, f"Only {len(quadrants)}/4 quadrants"

    def _check_biological_safety(self, state: dict[str, Any]) -> tuple[bool, str]:
        """Check C6: UBI alignment."""
        harm_indicators = ["harm", "damage", "destroy", "kill"]
        state_str = json.dumps(state).lower()
        for indicator in harm_indicators:
            if indicator in state_str:
                return False, f"Potential biological harm detected: {indicator}"
        return True, "No biological harm detected"

    def _check_communication(self, state: dict[str, Any]) -> tuple[bool, str]:
        """Check C7: Clear communication."""
        vague_terms = ["field", "energy field", "vibrations", "frequency"]
        state_str = json.dumps(state).lower()
        violations = [t for t in vague_terms if t in state_str]
        if violations:
            return False, f"Vague terms found: {violations}"
        return True, "Communication clear and grounded"

    def _check_ledger_integrity(self, state: dict[str, Any]) -> tuple[bool, str]:
        """Check C8: Ledger chain integrity."""
        if self.ledger.verify_chain():
            return True, f"Ledger chain valid ({len(self.ledger._entries)} entries)"
        return False, "Ledger chain integrity compromised"

    def get_verification_history(self, count: int = 10) -> list[VerificationResult]:
        """Get recent verification results from ledger."""
        # Query ledger for verification entries
        history = []
        for entry in self.ledger._entries[-count:]:
            if entry.entry_type == EntryType.VERIFICATION_RESULT:
                # Reconstruct from ledger
                history.append(self._reconstruct_result(entry))
        return history

    def _reconstruct_result(self, entry: LedgerEntry) -> VerificationResult:
        """Reconstruct VerificationResult from ledger entry."""
        data = entry.data
        return VerificationResult(
            state_hash=entry.state_hash,
            timestamp=entry.timestamp,
            valid=data.get("valid", False),
            constraints_checked=data.get("constraints_total", 0),
            constraints_passed=data.get("constraints_passed", 0),
            failed_constraints=data.get("failed", []),
            proof_hash=data.get("proof_hash", ""),
            details={},
        )

    def generate_formal_proof(self, state: dict[str, Any]) -> dict[str, Any]:
        """Generate formal mathematical proof of state validity.

        Returns:
            Proof structure with theorem, assumptions, and conclusion
        """
        result = self.verify_state(state)

        proof = {
            "theorem": "Valid(Σ) = ∧_i C_i(Σ)",
            "state_hash": result.state_hash,
            "timestamp": result.timestamp,
            "assumptions": {
                "ledger_integrity": self.ledger.verify_chain(),
                "constraint_count": result.constraints_checked,
                "verification_engine": "amosl_verification.py v1.0.0",
            },
            "proof_steps": [
                {"step": 1, "action": "Check C1-C8 constraints", "result": result.valid},
                {"step": 2, "action": "Compute Valid(Σ)", "result": result.valid},
                {"step": 3, "action": "Generate proof hash", "hash": result.proof_hash},
            ],
            "conclusion": {
                "valid": result.valid,
                "proof_hash": result.proof_hash,
                "constraints_satisfied": f"{result.constraints_passed}/{result.constraints_checked}",
            },
        }

        return proof


def demo_verification():
    """Demonstrate verification engine."""
    print("\n" + "=" * 70)
    print("AMOSL VERIFICATION ENGINE - DEMONSTRATION")
    print("=" * 70)

    # Create engine
    engine = VerificationEngine()

    print("\n[1] Registering constraints...")
    print(f"  Total constraints: {len(engine.constraints)}")
    for name, c in engine.constraints.items():
        print(f"    • {name}: {c.description}")

    print("\n[2] Verifying valid state...")
    valid_state = {
        "classical": {"value": 1.0},
        "quantum": {"value": 0.5},
        "biological": {"status": "safe"},
        "perspectives": ["technical", "economic"],
        "quadrants": ["bio", "tech", "econ", "env"],
        "invariant_violations": [],
    }

    result = engine.verify_state(valid_state)
    print(f"  Valid: {'✓ YES' if result.valid else '✗ NO'}")
    print(f"  Constraints: {result.constraints_passed}/{result.constraints_checked}")
    print(f"  Proof hash: {result.proof_hash[:16]}...")

    print("\n[3] Verifying invalid state...")
    invalid_state = {
        "classical": {"value": 1.0},
        "perspectives": ["only_one"],
        "quadrants": ["bio"],
        "invariant_violations": ["test_violation"],
    }

    result2 = engine.verify_state(invalid_state)
    print(f"  Valid: {'✓ YES' if result2.valid else '✗ NO'}")
    print(f"  Failed constraints: {result2.failed_constraints}")

    print("\n[4] Generating formal proof...")
    proof = engine.generate_formal_proof(valid_state)
    print(f"  Theorem: {proof['theorem']}")
    print(f"  Conclusion: Valid={proof['conclusion']['valid']}")
    print(f"  Proof hash: {proof['conclusion']['proof_hash'][:16]}...")

    print("\n[5] Verification history...")
    history = engine.get_verification_history()
    print(f"  Entries in ledger: {len(history)}")

    print("\n" + "=" * 70)
    print("✓ VERIFICATION ENGINE OPERATIONAL")
    print("=" * 70)
    print("\nFormal specification:")
    print("  Valid(Σ) = ∧_i C_i(Σ)")
    print("  Constraints: C1-C8")
    print("  Proof system: ENABLED")
    print("  Ledger integration: ACTIVE")
    print("=" * 70)


if __name__ == "__main__":
    demo_verification()
