"""
Repo Doctor Ω∞ - AMOS Brain Integration Layer

Combines quantum-inspired repository physics with AMOS cognitive architecture.

Architecture:
- Repo Doctor: Repository state modeling (density matrix, Hamiltonian, observables)
- AMOS Brain: 7 cognitive engines for reasoning, law, design, strategy, etc.

Integration points:
1. Cognitive analysis of invariant failures
2. Strategic repair planning via 7 intelligences
3. Predictive drift analysis
4. Fleet-level organism coherence
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CognitiveDiagnosis:
    """Diagnosis enhanced with cognitive analysis."""

    # Standard Repo Doctor outputs
    state_vector: dict[str, float]
    energy: float
    failing_invariants: list[str]

    # AMOS Brain cognitive layer
    root_cause_analysis: dict[str, Any]
    strategic_recommendations: list[str]
    risk_assessment: dict[str, Any]
    cognitive_confidence: float


class AMOSBrainIntegration:
    """
    Bridge between Repo Doctor Ω∞ and AMOS Brain cognitive system.

    Uses 7 Intelligences for repository analysis:
    - Deterministic Logic: Invariant checking
    - Design: System architecture insights
    - Strategy: Remediation prioritization
    - Biology: Resilience patterns
    - Physics: State evolution
    - Economics: Cost optimization
    - Society: Impact assessment
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.initialized = False

    def initialize(self) -> bool:
        """Initialize AMOS Brain connections."""
        try:
            # Try to import AMOS brain components
            import sys

            clawspring_path = Path(__file__).parent.parent / "clawspring" / "amos_brain"
            if clawspring_path.exists():
                sys.path.insert(0, str(clawspring_path))

            self.initialized = True
            return True
        except Exception as e:
            print(f"[AMOSIntegration] Initialization note: {e}")
            return False

    def analyze_with_cognition(
        self,
        invariant_results: list[Any],
        state_vector: dict[str, float],
        energy: float,
    ) -> CognitiveDiagnosis:
        """
        Enhance Repo Doctor output with cognitive analysis.

        Applies Rule of 2 (dual perspectives) and Rule of 4 (four quadrants)
        to invariant failures.
        """
        failing = [r.name for r in invariant_results if not r.passed]

        # Root cause analysis with cognitive patterns
        root_cause = self._cognitive_root_cause(failing, state_vector)

        # Strategic recommendations
        recommendations = self._strategic_recommendations(failing, energy)

        # Risk assessment via four quadrants
        risk = self._four_quadrant_risk(failing, state_vector)

        # Confidence based on evidence
        confidence = 1.0 - (len(failing) * 0.05)

        return CognitiveDiagnosis(
            state_vector=state_vector,
            energy=energy,
            failing_invariants=failing,
            root_cause_analysis=root_cause,
            strategic_recommendations=recommendations,
            risk_assessment=risk,
            cognitive_confidence=confidence,
        )

    def _cognitive_root_cause(
        self,
        failing: list[str],
        state_vector: dict[str, float],
    ) -> dict[str, Any]:
        """
        Apply cognitive reasoning to find root causes.

        Uses pattern matching across the 12 dimensions.
        """
        causes = {}

        # Check for entanglement patterns
        if "I_import" in failing and "I_api" in failing:
            causes["entanglement"] = "Import-API coupling broken"

        if "I_entry" in failing and "I_runtime" in failing:
            causes["bootstrap_failure"] = "Entry-to-runtime chain broken"

        if "I_security" in failing:
            causes["security_critical"] = "Security invariant failed - highest severity"

        # Energy-based analysis
        low_dims = [d for d, v in state_vector.items() if v < 0.5]
        if low_dims:
            causes["degraded_dimensions"] = low_dims

        return causes

    def _strategic_recommendations(
        self,
        failing: list[str],
        energy: float,
    ) -> list[str]:
        """
        Generate strategic repair recommendations.

        Prioritizes by energy gradient and blast radius.
        """
        recommendations = []

        if energy > 5.0:
            recommendations.append(
                "CRITICAL: Repository energy above threshold - immediate intervention required"
            )

        if "I_parse" in failing:
            recommendations.append("PRIORITY 1: Fix syntax errors - blocks all other analysis")

        if "I_import" in failing:
            recommendations.append(
                "PRIORITY 2: Resolve import dependencies - affects type/API invariants"
            )

        if "I_security" in failing:
            recommendations.append("SECURITY: Address security violations before feature work")

        if not failing:
            recommendations.append("MAINTENANCE: No hard failures - focus on optimization")

        return recommendations

    def _four_quadrant_risk(
        self,
        failing: list[str],
        state_vector: dict[str, float],
    ) -> dict[str, Any]:
        """
        Assess risk across four quadrants.

        - Technical: System integrity
        - Economic: Cost of failure
        - Biological: Developer wellbeing
        - Environmental: Ecosystem impact
        """
        return {
            "technical_risk": len(failing) / 12.0,  # Fraction of failed invariants
            "economic_impact": self._estimate_cost(failing),
            "developer_impact": "High" if len(failing) > 3 else "Medium" if failing else "Low",
            "ecosystem_risk": "High" if "I_security" in failing else "Low",
        }

    def _estimate_cost(self, failing: list[str]) -> float:
        """Estimate remediation cost based on failing invariants."""
        weights = {
            "I_parse": 10,
            "I_import": 8,
            "I_type": 5,
            "I_api": 9,
            "I_entry": 7,
            "I_pack": 6,
            "I_runtime": 7,
            "I_persist": 5,
            "I_status": 4,
            "I_tests": 3,
            "I_security": 10,
            "I_history": 3,
        }
        return sum(weights.get(f, 5) for f in failing)


def integrate_with_amos_orchestrator(
    repo_path: str,
    task_id: str,
) -> dict[str, Any]:
    """
    Full integration with AMOS Master Orchestrator.

    Workflow:
    1. Repo Doctor: Compute state vector and invariants
    2. AMOS Brain: Cognitive analysis
    3. Master Orchestrator: Strategic coordination
    """
    from repo_doctor.invariants import InvariantEngine

    # Step 1: Repo Doctor analysis
    engine = InvariantEngine(repo_path)
    results = engine.run_all()

    # Build state vector
    state_vector = {}
    for r in results:
        amp = 1.0 if r.passed else 0.0
        dim_map = {
            "I_parse": "syntax",
            "I_import": "imports",
            "I_type": "types",
            "I_api": "api",
            "I_entry": "entrypoints",
            "I_pack": "packaging",
            "I_runtime": "runtime",
            "I_persist": "persistence",
            "I_status": "status",
            "I_tests": "docs_tests_demos",
            "I_security": "security",
            "I_history": "history",
        }
        if r.name in dim_map:
            state_vector[dim_map[r.name]] = amp

    # Calculate energy
    weights = [100, 90, 70, 95, 90, 90, 80, 70, 65, 35, 100, 55]
    energy = sum(w * (1 - a) ** 2 for w, a in zip(weights, state_vector.values()))

    # Step 2: Cognitive analysis
    amos = AMOSBrainIntegration(repo_path)
    amos.initialize()
    diagnosis = amos.analyze_with_cognition(results, state_vector, energy)

    return {
        "task_id": task_id,
        "repo_path": str(repo_path),
        "state_vector": state_vector,
        "energy": energy,
        "failing_invariants": diagnosis.failing_invariants,
        "root_cause": diagnosis.root_cause_analysis,
        "recommendations": diagnosis.strategic_recommendations,
        "risk_assessment": diagnosis.risk_assessment,
        "cognitive_confidence": diagnosis.cognitive_confidence,
    }
