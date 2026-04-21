"""FastAPI integration for AMOS Kernel buses and services."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, Field

# Kernel imports
from amos_kernel import (
    BusType,
    create_llm_provider,
    get_bus_coordinator,
    get_engine_registry,
    get_nl_processor,
    get_unified_kernel,
)


# ============================================================================
# Pydantic Models
# ============================================================================

class ModelRequest(BaseModel):
    prompt: str
    model_id: str = "gpt-4o"
    parameters: dict[str, Any] = Field(default_factory=dict)


class ModelResponse(BaseModel):
    content: str
    model_id: str
    tokens_used: int
    latency_ms: float


class MemoryEntry(BaseModel):
    entry_id: str
    content: str
    domain: str = "general"
    tags: list[str] = Field(default_factory=list)


class ToolRequest(BaseModel):
    tool_id: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class NLProcessRequest(BaseModel):
    query: str
    context: dict[str, Any] = Field(default_factory=dict)


class NLProcessResponse(BaseModel):
    intent: str
    proposals: list[dict[str, Any]]
    explanation: str


class BusHealthResponse(BaseModel):
    bus_type: str
    status: str
    metrics: dict[str, Any]


class EngineInfo(BaseModel):
    name: str
    version: str
    capabilities: list[str]
    equations_count: int


# ============================================================================
# FastAPI Router Factory
# ============================================================================


def create_kernel_router() -> APIRouter:
    """Create FastAPI router with all kernel endpoints."""
    router = APIRouter(prefix="/kernel", tags=["kernel"])

    # -------------------------------------------------------------------------
    # Model/LLM Endpoints
    # -------------------------------------------------------------------------
    @router.post("/model/generate", response_model=ModelResponse)
    async def model_generate(request: ModelRequest) -> ModelResponse:
        """Generate text using LLM via ModelBus."""
        coordinator = get_bus_coordinator()
        model_bus = coordinator.get_bus(BusType.MODEL)

        # Use provider directly for now
        provider = create_llm_provider("mock")

        from amos_kernel import ModelRequest as KernelModelRequest

        kernel_request = KernelModelRequest(
            model_id=request.model_id,
            prompt=request.prompt,
            parameters=request.parameters,
        )

        # In production, this would route through ModelBus
        response = await provider.generate(kernel_request)

        return ModelResponse(
            content=response.content,
            model_id=response.model_id,
            tokens_used=response.tokens_used,
            latency_ms=0.0,
        )

    # -------------------------------------------------------------------------
    # Memory Endpoints
    # -------------------------------------------------------------------------
    @router.post("/memory/store")
    async def memory_store(entry: MemoryEntry) -> dict[str, Any]:
        """Store entry in memory via MemoryBus."""
        coordinator = get_bus_coordinator()
        memory_bus = coordinator.get_bus(BusType.MEMORY)

        await memory_bus.publish(
            {
                "topic": "memory.store",
                "payload": {
                    "entry_id": entry.entry_id,
                    "content": entry.content,
                    "domain": entry.domain,
                    "tags": entry.tags,
                },
            }
        )

        return {"stored": True, "entry_id": entry.entry_id}

    @router.get("/memory/search")
    async def memory_search(query: str, domain: str = "general") -> dict[str, Any]:
        """Search memory via MemoryBus."""
        coordinator = get_bus_coordinator()
        memory_bus = coordinator.get_bus(BusType.MEMORY)

        # In production, this would use memory_bus semantic search
        return {"query": query, "domain": domain, "results": []}

    # -------------------------------------------------------------------------
    # Tool Endpoints
    # -------------------------------------------------------------------------
    @router.post("/tool/execute")
    async def tool_execute(request: ToolRequest) -> dict[str, Any]:
        """Execute tool via ToolBus."""
        coordinator = get_bus_coordinator()
        tool_bus = coordinator.get_bus(BusType.TOOL)

        # In production, route through ToolBus
        return {
            "tool_id": request.tool_id,
            "executed": True,
            "result": {},
        }

    @router.get("/tool/list")
    async def tool_list() -> dict[str, Any]:
        """List available tools."""
        coordinator = get_bus_coordinator()
        tool_bus = coordinator.get_bus(BusType.TOOL)

        # Get from ToolBus registry
        return {"tools": []}

    # -------------------------------------------------------------------------
    # Natural Language Endpoints
    # -------------------------------------------------------------------------
    @router.post("/nl/process", response_model=NLProcessResponse)
    async def nl_process(request: NLProcessRequest) -> NLProcessResponse:
        """Process natural language via NL Processor."""
        processor = get_nl_processor()

        intent, proposals, explanation = processor.process(request.query)

        return NLProcessResponse(
            intent=intent.intent_type if hasattr(intent, "intent_type") else str(intent),
            proposals=[{"action": str(p)} for p in proposals],
            explanation=explanation,
        )

    # -------------------------------------------------------------------------
    # Bus Health Endpoints
    # -------------------------------------------------------------------------
    @router.get("/bus/health", response_model=list[BusHealthResponse])
    async def bus_health() -> list[BusHealthResponse]:
        """Get health status of all 8 buses."""
        coordinator = get_bus_coordinator()

        health_data = []
        for bus_type in BusType:
            bus = coordinator.get_bus(bus_type)
            # Async health check
            import asyncio

            health = await bus.health_check()
            health_data.append(
                BusHealthResponse(
                    bus_type=bus_type.value,
                    status=health.get("status", "unknown"),
                    metrics=health,
                )
            )

        return health_data

    @router.post("/bus/publish")
    async def bus_publish(bus_type: str, topic: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Publish message to any bus."""
        coordinator = get_bus_coordinator()

        try:
            bt = BusType(bus_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid bus type: {bus_type}")

        bus = coordinator.get_bus(bt)
        await bus.publish({"topic": topic, "payload": payload})

        return {"published": True, "bus_type": bus_type, "topic": topic}

    # -------------------------------------------------------------------------
    # Engine Endpoints
    # -------------------------------------------------------------------------
    @router.get("/engines", response_model=list[EngineInfo])
    async def list_engines() -> list[EngineInfo]:
        """List all discovered AMOS engines."""
        registry = get_engine_registry()

        engines = []
        for engine in registry.list_engines():
            engines.append(
                EngineInfo(
                    name=engine.name,
                    version=engine.version,
                    capabilities=[c.name for c in engine.capabilities],
                    equations_count=len(engine.get_equations()),
                )
            )

        return engines

    @router.get("/engines/{engine_name}")
    async def get_engine(engine_name: str) -> dict[str, Any]:
        """Get specific engine details."""
        registry = get_engine_registry()
        engine = registry.get_engine(engine_name)

        if not engine:
            raise HTTPException(status_code=404, detail=f"Engine {engine_name} not found")

        return {
            "name": engine.name,
            "version": engine.version,
            "domain_tags": engine.domain_tags,
            "capabilities": [
                {"name": c.name, "equations": c.equations}
                for c in engine.capabilities
            ],
        }

    # -------------------------------------------------------------------------
    # Unified Kernel Endpoints
    # -------------------------------------------------------------------------
    @router.get("/state")
    async def get_state() -> dict[str, Any]:
        """Get current unified kernel state."""
        kernel = get_unified_kernel()
        return {"state": str(kernel.current_state), "cycle": kernel.cycle_count}

    @router.post("/execute")
    async def execute_cycle(event: dict[str, Any]) -> dict[str, Any]:
        """Execute one kernel cycle."""
        kernel = get_unified_kernel()
        result = await kernel.execute_cycle(event)
        return {"result": result, "cycle": kernel.cycle_count}

    return router


# ============================================================================
# Main Application Factory
# ============================================================================


def create_kernel_app() -> FastAPI:
    """Create FastAPI application with all kernel endpoints."""
    app = FastAPI(
        title="AMOS Kernel API",
        description="REST API for AMOS Kernel 8 Integration Buses and Services",
        version="7.1.0",
    )

    # Add kernel router
    app.include_router(create_kernel_router())

    @app.get("/health")
    async def health_check() -> dict[str, Any]:
        """API health check."""
        return {
            "status": "healthy",
            "kernel_version": "7.1.0",
            "buses": 8,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return app
