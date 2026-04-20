from __future__ import annotations

from typing import Any, Optional

"""AMOS File Brain API

Real REST endpoints for file ingestion with brain-powered analysis.
Integrates streaming file ingestion with cognitive reading kernel.
"""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

try:
    from amos_file_brain_integration import (
        get_file_brain_processor,
        process_file_with_brain,
        query_file_with_brain,
    )
    from amos_file_ingestion_runtime import get_ingestion_runtime

    FILE_BRAIN_AVAILABLE = True
except ImportError:
    FILE_BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/file-brain", tags=["File Brain"])


class FileProcessRequest(BaseModel):
    """Request to process file content."""

    content: str
    source: Optional[str] = None
    context: dict[str, Any] = {}


class FileProcessResponse(BaseModel):
    """Response with brain-processed file."""

    file_id: str
    source: Optional[str]
    total_segments: int
    processed_segments: int
    stable_reads: list[dict[str, Any]]
    cognitive_summary: dict[str, Any]
    processing_time_ms: float
    errors: list[str]


class FileQueryRequest(BaseModel):
    """Query against processed file."""

    file_id: str
    query: str
    use_cognitive: bool = True


class FileQueryResponse(BaseModel):
    """Response to file query."""

    file_id: str
    query: str
    path: str
    context: Optional[str]
    latency_ms: float
    brain_enhancement: dict[str, Any] = None


@router.post("/process", response_model=FileProcessResponse)
async def process_file_endpoint(
    content: str = Form(...), source: Optional[str] = Form(None), context: str = Form("{}")
) -> FileProcessResponse:
    """Process file content through brain pipeline.

    Takes file content (text), ingests it, segments it,
    and processes each segment through the brain reading kernel.
    """
    if not FILE_BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="File brain not available")

    import json

    try:
        ctx = json.loads(context) if context else {}
    except json.JSONDecodeError:
        ctx = {}

    # Process through file-brain pipeline
    result = await process_file_with_brain(content=content.encode(), source=source, context=ctx)

    return FileProcessResponse(
        file_id=result.file_id,
        source=result.source_path,
        total_segments=result.total_segments,
        processed_segments=result.processed_segments,
        stable_reads=result.stable_reads,
        cognitive_summary=result.cognitive_summary,
        processing_time_ms=result.processing_time_ms,
        errors=result.errors,
    )


@router.post("/upload", response_model=FileProcessResponse)
async def upload_file_endpoint(
    file: UploadFile = File(...), context: str = Form("{}")
) -> FileProcessResponse:
    """Upload and process file through brain pipeline.

    Accepts file upload, reads content, processes through brain.
    """
    if not FILE_BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="File brain not available")

    try:
        ctx = json.loads(context) if context else {}
    except json.JSONDecodeError:
        ctx = {}

    # Read uploaded file
    content = await file.read()

    # Process through file-brain pipeline
    result = await process_file_with_brain(content=content, source=file.filename, context=ctx)

    return FileProcessResponse(
        file_id=result.file_id,
        source=result.source_path,
        total_segments=result.total_segments,
        processed_segments=result.processed_segments,
        stable_reads=result.stable_reads,
        cognitive_summary=result.cognitive_summary,
        processing_time_ms=result.processing_time_ms,
        errors=result.errors,
    )


@router.post("/query", response_model=FileQueryResponse)
async def query_file_endpoint(request: FileQueryRequest) -> FileQueryResponse:
    """Query a previously processed file.

    Uses cognitive search to find relevant segments and
    optionally enhances with brain analysis.
    """
    if not FILE_BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="File brain not available")

    # Get runtime and find cached document
    runtime = get_ingestion_runtime()

    # Find document in cache by ID
    doc = None
    for key, cached_doc in runtime.cache._cache.items():
        if cached_doc.doc_id == request.file_id:
            doc = cached_doc
            break

    if doc is None:
        raise HTTPException(
            status_code=404, detail=f"File {request.file_id} not found in cache. Process it first."
        )

    # Query the file
    result = await query_file_with_brain(doc=doc, query=request.query)

    return FileQueryResponse(
        file_id=request.file_id,
        query=request.query,
        path=result.get("path", "unknown"),
        context=result.get("context"),
        latency_ms=result.get("latency_ms", 0.0),
        brain_enhancement=result.get("brain_enhancement"),
    )


@router.get("/status")
async def get_file_brain_status() -> dict[str, Any]:
    """Get file brain service status."""
    if not FILE_BRAIN_AVAILABLE:
        return {
            "available": False,
            "file_brain": False,
            "ingestion_runtime": False,
            "cache_size": 0,
        }

    runtime = get_ingestion_runtime()

    return {
        "available": True,
        "file_brain": True,
        "ingestion_runtime": True,
        "cache_size": len(runtime.cache._cache),
        "max_cache_size": runtime.cache.max_size,
    }
