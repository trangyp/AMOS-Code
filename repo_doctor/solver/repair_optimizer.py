"""
Repo Doctor Omega - Repair Optimizer

Compute the minimum restoring set:

Find R* such that:
  - RepoValid(after R*) = true
  - cost(R*) is minimal
  - blast_radius(R*) is minimal
  - ΔE_repo is maximal

Optimization objective:
  min_R [c1·EditCost(R) + c2·BlastRadius(R) + c3·EntanglementRisk(R) - c4·EnergyReduction(R)]
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RepairAction:
    """A single repair action."""

    name: str
    target_files: List[str] = field(default_factory=list)
    invariants_restored: List[str] = field(default_factory=list)
    estimated_energy_reduction: float = 0.0
    blast_radius: int = 0  # Number of files affected
    entanglement_risk: float = 0.0  # 0-1 risk score
    edit_cost: int = 0  # Lines changed estimate

    @property
    def score(self) -> float:
        """
        Calculate repair score: higher is better.
        Score = EnergyReduction / (EditCost + BlastRadius + EntanglementRisk)
        """
        denominator = self.edit_cost + self.blast_radius + self.entanglement_risk * 10 + 1
        return self.estimated_energy_reduction / denominator


class RepairOptimizer:
    """
    Optimize repair set to minimize cost while maximizing energy reduction.
    """

    def __init__(self):
        self.actions: List[RepairAction] = []

    def add_action(self, action: RepairAction) -> None:
        """Add a candidate repair action."""
        self.actions.append(action)

    def compute_optimal_set(self, failed_invariants: List[str]) -> List[RepairAction]:
        """
        Compute optimal repair set covering all failed invariants.

        Greedy set cover with cost optimization.
        """
        remaining = set(failed_invariants)
        selected = []

        while remaining:
            # Find action with best score that covers remaining invariants
            best_action = None
            best_score = 0.0

            for action in self.actions:
                covered = set(action.invariants_restored) & remaining
                if covered:
                    score = action.score * len(covered)
                    if score > best_score:
                        best_score = score
                        best_action = action

            if not best_action:
                break  # No action covers remaining invariants

            selected.append(best_action)
            remaining -= set(best_action.invariants_restored)

        return selected

    def generate_repair_plan(
        self, failed_invariants: List[str], unsat_hints: list[dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Generate complete repair plan.

        Returns ordered patch plan with blast radius and entanglement risk.
        """
        optimal_set = self.compute_optimal_set(failed_invariants)

        # Sort by repair ordering rule
        repair_order = self._apply_repair_ordering(optimal_set)

        total_blast = sum(a.blast_radius for a in repair_order)
        total_risk = sum(a.entanglement_risk for a in repair_order)
        total_energy_reduction = sum(a.estimated_energy_reduction for a in repair_order)

        return {
            "actions": [
                {
                    "name": a.name,
                    "files": a.target_files,
                    "restores": a.invariants_restored,
                    "cost": a.edit_cost,
                    "blast_radius": a.blast_radius,
                }
                for a in repair_order
            ],
            "total_blast_radius": total_blast,
            "total_entanglement_risk": total_risk,
            "total_energy_reduction": total_energy_reduction,
            "unsat_core_hints": unsat_hints,
        }

    def _apply_repair_ordering(self, actions: List[RepairAction]) -> List[RepairAction]:
        """
        Apply repair ordering rule:
        1. parse
        2. import
        3. entrypoint
        4. packaging
        5. public/runtime API
        6. persistence
        7. runtime wrappers
        8. docs/tests/demos
        9. security hardening
        10. performance cleanup
        """
        order_priority = {
            "parse": 1,
            "import": 2,
            "entrypoint": 3,
            "packaging": 4,
            "api": 5,
            "persistence": 6,
            "runtime": 7,
            "docs": 8,
            "security": 9,
            "performance": 10,
        }

        def get_priority(action: RepairAction) -> int:
            for key, priority in order_priority.items():
                if key in action.name.lower():
                    return priority
            return 99

        return sorted(actions, key=get_priority)

    def estimate_impact(self, action: RepairAction) -> Dict[str, Any]:
        """
        Estimate impact of a repair action.
        """
        return {
            "energy_reduction": action.estimated_energy_reduction,
            "files_affected": action.blast_radius,
            "risk_level": "high"
            if action.entanglement_risk > 0.5
            else "medium"
            if action.entanglement_risk > 0.2
            else "low",
            "confidence": "high"
            if action.edit_cost < 10
            else "medium"
            if action.edit_cost < 50
            else "low",
        }
