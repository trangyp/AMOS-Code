from typing import Any

"""AMOS Brain API - Production Cognitive API Endpoints

Real API endpoints that use the brain for cognitive processing.
Integrates with backend/main.py for production use.
"""

import asyncio
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import real brain
from amos_active_brain import analyze_repo_file, get_active_brain, review_code_snippet

router = APIRouter(prefix="/brain-v2", tags=["brain-v2"])


# Request/Response Models
class AnalyzeFileRequest(BaseModel):
    file_path: str


class AnalyzeFileResponse(BaseModel):
    file: str
    analysis: str
    status: str
    brain_mode: str
    processing_time_ms: float


class ReviewCodeRequest(BaseModel):
    code: str
    language: str = "python"
    context: str = ""


class ReviewCodeResponse(BaseModel):
    status: str
    review: str
    verified: bool
    issues_found: int


class BrainStatsResponse(BaseModel):
    total_queries: int
    success_rate: float
    mode_usage: dict[str, int]
    learning_updates: int
    error_memory_size: int


# Global active brain
_brain_initialized = False


async def ensure_brain() -> None:
    """Ensure brain is initialized."""
    global _brain_initialized
    if not _brain_initialized:
        brain = get_active_brain()
        await brain.initialize()
        _brain_initialized = True


@router.post("/analyze-file", response_model=AnalyzeFileResponse)
async def analyze_file(request: AnalyzeFileRequest) -> AnalyzeFileResponse:
    """Analyze a file using cognitive processing.

    Uses deep thinking mode with world model integration.
    """
    await ensure_brain()

    start = time.time()
    result = await analyze_repo_file(request.file_path)
    elapsed = (time.time() - start) * 1000

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return AnalyzeFileResponse(
        file=result["file"],
        analysis=result.get("analysis", ""),
        status=result["status"],
        brain_mode=result.get("brain_mode", "unknown"),
        processing_time_ms=elapsed,
    )


@router.post("/review-code", response_model=ReviewCodeResponse)
async def review_code(request: ReviewCodeRequest) -> ReviewCodeResponse:
    """Review code for issues using safe mode (high verification).

    Detects bugs, security issues, and performance problems.
    """
    await ensure_brain()

    result = await review_code_snippet(request.code, request.language)

    issues_found = 0
    if result["status"] == "reviewed":
        # Count issues in review text
        issues_found = result.get("review", "").lower().count("issue")

    return ReviewCodeResponse(
        status=result["status"],
        review=result.get("review", ""),
        verified=result.get("verified", False),
        issues_found=issues_found,
    )


@router.get("/stats", response_model=BrainStatsResponse)
async def get_stats() -> BrainStatsResponse:
    """Get brain statistics and performance metrics."""
    await ensure_brain()

    brain = get_active_brain()
    stats = brain.get_brain_stats()

    return BrainStatsResponse(
        total_queries=stats["total_queries"],
        success_rate=stats["success_rate"],
        mode_usage=stats["mode_usage"],
        learning_updates=stats["learning_updates"],
        error_memory_size=stats["error_memory_size"],
    )


@router.post("/think")
async def think_endpoint(query: str, mode: str = "auto") -> dict[str, Any]:
    """Direct brain thinking endpoint.

    Args:
        query: The query to process
        mode: Thinking mode (fast/deep/safe/auto)

    Returns:
        Response with cognitive result
    """
    await ensure_brain()

    brain = get_active_brain()

    if mode == "fast":
        result = await brain.brain.think_fast(query)
    elif mode == "deep":
        result = await brain.brain.think_deep(query)
    elif mode == "safe":
        result = await brain.brain.think_safe(query)
    else:
        # Auto mode - let brain decide
        from amos_real_brain_integration import CognitiveRequest

        req = CognitiveRequest(query=query, mode="auto", importance=0.7)
        result = await brain.brain.think(req)
        return {
            "response": result.response,
            "mode": result.cognitive_mode,
            "confidence": result.confidence,
            "verified": result.was_verified,
        }

    return {"response": result, "mode": mode, "confidence": 0.7 if mode == "fast" else 0.9}


# Self-testing
def test_brain_api() -> bool:
    """Test the brain API endpoints."""
    print("=" * 60)
    print("TESTING BRAIN API")
    print("=" * 60)

    async def run_tests() -> bool:
        # Test 1: Stats endpoint
        print("\n[1] Testing stats endpoint...")
        stats = await get_stats()
        print(f"    Total queries: {stats.total_queries}")
        print(f"    Success rate: {stats.success_rate:.1%}")
        assert stats.total_queries >= 0

        # Test 2: Code review
        print("\n[2] Testing code review...")
        code = "def foo():\n    return eval('1+1')"  # Security issue
        result = await review_code(ReviewCodeRequest(code=code))
        print(f"    Status: {result.status}")
        print(f"    Issues found: {result.issues_found}")
        assert result.status in ["reviewed", "verification_failed"]

        # Test 3: Think endpoint
        print("\n[3] Testing think endpoint...")
        response = await think_endpoint("Hello world", mode="fast")
        print(f"    Response received: {len(str(response))} chars")
        assert "response" in response

        return True

    try:
        success = asyncio.run(run_tests())
        print("\n" + "=" * 60)
        print("BRAIN API TESTS PASSED")
        print("=" * 60)
        return success
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_brain_api()
