"""AMOS Brain-Powered Cognitive Streaming

Real-time streaming with brain analysis and cognitive processing.
Analyzes streaming data using BrainClient for intelligent insights.

Creator: Trang Phan
Version: 1.0.0
"""

import asyncio
import json
import time
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

# Import BrainClient facade and Canon
try:
    from clawspring.agents.amos_brain.facade import BrainClient
    from clawspring.agents.amos_brain.master_orchestrator import MasterOrchestrator

    from amos_brain.canon_bridge import get_canon_bridge

    _BRAIN_AVAILABLE = True
    _CANON_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False
    _CANON_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain/streaming", tags=["Brain Streaming"])


class StreamChunk(BaseModel):
    """Single chunk of streaming data."""

    content: str
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StreamAnalysisRequest(BaseModel):
    """Request for brain-powered stream analysis."""

    stream_id: str
    content_type: str = "text"
    analyze_sentiment: bool = True
    extract_entities: bool = True
    generate_summary: bool = False
    context: Dict[str, Any] = Field(default_factory=dict)


class StreamAnalysisResult(BaseModel):
    """Brain analysis result for a stream."""

    stream_id: str
    chunk_count: int
    total_chars: int
    sentiment_score: Optional[float]
    entities: List[dict[str, Any]]
    summary: Optional[str]
    insights: List[str]
    cognitive_load: float
    processing_time_ms: float
    timestamp: str


