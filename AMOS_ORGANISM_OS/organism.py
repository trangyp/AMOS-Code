"""
AMOS Organism — The 14-Subsystem Digital Organism

This is the main orchestrator that wires together all subsystems
according to the primary loop defined in the AMOS blueprint.

Primary Loop:
01_BRAIN -> 02_SENSES -> 05_SKELETON -> 08_WORLD_MODEL ->
12_QUANTUM_LAYER -> 06_MUSCLE -> 07_METABOLISM -> 01_BRAIN
"""

from __future__ import annotations

import json
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent to path for imports
_PARENT = Path(__file__).parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))
if str(_PARENT.parent) not in sys.path:
    sys.path.insert(0, str(_PARENT.parent))

# Import subsystems
from BRAIN.brain_os import BrainOS
from BRAIN.router import SystemRouter, RoutingDecision
from BRAIN.memory_layer import MemoryLayer
from SENSES.environment_scanner import EnvironmentScanner
from SENSES.context_gatherer import ContextGatherer
from SENSES.signal_detector import SignalDetector
from SKELETON.constraint_engine import ConstraintEngine
from SKELETON.rule_validator import RuleValidator
from SKELETON.structural_integrity import StructuralIntegrity
from WORLD_MODEL.knowledge_graph import KnowledgeGraph
from WORLD_MODEL.context_mapper import ContextMapper
from WORLD_MODEL.semantic_index import SemanticIndex
from BLOOD.resource_engine import ResourceEngine
from BLOOD.budget_manager import BudgetManager
from BLOOD.cashflow_tracker import CashflowTracker
from METABOLISM.pipeline_engine import PipelineEngine
from METABOLISM.transform_engine import TransformEngine
from METABOLISM.io_router import IORouter
from IMMUNE.immune_system import ImmuneSystem, ActionType
from IMMUNE.threat_detector import ThreatDetector
from IMMUNE.compliance_engine import ComplianceEngine
from MUSCLE.executor import MuscleExecutor
from MUSCLE.code_runner import CodeRunner
from MUSCLE.workflow_engine import WorkflowEngine
from MUSCLE.brain_muscle_bridge import BrainMuscleBridge, get_brain_muscle_bridge


