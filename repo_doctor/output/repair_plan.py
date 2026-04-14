"""
Repo Doctor Omega - Repair Plan Generator

Generate minimum restoring repair plan with:
- Ordered patch set
- Blast radius
- Entanglement risk
- Expected energy reduction
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RepairPlan:
    """Complete repair plan."""

    repository: str
    actions: list[dict[str, Any]] = field(default_factory=list)
    total_blast_radius: int = 0
    total_entanglement_risk: float = 0.0
    total_energy_reduction: float = 0.0
    estimated_time: str = ""
    unsat_core_hints: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository": self.repository,
            "actions": self.actions,
            "total_blast_radius": self.total_blast_radius,
            "total_entanglement_risk": self.total_entanglement_risk,
            "total_energy_reduction": self.total_energy_reduction,
            "estimated_time": self.estimated_time,
            "unsat_core_hints": self.unsat_core_hints,
        }

    def to_markdown(self) -> str:
        """Export as Markdown repair plan."""
        lines = [
            "# Repo Doctor Omega - Repair Plan",
            "",
            f"**Repository:** `{self.repository}`",
            "",
            "## Repair Actions (in order)",
            "",
        ]

        for i, action in enumerate(self.actions, 1):
            lines.extend(
                [
                    f"### {i}. {action['name']}",
                    "",
                    f"- **Files:** {', '.join(action['files'][:5])}",
                    f"- **Restores invariants:** {', '.join(action['restores'])}",
                    f"- **Edit cost:** ~{action['cost']} lines",
                    f"- **Blast radius:** {action['blast_radius']} files",
                    "",
                ]
            )

        # Summary
        lines.extend(
            [
                "## Summary",
                "",
                f"**Total blast radius:** {self.total_blast_radius} files",
                f"**Entanglement risk:** {self.total_entanglement_risk:.2f}",
                f"**Expected energy reduction:** {self.total_energy_reduction:.4f}",
                f"**Estimated time:** {self.estimated_time}",
            ]
        )

        if self.unsat_core_hints:
            lines.extend(
                [
                    "",
                    "## Root Causes (from unsat core)",
                    "",
                ]
            )
            for hint in self.unsat_core_hints:
                lines.append(f"- **{hint['issue']}** → {hint['action']}")

        return "\n".join(lines)


class RepairPlanGenerator:
    """Generate repair plan from analysis results."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def generate(
        self,
        failed_invariants: list[Any],
        unsat_hints: list[dict[str, str]],
        optimal_actions: list[Any],
    ) -> RepairPlan:
        """Generate complete repair plan."""
        total_blast = sum(a.blast_radius for a in optimal_actions)
        total_risk = sum(a.entanglement_risk for a in optimal_actions)
        total_energy = sum(a.estimated_energy_reduction for a in optimal_actions)

        # Estimate time
        total_lines = sum(a.edit_cost for a in optimal_actions)
        estimated_time = f"{total_lines // 50}h" if total_lines > 50 else f"{total_lines // 10}m"

        return RepairPlan(
            repository=self.repo_path,
            actions=[
                {
                    "name": a.name,
                    "files": a.target_files,
                    "restores": a.invariants_restored,
                    "cost": a.edit_cost,
                    "blast_radius": a.blast_radius,
                }
                for a in optimal_actions
            ],
            total_blast_radius=total_blast,
            total_entanglement_risk=total_risk,
            total_energy_reduction=total_energy,
            estimated_time=estimated_time,
            unsat_core_hints=unsat_hints,
        )
