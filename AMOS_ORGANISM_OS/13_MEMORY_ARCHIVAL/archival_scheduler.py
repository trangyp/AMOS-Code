"""Archival Scheduler — Automated Archival Scheduling

Schedules and manages archival processes, optimizes archival
timing, and handles batch operations.

Owner: Trang
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class JobStatus(Enum):
    """Status of archival job."""

    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(Enum):
    """Priority of archival job."""

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class ScheduleConfig:
    """Configuration for scheduling."""

    interval_minutes: int = 60
    batch_size: int = 100
    max_concurrent_jobs: int = 3
    retry_failed: bool = True
    max_retries: int = 3


@dataclass
class ArchivalJob:
    """An archival job."""

    job_id: str
    name: str
    priority: JobPriority
    status: JobStatus
    scheduled_at: datetime
    started_at: datetime = None
    completed_at: datetime = None
    memory_ids: List[str] = field(default_factory=list)
    processed_count: int = 0
    failed_count: int = 0
    error_message: str = None


class ArchivalScheduler:
    """Schedules and manages archival jobs.

    Handles batch archival operations, job prioritization,
    and scheduling optimization.
    """

    def __init__(self, config: Optional[ScheduleConfig] = None):
        self.config = config or ScheduleConfig()
        self.jobs: Dict[str, ArchivalJob] = {}
        self.job_queue: List[str] = []
        self.running_jobs: List[str] = []
        self.last_schedule_time: datetime = None

    def schedule_job(
        self,
        name: str,
        memory_ids: List[str],
        priority: JobPriority = JobPriority.NORMAL,
        scheduled_at: datetime = None,
    ) -> ArchivalJob:
        """Schedule a new archival job."""
        job_id = f"job_{len(self.jobs) + 1}"

        job = ArchivalJob(
            job_id=job_id,
            name=name,
            priority=priority,
            status=JobStatus.SCHEDULED,
            scheduled_at=scheduled_at or datetime.now(UTC),
            memory_ids=memory_ids,
        )

        self.jobs[job_id] = job

        # Add to queue based on priority
        self._add_to_queue(job_id)

        return job

    def _add_to_queue(self, job_id: str):
        """Add job to priority queue."""
        job = self.jobs[job_id]

        # Priority order
        priority_order = {
            JobPriority.CRITICAL: 0,
            JobPriority.HIGH: 1,
            JobPriority.NORMAL: 2,
            JobPriority.LOW: 3,
        }

        # Find position based on priority
        insert_pos = len(self.job_queue)
        for i, qid in enumerate(self.job_queue):
            qjob = self.jobs[qid]
            if priority_order[job.priority] < priority_order[qjob.priority]:
                insert_pos = i
                break

        self.job_queue.insert(insert_pos, job_id)

    def start_job(self, job_id: str) -> bool:
        """Start a scheduled job."""
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]

        if job.status != JobStatus.SCHEDULED:
            return False

        # Check concurrent limit
        if len(self.running_jobs) >= self.config.max_concurrent_jobs:
            return False

        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(UTC)

        if job_id in self.job_queue:
            self.job_queue.remove(job_id)

        self.running_jobs.append(job_id)
        return True

    def complete_job(self, job_id: str, processed: int, failed: int) -> bool:
        """Mark a job as completed."""
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]

        if job.status != JobStatus.RUNNING:
            return False

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(UTC)
        job.processed_count = processed
        job.failed_count = failed

        if job_id in self.running_jobs:
            self.running_jobs.remove(job_id)

        return True

    def fail_job(self, job_id: str, error_message: str) -> bool:
        """Mark a job as failed."""
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]

        if job.status != JobStatus.RUNNING:
            return False

        job.status = JobStatus.FAILED
        job.completed_at = datetime.now(UTC)
        job.error_message = error_message

        if job_id in self.running_jobs:
            self.running_jobs.remove(job_id)

        # Retry if enabled
        if self.config.retry_failed:
            job.status = JobStatus.SCHEDULED
            job.scheduled_at = datetime.now(UTC) + timedelta(minutes=5)
            self._add_to_queue(job_id)

        return True

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job."""
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]

        if job.status not in [JobStatus.SCHEDULED, JobStatus.RUNNING]:
            return False

        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now(UTC)

        if job_id in self.job_queue:
            self.job_queue.remove(job_id)

        if job_id in self.running_jobs:
            self.running_jobs.remove(job_id)

        return True

    def get_next_jobs(self, count: int = 1) -> List[ArchivalJob]:
        """Get next jobs to process."""
        available_slots = self.config.max_concurrent_jobs - len(self.running_jobs)
        count = min(count, available_slots, len(self.job_queue))

        jobs = []
        for i in range(count):
            if i < len(self.job_queue):
                job_id = self.job_queue[i]
                jobs.append(self.jobs[job_id])

        return jobs

    def get_jobs_by_status(self, status: JobStatus) -> List[ArchivalJob]:
        """Get all jobs with a specific status."""
        return [j for j in self.jobs.values() if j.status == status]

    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return {
            "total_jobs": len(self.jobs),
            "scheduled": len(self.get_jobs_by_status(JobStatus.SCHEDULED)),
            "running": len(self.running_jobs),
            "completed": len(self.get_jobs_by_status(JobStatus.COMPLETED)),
            "failed": len(self.get_jobs_by_status(JobStatus.FAILED)),
            "queue_length": len(self.job_queue),
            "max_concurrent": self.config.max_concurrent_jobs,
        }


if __name__ == "__main__":
    print("Archival Scheduler Module")
    print("=" * 50)

    scheduler = ArchivalScheduler()

    # Schedule jobs
    job1 = scheduler.schedule_job(
        "Batch Archive 1",
        ["mem_001", "mem_002", "mem_003"],
        JobPriority.HIGH,
    )
    print(f"Scheduled: {job1.name}")

    job2 = scheduler.schedule_job(
        "Batch Archive 2",
        ["mem_004", "mem_005"],
        JobPriority.NORMAL,
    )
    print(f"Scheduled: {job2.name}")

    # Start job
    if scheduler.start_job(job1.job_id):
        print(f"Started: {job1.name}")

    # Complete job
    scheduler.complete_job(job1.job_id, 3, 0)
    print(f"Completed: {job1.name}")

    stats = scheduler.get_scheduler_stats()
    print(f"\nStats: {stats}")

    print("Archival Scheduler ready")
