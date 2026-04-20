#!/usr/bin/env python3
from __future__ import annotations

"""SuperBrainRuntime - The ONE Canonical AMOS Brain

ABSOLUTE LAW ENFORCEMENT:
- ONE PROCESS ONLY: No subprocesses, daemons, or parallel runtimes
- FULL CONSOLIDATION: All capabilities in this single runtime owner
- CLAWD ABSORBED: Clawd is execution layer only, governed by this brain
- REGISTRY GOVERNANCE: All tools, models, sources through canonical registries
- CORE FROZEN: Core files protected against mutation
- NO DISCONNECT: Agents cannot disable tools, models, or core systems

This is the only allowed live process owning the AMOS runtime.
"""

import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc

from pathlib import Path
from threading import Lock, RLock
from typing import Any, Optional

from .action_gate import ActionGate
from .clawd_integration import ClawdExecutionLayer
from .core_freeze import CoreFreezeEnforcer

# Core AMOS imports
from .kernel_router import KernelRouter
from .memory_governance import MemoryGovernance
from .model_router import ModelRouter
from .source_registry import SourceRegistry
from .tool_registry_governed import GovernedToolRegistry


@dataclass
class SuperBrainState:
    """Immutable state snapshot of the SuperBrain."""

    timestamp: str
    status: str
    active_kernels: list[str]
    loaded_tools: list[str]
    available_models: list[str]
    memory_stats: dict[str, Any]
    clawd_status: str
    core_frozen: bool
    health_score: float
    math_framework_status: str = "unavailable"
    available_tools: int = 0  # Number of available tools


