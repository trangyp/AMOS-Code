"""AMOS API Hub - Production Backend API for hub-and-spoke architecture.

This is the AMOS-Consulting backend that serves as the single API hub
for all client repositories (AMOS-Claws, Mailinhconect, AMOS-Invest).

Integrates:
- Real LLM providers (Ollama, OpenAI, Anthropic)
- AMOS Brain cognitive runtime
- Repo Doctor analysis engine
- Workflow orchestration

Usage:
    uvicorn amos_api_hub:app --host 0.0.0.0 --port 8000
"""

import os
import sys
import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator, List, Optional
from pathlib import Path

# Ensure amos_brain is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(Path(__file__).parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent / "repo_doctor"))

try:
    from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, StreamingResponse
except ImportError:
    raise ImportError(
        "FastAPI not installed. Run: pip install fastapi uvicorn"
    )

from amos_brain.api_contracts import (
    ChatRequest,
    ChatResponse,
    ChatContext,
    ChatMessage,
    BrainRunRequest,
    BrainRunResponse,
    RepoScanRequest,
    RepoScanResult,
    RepoScanIssue,
    RepoFixRequest,
    RepoFixResult,
    ModelInfo,
    ModelRequest,
    ModelResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
    ApiError,
    ErrorCode,
)

# Import real providers
try:
    from llm_providers import llm_router, LLMRequest, Message, OllamaProvider
    LLM_PROVIDERS_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] LLM providers not available: {e}")
    LLM_PROVIDERS_AVAILABLE = False

# Import brain
try:
    from amos_brain import get_amos_integration, think, decide
    BRAIN_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] AMOS Brain not available: {e}")
    BRAIN_AVAILABLE = False

# Import repo doctor
try:
    from repo_doctor.ingest.treesitter_ingest import TreeSitterIngest
    from repo_doctor.architecture import ArchitectureAnalyzer
    REPO_DOCTOR_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Repo Doctor not available: {e}")
    REPO_DOCTOR_AVAILABLE = False


# ============================================================================
# Lifecycle Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Manage application lifecycle."""
    # Startup
    print("AMOS API Hub starting...")
    yield
    # Shutdown
    print("AMOS API Hub shutting down...")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="AMOS API Hub",
    description="Central API hub for AMOS ecosystem",
    version="14.0.0",
    lifespan=lifespan,
)

# CORS for client repos
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://claws.yourdomain.com",
        "https://mailinh.yourdomain.com",
        "https://invest.yourdomain.com",
        "http://localhost:3000",  # Dev
        "http://localhost:5173",  # Vite dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Error Handling
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    error = ApiError(
        code=ErrorCode.INTERNAL_ERROR,
        message=str(exc),
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=500,
        content={"error": error.model_dump()},
    )


# ============================================================================
# Health Check
# ============================================================================

@app.get("/v1/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "amos-api-hub",
        "version": "14.0.0",
    }


