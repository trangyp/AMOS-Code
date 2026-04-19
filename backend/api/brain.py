"""AMOS Brain API - Real brain-powered endpoints."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add brain path
_AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT / "clawspring" / "amos_brain"))

from amos_brain_working import think

router = APIRouter(prefix="/brain", tags=["brain"])


class BrainRequest(BaseModel):
    """Request to brain."""

    message: str
    context: dict[str, Any] = {}


class BrainResponse(BaseModel):
    """Response from brain."""

    status: str
    legality: float
    sigma: float
    mode: str
    brain_used: bool


@router.post("/think", response_model=BrainResponse)
async def brain_think(request: BrainRequest) -> BrainResponse:
    """Process request through AMOS brain."""
    try:
        result = think(request.message, request.context)
        return BrainResponse(
            status=result.get("status", "unknown"),
            legality=result.get("legality", 0.0),
            sigma=result.get("sigma", 0.0),
            mode=result.get("mode", "unknown"),
            brain_used=result.get("brain_used", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def brain_status() -> dict[str, Any]:
    """Get brain status."""
    result = think("Check brain status", {"check": True})
    return {
        "operational": result["status"] == "SUCCESS",
        "legality": result["legality"],
        "mode": result["mode"],
    }
