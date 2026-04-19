"""Repair optimizer for minimum-cost repository restoration.

Computes optimal repair plans using:
1. Z3 SMT solver for constraint satisfaction
2. Multi-objective optimization (cost, blast radius, entanglement)
3. Repair sequencing based on subsystem dependencies
"""

from dataclasses import dataclass, field
from typing import Any

from .z3_model import RepairCandidate, Z3Model


@dataclass
class RepairAction:
    """A concrete repair action."""

    step: int
    action: str
    target: str
    description: str
    estimated_cost: float
    blast_radius: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step": self.step,
            "action": self.action,
            "target": self.target,
            "description": self.description,
            "estimated_cost": self.estimated_cost,
            "blast_radius": self.blast_radius,
        }


@dataclass
class RepairPlan:
    """Optimized repair plan."""

    repository: str
    total_cost: float
    total_blast_radius: float
    expected_energy_drop: float
    actions: list[RepairAction] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    @property
    def action_count(self) -> int:
        """Number of repair actions."""
        return len(self.actions)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "repository": self.repository,
            "total_cost": self.total_cost,
            "total_blast_radius": self.total_blast_radius,
            "expected_energy_drop": self.expected_energy_drop,
            "action_count": self.action_count,
            "actions": [a.to_dict() for a in self.actions],
            "risks": self.risks,
        }


