"""Brain Active Processor API - Real AMOS Brain Cognitive Work.

This module ACTUALLY uses the AMOS brain to perform real cognitive tasks:
- File analysis with deep thinking
- Code review with verification
- Refactoring suggestions
- Architecture analysis
- Bug detection

Integrates directly with amos_active_brain for real brain processing.
"""


import asyncio
import sys
from collections.abc import AsyncIterator
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "clawspring", AMOS_ROOT / "amos_brain"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Import real brain

from amos_active_brain import get_active_brain

router = APIRouter(prefix="/api/v1/brain/active", tags=["Brain Active Processor"])


class FileAnalysisRequest(BaseModel):
    """Request to analyze a file."""

    file_path: str = Field(..., min_length=1, description="Path to file to analyze")
    context: Dict[str, Any] = Field(default_factory=dict)


class FileAnalysisResponse(BaseModel):
    """Response from file analysis."""

    file: str
    analysis: str
    brain_mode: str
    status: str
    processing_time_ms: float
    timestamp: datetime


class CodeReviewRequest(BaseModel):
    """Request for code review."""

    code: str = Field(..., min_length=10, description="Code to review")
    language: str = Field(default="python", description="Programming language")
    context: str = Field(default="", description="Additional context")


class CodeReviewResponse(BaseModel):
    """Response from code review."""

    status: str
    review: str
    verified: bool
    issues_found: int
    risk_level: float
    timestamp: datetime


class RefactoringRequest(BaseModel):
    """Request for refactoring suggestions."""

    code: str = Field(..., min_length=10, description="Code to refactor")
    goal: str = Field(default="improve readability", description="Refactoring goal")


class RefactoringResponse(BaseModel):
    """Response from refactoring analysis."""

    status: str
    suggestions: str
    cognitive_steps: int
    tools_used: List[str]
    timestamp: datetime


class BatchAnalysisRequest(BaseModel):
    """Request to analyze multiple files."""

    file_paths: List[str] = Field(..., min_length=1, max_length=20)
    analysis_type: str = Field(default="general", description="Type of analysis")


class BatchAnalysisResponse(BaseModel):
    """Response from batch analysis."""

    files_analyzed: int
    results: List[dict[str, Any]]
    architecture_issues: List[dict[str, Any]]
    summary: str
    timestamp: datetime


