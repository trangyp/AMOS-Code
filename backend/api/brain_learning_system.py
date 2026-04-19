"""Brain Learning System API - AMOS brain-powered learning and training.

Provides learning capabilities:
- Training job management
- Learning progress tracking
- Model versioning and deployment
- Training data management
- Performance evaluation
- Learning rate optimization
"""


import asyncio
import hashlib
import sys
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone

UTC = timezone.utc
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "amos_brain"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Import brain components
try:
    from cognitive_engine import get_cognitive_engine

    from memory import BrainMemory

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain/learning", tags=["Brain Learning System"])


class JobStatus(str, Enum):
    """Training job status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    """Type of learning job."""

    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    FINE_TUNING = "fine_tuning"
    TRANSFER = "transfer"


class TrainingJob(BaseModel):
    """Training job model."""

    job_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    name: str
    job_type: JobType
    status: JobStatus = JobStatus.PENDING
    dataset_id: str = ""
    model_config: Dict[str, Any] = Field(default_factory=dict)
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    epochs_total: int = Field(default=10, ge=1)
    epochs_completed: int = Field(default=0, ge=0)
    loss_history: List[float] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    error_message: Optional[str] = None
    model_id: Optional[str] = None


class Dataset(BaseModel):
    """Training dataset model."""

    dataset_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    name: str
    description: str = ""
    data_type: str = "mixed"
    record_count: int = 0
    feature_count: int = 0
    size_mb: float = 0.0
    hash: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ModelVersion(BaseModel):
    """Trained model version."""

    model_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    name: str
    version: str = "1.0.0"
    job_id: str
    architecture: str = ""
    parameters_count: int = 0
    training_duration_seconds: float = 0.0
    final_loss: Optional[float] = None
    accuracy: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_deployed: bool = False
    deployment_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)


class LearningMetrics(BaseModel):
    """Learning system metrics."""

    total_jobs: int
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_datasets: int
    total_models: int
    deployed_models: int
    avg_training_time_hours: float
    system_health: str


class LearningEngine:
    """Brain learning engine."""

    def __init__(self) -> None:
        self._jobs: Dict[str, TrainingJob] = {}
        self._datasets: Dict[str, Dataset] = {}
        self._models: Dict[str, ModelVersion] = {}
        self._lock = asyncio.Lock()
        self._cognitive_engine = None
        self._memory = None

    async def _get_cognitive_engine(self) -> Any:
        """Get cognitive engine."""
        if _BRAIN_AVAILABLE and self._cognitive_engine is None:
            try:
                self._cognitive_engine = get_cognitive_engine()
            except Exception:
                pass
        return self._cognitive_engine

    async def _get_memory(self) -> Any:
        """Get brain memory."""
        if _BRAIN_AVAILABLE and self._memory is None:
            try:
                self._memory = BrainMemory()
            except Exception:
                pass
        return self._memory

    async def create_job(self, job: TrainingJob) -> TrainingJob:
        """Create a training job."""
        async with self._lock:
            # Validate dataset exists
            if job.dataset_id and job.dataset_id not in self._datasets:
                raise HTTPException(status_code=404, detail=f"Dataset {job.dataset_id} not found")

            self._jobs[job.job_id] = job

            # Save to memory if available
            memory = await self._get_memory()
            if memory and hasattr(memory, "save_reasoning"):
                try:
                    memory.save_reasoning(
                        problem=f"Training job: {job.name}",
                        analysis=job.model_dump(),
                        tags=["learning", job.job_type.value],
                    )
                except Exception:
                    pass

            return job

    async def get_job(self, job_id: str) -> Optional[TrainingJob]:
        """Get training job by ID."""
        return self._jobs.get(job_id)

    async def list_jobs(
        self, status: Optional[JobStatus] = None, job_type: Optional[JobType] = None, limit: int = 50
    ) -> List[TrainingJob]:
        """List training jobs with optional filtering."""
        jobs = list(self._jobs.values())

        if status:
            jobs = [j for j in jobs if j.status == status]

        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]

        # Sort by created_at desc
        jobs.sort(key=lambda j: j.created_at, reverse=True)

        return jobs[:limit]

    async def start_job(self, job_id: str) -> TrainingJob:
        """Start a training job."""
        async with self._lock:
            if job_id not in self._jobs:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

            job = self._jobs[job_id]

            if job.status != JobStatus.PENDING:
                raise HTTPException(
                    status_code=400, detail=f"Cannot start job with status {job.status}"
                )

            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(UTC)

            # Start training simulation
            asyncio.create_task(self._simulate_training(job_id))

            return job

    async def _simulate_training(self, job_id: str) -> None:
        """Simulate training process."""
        job = self._jobs.get(job_id)
        if not job:
            return

        try:
            for epoch in range(job.epochs_completed, job.epochs_total):
                # Simulate epoch training
                await asyncio.sleep(0.5)  # Fast simulation

                # Update progress
                job.epochs_completed = epoch + 1
                job.progress_percent = (job.epochs_completed / job.epochs_total) * 100

                # Simulate loss curve
                import math

                loss = 1.0 * math.exp(-0.1 * job.epochs_completed) + 0.05
                job.loss_history.append(loss)

                # Check if still running
                if job.status != JobStatus.RUNNING:
                    break

            # Complete job if finished
            if job.status == JobStatus.RUNNING:
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now(UTC)
                job.progress_percent = 100.0
                job.metrics["final_loss"] = job.loss_history[-1] if job.loss_history else 0.0
                job.metrics["accuracy"] = (
                    0.85 + (0.1 * (1.0 - job.loss_history[-1])) if job.loss_history else 0.85
                )

                # Create model version
                model = ModelVersion(
                    name=f"{job.name}-model",
                    job_id=job.job_id,
                    training_duration_seconds=(job.completed_at - job.started_at).total_seconds()
                    if job.started_at
                    else 0,
                    final_loss=job.metrics.get("final_loss"),
                    accuracy=job.metrics.get("accuracy"),
                )
                self._models[model.model_id] = model
                job.model_id = model.model_id

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)

    async def pause_job(self, job_id: str) -> TrainingJob:
        """Pause a running job."""
        async with self._lock:
            if job_id not in self._jobs:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

            job = self._jobs[job_id]
            if job.status != JobStatus.RUNNING:
                raise HTTPException(status_code=400, detail="Can only pause running jobs")

            job.status = JobStatus.PAUSED
            return job

    async def cancel_job(self, job_id: str) -> TrainingJob:
        """Cancel a job."""
        async with self._lock:
            if job_id not in self._jobs:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

            job = self._jobs[job_id]
            if job.status not in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.PAUSED]:
                raise HTTPException(status_code=400, detail="Cannot cancel completed job")

            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now(UTC)
            return job

    async def create_dataset(self, dataset: Dataset) -> Dataset:
        """Create a dataset entry."""
        async with self._lock:
            # Generate hash from name
            dataset.hash = hashlib.sha256(dataset.name.encode()).hexdigest()[:16]
            self._datasets[dataset.dataset_id] = dataset
            return dataset

    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Get dataset by ID."""
        return self._datasets.get(dataset_id)

    async def list_datasets(self, limit: int = 50) -> List[Dataset]:
        """List datasets."""
        datasets = list(self._datasets.values())
        datasets.sort(key=lambda d: d.created_at, reverse=True)
        return datasets[:limit]

    async def get_model(self, model_id: str) -> Optional[ModelVersion]:
        """Get model by ID."""
        return self._models.get(model_id)

    async def list_models(self, deployed_only: bool = False, limit: int = 50) -> List[ModelVersion]:
        """List models."""
        models = list(self._models.values())

        if deployed_only:
            models = [m for m in models if m.is_deployed]

        models.sort(key=lambda m: m.created_at, reverse=True)
        return models[:limit]

    async def deploy_model(self, model_id: str) -> ModelVersion:
        """Deploy a model."""
        async with self._lock:
            if model_id not in self._models:
                raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

            model = self._models[model_id]
            model.is_deployed = True
            model.deployment_date = datetime.now(UTC)

            return model

    async def get_metrics(self) -> LearningMetrics:
        """Get learning system metrics."""
        jobs = list(self._jobs.values())
        active = len([j for j in jobs if j.status == JobStatus.RUNNING])
        completed = len([j for j in jobs if j.status == JobStatus.COMPLETED])
        failed = len([j for j in jobs if j.status == JobStatus.FAILED])

        # Calculate average training time
        completed_jobs = [
            j for j in jobs if j.status == JobStatus.COMPLETED and j.completed_at and j.started_at
        ]
        avg_time = 0.0
        if completed_jobs:
            total_seconds = sum(
                (j.completed_at - j.started_at).total_seconds() for j in completed_jobs
            )
            avg_time = (total_seconds / len(completed_jobs)) / 3600  # Convert to hours

        models = list(self._models.values())
        deployed = len([m for m in models if m.is_deployed])

        # System health
        health = (
            "healthy"
            if failed == 0 or (completed / max(1, completed + failed)) > 0.8
            else "degraded"
        )

        return LearningMetrics(
            total_jobs=len(jobs),
            active_jobs=active,
            completed_jobs=completed,
            failed_jobs=failed,
            total_datasets=len(self._datasets),
            total_models=len(models),
            deployed_models=deployed,
            avg_training_time_hours=avg_time,
            system_health=health,
        )

    async def stream_job_progress(self, job_id: str) -> AsyncIterator[dict[str, Any]]:
        """Stream job progress updates."""
        job = self._jobs.get(job_id)
        if not job:
            return

        last_progress = -1
        while job.status in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.PAUSED]:
            if job.progress_percent != last_progress:
                yield {
                    "job_id": job_id,
                    "status": job.status.value,
                    "progress": job.progress_percent,
                    "epoch": job.epochs_completed,
                    "total_epochs": job.epochs_total,
                    "current_loss": job.loss_history[-1] if job.loss_history else None,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                last_progress = job.progress_percent

            await asyncio.sleep(1.0)

        # Final update
        yield {
            "job_id": job_id,
            "status": job.status.value,
            "progress": job.progress_percent,
            "epoch": job.epochs_completed,
            "total_epochs": job.epochs_total,
            "final_loss": job.loss_history[-1] if job.loss_history else None,
            "metrics": job.metrics,
            "timestamp": datetime.now(UTC).isoformat(),
        }


# Global engine
_learning_engine: Optional[LearningEngine] = None


def get_learning_engine() -> LearningEngine:
    """Get or create learning engine."""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = LearningEngine()
    return _learning_engine


@router.post("/jobs", response_model=TrainingJob)
async def create_job(job: TrainingJob) -> TrainingJob:
    """Create a training job."""
    engine = get_learning_engine()
    return await engine.create_job(job)


@router.get("/jobs/{job_id}", response_model=TrainingJob)
async def get_job(job_id: str) -> TrainingJob:
    """Get training job by ID."""
    engine = get_learning_engine()
    job = await engine.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@router.get("/jobs", response_model=list[TrainingJob])
async def list_jobs(
    status: Optional[JobStatus] = None,
    job_type: Optional[JobType] = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> List[TrainingJob]:
    """List training jobs."""
    engine = get_learning_engine()
    return await engine.list_jobs(status, job_type, limit)


@router.post("/jobs/{job_id}/start")
async def start_job(job_id: str) -> TrainingJob:
    """Start a training job."""
    engine = get_learning_engine()
    return await engine.start_job(job_id)


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str) -> TrainingJob:
    """Pause a training job."""
    engine = get_learning_engine()
    return await engine.pause_job(job_id)


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str) -> TrainingJob:
    """Cancel a training job."""
    engine = get_learning_engine()
    return await engine.cancel_job(job_id)


