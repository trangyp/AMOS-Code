#!/usr/bin/env python3
"""AMOS Muscle Kernel - 06_MUSCLE Subsystem

import urllib.error
import urllib.request
import uuid
Responsible for:
- Action execution and task completion
- Tool invocation and management
- File operations (read, write, modify)
- External API calls
- Integration with BLOOD signals and IMMUNE safety checks
"""


import hashlib
import json
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.muscle")


class ActionType(Enum):
    """Types of actions MUSCLE can execute."""

    FILE_READ = auto()
    FILE_WRITE = auto()
    FILE_DELETE = auto()
    FILE_MODIFY = auto()
    COMMAND_EXECUTE = auto()
    API_CALL = auto()
    TOOL_INVOKE = auto()
    TASK_COMPLETE = auto()


class ActionStatus(Enum):
    """Status of an action execution."""

    PENDING = auto()
    VALIDATING = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    BLOCKED = auto()


@dataclass
class Action:
    """An action to be executed by MUSCLE."""

    action_id: str
    action_type: ActionType
    payload: Dict[str, Any]
    source: str
    status: ActionStatus = ActionStatus.PENDING
    created_at: str = ""
    started_at: str  = None
    completed_at: str  = None
    result: dict[str, Any ] = None
    error: str  = None
    safety_report: dict[str, Any ] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class Tool:
    """A tool that can be invoked."""

    tool_id: str
    name: str
    description: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]
    parameters: Dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    category: str = "general"


