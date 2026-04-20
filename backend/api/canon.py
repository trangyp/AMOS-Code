"""AMOS Canon API - Integration with canonical definitions.

Provides REST endpoints for accessing:
- Canonical glossary (system terminology)
- Agent registry
- Brain OS specifications
- Cognitive stack modules
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from amos_canon_integration import get_canon_loader

router = APIRouter(prefix="/canon", tags=["canon"])

# Global canon loader instance
_canon_loader = None
_canon_initialized = False


async def get_canon():
    """Get or initialize canon loader."""
    global _canon_loader, _canon_initialized
    if not _canon_initialized:
        _canon_loader = get_canon_loader()
        await _canon_loader.initialize()
        _canon_initialized = True
    return _canon_loader


class CanonStatusResponse(BaseModel):
    """Canon system status."""

    ready: bool
    timestamp: str
    loaded_files: list[str]
    failed_files: list[str]
    total_terms: int
    total_agents: int
    total_engines: int


class GlossaryResponse(BaseModel):
    """Canonical glossary response."""

    layers: list[dict[str, Any]]
    total_terms: int


class AgentRegistryResponse(BaseModel):
    """Agent registry response."""

    agents: dict[str, Any]
    total_agents: int


class BrainOSResponse(BaseModel):
    """Brain OS specification response."""

    components: dict[str, Any]
    total_engines: int


@router.get("/status", response_model=CanonStatusResponse)
async def canon_status() -> CanonStatusResponse:
    """Get Canon integration status."""
    loader = await get_canon()
    status = loader.get_status()
    return CanonStatusResponse(
        ready=status.ready,
        timestamp=status.timestamp,
        loaded_files=status.loaded_files,
        failed_files=status.failed_files,
        total_terms=status.total_terms,
        total_agents=status.total_agents,
        total_engines=status.total_engines,
    )


@router.get("/glossary", response_model=GlossaryResponse)
async def canon_glossary() -> GlossaryResponse:
    """Get canonical glossary with system terminology."""
    loader = await get_canon()
    glossary = loader.get_glossary()
    layers = glossary.get("layers", [])
    total_terms = sum(len(layer.get("terms", [])) for layer in layers)
    return GlossaryResponse(layers=layers, total_terms=total_terms)


@router.get("/agents", response_model=AgentRegistryResponse)
async def canon_agents() -> AgentRegistryResponse:
    """Get canonical agent registry."""
    loader = await get_canon()
    registry = loader.get_agent_registry()
    agents = registry.get("agents", {})
    return AgentRegistryResponse(agents=agents, total_agents=len(agents))


@router.get("/brain-os", response_model=BrainOSResponse)
async def canon_brain_os() -> BrainOSResponse:
    """Get Brain OS specification with UBI domain engines."""
    loader = await get_canon()
    brain_os_list = loader.get_brain_os_spec()
    if brain_os_list and len(brain_os_list) > 0:
        components = brain_os_list[0].get("components", {})
        brain_core = components.get("brain_core", {})
        engines = brain_core.get("engines", {})
        return BrainOSResponse(components=components, total_engines=len(engines))
    return BrainOSResponse(components={}, total_engines=0)


@router.get("/agents/{agent_id}")
async def canon_agent_detail(agent_id: str) -> dict[str, Any]:
    """Get specific agent details from registry."""
    loader = await get_canon()
    registry = loader.get_agent_registry()
    agents = registry.get("agents", {})
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return agents[agent_id]


@router.get("/terms/{term_id}")
async def canon_term_detail(term_id: str) -> dict[str, Any]:
    """Get specific term details from glossary."""
    loader = await get_canon()
    glossary = loader.get_glossary()
    layers = glossary.get("layers", [])
    for layer in layers:
        for term in layer.get("terms", []):
            if term.get("id") == term_id or term.get("name") == term_id:
                return term
    raise HTTPException(status_code=404, detail=f"Term {term_id} not found")
