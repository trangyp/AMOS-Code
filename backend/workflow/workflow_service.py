"""
AMOS Workflow Orchestration & Saga Pattern Implementation v2.0.0

Durable execution with:
- Saga pattern for distributed transactions
- Compensation management
- State machine workflows
- Event sourcing for audit trails
- Retry and timeout handling
- Parallel execution support

Owner: Trang Phan
Version: 2.0.0
"""


import asyncio
import hashlib
import json
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Coroutine, Optional

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
from typing import Callable, Optional
from typing import Dict, List, Tuple
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ActivityStatus(Enum):
    """Activity execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


@dataclass
class WorkflowActivity:
    """Single workflow activity/step."""
    activity_id: str
    name: str
    handler: Callable[..., Coroutine[Any, Any, Any]]
    compensation: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Any = None
    status: ActivityStatus = ActivityStatus.PENDING
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: float = 30.0


@dataclass
class WorkflowInstance:
    """Workflow execution instance."""
    workflow_id: str
    workflow_type: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    activities: List[WorkflowActivity] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    parent_workflow_id: Optional[str] = None
    saga_compensations: list[dict[str, Any]] = field(default_factory=list)


class SagaOrchestrator:
    """
    Saga pattern orchestrator for distributed transactions.
    Ensures all-or-nothing execution with compensation on failure.
    """

    def __init__(self):
        self._active_sagas: Dict[str, WorkflowInstance] = {}
        self._compensation_log: list[dict[str, Any]] = []

    async def execute_saga(
        self,
        workflow_id: str,
        activities: List[WorkflowActivity],
        context: Dict[str, Any]
    ) -> WorkflowInstance:
        """Execute saga workflow with compensation support."""
        saga = WorkflowInstance(
            workflow_id=workflow_id,
            workflow_type="saga",
            activities=activities,
            context=context,
            status=WorkflowStatus.RUNNING,
            started_at=time.time()
        )
        self._active_sagas[workflow_id] = saga

        completed_activities: List[WorkflowActivity] = []

        try:
            for activity in activities:
                activity.status = ActivityStatus.RUNNING
                activity.started_at = time.time()

                result = await self._execute_with_retry(activity, context)

                if result is None:
                    activity.status = ActivityStatus.FAILED
                    saga.status = WorkflowStatus.COMPENSATING
                    await self._compensate_saga(completed_activities, saga)
                    saga.status = WorkflowStatus.COMPENSATED
                    saga.error_message = f"Activity {activity.name} failed"
                    saga.completed_at = time.time()
                    return saga

                activity.output_data = result
                activity.status = ActivityStatus.COMPLETED
                activity.completed_at = time.time()
                completed_activities.append(activity)
                saga.results[activity.name] = result

                saga.saga_compensations.append({
                    "activity_id": activity.activity_id,
                    "name": activity.name,
                    "compensation": activity.compensation,
                    "input": activity.input_data,
                    "output": result
                })

            saga.status = WorkflowStatus.COMPLETED
            saga.completed_at = time.time()

        except Exception as e:
            saga.status = WorkflowStatus.FAILED
            saga.error_message = str(e)
            saga.completed_at = time.time()

        return saga

    async def _execute_with_retry(
        self,
        activity: WorkflowActivity,
        context: Dict[str, Any]
    ) -> Any:
        """Execute activity with exponential backoff retry."""
        for attempt in range(activity.max_retries + 1):
            try:
                if activity.started_at and (time.time() - activity.started_at) > activity.timeout_seconds:
                    raise TimeoutError(f"Activity {activity.name} timed out")

                result = await asyncio.wait_for(
                    activity.handler(**activity.input_data, context=context),
                    timeout=activity.timeout_seconds
                )
                return result

            except Exception as e:
                activity.retry_count += 1
                if attempt < activity.max_retries:
                    wait_time = 0.5 * (2 ** attempt)
                    await asyncio.sleep(wait_time)
                else:
                    activity.error = str(e)
                    return None

        return None

    async def _compensate_saga(
        self,
        completed_activities: List[WorkflowActivity],
        saga: WorkflowInstance
    ) -> None:
        """Run compensating transactions in reverse order."""
        for activity in reversed(completed_activities):
            if activity.compensation:
                try:
                    await activity.compensation(
                        activity.output_data,
                        context=saga.context
                    )
                    activity.status = ActivityStatus.COMPENSATED

                    self._compensation_log.append({
                        "workflow_id": saga.workflow_id,
                        "activity_id": activity.activity_id,
                        "compensated_at": time.time(),
                        "status": "success"
                    })
                except Exception as e:
                    self._compensation_log.append({
                        "workflow_id": saga.workflow_id,
                        "activity_id": activity.activity_id,
                        "compensated_at": time.time(),
                        "status": "failed",
                        "error": str(e)
                    })


class CompensationManager:
    """Manages compensation logic and audit trail."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or "redis://localhost:6379/9"
        self._redis: Optional[Any] = None

        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
            except Exception:
                pass

    async def record_compensation(
        self,
        workflow_id: str,
        activity_id: str,
        compensation_data: Dict[str, Any]
    ) -> bool:
        """Record compensation action for audit."""
        if not self._redis:
            return False

        try:
            key = f"compensation:{workflow_id}:{activity_id}"
            await self._redis.setex(
                key,
                86400 * 30,
                json.dumps({
                    "workflow_id": workflow_id,
                    "activity_id": activity_id,
                    "data": compensation_data,
                    "recorded_at": time.time()
                })
            )
            return True
        except Exception:
            return False

    async def get_compensation_log(
        self,
        workflow_id: str
    ) -> list[dict[str, Any]]:
        """Retrieve compensation history for workflow."""
        if not self._redis:
            return []

        try:
            pattern = f"compensation:{workflow_id}:*"
            keys = await self._redis.keys(pattern)
            logs = []
            for key in keys:
                data = await self._redis.get(key)
                if data:
                    logs.append(json.loads(data))
            return sorted(logs, key=lambda x: x.get("recorded_at", 0))
        except Exception:
            return []


