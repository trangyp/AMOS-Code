"""Backward-compatibility shim — real implementation is in multi_agent/subagent.py."""
from multi_agent.subagent import (  # noqa: F401
    _BUILTIN_AGENTS,
    AgentDefinition,
    SubAgentManager,
    SubAgentTask,
    _agent_run,
    _extract_final_text,
    get_agent_definition,
    load_agent_definitions,
)
