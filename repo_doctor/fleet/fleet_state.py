"""
Fleet State Management

Fleet state: |Ψ_fleet⟩ = Σr ωr |Ψ_repo_r⟩
Fleet energy: E_fleet = Σr ωr E_repo_r
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FleetState:
    """
    Multi-repo fleet state vector.

    |Ψ_fleet⟩ = Σr ωr |Ψ_repo_r⟩
    """

    repos: dict[str, dict[str, Any]] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)

    def add_repo(
        self,
        repo_id: str,
        state_vector: Dict[str, float],
        energy: float,
        weight: float = 1.0,
    ) -> None:
        """Add a repository to the fleet."""
        self.repos[repo_id] = {
            "state_vector": state_vector,
            "energy": energy,
        }
        self.weights[repo_id] = weight

    def compute_fleet_energy(self) -> float:
        """
        Compute fleet energy: E_fleet = Σr ωr E_repo_r
        """
        total = 0.0
        for repo_id, repo_data in self.repos.items():
            weight = self.weights.get(repo_id, 1.0)
            energy = repo_data.get("energy", 0.0)
            total += weight * energy
        return total

    def compute_aggregate_state(self) -> dict[str, float]:
        """
        Compute weighted aggregate state across fleet.
        """
        aggregate: Dict[str, float] = {}
        total_weight = sum(self.weights.values())

        if total_weight == 0:
            return aggregate

        for repo_id, repo_data in self.repos.items():
            weight = self.weights.get(repo_id, 1.0)
            state = repo_data.get("state_vector", {})

            for dim, value in state.items():
                if dim not in aggregate:
                    aggregate[dim] = 0.0
                aggregate[dim] += (weight / total_weight) * value

        return aggregate

    def find_critical_repos(self, threshold: float = 2.0) -> list[tuple[str, float]]:
        """
        Find repos with energy above threshold.

        Returns: [(repo_id, energy), ...] sorted by energy desc
        """
        critical = [
            (repo_id, data.get("energy", 0.0))
            for repo_id, data in self.repos.items()
            if data.get("energy", 0.0) > threshold
        ]
        return sorted(critical, key=lambda x: -x[1])


class FleetAnalyzer:
    """
    Analyze fleet-wide patterns and class defects.
    """

    def __init__(self, fleet_state: FleetState):
        self.fleet = fleet_state

    def find_class_defects(
        self,
        invariant_name: str,
    ) -> List[str]:
        """
        Find repos sharing the same invariant failure.

        A class defect repeats across repos and should be
        treated as a systemic issue, not isolated incidents.
        """
        affected = []

        for repo_id, repo_data in self.fleet.repos.items():
            failures = repo_data.get("hard_failures", [])
            if invariant_name in failures:
                affected.append(repo_id)

        return affected

    def compute_cross_repo_invariants(self) -> dict[str, list[str]]:
        """
        Compute invariants that fail across multiple repos.

        Returns: {invariant_name: [repo_ids], ...}
        """
        cross_repo: dict[str, list[str]] = {}

        for repo_id, repo_data in self.fleet.repos.items():
            failures = repo_data.get("hard_failures", [])
            for inv in failures:
                if inv not in cross_repo:
                    cross_repo[inv] = []
                cross_repo[inv].append(repo_id)

        # Only keep invariants that fail in multiple repos
        return {inv: repos for inv, repos in cross_repo.items() if len(repos) > 1}

    def suggest_fleet_remediation_priority(self) -> list[tuple[str, int, float]]:
        """
        Suggest remediation priority based on impact.

        Returns: [(invariant_name, affected_count, total_energy), ...]
        """
        cross_repo = self.compute_cross_repo_invariants()

        priorities = []
        for inv, repos in cross_repo.items():
            total_energy = sum(self.fleet.repos[r].get("energy", 0.0) for r in repos)
            priorities.append((inv, len(repos), total_energy))

        return sorted(priorities, key=lambda x: (-x[1], -x[2]))
