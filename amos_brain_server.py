#!/usr/bin/env python3
"""AMOS Brain Server - Production HTTP/MCP server with full cognitive capabilities.

Real implementation using:
- FastAPI for HTTP endpoints
- MCP for tool integration
- Anthropic/OpenAI for LLM reasoning
- AMOS laws for governance
- State-of-the-art agent patterns

Run: python amos_brain_server.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

# AMOS imports
from amos_brain.cognitive_engine_v2 import (
    CognitiveEngineV2,
    get_cognitive_engine_v2,
)
from amos_brain.laws import GlobalLaws
from amos_brain.mcp_tools_bridge import MCPToolsBridge
from clawspring.mcp.types import MCPServerConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos_brain_server")


@dataclass
class BrainSession:
    """Active brain session with state."""

    session_id: str
    engine: CognitiveEngineV2
    mcp_bridge: MCPToolsBridge
    created_at: float = field(default_factory=lambda: time.time())
    last_activity: float = field(default_factory=lambda: time.time())
    history: list[dict] = field(default_factory=list)

    def touch(self) -> None:
        self.last_activity = time.time()


class AMOSBrainServer:
    """Production AMOS Brain Server.

    Features:
    - HTTP API for cognitive queries
    - MCP tool integration (filesystem, git, web)
    - Streaming responses
    - Session management
    - Law-governed reasoning
    - Multi-provider LLM support
    """

    def __init__(self):
        self.sessions: dict[str, BrainSession] = {}
        self.laws = GlobalLaws()
        self.metrics = {
            "total_requests": 0,
            "active_sessions": 0,
            "avg_response_time_ms": 0.0,
        }
        self._cleanup_task: asyncio.Optional[Task] = None
        self._mcp_configs: list[MCPServerConfig] = []

    async def initialize(self) -> None:
        """Initialize server components."""
        logger.info("Initializing AMOS Brain Server...")

        # Start session cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("AMOS Brain Server initialized")

    async def shutdown(self) -> None:
        """Shutdown server."""
        logger.info("Shutting down AMOS Brain Server...")

        if self._cleanup_task:
            self._cleanup_task.cancel()

        # Close all sessions
        for session in self.sessions.values():
            # Cleanup if needed
            pass

        logger.info("AMOS Brain Server shutdown complete")

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of inactive sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                await self._cleanup_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")

    async def _cleanup_sessions(self) -> None:
        """Remove inactive sessions (inactive > 30 min)."""
        now = time.time()
        timeout = 1800  # 30 minutes

        to_remove = [
            sid for sid, session in self.sessions.items() if now - session.last_activity > timeout
        ]

        for sid in to_remove:
            del self.sessions[sid]
            logger.info(f"Cleaned up inactive session: {sid}")

        self.metrics["active_sessions"] = len(self.sessions)

    def create_session(
        self,
        provider: str = "anthropic",
        model: str = "claude-3-5-sonnet-20241022",
    ) -> BrainSession:
        """Create new brain session."""
        session_id = str(uuid.uuid4())[:12]

        engine = get_cognitive_engine_v2(provider=provider, model=model)
        mcp_bridge = MCPToolsBridge(root_path=".")

        session = BrainSession(
            session_id=session_id,
            engine=engine,
            mcp_bridge=mcp_bridge,
        )

        self.sessions[session_id] = session
        self.metrics["active_sessions"] = len(self.sessions)

        logger.info(f"Created session {session_id} with {provider}/{model}")
        return session

    def get_session(self, session_id: str) -> Optional[BrainSession]:
        """Get existing session."""
        session = self.sessions.get(session_id)
        if session:
            session.touch()
        return session

    async def think(
        self,
        session_id: Optional[str],
        query: str,
        domain: str = "general",
        stream: bool = False,
    ) -> dict[str, Any] | StreamingResponse:
        """Execute thinking process.

        Args:
            session_id: Existing session or None for new
            query: Query to think about
            domain: Domain context
            stream: Whether to stream response

        Returns:
            Cognitive result or streaming response
        """
        start_time = time.time()
        self.metrics["total_requests"] += 1

        # Get or create session
        if session_id:
            session = self.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = self.create_session()

        # Check laws before processing
        pre_check = self.laws.pre_process(query)
        if pre_check.get("blocked"):
            return {
                "error": "Query blocked by AMOS laws",
                "reason": pre_check.get("reason"),
                "law": pre_check.get("law"),
                "session_id": session.session_id,
            }

        # Execute thinking
        try:
            cognitive_state = await asyncio.to_thread(
                session.engine.think,
                query=query,
                domain=domain,
            )

            # Build response
            latency_ms = (time.time() - start_time) * 1000
            self._update_metrics(latency_ms)

            result = {
                "session_id": session.session_id,
                "query": query,
                "domain": domain,
                "reasoning_chain": cognitive_state.get_reasoning_chain(),
                "thoughts": [
                    {
                        "phase": t.phase.name,
                        "content": t.content,
                        "confidence": t.confidence,
                    }
                    for t in cognitive_state.thoughts
                ],
                "context": {
                    k: v
                    for k, v in cognitive_state.context.items()
                    if isinstance(v, (str, int, float, bool, list, dict))
                },
                "metrics": {
                    "latency_ms": latency_ms,
                    "thought_count": len(cognitive_state.thoughts),
                },
            }

            # Store in session history
            session.history.append(
                {
                    "query": query,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "result_summary": result["reasoning_chain"][:200] + "...",
                }
            )

            return result

        except Exception as e:
            logger.error(f"Thinking error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def execute_tool(
        self,
        session_id: str,
        tool_name: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute MCP tool through brain session.

        Args:
            session_id: Active session ID
            tool_name: Tool to execute (fs_read_file, git_status, web_search)
            params: Tool parameters

        Returns:
            Tool execution result
        """
        session = self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Map tool names to bridge methods
        tool_map: dict[str, Callable] = {
            "fs_read_file": session.mcp_bridge.fs_read_file,
            "fs_write_file": session.mcp_bridge.fs_write_file,
            "fs_search_files": session.mcp_bridge.fs_search_files,
            "git_status": session.mcp_bridge.git_status,
            "git_log": session.mcp_bridge.git_log,
            "git_diff": session.mcp_bridge.git_diff,
            "web_search": session.mcp_bridge.web_search,
            "web_fetch": session.mcp_bridge.web_fetch,
        }

        if tool_name not in tool_map:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown tool: {tool_name}. Available: {list(tool_map.keys())}",
            )

        try:
            result = await asyncio.to_thread(tool_map[tool_name], **params)
            return {
                "session_id": session_id,
                "tool": tool_name,
                "params": params,
                "result": result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def _update_metrics(self, latency_ms: float) -> None:
        """Update server metrics."""
        self.metrics["avg_response_time_ms"] = (
            self.metrics["avg_response_time_ms"] * 0.9 + latency_ms * 0.1
        )

    def get_metrics(self) -> dict[str, Any]:
        """Get server metrics."""
        return {
            **self.metrics,
            "uptime_seconds": time.time() - self._start_time if hasattr(self, "_start_time") else 0,
        }


# Global server instance
brain_server = AMOSBrainServer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    brain_server._start_time = time.time()
    await brain_server.initialize()
    yield
    await brain_server.shutdown()


# Create FastAPI app
app = FastAPI(
    title="AMOS Brain Server",
    description="Production cognitive server with MCP tool integration",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "metrics": brain_server.get_metrics(),
    }


@app.post("/v2/sessions")
async def create_session(
    provider: str = "anthropic",
    model: str = "claude-3-5-sonnet-20241022",
) -> dict[str, Any]:
    """Create new brain session."""
    session = brain_server.create_session(provider=provider, model=model)
    return {
        "session_id": session.session_id,
        "provider": provider,
        "model": model,
        "created_at": datetime.fromtimestamp(session.created_at, UTC).isoformat(),
    }


@app.get("/v2/sessions/{session_id}")
async def get_session(session_id: str) -> dict[str, Any]:
    """Get session info."""
    session = brain_server.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "created_at": datetime.fromtimestamp(session.created_at, UTC).isoformat(),
        "last_activity": datetime.fromtimestamp(session.last_activity, UTC).isoformat(),
        "history_count": len(session.history),
    }


