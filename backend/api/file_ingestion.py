"""File Ingestion API - Streaming document processing endpoints."""

import logging
import re
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Add paths
_AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT))

from amos_file_ingestion_runtime import (
    DocumentIngestionRuntime,
    FileFormat,
    TaskType,
)

router = APIRouter(prefix="/files", tags=["file-ingestion"])


class FileIngestRequest(BaseModel):
    task: str
    file_path: str
    task_type: str = "simple_lookup"


class FileIngestResponse(BaseModel):
    success: bool
    answer: str
    format_detected: str
    chunks_scanned: int
    deep_read_triggered: bool
    time_ms: float


def _validate_file_path(file_path: str) -> Path:
    """Validate file path to prevent path traversal attacks.

    Args:
        file_path: The requested file path

    Returns:
        Validated Path object

    Raises:
        HTTPException: If path is invalid or outside allowed directories
    """
    # Normalize the path
    path = Path(file_path).resolve()

    # Define allowed directories
    allowed_dirs = [
        Path("/tmp").resolve(),
        Path("/data").resolve(),
        Path.home().resolve() / "Documents",
    ]

    # Check for path traversal attempts
    if any(part.startswith(".") for part in path.parts):
        logger.warning("path_traversal_attempt_detected", file_path=file_path)
        raise HTTPException(status_code=400, detail="Invalid file path")

    # Check if path is within allowed directories
    if not any(str(path).startswith(str(allowed)) for allowed in allowed_dirs):
        logger.warning("file_path_outside_allowed_dirs", file_path=str(path))
        raise HTTPException(status_code=400, detail="File path not in allowed directories")

    return path


@router.post("/ingest", response_model=FileIngestResponse)
async def file_ingest_endpoint(request: FileIngestRequest) -> FileIngestResponse:
    """
    Ingest and query file with streaming processing.

    Pipeline: Open → DetectFormat → BuildQuickIndex → RouteTask →
              FastRetrieve → DeepReadIfNeeded → CacheParsedState
    """
    try:
        # Validate file path for security
        validated_path = _validate_file_path(request.file_path)

        runtime = DocumentIngestionRuntime()
        result = await runtime.ingest_and_query(
            file_path=str(validated_path),
            task=request.task,
            task_type=TaskType[request.task_type.upper()],
        )

        return FileIngestResponse(
            success=result.get("success", False),
            answer=result.get("answer", ""),
            format_detected=result.get("format_detected", "unknown"),
            chunks_scanned=result.get("chunks_scanned", 0),
            deep_read_triggered=result.get("deep_read_triggered", False),
            time_ms=result.get("time_ms", 0.0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def file_upload_endpoint(
    file: UploadFile = File(...), task: str = "summarize"
) -> dict[str, Any]:
    """Upload and process file immediately with streaming for large files."""
    try:
        # Sanitize filename to prevent path traversal
        safe_filename = re.sub(r"[^\w\-\.]", "_", file.filename)
        if not safe_filename or safe_filename.startswith("."):
            raise HTTPException(status_code=400, detail="Invalid filename")

        # Max upload size: 100MB
        max_upload_size = 100 * 1024 * 1024
        temp_path = Path(f"/tmp/amos_upload_{safe_filename}")

        # Stream write to temp file to avoid loading entire file into memory
        total_size = 0
        chunk_size = 64 * 1024  # 64KB chunks

        with open(temp_path, "wb") as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > max_upload_size:
                    temp_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="File too large (max 100MB)")
                f.write(chunk)

        logger.info("file_uploaded", filename=safe_filename, size=total_size)

        # Process
        runtime = DocumentIngestionRuntime()
        result = await runtime.ingest_and_query(
            file_path=str(temp_path),
            task=task,
            task_type=TaskType.SIMPLE_LOOKUP,
        )

        # Cleanup
        temp_path.unlink(missing_ok=True)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formats")
async def file_formats() -> dict[str, list[str]]:
    """Get supported file formats."""
    return {
        "formats": [f.name for f in FileFormat],
        "task_types": [t.name for t in TaskType],
    }
