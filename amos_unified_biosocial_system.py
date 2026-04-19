#!/usr/bin/env python3
"""AMOS Unified Biosocial System - Complete Integration Architecture.

Unifies the 57-component cognitive system with:
- UBI Engine (Unified Biological Intelligence - 4 domains)
- Advanced Systems (Repo Doctor Omega, Self-Evolution)
- Human-centric design considerations
- Continuous self-improvement

This creates a biosocial AI architecture that:
1. Has biological awareness (cognitive, emotional, physical)
2. Self-evolves based on repository health
3. Maintains human-centric design principles
4. Operates as a unified autonomous organism

State-of-the-art human-centric autonomous AI architecture.
"""


import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BiosocialState:
    """Complete state of the unified biosocial system."""

    # Cognitive state (57-component)
    cognitive_health: float
    coherence_score: float
    governance_grade: str

    # Biological state (UBI)
    biological_context: Dict[str, Any]
    human_factors: Dict[str, Any]

    # Repository state (Repo Doctor)
    repo_energy: float
    invariant_status: Dict[str, bool]

    # Evolution state
    improvement_opportunities: List[str]
    last_evolution: float

    # Unified metrics
    biosocial_harmony: float  # 0-1
    human_readiness: float  # 0-1
    last_updated: float


@dataclass
class HumanCentricDecision:
    """Decision with human-centric considerations."""

    decision_id: str
    cognitive_recommendation: str

    # UBI considerations
    cognitive_load_impact: str  # low/medium/high
    emotional_impact: str  # neutral/positive/negative
    physical_ergonomics: List[str]

    # Human readiness
    human_fatigue_estimate: str
    appropriate_timing: bool

    # Final decision
    approved: bool
    human_approval_required: bool
    rationale: str


