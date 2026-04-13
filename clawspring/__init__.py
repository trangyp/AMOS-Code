"""ClawSpring - Minimal Python implementation of Claude Code."""
from __future__ import annotations

__version__ = "3.05.5"

# Core exports
from .clawspring import main
from .agent import AgentState, run
from .tools import execute_tool, register_tool
from .tool_registry import ToolDef, register_tool as register_tool_def
from .providers import stream, AssistantTurn

__all__ = [
    "main",
    "AgentState",
    "run",
    "execute_tool",
    "register_tool",
    "register_tool_def",
    "ToolDef",
    "stream",
    "AssistantTurn",
]
