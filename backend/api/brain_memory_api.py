"""Brain Memory API - AMOS brain-powered memory management system.

Provides API endpoints for brain memory operations:
- Save reasoning results with full metadata
- Query memory by topic, tags, or similarity
- Recall relevant past analyses
- Memory statistics and health monitoring
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

UTC = timezone.utc

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "amos_brain"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Import brain memory
try:
    from memory import BrainMemory

    _MEMORY_AVAILABLE = True
except ImportError:
    _MEMORY_AVAILABLE = False
    BrainMemory = None

router = APIRouter(prefix="/api/v1/brain/memory", tags=["Brain Memory"])


class MemoryEntry(BaseModel):
    """Memory entry model."""

    id: str
    problem_fingerprint: str
    timestamp: datetime
    namespace: str = "amos_brain"
    problem: str
    problem_preview: str
    analysis_summary: dict[str, Any]
    tags: list[str] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    structural_integrity_score: float = 0.0
    rule_of_two_applied: bool = False
    rule_of_four_applied: bool = False


class SaveReasoningRequest(BaseModel):
    """Request to save reasoning to memory."""

    problem: str = Field(..., min_length=1, max_length=5000)
    analysis: dict[str, Any] = Field(..., description="Full analysis result")
    tags: list[str] = Field(default_factory=list, description="Categorization tags")


class SaveReasoningResponse(BaseModel):
    """Response after saving reasoning."""

    entry_id: str
    fingerprint: str
    timestamp: datetime
    memory_path: Optional[str] = None
    clawspring_saved: bool = False


class MemoryQueryRequest(BaseModel):
    """Request to query memory."""

    query: str = Field(..., min_length=1, description="Search query")
    tags: list[str] = Field(default_factory=list, description="Filter by tags")
    limit: int = Field(default=10, ge=1, le=100)
    min_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class MemoryQueryResult(BaseModel):
    """Single memory query result."""

    entry: MemoryEntry
    relevance_score: float = Field(ge=0.0, le=1.0)
    matched_tags: list[str] = Field(default_factory=list)


class MemoryStats(BaseModel):
    """Memory system statistics."""

    total_entries: int
    entries_by_tag: dict[str, int]
    average_confidence: float
    rule_of_two_count: int
    rule_of_four_count: int
    memory_size_bytes: int
    last_entry_timestamp: Optional[datetime] = None


class BrainMemoryManager:
    """Manager for brain memory operations."""

    def __init__(self) -> None:
        self._memory: Optional[BrainMemory] = None
        self._lock = asyncio.Lock()

    def _get_memory(self) -> BrainMemory:
        """Get or initialize brain memory."""
        if not _MEMORY_AVAILABLE:
            raise HTTPException(status_code=503, detail="Brain memory module not available")
        if self._memory is None:
            self._memory = BrainMemory()
        return self._memory

    async def save_reasoning(
        self, problem: str, analysis: dict[str, Any], tags: list[str]
    ) -> SaveReasoningResponse:
        """Save reasoning result to memory."""
        async with self._lock:
            memory = self._get_memory()

            # Save to memory
            entry_id = memory.save_reasoning(problem, analysis, tags)

            # Calculate fingerprint
            fingerprint = memory._hash_problem(problem)

            return SaveReasoningResponse(
                entry_id=entry_id,
                fingerprint=fingerprint,
                timestamp=datetime.now(UTC),
                memory_path=str(memory.memory_dir) if hasattr(memory, "memory_dir") else None,
                clawspring_saved=_MEMORY_AVAILABLE and hasattr(memory, "MEMORY_NAMESPACE"),
            )

    async def query_memory(
        self, query: str, tags: list[str], limit: int, min_confidence: float
    ) -> list[MemoryQueryResult]:
        """Query memory for relevant entries."""
        async with self._lock:
            memory = self._get_memory()

            results: list[MemoryQueryResult] = []

            # Get all entries and filter
            all_entries = memory._local_cache.values() if hasattr(memory, "_local_cache") else []

            for entry in all_entries:
                # Calculate relevance
                relevance = self._calculate_relevance(entry, query, tags)

                # Check confidence threshold
                confidence = entry.get("confidence_score", 0.0) or 0.0
                if confidence < min_confidence:
                    continue

                # Find matched tags
                entry_tags = set(entry.get("tags", []))
                matched = list(entry_tags & set(tags)) if tags else []

                if relevance > 0 or matched:
                    # Convert to MemoryEntry
                    mem_entry = MemoryEntry(
                        id=entry.get("id", ""),
                        problem_fingerprint=entry.get("problem_fingerprint", ""),
                        timestamp=datetime.fromisoformat(
                            entry.get("timestamp", datetime.now(UTC).isoformat())
                        ),
                        problem=entry.get("problem", ""),
                        problem_preview=entry.get("problem_preview", ""),
                        analysis_summary=entry.get("analysis_summary", {}),
                        tags=list(entry_tags),
                        confidence_score=confidence,
                        structural_integrity_score=entry.get("structural_integrity_score", 0.0),
                        rule_of_two_applied=entry.get("rule_of_two_applied", False),
                        rule_of_four_applied=entry.get("rule_of_four_applied", False),
                    )

                    results.append(
                        MemoryQueryResult(
                            entry=mem_entry, relevance_score=relevance, matched_tags=matched
                        )
                    )

            # Sort by relevance and limit
            results.sort(key=lambda r: r.relevance_score, reverse=True)
            return results[:limit]

    def _calculate_relevance(
        self, entry: dict[str, Any], query: str, filter_tags: list[str]
    ) -> float:
        """Calculate relevance score for an entry."""
        score = 0.0
        query_lower = query.lower()

        # Check problem match
        problem = entry.get("problem", "").lower()
        if query_lower in problem:
            score += 0.5

        # Check tags match
        entry_tags = set(entry.get("tags", []))
        if filter_tags:
            matching = len(entry_tags & set(filter_tags))
            score += 0.3 * (matching / len(filter_tags))

        # Boost by confidence
        confidence = entry.get("confidence_score", 0.0) or 0.0
        score += 0.2 * confidence

        return min(score, 1.0)

    async def recall_similar(self, problem: str, limit: int = 5) -> list[MemoryEntry]:
        """Recall similar past analyses."""
        async with self._lock:
            memory = self._get_memory()

            if hasattr(memory, "recall_similar"):
                # Use native recall if available
                results = memory.recall_similar(problem, limit)
            else:
                # Query using fingerprint similarity
                fingerprint = (
                    memory._hash_problem(problem) if hasattr(memory, "_hash_problem") else ""
                )
                query_results = await self.query_memory(
                    query=problem, tags=[], limit=limit, min_confidence=0.0
                )
                results = [r.entry for r in query_results]

            return results[:limit]

    async def get_stats(self) -> MemoryStats:
        """Get memory statistics."""
        async with self._lock:
            memory = self._get_memory()

            entries = list(memory._local_cache.values()) if hasattr(memory, "_local_cache") else []

            # Count by tag
            tag_counts: dict[str, int] = {}
            for entry in entries:
                for tag in entry.get("tags", []):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Calculate average confidence
            confidences = [e.get("confidence_score", 0.0) or 0.0 for e in entries]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # Count rules applied
            rule_two_count = sum(1 for e in entries if e.get("rule_of_two_applied", False))
            rule_four_count = sum(1 for e in entries if e.get("rule_of_four_applied", False))

            # Get last entry timestamp
            timestamps = [
                datetime.fromisoformat(e.get("timestamp", ""))
                for e in entries
                if e.get("timestamp")
            ]
            last_timestamp = max(timestamps) if timestamps else None

            # Calculate memory size
            memory_size = 0
            if hasattr(memory, "memory_dir") and memory.memory_dir.exists():
                for f in memory.memory_dir.glob("*.json"):
                    memory_size += f.stat().st_size

            return MemoryStats(
                total_entries=len(entries),
                entries_by_tag=tag_counts,
                average_confidence=avg_confidence,
                rule_of_two_count=rule_two_count,
                rule_four_count=rule_four_count,
                memory_size_bytes=memory_size,
                last_entry_timestamp=last_timestamp,
            )

    async def stream_entries(self) -> AsyncIterator[MemoryEntry]:
        """Stream all memory entries."""
        memory = self._get_memory()
        entries = list(memory._local_cache.values()) if hasattr(memory, "_local_cache") else []

        for entry in entries:
            yield MemoryEntry(
                id=entry.get("id", ""),
                problem_fingerprint=entry.get("problem_fingerprint", ""),
                timestamp=datetime.fromisoformat(
                    entry.get("timestamp", datetime.now(UTC).isoformat())
                ),
                problem=entry.get("problem", ""),
                problem_preview=entry.get("problem_preview", ""),
                analysis_summary=entry.get("analysis_summary", {}),
                tags=entry.get("tags", []),
                confidence_score=entry.get("confidence_score"),
                structural_integrity_score=entry.get("structural_integrity_score", 0.0),
                rule_of_two_applied=entry.get("rule_of_two_applied", False),
                rule_of_four_applied=entry.get("rule_of_four_applied", False),
            )


# Global manager instance
_memory_manager: Optional[BrainMemoryManager] = None


def get_memory_manager() -> BrainMemoryManager:
    """Get or create brain memory manager."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = BrainMemoryManager()
    return _memory_manager


