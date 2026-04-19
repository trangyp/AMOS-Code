#!/usr/bin/env python3
"""AMOS Async Task Queue v1.0.0
===========================

Distributed task processing with Celery and Redis.

Features:
  - Asynchronous agent spawning
  - Background orchestration execution
  - Vector memory indexing tasks
  - Real-time progress updates via WebSocket
  - Task prioritization (high, normal, low)
  - Automatic retries with exponential backoff
  - Dead letter queue for failed tasks
  - Task result persistence
  - Flower dashboard integration

Architecture:
  ┌─────────────────┐     ┌─────────────┐     ┌─────────────────┐
  │   AMOS API      │────▶│Redis Broker │────▶│  Celery Worker  │
  │   (FastAPI)     │     │  (Queue)     │     │  (Task Executor)│
  └─────────────────┘     └─────────────┘     └─────────────────┘
         │                                               │
         │ WebSocket/SSE                                  │
         ▼                                               ▼
  ┌─────────────────┐                           ┌─────────────────┐
  │   Client        │◀──────────────────────────│  Task Results   │
  │   (Progress)    │      (Result Backend)     │   (Redis)      │
  └─────────────────┘                           └─────────────────┘

Usage:
  # Start Redis
  redis-server

  # Start Celery worker
  celery -A amos_async_tasks worker --loglevel=info

  # Start Flower dashboard
  celery -A amos_async_tasks flower --port=5555

  # Submit task from FastAPI
    from amos_async_tasks import spawn_agent_task
  task = spawn_agent_task.delay(role="architect", paradigm="HYBRID")
  return {"task_id": task.id, "status": "queued"}

Requirements:
  pip install celery[redis] redis flower

Author: Trang Phan
Version: 1.0.0
"""


import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Try to import Celery
try:
    from celery import Celery, Task
    from celery.exceptions import MaxRetriesExceededError
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    print("[AsyncTasks] Celery not available, using mock implementation")

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Import AMOS configuration
try:
    from amos_config import settings
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("[AsyncTasks] Config not available, using defaults")


# Celery configuration
if CELERY_AVAILABLE:
    # Get Redis URL from config or use default
    redis_url = "redis://localhost:6379"
    if CONFIG_AVAILABLE:
        # Use a different Redis DB for tasks
        redis_url = "redis://localhost:6379/0"

    celery_app = Celery(
        "amos_tasks",
        broker=redis_url,
        backend=redis_url,
        include=["amos_async_tasks"]
    )

    # Celery configuration
    celery_app.conf.update(
        # Task serialization
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",

        # Timezone
        timezone="timezone.utc",
        enable_utc=True,

        # Task settings
        task_track_started=True,
        task_time_limit=300,  # 5 minutes max
        task_soft_time_limit=240,  # 4 minutes soft limit

        # Result settings
        result_expires=3600,  # Results expire after 1 hour
        result_extended=True,  # Include more result info

        # Worker settings
        worker_prefetch_multiplier=1,  # One task at a time
        worker_max_tasks_per_child=1000,  # Restart after 1000 tasks

        # Retry settings
        task_default_retry_delay=60,  # 1 minute between retries
        task_max_retries=3,  # Max 3 retries

        # Queue settings
        task_default_queue="amos_default",
        task_routes={
            "amos_async_tasks.spawn_agent_task": {"queue": "amos_agents"},
            "amos_async_tasks.orchestrate_task": {"queue": "amos_orchestration"},
            "amos_async_tasks.vector_index_task": {"queue": "amos_indexing"},
            "amos_async_tasks.self_evolution_task": {"queue": "amos_evolution"},
        },

        # Dead letter queue
        task_reject_on_worker_lost=True,
    )
else:
    # Mock Celery for development without Redis
    celery_app = None


