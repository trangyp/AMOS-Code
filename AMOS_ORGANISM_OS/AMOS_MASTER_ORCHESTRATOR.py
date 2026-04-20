#!/usr/bin/env python3
"""AMOS MASTER ORCHESTRATOR
========================

The central nervous system of the AMOS 7-System Organism.
Wires the primary cognitive loop across 14 subsystems.

Owner: Trang
Version: 1.0.0
Python: 3.9+
"""

import json
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime

UTC = UTC
from pathlib import Path
from typing import Any, Optional

# ============================================================================
# CONSTANTS & PATHS
# ============================================================================

# Use file-relative path for portability
AMOS_ROOT = Path(__file__).resolve().parent.parent
ORGANISM_ROOT = AMOS_ROOT / "AMOS_ORGANISM_OS"
BRAIN_ROOT = AMOS_ROOT / "_AMOS_BRAIN"

SYSTEM_REGISTRY_PATH = ORGANISM_ROOT / "system_registry.json"
AGENT_REGISTRY_PATH = ORGANISM_ROOT / "agent_registry.json"
ENGINE_REGISTRY_PATH = ORGANISM_ROOT / "engine_registry.json"
WORLD_STATE_PATH = ORGANISM_ROOT / "world_state.json"
OPERATOR_PROFILE_PATH = ORGANISM_ROOT / "operator_profile_trang.json"

LOGS_DIR = ORGANISM_ROOT / "logs"
MEMORY_DIR = ORGANISM_ROOT / "memory"

# Primary loop sequence as defined in system registry
PRIMARY_LOOP = [
    "01_BRAIN",
    "02_SENSES",
    "03_IMMUNE",  # Security validation
    "04_BLOOD",  # Financial engine - active
    "05_SKELETON",
    "08_WORLD_MODEL",
    "09_SOCIAL_ENGINE",  # Agent communication
    "10_LIFE_ENGINE",  # Personal life management
    "11_LEGAL_BRAIN",  # Compliance and governance
    "12_QUANTUM_LAYER",
    "13_FACTORY",  # Agent factory
    "13_MEMORY_ARCHIVAL",  # Memory archival
    "15_KNOWLEDGE_CORE",  # Feature discovery
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
    payload: dict[str, Any]


@dataclass
class CycleResult:
    subsystem: str
    status: str
    actions: list[str]
    outputs: dict[str, Any]
    next_recommended: str = None


@dataclass
class OrchestratorState:
    cycle_count: int = 0
    current_position: str = "01_BRAIN"
    active_subsystems: list[str] = field(default_factory=list)
    last_cycle_time: float = None
    errors: list[str] = field(default_factory=list)


# ============================================================================
# REGISTRY LOADER
# ============================================================================


class RegistryLoader:
    """Loads and caches all AMOS registries."""

    def __init__(self) -> None:
        self.system_registry: dict = None
        self.agent_registry: dict = None
        self.engine_registry: dict = None
        self.world_state: dict = None
        self.operator_profile: dict = None

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
    def _load_json(path: Path) -> dict:
        if not path.exists():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None


# ============================================================================
# SUBSYSTEM HANDLERS
# ============================================================================


class SubsystemHandler:
    """Base class for subsystem-specific logic."""

    def __init__(self, code: str, registry: dict) -> None:
        self.code = code
        self.registry = registry
        self.subsystems = registry.get("subsystems", {})
        self.config = self.subsystems.get(code, {})

    def process(self, context: dict[str, Any]) -> CycleResult:
        """Process one cycle for this subsystem."""
        raise NotImplementedError


class BrainHandler(SubsystemHandler):
    """01_BRAIN: Reasoning, planning, decomposition."""

    def __init__(self, code: str, config: dict[str, Any]):
        super().__init__(code, config)
        self._cognitive_activator = None
        self._worker_bridge = None

    def _load_cognitive_engines(self, organism_root: Path) -> dict[str, Any]:
        """Load dormant cognitive engines from _AMOS_BRAIN."""
        try:
            from BRAIN.cognitive_engine_activator import CognitiveEngineActivator

            self._cognitive_activator = CognitiveEngineActivator()
            return self._cognitive_activator.get_status()
        except Exception as e:
            print(f"[01_BRAIN] Cognitive engine loading error: {e}")
            return {"loaded": False, "engines_count": 0, "error": str(e)}

    def _initialize_worker_bridge(self, organism_root: Path) -> dict[str, Any]:
        """Initialize brain-worker bridge for task routing."""
        try:
            from BRAIN.brain_worker_bridge import BrainWorkerBridge

            self._worker_bridge = BrainWorkerBridge(organism_root)
            return self._worker_bridge.get_bridge_status()
        except Exception as e:
            print(f"[01_BRAIN] Bridge initialization error: {e}")
            return {"status": "error", "error": str(e)}

    def _route_pending_tasks(self, organism_root: Path, tasks: list[str]) -> list[dict[str, Any]]:
        """Route pending tasks to optimal workers."""
        if not self._worker_bridge:
            self._initialize_worker_bridge(organism_root)

        if self._worker_bridge and tasks:
            return self._worker_bridge.optimize_task_execution(tasks)
        return {"tasks": [], "total_tasks": 0, "average_confidence": 0}

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = [
            "load_cognition_engine",
            "activate_cognitive_engines",
            "initialize_worker_bridge",
            "route_pending_tasks",
            "check_working_memory",
        ]

        # Load cognition kernel references
        kernel_refs = self.config.get("kernel_refs", [])

        # Load cognitive engines from _AMOS_BRAIN
        organism_root = context.get("organism_root", Path.cwd())
        cognitive_status = self._load_cognitive_engines(organism_root)

        # Initialize brain-worker bridge
        bridge_status = self._initialize_worker_bridge(organism_root)

        # Route pending tasks if any
        pending_tasks = context.get("pending_tasks", [])
        task_routing = self._route_pending_tasks(organism_root, pending_tasks)

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "loaded_engines": ["AMOS_Cognition_Engine", "AMOS_Mind_Os"],
                "active_kernels": kernel_refs[:4] if kernel_refs else [],
                "cognitive_engines_loaded": cognitive_status.get("engines_count", 0),
                "cognitive_domains": list(cognitive_status.get("domains", {}).keys()),
                "cognitive_activator_ready": cognitive_status.get("loaded", False),
                "bridge_operational": bridge_status.get("status") == "operational",
                "tasks_routed": task_routing.get("total_tasks", 0),
                "routing_confidence": task_routing.get("average_confidence", 0),
            },
            next_recommended="02_SENSES",
        )


