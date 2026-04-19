#!/usr/bin/env python3
"""AXIOM One Execution Slot API - Real Brain Integration

FastAPI router for AXIOM One Execution Slots with AMOS Brain integration.
Uses real brain components: CognitiveEngine, MasterOrchestrator, SuperBrain.
"""

import sys
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Add paths for imports
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "clawspring"))

# Import AXIOM One

from axiom_one import ExecutionSlot, SlotMode
from axiom_one.execution_slot import ExecutionSlotManager

# Import Brain components directly
try:
    from amos_brain import get_super_brain
    from amos_brain.cognitive_engine import CognitiveEngine, get_cognitive_engine

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False
    get_cognitive_engine = None
    get_super_brain = None

router = APIRouter(prefix="/axiom-one", tags=["AXIOM One Execution Slots"])

# Global state
_slot_manager = ExecutionSlotManager()
_brain_cache: dict[str, Any] = {}


class CreateSlotRequest(BaseModel):
    objective: str
    mode: str = "local"
    context: dict[str, Any] = None


class SlotResponse(BaseModel):
    slot_id: str
    status: str
    mode: str
    objective: str
    created_at: str
    events: int
    artifacts: dict[str, Any]


@router.post("/slots", response_model=SlotResponse)
async def create_slot(request: CreateSlotRequest):
    """Create and execute an Execution Slot with brain integration."""
    mode_map = {
        "local": SlotMode.LOCAL,
        "managed": SlotMode.MANAGED,
        "orch": SlotMode.ORCHESTRATION,
        "orchestration": SlotMode.ORCHESTRATION,
    }

    slot_mode = mode_map.get(request.mode.lower(), SlotMode.LOCAL)

    # Create slot
    slot = ExecutionSlot.create_local(
        objective=request.objective,
        repo_path=Path.cwd(),
    )
    slot.mode = slot_mode

    # Allocate and start
    slot = _slot_manager.allocate(slot)
    _slot_manager.start(slot.slot_id)

    # Use brain for cognitive processing if available
    if _BRAIN_AVAILABLE and get_cognitive_engine:
        try:
            engine = get_cognitive_engine()
            result = engine.process(
                query=f"Execute: {request.objective}",
                domain="software",
                context=request.context or {},
            )
            slot.log_event(
                "brain_cognitive_result",
                content=result.content[:200] if len(result.content) > 200 else result.content,
                confidence=result.confidence,
                domain=result.domain,
            )
            slot.artifacts["brain_processing"] = {
                "content": result.content,
                "confidence": result.confidence,
                "domain": result.domain,
                "processing_time_ms": result.processing_time_ms,
            }
        except Exception as e:
            slot.log_event("brain_error", error=str(e))

    # Complete slot
    _slot_manager.complete(slot.slot_id, success=True, artifacts=slot.artifacts)

    return SlotResponse(
        slot_id=slot.slot_id,
        status=slot.status.value,
        mode=slot.mode.value,
        objective=slot.objective,
        created_at=slot.created_at,
        events=len(slot.event_log),
        artifacts=slot.artifacts,
    )


@router.get("/slots")
async def list_slots():
    """List all active Execution Slots."""
    slots = _slot_manager.list_active()
    return {
        "count": len(slots),
        "slots": [
            {
                "slot_id": s.slot_id,
                "status": s.status.value,
                "mode": s.mode.value,
                "objective": s.objective[:50] + "..." if len(s.objective) > 50 else s.objective,
                "events": len(s.event_log),
            }
            for s in slots
        ],
    }


@router.get("/slots/{slot_id}")
async def get_slot(slot_id: str):
    """Get Execution Slot details."""
    slot = _slot_manager.get(slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    return {
        "slot_id": slot.slot_id,
        "status": slot.status.value,
        "mode": slot.mode.value,
        "objective": slot.objective,
        "created_at": slot.created_at,
        "completion_time": slot.completion_time,
        "events": [
            {"timestamp": e.timestamp, "type": e.event_type, "data": e.data} for e in slot.event_log
        ],
        "artifacts": slot.artifacts,
        "failure_reason": slot.failure_reason,
    }


@router.post("/slots/{slot_id}/rollback")
async def rollback_slot(slot_id: str):
    """Roll back an Execution Slot."""
    success = _slot_manager.rollback(slot_id)
    if not success:
        raise HTTPException(status_code=400, detail="Rollback failed")
    return {"success": True, "slot_id": slot_id}


@router.get("/brain/status")
async def brain_status():
    """Get AMOS Brain integration status."""
    status = {
        "available": _BRAIN_AVAILABLE,
        "components": {},
        "timestamp": datetime.now(UTC).isoformat(),
    }

    if _BRAIN_AVAILABLE:
        # Check cognitive engine
        try:
            engine = get_cognitive_engine()
            status["components"]["cognitive_engine"] = engine is not None
        except Exception as e:
            status["components"]["cognitive_engine"] = False
            status["components"]["cognitive_error"] = str(e)

        # Check super brain
        try:
            brain = get_super_brain()
            status["components"]["super_brain"] = brain is not None
        except Exception:
            status["components"]["super_brain"] = False

    return status


@router.websocket("/ws/slots")
async def slot_websocket(websocket: WebSocket):
    """WebSocket for real-time slot updates."""
    await websocket.accept()

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "message": "AXIOM One Slot WebSocket ready",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        while True:
            message = await websocket.receive_text()
            await websocket.send_json(
                {
                    "type": "echo",
                    "received": message,
                }
            )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