class RepairOptimizer:
    """Repair optimizer for repository restoration.

    Computes minimum-cost repair sets that restore repository validity.
    Uses Z3 solver for optimization and dependency analysis for sequencing.

    Repair order (per architecture spec):
    1. parse
    2. import
    3. entrypoint
    4. packaging
    5. API
    6. persistence
    7. runtime wrappers
    8. tests / demos / docs
    9. security hardening
    10. performance cleanup

    Usage:
        optimizer = RepairOptimizer()

        # Generate repair candidates from violations
        candidates = [
            RepairCandidate("fix_import", "module.py", 1.0, 0.5),
            RepairCandidate("add_init", "package/__init__.py", 2.0, 1.0),
        ]

        # Compute optimal plan
        plan = optimizer.compute_plan("/path/to/repo", candidates)

        print(f"Repair plan: {plan.action_count} actions")
        for action in plan.actions:
            print(f"  {action.step}. {action.action} -> {action.target}")
    """

    # Repair priority order per architecture specification
    REPAIR_ORDER = [
        "parse",
        "import",
        "entrypoint",
        "packaging",
        "api",
        "persistence",
        "runtime",
        "tests",
        "security",
        "performance",
    ]

    def __init__(self):
        self.z3_model = Z3Model()

    def compute_plan(
        self,
        repo_path: str,
        violations: list[Any],
        candidates: list[RepairCandidate] = None,
    ) -> RepairPlan:
        """Compute optimal repair plan for repository.

        Args:
            repo_path: Path to repository
            violations: List of invariant violations
            candidates: Optional pre-computed repair candidates

        Returns:
            Optimized RepairPlan
        """
        # Generate candidates from violations if not provided
        if candidates is None:
            candidates = self._generate_candidates(violations)

        if not candidates:
            # No repairs needed
            return RepairPlan(
                repository=repo_path,
                total_cost=0.0,
                total_blast_radius=0.0,
                expected_energy_drop=0.0,
                actions=[],
                risks=[],
            )

        # Use Z3 to optimize repair selection
        optimized = self.z3_model.optimize_repairs(candidates)

        # Sort by repair order priority
        sequenced = self._sequence_repairs(optimized)

        # Build repair actions
        actions = []
        for i, candidate in enumerate(sequenced, 1):
            action = RepairAction(
                step=i,
                action=candidate.action,
                target=candidate.target,
                description=self._describe_action(candidate),
                estimated_cost=candidate.cost,
                blast_radius=candidate.blast_radius,
            )
            actions.append(action)

        # Calculate totals
        total_cost = sum(a.estimated_cost for a in actions)
        total_blast = sum(a.blast_radius for a in actions)

        # Estimate energy drop (simplified model)
        energy_drop = self._estimate_energy_drop(actions)

        # Identify risks
        risks = self._identify_risks(actions)

        return RepairPlan(
            repository=repo_path,
            total_cost=total_cost,
            total_blast_radius=total_blast,
            expected_energy_drop=energy_drop,
            actions=actions,
            risks=risks,
        )

    def _generate_candidates(self, violations: list[Any]) -> list[RepairCandidate]:
        """Generate repair candidates from violations."""
        candidates = []

        for v in violations:
            # Extract violation info
            invariant = getattr(v, "invariant", "unknown")
            message = getattr(v, "message", "")
            location = getattr(v, "location", "")
            remediation = getattr(v, "remediation", "")

            # Generate candidate based on invariant type
            candidate = self._violation_to_candidate(invariant, message, location, remediation)
            if candidate:
                candidates.append(candidate)

        # Deduplicate by target
        seen = set()
        unique = []
        for c in candidates:
            key = (c.action, c.target)
            if key not in seen:
                seen.add(key)
                unique.append(c)

        return unique

    def _violation_to_candidate(
        self,
        invariant: str,
        message: str,
        location: str,
        remediation: str,
    ) -> Optional[RepairCandidate]:
        """Convert a violation to a repair candidate."""
        # Parse location
        if ":" in location:
            target = location.split(":")[0]
        else:
            target = location or "unknown"

        # Determine action from invariant type
        action_map = {
            "parse": ("fix_syntax", 1.0, 0.8),
            "import": ("fix_import", 1.0, 0.6),
            "api": ("fix_api_export", 2.0, 1.0),
            "entrypoint": ("fix_entrypoint", 2.0, 0.9),
            "packaging": ("fix_package_config", 1.5, 0.7),
            "status": ("fix_status_claim", 1.0, 0.5),
            "test": ("fix_test", 1.0, 0.4),
        }

        # Get defaults
        action, cost, blast = action_map.get(invariant.lower(), ("fix_issue", 1.0, 0.5))

        return RepairCandidate(
            action=action,
            target=target,
            cost=cost,
            blast_radius=blast,
            invariant_impact=[invariant],
        )

    def _sequence_repairs(self, candidates: list[RepairCandidate]) -> list[RepairCandidate]:
        """Sequence repairs by priority order."""

        def priority(c: RepairCandidate) -> int:
            for i, order in enumerate(self.REPAIR_ORDER):
                if order in c.action.lower():
                    return i
            return len(self.REPAIR_ORDER)  # Default to end

        return sorted(candidates, key=priority)

    def _describe_action(self, candidate: RepairCandidate) -> str:
        """Generate human-readable description."""
        descriptions = {
            "fix_syntax": f"Fix syntax errors in {candidate.target}",
            "fix_import": f"Resolve import issues in {candidate.target}",
            "fix_api_export": f"Update API exports in {candidate.target}",
            "fix_entrypoint": f"Fix entrypoint target in {candidate.target}",
            "fix_package_config": f"Correct packaging configuration in {candidate.target}",
            "fix_status_claim": f"Fix status claim in {candidate.target}",
            "fix_test": f"Fix failing test in {candidate.target}",
            "fix_issue": f"Address issue in {candidate.target}",
        }

        return descriptions.get(candidate.action, f"{candidate.action} on {candidate.target}")

    def _estimate_energy_drop(self, actions: list[RepairAction]) -> float:
        """Estimate energy reduction from repairs."""
        # Simplified model: each repair reduces energy by cost * effectiveness
        # Effectiveness assumed to be 0.7 on average
        effectiveness = 0.7
        total_drop = sum(a.estimated_cost * effectiveness for a in actions)

        # Cap at reasonable value
        return min(total_drop, 10.0)

    def _identify_risks(self, actions: list[RepairAction]) -> list[str]:
        """Identify risks in repair plan."""
        risks = []

        # High blast radius risk
        high_blast = [a for a in actions if a.blast_radius > 0.8]
        if high_blast:
            risks.append(
                f"High blast radius: {len(high_blast)} actions may affect unrelated subsystems"
            )

        # Many actions risk
        if len(actions) > 10:
            risks.append(
                f"Large repair set: {len(actions)} actions suggest "
                f"systemic issues requiring broad revalidation"
            )

        # Cost accumulation risk
        total_cost = sum(a.estimated_cost for a in actions)
        if total_cost > 20:
            risks.append(
                f"High repair cost ({total_cost:.1f}): Consider refactoring over incremental fixes"
            )

        return risks

    def validate_plan(self, plan: RepairPlan) -> bool:
        """Validate that repair plan is sound.

        Args:
            plan: Repair plan to validate

        Returns:
            True if plan is valid
        """
        if not plan.actions:
            # Empty plan is valid if no repairs needed
            return plan.total_cost == 0

        # Check for duplicates
        targets = [a.target for a in plan.actions]
        if len(targets) != len(set(targets)):
            return False

        # Check step numbering
        steps = [a.step for a in plan.actions]
        if steps != list(range(1, len(steps) + 1)):
            return False

        return True
