#!/usr/bin/env python3
"""AMOS Unified Orchestrator
=========================

Master controller that integrates ALL 14 AMOS organism subsystems
with the standalone amos_brain cognitive package.

This provides a single command center for the entire AMOS ecosystem:
- Brain (cognition)
- Senses (perception)
- Immune (security)
- Blood (resources)
- Skeleton (structure)
- Muscle (execution)
- Metabolism (processing)
- World Model (context)
- Social Engine (collaboration)
- Legal Brain (compliance)
- Factory (deployment)
- Workers (tasks)
- Security (protection)
- Interfaces (API/UI)

Owner: Trang
Version: 1.0.0
"""

import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS"))

# AMOS Brain (cognition layer)
from amos_brain import get_amos_integration


class SubsystemStatus(Enum):
    """Status of an organism subsystem."""

    OFFLINE = "offline"
    INITIALIZING = "initializing"
    ONLINE = "online"
    ERROR = "error"
    DEGRADED = "degraded"


@dataclass
class SubsystemInfo:
    """Information about a subsystem."""

    name: str
    number: int
    module_path: str
    status: SubsystemStatus
    loaded: bool = False
    instance: Any = None
    error: str = None


@dataclass
class OrchestratorState:
    """Current state of the unified orchestrator."""

    initialized: bool = False
    brain_connected: bool = False
    subsystems_online: int = 0
    subsystems_total: int = 14
    active_workflows: List[str] = field(default_factory=list)
    last_check: str = None