class WorkflowService:
    """
    Main workflow orchestration service.
    Supports: Sequential, Parallel, Saga, and Child workflows.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or "redis://localhost:6379/9"
        self._redis: Optional[Any] = None
        self._saga_orchestrator = SagaOrchestrator()
        self._compensation_manager = CompensationManager(redis_url)
        self._workflows: Dict[str, WorkflowInstance] = {}
        self._workflow_definitions: dict[str, list[WorkflowActivity]] = {}

        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
            except Exception:
                pass

    def define_workflow(
        self,
        workflow_type: str,
        activities: List[WorkflowActivity]
    ) -> None:
        """Define a reusable workflow template."""
        self._workflow_definitions[workflow_type] = activities

    async def start_workflow(
        self,
        workflow_type: str,
        input_data: Dict[str, Any],
        parent_workflow_id: Optional[str] = None,
        use_saga: bool = False
    ) -> str:
        """Start new workflow execution."""
        workflow_id = f"wf_{uuid.uuid4().hex[:16]}"

        if SUPERBRAIN_AVAILABLE:
            try:
                brain = get_super_brain()
                if brain and hasattr(brain, 'action_gate'):
                    result = brain.action_gate.validate_action(
                        agent_id="workflow_service",
                        action="start_workflow",
                        details={
                            "workflow_type": workflow_type,
                            "workflow_id": workflow_id,
                            "use_saga": use_saga
                        }
                    )
                    if not result.authorized:
                        raise PermissionError(f"Workflow start blocked: {result.reason}")
            except Exception:
                pass

        activities = self._workflow_definitions.get(workflow_type, [])
        if not activities:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        instance = WorkflowInstance(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            status=WorkflowStatus.PENDING,
            context=input_data,
            parent_workflow_id=parent_workflow_id,
            activities=[
                WorkflowActivity(
                    activity_id=f"{workflow_id}_act_{i}",
                    name=act.name,
                    handler=act.handler,
                    compensation=act.compensation,
                    input_data={**act.input_data, **input_data},
                    max_retries=act.max_retries,
                    timeout_seconds=act.timeout_seconds
                )
                for i, act in enumerate(activities)
            ]
        )

        self._workflows[workflow_id] = instance

        if self._redis:
            try:
                await self._redis.setex(
                    f"workflow:{workflow_id}",
                    86400 * 7,
                    json.dumps({
                        "workflow_id": workflow_id,
                        "type": workflow_type,
                        "status": instance.status.value,
                        "created_at": instance.created_at,
                        "parent_id": parent_workflow_id
                    })
                )
            except Exception:
                pass

        if STREAMING_AVAILABLE:
            try:
                publish_event(
                    event_type="workflow_started",
                    source_system="workflow_service",
                    payload={
                        "workflow_id": workflow_id,
                        "type": workflow_type,
                        "use_saga": use_saga
                    },
                    requires_governance=True
                )
            except Exception:
                pass

        if use_saga:
            asyncio.create_task(
                self._saga_orchestrator.execute_saga(
                    workflow_id, instance.activities, instance.context
                )
            )
        else:
            asyncio.create_task(self._execute_sequential(instance))

        return workflow_id

    async def _execute_sequential(self, instance: WorkflowInstance) -> None:
        """Execute workflow activities sequentially."""
        instance.status = WorkflowStatus.RUNNING
        instance.started_at = time.time()

        for activity in instance.activities:
            activity.status = ActivityStatus.RUNNING
            activity.started_at = time.time()

            try:
                result = await asyncio.wait_for(
                    activity.handler(**activity.input_data, context=instance.context),
                    timeout=activity.timeout_seconds
                )
                activity.output_data = result
                activity.status = ActivityStatus.COMPLETED
                activity.completed_at = time.time()
                instance.results[activity.name] = result

            except Exception as e:
                activity.status = ActivityStatus.FAILED
                activity.error = str(e)
                instance.status = WorkflowStatus.FAILED
                instance.error_message = str(e)
                instance.completed_at = time.time()
                return

        instance.status = WorkflowStatus.COMPLETED
        instance.completed_at = time.time()

        if self._redis:
            try:
                await self._redis.setex(
                    f"workflow:{instance.workflow_id}",
                    86400 * 7,
                    json.dumps({
                        "workflow_id": instance.workflow_id,
                        "type": instance.workflow_type,
                        "status": instance.status.value,
                        "completed_at": instance.completed_at,
                        "results": instance.results
                    })
                )
            except Exception:
                pass

    async def execute_parallel(
        self,
        workflow_id: str,
        activities: List[WorkflowActivity],
        max_concurrent: int = 5
    ) -> Dict[str, Any]:
        """Execute activities in parallel with concurrency limit."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_with_limit(activity: WorkflowActivity) -> Tuple[str, Any]:
            async with semaphore:
                activity.status = ActivityStatus.RUNNING
                activity.started_at = time.time()
                try:
                    result = await asyncio.wait_for(
                        activity.handler(**activity.input_data),
                        timeout=activity.timeout_seconds
                    )
                    activity.status = ActivityStatus.COMPLETED
                    activity.completed_at = time.time()
                    return activity.name, result
                except Exception as e:
                    activity.status = ActivityStatus.FAILED
                    activity.error = str(e)
                    return activity.name, None

        results = await asyncio.gather(*[run_with_limit(act) for act in activities])
        return {name: result for name, result in results}

    async def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowInstance]:
        """Get current workflow status."""
        if workflow_id in self._workflows:
            return self._workflows[workflow_id]

        if self._redis:
            try:
                data = await self._redis.get(f"workflow:{workflow_id}")
                if data:
                    info = json.loads(data)
                    return WorkflowInstance(
                        workflow_id=info["workflow_id"],
                        workflow_type=info["type"],
                        status=WorkflowStatus(info["status"]),
                        results=info.get("results", {})
                    )
            except Exception:
                pass

        return None

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel running workflow."""
        instance = self._workflows.get(workflow_id)
        if not instance:
            return False

        if instance.status not in [WorkflowStatus.RUNNING, WorkflowStatus.PENDING]:
            return False

        instance.status = WorkflowStatus.CANCELLED
        instance.completed_at = time.time()

        completed = [a for a in instance.activities if a.status == ActivityStatus.COMPLETED]
        if completed and instance.workflow_type == "saga":
            await self._saga_orchestrator._compensate_saga(completed, instance)

        return True

    def get_active_workflows(self) -> List[WorkflowInstance]:
        """Get all currently running workflows."""
        return [
            wf for wf in self._workflows.values()
            if wf.status == WorkflowStatus.RUNNING
        ]

    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics."""
        all_workflows = list(self._workflows.values())
        return {
            "total": len(all_workflows),
            "running": sum(1 for w in all_workflows if w.status == WorkflowStatus.RUNNING),
            "completed": sum(1 for w in all_workflows if w.status == WorkflowStatus.COMPLETED),
            "failed": sum(1 for w in all_workflows if w.status == WorkflowStatus.FAILED),
            "compensated": sum(1 for w in all_workflows if w.status == WorkflowStatus.COMPENSATED),
            "avg_duration": (
                sum(
                    (w.completed_at or time.time()) - (w.started_at or w.created_at)
                    for w in all_workflows if w.started_at
                ) / len([w for w in all_workflows if w.started_at])
                if any(w.started_at for w in all_workflows) else 0
            )
        }