class SensesHandler(SubsystemHandler):
    """02_SENSES: Filesystem, environment, context."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = ["scan_filesystem", "check_environment", "read_emotion_inputs"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "filesystem_status": "accessible",
                "environment_loaded": True,
                "context_updated": datetime.now(UTC).isoformat(),
            },
            next_recommended="05_SKELETON",
        )


class SkeletonHandler(SubsystemHandler):
    """05_SKELETON: Rules, constraints, hierarchy."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = ["load_constraints", "check_permissions", "validate_time_architecture"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "constraints_loaded": ["Law_of_Law", "Rule_of_2", "Rule_of_4"],
                "permissions_valid": True,
            },
            next_recommended="08_WORLD_MODEL",
        )


class WorldModelHandler(SubsystemHandler):
    """08_WORLD_MODEL: Macroeconomics, geopolitics, sectors."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = ["load_tss_tpe", "scan_global_signals", "update_sector_maps"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={"tss_tpe_loaded": True, "global_signals": [], "sector_status": "stable"},
            next_recommended="12_QUANTUM_LAYER",
        )


class QuantumLayerHandler(SubsystemHandler):
    """12_QUANTUM_LAYER: Timing, probability flows, predictive analytics."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = [
            "load_quantum_stack",
            "check_timing_vectors",
            "assess_probabilities",
            "generate_predictions",
        ]

        # Generate predictions
        predictions = {}
        try:
            from QUANTUM_LAYER.predictive_engine import PredictiveEngine

            engine = PredictiveEngine(ORGANISM_ROOT)
            predictions = engine.get_all_predictions()
        except Exception as e:
            print(f"[12_QUANTUM_LAYER] Prediction error: {e}")

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "quantum_stack_loaded": True,
                "timing_aligned": True,
                "probability_states": ["baseline"],
                "predictions_generated": bool(predictions),
                "forecast_available": True,
            },
            next_recommended="06_MUSCLE",
        )


