"""AMOS A2A Protocol Orchestrator - Multi-Agent Communication System.

Implements Google's Agent2Agent (A2A) Protocol for multi-agent orchestration.
Enables AMOS SuperBrain to coordinate with other agents at 75% health.

References:
- Google A2A Protocol (April 2025)
- Agent2Agent Protocol Specification
- Multi-Agent Orchestration Best Practices 2025
"""

from __future__ import annotations

import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


from amos_brain import get_super_brain
from amos_brain.tools_extended import calculate


class TaskState(Enum):
    """A2A Protocol task states."""

    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input_required"
    COMPLETED = "completed"
    CANCELED = "canceled"


class MessageRole(Enum):
    """A2A message roles."""

    SYSTEM = "system"
    USER = "user"
    AGENT = "agent"


@dataclass
class AgentCard:
    """A2A Agent Card - describes agent capabilities.

    Used for agent discovery and capability advertisement.
    """

    name: str
    description: str
    version: str
    capabilities: list[str]
    skills: list[dict[str, Any]]
    endpoint: str
    authentication: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "skills": self.skills,
            "endpoint": self.endpoint,
            "authentication": self.authentication,
        }


@dataclass
class A2AMessage:
    """A2A Protocol message.

    Standard message format for agent communication.
    """

    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls, role: MessageRole, content: str, metadata: dict[str, Any] | None = None
    ) -> A2AMessage:
        """Create a new message."""
        return cls(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class A2ATask:
    """A2A Protocol task.

    Represents a unit of work assigned to an agent.
    """

    id: str
    state: TaskState
    messages: list[A2AMessage]
    artifacts: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    assigned_agent: str | None = None

    @classmethod
    def create(cls, initial_message: str, assigned_agent: str | None = None) -> A2ATask:
        """Create a new task."""
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid.uuid4()),
            state=TaskState.SUBMITTED,
            messages=[A2AMessage.create(MessageRole.USER, initial_message)],
            artifacts=[],
            created_at=now,
            updated_at=now,
            assigned_agent=assigned_agent,
        )

    def add_message(self, message: A2AMessage) -> None:
        """Add message to task."""
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)

    def update_state(self, state: TaskState) -> None:
        """Update task state."""
        self.state = state
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "state": self.state.value,
            "messages": [m.to_dict() for m in self.messages],
            "artifacts": self.artifacts,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "assigned_agent": self.assigned_agent,
        }


class A2AAgent:
    """A2A Protocol agent implementation.

    Base class for agents that can participate in A2A communication.
    """

    def __init__(
        self, name: str, description: str, capabilities: list[str], tools: list[Callable] = None
    ):
        """Initialize agent.

        Args:
            name: Agent name
            description: Agent description
            capabilities: List of capability strings
            tools: Optional list of tool functions
        """
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.tools = tools or []
        self.card = AgentCard(
            name=name,
            description=description,
            version="1.0",
            capabilities=capabilities,
            skills=[{"name": c, "description": f"Can perform {c}"} for c in capabilities],
            endpoint=f"/a2a/agents/{name.lower().replace(' ', '-')}",
        )
        self.tasks: dict[str, A2ATask] = {}
        self._lock = threading.Lock()

    def get_card(self) -> AgentCard:
        """Get agent card for discovery."""
        return self.card

    def can_handle(self, capability: str) -> bool:
        """Check if agent has capability."""
        return capability in self.capabilities

    def create_task(self, message: str) -> A2ATask:
        """Create a new task."""
        task = A2ATask.create(message, assigned_agent=self.name)
        with self._lock:
            self.tasks[task.id] = task
        return task

    def process_task(self, task: A2ATask) -> A2ATask:
        """Process a task. Override in subclasses.

        Args:
            task: Task to process

        Returns:
            Updated task
        """
        # Default implementation - mark as working
        task.update_state(TaskState.WORKING)

        # Add system response
        response = A2AMessage.create(
            MessageRole.AGENT,
            f"Agent {self.name} received task: {task.messages[0].content[:50]}...",
            {"agent": self.name},
        )
        task.add_message(response)

        # Mark complete
        task.update_state(TaskState.COMPLETED)
        return task


