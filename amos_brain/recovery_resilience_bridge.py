"""Recovery and Resilience Bridge.

Integrates recovery and resilience validation with AMOS Brain cognition.

Provides API for:
- Resilience assessment
- Recovery path validation
- Blast containment checking
- DR capability verification
- Failure domain isolation analysis
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

# Import recovery resilience engine
try:
    from repo_doctor.recovery_resilience_engine import (
        BlastContainment,
        BlastRadiusUnit,
        DisasterRecoveryCapability,
        FailureDomain,
        FailureDomainType,
        RecoveryPath,
        RecoveryResilienceEngine,
        RecoveryType,
    )

    RESILIENCE_AVAILABLE = True
except ImportError:
    RESILIENCE_AVAILABLE = False


class RecoveryResilienceBridge:
    """Bridge between recovery/resilience and AMOS Brain."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._engine: Optional[RecoveryResilienceEngine] = None

    @property
    def engine(self) -> Optional[RecoveryResilienceEngine]:
        """Lazy initialization of resilience engine."""
        if self._engine is None and RESILIENCE_AVAILABLE:
            self._engine = RecoveryResilienceEngine()
        return self._engine

    def assess_resilience(self) -> dict[str, Any]:
        """Perform comprehensive resilience assessment."""
        if not RESILIENCE_AVAILABLE or self.engine is None:
            return {"error": "resilience_engine not available"}

        assessment = self.engine.assess_resilience()
        return assessment.to_dict()

    def validate_recovery_path(
        self,
        path_id: str,
        failure_scenario: str,
        recovery_type: str,
        estimated_rto_minutes: int,
        automated: bool = False,
        tested: bool = False,
    ) -> dict[str, Any]:
        """Validate recovery path (I_recovery)."""
        if not RESILIENCE_AVAILABLE or self.engine is None:
            return {"error": "resilience_engine not available"}

        try:
            rec_type = RecoveryType(recovery_type)
        except ValueError:
            return {"error": f"Invalid recovery type: {recovery_type}"}

        path = RecoveryPath(
            path_id=path_id,
            name=path_id,
            description=f"Recovery for {failure_scenario}",
            failure_scenario=failure_scenario,
            recovery_type=rec_type,
            estimated_rto_minutes=estimated_rto_minutes,
            estimated_rpo_minutes=0,
            automated=automated,
            tested=tested,
        )
        self.engine.add_recovery_path(path)

        issues = []
        if not tested:
            issues.append("Recovery path has never been tested")
        if estimated_rto_minutes > 60:
            issues.append(f"RTO of {estimated_rto_minutes} min exceeds 1 hour guideline")

        return {
            "valid": len(issues) == 0,
            "path_id": path_id,
            "scenario": failure_scenario,
            "rto_minutes": estimated_rto_minutes,
            "issues": issues,
            "invariant": "I_recovery",
        }

    def validate_dr_capability(
        self,
        service_id: str,
        dr_enabled: bool,
        multi_region: bool,
        backup_frequency_hours: int,
        failover_automated: bool,
        estimated_failover_minutes: int,
        estimated_rpo_minutes: int,
        data_sync_mode: str,
        last_dr_test: str = None,
    ) -> dict[str, Any]:
        """Validate disaster recovery capability (I_disaster_recovery)."""
        if not RESILIENCE_AVAILABLE or self.engine is None:
            return {"error": "resilience_engine not available"}

        dr = DisasterRecoveryCapability(
            service_id=service_id,
            name=service_id,
            dr_enabled=dr_enabled,
            multi_region=multi_region,
            backup_frequency_hours=backup_frequency_hours,
            backup_retention_days=7,
            failover_automated=failover_automated,
            estimated_failover_minutes=estimated_failover_minutes,
            estimated_rpo_minutes=estimated_rpo_minutes,
            data_sync_mode=data_sync_mode,
            last_dr_test=last_dr_test,
        )
        self.engine.add_dr_capability(dr)

        issues = []
        if not dr_enabled:
            issues.append("DR is disabled for this service")
        if not last_dr_test:
            issues.append("DR has never been tested")
        if data_sync_mode == "async" and estimated_rpo_minutes > 60:
            issues.append(f"Async replication with {estimated_rpo_minutes} min RPO risks data loss")

        return {
            "valid": len(issues) == 0,
            "service_id": service_id,
            "dr_enabled": dr_enabled,
            "rpo_minutes": estimated_rpo_minutes,
            "issues": issues,
            "invariant": "I_disaster_recovery",
        }

    def validate_blast_containment(
        self,
        component_id: str,
        max_blast_radius: float,
        blast_unit: str,
        containment_measures: list[str],
        isolation_domain: str,
    ) -> dict[str, Any]:
        """Validate blast containment (I_blast)."""
        if not RESILIENCE_AVAILABLE or self.engine is None:
            return {"error": "resilience_engine not available"}

        try:
            unit = BlastRadiusUnit(blast_unit)
        except ValueError:
            return {"error": f"Invalid blast unit: {blast_unit}"}

        containment = BlastContainment(
            component_id=component_id,
            name=component_id,
            max_blast_radius=max_blast_radius,
            blast_unit=unit,
            containment_measures=containment_measures,
            isolation_domain=isolation_domain,
        )
        self.engine.add_blast_containment(containment)

        issues = []
        if not containment_measures:
            issues.append("No containment measures defined")

        return {
            "valid": len(issues) == 0,
            "component_id": component_id,
            "max_radius": max_blast_radius,
            "measures": len(containment_measures),
            "issues": issues,
            "invariant": "I_blast",
        }

    def validate_failure_domain(
        self,
        domain_id: str,
        domain_type: str,
        components: list[str],
        isolation_score: float,
        dependencies: list[str] = None,
    ) -> dict[str, Any]:
        """Validate failure domain isolation (I_isolation)."""
        if not RESILIENCE_AVAILABLE or self.engine is None:
            return {"error": "resilience_engine not available"}

        try:
            dom_type = FailureDomainType(domain_type)
        except ValueError:
            return {"error": f"Invalid domain type: {domain_type}"}

        domain = FailureDomain(
            domain_id=domain_id,
            name=domain_id,
            domain_type=dom_type,
            components=components,
            isolation_score=isolation_score,
            dependencies=dependencies or [],
        )
        self.engine.add_failure_domain(domain)

        issues = []
        if isolation_score < 0.5:
            issues.append(f"Low isolation score ({isolation_score}) may allow failure spread")

        return {
            "valid": len(issues) == 0,
            "domain_id": domain_id,
            "type": domain_type,
            "components": len(components),
            "isolation_score": isolation_score,
            "issues": issues,
            "invariant": "I_isolation",
        }

    def get_resilience_insights(self) -> dict[str, Any]:
        """Get resilience architecture insights."""
        if not RESILIENCE_AVAILABLE or self.engine is None:
            return {"error": "resilience_engine not available"}

        insights = self.engine.get_resilience_insights()
        return {
            "insights": insights,
            "count": len(insights),
        }


def get_recovery_resilience_bridge(repo_path: str | Path) -> RecoveryResilienceBridge:
    """Factory function to get recovery resilience bridge."""
    return RecoveryResilienceBridge(repo_path)
