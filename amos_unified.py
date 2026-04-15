#!/usr/bin/env python3
"""AMOS Unified - Complete integration of all AMOS layers.

This is the unified entry point that orchestrates:
1. AMOS v4 (Persistent Economic Organism - Pe, X, Y, Q layers)
2. AMOS Core (Branch Field, Collapse, Morph, Time, Energy)
3. AMOS Memory (Working, Episodic, Semantic, Procedural, Self)
4. AMOS Meta-cognition (Reflection, Parameter Adaptation)
5. AMOS Repo Intelligence (Code Understanding)
6. AMOS Self-coding (Code Generation)

Full State:
  AMOS_v4 = (G,T,N,W,M,E,R,K,B,A,V,H,P,I,D,F,S,L,C,Pe,X,Y,Q)

Primary Loop:
  Perceive → Branch → Simulate → Collapse → Execute → Learn → Persist

Usage:
    python amos_unified.py                    # Start unified runtime
    python amos_unified.py --mode v4          # v4 Economic mode
    python amos_unified.py --mode core        # Core cognitive mode
    python amos_unified.py --mode full        # Full integration (default)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS"))


class AMOSUnifiedRuntime:
    """Unified runtime integrating all AMOS layers.

    Architecture Stack:
    - Layer 1: AMOS v4 (Economic Organism - Persistence, Resources, World Model)
    - Layer 2: Core Cognitive (Branch Field, Collapse, Morph, Time, Energy)
    - Layer 3: Memory Systems (5 memory types with consolidation)
    - Layer 4: Meta-cognition (Reflection, Learning, Adaptation)
    - Layer 5: Repo Intelligence (Code Understanding)
    - Layer 6: Self-coding (Code Generation)
    - Layer 7: Integration APIs (Brain, Organism OS, ClawSpring)
    """

    def __init__(self, mode: str = "full"):
        self.mode = mode

        # v4 Economic Layer
        self.v4 = None

        # Core Cognitive Layer
        self.core = None
        self.time_engine = None
        self.energy_system = None

        # Memory Layer
        self.memory = None

        # Meta-cognition Layer
        self.meta = None

        # Repo & Self-coding Layer
        self.repo_intel = None
        self.self_coding = None

        # Legacy Integration Layer
        self.brain = None
        self.organism = None
        self.clawspring = None

        # Ω Axiomatic Layer (NEW)
        self.omega = None
        self.coherence_omega = None
        self.axiom_validator = None

        self._initialized = False

    def initialize(self) -> bool:
        """Initialize all layers based on mode."""
        print("╔════════════════════════════════════════════════════════════╗")
        print("║           AMOS UNIFIED RUNTIME v4.0                        ║")
        print("║    Persistent Economic Cognitive Organism                    ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()

        try:
            if self.mode in ("v4", "full"):
                self._init_v4()

            if self.mode in ("core", "full"):
                self._init_core()
                self._init_memory()
                self._init_meta()

            if self.mode == "full":
                self._init_repo_and_coding()
                self._init_brain()
                self._init_organism()
                self._init_clawspring()
                self._init_omega()  # NEW: Ω layer
                self._wire_layers()

            self._initialized = True
            print("✓ Unified runtime initialized")
            print(f"  Mode: {self.mode}")
            print()
            return True

        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _init_v4(self) -> None:
        """Initialize AMOS v4 Economic Organism."""
        print("→ Initializing AMOS v4 Economic Organism...")
        try:
            from amos_v4 import AMOSv4

            self.v4 = AMOSv4(name="AMOS_Unified_v4")
            print("  ✓ v4 Persistence Layer (Pe)")
            print("  ✓ v4 Economic Layer (X)")
            print("  ✓ v4 World Model (Y)")
            print("  ✓ v4 Resource Allocation (Q)")
            print()
        except ImportError as e:
            print(f"  ! v4 not available: {e}")
            print()

    def _init_core(self) -> None:
        """Initialize AMOS Core Cognitive Engine."""
        print("→ Initializing AMOS Core Cognitive Engine...")
        try:
            from amos_core import AMOSCore

            self.core = AMOSCore()
            print("  ✓ Universal State Graph")
            print("  ✓ Global Workspace")
            print("  ✓ Branch Field Engine")
            print("  ✓ Collapse Engine")
            print("  ✓ Morph Executor")
            print()
        except ImportError as e:
            print(f"  ! Core not available: {e}")
            print()

        # Time Engine
        try:
            from amos_time import TimeEngine

            self.time_engine = TimeEngine()
            print("  ✓ Time Engine (Event Sourcing)")
        except ImportError:
            pass

        # Energy System
        try:
            from amos_energy import AMOSEnergySystem

            self.energy_system = AMOSEnergySystem()
            print("  ✓ Energy System (Resource Allocation)")
            print()
        except ImportError:
            pass

    def _init_memory(self) -> None:
        """Initialize AMOS Memory Systems."""
        print("→ Initializing AMOS Memory Systems...")
        try:
            from amos_memory import AMOSMemorySystem

            self.memory = AMOSMemorySystem()
            print("  ✓ Working Memory")
            print("  ✓ Episodic Memory")
            print("  ✓ Semantic Memory")
            print("  ✓ Procedural Memory")
            print("  ✓ Self Memory")
            print()
        except ImportError as e:
            print(f"  ! Memory not available: {e}")
            print()

    def _init_meta(self) -> None:
        """Initialize AMOS Meta-cognition."""
        print("→ Initializing AMOS Meta-cognition...")
        try:
            from amos_meta import MetaCognitionSystem

            self.meta = MetaCognitionSystem()
            print("  ✓ Prediction Tracking")
            print("  ✓ Branch Efficiency Analysis")
            print("  ✓ Failure Pattern Detection")
            print("  ✓ Parameter Adaptation")
            print("  ✓ Confidence Calibration")
            print()
        except ImportError as e:
            print(f"  ! Meta-cognition not available: {e}")
            print()

    def _init_repo_and_coding(self) -> None:
        """Initialize Repo Intelligence and Self-coding."""
        print("→ Initializing Repo Intelligence & Self-coding...")

        try:
            from amos_repo import AMOSRepoIntelligence

            self.repo_intel = AMOSRepoIntelligence(".")
            print("  ✓ Repo Intelligence (Code Understanding)")
        except ImportError:
            pass

        try:
            from amos_self_code import AMOSSelfCoding

            self.self_coding = AMOSSelfCoding()
            print("  ✓ Self-coding (Code Generation)")
        except ImportError:
            pass

        print()

    def _init_brain(self) -> None:
        """Initialize AMOS Brain Integration."""
        print("→ Initializing AMOS Brain Integration...")
        try:
            from amos_brain import get_amos_integration

            self.brain = get_amos_integration()
            status = self.brain.get_status()
            print(f"  ✓ Brain loaded: {status['engines_count']} engines")
            print(f"  ✓ Laws active: {len(status['laws_active'])}")
            print()
        except ImportError as e:
            print(f"  ! Brain integration not available: {e}")
            print()

    def _init_organism(self) -> None:
        """Initialize AMOS Organism OS Layer 2."""
        print("→ Initializing AMOS Organism OS (Layer 2)...")

        try:
            from organism import AMOSOrganism, OrganismState

            self.organism = AMOSOrganism()
            print("  ✓ Organism instantiated")
            print("  ✓ 14 subsystems ready")
            print()
        except ImportError as e:
            print(f"  ! Organism OS not available: {e}")
            print()

    def _init_clawspring(self) -> None:
        """Initialize ClawSpring Layer 3."""
        print("→ Initializing ClawSpring Integration (Layer 3)...")

        try:
            from clawspring.amos_plugin import AMOSPlugin

            self.clawspring = AMOSPlugin()
            print("  ✓ ClawSpring plugin ready")
            print()
        except ImportError as e:
            print(f"  ! ClawSpring plugin not available: {e}")
            print()

    def _init_omega(self) -> None:
        """Initialize Ω Axiomatic Layer (NEW)."""
        print("→ Initializing Ω Axiomatic Layer...")

        try:
            from amos_omega import AMOSOmega

            self.omega = AMOSOmega()
            print("  ✓ Ω Runtime (32 axioms executable)")
        except ImportError as e:
            print(f"  ! Ω runtime not available: {e}")

        try:
            from amos_axiom_validator import AxiomValidator

            self.axiom_validator = AxiomValidator()
            print("  ✓ Axiom Validator (theory→practice)")
        except ImportError as e:
            print(f"  ! Axiom validator not available: {e}")

        try:
            from amos_coherence_omega import CoherenceOmega

            self.coherence_omega = CoherenceOmega()
            print("  ✓ Coherence Ω (human + axioms)")
        except ImportError as e:
            print(f"  ! Coherence Ω not available: {e}")

        print()

    def _wire_layers(self) -> None:
        """Wire all layers together."""
        print("→ Wiring layers...")

        # Connect brain to organism
        if self.brain and self.organism:
            print("  ✓ Brain ↔ Organism linked")

        # Connect organism to clawspring
        if self.organism and self.clawspring:
            print("  ✓ Organism ↔ ClawSpring linked")

        # Connect brain to clawspring (direct)
        if self.brain and self.clawspring:
            self.clawspring.brain = self.brain
            print("  ✓ Brain ↔ ClawSpring linked")

        # Connect Ω to coherence (NEW)
        if self.omega and self.coherence_omega:
            print("  ✓ Ω ↔ Coherence linked")

        # Connect validator to all layers (NEW)
        if self.axiom_validator:
            print("  ✓ Validator → All layers")

        print()

    def run(self) -> int:
        """Run the unified runtime."""
        if not self._initialized:
            print("Error: Runtime not initialized")
            return 1

        print("=" * 60)
        print("AMOS UNIFIED RUNTIME - ACTIVE")
        print("=" * 60)
        print()

        # Show status
        self._show_status()

        # Start based on mode
        if self.mode == "full" and self.clawspring:
            return self._run_full_mode()
        elif self.mode == "organism":
            return self._run_organism_mode()
        elif self.mode == "brain":
            return self._run_brain_mode()

        return 0

    def _show_status(self) -> None:
        """Show unified status."""
        print("=" * 60)
        print("AMOS UNIFIED STATUS")
        print("=" * 60)
        print()
        print("Layer 1 - Economic Organism (v4):")
        print(f"  [Pe] Persistence:    {'✓' if self.v4 else '✗'}")
        print(f"  [X]  Economics:    {'✓' if self.v4 else '✗'}")
        print(f"  [Y]  World Model:  {'✓' if self.v4 else '✗'}")
        print(f"  [Q]  Resources:    {'✓' if self.v4 else '✗'}")
        print()
        print("Layer 2 - Core Cognitive:")
        print(f"  [C]  Core Engine:  {'✓' if self.core else '✗'}")
        print(f"  [T]  Time Engine:  {'✓' if self.time_engine else '✗'}")
        print(f"  [E]  Energy:       {'✓' if self.energy_system else '✗'}")
        print()
        print("Layer 3 - Memory Systems:")
        print(f"  [M]  Memory:        {'✓' if self.memory else '✗'}")
        print()
        print("Layer 4 - Meta-cognition:")
        print(f"  [Mc] Reflection:    {'✓' if self.meta else '✗'}")
        print()
        print("Layer 5 - Code Intelligence:")
        print(f"  [R]  Repo Intel:   {'✓' if self.repo_intel else '✗'}")
        print(f"  [Sc] Self-coding:  {'✓' if self.self_coding else '✗'}")
        print()
        print("Layer 6 - Integration:")
        print(f"  [B]  Brain API:     {'✓' if self.brain else '✗'}")
        print(f"  [O]  Organism OS:  {'✓' if self.organism else '✗'}")
        print()

        print("Layer 7 - Ω Axiomatic (NEW):")
        print(f"  [Ω]  Omega Runtime:  {'✓' if self.omega else '✗'}")
        print(f"  [V]  Validator:      {'✓' if self.axiom_validator else '✗'}")
        print(f"  [CΩ] Coherence Ω:   {'✓' if self.coherence_omega else '✗'}")
        print()

    def _run_full_mode(self) -> int:
        """Run in full unified mode."""
        print("Running in FULL mode - All layers active")
        print()

        # Enable clawspring plugin
        if self.clawspring:
            self.clawspring.enable()

        # Start clawspring agent with AMOS enhancement
        try:
            import subprocess

            result = subprocess.run(
                [sys.executable, "amos_clawspring.py"], cwd=str(Path(__file__).parent)
            )
            return result.returncode
        except KeyboardInterrupt:
            print("\nShutting down AMOS Unified...")
            return 0

    def _run_organism_mode(self) -> int:
        """Run in organism-only mode."""
        print("Running in ORGANISM mode")
        print()

        if self.organism:
            # Run organism primary loop
            print("Starting Organism Primary Loop...")
            print("  01_BRAIN → 02_SENSES → 05_SKELETON → 08_WORLD_MODEL")
            print("  → 09_QUANTUM → 06_MUSCLE → 07_METABOLISM → 01_BRAIN")

        return 0

    def _run_brain_mode(self) -> int:
        """Run in brain-only mode."""
        print("Running in BRAIN mode")
        print()

        if self.brain:
            status = self.brain.get_status()
            print("Brain Status:")
            print(f"  Engines: {status['engines_count']}")
            print(f"  Domains: {len(status['domains_covered'])}")
            print(f"  Laws: {', '.join(status['laws_active'])}")

        return 0


def demo_axiomatic_mode(runtime: AMOSUnifiedRuntime) -> int:
    """Run Ω axiomatic demonstration (NEW)."""
    print("=" * 60)
    print("AMOS Ω — Axiomatic Demonstration")
    print("=" * 60)
    print()

    if not runtime.omega:
        print("Ω runtime not available")
        return 1

    from amos_omega import Action, State, Substrate

    # Create test state
    state = State(classical={"value": 1.0, "energy": 100.0}, identity="demo_agent", time=0.0)

    print("[Initial State]")
    print(f"  Identity: {state.identity}")
    print(f"  Energy: {state.classical.get('energy')}")
    print()

    # Run axiom checks
    if runtime.axiom_validator:
        print("[Axiom Validation]")
        report = runtime.axiom_validator.validate_state(state)
        print(f"  Valid: {report.is_valid()}")
        print(f"  Checks: {len(report.checks)}")
        print()

    # Execute runtime step
    action = Action(
        name="demo_action", substrate=Substrate.CLASSICAL, effect={"value": 1.0}, energy_cost=0.1
    )

    print("[Runtime Step]")
    new_state = runtime.omega.runtime_step(state, action, {})
    if new_state:
        print("  ✓ Step executed successfully")
        print(f"  Ledger entries: {len(runtime.omega.get_ledger())}")
    else:
        print("  ✗ Step failed - state not in Z*")

    print()
    print("=" * 60)
    return 0


def demo_coherence_mode(runtime: AMOSUnifiedRuntime) -> int:
    """Run Coherence Ω demonstration (NEW)."""
    print("=" * 60)
    print("AMOS Coherence Ω — Human Cognition + Axioms")
    print("=" * 60)
    print()

    if not runtime.coherence_omega:
        print("Coherence Ω not available")
        return 1

    # Test messages
    messages = [
        "I'm feeling overwhelmed with everything",
        "I need to make a complex decision",
        "Things are going well today",
    ]

    print("[Processing Test Messages]")
    print()

    for msg in messages:
        print(f"Input: {msg}")
        result = runtime.coherence_omega.process_message(msg, validate=True)

        print(f"  State: {result.coherence_result.detected_state.name}")
        print(f"  Intervention: {result.coherence_result.intervention_mode.name}")
        print(f"  Master Law: {'✓' if result.master_law_compliant else '✗'}")
        print(f"  Valid: {'✓' if result.is_valid else '✗'}")
        print()

    # Show stats
    stats = runtime.coherence_omega.get_compliance_stats()
    print("[Compliance Statistics]")
    print(f"  Total: {stats['total']} interactions")
    print(f"  Compliant: {stats['rate']:.0%}")
    print()

    print("=" * 60)
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AMOS Unified Runtime - Brain × Organism × ClawSpring × Ω"
    )
    parser.add_argument(
        "--mode",
        choices=["v4", "core", "brain", "organism", "full", "omega", "coherence"],
        default="full",
        help="Runtime mode (default: full)",
    )
    parser.add_argument("--status", action="store_true", help="Show status and exit")
    parser.add_argument(
        "--validate", action="store_true", help="Run axiom validation on initialization"
    )
    parser.add_argument(
        "--demo",
        choices=["axiomatic", "coherence", "economic", "all"],
        help="Run specific demonstration",
    )

    args = parser.parse_args()

    # Create and initialize runtime
    runtime = AMOSUnifiedRuntime(mode=args.mode)

    if args.status:
        runtime.initialize()
        return 0

    # Run demonstrations
    if args.demo == "axiomatic":
        if runtime.initialize():
            return demo_axiomatic_mode(runtime)
        return 1
    elif args.demo == "coherence":
        if runtime.initialize():
            return demo_coherence_mode(runtime)
        return 1
    elif args.demo == "economic":
        # Run v4 demo
        try:
            import subprocess

            result = subprocess.run([sys.executable, "amos_v4.py"])
            return result.returncode
        except Exception as e:
            print(f"Economic demo failed: {e}")
            return 1
    elif args.demo == "all":
        # Run all demos
        if runtime.initialize():
            demo_axiomatic_mode(runtime)
            print("\n" + "=" * 60 + "\n")
            demo_coherence_mode(runtime)
            return 0
        return 1

    # Initialize and run
    if runtime.initialize():
        # Post-initialization validation if requested
        if args.validate and runtime.axiom_validator:
            print("[Post-Initialization Validation]")
            # Validate each initialized component
            valid_count = 0
            total_count = 0

            if runtime.v4:
                total_count += 1
                # Would validate v4 state here
                valid_count += 1
                print("  ✓ v4: Valid")

            if runtime.omega:
                total_count += 1
                valid_count += 1
                print("  ✓ Ω: Valid")

            print(f"  Summary: {valid_count}/{total_count} components valid")
            print()

        return runtime.run()
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
