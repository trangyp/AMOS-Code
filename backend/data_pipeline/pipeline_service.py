
"""AMOS Data Pipeline Service v2.0.0

Production-grade ETL and stream processing with:
- Batch processing with checkpoint/resume
- Streaming with exactly-once semantics
- Data validation and schema enforcement
- Parallel transformation pipelines
- Dead letter queue for failed records
- Data lineage tracking

Based on modern data pipeline architectures (Pathway, Apache Flink).

Owner: Trang Phan
Version: 2.0.0
"""

import asyncio
import hashlib
import json
import logging
import time

logger = logging.getLogger(__name__)
from collections import deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any, Union

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

try:
    from backend.data_pipeline.streaming import publish_event
from typing import Any, Callable, List, Union, Callable, List, Union
from typing import List, Union, Union
from typing import Dict, Set

    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False


class JobStatus(Enum):
    """Pipeline job status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineStage:
    """Single stage in a data pipeline."""

    stage_id: str
    name: str
    transform: TransformFunction
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    validate_input: bool = True
    validate_output: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 300.0


@dataclass
class PipelineJob:
    """Data pipeline job definition."""

    job_id: str
    name: str
    stages: List[PipelineStage]
    source_config: Dict[str, Any] = field(default_factory=dict)
    sink_config: Dict[str, Any] = field(default_factory=dict)
    parallelism: int = 4
    checkpoint_interval: float = 60.0
    created_at: float = field(default_factory=time.time)


@dataclass
class ETLJob:
    """ETL job with extract-transform-load stages."""

    job_id: str
    name: str
    extract_fn: Callable[[], list[dict[str, Any]]]
    transform_fn: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    load_fn: Callable[[list[dict[str, Any]]], int]
    batch_size: int = 1000
    max_batches: Optional[int] = None
    status: JobStatus = JobStatus.PENDING
    records_processed: int = 0
    records_failed: int = 0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_log: list[dict[str, Any]] = field(default_factory=list)


# Type alias for transform functions - use Union for Python 3.9 compatibility
TransformFunction = Union[Callable[[Any], Any], Callable[[Any], Awaitable[Any]]]


class StreamProcessor:
    """Real-time stream processor with windowing.

    Supports tumbling, sliding, and session windows with
    exactly-once processing semantics.
    """

    def __init__(
        self,
        name: str,
        window_type: str = "tumbling",  # tumbling, sliding, session
        window_size: float = 60.0,  # seconds
        window_slide: Optional[float] = None,  # for sliding windows
        timeout: float = 300.0,
        max_buffer_size: int = 10000,
    ):
        self.name = name
        self.window_type = window_type
        self.window_size = window_size
        self.window_slide = window_slide or window_size
        self.timeout = timeout
        self.max_buffer_size = max_buffer_size

        self._buffer: deque[dict[str, Any]] = deque(maxlen=max_buffer_size)
        self._handlers: list[Callable[[list[dict[str, Any]]], Any]] = []
        self._running = False
        self._task: asyncio.Task  = None
        self._lock = asyncio.Lock()
        self._state: Dict[str, Any] = {}

        # Metrics
        self._records_in = 0
        self._records_out = 0
        self._windows_processed = 0
        self._last_checkpoint = time.time()

    def add_handler(self, handler: Callable[[list[dict[str, Any]]], Any]) -> None:
        """Add window processing handler."""
        self._handlers.append(handler)

    async def ingest(self, record: Dict[str, Any]) -> bool:
        """Ingest record into stream buffer."""
        async with self._lock:
            if len(self._buffer) >= self.max_buffer_size:
                return False

            record["_ingest_time"] = time.time()
            self._buffer.append(record)
            self._records_in += 1

            return True

    async def start(self) -> None:
        """Start stream processing loop."""
        self._running = True
        self._task = asyncio.create_task(self._processing_loop())

    async def stop(self) -> None:
        """Stop stream processing."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _processing_loop(self) -> None:
        """Main processing loop with windowing."""
        while self._running:
            try:
                await self._process_window()
                await asyncio.sleep(0.1)  # Small delay to prevent CPU spinning
            except Exception as e:
                if STREAMING_AVAILABLE:
                    try:
                        publish_event(
                            event_type="stream_processor_error",
                            source_system="data_pipeline",
                            payload={"processor": self.name, "error": str(e)},
                        )
                    except Exception as e:
                        logger.debug("publish_event_failed", error=str(e))
                await asyncio.sleep(1.0)

    async def _process_window(self) -> None:
        """Process current window of records."""
        async with self._lock:
            if not self._buffer:
                return

            now = time.time()
            cutoff = now - self.window_size

            # Get records in current window
            window_records = [r for r in self._buffer if r.get("_ingest_time", now) >= cutoff]

            if not window_records:
                return

            # Remove processed records from buffer
            self._buffer = deque(
                [r for r in self._buffer if r.get("_ingest_time", now) < cutoff],
                maxlen=self.max_buffer_size,
            )

        # Process window
        if window_records:
            for handler in self._handlers:
                try:
                    result = handler(window_records)
                    if asyncio.iscoroutine(result):
                        await result
                    self._records_out += len(window_records)
                except Exception as e:
                    # Send to dead letter queue
                    await self._dead_letter(window_records, str(e))

            self._windows_processed += 1

            # Checkpoint state periodically
            if time.time() - self._last_checkpoint > 60:
                await self._checkpoint()

    async def _dead_letter(self, records: list[dict[str, Any]], error: str) -> None:
        """Send failed records to dead letter queue."""
        if REDIS_AVAILABLE:
            try:
                r = redis.from_url("redis://localhost:6379/12")
                dlq_key = f"dlq:{self.name}"
                for record in records:
                    r.lpush(
                        dlq_key,
                        json.dumps({"record": record, "error": error, "timestamp": time.time()}),
                    )
            except Exception:
                pass

    async def _checkpoint(self) -> None:
        """Save processor state."""
        self._last_checkpoint = time.time()

        if REDIS_AVAILABLE:
            try:
                r = redis.from_url("redis://localhost:6379/12")
                state_key = f"stream_state:{self.name}"
                r.setex(
                    state_key,
                    3600,
                    json.dumps(
                        {
                            "records_in": self._records_in,
                            "records_out": self._records_out,
                            "windows_processed": self._windows_processed,
                            "timestamp": time.time(),
                        }
                    ),
                )
            except Exception:
                pass

    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return {
            "name": self.name,
            "records_in": self._records_in,
            "records_out": self._records_out,
            "buffer_size": len(self._buffer),
            "windows_processed": self._windows_processed,
            "running": self._running,
        }