@router.get("/jobs/{job_id}/stream")
async def stream_job_progress(job_id: str) -> StreamingResponse:
    """Stream job progress via SSE."""
    engine = get_learning_engine()

    async def event_generator():
        async for update in engine.stream_job_progress(job_id):
            yield f"data: {update}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/datasets", response_model=Dataset)
async def create_dataset(dataset: Dataset) -> Dataset:
    """Create a dataset entry."""
    engine = get_learning_engine()
    return await engine.create_dataset(dataset)


@router.get("/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str) -> Dataset:
    """Get dataset by ID."""
    engine = get_learning_engine()
    dataset = await engine.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    return dataset


@router.get("/datasets", response_model=list[Dataset])
async def list_datasets(limit: int = Query(default=50, ge=1, le=200)) -> List[Dataset]:
    """List datasets."""
    engine = get_learning_engine()
    return await engine.list_datasets(limit)


@router.get("/models/{model_id}", response_model=ModelVersion)
async def get_model(model_id: str) -> ModelVersion:
    """Get model by ID."""
    engine = get_learning_engine()
    model = await engine.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    return model


@router.get("/models", response_model=list[ModelVersion])
async def list_models(
    deployed_only: bool = False, limit: int = Query(default=50, ge=1, le=200)
) -> List[ModelVersion]:
    """List trained models."""
    engine = get_learning_engine()
    return await engine.list_models(deployed_only, limit)


@router.post("/models/{model_id}/deploy")
async def deploy_model(model_id: str) -> ModelVersion:
    """Deploy a model."""
    engine = get_learning_engine()
    return await engine.deploy_model(model_id)


@router.get("/metrics", response_model=LearningMetrics)
async def get_metrics() -> LearningMetrics:
    """Get learning system metrics."""
    engine = get_learning_engine()
    return await engine.get_metrics()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for learning system."""
    engine = get_learning_engine()
    metrics = await engine.get_metrics()

    return {
        "status": "healthy" if metrics.system_health == "healthy" else "degraded",
        "brain_available": _BRAIN_AVAILABLE,
        "total_jobs": metrics.total_jobs,
        "active_jobs": metrics.active_jobs,
        "system_health": metrics.system_health,
        "engine": "active",
    }
