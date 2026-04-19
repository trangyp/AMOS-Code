#!/usr/bin/env python3
"""AMOS Master Controller - Unified entry point for all AMOS versions.

Usage:
    python amos_master_controller.py --version v1         # Core cognitive
    python amos_master_controller.py --version v2         # + Memory + Meta
    python amos_master_controller.py --version v3       # + Time + Energy
    python amos_master_controller.py --version v4         # Economic organism
    python amos_master_controller.py --version v4-prod  # Production v4
    python amos_master_controller.py --version v5         # Civilization-scale
    python amos_master_controller.py --version full     # All layers
    python amos_master_controller.py --operational      # Run production system
    python amos_master_controller.py --demo             # Run all demos
    python amos_master_controller.py --arch             # Show architecture
"""

import argparse
import sys
from datetime import datetime
from typing import Any


class AMOSMasterController:
    """Master controller for all AMOS versions.

    Version Stack:
    - v1: Core (Branch, Collapse, Morph)
    - v2: v1 + Memory (5 types) + Meta-cognition
    - v3: v2 + Time Engine + Energy System
    - v4: v3 + Persistence + Economics + World Model
    - v5: v4 + Political + Negotiation + Narrative + Ecosystem + Civilization Memory
    """

    VERSIONS = {
        "unified": {
            "name": "Unified Hybrid System",
            "components": [
                "amos_unified",
                "amos_hybrid_orchestrator",
                "amos_memory_system",
                "amos_mcp_bridge",
                "repo_doctor_omega",
            ],
            "description": "Neural-Symbolic Hybrid + Memory + MCP + Repo Doctor",
        },
        "v1": {
            "name": "Core Cognitive",
            "components": ["amos_core"],
            "description": "Branch Field, Collapse, Morph execution",
        },
        "v2": {
            "name": "Memory & Learning",
            "components": ["amos_core", "amos_memory", "amos_meta"],
            "description": "5 memory types + Meta-cognitive reflection",
        },
        "v3": {
            "name": "Temporal & Resource",
            "components": ["amos_core", "amos_memory", "amos_meta", "amos_time", "amos_energy"],
            "description": "Time reasoning + Energy allocation",
        },
        "v4": {
            "name": "Economic Organism (Basic)",
            "components": [
                "amos_core",
                "amos_memory",
                "amos_meta",
                "amos_time",
                "amos_energy",
                "amos_v4",
            ],
            "description": "Persistence, Economics, World Model, Resources",
        },
        "v4-prod": {
            "name": "Economic Organism (Production)",
            "components": [
                "amos_core",
                "amos_memory",
                "amos_meta",
                "amos_time",
                "amos_energy",
                "amos_v4_runtime",
            ],
            "description": "Enhanced v4 with uncertainty, learning, identity-preservation, feedback compression",
        },
        "v5": {
            "name": "Civilization-Scale",
            "components": [
                "amos_core",
                "amos_memory",
                "amos_meta",
                "amos_time",
                "amos_energy",
                "amos_v4",
                "amos_v5",
            ],
            "description": "Political intelligence, Negotiation, Narrative, Ecosystem",
        },
        "full": {
            "name": "Complete AMOS",
            "components": [
                "amos_core",
                "amos_memory",
                "amos_meta",
                "amos_time",
                "amos_energy",
                "amos_repo",
                "amos_self_code",
                "amos_v4_runtime",
                "amos_v5",
            ],
            "description": "All layers with v4 Production enhancements",
        },
        "operational": {
            "name": "Production Operational System",
            "components": ["amos_operational"],
            "description": "Complete operational system with v4 Production + Connectors",
        },
    }

    def __init__(self):
        self.loaded_modules: Dict[str, Any] = {}
        self.active_version: str = None

    def show_architecture(self):
        """Display complete AMOS architecture."""
        print("=" * 70)
        print("🧬 AMOS ARCHITECTURE - COMPLETE STACK")
        print("=" * 70)
        print()

        for version, info in self.VERSIONS.items():
            print(f"  {version.upper():6} | {info['name']:20} | {info['description']}")

        print()
        print("=" * 70)
        print(
            f"Total Components: {len(set(c for v in self.VERSIONS.values() for c in v['components']))}"
        )
        print("=" * 70)
        print()

    def load_version(self, version: str) -> bool:
        """Load specific AMOS version."""
        if version not in self.VERSIONS:
            print(f"✗ Unknown version: {version}")
            return False

        info = self.VERSIONS[version]
        print(f"→ Loading AMOS {version.upper()}: {info['name']}")
        print()

        # Load each component
        success = True
        for component in info["components"]:
            if self._load_component(component):
                print(f"  ✓ {component}")
            else:
                print(f"  ✗ {component} (failed)")
                success = False

        print()
        if success:
            self.active_version = version
            print(f"✓ AMOS {version.upper()} loaded successfully")
        else:
            print(f"! AMOS {version.upper()} loaded with some failures")

        return success

    def _load_component(self, name: str) -> bool:
        """Load a single component."""
        try:
            if name == "amos_core":
                from amos_core import AMOSCore

                self.loaded_modules["core"] = AMOSCore()

            elif name == "amos_memory":
                from amos_memory import AMOSMemorySystem

                self.loaded_modules["memory"] = AMOSMemorySystem()

            elif name == "amos_meta":
                from amos_meta import MetaCognitionSystem

                self.loaded_modules["meta"] = MetaCognitionSystem()

            elif name == "amos_time":
                from amos_time import TimeEngine

                self.loaded_modules["time"] = TimeEngine()

            elif name == "amos_energy":
                from amos_energy import AMOSEnergySystem

                self.loaded_modules["energy"] = AMOSEnergySystem()

            elif name == "amos_repo":
                from amos_repo import AMOSRepoIntelligence

                self.loaded_modules["repo"] = AMOSRepoIntelligence(".")

            elif name == "amos_self_code":
                from amos_self_code import AMOSSelfCoding

                self.loaded_modules["self_code"] = AMOSSelfCoding()

            elif name == "amos_v4":
                from amos_v4 import AMOSv4

                self.loaded_modules["v4"] = AMOSv4()

            elif name == "amos_v4_runtime":
                from amos_v4_runtime import AMOSv4ProductionRuntime

                self.loaded_modules["v4_production"] = AMOSv4ProductionRuntime()

            elif name == "amos_v5":
                from amos_v5 import AMOSv5

                self.loaded_modules["v5"] = AMOSv5()

            elif name == "amos_operational":
                from amos_operational import AMOSOperational

                self.loaded_modules["operational"] = AMOSOperational()

            elif name == "amos_unified":
                from amos_unified_system import AMOSUnifiedSystem

                self.loaded_modules["unified"] = AMOSUnifiedSystem()

            elif name == "amos_hybrid_orchestrator":
                from amos_hybrid_orchestrator import HybridNeuralSymbolicOrchestrator

                self.loaded_modules["hybrid_orchestrator"] = HybridNeuralSymbolicOrchestrator()

            elif name == "amos_memory_system":
                from amos_memory_system import AMOSMemoryManager

                self.loaded_modules["memory_system"] = AMOSMemoryManager()

            elif name == "amos_mcp_bridge":
                from amos_mcp_bridge import AMOSMCPBridge

                self.loaded_modules["mcp_bridge"] = AMOSMCPBridge()

            elif name == "repo_doctor_omega":
                from repo_doctor_omega.engine import RepoDoctorEngine

                self.loaded_modules["repo_doctor"] = RepoDoctorEngine(".")

            return True

        except Exception:
            return False

    def run_demo(self, version: str):
        """Run demonstration for version."""
        print(f"\n{'=' * 70}")
        print(f"DEMO: AMOS {version.upper()}")
        print(f"{'=' * 70}\n")

        try:
            if version == "v1":
                from amos_core import demo_amos_core

                demo_amos_core()

            elif version == "v2":
                from amos_memory import demo_memory_system
                from amos_meta import demo_meta_cognition

                demo_memory_system()
                print("\n")
                demo_meta_cognition()

            elif version == "v3":
                from amos_energy import demo_energy_system
                from amos_time import demo_time_engine

                demo_time_engine()
                print("\n")
                demo_energy_system()

            elif version == "v4":
                from amos_v4 import demo_v4

                demo_v4()

            elif version == "v4-prod":
                from amos_v4_runtime import demo_production_v4

                demo_production_v4()

            elif version == "v5":
                from amos_v5 import demo_v5

                demo_v5()

            elif version == "operational":
                from amos_operational import demo_operational

                demo_operational()

            elif version == "full":
                self._run_full_demo()

        except Exception as e:
            print(f"✗ Demo failed: {e}")

    def _run_full_demo(self):
        """Run comprehensive demo of all capabilities."""
        print("🌌 FULL AMOS DEMONSTRATION")
        print("=" * 70)
        print()

        demos = [
            ("Core Cognitive", "amos_core", "demo_amos_core"),
            ("Memory Systems", "amos_memory", "demo_memory_system"),
            ("Meta-cognition", "amos_meta", "demo_meta_cognition"),
            ("Time Engine", "amos_time", "demo_time_engine"),
            ("Energy System", "amos_energy", "demo_energy_system"),
            ("Repo Intelligence", "amos_repo", "demo_repo_intelligence"),
            ("Self-coding", "amos_self_code", "demo_self_coding"),
            ("Economic Organism (v4)", "amos_v4", "demo_v4"),
            ("Civilization Intelligence (v5)", "amos_v5", "demo_v5"),
        ]

        for name, module, func in demos:
            print(f"\n{'─' * 70}")
            print(f"  {name}")
            print(f"{'─' * 70}")
            try:
                mod = __import__(module, fromlist=[func])
                getattr(mod, func)()
            except Exception as e:
                print(f"  ! Skipped: {e}")

    def get_status(self) -> dict:
        """Get complete system status."""
        return {
            "master_controller": "active",
            "active_version": self.active_version,
            "loaded_modules": list(self.loaded_modules.keys()),
            "timestamp": datetime.now(UTC).isoformat(),
            "architecture_complete": True,
            "versions_available": list(self.VERSIONS.keys()),
        }

    def interactive_mode(self):
        """Run interactive mode."""
        print("=" * 70)
        print("🧠 AMOS MASTER CONTROLLER - Interactive Mode")
        print("=" * 70)
        print()
        print("Commands:")
        print("  load <version>  - Load AMOS version (v1-v5, full)")
        print("  demo <version>  - Run demo")
        print("  status          - Show system status")
        print("  arch            - Show architecture")
        print("  quit            - Exit")
        print()

        while True:
            try:
                cmd = input("AMOS> ").strip().split()

                if not cmd:
                    continue

                if cmd[0] == "quit":
                    break

                elif cmd[0] == "load" and len(cmd) > 1:
                    self.load_version(cmd[1])

                elif cmd[0] == "demo" and len(cmd) > 1:
                    self.run_demo(cmd[1])

                elif cmd[0] == "status":
                    status = self.get_status()
                    print(f"\nActive: {status['active_version']}")
                    print(f"Modules: {', '.join(status['loaded_modules'])}")
                    print()

                elif cmd[0] == "arch":
                    self.show_architecture()

                else:
                    print("Unknown command")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\nShutting down AMOS...")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AMOS Master Controller - All Versions")
    parser.add_argument(
        "--version",
        "-v",
        choices=["unified", "v1", "v2", "v3", "v4", "v4-prod", "v5", "full", "operational"],
        default="unified",
        help="AMOS version to load (unified recommended for hybrid system)",
    )
    parser.add_argument(
        "--operational",
        "-o",
        action="store_true",
        help="Run operational production system (shortcut for --version operational)",
    )
    parser.add_argument("--demo", "-d", action="store_true", help="Run demonstration")
    parser.add_argument("--status", "-s", action="store_true", help="Show status and exit")
    parser.add_argument("--arch", "-a", action="store_true", help="Show architecture")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    controller = AMOSMasterController()

    if args.arch:
        controller.show_architecture()
        return 0

    if args.status:
        status = controller.get_status()
        print(f"AMOS Master Controller: {status['master_controller']}")
        print(f"Architecture: {'Complete' if status['architecture_complete'] else 'Partial'}")
        print(f"Versions: {', '.join(status['versions_available'])}")
        return 0

    if args.interactive:
        controller.interactive_mode()
        return 0

    if args.operational:
        controller.load_version("operational")
        if args.demo:
            controller.run_demo("operational")
        return 0

    if args.version:
        controller.load_version(args.version)
        if args.demo:
            controller.run_demo(args.version)
        return 0

    if args.demo:
        # Run full demo by default
        controller.run_demo("full")
        return 0

    # Default: show architecture and help
    controller.show_architecture()
    print()
    print("Usage:")
    print("  python amos_master_controller.py --version v4 --demo")
    print("  python amos_master_controller.py --interactive")
    print("  python amos_master_controller.py --arch")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