@router.post("/save", response_model=SaveReasoningResponse)
async def save_reasoning(request: SaveReasoningRequest) -> SaveReasoningResponse:
    """Save reasoning result to brain memory."""
    manager = get_memory_manager()
    return await manager.save_reasoning(
        problem=request.problem, analysis=request.analysis, tags=request.tags
    )


@router.post("/query", response_model=list[MemoryQueryResult])
async def query_memory(request: MemoryQueryRequest) -> list[MemoryQueryResult]:
    """Query brain memory for relevant entries."""
    manager = get_memory_manager()
    return await manager.query_memory(
        query=request.query,
        tags=request.tags,
        limit=request.limit,
        min_confidence=request.min_confidence,
    )


@router.get("/recall")
async def recall_similar(
    problem: str = Query(..., description="Problem to find similar analyses for"),
    limit: int = Query(default=5, ge=1, le=20),
) -> list[MemoryEntry]:
    """Recall similar past analyses for a problem."""
    manager = get_memory_manager()
    return await manager.recall_similar(problem, limit)


@router.get("/stats", response_model=MemoryStats)
async def get_memory_stats() -> MemoryStats:
    """Get brain memory statistics."""
    manager = get_memory_manager()
    return await manager.get_stats()


@router.get("/stream")
async def stream_memory_entries() -> StreamingResponse:
    """Stream all memory entries as Server-Sent Events."""
    manager = get_memory_manager()

    async def event_generator():
        async for entry in manager.stream_entries():
            yield f"data: {entry.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check for brain memory system."""
    try:
        manager = get_memory_manager()
        stats = await manager.get_stats()
        return {
            "status": "healthy",
            "memory_available": _MEMORY_AVAILABLE,
            "total_entries": stats.total_entries,
            "memory_size_mb": stats.memory_size_bytes / (1024 * 1024),
        }
    except Exception as e:
        return {
            "status": "degraded",
            "memory_available": _MEMORY_AVAILABLE,
            "error": str(e),
        }
