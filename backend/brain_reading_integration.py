from __future__ import annotations

from typing import Any, Optional

"""AMOS Brain Reading Kernel Integration

Connects the AMOS Reading Kernel to the FastAPI backend for
cognitive text processing and stable read generation.

Owner: Trang Phan
Version: 1.0.0
"""


import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import reading kernel
try:
    from amos_reading_kernel import (
        AMOSReadingKernel,
        StableRead,
        get_reading_kernel,
        read_text,
    )

    READING_KERNEL_AVAILABLE = True
except ImportError:
    READING_KERNEL_AVAILABLE = False

# Import brain components
try:
    from amos_brain import get_super_brain

    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False

# Import event streaming
try:
    from backend.event_stream import emit_event

    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/reading", tags=["Reading Kernel"])


class ReadRequest(BaseModel):
    """Request to process text through reading kernel."""

    text: str
    context: dict[str, Any] = {}
    memory_context: dict[str, Any] = {}
    world_context: dict[str, Any] = {}


class ReadResponse(BaseModel):
    """Response with stable read result."""

    status: str
    stable_read: dict[str, Any] = None
    processing_time_ms: float = 0.0
    error: Optional[str] = None


class ReadingKernelService:
    """Service wrapper for AMOS Reading Kernel."""

    def __init__(self):
        self._kernel: Optional[AMOSReadingKernel] = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the reading kernel."""
        if not READING_KERNEL_AVAILABLE:
            logger.error("Reading kernel not available")
            return False

        try:
            self._kernel = get_reading_kernel()
            self._initialized = True
            logger.info("Reading kernel initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize reading kernel: {e}")
            return False

    async def process_text(
        self,
        text: str,
        context: dict[str, Any] = None,
        memory_context: dict[str, Any] = None,
        world_context: dict[str, Any] = None,
    ) -> tuple[Optional[StableRead], float]:
        """Process text through reading pipeline.

        Returns:
            Tuple of (stable_read, processing_time_ms)
        """
        if not self._initialized or not self._kernel:
            return None, 0.0

        import time

        start = time.time()

        try:
            stable_read = await read_text(
                text=text,
                dialogue_context=context or {},
                memory_context=memory_context or {},
                world_context=world_context or {},
            )

            elapsed = (time.time() - start) * 1000

            # Emit event if streaming available
            if STREAMING_AVAILABLE:
                emit_event(
                    "reading.completed",
                    {
                        "text_preview": text[:50] if text else "",
                        "read_type": stable_read.read_type if stable_read else None,
                        "confidence": stable_read.confidence if stable_read else 0.0,
                        "processing_time_ms": elapsed,
                    },
                    "reading_kernel",
                )

            return stable_read, elapsed

        except Exception as e:
            logger.error(f"Reading processing failed: {e}")
            elapsed = (time.time() - start) * 1000
            return None, elapsed

    def get_status(self) -> dict[str, Any]:
        """Get kernel status."""
        return {
            "initialized": self._initialized,
            "kernel_available": READING_KERNEL_AVAILABLE,
            "brain_available": BRAIN_AVAILABLE,
        }


# Global service instance
_reading_service: Optional[ReadingKernelService] = None


async def get_reading_service() -> ReadingKernelService:
    """Get or create reading service."""
    global _reading_service
    if _reading_service is None:
        _reading_service = ReadingKernelService()
        await _reading_service.initialize()
    return _reading_service


@router.post("/process", response_model=ReadResponse)
async def process_read_request(request: ReadRequest) -> ReadResponse:
    """Process text through AMOS Reading Kernel.

    This endpoint takes raw text and produces a StableRead object
    that can be safely consumed by downstream AMOS components.
    """
    if not READING_KERNEL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Reading kernel not available")

    service = await get_reading_service()
    stable_read, elapsed = await service.process_text(
        text=request.text,
        context=request.context,
        memory_context=request.memory_context,
        world_context=request.world_context,
    )

    if stable_read is None:
        return ReadResponse(
            status="failed", error="Failed to produce stable read", processing_time_ms=elapsed
        )

    return ReadResponse(
        status="success", stable_read=stable_read.to_dict(), processing_time_ms=elapsed
    )


@router.get("/status")
async def get_kernel_status() -> dict[str, Any]:
    """Get reading kernel status."""
    service = await get_reading_service()
    return service.get_status()


@router.post("/reset")
async def reset_kernel() -> dict[str, str]:
    """Reset reading kernel state."""
    global _reading_service
    _reading_service = None
    return {"status": "reset"}


# Export bridge interface for consistency with other integrations
def get_reading_bridge() -> ReadingKernelService:
    """Get reading bridge (alias for get_reading_service).

    This provides API consistency with other brain integrations
    like real_orchestrator_bridge.get_real_orchestrator_bridge().
    """
    global _reading_service
    if _reading_service is None:
        _reading_service = ReadingKernelService()
    return _reading_service