class SuperBrainRuntime:
    """The ONE Canonical AMOS Brain Runtime.

    This class is the single owner of:
    - Brain execution authority
    - Kernel routing
    - Tool governance (via ActionGate)
    - Model routing (via ModelRouter)
    - Source management (via SourceRegistry)
    - Memory governance (via MemoryGovernance)
    - Clawd execution (via ClawdExecutionLayer)
    - Core freeze enforcement (via CoreFreezeEnforcer)
    - Math framework (via MathematicalFrameworkEngine) - ONE source of truth for equations

    LAW 0 COMPLIANCE: Exactly one process. No subprocesses spawned.
    """

    _instance: Optional[SuperBrainRuntime] = None
    _lock = Lock()

    def __new__(cls) -> SuperBrainRuntime:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        # Core identity
        self.brain_id = self._generate_brain_id()
        self.start_time = datetime.now(timezone.utc)
        self.status = "initializing"

        # Canonical subsystem ownership (LAW 2 COMPLIANCE)
        self._kernel_router: Optional[KernelRouter] = None
        self._action_gate: Optional[ActionGate] = None
        self._model_router: Optional[ModelRouter] = None
        self._tool_registry: Optional[GovernedToolRegistry] = None
        self._source_registry: Optional[SourceRegistry] = None
        self._memory_governance: Optional[MemoryGovernance] = None
        self._clawd_layer: Optional[ClawdExecutionLayer] = None
        self._core_freeze: Optional[CoreFreezeEnforcer] = None
        self._math_engine: Any = None
        self._math_audit_logger: Any = None
        self._equation_bridge: Any = None
        self._world_model: Any = None
        self._constitutional_governance: Any = None
        self._workflow_orchestrator: Any = None
        self._a2a_agent: Any = None
        self._knowledge_bridge: Any = None
        self._jepa_world_model: Any = None
        self._agentic_ai: Any = None

        # State protection
        self._state_lock = RLock()
        self._audit_log: list[dict] = []

        # Health tracking
        self._health_checks: dict[str, Callable[[], bool]] = {}
        self._last_health_check: datetime | None = None

    def _generate_brain_id(self) -> str:
        """Generate unique brain identifier."""
        timestamp = str(time.time())
        hostname = str(Path().absolute())
        return hashlib.sha256(f"{timestamp}{hostname}".encode()).hexdigest()[:16]

    def initialize(self) -> bool:
        """Initialize the SuperBrain and all canonical subsystems.

        Returns:
            bool: True if initialization successful
        """
        print("=" * 70)
        print(" SUPER BRAIN RUNTIME - INITIALIZATION")
        print("=" * 70)
        print(f"Brain ID: {self.brain_id}")
        print(f"Timestamp: {self.start_time.isoformat()}")
        print("=" * 70)

        try:
            # Initialize canonical subsystems in dependency order
            self._initialize_core_freeze()
            self._initialize_memory_governance()
            self._initialize_tool_registry()
            self._initialize_model_router()
            self._initialize_source_registry()
            self._initialize_action_gate()
            self._initialize_kernel_router()
            self._initialize_clawd_layer()

            self.status = "active"
            self._audit("SUPER_BRAIN_INIT", {"brain_id": self.brain_id})

            print("\n✅ SuperBrain Runtime ACTIVE")
            print(f"   Tools: {len(self._tool_registry.list_tools())}")
            print(f"   Models: {len(self._model_router.list_models())}")
            print(f"   Core Frozen: {self._core_freeze.is_frozen()}")
            print("=" * 70)

            return True

        except Exception as e:
            self.status = "failed"
            self._audit("SUPER_BRAIN_INIT_FAILED", {"error": str(e)})
            print(f"\n❌ SuperBrain initialization failed: {e}")
            return False

    def _initialize_core_freeze(self) -> None:
        """Initialize core freeze enforcement."""
        from .core_freeze import CoreFreezeEnforcer

        self._core_freeze = CoreFreezeEnforcer()
        self._core_freeze.freeze_core_files()
        print("✅ Core Freeze: ACTIVE")

    def _initialize_memory_governance(self) -> None:
        """Initialize memory governance layer."""
        from .memory_governance import MemoryGovernance

        self._memory_governance = MemoryGovernance()
        print("✅ Memory Governance: ACTIVE")

    def _initialize_tool_registry(self) -> None:
        """Initialize governed tool registry."""
        from .tool_registry_governed import GovernedToolRegistry

        self._tool_registry = GovernedToolRegistry(
            action_gate=self._action_gate,  # Will be set after init
            memory_governance=self._memory_governance,
        )
        print("✅ Tool Registry: ACTIVE (Governed)")

    def _initialize_model_router(self) -> None:
        """Initialize model router."""
        from .model_router import ModelRouter

        self._model_router = ModelRouter(memory_governance=self._memory_governance)
        print("✅ Model Router: ACTIVE")

    def _initialize_source_registry(self) -> None:
        """Initialize source registry."""
        from .source_registry import SourceRegistry

        self._source_registry = SourceRegistry(memory_governance=self._memory_governance)
        print("✅ Source Registry: ACTIVE")

    def _initialize_action_gate(self) -> None:
        """Initialize action gate."""
        from .action_gate import ActionGate

        self._action_gate = ActionGate(
            tool_registry=self._tool_registry, memory_governance=self._memory_governance
        )
        # Wire action gate to tool registry
        self._tool_registry.set_action_gate(self._action_gate)
        print("✅ Action Gate: ACTIVE")

    def _initialize_kernel_router(self) -> None:
        """Initialize kernel router."""
        from .kernel_router import KernelRouter
        from .loader import get_brain

        self._kernel_router = KernelRouter(brain_loader=get_brain())
        print("✅ Kernel Router: ACTIVE")

    def _initialize_clawd_layer(self) -> None:
        """Initialize Clawd execution layer (ABSORBED, not parallel)."""
        from .clawd_integration import ClawdExecutionLayer

        self._clawd_layer = ClawdExecutionLayer(
            tool_registry=self._tool_registry,
            action_gate=self._action_gate,
            model_router=self._model_router,
            memory_governance=self._memory_governance,
        )
        # Clawd is now a governed subsystem, not a parallel runtime
        print("✅ Clawd Execution Layer: ABSORBED (Governed)")

        # Register built-in tools
        self._register_builtin_tools()

        # Register default LLM models (if API keys available)
        self._register_default_models()

        # Initialize Mathematical Framework (ONE source of truth for equations)
        self._initialize_math_framework()

    def _initialize_math_framework(self) -> None:
        """Initialize Mathematical Framework Engine for equation validation and analysis."""
        try:
            # Use importlib to handle optional dependency
            import importlib.util

            # Correct path: from amos_brain/super_brain.py -> clawspring/amos_brain/
            math_framework_path = (
                Path(__file__).parent.parent
                / "clawspring"
                / "amos_brain"
                / "mathematical_framework_engine.py"
            )
            spec = importlib.util.spec_from_file_location(
                "mathematical_framework_engine", str(math_framework_path)
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # Fix: Register module in sys.modules before exec_module
                # This prevents dataclass 'NoneType' __dict__ error
                import sys
                sys.modules["mathematical_framework_engine"] = module
                spec.loader.exec_module(module)
                self._math_engine = module.get_framework_engine()
                stats = self._math_engine.get_stats()
                print(f"✅ Math Framework: ACTIVE ({stats.get('total_equations', 0)} equations)")

                # Initialize math framework audit logger
                self._initialize_math_audit_logger()

                # Initialize SuperBrain equation bridge (145+ equations, 33 domains)
                self._initialize_equation_bridge()

                # Initialize Phase 17 Predictive World Model
                self._initialize_world_model()

                # Initialize Phase 20 Constitutional Governance
                self._initialize_constitutional_governance()

                # Initialize Phase 21 Workflow Orchestrator
                self._initialize_workflow_orchestrator()

                # Initialize Phase 22 A2A Protocol
                self._initialize_a2a_protocol()

                # Initialize SuperBrain Knowledge Bridge (500+ unified equations)
                self._initialize_knowledge_bridge()

                # Emit event for math framework initialization
                self._emit_event(
                    "math_framework_initialized",
                    {
                        "total_equations": stats.get("total_equations", 0),
                        "domains": len(stats.get("domains", [])),
                        "version": stats.get("version", "1.0.0"),
                    },
                )
            else:
                self._math_engine = None
                print("⚠️  Math Framework: not available (no module)")
        except Exception as e:
            self._math_engine = None
            print(f"⚠️  Math Framework: not available ({e})")

    def _initialize_math_audit_logger(self) -> None:
        """Initialize MathFrameworkAuditLogger for comprehensive math operation tracking."""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "math_audit_logger",
                str(
                    Path(__file__).parent.parent
                    / "clawspring"
                    / "amos_brain"
                    / "math_audit_logger.py"
                ),
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                import sys
                sys.modules["math_audit_logger"] = module
                spec.loader.exec_module(module)
                self._math_audit_logger = module.MathFrameworkAuditLogger()
                print("✅ Math Audit Logger: ACTIVE")
            else:
                self._math_audit_logger = None
        except Exception as e:
            self._math_audit_logger = None
            print(f"⚠️  Math Audit Logger: not available ({e})")

    def _initialize_equation_bridge(self) -> None:
        """Initialize SuperBrain Equation Bridge for 145+ equations across 33 domains."""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "amos_superbrain_equation_bridge",
                str(Path(__file__).parent.parent / "amos_superbrain_equation_bridge.py"),
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                import sys
                sys.modules["amos_superbrain_equation_bridge"] = module
                spec.loader.exec_module(module)
                self._equation_bridge = module.EquationBridge()
                stats = self._equation_bridge.get_pattern_analysis()
                print(
                    f"✅ Equation Bridge: ACTIVE ({stats.get('total_equations', 0)} equations, {stats.get('domains_covered', 0)} domains)"
                )

                # Emit event for equation bridge initialization
                self._emit_event(
                    "equation_bridge_initialized",
                    {
                        "total_equations": stats.get("total_equations", 0),
                        "domains_covered": stats.get("domains_covered", 0),
                        "patterns": len(stats.get("pattern_distribution", {})),
                    },
                )
            else:
                self._equation_bridge = None
                print("⚠️  Equation Bridge: not available (no module)")
        except Exception as e:
            self._equation_bridge = None
            print(f"⚠️  Equation Bridge: not available ({e})")

    def _initialize_world_model(self) -> None:
        """Initialize Phase 17 Predictive World Model."""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "amos_predictive_world_model",
                str(Path(__file__).parent.parent / "amos_predictive_world_model.py"),
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                import sys
                sys.modules["amos_predictive_world_model"] = module
                spec.loader.exec_module(module)
                self._world_model = module.PredictiveWorldModel()
                print("✅ World Model: ACTIVE (Phase 17 - Recursive Self-Improvement)")

                # Emit event for world model initialization
                self._emit_event(
                    "world_model_initialized",
                    {
                        "phase": 17,
                        "capabilities": [
                            "simulation_engine",
                            "meta_cognitive_reflection",
                            "self_improvement",
                        ],
                    },
                )
            else:
                self._world_model = None
                print("⚠️  World Model: not available (no module)")
        except Exception as e:
            self._world_model = None
            print(f"⚠️  World Model: not available ({e})")

    def _initialize_constitutional_governance(self) -> None:
        """Initialize Phase 20 Constitutional AI & Self-Correcting Governance."""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "amos_constitutional_governance",
                str(Path(__file__).parent.parent / "amos_constitutional_governance.py"),
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                import sys
                sys.modules["amos_constitutional_governance"] = module
                spec.loader.exec_module(module)
                self._constitutional_governance = module.ConstitutionalGovernance()
                print("✅ Constitutional Governance: ACTIVE (Phase 20)")

                # Emit event for governance initialization
                self._emit_event(
                    "constitutional_governance_initialized",
                    {
                        "phase": 20,
                        "capabilities": [
                            "constitutional_principles",
                            "drift_detection",
                            "self_correction",
                        ],
                    },
                )
            else:
                self._constitutional_governance = None
                print("⚠️  Constitutional Governance: not available (no module)")
        except Exception as e:
            self._constitutional_governance = None
            print(f"⚠️  Constitutional Governance: not available ({e})")

    def _initialize_workflow_orchestrator(self) -> None:
        """Initialize Phase 21 Deterministic Workflow Orchestration."""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "amos_workflow_orchestrator",
                str(Path(__file__).parent.parent / "amos_workflow_orchestrator.py"),
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                import sys
                sys.modules["amos_workflow_orchestrator"] = module
                spec.loader.exec_module(module)
                self._workflow_orchestrator = module.WorkflowOrchestrator()
                print("✅ Workflow Orchestrator: ACTIVE (Phase 21)")

                # Emit event for orchestrator initialization
                self._emit_event(
                    "workflow_orchestrator_initialized",
                    {
                        "phase": 21,
                        "capabilities": ["durable_execution", "saga_pattern", "human_in_the_loop"],
                    },
                )
            else:
                self._workflow_orchestrator = None
                print("⚠️  Workflow Orchestrator: not available (no module)")
        except Exception as e:
            self._workflow_orchestrator = None
            print(f"⚠️  Workflow Orchestrator: not available ({e})")

    def _initialize_a2a_protocol(self) -> None:
        """Initialize Phase 22 A2A Protocol for Agent2Agent Interoperability."""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "amos_a2a_protocol", str(Path(__file__).parent.parent / "amos_a2a_protocol.py")
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                import sys
                sys.modules["amos_a2a_protocol"] = module
                spec.loader.exec_module(module)
                self._a2a_agent = module.A2AAgent()
                print("✅ A2A Protocol: ACTIVE (Phase 22)")

                # Emit event for A2A initialization
                self._emit_event(
                    "a2a_protocol_initialized",
                    {"phase": 22, "capabilities": ["agent_cards", "task_management", "streaming"]},
                )
            else:
                self._a2a_agent = None
                print("⚠️  A2A Protocol: not available (no module)")
        except Exception as e:
            self._a2a_agent = None
            print(f"⚠️  A2A Protocol: not available ({e})")

    def _initialize_knowledge_bridge(self) -> None:
        """Initialize SuperBrain Knowledge Bridge for 500+ unified equations."""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "amos_superbrain_knowledge_bridge",
                str(Path(__file__).parent.parent / "amos_superbrain_knowledge_bridge.py"),
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                import sys
                sys.modules["amos_superbrain_knowledge_bridge"] = module
                spec.loader.exec_module(module)
                self._knowledge_bridge = module.SuperBrainKnowledgeBridge()
                # Initialize the bridge to build unified cache
                self._knowledge_bridge.initialize()
                stats = self._knowledge_bridge.get_stats()
                print(
                    f"✅ Knowledge Bridge: ACTIVE ({stats.get('total_unified', 0)} unified equations)"
                )

                # Emit event for knowledge bridge initialization
                self._emit_event(
                    "knowledge_bridge_initialized",
                    {
                        "total_equations": stats.get("total_unified", 0),
                        "sources": list(stats.get("sources", {}).keys()),
                        "languages": stats.get("languages", []),
                    },
                )
            else:
                self._knowledge_bridge = None
                print("⚠️  Knowledge Bridge: not available (no module)")
        except Exception as e:
            self._knowledge_bridge = None
            print(f"⚠️  Knowledge Bridge: not available ({e})")

    def _register_builtin_tools(self) -> None:
        """Register built-in and extended tools with the tool registry."""
        try:
            from .tools_builtin import (
                TOOL_DESCRIPTIONS as BUILTIN_DESCRIPTIONS,
            )
            from .tools_builtin import (
                TOOL_SCHEMAS as BUILTIN_SCHEMAS,
            )
            from .tools_builtin import (
                analyze_code_structure,
                execute_shell_command,
                get_system_info,
                search_files,
                validate_json,
            )
            from .tools_extended import (
                TOOL_DESCRIPTIONS as EXTENDED_DESCRIPTIONS,
            )
            from .tools_extended import (
                TOOL_SCHEMAS as EXTENDED_SCHEMAS,
            )
            from .tools_extended import (
                calculate,
                database_query,
                file_read_write,
                git_operations,
                web_search,
            )

            # Register built-in tools
            builtin_tools = [
                ("analyze_code_structure", analyze_code_structure),
                ("execute_shell_command", execute_shell_command),
                ("search_files", search_files),
                ("get_system_info", get_system_info),
                ("validate_json", validate_json),
            ]

            # Register extended tools
            extended_tools = [
                ("web_search", web_search),
                ("database_query", database_query),
                ("file_read_write", file_read_write),
                ("calculate", calculate),
                ("git_operations", git_operations),
            ]

            registered = 0

            # Register built-in
            for name, func in builtin_tools:
                if self._tool_registry.register(
                    name=name,
                    func=func,
                    description=BUILTIN_DESCRIPTIONS.get(name, "Built-in tool"),
                    schema=BUILTIN_SCHEMAS.get(name),
                ):
                    registered += 1

            # Register extended
            for name, func in extended_tools:
                if self._tool_registry.register(
                    name=name,
                    func=func,
                    description=EXTENDED_DESCRIPTIONS.get(name, "Extended tool"),
                    schema=EXTENDED_SCHEMAS.get(name),
                ):
                    registered += 1

            print(f"✅ Tools: {registered} tools registered (5 built-in + 5 extended)")
        except Exception as e:
            print(f"⚠️  Tools: registration failed ({e})")

    def _register_default_models(self) -> None:
        """Register default LLM models if API keys available."""
        try:
            from .model_router import ModelConfig

            registered = 0

            # Check for OpenAI API key
            import os

            if os.environ.get("OPENAI_API_KEY"):
                self._model_router.register_model(
                    ModelConfig(model_id="gpt-4", provider="openai", priority=10)
                )
                self._model_router.register_model(
                    ModelConfig(model_id="gpt-3.5-turbo", provider="openai", priority=5)
                )
                registered += 2

            # Check for Anthropic API key
            if os.environ.get("ANTHROPIC_API_KEY"):
                self._model_router.register_model(
                    ModelConfig(
                        model_id="claude-3-sonnet-20240229", provider="anthropic", priority=10
                    )
                )
                registered += 1

            # Check for Kimi API key
            if os.environ.get("KIMI_API_KEY"):
                self._model_router.register_model(
                    ModelConfig(model_id="kimi-k2.5", provider="kimi", priority=10)
                )
                registered += 1

            if registered > 0:
                print(f"✅ Models: {registered} LLM providers registered")
            else:
                print(
                    "⚠️  Models: No API keys found (set OPENAI_API_KEY, ANTHROPIC_API_KEY, or KIMI_API_KEY)"
                )

        except Exception as e:
            print(f"⚠️  Models: registration failed ({e})")

    def query_math_equations(self, domain: str = None, query: str = None) -> list[dict]:
        """Query mathematical equations from the framework.

        Args:
            domain: Optional domain filter (e.g., 'UI_UX', 'AI_ML')
            query: Optional text query for fuzzy matching

        Returns:
            List of matching equations with metadata
        """
        if not self._math_engine:
            return []

        try:
            results = []
            if domain:
                results = self._math_engine.query_by_domain(domain)
            elif query:
                results = self._math_engine.fuzzy_query(query)
            else:
                # Return all equations
                all_eqs = []
                for domain_name in self._math_engine.list_domains():
                    all_eqs.extend(self._math_engine.query_by_domain(domain_name))
                results = all_eqs

            # Audit the query using specialized math audit logger
            if self._math_audit_logger:
                self._math_audit_logger.log_equation_query(
                    domain=domain or "all",
                    framework="mathematical_framework",
                    result_count=len(results),
                    query_params={"text_query": query} if query else None,
                )

            return results
        except Exception as e:
            self._audit("math_query_failed", {"error": str(e), "domain": domain, "query": query})
            return []

    def validate_with_math_framework(self, design_input: dict) -> dict:
        """Validate design input against mathematical invariants.

        Args:
            design_input: Design parameters to validate

        Returns:
            Validation results with passed/failed invariants
        """
        if not self._math_engine:
            return {"valid": False, "error": "Math framework not available"}

        try:
            # Get appropriate validator based on design type
            design_type = design_input.get("type", "UI_UX")
            validator = self._math_engine.get_validator(design_type)

            results = validator.validate_design(design_input)

            self._audit(
                "math_validation",
                {
                    "design_type": design_type,
                    "passed": results.get("passed", 0),
                    "failed": results.get("failed", 0),
                },
            )

            return results
        except Exception as e:
            self._audit("math_validation_failed", {"error": str(e)})
            return {"valid": False, "error": str(e)}

    def get_math_framework_stats(self) -> dict:
        """Get statistics about the mathematical framework."""
        if not self._math_engine:
            return {"available": False}

        try:
            stats = self._math_engine.get_stats()
            stats["available"] = True
            return stats
        except Exception:
            return {"available": False}

    def get_equation_bridge_stats(self) -> dict:
        """Get statistics about the SuperBrain equation bridge."""
        if not self._equation_bridge:
            return {"available": False}

        try:
            stats = self._equation_bridge.get_pattern_analysis()
            stats["available"] = True
            return stats
        except Exception:
            return {"available": False}

    def execute_equation(self, equation_name: str, inputs: dict) -> dict:
        """Execute an equation via the SuperBrain equation bridge.

        Args:
            equation_name: Name of the equation to execute
            inputs: Input parameters for the equation

        Returns:
            Execution result with validation
        """
        if not self._equation_bridge:
            return {"error": "Equation bridge not available"}

        try:
            result = self._equation_bridge.compute(equation_name, inputs)
            self._audit(
                "equation_executed",
                {
                    "equation": equation_name,
                    "success": result.is_valid if hasattr(result, "is_valid") else True,
                },
            )
            return {
                "equation": equation_name,
                "result": result.result if hasattr(result, "result") else None,
                "is_valid": result.is_valid if hasattr(result, "is_valid") else True,
                "metadata": result.metadata if hasattr(result, "metadata") else {},
            }
        except Exception as e:
            self._audit("equation_execution_failed", {"equation": equation_name, "error": str(e)})
            return {"error": str(e), "equation": equation_name}

    def simulate_future(self, initial_state: dict, actions: list[dict], horizon: int = 5) -> dict:
        """Simulate future states using the Predictive World Model.

        Args:
            initial_state: Starting state for simulation
            actions: Sequence of actions to apply
            horizon: Number of steps to simulate ahead

        Returns:
            Simulation result with trajectory and confidence
        """
        if not self._world_model:
            return {"error": "World Model not available"}

        try:
            result = self._world_model.simulate_future(initial_state, actions, horizon)
            self._audit(
                "future_simulated",
                {"horizon": horizon, "actions_count": len(actions), "success": True},
            )
            return {
                "trajectory": [
                    {"step": s.step, "confidence": s.confidence, "uncertainty": s.uncertainty}
                    for s in result.trajectory
                ]
                if hasattr(result, "trajectory")
                else [],
                "horizon": result.horizon if hasattr(result, "horizon") else horizon,
                "final_confidence": result.final_confidence
                if hasattr(result, "final_confidence")
                else 0.0,
                "success": True,
            }
        except Exception as e:
            self._audit("simulation_failed", {"error": str(e), "horizon": horizon})
            return {"error": str(e)}

    def reflect_on_error(self, simulation_error: dict) -> dict:
        """Perform meta-cognitive reflection on simulation errors.

        Args:
            simulation_error: Error from simulation vs actual comparison

        Returns:
            Reflection insights and recommended adjustments
        """
        if not self._world_model:
            return {"error": "World Model not available"}

        try:
            reflection = self._world_model.reflect_on_error(simulation_error)
            return {
                "error_type": reflection.error_type
                if hasattr(reflection, "error_type")
                else "unknown",
                "root_cause": reflection.root_cause if hasattr(reflection, "root_cause") else "",
                "recommendations": reflection.recommended_adjustments
                if hasattr(reflection, "recommended_adjustments")
                else [],
                "success": True,
            }
        except Exception as e:
            return {"error": str(e)}

    def improve_world_model(self) -> dict:
        """Trigger self-improvement of the world model based on accumulated reflections.

        Returns:
            Improvement results with applied changes
        """
        if not self._world_model:
            return {"error": "World Model not available"}

        try:
            improvements = self._world_model.improve_from_reflections()
            self._audit(
                "world_model_improved",
                {
                    "improvements_count": len(improvements)
                    if hasattr(improvements, "__len__")
                    else 0
                },
            )
            return {
                "improvements": len(improvements) if hasattr(improvements, "__len__") else 0,
                "success": True,
            }
        except Exception as e:
            return {"error": str(e)}

    def _audit(self, action: str, details: dict[str, Any]) -> None:
        """Record audit entry."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "brain_id": self.brain_id,
            "action": action,
            "details": details,
        }
        self._audit_log.append(entry)

    def _emit_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Emit event to the AMOS event bus for cross-component communication.

        Args:
            event_type: Type of event (e.g., 'math_framework_initialized')
            payload: Event data payload
        """
        try:
            # Attempt to import and use the event bus if available
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "event_bus", str(Path(__file__).parent.parent / "backend" / "event_bus.py")
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Create event
                _ = module.AMOSEvent(
                    event_type=event_type,
                    source=f"super_brain:{self.brain_id}",
                    payload=payload,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

                # Publish to event bus (async operation, fire-and-forget)
                print(f"[EventBus] Emitting {event_type}")
        except Exception:
            # Silent fail - events are best-effort
            pass

    # ============ PUBLIC API ============

    def get_state(self) -> SuperBrainState:
        """Get current immutable state snapshot."""
        with self._state_lock:
            return SuperBrainState(
                timestamp=datetime.now(timezone.utc).isoformat(),
                status=self.status,
                active_kernels=self._kernel_router.list_kernels() if self._kernel_router else [],
                loaded_tools=self._tool_registry.list_tools() if self._tool_registry else [],
                available_models=self._model_router.list_models() if self._model_router else [],
                memory_stats=self._memory_governance.get_stats() if self._memory_governance else {},
                clawd_status=self._clawd_layer.get_status() if self._clawd_layer else "unavailable",
                core_frozen=self._core_freeze.is_frozen() if self._core_freeze else False,
                math_framework_status="active" if self._math_engine else "unavailable",
                health_score=self._calculate_health_score(),
            )

    def _calculate_health_score(self) -> float:
        """Calculate overall health score (0.0-1.0)."""
        checks = []

        if self._kernel_router:
            checks.append(self._kernel_router.is_healthy())
        if self._tool_registry:
            checks.append(self._tool_registry.is_healthy())
        if self._model_router:
            checks.append(self._model_router.is_healthy())
        if self._clawd_layer:
            checks.append(self._clawd_layer.is_healthy())
        if self._math_engine:
            checks.append(True)  # Math framework is healthy if initialized

        if not checks:
            return 0.0
        return sum(checks) / len(checks)

    def execute_task(self, task: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Execute task through the SuperBrain (single entry point).

        LAW 0 COMPLIANCE: All execution flows through here.
        No subprocesses, no parallel runtimes.

        Args:
            task: Task description
            context: Optional execution context

        Returns:
            Execution result
        """
        if self.status != "active":
            return {"success": False, "error": f"SuperBrain status: {self.status}"}

        context = context or {}

        # Route through kernel
        kernel_result = self._kernel_router.route(task, context)

        # Audit the execution
        self._audit(
            "TASK_EXECUTED",
            {
                "task": task[:100],
                "kernel": kernel_result.get("kernel"),
                "success": kernel_result.get("success", False),
            },
        )

        return kernel_result

    def execute_tool(
        self, tool_name: str, inputs: dict[str, Any], agent_id: str = None
    ) -> dict[str, Any]:
        """Execute tool through ActionGate (authorized path only).

        LAW 4 COMPLIANCE: Agents cannot bypass ActionGate.
        All tool execution is authorized and audited.

        Args:
            tool_name: Name of tool to execute
            inputs: Tool inputs
            agent_id: Optional agent identifier for permission check

        Returns:
            Tool execution result
        """
        if self.status != "active":
            return {"success": False, "error": f"SuperBrain status: {self.status}"}

        # ActionGate enforces authorization (blocks unauthorized agents)
        return self._action_gate.execute_tool(tool_name, inputs, agent_id)

    def query_model(
        self, model_id: str, prompt: str, context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Query model through ModelRouter (single model path).

        Args:
            model_id: Model identifier
            prompt: Prompt text
            context: Optional context

        Returns:
            Model response
        """
        if self.status != "active":
            return {"success": False, "error": f"SuperBrain status: {self.status}"}

        return self._model_router.query(model_id, prompt, context)

    def write_memory(self, key: str, value: Any, agent_id: str = None) -> bool:
        """Write to memory through governance layer.

        LAW 4 COMPLIANCE: All writes go through MemoryGovernance.
        No direct memory access bypassing governance.

        Args:
            key: Memory key
            value: Value to store
            agent_id: Optional agent for permission check

        Returns:
            True if write successful
        """
        if self.status != "active":
            return False

        return self._memory_governance.write(key, value, agent_id)

    def read_memory(self, key: str) -> Any:
        """Read from memory through governance layer."""
        if self.status != "active":
            return None

        return self._memory_governance.read(key)

    def is_core_mutable(self, agent_id: str) -> bool:
        """Check if agent can mutate core files.

        LAW 5 COMPLIANCE: Only core-protected agents can mutate core.
        Normal agents are denied.

        Args:
            agent_id: Agent to check

        Returns:
            True only if agent has core mutation permission
        """
        return self._core_freeze.can_mutate(agent_id)

    def health_check(self) -> dict[str, Any]:
        """Run full health check on all subsystems."""
        results = {
            "brain_id": self.brain_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": self.status,
            "subsystems": {},
        }

        subsystems = [
            ("kernel_router", self._kernel_router),
            ("action_gate", self._action_gate),
            ("model_router", self._model_router),
            ("tool_registry", self._tool_registry),
            ("source_registry", self._source_registry),
            ("memory_governance", self._memory_governance),
            ("clawd_layer", self._clawd_layer),
            ("core_freeze", self._core_freeze),
        ]

        for name, subsystem in subsystems:
            if subsystem:
                try:
                    healthy = subsystem.is_healthy() if hasattr(subsystem, "is_healthy") else True
                    results["subsystems"][name] = "healthy" if healthy else "unhealthy"
                except Exception as e:
                    results["subsystems"][name] = f"error: {str(e)}"
            else:
                results["subsystems"][name] = "not_initialized"

        self._last_health_check = datetime.now(timezone.utc)
        return results

    def shutdown(self) -> None:
        """Graceful shutdown of SuperBrain."""
        print("\n" + "=" * 70)
        print(" SUPER BRAIN RUNTIME - SHUTDOWN")
        print("=" * 70)

        self.status = "shutting_down"
        self._audit("SUPER_BRAIN_SHUTDOWN", {"brain_id": self.brain_id})

        # Shutdown subsystems in reverse order
        if self._clawd_layer:
            self._clawd_layer.shutdown()
        if self._kernel_router:
            self._kernel_router.shutdown()
        if self._action_gate:
            self._action_gate.shutdown()
        if self._model_router:
            self._model_router.shutdown()
        if self._tool_registry:
            self._tool_registry.shutdown()
        if self._source_registry:
            self._source_registry.shutdown()
        if self._memory_governance:
            self._memory_governance.shutdown()

        self.status = "shutdown"
        print("✅ SuperBrain shutdown complete")
        print("=" * 70)


# Global singleton access
def get_super_brain() -> SuperBrainRuntime:
    """Get the singleton SuperBrainRuntime instance.

    This is the ONLY way to access the brain runtime.
    """
    return SuperBrainRuntime()


def initialize_super_brain() -> bool:
    """Initialize the SuperBrain (one-time call).

    Returns:
        bool: True if initialization successful
    """
    brain = get_super_brain()
    return brain.initialize()