class MockTask:
    """Mock task for when Celery is not available."""

    def __init__(self, task_id: str, func, args, kwargs):
        self.id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._status = "PENDING"
        self._result = None
        self._state = {}

    def delay(self, *args, **kwargs):
        """Execute synchronously for mock mode."""
        self._status = "STARTED"
        try:
            result = self.func(*self.args, **self.kwargs)
            self._result = result
            self._status = "SUCCESS"
        except Exception as e:
            self._result = str(e)
            self._status = "FAILURE"
        return self

    def get(self, timeout: int  = None) -> Any:
        """Get task result."""
        return self._result

    @property
    def status(self) -> str:
        """Get task status."""
        return self._status

    @property
    def state(self) -> str:
        """Get task state."""
        return self._status


class MockAsyncResult:
    """Mock AsyncResult for when Celery is not available."""

    def __init__(self, task_id: str):
        self.id = task_id
        self._status = "PENDING"
        self._result = None

    def get(self, timeout: int  = None) -> Any:
        return self._result

    @property
    def status(self) -> str:
        return self._status

    @property
    def state(self) -> str:
        return self._status

    @property
    def ready(self) -> bool:
        return self._status in ["SUCCESS", "FAILURE"]

    @property
    def successful(self) -> bool:
        return self._status == "SUCCESS"


