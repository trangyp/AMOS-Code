#!/usr/bin/env python3
"""
AMOS 57-Component Brain ↔ Repo Doctor Ω∞ Integration Layer

Unifies the 57-component AMOS autonomous system with Repo Doctor's
repository invariant checking for comprehensive self-governing architecture.

Architecture:
- Repo Doctor Ω∞: Repository state modeling (19 invariants, density matrix, energy)
- AMOS 57-Component Brain: Meta-architecture governance (10 systems) +
                           Meta-ontological layer (12 components) +
                           21-tuple formal core

Integration Points:
1. Repository invariants feed into meta-architecture governance
2. State vector informs temporal hierarchy and identity manifold
3. Energy gradients drive ethical boundary decisions
4. Grand unified AMOS step processes repository transformations
5. Self-healing across both cognitive and repository layers
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class UnifiedSystemState:
    """Complete state combining Repo Doctor and AMOS 57-Component system."""

    # Repository layer (from Repo Doctor)
    repo_path: str
    invariant_status: Dict[str, Any] = field(default_factory=dict)
    state_vector: Dict[str, float] = field(default_factory=dict)
    energy: float = 0.0
    density_matrix: Optional[Any] = None

    # Cognitive layer (from AMOS 57-Component)
    meta_governance_state: Dict[str, Any] = field(default_factory=dict)
    meta_ontological_state: Dict[str, Any] = field(default_factory=dict)
    formal_core_state: Dict[str, Any] = field(default_factory=dict)

    # Unified metrics
    coherence_score: float = 0.0  # 0-1, overall system coherence
    governance_grade: str = "UNKNOWN"  # EXCELLENT/GOOD/ACCEPTABLE/CRITICAL
    last_updated: str = field(default_factory=lambda: str(time.time()))


@dataclass
class UnifiedDecision:
    """Decision synthesized from Repo Doctor invariants + AMOS governance."""

    decision_id: str
    timestamp: str

    # Inputs
    repo_concerns: List[str] = field(default_factory=list)
    governance_concerns: List[str] = field(default_factory=list)

    # Synthesis
    priority: str = "LOW"  # CRITICAL/HIGH/MEDIUM/LOW
    category: str = "UNKNOWN"  # REPOSITORY/ARCHITECTURAL/GOVERNANCE/INTEGRATED

    # Actions
    recommended_actions: list[dict[str, Any]] = field(default_factory=list)
    auto_executable: bool = False
    requires_human_review: bool = False

    # Meta-architecture compliance
    promise_checks: Dict[str, bool] = field(default_factory=dict)
    breach_risk: float = 0.0
    identity_continuity: bool = True


class AMOS57RepoDoctorIntegration:
    """
    Bridge between Repo Doctor Ω∞ and AMOS 57-Component Brain.

    Enables unified autonomous governance across repository state and
    cognitive architecture layers.
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo_doctor_available = False
        self.amos_57_available = False
        self.unified_state: Optional[UnifiedSystemState] = None

        # Initialize subsystems
        self._init_repo_doctor()
        self._init_amos_57()

    def _init_repo_doctor(self) -> bool:
        """Initialize Repo Doctor Ω∞ connection."""
        try:
            # Try importing repo_doctor components
            import sys

            repo_doctor_path = Path(__file__).parent / "repo_doctor"
            if repo_doctor_path.exists():
                sys.path.insert(0, str(repo_doctor_path.parent))

            from repo_doctor.invariants import InvariantEngine
            from repo_doctor.state_vector import StateVector

            self.invariant_engine = InvariantEngine
            self.state_vector_class = StateVector
            self.repo_doctor_available = True
            return True

        except ImportError as e:
            print(f"[AMOS57Integration] Repo Doctor not available: {e}")
            return False

    def _init_amos_57(self) -> bool:
        """Initialize AMOS 57-Component Brain."""
        try:
            from amos_formal_core import AMOSFormalSystem
            from amos_meta_architecture import MetaGovernance
            from amos_meta_ontological import AMOSMetaOntological

            self.meta_governance = MetaGovernance()
            self.meta_ontological = AMOSMetaOntological()
            self.formal_core = AMOSFormalSystem()
            self.amos_57_available = True
            return True

        except ImportError as e:
            print(f"[AMOS57Integration] AMOS 57-Component not available: {e}")
            return False

    def compute_unified_state(self) -> UnifiedSystemState:
        """
        Compute unified state combining Repo Doctor and AMOS 57-Component.

        This is the core integration function that merges repository
        invariants with cognitive governance state.
        """
        if not self.repo_doctor_available:
            return self._compute_amos_only_state()

        # Step 1: Get Repo Doctor state
        repo_state = self._get_repo_doctor_state()

        # Step 2: Transform to AMOS 57-Component inputs
        amos_inputs = self._transform_to_amos_inputs(repo_state)

        # Step 3: Run AMOS governance
        governance_state = self._run_amos_governance(amos_inputs)

        # Step 4: Compute coherence score
        coherence = self._compute_coherence(repo_state, governance_state)

        # Step 5: Determine governance grade
        grade = self._determine_governance_grade(repo_state["energy"], governance_state, coherence)

        self.unified_state = UnifiedSystemState(
            repo_path=str(self.repo_path),
            invariant_status=repo_state["invariants"],
            state_vector=repo_state["state_vector"],
            energy=repo_state["energy"],
            meta_governance_state=governance_state["meta_architecture"],
            meta_ontological_state=governance_state["meta_ontological"],
            formal_core_state=governance_state["formal_core"],
            coherence_score=coherence,
            governance_grade=grade,
        )

        return self.unified_state

    def _get_repo_doctor_state(self) -> Dict[str, Any]:
        """Get current state from Repo Doctor."""
        if not self.repo_doctor_available:
            return {"invariants": {}, "state_vector": {}, "energy": 0.0}
        # ...existing code...

        try:
            engine = self.invariant_engine(str(self.repo_path))
            results = engine.run_all()

            # Build state vector from invariants
            state_vector = {}
            invariants = {}

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

            for r in results:
                amp = 1.0 if r.passed else 0.0
                if r.name in dim_map:
                    state_vector[dim_map[r.name]] = amp
                    invariants[r.name] = {"passed": r.passed, "details": r.details}

            # Calculate energy
            weights = [100, 90, 70, 95, 90, 90, 80, 70, 65, 35, 100, 55]
            energy = sum(
                w * (1 - a) ** 2
                for w, a in zip(weights, state_vector.values())
                if isinstance(a, (int, float))
            )

            return {
                "invariants": invariants,
                "state_vector": state_vector,
                "energy": energy,
            }

        except Exception as e:
            print(f"[AMOS57Integration] Error getting Repo Doctor state: {e}")
            return {"invariants": {}, "state_vector": {}, "energy": 0.0}

    def _transform_to_amos_inputs(self, repo_state: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Repo Doctor state to AMOS 57-Component inputs."""
        return {
            "repository_state": repo_state["state_vector"],
            "energy_gradient": repo_state["energy"],
            "failing_invariants": [
                k for k, v in repo_state["invariants"].items() if not v.get("passed", True)
            ],
            "system_type": "repository",
            "coherence_requirements": {"high_availability": True},
        }

    def _run_amos_governance(self, inputs: Dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Run AMOS 57-Component governance on transformed inputs."""
        if not self.amos_57_available:
            return {
                "meta_architecture": {},
                "meta_ontological": {},
                "formal_core": {},
            }

        governance_results = {}

        # Run meta-architecture validation
        try:
            validation = self.meta_governance.validate_full_system()
            governance_results["meta_architecture"] = {
                "systems_validated": sum(validation.values()),
                "total_systems": len(validation),
                "status": "HEALTHY" if all(validation.values()) else "DEGRADED",
            }
        except Exception as e:
            governance_results["meta_architecture"] = {"error": str(e)}

        # Run meta-ontological check
        try:
            energy_budget = self.meta_ontological.energy_budget
            temporal = self.meta_ontological.temporal_hierarchy
            governance_results["meta_ontological"] = {
                "energy_feasible": energy_budget.is_feasible(1.0),
                "current_scale": str(temporal.current_scale),
                "identity_preserved": (
                    self.meta_ontological.identity_manifold.check_persistence(0.9)
                ),
            }
        except Exception as e:
            governance_results["meta_ontological"] = {"error": str(e)}

        # Check formal core
        try:
            governance_results["formal_core"] = {
                "intent_valid": self.formal_core.intent is not None,
                "syntax_valid": self.formal_core.syntax is not None,
                "dynamics_valid": self.formal_core.dynamics is not None,
            }
        except Exception as e:
            governance_results["formal_core"] = {"error": str(e)}

        return governance_results

    def _compute_coherence(
        self, repo_state: Dict[str, Any], governance_state: Dict[str, Any]
    ) -> float:
        """Compute coherence score between repository and governance states."""
        # Base coherence from repository
        repo_coherence = 1.0 - (repo_state["energy"] / 1000.0)
        repo_coherence = max(0.0, min(1.0, repo_coherence))

        # Governance coherence
        gov_checks = []
        if "meta_architecture" in governance_state:
            arch = governance_state["meta_architecture"]
            if "status" in arch:
                gov_checks.append(1.0 if arch["status"] == "HEALTHY" else 0.5)

        if "meta_ontological" in governance_state:
            ont = governance_state["meta_ontological"]
            if "identity_preserved" in ont:
                gov_checks.append(1.0 if ont["identity_preserved"] else 0.0)

        gov_coherence = sum(gov_checks) / len(gov_checks) if gov_checks else 0.5

        # Combined coherence (weighted average)
        return 0.6 * repo_coherence + 0.4 * gov_coherence

    def _determine_governance_grade(
        self, energy: float, governance_state: Dict[str, Any], coherence: float
    ) -> str:
        """Determine overall governance grade."""
        # Critical conditions
        if energy > 50:
            return "CRITICAL"
        if coherence < 0.3:
            return "CRITICAL"

        # Check meta-architecture status
        arch_status = governance_state.get("meta_architecture", {}).get("status", "")
        if arch_status == "DEGRADED":
            return "HIGH_RISK"

        # Good conditions
        if energy < 10 and coherence > 0.8 and arch_status == "HEALTHY":
            return "EXCELLENT"
        if energy < 20 and coherence > 0.7:
            return "GOOD"
        if energy < 30:
            return "ACCEPTABLE"

        return "DEGRADED"

    def _compute_amos_only_state(self) -> UnifiedSystemState:
        """Compute state using only AMOS 57-Component (no Repo Doctor)."""
        governance_state = self._run_amos_governance({})

        return UnifiedSystemState(
            repo_path=str(self.repo_path),
            invariant_status={},
            state_vector={},
            energy=0.0,
            meta_governance_state=governance_state["meta_architecture"],
            meta_ontological_state=governance_state["meta_ontological"],
            formal_core_state=governance_state["formal_core"],
            coherence_score=0.5,
            governance_grade="AMOS_ONLY",
        )

    def make_unified_decision(self, context: dict[str, Any] = None) -> UnifiedDecision:
        """
        Make decision using both Repo Doctor invariants and AMOS governance.

        This is the key function for autonomous operation - it combines
        repository health with architectural governance to make decisions.
        """
        if not self.unified_state:
            self.compute_unified_state()

        state = self.unified_state
        assert state is not None

        # Analyze repository concerns
        repo_concerns = []
        if state.energy > 20:
            repo_concerns.append(f"High repository energy: {state.energy:.1f}")
        failing = [k for k, v in state.invariant_status.items() if not v.get("passed", True)]
        if failing:
            repo_concerns.append(f"Failing invariants: {failing}")

        # Analyze governance concerns
        gov_concerns = []
        if state.governance_grade in ["CRITICAL", "HIGH_RISK", "DEGRADED"]:
            gov_concerns.append(f"Governance grade: {state.governance_grade}")
        if state.coherence_score < 0.5:
            gov_concerns.append(f"Low coherence: {state.coherence_score:.2f}")

        # Determine priority
        if state.governance_grade == "CRITICAL" or state.energy > 50:
            priority = "CRITICAL"
        elif state.governance_grade in ["HIGH_RISK", "DEGRADED"] or state.energy > 30:
            priority = "HIGH"
        elif repo_concerns or gov_concerns:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        # Determine category
        if repo_concerns and gov_concerns:
            category = "INTEGRATED"
        elif repo_concerns:
            category = "REPOSITORY"
        elif gov_concerns:
            category = "GOVERNANCE"
        else:
            category = "MAINTENANCE"

        # Generate recommended actions
        actions = self._generate_actions(state, repo_concerns, gov_concerns, priority)

        # Check if auto-executable
        auto_exec = priority in ["LOW", "MEDIUM"] and not repo_concerns
        needs_review = priority in ["CRITICAL", "HIGH"]

        return UnifiedDecision(
            decision_id=f"unified_{int(time.time())}",
            timestamp=str(time.time()),
            repo_concerns=repo_concerns,
            governance_concerns=gov_concerns,
            priority=priority,
            category=category,
            recommended_actions=actions,
            auto_executable=auto_exec,
            requires_human_review=needs_review,
            promise_checks={"identity_preserved": state.governance_grade != "CRITICAL"},
            breach_risk=state.energy / 100.0,
            identity_continuity=state.governance_grade not in ["CRITICAL", "HIGH_RISK"],
        )

    def _generate_actions(
        self,
        state: UnifiedSystemState,
        repo_concerns: List[str],
        gov_concerns: List[str],
        priority: str,
    ) -> list[dict[str, Any]]:
        """Generate recommended actions based on unified state."""
        actions = []

        # Repository actions
        if state.energy > 20:
            actions.append(
                {
                    "type": "REPOSITORY",
                    "action": "run_invariant_checks",
                    "priority": "HIGH",
                    "details": "Repository energy above threshold",
                }
            )

        failing = [k for k, v in state.invariant_status.items() if not v.get("passed", True)]
        if failing:
            actions.append(
                {
                    "type": "REPOSITORY",
                    "action": "repair_invariants",
                    "priority": "HIGH",
                    "details": f"Fix failing invariants: {failing[:3]}",
                }
            )

        # Governance actions
        if state.governance_grade == "CRITICAL":
            actions.append(
                {
                    "type": "GOVERNANCE",
                    "action": "emergency_intervention",
                    "priority": "CRITICAL",
                    "details": "Activate emergency governance protocols",
                }
            )
        elif state.governance_grade in ["HIGH_RISK", "DEGRADED"]:
            actions.append(
                {
                    "type": "GOVERNANCE",
                    "action": "strengthen_promises",
                    "priority": "HIGH",
                    "details": "Review and strengthen architectural promises",
                }  # noqa: E501
            )

        if state.coherence_score < 0.5:
            actions.append(
                {
                    "type": "INTEGRATED",
                    "action": "restore_coherence",
                    "priority": "HIGH",
                    "details": "Restore system coherence via unified step",
                }  # noqa: E501
            )

        # Meta-ontological actions
        if self.amos_57_available:
            try:
                if not self.meta_ontological.energy_budget.is_feasible(1.0):
                    actions.append(
                        {
                            "type": "META_ONTOLOGICAL",
                            "action": "optimize_energy",
                            "priority": "MEDIUM",
                            "details": "Optimize energy consumption",
                        }
                    )
            except Exception:
                pass

        return actions


def run_unified_analysis(repo_path: str) -> Dict[str, Any]:
    """
    Run complete unified analysis of repository using both systems.

    This is the main entry point for integrated analysis.
    """
    integration = AMOS57RepoDoctorIntegration(repo_path)

    # Compute unified state
    state = integration.compute_unified_state()

    # Make unified decision
    decision = integration.make_unified_decision()

    return {
        "unified_state": {
            "repo_path": state.repo_path,
            "energy": state.energy,
            "coherence_score": state.coherence_score,
            "governance_grade": state.governance_grade,
            "invariant_count": len(state.invariant_status),
        },
        "decision": {
            "decision_id": decision.decision_id,
            "priority": decision.priority,
            "category": decision.category,
            "auto_executable": decision.auto_executable,
            "requires_human_review": decision.requires_human_review,
            "action_count": len(decision.recommended_actions),
        },
        "repo_concerns": decision.repo_concerns,
        "governance_concerns": decision.governance_concerns,
        "actions": decision.recommended_actions,
        "subsystems_available": {
            "repo_doctor": integration.repo_doctor_available,
            "amos_57": integration.amos_57_available,
        },
    }


if __name__ == "__main__":
    # Test the integration
    import sys

    test_path = sys.argv[1] if len(sys.argv) > 1 else "."
    result = run_unified_analysis(test_path)

    print("\n" + "=" * 70)
    print("AMOS 57-Component ↔ Repo Doctor Ω∞ Integration")
    print("=" * 70)
    print(f"\nRepository: {result['unified_state']['repo_path']}")
    print(f"Energy: {result['unified_state']['energy']:.2f}")
    print(f"Coherence: {result['unified_state']['coherence_score']:.2f}")
    print(f"Governance Grade: {result['unified_state']['governance_grade']}")
    print(f"\nDecision Priority: {result['decision']['priority']}")
    print(f"Category: {result['decision']['category']}")
    print(f"Auto-Executable: {result['decision']['auto_executable']}")
    print(f"\nRecommended Actions: {result['decision']['action_count']}")
    for action in result["actions"]:
        print(f"  - [{action['priority']}] {action['type']}: " f"{action['action']}")
    print("\n" + "=" * 70)