class AMOSSuperBrainAgent(A2AAgent):
    """AMOS SuperBrain as an A2A agent.

    Wraps the SuperBrain to participate in multi-agent orchestration.
    """

    def __init__(self, brain=None):
        """Initialize with SuperBrain instance."""

        self.brain = brain or get_super_brain()
        state = self.brain.get_state()

        super().__init__(
            name="AMOS SuperBrain",
            description=f"AMOS SuperBrain v3.0 - {state.health_score:.0%} health, {len(state.loaded_tools)} tools",
            capabilities=[
                "code_analysis",
                "file_operations",
                "web_search",
                "calculations",
                "git_operations",
                "database_queries",
                "system_info",
                "json_validation",
            ],
        )

    def process_task(self, task: A2ATask) -> A2ATask:
        """Process task using SuperBrain tools."""
        task.update_state(TaskState.WORKING)

        user_message = task.messages[0].content if task.messages else ""

        # Use SuperBrain to process
        try:
            # Check which tool to use based on message content
            tool_result = self._route_to_tool(user_message)

            response = A2AMessage.create(
                MessageRole.AGENT,
                tool_result,
                {"agent": self.name, "tools_used": self._detect_tools(user_message)},
            )
        except Exception as e:
            response = A2AMessage.create(
                MessageRole.AGENT, f"Error processing task: {e}", {"error": True}
            )

        task.add_message(response)
        task.update_state(TaskState.COMPLETED)
        return task

    def _route_to_tool(self, message: str) -> str:
        """Route message to appropriate tool."""
        msg_lower = message.lower()

        if "calculate" in msg_lower or any(c.isdigit() for c in message):
            expr = message.replace("calculate", "").strip()
            result = calculate(expr)
            return f"Calculation result: {result}"

        if "search" in msg_lower:
            return "Web search would be performed here (requires API key for 100% health)"

        if "file" in msg_lower:
            return "File operations available (use file_read_write tool)"

        return f"AMOS SuperBrain processed: {message[:100]}..."

    def _detect_tools(self, message: str) -> list[str]:
        """Detect which tools would be used."""
        msg_lower = message.lower()
        tools = []

        if "calculate" in msg_lower or any(c.isdigit() for c in message):
            tools.append("calculate")
        if "search" in msg_lower:
            tools.append("web_search")
        if "file" in msg_lower:
            tools.append("file_read_write")

        return tools


class A2AHostAgent:
    """A2A Host Agent - orchestrates multiple agents.

    Manages agent discovery, task routing, and coordination.
    """

    def __init__(self):
        """Initialize host agent."""
        self.agents: dict[str, A2AAgent] = {}
        self.tasks: dict[str, A2ATask] = {}
        self._lock = threading.Lock()

    def register_agent(self, agent: A2AAgent) -> bool:
        """Register an agent with the host.

        Args:
            agent: Agent to register

        Returns:
            True if registered successfully
        """
        with self._lock:
            self.agents[agent.name] = agent
        print(f"✅ A2A: Agent '{agent.name}' registered")
        return True

    def discover_agents(self, capability: str | None = None) -> list[AgentCard]:
        """Discover available agents.

        Args:
            capability: Optional capability filter

        Returns:
            List of agent cards
        """
        cards = []
        for agent in self.agents.values():
            if capability is None or agent.can_handle(capability):
                cards.append(agent.get_card())
        return cards

    def route_task(self, message: str, capability: str | None = None) -> A2ATask:
        """Route task to appropriate agent.

        Args:
            message: Task message
            capability: Required capability

        Returns:
            Created task
        """
        # Find capable agent
        target_agent = None
        for agent in self.agents.values():
            if capability and agent.can_handle(capability):
                target_agent = agent
                break
            elif capability is None:
                target_agent = agent
                break

        if target_agent is None:
            # Create unassigned task
            task = A2ATask.create(message)
            with self._lock:
                self.tasks[task.id] = task
            return task

        # Create and assign task
        task = target_agent.create_task(message)

        # Process task
        task = target_agent.process_task(task)

        with self._lock:
            self.tasks[task.id] = task

        return task

    def get_task_status(self, task_id: str) -> dict[str, Any]:
        """Get task status.

        Args:
            task_id: Task ID

        Returns:
            Task status or None if not found
        """
        with self._lock:
            task = self.tasks.get(task_id)

        if task:
            return {
                "id": task.id,
                "state": task.state.value,
                "agent": task.assigned_agent,
                "message_count": len(task.messages),
                "created": task.created_at.isoformat(),
            }
        return None

    def get_stats(self) -> dict[str, Any]:
        """Get orchestrator statistics."""
        with self._lock:
            return {
                "registered_agents": len(self.agents),
                "agent_names": list(self.agents.keys()),
                "total_tasks": len(self.tasks),
                "completed_tasks": sum(
                    1 for t in self.tasks.values() if t.state == TaskState.COMPLETED
                ),
                "working_tasks": sum(
                    1 for t in self.tasks.values() if t.state == TaskState.WORKING
                ),
            }


# Global orchestrator instance
_orchestrator: A2AHostAgent | None = None


def get_a2a_orchestrator() -> A2AHostAgent:
    """Get or create global A2A orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = A2AHostAgent()

        # Auto-register AMOS SuperBrain
        try:
            amos_agent = AMOSSuperBrainAgent()
            _orchestrator.register_agent(amos_agent)
        except Exception as e:
            print(f"⚠️ A2A: Could not auto-register AMOS SuperBrain: {e}")

    return _orchestrator


def initialize_a2a_protocol() -> dict[str, Any]:
    """Initialize A2A protocol and return status.

    Returns:
        Initialization status
    """
    try:
        orchestrator = get_a2a_orchestrator()
        stats = orchestrator.get_stats()

        return {
            "success": True,
            "status": "A2A Protocol Active",
            "orchestrator": "A2AHostAgent",
            "registered_agents": stats["registered_agents"],
            "agents": stats["agent_names"],
            "capabilities": ["agent_discovery", "task_routing", "multi_agent_coordination"],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
