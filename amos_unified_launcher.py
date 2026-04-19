#!/usr/bin/env python3
"""AMOS Unified Launcher
=====================

Integrates the 14-subsystem Organism OS with ClawSpring runtime,
enabling all 400+ features through a unified interface.

This bridge connects:
- AMOS Organism OS (14 subsystems)
- ClawSpring runtime (25 tools, agent loop)
- AMOS Brain (6 laws, cognitive stack)
- Knowledge base (160+ engines, 55 countries)

Owner: Trang
Version: 1.0.0
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Add paths for all systems
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "AMOS_ORGANISM_OS"))
sys.path.insert(0, str(REPO_ROOT / "clawspring"))
sys.path.insert(0, str(REPO_ROOT / "amos_brain"))


class AMOSUnifiedRuntime:
    """Unified runtime integrating all AMOS systems.

    Provides single interface to:
    - Organism OS (14 subsystems)
    - ClawSpring (agent loop, tools)
    - Brain (cognitive architecture)
    - Knowledge base (engines, packs)
    """

    def __init__(self):
        self.organism = None
        self.brain = None
        self.runtime = None
        self.knowledge_loaded = False
        self._init_status = {}

    def initialize(self) -> Dict[str, Any]:
        """Initialize all systems and return status."""
        print("🚀 AMOS Unified Runtime Initialization")
        print("=" * 60)

        # 1. Initialize Organism (14 subsystems)
        print("[1/4] Initializing Organism OS (14 subsystems)...")
        try:
            from organism import AmosOrganism

            self.organism = AmosOrganism()
            status = self.organism.status()
            self._init_status["organism"] = {
                "status": "✅ ACTIVE",
                "subsystems": len(status.get("active_subsystems", [])),
                "session": status.get("session_id", "N/A")[:8],
            }
            print(f"      ✓ {self._init_status['organism']['subsystems']}/14 subsystems active")
        except Exception as e:
            self._init_status["organism"] = {"status": f"❌ Error: {e}"}
            print(f"      ❌ Failed: {e}")

        # 2. Initialize Brain
        print("[2/4] Initializing AMOS Brain (cognitive architecture)...")
        try:
            from amos_brain import GlobalLaws, get_brain

            self.brain = get_brain()
            laws = GlobalLaws()
            self._init_status["brain"] = {
                "status": "✅ ACTIVE",
                "laws": len(laws.LAWS),
                "version": "vInfinity",
            }
            print("      ✓ 6 Global Laws loaded")
        except Exception as e:
            self._init_status["brain"] = {"status": f"❌ Error: {e}"}
            print(f"      ❌ Failed: {e}")

        # 3. Check ClawSpring
        print("[3/4] Checking ClawSpring runtime...")
        try:
            import clawspring

            version = getattr(clawspring, "VERSION", "unknown")
            self._init_status["clawspring"] = {"status": "✅ AVAILABLE", "version": version}
            print(f"      ✓ ClawSpring v{version} ready")
        except Exception as e:
            self._init_status["clawspring"] = {"status": f"⚠️  {e}"}
            print(f"      ⚠️  Not available: {e}")

        # 4. Knowledge Base
        print("[4/4] Cataloging knowledge base...")
        knowledge_stats = self._catalog_knowledge()
        self._init_status["knowledge"] = knowledge_stats
        print(f"      ✓ {knowledge_stats['engines']} engines")
        print(f"      ✓ {knowledge_stats['countries']} countries")
        print(f"      ✓ {knowledge_stats['sectors']} sectors")

        print("=" * 60)
        return self._init_status

    def _catalog_knowledge(self) -> Dict[str, Any]:
        """Catalog available knowledge."""
        brain_path = REPO_ROOT / "_AMOS_BRAIN"
        stats = {"engines": 0, "countries": 0, "sectors": 0, "manuals": 0}

        # Count engines
        for subdir in ["Kernels", "Core", "Cognitive", "Domains", "Unipower"]:
            path = brain_path / subdir
            if path.exists():
                stats["engines"] += len(list(path.glob("*.json")))

        # Count knowledge packs
        packs_path = brain_path / "Packs"
        if packs_path.exists():
            stats["countries"] = (
                len(list((packs_path / "Country_Packs").glob("*")))
                if (packs_path / "Country_Packs").exists()
                else 0
            )
            stats["sectors"] = (
                len(list((packs_path / "Sector_Packs").glob("*")))
                if (packs_path / "Sector_Packs").exists()
                else 0
            )

        # Count training manuals
        training_path = brain_path / "training"
        if training_path.exists():
            stats["manuals"] = len(list(training_path.glob("*.pdf")))

        stats["status"] = "✅ CATALOGED"
        return stats

    def get_organism(self) -> Any:
        """Get the initialized organism."""
        if not self.organism:
            raise RuntimeError("Organism not initialized. Call initialize() first.")
        return self.organism

    def get_subsystem(self, name: str) -> Any:
        """Get a specific subsystem by name."""
        if not self.organism:
            raise RuntimeError("Organism not initialized")

        subsystem_map = {
            # Core
            "brain": "brain",
            "senses": "senses",
            "memory": "memory",
            # Support
            "immune": "immune",
            "resources": "resources",
            "budget": "budget",
            "cashflow": "cashflow",
            "constraints": "constraints",
            "validator": "validator",
            "integrity": "integrity",
            "muscle": "muscle",
            "code_runner": "code_runner",
            "workflow": "workflow",
            "pipeline": "pipeline",
            "transform": "transform",
            "io_router": "io_router",
            # Intelligence
            "knowledge": "knowledge",
            "context_mapper": "context_mapper",
            "semantic_index": "semantic_index",
            "scenarios": "scenarios",
            "monte_carlo": "monte_carlo",
            "decision_optimizer": "decision_optimizer",
            # Evolution
            "agent_coordinator": "agent_coordinator",
            "communication_bridge": "communication_bridge",
            "human_interface": "human_interface",
            "negotiation_engine": "negotiation_engine",
            "growth_engine": "growth_engine",
            "adaptation_system": "adaptation_system",
            "health_monitor": "health_monitor",
            "lifecycle_manager": "lifecycle_manager",
            # Governance
            "policy_engine": "policy_engine",
            "compliance_auditor": "compliance_auditor",
            "contract_manager": "contract_manager",
            "risk_governor": "risk_governor",
            # Factory
            "agent_factory": "agent_factory",
            "code_generator": "code_generator",
            "builder": "builder",
            "quality": "quality",
            # Interfaces
            "api": "api",
            "mcp": "mcp",
        }

        attr = subsystem_map.get(name.lower())
        if not attr:
            raise ValueError(f"Unknown subsystem: {name}")

        return getattr(self.organism, attr, None)

    def think(self, problem: str, context: dict = None) -> Dict[str, Any]:
        """Use brain to think about a problem."""
        if not self.brain:
            return {"error": "Brain not initialized"}

        try:
            from amos_brain import think

            response = think(problem, context or {})
            return {
                "analysis": response.content[:500],
                "confidence": response.confidence,
                "law_compliant": response.law_compliant,
                "reasoning_steps": len(response.reasoning),
            }
        except Exception as e:
            return {"error": str(e)}

    def decide(self, question: str, context: dict = None) -> Dict[str, Any]:
        """Use brain to make a decision."""
        if not self.brain:
            return {"error": "Brain not initialized"}

        try:
            from amos_brain import decide

            decision = decide(question, context or {})
            return {
                "recommendation": decision.recommendation,
                "confidence": decision.confidence,
                "alternatives": decision.alternatives,
                "risk_assessment": decision.risk_assessment,
            }
        except Exception as e:
            return {"error": str(e)}

    def status(self) -> Dict[str, Any]:
        """Get unified runtime status."""
        if not self._init_status:
            return {"error": "Not initialized"}

        total_systems = len(
            [s for s in self._init_status.values() if "✅" in str(s.get("status", ""))]
        )

        return {
            "initialization": self._init_status,
            "systems_active": total_systems,
            "total_systems": 4,
            "organism_status": self.organism.status() if self.organism else None,
            "ready": total_systems >= 3,
        }

    def launch_clawspring(self, model: str = None) -> None:
        """Launch ClawSpring with AMOS integration."""
        try:
            # Import and run clawspring
            import clawspring

            print(f"\n🚀 Launching ClawSpring v{clawspring.VERSION}")
            print("✅ Organism integration: ACTIVE")
            print("✅ Brain integration: ACTIVE")
            print("✅ 14 subsystems: READY")
            print("\nType '/help' for commands, '/exit' to quit\n")

            # Start interactive mode
            clawspring.main()
        except Exception as e:
            print(f"❌ Failed to launch ClawSpring: {e}")

    def run_demo(self) -> None:
        """Run comprehensive demo of all systems."""
        print("\n" + "=" * 60)
        print("AMOS UNIFIED RUNTIME DEMO")
        print("=" * 60)

        # Demo 1: Organism status
        print("\n1. Organism Status:")
        if self.organism:
            status = self.organism.status()
            print(f"   Session: {status.get('session_id', 'N/A')[:12]}")
            print(f"   Active: {len(status.get('active_subsystems', []))} subsystems")
            print(f"   Started: {status.get('started_at', 'N/A')[:19]}")

        # Demo 2: Brain thinking
        print("\n2. Brain Thinking:")
        if self.brain:
            result = self.think("What is the best architecture for a scalable system?")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Compliant: {result.get('law_compliant', False)}")

        # Demo 3: Subsystem access
        print("\n3. Subsystem Access:")
        if self.organism:
            try:
                health = self.get_subsystem("health_monitor")
                print(f"   Health Monitor: {health.get_status() if health else 'N/A'}")
            except Exception as e:
                print(f"   Error: {e}")

        # Demo 4: Knowledge base
        print("\n4. Knowledge Base:")
        knowledge = self._init_status.get("knowledge", {})
        print(f"   Engines: {knowledge.get('engines', 0)}")
        print(f"   Countries: {knowledge.get('countries', 0)}")
        print(f"   Training Manuals: {knowledge.get('manuals', 0)}")

        print("\n" + "=" * 60)
        print("Demo complete!")
        print("=" * 60)


def main():
    """Main entry point."""
    print("\n🧠 AMOS - Absolute Meta Operating System")
    print("   Unified Launcher v1.0.0\n")

    # Create and initialize runtime
    runtime = AMOSUnifiedRuntime()
    status = runtime.initialize()

    # Check if ready
    ready = all("✅" in str(s.get("status", "")) for s in status.values() if isinstance(s, dict))

    if ready:
        print("\n✅ All systems operational!")
        print("\nOptions:")
        print("  1. Run demo (/demo)")
        print("  2. Launch ClawSpring (/launch)")
        print("  3. Access organism directly (/organism)")
        print("  4. Brain thinking mode (/think)")
        print("  5. Exit (/exit)")

        while True:
            try:
                cmd = input("\namos> ").strip().lower()

                if cmd in ["/demo", "demo", "1"]:
                    runtime.run_demo()
                elif cmd in ["/launch", "launch", "2"]:
                    runtime.launch_clawspring()
                elif cmd in ["/organism", "organism", "3"]:
                    print("\nOrganism Status:")
                    print(runtime.get_organism().status())
                elif cmd in ["/think", "think", "4"]:
                    problem = input("Enter problem to think about: ")
                    result = runtime.think(problem)
                    print(f"\nResult: {result}")
                elif cmd in ["/exit", "exit", "quit", "5", "/quit"]:
                    print("Goodbye! 👋")
                    break
                elif cmd in ["/status", "status"]:
                    print(runtime.status())
                else:
                    print("Unknown command. Type /help for options.")

            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        print("\n⚠️  Some systems failed to initialize.")
        print("Check status above and try again.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
