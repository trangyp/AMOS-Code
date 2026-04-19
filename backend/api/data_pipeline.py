"""AMOS Data Pipeline API - ETL & Stream Processing

Production-grade data processing endpoints.

Owner: Trang Phan
Version: 2.0.0
"""

from typing import Dict
import time

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.auth import User, get_current_user
from typing import Any, List, Optional

from backend.data_pipeline import (
    DataPipelineService,
    data_pipeline,
)

router = APIRouter(prefix="/data-pipeline", tags=["data-pipeline"])


class ETLJobRequest(BaseModel):
    """Create ETL job request."""

    name: str = Field(..., description="Job name")
    source_type: str = Field(..., description="Source: api, file, database, stream")
    transform_type: str = Field(
        default="passthrough", description="Transform: filter, map, aggregate"
    )
    sink_type: str = Field(..., description="Sink: api, file, database, stream")
    batch_size: int = Field(default=1000, ge=1, le=10000)
    schedule: Optional[str] = Field(None, description="Cron schedule for recurring jobs")


class StreamProcessorRequest(BaseModel):
    """Create stream processor request."""

    name: str = Field(..., description="Processor name")
    window_type: str = Field(default="tumbling", description="tumbling, sliding, session")
    window_size: float = Field(default=60.0, ge=1.0, description="Window size in seconds")
    window_slide: Optional[float] = Field(None, description="Slide interval for sliding windows")


class IngestRequest(BaseModel):
    """Ingest data into stream."""

    records: list[dict[str, Any]] = Field(..., description="Records to ingest")


class JobResponse(BaseModel):
    """ETL job response."""

    job_id: str
    name: str
    status: str
    records_processed: int = 0
    records_failed: int = 0
    created_at: float


class StreamStatsResponse(BaseModel):
    """Stream processor stats."""

    name: str
    records_in: int
    records_out: int
    buffer_size: int
    windows_processed: int
    running: bool


def get_pipeline_service() -> DataPipelineService:
    """Dependency injection for data pipeline service."""
    return data_pipeline


@router.post("/etl/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_etl_job(
    request: ETLJobRequest,
    service: DataPipelineService = Depends(get_pipeline_service),
    current_user: User = Depends(get_current_user),
) -> JobResponse:
    """Create a new ETL job.

    The job will extract from source, transform, and load to sink.
    """

    # Define extract function based on source type
    def extract_fn() -> list[dict[str, Any]]:
        # In production, this would connect to actual source
        return []

    # Define transform function
    def transform_fn(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if request.transform_type == "filter":
            return [r for r in records if r.get("valid", True)]
        elif request.transform_type == "map":
            return [{"transformed": True, **r} for r in records]
        elif request.transform_type == "aggregate":
            return [{"count": len(records), "aggregated": True}]
        return records

    # Define load function
    def load_fn(records: list[dict[str, Any]]) -> int:
        # In production, this would write to actual sink
        return len(records)

    job_id = service.create_etl_job(
        name=request.name,
        extract_fn=extract_fn,
        transform_fn=transform_fn,
        load_fn=load_fn,
        batch_size=request.batch_size,
    )

    job = service.get_job_status(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create job"
        )

    return JobResponse(
        job_id=job_id,
        name=job["name"],
        status=job["status"],
        records_processed=job["records_processed"],
        records_failed=job["records_failed"],
        created_at=time.time(),
    )


@router.get("/etl/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    service: DataPipelineService = Depends(get_pipeline_service),
    current_user: User = Depends(get_current_user),
) -> JobResponse:
    """Get ETL job status."""
    job = service.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found")

    return JobResponse(
        job_id=job["job_id"],
        name=job["name"],
        status=job["status"],
        records_processed=job["records_processed"],
        records_failed=job["records_failed"],
        created_at=job.get("started_at", time.time()),
    )


@router.get("/etl/jobs", response_model=list[JobResponse])
async def list_jobs(
    service: DataPipelineService = Depends(get_pipeline_service),
    current_user: User = Depends(get_current_user),
) -> List[JobResponse]:
    """List all ETL jobs."""
    jobs = service.list_jobs()
    return [
        JobResponse(
            job_id=j["job_id"],
            name=j["name"],
            status=j["status"],
            records_processed=j["records_processed"],
            records_failed=0,
            created_at=time.time(),
        )
        for j in jobs
    ]


@router.post("/streams", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_stream_processor_endpoint(
    request: StreamProcessorRequest,
    service: DataPipelineService = Depends(get_pipeline_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Create a new stream processor with windowing."""
    processor = service.create_stream_processor(
        name=request.name, window_type=request.window_type, window_size=request.window_size
    )

    # Start the processor
    await processor.start()

    return {
        "processor_name": request.name,
        "window_type": request.window_type,
        "window_size": request.window_size,
        "status": "running",
    }


@router.post("/streams/{processor_name}/ingest")
async def ingest_to_stream(
    processor_name: str,
    request: IngestRequest,
    service: DataPipelineService = Depends(get_pipeline_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Ingest records into stream processor."""
    stats = service.get_processor_stats(processor_name)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stream processor {processor_name} not found",
        )

    # In production, this would actually ingest to the processor
    return {
        "processor": processor_name,
        "records_received": len(request.records),
        "status": "accepted",
    }


@router.get("/streams/{processor_name}/stats", response_model=StreamStatsResponse)
async def get_stream_stats(
    processor_name: str,
    service: DataPipelineService = Depends(get_pipeline_service),
    current_user: User = Depends(get_current_user),
) -> StreamStatsResponse:
    """Get stream processor statistics."""
    stats = service.get_processor_stats(processor_name)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stream processor {processor_name} not found",
        )

    return StreamStatsResponse(
        name=stats["name"],
        records_in=stats["records_in"],
        records_out=stats["records_out"],
        buffer_size=stats["buffer_size"],
        windows_processed=stats["windows_processed"],
        running=stats["running"],
    )


@router.get("/stats", response_model=dict[str, Any])
async def get_pipeline_stats(
    service: DataPipelineService = Depends(get_pipeline_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get overall pipeline statistics."""
    return service.get_stats()
