from typing import Any

"""AMOS Cognitive File Processor API

Production REST endpoints for streaming cognitive file processing.
Real-time file analysis with brain-powered cognition.

Owner: Trang Phan
"""
from __future__ import annotations


from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

try:
    from amos_cognitive_file_processor import (
        CognitiveDocument,
        CognitiveFileProcessor,
        get_cognitive_processor,
        process_file_cognitively,
    )

    COGNITIVE_AVAILABLE = True
except ImportError:
    COGNITIVE_AVAILABLE = False

router = APIRouter(prefix="/api/v1/cognitive", tags=["Cognitive Processor"])


class CognitiveProcessRequest(BaseModel):
    """Request for cognitive file processing."""

    content: str
    source: str | None = None
    context: dict[str, Any] = {}
    max_concurrent: int = 5
    enable_brain: bool = True


class CognitiveProcessResponse(BaseModel):
    """Response with cognitively processed document."""

    doc_id: str
    source_path: str | None
    state: str
    total_segments: int
    processed_chunks: int
    failed_chunks: int
    brain_enhanced: bool
    total_processing_time_ms: float
    cognitive_summary: dict[str, Any]
    errors: list[str]
    chunks: list[dict[str, Any]]


class CognitiveStatusResponse(BaseModel):
    """Cognitive processor status."""

    available: bool
    brain_available: bool
    reading_available: bool
    max_concurrent: int


@router.post("/process", response_model=CognitiveProcessResponse)
async def process_cognitive_endpoint(
    background_tasks: BackgroundTasks,
    content: str = Form(...),
    source: str | None = Form(None),
    context: str = Form("{}"),
    max_concurrent: int = Form(5),
    enable_brain: bool = Form(True),
) -> CognitiveProcessResponse:
    """Process file content through cognitive pipeline.

    Streams file through ingestion → cognitive analysis → brain summary.
    Returns structured cognitive analysis with confidence scores.
    """
    if not COGNITIVE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cognitive processor not available")

    import json

    try:
        ctx = json.loads(context) if context else {}
    except json.JSONDecodeError:
        ctx = {}

    # Process through cognitive pipeline
    result = await process_file_cognitively(
        content=content.encode(),
        source=source,
        context=ctx,
        max_concurrent=max_concurrent,
        enable_brain=enable_brain,
    )

    return CognitiveProcessResponse(
        doc_id=result.doc_id,
        source_path=result.source_path,
        state=result.state.name,
        total_segments=result.total_segments,
        processed_chunks=result.processed_chunks,
        failed_chunks=result.failed_chunks,
        brain_enhanced=result.brain_enhanced,
        total_processing_time_ms=result.total_processing_time_ms,
        cognitive_summary=result.cognitive_summary,
        errors=result.errors,
        chunks=[
            {
                "chunk_id": c.chunk_id,
                "segment_id": c.segment_id,
                "content_preview": c.content[:100] + "..." if len(c.content) > 100 else c.content,
                "confidence": c.confidence,
                "read_type": c.read_type,
                "processing_time_ms": c.processing_time_ms,
            }
            for c in result.chunks
        ],
    )


@router.post("/upload", response_model=CognitiveProcessResponse)
async def upload_cognitive_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    context: str = Form("{}"),
    max_concurrent: int = Form(5),
    enable_brain: bool = Form(True),
) -> CognitiveProcessResponse:
    """Upload and process file through cognitive pipeline.

    Accepts file upload, processes through cognitive analysis.
    """
    if not COGNITIVE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cognitive processor not available")

    try:
        ctx = json.loads(context) if context else {}
    except json.JSONDecodeError:
        ctx = {}

    # Read uploaded file
    content = await file.read()

    # Process through cognitive pipeline
    result = await process_file_cognitively(
        content=content,
        source=file.filename,
        context=ctx,
        max_concurrent=max_concurrent,
        enable_brain=enable_brain,
    )

    return CognitiveProcessResponse(
        doc_id=result.doc_id,
        source_path=result.source_path,
        state=result.state.name,
        total_segments=result.total_segments,
        processed_chunks=result.processed_chunks,
        failed_chunks=result.failed_chunks,
        brain_enhanced=result.brain_enhanced,
        total_processing_time_ms=result.total_processing_time_ms,
        cognitive_summary=result.cognitive_summary,
        errors=result.errors,
        chunks=[
            {
                "chunk_id": c.chunk_id,
                "segment_id": c.segment_id,
                "content_preview": c.content[:100] + "..." if len(c.content) > 100 else c.content,
                "confidence": c.confidence,
                "read_type": c.read_type,
                "processing_time_ms": c.processing_time_ms,
            }
            for c in result.chunks
        ],
    )


@router.get("/status", response_model=CognitiveStatusResponse)
async def get_cognitive_status() -> CognitiveStatusResponse:
    """Get cognitive processor service status."""
    if not COGNITIVE_AVAILABLE:
        return CognitiveStatusResponse(
            available=False, brain_available=False, reading_available=False, max_concurrent=0
        )

    # Check component availability
    try:
        from amos_cognitive_file_processor import BRAIN_AVAILABLE, READING_AVAILABLE

        return CognitiveStatusResponse(
            available=True,
            brain_available=BRAIN_AVAILABLE,
            reading_available=READING_AVAILABLE,
            max_concurrent=5,
        )
    except Exception:
        return CognitiveStatusResponse(
            available=True, brain_available=False, reading_available=False, max_concurrent=5
        )


@router.post("/analyze-text")
async def analyze_text_endpoint(text: str = Form(...)) -> dict[str, Any]:
    """Quick cognitive analysis of text without full file processing."""
    if not COGNITIVE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cognitive processor not available")

    try:
        from amos_reading_kernel import read_text

        result = await read_text(
            raw_text=text, dialogue_context={}, memory_context={}, world_context={}
        )

        if result:
            return {
                "status": "success",
                "read_type": getattr(result.read_type, "value", str(result.read_type))
                if hasattr(result, "read_type")
                else None,
                "confidence": getattr(result, "confidence", 0.0),
                "primary_signal": getattr(result, "primary_signal", None),
                "noise_score": getattr(result, "noise_score", 0.0),
                "has_stable_read": True,
            }
        else:
            return {"status": "no_result", "has_stable_read": False}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
