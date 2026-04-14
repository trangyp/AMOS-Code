"""ClawSpring - AMOS Brain Integration Package.

This package integrates the AMOS cognitive architecture into the ClawSpring agent.
Creator: Trang Phan
System: AMOS vInfinity
"""

__version__ = "vInfinity"
__creator__ = "Trang Phan"
__system__ = "AMOS"

# Core exports - conditional to avoid import errors
# when optional modules are not present
try:
    from amos_runtime import AMOSRuntime, get_runtime
except ImportError:
    get_runtime = None
    AMOSRuntime = None

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
    "get_runtime",
    "AMOSRuntime",
    "full_execute",
    "ExecutionResult",
    "AMOS_TOOLS",
    "ToolDef",
]