workflow_service = WorkflowService()


async def start_workflow(
    workflow_type: str,
    input_data: Dict[str, Any],
    use_saga: bool = False
) -> str:
    """Start workflow execution."""
    return await workflow_service.start_workflow(workflow_type, input_data, use_saga=use_saga)


async def execute_activity(
    name: str,
    handler: Callable[..., Coroutine[Any, Any, Any]],
    input_data: Dict[str, Any],
    timeout: float = 30.0,
    retries: int = 3
) -> Any:
    """Execute single activity."""
    activity = WorkflowActivity(
        activity_id=f"act_{uuid.uuid4().hex[:8]}",
        name=name,
        handler=handler,
        input_data=input_data,
        max_retries=retries,
        timeout_seconds=timeout
    )

    activity.status = ActivityStatus.RUNNING
    activity.started_at = time.time()

    for attempt in range(retries + 1):
        try:
            result = await asyncio.wait_for(
                handler(**input_data),
                timeout=timeout
            )
            activity.output_data = result
            activity.status = ActivityStatus.COMPLETED
            return result
        except Exception as e:
            if attempt == retries:
                activity.status = ActivityStatus.FAILED
                activity.error = str(e)
                raise
            await asyncio.sleep(0.5 * (2 ** attempt))

    return None


async def compensate_activity(
    activity_data: Any,
    compensation_handler: Callable[..., Coroutine[Any, Any, Any]]
) -> bool:
    """Execute compensation for an activity."""
    try:
        await compensation_handler(activity_data)
        return True
    except Exception:
        return False