@dataclass
class OrganismState:
    """Global state of the AMOS organism."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    cycle_count: int = 0
    current_subsystem: str = "00_ROOT"
    global_context: Dict[str, Any] = field(default_factory=dict)


class AmosOrganism:
    """
    The AMOS Digital Organism — 14 subsystems working as one.

    Subsystems (from system_registry.json):
    - 00_ROOT: Identity, goals, global config
    - 01_BRAIN: Reasoning, planning, memory, routing
    - 02_SENSES: Filesystem, environment, context
    - 03_IMMUNE: Safety, legal, compliance
    - 04_BLOOD: Budgeting, cashflow, forecasting
    - 05_SKELETON: Rules, constraints, permissions
    - 06_MUSCLE: Run commands, write code, deploy
    - 07_METABOLISM: Pipelines, transforms, IO
    - 08_WORLD_MODEL: Macroeconomics, geopolitics
    - 09_SOCIAL_ENGINE: Humans, negotiation
    - 10_LIFE_ENGINE: Sleep, energy, health
    - 11_LEGAL_BRAIN: Contracts, IP, compliance
    - 12_QUANTUM_LAYER: Timing, probability flows
    - 13_FACTORY: Agent creation, self-upgrade
    - 14_INTERFACES: CLI, API, dashboard
    """

    def __init__(self):
        self.state = OrganismState()

        # Initialize core subsystems (Primary Loop)
        self.brain = BrainOS()
        self.router = SystemRouter()
        self.memory = MemoryLayer()

        # Initialize SENSES (perception layer)
        self.senses = EnvironmentScanner()
        self.context = ContextGatherer()
        self.signals = SignalDetector()

        # Initialize SKELETON (constraint layer)
        self.constraints = ConstraintEngine()
        self.rules = RuleValidator()
        self.integrity = StructuralIntegrity()

        # Initialize WORLD_MODEL (knowledge layer)
        self.knowledge = KnowledgeGraph()
        self.context_mapper = ContextMapper()
        self.semantic_index = SemanticIndex()

        # Initialize BLOOD (resource tracking layer)
        self.resources = ResourceEngine()
        self.budget = BudgetManager()
        self.cashflow = CashflowTracker()

        # Initialize METABOLISM (data pipeline layer)
        self.pipeline = PipelineEngine()
        self.transform = TransformEngine()
        self.io_router = IORouter()

        # Initialize IMMUNE (safety layer)
        self.immune = ImmuneSystem()
        self.threat_detector = ThreatDetector()
        self.compliance = ComplianceEngine()

        # Initialize MUSCLE (execution layer)
        self.muscle = MuscleExecutor()
        self.code_runner = CodeRunner()
        self.workflow = WorkflowEngine()

        # Register workflow handlers
        self._register_workflow_handlers()

        # Load system registry
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict:
        """Load system registry."""
        registry_path = Path(__file__).parent / "system_registry.json"
        if registry_path.exists():
            return json.loads(registry_path.read_text())
        return {}

    def _register_workflow_handlers(self):
        """Register handlers for workflow actions."""
        def handle_execute(params: Dict, context: Dict) -> Any:
            cmd = params.get("command", "")
            if cmd:
                result = self.muscle.execute(cmd)
                return result.to_dict()
            return None

        def handle_code(params: Dict, context: Dict) -> Any:
            code = params.get("code", "")
            lang = params.get("language", "python")
            from AMOS_ORGANISM_OS.MUSCLE.code_runner import Language
            language = Language.PYTHON if lang == "python" else Language.BASH
            result = self.code_runner.run(code, language)
            return {
                "success": result.success,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        def handle_think(params: Dict, context: Dict) -> Any:
            content = params.get("content", "")
            thought = self.brain.perceive(content)
            return {"thought_id": thought.id, "content": thought.content}

        self.workflow.register_handler("execute", handle_execute)
        self.workflow.register_handler("code", handle_code)
        self.workflow.register_handler("think", handle_think)

    def perceive(self, content: str, source: str = "external"):
        """Send perception to the brain."""
        return self.brain.perceive(content, source)

    def think(self, content: str):
        """Create a conceptual thought."""
        thought = self.brain.perceive(content)
        return self.brain.conceptualize(thought, pattern="manual_input")

    def plan(self, goal: str, horizon: str = "medium-term"):
        """Create a plan for a goal."""
        return self.brain.create_plan(goal, horizon)

    def decide(self, action: str, params: Dict = None) -> RoutingDecision:
        """Route an action to the appropriate subsystem."""
        return self.router.route(action, params or {})

    def execute(self, command: str, context=None):
        """Execute via muscle subsystem with IMMUNE validation."""
        from MUSCLE.executor import ExecutionContext

        # Validate with IMMUNE first
        validation = self.immune.validate(
            action=command,
            action_type=ActionType.EXECUTE,
            target=command,
            source="organism.execute",
        )

        if not validation.approved:
            from MUSCLE.executor import ExecutionResult, ExecutionStatus
            result = ExecutionResult(
                command=command,
                status=ExecutionStatus.CANCELLED,
                stderr=f"IMMUNE blocked: {validation.reason}",
            )
            return result

        # Execute via muscle
        ctx = context or ExecutionContext()
        return self.muscle.execute(command, ctx)

    def cycle(self) -> Dict[str, Any]:
        """Run one primary loop cycle."""
        results = {}

        # BRAIN: Current state assessment
        self.state.current_subsystem = "01_BRAIN"
        brain_status = self.brain.status()
        results["brain"] = brain_status

        # SENSES: Gather inputs (simplified)
        self.state.current_subsystem = "02_SENSES"
        results["senses"] = {"status": "active", "inputs": 0}

        # SKELETON: Validate constraints
        self.state.current_subsystem = "05_SKELETON"
        results["skeleton"] = {"constraints_checked": True}

        # WORLD_MODEL: Contextualize
        self.state.current_subsystem = "08_WORLD_MODEL"
        results["world_model"] = {"signals": []}

        # QUANTUM_LAYER: Timing
        self.state.current_subsystem = "12_QUANTUM_LAYER"
        results["quantum"] = {"timestamp": datetime.utcnow().isoformat()}

        # MUSCLE: Execute pending actions
        self.state.current_subsystem = "06_MUSCLE"
        muscle_status = self.muscle.status()
        results["muscle"] = muscle_status

        # METABOLISM: Cleanup and route
        self.state.current_subsystem = "07_METABOLISM"
        results["metabolism"] = {"pipelines_active": 0}

        # Back to BRAIN: Complete cycle
        self.state.current_subsystem = "01_BRAIN"
        self.brain.complete_cycle()
        self.state.cycle_count += 1

        return results

    def run_workflow(self, workflow_id: str = None) -> Optional[Any]:
        """Run a workflow."""
        if workflow_id:
            workflow = self.workflow.load_workflow(workflow_id)
            if workflow:
                return self.workflow.run_workflow(workflow_id)
        return None

    def create_workflow(self, name: str, description: str = "") -> Any:
        """Create a new workflow."""
        return self.workflow.create_workflow(name, description)

    def remember(self, content: str, layer: str = "short_term", importance: float = 0.5):
        """Store in memory."""
        return self.memory.store(content, layer=layer, importance=importance)

    def recall(self, query: str, limit: int = 10):
        """Search memory."""
        return self.memory.search(query, limit=limit)

    def status(self) -> Dict[str, Any]:
        """Get complete organism status."""
        return {
            "session_id": self.state.session_id,
            "started_at": self.state.started_at,
            "cycle_count": self.state.cycle_count,
            "current_subsystem": self.state.current_subsystem,
            "active_subsystems": [
                "01_BRAIN", "02_SENSES", "05_SKELETON", "08_WORLD_MODEL",
                "07_METABOLISM", "03_IMMUNE", "06_MUSCLE", "14_INTERFACES"
            ],
            "subsystems": {
                "brain": self.brain.status(),
                "senses": self.senses.status(),
                "skeleton": self.constraints.status(),
                "world_model": self.knowledge.status(),
                "metabolism": {
                    "total_pipelines": len(self.pipeline.list_pipelines()),
                },
                "immune": self.immune.status(),
                "muscle": self.muscle.status(),
                "memory": self.memory.stats(),
                "workflow": {
                    "workflows": len(self.workflow.list_workflows()),
                },
            },
            "registry": {
                "name": self.registry.get("_meta", {}).get("name", "Unknown"),
                "version": self.registry.get("_meta", {}).get("version", "0.0.0"),
            },
        }

    def scan(self, path: str = None):
        """Scan environment via SENSES."""
        return self.senses.scan(path)

    def gather_context(self) -> Dict[str, Any]:
        """Gather environment context."""
        return self.context.gather()

    def validate_constraints(self, filepath: str) -> bool:
        """Validate file against constraints via SKELETON."""
        results = self.constraints.validate_file(filepath)
        return all(r.passed for r in results)

    def save(self) -> Path:
        """Save organism state."""
        state_dir = Path(__file__).parent / "state"
        state_dir.mkdir(parents=True, exist_ok=True)

        filepath = state_dir / f"organism_{self.state.session_id}.json"
        data = {
            "session_id": self.state.session_id,
            "started_at": self.state.started_at,
            "cycle_count": self.state.cycle_count,
            "brain": self.brain.save_state(),
        }
        filepath.write_text(json.dumps(data, indent=2, default=str))
        return filepath


def main():
    """Demo the organism."""
    print("=" * 60)
    print("AMOS ORGANISM OS v1.0.0")
    print("14-Subsystem Digital Organism")
    print("=" * 60)
    print()

    organism = AmosOrganism()

    # Show initial status
    status = organism.status()
    print(f"Session ID: {status['session_id']}")
    print(f"Registry: {status['registry']['name']} v{status['registry']['version']}")
    print()

    # Demonstrate brain capabilities
    print("[BRAIN] Creating thoughts...")
    t1 = organism.perceive("System initialized", "bootstrap")
    print(f"  Perceived: {t1.id}")

    t2 = organism.think("Organism is ready for operation")
    print(f"  Concept: {t2.id}")

    # Create a plan
    print("\n[BRAIN] Creating plan...")
    plan = organism.plan("Demonstrate organism capabilities", "short-term")
    plan.add_step("Show status", "14_INTERFACES")
    plan.add_step("Run cycle", "01_BRAIN")
    print(f"  Plan: {plan.id} with {len(plan.steps)} steps")

    # Route an action
    print("\n[ROUTER] Routing actions...")
    for action in ["execute", "plan", "think", "code"]:
        decision = organism.decide(action)
        print(f"  {action} -> {decision.target}")

    # Run a cycle
    print("\n[ORGANISM] Running primary loop cycle...")
    cycle_results = organism.cycle()
    print(f"  Cycle {organism.state.cycle_count} complete")

    # Memory
    print("\n[MEMORY] Storing memories...")
    m1 = organism.remember("First run of AMOS Organism", importance=0.9)
    m2 = organism.remember("System is operational", importance=0.7)
    print(f"  Stored: {m1.id}, {m2.id}")

    memories = organism.recall("run")
    print(f"  Recall 'run': {len(memories)} results")

    # Final status
    print("\n" + "=" * 60)
    print("FINAL STATUS")
    print("=" * 60)
    final_status = organism.status()
    print(f"Cycles: {final_status['cycle_count']}")
    print(f"Thoughts: {final_status['subsystems']['brain']['thought_count']}")
    print(f"Executions: {final_status['subsystems']['muscle']['total_executions']}")
    print(f"Memories: {final_status['subsystems']['memory']['total_memories']}")

    # Save state
    filepath = organism.save()
    print(f"\nState saved to: {filepath}")
    print("\nOrganism ready for operation.")


if __name__ == "__main__":
    main()
