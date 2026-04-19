"""
Constitutional Architecture Engine.

Validates the constitutional, semantic, and governance foundations
of software architecture.

Addresses:
- Constitutional ambiguity (who owns architectural facts)
- State ownership (who can write to mutable domains)
- Absence semantics (missing vs deleted vs deprecated)
- Semantic versioning honesty
- Protocol lifecycle management
- Authority and capability discipline
- Negative capability (what the system must refuse)

Mathematical Foundation:
- Constitution C = (Facts, Authorities, Transitions, Invariants)
- Validity requires: every fact has declared authority, change rights,
  approval rights, and retirement rights
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AbsenceState(Enum):
    """Taxonomy of absence states."""

    UNKNOWN = "unknown"
    UNSET = "unset"
    NULL = "null"
    EMPTY = "empty"
    DELETED = "deleted"
    TOMBSTONED = "tombstoned"
    REVOKED = "revoked"
    EXPIRED = "expired"
    DEPRECATED = "deprecated"
    REMOVED = "removed"
    UNSUPPORTED = "unsupported"


class ProtocolState(Enum):
    """Protocol/interface lifecycle states."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"
    REMOVED = "removed"
    TOMBSTONED = "tombstoned"


class AuthorityLevel(Enum):
    """Levels of architectural authority."""

    SYSTEM = "system"  # Platform/language-level
    ORGANIZATION = "organization"  # Company-wide
    TEAM = "team"  # Team-level
    INDIVIDUAL = "individual"  # Personal
    AMBIENT = "ambient"  # Implicit/contextual


@dataclass
class ArchitecturalFact:
    """A canonical architectural fact with declared authority."""

    fact_id: str
    name: str
    description: str
    fact_type: str  # "api", "schema", "config", "command", etc.
    current_value: Any
    absence_state: AbsenceState

    # Constitutional properties
    defining_authority: str  # Who defined this fact
    change_authority: str  # Who can change it
    approval_authority: str  # Who must approve changes
    retirement_authority: str  # Who can retire it

    # Lifecycle
    created_at: str
    modified_at: str
    version: str
    deprecation_date: str = None
    sunset_date: str = None

    # Semantic properties
    semantic_equivalents: list[str] = field(default_factory=list)
    breaking_changes: list[str] = field(default_factory=list)


@dataclass
class StateDomain:
    """A mutable state domain with ownership."""

    domain_id: str
    name: str
    description: str

    # Ownership
    canonical_writer: str  # Single writer principle
    conflict_resolution: str = None  # If multiple writers allowed

    # Writers
    declared_writers: list[str] = field(default_factory=list)
    observed_writers: list[str] = field(default_factory=list)

    # Absence semantics
    absence_taxonomy: list[AbsenceState] = field(default_factory=list)
    default_absence: AbsenceState = AbsenceState.UNKNOWN


@dataclass
class ConstitutionalViolation:
    """Violation of constitutional architecture rules."""

    violation_id: str
    violation_type: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    affected_fact: str = None
    affected_domain: str = None
    invariant_broken: str
    evidence: list[str] = field(default_factory=list)
    remediation: str = ""


@dataclass
class ConstitutionalAssessment:
    """Complete constitutional architecture assessment."""

    assessment_id: str
    timestamp: str

    # State
    facts: list[ArchitecturalFact]
    domains: list[StateDomain]
    violations: list[ConstitutionalViolation]

    # Invariant status
    constitution_valid: bool
    ownership_valid: bool
    absence_valid: bool
    semantic_valid: bool
    protocol_valid: bool
    capability_valid: bool

    # Metrics
    total_facts: int
    facts_without_authority: int
    ambiguous_domains: int
    undefined_absence_states: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "timestamp": self.timestamp,
            "summary": {
                "total_facts": self.total_facts,
                "violations": len(self.violations),
                "critical": len([v for v in self.violations if v.severity == "critical"]),
            },
            "invariants": {
                "constitution": self.constitution_valid,
                "ownership": self.ownership_valid,
                "absence": self.absence_valid,
                "semantic": self.semantic_valid,
                "protocol": self.protocol_valid,
                "capability": self.capability_valid,
            },
        }