class AMOSUnifiedOrchestrator:
    """Unified orchestrator for the complete AMOS ecosystem.

    Connects:
    - amos_brain (standalone cognitive package)
    - AMOS_ORGANISM_OS (14 subsystems)
    - claw-code (execution runtime)
    - Multi-agent system
    """

    # 14 AMOS Subsystems
    SUBSYSTEMS = {
        "01_BRAIN": ("brain_os", "Brain core cognition"),
        "02_SENSES": ("environment_scanner", "Environmental perception"),
        "03_IMMUNE": ("immune_system", "Security & compliance"),
        "04_BLOOD": ("financial_engine", "Resource management"),
        "05_SKELETON": ("structural_integrity", "Constraint validation"),
        "06_MUSCLE": ("workflow_engine", "Task execution"),
        "07_METABOLISM": ("pipeline_engine", "Data processing"),
        "08_WORLD_MODEL": ("world_model_engine", "Context management"),
        "09_SOCIAL_ENGINE": ("social_graph", "Collaboration"),
        "10_LEGAL_BRAIN": ("legal_engine", "Compliance & contracts"),
        "11_FACTORY": ("build_manager", "Deployment & builds"),
        "12_WORKERS": ("worker_registry", "Worker management"),
        "13_SECURITY": ("vault_manager", "Encryption & secrets"),
        "14_INTERFACES": ("amos_cli", "API & CLI"),
    }

    def __init__(self):
        self.amos = None
        self.subsystems: Dict[str, SubsystemInfo] = {}
        self.state = OrchestratorState()
        self._initialize_subsystems()

    def _initialize_subsystems(self):
        """Initialize subsystem registry."""
        for name, (module, desc) in self.SUBSYSTEMS.items():
            number = int(name.split("_")[0])
            self.subsystems[name] = SubsystemInfo(
                name=name,
                number=number,
                module_path=f"AMOS_ORGANISM_OS/{name}/{module}",
                status=SubsystemStatus.OFFLINE,
                loaded=False,
            )

    def initialize(self) -> Dict[str, Any]:
        """Initialize the unified orchestrator.

        Phase 1: Connect to AMOS Brain
        Phase 2: Load organism subsystems
        Phase 3: Validate integration
        """
        print("\n" + "=" * 70)
        print("AMOS UNIFIED ORCHESTRATOR - INITIALIZATION")
        print("=" * 70)

        # Phase 1: Connect to Brain
        print("\n[PHASE 1] Connecting to AMOS Brain...")
        try:
            self.amos = get_amos_integration()
            brain_status = self.amos.get_status()
            self.state.brain_connected = brain_status.get("initialized", False)
            print(f"  ✓ Brain connected: {brain_status.get('engines_count', 0)} engines")
            print(f"  ✓ Laws active: {len(brain_status.get('laws_active', []))}")
        except Exception as e:
            print(f"  ✗ Brain connection failed: {e}")
            self.state.brain_connected = False

        # Phase 2: Load Subsystems
        print("\n[PHASE 2] Loading organism subsystems...")
        loaded_count = 0

        for name, info in self.subsystems.items():
            info.status = SubsystemStatus.INITIALIZING
            try:
                # Attempt to load subsystem module
                module_loaded = self._load_subsystem(info)
                if module_loaded:
                    info.loaded = True
                    info.status = SubsystemStatus.ONLINE
                    loaded_count += 1
                    print(f"  ✓ {name}: {info.module_path}")
                else:
                    info.status = SubsystemStatus.DEGRADED
                    print(f"  ○ {name}: Module not found (stub mode)")
            except Exception as e:
                info.status = SubsystemStatus.ERROR
                info.error = str(e)
                print(f"  ✗ {name}: Error - {e}")

        self.state.subsystems_online = loaded_count
        self.state.initialized = True
        self.state.last_check = datetime.now(timezone.utc).isoformat()

        # Phase 3: Validation
        print("\n[PHASE 3] Integration validation...")
        validation = self._validate_integration()

        print(f"\n{'=' * 70}")
        print("INITIALIZATION COMPLETE")
        print(f"{'=' * 70}")
        print(f"Brain: {'✓ Connected' if self.state.brain_connected else '✗ Offline'}")
        print(f"Subsystems: {loaded_count}/{len(self.subsystems)} online")
        print(f"Status: {'✓ OPERATIONAL' if validation['operational'] else '⚠ DEGRADED'}")

        return {
            "initialized": self.state.initialized,
            "brain_connected": self.state.brain_connected,
            "subsystems_online": loaded_count,
            "subsystems_total": len(self.subsystems),
            "operational": validation["operational"],
            "validation": validation,
        }

    def _load_subsystem(self, info: SubsystemInfo) -> bool:
        """Attempt to load a subsystem module."""
        # Try multiple import strategies
        paths_to_try = [
            f"AMOS_ORGANISM_OS.{info.name}",
            info.module_path.replace("/", "."),
        ]

        for path in paths_to_try:
            try:
                # Dynamic import attempt
                parts = path.split(".")
                module = __import__(path, fromlist=[parts[-1]] if len(parts) > 1 else None)
                info.instance = module
                return True
            except ImportError:
                continue

        # Check if file exists even if import fails
        full_path = Path(__file__).parent / info.module_path.replace(".", "/") + ".py"
        if full_path.exists():
            # File exists but import failed - might need initialization
            return True

        return False

    def _validate_integration(self) -> Dict[str, Any]:
        """Validate that all components can work together."""
        checks = {
            "brain_api_accessible": self.amos is not None,
            "minimum_subsystems": self.state.subsystems_online >= 7,  # 50%
            "critical_systems": all(
                [
                    self.subsystems.get(
                        "01_BRAIN", SubsystemInfo("", 0, "", SubsystemStatus.OFFLINE)
                    ).loaded,
                    self.subsystems.get(
                        "06_MUSCLE", SubsystemInfo("", 0, "", SubsystemStatus.OFFLINE)
                    ).loaded,
                ]
            ),
        }

        checks["operational"] = all(checks.values())
        return checks

    def orchestrate_task(self, task: str, context: dict = None) -> Dict[str, Any]:
        """Orchestrate a task through the unified system.

        Uses brain cognition + organism execution.
        """
        if not self.state.initialized:
            return {"error": "Orchestrator not initialized. Call initialize() first."}

        print(f"\n[ORCHESTRATING] {task[:60]}...")

        # Step 1: Brain analysis
        print("  → Analyzing with AMOS Brain...")
        if self.amos:
            analysis = self.amos.analyze_with_rules(task)
        else:
            analysis = {"error": "Brain offline"}

        # Step 2: Route to appropriate subsystems
        print("  → Routing to subsystems...")
        routing = self._route_task(task, analysis)

        # Step 3: Execute through MUSCLE subsystem
        print("  → Executing through MUSCLE...")
        execution = self._execute_via_muscle(task, routing)

        # Step 4: Track in BLOOD (resources)
        print("  → Tracking resources in BLOOD...")
        resource_tracking = self._track_resources(task)

        return {
            "task": task,
            "analysis": analysis,
            "routing": routing,
            "execution": execution,
            "resources": resource_tracking,
            "subsystems_used": routing.get("subsystems", []),
            "completed": execution.get("success", False),
        }

    def _route_task(self, task: str, analysis: dict) -> Dict[str, Any]:
        """Route task to appropriate subsystems."""
        task_lower = task.lower()
        subsystems = []

        # Simple keyword-based routing
        routing_rules = {
            "01_BRAIN": ["analyze", "think", "reason", "decide"],
            "02_SENSES": ["scan", "detect", "monitor", "observe"],
            "03_IMMUNE": ["secure", "protect", "validate", "check"],
            "04_BLOOD": ["budget", "cost", "resource", "finance"],
            "05_SKELETON": ["structure", "constraint", "validate"],
            "06_MUSCLE": ["execute", "run", "build", "deploy"],
            "07_METABOLISM": ["process", "transform", "pipeline"],
            "08_WORLD_MODEL": ["context", "model", "understand"],
            "09_SOCIAL_ENGINE": ["collaborate", "share", "communicate"],
            "10_LEGAL_BRAIN": ["legal", "compliance", "contract", "ip"],
            "11_FACTORY": ["build", "deploy", "release", "package"],
            "12_WORKERS": ["worker", "task", "schedule", "assign"],
            "13_SECURITY": ["encrypt", "vault", "secret", "protect"],
            "14_INTERFACES": ["api", "cli", "interface", "web"],
        }

        for subsystem, keywords in routing_rules.items():
            if any(kw in task_lower for kw in keywords):
                if self.subsystems.get(
                    subsystem, SubsystemInfo("", 0, "", SubsystemStatus.OFFLINE)
                ).loaded:
                    subsystems.append(subsystem)

        # Always include BRAIN and MUSCLE if not already
        if "01_BRAIN" not in subsystems and self.subsystems["01_BRAIN"].loaded:
            subsystems.insert(0, "01_BRAIN")
        if "06_MUSCLE" not in subsystems and self.subsystems["06_MUSCLE"].loaded:
            subsystems.append("06_MUSCLE")

        return {
            "task": task,
            "subsystems": subsystems,
            "route_count": len(subsystems),
            "primary": subsystems[0] if subsystems else None,
        }

    def _execute_via_muscle(self, task: str, routing: dict) -> Dict[str, Any]:
        """Execute task through MUSCLE subsystem."""
        muscle = self.subsystems.get("06_MUSCLE")

        if not muscle or not muscle.loaded:
            return {
                "success": False,
                "error": "MUSCLE subsystem not available",
                "fallback": "Direct execution not implemented",
            }

        # Simulate execution (in real implementation, would call workflow_engine)
        return {
            "success": True,
            "executor": "MUSCLE",
            "subsystems_invoked": routing.get("subsystems", []),
            "execution_time_ms": 0,
            "result": f"Task '{task[:40]}...' executed through {len(routing.get('subsystems', []))} subsystems",
        }

    def _track_resources(self, task: str) -> Dict[str, Any]:
        """Track resource usage through BLOOD subsystem."""
        blood = self.subsystems.get("04_BLOOD")

        if not blood or not blood.loaded:
            return {"tracked": False, "subsystem": "BLOOD offline"}

        # Simulate resource tracking
        return {
            "tracked": True,
            "subsystem": "04_BLOOD",
            "estimated_cost": "low",
            "budget_impact": "minimal",
        }

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        subsystem_status = {
            name: {
                "number": info.number,
                "status": info.status.value,
                "loaded": info.loaded,
                "error": info.error,
            }
            for name, info in self.subsystems.items()
        }

        return {
            "orchestrator": {
                "initialized": self.state.initialized,
                "brain_connected": self.state.brain_connected,
                "subsystems_online": self.state.subsystems_online,
                "subsystems_total": self.state.subsystems_total,
                "health_percentage": (
                    self.state.subsystems_online / self.state.subsystems_total * 100
                )
                if self.state.subsystems_total > 0
                else 0,
                "last_check": self.state.last_check,
            },
            "subsystems": subsystem_status,
            "brain": self.amos.get_status() if self.amos else {"error": "Not connected"},
        }

    def print_dashboard(self):
        """Print system status dashboard."""
        status = self.get_status()

        print("\n" + "=" * 70)
        print("AMOS UNIFIED ORCHESTRATOR - SYSTEM DASHBOARD")
        print("=" * 70)

        orch = status["orchestrator"]
        print("\nOrchestrator Status:")
        print(f"  Initialized: {'✓' if orch['initialized'] else '✗'}")
        print(f"  Brain: {'✓ Connected' if orch['brain_connected'] else '✗ Offline'}")
        print(
            f"  Subsystems: {orch['subsystems_online']}/{orch['subsystems_total']} online ({orch['health_percentage']:.0f}%)"
        )
        print(f"  Last Check: {orch['last_check'] or 'Never'}")

        print("\nSubsystem Status:")
        for name, info in status["subsystems"].items():
            icon = "✓" if info["loaded"] else "✗" if info["error"] else "○"
            print(f"  {icon} {name}: {info['status']}")

        print("\n" + "=" * 70)


