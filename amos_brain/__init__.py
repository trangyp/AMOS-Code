"""AMOS Brain - Minimal public API surface with lazy loading."""

# Core types (lightweight, no side effects)
from .facade import BrainResponse, Decision
from .config import FeatureFlags

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


# Optional features - deferred to avoid import-time failures
SystemPromptBuilder = None
ArchitectureDecision = None
CodeReview = None
SecurityAudit = None
DesignPattern = None
ProblemDiagnosis = None
ProjectPlanner = None
CookbookResult = None


def _load_optional_features():
    """Load optional features on first use - not at import time."""
    global SystemPromptBuilder, ArchitectureDecision, CodeReview
    global SecurityAudit, DesignPattern, ProblemDiagnosis
    global ProjectPlanner, CookbookResult
    
    try:
        from .prompt_builder import SystemPromptBuilder as spb
        SystemPromptBuilder = spb
    except Exception:
        pass
    
    try:
        from .cookbook import (
            ArchitectureDecision as ad,
            CodeReview as cr,
            SecurityAudit as sa,
            DesignPattern as dp,
            ProblemDiagnosis as pd,
            ProjectPlanner as pp,
            CookbookResult as cbr,
        )
        ArchitectureDecision = ad
        CodeReview = cr
        SecurityAudit = sa
        DesignPattern = dp
        ProblemDiagnosis = pd
        ProjectPlanner = pp
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
    if name in (
        "ArchitectureDecision", "CodeReview", "SecurityAudit",
        "DesignPattern", "ProblemDiagnosis", "ProjectPlanner", "CookbookResult"
    ):
        _OptionalLoader.ensure_loaded()
        return globals()[name]
    raise AttributeError(f"module 'amos_brain' has no attribute '{name}'")

__all__ = [
    # Core public API (minimal, lazy-loaded)
    "BrainClient",
    "get_brain",
    "get_amos_integration",
    "think",
    "decide",
    "validate",
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
    "CookbookResult",
]