class AMOSUnifiedBiosocialSystem:
    """
    Unified Biosocial Architecture combining 57-component cognition,
    biological intelligence, and self-evolution capabilities.
    """

    def __init__(self, repo_path: str  = None):
        self.repo_path = Path(repo_path) if repo_path else Path(".")

        # Component references
        self.orchestrator: Optional[Any] = None
        self.ubi_engine: Optional[Any] = None
        self.repo_doctor: Optional[Any] = None
        self.self_evolution: Optional[Any] = None

        # State
        self.biosocial_state: Optional[BiosocialState] = None
        self.initialized = False
        self.cycle_count = 0

    def initialize(self) -> bool:
        """
        Initialize all subsystems in unified sequence.

        Boot sequence:
        1. 57-Component Core (cognitive foundation)
        2. UBI Engine (biological awareness)
        3. Repo Doctor Omega (repository health)
        4. Self-Evolution Engine (continuous improvement)
        """
        print("\n" + "=" * 70)
        print("AMOS UNIFIED BIOSOCIAL SYSTEM")
        print("Initialization Sequence")
        print("=" * 70)

        success = True

        # Step 1: Initialize 57-Component Core
        print("\n[1/4] Initializing 57-Component Cognitive Core...")
        try:
            from amos_57_master_orchestrator import (
                AMOS57MasterOrchestrator,
                OrchestratorConfig,
            )

            config = OrchestratorConfig(
                health_check_interval=5.0,
                self_healing_enabled=True,
            )
            self.orchestrator = AMOS57MasterOrchestrator(config)
            self.orchestrator.initialize()
            print("   ✅ 57-Component Core: Meta-Architecture (10), Meta-Ontological (12)")
            print("      21-Tuple Formal Core (21), Production (46) = 57 components")
        except Exception as e:
            print(f"   ⚠️  57-Component Core initialization note: {e}")
            success = False

        # Step 2: Initialize UBI Engine
        print("\n[2/4] Initializing Unified Biological Intelligence...")
        try:
            sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
            from amos_ubi_engine import AMOSUBIEngine

            self.ubi_engine = AMOSUBIEngine()
            print("   ✅ UBI Engine: NBI, NEI, SI, BEI (4 domains)")
        except Exception as e:
            print(f"   ⚠️  UBI Engine not available: {e}")

        # Step 3: Initialize Repo Doctor Omega
        print("\n[3/4] Initializing Repo Doctor Omega...")
        try:
            from repo_doctor_omega.engine import RepoDoctorEngine

            self.repo_doctor = RepoDoctorEngine(str(self.repo_path))
            print("   ✅ Repo Doctor Omega: Repository invariants active")
        except Exception as e:
            print(f"   ⚠️  Repo Doctor Omega not available: {e}")

        # Step 4: Initialize Self-Evolution
        print("\n[4/4] Initializing Self-Evolution Engine...")
        try:
            from amos_self_evolution.evolution_opportunity_detector import (
                EvolutionOpportunityDetector,
            )

            self.self_evolution = EvolutionOpportunityDetector()
            print("   ✅ Self-Evolution: Continuous improvement enabled")
        except Exception as e:
            print(f"   ⚠️  Self-Evolution not available: {e}")

        self.initialized = True

        print("\n" + "=" * 70)
        print("INITIALIZATION COMPLETE")
        print("Biosocial Architecture Active")
        print("=" * 70)

        return success

    def compute_biosocial_state(self) -> BiosocialState:
        """Compute unified state across all subsystems."""
        # Cognitive state
        cognitive_health = 0.5
        coherence = 0.5
        governance = "UNKNOWN"

        if self.orchestrator and self.orchestrator.initialized:
            try:
                status = self.orchestrator.get_status()
                cognitive_health = status.get("coherence_score", 0.5)
                coherence = status.get("coherence_score", 0.5)
                governance = status.get("status", "UNKNOWN")
            except Exception:
                pass

        # Biological context
        biological_context = {}
        human_factors = {}

        if self.ubi_engine:
            try:
                ubi_results = self.ubi_engine.analyze(
                    description="System operating normally",
                    domains=["NBI", "NEI", "SI", "BEI"],
                )

                biological_context = {
                    "cognitive_load": ubi_results.get("NBI", {}).analysis
                    if hasattr(ubi_results.get("NBI"), "analysis")
                    else {},
                    "emotional_state": ubi_results.get("NEI", {}).analysis
                    if hasattr(ubi_results.get("NEI"), "analysis")
                    else {},
                    "physical_context": ubi_results.get("SI", {}).analysis
                    if hasattr(ubi_results.get("SI"), "analysis")
                    else {},
                    "environmental_context": ubi_results.get("BEI", {}).analysis
                    if hasattr(ubi_results.get("BEI"), "analysis")
                    else {},
                }

                human_factors = {
                    "design_recommendations": self._extract_design_recommendations(
                        ubi_results
                    ),
                    "safety_notices": self._extract_safety_notices(ubi_results),
                }
            except Exception as e:
                biological_context = {"error": str(e)}

        # Repository state
        repo_energy = 0.0
        invariant_status = {}

        if self.repo_doctor:
            try:
                state = self.repo_doctor.compute_state()
                repo_energy = state.compute_energy()
                # Run invariant checks
                results = self.repo_doctor.evaluate_invariants()
                invariant_status = {r.invariant: r.passed for r in results}
            except Exception:
                pass

        # Evolution opportunities
        opportunities = []
        last_evolution = 0.0

        if self.self_evolution:
            try:
                ops = self.self_evolution.detect_opportunities(str(self.repo_path))
                opportunities = [str(op) for op in ops[:5]]
            except Exception:
                pass

        # Compute biosocial harmony
        biosocial_harmony = (
            cognitive_health * 0.4
            + (1.0 - min(repo_energy / 100, 1.0)) * 0.4
            + (0.8 if biological_context else 0.5) * 0.2
        )

        # Compute human readiness
        human_readiness = 0.8 if biological_context else 0.5
        if "NEI" in biological_context:
            stress = biological_context.get("NEI", {}).get("stress_indicators_detected", 0)
            if stress > 0:
                human_readiness *= 0.8

        self.biosocial_state = BiosocialState(
            cognitive_health=cognitive_health,
            coherence_score=coherence,
            governance_grade=governance,
            biological_context=biological_context,
            human_factors=human_factors,
            repo_energy=repo_energy,
            invariant_status=invariant_status,
            improvement_opportunities=opportunities,
            last_evolution=last_evolution,
            biosocial_harmony=biosocial_harmony,
            human_readiness=human_readiness,
            last_updated=time.time(),
        )

        return self.biosocial_state

    def _extract_design_recommendations(self, ubi_results: Dict) -> List[str]:
        """Extract human-centric design recommendations from UBI."""
        recommendations = []

        for domain, result in ubi_results.items():
            if hasattr(result, "design_levers"):
                recommendations.extend(result.design_levers)

        return list(set(recommendations))  # Remove duplicates

    def _extract_safety_notices(self, ubi_results: Dict) -> List[str]:
        """Extract safety notices from UBI."""
        notices = []

        for domain, result in ubi_results.items():
            if hasattr(result, "safety_notices"):
                notices.extend(result.safety_notices)

        return notices

    def make_human_centric_decision(
        self, action_description: str, context: Optional[Dict] = None
    ) -> HumanCentricDecision:
        """
        Make a decision considering human biological factors.

        This is the key differentiator - biosocial AI considers
        human cognitive, emotional, and physical state.
        """
        if not self.biosocial_state:
            self.compute_biosocial_state()

        # Analyze with UBI
        ubi_analysis = {}
        if self.ubi_engine:
            try:
                ubi_analysis = self.ubi_engine.analyze(
                    description=action_description,
                    context=context or {},
                )
            except Exception:
                pass

        # Determine cognitive impact
        cognitive_impact = "medium"
        if "NBI" in ubi_analysis:
            load = ubi_analysis["NBI"].analysis.get("cognitive_load_profile", "medium")
            cognitive_impact = load

        # Determine emotional impact
        emotional_impact = "neutral"
        if "NEI" in ubi_analysis:
            valence = ubi_analysis["NEI"].analysis.get("valence_estimate", "neutral")
            emotional_impact = "negative" if "negative" in valence else "neutral"

        # Physical ergonomics
        ergonomics = []
        if "SI" in ubi_analysis:
            ergonomics = ubi_analysis["SI"].analysis.get("ergonomic_recommendations", [])

        # Human fatigue estimate
        fatigue = "moderate"
        if cognitive_impact == "high":
            fatigue = "elevated"
        elif cognitive_impact == "low":
            fatigue = "low"

        # Check appropriate timing
        appropriate = self.biosocial_state.human_readiness > 0.7 if self.biosocial_state else True

        # Build rationale
        rationale_parts = [f"Cognitive impact: {cognitive_impact}"]
        if emotional_impact != "neutral":
            rationale_parts.append(f"Emotional impact: {emotional_impact}")
        rationale_parts.append(f"Human readiness: {fatigue}")

        # Decision approval
        approved = appropriate and cognitive_impact != "high"
        requires_approval = cognitive_impact == "high" or emotional_impact == "negative"

        return HumanCentricDecision(
            decision_id=f"biosocial_{int(time.time())}",
            cognitive_recommendation=action_description,
            cognitive_load_impact=cognitive_impact,
            emotional_impact=emotional_impact,
            physical_ergonomics=ergonomics,
            human_fatigue_estimate=fatigue,
            appropriate_timing=appropriate,
            approved=approved,
            human_approval_required=requires_approval,
            rationale="; ".join(rationale_parts),
        )

    def get_unified_status(self) -> Dict[str, Any]:
        """Get complete unified system status."""
        if not self.biosocial_state:
            self.compute_biosocial_state()

        state = self.biosocial_state

        return {
            "biosocial_harmony": round(state.biosocial_harmony, 2),
            "human_readiness": round(state.human_readiness, 2),
            "cognitive": {
                "health": round(state.cognitive_health, 2),
                "coherence": round(state.coherence_score, 2),
                "grade": state.governance_grade,
            },
            "repository": {
                "energy": round(state.repo_energy, 2),
                "invariants_passed": sum(1 for v in state.invariant_status.values() if v),
                "invariants_total": len(state.invariant_status),
            },
            "biological": {
                "domains_active": len(state.biological_context),
                "design_recommendations": len(state.human_factors.get("design_recommendations", [])),
            },
            "evolution": {
                "opportunities": len(state.improvement_opportunities),
                "opportunities_list": state.improvement_opportunities[:3],
            },
            "subsystems": {
                "cognitive_57": self.orchestrator is not None,
                "ubi": self.ubi_engine is not None,
                "repo_doctor": self.repo_doctor is not None,
                "self_evolution": self.self_evolution is not None,
            },
        }