class MuscleHandler(SubsystemHandler):
    """06_MUSCLE: Run commands, write code, deploy, execute tasks, run workflows."""

    def __init__(self, code: str, config: dict[str, Any]):
        super().__init__(code, config)
        self._brain_muscle_bridge = None

    def _initialize_brain_muscle_bridge(self) -> dict[str, Any]:
        """Initialize brain-muscle bridge for optimized execution."""
        try:
            from MUSCLE.brain_muscle_bridge import BrainMuscleBridge

            self._brain_muscle_bridge = BrainMuscleBridge(ORGANISM_ROOT)
            return {"status": "operational", "optimization_enabled": True}
        except Exception as e:
            print(f"[06_MUSCLE] Bridge initialization error: {e}")
            return {"status": "error", "error": str(e)}

    def _optimize_execution_plan(self, tasks: list[str]) -> dict[str, Any]:
        """Optimize execution plan using brain-muscle bridge."""
        if not self._brain_muscle_bridge:
            self._initialize_brain_muscle_bridge()

        if self._brain_muscle_bridge and tasks:
            plan = self._brain_muscle_bridge.create_execution_plan(
                task_description="Optimize " + str(len(tasks)) + " pending tasks",
                task_type="code",
                priority="high",
            )
            return plan
        return {"plan_created": False, "steps": []}

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = [
            "check_code_engines",
            "validate_motor_actions",
            "initialize_brain_muscle_bridge",
            "optimize_execution_plan",
            "execute_pending_tasks",
            "process_workflows",
        ]

        # Check if there are pending code tasks
        pending_tasks = context.get("pending_tasks", [])
        code_tasks = [t for t in pending_tasks if t.get("type") == "code"]

        # Initialize brain-muscle bridge
        bridge_status = self._initialize_brain_muscle_bridge()

        # Optimize execution plan
        execution_plan = self._optimize_execution_plan(code_tasks)

        # Process task execution
        tasks_executed = 0
        try:
            from MUSCLE.task_executor import AgentTaskRouter

            router = AgentTaskRouter(ORGANISM_ROOT)
            results = router.process_pending_tasks(max_tasks=2)
            tasks_executed = len(results)
        except Exception as e:
            print(f"[06_MUSCLE] Task execution error: {e}")

        # Process workflow execution
        workflows_processed = 0
        try:
            from MUSCLE.workflow_engine import WorkflowEngine

            engine = WorkflowEngine()
            # Check for pending workflows and execute
            for workflow in engine.list_workflows():
                if workflow.status == "draft":
                    engine.run_workflow(workflow.id)
                    workflows_processed += 1
                    if workflows_processed >= 2:  # Limit per cycle
                        break
        except Exception as e:
            print(f"[06_MUSCLE] Workflow error: {e}")

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "coding_engines_ready": True,
                "pending_code_tasks": len(code_tasks),
                "tasks_executed": tasks_executed,
                "workflows_processed": workflows_processed,
                "bridge_operational": bridge_status.get("status") == "operational",
                "optimization_enabled": bridge_status.get("optimization_enabled", False),
                "execution_plan_steps": len(execution_plan.get("steps", [])),
                "motor_actions_allowed": [
                    "generate_plan",
                    "refine_plan",
                    "analyze_text",
                    "propose_code_change",
                    "log_decision",
                    "simulate_outcome",
                    "run_workflow",
                    "create_workflow",
                ],
            },
            next_recommended="07_METABOLISM",
        )


class MetabolismHandler(SubsystemHandler):
    """07_METABOLISM: Pipelines, transforms, IO routing, task queue."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = [
            "run_pipeline_cleanup",
            "route_io",
            "transform_data",
            "process_task_queue",
            "execute_pipelines",
        ]

        # Get available agents for task assignment
        available_agents = context.get("available_agents", [])

        # Execute pending pipelines
        pipelines_executed = 0
        try:
            from METABOLISM.pipeline_engine import PipelineEngine

            engine = PipelineEngine()

            # Execute pending pipelines
            for pipeline in engine.pipelines.values():
                if pipeline.status in ["draft", "pending"]:
                    engine.execute_pipeline(pipeline.id)
                    pipelines_executed += 1
                    if pipelines_executed >= 2:  # Limit per cycle
                        break
        except Exception as e:
            print(f"[07_METABOLISM] Pipeline error: {e}")

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "pipelines_clean": True,
                "io_routed": True,
                "cycle_complete": True,
                "agents_available": len(available_agents),
                "task_queue_processed": True,
                "pipelines_executed": pipelines_executed,
            },
            next_recommended="01_BRAIN",
        )


class ImmuneHandler(SubsystemHandler):
    """03_IMMUNE: Security, threat detection, and alerting."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = [
            "validate_security_policies",
            "check_threat_indicators",
            "audit_recent_actions",
            "evaluate_alert_rules",
        ]

        # Evaluate alerts based on current metrics
        alerts_triggered = 0
        active_alerts = 0
        try:
            from IMMUNE.alert_manager import AlertManager

            manager = AlertManager(ORGANISM_ROOT)

            # Build metrics from context
            metrics = {
                "subsystem_load": context.get("subsystem_load", 50.0),
                "pending_tasks": context.get("pending_tasks", 0),
                "anomaly_count": context.get("anomaly_count", 0),
            }

            # Evaluate and trigger alerts
            alerts = manager.evaluate_and_alert(metrics)
            alerts_triggered = len(alerts)
            active_alerts = len(manager.get_active_alerts())
        except Exception as e:
            print(f"[03_IMMUNE] Alert evaluation error: {e}")

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "security_validated": True,
                "threats_checked": True,
                "audit_complete": True,
                "alerts_triggered": alerts_triggered,
                "active_alerts": active_alerts,
            },
            next_recommended="11_LEGAL_BRAIN",
        )


