"""Pathology-Aware Architecture Bridge.

Integrates the Deep Architectural Pathology Engine with the AMOS Brain
to provide pre-decision pathology validation.

This allows the brain to:
1. Check for authority inversion before accepting decisions
2. Validate bootstrap paths before recommending actions
3. Detect layer leakage in proposed changes
4. Ensure artifact chain continuity for deployments
5. Verify migration geometry for database changes

Invariants enforced:
- I_decision_safe: Brain decisions preserve architectural validity
- I_pathology_aware: All critical decisions check for pathologies first
- I_repair_safe: Repairs don't increase pathology count
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Import architecture bridge components
from .architecture_bridge import (
    ArchitecturalCognitionBridge,
    ArchitecturalContext,
    ArchitectureValidationResult,
    get_architecture_bridge,
)

# Import pathology engine
try:
    from repo_doctor.arch_pathologies import (
        ArchitecturalPathology,
        ArchitecturalPathologyEngine,
        PathologyType,
        get_pathology_engine,
    )
    PATHOLOGY_AVAILABLE = True
except ImportError:
    PATHOLOGY_AVAILABLE = False


@dataclass
class PathologyAwareContext:
    """Extended architectural context with pathology information."""

    # Base architecture context
    arch_context: ArchitecturalContext

    # Pathology summary
    total_pathologies: int = 0
    critical_pathologies: int = 0
    high_pathologies: int = 0
    medium_pathologies: int = 0
    low_pathologies: int = 0

    # Pathology breakdown by type
    authority_issues: list[ArchitecturalPathology] = field(default_factory=list)
    layer_leakage: list[ArchitecturalPathology] = field(default_factory=list)
    bootstrap_issues: list[ArchitecturalPathology] = field(default_factory=list)
    shadow_deps: list[ArchitecturalPathology] = field(default_factory=list)
    artifact_issues: list[ArchitecturalPathology] = field(default_factory=list)
    migration_issues: list[ArchitecturalPathology] = field(default_factory=list)
    mode_issues: list[ArchitecturalPathology] = field(default_factory=list)

    # Composite scores
    pathology_score: float = 1.0  # 1.0 = clean, 0.0 = max pathologies
    authority_score: float = 1.0
    bootstrap_score: float = 1.0
    artifact_score: float = 1.0

    def __post_init__(self):
        """Calculate composite scores after initialization."""
        if self.total_pathologies > 0:
            # Weight by severity
            weighted_count = (
                self.critical_pathologies * 4 +
                self.high_pathologies * 2 +
                self.medium_pathologies * 1 +
                self.low_pathologies * 0.5
            )
            self.pathology_score = max(0.0, 1.0 - (weighted_count / 10))

            # Authority score
            auth_weight = len(self.authority_issues) * 2
            self.authority_score = max(0.0, 1.0 - (auth_weight / 5))

            # Bootstrap score
            bootstrap_weight = len(self.bootstrap_issues) * 1.5
            self.bootstrap_score = max(0.0, 1.0 - (bootstrap_weight / 5))

            # Artifact score
            artifact_weight = len(self.artifact_issues) * 1.5
            self.artifact_score = max(0.0, 1.0 - (artifact_weight / 5))


@dataclass
class PathologyValidationResult:
    """Result of pre-decision pathology validation."""

    approved: bool
    decision_type: str
    pathology_score: float
    issues: list[str]
    warnings: list[str]
    risks: list[str]
    suggested_constraints: list[str]
    requires_human_review: bool
    details: dict[str, Any] = field(default_factory=dict)


class PathologyAwareArchitectureBridge:
    """
    Enhanced architecture bridge with pathology awareness.

    Provides:
    - Pre-decision pathology validation
    - Action-specific pathology risk assessment
    - Architecture + pathology unified context
    """

    def __init__(self, repo_path: str | Path | None = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self._arch_bridge: ArchitecturalCognitionBridge | None = None
        self._pathology_engine: Any = None

    @property
    def arch_bridge(self) -> ArchitecturalCognitionBridge:
        """Lazy initialization of base architecture bridge."""
        if self._arch_bridge is None:
            self._arch_bridge = get_architecture_bridge(self.repo_path)
        return self._arch_bridge

    @property
    def pathology_engine(self) -> Any:
        """Lazy initialization of pathology engine."""
        if self._pathology_engine is None and PATHOLOGY_AVAILABLE:
            self._pathology_engine = get_pathology_engine(self.repo_path)
        return self._pathology_engine

    def get_pathology_aware_context(self) -> PathologyAwareContext:
        """Get complete architecture + pathology context."""
        # Get base architecture context
        arch_context = self.arch_bridge.get_context()

        if not PATHOLOGY_AVAILABLE or self.pathology_engine is None:
            # Return context without pathology data
            return PathologyAwareContext(arch_context=arch_context)

        # Run pathology detection
        pathology_results = self.pathology_engine.detect_all()

        # Flatten all pathologies
        all_pathologies: list[ArchitecturalPathology] = []
        for detector_pathologies in pathology_results.values():
            all_pathologies.extend(detector_pathologies)

        # Count by severity
        critical = sum(1 for p in all_pathologies if p.severity == "critical")
        high = sum(1 for p in all_pathologies if p.severity == "high")
        medium = sum(1 for p in all_pathologies if p.severity == "medium")
        low = sum(1 for p in all_pathologies if p.severity == "low")

        # Categorize by type
        authority_issues = [
            p for p in all_pathologies
            if p.pathology_type in [
                PathologyType.AUTHORITY_INVERSION,
                PathologyType.AUTHORITY_DUPLICATION,
            ]
        ]

        layer_leakage = [
            p for p in all_pathologies
            if p.pathology_type == PathologyType.LAYER_LEAKAGE
        ]

        bootstrap_issues = [
            p for p in all_pathologies
            if p.pathology_type == PathologyType.BOOTSTRAP_FAILURE
        ]

        shadow_deps = [
            p for p in all_pathologies
            if p.pathology_type in [
                PathologyType.SHADOW_DEPENDENCY,
                PathologyType.FOLKLORE_OPERATION,
            ]
        ]

        artifact_issues = [
            p for p in all_pathologies
            if p.pathology_type in [
                PathologyType.ARTIFACT_DISCONTINUITY,
                PathologyType.DERIVATION_DRIFT,
            ]
        ]

        migration_issues = [
            p for p in all_pathologies
            if p.pathology_type == PathologyType.MIGRATION_GEOMETRY_FAILURE
        ]

        mode_issues = [
            p for p in all_pathologies
            if p.pathology_type == PathologyType.MODE_LATTICE_DRIFT
        ]

        return PathologyAwareContext(
            arch_context=arch_context,
            total_pathologies=len(all_pathologies),
            critical_pathologies=critical,
            high_pathologies=high,
            medium_pathologies=medium,
            low_pathologies=low,
            authority_issues=authority_issues,
            layer_leakage=layer_leakage,
            bootstrap_issues=bootstrap_issues,
            shadow_deps=shadow_deps,
            artifact_issues=artifact_issues,
            migration_issues=migration_issues,
            mode_issues=mode_issues,
        )

    def validate_with_pathologies(
        self,
        action: str,
        target_files: list[str],
        context: dict[str, Any] | None = None,
    ) -> PathologyValidationResult:
        """
        Validate an action against both architecture and pathologies.

        Args:
            action: Type of action (modify, delete, create, refactor, migrate)
            target_files: Files that will be changed
            context: Additional context for validation

        Returns:
            PathologyValidationResult with approval status and constraints
        """
        if context is None:
            context = {}

        # Get base architecture validation
        arch_result = self.arch_bridge.validate(action, target_files)

        # Get pathology context
        pathology_context = self.get_pathology_aware_context()

        issues = []
        warnings = []
        risks = []
        constraints = []

        # Check pathology score threshold
        if pathology_context.pathology_score < 0.5:
            issues.append(
                f"Repository has severe architectural pathologies "
                f"(score: {pathology_context.pathology_score:.2f})"
            )

        # Action-specific pathology checks
        if action == "migrate":
            # Check for migration geometry issues
            if pathology_context.migration_issues:
                mig_count = len(pathology_context.migration_issues)
                issues.append(
                    f"Found {mig_count} migration geometry issues"
                )
                for p in pathology_context.migration_issues[:3]:
                    issues.append(f"  - {p.message}")

        elif action == "delete":
            # Check for authority issues (deleting authority sources)
            if pathology_context.authority_issues:
                auth_count = len(pathology_context.authority_issues)
                warnings.append(
                    f"Repository has {auth_count} authority issues; "
                    "deletion may worsen authority duplication"
                )

        elif action == "create":
            # Check for bootstrap issues (new files may need manual setup)
            if pathology_context.bootstrap_issues:
                constraints.append(
                    "Ensure new files don't require manual bootstrap steps"
                )

        elif action == "refactor":
            # Check for layer leakage (refactoring may worsen leakage)
            if pathology_context.layer_leakage:
                leak_count = len(pathology_context.layer_leakage)
                warnings.append(
                    f"Repository has {leak_count} layer leakage issues; "
                    "refactoring should reduce, not increase, these"
                )

        # Artifact continuity check for all actions
        if pathology_context.artifact_issues:
            artifact_count = len(pathology_context.artifact_issues)
            risks.append(
                f"Repository has {artifact_count} artifact continuity issues; "
                "ensure changes are reflected in build artifacts"
            )

        # Determine approval
        approved = arch_result.approved and len(issues) == 0

        # Require human review for high pathology count
        requires_review = (
            pathology_context.critical_pathologies > 0 or
            pathology_context.high_pathologies > 2 or
            pathology_context.pathology_score < 0.7
        )

        # If approved but has warnings, add constraint
        if approved and (warnings or risks):
            constraints.append(
                "Monitor for architectural pathology increase after change"
            )

        return PathologyValidationResult(
            approved=approved,
            decision_type=action,
            pathology_score=pathology_context.pathology_score,
            issues=issues,
            warnings=warnings,
            risks=risks,
            suggested_constraints=constraints,
            requires_human_review=requires_review,
            details={
                "arch_result": arch_result,
                "pathology_context": pathology_context,
            },
        )

    def get_repair_recommendations(
        self, max_recommendations: int = 5
    ) -> list[dict[str, Any]]:
        """Get prioritized pathology repair recommendations."""
        if not PATHOLOGY_AVAILABLE or self.pathology_engine is None:
            return []

        pathology_context = self.get_pathology_aware_context()
        recommendations = []

        # Priority 1: Critical pathologies
        for p in pathology_context.authority_issues:
            if p.severity == "critical":
                recommendations.append({
                    "priority": "critical",
                    "type": "authority",
                    "description": p.message,
                    "location": p.location,
                    "remediation": p.remediation,
                })

        # Priority 2: Bootstrap issues
        for p in pathology_context.bootstrap_issues:
            recommendations.append({
                "priority": "high",
                "type": "bootstrap",
                "description": p.message,
                "location": p.location,
                "remediation": p.remediation,
            })

        # Priority 3: Artifact issues
        for p in pathology_context.artifact_issues:
            recommendations.append({
                "priority": "high",
                "type": "artifact",
                "description": p.message,
                "location": p.location,
                "remediation": p.remediation,
            })

        # Priority 4: Migration issues
        for p in pathology_context.migration_issues:
            recommendations.append({
                "priority": "medium",
                "type": "migration",
                "description": p.message,
                "location": p.location,
                "remediation": p.remediation,
            })

        return recommendations[:max_recommendations]


def get_pathology_aware_bridge(
    repo_path: str | Path | None = None,
) -> PathologyAwareArchitectureBridge:
    """Factory function to get pathology-aware bridge instance."""
    return PathologyAwareArchitectureBridge(repo_path)
