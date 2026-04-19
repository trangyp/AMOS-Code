from typing import Any, Optional

"""AMOS Agent Service - Autonomous Agent Orchestration

Production-grade multi-agent system with:
- Agent lifecycle management (spawn, monitor, terminate)
- Agent-to-agent communication
- Tool/ capability registry
- Memory and context management
- Task delegation and coordination

Based on modern agent architectures (AutoGPT, CrewAI, LangChain patterns).

Owner: Trang Phan
Version: 2.0.0
"""

import asyncio
import json
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone

from enum import Enum

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

try:
    from backend.data_pipeline.streaming import publish_event
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False

class AgentStatus(Enum):
    """Agent lifecycle status."""

    SPAWNING = "spawning"
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    TERMINATING = "terminating"
    TERMINATED = "terminated"
    ERROR = "error"

class AgentCapability(Enum):
    """Agent capability types."""

    REASONING = "reasoning"
    CODE_EXECUTION = "code_execution"
    WEB_SEARCH = "web_search"
    FILE_OPERATIONS = "file_operations"
    API_CALLS = "api_calls"
    MEMORY_ACCESS = "memory_access"
    TOOL_USE = "tool_use"

@dataclass
class AgentMemory:
    """Agent working memory."""

    short_term: list[dict[str, Any]] = field(default_factory=list)
    long_term_refs: List[str] = field(default_factory=list)
    context_window: int = 4096
    last_accessed: float = field(default_factory=time.time)

@dataclass
class AgentConfig:
    """Agent configuration."""

    agent_id: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    max_tasks: int = 10
    timeout_seconds: float = 300.0
    memory_limit_mb: int = 512
    allow_delegation: bool = True
    verbose: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class Task:
    """Task for agent execution."""

    task_id: str
    description: str
    priority: int = 5  # 1-10, higher = more important
    status: str = "pending"
    assigned_agent: Optional[str] = None
    parent_task: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    result: Any = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

@dataclass
class AgentInstance:
    """Running agent instance."""

    agent_id: str
    config: AgentConfig
    status: AgentStatus
    memory: AgentMemory
    current_task: Optional[str] = None
    task_history: List[str] = field(default_factory=list)
    spawned_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0

class ToolRegistry:
    """Registry of tools available to agents."""

    def __init__(self):
        self._tools: dict[str, Callable[..., Any]] = {}
        self._descriptions: Dict[str, str] = {}
        self._capabilities: dict[str, list[AgentCapability]] = {}

    def register(
        self,
        name: str,
        handler: Callable[..., Any],
        description: str,
        required_caps: List[AgentCapability],
    ) -> None:
        """Register a new tool."""
        self._tools[name] = handler
        self._descriptions[name] = description
        self._capabilities[name] = required_caps

    def get_tool(self, name: str) -> Callable[..., Any] :
        """Get tool handler by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools."""
        return [
            {
                "name": name,
                "description": self._descriptions[name],
                "capabilities": [c.value for c in self._capabilities[name]],
            }
            for name in self._tools
        ]

    def can_use_tool(self, tool_name: str, agent_caps: List[AgentCapability]) -> bool:
        """Check if agent can use tool."""
        required = self._capabilities.get(tool_name, [])
        return all(cap in agent_caps for cap in required)

