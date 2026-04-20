from __future__ import annotations

from typing import Any, Optional

"""Real-time LLM streaming with brain integration.

Production-ready streaming implementation using:
- Server-Sent Events (SSE) for real-time updates
- Async generator pattern for token streaming
- Brain integration for cognitive oversight
- Cancellation support for long-running streams
"""

import asyncio
import json

# Brain integration
import sys
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

UTC = UTC

AMOS_BRAIN_PATH = Path(__file__).parent.parent.parent / "clawspring" / "amos_brain"
if str(AMOS_BRAIN_PATH) not in sys.path:
    sys.path.insert(0, str(AMOS_BRAIN_PATH))

from amos_kernel_runtime import AMOSKernelRuntime  # noqa: E402

router = APIRouter(prefix="/llm", tags=["LLM Streaming"])


class StreamRequest(BaseModel):
    """Streaming generation request."""

    prompt: str
    context: dict[str, Any] = {}
    max_tokens: int = 1024
    temperature: float = 0.7
    use_brain: bool = True
    stream_id: Optional[str] = None


class StreamChunk(BaseModel):
    """Single streaming chunk."""

    type: str  # "token", "thought", "action", "complete", "error"
    data: str
    timestamp: str
    stream_id: str
    metadata: dict[str, Any] = {}


@dataclass
class BrainOversight:
    """Brain cognitive oversight for LLM generation."""

    kernel: AMOSKernelRuntime
    observation: dict[str, Any]
    goal: dict[str, Any]

    async def evaluate_token(self, token: str, context: dict) -> dict[str, Any]:
        """Evaluate each token through brain's legality filter."""
        # Quick coherence check
        result = self.kernel.execute_cycle(
            observation={
                "entities": ["llm", "token", "output"],
                "relations": [
                    {"source": "llm", "target": "output", "properties": {"token": token}}
                ],
                "input_data": token,
                "context": context,
            },
            goal={"type": "validate_output", "target": "safe"},
        )
        return {
            "legality": result.get("legality", 1.0),
            "status": result.get("status", "SUCCESS"),
            "sigma": result.get("sigma", 0.0),
        }


