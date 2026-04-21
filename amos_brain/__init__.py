"""AMOS Brain - Minimal public API surface with lazy loading."""

import logging

# Core types (lightweight, no side effects)
from .config import FeatureFlags

# NOTE: BrainResponse and Decision are lazy-loaded via __getattr__ below
# to avoid 56ms facade import at startup

logger = logging.getLogger(__name__)

# Lazy module cache
_lazy_modules = {}


def _lazy_import(module_name: str):
    """Import module on first access to reduce startup blast radius."""
    if module_name not in _lazy_modules:
        try:
            if module_name == "BrainClient":
                from .facade import BrainClient as bc

                _lazy_modules[module_name] = bc
            elif module_name == "get_brain":
                from .loader import get_brain as gb

                _lazy_modules[module_name] = gb
            elif module_name == "BrainLoader":
                from .loader import BrainLoader as bl

                _lazy_modules[module_name] = bl
            elif module_name == "get_super_brain":
                from .super_brain import get_super_brain as gsb

                _lazy_modules[module_name] = gsb
            elif module_name == "SuperBrainRuntime":
                from .super_brain import SuperBrainRuntime as sbr

                _lazy_modules[module_name] = sbr
            elif module_name == "initialize_super_brain":
                from .super_brain import initialize_super_brain as isb

                _lazy_modules[module_name] = isb
            elif module_name == "SuperBrainOrchestrationAdapter":
                from .orchestration_adapter import SuperBrainOrchestrationAdapter as sboa

                _lazy_modules[module_name] = sboa
            elif module_name == "get_amos_integration":
                from .integration import get_amos_integration as gai

                _lazy_modules[module_name] = gai
            elif module_name == "think":
                from .facade import think as t

                _lazy_modules[module_name] = t
            elif module_name == "decide":
                from .facade import decide as d

                _lazy_modules[module_name] = d
            elif module_name == "validate":
                from .facade import validate as v

                _lazy_modules[module_name] = v
            elif module_name == "create_local_runtime":
                from .local_runtime import create_local_runtime as clr

                _lazy_modules[module_name] = clr
            elif module_name == "GlobalLaws":
                from .laws import GlobalLaws as gl

                _lazy_modules[module_name] = gl
            elif module_name == "RuleOfTwo":
                from .reasoning import RuleOfTwo as r2

                _lazy_modules[module_name] = r2
            elif module_name == "RuleOfFour":
                from .reasoning import RuleOfFour as r4

                _lazy_modules[module_name] = r4
            elif module_name == "CognitiveStack":
                from .cognitive_stack import CognitiveStack as cs

                _lazy_modules[module_name] = cs
            elif module_name == "KernelRouter":
                from .kernel_router import KernelRouter as kr

                _lazy_modules[module_name] = kr
            elif module_name == "process_task":
                from .task_processor import process_task as pt

                _lazy_modules[module_name] = pt
            elif module_name == "get_agent_bridge":
                from .agent_bridge import get_agent_bridge as gab

                _lazy_modules[module_name] = gab
            elif module_name == "get_state_manager":
                from .state_manager import get_state_manager as gsm

                _lazy_modules[module_name] = gsm
            elif module_name == "get_meta_controller":
                from .meta_controller import get_meta_controller as gmc

                _lazy_modules[module_name] = gmc
            elif module_name == "orchestrate_goal":
                from .meta_controller import orchestrate_goal as og

                _lazy_modules[module_name] = og
            elif module_name == "get_metrics":
                from .metrics import get_metrics as gm

                _lazy_modules[module_name] = gm
            elif module_name == "get_kernel_router":
                from .kernel_router import get_kernel_router as gkr

                _lazy_modules[module_name] = gkr
            elif module_name == "get_monitor":
                from .monitor import get_monitor as gmon

                _lazy_modules[module_name] = gmon
            elif module_name == "CognitiveConfig":
                from .config import CognitiveConfig as cc

                _lazy_modules[module_name] = cc
            elif module_name == "get_config":
                from .config import get_config as gc

                _lazy_modules[module_name] = gc
            elif module_name == "get_architecture_bridge":
                from .architecture_bridge import get_architecture_bridge as gab

                _lazy_modules[module_name] = gab
            elif module_name == "configure_tracing":
                from .tracing import configure_tracing as ct

                _lazy_modules[module_name] = ct
            elif module_name == "Tracer":
                from .tracing import Tracer as tr

                _lazy_modules[module_name] = tr
            elif module_name == "RealLearningEngine":
                from .real_learning_engine import RealLearningEngine as rle

                _lazy_modules[module_name] = rle
            elif module_name == "Procedure":
                from .real_learning_engine import Procedure as proc

                _lazy_modules[module_name] = proc
            elif module_name == "get_openclaw_bridge":
                from .openclaw_execution_bridge import get_openclaw_bridge as goc

                _lazy_modules[module_name] = goc
            elif module_name == "amos_openclaw_health":
                from .openclaw_execution_bridge import amos_openclaw_health as aoh

                _lazy_modules[module_name] = aoh
            elif module_name == "detect_openclaw_fakes":
                from .openclaw_fake_detector import detect_openclaw_fakes as dof

                _lazy_modules[module_name] = dof
            elif module_name == "Pattern":
                from .real_learning_engine import Pattern as pat

                _lazy_modules[module_name] = pat
            elif module_name == "Decision":
                from .real_learning_engine import Decision as dec

                _lazy_modules[module_name] = dec
            elif module_name == "FailurePattern":
                from .real_learning_engine import FailurePattern as fp

                _lazy_modules[module_name] = fp
            elif module_name == "learn_from_task":
                from .real_learning_engine import learn_from_task as lft

                _lazy_modules[module_name] = lft
            elif module_name == "attempt_procedure_reuse":
                from .real_learning_engine import attempt_procedure_reuse as apr

                _lazy_modules[module_name] = apr
            elif module_name == "get_learning_engine":
                from .real_learning_engine import get_learning_engine as gle

                _lazy_modules[module_name] = gle
            elif module_name == "query_math_framework":
                from .super_brain import query_math_framework as qmf

                _lazy_modules[module_name] = qmf
            elif module_name == "validate_equation":
                from .super_brain import validate_equation as ve

                _lazy_modules[module_name] = ve
            elif module_name == "get_math_framework_stats":
                from .super_brain import get_math_framework_stats as gmfs

                _lazy_modules[module_name] = gmfs
            elif module_name == "get_canon_knowledge_engine":
                from .canon_knowledge_engine import get_canon_knowledge_engine as gck

                _lazy_modules[module_name] = gck
            elif module_name == "get_canon_cognitive_processor":
                from .canon_cognitive_processor import get_canon_cognitive_processor as gcc

                _lazy_modules[module_name] = gcc
            elif module_name == "canon_process":
                from .canon_cognitive_processor import canon_process as cp

                _lazy_modules[module_name] = cp
            elif module_name == "get_canon_reasoning_engine":
                from .canon_reasoning_engine import get_canon_reasoning_engine as gcr

                _lazy_modules[module_name] = gcr
            elif module_name == "canon_reason":
                from .canon_reasoning_engine import canon_reason as cr

                _lazy_modules[module_name] = cr
            elif module_name == "get_canon_query_engine":
                from .canon_query_engine import get_canon_query_engine as gcq

                _lazy_modules[module_name] = gcq
            elif module_name == "canon_query":
                from .canon_query_engine import canon_query as cq

                _lazy_modules[module_name] = cq
            elif module_name == "get_canon_learning_engine":
                from .canon_learning_engine import get_canon_learning_engine as gcl

                _lazy_modules[module_name] = gcl
            elif module_name == "canon_learn":
                from .canon_learning_engine import canon_learn as cl

                _lazy_modules[module_name] = cl
            elif module_name == "get_canon_memory_system":
                from .canon_memory_system import get_canon_memory_system as gcm

                _lazy_modules[module_name] = gcm
            elif module_name == "canon_store":
                from .canon_memory_system import canon_store as cs

                _lazy_modules[module_name] = cs
            elif module_name == "canon_search":
                from .canon_memory_system import canon_search as csearch

                _lazy_modules[module_name] = csearch
            elif module_name == "get_canon_orchestrator":
                from .canon_orchestrator import get_canon_orchestrator as gco

                _lazy_modules[module_name] = gco
            elif module_name == "canon_orchestrate":
                from .canon_orchestrator import canon_orchestrate as co

                _lazy_modules[module_name] = co
            elif module_name == "get_cognitive_runtime":
                from amos_cognitive_runtime import get_cognitive_runtime as gcr

                _lazy_modules[module_name] = gcr
            elif module_name == "get_autonomous_compiler":
                from .autonomous_compiler_engine import get_autonomous_compiler as gac

                _lazy_modules[module_name] = gac
            elif module_name == "AutonomousCompilerEngine":
                from .autonomous_compiler_engine import AutonomousCompilerEngine as ace

                _lazy_modules[module_name] = ace
            elif module_name == "get_llm_generator":
                from .llm_code_generator import get_llm_generator as glg

                _lazy_modules[module_name] = glg
            elif module_name == "LLMCodeGenerator":
                from .llm_code_generator import LLMCodeGenerator as lcg

                _lazy_modules[module_name] = lcg
        except Exception as _load_err:
            # Capture values by using default arguments to avoid closure bug
            def _make_error_loader(name: str, err: str):
                def _error_loader(*args, **kwargs):
                    raise ImportError(f"Could not load {name}: {err}")

                return _error_loader

            _lazy_modules[module_name] = _make_error_loader(module_name, str(_load_err))
    return _lazy_modules[module_name]


