"""
Fleet Management - Multi-repository verification and control.

Implements fleet-scale repository health monitoring with:
- Fleet state vector aggregation
- Cross-repo invariant clusters
- Shared contract analysis
- Batch remediation planning

Fleet state:
|Ψ_fleet⟩ = Σr ωr |Ψ_repo_r⟩
E_fleet = Σr ωr E_repo_r

Where ωr is repository criticality weight.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .state_vector_omega import BasisState, Hamiltonian, StateVector


@dataclass
class RepoFleetMember:
    """A single repository in the fleet."""

    name: str
    path: Path
    criticality: float  # Weight ωr (0.0 to 1.0)
    state_vector: Optional[StateVector] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": str(self.path),
            "criticality": self.criticality,
            "tags": self.tags,
            "state": self.state_vector.to_dict() if self.state_vector else None,
        }


@dataclass
class InvariantCluster:
    """
    Cluster of repos sharing the same invariant failure.

    When the same invariant class fails across repos,
    treat it as a class defect requiring coordinated fix.
    """

    invariant: BasisState
    affected_repos: List[str]
    severity: float
    shared_root_cause: str = None

    def to_dict(self) -> dict:
        return {
            "invariant": self.invariant.symbol,
            "affected_repos": self.affected_repos,
            "repo_count": len(self.affected_repos),
            "severity": self.severity,
            "shared_root_cause": self.shared_root_cause,
        }


@dataclass
class SharedContract:
    """A contract (API, schema, etc.) shared across multiple repos."""

    name: str
    contract_type: str  # "api_schema", "shared_lib", "protocol", etc.
    repos: List[str]
    violations: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.contract_type,
            "repos": self.repos,
            "violation_count": len(self.violations),
        }


class FleetState:
    """
    Aggregate state across repository fleet.

    |Ψ_fleet⟩ = Σr ωr |Ψ_repo_r⟩
    """

    def __init__(self, name: str = "default_fleet"):
        self.name = name
        self.repos: Dict[str, RepoFleetMember] = {}
        self.H = Hamiltonian()

    def add_repo(
        self, name: str, path: Path | str, criticality: float = 1.0, tags: List[str] = None
    ):
        """Add a repository to the fleet."""
        self.repos[name] = RepoFleetMember(
            name=name, path=Path(path), criticality=criticality, tags=tags or []
        )

    def update_repo_state(self, name: str, state: StateVector):
        """Update state vector for a fleet member."""
        if name in self.repos:
            self.repos[name].state_vector = state

    def aggregate_state(self) -> dict[BasisState, float]:
        """
        Compute weighted aggregate amplitudes across fleet.

        αk_fleet = Σr ωr · αk_r / Σr ωr
        """
        total_weight = sum(r.criticality for r in self.repos.values())

        if total_weight == 0:
            return dict.fromkeys(BasisState, 1.0)

        aggregate = {}
        for state in BasisState:
            weighted_sum = sum(
                r.criticality * r.state_vector.amplitudes[state]
                for r in self.repos.values()
                if r.state_vector
            )
            aggregate[state] = weighted_sum / total_weight

        return aggregate

    def energy(self) -> float:
        """
        Compute fleet energy: E_fleet = Σr ωr E_repo_r
        """
        total_energy = 0.0
        total_weight = 0.0

        for repo in self.repos.values():
            if repo.state_vector:
                total_energy += repo.criticality * self.H.energy(repo.state_vector)
                total_weight += repo.criticality

        if total_weight == 0:
            return 0.0

        return total_energy / total_weight

    def find_invariant_clusters(self) -> List[InvariantCluster]:
        """
        Find clusters of repos failing the same invariant.

        Returns list of invariant clusters for coordinated fixing.
        """
        clusters = []

        for invariant in BasisState:
            failing_repos = [
                r.name
                for r in self.repos.values()
                if r.state_vector and r.state_vector.amplitudes[invariant] < 0.5
            ]

            if len(failing_repos) > 1:
                # Calculate cluster severity
                severities = [
                    1 - self.repos[name].state_vector.amplitudes[invariant]
                    for name in failing_repos
                    if self.repos[name].state_vector
                ]
                avg_severity = sum(severities) / len(severities)

                clusters.append(
                    InvariantCluster(
                        invariant=invariant,
                        affected_repos=failing_repos,
                        severity=avg_severity,
                        shared_root_cause=self._infer_shared_cause(invariant, failing_repos),
                    )
                )

        # Sort by severity
        clusters.sort(key=lambda c: c.severity, reverse=True)
        return clusters

    def _infer_shared_cause(self, invariant: BasisState, repos: List[str]) -> str:
        """Infer possible shared root cause for invariant failures."""
        # Simple heuristics based on invariant type
        cause_map = {
            BasisState.API: "shared_api_schema_changed",
            BasisState.IMPORT: "shared_dependency_updated",
            BasisState.PACKAGING: "shared_build_config_changed",
            BasisState.ENTRYPOINT: "shared_launcher_template_changed",
            BasisState.STATUS: "shared_status_helper_bug",
        }
        return cause_map.get(invariant)

    def find_shared_contracts(self) -> List[SharedContract]:
        """
        Find contracts shared across multiple repos.

        Examples: shared API schemas, common libraries, protocols.
        """
        # This would analyze pyproject.toml, imports, etc.
        # Simplified implementation
        contracts = []

        # Group repos by tags
        tag_groups: dict[str, list[str]] = {}
        for repo in self.repos.values():
            for tag in repo.tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(repo.name)

        # Create contracts for shared tags
        for tag, repo_names in tag_groups.items():
            if len(repo_names) > 1:
                contracts.append(
                    SharedContract(name=f"tag:{tag}", contract_type="shared_tag", repos=repo_names)
                )

        return contracts

    def get_critical_repos(self, threshold: float = 0.7) -> List[RepoFleetMember]:
        """Get repos with criticality above threshold."""
        return [r for r in self.repos.values() if r.criticality >= threshold]

    def get_unhealthy_repos(self) -> list[tuple[str, float]]:
        """Get repos with high energy (unhealthy)."""
        unhealthy = []
        for name, repo in self.repos.items():
            if repo.state_vector:
                energy = self.H.energy(repo.state_vector)
                if energy > 3.0:  # Above healthy threshold
                    unhealthy.append((name, energy))

        # Sort by energy (descending)
        unhealthy.sort(key=lambda x: x[1], reverse=True)
        return unhealthy

    def generate_batch_plan(self) -> Dict[str, Any]:
        """
        Generate batch remediation plan for fleet.

        Returns coordinated fix plan for shared defects.
        """
        clusters = self.find_invariant_clusters()
        shared_contracts = self.find_shared_contracts()

        plan = {
            "fleet_name": self.name,
            "total_repos": len(self.repos),
            "fleet_energy": round(self.energy(), 3),
            "invariant_clusters": [c.to_dict() for c in clusters],
            "shared_contracts": [c.to_dict() for c in shared_contracts],
            "recommended_actions": [],
        }

        # Generate recommendations
        for cluster in clusters[:3]:  # Top 3 clusters
            plan["recommended_actions"].append(
                {
                    "action": "coordinate_fix",
                    "invariant": cluster.invariant.symbol,
                    "affected_repos": cluster.affected_repos,
                    "shared_cause": cluster.shared_root_cause,
                    "estimated_blast_radius": len(cluster.affected_repos),
                }
            )

        # Add critical repo fixes
        critical_unhealthy = [
            (name, energy)
            for name, energy in self.get_unhealthy_repos()
            if self.repos[name].criticality > 0.8
        ]

        for name, energy in critical_unhealthy[:3]:
            plan["recommended_actions"].append(
                {
                    "action": "priority_fix",
                    "repo": name,
                    "energy": round(energy, 3),
                    "criticality": self.repos[name].criticality,
                }
            )

        return plan

    def to_dict(self) -> dict:
        """Serialize fleet state."""
        return {
            "name": self.name,
            "repo_count": len(self.repos),
            "energy": round(self.energy(), 3),
            "aggregate_amplitudes": {
                state.symbol: round(amp, 3) for state, amp in self.aggregate_state().items()
            },
            "repos": [r.to_dict() for r in self.repos.values()],
        }

    def format_report(self) -> str:
        """Generate human-readable fleet report."""
        lines = [
            "=" * 70,
            f"FLEET STATE REPORT: {self.name}",
            "=" * 70,
            f"Repositories: {len(self.repos)}",
            f"Fleet Energy: {self.energy():.4f}",
            "",
            "AGGREGATE STATE:",
            "-" * 40,
        ]

        for state, amp in sorted(self.aggregate_state().items(), key=lambda x: x[1]):
            status = "✓" if amp > 0.9 else "⚠" if amp > 0.5 else "✗"
            bar = "█" * int(amp * 20) + "░" * (20 - int(amp * 20))
            lines.append(f"  [{status}] {state.symbol:3} = {amp:.3f}  {bar}")

        # Invariant clusters
        clusters = self.find_invariant_clusters()
        if clusters:
            lines.extend(["", "INVARIANT CLUSTERS (shared defects):", "-" * 40])
            for cluster in clusters[:5]:
                lines.append(f"  {cluster.invariant.symbol}: {len(cluster.affected_repos)} repos")
                lines.append(f"    Severity: {cluster.severity:.3f}")
                if cluster.shared_root_cause:
                    lines.append(f"    Cause: {cluster.shared_root_cause}")
                lines.append(f"    Repos: {', '.join(cluster.affected_repos[:3])}")
                if len(cluster.affected_repos) > 3:
                    lines.append(f"    ... and {len(cluster.affected_repos) - 3} more")

        # Unhealthy repos
        unhealthy = self.get_unhealthy_repos()
        if unhealthy:
            lines.extend(["", "UNHEALTHY REPOSITORIES:", "-" * 40])
            for name, energy in unhealthy[:5]:
                repo = self.repos[name]
                lines.append(f"  {name}: E={energy:.3f}, crit={repo.criticality:.2f}")

        lines.append("=" * 70)
        return "\n".join(lines)


class FleetManager:
    """
    Manager for multiple repository fleets.

    Supports fleet discovery, monitoring, and coordinated operations.
    """

    def __init__(self):
        self.fleets: Dict[str, FleetState] = {}

    def create_fleet(self, name: str) -> FleetState:
        """Create a new fleet."""
        fleet = FleetState(name)
        self.fleets[name] = fleet
        return fleet

    def discover_fleet(
        self, root_path: Path, name: str = "discovered", max_depth: int = 2
    ) -> FleetState:
        """
        Auto-discover repositories under root path.

        Finds repos with pyproject.toml or .git directories.
        """
        fleet = FleetState(name)
        root = Path(root_path).resolve()

        for path in root.rglob("pyproject.toml"):
            repo_path = path.parent

            # Check depth
            depth = len(repo_path.relative_to(root).parts)
            if depth > max_depth:
                continue

            # Determine criticality from path hints
            criticality = 0.5
            repo_name = repo_path.name.lower()
            if "core" in repo_name or "main" in repo_name:
                criticality = 1.0
            elif "api" in repo_name or "service" in repo_name:
                criticality = 0.9
            elif "lib" in repo_name or "shared" in repo_name:
                criticality = 0.8

            fleet.add_repo(
                name=repo_path.name,
                path=repo_path,
                criticality=criticality,
                tags=["auto-discovered"],
            )

        self.fleets[name] = fleet
        return fleet

    def compare_fleets(self, fleet1_name: str, fleet2_name: str) -> dict:
        """Compare two fleets for divergence analysis."""
        f1 = self.fleets.get(fleet1_name)
        f2 = self.fleets.get(fleet2_name)

        if not f1 or not f2:
            return {"error": "Fleet not found"}

        return {
            "fleet1": f1.name,
            "fleet2": f2.name,
            "energy_diff": round(f1.energy() - f2.energy(), 3),
            "repo_count_diff": len(f1.repos) - len(f2.repos),
        }

    def get_global_health(self) -> dict:
        """Get global health across all fleets."""
        total_energy = sum(f.energy() for f in self.fleets.values())
        total_repos = sum(len(f.repos) for f in self.fleets.values())

        return {
            "fleets": len(self.fleets),
            "total_repos": total_repos,
            "average_energy": round(total_energy / len(self.fleets), 3) if self.fleets else 0,
        }
