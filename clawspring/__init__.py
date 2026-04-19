"""ClawSpring - AMOS SuperBrain Integration Package.

This package integrates the AMOS SuperBrain cognitive architecture.
Creator: Trang Phan
System: AMOS vInfinity
"""

__version__ = "vInfinity"
__creator__ = "Trang Phan"
__system__ = "AMOS"

# LAWS OF INTEGRATION:
# 1. ONE BRAIN: All capabilities flow through SuperBrainRuntime
# 2. NO PARALLEL: Old amos_runtime paths are redirected to SuperBrain
# 3. GOVERNED: All tool/model/memory access through canonical registries

# Core SuperBrain exports - single source of truth
try:
    from amos_brain.super_brain import SuperBrainRuntime, get_super_brain, initialize_super_brain

    _super_brain_available = True
except ImportError:
    SuperBrainRuntime = None
    get_super_brain = None
    initialize_super_brain = None
    _super_brain_available = False


# Legacy shim - redirect old runtime to SuperBrain
def get_runtime():
    """LEGACY SHIM: Returns SuperBrainRuntime (canonical brain)."""
    if _super_brain_available and get_super_brain:
        return get_super_brain()
    return None


# Legacy compatibility
try:
    from amos_execution import ExecutionResult, full_execute
except ImportError:
    full_execute = None
    ExecutionResult = None

try:
    from amos_tools import AMOS_TOOLS, ToolDef
except ImportError:
    AMOS_TOOLS = None
    ToolDef = None

__all__ = [
    # SuperBrain (Canonical)
    "SuperBrainRuntime",
    "get_super_brain",
    "initialize_super_brain",
    # Legacy shim
    "get_runtime",
    # Execution
    "full_execute",
    "ExecutionResult",
    # Tools
    "AMOS_TOOLS",
    "ToolDef",
]
