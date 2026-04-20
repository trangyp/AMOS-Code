"""Constitutional Architecture Bridge.

Integrates constitutional architecture validation with AMOS Brain cognition.

Provides API for:
- Constitutional integrity assessment
- State ownership validation
- Absence semantics verification
- Semantic versioning honesty checking
- Protocol lifecycle validation
- Capability discipline verification
- Negative capability checking
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Import constitutional architecture engine
try:
    from repo_doctor.constitutional_architecture_engine import (
        AbsenceState,
        ArchitecturalFact,
        ConstitutionalArchitectureEngine,
        ConstitutionalAssessment,
        ProtocolState,
        StateDomain,
    )

    CONSTITUTIONAL_AVAILABLE = True
except ImportError:
    CONSTITUTIONAL_AVAILABLE = False


class ConstitutionalBridge:
    """Bridge between constitutional architecture and AMOS Brain."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._engine: Optional[ConstitutionalArchitectureEngine] = None

    @property
    def engine(self) -> Optional[ConstitutionalArchitectureEngine]:
        """Lazy initialization of constitutional engine."""
        if self._engine is None and CONSTITUTIONAL_AVAILABLE:
            self._engine = ConstitutionalArchitectureEngine()
        return self._engine

    def assess_constitutional_integrity(self) -> dict[str, Any]:
        """Perform comprehensive constitutional architecture assessment."""
        if not CONSTITUTIONAL_AVAILABLE or self.engine is None:
            return {"error": "constitutional_engine not available"}

        assessment = self.engine.assess_constitutional_integrity()
        return assessment.to_dict()

    def check_state_ownership(
        self,
        domain: str,
        declared_writers: list[str],
        observed_writers: list[str],
    ) -> dict[str, Any]:
        """Check if state domain has clear ownership."""
        if not CONSTITUTIONAL_AVAILABLE or self.engine is None:
            return {"error": "constitutional_engine not available"}

        # Add domain to engine
        domain_obj = StateDomain(
            domain_id=domain,
            name=domain,
            description=f"State domain: {domain}",
            canonical_writer=declared_writers[0] if declared_writers else "unknown",
            declared_writers=declared_writers,
            observed_writers=observed_writers,
        )
        self.engine.add_domain(domain_obj)

        # Check for violations
        undeclared = set(observed_writers) - set(declared_writers)
        has_conflict = len(observed_writers) > 1 and not domain_obj.conflict_resolution

        return {
            "valid": len(undeclared) == 0 and not has_conflict,
            "domain": domain,
            "declared_writers": declared_writers,
            "observed_writers": observed_writers,
            "undeclared": list(undeclared),
            "has_conflict": has_conflict,
            "invariant": "I_state_ownership",
            "issue": (
                f"Undeclared writers: {list(undeclared)}"
                if undeclared
                else "Multiple writers without conflict resolution"
                if has_conflict
                else None
            ),
        }

    def validate_absence_semantics(
        self,
        domain: str,
        required_states: list[str],
    ) -> dict[str, Any]:
        """Validate domain has explicit absence taxonomy."""
        if not CONSTITUTIONAL_AVAILABLE or self.engine is None:
            return {"error": "constitutional_engine not available"}

        # Convert string states to AbsenceState enum
        available_states = []
        for state in required_states:
            try:
                available_states.append(AbsenceState(state))
            except ValueError:
                logger.debug(f"Invalid absence state: {state}")

        # Add domain with absence taxonomy
        domain_obj = StateDomain(
            domain_id=domain,
            name=domain,
            description=f"State domain: {domain}",
            canonical_writer="system",
            absence_taxonomy=available_states,
        )
        self.engine.add_domain(domain_obj)

        # Check for common required states
        standard_states = [
            AbsenceState.ACTIVE,
            AbsenceState.DEPRECATED,
            AbsenceState.REMOVED,
            AbsenceState.UNSUPPORTED,
        ]

        missing = [s.value for s in standard_states if s not in available_states]

        return {
            "valid": len(missing) == 0,
            "domain": domain,
            "available_states": [s.value for s in available_states],
            "missing_standard_states": missing,
            "invariant": "I_absence",
            "issue": f"Missing states: {missing}" if missing else None,
        }

    def check_semantic_versioning(
        self,
        claimed_version: str,
        actual_changes: dict[str, Any],
    ) -> dict[str, Any]:
        """Check if semantic versioning is honest."""
        if not CONSTITUTIONAL_AVAILABLE or self.engine is None:
            return {"error": "constitutional_engine not available"}

        return self.engine.check_semantic_versioning(claimed_version, actual_changes)

    def check_protocol_lifecycle(
        self,
        interface: str,
        current_state: str,
        has_replacement: bool = False,
        sunset_date: str = None,
    ) -> dict[str, Any]:
        """Validate interface has complete protocol lifecycle."""
        if not CONSTITUTIONAL_AVAILABLE or self.engine is None:
            return {"error": "constitutional_engine not available"}

        # Convert string state to ProtocolState enum
        try:
            state = ProtocolState(current_state)
        except ValueError:
            return {
                "valid": False,
                "error": f"Invalid protocol state: {current_state}",
            }

        # Add fact to engine
        fact = ArchitecturalFact(
            fact_id=interface,
            name=interface,
            description=f"Interface: {interface}",
            fact_type="interface",
            current_value=state.value,
            absence_state=AbsenceState.ACTIVE,
            defining_authority="system",
            change_authority="system",
            approval_authority="system",
            retirement_authority="system",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-01T00:00:00Z",
            version="1.0.0",
            sunset_date=sunset_date,
            semantic_equivalents=["replacement"] if has_replacement else [],
        )
        self.engine.add_fact(fact)

        return self.engine.check_protocol_lifecycle(interface, state)

    def check_capability_discipline(
        self,
        action: str,
        required_capability: str,
        granted_authority: str,
    ) -> dict[str, Any]:
        """Check if action uses scoped capability vs ambient authority."""
        if not CONSTITUTIONAL_AVAILABLE or self.engine is None:
            return {"error": "constitutional_engine not available"}

        return self.engine.check_capability_discipline(
            action, required_capability, granted_authority
        )

    def check_negative_capability(
        self,
        system_state: dict[str, Any],
        forbidden_states: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Check if forbidden states are explicitly blocked."""
        if not CONSTITUTIONAL_AVAILABLE or self.engine is None:
            return {"error": "constitutional_engine not available"}

        return self.engine.check_negative_capability(system_state, forbidden_states)

    def get_constitutional_insights(self) -> dict[str, Any]:
        """Get general constitutional insights."""
        if not CONSTITUTIONAL_AVAILABLE or self.engine is None:
            return {"error": "constitutional_engine not available"}

        insights = self.engine.get_constitutional_insights()
        return {
            "insights": insights,
            "count": len(insights),
        }


def get_constitutional_bridge(repo_path: str | Path) -> ConstitutionalBridge:
    """Factory function to get constitutional bridge."""
    return ConstitutionalBridge(repo_path)
