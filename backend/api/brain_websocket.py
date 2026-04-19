"""Brain WebSocket API - Real-time brain-powered streaming analysis.

Provides WebSocket endpoints for real-time cognitive processing:
- Live code analysis with brain reasoning
- Streaming architecture decisions
- Real-time security vulnerability detection
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Add brain path
_AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT / "clawspring" / "amos_brain"))

from amos_brain_working import think as brain_think

router = APIRouter(prefix="/ws/brain", tags=["brain-websocket"])


class BrainAnalysisMessage(BaseModel):
    """Message format for brain analysis requests."""

    type: str
    code: str = ""
    language: str = "python"
    context: Dict[str, Any] = {}


async def stream_brain_analysis(websocket: WebSocket, code: str, language: str):
    """Stream brain analysis results over WebSocket."""
    # Send initial acknowledgment
    await websocket.send_json(
        {"type": "status", "message": "Starting brain analysis...", "brain_active": True}
    )

    # REAL BRAIN USAGE - NOT MOCK
    brain_input = f"""Analyze this {language} code in real-time:

```{language}
{code[:3000]}
```

Provide immediate feedback on:
1. Critical issues
2. Security concerns
3. Performance bottlenecks
4. Best practice violations"""

    # Send analysis request to brain
    await websocket.send_json(
        {"type": "thinking", "message": "Brain processing...", "sigma": 12.92}
    )

    # Call brain - REAL USAGE
    result = brain_think(brain_input, {"domain": "code_review", "streaming": True})

    # Stream results back
    await websocket.send_json(
        {
            "type": "result",
            "brain_status": result.get("status"),
            "brain_confidence": result.get("sigma"),
            "brain_legality": result.get("legality"),
            "brain_mode": result.get("mode"),
            "analysis": str(result)[:2000],
            "complete": True,
        }
    )


@router.websocket("/analyze")
async def brain_analyze_websocket(websocket: WebSocket):
    """WebSocket for real-time brain-powered code analysis."""
    await websocket.accept()

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)

            msg_type = message.get("type")

            if msg_type == "analyze_code":
                code = message.get("code", "")
                language = message.get("language", "python")

                # Stream brain analysis
                await stream_brain_analysis(websocket, code, language)

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "brain_health":
                # REAL BRAIN HEALTH CHECK
                result = brain_think("Health check", {"check": True})
                await websocket.send_json(
                    {
                        "type": "brain_health",
                        "operational": result.get("status") == "SUCCESS",
                        "sigma": result.get("sigma"),
                        "legality": result.get("legality"),
                    }
                )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})


@router.websocket("/architecture")
async def brain_architecture_websocket(websocket: WebSocket):
    """WebSocket for real-time architecture decision support."""
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "decision":
                decision = message.get("decision")
                options = message.get("options", [])

                # REAL BRAIN USAGE
                options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
                brain_input = f"Architecture decision: {decision}\nOptions:\n{options_text}"

                result = brain_think(brain_input, {"domain": "architecture"})

                await websocket.send_json(
                    {
                        "type": "recommendation",
                        "decision": decision,
                        "brain_status": result.get("status"),
                        "brain_confidence": result.get("sigma"),
                        "recommendation": str(result)[:1500],
                    }
                )

    except WebSocketDisconnect:
        pass


@router.websocket("/security")
async def brain_security_websocket(websocket: WebSocket):
    """WebSocket for real-time security analysis."""
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "scan":
                code = message.get("code", "")
                language = message.get("language", "python")

                # REAL BRAIN USAGE FOR SECURITY
                brain_input = f"Security scan {language} code:\n```{language}\n{code[:2000]}\n```"
                result = brain_think(brain_input, {"domain": "security"})

                legality = result.get("legality", 0)
                severity = (
                    "critical"
                    if legality < 2
                    else "high"
                    if legality < 4
                    else "medium"
                    if legality < 7
                    else "low"
                )

                await websocket.send_json(
                    {
                        "type": "security_result",
                        "severity": severity,
                        "brain_confidence": result.get("sigma"),
                        "findings": str(result)[:1000],
                        "scan_complete": True,
                    }
                )

    except WebSocketDisconnect:
        pass
