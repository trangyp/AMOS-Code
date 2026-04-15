"""Multi-agent package for clawspring.

Provides:
  - AgentDefinition  — typed agent definition (name, system_prompt, model, tools)
  - SubAgentTask     — lifecycle-tracked task
  - SubAgentManager  — thread-pool manager for spawning agents
  - load_agent_definitions / get_agent_definition — agent registry
"""

from .subagent import (
    AgentDefinition,
    SubAgentManager,
    SubAgentTask,
    get_agent_definition,
    load_agent_definitions,
)

__all__ = [
    "AgentDefinition",
    "SubAgentTask",
    "SubAgentManager",
    "load_agent_definitions",
    "get_agent_definition",
]