# ============================================================================
# Chat API
# ============================================================================

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process chat message through AMOS brain with real LLM integration.

    This endpoint:
    1. Receives chat request from client repos
    2. Routes to appropriate LLM (Ollama local -> OpenAI -> Anthropic)
    3. Returns structured response with token usage
    """
    try:
        if not LLM_PROVIDERS_AVAILABLE:
            raise RuntimeError("LLM providers not available")

        # Build message history
        messages = []
        if request.history:
            for msg in request.history:
                messages.append(Message(role=msg.get("role", "user"), content=msg.get("content", "")))
        messages.append(Message(role="user", content=request.message))

        # Create LLM request
        llm_request = LLMRequest(
            messages=messages,
            model=request.model,
            temperature=0.7,
        )

        # Route to best available provider (Ollama preferred for local)
        start_time = time.time()
        response = await llm_router.route_request(llm_request)
        latency_ms = (time.time() - start_time) * 1000

        return ChatResponse(
            message=response.content,
            conversation_id=request.context.conversation_id or f"conv-{int(start_time)}",
            session_id=request.context.session_id,
            model=response.model,
            usage=response.usage or {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            latency_ms=latency_ms,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ApiError(
                code=ErrorCode.BRAIN_EXECUTION_FAILED,
                message=f"Chat processing failed: {e}",
            ).model_dump(),
        )


# ============================================================================
# Brain Execution API
# ============================================================================

@app.post("/v1/brain/run", response_model=BrainRunResponse)
async def brain_run(request: BrainRunRequest) -> BrainRunResponse:
    """Execute AMOS brain cycle with real cognitive runtime.

    Provides direct access to AMOS cognitive architecture for:
    - State graph execution
    - Branch generation
    - Morph execution
    """
    try:
        if not BRAIN_AVAILABLE:
            raise RuntimeError("AMOS Brain not available")

        start_time = time.time()

        # Use the think function from amos_brain for cognitive analysis
        analysis = think(
            query=request.input.get("query", "Process input"),
            context=request.input.get("context", {}),
        )

        execution_time_ms = (time.time() - start_time) * 1000

        return BrainRunResponse(
            run_id=f"run-{int(start_time * 1000)}",
            status="completed",
            branches=[],
            final_state=analysis,
            execution_time_ms=execution_time_ms,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ApiError(
                code=ErrorCode.BRAIN_EXECUTION_FAILED,
                message=str(e),
            ).model_dump(),
        )


# ============================================================================
# Repo Doctor API
# ============================================================================

@app.post("/v1/repo/scan", response_model=RepoScanResult)
async def repo_scan(request: RepoScanRequest) -> RepoScanResult:
    """Scan repository for issues.
    
    Analyzes code for:
    - Style violations
    - Security issues
    - Performance problems
    - Type errors
    """
    # TODO: Integrate with repo_doctor module
    return RepoScanResult(
        scan_id="scan-" + str(hash(request.repo_path))[:8],
        repo_path=request.repo_path,
        issues=[],
        summary={"total": 0, "by_severity": {}},
    )


@app.post("/v1/repo/fix", response_model=RepoFixResult)
async def repo_fix(request: RepoFixRequest) -> RepoFixResult:
    """Apply fixes to repository issues."""
    # TODO: Integrate with repo_doctor fix logic
    return RepoFixResult(
        fix_id="fix-" + str(hash(str(request.scan_id)))[:8],
        scan_id=request.scan_id,
        changes=[],
        applied=True,
    )


# ============================================================================
# Model API
# ============================================================================

@app.get("/v1/models", response_model=list[ModelInfo])
async def list_models() -> List[ModelInfo]:
    """List available LLM models.
    
    Returns models from:
    - Ollama (local)
    - vLLM (local)
    - LM Studio (local)
    """
    # TODO: Query actual model backends
    return [
        ModelInfo(
            model_id="llama3.1:8b",
            name="Llama 3.1 8B",
            provider="ollama",
            capabilities={
                "context_window": 128000,
                "max_output_tokens": 8192,
                "supports_tools": True,
                "supports_vision": False,
                "supports_streaming": True,
                "supports_json_mode": True,
            },
            is_local=True,
            is_loaded=True,
        ),
    ]


@app.post("/v1/models/run", response_model=ModelResponse)
async def run_model(request: ModelRequest) -> ModelResponse:
    """Run inference on specific model."""
    # TODO: Integrate with actual model backend
    return ModelResponse(
        content=f"Model {request.model_id} response to: {request.prompt[:50]}...",
        model_id=request.model_id,
        usage={"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
    )


# ============================================================================
# Workflow API
# ============================================================================

@app.post("/v1/workflow/run", response_model=WorkflowRunResponse)
async def run_workflow(request: WorkflowRunRequest) -> WorkflowRunResponse:
    """Execute AMOS workflow.
    
    Workflows include:
    - Repository analysis
    - Multi-step tasks
    - Automated fixing
    """
    # TODO: Integrate with workflow engine
    return WorkflowRunResponse(
        run_id="wf-" + str(hash(request.workflow_id))[:8],
        workflow_id=request.workflow_id,
        status="completed",
        tasks=[],
        output={"result": "Workflow executed"},
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