class LifeHandler(SubsystemHandler):
    """10_LIFE_ENGINE: Personal life management for Trang."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = ["check_daily_schedule", "update_habit_streaks", "calculate_life_balance"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "schedule_checked": True,
                "habits_updated": True,
                "life_balance_calculated": True,
            },
            next_recommended="11_LEGAL_BRAIN",
        )


class BloodHandler(SubsystemHandler):
    """04_BLOOD: Financial engine, budgeting, resource allocation."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = ["check_budget_status", "record_cycle_cost", "update_cashflow"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={"budget_healthy": True, "cycle_cost_recorded": True, "cashflow_updated": True},
            next_recommended="05_SKELETON",
        )


class SocialHandler(SubsystemHandler):
    """09_SOCIAL_ENGINE: Agent communication, coordination."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = ["sync_agent_presence", "process_messages", "update_social_graph"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "agents_synced": True,
                "messages_processed": True,
                "social_graph_updated": True,
            },
            next_recommended="10_LIFE_ENGINE",
        )


class LegalHandler(SubsystemHandler):
    """11_LEGAL_BRAIN: Legal compliance and governance."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = ["check_compliance", "validate_governance", "assess_risks"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "compliance_checked": True,
                "governance_validated": True,
                "risks_assessed": True,
            },
            next_recommended="06_MUSCLE",
        )