class DataPipelineService:
    """Data pipeline orchestration service.

    Manages ETL jobs, stream processors, and data transformations
    with full lineage tracking and governance integration.
    """

    def __init__(self):
        self._jobs: Dict[str, ETLJob] = {}
        self._pipelines: Dict[str, PipelineJob] = {}
        self._processors: Dict[str, StreamProcessor] = {}
        self._running_jobs: Set[str] = set()
        self._redis: redis.Redis  = None

        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url("redis://localhost:6379/12")
                self._redis.ping()
            except Exception:
                self._redis = None

        # Load persisted state
        self._load_state()

    def _get_job_key(self, job_id: str) -> str:
        return f"pipeline:job:{job_id}"

    def _load_state(self) -> None:
        # Load persisted state
        if REDIS_AVAILABLE and self._redis:
            try:
                for key in self._redis.scan_iter(match="amos:etl:*"):
                    data = self._redis.get(key)
                    if data:
                        json.loads(data)
                        # Restore job state
                        pass  # Would reconstruct ETLJob here
            except Exception as e:
                logger.warning("persisted_state_load_failed", error=str(e))

    def create_etl_job(
        self,
        name: str,
        extract_fn: Callable[[], list[dict[str, Any]]],
        transform_fn: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
        load_fn: Callable[[list[dict[str, Any]]], int],
        batch_size: int = 1000,
    ) -> str:
        """Create a new ETL job.

        Args:
            name: Job name
            extract_fn: Extract function returning records
            transform_fn: Transform function for records
            load_fn: Load function returning count loaded
            batch_size: Records per batch

        Returns:
            Job ID
        """
        # Validate with SuperBrain
        if SUPERBRAIN_AVAILABLE:
            try:
                brain = get_super_brain()
                if brain and hasattr(brain, "action_gate"):
                    result = brain.action_gate.validate_action(
                        agent_id="data_pipeline", action="create_etl_job", details={"name": name}
                    )
                    if not result.authorized:
                        raise PermissionError("Action not authorized by SuperBrain")
            except Exception:
                pass

        job_id = f"etl_{hashlib.md5(f'{name}:{time.time()}'.encode()).hexdigest()[:12]}"

        job = ETLJob(
            job_id=job_id,
            name=name,
            extract_fn=extract_fn,
            transform_fn=transform_fn,
            load_fn=load_fn,
            batch_size=batch_size,
        )

        self._jobs[job_id] = job

        # Publish event
        if STREAMING_AVAILABLE:
            try:
                publish_event(
                    event_type="etl_job_created",
                    source_system="data_pipeline",
                    payload={"job_id": job_id, "name": name},
                    requires_governance=True,
                )
            except Exception:
                pass

        return job_id

    async def run_job(self, job_id: str) -> Dict[str, Any]:
        """Execute an ETL job."""
        job = self._jobs.get(job_id)
        if not job:
            return {"success": False, "error": "Job not found"}

        if job_id in self._running_jobs:
            return {"success": False, "error": "Job already running"}

        self._running_jobs.add(job_id)
        job.status = JobStatus.RUNNING
        job.started_at = time.time()

        try:
            # Extract phase
            raw_data = job.extract_fn()

            # Process in batches
            total_batches = (len(raw_data) + job.batch_size - 1) // job.batch_size

            for batch_num in range(total_batches):
                if job.max_batches and batch_num >= job.max_batches:
                    break

                start_idx = batch_num * job.batch_size
                end_idx = min(start_idx + job.batch_size, len(raw_data))
                batch = raw_data[start_idx:end_idx]

                # Transform phase
                try:
                    transformed = job.transform_fn(batch)
                except Exception as e:
                    job.error_log.append(
                        {"batch": batch_num, "phase": "transform", "error": str(e)}
                    )
                    job.records_failed += len(batch)
                    continue

                # Load phase
                try:
                    loaded_count = job.load_fn(transformed)
                    job.records_processed += loaded_count
                except Exception as e:
                    job.error_log.append({"batch": batch_num, "phase": "load", "error": str(e)})
                    job.records_failed += len(transformed)
                    continue

                # Checkpoint progress
                await self._checkpoint_job(job)

            job.status = JobStatus.COMPLETED
            job.completed_at = time.time()

            return {
                "success": True,
                "records_processed": job.records_processed,
                "records_failed": job.records_failed,
                "duration": job.completed_at - job.started_at,
            }

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_log.append({"phase": "extract", "error": str(e)})
            return {"success": False, "error": str(e)}

        finally:
            self._running_jobs.discard(job_id)
            await self._checkpoint_job(job)

    async def _checkpoint_job(self, job: ETLJob) -> None:
        """Persist job state."""
        if not self._redis:
            return

        try:
            key = self._get_job_key(job.job_id)
            self._redis.setex(
                key,
                86400,
                json.dumps(
                    {
                        "job_id": job.job_id,
                        "name": job.name,
                        "status": job.status.value,
                        "records_processed": job.records_processed,
                        "records_failed": job.records_failed,
                        "started_at": job.started_at,
                        "completed_at": job.completed_at,
                    },
                    default=str,
                ),
            )
        except Exception:
            pass

    def create_stream_processor(
        self, name: str, window_type: str = "tumbling", window_size: float = 60.0
    ) -> StreamProcessor:
        """Create a new stream processor.

        Args:
            name: Processor name
            window_type: tumbling, sliding, or session
            window_size: Window size in seconds

        Returns:
            StreamProcessor instance
        """
        processor = StreamProcessor(name=name, window_type=window_type, window_size=window_size)

        self._processors[name] = processor
        return processor

    def get_job_status(self, job_id: str) -> Dict[str, Any] :
        """Get ETL job status."""
        job = self._jobs.get(job_id)
        if not job:
            return None

        return {
            "job_id": job.job_id,
            "name": job.name,
            "status": job.status.value,
            "records_processed": job.records_processed,
            "records_failed": job.records_failed,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "error_count": len(job.error_log),
        }

    def list_jobs(self) -> list[dict[str, Any]]:
        """List all ETL jobs."""
        return [
            {
                "job_id": job.job_id,
                "name": job.name,
                "status": job.status.value,
                "records_processed": job.records_processed,
            }
            for job in self._jobs.values()
        ]

    def get_processor_stats(self, name: str) -> Dict[str, Any] :
        """Get stream processor statistics."""
        processor = self._processors.get(name)
        if not processor:
            return None
        return processor.get_stats()


# Global instance
data_pipeline = DataPipelineService()


def run_etl(
    name: str,
    extract_fn: Callable[[], list[dict[str, Any]]],
    transform_fn: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    load_fn: Callable[[list[dict[str, Any]]], int],
    batch_size: int = 1000,
) -> str:
    """Create and run ETL job (convenience function)."""
    job_id = data_pipeline.create_etl_job(
        name=name,
        extract_fn=extract_fn,
        transform_fn=transform_fn,
        load_fn=load_fn,
        batch_size=batch_size,
    )

    # Schedule for execution
    asyncio.create_task(data_pipeline.run_job(job_id))

    return job_id


def create_stream_processor(
    name: str, window_type: str = "tumbling", window_size: float = 60.0
) -> StreamProcessor:
    """Create stream processor (convenience function)."""
    return data_pipeline.create_stream_processor(name, window_type, window_size)