@app.post("/v2/think")
async def think(
    query: str,
    session_id: Optional[str] = None,
    domain: str = "general",
) -> dict[str, Any]:
    """Execute cognitive thinking."""
    result = await brain_server.think(
        session_id=session_id,
        query=query,
        domain=domain,
    )
    return result


@app.post("/v2/tools/{tool_name}")
async def execute_tool(
    tool_name: str,
    session_id: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Execute MCP tool."""
    return await brain_server.execute_tool(session_id, tool_name, params)


@app.get("/v2/tools")
async def list_tools() -> dict[str, Any]:
    """List available tools."""
    return {
        "tools": [
            {"name": "fs_read_file", "description": "Read file or list directory"},
            {"name": "fs_write_file", "description": "Write content to file"},
            {"name": "fs_search_files", "description": "Search files for pattern"},
            {"name": "git_status", "description": "Get git repository status"},
            {"name": "git_log", "description": "Get commit history"},
            {"name": "git_diff", "description": "Get working directory changes"},
            {"name": "web_search", "description": "Search the web"},
            {"name": "web_fetch", "description": "Fetch content from URL"},
        ],
    }


@app.get("/v2/metrics")
async def get_metrics() -> dict[str, Any]:
    """Get server metrics."""
    return brain_server.get_metrics()


@app.delete("/v2/sessions/{session_id}")
async def close_session(session_id: str) -> dict[str, Any]:
    """Close session."""
    if session_id in brain_server.sessions:
        del brain_server.sessions[session_id]
        brain_server.metrics["active_sessions"] = len(brain_server.sessions)
        return {"status": "closed", "session_id": session_id}
    raise HTTPException(status_code=404, detail="Session not found")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


def main():
    """Run server."""
    import uvicorn

    host = os.environ.get("AMOS_BRAIN_HOST", "0.0.0.0")
    port = int(os.environ.get("AMOS_BRAIN_PORT", "8000"))

    logger.info(f"Starting AMOS Brain Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