class BrainStreamProcessor:
    """Brain-powered stream processor for real-time analysis with Canon context."""

    def __init__(self):
        self._streams: Dict[str, list[StreamChunk]] = {}
        self._analysis_results: Dict[str, StreamAnalysisResult] = {}
        self._lock = asyncio.Lock()
        self._canon_bridge = None

    async def _get_canon_bridge(self):
        """Lazy initialization of canon bridge."""
        if self._canon_bridge is None and _CANON_AVAILABLE:
            self._canon_bridge = await get_canon_bridge()
        return self._canon_bridge

    async def process_chunk(
        self,
        stream_id: str,
        content: str,
        metadata: Optional[Dict[str, Any] ] = None,
    ) -> StreamChunk:
        """Process a single stream chunk."""
        chunk = StreamChunk(
            content=content,
            timestamp=datetime.now(UTC).isoformat(),
            metadata=metadata or {},
        )

        async with self._lock:
            if stream_id not in self._streams:
                self._streams[stream_id] = []
            self._streams[stream_id].append(chunk)

        return chunk

    async def analyze_stream(
        self,
        request: StreamAnalysisRequest,
    ) -> StreamAnalysisResult:
        """Analyze entire stream using brain."""
        start_time = time.time()

        async with self._lock:
            chunks = self._streams.get(request.stream_id, [])

        if not chunks:
            raise HTTPException(
                status_code=404,
                detail=f"Stream {request.stream_id} not found or empty",
            )

        total_chars = sum(len(c.content) for c in chunks)
        combined_text = " ".join(c.content for c in chunks)

        sentiment_score = None
        entities: List[dict[str, Any]] = []
        summary = None
        insights: List[str] = []
        cognitive_load = 0.5
        canon_context = {}

        if _BRAIN_AVAILABLE:
            try:
                client = BrainClient()

                # Enrich with Canon context if available
                if _CANON_AVAILABLE:
                    try:
                        canon = await self._get_canon_bridge()
                        domain = request.context.get("domain", "general")
                        ctx = canon.get_context_for_domain(domain)
                        canon_context = {
                            "domain": ctx.domain,
                            "terms_available": len(ctx.glossary_terms),
                            "applicable_agents": ctx.applicable_agents[:3],
                            "relevant_engines": ctx.relevant_engines[:3],
                        }
                        # Enrich text with Canon context
                        combined_text = canon.enrich_query(combined_text, domain)
                    except Exception:
                        pass

                # Build analysis context
                context = {
                    "stream_id": request.stream_id,
                    "content_type": request.content_type,
                    "chunk_count": len(chunks),
                    "total_chars": total_chars,
                    "canon_context": canon_context,
                    **request.context,
                }

                # Get brain analysis
                if request.analyze_sentiment:
                    sentiment_result = await client.think(
                        thought=f"Analyze sentiment: {combined_text[:500]}",
                        domain=request.context.get("domain", "general"),
                        context={**context, "analysis_type": "sentiment"},
                    )
                    sentiment_score = getattr(sentiment_result, "metadata", {}).get(
                        "sentiment_score", 0.5
                    )

                if request.extract_entities:
                    entity_result = await client.think(
                        thought=f"Extract entities: {combined_text[:500]}",
                        domain=request.context.get("domain", "general"),
                        context={**context, "analysis_type": "entity_extraction"},
                    )
                    entities = getattr(entity_result, "metadata", {}).get("entities", [])

                if request.generate_summary and len(combined_text) > 200:
                    summary_result = await client.think(
                        thought=f"Summarize: {combined_text[:1000]}",
                        domain=request.context.get("domain", "general"),
                        context={**context, "analysis_type": "summarization"},
                    )
                    summary = getattr(summary_result, "content", None)

                # Get insights
                insight_result = await client.think(
                    thought=f"Provide insights on: {combined_text[:500]}",
                    domain=request.context.get("domain", "general"),
                    context={**context, "analysis_type": "insights"},
                )
                insights = [insight_result.content] if insight_result.success else []
                # Add Canon context info to insights
                if canon_context:
                    insights.append(
                        f"Canon context: {canon_context.get('terms_available', 0)} terms available"
                    )

                # Calculate cognitive load
                cognitive_load = min(0.3 + (len(chunks) * 0.02), 1.0)

            except Exception as e:
                insights = [f"Brain analysis error: {e!s}"]

        processing_time_ms = (time.time() - start_time) * 1000

        result = StreamAnalysisResult(
            stream_id=request.stream_id,
            chunk_count=len(chunks),
            total_chars=total_chars,
            sentiment_score=sentiment_score,
            entities=entities,
            summary=summary,
            insights=insights,
            cognitive_load=cognitive_load,
            processing_time_ms=processing_time_ms,
            timestamp=datetime.now(UTC).isoformat(),
        )
        # Store canon context in result metadata
        result.metadata = {"canon_context": canon_context}

        async with self._lock:
            self._analysis_results[request.stream_id] = result

        return result

    async def stream_with_analysis(
        self,
        stream_id: str,
        content_generator: AsyncGenerator[str, None],
    ) -> AsyncGenerator[str, None]:
        """Stream content with real-time brain analysis."""
        buffer = ""
        chunk_count = 0

        async for content in content_generator:
            chunk_count += 1
            buffer += content

            # Process chunk
            await self.process_chunk(stream_id, content, {"chunk_num": chunk_count})

            # Yield with metadata
            data = {
                "type": "chunk",
                "stream_id": stream_id,
                "content": content,
                "chunk_num": chunk_count,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            yield f"data: {json.dumps(data)}\n\n"

            # Periodic analysis every 5 chunks
            if chunk_count % 5 == 0 and _BRAIN_AVAILABLE:
                try:
                    client = BrainClient()
                    analysis = await client.think(
                        thought=f"Quick analysis of stream progress: {buffer[-200:]}",
                        context={
                            "stream_id": stream_id,
                            "chunks_processed": chunk_count,
                            "analysis_type": "progress",
                        },
                    )

                    progress_data = {
                        "type": "progress_analysis",
                        "stream_id": stream_id,
                        "chunks_processed": chunk_count,
                        "insights": analysis.get("insights", []),
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                    yield f"data: {json.dumps(progress_data)}\n\n"
                except Exception:
                    pass

        # Final analysis
        try:
            request = StreamAnalysisRequest(
                stream_id=stream_id,
                content_type="text",
            )
            final_analysis = await self.analyze_stream(request)

            final_data = {
                "type": "final_analysis",
                "stream_id": stream_id,
                "analysis": final_analysis.model_dump(),
                "timestamp": datetime.now(UTC).isoformat(),
            }
            yield f"data: {json.dumps(final_data)}\n\n"
        except Exception as e:
            error_data = {
                "type": "error",
                "stream_id": stream_id,
                "error": str(e),
            }
            yield f"data: {json.dumps(error_data)}\n\n"

        yield "data: [DONE]\n\n"

    def get_stream(self, stream_id: str) -> Optional[List[StreamChunk] ]:
        """Get stream chunks by ID."""
        return self._streams.get(stream_id)

    def get_analysis(self, stream_id: str) -> Optional[StreamAnalysisResult]:
        """Get analysis result by stream ID."""
        return self._analysis_results.get(stream_id)

    async def clear_stream(self, stream_id: str) -> bool:
        """Clear a stream and its analysis."""
        async with self._lock:
            if stream_id in self._streams:
                del self._streams[stream_id]
            if stream_id in self._analysis_results:
                del self._analysis_results[stream_id]
            return True


# Global stream processor
stream_processor = BrainStreamProcessor()


@router.post("/chunks/{stream_id}")
async def add_stream_chunk(
    stream_id: str,
    content: str,
    metadata: Optional[Dict[str, Any] ] = None,
) -> StreamChunk:
    """Add a chunk to a stream."""
    return await stream_processor.process_chunk(stream_id, content, metadata)


@router.post("/analyze", response_model=StreamAnalysisResult)
async def analyze_stream_endpoint(
    request: StreamAnalysisRequest,
) -> StreamAnalysisResult:
    """Analyze a complete stream using brain."""
    return await stream_processor.analyze_stream(request)


@router.get("/streams/{stream_id}")
async def get_stream_chunks(stream_id: str) -> List[StreamChunk]:
    """Get all chunks for a stream."""
    chunks = stream_processor.get_stream(stream_id)
    if chunks is None:
        raise HTTPException(status_code=404, detail="Stream not found")
    return chunks


@router.get("/analysis/{stream_id}")
async def get_stream_analysis(stream_id: str) -> StreamAnalysisResult:
    """Get analysis result for a stream."""
    result = stream_processor.get_analysis(stream_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@router.delete("/streams/{stream_id}")
async def clear_stream_endpoint(stream_id: str) -> Dict[str, str]:
    """Clear a stream and its analysis."""
    await stream_processor.clear_stream(stream_id)
    return {"status": "cleared", "stream_id": stream_id}


@router.websocket("/ws/{stream_id}")
async def brain_streaming_websocket(websocket: WebSocket, stream_id: str) -> None:
    """WebSocket endpoint for brain-powered streaming.

    Messages:
    - Client -> Server: {"action": "chunk", "content": "..."}
    - Server -> Client: {"type": "ack", "chunk_num": N}
    - Server -> Client: {"type": "analysis", ...}
    """
    await websocket.accept()
    chunk_count = 0

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "stream_id": stream_id,
                "brain_available": _BRAIN_AVAILABLE,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        while True:
            message = await websocket.receive_json()
            action = message.get("action")

            if action == "chunk":
                content = message.get("content", "")
                metadata = message.get("metadata", {})

                chunk_count += 1
                await stream_processor.process_chunk(
                    stream_id, content, {**metadata, "chunk_num": chunk_count}
                )

                await websocket.send_json(
                    {
                        "type": "ack",
                        "stream_id": stream_id,
                        "chunk_num": chunk_count,
                    }
                )

            elif action == "analyze":
                request = StreamAnalysisRequest(
                    stream_id=stream_id,
                    content_type=message.get("content_type", "text"),
                    analyze_sentiment=message.get("analyze_sentiment", True),
                    extract_entities=message.get("extract_entities", True),
                    generate_summary=message.get("generate_summary", False),
                )

                result = await stream_processor.analyze_stream(request)
                await websocket.send_json(
                    {
                        "type": "analysis",
                        "stream_id": stream_id,
                        "result": result.model_dump(),
                    }
                )

            elif action == "clear":
                await stream_processor.clear_stream(stream_id)
                await websocket.send_json(
                    {
                        "type": "cleared",
                        "stream_id": stream_id,
                    }
                )
                chunk_count = 0

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
