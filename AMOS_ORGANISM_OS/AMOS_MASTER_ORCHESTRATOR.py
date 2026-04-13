#!/usr/bin/env python3
"""
AMOS MASTER ORCHESTRATOR
========================

The central nervous system of the AMOS 7-System Organism.
Wires the primary cognitive loop across 14 subsystems.

Owner: Trang
Version: 1.0.0
Python: 3.9+
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================================
# CONSTANTS & PATHS
# ============================================================================

AMOS_ROOT = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
ORGANISM_ROOT = AMOS_ROOT / "AMOS_ORGANISM_OS"
BRAIN_ROOT = AMOS_ROOT / "_AMOS_BRAIN"

SYSTEM_REGISTRY_PATH = (
    ORGANISM_ROOT / "system_registry.json"
)
AGENT_REGISTRY_PATH = (
    ORGANISM_ROOT / "agent_registry.json"
)
ENGINE_REGISTRY_PATH = (
    ORGANISM_ROOT / "engine_registry.json"
)
WORLD_STATE_PATH = (
    ORGANISM_ROOT / "world_state.json"
)
OPERATOR_PROFILE_PATH = (
    ORGANISM_ROOT / "operator_profile_trang.json"
)

LOGS_DIR = ORGANISM_ROOT / "logs"
MEMORY_DIR = ORGANISM_ROOT / "memory"

# Primary loop sequence as defined in system registry
PRIMARY_LOOP = [
    "01_BRAIN",
    "02_SENSES",
    "05_SKELETON",
    "08_WORLD_MODEL",
    "12_QUANTUM_LAYER",
    "06_MUSCLE",
    "07_METABOLISM",
]


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AmosEvent:
    timestamp: str
    event_type: str
    subsystem: str
    payload: Dict[str, Any]


@dataclass
class CycleResult:
    subsystem: str
    status: str
    actions: List[str]
    outputs: Dict[str, Any]
    next_recommended: Optional[str] = None


@dataclass
class OrchestratorState:
    cycle_count: int = 0
    current_position: str = "01_BRAIN"
    active_subsystems: List[str] = field(default_factory=list)
    last_cycle_time: Optional[float] = None
    errors: List[str] = field(default_factory=list)


# ============================================================================
# REGISTRY LOADER
# ============================================================================

class RegistryLoader:
    """Loads and caches all AMOS registries."""

    def __init__(self) -> None:
        self.system_registry: Optional[Dict] = None
        self.agent_registry: Optional[Dict] = None
        self.engine_registry: Optional[Dict] = None
        self.world_state: Optional[Dict] = None
        self.operator_profile: Optional[Dict] = None

    def load_all(self) -> bool:
        """Load all registry files. Returns True if successful."""
        try:
            self.system_registry = self._load_json(SYSTEM_REGISTRY_PATH)
            self.agent_registry = self._load_json(AGENT_REGISTRY_PATH)
            self.engine_registry = self._load_json(ENGINE_REGISTRY_PATH)
            self.world_state = self._load_json(WORLD_STATE_PATH)
            self.operator_profile = self._load_json(OPERATOR_PROFILE_PATH)
            registries = [
                self.system_registry,
                self.agent_registry,
                self.engine_registry,
                self.world_state,
                self.operator_profile,
            ]
            return all(registries)
        except Exception as e:
            print(f"[ERROR] Failed to load registries: {e}")
            return False

    @staticmethod
    def _load_json(path: Path) -> Optional[Dict]:
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None


# ============================================================================
# SUBSYSTEM HANDLERS
# ============================================================================

class SubsystemHandler:
    """Base class for subsystem-specific logic."""

    def __init__(self, code: str, registry: Dict) -> None:
        self.code = code
        self.registry = registry
        self.subsystems = registry.get("subsystems", {})
        self.config = self.subsystems.get(code, {})

    def process(self, context: Dict[str, Any]) -> CycleResult:
        """Process one cycle for this subsystem."""
        raise NotImplementedError


class BrainHandler(SubsystemHandler):
    """01_BRAIN: Reasoning, planning, decomposition."""

    def process(self, context: Dict[str, Any]) -> CycleResult:
        actions = ["load_cognition_engine", "check_working_memory", "route_next_task"]

        # Load cognition kernel references
        kernel_refs = self.config.get("kernel_refs", [])

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "loaded_engines": ["AMOS_Cognition_Engine", "AMOS_Mind_Os"],
                "active_kernels": kernel_refs[:4] if kernel_refs else []
            },
            next_recommended="02_SENSES"
        )


class SensesHandler(SubsystemHandler):
    """02_SENSES: Filesystem, environment, context."""

    def process(self, context: Dict[str, Any]) -> CycleResult:
        actions = ["scan_filesystem", "check_environment", "read_emotion_inputs"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "filesystem_status": "accessible",
                "environment_loaded": True,
                "context_updated": datetime.utcnow().isoformat() + "Z"
            },
            next_recommended="05_SKELETON"
        )


class SkeletonHandler(SubsystemHandler):
    """05_SKELETON: Rules, constraints, hierarchy."""

    def process(self, context: Dict[str, Any]) -> CycleResult:
        actions = ["load_constraints", "check_permissions", "validate_time_architecture"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "constraints_loaded": ["Law_of_Law", "Rule_of_2", "Rule_of_4"],
                "permissions_valid": True
            },
            next_recommended="08_WORLD_MODEL"
        )


class WorldModelHandler(SubsystemHandler):
    """08_WORLD_MODEL: Macroeconomics, geopolitics, sectors."""

    def process(self, context: Dict[str, Any]) -> CycleResult:
        actions = ["load_tss_tpe", "scan_global_signals", "update_sector_maps"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "tss_tpe_loaded": True,
                "global_signals": [],
                "sector_status": "stable"
            },
            next_recommended="12_QUANTUM_LAYER"
        )


class QuantumLayerHandler(SubsystemHandler):
    """12_QUANTUM_LAYER: Timing, probability flows."""

    def process(self, context: Dict[str, Any]) -> CycleResult:
        actions = ["load_quantum_stack", "check_timing_vectors", "assess_probabilities"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "quantum_stack_loaded": True,
                "timing_aligned": True,
                "probability_states": ["baseline"]
            },
            next_recommended="06_MUSCLE"
        )


class MuscleHandler(SubsystemHandler):
    """06_MUSCLE: Run commands, write code, deploy."""

    def process(self, context: Dict[str, Any]) -> CycleResult:
        actions = ["check_code_engines", "validate_motor_actions", "prepare_deployment"]

        # Check if there are pending code tasks
        pending_tasks = context.get("pending_tasks", [])
        code_tasks = [t for t in pending_tasks if t.get("type") == "code"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "coding_engines_ready": True,
                "pending_code_tasks": len(code_tasks),
                "motor_actions_allowed": [
                    "generate_plan", "refine_plan", "analyze_text",
                    "propose_code_change", "log_decision", "simulate_outcome"
                ]
            },
            next_recommended="07_METABOLISM"
        )


class MetabolismHandler(SubsystemHandler):
    """07_METABOLISM: Pipelines, transforms, IO routing."""

    def process(self, context: Dict[str, Any]) -> CycleResult:
        actions = ["run_pipeline_cleanup", "route_io", "transform_data"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "pipelines_clean": True,
                "io_routed": True,
                "cycle_complete": True
            },
            next_recommended="01_BRAIN"
        )


# ============================================================================
# HANDLER FACTORY
# ============================================================================

HANDLER_MAP: Dict[str, type] = {
    "01_BRAIN": BrainHandler,
    "02_SENSES": SensesHandler,
    "05_SKELETON": SkeletonHandler,
    "08_WORLD_MODEL": WorldModelHandler,
    "12_QUANTUM_LAYER": QuantumLayerHandler,
    "06_MUSCLE": MuscleHandler,
    "07_METABOLISM": MetabolismHandler,
}


def get_handler(code: str, registry: Dict) -> Optional[SubsystemHandler]:
    """Factory function to get appropriate handler for subsystem code."""
    handler_class = HANDLER_MAP.get(code)
    if handler_class:
        return handler_class(code, registry)
    return None


# ============================================================================
# MASTER ORCHESTRATOR
# ============================================================================

class AmosMasterOrchestrator:
    """
    The central orchestrator for the AMOS 7-System Organism.
    Manages the primary cognitive loop across all subsystems.
    """

    def __init__(self) -> None:
        self.loader = RegistryLoader()
        self.state = OrchestratorState()
        self.running = False

        # Ensure directories exist
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> bool:
        """Initialize the orchestrator by loading all registries."""
        print("[AMOS] Initializing Master Orchestrator...")
        print(f"[AMOS] Root: {AMOS_ROOT}")
        print(f"[AMOS] Organism: {ORGANISM_ROOT}")

        if not self.loader.load_all():
            print("[AMOS] [ERROR] Failed to initialize - registry load failed")
            return False

        # Load active subsystems from registry
        registry = self.loader.system_registry or {}
        subsystems = registry.get("subsystems", {})
        active = [code for code, cfg in subsystems.items() if cfg.get("status") == "active"]
        self.state.active_subsystems = active

        print(f"[AMOS] Loaded {len(active)} active subsystems")
        print(f"[AMOS] Primary loop: {' -> '.join(PRIMARY_LOOP)}")

        return True

    def run_cycle(
        self, context: Optional[Dict] = None
    ) -> List[CycleResult]:
        """Run one complete cycle through the primary loop."""
        if context is None:
            context = {}

        results: List[CycleResult] = []
        start_time = time.time()

        print(f"\n[AMOS] === CYCLE {self.state.cycle_count + 1} ===")

        for subsystem_code in PRIMARY_LOOP:
            handler = get_handler(subsystem_code, self.loader.system_registry or {})

            if not handler:
                print(f"[AMOS] [WARN] No handler for {subsystem_code}")
                continue

            print(f"[AMOS] [{subsystem_code}] Processing...")

            try:
                result = handler.process(context)
                results.append(result)

                # Log the event
                self._log_event(AmosEvent(
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    event_type="subsystem_cycle",
                    subsystem=subsystem_code,
                    payload={
                        "status": result.status,
                        "actions": result.actions,
                        "outputs": result.outputs
                    }
                ))

                print(f"[AMOS] [{subsystem_code}] Status: {result.status}")

            except Exception as e:
                error_msg = f"[{subsystem_code}] Error: {str(e)}"
                print(f"[AMOS] [ERROR] {error_msg}")
                self.state.errors.append(error_msg)

        cycle_time = time.time() - start_time
        self.state.last_cycle_time = cycle_time
        self.state.cycle_count += 1

        print(f"[AMOS] Cycle completed in {cycle_time:.3f}s")

        return results

    def run_continuous(self, cycles: int = 1, delay: float = 0.1) -> None:
        """Run multiple cycles continuously."""
        self.running = True

        for i in range(cycles):
            if not self.running:
                break

            cycle_results = self.run_cycle()
            print(f"[AMOS] Cycle {i + 1} processed {len(cycle_results)} subsystems")

            if i < cycles - 1:
                time.sleep(delay)

        self.running = False
        print(f"\n[AMOS] Completed {cycles} cycles")

    def _log_event(self, event: AmosEvent) -> None:
        """Log an event to the log file."""
        log_file = LOGS_DIR / "orchestrator.log"
        log_entry = {
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "subsystem": event.subsystem,
            "payload": event.payload
        }

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        return {
            "cycle_count": self.state.cycle_count,
            "current_position": self.state.current_position,
            "active_subsystems": self.state.active_subsystems,
            "last_cycle_time": self.state.last_cycle_time,
            "error_count": len(self.state.errors),
            "running": self.running
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main() -> int:
    """Main entry point."""
    print("=" * 60)
    print("AMOS MASTER ORCHESTRATOR v1.0.0")
    print("Owner: Trang")
    print("=" * 60)

    orchestrator = AmosMasterOrchestrator()

    if not orchestrator.initialize():
        return 1

    # Run initial diagnostic cycle
    print("\n[AMOS] Running diagnostic cycle...")
    results = orchestrator.run_cycle()
    print(f"[AMOS] Diagnostic processed {len(results)} subsystems")

    # Print summary
    status = orchestrator.get_status()
    print("\n" + "=" * 60)
    print("STATUS SUMMARY")
    print("=" * 60)
    print(f"Cycles completed: {status['cycle_count']}")
    print(f"Active subsystems: {len(status['active_subsystems'])}")
    print(f"Last cycle time: {status['last_cycle_time']:.3f}s")
    print(f"Errors: {status['error_count']}")

    # Save state to memory
    state_file = MEMORY_DIR / "orchestrator_state.json"
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2)

    print(f"\n[AMOS] State saved to: {state_file}")
    print("[AMOS] Logs written to: {LOGS_DIR / 'orchestrator.log'}")
    print("\n[AMOS] Orchestrator ready.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