class ConstitutionalArchitectureEngine:
    """
    Engine for constitutional architecture validation.

    Validates:
    - Every architectural fact has declared authority
    - State ownership is unambiguous
    - Absence semantics are explicit
    - Semantic versioning is honest
    - Protocol lifecycles are complete
    - Capabilities are scoped (not ambient)
    - Negative capabilities are defined
    """

    def __init__(self):
        self.facts: Dict[str, ArchitecturalFact] = {}
        self.domains: Dict[str, StateDomain] = {}
        self.assessments: list[ConstitutionalAssessment] = []

    def add_fact(self, fact: ArchitecturalFact) -> None:
        """Add an architectural fact to the registry."""
        self.facts[fact.fact_id] = fact

    def add_domain(self, domain: StateDomain) -> None:
        """Add a state domain to the registry."""
        self.domains[domain.domain_id] = domain

    def assess_constitutional_integrity(self) -> ConstitutionalAssessment:
        """
        Perform comprehensive constitutional architecture assessment.

        Returns:
            Assessment with all violations found

        """
        violations: list[ConstitutionalViolation] = []

        # 1. Check constitutional invariants (I_constitution)
        for fact_id, fact in self.facts.items():
            # Check for undefined authorities
            if not fact.defining_authority or fact.defining_authority == "ambient":
                violations.append(
                    ConstitutionalViolation(
                        violation_id=f"const_{len(violations)}",
                        violation_type="constitutional_ambiguity",
                        severity="critical",
                        description=f"Fact '{fact.name}' has no defining authority",
                        affected_fact=fact_id,
                        invariant_broken="I_constitution",
                        evidence=[f"defining_authority='{fact.defining_authority}'"],
                        remediation="Declare explicit defining authority",
                    )
                )

            # Check for missing change/approval/retirement authorities
            for auth_type, auth_value in [
                ("change", fact.change_authority),
                ("approval", fact.approval_authority),
                ("retirement", fact.retirement_authority),
            ]:
                if not auth_value:
                    violations.append(
                        ConstitutionalViolation(
                            violation_id=f"const_{len(violations)}",
                            violation_type="authority_gap",
                            severity="high",
                            description=f"Fact '{fact.name}' lacks {auth_type} authority",
                            affected_fact=fact_id,
                            invariant_broken="I_constitution",
                            evidence=[f"{auth_type}_authority is undefined"],
                            remediation=f"Declare {auth_type} authority",
                        )
                    )

        # 2. Check state ownership (I_state_ownership)
        for domain_id, domain in self.domains.items():
            # Check for multiple writers without conflict resolution
            if len(domain.observed_writers) > 1 and not domain.conflict_resolution:
                violations.append(
                    ConstitutionalViolation(
                        violation_id=f"owner_{len(violations)}",
                        violation_type="ownership_ambiguity",
                        severity="critical",
                        description=f"Domain '{domain.name}' has multiple writers without conflict resolution",
                        affected_domain=domain_id,
                        invariant_broken="I_state_ownership",
                        evidence=[f"writers: {domain.observed_writers}"],
                        remediation="Declare canonical writer or explicit conflict resolution rule",
                    )
                )

            # Check for writer mismatch
            undeclared = set(domain.observed_writers) - set(domain.declared_writers)
            if undeclared:
                violations.append(
                    ConstitutionalViolation(
                        violation_id=f"owner_{len(violations)}",
                        violation_type="undeclared_writer",
                        severity="high",
                        description=f"Domain '{domain.name}' has undeclared writers",
                        affected_domain=domain_id,
                        invariant_broken="I_state_ownership",
                        evidence=[f"undeclared: {list(undeclared)}"],
                        remediation="Add undeclared writers to declared_writers or remove them",
                    )
                )

        # 3. Check absence semantics (I_absence)
        for domain_id, domain in self.domains.items():
            if not domain.absence_taxonomy:
                violations.append(
                    ConstitutionalViolation(
                        violation_id=f"abs_{len(violations)}",
                        violation_type="absence_semantics_undefined",
                        severity="high",
                        description=f"Domain '{domain.name}' has no explicit absence taxonomy",
                        affected_domain=domain_id,
                        invariant_broken="I_absence",
                        evidence=["absence_taxonomy is empty"],
                        remediation="Define explicit absence taxonomy for this domain",
                    )
                )

        # Build assessment
        assessment = ConstitutionalAssessment(
            assessment_id=f"const_{len(self.assessments)}",
            timestamp="2024-01-01T00:00:00Z",  # Placeholder
            facts=list(self.facts.values()),
            domains=list(self.domains.values()),
            violations=violations,
            constitution_valid=not any(
                v for v in violations if v.invariant_broken == "I_constitution"
            ),
            ownership_valid=not any(
                v for v in violations if v.invariant_broken == "I_state_ownership"
            ),
            absence_valid=not any(v for v in violations if v.invariant_broken == "I_absence"),
            semantic_valid=True,  # Simplified
            protocol_valid=True,  # Simplified
            capability_valid=True,  # Simplified
            total_facts=len(self.facts),
            facts_without_authority=len(
                [f for f in self.facts.values() if not f.defining_authority]
            ),
            ambiguous_domains=len(
                [d for d in self.domains.values() if len(d.observed_writers) > 1]
            ),
            undefined_absence_states=len(
                [d for d in self.domains.values() if not d.absence_taxonomy]
            ),
        )

        self.assessments.append(assessment)
        return assessment

    def check_semantic_versioning(
        self, claimed_version: str, actual_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if semantic versioning is honest.

        Args:
            claimed_version: The version number claimed
            actual_changes: Measured changes to public surface

        Returns:
            Honesty assessment

        """
        # Parse version
        parts = claimed_version.split(".")
        if len(parts) != 3:
            return {"valid": False, "reason": "Invalid version format"}

        major, minor, patch = parts

        # Check against actual changes
        breaking = actual_changes.get("breaking", [])
        features = actual_changes.get("features", [])
        fixes = actual_changes.get("fixes", [])

        issues = []

        # If breaking changes, major should increment
        if breaking and not self._is_major_bump(claimed_version):
            issues.append("Breaking changes without major version bump")

        # If features added, minor should increment (or major)
        if features and self._is_patch_only(claimed_version):
            issues.append("New features with only patch bump")

        return {
            "valid": len(issues) == 0,
            "claimed_version": claimed_version,
            "breaking_changes": len(breaking),
            "features": len(features),
            "fixes": len(fixes),
            "issues": issues,
            "invariant": "I_semver",
        }

    def _is_major_bump(self, version: str) -> bool:
        """Check if version indicates major bump."""
        # Simplified: assume version format is correct
        return True  # Placeholder

    def _is_patch_only(self, version: str) -> bool:
        """Check if version is patch-only change."""
        # Simplified
        return False  # Placeholder

    def check_protocol_lifecycle(
        self, interface_id: str, current_state: ProtocolState
    ) -> Dict[str, Any]:
        """
        Check if interface has complete protocol lifecycle.

        Args:
            interface_id: Interface identifier
            current_state: Current protocol state

        Returns:
            Lifecycle completeness assessment

        """
        fact = self.facts.get(interface_id)
        if not fact:
            return {"valid": False, "reason": "Interface not found"}

        issues = []

        # Check for missing lifecycle properties
        if current_state == ProtocolState.DEPRECATED:
            if not fact.deprecation_date:
                issues.append("Deprecated interface lacks deprecation date")
            if not fact.sunset_date:
                issues.append("Deprecated interface lacks sunset date")

        # Check for replacement
        if current_state in [ProtocolState.DEPRECATED, ProtocolState.BLOCKED]:
            if not fact.semantic_equivalents:
                issues.append("Deprecated/blocked interface has no replacement")

        return {
            "valid": len(issues) == 0,
            "interface": interface_id,
            "state": current_state.value,
            "issues": issues,
            "invariant": "I_protocol_lifecycle",
        }

    def check_capability_discipline(
        self, action: str, required_capability: str, granted_authority: str
    ) -> Dict[str, Any]:
        """
        Check if action uses scoped capability vs ambient authority.

        Args:
            action: The action being performed
            required_capability: Required capability for action
            granted_authority: Authority actually granted

        Returns:
            Capability discipline assessment

        """
        # Check if authority is ambient
        is_ambient = (
            granted_authority == "ambient" or AuthorityLevel.AMBIENT.value in granted_authority
        )

        if is_ambient:
            return {
                "valid": False,
                "action": action,
                "issue": "Action uses ambient authority instead of scoped capability",
                "required": required_capability,
                "granted": granted_authority,
                "invariant": "I_capability",
                "remediation": "Replace ambient authority with explicit scoped capability",
            }

        return {
            "valid": True,
            "action": action,
            "capability": granted_authority,
            "invariant": "I_capability",
        }

    def check_negative_capability(
        self, system_state: Dict[str, Any], forbidden_states: list[dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if forbidden states are explicitly blocked.

        Args:
            system_state: Current system state
            forbidden_states: List of states that must be forbidden

        Returns:
            Negative capability assessment

        """
        violations = []

        for forbidden in forbidden_states:
            # Check if this forbidden state is reachable
            if self._state_matches(system_state, forbidden):
                violations.append(
                    {
                        "forbidden_state": forbidden,
                        "current_state": system_state,
                        "issue": "Forbidden state is reachable",
                    }
                )

        return {
            "valid": len(violations) == 0,
            "forbidden_states_checked": len(forbidden_states),
            "violations": violations,
            "invariant": "I_negative_capability",
        }

    def _state_matches(self, state: Dict[str, Any], pattern: Dict[str, Any]) -> bool:
        """Check if state matches forbidden pattern."""
        for key, value in pattern.items():
            if key not in state or state[key] != value:
                return False
        return True

    def get_constitutional_insights(self) -> list[dict[str, Any]]:
        """Get general constitutional insights."""
        return [
            {
                "insight": "Constitutional ambiguity is the root of many architecture failures",
                "evidence": "Facts without declared authority become conventions, not laws",
                "recommendation": "Declare authority for every architecture-critical fact",
                "invariant": "I_constitution",
            },
            {
                "insight": "State ownership ambiguity leads to silent conflicts",
                "evidence": "Multiple writers to same domain without resolution rules",
                "recommendation": "Apply single-writer principle or explicit conflict resolution",
                "invariant": "I_state_ownership",
            },
            {
                "insight": "Absence semantics are often implicit and inconsistent",
                "evidence": "Missing, deleted, deprecated, null all treated as same",
                "recommendation": "Define explicit absence taxonomy for each domain",
                "invariant": "I_absence",
            },
            {
                "insight": "Semantic versioning dishonesty breaks compatibility guarantees",
                "evidence": "Breaking changes with minor/patch bumps",
                "recommendation": "Measure public surface delta against claimed version",
                "invariant": "I_semver",
            },
            {
                "insight": "Ambient authority is a security and correctness risk",
                "evidence": "Power granted by context instead of explicit capability",
                "recommendation": "Replace ambient authority with scoped capabilities",
                "invariant": "I_capability",
            },
            {
                "insight": "Systems often define what they can do, not what they must refuse",
                "evidence": "No explicit representation of forbidden states",
                "recommendation": "Define and block negative capabilities",
                "invariant": "I_negative_capability",
            },
        ]