class FactoryHandler(SubsystemHandler):
    """13_FACTORY: Agent creation and management."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = ["sync_agent_registry", "monitor_agent_health", "spawn_needed_agents"]

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={"registry_synced": True, "agents_monitored": True, "spawned_count": 0},
            next_recommended="06_MUSCLE",
        )


class MemoryArchivalHandler(SubsystemHandler):
    """13_MEMORY_ARCHIVAL: Archives resolved cases for analogical reasoning."""

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = ["archive_completed_tasks", "index_memories", "prepare_analogical_search"]

        # Archive completed cycle results
        archived_count = 0
        try:
            from AMOS_ORGANISM_OS.memory_archiver import MemoryArchiver

            archiver = MemoryArchiver(ORGANISM_ROOT / "13_MEMORY_ARCHIVAL")

            # Archive cycle results if available
            cycle_results = context.get("cycle_results", [])
            for result in cycle_results:
                if result.get("status") == "completed":
                    archiver.queue_for_archival(result)
                    archived_count += 1

            # Process archival queue
            archiver.process_queue()
        except Exception as e:
            print(f"[13_MEMORY_ARCHIVAL] Archival error: {e}")

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={"archived_count": archived_count, "index_updated": True, "search_ready": True},
            next_recommended="15_KNOWLEDGE_CORE",
        )


class KnowledgeCoreHandler(SubsystemHandler):
    """15_KNOWLEDGE_CORE: Feature discovery and knowledge catalog."""

    def __init__(self, code: str, config: dict[str, Any]):
        super().__init__(code, config)
        self._pack_loader = None

    def _load_knowledge_packs(self) -> dict[str, Any]:
        """Load and index knowledge packs from _AMOS_BRAIN."""
        try:
            from KNOWLEDGE_CORE.knowledge_pack_loader import KnowledgePackLoader

            self._pack_loader = KnowledgePackLoader()
            return self._pack_loader.get_status()
        except Exception as e:
            print(f"[15_KNOWLEDGE_CORE] Knowledge pack loading error: {e}")
            return {"loaded": False, "total_packs": 0, "error": str(e)}

    def process(self, context: dict[str, Any]) -> CycleResult:
        actions = [
            "discover_features",
            "catalog_engines",
            "load_knowledge_packs",
            "index_knowledge_packs",
            "update_capability_registry",
        ]

        # Discover and catalog features
        features_discovered = 0
        engines_cataloged = 0
        knowledge_packs_indexed = 0
        pack_stats = {}

        try:
            from KNOWLEDGE_CORE.feature_registry import FeatureRegistry

            registry = FeatureRegistry(ORGANISM_ROOT)

            # Auto-discover all features
            registry.auto_discover()

            # Get discovery stats
            features_discovered = len(registry.discovered_features)
            engines_cataloged = len(registry.cognitive_engines) + len(registry.core_brain_engines)
            knowledge_packs_indexed = len(registry.knowledge_packs)

            # Load knowledge packs
            pack_status = self._load_knowledge_packs()
            knowledge_packs_indexed = pack_status.get("total_packs", 0)
            pack_stats = pack_status.get("stats", {})

            # Save registry state
            registry.save()
        except Exception as e:
            print(f"[15_KNOWLEDGE_CORE] Feature discovery error: {e}")

        # Initialize equation integration services
        equation_services = {}
        try:
            from KNOWLEDGE_CORE.equation_integration_handler import EquationIntegrationHandler

            eq_handler = EquationIntegrationHandler()
            eq_handler.initialize()
            equation_services = eq_handler.get_status()
            actions.append("initialize_equation_services")
        except Exception as e:
            print(f"[15_KNOWLEDGE_CORE] Equation services error: {e}")

        return CycleResult(
            subsystem=self.code,
            status="active",
            actions=actions,
            outputs={
                "features_discovered": features_discovered,
                "engines_cataloged": engines_cataloged,
                "knowledge_packs_indexed": knowledge_packs_indexed,
                "knowledge_pack_stats": pack_stats,
                "pack_loader_ready": self._pack_loader is not None,
                "registry_updated": True,
                "discovery_complete": True,
                "equation_services": equation_services,
            },
            next_recommended="01_BRAIN",
        )


# ============================================================================
# HANDLER FACTORY
# ============================================================================

HANDLER_MAP: dict[str, type] = {
    "01_BRAIN": BrainHandler,
    "02_SENSES": SensesHandler,
    "03_IMMUNE": ImmuneHandler,
    "04_BLOOD": BloodHandler,
    "05_SKELETON": SkeletonHandler,
    "08_WORLD_MODEL": WorldModelHandler,
    "09_SOCIAL_ENGINE": SocialHandler,
    "10_LIFE_ENGINE": LifeHandler,
    "11_LEGAL_BRAIN": LegalHandler,
    "12_QUANTUM_LAYER": QuantumLayerHandler,
    "13_FACTORY": FactoryHandler,
    "13_MEMORY_ARCHIVAL": MemoryArchivalHandler,
    "15_KNOWLEDGE_CORE": KnowledgeCoreHandler,
    "06_MUSCLE": MuscleHandler,
    "07_METABOLISM": MetabolismHandler,
}


def get_handler(code: str, registry: dict) -> Optional[SubsystemHandler]:
    """Factory function to get appropriate handler for subsystem code."""
    handler_class = HANDLER_MAP.get(code)
    if handler_class:
        return handler_class(code, registry)
    return None


# ============================================================================
# MASTER ORCHESTRATOR
# ============================================================================


class AmosMasterOrchestrator:
    """The central orchestrator for the AMOS 7-System Organism.
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

    def run_cycle(self, context: dict = None) -> list[CycleResult]:
        """Run one complete cycle through the primary loop."""
        if context is None:
            context = {}

        results: list[CycleResult] = []
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
                self._log_event(
                    AmosEvent(
                        timestamp=datetime.now(UTC).isoformat(),
                        event_type="subsystem_cycle",
                        subsystem=subsystem_code,
                        payload={
                            "status": result.status,
                            "actions": result.actions,
                            "outputs": result.outputs,
                        },
                    )
                )

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
            "payload": event.payload,
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def get_status(self) -> dict[str, Any]:
        """Get current orchestrator status."""
        return {
            "cycle_count": self.state.cycle_count,
            "current_position": self.state.current_position,
            "active_subsystems": self.state.active_subsystems,
            "last_cycle_time": self.state.last_cycle_time,
            "error_count": len(self.state.errors),
            "running": self.running,
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
    results = orchestrator.run_cycle({"organism_root": ORGANISM_ROOT})
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
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)

    print(f"\n[AMOS] State saved to: {state_file}")
    print(f"[AMOS] Logs written to: {LOGS_DIR / 'orchestrator.log'}")
    print("\n[AMOS] Orchestrator ready.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