# Task definitions
if CELERY_AVAILABLE:
    @celery_app.task(
        bind=True,
        max_retries=3,
        default_retry_delay=60,
        queue="amos_agents"
    )
    def spawn_agent_task(self, role: str, paradigm: str = "HYBRID", name: str  = None):
        """
        Async task to spawn an agent.

        Args:
            role: Agent role (architect, reviewer, auditor, executor)
            paradigm: Cognitive paradigm (SYMBOLIC, NEURAL, HYBRID)
            name: Optional custom name

        Returns:
            Agent info dict
        """
        try:
            from amos_unified_system import AMOSUnifiedSystem

            # Initialize AMOS
            amos = AMOSUnifiedSystem()
            if not amos.initialize():
                raise RuntimeError("AMOS initialization failed")

            # Update task state
            self.update_state(
                state="PROGRESS",
                meta={"step": "spawning", "role": role, "paradigm": paradigm}
            )

            # Spawn agent
            agent = amos.spawn_agent(role=role, paradigm=paradigm, name=name)

            return {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "role": agent.role,
                "paradigm": agent.paradigm.name,
                "capabilities": {
                    "strengths": agent.capabilities.strengths,
                    "constraints": agent.capabilities.constraints,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as exc:
            # Retry on failure
            try:
                self.retry(countdown=60 * (self.request.retries + 1))
            except MaxRetriesExceededError:
                return {
                    "error": str(exc),
                    "status": "failed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

    @celery_app.task(
        bind=True,
        max_retries=2,
        default_retry_delay=30,
        queue="amos_orchestration",
        time_limit=300,  # 5 minutes for orchestration
    )
    def orchestrate_task(
        self,
        task_description: str,
        agents: List[str]  = None,
        require_consensus: bool = True,
        session_id: str  = None
    ):
        """
        Async task for multi-agent orchestration.

        Args:
            task_description: The task to execute
            agents: List of agent roles to use
            require_consensus: Whether to require consensus
            session_id: Session ID for memory

        Returns:
            Orchestration result dict
        """
        try:
            from amos_unified_system import AMOSUnifiedSystem

            # Initialize AMOS
            amos = AMOSUnifiedSystem()
            if not amos.initialize():
                raise RuntimeError("AMOS initialization failed")

            # Progress updates
            self.update_state(
                state="PROGRESS",
                meta={"step": "initialization", "progress": 10}
            )

            # Validate task
            validation = amos.validate_action(task_description)
            if not validation["compliant"]:
                return {
                    "success": False,
                    "error": "Task violates Global Laws",
                    "violations": validation["violations"],
                }

            self.update_state(
                state="PROGRESS",
                meta={"step": "executing", "progress": 30}
            )

            # Execute orchestration
            result = amos.execute(
                task=task_description,
                agents=agents,
                require_consensus=require_consensus
            )

            self.update_state(
                state="PROGRESS",
                meta={"step": "finalizing", "progress": 90}
            )

            # Record to memory if session provided
            if session_id and amos.memory:
                amos.memory.record_episode(
                    task=task_description,
                    outcome=result.get("final_decision", ""),
                    agents_used=result.get("agents_used", []),
                    law_compliance=result.get("law_compliant", False),
                    lessons_learned=[]
                )

            return {
                "success": True,
                "result": result,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as exc:
            try:
                self.retry(countdown=30 * (self.request.retries + 1))
            except MaxRetriesExceededError:
                return {
                    "success": False,
                    "error": str(exc),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

    @celery_app.task(
        bind=True,
        max_retries=3,
        default_retry_delay=120,
        queue="amos_indexing"
    )
    def vector_index_task(self, memories: List[dict]):
        """
        Async task to index memories in vector database.

        Args:
            memories: List of memory entries to index

        Returns:
            Indexing result
        """
        try:
            from amos_vector_memory import AMOSVectorMemory

            vm = AMOSVectorMemory()
            if not vm.initialize():
                raise RuntimeError("Vector memory initialization failed")

            indexed = 0
            for i, memory in enumerate(memories):
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "step": "indexing",
                        "current": i + 1,
                        "total": len(memories),
                        "progress": int((i + 1) / len(memories) * 100)
                    }
                )

                success = vm.add_memory(
                    content=memory.get("content", ""),
                    category=memory.get("category", "general"),
                    metadata=memory.get("metadata", {})
                )
                if success:
                    indexed += 1

            return {
                "success": True,
                "indexed": indexed,
                "total": len(memories),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as exc:
            try:
                self.retry(countdown=120 * (self.request.retries + 1))
            except MaxRetriesExceededError:
                return {
                    "success": False,
                    "error": str(exc),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

    @celery_app.task(
        bind=True,
        max_retries=1,
        default_retry_delay=300,
        queue="amos_evolution"
    )
    def self_evolution_task(self, target_file: str, evolution_plan: dict):
        """
        Async task for self-evolution (requires approval).

        Args:
            target_file: File to evolve
            evolution_plan: Evolution plan dict

        Returns:
            Evolution result awaiting approval
        """
        try:
            from amos_self_evolution import AMOSSelfEvolution
from typing import List, Optional

            evo = AMOSSelfEvolution()
            if not evo.initialize():
                raise RuntimeError("Self-evolution initialization failed")

            self.update_state(
                state="PROGRESS",
                meta={"step": "generating", "target": target_file}
            )

            # Generate evolution proposal
            proposal = evo.generate_proposal(target_file, evolution_plan)

            # Don't auto-apply - requires human approval
            return {
                "success": True,
                "status": "awaiting_approval",
                "proposal": proposal,
                "target_file": target_file,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "approval_url": f"/api/v1/evolution/approve/{proposal['id']}"
            }

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

else:
    # Mock implementations
    def spawn_agent_task(role: str, paradigm: str = "HYBRID", name: str  = None):
        return MockTask("mock-spawn", lambda r, p, n: {"agent_id": "mock"}, (role, paradigm, name), {})

    def orchestrate_task(task_description: str, agents: List[str]  = None,
                        require_consensus: bool = True, session_id: str  = None):
        return MockTask("mock-orchestrate", lambda **kw: {"success": True}, (), {})

    def vector_index_task(memories: List[dict]):
        return MockTask("mock-index", lambda m: {"indexed": len(m)}, (memories,), {})

    def self_evolution_task(target_file: str, evolution_plan: dict):
        return MockTask("mock-evolve", lambda **kw: {"status": "awaiting_approval"}, (), {})


class AMOSAsyncTaskManager:
    """Manager for AMOS async tasks."""

    def __init__(self):
        self.celery_available = CELERY_AVAILABLE
        self.redis_available = REDIS_AVAILABLE

    def initialize(self) -> bool:
        """Initialize async task manager."""
        print("[AsyncTasks] Initializing...")

        if not self.celery_available:
            print("  ⚠️  Celery not available (mock mode)")
            return True

        if not self.redis_available:
            print("  ⚠️  Redis not available (mock mode)")
            return True

        # Test Redis connection
        try:
            r = redis.Redis(host="localhost", port=6379, db=0)
            r.ping()
            print("  ✓ Redis connection successful")
        except Exception as e:
            print(f"  ⚠️  Redis connection failed: {e}")
            return False

        print("  ✓ Async task manager ready")
        return True

    def submit_spawn_agent(self, role: str, paradigm: str = "HYBRID",
                          name: str  = None) -> str:
        """Submit agent spawn task."""
        if CELERY_AVAILABLE:
            task = spawn_agent_task.delay(role, paradigm, name)
            return task.id
        else:
            return "mock-task-id"

    def submit_orchestrate(self, task: str, agents: List[str]  = None,
                           require_consensus: bool = True,
                           session_id: str  = None) -> str:
        """Submit orchestration task."""
        if CELERY_AVAILABLE:
            task = orchestrate_task.delay(task, agents, require_consensus, session_id)
            return task.id
        else:
            return "mock-task-id"

    def submit_vector_index(self, memories: List[dict]) -> str:
        """Submit vector indexing task."""
        if CELERY_AVAILABLE:
            task = vector_index_task.delay(memories)
            return task.id
        else:
            return "mock-task-id"

    def submit_self_evolution(self, target_file: str, evolution_plan: dict) -> str:
        """Submit self-evolution task."""
        if CELERY_AVAILABLE:
            task = self_evolution_task.delay(target_file, evolution_plan)
            return task.id
        else:
            return "mock-task-id"

    def get_task_status(self, task_id: str) -> dict:
        """Get task status by ID."""
        if CELERY_AVAILABLE:
            result = AsyncResult(task_id, app=celery_app)
            return {
                "task_id": task_id,
                "status": result.status,
                "state": result.state,
                "ready": result.ready(),
                "successful": result.successful() if result.ready() else None,
                "result": result.result if result.ready() else None,
            }
        else:
            return {
                "task_id": task_id,
                "status": "MOCK",
                "state": "SUCCESS",
                "ready": True,
                "successful": True,
                "result": {"mock": True},
            }

    def revoke_task(self, task_id: str, terminate: bool = False) -> bool:
        """Revoke/cancel a task."""
        if CELERY_AVAILABLE:
            celery_app.control.revoke(task_id, terminate=terminate)
            return True
        return False

    def get_queue_stats(self) -> dict:
        """Get queue statistics."""
        if CELERY_AVAILABLE:
            inspector = celery_app.control.inspect()
            stats = inspector.stats()
            active = inspector.active()
            scheduled = inspector.scheduled()

            return {
                "workers": list(stats.keys()) if stats else [],
                "active_tasks": active,
                "scheduled_tasks": scheduled,
            }
        return {"workers": [], "active_tasks": {}, "scheduled_tasks": {}}


def main():
    """Demo async task manager."""
    print("=" * 70)
    print("AMOS ASYNC TASK QUEUE v1.0.0")
    print("=" * 70)

    manager = AMOSAsyncTaskManager()
    if not manager.initialize():
        print("\nAsync task manager initialization failed!")
        sys.exit(1)

    print("\n[Submitting Tasks]")

    # Submit spawn agent task
    task1_id = manager.submit_spawn_agent("architect", "HYBRID")
    print(f"  ✓ Spawn agent task: {task1_id}")

    # Submit orchestration task
    task2_id = manager.submit_orchestrate(
        task="Design a REST API",
        agents=["architect", "reviewer"],
        require_consensus=True
    )
    print(f"  ✓ Orchestration task: {task2_id}")

    # Check status
    print("\n[Task Status]")
    status1 = manager.get_task_status(task1_id)
    print(f"  Task 1: {status1['status']}")
    status2 = manager.get_task_status(task2_id)
    print(f"  Task 2: {status2['status']}")

    # Queue stats
    print("\n[Queue Statistics]")
    stats = manager.get_queue_stats()
    print(f"  Workers: {len(stats['workers'])}")
    print(f"  Active tasks: {stats['active_tasks']}")

    print("\n" + "=" * 70)
    print("Async task manager ready!")
    print("=" * 70)
    print("\nTo start worker:")
    print("  celery -A amos_async_tasks worker --loglevel=info")
    print("\nTo start Flower dashboard:")
    print("  celery -A amos_async_tasks flower --port=5555")


if __name__ == "__main__":
    main()
