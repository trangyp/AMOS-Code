"""A2A (Agent2Agent) Protocol Implementation for AMOS SuperBrain.

Implements Google's A2A protocol for agent-to-agent communication.
Complements MCP (Model Context Protocol) which handles agent-to-tool.

A2A Design Principles:
1. Embrace agentic capabilities - agents collaborate without sharing memory/tools
2. Build on existing standards - HTTP, SSE, JSON-RPC
3. Secure by default - Enterprise-grade authentication
4. Support long-running tasks - Hours to days with human-in-loop
5. Modality agnostic - Text, audio, video streaming

Reference: https://a2a-protocol.org/latest/
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum, auto
from typing import Any



class TaskState(Enum):
    """A2A task states."""

    SUBMITTED = auto()
    WORKING = auto()
    INPUT_REQUIRED = auto()
    COMPLETED = auto()
    CANCELED = auto()


@dataclass
class A2AMessage:
    """A2A protocol message."""

    message_id: str
    task_id: str
    role: str  # "user" | "agent"
    content: str
    content_type: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "task_id": self.task_id,
            "role": self.role,
            "content": self.content,
            "content_type": self.content_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass
class A2ATask:
    """A2A protocol task."""

    task_id: str
    state: TaskState
    messages: list[A2AMessage] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_message(self, message: A2AMessage) -> None:
        """Add a message to the task."""
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "state": self.state.name,
            "messages": [m.to_dict() for m in self.messages],
            "artifacts": self.artifacts,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class A2AAgent:
    """A2A agent definition."""

    agent_id: str
    name: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    endpoint: str = None
    skills: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "endpoint": self.endpoint,
            "skills": self.skills,
        }


class A2AProtocol:
    """A2A Protocol handler for AMOS SuperBrain.

    Enables AMOS to communicate with other agents using the A2A standard.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, A2ATask] = {}
        self._agents: dict[str, A2AAgent] = {}
        self._handlers: dict[str, Callable[[A2ATask], None]] = {}

    def register_agent(self, agent: A2AAgent) -> bool:
        """Register an agent in the A2A network.

        Args:
            agent: Agent definition

        Returns:
            True if registration successful
        """
        self._agents[agent.agent_id] = agent
        return True

    def register_handler(self, capability: str, handler: Callable[[A2ATask], None]) -> bool:
        """Register a handler for a specific capability.

        Args:
            capability: Capability name (e.g., "code_review", "data_analysis")
            handler: Function to handle tasks with this capability

        Returns:
            True if registration successful
        """
        self._handlers[capability] = handler
        return True

    def create_task(
        self, initial_message: str, target_agent_id: str = None, context: dict[str, Any] = None
    ) -> A2ATask:
        """Create a new A2A task.

        Args:
            initial_message: Initial user message
            target_agent_id: Optional target agent ID
            context: Optional context

        Returns:
            Created task
        """
        task_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())

        task = A2ATask(
            task_id=task_id,
            state=TaskState.SUBMITTED,
        )

        # Add initial user message
        message = A2AMessage(
            message_id=message_id,
            task_id=task_id,
            role="user",
            content=initial_message,
            metadata=context or {},
        )
        task.add_message(message)

        self._tasks[task_id] = task

        return task

    def process_task(self, task_id: str) -> A2ATask:
        """Process a task through the A2A protocol.

        Args:
            task_id: Task ID to process

        Returns:
            Updated task
        """
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Update state to working
        task.state = TaskState.WORKING
        task.updated_at = datetime.now(timezone.utc).isoformat()

        # Find appropriate handler based on message content
        last_message = task.messages[-1] if task.messages else None
        if last_message:
            content = last_message.content.lower()

            # Route to appropriate handler
            for capability, handler in self._handlers.items():
                if capability.lower() in content:
                    handler(task)
                    break

        return task

    def complete_task(
        self, task_id: str, result: str, artifacts: list[dict[str, Any]] = None
    ) -> A2ATask:
        """Complete a task with results.

        Args:
            task_id: Task ID
            result: Result content
            artifacts: Optional artifacts

        Returns:
            Updated task
        """
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Add agent response
        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            task_id=task_id,
            role="agent",
            content=result,
        )
        task.add_message(message)

        # Update state and artifacts
        task.state = TaskState.COMPLETED
        if artifacts:
            task.artifacts.extend(artifacts)

        return task

    def list_agents(self, capability: str = None) -> list[A2AAgent]:
        """List registered agents.

        Args:
            capability: Optional capability filter

        Returns:
            List of agents
        """
        if capability:
            return [agent for agent in self._agents.values() if capability in agent.capabilities]
        return list(self._agents.values())

    def get_task(self, task_id: str) -> A2ATask | None:
        """Get a task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def list_tasks(self, state: TaskState | None = None) -> list[A2ATask]:
        """List tasks.

        Args:
            state: Optional state filter

        Returns:
            List of tasks
        """
        if state:
            return [t for t in self._tasks.values() if t.state == state]
        return list(self._tasks.values())

    def to_json(self) -> str:
        """Serialize protocol state to JSON.

        Returns:
            JSON string
        """
        return json.dumps(
            {
                "agents": {k: v.to_dict() for k, v in self._agents.items()},
                "tasks": {k: v.to_dict() for k, v in self._tasks.items()},
                "handlers": list(self._handlers.keys()),
            },
            indent=2,
        )


def create_amos_a2a_agent() -> A2AAgent:
    """Create the default AMOS SuperBrain A2A agent.

    Returns:
        AMOS A2A agent definition
    """
    return A2AAgent(
        agent_id="amos-superbrain",
        name="AMOS SuperBrain",
        description="Architectural Multi-agent Operating System with 52 technology domains and 145+ equations",
        capabilities=[
            "code_analysis",
            "architecture_design",
            "mathematical_modeling",
            "multi_agent_orchestration",
            "tool_execution",
            "knowledge_query",
        ],
        skills=[
            {
                "id": "analyze_code",
                "name": "Code Analysis",
                "description": "Analyze Python code structure and extract functions, classes, imports",
            },
            {
                "id": "search_files",
                "name": "File Search",
                "description": "Search for files matching glob patterns",
            },
            {
                "id": "execute_shell",
                "name": "Shell Execution",
                "description": "Execute shell commands safely with timeout",
            },
            {
                "id": "validate_json",
                "name": "JSON Validation",
                "description": "Validate and parse JSON data",
            },
            {
                "id": "system_info",
                "name": "System Information",
                "description": "Get system metrics and environment details",
            },
        ],
    )
