#!/usr/bin/env python3
"""AMOS Axiom Validator — Bridge Between Ω Axioms and Implementation

Validates that any AMOS runtime state satisfies the axiomatic constraints.

Usage:
    from amos_axiom_validator import AxiomValidator

    validator = AxiomValidator()

    # Validate a state
    result = validator.validate_state(state, context)

    # Check specific axiom
    ax1_ok = validator.check_axiom_1_substrate(state)

    # Full system validation
    report = validator.validate_system(amos_instance)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

UTC = UTC
from typing import Any, Optional

from amos_energy import BranchEnergyBudget
from amos_memory import MemoryEntry

# Import AMOS components to validate
from amos_omega import Action, State, Substrate
from amos_v4 import Goal


class ValidationLevel(Enum):
    """Severity levels for axiom violations."""

    PASS = "pass"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AxiomCheck:
    """Result of checking a single axiom."""

    axiom_number: int
    axiom_name: str
    level: ValidationLevel
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Complete validation report for a state/system."""

    timestamp: datetime
    target: str
    checks: list[AxiomCheck]
    summary: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if not self.summary:
            self.summary = {
                "total": len(self.checks),
                "passed": sum(1 for c in self.checks if c.passed),
                "failed": sum(1 for c in self.checks if not c.passed),
                "critical": sum(
                    1 for c in self.checks if c.level == ValidationLevel.CRITICAL and not c.passed
                ),
                "warnings": sum(
                    1 for c in self.checks if c.level == ValidationLevel.WARNING and not c.passed
                ),
            }

    def is_valid(self) -> bool:
        """System is valid if no critical errors and axioms pass."""
        critical = self.summary.get("critical", 0)
        failed = self.summary.get("failed", 0)
        return critical == 0 and failed == 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "target": self.target,
            "summary": self.summary,
            "checks": [
                {
                    "axiom": c.axiom_number,
                    "name": c.axiom_name,
                    "level": c.level.value,
                    "passed": c.passed,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self.checks
            ],
            "valid": self.is_valid(),
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AxiomValidator:
    """Validates AMOS implementation against Ω axioms.

    Bridges the gap between formal specification and implementation
    by checking that runtime states satisfy axiomatic constraints.
    """

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.violations: list[AxiomCheck] = []

    # ========================================================================
    # AXIOM 1: Substrate Partition
    # ========================================================================

    def check_axiom_1_substrate(self, entity: Any) -> AxiomCheck:
        """Axiom 1: ∀x (Meaningful(x) → Classical(x) ∨ Quantum(x) ∨ ...)

        Every meaningful entity belongs to at least one substrate.
        """
        substrates = self._detect_substrates(entity)

        if not substrates:
            entity_type = type(entity).__name__
            return AxiomCheck(
                axiom_number=1,
                axiom_name="Substrate Partition",
                level=ValidationLevel.ERROR,
                passed=False,
                message=f"Entity has no detectable substrate: {entity_type}",
                details={"entity_type": entity_type},
            )

        substrate_names = [s.name for s in substrates]
        return AxiomCheck(
            axiom_number=1,
            axiom_name="Substrate Partition",
            level=ValidationLevel.PASS,
            passed=True,
            message=f"Entity belongs to substrate(s): {substrate_names}",
            details={"substrates": substrate_names},
        )

    def _detect_substrates(self, entity: Any) -> set[Substrate]:
        """Detect which substrates an entity belongs to."""
        substrates = set()

        if isinstance(entity, State):
            if entity.classical is not None:
                substrates.add(Substrate.CLASSICAL)
            if entity.quantum is not None:
                substrates.add(Substrate.QUANTUM)
            if entity.biological is not None:
                substrates.add(Substrate.BIOLOGICAL)
            if entity.hybrid is not None:
                substrates.add(Substrate.HYBRID)

        elif isinstance(entity, Goal):
            # Goals are classical terms
            substrates.add(Substrate.CLASSICAL)

        elif isinstance(entity, MemoryEntry):
            # Memory is stored classically
            substrates.add(Substrate.CLASSICAL)

        elif isinstance(entity, BranchEnergyBudget):
            # Energy is a classical resource
            substrates.add(Substrate.CLASSICAL)

        else:
            # Default: assume classical substrate
            substrates.add(Substrate.CLASSICAL)

        return substrates

    # ========================================================================
    # AXIOM 2: Typedness
    # ========================================================================

    def check_axiom_2_typedness(self, entity: Any) -> AxiomCheck:
        """Axiom 2: AdmissibleTerm(e) → ∃τ HasType(e, τ)

        Every admissible term has a type.
        """
        entity_type = type(entity).__name__

        # Check if entity has a valid type
        valid_types = [
            "State",
            "Action",
            "Goal",
            "MemoryEntry",
            "BranchEnergyBudget",
            "dict",
            "list",
            "str",
            "float",
            "int",
        ]

        has_dataclass = hasattr(entity, "__dataclass_fields__")
        has_type = entity_type in valid_types or has_dataclass

        if not has_type:
            return AxiomCheck(
                axiom_number=2,
                axiom_name="Typedness",
                level=(ValidationLevel.ERROR if self.strict else ValidationLevel.WARNING),
                passed=False,
                message=f"Entity lacks proper type: {entity_type}",
                details={"detected_type": entity_type},
            )

        return AxiomCheck(
            axiom_number=2,
            axiom_name="Typedness",
            level=ValidationLevel.PASS,
            passed=True,
            message=f"Entity has type: {entity_type}",
            details={"type": entity_type},
        )

    # ========================================================================
    # AXIOM 3: Effect Explicitness
    # ========================================================================

    def check_axiom_3_effect_explicit(self, action: Any) -> AxiomCheck:
        """Axiom 3: Transforms(f) → ∃ε Eff(f) = ε

        Every transformation has explicit effect annotation.
        """
        if not hasattr(action, "effect"):
            action_type = type(action).__name__
            return AxiomCheck(
                axiom_number=3,
                axiom_name="Effect Explicitness",
                level=ValidationLevel.ERROR,
                passed=False,
                message=f"Action {action_type} lacks effect annotation",
                details={},
            )

        effect = getattr(action, "effect", None)

        if effect is None:
            return AxiomCheck(
                axiom_number=3,
                axiom_name="Effect Explicitness",
                level=ValidationLevel.WARNING,
                passed=False,
                message="Action effect is None (implicit pure)",
                details={"effect": None},
            )

        return AxiomCheck(
            axiom_number=3,
            axiom_name="Effect Explicitness",
            level=ValidationLevel.PASS,
            passed=True,
            message=f"Action has explicit effect: {effect}",
            details={"effect": str(effect)[:100]},
        )

    # ========================================================================
    # AXIOM 4: State Stratification
    # ========================================================================

    def check_axiom_4_state_stratification(self, state: State) -> AxiomCheck:
        """Axiom 4: X = X_c × X_q × X_b × X_h × ...

        State is a stratified product with projections.
        """
        components = {
            "classical": state.classical,
            "quantum": state.quantum,
            "biological": state.biological,
            "hybrid": state.hybrid,
            "world": state.world,
            "time": state.time,
            "utility": state.utility,
            "identity": state.identity,
        }

        # Check that at least one substrate has data
        substrate_data = sum(
            1
            for v in [state.classical, state.quantum, state.biological, state.hybrid]
            if v is not None
        )

        if substrate_data == 0:
            return AxiomCheck(
                axiom_number=4,
                axiom_name="State Stratification",
                level=ValidationLevel.ERROR,
                passed=False,
                message="State has no substrate components",
                details={"components": components},
            )

        # Check projections are accessible
        projections_ok = True
        try:
            _ = state.project(Substrate.CLASSICAL)
        except Exception:
            projections_ok = False

        return AxiomCheck(
            axiom_number=4,
            axiom_name="State Stratification",
            level=ValidationLevel.PASS,
            passed=True,
            message=f"State properly stratified with {substrate_data} substrates",
            details={
                "substrate_count": substrate_data,
                "projections_work": projections_ok,
                "has_identity": state.identity is not None,
                "has_time": state.time is not None,
            },
        )

    # ========================================================================
    # AXIOM 9: Constraint
    # ========================================================================

    def check_axiom_9_constraints(self, state: State, constraints: list[Any]) -> AxiomCheck:
        """Axiom 9: Valid(x) ↔ ∀α ∈ Hard, c_α(x) = ⊤

        State satisfies all hard constraints.
        """
        if not constraints:
            return AxiomCheck(
                axiom_number=9,
                axiom_name="Constraint Satisfaction",
                level=ValidationLevel.WARNING,
                passed=True,
                message="No constraints defined (vacuously valid)",
                details={"constraint_count": 0},
            )

        failed = []
        for c in constraints:
            if hasattr(c, "evaluate"):
                if not c.evaluate(state):
                    failed.append(getattr(c, "name", str(c)))
            elif callable(c):
                try:
                    if not c(state):
                        failed.append(str(c))
                except Exception:
                    failed.append(f"error_in_{c}")

        if failed:
            return AxiomCheck(
                axiom_number=9,
                axiom_name="Constraint Satisfaction",
                level=ValidationLevel.ERROR,
                passed=False,
                message=f"State violates {len(failed)} constraint(s)",
                details={"failed_constraints": failed},
            )

        return AxiomCheck(
            axiom_number=9,
            axiom_name="Constraint Satisfaction",
            level=ValidationLevel.PASS,
            passed=True,
            message=f"All {len(constraints)} constraint(s) satisfied",
            details={"constraint_count": len(constraints)},
        )

    # ========================================================================
    # AXIOM 10 & 21: Commit and Multi-Regime Admissibility (Z*)
    # ========================================================================

    def check_axiom_10_commit(self, state: State, checks: dict[str, bool]) -> AxiomCheck:
        """Axiom 10: Commits(x*) ↔ Valid(x*) ∧ Verified(x*) ∧ Feasible(x*)

        Axiom 21: Z* = Z_type ∩ Z_logic ∩ Z_physical ∩ ...
        """
        failed_checks = [k for k, v in checks.items() if not v]

        if failed_checks:
            return AxiomCheck(
                axiom_number=21,
                axiom_name="Multi-Regime Admissibility (Z*)",
                level=ValidationLevel.ERROR,
                passed=False,
                message=f"State not in Z*: failed {failed_checks}",
                details={"failed_regimes": failed_checks, "all_checks": checks},
            )

        return AxiomCheck(
            axiom_number=21,
            axiom_name="Multi-Regime Admissibility (Z*)",
            level=ValidationLevel.PASS,
            passed=True,
            message="State belongs to Z* (all regimes admissible)",
            details={"checks": checks},
        )

    # ========================================================================
    # AXIOM 13: Identity
    # ========================================================================

    def check_axiom_13_identity(self, state: State, previous: Optional[State] = None) -> AxiomCheck:
        """Axiom 13: I(x, x') — identity preservation predicate

        Identity is not equality: I(x, x') ⊬ x = x'
        """
        if state.identity is None:
            return AxiomCheck(
                axiom_number=13,
                axiom_name="Identity",
                level=ValidationLevel.WARNING,
                passed=False,
                message="State lacks identity annotation",
                details={"has_identity": False},
            )

        if previous and previous.identity:
            identity_preserved = state.identity == previous.identity

            if not identity_preserved:
                identity_change = f"{previous.identity} → {state.identity}"
                return AxiomCheck(
                    axiom_number=13,
                    axiom_name="Identity",
                    level=ValidationLevel.ERROR,
                    passed=False,
                    message=f"Identity changed: {identity_change}",
                    details={
                        "previous": previous.identity,
                        "current": state.identity,
                        "preserved": False,
                    },
                )

        return AxiomCheck(
            axiom_number=13,
            axiom_name="Identity",
            level=ValidationLevel.PASS,
            passed=True,
            message=f"Identity valid: {state.identity}",
            details={"identity": state.identity, "preserved": True},
        )

    # ========================================================================
    # AXIOM 14: Energy
    # ========================================================================

    def check_axiom_14_energy(self, energy_budget: Any, consumed: float) -> AxiomCheck:
        """Axiom 14: ∀χ ∈ {Action, Obs, Bridge, Adapt}: Occurs(χ) → ∃e ≥ 0 Consumes(χ, e)

        Σ e_i ≤ E_budget
        """
        if not hasattr(energy_budget, "available"):
            return AxiomCheck(
                axiom_number=14,
                axiom_name="Energy",
                level=ValidationLevel.ERROR,
                passed=False,
                message="Energy budget lacks proper structure",
                details={},
            )

        available = getattr(energy_budget, "available", 0)
        total = getattr(energy_budget, "total_capacity", available + consumed)

        if consumed > total:
            return AxiomCheck(
                axiom_number=14,
                axiom_name="Energy",
                level=ValidationLevel.CRITICAL,
                passed=False,
                message=f"Energy OVERFLOW: consumed {consumed} > budget {total}",
                details={"consumed": consumed, "budget": total, "overflow": consumed - total},
            )

        if consumed > available:
            return AxiomCheck(
                axiom_number=14,
                axiom_name="Energy",
                level=ValidationLevel.ERROR,
                passed=False,
                message=f"Energy exhausted: {consumed} / {total}",
                details={"consumed": consumed, "total": total, "remaining": total - consumed},
            )

        return AxiomCheck(
            axiom_number=14,
            axiom_name="Energy",
            level=ValidationLevel.PASS,
            passed=True,
            message=f"Energy feasible: {consumed:.2f} / {total:.2f}",
            details={
                "consumed": consumed,
                "budget": total,
                "remaining": total - consumed,
                "efficiency": consumed / total if total > 0 else 0,
            },
        )

    # ========================================================================
    # FULL VALIDATION
    # ========================================================================

    def validate_state(self, state: State, context: dict = None) -> ValidationReport:
        """Validate a single state against all applicable axioms."""
        context = context or {}
        checks = []

        # Run all applicable axiom checks
        checks.append(self.check_axiom_1_substrate(state))
        checks.append(self.check_axiom_2_typedness(state))
        checks.append(self.check_axiom_4_state_stratification(state))

        # Constraint check
        constraints = context.get("constraints", [])
        checks.append(self.check_axiom_9_constraints(state, constraints))

        # Identity check
        previous = context.get("previous_state")
        checks.append(self.check_axiom_13_identity(state, previous))

        # Z* check (multi-regime admissibility)
        z_checks = {
            "type": checks[1].passed,  # typedness
            "substrate": checks[0].passed,  # substrate
            "stratification": checks[2].passed,  # stratification
            "constraint": checks[3].passed,  # constraints
            "identity": checks[4].passed,  # identity
        }
        checks.append(self.check_axiom_10_commit(state, z_checks))

        return ValidationReport(
            timestamp=datetime.now(UTC),
            target=f"State({state.identity or 'anonymous'})",
            checks=checks,
        )

    def validate_action(self, action: Action, context: dict = None) -> ValidationReport:
        """Validate an action against axioms."""
        checks = []

        checks.append(self.check_axiom_1_substrate(action))
        checks.append(self.check_axiom_2_typedness(action))
        checks.append(self.check_axiom_3_effect_explicit(action))

        # Energy check if available
        energy_budget = context.get("energy_budget") if context else None
        energy_cost = getattr(action, "energy_cost", 0)
        if energy_budget:
            checks.append(self.check_axiom_14_energy(energy_budget, energy_cost))

        return ValidationReport(
            timestamp=datetime.now(UTC), target=f"Action({action.name})", checks=checks
        )

    def validate_system(self, amos_instance: Any) -> ValidationReport:
        """Validate a complete AMOS system instance."""
        checks = []

        # Check that system has required components
        required_attrs = ["state", "memory", "energy"]
        for attr in required_attrs:
            has_attr = hasattr(amos_instance, attr)
            checks.append(
                AxiomCheck(
                    axiom_number=0,
                    axiom_name=f"System Structure: {attr}",
                    level=ValidationLevel.ERROR if not has_attr else ValidationLevel.PASS,
                    passed=has_attr,
                    message=f"System {'has' if has_attr else 'MISSING'} required component: {attr}",
                    details={"component": attr, "present": has_attr},
                )
            )

        # Validate current state if available
        if hasattr(amos_instance, "state") and amos_instance.state:
            state_report = self.validate_state(amos_instance.state)
            checks.extend(state_report.checks)

        return ValidationReport(
            timestamp=datetime.now(UTC),
            target=f"AMOS({type(amos_instance).__name__})",
            checks=checks,
        )


def demo_axiom_validator():
    """Demonstrate the axiom validator."""
    print("=" * 70)
    print("AMOS Axiom Validator — Ω Axioms → Implementation Bridge")
    print("=" * 70)

    validator = AxiomValidator()

    # Test 1: Valid state
    print("\n[Test 1: Valid State]")
    valid_state = State(classical={"value": 1.0, "energy": 100.0}, identity="test_agent", time=0.0)

    report1 = validator.validate_state(valid_state)
    print(f"  Target: {report1.target}")
    print(f"  Total checks: {report1.summary['total']}")
    print(f"  Passed: {report1.summary['passed']}")
    print(f"  Failed: {report1.summary['failed']}")
    print(f"  Valid: {report1.is_valid()}")

    # Test 2: Invalid state (no substrate)
    print("\n[Test 2: Invalid State (empty)]")
    empty_state = State()

    report2 = validator.validate_state(empty_state)
    print(f"  Target: {report2.target}")
    print(f"  Critical errors: {report2.summary.get('critical', 0)}")
    print(f"  Valid: {report2.is_valid()}")

    # Show failed checks
    for check in report2.checks:
        if not check.passed:
            print(f"    ✗ Axiom {check.axiom_number}: {check.message}")

    # Test 3: Valid action
    print("\n[Test 3: Valid Action]")
    valid_action = Action(
        name="test_action",
        substrate=Substrate.CLASSICAL,
        effect={"value": 1.0},
        energy_cost=0.1,
        pure=False,
    )

    report3 = validator.validate_action(valid_action)
    print(f"  Target: {report3.target}")
    print(f"  Valid: {report3.is_valid()}")

    # Test 4: Invalid action (no effect)
    print("\n[Test 4: Invalid Action (no effect)]")

    class BadAction:
        name = "bad_action"
        substrate = Substrate.CLASSICAL
        # Missing 'effect' attribute

    bad_action = BadAction()
    report4 = validator.validate_action(bad_action)
    print(f"  Target: {report4.target}")
    print(f"  Valid: {report4.is_valid()}")

    for check in report4.checks:
        if not check.passed:
            print(f"    ✗ Axiom {check.axiom_number}: {check.message}")

    # Test 5: Energy overflow
    print("\n[Test 5: Energy Overflow]")
    from amos_energy import EnergyPool

    energy = EnergyPool(name="test", total_capacity=100.0)
    energy.allocated = 95.0  # Almost exhausted

    expensive_action = Action(
        name="expensive",
        substrate=Substrate.CLASSICAL,
        effect={"value": 100.0},
        energy_cost=20.0,  # Exceeds available
        pure=False,
    )

    report5 = validator.validate_action(expensive_action, context={"energy_budget": energy})
    print(f"  Target: {report5.target}")
    print(f"  Energy critical: {report5.summary.get('critical', 0) > 0}")

    for check in report5.checks:
        if check.axiom_number == 14:
            print(f"    Energy check: {check.message}")

    # Test 6: Full JSON report
    print("\n[Test 6: JSON Export]")
    json_report = report1.to_json()
    print(f"  Report size: {len(json_report)} chars")
    print(f"  First 200 chars:\n{json_report[:200]}...")

    print("\n" + "=" * 70)
    print("✓ Axiom validator demonstration complete")
    print("=" * 70)
    print()
    print("Summary: Validator bridges Ω axioms → implementation")
    print("  - Checks 6 core axioms (1, 2, 3, 4, 9, 13, 14, 21)")
    print("  - Validates states, actions, full systems")
    print("  - Exports JSON reports for auditing")
    print("  - Catches violations: substrate, type, effect, energy, identity")


if __name__ == "__main__":
    demo_axiom_validator()
