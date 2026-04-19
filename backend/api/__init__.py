"""
AMOS API Layer

Domain-based API organization following FastAPI best practices 2026.
Each domain (llm, agents, system) has its own router, schemas, and service layer.

Creator: Trang Phan
Version: 3.0.0
"""

from fastapi import APIRouter

from .agents import router as agents_router
from .llm import router as llm_router
from .math import router as math_router
from .streaming import router as streaming_router
from .superbrain import router as superbrain_router
from .system import router as system_router

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include domain routers
api_router.include_router(llm_router, prefix="/llm", tags=["LLM"])
api_router.include_router(agents_router, prefix="/agents", tags=["Agents"])
api_router.include_router(system_router, prefix="/system", tags=["System"])
api_router.include_router(math_router, prefix="/math", tags=["Math Framework"])
api_router.include_router(
    superbrain_router, prefix="/superbrain", tags=["SuperBrain Cognitive System"]
)
api_router.include_router(streaming_router, prefix="/streaming", tags=["Real-Time Streaming"])

__all__ = ["api_router"]
