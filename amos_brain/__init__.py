"""AMOS Brain - Minimal public API surface with lazy loading."""

# Core types (lightweight, no side effects)
from .config import FeatureFlags
from .facade import BrainResponse, Decision

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
        except Exception as e:
            _lazy_modules[module_name] = lambda *args, **kwargs: (_ for _ in ()).throw(
                ImportError(f"Could not load {module_name}: {e}")
            )
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


def CognitiveConfig():
    """Get cognitive config (lazy import)."""
    return _lazy_import("CognitiveConfig")()


def get_config():
    """Get config instance (lazy import)."""
    return _lazy_import("get_config")()


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
    except Exception:
        pass

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
    except Exception:
        pass


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
    # Types
    "BrainResponse",
    "Decision",
    "FeatureFlags",
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
]