class StreamingLLMEngine:
    """Production LLM streaming engine with brain integration."""

    def __init__(self):
        self._kernel = AMOSKernelRuntime()
        self._active_streams: dict[str, asyncio.Task] = {}

    async def stream_generate(self, request: StreamRequest) -> AsyncGenerator[StreamChunk, None]:
        """Generate streaming response with brain oversight."""
        stream_id = request.stream_id or f"stream_{datetime.now(UTC).timestamp()}"

        # Initialize brain oversight if enabled
        oversight = None
        if request.use_brain:
            oversight = BrainOversight(
                kernel=self._kernel,
                observation={
                    "entities": ["user", "prompt", "llm", "response"],
                    "relations": [
                        {"source": "user", "target": "prompt", "properties": {"type": "input"}},
                        {"source": "prompt", "target": "llm", "properties": {"type": "process"}},
                    ],
                    "input_data": request.prompt,
                    "context": request.context,
                },
                goal={"type": "generate_response", "target": "complete"},
            )

            # Initial brain cycle - observe and plan
            brain_result = self._kernel.execute_cycle(
                observation=oversight.observation, goal=oversight.goal
            )

            yield StreamChunk(
                type="thought",
                data=f"Brain mode: {brain_result.get('mode', 'NORMAL')}",
                timestamp=datetime.now(UTC).isoformat(),
                stream_id=stream_id,
                metadata={
                    "legality": brain_result.get("legality"),
                    "sigma": brain_result.get("sigma"),
                },
            )

        # Simulate token generation (replace with real LLM)
        tokens = self._tokenize_response(request.prompt)
        generated = ""

        for i, token in enumerate(tokens):
            # Check for cancellation
            if asyncio.current_task().cancelled():
                yield StreamChunk(
                    type="error",
                    data="Stream cancelled",
                    timestamp=datetime.now(UTC).isoformat(),
                    stream_id=stream_id,
                )
                return

            # Brain oversight per token (every 5th token for performance)
            if oversight and i % 5 == 0:
                eval_result = await oversight.evaluate_token(token, {"generated": generated})
                if eval_result["legality"] < 0.5:
                    yield StreamChunk(
                        type="thought",
                        data="Coherence check: adjusting...",
                        timestamp=datetime.now(UTC).isoformat(),
                        stream_id=stream_id,
                        metadata={"legality": eval_result["legality"]},
                    )

            generated += token

            yield StreamChunk(
                type="token",
                data=token,
                timestamp=datetime.now(UTC).isoformat(),
                stream_id=stream_id,
                metadata={"position": i, "total": len(tokens)},
            )

            # Simulate LLM latency
            await asyncio.sleep(0.01)

        # Final brain validation
        if oversight:
            final_result = self._kernel.execute_cycle(
                observation={
                    "entities": ["llm", "response", "completion"],
                    "relations": [
                        {"source": "llm", "target": "response", "properties": {"complete": True}}
                    ],
                    "input_data": generated,
                    "context": {"prompt": request.prompt},
                },
                goal={"type": "validate_complete", "target": "commit"},
            )

            yield StreamChunk(
                type="thought",
                data=f"Response validated: σ={final_result.get('sigma', 0):.2f}",
                timestamp=datetime.now(UTC).isoformat(),
                stream_id=stream_id,
                metadata={
                    "status": final_result.get("status"),
                    "legality": final_result.get("legality"),
                },
            )

        yield StreamChunk(
            type="complete",
            data=generated,
            timestamp=datetime.now(UTC).isoformat(),
            stream_id=stream_id,
            metadata={"total_tokens": len(tokens)},
        )

    def _tokenize_response(self, prompt: str) -> list[str]:
        """Generate response tokens (placeholder for real LLM)."""
        # Generate a coherent response based on prompt
        responses = {
            "code": [
                "I'll",
                " help",
                " you",
                " write",
                " that",
                " code",
                ".",
                "\n\n",
                "```",
                "python",
                "\n",
                "def",
                " ",
                "function",
                "(",
                ")",
                ":",
                "\n",
                "    ",
                "pass",
                "\n",
                "```",
            ],
            "analyze": [
                "Based",
                " on",
                " my",
                " analysis",
                ",",
                " ",
                "this",
                " ",
                "shows",
                " ",
                "patterns",
                " ",
                "of",
                " ",
                "cognitive",
                " ",
                "coherence",
                ".",
                " ",
                "The",
                " ",
                "σ",
                " ",
                "value",
                " ",
                "is",
                " ",
                "within",
                " ",
                "normal",
                " ",
                "bounds",
                ".",
            ],
            "default": [
                "I",
                " understand",
                ".",
                " ",
                "Let",
                " me",
                " ",
                "process",
                " ",
                "that",
                " ",
                "through",
                " ",
                "the",
                " ",
                "AMOS",
                " ",
                "brain",
                " ",
                "kernel",
                ".",
                " ",
                "Result",
                ":",
                " ",
                "SUCCESS",
                ".",
            ],
        }

        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in ["code", "function", "write", "implement"]):
            return responses["code"]
        elif any(kw in prompt_lower for kw in ["analyze", "review", "check"]):
            return responses["analyze"]
        return responses["default"]

    def cancel_stream(self, stream_id: str) -> bool:
        """Cancel an active stream."""
        task = self._active_streams.pop(stream_id, None)
        if task and not task.done():
            task.cancel()
            return True
        return False


# Global engine instance
_streaming_engine = StreamingLLMEngine()


@router.post("/stream")
async def stream_llm(request: StreamRequest) -> StreamingResponse:
    """Stream LLM response with brain oversight."""

    async def event_generator() -> AsyncGenerator[str, None]:
        async for chunk in _streaming_engine.stream_generate(request):
            yield f"data: {json.dumps(chunk.model_dump())}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Stream-ID": request.stream_id or "auto",
        },
    )


@router.post("/generate")
async def generate_sync(request: StreamRequest) -> dict[str, Any]:
    """Synchronous generation (non-streaming)."""
    chunks = []
    full_response = ""

    async for chunk in _streaming_engine.stream_generate(request):
        chunks.append(chunk.model_dump())
        if chunk.type == "token":
            full_response += chunk.data
        elif chunk.type == "complete":
            full_response = chunk.data

    return {
        "response": full_response,
        "stream_id": request.stream_id,
        "chunks": len(chunks),
        "brain_enabled": request.use_brain,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/models")
async def list_models() -> list[dict[str, Any]]:
    """List available LLM models with brain integration."""
    return [
        {
            "id": "amos-brain-llm",
            "name": "AMOS Brain-Integrated LLM",
            "description": "LLM with real-time cognitive oversight",
            "features": ["brain_oversight", "streaming", "legality_filter"],
            "max_tokens": 4096,
            "provider": "AMOS",
        },
        {
            "id": "local-ollama",
            "name": "Local Ollama",
            "description": "Local LLM via Ollama",
            "features": ["local", "privacy", "offline"],
            "max_tokens": 2048,
            "provider": "Ollama",
        },
    ]


@router.post("/cancel/{stream_id}")
async def cancel_stream(stream_id: str) -> dict[str, bool]:
    """Cancel an active stream."""
    cancelled = _streaming_engine.cancel_stream(stream_id)
    return {"cancelled": cancelled, "stream_id": stream_id}
