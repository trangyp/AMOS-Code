#!/usr/bin/env python3
"""AMOS Background Worker - Async Task Queue

Production-grade background task processing with:
- Async job queue using Redis
- Task prioritization
- Retry mechanism with exponential backoff
- Job status tracking
- Dead letter queue for failed jobs

Based on 2024 async task queue patterns (similar to Celery but native async).
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Redis import
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  Redis not installed. Worker disabled. Run: pip install redis")

# AMOS brain integration
try:
    from amos_brain import think
    AMOS_AVAILABLE = True
except ImportError:
    AMOS_AVAILABLE = False


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD = "dead"


class JobPriority(int, Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


@dataclass
class Job:
    """Background job definition."""
    id: str
    task_name: str
    args: list
    kwargs: dict
    priority: JobPriority
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class AMOSWorker:
    """AMOS Background Worker - Process async tasks."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis: Optional[redis.Redis] = None
        self._running = False
        self._tasks: dict[str, Callable] = {}
        self._task_queue: Optional[asyncio.Queue] = None
        
    async def initialize(self) -> bool:
        """Initialize worker with Redis."""
        if not REDIS_AVAILABLE:
            print("❌ Redis not available")
            return False
        
        try:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
            await self._redis.ping()
            self._task_queue = asyncio.Queue()
            print("✅ Worker initialized with Redis")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            return False
    
    def register_task(self, name: str, func: Callable) -> None:
        """Register a task handler."""
        self._tasks[name] = func
        print(f"✅ Registered task: {name}")
    
    async def submit(
        self,
        task_name: str,
        *args,
        priority: JobPriority = JobPriority.NORMAL,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """Submit a job to the queue."""
        if not self._redis:
            raise RuntimeError("Worker not initialized")
        
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            task_name=task_name,
            args=list(args),
            kwargs=kwargs,
            priority=priority,
            status=JobStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            max_retries=max_retries,
        )
        
        # Store job data
        job_data = json.dumps({
            "id": job.id,
            "task_name": job.task_name,
            "args": job.args,
            "kwargs": job.kwargs,
            "priority": job.priority.value,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "retry_count": job.retry_count,
            "max_retries": job.max_retries,
        })
        
        # Add to sorted set by priority (score = priority + timestamp for FIFO within priority)
        score = -job.priority.value  # Negative for descending order
        await self._redis.zadd("amos:jobs:pending", {job_data: score})
        
        print(f"✅ Job submitted: {job_id} ({task_name}, priority={priority.name})")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get job status by ID."""
        if not self._redis:
            return None
        
        # Check in all job stores
        for status in JobStatus:
            jobs = await self._redis.zrange(f"amos:jobs:{status.value}", 0, -1)
            for job_data in jobs:
                job_dict = json.loads(job_data)
                if job_dict["id"] == job_id:
                    return status
        
        return None
    
    async def _process_job(self, job_data: str) -> None:
        """Process a single job."""
        job_dict = json.loads(job_data)
        job_id = job_dict["id"]
        task_name = job_dict["task_name"]
        
        print(f"🔄 Processing job: {job_id} ({task_name})")
        
        # Update status to running
        job_dict["status"] = JobStatus.RUNNING.value
        job_dict["started_at"] = datetime.now(timezone.utc).isoformat()
        
        try:
            # Get task handler
            handler = self._tasks.get(task_name)
            if not handler:
                raise ValueError(f"Unknown task: {task_name}")
            
            # Execute task
            args = job_dict["args"]
            kwargs = job_dict["kwargs"]
            result = await handler(*args, **kwargs)
            
            # Mark completed
            job_dict["status"] = JobStatus.COMPLETED.value
            job_dict["completed_at"] = datetime.now(timezone.utc).isoformat()
            job_dict["result"] = str(result) if result else None
            
            await self._redis.zadd("amos:jobs:completed", {json.dumps(job_dict): 0})
            print(f"✅ Job completed: {job_id}")
            
        except Exception as e:
            error_msg = f"{e}\n{traceback.format_exc()}"
            job_dict["error"] = error_msg
            job_dict["retry_count"] = job_dict.get("retry_count", 0) + 1
            
            if job_dict["retry_count"] < job_dict["max_retries"]:
                # Retry with exponential backoff
                job_dict["status"] = JobStatus.RETRYING.value
                delay = 2 ** job_dict["retry_count"]  # 2, 4, 8 seconds...
                await asyncio.sleep(delay)
                await self._redis.zadd("amos:jobs:pending", {json.dumps(job_dict): -job_dict["priority"]})
                print(f"⚠️  Job retrying: {job_id} (attempt {job_dict['retry_count']})")
            else:
                # Dead letter queue
                job_dict["status"] = JobStatus.DEAD.value
                await self._redis.zadd("amos:jobs:dead", {json.dumps(job_dict): 0})
                print(f"❌ Job failed permanently: {job_id}")
    
    async def start(self) -> None:
        """Start worker processing loop."""
        if not self._redis:
            print("❌ Worker not initialized")
            return
        
        self._running = True
        print("🚀 Worker started - processing jobs...")
        
        while self._running:
            try:
                # Get highest priority job
                jobs = await self._redis.zpopmax("amos:jobs:pending", count=1)
                
                if not jobs:
                    await asyncio.sleep(1)
                    continue
                
                job_data = jobs[0][0]  # (data, score)
                await self._process_job(job_data)
                
            except Exception as e:
                print(f"❌ Worker error: {e}")
                await asyncio.sleep(5)
    
    def stop(self) -> None:
        """Stop worker."""
        self._running = False
        print("🛑 Worker stopped")


# Global worker instance
_worker: Optional[AMOSWorker] = None


def get_worker() -> AMOSWorker:
    """Get or create global worker."""
    global _worker
    if _worker is None:
        _worker = AMOSWorker()
    return _worker


# Pre-defined task handlers
async def task_think(query: str) -> str:
    """Background thinking task."""
    if AMOS_AVAILABLE:
        result = think(query)
        return result.content
    return "Brain not available"


async def task_heal_repo(repo_path: str) -> dict:
    """Background repo healing task."""
    # Run the heal script
    import subprocess
    result = subprocess.run(
        ["python3", "amos_self_heal_py39.py", repo_path],
        capture_output=True,
        text=True,
        timeout=300
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout[:500],
        "stderr": result.stderr[:500],
    }


async def main():
    """Run worker standalone."""
    worker = get_worker()
    
    if not await worker.initialize():
        return
    
    # Register tasks
    worker.register_task("think", task_think)
    worker.register_task("heal_repo", task_heal_repo)
    
    # Start processing
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
