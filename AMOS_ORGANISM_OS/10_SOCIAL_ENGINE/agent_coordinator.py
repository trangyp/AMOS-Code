"""Agent Coordinator — Multi-Agent Task Distribution

Coordinates multiple agents for collaborative task execution.
Manages agent pools, task distribution, and result aggregation.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Status of an agent task."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentTask:
    """A task to be executed by an agent."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    task_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: str = None
    result: Dict[str, Any] = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
        }


@dataclass
class AgentPool:
    """A pool of agents for task execution."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    agent_type: str = ""
    capabilities: List[str] = field(default_factory=list)
    agent_ids: List[str] = field(default_factory=list)
    max_concurrent: int = 5
    active_tasks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AgentCoordinator:
    """Coordinates multiple agents for collaborative execution.

    Manages agent pools, distributes tasks, tracks progress,
    and aggregates results from multiple agents.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.pools: Dict[str, AgentPool] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.agent_status: Dict[str, dict[str, Any]] = {}

        self._init_default_pools()

    def _init_default_pools(self):
        """Create default agent pools."""
        # General purpose agents
        general = AgentPool(
            name="general_agents",
            agent_type="general",
            capabilities=["research", "analysis", "writing"],
            max_concurrent=10,
        )
        self.pools[general.id] = general

        # Specialized agents
        specialist = AgentPool(
            name="specialist_agents",
            agent_type="specialist",
            capabilities=["code", "design", "testing"],
            max_concurrent=5,
        )
        self.pools[specialist.id] = specialist

        # External agents
        external = AgentPool(
            name="external_agents",
            agent_type="external",
            capabilities=["api", "integration", "coordination"],
            max_concurrent=3,
        )
        self.pools[external.id] = external

    def create_pool(
        self,
        name: str,
        agent_type: str,
        capabilities: List[str],
        max_concurrent: int = 5,
    ) -> AgentPool:
        """Create a new agent pool."""
        pool = AgentPool(
            name=name,
            agent_type=agent_type,
            capabilities=capabilities,
            max_concurrent=max_concurrent,
        )
        self.pools[pool.id] = pool
        return pool

    def create_task(
        self,
        name: str,
        task_type: str,
        parameters: Dict[str, Any],
        description: str = "",
    ) -> AgentTask:
        """Create a new task."""
        task = AgentTask(
            name=name,
            description=description,
            task_type=task_type,
            parameters=parameters,
        )
        self.tasks[task.id] = task
        return task

    def assign_task(self, task_id: str, pool_id: str = None) -> bool:
        """Assign a task to an agent pool."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        # Find suitable pool if not specified
        if pool_id is None:
            for pid, pool in self.pools.items():
                if task.task_type in pool.capabilities:
                    if len(pool.active_tasks) < pool.max_concurrent:
                        pool_id = pid
                        break

        if not pool_id:
            return False

        pool = self.pools.get(pool_id)
        if not pool:
            return False

        # Assign task
        task.assigned_agent = f"{pool.agent_type}_{len(pool.active_tasks)}"
        task.status = TaskStatus.ASSIGNED
        pool.active_tasks.append(task_id)

        return True

    def complete_task(
        self,
        task_id: str,
        result: Dict[str, Any],
        success: bool = True,
    ) -> bool:
        """Mark a task as completed."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.result = result
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.completed_at = datetime.now(UTC).isoformat()

        # Remove from pool's active tasks
        for pool in self.pools.values():
            if task_id in pool.active_tasks:
                pool.active_tasks.remove(task_id)

        self._save_tasks()
        return True

    def get_pool_status(self, pool_id: str) -> Dict[str, Any]:
        """Get status of an agent pool."""
        pool = self.pools.get(pool_id)
        if not pool:
            return None

        active_count = len(pool.active_tasks)
        return {
            "pool": pool.to_dict(),
            "utilization": active_count / pool.max_concurrent,
            "available_slots": pool.max_concurrent - active_count,
        }

    def aggregate_results(
        self,
        task_ids: List[str],
        aggregation_type: str = "merge",
    ) -> Dict[str, Any]:
        """Aggregate results from multiple tasks."""
        results = []
        for tid in task_ids:
            task = self.tasks.get(tid)
            if task and task.result:
                results.append(task.result)

        if aggregation_type == "merge":
            merged = {}
            for r in results:
                merged.update(r)
            return {"type": "merged", "data": merged, "sources": len(results)}

        elif aggregation_type == "concat":
            return {"type": "concatenated", "data": results, "count": len(results)}

        elif aggregation_type == "vote":
            # Simple majority voting on categorical results
            votes = {}
            for r in results:
                for key, value in r.items():
                    if key not in votes:
                        votes[key] = {}
                    votes[key][str(value)] = votes[key].get(str(value), 0) + 1

            winners = {}
            for key, counts in votes.items():
                winners[key] = max(counts.items(), key=lambda x: x[1])[0]

            return {"type": "voted", "data": winners, "participants": len(results)}

        return {"type": "raw", "data": results}

    def _save_tasks(self):
        """Save tasks to disk."""
        tasks_file = self.data_dir / "tasks.json"
        data = {
            "tasks": [t.to_dict() for t in self.tasks.values()],
            "saved_at": datetime.now(UTC).isoformat(),
        }
        tasks_file.write_text(json.dumps(data, indent=2))

    def list_pools(self) -> List[dict[str, Any]]:
        """List all agent pools."""
        return [p.to_dict() for p in self.pools.values()]

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[dict[str, Any]]:
        """List tasks, optionally filtered by status."""
        tasks = self.tasks.values()
        if status:
            tasks = [t for t in tasks if t.status == status]
        return [t.to_dict() for t in tasks]

    def get_status(self) -> Dict[str, Any]:
        """Get coordinator status."""
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        active = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)

        return {
            "total_pools": len(self.pools),
            "total_tasks": len(self.tasks),
            "pending": pending,
            "active": active,
            "completed": completed,
            "pool_utilization": {pid: self.get_pool_status(pid) for pid in self.pools.keys()},
        }


_COORDINATOR: Optional[AgentCoordinator] = None


def get_agent_coordinator(data_dir: Optional[Path] = None) -> AgentCoordinator:
    """Get or create global agent coordinator."""
    global _COORDINATOR
    if _COORDINATOR is None:
        _COORDINATOR = AgentCoordinator(data_dir)
    return _COORDINATOR
