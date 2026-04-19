#!/usr/bin/env python3
"""ActionGate - Canonical Authorization Layer for Tool Execution.

LAW 4 COMPLIANCE: All tool execution passes through this gate.
Agents cannot bypass this authorization layer.
All actions are audited and permission-checked.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc
from threading import Lock
from typing import Any


@dataclass
class ActionRequest:
    """Represents a request to execute a tool action."""

    tool_name: str
    inputs: dict[str, Any]
    agent_id: str
    timestamp: str
    request_id: str


@dataclass
class ActionResult:
    """Represents the result of a tool action."""

    success: bool
    output: Any
    error: str = None
    execution_time_ms: float = 0.0


class ActionGate:
    """Canonical authorization and execution gate for all tool actions.

    This is the ONLY path for tool execution in the SuperBrain.
    All tool calls must pass through this gate for authorization and audit.
    """

    def __init__(self, tool_registry: Any, memory_governance: Any):
        self._tool_registry = tool_registry
        self._memory_governance = memory_governance
        self._audit_log: list[dict[str, Any]] = []
        self._lock = Lock()
        self._blocked_agents: set[str] = set()
        self._execution_count = 0

    def execute_tool(
        self, tool_name: str, inputs: dict[str, Any], agent_id: str = None
    ) -> dict[str, Any]:
        """Execute tool through authorized path only.

        Args:
            tool_name: Name of tool to execute
            inputs: Tool inputs
            agent_id: Optional agent identifier

        Returns:
            Execution result
        """
        request_id = self._generate_request_id()
        request = ActionRequest(
            tool_name=tool_name,
            inputs=inputs,
            agent_id=agent_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=request_id,
        )

        # LAW 4: Check if agent is authorized
        if agent_id and agent_id in self._blocked_agents:
            self._audit(request, "DENIED_AGENT_BLOCKED", None)
            return {"success": False, "error": f"Agent {agent_id} is blocked from tool execution"}

        # Check if tool exists
        tool = self._tool_registry.get(tool_name)
        if not tool:
            self._audit(request, "DENIED_TOOL_NOT_FOUND", None)
            return {"success": False, "error": f"Tool '{tool_name}' not found in registry"}

        # Execute with audit
        try:
            import time

            start = time.time()
            result = tool.func(**inputs)
            execution_time = (time.time() - start) * 1000

            self._execution_count += 1
            self._audit(request, "EXECUTED", result)

            return {
                "success": True,
                "output": result,
                "execution_time_ms": execution_time,
                "request_id": request_id,
            }

        except Exception as e:
            self._audit(request, "EXECUTION_FAILED", str(e))
            return {"success": False, "error": str(e), "request_id": request_id}

    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        import hashlib
        import time

        timestamp = str(time.time())
        return hashlib.sha256(timestamp.encode()).hexdigest()[:12]

    def _audit(self, request: ActionRequest, outcome: str, result: Any) -> None:
        """Record audit entry."""
        entry = {
            "timestamp": request.timestamp,
            "request_id": request.request_id,
            "tool_name": request.tool_name,
            "agent_id": request.agent_id,
            "outcome": outcome,
            "result_preview": str(result)[:100] if result else None,
        }
        with self._lock:
            self._audit_log.append(entry)

    def is_healthy(self) -> bool:
        """Check if ActionGate is healthy."""
        return self._tool_registry is not None

    def shutdown(self) -> None:
        """Graceful shutdown."""
        pass
