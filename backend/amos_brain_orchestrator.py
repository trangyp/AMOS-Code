"""AMOS Brain Orchestrator - Unified Cognitive Operating System.

The central orchestration layer that integrates all AMOS subsystems into a
unified, coherent cognitive operating system. Provides the main interface
for agent lifecycle, task execution, and system coordination.

Features:
- Unified agent lifecycle management
- Task execution pipeline with all governance layers
- System health monitoring and coordination
- Cross-subsystem event propagation
- Graceful degradation and recovery
- Comprehensive system telemetry

Integration Layers:
- AI Governance & Safety
- AI Cost Management
- AI Agent Cognitive Systems
- Plugin System
- Knowledge & Memory
- Reasoning & Planning
- Messaging & Communication
- Observability & Tracing

Creator: Trang Phan
Version: 3.0.0
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime

UTC = UTC
from enum import Enum
from typing import Any

from agent_knowledge import knowledge_manager, recall
from agent_messaging import AgentMessage, message_bus
from agent_plugin_system import plugin_registry
from agent_reasoning import reason_with_react, reasoning_engine
from ai_cost_manager import cost_manager, track_llm_cost

# Import all AMOS subsystems
from ai_governance import (
    governance_engine,
    validate_output_with_governance,
    validate_with_governance,
)


class AgentStatus(Enum):
    """Agent lifecycle status."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class TaskPriority(Enum):
    """Task priority levels."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class AgentContext:
    """Context for an agent instance."""

    agent_id: str
    agent_type: str
    status: str = "initializing"
    capabilities: list[str] = field(default_factory=list)
    memory: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_active: str = None
    total_tasks: int = 0
    successful_tasks: int = 0


@dataclass
class TaskRequest:
    """Represents a task to be executed."""

    task_id: str
    agent_id: str
    task_type: str
    input_data: dict[str, Any]
    priority: int = 2
    context: dict[str, Any] = field(default_factory=dict)
    use_reasoning: bool = True
    use_knowledge: bool = True
    use_governance: bool = True
    use_cost_control: bool = True


@dataclass
class TaskResult:
    """Result of task execution."""

    task_id: str
    agent_id: str
    success: bool
    output: Any
    reasoning_chain: str = None
    knowledge_used: list[str] = field(default_factory=list)
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    violations: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class AMOSBrainOrchestrator:
    """Central orchestrator for the AMOS Cognitive Operating System."""

    def __init__(self):
        self.agents: dict[str, AgentContext] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.running_tasks: dict[str, asyncio.Task] = {}
        self.system_health: dict[str, Any] = {"status": "initializing", "subsystems": {}}
        self.initialized = False
        self._shutdown_event = asyncio.Event()

    async def initialize(self) -> bool:
        """Initialize all AMOS subsystems."""
        print("🧠 Initializing AMOS Brain Orchestrator...")

        try:
            # Initialize knowledge manager
            await knowledge_manager.initialize()
            self.system_health["subsystems"]["knowledge"] = "active"

            # Start message bus
            await message_bus.start()
            self.system_health["subsystems"]["messaging"] = "active"

            # Discover and load plugins
            if os.getenv("PLUGINS_ENABLED", "true").lower() == "true":
                plugins = await plugin_registry.discover_plugins()
                for plugin_path in plugins:
                    await plugin_registry.load_plugin(plugin_path)
                self.system_health["subsystems"]["plugins"] = "active"

            # Mark as initialized
            self.initialized = True
            self.system_health["status"] = "active"

            print("✅ AMOS Brain Orchestrator initialized successfully")
            return True

        except Exception as e:
            self.system_health["status"] = "error"
            self.system_health["error"] = str(e)
            print(f"❌ Initialization failed: {e}")
            return False

    async def create_agent(
        self, agent_type: str, capabilities: list[str] = None, config: dict[str, Any] = None
    ) -> AgentContext:
        """Create and register a new agent."""
        import uuid

        agent_id = f"{agent_type}_{str(uuid.uuid4())[:8]}"

        agent = AgentContext(
            agent_id=agent_id,
            agent_type=agent_type,
            status=AgentStatus.ACTIVE.value,
            capabilities=capabilities or [],
            config=config or {},
        )

        self.agents[agent_id] = agent

        # Subscribe agent to message bus
        await message_bus.subscribe(agent_id, self._agent_message_handler)

        print(f"✅ Agent created: {agent_id} ({agent_type})")
        return agent

    async def _agent_message_handler(self, message: AgentMessage):
        """Handle incoming messages for agents."""
        agent_id = message.recipient_id
        agent = self.agents.get(agent_id)

        if not agent:
            return

        # Update last active
        agent.last_active = datetime.now(UTC).isoformat()

        # Handle different message types
        if message.message_type == "task":
            # Create task from message
            task = TaskRequest(
                task_id=message.message_id,
                agent_id=agent_id,
                task_type=message.content.get("task_type", "default"),
                input_data=message.content.get("input", {}),
                priority=message.priority,
            )
            await self.submit_task(task)

    async def submit_task(self, task: TaskRequest) -> str:
        """Submit a task for execution."""
        # Add to priority queue
        await self.task_queue.put((task.priority, task.task_id, task))

        print(f"📋 Task submitted: {task.task_id} (priority: {task.priority})")
        return task.task_id

    async def execute_task(self, task: TaskRequest) -> TaskResult:
        """Execute a task through the full AMOS pipeline."""
        import time

        start_time = time.time()

        agent = self.agents.get(task.agent_id)
        if not agent:
            return TaskResult(
                task_id=task.task_id,
                agent_id=task.agent_id,
                success=False,
                output="Agent not found",
            )

        # Update agent status
        agent.status = AgentStatus.BUSY.value
        agent.total_tasks += 1

        # Initialize result
        result = TaskResult(task_id=task.task_id, agent_id=task.agent_id, success=True, output=None)

        try:
            # Step 1: Governance validation (input)
            if task.use_governance:
                validation = await validate_with_governance(task.agent_id, str(task.input_data))
                if not validation["valid"]:
                    result.success = False
                    result.output = "Governance validation failed"
                    result.violations = [v["policy_name"] for v in validation["violations"]]
                    return result

            # Step 2: Knowledge retrieval
            knowledge_context = ""
            if task.use_knowledge and task.input_data.get("query"):
                knowledge_result = await recall(task.input_data["query"])
                knowledge_context = knowledge_result.context
                result.knowledge_used = [c.content[:50] for c in knowledge_result.chunks]

            # Step 3: Reasoning and execution
            if task.use_reasoning:
                # Create reasoning chain
                chain = reasoning_engine.create_chain(
                    task.agent_id,
                    str(task.input_data),
                )

                # Execute with reasoning
                async def llm_call(prompt: str) -> str:
                    # Track cost
                    usage = await track_llm_cost("gpt-4o", len(prompt.split()), 100, task.agent_id)
                    result.cost_usd += usage.cost_usd

                    # Simulate LLM response
                    return f"Processed: {prompt[:50]}..."

                reasoning_result = await reason_with_react(
                    task.agent_id, str(task.input_data), llm_call
                )

                result.output = reasoning_result
                result.reasoning_chain = chain.chain_id
            else:
                # Direct execution
                result.output = await self._execute_direct(task)

            # Step 4: Governance validation (output)
            if task.use_governance:
                output_validation = await validate_output_with_governance(
                    task.agent_id, str(task.input_data), str(result.output)
                )
                if not output_validation["valid"]:
                    result.output = output_validation.get("output", result.output)
                    result.violations.extend(
                        [v["policy_name"] for v in output_validation["violations"]]
                    )

            # Step 5: Track cost
            if task.use_cost_control:
                budget_available = cost_manager.check_budget_available("default", result.cost_usd)
                if not budget_available:
                    result.success = False
                    result.output = "Budget exceeded"
                    return result

            # Success
            agent.successful_tasks += 1

        except Exception as e:
            result.success = False
            result.output = f"Error: {str(e)}"
            agent.status = AgentStatus.ERROR.value

        finally:
            # Calculate latency
            result.latency_ms = (time.time() - start_time) * 1000

            # Update agent status
            agent.status = AgentStatus.ACTIVE.value
            agent.last_active = datetime.now(UTC).isoformat()

        return result

    async def _execute_direct(self, task: TaskRequest) -> Any:
        """Execute task directly without reasoning."""
        # Check for plugin tools
        tools = plugin_registry.get_available_tools()
        if task.task_type in tools:
            tool = tools[task.task_type]
            return await tool(task.input_data)

        # Default execution
        return f"Executed {task.task_type} with input: {task.input_data}"

    async def get_agent_status(self, agent_id: str) -> dict[str, Any]:
        """Get detailed agent status."""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        return {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type,
            "status": agent.status,
            "capabilities": agent.capabilities,
            "total_tasks": agent.total_tasks,
            "successful_tasks": agent.successful_tasks,
            "success_rate": round(agent.successful_tasks / agent.total_tasks * 100, 1)
            if agent.total_tasks > 0
            else 0,
            "created_at": agent.created_at,
            "last_active": agent.last_active,
        }

    async def get_system_health(self) -> dict[str, Any]:
        """Get comprehensive system health status."""
        # Aggregate subsystem health
        health = {
            "orchestrator": self.system_health["status"],
            "agents": {
                "total": len(self.agents),
                "active": len(
                    [a for a in self.agents.values() if a.status == AgentStatus.ACTIVE.value]
                ),
                "busy": len(
                    [a for a in self.agents.values() if a.status == AgentStatus.BUSY.value]
                ),
                "error": len(
                    [a for a in self.agents.values() if a.status == AgentStatus.ERROR.value]
                ),
            },
            "subsystems": {
                "governance": "active" if governance_engine else "inactive",
                "cost_manager": "active" if cost_manager else "inactive",
                "knowledge": "active" if knowledge_manager.initialized else "inactive",
                "messaging": "active" if message_bus._running else "inactive",
                "plugins": len(plugin_registry.plugins),
            },
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return health

    async def broadcast_system_message(self, message_type: str, content: dict[str, Any]) -> bool:
        """Broadcast a message to all agents."""
        await message_bus.broadcast("system", {"type": message_type, "content": content})
        return True

    async def shutdown(self):
        """Gracefully shutdown the orchestrator."""
        print("🛑 Shutting down AMOS Brain Orchestrator...")

        self._shutdown_event.set()

        # Cancel running tasks
        for task_id, task in self.running_tasks.items():
            if not task.done():
                task.cancel()

        # Stop message bus
        await message_bus.stop()

        # Shutdown all agents
        for agent in self.agents.values():
            agent.status = AgentStatus.SHUTDOWN.value

        self.system_health["status"] = "shutdown"
        print("✅ AMOS Brain Orchestrator shutdown complete")


# Global orchestrator instance
amos_brain = AMOSBrainOrchestrator()


# Convenience functions
async def initialize_amos() -> bool:
    """Initialize the AMOS Brain."""
    return await amos_brain.initialize()


async def create_agent(agent_type: str, capabilities: list[str] = None) -> AgentContext:
    """Create a new agent."""
    return await amos_brain.create_agent(agent_type, capabilities)


async def execute_task(
    agent_id: str, task_type: str, input_data: dict[str, Any], priority: int = 2
) -> TaskResult:
    """Execute a task."""
    import uuid

    task = TaskRequest(
        task_id=str(uuid.uuid4())[:8],
        agent_id=agent_id,
        task_type=task_type,
        input_data=input_data,
        priority=priority,
    )
    return await amos_brain.execute_task(task)


async def get_health() -> dict[str, Any]:
    """Get system health."""
    return await amos_brain.get_system_health()


async def shutdown_amos():
    """Shutdown AMOS."""
    await amos_brain.shutdown()