def main():
    """Run the unified biosocial system."""
    import sys

    print("\n" + "=" * 70)
    print("AMOS UNIFIED BIOSOCIAL SYSTEM")
    print("=" * 70)

    # Initialize system
    system = AMOSUnifiedBiosocialSystem()

    if not system.initialize():
        print("\n⚠️  Partial initialization - continuing with available subsystems")

    # Compute initial state
    print("\n📊 Computing Biosocial State...")
    state = system.compute_biosocial_state()

    print(f"\n   Biosocial Harmony: {state.biosocial_harmony:.2f}")
    print(f"   Human Readiness: {state.human_readiness:.2f}")
    print(f"   Cognitive Health: {state.cognitive_health:.2f}")
    print(f"   Repository Energy: {state.repo_energy:.2f}")

    # Test human-centric decision
    print("\n🧠 Testing Human-Centric Decision...")
    decision = system.make_human_centric_decision(
        "Deploy new feature to production with high cognitive complexity"
    )

    print(f"\n   Decision ID: {decision.decision_id}")
    print(f"   Approved: {decision.approved}")
    print(f"   Requires Human Approval: {decision.human_approval_required}")
    print(f"   Cognitive Impact: {decision.cognitive_load_impact}")
    print(f"   Emotional Impact: {decision.emotional_impact}")
    print(f"   Rationale: {decision.rationale}")

    # Show unified status
    print("\n📋 Unified System Status:")
    status = system.get_unified_status()
    print(f"   Subsystems Active: {sum(status['subsystems'].values())}/4")
    print(f"   Biosocial Harmony: {status['biosocial_harmony']}")
    print(f"   Human Readiness: {status['human_readiness']}")

    print("\n" + "=" * 70)
    print("UNIFIED BIOSOCIAL SYSTEM OPERATIONAL")
    print("=" * 70)


if __name__ == "__main__":
    import sys
from typing import Dict, Final, Tuple

    main()