class MuscleKernel:
    """The Muscle Kernel provides execution capabilities -
    carrying out actions, invoking tools, and completing tasks.
    """

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.muscle_path = organism_root / "06_MUSCLE"
        self.memory_path = self.muscle_path / "memory"
        self.logs_path = self.muscle_path / "logs"

        # Ensure directories
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Action registry
        self.actions: Dict[str, Action] = {}
        self.action_history: List[Action] = []

        # Tool registry
        self.tools: Dict[str, Tool] = {}
        self._register_builtin_tools()

        # Execution settings
        self.max_concurrent = 5
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent)

        # Safety integration (will be connected to IMMUNE)
        self.immune_check: Callable[[str, dict[str, Any ], dict[str, Any]]] = None

        # Statistics
        self.stats = {
            "total_actions": 0,
            "completed_actions": 0,
            "failed_actions": 0,
            "blocked_actions": 0,
        }

        logger.info(f"MuscleKernel initialized at {self.muscle_path}")

    def _register_builtin_tools(self):
        """Register built-in tools."""
        self.tools["file_read"] = Tool(
            tool_id="file_read",
            name="File Read",
            description="Read contents of a file",
            handler=self._tool_file_read,
            parameters={"path": {"type": "string", "required": True}},
        )

        self.tools["file_write"] = Tool(
            tool_id="file_write",
            name="File Write",
            description="Write content to a file",
            handler=self._tool_file_write,
            parameters={
                "path": {"type": "string", "required": True},
                "content": {"type": "string", "required": True},
            },
            requires_confirmation=True,
        )

        self.tools["file_delete"] = Tool(
            tool_id="file_delete",
            name="File Delete",
            description="Delete a file",
            handler=self._tool_file_delete,
            parameters={"path": {"type": "string", "required": True}},
            requires_confirmation=True,
        )

        self.tools["command_execute"] = Tool(
            tool_id="command_execute",
            name="Command Execute",
            description="Execute a shell command",
            handler=self._tool_command_execute,
            parameters={
                "command": {"type": "string", "required": True},
                "timeout": {"type": "number", "default": 30},
            },
            requires_confirmation=True,
            category="system",
        )

        self.tools["api_call"] = Tool(
            tool_id="api_call",
            name="API Call",
            description="Make an HTTP API call",
            handler=self._tool_api_call,
            parameters={
                "url": {"type": "string", "required": True},
                "method": {"type": "string", "default": "GET"},
                "headers": {"type": "object", "default": {}},
                "body": {"type": "object", "default": None},
            },
            category="network",
        )

        logger.info(f"Registered {len(self.tools)} built-in tools")

    def set_immune_checker(self, checker: Callable[[str, dict[str, Any]], dict[str, Any]]):
        """Set the safety check function from IMMUNE."""
        self.immune_check = checker
        logger.info("Immune safety checker connected")

    def execute_action(
        self, action_type: ActionType, payload: Dict[str, Any], source: str = "unknown"
    ) -> Action:
        """Execute an action with safety validation.

        Args:
            action_type: Type of action to execute
            payload: Action parameters
            source: Source subsystem requesting the action

        Returns:
            Action object with results
        """
        action_id = self._generate_id()

        action = Action(
            action_id=action_id, action_type=action_type, payload=payload, source=source
        )

        self.actions[action_id] = action
        self.stats["total_actions"] += 1

        # 1. Safety validation
        action.status = ActionStatus.VALIDATING

        if self.immune_check:
            safety_result = self.immune_check(action_type.name, payload)
            action.safety_report = safety_result

            if not safety_result.get("safe", True):
                action.status = ActionStatus.BLOCKED
                action.error = f"Safety check failed: {safety_result.get('threats', [])}"
                self.stats["blocked_actions"] += 1
                logger.warning(f"Action {action_id} blocked by safety check")
                return action

        # 2. Execute action
        action.status = ActionStatus.EXECUTING
        action.started_at = datetime.now(timezone.utc).isoformat()

        try:
            result = self._execute(action_type, payload)
            action.result = result
            action.status = ActionStatus.COMPLETED
            action.completed_at = datetime.now(timezone.utc).isoformat()
            self.stats["completed_actions"] += 1
            logger.info(f"Action {action_id} completed successfully")

        except Exception as e:
            action.error = str(e)
            action.status = ActionStatus.FAILED
            action.completed_at = datetime.now(timezone.utc).isoformat()
            self.stats["failed_actions"] += 1
            logger.error(f"Action {action_id} failed: {e}")

        # Store in history
        self.action_history.append(action)
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-1000:]

        return action

    def _execute(self, action_type: ActionType, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Internal execution dispatcher."""
        if action_type == ActionType.FILE_READ:
            return self._exec_file_read(payload)
        elif action_type == ActionType.FILE_WRITE:
            return self._exec_file_write(payload)
        elif action_type == ActionType.FILE_DELETE:
            return self._exec_file_delete(payload)
        elif action_type == ActionType.FILE_MODIFY:
            return self._exec_file_modify(payload)
        elif action_type == ActionType.COMMAND_EXECUTE:
            return self._exec_command(payload)
        elif action_type == ActionType.API_CALL:
            return self._exec_api_call(payload)
        elif action_type == ActionType.TOOL_INVOKE:
            return self._exec_tool_invoke(payload)
        elif action_type == ActionType.TASK_COMPLETE:
            return self._exec_task_complete(payload)
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    def invoke_tool(
        self, tool_id: str, parameters: Dict[str, Any], source: str = "unknown"
    ) -> Action:
        """Invoke a registered tool."""
        if tool_id not in self.tools:
            action = Action(
                action_id=self._generate_id(),
                action_type=ActionType.TOOL_INVOKE,
                payload={"tool_id": tool_id, "parameters": parameters},
                source=source,
                status=ActionStatus.FAILED,
                error=f"Tool not found: {tool_id}",
            )
            return action

        tool = self.tools[tool_id]

        # Check if confirmation required
        if tool.requires_confirmation:
            # In real implementation, would request confirmation
            logger.info(f"Tool {tool_id} requires confirmation")

        # Execute via action system
        return self.execute_action(
            ActionType.TOOL_INVOKE, {"tool_id": tool_id, "parameters": parameters}, source
        )

    def _exec_file_read(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file read."""
        path = Path(payload["path"])

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        content = path.read_text()

        return {
            "path": str(path),
            "content": content,
            "size": len(content),
            "hash": hashlib.md5(content.encode()).hexdigest()[:8],
        }

    def _exec_file_write(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file write."""
        path = Path(payload["path"])
        content = payload["content"]

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content)

        return {
            "path": str(path),
            "bytes_written": len(content),
            "hash": hashlib.md5(content.encode()).hexdigest()[:8],
        }

    def _exec_file_delete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file delete."""
        path = Path(payload["path"])

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        path.unlink()

        return {"path": str(path), "deleted": True}

    def _exec_file_modify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file modification (edit)."""
        path = Path(payload["path"])

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Read current content
        content = path.read_text()

        # Apply modification
        if "old_string" in payload and "new_string" in payload:
            old = payload["old_string"]
            new = payload["new_string"]

            if old not in content:
                raise ValueError(f"Old string not found in file: {old[:50]}...")

            new_content = content.replace(old, new, 1)
            path.write_text(new_content)

            return {"path": str(path), "modifications": 1, "bytes_changed": len(new) - len(old)}
        else:
            raise ValueError("Modification requires 'old_string' and 'new_string'")

    def _exec_command(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell command."""
        command = payload["command"]
        timeout = payload.get("timeout", 30)

        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )

        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def _exec_api_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call."""

        url = payload["url"]
        method = payload.get("method", "GET")
        headers = payload.get("headers", {})
        body = payload.get("body")

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode() if body else None,
                headers=headers,
                method=method,
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                response_body = response.read().decode()
                return {
                    "url": url,
                    "status": response.status,
                    "body": response_body[:1000],  # Limit size
                }

        except urllib.error.HTTPError as e:
            return {"url": url, "status": e.code, "error": str(e)}
        except Exception as e:
            return {"url": url, "status": 0, "error": str(e)}

    def _exec_tool_invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool invocation."""
        tool_id = payload["tool_id"]
        parameters = payload.get("parameters", {})

        if tool_id not in self.tools:
            raise ValueError(f"Tool not found: {tool_id}")

        tool = self.tools[tool_id]
        return tool.handler(parameters)

    def _exec_task_complete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mark task as complete."""
        task_id = payload.get("task_id", "unknown")

        return {"task_id": task_id, "completed": True, "timestamp": datetime.now(timezone.utc).isoformat()}

    def _tool_file_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for file read."""
        return self._exec_file_read(params)

    def _tool_file_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for file write."""
        return self._exec_file_write(params)

    def _tool_file_delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for file delete."""
        return self._exec_file_delete(params)

    def _tool_command_execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for command execution."""
        return self._exec_command(params)

    def _tool_api_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for API call."""
        return self._exec_api_call(params)

    def register_tool(self, tool: Tool):
        """Register a custom tool."""
        self.tools[tool.tool_id] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_action(self, action_id: str) -> Optional[Action]:
        """Get action by ID."""
        return self.actions.get(action_id)

    def get_recent_actions(self, count: int = 10) -> List[Action]:
        """Get recent actions."""
        return self.action_history[-count:]

    def get_state(self) -> Dict[str, Any]:
        """Get current muscle state."""
        return {
            "active_actions": len(
                [a for a in self.actions.values() if a.status == ActionStatus.EXECUTING]
            ),
            "pending_actions": len(
                [a for a in self.actions.values() if a.status == ActionStatus.PENDING]
            ),
            "total_actions_ever": self.stats["total_actions"],
            "completed_actions": self.stats["completed_actions"],
            "failed_actions": self.stats["failed_actions"],
            "blocked_actions": self.stats["blocked_actions"],
            "registered_tools": len(self.tools),
            "immune_connected": self.immune_check is not None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_id(self) -> str:
        """Generate unique ID."""

        return str(uuid.uuid4())[:8]


if __name__ == "__main__":
    # Test the muscle kernel
    root = Path(__file__).parent.parent
    muscle = MuscleKernel(root)

    print("Muscle State:")
    print(json.dumps(muscle.get_state(), indent=2))

    print("\n=== Test 1: File read ===")
    action1 = muscle.execute_action(
        ActionType.FILE_READ, {"path": str(root / "00_ROOT" / "root_manifest.json")}, "TEST"
    )
    print(f"Status: {action1.status.name}, Success: {action1.result is not None}")
    if action1.result:
        print(f"Size: {action1.result.get('size')} bytes")

    print("\n=== Test 2: Tool invocation ===")
    action2 = muscle.invoke_tool("file_read", {"path": str(root / "amos_organism.py")}, "TEST")
    print(f"Status: {action2.status.name}, Success: {action2.result is not None}")

    print("\n=== Test 3: Invalid action ===")
    action3 = muscle.execute_action(ActionType.FILE_READ, {"path": "/nonexistent/file.txt"}, "TEST")
    print(f"Status: {action3.status.name}, Error: {action3.error}")

    print("\n=== Test 4: List tools ===")
    print(f"Registered tools: {list(muscle.tools.keys())}")

    print("\nFinal State:")
    print(json.dumps(muscle.get_state(), indent=2))