class AgentService:
    """Multi-agent orchestration service.

    Manages agent lifecycle, task delegation, and inter-agent
    communication with SuperBrain governance.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or "redis://localhost:6379/13"
        self._agents: Dict[str, AgentInstance] = {}
        self._tasks: Dict[str, Task] = {}
        self._tool_registry = ToolRegistry()
        self._redis: redis.Optional[Redis] = None

        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
            except Exception:
                pass

        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register default agent tools."""
        self._tool_registry.register(
            "calculator",
            lambda expr: eval(expr),  # Simple eval for demo
            "Evaluate mathematical expressions",
            [AgentCapability.CODE_EXECUTION],
        )

        self._tool_registry.register(
            "web_search",
            lambda query: {"results": f"Search for: {query}"},
            "Search the web for information",
            [AgentCapability.WEB_SEARCH],
        )

        self._tool_registry.register(
            "memory_store",
            lambda key, value: {"stored": True, "key": key},
            "Store information in agent memory",
            [AgentCapability.MEMORY_ACCESS],
        )

    async def spawn_agent(self, config: AgentConfig) -> str:
        """Spawn a new agent instance.

        Args:
            config: Agent configuration

        Returns:
            Agent ID
        """
        # Validate with SuperBrain
        if SUPERBRAIN_AVAILABLE:
            try:
                brain = get_super_brain()
                if brain and hasattr(brain, "action_gate"):
                    result = brain.action_gate.validate_action(
                        agent_id="agent_service",
                        action="spawn_agent",
                        details={
                            "agent_id": config.agent_id,
                            "name": config.name,
                            "capabilities": [c.value for c in config.capabilities],
                        },
                    )
                    if not result.authorized:
                        raise PermissionError(f"Agent spawn blocked: {result.reason}")
            except Exception:
                pass

        agent = AgentInstance(
            agent_id=config.agent_id, config=config, status=AgentStatus.IDLE, memory=AgentMemory()
        )

        self._agents[config.agent_id] = agent

        # Persist state
        if self._redis:
            try:
                await self._redis.setex(
                    f"agent:{config.agent_id}",
                    86400,
                    json.dumps(
                        {
                            "agent_id": config.agent_id,
                            "name": config.name,
                            "status": agent.status.value,
                            "capabilities": [c.value for c in config.capabilities],
                            "spawned_at": agent.spawned_at,
                        }
                    ),
                )
            except Exception:
                pass

        # Publish event
        if STREAMING_AVAILABLE:
            try:
                publish_event(
                    event_type="agent_spawned",
                    source_system="agent_service",
                    payload={"agent_id": config.agent_id, "name": config.name},
                    requires_governance=True,
                )
            except Exception:
                pass

        return config.agent_id

    async def assign_task(
        self, agent_id: str, description: str, priority: int = 5, parent_task: Optional[str] = None
    ) -> str:
        """Assign task to agent.

        Args:
            agent_id: Target agent
            description: Task description
            priority: Task priority (1-10)
            parent_task: Parent task ID for subtasks

        Returns:
            Task ID
        """
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        if agent.status == AgentStatus.TERMINATED:
            raise ValueError(f"Agent {agent_id} is terminated")

        task_id = f"task_{uuid.uuid4().hex[:12]}"

        task = Task(
            task_id=task_id,
            description=description,
            priority=priority,
            assigned_agent=agent_id,
            parent_task=parent_task,
        )

        self._tasks[task_id] = task

        # Update agent status
        agent.status = AgentStatus.RUNNING
        agent.current_task = task_id

        # Execute task
        asyncio.create_task(self._execute_task(agent_id, task_id))

        return task_id

    async def _execute_task(self, agent_id: str, task_id: str) -> None:
        """Execute agent task."""
        agent = self._agents[agent_id]
        task = self._tasks[task_id]

        task.status = "running"
        task.started_at = time.time()

        try:
            # Simulate task execution (in production, this would call LLM or tool)
            await asyncio.sleep(0.1)

            # Check if task needs tool use
            if "calculate" in task.description.lower():
                tool = self._tool_registry.get_tool("calculator")
                if tool:
                    # Extract expression
                    expr = task.description.replace("calculate", "").strip()
                    try:
                        result = tool(expr)
                        task.result = {"calculation": result}
                    except Exception as e:
                        task.error = f"Calculation error: {e}"
            else:
                task.result = {"status": "completed", "description": task.description}

            task.status = "completed"
            task.completed_at = time.time()
            agent.total_tasks_completed += 1

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            agent.total_tasks_failed += 1

        finally:
            agent.current_task = None
            agent.task_history.append(task_id)
            agent.status = AgentStatus.IDLE
            agent.last_heartbeat = time.time()

            # Persist
            await self._checkpoint_agent(agent)

    async def _checkpoint_agent(self, agent: AgentInstance) -> None:
        """Persist agent state."""
        if not self._redis:
            return

        try:
            await self._redis.setex(
                f"agent:{agent.agent_id}",
                86400,
                json.dumps(
                    {
                        "agent_id": agent.agent_id,
                        "status": agent.status.value,
                        "tasks_completed": agent.total_tasks_completed,
                        "tasks_failed": agent.total_tasks_failed,
                        "last_heartbeat": agent.last_heartbeat,
                    }
                ),
            )
        except Exception:
            pass

    async def terminate_agent(self, agent_id: str) -> bool:
        """Terminate an agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            return False

        agent.status = AgentStatus.TERMINATING

        # Cancel current task if any
        if agent.current_task:
            task = self._tasks.get(agent.current_task)
            if task:
                task.status = "cancelled"

        agent.status = AgentStatus.TERMINATED

        if STREAMING_AVAILABLE:
            try:
                publish_event(
                    event_type="agent_terminated",
                    source_system="agent_service",
                    payload={"agent_id": agent_id},
                )
            except Exception:
                pass

        return True

    async def delegate_task(
        self, from_agent_id: str, to_agent_id: str, description: str, priority: int = 5
    ) -> Optional[str]:
        """Delegate task from one agent to another."""
        from_agent = self._agents.get(from_agent_id)
        if not from_agent or not from_agent.config.allow_delegation:
            return None

        to_agent = self._agents.get(to_agent_id)
        if not to_agent or to_agent.status == AgentStatus.TERMINATED:
            return None

        # Create subtask
        task_id = await self.assign_task(
            to_agent_id, description, priority, parent_task=from_agent.current_task
        )

        return task_id

    def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """Get agent by ID."""
        return self._agents.get(agent_id)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self._tasks.get(task_id)

    def list_agents(self, status: Optional[AgentStatus] = None) -> List[AgentInstance]:
        """List agents, optionally filtered by status."""
        agents = list(self._agents.values())
        if status:
            agents = [a for a in agents if a.status == status]
        return agents

    def list_tasks(
        self, agent_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[Task]:
        """List tasks with optional filters."""
        tasks = list(self._tasks.values())

        if agent_id:
            tasks = [t for t in tasks if t.assigned_agent == agent_id]

        if status:
            tasks = [t for t in tasks if t.status == status]

        return tasks

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "total_agents": len(self._agents),
            "active_agents": len(
                [a for a in self._agents.values() if a.status != AgentStatus.TERMINATED]
            ),
            "total_tasks": len(self._tasks),
            "pending_tasks": len([t for t in self._tasks.values() if t.status == "pending"]),
            "running_tasks": len([t for t in self._tasks.values() if t.status == "running"]),
            "completed_tasks": len([t for t in self._tasks.values() if t.status == "completed"]),
            "registered_tools": len(self._tool_registry.list_tools()),
        }

# Global instance
agent_service = AgentService()
