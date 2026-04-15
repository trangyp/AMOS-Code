"""Fleet Intelligence Bridge.

Integrates multi-repository fleet management with AMOS Brain cognition.

Provides:
- Cross-repo pattern detection
- Fleet-wide health aggregation
- Shared contract monitoring
- Coordinated batch remediation
- Federated governance decisions

Extends autonomous governance from single-repo to fleet-wide coordination.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Import fleet management
try:
    from repo_doctor.fleet import FleetContext, FleetManager, FleetState
    from repo_doctor.fleet.batch_plan import BatchRemediationPlanner
    from repo_doctor.fleet.fleet_state import FleetAnalyzer
    from repo_doctor.fleet.shared_contracts import SharedContractAnalyzer

    FLEET_AVAILABLE = True
except ImportError:
    FLEET_AVAILABLE = False


class FleetIntelligenceBridge:
    """Bridge between fleet management and AMOS Brain.

    Enables the brain to:
    - Detect patterns across multiple repositories
    - Coordinate fleet-wide remediation
    - Monitor shared contracts across repos
    - Make federated governance decisions
    """

    def __init__(self, root_path: str | Path | None = None):
        self.root_path = Path(root_path) if root_path else Path(".")
        self._fleet_manager: FleetManager | None = None
        self._shared_contract_analyzer: SharedContractAnalyzer | None = None
        self._batch_planner: BatchRemediationPlanner | None = None

    @property
    def fleet_manager(self) -> FleetManager | None:
        """Lazy initialization of fleet manager."""
        if self._fleet_manager is None and FLEET_AVAILABLE:
            self._fleet_manager = FleetManager()
        return self._fleet_manager

    @property
    def contract_analyzer(self) -> SharedContractAnalyzer | None:
        """Lazy initialization of contract analyzer."""
        if self._shared_contract_analyzer is None and FLEET_AVAILABLE:
            self._shared_contract_analyzer = SharedContractAnalyzer()
        return self._shared_contract_analyzer

    @property
    def batch_planner(self) -> BatchRemediationPlanner | None:
        """Lazy initialization of batch planner."""
        if self._batch_planner is None and FLEET_AVAILABLE:
            self._batch_planner = BatchRemediationPlanner()
        return self._batch_planner

    def discover_fleet(self, name: str = "default", max_depth: int = 2) -> dict[str, Any]:
        """Auto-discover repositories under root path."""
        if not FLEET_AVAILABLE or self.fleet_manager is None:
            return {"error": "fleet_management not available"}

        fleet = self.fleet_manager.discover_fleet(
            root_path=self.root_path, name=name, max_depth=max_depth
        )

        return {
            "fleet_name": fleet.name,
            "repo_count": len(fleet.repos),
            "repositories": [
                {
                    "name": r.name,
                    "path": str(r.path),
                    "criticality": r.criticality,
                    "tags": r.tags,
                }
                for r in fleet.repos.values()
            ],
        }

    def get_fleet_health(self, fleet_name: str = "default") -> dict[str, Any]:
        """Get aggregated health across fleet."""
        if not FLEET_AVAILABLE or self.fleet_manager is None:
            return {"error": "fleet_management not available"}

        fleet = self.fleet_manager.fleets.get(fleet_name)
        if not fleet:
            return {"error": f"Fleet '{fleet_name}' not found"}

        # Get unhealthy repos
        unhealthy = fleet.get_unhealthy_repos()
        critical = fleet.get_critical_repos(threshold=0.8)

        return {
            "fleet_name": fleet.name,
            "total_repos": len(fleet.repos),
            "fleet_energy": round(fleet.energy(), 4),
            "aggregate_state": {
                state.symbol: round(amp, 3) for state, amp in fleet.aggregate_state().items()
            },
            "unhealthy_repos": [
                {"name": name, "energy": round(energy, 3)} for name, energy in unhealthy[:10]
            ],
            "critical_repos": [{"name": r.name, "criticality": r.criticality} for r in critical],
        }

    def find_cross_repo_patterns(self, fleet_name: str = "default") -> dict[str, Any]:
        """Find invariant failures common across multiple repos."""
        if not FLEET_AVAILABLE or self.fleet_manager is None:
            return {"error": "fleet_management not available"}

        fleet = self.fleet_manager.fleets.get(fleet_name)
        if not fleet:
            return {"error": f"Fleet '{fleet_name}' not found"}

        clusters = fleet.find_invariant_clusters()

        return {
            "fleet_name": fleet.name,
            "pattern_count": len(clusters),
            "patterns": [
                {
                    "invariant": c.invariant.symbol,
                    "affected_repos": c.affected_repos,
                    "repo_count": len(c.affected_repos),
                    "severity": round(c.severity, 3),
                    "shared_root_cause": c.shared_root_cause,
                }
                for c in clusters[:10]  # Top 10
            ],
        }

    def analyze_shared_contracts(self, fleet_name: str = "default") -> dict[str, Any]:
        """Analyze contracts shared across fleet."""
        if not FLEET_AVAILABLE or self.fleet_manager is None:
            return {"error": "fleet_management not available"}

        fleet = self.fleet_manager.fleets.get(fleet_name)
        if not fleet:
            return {"error": f"Fleet '{fleet_name}' not found"}

        contracts = fleet.find_shared_contracts()

        return {
            "fleet_name": fleet.name,
            "contract_count": len(contracts),
            "contracts": [
                {
                    "name": c.name,
                    "type": c.contract_type,
                    "repos": c.repos,
                    "violation_count": len(c.violations),
                }
                for c in contracts
            ],
        }

    def generate_fleet_remediation_plan(self, fleet_name: str = "default") -> dict[str, Any]:
        """Generate coordinated remediation plan for fleet."""
        if not FLEET_AVAILABLE or self.fleet_manager is None:
            return {"error": "fleet_management not available"}

        fleet = self.fleet_manager.fleets.get(fleet_name)
        if not fleet:
            return {"error": f"Fleet '{fleet_name}' not found"}

        plan = fleet.generate_batch_plan()

        return {
            "fleet_name": plan["fleet_name"],
            "total_repos": plan["total_repos"],
            "fleet_energy": plan["fleet_energy"],
            "invariant_clusters": plan["invariant_clusters"],
            "shared_contracts": plan["shared_contracts"],
            "recommended_actions": plan["recommended_actions"],
        }

    def create_batch_remediation(
        self,
        batch_id: str,
        name: str,
        target_repos: list[str],
        changes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create fleet-wide batch remediation."""
        if not FLEET_AVAILABLE or self.batch_planner is None:
            return {"error": "batch_planning not available"}

        batch = self.batch_planner.create_batch(
            batch_id=batch_id,
            name=name,
            description=f"Fleet-wide remediation: {name}",
            target_repos=target_repos,
            changes=changes,
        )

        return {
            "batch_id": batch.batch_id,
            "name": batch.name,
            "target_repos": batch.target_repos,
            "change_count": len(batch.changes),
            "status": batch.status.value,
        }

    def preview_batch(self, batch_id: str) -> dict[str, Any]:
        """Preview batch changes without applying."""
        if not FLEET_AVAILABLE or self.batch_planner is None:
            return {"error": "batch_planning not available"}

        return self.batch_planner.preview_batch(batch_id)

    def apply_batch(self, batch_id: str, dry_run: bool = True) -> dict[str, Any]:
        """Apply batch changes to target repos."""
        if not FLEET_AVAILABLE or self.batch_planner is None:
            return {"error": "batch_planning not available"}

        return self.batch_planner.apply_batch(batch_id, dry_run=dry_run)

    def get_batch_status(self, batch_id: str) -> dict[str, Any]:
        """Get status of batch remediation."""
        if not FLEET_AVAILABLE or self.batch_planner is None:
            return {"error": "batch_planning not available"}

        status = self.batch_planner.get_batch_status(batch_id)
        return status or {"error": f"Batch '{batch_id}' not found"}

    def compare_fleets(self, fleet1_name: str, fleet2_name: str) -> dict[str, Any]:
        """Compare two fleets for divergence analysis."""
        if not FLEET_AVAILABLE or self.fleet_manager is None:
            return {"error": "fleet_management not available"}

        return self.fleet_manager.compare_fleets(fleet1_name, fleet2_name)

    def get_global_health(self) -> dict[str, Any]:
        """Get global health across all fleets."""
        if not FLEET_AVAILABLE or self.fleet_manager is None:
            return {"error": "fleet_management not available"}

        return self.fleet_manager.get_global_health()


def get_fleet_bridge(
    root_path: str | Path | None = None,
) -> FleetIntelligenceBridge:
    """Factory function to get fleet bridge instance."""
    return FleetIntelligenceBridge(root_path or ".")