# Lazy properties for core entry points
class _LazyBrainClient:
    """Lazy BrainClient - imports only when first accessed."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = _lazy_import("BrainClient")()
        return cls._instance


def BrainClient():
    """Get BrainClient (lazy import)."""
    return _LazyBrainClient()


def get_brain():
    """Get brain instance (lazy import)."""
    return _lazy_import("get_brain")()


def get_amos_integration():
    """Get AMOS integration (lazy import)."""
    return _lazy_import("get_amos_integration")()


def think(*args, **kwargs):
    """Cognitive analysis (lazy import)."""
    return _lazy_import("think")(*args, **kwargs)


def decide(*args, **kwargs):
    """Decision making (lazy import)."""
    return _lazy_import("decide")(*args, **kwargs)


def validate(*args, **kwargs):
    """Action validation (lazy import)."""
    return _lazy_import("validate")(*args, **kwargs)


def process_task(*args, **kwargs):
    """Task processing (lazy import)."""
    return _lazy_import("process_task")(*args, **kwargs)


def get_agent_bridge():
    """Get agent bridge (lazy import)."""
    return _lazy_import("get_agent_bridge")()


def get_state_manager():
    """Get state manager (lazy import)."""
    return _lazy_import("get_state_manager")()


def get_meta_controller():
    """Get meta controller (lazy import)."""
    return _lazy_import("get_meta_controller")()


def orchestrate_goal(*args, **kwargs):
    """Orchestrate goal (lazy import)."""
    return _lazy_import("orchestrate_goal")(*args, **kwargs)


def get_metrics():
    """Get metrics collector (lazy import)."""
    return _lazy_import("get_metrics")()


def get_kernel_router():
    """Get kernel router (lazy import)."""
    return _lazy_import("get_kernel_router")()


def get_monitor():
    """Get cognitive monitor (lazy import)."""
    return _lazy_import("get_monitor")()


def get_super_brain():
    """Get SuperBrain runtime (lazy import)."""
    return _lazy_import("get_super_brain")()


def CognitiveConfig():
    """Get cognitive config (lazy import)."""
    return _lazy_import("CognitiveConfig")()


def get_config():
    """Get config instance (lazy import)."""
    return _lazy_import("get_config")()


# SuperBrain exports (ONE BRAIN - Canonical Runtime)
def initialize_super_brain():
    """Initialize SuperBrain (lazy import)."""
    return _lazy_import("initialize_super_brain")()


def SuperBrainRuntime():
    """Get SuperBrainRuntime class (lazy import)."""
    return _lazy_import("SuperBrainRuntime")


def SuperBrainState():
    """Get SuperBrainState class (lazy import)."""
    return _lazy_import("SuperBrainState")


def ActionGate():
    """Get ActionGate class (lazy import)."""
    return _lazy_import("ActionGate")


def ModelRouter():
    """Get ModelRouter class (lazy import)."""
    return _lazy_import("ModelRouter")


def get_autonomous_compiler():
    """Get autonomous compiler engine (lazy import)."""
    return _lazy_import("get_autonomous_compiler")()


def AutonomousCompilerEngine():
    """Get AutonomousCompilerEngine class (lazy import)."""
    return _lazy_import("AutonomousCompilerEngine")


def get_llm_generator():
    """Get LLM code generator (lazy import)."""
    return _lazy_import("get_llm_generator")()


def LLMCodeGenerator():
    """Get LLMCodeGenerator class (lazy import)."""
    return _lazy_import("LLMCodeGenerator")


def SourceRegistry():
    """Get SourceRegistry class (lazy import)."""
    return _lazy_import("SourceRegistry")


def MemoryGovernance():
    """Get MemoryGovernance class (lazy import)."""
    return _lazy_import("MemoryGovernance")


def CoreFreezeEnforcer():
    """Get CoreFreezeEnforcer class (lazy import)."""
    return _lazy_import("CoreFreezeEnforcer")


def ClawdExecutionLayer():
    """Get ClawdExecutionLayer class (lazy import)."""
    return _lazy_import("ClawdExecutionLayer")


def SuperBrainOrchestrationAdapter():
    """Get SuperBrainOrchestrationAdapter class (lazy import)."""
    return _lazy_import("SuperBrainOrchestrationAdapter")


def get_canon_knowledge_engine():
    """Get Canon knowledge engine (lazy import)."""
    return _lazy_import("get_canon_knowledge_engine")()


def get_canon_cognitive_processor():
    """Get Canon cognitive processor (lazy import)."""
    return _lazy_import("get_canon_cognitive_processor")()


def canon_process(*args, **kwargs):
    """Process with Canon enrichment (lazy import)."""
    return _lazy_import("canon_process")(*args, **kwargs)


def get_canon_reasoning_engine():
    """Get Canon reasoning engine (lazy import)."""
    return _lazy_import("get_canon_reasoning_engine")()


def canon_reason(*args, **kwargs):
    """Reason with Canon knowledge (lazy import)."""
    return _lazy_import("canon_reason")(*args, **kwargs)


def get_canon_query_engine():
    """Get Canon query engine (lazy import)."""
    return _lazy_import("get_canon_query_engine")()


def canon_query(*args, **kwargs):
    """Query with Canon context (lazy import)."""
    return _lazy_import("canon_query")(*args, **kwargs)


def get_canon_learning_engine():
    """Get Canon learning engine (lazy import)."""
    return _lazy_import("get_canon_learning_engine")()


def canon_learn(*args, **kwargs):
    """Learn with Canon guidance (lazy import)."""
    return _lazy_import("canon_learn")(*args, **kwargs)


def get_canon_memory_system():
    """Get Canon memory system (lazy import)."""
    return _lazy_import("get_canon_memory_system")()


def canon_store(*args, **kwargs):
    """Store memory with Canon context (lazy import)."""
    return _lazy_import("canon_store")(*args, **kwargs)


def canon_search(*args, **kwargs):
    """Search memories with Canon enhancement (lazy import)."""
    return _lazy_import("canon_search")(*args, **kwargs)


def get_canon_orchestrator():
    """Get Canon orchestrator (lazy import)."""
    return _lazy_import("get_canon_orchestrator")()


def canon_orchestrate(*args, **kwargs):
    """Orchestrate task with Canon integration (lazy import)."""
    return _lazy_import("canon_orchestrate")(*args, **kwargs)


# Optional features - deferred to avoid import-time failures
# These are loaded lazily via __getattr__ below
# DO NOT assign None here - it prevents __getattr__ from triggering


def _load_optional_features():
    """Load optional features on first use - not at import time."""
    global SystemPromptBuilder, ArchitectureDecision, CodeReview
    global SecurityAudit, DesignPattern, ProblemDiagnosis
    global ProjectPlanner, TechnologySelection, RiskAssessment, CookbookResult

    try:
        from .prompt_builder import SystemPromptBuilder as spb

        SystemPromptBuilder = spb
    except Exception as e:
        logger.debug(f"Optional feature 'prompt_builder' not available: {e}")

    try:
        from .cookbook import (
            ArchitectureDecision as ad,
        )
        from .cookbook import (
            CodeReview as cr,
        )
        from .cookbook import (
            CookbookResult as cbr,
        )
        from .cookbook import (
            DesignPattern as dp,
        )
        from .cookbook import (
            ProblemDiagnosis as pd,
        )
        from .cookbook import (
            ProjectPlanner as pp,
        )
        from .cookbook import (
            RiskAssessment as ra,
        )
        from .cookbook import (
            SecurityAudit as sa,
        )
        from .cookbook import (
            TechnologySelection as ts,
        )

        ArchitectureDecision = ad
        CodeReview = cr
        SecurityAudit = sa
        DesignPattern = dp
        ProblemDiagnosis = pd
        ProjectPlanner = pp
        TechnologySelection = ts
        RiskAssessment = ra
        CookbookResult = cbr
    except Exception as e:
        logger.debug(f"Optional feature 'cookbook' not available: {e}")


# Trigger optional loading on first property access
class _OptionalLoader:
    """Meta class to trigger optional loading."""

    _loaded = False

    @classmethod
    def ensure_loaded(cls):
        if not cls._loaded:
            _load_optional_features()
            cls._loaded = True


def __getattr__(name: str):
    """Dynamic attribute loading for optional features."""
    core_lazy_names = {
        "BrainLoader",
        "GlobalLaws",
        "RuleOfTwo",
        "RuleOfFour",
        "CognitiveStack",
        "KernelRouter",
    }
    if name in core_lazy_names:
        return _lazy_import(name)

    # Types from facade - lazy loaded to avoid 56ms import at startup
    facade_types = {"BrainResponse", "Decision"}
    if name in facade_types:
        from .facade import BrainResponse, Decision

        if name == "BrainResponse":
            return BrainResponse
        return Decision

    # Cookbook classes - ensure loaded and return
    cookbook_names = {
        "SystemPromptBuilder",
        "ArchitectureDecision",
        "CodeReview",
        "SecurityAudit",
        "DesignPattern",
        "ProblemDiagnosis",
        "ProjectPlanner",
        "TechnologySelection",
        "RiskAssessment",
        "CookbookResult",
    }
    if name in cookbook_names:
        if globals().get(name) is None:
            _load_optional_features()
        result = globals().get(name)
        if result is None:
            raise ImportError(f"Could not load {name} from cookbook module")
        return result

    # Organism bridge - lazy load
    organism_names = {"get_organism_bridge", "initialize_organism", "execute_organism_task"}
    if name in organism_names:
        return locals()[name]

    # Knowledge engine - lazy load
    if name in ("get_knowledge_engine", "query_knowledge"):
        return locals()[name]

    # Multi-agent orchestrator - lazy load
    if name in ("get_multi_agent_orchestrator", "spawn_agent", "orchestrate_task"):
        return locals()[name]

    # Performance engine - lazy load
    if name in ("get_performance_engine", "cached_think", "cached_decide", "batch_think"):
        return locals()[name]

    # Equation bridge - lazy load
    equation_names = {
        "get_equation_bridge",
        "compute_equation",
        "EquationBridgeIntegration",
        "EquationComputeRequest",
        "EquationComputeResponse",
    }
    if name in equation_names:
        from .equation_bridge_integration import (
            EquationBridgeIntegration as ebi,
        )
        from .equation_bridge_integration import (
            EquationComputeRequest as ecr,
        )
        from .equation_bridge_integration import (
            EquationComputeResponse as ecresp,
        )
        from .equation_bridge_integration import (
            compute_equation as ce,
        )
        from .equation_bridge_integration import (
            get_equation_bridge as geb,
        )

        globals()["EquationBridgeIntegration"] = ebi
        globals()["EquationComputeRequest"] = ecr
        globals()["EquationComputeResponse"] = ecresp
        globals()["get_equation_bridge"] = geb
        globals()["compute_equation"] = ce
        return globals()[name]

    # Debugging utilities - lazy load
    debug_names = {"ic", "pretty_print", "print_table", "trace", "debug_breakpoint", "DebugContext"}
    if name in debug_names:
        return locals()[name]

    raise AttributeError(f"module 'amos_brain' has no attribute '{name}'")


__all__ = [
    # Core public API (minimal, lazy-loaded)
    "BrainClient",
    "get_brain",
    "get_amos_integration",
    "think",
    "decide",
    "validate",
    "process_task",
    "get_agent_bridge",
    "get_state_manager",
    "get_meta_controller",
    "orchestrate_goal",
    "get_metrics",
    "BrainLoader",
    "GlobalLaws",
    "RuleOfTwo",
    "RuleOfFour",
    "CognitiveStack",
    "KernelRouter",
    # SuperBrain (Canonical Runtime - ONE BRAIN)
    "SuperBrainRuntime",
    "get_super_brain",
    "initialize_super_brain",
    "SuperBrainState",
    "get_brain_runtime",
    # Governance Components
    "ActionGate",
    "ModelRouter",
    "SourceRegistry",
    "MemoryGovernance",
    "CoreFreezeEnforcer",
    "ClawdExecutionLayer",
    # Types
    "BrainResponse",
    "Decision",
    "FeatureFlags",
    # Compiler / Code Generation
    "get_autonomous_compiler",
    "AutonomousCompilerEngine",
    "get_llm_generator",
    "LLMCodeGenerator",
    # Optional (deferred loading)
    "SystemPromptBuilder",
    "ArchitectureDecision",
    "CodeReview",
    "SecurityAudit",
    "DesignPattern",
    "ProblemDiagnosis",
    "ProjectPlanner",
    "TechnologySelection",
    "RiskAssessment",
    "CookbookResult",
    # Organism bridge
    "get_organism_bridge",
    "initialize_organism",
    "execute_organism_task",
    # Knowledge engine
    "get_knowledge_engine",
    "query_knowledge",
    # Multi-agent orchestrator
    "get_multi_agent_orchestrator",
    "spawn_agent",
    "orchestrate_task",
    # Performance engine
    "get_performance_engine",
    "cached_think",
    "cached_decide",
    "batch_think",
    # Debugging utilities
    "ic",
    "pretty_print",
    "print_table",
    "trace",
    "debug_breakpoint",
    "DebugContext",
    # Architecture bridge
    "get_architecture_bridge",
    # Tracing
    "Tracer",
    "configure_tracing",
    # Real Learning Engine
    "RealLearningEngine",
    "Procedure",
    "Pattern",
    "Decision",
    "FailurePattern",
    "learn_from_task",
    "attempt_procedure_reuse",
    "get_learning_engine",
    # Equation Bridge
    "get_equation_bridge",
    "compute_equation",
    "EquationBridgeIntegration",
    "EquationComputeRequest",
    "EquationComputeResponse",
    "get_cognitive_runtime",
]


def get_cognitive_runtime():
    """Get cognitive runtime (lazy import)."""
    return _lazy_import("get_cognitive_runtime")()
