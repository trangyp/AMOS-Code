"""Repair Synthesis Bridge.

Integrates Repo Doctor's repair planning with the AMOS Brain
to enable automated fix generation from:
- Pathology detections (authority inversion, layer leakage, etc.)
- Invariant violations (boundary, authority, entanglement)
- Temporal drift (state vector degradation)
- Entanglement analysis (coupling issues)

The bridge synthesizes concrete repair actions that can be:
1. Automatically applied (safe, low-risk fixes)
2. Human-reviewed (medium-risk changes)
3. Planned for batch execution (complex multi-file repairs)

Repair synthesis objective:
    min_R [
        c1·EditCost +
        c2·BlastRadius +
        c3·EntanglementRisk +
        c4·RollbackCost +
        c5·RolloutCost +
        c6·AuthorityDuplicationIncrease +
        c7·BoundaryViolationIncrease
        - c8·EnergyReduction
        - c9·ArchitectureIntegrityGain
    ]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Import repair planning from repo_doctor_omega
try:
    from repo_doctor_omega.solver import RepairOptimizer, RepairPlan
    from repo_doctor_omega.state.basis import BasisVector, RepositoryState

    REPAIR_AVAILABLE = True
except ImportError:
    REPAIR_AVAILABLE = False

# Import pathology detection (fallback to old for compatibility)
try:
    from repo_doctor.arch_pathologies import (
        ArchitecturalPathology,
        PathologyType,
        get_pathology_engine,
    )

    PATHOLOGY_AVAILABLE = True
except ImportError:
    PATHOLOGY_AVAILABLE = False


@dataclass
class SynthesizedRepair:
    """A synthesized repair with full context."""

    # Identification
    repair_id: str
    source_type: str  # "pathology", "invariant", "temporal", "entanglement"
    source_id: str  # The specific pathology or invariant that triggered this

    # Target
    target_file: str
    target_module: str
    line_number: int = None

    # Repair details
    repair_type: str = "modify"  # "add", "remove", "modify", "move", "create"
    description: str = ""
    original_code: str = None
    suggested_code: str = None
    diff_preview: str = None

    # Risk assessment
    auto_fixable: bool = False
    risk_level: str = "medium"  # "low", "medium", "high", "critical"
    confidence: float = 0.0  # 0-1

    # Architecture impact
    preserves_invariants: bool = True
    reduces_pathologies: bool = True
    estimated_energy_change: float = 0.0  # Positive = better

    # Metadata
    requires_human_review: bool = True
    test_recommendations: list[str] = field(default_factory=list)
    rollback_plan: str = None


@dataclass
class RepairSynthesisResult:
    """Complete result of repair synthesis."""

    # Synthesis summary
    total_repairs: int
    auto_fixable: int
    human_required: int
    total_estimated_energy_gain: float

    # Repairs by category
    critical_repairs: list[SynthesizedRepair]
    high_priority: list[SynthesizedRepair]
    medium_priority: list[SynthesizedRepair]
    low_priority: list[SynthesizedRepair]

    # Batched repairs
    safe_batch: list[SynthesizedRepair]  # Can apply together
    risky_batch: list[SynthesizedRepair]  # Need coordination

    # Action plan
    recommended_order: list[str]  # Repair IDs in order


class RepairSynthesisBridge:
    """Bridge between repair planning and AMOS Brain cognition.

    Synthesizes concrete repair actions from abstract detections:
    - Pathology → Concrete fix suggestions
    - Invariant violations → Remediation steps
    - Temporal drift → State restoration
    - Entanglement issues → Decoupling actions
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._optimizer: Optional[Any] = None

        # Risk thresholds
        self.auto_fix_threshold = 0.8  # Confidence needed for auto-fix
        self.human_review_threshold = 0.5  # Below this requires human review

    @property
    def optimizer(self) -> Optional[Any]:
        """Lazy initialization of repair optimizer."""
        if self._optimizer is None and REPAIR_AVAILABLE:
            self._optimizer = RepairOptimizer()
        return self._optimizer

    def synthesize_from_pathologies(
        self,
        pathologies: list[Any],
    ) -> list[SynthesizedRepair]:
        """Synthesize repairs from detected pathologies.

        Args:
            pathologies: List of ArchitecturalPathology objects

        Returns:
            List of synthesized repairs
        """
        repairs = []

        if not PATHOLOGY_AVAILABLE:
            return repairs

        for pathology in pathologies:
            repair = self._synthesize_pathology_repair(pathology)
            if repair:
                repairs.append(repair)

        return repairs

    def synthesize_from_invariants(
        self,
        invariant_results: list[Any],
    ) -> list[SynthesizedRepair]:
        """Synthesize repairs from invariant violations.

        Args:
            invariant_results: List of invariant check results

        Returns:
            List of synthesized repairs
        """
        repairs = []

        for result in invariant_results:
            if not getattr(result, "passed", True):
                repair = self._synthesize_invariant_repair(result)
                if repair:
                    repairs.append(repair)

        return repairs

    def generate_complete_repair_plan(
        self,
        include_pathologies: bool = True,
        include_invariants: bool = True,
    ) -> Optional[RepairSynthesisResult]:
        """Generate complete repair synthesis from all detections.

        Args:
            include_pathologies: Whether to include pathology-based repairs
            include_invariants: Whether to include invariant-based repairs

        Returns:
            Complete repair synthesis result
        """
        all_repairs: list[SynthesizedRepair] = []

        # Synthesize from pathologies
        if include_pathologies and PATHOLOGY_AVAILABLE:
            try:
                engine = get_pathology_engine(self.repo_path)
                pathology_results = engine.detect_all()

                for detector_pathologies in pathology_results.values():
                    repairs = self.synthesize_from_pathologies(detector_pathologies)
                    all_repairs.extend(repairs)
            except Exception as e:
                logger.debug(f"Repair synthesis failed for detector: {e}")

        # Categorize by risk
        critical = [r for r in all_repairs if r.risk_level == "critical"]
        high = [r for r in all_repairs if r.risk_level == "high"]
        medium = [r for r in all_repairs if r.risk_level == "medium"]
        low = [r for r in all_repairs if r.risk_level == "low"]

        # Determine auto-fixable
        auto_fixable = [r for r in all_repairs if r.auto_fixable]
        human_required = [r for r in all_repairs if r.requires_human_review]

        # Create safe and risky batches
        safe_batch = [
            r for r in all_repairs if r.auto_fixable and r.risk_level in ["low", "medium"]
        ]
        risky_batch = [
            r for r in all_repairs if not r.auto_fixable or r.risk_level in ["high", "critical"]
        ]

        # Calculate total energy gain
        total_energy = sum(r.estimated_energy_change for r in all_repairs)

        # Determine recommended order
        recommended_order = self._determine_repair_order(all_repairs)

        return RepairSynthesisResult(
            total_repairs=len(all_repairs),
            auto_fixable=len(auto_fixable),
            human_required=len(human_required),
            total_estimated_energy_gain=total_energy,
            critical_repairs=critical,
            high_priority=high,
            medium_priority=medium,
            low_priority=low,
            safe_batch=safe_batch,
            risky_batch=risky_batch,
            recommended_order=recommended_order,
        )

    def get_safe_auto_fixes(
        self,
        max_fixes: int = 10,
    ) -> list[SynthesizedRepair]:
        """Get repairs that can be safely applied automatically.

        Args:
            max_fixes: Maximum number of fixes to return

        Returns:
            List of safe auto-fixable repairs
        """
        plan = self.generate_complete_repair_plan()
        if plan is None:
            return []

        return plan.safe_batch[:max_fixes]

    def _synthesize_pathology_repair(
        self,
        pathology: Any,
    ) -> Optional[SynthesizedRepair]:
        """Synthesize a repair from a single pathology."""
        if not PATHOLOGY_AVAILABLE:
            return None

        ptype = pathology.pathology_type
        location = pathology.location
        severity = pathology.severity

        # Authority inversion repairs
        if ptype == PathologyType.AUTHORITY_INVERSION:
            return SynthesizedRepair(
                repair_id=f"auth_inv_{id(pathology)}",
                source_type="pathology",
                source_id=str(ptype),
                target_file=location,
                target_module=self._file_to_module(location),
                repair_type="move",
                description=f"Move authority from {location} to canonical layer",
                original_code=None,
                suggested_code="# TODO: Move to canonical authority layer",
                auto_fixable=False,
                risk_level=severity,
                confidence=0.7,
                preserves_invariants=True,
                reduces_pathologies=True,
                estimated_energy_change=0.2,
                requires_human_review=True,
                test_recommendations=["Verify authority chain post-migration"],
            )

        # Layer leakage repairs
        elif ptype == PathologyType.LAYER_LEAKAGE:
            return SynthesizedRepair(
                repair_id=f"layer_leak_{id(pathology)}",
                source_type="pathology",
                source_id=str(ptype),
                target_file=location,
                target_module=self._file_to_module(location),
                repair_type="refactor",
                description="Extract cross-layer logic to declared interface",
                original_code=None,
                suggested_code="# TODO: Extract to interface layer",
                auto_fixable=False,
                risk_level=severity,
                confidence=0.6,
                preserves_invariants=True,
                reduces_pathologies=True,
                estimated_energy_change=0.15,
                requires_human_review=True,
                test_recommendations=["Test cross-layer contract"],
            )

        # Bootstrap failure repairs
        elif ptype == PathologyType.BOOTSTRAP_FAILURE:
            return SynthesizedRepair(
                repair_id=f"bootstrap_{id(pathology)}",
                source_type="pathology",
                source_id=str(ptype),
                target_file=location,
                target_module=self._file_to_module(location),
                repair_type="add",
                description="Add explicit bootstrap dependency declaration",
                original_code=None,
                suggested_code="# TODO: Add to bootstrap manifest",
                auto_fixable=True,
                risk_level="low",
                confidence=0.9,
                preserves_invariants=True,
                reduces_pathologies=True,
                estimated_energy_change=0.3,
                requires_human_review=False,
                test_recommendations=["Verify clean bootstrap in fresh env"],
            )

        # Shadow dependency repairs
        elif ptype == PathologyType.SHADOW_DEPENDENCY:
            return SynthesizedRepair(
                repair_id=f"shadow_dep_{id(pathology)}",
                source_type="pathology",
                source_id=str(ptype),
                target_file=location,
                target_module=self._file_to_module(location),
                repair_type="add",
                description="Declare hidden dependency explicitly",
                original_code=None,
                suggested_code="# TODO: Add explicit dependency declaration",
                auto_fixable=True,
                risk_level="medium",
                confidence=0.8,
                preserves_invariants=True,
                reduces_pathologies=True,
                estimated_energy_change=0.25,
                requires_human_review=False,
                test_recommendations=["Verify dependency resolution"],
            )

        # Default repair for unknown pathology types
        else:
            return SynthesizedRepair(
                repair_id=f"generic_{id(pathology)}",
                source_type="pathology",
                source_id=str(ptype),
                target_file=location,
                target_module=self._file_to_module(location),
                repair_type="review",
                description=f"Review and address: {pathology.message}",
                original_code=None,
                suggested_code=f"# TODO: {pathology.remediation}",
                auto_fixable=False,
                risk_level=severity,
                confidence=0.5,
                preserves_invariants=True,
                reduces_pathologies=True,
                estimated_energy_change=0.1,
                requires_human_review=True,
                test_recommendations=["Full regression test"],
            )

    def _synthesize_invariant_repair(
        self,
        invariant_result: Any,
    ) -> Optional[SynthesizedRepair]:
        """Synthesize a repair from an invariant violation."""
        inv_name = getattr(invariant_result, "invariant_name", "unknown")
        details = getattr(invariant_result, "details", {})

        return SynthesizedRepair(
            repair_id=f"inv_{inv_name}",
            source_type="invariant",
            source_id=inv_name,
            target_file=details.get("file", "unknown"),
            target_module=details.get("module", "unknown"),
            repair_type="modify",
            description=f"Restore invariant: {inv_name}",
            original_code=None,
            suggested_code=f"# TODO: Fix {inv_name} violation",
            auto_fixable=False,
            risk_level="high",
            confidence=0.6,
            preserves_invariants=True,
            reduces_pathologies=True,
            estimated_energy_change=0.2,
            requires_human_review=True,
            test_recommendations=[f"Verify {inv_name} post-repair"],
        )

    def _determine_repair_order(
        self,
        repairs: list[SynthesizedRepair],
    ) -> list[str]:
        """Determine optimal order for applying repairs."""
        # Sort by: auto_fixable first, then by risk (low to high), then by confidence
        sorted_repairs = sorted(
            repairs,
            key=lambda r: (
                not r.auto_fixable,  # Auto-fixable first
                ["low", "medium", "high", "critical"].index(r.risk_level),
                -r.confidence,  # Higher confidence first
            ),
        )

        return [r.repair_id for r in sorted_repairs]

    def _file_to_module(self, file_path: str) -> str:
        """Convert file path to module name."""
        try:
            path = Path(file_path)
            if path.suffix == ".py":
                parts = list(path.relative_to(self.repo_path).parts)
                if parts[-1] == "__init__.py":
                    parts = parts[:-1]
                else:
                    parts[-1] = path.stem
                return ".".join(parts)
            return file_path
        except Exception:
            return file_path


def get_repair_bridge(repo_path: str | Path = None) -> RepairSynthesisBridge:
    """Factory function to get repair synthesis bridge instance."""
    return RepairSynthesisBridge(repo_path or ".")
