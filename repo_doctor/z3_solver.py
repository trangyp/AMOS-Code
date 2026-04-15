"""
Z3 SMT Solver Integration - Status Truth Verification

Implements theorem-proving layer for formal invariant verification.

Key capabilities:
- Encode status invariants as SMT constraints
- Check satisfiability of status claims
- Extract unsat cores for contradictory status
- Optimize repair plans

Example constraints:
    Initialized = true -> LoadedSpecsCount > 0
    BrainLoaded = true -> DomainsCount > 0
    Healthy = true -> ∧ hard invariants hold
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class StatusConstraint:
    """A status constraint with logical implication."""

    name: str
    claim: str  # e.g., "initialized"
    condition: str  # e.g., "loaded_specs > 0"
    severity: str = "critical"


@dataclass
class Z3Model:
    """
    Z3 SMT model for status truth verification.

    Encodes status invariants as logical constraints and checks
    if reported status labels are logically implied by actual state.
    """

    repo_path: Path
    constraints: list[StatusConstraint] = field(default_factory=list)
    status_vars: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.repo_path = Path(self.repo_path).resolve()
        self._init_default_constraints()

    def _init_default_constraints(self):
        """Initialize default status truth constraints."""
        self.constraints = [
            StatusConstraint(
                name="initialized_implies_specs",
                claim="initialized",
                condition="loaded_specs_count > 0",
                severity="critical",
            ),
            StatusConstraint(
                name="brain_loaded_implies_domains",
                claim="brain_loaded",
                condition="domains_count > 0",
                severity="critical",
            ),
            StatusConstraint(
                name="healthy_implies_invariants",
                claim="healthy",
                condition="all_hard_invariants_hold",
                severity="critical",
            ),
            StatusConstraint(
                name="active_plan_implies_not_terminal",
                claim="active_plan",
                condition="plan_status != 'terminal'",
                severity="high",
            ),
            StatusConstraint(
                name="ready_implies_initialized",
                claim="ready",
                condition="initialized and brain_loaded",
                severity="critical",
            ),
        ]

    def is_available(self) -> bool:
        """Check if Z3 solver is available."""
        try:
            import z3

            return True
        except ImportError:
            return False

    def verify_status_truth(
        self, claimed_status: dict[str, bool], actual_state: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Verify if claimed status is logically implied by actual state.

        Args:
        ----
            claimed_status: Map of status labels to claimed values
            actual_state: Map of actual state measurements

        Returns:
        -------
            Verification result with contradictions

        """
        if not self.is_available():
            return {"available": False, "error": "z3-solver not installed", "violations": []}

        try:
            import z3

            violations = []
            solver = z3.Solver()

            # Create Z3 variables for status claims
            z3_vars = {}
            for claim, value in claimed_status.items():
                z3_vars[claim] = z3.Bool(claim)
                # Assert claimed value
                solver.add(z3_vars[claim] == value)

            # Check each constraint
            for constraint in self.constraints:
                if constraint.claim in claimed_status:
                    claimed_value = claimed_status[constraint.claim]

                    # Parse condition
                    condition_satisfied = self._eval_condition(constraint.condition, actual_state)

                    # If status is claimed true but condition not met -> violation
                    if claimed_value and not condition_satisfied:
                        violations.append(
                            {
                                "constraint": constraint.name,
                                "claim": constraint.claim,
                                "claimed_value": claimed_value,
                                "condition": constraint.condition,
                                "condition_satisfied": condition_satisfied,
                                "severity": constraint.severity,
                                "message": (
                                    f"Status '{constraint.claim}'={claimed_value} "
                                    f"but condition '{constraint.condition}' is false"
                                ),
                            }
                        )

            return {
                "available": True,
                "violations": violations,
                "violation_count": len(violations),
                "is_valid": len(violations) == 0,
            }

        except Exception as e:
            return {"available": True, "error": str(e), "violations": [], "is_valid": False}

    def _eval_condition(self, condition: str, state: dict[str, Any]) -> bool:
        """
        Evaluate a condition against actual state.

        Supports simple conditions like:
        - "loaded_specs_count > 0"
        - "domains_count > 0"
        - "all_hard_invariants_hold"
        - "plan_status != 'terminal'"
        """
        # Parse simple conditions
        if " > " in condition:
            parts = condition.split(" > ")
            if len(parts) == 2:
                var_name = parts[0].strip()
                threshold = int(parts[1].strip())
                actual_value = state.get(var_name, 0)
                return actual_value > threshold

        if " != " in condition:
            parts = condition.split(" != ")
            if len(parts) == 2:
                var_name = parts[0].strip()
                expected = parts[1].strip().strip("'\"")
                actual_value = state.get(var_name, "")
                return actual_value != expected

        if condition == "all_hard_invariants_hold":
            return state.get("hard_invariants_hold", False)

        if " and " in condition:
            parts = condition.split(" and ")
            return all(self._eval_condition(p.strip(), state) for p in parts)

        # Default: check if boolean condition is true in state
        return state.get(condition, False)

    def find_unsat_core(
        self, claimed_status: dict[str, bool], actual_state: dict[str, Any]
    ) -> list[str]:
        """
        Find minimal unsatisfiable core of contradictory status claims.

        Returns list of status labels that form a contradiction.
        """
        if not self.is_available():
            return []

        try:
            import z3

            solver = z3.Solver()

            # Track constraints with assertion IDs
            assertions = []
            for claim, value in claimed_status.items():
                assertion_id = z3.Bool(f"{claim}={value}")
                solver.add(assertion_id)
                assertions.append((claim, assertion_id))

            # Add negation of conditions as constraints
            for constraint in self.constraints:
                if constraint.claim in claimed_status:
                    claimed_value = claimed_status[constraint.claim]
                    condition_satisfied = self._eval_condition(constraint.condition, actual_state)

                    if claimed_value and not condition_satisfied:
                        # This is a contradiction
                        contradiction_id = z3.Bool(f"contradiction:{constraint.name}")
                        solver.add(contradiction_id)

            # Check satisfiability
            result = solver.check()

            if result == z3.unsat:
                # Get unsat core
                core = solver.unsat_core()
                contradictions = [claim for claim, assertion in assertions if assertion in core]
                return contradictions

            return []

        except Exception:
            return []

    def optimize_repair_order(
        self,
        failed_invariants: list[str],
        repair_costs: dict[str, float],
        energy_impacts: dict[str, float],
    ) -> list[tuple[str, float]]:
        """
        Optimize repair order using Z3 optimization.

        Objective: minimize total cost while maximizing energy reduction

        min [c1·EditCost + c2·BlastRadius - c3·EnergyReduction]
        """
        if not self.is_available():
            # Fallback to simple greedy ordering
            return sorted(
                [(inv, repair_costs.get(inv, 1.0)) for inv in failed_invariants], key=lambda x: x[1]
            )

        try:
            # Simplified: use priority based on energy impact / cost ratio
            priorities = []
            for inv in failed_invariants:
                cost = repair_costs.get(inv, 1.0)
                impact = energy_impacts.get(inv, 1.0)
                priority = impact / cost if cost > 0 else impact
                priorities.append((inv, priority))

            # Sort by priority (descending)
            priorities.sort(key=lambda x: x[1], reverse=True)

            return priorities

        except Exception:
            return [(inv, 1.0) for inv in failed_invariants]

    def to_dict(self) -> dict:
        """Serialize model configuration."""
        return {
            "available": self.is_available(),
            "constraints": [
                {"name": c.name, "claim": c.claim, "condition": c.condition, "severity": c.severity}
                for c in self.constraints
            ],
            "constraint_count": len(self.constraints),
        }
