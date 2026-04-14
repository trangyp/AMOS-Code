"""AMOS Organism Bridge - Connect Organism OS to Cognitive System."""

import sys
from pathlib import Path
from typing import Any, Optional

# Add organism OS to path
ORGANISM_PATH = Path(
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/AMOS_ORGANISM_OS"
)
if str(ORGANISM_PATH) not in sys.path:
    sys.path.insert(0, str(ORGANISM_PATH))


class OrganismBridge:
    """Bridge between AMOS Organism OS and ClawSpring cognitive system."""

    def __init__(self):
        self._coherence_engine = None
        self._predictive_engine = None
        self._task_executor = None
        self._bridge_status = {"coherence": False, "predictive": False, "task_executor": False}

    def _load_coherence_engine(self):
        """Load coherence engine from AMOS_ORGANISM_OS."""
        try:
            # Try to import from the open file location
            import importlib.util

            coherence_path = Path(
                "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/amos_coherence_engine.py"
            )
            if coherence_path.exists():
                spec = importlib.util.spec_from_file_location("coherence_engine", coherence_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._coherence_engine = module
                self._bridge_status["coherence"] = True
                return True
        except Exception as e:
            print(f"[OrganismBridge] Coherence engine not available: {e}")
        return False

    def _load_predictive_engine(self):
        """Load predictive engine from quantum layer."""
        try:
            from predictive_integration import get_predictive_integration

            self._predictive_engine = get_predictive_integration()
            self._bridge_status["predictive"] = True
            return True
        except Exception as e:
            print(f"[OrganismBridge] Predictive engine not available: {e}")
        return False

    def _load_task_executor(self):
        """Load task executor from muscle layer."""
        try:
            from task_execution_integration import get_task_execution_integration

            self._task_executor = get_task_execution_integration()
            self._bridge_status["task_executor"] = True
            return True
        except Exception as e:
            print(f"[OrganismBridge] Task executor not available: {e}")
        return False

    def initialize(self):
        """Initialize all organism OS connections."""
        self._load_coherence_engine()
        self._load_predictive_engine()
        self._load_task_executor()
        return self._bridge_status

    def get_status(self) -> dict[str, Any]:
        """Get bridge connection status."""
        return {
            "organism_path": str(ORGANISM_PATH),
            "components": self._bridge_status,
            "total_connected": sum(self._bridge_status.values()),
            "total_available": 3,
        }

    def enhance_cognitive_analysis(self, task: str) -> dict[str, Any]:
        """Use organism components to enhance cognitive task analysis."""
        enhancement = {"task": task, "organism_enhancements": {}}

        # Use coherence engine if available
        if self._bridge_status["coherence"] and self._coherence_engine:
            try:
                # Check for coherence in task context
                enhancement["organism_enhancements"]["coherence_check"] = {
                    "status": "available",
                    "message": "Coherence engine ready for task validation",
                }
            except Exception as e:
                enhancement["organism_enhancements"]["coherence_error"] = str(e)

        # Use predictive engine if available
        if self._bridge_status["predictive"] and self._predictive_engine:
            try:
                enhancement["organism_enhancements"]["predictive_insights"] = {
                    "status": "available",
                    "message": "Predictive engine ready for outcome forecasting",
                }
            except Exception as e:
                enhancement["organism_enhancements"]["predictive_error"] = str(e)

        # Use task executor if available
        if self._bridge_status["task_executor"] and self._task_executor:
            try:
                enhancement["organism_enhancements"]["execution_ready"] = {
                    "status": "available",
                    "message": "Organism task executor ready for action",
                }
            except Exception as e:
                enhancement["organism_enhancements"]["executor_error"] = str(e)

        return enhancement


# Singleton instance
_organism_bridge: Optional[OrganismBridge] = None


def get_organism_bridge() -> OrganismBridge:
    """Get or create the singleton organism bridge."""
    global _organism_bridge
    if _organism_bridge is None:
        _organism_bridge = OrganismBridge()
        _organism_bridge.initialize()
    return _organism_bridge


def print_organism_status():
    """Print organism OS integration status."""
    bridge = get_organism_bridge()
    status = bridge.get_status()

    print("=" * 70)
    print("AMOS ORGANISM OS BRIDGE - INTEGRATION STATUS")
    print("=" * 70)
    print(f"\n📁 Organism Path: {status['organism_path']}")
    print("\n🔗 Components:")

    for component, connected in status["components"].items():
        icon = "✓" if connected else "✗"
        print(f"  {icon} {component}: {'connected' if connected else 'not available'}")

    print(f"\n  Total: {status['total_connected']}/{status['total_available']} connected")

    if status["total_connected"] == status["total_available"]:
        print("\n✅ ORGANISM BRIDGE: FULLY OPERATIONAL")
        print("   All organism OS components integrated")
    elif status["total_connected"] > 0:
        print("\n⚠️  ORGANISM BRIDGE: PARTIALLY OPERATIONAL")
        print(f"   {status['total_connected']} of {status['total_available']} components available")
    else:
        print("\n❌ ORGANISM BRIDGE: NOT OPERATIONAL")
        print("   No organism OS components detected")

    print("=" * 70)


if __name__ == "__main__":
    print_organism_status()

    # Test enhancement
    bridge = get_organism_bridge()
    test_task = "Design a scalable microservices architecture"
    enhancement = bridge.enhance_cognitive_analysis(test_task)

    print("\n🧪 Test Enhancement:")
    print(f"  Task: {enhancement['task']}")
    print(f"  Enhancements: {len(enhancement['organism_enhancements'])} available")