class ActiveBrainEngine:
    """Engine that ACTUALLY uses the AMOS brain."""

    def __init__(self) -> None:
        self._brain = None
        self._lock = asyncio.Lock()

    async def _get_brain(self) -> Any:
        """Get initialized brain."""
        if self._brain is None:
            self._brain = get_active_brain()
            await self._brain.initialize()
        return self._brain

    async def analyze_file(self, file_path: str, context: Dict[str, Any]) -> FileAnalysisResponse:
        """Analyze a file using REAL brain cognitive processing."""
        start_time = datetime.now(UTC)

        # Get brain
        brain = await self._get_brain()

        # Convert to Path
        path = Path(file_path)

        # REAL brain analysis
        result = await brain.analyze_file(path)

        end_time = datetime.now(UTC)
        processing_time = (end_time - start_time).total_seconds() * 1000

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return FileAnalysisResponse(
            file=result["file"],
            analysis=result.get("analysis", ""),
            brain_mode=result.get("brain_mode", "unknown"),
            status=result.get("status", "unknown"),
            processing_time_ms=processing_time,
            timestamp=end_time,
        )

    async def review_code(self, code: str, language: str, context: str) -> CodeReviewResponse:
        """Review code using REAL brain verification."""
        # Get brain
        brain = await self._get_brain()

        # REAL brain code review
        result = await brain.review_code(code, context=f"Language: {language}\n{context}")

        # Count issues
        issues_found = 0
        if result["status"] == "reviewed":
            review_text = result.get("review", "").lower()
            issues_found = (
                review_text.count("issue")
                + review_text.count("bug")
                + review_text.count("error")
                + review_text.count("warning")
                + review_text.count("vulnerability")
            )

        return CodeReviewResponse(
            status=result["status"],
            review=result.get("review", ""),
            verified=result.get("verified", False),
            issues_found=issues_found,
            risk_level=0.7 if result["status"] == "verification_failed" else 0.3,
            timestamp=datetime.now(UTC),
        )

    async def suggest_refactoring(self, code: str, goal: str) -> RefactoringResponse:
        """Get refactoring suggestions using REAL brain planning."""
        # Get brain
        brain = await self._get_brain()

        # REAL brain refactoring suggestions
        result = await brain.suggest_refactoring(code, goal)

        return RefactoringResponse(
            status=result["status"],
            suggestions=result.get("suggestions", ""),
            cognitive_steps=result.get("cognitive_steps", 0),
            tools_used=result.get("tools_used", []),
            timestamp=datetime.now(UTC),
        )

    async def analyze_batch(
        self, file_paths: List[str], analysis_type: str
    ) -> BatchAnalysisResponse:
        """Analyze multiple files using REAL brain architecture detection."""
        # Get brain
        brain = await self._get_brain()

        # Convert paths
        paths = [Path(fp) for fp in file_paths]

        # Analyze each file
        results = []
        for path in paths:
            if path.exists():
                result = await brain.analyze_file(path)
                results.append(result)

        # REAL architecture issue detection
        arch_result = await brain.detect_architecture_issues(paths)

        # Generate summary
        analyzed_count = len([r for r in results if r.get("status") == "analyzed"])
        summary = f"Analyzed {analyzed_count} of {len(file_paths)} files. "
        summary += f"Architecture issues detected in {len(arch_result.get('architecture_analysis', []))} areas."

        return BatchAnalysisResponse(
            files_analyzed=analyzed_count,
            results=results,
            architecture_issues=arch_result.get("architecture_analysis", []),
            summary=summary,
            timestamp=datetime.now(UTC),
        )

    async def stream_analysis(self, file_path: str) -> AsyncIterator[dict[str, Any]]:
        """Stream real-time brain analysis progress."""
        yield {
            "stage": "init",
            "message": "Initializing brain...",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Get brain
        brain = await self._get_brain()

        yield {
            "stage": "brain_ready",
            "message": "Brain initialized and ready",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Start analysis
        yield {
            "stage": "analyzing",
            "message": f"Analyzing file: {file_path}",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # REAL analysis
        path = Path(file_path)
        if path.exists():
            result = await brain.analyze_file(path)

            yield {
                "stage": "complete",
                "message": "Analysis complete",
                "file": result.get("file"),
                "brain_mode": result.get("brain_mode"),
                "status": result.get("status"),
                "preview": result.get("analysis", "")[:200],
                "timestamp": datetime.now(UTC).isoformat(),
            }
        else:
            yield {
                "stage": "error",
                "message": f"File not found: {file_path}",
                "timestamp": datetime.now(UTC).isoformat(),
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get brain usage statistics."""
        if self._brain:
            return self._brain.get_brain_stats()
        return {"error": "Brain not initialized"}


# Global engine
_active_engine: Optional[ActiveBrainEngine] = None


def get_active_engine() -> ActiveBrainEngine:
    """Get or create active brain engine."""
    global _active_engine
    if _active_engine is None:
        _active_engine = ActiveBrainEngine()
    return _active_engine


@router.post("/analyze-file", response_model=FileAnalysisResponse)
async def analyze_file(request: FileAnalysisRequest) -> FileAnalysisResponse:
    """Analyze a file using REAL AMOS brain cognitive processing.

    This endpoint actually uses the brain to think deeply about code.
    """
    engine = get_active_engine()
    return await engine.analyze_file(request.file_path, request.context)


@router.post("/review-code", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest) -> CodeReviewResponse:
    """Review code using REAL AMOS brain verification.

    Uses safe mode with high verification for security-critical analysis.
    """
    engine = get_active_engine()
    return await engine.review_code(request.code, request.language, request.context)


@router.post("/suggest-refactoring", response_model=RefactoringResponse)
async def suggest_refactoring(request: RefactoringRequest) -> RefactoringResponse:
    """Get refactoring suggestions using REAL brain planning.

    Uses cognitive loop with tool-augmented reasoning.
    """
    engine = get_active_engine()
    return await engine.suggest_refactoring(request.code, request.goal)


@router.post("/analyze-batch", response_model=BatchAnalysisResponse)
async def analyze_batch(request: BatchAnalysisRequest) -> BatchAnalysisResponse:
    """Analyze multiple files using REAL brain architecture detection.

    Detects cross-file issues and architecture problems.
    """
    engine = get_active_engine()
    return await engine.analyze_batch(request.file_paths, request.analysis_type)


@router.get("/analyze-stream")
async def stream_file_analysis(
    file_path: str = Query(..., description="Path to file to analyze"),
) -> StreamingResponse:
    """Stream real-time brain analysis progress via SSE.

    Shows brain initialization, thinking stages, and results.
    """
    engine = get_active_engine()

    async def event_generator():
        async for update in engine.stream_analysis(file_path):
            yield f"data: {update}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/stats")
async def get_brain_stats() -> Dict[str, Any]:
    """Get REAL brain usage statistics.

    Returns actual metrics from the active brain.
    """
    engine = get_active_engine()
    return engine.get_stats()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Check if brain is active and operational."""
    try:
        engine = get_active_engine()
        stats = engine.get_stats()

        return {
            "status": "healthy" if "error" not in stats else "degraded",
            "brain_active": "error" not in stats,
            "total_queries": stats.get("total_queries", 0),
            "success_rate": stats.get("success_rate", 0.0),
            "learning_updates": stats.get("learning_updates", 0),
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "brain_active": False,
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }
