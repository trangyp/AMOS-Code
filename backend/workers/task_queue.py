"""
AMOS SuperBrain Task Queue & Background Workers v2.0.0

Distributed task queue with background workers for all 12 systems.
Supports scheduled tasks, job retries, and SuperBrain governance.

Architecture:
- Redis-backed job queue
- Worker pool for distributed processing
- Job retry with exponential backoff
- Scheduled tasks (cron-like)
- SuperBrain governance on job execution

Owner: Trang Phan
Version: 2.0.0
"""

from __future__ import annotations


import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

# Redis for queue
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Threading for workers
try:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    CONCURRENT_AVAILABLE = True
except ImportError:
    CONCURRENT_AVAILABLE = False

# SuperBrain integration
try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

# Import existing modules
try:
    from backend.data_pipeline.streaming import publish_event

    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False


class JobStatus(Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class JobPriority(Enum):
    """Job priority levels."""

    LOW = 1
    MEDIUM = 5
    HIGH = 10
    CRITICAL = 20


@dataclass
class Job:
    """Task job definition with governance metadata."""

    job_id: str
    task_name: str
    system: str
    payload: dict[str, Any]
    priority: JobPriority = JobPriority.MEDIUM
    status: JobStatus = JobStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    scheduled_for: str = None
    started_at: str = None
    completed_at: str = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    requires_governance: bool = True
    correlation_id: str = None
    result: Any = None
    error: str = None


@dataclass
class WorkerStats:
    """Worker pool statistics."""

    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    retried_jobs: int = 0
    active_workers: int = 0
    queue_depth: int = 0
    avg_processing_time: float = 0.0
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class TaskQueue:
    """Central task queue with SuperBrain governance."""

    # Task registry for 12 systems
    TASK_REGISTRY: dict[str, dict[str, Any]] = {
        # Cognitive Router tasks
        "cognitive_router.analyze_task": {
            "system": "cognitive_router",
            "timeout": 300,
            "governance_required": True,
        },
        "cognitive_router.batch_process": {
            "system": "cognitive_router",
            "timeout": 600,
            "governance_required": True,
        },
        # Resilience Engine tasks
        "resilience_engine.health_check": {
            "system": "resilience_engine",
            "timeout": 60,
            "governance_required": False,
        },
        "resilience_engine.circuit_reset": {
            "system": "resilience_engine",
            "timeout": 30,
            "governance_required": True,
        },
        # Knowledge Loader tasks
        "knowledge_loader.sync_files": {
            "system": "knowledge_loader",
            "timeout": 300,
            "governance_required": True,
        },
        "knowledge_loader.index_update": {
            "system": "knowledge_loader",
            "timeout": 600,
            "governance_required": True,
        },
        # Master Orchestrator tasks
        "master_orchestrator.process_workflow": {
            "system": "master_orchestrator",
            "timeout": 300,
            "governance_required": True,
        },
        "master_orchestrator.batch_tasks": {
            "system": "master_orchestrator",
            "timeout": 900,
            "governance_required": True,
        },
        # Agent tasks
        "agent_messaging.broadcast": {
            "system": "agent_messaging",
            "timeout": 120,
            "governance_required": True,
        },
        "agent_observability.collect_metrics": {
            "system": "agent_observability",
            "timeout": 60,
            "governance_required": False,
        },
        # UBI Engine tasks
        "ubi_engine.batch_analysis": {
            "system": "ubi_engine",
            "timeout": 300,
            "governance_required": True,
        },
        # Tool tasks
        "amos_tools.execute_batch": {
            "system": "amos_tools",
            "timeout": 600,
            "governance_required": True,
        },
        # Audit tasks
        "audit_exporter.generate_report": {
            "system": "audit_exporter",
            "timeout": 300,
            "governance_required": True,
        },
        "audit_exporter.cleanup_old_logs": {
            "system": "audit_exporter",
            "timeout": 1800,
            "governance_required": False,
        },
        # SuperBrain tasks
        "superbrain.governance_audit": {
            "system": "superbrain",
            "timeout": 300,
            "governance_required": True,
        },
    }

    # Scheduled tasks (cron-like)
    SCHEDULED_TASKS: list[dict[str, Any]] = [
        {
            "task": "resilience_engine.health_check",
            "schedule": "*/5 * * * *",  # Every 5 minutes
            "priority": JobPriority.HIGH,
        },
        {
            "task": "agent_observability.collect_metrics",
            "schedule": "*/1 * * * *",  # Every minute
            "priority": JobPriority.MEDIUM,
        },
        {
            "task": "knowledge_loader.sync_files",
            "schedule": "0 */6 * * *",  # Every 6 hours
            "priority": JobPriority.LOW,
        },
        {
            "task": "audit_exporter.cleanup_old_logs",
            "schedule": "0 0 * * *",  # Daily at midnight
            "priority": JobPriority.LOW,
        },
    ]

    def __init__(self, redis_url: str = None, max_workers: int = 4):
        self.redis_url = redis_url or "redis://localhost:6379/3"
        self.max_workers = max_workers
        self._redis: redis.Redis = None
        self._brain = None
        self._executor: ThreadPoolExecutor | None = None
        self._stats = WorkerStats()
        self._handlers: dict[str, Callable] = {}
        self._running = False

        # Initialize connections
        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
                self._redis.ping()
            except Exception:
                self._redis = None

        if SUPERBRAIN_AVAILABLE:
            try:
                self._brain = get_super_brain()
            except Exception:
                pass

        if CONCURRENT_AVAILABLE:
            self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def _get_queue_key(self, priority: JobPriority) -> str:
        """Get Redis queue key for priority level."""
        return f"queue:priority:{priority.value}"

    def _get_job_key(self, job_id: str) -> str:
        """Get Redis job storage key."""
        return f"job:{job_id}"

    def submit_job(
        self,
        task_name: str,
        payload: dict[str, Any],
        system: str = None,
        priority: JobPriority = JobPriority.MEDIUM,
        scheduled_for: datetime = None,
        max_retries: int = 3,
        correlation_id: str = None,
        requires_governance: bool = None,
    ) -> str:
        """Submit job to queue with governance check."""
        # Validate task
        task_config = self.TASK_REGISTRY.get(task_name)
        if not task_config:
            return None

        # Use system from config if not provided
        system = system or task_config["system"]

        # Use governance from config if not provided
        if requires_governance is None:
            requires_governance = task_config.get("governance_required", True)

        # Generate job ID
        job_id = hashlib.sha256(
            f"{task_name}:{system}:{datetime.now(UTC).isoformat()}".encode()
        ).hexdigest()[:16]

        # Create job
        job = Job(
            job_id=job_id,
            task_name=task_name,
            system=system,
            payload=payload,
            priority=priority,
            scheduled_for=scheduled_for.isoformat() if scheduled_for else None,
            max_retries=max_retries,
            requires_governance=requires_governance,
            correlation_id=correlation_id,
        )

        # Store in Redis
        if self._redis:
            try:
                # Store job data
                self._redis.setex(
                    self._get_job_key(job_id),
                    86400,  # 24 hour TTL
                    json.dumps(job.__dict__, default=str),
                )

                # Add to priority queue
                queue_key = self._get_queue_key(priority)
                if scheduled_for:
                    # Delayed job - use sorted set with timestamp
                    self._redis.zadd(f"{queue_key}:delayed", {job_id: scheduled_for.timestamp()})
                else:
                    # Immediate job
                    self._redis.lpush(queue_key, job_id)

                # Publish event
                if STREAMING_AVAILABLE:
                    publish_event(
                        event_type="job_submitted",
                        source_system="task_queue",
                        payload={
                            "job_id": job_id,
                            "task": task_name,
                            "system": system,
                            "priority": priority.value,
                        },
                        correlation_id=correlation_id,
                        requires_governance=False,
                    )

                return job_id
            except Exception:
                pass

        return None

    def get_job(self, job_id: str) -> Job | None:
        """Get job by ID."""
        if not self._redis:
            return None

        try:
            data = self._redis.get(self._get_job_key(job_id))
            if data:
                job_dict = json.loads(data)
                # Convert priority and status enums
                job_dict["priority"] = JobPriority(job_dict.get("priority", 5))
                job_dict["status"] = JobStatus(job_dict.get("status", "pending"))
                return Job(**job_dict)
        except Exception:
            pass

        return None

    def _validate_job_with_superbrain(self, job: Job) -> bool:
        """Validate job execution via SuperBrain."""
        if not job.requires_governance:
            return True

        if not SUPERBRAIN_AVAILABLE or not self._brain:
            return True  # Fail open

        try:
            if hasattr(self._brain, "action_gate"):
                action_result = self._brain.action_gate.validate_action(
                    agent_id="task_queue",
                    action=f"execute_job_{job.task_name}",
                    details={
                        "job_id": job.job_id,
                        "system": job.system,
                        "payload_size": len(str(job.payload)),
                    },
                )
                return action_result.authorized
        except Exception:
            pass  # Fail open

        return True

    def _execute_job(self, job: Job) -> Any:
        """Execute job with handler."""
        handler = self._handlers.get(job.task_name)
        if not handler:
            raise ValueError(f"No handler for task: {job.task_name}")

        # Update status
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(UTC).isoformat()
        self._update_job(job)

        # CANONICAL: Validate via SuperBrain
        if not self._validate_job_with_superbrain(job):
            raise PermissionError(f"Job blocked by SuperBrain governance: {job.job_id}")

        # Execute handler
        start_time = time.time()
        try:
            result = handler(job.payload)

            # Update job success
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(UTC).isoformat()
            job.result = result

            # Update stats
            processing_time = time.time() - start_time
            self._stats.completed_jobs += 1
            self._update_avg_processing_time(processing_time)

            # Publish completion event
            if STREAMING_AVAILABLE:
                publish_event(
                    event_type="job_completed",
                    source_system="task_queue",
                    payload={
                        "job_id": job.job_id,
                        "task": job.task_name,
                        "duration": processing_time,
                    },
                    correlation_id=job.correlation_id,
                    requires_governance=False,
                )

            return result

        except Exception as e:
            # Handle failure
            job.retry_count += 1
            self._stats.failed_jobs += 1

            if job.retry_count < job.max_retries:
                job.status = JobStatus.RETRYING
                job.error = str(e)
                self._schedule_retry(job)
                self._stats.retried_jobs += 1
            else:
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.completed_at = datetime.now(UTC).isoformat()

                # Publish failure event
                if STREAMING_AVAILABLE:
                    publish_event(
                        event_type="job_failed",
                        source_system="task_queue",
                        payload={
                            "job_id": job.job_id,
                            "task": job.task_name,
                            "error": str(e),
                            "retries": job.retry_count,
                        },
                        correlation_id=job.correlation_id,
                        requires_governance=False,
                    )

            raise
        finally:
            self._update_job(job)

    def _schedule_retry(self, job: Job):
        """Schedule job for retry with exponential backoff."""
        delay = job.retry_delay * (2 ** (job.retry_count - 1))  # Exponential backoff
        retry_time = datetime.now(UTC) + timedelta(seconds=delay)

        if self._redis:
            try:
                queue_key = self._get_queue_key(job.priority)
                self._redis.zadd(f"{queue_key}:retry", {job.job_id: retry_time.timestamp()})
            except Exception:
                pass

    def _update_job(self, job: Job):
        """Update job in Redis."""
        if self._redis:
            try:
                self._redis.setex(
                    self._get_job_key(job.job_id), 86400, json.dumps(job.__dict__, default=str)
                )
            except Exception:
                pass

    def _update_avg_processing_time(self, processing_time: float):
        """Update average processing time."""
        if self._stats.completed_jobs == 1:
            self._stats.avg_processing_time = processing_time
        else:
            # Moving average
            self._stats.avg_processing_time = (
                0.9 * self._stats.avg_processing_time + 0.1 * processing_time
            )

    def register_handler(self, task_name: str, handler: Callable[[dict], Any]):
        """Register handler for task."""
        self._handlers[task_name] = handler

    def start_workers(self):
        """Start worker pool."""
        self._running = True
        self._stats.active_workers = self.max_workers

        # Start processing loop
        while self._running:
            job = self._fetch_next_job()
            if job:
                if CONCURRENT_AVAILABLE and self._executor:
                    self._executor.submit(self._execute_job, job)
                else:
                    try:
                        self._execute_job(job)
                    except Exception:
                        pass
            else:
                time.sleep(1)  # No jobs, sleep briefly

    def _fetch_next_job(self) -> Job | None:
        """Fetch next job from queue (prioritized)."""
        if not self._redis:
            return None

        # Check priority queues in order (high to low)
        for priority in [
            JobPriority.CRITICAL,
            JobPriority.HIGH,
            JobPriority.MEDIUM,
            JobPriority.LOW,
        ]:
            queue_key = self._get_queue_key(priority)

            # Check retry queue first
            retry_key = f"{queue_key}:retry"
            now = datetime.now(UTC).timestamp()

            try:
                # Get jobs ready for retry
                ready_jobs = self._redis.zrangebyscore(retry_key, 0, now, limit=1)
                if ready_jobs:
                    job_id = (
                        ready_jobs[0].decode()
                        if isinstance(ready_jobs[0], bytes)
                        else ready_jobs[0]
                    )
                    self._redis.zrem(retry_key, job_id)
                    return self.get_job(job_id)

                # Check delayed queue
                delayed_key = f"{queue_key}:delayed"
                ready_delayed = self._redis.zrangebyscore(delayed_key, 0, now, limit=1)
                if ready_delayed:
                    job_id = (
                        ready_delayed[0].decode()
                        if isinstance(ready_delayed[0], bytes)
                        else ready_delayed[0]
                    )
                    self._redis.zrem(delayed_key, job_id)
                    return self.get_job(job_id)

                # Check immediate queue
                job_id = self._redis.rpop(queue_key)
                if job_id:
                    job_id = job_id.decode() if isinstance(job_id, bytes) else job_id
                    return self.get_job(job_id)
            except Exception:
                pass

        return None

    def stop_workers(self):
        """Stop worker pool."""
        self._running = False
        if self._executor:
            self._executor.shutdown(wait=True)
        self._stats.active_workers = 0

    def get_stats(self) -> WorkerStats:
        """Get worker statistics."""
        # Update queue depth
        if self._redis:
            try:
                total_depth = 0
                for priority in JobPriority:
                    queue_key = self._get_queue_key(priority)
                    total_depth += self._redis.llen(queue_key) or 0
                    total_depth += self._redis.zcard(f"{queue_key}:delayed") or 0
                    total_depth += self._redis.zcard(f"{queue_key}:retry") or 0
                self._stats.queue_depth = total_depth
            except Exception:
                pass

        self._stats.last_updated = datetime.now(UTC).isoformat()
        return self._stats

    def cancel_job(self, job_id: str) -> bool:
        """Cancel pending job."""
        job = self.get_job(job_id)
        if not job:
            return False

        if job.status in [JobStatus.PENDING, JobStatus.RETRYING]:
            job.status = JobStatus.CANCELLED
            self._update_job(job)

            # Remove from queues
            if self._redis:
                try:
                    queue_key = self._get_queue_key(job.priority)
                    self._redis.lrem(queue_key, 0, job_id)
                    self._redis.zrem(f"{queue_key}:delayed", job_id)
                    self._redis.zrem(f"{queue_key}:retry", job_id)
                except Exception:
                    pass

            return True

        return False


# Global task queue
task_queue = TaskQueue()


# Convenience functions
def submit_task(
    task_name: str,
    payload: dict[str, Any],
    priority: JobPriority = JobPriority.MEDIUM,
    scheduled_for: datetime = None,
    correlation_id: str = None,
) -> str:
    """Submit task to queue."""
    return task_queue.submit_job(
        task_name=task_name,
        payload=payload,
        priority=priority,
        scheduled_for=scheduled_for,
        correlation_id=correlation_id,
    )


def get_job_status(job_id: str) -> JobStatus | None:
    """Get job status."""
    job = task_queue.get_job(job_id)
    return job.status if job else None


def cancel_task(job_id: str) -> bool:
    """Cancel task."""
    return task_queue.cancel_job(job_id)


def get_worker_stats() -> WorkerStats:
    """Get worker statistics."""
    return task_queue.get_stats()


def register_task_handler(task_name: str, handler: Callable[[dict], Any]):
    """Register task handler."""
    task_queue.register_handler(task_name, handler)