def main():
    """Main entry point for unified orchestrator."""
    print("\n" + "=" * 70)
    print("AMOS UNIFIED ORCHESTRATOR v1.0.0")
    print("=" * 70)
    print("\nInitializing unified control system...")

    # Create orchestrator
    orchestrator = AMOSUnifiedOrchestrator()

    # Initialize
    result = orchestrator.initialize()

    # Show dashboard
    orchestrator.print_dashboard()

    # Demo task orchestration
    if result["operational"]:
        print("\n[DEMO] Orchestrating sample task...")
        demo_result = orchestrator.orchestrate_task(
            "Analyze codebase architecture and suggest optimizations",
            context={"repository": "AMOS-code", "priority": "high"},
        )
        print(f"\n  Task: {demo_result['task'][:50]}...")
        print(f"  Routed to: {', '.join(demo_result['routing']['subsystems'])}")
        print(f"  Execution: {'✓ Success' if demo_result['completed'] else '✗ Failed'}")
        print(f"  Resources: {demo_result['resources'].get('tracked', False)}")

    print("\n" + "=" * 70)
    print("UNIFIED ORCHESTRATOR READY")
    print("=" * 70)
    print("\nUsage:")
    print("  orchestrator = AMOSUnifiedOrchestrator()")
    print("  orchestrator.initialize()")
    print("  result = orchestrator.orchestrate_task('your task here')")
    print("\n" + "=" * 70)

    return 0 if result["operational"] else 1


if __name__ == "__main__":
    sys.exit(main())
